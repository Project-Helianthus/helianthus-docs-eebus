---
canonical_source: "Project-Helianthus/helianthus-docs-eebus:architecture/_candidate/msp-052-outbound-pairing-contract.md"
owner_domain: "architecture"
license: "AGPL-3.0-only"
publication_status: "candidate"
claim_status: "evidence-backed"
source_class: "derived_inference"
evidence_ids: "EV-20260720-001"
hypothesis_status: "draft"
falsifier: "A reviewed implementation or conformance result shows that OPEN_EMPTY alone can authorize an outbound first-trust attempt, candidate_ref becomes durable or stable, a restart reuses journaled endpoint authority, one terminal event charges twice, or shutdown closes the coordinator/store before transport callbacks settle."
stable_navigation: "false"
search: "false"
sitemap: "false"
versioned_bundle: "false"
release_bundle: "false"
---

# Candidate MSP-052 Outbound Pairing Architecture Contract

## Status And Scope

This is candidate, non-stable architecture documentation for
[docs issue 54][docs-issue] and its companion
[`helianthus-eebusreg` issue 58][eebusreg-issue]. It extends the candidate
selection boundary introduced with [`helianthus-ship-go` pull request
15][ship-go-pr]. It specifies Helianthus runtime ownership and sequencing; it is
not a generic EEBUS or SHIP claim and does not establish deployed
VR940f/myVaillant behavior.

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
| `connected-untrusted` | TLS reached the selected peer and pinned its certificate identity before WebSocket upgrade. | The protocol state may reach `SmeStateApproved`; no SPINE setup, semantic processing, payload delivery, or durable trust is available. Any SPINE datagram received while approval is pending closes the connection fail-closed. |
| `trusted` | The exact selected association committed durably. | Only then may the pending handshake be approved and subsequent SPINE work begin. |

`candidate_ref` is opaque and process-local. It binds one exact mDNS
observation revision, rather than a reusable endpoint or a peer identity
attribute. The active candidate queue and every candidate reference are volatile:
a restart, withdrawal, replacement, or consumption discards them. A caller
cannot reconstruct one from remembered fields.

While recovery is `UNPAIRED_LOCKED`, outbound first-trust eligibility requires
both an active bounded pairing window and the exact currently selected candidate
SKI. `OPEN_EMPTY` alone describes only the open window and empty inbound slot; it
never grants broad outbound eligibility. An unselected visible candidate, an
allowlist match, or the active window by itself cannot authorize `Prepare`,
`AuthorizeLaunch`, or a transport dial. Both gate stages recheck the exact
selected SKI and fail closed if selection or window authority has expired.

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
SPINE setup, semantic processing, or payload delivery until the corresponding
trust association commits durably. A SPINE datagram received during that
approval hold is rejected, closes the connection, and is never buffered,
decoded, delivered, exposed, or persisted. Outside the approval hold, the
generic post-handshake setup-race buffer is bounded to at most 16 raw datagrams
and 16 KiB total for that exact connection. Overflow, cancellation, or a
terminal close fails closed and discards that buffer. Automatic trust and
persistence before the durable commit are forbidden.

After exact selection, the coordinator's private attempt journal may durably
bind the exact frozen discovered endpoint and path for one reservation before
transport launch. That journal is dependency-internal control state, not a
candidate inventory or reconnect route: it never contains `candidate_ref`, and
its endpoint/path fields cannot become `RuntimeConfig`, static configuration,
root-path default, or fallback authority. Every candidate-derived primary or
fallback dial is bound to the exact currently selected candidate SKI, and
requires its own fresh reservation and launch authorization for the concrete
endpoint/path supplied by that same frozen discovery attempt.

After restart, a trusted reconnect starts with fresh mDNS discovery. It may use
only the persisted identity anchors (`persisted_ski` and `persisted_ship_id`) to
recognize a newly observed matching peer; it never restores a candidate reference, queued
attempt, previous endpoint, or in-flight handshake. An unresolved journal
reservation is settled as a synthetic failure before runtime effects are
enabled; the stored endpoint/path is removed and is never used to reconnect.

## Reservation Settlement And Shutdown

Every durable reservation has one terminal settlement owner. `AbortPrepared`,
attempt-lease expiry, a protected attempt-helper panic, and restart recovery of
an unresolved reservation each synthesize exactly one failure. That settlement
removes the reservation and charges its retry/backoff scope exactly once;
duplicate, delayed, or stale terminal paths are no-ops. A matching revocation is
the only non-failure cancellation: it clears the exact reservation and in-flight
context without a retry charge, while a non-matching revocation cannot mutate
the attempt.

Shutdown is ordered. The transport/service stops first, then the attempt gate
and callback sink settle terminal callbacks and synthetic failures, and only
then may the coordinator, admin endpoint, and store close. No callback may
outlive the coordinator/store or acquire new durable authority during shutdown.

## Verified Dependency Baseline

The companion implementation's `go.mod`, verified with workspace replacement
disabled (`GOWORK=off`), currently pins:

| Module | Candidate dependency tag |
| --- | --- |
| `github.com/Project-Helianthus/helianthus-eebus-go` | `v0.7.1-helianthus.6` |
| `github.com/Project-Helianthus/helianthus-ship-go` | `v0.6.1-helianthus.6` |
| `github.com/Project-Helianthus/helianthus-spine-go` | `v0.7.1-helianthus.1` |

These are candidate implementation dependency pins, not a stable API promotion
or a protocol-version claim.

## Inbound Compatibility And Ownership

Inbound `register=true` remains a local advertisement for bounded registration
and is independent from outbound selection. It does not auto-trust, select an
outbound peer, or authorize a static route. The discovery owner creates and
invalidates observations; the pairing coordinator owns exact validation and
durable commit; the connection owner enforces TLS pinning and SHIP hold; the
store owns only durable records.

The durable record begins only after the selected/validated candidate reaches
the trusted transition. Candidate references, active queue state, and connection
state do not enter durable storage. The private attempt journal is the sole
exception for an unresolved reservation's exact frozen endpoint/path; it is
terminally cleared and never copied into the trusted association.

[docs-issue]: https://github.com/Project-Helianthus/helianthus-docs-eebus/issues/54
[eebusreg-issue]: https://github.com/Project-Helianthus/helianthus-eebusreg/issues/58
[ship-go-pr]: https://github.com/Project-Helianthus/helianthus-ship-go/pull/15
