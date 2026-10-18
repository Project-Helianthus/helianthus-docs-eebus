---
canonical_source: "Project-Helianthus/helianthus-docs-eebus:development/pairing-failure-recovery-guide.md"
owner_domain: "development"
license: "AGPL-3.0-only"
publication_status: "candidate"
claim_status: "evidence-backed"
source_class: "derived_inference"
evidence_ids: "EV-20260711-001,EV-20260720-001,EV-20260809-001,EV-20260811-001"
hypothesis_status: "draft"
falsifier: "A reviewed owning contract changes the separation of participation, trust, attempts, applied state or retry admission, or contradicts a recovery action described here."
stable_navigation: "false"
search: "false"
sitemap: "false"
versioned_bundle: "false"
release_bundle: "false"
---

# Pairing failure and recovery guide

This operator guide translates the existing candidate post-M9 contracts. It
adds no policy, API, normative revision or device qualification. It does not
establish that Portal or Home Assistant implements every described affordance.
Use only actions actually exposed by the installed version. Unimplemented or
unverified controls remain **pending**, rather than an instruction to call an
invented endpoint or edit protected state.

The owning references are the [pairing and browser contract](../architecture/_candidate/post-m9-operator-pairing-browsers-v1.md),
operator admin contract (`api/_candidate/post-m9-operator-admin-v1.md`),
[restore and quarantine contract](../architecture/_candidate/msp-04c-restore-revocation-quarantine-repair.md),
[outbound pairing contract](../architecture/_candidate/msp-052-outbound-pairing-contract.md)
and participation contract (`api/_candidate/portal-participation-contract-v1.md`).
The API paths above are source citations, excluded from stable navigation.
These are candidate product contracts, not new SHIP/SPINE specification claims.
Their evidence supports only each source's stated scope. Proven observations,
Hypothesis and Unknown must remain distinct from implementation qualification;
this guide promotes none of them. STD-01 specification access and normative
revision decisions stay with their operator/standards owners. Output-binding
design and mapping decisions stay with the INT-12 owner and semantic producer.
Pairing success supplies neither decision nor control permission.

## Read the five facts separately

| Fact | What to read | What it establishes |
| --- | --- | --- |
| Desired participation | Saved enabled/discovery preferences, saved revision and selected bindings. | What the operator requested; saving does not prove application, trust or connectivity. |
| Observed connection | Current SHIP session and `partner_readiness`: `disconnected`, `session_connected` or `topology_ready`. | Current runtime evidence; discovery alone is no session, and a session alone is no durable trust. |
| Trust association | The current durable association in the `trusted` view. | Trust when usable in the current lineage; an offline trusted partner is still offline. Transient trust is not durable commitment. |
| Pairing attempt | Current candidate/action and its sanitized outcome. | Progress or failure of one bounded action; neither a failed action nor its timeout resets an existing association. |
| Applied configuration | `applied_configuration` and `applied_revision`, separately from saved intent. | What the driver reports applied; null with revision zero means nothing applied. A result alone does not prove a binding operates. |

A saved-only binding cannot report a grant, native negotiation or `active`.
An older valid applied snapshot and still-held observations may remain after an
apply failure. Preserve those facts without presenting them as the latest
intent or restoring control eligibility after saved disable, removal or
revocation. The participation contract's interpretation of an older snapshot
remains explicitly provisional; it has no representation of a partially
applied revision. Do not merge fields into a fabricated applied revision.

## Inspect before choosing recovery

1. Read gateway process readiness, eeBUS readiness and the sanitized reason
   separately from partner readiness. `admin_boundary_unavailable` offers no
   partial admin capability. A failed eeBUS lane is not proof the whole gateway
   failed, and restarting unrelated runtimes is not a pairing remedy.
2. Refresh the relevant `discovered`, `candidate`, `trusted` or `connected`
   view. Discovery does not authorize a connection. Old UI handles and
   revisions are not reusable authority; refresh after stale-state rejection.
3. For first trust, use Pairing's bounded window, select the exact current
   observation, and independently compare the complete certificate short
   identifier against the TLS-bound candidate before confirming. An open
   window, familiar label or remembered endpoint is insufficient. Stop on
   `identity_mismatch`; do not shorten or normalize the comparison to pass it.
4. For an existing association, inspect SHIP's coordinator-provided retry
   state and `retry_admitted`. Do not infer retry permission from disconnection
   or elapsed time. SPINE browsing never initiates connection or retry.

## Failure and recovery decisions

