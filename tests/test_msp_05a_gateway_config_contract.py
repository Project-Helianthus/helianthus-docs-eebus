from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "architecture" / "_candidate" / "msp-05a-gateway-config-scaffold.md"


def table_fields(text: str, heading: str) -> list[str]:
    section = text.split(heading, 1)[1].split("\n## ", 1)[0]
    return re.findall(r"(?m)^\| `([A-Za-z0-9_]+)` \|", section)


class MSP05AGatewayConfigContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.text = CONTRACT.read_text(encoding="utf-8")
        cls.compact = " ".join(cls.text.split())

    def test_frozen_shape_has_one_current_configuration_product(self) -> None:
        self.assertEqual(
            table_fields(self.text, "## Frozen Configuration Shape"),
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

    def test_removed_material_and_remote_endpoint_fields_do_not_survive(self) -> None:
        for forbidden in (
            "CertificatePath",
            "PrivateKeyPath",
            "TrustStorePath",
            "QueueRemoteSKI",
            "ReportRemoteEndpoint",
            "configured endpoint",
            "source-compatible",
            "compatibility fields",
            "migration",
        ):
            self.assertNotIn(forbidden, self.text)

    def test_state_root_and_allowlist_have_separate_ownership(self) -> None:
        self.assertIn("`StateRoot` is the sole protected identity and trust root input", self.compact)
        self.assertIn("RemoteSKIAllowlist is authorization policy only", self.compact)
        self.assertIn("cannot create a service, session, topology row, or pairing candidate", self.compact)

    def test_disabled_default_has_no_effect(self) -> None:
        for required in (
            "opens no eeBUS socket",
            "emits no `_ship._tcp`",
            "creates no trust file or directory",
            "starts no eeBUS goroutine",
        ):
            self.assertIn(required, self.text)


if __name__ == "__main__":
    unittest.main()
