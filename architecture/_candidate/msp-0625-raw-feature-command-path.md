---
canonical_source: "Project-Helianthus/helianthus-docs-eebus:architecture/_candidate/msp-0625-raw-feature-command-path.md"
owner_domain: "architecture"
license: "AGPL-3.0-only"
publication_status: "candidate"
claim_status: "evidence-backed"
source_class: "derived_inference"
evidence_ids: "EV-20260711-001,EV-20260726-001"
hypothesis_status: "draft"
falsifier: "A fake-peer, race, crash-injection, reconnect, or bounded live run demonstrates that the single router path, waiter-before-send round trip, durable FSM, CAS guard, or quarantine rules cannot preserve the stated safety invariants."
stable_navigation: "false"
search: "false"
sitemap: "false"
versioned_bundle: "false"
release_bundle: "false"
---

# Candidate M6.25 Raw Feature Command Architecture

## Additive Milestone Boundary

This candidate implements the docs gate for
[issue 76](https://github.com/Project-Helianthus/helianthus-docs-eebus/issues/76)
as corrected before release by
[issue 78](https://github.com/Project-Helianthus/helianthus-docs-eebus/issues/78),
with additive SPINE transport-handoff evidence tracked by
[issue 80](https://github.com/Project-Helianthus/helianthus-docs-eebus/issues/80),
and the locked
[M6.25 plan](https://github.com/Project-Helianthus/helianthus-execution-plans/blob/fb384ab57d79f0020c54d2c66416e8a7666f0ceb/multi-runtime-semantic-platform.locked/118-w30-26-m625-raw-spine-feature-acquisition.md).
It is forward-only. M6 topology, snapshots, local/raw access, public/redacted
access, and reconnect completion remain accepted and unchanged. M6.5 live
evidence remains partial, M7 remains candidate-only, and no later consumer
milestone is promoted.

The protocol, API, and provenance owners are
[msp-0625-feature-data-acquisition.md](../../protocols/_candidate/msp-0625-feature-data-acquisition.md),
candidate API owner `msp-0625-raw-feature-acquisition.md`,
and
[msp-0625-provenance-policy.md](../../development/msp-0625-provenance-policy.md).

Every design below is a candidate Helianthus invariant, not a deployed-runtime
claim.

## Single Command Path

The only permitted path is:

```text
MCP
  -> gateway EEBusCommandRouter
  -> eebusreg RawFeatureRuntimeV1 or RawMutationRuntimeV1
  -> eebusreg internal durable mutation coordinator for mutation methods
  -> eebus-go exact feature executor
  -> spine-go atomic correlated round trip
  -> existing SHIP session
```

| Boundary | Sole responsibility |
| --- | --- |
| MCP | Parse a closed tool shape, authenticate, select fixed scope/tier policy, and deny public contact. |
| Gateway `EEBusCommandRouter` | Provide one reusable command entry point, select one runtime, and hand policy to eebusreg. |
| eebusreg `RawFeatureRuntimeV1` | Preserve the existing public read-only `FeaturesGet` and `FeaturesDataGet` method set unchanged. |
| eebusreg `RawMutationRuntimeV1` | Own the separate public `FeaturesDataSet`, `MutationsGet`, and `MutationsRollback` mutation capability. |
| eebusreg internal durable coordinator | Own runtime epoch, connection generation, read tokens, CAS, WAL/FSM, idempotency, lease, constraints, probe TTL, audit, recovery, and quarantine without becoming public. |
| eebus-go exact executor | Resolve the exact local/remote feature pair and build one full typed READ or WRITE. |
| spine-go round trip | Atomically register, send, correlate, cancel, clean up, and tombstone one request. |
| Existing SHIP | Carry the existing encrypted session payload without an M6.25 API or framing change. |

No MCP handler may call an Enbility feature, sender, adapter, or SHIP object
directly. Future semantic command callers, if separately authorized, must
reuse `EEBusCommandRouter`; M6.25 creates no such caller.

`RawFeatureRuntimeV1` remains exactly:

```go
type RawFeatureRuntimeV1 interface {
    FeaturesGet(context.Context, eebusraw.ReadAuthorizationV1, eebusraw.FeaturesGetRequestV1) (eebusraw.FeaturesGetDataV1, *eebusraw.ErrorV1)
    FeaturesDataGet(context.Context, eebusraw.ReadAuthorizationV1, eebusraw.FeatureDataGetRequestV1) (eebusraw.FeatureDataGetDataV1, *eebusraw.ErrorV1)
}
```

The existing public `Runtime` method set is unchanged and does not embed
`RawMutationRuntimeV1`. A concrete runtime implementation may satisfy both
interfaces. The gateway later capability-asserts `RawMutationRuntimeV1` and
fails closed when it is unavailable; no mutation method is added to `Runtime`.

The public source shows that approved transport completion already hands an
existing writer to SPINE setup
([eeBUS bridge](https://github.com/Project-Helianthus/helianthus-eebus-go/blob/0134afee59535d927d63b78070f828f0f6fb553d/service/service_hub.go#L30-L33)).
The new capability gap is above that established transport: exact generic
feature execution and atomic response correlation. ship-go therefore remains
unchanged unless later public source evidence falsifies this boundary.

## Authorization Before Contact

The local owner-authorized `AF_UNIX` surface is the only M6.25 tool surface.
It can receive `eebus.raw.read` and `eebus.raw.write` according to the exact
tool policy. The public/LAN surface receives neither M6.25 capability.

Evaluation order is fixed:

1. JSON-RPC and tool shape;
2. boundary identity and fixed transport policy;
3. required authorization scope;
4. only then provider lookup;
5. gateway router;
6. runtime and coordinator;
7. connection and remote contact.

A public request, wrong scope, caller-supplied tier selector, or malformed
request fails before provider, router, runtime, connection, or remote contact.
Tests instrument each boundary and require zero downstream calls and zero
frames. Authorization cannot be deferred to the provider or runtime.

The existing public `ReadAuthorizationV1`,
`AuthScopeV1RawRead`, and `ValidateReadAuthorizationV1` remain unchanged and
are not aliases for write authority. M6.25 adds the distinct public
`WriteAuthorizationV1`, `AuthScopeV1RawWrite`, and
`ValidateWriteAuthorizationV1`. `FeaturesDataSet` and `MutationsRollback`
require validated write authorization. `MutationsGet` remains status-only and
requires validated read authorization.

## Runtime Epoch And Connection Generation

`runtime_epoch` is a positive durable monotonic value. It changes when
persisted runtime identity or trust binding is replaced, repaired, or reset.
It does not change for a normal transport reconnect.

`connection_generation` is a positive monotonic value within one runtime
epoch. It changes for each newly admitted live SPINE connection. A disconnected
generation is never admitted again.

Every target, waiter, read token, mutation, idempotency record, audit link, and
recovery decision binds both values. A stale epoch or generation detected
before dispatch is `failed_no_contact`. Recovery may rebind to a new generation
only after a fresh READ proves the current value equals the before-image or
requested value.

## Atomic Correlated Round Trip

spine-go must expose one context-aware primitive that owns correlation from
allocation through retirement:

1. allocate a generation-bound monotonic key;
2. reject an active or retired duplicate;
3. register the waiter before send;
4. send after successful registration;
5. tolerate a reply delivered synchronously inside send;
6. complete exactly once;
7. remove the active waiter on success, send failure, timeout, cancellation,
   disconnect, malformed response, and remote error; and
8. retain a bounded tombstone through the generation.

The tombstone prevents late-response ABA: a reply for a timed-out or cancelled
key cannot complete a successor. Keys are not reused within a generation.
Disconnect retires the generation, completes its waiters, and rejects its
later responses. In-flight count and tombstone count are bounded and
observable without exposing payload data.

The current public stack sends before a caller can register a response callback
([request path](https://github.com/Project-Helianthus/helianthus-spine-go/blob/7383c108f72309c3636d896948d7a8de6d001708/spine/feature_local.go#L414-L440),
[callback path](https://github.com/Project-Helianthus/helianthus-spine-go/blob/7383c108f72309c3636d896948d7a8de6d001708/spine/feature_local.go#L107-L140)).
M6.25 therefore requires a new atomic spine-go primitive rather than wrapping
those two calls at a higher layer.

### SPINE-To-SHIP/Transport Evidence Contract

The round-trip API adds a bounded operation-scoped disposition without changing
its existing method:

```go
type DispatchDisposition uint8

const (
    NoTransportHandoff       DispatchDisposition = 1
    TransportHandoffPossible DispatchDisposition = 2
)

type CorrelatedRoundTripError struct {
    Cause       error
    Disposition DispatchDisposition
}

func (e *CorrelatedRoundTripError) Error() string
func (e *CorrelatedRoundTripError) Unwrap() error

RoundTrip(ctx context.Context, request CorrelatedRequest) (CorrelatedResponse, error)
```

Every terminal `RoundTrip` failure carries a non-nil cause and exactly one
disposition. `Unwrap` returns the cause. Existing sentinel checks with
`errors.Is`, existing typed-cause checks with `errors.As`, and direct
`errors.As` extraction of `*CorrelatedRoundTripError` therefore remain
compatible. Neither the response type nor the `RoundTrip` signature changes.

The classification boundary is writer entry for that exact operation:

| Operation phase at terminal failure | Required disposition |
| --- | --- |
| Context already done, request invalid, capacity/counter/key admission failed, marshaling failed, writer missing, sender closed, or any other failure before calling the SHIP writer | `NoTransportHandoff` |
| SHIP writer invocation began, or the operation was awaiting a correlated reply/result when cancellation, timeout, close, disconnect, remote rejection, malformed response, or another failure occurred | `TransportHandoffPossible` |

The distinction is evidence about one SPINE-to-SHIP handoff attempt, not the
connection, session, device, or mutation as a whole. The current SHIP writer is
`WriteShipMessageWithPayload(message []byte)` and has no return value
([writer call](https://github.com/Project-Helianthus/helianthus-spine-go/blob/b21400335be90ea95a6cad5f512d1c8e22f2cdeb/spine/send.go#L69-L112),
[transport interface](https://github.com/Project-Helianthus/helianthus-ship-go/blob/3abd41d19f419de907bc1bdf2a126ca19c930626/api/shipconnection.go#L195-L200)).
`TransportHandoffPossible` therefore proves only that writer invocation began.
It is not proof that bytes were queued, written on the wire, received by the
peer, accepted by SPINE, or applied by the remote feature.

The selected M6.25 executor path through eebus-go must preserve
`*CorrelatedRoundTripError` in the `errors.Is`/`errors.As` chain. Any dependency
path that stringifies or recreates the error destroys `NoTransportHandoff`
evidence and must be rejected or repaired. eebusreg must use `errors.As`, never
message text or cause identity, to obtain the disposition. If downstream still
receives an untyped error, missing wrapper, nil cause, zero value, or
unrecognized disposition, it treats the loss conservatively as
`TransportHandoffPossible`. Only an explicit valid `NoTransportHandoff` may
support a zero-contact assertion.

The rule is symmetric across mutation phases. For the original WRITE,
`NoTransportHandoff` may support `failed_no_contact`; possible handoff records
`outcome_unknown` from `dispatch_intent`. For the rollback WRITE,
`NoTransportHandoff` proves only that the rollback writer was not invoked: it
does not erase the original effect or prove `rolled_back`. A later rollback
attempt still requires the lease, fresh READ, exact binding, and durable
recovery decision. Possible rollback handoff records `outcome_unknown` from
`rollback_dispatch_intent`. Neither path permits blind retry after possible
handoff.

## Read Token And CAS

Each successful full READ mints a read token bound to:

- runtime epoch and connection generation;
- principal class, authorization scope, mask tier, and tool;
- remote SKI, SHIP ID, complete feature address, feature type/role, function,
  and operation;
- canonical request hash and before-image value hash;
- expiry; and
- one-use or explicitly reusable function profile.

A WRITE requires the token. Under the global writer lease, the coordinator
performs a fresh full READ immediately before recording `dispatch_intent`. The
fresh JCS value hash must match the token before-image and any supplied
`expected_current`. Token or target mismatch fails before runtime/session
contact; fresh-value mismatch may emit the guard READ but emits zero WRITE
frames. Token substitution across session, principal, tool, target, or tier is
`permission_denied` or `stale_read_token`, never automatic rebinding.

## Global Writer Lease And Idempotency

One global eebusreg runtime writer lease serializes all writes, automatic probe
rollbacks, explicit rollbacks, and recovery rollbacks. Reads may execute
concurrently within bounded round-trip capacity. Writers never interleave
frames and do not queue without a bound.

Idempotency identity is:

```text
(runtime_epoch, principal, tool, idempotency_key)
```

The durable record also binds the canonical request JCS hash. Same key and
same hash return the original mutation identity and current durable state
without a second frame. Same key and different hash is
`idempotency_conflict`. Idempotency never crosses epoch or principal.

## Constraints And Probe Profiles

The coordinator requires full WRITE, changeability, known enum/range/step/unit/
cardinality/cross-field constraints, an exact lab allowlist entry, a complete
rollback before-image, and green safety predicates.

Unknown constraints fail closed. The only override is a versioned exact-target
lab profile containing permitted values or bounds, probe TTL, safety
predicates, justification, and rollback shape. A wildcard, device-family
inference, or sibling-feature inheritance is invalid.

`mode=probe` persists the absolute TTL and rollback data before any side
effect. `mode=apply` has no automatic rollback deadline. Both modes use the
same READ-before-WRITE, WRITE, and READ-after-WRITE path.

## Durable WAL And Mutation FSM

Each transition is append-only, hash-linked with RFC 8785/JCS commitments, and
synced before its associated remote side effect:

| State | Durable meaning |
| --- | --- |
| `prepared` | Request, before-image, token binding, constraint decision, rollback data, deadline, and hashes exist; no frame sent. |
| `dispatch_intent` | A WRITE may be sent; durable before send. |
| `reply_observed` | Correlated no-error result observed; application is not proven. |
| `verify_pending` | Full READ-after-WRITE required. |
| `applied` | Readback equals requested typed value. |
| `probe_active` | Applied value is governed by a persisted probe deadline. |
| `rollback_intent` | Rollback ownership and expected current value are durable; no rollback frame sent. |
| `rollback_dispatch_intent` | Rollback WRITE may have been sent. |
| `rollback_reply_observed` | Correlated rollback result observed; restoration is not proven. |
| `rollback_verify_pending` | Full READ-after-rollback required. |
| `rolled_back` | Readback equals the canonical before-image. |
| `no_effect` | Possible-send recovery obtained a trustworthy full READ equal to the verified before-image; no lasting requested state exists at verification time. |
| `outcome_unknown` | Send may have occurred but no trustworthy final observation exists. |
| `conflict` | Current value matches neither permitted convergence value; all writes quarantined. |
| `failed_no_contact` | Failure occurred before any side-effect frame. |
| `rejected` | Correlated rejection plus readback proves no accepted effect. |

`reply_observed` cannot transition directly to `applied`.
`rollback_reply_observed` cannot transition directly to `rolled_back`.
An ACK or successful send is never sufficient.

## Restart And Reconnect Recovery

Crash injection is required after every transition. Recovery rules are:

| Recovered state | Action |
| --- | --- |
| `prepared`, `failed_no_contact` | Send nothing; require fresh binding and lease checks for any new attempt. |
| `dispatch_intent`, `rollback_dispatch_intent`, or possible-send timeout/cancel/disconnect | Enter `outcome_unknown`; never resend blindly; recover only through a trustworthy full READ. |
| `reply_observed`, `verify_pending` | Perform full readback. |
| `applied`, `probe_active` | Re-arm persisted probe deadline when present. |
| expired `probe_active` | Rebind, acquire lease, read current value, then start rollback. |
| `rollback_intent` | Rebind, acquire lease, and READ before any rollback dispatch. |
| `rollback_reply_observed`, `rollback_verify_pending` | Verify restoration by full READ. |
| `rolled_back`, `no_effect`, `rejected`, `failed_no_contact` | Remain terminal. |

After reconnect, a trustworthy full READ equal to the verified before-image
converges a possible-send original WRITE to terminal `no_effect`. Its
`protocol_accepted` remains `null`; `observed_after` is the before-image; its
`OutcomeEvidenceV1` retains `possible_side_effect=true` and
`blind_retry_forbidden=true`; `NoEffectVerificationV1` verifies
`observed_after_equals_before`; and terminal `ErrorV1` is `no_effect` with
`retriable=false`. This proves no lasting requested state at verification
time. It does not prove that the WRITE never transiently executed.

A trustworthy full READ equal to the requested value after an uncertain send
converges to `applied`, or `probe_active` when the persisted probe deadline
still governs it. In that recovery path `protocol_accepted` remains `null`,
`OutcomeEvidenceV1` is retained, and `ApplyVerificationV1` verifies equality
with the requested value. A third value enters `conflict`. Missing,
malformed, stale, cache-derived, identity-mismatched, or otherwise
untrustworthy readback remains `outcome_unknown`.

A correlated protocol rejection remains `rejected` with
`protocol_accepted=false` and `RejectionVerificationV1`; it is never
reclassified as `no_effect`.

## Conflict Quarantine

`conflict` globally disables new writes and rollbacks for the runtime. Feature
discovery, full READ, and mutation status remain available. Quarantine can be
cleared only by an owner-authorized recovery procedure that proves one
coherent current value, records the resolution in the durable audit chain, and
does not reuse a stale token or generation.

## Audit And Data Boundaries

Private mutation records may contain owner-authorized typed before/requested/
after values. Public audit evidence contains only classifications, aggregate
results, transition links, and deterministic commitments. It does not contain
stable identity, feature addresses, payload preimages, private keys, PEM
private material, credential or session tokens, or trust-store bytes.

Raw data never enters `ebus.v1`, the semantic registry, a public MCP result, or
a consumer surface. This architecture adds no GraphQL, Portal, Home Assistant,
semantic promotion, `candidate_ref`, v2, alias, invoke, selector, partial
operation, or `filterDelete` path.
