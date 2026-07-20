---
canonical_source: "Project-Helianthus/helianthus-docs-eebus:architecture/_candidate/msp-04b-first-trust-admin-local.md"
owner_domain: "architecture"
license: "AGPL-3.0-only"
publication_status: "candidate"
claim_status: "evidence-backed"
source_class: "derived_inference"
evidence_ids: "EV-20260711-001,EV-20260720-001"
hypothesis_status: "draft"
falsifier: "An accepted architecture review or conformance result demonstrates that the merged MSP-04B implementation cannot preserve exact-candidate confirmation, local-admin confinement, store ownership, or public privacy boundaries."
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
| `facade/service adapter` | Translation between eeBUS callbacks and private coordinator events, plus application of a durably confirmed association. | It does not auto-accept, bypass the coordinator, publish before durability, or preserve a race loser. |
| `public Runtime/Snapshot/PairingState` | The existing read-only supported observation surface. | MSP-04B adds no public mutation operation or candidate detail. |

The boundaries are directional. The coordinator asks `internal/eebusstore` to
validate and atomically publish a complete opaque association; the store
returns one deterministic outcome and never learns why the caller requested
it. The admin transport authenticates and frames a request before handing a
typed command to the coordinator; it never evaluates the fingerprint or
chooses a candidate. The facade translates callback shape and effects only a
coordinator decision.

## Candidate And Confirmation Binding

The coordinator has exactly one volatile candidate slot. An eligible first
contact captures the pairing identity and all immediately available bindings.
The candidate may remain association-incomplete until the matching service
identifier is observed, but it still occupies the only slot.

| Binding | Constraint |
| --- | --- |
| `remote_ski` | Opaque bytes from the pairing callback, bound to the exact connection generation and never rendered except as `fingerprint_v1` in the privileged local response. |
| `observed_remote_ship_id` | A non-empty opaque value supplied by `ServiceShipIDUpdate` for the same `remote_ski` and `connection_generation`; it may be absent while the candidate remains pending. |
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

The facade obtains `observed_remote_ship_id` only from `ServiceShipIDUpdate`.
An update that precedes the pairing callback may be attached from bounded
connection-scoped facade state only when its `remote_ski` and
`connection_generation` exactly match the winning candidate. An update that
arrives later completes that same candidate under the same equality rule.
Empty, stale-generation, differently keyed, ambiguous, or expired updates do
not complete it. The coordinator and facade MUST NOT invent, default, derive,
or copy the value from another connection.

A confirm received before `observed_remote_ship_id` is non-empty returns stable
`association_incomplete`, keeps the candidate pending with no store write, and
does not consume successful OOB input as a durable approval. The caller may
retry with the same candidate bindings after the matching update arrives and
before expiry. After exact OOB success and complete binding validation, the
proposed association persists `remote_ski` and `observed_remote_ship_id`
together in one atomic generation. Neither value is persisted earlier.

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
confirmation contract, new binding and normalization rules, migration of any
admin client, and a separate review. It MUST NOT be substituted silently for
`fingerprint_v1`.

## Coordinator State Machine

The private coordinator has exactly these externally testable states. All
events are serialized through one linearization point, and the first terminal
rule in the current state wins.

| State | Meaning | Allowed next state |
| --- | --- | --- |
| `DISABLED` | Mutation is unavailable because startup has not established a usable store, or a prior outcome requires reopen. | `PAIRING_CLOSED` only after a successful reopen and reload. |
| `PAIRING_CLOSED` | Default state; no first-trust candidate may be admitted. | `OPEN_EMPTY` when an authenticated admin command opens a bounded window. |
| `OPEN_EMPTY` | A bounded pairing window is open and the candidate slot is empty. | `CANDIDATE_PENDING` for the first linearized eligible peer; otherwise `PAIRING_CLOSED` on close or window expiry. |
| `CANDIDATE_PENDING` | Exactly one eligible RAM candidate owns the slot; `observed_remote_ship_id` may still be absent. | Remain pending on `association_incomplete`, enter `COMMITTING` after complete valid confirmation, enter `OPEN_EMPTY` after candidate cancel/expiry while the window remains open, or enter `PAIRING_CLOSED` when the window closes/expires. |
| `COMMITTING` | The window is already closed and one complete association is being validated and committed. | `PAIRING_CLOSED` after a known terminal result, or `DISABLED` when reopen is required. |

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
generation, or idempotency conflict leaves the store unchanged and the
candidate intact until its existing expiry. Cancel or expiry clears the
candidate. Candidate expiry returns to `OPEN_EMPTY` only while the pairing
window itself remains valid; window close or expiry enters `PAIRING_CLOSED`.

