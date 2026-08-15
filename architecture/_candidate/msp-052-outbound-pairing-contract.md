---
canonical_source: "Project-Helianthus/helianthus-docs-eebus:architecture/_candidate/msp-052-outbound-pairing-contract.md"
owner_domain: "architecture"
license: "AGPL-3.0-only"
publication_status: "candidate"
claim_status: "evidence-backed"
source_class: "derived_inference"
evidence_ids: "EV-20260720-001,EV-20260726-001"
hypothesis_status: "draft"
falsifier: "A reviewed implementation or conformance result shows that `RequireAnyClientCert` alone supplies identity or inbound TLS authority; that custom `Hub.ServeHTTP` accepts inbound initial TLS evidence before WebSocket upgrade, recomputation of the certificate short identifier from the P-256 public key by `cert.SkiFromCertificate`, constant-time equality with `SubjectKeyId`, exact resolution of the service/SKI pair, or atomic selection and internal registration of the exact winning inbound connection; that a pending outbound or competing inbound loser emits pairing, SHIP-ID, completion, or close evidence; that a wrong-SKI, unselected, stale-generation, or overlapping inbound/outbound callback supplies or replaces authority; that pre-confirm same-connection SHIP ID/completion is consumed before exact TLS-bound OOB confirmation has executed transient `RegisterRemoteSKI`; that its consumption omits revalidation of candidate nonce, remote fingerprint/SKI, connection generation, selected store generation, or connection liveness; that transient registration writes durable state; that commit omits same-generation `ship_handshake_complete` or non-empty `observed_remote_ship_id`; that exact outbound `SmeStateComplete` is treated as session close, leaves its authorized attempt durable, fails to reset retry state, cancels the live connection context, or permits a duplicate, stale, error, or lease callback to mutate the retired attempt or a newer generation; that a close after successful attempt retirement charges retry, misses exact live-context cleanup, or publishes disconnect more than once; that any other terminal path retains transient trust or changes the starting generation; that endpoint planning precedes SHIP Hub eligibility for a persisted-trusted service or actively authorized queued pairing candidate, permits a configured service address to replace or supplement observation addresses, mutates the shared mDNS observation, changes in-family order, places a hostname before a concrete address, or lets one endpoint/path authorization cover another attempt; or that candidate, reservation, TLS, trust, peer, or endpoint detail persists early or becomes public."
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

The limited pre-confirm ordering correction is documented by [docs issue
58][preconfirm-docs-issue] and [companion code issue 62][preconfirm-code-issue].
Their published live evidence permits only this inference: an exact TLS-bound,
already-certificate-trusting connection can report SHIP ID and completion before
local OOB confirmation. It does not establish a generic device or protocol rule.

The selected-candidate inbound TLS-binding correction is tracked by [docs issue
60][inbound-docs-issue] and [companion code issue
64][inbound-code-issue]. It records a custom `helianthus-ship-go` callback
boundary as candidate derived design; it does not establish generic SHIP,
SPINE, or external-device behavior.

The outbound endpoint-order correction is tracked by [docs issue
64][endpoint-docs-issue] and [companion SHIP pull request
21][endpoint-ship-pr]. The redacted runtime input is bounded to endpoint
selection and connection readiness. It establishes no generic device behavior,
supported runtime, semantic projection, or promoted API.

The successful-attempt and retry-projection correction is tracked by [docs
issue 66][success-docs-issue] and [companion code issue
75][success-code-issue]. It separates outbound attempt settlement from live
session lifetime and durable trust from transport retry control. It adds no
protocol claim, stable API, consumer surface, or private deployment evidence.

## Candidate Lifecycle

Passive `_ship._tcp` discovery and allowlist evaluation alone never initiate a
network attempt. A discovery callback may create `visible`; an authenticated
operator decision may advance exactly one current observation through this
state sequence:

