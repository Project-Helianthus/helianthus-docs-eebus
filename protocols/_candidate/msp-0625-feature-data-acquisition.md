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
[issue 78](https://github.com/Project-Helianthus/helianthus-docs-eebus/issues/78).
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
  [WRITE example](https://github.com/Project-Helianthus/helianthus-eebus-go/blob/0134afee59535d927d63b78070f828f0f6fb553d/features/client/deviceconfiguration.go#L55-L89)).

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
response equals request order.

A successful observation contains:

- the exact target and runtime binding;
- canonical typed request and response objects;
- typed function data plus bounded unknown fields;
- `requested_at`, `received_at`, and `data_timestamp`;
- source `live`;
- a deterministic JCS/SHA-256 commitment; and
- a bound `read_token`.

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

## Structured Terminal Outcomes

The contract represents at least these outcomes explicitly:

| Class | Required result |
| --- | --- |
| Invalid target/shape, unsupported operation, stale binding, CAS mismatch, scope denial, lease conflict, or constraint failure before send | `failed_no_contact` and zero WRITE frames |
| Remote correlated rejection with no changed readback | `rejected` |
| Send may have occurred but cancellation, timeout, disconnect, or restart prevents trustworthy observation | `outcome_unknown` |
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
