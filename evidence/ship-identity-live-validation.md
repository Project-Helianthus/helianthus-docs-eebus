---
canonical_source: "Project-Helianthus/helianthus-docs-eebus:evidence/ship-identity-live-validation.md"
owner_domain: "evidence"
license: "CC0-1.0"
publication_status: "publishable"
claim_status: "evidence-backed"
source_class: "derived_inference"
evidence_ids: "EV-20260714-001,EV-20260720-001"
hypothesis_status: "publishable"
contract_status: "normative"
live_validation_status: "pending"
falsifier: "A bounded redacted live run violates the canonical advertisement, callback provenance, transport ordering, or repair-stability gate."
---

# Canonical Live Validation For Local Identity

This is a normative derived gate. It is pending live execution and does not
claim a deployed result or support. One bounded run passes only when all
observations below are retained under one fresh run challenge:

1. Exactly one `_ship._tcp` advertisement is observed on `end0` at
   `<redacted-lab-address>:4712`, with DNS-SD instance
   `Helianthus EnergyManagementSystem eebusreg` and the closed TXT field set
   defined by the [protocol discovery page](../protocols/ship-spine-overview.md).
2. Opening the pairing window changes that advertisement to `register=true`
   and creates no remote queue, dial, service, session, topology row, or pairing
   candidate.
3. Before the first observed TCP SYN, `eebus.v1.sessions.list` is empty. A
   visible service may exist only after its mDNS observation callback.
4. The expected VR940 certificate `ski` matches its exact protected reference.
   Public output records only the redacted reference and pass/fail result.
5. Packet and runtime-stage evidence establishes TCP first, then SHIP, then the
   first redacted SPINE payload on the same connection generation. No SPINE
   payload receives semantic meaning.
6. After ordinary runtime restart, the decoded raw 32-byte `StoreInstance`,
   `nodeToken`, canonical SHIP ID, and DNS-SD instance remain exactly unchanged.
   Durable policy reloads privately; service, session, topology, and candidate
   observations remain absent until their live callbacks recur.
7. After a real host-key and certificate repair, certificate SKI must change,
   while the raw 32-byte `StoreInstance` must remain byte-for-byte unchanged,
   `nodeToken` must remain exactly unchanged, and the canonical SHIP ID must
   remain exactly unchanged. The repaired advertisement carries the unchanged
   `id` and changed `ski`.

The evidence artifact uses only the closed stable `eebus.v1` read-only tools.
It retains raw stage ordering, counts, redacted references, equality and
inequality results, and pass/fail. It omits private addresses, literal
fingerprints, packet captures, protected store bytes, actual SHIP ID, raw peer
identities, and promoted semantics.
