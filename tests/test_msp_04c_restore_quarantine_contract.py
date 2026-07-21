from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "architecture" / "_candidate" / "msp-04c-restore-revocation-quarantine-repair.md"


class MSP04CRestoreQuarantineContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.text = CONTRACT.read_text(encoding="utf-8")
        cls.compact = " ".join(cls.text.split())

    def test_scope_retains_restore_revocation_quarantine_and_repair_only(self) -> None:
        self.assertIn("Restore, Revocation, Quarantine, And Identity Repair Contract", self.text)
        for heading in (
            "## Ownership Boundary",
            "## Startup And Restore",
            "## Revocation",
            "## Persistent Quarantine",
            "## Host-Key And Certificate Repair",
            "## Observation And Evidence Boundary",
        ):
            self.assertIn(heading, self.text)

    def test_endpoint_forced_outbound_contract_is_absent(self) -> None:
        for forbidden in (
            "Outgoing Attempt Gate",
            "Durable Outgoing Attempt Reservation",
            "DialContext",
            "gatedDialContext",
            "endpoint_path",
            "endpoint_fallback",
            "QueueRemoteSKI",
            "ReportRemoteEndpoint",
            "explicit contract migration",
            "compatibility path",
        ):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, self.text)

    def test_repair_preserves_store_instance_and_ship_id(self) -> None:
        for required in (
            "real host-key and certificate repair",
            "certificate SKI MUST change",
            "raw 32-byte `StoreInstance` MUST remain byte-for-byte unchanged",
            "`nodeToken` MUST remain exactly unchanged",
            "canonical SHIP ID MUST remain exactly unchanged",
            "repair_identity_mismatch",
        ):
            self.assertIn(required, self.compact)

    def test_policy_and_observation_remain_separate_after_restart(self) -> None:
        for required in (
            "Durable trust and authorization records are policy only",
            "mDNS callback may create a visible service",
            "connection callback may create a session",
            "transport-backed pairing callback may create a candidate",
            "creates no remote row",
        ):
            self.assertIn(required, self.compact)

    def test_security_and_privacy_fail_closed(self) -> None:
        for required in (
            "tombstone",
            "ADMIN_HOLD",
            "same-effective-UID",
            "no public mutation",
            "raw and redacted",
            "no semantic promotion",
        ):
            self.assertIn(required, self.text)


if __name__ == "__main__":
    unittest.main()
