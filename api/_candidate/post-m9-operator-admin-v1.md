---
canonical_source: "Project-Helianthus/helianthus-docs-eebus:api/_candidate/post-m9-operator-admin-v1.md"
owner_domain: "api"
license: "AGPL-3.0-only"
publication_status: "candidate"
claim_status: "evidence-backed"
source_class: "derived_inference"
evidence_ids: "EV-20260720-001,EV-20260809-001,EV-20260811-001,EV-20260814-001"
hypothesis_status: "draft"
falsifier: "A reviewed gateway implementation shows that the closed operations, state-revision and idempotency bindings, or sanitized response models cannot represent the architecture contract without exposing coordinator/store internals or adding a second public eeBUS namespace."
stable_navigation: "false"
search: "false"
sitemap: "false"
versioned_bundle: "false"
release_bundle: "false"
candidate_output: "true"
candidate_output_path: "api/_candidate/post-m9-operator-admin-v1.md"
---

# Candidate eeBUS Operator Admin API v1

## Contract Boundary

Contract identity: `helianthus.eebus.operator-admin.v1`.

This is the initial gateway-owned typed operator HTTP contract for Portal and
Home Assistant. It is not MCP, GraphQL, a public Internet API, an eeBUS
protocol claim, or a direct wrapper around the owner Unix socket. Stable MCP
remains the single read-only `eebus.v1.*` namespace; no v2 or legacy alias is
defined here.

The in-process adapter contract is additive and separate from the public
runtime interface. `NewOperatorRuntimeV1(Config) (Runtime, AdminV1, error)`
returns the candidate-free runtime and its separate typed operator capability
together only to the creating gateway composition root. Existing `New(Config)`
callers receive only `Runtime`, and there is no exported accessor that accepts
an existing `Runtime`. The runtime concrete value does not implement
`AdminV1` or an exported admin-provider interface, so a holder of an already
distributed runtime cannot recover the capability through a type assertion or
helper call. The capability is not serializable and is retained only by the
gateway composition. Construction failure maps to `admin_boundary_unavailable`
before request object resolution.

eeBUS-specific authentication is out of scope. This contract does not define a
login, session, cookie, CSRF token, owner credential, HA credential, or
reauthentication flow. Existing Portal and Home Assistant authentication
lifecycles are outside this contract and remain unchanged. Pairing mutations
must not be withheld pending a separate Portal authentication change. Neither
Portal nor HA receives filesystem, trust-store, private-key, or operator-socket
access.

## Build Identity And Readiness Dimensions

The gateway constructs one immutable build-info object at process startup. It
contains `release_version` and `build_id`; no eeBUS adapter, Portal asset, MCP
handler, or runtime-state writer owns an independent version constant. Portal
health reports `gateway_version=release_version` plus the same `build_id`, MCP
initialize reports `serverInfo.version=release_version`, and
`runtime_state.meta` records `addon_version=release_version` plus
`gateway_build=build_id`. A mismatch is a packaging/startup defect, not a value
that a consumer may reconcile or rewrite.

This requirement does not add a field to a frozen stable `eebus.v1.*` tool and
does not change its schema. It freezes the one BuildIdentity source/mapping
across Portal health, MCP initialize `serverInfo.version`, and
`runtime_state.meta`; the existing raw eeBUS MCP contract remains unchanged.

Process readiness, eeBUS driver readiness, and partner/session readiness are
three independent dimensions. An eeBUS `DEGRADED` state does not rewrite
process readiness while the shared gateway APIs and other admitted protocol
runtimes are healthy. A disconnected partner does not rewrite eeBUS driver
readiness while listener/discovery are healthy. Conversely, a connected
session does not make a failed driver or process ready. AdminV1 reports these
dimensions; consumers display them without collapsing them into one `ok`
boolean.

The closed readiness enums are:

```text
process_readiness: `READY | NOT_READY`
eebus_readiness: `DISABLED | STARTING | READY | DEGRADED`
eebus_degraded_reason:
  `CONFIGURATION_INVALID | LOCAL_IDENTITY_UNAVAILABLE | LISTENER_UNAVAILABLE |
   RUNTIME_FACTORY_UNAVAILABLE | ADMIN_BOUNDARY_UNAVAILABLE |
   UNKNOWN_STARTUP_FAILURE`
```

`DISABLED`, `STARTING`, and `READY` carry no degradation reason. `DEGRADED`
requires exactly one reason. The ordered startup mapping is:

