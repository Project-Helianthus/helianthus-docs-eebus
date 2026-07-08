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
- private artifact location if one exists outside public git;
- redaction mode;
- publication status;
- falsification criteria.

## Artifact Classes

- `private_operator`: may contain sensitive data; never committed.
- `shareable_redacted`: safe to commit after redaction gate.

Private artifacts are not evidence for public claims until a redacted,
publishable evidence entry exists.
