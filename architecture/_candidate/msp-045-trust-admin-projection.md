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
| `semantic_change` | `new_contract_version+explicit_conformance_migration` |

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
| `indeterminate` | Any incomplete, ambiguous, recovery, or unknown-enum fact. | `unknown+paired_false` |
| `identity_unavailable` | Protected identity is unavailable after the indeterminate check. | `unknown+certificate_unavailable` |
| `terminal_denial` | Revoked, tombstoned, quarantined, corrupt, or admin-held. | `denied+denied-trust` |
| `durably_trusted` | Paired-trusted with one valid, active, trusted, allowlisted, reconnectable, non-tombstoned association in the same lineage. | `paired_or_liveness_degraded` |
| `not_yet_trusted` | Unpaired, open, candidate, or committing before durable commit. | `unpaired+candidate_private` |

There are no additional product classes. Missing or future enum values enter
`indeterminate`; they do not fall through to a permissive state.

## Closed Projection Precedence

First matching row wins. Conditions in a later row cannot override an earlier
row.

| Priority | Coordinator-owned condition | PairingObservationV1.State | ServiceV1.Paired | Trust degradation |
| --- | --- | --- | --- | --- |
| `1` | `incomplete\|ambiguous\|reopen\|reconcile\|repair\|unknown-enum` | `unknown` | `false` | `denied-trust` |
| `2` | `missing-protected-identity` | `unknown` | `false` | `certificate-unavailable` |
| `3` | `revoked\|tombstoned\|quarantined\|corrupt\|admin-held` | `denied` | `false` | `denied-trust` |
| `4` | `PAIRED_TRUSTED+same-lineage+active+trusted+allowlisted+reconnectable+non-tombstoned` | `paired` | `true` | `evaluate-liveness` |
| `5` | `UNPAIRED_LOCKED\|PAIRING_CLOSED\|OPEN_EMPTY\|CANDIDATE_PENDING\|COMMITTING-before-durable-commit` | `unpaired` | `false` | `evaluate-liveness` |
| `6` | `SHIP-callback` | `no-override-of-rows-1-through-5` | `no-override-of-rows-1-through-5` | `liveness-only` |

An incomplete, ambiguous, recovery, or unknown condition is never `paired`.
Committing remains unpaired before durable commit. The candidate identity and
candidate details remain private in every state. A stale callback after
revocation or restart cannot resurrect `paired`.

## Existing Public Field Mapping

All fields below are emitted from the same atomic capture. Their existing
types and allowed values remain unchanged.

| Public field | Projection source | Constraint |
| --- | --- | --- |
| `PairingObservationV1.State` | `coordinator-trust` | `unknown\|denied\|paired\|unpaired-only` |
| `ServiceV1.Paired` | `same-atomic-capture` | `true-only-with-paired-row` |
| `SessionV1.State+Since` | `SHIP-liveness` | `cannot-promote-trust` |
| `RuntimeObservationV1.Degradation` | `closed-precedence` | `existing-reasons-only` |

### Runtime Degradation Precedence

Trust and certificate degradation outrank disconnect and absence of visible
services. The reducer uses the first applicable existing reason.

| Priority | Reason |
| --- | --- |
| `1` | `certificate-unavailable` |
| `2` | `denied-trust` |
| `3` | `remote-disconnect` |
| `4` | `no-visible-services` |

## Admission, Admin, And Privacy Boundary

Configuration allowlist and pretrust are admission inputs only. They cannot
prove durable pairing and cannot promote durable trust. Admin availability is
mutation capability only; it is not evidence of trust, denial, or liveness.
Callbacks from the SHIP path report liveness only.

The candidate identity, fingerprint, nonce, idempotency key, admin path, and
history are never projected. No candidate detail, command detail, protected
identity material, or store record becomes a public observation through this
contract.

## Publication Linearization

State transitions publish after durable or terminal linearization even without
a network callback. Publication observes the coordinator result; callback
arrival is not the trust linearization point.

| Linearized outcome | Required publication | Network callback required |
| --- | --- | --- |
| `commit_durable` | `paired` | `no` |
| `commit_not_published` | `unpaired` | `no` |
| `durability_unknown\|reopen\|reconcile\|repair` | `unknown` | `no` |
| `revoked\|tombstoned\|quarantined\|corrupt\|admin-held` | `denied` | `no` |
| `disconnect\|reconnect-callback` | `liveness-only` | `callback-is-event` |

## Rollback Ledger

| Case | Projection | Rollback rule |
| --- | --- | --- |
| `pre-durable-cancel\|expiry\|failure` | `unpaired` | `no-candidate-publication` |
| `commit_durable` | `paired` | `callback-cannot-roll-back` |
| `commit_not_published` | `unpaired` | `no-trust-and-no-candidate-publication` |
| `durability_unknown\|repair-in-progress` | `unknown+denied-trust` | `fail-closed-until-terminal` |
| `revocation\|tombstone-terminal` | `denied+denied-trust` | `callback-cannot-resurrect` |

## Migration Boundary

Any future change to precedence, state meaning, field mapping, atomicity,
authority, or linearization requires a new contract version and an explicit
conformance migration. Reinterpreting this contract in place is forbidden.
