from __future__ import annotations

import hashlib
import json
import re
import sys
import unittest
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import validate_repository_policy as repository_policy  # noqa: E402


ROOT = Path(__file__).resolve().parents[1]
INVENTORY = (
    ROOT
    / "architecture"
    / "_candidate"
    / "msp-085-live-r2-vr940-source-inventory.md"
)
EVIDENCE = ROOT / "evidence" / "EV-20260811-002.md"
MANIFEST = ROOT / "evidence" / "manifests" / "EV-20260811-002-source-manifest.json"
HISTORICAL_OVERVIEW = ROOT / "tests/fixtures/history/ship-spine-overview.txt"
DEVICE = ROOT / "devices" / "vr940f.md"


def closed_inventory(text: str) -> dict[str, object]:
    match = re.search(r"## Closed Inventory.*?```yaml\n(.*?)\n```", text, re.DOTALL)
    if match is None:
        raise AssertionError("closed source inventory is missing")
    value = yaml.safe_load(match.group(1))
    if not isinstance(value, dict):
        raise AssertionError("closed source inventory must be a mapping")
    return value


RELATION_KINDS = ("zone_to_room", "circuit_to_system_function", "setpoint_to_measurement")


def observed_relations(text: str) -> dict[str, object]:
    match = re.search(r"## Observed Relations.*?```yaml\n(.*?)\n```", text, re.DOTALL)
    if match is None:
        raise AssertionError("observed relation statements are missing")
    value = yaml.safe_load(match.group(1))
    if not isinstance(value, dict):
        raise AssertionError("observed relation statements must be a mapping")
    return value


def normalized(text: str) -> str:
    return " ".join(text.split())


