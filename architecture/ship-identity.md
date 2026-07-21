---
canonical_source: "Project-Helianthus/helianthus-docs-eebus:architecture/ship-identity.md"
owner_domain: "architecture"
license: "AGPL-3.0-only"
publication_status: "publishable"
claim_status: "evidence-backed"
source_class: "derived_inference"
evidence_ids: "EV-20260714-001,EV-20260720-001"
hypothesis_status: "publishable"
falsifier: "A bounded publishable run shows that restart-stable local identity or observation provenance requires a different ownership boundary."
---

# Canonical Local Identity Contract

## Identity Ownership

The production runtime keeps these concepts independent:

| Concept | Canonical owner and meaning |
| --- | --- |
| Certificate SKI | Fingerprint of the currently active transport certificate. Certificate replacement may change it. |
| Protected `StoreInstance` | Persisted local store identity. It is protected runtime material and stays outside public output. |
| Alternate SHIP ID | Restart-stable protocol-service identity derived from the protected `StoreInstance`. |
| DNS-SD instance | Human-facing local service label used for discovery. It is not a certificate or trust identifier. |
| Authorization policy | Allowlists and configured endpoints constrain permitted behavior. They are not remote observations. |
| Observed runtime state | Services, sessions, and pairing candidates come only from their corresponding live callbacks. |

## Durable Node Token

The runtime derives one `nodeToken` as the lowercase hexadecimal encoding of
the first 16 bytes of this digest:

```text
SHA256("helianthus-eebus-node-v1\0" || protected persisted StoreInstance)
```

The canonical format for the alternate protocol-service identifier is
`HLS-<nodeToken>`. The `nodeToken` and alternate SHIP ID remain unchanged across
ordinary restart and certificate replacement because certificate SKI is not an
input to the derivation. The protected `StoreInstance`, raw digest, and actual
token stay outside public evidence.

## Observation Ownership

Policy configuration has no observation authority. An mDNS callback may create
a visible service. An actual connection callback may create a session. A
pairing callback backed by that transport connection may create the single
volatile candidate. Opening the bounded local pairing window changes the local
registration signal and starts no remote queue or dial.

The canonical discovery fields and callback ordering are defined by the
[discovery contract for SHIP](../protocols/ship-spine-overview.md). Shareable output
uses the closed `eebus.v1` read-only surface and remains raw and redacted, with
no semantic promotion.
