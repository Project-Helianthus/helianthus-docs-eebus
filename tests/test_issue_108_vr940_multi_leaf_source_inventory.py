from __future__ import annotations

import hashlib
import re
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
INVENTORY = (
    ROOT
    / "architecture"
    / "_candidate"
    / "msp-085-live-r2-vr940-source-inventory.md"
)
EVIDENCE = ROOT / "evidence" / "EV-20260811-002.md"
OVERVIEW = ROOT / "protocols" / "ship-spine-overview.md"


def closed_inventory(text: str) -> dict[str, object]:
    match = re.search(r"## Closed Inventory.*?```yaml\n(.*?)\n```", text, re.DOTALL)
    if match is None:
        raise AssertionError("closed source inventory is missing")
    value = yaml.safe_load(match.group(1))
    if not isinstance(value, dict):
        raise AssertionError("closed source inventory must be a mapping")
    return value


class Issue108VR940MultiLeafSourceInventoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.text = INVENTORY.read_text(encoding="utf-8")
        cls.evidence = EVIDENCE.read_text(encoding="utf-8")
        cls.inventory = closed_inventory(cls.text)
        cls.sources = {
            item["candidate_id"]: item for item in cls.inventory["sources"]
        }

    def test_all_18_candidates_have_exact_dispositions(self) -> None:
        terminal = self.inventory["terminal_candidates"]
        ids = [item["candidate_id"] for item in terminal]
        ids.extend(item["candidate_id"] for item in self.inventory["sources"])
        self.assertEqual(ids, [f"m7-candidate-{index:04d}" for index in range(1, 19)])
        self.assertEqual(
            [(item["required_disposition"], item["required_terminal_state"]) for item in terminal],
            [
                ("WITHHELD", "CLOUD_ONLY"),
                ("WITHHELD", "NOT_TESTED"),
                ("WITHHELD", "NOT_TESTED"),
                ("WITHHELD", "NOT_TESTED"),
            ],
        )

    def test_numeric_steps_are_protocol_owned(self) -> None:
        expected = {
            "m7-candidate-0005": (1, 0),
            "m7-candidate-0006": (1, 0),
            "m7-candidate-0010": (5, -1),
            "m7-candidate-0011": (5, -1),
            "m7-candidate-0014": (5, -1),
            "m7-candidate-0015": (5, -1),
            "m7-candidate-0018": (5, -1),
        }
        for candidate_id, step in expected.items():
            source = self.sources[candidate_id]
            self.assertEqual(source["comparator_class"], "NUMERIC_DECLARED_GRANULARITY")
            self.assertEqual(source["protocol_eligibility"], "ELIGIBLE")
            self.assertEqual(
                (source["declared_constraints"]["step"]["number"], source["declared_constraints"]["step"]["scale"]),
                step,
            )
            self.assertIn(
                source["constraints_function"],
                {"measurementConstraintsListData", "setpointConstraintsListData"},
            )

    def test_enum_and_boolean_relations_are_closed(self) -> None:
        for candidate_id in ("m7-candidate-0007", "m7-candidate-0012", "m7-candidate-0016"):
            self.assertEqual(self.sources[candidate_id]["exact_mapping"], {0: "auto", 1: "on", 2: "off"})
        self.assertEqual(
            self.sources["m7-candidate-0009"]["descriptor"],
            {
                "system_function_id": 0,
                "system_function_type": "dhw",
                "overrun_id": 0,
                "overrun_type": "oneTimeDhw",
                "affected_system_function_ids": [0],
            },
        )
        self.assertEqual(
            self.sources["m7-candidate-0009"]["exact_mapping"],
            {False: "inactive", True: "active"},
        )

    def test_capability_fields_are_not_comparable(self) -> None:
        for candidate_id in ("m7-candidate-0008", "m7-candidate-0013", "m7-candidate-0017"):
            source = self.sources[candidate_id]
            self.assertEqual(source["field_path"].split(".")[-1], "isOperationModeIdChangeable")
            self.assertEqual(source["protocol_eligibility"], "WITHHOLD_NO_EBUS_CAPABILITY_SOURCE")
        self.assertIn("remain `NOT_COMPARABLE`", self.evidence)

    def test_exact_descriptor_is_always_required_before_unit_conversion(self) -> None:
        self.assertIn("require the exact\ndescriptor and then either the exact unit", self.text)
        for source in self.sources.values():
            self.assertEqual(source["feature_role"], "server")
            self.assertIn("descriptor", source)
            self.assertIn("field_path", source)

    def test_public_files_exclude_private_identity_and_secret_material(self) -> None:
        combined = self.text + self.evidence
        self.assertIsNone(re.search(r"\b[0-9a-f]{40}\b", combined, re.IGNORECASE))
        self.assertNotRegex(combined, r"\b192\.168\.\d+\.\d+\b")
        self.assertNotIn("d:_i:", combined)
        for selector in ("[3]", "[4,1,1]", "[5,1,1]", "[6]"):
            self.assertNotIn(selector, combined)
        self.assertIn("read token", combined)
        self.assertIn("trust-store bytes", combined)

    def test_candidate_is_unreleased_and_overview_is_unchanged(self) -> None:
        self.assertIn('publication_status: "candidate"', self.text)
        for marker in (
            'stable_navigation: "false"',
            'search: "false"',
            'sitemap: "false"',
            'versioned_bundle: "false"',
            'release_bundle: "false"',
        ):
            self.assertIn(marker, self.text)
        self.assertEqual(
            hashlib.sha256(OVERVIEW.read_bytes()).hexdigest(),
            "734c5668cd1937b088cbb12c7c4dd6b78c0fc76cc76873dc2d49092aded65b3b",
        )


if __name__ == "__main__":
    unittest.main()
