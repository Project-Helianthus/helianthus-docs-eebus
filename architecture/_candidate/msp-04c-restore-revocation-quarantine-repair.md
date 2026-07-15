---
canonical_source: "Project-Helianthus/helianthus-docs-eebus:architecture/_candidate/msp-04c-restore-revocation-quarantine-repair.md"
owner_domain: "architecture"
license: "AGPL-3.0-only"
publication_status: "candidate"
claim_status: "evidence-backed"
source_class: "derived_inference"
evidence_ids: "EV-20260711-001"
hypothesis_status: "draft"
falsifier: "An accepted architecture review or conformance result demonstrates that MSP-04C can silently restore trust, lose a revocation, bypass persistent quarantine, or expose a public mutation or identity surface under this contract."
stable_navigation: "false"
search: "false"
sitemap: "false"
versioned_bundle: "false"
release_bundle: "false"
---

# Candidate MSP-04C Restore, Revocation, Quarantine, And Repair Contract

## Status And Authority

This is the pre-implementation candidate contract for MSP-04C. It constrains
the [companion source issue][code-issue] but does not claim that restore,
revocation, quarantine, or repair is implemented or supported. It follows the
[MSP-04A store contract][store-contract], the [MSP-04B trust contract][trust-contract],
the locked [MSP-04C execution-plan row][plan-row], and exact
[EEBUS-G10/G11/G16 gate definitions][gate-contract]. The active cruise run is
tracked by [meta issue 58][meta-issue].

These are project security and ownership decisions, not protocol claims.
Stable API, navigation, search, sitemap, versioned-bundle, and release-bundle
outputs intentionally omit this candidate.

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
revocation tombstones, quarantine records, bounded repair receipts, and the
state of any coordinated store/anchor publication. Remote references remain
opaque and sensitive. They never become paths, errors, metrics, fixture names,
or public fields.

The host anchor is outside the restorable store set and contains only:

- a provider version and random runtime-local anchor identity;
- the bound random store-instance value;
- high-water manifest generation and control epoch values; and
- at most one exact pending publication descriptor with operation class and
  expected previous/target generations.

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

## Allowed Trust-State Transitions

All events serialize at one coordinator linearization point. Any transition
not listed is forbidden.

| State | Allowed next state |
| --- | --- |
| `NO_LOCAL_IDENTITY` | `UNPAIRED_LOCKED` after durable host-key recovery; `QUARANTINED` on uncertain recovery. |
| `UNPAIRED_LOCKED` | `PAIRING_WINDOW_OPEN` through the MSP-04B admin command; `QUARANTINED` or `CORRUPT_STORE` on later evidence. |
| `PAIRING_WINDOW_OPEN` | `PAIRED_TRUSTED` only after MSP-04B confirmation plus durable store and anchor finalization; otherwise `UNPAIRED_LOCKED`, `REVOKED`, or `QUARANTINED`. |
| `PAIRED_TRUSTED` | `REVOKED` after durable revocation; `QUARANTINED` or `CORRUPT_STORE` on later evidence. |
| `REVOKED` | `PAIRING_WINDOW_OPEN` only for a new explicit OOB flow that cannot reuse the tombstoned association; `QUARANTINED` on uncertainty. |
| `QUARANTINED` | `UNPAIRED_LOCKED` or `REVOKED` after exact durable repair; `CORRUPT_STORE` if repair discovers invalid state. |
| `CORRUPT_STORE` | `UNPAIRED_LOCKED`, `REVOKED`, or `QUARANTINED` only through exact durable repair that publishes a new generation. |

Startup never enters `PAIRED_TRUSTED` from copied, restored, rolled-back,
legacy-anchorless, host-key-unavailable, or durability-unknown state. A repair
result never transitions directly to `PAIRED_TRUSTED`, invokes
`RegisterRemoteSKI`, or opens a pairing window. Re-pairing requires a later
explicit MSP-04B window and exact OOB confirmation.

## Durable Revocation Tombstones

Revocation first closes pairing and denies the target in memory, then proposes
one generation that both deactivates the association and appends an effective
tombstone. A tombstone binds the opaque association reference, revocation
epoch, operation id, and effective generation. Only after store and anchor
finalization are durable may the command report `revoked`.

On startup, a tombstone takes precedence over a durable association and blocks
automatic reload, `RegisterRemoteSKI`, allowlist reuse, reconnect trust, and
candidate admission for that exact association. Restart does not clear it.
`commit_not_published` retains in-process denial but reports unchanged durable
state; `commit_applied_maintenance_failed`, `commit_durability_unknown`, or
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

Retryable bad handshakes use the deterministic rule
`min(base_backoff * 2^min(attempt_count, exponent_cap), max_backoff)` with no
jitter. All constants are nonzero compile-time bounds. Attempt count saturates;
arithmetic overflow fails closed at `max_backoff`. A retry is admitted only
from `RETRY_READY`, and one failed admitted attempt durably returns to
`BACKOFF_ACTIVE` before another attempt is possible.

Wall clock is never used to shorten a deadline. In-process deadlines use a
monotonic clock. The store checkpoints bounded remaining duration; after
restart it conservatively rearms the complete persisted remainder from the new
monotonic origin. Restart or wall-clock change can extend a wait but can never
decrement attempt state, shorten backoff, admit early retry, or restore trust.
The bound applies to stored duration and each armed interval; repeated crashes
may conservatively extend elapsed wall time.

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
`expected_state`, `expected_reason`, selected manifest generation, manifest
epoch, control epoch, anchor version/high-water values, and a bounded
idempotency key and next monotonic repair sequence. Supported kinds are limited
to reconciling one pending publication, publishing an inactive parent as a new
untrusted generation, adopting a copied/current generation as a new untrusted
lineage, recovering an unavailable host key, or releasing one retry
quarantine. A stale or broader binding returns `repair_conflict` with no
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

