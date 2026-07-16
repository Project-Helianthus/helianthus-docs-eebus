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


def coded_rows(body: str, heading: str, columns: tuple[str, ...]) -> list[tuple[str, ...]]:
    return [
        tuple(code_value(row[column]) for column in columns)
        for row in table_rows(body, heading)
    ]


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
        "durable reservation timestamp/order and attempt id",
        "actual `DialContext` and fake-peer accept observations",
        "zero dials for denial, publication failure, backoff, quarantine, "
        "and terminal hold",
    ),
    ("EEBUS-G10", "Deterministic FAIL"): (
        "invokes `RegisterRemoteSKI`",
        "relies only on a helper-returned decision",
        "reaches a dial before durable reservation/permit",
        "treats callback injection as pre-dial evidence",
    ),
    ("EEBUS-G11", "Deterministic PASS"): (
        "Executed integration behavior drives the real pairing callback",
        "specified durable checkpoint and monotonic restart arm",
        "terminal `ADMIN_HOLD`",
        "durable reservation timestamp/order and attempt id",
        "path fallback, hostname/IPv4/IPv6 retry",
    ),
    ("EEBUS-G11", "Deterministic FAIL"): (
        "The real callback bypasses failure recording or checkpointing",
        "the ceiling admits another handshake/reconnect",
        "permit count differs from `DialContext` count",
        "injected callbacks pass without dial/accept observations",
    ),
    ("EEBUS-G16", "Deterministic PASS"): (
        "Executed integration artifacts",
        "Scans over the actual callbacks, effects",
        "redacted durable reservation timestamp/order and synthetic attempt id",
        "actual `DialContext` and fake-peer accept observations",
    ),
    ("EEBUS-G16", "Deterministic FAIL"): (
        "frozen API diff changes",
        "scan input omits executed production-composition output",
        "callback-only evidence is accepted without the reservation/dial/accept binding",
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
        "Each G10, G11, and G16 PASS row independently requires the same "
        "attempt-bound chain: durable reservation timestamp/order, durable "
        "attempt id, gate permit, actual `DialContext` observation, and "
        "fake-peer accept observation when the peer accepts. Callback injection "
        "is not pre-dial evidence and cannot satisfy any one of the three rows."
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
    "entry_precondition": (
        "three_repo_stages_merged+predial_evidence_bound+closure_pass"
    ),
    "required_repo_stages": "ship_go_fork+eebus_go_bridge+eebusreg_adoption",
    "closure_verdict": "PASS_or_SSH_ONLY_CARRIED",
    "carried_evidence": "ssh_only_provider_attestation",
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
        "the M4 R2 correction, not permission to start downstream platform or "
        "consumer work. MSP-045 must not start until the ship-go fork, eebus-go "
        "bridge, and eebusreg adoption stages have all merged in that order; "
        "every applicable R2 evidence field is populated; executed G10, G11, "
        "and G16 artifacts pass; and a bounded architecture closure review "
        "returns `PASS` or `PASS_WITH_CARRIED_EVIDENCE`. Carried evidence is "
        "limited to the explicit SSH-only provider-attestation limitation. A "
        "dependency fork, module graph, pre-dial runtime composition, "
        "reservation, revocation race, or gate failure cannot be carried."
    ),
    (
        "MSP-045 may then freeze only coordinator ownership, the combined "
        "MSP-04B/MSP-04C state machines, and the read-only trust/admin projection "
        "that later consumers can use without ad hoc security decisions. A later "
        "change to those frozen semantics requires explicit contract migration. "
        "MSP-045 does not implement or freeze either dependency fork or a "
        "platform provider. It does not implement a gateway, MCP, Portal, Home "
        "Assistant, or other consumer. Fork maintenance, provider backends, and "
        "platform attestations remain separate conformance work; consumer "
        "implementation remains in its downstream milestone and repository."
    ),
]

