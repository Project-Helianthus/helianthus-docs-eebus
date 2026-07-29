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
from typing import Any, Callable
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
    "api/_candidate/msp-06/helianthus.eebus.mcp.v1.schema.json",
    "api/_candidate/msp-06/helianthus.eebus.mcp.v1.raw.schema.json",
    "api/_candidate/msp-06/jcs-hash-vectors-v1.json",
    "api/_candidate/msp-0625/helianthus.eebus.mcp.v1.raw-feature.schema.json",
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
CANDIDATE_API_MACHINE_ARTIFACTS = {
    "api/_candidate/msp-06/helianthus.eebus.mcp.v1.schema.json",
    "api/_candidate/msp-06/helianthus.eebus.mcp.v1.raw.schema.json",
    "api/_candidate/msp-06/jcs-hash-vectors-v1.json",
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
MSP06_PROVENANCE_MACHINE_FINGERPRINTS = {
    "api/_candidate/msp-06/jcs-hash-vectors-v1.json": {
        "a" * 64,
        "b55af27c4bd5f02ebeca8f901b84d2940b22e7bea7230e4d06f275d903bfdd72",
        "fd16c106364021a01f7a014dbf9f6a2871051afc5eb7d313a5967f5346eb48f9",
        "d091f9c83c091f79652fe8786375b3fe4ce0861a56f5bfbafedbe431877ff0e8",
        "44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a",
        "bb80eb37329e0a7e980fe3638c9722c44ac3184f7488f20c28cf67ae0b5f4f96",
        "1dd1b393e6cd221850141f0fb4aa66e050abab7cd8fd32abffc8c3e8135b9555",
        "c88088abcd03a63a675b1b6886b67c9f44c4eff3e081fad3a7315dc8c4928ae9",
        "8ddc952deff2bd36eade164c45b2799d0b46851086f40a0acb0116f985c33395",
        "4ab875e3987cc60dd0fdc382a3d0063b86742bc2349be5831d96e3bf05b7918e",
    },
}
ISSUE68_AMENDMENT_REL = Path(
    "api/_candidate/msp-068-raw-operator-redaction-amendment.md"
)
ISSUE68_CURRENT_CONTRACT_RELS = (
    Path("api/_candidate/msp-06-eebus-mcp-v1.md"),
    Path("api/_candidate/raw-snapshot-view-v1.md"),
)
ISSUE68_M2_LOCKED_ARTIFACTS = {
    Path("api/eebusruntime-v1/reference.md"): (
        "a3265bf99558093d7330780921f7d8d5"
        "822f0bbd23a51f589a9ff7d67ee1e4f1"
    ),
    Path("api/eebusruntime-v1/manifest.json"): (
        "bbabab51cc0a0e833c645f51767e67a3"
        "4c0361ba61c45b0065ecfda55ed6c32f"
    ),
}
ISSUE68_G16_LOCKED_ARTIFACT = Path(
    "architecture/_candidate/msp-04b-first-trust-admin-local.md"
)
ISSUE68_G16_LOCKED_SHA256 = (
    "a374c244b7b20eef1caf6d307ec87932"
    "dfd6a1d83c7f8f1ceba6b04e7b10238e"
)
ISSUE68_STABLE_PROTOCOL = Path("protocols/ship-spine-overview.md")
ISSUE68_STABLE_PROTOCOL_SHA256 = (
    "734c5668cd1937b088cbb12c7c4dd6b7"
    "8c0fc76cc76873dc2d49092aded65b3b"
)
ISSUE68_REDACTED_SCHEMA_REL = Path(
    "api/_candidate/msp-06/helianthus.eebus.mcp.v1.schema.json"
)
ISSUE68_RAW_SCHEMA_REL = Path(
    "api/_candidate/msp-06/helianthus.eebus.mcp.v1.raw.schema.json"
)
ISSUE68_RAW_SNAPSHOT_REL = Path("api/_candidate/raw-snapshot-view-v1.md")
ISSUE68_OPAQUE_LIMITS = {
    "maxDepth": 3,
    "maxCanonicalBytesPerValue": 16384,
    "maxAggregateCanonicalBytes": 262144,
    "maxObservations": 256,
    "maxArrayItems": 32,
    "maxObjectProperties": 32,
    "maxStringBytes": 4096,
}
ISSUE68_SECRET_DENYLIST = [
    "private_key",
    "private_pem",
    "trust_store_bytes",
    "credential_token",
    "bearer_token",
    "session_token",
    "authentication_token",
    "cryptographic_secret",
]
ISSUE68_TOOL_NAMES = {
    "eebus.v1.runtime.status.get",
    "eebus.v1.services.list",
    "eebus.v1.services.get",
    "eebus.v1.sessions.list",
    "eebus.v1.sessions.get",
    "eebus.v1.topology.get",
    "eebus.v1.snapshot.capture",
    "eebus.v1.snapshot.drop",
    "eebus.v1.pairing.status.get",
}
ISSUE68_RAW_TYPE_FIELDS = {
    "ServiceV1": {
        "required": {
            "ski",
            "kind",
            "visible",
            "paired",
        },
        "optional": {
            "ship_id",
            "name",
            "identifier",
            "brand",
            "type",
            "model",
            "secondary_digest",
            "opaque",
        },
    },
    "DeviceV1": {
        "required": {"ski", "address", "type"},
        "optional": {"ship_id", "description", "metadata", "secondary_digest", "opaque"},
    },
    "EntityV1": {
        "required": {"device_address", "entity_address", "type"},
        "optional": {"description", "secondary_digest", "opaque"},
    },
    "FeatureV1": {
        "required": {
            "device_address",
            "entity_address",
            "feature_address",
            "type",
            "role",
        },
        "optional": {"description", "secondary_digest", "opaque"},
    },
    "UseCaseV1": {
        "required": {
            "context_address",
            "name",
            "actor",
        },
        "optional": {
            "resolved_role",
            "scenarios",
            "version",
            "availability",
            "document_subrevision",
            "secondary_digest",
            "opaque",
        },
    },
}
ISSUE68_REQUIRED_MARKERS = {
    "single namespace": "one initial MCP `eebus.v1.*` namespace",
    "authorized raw default": "authorized local/operator default is `mask_tier=raw`",
    "shareable redacted tier": "public/shareable export is explicit `mask_tier=redacted`",
    "boundary authorization": "authorization is enforced fail-closed at the boundary",
    "service fields": "service fields: SKI, SHIP ID, kind, visible, paired, name, identifier, brand, type, model",
    "device fields": "device fields: SKI, SHIP ID, address, type, description, metadata when present",
    "entity fields": "entity fields: device address, entity address, type, description",
    "feature fields": "feature fields: device address, entity address, feature address, type, role, description",
    "use-case fields": "use-case fields: context address, name, actor, optional resolved role, scenarios, version, availability, document subrevision",
    "unknown fields": "unknown protocol fields remain inspectable raw or opaque values in bounded objects with exactly `path`, `source`, and `value`",
    "operational identity metadata": "SKI, SHIP ID, SPINE addresses, and protocol metadata are operational data visible to the authorized local operator",
    "reference binding": "reference binding includes runtime, contract, tool, scope, mask_tier, auth_scope, and authorization boundary",
    "cross-tier rejection": "dereference rejects a mismatched mask_tier, auth_scope, or authorization boundary",
    "secret exclusion": "credential tokens, bearer tokens, session tokens, authentication tokens, and cryptographic secrets are forbidden in every tier",
    "reference exception": "server-generated opaque evidence references are allowed only in designated direct MCP response fields",
    "candidate ref exclusion": "`candidate_ref` is forbidden from the stable public API",
    "public identity redaction": "public/shareable artifacts redact stable identities",
}
ISSUE96_CANDIDATE_REL = Path(
    "protocols/_candidate/msp-096-spine13-hvac-model-erratum.md"
)
ISSUE96_EVIDENCE_RELS = (
    Path("evidence/EV-20260730-001.md"),
    Path("evidence/EV-20260730-002.md"),
)
ISSUE96_REQUIRED_MARKERS = {
    "issue link": "docs issue 96",
    "public implementation boundary": "public upstream implementation evidence",
    "spine 1.4 exclusion": "SPINE 1.4",
    "wholesale merge exclusion": "wholesale upstream-dev merge",
    "restricted material exclusion": "candidate must not use vendor-restricted specifications",
    "9970150 exclusion": "key-tag and update-engine changes are excluded",
    "setpoint model": "SetpointDescriptionDataType",
    "setpoint selector": "SetpointDescriptionListDataSelectorsType",
    "hvac description functions": "FunctionTypeHvacOperationModeDescriptionListData",
    "hvac relations": "HvacSystemFunctionSetpointRelationDataType",
    "selector hunk": "selector hunk only in `4f986b14324a0d9ed719121b82c2621d50f58303`",
    "baseline": "49 READ declared / 26 success / 23 failure",
    "classification boundary": "non_empty_reply_observed",
    "falsifier boundary": "typed-empty result is treated as a successful non-empty reply",
    "raw/redacted boundary": "raw/operator versus public-redacted rules remain unchanged",
}
ISSUE76_PROTOCOL_REL = Path(
    "protocols/_candidate/msp-0625-feature-data-acquisition.md"
)
ISSUE76_ARCHITECTURE_REL = Path(
    "architecture/_candidate/msp-0625-raw-feature-command-path.md"
)
ISSUE76_API_REL = Path(
    "api/_candidate/msp-0625-raw-feature-acquisition.md"
)
ISSUE76_POLICY_REL = Path("development/msp-0625-provenance-policy.md")
ISSUE76_DOCUMENT_RELS = (
    ISSUE76_PROTOCOL_REL,
    ISSUE76_ARCHITECTURE_REL,
    ISSUE76_API_REL,
    ISSUE76_POLICY_REL,
)
ISSUE76_SCHEMA_REL = Path(
    "api/_candidate/msp-0625/helianthus.eebus.mcp.v1.raw-feature.schema.json"
)
ISSUE76_TOOL_NAMES = {
    "eebus.v1.features.get",
    "eebus.v1.features.data.get",
    "eebus.v1.features.data.set",
    "eebus.v1.mutations.get",
    "eebus.v1.mutations.rollback",
}
ISSUE76_TOOL_SCOPES = {
    "eebus.v1.features.get": "eebus.raw.read",
    "eebus.v1.features.data.get": "eebus.raw.read",
    "eebus.v1.features.data.set": "eebus.raw.write",
    "eebus.v1.mutations.get": "eebus.raw.read",
    "eebus.v1.mutations.rollback": "eebus.raw.write",
}
ISSUE76_MUTATION_STATES = {
    "prepared",
    "dispatch_intent",
    "reply_observed",
    "verify_pending",
    "applied",
    "probe_active",
    "rollback_intent",
    "rollback_dispatch_intent",
    "rollback_reply_observed",
    "rollback_verify_pending",
    "rolled_back",
    "no_effect",
    "outcome_unknown",
    "conflict",
    "failed_no_contact",
    "rejected",
}
ISSUE76_SECRET_DENYLIST = ISSUE68_SECRET_DENYLIST
ISSUE76_SECRET_BOUNDARY = {
    "keyNormalization": (
        "Unicode NFKC; insert underscore at ASCII lower-or-digit to upper transition; "
        "map every run outside [A-Za-z0-9] to underscore; lowercase; collapse and trim "
        "underscores"
    ),
    "keyComparison": (
        "exact normalized or underscore-elided match against x-secret-denylist"
    ),
    "valueNormalization": "Unicode NFKC then trim leading and trailing whitespace",
    "valueRejection": [
        "case-insensitive PEM private-key boundary",
        "case-insensitive bearer authorization scheme followed by a non-empty credential",
    ],
    "action": "reject-before-hash-reference-audit-or-error-rendering",
}
ISSUE76_SECRET_KEY_COMPACT_DENYLIST = {
    value.replace("_", "") for value in ISSUE76_SECRET_DENYLIST
}
ISSUE82_CANONICAL_DTO_VALIDATORS = (
    "ValidateFeatureDataSetRequestV1",
    "ValidateMutationGetRequestV1",
    "ValidateMutationRollbackRequestV1",
    "ValidateFeaturesGetDataV1",
    "ValidateFeatureDataGetDataV1",
    "ValidateMutationV1",
)
ISSUE82_CANONICAL_DTO_VALIDATOR_SIGNATURES = {
    "ValidateFeatureDataSetRequestV1": (
        "func ValidateFeatureDataSetRequestV1"
        "(request FeatureDataSetRequestV1) *ErrorV1"
    ),
    "ValidateMutationGetRequestV1": (
        "func ValidateMutationGetRequestV1(request MutationGetRequestV1) *ErrorV1"
    ),
    "ValidateMutationRollbackRequestV1": (
        "func ValidateMutationRollbackRequestV1"
        "(request MutationRollbackRequestV1) *ErrorV1"
    ),
    "ValidateFeaturesGetDataV1": (
        "func ValidateFeaturesGetDataV1"
        "(request FeaturesGetRequestV1, data FeaturesGetDataV1) *ErrorV1"
    ),
    "ValidateFeatureDataGetDataV1": (
        "func ValidateFeatureDataGetDataV1"
        "(request FeatureDataGetRequestV1, data FeatureDataGetDataV1, "
        "terminal *ErrorV1) *ErrorV1"
    ),
    "ValidateMutationV1": "func ValidateMutationV1(mutation MutationV1) *ErrorV1",
}
ISSUE82_GATEWAY_RESIDUAL_RESPONSIBILITIES = (
    "duplicate-key rejection before typed decoding",
    (
        "boundary-derived authorization snapshot with exact principal_class, "
        "scope, tool, and raw mask tier"
    ),
    "public denial before provider, router, or runtime contact",
    "undecodable-input request nulling without raw-input echo",
    "canonical validator invocation and runtime-bound envelope construction",
    "public-safe error rendering and separate redacted evidence projection",
)
ISSUE92_ERROR_CODES = (
    "invalid_argument",
    "permission_denied",
    "unsupported_operation",
    "partial_operation_forbidden",
    "constraints_unknown",
    "constraint_failure",
    "stale_read_token",
    "cas_mismatch",
    "runtime_epoch_mismatch",
    "connection_generation_mismatch",
    "idempotency_conflict",
    "writer_busy",
    "timeout",
    "cancelled",
    "disconnected",
    "remote_error",
    "decode_error",
    "partial_result",
    "no_effect",
    "outcome_unknown",
    "conflict",
    "rollback_failed",
    "not_found",
    "secret_detected",
    "internal",
)
ISSUE84_RUNTIME_ADMISSION = {
    "definition": "complete-only-after-all-ordered-checks",
    "precedence": [
        {
            "order": 1,
            "check": "exact-current-topology-target",
            "failureCode": "not_found",
        },
        {
            "order": 2,
            "check": "compatible-local-protocol-source",
            "failureCode": "unsupported_operation",
        },
        {
            "order": 3,
            "check": "declared-full-operation",
            "failureCode": "unsupported_operation",
        },
        {
            "order": 4,
            "check": "current-runtime-epoch",
            "failureCode": "runtime_epoch_mismatch",
        },
        {
            "order": 5,
            "check": "current-connection-generation",
            "failureCode": "connection_generation_mismatch",
        },
    ],
    "errorBinding": {
        "determinedBy": "operation-stage",
        "carrier": "typed-runtime-outcome",
        "postErrorRuntimeLookup": False,
        "fabricatedBinding": False,
        "sameCodeMayBeBoundOrUnbound": True,
        "unboundSourceLayers": [
            "mcp",
            "gateway-router",
            "eebusreg-runtime",
            "eebusreg-coordinator",
        ],
        "postDispatchSourceLayers": [
            "remote",
            "spine-go-round-trip",
            "ship-session",
            "eebus-go-executor",
        ],
    },
    "positiveBindingRequiredFor": [
        "success",
        "partial-result",
        "MutationV1",
        "error-with-bound-data",
    ],
}
ISSUE84_LOCAL_PROTOCOL_SOURCE = {
    "count": 1,
    "featureType": "Generic",
    "featureRole": "client",
    "entity": "existing CEM",
    "provisionAfter": "service Setup",
    "provisionBefore": "network Start",
    "purpose": "SHIP/SPINE protocol-plane source only",
    "createsEntity": False,
    "createsUseCase": False,
    "createsPublicMethod": False,
    "rawRemoteTopology": False,
    "semanticProjection": False,
    "publicRedactedEvidence": False,
}
ISSUE84_NATIVE_FEATURE_TYPE = {
    "type": "string",
    "minLength": 1,
    "maxLength": 128,
    "pattern": "^[A-Z][A-Za-z0-9]*$",
    "examples": ["Measurement"],
    "x-topologyMatch": "exact-current-topology-value-no-alias",
}
ISSUE84_LOCAL_SOURCE_HEADING = "## Local SPINE Protocol Source"
ISSUE84_LOCAL_SOURCE_END_HEADING = "## `features.get`"
ISSUE84_SOURCE_MULTIPLICITY_ACTIONS = frozenset(
    {"add", "advertise", "allow", "create", "permit", "provision", "register", "use"}
)
ISSUE84_SOURCE_PROJECTION_ACTIONS = frozenset(
    {
        "allow",
        "copy",
        "emit",
        "enter",
        "export",
        "expose",
        "include",
        "permit",
        "project",
        "publish",
        "route",
        "surface",
    }
)
ISSUE84_SOURCE_LIFECYCLE_ACTIONS = frozenset(
    {"allow", "move", "permit", "provision"}
)
ISSUE86_READ_OBSERVATION_INVARIANTS = {
    "validator": "ValidateFeatureDataGetDataV1",
    "requestClassifier": "READ",
    "requestDataPresence": "optional",
    "requestDataOrigin": (
        "runtime-generated-canonical-function-specific-full-read-command"
    ),
    "callerSuppliedRequestNarrowing": False,
    "forbiddenCallerRequestNarrowing": [
        "selectors",
        "elements",
        "filters",
        "partial-mode",
    ],
    "requestErrorNumber": "forbidden",
    "responseClassifier": "REPLY",
    "responseData": "required-non-null-canonical-typed-function-data",
    "responseErrorNumber": "forbidden",
    "correlationBinding": (
        "raw_request.correlation_key-equals-raw_response.correlation_key"
    ),
    "functionBinding": (
        "raw_request.function-equals-raw_response.function-equals-target.function"
    ),
    "valueBinding": "raw_response.data-jcs-equals-value",
    "payloadExposure": "owner-only-raw-never-public-redacted",
    "secretBoundary": "recursive-typed-value-secret-rejection",
}
ISSUE88_LAB_PROFILE_MARKERS = {
    ISSUE76_PROTOCOL_REL: (
        "## Production Lab Profile Activation",
        "`helianthus.eebus.raw-mutation-lab-profile.v1`",
        "disabled by absence",
        "exact target",
        "permitted value hashes",
        "rollback value hash",
        "maximum probe ttl",
        "absolute expiry",
        "filesystem activation contract is owned by the",
        "supplies either zero profiles or exactly one already-validated",
        "profile removal or absence after durable mutation state exists",
        "protected owner file therefore contains exactly one profile when present",
        "runtime may carry up to `16` immutable validated profiles internally",
        "cannot prevent recovery or rollback",
    ),
    ISSUE76_ARCHITECTURE_REL: (
        "## Owner-Controlled Lab Profile Boundary",
        "at most `65536` bytes",
        "protected `0700` runtime state root",
        "`/data/eebus/eebusmutation/mutation-lab-profile-v1.json`",
        "existing protected raw-mutation subtree",
        "association-store top-level whitelist remains unchanged",
        "no alternate root-level or legacy path exists",
        "both the protected `0700` runtime state root and its `eebusmutation` child are `0700`",
        "descriptor-relative with `openat` and `o_nofollow`",
        "gateway-owned `0600` regular file",
        "`st_nlink=1`",
        "descriptor identity and metadata must remain byte-for-byte stable",
        "removing the profile, or observing it absent after a durable mutation exists",
        "denies every new forward write but does not revoke guarded recovery or rollback",
        "exactly one closed json `mutationlabprofilev1` object",
        "decoder rejects unknown keys, duplicate keys at every depth, trailing json values, and non-canonical field forms",
        "protected owner file carries exactly one profile when present",
        "runtime may carry up to `16` immutable profiles internally",
        "load and validate before runtime `start`",
        "request cannot create, widen, or persist a profile",
        "public http remains zero-contact denied",
        "new writes fail after profile expiry",
        "durable recovery and rollback remain authorized",
        "no new mcp tool",
    ),
    ISSUE76_API_REL: (
        "## `MutationLabProfileV1`",
        "`mutationlabprofilev1`",
        "storage and loader contract is owned by the",
        "choose a storage path",
        "all nine fields are required",
        "`contract`, `profile_id`, `target`, `allowed_value_hashes`, `rollback_value_hash`, `maximum_probe_ttl_seconds`, `safety_predicates`, `evidence_hashes`, and `expires_at`",
        "no other profile-root key is accepted",
        "`profile_id` is 1..128 bytes after exact/no-trim validation",
        "`allowed_value_hashes` contains 1..32 unique exact `hashv1` values",
        "`safety_predicates` contains 1..16 unique strings, each 1..128 bytes after exact/no-trim validation",
        "`evidence_hashes` contains 1..32 unique exact `hashv1` values",
        "`maximum_probe_ttl_seconds` is an integer 1..900",
        "`target` uses the existing exact `featuretargetv1` bounds",
        "`rollback_value_hash` is an exact `hashv1`",
        "`expires_at` uses the existing utc timestamp contract",
        "`profile_id`",
        "`target`",
        "`allowed_value_hashes`",
        "`rollback_value_hash`",
        "`maximum_probe_ttl_seconds`",
        "`safety_predicates`",
        "`evidence_hashes`",
        "`expires_at`",
        "exactly one already-loaded profile",
        "does not add an mcp tool",
        "disabled by absence",
    ),
}
ISSUE87_WAL_RESTORE_POLICY = {
    "recordValidator": "ValidateMutationV1",
    "recordValidation": "every-record-before-addressable",
    "precontractReference": "mutation:v1:<64-lowercase-hex>",
    "precontractReferenceAction": "reject",
    "semanticallyInvalidRecordAction": "reject",
    "restoreFailureAction": "reject-record-and-leave-coordinator-unavailable",
    "invalidWalBytes": "preserve-without-rewrite-or-migration",
    "validConflictStateAction": "restore-global-write-quarantine",
    "compatibility": {
        "legacyStableApi": False,
        "aliases": False,
        "v2": False,
    },
}
ISSUE76_PRIVATE_PEM_PATTERN = re.compile(
    r"-----BEGIN\s+(?:[A-Z0-9]+\s+)*PRIVATE\s+KEY-----",
    re.IGNORECASE,
)
ISSUE76_BEARER_VALUE_PATTERN = re.compile(r"^bearer\s+\S", re.IGNORECASE)
ISSUE76_M6_LOCKED_ARTIFACTS = {
    Path("api/_candidate/msp-06-eebus-mcp-v1.md"): (
        "6a0b9a2c012cca480586b622691ee2e02"
        "3096e4aa2e23877f074a16311f4247c"
    ),
    Path("api/_candidate/msp-06/helianthus.eebus.mcp.v1.schema.json"): (
        "a5f696d4c41cf78407bb13ac4a3e91cc"
        "2eadbd785d64f9436f81419bd5bd4fbd"
    ),
    Path("api/_candidate/msp-06/helianthus.eebus.mcp.v1.raw.schema.json"): (
        "e7fc213ad2b8d8ef426f426e486f8dba4"
        "035183bc5ceea2d1b6717b6adad986f"
    ),
    Path("api/_candidate/raw-snapshot-view-v1.md"): (
        "0ddf41bb9dca47c90f50f09b6c0be7be"
        "f3d664aa7575ace3f81faef82c59f954"
    ),
    Path("api/_candidate/msp-068-raw-operator-redaction-amendment.md"): (
        "f1ae2a676ec688c44f330911682e12b70"
        "8271ddf4022561ac8e7fd13d1b13a34"
    ),
    Path("protocols/ship-spine-overview.md"): (
        "734c5668cd1937b088cbb12c7c4dd6b7"
        "8c0fc76cc76873dc2d49092aded65b3b"
    ),
}
ISSUE82_REQUIRED_API_MARKERS = (
    "The six additive canonical validators are exported by",
    *ISSUE82_CANONICAL_DTO_VALIDATOR_SIGNATURES.values(),
    "The gateway retains duplicate-key rejection before typed decoding",
    "exact immutable authorization snapshot",
    "Public evidence remains a separate redacted projection",
    "arbitrary malformed input is never reflected into the raw response",
    (
        "`reply_observed` and `verify_pending` require the non-null correlated "
        "`protocol_accepted` boolean and permit either `true` or `false`"
    ),
    (
        "`rollback_reply_observed` and `rollback_verify_pending` require the "
        "nested rollback `protocol_accepted` to be a non-null correlated boolean"
    ),
    "Recovery after restart from either durable pending state performs this readback",
    "`mutation:v1:<64-lowercase-hex>` reference or any semantically invalid WAL record",
    "invalid WAL bytes are preserved without silent migration or rewrite",
    (
        "There is no legacy stable API support, compatibility alias, v2 surface, "
        "WAL migration, or fallback decoder"
    ),
)
ISSUE84_REQUIRED_API_MARKERS = (
    "`Measurement` remains `Measurement`",
    "lowercase `measurement` is invalid and is not an alias",
    "Runtime admission is complete only after all five checks below succeed",
    "The rows are exhaustive and use first-failure precedence",
    "Binding presence is determined by the operation stage, not by the error code",
    "An authenticated read token can supply its signed binding",
    "A malformed or unknown token supplies no binding",
    "A post-error runtime lookup is forbidden",
    "must not fabricate a `MutationV1`, infer binding from an error code",
    (
        "When `meta.runtime` is null, `source_layer` is limited to `mcp`, "
        "`gateway-router`, `eebusreg-runtime`, or `eebusreg-coordinator`"
    ),
    (
        "An error from `eebus-go-executor`, `spine-go-round-trip`, "
        "`ship-session`, or `remote` proves that dispatch was reached"
    ),
    (
        "Every success, partial result, returned `MutationV1`, and error "
        "envelope that accompanies bound data requires a positive runtime binding"
    ),
    "After service Setup completes and before network Start is invoked",
    (
        "exactly one local feature of type `Generic` and role `client` on "
        "the existing CEM"
    ),
    "solely the SHIP/SPINE protocol-plane source",
    "creates no second entity, no use case, and no public method",
    (
        "must not enter raw remote topology, semantic projection, GraphQL, "
        "or public/redacted evidence"
    ),
)
ISSUE76_REQUIRED_MARKERS = {
    ISSUE76_PROTOCOL_REL: (
        "topology says which feature functions and possible operations",
        "full `read` and full `write` only",
        "remote ski and ship id",
        (
            "may be absent or preserved in `raw_request.data`; "
            "it is not required to be null"
        ),
        (
            "does not add any caller-supplied selector, element, filter, "
            "or partial-mode field"
        ),
        "response data remains canonically equal to the observation value",
        "visible only on the owner-authorized raw surface",
        "register the waiter before send",
        "late response cannot complete an aba successor",
        "constraints_unknown",
        "partial_result",
        "no ship-go change is authorized",
    ),
    ISSUE76_ARCHITECTURE_REL: (
        "gateway `eebuscommandrouter`",
        "eebusreg `rawfeatureruntimev1`",
        "eebusreg `rawmutationruntimev1`",
        "the existing public `runtime` method set is unchanged",
        "`writeauthorizationv1`",
        "`validatewriteauthorizationv1`",
        "register the waiter before send",
        "`runtime_epoch`",
        "`connection_generation`",
        "one global eebusreg runtime writer lease",
        "idempotency identity is",
        "`outcome_unknown`",
        "noeffectverificationv1",
        "does not prove that the write never transiently executed",
        "`conflict` globally disables new writes",
        "ship-go therefore remains unchanged",
    ),
    ISSUE76_API_REL: (
        '["features.get","features.data.get","features.data.set","mutations.get","mutations.rollback"]',
        "public/lan mcp boundary exposes none of the five tools",
        "before provider lookup",
        "`read_token`",
        "`idempotency_key`",
        "`mode=probe`",
        "`rawmutationruntimev1`",
        "authscopev1rawwrite",
        *ISSUE82_REQUIRED_API_MARKERS,
        *ISSUE84_REQUIRED_API_MARKERS,
        "`raw_request` is result evidence and is not a caller input",
        (
            "`raw_request.data` may be absent or contain the runtime-generated "
            "canonical typed function-specific full-read command payload"
        ),
        (
            "does not authorize caller-supplied selectors, elements, filters, "
            "or partial mode"
        ),
        (
            "`raw_request.correlation_key` equals "
            "`raw_response.correlation_key`"
        ),
        "`raw_response.data` is canonically equal to `value`",
        (
            "the same boundary applies to `raw_request.data`: "
            "it is owner-only raw evidence"
        ),
        "noeffectverificationv1",
        "a correlated reply records `protocol_accepted` as a boolean, including `false`",
        "`partial_result`",
        "`candidate_ref`, partial operations, selectors, `filterdelete`, invoke, graphql, portal, home assistant, semantic promotion, v2, aliases, and legacy compatibility are out of scope",
    ),
    ISSUE76_POLICY_REL: (
        "every protocol statement must satisfy one of these paths",
        "non-public vendor specifications may be consulted privately",
        "may not be copied, closely paraphrased",
        "owner-authorized local raw surface may show real ship/spine operational data",
        "no tier may expose private keys, pem private material",
        "public evidence remains explicitly redacted",
        "raw references cannot be dereferenced through a public/redacted boundary",
        "m6 remains complete and byte-locked",
        "must not add substantive `docs/` trees",
    ),
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
PROVENANCE_MACHINE_FINGERPRINTS = {
    **MSP055_PROVENANCE_MACHINE_FINGERPRINTS,
    **MSP06_PROVENANCE_MACHINE_FINGERPRINTS,
}
MSP055_PROVENANCE_TEXT_FINGERPRINTS = {
    ".github/workflows/docs-ci.yml": {
        MSP055_SOURCE_COMMIT,
    },
    "api/_candidate/msp-05p-eebusruntime-v1-correction.md": {
        MSP055_SOURCE_COMMIT,
        MSP055_SOURCE_TREE,
        MSP055_MANIFEST_SHA256,
    },
    "api/_candidate/msp-06-eebus-mcp-v1.md": {
        MSP055_SOURCE_COMMIT,
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
ISSUE96_PUBLIC_SOURCE_COMMITS = {
    "d5f89c767706ef411fc622cd6771c479b7fd1b26",
    "a6cb0727a1509dd04454c8e8edce899f4111fb3a",
    "4f986b14324a0d9ed719121b82c2621d50f58303",
    "9970150f6d81ffa06605fecddedcdf0e38174543",
}
ISSUE96_PROVENANCE_TEXT_FINGERPRINTS = {
    "evidence/EV-20260730-001.md": ISSUE96_PUBLIC_SOURCE_COMMITS,
    "protocols/_candidate/msp-096-spine13-hvac-model-erratum.md": ISSUE96_PUBLIC_SOURCE_COMMITS,
    "scripts/validate_repository_policy.py": ISSUE96_PUBLIC_SOURCE_COMMITS,
}
PROVENANCE_TEXT_FINGERPRINTS = {
    **MSP055_PROVENANCE_TEXT_FINGERPRINTS,
    **ISSUE96_PROVENANCE_TEXT_FINGERPRINTS,
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
    "evidence/README.md": "evidence-policy",
    "evidence/evidence-template.md": "template",
    "re-notes/template.md": "template",
    "development/contributing.md": "contribution-policy",
}

SCAFFOLD_ARTIFACT_SHA256 = {
    "README.md": "2cbdf09619d7bdee2c6cc9c11495da1" "5a04a1888309ea5df487c70c1a5c1eeba",
    "api/README.md": "99cd8f1833d1a1f801f4d04d62b1ecb" "95f20ad73d8dadc04c654f1fdcf31f1f3",
    "api/api-surface-v1.md": "acb007a5a2366b63ed4a64fecfee5cad" "2109fcbd779c87c0281a37b9f44cbeca",
    "evidence/README.md": "8028825bcfba106864bb2f44984b6bcc" "d1717a557ebf9e2c6d98b64f5367941d",
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
        "734c5668cd1937b088cbb12c7c4dd6b7" "8c0fc76cc76873dc2d49092aded65b3b"
    ),
}

PRODUCTION_REVIEWED_DEVICE_ARTIFACT_SHA256 = {
    "devices/vr940f.md": (
        "75ad978cfaec7573003508df67a28305" "fc7ccdf580d05ee25d7784fad8da7510"
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
SHIP_IDENTITY_CURRENT_STATUSES = {
    "active",
    "api-contract",
    "candidate",
    "contribution-policy",
    "evidence-policy",
    "ownership-landing",
    "ownership-policy",
    "planned-target",
    "publishable",
}
SHIP_IDENTITY_SUPERSEDED_ALLOW: dict[str, frozenset[str]] = {}
SHIP_IDENTITY_FORBIDDEN_PATTERNS = {
    "configured-endpoint-field": re.compile(
        r"\bconfigured(?:[_ -]+remote)?[_ -]+endpoints?\b", re.IGNORECASE
    ),
    "queue-remote-ski": re.compile(r"\bQueueRemoteSKI\b"),
    "report-remote-endpoint": re.compile(r"\bReportRemoteEndpoint\b"),
    "endpoint-forced-pairing": re.compile(
        r"\bendpoint[-_ ]forced(?:[-_ ]pairing)?\b|"
        r"\bforced[-_ ]endpoint(?:[-_ ]pairing)?\b|"
        r"\bOutgoing Attempt Gate\b|"
        r"\bDurable Outgoing Attempt Reservation\b|"
        r"\bendpoint_(?:path|fallback)\b",
        re.IGNORECASE,
    ),
    "noncanonical-publisher": re.compile(
        r"\bRawProbe\b|\b(?:Python|compat(?:ibility)?) publisher\b",
        re.IGNORECASE,
    ),
    "outbound-initiation": re.compile(
        r"\b(?:OutgoingAttemptBridge|pre[-_ ]?dial|"
        r"(?:dial|pairing)[-_ ]?fallback|endpoint_(?:path|fallback))\b",
        re.IGNORECASE,
    ),
    "alternate-ship-id": re.compile(
        r"\balternate SHIP ID\b|\balternate protocol-service\b",
        re.IGNORECASE,
    ),
}
SHIP_IDENTITY_POLICY_CREATION_PATTERN = re.compile(
    r"\b(?:authorization policy|policy configuration|allowlist(?:ed)?(?: SKI| entry)?)\b"
    r"[^\n.]{0,120}\b(?:creates?|publishes?|produces?|populates?|synthesizes?)\b"
    r"[^\n.]{0,120}\b(?:service|session|candidate|observation|topology|remote row)\b",
    re.IGNORECASE,
)
SHIP_IDENTITY_NEGATED_CREATION_PATTERN = re.compile(
    r"\b(?:cannot|never|does not|do not|must not)\s+"
    r"(?:create|publish|produce|populate|synthesize)\b",
    re.IGNORECASE,
)
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
    "4a6caf9058d2682fd5e6980f4eada383" "011efc1aa35bf547e6868e0f4731045e": {
        "canonical_source": (
            "Project-Helianthus/helianthus-docs-eebus:architecture/README.md"
        ),
        "owner_domain": "architecture",
        "license": "AGPL-3.0-only",
        "claim_status": "evidence-backed",
        "publication_status": "active",
        "source_class": "derived_inference",
        "evidence_ids": "EV-20260711-001, EV-20260714-001, EV-20260720-001",
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
    "EV-20260720-001": {
        "18ddba29e4c8c7ed01659aa6a8799ac" "13ca6ede9c2a48b78f1bb52835697d593": {
            "canonical_source": (
                "Project-Helianthus/helianthus-docs-eebus:"
                "evidence/EV-20260720-001.md"
            ),
            "owner_domain": "evidence",
            "license": "CC0-1.0",
            "publication_status": "publishable",
            "claim_status": "evidence-backed",
            "source_class": "observed_runtime",
            "evidence_ids": "EV-20260720-001",
            "hypothesis_status": "publishable",
            "falsifier": (
                "A future independently reproducible redacted observation "
                "under the same bounded conditions shows different "
                "registration or automatic-accept behavior."
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
    "3d9476af41d3ebb0557b7a75dc86812c" "b1a06ae9b634b43622ab0139a9eb12de": {
        "canonical_source": (
            "Project-Helianthus/helianthus-docs-eebus:devices/vr940f.md"
        ),
        "owner_domain": "devices",
        "license": "CC0-1.0",
        "claim_status": "evidence-backed",
        "publication_status": "planned-target",
        "source_class": "derived_inference",
        "evidence_ids": "EV-20260714-001,EV-20260720-001",
        "hypothesis_status": "publishable",
        "falsifier": (
            "A bounded redacted live run violates the canonical advertisement, "
            "callback provenance, transport ordering, or restart-persistence gate."
        ),
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
        "live_validation_status": "pending",
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


def ship_identity_corpus_errors(
    root: Path,
    *,
    superseded_allow: dict[str, frozenset[str]] | None = None,
) -> list[str]:
    """Reject retired canonical-identity paths in every current normative document.

    Historical exceptions are never directory-wide. An exception must name one
    evidence file and one rule, and that file must explicitly declare
    identity_contract_scope=superseded_non_normative in front matter.
    """

    allow = SHIP_IDENTITY_SUPERSEDED_ALLOW if superseded_allow is None else superseded_allow
    errors: list[str] = []
    seen_allow_paths: set[str] = set()
    for rel, rules in allow.items():
        if (
            not rel.startswith("evidence/")
            or any(character in rel for character in "*?[]")
            or not rules
            or not rules.issubset(SHIP_IDENTITY_FORBIDDEN_PATTERNS)
        ):
            errors.append(
                f"{rel}: canonical-identity allowance must be an exact evidence path and exact rule set"
            )

    for domain in sorted(PUBLISHABLE_DOMAINS):
        domain_root = root / domain
        if not domain_root.is_dir():
            continue
        for path in sorted(domain_root.rglob("*.md")):
            if not path.is_file() or path.is_symlink():
                continue
            rel = _rel(path, root)
            try:
                text = _read(path)
            except UnicodeDecodeError:
                continue
            metadata, front_matter_error = _front_matter(text)
            if front_matter_error is not None or metadata is None:
                continue
            if metadata.get("publication_status") not in SHIP_IDENTITY_CURRENT_STATUSES:
                continue

            superseded = (
                metadata.get("identity_contract_scope")
                == "superseded_non_normative"
            )
            allowed_rules = allow.get(rel, frozenset())
            if allowed_rules:
                seen_allow_paths.add(rel)
                if not superseded or metadata.get("owner_domain") != "evidence":
                    errors.append(
                        f"{rel}: canonical-identity allowance requires superseded_non_normative evidence metadata"
                    )
                    allowed_rules = frozenset()
            elif superseded:
                errors.append(
                    f"{rel}: superseded_non_normative identity evidence has no exact allowance"
                )

            body = _markdown_body(text)
            for rule, pattern in SHIP_IDENTITY_FORBIDDEN_PATTERNS.items():
                for match in pattern.finditer(body):
                    if superseded and rule in allowed_rules:
                        continue
                    line = body.count("\n", 0, match.start()) + 1
                    errors.append(f"{rel}:{line}: forbidden canonical-identity rule {rule}")

            for match in SHIP_IDENTITY_POLICY_CREATION_PATTERN.finditer(body):
                if SHIP_IDENTITY_NEGATED_CREATION_PATTERN.search(match.group(0)):
                    continue
                rule = "policy-created-observation"
                if superseded and rule in allowed_rules:
                    continue
                line = body.count("\n", 0, match.start()) + 1
                errors.append(f"{rel}:{line}: forbidden canonical-identity rule {rule}")

    for rel in sorted(set(allow) - seen_allow_paths):
        errors.append(f"{rel}: canonical-identity allowance did not match current evidence")
    return sorted(set(errors), key=lambda value: value.encode("utf-8"))


STRICT_CURRENT_SCHEMA_PATH = "architecture/_candidate/msp-04a-persistent-store.md"
STRICT_CURRENT_SCHEMA_REQUIRED = (
    "only current persistence schema version 1",
    "Every non-current schema version fails closed",
    "leaves every store byte unchanged",
)
OUTBOUND_PAIRING_GUARD_PATHS = (
    "protocols/ship-spine-overview.md",
    "architecture/_candidate/msp-052-outbound-pairing-contract.md",
    "api/_candidate/msp-052-outbound-pairing-api.md",
)
NORMATIVE_OUTBOUND_PAIRING_CLAUSE = (
    "discovery and allowlist evaluation alone never initiate a network attempt"
)
OUTBOUND_PAIRING_PASSIVE_CLAUSE_BY_PATH = {
    "protocols/ship-spine-overview.md": (
        "Discovery observations and allowlist evaluation never initiate an outbound "
        "dial or pairing attempt"
    ),
    "architecture/_candidate/msp-052-outbound-pairing-contract.md": (
        NORMATIVE_OUTBOUND_PAIRING_CLAUSE
    ),
    "api/_candidate/msp-052-outbound-pairing-api.md": NORMATIVE_OUTBOUND_PAIRING_CLAUSE,
}
SEMANTIC_TOKEN = re.compile(r"[a-z0-9]+", re.IGNORECASE)
SEMANTIC_UNIT = re.compile(r"[^.!?;]+(?:[.!?;]+|$)")
INBOUND_SOURCE_LEMMAS = frozenset({"discover", "observe", "allowlist"})
INBOUND_ACTION_LEMMAS = frozenset(
    {"open", "initiate", "launch", "dial", "start", "trigger", "connect"}
)
INBOUND_TARGET_FORMS = frozenset(
    {
        "tcp",
        "ship",
        "connection",
        "connections",
        "handshake",
        "handshakes",
        "pairing",
        "pairings",
        "dial",
        "dials",
        "dialed",
        "dialing",
    }
)
SELECTED_GATE_ACTION_LEMMAS = frozenset(
    {"allow", "authorize", "connect", "dial", "initiate", "launch", "permit", "start", "trigger"}
)
SELECTED_GATE_ACTION_EXACT = frozenset({"eligible", "eligibility"})
SELECTED_GATE_TARGET_FORMS = INBOUND_TARGET_FORMS | frozenset(
    {"attempt", "attempts", "outbound", "outgoing"}
)
PERSISTENCE_ACTION_LEMMAS = frozenset(
    {
        "cache",
        "persist",
        "publish",
        "reload",
        "restore",
        "resurrect",
        "save",
        "serialize",
        "survive",
        "write",
    }
)
PERSISTENCE_ACTION_EXACT = frozenset({"durable", "durability", "stable"})
RESURRECTION_ACTION_LEMMAS = frozenset(
    {"fallback", "reconnect", "remember", "retain", "reuse", "restore", "resurrect"}
)
ENDPOINT_AUTHORITY_ACTION_LEMMAS = frozenset(
    {"authorize", "derive", "fallback", "permit", "provide", "resolve", "select", "supply", "use"}
)
SCHEMA_TRANSITION_LEMMAS = frozenset(
    {"accept", "load", "convert", "upgrade", "transform", "fallback"}
)
SCHEMA_TRANSITION_EXACT = frozenset({"conversion"})
SEMANTIC_LEMMA_ALIASES = {
    "acceptance": "accept",
    "conversion": "convert",
    "discoveries": "discover",
    "discovery": "discover",
    "initiation": "initiate",
    "observation": "observe",
    "observations": "observe",
    "supplies": "supply",
    "transformation": "transform",
}
SEMANTIC_CONTRACTIONS = {
    "aren't": "are not",
    "can't": "cannot",
    "couldn't": "could not",
    "didn't": "did not",
    "doesn't": "does not",
    "don't": "do not",
    "isn't": "is not",
    "mustn't": "must not",
    "shouldn't": "should not",
    "wasn't": "was not",
    "weren't": "were not",
    "won't": "will not",
}
NEGATION_PHRASES = (
    ("must", "not"),
    ("does", "not"),
    ("do", "not"),
    ("did", "not"),
    ("is", "not"),
    ("are", "not"),
    ("was", "not"),
    ("were", "not"),
    ("is", "prohibited", "from"),
    ("are", "prohibited", "from"),
    ("was", "prohibited", "from"),
    ("were", "prohibited", "from"),
    ("is", "not", "permitted", "to"),
    ("are", "not", "permitted", "to"),
)


def _semantic_tokens(text: str) -> list[str]:
    """Normalize punctuation and hyphens into lower-case semantic tokens."""

    normalized = text.lower().replace("’", "'")
    for contraction, expansion in SEMANTIC_CONTRACTIONS.items():
        normalized = normalized.replace(contraction, expansion)
    return [match.group(0) for match in SEMANTIC_TOKEN.finditer(normalized)]


def _semantic_units(body: str) -> list[tuple[int, str]]:
    """Return sentence-or-line units with their source offsets."""

    units: list[tuple[int, str]] = []
    for match in SEMANTIC_UNIT.finditer(body):
        sentence = match.group(0)
        stripped = sentence.lstrip()
        if stripped:
            units.append((match.start() + len(sentence) - len(stripped), stripped))
    return units


def _contains_phrase(tokens: list[str], phrase: tuple[str, ...]) -> bool:
    width = len(phrase)
    return any(tuple(tokens[index : index + width]) == phrase for index in range(len(tokens) - width + 1))


def _token_has_lemma(token: str, lemma: str) -> bool:
    if SEMANTIC_LEMMA_ALIASES.get(token, token) == lemma:
        return True
    if lemma.endswith("e"):
        return token in {f"{lemma}s", f"{lemma}d", f"{lemma[:-1]}ing"}
    return token in {f"{lemma}s", f"{lemma}es", f"{lemma}ed", f"{lemma}ing"}


def contains_negated_action(
    tokens: list[str],
    action_index: int,
    *,
    previous_action_index: int | None = None,
    previous_action_negated: bool = False,
    next_action_index: int | None = None,
) -> bool:
    """Classify explicit prohibition local to one matched action."""

    left_start = 0 if previous_action_index is None else previous_action_index + 1
    left = tokens[left_start:action_index]
    right_end = len(tokens) if next_action_index is None else next_action_index
    right = tokens[action_index + 1 : right_end]

    if previous_action_negated:
        if not left or all(
            token in {"and", "or", "nor", "also", "then"} for token in left
        ):
            return True
        if (
            any(token in {"or", "nor"} for token in left)
            and not any(
                token
                in {
                    "are",
                    "but",
                    "can",
                    "did",
                    "do",
                    "does",
                    "however",
                    "is",
                    "may",
                    "must",
                    "shall",
                    "should",
                    "was",
                    "were",
                    "will",
                    "yet",
                }
                for token in left
            )
        ):
            return True
    if "no" in left or "never" in left or "cannot" in left:
        return True
    for index, token in enumerate(left):
        if token == "not" and (index + 1 == len(left) or left[index + 1] != "only"):
            return True
    if any(_contains_phrase(left, phrase) for phrase in NEGATION_PHRASES):
        return True

    local_right = right[:7]
    return "no" in local_right or "prohibited" in local_right or any(
        _contains_phrase(local_right, phrase) for phrase in NEGATION_PHRASES
    )


def _action_indices(
    tokens: list[str],
    lemmas: frozenset[str],
    *,
    exact: frozenset[str] = frozenset(),
    fall_back: bool = False,
    exclude_nominal_dial: bool = False,
    exclude_connection_noun: bool = False,
) -> list[int]:
    indices = [
        index
        for index, token in enumerate(tokens)
        if token in exact or any(_token_has_lemma(token, lemma) for lemma in lemmas)
    ]
    if exclude_nominal_dial:
        indices = [
            index
            for index in indices
            if not (
                tokens[index] == "dial"
                and index > 0
                and tokens[index - 1] in {"a", "an", "the", "outbound", "remote", "local"}
            )
        ]
    if exclude_connection_noun:
        indices = [index for index in indices if tokens[index] not in {"connection", "connections"}]
    if fall_back:
        indices.extend(
            index
            for index, token in enumerate(tokens[:-1])
            if token in {"fall", "falls", "fell", "falling"} and tokens[index + 1] == "back"
        )
    return sorted(set(indices))


def _has_unnegated_action(tokens: list[str], action_indices: list[int]) -> bool:
    previous_index: int | None = None
    previous_negated = False
    for position, action_index in enumerate(action_indices):
        next_index = action_indices[position + 1] if position + 1 < len(action_indices) else None
        negated = contains_negated_action(
            tokens,
            action_index,
            previous_action_index=previous_index,
            previous_action_negated=previous_negated,
            next_action_index=next_index,
        )
        if not negated:
            return True
        previous_index = action_index
        previous_negated = negated
    return False


def _inbound_outbound_violation(sentence: str) -> bool:
    tokens = _semantic_tokens(sentence)
    if _allowed_fresh_discovery_attempt(tokens):
        return False
    actions = _action_indices(
        tokens,
        INBOUND_ACTION_LEMMAS,
        exclude_nominal_dial=True,
        exclude_connection_noun=True,
    )
    return (
        any(
            _token_has_lemma(token, lemma)
            for token in tokens
            for lemma in INBOUND_SOURCE_LEMMAS
        )
        and any(token in INBOUND_TARGET_FORMS for token in tokens)
        and bool(actions)
        and _has_unnegated_action(tokens, actions)
    )


def _automatic_outbound_violation(sentence: str) -> bool:
    tokens = _semantic_tokens(sentence)
    actions = _action_indices(
        tokens,
        INBOUND_ACTION_LEMMAS,
        exclude_nominal_dial=True,
        exclude_connection_noun=True,
    )
    return (
        any(token in {"automatic", "automatically"} for token in tokens)
        and any(token in INBOUND_TARGET_FORMS for token in tokens)
        and bool(actions)
        and _has_unnegated_action(tokens, actions)
    )


def _has_inbound_source(tokens: list[str]) -> bool:
    return any(
        _token_has_lemma(token, lemma)
        for token in tokens
        for lemma in INBOUND_SOURCE_LEMMAS
    )


def _has_unnegated_inbound_target_action(tokens: list[str]) -> bool:
    actions = _action_indices(
        tokens,
        INBOUND_ACTION_LEMMAS,
        exclude_nominal_dial=True,
        exclude_connection_noun=True,
    )
    return (
        any(token in INBOUND_TARGET_FORMS for token in tokens)
        and bool(actions)
        and _has_unnegated_action(tokens, actions)
    )


def _linked_outbound_units(source: str, action: str) -> bool:
    source_tokens = _semantic_tokens(source)
    action_tokens = _semantic_tokens(action)
    if any(token in {"cannot", "never", "no", "not"} for token in source_tokens):
        return False
    linked = (
        any(token in INBOUND_TARGET_FORMS for token in source_tokens)
        or any(
            token in {"automatic", "automatically", "it", "job", "that", "then", "this"}
            for token in action_tokens[:4]
        )
    )
    return (
        _has_inbound_source(source_tokens)
        and linked
        and _has_unnegated_inbound_target_action(action_tokens)
    )


def _inbound_outbound_adjacent_violation(left: str, right: str) -> bool:
    return _linked_outbound_units(left, right) or _linked_outbound_units(right, left)


def _automatic_outbound_adjacent_violation(left: str, right: str) -> bool:
    for marker, action in ((left, right), (right, left)):
        marker_tokens = _semantic_tokens(marker)
        action_tokens = _semantic_tokens(action)
        if any(token in {"cannot", "never", "no", "not"} for token in marker_tokens):
            continue
        if (
            any(token in {"automatic", "automatically"} for token in marker_tokens)
            and (
                any(token in INBOUND_TARGET_FORMS for token in marker_tokens)
                or any(token in {"it", "job", "that", "then", "this"} for token in action_tokens[:4])
            )
            and _has_unnegated_inbound_target_action(action_tokens)
        ):
            return True
    return False


def _has_exact_selected_candidate_binding(tokens: list[str]) -> bool:
    return (
        "exact" in tokens
        and any(token in {"current", "currently"} for token in tokens)
        and any(_token_has_lemma(token, "select") for token in tokens)
        and "candidate" in tokens
        and "ski" in tokens
    )


def _allowed_fresh_discovery_attempt(tokens: list[str]) -> bool:
    return (
        _has_exact_selected_candidate_binding(tokens)
        and "fresh" in tokens
        and "reservation" in tokens
        and "frozen" in tokens
        and any(_token_has_lemma(token, "discover") for token in tokens)
    )


def _has_selected_gate_source(tokens: list[str]) -> bool:
    return (
        _contains_phrase(tokens, ("open", "empty"))
        or _contains_phrase(tokens, ("unpaired", "locked"))
        or (
            "pairing" in tokens
            and "window" in tokens
            and any(token in {"active", "open"} for token in tokens)
        )
        or _contains_phrase(tokens, ("visible", "candidate"))
    )


def _selected_candidate_bypass_violation(sentence: str) -> bool:
    tokens = _semantic_tokens(sentence)
    actions = _action_indices(
        tokens,
        SELECTED_GATE_ACTION_LEMMAS,
        exact=SELECTED_GATE_ACTION_EXACT,
        exclude_nominal_dial=True,
        exclude_connection_noun=True,
    )
    return (
        _has_selected_gate_source(tokens)
        and any(token in SELECTED_GATE_TARGET_FORMS for token in tokens)
        and bool(actions)
        and _has_unnegated_action(tokens, actions)
        and not _has_exact_selected_candidate_binding(tokens)
    )


def _selected_candidate_bypass_adjacent_violation(left: str, right: str) -> bool:
    return _selected_candidate_bypass_violation(f"{left} {right}")


def _candidate_reference_persistence_violation(sentence: str) -> bool:
    tokens = _semantic_tokens(sentence)
    if "candidate" not in tokens or not any(
        token in {"ref", "reference", "references"} for token in tokens
    ):
        return False
    actions = _action_indices(
        tokens,
        PERSISTENCE_ACTION_LEMMAS | RESURRECTION_ACTION_LEMMAS,
        exact=PERSISTENCE_ACTION_EXACT,
        fall_back=True,
    )
    return bool(actions) and _has_unnegated_action(tokens, actions)


def _allowed_attempt_journal_binding(tokens: list[str]) -> bool:
    return (
        "attempt" in tokens
        and "journal" in tokens
        and "exact" in tokens
        and "frozen" in tokens
        and any(_token_has_lemma(token, "discover") for token in tokens)
        and not any(
            token in {"fallback", "reconnect", "restart", "runtimeconfig", "static"}
            for token in tokens
        )
    )


def _outbound_resurrection_violation(sentence: str) -> bool:
    tokens = _semantic_tokens(sentence)
    if _candidate_reference_persistence_violation(sentence):
        return True
    targets = {
        "address",
        "endpoint",
        "hostname",
        "observation",
        "path",
        "route",
    }
    if not any(token in targets for token in tokens):
        return False

    persistence_actions = _action_indices(
        tokens,
        PERSISTENCE_ACTION_LEMMAS,
        exact=PERSISTENCE_ACTION_EXACT,
        fall_back=True,
    )
    if (
        persistence_actions
        and _has_unnegated_action(tokens, persistence_actions)
        and not _allowed_attempt_journal_binding(tokens)
    ):
        return True

    resurrection_actions = _action_indices(
        tokens,
        RESURRECTION_ACTION_LEMMAS,
        fall_back=True,
    )
    if _allowed_fresh_discovery_attempt(tokens):
        return False
    return bool(resurrection_actions) and _has_unnegated_action(
        tokens, resurrection_actions
    )


def _outbound_resurrection_adjacent_violation(left: str, right: str) -> bool:
    target_tokens = _semantic_tokens(left)
    action_tokens = _semantic_tokens(right)
    candidate_reference = "candidate" in target_tokens and any(
        token in {"ref", "reference", "references"} for token in target_tokens
    )
    endpoint_target = any(
        token in {"address", "endpoint", "hostname", "observation", "path", "route"}
        for token in target_tokens
    )
    if not candidate_reference and not endpoint_target:
        return False
    actions = _action_indices(
        action_tokens,
        PERSISTENCE_ACTION_LEMMAS | RESURRECTION_ACTION_LEMMAS,
        exact=PERSISTENCE_ACTION_EXACT,
        fall_back=True,
    )
    return (
        bool(actions)
        and _has_unnegated_action(action_tokens, actions)
        and any(
            token in {"it", "record", "reference", "route", "that", "this"}
            for token in action_tokens[:8]
        )
    )


def _endpoint_authority_violation(sentence: str) -> bool:
    tokens = _semantic_tokens(sentence)
    if _allowed_fresh_discovery_attempt(tokens):
        return False
    targets = {"address", "endpoint", "hostname", "path", "route"}
    authority_markers = {"config", "configuration", "default", "fallback", "root", "runtimeconfig", "static"}
    if not any(token in targets for token in tokens) or not any(
        token in authority_markers for token in tokens
    ):
        return False
    actions = _action_indices(
        tokens,
        ENDPOINT_AUTHORITY_ACTION_LEMMAS,
        fall_back=True,
    )
    if actions and _has_unnegated_action(tokens, actions):
        return True
    return "authority" in tokens and not any(
        token in {"cannot", "never", "no", "not"} for token in tokens
    )


def _endpoint_authority_adjacent_violation(left: str, right: str) -> bool:
    marker_tokens = _semantic_tokens(left)
    action_tokens = _semantic_tokens(right)
    if not any(
        token in {"config", "configuration", "default", "fallback", "root", "runtimeconfig", "static"}
        for token in marker_tokens
    ):
        return False
    if not any(
        token in {"address", "endpoint", "hostname", "path", "route"}
        for token in action_tokens
    ):
        return False
    if not any(token in {"it", "that", "this"} for token in action_tokens[:5]):
        return False
    actions = _action_indices(
        action_tokens,
        ENDPOINT_AUTHORITY_ACTION_LEMMAS,
        fall_back=True,
    )
    return bool(actions) and _has_unnegated_action(action_tokens, actions)


def _has_noncurrent_schema_source(tokens: list[str]) -> bool:
    if any(token in {"older", "legacy", "noncurrent"} for token in tokens):
        return True
    if any(
        token.startswith("v") and token[1:].isdigit() and token != "v1"
        for token in tokens
    ):
        return True
    if any(tokens[index : index + 2] == ["non", "current"] for index in range(len(tokens) - 1)):
        return True
    return (
        "schema" in tokens
        and "version" in tokens
        and any(token.isdigit() and token != "1" for token in tokens)
    )


def _noncurrent_schema_transition_violation(sentence: str) -> bool:
    tokens = _semantic_tokens(sentence)
    actions = _action_indices(
        tokens,
        SCHEMA_TRANSITION_LEMMAS,
        exact=SCHEMA_TRANSITION_EXACT,
        fall_back=True,
    )
    actions = [
        index
        for index in actions
        if not (
            any(_token_has_lemma(tokens[index], lemma) for lemma in {"accept", "load"})
            and "v1" in tokens[index + 1 : index + 3]
        )
    ]
    return (
        _has_noncurrent_schema_source(tokens)
        and bool(actions)
        and _has_unnegated_action(tokens, actions)
    )


def _semantic_contract_errors(
    body: str,
    classifier: Callable[[str], bool],
    *,
    path: str,
    rule: str,
    adjacent_classifier: Callable[[str, str], bool] | None = None,
) -> list[str]:
    errors: list[str] = []
    units = _semantic_units(body)
    classified = [classifier(sentence) for _, sentence in units]
    for (offset, _), violation in zip(units, classified, strict=True):
        if violation:
            line = body.count("\n", 0, offset) + 1
            errors.append(f"{path}:{line}: forbidden {rule}")

    if adjacent_classifier is None:
        return errors

    for index, ((offset, sentence), (_, next_sentence)) in enumerate(
        zip(units, units[1:], strict=False)
    ):
        if classified[index] or classified[index + 1]:
            continue
        sentence_end = offset + len(sentence)
        next_offset = units[index + 1][0]
        if re.search(r"\n\s*\n", body[sentence_end:next_offset]):
            continue
        if adjacent_classifier(sentence, next_sentence):
            line = body.count("\n", 0, offset) + 1
            errors.append(f"{path}:{line}: forbidden {rule}")
    return errors


def outbound_pairing_contract_errors(root: Path) -> list[str]:
    """Require the bounded candidate route while preserving passive discovery."""

    errors: list[str] = []
    for relative_path in OUTBOUND_PAIRING_GUARD_PATHS:
        path = root / relative_path
        if not path.is_file() or path.is_symlink():
            errors.append(f"{relative_path}: missing outbound-pairing surface")
            continue
        try:
            body = _markdown_body(_read(path))
        except UnicodeDecodeError:
            errors.append(f"{relative_path}: outbound-pairing surface is unreadable")
            continue
        normalized = " ".join(body.split())
        required_passive_clause = OUTBOUND_PAIRING_PASSIVE_CLAUSE_BY_PATH[relative_path]
        if required_passive_clause not in normalized:
            errors.append(f"{relative_path}: missing passive-discovery clause")
        for rule, classifier, adjacent_classifier in (
            (
                "outbound-initiation",
                _inbound_outbound_violation,
                _inbound_outbound_adjacent_violation,
            ),
            (
                "automatic-outbound",
                _automatic_outbound_violation,
                _automatic_outbound_adjacent_violation,
            ),
            (
                "selected-candidate-bypass",
                _selected_candidate_bypass_violation,
                _selected_candidate_bypass_adjacent_violation,
            ),
            (
                "outbound-resurrection",
                _outbound_resurrection_violation,
                _outbound_resurrection_adjacent_violation,
            ),
            (
                "endpoint-authority",
                _endpoint_authority_violation,
                _endpoint_authority_adjacent_violation,
            ),
        ):
            errors.extend(
                _semantic_contract_errors(
                    body,
                    classifier,
                    path=relative_path,
                    rule=rule,
                    adjacent_classifier=adjacent_classifier,
                )
            )

    required_by_path = {
        "architecture/_candidate/msp-052-outbound-pairing-contract.md": (
            "`visible`",
            "`selected/validated`",
            "`connected-untrusted`",
            "`trusted`",
            "exactly 40 characters",
            "no SPINE setup, semantic processing, or payload delivery",
            "SPINE datagram received during that approval hold is rejected",
            "generic post-handshake setup-race buffer is bounded to at most 16 raw datagrams and 16 KiB total",
            "active candidate queue",
            "fresh mDNS discovery",
            "Inbound `register=true` remains",
            "While recovery is `UNPAIRED_LOCKED`, outbound first-trust eligibility requires both an active bounded pairing window and the exact currently selected candidate SKI",
            "`OPEN_EMPTY` alone describes only the open window and empty inbound slot",
            "private attempt journal may durably bind the exact frozen discovered endpoint and path",
            "never contains `candidate_ref`",
            "`RuntimeConfig`, static configuration, root-path default, or fallback authority",
            "`AbortPrepared`, attempt-lease expiry, a protected attempt-helper panic, and restart recovery of an unresolved reservation each synthesize exactly one failure",
            "matching revocation is the only non-failure cancellation",
            "without a retry charge",
            "The transport/service stops first",
            "callback sink settle terminal callbacks and synthetic failures",
            "`v0.7.1-helianthus.6`",
            "`v0.6.1-helianthus.6`",
            "`v0.7.1-helianthus.1`",
        ),
        "api/_candidate/msp-052-outbound-pairing-api.md": (
            "private, owner-only local administration",
            "No stable or public value exposes candidate presence",
            "experimental/admin",
            "`PairingCandidateQueuer` and `CandidateRef` are private experimental process-local dependency capabilities only",
            "does not promote `candidate_ref` into `helianthus-eebusreg` public state",
            "exactly 40 lowercase hexadecimal characters",
            "no stable GraphQL, MCP, Portal, Home Assistant, CLI, or network-admin mutation",
            "`candidate_ref` is a process-local dependency capability only",
            "never durable and never stable `helianthus-eebusreg`, MCP, or GraphQL state",
            "must not journal `candidate_ref`",
            "Stable eebusreg, MCP, and GraphQL remain candidate-free",
        ),
    }
    for relative_path, required_terms in required_by_path.items():
        path = root / relative_path
        if not path.is_file() or path.is_symlink():
            continue
        try:
            normalized = " ".join(_markdown_body(_read(path)).split())
        except UnicodeDecodeError:
            continue
        for required in required_terms:
            if required not in normalized:
                errors.append(
                    f"{relative_path}: missing outbound-pairing requirement {required!r}"
                )
    return errors


def strict_current_schema_errors(root: Path) -> list[str]:
    """Reject non-current persistence activation in the one current-schema contract."""

    path = root / STRICT_CURRENT_SCHEMA_PATH
    if not path.is_file() or path.is_symlink():
        return []
    try:
        body = _markdown_body(_read(path))
    except UnicodeDecodeError:
        return []
    errors = [
        f"{STRICT_CURRENT_SCHEMA_PATH}: strict-current-schema missing canonical current-only clause"
        for clause in STRICT_CURRENT_SCHEMA_REQUIRED
        if clause not in " ".join(body.split())
    ]
    errors.extend(
        _semantic_contract_errors(
            body,
            _noncurrent_schema_transition_violation,
            path=STRICT_CURRENT_SCHEMA_PATH,
            rule="strict-current-schema transition",
        )
    )
    return errors


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
    for fingerprint in PROVENANCE_TEXT_FINGERPRINTS.get(rel, set()):
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
    if rel in {
        ISSUE68_RAW_SCHEMA_REL.as_posix(),
        ISSUE76_SCHEMA_REL.as_posix(),
    }:
        # The candidate schema names operational fields but contains no field
        # values. Preserve the global identifier scan for every value/example
        # while exempting only these structurally validated JSON property keys.
        sanitized = re.sub(
            r'"(?:ski|remote_ski|ship_id)"(?=\s*:)',
            '"operational_identity_field"',
            text,
        )
        sanitized_result = decode_machine_json(sanitized.encode("utf-8"))
        if "private identifier" not in machine_publication_diagnostics(sanitized_result):
            diagnostics.discard("private identifier")
    allowed_fingerprints = PROVENANCE_MACHINE_FINGERPRINTS.get(rel)
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

    expected_device_hash = PRODUCTION_REVIEWED_DEVICE_ARTIFACT_SHA256.get(rel)
    if (
        expected_device_hash is not None
        and hashlib.sha256(text.encode("utf-8")).hexdigest() != expected_device_hash
    ):
        errors.append(f"{rel}: reviewed device artifact differs")

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

    if (
        rel == "api/_candidate/msp-06-eebus-mcp-v1.md"
        and claim_status == "no-protocol-claims"
    ):
        source_commit = metadata.get("source_commit")
        source_binding = (
            "Project-Helianthus/helianthus-eebusreg@"
            + MSP055_SOURCE_COMMIT
            + ":eebusruntime"
        )
        if source_commit != MSP055_SOURCE_COMMIT:
            errors.append(f"{rel}: source_commit must pin the reviewed runtime source")
        if source_binding not in text:
            errors.append(f"{rel}: source_commit body binding is missing or disagrees")
        if metadata.get("source_class") != "derived_inference":
            errors.append(
                f"{rel}: no-protocol candidate source_class must be derived_inference"
            )
        if metadata.get("hypothesis_status") != "draft":
            errors.append(f"{rel}: no-protocol candidate hypothesis_status must be draft")
        falsifier = metadata.get("falsifier", "").strip()
        if not falsifier or falsifier.lower() in {"none", "n/a", "unknown", "tbd"}:
            errors.append(f"{rel}: no-protocol candidate falsifier must be explicit")
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


def _issue_68_machine_contract_errors(root: Path) -> list[str]:
    """Validate both issue-68 MCP profiles as connected machine contracts."""
    errors: list[str] = []
    schemas: dict[Path, dict[str, object]] = {}
    for rel in (ISSUE68_REDACTED_SCHEMA_REL, ISSUE68_RAW_SCHEMA_REL):
        path = root / rel
        if not path.is_file() or path.is_symlink():
            errors.append(f"{rel}: issue-68 machine profile is missing")
            continue
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError):
            errors.append(f"{rel}: issue-68 machine profile is not valid JSON")
            continue
        if not isinstance(value, dict):
            errors.append(f"{rel}: issue-68 machine profile root must be an object")
            continue
        schemas[rel] = value

    redacted = schemas.get(ISSUE68_REDACTED_SCHEMA_REL)
    if redacted is not None:
        definitions = redacted.get("$defs")
        if not isinstance(definitions, dict):
            errors.append(f"{ISSUE68_REDACTED_SCHEMA_REL}: missing closed definitions")
        else:
            mask = definitions.get("MaskTierV1")
            auth = definitions.get("AuthScopeV1")
            tools = definitions.get("ToolV1")
            if not isinstance(mask, dict) or mask.get("const") != "redacted":
                errors.append(f"{ISSUE68_REDACTED_SCHEMA_REL}: profile must be redacted-only")
            if not isinstance(auth, dict) or auth.get("const") != "eebus.public.read":
                errors.append(f"{ISSUE68_REDACTED_SCHEMA_REL}: public authorization scope is not exact")
            if not isinstance(tools, dict) or set(tools.get("enum", [])) != ISSUE68_TOOL_NAMES:
                errors.append(f"{ISSUE68_REDACTED_SCHEMA_REL}: MCP tool inventory is not the exact v1 set")

    raw = schemas.get(ISSUE68_RAW_SCHEMA_REL)
    if raw is not None:
        expected_root = {
            "contract": "helianthus-eebus-mcp",
            "namespace": "eebus.v1",
            "source_type": "SnapshotV1",
            "redacted_projection_type": "RedactedSnapshotV1",
            "pairing_api": "PairingState",
            "mask_tier": "raw",
            "auth_scope": "eebus.raw.read",
            "transport": "owner-only-af-unix",
            "operator_socket": "/data/eebus/operator-mcp.sock",
            "parent_mode": "0700",
            "socket_mode": "0600",
            "peer_credentials": "same-euid-required-where-supported",
            "public_http_path": "/mcp",
            "public_http_tier": "redacted",
            "tier_selector": "none",
        }
        properties = raw.get("properties")
        if not isinstance(properties, dict):
            errors.append(f"{ISSUE68_RAW_SCHEMA_REL}: raw profile properties are missing")
            properties = {}
        for name, expected in expected_root.items():
            definition = properties.get(name)
            if not isinstance(definition, dict) or definition.get("const") != expected:
                errors.append(f"{ISSUE68_RAW_SCHEMA_REL}: raw profile {name} binding is not exact")
        canonicalization = raw.get("x-canonicalization")
        hash_rule = raw.get("x-hash")
        optional_semantics = raw.get("x-optional-field-semantics")
        opaque_limits = raw.get("x-opaque-limits")
        secret_denylist = raw.get("x-secret-denylist")
        if (
            not isinstance(canonicalization, dict)
            or canonicalization.get("standard") != "RFC 8785/JCS"
            or canonicalization.get("objectKeyOrder") != "UTF-16-code-unit"
            or canonicalization.get("rejectDuplicateIdentities") is not True
            or canonicalization.get("rejectNegativeZero") is not True
            or canonicalization.get("safeIntegerMaximum") != 9007199254740991
        ):
            errors.append(f"{ISSUE68_RAW_SCHEMA_REL}: raw JCS contract is not exact")
        if (
            not isinstance(hash_rule, dict)
            or hash_rule.get("algorithm") != "SHA-256"
            or hash_rule.get("projection") != "boundary-selected-profile"
            or hash_rule.get("encoding") != "sha256:lowercase-hex"
            or hash_rule.get("serviceStateFields") != ["kind", "visible", "paired"]
        ):
            errors.append(f"{ISSUE68_RAW_SCHEMA_REL}: raw hash projection is not exact")
        if optional_semantics != {
            "absent": "unavailable",
            "presentEmpty": "observed-empty",
            "presentFalse": "observed-false",
            "null": "only-where-explicitly-allowed",
        }:
            errors.append(f"{ISSUE68_RAW_SCHEMA_REL}: absence-versus-empty contract is not exact")
        if opaque_limits != ISSUE68_OPAQUE_LIMITS:
            errors.append(f"{ISSUE68_RAW_SCHEMA_REL}: opaque limits are not exact")
        if secret_denylist != ISSUE68_SECRET_DENYLIST:
            errors.append(f"{ISSUE68_RAW_SCHEMA_REL}: structured secret denylist is not exact")

        definitions = raw.get("$defs")
        if not isinstance(definitions, dict):
            errors.append(f"{ISSUE68_RAW_SCHEMA_REL}: missing closed definitions")
            definitions = {}
        tools = definitions.get("ToolV1")
        if not isinstance(tools, dict) or set(tools.get("enum", [])) != ISSUE68_TOOL_NAMES:
            errors.append(f"{ISSUE68_RAW_SCHEMA_REL}: MCP tool inventory is not the exact v1 set")

        for name, field_contract in ISSUE68_RAW_TYPE_FIELDS.items():
            definition = definitions.get(name)
            if not isinstance(definition, dict):
                errors.append(f"{ISSUE68_RAW_SCHEMA_REL}: missing first-party {name}")
                continue
            required = field_contract["required"]
            optional = field_contract["optional"]
            if (
                definition.get("type") != "object"
                or definition.get("additionalProperties") is not False
                or set(definition.get("required", [])) != required
                or set(definition.get("properties", {})) != required | optional
            ):
                errors.append(f"{ISSUE68_RAW_SCHEMA_REL}: {name} field contract is not exact")

        service_kind = definitions.get("ServiceKindV1")
        service = definitions.get("ServiceV1")
        service_properties = (
            service.get("properties", {})
            if isinstance(service, dict)
            else {}
        )
        if (
            not isinstance(service_kind, dict)
            or service_kind.get("enum") != ["local", "remote"]
            or service_properties.get("kind")
            != {"$ref": "#/$defs/ServiceKindV1"}
            or service_properties.get("visible") != {"type": "boolean"}
            or service_properties.get("paired") != {"type": "boolean"}
        ):
            errors.append(f"{ISSUE68_RAW_SCHEMA_REL}: ServiceV1 observable state contract is not exact")

        opaque = definitions.get("OpaqueObservationV1")
        opaque_value = definitions.get("OpaqueValueV1")
        opaque_scalar = definitions.get("OpaqueScalarV1")
        if (
            not isinstance(opaque, dict)
            or opaque.get("additionalProperties") is not False
            or set(opaque.get("required", [])) != {"path", "source", "value"}
            or set(opaque.get("properties", {})) != {"path", "source", "value"}
        ):
            errors.append(f"{ISSUE68_RAW_SCHEMA_REL}: opaque path/source/value contract is not exact")
        if (
            not isinstance(opaque_value, dict)
            or opaque_value.get("x-max-depth") != ISSUE68_OPAQUE_LIMITS["maxDepth"]
            or opaque_value.get("x-max-jcs-bytes")
            != ISSUE68_OPAQUE_LIMITS["maxCanonicalBytesPerValue"]
            or len(opaque_value.get("oneOf", [])) != 3
            or not isinstance(opaque_scalar, dict)
            or len(opaque_scalar.get("oneOf", [])) != 4
            or "OpaqueValueDepth2V1" not in definitions
            or "OpaqueValueDepth3V1" not in definitions
        ):
            errors.append(f"{ISSUE68_RAW_SCHEMA_REL}: bounded nested opaque value contract is not exact")
        for name in ("OpaqueValueV1", "OpaqueValueDepth2V1", "OpaqueValueDepth3V1"):
            definition = definitions.get(name)
            variants = definition.get("oneOf", []) if isinstance(definition, dict) else []
            arrays = [
                variant for variant in variants
                if isinstance(variant, dict) and variant.get("type") == "array"
            ]
            objects = [
                variant for variant in variants
                if isinstance(variant, dict) and variant.get("type") == "object"
            ]
            if (
                len(arrays) != 1
                or arrays[0].get("maxItems") != ISSUE68_OPAQUE_LIMITS["maxArrayItems"]
                or len(objects) != 1
                or objects[0].get("maxProperties")
                != ISSUE68_OPAQUE_LIMITS["maxObjectProperties"]
            ):
                errors.append(f"{ISSUE68_RAW_SCHEMA_REL}: {name} container limits are not exact")
        opaque_list = definitions.get("OpaqueObservationsV1")
        if (
            not isinstance(opaque_list, dict)
            or not isinstance(opaque_list.get("maxItems"), int)
            or opaque_list.get("maxItems", 0) <= 0
            or opaque_list.get("maxItems")
            != ISSUE68_OPAQUE_LIMITS["maxObservations"]
            or opaque_list.get("x-max-aggregate-jcs-bytes")
            != ISSUE68_OPAQUE_LIMITS["maxAggregateCanonicalBytes"]
            or opaque_list.get("x-order-by") != ["path", "source", "value"]
        ):
            errors.append(f"{ISSUE68_RAW_SCHEMA_REL}: opaque observations are not bounded and ordered")

        snapshot = definitions.get("OperatorSnapshotProfileV1")
        collections = (
            snapshot.get("properties", {})
            if isinstance(snapshot, dict)
            else {}
        )
        snapshot_meta = definitions.get("SnapshotMetaV1")
        if (
            not isinstance(snapshot_meta, dict)
            or snapshot_meta.get("type") != "object"
            or snapshot_meta.get("additionalProperties") is not False
            or set(snapshot_meta.get("required", []))
            != {
                "contract",
                "runtime",
                "local_ski",
                "mask_tier",
                "captured_at",
                "data_timestamp",
            }
            or set(snapshot_meta.get("properties", {}))
            != {
                "contract",
                "runtime",
                "local_ski",
                "mask_tier",
                "captured_at",
                "data_timestamp",
                "data_hash",
            }
            or snapshot_meta.get("properties", {}).get("local_ski")
            != {"$ref": "#/$defs/LocalSKIV1"}
            or collections.get("meta") != {"$ref": "#/$defs/SnapshotMetaV1"}
            or "meta" not in snapshot.get("required", [])
        ):
            errors.append(
                f"{ISSUE68_RAW_SCHEMA_REL}: raw SnapshotMetaV1 local_ski contract is not exact"
            )
        for collection in ("services", "devices", "entities", "features", "usecases"):
            schema = collections.get(collection)
            if (
                not isinstance(schema, dict)
                or not isinstance(schema.get("maxItems"), int)
                or schema.get("maxItems", 0) <= 0
                or not schema.get("uniqueItems")
                or not schema.get("x-order-by")
            ):
                errors.append(f"{ISSUE68_RAW_SCHEMA_REL}: {collection} is not bounded and ordered")
        service_collection = collections.get("services")
        if (
            not isinstance(service_collection, dict)
            or service_collection.get("x-order-by")
            != ["ski", "ship_id", "identifier", "kind", "visible", "paired"]
        ):
            errors.append(f"{ISSUE68_RAW_SCHEMA_REL}: services ordering is not exact")

        serialized = json.dumps(raw, sort_keys=True).casefold()
        if "rawsnapshotv1" in serialized:
            errors.append(f"{ISSUE68_RAW_SCHEMA_REL}: RawSnapshotV1 compatibility type is forbidden")
        if "enbility/eebus-go" in serialized or "github.com/enbility" in serialized:
            errors.append(f"{ISSUE68_RAW_SCHEMA_REL}: upstream implementation types are forbidden")

    return errors


def issue_68_raw_operator_redaction_errors(root: Path) -> list[str]:
    """Enforce the forward-only raw-operator/redacted-public correction."""
    errors: list[str] = []

    for rel, expected_sha256 in ISSUE68_M2_LOCKED_ARTIFACTS.items():
        path = root / rel
        if not path.is_file() or path.is_symlink() or hashlib.sha256(
            path.read_bytes()
        ).hexdigest() != expected_sha256:
            errors.append(f"{rel}: issue-68 historical M2 artifact must remain byte-identical")

    g16 = root / ISSUE68_G16_LOCKED_ARTIFACT
    if not g16.is_file() or g16.is_symlink() or hashlib.sha256(
        g16.read_bytes()
    ).hexdigest() != ISSUE68_G16_LOCKED_SHA256:
        errors.append(f"{ISSUE68_G16_LOCKED_ARTIFACT}: issue-68 historical G16 artifact must remain byte-identical")

    stable_protocol = root / ISSUE68_STABLE_PROTOCOL
    if not stable_protocol.is_file() or stable_protocol.is_symlink() or hashlib.sha256(
        stable_protocol.read_bytes()
    ).hexdigest() != ISSUE68_STABLE_PROTOCOL_SHA256:
        errors.append(f"{ISSUE68_STABLE_PROTOCOL}: issue-68 stable protocol must remain byte-identical")

    amendment = root / ISSUE68_AMENDMENT_REL
    amendment_text = (
        _read(amendment)
        if amendment.is_file() and not amendment.is_symlink()
        else ""
    )
    if not amendment_text:
        errors.append(f"{ISSUE68_AMENDMENT_REL}: issue-68 forward amendment is missing")

    normalized_amendment = " ".join(amendment_text.split()).casefold()
    for name, marker in ISSUE68_REQUIRED_MARKERS.items():
        if marker.casefold() not in normalized_amendment:
            errors.append(f"{ISSUE68_AMENDMENT_REL}: issue-68 missing {name} contract marker")

    errors.extend(_issue_68_machine_contract_errors(root))

    msp06 = root / "api/_candidate/msp-06-eebus-mcp-v1.md"
    msp06_text = _read(msp06) if msp06.is_file() and not msp06.is_symlink() else ""
    normalized_msp06 = " ".join(msp06_text.split()).casefold()
    connected_requirements = {
        "raw schema binding": ISSUE68_RAW_SCHEMA_REL.name.casefold(),
        "redacted schema binding": ISSUE68_REDACTED_SCHEMA_REL.name.casefold(),
        "raw source ownership": "eebusreg-owned `snapshotv1` is the secret-free raw source",
        "redacted builder ownership": "eebusreg-owned public-view builder constructs a structurally separate `redactedsnapshotv1`",
        "operator socket": "`/data/eebus/operator-mcp.sock`",
        "operator directory mode": "parent directory is `0700`",
        "operator socket mode": "socket is `0600`",
        "same-euid proof": "same-effective-uid peer proof",
        "http redacted boundary": "lan http `/mcp` endpoint is always explicit `mask_tier=redacted`",
        "raw unknown preservation": "raw operator profile instead carries them as bounded opaque objects",
        "pairing state retention": "retains the existing `pairingstate` api",
        "raw service state": "including service kind, visible, and paired state",
    }
    for name, requirement in connected_requirements.items():
        if requirement not in normalized_msp06:
            errors.append(f"{msp06.relative_to(root)}: issue-68 missing connected {name}")

    raw_snapshot = root / ISSUE68_RAW_SNAPSHOT_REL
    raw_snapshot_text = (
        _read(raw_snapshot)
        if raw_snapshot.is_file() and not raw_snapshot.is_symlink()
        else ""
    )
    normalized_raw_snapshot = " ".join(raw_snapshot_text.split()).casefold()
    raw_snapshot_requirements = {
        "raw SnapshotV1 ownership": "`snapshotv1` is the eebusreg-owned, secret-free raw source",
        "separate redacted type": "`redactedsnapshotv1`",
        "redacted builder": "`buildredactedsnapshotv1`",
        "optional SHIP ID pointer": "`servicev1.shipid` | `*string`",
        "required service kind": "`servicev1.kind` | `servicekindv1`",
        "required service visibility": "`servicev1.visible` | `bool`",
        "required service pairing": "`servicev1.paired` | `bool`",
        "explicit redacted service projection": "`redactedservicev1` | `id`, `kind`, `visible`, `paired`",
        "optional description pointer": "`devicev1.description` | `*string`",
        "optional metadata pointer": "`devicev1.metadata` | `*metadatav1`",
        "optional use-case boolean": "`usecasev1.availability` | `*bool`",
        "absence versus empty": "present empty string, array, object, or false boolean remains an observed value",
        "nested opaque value": "`opaquevaluev1` accepts scalars and nested json arrays/objects",
        "PairingState retained": "existing read-only `pairingstate` api remains unchanged",
    }
    for name, requirement in raw_snapshot_requirements.items():
        if requirement not in normalized_raw_snapshot:
            errors.append(f"{ISSUE68_RAW_SNAPSHOT_REL}: issue-68 missing {name}")
    for stale in (
        "eebusraw.redactedid",
        "eebusevidence.objectv1",
        "eebusraw.unknownfield",
        "local mcp view is separate from this historical public go inventory",
        "contains no credential material, unmasked device identity",
    ):
        if stale in normalized_raw_snapshot:
            errors.append(f"{ISSUE68_RAW_SNAPSHOT_REL}: stale redacted compatibility carveout")

    amendment_connections = (
        ISSUE68_RAW_SCHEMA_REL.name.casefold(),
        ISSUE68_REDACTED_SCHEMA_REL.name.casefold(),
        "`snapshotv1`",
        "`redactedsnapshotv1`",
    )
    for requirement in amendment_connections:
        if requirement not in normalized_amendment:
            errors.append(f"{ISSUE68_AMENDMENT_REL}: issue-68 amendment is disconnected from machine/source contract")

    contradictory_phrases = (
        "all `eebus.v1.*` output is redacted",
        "mask tier is always redacted",
        "fixed-redacted policy",
        "header selects `mask_tier`",
        "query parameter selects `mask_tier`",
        "tool argument selects `mask_tier`",
        "client principal selects `mask_tier`",
    )
    combined = normalized_amendment + "\n" + normalized_msp06
    for phrase in contradictory_phrases:
        if phrase in combined:
            errors.append(f"{ISSUE68_AMENDMENT_REL}: issue-68 contradictory boundary language")

    if re.search(r"\btokens? (?:are|is) forbidden in every tier\b", combined):
        errors.append(f"{ISSUE68_AMENDMENT_REL}: issue-68 secret rule ambiguously forbids evidence references")

    amendment_name = ISSUE68_AMENDMENT_REL.name
    for rel in ISSUE68_CURRENT_CONTRACT_RELS:
        path = root / rel
        if not path.is_file() or path.is_symlink() or amendment_name not in _read(path):
            errors.append(f"{rel}: issue-68 forward amendment binding is missing")

    stable_reference = root / "api/eebusruntime-v1/reference.md"
    if stable_reference.is_file() and "candidate_ref" in _read(stable_reference):
        errors.append("api/eebusruntime-v1/reference.md: issue-68 candidate_ref leaked into stable public API")

    return errors


def _issue_76_normalize_secret_key(name: str) -> str:
    normalized = unicodedata.normalize("NFKC", name)
    output: list[str] = []
    separator_pending = False
    previous_ascii_lower_or_digit = False
    for character in normalized:
        if character.isascii() and character.isalnum():
            if separator_pending and output and output[-1] != "_":
                output.append("_")
            if (
                character.isupper()
                and previous_ascii_lower_or_digit
                and output
                and output[-1] != "_"
            ):
                output.append("_")
            output.append(character.lower())
            separator_pending = False
            previous_ascii_lower_or_digit = character.islower() or character.isdigit()
        else:
            separator_pending = True
            previous_ascii_lower_or_digit = False
    return re.sub(r"_+", "_", "".join(output)).strip("_")


def issue_76_secret_boundary_errors(value: object) -> list[str]:
    """Reject recursively classified secret keys and string values."""

    errors: list[str] = []

    def visit(candidate: object, path: str) -> None:
        if isinstance(candidate, dict):
            for position, (name, item) in enumerate(candidate.items()):
                normalized = _issue_76_normalize_secret_key(str(name))
                if (
                    normalized in ISSUE76_SECRET_DENYLIST
                    or normalized.replace("_", "")
                    in ISSUE76_SECRET_KEY_COMPACT_DENYLIST
                ):
                    errors.append(f"{path}.field[{position}]: secret-classified field name")
                visit(item, f"{path}.field[{position}]")
        elif isinstance(candidate, list):
            for index, item in enumerate(candidate):
                visit(item, f"{path}[{index}]")
        elif isinstance(candidate, str):
            normalized = unicodedata.normalize("NFKC", candidate).strip()
            if ISSUE76_PRIVATE_PEM_PATTERN.search(normalized):
                errors.append(f"{path}: PEM private-key material")
            elif ISSUE76_BEARER_VALUE_PATTERN.match(normalized):
                errors.append(f"{path}: bearer credential material")

    visit(value, "$")
    return errors


def _issue_84_local_source_contradiction_errors(text: str) -> list[str]:
    """Reject permissive contradictions inside the local-source contract window."""

    if (
        text.count(ISSUE84_LOCAL_SOURCE_HEADING) != 1
        or text.count(ISSUE84_LOCAL_SOURCE_END_HEADING) != 1
    ):
        return [
            f"{ISSUE76_API_REL}: issue-84 local source contract window is not unique"
        ]

    start = text.index(ISSUE84_LOCAL_SOURCE_HEADING)
    end = text.find(ISSUE84_LOCAL_SOURCE_END_HEADING, start)
    if end <= start:
        return [
            f"{ISSUE76_API_REL}: issue-84 local source contract window is malformed"
        ]

    violations: set[str] = set()
    for _, unit in _semantic_units(text[start:end]):
        tokens = _semantic_tokens(unit)
        if not tokens:
            continue

        multiplicity = (
            any(
                token in {"additional", "another", "multiple", "second", "two"}
                for token in tokens
            )
            or _contains_phrase(tokens, ("more", "than", "one"))
        )
        multiplicity_actions = _action_indices(
            tokens,
            ISSUE84_SOURCE_MULTIPLICITY_ACTIONS,
        )
        if (
            multiplicity
            and "generic" in tokens
            and "client" in tokens
            and any(token in {"feature", "source"} for token in tokens)
            and multiplicity_actions
            and _has_unnegated_action(tokens, multiplicity_actions)
        ):
            violations.add(
                "issue-84 permits more than one local Generic/client source"
            )

        projection_surface = (
            "graphql" in tokens
            or ("semantic" in tokens and "projection" in tokens)
            or (
                "public" in tokens
                and "redacted" in tokens
                and "evidence" in tokens
            )
        )
        projection_actions = _action_indices(
            tokens,
            ISSUE84_SOURCE_PROJECTION_ACTIONS,
        )
        if (
            projection_surface
            and any(token in {"feature", "local", "source"} for token in tokens)
            and projection_actions
            and _has_unnegated_action(tokens, projection_actions)
        ):
            violations.add(
                "issue-84 permits local source projection into an excluded surface"
            )

        outside_lifecycle = (
            _contains_phrase(tokens, ("before", "service", "setup"))
            or _contains_phrase(tokens, ("prior", "to", "service", "setup"))
            or _contains_phrase(tokens, ("after", "network", "start"))
            or _contains_phrase(tokens, ("following", "network", "start"))
            or (
                "outside" in tokens
                and "setup" in tokens
                and "start" in tokens
            )
        )
        lifecycle_actions = _action_indices(
            tokens,
            ISSUE84_SOURCE_LIFECYCLE_ACTIONS,
        )
        if (
            outside_lifecycle
            and lifecycle_actions
            and _has_unnegated_action(tokens, lifecycle_actions)
        ):
            violations.add(
                "issue-84 permits provisioning outside post-Setup/pre-Start"
            )

    return [f"{ISSUE76_API_REL}: {violation}" for violation in sorted(violations)]


def _issue_76_machine_contract_errors(root: Path) -> list[str]:
    """Validate the closed M6.25 raw feature machine contract."""
    path = root / ISSUE76_SCHEMA_REL
    if not path.is_file() or path.is_symlink():
        return [f"{ISSUE76_SCHEMA_REL}: issue-76 machine contract is missing"]
    try:
        schema = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return [f"{ISSUE76_SCHEMA_REL}: issue-76 machine contract is not valid JSON"]
    if not isinstance(schema, dict):
        return [f"{ISSUE76_SCHEMA_REL}: issue-76 machine contract root must be an object"]

    errors: list[str] = []
    properties = schema.get("properties")
    expected_root = {
        "contract": "helianthus.eebus.raw-feature-runtime.v1",
        "namespace": "eebus.v1",
        "mask_tier": "raw",
        "transport": "owner-only-af-unix",
        "public_contact_policy": "deny-before-provider-router-runtime-contact",
        "read_auth_scope": "eebus.raw.read",
        "write_auth_scope": "eebus.raw.write",
    }
    if (
        schema.get("type") != "object"
        or schema.get("additionalProperties") is not False
        or set(schema.get("required", [])) != set(expected_root)
        or not isinstance(properties, dict)
        or set(properties) != set(expected_root)
    ):
        errors.append(f"{ISSUE76_SCHEMA_REL}: issue-76 root contract is not closed")
        properties = properties if isinstance(properties, dict) else {}
    for name, expected in expected_root.items():
        definition = properties.get(name)
        if not isinstance(definition, dict) or definition.get("const") != expected:
            label = "public contact" if name == "public_contact_policy" else name
            errors.append(f"{ISSUE76_SCHEMA_REL}: issue-76 {label} binding is not exact")

    definitions = schema.get("$defs")
    if not isinstance(definitions, dict):
        errors.append(f"{ISSUE76_SCHEMA_REL}: issue-76 closed definitions are missing")
        definitions = {}

    tools = definitions.get("ToolV1")
    if not isinstance(tools, dict) or set(tools.get("enum", [])) != ISSUE76_TOOL_NAMES:
        errors.append(f"{ISSUE76_SCHEMA_REL}: issue-76 exact tool inventory is not closed")
    if schema.get("x-tool-scopes") != ISSUE76_TOOL_SCOPES:
        errors.append(f"{ISSUE76_SCHEMA_REL}: issue-76 tool scope map is not exact")

    expected_tool_contracts = {
        "eebus.v1.features.get": {
            "request": "FeaturesGetRequestV1",
            "data": "FeaturesGetDataV1",
            "remoteContact": False,
        },
        "eebus.v1.features.data.get": {
            "request": "FeatureDataGetRequestV1",
            "data": "FeatureDataGetDataV1",
            "remoteContact": True,
        },
        "eebus.v1.features.data.set": {
            "request": "FeatureDataSetRequestV1",
            "data": "MutationV1",
            "remoteContact": True,
        },
        "eebus.v1.mutations.get": {
            "request": "MutationGetRequestV1",
            "data": "MutationV1",
            "remoteContact": False,
        },
        "eebus.v1.mutations.rollback": {
            "request": "MutationRollbackRequestV1",
            "data": "MutationV1",
            "remoteContact": True,
        },
    }
    if schema.get("x-tool-contracts") != expected_tool_contracts:
        errors.append(f"{ISSUE76_SCHEMA_REL}: issue-76 tool request/data map is not exact")

    states = definitions.get("MutationStateV1")
    if not isinstance(states, dict) or set(states.get("enum", [])) != ISSUE76_MUTATION_STATES:
        errors.append(f"{ISSUE76_SCHEMA_REL}: issue-76 mutation state set is not exact")
    mode = definitions.get("ModeV1")
    if not isinstance(mode, dict) or mode.get("enum") != ["apply", "probe"]:
        errors.append(f"{ISSUE76_SCHEMA_REL}: issue-76 mutation mode set is not exact")

    expected_command_path = [
        "MCP",
        "gateway EEBusCommandRouter",
        "eebusreg RawFeatureRuntimeV1 or RawMutationRuntimeV1",
        "eebusreg internal durable mutation coordinator for mutation methods",
        "eebus-go exact feature executor",
        "spine-go atomic correlated round trip",
        "existing SHIP session",
    ]
    if schema.get("x-command-path") != expected_command_path:
        errors.append(f"{ISSUE76_SCHEMA_REL}: issue-76 command path is not exact")
    if schema.get("x-runtime-admission") != ISSUE84_RUNTIME_ADMISSION:
        errors.append(
            f"{ISSUE76_SCHEMA_REL}: issue-84 runtime admission precedence is not exact"
        )
    if schema.get("x-local-protocol-source") != ISSUE84_LOCAL_PROTOCOL_SOURCE:
        errors.append(
            f"{ISSUE76_SCHEMA_REL}: issue-84 local protocol source is not exact"
        )

    expected_runtime_api = {
        "RawFeatureRuntimeV1": {
            "readOnly": True,
            "compatibility": "unchanged",
            "methods": [
                "FeaturesGet(context.Context, eebusraw.ReadAuthorizationV1, "
                "eebusraw.FeaturesGetRequestV1) (eebusraw.FeaturesGetDataV1, "
                "*eebusraw.ErrorV1)",
                "FeaturesDataGet(context.Context, eebusraw.ReadAuthorizationV1, "
                "eebusraw.FeatureDataGetRequestV1) "
                "(eebusraw.FeatureDataGetDataV1, *eebusraw.ErrorV1)",
            ],
        },
        "RawMutationRuntimeV1": {
            "methods": [
                "FeaturesDataSet(context.Context, eebusraw.WriteAuthorizationV1, "
                "eebusraw.FeatureDataSetRequestV1) (eebusraw.MutationV1, "
                "*eebusraw.ErrorV1)",
                "MutationsGet(context.Context, eebusraw.ReadAuthorizationV1, "
                "eebusraw.MutationGetRequestV1) (eebusraw.MutationV1, "
                "*eebusraw.ErrorV1)",
                "MutationsRollback(context.Context, eebusraw.WriteAuthorizationV1, "
                "eebusraw.MutationRollbackRequestV1) (eebusraw.MutationV1, "
                "*eebusraw.ErrorV1)",
            ],
            "coordinator": "internal",
            "gatewayCapabilityAssertion": "required-fail-closed",
        },
        "Runtime": {
            "methodSet": "unchanged",
            "embeds": ["RawFeatureRuntimeV1"],
            "methods": [
                "Start(context.Context) error",
                "Shutdown() error",
                "Snapshot() (SnapshotV1, error)",
                "PairingState() ([]PairingObservationV1, error)",
            ],
            "doesNotEmbed": ["RawMutationRuntimeV1"],
            "concreteImplementationMaySatisfy": [
                "RawFeatureRuntimeV1",
                "RawMutationRuntimeV1",
            ],
        },
    }
    if schema.get("x-public-runtime-api") != expected_runtime_api:
        errors.append(f"{ISSUE76_SCHEMA_REL}: issue-78 runtime interface split is not exact")

    expected_authorization_validators = {
        "ValidateReadAuthorizationV1": {
            "authorization": "ReadAuthorizationV1",
            "scope": "AuthScopeV1RawRead",
            "tools": [
                "eebus.v1.features.get",
                "eebus.v1.features.data.get",
                "eebus.v1.mutations.get",
            ],
            "compatibility": "unchanged",
        },
        "ValidateWriteAuthorizationV1": {
            "authorization": "WriteAuthorizationV1",
            "scope": "AuthScopeV1RawWrite",
            "tools": [
                "eebus.v1.features.data.set",
                "eebus.v1.mutations.rollback",
            ],
        },
    }
    if schema.get("x-authorization-validators") != expected_authorization_validators:
        errors.append(f"{ISSUE76_SCHEMA_REL}: issue-78 authorization split is not exact")

    expected_authorizations = {
        "ReadAuthorizationV1": {
            "scope": "AuthScopeV1RawRead",
            "tools": {
                "eebus.v1.features.get",
                "eebus.v1.features.data.get",
                "eebus.v1.mutations.get",
            },
        },
        "WriteAuthorizationV1": {
            "scope": "AuthScopeV1RawWrite",
            "tools": {
                "eebus.v1.features.data.set",
                "eebus.v1.mutations.rollback",
            },
        },
    }
    for name, expected in expected_authorizations.items():
        authorization = definitions.get(name)
        authorization_properties = (
            authorization.get("properties", {})
            if isinstance(authorization, dict)
            else {}
        )
        if (
            not isinstance(authorization, dict)
            or authorization.get("additionalProperties") is not False
            or set(authorization.get("required", []))
            != {"principal_class", "scope", "tool", "mask_tier"}
            or authorization_properties.get("scope")
            != {"$ref": f"#/$defs/{expected['scope']}"}
            or set(authorization_properties.get("tool", {}).get("enum", []))
            != expected["tools"]
        ):
            errors.append(
                f"{ISSUE76_SCHEMA_REL}: issue-78 {name} is not exact and distinct"
            )
    for name, value in {
        "AuthScopeV1RawRead": "eebus.raw.read",
        "AuthScopeV1RawWrite": "eebus.raw.write",
    }.items():
        if definitions.get(name) != {"const": value}:
            errors.append(f"{ISSUE76_SCHEMA_REL}: issue-78 {name} is not exact")

    expected_round_trip = {
        "registerWaiterBeforeSend": True,
        "completeExactlyOnce": True,
        "cleanupOnEveryTerminalPath": True,
        "generationBoundMonotonicKey": True,
        "retainGenerationTombstone": True,
        "rejectRetiredKeyReuse": True,
        "lateReplyCannotCompleteSuccessor": True,
    }
    if schema.get("x-round-trip") != expected_round_trip:
        errors.append(f"{ISSUE76_SCHEMA_REL}: issue-76 round trip contract is not exact")
    if (
        schema.get("x-read-observation-invariants")
        != ISSUE86_READ_OBSERVATION_INVARIANTS
    ):
        errors.append(
            f"{ISSUE76_SCHEMA_REL}: issue-86 read observation invariants are not exact"
        )

    protocol_message = definitions.get("ProtocolMessageV1")
    protocol_message_properties = (
        protocol_message.get("properties", {})
        if isinstance(protocol_message, dict)
        else {}
    )
    if (
        not isinstance(protocol_message, dict)
        or protocol_message.get("additionalProperties") is not False
        or set(protocol_message.get("required", []))
        != {"classifier", "correlation_key", "function"}
        or protocol_message_properties.get("data")
        != {"$ref": "#/$defs/TypedValueV1"}
    ):
        errors.append(
            f"{ISSUE76_SCHEMA_REL}: issue-86 optional protocol message data is not exact"
        )

    expected_read_request_message = {
        "allOf": [
            {"$ref": "#/$defs/ProtocolMessageV1"},
            {
                "type": "object",
                "properties": {
                    "classifier": {"const": "READ"},
                    "data": {"$ref": "#/$defs/VerifiedTypedValueV1"},
                },
                "not": {"required": ["error_number"]},
            },
        ]
    }
    expected_read_response_message = {
        "allOf": [
            {"$ref": "#/$defs/ProtocolMessageV1"},
            {
                "type": "object",
                "required": ["data"],
                "properties": {
                    "classifier": {"const": "REPLY"},
                    "data": {"$ref": "#/$defs/VerifiedTypedValueV1"},
                },
                "not": {"required": ["error_number"]},
            },
        ]
    }
    if definitions.get("FullReadRequestMessageV1") != expected_read_request_message:
        errors.append(
            f"{ISSUE76_SCHEMA_REL}: issue-86 READ request message is not exact"
        )
    if definitions.get("FullReadResponseMessageV1") != expected_read_response_message:
        errors.append(
            f"{ISSUE76_SCHEMA_REL}: issue-86 READ response message is not exact"
        )

    read_observation_properties = (
        definitions.get("ReadObservationV1", {}).get("properties", {})
        if isinstance(definitions.get("ReadObservationV1"), dict)
        else {}
    )
    read_failure_properties = (
        definitions.get("ReadFailureV1", {}).get("properties", {})
        if isinstance(definitions.get("ReadFailureV1"), dict)
        else {}
    )
    expected_read_bindings = {
        "target": {"$ref": "#/$defs/ReadFeatureTargetV1"},
        "raw_request": {"$ref": "#/$defs/FullReadRequestMessageV1"},
        "raw_response": {"$ref": "#/$defs/FullReadResponseMessageV1"},
    }
    if (
        any(
            read_observation_properties.get(field) != expected
            for field, expected in expected_read_bindings.items()
        )
        or read_failure_properties.get("target")
        != {"$ref": "#/$defs/ReadFeatureTargetV1"}
    ):
        errors.append(
            f"{ISSUE76_SCHEMA_REL}: issue-86 READ result bindings are not exact"
        )
    if schema.get("x-secret-denylist") != ISSUE76_SECRET_DENYLIST:
        errors.append(f"{ISSUE76_SCHEMA_REL}: issue-76 secret exclusion is not exact")
    if schema.get("x-secret-boundary") != ISSUE76_SECRET_BOUNDARY:
        errors.append(f"{ISSUE76_SCHEMA_REL}: issue-76 secret boundary is not exact")

    typed_scalar = definitions.get("TypedScalarV1")
    scalar_variants = (
        typed_scalar.get("oneOf", []) if isinstance(typed_scalar, dict) else []
    )
    string_variants = [
        item
        for item in scalar_variants
        if isinstance(item, dict) and item.get("type") == "string"
    ]
    if (
        len(string_variants) != 1
        or string_variants[0].get("not")
        != {"$ref": "#/$defs/SecretScalarPatternV1"}
    ):
        errors.append(
            f"{ISSUE76_SCHEMA_REL}: issue-76 recursive secret value rejection is missing"
        )

    for name in ("TypedValueDepth3V1", "TypedValueDepth2V1", "TypedValueV1"):
        definition = definitions.get(name)
        variants = definition.get("oneOf", []) if isinstance(definition, dict) else []
        object_variants = [
            item
            for item in variants
            if isinstance(item, dict) and item.get("type") == "object"
        ]
        if (
            len(object_variants) != 1
            or object_variants[0].get("propertyNames")
            != {"$ref": "#/$defs/SafeRawFieldNameV1"}
            or not isinstance(object_variants[0].get("patternProperties"), dict)
            or False not in object_variants[0]["patternProperties"].values()
        ):
            errors.append(
                f"{ISSUE76_SCHEMA_REL}: issue-76 recursive secret key rejection "
                f"is missing from {name}"
            )

    target = definitions.get("FeatureTargetV1")
    locator = definitions.get("FeatureLocatorV1")
    expected_target_fields = {
        "remote_ski",
        "ship_id",
        "device_address",
        "entity_address",
        "feature_address",
        "feature_type",
        "feature_role",
        "function",
        "operation",
    }
    if (
        not isinstance(target, dict)
        or target.get("additionalProperties") is not False
        or set(target.get("required", [])) != expected_target_fields
        or set(target.get("properties", {})) != expected_target_fields
    ):
        errors.append(f"{ISSUE76_SCHEMA_REL}: issue-76 exact target binding is not closed")
    expected_read_target = {
        "allOf": [
            {"$ref": "#/$defs/FeatureTargetV1"},
            {
                "type": "object",
                "properties": {"operation": {"const": "READ"}},
            },
        ]
    }
    if definitions.get("ReadFeatureTargetV1") != expected_read_target:
        errors.append(
            f"{ISSUE76_SCHEMA_REL}: issue-86 READ target binding is not exact"
        )
    if definitions.get("NativeFeatureTypeV1") != ISSUE84_NATIVE_FEATURE_TYPE:
        errors.append(
            f"{ISSUE76_SCHEMA_REL}: issue-84 native feature type is not exact"
        )
    for name, definition in (
        ("FeatureLocatorV1", locator),
        ("FeatureTargetV1", target),
    ):
        feature_type = (
            definition.get("properties", {}).get("feature_type")
            if isinstance(definition, dict)
            else None
        )
        if feature_type != {"$ref": "#/$defs/NativeFeatureTypeV1"}:
            errors.append(
                f"{ISSUE76_SCHEMA_REL}: issue-84 {name} feature_type "
                "does not preserve native topology casing"
            )

    operations = definitions.get("FullOperationsV1")
    if (
        not isinstance(operations, dict)
        or operations.get("additionalProperties") is not False
        or set(operations.get("required", [])) != {"read", "write"}
        or set(operations.get("properties", {})) != {"read", "write"}
    ):
        errors.append(f"{ISSUE76_SCHEMA_REL}: issue-76 full operation set is not exact")

    runtime = definitions.get("RuntimeBindingV1")
    if (
        not isinstance(runtime, dict)
        or runtime.get("additionalProperties") is not False
        or set(runtime.get("required", []))
        != {"runtime_epoch", "connection_generation"}
        or set(runtime.get("properties", {}))
        != {"runtime_epoch", "connection_generation"}
    ):
        errors.append(f"{ISSUE76_SCHEMA_REL}: issue-76 epoch/generation binding is not exact")

    request_contracts = {
        "FeaturesGetRequestV1": {"target"},
        "FeatureDataGetRequestV1": {"targets"},
        "FeatureDataSetRequestV1": {
            "target",
            "value",
            "read_token",
            "idempotency_key",
            "mode",
        },
        "MutationGetRequestV1": {"mutation_ref"},
        "MutationRollbackRequestV1": {"mutation_ref", "idempotency_key"},
    }
    for name, required in request_contracts.items():
        definition = definitions.get(name)
        if (
            not isinstance(definition, dict)
            or definition.get("additionalProperties") is not False
            or set(definition.get("required", [])) != required
        ):
            label = "write token" if name == "FeatureDataSetRequestV1" else name
            errors.append(f"{ISSUE76_SCHEMA_REL}: issue-76 {label} request is not exact")

    read_request = definitions.get("FeatureDataGetRequestV1")
    read_request_properties = (
        read_request.get("properties", {}) if isinstance(read_request, dict) else {}
    )
    read_targets = read_request_properties.get("targets")
    if (
        not isinstance(read_request, dict)
        or read_request.get("additionalProperties") is not False
        or set(read_request.get("required", [])) != {"targets"}
        or set(read_request_properties) != {"targets", "timeout_ms"}
        or not isinstance(read_targets, dict)
        or read_targets.get("items")
        != {"$ref": "#/$defs/ReadFeatureTargetV1"}
    ):
        errors.append(
            f"{ISSUE76_SCHEMA_REL}: issue-86 READ request closed property set "
            "is not exact"
        )

    set_request = definitions.get("FeatureDataSetRequestV1")
    expected_set_properties = {
        "target",
        "value",
        "read_token",
        "expected_current",
        "idempotency_key",
        "mode",
        "probe_ttl_seconds",
        "constraints_override",
    }
    if (
        not isinstance(set_request, dict)
        or set(set_request.get("properties", {})) != expected_set_properties
    ):
        errors.append(f"{ISSUE76_SCHEMA_REL}: issue-76 write token/CAS shape is not closed")

    mutation = definitions.get("MutationV1")
    expected_mutation_required = {
        "mutation_ref",
        "state",
        "mode",
        "target",
        "runtime",
        "before",
        "requested",
        "protocol_accepted",
        "observed_after",
        "audit",
    }
    if (
        not isinstance(mutation, dict)
        or mutation.get("additionalProperties") is not False
        or set(mutation.get("required", [])) != expected_mutation_required
    ):
        errors.append(f"{ISSUE76_SCHEMA_REL}: issue-76 durable mutation record is not exact")

    mutation_variants = mutation.get("oneOf", []) if isinstance(mutation, dict) else []
    mutation_by_state: dict[str, dict[str, Any]] = {}
    for variant in mutation_variants:
        if not isinstance(variant, dict):
            continue
        variant_properties = variant.get("properties")
        if not isinstance(variant_properties, dict):
            continue
        state_schema = variant_properties.get("state")
        if isinstance(state_schema, dict) and isinstance(state_schema.get("const"), str):
            mutation_by_state[state_schema["const"]] = variant
    if (
        len(mutation_variants) != len(ISSUE76_MUTATION_STATES)
        or set(mutation_by_state) != ISSUE76_MUTATION_STATES
    ):
        errors.append(
            f"{ISSUE76_SCHEMA_REL}: issue-76 mutation state oneOf is not exact"
        )

    pending_evidence = {
        "rollback",
        "error",
        "apply_verification",
        "conflict_evidence",
        "no_contact_evidence",
        "rejection_verification",
        "outcome_evidence",
    }
    for state in ("reply_observed", "verify_pending"):
        variant = mutation_by_state.get(state)
        variant_properties = (
            variant.get("properties", {}) if isinstance(variant, dict) else {}
        )
        exclusion = variant.get("not") if isinstance(variant, dict) else None
        alternatives = (
            exclusion.get("anyOf", []) if isinstance(exclusion, dict) else []
        )
        excluded_fields = {
            next(iter(required))
            for candidate in alternatives
            if isinstance(candidate, dict)
            and len(required := set(candidate.get("required", []))) == 1
        }
        if (
            variant_properties.get("protocol_accepted") != {"type": "boolean"}
            or variant_properties.get("observed_after") != {"type": "null"}
            or excluded_fields != pending_evidence
        ):
            errors.append(
                f"{ISSUE76_SCHEMA_REL}: issue-87 correlated {state} "
                "boolean checkpoint is not exact"
            )

    terminal_evidence = {
        "applied": {"apply_verification"},
        "rolled_back": {"apply_verification", "rollback"},
        "no_effect": {"error", "outcome_evidence", "no_effect_verification"},
        "outcome_unknown": {"error", "outcome_evidence"},
        "conflict": {"error", "conflict_evidence"},
        "failed_no_contact": {"error", "no_contact_evidence"},
        "rejected": {"error", "rejection_verification"},
    }
    for state, required_evidence in terminal_evidence.items():
        variant = mutation_by_state.get(state)
        if not isinstance(variant, dict) or set(variant.get("required", [])) != required_evidence:
            errors.append(
                f"{ISSUE76_SCHEMA_REL}: issue-76 {state} evidence is not exact"
            )
    no_effect_variant = mutation_by_state.get("no_effect", {})
    expected_no_effect_outcome = {
        "allOf": [
            {"$ref": "#/$defs/OutcomeEvidenceV1"},
            {
                "properties": {
                    "last_durable_state": {"const": "dispatch_intent"},
                }
            },
        ]
    }
    if (
        not isinstance(no_effect_variant, dict)
        or no_effect_variant.get("properties", {}).get("outcome_evidence")
        != expected_no_effect_outcome
    ):
        errors.append(
            f"{ISSUE76_SCHEMA_REL}: issue-76 no_effect original-write evidence is not exact"
        )
    conflict_variant = mutation_by_state.get("conflict", {})
    expected_conflict_acceptance = [
        {
            "required": ["outcome_evidence"],
            "properties": {"protocol_accepted": {"type": "null"}},
        },
        {
            "properties": {"protocol_accepted": {"type": "boolean"}},
            "not": {"required": ["outcome_evidence"]},
        },
    ]
    if (
        not isinstance(conflict_variant, dict)
        or conflict_variant.get("anyOf") != expected_conflict_acceptance
    ):
        errors.append(
            f"{ISSUE76_SCHEMA_REL}: issue-76 conflict uncertainty evidence is not exact"
        )

    rollback_intermediate_states = {
        "rollback_intent",
        "rollback_dispatch_intent",
        "rollback_reply_observed",
        "rollback_verify_pending",
    }
    forbidden_terminal_evidence = {
        "error",
        "conflict_evidence",
        "no_contact_evidence",
        "rejection_verification",
        "outcome_evidence",
    }
    for state in rollback_intermediate_states:
        variant = mutation_by_state.get(state)
        exclusion = variant.get("not") if isinstance(variant, dict) else None
        alternatives = (
            exclusion.get("anyOf", []) if isinstance(exclusion, dict) else []
        )
        excluded_fields = {
            next(iter(required))
            for candidate in alternatives
            if isinstance(candidate, dict)
            and len(required := set(candidate.get("required", []))) == 1
        }
        if excluded_fields != forbidden_terminal_evidence:
            errors.append(
                f"{ISSUE76_SCHEMA_REL}: issue-76 {state} terminal evidence "
                "exclusion is not exact"
            )

    evidence_contracts = {
        "ApplyVerificationV1": {
            "relation",
            "verified",
            "equal_value_hash",
            "verified_at",
        },
        "RollbackVerificationV1": {
            "relation",
            "verified",
            "equal_value_hash",
            "verified_at",
        },
        "ConflictEvidenceV1": {
            "relation",
            "verified",
            "before_hash",
            "requested_hash",
            "observed_after_hash",
            "verified_at",
        },
        "NoContactEvidenceV1": {
            "remote_frames_sent",
            "last_completed_phase",
            "verified_at",
        },
        "RejectionVerificationV1": {
            "relation",
            "verified",
            "correlated_rejection",
            "equal_value_hash",
            "verified_at",
        },
        "NoEffectVerificationV1": {
            "relation",
            "verified",
            "equal_value_hash",
            "verified_at",
        },
        "OutcomeEvidenceV1": {
            "possible_side_effect",
            "blind_retry_forbidden",
            "last_durable_state",
            "recorded_at",
        },
    }
    for name, required in evidence_contracts.items():
        definition = definitions.get(name)
        if (
            not isinstance(definition, dict)
            or definition.get("additionalProperties") is not False
            or set(definition.get("required", [])) != required
        ):
            errors.append(
                f"{ISSUE76_SCHEMA_REL}: issue-76 {name} is not a closed evidence record"
            )

    no_effect = mutation_by_state.get("no_effect")
    no_effect_properties = (
        no_effect.get("properties", {}) if isinstance(no_effect, dict) else {}
    )
    no_effect_error = no_effect_properties.get("error", {})
    no_effect_error_properties = (
        no_effect_error.get("properties", {})
        if isinstance(no_effect_error, dict)
        else {}
    )
    if (
        no_effect_properties.get("protocol_accepted") != {"type": "null"}
        or no_effect_properties.get("observed_after")
        != {"$ref": "#/$defs/VerifiedTypedValueV1"}
        or no_effect_error_properties.get("code") != {"const": "no_effect"}
        or no_effect_error_properties.get("retriable") != {"const": False}
    ):
        errors.append(f"{ISSUE76_SCHEMA_REL}: issue-78 no_effect terminal shape is not exact")

    for state in ("applied", "probe_active"):
        recovered = mutation_by_state.get(state)
        alternatives = recovered.get("anyOf", []) if isinstance(recovered, dict) else []
        if len(alternatives) != 2 or not any(
            isinstance(candidate, dict)
            and set(candidate.get("required", [])) == {"outcome_evidence"}
            and candidate.get("properties", {}).get("protocol_accepted")
            == {"type": "null"}
            for candidate in alternatives
        ):
            errors.append(
                f"{ISSUE76_SCHEMA_REL}: issue-78 uncertain {state} recovery is not exact"
            )

    rollback = definitions.get("RollbackV1")
    rollback_variants = rollback.get("oneOf", []) if isinstance(rollback, dict) else []
    rollback_by_state = {
        state_schema["const"]: variant
        for variant in rollback_variants
        if isinstance(variant, dict)
        and isinstance(variant.get("properties"), dict)
        and isinstance(
            state_schema := variant["properties"].get("state"),
            dict,
        )
        and isinstance(state_schema.get("const"), str)
    }
    if (
        len(rollback_variants) != 5
        or set(rollback_by_state)
        != {
            "rollback_intent",
            "rollback_dispatch_intent",
            "rollback_reply_observed",
            "rollback_verify_pending",
            "rolled_back",
        }
    ):
        errors.append(
            f"{ISSUE76_SCHEMA_REL}: issue-76 rollback state oneOf is not exact"
        )
    for state in ("rollback_reply_observed", "rollback_verify_pending"):
        variant = rollback_by_state.get(state)
        variant_properties = (
            variant.get("properties", {}) if isinstance(variant, dict) else {}
        )
        exclusion = variant.get("not") if isinstance(variant, dict) else None
        alternatives = (
            exclusion.get("anyOf", []) if isinstance(exclusion, dict) else []
        )
        excluded_fields = {
            next(iter(required))
            for candidate in alternatives
            if isinstance(candidate, dict)
            and len(required := set(candidate.get("required", []))) == 1
        }
        if (
            variant_properties.get("protocol_accepted") != {"type": "boolean"}
            or variant_properties.get("observed_after") != {"type": "null"}
            or excluded_fields != {"verification", "error"}
        ):
            errors.append(
                f"{ISSUE76_SCHEMA_REL}: issue-87 correlated {state} "
                "boolean checkpoint is not exact"
            )
    rolled_back_rollback = rollback_by_state.get("rolled_back")
    rolled_back_rollback_properties = (
        rolled_back_rollback.get("properties", {})
        if isinstance(rolled_back_rollback, dict)
        else {}
    )
    if "protocol_accepted" in rolled_back_rollback_properties:
        errors.append(
            f"{ISSUE76_SCHEMA_REL}: issue-87 rolled_back must preserve nullable "
            "correlated acceptance"
        )

    envelope = definitions.get("EnvelopeV1")
    envelope_variants = envelope.get("oneOf", []) if isinstance(envelope, dict) else []
    if (
        not isinstance(envelope, dict)
        or envelope.get("additionalProperties") is not False
        or set(envelope.get("required", [])) != {"meta", "request", "data", "error"}
    ):
        errors.append(
            f"{ISSUE76_SCHEMA_REL}: issue-76 envelope shape is not closed"
        )

    def ref_name(candidate: object) -> str | None:
        if not isinstance(candidate, dict):
            return None
        reference = candidate.get("$ref")
        prefix = "#/$defs/"
        if isinstance(reference, str) and reference.startswith(prefix):
            return reference.removeprefix(prefix)
        return None

    def nullable_ref_name(candidate: object) -> str | None:
        direct = ref_name(candidate)
        if direct is not None:
            return direct
        if not isinstance(candidate, dict) or not isinstance(
            variants := candidate.get("oneOf"), list
        ):
            return None
        references = {
            name for variant in variants if (name := ref_name(variant)) is not None
        }
        null_count = sum(
            isinstance(variant, dict) and variant.get("type") == "null"
            for variant in variants
        )
        if len(variants) != 2 or len(references) != 1 or null_count != 1:
            return None
        return f"{references.pop()}|null"

    meta_runtime = (
        definitions.get("EnvelopeMetaV1", {})
        .get("properties", {})
        .get("runtime", {})
    )
    if nullable_ref_name(meta_runtime) != "RuntimeBindingV1|null":
        errors.append(
            f"{ISSUE76_SCHEMA_REL}: issue-82 pre-runtime binding is not exact"
        )

    expected_dto_validation = {
        "owner": "Project-Helianthus/helianthus-eebusreg/eebusraw",
        "requestValidators": list(ISSUE82_CANONICAL_DTO_VALIDATORS[:3]),
        "resultValidators": list(ISSUE82_CANONICAL_DTO_VALIDATORS[3:]),
        "signatures": ISSUE82_CANONICAL_DTO_VALIDATOR_SIGNATURES,
        "gatewayResidualResponsibilities": list(
            ISSUE82_GATEWAY_RESIDUAL_RESPONSIBILITIES
        ),
        "gatewayMustNotReimplement": "closed DTO semantics",
    }
    if schema.get("x-canonical-dto-validation") != expected_dto_validation:
        errors.append(
            f"{ISSUE76_SCHEMA_REL}: issue-82 canonical DTO validator inventory is not exact"
        )

    if schema.get("x-wal-restore-policy") != ISSUE87_WAL_RESTORE_POLICY:
        errors.append(
            f"{ISSUE76_SCHEMA_REL}: issue-87 WAL restore policy is not exact"
        )

    for obsolete_definition in (
        "PreBindingErrorCodeV1",
        "PostBindingErrorCodeV1",
    ):
        if obsolete_definition in definitions:
            errors.append(
                f"{ISSUE76_SCHEMA_REL}: issue-92 error binding must not be classified by code"
            )

    error_code_definition = definitions.get("ErrorCodeV1")
    if (
        not isinstance(error_code_definition, dict)
        or error_code_definition.get("type") != "string"
        or error_code_definition.get("enum") != list(ISSUE92_ERROR_CODES)
    ):
        errors.append(
            f"{ISSUE76_SCHEMA_REL}: issue-92 error vocabulary is not exact"
        )

    unbound_source_layer = definitions.get("UnboundErrorSourceLayerV1")
    if (
        not isinstance(unbound_source_layer, dict)
        or unbound_source_layer.get("type") != "string"
        or unbound_source_layer.get("enum")
        != [
            "mcp",
            "gateway-router",
            "eebusreg-runtime",
            "eebusreg-coordinator",
        ]
    ):
        errors.append(
            f"{ISSUE76_SCHEMA_REL}: issue-92 unbound error source layers are not exact"
        )

    expected_envelope_implications = [
        {
            "if": {
                "properties": {"error": {"type": "null"}},
                "required": ["error"],
            },
            "then": {
                "properties": {
                    "meta": {
                        "properties": {
                            "runtime": {"$ref": "#/$defs/RuntimeBindingV1"}
                        }
                    },
                    "request": {"not": {"type": "null"}},
                }
            },
        },
        {
            "if": {
                "properties": {
                    "error": {
                        "type": "object",
                        "properties": {"code": {"const": "partial_result"}},
                        "required": ["code"],
                    }
                },
                "required": ["error"],
            },
            "then": {
                "properties": {
                    "meta": {
                        "properties": {
                            "runtime": {"$ref": "#/$defs/RuntimeBindingV1"}
                        }
                    },
                    "request": {"not": {"type": "null"}},
                }
            },
        },
        {
            "if": {
                "properties": {"request": {"type": "null"}},
                "required": ["request"],
            },
            "then": {
                "properties": {
                    "meta": {"properties": {"runtime": {"type": "null"}}},
                    "error": {
                        "type": "object",
                        "properties": {
                            "code": {"const": "invalid_argument"},
                            "source_layer": {"const": "mcp"},
                        },
                        "required": ["code", "source_layer"],
                    },
                }
            },
        },
        {
            "if": {
                "properties": {
                    "meta": {
                        "properties": {"runtime": {"type": "null"}},
                        "required": ["runtime"],
                    }
                },
                "required": ["meta"],
            },
            "then": {
                "properties": {
                    "error": {
                        "type": "object",
                        "properties": {
                            "source_layer": {
                                "$ref": "#/$defs/UnboundErrorSourceLayerV1"
                            }
                        },
                        "required": ["source_layer"],
                    }
                }
            },
        },
    ]
    if (
        not isinstance(envelope, dict)
        or envelope.get("allOf") != expected_envelope_implications
    ):
        errors.append(
            f"{ISSUE76_SCHEMA_REL}: issue-92 envelope implications are not exact"
        )

    envelope_signatures: set[tuple[str, str, str, str, str, str]] = set()
    for variant in envelope_variants:
        if not isinstance(variant, dict) or not isinstance(
            variant.get("properties"), dict
        ):
            continue
        variant_properties = variant["properties"]
        meta = variant_properties.get("meta")
        meta_properties = meta.get("properties", {}) if isinstance(meta, dict) else {}
        tool = meta_properties.get("tool", {}).get("const")
        scope = meta_properties.get("scope", {}).get("const")
        auth_scope = meta_properties.get("auth_scope", {}).get("const")
        request_name = nullable_ref_name(variant_properties.get("request"))
        data_schema = variant_properties.get("data")
        data_name = (
            "null"
            if isinstance(data_schema, dict) and data_schema.get("type") == "null"
            else ref_name(data_schema)
        )
        error_schema = variant_properties.get("error")
        if isinstance(error_schema, dict) and error_schema.get("type") == "null":
            error_name = "null"
        elif ref_name(error_schema) == "ErrorV1":
            error_code = error_schema.get("properties", {}).get("code", {}).get("const")
            error_name = (
                f"ErrorV1:{error_code}" if isinstance(error_code, str) else "ErrorV1"
            )
        else:
            error_name = None
        if all(
            isinstance(item, str)
            for item in (
                tool,
                scope,
                auth_scope,
                request_name,
                data_name,
                error_name,
            )
        ):
            envelope_signatures.add(
                (
                    tool,
                    scope,
                    auth_scope,
                    request_name,
                    data_name,
                    error_name,
                )
            )

    expected_envelope_signatures: set[
        tuple[str, str, str, str, str, str]
    ] = set()
    for tool, contract in expected_tool_contracts.items():
        scope = ISSUE76_TOOL_SCOPES[tool]
        request_name = contract["request"]
        data_name = contract["data"]
        expected_envelope_signatures.add(
            (tool, scope, scope, f"{request_name}|null", data_name, "null")
        )
        expected_envelope_signatures.add(
            (tool, scope, scope, f"{request_name}|null", "null", "ErrorV1")
        )
    expected_envelope_signatures.add(
        (
            "eebus.v1.features.data.get",
            "eebus.raw.read",
            "eebus.raw.read",
            "FeatureDataGetRequestV1|null",
            "FeatureDataGetDataV1",
            "ErrorV1:partial_result",
        )
    )
    if (
        len(envelope_variants) != len(expected_envelope_signatures)
        or envelope_signatures != expected_envelope_signatures
    ):
        errors.append(
            f"{ISSUE76_SCHEMA_REL}: issue-76 discriminated envelope oneOf is not exact"
        )

    serialized = json.dumps(schema, sort_keys=True).casefold()
    for forbidden in (
        "eebus.v2",
        "features.data.invoke",
        "candidate_ref",
        "filterdelete",
        "partialselector",
        "graphql",
        "portal",
        "home assistant",
    ):
        if forbidden in serialized:
            errors.append(f"{ISSUE76_SCHEMA_REL}: issue-76 forbidden machine surface {forbidden!r}")
    return errors


def issue_76_m625_raw_feature_errors(root: Path) -> list[str]:
    """Enforce the additive M6.25 raw feature acquisition contract."""
    errors: list[str] = []

    for rel, expected_sha256 in ISSUE76_M6_LOCKED_ARTIFACTS.items():
        path = root / rel
        if (
            not path.is_file()
            or path.is_symlink()
            or hashlib.sha256(path.read_bytes()).hexdigest() != expected_sha256
        ):
            errors.append(
                f"{rel}: issue-76 prior M6 artifact must remain byte-identical"
            )

    document_texts: dict[Path, str] = {}
    for rel in ISSUE76_DOCUMENT_RELS:
        path = root / rel
        if not path.is_file() or path.is_symlink():
            errors.append(f"{rel}: issue-76 canonical document is missing")
            continue
        document_texts[rel] = _read(path)

    for rel, markers in ISSUE76_REQUIRED_MARKERS.items():
        text = document_texts.get(rel, "")
        normalized = " ".join(text.split()).casefold()
        for marker in markers:
            if marker.casefold() not in normalized:
                errors.append(f"{rel}: issue-76 required contract marker is missing")

    for rel, text in document_texts.items():
        for peer in ISSUE76_DOCUMENT_RELS:
            if peer != rel and peer.name not in text:
                errors.append(
                    f"{rel}: issue-76 cross-domain link to {peer.name} is missing"
                )

    protocol = document_texts.get(ISSUE76_PROTOCOL_REL, "")
    for source_commit in (
        "7383c108f72309c3636d" "896948d7a8de6d001708",
        "0134afee59535d927d63b" "78070f828f0f6fb553d",
    ):
        if source_commit not in protocol:
            errors.append(
                f"{ISSUE76_PROTOCOL_REL}: issue-76 publishable source pin is missing"
            )
    architecture = document_texts.get(ISSUE76_ARCHITECTURE_REL, "")
    if "fb384ab57d79f0020c54" "d2c66416e8a7666f0ceb" not in architecture:
        errors.append(
            f"{ISSUE76_ARCHITECTURE_REL}: issue-76 locked plan source pin is missing"
        )
    api = document_texts.get(ISSUE76_API_REL, "")
    if ISSUE76_SCHEMA_REL.name not in api:
        errors.append(f"{ISSUE76_API_REL}: issue-76 machine schema binding is missing")
    errors.extend(_issue_84_local_source_contradiction_errors(api))

    errors.extend(_issue_76_machine_contract_errors(root))
    return errors


def issue_88_lab_profile_activation_errors(root: Path) -> list[str]:
    """Require the exact owner-controlled M6.25 lab-profile activation contract."""
    errors: list[str] = []
    for rel, markers in ISSUE88_LAB_PROFILE_MARKERS.items():
        path = root / rel
        if not path.is_file() or path.is_symlink():
            errors.append(f"{rel}: issue-88 canonical document is missing")
            continue
        normalized = " ".join(_read(path).split()).casefold()
        for marker in markers:
            if marker.casefold() not in normalized:
                errors.append(
                    f"{rel}: issue-88 lab-profile marker is missing: {marker}"
                )
    return errors


def issue_96_spine13_hvac_model_erratum_errors(root: Path) -> list[str]:
    """Enforce the bounded public-evidence SPINE 1.3 HVAC model erratum."""
    errors: list[str] = []
    candidate = root / ISSUE96_CANDIDATE_REL
    if not candidate.is_file() or candidate.is_symlink():
        return [f"{ISSUE96_CANDIDATE_REL}: issue-96 candidate document is missing"]

    normalized = " ".join(_read(candidate).split()).casefold()
    for name, marker in ISSUE96_REQUIRED_MARKERS.items():
        if marker.casefold() not in normalized:
            errors.append(f"{ISSUE96_CANDIDATE_REL}: issue-96 missing {name} marker")

    for relative in ISSUE96_EVIDENCE_RELS:
        path = root / relative
        if not path.is_file() or path.is_symlink():
            errors.append(f"{relative}: issue-96 evidence document is missing")
            continue
        if ISSUE96_CANDIDATE_REL.name not in _read(path):
            errors.append(f"{relative}: issue-96 evidence link to candidate is missing")

    for source_commit in ISSUE96_PUBLIC_SOURCE_COMMITS:
        if source_commit not in normalized:
            errors.append(f"{ISSUE96_CANDIDATE_REL}: issue-96 public source pin is missing")
    return errors


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
    if (root / "api").is_dir():
        if not CANDIDATE_API_MACHINE_ARTIFACTS <= API_MACHINE_ARTIFACTS:
            errors.append("api/_candidate/msp-06: candidate machine registry is not allowlisted")
        for rel in sorted(CANDIDATE_API_MACHINE_ARTIFACTS):
            if not _is_candidate_path(rel):
                errors.append(f"{rel}: candidate machine artifact escaped candidate root")
            artifact = root / rel
            if not artifact.is_file() or artifact.is_symlink():
                errors.append(f"{rel}: candidate machine artifact is missing")
        if publication_channels is not None:
            registered_outputs = set(publication_channels["registered"])
            for rel in sorted(CANDIDATE_API_MACHINE_ARTIFACTS & registered_outputs):
                errors.append(f"{rel}: candidate machine artifact registered as stable output")

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

    errors.extend(ship_identity_corpus_errors(root))
    errors.extend(outbound_pairing_contract_errors(root))
    errors.extend(strict_current_schema_errors(root))
    errors.extend(issue_68_raw_operator_redaction_errors(root))
    errors.extend(issue_76_m625_raw_feature_errors(root))
    errors.extend(issue_88_lab_profile_activation_errors(root))
    errors.extend(issue_96_spine13_hvac_model_erratum_errors(root))
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
