from __future__ import annotations

import json
import shutil
import sys
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import validate_repository_policy as repository_policy  # noqa: E402


SCHEMA_REL = Path(
    "api/_candidate/msp-0625/"
    "helianthus.eebus.m625.public-redacted-evidence.v1.schema.json"
)
FIXTURE_REL = Path(
    "tests/fixtures/issue98/m625-public-redacted-source-positive.json"
)
API_REL = Path("api/_candidate/msp-0625-raw-feature-acquisition.md")
PROTOCOL_REL = Path("protocols/_candidate/msp-0625-feature-data-acquisition.md")
DEVELOPMENT_REL = Path("development/msp-0625-provenance-policy.md")


def load_json(relative: Path) -> object:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def copy_repo(tmp_path: Path) -> Path:
    destination = tmp_path / "repo"
    shutil.copytree(
        ROOT,
        destination,
        ignore=shutil.ignore_patterns(".git", ".pytest_cache", "__pycache__"),
    )
    return destination


def schema_accepts(schema: dict, instance: object) -> bool:
    definitions = schema.get("$defs", {})

    def matches(candidate: object, value: object) -> bool:
        if not isinstance(candidate, dict):
            return False
        if "oneOf" in candidate and (
            sum(matches(option, value) for option in candidate["oneOf"]) != 1
        ):
            return False
        if "allOf" in candidate and not all(
            matches(option, value) for option in candidate["allOf"]
        ):
            return False
        if "not" in candidate and matches(candidate["not"], value):
            return False
        reference = candidate.get("$ref")
        if reference is not None:
            prefix = "#/$defs/"
            if not isinstance(reference, str) or not reference.startswith(prefix):
                return False
            return matches(definitions[reference.removeprefix(prefix)], value)

        expected_type = candidate.get("type")
        type_matches = {
            "null": value is None,
            "integer": isinstance(value, int) and not isinstance(value, bool),
            "string": isinstance(value, str),
            "array": isinstance(value, list),
            "object": isinstance(value, dict),
        }
        if isinstance(expected_type, str) and not type_matches.get(expected_type, False):
            return False
        if "const" in candidate and value != candidate["const"]:
            return False
        if "enum" in candidate and value not in candidate["enum"]:
            return False

        if isinstance(value, str):
            if len(value) < candidate.get("minLength", 0):
                return False
            if len(value) > candidate.get("maxLength", len(value)):
                return False
            pattern = candidate.get("pattern")
            if isinstance(pattern, str):
                import re

                if re.fullmatch(pattern, value) is None:
                    return False
            if candidate.get("format") == "date-time":
                from datetime import datetime

                try:
                    datetime.fromisoformat(value.replace("Z", "+00:00"))
                except ValueError:
                    return False

        if isinstance(value, int) and not isinstance(value, bool):
            if value < candidate.get("minimum", value):
                return False
            if value > candidate.get("maximum", value):
                return False

        if isinstance(value, list):
            if len(value) < candidate.get("minItems", 0):
                return False
            if len(value) > candidate.get("maxItems", len(value)):
                return False
            item_schema = candidate.get("items")
            if item_schema is not None and not all(
                matches(item_schema, item) for item in value
            ):
                return False

        if isinstance(value, dict):
            if not set(candidate.get("required", [])).issubset(value):
                return False
            properties = candidate.get("properties", {})
            for name, item in value.items():
                if name in properties:
                    if not matches(properties[name], item):
                        return False
                elif candidate.get("additionalProperties") is False:
                    return False
        return True

    return matches(schema, instance)


