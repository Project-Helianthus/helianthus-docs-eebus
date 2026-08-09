from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "architecture" / "_candidate" / "ha-addon-runtime-wiring.md"
EVIDENCE = ROOT / "evidence" / "EV-20260809-001.md"


class HAAddonRuntimeWiringTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.text = CONTRACT.read_text(encoding="utf-8")
        cls.compact = " ".join(cls.text.split())

    def test_complete_addon_to_gateway_mapping_is_explicit(self) -> None:
        rows = re.findall(r"(?m)^\| `([^`]+)` \| `([^`]+)` \|", self.text)
        self.assertEqual(
            rows,
            [
                ("eebus_enabled", "--eebus-enabled"),
                ("eebus_listen_port", "--eebus-listen-port"),
                ("eebus_interface", "--eebus-interfaces"),
                ("eebus_subnets", "--eebus-subnets"),
                ("eebus_discovery_enabled", "--eebus-discovery-enabled"),
                ("eebus_remote_ski_allowlist", "--eebus-remote-ski-allowlist"),
            ],
        )

    def test_state_and_pairing_policy_are_fixed(self) -> None:
        self.assertIn("`--eebus-state-root=/data/eebus`", self.text)
        self.assertIn("`--eebus-pairing-window-mode=closed`", self.text)
        self.assertIn("neither value is operator-configurable", self.compact)

    def test_disabled_and_invalid_configuration_fail_closed(self) -> None:
        self.assertIn("emits no `--eebus-*` argument", self.text)
        for phrase in (
            "every required eeBUS flag",
            "blank interface",
            "empty subnet set",
            "invalid listen port",
            "invalid allowlist",
            "never silently drops",
        ):
            self.assertIn(phrase, self.compact)

    def test_restart_gate_requires_container_recreation_and_identity_reload(self) -> None:
        for phrase in (
            "full add-on restart",
            "image-owned wrapper",
            "same host-bound machine identity, local certificate identity",
            "trusted peer identity, observed",
            "protocol-service identity, and pairing state",
            "without a new trust action",
            "remote session reconnects",
            "service-only restart",
        ):
            self.assertIn(phrase, self.compact)

        self.assertIn("`EV-20260809-001`", self.text)

    def test_restart_evidence_is_redacted_and_records_the_observed_gate(self) -> None:
        evidence = EVIDENCE.read_text(encoding="utf-8")
        compact = " ".join(evidence.split())
        for phrase in (
            "different container from the same candidate image",
            "same redacted peer was paired and visible",
            "one SHIP session returned to `connected`",
            "| Remote protocol devices | 1 |",
            "| Entities | 11 |",
            "| Features | 20 |",
            "| Use-case claims | 22 |",
            "`mask_tier=raw`",
            "`mask_tier=redacted`",
            "both failed with `permission_denied`",
            "does not claim a simultaneous live eBUS transport smoke test",
        ):
            self.assertIn(phrase, compact)

    def test_host_bound_key_identity_survives_without_identity_logging(self) -> None:
        for phrase in (
            "deterministic container machine identity",
            "using this frozen algorithm",
            "preserves access to host-bound key material",
            "Neither the interface identity nor the derived machine identity is logged",
        ):
            self.assertIn(phrase, self.compact)
        for exact in (
            "`/sys/class/net/<eebus_interface>/address`",
            "`[A-Za-z0-9_.:-]+`",
            "`helianthus-eebusreg-ha-v1:`",
            "synthetic normalized interface identity `020000000001`",
            "`helianthus-eebusreg-ha-v1:020000000001`",
            "`8a4c331847003c7bacbfa7f2f383cc8b49126d9b1ad071cf97a4ab39c6d12f7c`",
            "`/etc/machine-id`",
            "`0444`",
        ):
            self.assertIn(exact, self.text)

    def test_cached_supervisor_schema_fallback_is_bounded_and_fail_closed(self) -> None:
        for phrase in (
            "cached pre-eeBUS schema",
            "only an eeBUS field whose normal configuration lookup is missing or null",
            "MUST NOT replace a non-empty lookup value",
            "recover non-eeBUS fields through this path",
            "bypass any validation",
            "fails identically to the normal configuration path",
            "Fallback decoding preserves JSON presence and type",
            "JSON `null` means absent",
            "string `\"null\"` remains a string",
            "MUST match the types declared by the add-on schema",
            "`-flag=value` argument",
            "ignore later trust or identity options",
            "containing U+0000 MUST be rejected",
            "before shell capture",
            "shell command substitution removes NUL bytes",
            "MUST be JSON-type checked before any",
            "`bashio::config` capture",
            "normal and cached-schema paths",
        ):
            self.assertIn(phrase, self.compact)

    def test_raw_operator_and_public_redacted_boundaries_remain_separate(self) -> None:
        for phrase in (
            "`mask_tier=raw`",
            "`eebus.raw.read`",
            "Public HTTP MCP remains redacted",
            "cannot dereference a raw snapshot",
            "No tier exposes private keys",
            "public evidence replaces them with redacted references",
        ):
            self.assertIn(phrase, self.text)

    def test_consumer_and_version_scope_does_not_expand(self) -> None:
        self.assertIn("does not add a Home Assistant entity", self.compact)
        self.assertIn("v2 namespace", self.compact)
        self.assertIn("compatibility path", self.compact)


if __name__ == "__main__":
    unittest.main()
