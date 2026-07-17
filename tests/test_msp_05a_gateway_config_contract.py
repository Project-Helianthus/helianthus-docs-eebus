from __future__ import annotations

import re
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_REL = "architecture/_candidate/msp-05a-gateway-config-scaffold.md"
CONTRACT = ROOT / CONTRACT_REL
ROADMAP = ROOT / "architecture/README.md"


def read_markdown(path: Path) -> tuple[dict[str, str], str]:
    text = path.read_text(encoding="utf-8")
    _, front_matter, body = text.split("---", 2)
    return yaml.safe_load(front_matter), body


def table_rows(body: str, heading: str) -> list[dict[str, str]]:
    matches = list(re.finditer(rf"(?m)^{re.escape(heading)}$", body))
    if len(matches) != 1:
        raise AssertionError(f"{heading} must appear exactly once, got {len(matches)}")
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
        raise AssertionError(f"{heading} does not start with a valid Markdown table")

    rows: list[dict[str, str]] = []
    for line in lines[start + 2 :]:
        if not line.startswith("|"):
            break
        values = cells(line)
        if len(values) != len(headers):
            raise AssertionError(f"{heading} contains a malformed row: {line}")
        rows.append(dict(zip(headers, values, strict=True)))
    return rows


def code_value(value: str) -> str:
    if not (value.startswith("`") and value.endswith("`")):
        raise AssertionError(f"expected one code value, got: {value}")
    return value[1:-1]


class MSP05AGatewayConfigContractTest(unittest.TestCase):
    def contract(self) -> tuple[dict[str, str], str]:
        self.assertTrue(CONTRACT.is_file(), f"missing M5A contract: {CONTRACT_REL}")
        return read_markdown(CONTRACT)

    def test_candidate_metadata_and_issue_authority(self) -> None:
        metadata, body = self.contract()
        self.assertEqual(metadata["publication_status"], "candidate")
        self.assertEqual(metadata["claim_status"], "evidence-backed")
        self.assertEqual(metadata["source_class"], "derived_inference")
        self.assertEqual(metadata["evidence_ids"], "EV-20260711-001")
        self.assertEqual(metadata["hypothesis_status"], "draft")
        for channel in (
            "stable_navigation",
            "search",
            "sitemap",
            "versioned_bundle",
            "release_bundle",
        ):
            self.assertEqual(metadata[channel], "false")
        self.assertIn(
            "https://github.com/Project-Helianthus/helianthus-docs-eebus/issues/34",
            body,
        )

    def test_config_field_matrix_is_exact(self) -> None:
        _, body = self.contract()
        rows = table_rows(body, "## Frozen Configuration Shape")
        got = {
            code_value(row["Go field"]): (
                code_value(row["Go type"]),
                code_value(row["CLI flag"]),
                code_value(row["Default"]),
            )
            for row in rows
        }
        self.assertEqual(
            got,
            {
                "Enabled": ("bool", "--eebus-enabled", "false"),
                "ListenPort": ("uint16", "--eebus-listen-port", "0"),
                "Interfaces": ("[]string", "--eebus-interfaces", "[]"),
                "Subnets": ("[]string", "--eebus-subnets", "[]"),
                "CertificatePath": (
                    "string",
                    "--eebus-certificate-path",
                    "",
                ),
                "PrivateKeyPath": ("string", "--eebus-private-key-path", ""),
                "TrustStorePath": ("string", "--eebus-trust-store-path", ""),
                "RemoteSKIAllowlist": (
                    "[]string",
                    "--eebus-remote-ski-allowlist",
                    "[]",
                ),
                "PairingWindowMode": (
                    "EEBusPairingWindowMode",
                    "--eebus-pairing-window-mode",
                    "closed",
                ),
            },
        )

    def test_parsing_and_normalization_rules_are_closed(self) -> None:
        _, body = self.contract()
        rows = table_rows(body, "## Parsing And Normalization")
        got = {
            code_value(row["Input"]): (
                code_value(row["Normalization"]),
                code_value(row["Invalid result"]),
            )
            for row in rows
        }
        self.assertEqual(
            got,
            {
                "interfaces": ("trim+deduplicate+preserve-order", "flag-error"),
                "subnets": ("trim+netip-prefix+deduplicate+sort", "flag-error"),
                "remote_ski_allowlist": (
                    "trim+lowercase+40-hex+deduplicate+sort",
                    "flag-error",
                ),
                "pairing_window_mode": ("lowercase-enum", "flag-error"),
                "paths": ("trim-only", "flag-error-on-NUL"),
                "listen_port": ("base10-uint16", "flag-error"),
            },
        )
        self.assertIn("`closed` is the only M5A pairing-window value", body)
        self.assertIn("Empty lists never mean all interfaces or all subnets", body)

    def test_phase_ownership_prevents_side_effects(self) -> None:
        _, body = self.contract()
        rows = table_rows(body, "## Phase Ownership")
        got = {
            code_value(row["Concern"]): (
                code_value(row["M5A"]),
                code_value(row["M5B"]),
            )
            for row in rows
        }
        self.assertEqual(
            got,
            {
                "shape-and-CLI-parse": ("owned", "consume"),
                "filesystem-validation": ("forbidden", "required-before-start"),
                "interface-subnet-validation": ("syntax-only", "required-before-bind"),
                "runtime-construction": ("forbidden", "owned"),
                "socket-bind": ("forbidden", "owned"),
                "mdns-advertisement": ("forbidden", "policy-gated"),
                "trust-store-write": ("forbidden", "coordinator-only"),
            },
        )

    def test_disabled_default_and_anti_leak_boundaries_are_explicit(self) -> None:
        _, body = self.contract()
        normalized = " ".join(body.split())
        required = (
            "opens no eeBUS socket",
            "emits no `_ship._tcp`",
            "creates no trust file or directory",
            "starts no eeBUS goroutine",
            "imports no `helianthus-eebusreg` package",
            "does not modify `transportFromConn`",
            "does not modify `protocol.Bus`",
            "does not modify `router.BusEventRouter`",
            "does not modify existing eBUS registry or semantic output",
            "Certificate and private-key contents are never CLI values",
            "M5A cannot assert trust or durable pairing",
        )
        for phrase in required:
            self.assertIn(phrase, normalized)

    def test_rollback_and_roadmap_cross_link(self) -> None:
        _, body = self.contract()
        self.assertIn("## Rollback Ledger", body)
        self.assertIn("Remove the inert `EEBusConfig` scaffold", body)
        roadmap = ROADMAP.read_text(encoding="utf-8")
        self.assertIn("msp-05a-gateway-config-scaffold.md", roadmap)


if __name__ == "__main__":
    unittest.main()