R2_PENDING_EVIDENCE = [
    ("ship_go_fork_head_sha", "pending"),
    ("ship_go_fork_merge_sha", "pending"),
    ("ship_go_prerelease_tag", "pending"),
    ("ship_go_tag_target_sha", "pending"),
    ("ship_go_exact_head_ci_run", "pending"),
    ("ship_go_post_merge_ci_run", "pending"),
    ("eebus_go_fork_head_sha", "pending"),
    ("eebus_go_fork_merge_sha", "pending"),
    ("eebus_go_prerelease_tag", "pending"),
    ("eebus_go_tag_target_sha", "pending"),
    ("eebus_go_exact_head_ci_run", "pending"),
    ("eebus_go_post_merge_ci_run", "pending"),
    ("eebusreg_adoption_head_sha", "pending"),
    ("eebusreg_adoption_merge_sha", "pending"),
    ("eebusreg_adoption_exact_head_ci_run", "pending"),
    ("eebusreg_adoption_post_merge_ci_run", "pending"),
    ("eebus_g10_predial_artifact", "pending"),
    ("eebus_g11_predial_artifact", "pending"),
    ("eebus_g16_predial_artifact", "pending"),
    ("m4_r2_architecture_closure_verdict", "pending"),
    ("r2_platform_provider_attestation", "pending_ssh_only_non_normative"),
]

R2_FORK_STAGES = [
    (
        "ship_go_fork",
        "github.com/enbility/ship-go@v0.6.0",
        "github.com/Project-Helianthus/helianthus-ship-go",
        "license+notices+headers+upstream_remote+baseline_commit",
        "reviewed_semver_prerelease",
    ),
    (
        "eebus_go_fork",
        "github.com/enbility/eebus-go@v0.7.0",
        "github.com/Project-Helianthus/helianthus-eebus-go",
        "license+notices+headers+upstream_remote+baseline_commit",
        "reviewed_semver_prerelease",
    ),
    (
        "eebusreg_adoption",
        "helianthus-eebusreg_current_main",
        "internal_bridge_only",
        "exact_fork_tags+module_graph+public_api_diff",
        "merge_after_both_fork_tags",
    ),
]

R2_GATE_SCHEMA = [
    (
        "remote_ski",
        "input",
        "Exact opaque remote key for the selected association; never logged or published.",
    ),
    (
        "scope",
        "input",
        "Exact coordinator retry/quarantine scope for this concrete attempt.",
    ),
    (
        "control_epoch",
        "input",
        "Exact current coordinator epoch used for authorization and stale-callback rejection.",
    ),
    (
        "endpoint",
        "input",
        "Exact selected hostname, IPv4, or IPv6 endpoint plus port in private typed form.",
    ),
    (
        "path",
        "input",
        "Exact selected websocket path, including the `/ship` path fallback when chosen.",
    ),
    (
        "attempt_id",
        "input",
        "Fresh bounded coordinator id, unique within the current store instance and control epoch.",
    ),
    (
        "attempt_context",
        "input",
        "Exact per-attempt cancellable context retained by the coordinator until terminal resolution.",
    ),
    (
        "decision",
        "output",
        "Exactly `PERMIT` or `DENY`; absence, error, panic, or ambiguity is `DENY`.",
    ),
    (
        "reason",
        "output",
        "One stable closed permit/deny reason with no endpoint, key, path, or private error text.",
    ),
]

R2_DIAL_COVERAGE = [
    (
        "primary_endpoint_primary_path",
        "immediately_before_DialContext",
        "one_PERMIT_per_network_call",
    ),
    (
        "same_endpoint_ship_path_fallback",
        "immediately_before_DialContext",
        "one_fresh_gate_decision_per_network_call",
    ),
    (
        "hostname_retry",
        "immediately_before_DialContext",
        "one_fresh_gate_decision_per_network_call",
    ),
    (
        "ipv4_retry",
        "immediately_before_DialContext",
        "one_fresh_gate_decision_per_network_call",
    ),
    (
        "ipv6_retry",
        "immediately_before_DialContext",
        "one_fresh_gate_decision_per_network_call",
    ),
]

R2_RESERVATION_FIELDS = [
    (
        "state",
        "durable",
        "Exactly `ATTEMPT_RESERVED` until one matching terminal outcome is committed.",
    ),
    (
        "attempt_id",
        "durable",
        "Same fresh id supplied to the gate, `ShipConnection`, and terminal callbacks.",
    ),
    (
        "remote_ski_scope",
        "durable",
        "Exact opaque key and coordinator scope; never a public evidence value.",
    ),
    (
        "control_epoch",
        "durable",
        "Exact epoch at reservation linearization.",
    ),
    (
        "endpoint_path",
        "durable",
        "Private typed endpoint and path selected for the concrete dial.",
    ),
    (
        "reservation_order",
        "durable",
        "Monotonic coordinator sequence used as authoritative cross-event order.",
    ),
    (
        "reservation_timestamp",
        "durable_diagnostic",
        "Bounded injected-clock value used only to correlate test evidence, never for trust or deadlines.",
    ),
    (
        "attempt_count_before",
        "durable",
        "Exact unchanged count before this reservation.",
    ),
    (
        "attempt_context",
        "volatile",
        "Exact cancellable context keyed by attempt id; no context object or pointer is persisted.",
    ),
]

