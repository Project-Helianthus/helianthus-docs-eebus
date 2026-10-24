from __future__ import annotations

import unittest
from pathlib import Path

import sys
import shutil
import tempfile


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import validate_repository_policy as repository_policy  # noqa: E402

SUCCESSOR = ROOT / "api/_candidate/msp-138-native-runtime-exposure-v1.md"


class NativeRuntimeExposureContractTest(unittest.TestCase):
    def test_successor_preserves_native_runtime_data_without_semantic_promotion(self) -> None:
        text = " ".join(SUCCESSOR.read_text(encoding="utf-8").split()).casefold()
        required = (
            "implemented native payloads, identifiers, raw frames, registers, configuration",
            "protocol version, observation context, and source context",
            "must not replace a native value with a digest",
            "must not select, erase, or rewrite native data",
            "semantic promotion is a separate selective projection",
            "action-time operator confirmation",
            "synthetic fixtures",
        )
        for marker in required:
            self.assertIn(marker.casefold(), text)

    def test_successor_places_operator_socket_beside_the_state_root(self) -> None:
        text = " ".join(SUCCESSOR.read_text(encoding="utf-8").split())
        for marker in (
            "Nothing but the eeBUS store may live in the state root",
            "`<state-root>-operator/operator-mcp.sock` (`/data/eebus-operator/operator-mcp.sock` in the Home Assistant add-on)",
            "removes once at start a stale `operator-mcp.sock` that an earlier build left in the state root",
            "describe the earlier location, `/data/eebus/operator-mcp.sock` inside the state root",
        ):
            self.assertIn(marker, text)

    def test_repository_policy_rejects_successor_without_socket_location(self) -> None:
        mutations = {
            "rule": (
                "Nothing but the eeBUS store may live in the state root",
                "The state root may hold other files",
            ),
            "location": (
                "`<state-root>-operator/operator-mcp.sock`",
                "`/data/eebus/operator-mcp.sock`",
            ),
            "cleanup": (
                "removes once at start a stale `operator-mcp.sock`",
                "leaves a stale `operator-mcp.sock`",
            ),
            "frozen note": (
                "describe the earlier location",
                "describe the current location",
            ),
        }
        for name, (old, new) in mutations.items():
            with self.subTest(mutation=name), tempfile.TemporaryDirectory() as temporary:
                copied = Path(temporary) / "docs"
                shutil.copytree(ROOT, copied, ignore=shutil.ignore_patterns(".git", "worktrees", ".tmp"))
                page = copied / "api/_candidate/msp-138-native-runtime-exposure-v1.md"
                text = " ".join(page.read_text(encoding="utf-8").split())
                self.assertIn(old, text)
                page.write_text(text.replace(old, new), encoding="utf-8")
                errors = repository_policy.issue_138_native_runtime_exposure_errors(copied)
            self.assertTrue(
                any("missing native exposure marker" in error for error in errors), errors
            )

    def test_successor_explicitly_supersedes_legacy_redaction_contracts(self) -> None:
        text = SUCCESSOR.read_text(encoding="utf-8")
        for relative in (
            "api/_candidate/msp-068-raw-operator-redaction-amendment.md",
            "api/_candidate/raw-snapshot-view-v1.md",
            "api/_candidate/msp-06-eebus-mcp-v1.md",
            "architecture/_candidate/ha-addon-runtime-wiring.md",
        ):
            self.assertIn(relative, text)

    def test_repository_policy_enforces_successor_not_legacy_redaction(self) -> None:
        self.assertEqual(repository_policy.issue_138_native_runtime_exposure_errors(ROOT), [])

    def test_repository_policy_keeps_all_historical_artifacts_immutable(self) -> None:
        for historical in repository_policy.ISSUE138_FROZEN_HISTORICAL_ARTIFACTS:
            with self.subTest(historical=historical), tempfile.TemporaryDirectory() as temporary:
                copied = Path(temporary) / "docs"
                shutil.copytree(ROOT, copied, ignore=shutil.ignore_patterns(".git", "worktrees"))
                mutated = copied / historical
                mutated.write_text(
                    mutated.read_text(encoding="utf-8") + "\nmutation\n",
                    encoding="utf-8",
                )
                errors = repository_policy.check_repository(copied)
            self.assertTrue(
                any(str(historical) in error for error in errors),
                errors,
            )

    def test_repository_policy_rejects_historical_artifact_symlink(self) -> None:
        historical = Path("architecture/_candidate/ha-addon-runtime-wiring.md")
        with tempfile.TemporaryDirectory() as temporary:
            copied = Path(temporary) / "docs"
            shutil.copytree(ROOT, copied, ignore=shutil.ignore_patterns(".git", "worktrees"))
            replaced = copied / historical
            target = copied / "symlink-target.md"
            target.write_bytes(replaced.read_bytes())
            replaced.unlink()
            replaced.symlink_to(target)
            errors = repository_policy.check_repository(copied)
        self.assertTrue(any(str(historical) in error for error in errors), errors)


if __name__ == "__main__":
    unittest.main()
