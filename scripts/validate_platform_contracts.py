#!/usr/bin/env python3
"""Validate the closed cross-runtime documentation ownership contract."""

from __future__ import annotations

import argparse
import hashlib
import html
import importlib.metadata
import ipaddress
import os
import pathlib
import re
import stat
import string
import subprocess
import sys
import urllib.parse
from collections.abc import Iterable, Mapping
from datetime import datetime, timedelta, timezone
from html.parser import HTMLParser
from typing import Any

import yaml


MANIFEST = pathlib.Path("docs/platform/manifests/eebus-doc-ownership.yaml")
REPOSITORIES = (
    "helianthus-docs",
    "helianthus-docs-ebus",
    "helianthus-docs-eebus",
    "helianthus-eebusreg",
)
TRANSFERRED_PLATFORM = {
    "platform-cross-runtime-envelope": "docs/platform/cross-runtime-envelope.md",
    "platform-hash-auth-binding": "docs/platform/hash-auth-binding.md",
    "platform-shared-registry-boundary": "docs/platform/shared-registry-boundary.md",
    "platform-promotion-consumer-contract": "docs/platform/promotion-and-consumer-contract.md",
    "platform-ownership-validation": "docs/platform/ownership-validation.md",
    "cross-runtime-platform-contracts": "docs/platform/README.md",
}
SURFACES = {
    "protocol",
    "architecture",
    "api",
    "platform",
    "code_repo",
    "summary_only",
}
STATES = {"planned", "candidate", "active", "withdrawn"}
MILESTONES = (
    "MSP-DOCS-API-SCHEMA",
    "MSP-DOCS-PLATFORM",
    "MSP-DOCS-E2",
    "MSP-DOCS-CLEAN",
)
MILESTONE_INDEX = {name: index for index, name in enumerate(MILESTONES)}
TARGET_STATES = {"candidate", "active", "withdrawn"}

EXACT_PYTHON = (3, 12, 10)
EXACT_PYYAML = "6.0.2"
SUPPORTED_PYTHON_MIN = (3, 12, 0)
SUPPORTED_PYTHON_MAX = (3, 15, 0)
SUPPORTED_PYYAML_MIN = (6, 0, 2)
SUPPORTED_PYYAML_MAX = (7, 0, 0)
TOOLCHAIN_MODES = {"exact", "supported"}

MAX_MANIFEST_BYTES = 64 * 1024
MAX_YAML_NESTING = 24
MAX_YAML_ALIASES = 16
MAX_YAML_TOKENS = 8192
MAX_YAML_NODES = 4096

TOP_FIELDS_V1 = {"schema", "version", "entries"}
TOP_FIELDS_V2 = TOP_FIELDS_V1 | {
    "channel_registry",
    "eligible_channels",
    "exact_memberships",
}
ENTRY_FIELDS_V1 = {
    "id",
    "surface",
    "owner",
    "source",
    "canonical",
    "state",
    "outputs",
    "lifecycle",
    "enforcement",
}
ENTRY_FIELDS_V2 = ENTRY_FIELDS_V1 - {"outputs"} | {"kind"}
ENTRY_KIND_FIELDS = {
    "canonical_document": set(),
    "canonical_collection": {"members"},
    "summary_pointer": {"target"},
    "absence_constraint": {"forbidden_states", "channels"},
}
CHANNEL_FIELDS = {"visibility", "owner"}
CHANNEL_VISIBILITIES = {"candidate", "stable"}
LOCATION_FIELDS = {"repository", "path"}
OUTPUT_FIELDS = {
    "candidate",
    "stable_navigation",
    "search",
    "sitemap",
    "versioned_bundle",
    "release_bundle",
}
LIFECYCLE_FIELDS = {
    "created_at",
    "expires_at",
    "source_issue",
    "source_pr",
    "source_ref",
    "content_sha256",
    "approved_at",
    "frozen_at",
    "cleanup_required",
}
LIFECYCLE_TIMESTAMP_FIELDS = {
    "created_at",
    "expires_at",
    "approved_at",
    "frozen_at",
}
ENFORCEMENT_FIELDS = {"milestone", "required_state"}
STABLE_OUTPUTS = OUTPUT_FIELDS - {"candidate"}
CANONICAL_SURFACES = {"protocol", "architecture", "api", "platform"}

