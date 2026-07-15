from __future__ import annotations

import re
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
CANDIDATE_REL = (
    "architecture/_candidate/"
    "msp-04c-restore-revocation-quarantine-repair.md"
)
CANDIDATE = ROOT / CANDIDATE_REL
MSP04B_CANDIDATE = ROOT / "architecture/_candidate/msp-04b-first-trust-admin-local.md"
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


def table_rows(body: str, heading: str) -> list[dict[str, str]]:
    if heading.startswith("|"):
        lines = body.splitlines()
        start = next(
            index for index, line in enumerate(lines) if line.startswith(heading)
        )
    else:
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


def code_values(value: str) -> set[str]:
    return set(re.findall(r"`([^`]+)`", value))


def state_values(value: str) -> set[str]:
    return {token for token in code_values(value) if re.fullmatch(r"[A-Z_]+", token)}


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
        anchor = body.split("## Durable Control And Host Anchor", 1)[1].split(
            "\n## ", 1
        )[0]
        self.assertRegex(
            " ".join(anchor.split()),
            r"host anchor is outside the restorable store set.*"
            r"no machine id, hostname, hardware serial.*"
            r"cannot be rolled back with the protected store",
        )

        descriptor_rows = table_rows(body, "| Field | Exact binding |")
        descriptor_fields = [code_value(row["Field"]) for row in descriptor_rows]
        self.assertEqual(
            descriptor_fields,
            [
                "operation_id",
                "operation_class",
                "store_instance",
                "previous_control_epoch",
                "target_control_epoch",
                "previous_manifest_epoch",
                "previous_manifest_sha256",
                "previous_generation",
                "target_manifest_epoch",
                "target_manifest_sha256",
                "target_generation",
            ],
        )
        binding_by_field = {
            code_value(row["Field"]): row["Exact binding"]
            for row in descriptor_rows
        }
        self.assertIn("previous_control_epoch + 1", binding_by_field["target_control_epoch"])
        self.assertIn("canonical target manifest", binding_by_field["target_manifest_sha256"])
        self.assertIn("Complete intended target generation reference", binding_by_field["target_generation"])

    def test_coordinated_publication_rolls_back_only_the_exact_pending_descriptor(self) -> None:
        _, body = read_markdown(CANDIDATE)
        outcome_rows = table_rows(body, "| Store result | Required exact anchor action")
        outcomes = {
            code_value(row["Store result"]): (
                code_values(row["Required exact anchor action"]),
                code_value(row["Allowed immediate result"]),
            )
            for row in outcome_rows
        }
        self.assertEqual(
            outcomes,
            {
                "commit_durable": (
                    {"compare_and_finalize(exact_descriptor)"},
                    "success_only_after_durable_finalize",
                ),
                "commit_not_published": (
                    {"compare_and_clear(exact_descriptor)"},
                    "failed_closed_unchanged_only_after_durable_clear",
                ),
                "commit_applied_maintenance_failed": (
                    {"retain(exact_descriptor)"},
                    "DURABILITY_UNKNOWN",
                ),
                "commit_durability_unknown": (
                    {"retain(exact_descriptor)"},
                    "DURABILITY_UNKNOWN",
                ),
                "interruption_or_descriptor_mismatch": (
                    {"retain(exact_descriptor)"},
                    "DURABILITY_UNKNOWN",
                ),
            },
        )

        reconciliation_rows = table_rows(
            body, "| Store observation | Required anchor action"
        )
        reconciliation = {
            code_value(row["Store observation"]): (
                code_value(row["Required anchor action"]),
                code_value(row["Reconciliation result"]),
            )
            for row in reconciliation_rows
        }
        self.assertEqual(
            reconciliation,
            {
                "exact_target_selected": (
                    "compare_and_finalize(exact_descriptor)",
                    "operation_terminal_only_after_durable_finalize",
                ),
                "exact_previous_selected_and_target_absent": (
                    "compare_and_clear(exact_descriptor)",
                    "failed_closed_unchanged_only_after_durable_clear",
                ),
                "same_number_different_digest_or_reference": (
                    "none",
                    "DURABILITY_UNKNOWN/QUARANTINED",
                ),
                "other_or_ambiguous": ("none", "DURABILITY_UNKNOWN/QUARANTINED"),
            },
        )
        publication = body.split("## Coordinated Store And Anchor Publication", 1)[
            1
        ].split("\n## ", 1)[0]
        self.assertRegex(
            " ".join(publication.split()),
            r"commit_not_published.*compare-and-clear.*"
            r"compare mismatch, clear failure, ambiguous durability result, or crash "
            r"before durable clear makes durability unknown and enters `QUARANTINED`",
        )

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

    def test_msp04b_and_msp04c_are_orthogonal_closed_state_axes(self) -> None:
        _, body = read_markdown(CANDIDATE)
        _, msp04b_body = read_markdown(MSP04B_CANDIDATE)

        msp04b_rows = table_rows(msp04b_body, "## Coordinator State Machine")
        msp04b_edges = {
            code_value(row["State"]): state_values(row["Allowed next state"])
            for row in msp04b_rows
        }
        self.assertEqual(
            msp04b_edges,
            {
                "DISABLED": {"PAIRING_CLOSED"},
                "PAIRING_CLOSED": {"OPEN_EMPTY"},
                "OPEN_EMPTY": {"CANDIDATE_PENDING", "PAIRING_CLOSED"},
                "CANDIDATE_PENDING": {
                    "COMMITTING",
                    "OPEN_EMPTY",
                    "PAIRING_CLOSED",
                },
                "COMMITTING": {"PAIRING_CLOSED", "DISABLED"},
            },
        )

        product_rows = table_rows(body, "### Valid Cross-Product")
        products = {
            code_value(row["MSP-04B coordinator state"]): state_values(
                row["Allowed MSP-04C recovery/trust states"]
            )
            for row in product_rows
        }
        self.assertEqual(
            products,
            {
                "DISABLED": {
                    "NO_LOCAL_IDENTITY",
                    "QUARANTINED",
                    "CORRUPT_STORE",
                },
                "PAIRING_CLOSED": {
                    "UNPAIRED_LOCKED",
                    "PAIRED_TRUSTED",
                    "REVOKED",
                },
                "OPEN_EMPTY": {"UNPAIRED_LOCKED", "REVOKED"},
                "CANDIDATE_PENDING": {"UNPAIRED_LOCKED", "REVOKED"},
                "COMMITTING": {"UNPAIRED_LOCKED", "REVOKED"},
            },
        )

        recovery_rows = table_rows(body, "### Recovery/Trust Axis Transitions")
        recovery_edges = {
            code_value(row["MSP-04C state"]): state_values(
                row["Allowed next MSP-04C states"]
            )
            for row in recovery_rows
        }
        self.assertEqual(
            recovery_edges,
            {
                "NO_LOCAL_IDENTITY": {"UNPAIRED_LOCKED", "QUARANTINED"},
                "UNPAIRED_LOCKED": {
                    "PAIRED_TRUSTED",
                    "QUARANTINED",
                    "CORRUPT_STORE",
                },
                "PAIRED_TRUSTED": {"REVOKED", "QUARANTINED", "CORRUPT_STORE"},
                "REVOKED": {"PAIRED_TRUSTED", "QUARANTINED"},
                "QUARANTINED": {
                    "UNPAIRED_LOCKED",
                    "REVOKED",
                    "CORRUPT_STORE",
                },
                "CORRUPT_STORE": {"UNPAIRED_LOCKED", "REVOKED", "QUARANTINED"},
            },
        )

        confirmation_rows = table_rows(
            body, "| Confirmation phase/outcome | Required combined transition |"
        )
        confirmation_transitions = {
            code_value(row["Confirmation phase/outcome"]): code_value(
                row["Required combined transition"]
            )
            for row in confirmation_rows
        }
        self.assertEqual(
            confirmation_transitions,
            {
                "exact_confirmation_linearizes": (
                    "CANDIDATE_PENDING/untrusted -> COMMITTING/same_untrusted"
                ),
                "store_and_anchor_durable": (
                    "COMMITTING/same_untrusted -> PAIRING_CLOSED/PAIRED_TRUSTED"
                ),
                "commit_not_published_and_anchor_cleared": (
                    "COMMITTING/same_untrusted -> PAIRING_CLOSED/same_untrusted"
                ),
                "publication_unknown": (
                    "COMMITTING/same_untrusted -> DISABLED/QUARANTINED"
                ),
            },
        )

        precedence_rows = table_rows(body, "### Transition Precedence And Linearization")
        self.assertEqual(
            [code_value(row["Precedence"]) for row in precedence_rows],
            ["1", "2", "3", "4"],
        )
        self.assertIn(
            "one-writer lock",
            " ".join(
                body.split("### Transition Precedence And Linearization", 1)[1]
                .split("\n## ", 1)[0]
                .split()
            ),
        )

    def test_revocation_is_one_closed_bound_idempotent_admin_command(self) -> None:
        _, body = read_markdown(CANDIDATE)
        section = body.split("## Durable Revocation Tombstones", 1)[1].split(
            "\n## ", 1
        )[0]
        normalized = " ".join(section.split())
        self.assertRegex(
            normalized,
            r"Revocation is exactly the `revoke_association` command in the closed "
            r"command set of the existing MSP-04B AF_UNIX admin endpoint.*"
            r"same-effective-UID authentication succeeds before frame parsing.*"
            r"no TCP, loopback, HTTP, CLI.*other public revocation path",
        )

        binding_rows = table_rows(
            body, "| Revocation request field | Exact binding |"
        )
        self.assertEqual(
            [code_value(row["Revocation request field"]) for row in binding_rows],
            [
                "operation_id",
                "association_ref",
                "association_lineage",
                "expected_store_generation",
                "expected_manifest_epoch",
                "expected_manifest_sha256",
                "expected_control_epoch",
            ],
        )

        replay_rows = table_rows(
            body, "| Revocation request condition | Stable result | Additional mutation |"
        )
        replay_map = {
            code_value(row["Revocation request condition"]): (
                code_value(row["Stable result"]),
                code_value(row["Additional mutation"]),
            )
            for row in replay_rows
        }
        self.assertEqual(
            replay_map,
            {
                "new_exact_request": ("commit_once", "one_coordinated_publication"),
                "identical_in_flight_replay": ("operation_in_progress", "none"),
                "identical_terminal_replay": ("recorded_terminal_result", "none"),
                "operation_id_with_changed_binding": ("idempotency_conflict", "none"),
                "stale_association_or_generation": ("revocation_conflict", "none"),
                "replay_at_or_below_compacted_high_water": (
                    "idempotency_expired",
                    "none",
                ),
            },
        )
        self.assertRegex(
            normalized,
            r"same one-writer lock.*full request binding and terminal result.*"
            r"idempotent across restart.*deactivates the association and appends an "
            r"effective tombstone.*Only after store and anchor finalization are durable.*"
            r"tombstone takes precedence over a durable association and blocks automatic "
            r"reload.*Restart does not clear it",
        )

    def test_g11_backoff_formula_saturation_and_restart_vector_are_exact(self) -> None:
        _, body = read_markdown(CANDIDATE)
        section = body.split("## Persistent Quarantine And Backoff", 1)[1].split(
            "\n## ", 1
        )[0]
        normalized = " ".join(section.split())
        self.assertIn(
            "(state=RETRY_READY, attempt_count=0, remaining_delay=0)", normalized
        )
        formula = re.search(r"```text\n(?P<formula>.*?)\n```", section, re.DOTALL)
        self.assertIsNotNone(formula)
        self.assertEqual(
            formula.group("formula").splitlines(),
            [
                "next_attempt_count = min(attempt_count + 1, attempt_count_max)",
                "exponent = min(next_attempt_count - 1, exponent_cap)",
                "delay = min(checked(base_backoff * 2^exponent), max_backoff)",
                "next = (BACKOFF_ACTIVE, next_attempt_count, delay)",
            ],
        )
        self.assertRegex(
            normalized,
            r"count increments exactly at failure linearization, never on admission, denial, "
            r"restart, deadline expiry, or wall-clock change.*At `attempt_count_max`.*"
            r"Checked multiplication that would overflow saturates to `max_backoff`.*"
            r"invalid configured or decoded bound.*enters `ADMIN_HOLD` and admits no retry",
        )

        vector_rows = table_rows(
            body,
            "| Step | Event | Previous count | Persisted count | Persisted delay | Persisted state |",
        )
        vector = [
            tuple(code_value(value) for value in row.values()) for row in vector_rows
        ]
        self.assertEqual(
            vector,
            [
                ("0", "new_scope", "not_applicable", "0", "0s", "RETRY_READY"),
                ("1", "first_admitted_failure", "0", "1", "3s", "BACKOFF_ACTIVE"),
                ("2", "second_admitted_failure", "1", "2", "6s", "BACKOFF_ACTIVE"),
                ("3", "third_admitted_failure", "2", "3", "10s", "BACKOFF_ACTIVE"),
                ("4", "fourth_admitted_failure", "3", "4", "10s", "BACKOFF_ACTIVE"),
                ("5", "failure_at_saturated_count", "4", "4", "10s", "BACKOFF_ACTIVE"),
            ],
        )

        restart_rows = table_rows(
            body,
            "| Checkpoint | Durable tuple | Volatile monotonic state | Required decision |",
        )
        restart_vector = [
            tuple(code_value(value) for value in row.values()) for row in restart_rows
        ]
        self.assertEqual(
            restart_vector,
            [
                (
                    "after_step_2",
                    "BACKOFF_ACTIVE,count=2,remainder=6s",
                    "now=20s,deadline=26s",
                    "deny_retry",
                ),
                (
                    "durable_checkpoint_after_2s",
                    "BACKOFF_ACTIVE,count=2,remainder=4s",
                    "now=22s,deadline=26s",
                    "deny_retry",
                ),
                (
                    "restart_with_arbitrary_wall_change",
                    "BACKOFF_ACTIVE,count=2,remainder=4s",
                    "new_now=100s,new_deadline=104s",
                    "deny_retry",
                ),
                (
                    "probe_before_rearmed_deadline",
                    "BACKOFF_ACTIVE,count=2,remainder=4s",
                    "new_now=103.999s,new_deadline=104s",
                    "deny_retry",
                ),
                (
                    "probe_at_rearmed_deadline",
                    "RETRY_READY,count=2,remainder=0s",
                    "new_now=104s",
                    "persist_ready_before_admit",
                ),
            ],
        )

    def test_repair_is_exact_durable_idempotent_and_admin_local(self) -> None:
        _, body = read_markdown(CANDIDATE)
        section = body.split("## Deterministic Admin-Local Repair", 1)[1].split(
            "\n## ", 1
        )[0]
        normalized = " ".join(section.split())
        self.assertRegex(
            normalized,
            r"existing MSP-04B AF_UNIX endpoint only.*same-effective-UID "
            r"authentication occurs before frame parsing.*There is no TCP, loopback, "
            r"HTTP, CLI.*complete selected manifest epoch, digest, and current/parent "
            r"generation references, control epoch.*`repair_conflict` with no mutation",
        )
        self.assertEqual(
            set(
                re.findall(
                    r"`(reconcile_pending_publication|publish_inactive_parent|"
                    r"adopt_copied_current|recover_unavailable_host_key|"
                    r"release_retry_quarantine)`",
                    section,
                )
            ),
            {
                "reconcile_pending_publication",
                "publish_inactive_parent",
                "adopt_copied_current",
                "recover_unavailable_host_key",
                "release_retry_quarantine",
            },
        )
        self.assertRegex(
            normalized,
            r"existing one-writer lock.*including after restart, returns that result "
            r"without a second mutation.*publishes a new generation.*"
            r"cannot erase a reason, clear a tombstone.*silently re-pair.*"
            r"failed pending clear.*`repair_outcome_unknown`, enters `QUARANTINED`.*"
            r"No automatic retry occurs",
        )

    def test_inherited_trust_repairs_atomically_publish_a_fresh_untrusted_lineage(self) -> None:
        _, body = read_markdown(CANDIDATE)
        lineage_rows = table_rows(body, "### Untrusted-Lineage Repair Invariant")
        lineage_map = {
            code_value(row["Repair kind"]): (
                code_value(row["Exact source content"]),
                code_value(row["Target lineage"]),
                code_value(row["Inherited association effect"]),
                code_value(row["Success product"]),
            )
            for row in lineage_rows
        }
        self.assertEqual(
            lineage_map,
            {
                "publish_inactive_parent": (
                    "selected_manifest.parent",
                    "fresh_random",
                    "deactivate_all+effective_tombstone_each",
                    "PAIRING_CLOSED/UNPAIRED_LOCKED",
                ),
                "adopt_copied_current": (
                    "selected_manifest.current",
                    "fresh_random",
                    "deactivate_all+effective_tombstone_each",
                    "PAIRING_CLOSED/UNPAIRED_LOCKED",
                ),
                "recover_unavailable_host_key": (
                    "selected_manifest.current",
                    "fresh_random",
                    "deactivate_all+effective_tombstone_each",
                    "PAIRING_CLOSED/UNPAIRED_LOCKED",
                ),
            },
        )
        invariant = body.split("### Untrusted-Lineage Repair Invariant", 1)[1].split(
            "\n## ", 1
        )[0]
        self.assertRegex(
            " ".join(invariant.split()),
            r"every association record in the exact source generation.*"
            r"without filtering by current reachability, expiry, key availability, or "
            r"peer liveness.*One target generation atomically records a fresh random "
            r"association-lineage value, marks every member.*inactive, and appends one "
            r"effective tombstone for each member.*cannot report success until that "
            r"complete generation and its exact anchor finalization are durable.*"
            r"On restart.*zero inherited association may reload trust.*"
            r"`RegisterRemoteSKI`",
        )

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
            "complete untrusted-lineage invariant to every inherited association",
            "never exported, rebound, copied, or converted",
            "Success lands `UNPAIRED_LOCKED`",
            "Legacy MSP-04B state without an enrolled host anchor is not grandfathered",
        )
        for phrase in required:
            self.assertIn(phrase, normalized)

    def test_gate_rows_define_exact_redacted_pass_and_fail_evidence(self) -> None:
        _, body = read_markdown(CANDIDATE)
        gate_rows = table_rows(body, "## G10, G11, And G16 Evidence Contract")
        gates = {code_value(row["Gate"]): row for row in gate_rows}
        self.assertEqual(set(gates), {"EEBUS-G10", "EEBUS-G11", "EEBUS-G16"})
        self.assertIn(
            "fresh lineage with every inherited trusted association inactive and tombstoned",
            gates["EEBUS-G10"]["Deterministic PASS"],
        )
        self.assertIn(
            "same-number/different-digest branch",
            gates["EEBUS-G10"]["Deterministic FAIL"],
        )
        self.assertIn(
            "counts `0,1,2,3,4,4`",
            gates["EEBUS-G11"]["Deterministic PASS"],
        )
        self.assertIn(
            "increment occurs anywhere except failed-attempt linearization",
            gates["EEBUS-G11"]["Deterministic FAIL"],
        )
        section = body.split("## G10, G11, And G16 Evidence Contract", 1)[1].split(
            "\n## ", 1
        )[0]
        normalized = " ".join(section.split())
        required = (
            "zero trust registrations",
            "cannot reach `PAIRED_TRUSTED` before or after restart",
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
