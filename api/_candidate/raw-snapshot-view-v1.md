---
canonical_source: "Project-Helianthus/helianthus-docs-eebus:api/_candidate/raw-snapshot-view-v1.md"
owner_domain: "api"
license: "AGPL-3.0-only"
publication_status: "candidate"
claim_status: "evidence-backed"
source_class: "derived_inference"
evidence_ids: "EV-20260711-001"
hypothesis_status: "draft"
falsifier: "The reviewed MSP-036 implementation or normalized API manifest differs from this candidate inventory."
candidate_output: "true"
stable_navigation: "false"
search: "false"
sitemap: "false"
versioned_bundle: "false"
release_bundle: "false"
candidate_output_path: "api/_candidate/raw-snapshot-view-v1.md"
---

# Candidate Immutable Raw Snapshot/View v1

This page is the docs-first candidate for MSP-036. It is not a supported API
reference and does not assert deployed runtime behavior. A later normalized API
manifest must either match this candidate or falsify it before publication.

The issue-68 [raw operator and shareable redaction amendment](msp-068-raw-operator-redaction-amendment.md)
corrects the authorized local MCP boundary without changing this candidate's
historical public Go API inventory. The amendment retains the one initial MCP
`eebus.v1.*` namespace and introduces neither a v2 nor an alias.

## Boundary

MSP-036 may add immutable raw data values to the public `eebusruntime` package.
It may not add a runtime owner, a mutable view, transport dispatch, trust or
pairing mutation, semantic identity, consumer routing, or availability
authority.

The snapshot reports observations. A state, pairing, visibility, connection,
or degradation value is evidence about the captured instant only. It is not a
lifecycle decision, a trust decision, or a promise that the value remains
current after `data_timestamp`.

## Candidate Type Inventory

All newly exported data types are suffixed `V1`. The candidate inventory is:

| Type | Fields |
| --- | --- |
| `SnapshotV1` | `Meta`, `Status`, `Pairing`, `Services`, `Sessions`, `Devices`, `Entities`, `Features`, `UseCases`, `Opaque` |
| `RedactedSnapshotV1` | `Meta`, `Status`, `Pairing`, `Services`, `Sessions`, `Devices`, `Entities`, `Features`, `UseCases` |
| `SnapshotMetaV1` | `Contract`, `Runtime`, `LocalSKI`, `MaskTier`, `CapturedAt`, `DataTimestamp`, `DataHash` |
| `RuntimeObservationV1` | `State`, `Degradation` |
| `DegradationV1` | `Reason`, `Since` |
| `PairingObservationV1` | `RemoteSKI`, `State`, `Since`, `Opaque` |
| `ServiceV1` | `SKI`, `SHIPID`, `Kind`, `Visible`, `Paired`, `Name`, `Identifier`, `Brand`, `Type`, `Model`, `SecondaryDigest`, `Opaque` |
| `SessionV1` | `ID`, `RemoteSKI`, `State`, `Since`, `Opaque` |
| `DeviceV1` | `SKI`, `SHIPID`, `Address`, `Type`, `Description`, `Metadata`, `SecondaryDigest`, `Opaque` |
| `EntityV1` | `DeviceAddress`, `EntityAddress`, `Type`, `Description`, `SecondaryDigest`, `Opaque` |
| `FeatureV1` | `DeviceAddress`, `EntityAddress`, `FeatureAddress`, `Type`, `Role`, `Description`, `SecondaryDigest`, `Opaque` |
| `UseCaseV1` | `ContextAddress`, `Name`, `Actor`, `ResolvedRole`, `Scenarios`, `Version`, `Availability`, `DocumentSubrevision`, `SecondaryDigest`, `Opaque` |
| `OpaqueObservationV1` | `Path`, `Source`, `Value` |
| `OpaqueValueV1` | `Scalar`, `Array`, `Object` |
| `OpaqueScalarV1` | `Null`, `Boolean`, `Integer`, `String` |
| `MetadataV1` | `Values` |
| `MetadataValueV1` | `Null`, `Boolean`, `Integer`, `String` |
| `RedactedServiceV1` | `ID`, `Kind`, `Visible`, `Paired` |
| `RedactedSessionV1` | `ID`, `Remote`, `State`, `Since` |
| `RedactedDeviceV1` | `ID`, `Entities`, `UseCaseClaims` |
| `RedactedEntityV1` | `ID`, `Features` |
| `RedactedFeatureV1` | `ID`, `Role` |
| `RedactedUseCaseV1` | `ID` |

`SnapshotV1` is the eebusreg-owned, secret-free raw source. Its first-party
fields carry raw operational identity and protocol data directly; they use no
upstream implementation type. An eebusreg-owned public-view builder creates
the structurally separate `RedactedSnapshotV1` as an irreversible allowlisted
projection. This adds no `RawSnapshotV1`, v2, alias, or compatibility surface
and retains the existing `PairingState` API.

