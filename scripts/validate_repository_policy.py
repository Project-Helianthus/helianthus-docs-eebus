#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import html
import json
import os
import posixpath
import re
import stat
import sys
import unicodedata
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path, PurePosixPath
from typing import Any
from urllib.parse import unquote, urlsplit

import yaml
from markdown_it import MarkdownIt

from machine_publication_policy import (
    COMPLETE,
    IPV4_CANDIDATE_PATTERN,
    IPV6_CANDIDATE_PATTERN,
    MALFORMED_SENTINEL,
    NESTING_TOO_DEEP,
    PRIVATE_PATH_PATTERN,
    classify_ipv4,
    classify_ipv6,
    decode_machine_json,
    git_fingerprint_exempt_spans,
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
    "api/_candidate/msp-055/attestation.json",
    "api/_candidate/msp-055/candidate-record.json",
    "api/_candidate/msp-055/helianthus-eebusreg-api-surface-v1-predicate.json",
    "api/_candidate/msp-055/helianthus-eebusreg-api-surface-v1.json",
    "api/_candidate/msp-055/verification.json",
    "api/eebusruntime-v1/attestation.json",
    "api/eebusruntime-v1/manifest.json",
    "api/eebusruntime-v1/predicate.json",
    "api/eebusruntime-v1/publication-record.json",
    "api/eebusruntime-v1/verification.json",
    "api/schema/helianthus.eebus.api-surface.v1.schema.json",
    "api/schema/helianthus.docs.eebus.msp-055-api-freeze.v1.schema.json",
    "api/fixtures/v1/positive/canonical-go-rendering.json",
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
MSP055_RETIRED_MANIFEST_SHA256 = (
    "c93492bd275b5e14d3c9e05da701730d" "6d34a197e0653e6b169d103418bfcc8c"
)
MSP055_MANIFEST_SHA256 = (
    "bbabab51cc0a0e833c645f51767e67a3" "4c0361ba61c45b0065ecfda55ed6c32f"
)
MSP055_CANDIDATE_PREDICATE_SHA256 = (
    "5960ac6dc00942ea7a19d2559934b382" "ac700ae445b492abb8d223a6f14b72e4"
)
MSP055_CANDIDATE_ATTESTATION_SHA256 = (
    "2419bb9ab2187c19642f80f01d1e776b" "6b52df8cdf182e41ac9329e916ebdfc9"
)
MSP055_CANDIDATE_VERIFICATION_SHA256 = (
    "a1de3f1ff4163871dcb416348723b104" "afab4edfe3f0d4e1fe0a3f0fef58cbf0"
)
MSP055_ACTIVE_PREDICATE_SHA256 = (
    "e84acd2d7ccc63c3a150e9f53d61480d" "967bf03f5ac827f7a692f14e9ebe534e"
)
MSP055_ACTIVE_ATTESTATION_SHA256 = (
    "9b67ab54ef0b9637abdb9450e2a4b94e" "e56c040883b0d1ee98899d4a02d9142f"
)
MSP055_ACTIVE_VERIFICATION_SHA256 = (
    "485c7976f7de52a35c55ad590bc3fdfac" "97420f72bb7a6d7fc80afd418798c87"
)
MSP055_SOURCE_COMMIT = "7a5852e009bbdcba47f0" "a34ba866070a4ab35ef8"
MSP055_SOURCE_PR_HEAD = "6af4cdcedb5f7f93d01a" "53c48c6abc0c19f92edb"
MSP055_WORKFLOW_COMMIT = MSP055_SOURCE_COMMIT
MSP055_RETIRED_SOURCE_COMMIT = "59cbea0593f27caf558b" "c4cc9b665c52fc50b683"
MSP055_CANDIDATE_SOURCE = "ad79f0bbe589d95d56cc" "738203604fec78639d90"
MSP055_SOURCE_TREE = "b090651c99d5b6817a40" "997b14c1b6a2a37c124e"
MSP055_RETIRED_SOURCE_TREE = "01c17785fe9aac8d8536" "545e03e1ec1d4a4dff9d"
MSP055_CANDIDATE_DOCS_MERGE = "df231977989625fae8a9" "2d94b3ca88ef9e52c6f2"
MSP055_CANDIDATE_DIGESTS = {
    MSP055_RETIRED_MANIFEST_SHA256,
    MSP055_CANDIDATE_PREDICATE_SHA256,
    MSP055_CANDIDATE_ATTESTATION_SHA256,
    MSP055_CANDIDATE_VERIFICATION_SHA256,
}
MSP055_ACTIVE_DIGESTS = {
    MSP055_MANIFEST_SHA256,
    MSP055_ACTIVE_PREDICATE_SHA256,
    MSP055_ACTIVE_ATTESTATION_SHA256,
    MSP055_ACTIVE_VERIFICATION_SHA256,
}
MSP055_PROVENANCE_MACHINE_FINGERPRINTS = {
    "api/_candidate/msp-055/candidate-record.json": {
        MSP055_RETIRED_SOURCE_COMMIT,
        MSP055_CANDIDATE_SOURCE,
        *MSP055_CANDIDATE_DIGESTS,
    },
    "api/_candidate/msp-055/helianthus-eebusreg-api-surface-v1-predicate.json": {
        MSP055_CANDIDATE_SOURCE,
        MSP055_RETIRED_MANIFEST_SHA256,
    },
    "api/_candidate/msp-055/verification.json": {
        MSP055_CANDIDATE_SOURCE,
        MSP055_RETIRED_MANIFEST_SHA256,
    },
    "api/eebusruntime-v1/predicate.json": {
        MSP055_SOURCE_COMMIT,
        MSP055_MANIFEST_SHA256,
    },
    "api/eebusruntime-v1/publication-record.json": {
        MSP055_RETIRED_SOURCE_TREE,
        MSP055_SOURCE_TREE,
        MSP055_SOURCE_COMMIT,
        MSP055_WORKFLOW_COMMIT,
        MSP055_CANDIDATE_SOURCE,
        MSP055_CANDIDATE_DOCS_MERGE,
        *MSP055_CANDIDATE_DIGESTS,
        *MSP055_ACTIVE_DIGESTS,
    },
    "api/eebusruntime-v1/verification.json": {
        MSP055_SOURCE_COMMIT,
        MSP055_WORKFLOW_COMMIT,
        MSP055_MANIFEST_SHA256,
    },
    "api/schema/helianthus.docs.eebus.msp-055-api-freeze.v1.schema.json": {
        MSP055_RETIRED_SOURCE_TREE,
        MSP055_SOURCE_TREE,
        MSP055_SOURCE_COMMIT,
        MSP055_WORKFLOW_COMMIT,
        MSP055_CANDIDATE_SOURCE,
        MSP055_CANDIDATE_DOCS_MERGE,
    },
}
MSP055_PROVENANCE_IDENTIFIER_ARTIFACTS = set(
    MSP055_PROVENANCE_MACHINE_FINGERPRINTS
)
MSP055_PROVENANCE_TEXT_FINGERPRINTS = {
    ".github/workflows/docs-ci.yml": {
        MSP055_SOURCE_COMMIT,
    },
    "api/_candidate/msp-05p-eebusruntime-v1-correction.md": {
        MSP055_SOURCE_COMMIT,
        MSP055_SOURCE_TREE,
        MSP055_MANIFEST_SHA256,
    },
    "api/eebusruntime-v1/reference.md": {
        MSP055_SOURCE_COMMIT,
        MSP055_SOURCE_TREE,
    },
    "scripts/validate_msp_055_api_freeze.py": {
        MSP055_RETIRED_SOURCE_TREE,
        MSP055_RETIRED_SOURCE_COMMIT,
        MSP055_SOURCE_TREE,
        MSP055_SOURCE_COMMIT,
        MSP055_SOURCE_PR_HEAD,
        MSP055_WORKFLOW_COMMIT,
        MSP055_RETIRED_MANIFEST_SHA256,
        MSP055_MANIFEST_SHA256,
        MSP055_CANDIDATE_PREDICATE_SHA256,
        MSP055_CANDIDATE_ATTESTATION_SHA256,
        MSP055_CANDIDATE_VERIFICATION_SHA256,
        MSP055_ACTIVE_PREDICATE_SHA256,
        MSP055_ACTIVE_ATTESTATION_SHA256,
        MSP055_ACTIVE_VERIFICATION_SHA256,
        "dc6085b0c3ab3f2182d3609db042663d7f73439c85c2f4f9dc51c33b02c57762",
    },
    "tests/test_msp_055_api_freeze.py": {
        MSP055_RETIRED_SOURCE_TREE,
        MSP055_RETIRED_SOURCE_COMMIT,
        MSP055_WORKFLOW_COMMIT,
        MSP055_SOURCE_PR_HEAD,
        "dc6085b0c3ab3f2182d3609db042663d7f73439c85c2f4f9dc51c33b02c57762",
    },
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
    "api/README.md": "ownership-landing",
    "api/api-surface-v1.md": "api-contract",
    "devices/vr940f.md": "planned-target",
    "evidence/README.md": "evidence-policy",
    "evidence/evidence-template.md": "template",
    "re-notes/template.md": "template",
    "development/contributing.md": "contribution-policy",
}

SCAFFOLD_ARTIFACT_SHA256 = {
    "README.md": "2cbdf09619d7bdee2c6cc9c11495da1" "5a04a1888309ea5df487c70c1a5c1eeba",
    "api/README.md": "5e26fbec849b10143efb2e12001d9b01" "09bb9a119a2f723399322adf1917c454",
    "api/api-surface-v1.md": "acb007a5a2366b63ed4a64fecfee5cad" "2109fcbd779c87c0281a37b9f44cbeca",
    "devices/vr940f.md": "6eea7a357ebddb66073ad4647d87234c" "94bbbf58050685c49d3db5d9a286d211",
    "evidence/README.md": "4afae6e8ab7848ded9068f43523794ee" "ccf8f325f91659557a453646a00423ff",
    "evidence/evidence-template.md": (
        "02910e849eab14a43251f4d28f4cb1e" "115c0feb6f78a32b2b600c85830c150e5"
    ),
    "re-notes/template.md": "eaedfc96d49a573455f43df8f1542e0f" "d8724ef3770dcb9d0aac485ef23f8f32",
    "development/contributing.md": (
        "f52c046edb8bafeca43cdb1e9159e493" "55688ce7b114339bfe34cf02a1038586"
    ),
}

PRODUCTION_REVIEWED_PROTOCOL_ARTIFACT_SHA256 = {
    "protocols/ship-spine-overview.md": (
        "8e238089d340fd39e3064c62293caebe" "3c551789971c18eab87de5c7fcc4bfda"
    ),
}

EVIDENCE_SOURCE_CLASSES = {
    "observed_runtime",
    "derived_inference",
    "vendor_public",
    "app_observation",
}
HYPOTHESIS_STATUSES = {"draft", "publishable", "blocked", "withdrawn"}
EVIDENCE_ID_PATTERN = re.compile(r"EV-\d{8}-\d{3}")
CI_LOCAL_SHA256 = "b802f3ec2ea3dbf462cc7d1cf35e98a" "95ad1e08de5d6848b065f4cecadcffe02"
LICENSE_SHA256 = "aac2f93638f50b4347d37aeb656cab3" "1f447e0c0bc89f53ee144a81907a943ea"
LOCKED_REQUIREMENTS = (
    "PyYAML==6.0.3 \\\n"
    "    --hash=sha256:41715c910c881bc081f1e8872880d3c650acf13dfa8214bad49ed4cede7c34ea \\\n"
    "    --hash=sha256:5fcd34e47f6e0b794d17de1b4ff496c00986e1c83f7ab2fb8fcfe9616ff7477b \\\n"
    "    --hash=sha256:5fdec68f91a0c6739b380c83b951e2c72ac0197ace422360e6d5a959d8d97b2c \\\n"
    "    --hash=sha256:64386e5e707d03a7e172c0701abfb7e10f0fb753ee1d773128192742712a98fd \\\n"
    "    --hash=sha256:7f047e29dcae44602496db43be01ad42fc6f1cc0d8cd6c83d342306c32270196 \\\n"
    "    --hash=sha256:8dc52c23056b9ddd46818a57b78404882310fb473d63f17b07d5c40421e47f8e \\\n"
    "    --hash=sha256:9149cad251584d5fb4981be1ecde53a1ca46c891a79788c0df828d2f166bda28 \\\n"
    "    --hash=sha256:96b533f0e99f6579b3d4d4995707cf36df9100d67e0c8303a0c55b27b5f99bc5 \\\n"
    "    --hash=sha256:ba1cc08a7ccde2d2ec775841541641e4548226580ab850948cbfda66a1befcdc \\\n"
    "    --hash=sha256:fc09d0aa354569bc501d4e787133afc08552722d3ab34836a80547331bb5d4a0\n"
    "markdown-it-py==4.0.0 \\\n"
    "    --hash=sha256:87327c59b172c5011896038353a81343b6754500a08cd7a4973bb48c6d578147\n"
    "mdurl==0.1.2 \\\n"
    "    --hash=sha256:84008a41e51615a49fc9966191ff91509e3c40b939176e643fd50a5c2196b8f8\n"
)

LICENSE_ACK_LABEL = (
    "I have read the repository license policy and I accept the Helianthus "
    "licensing model for any contribution or reusable material I submit here."
)

CONTROL_MD = {
    "AGENTS.md",
}

PLATFORM_SNAPSHOT_REF = (
    "153191f72b5b9ecacbadcf2f3d7e480c6" + "fef89a4"
)
PLATFORM_REPO = "Project-Helianthus/helianthus-docs-ebus"
PLATFORM_SNAPSHOT_PATH = "scripts/platform_cross_seed_snapshot.yaml"
PLATFORM_SNAPSHOT_SHA256 = "2ba234d20e3687299ffc4777da7b1413" "8ebf9b49b1ca82ccbca834e5dc9d171b"
PLATFORM_SNAPSHOT_TARGETS = {
    "docs/platform/README.md",
    "docs/platform/cross-runtime-envelope.md",
    "docs/platform/eebus-ha-network-proof.md",
    "docs/platform/eebus-interop-smoke.md",
    "docs/platform/eebus-raw-first-contract.md",
    "docs/platform/hash-auth-binding.md",
    "docs/platform/ownership-and-doc-gates.md",
    "docs/platform/ownership-validation.md",
    "docs/platform/promotion-and-consumer-contract.md",
    "docs/platform/raw-correlation-and-leaf-promotion.md",
    "docs/platform/shared-registry-boundary.md",
}
PUBLICATION_CHANNELS_PATH = "scripts/publication_channels.yaml"
PLATFORM_SNAPSHOT_PATTERN = re.compile(
    rf"{re.escape(PLATFORM_REPO)}@([0-9a-f]{{40}}):(docs/platform/[A-Za-z0-9._/-]+\.md)"
)
CANDIDATE_API_ROOT = PurePosixPath("api/_candidate")
CANDIDATE_API_CHANNELS = (
    "stable_navigation",
    "search",
    "sitemap",
    "versioned_bundle",
    "release_bundle",
)
STABLE_PUBLICATION_CHANNELS = {
    "search",
    "sitemap",
    "versioned_bundle",
    "release_bundle",
}
PUBLICATION_PLATFORM_CONTRACT = {
    "source_repository": "Project-Helianthus/helianthus-docs-ebus",
    "source_merge": "8872f65b888048db001bc640ae04a4f460ee8db1",
    "source_manifest_path": "docs/platform/manifests/eebus-doc-ownership.yaml",
    "source_manifest_blob_mode": "100644",
    "source_manifest_oid": "1f7c7c0a94504614949e3478387fca4def079c2e",
    "source_manifest_sha256": "3f7b16f32ded7f16b12ecd644d361f315df1ba6d10d462a9c9054585774fd04e",
    "completion_proof_sha256": "0b695b603f19dff35b857ddf47e03fe0ae02ac39ca89c353de8482872fd8c3de",
    "channel_registry": {
        "canonical": {
            "visibility": "stable",
            "owner": "canonical_documentation_owner",
        }
    },
    "eligible_channels": {
        member: ["canonical"]
        for member in [
            "cross-runtime-platform-contracts",
            "eebus-api-v1",
            "eebus-architecture",
            "eebus-protocol",
            "platform-cross-runtime-envelope",
            "platform-hash-auth-binding",
            "platform-ownership-validation",
            "platform-promotion-consumer-contract",
            "platform-shared-registry-boundary",
        ]
    },
    "exact_memberships": {
        "canonical": [
            "cross-runtime-platform-contracts",
            "eebus-api-v1",
            "eebus-architecture",
            "eebus-protocol",
            "platform-cross-runtime-envelope",
            "platform-hash-auth-binding",
            "platform-ownership-validation",
            "platform-promotion-consumer-contract",
            "platform-shared-registry-boundary",
        ]
    },
    "candidate_inventory": [],
}
SITEMAP_NAMESPACE = "http://www.sitemaps.org/schemas/sitemap/0.9"
REPOSITORY_TEXT_SUFFIXES = {
    ".csv",
    ".html",
    ".htm",
    ".ini",
    ".json",
    ".jsonl",
    ".markdown",
    ".md",
    ".mdown",
    ".mkd",
    ".mkdn",
    ".ndjson",
    ".toml",
    ".tsv",
    ".txt",
    ".xml",
    ".yaml",
    ".yml",
}
MAX_REPOSITORY_TEXT_SCAN_BYTES = 2 * 1024 * 1024
MAX_PLATFORM_FINGERPRINT_WINDOWS = 100_000
STRUCTURED_SNAPSHOT_ARTIFACTS = {PLATFORM_SNAPSHOT_PATH}
MIN_PLATFORM_COPY_WORDS = 10
MIN_PLATFORM_COPY_CHARACTERS = 56
NONPUBLISHABLE_PUBLICATION_STATUSES = {
    "blocked",
    "candidate",
    "draft",
    "planned",
    "planned-target",
    "removed",
    "retired-candidate",
    "template",
    "withdrawn",
}
SUMMARY_NORMATIVE_PATTERN = re.compile(
    r"\b(?:must|shall|should(?:\s+not)?|may\s+not|cannot|never|"
    r"(?:is|are|be|remain)\s+(?:mandatory|required)|"
    r"(?:is|are)\s+required\s+to|requires?|mandatory)\b|"
    r"\bonly\b[^\n.]{0,80}\bmay\b|"
    r"\bmay\b[^\n.]{0,80}\bonly\b",
    re.IGNORECASE | re.MULTILINE,
)
SUMMARY_IMPERATIVE_PATTERN = re.compile(
    r"^\s*(?:(?:[-*+]\s+)|(?:\d+[.)]\s+))?"
    r"(?:allow|assign|bind|copy|define|do\s+not|document|ensure|expose|follow|"
    r"forward|implement|keep|map|merge|omit|preserve|publish|read|reject|require|"
    r"retain|return|route|store|use|validate|write)\b",
    re.IGNORECASE | re.MULTILINE,
)
REFERENCE_TOKEN_PATTERN = re.compile(
    r"(?:https?:)?//[^\s<>\"']+|(?:[./A-Za-z0-9%_~-]+/)+[./A-Za-z0-9%_~-]+",
    re.IGNORECASE,
)
JSON_STRING_PATTERN = re.compile(
    r'"(?:\\(?:["\\/bfnrt]|u[0-9A-Fa-f]{4})|[^"\\])*"'
)
UNICODE_SURROGATE_PAIR_PATTERN = re.compile(
    r"\\u([dD][89aAbB][0-9A-Fa-f]{2})\\u([dD][c-fC-F][0-9A-Fa-f]{2})"
)
UNICODE_ESCAPE_PATTERN = re.compile(r"\\u([0-9A-Fa-f]{4})")
PRODUCTION_REVIEWED_ACTIVE_ARCHITECTURE = {
    "3811303d2c1dc848dc12d3f36aef61eb" "f9a40eb6ef7c7a7c9d7f23fcef2d133d": {
        "canonical_source": (
            "Project-Helianthus/helianthus-docs-eebus:architecture/README.md"
        ),
        "owner_domain": "architecture",
        "license": "AGPL-3.0-only",
        "claim_status": "evidence-backed",
        "publication_status": "active",
        "source_class": "derived_inference",
        "evidence_ids": "EV-20260711-001, EV-20260714-001",
        "hypothesis_status": "publishable",
        "falsifier": (
            "A publishable canonical contract changes these ownership or "
            "evidence-acceptance boundaries."
        ),
        "cross_seed_target": (
            "Project-Helianthus/helianthus-docs-ebus:"
            "docs/platform/shared-registry-boundary.md"
        ),
        "cross_seed_mode": "summary-only",
        "cross_seed_snapshot": (
            "Project-Helianthus/helianthus-docs-ebus@"
            "153191f72b5b9ecacbad" "cf2f3d7e480c6fef89a4:"
            "docs/platform/shared-registry-boundary.md"
        ),
        "stable_navigation": "true",
        "search": "true",
        "sitemap": "true",
        "versioned_bundle": "true",
        "release_bundle": "true",
    },
}
PRODUCTION_REVIEWED_SUPPORTED_API = {
    "74a8f24cc7d835029d368d67ebcb1856" "77db7c4177a26bbb60165b4cbedf36d5": {
        "canonical_source": (
            "Project-Helianthus/helianthus-docs-eebus:api/api-surface-v1.md"
        ),
        "owner_domain": "api",
        "license": "AGPL-3.0-only",
        "publication_status": "api-contract",
        "claim_status": "no-protocol-claims",
    },
    "337bf7ffd7ec7bdd36ecd9b6ad9c5ad0" "31ec0aeef596cfae53d2a7d0371fa6a3": {
        "canonical_source": (
            "Project-Helianthus/helianthus-docs-eebus:"
            "api/eebusruntime-v1/reference.md"
        ),
        "owner_domain": "api",
        "license": "AGPL-3.0-only",
        "publication_status": "active",
        "claim_status": "evidence-backed",
        "source_class": "derived_inference",
        "evidence_ids": "EV-20260711-001",
        "hypothesis_status": "publishable",
        "falsifier": (
            "Regenerating the normalized API surface from the exact source "
            "commit produces different public declarations or evidence bytes."
        ),
        "api_version": "eebusruntime-v1",
        "source_commit": "7a5852e009bbdcba47f0" "a34ba866070a4ab35ef8",
        "source_tree": "b090651c99d5b6817a40" "997b14c1b6a2a37c124e",
        "stable_navigation": "true",
        "search": "true",
        "sitemap": "true",
        "versioned_bundle": "true",
        "release_bundle": "true",
    },
}
FIXTURE_REVIEWED_ACTIVE_ARCHITECTURE = {
    # Synthetic contract bytes are accepted only by the explicit fixture mode.
    "bebc7eb49d7eb838e6409c24369610e0" "c751adb47e9d8f96a7f7d2b90ae741a2": {
        "canonical_source": (
            "Project-Helianthus/helianthus-docs-eebus:architecture/README.md"
        ),
        "owner_domain": "architecture",
        "license": "AGPL-3.0-only",
        "claim_status": "evidence-backed",
        "publication_status": "active",
        "source_class": "vendor_public",
        "evidence_ids": "EV-20260711-001",
        "hypothesis_status": "publishable",
        "falsifier": "A publishable public source contradicts this runtime boundary.",
        "cross_seed_target": (
            "Project-Helianthus/helianthus-docs-ebus:"
            "docs/platform/shared-registry-boundary.md"
        ),
        "cross_seed_mode": "summary-only",
        "cross_seed_snapshot": (
            "Project-Helianthus/helianthus-docs-ebus@"
            "153191f72b5b9ecacbad" "cf2f3d7e480c6fef89a4:"
            "docs/platform/shared-registry-boundary.md"
        ),
    },
}
PRODUCTION_REVIEWED_EVIDENCE = {
    "EV-20260711-001": {
        "e9fc9220b0fcc8b02a968fe6a587be53" "8841f818754dd265c54c5580e1ed1bbf": {
            "canonical_source": (
                "Project-Helianthus/helianthus-docs-eebus:"
                "evidence/EV-20260711-001.md"
            ),
            "owner_domain": "evidence",
            "license": "CC0-1.0",
            "publication_status": "publishable",
            "claim_status": "evidence-backed",
            "source_class": "derived_inference",
            "evidence_ids": "EV-20260711-001",
            "hypothesis_status": "publishable",
            "falsifier": (
                "A publishable canonical ownership or API contract contradicts "
                "this record."
            ),
        },
    },
    "EV-20260714-001": {
        "89e3c9f6d44f3abb1bb41f10de8942e" "79841f8dca4635231b3c565164b447f85": {
            "canonical_source": (
                "Project-Helianthus/helianthus-docs-eebus:"
                "evidence/EV-20260714-001.md"
            ),
            "owner_domain": "evidence",
            "license": "CC0-1.0",
            "publication_status": "publishable",
            "claim_status": "evidence-backed",
            "source_class": "observed_runtime",
            "evidence_ids": "EV-20260714-001",
            "hypothesis_status": "publishable",
            "falsifier": (
                "A redacted report with the cited digest demonstrates inbound "
                "transport or protocol acceptance in this attempt."
            ),
        },
    },
}
FIXTURE_REVIEWED_EVIDENCE = {
    "EV-20260711-001": {
        "88dfdda055f32b274a8f74cb5fa6989c" "cf8ad435b7e5cd8d13b0244d5763c537": {
            "canonical_source": (
                "Project-Helianthus/helianthus-docs-eebus:"
                "evidence/EV-20260711-001.md"
            ),
            "owner_domain": "evidence",
            "license": "CC0-1.0",
            "publication_status": "publishable",
            "claim_status": "evidence-backed",
            "source_class": "vendor_public",
            "evidence_ids": "EV-20260711-001",
            "hypothesis_status": "publishable",
            "falsifier": (
                "A publishable public source contradicts the recorded observation."
            ),
        },
    },
}
PRODUCTION_REVIEWED_CROSS_SEED = {
    **PRODUCTION_REVIEWED_ACTIVE_ARCHITECTURE,
    "b389e0f6e69e02222a233524b000a614" "2237511322f96700adee2830af381719": {
        "canonical_source": (
            "Project-Helianthus/helianthus-docs-eebus:devices/vr940f.md"
        ),
        "owner_domain": "devices",
        "license": "CC0-1.0",
        "cross_seed_target": (
            "Project-Helianthus/helianthus-docs-ebus:"
            "docs/platform/eebus-raw-first-contract.md"
        ),
        "cross_seed_mode": "summary-only",
        "cross_seed_snapshot": (
            "Project-Helianthus/helianthus-docs-ebus@"
            "153191f72b5b9ecacbad" "cf2f3d7e480c6fef89a4:"
            "docs/platform/eebus-raw-first-contract.md"
        ),
        "claim_status": "no-protocol-claims",
        "publication_status": "planned-target",
    },
}
FIXTURE_REVIEWED_CROSS_SEED = {
    **FIXTURE_REVIEWED_ACTIVE_ARCHITECTURE,
}
MARKDOWN = MarkdownIt("commonmark", {"html": True})
MSP045_CONTRACT_PATH = "architecture/_candidate/msp-045-trust-admin-projection.md"
MSP045_NORMATIVE_TABLE_KEYS = {
    "Contract Identity And Ownership": "Boundary",
    "Combined State Product": "Product class",
    "Closed Projection Precedence": "Priority",
    "Existing Public Field Mapping": "Public field",
    "Runtime Degradation Precedence": "Priority",
    "Candidate Absence Rule": "Candidate condition",
    "Publication Linearization": "Linearized outcome",
    "Startup And Restart Publication": "Classified product",
    "Rollback Ledger": "Case",
}
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
PROVENANCE_IDENTIFIER_PATTERN = re.compile(
    r"(?<![0-9A-Fa-f])(?:[0-9A-Fa-f]{64}|[0-9A-Fa-f]{40})(?![0-9A-Fa-f])"
)
PRIVATE_ARTIFACT_FIELD_PATTERN = re.compile(
    r"^\s*(?:[-*]\s*)?[\"']?private[\s_-]+artifact[\s_-]+"
    r"(?:location|reference|filename|hash|identifier)[\"']?\s*[:=]",
    re.IGNORECASE | re.MULTILINE,
)
PRIVATE_ARTIFACT_RETAINED_PATTERN = re.compile(
    r"^\s*(?:[-*]\s*)?[\"']?private[\s_-]+artifact[\s_-]+retained"
    r"[\"']?\s*[:=]\s*(\S.*)$",
    re.IGNORECASE | re.MULTILINE,
)
EEBUS_ID_LABEL_PATTERN = (
    r"(?:(?:ski|ship)(?:[\s_-]*(?:id|identifier))?)"
)
ASCII_COLON = chr(58)
SENSITIVE_FIELD_PATTERN = re.compile(
    r"^\s*(?:[-*]\s*)?[\"']?"
    r"(token|password|passphrase|credential|secret|api[\s_-]*key|"
    r"client[\s_-]*secret|account (?:id|identifier)|"
    r"(?:full )?fingerprint|mac address|serial(?: number)?|local identity|"
    r"stable peer identifier|pairing history|household schedule|"
    rf"(?:raw\s+)?{EEBUS_ID_LABEL_PATTERN})[\"']?"
    r"\s*[:=]\s*(\S.*)$",
    re.IGNORECASE | re.MULTILINE,
)
RAW_EEBUS_ID_PATTERN = re.compile(
    rf"`?\b(?:raw\s+)?{EEBUS_ID_LABEL_PATTERN}\b`?"
    rf"\s*(?:{ASCII_COLON}|=|\bis\b)?\s*`?([A-Za-z0-9][A-Za-z0-9._{ASCII_COLON}-]{{7,}})`?",
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
    r"\bvendor[\s_-]+restric" r"ted(?=$|[\s_.-])|"
    r"\brestric" r"ted[ -]+source\b|"
    r"\brestric" r"ted\s+vendor\s+"
    r"(?:documents?|docs?|sources?|materials?|contents?|texts?)\b|"
    r"\bparaphras(?:e|ed|ing)\b[^\n]{0,80}\brestric" r"ted\b|"
    r"\bsource\s+class\s*:\s*restric" r"ted\b|"
    r"\b(?:restric" r"ted|quarantined)[\s_-]+(?:source|vendor|document|material)"
    r"[^\n]{0,80}\b(?:file(?:name)?|hash|sha(?:256)?|digest|locator|"
    r"paraphrase|rationale|reason|provenance|origin)\b|"
    r"\b(?:file(?:name)?|hash|sha(?:256)?|digest|locator|paraphrase|rationale|"
    r"reason|provenance|origin)\b[^\n]{0,80}"
    r"\b(?:restric" r"ted|quarantined)[\s_-]+(?:source|vendor|document|material)\b",
    re.IGNORECASE,
)
ALLOWED_RESTRICTED_POLICY_LINE = (
    "| `vendor_" + "restricted` | Quarantined; never public text, issue text, PR text, "
    "review text, or ADR rationale. |"
)
ALLOWED_RESTRICTED_POLICY_PATTERN = re.compile(
    r"\b(?:do not|must not|never|forbid(?:s|den)?|prohibit(?:s|ed)?|reject(?:s|ed)?)\b"
    r"[^\n]{0,120}\brestric" r"ted(?:[\s_-]+source|[\s_-]+material)?\b",
    re.IGNORECASE,
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


def _markdown_body(text: str) -> str:
    end = text.find("\n---\n", 4)
    return text[end + 5 :] if end >= 0 else text


def _git_blob_id(text: str) -> str:
    content = text.encode("utf-8")
    header = f"blob {len(content)}\0".encode("ascii")
    return hashlib.sha1(header + content).hexdigest()


def _load_platform_snapshot(root: Path) -> tuple[dict[str, Any] | None, list[str]]:
    snapshot_path = root / PLATFORM_SNAPSHOT_PATH
    invalid = f"{PLATFORM_SNAPSHOT_PATH}: platform cross-seed snapshot is unavailable or invalid"
    if not snapshot_path.is_file() or snapshot_path.is_symlink():
        return None, [invalid]
    try:
        snapshot_size = snapshot_path.stat().st_size
    except OSError:
        return None, [invalid]
    if snapshot_size > MAX_REPOSITORY_TEXT_SCAN_BYTES:
        return None, [invalid]
    if hashlib.sha256(snapshot_path.read_bytes()).hexdigest() != PLATFORM_SNAPSHOT_SHA256:
        return None, [invalid]
    try:
        document = yaml.load(_read(snapshot_path), Loader=UniqueKeySafeLoader)
    except (UnicodeDecodeError, yaml.YAMLError):
        return None, [invalid]
    if not isinstance(document, dict):
        return None, [invalid]

    expected = {
        "schema": "helianthus.platform-cross-seed-snapshot",
        "version": "1",
        "repository": PLATFORM_REPO,
        "commit": PLATFORM_SNAPSHOT_REF,
        "source_manifest_path": "docs/platform/manifests/eebus-doc-ownership.yaml",
        "source_manifest_entry": "cross-runtime-platform-contracts",
        "platform_contract_root": "docs/platform",
        "platform_contract_state": "active",
    }
    if any(document.get(key) != value for key, value in expected.items()):
        return None, [invalid]
    source_manifest_blob = document.get("source_manifest_blob")
    source_manifest_content = document.get("source_manifest_content")
    if (
        re.fullmatch(r"[0-9a-f]{40}", source_manifest_blob or "") is None
        or not isinstance(source_manifest_content, str)
        or _git_blob_id(source_manifest_content) != source_manifest_blob
    ):
        return None, [invalid]

    targets = document.get("targets")
    if not isinstance(targets, list) or not targets:
        return None, [invalid]
    target_paths: set[str] = set()
    source_contents: dict[str, str] = {}
    for target in targets:
        if not isinstance(target, dict) or set(target) != {"path", "blob", "content"}:
            return None, [invalid]
        path = target.get("path")
        blob = target.get("blob")
        content = target.get("content")
        if (
            not isinstance(path, str)
            or not isinstance(blob, str)
            or not isinstance(content, str)
            or not content.strip()
        ):
            return None, [invalid]
        normalized = posixpath.normpath(path)
        if (
            normalized != path
            or not path.startswith("docs/platform/")
            or not path.endswith(".md")
            or re.fullmatch(r"[0-9a-f]{40}", blob) is None
            or _git_blob_id(content) != blob
            or path in target_paths
        ):
            return None, [invalid]
        target_paths.add(path)
        source_contents[path] = content

    if target_paths != PLATFORM_SNAPSHOT_TARGETS:
        return None, [invalid]
    if (
        sum(len(value.encode("utf-8")) for value in source_contents.values())
        > MAX_REPOSITORY_TEXT_SCAN_BYTES
    ):
        return None, [invalid]

    try:
        manifest = yaml.load(source_manifest_content, Loader=UniqueKeySafeLoader)
    except yaml.YAMLError:
        return None, [invalid]
    entries = manifest.get("entries") if isinstance(manifest, dict) else None
    if not isinstance(entries, list):
        return None, [invalid]
    manifest_channel_pages = {
        channel: set() for channel in CANDIDATE_API_CHANNELS
    }
    local_repository = REPO_ID.split("/", 1)[1]
    seen_entry_ids: set[str] = set()
    for entry in entries:
        if not isinstance(entry, dict):
            return None, [invalid]
        entry_id = entry.get("id")
        if not isinstance(entry_id, str) or entry_id in seen_entry_ids:
            return None, [invalid]
        seen_entry_ids.add(entry_id)
        owner = entry.get("owner")
        outputs = entry.get("outputs")
        if not isinstance(owner, dict) or not isinstance(outputs, dict):
            return None, [invalid]
        if owner.get("repository") != local_repository or entry.get("state") != "active":
            continue
        owner_path = owner.get("path")
        if not isinstance(owner_path, str):
            return None, [invalid]
        for channel in CANDIDATE_API_CHANNELS:
            enabled = outputs.get(channel)
            if not isinstance(enabled, bool):
                return None, [invalid]
            if enabled:
                manifest_channel_pages[channel].add(owner_path)

    return {
        "repository": document["repository"],
        "commit": document["commit"],
        "targets": target_paths,
        "source_contents": source_contents,
        "manifest_channel_pages": manifest_channel_pages,
    }, []


def _load_publication_channels(
    root: Path,
) -> tuple[dict[str, Any] | None, list[str]]:
    invalid = f"{PUBLICATION_CHANNELS_PATH}: publication channel configuration is invalid"
    path = root / PUBLICATION_CHANNELS_PATH
    if not path.is_file() or path.is_symlink():
        return None, [invalid]
    try:
        size = path.stat().st_size
    except OSError:
        return None, [invalid]
    if size > MAX_REPOSITORY_TEXT_SCAN_BYTES:
        return None, [
            f"{PUBLICATION_CHANNELS_PATH}: publication channel configuration exceeds size limit"
        ]
    try:
        document = yaml.load(_read(path), Loader=UniqueKeySafeLoader)
    except (UnicodeDecodeError, yaml.YAMLError):
        return None, [invalid]
    if not isinstance(document, dict) or set(document) != {
        "schema", "version", "platform_contract", "public_output_roots",
        "publisher", "channels",
    }:
        return None, [invalid]
    if (
        document.get("schema") != "helianthus.publication-channels"
        or document.get("version") != "2"
        or document.get("platform_contract") != PUBLICATION_PLATFORM_CONTRACT
    ):
        return None, [invalid]
    roots = document.get("public_output_roots")
    channels = document.get("channels")
    publisher = document.get("publisher")
    if (
        not isinstance(roots, list)
        or not roots
        or any(
            not isinstance(value, str)
            or value != posixpath.normpath(value)
            or PurePosixPath(value).is_absolute()
            or ".." in PurePosixPath(value).parts
            for value in roots
        )
        or len(set(roots)) != len(roots)
        or roots != sorted(roots, key=lambda value: value.encode("utf-8"))
        or not isinstance(channels, dict)
        or set(channels) != STABLE_PUBLICATION_CHANNELS
        or not isinstance(publisher, dict)
        or set(publisher) != {"repository", "path", "blob_mode", "oid", "sha256"}
    ):
        return None, [invalid]
    publisher_path = publisher.get("path")
    if (
        publisher.get("repository") != REPO_ID
        or publisher_path != "scripts/render_publication.py"
        or publisher.get("blob_mode") != "100755"
        or not isinstance(publisher.get("oid"), str)
        or re.fullmatch(r"[0-9a-f]{40}", publisher["oid"]) is None
        or not isinstance(publisher.get("sha256"), str)
        or re.fullmatch(r"[0-9a-f]{64}", publisher["sha256"]) is None
    ):
        return None, [invalid]
    publisher_file = root / publisher_path
    if not publisher_file.is_file() or publisher_file.is_symlink():
        return None, [invalid]
    publisher_bytes = publisher_file.read_bytes()
    measured_blob_mode = (
        "100755" if publisher_file.lstat().st_mode & 0o111 else "100644"
    )
    publisher_oid = hashlib.sha1(
        f"blob {len(publisher_bytes)}\0".encode() + publisher_bytes
    ).hexdigest()
    if (
        publisher["blob_mode"] != measured_blob_mode
        or publisher["oid"] != publisher_oid
        or publisher["sha256"] != hashlib.sha256(publisher_bytes).hexdigest()
    ):
        return None, [invalid]
    registered: dict[str, str] = {}
    for channel, specification in channels.items():
        if (
            not isinstance(specification, dict)
            or set(specification) != {"artifact", "members"}
        ):
            return None, [invalid]
        value = specification.get("artifact")
        members = specification.get("members")
        if (
            not isinstance(value, str)
            or not isinstance(members, list)
            or not members
            or any(not isinstance(member, str) for member in members)
            or len(set(members)) != len(members)
            or members != sorted(members, key=lambda member: member.encode("utf-8"))
        ):
            return None, [invalid]
        for member in members:
            if (
                member != posixpath.normpath(member)
                or PurePosixPath(member).is_absolute()
                or ".." in PurePosixPath(member).parts
            ):
                return None, [invalid]
        normalized = posixpath.normpath(value)
        if (
            value != normalized
            or PurePosixPath(value).is_absolute()
            or ".." in PurePosixPath(value).parts
            or value in registered
            or not any(value == root_value or value.startswith(root_value + "/") for root_value in roots)
        ):
            return None, [invalid]
        registered[value] = channel
    return {"roots": tuple(roots), "registered": registered}, []


def _reviewed_architecture_claim(
    text: str,
    metadata: dict[str, str],
    *,
    fixture_mode: bool,
) -> dict[str, str] | None:
    body_hash = hashlib.sha256(_markdown_body(text).encode("utf-8")).hexdigest()
    reviewed = PRODUCTION_REVIEWED_ACTIVE_ARCHITECTURE.get(body_hash)
    if reviewed is None and fixture_mode:
        reviewed = FIXTURE_REVIEWED_ACTIVE_ARCHITECTURE.get(body_hash)
    if reviewed is None or metadata != reviewed:
        return None
    return reviewed


def _reviewed_supported_api_claim(
    text: str,
    metadata: dict[str, str],
) -> dict[str, str] | None:
    body_hash = hashlib.sha256(_markdown_body(text).encode("utf-8")).hexdigest()
    reviewed = PRODUCTION_REVIEWED_SUPPORTED_API.get(body_hash)
    if reviewed is None or metadata != reviewed:
        return None
    return reviewed


def _reviewed_cross_seed_claim(
    text: str,
    metadata: dict[str, str],
    *,
    fixture_mode: bool,
) -> dict[str, str] | None:
    body_hash = hashlib.sha256(_markdown_body(text).encode("utf-8")).hexdigest()
    reviewed = PRODUCTION_REVIEWED_CROSS_SEED.get(body_hash)
    if reviewed is None and fixture_mode:
        reviewed = FIXTURE_REVIEWED_CROSS_SEED.get(body_hash)
    if reviewed is None or metadata != reviewed:
        return None
    return reviewed


def _fully_unquote(value: str) -> str:
    """Decode nested percent escapes to a fixed point."""
    decoded = value
    while True:
        next_value = unquote(decoded)
        if next_value == decoded:
            return decoded
        decoded = next_value


def _decode_raw_unicode_escapes(value: str) -> str:
    """Decode only JSON-style Unicode escapes, leaving other escapes literal."""

    def decode_pair(match: re.Match[str]) -> str:
        high = int(match.group(1), 16)
        low = int(match.group(2), 16)
        return chr(0x10000 + ((high - 0xD800) << 10) + low - 0xDC00)

    def decode_bmp(match: re.Match[str]) -> str:
        codepoint = int(match.group(1), 16)
        if 0xD800 <= codepoint <= 0xDFFF:
            return match.group(0)
        return chr(codepoint)

    paired = UNICODE_SURROGATE_PAIR_PATTERN.sub(decode_pair, value)
    return UNICODE_ESCAPE_PATTERN.sub(decode_bmp, paired)


def _fully_decode_reference(value: str) -> str:
    """Normalize nested reference encodings to a fixed point."""
    decoded = value
    while True:
        next_value = _decode_raw_unicode_escapes(
            _fully_unquote(html.unescape(decoded))
        )
        if next_value == decoded:
            return decoded
        decoded = next_value


def _reference_text_variants(text: str) -> set[str]:
    """Return decoded text plus JSON string values embedded in serializations."""
    variants = {text, _fully_decode_reference(text)}
    pending = list(variants)
    while pending:
        value = pending.pop()
        for match in JSON_STRING_PATTERN.finditer(value):
            try:
                decoded = json.loads(match.group(0))
            except (json.JSONDecodeError, UnicodeDecodeError):
                continue
            if not isinstance(decoded, str):
                continue
            decoded = _fully_decode_reference(decoded)
            if decoded not in variants:
                variants.add(decoded)
                pending.append(decoded)
    return variants


def _github_repository_relative_path(value: str) -> str | None:
    """Map recognized URLs for this repository to their checkout-relative path."""
    decoded = _fully_decode_reference(value).replace("\\", "/")
    host_root = decoded.startswith("/") and not decoded.startswith("//")
    parsed_value = "https:" + decoded if decoded.startswith("//") else decoded
    try:
        parsed = urlsplit(parsed_value)
    except ValueError:
        return None
    hostname = parsed.hostname
    if hostname is None and not host_root:
        return None
    host = hostname.rstrip(".").casefold() if hostname is not None else "github.com"
    path = posixpath.normpath(_fully_decode_reference(parsed.path))
    segments = [segment for segment in path.split("/") if segment]
    repo_owner, repo_name = REPO_ID.split("/", 1)

    if host == "api.github.com":
        if (
            len(segments) < 5
            or segments[0].casefold() != "repos"
            or segments[1].casefold() != repo_owner.casefold()
            or segments[2].casefold() != repo_name.casefold()
            or segments[3].casefold() != "contents"
        ):
            return None
        return "/".join(segments[4:])

    if len(segments) < 4 or segments[0].casefold() != repo_owner.casefold() or segments[
        1
    ].casefold() != repo_name.casefold():
        return None

    if host in {"github.com", "www.github.com"}:
        if len(segments) < 5 or segments[2].casefold() not in {"blob", "raw", "tree"}:
            return None
        path_start = 4
    elif host == "raw.githubusercontent.com":
        path_start = 3
    else:
        return None

    for index in range(path_start, len(segments) - 1):
        if segments[index] == "api" and segments[index + 1] == "_candidate":
            path_start = index
            break
    return "/".join(segments[path_start:])


def _is_candidate_path(rel: str) -> bool:
    decoded = _fully_decode_reference(rel)
    normalized = posixpath.normpath(decoded.replace("\\", "/").lstrip("/"))
    path = PurePosixPath(normalized)
    return path == CANDIDATE_API_ROOT or CANDIDATE_API_ROOT in path.parents


def _is_candidate_api(rel: str, metadata: dict[str, str]) -> bool:
    return _is_candidate_path(rel) or metadata.get("owner_domain") == "api" and (
        metadata.get("publication_status") in {"candidate", "retired-candidate"}
        or metadata.get("candidate_output") == "true"
    )


def _candidate_api_errors(rel: str, metadata: dict[str, str]) -> list[str]:
    if not _is_candidate_api(rel, metadata):
        return []

    errors: list[str] = []
    status = metadata.get("publication_status")
    if _is_candidate_path(rel) and status not in {"candidate", "retired-candidate"}:
        errors.append(f"{rel}: candidate API path must declare publication_status candidate")
    if status == "retired-candidate" and metadata.get("hypothesis_status") != "withdrawn":
        errors.append(f"{rel}: retired candidate must declare hypothesis_status withdrawn")
    if metadata.get("candidate_output") != "true":
        errors.append(f"{rel}: candidate API must declare candidate_output true")
    for channel in CANDIDATE_API_CHANNELS:
        if metadata.get(channel) != "false":
            errors.append(f"{rel}: candidate API is exposed through {channel}")

    declared = metadata.get("candidate_output_path", "")
    candidate_path = PurePosixPath(declared)
    rel_path = PurePosixPath(rel)
    portable = (
        bool(declared)
        and "\\" not in declared
        and "%" not in declared
        and not candidate_path.is_absolute()
        and ".." not in candidate_path.parts
        and candidate_path == rel_path
        and CANDIDATE_API_ROOT in candidate_path.parents
    )
    if not portable:
        errors.append(
            f"{rel}: candidate API path must be portable and contained under api/_candidate"
        )
    return errors


def _active_architecture_errors(
    rel: str,
    text: str,
    metadata: dict[str, str],
    *,
    fixture_mode: bool,
) -> list[str]:
    if metadata.get("owner_domain") != "architecture" or metadata.get(
        "publication_status"
    ) != "active":
        return []

    errors: list[str] = []
    if (
        metadata.get("claim_status") != "evidence-backed"
        or metadata.get("source_class") not in EVIDENCE_SOURCE_CLASSES
        or metadata.get("hypothesis_status") != "publishable"
    ):
        errors.append(f"{rel}: active architecture claim lacks publishable support")

    if _reviewed_architecture_claim(text, metadata, fixture_mode=fixture_mode) is None:
        errors.append(f"{rel}: active architecture content is not in the reviewed claim registry")

    if any(
        "restricted" in key.lower() or "quarantined" in key.lower()
        for key in metadata
    ):
        errors.append(f"{rel}: restric" "ted-source provenance metadata is forbidden")

    return errors


def _supported_api_errors(
    rel: str,
    text: str,
    metadata: dict[str, str],
) -> list[str]:
    if metadata.get("owner_domain") != "api" or _is_candidate_api(rel, metadata):
        return []
    if rel == "api/README.md":
        return []
    if _reviewed_supported_api_claim(text, metadata) is None:
        return [f"{rel}: API content is not in the reviewed supported API registry"]
    return []


def _milestone_errors(rel: str, metadata: dict[str, str]) -> list[str]:
    terminal_states = {
        "abandoned",
        "aborted",
        "active",
        "available",
        "canceled",
        "cancelled",
        "closed",
        "complete",
        "completed",
        "delivered",
        "done",
        "failed",
        "finished",
        "landed",
        "merged",
        "passed",
        "published",
        "ready",
        "rejected",
        "released",
        "removed",
        "resolved",
        "retired",
        "shipped",
        "succeeded",
        "successful",
        "superseded",
        "terminated",
        "withdrawn",
    }
    lifecycle_fields = {
        "complete",
        "completion",
        "lifecycle",
        "phase",
        "stage",
        "state",
        "status",
    }

    def normalized(value: str) -> str:
        decoded = _fully_decode_reference(value)
        return re.sub(r"[^a-z0-9]+", "-", decoded.strip().casefold()).strip("-")

    entries = [(normalized(key), normalized(value)) for key, value in metadata.items()]
    clean_present = any(
        "msp-docs-clean" in key or "msp-docs-clean" in value
        for key, value in entries
    )
    completion_entries = [
        (key, value)
        for key, value in entries
        if any(part in lifecycle_fields for part in key.split("-"))
    ]
    terminal_present = any(
        bool(set(value.split("-")) & terminal_states)
        or value in {"1", "true", "yes"}
        or "msp-docs-clean" in value
        for _, value in completion_entries
    )
    inline_terminal_claim = any(
        ("msp-docs-clean" in key or "msp-docs-clean" in value)
        and bool((set(key.split("-")) | set(value.split("-"))) & terminal_states)
        for key, value in entries
    )
    if clean_present and (terminal_present or inline_terminal_claim):
        return [f"{rel}: MSP-DOCS-CLEAN cannot be claimed during MSP-DOCS-E2"]
    return []


def _normalized_reference_paths(text: str, source_rel: str) -> set[str]:
    paths: set[str] = set()
    source_parent = PurePosixPath(source_rel).parent.as_posix()

    def add_reference(value: str) -> None:
        decoded = _fully_decode_reference(value)
        repository_path = _github_repository_relative_path(decoded)
        if repository_path is not None:
            paths.add(posixpath.normpath(repository_path))
            return
        if "://" in decoded or decoded.startswith("//"):
            parsed_value = "https:" + decoded if decoded.startswith("//") else decoded
            try:
                decoded = urlsplit(parsed_value).path
            except ValueError:
                return
        decoded = decoded.split("#", 1)[0].split("?", 1)[0].replace("\\", "/")
        if not decoded:
            return
        root_relative = posixpath.normpath(decoded.lstrip("/"))
        source_relative = posixpath.normpath(posixpath.join(source_parent, decoded))
        paths.update({root_relative, source_relative})

    for variant in _reference_text_variants(text):
        decoded_text = variant.replace("\\", "/")
        if re.fullmatch(r"[^\s<>\"']+", decoded_text):
            add_reference(decoded_text)
        for match in REFERENCE_TOKEN_PATTERN.finditer(decoded_text):
            reference = match.group(0).rstrip(".,;:!?)]]}>")
            add_reference(reference)
    return paths


class _HTMLDestinationParser(HTMLParser):
    _VOID_ELEMENTS = {
        "area",
        "base",
        "br",
        "col",
        "embed",
        "hr",
        "img",
        "input",
        "link",
        "meta",
        "param",
        "source",
        "track",
        "wbr",
    }

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.destinations: list[str] = []
        self.visible_text: list[str] = []
        self._elements: list[tuple[str, bool]] = []

    @property
    def hidden(self) -> bool:
        return any(hidden for _, hidden in self._elements)

    def handle_starttag(
        self,
        tag: str,
        attrs: list[tuple[str, str | None]],
    ) -> None:
        normalized_tag = tag.casefold()
        normalized_attrs = {name.casefold(): value for name, value in attrs}
        hides_content = (
            normalized_tag in {"script", "style", "template"}
            or "hidden" in normalized_attrs
            or "inert" in normalized_attrs
            or (normalized_attrs.get("aria-hidden") or "").strip().casefold() == "true"
        )
        hidden = self.hidden or hides_content
        if normalized_tag == "a" and not hidden:
            href = normalized_attrs.get("href")
            if href is not None:
                self.destinations.append(href)
        if normalized_tag not in self._VOID_ELEMENTS:
            self._elements.append((normalized_tag, hides_content))

    def handle_endtag(self, tag: str) -> None:
        normalized_tag = tag.casefold()
        for index in range(len(self._elements) - 1, -1, -1):
            if self._elements[index][0] == normalized_tag:
                del self._elements[index:]
                break

    def handle_data(self, data: str) -> None:
        if not self.hidden:
            self.visible_text.append(data)


def _feed_html(parser: _HTMLDestinationParser, text: str) -> None:
    try:
        parser.feed(text)
    except (AssertionError, ValueError):
        pass


def _close_html(parser: _HTMLDestinationParser) -> None:
    try:
        parser.close()
    except (AssertionError, ValueError):
        pass


def _inline_visible_text(
    children: list[Any],
    html_parser: _HTMLDestinationParser | None = None,
) -> str:
    visible: list[str] = []
    if html_parser is None:
        html_parser = _HTMLDestinationParser()
    for child in children:
        if child.type == "text" and not html_parser.hidden:
            visible.append(child.content)
        elif child.type in {"softbreak", "hardbreak"} and not html_parser.hidden:
            visible.append("\n")
        elif child.type == "html_inline":
            before = len(html_parser.visible_text)
            _feed_html(html_parser, child.content)
            visible.extend(html_parser.visible_text[before:])
        # CommonMark image alt text and code spans are not visible policy prose.
    return "".join(visible)


def _visible_markdown_text(text: str) -> str:
    """Return rendered prose from a CommonMark parse, excluding code and images."""
    visible: list[str] = []
    html_parser = _HTMLDestinationParser()
    for token in MARKDOWN.parse(text):
        if token.type == "inline":
            visible.append(_inline_visible_text(token.children or [], html_parser))
            visible.append("\n")
        elif token.type == "html_block":
            before = len(html_parser.visible_text)
            _feed_html(html_parser, token.content)
            visible.extend(html_parser.visible_text[before:])
            visible.append("\n")
    before = len(html_parser.visible_text)
    _close_html(html_parser)
    visible.extend(html_parser.visible_text[before:])
    return "".join(visible)


def _visible_link_destinations(text: str) -> list[str]:
    """Extract CommonMark links and HTML anchors, excluding images and code."""
    destinations: list[str] = []
    html_parser = _HTMLDestinationParser()
    for token in MARKDOWN.parse(text):
        if token.type == "inline":
            for child in token.children or []:
                if child.type == "link_open" and not html_parser.hidden:
                    destination = child.attrGet("href")
                    if destination is not None:
                        destinations.append(destination)
                elif child.type == "html_inline":
                    before = len(html_parser.destinations)
                    _feed_html(html_parser, child.content)
                    destinations.extend(html_parser.destinations[before:])
        elif token.type == "html_block":
            before = len(html_parser.destinations)
            _feed_html(html_parser, token.content)
            destinations.extend(html_parser.destinations[before:])
    _close_html(html_parser)
    return destinations


def _visible_headings(text: str) -> set[str]:
    headings: set[str] = set()
    html_parser = _HTMLDestinationParser()
    in_heading = False
    for token in MARKDOWN.parse(text):
        if token.type == "heading_open":
            in_heading = True
        elif token.type == "inline":
            visible = _inline_visible_text(token.children or [], html_parser)
            if in_heading and visible:
                headings.add(visible)
            in_heading = False
        elif token.type == "html_block":
            _feed_html(html_parser, token.content)
        elif token.type == "heading_close":
            in_heading = False
    _close_html(html_parser)
    return headings


def _markdown_table_cells(line: str) -> list[str]:
    return [
        cell.replace(r"\|", "|").strip()
        for cell in re.split(r"(?<!\\)\|", line.strip("|"))
    ]


def _msp045_structure_errors(rel: str, text: str) -> list[str]:
    if rel != MSP045_CONTRACT_PATH:
        return []

    body = _markdown_body(text)
    lines = body.splitlines()
    headings: list[tuple[str, int]] = []
    tokens = MARKDOWN.parse(body)
    for index, token in enumerate(tokens[:-1]):
        if token.type != "heading_open" or token.map is None:
            continue
        inline = tokens[index + 1]
        if inline.type == "inline":
            headings.append((inline.content, token.map[0]))

    errors: list[str] = []
    for heading, key_column in MSP045_NORMATIVE_TABLE_KEYS.items():
        matches = [line for title, line in headings if title == heading]
        if len(matches) != 1:
            errors.append(
                f"{rel}: normative heading {heading!r} must appear exactly once"
            )
            continue

        start = matches[0] + 1
        end = min(
            (line for _, line in headings if line > matches[0]),
            default=len(lines),
        )
        table_blocks: list[list[str]] = []
        line_index = start
        while line_index < end:
            if not lines[line_index].startswith("|"):
                line_index += 1
                continue
            block: list[str] = []
            while line_index < end and lines[line_index].startswith("|"):
                block.append(lines[line_index])
                line_index += 1
            table_blocks.append(block)

        if len(table_blocks) != 1:
            errors.append(
                f"{rel}: {heading}: normative heading must contain exactly one table"
            )
            continue
        table = table_blocks[0]
        if len(table) < 3:
            errors.append(f"{rel}: {heading}: normative table is incomplete")
            continue

        headers = _markdown_table_cells(table[0])
        separator = _markdown_table_cells(table[1])
        if (
            len(headers) != len(separator)
            or not all(re.fullmatch(r":?-{3,}:?", cell) for cell in separator)
            or key_column not in headers
        ):
            errors.append(f"{rel}: {heading}: normative table header is invalid")
            continue

        key_index = headers.index(key_column)
        seen_keys: set[str] = set()
        for row in table[2:]:
            values = _markdown_table_cells(row)
            if len(values) != len(headers):
                errors.append(f"{rel}: {heading}: normative table row is malformed")
                continue
            raw_key = values[key_index]
            key = (
                raw_key[1:-1]
                if raw_key.startswith("`") and raw_key.endswith("`")
                else raw_key
            )
            if key in seen_keys:
                errors.append(
                    f"{rel}: {heading}: duplicate normative table key {key!r}"
                )
            seen_keys.add(key)

    return errors


def _contains_summary_normative_requirements(text: str) -> bool:
    visible = _visible_markdown_text(text)
    return (
        SUMMARY_NORMATIVE_PATTERN.search(visible) is not None
        or SUMMARY_IMPERATIVE_PATTERN.search(visible) is not None
    )


def _policy_text_variants(text: str, *, markdown: bool) -> set[str]:
    variants = _reference_text_variants(text)
    if markdown:
        variants.update(
            {
                _visible_markdown_text(text),
                _visible_markdown_text(_fully_decode_reference(text)),
            }
        )
    return variants


def _platform_normative_copy_targets(
    text: str,
    platform_snapshot: dict[str, Any] | None,
) -> set[str]:
    if platform_snapshot is None:
        return set()

    def fingerprints(value: str) -> set[str] | None:
        words = re.findall(r"[a-z0-9]+", _visible_markdown_text(value).casefold())
        result: set[str] = set()
        for index in range(len(words) - MIN_PLATFORM_COPY_WORDS + 1):
            window = " ".join(words[index : index + MIN_PLATFORM_COPY_WORDS])
            if len(window) < MIN_PLATFORM_COPY_CHARACTERS:
                continue
            result.add(hashlib.sha256(window.encode("utf-8")).hexdigest())
            if len(result) > MAX_PLATFORM_FINGERPRINT_WINDOWS:
                return None
        return result

    page_fingerprints = fingerprints(_markdown_body(text))
    if page_fingerprints is None:
        return set(platform_snapshot["source_contents"])
    copied: set[str] = set()
    for target, source_content in platform_snapshot["source_contents"].items():
        source_fingerprints = fingerprints(source_content)
        if source_fingerprints is None or page_fingerprints & source_fingerprints:
            copied.add(target)
    return copied


def _contains_non_link_platform_url(text: str) -> bool:
    visible = _visible_markdown_text(text)
    return re.search(
        rf"(?:https?:)?//(?:www\.)?github\.com/{re.escape(PLATFORM_REPO)}/"
        r"[^\s<>\"']*docs/platform/[^\s<>\"']+\.md\b",
        visible,
        re.IGNORECASE,
    ) is not None


def _platform_links(text: str) -> list[tuple[str, str, bool]]:
    """Return visible platform destinations and whether each is exactly canonical."""
    links: list[tuple[str, str, bool]] = []
    repo_owner, repo_name = PLATFORM_REPO.split("/", 1)
    for destination in _visible_link_destinations(text):
        decoded = _fully_decode_reference(destination).replace("\\", "/")
        host_root = decoded.startswith("/") and not decoded.startswith("//")
        parsed_value = "https:" + decoded if decoded.startswith("//") else decoded
        try:
            parsed = urlsplit(parsed_value)
            hostname = parsed.hostname
            port = parsed.port
        except ValueError:
            continue
        if not host_root and (
            hostname is None
            or hostname.rstrip(".").casefold()
            not in {
                "github.com",
                "www.github.com",
                "raw.githubusercontent.com",
            }
        ):
            continue

        normalized_path = posixpath.normpath(parsed.path)
        segments = [segment for segment in normalized_path.split("/") if segment]
        if len(segments) < 6:
            continue
        if segments[0].casefold() != repo_owner.casefold() or segments[
            1
        ].casefold() != repo_name.casefold():
            continue

        raw_host = (
            hostname is not None
            and hostname.rstrip(".").casefold() == "raw.githubusercontent.com"
        )
        ref_start = 2 if raw_host else 3
        platform_index = next(
            (
                index
                for index in range(ref_start + 1, len(segments) - 1)
                if segments[index].casefold() == "docs"
                and segments[index + 1].casefold() == "platform"
            ),
            None,
        )
        if platform_index is None:
            continue
        ref = "/".join(segments[ref_start:platform_index])
        target = "docs/platform/" + "/".join(segments[platform_index + 2 :])
        if not target.casefold().endswith(".md"):
            continue
        canonical_url = (
            f"https://github.com/{PLATFORM_REPO}/blob/{ref}/{target}"
        )
        canonical = (
            destination == canonical_url
            and decoded == destination
            and parsed.scheme == "https"
            and parsed.netloc == "github.com"
            and port is None
            and parsed.username is None
            and parsed.password is None
            and not parsed.query
            and not parsed.fragment
            and parsed.path == normalized_path
            and segments[0] == repo_owner
            and segments[1] == repo_name
            and not raw_host
            and segments[2] == "blob"
            and platform_index == 4
            and re.fullmatch(r"[0-9a-f]{40}", ref) is not None
            and re.fullmatch(r"docs/platform/[A-Za-z0-9._/-]+\.md", target)
            is not None
        )
        links.append((ref, target, canonical))
    return links


def _contains_candidate_destination(text: str, source_rel: str) -> bool:
    root = CANDIDATE_API_ROOT.as_posix()
    return any(
        path == root or path.startswith(root + "/")
        for path in _normalized_reference_paths(text, source_rel)
    )


def _contains_visible_candidate_destination(text: str, source_rel: str) -> bool:
    return any(
        _contains_candidate_destination(destination, source_rel)
        for destination in _visible_link_destinations(text)
    )


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


def _provenance_fingerprint_exempt_spans(
    text: str, rel: str
) -> tuple[tuple[int, int], ...]:
    spans = list(git_fingerprint_exempt_spans(text))
    for fingerprint in MSP055_PROVENANCE_TEXT_FINGERPRINTS.get(rel, set()):
        pattern = re.compile(
            rf"(?<![0-9A-Fa-f]){re.escape(fingerprint)}(?![0-9A-Fa-f])"
        )
        spans.extend(match.span() for match in pattern.finditer(text))
    return tuple(sorted(spans))


def _privacy_errors(text: str, rel: str, *, category_only: bool = False) -> list[str]:
    errors: list[str] = []
    structured_fingerprint_variants = {text, _fully_decode_reference(text)}

    def add(category: str, line: int | None = None) -> None:
        location = rel if category_only or line is None else f"{rel}:{line}"
        errors.append(f"{location}: {category}")

    def assignment_value(value: str) -> str:
        normalized = value.strip()
        if normalized.endswith(","):
            normalized = normalized[:-1].rstrip()
        if (
            len(normalized) >= 2
            and normalized[0] == normalized[-1]
            and normalized[0] in {"\"", "'"}
        ):
            normalized = normalized[1:-1]
        return normalized

    for variant in _reference_text_variants(text):
        source_positions_valid = variant == text
        if PEM_BLOCK_PATTERN.search(variant):
            add("PEM block marker found in publishable content")
        if MAC_ADDRESS_PATTERN.search(variant):
            add("MAC address found in publishable content")
        if variant in structured_fingerprint_variants:
            exemptions = _provenance_fingerprint_exempt_spans(variant, rel)
            exemption_index = 0
            for match in FULL_FINGERPRINT_PATTERN.finditer(variant):
                while (
                    exemption_index < len(exemptions)
                    and exemptions[exemption_index][1] <= match.start()
                ):
                    exemption_index += 1
                if exemption_index == len(exemptions):
                    add("full fingerprint or raw SKI found in publishable content")
                    break
                start, end = exemptions[exemption_index]
                if not (start <= match.start() and match.end() <= end):
                    add("full fingerprint or raw SKI found in publishable content")
                    break
        if PRIVATE_PATH_PATTERN.search(variant):
            add("private or identifying filesystem path found")
        for match in PRIVATE_ARTIFACT_FIELD_PATTERN.finditer(variant):
            line = text.count("\n", 0, match.start()) + 1 if source_positions_valid else None
            add("private artifact location/reference field is forbidden", line)
        for match in PRIVATE_ARTIFACT_RETAINED_PATTERN.finditer(variant):
            value = assignment_value(match.group(1))
            if SAFE_RETAINED_VALUE_PATTERN.fullmatch(value) is None:
                line = (
                    text.count("\n", 0, match.start()) + 1
                    if source_positions_valid
                    else None
                )
                add("private artifact retained value must be yes or no", line)
        for match in SENSITIVE_FIELD_PATTERN.finditer(variant):
            value = assignment_value(match.group(2))
            if SAFE_REDACTED_VALUE_PATTERN.fullmatch(value) is None:
                line = (
                    variant.count("\n", 0, match.start()) + 1
                    if source_positions_valid
                    else None
                )
                category = "populated sensitive field"
                if not category_only:
                    category += f" {match.group(1).lower()!r}"
                add(category, line)
        for match in RAW_EEBUS_ID_PATTERN.finditer(variant):
            value = match.group(1)
            if SAFE_REDACTED_VALUE_PATTERN.fullmatch(value) is None:
                line = (
                    variant.count("\n", 0, match.start()) + 1
                    if source_positions_valid
                    else None
                )
                add("populated raw SKI or SHIP ID", line)
        for match in IPV4_CANDIDATE_PATTERN.finditer(variant):
            if classify_ipv4(match.group(0)) == "private network":
                line = (
                    variant.count("\n", 0, match.start()) + 1
                    if source_positions_valid
                    else None
                )
                add("private IPv4 address found", line)
        for match in IPV6_CANDIDATE_PATTERN.finditer(variant):
            candidate = match.group(0)
            if classify_ipv6(candidate) == "private network":
                line = (
                    variant.count("\n", 0, match.start()) + 1
                    if source_positions_valid
                    else None
                )
                add("private or local IPv6 address found", line)
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
    markdown = PurePosixPath(rel).suffix.lower() in MARKDOWN_SUFFIXES
    for variant in _policy_text_variants(text, markdown=markdown):
        source_positions_valid = variant == text
        for line_number, line in enumerate(variant.splitlines(), start=1):
            if RESTRICTED_SOURCE_PATTERN.search(line) is None:
                continue
            if ALLOWED_RESTRICTED_POLICY_PATTERN.search(line) is not None:
                continue
            location = (
                rel
                if category_only or not source_positions_valid
                else f"{rel}:{line_number}"
            )
            errors.append(f"{location}: restric" "ted-source contamination marker found")
    return errors


def _premature_claim_errors(text: str, rel: str) -> list[str]:
    markdown = PurePosixPath(rel).suffix.lower() in MARKDOWN_SUFFIXES
    variants = _policy_text_variants(text, markdown=markdown)
    errors: list[str] = []
    if any(PREMATURE_COMPLETION_PATTERN.search(variant) for variant in variants):
        errors.append(f"{rel}: premature docs milestone or code-doc absence claim")
    if any(PREMATURE_CONSUMER_PATTERN.search(variant) for variant in variants):
        errors.append(f"{rel}: premature gateway or consumer availability claim")
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
    diagnostics = machine_publication_diagnostics(result)
    allowed_fingerprints = MSP055_PROVENANCE_MACHINE_FINGERPRINTS.get(rel)
    if allowed_fingerprints is not None:
        actual_fingerprints = set()
        for variant in {text, _fully_decode_reference(text)}:
            actual_fingerprints.update(
                match.group(0).lower()
                for match in PROVENANCE_IDENTIFIER_PATTERN.finditer(variant)
            )
        sanitized = text
        for fingerprint in allowed_fingerprints:
            sanitized = re.sub(
                rf"(?<![0-9A-Fa-f]){re.escape(fingerprint)}(?![0-9A-Fa-f])",
                "x" * 40,
                sanitized,
            )
        sanitized_result = decode_machine_json(sanitized.encode("utf-8"))
        sanitized_diagnostics = machine_publication_diagnostics(sanitized_result)
        if (
            actual_fingerprints == allowed_fingerprints
            and "private identifier" not in sanitized_diagnostics
        ):
            diagnostics.discard("private identifier")
    errors = [
        f"{rel}: {category}"
        for category in sorted(diagnostics)
    ]
    if result.status not in {expected_status, NESTING_TOO_DEEP}:
        errors.append(f"{rel}: machine publication boundary")
    return errors


def _lexical_publication_reference(value: str) -> bool:
    path = PurePosixPath(value)
    return (
        bool(value)
        and value == value.strip()
        and "\\" not in value
        and "%" not in value
        and not path.is_absolute()
        and ".." not in path.parts
        and posixpath.normpath(value) == value
        and re.fullmatch(r"[A-Za-z0-9._/-]+", value) is not None
        and path.suffix.lower() in MARKDOWN_SUFFIXES
    )


def _pages_like_key(value: str) -> bool:
    value = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", value)
    words = {
        word
        for word in re.split(r"[^a-z0-9]+", value.casefold())
        if word
    }
    return bool(
        words
        & {"document", "documents", "file", "files", "page", "pages", "path", "paths"}
    )


def _json_publication_references(value: Any) -> list[str]:
    references: list[str] = []
    if isinstance(value, dict):
        for key, item in value.items():
            if (
                isinstance(key, str)
                and _pages_like_key(key)
                and isinstance(item, list)
                and item
                and all(
                    isinstance(reference, str)
                    and _lexical_publication_reference(reference)
                    for reference in item
                )
            ):
                references.extend(item)
            references.extend(_json_publication_references(item))
    elif isinstance(value, list):
        for item in value:
            references.extend(_json_publication_references(item))
    return references


def _xml_local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1].casefold()


def _xml_publication_references(document: ET.Element) -> list[str]:
    return [
        (element.text or "").strip()
        for element in document.iter()
        if _xml_local_name(element.tag) == "loc" and (element.text or "").strip()
    ]


def _bundle_publication_references(
    text: str,
    *,
    registered: bool = False,
) -> list[str] | None:
    references: list[str] = []
    publisher_marker = registered
    headers = {
        "[documents]",
        "[files]",
        "[pages]",
        "[paths]",
        "document",
        "document:",
        "documents:",
        "file",
        "file:",
        "files:",
        "page",
        "page:",
        "pages:",
        "path",
        "path:",
        "paths:",
    }
    for raw_line in text.removeprefix("\ufeff").splitlines():
        line = raw_line.strip()
        normalized_header = re.sub(r"\s*:\s*$", ":", line.casefold())
        header_fields = [
            field.strip().casefold()
            for field in re.split(r"[,|\t]", line)
        ]
        structured_header = (
            len(header_fields) > 1
            and header_fields[0] in {"document", "file", "page", "path"}
            and all(re.fullmatch(r"[a-z_ -]+", field) for field in header_fields)
        )
        if not line or line.startswith(("#", ";", "//")):
            continue
        if normalized_header in headers or structured_header:
            publisher_marker = True
            continue
        entry = re.sub(r"\s+(?:#|;|//).*$", "", line).rstrip()
        if _lexical_publication_reference(entry):
            references.append(entry)
            continue
        return None
    return references if publisher_marker and references else None


def _publication_artifact_shape(
    text: str,
    *,
    registered_bundle: bool = False,
) -> tuple[str | None, list[str]]:
    result = decode_machine_json(text.encode("utf-8"))
    if (
        result.status == COMPLETE
        and not result.duplicate_keys
        and isinstance(result.document, dict)
    ):
        references = _json_publication_references(result.document)
        if references:
            return "search", references

    if not re.search(r"<!DOCTYPE|<!ENTITY", text, re.IGNORECASE):
        try:
            document = ET.fromstring(text.removeprefix("\ufeff"))
        except ET.ParseError:
            document = None
        if document is not None and _xml_local_name(document.tag) in {
            "sitemapindex",
            "urlset",
        }:
            return "sitemap", _xml_publication_references(document)

    references = _bundle_publication_references(text, registered=registered_bundle)
    if references is not None:
        return "bundle", references
    return None, []


def _classify_publication_artifact(text: str) -> str | None:
    channel, _ = _publication_artifact_shape(text)
    return channel


def _discover_publication_artifacts(
    root: Path,
    configuration: dict[str, Any],
) -> dict[str, str]:
    discovered: dict[str, str] = {}
    registered: dict[str, str] = configuration["registered"]
    for rel, channel in registered.items():
        artifact = root / rel
        if artifact.is_file() and not artifact.is_symlink():
            discovered[rel] = channel

    for path in sorted(root.rglob("*")):
        if (
            not path.is_file()
            or path.is_symlink()
            or ".git" in path.parts
            or ".pytest_cache" in path.parts
            or "__pycache__" in path.parts
        ):
            continue
        rel = _rel(path, root)
        if rel in discovered:
            continue
        if path.suffix.lower() in MARKDOWN_SUFFIXES:
            continue
        try:
            size = path.stat().st_size
        except OSError:
            continue
        if size > MAX_REPOSITORY_TEXT_SCAN_BYTES:
            continue
        try:
            raw = path.read_bytes()
        except OSError:
            continue
        if b"\0" in raw:
            continue
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            continue
        channel = _classify_publication_artifact(text)
        if channel is not None:
            discovered[rel] = channel
    return discovered


def _canonical_publication_entries(entries: list[str]) -> bool:
    return entries == sorted(entries, key=lambda value: value.encode("utf-8"))


def _is_stable_repository_reference(root: Path, value: str) -> bool:
    path = PurePosixPath(value)
    if (
        not value
        or value != value.strip()
        or "\\" in value
        or "%" in value
        or path.is_absolute()
        or ".." in path.parts
        or posixpath.normpath(value) != value
        or re.fullmatch(r"[A-Za-z0-9._/-]+", value) is None
        or _is_candidate_path(value)
    ):
        return False
    if value not in ROOT_MD and (not path.parts or path.parts[0] not in PUBLISHABLE_DOMAINS):
        return False

    artifact = root.joinpath(*path.parts)
    if not artifact.is_file() or artifact.is_symlink():
        return False
    if artifact.suffix.lower() in MARKDOWN_SUFFIXES:
        try:
            metadata, front_matter_error = _front_matter(_read(artifact))
        except UnicodeDecodeError:
            return False
        if front_matter_error is not None or metadata is None:
            return False
        if (
            metadata.get("publication_status") in NONPUBLISHABLE_PUBLICATION_STATUSES
            or metadata.get("candidate_output") == "true"
            or metadata.get("hypothesis_status") in {"blocked", "draft", "withdrawn"}
        ):
            return False
    return True


def _stable_artifact_references(
    root: Path,
    text: str,
    rel: str,
    channel: str,
) -> tuple[list[str], list[str]]:
    invalid = [f"{rel}: invalid stable publication artifact"]
    if channel == "search":
        result = decode_machine_json(text.encode("utf-8"))
        document = result.document
        if result.status != COMPLETE or result.duplicate_keys:
            return [], invalid
        if not isinstance(document, dict) or set(document) != {"pages"}:
            return [], invalid
        pages = document["pages"]
        if (
            not isinstance(pages, list)
            or not pages
            or any(not isinstance(page, str) for page in pages)
            or len(set(pages)) != len(pages)
            or any(not _is_stable_repository_reference(root, page) for page in pages)
        ):
            return [], invalid
        if not _canonical_publication_entries(pages):
            return [], [f"{rel}: non-canonical publication entry ordering"]
        return pages, []

    if channel == "sitemap":
        if re.search(r"<!DOCTYPE|<!ENTITY", text, re.IGNORECASE):
            return [], invalid
        try:
            document = ET.fromstring(text)
        except ET.ParseError:
            return [], invalid
        url_tag = f"{{{SITEMAP_NAMESPACE}}}url"
        loc_tag = f"{{{SITEMAP_NAMESPACE}}}loc"
        urls = list(document)
        if (
            document.tag != f"{{{SITEMAP_NAMESPACE}}}urlset"
            or document.attrib
            or not urls
            or (document.text or "").strip()
            or any(url.tag != url_tag or url.attrib or len(url) != 1 for url in urls)
        ):
            return [], invalid
        references: list[str] = []
        for url in urls:
            loc = url[0]
            value = loc.text or ""
            if (
                loc.tag != loc_tag
                or loc.attrib
                or len(loc)
                or (url.text or "").strip()
                or (loc.tail or "").strip()
                or (url.tail or "").strip()
                or not _is_stable_repository_reference(root, value)
            ):
                return [], invalid
            references.append(value)
        if len(set(references)) != len(references):
            return [], invalid
        if not _canonical_publication_entries(references):
            return [], [f"{rel}: non-canonical publication entry ordering"]
        return references, []

    references = _bundle_publication_references(text, registered=True)
    if (
        not references
        or len(set(references)) != len(references)
        or any(not _is_stable_repository_reference(root, value) for value in references)
    ):
        return [], invalid
    if not _canonical_publication_entries(references):
        return [], [f"{rel}: non-canonical publication entry ordering"]
    return references, []


def _provenance_errors(
    root: Path,
    rel: str,
    text: str,
    metadata: dict[str, str],
    *,
    fixture_mode: bool,
) -> list[str]:
    errors: list[str] = []
    expected_protocol_hash = PRODUCTION_REVIEWED_PROTOCOL_ARTIFACT_SHA256.get(rel)
    if (
        expected_protocol_hash is not None
        and hashlib.sha256(text.encode("utf-8")).hexdigest() != expected_protocol_hash
    ):
        errors.append(f"{rel}: reviewed protocol artifact differs")

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
                continue
            supported_claim = (
                metadata.get("owner_domain") == "architecture"
                and metadata.get("publication_status") == "active"
                and metadata.get("hypothesis_status") == "publishable"
            )
            if not supported_claim:
                continue
            try:
                evidence_text = _read(evidence_path)
            except UnicodeDecodeError:
                evidence_metadata = None
            else:
                evidence_metadata, _ = _front_matter(evidence_text)
            evidence_body_hash = (
                hashlib.sha256(_markdown_body(evidence_text).encode("utf-8")).hexdigest()
                if evidence_metadata is not None
                else ""
            )
            reviewed_evidence_metadata = PRODUCTION_REVIEWED_EVIDENCE.get(
                evidence_id, {}
            ).get(evidence_body_hash)
            if reviewed_evidence_metadata is None and fixture_mode:
                reviewed_evidence_metadata = FIXTURE_REVIEWED_EVIDENCE.get(
                    evidence_id, {}
                ).get(evidence_body_hash)
            evidence_values = (
                {
                    value.strip()
                    for value in evidence_metadata.get("evidence_ids", "").split(",")
                    if value.strip()
                }
                if evidence_metadata is not None
                else set()
            )
            expected_source = f"{REPO_ID}:evidence/{evidence_id}.md"
            if evidence_metadata is None or any(
                (
                    evidence_metadata.get("canonical_source") != expected_source,
                    evidence_metadata.get("owner_domain") != "evidence",
                    evidence_metadata.get("publication_status") != "publishable",
                    evidence_metadata.get("claim_status") != "evidence-backed",
                    evidence_metadata.get("source_class") not in EVIDENCE_SOURCE_CLASSES,
                    evidence_metadata.get("hypothesis_status") != "publishable",
                    evidence_id not in evidence_values,
                    reviewed_evidence_metadata is None,
                    reviewed_evidence_metadata is not None
                    and evidence_metadata != reviewed_evidence_metadata,
                )
            ):
                errors.append(
                    f"{rel}: supported claim evidence is not publishable and evidence-backed: "
                    f"{evidence_path.name}"
                )

    return errors


def _bounded_repository_text(path: Path, rel: str) -> tuple[str | None, list[str]]:
    try:
        size = path.stat().st_size
    except OSError:
        return None, [f"{rel}: repository artifact is unreadable"]
    if size > MAX_REPOSITORY_TEXT_SCAN_BYTES:
        return None, [f"{rel}: repository artifact exceeds scan size limit"]
    try:
        raw = path.read_bytes()
    except OSError:
        return None, [f"{rel}: repository artifact is unreadable"]
    if b"\0" in raw:
        return None, []
    try:
        return raw.decode("utf-8"), []
    except UnicodeDecodeError:
        return None, []


def _repository_lstat_preflight(
    root: Path,
) -> tuple[list[Path], set[Path], list[str]]:
    regular_files: list[Path] = []
    symlinks: set[Path] = set()
    errors: list[str] = []
    pending = [root]

    while pending:
        directory = pending.pop()
        try:
            with os.scandir(directory) as entries:
                children = sorted(entries, key=lambda entry: os.fsencode(entry.name))
        except OSError:
            errors.append(f"{_rel(directory, root)}: repository directory is unreadable")
            continue

        for entry in children:
            path = Path(entry.path)
            rel = _rel(path, root)
            if rel == ".git" or rel.startswith(".git/"):
                continue
            try:
                mode = entry.stat(follow_symlinks=False).st_mode
            except OSError:
                errors.append(f"{rel}: repository artifact is unreadable")
                continue
            if stat.S_ISLNK(mode):
                symlinks.add(path)
                errors.append(f"{rel}: symlinks are forbidden")
            elif stat.S_ISDIR(mode):
                pending.append(path)
            elif stat.S_ISREG(mode):
                regular_files.append(path)

    return regular_files, symlinks, errors


def check_repository(root: Path, *, fixture_mode: bool = False) -> list[str]:
    errors: list[str] = []
    root = root.absolute()
    stable_navigation_pages: dict[str, str] = {}
    channel_pages: dict[str, set[str]] = {
        channel: set() for channel in CANDIDATE_API_CHANNELS
    }

    try:
        root_mode = root.lstat().st_mode
    except OSError:
        return [".: repository root is unreadable"]
    if stat.S_ISLNK(root_mode) or not stat.S_ISDIR(root_mode):
        return [".: repository root must be a non-symlink directory"]

    regular_files, symlinks, preflight_errors = _repository_lstat_preflight(root)
    errors.extend(preflight_errors)
    if errors:
        return sorted(set(errors), key=lambda value: value.encode("utf-8"))

    platform_snapshot, snapshot_errors = _load_platform_snapshot(root)
    errors.extend(snapshot_errors)
    if platform_snapshot is not None:
        for channel, pages in platform_snapshot["manifest_channel_pages"].items():
            channel_pages[channel].update(pages)
    publication_channels, publication_channel_errors = _load_publication_channels(root)
    errors.extend(publication_channel_errors)

    for path in sorted(regular_files, key=lambda value: os.fsencode(_rel(value, root))):
        if ".pytest_cache" in path.parts or "__pycache__" in path.parts:
            continue
        rel = _rel(path, root)
        try:
            file_stat = path.lstat()
        except OSError:
            errors.append(f"{rel}: repository artifact is unreadable")
            continue
        if not stat.S_ISREG(file_stat.st_mode):
            errors.append(f"{rel}: repository artifact is not a regular file")
            continue
        if file_stat.st_size > MAX_REPOSITORY_TEXT_SCAN_BYTES:
            errors.append(f"{rel}: repository artifact exceeds scan size limit")
    if errors:
        return sorted(set(errors), key=lambda value: value.encode("utf-8"))

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
        if not isinstance(workflow_data, dict) or workflow_data.get("permissions") != {
            "contents": "read"
        }:
            errors.append(".github/workflows/docs-ci.yml: permissions must be contents read")
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
                    if not isinstance(step, dict):
                        continue
                    action = step.get("uses")
                    if isinstance(action, str) and re.fullmatch(r"[^@]+@[0-9a-f]{40}", action) is None:
                        errors.append(".github/workflows/docs-ci.yml: action refs must be immutable")
                    if isinstance(step, dict) and isinstance(step.get("run"), str):
                        run_commands.append(step["run"].strip())
                        if step["run"].strip() in {
                            "./scripts/ci_local.sh",
                            "python -m pip install --only-binary=:all: --require-hashes -r requirements-ci.txt",
                        } and any(key in step for key in ("if", "continue-on-error", "shell")):
                            errors.append(
                                ".github/workflows/docs-ci.yml: validator steps must be unconditional"
                            )
                checkout = next(
                    (
                        step for step in steps
                        if isinstance(step, dict)
                        and str(step.get("uses", "")).startswith("actions/checkout@")
                    ),
                    {},
                )
                setup_python = next(
                    (
                        step for step in steps
                        if isinstance(step, dict)
                        and str(step.get("uses", "")).startswith("actions/setup-python@")
                    ),
                    {},
                )
                if checkout.get("with", {}).get("persist-credentials") is not False:
                    errors.append(".github/workflows/docs-ci.yml: checkout credentials must not persist")
                if setup_python.get("with", {}).get("python-version") != "3.12.10":
                    errors.append(".github/workflows/docs-ci.yml: Python must be exactly 3.12.10")
        if "./scripts/ci_local.sh" not in run_commands:
            errors.append(".github/workflows/docs-ci.yml: must invoke ./scripts/ci_local.sh exactly")
        if (
            "python -m pip install --only-binary=:all: --require-hashes -r requirements-ci.txt"
            not in run_commands
        ):
            errors.append(
                ".github/workflows/docs-ci.yml: must install hash-locked validator dependencies"
            )

    requirements = root / "requirements-ci.txt"
    if requirements in symlinks or not requirements.exists():
        errors.append("requirements-ci.txt: missing pinned validator dependencies")
    elif _read(requirements) != LOCKED_REQUIREMENTS:
        errors.append("requirements-ci.txt: validator dependency pins differ")

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
        errors.extend(_msp045_structure_errors(rel, page_text))
        errors.extend(
            _provenance_errors(
                root,
                rel,
                page_text,
                metadata,
                fixture_mode=fixture_mode,
            )
        )
        errors.extend(
            _active_architecture_errors(
                rel,
                page_text,
                metadata,
                fixture_mode=fixture_mode,
            )
        )
        errors.extend(_supported_api_errors(rel, page_text, metadata))
        errors.extend(_candidate_api_errors(rel, metadata))
        errors.extend(_milestone_errors(rel, metadata))
        candidate_api = _is_candidate_api(rel, metadata)
        for channel in CANDIDATE_API_CHANNELS:
            value = metadata.get(channel)
            if value is not None and value not in {"true", "false"}:
                errors.append(f"{rel}: {channel} must be the string 'true' or 'false'")
            if value == "true":
                if candidate_api or not _is_stable_repository_reference(root, rel):
                    errors.append(f"{rel}: nonpublishable page cannot enable {channel}")
                else:
                    channel_pages[channel].add(rel)
        if fixture_mode:
            fixture_body_hash = hashlib.sha256(
                _markdown_body(page_text).encode("utf-8")
            ).hexdigest()
            if FIXTURE_REVIEWED_ACTIVE_ARCHITECTURE.get(fixture_body_hash) == metadata:
                for channel in CANDIDATE_API_CHANNELS:
                    channel_pages[channel].add(rel)
        if not candidate_api:
            stable_navigation_pages[rel] = page_text

        platform_links = _platform_links(page_text)
        links = {(ref, target) for ref, target, _ in platform_links}
        targets = {f"{PLATFORM_REPO}:{target}" for _, target in links}
        declared_target = metadata.get("cross_seed_target")
        declared_mode = metadata.get("cross_seed_mode")
        declared_snapshot = metadata.get("cross_seed_snapshot")
        declares_cross_seed = any(
            value is not None
            for value in (declared_target, declared_mode, declared_snapshot)
        )
        copied_platform_targets = _platform_normative_copy_targets(
            page_text,
            platform_snapshot,
        )
        linked_target_paths = {
            target.split(":", 1)[1]
            for target in targets
            if ":" in target
        }
        if copied_platform_targets and (
            copied_platform_targets != linked_target_paths
            or declared_mode != "summary-only"
        ):
            errors.append(
                f"{rel}: platform-owned normative text requires canonical "
                "summary-only cross-seed policy"
            )
        if copied_platform_targets:
            errors.append(
                f"{rel}: summary-only cross-seed copies pinned platform source content"
            )
        if declares_cross_seed and _reviewed_cross_seed_claim(
            page_text,
            metadata,
            fixture_mode=fixture_mode,
        ) is None:
            errors.append(
                f"{rel}: cross-seed content is not in the reviewed claim registry"
            )
        if targets:
            all_links_canonical = all(canonical for _, _, canonical in platform_links)
            if not all_links_canonical:
                errors.append(
                    f"{rel}: platform URL must use canonical immutable commit/path form"
                )
            if len(targets) != 1:
                errors.append(f"{rel}: a page may cross-seed exactly one platform target")
            expected_target = next(iter(targets)) if len(targets) == 1 else None
            if declared_target != expected_target:
                errors.append(
                    f"{rel}: cross_seed_target must match the linked platform page {expected_target!r}"
                )
            if declared_mode != "summary-only":
                errors.append(f"{rel}: cross_seed_mode must be 'summary-only'")
            target_path = expected_target.split(":", 1)[1] if expected_target else None
            snapshot_match = (
                PLATFORM_SNAPSHOT_PATTERN.fullmatch(declared_snapshot)
                if isinstance(declared_snapshot, str)
                else None
            )
            link_consistent = (
                all_links_canonical
                and len(platform_links) == 1
                and len(links) == 1
                and next(iter(links))[1] == target_path
                and next(iter(links))[0] == PLATFORM_SNAPSHOT_REF
                and snapshot_match is not None
                and snapshot_match.group(1) == PLATFORM_SNAPSHOT_REF
                and snapshot_match.group(2) == target_path
            )
            if not link_consistent:
                errors.append(f"{rel}: cross-seed commit, path, and snapshot must match")
            if (
                platform_snapshot is None
                or target_path not in platform_snapshot["targets"]
                or platform_snapshot["repository"] != PLATFORM_REPO
                or platform_snapshot["commit"] != PLATFORM_SNAPSHOT_REF
            ):
                errors.append(
                    f"{rel}: cross-seed target is not an active canonical platform page "
                    f"at {PLATFORM_SNAPSHOT_REF}"
                )
            headings = {
                re.sub(r"[^a-z0-9]+", " ", heading.lower()).strip()
                for heading in _visible_headings(page_text)
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
            if _contains_summary_normative_requirements(_markdown_body(page_text)):
                errors.append(
                    f"{rel}: summary-only cross-seed contains normative requirements"
                )
        else:
            if _contains_non_link_platform_url(page_text):
                errors.append(
                    f"{rel}: cross_seed_target must match an actual Markdown or HTML anchor destination"
                )
            if (
                declared_target is not None
                or declared_mode is not None
                or declared_snapshot is not None
            ):
                errors.append(f"{rel}: cross-seed metadata requires a canonical platform link")

        errors.extend(_premature_claim_errors(page_text, rel))
        errors.extend(_restricted_source_errors(page_text, rel))

        if rel in ROOT_MD:
            errors.extend(_privacy_errors(page_text, rel))

    for rel, text in stable_navigation_pages.items():
        if _contains_visible_candidate_destination(text, rel):
            errors.append(f"{rel}: candidate API leaked into stable_navigation")
    navigation_references = {
        reference
        for source_rel, text in stable_navigation_pages.items()
        for destination in _visible_link_destinations(text)
        for reference in _normalized_reference_paths(destination, source_rel)
    }
    for required in sorted(channel_pages["stable_navigation"]):
        if required not in navigation_references:
            errors.append(
                f"{required}: stable_navigation true page is missing from stable navigation"
            )

    if publication_channels is not None:
        registered = publication_channels["registered"]
        discovered = _discover_publication_artifacts(root, publication_channels)
        for artifact_rel in sorted(registered, key=lambda value: value.encode("utf-8")):
            artifact = root / artifact_rel
            if not artifact.is_file() or artifact.is_symlink():
                errors.append(
                    f"{artifact_rel}: configured stable publication artifact is missing"
                )
        for artifact_rel, discovered_channel in sorted(discovered.items()):
            artifact = root / artifact_rel
            configured_channel = registered.get(artifact_rel)
            channel = configured_channel or discovered_channel
            if configured_channel is None:
                errors.append(f"{artifact_rel}: unregistered stable publication artifact")
            try:
                artifact_text = _read(artifact)
            except UnicodeDecodeError:
                errors.append(f"{artifact_rel}: invalid stable publication artifact")
                continue
            references, format_errors = _stable_artifact_references(
                root,
                artifact_text,
                artifact_rel,
                channel,
            )
            errors.extend(format_errors)
            _, discovered_references = _publication_artifact_shape(
                artifact_text,
                registered_bundle=configured_channel is not None,
            )
            required_pages = channel_pages.get(channel, set())
            missing = sorted(required_pages - set(references), key=lambda value: value.encode("utf-8"))
            undeclared = sorted(
                set(references) - required_pages,
                key=lambda value: value.encode("utf-8"),
            )
            if missing:
                errors.append(
                    f"{artifact_rel}: stable channel is missing required pages {missing}"
                )
            if configured_channel is not None and undeclared:
                errors.append(
                    f"{artifact_rel}: stable channel has undeclared pages {undeclared}"
                )
            candidate_references = references or discovered_references
            if any(
                _contains_candidate_destination(reference, artifact_rel)
                for reference in candidate_references
            ):
                errors.append(f"{artifact_rel}: candidate API leaked into {channel}")

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
                    registered_outputs = (
                        set(publication_channels["registered"])
                        if publication_channels is not None
                        else set()
                    )
                    if rel not in API_MACHINE_ARTIFACTS and rel not in registered_outputs:
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
                errors.extend(_premature_claim_errors(text, rel))

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
        if (
            ".git" in path.parts
            or ".pytest_cache" in path.parts
            or "__pycache__" in path.parts
        ):
            continue
        rel = _rel(path, root)
        errors.extend(_privacy_errors(rel, rel, category_only=True))
        errors.extend(_restricted_source_errors(rel, rel, category_only=True))
        if rel in API_MACHINE_ARTIFACTS or rel in STRUCTURED_SNAPSHOT_ARTIFACTS:
            continue
        text, scan_errors = _bounded_repository_text(path, rel)
        errors.extend(scan_errors)
        if text is None:
            continue
        errors.extend(_privacy_errors(text, rel))
        errors.extend(_restricted_source_errors(text, rel))

    restricted_policy = (root / "development" / "contributing.md")
    if restricted_policy.exists():
        text = _read(restricted_policy)
        if text.count(ALLOWED_RESTRICTED_POLICY_LINE) != 1:
            errors.append(
                "development/contributing.md: missing vendor_"
                "restricted quarantine marker"
            )
        if "Restricted material must not appear in public repositories" not in text:
            errors.append(
                "development/contributing.md: missing restric"
                "ted-source quarantine rule"
            )

    return sorted(set(errors), key=lambda value: value.encode("utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument(
        "--fixture-mode",
        action="store_true",
        help="accept the immutable synthetic MSP-DOCS-E2 contract fixture registry",
    )
    args = parser.parse_args()

    errors = check_repository(args.repo, fixture_mode=args.fixture_mode)
    for error in errors:
        print(error, file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
