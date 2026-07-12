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

from validate_repository_policy import (
    _fully_decode_reference,
    _visible_headings,
    _visible_link_destinations,
    _visible_markdown_text,
)


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


def write_evidence_backed_page(repo: Path, relative_path: str, body: str) -> Path:
    path = repo / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    owner_domain = relative_path.split("/", 1)[0]
    license_id = "AGPL-3.0-only" if owner_domain in {"api", "architecture"} else "CC0-1.0"
    metadata = {
        "canonical_source": (
            "Project-Helianthus/helianthus-docs-eebus:" + relative_path
        ),
        "owner_domain": owner_domain,
        "license": license_id,
        "publication_status": "active",
        "claim_status": "evidence-backed",
        "source_class": "derived_inference",
        "evidence_ids": "EV-20260711-001",
        "hypothesis_status": "publishable",
        "falsifier": "A publishable public source contradicts this synthetic claim.",
    }
    rendered = yaml.safe_dump(metadata, sort_keys=False)
    path.write_text(f"---\n{rendered}---\n\n{body}\n", encoding="utf-8")
    return path


class MspDocsE2RemediationTests(unittest.TestCase):
    def test_clean_stable_publication_artifacts_are_allowed_and_parsed(self) -> None:
        artifacts = {
            "api/search-index.json": (
                '{"pages":["README.md","api/api-surface-v1.md"]}\n'
            ),
            "api/sitemap.xml": (
                '<?xml version="1.0" encoding="UTF-8"?>\n'
                '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
                "<url><loc>README.md</loc></url>"
                "<url><loc>api/api-surface-v1.md</loc></url></urlset>\n"
            ),
            "api/versioned-bundle.txt": "README.md\napi/api-surface-v1.md\n",
            "api/release-bundle.txt": "README.md\napi/api-surface-v1.md\n",
        }
        with tempfile.TemporaryDirectory() as tmp:
            repo = copy_repo(Path(tmp))
            for relative_path, payload in artifacts.items():
                (repo / relative_path).write_text(payload, encoding="utf-8")

            result = run_validator(repo)

            self.assertEqual(result.returncode, 0, result.stderr)

    def test_search_and_bundle_entries_require_canonical_byte_order(self) -> None:
        artifacts = {
            "api/search-index.json": (
                '{"pages":["api/api-surface-v1.md","README.md"]}\n'
            ),
            "api/versioned-bundle.txt": "api/api-surface-v1.md\nREADME.md\n",
            "api/release-bundle.txt": "api/api-surface-v1.md\nREADME.md\n",
        }
        for relative_path, payload in artifacts.items():
            with self.subTest(relative_path=relative_path), tempfile.TemporaryDirectory() as tmp:
                repo = copy_repo(Path(tmp))
                (repo / relative_path).write_text(payload, encoding="utf-8")

                result = run_validator(repo)

                self.assertEqual(result.returncode, 1, result.stderr)
                self.assertIn("non-canonical publication entry ordering", result.stderr)

    def test_unregistered_publication_artifacts_are_rejected_repository_wide(self) -> None:
        artifacts = {
            "public/search-index.json": '{"pages":["api/api-surface-v1.md"]}\n',
            "site/sitemap.xml": (
                '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
                "<url><loc>api/api-surface-v1.md</loc></url></urlset>\n"
            ),
            "exports/release-bundle.txt": "api/api-surface-v1.md\n",
            "output/public-export.json": '{"pages":["README.md"]}\n',
        }
        for relative_path, payload in artifacts.items():
            with self.subTest(relative_path=relative_path), tempfile.TemporaryDirectory() as tmp:
                repo = copy_repo(Path(tmp))
                artifact = repo / relative_path
                artifact.parent.mkdir(parents=True, exist_ok=True)
                artifact.write_text(payload, encoding="utf-8")

                result = run_validator(repo)

                self.assertEqual(result.returncode, 1, result.stderr)
                self.assertIn("unregistered stable publication artifact", result.stderr)

    def test_only_reviewed_supported_api_contract_may_publish_outside_candidate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = copy_repo(Path(tmp))
            write_evidence_backed_page(
                repo,
                "api/runtime-api.md",
                (
                    "# Supported Runtime API\n\n"
                    "Package `runtime` exports `NewAdapter` and supports live connections."
                ),
            )

            result = run_validator(repo)

            self.assertEqual(result.returncode, 1, result.stderr)
            self.assertIn(
                "API content is not in the reviewed supported API registry",
                result.stderr,
            )

    def test_repository_wide_confidentiality_scan_covers_unowned_text_artifacts(self) -> None:
        cases = {
            "credential": ('client_secret: "synthetic-secret"\n', "populated sensitive field"),
            "private artifact": (
                "private artifact reference: synthetic-capture.json\n",
                "private artifact location/reference field is forbidden",
            ),
            "home path": ("Capture: /Users/synthetic-user/capture.json\n", "private or identifying filesystem path found"),
            "MAC": ("Peer: 00:11:22:33:44:55\n", "MAC address found in publishable content"),
            "private IPv4": (
                "Peer: " + ".".join(("10", "23", "4", "5")) + "\n",
                "private IPv4 address found",
            ),
            "IPv6": ("Peer: fd00::1\n", "IPv6 address found in publishable content"),
        }
        for name, (payload, diagnostic) in cases.items():
            with self.subTest(name=name), tempfile.TemporaryDirectory() as tmp:
                repo = copy_repo(Path(tmp))
                artifact = repo / "misc/notes.txt"
                artifact.parent.mkdir()
                artifact.write_text(payload, encoding="utf-8")

                result = run_validator(repo)

                self.assertEqual(result.returncode, 1, result.stderr)
                self.assertIn(diagnostic, result.stderr)

    def test_repository_wide_confidentiality_scan_allows_public_controls(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = copy_repo(Path(tmp))
            artifact = repo / "misc/notes.txt"
            artifact.parent.mkdir()
            artifact.write_text(
                "Credential: <redacted>\n"
                '  "client_secret": "<redacted>",\n'
                "Public documentation endpoint: 203.0.113.10\n"
                "Generic roots /Users/ and /home/ are discussed without identities.\n",
                encoding="utf-8",
            )

            result = run_validator(repo)

            self.assertEqual(result.returncode, 0, result.stderr)

    def test_platform_normative_copy_requires_canonical_summary_link_policy(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = copy_repo(Path(tmp))
            write_evidence_backed_page(
                repo,
                "protocols/copied-platform-rule.md",
                (
                    "# Local Rule\n\n"
                    "An adapter may write only its native raw namespace and evidence references."
                ),
            )

            result = run_validator(repo)

            self.assertEqual(result.returncode, 1, result.stderr)
            self.assertIn(
                "platform-owned normative text requires canonical summary-only cross-seed policy",
                result.stderr,
            )

    def test_restricted_and_terminal_gates_normalize_rendered_entities(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = copy_repo(Path(tmp))
            write_evidence_backed_page(
                repo,
                "protocols/entity-restricted.md",
                "# Source\n\nThis uses vendor&#95;restricted material.",
            )
            readme = repo / "README.md"
            readme.write_text(
                readme.read_text(encoding="utf-8")
                + "\nMSP-DOCS-**CLE&#65;N** is complete.\n",
                encoding="utf-8",
            )

            result = run_validator(repo)

            self.assertEqual(result.returncode, 1, result.stderr)
            self.assertIn("restricted-source contamination marker found", result.stderr)
            self.assertIn("premature docs milestone or code-doc absence claim", result.stderr)

    def test_clean_metadata_gate_normalizes_html_entities(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = copy_repo(Path(tmp))
            replace_front_matter(
                repo / "architecture/README.md",
                milestone="MSP-DOCS-CLE&#65;N",
                milestone_completion="compl&#x65;te",
            )

            result = run_validator(repo)

            self.assertEqual(result.returncode, 1, result.stderr)
            self.assertIn(
                "MSP-DOCS-CLEAN cannot be claimed during MSP-DOCS-E2",
                result.stderr,
            )

    def test_malformed_stable_publication_artifacts_fail_their_structured_format(self) -> None:
        artifacts = {
            "api/search-index.json": '{"pages":[}\n',
            "api/sitemap.xml": "<urlset><url></urlset>\n",
            "api/versioned-bundle.txt": "api/api-surface-v1.md extra-column\n",
            "api/release-bundle.txt": "../api/api-surface-v1.md\n",
        }
        for relative_path, payload in artifacts.items():
            with self.subTest(relative_path=relative_path), tempfile.TemporaryDirectory() as tmp:
                repo = copy_repo(Path(tmp))
                (repo / relative_path).write_text(payload, encoding="utf-8")

                result = run_validator(repo)

                self.assertEqual(result.returncode, 1, result.stderr)
                self.assertIn("invalid stable publication artifact", result.stderr)

    def test_search_artifact_requires_strict_json_at_every_object_depth(self) -> None:
        payloads = {
            "NaN": '{"score":NaN}\n',
            "positive infinity": '{"score":Infinity}\n',
            "negative infinity": '{"score":-Infinity}\n',
            "duplicate root key": '{"page":"first","page":"second"}\n',
            "duplicate nested key": (
                '{"pages":[{"path":"first","path":"second"}]}\n'
            ),
        }
        for name, payload in payloads.items():
            with self.subTest(name=name), tempfile.TemporaryDirectory() as tmp:
                repo = copy_repo(Path(tmp))
                (repo / "api/search-index.json").write_text(
                    payload,
                    encoding="utf-8",
                )

                result = run_validator(repo)

                self.assertEqual(result.returncode, 1, result.stderr)
                self.assertIn("invalid stable publication artifact", result.stderr)

    def test_search_artifact_requires_exact_pages_schema_and_stable_entries(self) -> None:
        payloads = {
            "wrong root": '["api/api-surface-v1.md"]\n',
            "extra field": '{"pages":["api/api-surface-v1.md"],"version":1}\n',
            "wrong pages type": '{"pages":"api/api-surface-v1.md"}\n',
            "duplicate page": (
                '{"pages":["api/api-surface-v1.md","api/api-surface-v1.md"]}\n'
            ),
            "missing page": '{"pages":["api/not-found.md"]}\n',
            "candidate page": '{"pages":["api/_candidate/runtime-reference.md"]}\n',
        }
        for name, payload in payloads.items():
            with self.subTest(name=name), tempfile.TemporaryDirectory() as tmp:
                repo = copy_repo(Path(tmp))
                (repo / "api/search-index.json").write_text(payload, encoding="utf-8")

                result = run_validator(repo)

                self.assertEqual(result.returncode, 1, result.stderr)
                self.assertIn("invalid stable publication artifact", result.stderr)

    def test_sitemap_requires_namespaced_urlset_url_loc_schema(self) -> None:
        namespace = "http://www.sitemaps.org/schemas/sitemap/0.9"
        payloads = {
            "wrong root": f'<sitemapindex xmlns="{namespace}" />\n',
            "missing namespace": (
                "<urlset><url><loc>api/api-surface-v1.md</loc></url></urlset>\n"
            ),
            "wrong namespace": (
                '<urlset xmlns="https://example.invalid/sitemap">'
                "<url><loc>api/api-surface-v1.md</loc></url></urlset>\n"
            ),
            "missing loc": f'<urlset xmlns="{namespace}"><url /></urlset>\n',
            "nested loc": (
                f'<urlset xmlns="{namespace}"><loc>api/api-surface-v1.md</loc></urlset>\n'
            ),
            "nonexistent loc": (
                f'<urlset xmlns="{namespace}"><url><loc>api/not-found.md</loc>'
                "</url></urlset>\n"
            ),
        }
        for name, payload in payloads.items():
            with self.subTest(name=name), tempfile.TemporaryDirectory() as tmp:
                repo = copy_repo(Path(tmp))
                (repo / "api/sitemap.xml").write_text(payload, encoding="utf-8")

                result = run_validator(repo)

                self.assertEqual(result.returncode, 1, result.stderr)
                self.assertIn("invalid stable publication artifact", result.stderr)

    def test_bundles_require_unique_existing_stable_repository_paths(self) -> None:
        payloads = {
            "duplicate": "api/api-surface-v1.md\napi/api-surface-v1.md\n",
            "nonexistent": "api/not-found.md\n",
            "candidate": "api/_candidate/runtime-reference.md\n",
            "nonpublishable": "scripts/validate_repository_policy.py\n",
        }
        for channel in ("versioned-bundle.txt", "release-bundle.txt"):
            for name, payload in payloads.items():
                with self.subTest(channel=channel, name=name), tempfile.TemporaryDirectory() as tmp:
                    repo = copy_repo(Path(tmp))
                    (repo / "api" / channel).write_text(payload, encoding="utf-8")

                    result = run_validator(repo)

                    self.assertEqual(result.returncode, 1, result.stderr)
                    self.assertIn("invalid stable publication artifact", result.stderr)

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

    def test_github_contents_api_candidate_urls_cannot_leak(self) -> None:
        channels = {
            "stable_navigation": "README.md",
            "search": "api/search-index.json",
            "sitemap": "api/sitemap.xml",
            "versioned_bundle": "api/versioned-bundle.txt",
            "release_bundle": "api/release-bundle.txt",
        }
        candidate_url = (
            "https://api.github.com/repos/Project-Helianthus/"
            "helianthus-docs-eebus/contents/api/_candidate/runtime-reference.md"
        )
        payloads = {
            "absolute URL": candidate_url,
            "serialized escaped URL": (
                '{"url":"' + candidate_url.replace("/", r"\/") + '"}'
            ),
            "nested encoded URL": candidate_url.replace(
                "api/_candidate", "api/%255fcandidate"
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

    def test_template_anchors_do_not_supply_platform_link_evidence(self) -> None:
        hidden = f'<template><a href="{PLATFORM_URL}">platform</a></template>'
        self.assertEqual(_visible_link_destinations(hidden), [])

        with tempfile.TemporaryDirectory() as tmp:
            repo = copy_repo(Path(tmp))
            page = repo / "architecture/README.md"
            page.write_text(
                page.read_text(encoding="utf-8").replace(
                    f"[shared registry boundary]({PLATFORM_URL})",
                    hidden,
                    1,
                ),
                encoding="utf-8",
            )

            result = run_validator(repo)

            self.assertEqual(result.returncode, 1, result.stderr)
            self.assertIn(
                "cross-seed metadata requires a canonical platform link",
                result.stderr,
            )

    def test_hidden_html_state_propagates_to_descendant_cross_seed_anchors(self) -> None:
        hidden_forms = {
            "hidden ancestor": f'<div hidden><a href="{PLATFORM_URL}">platform</a></div>',
            "hidden anchor": f'<a hidden href="{PLATFORM_URL}">platform</a>',
            "aria hidden ancestor": (
                f'<section aria-hidden="TRUE"><a href="{PLATFORM_URL}">platform</a></section>'
            ),
            "inert ancestor": f'<div inert><a href="{PLATFORM_URL}">platform</a></div>',
        }
        for name, hidden in hidden_forms.items():
            with self.subTest(name=name), tempfile.TemporaryDirectory() as tmp:
                self.assertEqual(_visible_link_destinations(hidden), [])
                repo = copy_repo(Path(tmp))
                page = repo / "architecture/README.md"
                page.write_text(
                    page.read_text(encoding="utf-8").replace(
                        f"[shared registry boundary]({PLATFORM_URL})",
                        hidden,
                        1,
                    ),
                    encoding="utf-8",
                )

                result = run_validator(repo)

                self.assertEqual(result.returncode, 1, result.stderr)
                self.assertIn(
                    "cross-seed metadata requires a canonical platform link",
                    result.stderr,
                )

    def test_false_aria_hidden_does_not_hide_cross_seed_anchor(self) -> None:
        visible = (
            f'<div aria-hidden="false"><a href="{PLATFORM_URL}">platform</a></div>'
        )
        self.assertEqual(_visible_link_destinations(visible), [PLATFORM_URL])

    def test_template_state_crosses_commonmark_tokens_until_matching_close(self) -> None:
        visible_url = "https://example.invalid/visible"
        hidden = (
            "prefix <template>\n\n"
            "# Hidden heading\n\n"
            f"[hidden platform link]({PLATFORM_URL})\n\n"
            "</style>\n\n"
            f'<a href="{PLATFORM_URL}">hidden HTML link</a>\n\n'
            "</template>\n\n"
            "# Visible heading\n\n"
            f"[visible link]({visible_url})\n"
        )
        self.assertEqual(_visible_link_destinations(hidden), [visible_url])
        self.assertEqual(_visible_headings(hidden), {"Visible heading"})
        visible_text = _visible_markdown_text(hidden)
        self.assertNotIn("hidden platform link", visible_text)
        self.assertNotIn("hidden HTML link", visible_text)
        self.assertIn("visible link", visible_text)

        with tempfile.TemporaryDirectory() as tmp:
            repo = copy_repo(Path(tmp))
            page = repo / "architecture/README.md"
            page.write_text(
                page.read_text(encoding="utf-8").replace(
                    f"[shared registry boundary]({PLATFORM_URL})",
                    hidden,
                    1,
                ),
                encoding="utf-8",
            )

            result = run_validator(repo)

            self.assertEqual(result.returncode, 1, result.stderr)
            self.assertIn(
                "cross-seed metadata requires a canonical platform link",
                result.stderr,
            )

    def test_hidden_and_non_link_destinations_do_not_supply_cross_seed_evidence(self) -> None:
        hidden_forms = {
            "terminated comment": f"<!-- [hidden]({PLATFORM_URL}) -->",
            "unterminated comment": f"<!-- [hidden]({PLATFORM_URL})",
            "inline code": f"`[hidden]({PLATFORM_URL})`",
            "fenced code": f"```markdown\n[hidden]({PLATFORM_URL})\n```",
            "unterminated fence": f"```markdown\n[hidden]({PLATFORM_URL})",
            "image": f"![hidden]({PLATFORM_URL})",
            "bare URL": PLATFORM_URL,
            "non-anchor href": f'<link href="{PLATFORM_URL}">',
        }
        for name, replacement in hidden_forms.items():
            with self.subTest(name=name), tempfile.TemporaryDirectory() as tmp:
                repo = copy_repo(Path(tmp))
                page = repo / "architecture/README.md"
                text = page.read_text(encoding="utf-8").replace(
                    f"[shared registry boundary]({PLATFORM_URL})",
                    replacement,
                    1,
                )
                page.write_text(text, encoding="utf-8")

                result = run_validator(repo)

                self.assertEqual(result.returncode, 1, result.stderr)
                self.assertIn(
                    "cross-seed metadata requires a canonical platform link",
                    result.stderr,
                )

    def test_actual_markdown_and_html_anchors_expose_destinations(self) -> None:
        forms = {
            "inline Markdown": f"[platform]({PLATFORM_URL})",
            "angle Markdown destination": f"[platform](<{PLATFORM_URL}>)",
            "Markdown autolink": f"<{PLATFORM_URL}>",
            "full reference Markdown": (
                f"[platform][contract]\n\n[contract]: {PLATFORM_URL}"
            ),
            "shortcut reference Markdown": (
                f"[contract]\n\n[contract]: {PLATFORM_URL}"
            ),
            "HTML anchor": f'<a href="{PLATFORM_URL}">platform</a>',
            "fence shields comment marker": (
                f"```text\n<!--\n```\n[platform]({PLATFORM_URL})"
            ),
            "comment shields fence marker": (
                f"<!--\n```\n-->\n[platform]({PLATFORM_URL})"
            ),
            "inline code shields comment marker": (
                f"`<!--` [platform]({PLATFORM_URL})"
            ),
            "escaped image marker is a link": f"\\![platform]({PLATFORM_URL})",
            "destination with title": f'[platform](<{PLATFORM_URL}> "contract")',
        }
        for name, text in forms.items():
            with self.subTest(name=name):
                self.assertEqual(_visible_link_destinations(text), [PLATFORM_URL])

    def test_commonmark_code_and_image_forms_do_not_expose_destinations(self) -> None:
        hidden_forms = {
            "indented code": f"    [hidden]({PLATFORM_URL})\n",
            "image": f"![hidden]({PLATFORM_URL})",
            "image reference": f"![hidden][contract]\n\n[contract]: {PLATFORM_URL}",
            "comment": f"<!-- [hidden]({PLATFORM_URL}) -->",
            "unterminated comment": f"<!-- [hidden]({PLATFORM_URL})",
            "fenced code": f"~~~markdown\n[hidden]({PLATFORM_URL})\n~~~",
        }
        for name, text in hidden_forms.items():
            with self.subTest(name=name):
                self.assertEqual(_visible_link_destinations(text), [])

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

    def test_cross_seed_rejects_remaining_normative_forms(self) -> None:
        phrases = (
            "Only adapters may write the protocol-native namespace.",
            "Preserve the canonical platform boundary.",
            "Do not duplicate the canonical platform contract.",
            "The canonical platform boundary is mandatory.",
            "A canonical platform handoff is required.",
            "Adapters are required to preserve the platform handoff.",
            "Adapters must preserve the platform handoff.",
            "Adapters should preserve the platform handoff.",
        )
        for phrase in phrases:
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

    def test_every_production_cross_seed_page_requires_reviewed_exact_content(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = copy_repo(Path(tmp))
            page = repo / "devices/unreviewed-cross-seed.md"
            metadata = {
                "canonical_source": (
                    "Project-Helianthus/helianthus-docs-eebus:"
                    "devices/unreviewed-cross-seed.md"
                ),
                "owner_domain": "devices",
                "license": "CC0-1.0",
                "publication_status": "publishable",
                "claim_status": "evidence-backed",
                "source_class": "derived_inference",
                "evidence_ids": "EV-20260711-001",
                "hypothesis_status": "publishable",
                "falsifier": "A publishable canonical contract supersedes this summary.",
                "cross_seed_target": (
                    "Project-Helianthus/helianthus-docs-ebus:"
                    "docs/platform/shared-registry-boundary.md"
                ),
                "cross_seed_mode": "summary-only",
                "cross_seed_snapshot": (
                    "Project-Helianthus/helianthus-docs-ebus@"
                    f"{PLATFORM_COMMIT}:docs/platform/shared-registry-boundary.md"
                ),
            }
            rendered = yaml.safe_dump(metadata, sort_keys=False)
            page.write_text(
                f"---\n{rendered}---\n\n# Local Summary\n\n"
                "Responsibility stays with the linked platform contract.\n\n"
                f"[platform]({PLATFORM_URL})\n",
                encoding="utf-8",
            )

            result = run_validator(repo)

            self.assertEqual(result.returncode, 1, result.stderr)
            self.assertIn(
                "cross-seed content is not in the reviewed claim registry",
                result.stderr,
            )

    def test_private_artifact_labels_accept_no_separator_bypass(self) -> None:
        labels = (
            "Private artifact location",
            "Private_artifact_reference",
            "Private-artifact-filename",
            "Private artifact_hash",
            "Private_artifact-identifier",
        )
        for label in labels:
            with self.subTest(label=label), tempfile.TemporaryDirectory() as tmp:
                repo = copy_repo(Path(tmp))
                page = repo / "re-notes/template.md"
                page.write_text(
                    page.read_text(encoding="utf-8") + f"\n- {label}: redacted\n",
                    encoding="utf-8",
                )

                result = run_validator(repo)

                self.assertEqual(result.returncode, 1, result.stderr)
                self.assertIn(
                    "private artifact location/reference field is forbidden",
                    result.stderr,
                )

    def test_private_volume_paths_are_rejected_in_publishable_content(self) -> None:
        for relative_path in ("re-notes/template.md", "evidence/volume-path.txt"):
            with self.subTest(relative_path=relative_path), tempfile.TemporaryDirectory() as tmp:
                repo = copy_repo(Path(tmp))
                artifact = repo / relative_path
                prefix = artifact.read_text(encoding="utf-8") if artifact.exists() else ""
                artifact.write_text(
                    prefix + "\nCapture path: /Volumes/Operator/capture.json\n",
                    encoding="utf-8",
                )

                result = run_validator(repo)

                self.assertEqual(result.returncode, 1, result.stderr)
                self.assertIn("private or identifying filesystem path found", result.stderr)

    def test_private_assignments_and_decoded_paths_are_normalized_before_scanning(self) -> None:
        payloads = (
            "Private artifact location = /root/capture.json",
            "Private_artifact_reference = %2FUsers%2Fencoded-user%2Fcapture.json",
            "Private-artifact-filename:%2FVolumes%2FOperator%2Fcapture.json",
            "Private%20artifact%20hash%20%3D%20redacted",
        )
        for payload in payloads:
            with self.subTest(payload=payload), tempfile.TemporaryDirectory() as tmp:
                repo = copy_repo(Path(tmp))
                (repo / "evidence/private-assignment.txt").write_text(
                    payload + "\n",
                    encoding="utf-8",
                )

                result = run_validator(repo)

                self.assertEqual(result.returncode, 1, result.stderr)
                self.assertIn(
                    "private artifact location/reference field is forbidden",
                    result.stderr,
                )

    def test_root_and_encoded_user_or_volume_paths_are_rejected(self) -> None:
        paths = (
            "/root/capture.json",
            "%2FUsers%2Fencoded-user%2Fcapture.json",
            "%252FVolumes%252FOperator%252Fcapture.json",
        )
        for private_path in paths:
            with self.subTest(private_path=private_path), tempfile.TemporaryDirectory() as tmp:
                repo = copy_repo(Path(tmp))
                (repo / "evidence/private-path.txt").write_text(
                    f"Capture: {private_path}\n",
                    encoding="utf-8",
                )

                result = run_validator(repo)

                self.assertEqual(result.returncode, 1, result.stderr)
                self.assertIn("private or identifying filesystem path found", result.stderr)

    def test_bare_and_descendant_home_paths_are_rejected(self) -> None:
        paths = (
            "/Users/operator",
            "/Users/operator/capture.json",
            "/home/operator",
            "/home/operator/capture.json",
            "/root",
            "/root/capture.json",
        )
        for private_path in paths:
            with self.subTest(private_path=private_path), tempfile.TemporaryDirectory() as tmp:
                repo = copy_repo(Path(tmp))
                (repo / "evidence/private-path.txt").write_text(
                    f"Capture: {private_path}\n",
                    encoding="utf-8",
                )

                result = run_validator(repo)

                self.assertEqual(result.returncode, 1, result.stderr)
                self.assertIn("private or identifying filesystem path found", result.stderr)

    def test_home_paths_before_prose_and_markdown_boundaries_are_rejected(self) -> None:
        paths = (
            "/Users/operator,",
            "/Users/operator)",
            "/Users/operator]",
            "/Users/operator**",
            "/home/operator.",
            "/home/operator`",
            "/home/operator_",
            "/home/operator/capture.json",
            "/Users/operator/capture.json),",
            "/root!",
            "/root)",
            "/root]",
            "/root**",
            "/root/capture.json",
            "/root/capture.json`",
        )
        for private_path in paths:
            with self.subTest(private_path=private_path), tempfile.TemporaryDirectory() as tmp:
                repo = copy_repo(Path(tmp))
                (repo / "evidence/private-path.txt").write_text(
                    f"Capture: {private_path}\n",
                    encoding="utf-8",
                )

                result = run_validator(repo)

                self.assertEqual(result.returncode, 1, result.stderr)
                self.assertIn("private or identifying filesystem path found", result.stderr)

    def test_encoded_home_paths_are_decoded_by_the_artifact_pipeline(self) -> None:
        payloads = (
            '{"path":"%252FUsers%252Fencoded-user"}\n',
            r'{"path":"\u002fhome\u002fescaped-user\u002fcapture.json"}' + "\n",
            '{"path":"&#47;root"}\n',
        )
        for payload in payloads:
            with self.subTest(payload=payload), tempfile.TemporaryDirectory() as tmp:
                repo = copy_repo(Path(tmp))
                (repo / "api/search-index.json").write_text(
                    payload,
                    encoding="utf-8",
                )

                result = run_validator(repo)

                self.assertEqual(result.returncode, 1, result.stderr)
                self.assertIn("private or identifying filesystem path found", result.stderr)

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

    def test_alternate_clean_completion_fields_and_terminal_synonyms_are_rejected(self) -> None:
        cases = (
            {"milestone": "MSP-DOCS-CLEAN", "status": "available"},
            {"milestone": "MSP-DOCS-CLEAN", "complete": "ready"},
            {"milestone": "MSP-DOCS-CLEAN", "completion": "landed"},
            {"status": "MSP-DOCS-CLEAN available"},
            {"completion": "completed: MSP-DOCS-CLEAN"},
            {"milestone": "MSP-DOCS-CLEAN", "status": "withdrawn"},
            {"milestone": "MSP-DOCS-CLEAN", "state": "removed"},
            {"milestone": "MSP-DOCS-CLEAN", "completion": "succeeded"},
            {"status": "MSP DOCS CLEAN - superseded"},
            {"lifecycle": "MSP-DOCS-CLEAN / failed"},
        )
        for metadata in cases:
            with self.subTest(metadata=metadata), tempfile.TemporaryDirectory() as tmp:
                repo = copy_repo(Path(tmp))
                replace_front_matter(repo / "architecture/README.md", **metadata)

                result = run_validator(repo)

                self.assertEqual(result.returncode, 1, result.stderr)
                self.assertIn(
                    "MSP-DOCS-CLEAN cannot be claimed during MSP-DOCS-E2",
                    result.stderr,
                )

    def test_clean_terminal_state_and_lifecycle_fields_are_rejected(self) -> None:
        cases = (
            {"state": "  CoMpLeTe  "},
            {"lifecycle_state": "ready"},
            {"delivery_phase": "landed"},
            {"release_stage": "published"},
        )
        for lifecycle in cases:
            with self.subTest(lifecycle=lifecycle), tempfile.TemporaryDirectory() as tmp:
                repo = copy_repo(Path(tmp))
                replace_front_matter(
                    repo / "architecture/README.md",
                    milestone="MSP-DOCS-CLEAN",
                    publication_status="draft",
                    **lifecycle,
                )

                result = run_validator(repo)

                self.assertEqual(result.returncode, 1, result.stderr)
                self.assertIn(
                    "MSP-DOCS-CLEAN cannot be claimed during MSP-DOCS-E2",
                    result.stderr,
                )


if __name__ == "__main__":
    unittest.main()