## Candidate Field Value Types

| Field | Go candidate type | Availability |
| --- | --- | --- |
| `ServiceV1.SKI` | `string` | `required` |
| `ServiceV1.SHIPID` | `*string` | `optional; nil means unavailable; pointer to empty string means observed empty` |
| `ServiceV1.Kind` | `ServiceKindV1` | `required` |
| `ServiceV1.Visible` | `bool` | `required observed state` |
| `ServiceV1.Paired` | `bool` | `required observed state` |
| `ServiceV1.Name` | `string` | `required` |
| `ServiceV1.Identifier` | `string` | `required` |
| `ServiceV1.Brand` | `string` | `required` |
| `ServiceV1.Type` | `string` | `required` |
| `ServiceV1.Model` | `string` | `required` |
| `ServiceV1.SecondaryDigest` | `*string` | `optional` |
| `ServiceV1.Opaque` | `*[]OpaqueObservationV1` | `optional; nil differs from an observed empty array` |
| `DeviceV1.SKI` | `string` | `required` |
| `DeviceV1.SHIPID` | `*string` | `optional; absence differs from observed empty` |
| `DeviceV1.Address` | `string` | `required` |
| `DeviceV1.Type` | `string` | `required` |
| `DeviceV1.Description` | `*string` | `optional; absence differs from observed empty` |
| `DeviceV1.Metadata` | `*MetadataV1` | `optional; absence differs from an observed empty object` |
| `DeviceV1.SecondaryDigest` | `*string` | `optional` |
| `DeviceV1.Opaque` | `*[]OpaqueObservationV1` | `optional; nil differs from an observed empty array` |
| `EntityV1.DeviceAddress` | `string` | `required` |
| `EntityV1.EntityAddress` | `string` | `required` |
| `EntityV1.Type` | `string` | `required` |
| `EntityV1.Description` | `*string` | `optional; absence differs from observed empty` |
| `EntityV1.SecondaryDigest` | `*string` | `optional` |
| `EntityV1.Opaque` | `*[]OpaqueObservationV1` | `optional; nil differs from an observed empty array` |
| `FeatureV1.DeviceAddress` | `string` | `required` |
| `FeatureV1.EntityAddress` | `string` | `required` |
| `FeatureV1.FeatureAddress` | `string` | `required` |
| `FeatureV1.Type` | `string` | `required` |
| `FeatureV1.Role` | `string` | `required` |
| `FeatureV1.Description` | `*string` | `optional; absence differs from observed empty` |
| `FeatureV1.SecondaryDigest` | `*string` | `optional` |
| `FeatureV1.Opaque` | `*[]OpaqueObservationV1` | `optional; nil differs from an observed empty array` |
| `UseCaseV1.ContextAddress` | `string` | `required` |
| `UseCaseV1.Name` | `string` | `required` |
| `UseCaseV1.Actor` | `string` | `required` |
| `UseCaseV1.ResolvedRole` | `*string` | `optional` |
| `UseCaseV1.Scenarios` | `*[]string` | `optional; nil differs from an observed empty array` |
| `UseCaseV1.Version` | `*string` | `optional` |
| `UseCaseV1.Availability` | `*bool` | `optional; nil differs from observed false` |
| `UseCaseV1.DocumentSubrevision` | `*string` | `optional` |
| `UseCaseV1.SecondaryDigest` | `*string` | `optional` |
| `UseCaseV1.Opaque` | `*[]OpaqueObservationV1` | `optional; nil differs from an observed empty array` |
| `OpaqueObservationV1.Path` | `string` | `required` |
| `OpaqueObservationV1.Source` | `string` | `required` |
| `OpaqueObservationV1.Value` | `OpaqueValueV1` | `required bounded JSON value` |
| `MetadataV1.Values` | `map[string]MetadataValueV1` | `required; empty map is an observed empty object` |

Secondary digest and opaque-observation fields are optional first-party values.
An absent optional property means unavailable. A present empty string, array,
object, or false boolean remains an observed value and is not collapsed into
absence.

`OpaqueValueV1` accepts scalars and nested JSON arrays/objects to maximum depth
3. Arrays and objects have at most 32 members, strings have at most 4096 UTF-8
bytes, one canonical JCS value has at most 16384 bytes, and one snapshot has at
most 256 opaque observations and 262144 aggregate canonical opaque bytes. The
recursive structured secret denylist is `private_key`, `private_pem`,
`trust_store_bytes`, `credential_token`, `bearer_token`, `session_token`,
`authentication_token`, and `cryptographic_secret`.

