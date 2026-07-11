from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml


REPO = Path(__file__).resolve().parents[1]
VALIDATOR = REPO / "scripts" / "validate_repository_policy.py"
sys.path.insert(0, str(REPO / "scripts"))

from validate_repository_policy import _fully_decode_reference


PLATFORM_COMMIT = "153191f72b5b9ecacbadcf2f3d7e480c6fef89a4"
CANDIDATE_PATH = "api/_candidate/runtime-reference.md"
PLATFORM_URL = (
    "https://github.com/Project-Helianthus/helianthus-docs-ebus/blob/"
    f"{PLATFORM_COMMIT}/docs/platform/shared-registry-boundary.md"
)


def copy_repo(tmp_path: Path) -> Path:
    destination = tmp_path / "repo"
    shutil.copytree(
        REPO,
        destination,
        ignore=shutil.ignore_patterns(".git", ".pytest_cache", "__pycache__"),
    )
    return destination


def run_validator(repo: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(VALIDATOR), "--repo", str(repo)],
        cwd=repo,
        check=False,
        text=True,
        capture_output=True,
    )


def replace_front_matter(page: Path, **updates: str) -> None:
    text = page.read_text(encoding="utf-8")
    end = text.index("\n---\n", 4)
    metadata = yaml.safe_load(text[4:end])
    metadata.update(updates)
    rendered = yaml.safe_dump(metadata, sort_keys=False)
    page.write_text(f"---\n{rendered}---\n{text[end + 5:]}", encoding="utf-8")