IMMUTABLE_REF = re.compile(r"[0-9a-fA-F]{40}\Z")
GITHUB_REPOSITORY = re.compile(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+\Z")
SHA256 = re.compile(r"[0-9a-f]{64}\Z")
ENTRY_ID = re.compile(r"[a-z0-9][a-z0-9-]*\Z")
RFC3339_UTC = re.compile(
    r"[0-9]{4}-(?:0[1-9]|1[0-2])-(?:0[1-9]|[12][0-9]|3[01])"
    r"T(?:[01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9]"
    r"(?:\.[0-9]{1,6})?Z\Z"
)
PRIVATE_IDENTIFIER = re.compile(
    r"(?i)(?:serial|ski|mac|peer[_-]?id|device[_-]?id|token|password|secret)\s*="
)
M625_CROSS_SEED_ID = "platform-m625-public-acquisition-methodology"
M625_CROSS_SEED_PATH = pathlib.Path(
    "docs/platform/msp-0625-public-acquisition-methodology.md"
)
M625_INPUTS_PATH = pathlib.Path(
    "docs/platform/manifests/msp-0625-public-inputs.yaml"
)
# This registry is CI policy, not a property inferred from the manifest or the
# candidate artifacts.  Removing every M6.25 file therefore cannot deactivate
# the MSP-DOCS-CLEAN deliverable.
M625_REQUIRED_DELIVERABLE = {
    "id": M625_CROSS_SEED_ID,
    "page": M625_CROSS_SEED_PATH,
    "input_binding": M625_INPUTS_PATH,
    "milestone": "MSP-DOCS-CLEAN",
}
M625_PLAN_URL = (
    "https://github.com/Project-Helianthus/helianthus-execution-plans/blob/"
    "fb384ab5" "7d79f0020c54d2c66416e8a7666f0ceb/"
    "multi-runtime-semantic-platform.locked/"
    "118-w30-26-m625-raw-spine-feature-acquisition.md"
)
M625_PROVENANCE_URL = (
    "https://api.github.com/repositories/1293598306/contents/"
    "development/msp-0625-provenance-policy.md"
    "?ref=" "cedf238e" "34f879815ba773e9cd76b2b31c2822a3"
)
M625_ARCHITECTURE_URL = (
    "https://api.github.com/repositories/1293598306/contents/"
    "architecture/_candidate/msp-0625-raw-feature-command-path.md"
    "?ref=" "cedf238e" "34f879815ba773e9cd76b2b31c2822a3"
)
M625_EXTERNAL_INPUTS = (
    {
        "repository": "Project-Helianthus/helianthus-execution-plans",
        "ref": "fb384ab5" + "7d79f0020c54d2c66416e8a7666f0ceb",
        "path": (
            "multi-runtime-semantic-platform.locked/"
            "118-w30-26-m625-raw-spine-feature-acquisition.md"
        ),
        "content_sha256": (
            "21c4e525a39090a1c4f4ca6efdedb05978bc9f7588f9acbcaa6039fc21fa4536"
        ),
        "url": M625_PLAN_URL,
    },
    {
        "repository": "Project-Helianthus/helianthus-docs-eebus",
        "ref": "cedf238e" + "34f879815ba773e9cd76b2b31c2822a3",
        "path": "development/msp-0625-provenance-policy.md",
        "content_sha256": (
            "f52a15cab0ec7cfebb67a1932b27259489846619b109ea71e43ca54531191db2"
        ),
        "url": M625_PROVENANCE_URL,
    },
    {
        "repository": "Project-Helianthus/helianthus-docs-eebus",
        "ref": "cedf238e" + "34f879815ba773e9cd76b2b31c2822a3",
        "path": (
            "architecture/_candidate/msp-0625-raw-feature-command-path.md"
        ),
        "content_sha256": (
            "e782c764e5bed3ca103b3544e2bfcb97f7869416184175ad576a90c8f6302e64"
        ),
        "url": M625_ARCHITECTURE_URL,
    },
)
M625_PAGE_TITLE = "M6.25 Public Acquisition Methodology Cross-Seed"
M625_REQUIRED_HEADINGS = (
    "Ownership And Inputs",
    "Two Views, One Non-Escalation Rule",
    "Public Evidence Commitments",
    "Pending State And Falsifier",
)
M625_REQUIRED_CLAUSES = {
    "Ownership And Inputs": (
        "This page owns only language-neutral acquisition, reference-binding, and public evidence methodology.",
        "Protocol, API, and architecture material remains owned by `helianthus-docs-eebus` and is not restated here.",
    ),
    "Two Views, One Non-Escalation Rule": (
        "An owner-authorized local raw operator view may be necessary to perform or audit an authorized acquisition.",
        "A reference presented through a mismatched tier, authorization, runtime, tool, scope, or boundary fails closed before dereference.",
    ),
    "Public Evidence Commitments": (
        "Every tier, including the owner-authorized local raw operator view, prohibits private keys, passwords, credentials, bearer, session, and authentication tokens, cryptographic secrets, and trust-store bytes.",
        "It cannot be replaced by a digest or other deterministic commitment.",
        "Private or vendor-only material cannot support, attribute, or substitute for a public claim.",
    ),
    "Pending State And Falsifier": (
        "This methodology creates no stable API schema, tool name, protocol-native detail, or consumer surface.",
    ),
}
M625_REQUIRED_DOCUMENT_CLAUSES = (
    "Implementation and bounded live validation remain pending their separate gates.",
)
M625_SECTION_PARAGRAPH_COUNTS = {
    "Ownership And Inputs": 4,
    "Two Views, One Non-Escalation Rule": 2,
    "Public Evidence Commitments": 4,
    "Pending State And Falsifier": 2,
}
M625_NEGATIVE_ASSERTION = re.compile(
    r"\b(?:no|not|never|cannot|can't|without|exclude(?:s|d)?|prohibit(?:s|ed)?|"
    r"forbid(?:s|den)?|pending|unverified|withheld|fails?\s+closed)\b",
    re.I,
)
M625_PROTOCOL_OR_API_TERMS = frozenset(
    {
        "api", "command", "endpoint", "field", "frame", "message", "method",
        "payload", "protocol", "query", "tool", "wire",
    }
)
M625_PROTOCOL_OR_API_ACTIONS = frozenset(
    {
        "accept", "call", "declare", "define", "fetch", "provide", "return",
        "send", "support", "use",
    }
)
M625_LIVE_TERMS = frozenset(
    {"deployment", "installation", "live", "operational", "production", "runtime"}
)
M625_LIVE_ACTIONS = frozenset(
    {"active", "available", "implemented", "running", "supported", "validated", "verified", "work"}
)
M625_VENDOR_TERMS = frozenset(
    {"confidential", "manufacturer", "oem", "private", "vendor", "vendor-only"}
)
M625_EVIDENCE_TERMS = frozenset(
    {"document", "evidence", "manual", "material", "source", "specification"}
)
M625_SECRET_TERMS = frozenset(
    {"authentication", "credential", "password", "secret", "session", "token"}
)
M625_SECRET_OUTPUT_ACTIONS = frozenset(
    {"contain", "expose", "include", "publish", "release", "return", "retain"}
)
M625_SECRET_SUBSTITUTES = frozenset(
    {"checksum", "commitment", "digest", "fingerprint", "hash"}
)
M625_RESTRICTED_MATERIAL = re.compile(
    r"(?i)(?:-----BEGIN(?: [A-Z]+)? PRIVATE KEY-----|"
    r"\bbearer\s+(?!tokens?\b|credentials?\b|authentication\b|session\b)\S+|"
    r"\b(?:password|credential|session[ _-]?token|auth(?:entication)?[ _-]?token|"
    r"trust[ _-]?store|private[ _-]?key|cryptographic[ _-]?secret|"
    r"ski|ship[ _-]?id|device[ _-]?id|serial)\s*[:=]\s*\S+)"
)
WINDOWS_ABSOLUTE = re.compile(r"[A-Za-z]:[\\/]")
WINDOWS_INVALID_SEGMENT = re.compile(r'[<>:"|?*\x00-\x1f]')
WINDOWS_RESERVED_SEGMENT = re.compile(
    r"(?:CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(?:\..*)?\Z", re.I
)
NORMATIVE = re.compile(
    r"\b(?:must|shall|should|required|mandatory|acceptance criteria|needs? to)\b",
    re.I,
)
FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")
ATX_HEADING = re.compile(r"^ {0,3}(#{1,6})[ \t]+(.+?)[ \t]*#*[ \t]*$")
SETEXT_HEADING = re.compile(r"^ {0,3}(=+|-+)[ \t]*$")
REFERENCE_DEFINITION = re.compile(
    r"^ {0,3}\[([^\]]+)\]:[ \t]*(?:<([^>\n]+)>|(\S+))"
)
COMMONMARK_BACKSLASH_ESCAPE = re.compile(
    rf"\\([{re.escape(string.punctuation)}])"
)
VERSION = re.compile(r"([0-9]+)\.([0-9]+)\.([0-9]+)\Z")
RENDERED_URL = re.compile(r"\bhttps?://[^\s<>\"']+", re.I)
CLAUSE_BOUNDARY = re.compile(r"(?<=[.!?])\s+")
PREDICATE_BOUNDARY = re.compile(
    r"(?:\s+(?:and|or|but|yet|while|whereas|plus|as\s+well\s+as|"
    r"along\s+with|together\s+with)\s+|"
    r"\s+(?=(?:which|that|who)\b))",
    re.I,
)
COMMA_BOUNDARY = re.compile(r",\s*(?:(?:and|or|but|yet)\s+)?", re.I)
ANY_MODAL = re.compile(
    r"\b(?:must|shall|should|required|mandatory|needs?\s+to|may|might|can|"
    r"could|will|would)\b",
    re.I,
)

PROTOCOL_CONTEXT = re.compile(
    r"\b(?:SHIP|SPINE|SKI|wire protocol|protocol peer|protocol frame|protocol message)\b",
    re.I,
)
PROTOCOL_BEHAVIOR = re.compile(
    r"\b(?:send(?:s|ing)?|receiv(?:e|es|ed|ing)|negotiat(?:e|es|ed|ing)|"
    r"encod(?:e|es|ed|ing)|decod(?:e|es|ed|ing)|respond(?:s|ed|ing)?|"
    r"retr(?:y|ies|ied|ying)|acknowledg(?:e|es|ed|ing)|"
    r"advertis(?:e|es|ed|ing)|initiat(?:e|es|ed|ing)|"
    r"establish(?:es|ed|ing)?|clos(?:e|es|ed|ing))\b",
    re.I,
)
ARCHITECTURE_CONTEXT = re.compile(
    r"\beebus\b.*\b(?:runtime|trust|persistence|lifecycle|adapter|reconnect|"
    r"session store|cache)\b|\b(?:runtime|trust|persistence|lifecycle|adapter|"
    r"reconnect|session store|cache)\b.*\beebus\b",
    re.I | re.S,
)
ARCHITECTURE_BEHAVIOR = re.compile(
    r"\b(?:persist|store|load|restore|reconnect|manage|own|create|listen|cache)s?\b",
    re.I,
)
API_CONTEXT = re.compile(
    r"\beebus\b.*\b(?:Go API|package|function|method|symbol|signature|public API)\b|"
    r"\b(?:Go API|package|function|method|symbol|signature|public API)\b.*\beebus\b",
    re.I | re.S,
)
API_BEHAVIOR = re.compile(
    r"\b(?:expos(?:e|es|ed|ing)|export(?:s|ed|ing)?|return(?:s|ed|ing)?|"
    r"accept(?:s|ed|ing)?|declar(?:e|es|ed|ing)|defin(?:e|es|ed|ing)|"
    r"provid(?:e|es|ed|ing))\b",
    re.I,
)
GO_DECLARATION = re.compile(r"\bfunc\s+[A-Z][A-Za-z0-9_]*\s*\(")
NON_NORMATIVE = re.compile(
    r"\b(?:non[- ]normative|informative only|example only)\b", re.I
)
NON_NORMATIVE_LEAD = re.compile(
    r"\b(?:non[- ]normative|informative)\b.*"
    r"\b(?:example|quotation|quote|excerpt|reference)\b",
    re.I,
)
DOCUMENTATION_OWNERSHIP = re.compile(
    r"(?:\b(?:documentation|docs?|page|repository)\b[^.!?]{0,80}"
    r"\b(?:must|shall|required)\b[^.!?]{0,80}"
    r"\b(?:own|ownership|summar(?:y|ize|izes|ized)|link|reference|"
    r"source of truth)\b|"
    r"\b(?:must|shall|required)\b[^.!?]{0,80}"
    r"\b(?:owned|documented|summarized|linked|referenced)\b[^.!?]{0,80}"
    r"\b(?:documentation|docs?|page|repository|source of truth)\b)",
    re.I,
)
PLATFORM_GOVERNANCE_CONTEXT = re.compile(
    r"\b(?:gate|proof|artifact|evidence|ownership|summary)\b", re.I
)
PLATFORM_GOVERNANCE_PROSE = re.compile(
    r"\b(?:artifact|evidence|proof|case|result|record|claim|reference|scope)\w*\b",
    re.I,
)
PLATFORM_GOVERNANCE_ACTION = re.compile(
    r"\b(?:record|report|claim|prove|verify|capture|include|reference|link|"
    r"document|state)s?\b",
    re.I,
)
GOVERNANCE_COMPLEMENT = re.compile(
    r"\b(?:record|report|claim|prove|verify|capture|include|reference|link|"
    r"document|state)s?\b[^,;]*\b(?:whether|if)\b",
    re.I,
)
NEGATIVE_GOVERNANCE_CLAIM = re.compile(
    r"\b(?:must|shall|should|needs?\s+to)\s+not\s+"
    r"(?:claim|report|state|document)\b",
    re.I,
)
OBSERVATION_SUBJECT = re.compile(
    r"\s*(?:(?:the|a|an)\s+)?(?:[A-Za-z][A-Za-z0-9_-]*\s+){1,6}\Z", re.I
)

IPV4_LITERAL = re.compile(r"\b(?:(?:\d{1,3})\.){3}(?:\d{1,3})\b")
IPV6_LITERAL = re.compile(
    r"\[(?P<bracketed>[0-9A-Fa-f:.]+(?:%[0-9A-Za-z_.-]+)?)\]|"
    r"(?<![0-9A-Za-z])(?P<bare>(?:[0-9A-Fa-f]{0,4}:){2,}"
    r"[0-9A-Fa-f:.]*(?:%[0-9A-Za-z_.-]+)?)(?![0-9A-Za-z])"
)
PRIVATE_IPV4_NETWORKS = (
    ipaddress.IPv4Network((10 << 24, 8)),
    ipaddress.IPv4Network(((172 << 24) | (16 << 16), 12)),
    ipaddress.IPv4Network(((192 << 24) | (168 << 16), 16)),
    ipaddress.IPv4Network(((100 << 24) | (64 << 16), 10)),
    ipaddress.IPv4Network(((169 << 24) | (254 << 16), 16)),
)
PRIVATE_IPV6_NETWORKS = (
    ipaddress.IPv6Network((0xFC00 << 112, 7)),
    ipaddress.IPv6Network((0xFE80 << 112, 10)),
)
LOOPBACK_IPV6 = ipaddress.IPv6Address(1)

DOCUMENTATION_EXTENSIONS = {
    ".adoc",
    ".asciidoc",
    ".markdown",
    ".md",
    ".mdown",
    ".mkd",
    ".rst",
    ".txt",
}
MARKDOWN_EXTENSIONS = {".markdown", ".md", ".mdown", ".mkd"}
DOCUMENTATION_NAMES = re.compile(
    r"(?:README|ARCHITECTURE|DESIGN|PROTOCOL|API|CONTRIBUTING|CHANGELOG|"
    r"SECURITY|SUPPORT|GOVERNANCE|ROADMAP)(?:\..*)?\Z",
    re.I,
)
NONPUBLISHABLE_DIRECTORIES = {
    ".cache",
    ".git",
    ".pytest_cache",
    ".venv",
    "__pycache__",
    "build",
    "cache",
    "coverage",
    "dist",
    "generated",
    "node_modules",
    "out",
    "target",
    "vendor",
    "venv",
}


class _ManifestSchemaError(Exception):
    """Internal marker for non-reflective manifest parse failures."""


def _result(categories: Iterable[str]) -> list[str]:
    return sorted(set(categories))


def _run_git(root: pathlib.Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(root), *args],
        check=False,
        capture_output=True,
        text=True,
    )


def _run_git_bytes(
    root: pathlib.Path, *args: str
) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        ["git", "-C", str(root), *args],
        check=False,
        capture_output=True,
    )


def _clean_checkout(root: pathlib.Path) -> bool:
    inside = _run_git(root, "rev-parse", "--is-inside-work-tree")
    if inside.returncode != 0 or inside.stdout.strip() != "true":
        return False
    status_result = _run_git(
        root, "status", "--porcelain=v1", "--untracked-files=all"
    )
    return status_result.returncode == 0 and not status_result.stdout


def _checkout_matches_ref(root: pathlib.Path, ref: str | None) -> bool:
    if not isinstance(ref, str) or IMMUTABLE_REF.fullmatch(ref) is None:
        return False
    resolved = _run_git(root, "rev-parse", "--verify", f"{ref}^{{commit}}")
    head = _run_git(root, "rev-parse", "HEAD")
    return (
        resolved.returncode == 0
        and head.returncode == 0
        and resolved.stdout.strip().casefold() == ref.casefold()
        and head.stdout.strip().casefold() == ref.casefold()
    )


def _candidate_ref_matches_checkout(
    root: pathlib.Path, source_ref: str, pinned_ref: str | None
) -> bool:
    object_type = _run_git(root, "cat-file", "-t", source_ref)
    head = _run_git(root, "rev-parse", "--verify", "HEAD^{commit}")
    if (
        object_type.returncode != 0
        or object_type.stdout.strip() != "commit"
        or head.returncode != 0
        or head.stdout.strip().casefold() != source_ref.casefold()
    ):
        return False
    if pinned_ref is None or IMMUTABLE_REF.fullmatch(pinned_ref) is None:
        return True
    return pinned_ref.casefold() == source_ref.casefold()


def _remote_repository(value: str) -> str | None:
    remote = value.strip().removesuffix(".git")
    if remote.startswith("git@github.com:"):
        return remote.split(":", 1)[1]
    parsed = urllib.parse.urlsplit(remote)
    if parsed.hostname == "github.com":
        return parsed.path.lstrip("/")
    return None


def _repository_root_valid(root: pathlib.Path, expected_repository: str) -> bool:
    try:
        root_stat = root.lstat()
    except OSError:
        return False
    if stat.S_ISLNK(root_stat.st_mode) or not stat.S_ISDIR(root_stat.st_mode):
        return False
    top = _run_git(root, "rev-parse", "--show-toplevel")
    remote = _run_git(root, "remote", "get-url", "origin")
    if top.returncode != 0 or remote.returncode != 0:
        return False
    try:
        top_path = pathlib.Path(top.stdout.strip()).resolve(strict=True)
        root_path = root.resolve(strict=True)
    except OSError:
        return False
    actual = _remote_repository(remote.stdout)
    return (
        top_path == root_path
        and actual is not None
        and actual.casefold() == expected_repository.casefold()
    )


