---
canonical_source: "Project-Helianthus/helianthus-docs-eebus:architecture/_candidate/msp-05p-production-activation.md"
owner_domain: "architecture"
license: "AGPL-3.0-only"
publication_status: "candidate"
claim_status: "evidence-backed"
source_class: "derived_inference"
evidence_ids: "EV-20260711-001,EV-20260714-001"
hypothesis_status: "draft"
falsifier: "An accepted implementation or review demonstrates that production activation can widen listener scope, discard gateway configuration, expose a consumer surface, or persist trust before confirmation without violating the raw-first safety boundary."
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
It derives an activation boundary from the frozen M5A gateway scaffold,
published raw runtime evidence, and the accepted trust coordinator contracts.
It is not a supported runtime or semantic publication.

The disabled default performs no runtime construction, filesystem access,
goroutine, socket, or mDNS operation. Production activation is a sibling
eeBUS lifecycle and does not modify `transportFromConn`, `protocol.Bus`, or
`router.BusEventRouter`. This slice creates no `eebus.v1`, `ebus.v1`,
GraphQL, Portal, Home Assistant, command, raw-write, or promoted-semantic
surface.

## Gateway To Runtime Mapping

| Gateway input | Runtime v2 input | Rule |
| --- | --- | --- |
| `Enabled` | `Enabled` | `direct` |
| `ListenPort` | `ListenAddress.port` | `required-1..65535` |
| `Interfaces` | `Interface` | `exactly-one` |
| `Subnets` | `ListenAddress.addr` | `resolve-exactly-one` |
| `StateRoot` | `StateRoot` | `required-absolute-protected` |
| `DiscoveryEnabled` | `DiscoveryEnabled` | `direct-default-false` |
| `RemoteSKIAllowlist` | `Remotes` | `lossless-sorted` |
| `PairingWindowMode` | `PairingPolicy` | `closed-only` |
| `CertificatePath` | `unsupported` | `must-be-empty` |
| `PrivateKeyPath` | `unsupported` | `must-be-empty` |
| `TrustStorePath` | `unsupported` | `must-be-empty` |

Enabled activation rejects zero or multiple interfaces. Resolving the selected
interface against the configured subnet rejects zero or multiple matching
addresses and rejects an unspecified, multicast, or wildcard address. Every
such error must fail before runtime construction.

The adapter derives `StateRoot` only from the gateway's protected eeBUS data
root. It does not alias a legacy path to `StateRoot` and does not silently
discard a configured field. The three legacy material paths are therefore
accepted only when empty; a non-empty value is an unsupported configuration,
not a fallback or migration hint. Allowlist values retain their normalized,
deterministically sorted SKIs without widening or truncation.

## Activation Order

| Stage | Required result |
| --- | --- |
| `disabled_gate` | return-disabled-without-effects |
| `configuration_validation` | complete-lossless-product-valid |
| `state_root_validation` | protected-root-valid |
| `protected_material_load` | identity-valid-for-host |
| `trust_state_load` | durable-state-consistent |
| `service_construction` | internal-facades-ready |
| `listener_start` | exact-endpoint-bound |
| `discovery_publish` | requested-publication-active |
| `ready_publish` | observable-ready-state |

No later stage runs after the first failure. Cleanup closes every effect opened
by an earlier stage exactly once, so no socket, goroutine, publication, or
partial durable mutation remains. Shutdown is idempotent before `Start`,
after successful startup, during failed startup cleanup, and after an earlier
shutdown.

## Error Precedence

| Error class | Terminal meaning |
| --- | --- |
| `disabled` | feature-not-requested |
| `invalid_configuration` | mapping-or-cross-field-invalid |
| `unsafe_state_root` | root-or-file-policy-invalid |
| `protected_material_unavailable` | identity-cannot-load |
| `trust_state_unavailable` | durable-trust-cannot-load |
| `listener_unavailable` | exact-bind-cannot-start |
| `discovery_unavailable` | requested-publication-cannot-start |

Only the first class in this precedence is returned for one activation
attempt. A later networking condition cannot mask an earlier configuration,
filesystem, identity, or trust failure. Runtime status may retain a redacted
structured reason, but it cannot include protected material or raw peer
identity.

## Protected Identity And Trust

`StateRoot` is an absolute, dedicated tree with a `0700` directory and `0600`
regular files. Validation permits no symlink, traversal, device, FIFO, or
socket. Durable updates use same-directory temporary files, atomic replace and
directory `fsync`; interrupted updates must reload either the complete old
generation or the complete new generation.

The private identity uses a host-bound or explicitly backup-excluded key. Its
validation ensures wrong-host restore and cloned state fail before listener or mDNS activation.
The certificate, private key, local SKI, remote SKI, remote SHIP ID, and pairing
state survive restart when restored on the authorized host under the accepted
store policy. Their durable relationship is validated before any network
effect.

Protected values remain inside the runtime and coordinator: secrets never
appear in environment, argv, logs, snapshots, metrics, traces, or public
errors. An unknown peer cannot persist trust while pairing is closed. A future
first-trust flow may hold one ephemeral candidate and OOB fingerprint
confirmation, with no persistent write before confirmation. That flow remains
internal and admin-gated; this candidate adds no public trust mutation.

## Rollback And Dependency Gate

If any prerequisite cannot preserve these constraints, withdraw this candidate
before any dependent code merge. Runtime v2, listener policy, identity loading,
gateway activation, and M5B remain blocked until this candidate is accepted.
Rollback removes only the candidate pages and tests; it creates no durable
migration and leaves the inert M5A scaffold and existing eBUS lifecycle
unchanged.