| First failed eeBUS startup stage | `eebus_readiness` | Reason |
| --- | --- | --- |
| Configuration validation | `DEGRADED` | `CONFIGURATION_INVALID` |
| Local identity load/validation | `DEGRADED` | `LOCAL_IDENTITY_UNAVAILABLE` |
| Listener construction/bind | `DEGRADED` | `LISTENER_UNAVAILABLE` |
| Runtime factory construction | `DEGRADED` | `RUNTIME_FACTORY_UNAVAILABLE` |
| AdminV1 construction | `DEGRADED` | `ADMIN_BOUNDARY_UNAVAILABLE` |
| Unclassified or future startup failure | `DEGRADED` | `UNKNOWN_STARTUP_FAILURE` |

An unknown startup failure maps to `DEGRADED / UNKNOWN_STARTUP_FAILURE`; an
unknown eeBUS readiness token is treated the same way by consumers. A configured
lane is `STARTING` only while one bounded construction attempt is active and is
`READY` only when its runtime, listener, and required operator boundary are
usable. A deliberately disabled lane is `DISABLED`. eeBUS startup failure alone
never maps process readiness to `NOT_READY`; that process state is reserved for
failure of the shared gateway/API readiness gate.

## Common Request And Response Rules

Mutations require:

- `Content-Type: application/json`;
- a bounded `Idempotency-Key`;
- the last observed `state_revision`;
- a bounded request body with unknown fields rejected.

Every Portal and HA mutation supplies the expected state revision and
idempotency key defined below. Live pairing confirmation at action time is an
operational control, not an authentication mechanism.

Portal and HA use the same envelope with `state_revision` for reads and
mutations:

```json
{
  "contract": "helianthus.eebus.operator-admin.v1",
  "request_id": "opaque-audit-reference",
  "state_revision": 42,
  "data": {},
  "error": null
}
```

`request_id` is safe to display and correlate with a sanitized audit row. It
does not encode identity, endpoint, time, or store generation. A mutation
replayed with the same idempotency key and identical bindings returns the same
logical terminal result. Reuse with different bindings returns
`idempotency_conflict` and performs no effect.

Every typed in-process mutation request embeds the closed
`MutationPreconditionV1` object:

| Field | Type | Rule |
| --- | --- | --- |
| `idempotency_key` | string | 1..128 UTF-8 bytes; empty, malformed, or over-limit values are `invalid_request`. |
| `expected_state_revision` | unsigned integer | non-zero and exactly equal to the current operator revision after replay lookup. |

Within one operator serializer, replay lookup precedes revision comparison.
The same key with the identical operation, runtime instance, handle, expected
revision, and argument binding returns the same logical terminal result with
`replayed=true` and does not execute a second effect. The same key with a
changed operation, handle, revision, or argument binding returns
`idempotency_conflict` and does not execute a second effect. A stale revision
with an unseen key returns `state_conflict` without retaining a replay entry.

`ConnectRequestV1` has one optional sensitive `pin` field. It has an optional
`pin` field only on the existing selected-candidate `ConnectRequestV1`.
Omitting `pin` preserves the
existing PIN-free connect flow. The contract does not add an arm operation, PIN
store, or second connect operation. A supplied value is admitted only for the
current selection whose `pin_requirement` is `REQUIRED` or `OPTIONAL`; supplying it
for `NOT_APPLICABLE` is `invalid_request`.

The input is accepted only when it is exactly 8 through 16 ASCII hexadecimal
bytes. Validation does not trim, case-normalize, Unicode-normalize, decode, or
otherwise rewrite the bytes. The HTTP decoder gives the selected attempt
ephemeral mutable bytes; it must never create an immutable plaintext copy.
The gateway uses them once for that exact current attempt and best-effort clears
every buffer it owns on return, rejection, timeout, cancellation, disconnect,
generation replacement, and process exit. A PIN is never persisted, logged,
echoed, audited, metriced, traced, diagnosed, or exposed through MCP, GraphQL,
semantic registry, or Home Assistant entity.

The Connect idempotency binding additionally contains a process-local keyed
HMAC over the exact PIN bytes plus presence. The replay record retains only the
HMAC, never PIN bytes or a canonical plaintext body. The same exact request
replays without a second launch or write; the same ordinary binding with a
different PIN presence or value is `idempotency_conflict`. A process restart
invalidates every PIN-bearing replay entry. The sensitive field must not enter
the generic JSON/canonical-body replay cache: the gateway special-cases decoder
and replay admission before generic body retention. Connect responses carry
`Cache-Control: no-store`; no response, redirect, referrer, audit row, or
generic error contains the value or its HMAC.

