---
canonical_source: "Project-Helianthus/helianthus-docs-eebus:protocols/ship-spine-overview.md"
owner_domain: "protocols"
license: "CC0-1.0"
publication_status: "publishable"
claim_status: "evidence-backed"
source_class: "observed_runtime"
evidence_ids: "EV-20260714-001,EV-20260720-001"
hypothesis_status: "publishable"
falsifier: "A later accepted public gate contract changes the G17 or G19 acceptance boundary."
---

# G17/G19 SHIP/SPINE Interop Gates

## Scope

This page defines the accepted evidence boundary for the MSP-03D-R live interop
gates. It records transport-stage acceptance only. It does not publish SPINE
semantics or a consumer surface.

## G17: Local Announcement

G17 proves all of the following in one bounded live run:

- Helianthus publishes the configured local service announcement;
- an independent LAN observer discovers that announcement;
- myVaillant shows the corresponding trust visibility;
- withdrawal is observed with exact `TTL=0`; and
- the post-withdrawal negative confirms no inbound connection attributable to
  the withdrawn announcement.

G17 never establishes that VR940 advertises or exposes a server endpoint for
SHIP. Its
direction remains a local Helianthus announcement that may lead to an inbound
VR940 connection.

### Protected Registration Signal

In the SHIP DNS-SD record, `register=true` means that bounded pairing
registration is available. It does not mean that the peer is trusted and does
not enable automatic handshake acceptance. A manual first-trust implementation
therefore keeps handshake auto-accept disabled and composes the published
registration value from independent automatic and user-mediated availability.

The user-mediated value is true only for its authenticated, bounded lifecycle.
When that lifecycle closes, expires, or reaches a terminal effect, the service
must withdraw or replace the announcement with `register=false`. A selected
candidate may remain advertised during the same bounded window and commit-wait
interval; this preserves transport liveness but does not admit a competing
candidate or authorize persistent trust.

## G19: Inbound Direct Access

G19 starts with VR940 acting as the client and Helianthus accepting the inbound
connection. Acceptance requires one ordered TCP, TLS, and WebSocket sequence,
completion of SHIP, and then the first redacted SPINE evidence from that same
live run and connection generation. Evidence from another run or connection
generation does not complete G19.

The first SPINE evidence proves only that data reached the redacted evidence
boundary. It does not promote any protocol meaning.

## Evidence Authority

Live observer evidence and deterministic CI replay have separate authority.
Live evidence establishes what happened on the LAN and in the operator trust
flow. CI replay establishes deterministic handling of negative cases and
fail-closed validation. A replay result cannot substitute for a missing live
observation.

A negative or partial live run is terminal for that attempt. It narrows what
was observed without establishing that the same result applies to every
environment or later run.

## Run Binding And Redaction

A valid operator proof is bound to a fresh run challenge, a bounded acceptance
window, redacted endpoint and expected-peer references, and the transport
evidence from that run. The ordered transport proof and first redacted SPINE
evidence remain bound to one current connection generation. Stale, reused,
cross-run, or cross-generation proof is rejected.

Public evidence contains redacted references, digests, stage results, and
authority labels. It omits packet captures, raw transcripts, sensitive
material, private addresses, and raw peer identity.

## Candidate Implementation Status

The inspected code worktree proposes concrete fields for the run challenge,
time window, redacted references, transport digest, connection generation, and
first-SPINE digest. Those field choices are uncommitted candidate details. This
page supports the contract above, not a landed runtime or public API shape.
