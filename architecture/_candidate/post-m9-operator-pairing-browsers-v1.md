---
canonical_source: "Project-Helianthus/helianthus-docs-eebus:architecture/_candidate/post-m9-operator-pairing-browsers-v1.md"
owner_domain: "architecture"
license: "AGPL-3.0-only"
publication_status: "candidate"
claim_status: "evidence-backed"
source_class: "derived_inference"
evidence_ids: "EV-20260720-001,EV-20260809-001,EV-20260811-001"
hypothesis_status: "draft"
falsifier: "A reviewed implementation or bounded owner-authorized run shows that a consumer can safely mutate pairing without the gateway-owned authenticated boundary; that discovery alone can authorize trust or a dial; that exact complete certificate-identity approval, connection generation, and store generation are unnecessary; that raw SHIP/SPINE inspection requires a second topology model; or that the closed state and secret-exclusion rules cannot represent a reachable operator outcome."
stable_navigation: "false"
search: "false"
sitemap: "false"
versioned_bundle: "false"
release_bundle: "false"
---

# Candidate Post-M9 Pairing And SHIP/SPINE Browser Contract

## Status And Scope

This candidate defines the eeBUS-native operator boundary required after the
read-only M9 consumer rollout. It builds on the existing first-trust
coordinator, durable association store, SHIP runtime, raw `eebus.v1.*` MCP
contract, and promoted semantic consumers. It does not reopen or replace any
completed milestone and does not claim that the Portal or Home Assistant flow
is already deployed.

The target is myVaillant Connect/VR940. Device-specific observations remain
evidence, not generic protocol claims. The flow must also remain usable for a
different conforming peer without adding Vaillant logic to the gateway admin
boundary.

## Ownership And Isolation

| Component | Owns | Must not own |
| --- | --- | --- |
| eeBUS runtime and first-trust coordinator | Discovery observations, the bounded pairing-window and candidate lifecycle, transient trust, durable association commit, reconnect, quarantine, and native raw topology. | Browser sessions, Home Assistant UX, semantic projection, or cross-protocol identity. |
| Gateway authenticated admin boundary | Authentication, authorization, CSRF enforcement for browser principals, idempotency, audit outcomes, translation to coordinator commands, and sanitized operator views. | Trust-store parsing, private-key export, duplicate SHIP/SPINE state, or automatic trust policy. |
| Portal | Full owner workflow, SHIP partner browser, lazy SPINE tree, explicit OOB comparison, and deterministic status presentation. | Direct trust-store access, the eeBUS operator socket, transport ownership, or hidden automatic retry/trust. |
| Home Assistant integration | HA-native setup/options/repair UX, sanitized status, and an owner-action link to the Portal boundary. | Candidate identity, raw SPINE, any pairing mutation or trust decision, direct trust-store access, the eeBUS operator socket, transport state, or a second pairing FSM. |
| Stable public MCP | Existing read-only `eebus.v1.*` runtime, service, session, pairing-status, topology, and snapshot inspection. | Pairing mutations, candidate selection, trust writes, or legacy/v2 aliases. |
| Semantic consumers | Promoted protocol-neutral facts only. | Raw SHIP/SPINE records, trust state, certificate or protocol-service identity, endpoints, or candidate state. |

The Portal and Home Assistant are clients of one gateway-owned API. They never
open the protected store, import private coordinator packages, or connect to
the owner-only Unix socket. The gateway adapter calls the coordinator through
its typed command boundary and does not reinterpret store bytes.

## Namespace And Surface Boundary

The stable raw MCP namespace remains exactly `eebus.v1.*`. No `eebus.v2.*`,
legacy alias, duplicate public mutation tool, or parallel Portal-only topology
contract is introduced. Pairing mutations live only on the separately
authenticated admin boundary defined by the companion candidate operator API
contract.

The admin boundary is an owner control surface, not a public MCP graduation.
Its version identifies the initial authenticated HTTP contract and does not
create a second eeBUS runtime namespace. Stable public MCP stays read-only.
If the authenticated boundary cannot be established, all admin reads and
mutations fail closed as `admin_boundary_unavailable`; no unauthenticated admin
status survives. The existing candidate-free public MCP reads are the only
unchanged read-only fallback.

## Operator Pairing Sequence

The valid first-trust sequence preserves the later MSP-052 selected-candidate
inbound boundary:

1. An authenticated owner opens one bounded pairing window. Opening the window
   changes local `register=true`; it does not select a peer, dial, or trust.
2. Passive discovery adds a `discovered` observation. Discovery grants no
   authority and cannot initiate a connection by itself.
3. The owner selects the exact current observation and validates the expected
   complete 40-character lowercase certificate short identifier from an
   independent OOB source.