Connect is asynchronous. After all local validation and idempotency checks,
the accepted `POST` returns `200 connection_started`; it has no peer timing on
POST and does not wait for or reveal peer timing. A replay returns that same
logical accepted result.

`200 connection_started` includes one opaque `action_id`; same idempotency
replay returns the same `action_id` and does not relaunch the attempt. GET
status returns exactly one bounded identity-free `active_action` while that
action is live, keyed only by that `action_id`. Its closed fields are
`action_id`, `kind`, `state`, `outcome`, `retryable`, and `expiry`; `kind` is
the operation class, `state` is pending or terminal, `outcome` is nullable
until terminal, and `retryable` is an admission result rather than a client
grant. It is volatile only: the bounded record expires no later than two
minutes after acceptance and clears on terminal observation, expiry, explicit
flow abandonment, or process restart.

`active_action` must not include SKI, selection, partner, candidate, endpoint,
or PIN. It is neither a partner/candidate row nor a durable trust, discovery,
or semantic fact. A status response without a current action omits
`active_action`; it never substitutes an old terminal result or another
operator's action. The ordinary current partner and candidate projections keep
their existing identity, revision, retention, durable-denial, and withdrawal
rules independently.

The selection keeps the identity-bound requirement/baseline
`REQUIRED | OPTIONAL | NOT_APPLICABLE`; it is evidence about that selected
observation, not a peer result. Each terminal result is instead an action-local
identity-free terminal outcome: `pin_required`, `pin_optional`, `pin_busy`,
`pin_rejected`, `pin_unavailable`, or `pin_protocol_error`. The six categories
mean, respectively: required input was omitted; optional/restricted admission
continued without input; the current PIN admission was busy; the peer rejected
the attempt; the local PIN facility was unavailable; or the protocol returned
only a safe error class. They contain no value, byte position, peer timing,
identity, endpoint, candidate handle, or transport detail, and must not appear
in a partner or candidate row. The gateway retains them only in the active
action result long enough to complete the requesting flow; they are neither a
new durable fact nor a candidate lifecycle state.

The in-process operation set is closed:

```text
Snapshot(context, AdminSnapshotRequestV1) -> AdminSnapshotV1
OpenPairingWindow(context, OpenPairingWindowRequestV1) -> AdminMutationResultV1
ClosePairingWindow(context, ClosePairingWindowRequestV1) -> AdminMutationResultV1
Select(context, SelectRequestV1) -> AdminSelectionResultV1
Connect(context, ConnectRequestV1) -> ConnectResultV1
Confirm(context, ConfirmRequestV1) -> AdminMutationResultV1
Cancel(context, CancelRequestV1) -> AdminMutationResultV1
RetryTrusted(context, RetryTrustedRequestV1) -> AdminMutationResultV1
Untrust(context, UntrustRequestV1) -> AdminMutationResultV1
```

`AdminMutationResultV1` contains only `state_revision`, a closed outcome, and
`replayed`; every mutation above other than Connect retains that exact result.
ConnectResultV1 is the closed object:

```text
state_revision
outcome
replayed
action_id
additionalProperties: false
```

It carries the canonical mutation-result fields plus the one opaque
`action_id`; no undocumented field injection is allowed. The action ID follows
the same-idempotency replay/no-relaunch and volatile expiry/clear rules defined
above. `AdminSelectionResultV1` adds one opaque selection handle. There is no
generic action handle and no caller-controlled transport coordinate.

## Closed Operations

The route spellings below are the candidate wire shape. They are relative to
the typed gateway operator origin.

| Method and path | Typed operation | Coordinator effect |
| --- | --- | --- |
| `GET /admin/eebus/v1/status` | status | None; returns build identity, independent readiness dimensions, local endpoint summary, pairing-window state, listener/discovery health, and sanitized degradation. |
| `GET /admin/eebus/v1/partners?view=<view>` | partner view | None; lists exactly one of `trusted`, `connected`, `discovered`, or `candidate`. |
| `GET /admin/eebus/v1/partners/{partner_id}/spine?<closed-query>` | raw SPINE page | None; returns one lazy raw snapshot page bound to runtime and snapshot identity. |
| `POST /admin/eebus/v1/pairing-window:open` | open window | Opens one bounded window; never selects or dials. |
| `POST /admin/eebus/v1/pairing-window:close` | close window | Closes the window and retires only window-owned volatile state. |
| `POST /admin/eebus/v1/observations/{observation_id}:select` | select observation | Binds the exact current discovery revision and expected complete certificate short identifier; no dial or trust. |
| `POST /admin/eebus/v1/selections/{selection_id}:connect` | connect selection | Resolves only the current selection capability and starts its one bounded attempt; accepts optional transient `pin` only for a selection bound to `REQUIRED` or `OPTIONAL`. |
| `POST /admin/eebus/v1/candidate:confirm` | confirm candidate | Confirms the complete TLS-bound certificate short identifier and current candidate bindings; may create transient trust, never early persistence. |
| `POST /admin/eebus/v1/candidate:cancel` | cancel candidate | Retires only the exact current volatile candidate and selection; never changes durable trust. |
| `POST /admin/eebus/v1/partners/{partner_id}:retry` | retry trusted partner | Requests retry only when the current coordinator row is explicitly admitted; Portal/HA deadlines do not grant authority. |
| `DELETE /admin/eebus/v1/partners/{partner_id}/trust` | untrust partner | Durable denial/tombstone first; then authoritative already-absent or bounded same-generation live withdrawal determines complete versus incomplete outcome. |

