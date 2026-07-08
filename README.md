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

## Start Here

- [development/contributing.md](development/contributing.md)
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

Publishable eeBUS protocol facts and reverse-engineered evidence notes are
intended for permissive public documentation. Helianthus implementation
guidance remains project documentation. The provenance policy in
[development/contributing.md](development/contributing.md) decides what can be
published and what must remain out of public repositories.
