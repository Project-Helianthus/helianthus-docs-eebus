---
canonical_source: "Project-Helianthus/helianthus-docs-eebus:development/msp-0625-provenance-policy.md"
owner_domain: "development"
license: "AGPL-3.0-only"
publication_status: "contribution-policy"
claim_status: "evidence-backed"
source_class: "derived_inference"
evidence_ids: "EV-20260711-001,EV-20260726-001"
hypothesis_status: "publishable"
falsifier: "A later canonical ownership or publication policy changes the eeBUS-native owner, public-source threshold, raw operator boundary, or public evidence redaction requirements."
---

# M6.25 Provenance And Publication Policy

## Ownership

This repository is the only canonical owner for the M6.25 eeBUS-native
protocol, architecture, API, provenance, and contract-test gate. The owning
pages are:

- [msp-0625-feature-data-acquisition.md](../protocols/_candidate/msp-0625-feature-data-acquisition.md);
- [msp-0625-raw-feature-command-path.md](../architecture/_candidate/msp-0625-raw-feature-command-path.md);
- candidate API owner `msp-0625-raw-feature-acquisition.md`; and
- this `msp-0625-provenance-policy.md`.

Code repositories may contain concise package comments, generated API
references, and links to these owners. They must not add substantive `docs/`
trees or duplicate this contract. Cross-protocol methodology belongs in the
platform docs repository only through a separate authorized cross-seed.

## Publishable Claim Rule

Every protocol statement must satisfy one of these paths:

1. cite a stable public source directly;
2. cite a redacted, publishable evidence record; or
3. be labeled explicitly as a hypothesis with a concrete falsifier.

The M6.25 protocol page cites immutable public `spine-go` and `eebus-go`
sources for existing feature/function/operation and message-correlation
primitives. Waiter-before-send atomicity, durable mutation behavior, command
routing, authorization order, CAS, rollback, recovery, and quarantine are
Helianthus design hypotheses until implementation tests and bounded live
evidence falsify them.

Operator notes and source steering establish scope and intent only. They do
not establish protocol behavior or live capability.

## Non-Public Source Quarantine

Non-public vendor specifications may be consulted privately to understand
terminology or identify questions. They may not be copied, closely
paraphrased, quoted, cited, linked, named as evidence, fingerprinted, or used
as the sole support for a public claim.

If a proposed claim cannot be independently supported by public source or
publishable redacted evidence, it remains an explicit hypothesis or is omitted.
Public issue text, pull-request text, review comments, commit messages,
fixtures, tests, JSON schemas, and generated bundles follow the same rule as
Markdown.

## Owner-Authorized Raw Data

The owner-authorized local raw surface may show real SHIP/SPINE operational
data needed to perform and audit an exact READ/WRITE:

- remote SKI and SHIP ID;
- device, entity, and feature address;
- feature type, native role, function, and possible operations;
- constraints and changeability;
- typed request, response, before, requested, and observed-after values; and
- bounded unknown fields.

This local visibility is not a publication license. Raw capture files and live
payload values remain private operator material unless a separate redaction
review produces an approved public evidence record.

No tier may expose private keys, PEM private material, credential, bearer,
session, or authentication tokens, cryptographic secrets, or trust-store
bytes. Secret scanning happens before canonical hashing, reference storage,
audit publication, or error rendering. A secret-classified field fails closed
and cannot be replaced by a digest in a public artifact.

Secret scanning recursively visits every typed object, array, and scalar.
Field-name normalization is exactly: Unicode NFKC; insert `_` at each ASCII
lowercase-or-digit to uppercase transition; replace every remaining
run outside `[A-Za-z0-9]` with `_`; lowercase ASCII; collapse repeated
underscores; trim leading and trailing underscores. Reject when the
normalized name, or its underscore-elided form, exactly matches the
corresponding form of a denylisted name. String-value normalization is
Unicode NFKC followed by leading/trailing whitespace removal. Reject a value
containing a case-insensitive PEM private-key boundary or beginning with a
case-insensitive bearer authorization scheme followed by a non-empty
credential. Diagnostics identify only structural positions and
classifications; they never echo the rejected key or value.