### Endpoint Operations Matrix

| Operation | Portal | Home Assistant |
| --- | --- | --- |
| Status; `trusted`, `connected`, `discovered` views | allow | allow |
| `candidate` view | allow | allow |
| Raw SPINE page | allow | allow |
| Open/close pairing window; select/connect/retry | allow | allow |
| Confirm candidate trust | allow after OOB comparison | allow after OOB comparison |
| Cancel current candidate | allow | allow |
| Revoke durable trust | allow | allow |

Home Assistant performs the same typed closed operations through the gateway
boundary. It does not define an eeBUS credential or reauthentication flow and
does not receive a trust-store handle or an operator socket. Portal and HA both
enter the complete expected certificate short identifier independently for the
typed selection and confirmation flow; neither input can provide an endpoint or
store binding.

`partner_id`, `observation_id`, and `selection_id` are opaque, bounded, and
non-authoritative. Every operation resolves them under the current state
revision. No response or request contains `candidate_ref`, store generation
bytes, filesystem path, or socket framing.

The successful select response returns one opaque `selection_id` plus the
resulting `state_revision`. In the gateway, that identifier creates a bounded
server-side record that maps only to the returned in-process selection handle
and is bound to the same gateway runtime instance, issuing revision, and
expiry. It is not the serialized in-process
handle token. Connect accepts no observation identifier, expected certificate
short identifier,
endpoint, or reconstructed candidate input; it resolves that exact record and
invokes `AdminV1.Connect` with only the stored selection handle and common
precondition. Missing, expired, wrong-runtime, or stale-revision selection
identifiers reject without a transport effect.

The host client keeps only `selection_id` and its issuing revision in the
volatile active flow after Select. It clears the independently entered SKI and
observation data immediately. The `Select` response does not clear that
volatile selection; Connect terminal success/failure, selection expiry,
pairing-window close, navigation away, visibility loss, or explicit flow abort
does. No selection field enters persistent client storage.

Candidate comparison identity begins only when the candidate view for its
generation is returned. It remains through the active multi-step comparison.
Unrelated status, partner, discovery, selection, and readiness responses never
clear or replace the active candidate. Only a candidate response for a newer
candidate generation may replace it. Confirm terminal success or failure,
Cancel terminal success or failure, candidate expiry, pairing-window close,
connection close, generation change, navigation away, visibility loss, or
explicit flow abort clears the active candidate. Logout performs that explicit
flow abort before client teardown. Neither Portal nor HA persists selection or
candidate fields.

## Status And Partner Models

The `GET /admin/eebus/v1/status` response composes the immutable gateway
build/readiness object with the closed protocol portion from `AdminSnapshotV1`:

```text
build:
  release_version
  build_id
readiness:
  process_readiness
  eebus_readiness
  eebus_degraded_reason?
admin:
  local_ski
  local_ship_id
  pairing_window_state
  pairing_window_deadline?
  register
  listener_health
  discovery_health
  trusted_count
  connected_count
  discovered_count
  candidate_count
  state_revision
  active_action?
```

The in-process `AdminSnapshotV1` owns the `admin` portion, including
`local_ski` and `local_ship_id`; it does not own gateway build or process
readiness. Those two fields display the local protocol endpoint to the host operator
surfaces; they are never private-key material or durable store handles.
Public/shareable output redacts them. If local identity prevents AdminV1
construction, shared gateway health keeps `build` and `readiness` available,
while the typed admin origin returns `admin_boundary_unavailable` and exposes
no partial `admin` object.

