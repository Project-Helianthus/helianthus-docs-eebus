---
canonical_source: "Project-Helianthus/helianthus-docs-eebus:api/_candidate/msp-05p-eebusruntime-v2.md"
owner_domain: "api"
license: "AGPL-3.0-only"
publication_status: "candidate"
claim_status: "evidence-backed"
source_class: "derived_inference"
evidence_ids: "EV-20260711-001,EV-20260714-001"
hypothesis_status: "draft"
falsifier: "An accepted source review proves that the exact-address production contract cannot be represented additively without breaking the frozen v1 facade or exposing a dependency implementation type."
stable_navigation: "false"
search: "false"
sitemap: "false"
versioned_bundle: "false"
release_bundle: "false"
candidate_output: "true"
candidate_output_path: "api/_candidate/msp-05p-eebusruntime-v2.md"
---

# Candidate MSP-05P eeBUS Runtime v2 API

## Status And Compatibility

This candidate is tracked by
[issue 36](https://github.com/Project-Helianthus/helianthus-docs-eebus/issues/36).
It defines the smallest additive API needed to carry an exact listener address
and independent discovery policy into the raw runtime. It neither activates a
gateway nor changes the supported v1 publication.

`Config`, `Remote`, `Runtime`, and `New` remain source compatible. Existing
enabled v1 behavior remains fail closed because v1 cannot express the complete
production listener policy. The gateway production activation uses `NewV2`
only after the M5A configuration mapping and all production prerequisites pass.

## Candidate Public Additions

| Declaration | Shape | Purpose |
| --- | --- | --- |
| `ConfigV2` | `struct` | additive-production-input |
| `ListenAddress` | `netip.AddrPort` | exact-listener-endpoint |
| `DiscoveryEnabled` | `bool` | independent-publication-policy |
| `PairingPolicy` | `PairingPolicyV2` | closed-policy-input |
| `PairingPolicyV2Closed` | `constant` | only-accepted-production-value |
| `NewV2` | `func(ConfigV2)(Runtime,error)` | fail-closed-constructor |

`ConfigV2` also carries the existing enabled flag, protected state root, and
normalized remote allowlist without changing their value meaning. The endpoint
uses standard-library `net/netip.AddrPort`; it must be valid, specified,
unicast, and non-wildcard before construction.

The public facade contains no `enbility`, `ship-go`, `spine-go`, WebSocket,
mDNS, certificate-provider, or store implementation type. Those dependencies
remain internal and replaceable. No public trust or pairing mutation is added;
`PairingPolicyV2Closed` expresses a constructor invariant rather than an admin
command.

## Lifecycle And Surface Boundary

`NewV2` validates the complete value product without filesystem, goroutine,
socket, or mDNS effects. `Start` owns the ordered activation contract and
`Shutdown` retains the frozen idempotency requirement. The returned `Runtime`
interface remains the v1 interface, so this API does not introduce a second
lifecycle owner or a dependency-specific handle.

The API adds no MCP, GraphQL, Portal, Home Assistant, command, raw-write, or
semantic declaration. Snapshot and pairing observations retain their frozen
raw v1 shapes and do not gain secret material, bind credentials, or trust
mutation methods.

## Rollback

Before consumer adoption, rollback can remove the additive v2 contract and
retain v1 unchanged. No stored state is encoded exclusively by `ConfigV2`, and
no v1 caller is migrated implicitly. If exact listener scope cannot be
implemented behind this facade, the documentation candidate is withdrawn and
gateway production activation remains blocked.