The schema applies `propertyNames` and fail-closed `patternProperties` at every
recursive typed-object level and rejects the directly expressible secret
string patterns. The boundary traversal applies the same rule after NFKC and
therefore closes equivalent spellings that JSON Schema regular expressions
cannot generally normalize. Unknown fields that do not classify as secrets
remain bounded, typed, and inspectable on the owner-authorized raw surface.

## Public Evidence Boundary

Public evidence remains explicitly redacted and bound to the authorization
scope, mask tier, tool, runtime, and authorization boundary that created it.
It may contain:

- schema and error classifications;
- aggregate test or live-run results;
- timestamps and bounded counts;
- selected normalized scalar comparison observations admitted by the
  exception below;
- deterministic JCS/SHA-256 commitments; and
- pass/fail statements for identity, rollback, and anti-leak checks.

It must not contain:

- stable local or remote identity;
- SHIP ID or SPINE target address;
- raw typed function-data preimages;
- private network coordinates;
- payload or transport transcripts;
- unselected household state, labels, or schedules; or
- secret material.

Raw references cannot be dereferenced through a public/redacted boundary.
Public references cannot be upgraded to raw. A scope, tier, principal,
runtime-epoch, connection-generation, tool, or boundary mismatch fails closed
before data lookup.

### Public-redacted M6.25 comparison exception

This section defines the public-redacted M6.25 comparison exception.

The rule is that selected normalized values are publishable only inside the closed
`helianthus.eebus.m625.public-redacted-evidence.v1` source contract and its
validated MSP-065 wrapper. This is the public-redacted M6.25 comparison
exception needed for synchronized M7 value/unit comparison. It does not license owner-local raw payloads,
stable identity, native SHIP/SPINE
coordinates, labels, schedules, unknown raw objects, tokens, remapping data,
or secrets.

The closed allowlist contains only `Measurement/measurementListData` and
`Setpoint/setpointListData`, each with a canonical exact decimal value and a
64-character bound; numeric comparison values use canonical exact decimals.
Description, manufacturer, schedule, label, state, and
enum functions are not publishable through this exception. Units use the
bounded machine-token grammar. Successful observations carry explicit quality
and source time. Other terminal classifications carry null value, unit, and
quality.

Service/entity/feature/field selectors, observation references, source ids,
and runtime ids are minted or remasked inside one outer MSP-065 bundle. They
are not retained for reuse: no cross-bundle correlator is permitted. The
recorder's private issuance gate rejects reuse before persistence and its
two-bundle negative test must show fresh public identifiers for the same
owner-local native path.

The source-owned payload does not duplicate outer authority. The MSP-065
envelope remains the sole owner of immutable source binding, effective
authorization, phase and capture timing, per-bundle remasking manifest,
evidence refs, item/byte counts, artifact hash, bundle hash, and regenerated
replay hash. The source owns only normalized evidence; it contains no recorder
offset, summary count, outcome commitment, or parallel hash. A missing or
mismatched outer binding prevents `PRESENT` and therefore prevents M7
consumption.

## Evidence Authority

Contract and fake-peer tests establish shape, ordering, race, recovery, and
negative-path behavior. They do not establish that a live device supports a
function or value.

A bounded local live run may establish that one exact device/function accepted
READ or WRITE under the recorded conditions. It does not establish a device
family rule, semantic meaning, future availability, or consumer support.

An ACK or correlated no-error result establishes protocol acceptance only.
`applied` and `rolled_back` require a full live readback. Public mutation
evidence may report those classifications and commitments after redaction; it
may not publish the before, requested, observed-after, or rollback values used
to prove them. The comparison exception above is read-only and does not
authorize mutation-proof values.

## Milestone Preservation

M6 remains complete and byte-locked by the issue 76 validator. This additive
policy does not reopen M6 or change its nine-tool contract. M6.5 live
acquisition remains partial until M6.25 code and live gates finish. M7 and
later semantic or consumer work remain candidate-only and unauthorized by this
docs gate.

The contract adds no v2, alias, invoke, selector, partial operation,
`filterDelete`, `candidate_ref`, GraphQL, Portal, Home Assistant, semantic
promotion, or code-repository docs tree.
