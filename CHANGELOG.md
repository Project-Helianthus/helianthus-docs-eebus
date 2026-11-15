---
canonical_source: "Project-Helianthus/helianthus-docs-eebus:CHANGELOG.md"
owner_domain: "repository"
license: "AGPL-3.0-only"
claim_status: "evidence-backed"
source_class: "derived_inference"
evidence_ids: "EV-20260711-001"
hypothesis_status: "draft"
falsifier: "The coordinated implementation differs from this announcement."
publication_status: "ownership-policy"
---

# Changelog

## Unreleased

- Breaking eeBUS library structural JSON name: `usecases` becomes `use_cases` for native, raw and redacted snapshot views. Coordinate consumers in the same wave; no alias, duplicate field, compatibility shim or migration step is provided. Go `UseCases` members and public facade packages remain unchanged. See [the correspondence contract](architecture/naming-contract.md).
- Documentation ownership: the repository README and the architecture overview name the common semantic contract in docs-semantic as the owner of cross-protocol semantics; the docs-ebus shared registry boundary stays the language-neutral registry write boundary and owns no semantic meaning. The native runtime exposure candidate now says that semantic promotion is a separate step that selects what is promoted, and the repository policy validator pins that wording. No alias, compatibility shim or migration step is provided.
- Native relations and participation: the multi-leaf source inventory candidate states, for each bundle, the observed zone-to-room, circuit-to-system-function and setpoint-to-measurement relations with the native field that carries them, or `none_observed`, and declares slot labels local to their bundle, never an identity or an ordinal to join on. The participation contract candidate requires `Selection` to resolve to one element of the common element catalog on one canonical resource and every loss to name its declared target, distinct from plane membership; a selection that names no common element and a loss recorded without a target are rejected. The repository policy validator pins these rules. The registry follow-up in helianthus-eebusreg brings the exported participation contract into line with an in-place edit. No contract version is raised; no alias, compatibility shim or migration step is provided.
- Native SPINE snapshot: a new architecture candidate, `architecture/_candidate/native-snapshot-v2.md`, describes the node kinds, containment relations and their validation rule, the bounded absence records and the identity basis per node kind of the library's native snapshot v2, as native relations rather than common-graph relations. The SKI stays a trust record, never identity. The naming contract gains unchanged rows for the containment, absence and identity-basis keys. Promotion of the page into the stable channel is a later step of the publication procedure. No contract version is raised; no alias, compatibility shim or migration step is provided.
