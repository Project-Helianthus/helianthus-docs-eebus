#!/usr/bin/env python3
"""Generate the independent M6.25 synchronized-evidence bundle and replay."""

from __future__ import annotations

import argparse
import copy
import json
import pathlib
import sys
from typing import Any

import assemble_m625_validation_root


SCRIPT_ROOT = pathlib.Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_ROOT.parent
PLATFORM_ROOT = assemble_m625_validation_root.platform_root()
PLATFORM_SCRIPTS = PLATFORM_ROOT / "scripts"
if str(PLATFORM_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(PLATFORM_SCRIPTS))

import validate_synchronized_evidence as synchronized


ASSEMBLED_ROOT = assemble_m625_validation_root.assemble()
HISTORICAL_BUNDLE = (
    PLATFORM_ROOT
    / "docs/platform/fixtures/synchronized-evidence/v1/positive/bundle.json"
)
REGISTRY = (
    ASSEMBLED_ROOT
    / "docs/platform/schemas/synchronized-evidence-source-registry-v1.json"
)
DEFAULT_OUTPUT = (
    REPO_ROOT
    / "docs/platform/fixtures/synchronized-evidence/v1/m625/positive"
)
SOURCE_CONTRACT = "helianthus.eebus.m625.public-redacted-evidence.v1"
OWNER_COMMIT = "a09e3a77" + "153204bc3117e233c71e77ef1859834e"
OWNER_PATH = (
    "api/_candidate/msp-0625/"
    "helianthus.eebus.m625.public-redacted-evidence.v1.schema.json"
)
SCHEMA_SHA256 = (
    "0a2885d01d6703389541e246db59bcd845a332e7ed296abca2d49b4f8de31811"
)
OPERATION_VERSION = "git:" + "1a023881" + "70a1ee6befeed1529956a7104aa94e21"
MARKER_ID = "marker-66666666666666666666666666666666"
REMASK_SCOPE_ID = "remask-88888888888888888888888888888888"
CLOUD_SUBJECT_PSEUDONYM = "Q" * 43
SOURCE_IDS = {
    "ebus-11111111111111111111111111111111":
        "ebus-61111111111111111111111111111111",
    "ebus-22222222222222222222222222222222":
        "ebus-62222222222222222222222222222222",
    "ebus-33333333333333333333333333333333":
        "ebus-63333333333333333333333333333333",
    "eebus-44444444444444444444444444444444":
        "eebus-64444444444444444444444444444444",
    "cloud-55555555555555555555555555555555":
        "cloud-65555555555555555555555555555555",
}
RUNTIME_PSEUDONYMS = {
    "runtime-11111111111111111111111111111111":
        "runtime-66666666666666666666666666666666",
    "runtime-44444444444444444444444444444444":
        "runtime-77777777777777777777777777777777",
    "runtime-55555555555555555555555555555555":
        "runtime-88888888888888888888888888888888",
}
TARGET_PSEUDONYMS = {
    "target-aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa":
        "target-dddddddddddddddddddddddddddddddd",
    "target-bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb":
        "target-eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee",
    "target-cccccccccccccccccccccccccccccccc":
        "target-ffffffffffffffffffffffffffffffff",
}


def load_json(path: pathlib.Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"expected JSON object: {path}")
    return value


