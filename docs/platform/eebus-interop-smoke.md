# eeBUS G17/G19 Interop Smoke Gate

Canonical source: this page.

Plan provenance:
`helianthus-execution-plans/multi-runtime-semantic-platform.draft`.

Implementation companion:
[Project-Helianthus/helianthus-eebusreg#17](https://github.com/Project-Helianthus/helianthus-eebusreg/pull/17).

Protocol-owned companion:
[Project-Helianthus/helianthus-docs-eebus#13 merged content](https://github.com/Project-Helianthus/helianthus-docs-eebus/blob/b9413bda992b99e4f719ad2e26e1937ff11a5b4a/protocols/ship-spine-overview.md).

Implementation hook:
`helianthus-eebusreg/internal/eebusinteropsmoke`.

## Scope

MSP-03D-R proves bounded raw eeBUS transport feasibility after the internal
`eebus-go v0.7.0` facade and Home Assistant network gates. It does not enable
an eeBUS gateway sidecar, freeze the raw runtime contract, write production
trust, expose MCP tools, create candidate semantic facts, publish protocol
semantics, or enrich B509/B524 leaves.

This gate covers `eebus-transport-gate-v0` cases:

| Case | Required proof |
| --- | --- |
| `EEBUS-G01` | A black-box fake peer completes SHIP/TLS/session setup without importing the Helianthus facade under test. |
| `EEBUS-G17` | One bounded live run proves the local Helianthus `_ship._tcp` announcement, independent LAN observation, myVaillant trust visibility, exact `TTL=0` withdrawal, and the post-withdrawal negative. |
| `EEBUS-G19` | The same bounded live run proves an inbound VR940-client connection to Helianthus through TCP, TLS, WebSocket, and SHIP, followed by the first actual inbound SPINE payload on the current connection generation. |

## Fake Peer Boundary

Fake peer success is supporting evidence only. A valid `EEBUS-G01` artifact
records:

- the exact `github.com/enbility/eebus-go v0.7.0` module evidence;
- disposable, in-memory proof credentials;
- no production trust-store writes;
- no gateway, GraphQL, Portal, Home Assistant, command-routing, raw-write, or
  semantic-registry surface;
- an import-boundary check proving that the peer side did not import the
  Helianthus facade under test; and
- a redacted PASS/FAIL table for `EEBUS-G01`.

Passing `EEBUS-G01` cannot replace either live gate, cannot close M3 by itself,
and cannot justify a gateway import.

## G17: Local Helianthus Announcement

`EEBUS-G17` is a local-announcement gate. One bounded live run records all of
the following:

- Helianthus publishes the configured local `_ship._tcp` announcement;
- an independent LAN observer discovers that Helianthus announcement;
- myVaillant displays the corresponding trust visibility;
- the observer sees withdrawal with exact `TTL=0`; and
- the post-withdrawal negative records no inbound connection attributable to
  the withdrawn announcement.

G17 neither depends on nor claims a LAN-visible SHIP service from VR940. This
contract never treats or describes VR940 as a SHIP server.

## G19: Inbound VR940 Client

`EEBUS-G19` begins only when VR940 acts as the client and Helianthus accepts the
inbound connection. The accepted live sequence records, in order:

1. inbound TCP acceptance by Helianthus;
2. TLS completion on that connection;
3. WebSocket completion on that connection;
4. SHIP completion on that connection; and
5. the first actual inbound SPINE payload from the same live run and current
   connection generation.

Cross-run, stale, or prior-generation evidence does not complete G19. The first
SPINE payload proves only that data reached the redacted evidence boundary; it
does not establish protocol meaning or a semantic fact.

## Evidence Authority

### Live Authority

Live authority comes from the bounded run's independent LAN observation,
myVaillant trust visibility, withdrawal observation, and inbound transport
record. Only live authority can satisfy G17 or G19.

### Deterministic Executable CI Replay Authority

Deterministic executable CI replay authority covers fail-closed validation,
negative-case handling, stage ordering, generation binding, and report
redaction. Replay evidence cannot replace absent live LAN, trust, withdrawal,
transport, or first-payload evidence and cannot convert a partial live run into
a pass.

### Terminal Partial Or Negative Attempts

A terminal partial/negative attempt is final only for its bounded run. It
records exactly what was and was not observed, remains distinct from CI replay,
and does not establish behavior for later runs, other environments, or the
device class.

## First Home Assistant Attempt

The first Home Assistant-hosted attempt is published only as a redacted,
terminal partial/negative result:

- an independent LAN observer discovered the local Helianthus announcement;
- no inbound TCP connection reached Helianthus;
- pairing was not confirmed; and
- protocol acceptance was not confirmed.

Its public report digest is
`sha256:fe3e3cde5287d1151d55654f42a77520cbe606801d4245b4ac1ef4b2794f05df`.
This attempt proves only announcement visibility and its bounded negatives. It
does not complete G17 or G19 and does not support a VR940 server-role claim,
protocol semantics, or a broader device conclusion.

## Public Artifact Requirements

Public MSP-03D-R artifacts record:

- repository, branch, commit, issue id, mode, required cases, and generation
  time;
- Go/toolchain and module evidence;
- disposable credential posture;
- live, CI replay, or terminal partial/negative authority for each result;
- per-case PASS/FAIL/BLOCKED rows; and
- redacted command-log, endpoint, service, interface, and digest references.

Public artifacts omit raw identities, peer material, certificate or credential
data, private addresses, packet captures, transcripts, protocol payloads, and
other non-public material. Redacted digest references provide continuity only
inside the same evidence run; they are not semantic facts and are not copied
into eBUS registries, eeBUS candidate facts, GraphQL, Portal, or Home Assistant.

## Promotion Boundary

MSP-03D-R remains M3 feasibility evidence. M3.5 may freeze raw identity and
evidence shapes only after `EEBUS-G01`, `EEBUS-G17`, and `EEBUS-G19` are
accepted under their respective authority. M4 trust work, M5 gateway sidecar
import, M6 MCP, and later B509/B524/B555 enrichment remain separate gates.
