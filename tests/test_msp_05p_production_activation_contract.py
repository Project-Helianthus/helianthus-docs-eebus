from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "architecture" / "_candidate" / "msp-05p-production-activation.md"


def mapping_fields(text: str) -> list[str]:
    section = text.split("## Gateway To Runtime Mapping", 1)[1].split("\n## ", 1)[0]
    return re.findall(r"(?m)^\| `([A-Za-z0-9_]+)` \|", section)


class MSP05PProductionActivationContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.text = CONTRACT.read_text(encoding="utf-8")
        cls.compact = " ".join(cls.text.split())

    def test_gateway_mapping_is_single_and_lossless(self) -> None:
        self.assertEqual(
            mapping_fields(self.text),
            [
                "Enabled",
                "ListenPort",
                "Interfaces",
                "Subnets",
                "StateRoot",
                "DiscoveryEnabled",
                "RemoteSKIAllowlist",
                "PairingWindowMode",
            ],
        )

    def test_no_compatibility_or_material_path_mapping_remains(self) -> None:
        for forbidden in (
            "CertificatePath",
            "PrivateKeyPath",
            "TrustStorePath",
            "source compatibility",
            "legacy material",
            "fallback or migration",
            "configured endpoint",
            "QueueRemoteSKI",
            "ReportRemoteEndpoint",
        ):
            self.assertNotIn(forbidden, self.text)

    def test_activation_preserves_identity_ownership(self) -> None:
        for required in (
            "StateRoot is the sole protected identity and trust root input",
            "RemoteSKIAllowlist remains authorization policy only",
            "cannot create observed remote state",
            "listener_start",
            "discovery_publish",
        ):
            self.assertIn(required, self.compact)

    def test_activation_does_not_claim_support(self) -> None:
        self.assertIn("not a supported runtime", self.text)
        self.assertIn("live validation remains pending", self.text)


if __name__ == "__main__":
    unittest.main()
