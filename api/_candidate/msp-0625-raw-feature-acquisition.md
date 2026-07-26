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
[issue 76](https://github.com/Project-Helianthus/helianthus-docs-eebus/issues/76).
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
`RawFeatureRuntimeV1`, the durable coordinator, connection lookup, or remote
contact. Contract tests require zero calls at each downstream boundary and
zero frames.

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

Every tool uses the existing v1 success/error exclusivity except the explicit
bounded `partial_result`, whose data retains completed target results and
per-target failures. `ErrorV1` has exactly `code`, `message`, `retriable`,
`source_layer`, and optional public-safe `details`. Backend text, payload
preimages, and secret-classified values never enter `message` or `details`.

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
