---
canonical_source: "Project-Helianthus/helianthus-docs-eebus:architecture/_candidate/post-m9-operator-pairing-browsers-v1.md"
owner_domain: "architecture"
license: "AGPL-3.0-only"
publication_status: "candidate"
claim_status: "evidence-backed"
source_class: "derived_inference"
evidence_ids: "EV-20260720-001,EV-20260809-001,EV-20260811-001"
hypothesis_status: "draft"
falsifier: "A reviewed implementation or bounded operator-confirmed run shows that a consumer can safely mutate pairing without the gateway-owned typed boundary; that discovery alone can authorize trust or a dial; that exact complete certificate-identity approval, connection generation, and store generation are unnecessary; that raw SHIP/SPINE inspection requires a second topology model; or that the closed state and secret-exclusion rules cannot represent a reachable operator outcome."
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
| Gateway typed operator boundary | Idempotency, revision checks, bounded opaque capabilities, audit outcomes, translation to coordinator commands, and sanitized operator views. | Trust-store parsing, private-key export, duplicate SHIP/SPINE state, or automatic trust policy. |
| Portal | Full operator workflow, SHIP partner browser, lazy SPINE tree, explicit OOB comparison, and deterministic status presentation. | Direct trust-store access, the eeBUS operator socket, transport ownership, or hidden automatic retry/trust. |
| Home Assistant integration | HA-native setup/options/repair UX, the same typed operator workflow, SHIP partner browser, and lazy SPINE tree. | Direct trust-store access, the eeBUS operator socket, transport state, or a second pairing FSM. |
| Stable raw MCP | Existing read-only `eebus.v1.*` runtime, service, session, pairing-status, topology, and snapshot inspection for the host operator. | Pairing mutations, candidate selection, trust writes, or legacy/v2 aliases. |
| Semantic consumers | Promoted protocol-neutral facts only. | Raw SHIP/SPINE records, trust state, certificate or protocol-service identity, endpoints, or candidate state. |

The Portal and Home Assistant are clients of one gateway-owned API. They never
open the protected store, import private coordinator packages, or connect to
the owner-only Unix socket. The gateway adapter calls the coordinator through
its typed command boundary and does not reinterpret store bytes.

## Namespace And Surface Boundary

The stable raw MCP namespace remains exactly `eebus.v1.*`. No `eebus.v2.*`,
legacy alias, duplicate public mutation tool, or parallel Portal-only topology
contract is introduced. `eebus.v1.*` is a host operator inspection surface, not
an anonymous, semantic, or public Internet API. Pairing mutations live only on
the typed operator boundary defined by the companion candidate operator API
contract.

The operator boundary is not a public MCP graduation. Its version does not
create a second eeBUS runtime namespace. Stable raw MCP stays read-only.
Coordinator, revision, handle, and input failures fail closed; they never
substitute an MCP mutation.

eeBUS-specific authentication is out of scope. This contract does not define a
login, session, cookie, CSRF token, owner credential, HA credential, or
reauthentication flow. Existing Portal and Home Assistant authentication
lifecycles are outside this contract and remain unchanged. The gateway must not
withhold pairing mutations pending a separate Portal authentication change.

## Driver Startup Isolation And Bounded Recovery

The eeBUS driver is an optional protocol-adapter startup lane. Failure while
loading eeBUS configuration, local identity, listener, runtime factory, or
AdminV1 construction must not terminate or de-admit eBUS, Modbus, MCP,
GraphQL, Portal, or the gateway health API. The gateway process remains
available, the eeBUS lane reports `eebus_readiness=DEGRADED` with one sanitized
closed reason, and eeBUS-dependent actions fail closed. A disabled eeBUS lane
is distinct from a configured lane that failed startup.

