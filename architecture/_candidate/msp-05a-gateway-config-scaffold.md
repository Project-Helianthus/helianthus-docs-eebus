---
canonical_source: "Project-Helianthus/helianthus-docs-eebus:architecture/_candidate/msp-05a-gateway-config-scaffold.md"
owner_domain: "architecture"
license: "AGPL-3.0-only"
publication_status: "candidate"
claim_status: "evidence-backed"
source_class: "derived_inference"
evidence_ids: "EV-20260711-001"
hypothesis_status: "draft"
falsifier: "An accepted gateway implementation or architecture review demonstrates that this scaffold can open an eeBUS listener, advertise SHIP, write trust state, widen interface selection, accept secret material, or couple eeBUS to the existing eBUS transport while disabled."
stable_navigation: "false"
search: "false"
sitemap: "false"
versioned_bundle: "false"
release_bundle: "false"
---

# Candidate MSP-05A Gateway Configuration Scaffold

## Status And Scope

This candidate freezes the inert gateway configuration scaffold tracked by
[issue 34](https://github.com/Project-Helianthus/helianthus-docs-eebus/issues/34).
It defines the input shape required before the MSP-05B runtime sidecar can be
integrated. It does not claim an implemented listener, service discovery,
trust-store integration, runtime import, or supported gateway behavior.

The gateway root `Config` owns one `EEBusConfig` sibling named
`EEBusConfig`. It is separate from the existing eBUS `TransportConfig` and is
never translated through that transport. The M5A source slice may construct,
copy, compare, and parse this value. It may not consume it to create an
operational object.

## Frozen Configuration Shape

| Go field | Go type | CLI flag | Default |
| --- | --- | --- | --- |
| `Enabled` | `bool` | `--eebus-enabled` | `false` |
| `ListenPort` | `uint16` | `--eebus-listen-port` | `0` |
| `Interfaces` | `[]string` | `--eebus-interfaces` | `[]` |
| `Subnets` | `[]string` | `--eebus-subnets` | `[]` |
| `CertificatePath` | `string` | `--eebus-certificate-path` | `` |
| `PrivateKeyPath` | `string` | `--eebus-private-key-path` | `` |
| `TrustStorePath` | `string` | `--eebus-trust-store-path` | `` |
| `RemoteSKIAllowlist` | `[]string` | `--eebus-remote-ski-allowlist` | `[]` |
| `PairingWindowMode` | `EEBusPairingWindowMode` | `--eebus-pairing-window-mode` | `closed` |

`ListenPort=0` means unconfigured and inert. It never requests an ephemeral
port. Empty strings and lists are explicit missing configuration, not inferred
defaults. `closed` is the only M5A pairing-window value. Any future mode that
can arm pairing requires the MSP-05B security and admin contract first.

The list flags accept one comma-separated value. If a flag is repeated, the
last successfully parsed occurrence replaces the earlier value, matching
scalar flag behavior. A failed occurrence does not widen the accepted value.

## Parsing And Normalization

| Input | Normalization | Invalid result |
| --- | --- | --- |
| `interfaces` | `trim+deduplicate+preserve-order` | `flag-error` |
| `subnets` | `trim+netip-prefix+deduplicate+sort` | `flag-error` |
| `remote_ski_allowlist` | `trim+lowercase+40-hex+deduplicate+sort` | `flag-error` |
| `pairing_window_mode` | `lowercase-enum` | `flag-error` |
| `paths` | `trim-only` | `flag-error-on-NUL` |
| `listen_port` | `base10-uint16` | `flag-error` |

Empty comma-separated elements are discarded before deduplication. An input
that contains no non-empty elements becomes an empty list. Interface names are
opaque at M5A and preserve first occurrence order. Subnets use canonical
`netip.Prefix` text and deterministic lexical ordering. Remote SKIs contain
exactly 40 hexadecimal characters and are stored in lowercase deterministic
order. The enum parser trims and lowercases before comparing against the
closed set.

Paths are references, not secret-bearing inputs. M5A trims surrounding
whitespace and rejects NUL. It does not open, create, canonicalize, follow, or
validate a path. Absolute-path, root ownership, nofollow, permissions,
host-binding, and atomic durability checks belong to MSP-05B before runtime
construction. Certificate and private-key contents are never CLI values,
never environment values, never logged, and never included in snapshots.

Empty lists never mean all interfaces or all subnets. M5B must reject enabled
activation unless the explicit interface and subnet selections resolve to a
permitted, non-wildcard bind. No parser fallback may expand an invalid or empty
selection to every host interface.

## Phase Ownership

| Concern | M5A | M5B |
| --- | --- | --- |
| `shape-and-CLI-parse` | `owned` | `consume` |
| `filesystem-validation` | `forbidden` | `required-before-start` |
| `interface-subnet-validation` | `syntax-only` | `required-before-bind` |
| `runtime-construction` | `forbidden` | `owned` |
| `socket-bind` | `forbidden` | `owned` |
| `mdns-advertisement` | `forbidden` | `policy-gated` |
| `trust-store-write` | `forbidden` | `coordinator-only` |

M5A deliberately permits a syntactically valid but operationally incomplete
value to be represented. `Enabled=true` remains data only in this slice. M5B
must validate the complete cross-field product before constructing the sidecar
and must fail closed before the first filesystem or network side effect.

## Disabled-Default Invariants

The default configuration opens no eeBUS socket, emits no `_ship._tcp`,
creates no trust file or directory, and starts no eeBUS goroutine. M5A imports
no `helianthus-eebusreg` package and adds no module dependency for it. Merely
parsing any scaffold field has the same no-side-effect requirement.

The source slice does not modify `transportFromConn`, does not modify
`protocol.Bus`, does not modify `router.BusEventRouter`, and does not modify
existing eBUS registry or semantic output. It adds no GraphQL, Portal, Home
Assistant, MCP, command-routing, raw-write, or promoted-semantic surface.

Configuration is not security authority. An allowlist entry is admission
input, not proof of trust. A certificate path is not proof that a protected
identity exists. A pairing-window mode is policy input, not pairing state.
M5A cannot assert trust or durable pairing.

## Activation Handoff

The MSP-05P production contract supersedes the earlier M5B activation handoff
without changing this inert M5A source shape. `StateRoot` and
`DiscoveryEnabled` are deliberate `MSP-05A-R1` additions; neither is inferred
from an M5A field. The legacy certificate, private-key, and trust-store path
fields remain source-compatible but must be empty under the revised production
contract. They are not aliases for `StateRoot`.

M5A-R1 follows the runtime v2 and scoped-listener prerequisites. It must add the
two inputs explicitly and preserve every existing field until the gateway can
map the complete configuration product without loss. Any missing, ambiguous,
unsupported, or future value fails before runtime construction.

mDNS remains separately policy-gated. Pairing closed is not permission to
advertise. Runtime construction is not permission to bind. A valid bind is not
proof of trust. Those transitions remain explicit and independently testable.

## Rollback Ledger

Remove the inert `EEBusConfig` scaffold, its CLI parsers, and its tests. Because
M5A creates no runtime object, socket, discovery record, store, migration, API,
or consumer dependency, rollback requires no state conversion and leaves the
existing eBUS lifecycle unchanged.

## Cross-Contract Links

The [MSP-045 trust/admin projection](msp-045-trust-admin-projection.md) remains
the read-only authority boundary. The
[persistent-store contract](msp-04a-persistent-store.md),
[first-trust contract](msp-04b-first-trust-admin-local.md), and
[restore/revocation contract](msp-04c-restore-revocation-quarantine-repair.md)
remain prerequisites for MSP-05B. This scaffold neither duplicates nor
weakens them.
