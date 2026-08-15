---
canonical_source: "Project-Helianthus/helianthus-docs-eebus:api/_candidate/msp-052-outbound-pairing-api.md"
owner_domain: "api"
license: "AGPL-3.0-only"
publication_status: "candidate"
claim_status: "evidence-backed"
source_class: "derived_inference"
evidence_ids: "EV-20260720-001"
hypothesis_status: "draft"
falsifier: "A reviewed API contract exposes candidate_ref, `PairingCandidateQueuer`, `CandidateRef`, a post-success marker, the opaque winner reservation, or inbound/outbound TLS-binding detail outside the experimental internal dependency boundary; treats `RequireAnyClientCert` alone as identity; accepts inbound initial TLS evidence before custom `Hub.ServeHTTP` completes WebSocket upgrade, recomputation of the certificate short identifier from the P-256 public key by `cert.SkiFromCertificate`, constant-time equality with `SubjectKeyId`, exact resolution of the service/SKI pair, or atomic selection and internal registration of the exact winning inbound connection; lets a pending outbound or competing inbound loser emit pairing, SHIP-ID, completion, or close evidence; lets a wrong-SKI, unselected, stale-generation, or overlapping callback supply or replace authority; consumes pre-confirm same-connection SHIP ID/completion before exact TLS-bound OOB confirmation has executed transient `RegisterRemoteSKI` and revalidated candidate nonce, remote fingerprint/SKI, connection generation, selected store generation, and connection liveness; lets transient RegisterRemoteSKI mutate a durable generation; permits durable commit without same-generation TLS binding, non-empty `observed_remote_ship_id`, and `ship_handshake_complete`; treats exact outbound `SmeStateComplete` as a public event or session close, cancels the live context, retains the authorized attempt, charges retry after success, or allows duplicate, stale, error, lease, or close callbacks to mutate the retired attempt or a newer generation; retains transient trust after another terminal event; or persists or publicly exposes candidate, reservation, TLS, trust, peer, endpoint, retry, or post-success detail."
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

The narrow callback-ordering correction from [docs issue
58][preconfirm-docs-issue] and [companion code issue 62][preconfirm-code-issue]
is candidate-only. It accepts their published live evidence of pre-confirm SHIP
ID/completion for one exact TLS-bound already-certificate-trusting connection;
it does not promote a new stable API or broaden the contract to other peers.

The selected-candidate inbound TLS-binding correction from [docs issue
60][inbound-docs-issue] and [companion code issue
64][inbound-code-issue] is also candidate-only. It records a private custom
dependency callback and does not add a stable declaration, field, endpoint,
event, or consumer surface.

The successful-attempt correction from [docs issue
66][success-docs-issue] and [companion code issue
75][success-code-issue] is likewise private. It changes internal callback and
attempt-journal ownership only; it adds no stable eebusreg, MCP, GraphQL, or
consumer API.

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
`selected/validated`, `connected-untrusted`, `transient-trust-active`, and
`trusted`. `transient-trust-active` is a bounded runtime fact, never a durable
pairing result. The surface does not report an approval secret, queue
implementation, persisted association contents, `observed_remote_ship_id`, or an
in-flight endpoint. A reference disappears when its observation is withdrawn,
replaced, consumed, or the process restarts.

## Experimental/Admin Mutation Boundary

Any action that selects a candidate is experimental/admin, not stable or public
API. It accepts the opaque `candidate_ref` plus an operator-validated expected
SKI that is exactly 40 lowercase hexadecimal characters. The action rejects an
unknown or stale reference and a mismatched SKI. It cannot accept a
caller-supplied or static endpoint, and it has no hostname, path, or address
fallback.

The dependency-fork names `PairingCandidateQueuer` and `CandidateRef` are
private experimental process-local dependency capabilities only. They remain
internal even when their dependency spelling is exported; that spelling does
not make either symbol a supported Helianthus API. They are not members of the
public Helianthus `eebusruntime` v1 API, stable MCP, GraphQL, Portal, or Home
Assistant surfaces. Their presence in a dependency does not promote
`candidate_ref` into `helianthus-eebusreg` public state. It also does not promote
that reference into stable eebusreg state or establish a future promotion path.
Specifically, it does not promote `candidate_ref` into stable
`helianthus-eebusreg` state.

The action creates no trust by itself. It may request a candidate-bound attempt
only after exact validation; verification of the selected outbound TLS/WebSocket
certificate-derived fingerprint precedes WebSocket upgrade. The first exact
non-error `OutgoingAttemptHandshakeStateUpdate`, accepted only after exact
attempt metadata validation, supplies the initial TLS binding for that
generation on the outbound path.