def _portable_path(value: str) -> bool:
    parts = value.split("/")
    return (
        bool(value)
        and not value.startswith(("/", "~", "./"))
        and WINDOWS_ABSOLUTE.match(value) is None
        and "\\" not in value
        and "//" not in value
        and all(part not in {"", ".", ".."} for part in parts)
        and all(WINDOWS_INVALID_SEGMENT.search(part) is None for part in parts)
        and all(not part.endswith((".", " ")) for part in parts)
        and all(WINDOWS_RESERVED_SEGMENT.fullmatch(part) is None for part in parts)
    )


def _path_at_or_below(value: str, prefix: str) -> bool:
    path_parts = pathlib.PurePosixPath(value).parts
    prefix_parts = pathlib.PurePosixPath(prefix).parts
    return path_parts[: len(prefix_parts)] == prefix_parts


def _location_matches(
    location: Mapping[str, str], repository: str, prefix: str
) -> bool:
    return location["repository"] == repository and _path_at_or_below(
        location["path"], prefix
    )


def _surface_binding_valid(entry: Mapping[str, Any]) -> bool:
    surface = entry["surface"]
    owner = entry["owner"]
    source = entry["source"]
    if surface == "protocol":
        return _location_matches(
            owner, "helianthus-docs-eebus", "protocols"
        ) and _location_matches(source, "helianthus-docs-eebus", "protocols")
    if surface == "architecture":
        return _location_matches(
            owner, "helianthus-docs-eebus", "architecture"
        ) and _location_matches(source, "helianthus-docs-eebus", "architecture")
    if surface == "api":
        source_valid = _location_matches(
            source, "helianthus-docs-eebus", "api"
        ) or _location_matches(source, "helianthus-eebusreg", "api")
        return (
            _location_matches(owner, "helianthus-docs-eebus", "api")
            and source_valid
        )
    if surface == "platform":
        methodology = M625_CROSS_SEED_PATH.as_posix()
        transferred = TRANSFERRED_PLATFORM.get(entry["id"])
        if transferred is not None:
            if owner["path"] != transferred or source["path"] != transferred:
                return False
            current = (
                owner["repository"] == "helianthus-docs"
                and source["repository"] == "helianthus-docs"
            )
            historical = (
                owner["repository"] == "helianthus-docs-ebus"
                and source["repository"] == "helianthus-docs-ebus"
            )
            return current or historical
        if entry["id"] == M625_CROSS_SEED_ID:
            if owner["path"] != methodology or source["path"] != methodology:
                return False
            historical = (
                owner["repository"] == "helianthus-docs-ebus"
                and source["repository"] == "helianthus-docs-ebus"
            )
            later = (
                owner["repository"] == "helianthus-docs-eebus"
                and source["repository"] == "helianthus-docs-eebus"
            )
            return historical or later
        return _location_matches(
            owner, "helianthus-docs", "docs/platform"
        ) and _location_matches(
            source, "helianthus-docs", "docs/platform"
        )
    if surface == "code_repo":
        return _location_matches(
            owner, "helianthus-eebusreg", "docs"
        ) and _location_matches(source, "helianthus-eebusreg", "docs")
    if surface == "summary_only":
        return owner == {
            "repository": "helianthus-eebusreg",
            "path": "README.md",
        } and source == {
            "repository": "helianthus-docs-eebus",
            "path": "README.md",
        }
    return False


def _artifact_kind(root: pathlib.Path, relative: str) -> str:
    if not _portable_path(relative):
        return "outside"
    try:
        root_path = root.absolute()
        root_stat = root_path.lstat()
    except OSError:
        return "missing"
    if stat.S_ISLNK(root_stat.st_mode) or not stat.S_ISDIR(root_stat.st_mode):
        return "symlink" if stat.S_ISLNK(root_stat.st_mode) else "invalid"

    current = root_path
    parts = pathlib.PurePosixPath(relative).parts
    for index, part in enumerate(parts):
        current = current / part
        try:
            item_stat = current.lstat()
        except FileNotFoundError:
            return "missing"
        except OSError:
            return "invalid"
        if stat.S_ISLNK(item_stat.st_mode):
            return "symlink"
        if index < len(parts) - 1 and not stat.S_ISDIR(item_stat.st_mode):
            return "invalid"

    try:
        resolved_root = root_path.resolve(strict=True)
        resolved_item = current.resolve(strict=True)
    except OSError:
        return "invalid"
    if not resolved_item.is_relative_to(resolved_root):
        return "outside"
    final_stat = current.lstat()
    if stat.S_ISREG(final_stat.st_mode):
        return "regular"
    if stat.S_ISDIR(final_stat.st_mode):
        return "directory"
    return "invalid"


def _regular_path_without_symlinks(path: pathlib.Path) -> bool:
    absolute = path.absolute()
    if not absolute.anchor:
        return False
    current = pathlib.Path(absolute.anchor)
    try:
        root_stat = current.lstat()
    except OSError:
        return False
    if stat.S_ISLNK(root_stat.st_mode) or not stat.S_ISDIR(root_stat.st_mode):
        return False
    parts = absolute.parts[1:]
    for index, part in enumerate(parts):
        current = current / part
        try:
            item_stat = current.lstat()
        except OSError:
            return False
        if stat.S_ISLNK(item_stat.st_mode):
            return False
        if index < len(parts) - 1:
            if not stat.S_ISDIR(item_stat.st_mode):
                return False
        elif not stat.S_ISREG(item_stat.st_mode):
            return False
    return bool(parts)


def _read_regular_artifact(root: pathlib.Path, relative: str) -> bytes | None:
    if _artifact_kind(root, relative) != "regular":
        return None
    try:
        return (root / pathlib.PurePosixPath(relative)).read_bytes()
    except OSError:
        return None


def _scan_yaml_resources(text: str) -> None:
    alias_count = 0
    depth = 0
    token_count = 0
    starts = (
        yaml.tokens.BlockMappingStartToken,
        yaml.tokens.BlockSequenceStartToken,
        yaml.tokens.FlowMappingStartToken,
        yaml.tokens.FlowSequenceStartToken,
    )
    ends = (
        yaml.tokens.BlockEndToken,
        yaml.tokens.FlowMappingEndToken,
        yaml.tokens.FlowSequenceEndToken,
    )
    for token in yaml.scan(text, Loader=yaml.SafeLoader):
        token_count += 1
        if token_count > MAX_YAML_TOKENS:
            raise _ManifestSchemaError
        if isinstance(token, yaml.tokens.AliasToken):
            alias_count += 1
            if alias_count > MAX_YAML_ALIASES:
                raise _ManifestSchemaError
        if isinstance(token, starts):
            depth += 1
            if depth > MAX_YAML_NESTING:
                raise _ManifestSchemaError
        elif isinstance(token, ends):
            depth = max(0, depth - 1)


def _inspect_yaml_node(root: yaml.nodes.Node | None) -> None:
    if root is None:
        raise _ManifestSchemaError
    seen: set[int] = set()
    active: set[int] = set()
    node_count = 0

    def visit(node: yaml.nodes.Node, depth: int) -> None:
        nonlocal node_count
        if depth > MAX_YAML_NESTING:
            raise _ManifestSchemaError
        identity = id(node)
        if identity in active:
            raise _ManifestSchemaError
        if identity in seen:
            return
        seen.add(identity)
        active.add(identity)
        node_count += 1
        if node_count > MAX_YAML_NODES:
            raise _ManifestSchemaError
        try:
            if isinstance(node, yaml.nodes.MappingNode):
                keys: set[str] = set()
                for key, value in node.value:
                    if (
                        not isinstance(key, yaml.nodes.ScalarNode)
                        or key.tag != "tag:yaml.org,2002:str"
                        or key.value in keys
                    ):
                        raise _ManifestSchemaError
                    keys.add(key.value)
                    visit(key, depth + 1)
                    visit(value, depth + 1)
            elif isinstance(node, yaml.nodes.SequenceNode):
                for value in node.value:
                    visit(value, depth + 1)
            elif not isinstance(node, yaml.nodes.ScalarNode):
                raise _ManifestSchemaError
        finally:
            active.remove(identity)

    visit(root, 1)


def _parse_manifest_bytes(raw: bytes) -> dict[str, Any] | None:
    loader: yaml.SafeLoader | None = None
    try:
        if len(raw) > MAX_MANIFEST_BYTES:
            raise _ManifestSchemaError
        text = raw.decode("utf-8")
        _scan_yaml_resources(text)
        loader = yaml.SafeLoader(text)
        node = loader.get_single_node()
        _inspect_yaml_node(node)
        assert node is not None
        loaded = loader.construct_document(node)
    except (
        OSError,
        UnicodeError,
        yaml.YAMLError,
        RecursionError,
        MemoryError,
        OverflowError,
        _ManifestSchemaError,
    ):
        return None
    finally:
        if loader is not None:
            loader.dispose()
    if not isinstance(loaded, dict):
        return None
    return loaded


def _parse_manifest_path(path: pathlib.Path) -> dict[str, Any] | None:
    try:
        if not _regular_path_without_symlinks(path):
            raise _ManifestSchemaError
        return _parse_manifest_bytes(path.read_bytes())
    except (OSError, _ManifestSchemaError):
        return None


def _load_manifest(root: pathlib.Path) -> tuple[dict[str, Any] | None, str | None]:
    kind = _artifact_kind(root, MANIFEST.as_posix())
    if kind == "missing":
        return None, "manifest.missing"
    if kind != "regular":
        return None, "manifest.schema"
    loaded = _parse_manifest_path(root / MANIFEST)
    return (loaded, None) if loaded is not None else (None, "manifest.schema")


def _optional_text(value: Any) -> bool:
    return value is None or isinstance(value, str)


def _common_entry_schema_valid(entry: Mapping[str, Any], ids: set[str]) -> bool:
    entry_id = entry.get("id")
    surface = entry.get("surface")
    if (
        not isinstance(entry_id, str)
        or ENTRY_ID.fullmatch(entry_id) is None
        or entry_id in ids
        or not isinstance(surface, str)
        or surface not in SURFACES
        or not isinstance(entry.get("canonical"), bool)
        or not isinstance(entry.get("state"), str)
    ):
        return False
    ids.add(entry_id)
    for field in ("owner", "source"):
        location = entry.get(field)
        if (
            not isinstance(location, dict)
            or set(location) != LOCATION_FIELDS
            or location.get("repository") not in REPOSITORIES
            or not isinstance(location.get("path"), str)
            or not location.get("path")
        ):
            return False
    lifecycle = entry.get("lifecycle")
    if not isinstance(lifecycle, dict) or set(lifecycle) != LIFECYCLE_FIELDS:
        return False
    if _parse_instant(lifecycle.get("created_at")) is None:
        return False
    if any(
        not _optional_text(lifecycle.get(key))
        for key in LIFECYCLE_FIELDS - {"created_at", "cleanup_required"}
    ):
        return False
    if any(
        lifecycle.get(key) is not None
        and _parse_instant(lifecycle.get(key)) is None
        for key in LIFECYCLE_TIMESTAMP_FIELDS - {"created_at"}
    ):
        return False
    if not isinstance(lifecycle.get("cleanup_required"), bool):
        return False
    enforcement = entry.get("enforcement")
    milestone = enforcement.get("milestone") if isinstance(enforcement, dict) else None
    required_state = (
        enforcement.get("required_state") if isinstance(enforcement, dict) else None
    )
    return bool(
        isinstance(enforcement, dict)
        and set(enforcement) == ENFORCEMENT_FIELDS
        and isinstance(milestone, str)
        and milestone in MILESTONE_INDEX
        and isinstance(required_state, str)
        and required_state in TARGET_STATES
    )


