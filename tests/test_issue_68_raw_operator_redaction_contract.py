from __future__ import annotations

import hashlib
import json
import shutil
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

import sys

sys.path.insert(0, str(ROOT / "scripts"))

import validate_repository_policy as repository_policy  # noqa: E402


def copy_repo(tmp_path: Path) -> Path:
    destination = tmp_path / "repo"
    shutil.copytree(
        ROOT,
        destination,
        ignore=shutil.ignore_patterns(".git", ".pytest_cache", "__pycache__"),
    )
    return destination


class Issue68RawOperatorRedactionContractTests(unittest.TestCase):
    maxDiff = None

    def test_validator_has_the_complete_issue_68_contract_marker_inventory(self) -> None:
        self.assertEqual(
            repository_policy.issue_68_raw_operator_redaction_errors.__doc__,
            "Enforce the forward-only raw-operator/redacted-public correction.",
        )
        self.assertEqual(
            set(repository_policy.ISSUE68_REQUIRED_MARKERS),
            {
                "single namespace",
                "authorized raw default",
                "shareable redacted tier",
                "boundary authorization",
                "device fields",
                "entity fields",
                "feature fields",
                "use-case fields",
                "unknown fields",
                "operational identity metadata",
                "reference binding",
                "cross-tier rejection",
                "secret exclusion",
                "reference exception",
                "candidate ref exclusion",
                "public identity redaction",
            },
        )

    def test_forward_contract_requires_the_operator_raw_and_public_redacted_boundary(self) -> None:
        self.assertEqual(
            repository_policy.issue_68_raw_operator_redaction_errors(ROOT),
            [],
        )

    def test_historical_m2_g16_and_protocol_artifacts_are_byte_locked(self) -> None:
        for relative, expected_sha256 in repository_policy.ISSUE68_M2_LOCKED_ARTIFACTS.items():
            self.assertEqual(
                hashlib.sha256((ROOT / relative).read_bytes()).hexdigest(),
                expected_sha256,
                relative.as_posix(),
            )
        self.assertEqual(
            hashlib.sha256(
                (ROOT / repository_policy.ISSUE68_G16_LOCKED_ARTIFACT).read_bytes()
            ).hexdigest(),
            repository_policy.ISSUE68_G16_LOCKED_SHA256,
        )
        self.assertEqual(
            hashlib.sha256(
                (ROOT / repository_policy.ISSUE68_STABLE_PROTOCOL).read_bytes()
            ).hexdigest(),
            repository_policy.ISSUE68_STABLE_PROTOCOL_SHA256,
        )

    def test_validator_rejects_mutation_of_each_historical_lock(self) -> None:
        locked = {
            **repository_policy.ISSUE68_M2_LOCKED_ARTIFACTS,
            repository_policy.ISSUE68_G16_LOCKED_ARTIFACT: repository_policy.ISSUE68_G16_LOCKED_SHA256,
            repository_policy.ISSUE68_STABLE_PROTOCOL: repository_policy.ISSUE68_STABLE_PROTOCOL_SHA256,
        }
        for relative in locked:
            with self.subTest(relative=relative), tempfile.TemporaryDirectory() as tmp:
                repo = copy_repo(Path(tmp))
                path = repo / relative
                path.write_bytes(path.read_bytes() + b"\nissue-68-lock-probe\n")

                errors = repository_policy.issue_68_raw_operator_redaction_errors(repo)

                self.assertTrue(
                    any(relative.as_posix() in error and "byte-identical" in error for error in errors),
                    errors,
                )

    def test_validator_rejects_candidate_ref_in_stable_public_api(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = copy_repo(Path(tmp))
            stable_reference = repo / "api/eebusruntime-v1/reference.md"
            stable_reference.write_text(
                stable_reference.read_text(encoding="utf-8") + "\ncandidate_ref\n",
                encoding="utf-8",
            )

            errors = repository_policy.issue_68_raw_operator_redaction_errors(repo)

            self.assertIn(
                "api/eebusruntime-v1/reference.md: issue-68 candidate_ref leaked into stable public API",
                errors,
            )

    def test_both_machine_profiles_have_exact_tiers_tools_and_raw_fields(self) -> None:
        redacted = json.loads(
            (ROOT / repository_policy.ISSUE68_REDACTED_SCHEMA_REL).read_text(
                encoding="utf-8"
            )
        )
        raw = json.loads(
            (ROOT / repository_policy.ISSUE68_RAW_SCHEMA_REL).read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(redacted["$defs"]["MaskTierV1"]["const"], "redacted")
        self.assertEqual(redacted["$defs"]["AuthScopeV1"]["const"], "eebus.public.read")
        self.assertEqual(raw["properties"]["mask_tier"]["const"], "raw")
        self.assertEqual(raw["properties"]["auth_scope"]["const"], "eebus.raw.read")
        self.assertEqual(raw["properties"]["transport"]["const"], "owner-only-af-unix")
        self.assertEqual(raw["properties"]["source_type"]["const"], "SnapshotV1")
        self.assertEqual(
            raw["properties"]["redacted_projection_type"]["const"],
            "RedactedSnapshotV1",
        )
        self.assertEqual(raw["properties"]["pairing_api"]["const"], "PairingState")
        self.assertEqual(
            raw["properties"]["operator_socket"]["const"],
            "/data/eebus/operator-mcp.sock",
        )
        self.assertEqual(raw["properties"]["parent_mode"]["const"], "0700")
        self.assertEqual(raw["properties"]["socket_mode"]["const"], "0600")
        self.assertEqual(raw["properties"]["public_http_tier"]["const"], "redacted")
        self.assertEqual(raw["properties"]["tier_selector"]["const"], "none")
        self.assertEqual(
            set(redacted["$defs"]["ToolV1"]["enum"]),
            repository_policy.ISSUE68_TOOL_NAMES,
        )
        self.assertEqual(
            set(raw["$defs"]["ToolV1"]["enum"]),
            repository_policy.ISSUE68_TOOL_NAMES,
        )
        for name, contract in repository_policy.ISSUE68_RAW_TYPE_FIELDS.items():
            definition = raw["$defs"][name]
            self.assertEqual(set(definition["required"]), contract["required"])
            self.assertEqual(
                set(definition["properties"]),
                contract["required"] | contract["optional"],
            )
            self.assertFalse(definition["additionalProperties"])
        opaque = raw["$defs"]["OpaqueObservationV1"]
        self.assertEqual(set(opaque["required"]), {"path", "source", "value"})
        self.assertEqual(set(opaque["properties"]), {"path", "source", "value"})

    def test_disconnected_marker_only_amendment_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = copy_repo(Path(tmp))
            amendment = repo / repository_policy.ISSUE68_AMENDMENT_REL
            amendment.write_text(
                "\n".join(repository_policy.ISSUE68_REQUIRED_MARKERS.values()) + "\n",
                encoding="utf-8",
            )

            errors = repository_policy.issue_68_raw_operator_redaction_errors(repo)
            self.assertTrue(any("disconnected" in error for error in errors), errors)

    def test_validator_rejects_v2_alias_and_legacy_tool_mutations(self) -> None:
        replacements = {
            "v2": "eebus.v2.services.list",
            "alias": "eebus.v1.alias.services.list",
            "legacy": "eebus.legacy.services.list",
        }
        for name, replacement in replacements.items():
            with self.subTest(name=name), tempfile.TemporaryDirectory() as tmp:
                repo = copy_repo(Path(tmp))
                path = repo / repository_policy.ISSUE68_RAW_SCHEMA_REL
                schema = json.loads(path.read_text(encoding="utf-8"))
                schema["$defs"]["ToolV1"]["enum"][0] = replacement
                path.write_text(json.dumps(schema), encoding="utf-8")

                errors = repository_policy.issue_68_raw_operator_redaction_errors(repo)
                self.assertTrue(any("exact v1 set" in error for error in errors), errors)

    def test_validator_rejects_redacted_only_schema_and_missing_boundary(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = copy_repo(Path(tmp))
            (repo / repository_policy.ISSUE68_RAW_SCHEMA_REL).unlink()
            errors = repository_policy.issue_68_raw_operator_redaction_errors(repo)
            self.assertTrue(any("machine profile is missing" in error for error in errors), errors)

        with tempfile.TemporaryDirectory() as tmp:
            repo = copy_repo(Path(tmp))
            path = repo / "api/_candidate/msp-06-eebus-mcp-v1.md"
            path.write_text(
                path.read_text(encoding="utf-8").replace(
                    "`/data/eebus/operator-mcp.sock`",
                    "`/data/eebus/missing.sock`",
                ),
                encoding="utf-8",
            )
            errors = repository_policy.issue_68_raw_operator_redaction_errors(repo)
            self.assertTrue(any("operator socket" in error for error in errors), errors)

    def test_validator_rejects_contradiction_and_selector_controlled_tier(self) -> None:
        for phrase in (
            "All `eebus.v1.*` output is redacted.",
            "Header selects `mask_tier`.",
        ):
            with self.subTest(phrase=phrase), tempfile.TemporaryDirectory() as tmp:
                repo = copy_repo(Path(tmp))
                path = repo / repository_policy.ISSUE68_AMENDMENT_REL
                path.write_text(
                    path.read_text(encoding="utf-8") + "\n" + phrase + "\n",
                    encoding="utf-8",
                )
                errors = repository_policy.issue_68_raw_operator_redaction_errors(repo)
                self.assertTrue(any("contradictory boundary language" in error for error in errors), errors)

        with tempfile.TemporaryDirectory() as tmp:
            repo = copy_repo(Path(tmp))
            path = repo / repository_policy.ISSUE68_RAW_SCHEMA_REL
            schema = json.loads(path.read_text(encoding="utf-8"))
            schema["properties"]["tier_selector"]["const"] = "header"
            path.write_text(json.dumps(schema), encoding="utf-8")
            errors = repository_policy.issue_68_raw_operator_redaction_errors(repo)
            self.assertTrue(any("tier_selector binding is not exact" in error for error in errors), errors)

    def test_validator_rejects_unknown_drop_and_secret_reference_ambiguity(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = copy_repo(Path(tmp))
            path = repo / repository_policy.ISSUE68_RAW_SCHEMA_REL
            schema = json.loads(path.read_text(encoding="utf-8"))
            del schema["$defs"]["OpaqueObservationV1"]["properties"]["value"]
            path.write_text(json.dumps(schema), encoding="utf-8")
            errors = repository_policy.issue_68_raw_operator_redaction_errors(repo)
            self.assertTrue(any("opaque path/source/value" in error for error in errors), errors)

        with tempfile.TemporaryDirectory() as tmp:
            repo = copy_repo(Path(tmp))
            path = repo / repository_policy.ISSUE68_AMENDMENT_REL
            path.write_text(
                path.read_text(encoding="utf-8")
                + "\nTokens are forbidden in every tier.\n",
                encoding="utf-8",
            )
            errors = repository_policy.issue_68_raw_operator_redaction_errors(repo)
            self.assertTrue(any("ambiguously forbids evidence references" in error for error in errors), errors)

    def test_raw_schema_key_exemption_does_not_allow_identifier_values(self) -> None:
        text = (ROOT / repository_policy.ISSUE68_RAW_SCHEMA_REL).read_text(
            encoding="utf-8"
        )
        self.assertFalse(
            any(
                "private identifier" in error
                for error in repository_policy._machine_artifact_errors(
                    text,
                    repository_policy.ISSUE68_RAW_SCHEMA_REL.as_posix(),
                )
            )
        )
        schema = json.loads(text)
        schema["examples"] = [{"ski": "a" * 40}]
        errors = repository_policy._machine_artifact_errors(
            json.dumps(schema),
            repository_policy.ISSUE68_RAW_SCHEMA_REL.as_posix(),
        )
        self.assertTrue(any("private identifier" in error for error in errors), errors)


if __name__ == "__main__":
    unittest.main()
