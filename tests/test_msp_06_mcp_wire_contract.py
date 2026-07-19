from __future__ import annotations

import copy
import hashlib
import json
import re
import sys
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import validate_repository_policy as repository_policy  # noqa: E402


API_MACHINE_ARTIFACTS = repository_policy.API_MACHINE_ARTIFACTS
CANDIDATE_API_MACHINE_ARTIFACTS = getattr(
    repository_policy,
    "CANDIDATE_API_MACHINE_ARTIFACTS",
    set(),
)
MSP06_PROVENANCE_MACHINE_FINGERPRINTS = getattr(
    repository_policy,
    "MSP06_PROVENANCE_MACHINE_FINGERPRINTS",
    {},
)
_provenance_errors = repository_policy._provenance_errors


CONTRACT_REL = "api/_candidate/msp-06-eebus-mcp-v1.md"
CONTRACT = ROOT / CONTRACT_REL
LANDING = ROOT / "api/README.md"
MACHINE_ROOT_REL = "api/_candidate/msp-06"
SCHEMA_REL = f"{MACHINE_ROOT_REL}/helianthus.eebus.mcp.v1.schema.json"
JCS_FIXTURE_REL = f"{MACHINE_ROOT_REL}/jcs-hash-vectors-v1.json"
SCHEMA = ROOT / SCHEMA_REL
JCS_FIXTURE = ROOT / JCS_FIXTURE_REL
SOURCE_COMMIT = "7a5852e009bbdcba47f0" + "a34ba866070a4ab35ef8"


def read_markdown(path: Path) -> tuple[dict[str, str], str]:
    text = path.read_text(encoding="utf-8")
    _, front_matter, body = text.split("---", 2)
    return yaml.safe_load(front_matter), body


def table_rows(body: str, heading: str) -> list[dict[str, str]]:
    matches = list(re.finditer(rf"(?m)^{re.escape(heading)}$", body))
    if len(matches) != 1:
        raise AssertionError(f"{heading} must appear exactly once, got {len(matches)}")
    section = body[matches[0].end() :]
    next_heading = re.search(r"(?m)^#{1,6} .+$", section)
    lines = section[: next_heading.start() if next_heading else None].splitlines()
    start = next(index for index, line in enumerate(lines) if line.startswith("|"))

    def cells(line: str) -> list[str]:
        return [cell.strip() for cell in line.strip("|").split("|")]

    headers = cells(lines[start])
    separator = cells(lines[start + 1])
    if len(headers) != len(separator) or not all(
        re.fullmatch(r":?-{3,}:?", cell) for cell in separator
    ):
        raise AssertionError(f"{heading} does not start with a valid Markdown table")

    rows: list[dict[str, str]] = []
    for line in lines[start + 2 :]:
        if not line.startswith("|"):
            break
        values = cells(line)
        if len(values) != len(headers):
            raise AssertionError(f"{heading} contains a malformed row: {line}")
        rows.append(dict(zip(headers, values, strict=True)))
    return rows


def code_value(value: str) -> str:
    if not (value.startswith("`") and value.endswith("`")):
        raise AssertionError(f"expected one code value, got: {value}")
    return value[1:-1]


def parse_jcs_input(raw: str) -> object:
    def parse_int(token: str) -> int:
        if token == "-0":
            raise ValueError("negative-zero")
        value = int(token)
        if abs(value) > 9_007_199_254_740_991:
            raise ValueError("unsafe-integer")
        return value

    def parse_float(token: str) -> float:
        raise ValueError(f"non-integer-number:{token}")

    return json.loads(raw, parse_int=parse_int, parse_float=parse_float)


