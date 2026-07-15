#!/usr/bin/env python3
"""Validate the MSP-055 hidden exact-head API candidate.

The default mode is deliberately offline: it validates only the closed record
and the byte-preserved evidence committed with it.  ``--online`` adds current
GitHub state checks and asks ``gh`` to verify the Sigstore bundle.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import subprocess
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any, Callable, Sequence

from validate_api_surface_v1 import validate_document


RECORD_REL = Path("api/_candidate/msp-055/candidate-record.json")
PAGE_REL = Path("api/_candidate/runtime-reference.md")
SOURCE_REPOSITORY = "Project-Helianthus/helianthus-eebusreg"
SOURCE_HEAD = "ad79f0bbe589d95d56cc" + "738203604fec78639d90"
MERGED_SOURCE = "59cbea0593f27caf558b" + "c4cc9b665c52fc50b683"
SOURCE_REF = "refs/heads/issue/24-msp055-lifecycle-facade"
RUN_ID = 29397818751
RUN_ATTEMPT = 1
ARTIFACT_ID = 8335827060
ARTIFACT_NAME = "helianthus-eebusreg-api-surface-v1-29397818751-1"
PREDICATE_TYPE = "https://project-helianthus.github.io/attestations/eebus-api-surface/v1"
SIGNER_WORKFLOW = "Project-Helianthus/helianthus-eebusreg/.github/workflows/ci.yml"
API_SCHEMA_ID = "helianthus.eebus.api-surface.v1"
API_SCHEMA_VERSION = 1
EXPECTED_HASHES = {
    "manifest": "c93492bd275b5e14d3c9e05da701730d6d34a197e0653e6b169d103418bfcc8c",
    "predicate": "5960ac6dc00942ea7a19d2559934b382ac700ae445b492abb8d223a6f14b72e4",
    "bundle": "2419bb9ab2187c19642f80f01d1e776b6b52df8cdf182e41ac9329e916ebdfc9",
    "verification": "a1de3f1ff4163871dcb416348723b104afab4edfe3f0d4e1fe0a3f0fef58cbf0",
}
RECORD_SHA256 = "73c1b2bf1bc7408a5603dad0bd4ca30e77f9aa57b933588e1a398f71e321111c"
EXPECTED_PATHS = {
    "manifest": "api/_candidate/msp-055/helianthus-eebusreg-api-surface-v1.json",
    "predicate": "api/_candidate/msp-055/helianthus-eebusreg-api-surface-v1-predicate.json",
    "bundle": "api/_candidate/msp-055/attestation.json",
    "verification": "api/_candidate/msp-055/verification.json",
}
PAGE_TOKENS = (
    "publication_status: \"retired-candidate\"",
    "hypothesis_status: \"withdrawn\"",
    "candidate_output: \"true\"",
    "stable_navigation: \"false\"",
    "search: \"false\"",
    "sitemap: \"false\"",
    "versioned_bundle: \"false\"",
    "release_bundle: \"false\"",
    "Config",
    "Remote",
    "Runtime",
    "func New(Config) (Runtime, error)",
    "Start(context.Context)",
    "Shutdown()",
    "Snapshot()",
    "PairingState()",
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
    "NewSnapshotV1",
    "ComputeDataHash",
    "ship-go\nv0.6 wildcard listener is rejected",
    "GraphQL, Portal, Home Assistant, MCP,\nsemantics, or writes",
)

CommandRunner = Callable[[Sequence[str]], subprocess.CompletedProcess[str]]


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate key")
        result[key] = value
    return result


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_unique_object)


def _iso8601(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value.endswith("Z"):
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def _value(document: Any, *path: str) -> Any:
    current = document
    for part in path:
        if not isinstance(current, dict):
            return None
        current = current.get(part)
    return current


def _category(errors: set[str], value: str) -> None:
    errors.add(value)


def _record_shape_errors(record: Any, now: datetime) -> set[str]:
    errors: set[str] = set()
    if not isinstance(record, dict):
        return {"offline: record-shape"}
    exact = {
        ("schema",): "helianthus.docs.eebus.msp-055-api-candidate.v1",
        ("state",): "retired",
        ("retirement", "reason"): "promoted-to-active",
        ("retirement", "active_version"): "api/eebusruntime-v1",
        ("retirement", "publication_record"): "api/eebusruntime-v1/publication-record.json",
        ("retirement", "source_commit"): MERGED_SOURCE,
        ("source", "repository"): SOURCE_REPOSITORY,
        ("source", "issue"): 24,
        ("source", "pull_request"): 25,
        ("source", "head"): SOURCE_HEAD,
        ("source", "ref"): SOURCE_REF,
        ("run", "id"): RUN_ID,
        ("run", "attempt"): RUN_ATTEMPT,
        ("run", "event"): "workflow_dispatch",
        ("run", "conclusion"): "success",
        ("run", "created_at"): "2026-07-15T07:34:51Z",
        ("run", "expires_at"): "2026-08-14T07:34:51Z",
        ("artifact", "id"): ARTIFACT_ID,
        ("artifact", "name"): ARTIFACT_NAME,
        ("artifact", "expires_at"): "2026-10-13T07:34:53Z",
        ("attestation", "predicate_type"): PREDICATE_TYPE,
        ("attestation", "signer_workflow"): SIGNER_WORKFLOW,
        ("attestation", "runner_environment"): "github-hosted",
    }
    for path, expected in exact.items():
        if _value(record, *path) != expected:
            _category(errors, "offline: record-identity")
    if record.get("state") != "retired":
        _category(errors, "offline: candidate-state")
    created = _iso8601(_value(record, "run", "created_at"))
    expires = _iso8601(_value(record, "run", "expires_at"))
    artifact_expires = _iso8601(_value(record, "artifact", "expires_at"))
    if created is None or expires is None or artifact_expires is None:
        _category(errors, "offline: expiry-syntax")
    elif expires != created + timedelta(days=30) or artifact_expires < expires:
        _category(errors, "offline: expiry-window")
    if expires is not None and expires <= now:
        _category(errors, "offline: candidate-expired")
    return errors


def _artifact_errors(root: Path, record: dict[str, Any]) -> set[str]:
    errors: set[str] = set()
    artifacts = record.get("artifacts")
    if not isinstance(artifacts, dict):
        return {"offline: artifact-record"}
    for name, expected_path in EXPECTED_PATHS.items():
        entry = artifacts.get(name)
        if not isinstance(entry, dict) or entry.get("path") != expected_path:
            _category(errors, "offline: artifact-path")
            continue
        if entry.get("sha256") != EXPECTED_HASHES[name]:
            _category(errors, "offline: artifact-digest")
        path = root / expected_path
        if not path.is_file() or path.is_symlink():
            _category(errors, "offline: artifact-missing")
            continue
        if hashlib.sha256(path.read_bytes()).hexdigest() != EXPECTED_HASHES[name]:
            _category(errors, "offline: artifact-digest")
    return errors


def _statement_from_bundle(bundle: Any) -> Any:
    payload = _value(bundle, "dsseEnvelope", "payload")
    if not isinstance(payload, str):
        return None
    try:
        return json.loads(base64.b64decode(payload, validate=True), object_pairs_hook=_unique_object)
    except (ValueError, UnicodeDecodeError, json.JSONDecodeError):
        return None


def _attestation_errors(root: Path, record: dict[str, Any]) -> set[str]:
    errors: set[str] = set()
    paths = {name: root / path for name, path in EXPECTED_PATHS.items()}
    try:
        manifest = _read_json(paths["manifest"])
        predicate = _read_json(paths["predicate"])
        bundle = _read_json(paths["bundle"])
        verification = _read_json(paths["verification"])
    except (OSError, ValueError, json.JSONDecodeError):
        return {"offline: attestation-json"}
    if validate_document(paths["manifest"]):
        _category(errors, "offline: manifest-api-v1")
    statement = _statement_from_bundle(bundle)
    verified_statement = _value(verification, "0")
    if isinstance(verification, list) and verification:
        verified_statement = _value(verification[0], "verificationResult", "statement")
    else:
        verified_statement = None
    if not isinstance(statement, dict) or statement.get("predicate") != predicate:
        _category(errors, "offline: predicate-statement")
        return errors
    if statement != verified_statement:
        _category(errors, "offline: verification-statement")
    subject_digest = _value(statement, "subject", "0", "digest", "sha256")
    if isinstance(statement.get("subject"), list) and statement["subject"]:
        subject_digest = _value(statement["subject"][0], "digest", "sha256")
    expected = {
        "predicate_type": statement.get("predicateType"),
        "head": _value(statement, "predicate", "checkout", "head"),
        "source_head": _value(statement, "predicate", "source", "commit"),
        "source_ref": _value(statement, "predicate", "source", "ref"),
        "source_repo": _value(statement, "predicate", "source", "repository"),
        "event": _value(statement, "predicate", "source", "event_name"),
        "run_id": _value(statement, "predicate", "workflow", "run_id"),
        "run_attempt": _value(statement, "predicate", "workflow", "run_attempt"),
        "schema_id": _value(statement, "predicate", "producer", "api_schema_id"),
        "schema_version": _value(statement, "predicate", "producer", "api_schema_version"),
        "subject_digest": subject_digest,
    }
    if expected != {
        "predicate_type": PREDICATE_TYPE,
        "head": SOURCE_HEAD,
        "source_head": SOURCE_HEAD,
        "source_ref": SOURCE_REF,
        "source_repo": SOURCE_REPOSITORY,
        "event": "workflow_dispatch",
        "run_id": str(RUN_ID),
        "run_attempt": str(RUN_ATTEMPT),
        "schema_id": API_SCHEMA_ID,
        "schema_version": API_SCHEMA_VERSION,
        "subject_digest": EXPECTED_HASHES["manifest"],
    }:
        _category(errors, "offline: attestation-identity")
    if _value(manifest, "schema_id") != API_SCHEMA_ID or _value(manifest, "schema_version") != API_SCHEMA_VERSION:
        _category(errors, "offline: manifest-identity")
    certificate = _value(verification[0], "verificationResult", "signature", "certificate") if isinstance(verification, list) and verification else None
    if not isinstance(certificate, dict) or any(
        certificate.get(key) != expected
        for key, expected in {
            "githubWorkflowTrigger": "workflow_dispatch",
            "githubWorkflowSHA": SOURCE_HEAD,
            "githubWorkflowRepository": SOURCE_REPOSITORY,
            "githubWorkflowRef": SOURCE_REF,
            "runnerEnvironment": "github-hosted",
        }.items()
    ):
        _category(errors, "offline: signer-identity")
    return errors


def _page_errors(root: Path) -> set[str]:
    path = root / PAGE_REL
    if not path.is_file() or path.is_symlink():
        return {"offline: hidden-page"}
    text = path.read_text(encoding="utf-8")
    return {"offline: hidden-page-inventory"} if any(token not in text for token in PAGE_TOKENS) else set()


def _default_runner(args: Sequence[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(list(args), capture_output=True, text=True, check=False)


def _online_json(runner: CommandRunner, args: Sequence[str]) -> Any | None:
    completed = runner(args)
    if completed.returncode != 0:
        return None
    try:
        return json.loads(completed.stdout)
    except json.JSONDecodeError:
        return None


def online_errors(root: Path, record: dict[str, Any], runner: CommandRunner = _default_runner) -> set[str]:
    errors: set[str] = set()
    pr = _online_json(runner, ("gh", "pr", "view", "25", "--repo", SOURCE_REPOSITORY, "--json", "headRefOid,state,mergedAt,headRepositoryOwner"))
    owner = _value(pr, "headRepositoryOwner", "login")
    if not isinstance(pr, dict) or owner != "Project-Helianthus" or pr.get("headRefOid") != SOURCE_HEAD:
        _category(errors, "online: source-pr-head")
    if not isinstance(pr, dict) or pr.get("state") != "OPEN" or pr.get("mergedAt") is not None:
        _category(errors, "online: source-pr-state")
    run = _online_json(runner, ("gh", "api", f"repos/{SOURCE_REPOSITORY}/actions/runs/{RUN_ID}"))
    if not isinstance(run, dict) or any(run.get(key) != expected for key, expected in {
        "event": "workflow_dispatch", "conclusion": "success", "head_sha": SOURCE_HEAD, "run_attempt": RUN_ATTEMPT,
    }.items()):
        _category(errors, "online: workflow-run")
    artifacts = _online_json(runner, ("gh", "api", f"repos/{SOURCE_REPOSITORY}/actions/runs/{RUN_ID}/artifacts"))
    found = next((item for item in artifacts.get("artifacts", []) if item.get("id") == ARTIFACT_ID), None) if isinstance(artifacts, dict) else None
    if not isinstance(found, dict):
        _category(errors, "online: artifact-missing")
    elif (
        found.get("expired") is True
        or found.get("name") != ARTIFACT_NAME
        or found.get("expires_at") != _value(record, "artifact", "expires_at")
        or _value(found, "workflow_run", "id") != RUN_ID
        or _value(found, "workflow_run", "head_sha") != SOURCE_HEAD
    ):
        _category(errors, "online: artifact-expired")
    verify = runner(("gh", "attestation", "verify", str(root / EXPECTED_PATHS["manifest"]), "--repo", SOURCE_REPOSITORY, "--bundle", str(root / EXPECTED_PATHS["bundle"]), "--predicate-type", PREDICATE_TYPE, "--source-digest", SOURCE_HEAD, "--source-ref", SOURCE_REF, "--signer-workflow", SIGNER_WORKFLOW, "--deny-self-hosted-runners"))
    if verify.returncode != 0:
        _category(errors, "online: attestation-verification")
    return errors


def validate(root: Path, *, online: bool = False, now: datetime | None = None, runner: CommandRunner = _default_runner) -> list[str]:
    root = root.resolve()
    now = now or datetime.now(UTC)
    record_path = root / RECORD_REL
    try:
        record_bytes = record_path.read_bytes()
        record = json.loads(record_bytes, object_pairs_hook=_unique_object)
    except (OSError, ValueError, json.JSONDecodeError):
        return ["offline: record-json"]
    errors = _record_shape_errors(record, now)
    if hashlib.sha256(record_bytes).hexdigest() != RECORD_SHA256:
        errors.add("offline: record-digest")
    if isinstance(record, dict):
        errors |= _artifact_errors(root, record)
        errors |= _attestation_errors(root, record)
    errors |= _page_errors(root)
    if online and isinstance(record, dict):
        errors |= online_errors(root, record, runner)
    return sorted(errors)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--online", action="store_true")
    args = parser.parse_args()
    errors = validate(args.repo, online=args.online)
    for error in errors:
        print(error, file=sys.stderr)
    if errors:
        return 1
    print("msp-055 API candidate: valid" + (" (online)" if args.online else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
