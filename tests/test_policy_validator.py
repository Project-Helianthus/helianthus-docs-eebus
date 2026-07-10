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


def add_evidence_backed_page(repo: Path, relative_path: str, body: str) -> Path:
    evidence_id = "EV-20260710-001"
    evidence = repo / "evidence" / f"{evidence_id}.md"
    evidence.write_text(
        "---\n"
        f'canonical_source: "Project-Helianthus/helianthus-docs-eebus:evidence/{evidence_id}.md"\n'
        'owner_domain: "evidence"\n'
        'license: "CC0-1.0"\n'
        'claim_status: "evidence-backed"\n'
        'source_class: "observed_runtime"\n'
        f'evidence_ids: "{evidence_id}"\n'
        'hypothesis_status: "draft"\n'
        'falsifier: "A redacted replay without the observation"\n'
        "---\n\n# Redacted evidence\n",
        encoding="utf-8",
    )
    page = repo / relative_path
    owner_domain = relative_path.split("/", 1)[0]
    license_id = (
        "CC0-1.0"
        if owner_domain in {"protocols", "devices", "evidence", "re-notes"}
        else "AGPL-3.0-only"
    )
    page.write_text(
        "---\n"
        f'canonical_source: "Project-Helianthus/helianthus-docs-eebus:{relative_path}"\n'
        f'owner_domain: "{owner_domain}"\n'
        f'license: "{license_id}"\n'
        'claim_status: "evidence-backed"\n'
        'source_class: "observed_runtime"\n'
        f'evidence_ids: "{evidence_id}"\n'
        'hypothesis_status: "draft"\n'
        'falsifier: "A redacted replay without the observation"\n'
        f"---\n\n# Candidate\n\n{body}\n",
        encoding="utf-8",
    )
    return page


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

    def test_front_matter_is_strict_yaml_mapping_with_unique_string_values(self) -> None:
        mutations = {
            "malformed": "malformed: [unclosed\n",
            "duplicate": (
                'canonical_source: "Project-Helianthus/helianthus-docs-eebus:'
                'protocols/ship-spine-overview.md"\n'
            ),
            "non-mapping": "- canonical_source\n- owner_domain\n",
            "non-string": "reviewed: true\n",
        }
        for name, mutation in mutations.items():
            with self.subTest(name=name):
                with tempfile.TemporaryDirectory() as tmp:
                    repo = copy_repo(Path(tmp))
                    page = repo / "protocols" / "ship-spine-overview.md"
                    text = page.read_text(encoding="utf-8")
                    closing = text.find("\n---\n", 4)
                    if name == "non-mapping":
                        replacement = f"---\n{mutation}---\n"
                    else:
                        replacement = text[:closing] + "\n" + mutation + "---\n"
                    page.write_text(replacement + text[closing + 5 :], encoding="utf-8")

                    result = run_validator(repo)

                    self.assertEqual(result.returncode, 1)
                    self.assertIn("YAML front matter", result.stderr)

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

    def test_issue_template_requires_provenance(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = copy_repo(Path(tmp))
            template = repo / ".github" / "ISSUE_TEMPLATE" / "docs_task.yml"
            text = template.read_text(encoding="utf-8")
            marker = "    id: provenance\n"
            start = text.index(marker)
            end = text.index("\n  - type:", start)
            provenance = text[start:end].replace(
                "      required: true",
                "      required: false",
            )
            template.write_text(text[:start] + provenance + text[end:], encoding="utf-8")

            result = run_validator(repo)

            self.assertEqual(result.returncode, 1)
            self.assertIn("field 'provenance' must be required", result.stderr)

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

    def test_private_artifact_metadata_fields_fail(self) -> None:
        for field in ("filename", "hash", "identifier"):
            with self.subTest(field=field):
                with tempfile.TemporaryDirectory() as tmp:
                    repo = copy_repo(Path(tmp))
                    page = repo / "re-notes" / "template.md"
                    page.write_text(
                        page.read_text(encoding="utf-8")
                        + f"\nPrivate artifact {field}: redacted\n",
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
            "short raw ski": "Raw SKI: abcdef1234567890",
            "short raw shipid": "Raw SHIPID: abcdef1234567890",
            "prose raw ski": "Raw SKI abcdef1234567890",
            "backticked raw ship id": "`Raw SHIP ID abcdef1234567890`",
            "hyphenated raw ship id": "Raw SHIP-ID: abcdef1234567890",
            "underscored raw ship id": "Raw SHIP_ID: abcdef1234567890",
            "ship identifier": "SHIP identifier: abcdef1234567890",
            "ski identifier": "SKI identifier: abcdef1234567890",
            "ski id": "SKI ID: abcdef1234567890",
            "hyphenated ski id": "SKI-ID: abcdef1234567890",
            "underscored ski id": "SKI_ID: abcdef1234567890",
            "raw ski id": "Raw SKI ID abcdef1234567890",
            "backticked ski id": "`Raw SKI_ID abcdef1234567890`",
            "bare ship": "SHIP: abcdef1234567890",
            "raw bare ship": "Raw SHIP abcdef1234567890",
            "backticked bare ship": "`Raw SHIP abcdef1234567890`",
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

    def test_concatenated_identity_labels_fail_on_evidence_backed_page(self) -> None:
        for payload in ("SHIPID: abcdef1234567890", "Raw SKIID: abcdef1234567890"):
            with self.subTest(payload=payload):
                with tempfile.TemporaryDirectory() as tmp:
                    repo = copy_repo(Path(tmp))
                    add_evidence_backed_page(repo, "protocols/candidate.md", payload)

                    result = run_validator(repo)

                    self.assertEqual(result.returncode, 1)
                    self.assertIn("populated", result.stderr)

    def test_restricted_source_contamination_fails(self) -> None:
        payloads = (
            "Source class: vendor_restricted",
            "This claim was paraphrased from a restricted vendor document.",
            "restricted-source material was used for this claim.",
            "restricted source material was used for this claim.",
            "This claim used restricted vendor documents.",
            "restricted vendor docs.",
        )
        for payload in payloads:
            with self.subTest(payload=payload):
                with tempfile.TemporaryDirectory() as tmp:
                    repo = copy_repo(Path(tmp))
                    add_evidence_backed_page(repo, "protocols/restricted.md", payload)

                    result = run_validator(repo)

                    self.assertEqual(result.returncode, 1)
                    self.assertIn("restricted-source contamination marker found", result.stderr)

    def test_new_publishable_claim_requires_resolving_provenance(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = copy_repo(Path(tmp))
            page = repo / "protocols" / "invented.md"
            page.write_text(
                "---\n"
                'canonical_source: "Project-Helianthus/helianthus-docs-eebus:protocols/invented.md"\n'
                'owner_domain: "protocols"\n'
                'license: "CC0-1.0"\n'
                'claim_status: "no-protocol-claims"\n'
                'publication_status: "ownership-landing"\n'
                "---\n\n"
                "# Invented claim\n\nVR940f exposes an invented SPINE feature.\n",
                encoding="utf-8",
            )

            result = run_validator(repo)

            self.assertEqual(result.returncode, 1)
            self.assertIn("claim_status must be 'evidence-backed'", result.stderr)

    def test_scaffold_body_is_locked_against_asserted_behavior(self) -> None:
        claims = (
            "VR940f uses TLS pairing with myVaillant.",
            "VR940f has a stable peer identity after pairing.",
            "The gateway pairs with the remote.",
            "The gateway discovers peers.",
            "SHIP negotiates identity security.",
        )
        for claim in claims:
            with self.subTest(claim=claim):
                with tempfile.TemporaryDirectory() as tmp:
                    repo = copy_repo(Path(tmp))
                    page = repo / "protocols" / "ship-spine-overview.md"
                    page.write_text(
                        page.read_text(encoding="utf-8") + f"\n{claim}\n",
                        encoding="utf-8",
                    )

                    result = run_validator(repo)

                    self.assertEqual(result.returncode, 1)
                    self.assertIn("scaffold artifact differs", result.stderr)

    def test_scaffold_front_matter_is_locked_against_asserted_behavior(self) -> None:
        scaffold_pages = (
            "README.md",
            "protocols/ship-spine-overview.md",
            "architecture/README.md",
            "api/README.md",
            "devices/vr940f.md",
            "evidence/README.md",
            "evidence/evidence-template.md",
            "re-notes/template.md",
            "development/contributing.md",
        )
        for relative_path in scaffold_pages:
            with self.subTest(relative_path=relative_path):
                with tempfile.TemporaryDirectory() as tmp:
                    repo = copy_repo(Path(tmp))
                    page = repo / relative_path
                    text = page.read_text(encoding="utf-8")
                    page.write_text(
                        text.replace(
                            "\n---\n",
                            '\nsummary: "VR940f uses SHIP pairing with a peer."\n---\n',
                            1,
                        ),
                        encoding="utf-8",
                    )

                    result = run_validator(repo)

                    self.assertEqual(result.returncode, 1)
                    self.assertIn("scaffold artifact differs", result.stderr)

    def test_evidence_backed_claim_requires_existing_evidence_page(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = copy_repo(Path(tmp))
            page = repo / "protocols" / "claim.md"
            page.write_text(
                "---\n"
                'canonical_source: "Project-Helianthus/helianthus-docs-eebus:protocols/claim.md"\n'
                'owner_domain: "protocols"\n'
                'license: "CC0-1.0"\n'
                'claim_status: "evidence-backed"\n'
                'source_class: "observed_runtime"\n'
                'evidence_ids: "EV-20260710-001"\n'
                'hypothesis_status: "draft"\n'
                'falsifier: "A redacted replay without the observed feature"\n'
                "---\n\n# Candidate\n",
                encoding="utf-8",
            )

            result = run_validator(repo)

            self.assertEqual(result.returncode, 1)
            self.assertIn("publishable evidence page 'EV-20260710-001.md' is missing", result.stderr)

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

    def test_ipv6_address_fails_in_publishable_content(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = copy_repo(Path(tmp))
            page = repo / "evidence" / "evidence-template.md"
            page.write_text(
                page.read_text(encoding="utf-8") + "\nAddress: fe80::1234%en0\n",
                encoding="utf-8",
            )

            result = run_validator(repo)

            self.assertEqual(result.returncode, 1)
            self.assertIn("IPv6 address found", result.stderr)

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

    def test_control_yaml_duplicate_keys_fail(self) -> None:
        cases = (
            (".github/ISSUE_TEMPLATE/docs_task.yml", "name: Documentation task\n"),
            (".github/workflows/docs-ci.yml", "name: Docs CI\n"),
        )
        for relative_path, marker in cases:
            with self.subTest(relative_path=relative_path):
                with tempfile.TemporaryDirectory() as tmp:
                    repo = copy_repo(Path(tmp))
                    path = repo / relative_path
                    text = path.read_text(encoding="utf-8")
                    path.write_text(
                        text.replace(marker, marker + "name: Duplicate\n", 1),
                        encoding="utf-8",
                    )

                    result = run_validator(repo)

                    self.assertEqual(result.returncode, 1)
                    self.assertIn("invalid YAML", result.stderr)

    def test_issue_config_is_strict_and_disables_blank_issues(self) -> None:
        mutations = {
            "missing": None,
            "enabled": "blank_issues_enabled: true\n",
            "duplicate": "blank_issues_enabled: false\nblank_issues_enabled: true\n",
        }
        for name, replacement in mutations.items():
            with self.subTest(name=name):
                with tempfile.TemporaryDirectory() as tmp:
                    repo = copy_repo(Path(tmp))
                    config = repo / ".github" / "ISSUE_TEMPLATE" / "config.yml"
                    if replacement is None:
                        config.unlink()
                    else:
                        config.write_text(replacement, encoding="utf-8")

                    result = run_validator(repo)

                    self.assertEqual(result.returncode, 1)
                    self.assertIn(".github/ISSUE_TEMPLATE/config.yml", result.stderr)

    def test_ci_entrypoint_is_hash_locked(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = copy_repo(Path(tmp))
            ci_local = repo / "scripts" / "ci_local.sh"
            ci_local.write_text("#!/usr/bin/env bash\necho bypassed\n", encoding="utf-8")

            result = run_validator(repo)

            self.assertEqual(result.returncode, 1)
            self.assertIn("content differs from the reviewed CI entrypoint", result.stderr)

    def test_license_artifact_is_hash_locked(self) -> None:
        payloads = (
            "This claim was paraphrased from restricted vendor docs.",
            "Serial number: DEVICE-123456",
            "MAC address: 00:11:22:33:44:55",
        )
        for payload in payloads:
            with self.subTest(payload=payload):
                with tempfile.TemporaryDirectory() as tmp:
                    repo = copy_repo(Path(tmp))
                    license_file = repo / "LICENSE"
                    license_file.write_text(
                        license_file.read_text(encoding="utf-8") + f"\n{payload}\n",
                        encoding="utf-8",
                    )

                    result = run_validator(repo)

                    self.assertEqual(result.returncode, 1)
                    self.assertIn("content differs from the reviewed license policy", result.stderr)

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

    def test_licensing_acknowledgement_cannot_be_inverted(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = copy_repo(Path(tmp))
            template = repo / ".github" / "ISSUE_TEMPLATE" / "docs_task.yml"
            text = template.read_text(encoding="utf-8")
            start = "I have read the repository license policy and I accept"
            template.write_text(
                text.replace(start, "I reject the repository license policy and do not accept", 1),
                encoding="utf-8",
            )

            result = run_validator(repo)

            self.assertEqual(result.returncode, 1)
            self.assertIn("licensing acknowledgement text must match policy", result.stderr)

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
            self.assertIn("premature docs milestone or code-doc absence claim", result.stderr)

    def test_all_future_docs_milestones_and_code_docs_absence_claims_fail(self) -> None:
        claims = (
            "MSP-DOCS-API-SCHEMA is complete.",
            "MSP-DOCS-PLATFORM has merged.",
            "MSP-DOCS-E2 is ready.",
            "helianthus-eebusreg has no docs/ directory.",
            "The helianthus-eebusreg docs/ directory is absent.",
        )
        for claim in claims:
            with self.subTest(claim=claim):
                with tempfile.TemporaryDirectory() as tmp:
                    repo = copy_repo(Path(tmp))
                    readme = repo / "README.md"
                    readme.write_text(
                        readme.read_text(encoding="utf-8") + f"\n{claim}\n",
                        encoding="utf-8",
                    )

                    result = run_validator(repo)

                    self.assertEqual(result.returncode, 1)
                    self.assertIn("premature docs milestone or code-doc absence claim", result.stderr)

    def test_binary_publishable_artifact_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = copy_repo(Path(tmp))
            artifact = repo / "evidence" / "capture.bin"
            artifact.write_bytes(b"\x00\xff\x00")

            result = run_validator(repo)

            self.assertEqual(result.returncode, 1)
            self.assertIn("binary or non-UTF-8 publishable artifact is forbidden", result.stderr)

    def test_nul_bearing_utf8_publishable_artifact_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = copy_repo(Path(tmp))
            artifact = repo / "evidence" / "capture.dat"
            artifact.write_bytes(b"valid utf-8\x00payload\n")

            result = run_validator(repo)

            self.assertEqual(result.returncode, 1)
            self.assertIn("control bytes are forbidden", result.stderr)

    def test_root_publishable_control_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = copy_repo(Path(tmp))
            readme = repo / "README.md"
            readme.write_bytes(readme.read_bytes() + b"\ncontrol\x7f\n")

            result = run_validator(repo)

            self.assertEqual(result.returncode, 1)
            self.assertIn("control bytes are forbidden", result.stderr)

    def test_del_and_c1_publishable_controls_fail(self) -> None:
        payloads = (
            b"payload\x09\n",
            b"payload\x0d\n",
            b"payload\x7f\n",
            "payload\u0085\n".encode("utf-8"),
        )
        for payload in payloads:
            with self.subTest(payload=payload):
                with tempfile.TemporaryDirectory() as tmp:
                    repo = copy_repo(Path(tmp))
                    artifact = repo / "evidence" / "control.txt"
                    artifact.write_bytes(payload)

                    result = run_validator(repo)

                    self.assertEqual(result.returncode, 1)
                    self.assertIn("control bytes are forbidden", result.stderr)

    def test_required_owner_domain_directory_must_exist(self) -> None:
        for directory in ("architecture", "api"):
            with self.subTest(directory=directory):
                with tempfile.TemporaryDirectory() as tmp:
                    repo = copy_repo(Path(tmp))
                    shutil.rmtree(repo / directory)

                    result = run_validator(repo)

                    self.assertEqual(result.returncode, 1)
                    self.assertIn("path-domain owner must be a directory", result.stderr)

    def test_required_canonical_landing_page_cannot_be_substituted(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = copy_repo(Path(tmp))
            landing = repo / "api" / "README.md"
            replacement = repo / "api" / "placeholder.md"
            replacement.write_text(
                landing.read_text(encoding="utf-8").replace(
                    "api/README.md",
                    "api/placeholder.md",
                    1,
                ),
                encoding="utf-8",
            )
            landing.unlink()

            result = run_validator(repo)

            self.assertEqual(result.returncode, 1)
            self.assertIn("required canonical landing page is missing", result.stderr)

    def test_premature_consumer_availability_claim_fails(self) -> None:
        claims = (
            "GraphQL exposure, Home Assistant entities, and command routing are available now.",
            "HA entity rollout is shipped now.",
            "Portal consumer workflow is active now.",
            "GraphQL exposure has shipped.",
            "Home Assistant entities have been enabled.",
            "gateway import has been enabled.",
        )
        for claim in claims:
            with self.subTest(claim=claim):
                with tempfile.TemporaryDirectory() as tmp:
                    repo = copy_repo(Path(tmp))
                    page = repo / "protocols" / "ship-spine-overview.md"
                    page.write_text(
                        page.read_text(encoding="utf-8") + f"\n{claim}\n",
                        encoding="utf-8",
                    )

                    result = run_validator(repo)

                    self.assertEqual(result.returncode, 1)
                    self.assertIn("premature gateway or consumer availability claim", result.stderr)


if __name__ == "__main__":
    unittest.main()