class Issue108VR940MultiLeafSourceInventoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.text = INVENTORY.read_text(encoding="utf-8")
        cls.evidence = EVIDENCE.read_text(encoding="utf-8")
        cls.manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        cls.inventory = closed_inventory(cls.text)
        cls.sources = {
            item["candidate_id"]: item for item in cls.inventory["sources"]
        }

    def test_18_candidate_bound_sources_are_exact(self) -> None:
        self.assertEqual(
            [item["candidate_id"] for item in self.inventory["sources"]],
            [f"m7-candidate-{index:04d}" for index in range(5, 23)],
        )
        self.assertNotIn("terminal_candidates", self.inventory)

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
            "source_classification": "EEBUS_NATIVE_CAPABILITY",
        }
        metadata = lambda slot, entity, function, field, scope: {
            "entity_slot": slot,
            "entity_type": entity,
            "feature_type": "DeviceClassification",
            "description_functions": (),
            "constraints_function": None,
            "value_functions": (function,),
            "field_path": field,
            "descriptor": {"classification_scope": scope},
            "unit": None,
            "constraints": None,
            "mapping": None,
            "source_classification": "EEBUS_NATIVE_METADATA",
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
            "m7-candidate-0019": metadata("device_information", "DeviceInformation", "deviceClassificationManufacturerData", "brandName", "device_information"),
            "m7-candidate-0020": metadata("device_information", "DeviceInformation", "deviceClassificationManufacturerData", "vendorName", "device_information"),
            "m7-candidate-0021": metadata("zone_1", "HeatingZone", "deviceClassificationUserData", "userLabel", "heating_zone"),
            "m7-candidate-0022": metadata("zone_2", "HeatingZone", "deviceClassificationUserData", "userLabel", "heating_zone"),
        }
        actual = {}
        for candidate_id, source in self.sources.items():
            actual[candidate_id] = {
                "entity_slot": source["entity_slot"],
                "entity_type": source["entity_type"],
                "feature_type": source["feature_type"],
                "description_functions": tuple(
                    source["description_functions"]
                    if "description_functions" in source
                    else ([source["description_function"]] if "description_function" in source else [])
                ),
                "constraints_function": source.get("constraints_function"),
                "value_functions": tuple(source["value_functions"] if "value_functions" in source else [source["value_function"]]),
                "field_path": source["field_path"],
                "descriptor": source["descriptor"],
                "unit": source["unit"],
                "constraints": source.get("declared_constraints"),
                "mapping": source.get("exact_mapping"),
            }
            if "source_classification" in source:
                actual[candidate_id]["source_classification"] = source["source_classification"]
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

    def test_native_capability_fields_are_classified(self) -> None:
        for candidate_id in ("m7-candidate-0008", "m7-candidate-0013", "m7-candidate-0017"):
            source = self.sources[candidate_id]
            self.assertEqual(source["field_path"].split(".")[-1], "isOperationModeIdChangeable")
            self.assertEqual(source["source_classification"], "EEBUS_NATIVE_CAPABILITY")
        self.assertIn("does not\ndefine a comparator", self.text)
        self.assertIn("defines no campaign validation rule", self.evidence)
        self.assertNotIn("PRE/POST", self.evidence)

    def test_native_validation_partition_is_exact(self) -> None:
        native = {
            candidate_id
            for candidate_id, source in self.sources.items()
            if source.get("source_classification", "").startswith("EEBUS_NATIVE_")
        }
        self.assertEqual(
            native,
            {
                "m7-candidate-0008",
                "m7-candidate-0013",
                "m7-candidate-0017",
                "m7-candidate-0019",
                "m7-candidate-0020",
                "m7-candidate-0021",
                "m7-candidate-0022",
            },
        )
        self.assertEqual(set(self.sources) - native, {
            "m7-candidate-0005", "m7-candidate-0006", "m7-candidate-0007",
            "m7-candidate-0009", "m7-candidate-0010", "m7-candidate-0011",
            "m7-candidate-0012", "m7-candidate-0014", "m7-candidate-0015",
            "m7-candidate-0016", "m7-candidate-0018",
        })

        forbidden = {
            "semantic_path", "ebus_fallback", "validation_mode",
            "comparator_class", "protocol_eligibility", "promotion_decision",
            "terminal_state", "dossier_hash",
        }
        for source in self.sources.values():
            self.assertTrue(forbidden.isdisjoint(source))

    def test_shareable_manifest_binds_all_source_profiles_and_companion_pr(self) -> None:
        expected = {}
        for candidate_id, source in self.sources.items():
            encoded = json.dumps(
                source, sort_keys=True, separators=(",", ":"), ensure_ascii=True
            ).encode("ascii")
            expected[candidate_id] = "sha256:" + hashlib.sha256(encoded).hexdigest()
        self.assertEqual(self.manifest["source_profile_sha256"], expected)
        self.assertEqual(self.manifest["owner_validation"], "PASS")
        self.assertEqual(set(self.manifest["private_artifact_sha256"]), {
            "deployment_manifest", "hvac_descriptions_relations",
            "numeric_descriptors_constraints", "runtime_status", "topology",
        })
        self.assertIn("helianthus-docs-ebus#419", self.text)
        self.assertIn("exact PR head", self.text)

    def test_exact_descriptor_and_source_constraints_are_preserved(self) -> None:
        self.assertIn("bind the exact\ndescriptor, unit, and protocol-declared constraints", self.text)
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

    def test_every_bundle_states_each_relation_or_none_observed(self) -> None:
        relations = observed_relations(self.text)
        self.assertEqual(relations["slot_label_scope"], "bundle_local")
        bundles = relations["bundles"]
        self.assertEqual(
            set(bundles),
            {source["entity_slot"] for source in self.sources.values()},
        )
        for bundle, statements in bundles.items():
            with self.subTest(bundle=bundle):
                self.assertEqual(tuple(statements), RELATION_KINDS)
                for statement in statements.values():
                    if statement != "none_observed":
                        self.assertEqual(statement["status"], "observed")

    def test_observed_relations_are_exact(self) -> None:
        none = dict.fromkeys(RELATION_KINDS, "none_observed")

        def setpoint(setpoint_id: str, measurement_id: str) -> dict[str, object]:
            return {
                "status": "observed",
                "from": setpoint_id,
                "to": measurement_id,
                "native_basis": "setpointDescriptionListData.measurementId",
            }

        expected = {
            "dhw_circuit": {
                "zone_to_room": "none_observed",
                "circuit_to_system_function": {
                    "status": "observed",
                    "system_function": {"system_function_id": 0, "system_function_type": "dhw"},
                    "evidence": ["m7-candidate-0007", "m7-candidate-0008", "m7-candidate-0009"],
                    "native_basis": "hvacSystemFunctionDescriptionListData.systemFunctionType",
                },
                "setpoint_to_measurement": setpoint("m7-candidate-0006", "m7-candidate-0005"),
            },
            "zone_1_room": {
                **none,
                "setpoint_to_measurement": setpoint("m7-candidate-0011", "m7-candidate-0010"),
            },
            "zone_2_room": {
                **none,
                "setpoint_to_measurement": setpoint("m7-candidate-0015", "m7-candidate-0014"),
            },
            "outside_sensor": none,
            "device_information": none,
            "zone_1": none,
            "zone_2": none,
        }
        self.assertEqual(observed_relations(self.text)["bundles"], expected)

    def test_setpoint_relation_follows_the_native_measurement_reference(self) -> None:
        bundles = observed_relations(self.text)["bundles"]
        derived = {}
        for candidate_id, source in self.sources.items():
            if source["feature_type"] != "Setpoint":
                continue
            measured = [
                other_id
                for other_id, other in self.sources.items()
                if other["feature_type"] == "Measurement"
                and other["entity_slot"] == source["entity_slot"]
                and other["descriptor"]["measurement_id"] == source["descriptor"]["measurement_id"]
            ]
            self.assertEqual(len(measured), 1, candidate_id)
            derived[source["entity_slot"]] = (candidate_id, measured[0])
        for bundle, statements in bundles.items():
            relation = statements["setpoint_to_measurement"]
            with self.subTest(bundle=bundle):
                if bundle in derived:
                    self.assertEqual((relation["from"], relation["to"]), derived[bundle])
                else:
                    self.assertEqual(relation, "none_observed")

    def test_relation_evidence_never_joins_across_bundles(self) -> None:
        for bundle, statements in observed_relations(self.text)["bundles"].items():
            for kind, statement in statements.items():
                if statement == "none_observed":
                    continue
                cited = statement.get("evidence", []) + [
                    statement[end] for end in ("from", "to") if end in statement
                ]
                with self.subTest(bundle=bundle, relation=kind):
                    self.assertTrue(cited)
                    for candidate_id in cited:
                        self.assertEqual(self.sources[candidate_id]["entity_slot"], bundle)
        for statements in observed_relations(self.text)["bundles"].values():
            self.assertEqual(statements["zone_to_room"], "none_observed")

    def test_slot_labels_are_bundle_local_and_never_a_join_key(self) -> None:
        text = normalized(self.text)
        for sentence in (
            "Slot labels are local to their bundle.",
            "A slot label is never an identity, an anchor or an ordinal to join on.",
            "`zone_1` and `zone_1_room` are two bundles with no observed relation between them",
            "Similar names, shared digits and ordinal position are never a basis for a relation.",
            "`none_observed` is not an absence statement: for a consumer the relation stays unknown.",
            "A consumer must not derive a display name, a zone number or a pairing from a slot label.",
        ):
            self.assertIn(sentence, text)

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
            hashlib.sha256(HISTORICAL_OVERVIEW.read_bytes()).hexdigest(),
            repository_policy.ISSUE68_STABLE_PROTOCOL_SHA256,
        )
        heating = " ".join(DEVICE.read_text(encoding="utf-8").split())
        inventory = " ".join(self.text.split())
        for phrase in (
            "declared cross-protocol leaves are promoted and exposed by default",
            "recorded verification level",
            "hot-water mode",
            "zone names",
        ):
            self.assertIn(phrase, heating)
            self.assertIn(phrase, inventory)
        self.assertNotIn("LOCKED_" + "NOT_EXPOSED", inventory)
        self.assertNotIn("No promoted semantic fields", heating)


if __name__ == "__main__":
    unittest.main()
