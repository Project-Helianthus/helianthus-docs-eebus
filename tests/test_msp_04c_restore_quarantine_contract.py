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


def section_blocks(body: str, heading: str) -> list[str]:
    section = body.split(heading, 1)[1].split("\n## ", 1)[0].strip()
    return [" ".join(block.split()) for block in section.split("\n\n")]


def require_equal(actual: object, expected: object, label: str) -> None:
    if actual != expected:
        raise AssertionError(f"{label} differs: {actual!r}")


def require_markers(value: str, markers: tuple[str, ...], label: str) -> None:
    missing = [marker for marker in markers if marker not in value]
    if missing:
        raise AssertionError(f"{label} missing markers: {missing!r}")


def mutate_once(body: str, old: str, new: str) -> str:
    if body.count(old) != 1:
        raise AssertionError(f"mutation source is not unique: {old!r}")
    return body.replace(old, new, 1)


def mutate_normalized_once(body: str, old: str, new: str) -> str:
    pattern = re.compile(r"\s+".join(re.escape(part) for part in old.split()))
    matches = list(pattern.finditer(body))
    if len(matches) != 1:
        raise AssertionError(f"normalized mutation source is not unique: {old!r}")
    match = matches[0]
    return body[: match.start()] + new + body[match.end() :]


RUNTIME_EFFECTS = [
    (
        "startup_restore",
        "classify_startup_and_restore_retry",
        "none_before_durable_classification",
    ),
    (
        "listener_start",
        "authorize_listener_start(classified_state)",
        "start_listener",
    ),
    (
        "pairing_handshake",
        "authorize_handshake(exact_scope)",
        "real_pairing_transport_callback",
    ),
    (
        "remote_registration",
        "authorize_register_remote_ski(exact_association)",
        "RegisterRemoteSKI",
    ),
    (
        "reconnect_attempt",
        "authorize_reconnect(exact_association,exact_scope)",
        "reconnect",
    ),
    (
        "handshake_failure",
        "record_failure_and_checkpoint(exact_scope)",
        "no_next_attempt_before_durable_result",
    ),
]

RUNTIME_PROSE = [
    (
        "Startup keeps listener creation, remote registration, reconnect "
        "scheduling, and pairing callbacks inert. Store/anchor selection, "
        "tombstone precedence, trust classification and retry restoration "
        "complete before any listener is started or any remote effect is "
        "considered. A classification or restore failure therefore disables "
        "those effects rather than allowing the production runtime to start "
        "and attempting to withdraw them later."
    ),
    (
        "Every call to `RegisterRemoteSKI` and every reconnect decision is "
        "coordinator-authorized against the exact selected generation, control "
        "epoch, association lineage, tombstone set, trust state, and retry "
        "scope. No runtime adapter, restored configuration, library callback, "
        "or caller may infer that authorization. Authorization and the "
        "corresponding effect are serialized with revocation and repair; an "
        "asynchronous completion is revalidated before it can make trust "
        "usable, and a stale completion is actively disconnected and "
        "unregistered."
    ),
    (
        "The real pairing callback on the SHIP path obtains admission before "
        "continuing a handshake. Its terminal failure path records the failure "
        "into durable retry state and completes a durable remaining-delay "
        "checkpoint before the callback releases the scope for another "
        "attempt. The production checkpoint path persists only a same-boot "
        "monotonic reduction, and startup restores the persisted state and "
        "rearms it on the new monotonic clock before any effect. The same "
        "listener, registration, handshake, and reconnect authorization path "
        "observes that restored state after restart."
    ),
    (
        "A helper-only backoff API, direct coordinator unit call, caller-provided "
        "success/failure assertion, or transcript that does not execute this "
        "production composition is not G11 proof. The real callback must drive "
        "the coordinator record, checkpoint, restart restore, bounded backoff, "
        "and terminal quarantine."
    ),
]

GATE_FIELD_MARKERS = {
    ("EEBUS-G10", "Deterministic PASS"): (
        "Executed startup/runtime integration behavior",
        "through the production composition",
        "observed effects show zero trust registrations",
    ),
    ("EEBUS-G10", "Deterministic FAIL"): (
        "invokes `RegisterRemoteSKI`",
        "relies only on a helper-returned decision",
    ),
    ("EEBUS-G11", "Deterministic PASS"): (
        "Executed integration behavior drives the real pairing callback",
        "specified durable checkpoint and monotonic restart arm",
        "terminal `ADMIN_HOLD`",
    ),
    ("EEBUS-G11", "Deterministic FAIL"): (
        "The real callback bypasses failure recording or checkpointing",
        "the ceiling admits another handshake/reconnect",
    ),
    ("EEBUS-G16", "Deterministic PASS"): (
        "Executed integration artifacts",
        "Scans over the actual callbacks, effects",
    ),
    ("EEBUS-G16", "Deterministic FAIL"): (
        "frozen API diff changes",
        "scan input omits executed production-composition output",
    ),
}