The gateway owns one bounded restart schedule for a failed eeBUS lane. It has
finite attempts per window, a nonzero backoff, one outstanding restart timer,
and shutdown cancellation. It is never a tight retry loop and it never restarts
unrelated protocol runtimes or API listeners. Successful reconstruction
replaces the failed lane once and advances the operator revision; failure
retains the truthful degraded state without erasing durable associations.

If AdminV1 construction itself fails, the shared gateway health surface still
reports the eeBUS startup degradation and the typed admin origin returns
`admin_boundary_unavailable`. No handler obtains a partial capability. This is
product startup isolation, not a claim that the eeBUS protocol defines process
readiness or restart policy.

## Operator Pairing Sequence

The valid first-trust sequence preserves the later MSP-052 selected-candidate
inbound boundary:

1. An operator action opens one bounded pairing window. Opening the window
   changes local `register=true`; it does not select a peer, dial, or trust.
2. Passive discovery adds a `discovered` observation. Discovery grants no
   authority and cannot initiate a connection by itself.
3. The operator selects the exact current observation and validates the expected
   complete 40-character lowercase certificate short identifier from an
   independent OOB source.
4. Exactly one TLS path may win for that selected observation and current
   generation: either the operator starts the bounded outbound attempt, or an
   inbound callback binds only when its TLS identity equals the already
   selected observation. An inbound peer that arrives before selection, has a
   different identity, loses the winner reservation, or uses a stale generation
   is rejected without creating or replacing a candidate.
5. The gateway displays the complete TLS-bound certificate short identifier and
   current bindings. The operator confirms that exact complete value against the
   single server-held selected candidate. Prefix, suffix, shortened,
   case-folded, separator-bearing, or whitespace-bearing matches fail closed.
6. The coordinator may create transient runtime trust for that exact live
   connection generation. It writes no durable association yet.
7. Only matching same-generation protocol completion and a non-empty
   `remote_ship_id` value may commit the association atomically. Persistence
   failure is terminal and cannot be presented as trusted.
8. Reconnect outside the retry-control product uses only the durable identity
   anchors plus fresh discovery. Fresh discovery alone does not authorize
   reconnect in the `RETRY_READY` / `RETRYABLE_FAILURE` product; that product
   requires the typed retry admission below. Reconnect never restores a
   volatile selection or endpoint from before restart.

Every mutating request carries the current revision and an idempotency binding,
is evaluated against its closed coordinator state, and is auditable without
logging identity or secret material. A stale observation, state revision,
candidate nonce, connection generation, store generation, or idempotency
binding is a deterministic non-mutating rejection.

No step auto-trusts a peer. An allowlist, visible service, remembered endpoint,
open window, or prior failed attempt cannot stand in for explicit complete
certificate-identity approval.

This contract does not amend MSP-052 inbound eligibility. Outbound and inbound
TLS evidence converge only after the same exact observation has already been
selected. The inbound callback cannot select a candidate, and no path
synthesizes an observation.

## Scoped Link-Local Endpoints And Transient PIN

An IPv6 link-local endpoint requires the discovery-owned interface scope that
was observed with that endpoint. The runtime never accepts a caller-supplied
scope or endpoint, never guesses a default interface, and never dials the same
address on another interface. Missing, stale, or ambiguous scope rejects the
attempt as `endpoint_scope_unavailable` before a socket effect. Global IPv6 and
IPv4 observations keep their existing validation; link-local scope is not
copied into a durable trust anchor.

The identity-bound requirement/baseline remains exactly `REQUIRED`, `OPTIONAL`,
or `NOT_APPLICABLE` for the active selected observation. It is not a terminal
peer result. The six action-local identity-free terminal outcome categories are
`pin_required`, `pin_optional`, `pin_busy`, `pin_rejected`, `pin_unavailable`,
and `pin_protocol_error`: required input omitted; optional/restricted admission
without input; busy admission; peer rejection; local unavailability; and a
sanitized protocol failure. None identifies a peer, byte, endpoint, candidate,
or attempt timing, and a terminal outcome must not appear in a partner or
candidate row. The Pairing view never exposes a PIN value.

