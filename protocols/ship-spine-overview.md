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
falsifier: "A bounded redacted live run violates the canonical advertisement, callback provenance, transport ordering, or identity-repair stability gate."
---

# Canonical Discovery And Candidate Pairing For SHIP

## Scope And Classification

This page defines the Helianthus discovery design and the pending live
acceptance boundary for the G17/G19 gates. Its outbound-candidate rules are a
Helianthus runtime contract for the companion
[`helianthus-ship-go` pull request 15][ship-go-pr], not a generic protocol
claim or a quotation from a restricted EEBUS source. Earlier
evidence informs the gate shape but does not prove this identity or TXT
behavior. This page does not establish deployed support, SPINE semantics, or a
consumer surface.

## Canonical Local Advertisement

The runtime has exactly one canonical SHIP/mDNS publisher. It publishes
exactly one `_ship._tcp` service after the exact listener is bound. Its DNS-SD
instance is:

```text
Helianthus EnergyManagementSystem eebusreg
```

The TXT record has this closed field set:

| Key | Value |
| --- | --- |
| `txtvers` | `1` |
| `path` | `/ship/` |
| `id` | `HLS-<nodeToken>` |
| `ski` | `<certificate SKI>` |
| `brand` | `Helianthus` |
| `model` | `eebusreg` |
| `type` | `EnergyManagementSystem` |
| `register` | `<window>` |

`id` is the canonical SHIP ID derived from the protected `StoreInstance`.
`ski` is the current certificate SKI and has a separate lifecycle. The DNS-SD
instance is a fixed human-facing label and does not participate in either
identity. The advertised address and port equal the one bound listener.
`<window>` is `true` only while the bounded local registration window is open;
otherwise it is `false`. No second publisher, probe identity, or advertisement
path exists.

## G17: Pending Local Announcement Gate

One bounded live run must establish all of the following:

- exactly one canonical Helianthus announcement is visible on the selected
  interface and bound address;
- an independent LAN observer resolves the exact instance and closed TXT set;
- the registration window changes only `register` from `false` to `true` and
  back to `false`;
- withdrawal is observed with exact `TTL=0`; and
- the post-withdrawal negative confirms no inbound connection attributable to
  the withdrawn announcement.

The announcement alone creates no remote session or pairing candidate.

### Protected Registration Signal

`register=true` means that bounded pairing registration is
available. It does not mean that the peer is trusted and does not enable
automatic handshake acceptance. Opening the local pairing window changes only
this local value. It does not queue, report, or dial a remote and cannot create
a remote service, session, topology row, or candidate.

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

Inbound operation remains supported. In particular, local `register=true`
continues to advertise a bounded inbound registration window; it neither
auto-trusts a peer nor disables the separately constrained outbound candidate
path below.

## Observation Provenance

Authorization policy and observed network state have separate provenance. An
allowlisted SKI may permit later transport handling, but it cannot create a
visible service, session, pairing candidate, address observation, or topology
row. Passive discovery and allowlist evaluation alone never initiate a network
attempt.

An mDNS observation callback may create a visible remote service. Only an
actual connection callback may create a session. Only the pairing callback
from an active transport connection may create the single volatile pairing
candidate. A service observation cannot imply a session, and neither policy
configuration nor an open local registration window can stand in for a live
callback.

## Candidate-Bound Outbound Pairing

Passive `_ship._tcp` discovery may expose a visible candidate, but it does not
dial, trust, or persist that candidate. Each visible candidate has an opaque,
process-local `candidate_ref` bound to one exact mDNS observation and its
revision. A withdrawn, replaced, consumed, or restarted observation invalidates
that reference; neither its value nor an SKI alone identifies a dial target.

An operator may select that exact reference only after separately validating
the observation's expected SKI as exactly 40 lowercase hexadecimal characters.
The resulting attempt uses one deterministic concrete address from that same
observation. It accepts no caller-supplied or static endpoint and has no
hostname, path, or address fallback. The observation supplies the endpoint
material; the caller supplies only the expected identity check.

Before a WebSocket upgrade, the outbound TLS connection pins the presented
certificate identity to the exact selected expected identity. A mismatch fails before the
WebSocket handler or protocol traffic. A successful TLS check is still
connected-untrusted: SHIP remains at `SmeStateApproved` and SPINE does not
start until the matching trust association has committed durably.

The state meanings and persistence/reconnect rules are Helianthus architecture
concerns, and the read-only/public versus experimental/admin boundary is an API
concern. They are recorded separately so this protocol page does not turn them
into generic protocol claims.

## Evidence Boundary For The Candidate Contract

`EV-20260720-001` records only a protected local `register` transition with
automatic acceptance disabled. It did not observe an outbound target, endpoint,
TLS pin, completed SHIP session, durable trust, trusted reconnect, or a VR940f
server role. The outbound rules above are therefore candidate design
requirements backed by the companion source review, not an observed-lab claim
about VR940f/myVaillant.

## Repair Stability Gate

After a real host-key and certificate repair, the certificate SKI must change.
The decoded raw 32-byte `StoreInstance`, derived `nodeToken`, canonical SHIP ID,
and DNS-SD instance must remain exactly unchanged. The next advertisement must
contain the unchanged `id` and the changed `ski`. Failure of any equality or
inequality check fails the gate.

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
Live validation remains pending.

[ship-go-pr]: https://github.com/Project-Helianthus/helianthus-ship-go/pull/15
