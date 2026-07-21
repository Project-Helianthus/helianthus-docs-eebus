---
canonical_source: "Project-Helianthus/helianthus-docs-eebus:evidence/README.md"
owner_domain: "evidence"
license: "CC0-1.0"
claim_status: "no-protocol-claims"
publication_status: "evidence-policy"
---

# eeBUS Evidence Catalog

Evidence files in this directory are publishable only after redaction and
provenance review.

## Evidence Id Format

Use ids like `EV-YYYYMMDD-NNN`.

## Required Metadata

Every evidence entry records:

- evidence id;
- source class;
- capture date;
- device family;
- firmware/app/runtime versions when known;
- acquisition method;
- whether a private artifact is retained (`yes` or `no`), without its location,
  filename, hash, or identifier;
- redaction mode;
- publication status;
- falsification criteria.

## Artifact Classes

- `private_operator`: may contain sensitive data; never committed.
- `shareable_redacted`: safe to commit after redaction gate.

Private artifacts are not evidence for public claims until a redacted,
publishable evidence entry exists.

## Runtime Evidence Boundary

Shareable runtime evidence uses only the closed `eebus.v1` read-only contract
and remains raw and redacted. It does not publish certificate SKIs, durable SHIP
IDs, `nodeToken` values, protected `StoreInstance` material, private network
coordinates, or stable peer fingerprints. Exact
identity comparisons are recorded as pass/fail against protected redacted
references.

Policy is not observation evidence. An allowlist, durable association, or open
local pairing window cannot by itself produce a visible
service, session, pairing candidate, topology record, or protocol-stage claim.
Published service evidence requires an mDNS observation, session evidence
requires a connection callback, and candidate evidence requires a
transport-backed pairing callback.

No evidence entry promotes SPINE payloads into device semantics. Semantic
interpretation requires a separate documented promotion gate outside this raw
runtime contract.