`AdminSnapshotV1` / `StatusDataV1` is a closed shape with
`additionalProperties: false`; `active_action?` is its only optional async
action field. ActiveActionV1 is the closed optional status type:

```text
action_id
kind
state
outcome?
retryable
expiry
additionalProperties: false
```

The optional object repeats only the action contract above. Its expiry is the
same bounded volatile TTL, and its terminal/expiry/abandonment/restart clear
rules are not writable or extensible through status data.

Candidate lifecycle is visible only through this typed operator boundary; it
never enters public MCP, GraphQL, `ebus.v1`, the semantic registry, or HA entity
attributes. Process readiness, eeBUS readiness, and partner/session readiness
remain separate; counts and connection rows cannot override either process or
driver readiness.

Each partner row is the closed object:

```text
partner_id
view
remote_ski: <redacted>
remote_ship_id: <redacted>
name?
identifier?
brand?
device_type?
model?
endpoint?
trust_state
connection_state: `connected | idle`
partner_readiness: `disconnected | session_connected | topology_ready`
pin_requirement: `REQUIRED | OPTIONAL | NOT_APPLICABLE`?
retry_state: `RETRY_READY | BACKOFF_ACTIVE | ADMIN_HOLD`?
retry_deadline?
retry_admitted
last_seen?
observation_revision?
candidate_state?
degraded_reason?
```

The `remote_ski` field is the complete normalized 40-character lowercase value
for the host operator surfaces. It is never shortened for comparison. The
`remote_ship_id` field,
endpoint, and last-seen are present only when the owning runtime fact exists;
one view cannot synthesize them from another. The public/shareable formatter
redacts all operational identity and endpoint fields.

`retry_admitted` is true only for a currently admitted `RETRY_READY` row after
the coordinator resolves the current durable binding, observation, revision,
and retry gate. `BACKOFF_ACTIVE` requires a future retry deadline and always
sets `retry_admitted=false`. `ADMIN_HOLD` is terminal quarantine, has no retry
deadline, and sets `retry_admitted=false`. Retry rejects unless
`retry_admitted=true`; Portal and HA cannot derive admission by comparing a
clock or relabeling a terminal row.

Candidate rows additionally return only the bindings needed for the current
OOB decision: the complete observed certificate short identifier, expiry,
connection-bound state, and
sanitized outcome. Candidate nonce and coordinator/store generations remain
server-side. Confirmation carries the exact complete certificate short
identifier, current `state_revision`, and idempotency key. It does not require
an observation identifier. The gateway atomically binds those inputs to the
single server-held current candidate, including its connection and store
generations.

Earlier selection requires the exact current `observation_id` and its revision;
the returned selection is retained only in the server-side mapping described
above. Outbound TLS or an eligible inbound callback may then
bind only that already selected identity and generation. An inbound callback
cannot select a candidate, and no observation is fabricated. Both TLS paths
otherwise use identical OOB, expiry, generation, and persistence rules.

For an IPv6 link-local observation, the server-side selection record contains
the exact discovery-owned interface scope together with the endpoint. Connect
never accepts a caller-supplied scope or endpoint. If the current observation
has no one valid scope, resolution returns `endpoint_scope_unavailable` before
dial and consumes no attempt admission.

The selection record binds only the observed identity-bound requirement/baseline
`pin_requirement`, never a PIN or outcome. A missing PIN for `REQUIRED`
returns the action-local `pin_required`; `OPTIONAL` without one is the
action-local `pin_optional` path. `pin_busy`, `pin_rejected`,
`pin_unavailable`, and `pin_protocol_error` are likewise action-local
identity-free terminal outcomes. No terminal PIN outcome may be stored in or
returned from a partner/candidate row: it must not appear in a partner or
candidate row. The current attempt may retain no PIN after it terminates. PIN
handling does not change candidate retention: it neither confirms, replaces,
persists, nor revokes a candidate; the canonical durable-denial-first order,
durable tombstone, and rule that an incomplete withdrawal remains revoked are
unchanged. This protocol PIN is not an eeBUS-specific login, session, cookie,
CSRF token, credential, or reauthentication mechanism.

At the in-process boundary, select consumes only an observation handle and the
complete expected certificate short identifier, and returns a selection handle without dialing or
trusting; connect consumes only that selection handle and the exact current
revision; retry accepts only a partner handle and never an endpoint. SHIP owns
fresh discovery, endpoint validation, gate admission, and the single outbound
attempt; untrust resolves association, manifest, control, and store bindings
internally before durable revocation; none of those bindings are accepted from
the caller or exposed in a result.

