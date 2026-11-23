---
canonical_source: "Project-Helianthus/helianthus-docs-eebus:protocols/ship-spine-overview.md"
owner_domain: "protocols"
license: "CC0-1.0"
publication_status: "publishable"
claim_status: "evidence-backed"
source_class: "derived_inference"
evidence_ids: "EV-20260714-001,EV-20260720-001"
hypothesis_status: "publishable"
contract_status: "normative"
live_validation_status: "pending"
falsifier: "A cited clause of SHIP Specification 1.0.1 or SPINE 1.3.0 disagrees with the declared discovery, transport or detailed discovery, or a recorded verification level is treated as a condition on that declaration."
---

# Canonical Discovery For SHIP And G17/G19 Interop Gates

## Scope And Classification

Discovery, SHIP transport and SPINE detailed discovery are declared from
[SHIP Specification 1.0.1](ship-1.0.1.md) and
[SPINE Protocol Specification 1.3.0](spine-protocol-1.3.0.md).
The later revision [SHIP Specification 1.1.0](ship-1.1.0.md), the
[SHIP Pairing Service 1.0.0](ship-pairing-service-1.0.0.md), the
[SHIP Requirements for Installation Process 1.1.0](ship-installation-requirements-1.1.0.md),
the [SPINE Introduction 1.3.0](spine-introduction-1.3.0.md) and the
[SPINE Resource Specification 1.3.0](spine-resources-1.3.0.md) are recorded
beside that declaration. A live run is a recorded verification level (run, not
run, result) and conditions nothing. This page does not establish deployed support, or a consumer surface.

## Canonical Local Advertisement

SHIP 1.0.1 §7 states the discovery requirements. It prints
no fixed number of advertisements and no universal device type. The service
name is `ship`. The instance is a user-facing name of at most 63 bytes and is
re-chosen on a collision. The SHIP id is the separate identifier of at most 63
bytes, so a renamed instance with the same SHIP id is the same node.

The mandatory TXT keys are `txtvers` (first key, value 1), `id`, `path`, `ski`
and `register`. The optional keys are `brand`, `type` and `model`, and further
optional keys are each optional, all within the TXT record limit of 400 bytes.
Unknown keys are ignored, and an announcement without `type` is conformant. An announcement with a permitted additional key within 400 bytes is conformant.

| Key | Presence | Rule |
| --- | --- | --- |
| `txtvers` | mandatory, first | value 1 |
| `id` | mandatory | SHIP id, at most 63 bytes |
| `path` | mandatory | 1 to 32 bytes |
| `ski` | mandatory | certificate subject key identifier |
| `register` | mandatory | equals the auto-accept state |
| `brand` | optional | at most 32 bytes |
| `type` | optional | at most 32 bytes; not a device-type list |
| `model` | optional | at most 32 bytes |

`id` is the canonical SHIP id derived from the protected `StoreInstance`.
`ski` is the current certificate subject key identifier and has a separate
lifecycle. The DNS-SD instance is not an identity. The advertised address and
port equal the bound listener.

`register` is the mandatory Boolean that indicates whether auto accept is
active. The node sets it to true while auto accept is active and to false when
it is not. Only auto accept changes it. `register=true` with auto accept
inactive is not conformant. `register=false` with auto accept inactive is
conformant. The local pairing window (`OPEN_EMPTY`, `CANDIDATE_PENDING` and
`TRANSIENT_TRUSTED` advertise `register=true` while `auto-accept` remains
`false`) is an implementation divergence from that meaning. A local-window
toggle of `register` is not the conformance operand.

The SPINE standard or vendor-specific type check applies to
`deviceInformation.description.deviceType`. The SHIP TXT `type` stays optional
and no clause read for this row ties it to that list.

## G17: Recorded Announcement Observation

A recorded verification level may note the following. It conditions nothing.

- an independent observer resolves the announcement's instance name and TXT
  keys against the mandatory keys, the optional keys present and the 400-byte
  limit, with no required `type` and no fixed instance;
- the observer checks that `register` equals the node's auto-accept state;
- withdrawal is observed with exact `TTL=0`; and
- the post-withdrawal negative confirms no inbound connection attributable to
  the withdrawn announcement.

The announcement alone creates no remote session or pairing candidate.

### Protected Registration Signal

`register` is the mandatory Boolean that indicates whether auto accept is
active. It does not mean that the peer is trusted and does not enable
automatic handshake acceptance. Opening the local pairing window does not queue, report, or dial a remote and cannot create a remote service, session,
topology row, or candidate. That window's `register=true` while auto accept
stays inactive is an implementation divergence.

When the bounded lifecycle closes, expires, or reaches a terminal effect, the
service must withdraw or replace the announcement with `register=false`. No pairing-window
transition selects a peer or schedules transport work.

## G19: Pending Inbound Transport Gate

G19 starts with the live peer initiating TCP and Helianthus accepting that
connection. The gate requires ordered TCP, SHIP, and first redacted SPINE-stage
evidence from one live run and connection generation. Evidence from another
run or generation cannot complete the gate. The first SPINE evidence proves
only that data reached the raw redacted boundary and receives no semantic
meaning.

## Observation Provenance

Authorization policy and observed network state have separate provenance. An
allowlisted SKI may permit later transport handling, but it cannot create a
visible service, session, pairing candidate, address observation, or topology
row. Discovery observations and allowlist evaluation never initiate an outbound
dial or pairing attempt.

An mDNS observation callback may create a visible remote service. Only an
actual connection callback may create a session. Only the pairing callback
from an active transport connection may create the single volatile pairing
candidate. A service observation cannot imply a session, and neither policy
configuration nor an open local registration window can stand in for a live
callback.

## Repair Stability Gate

After a real host-key and certificate repair, the certificate SKI must change.
The decoded raw 32-byte `StoreInstance`, derived `nodeToken` and canonical SHIP
ID must remain exactly unchanged. The next advertisement carries the unchanged
`id` and the changed `ski`, each checked independently of the display name.
There is no equality of the DNS-SD instance. Failure of any required equality
or inequality check fails the gate.

## Run Binding And Redaction

A valid proof is bound to a fresh run challenge, bounded acceptance window,
redacted listener and expected-peer references, and transport evidence from
that run. Public evidence contains stage results, counts, protected-reference
comparisons, and authority labels. It omits packet captures, raw transcripts,
private addresses, actual store identity, actual SHIP ID, and raw peer
identity.

This contract is tracked by
[docs issue 48](https://github.com/Project-Helianthus/helianthus-docs-eebus/issues/48)
and
[runtime issue 54](https://github.com/Project-Helianthus/helianthus-eebusreg/issues/54).
A live run is a recorded verification level and is not admission.
