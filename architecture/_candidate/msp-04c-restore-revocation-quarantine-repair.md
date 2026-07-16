---
canonical_source: "Project-Helianthus/helianthus-docs-eebus:architecture/_candidate/msp-04c-restore-revocation-quarantine-repair.md"
owner_domain: "architecture"
license: "AGPL-3.0-only"
publication_status: "candidate"
claim_status: "evidence-backed"
source_class: "derived_inference"
evidence_ids: "EV-20260711-001"
hypothesis_status: "draft"
falsifier: "An accepted architecture review or conformance result demonstrates that MSP-04C can silently restore trust, start a remote effect before coordinator authorization, bypass production-composed persistent quarantine, report revocation before authoritative runtime withdrawal, lose a tombstone, or expose a public mutation or identity surface under this contract."
stable_navigation: "false"
search: "false"
sitemap: "false"
versioned_bundle: "false"
release_bundle: "false"
---

# Candidate MSP-04C-R Restore, Revocation, Quarantine, Repair, And Runtime Composition Contract

## Status And Authority

This is the pre-implementation candidate contract for MSP-04C. It constrains
the [companion source issue][code-issue] but does not claim that restore,
revocation, quarantine, or repair is implemented or supported. It follows the
[MSP-04A store contract][store-contract], the [MSP-04B trust contract][trust-contract],
the locked [MSP-04C execution-plan row][plan-row], and exact
[EEBUS-G10/G11/G16 gate definitions][gate-contract]. The active cruise run is
tracked by [meta issue 58][meta-issue].

The MSP-04C-R correction is tracked by [docs issue 26][corrective-docs-issue]
and [corrective source issue 30][corrective-source-issue]. The earlier MSP-04C
source merge is a predecessor, not evidence that the production callback on
the SHIP path, registration, reconnect, and revocation withdrawal lifecycle
satisfies this corrected contract.

These are project security and ownership decisions, not protocol claims.
Stable API, navigation, search, sitemap, versioned-bundle, and release-bundle
outputs intentionally omit this candidate.

## Corrective Source Evidence Status

