---
canonical_source: "Project-Helianthus/helianthus-docs-eebus:architecture/README.md"
owner_domain: "architecture"
license: "AGPL-3.0-only"
publication_status: "active"
claim_status: "evidence-backed"
source_class: "derived_inference"
evidence_ids: "EV-20260711-001"
hypothesis_status: "publishable"
falsifier: "A publishable canonical contract assigns these boundaries to another owner."
cross_seed_target: "Project-Helianthus/helianthus-docs-ebus:docs/platform/shared-registry-boundary.md"
cross_seed_mode: "summary-only"
cross_seed_snapshot: "Project-Helianthus/helianthus-docs-ebus#342"
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
[shared registry boundary](https://github.com/Project-Helianthus/helianthus-docs-ebus/blob/main/docs/platform/shared-registry-boundary.md).
This page records only where the local adapter hands responsibility to that
platform contract.

## Claim Register

| Status | Local statement | Evidence class | Evidence | Falsifier |
|---|---|---|---|---|
| Supported | This repository owns eeBUS adapter architecture and native runtime concerns. | `derived_inference` | `EV-20260711-001` | A publishable ownership decision assigns the surface elsewhere. |
| Supported | Cross-runtime registry semantics remain platform-owned. | `derived_inference` | `EV-20260711-001` and the canonical link above | The canonical platform ownership manifest withdraws or moves that contract. |
| Candidate policy | Unimplemented runtime and API details carry no supported status here. | `derived_inference` | `EV-20260711-001` | A merged implementation and regenerated API surface provide publishable support. |

No implementation hypothesis is promoted by this page. A later hypothesis
stays candidate-only and carries its own publishable evidence class and
testable falsifier.

## API Publication Boundary

The v1 schema contract and synthetic fixtures remain active and unchanged.
Unimplemented reference material is candidate-only; stable navigation, search,
sitemap, versioned bundles, and release bundles omit it.
