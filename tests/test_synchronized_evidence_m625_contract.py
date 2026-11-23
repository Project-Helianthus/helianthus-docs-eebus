from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import pathlib
import subprocess
import sys
from copy import deepcopy
from decimal import Decimal

import pytest


REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
_SCRIPTS = REPO_ROOT / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

import assemble_m625_validation_root


PLATFORM_ROOT = assemble_m625_validation_root.platform_root()
ASSEMBLED_ROOT = assemble_m625_validation_root.assemble()
SCHEMA_ROOT = ASSEMBLED_ROOT / "docs/platform/schemas"
FIXTURE_ROOT = REPO_ROOT / "docs/platform/fixtures/synchronized-evidence/v1"
HISTORICAL_FIXTURES = (
    PLATFORM_ROOT / "docs/platform/fixtures/synchronized-evidence/v1"
)
HISTORICAL_BUNDLE = HISTORICAL_FIXTURES / "positive/bundle.json"
HISTORICAL_REPLAY = HISTORICAL_FIXTURES / "positive/replay-result.json"
M625_ROOT = FIXTURE_ROOT / "m625/positive"
M625_BUNDLE = M625_ROOT / "bundle.json"
M625_REPLAY = M625_ROOT / "replay-result.json"
REGISTRY = SCHEMA_ROOT / "synchronized-evidence-source-registry-v1.json"
VALIDATOR = PLATFORM_ROOT / "scripts/validate_synchronized_evidence.py"
GENERATOR = REPO_ROOT / "scripts/generate_synchronized_evidence_m625_fixture.py"
CANDIDATE_VALIDATOR = PLATFORM_ROOT / "scripts/validate_candidate_fact_graph.py"
BUNDLE_SCHEMA = SCHEMA_ROOT / "synchronized-evidence-bundle-v1.schema.json"
REPLAY_SCHEMA = SCHEMA_ROOT / "synchronized-evidence-replay-v1.schema.json"
VENDORED_M625_SCHEMA = (
    REPO_ROOT
    / "docs/platform/schemas"
    / "vendor"
    / "helianthus.eebus.m625.public-redacted-evidence.v1.schema.json"
)
CANDIDATE_REGISTRY = SCHEMA_ROOT / "draft-candidate-fact-registry-v1.json"
CANDIDATE_GRAPH = (
    PLATFORM_ROOT
    / "docs/platform/fixtures/candidate-fact-graph/v1/positive/graph.json"
)

HISTORICAL_TUPLE = ("EEBUS", "helianthus-eebus-mcp", 1)
HISTORICAL_OWNER_COMMIT = "9819762a" + "61c28eeceb11beb775aa2a91c83a68b6"
HISTORICAL_SCHEMA_SHA256 = (
    "7f10fa6860e8ccee1af7f155e03d5ac208b5a6fb30518aa3145122a9a1dc0a1c"
)
HISTORICAL_BUNDLE_SHA256 = (
    "e6db2862f9001148deb6f40e286ee5f1eef2907812685a9b48128ddbfca5ce5a"
)
HISTORICAL_REPLAY_SHA256 = (
    "3061c507677f1f41861c20096ff7581ccb6e35c2e01bf66a568e2277df285539"
)
HISTORICAL_REGISTRY_SHA256 = (
    "a91b2106076c3ef0f70578e9fc1c85925dd085af323c5889f809b5b2ef1a2488"
)
HISTORICAL_REGISTRY = (
    SCHEMA_ROOT
    / "history"
    / HISTORICAL_REGISTRY_SHA256
    / "synchronized-evidence-source-registry-v1.json"
)

M625_TUPLE = (
    "EEBUS",
    "helianthus.eebus.m625.public-redacted-evidence.v1",
    1,
)
M625_OWNER_COMMIT = "a09e3a77" + "153204bc3117e233c71e77ef1859834e"
M625_OWNER_PATH = (
    "api/_candidate/msp-0625/"
    "helianthus.eebus.m625.public-redacted-evidence.v1.schema.json"
)
M625_SCHEMA_SHA256 = (
    "0a2885d01d6703389541e246db59bcd845a332e7ed296abca2d49b4f8de31811"
)