def canonicalize_jcs_subset(value: object) -> str:
    if value is None:
        return "null"
    if value is True:
        return "true"
    if value is False:
        return "false"
    if type(value) is int:
        if abs(value) > 9_007_199_254_740_991:
            raise ValueError("unsafe-integer")
        return str(value)
    if isinstance(value, float):
        raise ValueError("non-integer-number")
    if isinstance(value, str):
        return json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    if isinstance(value, list):
        return "[" + ",".join(canonicalize_jcs_subset(item) for item in value) + "]"
    if isinstance(value, dict):
        if any(not isinstance(key, str) for key in value):
            raise ValueError("non-string-key")
        keys = sorted(value, key=lambda key: key.encode("utf-16-be"))
        return "{" + ",".join(
            canonicalize_jcs_subset(key) + ":" + canonicalize_jcs_subset(value[key])
            for key in keys
        ) + "}"
    raise ValueError(f"unsupported-jcs-type:{type(value).__name__}")


def remove_json_pointers(value: object, pointers: list[str]) -> object:
    projected = copy.deepcopy(value)
    for pointer in pointers:
        self = projected
        parts = pointer.removeprefix("/").split("/") if pointer else []
        for part in parts[:-1]:
            if not isinstance(self, dict):
                raise AssertionError(f"non-object pointer segment in {pointer}")
            self = self[part.replace("~1", "/").replace("~0", "~")]
        if not parts or not isinstance(self, dict):
            raise AssertionError(f"invalid exclusion pointer {pointer}")
        del self[parts[-1].replace("~1", "/").replace("~0", "~")]
    return projected


