from __future__ import annotations

import re
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_REL = "api/_candidate/msp-06-eebus-mcp-v1.md"
CONTRACT = ROOT / CONTRACT_REL
LANDING = ROOT / "api/README.md"


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
        source_commit = "7a5852e009bbdcba47f0" + "a34ba866070a4ab35ef8"
        self.assertIn(source_commit, body)
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
                    "RuntimeObservationV1",
                ),
                "eebus.v1.services.list": (
                    "services",
                    "none",
                    "evidence_ref",
                    "[]ServiceV1",
                ),
                "eebus.v1.services.get": (
                    "service",
                    "id_digest",
                    "evidence_ref",
                    "ServiceV1",
                ),
                "eebus.v1.sessions.list": (
                    "sessions",
                    "none",
                    "evidence_ref",
                    "[]SessionV1",
                ),
                "eebus.v1.sessions.get": (
                    "session",
                    "id_digest",
                    "evidence_ref",
                    "SessionV1",
                ),
                "eebus.v1.topology.get": (
                    "topology",
                    "none",
                    "evidence_ref",
                    "TopologyV1",
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
                    "[]PairingObservationV1",
                ),
            },
        )
        self.assertNotIn("eebus.experimental", body)
        self.assertNotIn("pairing.open", body)
        self.assertNotIn("trust.register", body)

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
        ):
            self.assertIn(phrase, normalized)

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
        ):
            self.assertIn(phrase, normalized)
        landing = LANDING.read_text(encoding="utf-8")
        self.assertIn("msp-06-eebus-mcp-v1.md", landing)

    def test_transport_gate_and_rollback_are_explicit(self) -> None:
        _, body = self.contract()
        rows = table_rows(body, "## eeBUS Transport Gate v0 Mapping")
        self.assertEqual(
            [code_value(row["Case"]) for row in rows],
            ["EEBUS-G12", "EEBUS-G13", "EEBUS-G14", "EEBUS-G15", "EEBUS-G16"],
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
        ):
            self.assertIn(phrase, normalized)


if __name__ == "__main__":
    unittest.main()
