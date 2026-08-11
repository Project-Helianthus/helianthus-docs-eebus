---
canonical_source: "Project-Helianthus/helianthus-docs-eebus:architecture/_candidate/msp-085-live-r2-outdoor-temperature-promotion-evidence.md"
owner_domain: "architecture"
license: "AGPL-3.0-only"
publication_status: "candidate"
claim_status: "evidence-backed"
source_class: "derived_inference"
evidence_ids: "EV-20260811-001"
hypothesis_status: "draft"
falsifier: "A synchronized same-LAN capture cannot preserve the exact eeBUS and B524 source bindings, satisfy the closed comparator, replay deterministically, survive restart, or pass coexistence and public-redaction gates."
stable_navigation: "false"
search: "false"
sitemap: "false"
versioned_bundle: "false"
release_bundle: "false"
---

# Candidate MSP-085-LIVE-R2 Outdoor-Temperature Promotion Evidence

## Status And Scope

This page defines one unreleased V1 read-only evidence profile for the first
real Leaf Promotion Dossier. It correlates the VR940 outdoor-temperature
observation with one exact eBUS B524 register and proposes the candidate leaf
`/system/outdoor_temperature`.

The page is a capture and equivalence contract, not a promotion decision. It
does not create V2, aliases, legacy compatibility, mutation, GraphQL, Portal,
Home Assistant, command routing, or stable semantic-registry exposure. The
feasibility observation in
[`EV-20260811-001`](../../evidence/EV-20260811-001.md) is not synchronized
promotion evidence.

## Ownership Boundary

| Owner | Responsibility in this candidate |
| --- | --- |
| eeBUS runtime | Return the exact owner-authorized raw SPINE observation and its native source time and connection generation. |
| eBUS runtime | Return the exact B524 observation, admitted initiator, target, poll identity, source time, and transport generation available at capture. |
| Gateway | Own the synchronized capture window, capture generation, source timestamps, runtime/connection generations, sample and poll identities, capture-sample validity, comparator execution and evidence, deterministic replay envelope, and Leaf Promotion Dossier assembly. |
| Future protocol-neutral semantic owner | Own semantic leaf identity after promotion, consumer freshness/stale/unavailable policy, source precedence, and conflict policy beyond this evidence comparator. |

The gateway must not turn capture-sample expiry into protocol-neutral semantic
staleness, choose a preferred source for consumers, or publish a canonical
leaf. `helianthus-eebusreg` remains raw runtime/evidence plumbing and does not
own semantic freshness, source precedence, or cross-protocol registry policy.

## Exact Source Identity

The protected owner-local eeBUS binding is:

| Field | Exact value |
| --- | --- |
| Entity | type `TemperatureSensor`, native selector `[6]` |
| Feature | type `Measurement`, role `server`, native selector `11` |
| Description function | `measurementDescriptionListData` |
| Value function | `measurementListData` |
| Measurement identity | `measurementId=0` |
| Descriptor | `scopeType=outsideAirTemperature`, unit `degC` |
| Feasibility sample | `number=13`, `scale=0`, `valueType=value`; this is an observation, not a source-identity constant |
| Declared constraints | step `{number:5,scale:-1}` = `0.5 degC`; minimum `{number:-6,scale:1}` = `-60 degC`; maximum `{number:8,scale:1}` = `80 degC` |

The private capture also binds the exact service, peer, SPINE device address,
runtime epoch, and connection generation. Those values are not written into a
shareable artifact. Public evidence remasks native service/entity/feature/field
selectors per bundle and retains no reverse map.

The exact eBUS peer is B524
`OP=0x02/GG=0x00/II=0x00/RR=0x0073`, target `0x15`, category `STATE`, value
type `f32`, unit `degC`, with controller-local group and instance context. Its
`source_address` is not a constant: every capture must bind the exact admitted
initiator reported by `ebus.v1.runtime.status.get` and corroborated by the bus
observation for that poll. The current feasibility run admitted `0x7F`. A
different source, including a value copied from an older fixture, is an
identity mismatch unless that exact source was admitted for the new capture.

