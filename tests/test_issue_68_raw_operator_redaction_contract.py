from __future__ import annotations

import hashlib
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

    def test_complete_forward_amendment_and_candidate_bindings_satisfy_the_gate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = copy_repo(Path(tmp))
            amendment = repo / repository_policy.ISSUE68_AMENDMENT_REL
            amendment.parent.mkdir(parents=True, exist_ok=True)
            required_markers = (
                "one initial `eebus.v1.*` namespace",
                "authorized local/operator default is `mask_tier=raw`",
                "public/shareable export is explicit `mask_tier=redacted`",
                "authorization is enforced fail-closed at the boundary",
                "device fields: identity, useful protocol metadata",
                "entity fields: type, address, description",
                "feature fields: type, role, address, description",
                "use-case fields: name, actor, role, scenario, context, version",
                "unknown protocol fields remain inspectable raw or opaque values",
                "SKI, SHIP ID, SPINE addresses, and protocol metadata are operational data visible to the authorized local operator",
                "reference binding includes runtime, contract, tool, scope, mask_tier, and auth_scope",
                "dereference rejects a mismatched mask_tier or auth_scope",
                "private keys, private PEM material, tokens, trust-store bytes, and cryptographic secrets are forbidden in every tier",
                "`candidate_ref` is forbidden from the stable public API",
                "public/shareable artifacts redact stable identities",
            )
            amendment.write_text("\n".join(required_markers) + "\n", encoding="utf-8")
            for relative in repository_policy.ISSUE68_CURRENT_CONTRACT_RELS:
                path = repo / relative
                path.write_text(
                    path.read_text(encoding="utf-8")
                    + f"\n{repository_policy.ISSUE68_AMENDMENT_REL.name}\n",
                    encoding="utf-8",
                )

            self.assertEqual(repository_policy.issue_68_raw_operator_redaction_errors(repo), [])


if __name__ == "__main__":
    unittest.main()
