from __future__ import annotations

import base64
import hashlib
import importlib.util
import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path
from types import ModuleType
from typing import Any, Callable, Iterator, Sequence

import yaml


REPO = Path(__file__).resolve().parents[1]
SOURCE_REPOSITORY = "Project-Helianthus/helianthus-eebusreg"
DOCS_REPOSITORY = "Project-Helianthus/helianthus-docs-eebus"
SOURCE_PULL_REQUEST = 45
SOURCE_COMMIT = "7a5852e009bbdcba47f0" "a34ba866070a4ab35ef8"
SOURCE_TREE = "b090651c99d5b6817a40" "997b14c1b6a2a37c124e"
WORKFLOW_COMMIT = SOURCE_COMMIT
WORKFLOW_REF = "refs/heads/main"
RETIRED_SOURCE_COMMIT = "59cbea0593f27caf558bc4cc9b665c52fc50b683"
RETIRED_SOURCE_TREE = "01c17785fe9aac8d8536545e03e1ec1d4a4dff9d"
CANDIDATE_SOURCE = "ad79f0bbe589d95d56cc" "738203604fec78639d90"
CANDIDATE_DOCS_MERGE = "df231977989625fae8a9" "2d94b3ca88ef9e52c6f2"
CANDIDATE_DOCS_MERGED_AT = "2026-07-15T09:43:13Z"
SOURCE_REF = "refs/heads/main"
SOURCE_MERGED_AT = "2026-07-18T11:06:48Z"
SOURCE_PR_HEAD = "6af4cdcedb5f7f93d01a53c48c6abc0c19f92edb"
SOURCE_PR_REF = "issue/44-pre-release-api-v1"
CANDIDATE_REF = "refs/heads/issue/24-msp055-lifecycle-facade"
RUN_ID = 29642000784
RUN_ATTEMPT = 1
ARTIFACT_ID = 8428896581
ARTIFACT_NAME = "helianthus-eebusreg-api-surface-v1-29642000784-1"
PREDICATE_TYPE = (
    "https://project-helianthus.github.io/attestations/"
    "eebus-api-surface/v1"
)
SIGNER_WORKFLOW = (
    "Project-Helianthus/helianthus-eebusreg/.github/workflows/ci.yml"
)
GO_VERSION = "1.24.13"

ACTIVE_ROOT_REL = Path("api/eebusruntime-v1")
REFERENCE_REL = ACTIVE_ROOT_REL / "reference.md"
RECORD_REL = ACTIVE_ROOT_REL / "publication-record.json"
SCHEMA_REL = Path(
    "api/schema/helianthus.docs.eebus.msp-055-api-freeze.v1.schema.json"
)
VALIDATOR_REL = Path("scripts/validate_msp_055_api_freeze.py")
VALIDATOR = REPO / VALIDATOR_REL
CANDIDATE_RECORD_REL = Path("api/_candidate/msp-055/candidate-record.json")
CANDIDATE_REFERENCE_REL = Path("api/_candidate/runtime-reference.md")

ACTIVE_PATHS = {
    "reference": REFERENCE_REL,
    "manifest": ACTIVE_ROOT_REL / "manifest.json",
    "predicate": ACTIVE_ROOT_REL / "predicate.json",
    "attestation": ACTIVE_ROOT_REL / "attestation.json",
    "verification": ACTIVE_ROOT_REL / "verification.json",
    "publication_record": RECORD_REL,
}
CANDIDATE_PATHS = {
    "manifest": Path(
        "api/_candidate/msp-055/helianthus-eebusreg-api-surface-v1.json"
    ),
    "predicate": Path(
        "api/_candidate/msp-055/helianthus-eebusreg-api-surface-v1-predicate.json"
    ),
    "attestation": Path("api/_candidate/msp-055/attestation.json"),
    "verification": Path("api/_candidate/msp-055/verification.json"),
}
ACTIVE_HASHES = {
    "manifest": "bbabab51cc0a0e833c645f51767e67a3" "4c0361ba61c45b0065ecfda55ed6c32f",
    "predicate": "e84acd2d7ccc63c3a150e9f53d61480d" "967bf03f5ac827f7a692f14e9ebe534e",
    "attestation": "9b67ab54ef0b9637abdb9450e2a4b94e" "e56c040883b0d1ee98899d4a02d9142f",
    "verification": "485c7976f7de52a35c55ad590bc3fdfac" "97420f72bb7a6d7fc80afd418798c87",
}
CANDIDATE_HASHES = {
    "manifest": "c93492bd275b5e14d3c9e05da701730d" "6d34a197e0653e6b169d103418bfcc8c",
    "predicate": "5960ac6dc00942ea7a19d2559934b382" "ac700ae445b492abb8d223a6f14b72e4",
    "attestation": "2419bb9ab2187c19642f80f01d1e776b" "6b52df8cdf182e41ac9329e916ebdfc9",
    "verification": "a1de3f1ff4163871dcb416348723b104" "afab4edfe3f0d4e1fe0a3f0fef58cbf0",
}
SCHEMA_ID = "helianthus.docs.eebus.msp-055-api-freeze.v1"
SCHEMA_URN = "urn:helianthus:eebus:msp-055-api-freeze:v1"
SCHEMA_SHA256 = "dc6085b0c3ab3f2182d3609db042663d7f73439c85c2f4f9dc51c33b02c57762"
STABLE_CHANNELS = {
    "search": Path("api/search-index.json"),
    "sitemap": Path("api/sitemap.xml"),
    "versioned_bundle": Path("api/versioned-bundle.txt"),
    "release_bundle": Path("api/release-bundle.txt"),
}
OFFLINE_POLICY = {
    "closed-record-schema",
    "exact-artifact-byte-hashes",
    "candidate-byte-preservation-and-retirement",
    "green-source-merge-tree-ref-run-attempt",
    "manifest-regenerated-from-exact-source-head",
    "predicate-statement-verification-consistency",
    "stable-channel-membership-and-candidate-exclusion",
    "marked-go-examples-compile-at-exact-source",
    "workflow-and-local-ci-wiring",
    "online-provenance-required-in-ci",
}
ONLINE_POLICY = {
    "source-merge-commit-tree-and-pr",
    "workflow-run-and-artifact",
    (
        "attestation-repository-bundle-predicate-head-digest-head-ref-"
        "workflow-digest-workflow-ref-signer-workflow-deny-self-hosted-runners"
    ),
}
INVALIDATION_CONDITIONS = {
    "source-commit-or-tree-differs",
    "source-pr-merge-state-differs",
    "run-id-attempt-ref-or-conclusion-differs",
    "artifact-byte-digest-differs",
    "candidate-evidence-is-not-byte-preserved-or-retired",
    "active-reference-is-missing-from-any-stable-channel",
    "candidate-path-leaks-into-stable-output",
    "marked-example-does-not-compile-at-exact-source",
}


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_unique_object)


