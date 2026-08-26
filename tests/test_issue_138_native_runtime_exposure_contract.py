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
