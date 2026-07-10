---
canonical_source: "Project-Helianthus/helianthus-docs-eebus:README.md"
owner_domain: "repository"
license: "AGPL-3.0-only"
---

# Helianthus eeBUS Documentation

This repository is the canonical home for Helianthus eeBUS-native protocol,
device, discovery, and evidence documentation.

It owns:

- SHIP/SPINE discovery notes;
- eeBUS service and feature observations;
- VR940f/myVaillant raw evidence;
- eeBUS reverse-engineering notes;
- publishable eeBUS protocol facts.

It does not own cross-protocol Helianthus platform contracts. Platform contracts
live in `helianthus-docs-ebus/docs/platform/` until a future platform docs
repository exists.

## Ownership Policy

Canonical ownership is path-based:

- `protocols/` owns eeBUS/SHIP/SPINE protocol behavior, runtime observations,
  pairing/discovery behavior, SPINE feature graphs, and promoted protocol
  claims.
- `architecture/` owns Helianthus eeBUS runtime, adapter, trust, persistence,
  lifecycle, and integration architecture. It may contain planned scaffolding,
  but noncanonical placeholders must say so explicitly.
- `api/` owns eeBUS-specific Go public API schema, reference, and examples. It
  may contain planned scaffolding, but must not invent API facts.
- `devices/`, `evidence/`, and `re-notes/` remain native owners for device
  pages, redacted evidence records, and reverse-engineering notes.
- `helianthus-docs-ebus/docs/platform/` owns only language-neutral
  cross-runtime contracts. This repo may summarize those contracts only when it
  links to the canonical platform page.

Substantive eeBUS documentation does not belong in code repositories. If a code
repository needs context, it links here or to the platform docs and keeps only
external references, migration notes, or build/runtime-local comments.

The six historical `helianthus-eebusreg` docs paths known at issue #4 time are
noncanonical migration/adjudication inputs only:

- `docs/internal-facade-spike.md`
- `docs/interop-smoke-harness.md`
- `docs/raw-identity-contract.md`
- `docs/security/raw-identity-redaction-gate.md`
- `docs/snapshot-envelope-evidence.md`
- `docs/toolchain-boundary-proof.md`

Ownership is transferred by policy now. MSP-DOCS-E2 later migrates or discards
supported material, and MSP-DOCS-CLEAN later deletes `helianthus-eebusreg/docs/`
and installs the absence gate. This repository must not claim those files are
already physically absent.

Cross-seeding from eeBUS docs to `helianthus-docs-ebus/docs/platform/` is
allowed only for language-neutral cross-runtime contracts. A cross-seed must
name the target platform page, keep the local page summary-only, and pass the
repository policy validator.

Gateway import remains blocked until later canonical docs and runtime contracts
merge. Do not add gateway dependency instructions, GraphQL exposure, HA entity
rollout, or command routing as current behavior in this repository.

## Start Here

- [development/contributing.md](development/contributing.md)
- [architecture/README.md](architecture/README.md)
- [api/README.md](api/README.md)
- [protocols/ship-spine-overview.md](protocols/ship-spine-overview.md)
- [devices/vr940f.md](devices/vr940f.md)
- [evidence/README.md](evidence/README.md)
- [re-notes/template.md](re-notes/template.md)

## Summary-Only Rule

When this repo refers to platform contracts, the page must link to the
canonical `helianthus-docs-ebus/docs/platform/` page and remain summary-only.
It must not duplicate requirements, acceptance criteria, versioning policy, or
approval steps.

## Licensing Intent

Publishable eeBUS protocol facts and reverse-engineered evidence notes use the
CC0-1.0 public-domain lane. Helianthus implementation guidance and repository
policy use the AGPL-3.0-only lane. See [LICENSE](LICENSE) and
[development/contributing.md](development/contributing.md) for the full
publication and provenance rules.
