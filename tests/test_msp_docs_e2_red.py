from __future__ import annotations

import copy
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any

import yaml


REPO = Path(__file__).resolve().parents[1]
VALIDATOR = REPO / "scripts" / "validate_repository_policy.py"
CONTRACT = REPO / "tests" / "fixtures" / "msp_docs_e2_contract.yaml"
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


def load_contract() -> dict[str, Any]:
    document = yaml.safe_load(CONTRACT.read_text(encoding="utf-8"))
    if not isinstance(document, dict):
        raise AssertionError("E2 contract fixture must be a mapping")
    return document


def write_page(repo: Path, specification: dict[str, Any]) -> Path:
    relative_path = specification["relative_path"]
    path = repo / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    front_matter = yaml.safe_dump(
        specification["front_matter"],
        allow_unicode=False,
        default_flow_style=False,
        sort_keys=False,
    )
    path.write_text(
        f"---\n{front_matter}---\n\n{specification['body']}",
        encoding="utf-8",
    )
    return path


def materialize_claim(
    repo: Path,
    section: str,
    *,
    relative_path: str | None = None,
    metadata: dict[str, str] | None = None,
    body: str | None = None,
) -> Path:
    contract = load_contract()
    write_page(repo, contract["evidence"])
    specification = copy.deepcopy(contract[section])
    if relative_path is not None:
        specification["relative_path"] = relative_path
        specification["front_matter"]["canonical_source"] = (
            "Project-Helianthus/helianthus-docs-eebus:" + relative_path
        )
    if metadata:
        specification["front_matter"].update(metadata)
    if body is not None:
        specification["body"] = body
    return write_page(repo, specification)