| State | Meaning | Persistence and transition boundary |
| --- | --- | --- |
| `visible` | One passive mDNS observation is available for read-only inspection. | The observation owns its opaque `candidate_ref` and revision. |
| `selected/validated` | The operator selected that exact reference and supplied the expected certificate identity. | Validation accepts only a lowercase 40-hex value equal to the selected observation. No trust record exists. |
| `connected-untrusted` | The selected candidate has initial TLS evidence for the exact current generation from either the verified outbound callback or the verified inbound pairing-request callback. | Exactly one path supplies the initial TLS binding before exact TLS-bound OOB confirmation; no SPINE setup, semantic processing, or payload delivery is available. The sole ordering exception is an exact same-connection SHIP ID/completion callback from an already-certificate-trusting peer, which is volatile untrusted/no-write only; every other SPINE datagram received during that approval hold is rejected and closes the connection fail-closed. |
| `transient-trust-active` | Exactly one `RegisterRemoteSKI` effect has admitted the selected, same-generation runtime peer after exact OOB confirmation. | This is not persistence. Only after that effect executes may fresh protocol evidence or a fully revalidated pre-confirm latch supply the same-generation remote SHIP ID and completion. |
| `trusted` | The exact selected association committed durably after same-generation `ConnectionStateCompleted` with non-empty `observed_remote_ship_id`. | It is the only persistent first-trust result. |

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

SHIP Hub establishes the eligible authority before endpoint planning.

The current remote service must be either persisted-trusted and not subject to
retry-control admission, or an actively authorized queued pairing candidate.
A persisted-trusted remote in the `RETRY_READY` / `RETRYABLE_FAILURE` product
is not eligible for generic reconnect. A passive mDNS callback grants no
authority and cannot create either eligibility state.

When either eligibility state already exists, that callback may trigger or
schedule connection initiation from the current snapshot. Every resulting dial
must pass its own independent launch gate.

After eligibility, selection copies endpoint material only from the exact bound
observation into an immutable attempt-local mDNS snapshot: host, concrete
addresses, port, and path. It does not reorder or mutate the shared discovery
observation. Planning still happens before the per-attempt launch gate so that
the gate receives the actual endpoint and path proposed for that dial.
The selected mDNS observation is the sole endpoint-address input. No configured
or cached service address may replace, prepend, or supplement its addresses.

The attempt-local plan ignores nil or malformed addresses. It canonicalizes
IPv4 to 4 bytes and IPv6 to 16 bytes, treats equivalent 4-byte and 16-byte IPv4
representations as one address, and removes canonical IPv4 and IPv6 duplicates
first-seen before family ordering. It then orders every unique IPv4 address
before every unique IPv6 address while preserving first-seen order within each
family. The observed hostname is last unless it parses as an IP equal to an
already planned address, in which case that duplicate hostname endpoint is
omitted. If every concrete address fails, a distinct hostname remains the
final endpoint; if no valid concrete address was observed, it is the only
endpoint.

Every endpoint uses the observed port. Its observed path is attempted first;
after an ordinary failure, the empty path (root URL) is a second, independent
attempt for that same endpoint. The empty path does not rewrite the
observed path or mutate the frozen snapshot. There is no caller-supplied or
static endpoint, device-specific address, identity-specific route, or
configured path.

Before every dial, the outbound attempt gate revalidates the current Hub
authority and authorizes the exact endpoint and exact path from that frozen
snapshot or the explicit empty path. Authorization and permit for
the observed path do not transfer to the empty path, and authorization for one
endpoint cannot authorize the next address or the hostname. For such an
eligible generic trusted reconnect, authority comes from the current trusted
service.
On a queued first-trust attempt, the gate must also retain the exact currently
selected candidate SKI and stricter eebusreg trust/admin authorization.
Endpoint order does not weaken that first-trust boundary or let mDNS discovery
queue a candidate.

The expected identity uses the certificate short-identifier representation. It
is compared strictly: exactly lowercase hexadecimal, exactly 40 characters,
and exactly equal to the selected observation.

Outbound and inbound initial TLS evidence are distinct, generation-bound paths.
For outbound, the TLS peer certificate is pinned to the selected candidate's
exact SKI before WebSocket upgrade. A pin mismatch aborts before a WebSocket
handler runs. The first exact non-error
`OutgoingAttemptHandshakeStateUpdate` follows verification of that selected
outbound TLS/WebSocket certificate-derived fingerprint and exact attempt
metadata validation.

