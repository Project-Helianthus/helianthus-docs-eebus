---
canonical_source: "Project-Helianthus/helianthus-docs-eebus:architecture/_candidate/msp-04b-first-trust-admin-local.md"
owner_domain: "architecture"
license: "AGPL-3.0-only"
publication_status: "candidate"
claim_status: "evidence-backed"
source_class: "derived_inference"
evidence_ids: "EV-20260711-001,EV-20260720-001"
hypothesis_status: "draft"
falsifier: "An accepted conformance result shows that `RequireAnyClientCert` alone supplies identity or inbound TLS authority; that custom `Hub.ServeHTTP` accepts inbound initial TLS evidence before WebSocket upgrade, recomputation of the certificate short identifier from the P-256 public key by `cert.SkiFromCertificate`, constant-time equality with `SubjectKeyId`, exact resolution of the service/SKI pair, or atomic selection and internal registration of the exact winning inbound connection; that a pending outbound or competing inbound loser emits pairing, SHIP-ID, completion, or close evidence; that a wrong-SKI, unselected, stale-generation, or overlapping inbound/outbound callback supplies or replaces authority; that pre-confirm same-connection SHIP ID/completion is consumed before exact TLS-bound OOB confirmation has executed transient `RegisterRemoteSKI`; that its consumption omits revalidation of candidate nonce, remote fingerprint/SKI, connection generation, selected store generation, or connection liveness; that transient registration writes a generation; that durable commit omits same-generation `ship_handshake_complete` and non-empty `observed_remote_ship_id`; that a terminal path leaves transient trust registered or changes the starting store generation; or that any candidate, reservation, TLS, trust, or peer detail persists early or leaks into a public surface."
stable_navigation: "false"
search: "false"
sitemap: "false"
versioned_bundle: "false"
release_bundle: "false"
---

# Candidate MSP-04B First-Trust And Local Admin Contract

## Status And Authority

This document remains candidate and non-stable architecture documentation for
MSP-04B. The implementation merged in `helianthus-eebusreg` at the
[implementation commit][implementation-commit]. Recording that merge is status
context only: this page remains excluded from stable publication and does not
itself promote support. It records project ownership and security decisions,
not protocol observations or deployed behavior.

The design provenance is the [MSP-04B documentation issue][docs-issue], the
[companion code issue][code-issue], the candidate
[MSP-04A persistent-store contract][store-contract], and the supported eeBUS
architecture ownership boundary at `architecture/README.md`. No live device,
private identifier, local-network observation, or device-specific evidence is
needed to state this candidate contract.

The narrowly scoped ordering correction in [docs issue 58][preconfirm-docs-issue]
and [companion code issue 62][preconfirm-code-issue] is constrained to their
published live evidence: an exact TLS-bound connection may report SHIP ID and
completion before local OOB confirmation when the peer has already accepted the
local certificate. This page records the required fail-closed handling of that
ordering; it makes no broader device or protocol claim.

The selected-candidate inbound TLS-binding correction in [docs issue
60][inbound-docs-issue] and [companion code issue
64][inbound-code-issue] is candidate derived design. It records the custom
`helianthus-ship-go` callback boundary used by Helianthus; it does not attribute
that callback or its ordering to generic SHIP, SPINE, or an external device.

Stable API, navigation, search, sitemap, versioned-bundle, and release-bundle
outputs intentionally omit this candidate. Publication of this page does not
move any term below into the supported surface. A later implementation link or
support claim requires merged code, its required tests, and a separately
reviewed publication transition.

## Normative Language

`MUST`, `MUST NOT`, `SHOULD`, and `MAY` describe implementation acceptance for
MSP-04B. State names, command names, fields, and outcomes are internal
conformance vocabulary. They do not add exported Go declarations, create a
public admin protocol, or promise a stable wire format.

## Ownership Boundary

| Component | Owns | Must not own |
| --- | --- | --- |
| `internal/eebusstore` | policy-free validation, opaque remote associations, atomic generations, and deterministic commit outcomes. | It has no candidate selection, OOB decision, socket, pairing policy, or runtime transition. |
| `private trust coordinator` | The pairing-window FSM, one candidate slot, OOB comparison, idempotency, expiry, connection/store-generation binding, and commit ordering. | It does not implement filesystem publication, accept unauthenticated commands, or export candidate state. |
| `AF_UNIX admin transport` | Bounded framing, same-UID peer authentication, command delivery, and owner-only path/socket lifecycle. | It makes no trust, candidate, OOB, store, or runtime decision. |
| `facade/service adapter` | Translation between eeBUS callbacks and private coordinator events, plus one bounded transient registration before the later durably confirmed association. | It does not auto-accept, bypass the coordinator, persist transient trust, publish before durability, or preserve a race loser. |
| `public Runtime/Snapshot/PairingState` | The existing read-only supported observation surface. | MSP-04B adds no public mutation operation or candidate detail. |

The boundaries are directional. The coordinator asks `internal/eebusstore` to
validate and atomically publish a complete opaque association; the store
returns one deterministic outcome and never learns why the caller requested
it. The admin transport authenticates and frames a request before handing a
typed command to the coordinator; it never evaluates the fingerprint or
chooses a candidate. The facade translates callback shape and effects only a
coordinator decision.

## Candidate And Confirmation Binding

The coordinator has exactly one volatile candidate slot. Only a pairing
callback backed by an active transport connection may create it. Configuration,
an allowlist match, an mDNS observation, and a locally opened pairing window
cannot create a candidate. An eligible pairing callback captures the pairing
identity and all immediately available bindings. The candidate may remain
`association_incomplete` until its TLS binding is available, but it still
occupies the only slot. Once transient trust is active, the later missing-SHIP-
evidence state is `handshake_incomplete`, not a reason to write the store.

