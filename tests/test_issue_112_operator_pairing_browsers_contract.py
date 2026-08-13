from __future__ import annotations

import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
ARCH_REL = "architecture/_candidate/post-m9-operator-pairing-browsers-v1.md"
API_REL = "api/_candidate/post-m9-operator-admin-v1.md"
ARCH = ROOT / ARCH_REL
API = ROOT / API_REL


def read_markdown(path: Path) -> tuple[dict[str, str], str]:
    text = path.read_text(encoding="utf-8")
    _, front_matter, body = text.split("---", 2)
    return yaml.safe_load(front_matter), body


class PostM9OperatorContractTest(unittest.TestCase):
    def test_candidates_are_canonical_but_not_published_as_supported(self) -> None:
        for path in (ARCH, API):
            metadata, _ = read_markdown(path)
            self.assertEqual(metadata["publication_status"], "candidate")
            self.assertEqual(metadata["hypothesis_status"], "draft")
            for channel in (
                "stable_navigation",
                "search",
                "sitemap",
                "versioned_bundle",
                "release_bundle",
            ):
                self.assertEqual(metadata[channel], "false")

        self.assertEqual(read_markdown(ARCH)[0]["claim_status"], "evidence-backed")
        self.assertEqual(read_markdown(API)[0]["claim_status"], "evidence-backed")
        self.assertEqual(read_markdown(API)[0]["candidate_output"], "true")
        self.assertEqual(read_markdown(API)[0]["candidate_output_path"], API_REL)
        for relative in (
            "api/search-index.json",
            "api/sitemap.xml",
            "api/versioned-bundle.txt",
            "api/release-bundle.txt",
        ):
            published = (ROOT / relative).read_text(encoding="utf-8")
            self.assertNotIn(ARCH_REL, published)
            self.assertNotIn(API_REL, published)

    def test_architecture_preserves_namespace_and_ownership(self) -> None:
        _, body = read_markdown(ARCH)
        normalized = " ".join(body.split())
        required = (
            "stable raw MCP namespace remains exactly `eebus.v1.*`",
            "No `eebus.v2.*`",
            "Stable public MCP stays read-only",
            "Gateway authenticated admin boundary",
            "Direct trust-store access",
            "eeBUS operator socket",
            "never creates a Portal or Home Assistant model of protocol truth",
            "must not enter `ebus.v1`",
            "unrelated GraphQL fields",
            "semantic registry",
        )
        for phrase in required:
            self.assertIn(phrase, normalized)

    def test_pairing_is_explicit_generation_bound_and_fail_closed(self) -> None:
        _, body = read_markdown(ARCH)
        normalized = " ".join(body.split())
        required = (
            "complete 40-character lowercase certificate short identifier",
            "independent OOB source",
            "No step auto-trusts a peer",
            "same-generation protocol completion",
            "non-empty `remote_ship_id` value",
            "Persistence failure is terminal",
            "CSRF proof",
            "idempotency binding",
            "deterministic non-mutating rejection",
        )
        for phrase in required:
            self.assertIn(phrase, normalized)

    def test_ship_and_spine_models_cover_live_acceptance_shape(self) -> None:
        _, body = read_markdown(ARCH)
        normalized = " ".join(body.split())
        for view in ("`trusted`", "`connected`", "`discovered`", "`candidate`"):
            self.assertIn(view, normalized)
        for phrase in (
            "device/entity/feature/use-case topology",
            "opaque unknown fields",
            "eleven entities",
            "twenty features",
            "use-case claims",
            "acceptance shape, not a universal",
        ):
            self.assertIn(phrase, normalized)

    def test_admin_api_is_closed_authenticated_csrf_safe_and_non_disclosing(self) -> None:
        _, body = read_markdown(API)
        normalized = " ".join(body.split())
        required = (
            "helianthus.eebus.operator-admin.v1",
            "portal_owner",
            "ha_integration",
            "Mandatory session-bound CSRF token",
            "Idempotency-Key",
            "state_revision",
            "eebus.admin.trust",
            "candidate:confirm",
            "DELETE /admin/eebus/v1/partners/{partner_id}/trust",
            "No response or request contains `candidate_ref`",
            "private key",
            "private PEM",
            "trust-store bytes",
            "raw socket frame",
        )
        for phrase in required:
            self.assertIn(phrase, normalized)

    def test_closed_degraded_outcomes_are_documented(self) -> None:
        _, architecture = read_markdown(ARCH)
        _, api = read_markdown(API)
        combined = architecture + api
        for outcome in (
            "discovery_unavailable",
            "listener_unavailable",
            "trust_denied",
            "attempt_timeout",
            "disconnected",
            "backoff_active",
            "terminal_quarantine",
            "persistence_failure",
            "unknown_state",
        ):
            self.assertIn(outcome, combined)


if __name__ == "__main__":
    unittest.main()
