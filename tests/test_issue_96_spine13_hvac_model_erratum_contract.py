from __future__ import annotations

import re
import shutil
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import validate_repository_policy as repository_policy  # noqa: E402


def copy_repo(tmp_path: Path) -> Path:
    destination = tmp_path / "repo"
    shutil.copytree(
        ROOT,
        destination,
        ignore=shutil.ignore_patterns(".git", ".pytest_cache", "__pycache__"),
    )
    return destination


class Issue96Spine13HvacModelErratumContractTests(unittest.TestCase):
    def test_policy_has_the_complete_issue_96_marker_inventory(self) -> None:
        self.assertEqual(
            repository_policy.issue_96_spine13_hvac_model_erratum_errors.__doc__,
            "Enforce the bounded public-evidence SPINE 1.3 HVAC model erratum.",
        )
        self.assertEqual(
            set(repository_policy.ISSUE96_REQUIRED_MARKERS),
            {
                "issue link",
                "public implementation boundary",
                "spine 1.4 exclusion",
                "wholesale merge exclusion",
                "restricted material exclusion",
                "9970150 exclusion",
                "setpoint model",
                "setpoint selector",
                "hvac description functions",
                "hvac relations",
                "selector hunk",
                "baseline",
                "classification boundary",
                "falsifier boundary",
                "raw/redacted boundary",
                "version hunk binding",
                "baseline commitment",
            },
        )

    def test_candidate_and_evidence_pass_the_issue_96_policy(self) -> None:
        self.assertEqual(repository_policy.issue_96_spine13_hvac_model_erratum_errors(ROOT), [])

    def test_policy_rejects_each_missing_required_marker(self) -> None:
        candidate = repository_policy.ISSUE96_CANDIDATE_REL
        for name, marker in repository_policy.ISSUE96_REQUIRED_MARKERS.items():
            with self.subTest(name=name), tempfile.TemporaryDirectory() as tmp:
                repo = copy_repo(Path(tmp))
                path = repo / candidate
                text = path.read_text(encoding="utf-8")
                marker_pattern = r"\s+".join(
                    re.escape(token) for token in marker.split()
                )
                amended, replacements = re.subn(
                    marker_pattern,
                    "removed-marker",
                    text,
                    flags=re.IGNORECASE,
                )
                self.assertGreater(replacements, 0, marker)
                path.write_text(amended, encoding="utf-8")

                errors = repository_policy.issue_96_spine13_hvac_model_erratum_errors(repo)

                self.assertIn(f"{candidate}: issue-96 missing {name} marker", errors)

    def test_policy_rejects_version_or_hunk_binding_drift(self) -> None:
        relative = Path("evidence/EV-20260730-001.md")
        mutations = (
            ("implementation: SPINE 1.3", "implementation: SPINE 1.4"),
            (
                "advertised_specification_version: \"1.3.0\"",
                "advertised_specification_version: \"1.4.0\"",
            ),
            (
                "hvac_operation_mode_selector_hunk_only",
                "all_hunks_from_commit",
            ),
            ("- spine/const.go", "- model/commandframe.go"),
        )
        for before, after in mutations:
            with self.subTest(before=before), tempfile.TemporaryDirectory() as tmp:
                repo = copy_repo(Path(tmp))
                path = repo / relative
                text = path.read_text(encoding="utf-8")
                self.assertIn(before, text)
                path.write_text(text.replace(before, after, 1), encoding="utf-8")

                errors = repository_policy.issue_96_spine13_hvac_model_erratum_errors(repo)

                self.assertIn(
                    f"{relative}: issue-96 public_version_hunk_binding contract drift",
                    errors,
                )

    def test_policy_rejects_baseline_or_custody_commitment_drift(self) -> None:
        relative = Path("evidence/EV-20260730-002.md")
        retained_field = "private_artifact_" + "retained"
        mutations = (
            ("declared: 49", "declared: 50"),
            ("success: 26", "success: 27"),
            ("failure: 23", "failure: 22"),
            (
                f'{retained_field}: "yes"',
                f'{retained_field}: "no"',
            ),
            ("custody: owner_only_not_published", "custody: public"),
            (
                repository_policy.ISSUE96_PUBLIC_BASELINE_HASHES["result_table"],
                "0" * 64,
            ),
        )
        for before, after in mutations:
            with self.subTest(before=before), tempfile.TemporaryDirectory() as tmp:
                repo = copy_repo(Path(tmp))
                path = repo / relative
                text = path.read_text(encoding="utf-8")
                self.assertIn(before, text)
                path.write_text(text.replace(before, after, 1), encoding="utf-8")

                errors = repository_policy.issue_96_spine13_hvac_model_erratum_errors(repo)

                self.assertIn(
                    f"{relative}: issue-96 public_baseline_commitment contract drift",
                    errors,
                )

    def test_policy_rejects_duplicate_contract_keys(self) -> None:
        cases = (
            (
                Path("evidence/EV-20260730-001.md"),
                "  implementation: SPINE 1.3",
                "  implementation: SPINE 1.4\n  implementation: SPINE 1.3",
                "public_version_hunk_binding",
            ),
            (
                Path("evidence/EV-20260730-002.md"),
                "  declared: 49",
                "  declared: 50\n  declared: 49",
                "public_baseline_commitment",
            ),
        )
        for relative, before, after, key in cases:
            with self.subTest(relative=relative), tempfile.TemporaryDirectory() as tmp:
                repo = copy_repo(Path(tmp))
                path = repo / relative
                text = path.read_text(encoding="utf-8")
                self.assertIn(before, text)
                path.write_text(text.replace(before, after, 1), encoding="utf-8")

                errors = repository_policy.issue_96_spine13_hvac_model_erratum_errors(repo)

                self.assertIn(
                    f"{relative}: issue-96 malformed {key} block",
                    errors,
                )

    def test_policy_rejects_missing_provenance_or_baseline_evidence(self) -> None:
        for relative in repository_policy.ISSUE96_EVIDENCE_RELS:
            with self.subTest(relative=relative), tempfile.TemporaryDirectory() as tmp:
                repo = copy_repo(Path(tmp))
                (repo / relative).unlink()

                errors = repository_policy.issue_96_spine13_hvac_model_erratum_errors(repo)

                self.assertIn(f"{relative}: issue-96 evidence document is missing", errors)
