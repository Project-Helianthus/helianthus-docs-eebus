from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARCH = ROOT / "architecture/_candidate/post-m9-operator-pairing-browsers-v1.md"
API = ROOT / "api/_candidate/post-m9-operator-admin-v1.md"


def normalized(path: Path) -> str:
    return " ".join(path.read_text(encoding="utf-8").split())


class PostM9ClosureContractTests(unittest.TestCase):
    def test_eebus_driver_failure_is_nonfatal_and_restart_is_bounded(self) -> None:
        arch = normalized(ARCH)
        for phrase in (
            "optional protocol-adapter startup lane",
            "loading eeBUS configuration, local identity, listener, runtime factory, or AdminV1 construction",
            "must not terminate or de-admit eBUS, Modbus, MCP, GraphQL, Portal, or the gateway health API",
            "`eebus_readiness=DEGRADED`",
            "bounded restart schedule",
            "never a tight retry loop",
        ):
            self.assertIn(phrase, arch)

    def test_untrust_preserves_m4c_durable_denial_before_withdrawal(self) -> None:
        arch = normalized(ARCH)
        api = normalized(API)
        combined = f"{arch} {api}"
        for phrase in (
            "canonical M4C durable-denial-first invariant",
            "denies the association in memory before publishing the durable tombstone",
            "durable denial and tombstone precede live withdrawal",
            "already-absent result completes as `revoked` after durability",
            "same-generation disconnect ACK classifies withdrawal completeness, never trust state",
            "`revocation_withdrawal_incomplete`",
            "remains revoked and tombstoned",
        ):
            self.assertIn(phrase, combined)
        for forbidden in (
            "Durable revocation starts only after that ACK",
            "`disconnect_ack_timeout`, leaves durable trust unchanged",
            "preserves the durable association",
        ):
            self.assertNotIn(forbidden, combined)

    def test_raw_topology_exact_replaces_each_connected_generation(self) -> None:
        arch = normalized(ARCH)
        api = normalized(API)
        combined = f"{arch} {api}"
        for phrase in (
            "current connected generation",
            "exact replacement, never a merge",
            "disconnect, current-device removal, or a complete current-generation refresh with no devices publishes an empty raw topology",
            "entity or feature add/remove triggers a complete refreshed live graph",
            "exact replacement preserves every unrelated node still present",
            "reduced reconnect publishes exactly the reduced device/entity/feature sets",
            "invalidates every snapshot and cursor from the earlier generation",
            "Semantic last-known-good retention is a separate consumer fact",
            "must never repopulate the raw SPINE tree",
        ):
            self.assertIn(phrase, combined)
        for forbidden in (
            "disconnect, remove, or empty current-generation snapshot publishes an empty raw topology",
            "A remove or empty current-generation publication therefore produces no nodes",
        ):
            self.assertNotIn(forbidden, combined)

    def test_link_local_scope_and_pin_are_transient_secret_safe(self) -> None:
        arch = normalized(ARCH)
        api = normalized(API)
        combined = f"{arch} {api}"
        for phrase in (
            "IPv6 link-local endpoint requires the discovery-owned interface scope",
            "never accepts a caller-supplied scope or endpoint",
            "`endpoint_scope_unavailable`",
            "`REQUIRED`, `OPTIONAL`, or `NOT_APPLICABLE`",
            "`pin_required`",
            "`pin_rejected`",
            "optional sensitive `pin` field",
            "request-lifetime memory",
            "PIN value never enters a response, replay record, durable store, log, metric, trace, diagnostic, URL, or browser storage",
        ):
            self.assertIn(phrase, combined)

    def test_admin_status_and_partner_retry_fields_are_closed(self) -> None:
        api = normalized(API)
        for phrase in (
            "local_ski",
            "local_ship_id",
            "brand?",
            "device_type?",
            "model?",
            "endpoint?",
            "connection_state",
            "partner_readiness: `disconnected | session_connected | topology_ready`",
            "retry_state: `RETRY_READY | BACKOFF_ACTIVE | ADMIN_HOLD`",
            "retry_deadline?",
            "retry_admitted",
            "true only for a currently admitted `RETRY_READY` row",
            "`BACKOFF_ACTIVE` requires a future retry deadline",
            "`ADMIN_HOLD` is terminal quarantine",
            "Retry rejects unless `retry_admitted=true`",
        ):
            self.assertIn(phrase, api)

    def test_home_assistant_flow_is_native_ephemeral_and_error_closed(self) -> None:
        arch = normalized(ARCH)
        api = normalized(API)
        combined = f"{arch} {api}"
        for phrase in (
            "HA-native config/options/repair flow",
            "closed sanitized action-error table",
            "keeps only `selection_id` and its issuing revision in the volatile active flow",
            "The `Select` response does not clear that volatile selection",
            "until Connect reaches a terminal result or the selection expires",
            "candidate comparison data remains only until confirm, cancel, candidate expiry",
            "does not persist SKI or candidate identity",
            "config entry, entity registry, device registry, issue registry, diagnostics, or reusable application storage",
            "no eeBUS-specific login, session, cookie, CSRF token, credential, or reauthentication",
            "action-time confirmation remains an operational control only",
        ):
            self.assertIn(phrase, combined)

    def test_active_candidate_survives_unrelated_responses(self) -> None:
        api = normalized(API)
        for phrase in (
            "Unrelated status, partner, discovery, selection, and readiness responses never clear or replace the active candidate",
            "Only a candidate response for a newer candidate generation may replace it",
            "Confirm terminal success or failure, Cancel terminal success or failure, candidate expiry, pairing-window close, connection close, generation change, navigation away, visibility loss, or explicit flow abort clears the active candidate",
        ):
            self.assertIn(phrase, api)
        for forbidden in (
            "replacement by any later response",
            "replacement by a later response",
        ):
            self.assertNotIn(forbidden, api)

    def test_build_identity_and_readiness_dimensions_are_not_conflated(self) -> None:
        api = normalized(API)
        for phrase in (
            "one immutable build-info object",
            "`release_version` and `build_id`",
            "Portal health, MCP initialize `serverInfo.version`, and `runtime_state.meta`",
            "does not add a field to a frozen stable `eebus.v1.*` tool",
            "existing raw eeBUS MCP contract remains unchanged",
            "`AdminSnapshotV1` owns the `admin` portion",
            "does not own gateway build or process readiness",
            "Process readiness, eeBUS driver readiness, and partner/session readiness are three independent dimensions",
            "process_readiness: `READY | NOT_READY`",
            "eebus_readiness: `DISABLED | STARTING | READY | DEGRADED | FAILED`",
            "`CONFIGURATION_INVALID | LOCAL_IDENTITY_UNAVAILABLE | LISTENER_UNAVAILABLE | RUNTIME_FACTORY_UNAVAILABLE | ADMIN_BOUNDARY_UNAVAILABLE | UNKNOWN_STARTUP_FAILURE`",
            "An unknown startup failure with no usable runtime maps to `FAILED / UNKNOWN_STARTUP_FAILURE`",
            "eeBUS startup failure alone never maps process readiness to `NOT_READY`",
            "An eeBUS `DEGRADED` state does not rewrite process readiness",
            "A disconnected partner does not rewrite eeBUS driver readiness",
        ):
            self.assertIn(phrase, api)

    def test_environment_absence_is_not_product_behavior(self) -> None:
        arch = normalized(ARCH)
        for phrase in (
            "Physically disconnected eBUS participants",
            "an offline VR940F",
            "environment observations only",
            "must not be encoded as product behavior or generic protocol evidence",
        ):
            self.assertIn(phrase, arch)


if __name__ == "__main__":
    unittest.main()
