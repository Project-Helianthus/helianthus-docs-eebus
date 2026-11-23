"""Fact pages for the SHIP and SPINE revisions this repository records."""

import csv
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

TSV_HEADER = [
    "feature",
    "function",
    "element / identifier values",
    "type",
    "unit / scale",
    "use cases and scenarios (M/R/O)",
    "server actor",
    "client actor",
    "operations",
    "locators",
]

PAGE_SECTIONS = {
    "protocols/ship-1.0.1.md": (
        "Parameters",
        "Discovery",
        "Transport",
        "Trust",
        "Connection states",
        "Messages",
        "Commands, limits and timing",
        "Open points",
    ),
    "protocols/ship-1.1.0.md": (
        "Parameters",
        "Discovery",
        "Transport",
        "Trust",
        "Connection states",
        "Messages",
        "Changes from 1.0.1",
        "Commands, limits and timing",
        "Open points",
    ),
    "protocols/ship-pairing-service-1.0.0.md": (
        "Roles",
        "Steps",
        "DNS-SD records and TXT keys",
        "Request and digest",
        "QR code fields",
        "Commands, limits and timing",
        "Open points",
    ),
    "protocols/ship-installation-requirements-1.1.0.md": (
        "Numbered requirements",
        "Obligations without an identifier",
        "Fields",
        "Commands, limits and timing",
        "Open points",
    ),
    "protocols/spine-introduction-1.3.0.md": (
        "Document",
        "Actors",
        "Scenarios",
        "Entities features and roles",
        "Functions and data points",
        "Command limit and timing semantics",
        "Requirements",
        "Open points",
    ),
    "protocols/spine-protocol-1.3.0.md": (
        "Concepts",
        "Datagram header",
        "Addressing",
        "Command classifiers",
        "Acknowledgement and error codes",
        "Message counter",
        "Detailed discovery",
        "Binding and subscription",
        "Restricted function exchange",
        "Compatibility and unknown content",
        "Commands, limits and timing",
        "Open points",
    ),
    "protocols/spine-resources-1.3.0.md": (
        "Device, entity and feature types",
        "Functions per feature",
        "Commands, limits and timing",
        "Data file",
        "Open points",
    ),
}

PAGE_HEADERS = {
    "protocols/ship-1.0.1.md": (
        "| parameter | clause | value or range | unit |",
        "| DNS-SD item or TXT key | type | presence | meaning (own words) | clause |",
        "| layer | requirement (own words) | value | clause |",
        "| verification mode | trust level | clause |",
        "| state | entered on | leaves on | timer | clause |",
        "| message | field | type | presence | clause |",
    ),
    "protocols/ship-1.1.0.md": (
        "| parameter | clause | value or range | unit |",
        "| DNS-SD item or TXT key | type | presence | meaning (own words) | clause |",
        "| layer | requirement (own words) | value | clause |",
        "| verification mode | trust level | clause |",
        "| state | entered on | leaves on | timer | clause |",
        "| message | field | type | presence | clause |",
        "| topic | 1.0.1 | 1.1.0 | clause |",
    ),
    "protocols/ship-pairing-service-1.0.0.md": (
        "| role | does | clause |",
        "| key | type | presence | meaning | clause |",
    ),
    "protocols/ship-installation-requirements-1.1.0.md": (
        "| requirement id | category | obligation (SHALL, SHOULD, MAY) | subject (own words, at most 20) | clause |",
        "| obligation | subject | clause |",
        "| field | type | bounds | clause |",
    ),
    "protocols/spine-protocol-1.3.0.md": (
        "| element | type | presence | meaning | clause |",
        "| classifier | meaning | response | clause |",
        "| code | meaning | clause |",
        "| element of nodeManagementDetailedDiscoveryData | type | presence | clause |",
        "| operation | rule (own words) | clause |",
    ),
    "protocols/spine-resources-1.3.0.md": (
        "| type | meaning (own words) | clause |",
        "| feature | function | clause |",
    ),
}

