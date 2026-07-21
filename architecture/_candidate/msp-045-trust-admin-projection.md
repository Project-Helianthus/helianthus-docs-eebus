---
canonical_source: "Project-Helianthus/helianthus-docs-eebus:architecture/_candidate/msp-045-trust-admin-projection.md"
owner_domain: "architecture"
license: "AGPL-3.0-only"
publication_status: "candidate"
claim_status: "evidence-backed"
source_class: "derived_inference"
evidence_ids: "EV-20260711-001"
hypothesis_status: "draft"
falsifier: "An accepted architecture review or conformance result demonstrates that the frozen projection can report paired without durable coordinator authority, leak private trust or admin data, change the public API or disk schema, or violate the closed precedence."
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
| `semantic_change` | `new_contract_version+separate_review` |

This contract is not a public Go API, not a disk schema, not an admin wire
schema, and not an MCP schema. It adds no field, enum value, mutation, or
storage record. The disk store remains control schema v3, and the public API
manifest remains byte-identical to the frozen hash above.

## Combined State Product

The atomic coordinator capture contains the trust lifecycle, protected
identity availability, durable association state, association lineage and
eligibility, terminal denial state, and transport liveness. The projection
reduces that product through the closed precedence below.

| Product class | Coordinator-owned facts | Allowed projection class |
| --- | --- | --- |
| `structural_indeterminate` | Exactly `CORRUPT_STORE`, `DURABILITY_UNKNOWN`, `HOST_BINDING_MISMATCH`, `CLONE_DETECTED`, `MANIFEST_GENERATION_ROLLBACK`, `CONTROL_EPOCH_ROLLBACK`, `REOPEN_IN_PROGRESS`, `RECONCILIATION_IN_PROGRESS`, `REPAIR_IN_PROGRESS`, or `UNKNOWN_ENUM`. | `unknown+paired_false+denied-trust` |
| `terminal_denial` | Revoked, tombstoned, admin-held, backoff-held, or otherwise quarantined after no structural-indeterminate reason matched. | `denied+denied-trust` |
| `identity_unavailable` | Protected identity is unavailable after the structural and terminal-denial checks. | `unknown+certificate_unavailable` |
| `durably_trusted` | Paired-trusted only after the store commit and exact protected-anchor finalization are both durable, with one valid, active, trusted, allowlisted, reconnectable, non-tombstoned association in the same lineage. | `paired_or_liveness_degraded` |
| `not_yet_trusted` | Unpaired or open durable state, or candidate flow after the ephemeral candidate has been excluded from public enumeration. | `unpaired_existing_only+candidate_absent` |

There are no additional product classes. Missing or future enum values enter
`structural_indeterminate`; they do not fall through to a permissive state.
The structural facts above are an explicit closed structural-state set.
`association_incomplete` is not a structural unknown; it is the normal volatile
candidate flow governed only by the candidate-absence and unpaired rule below.

## Closed Projection Precedence

First matching row wins. Conditions in a later row cannot override an earlier
row.

| Priority | Coordinator-owned condition | PairingObservationV1.State | ServiceV1.Paired | Trust degradation |
| --- | --- | --- | --- | --- |
| `1` | `CORRUPT_STORE\|DURABILITY_UNKNOWN\|HOST_BINDING_MISMATCH\|CLONE_DETECTED\|MANIFEST_GENERATION_ROLLBACK\|CONTROL_EPOCH_ROLLBACK\|REOPEN_IN_PROGRESS\|RECONCILIATION_IN_PROGRESS\|REPAIR_IN_PROGRESS\|UNKNOWN_ENUM` | `unknown` | `false` | `denied-trust` |
| `2` | `REVOKED\|TOMBSTONED\|QUARANTINED\|ADMIN_HOLD\|BACKOFF_ACTIVE` | `denied` | `false` | `denied-trust` |
| `3` | `missing-protected-identity` | `unknown` | `false` | `certificate-unavailable` |
| `4` | `PAIRED_TRUSTED+store-and-protected-anchor-finalized+same-lineage+active+trusted+allowlisted+reconnectable+non-tombstoned` | `paired` | `true` | `evaluate-liveness` |
| `5` | `UNPAIRED_LOCKED\|PAIRING_CLOSED\|OPEN_EMPTY\|association_incomplete\|CANDIDATE_PENDING\|COMMITTING-before-store-and-anchor-durable` | `unpaired` | `false` | `evaluate-liveness` |
| `6` | `SHIP-callback` | `no-override-of-rows-1-through-5` | `no-override-of-rows-1-through-5` | `liveness-only` |

Every condition that produces `denied-trust` precedes
`missing-protected-identity`; therefore denial outranks
`certificate-unavailable` everywhere in this contract. Structural and terminal
denial is never `paired`. Rows 4 and 5 operate per durable remote record only
after candidate exclusion. In row 5, candidate conditions classify coordinator
status but create no candidate row; only separately existing durable records
can remain `unpaired`. A stale callback after revocation or restart cannot
resurrect `paired`.

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
| `REVOKED\|TOMBSTONED\|QUARANTINED\|ADMIN_HOLD\|BACKOFF_ACTIVE` | `denied-on-current-observed-row` | `current-observation-required-for-row` |
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

## Contract Change Boundary

Any future change to precedence, state meaning, field mapping, atomicity,
authority, or linearization requires a new contract version and a separate
review. Reinterpreting this contract in place is forbidden.
