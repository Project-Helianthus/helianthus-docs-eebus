---
canonical_source: "Project-Helianthus/helianthus-docs-eebus:api/eebusruntime-v1/reference.md"
owner_domain: "api"
license: "AGPL-3.0-only"
publication_status: "active"
claim_status: "evidence-backed"
source_class: "derived_inference"
evidence_ids: "EV-20260711-001"
hypothesis_status: "publishable"
falsifier: "Regenerating the normalized API surface from the exact source commit produces different public declarations or evidence bytes."
api_version: "eebusruntime-v1"
source_commit: "59cbea0593f27caf558bc4cc9b665c52fc50b683"
source_tree: "01c17785fe9aac8d8536545e03e1ec1d4a4dff9d"
stable_navigation: "true"
search: "true"
sitemap: "true"
versioned_bundle: "true"
release_bundle: "true"
---

# eeBUS Runtime API v1

This reference freezes the public Go API produced from the source commit and
tree declared above. The complete canonical public inventory is the adjacent
[manifest](manifest.json): 276 declarations across the root `eebusruntime`
package and the `eebusevidence` and `eebusraw` subpackages. The publication
record binds that manifest to its predicate, attestation, verification result,
source tree, workflow run, and stable publication channels.

## Fail-closed boundary

This publication establishes only a compile-time Go API at the exact source
commit. It does not prove that an enabled runtime is deployed or operational.
Enabled startup requires protected runtime material, an explicit interface,
an admitted remote, and a scoped listener. The merged source deliberately
returns an error while the protected material provider is unavailable and
rejects ship-go v0.6.0 because its listener binds on all interfaces.

The API does not expose or promise GraphQL, Portal, Home Assistant, MCP,
semantic projection, or write behavior. Those are explicit non-claims. A
source commit or tree mismatch, evidence-byte mismatch, provenance mismatch,
candidate replay, channel omission, candidate leak, or noncompiling marked
example invalidates this publication.

## Root package inventory

The root import path is
`github.com/Project-Helianthus/helianthus-eebusreg`, with package name
`eebusruntime`. Its 54 declarations are frozen exactly as follows.

### Lifecycle facade

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

### Snapshot declarations

The frozen named types are `SnapshotV1`, `SnapshotMetaV1`,
`RuntimeObservationV1`, `DegradationV1`, `PairingObservationV1`, `ServiceV1`,
`SessionV1`, `TopologyV1`, `DeviceV1`, `EntityV1`, `FeatureV1`,
`UseCaseClaimV1`, `ObservedRuntimeStateV1`, `ObservedSessionStateV1`,
`DegradationReasonV1`, `ServiceKindV1`, and `FeatureRoleV1`.

The frozen operations are `func NewSnapshotV1(SnapshotV1) (SnapshotV1,
error)`, `func (SnapshotV1) Clone() SnapshotV1`, `func (SnapshotV1)
ComputeDataHash() (string, error)`, `func (SnapshotV1) Format(fmt.State,
int32)`, `func (SnapshotV1) GoString() string`, `func (SnapshotV1)
MarshalJSON() ([]uint8, error)`, `func (SnapshotV1) String() string`, and
`func (SnapshotV1) Validate() error`.

The exact value inventory is:

- `SnapshotContractV1 = "helianthus.eebus.runtime.raw-snapshot.v1"`
- `DegradationReasonV1CertificateUnavailable = "certificate-unavailable"`
- `DegradationReasonV1DeniedTrust = "denied-trust"`
- `DegradationReasonV1MissingDiscovery = "missing-discovery"`
- `DegradationReasonV1NoData = "no-data"`
- `DegradationReasonV1NoVisibleServices = "no-visible-services"`
- `DegradationReasonV1RemoteDisconnect = "remote-disconnect"`
- `ObservedRuntimeStateV1Unknown = "unknown"`
- `ObservedRuntimeStateV1Stopped = "stopped"`
- `ObservedRuntimeStateV1Starting = "starting"`
- `ObservedRuntimeStateV1Ready = "ready"`
- `ObservedRuntimeStateV1Degraded = "degraded"`
- `ObservedRuntimeStateV1Shutdown = "shutdown"`
- `ObservedSessionStateV1Unknown = "unknown"`
- `ObservedSessionStateV1Connecting = "connecting"`
- `ObservedSessionStateV1Connected = "connected"`
- `ObservedSessionStateV1Disconnected = "disconnected"`
- `ObservedSessionStateV1Degraded = "degraded"`
- `ServiceKindV1Local = "local"`
- `ServiceKindV1Remote = "remote"`
- `FeatureRoleV1Unspecified = ""`
- `FeatureRoleV1Client = "client"`
- `FeatureRoleV1Server = "server"`

## Complete compile example

The disabled configuration is the only example shown because it exercises
the frozen facade without implying an enabled or deployed service.

<!-- go-example:compile -->
```go
package main

import (
    "context"
    "errors"

    eebusruntime "github.com/Project-Helianthus/helianthus-eebusreg"
)

func main() {
    runtime, err := eebusruntime.New(eebusruntime.Config{Enabled: false})
    if err != nil {
        panic(err)
    }
    if err := runtime.Start(context.Background()); err != nil {
        panic(err)
    }
    if _, err := runtime.Snapshot(); !errors.Is(err, eebusruntime.ErrRuntimeDisabled) {
        panic("disabled runtime returned an unexpected snapshot result")
    }
    if err := runtime.Shutdown(); err != nil {
        panic(err)
    }
}
```

The `eebusevidence` and `eebusraw` declarations, including every type,
constant, constructor, method, field, tag, and exact signature, remain part of
the same frozen API. Their nonduplicated normative inventory is the adjacent
manifest; prose on this page does not broaden or reinterpret it.
