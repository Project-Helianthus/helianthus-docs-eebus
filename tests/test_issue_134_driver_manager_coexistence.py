from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
COEXISTENCE = ROOT / "architecture" / "multi-runtime-coexistence.md"
ADMIN = ROOT / "api" / "_candidate" / "post-m9-operator-admin-v1.md"


def normalized(path: Path) -> str:
    return " ".join(path.read_text(encoding="utf-8").split())


class DriverManagerCoexistenceContractTest(unittest.TestCase):
    def test_admin_provider_remains_stable_across_driver_states(self) -> None:
        text = normalized(ADMIN)
        for phrase in (
            "`DISABLED | STARTING | READY | DEGRADED | FAILED`",
            "stable gateway-owned admin/provider boundary remains registered",
            "never requires a process restart to regain the operator boundary",
            "`connected_count=0` is valid in `READY`",
            "listener and discovery are healthy",
        ):
            self.assertIn(phrase, text)

    def test_stop_and_restart_have_closed_ownership_and_generation_rules(self) -> None:
        text = normalized(ADMIN) + " " + normalized(COEXISTENCE)
        for phrase in (
            "Stop cancels the current transient pairing action",
            "closes the pairing window",
            "stops listener and discovery",
            "preserves the durable local identity, trust store, and state root",
            "Restart is one ordered Stop followed by one bounded Start",
            "allocates a new runtime generation",
            "A callback from an older generation cannot publish",
        ):
            self.assertIn(phrase, text)

    def test_stale_callbacks_are_fenced_before_durable_or_volatile_mutation(self) -> None:
        text = normalized(ADMIN)
        for phrase in (
            "under the same operator serializer that owns the pending effect",
            "before every state or store mutation, including `commit_durable`",
            "captured runtime generation and cancellation state",
            "cannot create durable trust, a candidate, or an active action",
            "cannot alter the replacement generation",
        ):
            self.assertIn(phrase, text)

    def test_lifecycle_never_smuggles_pairing_or_trust_effects(self) -> None:
        text = normalized(ADMIN)
        for phrase in (
            "Start, Stop, and Restart never pair, retry, untrust, or confirm",
            "PIN and active-action confidentiality rules remain unchanged",
            "does not persist or replay a transient candidate",
            "requires a new explicit operator action",
        ):
            self.assertIn(phrase, text)

    def test_driver_failure_and_invalid_bootstrap_are_isolated(self) -> None:
        text = normalized(COEXISTENCE) + " " + normalized(ADMIN)
        for phrase in (
            "never terminates the eBUS or Modbus drivers",
            "never removes the shared API, Portal, MCP, or GraphQL listeners",
            "rejected eeBUS bootstrap",
            "categorized eeBUS configuration failure",
            "must not exit the whole gateway process",
        ):
            self.assertIn(phrase, text)

    def test_offline_vr940_is_a_valid_environmental_acceptance_state(self) -> None:
        text = normalized(COEXISTENCE)
        for phrase in (
            "VR940 is physically offline",
            "`READY` with `connected_count=0`",
            "not a driver degradation",
            "no SPINE topology is expected",
            "does not authorize synthetic topology or automatic pairing",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
