from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import shutil
import sys


REPO = Path(__file__).resolve().parents[1]
SCRIPTS = REPO / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from validate_repository_policy import check_repository  # noqa: E402
from validate_api_surface_v1 import validate_document, validate_repository  # noqa: E402


POLICY_FIXTURE_PATHS = (
    Path("LICENSE"),
    Path("README.md"),
    Path("requirements-ci.txt"),
    Path(".github/CODEOWNERS"),
    Path(".github/ISSUE_TEMPLATE"),
    Path(".github/workflows/docs-ci.yml"),
    Path("scripts/ci_local.sh"),
    Path("scripts/ci_docs_fast.sh"),
    Path("scripts/validate_repository_policy.py"),
    Path("scripts/machine_publication_policy.py"),
    Path("scripts/platform_cross_seed_snapshot.yaml"),
    Path("scripts/publication_channels.yaml"),
    Path("scripts/render_publication.py"),
    Path("tests/fixtures/issue98/m625-public-redacted-source-positive.json"),
    Path("tests/test_msp_docs_e2_remediation.py"),
    Path("api"),
    Path("architecture"),
    Path("protocols"),
    Path("devices"),
    Path("evidence"),
    Path("re-notes"),
    Path("development"),
)


@dataclass(frozen=True)
class RepositoryCheck:
    returncode: int
    stdout: str
    stderr: str


def materialize_policy_fixture(destination: Path) -> Path:
    """Build only the canonical corpus consumed by repository policy checks."""
    destination.mkdir(parents=True, exist_ok=False)
    for relative in POLICY_FIXTURE_PATHS:
        source = REPO / relative
        sources = (
            [source]
            if source.is_file()
            else [path for path in source.rglob("*") if path.is_file()]
        )
        for path in sources:
            target = destination / path.relative_to(REPO)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)
    return destination


def check_repository_result(root: Path, *, fixture_mode: bool = False) -> RepositoryCheck:
    errors = check_repository(root, fixture_mode=fixture_mode)
    return RepositoryCheck(
        returncode=1 if errors else 0,
        stdout="",
        stderr="\n".join(errors) + ("\n" if errors else ""),
    )


def check_api_repository_result(root: Path) -> RepositoryCheck:
    errors = validate_repository(root)
    return RepositoryCheck(
        returncode=1 if errors else 0,
        stdout="" if errors else "api-surface-v1: valid\n",
        stderr="\n".join(errors) + ("\n" if errors else ""),
    )


def check_api_document_result(path: Path, *, corpus: bool = False) -> RepositoryCheck:
    errors = validate_document(path, corpus=corpus)
    return RepositoryCheck(
        returncode=1 if errors else 0,
        stdout="" if errors else "api-surface-v1 document: valid\n",
        stderr="\n".join(errors) + ("\n" if errors else ""),
    )
