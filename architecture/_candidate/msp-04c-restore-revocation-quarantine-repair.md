---
canonical_source: "Project-Helianthus/helianthus-docs-eebus:architecture/_candidate/msp-04c-restore-revocation-quarantine-repair.md"
owner_domain: "architecture"
license: "AGPL-3.0-only"
publication_status: "candidate"
claim_status: "evidence-backed"
source_class: "derived_inference"
evidence_ids: "EV-20260711-001,EV-20260714-001"
hypothesis_status: "draft"
falsifier: "An accepted architecture review or conformance result demonstrates that restore, revocation, quarantine, identity repair, SPINE readiness, or observer shutdown can violate durable denial, local identity continuity, callback provenance, or the private administration boundary."
stable_navigation: "false"
search: "false"
sitemap: "false"
versioned_bundle: "false"
release_bundle: "false"
---

# Candidate MSP-04C Restore, Revocation, Quarantine, And Identity Repair Contract

## Status And Authority

This candidate defines security and ownership behavior for restore,
revocation, quarantine, and host-key or certificate repair. It follows the
[persistent-store contract](msp-04a-persistent-store.md), the
[first-trust contract](msp-04b-first-trust-admin-local.md), and the
[read-only trust projection](msp-045-trust-admin-projection.md), plus the
[canonical local identity contract](../ship-identity.md). It does not claim a
deployed implementation, device behavior, protocol requirement, or support.

The terms below are private conformance vocabulary. They add no exported Go
declaration, public administration protocol, consumer field, or semantic
projection.

## Ownership Boundary

| Owner | Owns | Cannot own |
| --- | --- | --- |
| Protected store | Canonical bytes, the raw 32-byte `StoreInstance`, durable generations, associations, tombstones, and deterministic durability outcomes. | Network state, callback provenance, or repair authorization. |
| Host-key provider | Protected host key and certificate lifecycle plus deterministic repair outcomes. | `StoreInstance`, SHIP ID, remote trust, or observed service/session state. |
| Trust coordinator | Startup classification, revocation, quarantine, repair authorization, and atomic ordering across store and host-key effects. | Protocol semantics or public mutation. |
| SHIP facade | Translation of mDNS, connection, pairing, disconnect, and certificate callbacks into coordinator events. | Policy synthesis, store repair, or observation without a callback. |
| Public read-only surface | Raw redacted runtime observations after their owning callbacks. | Secrets, administration, inferred peers, or semantic promotion. |

## Startup And Restore

Startup validates the selected store generation, exact host binding, host-key
provider state, `StoreInstance`, tombstones, and association classifications
before listener or discovery activation. Any unavailable, ambiguous, copied,
rolled-back, or durability-unknown product enters a closed state and creates no
remote row.

Durable trust and authorization records are policy only. Reload may classify a
later observed peer, but it cannot create service visibility, a session,
topology, or a candidate. A tombstone overrides an association on every
startup. Restart clears the volatile pairing window, candidate, session, and
service observations. Passive discovery and allowlist evaluation alone never
initiate a network attempt. This repair contract does not replace the separate
operator-selected, observation-bound outbound-pairing candidate contract.

## Revocation

Revocation first closes local pairing and denies the exact association in
memory. It then publishes one durable generation that deactivates the
association and appends an effective tombstone. Success is returned only after
the store outcome is durable and the live facade has completed disconnect and
unregister effects or returned an authoritative already-absent result.

An incomplete or ambiguous withdrawal remains denied and reports
`revocation_withdrawal_incomplete`. Restart cannot clear the tombstone,
re-enable the association, create a remote row, or turn incomplete withdrawal
into success. Repair cannot delete, weaken, or bypass an effective tombstone.

## Persistent Quarantine

The coordinator persists one closed reason and state for each quarantined
scope. `ADMIN_HOLD` is required for wrong-host material, copied state,
rollback, corruption, identity disagreement, and durability uncertainty.
Elapsed time and restart cannot leave `ADMIN_HOLD`. A retryable failure may use
bounded deterministic backoff, but authorization for another handshake remains
private coordinator policy and creates no observation.

Any malformed bound, overflow, underflow, missing durability result, or
unclassifiable record fails closed. Capacity exhaustion rejects new work and
does not evict active quarantine evidence or tombstones.

## Host-Key And Certificate Repair

Repair is available only through the existing private AF_UNIX administration
transport after same-effective-UID authentication. There is no TCP, HTTP, CLI,
environment, file-drop, MCP, GraphQL, Portal, Home Assistant, or remote repair
surface. Requests bind the exact current generation, reason, protected-provider
state, operation id, and expected identity values. Stale or incomplete input
returns `repair_conflict` without mutation.