The recovery-only exception is the exact release-repair restart product:
`RETRY_READY` / `RETRYABLE_FAILURE` with one usable current-lineage durable
association, nonzero `repair_sequence`, repair-receipt ledger cardinality
matches `repair_sequence`, and one terminal durable release-retry receipt:
exactly one terminal `release_retry_quarantine` / `repaired_unpaired` receipt
with nonzero operation and binding identifiers. The listener and discovery may
start and AdminV1 remains available while automatic outbound transport remains
closed. This recovery-only availability does not launch an automatic outbound
attempt and does not erase or rewrite durable trust. The receipt is internal
control evidence and is never exposed through AdminV1.

Not every persisted `RETRY_READY` / `RETRYABLE_FAILURE` record is that
exception. An ordinary first-trust commit/reset may persist one usable
association with `repair_sequence=0` and no release-retry receipt, or may
coexist with unrelated repair receipts when their ledger cardinality is
consistent. Without an exact release-repair marker, ordinary paired
classification and its exact journaled reconnect gate remain valid. A
malformed or otherwise non-exact release-repair receipt, or an inconsistent
repair-receipt ledger, remains `DURABILITY_UNKNOWN`.

Before listener or discovery startup, reopen may resolve only an interrupted
`attempt_prepare` whose store observation is exactly
`exact_previous_selected_and_target_absent`. Protected-anchor
compare-and-clear must complete durably, preserve the unchanged selected store,
and then use normal recovery classification. It does not synthesize failure or
launch an automatic outbound attempt. The denied result set is: exact target
selected, ambiguous observation, descriptor mismatch, or compare-and-clear
failure.

Each denied result remains `DURABILITY_UNKNOWN` and cannot start transport
effects.

`AdminV1.RetryTrusted` arms exactly one retry for the complete trusted-partner
identity resolved from the current opaque partner handle and revision. It
accepts no caller-supplied endpoint and uses only the library-owned current
discovery observation. The automatic mDNS reconnect remains denied until that
typed operation succeeds in arming the attempt. A failed synchronous retry
releases the volatile admission; it cannot be reused by a later automatic or
operator request.

`BACKOFF_ACTIVE`, `ADMIN_HOLD`, `REVOKED`, `CORRUPT_STORE`,
`NO_LOCAL_IDENTITY`, structural quarantine, terminal security quarantine, or
an absent/non-current durable association cannot start transport effects or arm
retry. They retain their existing fail-closed error mapping.

At snapshot time the adapter maps only the coordinator result to the closed
`RETRY_READY | BACKOFF_ACTIVE | ADMIN_HOLD` retry state. It never infers
retry-ready from a disconnected row. `RetryTrusted` re-resolves admission under
the serializer and performs an effect only while `retry_admitted=true`;
`BACKOFF_ACTIVE` returns `backoff_active` with its non-secret deadline, while
`ADMIN_HOLD` and every terminal security/structural quarantine return
`terminal_quarantine` without a deadline or transport effect.

`AdminV1.Untrust` preserves the canonical M4C durable-denial-first invariant
inside one serializer. It closes local pairing and denies the association in
memory before publishing a durable generation that deactivates the association
and appends its effective tombstone. Only after that durable result may the live
facade withdraw a current session.

With no connected generation, an authoritative already-absent result completes
as `revoked` after durability. With a connected generation, one bounded
same-generation disconnect/unregister completion determines only whether live
withdrawal is complete. A missing, late, foreign-generation, or ambiguous ACK
returns `revocation_withdrawal_incomplete`; the association remains revoked and
tombstoned, is excluded from retry admission, and cannot revive after restart.
Only completed live withdrawal returns `revoked`. A durable-write error before
the tombstone is effective returns `persistence_failure` and starts no live
withdrawal.

Operator snapshots request exactly one closed view: `trusted`, `connected`,
`discovered`, or `candidate`. Each response contains one non-zero operator
revision, capture time, sanitized status, and only the selected typed row set.
Partner, observation, selection, and candidate handles are process-local,
opaque, non-serializable capabilities. They expire after at most two minutes,
are capped at 128 live handles per kind and 512 live handles in total, and are
invalidated on every admin revision change. Capacity exhaustion never evicts a
still-valid handle and returns `admin_boundary_unavailable` without partial
output.

Candidate rows and complete candidate certificate identity are returned only to
the host operator surfaces. Portal and HA can inspect them and invoke the same
typed confirm, cancel, retry, and untrust actions, but neither can forward a
trust-store handle, raw socket, or server-side capability token.

