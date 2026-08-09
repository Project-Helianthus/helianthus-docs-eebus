from __future__ import annotations

import ipaddress
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "architecture" / "_candidate" / "ha-addon-runtime-wiring.md"
EVIDENCE = ROOT / "evidence" / "EV-20260809-001.md"


def restart_evidence_redaction_violations(text: str) -> set[str]:
    violations: set[str] = set()
    for candidate in re.findall(r"(?<![0-9.])(?:[0-9]{1,3}\.){3}[0-9]{1,3}(?![0-9.])", text):
        try:
            if ipaddress.ip_address(candidate).is_private:
                violations.add("private-ipv4")
        except ValueError:
            continue

    for candidate in re.findall(
        r"(?<![0-9A-Fa-f:])(?:[0-9A-Fa-f]{0,4}:){2,}[0-9A-Fa-f]{0,4}"
        r"(?:%[A-Za-z0-9_.-]+)?(?![0-9A-Fa-f:])",
        text,
    ):
        try:
            address = ipaddress.ip_address(candidate.split("%", 1)[0])
            if address.version == 6 and (address.is_private or address.is_link_local):
                violations.add("private-ipv6")
        except ValueError:
            continue

    sensitive_labels = (
        "container" + r"(?:_id)?",
        "machine" + r"(?:_id)?",
        "image" + r"(?:_id|_digest)?",
        "manifest" + r"(?:_[ab])?(?:_sha256|_hash)?",
        "trust" + r"(?:_store|_manifest)?(?:_path|_hash|_bytes)?",
        "private" + r"_artifact(?:_path|_location|_hash)?",
        "ship" + r"_id",
    )
    labeled_value = re.compile(
        rf"(?i)\b(?:{'|'.join(sensitive_labels)})\b\s*[:=]\s*[^\s,;`]+"
    )
    if labeled_value.search(text):
        violations.add("labeled-protected-value")

    patterns = {
        "stable-fingerprint": r"(?i)\b[0-9a-f]{40}\b",
        "protected-digest-or-identifier": r"(?i)\b(?:sha256:)?[0-9a-f]{64}\b",
        "canonical-ship" + "-id": r"(?i)\bHLS-[0-9a-f]{32}\b",
        "numeric-ship" + "-id": r"\b[0-9]{20,}[A-Za-z0-9]*\b",
        "spine-address": r"(?<![A-Za-z0-9_])d:[^\s`]+",
        "mac-address": r"(?i)\b(?:[0-9a-f]{2}:){5}[0-9a-f]{2}\b",
        "private-key": r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE " + r"KEY-----",
        "credential-token": (
            r"(?i)(?:authorization:\s*bearer\s+\S+|\b(?:access_|refresh_)?token\s*[:=]\s*"
            r"[A-Za-z0-9._~-]{16,}|\b(?:api_key|credential)\s*[:=]\s*[A-Za-z0-9._~-]{16,})"
        ),
        "private-artifact-locator": r"(?<![A-Za-z0-9_])(?:/mnt)?/data/[A-Za-z0-9._/-]+",
        "candidate-ref": r"\bcandidate" + r"_ref\b",
    }
    for name, pattern in patterns.items():
        if re.search(pattern, text):
            violations.add(name)
    return violations


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
        self.assertEqual(restart_evidence_redaction_violations(evidence), set())

    def test_restart_evidence_redaction_rejects_each_protected_class(self) -> None:
        evidence = EVIDENCE.read_text(encoding="utf-8")
        synthetic_mutations = {
            "private-ipv4": ("private-ipv4", "host=" + ".".join(("192", "168", "10", "4"))),
            "private-ipv6": ("private-ipv6", "host=" + "fd00" + "::1234"),
            "stable-fingerprint": ("stable-fingerprint", "ski=" + ("a" * 40)),
            "container-short-id": (
                "labeled-protected-value",
                "container" + "_id=" + "ab12" + "cd34" + "ef56",
            ),
            "machine-identifier": (
                "labeled-protected-value",
                "machine" + "_id=synthetic-host-id",
            ),
            "image-identifier": (
                "labeled-protected-value",
                "image" + "_id=sha256:deadbeef",
            ),
            "image-digest": (
                "protected-digest-or-identifier",
                "image=sha256:" + ("c" * 64),
            ),
            "trust-manifest-hash": (
                "labeled-protected-value",
                "trust" + "_manifest_hash=synthetic-trust-hash",
            ),
            "trust-store-locator": (
                "labeled-protected-value",
                "trust" + "_store_path=/var/lib/synthetic/trust.json",
            ),
            "private-artifact" + "-hash": (
                "labeled-protected-value",
                "private" + "_artifact_hash=synthetic-artifact-hash",
            ),
            "private-artifact" + "-labeled-locator": (
                "labeled-protected-value",
                "private" + "_artifact_path=/" + "Users/example/operator.json",
            ),
            "canonical-ship" + "-id": (
                "canonical-ship" + "-id",
                "HLS-" + ("1" * 32),
            ),
            "opaque-ship" + "-id": (
                "labeled-protected-value",
                "ship" + "_id=opaque-synthetic-peer",
            ),
            "numeric-ship" + "-id": (
                "numeric-ship" + "-id",
                "ship" + "_id=12345678901234567890TEST",
            ),
            "spine-address": ("spine-address", "feature=d:synthetic_peer:[1]:4"),
            "mac-address": ("mac-address", "interface=" + ":".join(("02", "00", "00", "00", "00", "01"))),
            "generic-private-key": ("private-key", "-----BEGIN PRIVATE " + "KEY-----"),
            "rsa-private-key": ("private-key", "-----BEGIN RSA PRIVATE " + "KEY-----"),
            "ec-private-key": ("private-key", "-----BEGIN EC PRIVATE " + "KEY-----"),
            "openssh-private-key": (
                "private-key",
                "-----BEGIN OPENSSH PRIVATE " + "KEY-----",
            ),
            "bearer-token": (
                "credential-token",
                "Authorization:" + " Bearer synthetic-token-value-1234",
            ),
            "access-token": (
                "credential-token",
                "access" + "_token=synthetic-token-value-1234",
            ),
            "refresh-token": (
                "credential-token",
                "refresh" + "_token=synthetic-token-value-1234",
            ),
            "api" + "-key": (
                "credential-token",
                "api" + "_key=synthetic-api-value-1234",
            ),
            "private-artifact" + "-locator": ("private-artifact-locator", "/mnt" + "/data/private/operator.json"),
            "candidate" + "-ref": ("candidate-ref", "candidate" + "_ref=synthetic"),
        }
        for scenario, (expected_violation, mutation) in synthetic_mutations.items():
            with self.subTest(scenario=scenario):
                self.assertIn(
                    expected_violation,
                    restart_evidence_redaction_violations(f"{evidence}\n{mutation}\n"),
                    msg=f"mutation for {scenario} was not rejected by {expected_violation}",
                )

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