4. Exactly one TLS path may win for that selected observation and current
   generation: either the owner starts the bounded outbound attempt, or an
   inbound callback binds only when its TLS identity equals the already
   selected observation. An inbound peer that arrives before selection, has a
   different identity, loses the winner reservation, or uses a stale generation
   is rejected without creating or replacing a candidate.
5. The gateway displays the complete TLS-bound certificate short identifier and
   current bindings. The owner confirms that exact complete value against the
   single server-held selected candidate. Prefix, suffix, shortened,
   case-folded, separator-bearing, or whitespace-bearing matches fail closed.
6. The coordinator may create transient runtime trust for that exact live
   connection generation. It writes no durable association yet.
7. Only matching same-generation protocol completion and a non-empty
   `remote_ship_id` value may commit the association atomically. Persistence
   failure is terminal and cannot be presented as trusted.
8. Reconnect uses only the durable identity anchors plus fresh discovery. It
   never restores a volatile selection or endpoint from before restart.

Every mutating request is owner-authenticated, authorized for its exact action,
idempotent where the state permits, and auditable without logging identity or
secret material. A stale observation, state revision, candidate nonce,
connection generation, store generation, CSRF proof, or idempotency binding is
a deterministic non-mutating rejection.

No step auto-trusts a peer. An allowlist, visible service, remembered endpoint,
open window, or prior failed attempt cannot stand in for explicit complete
certificate-identity approval.

This contract does not amend MSP-052 inbound eligibility. Outbound and inbound
TLS evidence converge only after the same exact observation has already been
selected. The inbound callback cannot select a candidate, and no path
synthesizes an observation.

## SHIP Partner Browser

The operator view classifies each row from coordinator and runtime facts; it
does not infer trust from connectivity or connectivity from discovery.

| View | Source fact | Minimum operator fields | Authority |
| --- | --- | --- | --- |
| `trusted` | One usable current-lineage durable association. | Complete certificate short identifier, protocol service identifier when available, brand, device type, model, trust state, connection state, and last-seen time. | May reconnect after fresh discovery; does not imply currently connected. |
| `connected` | One current live session generation. | Complete certificate short identifier, protocol service identifier when available, peer metadata, endpoint, connection state, generation-safe last-seen time. | May expose raw SPINE for the current session; does not imply durable trust. |
| `discovered` | One current passive discovery observation. | Complete certificate short identifier when advertised, protocol service identifier, brand, device type, model, endpoint, observation revision, and last-seen time. | Read-only until an authenticated selection; never authorizes a dial. |
| `candidate` | One coordinator-owned volatile candidate for the current pairing window. | Complete TLS-bound certificate short identifier, lifecycle state, expiry, connection binding, and sanitized failure state. | Owner-sensitive only; never public, persisted, logged, metriced, traced, or included in shareable evidence. |

A peer may appear in more than one view because discovery, connection, and
durable trust are independent facts. The response supplies explicit states and
correlation keys so the UI can group rows without collapsing those facts. No
stable or public API exposes `candidate_ref`; selection uses a bounded opaque
observation identifier plus the state revision, and the gateway resolves it
inside the authenticated request.

## SPINE Browser

The SPINE browser is a lazy projection of one immutable raw runtime snapshot.
It reuses the canonical device/entity/feature/use-case topology and never
creates a Portal or Home Assistant model of protocol truth.

The tree is ordered deterministically:

```text
device
  entity
    feature
      role
      type
      description
      opaque unknown fields
  use-case claim
    actor
    support state
    scenarios
```

Every node carries its native address or identifier only in the authorized
operator tier, plus the snapshot identity and a stable sort key. Features keep
the full canonical raw-snapshot object, including device/entity/feature
addresses, type, role, description, secondary digest, metadata, and opaque
fields whenever the corresponding canonical type defines them. Use-case claims
likewise retain context address, name, actor, resolved role, scenarios, version,
availability, document subrevision, secondary digest, and opaque fields.
Unknown values are preserved as typed opaque data; the browser must not
silently drop them, rename them into semantics, or invent a normalized meaning.
The lazy wrapper adds only tree identity and ordering; it never substitutes a
reduced Portal DTO for the canonical raw object.

Meta-issue #92 requests a live acceptance target of one device, eleven entities,
twenty features, and use-case claims for VR940. This is a derived, falsifiable
target awaiting the final owner-authorized live run, not an evidence-backed
claim that every VR940 has that cardinality. `EV-20260809-001` supports the
redacted public topology shape only; because its public device family is
redacted, it does not bind those counts to VR940. The target must be corrected
or rejected if the final protected live evidence does not establish both the
device identity and the shape.

Raw facts and promoted semantic facts are visually and structurally separate.
The raw tree must not enter `ebus.v1`, unrelated GraphQL fields, or the semantic
registry. Portal may link between views but cannot copy raw identity or native
addresses into semantic payloads.