For inbound, the custom `helianthus-ship-go` `Hub.ServeHTTP` emits
`ConnectionStateReceivedPairingRequest` only after WebSocket upgrade and a
complete identity gate. The gate recomputes the certificate short identifier
from the presented P-256 public key through `cert.SkiFromCertificate`,
constant-time compares the recomputed bytes with `SubjectKeyId`, and resolves
the exact service/SKI pair. `RequireAnyClientCert` establishes certificate
presence only; it is not identity proof and cannot authorize this callback as
TLS evidence.

Before callback emission, an opaque internal reservation keyed by the
certificate-derived SKI selects and registers the exact winning inbound
connection atomically. This is internal connection arbitration, not transient
`RegisterRemoteSKI`, durable trust, or persistence. A pending outbound attempt
and every competing inbound attempt for that key lose and emit no pairing
callback, tagged SHIP-ID update, `ConnectionStateCompleted`, or close evidence.

For a selected candidate, the facade may use the emitted winner callback as
initial inbound TLS binding only when the resolved service/SKI equals the
selection and the callback is bound to the exact current connection generation.
There is no valid overlapping callback from a loser. Wrong-SKI,
unselected-peer, stale-generation, loser, or overlap evidence fails closed
without replacing the binding, registering trust, writing state, or exposing
candidate detail.

Passing either winning initial TLS path does not create durable trust. Exact
OOB confirmation of the TLS-bound fingerprint, nonce, expiry, connection
generation, and starting store generation may call
`RegisterRemoteSKI` once for that live generation, with no durable
generation/store write. This transient runtime trust is bounded by the candidate
and connection lifetime.

The registered peer may then progress Hello to mutual trust-ready. The candidate
must not demand SHIP Access Methods or `observed_remote_ship_id` before local
confirmation: neither can authorize transient or durable trust. For the
published pre-confirm correction, tagged `RemoteSKIConnected`/`ServiceShipIDUpdate`
and `ConnectionStateCompleted` may arrive on the exact TLS-bound connection
before confirmation, but the facade may retain them only as a volatile untrusted
latch. Exact OOB confirmation must execute `RegisterRemoteSKI` first. Only then
may the facade consume the latch after revalidating candidate nonce, remote
fingerprint/SKI, connection generation, selected store generation, and
connection liveness. The tagged update is never the initial TLS binding. No
durable proposal may start until those checks pass and it has non-empty
`observed_remote_ship_id` and `ConnectionStateCompleted` for the transiently
registered connection. Every other SPINE datagram received during the
pre-transient approval hold is rejected, closes the connection, and is never
buffered, decoded, delivered, exposed, or persisted. Outside that hold, the
generic post-handshake setup-race buffer is bounded to at most 16 raw datagrams
and 16 KiB total for that exact connection. Overflow, cancellation, or a
terminal close fails closed and discards that buffer. Automatic durable trust
and persistence before the post-handshake commit are forbidden.

An initial request without the initial TLS binding is
`association_incomplete`; transient expiry is `candidate_expired`. Other
deterministic disconnect, cancel, close, generation, and store outcomes retain
their existing exact names. Invalid or stale post-transient admin requests are
deterministic non-mutating no-ops or errors and do not revoke the legitimate
authorized candidate. Actual candidate-lifecycle terminal events—expiry,
observed disconnect/error, exact cancellation/close, generation conflict,
shutdown, or deterministic store failure—issue the matching
`UnregisterRemoteSKI` exactly once when transient registration remains active,
discard the candidate and every pre-confirm latch, and leave the selected store
generation unchanged. This cleanup remains required when an outbound attempt
has already retired successfully but its candidate has not committed durably.
After durable commit, the same disconnect handoff preserves the durable
association and performs no transient-candidate unregister. A process crash
cannot rely on a final callback; recovery starts without any transient
registration, candidate, latch, or replay record and never reconstructs one
from durable state.