def _schema_valid_v1(manifest: Mapping[str, Any]) -> bool:
    if set(manifest) != TOP_FIELDS_V1:
        return False
    if not isinstance(manifest.get("schema"), str):
        return False
    version = manifest.get("version")
    if not isinstance(version, int) or isinstance(version, bool):
        return False
    entries = manifest.get("entries")
    if not isinstance(entries, list) or not entries:
        return False

    ids: set[str] = set()
    for entry in entries:
        if not isinstance(entry, dict) or set(entry) != ENTRY_FIELDS_V1:
            return False
        if not _common_entry_schema_valid(entry, ids):
            return False
        outputs = entry.get("outputs")
        if (
            not isinstance(outputs, dict)
            or set(outputs) != OUTPUT_FIELDS
            or any(not isinstance(outputs.get(key), bool) for key in OUTPUT_FIELDS)
        ):
            return False
    return True


def _sorted_unique_names(value: Any, allowed: set[str]) -> bool:
    return bool(
        isinstance(value, list)
        and all(isinstance(item, str) and item in allowed for item in value)
        and value == sorted(set(value))
    )


def _schema_valid_v2(manifest: Mapping[str, Any]) -> bool:
    if set(manifest) != TOP_FIELDS_V2 or manifest.get("version") != 2:
        return False
    if manifest.get("schema") != "helianthus.platform.doc-ownership":
        return False
    entries = manifest.get("entries")
    registry = manifest.get("channel_registry")
    eligible = manifest.get("eligible_channels")
    memberships = manifest.get("exact_memberships")
    if (
        not isinstance(entries, list)
        or not entries
        or not isinstance(registry, dict)
        or not registry
        or not isinstance(eligible, dict)
        or not isinstance(memberships, dict)
        or set(memberships) != set(registry)
    ):
        return False

    channels = set(registry)
    for channel, definition in registry.items():
        if (
            not isinstance(channel, str)
            or ENTRY_ID.fullmatch(channel) is None
            or not isinstance(definition, dict)
            or set(definition) != CHANNEL_FIELDS
            or definition.get("visibility") not in CHANNEL_VISIBILITIES
            or not isinstance(definition.get("owner"), str)
            or not definition["owner"]
        ):
            return False

    ids: set[str] = set()
    entries_by_id: dict[str, Mapping[str, Any]] = {}
    for entry in entries:
        if not isinstance(entry, dict):
            return False
        kind = entry.get("kind")
        kind_fields = ENTRY_KIND_FIELDS.get(kind) if isinstance(kind, str) else None
        if kind_fields is None or set(entry) != ENTRY_FIELDS_V2 | kind_fields:
            return False
        if not _common_entry_schema_valid(entry, ids):
            return False
        entries_by_id[entry["id"]] = entry

    for entry_id, entry_channels in eligible.items():
        if entry_id not in entries_by_id or not _sorted_unique_names(
            entry_channels, channels
        ):
            return False
    for channel, members in memberships.items():
        if not _sorted_unique_names(members, ids):
            return False
        for entry_id in members:
            if (
                channel not in eligible.get(entry_id, [])
                or entries_by_id[entry_id]["state"] != "active"
                or entries_by_id[entry_id]["kind"]
                not in {"canonical_document", "canonical_collection"}
                or not entries_by_id[entry_id]["canonical"]
            ):
                return False

    for entry in entries:
        entry_id = entry["id"]
        kind = entry["kind"]
        if kind == "canonical_collection":
            if not _sorted_unique_names(entry["members"], ids - {entry_id}):
                return False
            if any(
                entries_by_id[member]["kind"] != "canonical_document"
                or entries_by_id[member]["state"] != "active"
                or not entries_by_id[member]["canonical"]
                for member in entry["members"]
            ):
                return False
        elif kind == "summary_pointer":
            target = entries_by_id.get(entry["target"])
            if (
                entry["canonical"]
                or eligible.get(entry_id, [])
                or any(entry_id in members for members in memberships.values())
                or target is None
                or target["kind"]
                not in {"canonical_document", "canonical_collection"}
                or target["state"] != "active"
                or not target["canonical"]
            ):
                return False
        elif kind == "absence_constraint":
            if (
                entry["canonical"]
                or eligible.get(entry_id, [])
                or any(entry_id in members for members in memberships.values())
                or entry["forbidden_states"] != ["candidate"]
                or entry["channels"] != sorted(channels)
            ):
                return False
        if kind in {"canonical_document", "canonical_collection"}:
            for channel in eligible.get(entry_id, []):
                if (
                    entry["state"] == "active"
                    and entry_id not in memberships[channel]
                ):
                    return False
        if entry["state"] == "candidate" and any(
            entry_id in members for members in memberships.values()
        ):
            return False
    return True


def _schema_valid(manifest: Mapping[str, Any]) -> bool:
    fields = set(manifest)
    if fields == TOP_FIELDS_V1:
        return _schema_valid_v1(manifest)
    if fields == TOP_FIELDS_V2:
        return _schema_valid_v2(manifest)
    return False


def _parse_instant(value: Any) -> datetime | None:
    if not isinstance(value, str) or RFC3339_UTC.fullmatch(value) is None:
        return None
    try:
        parsed = datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError:
        return None
    if parsed.tzinfo is None or parsed.utcoffset() != timedelta(0):
        return None
    return parsed.astimezone(timezone.utc)


def _all_strings(value: Any) -> Iterable[str]:
    seen: set[int] = set()

    def walk(item: Any) -> Iterable[str]:
        if isinstance(item, str):
            yield item
            return
        if not isinstance(item, (Mapping, list)):
            return
        identity = id(item)
        if identity in seen:
            return
        seen.add(identity)
        if isinstance(item, Mapping):
            for child in item.values():
                yield from walk(child)
        else:
            for child in item:
                yield from walk(child)

    yield from walk(value)


def _private_network_literals(value: str) -> list[tuple[str, int]]:
    private: list[tuple[str, int]] = []
    for match in IPV4_LITERAL.finditer(value):
        literal = match.group(0)
        try:
            address = ipaddress.ip_address(literal)
        except ValueError:
            continue
        if any(address in network for network in PRIVATE_IPV4_NETWORKS):
            private.append((literal, match.start()))

    for match in IPV6_LITERAL.finditer(value):
        literal = match.group("bracketed") or match.group("bare")
        try:
            address = ipaddress.ip_address(literal)
        except ValueError:
            continue
        if not isinstance(address, ipaddress.IPv6Address):
            continue
        mapped = address.ipv4_mapped
        if (
            address == LOOPBACK_IPV6
            or any(address in network for network in PRIVATE_IPV6_NETWORKS)
            or (
                mapped is not None
                and any(mapped in network for network in PRIVATE_IPV4_NETWORKS)
            )
        ):
            private.append((literal, match.start()))
    return private


def _contains_private_network(value: str) -> bool:
    return bool(_private_network_literals(value))


def _manifest_categories(manifest: dict[str, Any]) -> set[str]:
    categories: set[str] = set()
    if manifest["schema"] != "helianthus.platform.doc-ownership":
        categories.add("manifest.schema")
    if (
        set(manifest) == TOP_FIELDS_V1
        and manifest["version"] != 1
    ) or (
        set(manifest) == TOP_FIELDS_V2
        and manifest["version"] != 2
    ):
        categories.add("manifest.version")
    manifest_surfaces = [entry["surface"] for entry in manifest["entries"]]
    if set(manifest_surfaces) != SURFACES:
        categories.add("ownership.surface-missing")
    duplicate_surfaces = {
        surface
        for surface in manifest_surfaces
        if manifest_surfaces.count(surface) > 1
    }
    allowed_duplicate_surfaces = (
        {"platform"} if set(manifest) == TOP_FIELDS_V2 else set()
    )
    if duplicate_surfaces - allowed_duplicate_surfaces:
        categories.add("ownership.surface-duplicate")

    pairs: set[tuple[str, str, str, str]] = set()
    canonical_owners: set[tuple[str, str]] = set()
    for entry in manifest["entries"]:
        pair = (
            entry["owner"]["repository"],
            entry["owner"]["path"],
            entry["source"]["repository"],
            entry["source"]["path"],
        )
        if pair in pairs:
            categories.add("ownership.pair-duplicate")
        pairs.add(pair)
        if entry["canonical"]:
            owner = (entry["owner"]["repository"], entry["owner"]["path"])
            if owner in canonical_owners:
                categories.add("ownership.canonical-duplicate")
            canonical_owners.add(owner)
        for location in (entry["owner"], entry["source"]):
            if not _portable_path(location["path"]):
                categories.add("path.absolute")
        if all(
            _portable_path(location["path"])
            for location in (entry["owner"], entry["source"])
        ) and not _surface_binding_valid(entry):
            categories.add("ownership.surface-binding")
        if entry["state"] in STATES:
            expected_canonical = (
                entry["surface"] in CANONICAL_SURFACES
                and entry["state"] == "active"
            )
            if entry["canonical"] != expected_canonical:
                categories.add("ownership.canonical-state")

    if any(
        PRIVATE_IDENTIFIER.search(value) or _contains_private_network(value)
        for value in _all_strings(manifest)
    ):
        categories.add("privacy.private-identifier")
    return categories


def _enforcement_categories(
    manifest: dict[str, Any], enforce_through: str
) -> set[str]:
    if enforce_through not in MILESTONE_INDEX:
        return {"enforcement.stage"}
    stage = MILESTONE_INDEX[enforce_through]
    for entry in manifest["entries"]:
        enforcement = entry["enforcement"]
        required_at = MILESTONE_INDEX[enforcement["milestone"]]
        state = entry["state"]
        if state not in STATES:
            continue
        if state == "withdrawn":
            if enforcement["required_state"] not in {"candidate", "withdrawn"}:
                return {"enforcement.transition"}
            continue
        if required_at <= stage:
            if state != enforcement["required_state"]:
                return {"enforcement.transition"}
        elif state not in {"planned", "candidate"}:
            return {"enforcement.transition"}
    return set()