class MspDocsE2RemediationTests(unittest.TestCase):
    def test_candidate_location_overrides_metadata_escape(self) -> None:
        for relative_path in (CANDIDATE_PATH, "api/_candidate/nested/runtime-reference.md"):
            with self.subTest(
                relative_path=relative_path
            ), tempfile.TemporaryDirectory() as tmp:
                repo = copy_repo(Path(tmp))
                page = repo / relative_path
                if relative_path != CANDIDATE_PATH:
                    page.parent.mkdir(parents=True)
                    page.write_text(
                        (repo / CANDIDATE_PATH).read_text(encoding="utf-8"),
                        encoding="utf-8",
                    )
                    replace_front_matter(
                        page,
                        canonical_source=(
                            "Project-Helianthus/helianthus-docs-eebus:" + relative_path
                        ),
                        candidate_output_path=relative_path,
                    )
                replace_front_matter(
                    page,
                    publication_status="active",
                    candidate_output="false",
                    stable_navigation="false",
                    search="false",
                    sitemap="false",
                    versioned_bundle="false",
                    release_bundle="false",
                )

                result = run_validator(repo)

                self.assertEqual(result.returncode, 1, result.stderr)
                self.assertIn(
                    "candidate API path must declare publication_status candidate",
                    result.stderr,
                )
                self.assertIn("candidate API must declare candidate_output true", result.stderr)

    def test_percent_normalized_candidate_location_overrides_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = copy_repo(Path(tmp))
            source = repo / CANDIDATE_PATH
            encoded = repo / "api/%5Fcandidate/runtime-reference.md"
            encoded.parent.mkdir(parents=True)
            encoded.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
            source.unlink()
            replace_front_matter(
                encoded,
                canonical_source=(
                    "Project-Helianthus/helianthus-docs-eebus:"
                    "api/%5Fcandidate/runtime-reference.md"
                ),
                publication_status="active",
                candidate_output="false",
                candidate_output_path="api/%5Fcandidate/runtime-reference.md",
            )

            result = run_validator(repo)

            self.assertEqual(result.returncode, 1, result.stderr)
            self.assertIn("candidate API path must declare publication_status candidate", result.stderr)
            self.assertIn("candidate API must declare candidate_output true", result.stderr)

    def test_normalized_candidate_destinations_cannot_leak(self) -> None:
        leaks = {
            "stable_navigation": (
                "README.md",
                "\n[Candidate](api/stable/../%5fcandidate/runtime-reference.md)\n",
            ),
            "search": (
                "api/search-index.json",
                '{"path":"%2525252561pi%252525252f%252525255fcandidate%252525252fruntime-reference.md"}\n',
            ),
            "sitemap": (
                "api/sitemap.xml",
                "<loc>/api/stable/../_candidate/runtime-reference.md</loc>\n",
            ),
            "versioned_bundle": (
                "api/versioned-bundle.txt",
                "%61pi/_candidate/runtime-reference.md\n",
            ),
            "release_bundle": (
                "api/release-bundle.txt",
                "api/%2e%2e/api/_candidate/runtime-reference.md\n",
            ),
        }
        for channel, (relative_path, payload) in leaks.items():
            with self.subTest(channel=channel), tempfile.TemporaryDirectory() as tmp:
                repo = copy_repo(Path(tmp))
                artifact = repo / relative_path
                if artifact.exists():
                    payload = artifact.read_text(encoding="utf-8") + payload
                artifact.write_text(payload, encoding="utf-8")

                result = run_validator(repo)

                self.assertEqual(result.returncode, 1, result.stderr)
                self.assertIn(f"candidate API leaked into {channel}", result.stderr)

    def test_obfuscated_link_forms_cannot_leak_from_any_stable_channel(self) -> None:
        channels = {
            "stable_navigation": "README.md",
            "search": "api/search-index.json",
            "sitemap": "api/sitemap.xml",
            "versioned_bundle": "api/versioned-bundle.txt",
            "release_bundle": "api/release-bundle.txt",
        }
        payloads = {
            "markdown": (
                "[Candidate](api%25255cstable%25255c..%25255c"
                "%25255fcandidate%25255cruntime-reference.md)\n"
            ),
            "html": (
                '<a href="api&#37;25255cstable&#37;25255c..&#37;25255c'
                '&#37;25255fcandidate&#37;25255cruntime-reference.md">Candidate</a>\n'
            ),
        }
        for channel, relative_path in channels.items():
            for form, payload in payloads.items():
                with self.subTest(
                    channel=channel, form=form
                ), tempfile.TemporaryDirectory() as tmp:
                    repo = copy_repo(Path(tmp))
                    artifact = repo / relative_path
                    prefix = artifact.read_text(encoding="utf-8") if artifact.exists() else ""
                    artifact.write_text(prefix + "\n" + payload, encoding="utf-8")

                    result = run_validator(repo)

                    self.assertEqual(result.returncode, 1, result.stderr)
                    self.assertIn(f"candidate API leaked into {channel}", result.stderr)

    def test_github_candidate_urls_and_json_escapes_cannot_leak(self) -> None:
        channels = {
            "stable_navigation": "README.md",
            "search": "api/search-index.json",
            "sitemap": "api/sitemap.xml",
            "versioned_bundle": "api/versioned-bundle.txt",
            "release_bundle": "api/release-bundle.txt",
        }
        candidate_url = (
            "https://github.com/Project-Helianthus/helianthus-docs-eebus/"
            "blob/main/api/_candidate/runtime-reference.md"
        )
        payloads = {
            "absolute GitHub URL": candidate_url,
            "JSON unicode escapes": (
                '{"candidate":"' + candidate_url.replace("/", r"\u002f") + '"}'
            ),
        }
        for channel, relative_path in channels.items():
            for form, payload in payloads.items():
                with self.subTest(
                    channel=channel, form=form
                ), tempfile.TemporaryDirectory() as tmp:
                    repo = copy_repo(Path(tmp))
                    artifact = repo / relative_path
                    prefix = artifact.read_text(encoding="utf-8") if artifact.exists() else ""
                    artifact.write_text(prefix + "\n" + payload + "\n", encoding="utf-8")

                    result = run_validator(repo)

                    self.assertEqual(result.returncode, 1, result.stderr)
                    self.assertIn(f"candidate API leaked into {channel}", result.stderr)

    def test_host_root_github_candidate_urls_cannot_leak(self) -> None:
        channels = {
            "stable_navigation": "README.md",
            "search": "api/search-index.json",
            "sitemap": "api/sitemap.xml",
            "versioned_bundle": "api/versioned-bundle.txt",
            "release_bundle": "api/release-bundle.txt",
        }
        payload = (
            "/Project-Helianthus/helianthus-docs-eebus/"
            "blob/main/api/_candidate/runtime-reference.md"
        )
        for channel, relative_path in channels.items():
            with self.subTest(channel=channel), tempfile.TemporaryDirectory() as tmp:
                repo = copy_repo(Path(tmp))
                artifact = repo / relative_path
                prefix = artifact.read_text(encoding="utf-8") if artifact.exists() else ""
                artifact.write_text(prefix + "\n" + payload + "\n", encoding="utf-8")

                result = run_validator(repo)

                self.assertEqual(result.returncode, 1, result.stderr)
                self.assertIn(f"candidate API leaked into {channel}", result.stderr)

    def test_raw_unicode_escaped_candidate_paths_cannot_leak(self) -> None:
        escaped = r"api\u002f_candidate\u002fruntime-reference.md"
        channels = {
            "stable_navigation": ("README.md", f"[Candidate]({escaped})"),
            "search": ("api/search-index.json", '{"candidate":"' + escaped + '"}'),
            "sitemap": ("api/sitemap.xml", f"<loc>{escaped}</loc>"),
            "versioned_bundle": ("api/versioned-bundle.txt", escaped),
            "release_bundle": ("api/release-bundle.txt", escaped),
        }
        for channel, (relative_path, payload) in channels.items():
            with self.subTest(channel=channel), tempfile.TemporaryDirectory() as tmp:
                repo = copy_repo(Path(tmp))
                artifact = repo / relative_path
                prefix = artifact.read_text(encoding="utf-8") if artifact.exists() else ""
                artifact.write_text(prefix + "\n" + payload + "\n", encoding="utf-8")

                result = run_validator(repo)

                self.assertEqual(result.returncode, 1, result.stderr)
                self.assertIn(f"candidate API leaked into {channel}", result.stderr)

    def test_reference_normalization_does_not_interpret_arbitrary_escapes(self) -> None:
        for value in (
            r"api\x2f_candidate\x2fruntime-reference.md",
            r"api\n_candidate\truntime-reference.md",
        ):
            with self.subTest(value=value):
                self.assertEqual(_fully_decode_reference(value), value)

    def test_supported_claim_requires_publishable_evidence_metadata(self) -> None:
        mutations = {
            "publication": {"publication_status": "draft"},
            "claim": {"claim_status": "no-protocol-claims"},
            "hypothesis": {"hypothesis_status": "draft"},
            "owner": {"owner_domain": "architecture"},
            "different allowed source class": {"source_class": "vendor_public"},
            "different explicit falsifier": {
                "falsifier": "A different publishable observation contradicts this record."
            },
        }
        for name, updates in mutations.items():
            with self.subTest(name=name), tempfile.TemporaryDirectory() as tmp:
                repo = copy_repo(Path(tmp))
                replace_front_matter(repo / "evidence/EV-20260711-001.md", **updates)

                result = run_validator(repo)

                self.assertEqual(result.returncode, 1, result.stderr)
                self.assertIn(
                    "supported claim evidence is not publishable and evidence-backed",
                    result.stderr,
                )

    def test_supported_claim_body_is_bound_to_reviewed_content(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = copy_repo(Path(tmp))
            page = repo / "architecture/README.md"
            page.write_text(
                page.read_text(encoding="utf-8")
                + "\nThe adapter exposes an additional supported semantic projection.\n",
                encoding="utf-8",
            )

            result = run_validator(repo)

            self.assertEqual(result.returncode, 1, result.stderr)
            self.assertIn(
                "active architecture content is not in the reviewed claim registry",
                result.stderr,
            )

    def test_supported_claim_rejects_unreviewed_evidence_body(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = copy_repo(Path(tmp))
            evidence = repo / "evidence/EV-20260711-001.md"
            evidence.write_text(
                evidence.read_text(encoding="utf-8")
                + "\nThis unreviewed sentence purports to support another runtime claim.\n",
                encoding="utf-8",
            )

            result = run_validator(repo)

            self.assertEqual(result.returncode, 1, result.stderr)
            self.assertIn(
                "supported claim evidence is not publishable and evidence-backed",
                result.stderr,
            )

    def test_reviewed_claim_bindings_reject_additional_front_matter_keys(self) -> None:
        cases = {
            "active architecture": (
                "architecture/README.md",
                "active architecture content is not in the reviewed claim registry",
            ),
            "reviewed evidence": (
                "evidence/EV-20260711-001.md",
                "supported claim evidence is not publishable and evidence-backed",
            ),
        }
        for name, (relative_path, expected_error) in cases.items():
            with self.subTest(name=name), tempfile.TemporaryDirectory() as tmp:
                repo = copy_repo(Path(tmp))
                replace_front_matter(
                    repo / relative_path,
                    review_ticket="synthetic-extra-key",
                )

                result = run_validator(repo)

                self.assertEqual(result.returncode, 1, result.stderr)
                self.assertIn(expected_error, result.stderr)

    def test_cross_seed_link_and_snapshot_are_commit_path_consistent(self) -> None:
        mutations = {
            "mutable ref": lambda text: text.replace(
                f"blob/{PLATFORM_COMMIT}/", "blob/main/", 1
            ),
            "snapshot commit": lambda text: text.replace(
                f"@{PLATFORM_COMMIT}:", "@" + ("0" * 40) + ":", 1
            ),
            "snapshot path": lambda text: text.replace(
                "@" + PLATFORM_COMMIT + ":docs/platform/shared-registry-boundary.md",
                "@" + PLATFORM_COMMIT + ":docs/platform/not-the-linked-page.md",
                1,
            ),
        }
        for name, mutate in mutations.items():
            with self.subTest(name=name), tempfile.TemporaryDirectory() as tmp:
                repo = copy_repo(Path(tmp))
                page = repo / "architecture/README.md"
                page.write_text(mutate(page.read_text(encoding="utf-8")), encoding="utf-8")

                result = run_validator(repo)

                self.assertEqual(result.returncode, 1, result.stderr)
                self.assertIn("cross-seed commit, path, and snapshot must match", result.stderr)

    def test_equivalent_github_platform_urls_are_rejected_fail_closed(self) -> None:
        encoded_commit = "%2531" + PLATFORM_COMMIT[1:]
        variants = {
            "case variant": (
                "HTTPS://GITHUB.COM/project-helianthus/HELIANTHUS-DOCS-EBUS/"
                f"blob/{PLATFORM_COMMIT}/docs/platform/shared-registry-boundary.md"
            ),
            "mutable ref": (
                "https://github.com/Project-Helianthus/helianthus-docs-ebus/"
                "blob/main/docs/platform/shared-registry-boundary.md"
            ),
            "mutable slash ref": (
                "https://github.com/Project-Helianthus/helianthus-docs-ebus/"
                "blob/heads/main/docs/platform/shared-registry-boundary.md"
            ),
            "alternate raw host": (
                "https://RAW.GITHUBUSERCONTENT.COM/Project-Helianthus/"
                f"helianthus-docs-ebus/{PLATFORM_COMMIT}/docs/platform/"
                "shared-registry-boundary.md"
            ),
            "encoded dot segments": (
                "https://github.com/Project-Helianthus/helianthus-docs-ebus/"
                f"blob/{encoded_commit}/docs/platform/unused/%252e%252e/"
                "shared-registry-boundary.md"
            ),
        }
        for name, variant in variants.items():
            with self.subTest(name=name), tempfile.TemporaryDirectory() as tmp:
                repo = copy_repo(Path(tmp))
                page = repo / "architecture/README.md"
                text = page.read_text(encoding="utf-8").replace(PLATFORM_URL, variant, 1)
                if name == "encoded dot segments":
                    text = text.replace(
                        f"[shared registry boundary]({variant})",
                        f'<a href="{variant}">shared registry boundary</a>',
                        1,
                    )
                page.write_text(text, encoding="utf-8")

                result = run_validator(repo)

                self.assertEqual(result.returncode, 1, result.stderr)
                self.assertIn(
                    "platform URL must use canonical immutable commit/path form",
                    result.stderr,
                )
                self.assertIn("cross-seed commit, path, and snapshot must match", result.stderr)

    def test_visible_markdown_and_html_platform_destinations_are_fail_closed(self) -> None:
        variants = {
            "protocol-relative Markdown": (
                "//GitHub.COM/project-helianthus/HELIANTHUS-DOCS-EBUS/"
                f"blob/{PLATFORM_COMMIT}/docs/platform/shared-registry-boundary.md"
            ),
            "case-equivalent HTML": (
                "HTTPS://GITHUB.COM/project-helianthus/HELIANTHUS-DOCS-EBUS/"
                f"blob/{PLATFORM_COMMIT}/DOCS/PLATFORM/shared-registry-boundary.md"
            ),
        }
        for name, variant in variants.items():
            with self.subTest(name=name), tempfile.TemporaryDirectory() as tmp:
                repo = copy_repo(Path(tmp))
                page = repo / "architecture/README.md"
                text = page.read_text(encoding="utf-8")
                if name == "case-equivalent HTML":
                    replacement = f'<a href="{variant}">shared registry boundary</a>'
                    text = text.replace(
                        f"[shared registry boundary]({PLATFORM_URL})",
                        replacement,
                        1,
                    )
                else:
                    text = text.replace(PLATFORM_URL, variant, 1)
                page.write_text(text, encoding="utf-8")

                result = run_validator(repo)

                self.assertEqual(result.returncode, 1, result.stderr)
                self.assertIn(
                    "platform URL must use canonical immutable commit/path form",
                    result.stderr,
                )
                self.assertIn("cross-seed commit, path, and snapshot must match", result.stderr)

    def test_html_comments_do_not_supply_platform_link_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = copy_repo(Path(tmp))
            page = repo / "architecture/README.md"
            text = page.read_text(encoding="utf-8").replace(
                f"[shared registry boundary]({PLATFORM_URL})",
                f"<!-- [shared registry boundary]({PLATFORM_URL}) -->",
                1,
            )
            page.write_text(text, encoding="utf-8")

            result = run_validator(repo)

            self.assertEqual(result.returncode, 1, result.stderr)
            self.assertIn(
                "cross-seed metadata requires a canonical platform link",
                result.stderr,
            )

    def test_every_visible_platform_destination_must_be_the_single_canonical_url(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = copy_repo(Path(tmp))
            page = repo / "architecture/README.md"
            mutable = PLATFORM_URL.replace(f"blob/{PLATFORM_COMMIT}/", "blob/main/")
            page.write_text(
                page.read_text(encoding="utf-8")
                + f'\n<a href="{mutable}">mutable duplicate</a>\n',
                encoding="utf-8",
            )

            result = run_validator(repo)

            self.assertEqual(result.returncode, 1, result.stderr)
            self.assertIn(
                "platform URL must use canonical immutable commit/path form",
                result.stderr,
            )
            self.assertIn("cross-seed commit, path, and snapshot must match", result.stderr)

    def test_host_root_mutable_platform_duplicate_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = copy_repo(Path(tmp))
            page = repo / "architecture/README.md"
            mutable = (
                "/Project-Helianthus/helianthus-docs-ebus/blob/main/"
                "docs/platform/shared-registry-boundary.md"
            )
            page.write_text(
                page.read_text(encoding="utf-8")
                + f"\n[mutable duplicate]({mutable})\n",
                encoding="utf-8",
            )

            result = run_validator(repo)

            self.assertEqual(result.returncode, 1, result.stderr)
            self.assertIn(
                "platform URL must use canonical immutable commit/path form",
                result.stderr,
            )
            self.assertIn("cross-seed commit, path, and snapshot must match", result.stderr)

    def test_noncanonical_platform_link_still_runs_normative_summary_gate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = copy_repo(Path(tmp))
            page = repo / "architecture/README.md"
            text = page.read_text(encoding="utf-8").replace(
                PLATFORM_URL,
                PLATFORM_URL.replace("github.com", "GitHub.COM"),
                1,
            )
            page.write_text(
                text + "\nAn adapter must retain this copied platform requirement.\n",
                encoding="utf-8",
            )

            result = run_validator(repo)

            self.assertEqual(result.returncode, 1, result.stderr)
            self.assertIn(
                "platform URL must use canonical immutable commit/path form",
                result.stderr,
            )
            self.assertIn("summary-only cross-seed contains normative requirements", result.stderr)

    def test_cross_seed_snapshot_is_required_and_status_is_fail_closed(self) -> None:
        for name in ("missing", "not active"):
            with self.subTest(name=name), tempfile.TemporaryDirectory() as tmp:
                repo = copy_repo(Path(tmp))
                snapshot = repo / "scripts/platform_cross_seed_snapshot.yaml"
                if name == "missing":
                    snapshot.unlink()
                else:
                    snapshot.write_text(
                        snapshot.read_text(encoding="utf-8").replace(
                            "platform_contract_state: active",
                            "platform_contract_state: planned",
                            1,
                        ),
                        encoding="utf-8",
                    )

                result = run_validator(repo)

                self.assertEqual(result.returncode, 1, result.stderr)
                self.assertIn("platform cross-seed snapshot is unavailable or invalid", result.stderr)

    def test_cross_seed_rejects_copied_normative_platform_text(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = copy_repo(Path(tmp))
            page = repo / "architecture/README.md"
            page.write_text(
                page.read_text(encoding="utf-8")
                + "\nAn adapter may write only its native raw namespace and evidence references.\n",
                encoding="utf-8",
            )

            result = run_validator(repo)

            self.assertEqual(result.returncode, 1, result.stderr)
            self.assertIn("summary-only cross-seed contains normative requirements", result.stderr)

    def test_cross_seed_rejects_should_normative_language(self) -> None:
        for phrase in (
            "An adapter should preserve the canonical platform boundary.",
            "An adapter should not duplicate the canonical platform contract.",
        ):
            with self.subTest(phrase=phrase), tempfile.TemporaryDirectory() as tmp:
                repo = copy_repo(Path(tmp))
                page = repo / "architecture/README.md"
                page.write_text(
                    page.read_text(encoding="utf-8") + "\n" + phrase + "\n",
                    encoding="utf-8",
                )

                result = run_validator(repo)

                self.assertEqual(result.returncode, 1, result.stderr)
                self.assertIn(
                    "summary-only cross-seed contains normative requirements",
                    result.stderr,
                )

    def test_split_clean_milestone_metadata_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = copy_repo(Path(tmp))
            page = repo / "architecture/README.md"
            replace_front_matter(
                page,
                milestone="MSP-DOCS-CLEAN",
                milestone_completion="complete",
            )

            result = run_validator(repo)

            self.assertEqual(result.returncode, 1, result.stderr)
            self.assertIn("MSP-DOCS-CLEAN cannot be claimed during MSP-DOCS-E2", result.stderr)

    def test_clean_milestone_metadata_is_normalized_before_rejection(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = copy_repo(Path(tmp))
            page = repo / "architecture/README.md"
            replace_front_matter(
                page,
                milestone="  mSp-DoCs-ClEaN  ",
                milestone_completion="  CoMpLeTe  ",
            )

            result = run_validator(repo)

            self.assertEqual(result.returncode, 1, result.stderr)
            self.assertIn("MSP-DOCS-CLEAN cannot be claimed during MSP-DOCS-E2", result.stderr)


if __name__ == "__main__":
    unittest.main()
