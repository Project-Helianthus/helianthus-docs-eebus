from __future__ import annotations

import hashlib
import re
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
STABLE_PROTOCOL = "protocols/ship-spine-overview.md"
PROTOCOL_CANDIDATE = "protocols/_candidate/msp-052-outbound-endpoint-selection.md"
ARCHITECTURE_CANDIDATE = (
    "architecture/_candidate/msp-052-outbound-pairing-contract.md"
)
EVIDENCE = "evidence/EV-20260726-001.md"
TOKEN_PATTERN = re.compile(r"[a-z0-9]+", re.IGNORECASE)
SECTION_PATTERN = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)


def read(relative: str) -> str:
    return (REPO / relative).read_text(encoding="utf-8")


def section(text: str, heading: str) -> str:
    matches = list(SECTION_PATTERN.finditer(text))
    for index, match in enumerate(matches):
        if match.group(1).casefold() != heading.casefold():
            continue
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        return text[start:end]
    raise AssertionError(f"missing section: {heading}")


def semantic_tokens(text: str) -> tuple[str, ...]:
    return tuple(token.casefold() for token in TOKEN_PATTERN.findall(text))


def metadata_value(text: str, label: str) -> str:
    match = re.search(
        rf"^-\s+{re.escape(label)}:\s*(.+?)\s*$",
        text,
        re.IGNORECASE | re.MULTILINE,
    )
    if match is None:
        raise AssertionError(f"missing metadata field: {label}")
    return match.group(1)