def _state_categories(
    manifest: dict[str, Any],
    roots: Mapping[str, pathlib.Path],
    refs: Mapping[str, str | None] | None = None,
) -> set[str]:
    categories: set[str] = set()
    is_v2 = set(manifest) == TOP_FIELDS_V2
    for entry in manifest["entries"]:
        state = entry["state"]
        if state not in STATES:
            categories.add("state.invalid")
            continue

        lifecycle = entry["lifecycle"]
        if is_v2:
            eligible_channels = set(
                manifest["eligible_channels"].get(entry["id"], [])
            )
            published_channels = {
                channel
                for channel, members in manifest["exact_memberships"].items()
                if entry["id"] in members
            }
            stable_eligible = {
                channel
                for channel in eligible_channels
                if manifest["channel_registry"][channel]["visibility"] == "stable"
            }
            candidate_eligible = eligible_channels - stable_eligible
            has_publication = bool(eligible_channels or published_channels)
        else:
            outputs = entry["outputs"]
            stable_eligible = {
                key for key in STABLE_OUTPUTS if outputs[key]
            }
            candidate_eligible = {"candidate"} if outputs["candidate"] else set()
            published_channels = stable_eligible | candidate_eligible
            has_publication = any(outputs.values())
        created = _parse_instant(lifecycle["created_at"])
        expires = _parse_instant(lifecycle["expires_at"])
        approved = _parse_instant(lifecycle["approved_at"])
        frozen = _parse_instant(lifecycle["frozen_at"])

        if state == "planned":
            invalid = (
                created is None
                or expires is None
                or expires - created != timedelta(days=14)
                or entry["canonical"]
                or has_publication
                or not (lifecycle["source_issue"] or lifecycle["source_pr"])
                or lifecycle["source_ref"] is not None
                or lifecycle["content_sha256"] is not None
                or approved is not None
                or frozen is not None
                or lifecycle["cleanup_required"]
            )
            if invalid:
                categories.add("state.planned")

        elif state == "candidate":
            hidden = "_candidate" in pathlib.PurePosixPath(
                entry["owner"]["path"]
            ).parts
            source_ref = lifecycle["source_ref"]
            content_hash = lifecycle["content_sha256"]
            invalid = (
                created is None
                or expires is None
                or expires - created != timedelta(days=30)
                or entry["canonical"]
                or (not is_v2 and not candidate_eligible)
                or bool(stable_eligible)
                or bool(published_channels - candidate_eligible)
                or not hidden
                or not lifecycle["source_pr"]
                or not isinstance(source_ref, str)
                or IMMUTABLE_REF.fullmatch(source_ref or "") is None
                or not isinstance(content_hash, str)
                or SHA256.fullmatch(content_hash or "") is None
                or approved is not None
                or frozen is not None
                or lifecycle["cleanup_required"]
            )
            source_root = roots.get(entry["source"]["repository"])
            if not invalid and source_root is not None:
                pinned_ref = (
                    refs.get(entry["source"]["repository"])
                    if refs is not None
                    else None
                )
                invalid = not _candidate_ref_matches_checkout(
                    source_root, source_ref, pinned_ref
                )
                if (
                    not invalid
                    and _artifact_kind(source_root, entry["source"]["path"])
                    == "regular"
                ):
                    shown = _run_git_bytes(
                        source_root,
                        "show",
                        f"{source_ref}:{entry['source']['path']}",
                    )
                    invalid = shown.returncode != 0 or hashlib.sha256(
                        shown.stdout
                    ).hexdigest() != content_hash
            if invalid:
                categories.add("state.candidate")

        elif state == "active":
            invalid = (
                created is None
                or lifecycle["expires_at"] is not None
                or approved is None
                or frozen is None
                or not (created <= approved <= frozen)
                or bool(candidate_eligible)
                or (
                    not is_v2
                    and stable_eligible != STABLE_OUTPUTS
                )
                or (
                    is_v2
                    and entry["kind"]
                    in {"canonical_document", "canonical_collection"}
                    and not published_channels
                )
                or lifecycle["cleanup_required"]
            )
            if invalid:
                categories.add("state.active")

        elif state == "withdrawn":
            invalid = (
                created is None
                or entry["canonical"]
                or has_publication
                or lifecycle["expires_at"] is not None
                or approved is not None
                or frozen is not None
                or not lifecycle["cleanup_required"]
            )
            if invalid:
                categories.add("state.withdrawn")
    return categories


def _artifact_categories(
    manifest: dict[str, Any], roots: Mapping[str, pathlib.Path]
) -> set[str]:
    categories: set[str] = set()
    for entry in manifest["entries"]:
        state = entry["state"]
        if state in {"active", "candidate"}:
            owner = entry["owner"]
            owner_root = roots.get(owner["repository"])
            owner_kind = (
                _artifact_kind(owner_root, owner["path"])
                if owner_root is not None
                else None
            )
            if owner_kind == "symlink":
                categories.add("path.symlink")
            elif owner_kind == "outside":
                categories.add("path.absolute")
            elif owner_kind is not None and owner_kind != "regular":
                categories.add("artifact.owner")

            source = entry["source"]
            same_location = source == owner
            source_root = roots.get(source["repository"])
            source_kind = (
                owner_kind
                if same_location
                else (
                    _artifact_kind(source_root, source["path"])
                    if source_root is not None
                    else None
                )
            )
            if same_location and owner_kind != "regular":
                continue
            if source_kind == "symlink":
                categories.add("path.symlink")
            elif source_kind == "outside":
                categories.add("path.absolute")
            elif source_kind is not None and source_kind != "regular":
                categories.add("artifact.source")

        elif state == "withdrawn":
            checked: set[tuple[str, str]] = set()
            for location in (entry["owner"], entry["source"]):
                identity = (location["repository"], location["path"])
                if identity in checked:
                    continue
                checked.add(identity)
                location_root = roots.get(location["repository"])
                if location_root is not None and _artifact_kind(
                    location_root, location["path"]
                ) != "missing":
                    categories.add("artifact.withdrawn")
    return categories


def _expiry_categories(
    manifest: dict[str, Any], evaluated_at: str | None, evaluation_source: str | None
) -> set[str]:
    if not isinstance(evaluation_source, str) or not evaluation_source.strip():
        return {"expiry.source"}
    evaluated = _parse_instant(evaluated_at)
    if evaluated is None:
        return {"expiry.timestamp"}
    categories: set[str] = set()
    for entry in manifest["entries"]:
        state = entry["state"]
        if state not in {"planned", "candidate"}:
            continue
        expires = _parse_instant(entry["lifecycle"]["expires_at"])
        if expires is not None and evaluated >= expires:
            categories.add(f"expiry.{state}")
    return categories


def _strip_inline_code(line: str) -> str:
    result: list[str] = []
    index = 0
    while index < len(line):
        if line[index] != "`":
            result.append(line[index])
            index += 1
            continue
        end_run = index
        while end_run < len(line) and line[end_run] == "`":
            end_run += 1
        marker = line[index:end_run]
        closing = line.find(marker, end_run)
        if closing == -1:
            result.append(marker)
            index = end_run
            continue
        result.append(" " * (closing + len(marker) - index))
        index = closing + len(marker)
    return "".join(result)


def _strip_markdown_code(text: str) -> str:
    clean: list[str] = []
    fence_char: str | None = None
    fence_length = 0
    for line in text.splitlines():
        match = FENCE.match(line)
        if fence_char is not None:
            if (
                match is not None
                and match.group(1)[0] == fence_char
                and len(match.group(1)) >= fence_length
                and not match.group(2).strip()
            ):
                fence_char = None
                fence_length = 0
            clean.append("")
            continue
        if match is not None:
            fence_char = match.group(1)[0]
            fence_length = len(match.group(1))
            clean.append("")
            continue
        if line.startswith(("    ", "\t")):
            clean.append("")
            continue
        clean.append(_strip_inline_code(line))
    return "\n".join(clean)


def _is_markdown_document(path: str) -> bool:
    return pathlib.PurePosixPath(path).suffix.casefold() in MARKDOWN_EXTENSIONS


def _platform_markdown(root: pathlib.Path) -> Iterable[tuple[pathlib.Path, str]]:
    platform = root / "docs/platform"
    if _artifact_kind(root, "docs/platform") != "directory":
        return
    for path in sorted(platform.rglob("*.md")):
        try:
            relative = path.relative_to(root).as_posix()
        except ValueError:
            continue
        if _artifact_kind(root, relative) != "regular":
            continue
        try:
            yield path, path.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            continue


def _normalize_commonmark_text(value: str) -> str:
    decoded = html.unescape(value)
    return COMMONMARK_BACKSLASH_ESCAPE.sub(r"\1", decoded)


def _normalize_reference_label(value: str) -> str:
    return " ".join(_normalize_commonmark_text(value).split()).casefold()


def _commonmark_escape_at(text: str, index: int) -> bool:
    return (
        text[index] == "\\"
        and index + 1 < len(text)
        and text[index + 1] in string.punctuation
    )


def _find_markdown_closer(text: str, start: int, opening: str, closing: str) -> int:
    depth = 1
    index = start
    while index < len(text):
        if _commonmark_escape_at(text, index):
            index += 2
            continue
        if text[index] == opening:
            depth += 1
        elif text[index] == closing:
            depth -= 1
            if depth == 0:
                return index
        index += 1
    return -1


def _inline_destination(value: str) -> str | None:
    content = value.strip()
    if not content:
        return None
    if content.startswith("<"):
        index = 1
        while index < len(content):
            if _commonmark_escape_at(content, index):
                index += 2
                continue
            if content[index] == ">":
                return content[1:index] if index > 1 else None
            index += 1
        return None
    depth = 0
    result: list[str] = []
    index = 0
    while index < len(content):
        char = content[index]
        if _commonmark_escape_at(content, index):
            result.extend(content[index : index + 2])
            index += 2
            continue
        if char == "(":
            depth += 1
        elif char == ")" and depth:
            depth -= 1
        elif char.isspace() and depth == 0:
            break
        result.append(char)
        index += 1
    return "".join(result) or None


