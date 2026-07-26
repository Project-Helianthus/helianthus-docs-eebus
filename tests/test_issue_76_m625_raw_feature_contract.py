from __future__ import annotations

import hashlib
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import validate_repository_policy as repository_policy  # noqa: E402


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