All source-controlled fields below remain pending until the corrective source
merges from [source issue 30](https://github.com/Project-Helianthus/helianthus-eebusreg/issues/30).
This candidate does not predict a source head, CI run, artifact identity, or
closure verdict.

| Evidence field | Candidate value | Required closure evidence |
| --- | --- | --- |
| `corrective_source_head_sha` | `pending` | Full reviewed 40-character source head that implements this correction. |
| `corrective_source_merge_sha` | `pending` | Full 40-character squash merge on source `main`. |
| `corrective_source_exact_head_ci_run` | `pending` | Successful exact-head source CI run identifier. |
| `corrective_source_post_merge_ci_run` | `pending` | Successful post-merge source `main` CI run identifier. |
| `eebus_g10_integration_artifact` | `pending` | Immutable redacted artifact from executed production-composed G10 cases. |
| `eebus_g11_integration_artifact` | `pending` | Immutable redacted artifact from executed production callback, restart, retry, and terminal-quarantine cases. |
| `eebus_g16_integration_artifact` | `pending` | Immutable redacted scan artifact over the executed integration behavior and its outputs. |
| `m4_architecture_closure_verdict` | `pending` | Bounded post-merge architecture review result, `PASS` or `PASS_WITH_CARRIED_EVIDENCE`. |
| `platform_provider_attestation` | `pending_ssh_only_non_normative` | Provider-specific no-export, host-binding, and backup-exclusion attestation from an eligible platform lane. |

An existing MSP-04C merge, unit helper, or synthetic helper result does not
satisfy or replace any executed integration field. SSH-only platform
observations remain supporting, non-normative evidence. They cannot clear
`platform_provider_attestation`, claim a portable provider, or substitute for
the deterministic integration gates.

## Normative Language And Boundary

`MUST`, `MUST NOT`, `SHOULD`, and `MAY` define MSP-04C acceptance. Names in
this page are private conformance vocabulary, not exported Go declarations or
a stable disk/admin format.

The private trust coordinator owns restore classification, trust-state
transitions, revocation, quarantine, retry policy, and repair authorization.
`internal/eebusstore` remains mechanical and policy-free: it validates a
closed internal schema, canonical bytes, bounds, generations, and durability;
it never interprets a reason, selects a repair, computes backoff, clears a
tombstone, or decides trust. Any new coordinator-owned records require an
explicit internal schema version and deterministic MSP-04A migration. The
store persists the caller's complete proposed generation atomically and
returns one existing deterministic store outcome.

A separate internal host-anchor provider owns only sealed, non-restorable
anchor bytes and deterministic durability outcomes. It has no remote identity,
pairing, trust, quarantine, or repair policy. The coordinator is the sole
writer across store, anchor, facade effects, and AF_UNIX commands.

## Durable Control And Host Anchor

The coordinator-owned control record is inside the selected store generation.
It contains a random store-instance value, a monotonic control epoch,
an association-lineage value, revocation tombstones, quarantine records,
bounded admin-operation receipts, and the state of any coordinated store/anchor
publication. Remote references remain opaque and sensitive. They never become
paths, errors, metrics, fixture names, or public fields.

The host anchor is outside the restorable store set and contains only:

- a provider version and random runtime-local anchor identity;
- the bound random store-instance value;
- high-water manifest generation and control epoch values; and
- at most one exact pending publication descriptor in the closed form below.

The pending descriptor contains exactly these fields. A generation binding is
the complete MSP-04A generation reference: sequence, filename, SHA-256, and
schema version. A manifest SHA-256 is the envelope's digest of the complete
canonical manifest payload, so a sequence number never identifies a branch by
itself.

| Field | Exact binding |
| --- | --- |
| `operation_id` | Bounded coordinator-issued idempotency identifier, never reused within one anchor identity. |
| `operation_class` | One closed coordinator operation kind: first trust, revocation, or one enumerated repair kind. |
| `store_instance` | Exact random store-instance value observed before staging. |
| `previous_control_epoch` | Exact control epoch in the selected previous generation. |
| `target_control_epoch` | Exactly `previous_control_epoch + 1`, represented without overflow. |
| `previous_manifest_epoch` | Exact selected manifest epoch before the operation. |
| `previous_manifest_sha256` | Exact selected canonical manifest-payload digest before the operation. |
| `previous_generation` | Complete selected-current generation reference before the operation. |
| `target_manifest_epoch` | Exact epoch-plus-one manifest intended for publication. |
| `target_manifest_sha256` | Exact digest of the intended canonical target manifest payload. |
| `target_generation` | Complete intended target generation reference. |

Staging, finalization, clearing, and reconciliation compare every descriptor
field. The previous and target generation sequences MUST differ and the target
manifest epoch MUST advance by one, but those numeric checks never replace the
digest and complete-reference comparisons. A same-number generation or
manifest branch with different bytes is a mismatch, not a reconciliation
candidate.

The anchor contains no machine id, hostname, hardware serial, MAC/IP address,
account id, remote SKI, SHIP ID, certificate fingerprint, or peer-derived
digest. Clone detection compares independently durable random bindings; it
does not disclose or derive a host-global identity.

The provider MUST attest host/deployment binding, no-export access, monotonic
compare-and-advance, and a durability domain that cannot be rolled back with
the protected store. It must also attest anchor non-restorability or effective
exclusion from every supported backup path. A path name, mode bit,
configuration flag, or persisted `backup_excluded` boolean is not an
attestation. An unavailable or ambiguous capability fails closed.

The provider-specific host-anchor backend is a source implementation choice.
Every backend nevertheless MUST provide authenticated no-export access,
host/deployment binding, durable exact compare-and-stage, compare-and-finalize,
and compare-and-clear operations, monotonic high-water updates, and explicit
durability outcomes. An unsupported primitive or ambiguous result fails closed;
there is no weaker file-only fallback.

## Coordinated Store And Anchor Publication

Every operation that can change trust, revocation, lineage, or a high-water mark
uses one protocol. Under the coordinator's one-writer lock it validates the
complete request, constructs the exact target generation and descriptor, and
durably stages that descriptor in the anchor before calling MSP-04A Commit. It
then applies exactly this outcome map:

| Store result | Required exact anchor action | Allowed immediate result |
| --- | --- | --- |
| `commit_durable` | `compare_and_finalize(exact_descriptor)` atomically advances the bound high-water values and clears that descriptor. | `success_only_after_durable_finalize` |
| `commit_not_published` | `compare_and_clear(exact_descriptor)` without advancing a high-water value. | `failed_closed_unchanged_only_after_durable_clear` |
| `commit_applied_maintenance_failed` | `retain(exact_descriptor)` for explicit reconciliation after reopen. | `DURABILITY_UNKNOWN` |
| `commit_durability_unknown` | `retain(exact_descriptor)` for explicit reconciliation after reopen. | `DURABILITY_UNKNOWN` |
| `interruption_or_descriptor_mismatch` | `retain(exact_descriptor)` and disable mutation. | `DURABILITY_UNKNOWN` |

For `commit_not_published`, unchanged store state is reportable only after the
provider durably completes compare-and-clear against the byte-identical pending
descriptor. A compare mismatch, clear failure, ambiguous durability result, or
crash before durable clear makes durability unknown and enters `QUARANTINED`;
the coordinator MUST NOT infer rollback from the store result alone. An
unresolved pending descriptor at startup has the same result.

Reconciliation is an authenticated admin operation and never runs
automatically. After MSP-04A Open selects one current manifest, it uses this
closed decision table:

| Store observation | Required anchor action | Reconciliation result |
| --- | --- | --- |
| `exact_target_selected` | `compare_and_finalize(exact_descriptor)` | `operation_terminal_only_after_durable_finalize` |
| `exact_previous_selected_and_target_absent` | `compare_and_clear(exact_descriptor)` | `failed_closed_unchanged_only_after_durable_clear` |
| `same_number_different_digest_or_reference` | `none` | `DURABILITY_UNKNOWN/QUARANTINED` |
| `other_or_ambiguous` | `none` | `DURABILITY_UNKNOWN/QUARANTINED` |

`exact_target_selected` requires the target manifest epoch and digest, complete
target generation reference, target control epoch, operation id, class, and
store instance all to match. The previous-state case requires the complete
previous bindings to match and proof that the exact target is not selected or
publication-valid. Therefore reconciliation cannot bless a different branch
merely because it reuses a manifest epoch or generation sequence.

## Startup Classification And Precedence

MSP-04A Open precedence remains authoritative through selection and validation
of the current generation. MSP-04C never falls back to a lower manifest or an
orphan. The table is the combined startup classification: store-owned
structural failure is decided before policy rows, and rows that inspect control
state are considered only after a mechanically valid current generation is
returned; the first matching row wins:

| Precedence | Reason | Distinguishing evidence | State |
| --- | --- | --- | --- |
| 1 | `CORRUPT_STORE` | Current state is structurally invalid under MSP-04A and no policy record is available. | `CORRUPT_STORE` |
| 2 | `DURABILITY_UNKNOWN` | Store durability is unknown, the host anchor has an unresolved pending publication, or store/anchor finalization cannot be proved. | `QUARANTINED` |
| 3 | `HOST_KEY_UNAVAILABLE` | The protected local signing capability or required anchor provider is absent/unavailable, without evidence that it belongs to another host. | `NO_LOCAL_IDENTITY` |
| 4 | `HOST_BINDING_MISMATCH` | Provider validation positively reports wrong-host or wrong-deployment protected material. | `QUARANTINED` |
| 5 | `CLONE_DETECTED` | A valid local host anchor binds a different random store-instance value. | `QUARANTINED` |
| 6 | `MANIFEST_GENERATION_ROLLBACK` | The selected manifest generation is below the anchor's durable high-water generation. | `QUARANTINED` |
| 7 | `CONTROL_EPOCH_ROLLBACK` | The selected coordinator control epoch is below the anchor's durable high-water control epoch. | `QUARANTINED` |
| 8 | `REVOKED_ASSOCIATION` | The otherwise matching association has a durable effective tombstone. | `REVOKED` |
| 9 | persisted quarantine reason | An exact active `ADMIN_HOLD` or `BACKOFF_ACTIVE` record applies. | `QUARANTINED` |

Absence is not positive clone evidence. A copied store on a fresh host with no
usable anchor is `HOST_KEY_UNAVAILABLE`; wrong-host key attestation is
`HOST_BINDING_MISMATCH`; an instance conflict is `CLONE_DETECTED`.
`CONTROL_EPOCH_ROLLBACK` is logical-state rollback, while
`MANIFEST_GENERATION_ROLLBACK` is rollback of the selected manifest's current
generation. Logical rollback, manifest rollback, and durability uncertainty
therefore remain separate terminal reasons. Errors and evidence report only
these stable reason labels and bounded counters.

## Production Runtime Composition And Authorization

Startup keeps listener creation, remote registration, reconnect scheduling,
and pairing callbacks inert. Store/anchor selection, tombstone precedence,
trust classification and retry restoration complete before any listener is
started or any remote effect is considered. A classification or restore
failure therefore disables those effects rather than allowing the production
runtime to start and attempting to withdraw them later.

| Runtime event | Required coordinator decision | Permitted effect |
| --- | --- | --- |
| `startup_restore` | `classify_startup_and_restore_retry` | `none_before_durable_classification` |
| `listener_start` | `authorize_listener_start(classified_state)` | `start_listener` |
| `pairing_handshake` | `authorize_handshake(exact_scope)` | `real_pairing_transport_callback` |
| `remote_registration` | `authorize_register_remote_ski(exact_association)` | `RegisterRemoteSKI` |
| `reconnect_attempt` | `authorize_reconnect(exact_association,exact_scope)` | `reconnect` |
| `handshake_failure` | `record_failure_and_checkpoint(exact_scope)` | `no_next_attempt_before_durable_result` |

Every call to `RegisterRemoteSKI` and every reconnect decision is
coordinator-authorized against the exact selected generation, control epoch,
association lineage, tombstone set, trust state, and retry scope. No runtime
adapter, restored configuration, library callback, or caller may infer that
authorization. Authorization and the corresponding effect are serialized
with revocation and repair; an asynchronous completion is revalidated before
it can make trust usable, and a stale completion is actively disconnected and
unregistered.

The real pairing callback on the SHIP path obtains admission before continuing
a handshake. Its terminal failure path records the failure into durable retry
state and completes a durable remaining-delay checkpoint before the callback
releases the scope for another attempt. The production checkpoint path
persists only a same-boot monotonic reduction, and startup restores the
persisted state and rearms it on the new monotonic clock before any effect. The
same listener, registration, handshake, and reconnect authorization path
observes that restored state after restart.

A helper-only backoff API, direct coordinator unit call, caller-provided
success/failure assertion, or transcript that does not execute this production
composition is not G11 proof. The real callback must drive the coordinator
record, checkpoint, restart restore, bounded backoff, and terminal quarantine.

## Orthogonal Coordinator And Recovery State Machines

MSP-04B's coordinator FSM and MSP-04C's recovery/trust FSM are orthogonal axes,
not one replacement state list. The MSP-04B axis remains exactly `DISABLED`,
`PAIRING_CLOSED`, `OPEN_EMPTY`, `CANDIDATE_PENDING`, and `COMMITTING`, with its
existing candidate, window, and terminal rules unchanged. MSP-04C adds only the
second axis: `NO_LOCAL_IDENTITY`, `UNPAIRED_LOCKED`, `PAIRED_TRUSTED`, `REVOKED`,
`QUARANTINED`, and `CORRUPT_STORE`.

### Valid Cross-Product

Only these products are valid after startup classification has linearized. A
product not listed is forbidden and fails closed to
`DISABLED/QUARANTINED` unless MSP-04A has already selected `CORRUPT_STORE`.

| MSP-04B coordinator state | Allowed MSP-04C recovery/trust states |
| --- | --- |
| `DISABLED` | `NO_LOCAL_IDENTITY`, `QUARANTINED`, `CORRUPT_STORE` |
| `PAIRING_CLOSED` | `UNPAIRED_LOCKED`, `PAIRED_TRUSTED`, `REVOKED` |
| `OPEN_EMPTY` | `UNPAIRED_LOCKED`, `REVOKED` |
| `CANDIDATE_PENDING` | `UNPAIRED_LOCKED`, `REVOKED` |
| `COMMITTING` | `UNPAIRED_LOCKED`, `REVOKED` |

The one-writer lock may hold an operation in progress without publishing an
intermediate product. During that interval facade effects are denied and no
other event can observe or mutate either axis. The operation publishes only one
of the terminal products below.

### Recovery/Trust Axis Transitions

| MSP-04C state | Allowed next MSP-04C states |
| --- | --- |
| `NO_LOCAL_IDENTITY` | `UNPAIRED_LOCKED`, `QUARANTINED` |
| `UNPAIRED_LOCKED` | `PAIRED_TRUSTED`, `QUARANTINED`, `CORRUPT_STORE` |
| `PAIRED_TRUSTED` | `REVOKED`, `QUARANTINED`, `CORRUPT_STORE` |
| `REVOKED` | `PAIRED_TRUSTED`, `QUARANTINED` |
| `QUARANTINED` | `UNPAIRED_LOCKED`, `REVOKED`, `CORRUPT_STORE` |
| `CORRUPT_STORE` | `UNPAIRED_LOCKED`, `REVOKED`, `QUARANTINED` |

`UNPAIRED_LOCKED` or `REVOKED` reaches `PAIRED_TRUSTED` only through a later
explicit MSP-04B window, a new exact OOB confirmation, and durable coordinated
publication. A `REVOKED` transition uses a new association lineage and cannot
reuse a tombstoned association. Repair never takes either transition.

### Transition Precedence And Linearization

Every event acquires the same one-writer lock and has one coordinator
linearization point. Lock acquisition order decides between concurrent valid
events; within the winning event, these checks have strict precedence:

| Precedence | Rule at the linearization point |
| --- | --- |
| `1` | MSP-04A structural selection and unresolved store/anchor durability evidence disable the MSP-04B axis and select `CORRUPT_STORE` or `QUARANTINED`. |
| `2` | A staged coordinated publication is completed or classified before any new pairing, revocation, repair, retry, or startup effect. |
| `3` | An exact revocation or repair command closes/cancels MSP-04B window and candidate state before its store mutation begins. |
| `4` | An MSP-04B close, expiry, cancel, exact confirmation, open, or admission event applies its existing first-terminal-rule ordering if the current cross-product permits it. |

The exact confirmation path preserves the MSP-04B transition that MSP-04C
depends on:

| Confirmation phase/outcome | Required combined transition |
| --- | --- |
| `exact_confirmation_linearizes` | `CANDIDATE_PENDING/untrusted -> COMMITTING/same_untrusted` |
| `store_and_anchor_durable` | `COMMITTING/same_untrusted -> PAIRING_CLOSED/PAIRED_TRUSTED` |
| `commit_not_published_and_anchor_cleared` | `COMMITTING/same_untrusted -> PAIRING_CLOSED/same_untrusted` |
| `publication_unknown` | `COMMITTING/same_untrusted -> DISABLED/QUARANTINED` |

Here `untrusted` is exactly `UNPAIRED_LOCKED` or `REVOKED`. Confirmation closes
the window and moves `CANDIDATE_PENDING` to `COMMITTING` before any store or
anchor mutation. The recovery/trust axis remains unchanged until both durable
boundaries are known. Startup never enters `PAIRED_TRUSTED` from copied,
restored, rolled-back, legacy-anchorless, host-key-unavailable, or
durability-unknown state. A repair result never transitions directly to
`PAIRED_TRUSTED`, invokes `RegisterRemoteSKI`, or opens a pairing window.

## Durable Revocation Tombstones

Revocation is exactly the `revoke_association` command in the closed command set
of the existing MSP-04B AF_UNIX admin endpoint. Kernel-reported
same-effective-UID authentication succeeds before frame parsing. Unknown
commands and fields are rejected. There is no TCP, loopback, HTTP, CLI,
environment, file-drop, MCP, GraphQL, Portal, Home Assistant, exported Go, or
other public revocation path.

The request contains exactly one target and the following complete binding:

| Revocation request field | Exact binding |
| --- | --- |
| `operation_id` | Bounded idempotency identifier for this command. |
| `association_ref` | Exact opaque active association reference; no prefix, peer-only, or wildcard match. |
| `association_lineage` | Exact current lineage containing that association. |
| `expected_store_generation` | Complete selected-current MSP-04A generation reference. |
| `expected_manifest_epoch` | Exact selected manifest epoch. |
| `expected_manifest_sha256` | Exact selected canonical manifest-payload digest. |
| `expected_control_epoch` | Exact control epoch in that generation. |

The coordinator authenticates, parses, validates, and serializes revocation
with startup, pairing, retry, repair, facade effects, anchor operations, and
store Commit under the same one-writer lock. Any stale target, lineage,
generation reference, manifest binding, or control epoch returns conflict
without changing in-memory or durable state.

The control record durably retains the full request binding and terminal result
in a bounded receipt. Replay behavior is closed:

| Revocation request condition | Stable result | Additional mutation |
| --- | --- | --- |
| `new_exact_request` | `commit_once` | `one_coordinated_publication` |
| `identical_in_flight_replay` | `operation_in_progress` | `none` |
| `identical_terminal_replay` | `recorded_terminal_result` | `none` |
| `operation_id_with_changed_binding` | `idempotency_conflict` | `none` |
| `stale_association_or_generation` | `revocation_conflict` | `none` |
| `replay_at_or_below_compacted_high_water` | `idempotency_expired` | `none` |

Identical means byte-for-byte equality of every decoded request field, not only
the operation id. Terminal replay remains idempotent across restart. Receipt
compaction may retain only a non-identifying operation-id high water after its
bounded retention condition, but can never permit an old id to execute again.

Revocation first closes pairing and denies the target in memory, then proposes
one generation that both deactivates the association and appends an effective
tombstone. A tombstone binds the opaque association reference, revocation
epoch, operation id, and effective generation. Only after store and anchor
finalization are durable may runtime withdrawal begin. Durable publication is
necessary but not sufficient: the coordinator does not report `revoked` until
the exact runtime withdrawal below also completes.

### Authoritative Runtime Withdrawal

| Revocation phase | Required effect | Success condition |
| --- | --- | --- |
| `deny_in_memory` | `coordinator_deny_exact_association` | `registration_and_reconnect_denied` |
| `commit_tombstone` | `durable_coordinated_publication` | `tombstone_and_anchor_finalized` |
| `disconnect_active_session` | `DisconnectSKI(exact_remote_ski)` | `disconnected_or_authoritatively_absent` |
| `unregister_remote` | `UnregisterRemoteSKI(exact_remote_ski)` | `unregistered_or_authoritatively_absent` |
| `return_success` | `record_terminal_revoked` | `all_prior_phases_complete` |

The coordinator invokes both `DisconnectSKI` and `UnregisterRemoteSKI`; it does
not skip either call based only on cached liveness or registration state. An
authoritative already-absent result is idempotent success for that effect. If
either withdrawal fails or is ambiguous, the tombstone remains effective,
the association stays denied, the command reports
`revocation_withdrawal_incomplete`, and the receipt cannot record terminal
`revoked`. Exact replay may finish the missing withdrawal but cannot repeat or
undo the tombstone publication.

On startup, a tombstone takes precedence over a durable association and blocks
automatic reload. Startup must not call `RegisterRemoteSKI`, schedule
reconnect, restore allowlist trust, or admit a candidate for any tombstoned
association. Restart does not clear it or convert an incomplete withdrawal
into success.
`commit_not_published` plus exact durable anchor clear retains in-process denial
but reports unchanged durable state. Clear failure, crash before durable clear,
`commit_applied_maintenance_failed`, `commit_durability_unknown`, or other
anchor uncertainty enters `DURABILITY_UNKNOWN` quarantine with no trust effect.

Repair cannot delete, truncate, rewrite, or mark a tombstone ineffective.
Compaction may move old tombstones into a versioned deny set only if exact deny
behavior and revocation high-water evidence are preserved. Capacity exhaustion
fails closed; it never evicts the oldest tombstone. A later explicit OOB flow
creates a new association lineage and does not resurrect the tombstoned record.

## Persistent Quarantine And Backoff

Each quarantine record persists an opaque scope, stable reason, state
(`BACKOFF_ACTIVE`, `RETRY_READY`, or `ADMIN_HOLD`), saturating attempt count,
bounded backoff step, bounded remaining delay, bounded retention budget, and
last control epoch. Clone, rollback, host-binding, revocation-uncertainty, and
durability reasons use `ADMIN_HOLD` and never retry automatically.

For a new retryable scope the initial durable tuple is
`(state=RETRY_READY, attempt_count=0, remaining_delay=0)`. Admission does not
increment the count. If that admitted handshake fails, the coordinator
linearizes the failure, computes and atomically persists these values before it
releases the one-writer lock:

```text
next_attempt_count = min(attempt_count + 1, attempt_count_max)
if next_attempt_count == attempt_count_max:
    next = (ADMIN_HOLD, next_attempt_count, 0, HANDSHAKE_ATTEMPT_LIMIT)
else:
    exponent = min(next_attempt_count - 1, exponent_cap)
    delay = min(checked(base_backoff * 2^exponent), max_backoff)
    next = (BACKOFF_ACTIVE, next_attempt_count, delay)
```

When `attempt_count_max > 1`, the first nonterminal admitted failure uses
`base_backoff`. The count increments exactly at failure linearization, never on
admission, denial, restart, deadline expiry, or wall-clock change. At
`attempt_count_max`, that failure atomically enters terminal `ADMIN_HOLD` with
reason `HANDSHAKE_ATTEMPT_LIMIT` and zero remaining delay; no later handshake
or reconnect is automatically admitted. There is no admitted failure at an
already saturated count. Exponent saturation begins when
`next_attempt_count - 1 >= exponent_cap`; duration saturation occurs when the
checked product reaches `max_backoff`. A nonterminal retry is admitted only
after a durable `BACKOFF_ACTIVE -> RETRY_READY` transition with unchanged
attempt count. Leaving terminal hold requires the exact authenticated repair
contract and never follows elapsed time or restart.

`base_backoff`, `max_backoff`, `attempt_count_max`, and `exponent_cap` are
source implementation constants, not portable API values. They MUST satisfy
`base_backoff > 0`, `max_backoff >= base_backoff`,
`attempt_count_max >= 1`, and `exponent_cap >= 0`, fit the closed persisted
ranges, and be covered by boundary tests. Checked multiplication that would
overflow saturates to `max_backoff`; an invalid configured or decoded bound,
underflow, negative duration, or out-of-range persisted value enters
`ADMIN_HOLD` and admits no retry. There is no jitter.

Wall clock is never used to derive or shorten a deadline. The durable
representation is only `(state, attempt_count, remaining_delay)`; it contains
no wall timestamp and no monotonic timestamp from an earlier boot. While
running, the volatile representation is
`deadline_monotonic = monotonic_now + remaining_delay`. A checkpoint may reduce
the durable remainder only from elapsed time measured on that same monotonic
clock and only after the reduced remainder is durable. A crash before that
durability point leaves the earlier, greater remainder authoritative.

After restart the coordinator sets
`deadline_monotonic = new_monotonic_now + persisted_remaining_delay`. It first
persists `RETRY_READY` with zero remainder when that deadline is reached, then
may admit one retry. Restart or wall-clock change can extend a wait but can
never decrement attempt state, shorten the persisted remainder, admit early
retry, or restore trust. A checkpoint or ready-transition durability failure
fails closed in `BACKOFF_ACTIVE` or `ADMIN_HOLD`. The configured bound applies
to stored duration and each armed interval; repeated crashes may conservatively
extend elapsed wall time.

### EEBUS-G11 Deterministic Vector

The required synthetic vector injects
`base_backoff=3s`, `exponent_cap=2`, `max_backoff=10s`, and
`attempt_count_max=4`. These are fixture values and do not freeze production
policy constants.

| Step | Event | Previous count | Persisted count | Persisted delay | Persisted state |
| --- | --- | --- | --- | --- | --- |
| `0` | `new_scope` | `not_applicable` | `0` | `0s` | `RETRY_READY` |
| `1` | `first_admitted_failure` | `0` | `1` | `3s` | `BACKOFF_ACTIVE` |
| `2` | `second_admitted_failure` | `1` | `2` | `6s` | `BACKOFF_ACTIVE` |
| `3` | `third_admitted_failure` | `2` | `3` | `10s` | `BACKOFF_ACTIVE` |
| `4` | `fourth_admitted_failure` | `3` | `4` | `0s` | `ADMIN_HOLD` |

The restart arm in the same vector is exact:

| Checkpoint | Durable tuple | Volatile monotonic state | Required decision |
| --- | --- | --- | --- |
| `after_step_2` | `BACKOFF_ACTIVE,count=2,remainder=6s` | `now=20s,deadline=26s` | `deny_retry` |
| `durable_checkpoint_after_2s` | `BACKOFF_ACTIVE,count=2,remainder=4s` | `now=22s,deadline=26s` | `deny_retry` |
| `restart_with_arbitrary_wall_change` | `BACKOFF_ACTIVE,count=2,remainder=4s` | `new_now=100s,new_deadline=104s` | `deny_retry` |
| `probe_before_rearmed_deadline` | `BACKOFF_ACTIVE,count=2,remainder=4s` | `new_now=103.999s,new_deadline=104s` | `deny_retry` |
| `probe_at_rearmed_deadline` | `RETRY_READY,count=2,remainder=0s` | `new_now=104s` | `persist_ready_before_admit` |

Active records are never evicted to satisfy a count or retention bound. After
a successful trusted handshake or exact repair, detailed terminal history may
compact only after the bounded monotonic retention budget is consumed. The
compacted record retains reason class, saturated attempt summary, control-epoch
high water, and outcome without peer material. At capacity, the coordinator
enters `ADMIN_HOLD` and rejects new attempts rather than deleting evidence.

## Deterministic Admin-Local Repair

Repair extends the existing MSP-04B AF_UNIX endpoint only. Kernel-reported
same-effective-UID authentication occurs before frame parsing. There is no TCP,
loopback, HTTP, CLI, environment, file-drop, MCP, GraphQL, Portal, Home
Assistant, or remote repair path.

Every repair request binds exactly one repair kind and scope plus
`expected_state`, `expected_reason`, the complete selected manifest epoch,
digest, and current/parent generation references, control epoch, anchor
version/high-water values, a bounded operation/idempotency id, and the next
monotonic repair sequence. Supported kinds are limited to
`reconcile_pending_publication`, `publish_inactive_parent`,
`adopt_copied_current`, `recover_unavailable_host_key`, or
`release_retry_quarantine`. A stale, digest-incomplete, same-number or
different-branch binding, or broader binding returns `repair_conflict` with no
mutation.

The coordinator serializes repair with pairing, revocation, retry, startup,
and store commit under the existing one-writer lock. It durably records the
full request binding and terminal result in a bounded private repair receipt.
An identical replay, including after restart, returns that result without a
second mutation. Reuse of the key with any changed field returns
`idempotency_conflict`. Expired receipts may compact to a non-identifying
repair-sequence high-water summary. A replay at or below that high water returns
`idempotency_expired` with no mutation. Active evidence, tombstones, and
detection lineage remain intact.

Repair publishes a new generation; it never edits a manifest, generation,
anchor, tombstone, or recovery candidate in place. The new generation appends
the detection and repair result, preserves immutable prior evidence, and lands
in `UNPAIRED_LOCKED` or `REVOKED`. It cannot erase a reason, clear a tombstone,
approve/register a peer, synthesize an association, reuse an old pairing
candidate, or silently re-pair.

### Untrusted-Lineage Repair Invariant

For the three repairs that adopt inherited association content, the required
effects are closed:

| Repair kind | Exact source content | Target lineage | Inherited association effect | Success product |
| --- | --- | --- | --- | --- |
| `publish_inactive_parent` | `selected_manifest.parent` | `fresh_random` | `deactivate_all+effective_tombstone_each` | `PAIRING_CLOSED/UNPAIRED_LOCKED` |
| `adopt_copied_current` | `selected_manifest.current` | `fresh_random` | `deactivate_all+effective_tombstone_each` | `PAIRING_CLOSED/UNPAIRED_LOCKED` |
| `recover_unavailable_host_key` | `selected_manifest.current` | `fresh_random` | `deactivate_all+effective_tombstone_each` | `PAIRING_CLOSED/UNPAIRED_LOCKED` |

The inherited association set is every association record in the exact source
generation that is trusted, active, allowlisted, reconnectable, or otherwise
capable of causing present or future `RegisterRemoteSKI`. The coordinator MUST
enumerate that complete set without filtering by current reachability, expiry,
key availability, or peer liveness. If any record cannot be classified or a
tombstone cannot be represented within bounds, validation fails before
publication.

One target generation atomically records a fresh random association-lineage
value, marks every member of that inherited set inactive, and appends one
effective tombstone for each member. It is invalid to publish only the fresh
lineage, only deactivation, or only a subset of tombstones. The command cannot
report success until that complete generation and its exact anchor finalization
are durable. On restart the loader selects only the target generation,
tombstones dominate every inherited association, and zero inherited association
may reload trust, enter an allowlist, reconnect as trusted, or invoke
`RegisterRemoteSKI`.

Before store mutation, the provider durably stages the exact pending anchor
publication descriptor defined above. The coordinator then commits one store
generation and applies the coordinated outcome map, including exact
compare-and-clear for `commit_not_published`. Trust is usable only after both
durability domains are known. Any timeout, mismatch,
`commit_applied_maintenance_failed`, `commit_durability_unknown`, failed pending
clear, or anchor durability ambiguity returns `repair_outcome_unknown`, enters
`QUARANTINED`, keeps mutation disabled, and requires a new exact reconciliation
request after reopen. No automatic retry occurs.

## Backup And Unavailable-Key Recovery

Generic backup is not a trust-preserving operation. A host-bound protected key
cannot be unsealed on another host; a correctly backup-excluded key or anchor
is absent after restore. Both cases fail closed before association reload.
Backup exclusion may be claimed only by a provider-specific attestation and
platform conformance lane; MSP-04A's v1 records gain no portable key or trusted
`backup_excluded` metadata assertion.

When the host key is unavailable, the only recovery is the exact
`recover_unavailable_host_key` repair. It creates a fresh non-exporting local
identity and fresh host anchor and applies the complete untrusted-lineage
invariant to every inherited association from the restored generation.
Wrong-host key material is never exported, rebound, copied, or converted.
Success lands `UNPAIRED_LOCKED`; every peer requires a new explicit OOB flow.
If provider creation, tombstone publication, or either durability boundary is
unavailable, recovery remains `NO_LOCAL_IDENTITY` or `QUARANTINED`.

Legacy MSP-04B state without an enrolled host anchor is not grandfathered into
trusted state. It requires this same untrusted-lineage repair. This deliberately
trades automatic upgrade continuity for a falsifiable no-silent-restore rule.

## Public Surface And Evidence Privacy

The supported public Go API remains byte-for-byte frozen. Public `Runtime`,
`Snapshot`, and `PairingState` gain no restore reason, anchor, tombstone,
attempt, backoff, repair, idempotency, host-key, generation, or mutation field
or method. MSP-04C adds no semantic identity, raw write, MCP tool/resource,
GraphQL field/mutation, Portal action, Home Assistant entity/service, gateway
command, HTTP handler, network listener, or protocol behavior.

Restore and clone fixtures use disposable directories, deterministic fake
providers, random per-run labels, and synthetic ordinal scopes only. They MUST
NOT contain private keys, public-key encodings, certificates, SKIs,
fingerprints, SHIP IDs, stable peer identity, host identifiers, private paths,
or network addresses. Hardware checks remain SSH-only and cannot replace the
deterministic synthetic gate cases.

## G10, G11, And G16 Evidence Contract

| Gate | Deterministic PASS | Deterministic FAIL |
| --- | --- | --- |
| `EEBUS-G10` | Executed startup/runtime integration behavior restores each clone-instance conflict, wrong-host binding, missing host key/anchor, older manifest generation, older control epoch, and durability-unknown fixture through the production composition; observed effects show zero trust registrations and cannot reach `PAIRED_TRUSTED` before or after restart; copied-current and inactive-parent repair publish a fresh lineage with every inherited trusted association inactive and tombstoned. | Any copied/restored/rolled-back case reaches or reloads `PAIRED_TRUSTED`, invokes `RegisterRemoteSKI`, selects a lower manifest, conflates the required reasons, accepts a same-number/different-digest branch, repairs without complete durable deactivation and tombstones, or relies only on a helper-returned decision. |
| `EEBUS-G11` | Executed integration behavior drives the real pairing callback on the SHIP path through the exact vector: counts `0,1,2,3,4`, delays `0s,3s,6s,10s,0s`, the specified durable checkpoint and monotonic restart arm, no early retry, and terminal `ADMIN_HOLD` at the fourth failure; source-constant boundary cases stay within count, retention, exponent, and duration bounds. | The real callback bypasses failure recording or checkpointing, restart clears or reduces state, a wall-clock change shortens delay, a retry occurs before durable `RETRY_READY`, an increment occurs anywhere except failed-attempt linearization, the ceiling admits another handshake/reconnect, arithmetic exceeds a bound, an active record is evicted, or quarantine restores trust. |
| `EEBUS-G16` | Executed integration artifacts contain only repository/branch/commit/issue metadata, tool versions, redacted command names, random per-run/case labels, stable outcome/reason/state enums, bounded counts/durations, and PASS/FAIL. Scans over the actual callbacks, effects, logs, errors, panic text, fixture bytes, and diffs find none of the forbidden categories below. | Any PEM, key, token, full fingerprint, raw/encoded/hashed/truncated SKI or SHIP ID, IP/MAC/serial, local identity, stable peer id/digest, pairing history, private path, or reusable cross-run label appears, the frozen API diff changes, or scan input omits executed production-composition output. |

Only executed integration behavior from the production-composed lifecycle
supplies G10, G11, or G16 evidence. A result is rejected because caller
assertions and helper transcripts are not evidence. The collector derives
registration, reconnect, callback, disconnect, unregister, checkpoint,
restart, and terminal-state fields from observed effects and coordinator state;
a test caller cannot submit those fields as claimed booleans. Helper-only
transcripts may diagnose a failure but cannot produce a PASS row.

The compact public artifact identifies `MSP-04C`, exact commit and commands,
marks topology and credentials `not_applicable_synthetic`, marks temporary
paths `redacted`, and includes one PASS/FAIL row per required case. Raw store,
anchor, admin frames, transcripts, and fixture internals are never published.
Case ordering and output bytes are independent of scheduler, map/directory
order, locale, wall clock, and failure wording.

## MSP-045 Entry Contract

The locked [MSP-045 row][freeze-plan-row] is an interface freeze after the M4
correction, not permission to start downstream platform or consumer work.
MSP-045 must not start until the corrective source merge populates every
applicable source-evidence field above, executed G10, G11, and G16 artifacts
pass, and a bounded architecture closure review returns `PASS` or
`PASS_WITH_CARRIED_EVIDENCE`. Carried evidence is limited to the explicit
SSH-only platform-attestation limitation; it cannot carry a runtime-composition
or gate failure.

| Boundary | MSP-045 decision |
| --- | --- |
| `entry_precondition` | `corrective_source_merged+evidence_bound+architecture_pass` |
| `freeze_scope` | `coordinator_ownership+combined_fsm+read_only_trust_admin_projection` |
| `platform_providers` | `deferred` |
| `consumers` | `deferred` |
| `post_freeze_change` | `explicit_contract_migration` |

MSP-045 may then freeze only coordinator ownership, the combined
MSP-04B/MSP-04C state machines, and the read-only trust/admin projection that
later consumers can use without ad hoc security decisions. A later change to
those frozen semantics requires explicit contract migration. MSP-045 does not
implement or freeze a platform provider. It does not implement a gateway, MCP,
Portal, Home Assistant, or other consumer. Provider backends and their
platform attestations remain separate conformance work; consumer implementation
remains in its downstream milestone and repository.

## Required Tests And Exclusions

Focused code acceptance MUST cover every valid cross-product, precedence row,
and allowed transition; clone versus host mismatch; manifest versus control
rollback; exact pending-descriptor fields and same-number branch conflicts;
`commit_not_published` clear failure and crash; restart; complete inherited-trust
deactivation/tombstones; revocation authentication, exact binding, replay,
conflict, one-writer races, active `DisconnectSKI`, and
`UnregisterRemoteSKI`; startup-before-listener classification; coordinator
authorization of every registration and reconnect; the real pairing callback
on the SHIP path; exact backoff vectors, terminal attempt-limit quarantine,
checkpoint, restart rearm; and every store/anchor outcome. G10/G11 integration
tests exercise production composition rather than helper-only decisions.
Public API and G16 scanners run over successes, failures, callbacks, effects,
fuzz output, golden diffs, and test names. Full race-enabled source CI and docs
CI must pass at exact heads.

MSP-04C does not define a portable key, remote administration, automatic
re-trust, tombstone deletion, trust-preserving backup restore, protocol fact,
consumer behavior, or stable representation. Live hardware is not required
for G10/G11/G16; if an additional smoke run is performed, access remains
SSH-only and its redacted result is supporting evidence only.

[code-issue]: https://github.com/Project-Helianthus/helianthus-eebusreg/issues/28
[corrective-docs-issue]: https://github.com/Project-Helianthus/helianthus-docs-eebus/issues/26
[corrective-source-issue]: https://github.com/Project-Helianthus/helianthus-eebusreg/issues/30
[gate-contract]: https://github.com/Project-Helianthus/helianthus-execution-plans/blob/f5c095935f8a8a67a7873ff349ddaff86eb41994/multi-runtime-semantic-platform.locked/93-eebus-transport-gate-v0.md#case-matrix
[meta-issue]: https://github.com/Project-Helianthus/helianthus-execution-plans/issues/58
[freeze-plan-row]: https://github.com/Project-Helianthus/helianthus-execution-plans/blob/f5c095935f8a8a67a7873ff349ddaff86eb41994/multi-runtime-semantic-platform.locked/92-m0-issue-matrix.yaml#L571-L589
[plan-row]: https://github.com/Project-Helianthus/helianthus-execution-plans/blob/f5c095935f8a8a67a7873ff349ddaff86eb41994/multi-runtime-semantic-platform.locked/92-m0-issue-matrix.yaml#L551-L570
[store-contract]: msp-04a-persistent-store.md
[trust-contract]: msp-04b-first-trust-admin-local.md