Callback and event handoffs are serialized with the candidate generation. If a
disconnect transition is ordered before the SHIP-ID or completed handoff, that
handoff is stale and cannot commit. If either callback was latched before
confirmation, the exact confirmation must first execute transient registration,
then revalidate candidate nonce, remote fingerprint/SKI, connection generation,
selected store generation, and connection liveness before consumption. Only then
may `ConnectionStateCompleted` with all exact same-generation bindings permit
durable commit.
`trust_outcome_unknown` is reserved only after the durability-affecting recovery
publication pipeline has begun: ambiguity in `PrepareControl`, anchor staging,
finalization, clear, or `CommitControl` requires reopen. It is never used for a
pre-persistence candidate, TLS, or handshake terminal event.

After exact selection, the coordinator's private attempt journal may durably
bind the exact frozen discovered endpoint and path for one reservation before
transport launch. That journal is dependency-internal control state, not a
candidate inventory or reconnect route: it never contains `candidate_ref`, and
its endpoint/path fields cannot become `RuntimeConfig`, static configuration,
root-path default, or fallback authority. Every candidate-derived dial is bound
to the exact currently selected candidate SKI and requires its own fresh
reservation and launch authorization for the endpoint/path supplied by that
same frozen discovery attempt.

After restart, a generic trusted reconnect that requires no retry-control
admission starts with fresh mDNS discovery. It may use only the persisted
identity anchors (`persisted_ski` and `persisted_ship_id`) to recognize a newly
observed matching peer; it never restores a candidate reference, queued
attempt, previous endpoint, or in-flight handshake.

The `RETRY_READY` /
`RETRYABLE_FAILURE` product is recovery-only. Only an explicit identity-bound
`AdminV1.RetryTrusted` admission may authorize one attempt. Fresh mDNS discovery
cannot supply or replace that admission. An unresolved journal
reservation is settled as a synthetic failure before runtime effects are
enabled; the stored endpoint/path is removed and is never used to reconnect.
The successful-retirement durability-unknown case below is the ambiguous
exception: reopen/reconciliation owns it and may not reinterpret it as
synthetic failure. The exact known-unapplied `attempt_prepare` branch below is
the separate deterministic exception.

Reopen also owns one deterministic known-unapplied branch before listener or
discovery startup. When an interrupted `attempt_prepare` descriptor observes
its exact previous generation and control epoch still selected and its exact
target absent (`exact_previous_selected_and_target_absent`), reopen performs a
protected-anchor compare-and-clear. A durable clear preserves the unchanged
selected store, does not synthesize failure, and resumes normal recovery
classification. It grants no outbound authority: an otherwise exact
`RETRY_READY` / `RETRYABLE_FAILURE` product with one terminal durable
release-retry receipt still requires
`AdminV1.RetryTrusted` to arm one retry and does not launch an automatic
outbound attempt. The denied result set is: exact target selected, ambiguous
observation, descriptor mismatch, or compare-and-clear failure.

Each denied result remains `DURABILITY_UNKNOWN` and cannot start transport
effects.

## Successful Attempt And Session Close

Within the existing serialized lane for the exact peer, acceptance of
`SmeStateComplete` for the exact authorized outbound attempt is the successful
outbound-attempt linearization point. Before accepting it, the coordinator
revalidates the exact remote identity,
attempt token, attempt generation, connection generation, and current launch
authorization. It then publishes `ConnectionStateCompleted` first. That
synchronous handoff may re-enter the coordinator and durably advance trust or
the shared control/store generation, but its effect token queues every
duplicate, close, error, and lease callback behind the same lane.

After publication, the coordinator resnapshots the latest control/store
generation and revalidates the exact remote identity, attempt token, attempt
generation, connection generation, and success ownership. Only after that
post-publication revalidation may it durably retire the exact authorized attempt
reservation and reset that attempt's retry/backoff state. It merges those exact
changes onto the current snapshot, preserving any durable association or
generation advanced by the handoff. A retirement target captured before
publication is never written afterward. Publication, post-publication
revalidation, durable retirement, and retry reset complete in this order before
successful settlement releases the lane.