Before store mutation, the provider durably stages the exact pending anchor
publication. The coordinator then commits one store generation and finalizes
the matching anchor high-water mark. Trust is usable only after both are known
durable. Any timeout, mismatch, `commit_applied_maintenance_failed`,
`commit_durability_unknown`, or anchor durability ambiguity returns
`repair_outcome_unknown`, keeps mutation disabled, and requires a new exact
reconciliation request after reopen. No automatic retry occurs.

## Backup And Unavailable-Key Recovery

Generic backup is not a trust-preserving operation. A host-bound protected key
cannot be unsealed on another host; a correctly backup-excluded key or anchor
is absent after restore. Both cases fail closed before association reload.
Backup exclusion may be claimed only by a provider-specific attestation and
platform conformance lane; MSP-04A's v1 records gain no portable key or trusted
`backup_excluded` metadata assertion.

When the host key is unavailable, the only recovery is the exact
`recover_unavailable_host_key` repair. It creates a fresh non-exporting local
identity and fresh host anchor, publishes a new lineage, and tombstones every
recoverable association from the restored generation. Wrong-host key material
is never exported, rebound, copied, or converted. Success lands
`UNPAIRED_LOCKED`; every peer requires a new explicit OOB flow. If provider
creation, tombstone publication, or either durability boundary is unavailable,
recovery remains `NO_LOCAL_IDENTITY` or `QUARANTINED`.

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
| `EEBUS-G10` | Clone-instance conflict, wrong-host binding, missing host key/anchor, older manifest generation, older control epoch, and durability-unknown fixtures each select their exact reason, perform zero trust registrations, and cannot reach `PAIRED_TRUSTED` before or after restart; exact repair lands untrusted. | Any copied/restored/rolled-back case reaches or reloads `PAIRED_TRUSTED`, invokes `RegisterRemoteSKI`, selects a lower manifest, conflates the required reasons, or repairs without exact durable binding. |
| `EEBUS-G11` | Repeated synthetic bad handshakes produce the exact saturating attempt/backoff sequence, persist reason/state/attempt/remainder across restart, deny early retry after monotonic rearm, and stay within count, retention, exponent, and duration bounds. | Restart clears or reduces state, a wall-clock change shortens delay, a retry occurs before `RETRY_READY`, arithmetic exceeds a bound, an active record is evicted, or quarantine restores trust. |
| `EEBUS-G16` | Shareable case output contains only repository/branch/commit/issue metadata, tool versions, redacted command names, random per-run/case labels, stable outcome/reason/state enums, bounded counts/durations, and PASS/FAIL. Scans find none of the forbidden categories below in values, names, paths, diffs, logs, errors, panic text, or fixture bytes. | Any PEM, key, token, full fingerprint, raw/encoded/hashed/truncated SKI or SHIP ID, IP/MAC/serial, local identity, stable peer id/digest, pairing history, private path, or reusable cross-run label appears, or the frozen API diff changes. |

The compact public artifact identifies `MSP-04C`, exact commit and commands,
marks topology and credentials `not_applicable_synthetic`, marks temporary
paths `redacted`, and includes one PASS/FAIL row per required case. Raw store,
anchor, admin frames, transcripts, and fixture internals are never published.
Case ordering and output bytes are independent of scheduler, map/directory
order, locale, wall clock, and failure wording.

## Required Tests And Exclusions

Focused code acceptance MUST cover every precedence row and allowed transition;
clone versus host mismatch; manifest versus control rollback; missing anchor;
durability uncertainty at every store/anchor boundary; restart; tombstone
dominance and capacity; exact backoff vectors and saturation; wall-clock jumps;
same-UID AF_UNIX framing; repair races, stale scopes, idempotent restart replay,
and all store outcomes. Public API and G16 scanners run over successes,
failures, fuzz output, golden diffs, and test names. Full race-enabled source CI
and docs CI must pass at exact heads.

MSP-04C does not define a portable key, remote administration, automatic
re-trust, tombstone deletion, trust-preserving backup restore, protocol fact,
consumer behavior, or stable representation. Live hardware is not required
for G10/G11/G16; if an additional smoke run is performed, access remains
SSH-only and its redacted result is supporting evidence only.

[code-issue]: https://github.com/Project-Helianthus/helianthus-eebusreg/issues/28
[gate-contract]: https://github.com/Project-Helianthus/helianthus-execution-plans/blob/f5c095935f8a8a67a7873ff349ddaff86eb41994/multi-runtime-semantic-platform.locked/93-eebus-transport-gate-v0.md#case-matrix
[meta-issue]: https://github.com/Project-Helianthus/helianthus-execution-plans/issues/58
[plan-row]: https://github.com/Project-Helianthus/helianthus-execution-plans/blob/f5c095935f8a8a67a7873ff349ddaff86eb41994/multi-runtime-semantic-platform.locked/92-m0-issue-matrix.yaml#L551-L570
[store-contract]: msp-04a-persistent-store.md
[trust-contract]: msp-04b-first-trust-admin-local.md