class Issue64ShipEndpointOrderContractTests(unittest.TestCase):
    def assert_tokens(self, text: str, required: set[str]) -> None:
        actual = set(semantic_tokens(text))
        self.assertFalse(required - actual, f"missing semantic tokens: {required - actual}")

    def assert_markers_ordered(self, text: str, markers: tuple[str, ...]) -> None:
        normalized = " ".join(text.casefold().split())
        positions = [normalized.find(marker.casefold()) for marker in markers]
        self.assertNotIn(-1, positions, f"missing ordered marker: {markers}")
        self.assertEqual(positions, sorted(positions))

    def test_stable_protocol_invariant_remains_byte_identical(self) -> None:
        digest = hashlib.sha256((REPO / STABLE_PROTOCOL).read_bytes()).hexdigest()
        self.assertEqual(
            digest,
            "734c5668cd1937b088cbb12c7c4dd6b78c0fc76cc76873dc2d49092aded65b3b",
        )

    def test_endpoint_order_uses_only_canonical_mdns_observation_addresses(self) -> None:
        protocol = read(PROTOCOL_CANDIDATE)
        endpoint_order = section(protocol, "Candidate Endpoint Order")

        self.assert_markers_ordered(
            endpoint_order,
            (
                "unique canonical IPv4",
                "unique canonical IPv6",
                "observed hostname",
            ),
        )
        self.assert_tokens(
            endpoint_order,
            {
                "nil",
                "canonicalized",
                "ipv4",
                "ipv6",
                "duplicates",
                "first",
                "seen",
                "hostname",
                "fallback",
            },
        )
        self.assertRegex(
            " ".join(endpoint_order.split()),
            r"4-byte.+16-byte.+one address",
        )
        self.assert_tokens(
            endpoint_order,
            {
                "selected",
                "mdns",
                "observation",
                "sole",
                "endpoint",
                "address",
                "input",
                "configured",
                "cannot",
                "replace",
                "prepend",
                "supplement",
            },
        )

        endpoint_lower = " ".join(endpoint_order.casefold().split())
        contradictions = (
            r"configured service address (?:is|may be) (?:attempted|preferred|used)",
            r"service address .{0,40} before .{0,40} observation",
            r"observation addresses .{0,40} replaced by",
        )
        for pattern in contradictions:
            with self.subTest(pattern=pattern):
                self.assertIsNone(re.search(pattern, endpoint_lower))

        falsifier = protocol.split("---", 2)[1]
        self.assert_tokens(
            falsifier,
            {
                "configured",
                "service",
                "address",
                "replace",
                "prepend",
                "supplement",
                "observation",
            },
        )

    def test_path_order_and_attempt_authorization_are_independent(self) -> None:
        protocol = read(PROTOCOL_CANDIDATE)
        endpoint_order = section(protocol, "Candidate Endpoint Order")
        dial_boundary = section(protocol, "Discovery, Authorization, And Dial")
        architecture_endpoint = section(
            read(ARCHITECTURE_CANDIDATE),
            "Endpoint And Trust Boundaries",
        )

        self.assert_markers_ordered(endpoint_order, ("observed path", "empty path"))
        self.assert_tokens(
            endpoint_order,
            {"observed", "path", "empty", "root", "url", "fallback", "second"},
        )
        self.assert_tokens(
            dial_boundary,
            {
                "gate",
                "authorize",
                "exact",
                "endpoint",
                "path",
                "permit",
                "separately",
            },
        )
        self.assert_tokens(
            architecture_endpoint,
            {
                "authorization",
                "permit",
                "observed",
                "path",
                "transfer",
                "empty",
                "endpoint",
            },
        )

        scoped_contract = "\n".join((endpoint_order, dial_boundary)).casefold()
        contradictions = (
            r"exact observed path",
            r"path is never .{0,40} default",
            r"only the observed path",
            r"empty path .{0,30} (?:forbidden|prohibited|skipped)",
        )
        for pattern in contradictions:
            with self.subTest(pattern=pattern):
                self.assertIsNone(re.search(pattern, scoped_contract))

    def test_protocol_keeps_eligibility_concise_and_architecture_owns_authority(self) -> None:
        protocol = read(PROTOCOL_CANDIDATE)
        eligibility = section(protocol, "Eligibility Precondition")
        discovery_dial = section(protocol, "Discovery, Authorization, And Dial")
        architecture_endpoint = section(
            read(ARCHITECTURE_CANDIDATE),
            "Endpoint And Trust Boundaries",
        )

        self.assert_tokens(
            eligibility,
            {
                "eligibility",
                "persisted",
                "trusted",
                "reconnect",
                "authorized",
                "queued",
                "pairing",
                "mdns",
                "observation",
                "grants",
                "authority",
                "cannot",
                "create",
                "already",
                "exists",
                "callback",
                "trigger",
                "schedule",
                "connection",
                "initiation",
                "gate",
                "dial",
            },
        )
        self.assert_tokens(
            discovery_dial,
            {
                "mdns",
                "callback",
                "eligibility",
                "already",
                "exists",
                "trigger",
                "schedule",
                "connection",
                "initiation",
                "grant",
                "authority",
                "bypass",
                "gate",
            },
        )
        self.assertIn(
            "../../architecture/_candidate/msp-052-outbound-pairing-contract.md",
            eligibility,
        )
        for lifecycle_detail in (
            "RegisterRemoteSKI",
            "UNPAIRED_LOCKED",
            "candidate SKI",
            "transient trust",
        ):
            with self.subTest(lifecycle_detail=lifecycle_detail):
                self.assertNotIn(lifecycle_detail.casefold(), eligibility.casefold())

        scoped_discovery = "\n".join(
            (eligibility, discovery_dial, architecture_endpoint)
        ).casefold()
        discovery_alone_contradictions = (
            r"(?:mdns|discovery)[^.]{0,100}\bgrants?\s+(?!no\b)(?:authority|eligibility)",
            r"(?:mdns|discovery)[^.]{0,100}\bcreates?\s+(?!no\b)(?:authority|eligibility)",
            r"(?:mdns|discovery)[^.]{0,100}\bsupplies?\s+(?:authority|eligibility)",
            r"(?:mdns|discovery)[^.]{0,100}\b(?:dials?|starts? (?:a )?dial|starts? transport)\b",
            r"(?:mdns|discovery)[^.]{0,100}\b(?:cannot|does not|never)\s+(?:initiate|start|trigger|schedule)\s+(?:a\s+)?(?:dial|transport|connection initiation)\b",
        )
        for pattern in discovery_alone_contradictions:
            with self.subTest(pattern=pattern):
                self.assertIsNone(re.search(pattern, scoped_discovery))

        self.assert_tokens(
            architecture_endpoint,
            {
                "persisted",
                "trusted",
                "queued",
                "pairing",
                "selected",
                "candidate",
                "ski",
                "trust",
                "admin",
                "mdns",
                "grants",
                "authority",
                "cannot",
                "create",
                "eligibility",
                "already",
                "exists",
                "callback",
                "trigger",
                "schedule",
                "connection",
                "initiation",
                "resulting",
                "dial",
                "independent",
                "gate",
            },
        )

    def test_evidence_provenance_falsifiers_and_public_redaction(self) -> None:
        protocol = read(PROTOCOL_CANDIDATE)
        architecture = read(ARCHITECTURE_CANDIDATE)
        evidence = read(EVIDENCE)
        falsifiers = section(protocol, "Falsifiers And Limits")
        observed = section(evidence, "Observed Inputs And Outcomes")

        self.assert_tokens(
            falsifiers,
            {
                "local",
                "resolver",
                "ownership",
                "concrete",
                "275",
                "spine",
                "topology",
                "hostname",
                "fallback",
            },
        )
        self.assert_tokens(
            observed,
            {"persisted", "trusted", "reconnect", "non", "empty"},
        )
        self.assertEqual(metadata_value(evidence, "Device family"), "redacted / not published")
        self.assertEqual(
            metadata_value(evidence, "Firmware version"),
            "redacted / not published",
        )
        self.assertEqual(metadata_value(evidence, "App version"), "unknown")
        self.assertEqual(metadata_value(evidence, "Runtime version"), "unknown")

        corpus = "\n".join((protocol, architecture, evidence))
        self.assertIn(
            "https://github.com/Project-Helianthus/helianthus-docs-eebus/issues/64",
            corpus,
        )
        self.assertIn(
            "https://github.com/Project-Helianthus/helianthus-ship-go/pull/21",
            corpus,
        )
        public_material = "\n".join((protocol, evidence))
        self.assertNotIn("VR940", public_material)
        self.assertIsNone(re.search(r"\b[0-9a-fA-F]{40}\b", public_material))


if __name__ == "__main__":
    unittest.main()
