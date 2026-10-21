---
canonical_source: "Project-Helianthus/helianthus-docs-eebus:development/spine-browser-request-ownership.md"
owner_domain: "development"
license: "AGPL-3.0-only"
publication_status: "draft"
claim_status: "evidence-backed"
source_class: "derived_inference"
evidence_ids: "EV-20260711-001,EV-20260720-001,EV-20260809-001,EV-20260811-001,EV-20260814-001"
hypothesis_status: "draft"
falsifier: "A reviewed client implementation or current operator-admin contract permits a stale completion to replace the active peer, snapshot, or parent scope, or cannot implement the proposed reducer without extending the API."
---

# SPINE browser request ownership

This application lifecycle design supplies the asynchronous acceptance slice of
[docs-eebus issue 153](https://github.com/Project-Helianthus/helianthus-docs-eebus/issues/153),
via issue 159, and
[execution-plans issue 92](https://github.com/Project-Helianthus/helianthus-execution-plans/issues/92).
Both parents retain their remaining acceptance. This page is outside the
protocol/type CC0 trees and does not amend the native API or the separate
browser display-state guide.

All reducer behavior below is **proposed future client work**, not evidence of
an implemented Portal or Home Assistant browser. Nothing is stable before the
Helianthus 1.0 release. No additional namespace, API field, credential,
principal, authentication or permission check is introduced. Authentication and
authorization are 0.11 subjects; this slice adds no authorization gate before
0.9 and no such check in 0.7.

## Sources and claim status

Source labels used in the tables refer to these public owners:

- **A:** Operator-admin candidate API, `post-m9-operator-admin-v1.md`,
  especially Common Request And Response Rules, Closed Operations, Lazy SPINE
  Page, DriverManager Lifecycle Integration, and Errors.
- **N:** Native runtime exposure candidate, `msp-138-native-runtime-exposure-v1.md`,
  especially Native Preservation Boundary and Public Repository Boundary.
- **R:** [Raw feature types](https://github.com/Project-Helianthus/helianthus-eebusreg/blob/main/eebusraw/raw_feature_v1.go),
  specifically `RuntimeBindingV1` and `FeatureDataGetDataV1`. This is a secondary
  implementation reference, not authority for the operator-admin wire shape.

| Status | Bounded claim | Evidence and limit |
| --- | --- | --- |
| Proven from current source text | Connected-view capability required for browsing; disconnect invalidates capabilities; pages and cursors have immutable snapshot and parent bindings. | A, Lazy SPINE Page. This proves the documented candidate contract, not runtime compliance. |
| Proven from current source text | Native values and unknown fields remain native; public examples must be synthetic. | N. Evidence ids above retain source provenance, not proof that this reducer has executed. |
| Hypothesis / proposed | Local lifetime and per-scope request ownership can fence late completions without changing A. | Reducer and sequences below; requires implementation and independent acceptance. |
| Unknown | Actual client cancellation, event delivery ordering, cache retention, reconnect races and server/client conformance. | No executable client or runtime evidence is supplied here. |

These statuses are separate from device qualification, profile admission and
runtime admission. A returned use-case claim is native evidence, not a newly
qualified semantic fact. R exposes generation bindings in its own raw feature
types; it does not imply that the browser receives those fields. A remains the
public native contract first. No new SHIP/SPINE protocol fact is promoted here.

## Current API boundary

A alone defines these closed query shapes on
`GET /admin/eebus/v1/partners/{partner_id}/spine`:

| Operation | Query | Authoritative response rule |
| --- | --- | --- |
| Root | `request=root` | No additional query parameters; returned `parent_node_id` is null. |
| Child | `request=children&snapshot_id=<opaque>&parent_node_id=<opaque>` | Expand exactly one parent in that snapshot. |
| Root continuation | `request=continue&snapshot_id=<opaque>&cursor=<opaque>` | Returned parent is null; cursor belongs to root. |
| Child continuation | `request=continue&snapshot_id=<opaque>&parent_node_id=<opaque>&cursor=<opaque>` | Cursor and returned parent belong to that exact child scope. |

Every page carries `snapshot_id`, `snapshot_hash`, `parent_node_id`, `nodes[]`
and optional `next_cursor`. Missing `next_cursor` means that scope is exhausted.
A defines `snapshot_expired` for expired snapshots/cursors and wrong cursor
scope, and `invalid_request` for malformed closed queries. Clients neither
parse a cursor nor discover its valid scope by trial. Page size is server-owned.
The ordinary envelope and errors remain unchanged; its `request_id` is an audit
reference, not the local request identity described below. `state_revision` is
not a replacement snapshot identity or a client-visible connection generation.

Only a capability from the current connected view opens a root. A trusted but
offline capability returns `disconnected` without reading the raw snapshot
provider. A live session without matching inventory instead returns
`spine_topology_unavailable`; provider failure can return
`admin_boundary_unavailable`. None authorizes a partial fabricated tree or an
implicit connection. SHIP Retry remains a separate explicit operation (A).

## Proposed local state and completion predicate

The following names describe volatile UI bookkeeping only. They are not a wire
schema, server cursor format, server capability, or runtime generation counter.
The selected peer capability here is A's connected-view `partner_id`, not the
pairing flow's `selection_id`. Display names never key requests or retained data.

| Local item | Proposed meaning and lifetime | Source constraint |
| --- | --- | --- |
| View lifetime | A fresh local identity on entry, peer selection, navigation return, disconnect or observed handle invalidation; retired on leave. | A capability invalidation; local fencing is proposed. |
| Peer binding | Exact current connected-view capability plus the view lifetime; no binding by display label or trusted row. | A, Lazy SPINE Page. |
| Tree lifetime | Fresh local identity on each root attempt, even when the returned opaque snapshot happens to compare equal to an earlier one. | A exact replacement; local root fencing is proposed. |
| Accepted snapshot | Returned opaque `snapshot_id` and `snapshot_hash` of the accepted root; absent before acceptance. | A immutable page identity; never synthesized. |
| Scope | Root sentinel or exact `parent_node_id` obtained from a node in the accepted snapshot. | A parent validation and cursor scope. |
| Pending request | Fresh local identity, operation, view/peer/tree binding, scope, expected snapshot pair where known, and exact input cursor when continuing. | A query shapes; request ownership is proposed. |
| Branch state | Accepted pages, next cursor or exhaustion, loading and local error per scope; no shared sibling error slot. | A independent page scopes; presentation policy is proposed. |

Allocate a pending record before dispatch. Only one request owns a scope's
pending slot at a time; independent child scopes may run concurrently. A new
attempt in the same scope retires the previous slot before dispatch. Child and
continuation requests require an accepted root. A child parent must still exist
in that same accepted tree. Continuations use only the exact last accepted
`next_cursor` for that scope; do not speculate the next cursor or issue parallel
continuations for one chain. No cursor is persisted or reconstructed.

On completion, first compare the captured view lifetime, exact peer capability,
tree lifetime, scope and request identity to the current pending slot. A
continuation must also still own its captured input cursor. If any comparison
fails, discard the entire completion, including its error and loading update;
it cannot clear a newer request's spinner. A current error is processed using
A's category; local bookkeeping does not reclassify an API failure as success.

For a current success, require the expected response parent. For a child or
continuation also require the accepted snapshot ID and hash unchanged. A root
success establishes its returned snapshot pair atomically. Reject an inconsistent
success locally without rendering or inventing a server error code; retire the
whole tree and its pending work, expose a local contract-mismatch state and
require a fresh root action. No unvalidated
payload is partially applied. Do not infer expiry durations or server bindings
from opaque values.

Append a continuation exactly once only after those checks, in server page
order. Accept its next cursor or exhaustion as returned. Repeated completion of
a settled request is stale. A child success replaces that scope's initial page;
a new root atomically replaces the whole active tree, never merges snapshots.
Payloads, including typed unknown data, remain lossless (A, N). Do not fill gaps
from another snapshot, connection, sibling, or semantic last-known-good state.

## Proposed transition rules

| Event | Local transition and permitted next work | Constraint / status |
| --- | --- | --- |
| Select connected peer or enter browser | Retire old pending work, allocate view lifetime, bind exact connected capability; explicit root action starts a tree lifetime. | A connected-only access; proposed reducer. |
| Root refresh | Retire all old tree requests and cursors before dispatch; freeze any visible old pages as inactive last-known-good display, with no expansion or continuation. Accept only the newest root attempt. | A replacement; proposed presentation. |
| Refresh fails without invalidation | Keep the inactive old display separately labeled unavailable/stale and retain native data without making it actionable. Offer explicit new root action, no silent retry. | A errors and N preservation; proposed presentation. |
| Cancel request or collapse branch | Retire the slot before best-effort local transport abort. Collapse retires descendant work too. Retain already accepted same-snapshot pages as inactive if useful; reopening requires current bindings. | Proposed local cancellation; no server cancellation field or admin pairing Cancel call. |
| `snapshot_expired` on current work | Retire the whole tree, all pending children and cursors; discard its browseable pages. Refresh status, then require a new explicit root action with a current connected capability. | A recovery and error mapping; proposed sequencing. |
| Disconnect or handle invalidation observed | Retire view/tree work immediately, clear actionable topology and cursors. Do not perform an implicit network read for the disconnected peer. Status and explicit SHIP Retry remain separate. | A invalidation and disconnected provider rule. |
| Navigation away | Retire view/tree and all slots before aborting; clear volatile browser capability, pages and cursors. | Proposed browser retention policy, separate from A's pairing selection clearing. |
| Return | Allocate fresh local lifetime, obtain a current connected-view capability through the ordinary partner view, require a new explicit root action. No cached cursor replay. | A capability boundary; proposed return policy. |
| Current ordinary branch failure | Clear only that slot's loading state, retain accepted pages in that scope as incomplete with error, and allow unaffected siblings to finish. Retry requires explicit action and still-valid bindings. | A error categories; proposed independent presentation. |
| Unknown error / inconsistent success | Fail the affected work closed; display local unavailability, never success or an empty completed branch. | A closed error model; proposed local handling. |

A disconnect or `snapshot_expired` is tree-wide even when delivered to one
branch; it is not an ordinary branch-local failure. Navigation and cancellation
cannot promise remote cancellation: a late completion may still arrive and must
pass the same ownership predicate. No local epoch can detect an unobserved
connection change by itself. Until invalidation is observed, the server's
current capability resolution and API errors are authoritative. Equal display
names, revisions or node labels never prove continuity. No polling interval is
specified.

## Synthetic asynchronous acceptance sequences

Letters below are symbolic UI bookkeeping, not sample server tokens or device
identifiers. Each row is ordered left to right; expectations describe the
proposed reducer, not executed tests. Device families may share display labels.

| Case | Ordered events | Required result | Current constraint and proposed acceptance |
| --- | --- | --- | --- |
| Late response after peer change | Select connected peer A; dispatch root rA; select B in a new view lifetime; dispatch rB; receive rA; receive rB. | Discard rA without clearing B's loading state. Only rB may establish B's tree. A late error from rA is discarded too. | A peer capability binding; proposed view and request fences. |
| Disconnect/reconnect with reused display name | Peer A root accepted as S; child pending; disconnect observed; a connected row with the same display label later appears; old child completes; operator selects current capability and requests root. | Retire S at disconnect, discard old child; no automatic browse while offline. New view/tree lifetimes apply even if opaque strings compare equal. New root alone establishes current topology. | A generation invalidation and exact replacement; proposed local reconnect fencing. |
| Root refresh races child | S accepted; child c in flight; refresh r starts new tree lifetime; c returns; r returns T. | c is stale as soon as refresh starts. Keep S only as inactive display while pending; accept T as an exact replacement with no children copied from S. | A immutable snapshots; proposed tree fence. |
| Child cursor used at root | S child page supplies cursor C for parent P; faulty dispatch sends root continuation without P; server returns `snapshot_expired`. | Correct reducer prevents dispatch by scope check. If faulty dispatch occurs, preserve authoritative error, retire S and require fresh explicit root recovery; never guess P or remap C. | A expressly defines wrong-scope error; proposed pre-dispatch bookkeeping. |
| Out-of-order continuations | Scope P has cursor C; request a owns C; explicit replacement attempt b retires a and owns C; b succeeds with next cursor D; request d uses D; a completes after b or d. | Discard a entirely, including any error. Append b once, then d only under its own bindings; no duplicate pages, cursor rollback or exhausted-to-loading regression. Ordinarily serialize one continuation per scope. | A opaque scoped cursor and fixed ordering; proposed slot ownership. |
| One failed sibling | Under S, expand P and Q concurrently; P returns an ordinary `admin_boundary_unavailable` error; Q succeeds for S/Q. | Keep P's accepted partial pages and local error, leave P incomplete; accept Q and preserve other siblings. Do not convert P to empty success or fail the whole tree. Global invalidation errors follow the tree-wide rule instead. | A page/error model; proposed branch isolation. |
| Navigation away and return | S accepted; child pending; leave; return; old completion arrives; new connected capability and explicit root acquired. | Old completion cannot repopulate or alter new loading state. No S cursor replay; new root owns the returned tree. | A capability boundary; proposed view lifecycle. |
| Expiry during continuation | P has accepted pages in S; continuation returns `snapshot_expired`; sibling response for S arrives later. | Retire all S work and discard the expired tree, including sibling response. Status refresh and a new explicit root action recover; no append across snapshots. | A expiry recovery; proposed global fence. |

## Remaining evidence and parent acceptance

Manual source review supports compatibility with A's current candidate surface,
not semantic validation or runtime success. The proposal still needs client
implementation, deterministic asynchronous reducer acceptance for all cases,
server conformance evidence and independent review. R's `Results`, `Failures`
and `Complete` describe a different raw feature response; they neither add
fields to a browser page nor prove branch behavior here.

Partial accepted pages in a still-valid snapshot are last-known-good local
state, not a complete topology. Inactive display never grants admission. Expired
trees are discarded; missing current native nodes are never backfilled. Device
qualification, profile admission, hardware acceptance and live smoke remain
separate and unproven.

This page changes no eBUS MCP behavior, eeBUS MCP schema, GraphQL surface, driver
output binding or consumer rollout. MCP/GraphQL parity remains a companion
acceptance obligation, not demonstrated parity. No unmerged implementation or
another ticket is required as a source. The display-state guide, normative
corpus, full parent issues and release acceptance remain open.
