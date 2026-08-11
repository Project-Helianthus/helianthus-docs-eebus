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

    def test_complete_source_projection_is_closed_per_candidate(self) -> None:
        numeric = lambda slot, entity, feature, function, path, descriptor, minimum, maximum, step: {
            "entity_slot": slot,
            "entity_type": entity,
            "feature_type": feature,
            "description_functions": (function.replace("ListData", "DescriptionListData"),),
            "constraints_function": function.replace("ListData", "ConstraintsListData"),
            "value_functions": (function,),
            "field_path": path,
            "descriptor": descriptor,
            "unit": "degC",
            "constraints": {"minimum": minimum, "maximum": maximum, "step": step},
            "mapping": None,
            "comparator": "NUMERIC_DECLARED_GRANULARITY",
            "eligibility": "ELIGIBLE",
        }
        mode = lambda slot, entity, system_type: {
            "entity_slot": slot,
            "entity_type": entity,
            "feature_type": "HVAC",
            "description_functions": (
                "hvacSystemFunctionDescriptionListData",
                "hvacOperationModeDescriptionListData",
                "hvacSystemFunctionOperationModeRelationListData",
            ),
            "constraints_function": None,
            "value_functions": ("hvacSystemFunctionListData",),
            "field_path": "hvacSystemFunctionData[systemFunctionId=0].currentOperationModeId",
            "descriptor": {"system_function_id": 0, "system_function_type": system_type},
            "unit": None,
            "constraints": None,
            "mapping": {0: "auto", 1: "on", 2: "off"},
            "comparator": "ENUM_EXACT_MAPPING",
            "eligibility": "ELIGIBLE",
        }
        capability = lambda slot, entity, system_type: {
            "entity_slot": slot,
            "entity_type": entity,
            "feature_type": "HVAC",
            "description_functions": ("hvacSystemFunctionDescriptionListData",),
            "constraints_function": None,
            "value_functions": ("hvacSystemFunctionListData",),
            "field_path": "hvacSystemFunctionData[systemFunctionId=0].isOperationModeIdChangeable",
            "descriptor": {"system_function_id": 0, "system_function_type": system_type},
            "unit": None,
            "constraints": None,
            "mapping": {False: False, True: True},
            "comparator": "BOOLEAN_EXACT_MAPPING",
            "eligibility": "WITHHOLD_NO_EBUS_CAPABILITY_SOURCE",
        }
        expected = {
            "m7-candidate-0005": numeric("dhw_circuit", "DHWCircuit", "Measurement", "measurementListData", "measurementData[measurementId=0].value", {"measurement_id": 0, "commodity_type": "domesticHotWater", "measurement_type": "temperature", "scope_type": "dhwTemperature", "unit": "degC"}, {"number": 0, "scale": -6}, {"number": 99, "scale": 0}, {"number": 1, "scale": 0}),
            "m7-candidate-0006": numeric("dhw_circuit", "DHWCircuit", "Setpoint", "setpointListData", "setpointData[setpointId=1].value", {"measurement_id": 0, "setpoint_id": 1, "setpoint_type": "valueAbsolute", "scope_type": "dhwTemperature", "unit": "degC"}, {"number": 35, "scale": 0}, {"number": 7, "scale": 1}, {"number": 1, "scale": 0}),
            "m7-candidate-0007": mode("dhw_circuit", "DHWCircuit", "dhw"),
            "m7-candidate-0008": capability("dhw_circuit", "DHWCircuit", "dhw"),
            "m7-candidate-0009": {
                "entity_slot": "dhw_circuit", "entity_type": "DHWCircuit", "feature_type": "HVAC",
                "description_functions": ("hvacSystemFunctionDescriptionListData", "hvacOverrunDescriptionListData"),
                "constraints_function": None,
                "value_functions": ("hvacSystemFunctionListData", "hvacOverrunListData"),
                "field_path": "hvacSystemFunctionData[systemFunctionId=0].isOverrunActive",
                "descriptor": {"system_function_id": 0, "system_function_type": "dhw", "overrun_id": 0, "overrun_type": "oneTimeDhw", "affected_system_function_ids": [0]},
                "unit": None, "constraints": None, "mapping": {False: False, True: True},
                "comparator": "BOOLEAN_EXACT_MAPPING", "eligibility": "ELIGIBLE",
            },
            "m7-candidate-0010": numeric("zone_1_room", "HVACRoom", "Measurement", "measurementListData", "measurementData[measurementId=0].value", {"measurement_id": 0, "commodity_type": "air", "measurement_type": "temperature", "scope_type": "roomAirTemperature", "unit": "degC"}, {"number": 0, "scale": -6}, {"number": 6, "scale": 1}, {"number": 5, "scale": -1}),
            "m7-candidate-0011": numeric("zone_1_room", "HVACRoom", "Setpoint", "setpointListData", "setpointData[setpointId=1].value", {"measurement_id": 0, "setpoint_id": 1, "setpoint_type": "valueAbsolute", "scope_type": "roomAirTemperature", "unit": "degC"}, {"number": 5, "scale": 0}, {"number": 3, "scale": 1}, {"number": 5, "scale": -1}),
            "m7-candidate-0012": mode("zone_1_room", "HVACRoom", "heating"),
            "m7-candidate-0013": capability("zone_1_room", "HVACRoom", "heating"),
            "m7-candidate-0014": numeric("zone_2_room", "HVACRoom", "Measurement", "measurementListData", "measurementData[measurementId=0].value", {"measurement_id": 0, "commodity_type": "air", "measurement_type": "temperature", "scope_type": "roomAirTemperature", "unit": "degC"}, {"number": 0, "scale": -6}, {"number": 6, "scale": 1}, {"number": 5, "scale": -1}),
            "m7-candidate-0015": numeric("zone_2_room", "HVACRoom", "Setpoint", "setpointListData", "setpointData[setpointId=1].value", {"measurement_id": 0, "setpoint_id": 1, "setpoint_type": "valueAbsolute", "scope_type": "roomAirTemperature", "unit": "degC"}, {"number": 5, "scale": 0}, {"number": 3, "scale": 1}, {"number": 5, "scale": -1}),
            "m7-candidate-0016": mode("zone_2_room", "HVACRoom", "heating"),
            "m7-candidate-0017": capability("zone_2_room", "HVACRoom", "heating"),
            "m7-candidate-0018": numeric("outside_sensor", "TemperatureSensor", "Measurement", "measurementListData", "measurementData[measurementId=0].value", {"measurement_id": 0, "commodity_type": "air", "measurement_type": "temperature", "scope_type": "outsideAirTemperature", "unit": "degC"}, {"number": -6, "scale": 1}, {"number": 8, "scale": 1}, {"number": 5, "scale": -1}),
        }
        actual = {}
        for candidate_id, source in self.sources.items():
            actual[candidate_id] = {
                "entity_slot": source["entity_slot"],
                "entity_type": source["entity_type"],
                "feature_type": source["feature_type"],
                "description_functions": tuple(source["description_functions"] if "description_functions" in source else [source["description_function"]]),
                "constraints_function": source.get("constraints_function"),
                "value_functions": tuple(source["value_functions"] if "value_functions" in source else [source["value_function"]]),
                "field_path": source["field_path"],
                "descriptor": source["descriptor"],
                "unit": source["unit"],
                "constraints": source.get("declared_constraints"),
                "mapping": source.get("exact_mapping"),
                "comparator": source["comparator_class"],
                "eligibility": source["protocol_eligibility"],
            }
        self.assertEqual(actual, expected)

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
            {False: False, True: True},
        )
        self.assertTrue(all(isinstance(value, bool) for value in self.sources["m7-candidate-0009"]["exact_mapping"].values()))

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
        for private_identity_field in (
            "service_id:",
            "device_address:",
            "entity_address:",
            "feature_address:",
            "ship" + "_id:",
            "s" + "ki:",
        ):
            self.assertNotIn(private_identity_field, combined.lower())
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
