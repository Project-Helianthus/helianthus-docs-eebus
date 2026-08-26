---
canonical_source: "Project-Helianthus/helianthus-docs-eebus:api/_candidate/msp-138-native-runtime-exposure-v1.md"
owner_domain: "api"
license: "AGPL-3.0-only"
publication_status: "candidate"
claim_status: "evidence-backed"
source_class: "derived_inference"
evidence_ids: "EV-20260711-001"
hypothesis_status: "draft"
falsifier: "A reviewed implementation replaces an implemented native runtime value with a digest-only, redacted, sanitized, or semantic-only projection."
candidate_output: "true"
stable_navigation: "false"
search: "false"
sitemap: "false"
versioned_bundle: "false"
release_bundle: "false"
candidate_output_path: "api/_candidate/msp-138-native-runtime-exposure-v1.md"
---

# Candidate Native eeBUS Runtime Exposure v1

This successor contract defines the active direction for static and runtime
eeBUS boundaries. It supersedes the runtime redaction requirements in the
historical MSP-06, MSP-036, MSP-068, and related HA-wiring candidates without
rewriting their frozen publication records.

The following byte-frozen historical candidates remain available as records,
but their runtime redaction rules are superseded by MSP-138:

- `api/_candidate/msp-06-eebus-mcp-v1.md`
- `api/_candidate/raw-snapshot-view-v1.md`
- `api/_candidate/msp-068-raw-operator-redaction-amendment.md`
- `architecture/_candidate/ha-addon-runtime-wiring.md`

## Native Preservation Boundary

When an implementation has a value, its static/runtime API and MCP boundary
preserve implemented native payloads, identifiers, raw frames, registers, configuration,
and other protocol data. Each value carries its available protocol version,
observation context, and source context. A boundary must not replace a native
value with a digest, hash-only reference, redaction marker, sanitized value, or
semantic substitute.

The API must not select, erase, or rewrite native data merely because it is
sensitive, unknown, candidate-only, or associated with a mutating protocol
operation. Missing data is reported as unavailable with its available native
error/context; it is never fabricated from another observation.

Semantic promotion is a separate selective projection. A semantic consumer may
choose qualified facts, but it does not redefine, remove, or become the only
path to the native record.

## Runtime And Action Boundary

Reading or returning a supported native value does not itself authorize a live
operation. Hardware writes, credentials, deployment, and real I/O retain
action-time operator confirmation. Implementations may construct commands and
exercise fake or replay executors without that confirmation, provided they do
not contact a real device.

Opaque handles for a pending mutation or an action capability remain capability
objects, not replacements for protocol-native observations. They may remain
non-forgeable while the associated native data stays available.

## Public Repository Boundary

The sole redaction boundary is publication into a public repository. Documents,
fixtures, tests, PR text, and examples use synthetic fixtures and must not
contain an operator's actual captures, identifiers, credentials, endpoints,
trust-store material, or lab data. This publication rule does not require a
runtime/API/MCP projection to suppress an implemented native value.

## Migration

The frozen `api/eebusruntime-v1/` publication record remains historical and
byte-identical. Successor implementation work updates its own versioned native
contract in `helianthus-eebusreg`, then updates gateway and consumer bindings
through their normal docs gates. No semantic registry, DriverManager, or
gateway rewrite is implied by this documentation change.
