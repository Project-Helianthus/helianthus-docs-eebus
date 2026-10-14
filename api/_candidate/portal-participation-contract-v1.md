---
canonical_source: "Project-Helianthus/helianthus-docs-eebus:api/_candidate/portal-participation-contract-v1.md"
owner_domain: "api"
license: "AGPL-3.0-only"
publication_status: "candidate"
claim_status: "evidence-backed"
source_class: "derived_inference"
evidence_ids: "EV-20260711-001"
hypothesis_status: "draft"
falsifier: "A reviewed implementation of the participation driver hook, or the merged source at the pinned contract, shows that a rule, field, tag or enum value stated here differs from the exported Go contract, or cannot represent the saved, applied and observed split without conflating them."
stable_navigation: "false"
search: "false"
sitemap: "false"
versioned_bundle: "false"
release_bundle: "false"
candidate_output: "true"
candidate_output_path: "api/_candidate/portal-participation-contract-v1.md"
---

# Candidate Portal-Managed eeBUS Participation Contract v1

## Status and scope

This page publishes the public contract for the Portal-managed eeBUS
participation, trust and device-binding workflow (PORTAL-05, issue
[helianthus-docs-eebus#148](https://github.com/Project-Helianthus/helianthus-docs-eebus/issues/148)).
It is the documentation-gate companion of
[helianthus-eebusreg#137](https://github.com/Project-Helianthus/helianthus-eebusreg/issues/137)
and its pull request
[helianthus-eebusreg#138](https://github.com/Project-Helianthus/helianthus-eebusreg/pull/138).

- Status: **candidate**. It is excluded from stable navigation, search,
  sitemap, versioned bundles and release bundles until the source contract is
  merged and this page is re-pinned to the merge commit (see
  [Compatibility effect](#compatibility-effect)).
- Claim class: a contract published from source. It makes no runtime,
  deployment, interoperability or device claim, and no implementation of the
  driver hook exists in the pinned source.
- Nothing here is an eeBUS, SHIP or SPINE specification statement. Standard
  text is neither copied nor paraphrased; protocol facts remain in
  `protocols/`.

## Evidence basis

| Item | Value |
| --- | --- |
| Source repository | `Project-Helianthus/helianthus-eebusreg` (pull request 138) |
| Pinned commit | head of pull request 138; see the [pinned tree](https://github.com/Project-Helianthus/helianthus-eebusreg/tree/faa883237aedad306da000a495af44a10d7248ce/) (full SHA in the link target and in the source references below) |
| Contract sources (package `eebusruntime`) | `Project-Helianthus/helianthus-eebusreg@faa883237aedad306da000a495af44a10d7248ce:participation_contract_v1.go` and `Project-Helianthus/helianthus-eebusreg@faa883237aedad306da000a495af44a10d7248ce:participation_driver_v1.go` |
| Narrative source | the "Portal Participation Contract (PORTAL-05)" section of `Project-Helianthus/helianthus-eebusreg@faa883237aedad306da000a495af44a10d7248ce:README.md` |
| Derivation | The types, tags, enum values and validator rules below were read from the pinned source. The narrative rules were read from the pinned README. Where both speak, they agree; this page notes where only one of them speaks. |

Evidence class is `derived_inference` from code and README of one commit. No
live device, bus capture or standards document supports any statement here.
`EV-20260711-001` is the existing ownership-contract evidence record and is
cited only for the ownership boundary.

## Ownership

- `helianthus-eebusreg` owns the typed contract, its validators and the
  participation driver hook, and the runtime boundary that implements them. It
  keeps protected participant identity, peer trust, negotiated permissions and
  native evidence.
- The existing semantic producer owns promotion, selection and projection
  assessment. The contract references that producer's selected result and
  defines no universal semantic type.
- The gateway owns Portal composition, HTTP authorization, versioned atomic
  configuration storage, edit conflicts and restart coordination. It consumes
  the contract (PORTAL-03) and must not decode SHIP or SPINE itself.
- This repository (`helianthus-docs-eebus`) owns the public documentation of
  the contract. Cross-protocol platform contracts stay in
  `helianthus-docs-ebus/docs/platform/`.
- Peer trust uses the existing operator admin boundary
  ([candidate operator admin API](post-m9-operator-admin-v1.md)). Portal adds no
  parallel trust store and no Home Assistant session or trust contract. HTTP or
  ingress authentication does not establish native eeBUS trust.

## Export inventory

Contract version constant: `ParticipationContractV1` of type
`ParticipationContractVersionV1`, value `helianthus.eebus.participation.v1`.

Hook interface `ParticipationDriverV1`:

| Method | Purpose |
| --- | --- |
| `Participation(ctx)` | Returns one `ParticipationContributionV1`: saved intent, applied snapshot and observations. |
| `ApplyParticipation(ctx, ParticipationApplyRequestV1)` | Applies a complete candidate configuration; returns `ParticipationApplyResultV1`. |
| `OperatorAdmin()` | Returns the existing admin boundary for discovered, candidate, trusted and connected views, selection, connect or confirm, cancel, retry and untrust. |

Exported validators (pure; they check shape and state prerequisites, not
machine availability): `ParticipationConfigurationV1.Validate`,
`ParticipationContributionV1.Validate`, `ParticipationApplyResultV1.Validate`,
`ValidateParticipationChangeV1` and `ValidateParticipationControlV1`.

## Field, tag and enum manifest

Field tags are the JSON tags in the source. Several types are in-process
contract values; see [Serializer boundary](#serializer-boundary).

`ParticipationConfigurationV1` (saved or applied configuration):

| Field | Tag | Type | Rule |
| --- | --- | --- | --- |
| Contract | `contract` | version string | must equal `helianthus.eebus.participation.v1` |
| Revision | `revision` | uint64 | nonzero |
| LocalParticipant | `local_participant` | reference | 32 lowercase hex characters |
| Enabled | `enabled` | bool | when true, a valid listener is required; a non-empty listener is validated even when false |
| Listener | `listener` | `ParticipationListenerV1` | one listener only |
| DiscoveryEnabled | `discovery_enabled` | bool | a preference; grants neither trust nor control |
| Bindings | `bindings` | list of `ParticipationBindingV1` | at most 256 |

`ParticipationListenerV1`: `interface` (1 to 64 characters of letters, digits
and `_ . : -`, no surrounding whitespace; the wildcard spellings `*`,
the unspecified IPv4 and IPv6 addresses and the empty string are rejected) and
`address` (a valid address and port: nonzero port; not unspecified, multicast,
IPv4-mapped IPv6, IPv4 with a zero first octet, or IPv4 broadcast). The
listener is validated when `enabled` is true or when it is not the zero value.
Whether the interface exists or the address is exposed acceptably
is a driver decision at apply time.

`ParticipationBindingV1`:

| Field | Tag | Rule |
| --- | --- | --- |
| ID | `id` | reference, unique within one configuration |
| PeerParticipant | `peer_participant` | reference, must differ from the local participant |
| LocalCapability | `local_capability` | reference |
| PeerCapability | `peer_capability` | reference |
| Selection | `selection` | reference to the semantic producer's selected result |
| Direction | `direction` | `send` or `receive` |
| Permissions | `permissions` | non-empty, no duplicates, only `observe` and `control` |

All references are owner-allocated opaque 128-bit tokens in the same
32-lowercase-hex encoding. They must not encode or derive from a device
fingerprint, key identifier, serial, address, discovery order or display name.

`ParticipationContributionV1` (validator constraints as enforced by
`ParticipationContributionV1.Validate`):

| Field | Tag | Rule |
| --- | --- | --- |
| Configuration | `configuration` | saved intent; must itself validate |
| AppliedConfiguration | `applied_configuration` | nullable; if non-null it must validate, have the same local participant, and its revision must equal `applied_revision`; if its revision equals the saved revision the two configurations must be equal (order ignored) |
| AppliedRevision | `applied_revision` | at most the saved revision; zero exactly when the snapshot is null |
| ObservedAt | `observed_at` | nonzero time |
| ListenerState | `listener_state` | one of `configured`, `offline`, `active`, `error`; **`incompatible` exists in the enum but is rejected here**; `active` requires an applied snapshot that is enabled |
| Bindings | `bindings` | exactly one observation per ID in the union of saved and applied binding IDs |

`ParticipationBindingObservationV1` (per observation):

| Field | Tag | Rule |
| --- | --- | --- |
| ID | `id` | in the union; no duplicates |
| ConfigurationRevision | `configuration_revision` | the applied revision if the ID is in the applied snapshot, otherwise the saved revision |
| State | `state` | any of the five states, subject to the cross-field rules below |
| PeerOnline | `peer_online` | must be false when the state is `offline`; must be true when `active` |
| Trusted | `trusted` | must be true when `active` |
| Compatibility | `compatibility` | `unknown`, `compatible` or `incompatible`; must be `incompatible` when the state is `incompatible`; must be `compatible` when `active` |
| Admission | `admission` | one of the five values; must be `promoted` when `active` |
| Negotiated | `negotiated` | must be false for a saved-only binding; must be true when `active` |
| Granted | `granted` | at most two, no duplicates, only `observe` and `control`; empty for a saved-only binding; each grant must be among the permissions of the binding as applied (saved binding if saved-only); non-empty when `active` |
| ControlOutcome | `control_outcome` | one of the four values; `rejected` and `outcome_unknown` require a failure |
| Failure | `failure` | one of the six values; not `none` exactly when the state is `error` |
| Provenance | `provenance` | see below |
| Losses | `losses` | at most 256 records; null means unassessed |

An `active` observation additionally requires: an applied snapshot that is
enabled, an active listener state, a native evidence envelope with a non-empty
data hash, both version labels present, non-null losses and no `unknown` loss.
A saved-only observation cannot be `active`.

`ParticipationProvenanceV1`: `native` (nullable redacted evidence envelope from
the evidence package; if present it must validate and hold at most 256
objects), `transport_version` and `data_model_version` (nullable, null means
unknown; if present: 1 to 64 characters, starting with a letter or digit, then
letters, digits and `. _ -`).

`ParticipationLossV1`: `native_path` (at most 256 characters; one or more
segments each starting with `/` and made of letters, digits, `_` and `-`),
`code` (`omitted`, `transformed` or `unknown`; `unknown` blocks `active`) and
`control_safe` (bool; any false value blocks control eligibility).

`ParticipationApplyResultV1` (validator constraints):

| Field | Tag | Rule |
| --- | --- | --- |
| StateRevision | `state_revision` | nonzero |
| AppliedRevision | `applied_revision` | nonzero when `state` is `active`; otherwise unconstrained, and an `error` result may retain the previous value |
| State | `state` | any of the five states; unlike the listener state, `incompatible` is accepted here |
| Failure | `failure` | one of the six values; not `none` exactly when `state` is `error` |

`ParticipationApplyRequestV1` embeds the existing mutation
precondition (expected native state revision and idempotency key) and carries
a complete candidate `Configuration`.

Enumerations (closed sets):

| Type | Values |
| --- | --- |
| Direction | `send`, `receive` |
| Permission | `observe`, `control` |
| State | `configured`, `offline`, `incompatible`, `active`, `error` |
| Failure | `none`, `authorization`, `negotiation`, `listener`, `persistence`, `recovery` |
| Control outcome | `not_requested`, `rejected`, `accepted`, `outcome_unknown` |
| Loss code | `omitted`, `transformed`, `unknown` |
| Compatibility | `unknown`, `compatible`, `incompatible` |
| Admission | `unknown`, `candidate`, `qualified`, `promoted`, `unsupported` |

## Saved, applied and observed state

The contract keeps three facts separate. A consumer must never display one as
another.

1. **Saved intent.** `Configuration` with its monotonically increasing
   `Revision`. It is what the operator asked for, stored by the gateway.
2. **Applied configuration.** `AppliedConfiguration`, an independent snapshot
   with its own `Revision`, equal to `AppliedRevision`. A null snapshot
   requires `AppliedRevision` zero and means nothing has been applied. The
   applied revision may never exceed the saved revision. If both revisions are
   equal the two configurations must be equal, with binding and permission
   order ignored.
3. **Observed state.** One `ParticipationBindingObservationV1` per binding.
   Each carries `ConfigurationRevision`, the revision whose binding the
   observation describes: the applied revision whenever that binding ID is
   still applied, otherwise the saved revision for a saved-only binding.

Rules:

- **Union preserved.** The observation list must contain exactly one entry for
  every binding ID in the union of saved and applied bindings, including
  unavailable peers and bindings removed from saved intent but still operating.
  Each configuration holds at most 256 bindings, so the union is at most 512
  observations. A removal that is saved but not yet applied cannot hide a
  still-operating binding.
- **Saved-only bindings are inert.** An observation of a binding that is not
  applied cannot report a grant, native negotiation or the `active` state.
- **Grants validated against applied permissions.** Every native grant must be
  a subset of the permissions of the binding as applied (or, for saved-only
  bindings, none). A still-held control grant while a revocation is pending is
  reportable; it does not restore control eligibility (see below).
- **Active requires established operation.** `active` needs an enabled applied
  configuration, an active listener, an online and trusted peer, compatible
  capabilities, promoted admission, established negotiation, at least one
  grant, a hashed native evidence envelope, both native version labels, an
  explicit (non-null) loss assessment and no `unknown` loss. Unknown or false
  trust, availability or negotiation never yields `active`.
- **Failure and state agree.** A failure other than `none` is exactly an
  `error` state. A rejected or `outcome_unknown` control outcome requires an
  error. `offline` contradicts an online peer; `incompatible` requires negative
  compatibility.
- **Loss assessment.** A non-null `losses` list is the producer's explicit
  projection assessment: empty means assessed with no reported loss, null means
  unassessed. `control_safe` must come from the owning qualification, never from
  a Portal setting. At most 256 evidence objects and 256 loss records per
  observation.
- **Native evidence retained.** Provenance keeps the redacted evidence envelope
  and the observed transport and data-model version labels. Version labels,
  references and fixture values are not normative specification evidence and
  not device compatibility evidence.

### Control eligibility

`ValidateParticipationControlV1` is a pure eligibility check. It is not
authorization and not dispatch. Control is eligible for a binding only when all
of these hold:

1. the whole contribution validates;
2. the saved intent is enabled;
3. the same binding ID is still present in the saved intent (still selected)
   with the same target as the operating binding;
4. the saved binding carries the `control` permission;
5. the observation is `active` and holds a native `control` grant; and
6. no loss on that observation has `control_safe` false.

Saved removal, revocation or disable therefore rejects control even while the
older applied binding is truthfully observed as active. Control is never
inferred from observation permission, a functional mapping or peer trust.
The native control owner must additionally require authenticated operator
authority, action-time confirmation of the exact target, direction and
operation, current promotion and compatibility, a fresh observation and its own
mutation preconditions. No generic control endpoint or command is defined here.
An accepted control outcome means peer acceptance only, not verified effect.

### Direction and receive-direction control

`send` means the local capability is offered to the selected peer capability.
`receive` means the reverse.

For the `control` permission:

- On a `send` binding, the local participant may control the selected peer
  capability.
- On a **`receive` binding, the selected peer controls the bound local
  capability.** A receive grant does not authorize Portal to issue control to
  that peer.

The native owner checks the actual actor and feature roles and target policy
in either direction. Incoming peer control is subject to the same explicit
target policy.

## Apply lifecycle

1. The gateway validates the candidate and checks its own saved-revision
   conflict first. `ValidateParticipationChangeV1` requires the next revision to
   be exactly the previous revision plus one, the same local participant, and
   that an existing binding ID keeps the same peer, capabilities, selection and
   direction. Changing any of those needs a new binding ID. Permissions may
   change under the same ID.
2. The operator reviews the exact configuration delta before sensitive changes
   are applied.
3. `ApplyParticipation` receives the complete candidate configuration plus the
   native expected state revision and an idempotency key. The driver checks the
   native state precondition and the immutable binding targets.
4. Calls carry a context deadline of at most 30 seconds. At most one apply is in
   flight. Retries reuse the key and the identical payload. At most three
   context-bounded attempts are made per operator request; then an error is
   surfaced and an explicit retry is required. Error text is a fixed safe
   category, never a native payload.
5. The gateway saves atomically only after validation, retains the previous
   valid configuration if saving fails, and displays a saved but unapplied
   revision after an apply failure.
6. Native persistence and generic configuration persistence are not one
   transaction. An interrupted or timed-out application is reconciled by fresh
   inspection before any retry. Returning from a call is not evidence that a
   device operated.

The deadline, attempt and single-flight limits are documented as hook
obligations. The pinned validators do not enforce them (see
[Unresolved questions](#unresolved-questions)).

### `ParticipationApplyResultV1` outcomes

The validator requires: a nonzero `state_revision`; known `state` and `failure`
categories; `failure` other than `none` exactly when `state` is `error`; and a
nonzero `applied_revision` when `state` is `active`.

- A successful active result names the applied revision it brought into effect.
- An `error` result may retain the previous `applied_revision`. The failed
  attempt and the older runtime's still-active observations are two separate
  facts.
- A result used for display must pass validation. A boundary error that yields
  no valid result requires fresh inspection.
- A result is not an observation and does not by itself establish that any
  binding is operating.

### Disable, removal, untrust, restart and recovery

- **Disable** stops discovery, listening and new negotiation or control,
  cancels outstanding work and closes native sessions within the apply
  deadline. It retains protected local identity, trusted peers, binding IDs and
  preferences. Disable failure is an explicit error and never reports a stopped
  listener without observation. Disabling discovery alone does not untrust
  peers. Re-enabling constructs a fresh runtime over the retained native state.
- **Removal** of a binding revokes its functional permission and cancels its
  in-flight work before removal is reported applied. It does not untrust the
  peer or reset local identity.
- **Untrust** is the separate, confirmed admin action. It invalidates grants
  and suspends all affected bindings without deleting their saved records.
- **Replacing** a target, direction or selection requires a new binding ID and
  an explicit reviewed delta.
- **Identity reset** is a separate authorized operation outside ordinary
  participation configuration. It cannot be a side effect of disabling or of
  deleting the last binding. `ValidateParticipationChangeV1` rejects a changed
  local participant in an ordinary change. What a reset leaves behind is not
  specified (see [Unresolved questions](#unresolved-questions)).
- **Restart or reconnect** reloads the saved bindings and the owner's durable
  reference and trust resolution before negotiation. Target identity and
  selection are preserved; availability, admission, compatibility and grants
  are recomputed from fresh evidence. No earlier `active` flag or grant is
  restored as operating authority.
- An unavailable or changed peer stays `offline` or `incompatible`. Neither name
  matching nor discovery reassigns a binding to another device.
- Fresh inspection after a failed or timed-out apply retains the last applied
  snapshot and still-held grants. They do not become permission under the latest
  saved intent. No background recovery restores control eligibility after a
  saved revocation, removal or disable.

## Two reviewer-flagged semantics

### Binding-ID reuse after removal

Statement of the contract:

- **Reuse of a removed binding ID for a different target is invalid for the
  owner.** The owner reserves deleted binding IDs against reuse (a tombstone
  obligation stated in the source README). A new target needs a new ID.
- If such reuse nevertheless reaches a contribution while an older revision that
  still contains the old target is the applied revision, the contribution
  validator rejects the **whole** contribution (saved and applied binding
  identities differ). Every consumer of that contribution, including the
  control-eligibility check for unrelated bindings, therefore **fails closed**
  until the applied revision no longer contains the old target.
- The change validator `ValidateParticipationChangeV1` compares only adjacent
  revisions. It cannot detect reuse across a removal, because the removed
  binding is absent from the previous revision. Enforcement of non-reuse
  across revisions rests on the owner's reservation, not on that validator.
  This is a documented gap, not an intended permission.

### Applied snapshot older than the saved revision

Working interpretation (to be confirmed, see
[Unresolved questions](#unresolved-questions)):

- An applied snapshot older than the saved revision means the saved revision
  has **not been applied**: the application is pending, failed or timed out. The
  snapshot is the last revision the driver reports as applied, and the
  observations describe that revision's operation.
- v1 has **no representation of a partially applied revision**. A revision is
  either reported as applied (`applied_revision` equals it and the snapshot
  equals the saved configuration) or it is not. After an apply that was
  interrupted, the contract requires fresh inspection and explicit retry; it
  does not allow a driver to express "some bindings of revision N are in
  effect" by moving `applied_revision` or by mixing fields.
- Not covered by the validators: for an applied revision older than the saved
  one, the content is checked only for internal validity, identity of the local
  participant, and consistency of shared binding IDs with the saved targets. It
  is not tied to any content that was previously saved at that revision number.

## Serializer boundary

`ParticipationApplyRequestV1` is an **in-process contract**. It embeds the
existing mutation precondition, which intentionally inherits the admin
serializer that refuses JSON output. The request therefore defines **no wire
shape and no persistence format**. The JSON tags on the other contract types
document field names for the typed contract; they do not by themselves define a
public HTTP, MCP or storage schema. Gateway-owned saved configuration and any
transport of these values are defined and reviewed by their own owners.

## Compatibility effect

- Adds a new exported contract to package `eebusruntime` and changes the
  characterization fingerprint of the exact API surface. The source states that
  historical API hashes are unchanged.
- No runtime adapter, user interface, persistence backend, binding executor or
  dependency change is included, and no existing constructor implements the
  driver hook.
- This page is a candidate pin to a pull-request head. After the source pull
  request merges, a follow-up must re-pin the evidence to the merge commit and
  decide promotion of this page; until then it remains excluded from stable
  publication channels. A stable API reference under `api/eebusruntime-v1/`
  is unchanged.
- The gateway Portal integration (PORTAL-03) may bind to this contract only
  after the source merges.

## Unresolved questions

1. **Meaning of an older applied snapshot.** Is "not yet applied, with no
   partial state" the intended meaning, or must v1 report partial application
   (for example after a timeout)? The source states the older snapshot is
   allowed "during pending or failed application" and does not define partial
   application.
2. **Content binding of older revisions.** Should an older applied snapshot be
   tied to the content that was saved at that revision (for example by a
   digest)? Today only revision number, local participant and shared-ID target
   consistency are checked.
3. **Scope of fail-closed on ID reuse.** Should a conflicting reused ID fail
   only its own binding rather than the whole contribution? v1 fails the whole
   contribution.
4. **Cross-revision reuse detection.** Whether a validator, rather than only
   the owner's tombstone reservation, must detect reuse across a removal.
5. **Narrowing changes.** A change that narrows permissions leaves the older
   applied binding observed as active, and its grant truthfully held, until the
   change is applied. Control eligibility is already denied by the saved
   intent; whether the older listener needs a further explicit marker is open.
6. **Obligations not enforced by validators.** The deadline, single-flight and
   three-attempt limits, listener availability checks, tombstones, atomic
   storage, cancellation, cross-owner reconciliation and physical effects are
   implementation and integration gates. No test or fixture here establishes
   them.
7. **Consequence of an identity reset.** The pinned source and README do not
   state what a reset does to the contribution. A review discussion
   hypothesized that no valid contribution remains until a new configuration
   exists; that is an unverified hypothesis, not a contract rule.
8. **Negative-test depth.** The round-2 review observed that some negative
   tests assert only that an error occurred, not which one.

## Falsifiers

- A merged source whose exported types, tags, enum sets, limits or validator
  rules differ from the manifest above.
- An implementation showing that the saved, applied and observed split cannot
  carry a real apply, timeout or restart without conflating two of the three.
- A reviewed behavior in which a saved-only or revoked binding becomes
  control-eligible, or in which a binding is silently reassigned to another
  peer.
- A reviewed behavior in which an older applied snapshot is the intended way to
  report a partial apply, which would falsify the working interpretation above.

## Related pages

- [Candidate operator admin API v1](post-m9-operator-admin-v1.md)
- [Runtime reference (candidate)](runtime-reference.md)
- [Multi-runtime coexistence](../../architecture/multi-runtime-coexistence.md)
- [Supported eeBUS architecture](../../architecture/README.md)
