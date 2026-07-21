from __future__ import annotations

import hashlib
import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
POLICY_PATH = REPO / "scripts" / "validate_repository_policy.py"


def read(relative: str) -> str:
    return (REPO / relative).read_text(encoding="utf-8")


def compact(value: str) -> str:
    return " ".join(value.split())


def load_policy_module():
    spec = importlib.util.spec_from_file_location("issue48_policy", POLICY_PATH)
    if spec is None or spec.loader is None:
        raise AssertionError("repository policy validator cannot be loaded")
    module = importlib.util.module_from_spec(spec)
    scripts_path = str(POLICY_PATH.parent)
    sys.path.insert(0, scripts_path)
    try:
        spec.loader.exec_module(module)
    finally:
        sys.path.remove(scripts_path)
    return module


class Issue48ShipIdentityContractTests(unittest.TestCase):
    def test_node_token_bytes_and_known_vector_are_exact(self) -> None:
        architecture = read("architecture/ship-identity.md")
        store_instance = bytes(range(32))
        digest = hashlib.sha256(
            b"helianthus-eebus-node-v1" + b"\x00" + store_instance
        ).digest()
        derived_value = digest[:16].hex()

        self.assertEqual(
            digest.hex(),
            "829b6a31d06778a73e1be775912663953b561c1e30fd6d2dbc8eacbc453e787b",
        )
        self.assertEqual(derived_value, "829b6a31d06778a73e1be77591266395")
        self.assertIn("decoded raw 32-byte `StoreInstance`", architecture)
        self.assertIn("single NUL byte", architecture)
        self.assertIn(
            "000102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f",
            architecture,
        )
        self.assertIn(digest.hex(), architecture)
        self.assertIn(derived_value, architecture)
        self.assertIn(f"HLS-{derived_value}", architecture)

    def test_ship_id_and_advertisement_have_one_canonical_name(self) -> None:
        architecture = read("architecture/ship-identity.md")
        protocol = read("protocols/ship-spine-overview.md")
        live_gate = read("evidence/ship-identity-live-validation.md")
        corpus = "\n".join((architecture, protocol, live_gate))

        self.assertIn("Canonical SHIP ID", architecture)
        self.assertIn("`HLS-<nodeToken>`", architecture)
        self.assertNotIn("alternate SHIP ID", corpus.lower())
        self.assertNotIn("alternate protocol-service", corpus.lower())
        self.assertNotIn("compatibility publisher", corpus.lower())

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

    def test_identity_contract_is_normative_derived_and_live_pending(self) -> None:
        for relative in (
            "architecture/ship-identity.md",
            "protocols/ship-spine-overview.md",
            "evidence/ship-identity-live-validation.md",
        ):
            with self.subTest(relative=relative):
                text = read(relative)
                self.assertIn('source_class: "derived_inference"', text)
                self.assertIn('contract_status: "normative"', text)
                self.assertIn('live_validation_status: "pending"', text)
                self.assertNotIn('source_class: "observed_runtime"', text)
        self.assertIn("does not establish deployed support", read("protocols/ship-spine-overview.md"))

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
        self.assertIn("Durable policy does not create a remote row", projection)

    def test_repair_rotates_certificate_without_rotating_ship_identity(self) -> None:
        architecture = read("architecture/ship-identity.md")
        repair = read("architecture/_candidate/msp-04c-restore-revocation-quarantine-repair.md")
        live_gate = read("evidence/ship-identity-live-validation.md")
        combined = compact("\n".join((architecture, repair, live_gate)))

        self.assertIn("real host-key and certificate repair", combined)
        self.assertIn("certificate SKI must change", combined)
        self.assertIn("raw 32-byte `StoreInstance` must remain byte-for-byte unchanged", combined)
        self.assertIn("`nodeToken` must remain exactly unchanged", combined)
        self.assertIn("canonical SHIP ID must remain exactly unchanged", combined)

    def test_evidence_remains_raw_redacted_and_live_gated(self) -> None:
        api = read("api/_candidate/msp-06-eebus-mcp-v1.md")
        evidence = read("evidence/README.md")
        live_gate = read("evidence/ship-identity-live-validation.md")

        self.assertIn("closed stable inventory", api)
        self.assertIn("raw runtime observations only", api)
        self.assertIn("adds no tool, field, semantic object", api)
        self.assertIn("closed `eebus.v1` read-only contract", evidence)
        self.assertIn("No evidence entry promotes SPINE payloads into device semantics", evidence)
        self.assertIn("Exactly one `_ship._tcp` advertisement", live_gate)
        self.assertIn("`<redacted-lab-address>:4712`", live_gate)
        self.assertIn("Before the first observed TCP SYN", live_gate)
        self.assertIn("closed stable `eebus.v1` read-only tools", live_gate)

    def test_normative_corpus_has_no_forced_endpoint_or_compatibility_path(self) -> None:
        policy = load_policy_module()
        validator = getattr(policy, "ship_identity_corpus_errors")
        self.assertEqual(validator(REPO), [])

    def test_superseded_allowance_is_exact_path_and_rule_only(self) -> None:
        policy = load_policy_module()
        validator = getattr(policy, "ship_identity_corpus_errors")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            evidence = root / "evidence" / "EV-20990101-001.md"
            evidence.parent.mkdir(parents=True)
            evidence.write_text(
                "---\n"
                'canonical_source: "fixture"\n'
                'owner_domain: "evidence"\n'
                'license: "CC0-1.0"\n'
                'publication_status: "publishable"\n'
                'identity_contract_scope: "superseded_non_normative"\n'
                "---\n\n"
                "# Historical\n\nAlternate SHIP ID and QueueRemoteSKI.\n",
                encoding="utf-8",
            )
            errors = validator(
                root,
                superseded_allow={
                    "evidence/EV-20990101-001.md": frozenset({"alternate-ship-id"})
                },
            )
        self.assertEqual(len(errors), 1)
        self.assertIn("queue-remote-ski", errors[0])


if __name__ == "__main__":
    unittest.main()