| Binding | Constraint |
| --- | --- |
| `remote_ski` | Opaque bytes from the pairing callback, bound to the exact connection generation and never rendered except as `fingerprint_v1` in the privileged local response. |
| `tls_binding` | The initial binding supplied by exactly one verified winning path for the selected candidate and current `connection_generation`: the first exact non-error outbound `OutgoingAttemptHandshakeStateUpdate` after certificate-derived fingerprint and attempt-metadata validation, or inbound `ConnectionStateReceivedPairingRequest` after the custom `Hub.ServeHTTP` has completed WebSocket upgrade, recomputed the certificate short identifier from the presented P-256 public key through `cert.SkiFromCertificate`, matched the recomputed bytes to `SubjectKeyId` in constant time, resolved the exact service/SKI pair, and atomically reserved and internally registered the exact inbound winner. It is required before any transient trust registration. |
| `observed_remote_ship_id` | A non-empty opaque value supplied by tagged `RemoteSKIConnected`/`ServiceShipIDUpdate` at the Access-Methods stage for the same `remote_ski` and `connection_generation`. It is not initial TLS evidence. Before OOB confirmation it may be latched only as volatile untrusted evidence for an already-certificate-trusting peer; it cannot cause registration, commit, persistence, or public observation. |
| `ship_handshake_complete` | `ConnectionStateCompleted`, the facade's same-generation terminal proof of completed protocol setup. Before OOB confirmation it may be latched only with the same exact bindings as volatile untrusted evidence; it is not inferred from TLS, registration, or a callback from another connection. |
| `fingerprint_v1` | The normalized, full 40-character lowercase hexadecimal encoding of the bytes in `remote_ski`, with no separators, prefix, surrounding whitespace, truncation, or alternate encoding. |
| `candidate_nonce` | A fresh random candidate nonce generated from the operating-system cryptographic random source for this candidate only. |
| `idempotency_key` | A bounded opaque request key scoped to this candidate; an active entry moves to the bounded terminal-result cache after a terminal result. |
| `connection_generation` | The facade-assigned generation for the exact live peer connection that supplied the candidate. |
| `expires_at` | A monotonic expiry deadline bounded by the pairing-window deadline. Wall-clock changes cannot extend it. |
| `starting_store_generation` | The exact selected MSP-04A generation observed when the candidate slot was created. |

For this contract, `fingerprint_v1` is the normalized, full 40-character
lowercase hexadecimal encoding of the bytes in `remote_ski` described above.
Its parsing is strict: invalid length, uppercase, non-hexadecimal
input, separators, or whitespace is rejected before comparison. A valid input
is decoded and checked with exact constant-time comparison over the complete
association-key bytes. No prefix, suffix, case-folded, shortened, or display-form match is
accepted. Comparison behavior and externally visible outcomes MUST NOT reveal
which byte differed.

Outbound and inbound initial TLS evidence are distinct paths. The first exact
non-error `OutgoingAttemptHandshakeStateUpdate` is downstream of verification
of the selected outbound TLS/WebSocket certificate-derived fingerprint and
exact attempt metadata validation. For a selected candidate, the custom
`Hub.ServeHTTP` may instead emit
`ConnectionStateReceivedPairingRequest` only after WebSocket upgrade and the
complete inbound identity gate. That gate requires a presented P-256 client
certificate, recomputation of its short identifier from the public key by
`cert.SkiFromCertificate`, constant-time equality of the recomputed bytes and
`SubjectKeyId`, and exact resolution of the service/SKI pair.
`RequireAnyClientCert` proves only certificate presence; by itself it is not
identity proof and cannot supply TLS binding or trust authority.

Before emitting the callback, an opaque internal reservation keyed by the
certificate-derived SKI selects and registers the exact winning inbound
connection atomically. This registration is connection arbitration inside
`helianthus-ship-go`, not `RegisterRemoteSKI`, trust, or persistence. A pending
outbound attempt and every competing inbound attempt for the same key are
losers. They emit no pairing callback, tagged SHIP-ID update,
`ConnectionStateCompleted`, or close evidence to the facade.

The facade may accept that callback as the initial inbound TLS binding only
when its certificate-derived SKI and resolved service/SKI equal the selected
candidate and it is tagged with the exact current connection generation.

The exact reservation winner supplies the candidate's initial TLS binding.
There is no valid overlapping duplicate from a losing inbound or outbound
attempt. Any loser evidence, wrong-SKI, unselected-peer, stale-generation, or
overlapping callback is rejected without replacing the binding, registering
trust, changing the store, or exposing candidate detail.

Published live evidence for the pre-confirm correction issues shows one
narrower ordering: an already-certificate-trusting peer may send tagged
`RemoteSKIConnected`/`ServiceShipIDUpdate` and `ConnectionStateCompleted` on
that same TLS-bound connection while the candidate is still
`CANDIDATE_PENDING`. These callbacks are neither initial TLS evidence nor local
approval. The facade may latch them only as volatile untrusted evidence bound
to the exact `remote_ski`, TLS binding, and `connection_generation`; it MUST
NOT use them to register, commit, persist, publish, or retain authority across
restart.

Exact OOB confirmation remains the first local trust decision. It must cause
the one transient `RegisterRemoteSKI` effect to execute first. Only after that
effect has succeeded may the coordinator consume a pre-confirm latch, and it
MUST then revalidate the candidate nonce, remote fingerprint/SKI, connection
generation, selected store generation, and connection liveness. Empty,
stale-generation, differently keyed, ambiguous, expired, disconnected, or
otherwise unbound evidence is rejected and cannot complete anything. The
coordinator and facade MUST NOT invent, default, derive, cache across a restart,
or copy either value from another connection.

