---
canonical_source: "Project-Helianthus/helianthus-docs-eebus:architecture/_candidate/ha-addon-runtime-wiring.md"
owner_domain: "architecture"
license: "AGPL-3.0-only"
publication_status: "candidate"
claim_status: "evidence-backed"
source_class: "derived_inference"
evidence_ids: "EV-20260729-001"
hypothesis_status: "draft"
falsifier: "A supported Home Assistant deployment cannot preserve the exact enabled eeBUS configuration and protected state across container recreation without widening listener, trust, or public API boundaries."
stable_navigation: "false"
search: "false"
sitemap: "false"
versioned_bundle: "false"
release_bundle: "false"
---

# Candidate Home Assistant Add-on Runtime Wiring

## Scope

This contract maps Home Assistant add-on options to the existing gateway
eeBUS runtime product. It packages the raw SHIP/SPINE sibling runtime; it does
not add a Home Assistant entity, GraphQL field, Portal model, semantic
promotion, command route, v2 namespace, alias, or compatibility path.

The add-on configuration is persistent deployment intent. A temporary service
wrapper replacement is not configuration persistence because Home Assistant
may recreate the container and restore the image-owned wrapper.

## Option Mapping

| Add-on option | Gateway input | Default | Enabled rule |
| --- | --- | --- | --- |
| `eebus_enabled` | `--eebus-enabled` | `false` | direct |
| `eebus_listen_port` | `--eebus-listen-port` | `4712` | integer `1..65535` |
| `eebus_interface` | `--eebus-interfaces` | empty | exactly one explicit interface |
| `eebus_subnets` | `--eebus-subnets` | empty | comma-separated non-empty prefix set |
| `eebus_discovery_enabled` | `--eebus-discovery-enabled` | `true` | direct |
| `eebus_remote_ski_allowlist` | `--eebus-remote-ski-allowlist` | empty | optional comma-separated 40-hex entries |

The wrapper supplies `--eebus-state-root=/data/eebus` and
`--eebus-pairing-window-mode=closed`; neither value is operator-configurable
through add-on options. The add-on does not expose certificate, private-key,
or trust-store paths. The runtime owns all protected material below the fixed
state root.

When `eebus_enabled=false`, the wrapper emits no `--eebus-*` argument. The
existing eBUS transport, HTTP, GraphQL, MCP, mDNS, proxy, and semantic-cache
arguments remain byte-for-byte independent of the dormant eeBUS product.

## Fail-Closed Activation

Before invoking the gateway with eeBUS enabled, the wrapper MUST prove that
the selected binary advertises every required eeBUS flag. A missing flag,
blank interface, empty subnet set, invalid listen port, or invalid allowlist
stops startup with an operator-visible error. The wrapper never silently drops
an enabled eeBUS request and never widens an empty interface or subnet to all
host networks.

Input normalization is deliberately bounded. The interface is trimmed but is
not inferred. Subnet and allowlist strings are trimmed and passed to the
gateway parser, which remains authoritative for prefix and peer-identity
validation, deduplication, and stable ordering. Secrets are not accepted
through add-on options, environment variables, or process arguments.

During an in-place upgrade, Supervisor may temporarily answer configuration
lookups from its cached pre-eeBUS schema while the protected
`/data/options.json` already contains the new fields. The wrapper MAY recover
only an eeBUS field whose normal configuration lookup is missing or null from
that protected file. It MUST NOT replace a non-empty lookup value, recover
non-eeBUS fields through this path, or bypass any validation below. A recovered
invalid interface, subnet set, port, allowlist, or unsupported gateway binary
fails identically to the normal configuration path.

Fallback decoding preserves JSON presence and type. JSON `null` means absent,
while the string `"null"` remains a string and is validated as such. Boolean,
integer, and string options MUST match the types declared by the add-on schema;
wrong-typed protected values stop startup. Boolean gateway options use one
`-flag=value` argument so Go flag parsing cannot interpret the value as a
positional argument and ignore later trust or identity options.

Protected string values containing U+0000 MUST be rejected by the JSON decoder
before shell capture. The wrapper cannot rely on post-capture validation
because shell command substitution removes NUL bytes and could otherwise
transform an invalid identity or network selector into a different value.

Before protected material is loaded, the wrapper recreates a deterministic
container machine identity using this frozen algorithm:

1. read `/sys/class/net/<eebus_interface>/address` after the interface name has
   passed the single-component allowlist `[A-Za-z0-9_.:-]+`;
2. remove colon, carriage-return, and newline bytes, convert ASCII `A-F` to
   lowercase, and require exactly 12 lowercase hexadecimal bytes;
3. concatenate the exact ASCII domain-separation bytes
   `helianthus-eebusreg-ha-v1:` with those 12 bytes, with no separator or
   terminator;
4. compute SHA-256 and encode all 32 digest bytes as 64 lowercase hexadecimal
   bytes; and
5. write those 64 bytes plus one line-feed byte to `/etc/machine-id`, then set
   its mode to `0444`.

For the synthetic normalized interface identity `020000000001`, the canonical
input is `helianthus-eebusreg-ha-v1:020000000001` and the file value is
`8a4c331847003c7bacbfa7f2f383cc8b49126d9b1ad071cf97a4ab39c6d12f7c`.

This preserves access to host-bound key material across container recreation.
Neither the interface identity nor the derived machine identity is logged or
exposed through an API.

## Persistence And Restart Gate

The protected `/data/eebus` tree and Home Assistant option values survive
container recreation. Acceptance requires all of the following on one exact
gateway build:

1. initial startup binds the configured address and port and publishes
   discovery only after the listener is ready;
2. the authorized local operator MCP reports the expected paired service,
   session, device, entities, features, and use-case claims;
3. a full add-on restart recreates the process from the image-owned wrapper;
4. the same host-bound machine identity, local certificate identity, trusted
   peer identity, observed protocol-service identity, and pairing state reload
   from `/data/eebus` without a new trust action; and
5. the runtime returns to `ready` and the remote session reconnects.

A service-only restart can test gateway lifecycle handling, but it cannot
satisfy item 3. Public evidence records only redacted identifiers and network
references. Exact identities and protocol addresses remain visible only on
the authorized local operator surface.

## API And Security Boundary

The local operator socket keeps `mask_tier=raw` and the effective
`eebus.raw.read` authorization scope. Public HTTP MCP remains redacted and
cannot dereference a raw snapshot. Snapshot references remain bound to the
runtime, contract, tool scope, mask tier, and authorization scope.

No tier exposes private keys, PEM private material, tokens, credential-store
bytes, or trust-store bytes. SKI, SHIP ID, SPINE addresses, feature metadata,
and use-case claims are operational protocol data on the local authorized
surface; public evidence replaces them with redacted references.
