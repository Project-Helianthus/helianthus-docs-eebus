from __future__ import annotations

import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
CANDIDATE_REL = (
    "architecture/_candidate/"
    "msp-04c-restore-revocation-quarantine-repair.md"
)
CANDIDATE = ROOT / CANDIDATE_REL
PLAN_COMMIT = "f5c095935f8a8a67a787" + "3ff349ddaff86eb41994"


def read_markdown(path: Path) -> tuple[dict[str, str], str]:
    text = path.read_text(encoding="utf-8")
    _, front_matter, body = text.split("---", 2)
    return yaml.safe_load(front_matter), body


def table_column_values(body: str, heading: str, column: int) -> list[str]:
    section = body.split(heading, 1)[1].split("\n## ", 1)[0]
    values: list[str] = []
    in_table = False
    for line in section.splitlines():
        if line.startswith("| ---"):
            in_table = True
            continue
        if in_table and not line.startswith("|"):
            break
        if not in_table or not line.startswith("|"):
            continue
        cells = [cell.strip().strip("`") for cell in line.strip("|").split("|")]
        values.append(cells[column])
    return values


def table_column(body: str, heading: str, column: int) -> set[str]:
    return set(table_column_values(body, heading, column))


class MSP04CRestoreQuarantineContractTest(unittest.TestCase):
    def test_candidate_metadata_confinement_and_provenance(self) -> None:
        metadata, body = read_markdown(CANDIDATE)
        self.assertEqual(metadata["publication_status"], "candidate")
        self.assertEqual(metadata["claim_status"], "evidence-backed")
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

        for relative in (
            "README.md",
            "architecture/README.md",
            "api/search-index.json",
            "api/sitemap.xml",
            "api/versioned-bundle.txt",
            "api/release-bundle.txt",
        ):
            self.assertNotIn(
                CANDIDATE_REL,
                (ROOT / relative).read_text(encoding="utf-8"),
            )

        normalized = " ".join(body.split())
        required_links = (
            "https://github.com/Project-Helianthus/helianthus-eebusreg/issues/28",
            "https://github.com/Project-Helianthus/helianthus-execution-plans/issues/58",
            PLAN_COMMIT,
        )
        for link in required_links:
            self.assertIn(link, body)
        self.assertIn("does not claim that restore", normalized)
        self.assertIn("is implemented or supported", normalized)

    def test_store_and_anchor_ownership_are_policy_free_and_nonidentifying(self) -> None:
        _, body = read_markdown(CANDIDATE)
        normalized = " ".join(body.split())
        required = (
            "private trust coordinator owns restore classification",
            "`internal/eebusstore` remains mechanical and policy-free",
            "never interprets a reason",
            "explicit internal schema version",
            "sole writer",
            "host anchor is outside the restorable store set",
            "high-water manifest generation and control epoch",
            "no machine id, hostname, hardware serial",
            "does not disclose or derive a host-global identity",
            "monotonic compare-and-advance",
            "cannot be rolled back with the protected store",
            "persisted `backup_excluded` boolean is not an attestation",
        )
        for phrase in required:
            self.assertIn(phrase, normalized)

    def test_restore_reasons_are_distinct_and_have_closed_precedence(self) -> None:
        _, body = read_markdown(CANDIDATE)
        reasons = table_column_values(
            body, "## Startup Classification And Precedence", 1
        )
        self.assertEqual(
            reasons,
            [
                "CORRUPT_STORE",
                "DURABILITY_UNKNOWN",
                "HOST_KEY_UNAVAILABLE",
                "HOST_BINDING_MISMATCH",
                "CLONE_DETECTED",
                "MANIFEST_GENERATION_ROLLBACK",
                "CONTROL_EPOCH_ROLLBACK",
                "REVOKED_ASSOCIATION",
                "persisted quarantine reason",
            ],
        )
        normalized = " ".join(body.split())
        required = (
            "the first matching row wins",
            "Absence is not positive clone evidence",
            "`CONTROL_EPOCH_ROLLBACK` is logical-state rollback",
            "`MANIFEST_GENERATION_ROLLBACK` is rollback of the selected "
            "manifest's current generation",
            "Logical rollback, manifest rollback, and durability uncertainty",
            "remain separate terminal reasons",
            "never falls back to a lower manifest or an orphan",
        )
        for phrase in required:
            self.assertIn(phrase, normalized)

    def test_state_transitions_cannot_restore_or_repair_directly_to_trust(self) -> None:
        _, body = read_markdown(CANDIDATE)
        self.assertEqual(
            table_column(body, "## Allowed Trust-State Transitions", 0),
            {
                "NO_LOCAL_IDENTITY",
                "UNPAIRED_LOCKED",
                "PAIRING_WINDOW_OPEN",
                "PAIRED_TRUSTED",
                "REVOKED",
                "QUARANTINED",
                "CORRUPT_STORE",
            },
        )
        normalized = " ".join(body.split())
        required = (
            "Any transition not listed is forbidden",
            "plus durable store and anchor finalization",
            "Startup never enters `PAIRED_TRUSTED` from copied, restored, rolled-back",
            "A repair result never transitions directly to `PAIRED_TRUSTED`",
            "Re-pairing requires a later explicit MSP-04B window and exact OOB confirmation",
        )
        for phrase in required:
            self.assertIn(phrase, normalized)

    def test_revocation_tombstones_survive_restart_and_dominate_trust(self) -> None:
        _, body = read_markdown(CANDIDATE)
        section = body.split("## Durable Revocation Tombstones", 1)[1].split(
            "\n## ", 1
        )[0]
        normalized = " ".join(section.split())
        required = (
            "deactivates the association and appends an effective tombstone",
            "Only after store and anchor finalization are durable",
            "takes precedence over a durable association",
            "blocks automatic reload",
            "Restart does not clear it",
            "Repair cannot delete, truncate, rewrite, or mark a tombstone ineffective",
            "Capacity exhaustion fails closed",
            "new association lineage",
        )
        for phrase in required:
            self.assertIn(phrase, normalized)

    def test_quarantine_backoff_is_persistent_bounded_and_monotonic_safe(self) -> None:
        _, body = read_markdown(CANDIDATE)
        section = body.split("## Persistent Quarantine And Backoff", 1)[1].split(
            "\n## ", 1
        )[0]
        normalized = " ".join(section.split())
        required = (
            "`BACKOFF_ACTIVE`, `RETRY_READY`, or `ADMIN_HOLD`",
            "saturating attempt count",
            "bounded remaining delay",
            "never retry automatically",
            "`min(base_backoff * 2^min(attempt_count, exponent_cap), max_backoff)`",
            "with no jitter",
            "Wall clock is never used to shorten a deadline",
            "conservatively rearms the complete persisted remainder",
            "can never decrement attempt state, shorten backoff, admit early retry, or restore trust",
            "Active records are never evicted",
            "At capacity, the coordinator enters `ADMIN_HOLD`",
        )
        for phrase in required:
            self.assertIn(phrase, normalized)

    def test_repair_is_exact_durable_idempotent_and_admin_local(self) -> None:
        _, body = read_markdown(CANDIDATE)
        section = body.split("## Deterministic Admin-Local Repair", 1)[1].split(
            "\n## ", 1
        )[0]
        normalized = " ".join(section.split())
        required = (
            "existing MSP-04B AF_UNIX endpoint only",
            "same-effective-UID authentication occurs before frame parsing",
            "no TCP, loopback, HTTP, CLI",
            "`expected_state`, `expected_reason`, selected manifest generation, manifest epoch, control epoch",
            "next monotonic repair sequence",
            "`repair_conflict` with no mutation",
            "existing one-writer lock",
            "including after restart, returns that result without a second mutation",
            "`idempotency_conflict`",
            "`idempotency_expired` with no mutation",
            "publishes a new generation",
            "cannot erase a reason, clear a tombstone",
            "or silently re-pair",
            "Trust is usable only after both are known durable",
            "`repair_outcome_unknown`",
            "No automatic retry occurs",
        )
        for phrase in required:
            self.assertIn(phrase, normalized)

    def test_host_key_recovery_is_explicit_and_lands_untrusted(self) -> None:
        _, body = read_markdown(CANDIDATE)
        section = body.split("## Backup And Unavailable-Key Recovery", 1)[1].split(
            "\n## ", 1
        )[0]
        normalized = " ".join(section.split())
        required = (
            "Generic backup is not a trust-preserving operation",
            "host-bound protected key cannot be unsealed on another host",
            "correctly backup-excluded key or anchor is absent after restore",
            "exact `recover_unavailable_host_key` repair",
            "fresh non-exporting local identity and fresh host anchor",
            "tombstones every recoverable association",
            "never exported, rebound, copied, or converted",
            "Success lands `UNPAIRED_LOCKED`",
            "Legacy MSP-04B state without an enrolled host anchor is not grandfathered",
        )
        for phrase in required:
            self.assertIn(phrase, normalized)

    def test_gate_rows_define_exact_redacted_pass_and_fail_evidence(self) -> None:
        _, body = read_markdown(CANDIDATE)
        self.assertEqual(
            table_column(body, "## G10, G11, And G16 Evidence Contract", 0),
            {"EEBUS-G10", "EEBUS-G11", "EEBUS-G16"},
        )
        section = body.split("## G10, G11, And G16 Evidence Contract", 1)[1].split(
            "\n## ", 1
        )[0]
        header = next(
            line for line in section.splitlines() if line.startswith("| Gate")
        )
        self.assertIn("PASS", header)
        self.assertIn("FAIL", header)
        for gate in ("EEBUS-G10", "EEBUS-G11", "EEBUS-G16"):
            row = next(
                line for line in section.splitlines() if line.startswith(f"| `{gate}`")
            )
            self.assertGreaterEqual(row.count("|"), 4)

        normalized = " ".join(section.split())
        required = (
            "zero trust registrations",
            "cannot reach `PAIRED_TRUSTED` before or after restart",
            "exact saturating attempt/backoff sequence",
            "deny early retry after monotonic rearm",
            "topology and credentials `not_applicable_synthetic`",
            "temporary paths `redacted`",
            "one PASS/FAIL row per required case",
        )
        for phrase in required:
            self.assertIn(phrase, normalized)

    def test_public_api_fixtures_and_hardware_are_confined(self) -> None:
        _, body = read_markdown(CANDIDATE)
        normalized = " ".join(body.split())
        required = (
            "supported public Go API remains byte-for-byte frozen",
            "adds no semantic identity, raw write, MCP tool/resource",
            "GraphQL field/mutation, Portal action, Home Assistant entity/service",
            "random per-run labels, and synthetic ordinal scopes only",
            "MUST NOT contain private keys, public-key encodings, certificates, SKIs",
            "stable peer identity",
            "Hardware checks remain SSH-only",
            "Raw store, anchor, admin frames, transcripts, and fixture internals are never published",
        )
        for phrase in required:
            self.assertIn(phrase, normalized)


if __name__ == "__main__":
    unittest.main()
