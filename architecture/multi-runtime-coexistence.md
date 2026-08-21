---
canonical_source: "Project-Helianthus/helianthus-docs-eebus:architecture/multi-runtime-coexistence.md"
owner_domain: "architecture"
license: "AGPL-3.0-only"
publication_status: "active"
claim_status: "evidence-backed"
source_class: "derived_inference"
evidence_ids: "EV-20260711-001"
hypothesis_status: "publishable"
falsifier: "A publishable canonical coexistence contract changes the M8 authority, isolation, or scope boundaries summarized here."
cross_seed_target: "Project-Helianthus/helianthus-docs-ebus:docs/platform/multi-runtime-coexistence-no-drift-v1.md"
cross_seed_mode: "summary-only"
cross_seed_snapshot: "Project-Helianthus/helianthus-docs-ebus@9cede4c61a4f73019142b7418cf6f87537cf645c:docs/platform/multi-runtime-coexistence-no-drift-v1.md"
stable_navigation: "true"
search: "true"
sitemap: "true"
versioned_bundle: "true"
release_bundle: "true"
---

# eeBUS Multi-Runtime Coexistence

Helianthus runs eBUS and eeBUS concurrently with separate raw surfaces. In the
M8 boundary, promoted eBUS leaves remain authoritative, while eeBUS candidate
and conflict facts stay in raw/debug evidence. The canonical contract records
no eBUS consumer drift across its protected views and rollback profile.

Canonical platform source:
[M8 coexistence no-drift v1](https://github.com/Project-Helianthus/helianthus-docs-ebus/blob/9cede4c61a4f73019142b7418cf6f87537cf645c/docs/platform/multi-runtime-coexistence-no-drift-v1.md)

## Local Reading

This page is an eeBUS navigation summary for the platform-owned M8 contract.
The eeBUS side remains raw-first, and candidate or conflict visibility remains
separate from promoted eBUS output and stable consumer surfaces.

M8 records no semantic promotion, protocol translation, write path, or new
consumer exposure. It does not authorize M8.5 or M9, including GraphQL,
Portal, Home Assistant, or command-routing rollout.

## Driver Lifecycle Coexistence

The DriverManager target presents eeBUS as an independently managed lane beside
eBUS and Modbus. Driver state and process readiness remain separate dimensions,
with shared consumer availability described independently from eeBUS listener,
discovery, session, and partner state. The unpublished candidate operator-admin
contract contains the lifecycle state, failure-isolation, generation,
durable-state, and transient-action rules.

Partner presence is not driver readiness. The current environmental acceptance
may state `VR940 is physically offline`; this is operator-supplied lab context,
not protocol evidence. In that condition `READY` with `connected_count=0` is
valid when the eeBUS listener and discovery facilities are healthy. It is not a
driver degradation, no SPINE topology is expected, and the condition does not
authorize synthetic topology or automatic pairing. A connected partner may be
useful later for live SHIP/SPINE acceptance, while independent driver lifecycle
and process coexistence have a separate evidence boundary.