Every response containing candidate-derived data includes `Cache-Control:
private, no-store`, `Pragma: no-cache`, `Expires: 0`, and `Referrer-Policy:
no-referrer`. Portal service workers and offline caches must exclude the entire
`/admin/eebus/v1/` path. Portal and HA hold candidate fields only in
request-lifetime memory and the active view model. The active view retains the
current candidate across unrelated responses and applies only the closed
terminal, abort, and newer-candidate-generation rules above. Candidate fields
never enter local/session storage, IndexedDB, browser history, URL state,
telemetry, crash capture, or reusable application cache.

The server and client lifetimes are distinct and both bounded. Gateway and
intermediary request/response buffers clear candidate identity immediately
after response completion. A host client may keep it only in the currently
visible active OOB view long enough for the operator comparison. It applies the
same closed clearing and replacement rules above; an unrelated response cannot
shorten that lifetime.

## Lazy SPINE Page

Only a capability issued by the current `connected` view can open a SPINE
root. A `trusted` capability is a durable-association handle, not a live-session
handle. A root request with a trusted-but-offline capability returns
`disconnected` and must not read the raw snapshot provider. The client directs
the operator to the separate SHIP Retry action; the read-only SPINE request
never retries or connects implicitly.

After a connected capability resolves, a valid raw snapshot with no matching
current partner device inventory returns `spine_topology_unavailable`. This
distinguishes a live session whose canonical topology is not ready from both a
trusted-but-offline relationship and a genuine `admin_boundary_unavailable`
construction/provider/capacity failure. No case returns a partial tree.

The connected capability and every returned snapshot/cursor are bound to the
current connected generation. A disconnect or generation change invalidates
them before dereference. For one generation the raw provider publishes an exact
replacement, never a merge. A disconnect, current-device removal, or a complete
current-generation refresh with no devices produces no nodes. An incremental
entity or feature add/remove first triggers a complete refreshed live graph
from the active remote; exact replacement preserves every unrelated node still
present. The event delta is not itself a complete graph. A reduced reconnect
returns only the reduced device/entity/feature sets. The adapter never fills
missing raw nodes from a prior generation or from semantic last-known-good
state.

The route accepts exactly one of these closed query shapes:

```text
request=root
request=children&snapshot_id=<opaque>&parent_node_id=<opaque>
request=continue&snapshot_id=<opaque>&parent_node_id=<opaque>&cursor=<opaque>
```

`request=root` is the only initial request and rejects every additional query
parameter. `request=children` expands exactly one node in the named snapshot.
`request=continue` advances the same parent page. Missing, duplicate, unknown,
empty, or extra parameters return `invalid_request`; a cursor is never accepted
as a child identifier. Page size is a fixed bounded server setting, not a
caller-controlled parameter. An expired snapshot or cursor returns
`snapshot_expired`; the client discards that tree and starts again with
`request=root` rather than combining generations.

The SPINE route returns one immutable snapshot page:

```text
snapshot_id
snapshot_hash
parent_node_id: <opaque-or-null>
nodes[]
next_cursor?
```

`parent_node_id` is `null` only for `request=root`; otherwise it equals the
requested parent. `next_cursor` is omitted exactly when that parent's fixed
ordering is exhausted. Each node has exactly `node_id`, `parent_node_id`,
`kind`, `sort_key`, and `payload`. The closed `kind` set is `device`, `entity`,
`feature`, `use_case_claim`, and `opaque`. The wrapper is only a lazy tree index:
`payload` is the lossless JSON object from the canonical
`helianthus.eebus.runtime.raw-snapshot.v1` inventory, with original field names,
presence/omission, typed values, and opaque arrays preserved:

| Kind | Canonical payload field inventory |
| --- | --- |
| `device` | `ski`, `ship_id?`, `address`, `type`, `description?`, `metadata?`, `secondary_digest?`, `opaque?` |
| `entity` | `device_address`, `entity_address`, `type`, `description?`, `secondary_digest?`, `opaque?` |
| `feature` | `device_address`, `entity_address`, `feature_address`, `type`, `role`, `description?`, `secondary_digest?`, `opaque?` |
| `use_case_claim` | `context_address`, `name`, `actor`, `resolved_role?`, `scenarios?`, `version?`, `availability?`, `document_subrevision?`, `secondary_digest?`, `opaque?` |
| `opaque` | `path`, `source`, `value` |

