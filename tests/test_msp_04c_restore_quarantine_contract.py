from __future__ import annotations

import hashlib
import json
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
SHIP_TAG_OBJECT = "c2b94943a0106e90f603" + "a2ee0e155c1f6ac0b54b"
SHIP_COMMIT = "760c312bf723d726d888" + "2af3bb06650ddcd11ca9"
SHIP_TREE = "958ddf185fc09dd4d3b3" + "82fc108641513412d927"
SHIP_LICENSE_SHA256 = (
    "c853996135802c50b3048937e48022bc" + "00b41ff5f56a31cebe7d686bf91f87db"
)
EEBUS_TAG_OBJECT = "e4677eb9c46f1cc46c25" + "59027c35fbf39766bcfb"
EEBUS_COMMIT = "99f07ff79819b728dd2f" + "e37472c4a26865d8076c"
EEBUS_TREE = "fee9de0ecb34dcb7c416" + "5922fd49fedd42d8df23"
EEBUS_LICENSE_SHA256 = (
    "0871acb60d194272cd91ad02dcaf0102" + "d8047a993f1b00973da4c9c2cba845a4"
)
PUBLIC_API_SOURCE = "59cbea0593f27caf558b" + "c4cc9b665c52fc50b683"
PUBLIC_API_SHA256 = (
    "c93492bd275b5e14d3c9e05da701730d" + "6d34a197e0653e6b169d103418bfcc8c"
)


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


def machine_yaml(body: str, heading: str) -> dict[str, object]:
    section = body.split(heading, 1)[1].split("\n## ", 1)[0]
    matches = re.findall(r"```yaml\n(.*?)\n```", section, flags=re.DOTALL)
    if len(matches) != 1:
        raise AssertionError(f"{heading} must contain exactly one YAML object")
    value = yaml.safe_load(matches[0])
    if not isinstance(value, dict):
        raise AssertionError(f"{heading} YAML must be an object")
    return value


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
        "durable reservation and launch order",
        "actual exact-context `DialContext` and fake-peer accept observations",
        "zero calls for pre-launch denial, publication failure, backoff, quarantine, "
        "and terminal hold",
    ),
    ("EEBUS-G10", "Deterministic FAIL"): (
        "invokes `RegisterRemoteSKI`",
        "relies only on a helper-returned decision",
        "reaches a dial before durable reservation and launch permit",
        "bypasses the fresh IPv6 lease",
        "treats callback injection as pre-dial evidence",
    ),
    ("EEBUS-G11", "Deterministic PASS"): (
        "Executed integration behavior drives the real pairing callback",
        "specified durable checkpoint and monotonic restart arm",
        "terminal `ADMIN_HOLD`",
        "reservation, handle, launch authorization, exact context",
        "selected-path and root/no-path fallback, hostname/IPv4/IPv6 retry",
    ),
    ("EEBUS-G11", "Deterministic FAIL"): (
        "The real callback bypasses failure recording or checkpointing",
        "the ceiling admits another handshake/reconnect",
        "unresolved reservation restart clears without one synthetic failure charge",
        "permit count differs from `DialContext` count outside the explicit process-termination gap",
        "canceled-context call uses another context",
        "injected callbacks pass without dial/accept observations",
    ),
    ("EEBUS-G16", "Deterministic PASS"): (
        "Publishable integration artifacts",
        "private input/store root may contain generated synthetic SKI",
        "Canary scans over captured callbacks, effects, logs, errors",
        "redacted reservation/launch ordering and ordinal attempt labels",
    ),
    ("EEBUS-G16", "Deterministic FAIL"): (
        "frozen API diff changes",
        "scan input omits an output surface",
        "residual direct `Dial` or extra `DialContext` remains",
        "callback-only evidence is accepted without the reservation/launch/dial/accept binding",
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
        "Each G10, G11, and G16 PASS row independently requires the same privately "
        "observed attempt-bound chain: durable reservation order, handle return, "
        "durable launch authorization, single-use permit, exact-context "
        "`DialContext`, and fake-peer accept when the peer accepts. Callback "
        "injection is not pre-dial evidence and cannot satisfy any one of the "
        "three rows. Public output replaces the actual attempt id and private "
        "values with independent ordinal labels."
    ),
    (
        "The compact public artifact identifies `MSP-04C`, exact commit and "
        "commands, marks topology and credentials `not_applicable_synthetic`, "
        "marks temporary paths `redacted`, and includes one PASS/FAIL row per "
        "required case. Raw store, anchor, admin frames, transcripts, private "
        "generated inputs, and fixture internals are never published. Case "
        "ordering and output bytes are "
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
    (
        "ship_go_upstream_tag_object_sha",
        "machine.baselines.ship_go.tag_object.oid",
    ),
    (
        "ship_go_upstream_peeled_commit_sha",
        "machine.baselines.ship_go.peeled_commit.commit",
    ),
    ("ship_go_upstream_tree_sha", "machine.baselines.ship_go.tree.oid"),
    (
        "ship_go_upstream_license_sha256",
        "machine.baselines.ship_go.license.sha256",
    ),
    (
        "eebus_go_upstream_tag_object_sha",
        "machine.baselines.eebus_go.tag_object.oid",
    ),
    (
        "eebus_go_upstream_peeled_commit_sha",
        "machine.baselines.eebus_go.peeled_commit.commit",
    ),
    ("eebus_go_upstream_tree_sha", "machine.baselines.eebus_go.tree.oid"),
    (
        "eebus_go_upstream_license_sha256",
        "machine.baselines.eebus_go.license.sha256",
    ),
    (
        "eebusreg_public_api_baseline_source_sha",
        "machine.baselines.eebusreg_public_api.source_sha",
    ),
    (
        "eebusreg_published_api_manifest_sha256",
        "machine.baselines.eebusreg_public_api.manifest.sha256",
    ),
    ("ship_go_fork_head_sha", "pending"),
    ("ship_go_fork_merge_sha", "pending"),
    ("ship_go_prerelease_tag", "pending"),
    ("ship_go_prerelease_tag_object_sha", "pending"),
    ("ship_go_prerelease_peeled_commit_sha", "pending"),
    ("ship_go_license_provenance_manifest_sha256", "pending"),
    ("ship_go_module_graph_sha256", "pending"),
    ("ship_go_exact_head_ci_run", "pending"),
    ("ship_go_post_merge_ci_run", "pending"),
    ("eebus_go_fork_head_sha", "pending"),
    ("eebus_go_fork_merge_sha", "pending"),
    ("eebus_go_prerelease_tag", "pending"),
    ("eebus_go_prerelease_tag_object_sha", "pending"),
    ("eebus_go_prerelease_peeled_commit_sha", "pending"),
    ("eebus_go_license_provenance_manifest_sha256", "pending"),
    ("eebus_go_module_graph_sha256", "pending"),
    ("eebus_go_exact_head_ci_run", "pending"),
    ("eebus_go_post_merge_ci_run", "pending"),
    ("eebusreg_adoption_head_sha", "pending"),
    ("eebusreg_adoption_merge_sha", "pending"),
    ("eebusreg_adoption_module_graph_sha256", "pending"),
    ("eebusreg_adoption_api_manifest_sha256", "pending"),
    ("eebusreg_public_api_comparison", "pending"),
    ("eebusreg_adoption_exact_head_ci_run", "pending"),
    ("eebusreg_adoption_post_merge_ci_run", "pending"),
    ("eebus_g10_predial_artifact", "pending"),
    ("eebus_g11_predial_artifact", "pending"),
    ("eebus_g16_predial_artifact", "pending"),
    ("m4_r2_architecture_closure_verdict", "pending"),
    ("r2_platform_provider_attestation", "pending_ssh_only_non_normative"),
    ("upstream_neutral_proposal_evidence_pack", "pending_nonblocking_post_M4"),
    ("ship_go_upstream_discussion_url_status", "pending_nonblocking_post_M4"),
    (
        "ship_go_upstream_issue_or_draft_pr_url_status",
        "pending_nonblocking_post_M4",
    ),
    ("ship_go_upstream_release_tag", "pending_nonblocking_post_M4"),
    ("eebus_go_upstream_discussion_url_status", "pending_nonblocking_post_M4"),
    (
        "eebus_go_upstream_issue_or_draft_pr_url_status",
        "pending_nonblocking_post_M4",
    ),
    ("eebus_go_upstream_release_tag", "pending_nonblocking_post_M4"),
    ("final_repatriation_evidence", "pending_nonblocking_post_M4"),
]

