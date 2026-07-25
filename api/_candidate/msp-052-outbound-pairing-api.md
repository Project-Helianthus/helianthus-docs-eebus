---
canonical_source: "Project-Helianthus/helianthus-docs-eebus:api/_candidate/msp-052-outbound-pairing-api.md"
owner_domain: "api"
license: "AGPL-3.0-only"
publication_status: "candidate"
claim_status: "evidence-backed"
source_class: "derived_inference"
evidence_ids: "EV-20260720-001"
hypothesis_status: "draft"
falsifier: "A reviewed API contract promotes candidate_ref or attempt-journal fields into stable eebusreg, MCP, or GraphQL; persists candidate_ref; accepts a non-current selection; or lets RuntimeConfig, static, or root fallback data authorize a dial."
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

This candidate records the eeBUS control-plane boundary for
[docs issue 54][docs-issue] and companion
[`helianthus-eebusreg` issue 58][eebusreg-issue], building on
[`helianthus-ship-go` pull request 15][ship-go-pr]. It adds no stable
declaration, wire schema, consumer availability, or protocol fact. Candidate
inspection and selection remain private, owner-only local administration; this
contract does not establish a promotion path for `candidate_ref`.

## Private Owner-Only Candidate Inspection

The same-UID local admin control plane may expose an opaque `candidate_ref`, its
lifecycle state, and redacted evidence status. This inspection surface is
experimental and non-public. `candidate_ref` names one exact, current mDNS
observation revision for the current process. It is not an endpoint token and
must not expose or accept a hostname, path, address, port, certificate, or peer
identity.

`candidate_ref` is a process-local dependency capability only. It may cross the
in-process discovery, private administration, and candidate-queue boundary for
the selected operation, but it is never durable and never stable
`helianthus-eebusreg`, MCP, or GraphQL state. It cannot be serialized into the
attempt journal, trusted association, snapshot, reconnect record, or consumer
payload.

The private local surface uses only the following state vocabulary: `visible`,
`selected/validated`, `connected-untrusted`, and `trusted`. It does not report
an approval secret, queue implementation, persisted association contents, or
an in-flight endpoint. A reference disappears when its observation is
withdrawn, replaced, consumed, or the process restarts.

## Experimental/Admin Mutation Boundary

Any action that selects a candidate is experimental/admin, not stable or public
API. It accepts the opaque `candidate_ref` plus an operator-validated expected
SKI that is exactly 40 lowercase hexadecimal characters. The action rejects an
unknown or stale reference and a mismatched SKI. It cannot accept a
caller-supplied or static endpoint, and it has no hostname, path, or address
fallback.

The dependency-fork names `PairingCandidateQueuer` and `CandidateRef` are
private experimental process-local dependency capabilities only. They are not
members of the public Helianthus `eebusruntime` v1 API, stable MCP, GraphQL,
Portal, or Home Assistant surfaces. Their presence in a dependency does not
promote `candidate_ref` into `helianthus-eebusreg` public state.

The action creates no trust by itself. It may request a candidate-bound attempt
only after exact validation; TLS pinning precedes WebSocket upgrade; the
connection remains untrusted until durable trust commit. There is no public
auto-trust operation, no mutation that persists before that commit, and no
stable GraphQL, MCP, Portal, Home Assistant, CLI, or network-admin mutation.

The private attempt-gate dependency may journal an opaque reservation and that
reservation's exact frozen discovered endpoint/path. It must not journal
`candidate_ref` or expose the endpoint/path through admin inspection. No
`RuntimeConfig`, static endpoint, configured root path, public API argument, or
consumer field can supply fallback authority. Restart consumes an unresolved
reservation as one synthetic failure before serving requests; it does not
restore a candidate capability or reconnect route.

## Stable Public Freeze

No stable or public value exposes candidate presence, `candidate_ref`, remote
candidate identity, attempt-journal material, endpoint material, selection
state, or pairing control. Public `Runtime`, `Snapshot`, and `PairingState`
remain unchanged. Stable eebusreg, MCP, and GraphQL remain candidate-free.
Promotion of any candidate detail requires a separate API contract, doc gate,
and consumer compatibility review.

Inbound `register=true` remains compatible as an inbound registration signal.
Passive discovery and allowlist evaluation alone never initiate a network
attempt, and public visibility never implies a selected, connected, or trusted
peer.

[docs-issue]: https://github.com/Project-Helianthus/helianthus-docs-eebus/issues/54
[eebusreg-issue]: https://github.com/Project-Helianthus/helianthus-eebusreg/issues/58
[ship-go-pr]: https://github.com/Project-Helianthus/helianthus-ship-go/pull/15