Use-case claims preserve the scope carried by their canonical
`context_address`. Parent resolution is closed and deterministic: an exact
feature-address match makes the claim a child of that feature; otherwise an
exact entity-address match makes it a child of that entity. The second form is
an entity-scoped claim, not a missing feature. The wrapper does not synthesize
a feature, rewrite `context_address`, or copy an entity-scoped claim onto every
feature. If a claim belongs to the selected partner but matches neither one
exact feature address nor one exact entity address in the same immutable
snapshot, the snapshot fails closed as `admin_boundary_unavailable`. Claims
for another partner remain excluded by the existing partner filter.

The adapter may not replace, rename, synthesize, or discard any canonical
payload field. `metadata`, `opaque`, and their typed nested values cross the
boundary intact; the Portal renders unknown values as raw typed data rather
than inferring semantics. Unknown kind values or a payload that cannot be
represented by this lossless mapping fail the page closed.

`snapshot_id` and `next_cursor` are opaque and bound to the effective operator
view, mask tier, runtime instance, contract, partner, parent node, stable sort
position, and snapshot hash. They expire and cannot be replayed after any
binding changes. The gateway validates the parent against the same immutable
snapshot before dereference and must not assemble a page from live mutable maps
after issuing the snapshot ID.

## Errors

The closed category set is:

```text
admin_boundary_unavailable
invalid_request
state_conflict
snapshot_expired
idempotency_conflict
pairing_closed
observation_stale
endpoint_scope_unavailable
identity_mismatch
pin_required
pin_optional
pin_busy
pin_rejected
pin_unavailable
pin_protocol_error
association_incomplete
candidate_expired
candidate_busy
trust_denied
listener_unavailable
discovery_unavailable
attempt_timeout
disconnected
spine_topology_unavailable
revocation_withdrawal_incomplete
backoff_active
terminal_quarantine
persistence_failure
unknown_state
```

Errors do not reveal which certificate-identity byte differed, whether a
partner exists, store contents, private paths, or coordinator internals. Unknown
runtime outcomes map to `unknown_state` and reject mutation.

### Home Assistant Closed Action Errors

Home Assistant uses this closed sanitized action-error table; unknown input
maps to the last row and never falls through to success:

| AdminV1 category | HA-native result | Retained data |
| --- | --- | --- |
| `invalid_request`, `idempotency_conflict` | Abort the malformed/conflicting action. | Sanitized category and request ID for the active flow only. |
| `state_conflict`, `snapshot_expired`, `observation_stale`, `candidate_expired`, `candidate_busy` | Refresh status and require a new explicit action. | None after the active flow closes. |
| `pairing_closed` | Return to the pairing-window step. | Sanitized category only. |
| `endpoint_scope_unavailable`, `listener_unavailable`, `discovery_unavailable`, `admin_boundary_unavailable` | Create or refresh a generic availability repair. | Category and non-secret readiness state only. |
| `identity_mismatch`, `pin_required`, `pin_optional`, `pin_busy`, `pin_rejected`, `pin_unavailable`, `pin_protocol_error`, `trust_denied` | Show a form/error state without echoing identity or PIN; `pin_unavailable` and `pin_protocol_error` may instead offer generic repair. | Category only; no submitted value. |
| `attempt_timeout`, `disconnected`, `spine_topology_unavailable` | Refresh the SHIP/SPINE status view. | Category only. |
| `backoff_active` | Disable Retry until the server deadline, then refresh; the client clock grants no admission. | Category and non-secret retry deadline only. |
| `revocation_withdrawal_incomplete`, `terminal_quarantine`, `persistence_failure`, `association_incomplete`, `unknown_state` | Create or refresh a fail-closed repair; an incomplete withdrawal remains revoked and is never offered as Retry. | Category and request ID only. |

The table is presentation mapping, not a second state machine. HA invokes only
the typed gateway actions, does not persist SKI or candidate identity, and does
not store the action payload in a config entry, entity registry, device
registry, issue registry, diagnostics, or reusable application storage.

## Non-Disclosure And Anti-Leak Rules

This contract defines no eeBUS-specific authentication material. A URL, query
string, request body, response, audit row, log, metric, trace, diagnostic
bundle, or shareable screenshot must never contain or echo a private key,
private PEM, token, trust-store bytes, candidate nonce, store internals, or raw
socket frame. Those values are never copied into application state, idempotency
records, errors, or coordinator commands.
Complete certificate short identifiers, protocol service identifiers,
endpoints, native SPINE addresses, and raw/opaque fields are host-operator
operational data and are removed from public/shareable output.

The admin API never writes raw eeBUS data into `ebus.v1`, unrelated GraphQL,
the semantic registry, or Home Assistant entity attributes. Portal and HA do
not cache protocol truth; they refetch gateway state after restart or conflict.