A confirm needs exact `fingerprint_v1`, nonce, expiry, connection generation,
starting store generation, and TLS binding, but it does **not** need
`observed_remote_ship_id` or `ship_handshake_complete`. On that exact
confirmation it authorizes one bounded transient runtime registration and
performs no store write; the selected store generation remains unchanged. A
confirm before the TLS binding is present returns `association_incomplete` and
makes no runtime or durable mutation. A replay of the same complete
confirmation returns the same transient result and cannot register twice.

Only after the registered live connection has a non-empty matching
`observed_remote_ship_id` and same-generation `ConnectionStateCompleted`—from
post-registration callbacks or from a revalidated pre-confirm latch—may the
coordinator propose an association. That later proposal persists `remote_ski`
and `observed_remote_ship_id` together in one atomic generation. Neither value
is persisted during transient trust.

The nonce prevents an approval prepared for an earlier candidate from naming a
new slot. The connection generation prevents a reconnect from inheriting an
approval. The starting store generation prevents a candidate from committing
over a store state it did not observe. The idempotency key prevents one accepted
request from producing more than one logical commit. Active and terminal replay
behavior is defined under the local admin transport below; reuse with different
bindings always returns `idempotency_conflict` without mutation.

This mechanism proves explicit confirmation of that exact candidate under
`fingerprint_v1`. It does not prove that a human used an independent OOB
channel, that displayed data came from an independent source, or that the peer
certificate has any property beyond the separately validated association. If
certificate-leaf SHA-256 is desired later, that requires a redesigned
confirmation contract, new binding and normalization rules, and a separate
review. It MUST NOT be substituted silently for
`fingerprint_v1`.

## Private Admin State Vocabulary

| State | Meaning | Persistence boundary |
| --- | --- | --- |
| `TRANSIENT_TRUSTED` | Exact OOB confirmation has authorized one same-generation `RegisterRemoteSKI` effect after the initial TLS binding, while the candidate awaits fresh post-registration or fully revalidated latched remote SHIP ID and `ConnectionStateCompleted` evidence. | Volatile only; it is never a durable association and is revoked exactly once only by a candidate-lifecycle terminal event. |

## Coordinator State Machine

The private coordinator has exactly these externally testable states. All
events are serialized through one linearization point, and the first terminal
rule in the current state wins.

| State | Meaning | Allowed next state |
| --- | --- | --- |
| `DISABLED` | Mutation is unavailable because startup has not established a usable store, or a prior outcome requires reopen. | `PAIRING_CLOSED` only after a successful reopen and reload. |
| `PAIRING_CLOSED` | Default state; no first-trust candidate may be admitted. | `OPEN_EMPTY` when an authenticated admin command opens a bounded window. |
| `OPEN_EMPTY` | A bounded pairing window is open and the candidate slot is empty. | `CANDIDATE_PENDING` for the first linearized eligible peer; otherwise `PAIRING_CLOSED` on close or window expiry. |
| `CANDIDATE_PENDING` | Exactly one eligible RAM candidate owns the slot before OOB confirmation has authorized a transient registration. Exact same-connection SHIP ID/completion may be latched only as volatile untrusted evidence. | Enter `TRANSIENT_TRUSTED` only after exact OOB confirmation and same-generation initial TLS binding, enter `OPEN_EMPTY` after candidate cancel/expiry while the window remains open, or enter `PAIRING_CLOSED` when the window closes/expires. |
| `TRANSIENT_TRUSTED` | The exact candidate owns one volatile transient registration and awaits same-generation protocol evidence. | Remain transient on incomplete evidence; enter `COMMITTING` only after transient registration has executed and fresh or revalidated latched non-empty matching `observed_remote_ship_id` plus `ship_handshake_complete` from `ConnectionStateCompleted` pass all exact bindings; enter `OPEN_EMPTY` after candidate cancel/expiry while the window remains open, or enter `PAIRING_CLOSED` when the window closes/expires. |
| `COMMITTING` | The window is already closed and one complete post-handshake association is being validated and committed. | `PAIRING_CLOSED` after a known terminal result, or `DISABLED` when reopen is required. |

Startup enters `DISABLED`. A successful store open reloads trust from durable
remote associations and enters `PAIRING_CLOSED`; it never restores an open
window or candidate. The window has a monotonic deadline and an implementation
maximum. Opening a window while already open is idempotent only when the full
request and idempotency key match; otherwise it returns a stable conflict.

First linearized eligible event wins the single candidate slot. A competing
peer receives stable `candidate_busy` and is cancelled by the facade. Scheduler
order, map order, callback batching, and transport read boundaries cannot
produce two winners. Ineligible, already trusted, malformed, or stale-generation
events do not occupy the slot.

Wrong fingerprint, stale nonce, stale connection generation, stale store
generation, or idempotency conflict is a deterministic non-mutating no-op or
error. It leaves the store unchanged and the candidate intact; it does not revoke
the legitimate authorized candidate or its active transient registration. In particular, a
stale admin request is not an exact candidate-lifecycle generation conflict.
Actual terminal events—candidate expiry (`candidate_expired`), observed
disconnect/error, exact cancellation/close, exact generation conflict,
shutdown, or deterministic store failure—unregister the exact transient remote
once when present, discard every pre-confirm latch, clear the candidate, and
retain the starting store generation. Candidate expiry returns to `OPEN_EMPTY`
only while the pairing window itself remains valid; window close or expiry
enters `PAIRING_CLOSED`. Cancel or expiry clears the candidate.

