---
canonical_source: "Project-Helianthus/helianthus-docs-eebus:protocols/ship-spine-overview.md"
owner_domain: "protocols"
license: "CC0-1.0"
---

# SHIP/SPINE Overview For Helianthus eeBUS

## Scope

This page records Helianthus observations about eeBUS SHIP/SPINE behavior. It
starts as a placeholder for publishable, redacted runtime evidence from the
VR940f/myVaillant track.

## Raw-First Rule

Helianthus treats `enbility/eebus-go` as a SHIP/SPINE runtime facade. It is not
an eBUS-style byte transport. Pairing, trust, SKI, mDNS discovery, sessions,
entities, features, and usecase claims remain native eeBUS runtime concepts.

## Initial Observation Targets

- discovery advertisement;
- SHIP session establishment;
- pairing state;
- remote SKI and SHIP id after redaction;
- SPINE entities;
- features;
- usecase claims;
- reconnect behavior.

## Publication Status

No protocol claim on this page is promoted yet. Claims become publishable only
after evidence ids are linked under `evidence/`.
