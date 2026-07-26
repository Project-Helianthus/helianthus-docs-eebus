from __future__ import annotations

import hashlib
import json
import re
import shutil
import sys
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import validate_repository_policy as repository_policy  # noqa: E402


def schema_accepts(schema: dict, definition: str, instance: object) -> bool:
    """Evaluate the Draft 2020-12 subset used by the issue-76 schema."""

    definitions = schema["$defs"]

    def matches(candidate: object, value: object) -> bool:
        if isinstance(candidate, bool):
            return candidate
        if not isinstance(candidate, dict):
            return False

        reference = candidate.get("$ref")
        if reference is not None:
            prefix = "#/$defs/"
            if not isinstance(reference, str) or not reference.startswith(prefix):
                return False
            if not matches(definitions[reference.removeprefix(prefix)], value):
                return False

        if "allOf" in candidate and not all(
            matches(part, value) for part in candidate["allOf"]
        ):
            return False
        if "anyOf" in candidate and not any(
            matches(part, value) for part in candidate["anyOf"]
        ):
            return False
        if "oneOf" in candidate and sum(
            matches(part, value) for part in candidate["oneOf"]
        ) != 1:
            return False
        if "not" in candidate and matches(candidate["not"], value):
            return False
        if "if" in candidate:
            branch = "then" if matches(candidate["if"], value) else "else"
            if branch in candidate and not matches(candidate[branch], value):
                return False

        expected_type = candidate.get("type")
        type_matches = {
            "null": value is None,
            "boolean": isinstance(value, bool),
            "integer": isinstance(value, int) and not isinstance(value, bool),
            "number": isinstance(value, (int, float)) and not isinstance(value, bool),
            "string": isinstance(value, str),
            "array": isinstance(value, list),
            "object": isinstance(value, dict),
        }
        if isinstance(expected_type, str) and not type_matches.get(expected_type, False):
            return False
        if isinstance(expected_type, list) and not any(
            type_matches.get(item, False) for item in expected_type
        ):
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
            if isinstance(pattern, str) and re.search(pattern, value) is None:
                return False

        if isinstance(value, (int, float)) and not isinstance(value, bool):
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
            if len(value) < candidate.get("minProperties", 0):
                return False
            if len(value) > candidate.get("maxProperties", len(value)):
                return False
            if not set(candidate.get("required", [])).issubset(value):
                return False

            property_name_schema = candidate.get("propertyNames")
            if property_name_schema is not None and not all(
                matches(property_name_schema, name) for name in value
            ):
                return False

            properties = candidate.get("properties", {})
            pattern_properties = candidate.get("patternProperties", {})
            for name, item in value.items():
                matched = False
                if name in properties:
                    matched = True
                    if not matches(properties[name], item):
                        return False
                for pattern, pattern_schema in pattern_properties.items():
                    if re.search(pattern, name) is not None:
                        matched = True
                        if not matches(pattern_schema, item):
                            return False
                if not matched:
                    additional = candidate.get("additionalProperties", {})
                    if additional is False or not matches(additional, item):
                        return False

        return True

    return matches(definitions[definition], instance)


def runtime_binding() -> dict:
    return {"runtime_epoch": 7, "connection_generation": 3}


def feature_locator() -> dict:
    ship_identifier_field = "ship" + "_id"
    return {
        "remote_ski": "example-remote-ski",
        ship_identifier_field: "example-ship-id",
        "device_address": "example-device",
        "entity_address": [1],
        "feature_address": 2,
        "feature_type": "example-feature",
        "feature_role": "server",
    }


def feature_target() -> dict:
    return {
        **feature_locator(),
        "function": "exampleFunction",
        "operation": "READ",
    }


def envelope_meta(tool: str, scope: str) -> dict:
    return {
        "contract": "helianthus.eebus.raw-feature-runtime.v1",
        "tool": tool,
        "scope": scope,
        "mask_tier": "raw",
        "auth_scope": scope,
        "data_timestamp": "2026-07-27T00:00:00Z",
        "data_hash": f"sha256:{'0' * 64}",
        "runtime": runtime_binding(),
    }