Missing `observed_remote_ship_id` or absent `ConnectionStateCompleted` follows
the same no-write rule but remains `handshake_incomplete` while the exact
transient registration is live; the state is candidate pending with no store
write, and it is not a fingerprint failure. A matching tagged
`RemoteSKIConnected`/`ServiceShipIDUpdate` and `ConnectionStateCompleted` may
advance the candidate only before expiry and only in that connection generation.
Before transient registration, a matching pair may be latched but is still
untrusted and unconsumable; it does not change this rule.

A valid confirmation is linearized before any filesystem mutation and before
one transient-registration effect is queued. The registration effect runs
outside the coordinator lock, rechecks liveness and the exact generation, and
may synchronously re-enter through a callback. The coordinator serializes that
re-entry by effect token; no callback can register twice, mutate an obsolete
candidate, or start a Commit.

The coordinator MUST Close the pairing window before beginning one commit only
after the durable prerequisites are present, enter `COMMITTING`, and prevent
another candidate or confirmation from
being admitted. This ordering makes confirm-versus-cancel,
transient-registration-versus-disconnect, and completion-versus-expiry races
deterministic: whichever event linearizes first determines the one terminal
result. A losing callback cannot reopen, replace, register, unregister a newer
generation, or commit a cleared candidate.

## Waiting Permission And Commit Ordering

In the pinned eeBUS library, `UserIsAbleToApproveOrCancelPairingRequests`
controls the global `AllowWaitingForTrust` permission. That permission allows a
pending protocol exchange to wait; it does not approve a peer, select a candidate,
validate OOB input, or persist trust. It is a transport-liveness control, not
the security decision.

After complete exact confirmation linearizes, the coordinator admits no new
candidate but keeps the winning candidate bounded while it awaits
same-generation protocol evidence. `auto-accept` remains `false`, every competing
peer is cancelled, and a new callback is refused even if the library's global
waiting permission has not yet changed. Candidate admission therefore does not
depend on that global flag.

After transient registration has executed and same-generation
`observed_remote_ship_id` and `ConnectionStateCompleted` are both available as
fresh evidence or a fully revalidated latch, the coordinator logically closes
the pairing window before Commit and admits no new candidate. This late closure
does not retract already active transient trust; its terminal cleanup rules
still apply.

The facade may call `RegisterRemoteSKI` once only after the exact TLS-bound
confirmation has passed. The call creates transient runtime trust, not durable
trust: the selected store generation is still unchanged. It must execute before
any pre-confirm SHIP ID/completion latch is consumed. The former rule that
`RegisterRemoteSKI` only after `commit_durable` actually approves the winner is
rejected by this contract; it would make required protocol evidence unreachable.
The exact stale assertion is: Only `RegisterRemoteSKI` after `commit_durable`
actually approves. It is a falsifier. The global flag itself never approves a
peer.

The adapter may keep `AllowWaitingForTrust` `true` only through the bounded
`COMMITTING` interval for the winner and its preceding bounded transient
interval. A nonzero implementation constant defines the monotonic transient
and commit-wait bounds. The flag is set
`false` before or atomically with the terminal effect. A transient-phase
terminal candidate lifecycle event uses its existing exact deterministic
outcome: an initial missing TLS binding is `association_incomplete`, and
transient expiry is `candidate_expired`. It unregisters transient trust when
present, clears the candidate, performs no durable mutation, and retains the
starting store generation. An invalid or stale post-transient admin request
instead remains a non-mutating no-op or error and does not revoke the legitimate
authorized candidate. Neither class reports the trust outcome unknown.

`trust_outcome_unknown` and mandatory reopen are reserved for ambiguity after
the durability-affecting recovery publication pipeline has begun, including
ambiguous `PrepareControl`, anchor staging, finalization, clear, or
`CommitControl` outcomes. It is never used for a pre-persistence candidate,
TLS, or handshake terminal event. That path performs no additional
`RegisterRemoteSKI` effect, performs no `RegisterRemoteSKI` after the unknown
result, and unregisters the transient registration before recovery; this is the
only reopen required path here. Known store outcomes follow the mapping below.
Deterministic tests MUST record the ordered events for success, every failure
outcome, a blocked Commit, a racing peer while the global flag remains true,
synchronous callback reentry, and terminal cleanup.

## SHIP Pairing Registration Advertisement

The SHIP DNS-SD `register` value is a discovery signal, not a trust decision.
`PAIRING_CLOSED` advertises `register=false`, while `OPEN_EMPTY` advertises
`register=true`. `CANDIDATE_PENDING` and `TRANSIENT_TRUSTED` keep
`register=true` within the original bounded window so the selected protocol
exchange remains discoverable; the single-candidate rule still rejects every
competing peer deterministically.

Opening the window has one network-visible effect: the local advertisement
changes to `register=true`. It does not queue or report a remote, launch a dial,
fabricate a service or session observation, or select a candidate. Those states
require their corresponding discovery, connection, and pairing callbacks.

After exact confirmation, `TRANSIENT_TRUSTED` and then `COMMITTING` may retain
`register=true` only during the bounded handshake and commit-wait intervals.
Close, expiry, cancellation, or any terminal commit effect withdraws or
replaces the announcement with `register=false`. `DISABLED` also advertises
`register=false` and requires a successful reopen before another window.

This registration signal is independent from handshake acceptance:
`auto-accept` remains `false`. It does not approve the selected peer and does
not persist trust. The exact OOB-confirmed candidate may reach
`RegisterRemoteSKI` only as bounded transient trust; durable association follows
only after same-generation `ship_handshake_complete` from
`ConnectionStateCompleted`. A failed registration update is an
explicit degraded outcome and cannot be represented as an empty successful
window.

