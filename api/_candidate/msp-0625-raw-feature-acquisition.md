---
canonical_source: "Project-Helianthus/helianthus-docs-eebus:api/_candidate/msp-0625-raw-feature-acquisition.md"
owner_domain: "api"
license: "AGPL-3.0-only"
publication_status: "candidate"
claim_status: "evidence-backed"
source_class: "derived_inference"
evidence_ids: "EV-20260711-001,EV-20260726-001"
hypothesis_status: "draft"
falsifier: "Contract, fake-peer, race, crash-injection, authorization, or live tests require a different five-tool shape, scope split, durable mutation state, or zero-contact public denial."
candidate_output: "true"
stable_navigation: "false"
search: "false"
sitemap: "false"
versioned_bundle: "false"
release_bundle: "false"
candidate_output_path: "api/_candidate/msp-0625-raw-feature-acquisition.md"
---

# Candidate M6.25 Raw Feature MCP Contract

## Additive API Boundary

This candidate is tracked by
[issue 76](https://github.com/Project-Helianthus/helianthus-docs-eebus/issues/76)
and corrected before release by
[issue 78](https://github.com/Project-Helianthus/helianthus-docs-eebus/issues/78).
The additive SPINE dependency evidence is tracked by
[issue 80](https://github.com/Project-Helianthus/helianthus-docs-eebus/issues/80).
It adds raw typed feature-data acquisition to the unreleased `eebus.v1`
namespace. It does not modify or reclassify the nine M6 read-only tools or
their raw/redacted profiles.

The owning protocol, architecture, and provenance pages are
[msp-0625-feature-data-acquisition.md](../../protocols/_candidate/msp-0625-feature-data-acquisition.md),
[msp-0625-raw-feature-command-path.md](../../architecture/_candidate/msp-0625-raw-feature-command-path.md),
and
[msp-0625-provenance-policy.md](../../development/msp-0625-provenance-policy.md).
The closed machine contract is
[helianthus.eebus.mcp.v1.raw-feature.schema.json](msp-0625/helianthus.eebus.mcp.v1.raw-feature.schema.json).

This page is candidate-only. It asserts no deployed tool, successful live
READ/WRITE, semantic fact, or consumer availability.

## Exact Tool Inventory

The new suffix set is exactly:

```json
["features.get","features.data.get","features.data.set","mutations.get","mutations.rollback"]
```

| Tool | Required scope | Remote contact | Request | Data |
| --- | --- | --- | --- | --- |
| `eebus.v1.features.get` | `eebus.raw.read` | no; topology/runtime view only | `FeaturesGetRequestV1` | `FeaturesGetDataV1` |
| `eebus.v1.features.data.get` | `eebus.raw.read` | yes; full READ | `FeatureDataGetRequestV1` | `FeatureDataGetDataV1` |
| `eebus.v1.features.data.set` | `eebus.raw.write` | yes; guarded full WRITE | `FeatureDataSetRequestV1` | `MutationV1` |
| `eebus.v1.mutations.get` | `eebus.raw.read` | no; durable coordinator view | `MutationGetRequestV1` | `MutationV1` |
| `eebus.v1.mutations.rollback` | `eebus.raw.write` | conditional; guarded rollback path | `MutationRollbackRequestV1` | `MutationV1` |

There is no v2, alias, legacy name, generic command endpoint, or second
namespace. `candidate_ref`, partial operations, selectors, `filterDelete`,
invoke, GraphQL, Portal, Home Assistant, semantic promotion, v2, aliases, and
legacy compatibility are out of scope.

## Boundary And Authorization

All five tools exist only on the owner-authorized `AF_UNIX` raw surface with
`mask_tier=raw`. Tool scope is fixed by the table and cannot be selected by a
request field, header, query parameter, reference, principal label, or
payload.

The public/LAN MCP boundary exposes none of the five tools. A public call using
one of the names fails as `permission_denied` after JSON-RPC/tool shape and
boundary/scope checks but before provider lookup, `EEBusCommandRouter`,
the selected raw runtime interface, the internal durable coordinator,
connection lookup, or remote contact. Contract tests require zero calls at
each downstream boundary and zero frames.

The existing public `RawFeatureRuntimeV1` remains read-only and byte-compatible
at the Go method-set level:

```go
type RawFeatureRuntimeV1 interface {
    FeaturesGet(context.Context, eebusraw.ReadAuthorizationV1, eebusraw.FeaturesGetRequestV1) (eebusraw.FeaturesGetDataV1, *eebusraw.ErrorV1)
    FeaturesDataGet(context.Context, eebusraw.ReadAuthorizationV1, eebusraw.FeatureDataGetRequestV1) (eebusraw.FeatureDataGetDataV1, *eebusraw.ErrorV1)
}
```

M6.25 adds a separate public mutation capability:

```go
type RawMutationRuntimeV1 interface {
    FeaturesDataSet(context.Context, eebusraw.WriteAuthorizationV1, eebusraw.FeatureDataSetRequestV1) (eebusraw.MutationV1, *eebusraw.ErrorV1)
    MutationsGet(context.Context, eebusraw.ReadAuthorizationV1, eebusraw.MutationGetRequestV1) (eebusraw.MutationV1, *eebusraw.ErrorV1)
    MutationsRollback(context.Context, eebusraw.WriteAuthorizationV1, eebusraw.MutationRollbackRequestV1) (eebusraw.MutationV1, *eebusraw.ErrorV1)
}
```

The existing public `Runtime` method set remains unchanged and does not embed
`RawMutationRuntimeV1`. Concrete runtime implementations may satisfy both.
The gateway later capability-asserts `RawMutationRuntimeV1` and fails closed
when absent. The durable coordinator remains internal.

```go
type Runtime interface {
    RawFeatureRuntimeV1
    Start(context.Context) error
    Shutdown() error
    Snapshot() (SnapshotV1, error)
    PairingState() ([]PairingObservationV1, error)
}
```

`ReadAuthorizationV1`, `AuthScopeV1RawRead`, and
`ValidateReadAuthorizationV1` retain their existing names, identity, and
read-only purpose; no alias or rename is introduced. The public
`WriteAuthorizationV1` is a distinct type, uses
`AuthScopeV1RawWrite = "eebus.raw.write"`, and is validated by
`ValidateWriteAuthorizationV1`. `FeaturesDataSet` and `MutationsRollback`
require it. `MutationsGet` remains read-authorized.

Owner authorization permits real local SHIP/SPINE identity, addresses,
feature/function metadata, typed values, and bounded unknown fields. It never
permits private keys, PEM private material, credential/bearer/session/
authentication tokens, cryptographic secrets, or trust-store bytes. A
`read_token`, `mutation_ref`, and `idempotency_key` are purpose-bound contract
values; they are not credential material and may appear only in their
designated fields.

## Common Target And Runtime Binding

`FeatureTargetV1` requires:

| Field | Type | Rule |
| --- | --- | --- |
| `FeatureTargetV1.remoteSKI` | non-empty string | Exact owner-authorized remote identity. |
| Protocol-service identity field | non-empty string | Exact owner-authorized identity carried by `FeatureTargetV1`. |
| `device_address` | non-empty string | Exact SPINE device address. |
| `entity_address` | array of safe non-negative integers | Exact complete entity path. |
| `feature_address` | safe non-negative integer | Exact feature address. |
| `feature_type` | non-empty string | Must match current topology. |
| `feature_role` | `client`, `server`, or `special` | Native role; no lossy substitution. |
| `function` | non-empty string | Exact typed function name. |
| `operation` | `READ` or `WRITE` | Must match the tool and possible-operation gate. |

`RuntimeBindingV1` requires positive `runtime_epoch` and
`connection_generation`. The server supplies this binding in results and
tokens. A caller cannot override a current binding.

## `features.get`

The closed request is `FeaturesGetRequestV1 { target: FeatureLocatorV1 }`.
The locator carries the operational identity and complete SPINE feature
address defined above; this public document intentionally provides no sample
identity or address value.

The response returns `FeatureFunctionV1` with the exact target, optional
description, full READ/WRITE possible operations, changeability, constraints,
topology source, data timestamp, runtime binding, and deterministic hash.
`features.get` may report topology/cache data; it does not perform a function
READ and does not mint a read token.

## `features.data.get`

The closed request is
`FeatureDataGetRequestV1 { targets: FeatureTargetV1[1..16], timeout_ms? }`.
This public document provides no sample target value.

`targets` contains 1 through 16 exact full-READ targets. `timeout_ms` is
bounded by server policy. No target accepts selectors, elements, filters, or a
partial mode.

Each `ReadObservationV1` binds:

- target and runtime epoch/connection generation;
- canonical typed raw request, raw response, payload, and bounded unknown
  fields;
- `requested_at`, `received_at`, and `data_timestamp`;
- source `live`;
- deterministic `data_hash`; and
- `ReadTokenV1`.

Results preserve request order. A mixed bounded result sets `complete=false`,
retains completed observations, adds per-target structured failures, and uses
error code `partial_result`. Empty or missing data is never a successful
observation.

The read token binds principal class, scope, tier, tool, target, request shape,
runtime epoch, connection generation, before-image hash, expiry, and a
function profile that says one-use or reusable. It is rejected on any
substitution.

## `features.data.set`

Request shape, with the exact target intentionally represented by its type
rather than a populated public example:

```json
{
  "target": "<FeatureTargetV1>",
  "value": {"<typed-function-data>": "<complete-value>"},
  "read_token": "<opaque-bound-value>",
  "expected_current": {"<typed-function-data>": "<optional-complete-value>"},
  "idempotency_key": "<caller-stable-key>",
  "mode": "probe",
  "probe_ttl_seconds": 60
}
```

`target`, `value`, `read_token`, `idempotency_key`, and `mode` are required.
`expected_current` is optional but, when present, is part of the CAS guard.
`probe_ttl_seconds` is required for `mode=probe` and forbidden for
`mode=apply`.

`constraints_override` is accepted only as an explicit versioned lab profile
containing exact profile id, justification, and expiry. The coordinator must
already hold the profile's exact target/value bounds, safety predicates,
rollback shape, and maximum TTL; request data cannot create or widen a profile.

The response is the durable `MutationV1`. A correlated no-error response sets
`protocol_accepted=true` but cannot set state `applied`. A full readback equal
to `requested` is required.

## Operation-Scoped Transport-Handoff Evidence

The additive spine-go dependency API defines exactly two dispositions:

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
```

Every terminal error from one correlated operation is a non-nil
`*CorrelatedRoundTripError` with a non-nil `Cause` and one of the two
dispositions. `Unwrap` returns `Cause`, so existing checks such as
`errors.Is(err, context.Canceled)`,
`errors.Is(err, ErrCorrelatedRoundTripClosed)`, and `errors.As` for existing
typed causes continue to work. `errors.As(err, &roundTripError)` exposes the
operation's disposition without string or sentinel inference.

The existing interface method remains unchanged:

```go
RoundTrip(ctx context.Context, request CorrelatedRequest) (CorrelatedResponse, error)
```

`NoTransportHandoff` means the SHIP writer was not invoked for that operation.
`TransportHandoffPossible` means writer invocation began or the operation was
already awaiting correlation. It does not prove bytes reached the wire, a
remote peer received data, or the protocol accepted or applied a value. The
SHIP writer method returns no delivery result, so SPINE cannot make any
stronger transport claim after invocation.

The coordinator may use `NoTransportHandoff` as zero-contact evidence only for
that exact original or rollback dispatch. An untyped error, a missing typed
error, or an unknown disposition is always classified conservatively as
`TransportHandoffPossible`. This dependency evidence is internal input to the
existing mutation FSM; it adds no field, enum, tool, or envelope variant to the
candidate MCP machine contract.

## `mutations.get`

Request:

```json
{"mutation_ref":"<opaque-bound-value>"}
```

The reference is bound to runtime epoch, principal, raw tier, authorization
boundary, and originating mutation. Cross-principal, cross-tier, cross-epoch,
or public dereference is `permission_denied`. Status reads never dispatch a
remote frame.

`MutationV1` contains:

- mutation reference, state, mode, target, and runtime binding;
- `before`, `requested`, `protocol_accepted`, and `observed_after`;
- optional rollback record and probe deadline;
- created/updated timestamps;
- structured terminal error when present; and
- public-safe, transition-linked audit commitments.

`MutationV1.oneOf` discriminates every state. In the ordinary correlated
acceptance path, `applied` requires `protocol_accepted=true`; possible-send
recovery uses `protocol_accepted=null` only with retained uncertainty evidence.
Both paths require a non-null `observed_after` and a closed
`ApplyVerificationV1` whose relation is `observed_after_equals_requested`;
its single equality commitment is the RFC 8785/JCS SHA-256 hash recomputed for
both values. `rolled_back` requires the prior apply verification plus a
`RollbackV1` with non-null rollback readback and `RollbackVerificationV1`
relation
`rollback_observed_after_equals_before`. The equality commitment is likewise
recomputed for both the rollback readback and canonical before-image.

`no_effect`, `outcome_unknown`, `conflict`, `failed_no_contact`, and
`rejected` require their closed evidence records and matching structured
errors.
`failed_no_contact` evidence fixes `remote_frames_sent=0`; `rejected` requires
a correlated rejection plus verified readback equal to `before`; `conflict`
commits distinct before, requested, and observed hashes; and
`outcome_unknown` records the last possible-side-effect intent and forbids
blind retry. Evidence relations are runtime assertions: the boundary
recomputes every named hash and rejects a false relation rather than trusting
caller-supplied commitments.

Possible-send recovery with a trustworthy full READ equal to `before` is
terminal `no_effect`. It requires `protocol_accepted=null`,
`observed_after=before`, retained `OutcomeEvidenceV1` with
`possible_side_effect=true` and `blind_retry_forbidden=true`, and closed
`NoEffectVerificationV1 { relation:
"observed_after_equals_before", verified: true, equal_value_hash,
verified_at }`. Its terminal `ErrorV1` has `code=no_effect` and
`retriable=false`. This proves no lasting requested state at verification
time, not that the WRITE never transiently executed.

Possible-send recovery with trustworthy readback equal to `requested`
converges to `applied`, or `probe_active` for a still-governed probe, with
`protocol_accepted=null`, retained `OutcomeEvidenceV1`, and verified
`ApplyVerificationV1`. A third value is `conflict`. Missing or untrustworthy
readback remains `outcome_unknown`. A correlated rejection remains
`rejected`, with `protocol_accepted=false`; it is not `no_effect`.

The full state enum is:

```text
prepared
dispatch_intent
reply_observed
verify_pending
applied
probe_active
rollback_intent
rollback_dispatch_intent
rollback_reply_observed
rollback_verify_pending
rolled_back
no_effect
outcome_unknown
conflict
failed_no_contact
rejected
```

## `mutations.rollback`

Request:

```json
{
  "mutation_ref": "<opaque-bound-value>",
  "idempotency_key": "<caller-stable-key>"
}
```

The explicit rollback uses the same global writer lease and verified path as
probe expiry. It checks exact binding, performs a fresh full READ, records
rollback intent before side effect, writes the complete before-image, and
performs a full READ-after-rollback. An already restored before-image converges
to `rolled_back` without another WRITE. The requested value permits rollback
dispatch. Any third value enters `conflict` and quarantines writes.

## Mutation Durability And Idempotency

The durable coordinator writes and syncs the WAL before each possible remote
side effect. Idempotency identity is:

```text
(runtime_epoch, principal, tool, idempotency_key)
```

The record also binds the canonical request JCS hash. Same identity and same
hash return the original mutation and emit no second frame. Same identity and
different hash returns `idempotency_conflict`.

One global runtime writer lease covers new writes, explicit rollback,
probe-expiry rollback, and recovery. A different writer receives
`writer_busy`; it cannot interleave or queue without a bound.

## Error Envelope

`EnvelopeV1.oneOf` discriminates on `meta.tool` and fixes `meta.scope`,
`meta.auth_scope`, the exact closed `request`, and the exact response `data`
type for that tool. A success has non-null typed `data` and `error=null`; a
failure has `data=null` and non-null `ErrorV1`. Both-null and ordinary
data-plus-error envelopes are invalid. The sole data-plus-error variant is
`eebus.v1.features.data.get` with code `partial_result`, whose data retains
completed target results and per-target failures.

`ErrorV1` has exactly `code`, `message`, `retriable`, `source_layer`, and
optional public-safe `details`. Backend text, payload preimages, and
secret-classified values never enter `message` or `details`.

The closed error vocabulary includes:

| Code | Meaning |
| --- | --- |
| `invalid_argument` | Closed shape or exact target is invalid. |
| `permission_denied` | Scope, boundary, tier, principal, or reference binding failed. |
| `unsupported_operation` | Full READ/WRITE is not declared or requested classifier is out of scope. |
| `partial_operation_forbidden` | Selector/filter/partial behavior was requested. |
| `constraints_unknown` | Complete constraints are unavailable and no exact profile applies. |
| `constraint_failure` | Known constraint, changeability, allowlist, or safety predicate failed. |
| `stale_read_token` | Read token expired or no longer binds current context. |
| `cas_mismatch` | Fresh before-image differs; zero WRITE frames. |
| `runtime_epoch_mismatch` | Durable runtime identity changed. |
| `connection_generation_mismatch` | Admitted SPINE connection changed. |
| `idempotency_conflict` | Same key was reused with a different canonical request. |
| `writer_busy` | Another global writer owns the bounded lease. |
| `timeout`, `cancelled`, `disconnected` | Round trip ended without a trusted correlated result. |
| `remote_error` | Correlated remote rejection/error. |
| `decode_error` | Correlated response is malformed or cannot produce typed data. |
| `partial_result` | Some bounded READ targets failed. |
| `no_effect` | Possible-send recovery verified the before-image; non-retriable because blind resend remains forbidden. |
| `outcome_unknown` | A side effect may have occurred; blind retry forbidden. |
| `conflict` | Readback matches neither allowed convergence value; writes quarantined. |
| `rollback_failed` | Restoration could not be verified. |
| `not_found` | Well-formed mutation reference is unknown after binding checks. |
| `secret_detected` | A secret-classified field/value failed closed before output or hashing. |
| `internal` | Fixed public-safe internal failure. |

Timeout, cancellation, disconnect, malformed response, and late response all
clean up the live waiter. A bounded generation tombstone remains to prevent
late-response ABA.

## Determinism And Evidence

RFC 8785/JCS canonical JSON and SHA-256 commit request, before-image, requested
value, observations, rollback value, and transition links. Non-finite numbers
and negative zero are forbidden. Exact decimals and integers outside the
portable JSON safe range are strings.

Local operator responses may contain the real typed values and operational
identity. Public evidence is a separate redacted projection bound to public
authorization and tier. It may expose classifications, aggregate results,
timestamps, and commitments, but never the raw target, typed preimages, stable
identity, or secret material. No raw result is copied into `ebus.v1`, a
semantic registry, or a consumer surface.

Before hashing, reference creation, audit insertion, or error rendering, the
boundary recursively traverses every typed object, array, and scalar. Field
names are normalized by Unicode NFKC, insertion of `_` at each ASCII
lowercase-or-digit to uppercase transition, replacement of every remaining
run outside `[A-Za-z0-9]` by `_`, ASCII lowercase conversion, underscore
collapse, and leading/trailing underscore removal. A field is rejected when
that normalized name, or the same name with underscores removed, equals a
member of `x-secret-denylist`. String values are Unicode-NFKC normalized and
trimmed, then rejected when they contain a case-insensitive PEM private-key
boundary or begin with a case-insensitive bearer scheme followed by a
non-empty credential. Other bounded unknown names and values remain
inspectable raw data.
