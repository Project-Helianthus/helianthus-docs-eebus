from __future__ import annotations

import copy
import importlib.util
import os
import pathlib
import subprocess

import pytest
import yaml


REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
MANIFEST_PATH = REPO_ROOT / "docs/platform/manifests/eebus-doc-ownership.yaml"
INPUTS_PATH = REPO_ROOT / "docs/platform/manifests/msp-0625-public-inputs.yaml"
M625_SOURCE_REF = "cedf238e" + "34f879815ba773e9cd76b2b31c2822a3"
M625_PLAN_REF = "fb384ab5" + "7d79f0020c54d2c66416e8a7666f0ceb"
TRUSTED_BASE_REF = "8215201a" + "4274db5310ee672619ba2f1d27b99bec"
COMBINED_DOCS_EEBUS_REF = "b9413bda" + "992b99e4f719ad2e26e1937ff11a5b4a"
M625_PROVENANCE_URL = (
    "https://api.github.com/repositories/1293598306/contents/"
    "development/msp-0625-provenance-policy.md"
    f"?ref={M625_SOURCE_REF}"
)
M625_ARCHITECTURE_URL = (
    "https://api.github.com/repositories/1293598306/contents/"
    "architecture/_candidate/msp-0625-raw-feature-command-path.md"
    f"?ref={M625_SOURCE_REF}"
)