## Closed V1 Profile

This YAML block is the testable candidate profile. Numeric time values are
seconds. `maximum_sample_age_seconds` is capture-evidence validity only; it is
not a semantic freshness or unavailable policy.

```yaml
contract: helianthus.eebus.outdoor-temperature-promotion-evidence.v1
schema_version: 1
candidate_id: MSP-085-LIVE-R2
leaf_path: /system/outdoor_temperature
mode: read_only
capture:
  topology: SAME_LAN
  slot_count: 6
  cadence_seconds: 10
  minimum_valid_pairs: 5
  maximum_missing_slots: 1
  maximum_pairing_skew_seconds: 5
  maximum_sample_age_seconds: 10
  require_single_capture_generation: true
  require_single_eebus_connection_generation: true
  require_single_ebus_poll_generation: true
eebus_source:
  entity_type: TemperatureSensor
  entity_selector: [6]
  feature_type: Measurement
  feature_role: server
  feature_selector: 11
  description_function: measurementDescriptionListData
  value_function: measurementListData
  measurement_id: 0
  scope_type: outsideAirTemperature
  value_type: DECIMAL
  unit: degC
  value_representation:
    number_field: number
    scale_field: scale
    value_type_field: valueType
    decimal_rule: number_times_ten_to_scale
  declared_constraints:
    value_step_size:
      number: 5
      scale: -1
    minimum_value:
      number: -6
      scale: 1
    maximum_value:
      number: 8
      scale: 1
ebus_source:
  family: B524
  opcode: "0x02"
  group: "0x00"
  instance: "0x00"
  register: "0x0073"
  source_address: from_capture
  target_address: "0x15"
  category: STATE
  value_type: f32
  unit: degC
comparator:
  id: NUMERIC_WINDOW_OUTDOOR_TEMPERATURE_V1
  conversion: identity_degC
  decision_rounding: none
  report_rounding: decimal_places_6_half_even
  tolerance_derivation: eebus_declared_value_step_size
  tolerance_absolute_degC: "0.5"
  equivalence_relation: abs_delta_lte_declared_granularity
  metrological_accuracy_claim: false
  conflict_pair_threshold: 1
  match_requires_all_valid_pairs_in_tolerance: true
terminal_precedence:
  - SOURCE_IDENTITY_MISMATCH
  - GENERATION_CHANGED
  - TYPE_MISMATCH
  - UNIT_MISMATCH
  - CAPTURE_SAMPLE_EXPIRED
  - PAIRING_SKEW_EXCEEDED
  - MISSING
  - CONFLICT
  - COEXISTENCE_DRIFT
  - REPLAY_MISMATCH
  - MATCH
mutable_proof: null
```

## Capture And Replay Record

One private capture record must bind all of the following before comparison:

- gateway version and full source commit, profile contract, candidate id,
  `SAME_LAN` scope, authorization scope, and raw mask tier;
- capture id and generation, wall-clock window start/end, monotonic recorder
  offsets, and final capture time;
- runtime epoch plus the admitted eeBUS connection generation;
- each eeBUS sample id, native source timestamp, exact private source binding,
  typed decimal value, unit, and raw evidence reference;
- each eBUS sample id and poll id, poll generation, native source timestamp,
  exact B524 tuple, admitted `source_address`, target, decoded `f32` value, unit,
  and raw evidence reference;
- pairing decision for each slot, absolute source-time skew, sample ages, and
  capture-validity result;
- M8 coexistence bundle id, baseline and enabled-run commitments, no-drift
  result, and anti-leak result;
- comparator profile hash, canonical input commitment, replay tool and version,
  expected normalized output commitment, regenerated output commitment, and
  replay result.

Rows are canonicalized by slot index, then source order `eebus`, `ebus`, then
sample id. Unknown or duplicate slots, identities, samples, or poll ids fail
closed. A source timestamp outside the capture window, a negative age, or a
generation change invalidates the run rather than being normalized away.

Snapshot and evidence references retain their exact runtime, contract,
tool/scope, mask tier, and authorization binding. Dereference under a different
tier or authority is denied; a redacted bundle cannot be upgraded back to the
private source.

