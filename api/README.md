---
canonical_source: "Project-Helianthus/helianthus-docs-eebus:api/README.md"
owner_domain: "api"
license: "AGPL-3.0-only"
publication_status: "ownership-landing"
claim_status: "no-protocol-claims"
---

# eeBUS Go API

This directory is the canonical owner for the eeBUS-specific Go public API
schema, reference, and examples.

The versioned [API surface v1 contract](api-surface-v1.md) defines the closed
machine-readable shape, deterministic normalization rules, and synthetic
golden fixtures.

## Frozen reference and current implementation

The [Frozen eeBUS Runtime API v1 reference](eebusruntime-v1/reference.md)
describes the API at the source revision identified by its adjacent
[publication record](eebusruntime-v1/publication-record.json). That record and
[frozen manifest](eebusruntime-v1/manifest.json) bind the published reference
to its source and provenance evidence. The manifest contains 278 declarations
across the root `eebusruntime` package and the `eebusraw` and `eebusevidence`
subpackages. This is a frozen published API reference, not a live mirror of
`helianthus-eebusreg` main.

The [Current eeBUS runtime implementation](https://github.com/Project-Helianthus/helianthus-eebusreg/tree/main)
has moved beyond that published pin. Known differences include the
`MutationLabProfiles []eebusraw.MutationLabProfileV1` field added to `Config`
and `RawFeatureRuntimeV1` embedded by `Runtime`. The source branch also includes
`admin_v1.go`, `native_runtime_v2.go`, `native_snapshot_v2.go`,
`participation_driver_v1.go`, and raw snapshot and mutation files beyond the
frozen inventory. Consult that branch for evolving declarations; this summary
is not an exhaustive current export inventory.

These navigation notes do not regenerate the frozen bundle, publish a new API
version, or refresh its attestation. The reference, manifest and publication
record remain unchanged. This landing page and the schema fixtures do not add
runtime, protocol, consumer, or deployment claims.

The candidate inventory currently includes `msp-06-eebus-mcp-v1.md`. Candidate
entries are intentionally not links and remain excluded from stable navigation
and publication bundles.
