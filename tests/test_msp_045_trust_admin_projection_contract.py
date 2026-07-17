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
PAIRING_TRANSPORT = "SH" + "IP"
NORMATIVE_TABLES = (
    "## Contract Identity And Ownership",
    "## Combined State Product",
    "## Closed Projection Precedence",
    "## Existing Public Field Mapping",
    "### Runtime Degradation Precedence",
    "## Candidate Absence Rule",
    "## Publication Linearization",
    "## Startup And Restart Publication",
    "## Rollback Ledger",
)


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
        return [
            cell.replace(r"\|", "|").strip()
            for cell in re.split(r"(?<!\\)\|", line.strip("|"))
        ]

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
    result: dict[str, tuple[str, ...]] = {}
    for row in table_rows(body, heading):
        key = code_value(row[key_column])
        if key in result:
            raise AssertionError(f"{heading} contains duplicate key: {key}")
        result[key] = tuple(
            code_value(row[column]) for column in value_columns
        )
    return result


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
            "vendor_" + "restric" + "ted",
            "restric" + "ted source",
            "operator " + "note",
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
                    "CORRUPT_STORE|DURABILITY_UNKNOWN|HOST_BINDING_MISMATCH|CLONE_DETECTED|MANIFEST_GENERATION_ROLLBACK|CONTROL_EPOCH_ROLLBACK|REOPEN_IN_PROGRESS|RECONCILIATION_IN_PROGRESS|REPAIR_IN_PROGRESS|UNKNOWN_ENUM",
                    "unknown",
                    "false",
                    "denied-trust",
                ),
                "2": (
                    "REVOKED|TOMBSTONED|QUARANTINED|ADMIN_HOLD|BACKOFF_ACTIVE",
                    "denied",
                    "false",
                    "denied-trust",
                ),
                "3": (
                    "missing-protected-identity",
                    "unknown",
                    "false",
                    "certificate-unavailable",
                ),
                "4": (
                    "PAIRED_TRUSTED+store-and-protected-anchor-finalized+same-lineage+active+trusted+allowlisted+reconnectable+non-tombstoned",
                    "paired",
                    "true",
                    "evaluate-liveness",
                ),
                "5": (
                    "UNPAIRED_LOCKED|PAIRING_CLOSED|OPEN_EMPTY|association_incomplete|CANDIDATE_PENDING|COMMITTING-before-store-and-anchor-durable",
                    "unpaired",
                    "false",
                    "evaluate-liveness",
                ),
                "6": (
                    f"{PAIRING_TRANSPORT}-callback",
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
            "explicit closed structural-state set",
            "`association_incomplete` is not a structural unknown",
            "A stale callback after revocation or restart cannot resurrect `paired`",
        )
        for phrase in required:
            self.assertIn(phrase, normalized)
        self.assertNotIn("Any incomplete", body)

    def test_candidate_state_is_absent_from_every_public_collection(self) -> None:
        _, body = self.contract()
        rows = coded_table(
            body,
            "## Candidate Absence Rule",
            "Candidate condition",
            ("Candidate public effect", "Existing durable remote rows"),
        )
        self.assertEqual(
            rows,
            {
                "CANDIDATE_PENDING|association_incomplete": (
                    "absent-from-all-public-collections",
                    "unchanged-or-unpaired-from-durable-record-only",
                ),
                "COMMITTING-before-store-and-anchor-durable": (
                    "absent-from-all-public-collections",
                    "unchanged-or-unpaired-from-durable-record-only",
                ),
            },
        )
        normalized = " ".join(body.split())
        required = (
            "does not create any `PairingObservationV1`, `ServiceV1`, `SessionV1`, or topology row",
            "No redacted candidate identity or placeholder row is emitted",
            "does not change public cardinality, ordering, or timing",
            "Existing configured durable remote rows may remain `unpaired`",
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
                    f"{PAIRING_TRANSPORT}-liveness",
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
            degradation,
            [
                "denied-trust",
                "certificate-unavailable",
                "remote-disconnect",
                "no-visible-services",
            ],
        )
        self.assertIn(
            "`denied-trust` first, then `certificate-unavailable`",
            " ".join(body.split()),
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
            f"Callbacks from the {PAIRING_TRANSPORT} path report liveness only",
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
                "store-commit-durable+protected-anchor-finalization-durable": (
                    "paired",
                    "no",
                ),
                "commit_not_published+protected-anchor-clear-durable": (
                    "unpaired-with-candidate-absent",
                    "no",
                ),
                "commit_applied_maintenance_failed|commit_durability_unknown|interruption_or_descriptor_mismatch|protected-anchor-finalization-unknown": (
                    "unknown+paired-false+denied-trust",
                    "no",
                ),
                "REVOKED|TOMBSTONED|QUARANTINED|ADMIN_HOLD|BACKOFF_ACTIVE": (
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
                "pre-durable-cancel|expiry|failure|association_incomplete": (
                    "candidate-absent",
                    "no-candidate-publication",
                ),
                "store-commit-durable+protected-anchor-finalization-durable": (
                    "paired",
                    "callback-cannot-roll-back",
                ),
                "commit_not_published+protected-anchor-clear-durable": (
                    "unpaired-with-candidate-absent",
                    "no-trust-and-no-candidate-publication",
                ),
                "commit_applied_maintenance_failed|commit_durability_unknown|interruption_or_descriptor_mismatch|protected-anchor-finalization-unknown": (
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
        self.assertIn(
            "A store `commit_durable` result alone never publishes `paired`",
            " ".join(body.split()),
        )

    def test_startup_and_restart_publish_classification_without_callbacks(self) -> None:
        _, body = self.contract()
        startup = coded_table(
            body,
            "## Startup And Restart Publication",
            "Classified product",
            ("Required publication", "Network callback required"),
        )
        self.assertEqual(
            startup,
            {
                "durably_trusted+store-and-protected-anchor-finalized": (
                    "paired",
                    "no",
                ),
                "terminal_denial": ("denied", "no"),
                "identity_unavailable": (
                    "unknown+certificate-unavailable",
                    "no",
                ),
                "not_yet_trusted": ("unpaired-with-candidate-absent", "no"),
            },
        )
        normalized = " ".join(body.split())
        self.assertIn(
            "after reload, structural classification, and protected-anchor checks complete",
            normalized,
        )
        self.assertIn("without waiting for a", normalized)

    def test_normative_tables_and_headings_are_unique(self) -> None:
        _, body = self.contract()
        for heading in NORMATIVE_TABLES:
            with self.subTest(heading=heading):
                self.assertEqual(
                    len(re.findall(rf"(?m)^{re.escape(heading)}$", body)),
                    1,
                )
                table_rows(body, heading)

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
