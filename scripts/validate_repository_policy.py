#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import ipaddress
import re
import sys
import unicodedata
from pathlib import Path
from typing import Any

import yaml

from machine_publication_policy import (
    COMPLETE,
    IPV4_CANDIDATE_PATTERN,
    MALFORMED_SENTINEL,
    classify_ipv4,
    decode_machine_json,
    machine_publication_diagnostics,
)

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
MARKDOWN_SUFFIXES = {".md", ".markdown", ".mdown", ".mkd", ".mkdn"}
MARKDOWN_ONLY_DOMAINS = {
    "protocols",
    "devices",
    "architecture",
    "development",
    "re-notes",
}
API_MACHINE_ARTIFACTS = {
    "api/schema/helianthus.eebus.api-surface.v1.schema.json",
    "api/fixtures/v1/positive/kinds-types-signatures.json",
    "api/fixtures/v1/positive/packages-and-symbols.json",
    "api/fixtures/v1/negative/duplicate-identity.json",
    "api/fixtures/v1/negative/duplicate-json-key.json",
    "api/fixtures/v1/negative/implementation-dependency-type.json",
    "api/fixtures/v1/negative/internal-package.json",
    "api/fixtures/v1/negative/invalid-ordering.json",
    "api/fixtures/v1/negative/malformed.json",
    "api/fixtures/v1/negative/non-nfc.json",
    "api/fixtures/v1/negative/unexported-declaration.json",
    "api/fixtures/v1/negative/unexported-receiver.json",
    "api/fixtures/v1/negative/unknown-field.json",
}
MALFORMED_API_FIXTURE = "api/fixtures/v1/negative/malformed.json"

ROOT_MD = {
    "README.md": ("repository", "AGPL-3.0-only"),
}

REQUIRED_DOMAIN_PAGES = {
    "protocols": "protocols/ship-spine-overview.md",
    "architecture": "architecture/README.md",
    "api": "api/README.md",
    "devices": "devices/vr940f.md",
    "evidence": "evidence/README.md",
    "re-notes": "re-notes/template.md",
}

SCAFFOLD_PAGES = {
    "README.md": "ownership-policy",
    "protocols/ship-spine-overview.md": "ownership-landing",
    "architecture/README.md": "ownership-landing",
    "api/README.md": "ownership-landing",
    "api/api-surface-v1.md": "api-contract",
    "devices/vr940f.md": "planned-target",
    "evidence/README.md": "evidence-policy",
    "evidence/evidence-template.md": "template",
    "re-notes/template.md": "template",
    "development/contributing.md": "contribution-policy",
}

SCAFFOLD_ARTIFACT_SHA256 = {
    "README.md": "6e7e2e079fca9e559f50555b29a6e7f44c4e7305316e5f4bb54498943d3b9a8d",
    "protocols/ship-spine-overview.md": "866bb693935bb64e8ab34e2a2f9766e0662e6738886416617e8f59a075bc6073",
    "architecture/README.md": "d21fccf5a5ee9c7d3ed43bc1f895a307fc75ea2456d0851f648607bf7fd34da8",
    "api/README.md": "36bb41e1a6b843a05cc6b5641bdfb010285607ad10016fa39ffe2424c123eb4a",
    "api/api-surface-v1.md": "bd2ab30908dca4139ab8fd3c0a1f99834b7d89808823dc25bbe8faeef8b859d4",
    "devices/vr940f.md": "96c6d81d9e758cbd8ed6835f197dbf92b54cbf8dc5eb6afeac0524c8bcabde15",
    "evidence/README.md": "4afae6e8ab7848ded9068f43523794eeccf8f325f91659557a453646a00423ff",
    "evidence/evidence-template.md": "02910e849eab14a43251f4d28f4cb1e115c0feb6f78a32b2b600c85830c150e5",
    "re-notes/template.md": "eaedfc96d49a573455f43df8f1542e0fd8724ef3770dcb9d0aac485ef23f8f32",
    "development/contributing.md": "f52c046edb8bafeca43cdb1e9159e49355688ce7b114339bfe34cf02a1038586",
}