Portal renders an optional password field only in the active Pairing Connect
step. It sends exact 8--16 ASCII hexadecimal bytes without normalization and
clears it immediately after submit, before rendering either a response or an
error. The page never reconstructs it for replay, history, autofill,
telemetry, or local/session storage. The gateway accepts it only in the
existing selected-candidate Connect request, holds ephemeral mutable bytes in
request-lifetime memory for
one attempt, and returns `200 connection_started` without waiting for peer
timing. The field is not an arm operation, PIN store, second connection action,
or eeBUS-specific authentication.

The generic Home Assistant service remains PIN-free. Its guided native pairing
or repair flow may hold the password only in the volatile current action form,
clears it after submit, and never writes it into a config entry, service data,
diagnostics, entities, registries, or reusable application storage. HA renders
only the same sanitized state/category supplied by the gateway; it cannot
retry, reconstruct, or infer a PIN.

Portal and HA render the same six action-local categories: `pin_required`
returns to the input decision, `pin_optional` permits the existing no-PIN
Connect action, `pin_busy` asks for a fresh explicit action, `pin_rejected`
clears the active form, and `pin_unavailable` or `pin_protocol_error` offers
generic availability repair. This is a
presentation mapping only: neither client associates a terminal PIN outcome
with a SKI-bearing partner/candidate row or retains it after the active action.

After `200 connection_started`, each client polls `active_action` and
correlates only by `action_id`. Portal and HA render only its bounded kind, state,
identity-free outcome, retryability, and expiry; neither client joins it to a
SKI, selection, partner, candidate, endpoint, or PIN. The client clears the
action state on terminal observation, expiry, abandonment, or restart. A
missing or mismatched action ID is not a candidate lookup and cannot be
reconstructed from another view. This volatile action card is separate from
partner/candidate rows, durable trust, and semantic data.

Implementation follows this dependency order exactly: SHIP `.16` -> eebus-go
bridge -> eebusreg -> gateway/Portal -> Home Assistant. The SHIP lane owns
protocol admission and transient consumption; each later layer passes only the
bounded optional request field and sanitized state. No layer promotes it into
durable candidate/trust state, raw MCP, GraphQL, semantics, or generic HA
service surface.

The PIN value never enters a response, replay record, durable store, log,
metric, trace, diagnostic, URL, or browser storage.

## Operator Workspace Information Architecture

The eeBUS Portal area has exactly three nested workspaces: `Pairing`, `SHIP`,
and `SPINE`. They share one read-only health strip and one gateway-owned typed
AdminV1 client, but they do not share presentation authority or volatile UI
state.

- Pairing owns every first-trust mutation: pairing-window control, discovery,
  independent OOB SKI input, observation selection, connection, exact
  TLS-bound candidate confirmation, and cancellation.
- SHIP owns durable trust and live-session inspection. It presents trusted
  associations and connected sessions as overlapping facts and owns explicit
  retry and untrust actions.
- SPINE is read-only and issues only `GET` requests. It selects a current live
  SHIP session and lazily inspects one immutable raw topology snapshot.

Browse SPINE never retries, connects, selects, confirms, or otherwise starts
transport. A trusted-but-offline association appears in SHIP as
`Disconnected — Reconnect required`; it is not a selectable SPINE peer. The
operator may explicitly invoke Retry in SHIP, then refresh the connected view
before entering SPINE.

The scoped `disconnected` and `spine_topology_unavailable` outcomes do not
degrade the shared boundary. `admin_boundary_unavailable` is reserved for a
genuine AdminV1 construction, raw-provider, entropy, or bounded-capacity
failure.

Leaving Pairing clears selection, candidate, OOB input, and Pairing-scoped
pending state; leaving SHIP clears armed untrust state; leaving SPINE clears
partner, snapshot, cursors, and every rendered raw node. The local workspace
selection does not place SKI, endpoint, partner capability, snapshot
identifier, or cursor in URL or browser history. Visibility loss retains the
same fail-closed clearing rules.