R2_RESERVATION_TRANSITIONS = [
    ("eligible_gate_entry", "RETRY_READY -> ATTEMPT_RESERVED", "zero_dials_before_commit"),
    (
        "reservation_commit_durable",
        "ATTEMPT_RESERVED -> ATTEMPT_RESERVED",
        "PERMIT_may_return",
    ),
    (
        "reservation_not_published",
        "RETRY_READY -> RETRY_READY",
        "DENY+zero_dials",
    ),
    (
        "reservation_durability_unknown",
        "ATTEMPT_RESERVED -> QUARANTINED",
        "DENY+zero_dials",
    ),
    (
        "matching_terminal_success",
        "ATTEMPT_RESERVED -> clear_reservation_without_failure_charge",
        "accept_only_if_epoch_and_tombstone_still_valid",
    ),
    (
        "matching_terminal_failure",
        "ATTEMPT_RESERVED -> BACKOFF_ACTIVE_or_ADMIN_HOLD",
        "charge_attempt_count_exactly_once",
    ),
    (
        "restart_with_unresolved_reservation",
        "ATTEMPT_RESERVED -> BACKOFF_ACTIVE_or_ADMIN_HOLD",
        "charge_once_before_any_new_dial",
    ),
    ("stale_terminal_callback", "no_state_change", "discard_without_charge_or_trust"),
]

R2_BRIDGE_ROWS = [
    (
        "helianthus_ship_go",
        "optional_OutgoingAttemptGate_at_every_concrete_dial",
        "protocol_or_handshake_semantic_change",
    ),
    (
        "helianthus_eebus_go",
        "configuration_bridge_exposes_gate_and_attempt_id",
        "SPINE_or_semantic_model_change",
    ),
    (
        "helianthus_eebusreg_internal",
        "coordinator_adapter+reservation+callback_validation",
        "fork_type_in_public_package",
    ),
    ("helianthus_eebusreg_public", "unchanged", "fork_import_or_new_public_surface"),
]

R2_RACE_ROWS = [
    (
        "revocation_before_reservation",
        "revocation_wins",
        "tombstone+DENY+zero_dials+unregister",
    ),
    (
        "revocation_after_reservation_before_dial",
        "revocation_wins",
        "cancel_exact_context+DENY+zero_dials+disconnect_observed+unregister",
    ),
    (
        "dial_launched_before_revocation",
        "attempt_launch_wins_then_revocation",
        "tombstone+cancel_exact_context+disconnect_observed+unregister+no_trust_accept",
    ),
    (
        "callback_after_tombstone",
        "revocation_already_won",
        "discard_stale_callback+no_state_change",
    ),
    (
        "withdrawal_failure_or_ambiguity",
        "revocation_nonterminal",
        "tombstone_effective+ADMIN_HOLD+no_success",
    ),
]

