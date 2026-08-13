---
canonical_source: "Project-Helianthus/helianthus-docs-eebus:api/_candidate/post-m9-operator-admin-v1.md"
owner_domain: "api"
license: "AGPL-3.0-only"
publication_status: "candidate"
claim_status: "evidence-backed"
source_class: "derived_inference"
evidence_ids: "EV-20260720-001,EV-20260809-001,EV-20260811-001"
hypothesis_status: "draft"
falsifier: "A reviewed gateway implementation shows that the closed operations, authentication profiles, state-revision and idempotency bindings, or sanitized response models cannot represent the architecture contract without exposing coordinator/store internals or adding a second public eeBUS namespace."
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

This is the initial gateway-owned authenticated admin HTTP contract for Portal
and Home Assistant. It is not MCP, GraphQL, a public Internet API, an eeBUS
protocol claim, or a direct wrapper around the owner Unix socket. Stable MCP
remains the single read-only `eebus.v1.*` namespace; no v2 or legacy alias is
defined here.

If the gateway cannot establish an authenticated admin boundary, every mutation
below returns `admin_boundary_unavailable` without invoking the coordinator.
Read-only public MCP behavior remains unchanged.

## Authentication Profiles

| Profile | Authentication | CSRF rule | Allowed use |
| --- | --- | --- | --- |
| `portal_owner` | Owner-authenticated, same-origin gateway session. | Mandatory session-bound CSRF token plus strict Origin/Referer and JSON content-type validation. | Read operator views and invoke explicitly authorized pairing actions. |
| `ha_integration` | Non-cookie least-privilege machine credential bound to one HA config entry. | Browser CSRF does not apply; ambient cookies and browser-origin requests are rejected. | Read sanitized status and non-candidate partner views only. Every mutation, candidate view, and raw view is denied. |

Authentication and authorization run before request decoding can reveal whether
a partner, observation, trust record, or snapshot exists. Errors are category
only. Neither profile grants filesystem, trust-store, private-key, or operator-
socket access.

## Common Request And Response Rules

Mutations require:

- `Content-Type: application/json`;
- a bounded `Idempotency-Key`;
- the last observed `state_revision`;
- an action-specific authorization scope;
- the profile-specific authentication and CSRF checks; and
- a bounded request body with unknown fields rejected.

Successful and failed responses use one closed envelope:

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

## Closed Operations

The route spellings below are the candidate wire shape. They are relative to
the protected gateway admin origin.

| Method and path | Scope | Coordinator effect |
| --- | --- | --- |
| `GET /admin/eebus/v1/status` | `eebus.admin.read` | None; returns local identity summary, pairing-window state, listener/discovery health, and sanitized degradation. |
| `GET /admin/eebus/v1/partners?view=<view>` | `eebus.admin.read` | None; lists exactly one of `trusted`, `connected`, `discovered`, or `candidate`. |
| `GET /admin/eebus/v1/partners/{partner_id}/spine` | `eebus.admin.raw.read` | None; returns one lazy raw snapshot page bound to auth scope and snapshot identity. |
| `POST /admin/eebus/v1/pairing-window:open` | `eebus.admin.pairing` | Opens one bounded window; never selects or dials. |
| `POST /admin/eebus/v1/pairing-window:close` | `eebus.admin.pairing` | Closes the window and retires only window-owned volatile state. |
| `POST /admin/eebus/v1/observations/{observation_id}:select` | `eebus.admin.pairing` | Binds the exact current discovery revision and expected complete certificate short identifier; no dial or trust. |
| `POST /admin/eebus/v1/observations/{observation_id}:connect` | `eebus.admin.pairing` | Starts one bounded authorized attempt for the selected current observation. |
| `POST /admin/eebus/v1/candidate:confirm` | `eebus.admin.trust` | Confirms the complete TLS-bound certificate short identifier and current candidate bindings; may create transient trust, never early persistence. |
| `POST /admin/eebus/v1/partners/{partner_id}:retry` | `eebus.admin.pairing` | Requests retry only when coordinator state is retry-ready and backoff has elapsed. |
| `DELETE /admin/eebus/v1/partners/{partner_id}/trust` | `eebus.admin.trust` | Revokes the exact durable association and current runtime trust through the coordinator. |

### Endpoint Authorization Matrix

| Operation | `portal_owner` | `ha_integration` |
| --- | --- | --- |
| Status; `trusted`, `connected`, `discovered` views | allow | allow, sanitized |
| `candidate` view | allow | deny |
| Raw SPINE page | allow | deny; open Portal instead |
| Open/close pairing window; select/connect/retry | allow | deny |
| Confirm candidate trust | allow after OOB comparison | deny |
| Revoke durable trust | allow | deny |

There is no HA mutation grant, minting route, exchange route, mutation scope, or
credential escalation. HA setup/options/repair may display one fixed
same-origin Portal path such as `/portal/eebus`; it contains no query or
fragment data and conveys no authority. The authenticated owner performs every
mutation directly in Portal. After return, HA resumes polling only its
candidate-free read projection.

