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
