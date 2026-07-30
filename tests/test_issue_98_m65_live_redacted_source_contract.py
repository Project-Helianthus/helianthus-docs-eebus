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
            schema["properties"]["contract"]["const"],
            "helianthus.eebus.m625.public-redacted-evidence.v1",
        )
        self.assertEqual(schema["properties"]["schema_version"]["const"], 1)
        self.assertEqual(
            schema["properties"]["mask_tier"]["const"],
            "redacted",
        )
        self.assertEqual(
            schema["properties"]["source_kind"]["const"],
            "EEBUS",
        )

    def test_schema_exposes_only_counts_classifications_and_commitments(self) -> None:
        schema = load_json(SCHEMA_REL)
        fixture = load_json(FIXTURE_REL)

        forbidden_fields = (
            "remote_ski",
            "ship_id",
            "device_address",
            "entity_address",
            "feature_address",
            "target",
            "typed_value",
            "raw_request",
            "raw_response",
            "read_token",
            "candidate_ref",
            "private_key",
            "pem",
            "trust_store",
            "credential",
            "token",
        )
        for field in forbidden_fields:
            with self.subTest(field=field):
                mutated = deepcopy(fixture)
                mutated["reads"][0][field] = "forbidden"
                self.assertFalse(schema_accepts(schema, mutated))

    def test_schema_closes_ordering_counts_and_terminal_vocabulary(self) -> None:
        schema = load_json(SCHEMA_REL)
        fixture = load_json(FIXTURE_REL)

        mutated = deepcopy(fixture)
        mutated["reads"].reverse()
        errors = repository_policy.issue_98_m65_live_redacted_source_instance_errors(
            schema,
            mutated,
        )
        self.assertIn("reads must be ordered by read_ref", errors)

        mutated = deepcopy(fixture)
        mutated["summary"]["terminal_counts"].reverse()
        errors = repository_policy.issue_98_m65_live_redacted_source_instance_errors(
            schema,
            mutated,
        )
        self.assertIn(
            "terminal_counts must be ordered by terminal classification",
            errors,
        )

        mutated = deepcopy(fixture)
        mutated["summary"]["attempted_read_count"] = 50
        errors = repository_policy.issue_98_m65_live_redacted_source_instance_errors(
            schema,
            mutated,
        )
        self.assertIn(
            "terminal count sum must equal attempted_read_count",
            errors,
        )

        mutated = deepcopy(fixture)
        mutated["reads"][0]["terminal_classification"] = "INVENTED_SUCCESS"
        self.assertFalse(schema_accepts(schema, mutated))

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
            ),
            PROTOCOL_REL: (
                "direct typed READ",
                "per-capture keyed commitment",
                "no stable identity or SPINE address",
                "no cloud client, credential, refresh, or retry",
            ),
        }
        for relative, markers in required_markers.items():
            text = (ROOT / relative).read_text(encoding="utf-8")
            for marker in markers:
                with self.subTest(relative=relative, marker=marker):
                    self.assertIn(marker, text)

    def test_policy_rejects_schema_or_document_removal(self) -> None:
        for relative in (SCHEMA_REL, API_REL, PROTOCOL_REL):
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


if __name__ == "__main__":
    unittest.main()