On the distinct inbound path, custom `helianthus-ship-go`
`Hub.ServeHTTP` emits `ConnectionStateReceivedPairingRequest` only after
WebSocket upgrade and the complete private identity gate. The gate recomputes
the certificate short identifier from the presented P-256 public key through
`cert.SkiFromCertificate`, constant-time compares it with `SubjectKeyId`, and
resolves the exact service/SKI pair. `RequireAnyClientCert` alone proves only
certificate presence and is not identity proof.

An opaque internal reservation keyed by the certificate-derived SKI then
atomically selects and internally registers the exact winning inbound
connection before callback emission. This connection arbitration is not
transient trust, durable trust, or public API. A pending outbound attempt and
every competing inbound attempt are losers and emit no pairing callback,
tagged SHIP-ID update, `ConnectionStateCompleted`, or close evidence.

For an already selected candidate, the private facade may accept the emitted
winner callback as the initial inbound TLS binding only when its
certificate-derived SKI and resolved service/SKI equal the selection and the
callback is bound to the exact current connection generation. Wrong-SKI,
unselected, stale-generation, loser, or overlapping evidence is rejected
without mutation or disclosure.

An exact same-connection SHIP ID/completion callback may arrive before
confirmation for an already-certificate-trusting peer, but it is only a
volatile untrusted latch: it cannot expose candidate detail, register trust,
write state, or start durable commit.

The exact TLS-bound OOB confirm checks the complete fingerprint, nonce, expiry,
connection generation, and starting store generation. It must execute
`RegisterRemoteSKI` once for that live generation as bounded transient runtime
trust, with no durable generation/store write, before it may consume a latch.
Immediately before consumption, the private coordinator revalidates candidate
nonce, remote fingerprint/SKI, connection generation, selected store generation,
and connection liveness. The tagged `RemoteSKIConnected`/`ServiceShipIDUpdate`
is not initial TLS evidence. It may supply the same-generation remote SHIP ID as
fresh post-registration evidence or as that fully revalidated latch. The private
coordinator may propose durable trust only when the same transient generation
remains TLS-bound, reports non-empty `observed_remote_ship_id`, and has
`ConnectionStateCompleted` as its terminal handshake proof. There is no public
auto-trust operation, no mutation that persists before that post-handshake
commit, and no stable GraphQL, MCP, Portal, Home Assistant, CLI, or
network-admin mutation.

An initial request that lacks this TLS binding is
`association_incomplete`; transient expiry is `candidate_expired`. Other
deterministic disconnect, cancel, close, generation, and store outcomes retain
their existing exact names. An invalid or stale post-transient admin request is
a deterministic non-mutating no-op or error: it does not unregister or revoke
the legitimate authorized candidate. In contrast, an actual candidate-lifecycle
terminal event—expiry, observed disconnect/error, exact cancellation/close,
generation conflict, shutdown, or deterministic store failure—revokes that
candidate's transient trust exactly once when it was active, discards every
pre-confirm latch, and cannot advance or rewrite the starting store generation.
Identical idempotent replay returns the cached terminal or active result without
a second register/unregister/commit effect.

Reentrant and concurrent callbacks are serialized by the private coordinator
and must revalidate the generation before each external effect. If the
disconnect transition linearizes before the SHIP-ID or completion handoff,
those stale handoffs cannot commit. A pre-confirm latch also fails closed unless
the post-registration nonce, remote fingerprint/SKI, connection generation,
selected store generation, and connection-liveness revalidation succeeds; only
then may `ConnectionStateCompleted` with all exact bindings permit durable
commit. The outcome
`trust_outcome_unknown` is reserved only after the durability-affecting recovery
publication pipeline has begun: ambiguity in `PrepareControl`, anchor staging,
finalization, clear, or `CommitControl` requires reopen. It is never used for a
pre-persistence candidate, TLS, or handshake terminal event.

The private attempt-gate dependency may journal an opaque reservation and that
reservation's exact frozen discovered endpoint/path. It must not journal
`candidate_ref` or expose the endpoint/path through admin inspection. No
`RuntimeConfig`, static endpoint, configured root path, public API argument, or
consumer field can supply fallback authority. Restart normally consumes an
unresolved reservation as one synthetic failure before serving requests; it
does not restore a candidate capability or reconnect route. The sole
known-unapplied exception is an interrupted `attempt_prepare` observed as
`exact_previous_selected_and_target_absent`. Before listener or discovery
startup, reopen performs protected-anchor compare-and-clear, preserves the
unchanged selected store, does not synthesize failure, and resumes normal
recovery classification. The denied result set is: exact target selected,
ambiguous observation, descriptor mismatch, or compare-and-clear failure.

