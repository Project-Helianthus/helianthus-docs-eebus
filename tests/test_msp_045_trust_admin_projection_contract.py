from __future__ import annotations

import hashlib
import json
import re
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_REL = (
    "architecture/_candidate/msp-045-trust-admin-projection.md"
)
CONTRACT = ROOT / CONTRACT_REL
MSP04B = ROOT / "architecture/_candidate/msp-04b-first-trust-admin-local.md"
MSP04C = ROOT / (
    "architecture/_candidate/msp-04c-restore-revocation-quarantine-repair.md"
)
ROADMAP = ROOT / "architecture/README.md"
PUBLIC_API_MANIFEST = ROOT / "api/eebusruntime-v1/manifest.json"
PUBLIC_API_SHA256 = (
    "c93492bd275b5e14d3c9e05da701730d" + "6d34a197e0653e6b169d103418bfcc8c"
)


def read_markdown(path: Path) -> tuple[dict[str, str], str]:
    text = path.read_text(encoding="utf-8")
    _, front_matter, body = text.split("---", 2)
    return yaml.safe_load(front_matter), body


def table_rows(body: str, heading: str) -> list[dict[str, str]]:
    lines = body.split(heading, 1)[1].splitlines()
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
            raise AssertionError(f"{heading} contains a malformed table row: {line}")
        rows.append(dict(zip(headers, values, strict=True)))
    return rows


def code_value(value: str) -> str:
    if not (value.startswith("`") and value.endswith("`")):
        raise AssertionError(f"expected one code value, got: {value}")
    return value[1:-1]


def coded_table(
    body: str,
    heading: str,
    key_column: str,
    value_columns: tuple[str, ...],
) -> dict[str, tuple[str, ...]]:
    return {
        code_value(row[key_column]): tuple(
            code_value(row[column]) for column in value_columns
        )
        for row in table_rows(body, heading)
    }


