---
canonical_source: "Project-Helianthus/helianthus-docs-eebus:architecture/README.md"
owner_domain: "architecture"
license: "AGPL-3.0-only"
publication_status: "active"
claim_status: "evidence-backed"
source_class: "derived_inference"
evidence_ids: "EV-20260711-001, EV-20260714-001, EV-20260720-001"
hypothesis_status: "publishable"
falsifier: "A publishable canonical contract changes these ownership or evidence-acceptance boundaries."
cross_seed_target: "Project-Helianthus/helianthus-docs-ebus:docs/platform/shared-registry-boundary.md"
cross_seed_mode: "summary-only"
cross_seed_snapshot: "Project-Helianthus/helianthus-docs-ebus@153191f72b5b9ecacbadcf2f3d7e480c6fef89a4:docs/platform/shared-registry-boundary.md"
stable_navigation: "true"
search: "true"
sitemap: "true"
versioned_bundle: "true"
release_bundle: "true"
---

# Supported eeBUS Architecture

This page defines the supported documentation and integration boundary for the
Helianthus eeBUS adapter. It does not assert a package layout, runtime symbol,
transport implementation, or deployed consumer behavior.

## Local Boundary

The eeBUS architecture surface owns adapter-specific runtime lifecycle, trust,
persistence, and the preservation of eeBUS-native records. Protocol behavior
stays in `protocols/`; public Go shape stays in the active
[API surface v1 contract](../api/api-surface-v1.md).

Language-neutral registry semantics remain outside this repository. The
canonical source is the
[shared registry boundary](https://github.com/Project-Helianthus/helianthus-docs-ebus/blob/153191f72b5b9ecacbadcf2f3d7e480c6fef89a4/docs/platform/shared-registry-boundary.md).
This page records only where the local adapter hands responsibility to that
platform contract.

The [canonical local identity contract](ship-identity.md) defines separate
ownership for the protected local store, certificate identity,
protocol-service identity, discovery label, authorization policy, and observed
runtime state.

## Claim Register

| Status | Local statement | Evidence class | Evidence | Falsifier |
|---|---|---|---|---|
| Supported | This repository owns eeBUS adapter architecture and native runtime concerns. | `derived_inference` | `EV-20260711-001` | A publishable ownership decision assigns the surface elsewhere. |
| Supported | Cross-runtime registry semantics remain platform-owned. | `derived_inference` | `EV-20260711-001` and the canonical link above | The canonical platform ownership manifest withdraws or moves that contract. |
| Supported | G17 and G19 use live-run authority; CI replay has separate authority for deterministic negative cases. | `observed_runtime` | `EV-20260714-001` | A later accepted public gate contract merges those evidence authorities. |
| Supported | Run proof binds a fresh challenge and bounded window to one run, while G19 transport and first redacted SPINE evidence bind to one connection generation. | `derived_inference` | `EV-20260714-001` | An accepted public gate contract permits stale, cross-run, or cross-generation proof. |
| Partial/negative observation | One protected pairing observation recorded only the local registration transition with auto-accept disabled; it recorded no completed candidate, durable trust, trusted reconnect, or device-semantic result. | `observed_runtime` | `EV-20260720-001` | A future independently reproducible redacted observation under the same bounded conditions demonstrates different registration or automatic-accept behavior. |
| Candidate policy | Allowlists and configured endpoints authorize possible transport behavior but create no visible service, session, pairing candidate, or other observation. | `derived_inference` | `architecture/_candidate/msp-04b-first-trust-admin-local.md`; informed but not proven by `EV-20260720-001` | A merged, tested contract permits policy configuration alone to create observed remote state. |
| Canonical identity | Certificate SKI, protected store identity, durable SHIP ID, DNS-SD instance, authorization policy, and observed state retain separate ownership and lifecycles. | `derived_inference` | `EV-20260714-001`, `EV-20260720-001` | A publishable bounded run demonstrates forced shared identity or observation authority between any two concepts. |
| Candidate policy | Unimplemented runtime and API details carry no supported status here. | `derived_inference` | `EV-20260711-001` | A merged implementation and regenerated API surface provide publishable support. |

## Interop Evidence Boundary

G17 records the local Helianthus announcement, independent LAN discovery,
myVaillant trust visibility, and exact `TTL=0` withdrawal/negative. It does not
attribute a server role for SHIP to VR940.

G19 records inbound VR940-to-Helianthus TCP, TLS, WebSocket, and SHIP stages,
then the first redacted SPINE evidence from the same run and connection
generation. The evidence boundary does not promote protocol meaning from that
first data.

Live operator evidence and deterministic CI replay remain separate. A CI replay
can establish deterministic negative handling; it does not replace absent live
transport or trust evidence. A terminal negative/partial report describes one
attempt and does not become a global device claim.

The acceptance contract binds a fresh run challenge, a bounded window,
redacted endpoint and expected-peer references, and transport evidence. Public
material retains redacted references, digests, stage results, and authority
labels while omitting packet captures, raw transcripts, sensitive material,
private addresses, and raw peer identity.

The inspected code worktree proposes concrete challenge, time-window,
connection-generation, transport-digest, and first-SPINE-digest fields. Those
uncommitted representation details remain candidate-only and do not establish
a landed runtime or public API shape.

## API Publication Boundary

The v1 schema contract and synthetic fixtures remain active and unchanged.
Unimplemented reference material is candidate-only; stable navigation, search,
sitemap, versioned bundles, and release bundles omit it.

Identity and discovery changes do not add a semantic projection. Shareable
runtime evidence remains raw, redacted, and available through the `eebus.v1`
closed read-only tool family. Policy configuration has no representation as
observed service, session, topology, pairing, or semantic state.

## M4.5 Roadmap

The [candidate MSP-045 trust/admin projection contract](_candidate/msp-045-trust-admin-projection.md)
freezes the coordinator-owned read-only mapping for downstream conformance. It
is not a support claim, implementation claim, or public API change, and remains
excluded from every stable publication channel.

## M5 Roadmap

The [candidate MSP-05A gateway configuration scaffold](_candidate/msp-05a-gateway-config-scaffold.md)
freezes the disabled-default input shape before runtime integration. It creates
no listener, discovery advertisement, trust state, API, or consumer surface and
remains excluded from every stable publication channel.
