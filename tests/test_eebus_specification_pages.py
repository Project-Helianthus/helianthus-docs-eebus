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
    "shard locators",
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
    r"facts-[A-Za-z0-9._-]+\.md|`l\.\d+|`p\.\d+|(?<![A-Za-z])l\.\d+|(?<![A-Za-z])p\.\d+"
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


if __name__ == "__main__":
    unittest.main()
