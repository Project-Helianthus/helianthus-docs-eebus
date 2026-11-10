---
canonical_source: "Project-Helianthus/helianthus-docs-eebus:architecture/naming-contract.md"
owner_domain: "architecture"
license: "AGPL-3.0-only"
publication_status: "candidate"
claim_status: "evidence-backed"
source_class: "derived_inference"
evidence_ids: "EV-20260711-001"
hypothesis_status: "draft"
falsifier: "The public library inventory or implementation differs from this correspondence."
candidate_output: "true"
stable_navigation: "false"
search: "false"
sitemap: "false"
versioned_bundle: "false"
release_bundle: "false"
candidate_output_path: "architecture/naming-contract.md"
---

# eeBUS implementation-name correspondence

This companion specifies implementation names, not new native evidence or device qualification. The complete row inventory, including unchanged and provisional rows and each row's public source proof, is [naming-contract.json](naming-contract.json). The source paths in that inventory refer to the public [eeBUS library](https://github.com/Project-Helianthus/helianthus-eebusreg/tree/main). They identify code evidence, not a claim of native semantic proof. Each identity is an ordered list of colon-separated components; joining them with colons reconstructs the public inventory identity. Provisional rows retain their open questions; an unknown value class or unit remains unknown. Proven, Hypothesis and Unknown describe evidence, not qualification.

## Supported structural change

| Public shape | Previous key | Current contract key | Public code proof |
| --- | --- | --- | --- |
| NativeSnapshotV2 | `usecases` | `use_cases` | [native snapshot](https://github.com/Project-Helianthus/helianthus-eebusreg/blob/main/native_snapshot_v2.go) |
| RawSnapshotV1 (SnapshotV1) | `usecases` | `use_cases` | [raw snapshot](https://github.com/Project-Helianthus/helianthus-eebusreg/blob/main/raw_snapshot_v1.go) |
| RedactedSnapshotV1 | `usecases` | `use_cases` | [redacted snapshot](https://github.com/Project-Helianthus/helianthus-eebusreg/blob/main/redacted_snapshot_v1.go) |

The previous key is documentary correspondence only, never a runtime fallback. No alias, duplicate field, compatibility shim or migration step is supported. The Go `UseCases` members and type names remain unchanged. Public facade packages remain `eebusruntime`, `eebusraw` and `eebusevidence`.

`observed_at`, `data_timestamp`, `device_address`, `entity_address`, `feature_address`, `OpaqueObservationV1.path`, `OpaqueObservationV1.source`, `OpaqueObservationV1.value` and existing snake_case envelope keys remain unchanged. The inventory retains the unchanged structural and identity rows individually. Opaque native object keys, SHIP/SPINE type values and maker strings remain exact raw evidence, outside canonical semantic naming. Preserve native identity and raw bytes, value classes, units, scale, polarity, access, qualification, fail-closed admission and partial last-known-good fields. This correspondence grants no mutation authority or semantic promotion.

The candidate raw view remains a candidate; this spelling change does not promote an older frozen reference. Version and identity namespaces are unchanged. The library and consumers must coordinate this breaking change; eBUS MCP compatibility and GraphQL parity remain required. The surveyed gateway consumer surface includes administration, runtime adapters, synchronized evidence and MCP schemas and fixtures. Matter binding, Home Assistant integration, virtual device and explorer consumer correspondence, including generic passthrough and schema consumers, remains unverified. Consumer source correspondence is not proof that updates have shipped.