| Displayed outcome or state | Meaning and supported next step |
| --- | --- |
| Failed attempt | Read the exact sanitized category, rather than inventing a generic `failed` trust state. `pin_rejected` and `pin_protocol_error` retire only the current attempt; `trust_denied` permits no launch or trust write. Refresh before a new explicit action and respect admission. |
| `attempt_timeout` | The bounded attempt expired. Only that attempt retires under bounded retry policy. Inspect fresh state; timeout is neither successful pairing nor authority to reset trust or loop Connect. |
| `disconnected` | The session ended. Durable trust, if present, is preserved. Clear connection-owned topology; use SHIP for retry inspection. |
| `RETRY_READY` | A coordinator retry state, not automatic authorization. Explicit Retry is available only with current `retry_admitted=true`; it resolves the current durable binding and fresh discovery and arms exactly one attempt. A failed synchronous retry releases admission; later requests cannot reuse it. |
| `BACKOFF_ACTIVE` / `backoff_active` | Retry is blocked until the supplied deadline. Wait, then refresh; neither Portal nor HA may bypass the gate or compute admission from its clock. |
| `ADMIN_HOLD` / `terminal_quarantine` | Structural or security quarantine requires the owning repair/admin path. Retry is denied, no retry deadline is offered, and restart or elapsed time cannot clear it. Do not repeatedly pair. |
| `persistence_failure` | Durable publication did not complete safely. Never label the new association trusted; retain the sanitized failure and let the coordinator's repair/reopen classification determine availability. |
| Known-but-unapplied attempt at reopen | This is the narrowly defined `attempt_prepare` reconciliation below, not a general retry-ready label. |
| Saved but unapplied participation | Refresh saved, applied and observed state after failed, interrupted or timed-out apply before any explicit retry. A retained applied snapshot is not proof the latest revision took effect. |
| `spine_topology_unavailable` | A valid raw snapshot has no matching current-partner inventory. Keep the session visible and use read-only refresh. Do not connect or retry from SPINE. |
| `unknown_state` | Reject mutation and obtain fresh inspection/owner diagnosis; never reinterpret it as trusted, connected or retry-ready. |

A trusted offline partner belongs in SHIP as
`Disconnected — Reconnect required`; it is not a selectable SPINE peer.
Disconnect invalidates old raw topology snapshots and cursors. Semantic
last-known-good retention is a separate consumer fact and cannot fill missing
raw nodes or authorize control.

## Known-but-unapplied and quarantine boundaries

At reopen, only an interrupted `attempt_prepare` with store observation exactly
`exact_previous_selected_and_target_absent` may be reconciled before listener
or discovery startup. The coordinator must durably complete protected-anchor
compare-and-clear, preserve the unchanged selected store, then perform normal
recovery classification. The operator does not perform that operation manually.
Exact target selected, ambiguous observation, descriptor mismatch or
compare-and-clear failure remains `DURABILITY_UNKNOWN` with no transport
effects. Reconciliation synthesizes neither failure nor an automatic attempt.

Recovery-only startup for `RETRY_READY` / `RETRYABLE_FAILURE` is the exact
release-repair product defined by the admin contract, including its usable
current-lineage association and internally consistent terminal repair evidence.
It can make listener, discovery and AdminV1 available while automatic outbound
transport stays closed. Not every persisted retry-ready record is that product:
ordinary paired classification and its exact journaled reconnect gate remain
valid without a release-repair marker. The UI must not inspect private receipts
or reconstruct this classification.

Wrong-host, copied, rolled-back, corrupt, identity-disagreeing or
durability-uncertain material remains fail-closed. Host-key/certificate repair
belongs to the existing private authenticated administration boundary; it is
not a Portal, HA, MCP or GraphQL repair recipe. Do not edit stores, remove
identity files, reset trust or unpair as generic recovery. Untrust is a separate
confirmed action, not a timeout remedy. If an independently requested untrust
reports `revocation_withdrawal_incomplete`, durable revocation remains effective
and reconnect is denied; incomplete withdrawal never means retry-ready.

## Synthetic walkthroughs and pending UI

These examples contain no real peer identity, endpoint, capture time or secret.
They illustrate contract decisions only, not observed hardware results.

- A synthetic heating-controller family has saved participation revision 12
  and applied revision 11. Apply reports `error`; fresh inspection still shows
  the older valid snapshot. Display all three facts. If revision 12 removed
  control permission, the old observation cannot restore that permission.
- A synthetic energy-controller family is trusted but `disconnected`.
  `BACKOFF_ACTIVE` keeps Retry unavailable. After refreshing, `RETRY_READY`
  with `retry_admitted=true` allows one explicit SHIP Retry. Browse SPINE only
  after a current connected view is available; connectivity alone need not
  imply topology readiness.
- A synthetic first-trust action ends with `attempt_timeout`. Refresh shows
  no durable association. Do not show trusted, reuse an expired selection, or
  reset local identity. Any subsequent attempt requires the current permitted
  Pairing flow and exact independent identity comparison.
- Reopen reports `DURABILITY_UNKNOWN`. Preserve the closed state and sanitized
  category for owner diagnosis. A restart is not repair authorization.

Pending where not implemented or verified: separate saved/applied/observed
panels, the volatile active-action card, retry admission/deadline display,
quarantine repair guidance, and connected-only lazy SPINE browsing. The
participation source documents a hook without an implementation; do not claim
its Portal apply controls work from this guide. Portal and HA remain clients of
one typed operator boundary, without a second pairing state machine. Raw
`eebus.v1.*` inspection stays read-only; no mutation namespace, GraphQL pairing
field or generic HA PIN service is added. Keep transient PIN input only in the
active supported form and clear it on submit; never include it in diagnostics.

For a support handoff, share only the sanitized category and permitted request
identifier where the owning contract allows it, plus identity-free readiness
and revision distinctions. Exclude candidate/partner handles, certificate
identifiers, endpoints, trust-store bytes, PINs and private captures.
