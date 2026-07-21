from __future__ import annotations

import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]


def read(relative: str) -> str:
    return (REPO / relative).read_text(encoding="utf-8")


def compact(value: str) -> str:
    return " ".join(value.split())


class Issue48ShipIdentityContractTests(unittest.TestCase):
    def test_identity_derivation_and_advertisement_are_canonical(self) -> None:
        architecture = read("architecture/ship-identity.md")
        protocol = read("protocols/ship-spine-overview.md")

        self.assertIn(
            'SHA256("helianthus-eebus-node-v1\\0" || protected persisted StoreInstance)',
            architecture,
        )
        self.assertIn("first 16 bytes", architecture)
        self.assertIn("lowercase hexadecimal", architecture)
        self.assertIn("`HLS-<nodeToken>`", architecture)
        self.assertIn("Certificate SKI", architecture)
        self.assertIn("DNS-SD instance", architecture)
        self.assertIn("Authorization policy", architecture)
        self.assertIn("Observed runtime state", architecture)

        self.assertIn("exactly one `_ship._tcp` service", protocol)
        self.assertIn("Helianthus EnergyManagementSystem eebusreg", protocol)
        for row in (
            "| `txtvers` | `1` |",
            "| `path` | `/ship/` |",
            "| `id` | `HLS-<nodeToken>` |",
            "| `ski` | `<certificate SKI>` |",
            "| `brand` | `Helianthus` |",
            "| `model` | `eebusreg` |",
            "| `type` | `EnergyManagementSystem` |",
            "| `register` | `<window>` |",
        ):
            self.assertIn(row, protocol)

    def test_policy_inputs_never_create_observed_remote_state(self) -> None:
        protocol = read("protocols/ship-spine-overview.md")
        trust = read("architecture/_candidate/msp-04b-first-trust-admin-local.md")
        projection = read("architecture/_candidate/msp-045-trust-admin-projection.md")

        self.assertIn("Opening the local pairing window", protocol)
        self.assertIn("does not queue, report, or dial", protocol)
        self.assertIn("An mDNS observation callback may create a visible remote service", protocol)
        self.assertIn("Only an actual connection callback may create a session", compact(protocol))
        self.assertIn("transport connection may create the single volatile pairing", protocol)

        self.assertIn("Authorization And Observation Separation", trust)
        self.assertIn("Only a pairing callback backed by an active transport connection", compact(trust))
        self.assertIn("Configured or durable policy does not create a remote row", projection)
        self.assertNotIn("Migration Boundary", projection)
        self.assertNotIn("explicit_conformance_migration", projection)

        for obsolete in (
            "Candidate Outbound Endpoint Policy",
            "bounded, RAM-only queue of eligible outbound attempt records",
            "outbound-attempt queue",
            "endpoint-report path",
        ):
            self.assertNotIn(obsolete, protocol)
            self.assertNotIn(obsolete, trust)

    def test_evidence_remains_raw_redacted_and_live_gated(self) -> None:
        api = read("api/_candidate/msp-06-eebus-mcp-v1.md")
        evidence = read("evidence/README.md")
        device = read("devices/vr940f.md")
        live_gate = read("evidence/ship-identity-live-validation.md")

        self.assertIn("closed stable inventory", api)
        self.assertIn("raw runtime observations only", api)
        self.assertIn("adds no tool, field, semantic object", api)
        self.assertIn("closed `eebus.v1` read-only contract", evidence)
        self.assertIn("No evidence entry promotes SPINE payloads into device semantics", evidence)

        self.assertIn("canonical live validation gate", device)
        self.assertIn("Exactly one `_ship._tcp` advertisement", live_gate)
        self.assertIn("`end0`", live_gate)
        self.assertIn("`<redacted-lab-address>:4712`", live_gate)
        self.assertIn("Before the first observed TCP SYN", live_gate)
        self.assertIn("exact protected\n   reference", live_gate)
        self.assertIn("TCP first, then SHIP", live_gate)
        self.assertIn("same `nodeToken`", live_gate)
        self.assertIn("closed stable `eebus.v1` read-only tools", live_gate)


if __name__ == "__main__":
    unittest.main()
