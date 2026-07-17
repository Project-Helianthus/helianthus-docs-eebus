---
canonical_source: "Project-Helianthus/helianthus-docs-eebus:protocols/_candidate/msp-05p-scoped-ship-listener.md"
owner_domain: "protocols"
license: "CC0-1.0"
publication_status: "candidate"
claim_status: "evidence-backed"
source_class: "derived_inference"
evidence_ids: "EV-20260714-001"
hypothesis_status: "draft"
falsifier: "A bounded publishable transport run proves that wildcard binding, advertise-before-bind, or discovery-coupled pairing is required for interoperable SHIP/SPINE operation."
stable_navigation: "false"
search: "false"
sitemap: "false"
versioned_bundle: "false"
release_bundle: "false"
---

# Candidate MSP-05P Scoped SHIP/SPINE Listener Policy

## Status And Evidence Boundary

This candidate is tracked by
[issue 36](https://github.com/Project-Helianthus/helianthus-docs-eebus/issues/36).
It derives a production listener policy from publishable G17/G19 evidence. It
does not reproduce restricted specifications, publish private endpoint data,
or claim generic eeBUS interoperability.

The listener accepts inbound SHIP only on the one address selected by the
gateway-to-runtime mapping. It never binds an unspecified or wildcard address.
Interface, address, port, listener state, and discovery state remain separate
observations rather than inferred aliases.

## Listener And Discovery Policy Matrix

| Listener requested | Discovery requested | Socket result | mDNS result |
| --- | --- | --- | --- |
| `false` | `false` | `none` | `none` |
| `true` | `false` | `exact-address` | `none` |
| `true` | `true` | `exact-address` | `publish-after-bind` |
| `false` | `true` | `reject` | `none` |

For an active publication, the advertised address and port equal the bound
endpoint. The mDNS publication starts only after a successful bind and never repairs or
widens a failed bind. Normal shutdown and startup rollback perform withdrawal
with `TTL=0` before listener close when a publication was active.

An initial publication failure rolls back the listener and returns
`discovery_unavailable`; no ready state is emitted. After ready, post-ready
discovery loss is explicit `missing-discovery` degradation. The runtime keeps
the exact listener only when policy permits degraded operation, retries with
bounded backoff, and never reports an empty success.

Discovery advertises reachability only. It does not imply an open pairing
window, trust, authorization, a connected session, or SPINE readiness. Pairing
remains closed in this production prerequisite, and unknown peers cannot turn
an advertisement into persistent trust.

## Isolation And Rollback

This policy is internal transport plumbing. It adds no raw or semantic API and
does not change the eBUS transport path. To roll back, remove
listener/discovery policy additions and retain the legacy constructor. A
rollback withdraws any active candidate publication before closing the exact
listener, then leaves no multicast record, listener, goroutine, or durable
trust mutation.