Only a proven durable retirement completes normal successful settlement. A
known-unapplied write is retried from a fresh current snapshot while exact
success ownership remains. An ambiguous retirement result enters existing
`DURABILITY_UNKNOWN`, disables new launch and retry authority for that scope,
and requires reopen/reconciliation; it does not cancel the live connection,
charge retry, or let lease/error callbacks reinterpret the attempt as failure.
Reconciliation may only confirm the exact reservation absent or retire it as
success while preserving newer trust state. It must never synthesize failure
from a reservation whose successful-retirement outcome was durability-unknown.

`SmeStateComplete` closes the attempt, not the live connection or session. The
success handler MUST NOT invoke attempt cancellation, call the permit cancel
function, or cancel the live connection context. The connection owner retains
that context while the connection remains live.

Before either normal success or fail-closed `DURABILITY_UNKNOWN` releases the
lane, the handler replaces active-attempt callback ownership with one bounded
volatile post-success marker for the exact remote identity, attempt token,
attempt generation, and connection generation. At most one marker exists per
live connection, and the marker collection cannot exceed the existing bound on
live outbound connection owners. Duplicate or stale callbacks cannot allocate a
marker. It grants no launch, retry, trust, candidate, endpoint, persistence, or
public authority and is discarded on restart. It exists only to bridge
successful attempt linearization to exact later connection cleanup.

The matching later close is serialized in the same per-SKI lane. After SHIP has
disabled its close `context.AfterFunc`, that close consumes the exact marker and
cancels the live permit context once. It then performs the ordinary exact
MSP-04B candidate-terminal handoff: a pending or transient candidate is cleared,
every latch is discarded, and an active transient `RegisterRemoteSKI` is matched
by one `UnregisterRemoteSKI`. It then publishes disconnect once. If the candidate
already committed durably, no transient unregister occurs and the durable
association remains trusted. Marker consumption itself neither recreates nor
fails the retired attempt, increments retry/backoff, nor mutates durable trust.
A duplicate close or a close for any other attempt or connection generation is
a no-op.

Exact revocation or shutdown consumes the same marker under the lane and
cancels the retained live context once. Revocation then follows its separate
durable trust-withdrawal contract; shutdown performs no retry settlement. Both
release the marker and retained permit ownership, and a later close is a no-op
against that consumed marker.

Success and terminal races are first-linearized-event wins. If exact
`SmeStateComplete` wins before lease expiry, the durable reservation is absent,
retry state is reset, the live context remains uncancelled, and every duplicate,
delayed, stale, error, or lease callback is a no-op against that attempt. If
lease expiry or another authorized failure wins first, it settles failure once
under the existing rule and later completion is stale. Neither ordering may
mutate a newer attempt generation.

## Successful Attempt Falsifiers