R2_FORK_STAGES = [
    (
        "ship_go_fork",
        "github.com/enbility/ship-go@v0.6.0^{commit}",
        "github.com/Project-Helianthus/helianthus-ship-go",
        "tag_object+peeled_commit+tree+license_provenance_digest",
        "reviewed_semver_prerelease",
    ),
    (
        "eebus_go_fork",
        "github.com/enbility/eebus-go@v0.7.0^{commit}",
        "github.com/Project-Helianthus/helianthus-eebus-go",
        "tag_object+peeled_commit+tree+license_provenance_digest",
        "reviewed_semver_prerelease",
    ),
    (
        "eebusreg_adoption",
        (
            "Project-Helianthus/helianthus-eebusreg@"
            "machine.baselines.eebusreg_public_api.source_sha"
        ),
        "internal_bridge_only",
        "exact_peeled_fork_commits+module_graph+api_manifest_comparison",
        "merge_after_both_fork_tags",
    ),
]

R2_GATE_SCHEMA = [
    (
        "remote_ski",
        "Prepare",
        "input",
        "Exact opaque remote key for the selected association; never logged or published.",
    ),
    (
        "endpoint",
        "Prepare",
        "input",
        "Exact selected hostname, IPv4, or IPv6 endpoint plus port in private typed form.",
    ),
    (
        "path",
        "Prepare",
        "input",
        "Exact selected websocket path, including root/no-path fallback when chosen.",
    ),
    (
        "attempt_id",
        "Prepare",
        "output_handle",
        "Fresh bounded coordinator id, unique within the current store instance and control epoch.",
    ),
    (
        "scope",
        "Prepare",
        "output_handle",
        "Exact coordinator retry/quarantine scope allocated for this concrete attempt.",
    ),
    (
        "control_epoch",
        "Prepare",
        "output_handle",
        "Exact epoch committed by the durable reservation.",
    ),
    (
        "attempt_context",
        "Prepare",
        "output_handle",
        "Exact per-attempt cancellable context retained by the coordinator until terminal resolution.",
    ),
    (
        "attempt_handle",
        "Prepare",
        "output",
        "Opaque single-owner lease containing exactly the four output-handle fields.",
    ),
    (
        "attempt_handle",
        "AuthorizeLaunch",
        "input",
        "Exact unconsumed handle returned by `Prepare`; copying does not create another use.",
    ),
    (
        "permit",
        "AuthorizeLaunch",
        "output",
        "Exactly `PERMIT` or `DENY`; absence, error, panic, stale handle, or ambiguity is `DENY`.",
    ),
    (
        "reason",
        "AuthorizeLaunch",
        "output",
        "One stable closed permit/deny reason with no endpoint, key, path, context, or private error text.",
    ),
]

R2_DIAL_COVERAGE = [
    (
        "selected_endpoint_selected_path",
        "Prepare_then_AuthorizeLaunch_immediately_before_DialContext",
        "one_fresh_lease+one_single_use_PERMIT+one_DialContext_call",
    ),
    (
        "same_endpoint_root_no_path_fallback",
        "Prepare_then_AuthorizeLaunch_immediately_before_DialContext",
        "one_new_lease+one_new_single_use_PERMIT+one_DialContext_call",
    ),
    (
        "hostname_retry",
        "Prepare_then_AuthorizeLaunch_immediately_before_DialContext",
        "one_new_lease+one_new_single_use_PERMIT+one_DialContext_call",
    ),
    (
        "ipv4_retry",
        "Prepare_then_AuthorizeLaunch_immediately_before_DialContext",
        "one_new_lease+one_new_single_use_PERMIT+one_DialContext_call",
    ),
    (
        "ipv6_retry",
        "Prepare_then_AuthorizeLaunch_immediately_before_DialContext",
        "one_new_lease+one_new_single_use_PERMIT+one_DialContext_call",
    ),
]