## Store Commit Outcome Mapping

The coordinator passes one complete proposed generation to
`internal/eebusstore`; it does not edit a live association in place. The
starting generation must still match immediately before Commit. Store
validation and provider checks remain store-owned and precede filesystem
publication.

| Store result | Coordinator result | Required action |
| --- | --- | --- |
| `commit_durable` | `trusted` | Clear the candidate, retain the closed window, and retain the already registered live connection as the durable association for this exact generation. |
| `commit_not_published` | `failed_closed_unchanged` | Unregister transient trust, treat the store as unchanged, clear the candidate, keep pairing closed, and require a new window/candidate for retry. |
| `validation/provider failure` | `failed_closed_unchanged` | Unregister transient trust; map deterministic validation, key-provider, or key-material outcomes without mutation; clear the candidate and keep pairing closed. |
| `commit_applied_maintenance_failed` | `applied_reopen_required` | Unregister transient trust, disable mutation, close/cancel live pairing work, and reopen before durable associations may reload trust. |
| `commit_durability_unknown` | `trust_outcome_unknown` | Unregister transient trust, do not report success or failure-as-unapplied, disable mutation, and require reopen to determine the selected generation. |

Only `commit_durable` may make the current in-process result durably trusted.
The stale claim "trusted and invoke `RegisterRemoteSKI`" is an exact falsifier,
not permitted behavior. Known-unapplied failures never retry automatically.
`commit_applied_maintenance_failed` means the association was applied, but
maintenance failed and reopen is required. A durability-unknown result means
the trust outcome is unknown until Open reselects a generation.
For the last two outcomes, mutation is disabled, live pairing work is
cancelled, and reopen is required.

After reopen, durable remote association alone reloads trust. Neither an old
volatile candidate nor a previous process result can add or remove it. A
reloaded association may then be applied through the normal facade startup
path; it is not evidence that the interrupted process observed
`commit_durable`.

## Local Admin Transport

The admin endpoint is a separate local transport, not part of the store and not
part of the public Go API. Default transport is AF_UNIX only. There is no
loopback fallback, TCP listener, network bind, environment-triggered network
mode, or automatic fallback when local socket setup fails. An unsupported
platform or unavailable peer-credential primitive disables admin mutation.

The proposed socket resides outside `StateRoot` in an owner-controlled runtime
directory because the MSP-04A store rejects unknown entries and socket objects.
The admin directory and socket path are configuration owned by the service
bootstrap, while the store continues to enumerate only its fixed layout. No
socket filename contains a local or remote identity, fingerprint, nonce, or
stable peer-derived value.

### Authentication And Lifecycle

Before request parsing, each accepted connection MUST pass same-UID peer
authentication using the platform's kernel-reported peer credentials. The
effective runtime UID is the only accepted UID. Missing, ambiguous, malformed,
or changed credentials and every wrong UID are rejected before a frame body is
read or a coordinator command is constructed. Filesystem mode bits alone do
not authenticate a connected peer.

The owning service creates or safely opens an owner-only admin directory,
rejects symlink components, pins descriptor identity, and performs
descriptor-relative no-follow checks around bind and cleanup. An existing path
is never blindly removed. A symlink, non-socket object, wrong owner, active
listener, pathname-to-descriptor substitution, or ambiguous stale socket fails
closed. A stale socket may be removed only after same-owner/type/identity checks
and a failed connect prove it has no listener. Post-bind verification must show
the expected owner-only socket at the pinned location. Shutdown removes only
the exact socket object created by this process; a substituted path is left
untouched and reported as a lifecycle failure.

### Bounded Framing And Commands

The transport uses a versioned, length-delimited request envelope with one
request per frame. A compile-time nonzero `max_admin_frame_bytes` bounds both
declared length and allocation before body read. The implementation also bounds
field lengths, command count per connection, concurrent accepted connections,
read/write deadlines, and reply bytes. Partial prefix/body, extra bytes,
unknown version or command, duplicate/unknown fields, malformed encoding,
oversized frame, and deadline expiry produce stable transport errors and no
coordinator event.

The private command inventory is limited to opening or closing a pairing
window, confirming or cancelling the current candidate by its opaque bindings,
reading redacted coordinator status, and the privileged candidate read defined
below. The transport conveys commands but makes no trust decision. It does not
derive `fingerprint_v1`, select a candidate, inspect store records, extend
expiry, change a connection generation, or translate a transport error into
acceptance.

### Privileged Candidate Read

OOB comparison is enabled by a privileged candidate-read command over the same
same-UID authenticated AF_UNIX connection. When one unexpired candidate is
pending, its sensitive local-only response may contain exactly
`fingerprint_v1`, `candidate_nonce`, `expires_at`, `connection_generation`,
`starting_store_generation`, and a boolean association-complete indicator. The
response does not return `observed_remote_ship_id`, raw association bytes, or
any local identity.

This response exists only for immediate local OOB comparison. It MUST NOT be
logged, metriced, traced, captured, persisted, or shared by the service, admin
client, tests, or diagnostics. Errors use stable categories without echoing
sensitive fields. The response is cleared from service-owned buffers after the
reply and becomes stale when any returned binding changes or expires. Public
`Runtime`, MCP, GraphQL, Portal, and Home Assistant surfaces remain
candidate-free.

Ordinary status remains redacted and does not return candidate bindings. The
privileged read is the sole private response exception; it is not a public API,
shareable artifact, or stable administration contract.

### Idempotency And Replay

