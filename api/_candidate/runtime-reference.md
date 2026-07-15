---
canonical_source: "Project-Helianthus/helianthus-docs-eebus:api/_candidate/runtime-reference.md"
owner_domain: "api"
license: "AGPL-3.0-only"
publication_status: "retired-candidate"
claim_status: "evidence-backed"
source_class: "derived_inference"
evidence_ids: "EV-20260711-001"
hypothesis_status: "withdrawn"
falsifier: "The active publication record no longer preserves this candidate evidence or its retirement binding."
candidate_output: "true"
stable_navigation: "false"
search: "false"
sitemap: "false"
versioned_bundle: "false"
release_bundle: "false"
candidate_output_path: "api/_candidate/runtime-reference.md"
---

# Retired Candidate eeBUS Runtime API Reference

This hidden exact-head candidate is retired. It preceded source pull request
25 and remains only as historical evidence for the active
`api/eebusruntime-v1/` publication. It is not a supported API reference and
makes no deployed-runtime claim. Its original workflow-dispatch record and
byte-preserved evidence remain under `api/_candidate/msp-055/`.

## Candidate boundary

The retired candidate was limited to the public lifecycle facade in the
manifest. In a
production-enabled configuration, `Start` is fail-closed: protected material
and the scoped transport listener (SHIP) are downstream M4B responsibilities. A ship-go
v0.6 wildcard listener is rejected.

This retired candidate does not expose GraphQL, Portal, Home Assistant, MCP,
semantics, or writes. It neither establishes a supported release nor proves a
deployed service.

## Exact lifecycle facade inventory

The source manifest names package `eebusruntime`. Its lifecycle additions are
the following closed inventory:

| Declaration | Exact public shape |
| --- | --- |
| `Config` | `struct{ Enabled bool; StateRoot string; Interface string; ListenPort int; Remotes []Remote }` |
| `Remote` | `struct{ SKI string }` |
| `Runtime` | `interface{ PairingState() ([]PairingObservationV1, error); Shutdown() error; Snapshot() (SnapshotV1, error); Start(context.Context) error }` |
| `New` | `func New(Config) (Runtime, error)` |
| `Start` | `Start(context.Context) error` |
| `Shutdown` | `Shutdown() error` |
| `Snapshot` | `Snapshot() (SnapshotV1, error)` |
| `PairingState` | `PairingState() ([]PairingObservationV1, error)` |
| `ErrRuntimeDisabled` | `var ErrRuntimeDisabled error` |
| `ErrRuntimeShutdown` | `var ErrRuntimeShutdown error` |

## Frozen raw snapshot inventory

The facade returns the already frozen raw snapshot contract, without changing
its value semantics. The exact referenced type inventory is `SnapshotV1`,
`SnapshotMetaV1`, `RuntimeObservationV1`, `DegradationV1`,
`PairingObservationV1`, `ServiceV1`, `SessionV1`, `TopologyV1`, `DeviceV1`,
`EntityV1`, `FeatureV1`, `UseCaseClaimV1`, `ObservedRuntimeStateV1`,
`ObservedSessionStateV1`, `DegradationReasonV1`, `ServiceKindV1`, and
`FeatureRoleV1`.

The same manifest retains these snapshot operations: `NewSnapshotV1`,
`Validate`, `Clone`, `ComputeDataHash`, `MarshalJSON`, `String`, `GoString`,
and `Format`. Its closed vocabularies retain the raw observation states,
degradation reasons, service kinds, session states, feature roles, and
`SnapshotContractV1`; this page does not reinterpret them as semantic facts.

## Explicit exclusions

No additional lifecycle owner, listener policy, transport dispatch, trust or
pairing mutation, semantic projection, consumer binding, or write route was
part of this candidate. In particular, it did not add GraphQL fields, Portal
views, Home Assistant entities, MCP tools, or a semantic device model.

The historical evidence is invalidated if its exact source head, source ref,
workflow-dispatch result, attempt, artifact, attestation, or manifest bytes
change, or if its retired state and active-publication binding are removed.
