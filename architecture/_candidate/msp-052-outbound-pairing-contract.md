---
canonical_source: "Project-Helianthus/helianthus-docs-eebus:architecture/_candidate/msp-052-outbound-pairing-contract.md"
owner_domain: "architecture"
license: "AGPL-3.0-only"
publication_status: "candidate"
claim_status: "evidence-backed"
source_class: "derived_inference"
evidence_ids: "EV-20260720-001"
hypothesis_status: "draft"
falsifier: "A reviewed implementation or conformance result shows that the companion contract can select a non-observed endpoint, progress to SPINE before durable trust, preserve volatile pairing work across restart, or create trust without exact operator validation."
stable_navigation: "false"
search: "false"
sitemap: "false"
versioned_bundle: "false"
release_bundle: "false"
---

# Candidate MSP-052 Outbound Pairing Architecture Contract

## Status And Scope

This is candidate, non-stable architecture documentation for
[docs issue 52][docs-issue] and its companion
[`helianthus-ship-go` pull request 15][ship-go-pr]. It specifies Helianthus
runtime ownership and sequencing; it is not a generic EEBUS or SHIP claim and
does not establish deployed VR940f/myVaillant behavior.

`EV-20260720-001` observed only a local inbound-registration transition. It did
not observe an outbound endpoint, TLS pin, completion of that protocol stage, durable commit, or
reconnect. Those items below are derived design requirements and remain
candidate until the companion implementation and its review gates are complete.

## Candidate Lifecycle

Passive `_ship._tcp` discovery and allowlist evaluation alone never initiate a
network attempt. A discovery callback may create `visible`; an authenticated
operator decision may advance exactly one current observation through this
state sequence:

| State | Meaning | Persistence and transition boundary |
| --- | --- | --- |
| `visible` | One passive mDNS observation is available for read-only inspection. | The observation owns its opaque `candidate_ref` and revision. |
| `selected/validated` | The operator selected that exact reference and supplied the expected certificate identity. | Validation accepts only a lowercase 40-hex value equal to the selected observation. No trust record exists. |
| `connected-untrusted` | TLS reached the selected peer and pinned its certificate identity before WebSocket upgrade. | The protocol state may reach `SmeStateApproved`; no SPINE data or durable trust is available. |
| `trusted` | The exact selected association committed durably. | Only then may the pending handshake be approved and subsequent SPINE work begin. |

`candidate_ref` is opaque and process-local. It binds one exact mDNS
observation revision, rather than a reusable endpoint or a peer identity
attribute. The active candidate queue and every candidate reference are volatile:
a restart, withdrawal, replacement, or consumption discards them. A caller
cannot reconstruct one from remembered fields.

## Endpoint And Trust Boundaries

Selection resolves the endpoint only from the bound observation and freezes one
deterministic concrete address from it for that attempt. There is no
caller-supplied or static endpoint, and no hostname, path, or address fallback.
The expected identity uses the certificate short-identifier representation. It is compared strictly:
exactly lowercase hexadecimal, exactly 40 characters, and exactly equal to the
selected observation.

The TLS peer certificate is pinned to that exact SKI before the WebSocket
upgrade. A pin mismatch aborts before a WebSocket handler runs. Passing the pin
does not create trust: the connection holds at `SmeStateApproved`, with no
SPINE progression, until the corresponding trust association commits durably.
Automatic trust and persistence before that durable commit are forbidden.

After restart, a trusted reconnect starts with fresh mDNS discovery. It may use
only the persisted identity anchors (`persisted_ski` and `persisted_ship_id`) to
recognize a newly observed matching peer; it never restores a candidate reference, queued
attempt, previous endpoint, or in-flight handshake.

## Inbound Compatibility And Ownership

Inbound `register=true` remains a local advertisement for bounded registration
and is independent from outbound selection. It does not auto-trust, select an
outbound peer, or authorize a static route. The discovery owner creates and
invalidates observations; the pairing coordinator owns exact validation and
durable commit; the connection owner enforces TLS pinning and SHIP hold; the
store owns only durable records.

The durable record begins only after the selected/validated candidate reaches
the trusted transition. Candidate references, active queue state, endpoint
material, and connection state do not enter durable storage.

[docs-issue]: https://github.com/Project-Helianthus/helianthus-docs-eebus/issues/52
[ship-go-pr]: https://github.com/Project-Helianthus/helianthus-ship-go/pull/15