def pretty_bytes(value: Any) -> bytes:
    return (
        json.dumps(
            value,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n"
    ).encode("utf-8")


def compact_bytes(value: Any) -> bytes:
    return synchronized.canonical(value) + b"\n"


def source_payload(source_observed_at: str) -> dict[str, Any]:
    service = "K" * 43
    entity = "L" * 43
    feature = "M" * 43
    field = "N" * 43
    observation = "P" * 43
    return {
        "contract": SOURCE_CONTRACT,
        "schema_version": 1,
        "source_observed_at": source_observed_at,
        "services": [service],
        "feature_paths": [
            {
                "service": service,
                "entity": entity,
                "feature": feature,
                "feature_path": [
                    {"kind": "SERVICE", "selector": service},
                    {"kind": "ENTITY", "selector": entity},
                    {"kind": "FEATURE", "selector": feature},
                    {"kind": "FIELD", "selector": field},
                ],
            }
        ],
        "observations": [
            {
                "observation_ref": "obs-" + observation,
                "path_index": 0,
                "feature_type": "Measurement",
                "feature_role": "server",
                "function": "measurementListData",
                "source_observed_at": source_observed_at,
                "terminal_classification": "SUCCESS",
                "value_type": "DECIMAL",
                "value": "21.5",
                "unit": "degC",
                "quality": "OBSERVED",
            }
        ],
    }


def remap_identity(identity: dict[str, Any] | None) -> dict[str, Any] | None:
    if identity is None:
        return None
    remapped = copy.deepcopy(identity)
    remapped["target_pseudonym"] = TARGET_PSEUDONYMS[
        remapped["target_pseudonym"]
    ]
    return remapped


def independentize_bundle(bundle: dict[str, Any]) -> None:
    capture_window = copy.deepcopy(bundle["capture_window"])
    capture_window["action"]["marker_id"] = MARKER_ID
    bundle["capture_window"] = capture_window

    for source in bundle["sources"]:
        source["source_id"] = SOURCE_IDS[source["source_id"]]
        source["capture_window"] = copy.deepcopy(capture_window)
        source["ebus_identity"] = remap_identity(source["ebus_identity"])
        binding = source["source_binding"]
        binding["runtime_pseudonym"] = RUNTIME_PSEUDONYMS[
            binding["runtime_pseudonym"]
        ]
        binding["capture_window"] = copy.deepcopy(capture_window)
        binding["ebus_identity"] = copy.deepcopy(source["ebus_identity"])

    for artifact in bundle["artifacts"]:
        artifact["source_id"] = SOURCE_IDS[artifact["source_id"]]
        artifact["capture_window"] = copy.deepcopy(capture_window)
        artifact["ebus_identity"] = remap_identity(artifact["ebus_identity"])
        binding = artifact["source_binding"]
        binding["runtime_pseudonym"] = RUNTIME_PSEUDONYMS[
            binding["runtime_pseudonym"]
        ]
        binding["capture_window"] = copy.deepcopy(capture_window)
        binding["ebus_identity"] = copy.deepcopy(artifact["ebus_identity"])
        artifact["remasking"]["scope_id"] = REMASK_SCOPE_ID
        if artifact["source_kind"] == "EBUS":
            artifact["normalized_evidence"]["identity"] = copy.deepcopy(
                artifact["ebus_identity"]
            )
        elif artifact["source_kind"] == "CLOUD_APP":
            artifact["normalized_evidence"][
                "subject_pseudonym"
            ] = CLOUD_SUBJECT_PSEUDONYM
            artifact["remasking"]["entries"] = [
                {
                    "path": "/subject_pseudonym",
                    "pseudonym": CLOUD_SUBJECT_PSEUDONYM,
                }
            ]


def replace_eebus_source(bundle: dict[str, Any]) -> None:
    source = next(
        row for row in bundle["sources"] if row["source_kind"] == "EEBUS"
    )
    artifact = next(
        row for row in bundle["artifacts"] if row["source_kind"] == "EEBUS"
    )
    binding = copy.deepcopy(source["source_binding"])
    binding.update(
        {
            "operation_id": "eebus.v1.features.data.get",
            "operation_version": OPERATION_VERSION,
            "snapshot_scope": {
                "mode": "LIVE_READ",
                "selector": "feature-data",
            },
            "source_contract": SOURCE_CONTRACT,
            "source_schema_version": 1,
            "owner_repository": "Project-Helianthus/helianthus-docs-eebus",
            "owner_path": OWNER_PATH,
            "owner_commit": OWNER_COMMIT,
            "schema_sha256": SCHEMA_SHA256,
        }
    )
    binding["request_scope"]["operation_scope"] = "feature-data"

    source["source_contract"] = SOURCE_CONTRACT
    source["source_schema_version"] = 1
    source["source_binding"] = copy.deepcopy(binding)

    payload = source_payload(artifact["source_observed_at"])
    artifact["source_contract"] = SOURCE_CONTRACT
    artifact["source_schema_version"] = 1
    artifact["source_binding"] = copy.deepcopy(binding)
    artifact["normalized_evidence"] = payload
    artifact["item_count"] = len(payload["observations"])
    artifact["byte_count"] = len(synchronized.canonical(payload))
    artifact["remasking"] = {
        "method": "PER_BUNDLE_CSPRNG",
        "scope_id": REMASK_SCOPE_ID,
        "entries": [
            {
                "path": "/feature_paths/0/entity",
                "pseudonym": payload["feature_paths"][0]["entity"],
            },
            {
                "path": "/feature_paths/0/feature",
                "pseudonym": payload["feature_paths"][0]["feature"],
            },
            {
                "path": "/feature_paths/0/feature_path/0/selector",
                "pseudonym": payload["feature_paths"][0]["feature_path"][0][
                    "selector"
                ],
            },
            {
                "path": "/feature_paths/0/feature_path/1/selector",
                "pseudonym": payload["feature_paths"][0]["feature_path"][1][
                    "selector"
                ],
            },
            {
                "path": "/feature_paths/0/feature_path/2/selector",
                "pseudonym": payload["feature_paths"][0]["feature_path"][2][
                    "selector"
                ],
            },
            {
                "path": "/feature_paths/0/feature_path/3/selector",
                "pseudonym": payload["feature_paths"][0]["feature_path"][3][
                    "selector"
                ],
            },
            {
                "path": "/feature_paths/0/service",
                "pseudonym": payload["feature_paths"][0]["service"],
            },
            {
                "path": "/observations/0/observation_ref",
                "pseudonym": payload["observations"][0][
                    "observation_ref"
                ].removeprefix("obs-"),
            },
            {
                "path": "/services/0",
                "pseudonym": payload["services"][0],
            },
        ],
    }


def rehash_artifacts(bundle: dict[str, Any]) -> None:
    artifacts_by_source: dict[str, list[str]] = {
        source["source_id"]: [] for source in bundle["sources"]
    }
    for artifact in bundle["artifacts"]:
        artifact_view = {
            key: value
            for key, value in artifact.items()
            if key not in {"artifact_id", "redacted_hash"}
        }
        artifact_hash = synchronized.digest(
            synchronized.ARTIFACT_DOMAIN, artifact_view
        )
        artifact["artifact_id"] = "seav1:sha256:" + artifact_hash
        artifact["redacted_hash"] = "sha256:" + artifact_hash
        artifacts_by_source[artifact["source_id"]].append(
            artifact["artifact_id"]
        )
    for source in bundle["sources"]:
        source["artifact_ids"] = sorted(artifacts_by_source[source["source_id"]])


def generate() -> tuple[bytes, bytes]:
    bundle = load_json(HISTORICAL_BUNDLE)
    independentize_bundle(bundle)
    replace_eebus_source(bundle)
    rehash_artifacts(bundle)
    bundle["sources"].sort(
        key=lambda row: (
            synchronized.PHASE_RANK[row["phase"]],
            synchronized.KIND_RANK[row["source_kind"]],
            row["source_id"],
        )
    )
    bundle["artifacts"].sort(
        key=lambda row: (
            synchronized.PHASE_RANK[row["phase"]],
            synchronized.KIND_RANK[row["source_kind"]],
            row["source_id"],
            row["artifact_id"],
        )
    )
    bundle_view = {
        key: value
        for key, value in bundle.items()
        if key not in {"bundle_id", "bundle_hash"}
    }
    bundle_hash = synchronized.digest(
        synchronized.BUNDLE_DOMAIN, bundle_view
    )
    bundle["bundle_id"] = "sebv1:sha256:" + bundle_hash
    bundle["bundle_hash"] = "sha256:" + bundle_hash
    bundle_bytes = pretty_bytes(bundle)

    registry = synchronized.load_registry(REGISTRY)
    verified = synchronized.verify(
        copy.deepcopy(bundle), registry, len(bundle_bytes)
    )
    replay = synchronized.replay(verified)
    return bundle_bytes, compact_bytes(replay)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-dir",
        type=pathlib.Path,
        default=DEFAULT_OUTPUT,
    )
    args = parser.parse_args()
    bundle, replay = generate()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "bundle.json").write_bytes(bundle)
    (args.output_dir / "replay-result.json").write_bytes(replay)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