R2_RESERVATION_FIELDS = [
    (
        "state",
        "durable",
        "Exactly `ATTEMPT_RESERVED` or `ATTEMPT_LAUNCH_AUTHORIZED` until one matching terminal outcome is committed.",
    ),
    (
        "attempt_id",
        "durable",
        "Same fresh id returned in the handle and carried through `ShipConnection` and terminal callbacks.",
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
    (
        "lease_state",
        "volatile",
        "Exactly `fresh`, `consumed`, or `expired`; at most one active handle exists per scope.",
    ),
    (
        "lease_deadline",
        "volatile",
        "Bounded injected-monotonic deadline; expiry resolves as one synthetic failure, never silent clear.",
    ),
]

R2_RESERVATION_TRANSITIONS = [
    (
        "prepare_eligible",
        "RETRY_READY -> ATTEMPT_RESERVED",
        "zero_DialContext_calls_before_commit",
    ),
    (
        "prepare_commit_durable",
        "ATTEMPT_RESERVED -> ATTEMPT_RESERVED",
        "handle_may_return",
    ),
    (
        "prepare_not_published",
        "RETRY_READY -> RETRY_READY",
        "no_handle+zero_DialContext_calls",
    ),
    (
        "prepare_durability_unknown",
        "ATTEMPT_RESERVED -> QUARANTINED",
        "no_handle+zero_DialContext_calls",
    ),
    (
        "authorize_launch_matching",
        "ATTEMPT_RESERVED -> ATTEMPT_LAUNCH_AUTHORIZED",
        "single_use_PERMIT_is_launch_linearization",
    ),
    (
        "authorize_stale_consumed_or_mismatched",
        "no_state_change",
        "DENY+zero_DialContext_calls_for_that_handle",
    ),
    (
        "permit_context_already_canceled",
        "ATTEMPT_LAUNCH_AUTHORIZED -> ATTEMPT_LAUNCH_AUTHORIZED",
        "one_DialContext_call+zero_network_effect",
    ),
    (
        "matching_terminal_success",
        "active_attempt -> clear_reservation_without_failure_charge",
        "accept_only_if_epoch_and_tombstone_still_valid",
    ),
    (
        "matching_terminal_failure",
        "active_attempt -> BACKOFF_ACTIVE_or_ADMIN_HOLD",
        "charge_attempt_count_exactly_once",
    ),
    (
        "matching_abort_or_lease_expiry",
        "active_attempt -> BACKOFF_ACTIVE_or_ADMIN_HOLD",
        "synthetic_failure_charge_exactly_once",
    ),
    (
        "restart_with_unresolved_reservation",
        "active_attempt -> BACKOFF_ACTIVE_or_ADMIN_HOLD",
        "synthetic_failure_linearization+charge_exactly_once_before_runtime",
    ),
    (
        "durable_retry_ready",
        "BACKOFF_ACTIVE -> RETRY_READY",
        "no_new_Prepare_before_commit",
    ),
    (
        "matching_revocation",
        "active_attempt -> tombstone+clear_reservation",
        "atomic_no_failure_charge+DENY_or_cancel",
    ),
    ("stale_terminal_callback", "no_state_change", "discard_without_charge_or_trust"),
]

R2_BRIDGE_ROWS = [
    (
        "helianthus_ship_go",
        "optional_Prepare+AuthorizeLaunch+one_gatedDialContext_helper",
        "protocol_or_handshake_semantic_change",
    ),
    (
        "helianthus_eebus_go",
        "configuration_bridge_carries_attempt_handle_and_id",
        "SPINE_or_semantic_model_change",
    ),
    (
        "helianthus_eebusreg_internal",
        "coordinator_adapter+attempt_journal+callback_validation",
        "fork_type_in_public_package",
    ),
    ("helianthus_eebusreg_public", "unchanged", "fork_import_or_new_public_surface"),
]

R2_RACE_ROWS = [
    (
        "revocation_before_prepare",
        "revocation_wins",
        "tombstone+no_handle+zero_DialContext_calls+unregister",
    ),
    (
        "revocation_after_prepare_before_authorize",
        "matching_revocation_wins",
        "atomic_tombstone+clear_reservation+no_failure_charge+DENY+zero_DialContext_calls",
    ),
    (
        "revocation_after_authorize_before_DialContext",
        "launch_wins_then_revocation",
        "atomic_tombstone+clear_reservation+no_failure_charge+cancel_exact_context+one_canceled_DialContext_call+zero_network_effect+unregister",
    ),
    (
        "DialContext_invoked_before_revocation",
        "launch_wins_then_revocation",
        "atomic_tombstone+clear_reservation+no_failure_charge+cancel_exact_context+disconnect_observed+unregister+no_trust_accept",
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
        "denied_prepare",
        "Prepare_returns_no_handle",
        "zero_DialContext_calls+zero_accepts+zero_reannounce",
        "any_DialContext_call_or_reannounce",
    ),
    (
        "denied_authorize",
        "AuthorizeLaunch_returns_DENY",
        "zero_DialContext_calls_for_handle+zero_accepts",
        "DialContext_call_for_denied_handle",
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
        "selected_path_then_root_no_path",
        "fresh_lease_and_PERMIT_each+PERMIT_count_equals_DialContext_count",
        "changed_fallback_semantics_or_reused_handle_or_count_mismatch",
    ),
    (
        "endpoint_fallback",
        "hostname_then_ipv4_then_ipv6",
        "fresh_lease_and_PERMIT_each+exact_endpoint_binding",
        "ungated_or_reused_hostname_IPv4_IPv6_attempt",
    ),
    (
        "canceled_context_after_permit",
        "revocation_cancels_exact_context_before_call",
        "one_DialContext_call_with_same_canceled_context+zero_network_effect",
        "skipped_call_or_unrelated_context_or_network_effect",
    ),
    (
        "mdns_storm",
        "concurrent_repeated_discovery_events",
        "per_SKI_serialization+denied_events_zero_dials+no_auto_reannounce",
        "parallel_unauthorized_dial_or_reannounce",
    ),
    (
        "crash_after_reservation",
        "crash_after_durable_ATTEMPT_RESERVED_before_authorize",
        "restart_synthetic_failure_charges_once_before_runtime",
        "reservation_cleared_or_uncharged_or_double_charged",
    ),
    (
        "crash_after_launch_authorization",
        "crash_after_PERMIT_before_DialContext",
        "restart_synthetic_failure_charges_once+explicit_gap_observation",
        "hidden_permit_bypass_or_clear_without_charge",
    ),
    (
        "abort_expiry_panic",
        "abort+lease_expiry+panic_at_each_boundary",
        "bounded_one_active_reservation+one_synthetic_failure_or_existing_terminal",
        "leak_or_double_charge_or_stale_handle_permit",
    ),
    (
        "delayed_callback",
        "old_attempt_callback_after_new_reservation",
        "stale_callback_discarded+active_reservation_unchanged",
        "old_callback_charges_clears_or_trusts",
    ),
    (
        "matching_revocation_crash_boundaries",
        "crash_before_stage+after_stage+after_target+after_finalize",
        "ordinary_recovery_before_stage+otherwise_tombstone_and_clear_without_charge_once",
        "post_stage_failure_charge_or_missing_tombstone_or_double_terminal",
    ),
    (
        "revocation_race",
        "revocation_at_each_Prepare_Authorize_DialContext_boundary",
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
        "reservation_commit_before_handle_before_launch_commit_before_permit_before_DialContext_before_accept",
        "missing_or_reordered_observation",
    ),
    (
        "ship_go_AST_inventory",
        "scan_fixed_fork_source",
        "zero_direct_Dial+one_DialContext_in_gatedDialContext_only",
        "residual_Dial_or_other_DialContext_or_hidden_alias",
    ),
    (
        "private_public_split",
        "generated_private_inputs_then_G16_collection",
        "private_root_only+zero_canary_matches_in_all_public_surfaces+deletion_verified",
        "private_value_in_log_error_panic_artifact_diff_evidence_or_public_output",
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

R2_BASELINE_INVENTORY = [
    (
        "selected_path_call",
        "hub/hub_connections.go:websocket.Dial(selected_path)",
        "fresh_Prepare+fresh_AuthorizeLaunch+gatedDialContext",
    ),
    (
        "root_no_path_fallback_call",
        "hub/hub_connections.go:websocket.Dial(root_no_path)",
        "fresh_Prepare+fresh_AuthorizeLaunch+gatedDialContext",
    ),
    ("direct_websocket_Dial_calls", "2", "0"),
    ("direct_DialContext_calls", "0", "1_in_gatedDialContext_only"),
    (
        "fallback_semantics",
        "selected_path_then_root_no_path_on_same_error_condition",
        "preserved_exactly",
    ),
]

R2_FORK_LIFECYCLE = [
    (
        "1_m4_proof",
        "stabilize_on_VR940f+G10_G11_G16+M4_PASS",
        "current_execution",
        "required",
    ),
    (
        "2_proposal_pack",
        "publish_upstream_neutral_optional_gate_test_seam_evidence",
        "M4_PASS",
        "no_post_M4",
    ),
    (
        "3_ship_discussion",
        "open_ship_go_GitHub_Discussion+obtain_positive_feedback",
        "proposal_pack_ready",
        "no_post_M4",
    ),
    (
        "4_ship_issue_or_draft_pr",
        "open_accepted_issue_or_draft_PR",
        "ship_positive_feedback",
        "no_post_M4",
    ),
    (
        "5_ship_release",
        "obtain_tagged_upstream_release_with_equivalent_behavior",
        "ship_change_accepted_and_merged",
        "no_post_M4",
    ),
    (
        "6_eebus_discussion",
        "open_eebus_go_GitHub_Discussion+obtain_positive_feedback",
        "ship_tagged_release",
        "no_post_M4",
    ),
    (
        "7_eebus_issue_or_draft_pr",
        "open_accepted_issue_or_draft_PR_for_configuration_bridge",
        "eebus_positive_feedback",
        "no_post_M4",
    ),
    (
        "8_eebus_release",
        "obtain_tagged_upstream_release_with_equivalent_behavior",
        "eebus_change_accepted_and_merged",
        "no_post_M4",
    ),
    (
        "9_repatriation",
        "migrate_to_github.com/enbility_modules+rerun_exit_gates+archive_forks_read_only",
        "both_tagged_upstream_releases",
        "no_post_M4",
    ),
]

R2_OPERATION_CLASSES = [
    ("first_trust", "publish_trusted_association", "not_applicable"),
    (
        "revoke_association",
        "publish_tombstone+deactivate_association",
        "no_attempt_charge",
    ),
    (
        "repair_publish_inactive_parent",
        "publish_fresh_untrusted_lineage",
        "not_applicable",
    ),
    (
        "repair_adopt_copied_current",
        "publish_fresh_untrusted_lineage",
        "not_applicable",
    ),
    (
        "repair_recover_unavailable_host_key",
        "publish_fresh_untrusted_lineage",
        "not_applicable",
    ),
    (
        "repair_release_retry_quarantine",
        "publish_retry_ready",
        "no_attempt_charge",
    ),
    ("attempt_prepare", "RETRY_READY_to_ATTEMPT_RESERVED", "no_attempt_charge"),
    (
        "attempt_authorize_launch",
        "ATTEMPT_RESERVED_to_ATTEMPT_LAUNCH_AUTHORIZED",
        "no_attempt_charge",
    ),
    ("attempt_terminal_success", "clear_matching_reservation", "no_attempt_charge"),
    (
        "attempt_terminal_failure",
        "clear_matching_reservation+publish_backoff_or_hold",
        "charge_exactly_once",
    ),
    (
        "attempt_abort_synthetic_failure",
        "clear_matching_reservation+publish_backoff_or_hold",
        "charge_exactly_once",
    ),
    (
        "attempt_restart_synthetic_failure",
        "clear_unresolved_reservation+publish_backoff_or_hold",
        "charge_exactly_once",
    ),
    ("attempt_retry_ready", "BACKOFF_ACTIVE_to_RETRY_READY", "no_attempt_charge"),
    (
        "attempt_matching_revocation",
        "publish_tombstone+deactivate_association+clear_matching_reservation",
        "no_attempt_charge",
    ),
]

R2_ATTEMPT_RECONCILIATION = [
    (
        "attempt_class+exact_target_selected",
        "compare_and_finalize(exact_descriptor)",
        "target_transition_terminal_once",
    ),
    (
        "attempt_class+exact_previous_selected_and_target_absent",
        "compare_and_clear(exact_descriptor)",
        "previous_state_retained+operation_may_be_reissued_once",
    ),
    (
        "attempt_matching_revocation+exact_previous_selected_and_target_absent",
        "retry_exact_target_commit_without_clear_then_finalize",
        "tombstone_and_clear_reservation_without_charge",
    ),
    (
        "attempt_class+same_number_different_digest_or_reference",
        "none",
        "DURABILITY_UNKNOWN/QUARANTINED",
    ),
    (
        "attempt_class+other_or_ambiguous",
        "none",
        "DURABILITY_UNKNOWN/QUARANTINED",
    ),
]

R2_PRIVACY_ROWS = [
    (
        "private_generated_test_input",
        "synthetic_private_key+certificate+SKI+SHIP_ID+endpoint+IP+port+selected_path+root_fallback_path",
        "isolated_ephemeral_input_root_only",
    ),
    (
        "private_generated_store",
        "raw_store+anchor+attempt_endpoint_path+opaque_association",
        "isolated_ephemeral_store_root_only",
    ),
    (
        "publishable_G16_output",
        "repo+branch+commit+issue+tool_versions+redacted_commands+per_run_ordinal_labels+stable_enums+bounded_counts_durations+PASS_FAIL",
        "public_output_root_only",
    ),
]

FORBIDDEN_R2_CONTRADICTIONS = (
    "IPv6 retry may bypass Prepare and AuthorizeLaunch.",
    "Restart may clear an unresolved reservation without a failure charge.",
    "DialContext may use an unrelated context.",
    "An untagged pseudo-version is allowed.",
    "Residual direct Dial calls are allowed.",
    "Private fixture data may appear in logs or public evidence.",
    "The Project-Helianthus forks are permanent product forks.",
    "Current M4 closure must wait for upstream maintainer approval.",
    "The forks are deleted on retirement.",
)

R2_MACHINE_CONTRACT = {
    "schema_id": "helianthus.docs.eebus.msp-04c-r2",
    "schema_version": 1,
    "baselines": {
        "ship_go": {
            "tag": "v0.6.0",
            "tag_object": {"oid": SHIP_TAG_OBJECT},
            "peeled_commit": {"commit": SHIP_COMMIT},
            "tree": {"oid": SHIP_TREE},
            "license": {"sha256": SHIP_LICENSE_SHA256},
        },
        "eebus_go": {
            "tag": "v0.7.0",
            "tag_object": {"oid": EEBUS_TAG_OBJECT},
            "peeled_commit": {"commit": EEBUS_COMMIT},
            "tree": {"oid": EEBUS_TREE},
            "license": {"sha256": EEBUS_LICENSE_SHA256},
        },
        "eebusreg_public_api": {
            "source_sha": PUBLIC_API_SOURCE,
            "manifest": {
                "path": "api/eebusruntime-v1/manifest.json",
                "sha256": PUBLIC_API_SHA256,
            },
        },
    },
    "dependency_policy": {
        "required_version": "reviewed_semver_prerelease",
        "forbidden_versions": [
            "replace",
            "local_override",
            "pseudo_version",
            "branch",
            "upstream_module_return",
        ],
        "closure_bindings": [
            "annotated_tag_object",
            "peeled_commit",
            "tree",
            "license_provenance_digest",
            "module_graph_digest",
            "exact_source_ci",
            "public_api_manifest_comparison",
        ],
    },
    "fork_lifecycle": {
        "classification": "temporary_downstream_patch_carriers",
        "current_m4_upstream_dependency": "nonblocking",
        "divergence": "minimal_gate_and_bridge_only",
        "unrelated_features": "forbidden",
        "sequence": [
            "m4_vr940f_proof_and_PASS",
            "upstream_neutral_proposal_evidence_pack",
            "ship_go_Discussion_positive_feedback",
            "ship_go_accepted_issue_or_draft_PR",
            "ship_go_tagged_release",
            "eebus_go_Discussion_positive_feedback",
            "eebus_go_accepted_issue_or_draft_PR",
            "eebus_go_tagged_release",
            "repatriation_gate",
        ],
        "repatriation": {
            "module_paths": "github.com/enbility",
            "replace_directives": "zero",
            "rerun_gates": [
                "G10",
                "G11",
                "G16",
                "public_API_anti_leak",
                "coexistence",
            ],
            "retirement": "archive_read_only_never_delete",
        },
    },
    "ship_go_dial_inventory": {
        "baseline_file": "hub/hub_connections.go",
        "baseline_direct_Dial_calls": 2,
        "baseline_order": ["selected_path", "root_no_path_fallback"],
        "fork_direct_Dial_calls": 0,
        "fork_direct_DialContext_calls": 1,
        "allowed_DialContext_owner": "gatedDialContext",
        "fallback_semantics": "preserve_exactly",
        "fresh_attempts": [
            "selected_path",
            "root_no_path_fallback",
            "hostname",
            "ipv4",
            "ipv6",
        ],
    },
    "attempt_contract": {
        "prepare": {
            "request": ["remote_ski", "endpoint", "path"],
            "durable_transition": "RETRY_READY_to_ATTEMPT_RESERVED",
            "handle_fields": [
                "attempt_id",
                "scope",
                "control_epoch",
                "attempt_context",
            ],
            "return_only_after": "durable_reservation_and_anchor_finalize",
        },
        "authorize_launch": {
            "handle_use": "single",
            "gate": "same_per_SKI",
            "rechecks": [
                "active_reservation",
                "scope",
                "control_epoch",
                "association_lineage",
                "endpoint",
                "path",
                "retry_state",
                "tombstone_set",
            ],
            "durable_transition": (
                "ATTEMPT_RESERVED_to_ATTEMPT_LAUNCH_AUTHORIZED"
            ),
            "linearization": "launch",
            "stale_handle": "DENY_without_mutation",
        },
        "dial": {
            "immediate_successor": "DialContext",
            "invocations_per_permit": 1,
            "context": "exact_permit_context",
            "canceled_context": "invoke_once_with_zero_network_effect",
            "uninterrupted_cardinality": "PERMIT_equals_DialContext",
            "crash_gap": "restart_synthetic_failure_exactly_once",
        },
        "bounded_failure": {
            "max_active_reservations_per_scope": 1,
            "handle_terminal_actions": [
                "AuthorizeLaunch_once",
                "AbortPrepared_once",
                "lease_expiry_once",
            ],
            "abort_leak_panic": (
                "synthetic_failure_exactly_once_unless_terminal_already_won"
            ),
        },
        "restart": {
            "unresolved_states": [
                "ATTEMPT_RESERVED",
                "ATTEMPT_LAUNCH_AUTHORIZED",
            ],
            "event": "attempt_restart_synthetic_failure",
            "charge": "exactly_once",
            "order": "before_all_runtime_effects",
        },
        "matching_revocation": {
            "before_launch": "atomic_tombstone_deactivate_clear_without_charge",
            "after_launch": (
                "atomic_tombstone_deactivate_clear_then_cancel_"
                "exact_context_without_charge"
            ),
            "crash_after_descriptor": (
                "reconcile_revocation_before_restart_failure"
            ),
            "stale_callback": "no_state_change_no_charge_no_trust",
        },
    },
    "attempt_journal": {
        "rollback_domain": "coordinated_store_and_anchor_publication",
        "operation_classes": [
            "attempt_prepare",
            "attempt_authorize_launch",
            "attempt_terminal_success",
            "attempt_terminal_failure",
            "attempt_abort_synthetic_failure",
            "attempt_restart_synthetic_failure",
            "attempt_retry_ready",
            "attempt_matching_revocation",
        ],
        "reconciliation_observations": [
            "exact_target_selected",
            "exact_previous_selected_and_target_absent",
            "same_number_different_digest_or_reference",
            "other_or_ambiguous",
        ],
    },
    "privacy_contract": {
        "private_root_allowed": [
            "synthetic_private_key",
            "synthetic_certificate",
            "synthetic_SKI",
            "synthetic_SHIP_ID",
            "endpoint",
            "IP",
            "port",
            "path",
            "raw_store",
            "anchor",
        ],
        "public_output_allowed": [
            "repository_metadata",
            "tool_versions",
            "redacted_commands",
            "independent_ordinal_labels",
            "stable_enums",
            "bounded_counts_durations",
            "PASS_FAIL",
        ],
        "forbidden_escape_surfaces": [
            "logs",
            "errors",
            "panic_text",
            "stdout_stderr",
            "artifacts",
            "snapshots",
            "diffs",
            "evidence",
            "public_output_root",
        ],
        "actual_attempt_id_publication": "forbidden",
        "private_root_publication": "forbidden",
        "private_root_deletion": "required",
    },
}


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
    commands = [
        (code_value(row["Closure field"]), row["Exact canonical command or comparison"])
        for row in table_rows(body, "### Immutable Baseline And Closure Commands")
    ]
    require_equal(
        commands,
        [
            ("upstream_tag_object_sha", '`git rev-parse "refs/tags/$TAG^{tag}"`'),
            (
                "upstream_peeled_commit_sha",
                '`git rev-parse "refs/tags/$TAG^{commit}"`',
            ),
            ("upstream_tree_sha", '`git rev-parse "refs/tags/$TAG^{tree}"`'),
            (
                "upstream_license_sha256",
                '`git cat-file blob "$SOURCE_SHA:LICENSE" > "$SCRATCH/LICENSE.bytes" && sha256sum "$SCRATCH/LICENSE.bytes"`',
            ),
            (
                "license_provenance_manifest_sha256",
                '`git cat-file blob "$SOURCE_SHA:provenance/closure-manifest.json" > "$SCRATCH/provenance.json" && sha256sum "$SCRATCH/provenance.json"`',
            ),
            (
                "prerelease_tag_object_sha",
                '`git rev-parse "refs/tags/$TAG^{tag}"`',
            ),
            (
                "prerelease_peeled_commit_sha",
                '`git rev-parse "refs/tags/$TAG^{commit}"`',
            ),
            (
                "module_graph_sha256",
                '`GOWORK=off GOTOOLCHAIN=local go list -mod=readonly -m -json all > "$SCRATCH/modules.json" && jq -S -c . "$SCRATCH/modules.json" > "$SCRATCH/modules.canonical.json" && sha256sum "$SCRATCH/modules.canonical.json"`',
            ),
            (
                "eebusreg_adoption_source_sha",
                "`git rev-parse HEAD` in the clean detached adoption checkout.",
            ),
            (
                "eebusreg_adoption_api_manifest_sha256",
                '`GOWORK=off GOTOOLCHAIN=local go run ./internal/apisurface -output "$SCRATCH/api.json" && sha256sum "$SCRATCH/api.json"`',
            ),
            (
                "eebusreg_public_api_comparison",
                "Generated digest equals `machine.baselines.eebusreg_public_api.manifest.sha256`, whose publication predicate binds `machine.baselines.eebusreg_public_api.source_sha`; byte comparison reports identical.",
            ),
        ],
        "R2 immutable closure commands",
    )
    inventory = coded_rows(
        body,
        "### ship-go Baseline Dial Inventory",
        ("Inventory item", "Baseline", "Required fork result"),
    )
    require_equal(inventory, R2_BASELINE_INVENTORY, "R2 ship-go dial inventory")
    lifecycle = coded_rows(
        body,
        "### Temporary Fork Upstreaming And Retirement",
        ("Sequence", "Required action", "Entry condition", "Current-M4 blocking"),
    )
    require_equal(lifecycle, R2_FORK_LIFECYCLE, "R2 fork lifecycle")


def validate_r2_outgoing_gate_contract(body: str) -> None:
    schema = [
        (
            code_value(row["Phase field"]),
            code_value(row["Phase"]),
            code_value(row["Direction"]),
            row["Exact binding"],
        )
        for row in table_rows(
            body, "| Phase field | Phase | Direction | Exact binding |"
        )
    ]
    require_equal(schema, R2_GATE_SCHEMA, "R2 outgoing gate schema")
    coverage = coded_rows(
        body,
        "### Dial Site Coverage",
        ("Dial variant", "Required gate placement", "Required cardinality"),
    )
    require_equal(coverage, R2_DIAL_COVERAGE, "R2 dial site coverage")


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


def validate_r2_bridge_contract(body: str) -> None:
    rows = coded_rows(
        body,
        "## eebus-go Bridge And Type Boundary",
        ("Layer", "Required additive change", "Forbidden change"),
    )
    require_equal(rows, R2_BRIDGE_ROWS, "R2 bridge rows")


def validate_r2_revocation_race_contract(body: str) -> None:
    rows = coded_rows(
        body,
        "## Revocation And Dial Race Linearization",
        ("Race order", "Linearization", "Required result"),
    )
    require_equal(rows, R2_RACE_ROWS, "R2 revocation race rows")


def validate_r2_falsification_matrix(body: str) -> None:
    rows = coded_rows(
        body,
        "## R2 Pre-Dial Falsification Matrix",
        ("Case", "Fixture/action", "Required observation", "Falsifier"),
    )
    require_equal(rows, R2_MATRIX_ROWS, "R2 falsification matrix")


def validate_r2_operation_journal(body: str) -> None:
    classes = coded_rows(
        body,
        "| Operation class | Exact target mutation | Failure-charge rule |",
        ("Operation class", "Exact target mutation", "Failure-charge rule"),
    )
    require_equal(classes, R2_OPERATION_CLASSES, "R2 operation classes")
    reconciliation = coded_rows(
        body,
        "| Pending class observation | Required reconciliation before runtime | Result |",
        (
            "Pending class observation",
            "Required reconciliation before runtime",
            "Result",
        ),
    )
    require_equal(
        reconciliation,
        R2_ATTEMPT_RECONCILIATION,
        "R2 attempt reconciliation",
    )


def validate_r2_privacy_contract(body: str) -> None:
    rows = coded_rows(
        body,
        "## Public Surface And Evidence Privacy",
        ("Data class", "Allowed content", "Required confinement"),
    )
    require_equal(rows, R2_PRIVACY_ROWS, "R2 private/public data split")


def validate_r2_machine_contract(body: str) -> None:
    contract = machine_yaml(body, "## R2 Normative Machine Contract")
    require_equal(contract, R2_MACHINE_CONTRACT, "R2 normative machine contract")
    normalized = " ".join(body.split())
    contradictions = [
        phrase for phrase in FORBIDDEN_R2_CONTRADICTIONS if phrase in normalized
    ]
    if contradictions:
        raise AssertionError(f"R2 contradiction inserted: {contradictions!r}")


def validate_r2_complete(body: str) -> None:
    validate_r2_machine_contract(body)
    validate_r2_pending_evidence(body)
    validate_r2_fork_contract(body)
    validate_r2_outgoing_gate_contract(body)
    validate_r2_reservation_contract(body)
    validate_r2_bridge_contract(body)
    validate_r2_revocation_race_contract(body)
    validate_r2_operation_journal(body)
    validate_r2_privacy_contract(body)
    validate_r2_falsification_matrix(body)


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
            r"count increments exactly at a matching terminal-failure linearization or an "
            r"explicit abort, lease-expiry, or unresolved-reservation synthetic-failure "
            r"linearization.*never increments on admission, denial, ordinary restart without "
            r"an unresolved reservation, deadline expiry, or wall-clock change.*"
            r"At `attempt_count_max`.*"
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
        validate_r2_machine_contract(body)

    def test_r2_published_api_baseline_is_bound_to_exact_source_and_bytes(self) -> None:
        manifest = ROOT / "api/eebusruntime-v1/manifest.json"
        predicate = json.loads(
            (ROOT / "api/eebusruntime-v1/predicate.json").read_text(encoding="utf-8")
        )
        self.assertEqual(
            hashlib.sha256(manifest.read_bytes()).hexdigest(),
            PUBLIC_API_SHA256,
        )
        self.assertEqual(
            predicate["source"]["commit"],
            PUBLIC_API_SOURCE,
        )
        self.assertEqual(
            predicate["subject"]["sha256"],
            PUBLIC_API_SHA256,
        )

    def test_r2_outgoing_gate_and_reservation_are_closed(self) -> None:
        _, body = read_markdown(CANDIDATE)
        validate_r2_outgoing_gate_contract(body)
        validate_r2_reservation_contract(body)

    def test_r2_bridge_revocation_race_and_matrix_are_closed(self) -> None:
        _, body = read_markdown(CANDIDATE)
        validate_r2_bridge_contract(body)
        validate_r2_revocation_race_contract(body)
        validate_r2_operation_journal(body)
        validate_r2_privacy_contract(body)
        validate_r2_falsification_matrix(body)

    def test_r2_closed_machine_contract_matches_every_normative_table(self) -> None:
        _, body = read_markdown(CANDIDATE)
        validate_r2_complete(body)

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
                "upstream_tag_object_confused_with_peeled_commit",
                validate_r2_pending_evidence,
                "| `ship_go_upstream_tag_object_sha` | "
                "`machine.baselines.ship_go.tag_object.oid` |",
                "| `ship_go_upstream_tag_object_sha` | "
                "`machine.baselines.ship_go.peeled_commit.commit` |",
            ),
            (
                "ship_go_upstream_baseline_changed",
                validate_r2_fork_contract,
                "| `ship_go_fork` | "
                "`github.com/enbility/ship-go@v0.6.0^{commit}` |",
                "| `ship_go_fork` | `github.com/enbility/ship-go@v0.6.1` |",
            ),
            (
                "root_fallback_changed",
                validate_r2_fork_contract,
                "| `fallback_semantics` | "
                "`selected_path_then_root_no_path_on_same_error_condition` | "
                "`preserved_exactly` |",
                "| `fallback_semantics` | `selected_path_only` | `changed` |",
            ),
            (
                "ipv6_gate_bypass",
                validate_r2_outgoing_gate_contract,
                "| `ipv6_retry` | "
                "`Prepare_then_AuthorizeLaunch_immediately_before_DialContext` |",
                "| `ipv6_retry` | `bypass_gate` |",
            ),
            (
                "gate_ambiguity_permitted",
                validate_r2_outgoing_gate_contract,
                "absence, error, panic, stale handle, or ambiguity is `DENY`",
                "absence, error, panic, stale handle, or ambiguity may be `PERMIT`",
            ),
            (
                "unrelated_context_allowed",
                validate_r2_outgoing_gate_contract,
                "Exact per-attempt cancellable context retained by the coordinator",
                "Any unrelated context selected by ship-go",
            ),
            (
                "denial_may_dial",
                validate_r2_falsification_matrix,
                "| `denied_authorize` | `AuthorizeLaunch_returns_DENY` | "
                "`zero_DialContext_calls_for_handle+zero_accepts` |",
                "| `denied_authorize` | `AuthorizeLaunch_returns_DENY` | "
                "`one_DialContext_call` |",
            ),
            (
                "reservation_charges_on_entry",
                validate_r2_reservation_contract,
                "| `prepare_eligible` | `RETRY_READY -> ATTEMPT_RESERVED` | "
                "`zero_DialContext_calls_before_commit` |",
                "| `prepare_eligible` | `RETRY_READY -> BACKOFF_ACTIVE` | "
                "`charge_on_prepare` |",
            ),
            (
                "restart_drops_reservation",
                validate_r2_reservation_contract,
                "| `restart_with_unresolved_reservation` | "
                "`active_attempt -> BACKOFF_ACTIVE_or_ADMIN_HOLD` | "
                "`synthetic_failure_linearization+charge_exactly_once_before_runtime` |",
                "| `restart_with_unresolved_reservation` | `no_state_change` | "
                "`clear_without_charge` |",
            ),
            (
                "matching_revocation_charges_failure",
                validate_r2_reservation_contract,
                "| `matching_revocation` | "
                "`active_attempt -> tombstone+clear_reservation` | "
                "`atomic_no_failure_charge+DENY_or_cancel` |",
                "| `matching_revocation` | `active_attempt -> BACKOFF_ACTIVE` | "
                "`charge_failure` |",
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
                "`configuration_bridge_carries_attempt_handle_and_id` | "
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
                "`atomic_tombstone+clear_reservation+no_failure_charge+cancel_exact_context+disconnect_observed+unregister+no_trust_accept`",
                "`atomic_tombstone+clear_reservation+no_failure_charge+disconnect_observed+unregister+no_trust_accept`",
            ),
            (
                "matching_revocation_reconciliation_removed",
                validate_r2_operation_journal,
                "| `attempt_matching_revocation+exact_previous_selected_and_target_absent` | "
                "`retry_exact_target_commit_without_clear_then_finalize` |",
                "| `attempt_matching_revocation+exact_previous_selected_and_target_absent` | "
                "`compare_and_clear(exact_descriptor)` |",
            ),
            (
                "private_input_allowed_in_public_output",
                validate_r2_privacy_contract,
                "| `publishable_G16_output` | "
                "`repo+branch+commit+issue+tool_versions+redacted_commands+per_run_ordinal_labels+stable_enums+bounded_counts_durations+PASS_FAIL` |",
                "| `publishable_G16_output` | `synthetic_SKI+endpoint+PASS_FAIL` |",
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

    def test_r2_rejects_cross_section_contradiction_insertions(self) -> None:
        _, body = read_markdown(CANDIDATE)
        anchor = "\n## Required Tests And Exclusions"
        for contradiction in FORBIDDEN_R2_CONTRADICTIONS:
            with self.subTest(contradiction=contradiction):
                mutated = mutate_once(
                    body,
                    anchor,
                    f"\n{contradiction}\n{anchor}",
                )
                with self.assertRaises(AssertionError):
                    validate_r2_complete(mutated)

    def test_r2_machine_contract_rejects_machine_only_weakening(self) -> None:
        _, body = read_markdown(CANDIDATE)
        mutations = (
            ("ipv6", "    - ipv6\n", "    - ipv6_bypass\n"),
            (
                "restart_charge",
                "    charge: exactly_once\n",
                "    charge: clear_without_charge\n",
            ),
            (
                "context_identity",
                "    context: exact_permit_context\n",
                "    context: unrelated_context\n",
            ),
            (
                "pseudo_version",
                "    - pseudo_version\n",
                "    - pseudo_version_allowed\n",
            ),
            (
                "residual_dial",
                "  fork_direct_Dial_calls: 0\n",
                "  fork_direct_Dial_calls: 1\n",
            ),
            (
                "private_leak",
                "  actual_attempt_id_publication: forbidden\n",
                "  actual_attempt_id_publication: allowed\n",
            ),
            (
                "after_launch_revocation_leaves_reservation_live",
                "    after_launch: atomic_tombstone_deactivate_clear_then_cancel_exact_context_without_charge\n",
                "    after_launch: tombstone_then_cancel_exact_context\n",
            ),
        )
        for label, old, new in mutations:
            with self.subTest(label=label):
                mutated = mutate_once(body, old, new)
                with self.assertRaises(AssertionError):
                    validate_r2_machine_contract(mutated)

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
                "Publishable integration artifacts",
                "Caller-asserted artifacts",
            ),
            (
                "g16_fail",
                "scan input omits an output surface",
                "scan input omits helper output",
            ),
            (
                "g10_r2_pass",
                "with zero calls for pre-launch denial, publication failure, backoff, "
                "quarantine, and terminal hold",
                "with caller-asserted zero calls",
            ),
            (
                "g10_r2_fail",
                "treats callback injection as pre-dial evidence",
                "accepts callback injection as pre-dial evidence",
            ),
            (
                "g11_r2_pass",
                "across selected-path and root/no-path fallback, hostname/IPv4/IPv6 retry, "
                "crash recovery, delayed callback, discovery storm, abort/panic, "
                "and revocation races",
                "across one helper callback",
            ),
            (
                "g11_r2_fail",
                "injected callbacks pass without dial/accept observations",
                "injected callbacks pass with no observations",
            ),
            (
                "g16_r2_pass",
                "R2 publishes only redacted reservation/launch ordering and "
                "ordinal attempt labels",
                "R2 records a caller-asserted attempt",
            ),
            (
                "g16_r2_fail",
                "callback-only evidence is accepted without the "
                "reservation/launch/dial/accept binding",
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
            "Private generated fixture inputs and publishable evidence are disjoint roots",
            "synthetic private material only inside its isolated per-run input/store root",
            "private_generated_test_input",
            "publishable_G16_output",
            "forbidden canary set from every private generated input",
            "captured logs, structured and unstructured errors, recovered panic text",
            "Hardware checks remain SSH-only",
            "Raw store, anchor, admin frames, transcripts, private generated inputs, and fixture internals are never published",
        )
        for phrase in required:
            self.assertIn(phrase, normalized)


if __name__ == "__main__":
    unittest.main()