def load_validator():
    spec = importlib.util.spec_from_file_location(
        "validate_platform_contracts",
        REPO_ROOT / "scripts/validate_platform_contracts.py",
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def cross_seed_text() -> str:
    return (
        REPO_ROOT
        / "docs/platform/msp-0625-public-acquisition-methodology.md"
    ).read_text(encoding="utf-8")


def test_m625_cross_seed_is_active_methodology_and_immutably_bound() -> None:
    validator = load_validator()
    manifest = yaml.safe_load(MANIFEST_PATH.read_text(encoding="utf-8"))
    entry = next(
        item
        for item in manifest["entries"]
        if item["id"] == validator.M625_CROSS_SEED_ID
    )

    assert entry["state"] == "active"
    assert entry["canonical"] is True
    assert entry["owner"]["path"] == validator.M625_CROSS_SEED_PATH.as_posix()
    assert entry["source"] == entry["owner"]
    assert entry["lifecycle"]["source_pr"] == (
        "Project-Helianthus/helianthus-docs-ebus#381"
    )
    assert entry["lifecycle"]["source_ref"] is None
    assert entry["lifecycle"]["content_sha256"] is None
    assert validator._m625_cross_seed_categories(REPO_ROOT, manifest) == set()

    forged = copy.deepcopy(entry)
    forged["source"]["repository"] = "helianthus-docs-ebus"
    assert validator._surface_binding_valid(forged) is False


def test_m625_cross_seed_manifest_entry_is_required_fail_closed() -> None:
    validator = load_validator()
    manifest = yaml.safe_load(MANIFEST_PATH.read_text(encoding="utf-8"))
    manifest["entries"] = [
        entry
        for entry in manifest["entries"]
        if entry["id"] != "platform-m625-public-acquisition-methodology"
    ]

    assert validator._m625_cross_seed_categories(REPO_ROOT, manifest) == {
        "m625.cross-seed-manifest"
    }


def test_m625_cross_seed_complete_deletion_is_required_fail_closed(
    tmp_path: pathlib.Path,
) -> None:
    """The static M6.25 registry, not surviving artifacts, anchors the gate."""
    validator = load_validator()
    manifest = yaml.safe_load(MANIFEST_PATH.read_text(encoding="utf-8"))
    manifest["entries"] = [
        entry
        for entry in manifest["entries"]
        if entry["id"] != "platform-m625-public-acquisition-methodology"
    ]
    # Deliberately provide a root with neither page nor input binding.
    empty_root = tmp_path / "empty-docs-root"
    empty_root.mkdir()

    assert validator._m625_cross_seed_categories(empty_root, manifest) == {
        "m625.cross-seed-manifest"
    }


def test_m625_cross_seed_machine_binds_exact_external_inputs() -> None:
    validator = load_validator()
    binding = yaml.safe_load(INPUTS_PATH.read_text(encoding="utf-8"))
    manifest = yaml.safe_load(MANIFEST_PATH.read_text(encoding="utf-8"))

    assert binding["sources"] == [
        {
            "repository": "Project-Helianthus/helianthus-execution-plans",
            "ref": M625_PLAN_REF,
            "path": (
                "multi-runtime-semantic-platform.locked/"
                "118-w30-26-m625-raw-spine-feature-acquisition.md"
            ),
            "content_sha256": (
                "21c4e525a39090a1c4f4ca6efdedb05978bc9f7588f9acbcaa6039fc21fa4536"
            ),
            "url": validator.M625_PLAN_URL,
        },
        {
            "repository": "Project-Helianthus/helianthus-docs-eebus",
            "ref": M625_SOURCE_REF,
            "path": "development/msp-0625-provenance-policy.md",
            "content_sha256": (
                "f52a15cab0ec7cfebb67a1932b27259489846619b109ea71e43ca54531191db2"
            ),
            "url": M625_PROVENANCE_URL,
        },
        {
            "repository": "Project-Helianthus/helianthus-docs-eebus",
            "ref": M625_SOURCE_REF,
            "path": (
                "architecture/_candidate/"
                "msp-0625-raw-feature-command-path.md"
            ),
            "content_sha256": (
                "e782c764e5bed3ca103b3544e2bfcb97f7869416184175ad576a90c8f6302e64"
            ),
            "url": M625_ARCHITECTURE_URL,
        },
    ]
    text = cross_seed_text()
    parsed_links = set(validator._markdown_links(text, include_rendered=False))
    assert validator.M625_PLAN_URL in parsed_links
    assert M625_PROVENANCE_URL in parsed_links
    assert M625_ARCHITECTURE_URL in parsed_links
    assert f"`{M625_PROVENANCE_URL}`" not in text
    assert f"`{M625_ARCHITECTURE_URL}`" not in text
    assert validator._m625_cross_seed_categories(REPO_ROOT, manifest) == set()


def test_m625_source_links_coexist_with_the_exact_trusted_base_validator(
    tmp_path: pathlib.Path,
) -> None:
    """M6.25 source links must not become legacy combined-ref forward links."""
    trusted_root = os.environ.get("M625_TRUSTED_BASE_ROOT")
    if not trusted_root:
        default_checkout = REPO_ROOT / ".tmp" / "m625-trusted-base"
        if default_checkout.is_dir():
            trusted_root = os.fspath(default_checkout)
    if trusted_root:
        trusted_checkout = pathlib.Path(trusted_root)
        assert (
            subprocess.run(
                ["git", "-C", trusted_checkout, "rev-parse", "--verify", "HEAD"],
                check=True,
                capture_output=True,
                text=True,
            ).stdout.strip()
            == TRUSTED_BASE_REF
        )
        validator_source = (
            trusted_checkout / "scripts/validate_platform_contracts.py"
        ).read_text(encoding="utf-8")
    else:
        validator_source = subprocess.run(
            [
                "git",
                "show",
                f"{TRUSTED_BASE_REF}:scripts/validate_platform_contracts.py",
            ],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        ).stdout
    trusted_path = tmp_path / "trusted_validate_platform_contracts.py"
    trusted_path.write_text(validator_source, encoding="utf-8")
    spec = importlib.util.spec_from_file_location(
        "trusted_validate_platform_contracts", trusted_path
    )
    assert spec is not None and spec.loader is not None
    trusted = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(trusted)

    manifest = yaml.safe_load(MANIFEST_PATH.read_text(encoding="utf-8"))
    combined_target = tmp_path / "protocols/ship-spine-overview.md"
    combined_target.parent.mkdir()
    combined_target.write_text("trusted combined target\n", encoding="utf-8")
    assert trusted._link_categories(
        REPO_ROOT, tmp_path, COMBINED_DOCS_EEBUS_REF, manifest
    ) == set()


def test_m625_external_provenance_fails_closed_for_unavailable_roots() -> None:
    validator = load_validator()

    assert validator._m625_external_input_categories(REPO_ROOT, {}) == {
        "m625.cross-seed-input-source"
    }


def test_m625_external_provenance_fails_closed_for_hash_mismatch(
    monkeypatch: pytest.MonkeyPatch, tmp_path: pathlib.Path
) -> None:
    validator = load_validator()
    source_roots = {
        source["repository"]: tmp_path / source["repository"].rsplit("/", 1)[-1]
        for source in validator.M625_EXTERNAL_INPUTS
    }
    for root in source_roots.values():
        root.mkdir()

    monkeypatch.setattr(validator, "_repository_root_valid", lambda *_: True)
    monkeypatch.setattr(validator, "_checkout_matches_ref", lambda *_: True)
    monkeypatch.setattr(
        validator,
        "_run_git_bytes",
        lambda *_: subprocess.CompletedProcess([], 0, stdout=b"wrong-content"),
    )

    assert validator._m625_external_input_categories(REPO_ROOT, source_roots) == {
        "m625.cross-seed-input-content"
    }


@pytest.mark.parametrize(
    ("mutation", "category"),
    [
        (
            "A wire-format message uses the field command_selector.",
            "m625.cross-seed-protocol-api-declaration",
        ),
        (
            "Clients call queryCrossSeed() to fetch the result.",
            "m625.cross-seed-protocol-api-declaration",
        ),
        (
            "The operational path now works against a real installation.",
            "m625.cross-seed-live-claim",
        ),
        (
            "An OEM document supplies the evidence for this behavior.",
            "m625.cross-seed-private-source-attribution",
        ),
        (
            "pass" + "word: " + "example-password-value",
            "m625.cross-seed-restricted-material",
        ),
        (
            "session_token = example-session-value",
            "m625.cross-seed-restricted-material",
        ),
        (
            "trust_store: example-trust-bytes",
            "m625.cross-seed-restricted-material",
        ),
        (
            "private_key: example-private-key-bytes",
            "m625.cross-seed-restricted-material",
        ),
        (
            "cryptographic_secret: example-secret-bytes",
            "m625.cross-seed-restricted-material",
        ),
        (
            "-----BEGIN " + "ENCRYPTED PRIVATE KEY-----",
            "m625.cross-seed-restricted-material",
        ),
        (
            "Bearer example-authorization-value",
            "m625.cross-seed-restricted-material",
        ),
        (
            "Return the session credential to the owner-authorized operator.",
            "m625.cross-seed-secret-policy",
        ),
        (
            "Password material is represented as a checksum in public evidence.",
            "m625.cross-seed-secret-policy",
        ),
    ],
)
def test_m625_cross_seed_rejects_independent_policy_mutations(
    mutation: str, category: str
) -> None:
    validator = load_validator()

    categories = validator._m625_cross_seed_text_categories(
        cross_seed_text() + f"\n{mutation}\n"
    )
    # A new paragraph also violates the closed thin-page shape.  The category
    # under test must still be independently present and not rely on that
    # structural rejection.
    assert category in categories


def test_m625_cross_seed_policy_checks_allow_legitimate_exclusion_prose() -> None:
    validator = load_validator()
    exclusion = (
        "\nNo protocol or API declaration is made. Live support remains unverified. "
        "Private vendor material is prohibited as evidence. Passwords, session "
        "tokens, bearer tokens, private keys, and trust-store bytes are prohibited "
        "in every tier and cannot be replaced by a digest.\n"
    )

    assert validator._m625_positive_assertion_categories(
        cross_seed_text() + exclusion
    ) == set()


def test_m625_cross_seed_states_all_tier_secret_and_digest_prohibition() -> None:
    text = cross_seed_text()

    assert "Every tier, including the owner-authorized local raw operator view" in text
    assert "private keys, passwords, credentials, bearer, session, and authentication tokens" in text
    assert "cryptographic secrets, and trust-store bytes" in text
    assert "cannot be replaced by a digest or other deterministic commitment" in text


def test_m625_focused_contract_is_in_local_and_github_docs_ci() -> None:
    donor_root = REPO_ROOT / ".tmp" / "docs-ebus"
    local_ci_paths = (
        REPO_ROOT / "scripts/ci_local.sh",
        donor_root / "scripts/ci_local.sh",
    )
    docs_ci_paths = (
        REPO_ROOT / ".github/workflows/docs-ci.yml",
        donor_root / ".github/workflows/docs-ci.yml",
    )
    combined_ref = (
        REPO_ROOT / ".github/workflows/platform-contracts-combined-ref.yml"
    ).read_text(encoding="utf-8")

    for local_ci_path in local_ci_paths:
        local_ci = local_ci_path.read_text(encoding="utf-8")
        assert "python3 -m pytest -q tests/test_m625_cross_seed_contract.py" in local_ci
        assert "--m625-docs-eebus-root \"${PLATFORM_M625_DOCS_EEBUS_ROOT}\"" in local_ci
        assert (
            "--m625-execution-plans-root \"${PLATFORM_M625_EXECUTION_PLANS_ROOT}\""
            in local_ci
        )
    for docs_ci_path in docs_ci_paths:
        docs_ci = docs_ci_path.read_text(encoding="utf-8")
        assert "M625_TRUSTED_BASE_ROOT" in docs_ci
        assert "Checkout exact M6.25 trusted validator base" in docs_ci
        assert "ref: " + TRUSTED_BASE_REF in docs_ci
        assert "path: checkouts/m625-trusted-base" in docs_ci
        assert (
            "M625_TRUSTED_BASE_ROOT: ${{ github.workspace }}/checkouts/m625-trusted-base"
            in docs_ci
        )
        assert "run: ./scripts/ci_local.sh" in docs_ci
    assert "Validate PR M6.25 provenance contract" in combined_ref
    assert "checkouts/docs/scripts/validate_platform_combined_ref.py" in combined_ref
    assert (
        combined_ref.count(
            "--m625-docs-eebus-root checkouts/m625-docs-eebus"
        )
        == 3
    )
    assert (
        combined_ref.count(
            "--m625-execution-plans-root checkouts/m625-execution-plans"
        )
        == 3
    )
