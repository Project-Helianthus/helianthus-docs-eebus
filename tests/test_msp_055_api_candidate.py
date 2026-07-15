from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Sequence


REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

from validate_msp_055_api_candidate import (  # noqa: E402
    ARTIFACT_ID,
    ARTIFACT_NAME,
    EXPECTED_PATHS,
    RUN_ATTEMPT,
    SOURCE_HEAD,
    validate,
)
from validate_repository_policy import (  # noqa: E402
    API_MACHINE_ARTIFACTS,
    MSP055_PROVENANCE_IDENTIFIER_ARTIFACTS,
)


NOW = datetime(2026, 7, 15, 12, 0, tzinfo=UTC)
RECORD_REL = Path("api/_candidate/msp-055/candidate-record.json")


class MSP055APICandidateTests(unittest.TestCase):
    def copy_repo(self) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        temporary = tempfile.TemporaryDirectory()
        root = Path(temporary.name) / "repo"
        shutil.copytree(REPO / "api", root / "api")
        shutil.copytree(REPO / "scripts", root / "scripts")
        return temporary, root

    def record(self, root: Path) -> dict[str, Any]:
        return json.loads((root / RECORD_REL).read_text(encoding="utf-8"))

    def write_record(self, root: Path, record: dict[str, Any]) -> None:
        (root / RECORD_REL).write_text(json.dumps(record), encoding="utf-8")

    def online_runner(
        self,
        *,
        pr: dict[str, Any] | None = None,
        run: dict[str, Any] | None = None,
        artifacts: dict[str, Any] | None = None,
        attestation_code: int = 0,
    ) -> Any:
        pr = pr or {
            "headRefOid": SOURCE_HEAD,
            "isDraft": True,
            "state": "OPEN",
            "mergedAt": None,
            "headRepositoryOwner": {"login": "Project-Helianthus"},
        }
        run = run or {
            "event": "workflow_dispatch",
            "conclusion": "success",
            "head_sha": SOURCE_HEAD,
            "run_attempt": RUN_ATTEMPT,
        }
        artifacts = artifacts or {
            "artifacts": [{
                "id": ARTIFACT_ID,
                "name": ARTIFACT_NAME,
                "expired": False,
                "expires_at": "2026-10-13T07:34:53Z",
                "workflow_run": {"id": 29397818751, "head_sha": SOURCE_HEAD},
            }]
        }

        def runner(args: Sequence[str]) -> subprocess.CompletedProcess[str]:
            if args[:3] == ("gh", "pr", "view"):
                payload, code = pr, 0
            elif args[:2] == ("gh", "api") and args[-1].endswith("/artifacts"):
                payload, code = artifacts, 0
            elif args[:2] == ("gh", "api"):
                payload, code = run, 0
            elif args[:3] == ("gh", "attestation", "verify"):
                payload, code = {}, attestation_code
            else:
                self.fail(f"unexpected command: {args!r}")
            return subprocess.CompletedProcess(list(args), code, json.dumps(payload), "")

        return runner

    def test_positive_offline_validation(self) -> None:
        self.assertEqual(validate(REPO, now=NOW), [])

    def test_candidate_machine_artifacts_are_exact_policy_entries(self) -> None:
        expected = set(EXPECTED_PATHS.values()) | {RECORD_REL.as_posix()}
        self.assertTrue(expected <= API_MACHINE_ARTIFACTS)
        self.assertEqual(
            {path for path in API_MACHINE_ARTIFACTS if path.startswith("api/_candidate/msp-055/")},
            expected,
        )
        self.assertEqual(
            MSP055_PROVENANCE_IDENTIFIER_ARTIFACTS,
            {
                RECORD_REL.as_posix(),
                EXPECTED_PATHS["predicate"],
                EXPECTED_PATHS["verification"],
            },
        )

    def test_source_push_is_terminal_online_failure(self) -> None:
        runner = self.online_runner(pr={
            "headRefOid": "0" * 40, "isDraft": True, "state": "OPEN", "mergedAt": None,
            "headRepositoryOwner": {"login": "Project-Helianthus"},
        })
        self.assertIn("online: source-pr-head", validate(REPO, online=True, now=NOW, runner=runner))

    def test_source_ready_for_review_remains_valid(self) -> None:
        runner = self.online_runner(pr={
            "headRefOid": SOURCE_HEAD,
            "isDraft": False,
            "state": "OPEN",
            "mergedAt": None,
            "headRepositoryOwner": {"login": "Project-Helianthus"},
        })
        self.assertEqual(validate(REPO, online=True, now=NOW, runner=runner), [])

    def test_source_closure_and_merge_are_terminal_online_failures(self) -> None:
        for state, merged_at in (("CLOSED", None), ("MERGED", "2026-07-15T08:00:00Z")):
            with self.subTest(state=state):
                runner = self.online_runner(pr={
                    "headRefOid": SOURCE_HEAD, "isDraft": True, "state": state, "mergedAt": merged_at,
                    "headRepositoryOwner": {"login": "Project-Helianthus"},
                })
                self.assertIn("online: source-pr-state", validate(REPO, online=True, now=NOW, runner=runner))

    def test_expiry_and_withdrawn_state_are_terminal_offline_failures(self) -> None:
        temporary, root = self.copy_repo()
        with temporary:
            record = self.record(root)
            record["run"]["expires_at"] = "2026-07-14T07:34:51Z"
            record["artifact"]["expires_at"] = "2026-07-14T07:34:51Z"
            self.write_record(root, record)
            self.assertIn("offline: candidate-expired", validate(root, now=NOW))
            record["state"] = "withdrawn"
            self.write_record(root, record)
            self.assertIn("offline: candidate-state", validate(root, now=NOW))

    def test_wrong_digest_run_attempt_and_ref_are_terminal_offline_failures(self) -> None:
        temporary, root = self.copy_repo()
        with temporary:
            record = self.record(root)
            record["artifacts"]["manifest"]["sha256"] = "0" * 64
            record["run"]["id"] = 1
            record["run"]["attempt"] = 2
            record["source"]["ref"] = "refs/heads/other"
            self.write_record(root, record)
            errors = validate(root, now=NOW)
            self.assertIn("offline: record-digest", errors)
            self.assertIn("offline: artifact-digest", errors)
            self.assertIn("offline: record-identity", errors)

    def test_missing_and_expired_artifacts_are_terminal_failures(self) -> None:
        temporary, root = self.copy_repo()
        with temporary:
            (root / EXPECTED_PATHS["bundle"]).unlink()
            self.assertIn("offline: artifact-missing", validate(root, now=NOW))
        runner = self.online_runner(artifacts={
            "artifacts": [{
                "id": ARTIFACT_ID,
                "name": ARTIFACT_NAME,
                "expired": True,
                "expires_at": "2026-10-13T07:34:53Z",
                "workflow_run": {"id": 29397818751, "head_sha": SOURCE_HEAD},
            }]
        })
        self.assertIn("online: artifact-expired", validate(REPO, online=True, now=NOW, runner=runner))

    def test_wrong_run_attempt_and_ref_are_terminal_online_failures(self) -> None:
        runner = self.online_runner(run={
            "event": "workflow_dispatch", "conclusion": "success", "head_sha": "0" * 40, "run_attempt": 2,
        })
        self.assertIn("online: workflow-run", validate(REPO, online=True, now=NOW, runner=runner))

    def test_failed_attestation_verification_is_terminal_online_failure(self) -> None:
        runner = self.online_runner(attestation_code=1)
        self.assertIn("online: attestation-verification", validate(REPO, online=True, now=NOW, runner=runner))


if __name__ == "__main__":
    unittest.main()