Every mutating request carries a bounded idempotency key. While a candidate is
active, its key and full request binding are volatile. At a terminal result,
including cancellation or expiry, the coordinator moves the binding and result
into a bounded volatile terminal-result cache. Both entry count and retention
use implementation constants; each entry has a bounded replay TTL and is kept
never beyond the current process lifetime.

During that TTL, identical replay returns the cached stable result and cannot
produce a second commit. Conflicting key reuse returns
`idempotency_conflict`. Replay for a cancelled or expired candidate returns its
cached no-write result and cannot resurrect the candidate, reopen the window,
or recreate a previous generation binding. After cache expiry, the same replay
is stale and no-write rather than a new command. Restart discards the active
idempotency state and terminal-result cache.

Ordinary admin replies contain command outcome, coordinator state, and random
per-run correlation labels only. Status never returns a remote association,
`fingerprint_v1`, raw candidate input, certificate material, local identity, or
a stable peer-derived digest. The admin protocol is private even though its
privacy constraints are documented publicly.

## Facade And Service Adapter

The existing eeBUS facade remains conservative: `auto-accept` remains `false`.
An untrusted-peer callback is translated into one generation-bound coordinator
event. The callback itself cannot modify the store, open a window, compare OOB
input, or register trust.

The first exact non-error outbound `OutgoingAttemptHandshakeStateUpdate` is
translated only after verification of the selected outbound TLS/WebSocket
certificate-derived fingerprint and exact attempt metadata validation. The
custom inbound `Hub.ServeHTTP` translates
`ConnectionStateReceivedPairingRequest` only after successful WebSocket
upgrade; P-256 public-key recomputation by `cert.SkiFromCertificate`;
constant-time equality with `SubjectKeyId`; exact resolution of the service/SKI
pair; and atomic selection and internal registration of the exact inbound
winner in an opaque identity-keyed reservation. `RequireAnyClientCert` alone
cannot pass this gate. For a selected candidate, either path may supply the
initial TLS binding only for its exact certificate-derived SKI and current
connection generation.

If the inbound callback is emitted, a pending outbound and all competing
inbound attempts have already lost the reservation and emit no pairing,
SHIP-ID, completion, or close evidence. Wrong-SKI, unselected,
stale-generation, loser, or overlapping evidence is rejected and cannot
replace or combine bindings.

The tagged `RemoteSKIConnected`/`ServiceShipIDUpdate` and
`ConnectionStateCompleted` are translated separately. For the exact
already-certificate-trusting connection documented by the correction issues,
they may arrive before confirmation and are then latches only; no other SHIP or
SPINE payload is accepted from that ordering exception. The facade binds each
non-empty opaque value to the same `remote_ski`, TLS binding, and
`connection_generation`; a mismatched, absent, stale, early-but-unbound, or
disconnected value never completes an association. No fallback value is
synthesized.

After exact OOB confirmation, the facade must invoke `RegisterRemoteSKI` once
for the same `remote_ski` and connection generation before any durable commit.
It MUST recheck connection liveness, TLS binding, and generation immediately
before the call, and run it outside the coordinator lock so a synchronous
callback cannot deadlock the linearization point. Only after that call executes
may it consume a pre-confirm latch; immediately before consumption it MUST
revalidate candidate nonce, remote fingerprint/SKI, connection generation,
selected store generation, and connection liveness. The effect token makes
reentrant or concurrent duplicate callbacks no-ops. A disconnected or replaced
connection does not transfer either transient or durable authority to a stale
callback; normal discovery may apply a later durable association only through a
new generation.

The facade starts the one durable proposal only after the registered connection
has non-empty same-generation `observed_remote_ship_id` and
`ConnectionStateCompleted`, whether they arrived after registration or as a
revalidated pre-confirm latch. Any code path that consumes a latch before
`RegisterRemoteSKI` executes, or attempts to call `RegisterRemoteSKI` only after
durable confirmation, is a stale-ordering falsifier. Before durable commit,
terminal candidate-lifecycle events call `UnregisterRemoteSKI` once when
transient registration occurred, discard every latch, and keep the store
generation unchanged. Invalid or stale post-transient admin requests are
no-ops/errors and do not revoke the legitimate authorized candidate.

The facade serializes callback and event handoff with the coordinator's
generation check. If the disconnect transition is ordered before the SHIP-ID or
completed handoff, that evidence is stale and cannot commit. If
`ConnectionStateCompleted` is ordered first with all exact same-generation
bindings, the durable commit may proceed.

Competing peers, race losers and a peer arriving after window closure are
cancelled. A peer is also cancelled when its candidate expires, the admin
transport closes the window, a commit fails closed, or mutation becomes
disabled. Cancellation is a runtime effect of the coordinator result, not a
store operation or proof that the peer was malicious.

## Authorization And Observation Separation

An allowlisted SKI is policy input only. It may constrain
which peer a transport is permitted to handle, but it does not authenticate a
peer, complete SHIP, authorize `RegisterRemoteSKI`, write a durable association,
or create any observation. Startup and pairing-window transitions do not
convert configured policy into remote service, session, topology, pairing, or
candidate state.

Remote evidence has three independent sources. An mDNS observation callback may
create a visible service. An actual connection callback may create a session.
The pairing callback from that transport connection may create the single
volatile candidate. Earlier stages cannot synthesize later stages. Only exact
OOB confirmation followed by `commit_durable` creates durable trust.

Allowlist entries, protected identity material, and raw
callback identities are private runtime material. They are excluded from public
`Runtime`, `Snapshot`, `PairingState`, MCP, GraphQL, Portal, Home Assistant,
CLI, metrics, traces, logs, fixtures, evidence, and all other shareable output.

## Public Surface Freeze