def features_get_envelope() -> dict:
    locator = feature_locator()
    return {
        "meta": envelope_meta("eebus.v1.features.get", "eebus.raw.read"),
        "request": {"target": locator},
        "data": {
            "feature": locator,
            "functions": [],
            "source": "live",
            "data_timestamp": "2026-07-27T00:00:00Z",
            "runtime": runtime_binding(),
            "data_hash": f"sha256:{'1' * 64}",
        },
        "error": None,
    }


def error_payload(code: str = "internal") -> dict:
    return {
        "code": code,
        "message": "fixed public-safe error",
        "retriable": False,
        "source_layer": "mcp",
    }


def mutation_record(state: str) -> dict:
    record = {
        "mutation_ref": "A" * 43,
        "state": state,
        "mode": "apply",
        "target": feature_target(),
        "runtime": runtime_binding(),
        "before": 18,
        "requested": 21,
        "protocol_accepted": None,
        "observed_after": None,
        "audit": [
            {
                "sequence": 1,
                "state": state,
                "transitioned_at": "2026-07-27T00:00:00Z",
                "previous_hash": None,
                "transition_hash": f"sha256:{'2' * 64}",
            }
        ],
    }
    if state == "applied":
        record.update(
            {
                "protocol_accepted": True,
                "observed_after": 21,
                "apply_verification": {
                    "relation": "observed_after_equals_requested",
                    "verified": True,
                    "equal_value_hash": f"sha256:{'3' * 64}",
                    "verified_at": "2026-07-27T00:00:00Z",
                },
            }
        )
    elif state == "rolled_back":
        record.update(
            {
                "protocol_accepted": True,
                "observed_after": 21,
                "apply_verification": {
                    "relation": "observed_after_equals_requested",
                    "verified": True,
                    "equal_value_hash": f"sha256:{'3' * 64}",
                    "verified_at": "2026-07-27T00:00:00Z",
                },
                "rollback": {
                    "state": "rolled_back",
                    "before": 18,
                    "protocol_accepted": True,
                    "observed_after": 18,
                    "verification": {
                        "relation": "rollback_observed_after_equals_before",
                        "verified": True,
                        "equal_value_hash": f"sha256:{'4' * 64}",
                        "verified_at": "2026-07-27T00:00:00Z",
                    },
                },
            }
        )
    elif state == "outcome_unknown":
        record.update(
            {
                "error": error_payload("outcome_unknown"),
                "outcome_evidence": {
                    "possible_side_effect": True,
                    "blind_retry_forbidden": True,
                    "last_durable_state": "dispatch_intent",
                    "recorded_at": "2026-07-27T00:00:00Z",
                },
            }
        )
    elif state == "conflict":
        record.update(
            {
                "observed_after": 19,
                "error": error_payload("conflict"),
                "conflict_evidence": {
                    "relation": "observed_after_differs_from_before_and_requested",
                    "verified": True,
                    "before_hash": f"sha256:{'5' * 64}",
                    "requested_hash": f"sha256:{'6' * 64}",
                    "observed_after_hash": f"sha256:{'7' * 64}",
                    "verified_at": "2026-07-27T00:00:00Z",
                },
            }
        )
    elif state == "failed_no_contact":
        record.update(
            {
                "error": error_payload("permission_denied"),
                "no_contact_evidence": {
                    "remote_frames_sent": 0,
                    "last_completed_phase": "authentication",
                    "verified_at": "2026-07-27T00:00:00Z",
                },
            }
        )
    elif state == "rejected":
        record.update(
            {
                "protocol_accepted": False,
                "observed_after": 18,
                "error": error_payload("remote_error"),
                "rejection_verification": {
                    "relation": "observed_after_equals_before",
                    "verified": True,
                    "correlated_rejection": True,
                    "equal_value_hash": f"sha256:{'5' * 64}",
                    "verified_at": "2026-07-27T00:00:00Z",
                },
            }
        )
    return record