GATE_PROSE = [
    (
        "Only executed integration behavior from the production-composed "
        "lifecycle supplies G10, G11, or G16 evidence. A result is rejected "
        "because caller assertions and helper transcripts are not evidence. "
        "The collector derives registration, reconnect, callback, disconnect, "
        "unregister, checkpoint, restart, and terminal-state fields from "
        "observed effects and coordinator state; a test caller cannot submit "
        "those fields as claimed booleans. Helper-only transcripts may diagnose "
        "a failure but cannot produce a PASS row."
    ),
    (
        "The compact public artifact identifies `MSP-04C`, exact commit and "
        "commands, marks topology and credentials `not_applicable_synthetic`, "
        "marks temporary paths `redacted`, and includes one PASS/FAIL row per "
        "required case. Raw store, anchor, admin frames, transcripts, and fixture "
        "internals are never published. Case ordering and output bytes are "
        "independent of scheduler, map/directory order, locale, wall clock, and "
        "failure wording."
    ),
]

MSP045_ENTRY_CONTRACT = {
    "entry_precondition": "corrective_source_merged+evidence_bound+architecture_pass",
    "freeze_scope": (
        "coordinator_ownership+combined_fsm+read_only_trust_admin_projection"
    ),
    "platform_providers": "deferred",
    "consumers": "deferred",
    "post_freeze_change": "explicit_contract_migration",
}

MSP045_PROSE = [
    (
        "The locked [MSP-045 row][freeze-plan-row] is an interface freeze after "
        "the M4 correction, not permission to start downstream platform or "
        "consumer work. MSP-045 must not start until the corrective source merge "
        "populates every applicable source-evidence field above, executed G10, "
        "G11, and G16 artifacts pass, and a bounded architecture closure review "
        "returns `PASS` or `PASS_WITH_CARRIED_EVIDENCE`. Carried evidence is "
        "limited to the explicit SSH-only platform-attestation limitation; it "
        "cannot carry a runtime-composition or gate failure."
    ),
    (
        "MSP-045 may then freeze only coordinator ownership, the combined "
        "MSP-04B/MSP-04C state machines, and the read-only trust/admin projection "
        "that later consumers can use without ad hoc security decisions. A later "
        "change to those frozen semantics requires explicit contract migration. "
        "MSP-045 does not implement or freeze a platform provider. It does not "
        "implement a gateway, MCP, Portal, Home Assistant, or other consumer. "
        "Provider backends and their platform attestations remain separate "
        "conformance work; consumer implementation remains in its downstream "
        "milestone and repository."
    ),
]


def validate_runtime_authorization_contract(body: str) -> None:
    rows = table_rows(body, "## Production Runtime Composition And Authorization")
    effects = [
        (
            code_value(row["Runtime event"]),
            code_value(row["Required coordinator decision"]),
            code_value(row["Permitted effect"]),
        )
        for row in rows
    ]
    require_equal(effects, RUNTIME_EFFECTS, "runtime authorization table")

    blocks = section_blocks(body, "## Production Runtime Composition And Authorization")
    require_equal(len(blocks), 5, "runtime authorization block count")
    require_equal(
        [blocks[0], blocks[2], blocks[3], blocks[4]],
        RUNTIME_PROSE,
        "runtime authorization normative prose",
    )


def validate_gate_evidence_contract(body: str) -> None:
    rows = table_rows(body, "## G10, G11, And G16 Evidence Contract")
    gates = {code_value(row["Gate"]): row for row in rows}
    require_equal(
        set(gates),
        {"EEBUS-G10", "EEBUS-G11", "EEBUS-G16"},
        "gate evidence rows",
    )
    for (gate, field), markers in GATE_FIELD_MARKERS.items():
        require_markers(gates[gate][field], markers, f"{gate} {field}")

    blocks = section_blocks(body, "## G10, G11, And G16 Evidence Contract")
    require_equal(len(blocks), 3, "gate evidence block count")
    require_equal(blocks[1:], GATE_PROSE, "gate evidence normative prose")


