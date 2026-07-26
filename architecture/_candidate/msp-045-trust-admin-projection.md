---
canonical_source: "Project-Helianthus/helianthus-docs-eebus:architecture/_candidate/msp-045-trust-admin-projection.md"
owner_domain: "architecture"
license: "AGPL-3.0-only"
publication_status: "candidate"
claim_status: "evidence-backed"
source_class: "derived_inference"
evidence_ids: "EV-20260711-001"
hypothesis_status: "draft"
falsifier: "An accepted architecture review or conformance result demonstrates that the frozen projection can report paired without a usable current-lineage durable association; that `BACKOFF_ACTIVE` or `RETRY_READY` denies trust or clears paired while such an association remains usable and no fail-closed fact exists; that either retry state projects paired when no usable durable association exists; that structural uncertainty, `ADMIN_HOLD`, revocation, tombstone, or valid terminal security quarantine can project paired; that retry control overlaps terminal security quarantine instead of being classified as a disjoint product fact; that the projection leaks private trust or admin data, changes the public API or disk schema, or violates the closed precedence."
stable_navigation: "false"
search: "false"
sitemap: "false"
versioned_bundle: "false"
release_bundle: "false"
---

# Candidate MSP-045 Trust And Admin Projection Contract

## Status And Authority

This candidate freezes the MSP-045 read-only trust and admin projection tracked
by [issue 32](https://github.com/Project-Helianthus/helianthus-docs-eebus/issues/32).
Its publishable architecture evidence is `EV-20260711-001`. It defines an
internal behavioral contract and does not claim an implementation or a stable
publication transition.

[Issue 66](https://github.com/Project-Helianthus/helianthus-docs-eebus/issues/66)
corrects the candidate projection of transport retry control. `BACKOFF_ACTIVE`
and `RETRY_READY` are not durable-trust terminal states. This correction remains
internal candidate architecture and adds no public field, enum, or schema.
Issue 66 is the separate pre-implementation corrective review required by the
change boundary below. Contract v1 remains unpublished and unimplemented, so
this correction completes its initial candidate freeze rather than creating or
claiming a published v2.

The first-trust coordinator is the sole policy authority. Coordinator-owned
state is captured atomically before any mapping decision. No observer
reconstructs security policy from store contents, configuration, admin
availability, callback order, or public observations.

## Contract Identity And Ownership

| Boundary | Frozen value |
| --- | --- |
| `contract_id` | `helianthus.eebus.trust-admin-projection.v1` |
| `contract_kind` | `internal_behavioral` |
| `authority` | `first_trust_coordinator_only` |
| `capture` | `atomic_under_coordinator_ownership` |
| `public_mapping` | `existing_public_fields_only` |
| `public_api_bytes` | `95207` |
| `public_api_sha256` | `c93492bd275b5e14d3c9e05da701730d6d34a197e0653e6b169d103418bfcc8c` |
| `disk_schema` | `MSP-04C-R2_control_schema_v3_unchanged` |
| `persistence` | `derived_never_persisted` |
| `initial_freeze` | `issue_66_preimplementation_correction` |
| `semantic_change` | `after-initial-freeze:new_contract_version+separate_review` |

This contract is not a public Go API, not a disk schema, not an admin wire
schema, and not an MCP schema. It adds no field, enum value, mutation, or
storage record. The disk store remains control schema v3, and the public API
manifest remains byte-identical to the frozen hash above.

## Combined State Product

The atomic coordinator capture contains the trust lifecycle, protected
identity availability, durable association state, association lineage and
eligibility, terminal denial reason, outbound retry control, and transport
liveness. Retry control and durable trust are independent facts in that capture.
Before projection, the coordinator classifies a recognized persistent
quarantine reason as exactly one of `terminal_security_quarantine` or
`retry_control_quarantine`; those facts are mutually exclusive. The projection
reduces that disjoint product through the closed precedence below.

| Product class | Coordinator-owned facts | Allowed projection class |
| --- | --- | --- |
| `structural_indeterminate` | Exactly `CORRUPT_STORE`, `DURABILITY_UNKNOWN`, `HOST_BINDING_MISMATCH`, `CLONE_DETECTED`, `MANIFEST_GENERATION_ROLLBACK`, `CONTROL_EPOCH_ROLLBACK`, `REOPEN_IN_PROGRESS`, `RECONCILIATION_IN_PROGRESS`, `REPAIR_IN_PROGRESS`, `MALFORMED_STATE_PRODUCT`, or `UNKNOWN_ENUM`. | `unknown+paired_false+denied-trust` |
| `terminal_denial` | Revoked, current-lineage tombstoned, valid `ADMIN_HOLD`, or `terminal_security_quarantine` after no structural-indeterminate reason matched. | `denied+denied-trust` |
| `identity_unavailable` | Protected identity is unavailable after the structural and terminal-denial checks. | `unknown+certificate_unavailable` |
| `durably_trusted` | One usable durable association exists only after the store commit and exact protected-anchor finalization are both durable, with one valid, active, trusted, allowlisted, reconnectable, non-tombstoned association in the current lineage. `IDLE` and valid `retry_control_quarantine` expressed as `BACKOFF_ACTIVE` or `RETRY_READY` do not change that durable fact. | `paired_or_liveness_degraded` |
| `not_yet_trusted` | Unpaired or open durable state, candidate flow after the ephemeral candidate has been excluded from public enumeration, or valid `retry_control_quarantine` without a usable durable association. | `unpaired_existing_only+candidate_absent` |

There are no additional product classes. Missing or future enum values enter
`structural_indeterminate`; they do not fall through to a permissive state.
The structural facts above are an explicit closed structural-state set.
An unknown quarantine reason, a terminal reason combined with retry-control
classification, or any other overlapping or malformed product enters
`MALFORMED_STATE_PRODUCT`; it never falls through to a retry row.
`association_incomplete` is not a structural unknown; it is the normal volatile
candidate flow governed only by the candidate-absence and unpaired rule below.

## Closed Projection Precedence

First matching row wins. Conditions in a later row cannot override an earlier
row.

| Priority | Coordinator-owned condition | PairingObservationV1.State | ServiceV1.Paired | Trust degradation |
| --- | --- | --- | --- | --- |
| `1` | `CORRUPT_STORE\|DURABILITY_UNKNOWN\|HOST_BINDING_MISMATCH\|CLONE_DETECTED\|MANIFEST_GENERATION_ROLLBACK\|CONTROL_EPOCH_ROLLBACK\|REOPEN_IN_PROGRESS\|RECONCILIATION_IN_PROGRESS\|REPAIR_IN_PROGRESS\|MALFORMED_STATE_PRODUCT\|UNKNOWN_ENUM` | `unknown` | `false` | `denied-trust` |
| `2` | `REVOKED\|TOMBSTONED\|ADMIN_HOLD\|terminal_security_quarantine` | `denied` | `false` | `denied-trust` |
| `3` | `missing-protected-identity` | `unknown` | `false` | `certificate-unavailable` |
| `4` | `no-row-1-through-3-condition+usable-current-lineage-durable-association+(retry-control=IDLE\|BACKOFF_ACTIVE\|RETRY_READY)` | `paired` | `true` | `evaluate-liveness` |
| `5` | `no-row-1-through-3-condition+(UNPAIRED_LOCKED\|PAIRING_CLOSED\|OPEN_EMPTY\|association_incomplete\|CANDIDATE_PENDING\|COMMITTING-before-store-and-anchor-durable\|BACKOFF_ACTIVE-without-usable-durable-association\|RETRY_READY-without-usable-durable-association)` | `unpaired` | `false` | `evaluate-liveness` |
| `6` | `SHIP-callback` | `no-override-of-rows-1-through-5` | `no-override-of-rows-1-through-5` | `liveness-only` |

Every condition that produces `denied-trust` precedes
`missing-protected-identity`; therefore denial outranks
`certificate-unavailable` everywhere in this contract. Structural and terminal
denial is never `paired`. Rows 4 and 5 operate per durable remote record only
after candidate exclusion. In row 5, candidate conditions classify coordinator
status but create no candidate row; only separately existing durable records
can remain `unpaired`. A stale callback after revocation or restart cannot
resurrect `paired`.

`BACKOFF_ACTIVE` and `RETRY_READY` describe outbound attempt scheduling only.
MSP-04C may retain their recognized retryable reason under persistent
quarantine, but the coordinator classifies that state as
`retry_control_quarantine`, not `terminal_security_quarantine`. They never
revoke, tombstone, or structurally invalidate a usable durable association.
Subject to rows 1 through 3, either retry state with that association remains
`paired` with `ServiceV1.Paired=true` and no `denied-trust`; liveness may still
project `remote-disconnect`. Without a usable durable association, either retry
state enters row 5 and remains `unpaired`.

## Retry And Trust Cross-Product

The table is exhaustive for recognized retry-control values after candidate
exclusion. `none` means that no row 1 through 3 condition exists. Every row is
evaluated from one atomic capture.

| Fail-closed fact | Usable current-lineage durable association | Retry control | Projection | Trust degradation |
| --- | --- | --- | --- | --- |
| `structural_indeterminate` | `either` | `IDLE\|BACKOFF_ACTIVE\|RETRY_READY` | `unknown+paired_false` | `denied-trust` |
| `terminal_denial` | `either` | `IDLE\|BACKOFF_ACTIVE\|RETRY_READY` | `denied+paired_false` | `denied-trust` |
| `missing-protected-identity` | `either` | `IDLE\|BACKOFF_ACTIVE\|RETRY_READY` | `unknown+paired_false` | `certificate-unavailable` |
| `none` | `yes` | `IDLE` | `paired+paired_true` | `evaluate-liveness` |
| `none` | `yes` | `BACKOFF_ACTIVE` | `paired+paired_true` | `evaluate-liveness` |
| `none` | `yes` | `RETRY_READY` | `paired+paired_true` | `evaluate-liveness` |
| `none` | `no` | `IDLE\|BACKOFF_ACTIVE\|RETRY_READY` | `unpaired+paired_false` | `evaluate-liveness` |

## Existing Public Field Mapping

For public rows that remain after candidate exclusion, all fields below are
emitted from the same atomic capture. Their existing types and allowed values
remain unchanged.

| Public field | Projection source | Constraint |
| --- | --- | --- |
| `PairingObservationV1.State` | `coordinator-trust` | `unknown\|denied\|paired\|unpaired-only` |
| `ServiceV1.Paired` | `same-atomic-capture` | `true-only-with-paired-row` |
| `SessionV1.State+Since` | `SHIP-liveness` | `cannot-promote-trust` |
| `RuntimeObservationV1.Degradation` | `closed-precedence` | `existing-reasons-only` |

### Runtime Degradation Precedence

The exact first-match order is `denied-trust` first, then
`certificate-unavailable`, then disconnect, then absence of visible services.
Every prose statement and projection row uses this same order.

| Priority | Reason |
| --- | --- |
| `1` | `denied-trust` |
| `2` | `certificate-unavailable` |
| `3` | `remote-disconnect` |
| `4` | `no-visible-services` |

## Candidate Absence Rule

The ephemeral candidate is removed before public collection enumeration. It
does not create any `PairingObservationV1`, `ServiceV1`, `SessionV1`, or topology row.
No redacted candidate identity or placeholder row is emitted. Candidate
arrival, `association_incomplete`, confirmation, expiry, cancellation, and
pre-durable committing form one flow that does not change public cardinality,
ordering, or timing.

| Candidate condition | Candidate public effect | Existing durable remote rows |
| --- | --- | --- |
| `CANDIDATE_PENDING\|association_incomplete` | `absent-from-all-public-collections` | `absent-without-live-observation` |
| `COMMITTING-before-store-and-anchor-durable` | `absent-from-all-public-collections` | `absent-without-live-observation` |

Durable policy does not create a remote row. A service row
requires an mDNS observation callback, a session row requires a connection
callback, and a candidate requires the pairing callback from that transport
connection. Durable trust may classify an already observed remote; it cannot
create observation cardinality, identity, ordering, or timestamps by itself.

## Admission, Admin, And Privacy Boundary

Configuration allowlist and pretrust are admission inputs only. They cannot
prove durable pairing and cannot promote durable trust. Admin availability is
mutation capability only; it is not evidence of trust, denial, or liveness.
Durable associations are policy, not observation
evidence. Callbacks from the SHIP path report the corresponding observed stage
only.

The candidate identity, fingerprint, nonce, idempotency key, admin path, and
history are never projected. No candidate detail, command detail, protected
identity material, or store record becomes a public observation through this
contract.

## Publication Linearization

State transitions publish after durable or terminal linearization only when a
matching live observation already owns the remote row. Publication observes
the coordinator result; callback arrival is not the trust linearization point,
but policy state cannot create a row. A store `commit_durable` result alone
never publishes `paired`; the exact protected-anchor finalization and a current
transport-backed observation must both exist.

| Linearized outcome | Required publication | Network callback required |
| --- | --- | --- |
| `store-commit-durable+protected-anchor-finalization-durable` | `paired-on-current-observed-row` | `current-observation-required` |
| `commit_not_published+protected-anchor-clear-durable` | `candidate-absent; no policy-derived row` | `current-observation-required-for-row` |
| `commit_applied_maintenance_failed\|commit_durability_unknown\|interruption_or_descriptor_mismatch\|protected-anchor-finalization-unknown` | `unknown+paired-false+denied-trust-on-current-observed-row` | `current-observation-required-for-row` |
| `REVOKED\|TOMBSTONED\|ADMIN_HOLD\|terminal_security_quarantine` | `denied-on-current-observed-row` | `current-observation-required-for-row` |
| `BACKOFF_ACTIVE-or-RETRY_READY+usable-durable-association` | `paired-on-current-observed-row; liveness-only` | `current-observation-required-for-row` |
| `BACKOFF_ACTIVE-or-RETRY_READY+no-usable-durable-association` | `unpaired-on-current-observed-row` | `current-observation-required-for-row` |
| `disconnect\|reconnect-callback` | `liveness-only` | `callback-is-event` |

Maintenance failure, interruption, descriptor mismatch, and every
durability-unknown store or protected-anchor outcome fail closed, keep
`ServiceV1.Paired=false`, and never publish `paired`.

## Startup And Restart Publication

On successful startup or restart, the coordinator reloads durable
classifications privately after structural classification and protected-anchor
checks complete. Reload creates no remote row. A later live observation may
create a row that the coordinator then classifies from that durable state.
Local runtime degradation remains available without a remote callback.

| Classified product | Required publication | Network callback required |
| --- | --- | --- |
| `durably_trusted+store-and-protected-anchor-finalized` | `no-policy-derived-remote-row` | `current-observation-required-for-row` |
| `terminal_denial` | `no-policy-derived-remote-row` | `current-observation-required-for-row` |
| `identity_unavailable` | `runtime-degradation-only` | `no` |
| `not_yet_trusted` | `no-policy-derived-remote-row` | `current-observation-required-for-row` |

## Rollback Ledger

| Case | Projection | Rollback rule |
| --- | --- | --- |
| `pre-durable-cancel\|expiry\|failure\|association_incomplete` | `candidate-absent` | `no-candidate-publication` |
| `store-commit-durable+protected-anchor-finalization-durable` | `paired-on-current-observed-row` | `restart-cannot-create-row` |
| `commit_not_published+protected-anchor-clear-durable` | `candidate-absent` | `no-trust-and-no-policy-derived-row` |
| `commit_applied_maintenance_failed\|commit_durability_unknown\|interruption_or_descriptor_mismatch\|protected-anchor-finalization-unknown` | `unknown+denied-trust-on-current-observed-row` | `fail-closed-without-policy-derived-row` |
| `revocation\|tombstone-terminal` | `denied-on-current-observed-row` | `callback-cannot-resurrect-or-create` |
| `retry-control+usable-durable-association` | `paired-on-current-observed-row` | `retry-cannot-degrade-trust` |
| `retry-control+no-usable-durable-association` | `unpaired-on-current-observed-row` | `retry-cannot-invent-trust` |

## Retry-State Trust Falsifiers

| Falsifier | Required result | Contract is falsified if |
| --- | --- | --- |
| `A66-RETRY-USABLE` | With no row 1 through 3 condition, `BACKOFF_ACTIVE` and `RETRY_READY`, each combined with one usable current-lineage durable association, project `PairingObservationV1.State=paired`, `ServiceV1.Paired=true`, and no `denied-trust`. | Either retry state projects denied or unpaired, clears paired, or emits trust degradation solely because retry control is active. |
| `A66-RETRY-ABSENT` | With no row 1 through 3 condition, each retry state without a usable durable association projects `unpaired` and `ServiceV1.Paired=false`. | Retry control invents paired, durable trust, or a policy-derived row. |
| `A66-RETRY-FAIL-CLOSED` | Structural uncertainty wins first; valid `ADMIN_HOLD`, revocation, current-lineage tombstone, and terminal security quarantine remain denied with `ServiceV1.Paired=false`, regardless of retry state or callbacks. | Any fail-closed condition projects paired, or retry/callback state overrides its precedence. |

## Contract Change Boundary

Issue 66 is the separate corrective review for this still-unpublished,
unimplemented v1 candidate. After its first implementation or publication, any
future change to precedence, state meaning, field mapping, atomicity, authority,
or linearization requires a new contract version and a separate review.
Reinterpreting an implemented or published contract in place is forbidden.