LOCATOR_LEAK = re.compile(
    r"facts-[A-Za-z0-9._-]+\.md"
    r"|`l\.\d+|`p\.\d+"
    r"|(?<![A-Za-z])l\.\d+"
    r"|(?<![A-Za-z])p\.\d+"
    r"|(?<![A-Za-z0-9])L(?!(?:[123])(?!\d))\d+"
    r"|(?<![A-Za-z])lines?\s+\d+"
    r"|(?<=[\s(])–\d+"
    r"|outside this (?:shard|range|page range)"
    r"|(?:not )?in this (?:page )?range"
    r"|\(\s*outside\s*\)"
    r"|pages \d+–\d+"
    r"|open points? \d+"
    r"|(?:first|second) shard"
    r"|\bshards?\b"
    r"|text extract"
    r"|extracted steps"
    r"|extracted glyphs"
    r"|in the extract"
    r"|not recoverable"
    r"|recoverable direction"
    r"|separate line numbers"
    r"|taken from the drawing",
    re.IGNORECASE,
)


def _cells(line):
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def _tables(text):
    lines = text.splitlines()
    index = 0
    while index < len(lines):
        line = lines[index]
        if (
            line.startswith("|")
            and index + 1 < len(lines)
            and re.match(r"^\|\s*-+", lines[index + 1])
        ):
            header = _cells(line)
            rows = []
            index += 2
            while index < len(lines) and lines[index].startswith("|"):
                rows.append(_cells(lines[index]))
                index += 1
            yield header, rows
            continue
        index += 1