## SHIP Partner Browser

The operator view classifies each row from coordinator and runtime facts; it
does not infer trust from connectivity or connectivity from discovery.

| View | Source fact | Minimum operator fields | Authority |
| --- | --- | --- | --- |
| `trusted` | One usable current-lineage durable association. | Complete certificate short identifier, protocol service identifier when available, brand, device type, model, trust state, connection state, and last-seen time. | Durable trust may reconnect after fresh discovery only when no retry-control admission is required; it does not imply currently connected. |
| `connected` | One current live session generation. | Complete certificate short identifier, protocol service identifier when available, peer metadata, endpoint, connection state, generation-safe last-seen time. | May expose raw SPINE for the current session; does not imply durable trust. |
| `discovered` | One current passive discovery observation. | Complete certificate short identifier when advertised, protocol service identifier, brand, device type, model, endpoint, observation revision, and last-seen time. | Read-only until typed selection; never authorizes a dial. |
| `candidate` | One coordinator-owned volatile candidate for the current pairing window. | Complete TLS-bound certificate short identifier, lifecycle state, expiry, connection binding, and sanitized failure state. | Operator-surface only; never public, persisted, logged, metriced, traced, or included in shareable evidence. |

A peer may appear in more than one view because discovery, connection, and
durable trust are independent facts. The response supplies explicit states and
correlation keys so the UI can group rows without collapsing those facts. No
stable or public API exposes `candidate_ref`; selection uses a bounded opaque
observation identifier plus the state revision, and the gateway resolves it
inside the typed request.

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
target awaiting the final operator-confirmed live run, not an evidence-backed
claim that every VR940 has that cardinality. `EV-20260809-001` supports the
redacted public topology shape only; because its public device family is
redacted, it does not bind those counts to VR940. The target must be corrected
or rejected if the final protected live evidence does not establish both the
device identity and the shape.

Raw facts and promoted semantic facts are visually and structurally separate.
The raw tree must not enter `ebus.v1`, unrelated GraphQL fields, or the semantic
registry. Portal may link between views but cannot copy raw identity or native
addresses into semantic payloads.

## Connected-Generation Topology Replacement

Raw SPINE topology belongs only to the current connected generation. Each
accepted complete runtime topology refresh carries that generation and performs
exact replacement, never a merge, of the device, entity, feature, use-case, and
opaque sets for that generation. A stale-generation callback is discarded
without changing the current tree.

A disconnect, current-device removal, or a complete current-generation refresh
with no devices publishes an empty raw topology and invalidates every snapshot
and cursor from the earlier generation. An entity or feature add/remove triggers
a complete refreshed live graph from the active current-generation remote; its
exact replacement preserves every unrelated node still present. The event delta
itself is never treated as a complete empty graph.

A reduced reconnect publishes exactly the reduced device/entity/feature sets;
nodes from the prior connection cannot survive by union, cache fill, or
last-seen inference. While a current connection has no matching device
inventory, the browser reports `spine_topology_unavailable` rather than
displaying the previous generation.

Semantic last-known-good retention is a separate consumer fact. It may retain
already promoted semantic values with explicit age and provenance, but it must
never repopulate the raw SPINE tree, establish current connectivity, or keep a
removed raw node visible. Raw topology and semantic LKG therefore have separate
generation and freshness authorities.

## Retry-Ready Recovery-Only Startup

