#!/usr/bin/env python3
"""Validate the closed MSP-055 pre-release API publication."""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Callable, Sequence

import yaml

from validate_api_surface_v1 import validate_document


SOURCE_REPOSITORY = "Project-Helianthus/helianthus-eebusreg"
DOCS_REPOSITORY = "Project-Helianthus/helianthus-docs-eebus"
SOURCE_PULL_REQUEST = 45
SOURCE_COMMIT = "7a5852e009bbdcba47f0a34ba866070a4ab35ef8"
SOURCE_TREE = "b090651c99d5b6817a40" "997b14c1b6a2a37c124e"
SOURCE_REF = "refs/heads/main"
SOURCE_MERGED_AT = "2026-07-18T11:06:48Z"
SOURCE_PR_HEAD = "6af4cdcedb5f7f93d01a53c48c6abc0c19f92edb"
SOURCE_PR_REF = "issue/44-pre-release-api-v1"
WORKFLOW_COMMIT = SOURCE_COMMIT
WORKFLOW_REF = SOURCE_REF
RETIRED_SOURCE_COMMIT = "59cbea0593f27caf558bc4cc9b665c52fc50b683"
RETIRED_SOURCE_TREE = "01c17785fe9aac8d8536545e03e1ec1d4a4dff9d"
CANDIDATE_SOURCE = "ad79f0bbe589d95d56cc" "738203604fec78639d90"
CANDIDATE_REF = "refs/heads/issue/24-msp055-lifecycle-facade"
CANDIDATE_DOCS_MERGE = "df231977989625fae8a9" "2d94b3ca88ef9e52c6f2"
CANDIDATE_DOCS_MERGED_AT = "2026-07-15T09:43:13Z"
RUN_ID = 29642000784
RUN_ATTEMPT = 1
ARTIFACT_ID = 8428896581
ARTIFACT_NAME = "helianthus-eebusreg-api-surface-v1-29642000784-1"
PREDICATE_TYPE = (
    "https://project-helianthus.github.io/attestations/eebus-api-surface/v1"
)
SIGNER_WORKFLOW = (
    "Project-Helianthus/helianthus-eebusreg/.github/workflows/ci.yml"
)
GO_VERSION = "1.24.13"
SCHEMA_ID = "helianthus.docs.eebus.msp-055-api-freeze.v1"
SCHEMA_URN = "urn:helianthus:eebus:msp-055-api-freeze:v1"
SCHEMA_SHA256 = "dc6085b0c3ab3f2182d3609db042663d7f73439c85c2f4f9dc51c33b02c57762"

ACTIVE_ROOT_REL = Path("api/eebusruntime-v1")
REFERENCE_REL = ACTIVE_ROOT_REL / "reference.md"
RECORD_REL = ACTIVE_ROOT_REL / "publication-record.json"
SCHEMA_REL = Path("api/schema/helianthus.docs.eebus.msp-055-api-freeze.v1.schema.json")
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
    "manifest": Path("api/_candidate/msp-055/helianthus-eebusreg-api-surface-v1.json"),
    "predicate": Path(
        "api/_candidate/msp-055/helianthus-eebusreg-api-surface-v1-predicate.json"
    ),
    "attestation": Path("api/_candidate/msp-055/attestation.json"),
    "verification": Path("api/_candidate/msp-055/verification.json"),
}
ACTIVE_HASHES = {
    "manifest": "bbabab51cc0a0e833c645f51767e67a34c0361ba61c45b0065ecfda55ed6c32f",
    "predicate": "e84acd2d7ccc63c3a150e9f53d61480d967bf03f5ac827f7a692f14e9ebe534e",
    "attestation": "9b67ab54ef0b9637abdb9450e2a4b94ee56c040883b0d1ee98899d4a02d9142f",
    "verification": "485c7976f7de52a35c55ad590bc3fdfac97420f72bb7a6d7fc80afd418798c87",
}
CANDIDATE_HASHES = {
    "manifest": "c93492bd275b5e14d3c9e05da701730d6d34a197e0653e6b169d103418bfcc8c",
    "predicate": "5960ac6dc00942ea7a19d2559934b382ac700ae445b492abb8d223a6f14b72e4",
    "attestation": "2419bb9ab2187c19642f80f01d1e776b6b52df8cdf182e41ac9329e916ebdfc9",
    "verification": "a1de3f1ff4163871dcb416348723b104afab4edfe3f0d4e1fe0a3f0fef58cbf0",
}
STABLE_CHANNELS = {
    "search": Path("api/search-index.json"),
    "sitemap": Path("api/sitemap.xml"),
    "versioned_bundle": Path("api/versioned-bundle.txt"),
    "release_bundle": Path("api/release-bundle.txt"),
}
EXPECTED_OFFLINE_POLICY = {
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
EXPECTED_ONLINE_POLICY = {
    "source-merge-commit-tree-and-pr",
    "workflow-run-and-artifact",
    (
        "attestation-repository-bundle-predicate-head-digest-head-ref-"
        "workflow-digest-workflow-ref-signer-workflow-deny-self-hosted-runners"
    ),
}
EXPECTED_INVALIDATIONS = {
    "source-commit-or-tree-differs",
    "source-pr-merge-state-differs",
    "run-id-attempt-ref-or-conclusion-differs",
    "artifact-byte-digest-differs",
    "candidate-evidence-is-not-byte-preserved-or-retired",
    "active-reference-is-missing-from-any-stable-channel",
    "candidate-path-leaks-into-stable-output",
    "marked-example-does-not-compile-at-exact-source",
}

CommandRunner = Callable[..., subprocess.CompletedProcess[str]]


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_unique_object)


