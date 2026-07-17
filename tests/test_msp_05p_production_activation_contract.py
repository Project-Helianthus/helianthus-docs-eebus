from __future__ import annotations

import re
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
ARCH_REL = "architecture/_candidate/msp-05p-production-activation.md"
PROTOCOL_REL = "protocols/_candidate/msp-05p-scoped-ship-listener.md"
API_REL = "api/_candidate/msp-05p-eebusruntime-v2.md"
M5A_REL = "architecture/_candidate/msp-05a-gateway-config-scaffold.md"
ARCH = ROOT / ARCH_REL
PROTOCOL = ROOT / PROTOCOL_REL
API = ROOT / API_REL
M5A = ROOT / M5A_REL


def read_markdown(path: Path) -> tuple[dict[str, str], str]:
    text = path.read_text(encoding="utf-8")
    _, front_matter, body = text.split("---", 2)
    metadata = yaml.safe_load(front_matter)
    if not isinstance(metadata, dict):
        raise AssertionError(f"{path} front matter must be a mapping")
    return metadata, body


def table_rows(body: str, heading: str) -> list[dict[str, str]]:
    matches = list(re.finditer(rf"(?m)^{re.escape(heading)}$", body))
    if len(matches) != 1:
        raise AssertionError(f"{heading} must appear exactly once")
    section = body[matches[0].end() :]
    next_heading = re.search(r"(?m)^#{1,6} .+$", section)
    lines = section[: next_heading.start() if next_heading else None].splitlines()
    start = next(index for index, line in enumerate(lines) if line.startswith("|"))

    def cells(line: str) -> list[str]:
        return [cell.strip() for cell in line.strip("|").split("|")]

    headers = cells(lines[start])
    separator = cells(lines[start + 1])
    if len(headers) != len(separator) or not all(
        re.fullmatch(r":?-{3,}:?", cell) for cell in separator
    ):
        raise AssertionError(f"{heading} has an invalid Markdown table")
    rows: list[dict[str, str]] = []
    for line in lines[start + 2 :]:
        if not line.startswith("|"):
            break
        values = cells(line)
        if len(values) != len(headers):
            raise AssertionError(f"{heading} contains a malformed row: {line}")
        rows.append(dict(zip(headers, values, strict=True)))
    return rows


def code(value: str) -> str:
    if not (value.startswith("`") and value.endswith("`")):
        raise AssertionError(f"expected one code value, got {value!r}")
    return value[1:-1]