EVIDENCE_SOURCE_CLASSES = {
    "observed_runtime",
    "derived_inference",
    "vendor_public",
    "app_observation",
}
HYPOTHESIS_STATUSES = {"draft", "publishable", "blocked", "withdrawn"}
EVIDENCE_ID_PATTERN = re.compile(r"EV-\d{8}-\d{3}")
CI_LOCAL_SHA256 = "ee5413bcb10b811225ff6f5c4bfa998b48f2a67e1282f3e5e74d78f8b87dce7a"
LICENSE_SHA256 = "aac2f93638f50b4347d37aeb656cab31f447e0c0bc89f53ee144a81907a943ea"

LICENSE_ACK_LABEL = (
    "I have read the repository license policy and I accept the Helianthus "
    "licensing model for any contribution or reusable material I submit here."
)

CONTROL_MD = {
    "AGENTS.md",
}

PLATFORM_LINK_PATTERN = re.compile(
    r"https://github\.com/Project-Helianthus/helianthus-docs-ebus/"
    r"blob/main/(docs/platform/[A-Za-z0-9._/-]+\.md)"
    r"(?=$|[\s<>()\[\]{},;:!?'\"#]|\.(?=$|[\s)\]}>]))"
)
FORBIDDEN_CROSS_SEED_HEADINGS = {
    "requirements",
    "acceptance criteria",
    "versioning policy",
    "approval steps",
}
PEM_BLOCK_PATTERN = re.compile(r"-----BEGIN [A-Z0-9 ][A-Z0-9 -]*-----")
MAC_ADDRESS_PATTERN = re.compile(
    r"(?<![0-9A-Fa-f])(?:"
    r"(?:[0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}|"
    r"(?:[0-9A-Fa-f]{4}\.){2}[0-9A-Fa-f]{4}"
    r")(?![0-9A-Fa-f])"
)
FULL_FINGERPRINT_PATTERN = re.compile(
    r"(?<![0-9A-Fa-f])[0-9A-Fa-f]{40}(?![0-9A-Fa-f])"
)
PRIVATE_ARTIFACT_FIELD_PATTERN = re.compile(
    r"^\s*(?:[-*]\s*)?private artifact "
    r"(?:location|reference|filename|hash|identifier)\s*:",
    re.IGNORECASE | re.MULTILINE,
)
PRIVATE_ARTIFACT_RETAINED_PATTERN = re.compile(
    r"^\s*(?:[-*]\s*)?private artifact retained\s*:\s*(\S.*)$",
    re.IGNORECASE | re.MULTILINE,
)
EEBUS_ID_LABEL_PATTERN = (
    r"(?:(?:ski|ship)(?:[\s_-]*(?:id|identifier))?)"
)
SENSITIVE_FIELD_PATTERN = re.compile(
    r"^\s*(?:[-*]\s*)?"
    r"(token|password|passphrase|credential|secret|api[\s_-]*key|"
    r"client[\s_-]*secret|account (?:id|identifier)|"
    r"(?:full )?fingerprint|mac address|serial(?: number)?|local identity|"
    r"stable peer identifier|pairing history|household schedule|"
    rf"(?:raw\s+)?{EEBUS_ID_LABEL_PATTERN})"
    r"\s*:\s*(\S.*)$",
    re.IGNORECASE | re.MULTILINE,
)
RAW_EEBUS_ID_PATTERN = re.compile(
    rf"`?\b(?:raw\s+)?{EEBUS_ID_LABEL_PATTERN}\b`?"
    r"\s*(?::|=|\bis\b)?\s*`?([A-Za-z0-9][A-Za-z0-9._:-]{7,})`?",
    re.IGNORECASE,
)
SAFE_REDACTED_VALUE_PATTERN = re.compile(
    r"^\s*[<\[(]?(?:redacted|masked|omitted|unknown|not applicable|n/a)[>\])]?[.!]?\s*$",
    re.IGNORECASE,
)
SAFE_RETAINED_VALUE_PATTERN = re.compile(
    r"^\s*(?:yes|no|<yes-or-no>)\s*$",
    re.IGNORECASE,
)
PRIVATE_PATH_PATTERN = re.compile(
    r"(?:/Users/[^/\s]+/|/home/[^/\s]+/|/tmp/[^\s]+|/var/folders/[^\s]+|"
    r"[A-Za-z]:\\Users\\[^\\\s]+\\)"
)
IPV6_CANDIDATE_PATTERN = re.compile(
    r"(?<![0-9A-Fa-f:])(?:[0-9A-Fa-f]{0,4}:){2,7}[0-9A-Fa-f]{0,4}"
    r"(?:%[A-Za-z0-9_.-]+)?(?![0-9A-Fa-f:])"
)
PREMATURE_COMPLETION_PATTERN = re.compile(
    r"(?:MSP-DOCS-[A-Z0-9-]+\b[^\n]{0,40}\b"
    r"(?:complete|completed|merged|done|ready|available|shipped|landed)\b|"
    r"(?:absence gate|helianthus-eebusreg/docs)\s+(?:is|was|has been)\s+"
    r"(?:installed|absent|deleted|removed)|"
    r"helianthus-eebusreg[^\n]{0,80}\b(?:has|contains|tracks|keeps|ships)\s+"
    r"no\s+(?:tracked\s+)?(?:docs/?|documentation)(?:\s+directory)?|"
    r"helianthus-eebusreg[^\n]{0,80}\b(?:docs/?|documentation)[^\n]{0,40}"
    r"\b(?:is|are|was|were|has been)\s+(?:absent|deleted|removed))",
    re.IGNORECASE,
)
PREMATURE_CONSUMER_PATTERN = re.compile(
    r"(?:GraphQL exposure|Home Assistant entit(?:y|ies)(?: rollout)?|"
    r"HA entit(?:y|ies)(?: rollout)?|HA consumer rollout|"
    r"Portal consumer workflow|Portal rollout|command routing|gateway import)"
    r"[^\n]{0,120}\b(?:(?:is|are|was|were|becomes?)|"
    r"(?:has|have)(?:\s+been)?)\s+"
    r"(?:available|active|enabled|supported|shipped|ready|complete|completed|done|"
    r"landed|unblocked|allowed|permitted|open)"
    r"(?:\s+now)?\b",
    re.IGNORECASE,
)
RESTRICTED_SOURCE_PATTERN = re.compile(
    r"\bvendor[_ -]restricted\b|"
    r"\brestricted[ -]+source\b|"
    r"\brestricted\s+vendor\s+"
    r"(?:documents?|docs?|sources?|materials?|contents?|texts?)\b|"
    r"\bparaphras(?:e|ed|ing)\b[^\n]{0,80}\brestricted\b|"
    r"\bsource\s+class\s*:\s*restricted\b",
    re.IGNORECASE,
)
ALLOWED_RESTRICTED_POLICY_LINE = (
    "| `vendor_restricted` | Quarantined; never public text, issue text, PR text, "
    "review text, or ADR rationale. |"
)