R2_MATRIX_ROWS = [
    (
        "denied_permit",
        "gate_returns_DENY",
        "zero_DialContext_calls+zero_accepts+zero_reannounce",
        "any_network_call_or_reannounce",
    ),
    (
        "reservation_publication_failure",
        "commit_not_published_or_unknown",
        "zero_DialContext_calls+DENY_or_quarantine",
        "permit_or_network_call",
    ),
    (
        "backoff_active",
        "persisted_BACKOFF_ACTIVE",
        "zero_DialContext_calls_before_durable_RETRY_READY",
        "early_network_call",
    ),
    (
        "quarantine_active",
        "persisted_QUARANTINED",
        "zero_DialContext_calls",
        "any_network_call",
    ),
    ("admin_hold", "persisted_ADMIN_HOLD", "zero_DialContext_calls", "any_network_call"),
    (
        "path_fallback",
        "primary_path_then_/ship_path",
        "PERMIT_count_equals_DialContext_count+distinct_attempt_ids",
        "ungated_fallback_or_count_mismatch",
    ),
    (
        "endpoint_fallback",
        "hostname_then_ipv4_then_ipv6",
        "PERMIT_count_equals_DialContext_count+exact_endpoint_binding",
        "ungated_retry_or_count_mismatch",
    ),
    (
        "mdns_storm",
        "concurrent_repeated_discovery_events",
        "per_SKI_serialization+denied_events_zero_dials+no_auto_reannounce",
        "parallel_unauthorized_dial_or_reannounce",
    ),
    (
        "crash_after_reservation",
        "crash_after_durable_ATTEMPT_RESERVED_before_dial",
        "restart_charges_once_before_zero_or_next_authorized_dial",
        "reservation_cleared_or_uncharged",
    ),
    (
        "delayed_callback",
        "old_attempt_callback_after_new_reservation",
        "stale_callback_discarded+active_reservation_unchanged",
        "old_callback_charges_clears_or_trusts",
    ),
    (
        "revocation_race",
        "revocation_at_each_launch_boundary",
        "one_linearized_order+exact_context_cancel+disconnect_observed+unregister",
        "post_tombstone_trust_or_success_before_withdrawal",
    ),
    (
        "fourth_failure_admin_hold",
        "four_matching_terminal_failures",
        "counts_1_2_3_4+fourth_enters_ADMIN_HOLD+zero_fifth_dial",
        "fifth_permit_or_dial",
    ),
    (
        "dial_accept_order",
        "one_permitted_fake_peer_connection",
        "reservation_commit_before_permit_before_DialContext_before_accept",
        "missing_or_reordered_observation",
    ),
    (
        "callback_injection_negative_control",
        "terminal_callback_without_dialer_or_accept_event",
        "not_pre_dial_evidence+case_FAIL",
        "case_PASS",
    ),
    (
        "race_detector",
        "all_cases_under_go_test_race",
        "zero_race_reports+deterministic_counts",
        "race_report_or_nondeterministic_result",
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
    require_equal(len(blocks), 4, "gate evidence block count")
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


def validate_r2_pending_evidence(body: str) -> None:
    rows = table_rows(body, "## R2 Dependency Evidence Status")
    evidence = [
        (code_value(row["Evidence field"]), code_value(row["Candidate value"]))
        for row in rows
    ]
    require_equal(evidence, R2_PENDING_EVIDENCE, "R2 pending evidence fields")
    blocks = section_blocks(body, "## R2 Dependency Evidence Status")
    require_equal(len(blocks), 3, "R2 pending evidence block count")
    require_markers(
        blocks[2],
        (
            "tag target, merge SHA, module graph, and CI head MUST agree",
            "without a `replace` directive",
            "may carry only `r2_platform_provider_attestation`",
            "cannot fill a fork, adoption, pre-dial artifact, or closure field",
        ),
        "R2 pending evidence closure policy",
    )


def validate_r2_fork_contract(body: str) -> None:
    rows = coded_rows(
        body,
        "## Dependency Fork Provenance And Release Policy",
        (
            "Stage",
            "Upstream baseline",
            "Canonical module",
            "Required provenance",
            "Release rule",
        ),
    )
    require_equal(rows, R2_FORK_STAGES, "R2 fork stages")
    blocks = section_blocks(body, "## Dependency Fork Provenance And Release Policy")
    require_equal(len(blocks), 5, "R2 fork policy block count")
    require_markers(
        " ".join(blocks[2:]),
        (
            "preserves every upstream license file, notice, and applicable source header",
            "a read-only `upstream` remote names the source project",
            "published fork tags are never retargeted",
            "`v0.6.1-helianthus.<positive_integer>`",
            "`v0.7.1-helianthus.<positive_integer>`",
            "A `replace` directive",
            "eebusreg adoption cannot merge before both fork tags exist",
        ),
        "R2 fork policy prose",
    )


def validate_r2_outgoing_gate_contract(body: str) -> None:
    schema = [
        (
            code_value(row["Gate field"]),
            code_value(row["Direction"]),
            row["Exact binding"],
        )
        for row in table_rows(body, "| Gate field | Direction | Exact binding |")
    ]
    require_equal(schema, R2_GATE_SCHEMA, "R2 outgoing gate schema")
    coverage = coded_rows(
        body,
        "### Dial Site Coverage",
        ("Dial variant", "Required gate placement", "Required cardinality"),
    )
    require_equal(coverage, R2_DIAL_COVERAGE, "R2 dial site coverage")
    blocks = section_blocks(body, "## Outgoing Attempt Gate And Dial Sites")
    require_equal(len(blocks), 6, "R2 outgoing gate block count")
    require_markers(
        " ".join((blocks[0], blocks[1], blocks[5])),
        (
            "optional, additive `OutgoingAttemptGate`",
            "install a non-nil gate before enabling listener, registration, discovery, or reconnect activity",
            "immediately before every concrete websocket `DialContext` call",
            "A `DENY` returns without invoking the concrete dialer",
            "zero network calls and no automatic reannounce for that attempt",
            "`PERMIT` decisions MUST equal the count of concrete `DialContext` calls",
        ),
        "R2 outgoing gate normative prose",
    )


def validate_r2_reservation_contract(body: str) -> None:
    fields = [
        (
            code_value(row["Reservation field"]),
            code_value(row["Storage"]),
            row["Exact rule"],
        )
        for row in table_rows(body, "| Reservation field | Storage | Exact rule |")
    ]
    require_equal(fields, R2_RESERVATION_FIELDS, "R2 reservation fields")
    transitions = coded_rows(
        body,
        "| Reservation event | Required durable transition | Dial/callback consequence |",
        ("Reservation event", "Required durable transition", "Dial/callback consequence"),
    )
    require_equal(transitions, R2_RESERVATION_TRANSITIONS, "R2 reservation transitions")
    blocks = section_blocks(body, "## Durable Outgoing Attempt Reservation")
    require_equal(len(blocks), 6, "R2 reservation block count")
    require_markers(
        " ".join((blocks[0], blocks[3], blocks[4], blocks[5])),
        (
            "`ATTEMPT_RESERVED` is a coordinator-owned durable state separate from `attempt_count`",
            "durable before `OutgoingAttemptGate` may return `PERMIT`",
            "attempt id is carried through `ShipConnection`",
            "unresolved `ATTEMPT_RESERVED` record is conservatively resolved as one failed attempt before listener setup",
            "fourth charged failure in the deterministic vector enters terminal `ADMIN_HOLD`",
            "Callback injection without those observations is not pre-dial evidence",
        ),
        "R2 reservation normative prose",
    )


def validate_r2_bridge_contract(body: str) -> None:
    rows = coded_rows(
        body,
        "## eebus-go Bridge And Type Boundary",
        ("Layer", "Required additive change", "Forbidden change"),
    )
    require_equal(rows, R2_BRIDGE_ROWS, "R2 bridge rows")
    blocks = section_blocks(body, "## eebus-go Bridge And Type Boundary")
    require_equal(len(blocks), 3, "R2 bridge block count")
    require_markers(
        " ".join(blocks[1:]),
        (
            "does not change SPINE models, feature discovery, semantic projection",
            "canonical module path and tag without `replace`",
            "Only an eebusreg internal adapter",
            "No exported declaration, public package field, method, alias, generic argument, error, or callback",
            "frozen public Go API and all protocol/API docs remain unchanged",
        ),
        "R2 bridge normative prose",
    )


def validate_r2_revocation_race_contract(body: str) -> None:
    rows = coded_rows(
        body,
        "## Revocation And Dial Race Linearization",
        ("Race order", "Linearization", "Required result"),
    )
    require_equal(rows, R2_RACE_ROWS, "R2 revocation race rows")
    blocks = section_blocks(body, "## Revocation And Dial Race Linearization")
    require_equal(len(blocks), 3, "R2 revocation race block count")
    require_markers(
        " ".join((blocks[0], blocks[2])),
        (
            "same per-SKI gate owned by the coordinator",
            "holds the per-SKI gate through reservation commit, permit, and the concrete dial-launch linearization point",
            "durably tombstones first, cancels the exact reserved context, observes transport disconnect",
            "`UnregisterRemoteSKI` before success",
            "No accept or terminal callback after the tombstone can make the association trusted",
        ),
        "R2 revocation race normative prose",
    )


def validate_r2_falsification_matrix(body: str) -> None:
    rows = coded_rows(
        body,
        "## R2 Pre-Dial Falsification Matrix",
        ("Case", "Fixture/action", "Required observation", "Falsifier"),
    )
    require_equal(rows, R2_MATRIX_ROWS, "R2 falsification matrix")
    blocks = section_blocks(body, "## R2 Pre-Dial Falsification Matrix")
    require_equal(len(blocks), 3, "R2 falsification matrix block count")
    require_markers(
        " ".join((blocks[0], blocks[2])),
        (
            "fake TLS endpoint",
            "fake peer on the SHIP path",
            "injectable websocket dialer",
            "direct callback invocation is used only as a negative control",
            "Equality of permit and `DialContext` counts is checked separately for path fallback, hostname retry, IPv4 retry, and IPv6 retry",
        ),
        "R2 falsification matrix prose",
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

    def test_r2_dependency_stages_and_pending_evidence_are_closed(self) -> None:
        _, body = read_markdown(CANDIDATE)
        validate_r2_pending_evidence(body)
        validate_r2_fork_contract(body)

    def test_r2_outgoing_gate_and_reservation_are_closed(self) -> None:
        _, body = read_markdown(CANDIDATE)
        validate_r2_outgoing_gate_contract(body)
        validate_r2_reservation_contract(body)

    def test_r2_bridge_revocation_race_and_matrix_are_closed(self) -> None:
        _, body = read_markdown(CANDIDATE)
        validate_r2_bridge_contract(body)
        validate_r2_revocation_race_contract(body)
        validate_r2_falsification_matrix(body)

    def test_r2_validators_reject_required_contract_mutations(self) -> None:
        _, body = read_markdown(CANDIDATE)
        mutations = (
            (
                "pending_fork_tag_filled_early",
                validate_r2_pending_evidence,
                "| `ship_go_prerelease_tag` | `pending` |",
                "| `ship_go_prerelease_tag` | `v0.6.1-helianthus.1` |",
            ),
            (
                "replace_directive_allowed",
                validate_r2_fork_contract,
                "A `replace` directive, local filesystem module override",
                "A reviewed `replace` directive or local filesystem module override",
            ),
            (
                "ship_go_upstream_baseline_changed",
                validate_r2_fork_contract,
                "| `ship_go_fork` | `github.com/enbility/ship-go@v0.6.0` |",
                "| `ship_go_fork` | `github.com/enbility/ship-go@v0.6.1` |",
            ),
            (
                "gate_moved_above_dial_site",
                validate_r2_outgoing_gate_contract,
                "| `ipv6_retry` | `immediately_before_DialContext` |",
                "| `ipv6_retry` | `once_per_remote` |",
            ),
            (
                "gate_ambiguity_permitted",
                validate_r2_outgoing_gate_contract,
                "absence, error, panic, or ambiguity is `DENY`",
                "absence, error, panic, or ambiguity may be `PERMIT`",
            ),
            (
                "attempt_context_not_cancellable",
                validate_r2_outgoing_gate_contract,
                "Exact per-attempt cancellable context retained by the coordinator",
                "Per-remote context retained by the coordinator",
            ),
            (
                "denial_may_dial",
                validate_r2_outgoing_gate_contract,
                "A `DENY` returns without invoking the concrete dialer.",
                "A `DENY` may invoke the concrete dialer.",
            ),
            (
                "reservation_charges_on_entry",
                validate_r2_reservation_contract,
                "| `eligible_gate_entry` | `RETRY_READY -> ATTEMPT_RESERVED` | "
                "`zero_dials_before_commit` |",
                "| `eligible_gate_entry` | `RETRY_READY -> BACKOFF_ACTIVE` | "
                "`dial_may_start` |",
            ),
            (
                "restart_drops_reservation",
                validate_r2_reservation_contract,
                "| `restart_with_unresolved_reservation` | "
                "`ATTEMPT_RESERVED -> BACKOFF_ACTIVE_or_ADMIN_HOLD` | "
                "`charge_once_before_any_new_dial` |",
                "| `restart_with_unresolved_reservation` | `no_state_change` | "
                "`clear_without_charge` |",
            ),
            (
                "stale_callback_clears_active",
                validate_r2_reservation_contract,
                "| `stale_terminal_callback` | `no_state_change` | "
                "`discard_without_charge_or_trust` |",
                "| `stale_terminal_callback` | `clear_reservation` | `accept_trust` |",
            ),
            (
                "reservation_count_not_separate",
                validate_r2_reservation_contract,
                "Exact unchanged count before this reservation.",
                "Count incremented when this reservation is entered.",
            ),
            (
                "bridge_changes_spine",
                validate_r2_bridge_contract,
                "| `helianthus_eebus_go` | "
                "`configuration_bridge_exposes_gate_and_attempt_id` | "
                "`SPINE_or_semantic_model_change` |",
                "| `helianthus_eebus_go` | `bridge_and_SPINE_change` | `none` |",
            ),
            (
                "fork_type_leaks_publicly",
                validate_r2_bridge_contract,
                "| `helianthus_eebusreg_public` | `unchanged` | "
                "`fork_import_or_new_public_surface` |",
                "| `helianthus_eebusreg_public` | `exports_fork_gate` | `none` |",
            ),
            (
                "revocation_skips_context_cancel",
                validate_r2_revocation_race_contract,
                "`cancel_exact_context+DENY+zero_dials+disconnect_observed+unregister`",
                "`DENY+zero_dials+unregister`",
            ),
            (
                "callback_injection_passes",
                validate_r2_falsification_matrix,
                "| `callback_injection_negative_control` | "
                "`terminal_callback_without_dialer_or_accept_event` | "
                "`not_pre_dial_evidence+case_FAIL` | `case_PASS` |",
                "| `callback_injection_negative_control` | `terminal_callback_only` | "
                "`case_PASS` | `none` |",
            ),
            (
                "quarantine_may_dial",
                validate_r2_falsification_matrix,
                "| `quarantine_active` | `persisted_QUARANTINED` | "
                "`zero_DialContext_calls` | `any_network_call` |",
                "| `quarantine_active` | `persisted_QUARANTINED` | "
                "`one_DialContext_call` | `none` |",
            ),
            (
                "race_detector_removed",
                validate_r2_falsification_matrix,
                "| `race_detector` | `all_cases_under_go_test_race` |",
                "| `race_detector` | `all_cases_without_race_detector` |",
            ),
        )
        for label, validator, old, new in mutations:
            with self.subTest(label=label):
                mutated = mutate_normalized_once(body, old, new)
                with self.assertRaises(AssertionError):
                    validator(mutated)

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
            (
                "g10_r2_pass",
                "with zero dials for denial, publication failure, backoff, "
                "quarantine, and terminal hold",
                "with caller-asserted zero dials",
            ),
            (
                "g10_r2_fail",
                "treats callback injection as pre-dial evidence",
                "accepts callback injection as pre-dial evidence",
            ),
            (
                "g11_r2_pass",
                "across path fallback, hostname/IPv4/IPv6 retry, crash recovery, "
                "delayed callback, discovery storm, and revocation race",
                "across one helper callback",
            ),
            (
                "g11_r2_fail",
                "injected callbacks pass without dial/accept observations",
                "injected callbacks pass with no observations",
            ),
            (
                "g16_r2_pass",
                "R2 binds a redacted durable reservation timestamp/order and "
                "synthetic attempt id",
                "R2 records a caller-asserted attempt",
            ),
            (
                "g16_r2_fail",
                "callback-only evidence is accepted without the "
                "reservation/dial/accept binding",
                "callback-only evidence is accepted as sufficient",
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

    def test_msp045_validator_rejects_weakened_r2_entry_boundary(self) -> None:
        _, body = read_markdown(CANDIDATE)
        boundary = (
            "Carried evidence is limited to the explicit SSH-only "
            "provider-attestation limitation. A dependency fork, module graph, "
            "pre-dial runtime composition, reservation, revocation race, or gate "
            "failure cannot be carried."
        )
        mutations = (
            (
                "additional_provider_evidence",
                boundary,
                "Carried evidence may include the SSH-only provider-attestation "
                "limitation and other provider limitations. A dependency fork, "
                "module graph, pre-dial runtime composition, reservation, "
                "revocation race, or gate failure cannot be carried.",
            ),
            (
                "runtime_composition_carried",
                boundary,
                "Carried evidence is limited to the explicit SSH-only "
                "provider-attestation limitation, but pre-dial runtime composition "
                "and reservation failures may also be carried.",
            ),
            (
                "gate_failure_carried",
                boundary,
                "Carried evidence is limited to the explicit SSH-only "
                "provider-attestation limitation, but revocation races and gate "
                "failures may also be carried.",
            ),
            (
                "adoption_stage_not_required",
                "| `required_repo_stages` | "
                "`ship_go_fork+eebus_go_bridge+eebusreg_adoption` |",
                "| `required_repo_stages` | "
                "`ship_go_fork+eebus_go_bridge` |",
            ),
            (
                "closure_accepts_any_carried_failure",
                "| `closure_verdict` | `PASS_or_SSH_ONLY_CARRIED` |",
                "| `closure_verdict` | `PASS_or_ANY_CARRIED` |",
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