Each denied result remains `DURABILITY_UNKNOWN` and cannot start transport
effects. After a durable clear, the recovery-only exception is the exact
release-repair `RETRY_READY` / `RETRYABLE_FAILURE` product with one usable
current-lineage durable association, nonzero `repair_sequence`, repair-receipt
ledger cardinality matches `repair_sequence`, and one terminal durable
release-retry receipt: exactly one terminal `release_retry_quarantine` /
`repaired_unpaired` receipt with nonzero operation and binding identifiers. It
still does not launch an automatic outbound attempt; only
`AdminV1.RetryTrusted` may arm one retry.

Not every persisted `RETRY_READY` / `RETRYABLE_FAILURE` record is that
exception. An ordinary first-trust commit/reset may persist one usable
association with `repair_sequence=0` and no release-retry receipt, or may
coexist with unrelated repair receipts when their ledger cardinality is
consistent. Without an exact release-repair marker, ordinary paired
classification and its exact journaled reconnect gate remain valid. A
malformed or otherwise non-exact release-repair receipt, or an inconsistent
repair-receipt ledger, remains `DURABILITY_UNKNOWN`.

That durable outbound attempt-journal reservation is distinct from the
volatile inbound winner reservation. The winner reservation is discarded on
connection termination or restart and is never journaled, persisted, exposed,
or reconstructed.

## Internal Successful-Attempt Handoff

Exact outbound `SmeStateComplete` is an internal dependency callback and the
successful attempt linearization point, not a public event and not session
close. Under the existing serialized lane for the exact peer, the private facade
revalidates the exact remote, attempt, attempt generation, connection
generation, and authorization; publishes the existing private
`ConnectionStateCompleted` handoff; then resnapshots the current control/store
generation, revalidates exact success ownership, and durably retires only that
attempt while preserving any trust generation advanced by the handoff. It then
resets that attempt's retry state. A known-unapplied retirement retries from a
fresh snapshot; an ambiguous result fails closed as `DURABILITY_UNKNOWN` and
cannot authorize launch, retry, or synthetic failure. Success does not call the
attempt cancel function or cancel the connection owner's live context.

The facade may retain one bounded volatile post-success marker per live
connection, with the collection capped by the existing live outbound connection
owner bound. Duplicate and stale callbacks cannot allocate one. The marker is
keyed only to exact internal attempt/connection ownership and is consumed by
the exact later close after disablement of the close `context.AfterFunc`.
Consumption cancels the live permit once, performs ordinary exact candidate
cleanup including one matching transient unregister when still active, and
publishes the existing disconnect handoff once without retry or durable-trust
mutation. Duplicate, stale, error, lease, and non-matching close callbacks are
non-mutating no-ops against the retired attempt and every newer generation.
Exact revocation or shutdown also consumes the marker and releases retained
permit ownership once under its existing private lifecycle contract.

The marker, callback ordering, attempt token, retry state, permit context, and
close ownership are implementation-private. They add no declaration or field to
stable eebusreg, MCP, GraphQL, `Runtime`, `Snapshot`, or `PairingState`; they are
not persisted, inspected through admin, logged, measured, traced, or accepted as
consumer input.

## Stable Public Freeze

No stable or public value exposes candidate presence, `candidate_ref`, remote
candidate identity, attempt-journal material, endpoint material, selection
state, or pairing control. Public `Runtime`, `Snapshot`, and `PairingState`
remain unchanged. Stable eebusreg, MCP, and GraphQL remain candidate-free.
Promotion of any candidate detail requires a separate API contract, doc gate,
and consumer compatibility review.

Inbound `register=true` remains compatible as an inbound registration signal.
Passive discovery and allowlist evaluation alone never initiate a network
attempt. `ConnectionStateReceivedPairingRequest` remains private dependency
evidence and cannot select a peer. The opaque winner reservation and
`candidate_ref` cannot enter `Runtime`, `Snapshot`, `PairingState`, stable
eebusreg, MCP, GraphQL, Portal, Home Assistant, CLI, logs, metrics, traces,
fixtures, or any stable/public schema. Public visibility never implies a
selected, connected, or trusted peer.

[docs-issue]: https://github.com/Project-Helianthus/helianthus-docs-eebus/issues/54
[eebusreg-issue]: https://github.com/Project-Helianthus/helianthus-eebusreg/issues/58
[preconfirm-docs-issue]: https://github.com/Project-Helianthus/helianthus-docs-eebus/issues/58
[preconfirm-code-issue]: https://github.com/Project-Helianthus/helianthus-eebusreg/issues/62
[inbound-docs-issue]: https://github.com/Project-Helianthus/helianthus-docs-eebus/issues/60
[inbound-code-issue]: https://github.com/Project-Helianthus/helianthus-eebusreg/issues/64
[success-docs-issue]: https://github.com/Project-Helianthus/helianthus-docs-eebus/issues/66
[success-code-issue]: https://github.com/Project-Helianthus/helianthus-eebusreg/issues/75
[ship-go-pr]: https://github.com/Project-Helianthus/helianthus-ship-go/pull/15
