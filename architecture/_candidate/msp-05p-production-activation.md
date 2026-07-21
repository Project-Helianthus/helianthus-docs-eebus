---
canonical_source: "Project-Helianthus/helianthus-docs-eebus:architecture/_candidate/msp-05p-production-activation.md"
owner_domain: "architecture"
license: "AGPL-3.0-only"
publication_status: "candidate"
claim_status: "evidence-backed"
source_class: "derived_inference"
evidence_ids: "EV-20260711-001,EV-20260714-001"
hypothesis_status: "draft"
falsifier: "An accepted implementation or review demonstrates that activation can widen listener scope, discard the frozen gateway product, expose a consumer surface, or publish observed remote state from policy."
stable_navigation: "false"
search: "false"
sitemap: "false"
versioned_bundle: "false"
release_bundle: "false"
---

# Candidate MSP-05P Production Activation Contract

## Status And Scope

This candidate freezes the production prerequisite tracked by
[issue 36](https://github.com/Project-Helianthus/helianthus-docs-eebus/issues/36).
It consumes the current M5A gateway product and the private trust coordinator.
It is not a supported runtime or semantic publication; live validation remains pending.

The disabled default performs no runtime construction, filesystem access,
goroutine, socket, or mDNS operation. Activation remains an eeBUS sibling
lifecycle and adds no consumer or write surface.

## Gateway To Runtime Mapping

The exact current gateway product maps as follows:

| Gateway input | Runtime v1 input | Rule |
| --- | --- | --- |
| `Enabled` | `Enabled` | `direct` |
| `ListenPort` | `ListenAddress.port` | `required-1..65535` |
| `Interfaces` | `Interface` | `exactly-one` |
| `Subnets` | `ListenAddress.addr` | `resolve-exactly-one` |
| `StateRoot` | `StateRoot` | `required-absolute-protected` |
| `DiscoveryEnabled` | `DiscoveryEnabled` | `direct-default-false` |
| `RemoteSKIAllowlist` | `Remotes` | `lossless-sorted` |
| `PairingWindowMode` | `PairingPolicy` | `closed-only` |

StateRoot is the sole protected identity and trust root input.
RemoteSKIAllowlist remains authorization policy only and cannot create observed
remote state. Enabled activation rejects zero or multiple interfaces, zero or
multiple matching unicast addresses, a zero port, an unsafe root, or any
unmapped input before runtime construction.

## Activation Order

| Stage | Required result |
| --- | --- |
| `configuration_validation` | `complete-lossless-product-valid` |
| `disabled_gate` | `return-disabled-without-effects` |
| `state_root_validation` | `protected-root-valid` |
| `protected_material_load` | `identity-valid-for-host` |
| `trust_state_load` | `durable-state-consistent` |
| `service_construction` | `internal-facades-ready` |
| `listener_start` | `exact-listener-bound` |
| `discovery_publish` | `requested-publication-active` |
| `ready_publish` | `observable-ready-state` |

No later stage runs after the first failure. Cleanup closes each earlier effect
exactly once. Shutdown withdraws an active advertisement before listener close
and leaves no multicast record, listener, goroutine, session, or partial
durable mutation.

## Protected Identity And Trust

`StateRoot` is an absolute dedicated tree with owner-only directories and
regular files. Validation permits no symlink, traversal, device, FIFO, or
socket. Durable updates use atomic replacement and directory synchronization.

Startup loads the exact raw 32-byte `StoreInstance` and derives `nodeToken` plus
the canonical SHIP ID. It then loads the current certificate identity (SKI). A real
host-key and certificate repair must change certificate SKI while preserving
the exact `StoreInstance`, `nodeToken`, and canonical SHIP ID. Failure of that
comparison prevents listener and discovery activation.

An allowlist entry cannot populate a service, session, topology row, or pairing
candidate. Those rows remain owned by mDNS, connection, and transport-backed
pairing callbacks respectively.

## Activation Proof Gate

| Gate | Required implementation proof |
| --- | --- |
| `identity_load` | The protected store and host-key provider load separate stable store identity and current certificate identity before network effects. |
| `listener_scope` | The listener binds only the one selected address and port. |
| `discovery_order` | The canonical advertisement begins only after bind and is withdrawn before listener close. |
| `repair_stability` | Real host-key and certificate repair changes certificate SKI while preserving exact `StoreInstance`, `nodeToken`, and canonical SHIP ID. |
| `observation_provenance` | Policy load creates no remote row; each live callback creates only its owned stage. |

The proof gate is normative derived design. It does not establish deployed
support. Shareable artifacts remain raw, redacted, and free of promoted
semantics.

## Dependency Gate

If any prerequisite cannot preserve these constraints, withdraw this candidate
before dependent code merges. No durable state conversion is defined by this
contract.