## Closed Operator Outcomes

| Code | Meaning | Required behavior |
| --- | --- | --- |
| `discovery_unavailable` | No usable discovery source is running. | Show degraded read state; do not synthesize partners or dial. |
| `listener_unavailable` | The scoped protocol listener is not bound. | Pairing mutation fails closed; existing durable trust is not erased. |
| `pairing_closed` | No bounded owner window is open. | Candidate admission and first-trust launch are denied. |
| `identity_mismatch` | The supplied complete certificate short identifier does not exactly match the TLS-bound candidate. | No transient trust, persistence, or candidate replacement. |
| `trust_denied` | Policy or a terminal trust state denies the peer. | No connection launch or trust write; report the sanitized reason class. |
| `attempt_timeout` | The bounded attempt expired. | Retire only that attempt and apply bounded retry policy. |
| `disconnected` | A current session ended. | Preserve durable trust when present; clear only connection-owned state. |
| `backoff_active` | Retry is quarantined until a known deadline. | Expose the deadline; do not bypass it through Portal or HA. |
| `terminal_quarantine` | Security or structural state requires repair/admin action. | Deny pairing and retry until the coordinator clears the condition. |
| `persistence_failure` | Durable association publication did not complete safely. | Never report trusted; enter the coordinator's repair/reopen path. |

Unknown future state values map to one fail-closed `unknown_state` outcome.
They do not fall through to connected, trusted, or retry-ready.

## Authentication, CSRF, And Audit Boundary

Browser mutation requires an owner-authenticated same-origin session and a
session-bound CSRF proof. The gateway rejects missing or invalid Origin,
Referer policy, CSRF token, content type, action scope, state revision, and
idempotency binding before the coordinator receives a command. Cookies are
`Secure`, `HttpOnly`, and `SameSite=Strict` where HTTPS termination supports
them. Deployments without a valid authenticated boundary deny every admin read
and mutation as `admin_boundary_unavailable`, return no operator data, and do
not invoke the coordinator. Only the separate candidate-free public MCP
read-only surface remains available under its existing authorization rules.

Home Assistant uses a non-cookie, least-privilege machine principal bound to
the integration/config entry and explicit actions. That credential alone may
read sanitized status, the `trusted` and `discovered` views, and only connected
rows already backed by an independently usable durable association;
it cannot read the `candidate` view or raw SPINE, confirm/revoke trust, or
complete first trust. A browser cannot substitute that credential, and
machine-authenticated requests do not accept ambient browser cookies.

An HA user action that needs pairing, confirmation, retry, or untrust opens an
owner-action link to the Portal boundary. HA sends no mutation and receives no
grant or candidate data. The owner-authenticated same-origin Portal session
performs the complete action directly, including OOB comparison. HA only polls
its candidate-free status projection after the owner returns. The link carries
no identity, action authority, token, candidate, partner, or endpoint value.

The audit record contains action, authenticated principal class, request ID,
idempotency outcome, prior and resulting state class, timestamp, and sanitized
reason. It never contains private keys, PEM material, tokens, trust-store bytes,
credentials, complete certificate or protocol-service identity, raw endpoint,
candidate nonce, raw SPINE
payload, or Home Assistant secret material.

## Secret And Evidence Exclusions

Responses, logs, metrics, traces, diagnostics, screenshots intended for sharing,
and public evidence must not expose private keys, private PEM, bearer/session
tokens, credentials, trust-store bytes, candidate nonce, or store internals.
Complete certificate and protocol-service identifiers, native addresses,
endpoint, and raw protocol metadata are
operational data visible only to the authenticated local owner; public or
shareable output redacts them.

Snapshot and lazy-tree dereference remains bound to runtime, contract, tool or
admin scope, mask tier, effective authorization scope, and snapshot identity.
Changing any binding invalidates the reference rather than widening access.

## Consumer And Restart Acceptance

Portal is the complete operator workbench. Home Assistant provides an ergonomic
native flow and status but delegates all decisions and state to the gateway.
Independent Home Assistant restart must not change runtime trust. Independent
add-on restart must restore only durable associations, rediscover the peer,
reconnect, and rebuild raw topology without restoring a volatile candidate.

The final live gate must show discovery, exact complete certificate-identity
comparison, approval,
durable trust, connection, untrust, reconnect, and persistence for VR940 while
the existing eBUS runtime remains operational. The raw SPINE tree must test the
derived one-device, eleven-entity, twenty-feature target and use-case claims
without leaking it into semantic or eBUS surfaces; only that run may establish
whether the target is valid for this VR940.

## In-Process Operator Capability