class MSP045TrustAdminProjectionContractTest(unittest.TestCase):
    def contract(self) -> tuple[dict[str, str], str]:
        self.assertTrue(CONTRACT.is_file(), f"missing MSP-045 contract: {CONTRACT_REL}")
        return read_markdown(CONTRACT)

    def test_metadata_and_candidate_confinement(self) -> None:
        metadata, body = self.contract()
        self.assertEqual(metadata["publication_status"], "candidate")
        self.assertEqual(metadata["claim_status"], "evidence-backed")
        self.assertEqual(metadata["source_class"], "derived_inference")
        self.assertEqual(metadata["evidence_ids"], "EV-20260711-001")
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
            "https://github.com/Project-Helianthus/helianthus-docs-eebus/issues/32",
            body,
        )
        normalized = " ".join(body.split()).lower()
        for forbidden in (
            "vendor_restricted",
            "restricted source",
            "operator note",
        ):
            self.assertNotIn(forbidden, normalized)

    def test_contract_identity_ownership_and_freeze_boundaries(self) -> None:
        _, body = self.contract()
        rows = coded_table(
            body,
            "## Contract Identity And Ownership",
            "Boundary",
            ("Frozen value",),
        )
        self.assertEqual(
            rows,
            {
                "contract_id": ("helianthus.eebus.trust-admin-projection.v1",),
                "contract_kind": ("internal_behavioral",),
                "authority": ("first_trust_coordinator_only",),
                "capture": ("atomic_under_coordinator_ownership",),
                "public_mapping": ("existing_public_fields_only",),
                "public_api_bytes": ("95207",),
                "public_api_sha256": (PUBLIC_API_SHA256,),
                "disk_schema": ("MSP-04C-R2_control_schema_v3_unchanged",),
                "persistence": ("derived_never_persisted",),
                "semantic_change": (
                    "new_contract_version+explicit_conformance_migration",
                ),
            },
        )

        normalized = " ".join(body.split())
        required = (
            "not a public Go API",
            "not a disk schema",
            "not an admin wire schema",
            "not an MCP schema",
            "Coordinator-owned state is captured atomically",
            "No observer reconstructs security policy",
        )
        for phrase in required:
            self.assertIn(phrase, normalized)

    def test_closed_projection_precedence_is_exact(self) -> None:
        _, body = self.contract()
        rows = coded_table(
            body,
            "## Closed Projection Precedence",
            "Priority",
            (
                "Coordinator-owned condition",
                "PairingObservationV1.State",
                "ServiceV1.Paired",
                "Trust degradation",
            ),
        )
        self.assertEqual(
            rows,
            {
                "1": (
                    "incomplete|ambiguous|reopen|reconcile|repair|unknown-enum",
                    "unknown",
                    "false",
                    "denied-trust",
                ),
                "2": (
                    "missing-protected-identity",
                    "unknown",
                    "false",
                    "certificate-unavailable",
                ),
                "3": (
                    "revoked|tombstoned|quarantined|corrupt|admin-held",
                    "denied",
                    "false",
                    "denied-trust",
                ),
                "4": (
                    "PAIRED_TRUSTED+same-lineage+active+trusted+allowlisted+reconnectable+non-tombstoned",
                    "paired",
                    "true",
                    "evaluate-liveness",
                ),
                "5": (
                    "UNPAIRED_LOCKED|PAIRING_CLOSED|OPEN_EMPTY|CANDIDATE_PENDING|COMMITTING-before-durable-commit",
                    "unpaired",
                    "false",
                    "evaluate-liveness",
                ),
                "6": (
                    "SHIP-callback",
                    "no-override-of-rows-1-through-5",
                    "no-override-of-rows-1-through-5",
                    "liveness-only",
                ),
            },
        )

        normalized = " ".join(body.split())
        required = (
            "First matching row wins",
            "never `paired`",
            "before durable commit",
            "candidate identity and candidate details remain private",
            "A stale callback after revocation or restart cannot resurrect `paired`",
        )
        for phrase in required:
            self.assertIn(phrase, normalized)

    def test_public_mapping_and_degradation_order_use_existing_fields(self) -> None:
        _, body = self.contract()
        rows = coded_table(
            body,
            "## Existing Public Field Mapping",
            "Public field",
            ("Projection source", "Constraint"),
        )
        self.assertEqual(
            rows,
            {
                "PairingObservationV1.State": (
                    "coordinator-trust",
                    "unknown|denied|paired|unpaired-only",
                ),
                "ServiceV1.Paired": (
                    "same-atomic-capture",
                    "true-only-with-paired-row",
                ),
                "SessionV1.State+Since": (
                    "SHIP-liveness",
                    "cannot-promote-trust",
                ),
                "RuntimeObservationV1.Degradation": (
                    "closed-precedence",
                    "existing-reasons-only",
                ),
            },
        )

        degradation = [
            code_value(row["Reason"])
            for row in table_rows(body, "### Runtime Degradation Precedence")
        ]
        self.assertEqual(
            degradation[:4],
            [
                "certificate-unavailable",
                "denied-trust",
                "remote-disconnect",
                "no-visible-services",
            ],
        )

    def test_admission_admin_and_private_data_cannot_promote_or_leak(self) -> None:
        _, body = self.contract()
        normalized = " ".join(body.split())
        required = (
            "Configuration allowlist and pretrust are admission inputs only",
            "cannot prove durable pairing",
            "cannot promote durable trust",
            "Admin availability is mutation capability only",
            "candidate identity, fingerprint, nonce, idempotency key, admin path, and history are never projected",
            "SHIP callbacks report liveness only",
        )
        for phrase in required:
            self.assertIn(phrase, normalized)

    def test_publication_linearization_and_rollback_ledger_are_closed(self) -> None:
        _, body = self.contract()
        publication = coded_table(
            body,
            "## Publication Linearization",
            "Linearized outcome",
            ("Required publication", "Network callback required"),
        )
        self.assertEqual(
            publication,
            {
                "commit_durable": ("paired", "no"),
                "commit_not_published": ("unpaired", "no"),
                "durability_unknown|reopen|reconcile|repair": ("unknown", "no"),
                "revoked|tombstoned|quarantined|corrupt|admin-held": (
                    "denied",
                    "no",
                ),
                "disconnect|reconnect-callback": ("liveness-only", "callback-is-event"),
            },
        )

        rollback = coded_table(
            body,
            "## Rollback Ledger",
            "Case",
            ("Projection", "Rollback rule"),
        )
        self.assertEqual(
            rollback,
            {
                "pre-durable-cancel|expiry|failure": (
                    "unpaired",
                    "no-candidate-publication",
                ),
                "commit_durable": ("paired", "callback-cannot-roll-back"),
                "commit_not_published": (
                    "unpaired",
                    "no-trust-and-no-candidate-publication",
                ),
                "durability_unknown|repair-in-progress": (
                    "unknown+denied-trust",
                    "fail-closed-until-terminal",
                ),
                "revocation|tombstone-terminal": (
                    "denied+denied-trust",
                    "callback-cannot-resurrect",
                ),
            },
        )

        self.assertIn(
            "State transitions publish after durable or terminal linearization even without a network callback",
            " ".join(body.split()),
        )

    def test_public_api_artifact_remains_byte_identical(self) -> None:
        self.contract()
        payload = PUBLIC_API_MANIFEST.read_bytes()
        self.assertEqual(len(payload), 95_207)
        self.assertEqual(hashlib.sha256(payload).hexdigest(), PUBLIC_API_SHA256)
        manifest = json.loads(payload)
        names = {
            symbol["name"]
            for package in manifest["packages"]
            for symbol in package["symbols"]
        }
        for forbidden in (
            "TrustAdminProjection",
            "CandidateFingerprint",
            "AdminPath",
            "PairingHistory",
        ):
            self.assertNotIn(forbidden, names)

    def test_candidate_architecture_and_m45_roadmap_cross_link(self) -> None:
        link = "msp-045-trust-admin-projection.md"
        self.assertIn(link, MSP04B.read_text(encoding="utf-8"))
        self.assertIn(link, MSP04C.read_text(encoding="utf-8"))
        roadmap = ROADMAP.read_text(encoding="utf-8")
        self.assertIn("## M4.5 Roadmap", roadmap)
        self.assertIn(f"_candidate/{link}", roadmap)


if __name__ == "__main__":
    unittest.main()