The recovery-only exception is the exact release-repair product:
`RETRY_READY` / `RETRYABLE_FAILURE` with one usable current-lineage durable
association, nonzero `repair_sequence`, repair-receipt ledger cardinality
matches `repair_sequence`, and one terminal durable release-retry receipt:
exactly one terminal `release_retry_quarantine` / `repaired_unpaired` receipt
with nonzero operation and binding identifiers. It is a retry-control
degradation, not a structural or terminal trust denial. On restart, the
listener and discovery may start so AdminV1 remains available and can obtain a
library-owned current discovery observation. Startup does not launch an
automatic outbound attempt, does not erase or rewrite durable trust, and does
not restore a caller endpoint or a volatile pre-restart selection.

Not every persisted `RETRY_READY` / `RETRYABLE_FAILURE` record is that
exception. An ordinary first-trust commit/reset may persist one usable
association with `repair_sequence=0` and no release-retry receipt, or may
coexist with unrelated repair receipts when their ledger cardinality is
consistent. Without an exact release-repair marker, ordinary paired
classification and its exact journaled reconnect gate remain valid.

The automatic mDNS reconnect remains denied in this product. Only
`AdminV1.RetryTrusted` arms exactly one retry for the complete trusted-partner
identity after the current revision and opaque partner handle resolve. The
attempt uses the library-owned current discovery observation and no
caller-supplied endpoint. The volatile admission is consumed by that one
attempt; a failed synchronous retry releases the volatile admission. A later
retry therefore requires another current typed operation and cannot inherit
authority from the earlier request.

This recovery-only exception is exact. `BACKOFF_ACTIVE`, `ADMIN_HOLD`,
`REVOKED`, `CORRUPT_STORE`, `NO_LOCAL_IDENTITY`, structural quarantine, and
terminal security quarantine cannot start transport effects or arm retry.
Missing, duplicated, stale, tombstoned, or otherwise unusable durable
association bindings also remain fail closed. A malformed or otherwise
non-exact release-repair receipt, including a duplicated or non-terminal one,
or an inconsistent repair-receipt ledger remains `DURABILITY_UNKNOWN` and
cannot start transport effects. A missing release-repair receipt alone means
only that the record is not this recovery-only exception; the ordinary
classification above still applies. Listener/discovery availability in the
exact retry-ready product does not widen candidate, trust, store, socket,
raw-data, or semantic authority.

## Untrust Durable Denial And Withdrawal

Untrust remains subordinate to the
[canonical M4C durable-denial-first invariant](msp-04c-restore-revocation-quarantine-repair.md).
Inside the coordinator serializer it first closes local pairing and denies the
association in memory before publishing the durable tombstone. The durable
generation deactivates the association; durable denial and tombstone precede
live withdrawal.

With no current connected generation, an authoritative already-absent result
completes as `revoked` after durability. With a connected generation, the live
facade then performs one bounded disconnect/unregister request. Its
same-generation disconnect ACK classifies withdrawal completeness, never trust
state. A missing, late, foreign-generation, or ambiguous result returns
`revocation_withdrawal_incomplete`; the association remains revoked and
tombstoned and cannot reconnect or revive after restart. Only durable denial
plus completed withdrawal returns the terminal success `revoked`.

A persistence error before the tombstone becomes durable returns
`persistence_failure` and cannot be rendered as successful revocation. Replay
uses the original idempotency binding and never performs a second durable or
live effect after a terminal result.

## Closed Operator Outcomes