class Issue98M65LiveRedactedSourceContractTests(unittest.TestCase):
    def test_closed_source_schema_accepts_the_canonical_positive_fixture(self) -> None:
        schema = load_json(SCHEMA_REL)
        fixture = load_json(FIXTURE_REL)

        self.assertTrue(schema_accepts(schema, fixture))

        self.assertFalse(schema["additionalProperties"])
        self.assertEqual(
            set(schema["properties"]),
            {
                "contract",
                "schema_version",
                "source_observed_at",
                "services",
                "feature_paths",
                "observations",
            },
        )
        self.assertEqual(
            schema["properties"]["contract"]["const"],
            "helianthus.eebus.m625.public-redacted-evidence.v1",
        )
        self.assertEqual(schema["properties"]["schema_version"]["const"], 1)
        for envelope_owned in (
            "summary",
            "recorder_offset_ns",
            "outcome_commitment",
            "bundle_id",
            "source_id",
            "artifact_id",
            "redacted_hash",
            "replay_hash",
        ):
            self.assertNotIn(envelope_owned, schema["properties"])
            self.assertNotIn(
                envelope_owned,
                schema["$defs"]["ObservationV1"]["properties"],
            )

    def test_schema_preserves_m7_comparison_data_without_native_identity(self) -> None:
        schema = load_json(SCHEMA_REL)
        fixture = load_json(FIXTURE_REL)

        successful = fixture["observations"][0]
        self.assertEqual(successful["feature_type"], "Measurement")
        self.assertEqual(successful["feature_role"], "server")
        self.assertEqual(successful["function"], "measurementListData")
        self.assertEqual(successful["value_type"], "DECIMAL")
        self.assertEqual(successful["value"], "21.5")
        self.assertEqual(successful["unit"], "degC")
        self.assertEqual(successful["quality"], "OBSERVED")
        self.assertEqual(
            [
                segment["kind"]
                for segment in fixture["feature_paths"][successful["path_index"]][
                    "feature_path"
                ]
            ],
            ["SERVICE", "ENTITY", "FEATURE", "FIELD"],
        )

        forbidden_fields = (
            "remote_ski",
            "local_ski",
            "ship_id",
            "device_address",
            "entity_address",
            "feature_address",
            "target",
            "typed_value",
            "raw_request",
            "raw_response",
            "read_token",
            "mutation_ref",
            "idempotency_key",
            "runtime_epoch",
            "connection_generation",
            "private_network_address",
            "label",
            "schedule",
            "remapping_table",
            "candidate_ref",
            "private_key",
            "pem",
            "trust_store",
            "credential",
            "token",
            "bundle_id",
            "source_id",
            "artifact_id",
            "source_binding",
            "auth_scope",
            "pseudonym_scope",
            "evidence_refs",
            "redacted_hash",
            "replay_hash",
        )
        for field in forbidden_fields:
            with self.subTest(field=field):
                mutated = deepcopy(fixture)
                mutated["observations"][0][field] = "forbidden"
                self.assertFalse(schema_accepts(schema, mutated))

    def test_schema_closes_ordering_terminal_and_success_shape(self) -> None:
        schema = load_json(SCHEMA_REL)
        fixture = load_json(FIXTURE_REL)

        mutated = deepcopy(fixture)
        mutated["observations"].reverse()
        errors = repository_policy.issue_98_m65_live_redacted_source_instance_errors(
            schema,
            mutated,
        )
        self.assertIn("observations must be ordered by observation_ref", errors)

        mutated = deepcopy(fixture)
        mutated["observations"][0]["terminal_classification"] = "INVENTED_SUCCESS"
        self.assertFalse(schema_accepts(schema, mutated))

        mutated = deepcopy(fixture)
        mutated["observations"][0]["value"] = None
        errors = repository_policy.issue_98_m65_live_redacted_source_instance_errors(
            schema,
            mutated,
        )
        self.assertIn(
            "SUCCESS observations require value_type, value, and quality",
            errors,
        )

        mutated = deepcopy(fixture)
        mutated["observations"][1]["value"] = "fabricated"
        errors = repository_policy.issue_98_m65_live_redacted_source_instance_errors(
            schema,
            mutated,
        )
        self.assertIn(
            "non-SUCCESS observations require null value_type, value, unit, and quality",
            errors,
        )

        mutated = deepcopy(fixture)
        mutated["feature_paths"][1]["service"] = fixture["feature_paths"][1]["feature"]
        errors = repository_policy.issue_98_m65_live_redacted_source_instance_errors(
            schema,
            mutated,
        )
        self.assertIn("eeBUS path selectors must be complete and ordered", errors)

        mutated = deepcopy(fixture)
        mutated["observations"][1]["path_index"] = 9
        errors = repository_policy.issue_98_m65_live_redacted_source_instance_errors(
            schema,
            mutated,
        )
        self.assertIn("observation path_index must select a declared feature_path", errors)

    def test_numeric_values_units_and_privacy_are_executable(self) -> None:
        schema = load_json(SCHEMA_REL)
        fixture = load_json(FIXTURE_REL)

        allowed_cases = (
            ("Measurement", "measurementListData", "DECIMAL", "21.5", "degC"),
            ("Setpoint", "setpointListData", "DECIMAL", "20", "degC"),
            ("Setpoint", "setpointListData", "BOOLEAN", "true", None),
            ("HVAC", "hvacSystemFunctionListData", "BOOLEAN", "false", None),
            ("HVAC", "hvacSystemFunctionListData", "ENUM", "ID_2", None),
        )
        for feature_type, function, value_type, value, unit in allowed_cases:
            with self.subTest(
                feature_type=feature_type,
                function=function,
                value_type=value_type,
            ):
                mutated = deepcopy(fixture)
                observation = mutated["observations"][0]
                observation["feature_type"] = feature_type
                observation["function"] = function
                observation["value_type"] = value_type
                observation["value"] = value
                observation["unit"] = unit
                self.assertTrue(schema_accepts(schema, mutated))
                self.assertEqual(
                    repository_policy.issue_98_m65_live_redacted_source_instance_errors(
                        schema,
                        mutated,
                    ),
                    [],
                )

        forbidden_pairs = (
            ("Schedule", "scheduleListData", "DECIMAL", "21.5"),
            ("DeviceClassification", "deviceClassificationManufacturerData", "ENUM", "Vaillant"),
            ("HvacSystemFunction", "hvacSystemFunctionDescriptionListData", "ENUM", "HEATING"),
            ("Measurement", "measurementListData", "BOOLEAN", "true"),
            ("Setpoint", "setpointListData", "ENUM", "AUTO"),
            ("HVAC", "hvacSystemFunctionDescriptionListData", "ENUM", "HEATING"),
        )
        for feature_type, function, value_type, value in forbidden_pairs:
            with self.subTest(feature_type=feature_type, function=function):
                mutated = deepcopy(fixture)
                observation = mutated["observations"][0]
                observation["feature_type"] = feature_type
                observation["function"] = function
                observation["value_type"] = value_type
                observation["value"] = value
                observation["unit"] = None
                self.assertFalse(schema_accepts(schema, mutated))
                self.assertIn(
                    "observation is outside the public value allowlist",
                    repository_policy.issue_98_m65_live_redacted_source_instance_errors(
                        schema,
                        mutated,
                    ),
                )

        negatives = (
            ("value", "not-a-number", "DECIMAL observations require canonical exact decimal"),
            (
                "value",
                "b1b7197b064084e4cfef" + "2365105d8d36ff185e5b",
                "public string field contains stable identity",
            ),
            ("unit", "Bearer secret", "public string field contains secret material"),
            (
                "function",
                "192.168." + "100.4",
                "public string field contains private network coordinate",
            ),
        )
        for field, value, expected in negatives:
            with self.subTest(field=field, value=value):
                mutated = deepcopy(fixture)
                mutated["observations"][0][field] = value
                errors = repository_policy.issue_98_m65_live_redacted_source_instance_errors(
                    schema,
                    mutated,
                )
                self.assertIn(expected, errors)

        mutated = deepcopy(fixture)
        mutated["observations"][0]["unit"] = "unit-with-identity=abc"
        self.assertFalse(schema_accepts(schema, mutated))

        for disguised_identity in ("Kitchen", "Vaillant"):
            with self.subTest(disguised_identity=disguised_identity):
                mutated = deepcopy(fixture)
                mutated["observations"][0]["unit"] = disguised_identity
                self.assertFalse(schema_accepts(schema, mutated))
                self.assertIn(
                    "observation unit must be null or a public protocol unit",
                    repository_policy.issue_98_m65_live_redacted_source_instance_errors(
                        schema,
                        mutated,
                    ),
                )

                mutated = deepcopy(fixture)
                observation = mutated["observations"][0]
                observation["feature_type"] = "HVAC"
                observation["function"] = "hvacSystemFunctionListData"
                observation["value_type"] = "ENUM"
                observation["value"] = disguised_identity
                observation["unit"] = None
                self.assertFalse(schema_accepts(schema, mutated))
                self.assertIn(
                    "HVAC ENUM observations require canonical opaque ID_<uint>",
                    repository_policy.issue_98_m65_live_redacted_source_instance_errors(
                        schema,
                        mutated,
                    ),
                )

        for noncanonical_enum in ("ID_", "ID_02", "ID_18446744073709551616"):
            with self.subTest(noncanonical_enum=noncanonical_enum):
                mutated = deepcopy(fixture)
                observation = mutated["observations"][0]
                observation["feature_type"] = "HVAC"
                observation["function"] = "hvacSystemFunctionListData"
                observation["value_type"] = "ENUM"
                observation["value"] = noncanonical_enum
                observation["unit"] = None
                self.assertFalse(schema_accepts(schema, mutated))

    def test_timestamp_grammar_is_identical_in_schema_and_policy(self) -> None:
        schema = load_json(SCHEMA_REL)
        timestamp = schema["$defs"]["TimestampV1"]
        self.assertEqual(timestamp["format"], "date-time")
        self.assertEqual(
            timestamp["pattern"],
            (
                "^[0-9]{4}-(0[1-9]|1[0-2])-([0-2][0-9]|3[01])"
                "T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9]"
                "(\\.[0-9]{0,8}[1-9])?Z$"
            ),
        )
        fixture = load_json(FIXTURE_REL)
        for accepted in (
            "2026-07-30T00:00:00Z",
            "2026-07-30T00:00:00.1Z",
            "2026-07-30T00:00:00.123456789Z",
        ):
            with self.subTest(accepted=accepted):
                mutated = deepcopy(fixture)
                mutated["observations"][0]["source_observed_at"] = accepted
                self.assertTrue(schema_accepts(schema, mutated))
                self.assertNotIn(
                    "observation source_observed_at must be a canonical UTC timestamp",
                    repository_policy.issue_98_m65_live_redacted_source_instance_errors(
                        schema,
                        mutated,
                    ),
                )

        for rejected in (
            "2026-07-30 00:00:00Z",
            "20260730T000000Z",
            "2026-07-30T00:00:00.10Z",
            "2026-07-30T00:00:00.1234567890Z",
            "2026-02-31T00:00:00Z",
        ):
            with self.subTest(rejected=rejected):
                mutated = deepcopy(fixture)
                mutated["observations"][0]["source_observed_at"] = rejected
                self.assertFalse(schema_accepts(schema, mutated))
                self.assertIn(
                    "observation source_observed_at must be a canonical UTC timestamp",
                    repository_policy.issue_98_m65_live_redacted_source_instance_errors(
                        schema,
                        mutated,
                    ),
                )

    def test_repository_gate_executes_the_checked_in_json_schema(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = copy_repo(Path(tmp))
            schema_path = repo / SCHEMA_REL
            schema = json.loads(schema_path.read_text(encoding="utf-8"))
            schema["properties"]["observations"] = {"type": "null"}
            schema_path.write_text(
                json.dumps(schema, indent=2) + "\n",
                encoding="utf-8",
            )
            self.assertTrue(
                any(
                    "checked-in JSON Schema rejects the positive fixture" in error
                    or "ObservationV1 schema is not exact" in error
                    for error in repository_policy.issue_98_m65_live_redacted_source_errors(
                        repo
                    )
                )
            )

        with tempfile.TemporaryDirectory() as tmp:
            repo = copy_repo(Path(tmp))
            schema_path = repo / SCHEMA_REL
            schema = json.loads(schema_path.read_text(encoding="utf-8"))
            schema["properties"]["observations"]["items"]["$ref"] = (
                "#/$defs/MissingObservationV1"
            )
            schema_path.write_text(
                json.dumps(schema, indent=2) + "\n",
                encoding="utf-8",
            )
            self.assertTrue(
                any(
                    "unresolved local JSON Schema reference" in error
                    for error in repository_policy.issue_98_m65_live_redacted_source_errors(
                        repo
                    )
                )
            )

    def test_repository_policy_binds_docs_schema_and_public_boundary(self) -> None:
        self.assertEqual(
            repository_policy.issue_98_m65_live_redacted_source_errors(ROOT),
            [],
        )

        required_markers = {
            API_REL: (
                "public-redacted M6.25 evidence source",
                "historical MSP-06 authority remains immutable",
                "owner-local raw response is not the public source payload",
                "CLOUD_APP remains pre-captured",
                "normalized value, unit, and quality",
                "Measurement/measurementListData",
                "Setpoint/setpointListData",
                "HVAC/hvacSystemFunctionListData",
                "UnitOfMeasurementType",
                "bundle-local pseudonymous service/entity/feature path",
                "MSP-065 envelope owns source authority, artifact hash, and replay hash",
                "timing, counts, and hashes",
            ),
            PROTOCOL_REL: (
                "direct typed READ",
                "bundle-local pseudonymous path",
                "no stable identity or native SPINE address",
                "normalized comparison value",
                "closed public value allowlist",
                "HVAC/hvacSystemFunctionListData",
                "UnitOfMeasurementType",
                "no cloud client, credential, refresh, or retry",
            ),
            DEVELOPMENT_REL: (
                "public-redacted M6.25 comparison exception",
                "selected normalized values are publishable",
                "Measurement/measurementListData",
                "Setpoint/setpointListData",
                "HVAC/hvacSystemFunctionListData",
                "UnitOfMeasurementType",
                "does not license owner-local raw payloads",
                "no cross-bundle correlator",
                "numeric comparison values use canonical exact decimals",
            ),
        }
        for relative, markers in required_markers.items():
            text = (ROOT / relative).read_text(encoding="utf-8")
            for marker in markers:
                with self.subTest(relative=relative, marker=marker):
                    self.assertIn(marker, text)

    def test_policy_rejects_schema_or_document_removal(self) -> None:
        for relative in (SCHEMA_REL, API_REL, PROTOCOL_REL, DEVELOPMENT_REL):
            with self.subTest(relative=relative), tempfile.TemporaryDirectory() as tmp:
                repo = copy_repo(Path(tmp))
                (repo / relative).unlink()
                errors = repository_policy.issue_98_m65_live_redacted_source_errors(
                    repo
                )
                self.assertTrue(errors)

    def test_command_inventory_remains_the_existing_five_tools(self) -> None:
        api_text = (ROOT / API_REL).read_text(encoding="utf-8")
        self.assertIn(
            '["features.get","features.data.get","features.data.set",'
            '"mutations.get","mutations.rollback"]',
            api_text,
        )
        self.assertNotIn("eebus.v2", api_text)

    def test_public_contract_cannot_add_consumer_or_semantic_surfaces(self) -> None:
        serialized = json.dumps(load_json(SCHEMA_REL), sort_keys=True).casefold()
        for forbidden in (
            "candidate_ref",
            '"ebus.v1',
            "graphql",
            "portal",
            "home assistant",
            "semantic registry",
        ):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, serialized)


if __name__ == "__main__":
    unittest.main()