## Comparator Decision

Both values are interpreted as exact decimal degrees Celsius only after the
scope, measurement identity, value kind, and unit match. Conversion is
identity. No value or delta is rounded before the decision. The report may
render the absolute delta to six decimal places using round-half-even.

The observed `number=13`, `scale=0` feasibility sample is evidence only and is
not part of source identity or a required future value. The tolerance is not
an arbitrary gateway constant. The comparator derives it
from the SPINE-declared `valueStepSize` captured with the exact source. For this
source, `{number:5,scale:-1}` yields `0.5 degC`; the profile requires that exact
declared granularity and then evaluates `abs(eebus - ebus) <= 0.5 degC`. A
missing or changed step/range invalidates this profile instead of silently
retuning it. This proves only representational equivalence within the declared
granularity. It makes no claim about sensor calibration, physical accuracy,
traceability, or metrological uncertainty.

The fixed run has six ten-second slots. At least five valid pairs are required,
at most one slot may be missing, and paired source timestamps may differ by at
most five seconds. Each sample must be no more than ten seconds old when the
slot is committed. One valid pair outside tolerance reaches the conflict
threshold and terminates as `CONFLICT`; therefore `MATCH` requires every valid
pair to be within tolerance.

The terminal precedence in the profile is deterministic. A lower row cannot
hide a higher-priority failure. `CAPTURE_SAMPLE_EXPIRED` is sometimes called a
stale sample during capture review, but it says nothing about how a promoted
semantic leaf later becomes stale, unavailable, or replaced.

## Leaf Promotion Dossier

The first dossier is complete only when it contains:

1. the exact private source identities above and public bundle-local redacted
   selectors;
2. one complete synchronized window with comparator result `MATCH`;
3. a second complete synchronized `MATCH` window after a full Home Assistant
   add-on restart, with persistent local identity and trust proven and the new
   connection/poll generations recorded rather than forced to equal the first;
4. passing M8 coexistence/no-drift evidence for eBUS baseline, eeBUS-enabled
   operation, stable `ebus.v1` and consumer outputs, and raw eeBUS anti-leak;
5. deterministic replay whose regenerated commitment equals the expected
   commitment;
6. public-redaction validation that exposes neither private selector mapping,
   peer identity, network coordinates, secret material, nor `candidate_ref`;
7. decision, reviewers, code and docs revisions, rollback to zero-promotion,
   and `mutable_proof: null`.

The restart connects two independent capture windows; it does not compare
their temperature values to each other. Each window must independently satisfy
the comparator against contemporaneous eBUS evidence.

## Public Evidence Boundary

The public evidence record may retain the candidate and comparator ids,
normalized selected values admitted by the M6.25 comparison exception, units,
capture/result counts, terminal outcome, eBUS register tuple and observed bus
source/target context, fresh bundle-local selector pseudonyms, and deterministic
commitments. It omits the peer SKI, SHIP ID, SPINE device address, native path
selectors from the runtime artifact, remapping table, private network data,
credentials, private keys, PEM material, trust-store bytes, tokens, and raw
payloads.

No dossier field is copied into `ebus.v1`, GraphQL, Portal, Home Assistant, a
stable semantic registry, or command routing before a separate per-leaf lock
and later consumer gates.

## Falsifiers

The candidate remains unpromoted if any of these conditions occurs:

- the exact SPINE field disappears, changes type or unit, its descriptor no
  longer identifies `outsideAirTemperature` and `measurementId=0`, or the
  captured step/range differs from this exact profile; the observed sample
  itself may change and is not a falsifier;
- the exact B524 identity is unavailable, is decoded under another tuple, or
  the capture does not bind the admitted source address;
- pairing skew, sample-age, missing-count, type, unit, or generation checks
  fail;
- one paired delta exceeds tolerance, producing `CONFLICT`;
- restart persistence, deterministic replay, M8 coexistence/no-drift, or
  anti-leak checks fail; or
- a public artifact exposes a native identity, private address, secret,
  `candidate_ref`, or a consumer-facing semantic value.
