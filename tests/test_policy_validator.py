from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
VALIDATOR = REPO / "scripts" / "validate_repository_policy.py"


def copy_repo(tmp_path: Path) -> Path:
    dst = tmp_path / "repo"
    ignore = shutil.ignore_patterns(".git", ".pytest_cache", "__pycache__")
    shutil.copytree(REPO, dst, ignore=ignore)
    return dst


def run_validator(repo: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(VALIDATOR), "--repo", str(repo)],
        check=False,
        text=True,
        capture_output=True,
    )


def reassign_front_matter_value(text: str, key: str, value: str) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.startswith(f"{key}:"):
            lines[index] = f'{key}: "{value}"'
            return "\n".join(lines) + "\n"
    raise AssertionError(f"missing front matter key: {key}")


class PolicyValidatorTests(unittest.TestCase):
    def test_current_repository_passes_policy_validator(self) -> None:
        result = run_validator(REPO)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_missing_canonical_source_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = copy_repo(Path(tmp))
            page = repo / "protocols" / "ship-spine-overview.md"
            text = page.read_text(encoding="utf-8")
            page.write_text(text.replace("canonical_source:", "canonical_source_missing:", 1), encoding="utf-8")

            result = run_validator(repo)

            self.assertEqual(result.returncode, 1)
            self.assertIn("canonical_source must be", result.stderr)

    def test_mismatched_canonical_source_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = copy_repo(Path(tmp))
            page = repo / "devices" / "vr940f.md"
            text = page.read_text(encoding="utf-8")
            wrong_source = "Project-Helianthus/helianthus-docs-eebus:protocols/ship-spine-overview.md"
            text = reassign_front_matter_value(text, "canonical_source", wrong_source)
            page.write_text(text, encoding="utf-8")

            result = run_validator(repo)

            self.assertEqual(result.returncode, 1)
            self.assertIn("canonical_source must be", result.stderr)

    def test_private_ipv4_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = copy_repo(Path(tmp))
            leak = "192.168." + "1.42"
            page = repo / "README.md"
            page.write_text(page.read_text(encoding="utf-8") + f"\nLeak: {leak}\n", encoding="utf-8")

            result = run_validator(repo)

            self.assertEqual(result.returncode, 1)
            self.assertIn("private IPv4 address found", result.stderr)

    def test_wrong_path_domain_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = copy_repo(Path(tmp))
            page = repo / "protocols" / "ship-spine-overview.md"
            text = page.read_text(encoding="utf-8")
            text = reassign_front_matter_value(text, "owner_domain", "api")
            page.write_text(text, encoding="utf-8")

            result = run_validator(repo)

            self.assertEqual(result.returncode, 1)
            self.assertIn("owner_domain must be 'protocols'", result.stderr)

    def test_required_control_files_are_enforced(self) -> None:
        required_files = [
            "LICENSE",
            ".github/CODEOWNERS",
            ".github/ISSUE_TEMPLATE/docs_task.yml",
        ]
        for relative_path in required_files:
            with self.subTest(relative_path=relative_path):
                with tempfile.TemporaryDirectory() as tmp:
                    repo = copy_repo(Path(tmp))
                    (repo / relative_path).unlink()

                    result = run_validator(repo)

                    self.assertEqual(result.returncode, 1)
                    self.assertIn(relative_path, result.stderr)

    def test_issue_template_requires_smoke_test_field(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = copy_repo(Path(tmp))
            template = repo / ".github" / "ISSUE_TEMPLATE" / "docs_task.yml"
            text = template.read_text(encoding="utf-8")
            template.write_text(
                text.replace("label: Smoke test required", "label: Runtime check", 1),
                encoding="utf-8",
            )

            result = run_validator(repo)

            self.assertEqual(result.returncode, 1)
            self.assertIn("Smoke test required", result.stderr)


if __name__ == "__main__":
    unittest.main()
