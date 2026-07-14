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
| `SnapshotV1` | `Meta`, `Status`, `Pairing`, `Services`, `Sessions`, `Topology`, `Raw` |
| `SnapshotMetaV1` | `Contract`, `Runtime`, `LocalSKI`, `MaskTier`, `CapturedAt`, `DataTimestamp`, `DataHash` |
| `RuntimeObservationV1` | `State`, `Degradation` |
| `DegradationV1` | `Reason`, `Since` |
| `PairingObservationV1` | `Remote`, `State`, `Since`, `Raw`, `Unknown` |
| `ServiceV1` | `ID`, `Kind`, `Visible`, `Paired`, `Raw`, `Unknown` |
| `SessionV1` | `ID`, `Remote`, `State`, `Since`, `Raw`, `Unknown` |
| `TopologyV1` | `Devices` |
| `DeviceV1` | `ID`, `Entities`, `UseCaseClaims`, `Raw`, `Unknown` |
| `EntityV1` | `ID`, `Features`, `Raw`, `Unknown` |
| `FeatureV1` | `ID`, `Role`, `Raw`, `Unknown` |
| `UseCaseClaimV1` | `ID`, `Raw`, `Unknown` |

Identity fields use `eebusraw.RedactedID`. Opaque raw observations use
`eebusevidence.ObjectV1`; unknown values use `eebusraw.UnknownField`. No field
contains credential material, an unmasked device identity, a network endpoint,
vendor implementation type, or promoted semantic identifier.

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
| `Validate` | rejects malformed, unredacted, duplicate, inconsistent, or hash-mismatched data |
| `Clone` | returns a complete defensive copy |
| `ComputeDataHash` | hashes the context-bound canonical payload without `data_hash` |
| `MarshalJSON` | emits the validated canonical representation |
| `String` | returns a redacted display value |
| `GoString` | returns a redacted display value |
| `Format` | writes a redacted display value |

The type, field, enum, and operation tables are closed inventories. MSP-036
permits no additional exported declaration outside those tables and the frozen
MSP-035 `eebusraw` and `eebusevidence` dependencies.

There is no public `Runtime`, `View`, `SnapshotSource`, store handle, capture
set, dereference operation, or update method in this milestone. `Start`,
`Shutdown`, and read-only lifecycle ownership remain MSP-055. MCP capture/drop
and tool-scoped authorization binding remain M6. Trust and pairing mutations
remain behind the later admin-local gate.

## Immutability And Canonicalization

Construction and cloning recursively copy every slice and nested raw or unknown
collection. Mutating constructor inputs, clone outputs, or later runtime state
cannot change a previously captured value. Go exported fields remain ordinary
value fields; the contract's immutability guarantee is snapshot detachment and
defensive-copy behavior, not language-level `const` enforcement.

Validation and JSON encoding use stable ordering without mutating caller-owned
storage:

- services, sessions, pairing observations, devices, entities, features, and
  use-case claims sort by redacted identity kind and digest;
- raw evidence objects use their frozen `ObjectV1` order;
- unknown fields use their frozen path/digest/value order; and
- timestamps are normalized to UTC and must be valid JSON timestamps.

`data_hash` uses the Helianthus canonical `sha256:<64 lowercase hex>` form. Its
JSON hash view contains `contract`, `runtime`, `local_ski`, `mask_tier`,
`data_timestamp`, `status`, `pairing`, `services`, `sessions`, `topology`, and
`raw`; only `captured_at` and `data_hash` are omitted. The identity and mask
context therefore cannot be substituted while retaining a valid hash.
`Validate` recomputes every non-empty `data_hash` and rejects a mismatch.
Equivalent input orderings must produce byte-identical JSON and the same hash.

## Forbidden Public Inventory

MSP-036 expressly forbids the public types `Runtime`, `RuntimeV1`, `View`,
`ViewV1`, `SnapshotSource`, `Store`, `CaptureRef`, and `ViewResult`. It also
forbids public `Start`, `Shutdown`, `Snapshot`, `PairingState`,
`RegisterRemoteSKI`, `UnregisterRemoteSKI`, `SetPairingWindow`,
`UpdateSnapshot`, `Capture`, `Drop`, `CapturedSnapshot`, and `Dereference`
operations. These names may be introduced only by their later owning
milestones and gates.

## Explicit Non-Authority

MSP-036 exports no semantic device ID, canonical zone/DHW/energy fact,
availability guarantee, listener or socket behavior, lifecycle transition,
trust decision, pairing action, registry/projection API, GraphQL field, Portal
binding, Home Assistant entity, or command route. No public declaration may
depend on an `enbility/eebus-go` type.