Missing `observed_remote_ship_id` follows the same no-write rule but returns
`association_incomplete`; it is not a fingerprint failure and does not clear
the candidate. A matching `ServiceShipIDUpdate` may complete the candidate only
before the candidate and connection generations expire.

A valid confirmation is linearized before any filesystem mutation. The
coordinator MUST Close the pairing window before beginning one commit, enter
`COMMITTING`, and prevent another candidate or confirmation from being
admitted. This ordering makes confirm-versus-cancel and confirm-versus-expiry
races deterministic: whichever event linearizes first determines whether the
commit may start. A losing confirm cannot reopen, replace, or commit a cleared
candidate.

## Waiting Permission And Commit Ordering

In the pinned eeBUS library, `UserIsAbleToApproveOrCancelPairingRequests`
controls the global `AllowWaitingForTrust` permission. That permission allows a
pending protocol exchange to wait; it does not approve a peer, select a candidate,
validate OOB input, or persist trust. It is a transport-liveness control, not
the security decision.

After complete exact confirmation linearizes, the coordinator logically closes
the pairing window before Commit and admits no new candidate. `auto-accept`
remains `false`, every competing peer is cancelled, and a new callback is
refused even if the library's global waiting permission has not yet changed.
Logical closure and candidate admission therefore do not depend on that global
flag.

To avoid aborting the winning pending handshake before disk publication, the
adapter may keep `AllowWaitingForTrust` `true` only through the bounded
`COMMITTING` interval for the winner. A nonzero implementation constant defines
the monotonic commit-wait bound, and Commit must run under that bound. The flag
is set `false` before or atomically with the terminal effect. Only
`RegisterRemoteSKI` after `commit_durable` actually approves the winner; the
global flag itself never does.

If the commit-wait bound expires before a deterministic store result, the
adapter sets the flag `false`, cancels the winner, performs no
`RegisterRemoteSKI`, disables mutation, reports the trust outcome unknown, and
marks reopen required after the in-flight store operation is safely fenced.
Known store outcomes follow the mapping below. Deterministic tests MUST record
the ordered events for success, every failure outcome, a blocked Commit, a
racing peer while the global flag remains true, and terminal cleanup.

## SHIP Pairing Registration Advertisement

The SHIP DNS-SD `register` value is a discovery signal, not a trust decision.
`PAIRING_CLOSED` advertises `register=false`, while `OPEN_EMPTY` advertises
`register=true`. `CANDIDATE_PENDING` keeps `register=true` within the original
bounded window so the selected protocol exchange remains discoverable; the
single-candidate rule still rejects every competing peer deterministically.

After exact confirmation, `COMMITTING` may retain `register=true` only during
the bounded commit-wait interval needed by the winning handshake. Close,
expiry, cancellation, or any terminal commit effect withdraws or replaces the
announcement with `register=false`. `DISABLED` also advertises
`register=false` and requires a successful reopen before another window.

This registration signal is independent from handshake acceptance:
`auto-accept` remains `false`. It does not approve the selected peer and does
not persist trust. Only the exact, durably confirmed association reaches
`RegisterRemoteSKI`. A failed registration update is an explicit degraded
outcome and cannot be represented as an empty successful window.

## Store Commit Outcome Mapping

The coordinator passes one complete proposed generation to
`internal/eebusstore`; it does not edit a live association in place. The
starting generation must still match immediately before Commit. Store
validation and provider checks remain store-owned and precede filesystem
publication.

| Store result | Coordinator result | Required action |
| --- | --- | --- |
| `commit_durable` | `trusted` | Clear the candidate, retain the closed window, and allow the facade to invoke `RegisterRemoteSKI` for this exact connection generation. |
| `commit_not_published` | `failed_closed_unchanged` | Treat the store as unchanged, clear the candidate, keep pairing closed, and require a new window/candidate for retry. |
| `validation/provider failure` | `failed_closed_unchanged` | Map deterministic validation, key-provider, or key-material outcomes without mutation; clear the candidate and keep pairing closed. |
| `commit_applied_maintenance_failed` | `applied_reopen_required` | Do not invoke `RegisterRemoteSKI`; disable mutation, close/cancel live pairing work, and reopen before durable associations may reload trust. |
| `commit_durability_unknown` | `trust_outcome_unknown` | Do not report success or failure-as-unapplied and do not invoke `RegisterRemoteSKI`; disable mutation and require reopen to determine the selected generation. |

Only `commit_durable` may make the current in-process result trusted and invoke
`RegisterRemoteSKI`. Known-unapplied failures never retry automatically.
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