class _HTMLLinks(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.targets: list[str] = []

    def handle_starttag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        for key, value in attrs:
            if key.casefold() == "href" and value:
                self.targets.append(value)


def _trim_rendered_url(value: str) -> str:
    trimmed = value.rstrip(".,;:!?")
    for opening, closing in (("(", ")"), ("[", "]"), ("{", "}")):
        while trimmed.endswith(closing) and trimmed.count(closing) > trimmed.count(
            opening
        ):
            trimmed = trimmed[:-1]
    return trimmed


def _markdown_links(text: str, *, include_rendered: bool = True) -> list[str]:
    clean = _strip_markdown_code(text)
    definitions: dict[str, str] = {}
    body_lines: list[str] = []
    for line in clean.splitlines():
        match = REFERENCE_DEFINITION.match(line)
        if match is None:
            body_lines.append(line)
            continue
        definitions.setdefault(
            _normalize_reference_label(match.group(1)),
            match.group(2) or match.group(3),
        )
        body_lines.append("")
    body = "\n".join(body_lines)
    targets: list[str] = []
    index = 0
    while index < len(body):
        if body[index] != "[" or (index > 0 and body[index - 1] == "\\"):
            index += 1
            continue
        label_end = _find_markdown_closer(body, index + 1, "[", "]")
        if label_end == -1:
            index += 1
            continue
        label = body[index + 1 : label_end]
        cursor = label_end + 1
        while cursor < len(body) and body[cursor] in " \t\n":
            cursor += 1
        if cursor < len(body) and body[cursor] == "(":
            destination_end = _find_markdown_closer(body, cursor + 1, "(", ")")
            if destination_end != -1:
                destination = _inline_destination(body[cursor + 1 : destination_end])
                if destination is not None:
                    targets.append(destination)
                index = destination_end + 1
                continue
        if cursor < len(body) and body[cursor] == "[":
            reference_end = _find_markdown_closer(body, cursor + 1, "[", "]")
            if reference_end != -1:
                reference = body[cursor + 1 : reference_end] or label
                target = definitions.get(_normalize_reference_label(reference))
                if target is not None:
                    targets.append(target)
                index = reference_end + 1
                continue
        shortcut = definitions.get(_normalize_reference_label(label))
        if shortcut is not None:
            targets.append(shortcut)
        index = label_end + 1

    html_links = _HTMLLinks()
    try:
        html_links.feed(body)
    except (ValueError, RecursionError):
        pass
    targets.extend(html_links.targets)
    if include_rendered:
        targets.extend(
            target
            for match in RENDERED_URL.finditer(body)
            if (target := _trim_rendered_url(match.group(0)))
        )
    return list(
        dict.fromkeys(_normalize_commonmark_text(target) for target in targets)
    )


def _eebus_link_target(
    target: str, docs_eebus_ref: str
) -> tuple[str | None, bool]:
    decoded = _normalize_commonmark_text(urllib.parse.unquote(target))
    parsed = urllib.parse.urlsplit(decoded)
    hostname = (parsed.hostname or "").casefold()
    if hostname in {"github.com", "www.github.com"}:
        parts = parsed.path.strip("/").split("/")
        folded = [part.casefold() for part in parts]
        if len(parts) >= 6 and folded[:3] == [
            "project-helianthus",
            "helianthus-docs-eebus",
            "blob",
        ]:
            ref = parts[3]
            relative = "/".join(parts[4:])
            valid = (
                IMMUTABLE_REF.fullmatch(ref) is not None
                and ref.casefold() == docs_eebus_ref.casefold()
                and _portable_path(relative)
            )
            return relative, valid
        if "helianthus-docs-eebus" in folded:
            return "", False
    if hostname == "raw.githubusercontent.com":
        parts = parsed.path.strip("/").split("/")
        folded = [part.casefold() for part in parts]
        if len(parts) >= 4 and folded[:2] == [
            "project-helianthus",
            "helianthus-docs-eebus",
        ]:
            ref = parts[2]
            relative = "/".join(parts[3:])
            valid = (
                IMMUTABLE_REF.fullmatch(ref) is not None
                and ref.casefold() == docs_eebus_ref.casefold()
                and _portable_path(relative)
            )
            return relative, valid
    repository = "helianthus-docs-eebus/"
    repository_index = decoded.casefold().find(repository)
    if repository_index >= 0 and (
        repository_index == 0 or decoded[repository_index - 1] == "/"
    ):
        relative = decoded[repository_index + len(repository) :].split("#", 1)[0]
        return relative, False
    return None, True


def _link_categories(
    docs_root: pathlib.Path,
    docs_eebus_root: pathlib.Path,
    docs_eebus_ref: str,
    manifest: dict[str, Any],
) -> set[str]:
    active_targets = {
        entry["owner"]["path"]
        for entry in manifest["entries"]
        if entry["owner"]["repository"] == "helianthus-docs-eebus"
        and entry["state"] == "active"
    }
    for relative_path, text in _platform_markdown(docs_root):
        for target in _markdown_links(text):
            relative, immutable = _eebus_link_target(target, docs_eebus_ref)
            if relative is None:
                continue
            if (
                not immutable
                or relative not in active_targets
                or _artifact_kind(docs_eebus_root, relative) != "regular"
            ):
                return {"link.forward"}
    return set()


def _semantic_sections(text: str) -> list[tuple[str, str, bool]]:
    headings: dict[int, str] = {}
    sections: list[tuple[str, str, bool]] = []
    paragraph: list[str] = []
    non_normative_lead = False

    def flush() -> None:
        nonlocal non_normative_lead
        compact = " ".join(" ".join(paragraph).split())
        quoted = bool(paragraph) and all(
            line.lstrip().startswith(">") for line in paragraph
        )
        paragraph.clear()
        if not compact:
            return
        heading_context = " ".join(headings[level] for level in sorted(headings))
        explicitly_non_normative = (
            NON_NORMATIVE.search(compact) is not None
            or any(NON_NORMATIVE.search(heading) for heading in headings.values())
            or non_normative_lead
            or quoted
        )
        sections.append((heading_context, compact, explicitly_non_normative))
        non_normative_lead = NON_NORMATIVE_LEAD.search(compact) is not None

    lines = text.splitlines()
    index = 0
    while index < len(lines):
        line = lines[index]
        atx = ATX_HEADING.match(line)
        setext = (
            SETEXT_HEADING.match(lines[index + 1])
            if line.strip() and index + 1 < len(lines)
            else None
        )
        if atx is not None or setext is not None:
            flush()
            non_normative_lead = False
            if atx is not None:
                level = len(atx.group(1))
                heading = atx.group(2).strip()
            else:
                assert setext is not None
                level = 1 if setext.group(1).startswith("=") else 2
                heading = line.strip()
                index += 1
            headings = {
                current_level: current_heading
                for current_level, current_heading in headings.items()
                if current_level < level
            }
            headings[level] = heading
        elif not line.strip():
            flush()
        else:
            paragraph.append(line)
        index += 1
    flush()
    return sections


def _documentation_ownership_summary(paragraph: str) -> bool:
    return DOCUMENTATION_OWNERSHIP.search(paragraph) is not None


def _without_documentation_ownership_spans(paragraph: str) -> str:
    redacted = list(paragraph)
    for match in DOCUMENTATION_OWNERSHIP.finditer(paragraph):
        redacted[match.start() : match.end()] = " " * (match.end() - match.start())
    return "".join(redacted)


def _observation_subject(value: str) -> bool:
    return (
        bool(value.strip())
        and ANY_MODAL.search(value) is None
        and re.search(r"[,;:]", value) is None
        and OBSERVATION_SUBJECT.fullmatch(value) is not None
    )


def _platform_governance_summary(heading_context: str, paragraph: str) -> bool:
    governance = bool(
        PLATFORM_GOVERNANCE_CONTEXT.search(heading_context)
        and PLATFORM_GOVERNANCE_PROSE.search(paragraph)
        and PLATFORM_GOVERNANCE_ACTION.search(paragraph)
    )
    if not governance:
        return False
    behavior_patterns = (
        PROTOCOL_BEHAVIOR,
        ARCHITECTURE_BEHAVIOR,
        API_BEHAVIOR,
    )
    if not any(
        pattern.search(paragraph) for pattern in behavior_patterns
    ) or NEGATIVE_GOVERNANCE_CLAIM.search(paragraph):
        return True

    observation = GOVERNANCE_COMPLEMENT.search(paragraph)
    if observation is None:
        return False
    if any(
        pattern.search(paragraph, 0, observation.end())
        for pattern in behavior_patterns
    ):
        return False

    complement = paragraph[observation.end() :]
    first_behavior = min(
        (
            match
            for pattern in behavior_patterns
            if (match := pattern.search(complement)) is not None
        ),
        key=lambda match: match.start(),
        default=None,
    )
    if first_behavior is None or ANY_MODAL.search(complement):
        return False
    return _observation_subject(complement[: first_behavior.start()])


def _predicate_units(clause: str) -> list[tuple[str, bool]]:
    """Return predicate-local text and whether a leading modal is inherited."""

    comma_parts: list[str] = []
    start = 0
    for boundary in COMMA_BOUNDARY.finditer(clause):
        tail = clause[boundary.end() :]
        candidate = tail.split(",", 1)[0].strip()
        behavior = (
            PROTOCOL_BEHAVIOR.search(candidate)
            or ARCHITECTURE_BEHAVIOR.search(candidate)
            or API_BEHAVIOR.search(candidate)
        )
        starts_predicate = bool(
            re.match(r"(?:which|that|who)\b", candidate, re.I)
            or NORMATIVE.search(candidate)
            or (
                behavior is not None
                and ("," not in tail or candidate[behavior.end() :].strip())
            )
        )
        if starts_predicate:
            comma_parts.append(clause[start : boundary.start()])
            start = boundary.end()
    comma_parts.append(clause[start:])

    units: list[tuple[str, bool]] = []
    normative_scope = False
    for comma_part in comma_parts:
        for raw_part in PREDICATE_BOUNDARY.split(comma_part):
            part = raw_part.strip()
            if not part:
                continue
            explicit_normative = NORMATIVE.search(part) is not None
            explicit_modal = ANY_MODAL.search(part) is not None
            units.append((part, normative_scope and not explicit_modal))
            if explicit_modal or explicit_normative:
                normative_scope = explicit_normative
    return units


def _prohibited_clause_categories(
    heading_context: str,
    predicate: str,
    *,
    clause_context: str | None = None,
    inherited_normative: bool = False,
) -> set[str]:
    if not inherited_normative and NORMATIVE.search(predicate) is None:
        return set()
    contextual = " ".join(
        part for part in (heading_context, clause_context or predicate) if part
    )
    categories: set[str] = set()
    if PROTOCOL_CONTEXT.search(contextual) and PROTOCOL_BEHAVIOR.search(predicate):
        categories.add("ownership.protocol-copy")
    if ARCHITECTURE_CONTEXT.search(
        contextual
    ) and ARCHITECTURE_BEHAVIOR.search(predicate):
        categories.add("ownership.architecture-copy")
    if API_CONTEXT.search(contextual) and API_BEHAVIOR.search(predicate):
        categories.add("ownership.api-copy")
    return categories


def _semantic_copy_categories(text: str, *, markdown: bool = True) -> set[str]:
    categories: set[str] = set()
    clean = _strip_markdown_code(text) if markdown else text
    for heading_context, paragraph, explicitly_non_normative in _semantic_sections(
        clean
    ):
        contextual = " ".join(part for part in (heading_context, paragraph) if part)
        if GO_DECLARATION.search(paragraph) and re.search(
            r"\b(?:eebus|SHIP|SPINE)\b", contextual, re.I
        ) and not explicitly_non_normative:
            categories.add("ownership.api-copy")
        for clause in CLAUSE_BOUNDARY.split(paragraph):
            for predicate, inherited_normative in _predicate_units(clause):
                inspected = _without_documentation_ownership_spans(predicate)
                prohibited = _prohibited_clause_categories(
                    heading_context,
                    inspected,
                    clause_context=clause,
                    inherited_normative=(
                        inherited_normative or NORMATIVE.search(predicate) is not None
                    ),
                )
                if not prohibited:
                    continue
                if (
                    explicitly_non_normative
                    or _platform_governance_summary(heading_context, inspected)
                ):
                    continue
                categories.update(prohibited)
    return categories


def _ownership_copy_categories(docs_root: pathlib.Path) -> set[str]:
    categories: set[str] = set()
    for _, text in _platform_markdown(docs_root):
        categories.update(_semantic_copy_categories(text))
    return categories


def _documentation_like(name: str) -> bool:
    return (
        pathlib.PurePosixPath(name).suffix.casefold() in DOCUMENTATION_EXTENSIONS
        or DOCUMENTATION_NAMES.fullmatch(name) is not None
    )


def _code_repository_documents(
    root: pathlib.Path,
) -> Iterable[tuple[str, str]]:
    for current, directory_names, file_names in os.walk(
        root, topdown=True, followlinks=False
    ):
        current_path = pathlib.Path(current)
        directory_names[:] = [
            name
            for name in sorted(directory_names)
            if name.casefold() not in NONPUBLISHABLE_DIRECTORIES
            and not (current_path / name).is_symlink()
        ]
        for name in sorted(file_names):
            if not _documentation_like(name):
                continue
            path = current_path / name
            try:
                relative = path.relative_to(root).as_posix()
            except ValueError:
                continue
            raw = _read_regular_artifact(root, relative)
            if raw is None or b"\x00" in raw:
                continue
            try:
                text = raw.decode("utf-8")
            except UnicodeError:
                continue
            yield relative, text


def _code_repo_categories(
    manifest: dict[str, Any],
    roots: Mapping[str, pathlib.Path],
    enforce_through: str,
) -> set[str]:
    if MILESTONE_INDEX[enforce_through] < MILESTONE_INDEX["MSP-DOCS-CLEAN"]:
        return set()
    categories: set[str] = set()
    for entry in manifest["entries"]:
        if entry["surface"] == "code_repo":
            checked: set[tuple[str, str]] = set()
            for location in (entry["owner"], entry["source"]):
                identity = (location["repository"], location["path"])
                if identity in checked:
                    continue
                checked.add(identity)
                location_root = roots.get(location["repository"])
                if location_root is not None and _artifact_kind(
                    location_root, location["path"]
                ) != "missing":
                    categories.add("ownership.code-repo-substantive")
        if entry["surface"] != "summary_only" or entry["state"] != "active":
            continue
        owner_root = roots.get(entry["owner"]["repository"])
        if owner_root is None:
            continue
        raw = _read_regular_artifact(owner_root, entry["owner"]["path"])
        if raw is None:
            continue
        try:
            text = raw.decode("utf-8")
        except UnicodeError:
            categories.add("ownership.summary-only-substantive")
            continue
        markdown = _is_markdown_document(entry["owner"]["path"])
        prose = _strip_markdown_code(text) if markdown else text
        nonblank_lines = [line for line in text.splitlines() if line.strip()]
        if (
            NORMATIVE.search(prose)
            or len(nonblank_lines) > 12
            or re.search(r"(?m)^##\s+", prose)
            or _semantic_copy_categories(prose, markdown=False)
        ):
            categories.add("ownership.summary-only-substantive")
    code_root = roots.get("helianthus-eebusreg")
    summary_paths = {
        entry["owner"]["path"]
        for entry in manifest["entries"]
        if entry["surface"] == "summary_only" and entry["state"] == "active"
    }
    if code_root is not None:
        for relative, text in _code_repository_documents(code_root):
            if relative in summary_paths:
                continue
            contextual = f"# eeBUS code repository {relative}\n\n{text}"
            if _semantic_copy_categories(
                contextual, markdown=_is_markdown_document(relative)
            ):
                categories.add("ownership.code-repo-substantive")
    return categories


def _privacy_categories(root: pathlib.Path) -> set[str]:
    for _, text in _platform_markdown(root):
        if PRIVATE_IDENTIFIER.search(text) or _contains_private_network(text):
            return {"privacy.private-identifier"}
    return set()


def _m625_heading_structure(text: str) -> tuple[str | None, list[str]]:
    title: str | None = None
    headings: list[str] = []
    for line in text.splitlines():
        match = ATX_HEADING.match(line)
        if match is None:
            continue
        level = len(match.group(1))
        heading = match.group(2).strip()
        if level == 1 and title is None:
            title = heading
        elif level == 2:
            headings.append(heading)
        else:
            return title, [*headings, "__invalid_heading_level__"]
    return title, headings


def _m625_structure_categories(text: str) -> set[str]:
    title, headings = _m625_heading_structure(text)
    if (
        title != M625_PAGE_TITLE
        or headings != list(M625_REQUIRED_HEADINGS)
        or any(FENCE.match(line) for line in text.splitlines())
    ):
        return {"m625.cross-seed-contract"}

    sections = _semantic_sections(text)
    paragraphs_by_heading: dict[str, list[str]] = {
        heading: [] for heading in M625_REQUIRED_HEADINGS
    }
    for heading_context, paragraph, _ in sections:
        matches = [
            heading
            for heading in M625_REQUIRED_HEADINGS
            if heading_context.endswith(heading)
        ]
        if not matches:
            continue
        paragraphs_by_heading[matches[-1]].append(paragraph)
    for heading, clauses in M625_REQUIRED_CLAUSES.items():
        joined = "\n".join(paragraphs_by_heading[heading])
        if (
            len(paragraphs_by_heading[heading])
            != M625_SECTION_PARAGRAPH_COUNTS[heading]
            or any(clause not in joined for clause in clauses)
        ):
            return {"m625.cross-seed-contract"}
    compact_text = " ".join(text.split())
    if any(
        " ".join(clause.split()) not in compact_text
        for clause in M625_REQUIRED_DOCUMENT_CLAUSES
    ):
        return {"m625.cross-seed-contract"}

    source_links = set(_markdown_links(text, include_rendered=False))
    expected_links = {
        M625_PLAN_URL,
        M625_PROVENANCE_URL,
        M625_ARCHITECTURE_URL,
    }
    if source_links != expected_links:
        return {"m625.cross-seed-contract"}
    return set()


def _m625_positive_assertion_categories(text: str) -> set[str]:
    categories: set[str] = set()
    for _, paragraph, _ in _semantic_sections(text):
        for sentence in CLAUSE_BOUNDARY.split(paragraph):
            normalized = re.sub(r"(?<=[a-z])(?=[A-Z])", " ", sentence)
            words = {
                word.casefold()
                for word in re.findall(r"[A-Za-z][A-Za-z0-9]*", normalized)
            }
            if not words or M625_NEGATIVE_ASSERTION.search(sentence):
                continue
            action_words = {
                word[:-1] if word.endswith("s") else word for word in words
            }
            if (
                words & M625_PROTOCOL_OR_API_TERMS
                and action_words & M625_PROTOCOL_OR_API_ACTIONS
            ):
                categories.add("m625.cross-seed-protocol-api-declaration")
            if words & M625_LIVE_TERMS and action_words & M625_LIVE_ACTIONS:
                categories.add("m625.cross-seed-live-claim")
            if words & M625_VENDOR_TERMS and words & M625_EVIDENCE_TERMS:
                categories.add("m625.cross-seed-private-source-attribution")
            if words & M625_SECRET_TERMS and (
                action_words & M625_SECRET_OUTPUT_ACTIONS
                or words & M625_SECRET_SUBSTITUTES
            ):
                categories.add("m625.cross-seed-secret-policy")
    return categories


def _m625_cross_seed_text_categories(text: str) -> set[str]:
    categories = _m625_structure_categories(text)
    categories.update(_m625_positive_assertion_categories(text))
    if M625_RESTRICTED_MATERIAL.search(text) or _contains_private_network(text):
        categories.add("m625.cross-seed-restricted-material")
    return categories


def _m625_external_input_categories(
    root: pathlib.Path, source_roots: Mapping[str, pathlib.Path] | None = None
) -> set[str]:
    if _artifact_kind(root, M625_INPUTS_PATH.as_posix()) != "regular":
        return {"m625.cross-seed-input-binding"}
    try:
        binding = yaml.safe_load(
            (root / M625_INPUTS_PATH).read_text(encoding="utf-8")
        )
    except (OSError, UnicodeError, yaml.YAMLError):
        return {"m625.cross-seed-input-binding"}
    expected = {
        "schema": "helianthus.platform.external-inputs",
        "version": 1,
        "owner": "Project-Helianthus/helianthus-docs-ebus#380",
        "sources": list(M625_EXTERNAL_INPUTS),
    }
    if binding != expected:
        return {"m625.cross-seed-input-binding"}
    # Unit-level page checks can omit external roots; all repository and
    # combined-ref entry points pass an explicit mapping, including an empty
    # mapping, so a real gate fails closed on an unavailable source root.
    if source_roots is None:
        return set()
    roots = source_roots
    for source in M625_EXTERNAL_INPUTS:
        source_root = roots.get(source["repository"])
        if source_root is None or not _repository_root_valid(
            source_root, source["repository"]
        ):
            return {"m625.cross-seed-input-source"}
        source_ref = source["ref"]
        if not _checkout_matches_ref(source_root, source_ref):
            return {"m625.cross-seed-input-source"}
        shown = _run_git_bytes(
            source_root, "show", f"{source_ref}:{source['path']}"
        )
        if shown.returncode != 0:
            return {"m625.cross-seed-input-source"}
        if hashlib.sha256(shown.stdout).hexdigest() != source["content_sha256"]:
            return {"m625.cross-seed-input-content"}
    return set()


def _m625_cross_seed_categories(
    root: pathlib.Path,
    manifest: Mapping[str, Any],
    source_roots: Mapping[str, pathlib.Path] | None = None,
) -> set[str]:
    entries = [
        entry for entry in manifest["entries"] if entry["id"] == M625_CROSS_SEED_ID
    ]
    if not entries:
        return {"m625.cross-seed-manifest"}
    if len(entries) != 1:
        return {"m625.cross-seed-manifest"}
    entry = entries[0]
    if (
        entry["surface"] != "platform"
        or entry["owner"]
        != {
            "repository": "helianthus-docs-eebus",
            "path": M625_CROSS_SEED_PATH.as_posix(),
        }
        or entry["source"]
        != {
            "repository": "helianthus-docs-eebus",
            "path": M625_CROSS_SEED_PATH.as_posix(),
        }
        or not entry["canonical"]
        or entry["state"] != "active"
        or entry["kind"] != "canonical_document"
        or entry["lifecycle"]["source_issue"]
        != "Project-Helianthus/helianthus-docs-ebus#380"
        or entry["lifecycle"]["source_pr"]
        != "Project-Helianthus/helianthus-docs-ebus#381"
        or entry["lifecycle"]["source_ref"]
        is not None
        or entry["lifecycle"]["content_sha256"]
        is not None
        or entry["enforcement"]
        != {"milestone": "MSP-DOCS-CLEAN", "required_state": "active"}
    ):
        return {"m625.cross-seed-manifest"}
    if _artifact_kind(root, M625_CROSS_SEED_PATH.as_posix()) != "regular":
        return {"m625.cross-seed-artifact"}
    input_categories = _m625_external_input_categories(root, source_roots)
    if input_categories:
        return input_categories
    path = root / M625_CROSS_SEED_PATH
    return _m625_cross_seed_text_categories(path.read_text(encoding="utf-8"))


def _version_tuple(value: str | None) -> tuple[int, int, int] | None:
    if not isinstance(value, str):
        return None
    match = VERSION.fullmatch(value)
    if match is None:
        return None
    return tuple(int(part) for part in match.groups())  # type: ignore[return-value]


def _actual_tool_versions() -> tuple[tuple[int, int, int], str | None, str | None]:
    python = tuple(sys.version_info[:3])
    try:
        distribution = importlib.metadata.version("PyYAML")
    except importlib.metadata.PackageNotFoundError:
        distribution = None
    module = getattr(yaml, "__version__", None)
    return python, distribution, module


def _toolchain_categories(mode: str) -> set[str]:
    if mode not in TOOLCHAIN_MODES:
        return {"toolchain.mode"}
    python, pyyaml_distribution, pyyaml_module = _actual_tool_versions()
    categories: set[str] = set()
    if mode == "exact":
        if python != EXACT_PYTHON:
            categories.add("toolchain.python")
        if (
            pyyaml_distribution != EXACT_PYYAML
            or pyyaml_module != EXACT_PYYAML
        ):
            categories.add("toolchain.pyyaml")
        return categories

    if not (SUPPORTED_PYTHON_MIN <= python < SUPPORTED_PYTHON_MAX):
        categories.add("toolchain.python")
    parsed_pyyaml = _version_tuple(pyyaml_distribution)
    if (
        parsed_pyyaml is None
        or not (SUPPORTED_PYYAML_MIN <= parsed_pyyaml < SUPPORTED_PYYAML_MAX)
        or pyyaml_distribution != pyyaml_module
    ):
        categories.add("toolchain.pyyaml")
    return categories


def _validated_manifest(
    root: pathlib.Path, *, current_manifest_version: int = 2
) -> tuple[dict[str, Any] | None, set[str]]:
    manifest, error = _load_manifest(root)
    if error is not None:
        return None, {error}
    assert manifest is not None
    if not _schema_valid(manifest):
        return None, {"manifest.schema"}
    manifest_categories = _manifest_categories(manifest)
    if manifest_categories:
        return manifest, manifest_categories
    if manifest["version"] < current_manifest_version:
        return None, {"manifest.version-floor"}
    return manifest, set()


def _history_categories(
    manifest: dict[str, Any], prior_manifest_path: pathlib.Path | None
) -> set[str]:
    if prior_manifest_path is None:
        return set()
    prior = _parse_manifest_path(pathlib.Path(prior_manifest_path))
    if prior is None or not _schema_valid(prior):
        return {"history.prior-manifest"}
    prior_errors = _manifest_categories(prior)
    prior_errors.update(_state_categories(prior, {}))
    if prior_errors:
        return {"history.prior-manifest"}

    categories: set[str] = set()
    current_by_id = {entry["id"]: entry for entry in manifest["entries"]}
    current_by_surface: dict[str, list[dict[str, Any]]] = {}
    for entry in manifest["entries"]:
        current_by_surface.setdefault(entry["surface"], []).append(entry)
    for prior_entry in prior["entries"]:
        if prior_entry["state"] != "withdrawn":
            continue
        current_entry = current_by_id.get(prior_entry["id"])
        surface_entries = current_by_surface.get(prior_entry["surface"], [])
        tombstone_is_unique = (
            len(surface_entries) == 1
            and surface_entries[0]["id"] == prior_entry["id"]
        )
        if (
            current_entry is None
            or current_entry["state"] != "withdrawn"
            or not tombstone_is_unique
        ):
            categories.add("history.withdrawn-terminal")
        if (
            current_entry is not None
            and current_entry["state"] == "withdrawn"
            and current_entry["surface"] == prior_entry["surface"]
            and current_entry != prior_entry
        ):
            categories.add("history.tombstone-identity")
    return categories


def validate_repository(
    *,
    docs_root: pathlib.Path,
    docs_repository: str,
    mode: str,
    enforce_through: str,
    toolchain_mode: str,
    prior_manifest: pathlib.Path | None = None,
    evaluated_at: str | None = None,
    evaluation_source: str | None = None,
    m625_docs_eebus_root: pathlib.Path | None = None,
    m625_execution_plans_root: pathlib.Path | None = None,
    owner_manifest_root: pathlib.Path | None = None,
    _current_manifest_version: int = 2,
    _m625_required: bool = True,
) -> list[str]:
    root = pathlib.Path(docs_root)
    categories = _toolchain_categories(toolchain_mode)
    repository_valid = GITHUB_REPOSITORY.fullmatch(docs_repository) is not None
    if not repository_valid:
        categories.add("input.docs-repository")
    root_valid = repository_valid and _repository_root_valid(
        root, docs_repository
    )
    if not root_valid:
        categories.add("input.repository-root")
    manifest_root = (
        pathlib.Path(owner_manifest_root)
        if owner_manifest_root is not None
        else root
    )
    owner_root_valid = owner_manifest_root is None or _repository_root_valid(
        manifest_root, "Project-Helianthus/helianthus-docs-eebus"
    )
    if not owner_root_valid:
        categories.add("input.repository-root")
    manifest, manifest_categories = _validated_manifest(
        manifest_root, current_manifest_version=_current_manifest_version
    )
    categories.update(manifest_categories)
    if manifest is None:
        return _result(categories)
    categories.update(_history_categories(manifest, prior_manifest))
    categories.update(_enforcement_categories(manifest, enforce_through))
    roots = {"helianthus-docs": root} if root_valid else {}
    if owner_manifest_root is not None and owner_root_valid:
        roots["helianthus-docs-eebus"] = manifest_root
    categories.update(_state_categories(manifest, roots))
    categories.update(_artifact_categories(manifest, roots))
    categories.update(_ownership_copy_categories(root))
    categories.update(_privacy_categories(root))
    if _m625_required and enforce_through == M625_REQUIRED_DELIVERABLE["milestone"]:
        categories.update(
            _m625_cross_seed_categories(
                manifest_root,
                manifest,
                {
                    "Project-Helianthus/helianthus-docs-eebus": m625_docs_eebus_root,
                    "Project-Helianthus/helianthus-execution-plans": m625_execution_plans_root,
                }
                if m625_docs_eebus_root is not None
                and m625_execution_plans_root is not None
                else {},
            )
        )
    if mode == "main-expiry":
        categories.update(_expiry_categories(manifest, evaluated_at, evaluation_source))
    elif mode != "repository":
        categories.add("input.mode")
    return _result(categories)


def validate_workspace(
    *,
    docs_root: pathlib.Path,
    docs_eebus_root: pathlib.Path,
    eebusreg_root: pathlib.Path,
    mode: str,
    docs_ref: str | None,
    docs_eebus_ref: str | None,
    eebusreg_ref: str | None,
    docs_repository: str,
    enforce_through: str,
    toolchain_mode: str,
    prior_manifest: pathlib.Path | None = None,
    m625_docs_eebus_root: pathlib.Path | None = None,
    m625_execution_plans_root: pathlib.Path | None = None,
    owner_manifest_root: pathlib.Path | None = None,
    _current_manifest_version: int = 2,
    _m625_required: bool = True,
) -> list[str]:
    roots = {
        "helianthus-docs": pathlib.Path(docs_root),
        "helianthus-docs-eebus": pathlib.Path(docs_eebus_root),
        "helianthus-eebusreg": pathlib.Path(eebusreg_root),
    }
    refs = {
        "helianthus-docs": docs_ref,
        "helianthus-docs-eebus": docs_eebus_ref,
        "helianthus-eebusreg": eebusreg_ref,
    }
    ref_categories = {
        "helianthus-docs": "input.docs-ref",
        "helianthus-docs-eebus": "input.docs-eebus-ref",
        "helianthus-eebusreg": "input.eebusreg-ref",
    }
    categories = _toolchain_categories(toolchain_mode)
    if mode != "combined-ref":
        categories.add("input.mode")
    for repository, root in roots.items():
        if not _checkout_matches_ref(root, refs[repository]):
            categories.add(ref_categories[repository])
    if any(not _clean_checkout(root) for root in roots.values()):
        categories.add("input.clean-clone")

    expected_repositories = {
        "helianthus-docs": docs_repository,
        "helianthus-docs-eebus": "Project-Helianthus/helianthus-docs-eebus",
        "helianthus-eebusreg": "Project-Helianthus/helianthus-eebusreg",
    }
    if GITHUB_REPOSITORY.fullmatch(docs_repository) is None:
        categories.add("input.docs-repository")

    valid_roots: dict[str, pathlib.Path] = {}
    resolved: set[pathlib.Path] = set()
    for repository, root in roots.items():
        if not _repository_root_valid(root, expected_repositories[repository]):
            categories.add("input.repository-root")
            continue
        resolved_root = root.resolve(strict=True)
        if resolved_root in resolved:
            categories.add("input.repository-root")
            continue
        resolved.add(resolved_root)
        valid_roots[repository] = root

    manifest_root = roots["helianthus-docs"]
    if owner_manifest_root is not None:
        manifest_root = pathlib.Path(owner_manifest_root)
        if not _repository_root_valid(
            manifest_root, "Project-Helianthus/helianthus-docs-eebus"
        ):
            categories.add("input.repository-root")
        else:
            resolved_owner = manifest_root.resolve(strict=True)
            existing = valid_roots.get("helianthus-docs-eebus")
            if resolved_owner in resolved:
                if (
                    existing is None
                    or existing.resolve(strict=True) != resolved_owner
                ):
                    categories.add("input.repository-root")
            else:
                resolved.add(resolved_owner)
                valid_roots["helianthus-docs-eebus"] = manifest_root

    manifest, manifest_categories = _validated_manifest(
        manifest_root,
        current_manifest_version=_current_manifest_version,
    )
    categories.update(manifest_categories)
    if manifest is None:
        return _result(categories)
    categories.update(_history_categories(manifest, prior_manifest))
    categories.update(_enforcement_categories(manifest, enforce_through))
    categories.update(_state_categories(manifest, valid_roots, refs))
    categories.update(_artifact_categories(manifest, valid_roots))
    categories.update(_ownership_copy_categories(roots["helianthus-docs"]))
    categories.update(_code_repo_categories(manifest, valid_roots, enforce_through))
    categories.update(_privacy_categories(roots["helianthus-docs"]))
    if _m625_required and enforce_through == M625_REQUIRED_DELIVERABLE["milestone"]:
        categories.update(
            _m625_cross_seed_categories(
                manifest_root,
                manifest,
                {
                    "Project-Helianthus/helianthus-docs-eebus": m625_docs_eebus_root,
                    "Project-Helianthus/helianthus-execution-plans": m625_execution_plans_root,
                }
                if m625_docs_eebus_root is not None
                and m625_execution_plans_root is not None
                else {},
            )
        )
    if (
        "helianthus-docs-eebus" in valid_roots
        and isinstance(docs_eebus_ref, str)
        and IMMUTABLE_REF.fullmatch(docs_eebus_ref) is not None
    ):
        categories.update(
            _link_categories(
                roots["helianthus-docs"],
                roots["helianthus-docs-eebus"],
                docs_eebus_ref,
                manifest,
            )
        )
    return _result(categories)


class _CategoryParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        raise ValueError(message)


def _parser() -> argparse.ArgumentParser:
    parser = _CategoryParser(add_help=True)
    parser.add_argument(
        "--mode",
        default="repository",
        choices=("repository", "combined-ref", "main-expiry"),
    )
    parser.add_argument("--docs-root", type=pathlib.Path, default=pathlib.Path("."))
    parser.add_argument("--docs-eebus-root", type=pathlib.Path)
    parser.add_argument("--eebusreg-root", type=pathlib.Path)
    parser.add_argument("--docs-ref")
    parser.add_argument(
        "--docs-repository",
        default="Project-Helianthus/helianthus-docs",
    )
    parser.add_argument("--docs-eebus-ref")
    parser.add_argument("--eebusreg-ref")
    parser.add_argument("--evaluated-at")
    parser.add_argument("--evaluation-source")
    parser.add_argument("--prior-manifest", type=pathlib.Path)
    parser.add_argument("--m625-docs-eebus-root", type=pathlib.Path)
    parser.add_argument("--m625-execution-plans-root", type=pathlib.Path)
    parser.add_argument("--owner-manifest-root", type=pathlib.Path)
    parser.add_argument("--enforce-through", required=True, choices=MILESTONES)
    parser.add_argument(
        "--toolchain-mode", default="exact", choices=tuple(sorted(TOOLCHAIN_MODES))
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.mode in {"repository", "main-expiry"}:
        diagnostics = validate_repository(
            docs_root=args.docs_root,
            docs_repository=args.docs_repository,
            mode=args.mode,
            enforce_through=args.enforce_through,
            toolchain_mode=args.toolchain_mode,
            prior_manifest=args.prior_manifest,
            evaluated_at=args.evaluated_at,
            evaluation_source=args.evaluation_source,
            m625_docs_eebus_root=args.m625_docs_eebus_root,
            m625_execution_plans_root=args.m625_execution_plans_root,
            owner_manifest_root=args.owner_manifest_root,
        )
    elif args.docs_eebus_root is None or args.eebusreg_root is None:
        diagnostics = ["input.roots"]
    else:
        diagnostics = validate_workspace(
            docs_root=args.docs_root,
            docs_eebus_root=args.docs_eebus_root,
            eebusreg_root=args.eebusreg_root,
            mode=args.mode,
            docs_ref=args.docs_ref,
            docs_eebus_ref=args.docs_eebus_ref,
            eebusreg_ref=args.eebusreg_ref,
            docs_repository=args.docs_repository,
            enforce_through=args.enforce_through,
            toolchain_mode=args.toolchain_mode,
            prior_manifest=args.prior_manifest,
            m625_docs_eebus_root=args.m625_docs_eebus_root,
            m625_execution_plans_root=args.m625_execution_plans_root,
            owner_manifest_root=args.owner_manifest_root,
        )
    for diagnostic in diagnostics:
        print(diagnostic)
    return 1 if diagnostics else 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except BrokenPipeError:
        raise SystemExit(1) from None
    except (
        OSError,
        ValueError,
        yaml.YAMLError,
        RecursionError,
        MemoryError,
        OverflowError,
    ):
        print("input.arguments")
        raise SystemExit(1) from None