class MspDocsE2RedTests(unittest.TestCase):
    def test_supported_architecture_can_replace_the_planned_scaffold(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = copy_repo(Path(tmp))
            materialize_claim(repo, "architecture")

            result = run_validator(repo)

            self.assertEqual(result.returncode, 0, result.stderr)

    def test_active_architecture_rejects_unsupported_promotion(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = copy_repo(Path(tmp))
            materialize_claim(
                repo,
                "architecture",
                relative_path="architecture/unsupported.md",
                metadata={"hypothesis_status": "draft"},
            )

            result = run_validator(repo)

            self.assertEqual(result.returncode, 1, result.stderr)
            self.assertIn(
                "active architecture claim lacks publishable support",
                result.stderr,
            )

    def test_active_architecture_rejects_restricted_origin_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = copy_repo(Path(tmp))
            materialize_claim(
                repo,
                "architecture",
                relative_path="architecture/quarantine-negative.md",
                metadata={"restricted_input_locator": "synthetic-quarantined-input.pdf"},
            )

            result = run_validator(repo)

            self.assertEqual(result.returncode, 1, result.stderr)
            self.assertIn(
                "restricted-source provenance metadata is forbidden",
                result.stderr,
            )

    def test_cross_seed_target_must_be_an_active_canonical_platform_page(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = copy_repo(Path(tmp))
            missing_target = "docs/platform/not-an-active-contract.md"
            materialize_claim(
                repo,
                "architecture",
                relative_path="architecture/stale-cross-seed.md",
                metadata={
                    "cross_seed_target": (
                        "Project-Helianthus/helianthus-docs-ebus:" + missing_target
                    )
                },
                body=(
                    "# Stale Cross-Seed\n\n"
                    "Canonical platform source: "
                    "[missing](https://github.com/Project-Helianthus/"
                    "helianthus-docs-ebus/blob/main/"
                    f"{missing_target})\n"
                ),
            )

            result = run_validator(repo)

            self.assertEqual(result.returncode, 1, result.stderr)
            self.assertIn(
                "cross-seed target is not an active canonical platform page",
                result.stderr,
            )

    def test_cross_seed_summary_cannot_restate_normative_requirements(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = copy_repo(Path(tmp))
            materialize_claim(
                repo,
                "architecture",
                relative_path="architecture/copied-requirement.md",
                body=(
                    "# Local Architecture Note\n\n"
                    "Every adapter must implement the canonical platform merge rule.\n\n"
                    "Canonical platform source: "
                    "[shared registry boundary](https://github.com/"
                    "Project-Helianthus/helianthus-docs-ebus/blob/main/"
                    "docs/platform/shared-registry-boundary.md)\n"
                ),
            )

            result = run_validator(repo)

            self.assertEqual(result.returncode, 1, result.stderr)
            self.assertIn(
                "summary-only cross-seed contains normative requirements",
                result.stderr,
            )

    def test_candidate_api_declared_outputs_are_candidate_only(self) -> None:
        stable_channels = (
            "stable_navigation",
            "search",
            "sitemap",
            "versioned_bundle",
            "release_bundle",
        )
        for channel in stable_channels:
            with self.subTest(channel=channel), tempfile.TemporaryDirectory() as tmp:
                repo = copy_repo(Path(tmp))
                materialize_claim(
                    repo,
                    "candidate_api",
                    metadata={channel: "true"},
                )

                result = run_validator(repo)

                self.assertEqual(result.returncode, 1, result.stderr)
                self.assertIn(
                    f"candidate API is exposed through {channel}",
                    result.stderr,
                )

    def test_candidate_api_cannot_leak_into_stable_output_artifacts(self) -> None:
        def leak_navigation(repo: Path) -> None:
            readme = repo / "README.md"
            readme.write_text(
                readme.read_text(encoding="utf-8")
                + f"\n[Candidate API]({CANDIDATE_PATH})\n",
                encoding="utf-8",
            )

        def leak_search(repo: Path) -> None:
            (repo / "api" / "search-index.json").write_text(
                json.dumps({"pages": [CANDIDATE_PATH]}) + "\n",
                encoding="utf-8",
            )

        def leak_text(repo: Path, name: str) -> None:
            (repo / "api" / name).write_text(CANDIDATE_PATH + "\n", encoding="utf-8")

        carriers = {
            "stable_navigation": leak_navigation,
            "search": leak_search,
            "sitemap": lambda repo: leak_text(repo, "sitemap.xml"),
            "versioned_bundle": lambda repo: leak_text(repo, "versioned-bundle.txt"),
            "release_bundle": lambda repo: leak_text(repo, "release-bundle.txt"),
        }
        for channel, leak in carriers.items():
            with self.subTest(channel=channel), tempfile.TemporaryDirectory() as tmp:
                repo = copy_repo(Path(tmp))
                materialize_claim(repo, "candidate_api")
                leak(repo)

                result = run_validator(repo)

                self.assertEqual(result.returncode, 1, result.stderr)
                self.assertIn(
                    f"candidate API leaked into {channel}",
                    result.stderr,
                )

    def test_candidate_api_paths_are_portable_and_contained(self) -> None:
        cases = (
            (
                "outside candidate root",
                "api/runtime-reference-candidate.md",
                {"candidate_output_path": "api/runtime-reference-candidate.md"},
            ),
            (
                "parent traversal",
                CANDIDATE_PATH,
                {"candidate_output_path": "api/_candidate/../../README.md"},
            ),
            (
                "absolute path",
                CANDIDATE_PATH,
                {"candidate_output_path": "/tmp/synthetic-candidate.md"},
            ),
        )
        for name, relative_path, metadata in cases:
            with self.subTest(name=name), tempfile.TemporaryDirectory() as tmp:
                repo = copy_repo(Path(tmp))
                materialize_claim(
                    repo,
                    "candidate_api",
                    relative_path=relative_path,
                    metadata=metadata,
                )

                result = run_validator(repo)

                self.assertEqual(result.returncode, 1, result.stderr)
                self.assertIn(
                    "candidate API path must be portable and contained under api/_candidate",
                    result.stderr,
                )

    def test_e2_metadata_cannot_claim_msp_docs_clean_completion(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = copy_repo(Path(tmp))
            materialize_claim(
                repo,
                "architecture",
                relative_path="architecture/premature-successor.md",
                metadata={"milestone_completion": "complete: MSP-DOCS-CLEAN"},
            )

            result = run_validator(repo)

            self.assertEqual(result.returncode, 1, result.stderr)
            self.assertIn(
                "MSP-DOCS-CLEAN cannot be claimed during MSP-DOCS-E2",
                result.stderr,
            )


if __name__ == "__main__":
    unittest.main()
