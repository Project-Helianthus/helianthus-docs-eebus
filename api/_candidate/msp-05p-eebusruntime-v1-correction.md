---
canonical_source: "Project-Helianthus/helianthus-docs-eebus:api/_candidate/msp-05p-eebusruntime-v1-correction.md"
owner_domain: "api"
license: "AGPL-3.0-only"
publication_status: "candidate"
claim_status: "evidence-backed"
source_class: "derived_inference"
evidence_ids: "EV-20260711-001,EV-20260714-001"
hypothesis_status: "draft"
falsifier: "The exact green source head exposes a different public shape, requires wildcard listener scope, or cannot preserve the frozen Runtime lifecycle."
source_repository: "Project-Helianthus/helianthus-eebusreg"
source_pull_request: "45"
source_commit: "7a5852e009bbdcba47f0a34ba866070a4ab35ef8"
source_tree: "b090651c99d5b6817a40997b14c1b6a2a37c124e"
source_run: "29642000784"
source_manifest_sha256: "bbabab51cc0a0e833c645f51767e67a34c0361ba61c45b0065ecfda55ed6c32f"
stable_navigation: "false"
search: "false"
sitemap: "false"
versioned_bundle: "false"
release_bundle: "false"
candidate_output: "true"
candidate_output_path: "api/_candidate/msp-05p-eebusruntime-v1-correction.md"
---

# Candidate MSP-05P Initial eeBUS Runtime v1 API

## Status And Compatibility

This candidate is tracked by
[issue 40](https://github.com/Project-Helianthus/helianthus-docs-eebus/issues/40).
It records the exact pre-release API generated and attested after source pull
request 45 merged to `main`. The module has no tag, GitHub release, or known downstream
consumer, so the first release has one constructor and one configuration
shape rather than carrying an unpublished compatibility layer.

The candidate does not activate the gateway. Its final source merge, tree,
push workflow run, and manifest digest are declared in the front matter and
repeated by the active publication record.

## Exact Public Shape

| Public name | Shape | Location |
| --- | --- | --- |
| `Config` | `struct` | package-type |
| `ListenAddress` | `netip.AddrPort` | Config-field |
| `DiscoveryEnabled` | `bool` | Config-field |
| `Config.PairingPolicy` | `PairingPolicy` | Config-field |
| `PairingPolicy` | `string` | package-type |
| `PairingPolicyClosed` | `constant` | package-constant |
| `New` | `func(Config)(Runtime,error)` | package-function |

## Exact Go Shape

```go
type PairingPolicy string

const PairingPolicyClosed PairingPolicy = "closed"

type Config struct {
    Enabled          bool
    StateRoot        string
    Interface        string
    ListenAddress    netip.AddrPort
    DiscoveryEnabled bool
    Remotes          []Remote
    PairingPolicy    PairingPolicy
}

func New(config Config) (Runtime, error)
```

The package imports standard-library `net/netip` for the endpoint type. When
enabled, `New` requires an absolute non-root state directory, one explicit
interface, a valid specified unicast address with a non-zero port, and
`PairingPolicyClosed`. `DiscoveryEnabled=false` and a nil or empty remote
allowlist are valid. Duplicate or malformed SKIs are rejected after canonical
lowercase normalization.

Disabled configuration is valid only as the zero product. Supplying any
active-only field while `Enabled=false` is invalid and causes no filesystem,
goroutine, socket, service, or mDNS effect.

## Lifecycle And Surface Boundary

`New` validates without I/O and delegates to one private runtime factory.
`Start`, `Shutdown`, `Snapshot`, and `PairingState` retain the frozen Runtime
interface. The public facade contains no `enbility`, SHIP, SPINE, WebSocket,
mDNS, certificate-provider, or store implementation type.

This contract adds no MCP, GraphQL, Portal, Home Assistant, command,
raw-write, semantic projection, or public trust mutation. Closed pairing is a
constructor invariant, not an administrative mutation API.

## Provenance And Rollback

The normalized manifest contains 278 declarations, 56 in the root package.
The predicate checkout binds the exact source head. GitHub's signing
certificate binds the workflow invocation to the synthetic pull-request merge
ref; the active publication validates both values rather than treating them as
the same identity.

Before source merge, rollback withdraws this candidate and restores the prior
active reference. It performs no state migration. After source squash-merge,
promotion requires a provenance-only refresh proving that the merged source
tree is exactly the candidate tree.
