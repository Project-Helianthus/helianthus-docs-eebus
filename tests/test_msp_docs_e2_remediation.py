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
PLATFORM_COMMIT = "153191f72b5b9ecacbadcf2f3d7e480c6fef89a4"
CANDIDATE_PATH = "api/_candidate/runtime-reference.md"


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

    def test_supported_claim_requires_publishable_evidence_metadata(self) -> None:
        mutations = {
            "publication": {"publication_status": "draft"},
            "claim": {"claim_status": "no-protocol-claims"},
            "hypothesis": {"hypothesis_status": "draft"},
            "owner": {"owner_domain": "architecture"},
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


if __name__ == "__main__":
    unittest.main()