class MSP05PProductionActivationContractTest(unittest.TestCase):
    def require_contracts(self) -> None:
        missing = [
            relative
            for relative, path in (
                (ARCH_REL, ARCH),
                (PROTOCOL_REL, PROTOCOL),
                (API_REL, API),
            )
            if not path.is_file()
        ]
        self.assertEqual(missing, [], f"missing MSP-DOCS-05P contracts: {missing}")

    def test_candidate_metadata_and_publication_confinement(self) -> None:
        self.require_contracts()
        for relative, path, domain in (
            (ARCH_REL, ARCH, "architecture"),
            (PROTOCOL_REL, PROTOCOL, "protocols"),
            (API_REL, API, "api"),
        ):
            with self.subTest(relative=relative):
                metadata, body = read_markdown(path)
                self.assertEqual(metadata["publication_status"], "candidate")
                self.assertEqual(metadata["claim_status"], "evidence-backed")
                self.assertEqual(metadata["source_class"], "derived_inference")
                self.assertEqual(metadata["hypothesis_status"], "draft")
                self.assertEqual(metadata["owner_domain"], domain)
                for channel in (
                    "stable_navigation",
                    "search",
                    "sitemap",
                    "versioned_bundle",
                    "release_bundle",
                ):
                    self.assertEqual(metadata[channel], "false")
                self.assertIn(
                    "https://github.com/Project-Helianthus/helianthus-docs-eebus/issues/36",
                    body,
                )
        for relative in (
            "README.md",
            "architecture/README.md",
            "api/search-index.json",
            "api/sitemap.xml",
            "api/versioned-bundle.txt",
            "api/release-bundle.txt",
        ):
            text = (ROOT / relative).read_text(encoding="utf-8")
            self.assertNotIn(ARCH_REL, text)
            self.assertNotIn(PROTOCOL_REL, text)
            self.assertNotIn(API_REL, text)

    def test_gateway_mapping_is_lossless_and_fail_closed(self) -> None:
        self.require_contracts()
        _, body = read_markdown(ARCH)
        rows = table_rows(body, "## Gateway To Runtime Mapping")
        got = {
            code(row["Gateway input"]): (
                code(row["Runtime v2 input"]),
                code(row["Rule"]),
            )
            for row in rows
        }
        self.assertEqual(
            got,
            {
                "Enabled": ("Enabled", "direct"),
                "ListenPort": ("ListenAddress.port", "required-1..65535"),
                "Interfaces": ("Interface", "exactly-one"),
                "Subnets": ("ListenAddress.addr", "resolve-exactly-one"),
                "StateRoot": ("StateRoot", "required-absolute-protected"),
                "DiscoveryEnabled": ("DiscoveryEnabled", "direct-default-false"),
                "RemoteSKIAllowlist": ("Remotes", "lossless-sorted"),
                "PairingWindowMode": ("PairingPolicy", "closed-only"),
                "CertificatePath": ("unsupported", "must-be-empty"),
                "PrivateKeyPath": ("unsupported", "must-be-empty"),
                "TrustStorePath": ("unsupported", "must-be-empty"),
            },
        )
        normalized = " ".join(body.split())
        for phrase in (
            "zero or multiple interfaces",
            "zero or multiple matching addresses",
            "unspecified, multicast, or wildcard address",
            "must fail before runtime construction",
            "does not alias a legacy path to `StateRoot`",
            "does not silently discard a configured field",
        ):
            self.assertIn(phrase, normalized)

        _, m5a_body = read_markdown(M5A)
        m5a_fields = {
            code(row["Go field"])
            for row in table_rows(m5a_body, "## Frozen Configuration Shape")
        }
        self.assertNotIn("StateRoot", m5a_fields)
        self.assertNotIn("DiscoveryEnabled", m5a_fields)
        m5a_normalized = " ".join(m5a_body.split())
        for phrase in (
            "MSP-05P production contract supersedes the earlier M5B activation handoff",
            "`StateRoot` and `DiscoveryEnabled` are deliberate `MSP-05A-R1` additions",
            "legacy certificate, private-key, and trust-store path fields remain source-compatible but must be empty",
            "They are not aliases for `StateRoot`",
        ):
            self.assertIn(phrase, m5a_normalized)

    def test_activation_order_and_error_precedence_prevent_partial_effects(self) -> None:
        self.require_contracts()
        _, body = read_markdown(ARCH)
        stages = table_rows(body, "## Activation Order")
        self.assertEqual(
            [code(row["Stage"]) for row in stages],
            [
                "configuration_validation",
                "disabled_gate",
                "state_root_validation",
                "protected_material_load",
                "trust_state_load",
                "service_construction",
                "listener_start",
                "discovery_publish",
                "ready_publish",
            ],
        )
        precedence = table_rows(body, "## Error Precedence")
        self.assertEqual(
            [code(row["Error class"]) for row in precedence],
            [
                "invalid_configuration",
                "disabled",
                "unsafe_state_root",
                "protected_material_unavailable",
                "trust_state_unavailable",
                "listener_unavailable",
                "discovery_unavailable",
            ],
        )
        normalized = " ".join(body.split())
        for phrase in (
            "No later stage runs after the first failure",
            "closes every effect opened by an earlier stage exactly once",
            "no socket, goroutine, publication, or partial durable mutation remains",
            "Shutdown is idempotent",
        ):
            self.assertIn(phrase, normalized)

    def test_listener_and_discovery_are_independent_exact_scope_controls(self) -> None:
        self.require_contracts()
        _, body = read_markdown(PROTOCOL)
        rows = table_rows(body, "## Listener And Discovery Policy Matrix")
        got = {
            (code(row["Listener requested"]), code(row["Discovery requested"])): (
                code(row["Socket result"]),
                code(row["mDNS result"]),
            )
            for row in rows
        }
        self.assertEqual(
            got,
            {
                ("false", "false"): ("none", "none"),
                ("true", "false"): ("exact-address", "none"),
                ("true", "true"): ("exact-address", "publish-after-bind"),
                ("false", "true"): ("reject", "none"),
            },
        )
        normalized = " ".join(body.split())
        for phrase in (
            "never binds an unspecified or wildcard address",
            "advertised address and port equal the bound endpoint",
            "publication starts only after a successful bind",
            "withdrawal with `TTL=0`",
            "initial publication failure rolls back the listener",
            "post-ready discovery loss is explicit `missing-discovery` degradation",
            "does not imply an open pairing window",
            "post-ready discovery loss retains the exact listener and established sessions",
            "cannot report ready or empty success, widen the listener, open pairing, accept new trust, or terminate an established session",
            "candidate safety constraints, not observed requirements",
        ):
            self.assertIn(phrase, normalized)

    def test_additive_v2_api_preserves_v1_and_hides_dependencies(self) -> None:
        self.require_contracts()
        _, body = read_markdown(API)
        rows = table_rows(body, "## Candidate Public Additions")
        got = {code(row["Public name"]): code(row["Shape"]) for row in rows}
        self.assertEqual(
            got,
            {
                "ConfigV2": "struct",
                "ListenAddress": "netip.AddrPort",
                "DiscoveryEnabled": "bool",
                "PairingPolicy": "PairingPolicyV2",
                "PairingPolicyV2": "string",
                "PairingPolicyV2Closed": "constant",
                "NewV2": "func(ConfigV2)(Runtime,error)",
            },
        )
        normalized = " ".join(body.split())
        for phrase in (
            "`Config`, `Remote`, `Runtime`, and `New` remain source compatible",
            "enabled v1 behavior remains fail closed",
            "gateway production activation uses `NewV2` only",
            "no `enbility`, `ship-go`, `spine-go`, WebSocket, mDNS, certificate-provider, or store implementation type",
            "standard-library `net/netip.AddrPort`",
            "No public trust or pairing mutation is added",
        ):
            self.assertIn(phrase, normalized)

        go_blocks = re.findall(r"```go\n(.*?)\n```", body, flags=re.DOTALL)
        self.assertEqual(len(go_blocks), 1)
        self.assertEqual(
            " ".join(go_blocks[0].split()),
            " ".join(
                """type PairingPolicyV2 string

const PairingPolicyV2Closed PairingPolicyV2 = "closed"

type ConfigV2 struct {
    Enabled bool
    StateRoot string
    Interface string
    ListenAddress netip.AddrPort
    DiscoveryEnabled bool
    Remotes []Remote
    PairingPolicy PairingPolicyV2
}

func NewV2(config ConfigV2) (Runtime, error)""".split()
            ),
        )

    def test_identity_trust_and_secret_boundaries_remain_closed(self) -> None:
        self.require_contracts()
        _, body = read_markdown(ARCH)
        normalized = " ".join(body.split())
        for phrase in (
            "`0700` directory and `0600` regular files",
            "no symlink, traversal, device, FIFO, or socket",
            "atomic replace and directory `fsync`",
            "host-bound or explicitly backup-excluded key",
            "wrong-host restore and cloned state fail before listener or mDNS",
            "certificate, private key, local SKI, remote SKI, remote SHIP ID, and pairing state survive restart",
            "secrets never appear in environment, argv, logs, snapshots, metrics, traces, or public errors",
            "unknown peer cannot persist trust while pairing is closed",
            "one ephemeral candidate and OOB fingerprint confirmation",
            "no persistent write before confirmation",
        ):
            self.assertIn(phrase, normalized)

    def test_disabled_default_anti_leak_and_rollback_are_explicit(self) -> None:
        self.require_contracts()
        bodies = [read_markdown(path)[1] for path in (ARCH, PROTOCOL, API)]
        normalized = " ".join(" ".join(bodies).split())
        for phrase in (
            "disabled default performs no runtime construction, filesystem access, goroutine, socket, or mDNS operation",
            "does not modify `transportFromConn`, `protocol.Bus`, or `router.BusEventRouter`",
            "no `eebus.v1`, `ebus.v1`, GraphQL, Portal, Home Assistant, command, raw-write, or promoted-semantic surface",
            "remove the additive v2 contract and retain v1 unchanged",
            "remove listener/discovery policy additions and retain the legacy constructor",
            "withdraw this candidate before any dependent code merge",
        ):
            self.assertIn(phrase, normalized)


if __name__ == "__main__":
    unittest.main()
