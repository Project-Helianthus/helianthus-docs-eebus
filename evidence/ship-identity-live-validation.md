---
canonical_source: "Project-Helianthus/helianthus-docs-eebus:evidence/ship-identity-live-validation.md"
owner_domain: "evidence"
license: "CC0-1.0"
publication_status: "publishable"
claim_status: "evidence-backed"
source_class: "derived_inference"
evidence_ids: "EV-20260714-001,EV-20260720-001"
hypothesis_status: "publishable"
falsifier: "A bounded redacted live run violates the canonical advertisement, callback provenance, transport ordering, or restart-persistence gate."
---

# Canonical Live Validation For Local Identity

One bounded run passes only when all observations below are retained under one
fresh run challenge and one connection generation:

1. Exactly one `_ship._tcp` advertisement is observed on `end0` at
   `<redacted-lab-address>:4712`, with DNS-SD instance
   `Helianthus EnergyManagementSystem eebusreg` and the closed TXT field set
   defined by the [protocol discovery page](../protocols/ship-spine-overview.md).
2. Opening the pairing window changes that advertisement to `register=true`
   and creates no remote queue, dial, service, session, topology row, or pairing
   candidate.
3. Before the first observed TCP SYN, `eebus.v1.sessions.list` is empty. A
   visible service may exist only after its mDNS observation callback.
4. The expected VR940 certificate `ski` value matches its exact protected
   reference. Public output records the redacted reference and pass/fail result.
5. Packet and runtime-stage evidence establishes TCP first, then SHIP, then the
   first redacted SPINE payload on the same connection generation. No SPINE
   payload receives semantic meaning.
6. After runtime restart, the protected store produces the same `nodeToken`,
   `HLS-<nodeToken>` alternate protocol-service identifier, and DNS-SD instance.
   Durable trust reloads from the selected store association, while service,
   session, topology, and candidate observations remain absent until their live
   callbacks recur.

The evidence artifact uses only the closed stable `eebus.v1` read-only tools.
It retains raw stage ordering, counts, redacted references, and pass/fail
results. It omits private addresses, the literal peer fingerprint, packet
captures, raw identities, and promoted semantics.
