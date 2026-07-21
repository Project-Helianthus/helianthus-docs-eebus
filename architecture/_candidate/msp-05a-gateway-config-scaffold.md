---
canonical_source: "Project-Helianthus/helianthus-docs-eebus:architecture/_candidate/msp-05a-gateway-config-scaffold.md"
owner_domain: "architecture"
license: "AGPL-3.0-only"
publication_status: "candidate"
claim_status: "evidence-backed"
source_class: "derived_inference"
evidence_ids: "EV-20260711-001"
hypothesis_status: "draft"
falsifier: "An accepted gateway implementation or architecture review demonstrates that this scaffold can create runtime effects while disabled or cannot map its complete current configuration product without loss."
stable_navigation: "false"
search: "false"
sitemap: "false"
versioned_bundle: "false"
release_bundle: "false"
---

# Candidate MSP-05A Gateway Configuration Scaffold

## Status And Scope

This candidate freezes the one inert gateway configuration product tracked by
[issue 34](https://github.com/Project-Helianthus/helianthus-docs-eebus/issues/34).
It defines input ownership before runtime integration and does not claim an
implemented listener, discovery publication, trust integration, or supported
gateway behavior.

The gateway root `Config` owns one `EEBusConfig` sibling. It remains separate
from eBUS transport configuration and is never translated through that
transport. Parsing may construct and validate data only; it cannot create a
runtime object.

## Frozen Configuration Shape

| Go field | Go type | CLI flag | Default |
| --- | --- | --- | --- |
| `Enabled` | `bool` | `--eebus-enabled` | `false` |
| `ListenPort` | `uint16` | `--eebus-listen-port` | `0` |
| `Interfaces` | `[]string` | `--eebus-interfaces` | `[]` |
| `Subnets` | `[]string` | `--eebus-subnets` | `[]` |
| `StateRoot` | `string` | `--eebus-state-root` | `` |
| `DiscoveryEnabled` | `bool` | `--eebus-discovery-enabled` | `false` |
| `RemoteSKIAllowlist` | `[]string` | `--eebus-remote-ski-allowlist` | `[]` |
| `PairingWindowMode` | `EEBusPairingWindowMode` | `--eebus-pairing-window-mode` | `closed` |

`ListenPort=0` is inert. Empty strings and lists are missing configuration,
not inferred values. `closed` is the only scaffold pairing-window value.
`StateRoot` is the sole protected identity and trust root input.

## Parsing And Normalization

| Input | Normalization | Invalid result |
| --- | --- | --- |
| `interfaces` | `trim+deduplicate+preserve-order` | `flag-error` |
| `subnets` | `trim+netip-prefix+deduplicate+sort` | `flag-error` |
| `state_root` | `trim-only` | `flag-error-on-empty-or-NUL-when-enabled` |
| `remote_ski_allowlist` | `trim+lowercase+40-hex+deduplicate+sort` | `flag-error` |
| `pairing_window_mode` | `lowercase-enum` | `flag-error` |
| `listen_port` | `base10-uint16` | `flag-error` |

Empty lists never mean every interface or subnet. Enabled activation later
requires one explicit interface, one permitted unicast address, a non-zero
port, and a protected absolute `StateRoot` before any effect.

RemoteSKIAllowlist is authorization policy only. It cannot create a service,
session, topology row, or pairing candidate. `DiscoveryEnabled` permits local
publication only after the exact listener is bound; it says nothing about a
remote peer.

## Phase Ownership

| Concern | Scaffold | Runtime activation |
| --- | --- | --- |
| `shape-and-CLI-parse` | `owned` | `consume` |
| `state-root-validation` | `syntax-only` | `required-before-start` |
| `interface-subnet-validation` | `syntax-only` | `required-before-bind` |
| `runtime-construction` | `forbidden` | `owned` |
| `socket-bind` | `forbidden` | `owned` |
| `mdns-advertisement` | `forbidden` | `policy-gated-after-bind` |
| `trust-store-write` | `forbidden` | `coordinator-only` |

## Disabled-Default Invariants

The default configuration opens no eeBUS socket, emits no `_ship._tcp`,
creates no trust file or directory, and starts no eeBUS goroutine. Merely
parsing any field has the same no-effect requirement.

The scaffold adds no GraphQL, Portal, Home Assistant, MCP, command-routing,
raw-write, trust mutation, observed remote state, or promoted-semantic surface.
Activation consumes the exact frozen product above or rejects it before the
first filesystem or network effect.

## Contract Links

The [production activation contract](msp-05p-production-activation.md) consumes
this shape. The [trust projection](msp-045-trust-admin-projection.md),
[first-trust contract](msp-04b-first-trust-admin-local.md), and
[restore/revocation/repair contract](msp-04c-restore-revocation-quarantine-repair.md)
retain their own security ownership.
