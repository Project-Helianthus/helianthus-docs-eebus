#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ipaddress
import re
import sys
from pathlib import Path

REPO_ID = "Project-Helianthus/helianthus-docs-eebus"
VALID_OWNER = "@d3vi1"

PUBLISHABLE_DOMAINS = {
    "protocols": ("protocols", "CC0-1.0"),
    "devices": ("devices", "CC0-1.0"),
    "evidence": ("evidence", "CC0-1.0"),
    "re-notes": ("re-notes", "CC0-1.0"),
    "architecture": ("architecture", "AGPL-3.0-only"),
    "api": ("api", "AGPL-3.0-only"),
    "development": ("development", "AGPL-3.0-only"),
}

ROOT_MD = {
    "README.md": ("repository", "AGPL-3.0-only"),
}

CONTROL_MD = {
    "AGENTS.md",
}

PRIVATE_NETS = [
    ipaddress.ip_network("10." + "0.0.0/8"),
    ipaddress.ip_network("172.16." + "0.0/12"),
    ipaddress.ip_network("192.168." + "0.0/16"),
    ipaddress.ip_network("100.64." + "0.0/10"),
    ipaddress.ip_network("169.254." + "0.0/16"),
]

PLATFORM_LINK_PATTERN = re.compile(
    r"https://github\.com/Project-Helianthus/helianthus-docs-ebus/"
    r"blob/main/(docs/platform/[A-Za-z0-9._/-]+\.md)"
)
FORBIDDEN_CROSS_SEED_HEADINGS = {
    "requirements",
    "acceptance criteria",
    "versioning policy",
    "approval steps",
}
PEM_BLOCK_PATTERN = re.compile(r"-----BEGIN [A-Z0-9 ][A-Z0-9 -]*-----")
MAC_ADDRESS_PATTERN = re.compile(
    r"(?<![0-9A-Fa-f])(?:[0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}(?![0-9A-Fa-f])"
)
FULL_FINGERPRINT_PATTERN = re.compile(
    r"(?<![0-9A-Fa-f])[0-9A-Fa-f]{40}(?![0-9A-Fa-f])"
)
PRIVATE_ARTIFACT_FIELD_PATTERN = re.compile(
    r"^\s*(?:[-*]\s*)?private artifact (?:location|reference)\s*:",
    re.IGNORECASE | re.MULTILINE,
)
SENSITIVE_FIELD_PATTERN = re.compile(
    r"^\s*(?:[-*]\s*)?"
    r"(token|account (?:id|identifier)|"
    r"full fingerprint|mac address|serial(?: number)?|local identity|"
    r"stable peer identifier|pairing history|household schedule)"
    r"\s*:\s*(\S.*)$",
    re.IGNORECASE | re.MULTILINE,
)
SAFE_REDACTION_MARKERS = ("redacted", "masked", "omitted", "unknown", "not applicable", "n/a")


def _rel(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _front_matter(text: str) -> dict[str, str] | None:
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---\n", 4)
    if end == -1:
        return None
    metadata: dict[str, str] = {}
    for line in text[4:end].splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        key, sep, value = line.partition(":")
        if sep != ":":
            return None
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] == '"':
            value = value[1:-1]
        metadata[key.strip()] = value
    return metadata


def _is_exempt_markdown(path: Path, root: Path) -> bool:
    rel = _rel(path, root)
    return (
        rel in CONTROL_MD
        or rel.startswith(".github/")
        or rel.startswith("tests/")
    )


def _expected_domain_and_license(rel: str) -> tuple[str, str] | None:
    if rel in ROOT_MD:
        return ROOT_MD[rel]
    top = rel.split("/", 1)[0]
    if top in PUBLISHABLE_DOMAINS:
        domain, license_id = PUBLISHABLE_DOMAINS[top]
        return domain, license_id
    return None