MSP-04B does not change the active public API contract. Public `Runtime`,
`Snapshot`, and `PairingState` remain read-only observations. No public
declaration gains an open, close, confirm, cancel, register, unregister, trust,
candidate-mutation, allowlist, or endpoint operation. No
public value exposes candidate presence, the inbound winner reservation, remote
candidate identity, fingerprint, nonce, idempotency key, connection generation,
starting store generation, expiry, admin path, command history, or allowlist
entry.

The AF_UNIX command protocol, coordinator, candidate record, and facade
translation types remain private implementation details. The candidate does
not add an MCP tool/resource, GraphQL mutation, Portal action, Home Assistant
service, command-line mutation, HTTP handler, or network administration
surface.

MSP-045's combined read-only mapping is defined by the
[candidate trust/admin projection contract][projection-contract].

## Restart And Recovery

Orderly restart first unregisters every transiently registered candidate, then
discards the volatile window, candidate, nonce, active idempotency state, and
terminal-result cache. Restart discards the volatile window, candidate, nonce,
active idempotency state, and terminal-result cache even after a crash. It also
discards the volatile inbound winner reservation. A crash cannot depend on the
unregister callback, and the transient runtime registration dies with the
process. The next process must not replay or infer it.
The new process starts `DISABLED`, opens the store under MSP-04A rules, reloads
only the selected durable associations, and enters `PAIRING_CLOSED` when safe.
It never infers an open window, visible service, session, candidate, or observed
endpoint from configuration, a stale socket, process residue, previous reply,
log, cache, or client replay.

If Open reports an unavailable or ambiguous store state, mutation stays
`DISABLED`. `commit_applied_maintenance_failed` and
`commit_durability_unknown` always take this reopen path. Recovery-candidate
activation and anti-rollback policy remain outside MSP-04B; the coordinator
cannot promote an inactive MSP-04A recovery candidate.

## Falsifiable Gate Matrix

All evidence uses synthetic identities and disposable temporary directories.
Live device or private network evidence is neither required nor accepted as a
substitute for the deterministic cases below.

| Gate | Required observation | Falsifier |
| --- | --- | --- |
| `G02` | While pairing is closed, an unknown peer is refused and a store spy observes zero store writes. | Falsified if the peer is admitted, a candidate appears, or any persistent write occurs while the window is closed. |
| `G03` | While the window is open, the coordinator holds exactly one ephemeral RAM candidate and performs no persistent write before exact OOB confirmation. Exact selected-candidate inbound or outbound TLS evidence may bind only the current generation. Inbound evidence additionally follows P-256 public-key recomputation, constant-time `SubjectKeyId` equality, exact service resolution, and atomic winner reservation. Exact same-connection SHIP ID/completion received before confirmation is volatile untrusted/no-write; confirmation executes transient registration once before the latch may be consumed after all exact revalidation. | Falsified if `RequireAnyClientCert` alone supplies identity; wrong-SKI, unselected, stale-generation, loser, or overlap evidence supplies authority; pre-confirm evidence registers, commits, persists, or becomes public; candidate or transient state is durable; registration occurs without exact bindings; latch consumption omits nonce, fingerprint/SKI, generation, store-generation, or liveness revalidation; or a write occurs before complete post-handshake association binding. |
| `G04` | Two racing peers yield one candidate and one deterministic `candidate_busy` denial; wrong fingerprint leaves the store unchanged; and the opaque reservation emits evidence only for its exact winner. | Falsified if both peers win, the loser outcome varies, a pending outbound or competing inbound loser emits pairing/SHIP-ID/completion/close evidence, an unselected callback or a callback carrying the wrong SKI binds the candidate, stale or overlapping evidence replaces the binding, wrong OOB input clears/replaces the candidate, or any store write occurs for the wrong fingerprint. |
| `G05` | Allowlist entries and opening a pairing window result in no remote queue, dial, visible service, session, topology, or candidate; the window changes only local `register=true`. | Falsified if any remote effect or observed state follows policy configuration or the window transition. |
| `G06` | An mDNS callback creates only service visibility, a connection callback creates the session, and a transport-backed pairing callback creates the candidate; exact OOB confirmation creates bounded transient trust, while only exact OOB confirmation plus `commit_durable` create durable trust after executed transient registration and protocol completion. | Falsified if an earlier stage creates a later-stage observation, pre-confirm evidence gains authority, transient trust persists, durable trust lacks same-generation protocol completion, or policy input substitutes for a callback. |
| `G16` | Public artifact scans contain random per-run labels, outcomes, and counts only, while API-diff tests keep the supported public surface read-only and candidate-free. | Falsified if any winner-reservation or inbound/outbound TLS-binding detail, forbidden identity/secret category, candidate detail, stable peer history, or public mutation declaration appears in an artifact or stable surface. |

Store-boundary and AF_UNIX proofs remain separate required tests. They support
the architecture and security contract but are not substitutes for the locked
gate meanings above.

### G16 Public Artifact Contract

Public and other shareable artifacts, including test reports, CI logs, failure
summaries, fixtures, screenshots, metrics, and traces, use random per-run
labels, outcomes, and counts only. Labels are generated independently for each
run, are not derived from peer or local data, and are not reusable as history
keys.

Public artifacts forbid raw or encoded peer identity, fingerprint, PEM, key,
token, protocol-service identity, endpoint, IP address, port, MAC address,
serial, local identity, stable peer digest, attempt token, and history. The
prohibition includes plaintext,
alternate encoding, truncation, hashing, structured fields, filenames, paths,
test names, exception wrapping, debug formatting, panic output, and golden-file
diffs. A stable hash of a peer identifier or endpoint is still a forbidden
stable peer digest, not acceptable redaction.