`partner_id` and `observation_id` are opaque, bounded, and non-authoritative.
Every operation resolves them under the current state revision. No response or
request contains `candidate_ref`, store generation bytes, filesystem path, or
socket framing.

## Status And Partner Models

Status contains only:

- local protocol-service identity display fields permitted for the authenticated owner;
- pairing-window state, deadline, and `register` state;
- listener and discovery health;
- aggregate counts for trusted, connected, discovered, and candidate views;
- one closed degraded-state code; and
- `state_revision`.

That complete status object is `portal_owner` only. The `ha_integration`
projection omits every candidate-derived field, including candidate count,
presence, lifecycle state, expiry, identity, failure, and any aggregate whose
value would change merely because a candidate exists. Its response is
therefore indistinguishable for zero versus one-or-more candidates when all
non-candidate runtime facts are equal. HA receives only listener/discovery
health, trusted/connected/discovered counts, sanitized degradation, and
`state_revision`. It receives no pairing-window state, deadline, `register`
state, or owner-intent derivative. Candidate admission, automatic window close,
commit failure, or any other candidate lifecycle event alone changes no
HA-visible field: the revision is not advanced or partitioned solely to signal
a candidate-visible change to that principal, and the complete HA JSON
projection is byte-identical across `OPEN_EMPTY`, `CANDIDATE_PENDING`,
`TRANSIENT_TRUSTED`, `COMMITTING`, and failed-closed states when all permitted
non-candidate facts are equal.

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
for the authenticated owner. It is never shortened for comparison. The
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
that selection is retained only as a hidden server binding. Outbound TLS or an
eligible inbound callback may then bind only that already selected identity and
generation. An inbound callback cannot select a candidate, and no observation
is fabricated. Both TLS paths otherwise use identical OOB, expiry, generation,
and persistence rules.

Candidate rows and complete candidate certificate identity are returned only
to `portal_owner`. The HA response shape omits them and cannot distinguish an
absent candidate from one that exists but is unauthorized. HA cannot confirm,
forward, or relay a candidate action.

Every response containing candidate-derived data includes `Cache-Control:
private, no-store`, `Pragma: no-cache`, `Expires: 0`, and `Referrer-Policy:
no-referrer`. Portal service workers and offline caches must exclude the entire
`/admin/eebus/v1/` path. Portal holds candidate fields only in request-lifetime
memory and the active view model; it clears them on candidate expiry or change,
logout, navigation away, visibility loss, and replacement by any later
response. Candidate fields never enter local/session storage, IndexedDB,
browser history, URL state, telemetry, crash capture, or reusable application
cache.

## Lazy SPINE Page

The SPINE route returns one immutable snapshot page:

```text
snapshot_id
snapshot_hash
parent_node_id
nodes[]
next_cursor?
```

Each node has `node_id`, `parent_node_id`, `kind`, `native_address`, `sort_key`,
and a kind-specific payload. The closed `kind` set is `device`, `entity`,
`feature`, `use_case_claim`, and `opaque`. Feature payload retains native role,
type, description, available function data, and opaque unknown fields. Use-case
claims retain actor, support state, and scenarios. Unknown kind values fail the
page closed rather than being reclassified as semantics.

`snapshot_id` and `next_cursor` are opaque and bound to the effective auth
scope, mask tier, runtime instance, contract, parent node, and snapshot hash.
They expire and cannot be replayed after any binding changes. The gateway must
not assemble the page from live mutable maps after issuing the snapshot ID.

## Errors

The closed category set is:

```text
admin_boundary_unavailable
unauthenticated
forbidden
csrf_rejected
invalid_request
state_conflict
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

Errors do not reveal which certificate-identity byte differed, whether an unauthorized partner
exists, store contents, private paths, or coordinator internals. Unknown
runtime outcomes map to `unknown_state` and deny mutation.

## Non-Disclosure And Anti-Leak Rules

Authentication material is accepted only in the designated secure session
cookie, CSRF header, or HA authorization header defined by the deployment
profile. A URL, query string, request body, response, audit row, log, metric,
trace, diagnostic bundle, or shareable screenshot must never contain or echo a
private key, private PEM, token, credential, trust-store bytes, candidate nonce,
store internals, or raw socket frame. Authentication headers/cookies are
consumed before application logging and are never copied into application
state, idempotency records, errors, or coordinator commands.
Complete certificate short identifiers, protocol service identifiers,
endpoints, native SPINE addresses, and raw/opaque fields are owner-only
operational data and are removed from public/shareable output.

The admin API never writes raw eeBUS data into `ebus.v1`, unrelated GraphQL,
the semantic registry, or Home Assistant entity attributes. Portal and HA do
not cache protocol truth; they refetch gateway state after restart or conflict.