def copy_repo(tmp_path: Path) -> Path:
    destination = tmp_path / "repo"
    required = {
        *repository_policy.ISSUE76_DOCUMENT_RELS,
        repository_policy.ISSUE76_SCHEMA_REL,
        *repository_policy.ISSUE76_M6_LOCKED_ARTIFACTS,
    }
    for relative in required:
        source = ROOT / relative
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    return destination


class Issue76M625RawFeatureContractTests(unittest.TestCase):
    maxDiff = None

    def test_validator_has_the_complete_issue_76_contract_inventory(self) -> None:
        self.assertEqual(
            repository_policy.issue_76_m625_raw_feature_errors.__doc__,
            "Enforce the additive M6.25 raw feature acquisition contract.",
        )
        self.assertEqual(
            repository_policy.ISSUE76_TOOL_NAMES,
            {
                "eebus.v1.features.get",
                "eebus.v1.features.data.get",
                "eebus.v1.features.data.set",
                "eebus.v1.mutations.get",
                "eebus.v1.mutations.rollback",
            },
        )
        self.assertEqual(
            repository_policy.ISSUE76_TOOL_SCOPES,
            {
                "eebus.v1.features.get": "eebus.raw.read",
                "eebus.v1.features.data.get": "eebus.raw.read",
                "eebus.v1.features.data.set": "eebus.raw.write",
                "eebus.v1.mutations.get": "eebus.raw.read",
                "eebus.v1.mutations.rollback": "eebus.raw.write",
            },
        )
        self.assertEqual(
            repository_policy.ISSUE76_MUTATION_STATES,
            {
                "prepared",
                "dispatch_intent",
                "reply_observed",
                "verify_pending",
                "applied",
                "probe_active",
                "rollback_intent",
                "rollback_dispatch_intent",
                "rollback_reply_observed",
                "rollback_verify_pending",
                "rolled_back",
                "outcome_unknown",
                "conflict",
                "failed_no_contact",
                "rejected",
            },
        )

    def test_forward_contract_is_complete(self) -> None:
        self.assertEqual(
            repository_policy.issue_76_m625_raw_feature_errors(ROOT),
            [],
        )

    def test_m6_completion_and_stable_protocol_remain_byte_identical(self) -> None:
        for relative, expected_sha256 in repository_policy.ISSUE76_M6_LOCKED_ARTIFACTS.items():
            self.assertEqual(
                hashlib.sha256((ROOT / relative).read_bytes()).hexdigest(),
                expected_sha256,
                relative.as_posix(),
            )

    def test_machine_schema_closes_the_exact_additive_surface(self) -> None:
        schema = json.loads(
            (ROOT / repository_policy.ISSUE76_SCHEMA_REL).read_text(encoding="utf-8")
        )
        self.assertFalse(schema["additionalProperties"])
        self.assertEqual(schema["properties"]["namespace"]["const"], "eebus.v1")
        self.assertEqual(schema["properties"]["mask_tier"]["const"], "raw")
        self.assertEqual(
            schema["properties"]["transport"]["const"],
            "owner-only-af-unix",
        )
        self.assertEqual(
            schema["properties"]["public_contact_policy"]["const"],
            "deny-before-provider-router-runtime-contact",
        )
        self.assertEqual(
            set(schema["$defs"]["ToolV1"]["enum"]),
            repository_policy.ISSUE76_TOOL_NAMES,
        )
        self.assertEqual(
            schema["x-tool-scopes"],
            repository_policy.ISSUE76_TOOL_SCOPES,
        )
        self.assertEqual(
            set(schema["$defs"]["MutationStateV1"]["enum"]),
            repository_policy.ISSUE76_MUTATION_STATES,
        )
        self.assertEqual(schema["$defs"]["ModeV1"]["enum"], ["apply", "probe"])
        self.assertEqual(
            schema["x-command-path"],
            [
                "MCP",
                "gateway EEBusCommandRouter",
                "eebusreg RawFeatureRuntimeV1",
                "eebusreg durable mutation coordinator",
                "eebus-go exact feature executor",
                "spine-go atomic correlated round trip",
                "existing SHIP session",
            ],
        )
        self.assertEqual(
            schema["x-round-trip"],
            {
                "registerWaiterBeforeSend": True,
                "completeExactlyOnce": True,
                "cleanupOnEveryTerminalPath": True,
                "generationBoundMonotonicKey": True,
                "retainGenerationTombstone": True,
                "rejectRetiredKeyReuse": True,
                "lateReplyCannotCompleteSuccessor": True,
            },
        )
        self.assertEqual(
            schema["x-secret-denylist"],
            repository_policy.ISSUE76_SECRET_DENYLIST,
        )
        self.assertEqual(
            set(schema["$defs"]["FeatureDataSetRequestV1"]["required"]),
            {
                "target",
                "value",
                "read_token",
                "idempotency_key",
                "mode",
            },
        )
        self.assertEqual(
            set(schema["$defs"]["FeatureDataSetRequestV1"]["properties"]),
            {
                "target",
                "value",
                "read_token",
                "expected_current",
                "idempotency_key",
                "mode",
                "probe_ttl_seconds",
                "constraints_override",
            },
        )
        self.assertEqual(
            set(schema["$defs"]["MutationV1"]["required"]),
            {
                "mutation_ref",
                "state",
                "mode",
                "target",
                "runtime",
                "before",
                "requested",
                "protocol_accepted",
                "observed_after",
                "audit",
            },
        )

    def test_machine_schema_forbids_non_m625_surfaces(self) -> None:
        schema = json.loads(
            (ROOT / repository_policy.ISSUE76_SCHEMA_REL).read_text(encoding="utf-8")
        )
        serialized = json.dumps(schema, sort_keys=True).casefold()
        for forbidden in (
            "eebus.v2",
            "features.data.invoke",
            "candidate_ref",
            "filterdelete",
            "partialselector",
            "graphql",
            "portal",
            "home assistant",
        ):
            self.assertNotIn(forbidden, serialized)
        for definition in (
            "FeaturesGetRequestV1",
            "FeatureDataGetRequestV1",
            "FeatureDataSetRequestV1",
            "MutationGetRequestV1",
            "MutationRollbackRequestV1",
        ):
            self.assertFalse(schema["$defs"][definition]["additionalProperties"])

    def test_envelope_schema_rejects_cross_tool_and_exclusivity_mismatches(self) -> None:
        schema = json.loads(
            (ROOT / repository_policy.ISSUE76_SCHEMA_REL).read_text(encoding="utf-8")
        )
        valid = features_get_envelope()
        self.assertTrue(schema_accepts(schema, "EnvelopeV1", valid))

        invalid = {}
        wrong_scope = deepcopy(valid)
        wrong_scope["meta"]["scope"] = "eebus.raw.write"
        invalid["wrong scope"] = wrong_scope

        wrong_auth_scope = deepcopy(valid)
        wrong_auth_scope["meta"]["auth_scope"] = "eebus.raw.write"
        invalid["wrong auth scope"] = wrong_auth_scope

        wrong_request = deepcopy(valid)
        wrong_request["request"] = {"mutation_ref": "B" * 43}
        invalid["wrong request payload"] = wrong_request

        wrong_data = deepcopy(valid)
        wrong_data["data"] = {"results": [], "failures": [], "complete": True}
        invalid["wrong response payload"] = wrong_data

        both = deepcopy(valid)
        both["error"] = error_payload()
        invalid["both data and error"] = both

        neither = deepcopy(valid)
        neither["data"] = None
        neither["error"] = None
        invalid["neither data nor error"] = neither

        for name, instance in invalid.items():
            with self.subTest(name=name):
                self.assertFalse(schema_accepts(schema, "EnvelopeV1", instance))

        error_envelope = deepcopy(valid)
        error_envelope["data"] = None
        error_envelope["error"] = error_payload()
        self.assertTrue(schema_accepts(schema, "EnvelopeV1", error_envelope))

    def test_mutation_schema_rejects_incoherent_terminal_evidence(self) -> None:
        schema = json.loads(
            (ROOT / repository_policy.ISSUE76_SCHEMA_REL).read_text(encoding="utf-8")
        )
        terminal_states = (
            "applied",
            "rolled_back",
            "outcome_unknown",
            "conflict",
            "failed_no_contact",
            "rejected",
        )
        for state in terminal_states:
            with self.subTest(state=state):
                self.assertTrue(
                    schema_accepts(schema, "MutationV1", mutation_record(state))
                )

        invalid = {}
        applied_without_acceptance = mutation_record("applied")
        applied_without_acceptance["protocol_accepted"] = False
        invalid["applied protocol acceptance"] = applied_without_acceptance

        applied_without_verification = mutation_record("applied")
        del applied_without_verification["apply_verification"]
        invalid["applied request equality"] = applied_without_verification

        rolled_back_without_readback = mutation_record("rolled_back")
        rolled_back_without_readback["rollback"]["observed_after"] = None
        invalid["rollback readback"] = rolled_back_without_readback

        rolled_back_without_verification = mutation_record("rolled_back")
        del rolled_back_without_verification["rollback"]["verification"]
        invalid["rollback before equality"] = rolled_back_without_verification

        rolled_back_with_conflict = mutation_record("rolled_back")
        rolled_back_with_conflict["conflict_evidence"] = mutation_record("conflict")[
            "conflict_evidence"
        ]
        invalid["rolled back contradictory evidence"] = rolled_back_with_conflict

        outcome_without_evidence = mutation_record("outcome_unknown")
        del outcome_without_evidence["outcome_evidence"]
        invalid["outcome unknown evidence"] = outcome_without_evidence

        conflict_without_evidence = mutation_record("conflict")
        del conflict_without_evidence["conflict_evidence"]
        invalid["conflict evidence"] = conflict_without_evidence

        conflict_without_observation = mutation_record("conflict")
        conflict_without_observation["observed_after"] = None
        invalid["conflict observation"] = conflict_without_observation

        contact_without_evidence = mutation_record("failed_no_contact")
        del contact_without_evidence["no_contact_evidence"]
        invalid["failed no contact evidence"] = contact_without_evidence

        contact_with_frame = mutation_record("failed_no_contact")
        contact_with_frame["no_contact_evidence"]["remote_frames_sent"] = 1
        invalid["failed no contact frame count"] = contact_with_frame

        rejected_without_verification = mutation_record("rejected")
        del rejected_without_verification["rejection_verification"]
        invalid["rejected verification"] = rejected_without_verification

        rejected_without_readback = mutation_record("rejected")
        rejected_without_readback["observed_after"] = None
        invalid["rejected readback"] = rejected_without_readback

        for name, instance in invalid.items():
            with self.subTest(name=name):
                self.assertFalse(schema_accepts(schema, "MutationV1", instance))

    def test_typed_values_reject_recursive_secret_keys_and_values(self) -> None:
        schema = json.loads(
            (ROOT / repository_policy.ISSUE76_SCHEMA_REL).read_text(encoding="utf-8")
        )
        legitimate_unknown = {
            "vendorOpaque": {
                "calibrationSlot": "opaque-value",
                "values": [1, "normal"],
            }
        }
        self.assertTrue(schema_accepts(schema, "TypedValueV1", legitimate_unknown))
        self.assertEqual(
            repository_policy.issue_76_secret_boundary_errors(legitimate_unknown),
            [],
        )

        secret_fixtures = {
            "nested underscore key": {
                "vendorOpaque": {"private_key": "opaque-value"}
            },
            "nested camel key": {
                "vendorOpaque": {"credentialToken": "opaque-value"}
            },
            "nested separator key": {
                "vendorOpaque": {"PRIVATE-PEM": "opaque-value"}
            },
            "private PEM value": {
                "vendorOpaque": "-----BEGIN " + "PRIVATE KEY-----\nredacted"
            },
            "bearer value": {"vendorOpaque": "Bearer redacted-token"},
        }
        for name, instance in secret_fixtures.items():
            with self.subTest(name=name):
                self.assertFalse(schema_accepts(schema, "TypedValueV1", instance))
                self.assertTrue(
                    repository_policy.issue_76_secret_boundary_errors(instance)
                )

        normalized_only = {"vendorOpaque": {"ｐｒｉｖａｔｅ＿ｋｅｙ": "opaque-value"}}
        self.assertTrue(schema_accepts(schema, "TypedValueV1", normalized_only))
        self.assertTrue(
            repository_policy.issue_76_secret_boundary_errors(normalized_only)
        )

    def test_docs_cross_link_the_protocol_architecture_api_and_policy_contracts(self) -> None:
        documents = {
            relative: (ROOT / relative).read_text(encoding="utf-8")
            for relative in repository_policy.ISSUE76_DOCUMENT_RELS
        }
        normalized = {
            relative: " ".join(text.split()).casefold()
            for relative, text in documents.items()
        }
        for relative, markers in repository_policy.ISSUE76_REQUIRED_MARKERS.items():
            for marker in markers:
                self.assertIn(marker.casefold(), normalized[relative], relative.as_posix())
        for relative, text in documents.items():
            for peer in repository_policy.ISSUE76_DOCUMENT_RELS:
                if peer == relative:
                    continue
                self.assertIn(peer.name, text, f"{relative} does not link {peer}")

    def test_validator_rejects_each_missing_issue_76_artifact(self) -> None:
        required = {
            *repository_policy.ISSUE76_DOCUMENT_RELS,
            repository_policy.ISSUE76_SCHEMA_REL,
        }
        for relative in required:
            with self.subTest(relative=relative), tempfile.TemporaryDirectory() as tmp:
                repo = copy_repo(Path(tmp))
                (repo / relative).unlink()

                errors = repository_policy.issue_76_m625_raw_feature_errors(repo)

                self.assertTrue(
                    any(relative.as_posix() in error and "missing" in error for error in errors),
                    errors,
                )

    def test_validator_rejects_m6_lock_mutation(self) -> None:
        for relative in repository_policy.ISSUE76_M6_LOCKED_ARTIFACTS:
            with self.subTest(relative=relative), tempfile.TemporaryDirectory() as tmp:
                repo = copy_repo(Path(tmp))
                path = repo / relative
                path.write_bytes(path.read_bytes() + b"\nissue-76-lock-probe\n")

                errors = repository_policy.issue_76_m625_raw_feature_errors(repo)

                self.assertTrue(
                    any(relative.as_posix() in error and "byte-identical" in error for error in errors),
                    errors,
                )

    def test_validator_rejects_weakened_machine_contract(self) -> None:
        mutations = {
            "public contact": lambda schema: schema["properties"][
                "public_contact_policy"
            ].update({"const": "deny-after-runtime-contact"}),
            "tool scope": lambda schema: schema["x-tool-scopes"].update(
                {"eebus.v1.features.data.set": "eebus.raw.read"}
            ),
            "mutation state": lambda schema: schema["$defs"]["MutationStateV1"][
                "enum"
            ].remove("outcome_unknown"),
            "round trip": lambda schema: schema["x-round-trip"].update(
                {"registerWaiterBeforeSend": False}
            ),
            "write token": lambda schema: schema["$defs"][
                "FeatureDataSetRequestV1"
            ]["required"].remove("read_token"),
            "discriminated envelope": lambda schema: schema["$defs"]["EnvelopeV1"][
                "oneOf"
            ].pop(),
            "applied evidence": lambda schema: schema["$defs"]["MutationV1"][
                "oneOf"
            ][4]["required"].remove("apply_verification"),
            "recursive secret key rejection": lambda schema: schema["$defs"][
                "TypedValueV1"
            ]["oneOf"][2].update({"propertyNames": {"type": "string"}}),
        }
        for name, mutate in mutations.items():
            with self.subTest(name=name), tempfile.TemporaryDirectory() as tmp:
                repo = copy_repo(Path(tmp))
                path = repo / repository_policy.ISSUE76_SCHEMA_REL
                schema = json.loads(path.read_text(encoding="utf-8"))
                mutate(schema)
                path.write_text(json.dumps(schema), encoding="utf-8")

                errors = repository_policy.issue_76_m625_raw_feature_errors(repo)

                self.assertTrue(any(name in error for error in errors), errors)


if __name__ == "__main__":
    unittest.main()