class SpecificationPagesTest(unittest.TestCase):
    def test_locator_leak_catches_shard_lines_offsets_and_anchors(self):
        samples = (
            "L330–L332",
            "L363–L369 (–3042)",
            "L165–L166",
            "lines 1707–1708",
            "lines 2948–2949",
            "(–335)",
            "(–2722)",
            "outside this shard",
            "outside this range",
            "outside this page range",
            "not in this range",
            "not in this page range",
            "§3.2 (outside)",
            "pages 1–64",
            "open point 18",
            "Open points 12–13",
            "first shard",
            "second shard",
            "shard locators",
            "text extract",
            "extracted steps",
            "in the extract",
            "not recoverable from the text",
            "without a recoverable direction",
            "no separate line numbers",
            "labels are taken from the drawing",
            "facts-spine-protocol.md",
            "l.452",
            "p.53",
        )
        for sample in samples:
            self.assertIsNotNone(LOCATOR_LEAK.search(sample), sample)
        for spared in (
            "outside this specification",
            "outside this class",
            "outside this element",
            "phase a or L1",
            "locators",
            "extracts the public key",
            "extracts SHIP messages",
            "See open points.",
            "cardinality 1..unbounded",
            "16–32",
        ):
            self.assertIsNone(LOCATOR_LEAK.search(spared), spared)

    def test_each_page_has_named_sections_and_clause_cells(self):
        for rel, sections in PAGE_SECTIONS.items():
            path = ROOT / rel
            self.assertTrue(path.is_file(), rel)
            text = path.read_text(encoding="utf-8")
            for section in sections:
                self.assertIn(f"## {section}", text, rel)
            for header in PAGE_HEADERS.get(rel, ()):
                self.assertIn(header, text, rel)
            self.assertIsNone(LOCATOR_LEAK.search(text), rel)
            for header, rows in _tables(text):
                clause_at = [
                    position
                    for position, name in enumerate(header)
                    if "clause" in name.lower()
                ]
                self.assertEqual(len(clause_at), 1, header)
                position = clause_at[0]
                for row in rows:
                    self.assertEqual(len(row), len(header), row)
                    self.assertTrue(row[position], row)

    def test_open_points_name_printed_conflicts(self):
        ship_101 = (ROOT / "protocols/ship-1.0.1.md").read_text(encoding="utf-8")
        ship_110 = (ROOT / "protocols/ship-1.1.0.md").read_text(encoding="utf-8")
        pairing = (ROOT / "protocols/ship-pairing-service-1.0.0.md").read_text(
            encoding="utf-8"
        )
        resources = (ROOT / "protocols/spine-resources-1.3.0.md").read_text(
            encoding="utf-8"
        )
        protocol = (ROOT / "protocols/spine-protocol-1.3.0.md").read_text(
            encoding="utf-8"
        )
        for page in (ship_101, ship_110):
            self.assertIn("512", page)
            self.assertIn("1024", page)
        self.assertIn("20 bytes", ship_101)
        self.assertIn("40 byte", ship_101)
        self.assertIn("8", ship_110)
        self.assertIn("32", ship_110)
        self.assertIn("devA-secret", pairing)
        self.assertIn("devZ-nonce", pairing)
        self.assertIn("defaultMaxResponseDelay", protocol)
        self.assertIn("10 seconds", protocol)
        self.assertIn("heartbeatTimeout", resources)
        self.assertIn("failsafeDurationMinimum", resources)
        self.assertIn("256", resources)
        self.assertIn("4096", resources)

    def test_figure_notes_do_not_name_a_reading(self):
        intro = (ROOT / "protocols/spine-introduction-1.3.0.md").read_text(
            encoding="utf-8"
        )
        resources = (ROOT / "protocols/spine-resources-1.3.0.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("Figure 3 is the specification stack", intro)
        self.assertIn(
            "Figure 4 is that picture; its body is not recorded",
            intro,
        )
        self.assertIn(
            "Figures 10, 11, and 12 draw that shape; their bodies are not recorded",
            intro,
        )
        self.assertIn(
            "Figure 12 groups the constituents; the groups are not recorded",
            intro,
        )
        self.assertIn(
            "Figure 6 prints 1 and n beside the function band and beside the element band. Which side is 1 and which side is n is not recorded.",
            intro,
        )
        protocol_page_11 = (ROOT / "protocols/ship-1.1.0.md").read_text(encoding="utf-8")
        self.assertIn(
            "Figure 3 draws the complete mutually authenticated TLS 1.2 handshake. Figure 4 draws the shorter handshake that resumes a session. Step labels inside the drawings are not recorded.",
            protocol_page_11,
        )
        self.assertIn(
            "Figure 9 names these layers from the application side downward",
            protocol_page_11,
        )
        self.assertIn("Which boxes are white and which are grey is not recorded.", protocol_page_11)
        protocol = (ROOT / "protocols/spine-protocol-1.3.0.md").read_text(encoding="utf-8")
        self.assertIn("The steps of Figure 27 are not recorded.", protocol)
        self.assertIn("The figure content is not recorded.", protocol)
        pairing = (ROOT / "protocols/ship-pairing-service-1.0.0.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("Figure 1 includes SKI in the scanned QR list.", pairing)
        self.assertIn("Figure content beyond those labels is not recorded.", pairing)
        self.assertIn(
            "Figure 2 is a picture of the Annex A example QR code.",
            pairing,
        )
        data = (ROOT / "protocols/spine-resources-1.3.0-data-points.tsv").read_text(
            encoding="utf-8"
        )
        self.assertIn(
            "Figure 13 is about referencing this function and loadControlLimitDescriptionListData; the drawing is not recorded",
            data,
        )
        self.assertIn("which side is which is not recorded", data)
        self.assertNotIn("section 5..", resources)
        self.assertIn("section 5.", resources)
        self.assertIn("and locators.", resources)
        self.assertNotIn("shard", resources.casefold())

    def test_data_file_has_header_and_one_row_per_index_point(self):
        path = ROOT / "protocols/spine-resources-1.3.0-data-points.tsv"
        self.assertTrue(path.is_file())
        with path.open(encoding="utf-8", newline="") as handle:
            rows = list(csv.reader(handle, delimiter="\t"))
        self.assertEqual(rows[0], TSV_HEADER)
        self.assertEqual(len(rows) - 1, 6507)
        text = path.read_text(encoding="utf-8")
        self.assertIsNone(LOCATOR_LEAK.search(text))
        self.assertNotIn("Illustration", text)

    def test_introduction_does_not_name_source_files(self):
        text = (ROOT / "protocols/spine-introduction-1.3.0.md").read_text(encoding="utf-8")
        self.assertNotIn(".pdf", text)
        self.assertIsNone(re.search(r"\b[\w.-]+\.(?:pdf|xsd)\b", text))
        self.assertIn('source_class: "vendor_public"', text)
        self.assertIn("extension .xsd", text)

    def test_binding_operation_names_the_topic(self):
        text = (ROOT / "protocols/spine-protocol-1.3.0.md").read_text(encoding="utf-8")
        section = text.split("## Binding and subscription", 1)[1].split("\n## ", 1)[0]
        rows = []
        for line in section.splitlines():
            if not line.startswith("|") or line.startswith("| ---") or line.startswith("| operation"):
                continue
            cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
            self.assertEqual(len(cells), 3, line[:80])
            rows.append(cells)

        def operation_for(fragment):
            matches = [operation for operation, rule, _clause in rows if fragment in rule]
            self.assertEqual(len(matches), 1, fragment)
            return matches[0]

        self.assertEqual(
            operation_for("Final versus preliminary use-case documents"),
            "Use-case document",
        )
        self.assertEqual(
            operation_for("The specification phase is the time between official releases"),
            "Release versioning",
        )
        self.assertEqual(operation_for("A release candidate appends RC"), "Release versioning")
        self.assertEqual(operation_for("Two gateway kinds are described"), "Annex E")
        self.assertEqual(operation_for("E.5 SPINE proxy"), "Annex E")
        self.assertEqual(
            operation_for("Schema version numbers have a natural order"),
            "Schema versioning",
        )
        for operation, rule, _clause in rows:
            if operation != "Subscription":
                continue
            lowered = rule.casefold()
            self.assertTrue("subscription" in lowered or "§7.4" in rule, rule[:120])
            for banned in (
                "release candidate",
                "gateway kinds",
                "useCaseDocumentSubRevision",
                "SPINE proxy",
            ):
                self.assertNotIn(banned, rule)

    def test_worked_examples_state_the_rule_without_values(self):
        protocol = (ROOT / "protocols/spine-protocol-1.3.0.md").read_text(encoding="utf-8")
        for banned in (
            "V1.1.0_draft1_1234",
            "draft1_1234",
            "V1.1.0_RC1_1765",
            "RC1_1765",
            "SOME_specification_V1.0.0_20150522",
            "entity list is 1 then 4",
            "entity list is only 4",
            "nested entity 4",
            "under entity 1",
        ):
            self.assertNotIn(banned, protocol, banned)
        version_rule = (
            "placing its version numerals in useCaseVersion and the following "
            "release token in useCaseDocumentSubRevision "
            "(SPINE Protocol Specification 1.3.0 Table 20)"
        )
        self.assertEqual(protocol.count(version_rule), 2)
        annex_rule = (
            "A date in YYYYMMDD form may sit after the version part and before any label. "
            "On a final release the date follows the version. "
            "For draft, alpha, beta, or RC the date follows that tag's numeral. "
            "For a snapshot the date follows the repository revision "
            "(SPINE Protocol Specification 1.3.0 Annex C)."
        )
        self.assertEqual(protocol.count(annex_rule), 3)
        self.assertIn(
            "A selector matches only an exact entity list. "
            "That list matches the same entity path and the same path with a feature after it. "
            "A list of one entity number matches only the top-level entity with that number. "
            "A nested entity that reuses that number under a parent matches a list that includes the parent "
            "(SPINE Protocol Specification 1.3.0 §5.3.4.7.2, Table 10).",
            protocol,
        )

        protocol_page_11 = (ROOT / "protocols/ship-1.1.0.md").read_text(encoding="utf-8")
        for banned in ("10.89", "15.51", "33 × 0.33", "47 × 0.33", "0.33 mm"):
            self.assertNotIn(banned, protocol_page_11, banned)
        self.assertIn(
            "A symbol that carries only SKI and PIN has a drawn size, quiet zone excluded, "
            "equal to its module count times the module size (SHIP Specification 1.1.0 §12.7).",
            protocol_page_11,
        )
        self.assertIn(
            "When the optional text fields are also carried, the module count follows the lengths of "
            "ID, BRAND, TYPE, and MODEL (SHIP Specification 1.1.0 §12.7).",
            protocol_page_11,
        )
        self.assertIn("Module size at least 330×10⁻⁶ m", protocol_page_11)
        self.assertIn("Quiet zone at least 4 modules wide.", protocol_page_11)
        self.assertIn("Field order that is printed: SHIP;", protocol_page_11)

        data = (ROOT / "protocols/spine-resources-1.3.0-data-points.tsv").read_text(
            encoding="utf-8"
        )
        for banned in (
            "examples printed",
            "1.0.0, 1.5.3",
            "charge, discharge, idle",
            "m^3, m^3/h, m/s^2, kg_m^2",
        ):
            self.assertNotIn(banned, data, banned)
        self.assertIn(
            "specificationVersionList; id: SPINE specification versions the device supports; "
            "range: at least the child below (SPINE Protocol Specification 1.3.0 Table 11)",
            data,
        )
        self.assertIn(
            "scope; id: batteryControl; range: battery control "
            "(SPINE Resource Specification 1.3.0 §3.10.1.22, Table 9)",
            data,
        )
        self.assertIn(
            "x/y division; x^y power; x_y multiplication "
            "(SPINE Resource Specification 1.3.0 §3.10.1.18)",
            data,
        )
        self.assertIn("scope; id: charge; range: battery charge", data)
        self.assertIn("unit; id: m^3/h; range: Table 7", data)


if __name__ == "__main__":
    unittest.main()