## Required Tests

MSP-04B code acceptance requires focused deterministic tests with synthetic
values and no live peer dependency:

1. Store-boundary spies prove policy-free calls, complete proposed generations,
   starting-generation conflict handling, one Commit, every store commit
   outcome, no retry, and exact facade ordering after `commit_durable`.
2. Coordinator table tests cover every state/event pair, first-event wins,
   `candidate_busy`, wrong fingerprint, stale nonce, both generation mismatches,
   transient registration, same-generation `ship_handshake_complete` from
   `ConnectionStateCompleted`, idempotent replay/conflict, bounded
   terminal-cache expiry, candidate/window expiry, cancel, close, and restart.
   Dedicated negative cases prove that pre-confirm SHIP ID/completion is
   volatile/no-write, that confirmation executes registration before latch
   consumption, and that wrong nonce, fingerprint/SKI, connection generation,
   store generation, or connection liveness rejects the latch. Dedicated cases
   also enforce exact G02, G03, and G04 meanings.
3. Deterministic scheduler tests force confirm-versus-cancel and
   confirm-versus-expiry at each linearization boundary and prove at most one
   commit with stable loser outcomes. Fake-clock and blocked-Commit cases prove
   logical close precedes Commit, no new candidate is admitted while the global
   waiting permission remains true, the permission interval is bounded, and
   terminal effects follow the required false-before-approval ordering.
4. Admin transport tests cover wrong UID, missing peer credentials, symlink,
   pathname substitution, stale socket, active socket, wrong owner/type,
   malformed and oversized frames, partial frames, unknown/duplicate fields,
   replayed request, deadlines, connection/concurrency bounds, and no loopback
   listener or fallback. Privileged-read tests prove exact fields, same-UID
   gating, buffer clearing, and absence from logs, metrics, traces, captures,
   fixtures, and other shareable outputs.
5. Facade tests keep auto-accept false, bind callbacks to one connection
   generation, prove `RequireAnyClientCert` alone is insufficient, and prove
   the inbound callback follows WebSocket upgrade, P-256 public-key
   recomputation by `cert.SkiFromCertificate`, constant-time `SubjectKeyId`
   equality, exact resolution of the service/SKI pair, and atomic reservation
   of the exact inbound winner. They cover wrong SKI, an unselected peer, stale
   generation, a pending outbound loser, competing inbound losers, and
   forbidden inbound/outbound overlap; prove losers emit no
   pairing/SHIP-ID/completion/close evidence; bind `ServiceShipIDUpdate`
   and protocol completion to the same TLS-bound pairing key/generation; reject
   absent/stale/mismatched/disconnected values without writes; call
   `RegisterRemoteSKI` once after exact OOB confirmation before durable commit;
   and prove the stale policy to call
   `RegisterRemoteSKI` only after durable commit is rejected. They also
   prove pre-confirm SHIP ID/completion cannot be consumed until registration
   executes and every exact binding is revalidated, while race losers/closed-window
   peers are cancelled and terminal transient trust is unregistered once.
6. Observation-source tests prove that allowlist entries and opening a
   pairing window create no queue, dial, service, session, topology, or
   candidate; mDNS, connection, and transport-backed pairing callbacks create
   only their respective stages, and trust follows only exact OOB confirmation
   plus `commit_durable`.
7. Recovery tests cover `commit_applied_maintenance_failed`,
   `commit_durability_unknown`, disabled mutation, mandatory reopen, durable
   association reload, loss of every volatile field across restart, and no
   reconstruction of observed remote state from policy configuration.
8. Public API and artifact tests compare the frozen public API, reject public
   mutation/candidate detail, and scan all G16 outputs for forbidden raw,
   encoded, truncated, hashed, formatted, endpoint-derived, and path-derived
   identity material.

The authoritative local CI must pass. No test may rely on a real identifier,
private network or device evidence, a public mutation surface, or an assertion
that implementation already exists.

## Explicit Exclusions

MSP-04B adds none of the following:

- trust revocation, association deletion, or recovery activation;
- more than one pending candidate or concurrent pairing window;
- automatic trust, TOFU without explicit confirmation, or auto-accept;
- certificate-leaf fingerprint confirmation under `fingerprint_v1`;
- TCP, HTTP, loopback, remote, Portal, GraphQL, MCP, Home Assistant, or
  command-line administration;
- store-owned pairing/trust policy or socket lifecycle;
- durable window, candidate, nonce, idempotency, or command-history records;
- policy-derived remote observations or pairing-window-triggered remote work;
- public candidate detail or public mutation API;
- protocol-semantic claims or device-specific behavior; or
- support or implementation-completion claims before code and publication
  gates complete.

[docs-issue]: https://github.com/Project-Helianthus/helianthus-docs-eebus/issues/22
[code-issue]: https://github.com/Project-Helianthus/helianthus-eebusreg/issues/26
[preconfirm-docs-issue]: https://github.com/Project-Helianthus/helianthus-docs-eebus/issues/58
[preconfirm-code-issue]: https://github.com/Project-Helianthus/helianthus-eebusreg/issues/62
[inbound-docs-issue]: https://github.com/Project-Helianthus/helianthus-docs-eebus/issues/60
[inbound-code-issue]: https://github.com/Project-Helianthus/helianthus-eebusreg/issues/64
[implementation-commit]: https://github.com/Project-Helianthus/helianthus-eebusreg/tree/18049eef059813c23d0a3385115bfa61fcec635c/
[projection-contract]: msp-045-trust-admin-projection.md
[store-contract]: msp-04a-persistent-store.md
