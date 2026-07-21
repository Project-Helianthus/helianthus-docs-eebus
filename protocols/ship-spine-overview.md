---
canonical_source: "Project-Helianthus/helianthus-docs-eebus:protocols/ship-spine-overview.md"
owner_domain: "protocols"
license: "CC0-1.0"
publication_status: "publishable"
claim_status: "evidence-backed"
source_class: "observed_runtime"
evidence_ids: "EV-20260714-001,EV-20260720-001"
hypothesis_status: "publishable"
falsifier: "A later accepted public gate changes the canonical advertisement, callback provenance, or G17/G19 acceptance boundary."
---

# Canonical Discovery For SHIP And G17/G19 Interop Gates

## Scope

This page defines the single local discovery contract for SHIP and the accepted
evidence boundary for the MSP-03D-R live interop gates. It records
transport-stage acceptance only. It does not publish SPINE semantics or a
consumer surface.

## Canonical Local Advertisement

The runtime publishes exactly one `_ship._tcp` service after the exact listener
is bound. Its DNS-SD instance is:

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

The SHIP ID and certificate SKI are intentionally distinct TXT values. The
DNS-SD instance is a human-facing label and does not participate in either
identity. The advertised endpoint must equal the one bound listener endpoint.
`<window>` is `true` only while the bounded local registration window is open;
otherwise it is `false`.

## G17: Local Announcement

G17 proves all of the following in one bounded live run:

- Helianthus publishes the configured local service announcement;
- an independent LAN observer discovers that announcement;
- myVaillant shows the corresponding trust visibility;
- withdrawal is observed with exact `TTL=0`; and
- the post-withdrawal negative confirms no inbound connection attributable to
  the withdrawn announcement.

G17 does not fix the direction of a later protocol handshake. A local
Helianthus announcement may lead to an inbound connection, but the
announcement alone creates no remote session or pairing candidate.

### Protected Registration Signal

In the SHIP DNS-SD record, `register=true` means that bounded pairing
registration is available. It does not mean that the peer is trusted and does
not enable automatic handshake acceptance. Opening the local pairing window
changes only this local registration value. It does not queue, report, or dial
a remote endpoint and does not create remote service, session, or candidate
state.

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

## Observation Provenance

Authorization policy and observed network state have separate provenance. An
allowlisted SKI or configured endpoint may permit later transport handling, but
its presence creates no visible service, session, pairing candidate, endpoint
observation, or topology record.

An mDNS observation callback may create a visible remote service. Only an
actual connection callback may create a session. Only the pairing callback
from an active transport connection may create the single volatile pairing
candidate. A service observation cannot imply a session, and neither policy
configuration nor an open local registration window can stand in for any of
these callbacks.

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

## Implementation And Publication Status

This page defines the canonical documentation contract tracked by
[docs issue 48](https://github.com/Project-Helianthus/helianthus-docs-eebus/issues/48)
and
[runtime issue 54](https://github.com/Project-Helianthus/helianthus-eebusreg/issues/54).
A branch, configuration value, or deterministic replay does not establish a
live deployment result. Support requires the
[redacted live gate](../evidence/ship-identity-live-validation.md) and preserves
the raw-only evidence boundary above.