class MSP06MCPWireContractTest(unittest.TestCase):
    def contract(self) -> tuple[dict[str, str], str]:
        self.assertTrue(CONTRACT.is_file(), f"missing MSP-06 contract: {CONTRACT_REL}")
        return read_markdown(CONTRACT)

    def test_candidate_metadata_and_non_protocol_provenance(self) -> None:
        metadata, body = self.contract()
        self.assertEqual(metadata["publication_status"], "candidate")
        self.assertEqual(metadata["owner_domain"], "api")
        self.assertEqual(metadata["claim_status"], "no-protocol-claims")
        self.assertEqual(metadata["source_class"], "derived_inference")
        self.assertEqual(metadata["hypothesis_status"], "draft")
        for channel in (
            "stable_navigation",
            "search",
            "sitemap",
            "versioned_bundle",
            "release_bundle",
        ):
            self.assertEqual(metadata[channel], "false")
        self.assertIn(
            "https://github.com/Project-Helianthus/helianthus-docs-eebus/issues/43",
            body,
        )
        self.assertEqual(metadata["source_commit"], SOURCE_COMMIT)
        self.assertIn(SOURCE_COMMIT, body)
        restricted_marker = "vendor" + "-restricted"
        self.assertIn(f"uses no {restricted_marker} source", body)

    def test_stable_tool_inventory_and_shapes_are_closed(self) -> None:
        _, body = self.contract()
        rows = table_rows(body, "## Stable Tool Inventory")
        got = {
            code_value(row["Tool"]): (
                code_value(row["Scope"]),
                code_value(row["Required input"]),
                code_value(row["Optional input"]),
                code_value(row["Data"]),
            )
            for row in rows
        }
        self.assertEqual(
            got,
            {
                "eebus.v1.runtime.status.get": (
                    "runtime-status",
                    "none",
                    "evidence_ref",
                    "RuntimeStatusDataV1",
                ),
                "eebus.v1.services.list": (
                    "services",
                    "none",
                    "evidence_ref",
                    "ServicesListDataV1",
                ),
                "eebus.v1.services.get": (
                    "service",
                    "id_digest",
                    "evidence_ref",
                    "ServiceDataV1",
                ),
                "eebus.v1.sessions.list": (
                    "sessions",
                    "none",
                    "evidence_ref",
                    "SessionsListDataV1",
                ),
                "eebus.v1.sessions.get": (
                    "session",
                    "id_digest",
                    "evidence_ref",
                    "SessionDataV1",
                ),
                "eebus.v1.topology.get": (
                    "topology",
                    "none",
                    "evidence_ref",
                    "TopologyDataV1",
                ),
                "eebus.v1.snapshot.capture": (
                    "whole-root",
                    "none",
                    "none",
                    "CapturedRootV1",
                ),
                "eebus.v1.snapshot.drop": (
                    "whole-root",
                    "snapshot_ref",
                    "none",
                    "DropResultV1",
                ),
                "eebus.v1.pairing.status.get": (
                    "pairing-status",
                    "none",
                    "evidence_ref",
                    "PairingStatusDataV1",
                ),
            },
        )
        self.assertNotIn("eebus.experimental", body)
        self.assertNotIn("pairing.open", body)
        self.assertNotIn("trust.register", body)

    def test_wire_object_schemas_and_envelope_states_are_closed(self) -> None:
        _, body = self.contract()
        rows = table_rows(body, "## Wire Object Schemas")
        got = {
            code_value(row["Object"]): (
                code_value(row["Required fields"]),
                code_value(row["Optional fields"]),
                code_value(row["Additional properties"]),
            )
            for row in rows
        }
        self.assertEqual(
            got,
            {
                "EnvelopeV1": ("meta,data,error", "none", "false"),
                "MetaV1": (
                    "contract,tool,scope,mask_tier,auth_scope,mode,data_timestamp,data_hash,runtime",
                    "none",
                    "false",
                ),
                "ContractV1": ("name,major,minor", "none", "false"),
                "RuntimeMetaV1": ("state", "degradation", "false"),
                "ErrorV1": ("code,message,retriable,source_layer", "none", "false"),
                "IdentityDigestV1": ("kind,digest", "none", "false"),
                "EvidenceDescriptorV1": ("kind,digest,size,data_timestamp", "none", "false"),
                "DegradationDataV1": ("reason,since", "none", "false"),
                "RuntimeStatusDataV1": ("state", "degradation", "false"),
                "ServiceDataV1": ("id,kind,visible,paired", "evidence", "false"),
                "ServicesListDataV1": ("services", "none", "false"),
                "SessionDataV1": ("id,remote,state", "since,evidence", "false"),
                "SessionsListDataV1": ("sessions", "none", "false"),
                "PairingDataV1": ("remote,state", "since,evidence", "false"),
                "PairingStatusDataV1": ("pairing", "none", "false"),
                "FeatureDataV1": ("id,role", "evidence", "false"),
                "EntityDataV1": ("id,features", "evidence", "false"),
                "UseCaseClaimDataV1": ("id", "evidence", "false"),
                "DeviceDataV1": ("id,entities,usecase_claims", "evidence", "false"),
                "TopologyDataV1": ("devices", "none", "false"),
                "SnapshotMetaDataV1": (
                    "contract,runtime,mask_tier,captured_at,data_timestamp,data_hash",
                    "none",
                    "false",
                ),
                "SnapshotDataV1": (
                    "meta,status,pairing,services,sessions,topology",
                    "evidence",
                    "false",
                ),
                "EvidenceRefsV1": (
                    "runtime_status_ref,services_list_ref,services_get_ref,sessions_list_ref,sessions_get_ref,topology_ref,pairing_status_ref",
                    "none",
                    "false",
                ),
                "CapturedRootV1": (
                    "snapshot_ref,expires_at,snapshot_content_hash,evidence_refs,snapshot",
                    "none",
                    "false",
                ),
                "DropResultV1": ("status", "none", "false"),
            },
        )
        normalized = " ".join(body.split())
        for phrase in (
            "Success requires non-null `data` and null `error`",
            "failure requires null `data` and non-null `error`",
            "omitted optional field is not serialized as null",
            "Raw runtime `Unknown` values are never copied to wire DTOs",
            "backend error text is never copied into `message`",
            "`id_digest` is a redacted SHA-256 selector",
        ):
            self.assertIn(phrase, normalized)

    def test_reference_binding_and_capture_shape_are_exact(self) -> None:
        _, body = self.contract()
        rows = table_rows(body, "## Opaque Reference Binding")
        got = {
            code_value(row["Reference"]): (
                code_value(row["Tool binding"]),
                code_value(row["Scope binding"]),
                code_value(row["Consumer"]),
            )
            for row in rows
        }
        self.assertEqual(
            got,
            {
                "snapshot_ref": (
                    "eebus.v1.snapshot.capture",
                    "whole-root",
                    "eebus.v1.snapshot.drop",
                ),
                "runtime_status_ref": (
                    "eebus.v1.runtime.status.get",
                    "runtime-status",
                    "eebus.v1.runtime.status.get",
                ),
                "services_list_ref": (
                    "eebus.v1.services.list",
                    "services",
                    "eebus.v1.services.list",
                ),
                "services_get_ref": (
                    "eebus.v1.services.get",
                    "service",
                    "eebus.v1.services.get",
                ),
                "sessions_list_ref": (
                    "eebus.v1.sessions.list",
                    "sessions",
                    "eebus.v1.sessions.list",
                ),
                "sessions_get_ref": (
                    "eebus.v1.sessions.get",
                    "session",
                    "eebus.v1.sessions.get",
                ),
                "topology_ref": (
                    "eebus.v1.topology.get",
                    "topology",
                    "eebus.v1.topology.get",
                ),
                "pairing_status_ref": (
                    "eebus.v1.pairing.status.get",
                    "pairing-status",
                    "eebus.v1.pairing.status.get",
                ),
            },
        )
        normalized = " ".join(body.split())
        for phrase in (
            "runtime identity",
            "MCP contract identity",
            "tool identity",
            "scope",
            "`redacted` mask tier",
            "effective `eebus.raw.read` authorization scope",
            "Callers supply only the opaque token",
            "32 cryptographically random bytes",
            "unpadded base64url",
            "does not require a public `ToolDrop` declaration",
        ):
            self.assertIn(phrase, normalized)

    def test_lifecycle_quota_expiry_and_drop_are_bounded(self) -> None:
        _, body = self.contract()
        rows = table_rows(body, "## Snapshot Lifecycle Constants")
        got = {
            code_value(row["Constant"]): code_value(row["Value"]) for row in rows
        }
        self.assertEqual(
            got,
            {
                "active_ttl": "5m",
                "max_active": "32",
                "tombstone_ttl": "5m",
                "max_tombstones": "256",
                "token_entropy": "256-bit",
            },
        )
        normalized = " ".join(body.split())
        for phrase in (
            "Capture failure consumes no active slot",
            "quota_exceeded",
            "oldest terminal tombstone",
            "snapshot_gone",
            "unknown well-formed evidence reference returns `not_found`",
            "`snapshot.drop` returns exactly `dropped` or `already_gone`",
            "never returns `not_found`",
            "invalidates every descendant evidence reference",
            "32 active root captures",
            "seven descendant evidence references per root",
            "Live reads allocate no store entry",
            "`now >= expires_at`",
            "Tombstone TTL starts at the terminal transition",
            "concurrent captures reserve quota atomically",
            "exactly 43 ASCII characters",
            "decodes to exactly 32 bytes",
            "one root group regardless of its eight tokens",
            "linearization point",
            "terminal_at then root token bytes",
            "policy version that minted it",
        ):
            self.assertIn(phrase, normalized)

        outcomes = {
            code_value(row["Condition"]): code_value(row["Result"])
            for row in table_rows(body, "## Reference Resolution Matrix")
        }
        self.assertEqual(
            outcomes,
            {
                "malformed-token": "invalid_argument",
                "unknown-evidence-token": "not_found",
                "known-wrong-binding": "permission_denied",
                "root-used-as-evidence": "permission_denied",
                "evidence-used-as-root": "already_gone",
                "expired-or-dropped-descendant": "snapshot_gone",
                "evicted-descendant-tombstone": "not_found",
                "active-root-drop": "dropped",
                "terminal-root-drop": "already_gone",
                "unknown-well-formed-root-drop": "already_gone",
            },
        )

    def test_authorization_and_error_precedence_fail_closed(self) -> None:
        _, body = self.contract()
        error_rows = table_rows(body, "## Exhaustive Error Inventory")
        self.assertEqual(
            [code_value(row["Code"]) for row in error_rows],
            [
                "invalid_argument",
                "not_found",
                "permission_denied",
                "admin_required",
                "backend_unavailable",
                "timeout",
                "snapshot_gone",
                "quota_exceeded",
                "contract_violation",
            ],
        )
        precedence = [
            code_value(row["Stage"])
            for row in table_rows(body, "## Error Precedence")
        ]
        self.assertEqual(
            precedence,
            ["shape-and-syntax", "authorization", "reference-lifecycle", "backend", "invariant"],
        )
        normalized = " ".join(body.split())
        for phrase in (
            "does not authenticate an end user",
            "production MCP HTTP route is currently unauthenticated",
            "fixed redacted-reader policy",
            "never accepted from tool arguments or headers",
            "A future authenticated policy may replace that grant",
            "cannot reinterpret an already minted reference",
            "authorization, mask, or principal arguments return `invalid_argument`",
            "HTTP headers cannot alter the fixed policy",
        ):
            self.assertIn(phrase, normalized)

    def test_envelope_hash_and_degraded_state_contract_are_deterministic(self) -> None:
        _, body = self.contract()
        normalized = " ".join(body.split())
        for phrase in (
            "`meta`, `data`, and `error`",
            "`helianthus-eebus-mcp`",
            "major `1` and minor `0`",
            "`sha256:<64-lowercase-hex>`",
            "RFC 8785/JCS",
            "non-finite numbers and negative zero are rejected",
            "portable JSON safe-integer range are strings",
            "opaque reference tokens",
            "excluded from hash material",
            "runtime state and degradation reason",
            "no visible services is never represented as an unexplained empty success",
            "snapshot_content_hash equals snapshot.meta.data_hash",
            "excludes SnapshotMetaDataV1.data_hash",
            "capture envelope meta.data_hash is a separate envelope hash",
            "UTF-16 code units",
        ):
            self.assertIn(phrase, normalized)
        hash_fields = {
            code_value(row["Field"])
            for row in table_rows(body, "## Hash View")
        }
        self.assertEqual(
            hash_fields,
            {
                "contract",
                "tool",
                "scope",
                "mask_tier",
                "auth_scope",
                "mode",
                "data_timestamp",
                "runtime_state",
                "degradation",
                "data",
                "error",
            },
        )

        self.assertTrue(JCS_FIXTURE.is_file(), f"missing JCS vectors: {JCS_FIXTURE}")
        fixture = json.loads(JCS_FIXTURE.read_text(encoding="utf-8"))
        self.assertEqual(fixture["contract"], "helianthus.eebus.mcp.jcs-hash-vectors.v1")
        names = [vector["name"] for vector in fixture["vectors"]]
        self.assertEqual(
            names,
            [
                "object-key-order",
                "unicode-key-order",
                "explicit-null",
                "omitted-field",
                "safe-integer-string",
                "negative-zero-rejected",
                "token-substitution-invariant",
                "payload-mutation",
                "error-message-invariant",
            ],
        )
        for vector in fixture["vectors"]:
            self.assertTrue(vector["cases"], vector["name"])
            if vector["outcome"] == "reject":
                self.assertNotIn("sha256", vector["cases"][0])
        self.assertNotEqual(
            fixture["vectors"][2]["cases"][0]["sha256"],
            fixture["vectors"][3]["cases"][0]["sha256"],
        )

    def test_candidate_machine_artifacts_and_wire_schema_are_closed(self) -> None:
        expected_artifacts = {SCHEMA_REL, JCS_FIXTURE_REL}
        self.assertEqual(CANDIDATE_API_MACHINE_ARTIFACTS, expected_artifacts)
        self.assertTrue(expected_artifacts <= API_MACHINE_ARTIFACTS)
        self.assertTrue(all(path.startswith(MACHINE_ROOT_REL + "/") for path in expected_artifacts))
        self.assertEqual(
            set(MSP06_PROVENANCE_MACHINE_FINGERPRINTS),
            {JCS_FIXTURE_REL},
        )

        self.assertTrue(SCHEMA.is_file(), f"missing wire schema: {SCHEMA_REL}")
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        self.assertEqual(schema["$schema"], "https://json-schema.org/draft/2020-12/schema")
        self.assertEqual(schema["$id"], "urn:helianthus:eebus:mcp:v1:candidate")
        definitions = schema["$defs"]
        _, body = self.contract()
        wire_rows = table_rows(body, "## Wire Object Schemas")
        for row in wire_rows:
            name = code_value(row["Object"])
            definition = definitions[name]
            self.assertEqual(definition["type"], "object", name)
            self.assertFalse(definition["additionalProperties"], name)
            required = set(code_value(row["Required fields"]).split(","))
            optional_text = code_value(row["Optional fields"])
            optional = set() if optional_text == "none" else set(optional_text.split(","))
            self.assertEqual(set(definition["required"]), required, name)
            self.assertEqual(set(definition["properties"]), required | optional, name)

        self.assertNotIn("local_ski", definitions["SnapshotMetaDataV1"]["properties"])
        self.assertEqual(definitions["TimestampV1"]["format"], "date-time")
        self.assertEqual(definitions["HashV1"]["pattern"], "^sha256:[0-9a-f]{64}$")
        self.assertEqual(definitions["OpaqueTokenV1"]["pattern"], "^[A-Za-z0-9_-]{43}$")
        self.assertEqual(definitions["MaskTierV1"]["const"], "redacted")
        self.assertEqual(definitions["AuthScopeV1"]["const"], "eebus.raw.read")
        self.assertNotIn("unknown", definitions["RuntimeStateV1"]["enum"])
        for name in (
            "ServicesListDataV1",
            "SessionsListDataV1",
            "PairingStatusDataV1",
            "TopologyDataV1",
        ):
            array_schema = next(
                value
                for value in definitions[name]["properties"].values()
                if value.get("type") == "array"
            )
            self.assertTrue(array_schema["uniqueItems"], name)
            self.assertTrue(array_schema["x-order-by"], name)

        error_map = {
            code_value(row["Code"]): (
                code_value(row["Message"]),
                code_value(row["Retriable"]),
                code_value(row["Source layer"]),
            )
            for row in table_rows(body, "## Exact Error Mapping")
        }
        self.assertEqual(set(error_map), {
            "invalid_argument", "not_found", "permission_denied", "admin_required",
            "backend_unavailable", "timeout", "snapshot_gone", "quota_exceeded",
            "contract_violation",
        })
        self.assertEqual(error_map["backend_unavailable"], (
            "eeBUS runtime unavailable", "true", "eebusruntime"
        ))

    def test_jcs_vectors_execute_projection_canonicalization_and_relations(self) -> None:
        fixture = json.loads(JCS_FIXTURE.read_text(encoding="utf-8"))
        self.assertEqual(fixture["contract"], "helianthus.eebus.mcp.jcs-hash-vectors.v1")
        for vector in fixture["vectors"]:
            cases = vector["cases"]
            if vector["outcome"] == "reject":
                for case in cases:
                    with self.assertRaisesRegex(ValueError, vector["reason"]):
                        parse_jcs_input(case["input_json"])
                continue
            digests: list[str] = []
            for case in cases:
                value = parse_jcs_input(case["input_json"])
                projection = remove_json_pointers(value, vector.get("exclude_paths", []))
                canonical = canonicalize_jcs_subset(projection)
                self.assertEqual(canonical, case["canonical"], vector["name"])
                digest = "sha256:" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()
                self.assertEqual(digest, case["sha256"], vector["name"])
                digests.append(digest)
            if vector["relation"] == "equal":
                self.assertEqual(len(set(digests)), 1, vector["name"])
            elif vector["relation"] == "distinct":
                self.assertEqual(len(set(digests)), len(digests), vector["name"])
            else:
                self.assertEqual(vector["relation"], "single")

        recursive = next(v for v in fixture["vectors"] if v["name"] == "unicode-key-order")
        self.assertIn("😀", recursive["cases"][0]["canonical"])
        token = next(v for v in fixture["vectors"] if v["name"] == "token-substitution-invariant")
        self.assertEqual(len(token["cases"]), 2)
        self.assertEqual(token["exclude_paths"], ["/data/snapshot_ref"])
        mutated = next(v for v in fixture["vectors"] if v["name"] == "payload-mutation")
        self.assertEqual(mutated["relation"], "distinct")
        error = next(v for v in fixture["vectors"] if v["name"] == "error-message-invariant")
        self.assertEqual(error["exclude_paths"], ["/backend_error"])
        self.assertTrue(all('"message":"eeBUS runtime unavailable"' in case["canonical"] for case in error["cases"]))

    def test_provenance_pin_rejects_omission_mismatch_and_body_disagreement(self) -> None:
        metadata, body = self.contract()
        for name, mutated_metadata, mutated_body in (
            ("omitted", {key: value for key, value in metadata.items() if key != "source_commit"}, body),
            ("mismatch", {**metadata, "source_commit": "0" * 40}, body),
            ("body-disagreement", metadata, body.replace(SOURCE_COMMIT, "1" * 40)),
        ):
            with self.subTest(name=name):
                errors = _provenance_errors(
                    ROOT,
                    CONTRACT_REL,
                    mutated_body,
                    mutated_metadata,
                    fixture_mode=False,
                )
                self.assertTrue(any("source_commit" in error for error in errors), errors)

    def test_runtime_registration_reconnect_and_anti_leak_boundaries(self) -> None:
        _, body = self.contract()
        normalized = " ".join(body.split())
        for phrase in (
            "tools are absent from `tools/list` until an enabled eeBUS runtime provider is registered",
            "Registration happens once and is never removed during a transient disconnect",
            "live call returns `backend_unavailable`",
            "previously captured roots remain readable",
            "later live calls recover without re-registering tools",
            "one detached `SnapshotV1` per live tool call",
            "no stale-live fallback",
            "does not modify `ebus.v1.*`",
            "does not modify GraphQL",
            "does not modify Portal",
            "does not modify Home Assistant",
            "does not register semantic facts",
            "does not expose a write or pairing mutation",
            "exactly one `Snapshot()` call for each live read or capture",
            "zero provider calls for evidence reads and drop",
            "byte-identical after provider mutation, disconnect, and provider error",
            "valid degraded snapshot is an explained success",
            "second registration is rejected",
            "registration completes before the MCP handler is mounted",
        ):
            self.assertIn(phrase, normalized)
        landing = LANDING.read_text(encoding="utf-8")
        self.assertIn("msp-06-eebus-mcp-v1.md", landing)

    def test_transport_gate_and_rollback_are_explicit(self) -> None:
        _, body = self.contract()
        rows = table_rows(body, "## eeBUS Transport Gate v0 Mapping")
        self.assertEqual(
            {
                code_value(row["Case"]): code_value(row["Behavior"])
                for row in rows
            },
            {
                "EEBUS-G12": "whole-root-capture",
                "EEBUS-G13": "byte-stable-tool-bound-replay",
                "EEBUS-G14": "exact-binding-and-fixed-policy",
                "EEBUS-G15": "drop-expiry-and-tombstones",
                "EEBUS-G16": "wire-log-error-artifact-redaction",
            },
        )
        normalized = " ".join(body.split())
        for phrase in (
            "Remove the eeBUS provider registration",
            "delete only the in-memory snapshot store",
            "No trust-store migration",
            "no eBUS rollback",
            "no consumer rollback",
            "PEM",
            "token",
            "full fingerprint",
            "IP",
            "MAC",
            "serial",
            "local identity",
            "stable peer id",
            "pairing history",
            "Reference tokens are permitted only in designated direct MCP response fields",
            "logs, errors, and publishable gate artifacts contain no reference token",
            "public API manifest contains no `ToolDrop` declaration",
            "process-ephemeral HMAC-SHA-256 key",
            "runtime-scoped pseudonym",
            "raw SKI",
            "raw SHIP ID",
            "certificate or authentication material",
            "fixed reader policy does not establish a trusted network boundary",
        ):
            self.assertIn(phrase, normalized)


if __name__ == "__main__":
    unittest.main()