`ServiceShipIDUpdate` is translated separately and may occur before or after
the pairing callback. The facade binds its non-empty opaque value to the same
`remote_ski` and `connection_generation`; a mismatched or absent value never
completes an association. Confirmation persists both values only after exact
OOB success. No fallback value is synthesized.

When the coordinator reports `trusted` after `commit_durable`, the facade may
invoke `RegisterRemoteSKI` once for the same remote SKI and connection
generation. It MUST recheck connection liveness and generation immediately
before the call. A disconnected or replaced connection does not transfer the
durable association to a stale callback; normal discovery may apply it to a
later matching peer through a new generation.

Competing peers, race losers and a peer arriving after window closure are
cancelled. A peer is also cancelled when its candidate expires, the admin
transport closes the window, a commit fails closed, or mutation becomes
disabled. Cancellation is a runtime effect of the coordinator result, not a
store operation or proof that the peer was malicious.

## Protected Outbound Pairing And Endpoint Discipline

An outbound endpoint allowlist is an admission input, not trust. It may say
that the private coordinator is permitted to consider a discovered endpoint
for one outbound SHIP attempt; it does not authenticate a peer, complete SHIP,
authorize `RegisterRemoteSKI`, create a reconnect right, or write a durable
association. A malformed, stale, ambiguous, unauthorized, or unavailable
allowlist result fails closed: no dial, no candidate, no endpoint report, and
no trust effect.

While a locally authenticated pairing window is open, the coordinator may keep
a bounded, RAM-only queue of eligible outbound attempt records. An entry holds
only opaque endpoint and discovery bindings, a fresh private attempt token,
the window/candidate generation, and a monotonic expiry. The queue has a fixed
capacity and per-entry expiry; duplicate, stale, over-capacity, and
window-mismatched reports are rejected without replacing an earlier entry.
It is neither a durable work queue nor a retry ledger. Closing the window,
window expiry, candidate expiry, cancellation, commit start, disabled
mutation, and process restart clear every queued record and cancel any
associated in-flight attempt.

The endpoint-report path is a gate, not a passive diagnostic feed. It may
release an attempt only after same-UID local authorization, an open unexpired
window, a successful current allowlist decision, and a complete bounded report
binding. If report validation, queueing, cancellation, or dispatch cannot be
proved for that exact record, the coordinator reports a stable no-attempt
outcome and fails closed. It must not fall back to an older endpoint, a DNS
cache entry, an inferred address, or an unauthenticated discovery result.

`SHIP` pairing completion is attempt-aware. A completion or callback may affect the
current candidate only when its private attempt token, endpoint binding,
connection generation, and unexpired window all match the linearized queue
record. A late completion, a completion from a prior retry, or a callback after
close/expiry/cancel is ignored or cancelled and cannot turn an allowlisted
endpoint into a trusted peer. This rule applies equally when the transport
performs address-family or discovery retries: each wire attempt remains bound
to the same authorized record or is denied.

Revocation or unregister linearizes ahead of an in-flight gated trusted
reconnect before its `DialContext` call or later continuation. The coordinator
then invalidates the attempt record and cancels its exact attempt context; the
facade rechecks that invalidation immediately before dialing and before every
continuation that could use the reconnect endpoint. A revocation/unregister
winner therefore permits neither a new dial nor a resumed handshake, even if
the record was previously allowlisted or had already passed a report gate.

The coordinator may hold its serialization lock while it creates, binds, or
invalidates an attempt record, but it MUST release that lock before
`DialContext`. No lock may span the dial or wait for its result. Cancellation,
close, expiry, revocation, and unregister must be able to reach the exact
attempt context without waiting for an in-flight dial to return. The dialer
receives only a cancellable attempt context and an immutable private snapshot;
once cancellation wins, a late dial result cannot revive, continue, or register
the attempt.

Only exact OOB confirmation followed by `commit_durable` creates durable trust.
Before that point, an endpoint is an ephemeral attempt input, not an association
attribute. After durable confirmation, a matching endpoint may be retained as
a private trusted-reconnect endpoint for that exact association and used only
through the normal trusted reconnect path. Reconnect eligibility is derived
from the durable association, never from the allowlist or an unfinished queue
entry; revocation, a changed association binding, or a failed durability result
removes the right to use it.

Endpoint values, attempt tokens, queue position, endpoint-report outcomes that
would identify a peer, and reconnect endpoint details are private runtime
material. They are excluded from public `Runtime`, `Snapshot`, `PairingState`,
MCP, GraphQL, Portal, Home Assistant, CLI, metrics, traces, logs, fixtures,
evidence, and all other shareable output.

## Public Surface Freeze

