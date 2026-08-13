from __future__ import annotations

import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
ARCH_REL = "architecture/_candidate/post-m9-operator-pairing-browsers-v1.md"
API_REL = "api/_candidate/post-m9-operator-admin-v1.md"
ARCH = ROOT / ARCH_REL
API = ROOT / API_REL
M4B = ROOT / "architecture/_candidate/msp-04b-first-trust-admin-local.md"
MSP052 = ROOT / "architecture/_candidate/msp-052-outbound-pairing-contract.md"


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
            "derived, falsifiable target awaiting the final owner-authorized live run",
            "not an evidence-backed claim that every VR940 has that cardinality",
            "does not bind those counts to VR940",
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

    def test_ha_credential_cannot_autonomously_read_or_mutate_trust(self) -> None:
        _, architecture = read_markdown(ARCH)
        _, api = read_markdown(API)
        normalized = " ".join((architecture + api).split())
        required = (
            "Endpoint Authorization Matrix",
            "`candidate` view | allow | deny",
            "Raw SPINE page | allow | deny; open Portal instead",
            "Confirm candidate trust | allow after OOB comparison | deny",
            "Revoke durable trust | allow | deny",
            "There is no HA mutation grant, minting route, exchange route, mutation scope, or credential escalation",
            "contains no query or fragment data and conveys no authority",
            "owner performs every mutation directly in Portal",
            "`ha_integration` projection omits every candidate-derived field",
            "candidate count, presence, lifecycle state, expiry, identity, failure",
            "indistinguishable for zero versus one-or-more candidates",
            "revision is not advanced or partitioned solely to signal a candidate-visible change",
            "receives no pairing-window state, deadline, `register` state, or owner-intent derivative",
            "automatic window close, commit failure, or any other candidate lifecycle event alone changes no HA-visible field",
            "complete HA JSON projection is byte-identical across `OPEN_EMPTY`, `CANDIDATE_PENDING`, `TRANSIENT_TRUSTED`, `COMMITTING`, and failed-closed states",
            "Candidate-bound, connected-untrusted, and transient-trust sessions are absent from every HA row, count, revision input, and degradation input",
            "`connected` includes only rows already backed by an independently usable durable association",
        )
        for phrase in required:
            self.assertIn(phrase, normalized)

    def test_inbound_and_outbound_require_the_same_selected_observation(self) -> None:
        _, architecture = read_markdown(ARCH)
        _, api = read_markdown(API)
        _, msp052 = read_markdown(MSP052)
        normalized = " ".join((architecture + api + msp052).split())
        required = (
            "preserves the later MSP-052 selected-candidate inbound boundary",
            "inbound callback binds only when its TLS identity equals the already selected observation",
            "inbound peer that arrives before selection",
            "rejected without creating or replacing a candidate",
            "does not amend MSP-052 inbound eligibility",
            "inbound callback cannot select a candidate",
            "does not require an observation identifier",
            "single server-held current candidate",
            "no observation is fabricated",
            "Inbound `register=true` remains a local advertisement for bounded registration",
            "cannot select a candidate; it may bind TLS only for the exact already selected candidate",
            "volatile inbound winner reservation",
        )
        for phrase in required:
            self.assertIn(phrase, normalized)

    def test_m4b_relay_precedence_is_narrow_and_ephemeral(self) -> None:
        _, architecture = read_markdown(ARCH)
        normalized = " ".join(architecture.split())
        required = (
            "supersedes M4B's no-capture/no-share rule only to the minimum extent",
            "bounded request-lifetime memory",
            "transmit it once in the authenticated Portal response",
            "continuation of M4B's sole private candidate-read exception",
            "MUST NOT be logged, metriced, traced, persisted",
            "request/response buffers clear it immediately after the response completes",
            "Portal client may retain it only in the bounded active OOB view lifetime",
            "clears it on every specified terminal or UI event",
        )
        for phrase in required:
            self.assertIn(phrase, normalized)

    def test_authentication_material_uses_only_designated_transport_fields(self) -> None:
        _, api = read_markdown(API)
        normalized = " ".join(api.split())
        required = (
            "designated secure session cookie, CSRF header, or HA authorization header",
            "URL, query string, request body, response, audit row, log, metric",
            "must never contain or echo",
            "never copied into application state, idempotency records, errors, or coordinator commands",
        )
        for phrase in required:
            self.assertIn(phrase, normalized)

    def test_candidate_http_and_ui_state_is_ephemeral(self) -> None:
        _, api = read_markdown(API)
        normalized = " ".join(api.split())
        required = (
            "`Cache-Control: private, no-store`",
            "`Pragma: no-cache`",
            "`Expires: 0`",
            "`Referrer-Policy: no-referrer`",
            "service workers and offline caches must exclude the entire",
            "clears them on candidate expiry or change, logout, navigation away, visibility loss",
            "never enter local/session storage, IndexedDB, browser history, URL state",
            "server and client lifetimes are distinct and both bounded",
            "request/response buffers clear candidate identity immediately after response completion",
            "only in the currently visible active OOB view long enough for the owner comparison",
        )
        for phrase in required:
            self.assertIn(phrase, normalized)

    def test_post_m9_explicitly_amends_m4b_without_widening_public_surfaces(self) -> None:
        _, architecture = read_markdown(ARCH)
        _, m4b = read_markdown(M4B)
        combined = " ".join((architecture + m4b).split())
        required = (
            "Amendment To The M4B Local Admin Boundary",
            "narrowly amends the candidate-free clauses",
            "immutable historical milestone artefact",
            "records precedence without rewriting M4B's original scope statement",
            "Public `Runtime`, MCP, GraphQL, Portal, and Home Assistant surfaces remain candidate-free",
            "does not add an MCP tool/resource, GraphQL mutation, Portal action, Home Assistant service",
            "same-UID AF_UNIX transport remains the private coordinator command",
            "authenticated `portal_owner` adapter",
            "The amendment does not expose `candidate_nonce`",
            "Home Assistant remains candidate-free",
            "public Runtime, MCP, GraphQL",
            "Every other M4B confidentiality, same-generation confirmation, persistence, and restart rule continues unchanged",
        )
        for phrase in required:
            self.assertIn(phrase, combined)

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
