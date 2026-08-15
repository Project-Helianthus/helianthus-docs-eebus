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

The in-process operation set is closed:

```text
Snapshot(context, AdminSnapshotRequestV1) -> AdminSnapshotV1
OpenPairingWindow(context, OpenPairingWindowRequestV1) -> AdminMutationResultV1
ClosePairingWindow(context, ClosePairingWindowRequestV1) -> AdminMutationResultV1
Select(context, SelectRequestV1) -> AdminSelectionResultV1
Connect(context, ConnectRequestV1) -> AdminMutationResultV1
Confirm(context, ConfirmRequestV1) -> AdminMutationResultV1
Cancel(context, CancelRequestV1) -> AdminMutationResultV1
RetryTrusted(context, RetryTrustedRequestV1) -> AdminMutationResultV1
Untrust(context, UntrustRequestV1) -> AdminMutationResultV1
```

`AdminMutationResultV1` contains only `state_revision`, a closed outcome, and
`replayed`. `AdminSelectionResultV1` adds one opaque selection handle. There is
no generic action handle and no caller-controlled transport coordinate.

## Closed Operations

The route spellings below are the candidate wire shape. They are relative to
the typed gateway operator origin.

| Method and path | Typed operation | Coordinator effect |
| --- | --- | --- |
| `GET /admin/eebus/v1/status` | status | None; returns local identity summary, pairing-window state, listener/discovery health, and sanitized degradation. |
| `GET /admin/eebus/v1/partners?view=<view>` | partner view | None; lists exactly one of `trusted`, `connected`, `discovered`, or `candidate`. |
| `GET /admin/eebus/v1/partners/{partner_id}/spine?<closed-query>` | raw SPINE page | None; returns one lazy raw snapshot page bound to runtime and snapshot identity. |
| `POST /admin/eebus/v1/pairing-window:open` | open window | Opens one bounded window; never selects or dials. |
| `POST /admin/eebus/v1/pairing-window:close` | close window | Closes the window and retires only window-owned volatile state. |
| `POST /admin/eebus/v1/observations/{observation_id}:select` | select observation | Binds the exact current discovery revision and expected complete certificate short identifier; no dial or trust. |
| `POST /admin/eebus/v1/selections/{selection_id}:connect` | connect selection | Resolves only the current selection capability and starts its one bounded attempt. |
| `POST /admin/eebus/v1/candidate:confirm` | confirm candidate | Confirms the complete TLS-bound certificate short identifier and current candidate bindings; may create transient trust, never early persistence. |
| `POST /admin/eebus/v1/candidate:cancel` | cancel candidate | Retires only the exact current volatile candidate and selection; never changes durable trust. |
| `POST /admin/eebus/v1/partners/{partner_id}:retry` | retry trusted partner | Requests retry only when coordinator state is retry-ready and backoff has elapsed. |
| `DELETE /admin/eebus/v1/partners/{partner_id}/trust` | untrust partner | Revokes the exact durable association and current runtime trust through the coordinator. |

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

## Status And Partner Models

Status for both host operator surfaces contains local protocol-service identity
display fields, pairing-window state and deadline, `register` state, listener
and discovery health, trusted/connected/discovered/candidate view counts, a
closed degraded-state code, and `state_revision`. Candidate lifecycle is
visible only through this typed operator boundary; it never enters public MCP,
GraphQL, `ebus.v1`, the semantic registry, or HA entity attributes.

Each partner row is the closed object:

```text
partner_id
view
remote_ski: <redacted>
remote_ship_id: <redacted>
brand?
device_type?
model?
endpoint?
trust_state
connection_state
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

At the in-process boundary, select consumes only an observation handle and the
complete expected certificate short identifier, and returns a selection handle without dialing or
trusting; connect consumes only that selection handle and the exact current
revision; retry accepts only a partner handle and never an endpoint. SHIP owns
fresh discovery, endpoint validation, gate admission, and the single outbound
attempt; untrust resolves association, manifest, control, and store bindings
internally before durable revocation; none of those bindings are accepted from
the caller or exposed in a result.

For the exact restart product `RETRY_READY` / `RETRYABLE_FAILURE` with one
usable current-lineage durable association, the listener and discovery may
start and AdminV1 remains available while automatic outbound transport remains
closed. This recovery-only availability does not launch an automatic outbound
attempt and does not erase or rewrite durable trust.

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
request-lifetime memory and the active view model; each clears them on candidate
expiry or change, logout, navigation away, visibility loss, and replacement by
any later response. Candidate fields never enter local/session storage, IndexedDB,
browser history, URL state, telemetry, crash capture, or reusable application
cache.

The server and client lifetimes are distinct and both bounded. Gateway and
intermediary request/response buffers clear candidate identity immediately
after response completion. A host client may keep it only in the currently
visible active OOB view long enough for the operator comparison; it clears the
view on confirmation/cancel, candidate expiry or change, connection close,
navigation away, visibility loss, or replacement by a later response.

## Lazy SPINE Page

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
identity_mismatch
association_incomplete
candidate_expired
candidate_busy
trust_denied
listener_unavailable
discovery_unavailable
attempt_timeout
disconnected
backoff_active
terminal_quarantine
persistence_failure
unknown_state
```

Errors do not reveal which certificate-identity byte differed, whether a
partner exists, store contents, private paths, or coordinator internals. Unknown
runtime outcomes map to `unknown_state` and reject mutation.

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