def check_repository(root: Path) -> list[str]:
    errors: list[str] = []
    root = root.resolve()

    symlinks: set[Path] = set()
    for path in sorted(root.rglob("*")):
        if ".git" in path.parts or ".pytest_cache" in path.parts:
            continue
        if path.is_symlink():
            symlinks.add(path)
            errors.append(f"{_rel(path, root)}: symlinks are forbidden")

    license_file = root / "LICENSE"
    if not license_file.exists():
        errors.append("LICENSE: missing repository license policy")
    elif license_file not in symlinks:
        text = _read(license_file)
        for required in [
            "CC0-1.0",
            "AGPL-3.0-only",
            "https://creativecommons.org/publicdomain/zero/1.0/legalcode",
            "https://www.gnu.org/licenses/agpl-3.0.txt",
            "protocols/",
            "devices/",
            "evidence/",
            "re-notes/",
        ]:
            if required not in text:
                errors.append(f"LICENSE: missing required licensing lane marker {required!r}")

    codeowners = root / ".github" / "CODEOWNERS"
    if not codeowners.exists():
        errors.append(".github/CODEOWNERS: missing")
    elif codeowners not in symlinks:
        text = _read(codeowners)
        active_rules = []
        for line in text.splitlines():
            rule = line.strip()
            if not rule or rule.startswith("#"):
                continue
            active_rules.append(rule.split())
        if not any(
            fields[0] == "*" and VALID_OWNER in fields[1:]
            for fields in active_rules
            if fields
        ):
            errors.append(f".github/CODEOWNERS: must assign default ownership to {VALID_OWNER}")

    issue_template = root / ".github" / "ISSUE_TEMPLATE" / "docs_task.yml"
    if not issue_template.exists():
        errors.append(".github/ISSUE_TEMPLATE/docs_task.yml: missing standard documentation issue template")
    elif issue_template not in symlinks:
        text = _read(issue_template)
        for required in [
            "What",
            "Why",
            "Acceptance Criteria",
            "Ownership domain",
            "Provenance",
            "Smoke test required",
            "Licensing acknowledgement",
        ]:
            if required not in text:
                errors.append(f".github/ISSUE_TEMPLATE/docs_task.yml: missing {required!r}")

    workflow = root / ".github" / "workflows" / "docs-ci.yml"
    if not workflow.exists():
        errors.append(".github/workflows/docs-ci.yml: missing GitHub Actions docs CI")
    elif workflow not in symlinks and "./scripts/ci_local.sh" not in _read(workflow):
        errors.append(".github/workflows/docs-ci.yml: must invoke ./scripts/ci_local.sh")

    readme_path = root / "README.md"
    contributing_path = root / "development" / "contributing.md"
    readme = _read(readme_path) if readme_path.exists() and readme_path not in symlinks else ""
    contributing = (
        _read(contributing_path)
        if contributing_path.exists() and contributing_path not in symlinks
        else ""
    )
    combined_policy = readme + "\n" + contributing
    required_policy_terms = [
        "protocols/` owns eeBUS/SHIP/SPINE protocol behavior",
        "architecture/` owns Helianthus eeBUS runtime",
        "api/` owns eeBUS-specific Go API schema",
        "devices/`, `evidence/`, and `re-notes/` remain native owners",
        "helianthus-docs-ebus/docs/platform/` owns only language-neutral",
        "Code repositories are external-only",
        "Cross-seeding",
        "Provenance Classes",
        "gateway import remains blocked",
        "noncanonical migration/adjudication inputs",
        "MSP-DOCS-E2",
        "MSP-DOCS-CLEAN",
    ]
    for required in required_policy_terms:
        if required not in combined_policy:
            errors.append(f"README/development policy: missing required declaration {required!r}")

    seen_sources: dict[str, str] = {}
    for path in sorted(root.rglob("*.md")):
        if ".git" in path.parts:
            continue
        if ".pytest_cache" in path.parts:
            continue
        if path in symlinks:
            continue
        rel = _rel(path, root)
        if _is_exempt_markdown(path, root):
            continue
        expected = _expected_domain_and_license(rel)
        if expected is None:
            errors.append(f"{rel}: publishable markdown path has no registered owner domain")
            continue
        expected_domain, expected_license = expected
        page_text = _read(path)
        metadata = _front_matter(page_text)
        if metadata is None:
            errors.append(f"{rel}: missing YAML front matter")
            continue
        canonical_source = metadata.get("canonical_source")
        expected_source = f"{REPO_ID}:{rel}"
        if canonical_source != expected_source:
            errors.append(f"{rel}: canonical_source must be {expected_source!r}")
        elif canonical_source in seen_sources:
            errors.append(f"{rel}: duplicate canonical_source also used by {seen_sources[canonical_source]}")
        else:
            seen_sources[canonical_source] = rel
        if metadata.get("owner_domain") != expected_domain:
            errors.append(f"{rel}: owner_domain must be {expected_domain!r}")
        if metadata.get("license") != expected_license:
            errors.append(f"{rel}: license must be {expected_license!r}")

        targets = {
            f"Project-Helianthus/helianthus-docs-ebus:{target}"
            for target in PLATFORM_LINK_PATTERN.findall(page_text)
        }
        declared_target = metadata.get("cross_seed_target")
        declared_mode = metadata.get("cross_seed_mode")
        if targets:
            if len(targets) != 1:
                errors.append(f"{rel}: a page may cross-seed exactly one platform target")
            expected_target = next(iter(targets)) if len(targets) == 1 else None
            if declared_target != expected_target:
                errors.append(
                    f"{rel}: cross_seed_target must match the linked platform page {expected_target!r}"
                )
            if declared_mode != "summary-only":
                errors.append(f"{rel}: cross_seed_mode must be 'summary-only'")
            headings = {
                re.sub(r"[^a-z0-9]+", " ", match.group(1).lower()).strip()
                for match in re.finditer(r"^##+\s+(.+?)\s*$", page_text, re.MULTILINE)
            }
            duplicated = sorted(
                forbidden
                for forbidden in FORBIDDEN_CROSS_SEED_HEADINGS
                if any(forbidden in heading for heading in headings)
            )
            if duplicated:
                errors.append(
                    f"{rel}: summary-only cross-seed contains platform-owned headings {duplicated}"
                )
        elif declared_target is not None or declared_mode is not None:
            errors.append(f"{rel}: cross-seed metadata requires a canonical platform link")

        if PEM_BLOCK_PATTERN.search(page_text):
            errors.append(f"{rel}: PEM block marker found in publishable content")
        if MAC_ADDRESS_PATTERN.search(page_text):
            errors.append(f"{rel}: MAC address found in publishable content")
        if FULL_FINGERPRINT_PATTERN.search(page_text):
            errors.append(f"{rel}: full fingerprint or raw SKI found in publishable content")
        for match in PRIVATE_ARTIFACT_FIELD_PATTERN.finditer(page_text):
            line = page_text.count("\n", 0, match.start()) + 1
            errors.append(f"{rel}:{line}: private artifact location/reference field is forbidden")
        for match in SENSITIVE_FIELD_PATTERN.finditer(page_text):
            field = match.group(1).lower()
            value = match.group(2).lower()
            if not any(marker in value for marker in SAFE_REDACTION_MARKERS):
                line = page_text.count("\n", 0, match.start()) + 1
                errors.append(f"{rel}:{line}: populated sensitive field {field!r}")

    for directory in ["protocols", "architecture", "api", "devices", "evidence", "re-notes"]:
        dir_path = root / directory
        if dir_path.exists() and not dir_path.is_dir():
            errors.append(f"{directory}: path-domain owner must be a directory")

    ipv4_pattern = re.compile(r"\b(?:(?:\d{1,3})\.){3}(?:\d{1,3})\b")
    scan_suffixes = {".md", ".yml", ".yaml", ".py", ".sh", ""}
    for path in sorted(
        p for p in root.rglob("*") if p.is_file() and not p.is_symlink()
    ):
        if ".git" in path.parts or ".pytest_cache" in path.parts:
            continue
        if path.suffix not in scan_suffixes and path.name not in {"LICENSE", "Makefile"}:
            continue
        text = _read(path)
        rel = _rel(path, root)
        for match in ipv4_pattern.finditer(text):
            try:
                addr = ipaddress.ip_address(match.group(0))
            except ValueError:
                continue
            if any(addr in net for net in PRIVATE_NETS):
                line = text.count("\n", 0, match.start()) + 1
                errors.append(f"{rel}:{line}: private IPv4 address found")

    restricted_policy = (root / "development" / "contributing.md")
    if restricted_policy.exists():
        text = _read(restricted_policy)
        if "`vendor_restricted` | Quarantined" not in text:
            errors.append("development/contributing.md: missing vendor_restricted quarantine marker")
        if "Restricted material must not appear in public repositories" not in text:
            errors.append("development/contributing.md: missing restricted-source quarantine rule")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()

    errors = check_repository(args.repo)
    for error in errors:
        print(error, file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
