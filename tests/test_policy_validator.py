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

    def test_commented_codeowners_rule_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = copy_repo(Path(tmp))
            codeowners = repo / ".github" / "CODEOWNERS"
            codeowners.write_text("# * @d3vi1\n", encoding="utf-8")

            result = run_validator(repo)

            self.assertEqual(result.returncode, 1)
            self.assertIn("must assign default ownership", result.stderr)

    def test_later_codeowners_default_override_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = copy_repo(Path(tmp))
            codeowners = repo / ".github" / "CODEOWNERS"
            codeowners.write_text(
                codeowners.read_text(encoding="utf-8") + "* @someoneelse\n",
                encoding="utf-8",
            )

            result = run_validator(repo)

            self.assertEqual(result.returncode, 1)
            self.assertIn("must assign default ownership", result.stderr)

    def test_codeowners_inline_comment_cannot_spoof_owner(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = copy_repo(Path(tmp))
            codeowners = repo / ".github" / "CODEOWNERS"
            codeowners.write_text("* @someoneelse # @d3vi1\n", encoding="utf-8")

            result = run_validator(repo)

            self.assertEqual(result.returncode, 1)
            self.assertIn("must assign default ownership", result.stderr)

    def test_specific_codeowners_rule_must_retain_owner(self) -> None:
        for rule in ("/protocols/** @someoneelse", "*.md @someoneelse"):
            with self.subTest(rule=rule):
                with tempfile.TemporaryDirectory() as tmp:
                    repo = copy_repo(Path(tmp))
                    codeowners = repo / ".github" / "CODEOWNERS"
                    codeowners.write_text(
                        codeowners.read_text(encoding="utf-8") + rule + "\n",
                        encoding="utf-8",
                    )

                    result = run_validator(repo)

                    self.assertEqual(result.returncode, 1)
                    self.assertIn("must retain", result.stderr)

    def test_symlinked_markdown_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = copy_repo(Path(tmp))
            outside = Path(tmp) / "outside.md"
            outside.write_bytes(b"\xff")
            symlink = repo / "protocols" / "symlinked.md"
            try:
                symlink.symlink_to(outside)
            except OSError as error:
                self.skipTest(f"symlinks unavailable: {error}")

            result = run_validator(repo)

            self.assertEqual(result.returncode, 1)
            self.assertIn("symlinks are forbidden", result.stderr)
            self.assertNotIn("Traceback", result.stderr)

    def test_platform_link_requires_cross_seed_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = copy_repo(Path(tmp))
            page = repo / "devices" / "vr940f.md"
            text = page.read_text(encoding="utf-8")
            page.write_text(
                text.replace("cross_seed_target:", "cross_seed_target_missing:", 1),
                encoding="utf-8",
            )

            result = run_validator(repo)

            self.assertEqual(result.returncode, 1)
            self.assertIn("cross_seed_target must match", result.stderr)

    def test_cross_seed_cannot_duplicate_platform_requirements(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = copy_repo(Path(tmp))
            page = repo / "devices" / "vr940f.md"
            page.write_text(
                page.read_text(encoding="utf-8")
                + "\n## Requirements and Acceptance Criteria\n\n- duplicated\n",
                encoding="utf-8",
            )

            result = run_validator(repo)

            self.assertEqual(result.returncode, 1)
            self.assertIn("platform-owned headings", result.stderr)

    def test_cross_seed_cannot_use_setext_platform_heading(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = copy_repo(Path(tmp))
            page = repo / "devices" / "vr940f.md"
            page.write_text(
                page.read_text(encoding="utf-8") + "\nRequirements\n------------\n\n- duplicated\n",
                encoding="utf-8",
            )

            result = run_validator(repo)

            self.assertEqual(result.returncode, 1)
            self.assertIn("platform-owned headings", result.stderr)

    def test_cross_seed_cannot_use_h1_platform_heading(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = copy_repo(Path(tmp))
            page = repo / "devices" / "vr940f.md"
            page.write_text(
                page.read_text(encoding="utf-8") + "\n# Requirements\n\n- duplicated\n",
                encoding="utf-8",
            )

            result = run_validator(repo)

            self.assertEqual(result.returncode, 1)
            self.assertIn("platform-owned headings", result.stderr)

    def test_platform_autolink_requires_cross_seed_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = copy_repo(Path(tmp))
            page = repo / "protocols" / "ship-spine-overview.md"
            page.write_text(
                page.read_text(encoding="utf-8")
                + "\n<https://github.com/Project-Helianthus/helianthus-docs-ebus/"
                "blob/main/docs/platform/eebus-raw-first-contract.md>\n",
                encoding="utf-8",
            )

            result = run_validator(repo)

            self.assertEqual(result.returncode, 1)
            self.assertIn("cross_seed_target must match", result.stderr)

    def test_platform_link_suffix_must_be_exact(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = copy_repo(Path(tmp))
            page = repo / "devices" / "vr940f.md"
            page.write_text(
                page.read_text(encoding="utf-8").replace(
                    "eebus-raw-first-contract.md)",
                    "eebus-raw-first-contract.md.bak)",
                    1,
                ),
                encoding="utf-8",
            )

            result = run_validator(repo)

            self.assertEqual(result.returncode, 1)
            self.assertIn("cross-seed metadata requires a canonical platform link", result.stderr)

    def test_platform_bare_url_with_period_is_detected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = copy_repo(Path(tmp))
            page = repo / "protocols" / "ship-spine-overview.md"
            page.write_text(
                page.read_text(encoding="utf-8")
                + "\nhttps://github.com/Project-Helianthus/helianthus-docs-ebus/"
                "blob/main/docs/platform/eebus-raw-first-contract.md.\n"
                "\n## Requirements\n\n- duplicated\n",
                encoding="utf-8",
            )

            result = run_validator(repo)

            self.assertEqual(result.returncode, 1)
            self.assertIn("cross_seed_target must match", result.stderr)

    def test_private_artifact_reference_field_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = copy_repo(Path(tmp))
            page = repo / "re-notes" / "template.md"
            page.write_text(
                page.read_text(encoding="utf-8") + "\n- Private artifact reference:\n",
                encoding="utf-8",
            )

            result = run_validator(repo)

            self.assertEqual(result.returncode, 1)
            self.assertIn("private artifact location/reference field is forbidden", result.stderr)

    def test_sensitive_payload_patterns_fail_in_any_publishable_page(self) -> None:
        cases = {
            "private artifact": "Private artifact location: /tmp/operator/capture.json",
            "pem": "-----BEGIN PRIVATE KEY-----",
            "mac": "MAC address: 00:11:22:33:44:55",
            "dotted mac": "Observed peer 0011.2233.4455",
            "serial": "Serial number: DEVICE-123456",
            "redaction suffix": "Serial number: redacted DEVICE-123456",
            "fingerprint": "Fingerprint: 0123456789abcdef0123456789abcdef01234567",
        }
        for name, payload in cases.items():
            with self.subTest(name=name):
                with tempfile.TemporaryDirectory() as tmp:
                    repo = copy_repo(Path(tmp))
                    page = repo / "evidence" / "evidence-template.md"
                    page.write_text(
                        page.read_text(encoding="utf-8") + f"\n{payload}\n",
                        encoding="utf-8",
                    )

                    result = run_validator(repo)

                    self.assertEqual(result.returncode, 1)

    def test_non_markdown_publishable_artifact_gets_privacy_scan(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = copy_repo(Path(tmp))
            leak = repo / "evidence" / "leak.txt"
            leak.write_text(
                "Private artifact location: /tmp/operator/capture.json\n"
                "Serial number: DEVICE-123456\n"
                "MAC address: 00:11:22:33:44:55\n"
                "-----BEGIN PRIVATE KEY-----\n"
                "Address: " + "192.168." + "1.42\n",
                encoding="utf-8",
            )

            result = run_validator(repo)

            self.assertEqual(result.returncode, 1)
            self.assertIn("private artifact location/reference field is forbidden", result.stderr)
            self.assertIn("private IPv4 address found", result.stderr)

    def test_root_publishable_page_gets_privacy_scan(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = copy_repo(Path(tmp))
            readme = repo / "README.md"
            readme.write_text(
                readme.read_text(encoding="utf-8")
                + "\nSerial number: DEVICE-123456\nMAC address: 00:11:22:33:44:55\n",
                encoding="utf-8",
            )

            result = run_validator(repo)

            self.assertEqual(result.returncode, 1)
            self.assertIn("populated sensitive field", result.stderr)
            self.assertIn("MAC address found", result.stderr)

    def test_private_artifact_retained_value_cannot_smuggle_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = copy_repo(Path(tmp))
            page = repo / "evidence" / "evidence-template.md"
            page.write_text(
                page.read_text(encoding="utf-8").replace(
                    "Private artifact retained: <yes-or-no>",
                    "Private artifact retained: yes /tmp/operator/capture.json",
                    1,
                ),
                encoding="utf-8",
            )

            result = run_validator(repo)

            self.assertEqual(result.returncode, 1)
            self.assertIn("private artifact retained value must be yes or no", result.stderr)

    def test_workflow_path_filter_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = copy_repo(Path(tmp))
            workflow = repo / ".github" / "workflows" / "docs-ci.yml"
            workflow.write_text(
                workflow.read_text(encoding="utf-8").replace(
                    "  pull_request:\n",
                    "  pull_request:\n    paths:\n      - '**/*.md'\n",
                    1,
                ),
                encoding="utf-8",
            )

            result = run_validator(repo)

            self.assertEqual(result.returncode, 1)
            self.assertIn("path filters are forbidden", result.stderr)

    def test_workflow_semantic_bypasses_fail(self) -> None:
        mutations = {
            "fake command": lambda text: text.replace(
                "run: ./scripts/ci_local.sh",
                "run: echo docs-only # ./scripts/ci_local.sh",
                1,
            ),
            "inline paths": lambda text: text.replace(
                "  pull_request:\n",
                "  pull_request: {paths: ['**/*.md']}\n",
                1,
            ),
            "inline paths-ignore": lambda text: text.replace(
                "  pull_request:\n",
                "  pull_request: {paths-ignore: ['**/*.txt']}\n",
                1,
            ),
            "missing trigger": lambda text: text.replace("  pull_request:\n", "", 1),
            "closed only": lambda text: text.replace(
                "  pull_request:\n",
                "  pull_request: {types: [closed]}\n",
                1,
            ),
            "job condition": lambda text: text.replace(
                "    name: Docs Checks\n",
                "    name: Docs Checks\n    if: ${{ false }}\n",
                1,
            ),
            "job continue": lambda text: text.replace(
                "    name: Docs Checks\n",
                "    name: Docs Checks\n    continue-on-error: true\n",
                1,
            ),
            "step condition": lambda text: text.replace(
                "        run: ./scripts/ci_local.sh\n",
                "        if: ${{ false }}\n        run: ./scripts/ci_local.sh\n",
                1,
            ),
            "job needs": lambda text: text.replace(
                "    name: Docs Checks\n",
                "    name: Docs Checks\n    needs: never-runs\n",
                1,
            ),
            "step shell": lambda text: text.replace(
                "        run: ./scripts/ci_local.sh\n",
                "        shell: custom {0}\n        run: ./scripts/ci_local.sh\n",
                1,
            ),
            "dependency condition": lambda text: text.replace(
                "        run: python -m pip install -r requirements-ci.txt\n",
                "        if: ${{ false }}\n"
                "        run: python -m pip install -r requirements-ci.txt\n",
                1,
            ),
            "missing dependency install": lambda text: text.replace(
                "      - name: Install policy validator dependencies\n"
                "        run: python -m pip install -r requirements-ci.txt\n\n",
                "",
                1,
            ),
            "wrong runner": lambda text: text.replace(
                "    runs-on: ubuntu-latest\n",
                "    runs-on: self-hosted\n",
                1,
            ),
        }
        for name, mutate in mutations.items():
            with self.subTest(name=name):
                with tempfile.TemporaryDirectory() as tmp:
                    repo = copy_repo(Path(tmp))
                    workflow = repo / ".github" / "workflows" / "docs-ci.yml"
                    workflow.write_text(
                        mutate(workflow.read_text(encoding="utf-8")),
                        encoding="utf-8",
                    )

                    result = run_validator(repo)

                    self.assertEqual(result.returncode, 1)

    def test_issue_form_keyword_stuffing_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = copy_repo(Path(tmp))
            template = repo / ".github" / "ISSUE_TEMPLATE" / "docs_task.yml"
            template.write_text(
                "name: Documentation task\n"
                "description: What Why Acceptance Criteria Ownership domain Provenance "
                "Dependencies Smoke test required Licensing acknowledgement\n"
                "body: []\n",
                encoding="utf-8",
            )

            result = run_validator(repo)

            self.assertEqual(result.returncode, 1)
            self.assertIn("missing field", result.stderr)

    def test_issue_form_types_and_options_are_enforced(self) -> None:
        mutations = {
            "ownership type": lambda text: text.replace(
                "  - type: dropdown\n    id: ownership_domain",
                "  - type: input\n    id: ownership_domain",
                1,
            ),
            "smoke type": lambda text: text.replace(
                "  - type: dropdown\n    id: smoke_test",
                "  - type: input\n    id: smoke_test",
                1,
            ),
            "smoke options": lambda text: text.replace(
                '        - "YES"\n',
                '        - "MAYBE"\n',
                1,
            ),
        }
        for name, mutate in mutations.items():
            with self.subTest(name=name):
                with tempfile.TemporaryDirectory() as tmp:
                    repo = copy_repo(Path(tmp))
                    template = repo / ".github" / "ISSUE_TEMPLATE" / "docs_task.yml"
                    template.write_text(
                        mutate(template.read_text(encoding="utf-8")),
                        encoding="utf-8",
                    )

                    result = run_validator(repo)

                    self.assertEqual(result.returncode, 1)

    def test_premature_execution_completion_claim_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = copy_repo(Path(tmp))
            readme = repo / "README.md"
            readme.write_text(
                readme.read_text(encoding="utf-8")
                + "\nMSP-DOCS-CLEAN is complete and the absence gate is installed.\n",
                encoding="utf-8",
            )

            result = run_validator(repo)

            self.assertEqual(result.returncode, 1)
            self.assertIn("premature MSP-DOCS-E2/CLEAN completion claim", result.stderr)

    def test_binary_publishable_artifact_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = copy_repo(Path(tmp))
            artifact = repo / "evidence" / "capture.bin"
            artifact.write_bytes(b"\x00\xff\x00")

            result = run_validator(repo)

            self.assertEqual(result.returncode, 1)
            self.assertIn("binary or non-UTF-8 publishable artifact is forbidden", result.stderr)

    def test_required_owner_domain_directory_must_exist(self) -> None:
        for directory in ("architecture", "api"):
            with self.subTest(directory=directory):
                with tempfile.TemporaryDirectory() as tmp:
                    repo = copy_repo(Path(tmp))
                    shutil.rmtree(repo / directory)

                    result = run_validator(repo)

                    self.assertEqual(result.returncode, 1)
                    self.assertIn("path-domain owner must be a directory", result.stderr)


if __name__ == "__main__":
    unittest.main()