| Code | Meaning | Required behavior |
| --- | --- | --- |
| `discovery_unavailable` | No usable discovery source is running. | Show degraded read state; do not synthesize partners or dial. |
| `listener_unavailable` | The scoped protocol listener is not bound. | Pairing mutation fails closed; existing durable trust is not erased. |
| `pairing_closed` | No bounded operator window is open. | Candidate admission and first-trust launch are denied. |
| `endpoint_scope_unavailable` | A link-local observation has no one current discovery-owned interface scope. | Reject before dial; never accept or guess a caller scope. |
| `pin_required` | The current closed coordinator state requires a transient PIN and no value was supplied. | Reject before protocol progress; never persist or echo the value. |
| `pin_optional` | The selected current observation permits the optional/restricted no-PIN path. | Continue only through the existing selected Connect action; retain no PIN or identity-bearing terminal result. |
| `pin_busy` | The current PIN admission is busy. | Do not launch or wait for a peer; clear the active form and require a fresh explicit Connect action. |
| `pin_rejected` | The peer rejected the transient PIN without a more specific safe category. | Retire only the current attempt; never echo, persist, or identify which value element differed. |
| `pin_unavailable` | The local PIN facility is unavailable before protocol progress. | Do not launch; retain no secret and offer only generic availability repair. |
| `pin_protocol_error` | The protocol returned only a safe PIN-failure category. | Retire only the current attempt, expose no peer detail, and offer generic availability repair. |
| `identity_mismatch` | The supplied complete certificate short identifier does not exactly match the TLS-bound candidate. | No transient trust, persistence, or candidate replacement. |
| `trust_denied` | Policy or a terminal trust state denies the peer. | No connection launch or trust write; report the sanitized reason class. |
| `attempt_timeout` | The bounded attempt expired. | Retire only that attempt and apply bounded retry policy. |
| `disconnected` | A current session ended. | Preserve durable trust when present; clear only connection-owned state. |
| `spine_topology_unavailable` | The raw provider returned a valid snapshot, but it contains no matching current-partner device inventory. | Keep the session visible, expose a read-only refresh action, and do not retry or start transport. An unavailable or invalid raw-provider result is `admin_boundary_unavailable`. |
| `backoff_active` | Retry is quarantined until a known deadline. | Expose the deadline; do not bypass it through Portal or HA. |
| `terminal_quarantine` | Security or structural state requires repair/admin action. | Deny pairing and retry until the coordinator clears the condition. |
| `revocation_withdrawal_incomplete` | Durable revocation succeeded, but live disconnect/unregister did not complete authoritatively within its bound. | Keep the association revoked and tombstoned; report incomplete withdrawal and deny reconnect. |
| `persistence_failure` | Durable association publication did not complete safely. | Never report trusted; enter the coordinator's repair/reopen path. |

Unknown future state values map to one fail-closed `unknown_state` outcome.
They do not fall through to connected, trusted, or retry-ready.

## Typed Operator Boundary And Audit

Portal and Home Assistant invoke the same closed typed operations: open/close
the pairing window; list/select an observation; enter and compare the complete
SKI; connect; confirm/cancel; retry; and untrust. Both surfaces receive the
candidate view, pairing-window state, and sanitized operation outcomes through
the gateway. Neither receives a trust-store handle or an operator socket.

The gateway rejects malformed input, missing or stale revision, bad opaque
capability, expired capability, duplicate-conflicting idempotency binding, and
any coordinator state that does not permit the requested operation before the
coordinator effect. Live pairing confirmation at action time is an operational
control, not an authentication mechanism. It requires the explicit current
operator confirmation only for the live mutation; it is not a login substitute.

Home Assistant presents this boundary through an HA-native config/options/repair
flow and ephemeral action forms. After Select succeeds, it clears observation
and entered identity input, then keeps only `selection_id` and its issuing
revision in the volatile active flow. The `Select` response does not clear that
volatile selection: it remains only until Connect reaches a terminal result or
the selection expires, unless the operator abandons the flow earlier.

Once a TLS-bound candidate exists, candidate comparison data remains only until
confirm, cancel, candidate expiry, connection close, generation change, or
active-flow abandonment. PIN exists only for the current Connect request. HA
does not persist SKI or candidate identity in a config entry, entity registry,
device registry, issue registry, diagnostics, or reusable application storage.
Only a sanitized closed status/error code and a non-secret retry deadline may
be shown in an HA repair issue.

This flow creates no eeBUS-specific login, session, cookie, CSRF token,
credential, or reauthentication. Existing HA authentication and lifecycle stay
outside this contract, and action-time confirmation remains an operational
control only. HA never derives retry authority from a button press: the current
AdminV1 row must report admission, and the coordinator remains authoritative.