| Falsifier | Required result | Contract is falsified if |
| --- | --- | --- |
| `A66-SUCCESS-BEFORE-LEASE` | Exact `SmeStateComplete` publishes `ConnectionStateCompleted`, then durably removes the exact reservation and resets retry state while the live context remains uncancelled. Advancing beyond the retired lease has no effect. | The attempt remains authorized or durable, retry is charged, the live context is cancelled, ordering differs, or the old lease mutates any state. |
| `A66-LEASE-BEFORE-SUCCESS` | Exact lease expiry settles failure once; later `SmeStateComplete` and duplicate error/lease callbacks are stale no-ops. | Completion resurrects or succeeds the expired attempt, a terminal effect repeats, or a newer generation changes. |
| `A66-HANDOFF-GENERATION` | A synchronous `ConnectionStateCompleted` handoff advances durable trust/control generation; post-publication resnapshot retires only the exact successful reservation on that latest generation and preserves the trust commit. | Retirement uses a pre-publication snapshot, conflicts with or overwrites the trust commit, leaves the exact attempt authorized, or charges retry. |
| `A66-RETIREMENT-DURABILITY` | Known-unapplied retirement is retried from a fresh snapshot; ambiguous retirement enters `DURABILITY_UNKNOWN`, blocks launch/retry, preserves the live context and newer trust, and reconciles the exact attempt only as success. | An unproven retirement reports normal settlement, enables another launch, charges failure, cancels the live context, or overwrites newer trust. |
| `A66-CLOSE-AFTER-SUCCESS` | Exact later close consumes one bounded post-success marker after the SHIP close `context.AfterFunc` is disabled, cancels the live permit once, performs exact candidate-terminal cleanup, and publishes one disconnect without retry or durable-trust mutation. | Success closes the session, close is lost, cleanup or disconnect repeats, retry increments, or the durable association degrades. |
| `A66-PRECONF-CLOSE-AFTER-SUCCESS` | Pre-confirm completion retires the attempt; if exact OOB later activates transient trust but close wins before durable commit, marker consumption clears the candidate/latches and invokes one matching `UnregisterRemoteSKI`. | Transient trust or a candidate latch survives close, unregister repeats, the retired attempt is failed, or durable state changes. |
| `A66-STALE-GENERATION` | Duplicate, stale, error, lease, and close callbacks for the retired attempt cannot mutate a newer attempt or connection generation. | Any stale callback cancels, retires, resets, charges, publishes for, or otherwise changes a newer generation. |

## Reservation Settlement And Shutdown

Every durable reservation has one terminal settlement owner. Exact
`SmeStateComplete` owns successful settlement under the ordering above.
`AbortPrepared`, attempt-lease expiry, a protected attempt-helper panic, and
restart recovery of an unresolved reservation each synthesize exactly one
failure when they linearize first. Failure settlement removes the reservation
and charges its retry/backoff scope exactly once; duplicate, delayed, stale, or
post-success terminal paths are no-ops. A matching revocation is the only
non-failure cancellation: it clears the exact reservation and in-flight context
without a retry charge, while a non-matching revocation cannot mutate the
attempt. Successful settlement is neither failure nor cancellation and does not
cancel the live connection context.

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
outbound peer, or authorize a static route. An inbound
`ConnectionStateReceivedPairingRequest` cannot select a candidate; it may bind
TLS only for the exact already selected candidate and current connection
generation after the custom `Hub.ServeHTTP` identity and winner-reservation
preconditions above. This volatile inbound winner reservation is distinct from
the durable outbound attempt-journal reservation below. It never becomes
candidate state, durable state, or a public identifier. The discovery owner
creates and invalidates observations; the pairing coordinator owns exact
validation and durable commit; the connection owner enforces TLS pinning and
SHIP hold; the store owns only durable records.

The durable record begins only after the selected/validated candidate reaches
the post-handshake trusted transition. Candidate references, active queue state,
transient-registration state, and connection state do not enter durable
storage. The private attempt journal is the sole exception for an unresolved
reservation's exact frozen endpoint/path; it is terminally cleared and never
copied into the trusted association.

[docs-issue]: https://github.com/Project-Helianthus/helianthus-docs-eebus/issues/54
[eebusreg-issue]: https://github.com/Project-Helianthus/helianthus-eebusreg/issues/58
[preconfirm-docs-issue]: https://github.com/Project-Helianthus/helianthus-docs-eebus/issues/58
[preconfirm-code-issue]: https://github.com/Project-Helianthus/helianthus-eebusreg/issues/62
[inbound-docs-issue]: https://github.com/Project-Helianthus/helianthus-docs-eebus/issues/60
[inbound-code-issue]: https://github.com/Project-Helianthus/helianthus-eebusreg/issues/64
[endpoint-docs-issue]: https://github.com/Project-Helianthus/helianthus-docs-eebus/issues/64
[endpoint-ship-pr]: https://github.com/Project-Helianthus/helianthus-ship-go/pull/21
[success-docs-issue]: https://github.com/Project-Helianthus/helianthus-docs-eebus/issues/66
[success-code-issue]: https://github.com/Project-Helianthus/helianthus-eebusreg/issues/75
[ship-go-pr]: https://github.com/Project-Helianthus/helianthus-ship-go/pull/15
