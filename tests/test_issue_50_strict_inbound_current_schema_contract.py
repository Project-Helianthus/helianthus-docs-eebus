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
    OUTBOUND_PATHS = (
        "architecture/_candidate/msp-052-outbound-pairing-contract.md",
        "api/_candidate/msp-052-outbound-pairing-api.md",
    )
    OUTBOUND_GUARD_PATHS = ("protocols/ship-spine-overview.md",) + OUTBOUND_PATHS
    OUTBOUND_CLAUSE = (
        "discovery and allowlist evaluation alone never initiate a "
        "network attempt"
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
        cls.outbound_api = read("api/_candidate/msp-052-outbound-pairing-api.md")
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

    def test_stable_protocol_retains_reviewed_passive_discovery_rule(self) -> None:
        normalized = compact(self.protocol)
        self.assertIn(
            "Discovery observations and allowlist evaluation never initiate an outbound dial or pairing attempt",
            normalized,
        )
        self.assertNotIn("candidate_ref", normalized)

    def test_candidate_dependency_contracts_remain_private_and_experimental(self) -> None:
        normalized = compact(self.outbound_api)
        self.assertIn(
            "`PairingCandidateQueuer` and `CandidateRef` are private experimental process-local dependency capabilities only",
            normalized,
        )
        self.assertIn(
            "does not promote `candidate_ref` into `helianthus-eebusreg` public state",
            normalized,
        )
        self.assertIn(
            "`candidate_ref` is a process-local dependency capability only",
            normalized,
        )
        self.assertIn(
            "never durable and never stable `helianthus-eebusreg`, MCP, or GraphQL state",
            normalized,
        )

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

    def test_policy_requires_all_outbound_pairing_contract_surfaces(self) -> None:
        policy = load_policy_module()
        validator = getattr(policy, "outbound_pairing_contract_errors")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for relative_path in self.OUTBOUND_PATHS:
                page = root / relative_path
                page.parent.mkdir(parents=True, exist_ok=True)
                page.write_text(self.OUTBOUND_CLAUSE + ".\n", encoding="utf-8")
            errors = validator(root)

        self.assertTrue(
            any("missing outbound-pairing requirement" in error for error in errors),
            errors,
        )

    def test_outbound_pairing_contract_is_canonical_across_owned_surfaces(self) -> None:
        for relative_path in self.OUTBOUND_PATHS:
            with self.subTest(document=relative_path):
                self.assertIn(self.OUTBOUND_CLAUSE, compact(read(relative_path)))

    def test_issue54_selected_candidate_journal_and_shutdown_contract_is_explicit(self) -> None:
        normalized = compact(
            read("architecture/_candidate/msp-052-outbound-pairing-contract.md")
        )
        for required in (
            "outbound first-trust eligibility requires both an active bounded pairing window and the exact currently selected candidate SKI",
            "`OPEN_EMPTY` alone describes only the open window and empty inbound slot",
            "private attempt journal may durably bind the exact frozen discovered endpoint and path",
            "`AbortPrepared`, attempt-lease expiry, a protected attempt-helper panic, and restart recovery of an unresolved reservation each synthesize exactly one failure",
            "matching revocation is the only non-failure cancellation",
            "The transport/service stops first",
            "`v0.7.1-helianthus.6`",
            "`v0.6.1-helianthus.6`",
            "`v0.7.1-helianthus.1`",
        ):
            with self.subTest(required=required):
                self.assertIn(required, normalized)

    def test_retry_ready_is_excluded_from_generic_trusted_reconnect(self) -> None:
        contract = compact(
            read("architecture/_candidate/msp-052-outbound-pairing-contract.md")
        )
        for required in (
            "A persisted-trusted remote in the `RETRY_READY` / `RETRYABLE_FAILURE` product is not eligible for generic reconnect",
            "Only an explicit identity-bound `AdminV1.RetryTrusted` admission may authorize one attempt",
            "Fresh mDNS discovery cannot supply or replace that admission",
        ):
            with self.subTest(required=required):
                self.assertIn(required, contract)
        for forbidden in (
            "The current remote service must be either persisted-trusted for reconnect or an actively authorized queued pairing candidate",
            "After restart, a trusted reconnect starts with fresh mDNS discovery",
        ):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, contract)

    def test_policy_rejects_automatic_or_discovery_driven_outbound_routes(self) -> None:
        policy = load_policy_module()
        validator = getattr(policy, "outbound_pairing_contract_errors")
        variants = (
            ("Discovery automatically dials a SHIP peer.", "automatic-outbound"),
            ("An allowlisted S" + "KI triggers a remote connection.", "outbound-initiation"),
            ("Discovery starts pairing with the visible peer.", "outbound-initiation"),
            (
                "Discovery creates a dial job. That job opens a TCP connection.",
                "outbound-initiation",
            ),
        )
        for body, rule in variants:
            with self.subTest(body=body), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                for relative_path in self.OUTBOUND_GUARD_PATHS:
                    page = root / relative_path
                    page.parent.mkdir(parents=True, exist_ok=True)
                    page.write_text(read(relative_path), encoding="utf-8")
                target = root / "architecture/_candidate/msp-052-outbound-pairing-contract.md"
                target.write_text(
                    target.read_text(encoding="utf-8") + f"\n{body}\n",
                    encoding="utf-8",
                )

                errors = validator(root)

            self.assertTrue(any(f"forbidden {rule}" in error for error in errors), errors)

    def test_policy_rejects_endpoint_or_candidate_resurrection(self) -> None:
        policy = load_policy_module()
        validator = getattr(policy, "outbound_pairing_contract_errors")
        variants = (
            "The runtime restores the previous endpoint after restart.",
            "A hostname fallback is used when the observation disappears.",
            "The process reuses a remembered candidate reference.",
            "The runtime retains the endpoint. After restart, it connects to the peer.",
        )
        for body in variants:
            with self.subTest(body=body), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                for relative_path in self.OUTBOUND_GUARD_PATHS:
                    page = root / relative_path
                    page.parent.mkdir(parents=True, exist_ok=True)
                    page.write_text(read(relative_path), encoding="utf-8")
                target = root / "architecture/_candidate/msp-052-outbound-pairing-contract.md"
                target.write_text(
                    target.read_text(encoding="utf-8") + f"\n{body}\n",
                    encoding="utf-8",
                )

                errors = validator(root)

            self.assertTrue(
                any("forbidden outbound-resurrection" in error for error in errors),
                errors,
            )

    def test_policy_rejects_split_selected_candidate_bypasses(self) -> None:
        policy = load_policy_module()
        validator = getattr(policy, "outbound_pairing_contract_errors")
        classifier = getattr(policy, "_selected_candidate_bypass_violation")
        variants = (
            (
                "Recovery is UNPAIRED_LOCKED and the pairing window is active.",
                "It authorizes the outbound attempt.",
            ),
            (
                "The runtime is in OPEN_EMPTY.",
                "The next network attempt is eligible.",
            ),
            (
                "A visible candidate is present.",
                "The transport may initiate the connection.",
            ),
        )
        for left, right in variants:
            body = f"{left} {right}"
            with self.subTest(body=body), tempfile.TemporaryDirectory() as directory:
                self.assertFalse(classifier(left))
                self.assertFalse(classifier(right))
                root = Path(directory)
                for relative_path in self.OUTBOUND_GUARD_PATHS:
                    page = root / relative_path
                    page.parent.mkdir(parents=True, exist_ok=True)
                    page.write_text(read(relative_path), encoding="utf-8")
                target = root / "architecture/_candidate/msp-052-outbound-pairing-contract.md"
                target.write_text(
                    target.read_text(encoding="utf-8") + f"\n{body}\n",
                    encoding="utf-8",
                )

                errors = validator(root)

            self.assertTrue(
                any("forbidden selected-candidate-bypass" in error for error in errors),
                errors,
            )

    def test_policy_rejects_split_persistence_reconnect_and_config_authority(self) -> None:
        policy = load_policy_module()
        validator = getattr(policy, "outbound_pairing_contract_errors")
        resurrection = getattr(policy, "_outbound_resurrection_violation")
        authority = getattr(policy, "_endpoint_authority_violation")
        variants = (
            (
                "The attempt journal records the exact frozen discovered endpoint.",
                "After restart, the runtime reconnects using that record.",
                "outbound-resurrection",
                resurrection,
            ),
            (
                "The candidate_ref remains in process state.",
                "It survives restart.",
                "outbound-resurrection",
                resurrection,
            ),
            (
                "RuntimeConfig remains available.",
                "It supplies the route.",
                "endpoint-authority",
                authority,
            ),
            (
                "The root configuration is consulted.",
                "It provides the WebSocket path.",
                "endpoint-authority",
                authority,
            ),
        )
        for left, right, rule, classifier in variants:
            body = f"{left} {right}"
            with self.subTest(body=body), tempfile.TemporaryDirectory() as directory:
                self.assertFalse(classifier(left))
                self.assertFalse(classifier(right))
                root = Path(directory)
                for relative_path in self.OUTBOUND_GUARD_PATHS:
                    page = root / relative_path
                    page.parent.mkdir(parents=True, exist_ok=True)
                    page.write_text(read(relative_path), encoding="utf-8")
                target = root / "architecture/_candidate/msp-052-outbound-pairing-contract.md"
                target.write_text(
                    target.read_text(encoding="utf-8") + f"\n{body}\n",
                    encoding="utf-8",
                )

                errors = validator(root)

            self.assertTrue(any(f"forbidden {rule}" in error for error in errors), errors)

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