def validate_msp045_entry_contract(body: str) -> None:
    rows = table_rows(body, "## MSP-045 Entry Contract")
    entry_contract = {
        code_value(row["Boundary"]): code_value(row["MSP-045 decision"])
        for row in rows
    }
    require_equal(entry_contract, MSP045_ENTRY_CONTRACT, "MSP-045 entry table")

    blocks = section_blocks(body, "## MSP-045 Entry Contract")
    require_equal(len(blocks), 3, "MSP-045 block count")
    require_equal(
        [blocks[0], blocks[2]],
        MSP045_PROSE,
        "MSP-045 normative prose",
    )


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
            "https://github.com/Project-Helianthus/helianthus-docs-eebus/issues/26",
            "https://github.com/Project-Helianthus/helianthus-eebusreg/issues/30",
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

        withdrawal_rows = table_rows(body, "### Authoritative Runtime Withdrawal")
        withdrawal = [
            (
                code_value(row["Revocation phase"]),
                code_value(row["Required effect"]),
                code_value(row["Success condition"]),
            )
            for row in withdrawal_rows
        ]
        self.assertEqual(
            withdrawal,
            [
                (
                    "deny_in_memory",
                    "coordinator_deny_exact_association",
                    "registration_and_reconnect_denied",
                ),
                (
                    "commit_tombstone",
                    "durable_coordinated_publication",
                    "tombstone_and_anchor_finalized",
                ),
                (
                    "disconnect_active_session",
                    "DisconnectSKI(exact_remote_ski)",
                    "disconnected_or_authoritatively_absent",
                ),
                (
                    "unregister_remote",
                    "UnregisterRemoteSKI(exact_remote_ski)",
                    "unregistered_or_authoritatively_absent",
                ),
                (
                    "return_success",
                    "record_terminal_revoked",
                    "all_prior_phases_complete",
                ),
            ],
        )
        self.assertRegex(
            normalized,
            r"does not report `revoked`.*`DisconnectSKI`.*`UnregisterRemoteSKI`.*"
            r"withdrawal fails or is ambiguous.*tombstone remains effective.*"
            r"startup.*must not call `RegisterRemoteSKI`.*tombstoned",
        )

    def test_live_runtime_effects_require_coordinator_authorization(self) -> None:
        _, body = read_markdown(CANDIDATE)
        validate_runtime_authorization_contract(body)

    def test_runtime_authorization_validator_rejects_weakened_prose(self) -> None:
        _, body = read_markdown(CANDIDATE)
        mutations = (
            (
                "classification_after_effects",
                "trust classification and retry restoration complete before any "
                "listener is started or any remote effect is considered",
                "trust classification and retry restoration may complete after a "
                "listener is started or a remote effect is considered",
            ),
            (
                "non_universal_authorization",
                "Every call to `RegisterRemoteSKI` and every reconnect decision is "
                "coordinator-authorized",
                "Some calls to `RegisterRemoteSKI` and some reconnect decisions are "
                "coordinator-authorized",
            ),
            (
                "negated_startup_inertness",
                "Startup keeps listener creation, remote registration, reconnect "
                "scheduling, and pairing callbacks inert.",
                "Startup does not keep listener creation, remote registration, "
                "reconnect scheduling, and pairing callbacks inert.",
            ),
            (
                "caller_authorized_registration",
                "| `remote_registration` | "
                "`authorize_register_remote_ski(exact_association)` | "
                "`RegisterRemoteSKI` |",
                "| `remote_registration` | `caller_authorized` | "
                "`RegisterRemoteSKI` |",
            ),
        )
        for label, old, new in mutations:
            with self.subTest(label=label):
                mutated = mutate_normalized_once(body, old, new)
                with self.assertRaises(AssertionError):
                    validate_runtime_authorization_contract(mutated)

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
                "if next_attempt_count == attempt_count_max:",
                "    next = (ADMIN_HOLD, next_attempt_count, 0, HANDSHAKE_ATTEMPT_LIMIT)",
                "else:",
                "    exponent = min(next_attempt_count - 1, exponent_cap)",
                "    delay = min(checked(base_backoff * 2^exponent), max_backoff)",
                "    next = (BACKOFF_ACTIVE, next_attempt_count, delay)",
            ],
        )
        self.assertRegex(
            normalized,
            r"count increments exactly at failure linearization, never on admission, denial, "
            r"restart, deadline expiry, or wall-clock change.*At `attempt_count_max`.*"
            r"terminal `ADMIN_HOLD`.*no later handshake or reconnect.*"
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
                (
                    "4",
                    "fourth_admitted_failure",
                    "3",
                    "4",
                    "0s",
                    "ADMIN_HOLD",
                ),
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
        validate_gate_evidence_contract(body)

    def test_gate_evidence_validator_rejects_each_cell_mutation(self) -> None:
        _, body = read_markdown(CANDIDATE)
        mutations = (
            (
                "g10_pass",
                "Executed startup/runtime integration behavior",
                "Helper-simulated startup behavior",
            ),
            (
                "g10_fail",
                "relies only on a helper-returned decision",
                "relies on a returned decision",
            ),
            (
                "g11_pass",
                "Executed integration behavior drives the real pairing callback",
                "A helper drives a pairing callback",
            ),
            (
                "g11_fail",
                "The real callback bypasses failure recording or checkpointing",
                "A helper bypasses failure recording",
            ),
            (
                "g16_pass",
                "Executed integration artifacts",
                "Caller-asserted artifacts",
            ),
            (
                "g16_fail",
                "scan input omits executed production-composition output",
                "scan input omits helper output",
            ),
        )
        for label, old, new in mutations:
            with self.subTest(label=label):
                mutated = mutate_once(body, old, new)
                with self.assertRaises(AssertionError):
                    validate_gate_evidence_contract(mutated)

    def test_corrective_source_evidence_stays_pending_until_merge(self) -> None:
        _, body = read_markdown(CANDIDATE)
        rows = table_rows(body, "## Corrective Source Evidence Status")
        evidence = [
            (
                code_value(row["Evidence field"]),
                code_value(row["Candidate value"]),
            )
            for row in rows
        ]
        self.assertEqual(
            evidence,
            [
                ("corrective_source_head_sha", "pending"),
                ("corrective_source_merge_sha", "pending"),
                ("corrective_source_exact_head_ci_run", "pending"),
                ("corrective_source_post_merge_ci_run", "pending"),
                ("eebus_g10_integration_artifact", "pending"),
                ("eebus_g11_integration_artifact", "pending"),
                ("eebus_g16_integration_artifact", "pending"),
                ("m4_architecture_closure_verdict", "pending"),
                (
                    "platform_provider_attestation",
                    "pending_ssh_only_non_normative",
                ),
            ],
        )
        section = body.split("## Corrective Source Evidence Status", 1)[1].split(
            "\n## ", 1
        )[0]
        normalized = " ".join(section.split())
        self.assertIn(
            "https://github.com/Project-Helianthus/helianthus-eebusreg/issues/30",
            section,
        )
        self.assertRegex(
            normalized,
            r"remain pending until the corrective source merges.*"
            r"does not satisfy or replace any executed integration field.*"
            r"SSH-only.*supporting, non-normative.*cannot clear.*"
            r"platform_provider_attestation",
        )

    def test_msp045_entry_freezes_only_corrected_architecture_contract(self) -> None:
        _, body = read_markdown(CANDIDATE)
        validate_msp045_entry_contract(body)

    def test_msp045_validator_rejects_broadened_carried_evidence(self) -> None:
        _, body = read_markdown(CANDIDATE)
        boundary = (
            "Carried evidence is limited to the explicit SSH-only "
            "platform-attestation limitation; it cannot carry a "
            "runtime-composition or gate failure."
        )
        mutations = (
            (
                "additional_provider_evidence",
                boundary,
                "Carried evidence may include the SSH-only platform-attestation "
                "limitation and other provider limitations; it cannot carry a "
                "runtime-composition or gate failure.",
            ),
            (
                "runtime_composition_carried",
                boundary,
                "Carried evidence is limited to the explicit SSH-only "
                "platform-attestation limitation; it may also carry a "
                "runtime-composition failure.",
            ),
            (
                "gate_failure_carried",
                boundary,
                "Carried evidence is limited to the explicit SSH-only "
                "platform-attestation limitation; it may also carry a gate failure.",
            ),
        )
        for label, old, new in mutations:
            with self.subTest(label=label):
                mutated = mutate_normalized_once(body, old, new)
                with self.assertRaises(AssertionError):
                    validate_msp045_entry_contract(mutated)

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