The audit record contains action, request ID, idempotency outcome, prior and
resulting state class, timestamp, and sanitized reason. It never contains
private keys, PEM material, tokens, trust-store bytes, complete certificate or
protocol-service identity, raw endpoint, candidate nonce, or raw SPINE payload.

## Secret And Evidence Exclusions

Responses, logs, metrics, traces, diagnostics, screenshots intended for sharing,
and public evidence must not expose private keys, private PEM, tokens,
trust-store bytes, candidate nonce, or store internals.
Complete certificate and protocol-service identifiers, native addresses,
endpoint, and raw protocol metadata are
operational data visible only to the host operator surfaces; public or
shareable output redacts them.

Snapshot and lazy-tree dereference remains bound to runtime, contract, tool
scope, mask tier, and snapshot identity.
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

Physically disconnected eBUS participants and an offline VR940F are
environment observations only. They may explain why a particular protected
acceptance run cannot proceed, but they must not be encoded as product behavior
or generic protocol evidence, and they do not falsify the nonfatal startup
contract without an in-scope product failure.

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
retains the returned value; the gateway-owned adapter performs request bounding,
revision and idempotency validation, then invokes it. Portal and Home Assistant
never receive the capability and never open the trust store or same-UID admin
socket.

The ordinary `Runtime.Snapshot`, `Runtime.PairingState`, raw MCP, GraphQL, Home
Assistant, semantic registry, logging, metrics, diagnostics, and shareable
evidence cannot reach or serialize `AdminV1`. Their existing contracts and
revisions do not change solely because an operator-only candidate exists. The
operator capability owns a separate instance-scoped reducer and revision.

That reducer is the single linearization point for snapshots and mutations.
Its revision starts at 1 only after the backend and coordinator are ready,
never exposes zero, advances once for each distinct sanitized operator-visible
transition, and must fail closed before unsigned 64-bit wrap. It performs
expiry and idempotency replay lookup before revision comparison, resolves the
typed handle, reserves the transition, and only then releases its lock for a
transport or persistence effect.

The operator revision still advances for candidate admission, cancellation,
expiry, transient trust, and every other distinct operator-visible transition;
stale mutations return `state_conflict`. Portal and HA consume the same typed
operator projection; neither projection is a public MCP, GraphQL, semantic, or
eBUS surface.

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
surface: the gateway may translate its privileged read into the typed Portal
and Home Assistant responses defined here.

The amendment does not expose `candidate_nonce`, connection generation, store
generation, or socket framing to Portal or HA. Those bindings stay server-side.
Home Assistant may invoke the same typed pairing operations, and the public
Runtime, MCP, GraphQL, semantic, logging, metrics, diagnostics, and shareable
evidence boundaries remain candidate-free. Where M4B says all Portal surfaces
are candidate-free or that no HTTP handler/Portal action exists, this section
supersedes only those statements for typed Portal and Home Assistant adapters.
It replaces the earlier relay restriction and supersedes M4B's
no-capture/no-share rule only to the minimum extent needed for the gateway
service and adapter to hold the complete comparison identity in bounded
request-lifetime memory. Both host operator surfaces may receive the
complete comparison identity via the typed boundary once for the active OOB
view. That relay remains the continuation of M4B's sole private candidate-read
exception, not a second candidate source or public response.

The identity still MUST NOT be logged, metriced, traced, persisted, included in
diagnostics/tests/shareable capture, or included in public MCP, GraphQL,
`ebus.v1`, the semantic registry, or shareable output. Gateway and intermediary
request/response buffers clear it immediately after the response completes.
Each host client may retain it only in the bounded active OOB view lifetime
defined by the API contract, then clears it on every specified terminal or UI
event. Every other M4B confidentiality, same-generation confirmation,
persistence, and restart rule continues unchanged.
