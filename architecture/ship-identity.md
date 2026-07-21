---
canonical_source: "Project-Helianthus/helianthus-docs-eebus:architecture/ship-identity.md"
owner_domain: "architecture"
license: "AGPL-3.0-only"
publication_status: "publishable"
claim_status: "evidence-backed"
source_class: "derived_inference"
evidence_ids: "EV-20260714-001,EV-20260720-001"
hypothesis_status: "publishable"
contract_status: "normative"
live_validation_status: "pending"
falsifier: "A bounded publishable run shows that restart-stable local identity or observation provenance requires a different ownership boundary."
---

# Canonical Local Identity Contract

## Identity Ownership

The production design keeps these concepts independent:

| Concept | Canonical owner and meaning |
| --- | --- |
| Certificate SKI | Fingerprint of the currently active transport certificate. Host-key or certificate repair changes it. |
| Protected `StoreInstance` | Persisted 32-byte local store identity. It is protected runtime material and stays outside public output. |
| Canonical SHIP ID | Restart-stable protocol-service identity derived only from the protected `StoreInstance`. Its format is `HLS-<nodeToken>`. |
| DNS-SD instance | Human-facing local service label used for discovery. It is not a certificate or trust identifier. |
| Authorization policy | The authorization allowlist constrains permitted transport handling. It is not a remote observation. |
| Observed runtime state | Services, sessions, and pairing candidates come only from their corresponding live callbacks. |

## Exact Node Token Bytes

The persisted `StoreInstance` has one canonical encoded representation. The
runtime decodes that representation to a decoded raw 32-byte `StoreInstance`
before derivation. The hash input is exactly this byte sequence:

```text
ASCII("helianthus-eebus-node-v1") || single NUL byte || decoded raw 32-byte StoreInstance
```

The single NUL byte is exactly `0x00`. There is no trailing terminator, length
prefix, encoded text, whitespace, certificate byte, or host-key byte in the
hash input. The result is:

```text
nodeToken = lowercase_hex(first_16_bytes(SHA-256(hash_input)))
canonical SHIP ID = "HLS-" || nodeToken
```

`nodeToken` is therefore exactly 32 lowercase hexadecimal characters.

## Known Vector

For this decoded raw 32-byte `StoreInstance`:

```text
000102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f
```

the complete SHA-256 digest is:

```text
829b6a31d06778a73e1be775912663953b561c1e30fd6d2dbc8eacbc453e787b
```

and the required values are:

```text
nodeToken = 829b6a31d06778a73e1be77591266395
HLS-829b6a31d06778a73e1be77591266395
```

## Repair Stability

A real host-key and certificate repair replaces the protected host key and
certificate. The certificate SKI must change. The raw 32-byte `StoreInstance`
must remain byte-for-byte unchanged, `nodeToken` must remain exactly unchanged,
and the canonical SHIP ID must remain exactly unchanged. If the protected
`StoreInstance` cannot be recovered exactly, that repair fails closed rather
than creating a different store identity within the same operation.

The DNS-SD instance also remains
`Helianthus EnergyManagementSystem eebusreg`. It is a fixed human-facing label,
not a value derived from the certificate or store.

## Observation Ownership

Policy configuration has no observation authority. An mDNS callback may create
a visible service. An actual connection callback may create a session. A
pairing callback backed by that transport connection may create the single
volatile candidate. Opening the bounded local pairing window changes the local
registration signal and starts no remote queue or dial.

The canonical discovery fields and callback ordering are defined by the
[discovery contract for SHIP](../protocols/ship-spine-overview.md). Shareable
output uses the closed `eebus.v1` read-only surface and remains raw and
redacted, with no semantic promotion. The design is normative and derived;
live validation remains pending.