def write_json(path: Path, value: Any) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":"))
        + "\n",
        encoding="utf-8",
    )


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_utc(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(UTC)


def decode_statement(bundle: Any) -> Any:
    payload = bundle["dsseEnvelope"]["payload"]
    return json.loads(base64.b64decode(payload, validate=True), object_pairs_hook=_unique_object)


def require_file(test: unittest.TestCase, root: Path, relative: Path) -> Path:
    path = root / relative
    test.assertTrue(
        path.is_file() and not path.is_symlink(),
        f"missing regular contract file: {relative.as_posix()}",
    )
    return path


_validator_module: ModuleType | None = None


def load_validator() -> ModuleType:
    global _validator_module
    if _validator_module is not None:
        return _validator_module
    if not VALIDATOR.is_file():
        raise AssertionError(f"missing implementation module: {VALIDATOR_REL.as_posix()}")
    name = "_msp_055_api_freeze_validator_for_tests"
    spec = importlib.util.spec_from_file_location(name, VALIDATOR)
    if spec is None or spec.loader is None:
        raise AssertionError(f"cannot load implementation module: {VALIDATOR_REL.as_posix()}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    scripts = str(REPO / "scripts")
    sys.path.insert(0, scripts)
    try:
        spec.loader.exec_module(module)
    finally:
        sys.path.remove(scripts)
    _validator_module = module
    return module


class MSP055APIFreezeStaticContractTests(unittest.TestCase):
    def test_active_version_has_exact_immutable_file_inventory(self) -> None:
        root = REPO / ACTIVE_ROOT_REL
        self.assertTrue(
            root.is_dir() and not root.is_symlink(),
            f"missing active API version directory: {ACTIVE_ROOT_REL.as_posix()}",
        )
        actual = {
            path.relative_to(REPO)
            for path in root.rglob("*")
            if path.is_file() or path.is_symlink()
        }
        self.assertEqual(
            actual,
            set(ACTIVE_PATHS.values()),
            "active API version must contain only reference, evidence, and publication record",
        )

    def test_publication_record_is_closed_and_exact(self) -> None:
        record = read_json(require_file(self, REPO, RECORD_REL))
        self.assertEqual(
            set(record),
            {
                "schema_id",
                "schema_version",
                "state",
                "version",
                "source",
                "candidate",
                "run",
                "attestation",
                "artifacts",
                "publication",
                "verification_policy",
                "invalidation_conditions",
            },
        )
        self.assertEqual(record["schema_id"], SCHEMA_ID)
        self.assertIs(type(record["schema_version"]), int)
        self.assertEqual(record["schema_version"], 1)
        self.assertEqual(record["state"], "active")
        self.assertEqual(record["version"], "eebusruntime-v1")

        self.assertEqual(
            record["source"],
            {
                "repository": SOURCE_REPOSITORY,
                "pull_request": SOURCE_PULL_REQUEST,
                "commit": SOURCE_COMMIT,
                "tree": SOURCE_TREE,
                "ref": SOURCE_REF,
                "merged_at": SOURCE_MERGED_AT,
            },
        )
        self.assertEqual(
            set(record["candidate"]),
            {
                "docs_repository",
                "docs_commit",
                "docs_merged_at",
                "source_commit",
                "source_tree",
                "source_ref",
                "record_path",
                "reference_path",
                "state",
                "artifacts",
            },
        )
        candidate = record["candidate"]
        self.assertEqual(candidate["docs_repository"], DOCS_REPOSITORY)
        self.assertEqual(candidate["docs_commit"], CANDIDATE_DOCS_MERGE)
        self.assertEqual(candidate["docs_merged_at"], CANDIDATE_DOCS_MERGED_AT)
        self.assertEqual(candidate["source_commit"], CANDIDATE_SOURCE)
        self.assertEqual(candidate["source_tree"], RETIRED_SOURCE_TREE)
        self.assertEqual(candidate["source_ref"], CANDIDATE_REF)
        self.assertEqual(candidate["record_path"], CANDIDATE_RECORD_REL.as_posix())
        self.assertEqual(candidate["reference_path"], CANDIDATE_REFERENCE_REL.as_posix())
        self.assertEqual(candidate["state"], "retired")

        self.assertEqual(
            record["run"],
            {
                "id": RUN_ID,
                "attempt": RUN_ATTEMPT,
                "event": "push",
                "conclusion": "success",
                "ref": SOURCE_REF,
                "artifact_id": ARTIFACT_ID,
                "artifact_name": ARTIFACT_NAME,
            },
        )
        self.assertEqual(
            record["attestation"],
            {
                "predicate_type": PREDICATE_TYPE,
                "signer_workflow": SIGNER_WORKFLOW,
                "runner_environment": "github-hosted",
                "workflow_commit": WORKFLOW_COMMIT,
                "workflow_ref": WORKFLOW_REF,
            },
        )
        expected_publication = {
            "reference": REFERENCE_REL.as_posix(),
            "landing": "api/README.md",
            "stable_channels": [path.as_posix() for path in STABLE_CHANNELS.values()],
        }
        self.assertEqual(record["publication"], expected_publication)
        self.assertEqual(set(record["verification_policy"]), {"offline", "online"})
        self.assertEqual(set(record["verification_policy"]["offline"]), OFFLINE_POLICY)
        self.assertEqual(set(record["verification_policy"]["online"]), ONLINE_POLICY)
        self.assertEqual(set(record["invalidation_conditions"]), INVALIDATION_CONDITIONS)

        for name, expected_hash in ACTIVE_HASHES.items():
            self.assertEqual(
                record["artifacts"][name],
                {
                    "path": ACTIVE_PATHS[name].as_posix(),
                    "sha256": expected_hash,
                },
            )
        for name, expected_hash in CANDIDATE_HASHES.items():
            self.assertEqual(
                candidate["artifacts"][name],
                {
                    "path": CANDIDATE_PATHS[name].as_posix(),
                    "sha256": expected_hash,
                },
            )
    def test_publication_record_schema_closes_every_object(self) -> None:
        schema_path = require_file(self, REPO, SCHEMA_REL)
        self.assertEqual(sha256(schema_path), SCHEMA_SHA256)
        schema = read_json(schema_path)
        self.assertEqual(
            set(schema),
            {
                "$schema", "$id", "schema_id", "schema_version", "type",
                "additionalProperties", "required", "properties", "$defs",
            },
        )
        self.assertEqual(schema["$schema"], "https://json-schema.org/draft/2020-12/schema")
        self.assertEqual(schema["$id"], SCHEMA_URN)
        self.assertEqual(schema["schema_id"], SCHEMA_ID)
        self.assertIs(type(schema["schema_version"]), int)
        self.assertEqual(schema["schema_version"], 1)
        top_level = {
            "schema_id",
            "schema_version",
            "state",
            "version",
            "source",
            "candidate",
            "run",
            "attestation",
            "artifacts",
            "publication",
            "verification_policy",
            "invalidation_conditions",
        }
        self.assertEqual(set(schema["properties"]), top_level)
        self.assertEqual(set(schema["required"]), top_level)

        open_objects: list[str] = []

        def visit(value: Any, path: str) -> None:
            if isinstance(value, dict):
                if value.get("type") == "object" and value.get("additionalProperties") is not False:
                    open_objects.append(path)
                for key, child in value.items():
                    visit(child, f"{path}/{key}")
            elif isinstance(value, list):
                for index, child in enumerate(value):
                    visit(child, f"{path}/{index}")

        visit(schema, "#")
        self.assertEqual(open_objects, [], f"publication schema has open objects: {open_objects}")

    def test_pre_release_artifacts_have_exact_bytes(self) -> None:
        missing = [
            ACTIVE_PATHS[name].as_posix()
            for name in ACTIVE_HASHES
            if not (REPO / ACTIVE_PATHS[name]).is_file()
        ]
        self.assertEqual(missing, [], f"missing merged evidence artifacts: {missing}")
        for name, expected in ACTIVE_HASHES.items():
            with self.subTest(name=name):
                self.assertEqual(sha256(REPO / ACTIVE_PATHS[name]), expected)

    def test_predicate_and_certificate_bind_head_and_workflow_identities(self) -> None:
        predicate = read_json(require_file(self, REPO, ACTIVE_PATHS["predicate"]))
        bundle = read_json(require_file(self, REPO, ACTIVE_PATHS["attestation"]))
        verification = read_json(require_file(self, REPO, ACTIVE_PATHS["verification"]))
        statement = decode_statement(bundle)
        self.assertEqual(statement["predicate"], predicate)
        self.assertEqual(statement["predicateType"], PREDICATE_TYPE)
        self.assertEqual(statement["subject"][0]["digest"]["sha256"], ACTIVE_HASHES["manifest"])
        self.assertEqual(predicate["checkout"], {"clean": True, "head": SOURCE_COMMIT})
        self.assertEqual(
            predicate["source"],
            {
                "repository": SOURCE_REPOSITORY,
                "commit": SOURCE_COMMIT,
                "ref": SOURCE_REF,
                "event_name": "push",
                "pull_request_number": "",
            },
        )
        self.assertEqual(predicate["workflow"]["run_id"], str(RUN_ID))
        self.assertEqual(predicate["workflow"]["run_attempt"], str(RUN_ATTEMPT))
        self.assertNotIn(CANDIDATE_SOURCE, json.dumps(statement, sort_keys=True))

        self.assertIsInstance(verification, list)
        self.assertEqual(len(verification), 1)
        result = verification[0]["verificationResult"]
        self.assertEqual(result["statement"], statement)
        certificate = result["signature"]["certificate"]
        self.assertEqual(certificate["githubWorkflowTrigger"], "push")
        self.assertEqual(certificate["githubWorkflowSHA"], WORKFLOW_COMMIT)
        self.assertEqual(certificate["githubWorkflowRepository"], SOURCE_REPOSITORY)
        self.assertEqual(certificate["githubWorkflowRef"], WORKFLOW_REF)
        self.assertEqual(certificate["sourceRepositoryDigest"], WORKFLOW_COMMIT)
        self.assertEqual(certificate["sourceRepositoryRef"], WORKFLOW_REF)
        self.assertEqual(certificate["runnerEnvironment"], "github-hosted")
        self.assertEqual(
            certificate["runInvocationURI"],
            f"https://github.com/{SOURCE_REPOSITORY}/actions/runs/{RUN_ID}/attempts/{RUN_ATTEMPT}",
        )

    def test_candidate_evidence_bytes_are_preserved(self) -> None:
        for name, expected in CANDIDATE_HASHES.items():
            with self.subTest(name=name):
                path = require_file(self, REPO, CANDIDATE_PATHS[name])
                self.assertEqual(sha256(path), expected)

    def test_candidate_record_and_reference_are_explicitly_retired_and_hidden(self) -> None:
        record = read_json(require_file(self, REPO, CANDIDATE_RECORD_REL))
        self.assertEqual(record["state"], "retired")
        self.assertEqual(
            record["retirement"],
            {
                "reason": "promoted-to-active",
                "active_version": ACTIVE_ROOT_REL.as_posix(),
                "publication_record": RECORD_REL.as_posix(),
                "source_commit": RETIRED_SOURCE_COMMIT,
            },
        )
        page = require_file(self, REPO, CANDIDATE_REFERENCE_REL).read_text(encoding="utf-8")
        for token in (
            'publication_status: "retired-candidate"',
            'hypothesis_status: "withdrawn"',
            'candidate_output: "true"',
            'stable_navigation: "false"',
            'search: "false"',
            'sitemap: "false"',
            'versioned_bundle: "false"',
            'release_bundle: "false"',
        ):
            self.assertIn(token, page)

    def test_api_landing_and_all_stable_channels_publish_only_active_reference(self) -> None:
        active = REFERENCE_REL.as_posix()
        landing = require_file(self, REPO, Path("api/README.md")).read_text(encoding="utf-8")
        self.assertRegex(landing, r"\]\(eebusruntime-v1/reference\.md\)")

        search = read_json(require_file(self, REPO, STABLE_CHANNELS["search"]))
        search_members = search["pages"]
        sitemap_root = ET.fromstring(
            require_file(self, REPO, STABLE_CHANNELS["sitemap"]).read_text(encoding="utf-8")
        )
        sitemap_members = [
            element.text
            for element in sitemap_root.findall("{http://www.sitemaps.org/schemas/sitemap/0.9}url/{http://www.sitemaps.org/schemas/sitemap/0.9}loc")
        ]
        versioned_members = require_file(
            self, REPO, STABLE_CHANNELS["versioned_bundle"]
        ).read_text(encoding="utf-8").splitlines()
        release_members = require_file(
            self, REPO, STABLE_CHANNELS["release_bundle"]
        ).read_text(encoding="utf-8").splitlines()
        members = {
            "search": search_members,
            "sitemap": sitemap_members,
            "versioned_bundle": versioned_members,
            "release_bundle": release_members,
        }
        for channel, values in members.items():
            with self.subTest(channel=channel):
                self.assertEqual(values.count(active), 1, f"{channel} must contain active reference once")
                self.assertFalse(
                    any("_candidate/" in str(value) for value in values),
                    f"candidate path leaked into {channel}",
                )
        self.assertNotIn("_candidate/", landing)

    def test_active_reference_binds_exact_source_and_complete_public_inventory(self) -> None:
        text = require_file(self, REPO, REFERENCE_REL).read_text(encoding="utf-8")
        for token in (
            'publication_status: "active"',
            'api_version: "eebusruntime-v1"',
            f'source_commit: "{SOURCE_COMMIT}"',
            f'source_tree: "{SOURCE_TREE}"',
            "Config",
            "ListenAddress netip.AddrPort",
            "DiscoveryEnabled bool",
            "PairingPolicy PairingPolicy",
            "PairingPolicyClosed",
            "Remote",
            "Runtime",
            "func New(Config) (Runtime, error)",
            "Start(context.Context) error",
            "Shutdown() error",
            "Snapshot() (SnapshotV1, error)",
            "PairingState() ([]PairingObservationV1, error)",
            "ErrRuntimeDisabled",
            "ErrRuntimeShutdown",
            "SnapshotV1",
            "SnapshotMetaV1",
            "RuntimeObservationV1",
            "DegradationV1",
            "PairingObservationV1",
            "ServiceV1",
            "SessionV1",
            "TopologyV1",
            "DeviceV1",
            "EntityV1",
            "FeatureV1",
            "UseCaseClaimV1",
            "ObservedRuntimeStateV1",
            "ObservedSessionStateV1",
            "DegradationReasonV1",
            "ServiceKindV1",
            "FeatureRoleV1",
            "NewSnapshotV1",
            "ComputeDataHash",
            "GraphQL",
            "Portal",
            "Home Assistant",
            "MCP",
        ):
            self.assertIn(token, text)
        for stale in ("ConfigV2", "NewV2", "PairingPolicyV2", "PairingPolicyV2Closed"):
            self.assertNotIn(stale, text)

    def test_every_go_example_is_complete_marked_and_compile_owned(self) -> None:
        text = require_file(self, REPO, REFERENCE_REL).read_text(encoding="utf-8")
        raw_fences = re.findall(r"(?m)^```go\s*$", text)
        examples = re.findall(
            r"<!-- go-example:compile -->\s*```go\n(.*?)\n```",
            text,
            flags=re.DOTALL,
        )
        self.assertGreaterEqual(len(examples), 1, "active reference needs a marked compile example")
        self.assertEqual(
            len(raw_fences),
            len(examples),
            "every Go fence must be a complete go-example:compile contract",
        )
        for index, source in enumerate(examples):
            with self.subTest(index=index):
                self.assertRegex(source, r"(?m)^package [A-Za-z_][A-Za-z0-9_]*$")
                self.assertIn(
                    '"github.com/Project-Helianthus/helianthus-eebusreg"',
                    source,
                )
                self.assertNotIn("...", source)

    def workflow_steps(self) -> list[dict[str, Any]]:
        workflow = yaml.safe_load(
            require_file(self, REPO, Path(".github/workflows/docs-ci.yml")).read_text(
                encoding="utf-8"
            )
        )
        return workflow["jobs"]["docs-checks"]["steps"]

    def test_workflow_checks_out_exact_merged_source(self) -> None:
        steps = self.workflow_steps()
        docs_step = next(step for step in steps if step.get("name") == "Checkout")
        self.assertEqual(
            docs_step,
            {
                "name": "Checkout",
                "uses": (
                    "actions/checkout@34e114876b0b11c390a5"
                    "6381ad16ebd13914f8d5"
                ),
                "with": {"path": "docs", "persist-credentials": False},
            },
        )
        source_steps = [
            step for step in steps if step.get("name") == "Checkout exact MSP-055 source"
        ]
        self.assertEqual(
            len(source_steps),
            1,
            "workflow missing exact MSP-055 source checkout step",
        )
        step = source_steps[0]
        self.assertEqual(
            step["uses"],
            "actions/checkout@9c091bb21b7c1c1d1991" "bb908d89e4e9dddfe3e0",
        )
        self.assertEqual(
            step["with"],
            {
                "repository": SOURCE_REPOSITORY,
                "ref": SOURCE_COMMIT,
                "path": "source",
                "persist-credentials": False,
            },
        )

    def test_workflow_pins_go_and_wires_source_checkout_into_local_ci(self) -> None:
        steps = self.workflow_steps()
        go_steps = [step for step in steps if step.get("name") == "Set up exact MSP-055 Go"]
        self.assertEqual(len(go_steps), 1, "workflow missing pinned MSP-055 Go setup")
        self.assertEqual(
            go_steps[0]["uses"],
            "actions/setup-go@924ae3a1cded613372ab" "5595356fb5720e22ba16",
        )
        self.assertEqual(
            go_steps[0]["with"],
            {"go-version": GO_VERSION, "check-latest": False, "cache": False},
        )
        ci_step = next(step for step in steps if step.get("name") == "Run local docs CI")
        self.assertEqual(ci_step["working-directory"], "docs")
        self.assertEqual(ci_step["run"], "./scripts/ci_local.sh")
        self.assertEqual(
            ci_step["env"]["MSP055_SOURCE_CHECKOUT"],
            "${{ github.workspace }}/source",
        )
        self.assertLess(steps.index(go_steps[0]), steps.index(ci_step))

        online_step = next(
            step for step in steps
            if step.get("name") == "Verify MSP-055 online provenance"
        )
        self.assertEqual(online_step["working-directory"], "docs")
        self.assertEqual(
            online_step["run"],
            "python3 scripts/validate_msp_055_api_freeze.py "
            '--source-checkout "$MSP055_SOURCE_CHECKOUT" --online',
        )
        self.assertEqual(
            online_step["env"],
            {
                "GH_TOKEN": "${{ github.token }}",
                "MSP055_SOURCE_CHECKOUT": "${{ github.workspace }}/source",
            },
        )
        self.assertLess(steps.index(ci_step), steps.index(online_step))

    def test_local_ci_invokes_freeze_validator_with_exact_source_checkout(self) -> None:
        text = require_file(self, REPO, Path("scripts/ci_local.sh")).read_text(encoding="utf-8")
        self.assertIn("MSP055_SOURCE_CHECKOUT", text)
        self.assertRegex(
            text,
            r"python3 scripts/validate_msp_055_api_freeze\.py[^\n]*--source-checkout",
        )
        self.assertNotRegex(
            text,
            r"(?m)^python3 scripts/validate_msp_055_api_candidate\.py\s*$",
            "retired candidate validator must not remain the active CI gate",
        )

    def test_freeze_validator_module_exists_without_import_time_dependency(self) -> None:
        self.assertTrue(
            VALIDATOR.is_file() and not VALIDATOR.is_symlink(),
            f"missing freeze validator: {VALIDATOR_REL.as_posix()}",
        )
        module = load_validator()
        self.assertTrue(callable(getattr(module, "validate", None)))
        source = VALIDATOR.read_text(encoding="utf-8")
        self.assertIn("--source-checkout", source)
        self.assertIn("--online", source)


class FakeRunner:
    def __init__(
        self,
        *,
        go_code: int = 0,
        attestation_code: int = 0,
        generated_manifest: bytes | None = None,
    ) -> None:
        self.go_code = go_code
        self.attestation_code = attestation_code
        self.generated_manifest = (
            (REPO / ACTIVE_PATHS["manifest"]).read_bytes()
            if generated_manifest is None
            else generated_manifest
        )
        self.calls: list[tuple[tuple[str, ...], dict[str, Any]]] = []

    def completed(
        self,
        args: tuple[str, ...],
        code: int = 0,
        stdout: str = "",
        stderr: str = "",
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(list(args), code, stdout, stderr)

    def __call__(self, args: Sequence[str], **kwargs: Any) -> subprocess.CompletedProcess[str]:
        command = tuple(str(part) for part in args)
        self.calls.append((command, kwargs))
        if not command:
            raise AssertionError("validator invoked an empty command")
        if command[0] == "git":
            joined = " ".join(command)
            if "rev-parse" in command and "HEAD^{tree}" in command:
                return self.completed(command, stdout=SOURCE_TREE + "\n")
            if "rev-parse" in command and "HEAD" in command:
                return self.completed(command, stdout=SOURCE_COMMIT + "\n")
            if "status" in command or "diff" in command:
                return self.completed(command)
            raise AssertionError(f"unexpected git command: {joined}")
        if command[0] == "go":
            if command[1:] == ("env", "GOVERSION"):
                return self.completed(command, stdout="go" + GO_VERSION + "\n")
            if command[1:3] == ("run", "./internal/apisurface"):
                if self.go_code:
                    return self.completed(
                        command,
                        code=self.go_code,
                        stderr="synthetic manifest generation failure",
                    )
                output = Path(command[command.index("-output") + 1])
                output.write_bytes(self.generated_manifest)
                return self.completed(command)
            return self.completed(
                command,
                code=self.go_code,
                stderr="synthetic example compilation failure" if self.go_code else "",
            )
        if command[:3] == ("gh", "attestation", "verify"):
            return self.completed(
                command,
                code=self.attestation_code,
                stdout="[]\n" if not self.attestation_code else "",
                stderr="synthetic attestation failure" if self.attestation_code else "",
            )
        if command[:2] == ("gh", "pr"):
            number = next(
                (part for part in command if part in {"19", str(SOURCE_PULL_REQUEST)}),
                "",
            )
            payload = (
                {
                    "state": "MERGED",
                    "mergedAt": CANDIDATE_DOCS_MERGED_AT,
                    "mergeCommit": {"oid": CANDIDATE_DOCS_MERGE},
                    "headRepositoryOwner": {"login": "Project-Helianthus"},
                }
                if number == "19"
                else {
                    "state": "MERGED",
                    "mergedAt": SOURCE_MERGED_AT,
                    "mergeCommit": {"oid": SOURCE_COMMIT},
                    "headRefName": SOURCE_PR_REF,
                    "headRefOid": SOURCE_PR_HEAD,
                    "headRepositoryOwner": {"login": "Project-Helianthus"},
                }
            )
            return self.completed(command, stdout=json.dumps(payload))
        if command[:2] == ("gh", "api"):
            endpoint = " ".join(command[2:])
            if f"/commits/{SOURCE_COMMIT}" in endpoint:
                payload = {
                    "sha": SOURCE_COMMIT,
                    "commit": {
                        "tree": {"sha": SOURCE_TREE},
                        "committer": {"date": "2026-07-18T09:08:54Z"},
                    },
                    "verification": None,
                }
            elif f"/commits/{CANDIDATE_DOCS_MERGE}" in endpoint:
                payload = {
                    "sha": CANDIDATE_DOCS_MERGE,
                    "commit": {"committer": {"date": CANDIDATE_DOCS_MERGED_AT}},
                    "verification": None,
                }
            elif f"actions/runs/{RUN_ID}/artifacts" in endpoint:
                payload = {"artifacts": [self.artifact()]}
            elif f"actions/runs/{RUN_ID}" in endpoint:
                payload = {
                    "id": RUN_ID,
                    "event": "push",
                    "conclusion": "success",
                    "head_sha": SOURCE_COMMIT,
                    "head_branch": SOURCE_REF.removeprefix("refs/heads/"),
                    "run_attempt": RUN_ATTEMPT,
                    "path": ".github/workflows/ci.yml",
                }
            elif f"actions/artifacts/{ARTIFACT_ID}" in endpoint:
                payload = self.artifact()
            else:
                raise AssertionError(f"unexpected gh api endpoint: {endpoint}")
            return self.completed(command, stdout=json.dumps(payload))
        raise AssertionError(f"unexpected validator command: {command!r}")

    def artifact(self) -> dict[str, Any]:
        return {
            "id": ARTIFACT_ID,
            "name": ARTIFACT_NAME,
            "expired": False,
            "digest": "sha256:" + "8c4822fcdcbf2c590943e244ec492e8c" "cd8b2bae314deb45f2de88b1ab568d6b",
            "workflow_run": {
                "id": RUN_ID,
                "head_sha": SOURCE_COMMIT,
                "head_branch": SOURCE_REF.removeprefix("refs/heads/"),
            },
        }


@contextmanager
def contract_fixture() -> Iterator[tuple[Path, Path]]:
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary) / "docs"
        root.mkdir()
        for relative in (Path("api"), Path("scripts"), Path(".github")):
            shutil.copytree(REPO / relative, root / relative)
        shutil.copy2(REPO / "requirements-ci.txt", root / "requirements-ci.txt")
        source = Path(temporary) / "source"
        source.mkdir()
        (source / "go.mod").write_text(
            "module github.com/Project-Helianthus/helianthus-eebusreg\n\ngo 1.22.0\n",
            encoding="utf-8",
        )
        yield root, source


Mutation = Callable[[Path], None]


@unittest.skipUnless(VALIDATOR.is_file(), "requires RED-target freeze validator implementation")
class MSP055APIFreezeValidatorTests(unittest.TestCase):
    def validate(
        self,
        root: Path,
        source: Path,
        runner: FakeRunner,
        *,
        online: bool = False,
    ) -> list[str]:
        module = load_validator()
        errors = module.validate(
            root,
            source_checkout=source,
            online=online,
            runner=runner,
        )
        self.assertIsInstance(errors, list)
        self.assertTrue(all(isinstance(error, str) for error in errors))
        return errors

    def mutate_record(self, root: Path, mutate: Callable[[dict[str, Any]], None]) -> None:
        path = root / RECORD_REL
        record = read_json(path)
        mutate(record)
        write_json(path, record)

    def assert_mutation(
        self,
        category: str,
        mutate: Mutation,
        *,
        runner: FakeRunner | None = None,
    ) -> None:
        with contract_fixture() as (root, source):
            mutate(root)
            errors = self.validate(root, source, runner or FakeRunner())
            self.assertIn(category, errors)

    def test_offline_validator_accepts_exact_contract_without_network(self) -> None:
        with contract_fixture() as (root, source):
            runner = FakeRunner()
            self.assertEqual(self.validate(root, source, runner), [])
            commands = [call[0] for call in runner.calls]
            self.assertTrue(any(command[0] == "git" for command in commands))
            self.assertTrue(any(command[0] == "go" for command in commands))
            self.assertFalse(any(command[0] == "gh" for command in commands))

    def test_source_commit_mutation_is_rejected(self) -> None:
        self.assert_mutation(
            "offline: source-commit",
            lambda root: self.mutate_record(
                root, lambda record: record["source"].__setitem__("commit", "0" * 40)
            ),
        )

    def test_source_tree_mutation_is_rejected(self) -> None:
        self.assert_mutation(
            "offline: source-tree",
            lambda root: self.mutate_record(
                root, lambda record: record["source"].__setitem__("tree", "0" * 40)
            ),
        )

    def test_run_id_mutation_is_rejected(self) -> None:
        self.assert_mutation(
            "offline: run-id",
            lambda root: self.mutate_record(
                root, lambda record: record["run"].__setitem__("id", RUN_ID + 1)
            ),
        )

    def test_run_attempt_mutation_is_rejected(self) -> None:
        self.assert_mutation(
            "offline: run-attempt",
            lambda root: self.mutate_record(
                root, lambda record: record["run"].__setitem__("attempt", RUN_ATTEMPT + 1)
            ),
        )

    def test_source_ref_mutation_is_rejected(self) -> None:
        self.assert_mutation(
            "offline: source-ref",
            lambda root: self.mutate_record(
                root, lambda record: record["source"].__setitem__("ref", "refs/heads/other")
            ),
        )

    def test_artifact_digest_mutation_is_rejected(self) -> None:
        def mutate(root: Path) -> None:
            path = root / ACTIVE_PATHS["predicate"]
            path.write_bytes(path.read_bytes() + b"\n")

        self.assert_mutation("offline: artifact-digest", mutate)

    def test_merged_source_state_mutation_is_rejected(self) -> None:
        self.assert_mutation(
            "offline: source-state",
            lambda root: self.mutate_record(
                root,
                lambda record: record["source"].__setitem__(
                    "merged_at", "2026-07-18T11:06:49Z"
                ),
            ),
        )

    def test_candidate_retirement_mutation_is_rejected(self) -> None:
        def mutate(root: Path) -> None:
            path = root / CANDIDATE_RECORD_REL
            record = read_json(path)
            record["state"] = "candidate"
            record.pop("retirement", None)
            write_json(path, record)

        self.assert_mutation("offline: candidate-retirement", mutate)

    def test_candidate_channel_leak_mutation_is_rejected(self) -> None:
        def mutate(root: Path) -> None:
            path = root / STABLE_CHANNELS["search"]
            value = read_json(path)
            value["pages"].append(CANDIDATE_REFERENCE_REL.as_posix())
            write_json(path, value)

        self.assert_mutation("offline: stable-channel", mutate)

    def test_noncompiling_marked_example_mutation_is_rejected(self) -> None:
        def mutate(root: Path) -> None:
            path = root / REFERENCE_REL
            text = path.read_text(encoding="utf-8")
            match = re.search(
                r"(<!-- go-example:compile -->\s*```go\n)(.*?)(\n```)",
                text,
                flags=re.DOTALL,
            )
            self.assertIsNotNone(match, "fixture must contain a marked Go example")
            assert match is not None
            text = text[: match.start(2)] + match.group(2) + "\nthis is not Go" + text[match.end(2) :]
            path.write_text(text, encoding="utf-8")

        self.assert_mutation(
            "offline: example-compilation",
            mutate,
            runner=FakeRunner(go_code=1),
        )

    def test_regenerated_manifest_mismatch_is_rejected(self) -> None:
        with contract_fixture() as (root, source):
            errors = self.validate(
                root,
                source,
                FakeRunner(generated_manifest=b"{}\n"),
            )
            self.assertIn("offline: generated-manifest", errors)

    def test_candidate_attestation_replay_cannot_replace_source_provenance(self) -> None:
        def mutate(root: Path) -> None:
            for name in ("attestation", "verification"):
                destination = root / ACTIVE_PATHS[name]
                destination.write_bytes((root / CANDIDATE_PATHS[name]).read_bytes())
            self.mutate_record(
                root,
                lambda record: (
                    record["artifacts"]["attestation"].__setitem__(
                        "sha256", CANDIDATE_HASHES["attestation"]
                    ),
                    record["artifacts"]["verification"].__setitem__(
                        "sha256", CANDIDATE_HASHES["verification"]
                    ),
                ),
            )

        self.assert_mutation("offline: source-provenance", mutate)

    def test_online_verification_is_optional_and_exact_when_enabled(self) -> None:
        with contract_fixture() as (root, source):
            runner = FakeRunner()
            self.assertEqual(self.validate(root, source, runner, online=True), [])
            commands = [call[0] for call in runner.calls]
            verify = next(
                command
                for command in commands
                if command[:3] == ("gh", "attestation", "verify")
            )
            for flag, value in (
                ("--repo", SOURCE_REPOSITORY),
                ("--predicate-type", PREDICATE_TYPE),
                ("--source-digest", WORKFLOW_COMMIT),
                ("--source-ref", WORKFLOW_REF),
                ("--signer-workflow", SIGNER_WORKFLOW),
            ):
                index = verify.index(flag)
                self.assertEqual(verify[index + 1], value)
            self.assertIn("--deny-self-hosted-runners", verify)
            self.assertIn(str(root / ACTIVE_PATHS["attestation"]), verify)
            self.assertTrue(any(f"actions/runs/{RUN_ID}" in " ".join(command) for command in commands))
            self.assertTrue(any(str(ARTIFACT_ID) in " ".join(command) for command in commands))

    def test_online_attestation_failure_is_terminal(self) -> None:
        with contract_fixture() as (root, source):
            errors = self.validate(
                root,
                source,
                FakeRunner(attestation_code=1),
                online=True,
            )
            self.assertIn("online: attestation-verification", errors)


if __name__ == "__main__":
    unittest.main()