## Redacted Builder Inventory

| Builder | Input | Output | Contract |
| --- | --- | --- | --- |
| `BuildRedactedSnapshotV1` | `SnapshotV1` | `RedactedSnapshotV1` | `irreversible allowlisted projection; raw and opaque fields cannot be reconstructed` |

The builder rejects credential, bearer, session, and authentication tokens,
private key or PEM material, trust-store bytes, and cryptographic secrets
before either snapshot is returned.

The exact closed candidate enum inventory is:

| Type or constant | Values |
| --- | --- |
| `SnapshotContractV1` | `helianthus.eebus.runtime.raw-snapshot.v1` |
| `ObservedRuntimeStateV1` | `unknown`, `stopped`, `starting`, `ready`, `degraded`, `shutdown` |
| `DegradationReasonV1` | `missing-discovery`, `denied-trust`, `remote-disconnect`, `certificate-unavailable`, `no-visible-services`, `no-data` |
| `ServiceKindV1` | `local`, `remote` |
| `ObservedSessionStateV1` | `unknown`, `connecting`, `connected`, `disconnected`, `degraded` |
| `FeatureRoleV1` | `""`, `client`, `server` |

These are raw structural vocabularies with no free-form semantic labels.

## Allowed Operations

MSP-036 may expose only this exact value-oriented operation inventory:

| Operation | Contract |
| --- | --- |
| `NewSnapshotV1` | constructs a detached snapshot |
| `Validate` | rejects malformed, secret-bearing, duplicate, inconsistent, or hash-mismatched data |
| `Clone` | returns a complete defensive copy |
| `ComputeDataHash` | hashes the context-bound canonical payload without `data_hash` |
| `MarshalJSON` | emits the validated canonical representation |
| `String` | returns a redacted display value |
| `GoString` | returns a redacted display value |
| `Format` | writes a redacted display value |

The type, field, enum, builder, and operation tables are closed inventories.
Every listed type is first-party and no declaration depends on an upstream
implementation type.

There is no public `Runtime`, `View`, `SnapshotSource`, store handle, capture
set, dereference operation, or update method in this milestone. `Start`,
`Shutdown`, and read-only lifecycle ownership remain MSP-055. MCP capture/drop
and tool-scoped authorization binding remain M6. Trust and pairing mutations
remain behind the later admin-local gate.

## Immutability And Canonicalization

Construction and cloning recursively copy every slice and nested raw or opaque
collection. Mutating constructor inputs, clone outputs, or later runtime state
cannot change a previously captured value. Go exported fields remain ordinary
value fields; the contract's immutability guarantee is snapshot detachment and
defensive-copy behavior, not language-level `const` enforcement.

Validation and JSON encoding use stable ordering without mutating caller-owned
storage:

- services sort by SKI, optional SHIP ID, identifier, kind, visible, and paired;
- devices sort by address, SKI, and optional SHIP ID;
- entities, features, and use cases sort by their complete address paths and
  the raw-profile tie breakers;
- opaque observations sort by path, source, and canonical value; and
- timestamps are normalized to UTC and must be valid JSON timestamps.

`data_hash` uses the Helianthus canonical `sha256:<64 lowercase hex>` form. Its
JSON hash view contains `contract`, `runtime`, `local_ski`, `mask_tier`,
`data_timestamp`, `status`, `pairing`, `services`, `sessions`, `devices`,
`entities`, `features`, `usecases`, and `opaque`; only `captured_at` and
`data_hash` are omitted. The identity and mask context therefore cannot be
substituted while retaining a valid hash. Service kind, visible, and paired are
part of each service value and therefore part of that hash view.
`Validate` recomputes every non-empty `data_hash` and rejects a mismatch.
Equivalent input orderings must produce byte-identical JSON and the same hash.

## Forbidden Public Inventory

MSP-036 expressly forbids the public types `Runtime`, `RuntimeV1`, `View`,
`ViewV1`, `SnapshotSource`, `Store`, `CaptureRef`, and `ViewResult`. It also
forbids public `Start`, `Shutdown`, `Snapshot`,
`RegisterRemoteSKI`, `UnregisterRemoteSKI`, `SetPairingWindow`,
`UpdateSnapshot`, `Capture`, `Drop`, `CapturedSnapshot`, and `Dereference`
operations. These names may be introduced only by their later owning
milestones and gates. The existing read-only `PairingState` API remains
unchanged.

## Explicit Non-Authority

MSP-036 exports no semantic device ID, canonical zone/DHW/energy fact,
availability guarantee, listener or socket behavior, lifecycle transition,
trust decision, pairing action, registry/projection API, GraphQL field, Portal
binding, Home Assistant entity, or command route. No public declaration may
depend on an `enbility/eebus-go` type.