MSP-04B does not change the active public API contract. Public `Runtime`,
`Snapshot`, and `PairingState` remain read-only observations. No public
declaration gains an open, close, confirm, cancel, register, unregister, trust,
candidate-mutation, endpoint-report, allowlist, or reconnect operation. No
public value exposes candidate presence, remote candidate identity, fingerprint,
nonce, idempotency key, connection generation, starting store generation,
expiry, admin path, command history, endpoint, endpoint report, queue state,
attempt token, or trusted reconnect endpoint.

The AF_UNIX command protocol, coordinator, candidate record, and facade
translation types remain private implementation details. The candidate does
not add an MCP tool/resource, GraphQL mutation, Portal action, Home Assistant
service, command-line mutation, HTTP handler, or network administration
surface.

MSP-045's combined read-only mapping is defined by the
[candidate trust/admin projection contract][projection-contract].

## Restart And Recovery

Restart discards the volatile window, candidate, nonce, active idempotency
state, terminal-result cache, endpoint reports, and outbound-attempt queue.
The new process starts `DISABLED`, opens the store under MSP-04A rules, reloads
only the selected durable associations, and enters `PAIRING_CLOSED` when safe.
It never infers an open window, permitted endpoint, or in-flight attempt from a
stale socket, process residue, previous reply, log, cache, or client replay.

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
| `G03` | While the window is open, the coordinator holds exactly one ephemeral RAM candidate and performs no persistent write before exact OOB confirmation; an incomplete association remains pending/no-write. | Falsified if candidate state is durable, more than one candidate is held, or a write occurs before exact OOB confirmation and complete association binding. |
| `G04` | Two racing peers yield one candidate and one deterministic `candidate_busy` denial, and wrong fingerprint leaves the store unchanged. | Falsified if both peers win, the loser outcome varies, wrong OOB input clears/replaces the candidate, or any store write occurs for the wrong fingerprint. |
| `G05` | An allowlisted outbound endpoint creates at most one bounded ephemeral attempt record; stale, malformed, unauthorized, full-queue, closed-window, cancelled, and expired reports cause no dial, trust write, or public endpoint output. | Falsified if an allowlist result acts as trust, a stale/unauthorized report dials, queue state survives cleanup, or an endpoint value reaches a shareable surface. |
| `G06` | A `SHIP` pairing completion is accepted only for its current private attempt binding, and only exact OOB confirmation plus `commit_durable` enables a trusted reconnect endpoint. | Falsified if a late/retried completion is accepted, close/expiry/cancel leaves an attempt live, or an endpoint becomes reconnectable before durable trust. |
| `G16` | Public artifact scans contain random per-run labels, outcomes, and counts only, while API-diff tests keep the supported public surface read-only and candidate-free. | Falsified if any forbidden identity/secret category, candidate detail, stable peer history, or public mutation declaration appears in an artifact. |

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
   association-incomplete confirmation, both `ServiceShipIDUpdate` orders,
   idempotent replay/conflict, bounded terminal-cache expiry, candidate/window
   expiry, cancel, close, and restart. Dedicated cases enforce exact G02, G03,
   and G04 meanings.
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
   generation, bind `ServiceShipIDUpdate` to the same pairing key/generation,
   reject absent/stale/mismatched values without writes, call
   `RegisterRemoteSKI` only after durable confirmation, and prove race
   losers/closed-window peers are cancelled.
6. Outbound-attempt tests prove allowlist-not-trust, bounded ephemeral queue
   capacity and expiry, endpoint-report fail-closed behavior, attempt-aware
   `SHIP` pairing completion across retry and late-callback cases, cleanup on close,
   expiry, and cancel, revocation/unregister cancellation before dial and
   continuation, no serialization lock across `DialContext`, and private
   trusted-reconnect use only after exact OOB confirmation plus `commit_durable`.
7. Recovery tests cover `commit_applied_maintenance_failed`,
   `commit_durability_unknown`, disabled mutation, mandatory reopen, durable
   association reload, loss of every volatile field across restart, and no
   restoration of an untrusted endpoint or outbound attempt.
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
- durable outbound attempt queues or endpoint reports before `commit_durable`;
- public candidate detail or public mutation API;
- protocol-semantic claims or device-specific behavior; or
- support or implementation-completion claims before code and publication
  gates complete.

[docs-issue]: https://github.com/Project-Helianthus/helianthus-docs-eebus/issues/22
[code-issue]: https://github.com/Project-Helianthus/helianthus-eebusreg/issues/26
[implementation-commit]: https://github.com/Project-Helianthus/helianthus-eebusreg/tree/18049eef059813c23d0a3385115bfa61fcec635c/
[projection-contract]: msp-045-trust-admin-projection.md
[store-contract]: msp-04a-persistent-store.md