def _value(document: Any, *parts: str | int) -> Any:
    current = document
    for part in parts:
        if isinstance(part, int):
            if not isinstance(current, list) or part >= len(current):
                return None
            current = current[part]
        else:
            if not isinstance(current, dict):
                return None
            current = current.get(part)
    return current


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _string_set(value: Any) -> set[str] | None:
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        return None
    return set(value)


def _parse_utc(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value.endswith("Z"):
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(UTC)
    except ValueError:
        return None


def _default_runner(
    args: Sequence[str], **kwargs: Any
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        list(args), capture_output=True, text=True, check=False, **kwargs
    )


def _completed(
    runner: CommandRunner, args: Sequence[str], **kwargs: Any
) -> subprocess.CompletedProcess[str] | None:
    try:
        return runner(tuple(str(part) for part in args), **kwargs)
    except (OSError, subprocess.SubprocessError):
        return None


def _json_result(
    runner: CommandRunner, args: Sequence[str]
) -> Any | None:
    completed = _completed(runner, args)
    if completed is None or completed.returncode != 0:
        return None
    try:
        return json.loads(completed.stdout, object_pairs_hook=_unique_object)
    except (ValueError, json.JSONDecodeError):
        return None


def _record_errors(root: Path, record: Any) -> set[str]:
    errors: set[str] = set()
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
    if not isinstance(record, dict) or set(record) != top_level:
        return {"offline: record-schema"}
    if (
        record.get("schema_id") != SCHEMA_ID
        or type(record.get("schema_version")) is not int
        or record.get("schema_version") != 1
        or record.get("state") != "active"
        or record.get("version") != "eebusruntime-v1"
    ):
        errors.add("offline: record-schema")

    source = record.get("source")
    if not isinstance(source, dict) or set(source) != {
        "repository", "pull_request", "commit", "tree", "ref", "merged_at"
    }:
        errors.add("offline: record-schema")
        source = {}
    if (
        source.get("repository") != SOURCE_REPOSITORY
        or source.get("pull_request") != SOURCE_PULL_REQUEST
    ):
        errors.add("offline: source-identity")
    if source.get("commit") != SOURCE_COMMIT:
        errors.add("offline: source-commit")
    if source.get("tree") != SOURCE_TREE:
        errors.add("offline: source-tree")
    if source.get("ref") != SOURCE_REF:
        errors.add("offline: source-ref")
    if source.get("merged_at") != SOURCE_MERGED_AT:
        errors.add("offline: source-state")

    run = record.get("run")
    expected_run = {
        "id": RUN_ID,
        "attempt": RUN_ATTEMPT,
        "event": "push",
        "conclusion": "success",
        "ref": SOURCE_REF,
        "artifact_id": ARTIFACT_ID,
        "artifact_name": ARTIFACT_NAME,
    }
    if not isinstance(run, dict) or set(run) != set(expected_run):
        errors.add("offline: record-schema")
        run = {}
    if run.get("id") != RUN_ID:
        errors.add("offline: run-id")
    if run.get("attempt") != RUN_ATTEMPT:
        errors.add("offline: run-attempt")
    if run.get("ref") != SOURCE_REF:
        errors.add("offline: source-ref")
    if any(run.get(key) != value for key, value in expected_run.items() if key not in {"id", "attempt", "ref"}):
        errors.add("offline: run-identity")

    candidate = record.get("candidate")
    candidate_keys = {
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
    }
    if not isinstance(candidate, dict) or set(candidate) != candidate_keys:
        errors.add("offline: record-schema")
        candidate = {}
    expected_candidate = {
        "docs_repository": DOCS_REPOSITORY,
        "docs_commit": CANDIDATE_DOCS_MERGE,
        "docs_merged_at": CANDIDATE_DOCS_MERGED_AT,
        "source_commit": CANDIDATE_SOURCE,
        "source_tree": RETIRED_SOURCE_TREE,
        "source_ref": CANDIDATE_REF,
        "record_path": CANDIDATE_RECORD_REL.as_posix(),
        "reference_path": CANDIDATE_REFERENCE_REL.as_posix(),
        "state": "retired",
    }
    if any(candidate.get(key) != value for key, value in expected_candidate.items()):
        errors.add("offline: candidate-retirement")
    attestation = record.get("attestation")
    if attestation != {
        "predicate_type": PREDICATE_TYPE,
        "signer_workflow": SIGNER_WORKFLOW,
        "runner_environment": "github-hosted",
        "workflow_commit": WORKFLOW_COMMIT,
        "workflow_ref": WORKFLOW_REF,
    }:
        errors.add("offline: record-schema")
    publication = record.get("publication")
    if publication != {
        "reference": REFERENCE_REL.as_posix(),
        "landing": "api/README.md",
        "stable_channels": [path.as_posix() for path in STABLE_CHANNELS.values()],
    }:
        errors.add("offline: record-schema")
    policy = record.get("verification_policy")
    if (
        not isinstance(policy, dict)
        or set(policy) != {"offline", "online"}
        or _string_set(policy.get("offline")) != EXPECTED_OFFLINE_POLICY
        or _string_set(policy.get("online")) != EXPECTED_ONLINE_POLICY
        or _string_set(record.get("invalidation_conditions")) != EXPECTED_INVALIDATIONS
    ):
        errors.add("offline: record-schema")

    for container, hashes, paths in (
        (record.get("artifacts"), ACTIVE_HASHES, ACTIVE_PATHS),
        (candidate.get("artifacts"), CANDIDATE_HASHES, CANDIDATE_PATHS),
    ):
        if not isinstance(container, dict) or set(container) != set(hashes):
            errors.add("offline: record-schema")
            continue
        for name, expected_hash in hashes.items():
            if container.get(name) != {
                "path": paths[name].as_posix(),
                "sha256": expected_hash,
            }:
                errors.add("offline: artifact-digest")

    schema_path = root / SCHEMA_REL
    try:
        schema = _read_json(schema_path)
    except (OSError, ValueError, json.JSONDecodeError):
        errors.add("offline: record-schema")
    else:
        schema_properties = schema.get("properties") if isinstance(schema, dict) else None
        schema_required = schema.get("required") if isinstance(schema, dict) else None
        if (
            not isinstance(schema, dict)
            or _sha256(schema_path) != SCHEMA_SHA256
            or set(schema) != {
                "$schema", "$id", "schema_id", "schema_version", "type",
                "additionalProperties", "required", "properties", "$defs",
            }
            or schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema"
            or schema.get("$id") != SCHEMA_URN
            or schema.get("schema_id") != SCHEMA_ID
            or schema.get("schema_version") != 1
            or schema.get("additionalProperties") is not False
            or not isinstance(schema_properties, dict)
            or set(schema_properties) != top_level
            or _string_set(schema_required) != top_level
        ):
            errors.add("offline: record-schema")
    return errors


def _artifact_errors(root: Path, record: dict[str, Any]) -> set[str]:
    errors: set[str] = set()
    for paths, hashes, category in (
        (ACTIVE_PATHS, ACTIVE_HASHES, "offline: artifact-digest"),
        (CANDIDATE_PATHS, CANDIDATE_HASHES, "offline: candidate-evidence"),
    ):
        for name, expected_hash in hashes.items():
            path = root / paths[name]
            if not path.is_file() or path.is_symlink():
                errors.add(category)
                continue
            if _sha256(path) != expected_hash:
                errors.add(category)
                if paths is ACTIVE_PATHS:
                    errors.add("offline: artifact-digest")
    active_root = root / ACTIVE_ROOT_REL
    expected_inventory = set(ACTIVE_PATHS.values())
    actual_inventory = {
        path.relative_to(root)
        for path in active_root.rglob("*")
        if path.is_file() or path.is_symlink()
    } if active_root.is_dir() and not active_root.is_symlink() else set()
    if actual_inventory != expected_inventory:
        errors.add("offline: active-inventory")

    manifest_path = root / ACTIVE_PATHS["manifest"]
    if manifest_path.is_file() and validate_document(manifest_path):
        errors.add("offline: manifest-api-v1")
    return errors


def _statement(bundle: Any) -> Any:
    payload = _value(bundle, "dsseEnvelope", "payload")
    if not isinstance(payload, str):
        return None
    try:
        return json.loads(
            base64.b64decode(payload, validate=True), object_pairs_hook=_unique_object
        )
    except (ValueError, UnicodeDecodeError, json.JSONDecodeError):
        return None


def _provenance_errors(root: Path) -> set[str]:
    try:
        predicate = _read_json(root / ACTIVE_PATHS["predicate"])
        bundle = _read_json(root / ACTIVE_PATHS["attestation"])
        verification = _read_json(root / ACTIVE_PATHS["verification"])
    except (OSError, ValueError, json.JSONDecodeError):
        return {"offline: source-provenance"}
    statement = _statement(bundle)
    verified_statement = _value(verification, 0, "verificationResult", "statement")
    certificate = _value(verification, 0, "verificationResult", "signature", "certificate")
    expected_predicate = {
        "checkout": {"clean": True, "head": SOURCE_COMMIT},
        "producer": {
            "api_schema_id": "helianthus.eebus.api-surface.v1",
            "api_schema_version": 1,
            "command": "GOWORK=off GOTOOLCHAIN=local go run ./internal/apisurface -output <manifest>",
            "go_version": "go" + GO_VERSION,
        },
        "schema_id": "helianthus.eebus.api-surface.provenance.v1",
        "schema_version": 1,
        "source": {
            "commit": SOURCE_COMMIT,
            "event_name": "push",
            "pull_request_number": "",
            "ref": SOURCE_REF,
            "repository": SOURCE_REPOSITORY,
        },
        "subject": {
            "name": "helianthus-eebusreg-api-surface-v1.json",
            "sha256": ACTIVE_HASHES["manifest"],
        },
        "workflow": {
            "name": "CI",
            "run_attempt": str(RUN_ATTEMPT),
            "run_id": str(RUN_ID),
        },
    }
    valid_statement = (
        isinstance(statement, dict)
        and statement.get("predicate") == predicate == expected_predicate
        and statement.get("predicateType") == PREDICATE_TYPE
        and _value(statement, "subject", 0, "digest", "sha256")
        == ACTIVE_HASHES["manifest"]
        and statement == verified_statement
    )
    certificate_expected = {
        "githubWorkflowTrigger": "push",
        "githubWorkflowSHA": WORKFLOW_COMMIT,
        "githubWorkflowRepository": SOURCE_REPOSITORY,
        "githubWorkflowRef": WORKFLOW_REF,
        "sourceRepositoryDigest": WORKFLOW_COMMIT,
        "sourceRepositoryRef": WORKFLOW_REF,
        "runnerEnvironment": "github-hosted",
        "runInvocationURI": (
            f"https://github.com/{SOURCE_REPOSITORY}/actions/runs/"
            f"{RUN_ID}/attempts/{RUN_ATTEMPT}"
        ),
    }
    valid_certificate = isinstance(certificate, dict) and all(
        certificate.get(key) == value for key, value in certificate_expected.items()
    )
    serialized = json.dumps(statement, sort_keys=True) if statement is not None else ""
    if not valid_statement or not valid_certificate or CANDIDATE_SOURCE in serialized:
        return {"offline: source-provenance"}
    return set()


def _candidate_errors(root: Path) -> set[str]:
    errors: set[str] = set()
    try:
        record = _read_json(root / CANDIDATE_RECORD_REL)
    except (OSError, ValueError, json.JSONDecodeError):
        return {"offline: candidate-retirement"}
    if (
        not isinstance(record, dict)
        or record.get("state") != "retired"
        or record.get("retirement") != {
            "reason": "promoted-to-active",
            "active_version": ACTIVE_ROOT_REL.as_posix(),
            "publication_record": RECORD_REL.as_posix(),
            "source_commit": RETIRED_SOURCE_COMMIT,
        }
    ):
        errors.add("offline: candidate-retirement")
    try:
        page = (root / CANDIDATE_REFERENCE_REL).read_text(encoding="utf-8")
    except OSError:
        errors.add("offline: candidate-retirement")
    else:
        tokens = (
            'publication_status: "retired-candidate"',
            'hypothesis_status: "withdrawn"',
            'candidate_output: "true"',
            'stable_navigation: "false"',
            'search: "false"',
            'sitemap: "false"',
            'versioned_bundle: "false"',
            'release_bundle: "false"',
        )
        if any(token not in page for token in tokens):
            errors.add("offline: candidate-retirement")
    return errors


def _channel_errors(root: Path) -> set[str]:
    errors: set[str] = set()
    active = REFERENCE_REL.as_posix()
    try:
        search = _read_json(root / STABLE_CHANNELS["search"])["pages"]
        sitemap = ET.fromstring(
            (root / STABLE_CHANNELS["sitemap"]).read_text(encoding="utf-8")
        )
        sitemap_values = [
            node.text
            for node in sitemap.findall(
                "{http://www.sitemaps.org/schemas/sitemap/0.9}url/"
                "{http://www.sitemaps.org/schemas/sitemap/0.9}loc"
            )
        ]
        versioned = (root / STABLE_CHANNELS["versioned_bundle"]).read_text(
            encoding="utf-8"
        ).splitlines()
        release = (root / STABLE_CHANNELS["release_bundle"]).read_text(
            encoding="utf-8"
        ).splitlines()
        landing = (root / "api/README.md").read_text(encoding="utf-8")
        registry = yaml.safe_load(
            (root / "scripts/publication_channels.yaml").read_text(encoding="utf-8")
        )
    except (OSError, KeyError, TypeError, ValueError, ET.ParseError, yaml.YAMLError):
        return {"offline: stable-channel"}
    channels = (search, sitemap_values, versioned, release)
    if any(
        not isinstance(values, list)
        or values.count(active) != 1
        or any("_candidate/" in str(value) for value in values)
        for values in channels
    ):
        errors.add("offline: stable-channel")
    configured = _value(registry, "channels")
    if not isinstance(configured, dict) or any(
        _value(configured, channel, "members") != values
        for channel, values in zip(STABLE_CHANNELS, channels)
    ):
        errors.add("offline: stable-channel")
    if "](eebusruntime-v1/reference.md)" not in landing or "_candidate/" in landing:
        errors.add("offline: stable-channel")
    return errors


def _source_errors(
    root: Path, source_checkout: Path, runner: CommandRunner
) -> set[str]:
    errors: set[str] = set()
    commands = {
        "commit": ("git", "-C", str(source_checkout), "rev-parse", "HEAD"),
        "tree": ("git", "-C", str(source_checkout), "rev-parse", "HEAD^{tree}"),
        "clean": (
            "git", "-C", str(source_checkout), "status", "--porcelain=v1",
            "--untracked-files=all",
        ),
    }
    results = {name: _completed(runner, command) for name, command in commands.items()}
    if results["commit"] is None or results["commit"].returncode != 0 or results["commit"].stdout.strip() != SOURCE_COMMIT:
        errors.add("offline: source-commit")
    if results["tree"] is None or results["tree"].returncode != 0 or results["tree"].stdout.strip() != SOURCE_TREE:
        errors.add("offline: source-tree")
    if results["clean"] is None or results["clean"].returncode != 0 or results["clean"].stdout.strip():
        errors.add("offline: source-clean")
    go_env = os.environ.copy()
    go_env.update({"GOWORK": "off", "GOTOOLCHAIN": "go" + GO_VERSION})
    with tempfile.TemporaryDirectory(prefix="msp-055-manifest-") as temporary:
        generated = Path(temporary) / "helianthus-eebusreg-api-surface-v1.json"
        result = _completed(
            runner,
            ("go", "run", "./internal/apisurface", "-output", str(generated)),
            cwd=source_checkout,
            env=go_env,
        )
        try:
            generated_bytes = generated.read_bytes()
            active_bytes = (root / ACTIVE_PATHS["manifest"]).read_bytes()
        except OSError:
            generated_bytes = active_bytes = b""
            errors.add("offline: generated-manifest")
        if (
            result is None
            or result.returncode != 0
            or not generated_bytes
            or generated_bytes != active_bytes
        ):
            errors.add("offline: generated-manifest")
    return errors


def _example_errors(
    root: Path, source_checkout: Path, runner: CommandRunner
) -> set[str]:
    errors: set[str] = set()
    try:
        text = (root / REFERENCE_REL).read_text(encoding="utf-8")
    except OSError:
        return {"offline: example-compilation"}
    raw_fences = re.findall(r"(?m)^```go\s*$", text)
    examples = re.findall(
        r"<!-- go-example:compile -->\s*```go\n(.*?)\n```",
        text,
        flags=re.DOTALL,
    )
    if not examples or len(examples) != len(raw_fences):
        return {"offline: example-compilation"}
    go_env = os.environ.copy()
    go_env.update({"GOWORK": "off", "GOTOOLCHAIN": "go" + GO_VERSION})
    version = _completed(runner, ("go", "env", "GOVERSION"), cwd=source_checkout, env=go_env)
    if version is None or version.returncode != 0 or version.stdout.strip() != "go" + GO_VERSION:
        errors.add("offline: go-version")
    for source in examples:
        if (
            re.search(r"(?m)^package [A-Za-z_][A-Za-z0-9_]*$", source) is None
            or '"github.com/Project-Helianthus/helianthus-eebusreg"' not in source
            or "..." in source
        ):
            errors.add("offline: example-compilation")
            continue
        with tempfile.TemporaryDirectory(prefix="msp-055-example-") as temporary:
            example_root = Path(temporary)
            (example_root / "go.mod").write_text(
                "module helianthus.invalid/msp055-example\n\n"
                "go 1.24.0\n\n"
                "require github.com/Project-Helianthus/helianthus-eebusreg v0.0.0\n\n"
                f"replace github.com/Project-Helianthus/helianthus-eebusreg => {source_checkout.resolve()}\n",
                encoding="utf-8",
            )
            (example_root / "main.go").write_text(source + "\n", encoding="utf-8")
            compiled = _completed(
                runner,
                ("go", "test", "-mod=mod", "./..."),
                cwd=example_root,
                env=go_env,
            )
            if compiled is None or compiled.returncode != 0:
                errors.add("offline: example-compilation")
    return errors


def _wiring_errors(root: Path) -> set[str]:
    errors: set[str] = set()
    try:
        workflow = yaml.safe_load(
            (root / ".github/workflows/docs-ci.yml").read_text(encoding="utf-8")
        )
        steps = workflow["jobs"]["docs-checks"]["steps"]
        ci_text = (root / "scripts/ci_local.sh").read_text(encoding="utf-8")
    except (OSError, KeyError, TypeError, yaml.YAMLError):
        return {"offline: ci-wiring"}
    source_steps = [step for step in steps if step.get("name") == "Checkout exact MSP-055 source"]
    docs_steps = [step for step in steps if step.get("name") == "Checkout"]
    go_steps = [step for step in steps if step.get("name") == "Set up exact MSP-055 Go"]
    ci_steps = [step for step in steps if step.get("name") == "Run local docs CI"]
    online_steps = [step for step in steps if step.get("name") == "Verify MSP-055 online provenance"]
    if len(docs_steps) != 1 or docs_steps[0] != {
        "name": "Checkout",
        "uses": (
            "actions/checkout@34e114876b0b11c390a5"
            "6381ad16ebd13914f8d5"
        ),
        "with": {"path": "docs", "persist-credentials": False},
    }:
        errors.add("offline: ci-wiring")
    if len(source_steps) != 1 or source_steps[0] != {
        "name": "Checkout exact MSP-055 source",
        "uses": (
            "actions/checkout@9c091bb21b7c1c1d1991"
            "bb908d89e4e9dddfe3e0"
        ),
        "with": {
            "repository": SOURCE_REPOSITORY,
            "ref": SOURCE_COMMIT,
            "path": "source",
            "persist-credentials": False,
        },
    }:
        errors.add("offline: ci-wiring")
    if len(go_steps) != 1 or go_steps[0] != {
        "name": "Set up exact MSP-055 Go",
        "uses": (
            "actions/setup-go@924ae3a1cded613372ab"
            "5595356fb5720e22ba16"
        ),
        "with": {"go-version": GO_VERSION, "check-latest": False, "cache": False},
    }:
        errors.add("offline: ci-wiring")
    if (
        len(ci_steps) != 1
        or ci_steps[0].get("working-directory") != "docs"
        or ci_steps[0].get("run") != "./scripts/ci_local.sh"
        or _value(ci_steps[0], "env", "MSP055_SOURCE_CHECKOUT")
        != "${{ github.workspace }}/source"
    ):
        errors.add("offline: ci-wiring")
    if len(online_steps) != 1 or online_steps[0] != {
        "name": "Verify MSP-055 online provenance",
        "working-directory": "docs",
        "run": (
            "python3 scripts/validate_msp_055_api_freeze.py "
            '--source-checkout "$MSP055_SOURCE_CHECKOUT" --online'
        ),
        "env": {
            "GH_TOKEN": "${{ github.token }}",
            "MSP055_SOURCE_CHECKOUT": "${{ github.workspace }}/source",
        },
    }:
        errors.add("offline: ci-wiring")
    if (
        "MSP055_SOURCE_CHECKOUT" not in ci_text
        or re.search(
            r"python3 scripts/validate_msp_055_api_freeze\.py[^\n]*--source-checkout",
            ci_text,
        ) is None
        or re.search(r"(?m)^python3 scripts/validate_msp_055_api_candidate\.py\s*$", ci_text)
    ):
        errors.add("offline: ci-wiring")
    return errors


def _online_errors(root: Path, runner: CommandRunner) -> set[str]:
    errors: set[str] = set()
    docs_pr = _json_result(
        runner,
        (
            "gh", "pr", "view", "19", "--repo", DOCS_REPOSITORY,
            "--json", "state,mergedAt,mergeCommit,headRepositoryOwner",
        ),
    )
    source_pr = _json_result(
        runner,
        (
            "gh", "pr", "view", str(SOURCE_PULL_REQUEST), "--repo", SOURCE_REPOSITORY,
            "--json", "state,mergedAt,mergeCommit,headRefName,headRefOid,headRepositoryOwner",
        ),
    )
    if (
        _value(docs_pr, "state") != "MERGED"
        or _value(docs_pr, "mergedAt") != CANDIDATE_DOCS_MERGED_AT
        or _value(docs_pr, "mergeCommit", "oid") != CANDIDATE_DOCS_MERGE
        or _value(docs_pr, "headRepositoryOwner", "login") != "Project-Helianthus"
    ):
        errors.add("online: candidate-merge")
    if (
        _value(source_pr, "state") != "MERGED"
        or _value(source_pr, "mergedAt") != SOURCE_MERGED_AT
        or _value(source_pr, "mergeCommit", "oid") != SOURCE_COMMIT
        or _value(source_pr, "headRefName") != SOURCE_PR_REF
        or _value(source_pr, "headRefOid") != SOURCE_PR_HEAD
        or _value(source_pr, "headRepositoryOwner", "login") != "Project-Helianthus"
    ):
        errors.add("online: source-pr-merge")

    source_commit = _json_result(
        runner, ("gh", "api", f"repos/{SOURCE_REPOSITORY}/commits/{SOURCE_COMMIT}")
    )
    docs_commit = _json_result(
        runner, ("gh", "api", f"repos/{DOCS_REPOSITORY}/commits/{CANDIDATE_DOCS_MERGE}")
    )
    if (
        _value(source_commit, "sha") != SOURCE_COMMIT
        or _value(source_commit, "commit", "tree", "sha") != SOURCE_TREE
    ):
        errors.add("online: source-commit-tree")
    if _value(docs_commit, "sha") != CANDIDATE_DOCS_MERGE:
        errors.add("online: candidate-merge")

    run = _json_result(
        runner, ("gh", "api", f"repos/{SOURCE_REPOSITORY}/actions/runs/{RUN_ID}")
    )
    expected_run = {
        "id": RUN_ID,
        "event": "push",
        "conclusion": "success",
        "head_sha": SOURCE_COMMIT,
        "head_branch": SOURCE_REF.removeprefix("refs/heads/"),
        "run_attempt": RUN_ATTEMPT,
        "path": ".github/workflows/ci.yml",
    }
    if not isinstance(run, dict) or any(run.get(key) != value for key, value in expected_run.items()):
        errors.add("online: workflow-run")
    artifacts = _json_result(
        runner,
        ("gh", "api", f"repos/{SOURCE_REPOSITORY}/actions/runs/{RUN_ID}/artifacts"),
    )
    artifact = _json_result(
        runner,
        ("gh", "api", f"repos/{SOURCE_REPOSITORY}/actions/artifacts/{ARTIFACT_ID}"),
    )
    listed = next(
        (
            value
            for value in _value(artifacts, "artifacts") or []
            if isinstance(value, dict) and value.get("id") == ARTIFACT_ID
        ),
        None,
    )
    for value in (listed, artifact):
        if (
            not isinstance(value, dict)
            or value.get("id") != ARTIFACT_ID
            or value.get("name") != ARTIFACT_NAME
            or value.get("expired") is not False
            or _value(value, "workflow_run", "id") != RUN_ID
            or _value(value, "workflow_run", "head_sha") != SOURCE_COMMIT
            or _value(value, "workflow_run", "head_branch")
            != SOURCE_REF.removeprefix("refs/heads/")
        ):
            errors.add("online: workflow-artifact")
    verified = _completed(
        runner,
        (
            "gh", "attestation", "verify", str(root / ACTIVE_PATHS["manifest"]),
            "--repo", SOURCE_REPOSITORY,
            "--bundle", str(root / ACTIVE_PATHS["attestation"]),
            "--predicate-type", PREDICATE_TYPE,
            "--source-digest", WORKFLOW_COMMIT,
            "--source-ref", WORKFLOW_REF,
            "--signer-workflow", SIGNER_WORKFLOW,
            "--deny-self-hosted-runners",
        ),
    )
    if verified is None or verified.returncode != 0:
        errors.add("online: attestation-verification")
    return errors


def validate(
    root: Path,
    *,
    source_checkout: Path,
    online: bool = False,
    runner: CommandRunner = _default_runner,
) -> list[str]:
    root = root.absolute()
    source_checkout = source_checkout.absolute()
    try:
        record = _read_json(root / RECORD_REL)
    except (OSError, ValueError, json.JSONDecodeError):
        return ["offline: record-schema"]
    errors = _record_errors(root, record)
    errors |= _artifact_errors(root, record)
    errors |= _provenance_errors(root)
    errors |= _candidate_errors(root)
    errors |= _channel_errors(root)
    errors |= _source_errors(root, source_checkout, runner)
    errors |= _example_errors(root, source_checkout, runner)
    errors |= _wiring_errors(root)
    if online:
        errors |= _online_errors(root, runner)
    return sorted(errors)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--source-checkout", type=Path, required=True)
    parser.add_argument("--online", action="store_true")
    args = parser.parse_args()
    errors = validate(
        args.repo,
        source_checkout=args.source_checkout,
        online=args.online,
    )
    for error in errors:
        print(error, file=sys.stderr)
    if errors:
        return 1
    print("msp-055 API freeze: valid" + (" (online)" if args.online else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
