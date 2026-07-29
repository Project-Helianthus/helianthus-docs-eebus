---
canonical_source: "Project-Helianthus/helianthus-docs-eebus:protocols/_candidate/msp-0625-feature-data-acquisition.md"
owner_domain: "protocols"
license: "CC0-1.0"
publication_status: "candidate"
claim_status: "evidence-backed"
source_class: "derived_inference"
evidence_ids: "EV-20260726-001"
hypothesis_status: "draft"
falsifier: "A publishable source or bounded fake-peer/live run contradicts the full-operation gate, exact target binding, correlated response classification, or typed function-data boundary."
stable_navigation: "false"
search: "false"
sitemap: "false"
versioned_bundle: "false"
release_bundle: "false"
---

# Candidate M6.25 SPINE Feature-Data Acquisition

## Status And Source Boundary

This page is the protocol owner for
[issue 76](https://github.com/Project-Helianthus/helianthus-docs-eebus/issues/76)
as corrected before release by
[issue 78](https://github.com/Project-Helianthus/helianthus-docs-eebus/issues/78),
with additive SPINE transport-handoff evidence tracked by
[issue 80](https://github.com/Project-Helianthus/helianthus-docs-eebus/issues/80)
and canonical full-READ request payload admission corrected by
[issue 86](https://github.com/Project-Helianthus/helianthus-docs-eebus/issues/86).
It distinguishes completed M6 feature topology from M6.25 feature-data
acquisition. Topology says which feature functions and possible operations a
remote reports; it does not contain a fresh value and is not proof that a
READ or WRITE round trip succeeds.

The public source observations used here are:

- Detailed Discovery carries feature address, type, role, supported functions,
  description, and maximum response delay in the public SPINE model
  ([model source](https://github.com/Project-Helianthus/helianthus-spine-go/blob/7383c108f72309c3636d896948d7a8de6d001708/model/networkmanagement.go#L204-L215));
- the public stack projects each supported function's possible full and partial
  READ/WRITE operations
  ([operation projection](https://github.com/Project-Helianthus/helianthus-spine-go/blob/7383c108f72309c3636d896948d7a8de6d001708/spine/feature_remote.go#L79-L90),
  [operation vocabulary](https://github.com/Project-Helianthus/helianthus-spine-go/blob/7383c108f72309c3636d896948d7a8de6d001708/spine/operations.go#L23-L36));
- a READ request is sent with a message counter and a reply/result carries the
  corresponding message-counter reference
  ([request construction](https://github.com/Project-Helianthus/helianthus-spine-go/blob/7383c108f72309c3636d896948d7a8de6d001708/spine/send.go#L153-L190),
  [reply construction](https://github.com/Project-Helianthus/helianthus-spine-go/blob/7383c108f72309c3636d896948d7a8de6d001708/spine/send.go#L240-L261),
  [result construction](https://github.com/Project-Helianthus/helianthus-spine-go/blob/7383c108f72309c3636d896948d7a8de6d001708/spine/send.go#L200-L237)); and
- the public eeBUS client checks the remote READ operation before issuing a
  request, while existing feature-specific writers can emit WRITE requests
  ([READ gate](https://github.com/Project-Helianthus/helianthus-eebus-go/blob/0134afee59535d927d63b78070f828f0f6fb553d/features/client/feature.go#L125-L155),
  [WRITE example](https://github.com/Project-Helianthus/helianthus-eebus-go/blob/0134afee59535d927d63b78070f828f0f6fb553d/features/client/deviceconfiguration.go#L55-L89)); and
- the SPINE sender calls
  `WriteShipMessageWithPayload(message []byte)`, whose writer interface returns
  no delivery result
  ([writer call](https://github.com/Project-Helianthus/helianthus-spine-go/blob/b21400335be90ea95a6cad5f512d1c8e22f2cdeb/spine/send.go#L69-L112),
  [transport interface](https://github.com/Project-Helianthus/helianthus-ship-go/blob/3abd41d19f419de907bc1bdf2a126ca19c930626/api/shipconnection.go#L195-L200)); and
- eebusreg v0.1.20 converts the actual dispatched full-READ command and its
  correlated reply to canonical typed values, preserving them as
  `raw_request.data` and `raw_response.data`
  ([runtime projection](https://github.com/Project-Helianthus/helianthus-eebusreg/blob/63e43d94024d101cea882697acb5436a3b51fc77/internal/eebusfacade/raw_feature_runtime.go#L737-L768)),
  while its result validator preserves the response, value, function, and
  correlation checks but also rejects every non-nil request payload
  ([validator contradiction](https://github.com/Project-Helianthus/helianthus-eebusreg/blob/63e43d94024d101cea882697acb5436a3b51fc77/eebusraw/contract_validation_v1.go#L457-L484)).

These source observations establish available public primitives, not the
unimplemented Helianthus M6.25 guarantees. Every requirement below is a
normative Helianthus design hypothesis until the fake-peer, race, restart, and
bounded live gates falsify it. No non-public specification establishes a claim
on this page.

The owning architecture, API, and provenance pages are
[msp-0625-raw-feature-command-path.md](../../architecture/_candidate/msp-0625-raw-feature-command-path.md),
candidate API owner `msp-0625-raw-feature-acquisition.md`,
and
[msp-0625-provenance-policy.md](../../development/msp-0625-provenance-policy.md).

## Closed Operation Set

M6.25 supports full `READ` and full `WRITE` only. It does not expose partial
operations, selectors, element projections, `filterDelete`, calls, or invoke.
The exact operation gate is:

| Requested operation | Required remote declaration | M6.25 result |
| --- | --- | --- |
| Full `READ` | function possible operations contains full READ | One correlated typed READ may be dispatched. |
| Full `WRITE` | function possible operations contains full WRITE and the changeability/constraint gate passes | One correlated typed WRITE may be dispatched under the mutation coordinator. |
| Partial READ or WRITE | any declaration | `unsupported_operation` before remote contact. |
| Any other classifier | any declaration | `unsupported_operation` before remote contact. |

The executor does not infer WRITE from feature type, sibling functions, local
use-case registration, a prior session, or device family. A missing function
or possible-operation declaration is unsupported, not an empty success.

## Exact Feature And Function Target

Every READ, WRITE, reply, result, read token, mutation, rollback, and audit
commitment binds the same closed target:

- remote SKI and SHIP ID;
- SPINE device, entity, and feature address;
- feature type and native role;
- exact function;
- exact operation; and
- `runtime_epoch` plus `connection_generation`.

Both remote SKI and SHIP ID are operational identity on the owner-authorized
raw surface. Neither is publishable public evidence. A stale generation,
different identity, changed address, changed function, changed operation, or
different canonical request shape cannot be rebound to the request.

## Feature And Function Discovery

For each exact feature, discovery returns:

- feature identity, address, type, native role, and optional description;
- the current function inventory;
- each function's declared full READ and full WRITE availability;
- known changeability properties;
- known enum, range, step, unit, cardinality, and cross-field constraints; and
- an explicit `constraints_unknown` classification when a complete constraint
  set is unavailable.

Discovery may be topology/cache sourced and carries its data timestamp. A
feature-data READ is always a live correlated round trip; cached function data
cannot satisfy it or mint a current read token.

## Full READ

A READ request contains exactly one function and no selector or filter. A
bounded `features.data.get` call may contain 1 through 16 exact targets. Each
target gets an independent correlated round trip and result. Ordering in the
response equals request order. The machine contract binds every request,
successful observation, and per-target failure to `ReadFeatureTargetV1`, whose
operation is the constant `READ`.

The runtime, not the caller, constructs the actual function-specific full-READ
command after exact-target admission. Its canonical typed command payload may
be absent or preserved in `raw_request.data`; it is not required to be null.
This result-side evidence does not add any caller-supplied selector, element,
filter, or partial-mode field to `FeatureDataGetRequestV1`.

A successful observation contains:

- the exact target and runtime binding;
- canonical typed request and response objects;
- typed function data plus bounded unknown fields;
- `requested_at`, `received_at`, and `data_timestamp`;
- source `live`;
- a deterministic JCS/SHA-256 commitment; and
- a bound `read_token`.

The raw request remains classifier `READ` with no error number. The raw
response remains classifier `REPLY` with no error number and required non-null
typed function data. Both messages retain the same correlation key and exact
target function, and the response data remains canonically equal to the
observation value. Request payload admission changes none of those
`ValidateFeatureDataGetDataV1` invariants.

The payload is visible only on the owner-authorized raw surface, is recursively
subject to the existing cryptographic-secret exclusion, and is absent from
public/redacted evidence.

If some targets succeed and another fails, the call reports
`partial_result`, preserves each completed result in request order, and lists
each failed target with a structured error. It never converts a missing target
or missing payload into an empty successful value.

## Full WRITE And Verification

A WRITE carries one exact target and one complete typed function-data value.
The coordinator first performs a fresh full READ under the global writer
lease. The fresh value must match the read token's canonical before-image and,
when supplied, `expected_current`. Only then may a full WRITE be sent.

A correlated no-error result means `protocol_accepted=true`. It does not prove
the value applied. The mutation reaches `applied` only when a subsequent full
READ returns a canonical value equal to the requested value. The same rule
applies to rollback: a no-error result does not prove restoration, and
`rolled_back` requires a full READ equal to the recorded before-image.

When a crash, timeout, cancellation, or disconnect leaves send uncertain,
there is no correlated acceptance fact and `protocol_accepted` remains
`null`. A trustworthy recovery READ equal to the requested value may still
prove `applied`, or `probe_active` for a governed probe, only when the record
retains possible-side-effect/blind-retry-forbidden uncertainty evidence and
verified equality with the requested value.

The acquisition record distinguishes:

- `before`;
- `requested`;
- `protocol_accepted`; and
- `observed_after`.

No successful result field is synthesized when any of those observations is
absent.

## Correlated Round-Trip Rule

The new spine-go primitive is one atomic, context-aware operation:

1. allocate a monotonic correlation key bound to the admitted connection
   generation;
2. register the waiter before send;
3. send only after registration succeeds;
4. complete exactly once from the correlated reply/result, send failure,
   cancellation, timeout, disconnect, malformed response, or remote error;
5. remove the live waiter on every terminal path; and
6. retain a bounded generation tombstone so a late response cannot complete an
   ABA successor.

The implementation must tolerate a response delivered synchronously during
the send call. Reply/result admission is generation ordered. A prior
generation can neither satisfy nor cancel a current request. Correlated
application results preserve dispatch order at the coordinator boundary even
when independent reads execute concurrently.

Every terminal round-trip error carries one operation-scoped
`DispatchDisposition`:

| Disposition | Protocol evidence |
| --- | --- |
| `NoTransportHandoff` | The SHIP writer was not invoked for this correlated operation. |
| `TransportHandoffPossible` | Writer invocation began, or the operation had entered correlation wait. |

The exported `CorrelatedRoundTripError` carries the original `Cause` and the
disposition, and its `Unwrap` returns that cause. Existing `errors.Is` checks
for sentinels or context errors and `errors.As` checks for existing typed
causes remain compatible. Callers use `errors.As` to read the disposition; the
existing signature remains
`RoundTrip(ctx context.Context, request CorrelatedRequest)
(CorrelatedResponse, error)`.

Pre-cancel, invalid request, capacity/counter/key admission, marshal,
missing-writer, and all other failures before writer invocation are
`NoTransportHandoff`. Cancellation, timeout, close, disconnect, remote
rejection, malformed response, and every other failure after writer entry are
`TransportHandoffPossible`. An untyped error, absent wrapper, nil cause, zero
value, or unknown disposition is conservatively
`TransportHandoffPossible`.

Because the SHIP writer returns no result, `TransportHandoffPossible` is not
proof of bytes on the wire. It also does not prove peer receipt, a correlated
acceptance, or a remote state change. Only later protocol correlation and
verified full readback can establish those stronger facts.

The current public stack exposes separate send and callback-registration
operations
([send surface](https://github.com/Project-Helianthus/helianthus-spine-go/blob/7383c108f72309c3636d896948d7a8de6d001708/api/sender.go#L12-L35),
[callback surface](https://github.com/Project-Helianthus/helianthus-spine-go/blob/7383c108f72309c3636d896948d7a8de6d001708/api/feature.go#L45-L52)).
Therefore the atomic waiter-before-send primitive is a proven public-source
gap in spine-go for this contract. Existing SHIP framing and transport remain
unchanged; no ship-go change is authorized.

## Constraints And Probe Safety

WRITE fails before dispatch unless:

- full WRITE is declared;
- the target is changeable;
- every known constraint passes;
- a representable full-WRITE before-image exists;
- the exact target is lab-allowlisted;
- runtime safety predicates are green; and
- the global writer lease, read token, epoch, and generation remain current.

`constraints_unknown` fails closed. A local owner may proceed only through a
versioned exact-target lab profile that fixes permitted values or bounds,
probe TTL, safety predicates, and rollback shape. Wildcards and sibling or
device-family inheritance are forbidden.

`mode=apply` leaves a verified value applied. `mode=probe` persists an absolute
TTL before dispatch and requires automatic verified rollback by that deadline,
including across restart.

## Production Lab Profile Activation

The production exception contract is
`helianthus.eebus.raw-mutation-lab-profile.v1`. It is disabled by absence and
does not infer permission from a device family, sibling feature, declared
WRITE operation, or MCP request. One profile binds one exact target, permitted
value hashes, rollback value hash, maximum probe TTL, safety predicates,
publishable evidence commitments, and absolute expiry.

The gateway loads the first production slice only from the owner-controlled
regular file
`/data/eebus/eebusmutation/mutation-lab-profile-v1.json`. The state root and
its existing protected raw-mutation subtree are mode `0700`; the profile is
mode `0600`, owned by the gateway identity, and its complete byte stream is at
most `65536` bytes. No alternate root-level, legacy, CLI, or environment path
exists, and the association-store top-level whitelist remains unchanged. The
file contains exactly one JSON object: one `MutationLabProfileV1`, not an
array, stream, wrapper, or concatenation. It is parsed as closed JSON. Unknown
keys, duplicate keys, trailing JSON values, and non-canonical field forms are
rejected; duplicate object keys are rejected at every depth. Symbolic links
are rejected, every parent is checked without following links, and profile
content is forbidden in environment variables and process arguments. A
missing file is the normal disabled state. An invalid, over-permissive,
duplicated, or expired profile prevents mutation activation without preventing
the read-only runtime from starting.

An exact profile may attest lab-only changeability and complete constraints
only when the remote declares full WRITE, the profile binds the current live
capability evidence, both the requested and rollback hashes match, and every
safety predicate is green. The request's `constraints_override` selects one
already-loaded profile and supplies a bounded justification and earlier
expiry; it cannot create, widen, or persist a profile.

The protected owner file therefore contains exactly one profile when present.
The runtime may carry up to `16` immutable validated profiles internally for
future composition, but that capacity does not widen the first gateway file
format or its disabled-by-absence default.

Profile expiry denies every new write. It cannot prevent recovery or rollback
of a mutation that already has a durable `dispatch_intent`, `probe_active`, or
rollback state. Recovery uses the persisted exact target, before-image,
requested value, absolute probe deadline, and commitments; it never converts
profile expiry into permission for a new forward mutation.

## Structured Terminal Outcomes

The contract represents at least these outcomes explicitly:

| Class | Required result |
| --- | --- |
| Invalid target/shape, unsupported operation, stale binding, CAS mismatch, scope denial, lease conflict, constraint failure, or explicit original-WRITE `NoTransportHandoff` | `failed_no_contact` and zero WRITE frames for that operation |
| Original-WRITE `TransportHandoffPossible`, unknown/untyped dispatch error, or loss of trustworthy observation after writer entry | `outcome_unknown` from `dispatch_intent`; blind retry forbidden |
| Rollback-WRITE `NoTransportHandoff` | Zero rollback handoff for that attempt; preserve the original effect, do not claim `rolled_back`, and require fresh guarded recovery before another rollback dispatch |
| Rollback-WRITE `TransportHandoffPossible` or unknown/untyped rollback dispatch error | `outcome_unknown` from `rollback_dispatch_intent`; blind retry forbidden |
| Remote correlated rejection with no changed readback | `rejected` |
| Trustworthy recovery READ after possible send equals the verified before-image | `no_effect`, with `protocol_accepted=null`, retained uncertainty evidence, and non-retriable `no_effect` error |
| Trustworthy recovery READ after possible send equals the requested value | `applied` or governed `probe_active`, with `protocol_accepted=null`, retained uncertainty evidence, and verified requested-value equality |
| Readback differs from both expected values | `conflict` and global write quarantine |
| Some bounded READ targets fail | `partial_result` with per-target structured errors |
| Decode failure or malformed correlated response | `decode_error`; never empty success |
| Rollback cannot be verified | `rollback_failed`, `outcome_unknown`, or `conflict`; never `rolled_back` |

`outcome_unknown` is resolved only by a trustworthy fresh full READ after
identity and generation rebind. Blind resend is forbidden. Before-image
equality produces `NoEffectVerificationV1` with relation
`observed_after_equals_before`, `verified=true`, one recomputed
`equal_value_hash`, and `verified_at`. `no_effect` proves that the requested
state did not persist through verification time; it does not prove the WRITE
never transiently executed.

Requested-value equality uses `ApplyVerificationV1` and retains uncertainty
evidence. Any third value enters `conflict` and quarantines all writes while
preserving reads and mutation status. Missing, malformed, stale,
cache-derived, identity-mismatched, or otherwise untrustworthy readback
remains `outcome_unknown`. A correlated rejection remains `rejected` and is
not reclassified by the possible-send recovery rules.

Authorization is also operation-specific above the protocol executor:
`FeaturesDataSet` and `MutationsRollback` require the distinct public
`WriteAuthorizationV1` validated by `ValidateWriteAuthorizationV1` with
`AuthScopeV1RawWrite`; `MutationsGet` remains under the unchanged
`ReadAuthorizationV1` path. The public read-only `RawFeatureRuntimeV1` and
existing `Runtime` method set remain unchanged; mutation methods live on the
separate public `RawMutationRuntimeV1`, while the coordinator remains
internal.

## Scope Exclusions

This protocol contract adds no v2 namespace, alias, compatibility surface,
semantic fact, candidate reference, GraphQL field, Portal model, Home
Assistant entity, or consumer command. M6 remains complete. M6.5 live
acquisition and candidate-only M7 or later work remain blocked on the M6.25
implementation and live gate.
