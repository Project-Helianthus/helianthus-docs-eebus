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
            "Stable raw MCP stays read-only",
            "`eebus.v1.*` is a host operator inspection surface",
            "not an anonymous, semantic, or public Internet API",
            "Gateway typed operator boundary",
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
            "derived, falsifiable target awaiting the final operator-confirmed live run",
            "not an evidence-backed claim that every VR940 has that cardinality",
            "does not bind those counts to VR940",
        ):
            self.assertIn(phrase, normalized)

    def test_lazy_spine_wire_shape_is_closed_lossless_and_snapshot_bound(self) -> None:
        _, body = read_markdown(API)
        normalized = " ".join(body.split())
        required = (
            "request=root",
            "request=children&snapshot_id=<opaque>&parent_node_id=<opaque>",
            "request=continue&snapshot_id=<opaque>&parent_node_id=<opaque>&cursor=<opaque>",
            "Missing, duplicate, unknown, empty, or extra parameters return `invalid_request`",
            "Page size is a fixed bounded server setting",
            "An expired snapshot or cursor returns `snapshot_expired`",
            "`next_cursor` is omitted exactly when that parent's fixed ordering is exhausted",
            "`helianthus.eebus.runtime.raw-snapshot.v1` inventory",
            "original field names, presence/omission, typed values, and opaque arrays preserved",
            "`device` | `ski`, `ship_id?`, `address`, `type`, `description?`, `metadata?`, `secondary_digest?`, `opaque?`",
            "`feature` | `device_address`, `entity_address`, `feature_address`, `type`, `role`, `description?`, `secondary_digest?`, `opaque?`",
            "`use_case_claim` | `context_address`, `name`, `actor`, `resolved_role?`, `scenarios?`, `version?`, `availability?`, `document_subrevision?`, `secondary_digest?`, `opaque?`",
            "may not replace, rename, synthesize, or discard any canonical payload field",
            "partner, parent node, stable sort position, and snapshot hash",
        )
        for phrase in required:
            self.assertIn(phrase, normalized)

    def test_eebus_specific_auth_is_not_a_pairing_prerequisite(self) -> None:
        _, architecture = read_markdown(ARCH)
        _, api = read_markdown(API)
        normalized = " ".join((architecture + api).split())
        required = (
            "eeBUS-specific authentication is out of scope",
            "does not define a login, session, cookie, CSRF token, owner credential, HA credential, or reauthentication flow",
            "Existing Portal and Home Assistant authentication lifecycles are outside this contract",
            "must not withhold pairing mutations pending a separate Portal authentication change",
        )
        for phrase in required:
            self.assertIn(phrase, normalized)

    def test_operator_api_is_closed_non_disclosing_and_not_an_auth_profile(self) -> None:
        _, body = read_markdown(API)
        normalized = " ".join(body.split())
        required = (
            "helianthus.eebus.operator-admin.v1",
            "Idempotency-Key",
            "state_revision",
            "confirm candidate",
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

    def test_portal_and_ha_have_the_same_closed_pairing_actions(self) -> None:
        _, architecture = read_markdown(ARCH)
        _, api = read_markdown(API)
        normalized = " ".join((architecture + api).split())
        required = (
            "Endpoint Operations Matrix",
            "| `candidate` view | allow | allow |",
            "| Raw SPINE page | allow | allow |",
            "| Open/close pairing window; select/connect/retry | allow | allow |",
            "| Confirm candidate trust | allow after OOB comparison | allow after OOB comparison |",
            "| Cancel current candidate | allow | allow |",
            "| Revoke durable trust | allow | allow |",
            "Home Assistant performs the same typed closed operations through the gateway boundary",
            "does not receive a trust-store handle or an operator socket",
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
            "once for the active OOB view",
            "Both host operator surfaces may receive the complete comparison identity",
            "replaces the earlier relay restriction",
            "continuation of M4B's sole private candidate-read exception",
            "MUST NOT be logged, metriced, traced, persisted",
            "request/response buffers clear it immediately after the response completes",
            "Each host client may retain it only in the bounded active OOB view lifetime",
            "clears it on every specified terminal or UI event",
        )
        for phrase in required:
            self.assertIn(phrase, normalized)
        self.assertNotIn("or sent to HA", normalized)
        self.assertNotIn("transmit it once in the Portal response", normalized)

    def test_routes_name_a_typed_gateway_operator_origin(self) -> None:
        _, api = read_markdown(API)
        normalized = " ".join(api.split())
        self.assertIn("typed gateway operator origin", normalized)
        self.assertNotIn("protected gateway admin origin", normalized)

    def test_action_time_confirmation_is_operational_not_login(self) -> None:
        _, api = read_markdown(API)
        normalized = " ".join(api.split())
        required = (
            "Live pairing confirmation at action time is an operational control, not an authentication mechanism",
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
            "active view retains the current candidate across unrelated responses",
            "closed terminal, abort, and newer-candidate-generation rules",
            "never enter local/session storage, IndexedDB, browser history, URL state",
            "server and client lifetimes are distinct and both bounded",
            "request/response buffers clear candidate identity immediately after response completion",
            "only in the currently visible active OOB view long enough for the operator comparison",
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
            "typed Portal and Home Assistant adapters",
            "The amendment does not expose `candidate_nonce`",
            "Home Assistant may invoke the same typed pairing operations",
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
