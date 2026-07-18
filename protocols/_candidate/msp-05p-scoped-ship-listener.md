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
It uses publishable G17/G19 transport evidence as an input to a normative
production design. It does not reproduce restricted specifications, publish
private endpoint data, or claim generic eeBUS interoperability.

## Claim Classification

| Claim | Authority |
| --- | --- |
| local-announcement-visible-to-VR940 | observed-G17 |
| inbound-VR940-client-direction | observed-G19 |
| exact-address-bind | normative-design-hypothesis |
| bind-before-publish | normative-design-hypothesis |
| initial-failure-rollback | normative-design-hypothesis |
| post-ready-degradation | normative-design-hypothesis |

G17/G19 supports direction and bounded announcement behavior only. Exact bind
scope, ordering, rollback, and degradation are candidate safety constraints,
not observed requirements attributed to the device or protocol specification.

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
discovery loss is explicit `missing-discovery` degradation. The post-ready
discovery loss retains the exact listener and established sessions and retries
publication with bounded backoff. It cannot report ready or empty success,
widen the listener, open pairing, accept new trust, or terminate an established
session solely because discovery is unavailable.

Discovery advertises reachability only. It does not imply an open pairing
window, trust, authorization, a connected session, or SPINE readiness. Pairing
remains closed in this production prerequisite, and unknown peers cannot turn
an advertisement into persistent trust.

## Isolation And Rollback

This policy is internal transport plumbing. It adds no raw or semantic API and
does not change the eBUS transport path. To roll back, remove
exact-address configuration and retain the single initial constructor. A
rollback withdraws any active candidate publication before closing the exact
listener, then leaves no multicast record, listener, goroutine, or durable
trust mutation.
