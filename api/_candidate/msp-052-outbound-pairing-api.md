---
canonical_source: "Project-Helianthus/helianthus-docs-eebus:api/_candidate/msp-052-outbound-pairing-api.md"
owner_domain: "api"
license: "AGPL-3.0-only"
publication_status: "candidate"
claim_status: "evidence-backed"
source_class: "derived_inference"
evidence_ids: "EV-20260720-001"
hypothesis_status: "draft"
falsifier: "A reviewed API contract exposes endpoint selection or trust mutation in the stable read-only surface, accepts a reference not bound to one current observation revision, or permits persistence before the durable trust result."
candidate_output: "true"
stable_navigation: "false"
search: "false"
sitemap: "false"
versioned_bundle: "false"
release_bundle: "false"
candidate_output_path: "api/_candidate/msp-052-outbound-pairing-api.md"
---

# Candidate MSP-052 Outbound Pairing API Boundary

## Status And Scope

This candidate records the eeBUS API boundary for [docs issue 52][docs-issue]
and companion [`helianthus-ship-go` pull request 15][ship-go-pr]. It adds no
stable declaration, wire schema, consumer availability, or protocol fact. It
describes the proposed public/read-only and experimental/admin split only.

## Stable Read-Only Candidate Visibility

The stable API surface is read-only candidate visibility. A visible row may
contain an opaque `candidate_ref`, its lifecycle state, and redacted evidence
status. `candidate_ref` names one exact, current mDNS observation revision for
the current process. It is not an endpoint token and must not expose or accept a
hostname, path, address, port, certificate, or peer identity.

The stable surface reports only the following state vocabulary: `visible`,
`selected/validated`, `connected-untrusted`, and `trusted`. It does not report
an approval secret, queue implementation, persisted association contents, or
an in-flight endpoint. A reference disappears when its observation is
withdrawn, replaced, consumed, or the process restarts.

## Experimental/Admin Mutation Boundary

Any action that selects a candidate is experimental/admin, not stable public
API. It accepts the opaque `candidate_ref` plus an operator-validated expected
SKI that is exactly 40 lowercase hexadecimal characters. The action rejects an
unknown or stale reference and a mismatched SKI. It cannot accept a
caller-supplied or static endpoint, and it has no hostname, path, or address
fallback.

The action creates no trust by itself. It may request a candidate-bound attempt
only after exact validation; TLS pinning precedes WebSocket upgrade; the
connection remains untrusted until durable trust commit. There is no public
auto-trust operation, no mutation that persists before that commit, and no
stable GraphQL, MCP, Portal, Home Assistant, CLI, or network-admin mutation.

Inbound `register=true` remains compatible as an inbound registration signal.
Passive discovery and allowlist evaluation alone never initiate a network
attempt, and public visibility never implies a selected, connected, or trusted
peer.

[docs-issue]: https://github.com/Project-Helianthus/helianthus-docs-eebus/issues/52
[ship-go-pr]: https://github.com/Project-Helianthus/helianthus-ship-go/pull/15