The gateway obtains the coordinator-owned operator capability only while it
creates the runtime through
`NewOperatorRuntimeV1(Config) (Runtime, AdminV1, error)`. This composition
constructor returns two separate values to the creator. Existing `New(Config)`
callers continue to receive only the candidate-free public `Runtime`, and
there is no exported accessor that accepts an existing runtime.

The concrete runtime does not implement `AdminV1` or any exported
admin-provider interface. A holder of a previously distributed `Runtime`
therefore cannot recover the capability through a helper call or type
assertion. The gateway composition retains the separate `AdminV1` value and
passes only `Runtime` to ordinary MCP, GraphQL, semantic, and Home Assistant
components.

This is capability plumbing, not authentication. Only the gateway composition
retains the returned value; the gateway-owned HTTP adapter still performs
authentication, authorization, CSRF validation, request bounding, and
principal-specific projection before invoking it. Portal and Home Assistant
never receive the capability and never open the trust store or same-UID admin
socket.

The ordinary `Runtime.Snapshot`, `Runtime.PairingState`, raw MCP, GraphQL, Home
Assistant, semantic registry, logging, metrics, diagnostics, and shareable
evidence cannot reach or serialize `AdminV1`. Their existing contracts and
revisions do not change solely because an owner-only candidate exists. The
operator capability owns a separate instance-scoped reducer and revision.

That reducer is the single linearization point for snapshots and mutations.
Its revision starts at 1 only after the backend and coordinator are ready,
never exposes zero, advances once for each distinct sanitized owner-visible
transition, and must fail closed before unsigned 64-bit wrap. It performs
expiry and idempotency replay lookup before revision comparison, resolves the
typed handle, reserves the transition, and only then releases its lock for a
transport or persistence effect.

The owner/admin revision still advances for candidate admission,
cancellation, expiry, transient trust, and every other distinct owner-visible
transition; stale owner mutations return `state_conflict`. The gateway derives
the HA read-only projection through a separate reducer whose revision advances
only when an HA-permitted serialized fact changes. It neither consumes nor
mirrors the owner revision, so a candidate-only transition cannot become an HA
side channel.

The capability uses four distinct opaque handle kinds: partner, observation,
selection, and candidate. Each handle is generated with cryptographically
secure randomness and is bound server-side to the runtime instance, kind,
target, issuing revision, and expiry. A handle lives for at most two minutes;
selection and candidate handles also expire at the earlier owning window or
candidate deadline. The reducer permits at most 128 live handles per kind and
512 live handles in total. It prunes expired values first and never evicts a
still-valid handle to make space.

All handles are invalidated on every admin revision change, runtime shutdown,
backend replacement, process restart, or an earlier target-specific close or
expiry. A snapshot may reuse the current-revision handle for the same target;
no handle survives into a later revision. Zero, malformed, expired,
wrong-kind, cross-instance, or stale-revision handles reject without an
effect. The generic JSON, text, formatting, logging, metrics, diagnostics, and
shareable evidence reveal neither handle tokens nor operator identity or
endpoint wrappers.

## Amendment To The M4B Local Admin Boundary

This post-M9 candidate narrowly amends the candidate-free clauses in
[`msp-04b-first-trust-admin-local.md`](./msp-04b-first-trust-admin-local.md).
M4B remains an immutable historical milestone artefact, so this later contract
records precedence without rewriting M4B's original scope statement.
The same-UID AF_UNIX transport remains the private coordinator command and
candidate-binding boundary. It is no longer the only operator presentation
surface: the gateway may translate its privileged read into the owner-only
Portal response defined here, after gateway authentication and CSRF checks.

The amendment does not expose `candidate_nonce`, connection generation, store
generation, or socket framing to Portal or HA. Those bindings stay server-side.
Home Assistant remains candidate-free, and the public Runtime, MCP, GraphQL,
semantic, logging, metrics, diagnostics, and shareable evidence boundaries
remain candidate-free. Where M4B says all Portal surfaces are candidate-free or
that no HTTP handler/Portal action exists, this section supersedes only those
statements for the authenticated `portal_owner` adapter. It also supersedes
M4B's no-capture/no-share rule only to the minimum extent needed for the gateway
service and admin adapter to hold the complete comparison identity in bounded
request-lifetime memory and transmit it once in the authenticated Portal
response. That end-to-end relay remains the continuation of M4B's sole private
candidate-read exception, not a second candidate source or public response.

The identity still MUST NOT be logged, metriced, traced, persisted, included in
diagnostics/tests/shareable capture, or sent to HA. Gateway and intermediary
request/response buffers clear it immediately after the response completes.
The Portal client may retain it only in the bounded active OOB view lifetime
defined by the API contract, then clears it on every specified terminal or UI
event. Every other M4B confidentiality, same-generation confirmation,
persistence, and restart rule continues unchanged.