For a real host-key and certificate repair, the protected key and certificate
are replaced and the certificate SKI MUST change. The raw 32-byte
`StoreInstance` MUST remain byte-for-byte unchanged, `nodeToken` MUST remain
exactly unchanged, and the canonical SHIP ID MUST remain exactly unchanged.
The coordinator recomputes the token from the preserved bytes and compares all
three values before publication. Any disagreement returns
`repair_identity_mismatch`, leaves the runtime closed, and publishes no partial
repair.

If the exact `StoreInstance` is unavailable or corrupt, host-key repair cannot
substitute a new store identity. Recovery remains closed and requires a
separately initialized store outside this repair operation. Certificate repair
does not activate, revoke, or create a remote association and does not populate
service, session, topology, or pairing observations.

## Observation And Evidence Boundary

After startup or repair, an mDNS callback may create a visible service, a
connection callback may create a session, and a transport-backed pairing
callback may create a candidate. Earlier policy state cannot stand in for a
later callback. Durable classification may annotate only a row already owned
by current live observation.

Public evidence remains raw and redacted. It records stable outcomes, stage
order, counts, and protected-reference pass/fail only. It contains no private
address, full fingerprint, key, certificate bytes, raw `StoreInstance`, actual
`nodeToken`, actual SHIP ID, administration payload, or durable record. There
is no public mutation and no semantic promotion.

## SHIP/SPINE Readiness And Observer Lifecycle

The
[candidate SHIP/SPINE readiness boundary](../../protocols/_candidate/ship-spine-readiness.md)
separates transport liveness from native graph and use-case evidence. A
SHIP-layer connection callback owns the connected session only. It precedes
SPINE remote device setup and Detailed Discovery, so a current connected session may
transiently have an empty topology. Empty at that stage is not evidence that
the remote has no entities or features.

The runtime refreshes the device, entity, and feature graph only after the
native Detailed Discovery `DeviceChange`/`Add` event, reading the configured
remote from the active service instance. A later native entity add/remove
event may refresh that same live graph. Every refresh is bound to the current
connection generation; an unrelated remote identity, foreign device object,
stale service, or callback from an earlier generation is inert.

Graph refresh preserves each native feature role exactly, including `client`,
`server`, and `special`. It never collapses `special` to an empty or
unspecified role. If a public projection cannot represent a native role, the
raw observation remains distinct and that projection is unavailable pending a
separate versioned API review; no lossy substitute or API promotion occurs in
this contract.

Detailed Discovery does not establish use-case support. The native stack asks
for NodeManagement use-case data afterward. Use-case claims remain absent
until a native data-update event carries real NodeManagement use-case data,
then refresh from the active remote device. The runtime never derives them
from feature presence, device class, local registration, configuration, or a
prior session.

The SPINE observer belongs to exactly one runtime lifecycle. Shutdown first
closes callback admission and unsubscribes that observer, then drains callbacks
already admitted by an in-flight event publication, then shuts down the
service and releases the runtime. A callback after close is inert, and shutdown
cannot return while an admitted callback can still publish. Startup failure
and rollback follow the same unsubscribe-and-drain rule.

These rules are private conformance behavior. They add no `CandidateRef`,
exported dependency type, public API declaration, consumer field, or semantic
promotion.

## Required Falsification Gates

| Gate | Required result |
| --- | --- |
| `restore_closed` | Wrong-host, copied, rolled-back, corrupt, and durability-unknown fixtures create no trust registration or remote observation before or after restart. |
| `revocation_durable` | Tombstone durability precedes successful withdrawal reporting, and restart cannot resurrect the association. |
| `repair_identity_stable` | Real host-key and certificate repair changes certificate SKI while exact `StoreInstance`, `nodeToken`, and canonical SHIP ID remain unchanged. |
| `callback_provenance` | Policy reload creates no row; mDNS, connection, and transport-backed pairing callbacks create only their owning stages. |
| `ship_spine_readiness` | A connected session may remain topology-empty until Detailed Discovery device-add evidence; graph and later use-case events refresh only their native evidence classes, and `special` feature roles remain distinct. |
| `observer_shutdown` | Unsubscribe precedes service shutdown, admitted callbacks drain before return, and stale or post-close callbacks publish nothing. |
| `public_redaction` | Captured output contains no protected identity, private coordinate, secret, or promoted semantic. |

All deterministic tests use synthetic identities and disposable protected
roots. Live validation of the repair gate is pending and must use the redacted
evidence contract.