def load_json(path: pathlib.Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def registry_entries() -> dict[tuple[str, str, int], dict]:
    return {
        (
            entry["source_kind"],
            entry["source_contract"],
            entry["source_schema_version"],
        ): entry
        for entry in load_json(REGISTRY)["entries"]
    }


def run_validator(
    command: str, bundle: pathlib.Path
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(VALIDATOR),
            command,
            "--bundle",
            str(bundle),
            "--registry",
            str(REGISTRY),
        ],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
        env={**os.environ, "PYTHONHASHSEED": "random"},
    )


def write_mutation(tmp_path: pathlib.Path, mutation) -> pathlib.Path:
    bundle = deepcopy(load_json(M625_BUNDLE))
    mutation(bundle)
    path = tmp_path / "mutated.json"
    path.write_text(
        json.dumps(bundle, ensure_ascii=False, separators=(",", ":"), sort_keys=True),
        encoding="utf-8",
    )
    return path


def write_rehashed_bundle(
    tmp_path: pathlib.Path, bundle: dict, module
) -> pathlib.Path:
    artifacts_by_source: dict[str, list[str]] = {
        source["source_id"]: [] for source in bundle["sources"]
    }
    for artifact in bundle["artifacts"]:
        view = {
            key: value
            for key, value in artifact.items()
            if key not in {"artifact_id", "redacted_hash"}
        }
        digest = module.digest(module.ARTIFACT_DOMAIN, view)
        artifact["artifact_id"] = "seav1:sha256:" + digest
        artifact["redacted_hash"] = "sha256:" + digest
        artifacts_by_source[artifact["source_id"]].append(artifact["artifact_id"])
    for source in bundle["sources"]:
        source["artifact_ids"] = sorted(artifacts_by_source[source["source_id"]])
    bundle_view = {
        key: value
        for key, value in bundle.items()
        if key not in {"bundle_id", "bundle_hash"}
    }
    digest = module.digest(module.BUNDLE_DOMAIN, bundle_view)
    bundle["bundle_id"] = "sebv1:sha256:" + digest
    bundle["bundle_hash"] = "sha256:" + digest
    path = tmp_path / "rehashed.json"
    path.write_text(
        json.dumps(bundle, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return path


def eebus_source(bundle: dict) -> dict:
    return next(source for source in bundle["sources"] if source["source_kind"] == "EEBUS")


def eebus_artifact(bundle: dict) -> dict:
    return next(
        artifact for artifact in bundle["artifacts"] if artifact["source_kind"] == "EEBUS"
    )


def artifact_by_contract(bundle: dict, contract: str) -> dict:
    return next(
        artifact
        for artifact in bundle["artifacts"]
        if artifact["source_contract"] == contract
    )


def source_by_contract(bundle: dict, contract: str) -> dict:
    return next(
        source
        for source in bundle["sources"]
        if source["source_contract"] == contract
    )


def test_historical_tuple_and_fixture_bytes_are_immutable() -> None:
    assert hashlib.sha256(HISTORICAL_BUNDLE.read_bytes()).hexdigest() == (
        HISTORICAL_BUNDLE_SHA256
    )
    assert hashlib.sha256(HISTORICAL_REPLAY.read_bytes()).hexdigest() == (
        HISTORICAL_REPLAY_SHA256
    )
    assert hashlib.sha256(HISTORICAL_REGISTRY.read_bytes()).hexdigest() == (
        HISTORICAL_REGISTRY_SHA256
    )
    historical = registry_entries()[HISTORICAL_TUPLE]
    assert historical["owner_commit"] == HISTORICAL_OWNER_COMMIT
    assert historical["schema_sha256"] == HISTORICAL_SCHEMA_SHA256


def per_bundle_identity_values(bundle: dict) -> set[str]:
    values = {
        bundle["bundle_id"],
        bundle["capture_window"]["action"]["marker_id"],
    }
    for source in bundle["sources"]:
        values.add(source["source_id"])
        values.add(source["source_binding"]["runtime_pseudonym"])
        identity = source["ebus_identity"]
        if identity is not None:
            values.add(identity["target_pseudonym"])
        values.update(source["artifact_ids"])
    for artifact in bundle["artifacts"]:
        values.add(artifact["artifact_id"])
        values.add(artifact["remasking"]["scope_id"])
        values.update(
            entry["pseudonym"] for entry in artifact["remasking"]["entries"]
        )
    return values


def test_m625_fixture_uses_an_independent_bundle_identity_domain() -> None:
    historical = load_json(HISTORICAL_BUNDLE)
    m625 = load_json(M625_BUNDLE)
    assert per_bundle_identity_values(historical).isdisjoint(
        per_bundle_identity_values(m625)
    )
    marker = m625["capture_window"]["action"]["marker_id"]
    for source in m625["sources"]:
        assert source["capture_window"]["action"]["marker_id"] == marker
        assert source["source_binding"]["capture_window"]["action"]["marker_id"] == marker
    for artifact in m625["artifacts"]:
        assert artifact["capture_window"]["action"]["marker_id"] == marker
        assert artifact["source_binding"]["capture_window"]["action"]["marker_id"] == marker


def test_registry_appends_exact_m625_source_authority_tuple() -> None:
    entries = registry_entries()
    assert HISTORICAL_TUPLE in entries
    m625 = entries[M625_TUPLE]
    assert m625 == {
        "source_kind": "EEBUS",
        "source_contract": M625_TUPLE[1],
        "source_schema_version": 1,
        "owner_repository": "Project-Helianthus/helianthus-docs-eebus",
        "owner_path": M625_OWNER_PATH,
        "owner_commit": M625_OWNER_COMMIT,
        "schema_sha256": M625_SCHEMA_SHA256,
        "embedded_schema": (
            "docs/platform/schemas/vendor/"
            "helianthus.eebus.m625.public-redacted-evidence.v1.schema.json"
        ),
    }
    assert VENDORED_M625_SCHEMA.is_file()
    assert hashlib.sha256(VENDORED_M625_SCHEMA.read_bytes()).hexdigest() == (
        M625_SCHEMA_SHA256
    )


def test_m625_fixture_and_canonical_generator_inventory_is_complete() -> None:
    for path in (GENERATOR, M625_BUNDLE, M625_REPLAY):
        assert path.is_file(), f"missing M6.25 synchronized-evidence artifact: {path}"


def test_generator_reproduces_committed_bundle_and_replay_bytes(
    tmp_path: pathlib.Path,
) -> None:
    first = tmp_path / "first"
    second = tmp_path / "second"
    for output in (first, second):
        result = subprocess.run(
            [
                sys.executable,
                str(GENERATOR),
                "--output-dir",
                str(output),
            ],
            cwd=REPO_ROOT,
            check=False,
            capture_output=True,
            text=True,
            env={**os.environ, "PYTHONHASHSEED": "random"},
        )
        assert result.returncode == 0, result.stdout + result.stderr
        assert result.stderr == ""
    for name, committed in (
        ("bundle.json", M625_BUNDLE),
        ("replay-result.json", M625_REPLAY),
    ):
        assert (first / name).read_bytes() == committed.read_bytes()
        assert (second / name).read_bytes() == committed.read_bytes()


def test_m625_bundle_validates_and_replays_to_exact_golden_bytes() -> None:
    verified = run_validator("verify", M625_BUNDLE)
    replayed = run_validator("replay", M625_BUNDLE)
    assert verified.returncode == 0, verified.stdout + verified.stderr
    assert verified.stdout == "ok\n"
    assert verified.stderr == ""
    assert replayed.returncode == 0, replayed.stdout + replayed.stderr
    assert replayed.stdout == M625_REPLAY.read_text(encoding="utf-8")
    assert replayed.stderr == ""
    for schema, fixture in (
        (BUNDLE_SCHEMA, M625_BUNDLE),
        (REPLAY_SCHEMA, M625_REPLAY),
    ):
        schema_result = subprocess.run(
            ["jv", str(schema), str(fixture)],
            cwd=REPO_ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        assert schema_result.returncode == 0, (
            schema_result.stdout + schema_result.stderr
        )


def test_m625_dispatch_preserves_complete_path_and_comparison_pointers() -> None:
    bundle = load_json(M625_BUNDLE)
    source = eebus_source(bundle)
    artifact = eebus_artifact(bundle)
    payload = artifact["normalized_evidence"]
    assert (
        source["source_contract"],
        artifact["source_contract"],
        source["source_binding"]["source_contract"],
    ) == (M625_TUPLE[1],) * 3
    assert source["source_binding"]["operation_id"] == "eebus.v1.features.data.get"

    observation = payload["observations"][0]
    path = payload["feature_paths"][observation["path_index"]]
    assert [segment["kind"] for segment in path["feature_path"]] == [
        "SERVICE",
        "ENTITY",
        "FEATURE",
        "FIELD",
    ]
    assert [segment["selector"] for segment in path["feature_path"][:3]] == [
        path["service"],
        path["entity"],
        path["feature"],
    ]
    assert observation["value"] == "21.5"
    assert observation["unit"] == "degC"

    manifested = {
        entry["path"]: entry["pseudonym"]
        for entry in artifact["remasking"]["entries"]
    }
    assert set(manifested) == {
        "/feature_paths/0/entity",
        "/feature_paths/0/feature",
        "/feature_paths/0/feature_path/0/selector",
        "/feature_paths/0/feature_path/1/selector",
        "/feature_paths/0/feature_path/2/selector",
        "/feature_paths/0/feature_path/3/selector",
        "/feature_paths/0/service",
        "/observations/0/observation_ref",
        "/services/0",
    }
    assert manifested["/services/0"] == path["service"]
    assert manifested["/feature_paths/0/service"] == path["service"]
    assert (
        manifested["/feature_paths/0/feature_path/0/selector"]
        == path["service"]
    )


@pytest.mark.parametrize(
    "mutation,category",
    (
        (
            lambda bundle: _substitute_historical_tuple(bundle),
            "schema.source",
        ),
        (
            lambda bundle: eebus_source(bundle)["source_binding"].__setitem__(
                "owner_commit", HISTORICAL_OWNER_COMMIT
            ),
            "binding.registry",
        ),
        (
            lambda bundle: eebus_artifact(bundle)["source_binding"].__setitem__(
                "schema_sha256", HISTORICAL_SCHEMA_SHA256
            ),
            "binding.registry",
        ),
        (
            lambda bundle: eebus_artifact(bundle)["normalized_evidence"].pop(
                "observations"
            ),
            "schema.source",
        ),
        (
            lambda bundle: eebus_artifact(bundle)["normalized_evidence"][
                "feature_paths"
            ][0]["feature_path"][1].__setitem__("selector", "Z" * 43),
            "schema.source",
        ),
    ),
    ids=(
        "tuple-substitution",
        "owner-mismatch",
        "schema-hash-mismatch",
        "malformed-payload",
        "incomplete-pseudonymous-path",
    ),
)
def test_m625_tuple_and_payload_mutations_fail_closed(
    tmp_path: pathlib.Path, mutation, category: str
) -> None:
    result = run_validator("verify", write_mutation(tmp_path, mutation))
    assert result.returncode == 1
    assert result.stdout == f"{category}\n"
    assert result.stderr == ""


def _substitute_historical_tuple(bundle: dict) -> None:
    historical = registry_entries()[HISTORICAL_TUPLE]
    for value in (eebus_source(bundle), eebus_artifact(bundle)):
        value["source_contract"] = HISTORICAL_TUPLE[1]
        binding = value["source_binding"]
        binding["source_contract"] = HISTORICAL_TUPLE[1]
        for field in (
            "owner_repository",
            "owner_path",
            "owner_commit",
            "schema_sha256",
        ):
            binding[field] = historical[field]
        binding["operation_id"] = "eebus.v1.services.list"
        binding["snapshot_scope"] = {"mode": "LIVE_READ", "selector": "services"}
        binding["request_scope"]["operation_scope"] = "services"


def load_candidate_validator():
    scripts = str(PLATFORM_ROOT / "scripts")
    if scripts not in sys.path:
        sys.path.insert(0, scripts)
    spec = importlib.util.spec_from_file_location(
        "candidate_fact_m625_validator", CANDIDATE_VALIDATOR
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def refresh_candidate_hashes(module, graph: dict) -> None:
    for fact in graph["facts"]:
        fact["fact_hash"] = "sha256:" + module.fact_hexdigest(fact)
    digest = module.graph_hexdigest(graph)
    graph["graph_id"] = "dcfgv1:sha256:" + digest
    graph["graph_hash"] = "sha256:" + digest


def candidate_graph_for_source(module, source: dict, replay: dict) -> dict:
    graph = deepcopy(load_json(CANDIDATE_GRAPH))
    graph["source_bundle"] = {
        "contract": source["contract"],
        "schema_version": source["schema_version"],
        "bundle_id": source["bundle_id"],
        "bundle_hash": source["bundle_hash"],
        "replay_hash": "sha256:" + module.source_replay_hexdigest(replay),
        "evidence_refs": deepcopy(source["evidence_refs"]),
    }
    for fact in graph["facts"]:
        provenance = fact["provenance"]
        provenance["source_bundle_id"] = source["bundle_id"]
        if provenance["ebus"] is not None:
            family = provenance["ebus"]["family"]
            contract = f"helianthus.ebus.{family.lower()}.evidence.v1"
            source_row = source_by_contract(source, contract)
            artifact = artifact_by_contract(source, contract)
            provenance["ebus_source_id"] = source_row["source_id"]
            provenance["ebus_artifact_id"] = artifact["artifact_id"]
            provenance["ebus"] = deepcopy(artifact["ebus_identity"])
        if provenance["eebus_source_id"] is not None:
            source_row = source_by_contract(source, M625_TUPLE[1])
            artifact = artifact_by_contract(source, M625_TUPLE[1])
            provenance["eebus_source_id"] = source_row["source_id"]
            provenance["eebus_artifact_id"] = artifact["artifact_id"]
            provenance["eebus_service"] = artifact["normalized_evidence"][
                "services"
            ][0]
        if provenance["cloud"] is not None:
            contract = "helianthus.cloud-app.precaptured.evidence.v1"
            source_row = source_by_contract(source, contract)
            artifact = artifact_by_contract(source, contract)
            provenance["cloud"]["source_id"] = source_row["source_id"]
            provenance["cloud"]["artifact_id"] = artifact["artifact_id"]
        provenance["native_evidence_refs"] = sorted(
            provenance["native_evidence_refs"],
            key=module.ref_sort_key,
        )
    refresh_candidate_hashes(module, graph)
    return graph


def test_candidate_outer_verifier_accepts_historical_and_m625_authorities(
    tmp_path: pathlib.Path,
) -> None:
    historical = subprocess.run(
        [
            sys.executable,
            str(CANDIDATE_VALIDATOR),
            "verify",
            "--graph",
            str(CANDIDATE_GRAPH),
            "--registry",
            str(CANDIDATE_REGISTRY),
            "--source-bundle",
            str(HISTORICAL_BUNDLE),
            "--source-replay",
            str(HISTORICAL_REPLAY),
        ],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert historical.returncode == 0, historical.stdout + historical.stderr

    module = load_candidate_validator()
    source = load_json(M625_BUNDLE)
    replay = load_json(M625_REPLAY)
    graph = candidate_graph_for_source(module, source, replay)
    graph_path = tmp_path / "m625-candidate.json"
    graph_path.write_text(
        json.dumps(graph, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    m625 = subprocess.run(
        [
            sys.executable,
            str(CANDIDATE_VALIDATOR),
            "verify",
            "--graph",
            str(graph_path),
            "--registry",
            str(CANDIDATE_REGISTRY),
            "--source-bundle",
            str(M625_BUNDLE),
            "--source-replay",
            str(M625_REPLAY),
        ],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert m625.returncode == 0, m625.stdout + m625.stderr
    assert m625.stdout == "ok\n"
    assert m625.stderr == ""


def m625_two_path_artifact() -> tuple[dict, dict]:
    bundle = deepcopy(load_json(M625_BUNDLE))
    artifact = eebus_artifact(bundle)
    payload = artifact["normalized_evidence"]
    second_path = deepcopy(payload["feature_paths"][0])
    second_path["entity"] = "R" * 43
    second_path["feature"] = "S" * 43
    second_path["feature_path"][1]["selector"] = second_path["entity"]
    second_path["feature_path"][2]["selector"] = second_path["feature"]
    second_path["feature_path"][3]["selector"] = "T" * 43
    payload["feature_paths"].append(second_path)
    second_observation = deepcopy(payload["observations"][0])
    second_observation["observation_ref"] = "obs-" + "U" * 43
    second_observation["path_index"] = 1
    payload["observations"].append(second_observation)
    return bundle, artifact


def m625_sample_fact(artifact: dict, observation_index: int) -> dict:
    bundle = load_json(M625_BUNDLE)
    ebus = next(row for row in bundle["artifacts"] if row["source_kind"] == "EBUS")
    payload = artifact["normalized_evidence"]
    selected_path = payload["feature_paths"][0]
    return {
        "provenance": {
            "native_evidence_refs": [
                deepcopy(ebus["evidence_refs"][0]),
                deepcopy(artifact["evidence_refs"][0]),
            ],
            "ebus_source_id": ebus["source_id"],
            "ebus_artifact_id": ebus["artifact_id"],
            "eebus_source_id": artifact["source_id"],
            "eebus_artifact_id": artifact["artifact_id"],
            "eebus_service": selected_path["service"],
            "eebus": deepcopy(selected_path),
        },
        "comparator": {
            "samples": [
                {
                    "left": {
                        "source_kind": "EBUS",
                        "source_id": ebus["source_id"],
                        "artifact_id": ebus["artifact_id"],
                        "evidence_ref": deepcopy(ebus["evidence_refs"][0]),
                        "observed_offset_ns": ebus[
                            "recorder_ingested_offset_ns"
                        ],
                        "value_pointer": "/observations/0/value",
                        "unit_pointer": "/observations/0/unit",
                        "native_decimal": "21.5",
                        "native_unit": "degC",
                    },
                    "right": {
                        "source_kind": "EEBUS",
                        "source_id": artifact["source_id"],
                        "artifact_id": artifact["artifact_id"],
                        "evidence_ref": deepcopy(artifact["evidence_refs"][0]),
                        "observed_offset_ns": artifact[
                            "recorder_ingested_offset_ns"
                        ],
                        "value_pointer": (
                            f"/observations/{observation_index}/value"
                        ),
                        "unit_pointer": (
                            f"/observations/{observation_index}/unit"
                        ),
                        "native_decimal": "21.5",
                        "native_unit": "degC",
                    },
                }
            ]
        },
    }


def test_candidate_m625_pointer_binding_is_exact_and_path_index_bound() -> None:
    module = load_candidate_validator()
    bundle, artifact = m625_two_path_artifact()
    artifacts = module._artifact_index(bundle)
    valid = m625_sample_fact(artifact, 0)
    module._check_sample_provenance(valid, artifacts)

    mismatch = m625_sample_fact(artifact, 1)
    with pytest.raises(module.Failure):
        module._check_sample_provenance(mismatch, artifacts)

    malformed = m625_sample_fact(artifact, 0)
    malformed["comparator"]["samples"][0]["right"]["value_pointer"] = (
        "/observations/00/value"
    )
    with pytest.raises(module.Failure):
        module._check_sample_provenance(malformed, artifacts)


def test_candidate_m625_pointer_binding_matches_source_schema_path_index_rules(
    tmp_path: pathlib.Path,
) -> None:
    module = load_candidate_validator()
    bundle, artifact = m625_two_path_artifact()
    artifacts = module._artifact_index(bundle)
    payload = artifact["normalized_evidence"]
    payload["observations"][0]["path_index"] = 0.0

    assert schema_accepts(VENDORED_M625_SCHEMA, payload, tmp_path / "integral")
    module._check_sample_provenance(m625_sample_fact(artifact, 0), artifacts)

    bound_to_other_path = m625_sample_fact(artifact, 0)
    bound_to_other_path["provenance"]["eebus"] = payload["feature_paths"][1]
    bound_to_other_path["provenance"]["eebus_service"] = payload["feature_paths"][1][
        "service"
    ]
    with pytest.raises(module.Failure):
        module._check_sample_provenance(bound_to_other_path, artifacts)

    for invalid_path_index in (True, 0.5, 2):
        invalid_bundle, invalid_artifact = m625_two_path_artifact()
        invalid_artifact["normalized_evidence"]["observations"][0][
            "path_index"
        ] = invalid_path_index
        with pytest.raises(module.Failure):
            module._check_sample_provenance(
                m625_sample_fact(invalid_artifact, 0),
                module._artifact_index(invalid_bundle),
            )


def test_m625_rehashed_bundle_rejects_observation_ref_shared_across_paths(
    tmp_path: pathlib.Path,
) -> None:
    module = load_candidate_validator().synchronized
    bundle, artifact = m625_two_path_artifact()
    payload = artifact["normalized_evidence"]
    second_path = payload["feature_paths"][1]
    payload["observations"][1]["observation_ref"] = payload["observations"][0][
        "observation_ref"
    ]
    for field in ("service", "entity", "feature"):
        artifact["remasking"]["entries"].append(
            {
                "path": f"/feature_paths/1/{field}",
                "pseudonym": second_path[field],
            }
        )
    for index, segment in enumerate(second_path["feature_path"]):
        artifact["remasking"]["entries"].append(
            {
                "path": f"/feature_paths/1/feature_path/{index}/selector",
                "pseudonym": segment["selector"],
            }
        )
    artifact["remasking"]["entries"].append(
        {
            "path": "/observations/1/observation_ref",
            "pseudonym": payload["observations"][0][
                "observation_ref"
            ].removeprefix("obs-"),
        }
    )
    artifact["remasking"]["entries"].sort(key=lambda entry: entry["path"])
    artifact["item_count"] = len(payload["observations"])
    artifact["byte_count"] = len(module.canonical(payload))

    result = run_validator(
        "verify", write_rehashed_bundle(tmp_path, bundle, module)
    )
    assert result.returncode == 1
    assert result.stdout == "privacy.remask\n"
    assert result.stderr == ""


def schema_accepts(path: pathlib.Path, payload: dict, tmp_path: pathlib.Path) -> bool:
    tmp_path.mkdir(parents=True, exist_ok=True)
    instance = tmp_path / "source.json"
    instance.write_text(
        json.dumps(payload, ensure_ascii=False, separators=(",", ":"), sort_keys=True),
        encoding="utf-8",
    )
    result = subprocess.run(
        ["jv", str(path), str(instance)],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    return result.returncode == 0


def validator_accepts_m625(module, artifact: dict, payload: dict) -> bool:
    candidate = deepcopy(artifact)
    candidate["normalized_evidence"] = payload
    try:
        module.validate_m625_eebus_payload(payload, candidate)
        module.validate_m625_path_binding(payload)
    except module.Failure:
        return False
    return True


def test_m625_validator_matches_vendored_source_schema_for_integer_edges(
    tmp_path: pathlib.Path,
) -> None:
    module = load_candidate_validator().synchronized
    artifact = eebus_artifact(load_json(M625_BUNDLE))
    base = deepcopy(artifact["normalized_evidence"])
    schema_integral = deepcopy(base)
    schema_integral["schema_version"] = 1.0
    schema_bool = deepcopy(base)
    schema_bool["schema_version"] = True
    path_integral = deepcopy(base)
    path_integral["observations"][0]["path_index"] = 0.0
    path_bool = deepcopy(base)
    path_bool["observations"][0]["path_index"] = True
    repeated_path = deepcopy(base)
    second = deepcopy(repeated_path["observations"][0])
    second["observation_ref"] = "obs-" + "V" * 43
    repeated_path["observations"].append(second)

    for name, payload in (
        ("base", base),
        ("schema-version-integral-number", schema_integral),
        ("schema-version-bool", schema_bool),
        ("path-index-integral-number", path_integral),
        ("path-index-bool", path_bool),
        ("repeated-path-index", repeated_path),
    ):
        expected = schema_accepts(
            VENDORED_M625_SCHEMA, payload, tmp_path / name
        )
        actual = validator_accepts_m625(module, artifact, payload)
        assert actual == expected, name


@pytest.mark.parametrize(
    "mutation",
    (
        lambda bundle: _set_all_schema_versions(bundle, True),
        lambda bundle: eebus_artifact(bundle).__setitem__("item_count", True),
        lambda bundle: eebus_artifact(bundle).__setitem__("byte_count", True),
    ),
    ids=("schema-version-bool", "item-count-bool", "byte-count-bool"),
)
def test_bundle_integer_fields_reject_boolean_before_hash(
    tmp_path: pathlib.Path, mutation
) -> None:
    result = run_validator("verify", write_mutation(tmp_path, mutation))
    assert result.returncode == 1
    assert result.stdout == "schema.bundle\n"
    assert result.stderr == ""


def _set_all_schema_versions(bundle: dict, value: bool) -> None:
    bundle["schema_version"] = value
    for source in bundle["sources"]:
        source["schema_version"] = value
    for artifact in bundle["artifacts"]:
        artifact["schema_version"] = value


def test_m625_remasking_rejects_one_pseudonym_for_distinct_identities() -> None:
    module = load_candidate_validator().synchronized
    artifact = deepcopy(eebus_artifact(load_json(M625_BUNDLE)))
    payload = artifact["normalized_evidence"]
    service = payload["services"][0]
    payload["feature_paths"][0]["entity"] = service
    payload["feature_paths"][0]["feature_path"][1]["selector"] = service
    artifact["remasking"]["entries"] = [
        entry
        for entry in artifact["remasking"]["entries"]
        if entry["path"] != "/feature_paths/0/entity"
    ]
    with pytest.raises(module.Failure):
        module.validate_remasking([artifact])


def test_candidate_fact_consumes_m625_identity_and_observation_pointers() -> None:
    module = load_candidate_validator()
    bundle = load_json(M625_BUNDLE)
    artifact = eebus_artifact(bundle)
    payload = artifact["normalized_evidence"]
    observation = payload["observations"][0]
    path = payload["feature_paths"][observation["path_index"]]
    source = eebus_source(bundle)
    provenance = {
        "ebus_source_id": None,
        "ebus_artifact_id": None,
        "ebus": None,
        "eebus_source_id": source["source_id"],
        "eebus_artifact_id": artifact["artifact_id"],
        "eebus_service": path["service"],
        "eebus": path,
    }
    module.check_identities({"facts": [{"provenance": provenance}]}, bundle)

    side = {
        "source_kind": "EEBUS",
        "source_id": source["source_id"],
        "artifact_id": artifact["artifact_id"],
        "evidence_ref": deepcopy(artifact["evidence_refs"][0]),
        "observed_offset_ns": artifact["recorder_ingested_offset_ns"],
        "value_pointer": "/observations/0/value",
        "unit_pointer": "/observations/0/unit",
        "native_decimal": "21.5",
        "native_unit": "degC",
    }
    index = {(source["source_id"], artifact["artifact_id"]): artifact}
    value, unit, offset = module._bind_observation_side(
        side, "EEBUS", index, None
    )
    assert value == Decimal("21.5")
    assert unit == "degC"
    assert offset == artifact["recorder_ingested_offset_ns"]
