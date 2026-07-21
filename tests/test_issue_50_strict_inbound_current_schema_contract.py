from __future__ import annotations

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
    spec = importlib.util.spec_from_file_location("issue50_policy", POLICY_PATH)
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


class Issue50StrictInboundCurrentSchemaContractTests(unittest.TestCase):
    INBOUND_PATHS = (
        "protocols/ship-spine-overview.md",
        "architecture/_candidate/msp-04c-restore-revocation-quarantine-repair.md",
        "api/_candidate/msp-05p-eebusruntime-v1-correction.md",
    )
    INBOUND_CLAUSE = (
        "Discovery observations and allowlist evaluation never initiate an "
        "outbound dial or pairing attempt"
    )
    SCHEMA_PATH = "architecture/_candidate/msp-04a-persistent-store.md"
    SCHEMA_CLAUSES = (
        "only current persistence schema version 1",
        "Every non-current schema version fails closed",
        "leaves every store byte unchanged",
    )

    @classmethod
    def setUpClass(cls) -> None:
        cls.architecture = read("architecture/_candidate/msp-04a-persistent-store.md")
        cls.protocol = read("protocols/ship-spine-overview.md")
        cls.security = read(
            "architecture/_candidate/msp-04c-restore-revocation-quarantine-repair.md"
        )
        cls.api = read("api/_candidate/msp-05p-eebusruntime-v1-correction.md")
        cls.identity = read("architecture/ship-identity.md")
        cls.corpus = "\n".join(
            (
                cls.architecture,
                cls.protocol,
                cls.security,
                cls.api,
                cls.identity,
            )
        )

    def test_canonical_ship_publisher_has_no_rawprobe_runtime_identity(self) -> None:
        normalized = compact(self.protocol)

        self.assertIn("exactly one canonical SHIP/mDNS publisher", normalized)
        self.assertIn("No second publisher, probe identity", normalized)
        self.assertNotIn("RawProbe", self.corpus)

    def test_discovery_and_allowlist_are_inbound_only(self) -> None:
        for text in (self.protocol, self.security):
            with self.subTest(document=text):
                normalized = compact(text)
                self.assertIn("never initiate an outbound dial or pairing attempt", normalized)

    def test_outgoing_attempt_legacy_paths_are_absent(self) -> None:
        for forbidden in (
            "OutgoingAttemptBridge",
            "pre-dial",
            "predial",
            "endpoint_fallback",
            "endpoint_path",
            "fallback outbound",
        ):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, self.corpus)

    def test_only_current_schema_loads_without_rewrite(self) -> None:
        normalized = compact(self.architecture)

        self.assertIn("only current persistence schema version 1", normalized)
        self.assertIn("Every non-current schema version fails closed", normalized)
        self.assertIn("leaves every store byte unchanged", normalized)
        self.assertNotIn("migration", self.architecture.lower())
        self.assertNotIn("rewrite", self.architecture.lower())

    def test_current_store_instance_stays_stable_across_restart(self) -> None:
        normalized = compact(self.architecture)

        self.assertIn("ordinary restart loads the exact current StoreInstance", normalized)
        self.assertIn("must remain byte-for-byte unchanged", normalized)
        self.assertIn("canonical SHIP ID", normalized)

    def test_policy_rejects_removed_runtime_paths_in_current_docs(self) -> None:
        policy = load_policy_module()
        validator = getattr(policy, "ship_identity_corpus_errors")
        schema_validator = getattr(policy, "strict_current_schema_errors")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            page = root / "protocols" / "current.md"
            page.parent.mkdir(parents=True)
            page.write_text(
                "---\n"
                'canonical_source: "fixture"\n'
                'owner_domain: "protocols"\n'
                'license: "CC0-1.0"\n'
                'publication_status: "publishable"\n'
                "---\n\n"
                "RawProbe starts a pre-dial fallback outbound pairing attempt.\n",
                encoding="utf-8",
            )
            errors = validator(root)
            schema_page = root / "architecture" / "_candidate" / "msp-04a-persistent-store.md"
            schema_page.parent.mkdir(parents=True)
            schema_page.write_text(
                "---\n"
                'canonical_source: "fixture"\n'
                'owner_domain: "architecture"\n'
                'license: "AGPL-3.0-only"\n'
                'publication_status: "candidate"\n'
                "---\n\n"
                "Older bytes need a migration before use.\n",
                encoding="utf-8",
            )
            schema_errors = schema_validator(root)

        self.assertTrue(
            any("noncanonical-publisher" in error for error in errors), errors
        )
        self.assertTrue(
            any("outbound-initiation" in error for error in errors), errors
        )
        self.assertTrue(
            any("strict-current-schema" in error for error in schema_errors),
            schema_errors,
        )

    def test_policy_rejects_renamed_outbound_initiation(self) -> None:
        policy = load_policy_module()
        validator = getattr(policy, "normative_inbound_only_errors")
        variants = (
            "A discovery observation opens a TCP connection to an allowlisted peer.",
            "A TCP connection is opened when discovery sees an allowlisted peer.",
            "Pairing is triggered by allowlist evaluation.",
            "A " + "SH" + "IP handshake launches after an observed service appears.",
            "A pairing dial starts because an allowlisted peer was observed.",
            "To connect by TCP, the runtime consumes a discovery observation",
            "Discovery must not open TCP but launches a "
            + "SH"
            + "IP handshake.",
            "A discovery observation dials a remote peer over TCP.",
            "An allowlisted peer was dialed after a network observation.",
            "Dialing starts after an allowlist observation.",
            "A TCP dial launches after discovery.",
        )

        for body in variants:
            with self.subTest(body=body), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                for relative_path in self.INBOUND_PATHS:
                    page = root / relative_path
                    page.parent.mkdir(parents=True, exist_ok=True)
                    page.write_text(
                        self.INBOUND_CLAUSE
                        + ".\n"
                        + (f"{body}\n" if relative_path == self.INBOUND_PATHS[0] else ""),
                        encoding="utf-8",
                    )
                errors = validator(root)

            self.assertEqual(
                [
                    "protocols/ship-spine-overview.md:2: forbidden "
                    "outbound-initiation"
                ],
                errors,
            )

    def test_policy_allows_explicit_inbound_only_prohibitions(self) -> None:
        policy = load_policy_module()
        validator = getattr(policy, "normative_inbound_only_errors")
        variants = (
            "No discovery observation opens a TCP connection.",
            "An allowlisted peer must not initiate pairing.",
            "SH" + "IP pairing is prohibited from starting after observation.",
            "A TCP connection does not launch from discovery.",
            "Discovery cannot trigger a " + "SH" + "IP handshake.",
            "The allowlist is not permitted to connect a TCP peer.",
            "A discovery observation doesn't open a TCP connection.",
            "An allowlisted peer can't initiate pairing.",
            "Discovery won't trigger a " + "SH" + "IP handshake.",
            "A discovery observation opens no TCP connection.",
            "An observed service dials no " + "SH" + "IP peer.",
        )

        for body in variants:
            with self.subTest(body=body), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                for relative_path in self.INBOUND_PATHS:
                    page = root / relative_path
                    page.parent.mkdir(parents=True, exist_ok=True)
                    page.write_text(
                        self.INBOUND_CLAUSE
                        + ".\n"
                        + (f"{body}\n" if relative_path == self.INBOUND_PATHS[0] else ""),
                        encoding="utf-8",
                    )

                self.assertEqual([], validator(root))

    def test_inbound_only_clause_is_canonical_across_normative_surfaces(self) -> None:
        required = "Discovery observations and allowlist evaluation never initiate an outbound dial or pairing attempt"

        for text in (self.protocol, self.security, self.api):
            with self.subTest(document=text):
                self.assertIn(required, compact(text))

    def test_policy_rejects_noncurrent_schema_transitions_and_missing_contract(self) -> None:
        policy = load_policy_module()
        validator = getattr(policy, "strict_current_schema_errors")
        variants = (
            "Schema version 0 is converted to schema version 1 before activation.",
            "An older store is loaded before activation.",
            "Loading occurs before activation for a legacy store.",
            "Conversion precedes activation of schema version 0.",
            "Upgrade is applied to a non-current schema before startup.",
            "A schema-version-0 store is transformed before activation.",
            "The runtime falls back to older persisted state.",
            "Fallback accepts legacy state during startup",
            "A legacy store is not loaded but is converted before activation.",
            "A noncurrent schema is loaded before activation.",
            "The runtime converts v0 to v1 before activation.",
            "Fallback loads v2 during startup.",
            "A v0 store is accepted before activation.",
        )

        for body in variants:
            with self.subTest(body=body), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                page = root / self.SCHEMA_PATH
                page.parent.mkdir(parents=True)
                page.write_text(
                    "\n".join(f"{clause}." for clause in self.SCHEMA_CLAUSES)
                    + f"\n{body}\n",
                    encoding="utf-8",
                )
                errors = validator(root)

            self.assertEqual(
                [
                    "architecture/_candidate/msp-04a-persistent-store.md:4: "
                    "forbidden strict-current-schema transition"
                ],
                errors,
            )

    def test_policy_allows_explicit_current_only_prohibitions(self) -> None:
        policy = load_policy_module()
        validator = getattr(policy, "strict_current_schema_errors")
        variants = (
            "No older schema is accepted or loaded.",
            "Schema version 0 is not loaded before activation.",
            "Conversion of a legacy store is prohibited.",
            "The runtime must not upgrade a non-current store.",
            "Current-only activation cannot fall back to schema version 0.",
            "An older fixture was observed but never transformed.",
            "The runtime accepts no older schema.",
            "The runtime doesn't load a noncurrent schema.",
            "The runtime can't transform v0.",
            "Only v1 is accepted before activation.",
            "No v2 schema is upgraded.",
            "The runtime won't fall back to v0.",
        )

        for body in variants:
            with self.subTest(body=body), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                page = root / self.SCHEMA_PATH
                page.parent.mkdir(parents=True)
                page.write_text(
                    "\n".join(f"{clause}." for clause in self.SCHEMA_CLAUSES)
                    + f"\n{body}\n",
                    encoding="utf-8",
                )

                self.assertEqual([], validator(root))


if __name__ == "__main__":
    unittest.main()
