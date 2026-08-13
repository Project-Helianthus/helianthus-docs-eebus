---
canonical_source: "Project-Helianthus/helianthus-docs-eebus:architecture/_candidate/post-m9-operator-pairing-browsers-v1.md"
owner_domain: "architecture"
license: "AGPL-3.0-only"
publication_status: "candidate"
claim_status: "evidence-backed"
source_class: "derived_inference"
evidence_ids: "EV-20260720-001,EV-20260811-001"
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
| Home Assistant integration | HA-native setup/options/repair UX, sanitized status, and owner-initiated action forwarding against the gateway boundary. | Candidate identity, raw SPINE, an autonomous trust decision, direct trust-store access, the eeBUS operator socket, transport state, or a second pairing FSM. |
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

## Operator Pairing Sequence

The only valid first-trust sequence is:

1. An authenticated owner opens one bounded pairing window. Opening the window
   changes local `register=true`; it does not select a peer, dial, or trust.
2. Passive discovery may add a `discovered` observation. Discovery grants no
   authority and cannot initiate a connection by itself.
3. The owner selects the exact current observation and validates the expected
   complete 40-character lowercase certificate short identifier from an
   independent OOB source.
4. The owner explicitly initiates a bounded connection/binding attempt, or an
   eligible inbound attempt supplies the exact current TLS-bound candidate.
5. The gateway displays the complete observed certificate short identifier and
   the current bindings. The owner confirms that exact complete value against
   the single server-held current candidate; confirmation does not require or
   fabricate a discovery observation. Prefix,
   suffix, shortened, case-folded,
   separator-bearing, or whitespace-bearing matches fail closed.
6. The coordinator may create transient runtime trust for that exact live
   connection generation. It writes no durable association yet.
7. Only matching same-generation protocol completion and a non-empty
   `remote_ship_id` value
   may commit the association atomically. Persistence failure is terminal and
   cannot be presented as trusted.
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

Outbound selection remains bound to an exact current discovery observation.
Inbound first trust may reach the candidate callback before mDNS and therefore
has no `observation_id`; admission, presentation, and confirmation use only its
TLS-bound server-held candidate bindings. The two paths converge at the same
OOB confirmation and durable-commit state machine without synthesizing an
observation.

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
native role, type, description, function data, and raw/opaque unknown fields
when the runtime captured them. Unknown values are preserved as typed opaque
data; the browser must not silently drop them, rename them into semantics, or
invent a normalized meaning.

The initial VR940 live acceptance fixture contains one device, eleven entities,
twenty features, and its observed use-case claims. Those counts are an
acceptance shape, not a universal VR940 or SPINE cardinality rule.

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
them; deployments without a valid authenticated boundary expose read-only
status only and all mutation routes fail closed.

Home Assistant uses a non-cookie, least-privilege machine principal bound to
the integration/config entry and explicit actions. That credential alone may
read sanitized status and the `trusted`, `connected`, and `discovered` views;
it cannot read the `candidate` view or raw SPINE, confirm/revoke trust, or
complete first trust. A browser cannot substitute that credential, and
machine-authenticated requests do not accept ambient browser cookies.

An HA user action that needs `confirm` or `untrust` first redirects the owner to
the Portal boundary. The owner-authenticated same-origin session performs the
OOB comparison and issues one short-lived opaque approval grant bound to the
exact action, partner or candidate, state revision, connection generation,
idempotency key, config-entry principal, and expiry. HA can forward that grant
once without seeing candidate identity. A grant with any changed binding,
replay, or expiry fails closed before the coordinator receives a command. The
result surfaces the sanitized audit request identifier.

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
the existing eBUS runtime remains operational. The raw SPINE tree must retain
the observed one-device, eleven-entity, twenty-feature shape and use-case
claims without leaking it into semantic or eBUS surfaces.

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
statements for the authenticated `portal_owner` adapter. Every other M4B
confidentiality, same-generation confirmation, persistence, and restart rule
continues unchanged.
