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

1. An independent observer resolves the announcement's instance name and TXT
   keys on `end0` at `<redacted-lab-address>:4712` against the mandatory keys
   `txtvers` (first, value 1), `id`, `path`, `ski` and `register`, the optional
   keys present, and the 400-byte limit. Here an announcement without `type` is valid.
   A renamed instance with the same SHIP id is valid. The instance is
   not a fixed name. The rules are the
   [protocol discovery page](../protocols/ship-spine-overview.md).
2. `register` equals the node's auto-accept state and creates no remote queue,
   dial, service, session, topology row, or pairing candidate.
   `register=true` with auto accept inactive is not conformant.
   `register=false` with auto accept inactive is conformant. A local-window
   toggle of `register` is not the conformance operand.
3. Before the first observed TCP SYN, `eebus.v1.sessions.list` is empty. A
   visible service may exist only after its mDNS observation callback.
4. The expected VR940 certificate `ski` matches its exact protected reference.
   Public output records only the redacted reference and pass/fail result.
5. Packet and runtime-stage evidence establishes TCP first, then SHIP, then the
   first redacted SPINE payload on the same connection generation. No SPINE
   payload receives semantic meaning.
6. After ordinary runtime restart, the decoded raw 32-byte `StoreInstance`,
   `nodeToken` and canonical SHIP ID remain exactly unchanged. The DNS-SD
   instance is not an identity equality. Durable policy reloads privately;
   service, session, topology, and candidate observations remain absent until
   their live callbacks recur.
7. After a real host-key and certificate repair, certificate SKI must change,
   while the raw 32-byte `StoreInstance` must remain byte-for-byte unchanged,
   `nodeToken` must remain exactly unchanged, and the canonical SHIP ID must
   remain exactly unchanged. The repaired advertisement carries the unchanged
   `id` and changed `ski`, each checked independently of the display name.
   There is no equality of the DNS-SD instance.

| TXT key | Presence |
| --- | --- |
| `txtvers` | mandatory, first, value 1 |
| `id` | mandatory |
| `path` | mandatory |
| `ski` | mandatory |
| `register` | mandatory, equals auto accept |
| `brand`, `type`, `model` | optional |

A live run of this procedure is a recorded verification level and is not
admission. This text does not authorize or perform field activity.

The evidence artifact uses only the closed stable `eebus.v1` read-only tools.
It retains raw stage ordering, counts, redacted references, equality and
inequality results, and pass/fail. It omits private addresses, literal
fingerprints, packet captures, protected store bytes, actual SHIP ID, raw peer
identities, and promoted semantics.
