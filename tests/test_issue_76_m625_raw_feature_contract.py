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
        "feature_type": "Measurement",
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


def feature_data_get_partial_envelope() -> dict:
    target = feature_target()
    return {
        "meta": envelope_meta(
            "eebus.v1.features.data.get",
            "eebus.raw.read",
        ),
        "request": {"targets": [target]},
        "data": {
            "results": [],
            "failures": [
                {
                    "target_index": 0,
                    "target": target,
                    "error": error_payload("remote_error"),
                }
            ],
            "complete": False,
        },
        "error": error_payload("partial_result"),
    }


def read_observation() -> dict:
    target = feature_target()
    response_value = {"exampleValue": 21}
    return {
        "target": target,
        "runtime": runtime_binding(),
        "raw_request": {
            "classifier": "READ",
            "correlation_key": 41,
            "function": target["function"],
            "data": {},
        },
        "raw_response": {
            "classifier": "REPLY",
            "correlation_key": 41,
            "function": target["function"],
            "data": response_value,
        },
        "value": deepcopy(response_value),
        "requested_at": "2026-07-27T00:00:00Z",
        "received_at": "2026-07-27T00:00:01Z",
        "data_timestamp": "2026-07-27T00:00:01Z",
        "source": "live",
        "read_token": {
            "read_token": "R" * 43,
            "reusable": False,
            "expires_at": "2026-07-27T00:05:00Z",
            "binding_hash": f"sha256:{'8' * 64}",
        },
        "data_hash": f"sha256:{'9' * 64}",
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
    elif state == "no_effect":
        record.update(
            {
                "protocol_accepted": None,
                "observed_after": 18,
                "error": error_payload("no_effect"),
                "outcome_evidence": {
                    "possible_side_effect": True,
                    "blind_retry_forbidden": True,
                    "last_durable_state": "dispatch_intent",
                    "recorded_at": "2026-07-27T00:00:00Z",
                },
                "no_effect_verification": {
                    "relation": "observed_after_equals_before",
                    "verified": True,
                    "equal_value_hash": f"sha256:{'5' * 64}",
                    "verified_at": "2026-07-27T00:00:00Z",
                },
            }
        )
    elif state == "conflict":
        record.update(
            {
                "observed_after": 19,
                "error": error_payload("conflict"),
                "outcome_evidence": {
                    "possible_side_effect": True,
                    "blind_retry_forbidden": True,
                    "last_durable_state": "dispatch_intent",
                    "recorded_at": "2026-07-27T00:00:00Z",
                },
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


def mutation_intermediate_record(state: str, protocol_accepted: bool) -> dict:
    record = mutation_record(state)
    record["protocol_accepted"] = protocol_accepted
    return record


def rollback_intermediate_record(
    state: str,
    protocol_accepted: bool = True,
) -> dict:
    record = mutation_record("applied")
    record["state"] = state
    record["audit"][0]["state"] = state
    rollback_protocol_accepted = (
        protocol_accepted
        if state in {"rollback_reply_observed", "rollback_verify_pending"}
        else None
    )
    record["rollback"] = {
        "state": state,
        "before": 18,
        "protocol_accepted": rollback_protocol_accepted,
        "observed_after": None,
    }
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
                "no_effect",
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
                "eebusreg RawFeatureRuntimeV1 or RawMutationRuntimeV1",
                "eebusreg internal durable mutation coordinator for mutation methods",
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
            schema["x-runtime-admission"],
            repository_policy.ISSUE84_RUNTIME_ADMISSION,
        )
        self.assertEqual(
            schema["x-local-protocol-source"],
            repository_policy.ISSUE84_LOCAL_PROTOCOL_SOURCE,
        )
        self.assertEqual(
            schema["$defs"]["NativeFeatureTypeV1"],
            repository_policy.ISSUE84_NATIVE_FEATURE_TYPE,
        )
        for definition in ("FeatureLocatorV1", "FeatureTargetV1"):
            self.assertEqual(
                schema["$defs"][definition]["properties"]["feature_type"],
                {"$ref": "#/$defs/NativeFeatureTypeV1"},
            )
        self.assertEqual(
            schema["x-secret-denylist"],
            repository_policy.ISSUE76_SECRET_DENYLIST,
        )
        self.assertTrue(
            schema["x-public-runtime-api"]["RawFeatureRuntimeV1"]["readOnly"]
        )
        self.assertEqual(
            schema["x-public-runtime-api"]["RawFeatureRuntimeV1"]["compatibility"],
            "unchanged",
        )
        self.assertEqual(
            schema["x-public-runtime-api"]["Runtime"]["methodSet"],
            "unchanged",
        )
        self.assertEqual(
            schema["x-public-runtime-api"]["Runtime"]["methods"],
            [
                "Start(context.Context) error",
                "Shutdown() error",
                "Snapshot() (SnapshotV1, error)",
                "PairingState() ([]PairingObservationV1, error)",
            ],
        )
        self.assertEqual(
            schema["x-public-runtime-api"]["Runtime"]["doesNotEmbed"],
            ["RawMutationRuntimeV1"],
        )
        self.assertEqual(
            schema["x-authorization-validators"]["ValidateWriteAuthorizationV1"],
            {
                "authorization": "WriteAuthorizationV1",
                "scope": "AuthScopeV1RawWrite",
                "tools": [
                    "eebus.v1.features.data.set",
                    "eebus.v1.mutations.rollback",
                ],
            },
        )
        self.assertEqual(
            schema["$defs"]["AuthScopeV1RawWrite"],
            {"const": "eebus.raw.write"},
        )
        self.assertEqual(
            schema["x-canonical-dto-validation"],
            {
                "owner": "Project-Helianthus/helianthus-eebusreg/eebusraw",
                "requestValidators": list(
                    repository_policy.ISSUE82_CANONICAL_DTO_VALIDATORS[:3]
                ),
                "resultValidators": list(
                    repository_policy.ISSUE82_CANONICAL_DTO_VALIDATORS[3:]
                ),
                "signatures": (
                    repository_policy.ISSUE82_CANONICAL_DTO_VALIDATOR_SIGNATURES
                ),
                "gatewayResidualResponsibilities": list(
                    repository_policy.ISSUE82_GATEWAY_RESIDUAL_RESPONSIBILITIES
                ),
                "gatewayMustNotReimplement": "closed DTO semantics",
            },
        )
        self.assertEqual(
            schema["x-wal-restore-policy"],
            repository_policy.ISSUE87_WAL_RESTORE_POLICY,
        )
        self.assertNotIn("PreBindingErrorCodeV1", schema["$defs"])
        self.assertNotIn("PostBindingErrorCodeV1", schema["$defs"])
        self.assertEqual(
            schema["$defs"]["ErrorCodeV1"]["enum"],
            list(repository_policy.ISSUE92_ERROR_CODES),
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

    def test_issue_92_error_binding_is_operation_stage_driven(self) -> None:
        schema = json.loads(
            (ROOT / repository_policy.ISSUE76_SCHEMA_REL).read_text(encoding="utf-8")
        )
        self.assertNotIn("PreBindingErrorCodeV1", schema["$defs"])
        self.assertNotIn("PostBindingErrorCodeV1", schema["$defs"])

        for code in ("stale_read_token", "disconnected"):
            for runtime in (runtime_binding(), None):
                with self.subTest(code=code, runtime=runtime):
                    envelope = features_get_envelope()
                    envelope["meta"]["runtime"] = runtime
                    envelope["data"] = None
                    envelope["error"] = error_payload(code)
                    envelope["error"]["source_layer"] = "eebusreg-runtime"
                    self.assertTrue(schema_accepts(schema, "EnvelopeV1", envelope))

        prose = (ROOT / repository_policy.ISSUE76_API_REL).read_text(
            encoding="utf-8"
        )
        self.assertIn(
            "Binding presence is determined by the operation stage, not by the error code",
            prose,
        )
        self.assertIn("A post-error runtime lookup is forbidden", prose)

    def test_issue_86_canonical_full_read_request_data_is_allowed_and_typed(
        self,
    ) -> None:
        schema = json.loads(
            (ROOT / repository_policy.ISSUE76_SCHEMA_REL).read_text(encoding="utf-8")
        )
        observation = read_observation()
        request_message = observation["raw_request"]

        self.assertTrue(
            schema_accepts(
                schema,
                "FullReadRequestMessageV1",
                request_message,
            )
        )
        self.assertTrue(schema_accepts(schema, "ReadObservationV1", observation))

        request_without_data = deepcopy(request_message)
        del request_without_data["data"]
        self.assertTrue(
            schema_accepts(
                schema,
                "FullReadRequestMessageV1",
                request_without_data,
            )
        )

        malformed_request_data = deepcopy(request_message)
        malformed_request_data["data"] = {
            "level1": {"level2": {"level3": {"level4": "too-deep"}}}
        }
        self.assertFalse(
            schema_accepts(
                schema,
                "FullReadRequestMessageV1",
                malformed_request_data,
            )
        )
        malformed_observation = deepcopy(observation)
        malformed_observation["raw_request"] = malformed_request_data
        self.assertFalse(
            schema_accepts(schema, "ReadObservationV1", malformed_observation)
        )

    def test_issue_86_context_specific_read_message_shapes_reject_mismatches(
        self,
    ) -> None:
        schema = json.loads(
            (ROOT / repository_policy.ISSUE76_SCHEMA_REL).read_text(encoding="utf-8")
        )
        observation = read_observation()
        invalid = {}

        write_request = deepcopy(observation)
        write_request["raw_request"]["classifier"] = "WRITE"
        invalid["request classifier WRITE"] = write_request

        request_error = deepcopy(observation)
        request_error["raw_request"]["error_number"] = 1
        invalid["request error_number"] = request_error

        response_error = deepcopy(observation)
        response_error["raw_response"]["error_number"] = 1
        invalid["response error_number"] = response_error

        result_response = deepcopy(observation)
        result_response["raw_response"]["classifier"] = "RESULT"
        invalid["response classifier RESULT"] = result_response

        missing_response_data = deepcopy(observation)
        del missing_response_data["raw_response"]["data"]
        invalid["missing response data"] = missing_response_data

        null_response_data = deepcopy(observation)
        null_response_data["raw_response"]["data"] = None
        invalid["null response data"] = null_response_data

        for name, instance in invalid.items():
            with self.subTest(name=name):
                self.assertFalse(schema_accepts(schema, "ReadObservationV1", instance))

    def test_issue_86_cross_field_equality_remains_a_go_validator_obligation(
        self,
    ) -> None:
        schema = json.loads(
            (ROOT / repository_policy.ISSUE76_SCHEMA_REL).read_text(encoding="utf-8")
        )
        self.assertEqual(
            schema["x-read-observation-invariants"],
            repository_policy.ISSUE86_READ_OBSERVATION_INVARIANTS,
        )

        observation = read_observation()
        self.assertTrue(schema_accepts(schema, "ReadObservationV1", observation))

        mismatched = {}
        correlation = deepcopy(observation)
        correlation["raw_response"]["correlation_key"] += 1
        mismatched["correlation"] = correlation

        function = deepcopy(observation)
        function["raw_response"]["function"] = "differentFunction"
        mismatched["function"] = function

        value = deepcopy(observation)
        value["value"] = {"exampleValue": 22}
        mismatched["value"] = value

        for name, instance in mismatched.items():
            with self.subTest(name=name):
                self.assertTrue(schema_accepts(schema, "ReadObservationV1", instance))

        invariants = schema["x-read-observation-invariants"]
        self.assertEqual(invariants["validator"], "ValidateFeatureDataGetDataV1")
        self.assertIn("equals", invariants["correlationBinding"])
        self.assertIn("equals", invariants["functionBinding"])
        self.assertIn("equals", invariants["valueBinding"])

    def test_issue_86_read_request_rejects_write_targets_and_narrowing_fields(
        self,
    ) -> None:
        schema = json.loads(
            (ROOT / repository_policy.ISSUE76_SCHEMA_REL).read_text(encoding="utf-8")
        )
        request = {"targets": [feature_target()]}
        self.assertTrue(schema_accepts(schema, "ReadFeatureTargetV1", feature_target()))
        self.assertTrue(schema_accepts(schema, "FeatureDataGetRequestV1", request))

        write_request = deepcopy(request)
        write_request["targets"][0]["operation"] = "WRITE"
        self.assertFalse(
            schema_accepts(
                schema,
                "ReadFeatureTargetV1",
                write_request["targets"][0],
            )
        )
        self.assertFalse(
            schema_accepts(schema, "FeatureDataGetRequestV1", write_request)
        )

        narrowing_fields = {
            "selector": {},
            "elements": [],
            "filter": {},
            "partial": True,
        }
        for field, value in narrowing_fields.items():
            with self.subTest(field=field):
                widened = deepcopy(request)
                widened[field] = value
                self.assertFalse(
                    schema_accepts(schema, "FeatureDataGetRequestV1", widened)
                )

    def test_issue_84_native_measurement_round_trip_rejects_lowercase_alias(
        self,
    ) -> None:
        schema = json.loads(
            (ROOT / repository_policy.ISSUE76_SCHEMA_REL).read_text(encoding="utf-8")
        )
        locator = feature_locator()
        target = feature_target()
        envelope = features_get_envelope()

        self.assertEqual(locator["feature_type"], "Measurement")
        self.assertEqual(
            envelope["request"]["target"]["feature_type"],
            envelope["data"]["feature"]["feature_type"],
        )
        self.assertTrue(schema_accepts(schema, "FeatureLocatorV1", locator))
        self.assertTrue(schema_accepts(schema, "FeatureTargetV1", target))
        self.assertTrue(schema_accepts(schema, "EnvelopeV1", envelope))

        lowercase_locator = deepcopy(locator)
        lowercase_locator["feature_type"] = "measurement"
        self.assertFalse(
            schema_accepts(schema, "FeatureLocatorV1", lowercase_locator)
        )

        lowercase_target = deepcopy(target)
        lowercase_target["feature_type"] = "measurement"
        self.assertFalse(
            schema_accepts(schema, "FeatureTargetV1", lowercase_target)
        )

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

        for code in (
            code
            for code in repository_policy.ISSUE92_ERROR_CODES
            if code != "partial_result"
        ):
            for runtime in (runtime_binding(), None):
                with self.subTest(error_code=code, runtime=runtime):
                    operation_error = deepcopy(error_envelope)
                    operation_error["meta"]["runtime"] = runtime
                    operation_error["error"] = error_payload(code)
                    self.assertTrue(
                        schema_accepts(schema, "EnvelopeV1", operation_error)
                    )

        success_without_runtime = deepcopy(valid)
        success_without_runtime["meta"]["runtime"] = None
        self.assertFalse(
            schema_accepts(schema, "EnvelopeV1", success_without_runtime)
        )

        write_target = feature_target()
        write_target["operation"] = "WRITE"
        mutation = {
            "meta": envelope_meta(
                "eebus.v1.features.data.set",
                "eebus.raw.write",
            ),
            "request": {
                "target": write_target,
                "value": 21,
                "read_token": "R" * 43,
                "idempotency_key": "issue-84-example-1",
                "mode": "apply",
            },
            "data": mutation_record("applied"),
            "error": None,
        }
        self.assertTrue(schema_accepts(schema, "EnvelopeV1", mutation))

        mutation_without_meta_runtime = deepcopy(mutation)
        mutation_without_meta_runtime["meta"]["runtime"] = None
        self.assertFalse(
            schema_accepts(
                schema,
                "EnvelopeV1",
                mutation_without_meta_runtime,
            )
        )

        mutation_without_data_runtime = deepcopy(mutation)
        del mutation_without_data_runtime["data"]["runtime"]
        self.assertFalse(
            schema_accepts(
                schema,
                "EnvelopeV1",
                mutation_without_data_runtime,
            )
        )

        partial = feature_data_get_partial_envelope()
        self.assertTrue(schema_accepts(schema, "EnvelopeV1", partial))

        partial_without_runtime = deepcopy(partial)
        partial_without_runtime["meta"]["runtime"] = None
        self.assertFalse(
            schema_accepts(schema, "EnvelopeV1", partial_without_runtime)
        )

        partial_without_request = deepcopy(partial)
        partial_without_request["request"] = None
        self.assertFalse(
            schema_accepts(schema, "EnvelopeV1", partial_without_request)
        )

        malformed = deepcopy(error_envelope)
        malformed["meta"]["runtime"] = None
        malformed["request"] = None
        malformed["error"] = error_payload("invalid_argument")
        self.assertTrue(schema_accepts(schema, "EnvelopeV1", malformed))

        malformed_with_fabricated_runtime = deepcopy(malformed)
        malformed_with_fabricated_runtime["meta"]["runtime"] = runtime_binding()
        self.assertFalse(
            schema_accepts(schema, "EnvelopeV1", malformed_with_fabricated_runtime)
        )

        untyped_non_validation_error = deepcopy(malformed)
        untyped_non_validation_error["error"] = error_payload("internal")
        self.assertFalse(
            schema_accepts(schema, "EnvelopeV1", untyped_non_validation_error)
        )

        malformed_from_router = deepcopy(malformed)
        malformed_from_router["error"]["source_layer"] = "gateway-router"
        self.assertFalse(
            schema_accepts(schema, "EnvelopeV1", malformed_from_router)
        )

        malformed_echo = deepcopy(malformed)
        malformed_echo["error"]["details"] = {"raw_input": "not echoed"}
        self.assertFalse(
            schema_accepts(schema, "EnvelopeV1", malformed_echo)
        )

    def test_mutation_schema_rejects_incoherent_terminal_evidence(self) -> None:
        schema = json.loads(
            (ROOT / repository_policy.ISSUE76_SCHEMA_REL).read_text(encoding="utf-8")
        )
        terminal_states = (
            "applied",
            "rolled_back",
            "no_effect",
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

        no_effect_without_uncertainty = mutation_record("no_effect")
        del no_effect_without_uncertainty["outcome_evidence"]
        invalid["no effect uncertainty evidence"] = no_effect_without_uncertainty

        no_effect_without_verification = mutation_record("no_effect")
        del no_effect_without_verification["no_effect_verification"]
        invalid["no effect verification"] = no_effect_without_verification

        no_effect_with_acceptance = mutation_record("no_effect")
        no_effect_with_acceptance["protocol_accepted"] = True
        invalid["no effect protocol acceptance"] = no_effect_with_acceptance

        no_effect_without_readback = mutation_record("no_effect")
        no_effect_without_readback["observed_after"] = None
        invalid["no effect readback"] = no_effect_without_readback

        no_effect_retriable = mutation_record("no_effect")
        no_effect_retriable["error"]["retriable"] = True
        invalid["no effect retriable"] = no_effect_retriable

        no_effect_from_rollback = mutation_record("no_effect")
        no_effect_from_rollback["outcome_evidence"][
            "last_durable_state"
        ] = "rollback_dispatch_intent"
        invalid["no effect rollback evidence"] = no_effect_from_rollback

        conflict_without_evidence = mutation_record("conflict")
        del conflict_without_evidence["conflict_evidence"]
        invalid["conflict evidence"] = conflict_without_evidence

        conflict_without_observation = mutation_record("conflict")
        conflict_without_observation["observed_after"] = None
        invalid["conflict observation"] = conflict_without_observation

        uncertain_conflict_without_outcome = mutation_record("conflict")
        del uncertain_conflict_without_outcome["outcome_evidence"]
        invalid["conflict uncertainty evidence"] = uncertain_conflict_without_outcome

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

        for accepted in (True, False):
            with self.subTest(correlated_conflict=accepted):
                correlated = mutation_record("conflict")
                correlated["protocol_accepted"] = accepted
                del correlated["outcome_evidence"]
                self.assertTrue(schema_accepts(schema, "MutationV1", correlated))

                contradictory = deepcopy(correlated)
                contradictory["outcome_evidence"] = mutation_record("conflict")[
                    "outcome_evidence"
                ]
                self.assertFalse(schema_accepts(schema, "MutationV1", contradictory))

    def test_correlated_pending_states_require_and_preserve_boolean_reply(
        self,
    ) -> None:
        schema = json.loads(
            (ROOT / repository_policy.ISSUE76_SCHEMA_REL).read_text(encoding="utf-8")
        )
        for state in ("reply_observed", "verify_pending"):
            for accepted in (True, False):
                with self.subTest(state=state, accepted=accepted):
                    self.assertTrue(
                        schema_accepts(
                            schema,
                            "MutationV1",
                            mutation_intermediate_record(state, accepted),
                        )
                    )
            for invalid in (None, 0, "false"):
                with self.subTest(state=state, invalid=invalid):
                    record = mutation_intermediate_record(state, True)
                    record["protocol_accepted"] = invalid
                    self.assertFalse(schema_accepts(schema, "MutationV1", record))

    def test_rollback_pending_and_terminal_states_preserve_correlated_reply(
        self,
    ) -> None:
        schema = json.loads(
            (ROOT / repository_policy.ISSUE76_SCHEMA_REL).read_text(encoding="utf-8")
        )
        for state in ("rollback_reply_observed", "rollback_verify_pending"):
            for accepted in (True, False):
                with self.subTest(state=state, accepted=accepted):
                    self.assertTrue(
                        schema_accepts(
                            schema,
                            "MutationV1",
                            rollback_intermediate_record(state, accepted),
                        )
                    )
            for invalid in (None, 0, "false"):
                with self.subTest(state=state, invalid=invalid):
                    record = rollback_intermediate_record(state)
                    record["rollback"]["protocol_accepted"] = invalid
                    self.assertFalse(schema_accepts(schema, "MutationV1", record))

        for accepted in (True, False, None):
            with self.subTest(rolled_back=accepted):
                rolled_back = mutation_record("rolled_back")
                rolled_back["rollback"]["protocol_accepted"] = accepted
                self.assertTrue(schema_accepts(schema, "MutationV1", rolled_back))

    def test_uncertain_send_requested_readback_requires_uncertainty_evidence(self) -> None:
        schema = json.loads(
            (ROOT / repository_policy.ISSUE76_SCHEMA_REL).read_text(encoding="utf-8")
        )
        for state, mode in (("applied", "apply"), ("probe_active", "probe")):
            with self.subTest(state=state):
                recovered = mutation_record("applied")
                recovered["state"] = state
                recovered["mode"] = mode
                recovered["audit"][0]["state"] = state
                if state == "probe_active":
                    recovered["probe_deadline"] = "2026-07-27T00:01:00Z"
                recovered["protocol_accepted"] = None
                recovered["outcome_evidence"] = {
                    "possible_side_effect": True,
                    "blind_retry_forbidden": True,
                    "last_durable_state": "dispatch_intent",
                    "recorded_at": "2026-07-27T00:00:00Z",
                }
                self.assertTrue(schema_accepts(schema, "MutationV1", recovered))

                missing_uncertainty = deepcopy(recovered)
                del missing_uncertainty["outcome_evidence"]
                self.assertFalse(
                    schema_accepts(schema, "MutationV1", missing_uncertainty)
                )

                false_acceptance = deepcopy(recovered)
                false_acceptance["protocol_accepted"] = False
                self.assertFalse(schema_accepts(schema, "MutationV1", false_acceptance))

    def test_rollback_intermediate_states_reject_top_level_terminal_error(self) -> None:
        schema = json.loads(
            (ROOT / repository_policy.ISSUE76_SCHEMA_REL).read_text(encoding="utf-8")
        )
        states = (
            "rollback_intent",
            "rollback_dispatch_intent",
            "rollback_reply_observed",
            "rollback_verify_pending",
        )
        for state in states:
            with self.subTest(state=state):
                valid = rollback_intermediate_record(state)
                self.assertTrue(schema_accepts(schema, "MutationV1", valid))

                contradictory = deepcopy(valid)
                contradictory["error"] = error_payload("rollback_failed")
                self.assertFalse(
                    schema_accepts(schema, "MutationV1", contradictory)
                )

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

    def test_validator_rejects_each_issue_84_envelope_implication_removal(
        self,
    ) -> None:
        for index in range(3):
            with self.subTest(index=index), tempfile.TemporaryDirectory() as tmp:
                repo = copy_repo(Path(tmp))
                path = repo / repository_policy.ISSUE76_SCHEMA_REL
                schema = json.loads(path.read_text(encoding="utf-8"))
                schema["$defs"]["EnvelopeV1"]["allOf"].pop(index)
                path.write_text(json.dumps(schema), encoding="utf-8")

                errors = repository_policy.issue_76_m625_raw_feature_errors(repo)

                self.assertTrue(
                    any(
                        "issue-92 envelope implications are not exact" in error
                        for error in errors
                    ),
                    errors,
                )

    def test_validator_rejects_issue_84_runtime_and_source_contract_weakening(
        self,
    ) -> None:
        mutations = {
            "runtime admission precedence": (
                lambda schema: schema["x-runtime-admission"]["precedence"][
                    0
                ].update({"order": 2}),
                "runtime admission",
            ),
            "operation-stage error binding": (
                lambda schema: schema["x-runtime-admission"][
                    "errorBinding"
                ].update({"postErrorRuntimeLookup": True}),
                "runtime admission",
            ),
            "positive mutation binding": (
                lambda schema: schema["x-runtime-admission"][
                    "positiveBindingRequiredFor"
                ].remove("MutationV1"),
                "runtime admission",
            ),
            "single local source": (
                lambda schema: schema["x-local-protocol-source"].update(
                    {"count": 2}
                ),
                "local protocol source",
            ),
            "source lifecycle order": (
                lambda schema: schema["x-local-protocol-source"].update(
                    {"provisionBefore": "service Setup"}
                ),
                "local protocol source",
            ),
            "source topology isolation": (
                lambda schema: schema["x-local-protocol-source"].update(
                    {"rawRemoteTopology": True}
                ),
                "local protocol source",
            ),
        }
        for name, (mutate, expected) in mutations.items():
            with self.subTest(name=name), tempfile.TemporaryDirectory() as tmp:
                repo = copy_repo(Path(tmp))
                path = repo / repository_policy.ISSUE76_SCHEMA_REL
                schema = json.loads(path.read_text(encoding="utf-8"))
                mutate(schema)
                path.write_text(json.dumps(schema), encoding="utf-8")

                errors = repository_policy.issue_76_m625_raw_feature_errors(repo)

                self.assertTrue(
                    any(f"issue-84 {expected}" in error for error in errors),
                    errors,
                )

    def test_validator_rejects_issue_84_native_feature_type_weakening(self) -> None:
        mutations = {
            "native feature type pattern": lambda schema: schema["$defs"][
                "NativeFeatureTypeV1"
            ].update({"pattern": "^[A-Za-z][A-Za-z0-9]*$"}),
            "locator native feature type": lambda schema: schema["$defs"][
                "FeatureLocatorV1"
            ]["properties"].update(
                {"feature_type": {"type": "string"}}
            ),
            "target native feature type": lambda schema: schema["$defs"][
                "FeatureTargetV1"
            ]["properties"].update(
                {"feature_type": {"type": "string"}}
            ),
        }
        for name, mutate in mutations.items():
            with self.subTest(name=name), tempfile.TemporaryDirectory() as tmp:
                repo = copy_repo(Path(tmp))
                path = repo / repository_policy.ISSUE76_SCHEMA_REL
                schema = json.loads(path.read_text(encoding="utf-8"))
                mutate(schema)
                path.write_text(json.dumps(schema), encoding="utf-8")

                errors = repository_policy.issue_76_m625_raw_feature_errors(repo)

                self.assertTrue(
                    any(
                        all(
                            token in error
                            for token in ("issue-84", "feature", "type")
                        )
                        for error in errors
                    ),
                    errors,
                )

    def test_validator_rejects_issue_92_stage_binding_implication_change(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = copy_repo(Path(tmp))
            path = repo / repository_policy.ISSUE76_SCHEMA_REL
            schema = json.loads(path.read_text(encoding="utf-8"))
            schema["$defs"]["EnvelopeV1"]["allOf"].append(
                {"if": {"properties": {"meta": {"type": "object"}}}}
            )
            path.write_text(json.dumps(schema), encoding="utf-8")

            errors = repository_policy.issue_76_m625_raw_feature_errors(repo)

            self.assertTrue(
                any("issue-92 envelope implications are not exact" in error for error in errors),
                errors,
            )

    def test_validator_rejects_issue_92_code_binding_reintroduction(self) -> None:
        for definition in ("PreBindingErrorCodeV1", "PostBindingErrorCodeV1"):
            with self.subTest(definition=definition), tempfile.TemporaryDirectory() as tmp:
                repo = copy_repo(Path(tmp))
                path = repo / repository_policy.ISSUE76_SCHEMA_REL
                schema = json.loads(path.read_text(encoding="utf-8"))
                schema["$defs"][definition] = {
                    "type": "string",
                    "enum": ["internal"],
                }
                path.write_text(json.dumps(schema), encoding="utf-8")

                errors = repository_policy.issue_76_m625_raw_feature_errors(repo)

                self.assertTrue(
                    any(
                        "issue-92 error binding must not be classified by code"
                        in error
                        for error in errors
                    ),
                    errors,
                )

        with tempfile.TemporaryDirectory() as tmp:
            repo = copy_repo(Path(tmp))
            path = repo / repository_policy.ISSUE76_SCHEMA_REL
            schema = json.loads(path.read_text(encoding="utf-8"))
            schema["$defs"]["ErrorCodeV1"]["enum"].append("unclassified")
            path.write_text(json.dumps(schema), encoding="utf-8")

            errors = repository_policy.issue_76_m625_raw_feature_errors(repo)

            self.assertTrue(
                    any("issue-92 error vocabulary is not exact" in error for error in errors),
                    errors,
                )

    def test_validator_rejects_issue_82_dto_inventory_weakening(self) -> None:
        mutations = [
            ("owner", lambda contract: contract.update({"owner": "gateway"})),
            (
                "duplicate validation",
                lambda contract: contract.update(
                    {"gatewayMustNotReimplement": "allowed"}
                ),
            ),
        ]
        validator_groups = (
            (
                "requestValidators",
                repository_policy.ISSUE82_CANONICAL_DTO_VALIDATORS[:3],
            ),
            (
                "resultValidators",
                repository_policy.ISSUE82_CANONICAL_DTO_VALIDATORS[3:],
            ),
        )
        for group, validators in validator_groups:
            mutations.extend(
                (
                    f"validator {validator}",
                    lambda contract, group=group, index=index: contract[
                        group
                    ].pop(index),
                )
                for index, validator in enumerate(validators)
            )
        mutations.extend(
            (
                f"gateway responsibility {responsibility}",
                lambda contract, index=index: contract[
                    "gatewayResidualResponsibilities"
                ].pop(index),
            )
            for index, responsibility in enumerate(
                repository_policy.ISSUE82_GATEWAY_RESIDUAL_RESPONSIBILITIES
            )
        )
        mutations.extend(
            (
                f"validator signature {validator}",
                lambda contract, validator=validator: contract["signatures"].pop(
                    validator
                ),
            )
            for validator in repository_policy.ISSUE82_CANONICAL_DTO_VALIDATORS
        )
        for name, mutate in mutations:
            with self.subTest(name=name), tempfile.TemporaryDirectory() as tmp:
                repo = copy_repo(Path(tmp))
                path = repo / repository_policy.ISSUE76_SCHEMA_REL
                schema = json.loads(path.read_text(encoding="utf-8"))
                mutate(schema["x-canonical-dto-validation"])
                path.write_text(json.dumps(schema), encoding="utf-8")

                errors = repository_policy.issue_76_m625_raw_feature_errors(repo)

                self.assertTrue(
                    any(
                        "issue-82 canonical DTO validator inventory is not exact"
                        in error
                        for error in errors
                    ),
                    errors,
                )

    def test_validator_rejects_issue_82_prose_removal(self) -> None:
        def remove_section(text: str, start: str, end: str) -> str:
            section_start = text.index(start)
            section_end = text.index(end, section_start)
            return text[:section_start] + text[section_end:]

        mutations = {
            "validator ownership": lambda text: remove_section(
                text,
                "## Canonical DTO Validation Ownership",
                "Owner authorization permits",
            ),
            "runtime binding": lambda text: remove_section(
                text,
                "`EnvelopeMetaV1.runtime` contains",
                "## `features.get`",
            ),
            "malformed no echo": lambda text: remove_section(
                text,
                "The envelope echoes the typed closed request",
                "`ErrorV1` has exactly",
            ),
            "correlated recovery": lambda text: remove_section(
                text,
                "For an original correlated reply",
                "Possible-send recovery with a trustworthy full READ",
            ),
            "rollback recovery": lambda text: remove_section(
                text,
                "`rollback_reply_observed` and `rollback_verify_pending` require",
                "## Mutation Durability And Idempotency",
            ),
            "wal rejection": lambda text: remove_section(
                text,
                "Restore validates every WAL mutation",
                "One global runtime writer lease",
            ),
        }
        for name, mutate in mutations.items():
            with self.subTest(name=name), tempfile.TemporaryDirectory() as tmp:
                repo = copy_repo(Path(tmp))
                path = repo / repository_policy.ISSUE76_API_REL
                path.write_text(
                    mutate(path.read_text(encoding="utf-8")),
                    encoding="utf-8",
                )

                errors = repository_policy.issue_76_m625_raw_feature_errors(repo)

                self.assertTrue(
                    any(
                        "required contract marker is missing" in error
                        for error in errors
                    ),
                    errors,
                )

    def test_validator_rejects_issue_84_local_source_contradictions(self) -> None:
        def inject_projection(text: str, statement: str) -> str:
            return text.replace(
                (
                    "topology, semantic projection, GraphQL, or "
                    "public/redacted evidence. It changes"
                ),
                (
                    "topology, semantic projection, GraphQL, or "
                    f"public/redacted evidence. {statement} It changes"
                ),
                1,
            )

        projection_error = (
            "issue-84 permits local source projection into an excluded surface"
        )
        mutations = {
            "second Generic/client source": (
                lambda text: text.replace(
                    "\n## `features.get`",
                    (
                        "\nA second Generic/client source may be provisioned.\n\n"
                        "## `features.get`"
                    ),
                    1,
                ),
                "issue-84 permits more than one local Generic/client source",
            ),
            "GraphQL projection": (
                lambda text: inject_projection(
                    text,
                    "The local source may enter GraphQL.",
                ),
                projection_error,
            ),
            "semantic projection": (
                lambda text: inject_projection(
                    text,
                    "The local source may enter semantic projection.",
                ),
                projection_error,
            ),
            "public-redacted evidence projection": (
                lambda text: inject_projection(
                    text,
                    "The local source may enter public/redacted evidence.",
                ),
                projection_error,
            ),
            "outside lifecycle window": (
                lambda text: text.replace(
                    "existing CEM. That feature",
                    (
                        "existing CEM. Provisioning may occur before service "
                        "Setup or after network Start. That feature"
                    ),
                    1,
                ),
                (
                    "issue-84 permits provisioning outside "
                    "post-Setup/pre-Start"
                ),
            ),
        }
        for name, (mutate, expected) in mutations.items():
            with self.subTest(name=name), tempfile.TemporaryDirectory() as tmp:
                repo = copy_repo(Path(tmp))
                path = repo / repository_policy.ISSUE76_API_REL
                original = path.read_text(encoding="utf-8")
                mutated = mutate(original)
                self.assertNotEqual(mutated, original)
                path.write_text(mutated, encoding="utf-8")

                errors = repository_policy.issue_76_m625_raw_feature_errors(repo)

                self.assertTrue(any(expected in error for error in errors), errors)

    def test_validator_allows_valid_adjacent_issue_84_prohibitions(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = copy_repo(Path(tmp))
            path = repo / repository_policy.ISSUE76_API_REL
            text = path.read_text(encoding="utf-8")
            text = text.replace(
                "\n## `features.get`",
                (
                    "\nNo second Generic/client source may be provisioned. "
                    "The local source must not enter GraphQL, semantic "
                    "projection, or public/redacted evidence. Provisioning "
                    "must not occur before service Setup or after network "
                    "Start.\n\n## `features.get`"
                ),
                1,
            )
            path.write_text(text, encoding="utf-8")

            self.assertEqual(
                repository_policy.issue_76_m625_raw_feature_errors(repo),
                [],
            )

    def test_validator_rejects_issue_86_read_observation_weakening(self) -> None:
        mutations = {
            "requestDataPresence": "forbidden",
            "callerSuppliedRequestNarrowing": True,
            "correlationBinding": "unbound",
            "functionBinding": "unbound",
            "valueBinding": "unbound",
        }
        for field, replacement in mutations.items():
            with self.subTest(field=field), tempfile.TemporaryDirectory() as tmp:
                repo = copy_repo(Path(tmp))
                path = repo / repository_policy.ISSUE76_SCHEMA_REL
                schema = json.loads(path.read_text(encoding="utf-8"))
                schema["x-read-observation-invariants"][field] = replacement
                path.write_text(json.dumps(schema), encoding="utf-8")

                errors = repository_policy.issue_76_m625_raw_feature_errors(repo)

                self.assertTrue(
                    any(
                        "issue-86 read observation invariants are not exact" in error
                        for error in errors
                    ),
                    errors,
                )

    def test_validator_rejects_issue_86_read_request_schema_widening(self) -> None:
        for field in ("selector", "elements", "filter", "partial"):
            with self.subTest(field=field), tempfile.TemporaryDirectory() as tmp:
                repo = copy_repo(Path(tmp))
                path = repo / repository_policy.ISSUE76_SCHEMA_REL
                schema = json.loads(path.read_text(encoding="utf-8"))
                schema["$defs"]["FeatureDataGetRequestV1"]["properties"][field] = {
                    "type": "boolean"
                }
                path.write_text(json.dumps(schema), encoding="utf-8")

                errors = repository_policy.issue_76_m625_raw_feature_errors(repo)

                self.assertTrue(
                    any(
                        "issue-86 READ request closed property set is not exact"
                        in error
                        for error in errors
                    ),
                    errors,
                )

        mutations = {
            "generic target": lambda schema: schema["$defs"][
                "FeatureDataGetRequestV1"
            ]["properties"]["targets"]["items"].update(
                {"$ref": "#/$defs/FeatureTargetV1"}
            ),
            "WRITE target": lambda schema: schema["$defs"][
                "ReadFeatureTargetV1"
            ]["allOf"][1]["properties"]["operation"].update({"const": "WRITE"}),
        }
        for name, mutate in mutations.items():
            with self.subTest(name=name), tempfile.TemporaryDirectory() as tmp:
                repo = copy_repo(Path(tmp))
                path = repo / repository_policy.ISSUE76_SCHEMA_REL
                schema = json.loads(path.read_text(encoding="utf-8"))
                mutate(schema)
                path.write_text(json.dumps(schema), encoding="utf-8")

                errors = repository_policy.issue_76_m625_raw_feature_errors(repo)

                self.assertTrue(
                    any("issue-86 READ " in error for error in errors),
                    errors,
                )

    def test_validator_rejects_issue_87_boolean_checkpoint_weakening(self) -> None:
        definitions_and_states = {
            "MutationV1": ("reply_observed", "verify_pending"),
            "RollbackV1": (
                "rollback_reply_observed",
                "rollback_verify_pending",
            ),
        }
        for definition, states in definitions_and_states.items():
            for state in states:
                with (
                    self.subTest(definition=definition, state=state),
                    tempfile.TemporaryDirectory() as tmp,
                ):
                    repo = copy_repo(Path(tmp))
                    path = repo / repository_policy.ISSUE76_SCHEMA_REL
                    schema = json.loads(path.read_text(encoding="utf-8"))
                    variant = next(
                        candidate
                        for candidate in schema["$defs"][definition]["oneOf"]
                        if candidate["properties"]["state"].get("const") == state
                    )
                    variant["properties"]["protocol_accepted"] = {"const": True}
                    path.write_text(json.dumps(schema), encoding="utf-8")

                    errors = repository_policy.issue_76_m625_raw_feature_errors(repo)

                    self.assertTrue(
                        any(
                            f"correlated {state} boolean checkpoint is not exact"
                            in error
                            for error in errors
                        ),
                        errors,
                    )

    def test_validator_rejects_each_issue_87_wal_policy_weakening(self) -> None:
        mutations = {
            "record validator": lambda policy: policy.update(
                {"recordValidator": "gateway"}
            ),
            "record validation scope": lambda policy: policy.update(
                {"recordValidation": "selected-records"}
            ),
            "precontract reference": lambda policy: policy.update(
                {"precontractReference": "accepted"}
            ),
            "precontract action": lambda policy: policy.update(
                {"precontractReferenceAction": "migrate"}
            ),
            "semantic invalid action": lambda policy: policy.update(
                {"semanticallyInvalidRecordAction": "skip"}
            ),
            "restore failure": lambda policy: policy.update(
                {"restoreFailureAction": "continue"}
            ),
            "wal rewrite": lambda policy: policy.update(
                {"invalidWalBytes": "rewrite"}
            ),
            "conflict quarantine": lambda policy: policy.update(
                {"validConflictStateAction": "admit-writes"}
            ),
            "legacy stable api": lambda policy: policy["compatibility"].update(
                {"legacyStableApi": True}
            ),
            "alias": lambda policy: policy["compatibility"].update({"aliases": True}),
            "v2": lambda policy: policy["compatibility"].update({"v2": True}),
        }
        for name, mutate in mutations.items():
            with self.subTest(name=name), tempfile.TemporaryDirectory() as tmp:
                repo = copy_repo(Path(tmp))
                path = repo / repository_policy.ISSUE76_SCHEMA_REL
                schema = json.loads(path.read_text(encoding="utf-8"))
                mutate(schema["x-wal-restore-policy"])
                path.write_text(json.dumps(schema), encoding="utf-8")

                errors = repository_policy.issue_76_m625_raw_feature_errors(repo)

                self.assertTrue(
                    any("issue-87 WAL restore policy is not exact" in error for error in errors),
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
            ].remove("no_effect"),
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
            "runtime interface split": lambda schema: schema[
                "x-public-runtime-api"
            ]["Runtime"].update({"methodSet": "expanded"}),
            "authorization split": lambda schema: schema[
                "x-authorization-validators"
            ].pop("ValidateWriteAuthorizationV1"),
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