class UniqueKeySafeLoader(yaml.SafeLoader):
    pass


def _construct_unique_mapping(
    loader: UniqueKeySafeLoader,
    node: yaml.MappingNode,
    deep: bool = False,
) -> dict[object, object]:
    loader.flatten_mapping(node)
    mapping: dict[object, object] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        try:
            duplicate = key in mapping
        except TypeError as error:
            raise yaml.constructor.ConstructorError(
                "while constructing a mapping",
                node.start_mark,
                "found an unhashable key",
                key_node.start_mark,
            ) from error
        if duplicate:
            raise yaml.constructor.ConstructorError(
                "while constructing a mapping",
                node.start_mark,
                f"found duplicate key {key!r}",
                key_node.start_mark,
            )
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


UniqueKeySafeLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
    _construct_unique_mapping,
)


def _rel(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def _read(path: Path) -> str:
    return path.read_bytes().decode("utf-8")


def _front_matter(text: str) -> tuple[dict[str, str] | None, str | None]:
    if not text.startswith("---\n"):
        return None, "missing YAML front matter"
    end = text.find("\n---\n", 4)
    if end == -1:
        return None, "unterminated YAML front matter"
    try:
        parsed = yaml.load(text[4:end], Loader=UniqueKeySafeLoader)
    except yaml.YAMLError as error:
        return None, f"invalid YAML front matter: {error}"
    if not isinstance(parsed, dict):
        return None, "YAML front matter must be a mapping"
    if not all(isinstance(key, str) and isinstance(value, str) for key, value in parsed.items()):
        return None, "YAML front matter keys and values must be strings"
    return parsed, None


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


def _privacy_errors(text: str, rel: str, *, category_only: bool = False) -> list[str]:
    errors: list[str] = []

    def add(category: str, line: int | None = None) -> None:
        location = rel if category_only or line is None else f"{rel}:{line}"
        errors.append(f"{location}: {category}")

    if PEM_BLOCK_PATTERN.search(text):
        add("PEM block marker found in publishable content")
    if MAC_ADDRESS_PATTERN.search(text):
        add("MAC address found in publishable content")
    if FULL_FINGERPRINT_PATTERN.search(text):
        add("full fingerprint or raw SKI found in publishable content")
    if PRIVATE_PATH_PATTERN.search(text):
        add("private or identifying filesystem path found")
    for match in PRIVATE_ARTIFACT_FIELD_PATTERN.finditer(text):
        line = text.count("\n", 0, match.start()) + 1
        add("private artifact location/reference field is forbidden", line)
    for match in PRIVATE_ARTIFACT_RETAINED_PATTERN.finditer(text):
        value = match.group(1)
        if SAFE_RETAINED_VALUE_PATTERN.fullmatch(value) is None:
            line = text.count("\n", 0, match.start()) + 1
            add("private artifact retained value must be yes or no", line)
    for match in SENSITIVE_FIELD_PATTERN.finditer(text):
        value = match.group(2)
        if SAFE_REDACTED_VALUE_PATTERN.fullmatch(value) is None:
            line = text.count("\n", 0, match.start()) + 1
            category = "populated sensitive field"
            if not category_only:
                category += f" {match.group(1).lower()!r}"
            add(category, line)
    for match in RAW_EEBUS_ID_PATTERN.finditer(text):
        value = match.group(1)
        if SAFE_REDACTED_VALUE_PATTERN.fullmatch(value) is None:
            line = text.count("\n", 0, match.start()) + 1
            add("populated raw SKI or SHIP ID", line)
    for match in IPV4_CANDIDATE_PATTERN.finditer(text):
        if classify_ipv4(match.group(0)) == "private network":
            line = text.count("\n", 0, match.start()) + 1
            add("private IPv4 address found", line)
    for match in IPV6_CANDIDATE_PATTERN.finditer(text):
        candidate = match.group(0)
        address = candidate.split("%", 1)[0]
        try:
            parsed = ipaddress.ip_address(address)
        except ValueError:
            continue
        if isinstance(parsed, ipaddress.IPv6Address):
            line = text.count("\n", 0, match.start()) + 1
            add("IPv6 address found in publishable content", line)
    return errors


def _restricted_source_errors(
    text: str,
    rel: str,
    *,
    category_only: bool = False,
) -> list[str]:
    if rel in SCAFFOLD_PAGES:
        return []
    errors: list[str] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        if RESTRICTED_SOURCE_PATTERN.search(line) is None:
            continue
        location = rel if category_only else f"{rel}:{line_number}"
        errors.append(f"{location}: restricted-source contamination marker found")
    return errors


def _has_forbidden_control(text: str) -> bool:
    return any(
        unicodedata.category(char) == "Cc" and char != "\n"
        for char in text
    )


def _machine_artifact_errors(text: str, rel: str) -> list[str]:
    allow_sentinel = rel == MALFORMED_API_FIXTURE
    result = decode_machine_json(
        text.encode("utf-8"),
        allow_malformed_sentinel=allow_sentinel,
    )
    expected_status = MALFORMED_SENTINEL if allow_sentinel else COMPLETE
    errors = [
        f"{rel}: {category}"
        for category in sorted(machine_publication_diagnostics(result))
    ]
    if result.status != expected_status:
        errors.append(f"{rel}: machine publication boundary")
    return errors


def _provenance_errors(
    root: Path,
    rel: str,
    text: str,
    metadata: dict[str, str],
) -> list[str]:
    errors: list[str] = []
    expected_scaffold_status = SCAFFOLD_PAGES.get(rel)
    claim_status = metadata.get("claim_status")

    if expected_scaffold_status is not None:
        if claim_status != "no-protocol-claims":
            errors.append(f"{rel}: scaffold claim_status must be 'no-protocol-claims'")
        if metadata.get("publication_status") != expected_scaffold_status:
            errors.append(
                f"{rel}: publication_status must be {expected_scaffold_status!r}"
            )
        artifact_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()
        if artifact_hash != SCAFFOLD_ARTIFACT_SHA256[rel]:
            errors.append(f"{rel}: scaffold artifact differs from the reviewed no-claim content")
        return errors

    if claim_status != "evidence-backed":
        errors.append(f"{rel}: non-scaffold page claim_status must be 'evidence-backed'")
        return errors

    if metadata.get("source_class") not in EVIDENCE_SOURCE_CLASSES:
        errors.append(f"{rel}: evidence-backed source_class is missing or not publishable")
    if metadata.get("hypothesis_status") not in HYPOTHESIS_STATUSES:
        errors.append(f"{rel}: evidence-backed hypothesis_status is invalid")

    falsifier = metadata.get("falsifier", "").strip()
    if not falsifier or falsifier.lower() in {"none", "n/a", "unknown", "tbd"}:
        errors.append(f"{rel}: evidence-backed falsifier must be explicit")

    evidence_ids = [
        value.strip()
        for value in metadata.get("evidence_ids", "").split(",")
        if value.strip()
    ]
    if not evidence_ids or any(
        EVIDENCE_ID_PATTERN.fullmatch(value) is None for value in evidence_ids
    ):
        errors.append(f"{rel}: evidence_ids must contain canonical EV-YYYYMMDD-NNN ids")
    else:
        for evidence_id in evidence_ids:
            evidence_path = root / "evidence" / f"{evidence_id}.md"
            if not evidence_path.is_file() or evidence_path.is_symlink():
                errors.append(f"{rel}: publishable evidence page {evidence_path.name!r} is missing")

    return errors


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

    ci_local = root / "scripts" / "ci_local.sh"
    if not ci_local.is_file() or ci_local.is_symlink():
        errors.append("scripts/ci_local.sh: missing regular CI entrypoint")
    elif hashlib.sha256(ci_local.read_bytes()).hexdigest() != CI_LOCAL_SHA256:
        errors.append("scripts/ci_local.sh: content differs from the reviewed CI entrypoint")

    license_file = root / "LICENSE"
    if not license_file.exists():
        errors.append("LICENSE: missing repository license policy")
    elif license_file not in symlinks:
        text = _read(license_file)
        if hashlib.sha256(text.encode("utf-8")).hexdigest() != LICENSE_SHA256:
            errors.append("LICENSE: content differs from the reviewed license policy")
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
            rule = line.split("#", 1)[0].strip()
            if not rule or rule.startswith("#"):
                continue
            active_rules.append(rule.split())
        broad_rules = [
            fields
            for fields in active_rules
            if fields and fields[0] in {"*", "/**", "/"}
        ]
        if not broad_rules or VALID_OWNER not in broad_rules[-1][1:]:
            errors.append(f".github/CODEOWNERS: must assign default ownership to {VALID_OWNER}")
        for fields in active_rules:
            if len(fields) < 2 or VALID_OWNER not in fields[1:]:
                errors.append(
                    f".github/CODEOWNERS: rule {fields[0]!r} must retain {VALID_OWNER}"
                )

    issue_config = root / ".github" / "ISSUE_TEMPLATE" / "config.yml"
    if not issue_config.exists():
        errors.append(".github/ISSUE_TEMPLATE/config.yml: missing")
    elif issue_config not in symlinks:
        try:
            issue_config_data = yaml.load(_read(issue_config), Loader=UniqueKeySafeLoader)
        except yaml.YAMLError as error:
            errors.append(f".github/ISSUE_TEMPLATE/config.yml: invalid YAML: {error}")
            issue_config_data = None
        if not isinstance(issue_config_data, dict):
            errors.append(".github/ISSUE_TEMPLATE/config.yml: root must be a mapping")
        elif issue_config_data.get("blank_issues_enabled") is not False:
            errors.append(".github/ISSUE_TEMPLATE/config.yml: blank issues must be disabled")

    issue_template = root / ".github" / "ISSUE_TEMPLATE" / "docs_task.yml"
    if not issue_template.exists():
        errors.append(".github/ISSUE_TEMPLATE/docs_task.yml: missing standard documentation issue template")
    elif issue_template not in symlinks:
        try:
            form = yaml.load(_read(issue_template), Loader=UniqueKeySafeLoader)
        except yaml.YAMLError as error:
            errors.append(f".github/ISSUE_TEMPLATE/docs_task.yml: invalid YAML: {error}")
            form = None
        body = form.get("body") if isinstance(form, dict) else None
        fields = {
            item.get("id"): item
            for item in body or []
            if isinstance(item, dict) and isinstance(item.get("id"), str)
        }
        required_fields = {
            "what": "What",
            "why": "Why",
            "ownership_domain": "Ownership domain",
            "acceptance": "Acceptance Criteria",
            "provenance": "Provenance",
            "dependencies": "Dependencies",
            "smoke_test": "Smoke test required",
            "licensing_ack": "Licensing acknowledgement",
        }
        expected_types = {
            "what": "textarea",
            "why": "textarea",
            "ownership_domain": "dropdown",
            "acceptance": "textarea",
            "provenance": "textarea",
            "dependencies": "input",
            "smoke_test": "dropdown",
            "licensing_ack": "checkboxes",
        }
        for field_id, label in required_fields.items():
            item = fields.get(field_id)
            attributes = item.get("attributes") if isinstance(item, dict) else None
            if not isinstance(attributes, dict) or attributes.get("label") != label:
                errors.append(
                    f".github/ISSUE_TEMPLATE/docs_task.yml: missing field {field_id!r} with label {label!r}"
                )
            if not isinstance(item, dict) or item.get("type") != expected_types[field_id]:
                errors.append(
                    f".github/ISSUE_TEMPLATE/docs_task.yml: field {field_id!r} must use type {expected_types[field_id]!r}"
                )
        expected_dropdown_options = {
            "ownership_domain": [
                "protocols",
                "architecture",
                "api",
                "devices",
                "evidence",
                "re-notes",
                "development",
                "repository-control",
                "cross-seed-candidate",
            ],
            "smoke_test": ["NO", "YES"],
        }
        for field_id, expected_options in expected_dropdown_options.items():
            item = fields.get(field_id)
            attributes = item.get("attributes") if isinstance(item, dict) else None
            options = attributes.get("options") if isinstance(attributes, dict) else None
            if options != expected_options:
                errors.append(
                    f".github/ISSUE_TEMPLATE/docs_task.yml: field {field_id!r} options must be {expected_options!r}"
                )
        for field_id in {
            "what",
            "why",
            "ownership_domain",
            "acceptance",
            "provenance",
            "smoke_test",
        }:
            item = fields.get(field_id)
            validations = item.get("validations") if isinstance(item, dict) else None
            if not isinstance(validations, dict) or validations.get("required") is not True:
                errors.append(
                    f".github/ISSUE_TEMPLATE/docs_task.yml: field {field_id!r} must be required"
                )
        licensing_item = fields.get("licensing_ack")
        licensing_attributes = (
            licensing_item.get("attributes") if isinstance(licensing_item, dict) else None
        )
        licensing_options = (
            licensing_attributes.get("options")
            if isinstance(licensing_attributes, dict)
            else None
        )
        if not isinstance(licensing_options, list) or not any(
            isinstance(option, dict) and option.get("required") is True
            for option in licensing_options
        ):
            errors.append(
                ".github/ISSUE_TEMPLATE/docs_task.yml: licensing acknowledgement must be required"
            )
        if licensing_options != [{"label": LICENSE_ACK_LABEL, "required": True}]:
            errors.append(
                ".github/ISSUE_TEMPLATE/docs_task.yml: licensing acknowledgement text must match policy"
            )

    workflow = root / ".github" / "workflows" / "docs-ci.yml"
    if not workflow.exists():
        errors.append(".github/workflows/docs-ci.yml: missing GitHub Actions docs CI")
    elif workflow not in symlinks:
        try:
            workflow_data = yaml.load(_read(workflow), Loader=UniqueKeySafeLoader)
        except yaml.YAMLError as error:
            errors.append(f".github/workflows/docs-ci.yml: invalid YAML: {error}")
            workflow_data = None
        triggers = workflow_data.get("on") if isinstance(workflow_data, dict) else None
        if not isinstance(triggers, dict) or "pull_request" not in triggers:
            errors.append(".github/workflows/docs-ci.yml: pull_request trigger is required")
        else:
            if triggers.get("pull_request") not in (None, {}):
                errors.append(
                    ".github/workflows/docs-ci.yml: pull_request trigger must be unconditional"
                )
            for trigger_name in ("pull_request", "push"):
                trigger = triggers.get(trigger_name)
                if isinstance(trigger, dict) and any(
                    key in trigger for key in ("paths", "paths-ignore")
                ):
                    errors.append(".github/workflows/docs-ci.yml: path filters are forbidden")
            push_trigger = triggers.get("push")
            if not isinstance(push_trigger, dict) or push_trigger.get("branches") != [
                "main",
                "issue/**",
            ]:
                errors.append(
                    ".github/workflows/docs-ci.yml: push branches must be main and issue/**"
                )
        jobs = workflow_data.get("jobs") if isinstance(workflow_data, dict) else None
        run_commands = []
        docs_job = jobs.get("docs-checks") if isinstance(jobs, dict) else None
        if not isinstance(docs_job, dict):
            errors.append(".github/workflows/docs-ci.yml: docs-checks job is required")
        else:
            if any(key in docs_job for key in ("if", "continue-on-error", "needs")):
                errors.append(
                    ".github/workflows/docs-ci.yml: docs-checks job must be unconditional"
                )
            if docs_job.get("runs-on") != "ubuntu-latest":
                errors.append(
                    ".github/workflows/docs-ci.yml: docs-checks must run on ubuntu-latest"
                )
            steps = docs_job.get("steps")
            if isinstance(steps, list):
                for step in steps:
                    if isinstance(step, dict) and isinstance(step.get("run"), str):
                        run_commands.append(step["run"].strip())
                        if step["run"].strip() in {
                            "./scripts/ci_local.sh",
                            "python -m pip install -r requirements-ci.txt",
                        } and any(key in step for key in ("if", "continue-on-error", "shell")):
                            errors.append(
                                ".github/workflows/docs-ci.yml: validator steps must be unconditional"
                            )
        if "./scripts/ci_local.sh" not in run_commands:
            errors.append(".github/workflows/docs-ci.yml: must invoke ./scripts/ci_local.sh exactly")
        if "python -m pip install -r requirements-ci.txt" not in run_commands:
            errors.append(
                ".github/workflows/docs-ci.yml: must install pinned validator dependencies"
            )

    requirements = root / "requirements-ci.txt"
    if requirements in symlinks or not requirements.exists():
        errors.append("requirements-ci.txt: missing pinned validator dependencies")
    elif _read(requirements).splitlines() != ["PyYAML==6.0.3"]:
        errors.append("requirements-ci.txt: expected exact PyYAML==6.0.3 pin")

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
    for path in sorted(
        path
        for path in root.rglob("*")
        if path.is_file() and path.suffix.lower() in MARKDOWN_SUFFIXES
    ):
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
        if _has_forbidden_control(page_text):
            errors.append(f"{rel}: control bytes are forbidden in publishable artifacts")
        metadata, front_matter_error = _front_matter(page_text)
        if metadata is None:
            errors.append(f"{rel}: {front_matter_error}")
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
        errors.extend(_provenance_errors(root, rel, page_text, metadata))

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
            atx_headings = {
                match.group(1)
                for match in re.finditer(r"^#+\s+(.+?)\s*$", page_text, re.MULTILINE)
            }
            setext_headings = {
                match.group(1)
                for match in re.finditer(
                    r"^([^\n]+)\n(?:=+|-+)\s*$", page_text, re.MULTILINE
                )
            }
            headings = {
                re.sub(r"[^a-z0-9]+", " ", heading.lower()).strip()
                for heading in atx_headings | setext_headings
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

        if PREMATURE_COMPLETION_PATTERN.search(page_text):
            errors.append(f"{rel}: premature docs milestone or code-doc absence claim")
        if PREMATURE_CONSUMER_PATTERN.search(page_text):
            errors.append(f"{rel}: premature gateway or consumer availability claim")
        errors.extend(_restricted_source_errors(page_text, rel))

        if rel in ROOT_MD:
            errors.extend(_privacy_errors(page_text, rel))

    for top in PUBLISHABLE_DOMAINS:
        domain_root = root / top
        if not domain_root.exists() or domain_root in symlinks:
            continue
        for path in sorted(p for p in domain_root.rglob("*") if p.is_file()):
            if path.is_symlink():
                continue
            rel = _rel(path, root)
            if path.suffix.lower() not in MARKDOWN_SUFFIXES:
                if top == "api":
                    if rel not in API_MACHINE_ARTIFACTS:
                        errors.append(f"{rel}: path is not in the API machine artifact allowlist")
                        continue
                elif top in MARKDOWN_ONLY_DOMAINS:
                    errors.append(f"{rel}: substantive documentation must use a Markdown extension")
                    continue
            try:
                text = _read(path)
            except UnicodeDecodeError:
                errors.append(f"{rel}: binary or non-UTF-8 publishable artifact is forbidden")
                continue
            if rel in API_MACHINE_ARTIFACTS:
                errors.extend(_machine_artifact_errors(text, rel))
            else:
                if _has_forbidden_control(text):
                    errors.append(f"{rel}: control bytes are forbidden in publishable artifacts")
                errors.extend(_privacy_errors(text, rel))
                errors.extend(_restricted_source_errors(text, rel))
                if PREMATURE_COMPLETION_PATTERN.search(text):
                    errors.append(f"{rel}: premature docs milestone or code-doc absence claim")
                if PREMATURE_CONSUMER_PATTERN.search(text):
                    errors.append(f"{rel}: premature gateway or consumer availability claim")

    for directory, required_page in REQUIRED_DOMAIN_PAGES.items():
        dir_path = root / directory
        if not dir_path.is_dir() or dir_path.is_symlink():
            errors.append(f"{directory}: path-domain owner must be a directory")
        elif not any(path.is_file() and not path.is_symlink() for path in dir_path.rglob("*.md")):
            errors.append(f"{directory}: path-domain owner must contain a canonical Markdown page")
        page_path = root / required_page
        if not page_path.is_file() or page_path.is_symlink():
            errors.append(f"{required_page}: required canonical landing page is missing")

    for path in sorted(
        p for p in root.rglob("*") if p.is_file() and not p.is_symlink()
    ):
        if ".git" in path.parts or ".pytest_cache" in path.parts:
            continue
        rel = _rel(path, root)
        if rel in API_MACHINE_ARTIFACTS:
            continue
        try:
            text = _read(path)
        except UnicodeDecodeError:
            continue
        for match in IPV4_CANDIDATE_PATTERN.finditer(text):
            if classify_ipv4(match.group(0)) == "private network":
                line = text.count("\n", 0, match.start()) + 1
                errors.append(f"{rel}:{line}: private IPv4 address found")

    restricted_policy = (root / "development" / "contributing.md")
    if restricted_policy.exists():
        text = _read(restricted_policy)
        if text.count(ALLOWED_RESTRICTED_POLICY_LINE) != 1:
            errors.append("development/contributing.md: missing vendor_restricted quarantine marker")
        if "Restricted material must not appear in public repositories" not in text:
            errors.append("development/contributing.md: missing restricted-source quarantine rule")

    return sorted(set(errors), key=lambda value: value.encode("utf-8"))


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
