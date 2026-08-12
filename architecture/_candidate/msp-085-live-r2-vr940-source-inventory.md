---
canonical_source: "Project-Helianthus/helianthus-docs-eebus:architecture/_candidate/msp-085-live-r2-vr940-source-inventory.md"
owner_domain: "architecture"
license: "AGPL-3.0-only"
publication_status: "candidate"
claim_status: "evidence-backed"
source_class: "observed_runtime"
evidence_ids: "EV-20260811-002"
hypothesis_status: "draft"
falsifier: "A repeated owner-authorized raw read changes a candidate's descriptor, field identity, declared constraint, operation-mode relation, or overrun relation."
stable_navigation: "false"
search: "false"
sitemap: "false"
versioned_bundle: "false"
release_bundle: "false"
---

# Candidate VR940f M7 Source Inventory V1

## Scope

This page owns the eeBUS protocol identity used to assess the 18 real VR940f
semantic candidates. It also preserves four earlier terminal records as retired
non-leaves; their ids and fact hashes remain immutable provenance. It does not
decide semantic promotion. The gateway must bind each
native selector from private operator evidence and compare the observed source
with this closed inventory. A private campaign may not substitute a descriptor,
field, unit, declared step, enum map, or boolean relation.

The inventory creates no V2, alias, compatibility surface, mutation, GraphQL,
Portal, Home Assistant entity, command route, semantic freshness policy, or
source precedence. A positive result remains `LOCKED_NOT_EXPOSED` until a later
consumer milestone.

## Native Selector Boundary

Every `selector_binding: exact_from_private_capture` binds the peer, service,
SPINE device address, entity address, feature address, runtime epoch, and
connection generation in owner-local evidence. Those native values are not
portable VR940f constants and are excluded from this shareable page. Entity
slots distinguish separately captured sources without publishing their native
addresses.

## Closed Inventory

The following YAML document is the canonical protocol-owned inventory. Decimal
values use `number * 10^scale`. A numeric comparator must require the exact
descriptor and then either the exact unit or one separately bound affine unit
conversion. Its inclusive limit is the declared step in this inventory, not a
step supplied by a campaign.

```yaml
contract: helianthus.eebus.vr940f-m7-source-inventory.v1
schema_version: 1
target_model: VR940f
selector_binding: exact_from_private_capture
decimal_rule: number_times_ten_to_scale
default_validation_mode: CROSS_PROTOCOL_EQUIVALENCE
terminal_candidates:
  - candidate_id: m7-candidate-0001
    fact_hash: sha256:867157d98ac046e6bc09ae60b4a963e5f7c6d174f12d293b09cc339c7f9dd9a2
    required_disposition: WITHHELD
    required_terminal_state: CLOUD_ONLY
    retirement_state: RETIRED_TERMINAL_NOT_A_LEAF
    protocol_binding: null
  - candidate_id: m7-candidate-0002
    fact_hash: sha256:26df8fd76d3d2804c899a063766075a9cad25ad90cccfcde067c10b95cb793be
    required_disposition: WITHHELD
    required_terminal_state: NOT_TESTED
    retirement_state: RETIRED_TERMINAL_NOT_A_LEAF
    protocol_binding: null
  - candidate_id: m7-candidate-0003
    fact_hash: sha256:4f64a3fb317dee55c8838b2f5406976e3ba6e24f1c977cb141a0e1c1ed300911
    required_disposition: WITHHELD
    required_terminal_state: NOT_TESTED
    retirement_state: RETIRED_TERMINAL_NOT_A_LEAF
    protocol_binding: null
  - candidate_id: m7-candidate-0004
    fact_hash: sha256:aae4e6db120c3ac922e9c981fd80041388c2e17cb099eadcddb34e61008e3490
    required_disposition: WITHHELD
    required_terminal_state: NOT_TESTED
    retirement_state: RETIRED_TERMINAL_NOT_A_LEAF
    protocol_binding: null
sources:
  - candidate_id: m7-candidate-0005
    semantic_path: /dhw/temperature_c
    entity_slot: dhw_circuit
    entity_type: DHWCircuit
    feature_type: Measurement
    feature_role: server
    description_function: measurementDescriptionListData
    constraints_function: measurementConstraintsListData
    value_function: measurementListData
    field_path: measurementData[measurementId=0].value
    descriptor:
      measurement_id: 0
      commodity_type: domesticHotWater
      measurement_type: temperature
      scope_type: dhwTemperature
      unit: degC
    unit: degC
    declared_constraints:
      minimum: {number: 0, scale: -6}
      maximum: {number: 99, scale: 0}
      step: {number: 1, scale: 0}
    comparator_class: NUMERIC_DECLARED_GRANULARITY
    protocol_eligibility: ELIGIBLE
  - candidate_id: m7-candidate-0006
    semantic_path: /dhw/target_temperature_c
    ebus_fallback:
      family: B555
      operation: TIMER_READ
      target_pseudonym_rule: active_controller_target_hash
      device_family: BASV2
      schedule_program: DHW
      slot_index: 0
      day_of_week: MONDAY
      time_identity: "00:00:00"
      operation_mode_context: temp_slots_1_shared_setpoint
      unit_scale_source: B555_DHW_TEMPERATURE_RAW_DIV10_C
      field_path: timerSlot.temperature
      unit: degC
      coupling_rule: dhw_temp_slots_1_mirrors_b524_setpoint
    entity_slot: dhw_circuit
    entity_type: DHWCircuit
    feature_type: Setpoint
    feature_role: server
    description_function: setpointDescriptionListData
    constraints_function: setpointConstraintsListData
    value_function: setpointListData
    field_path: setpointData[setpointId=1].value
    descriptor:
      measurement_id: 0
      setpoint_id: 1
      setpoint_type: valueAbsolute
      scope_type: dhwTemperature
      unit: degC
    unit: degC
    declared_constraints:
      minimum: {number: 35, scale: 0}
      maximum: {number: 7, scale: 1}
      step: {number: 1, scale: 0}
    comparator_class: NUMERIC_DECLARED_GRANULARITY
    protocol_eligibility: ELIGIBLE
  - candidate_id: m7-candidate-0007
    semantic_path: /dhw/operating_mode
    entity_slot: dhw_circuit
    entity_type: DHWCircuit
    feature_type: HVAC
    feature_role: server
    description_functions:
      - hvacSystemFunctionDescriptionListData
      - hvacOperationModeDescriptionListData
      - hvacSystemFunctionOperationModeRelationListData
    value_function: hvacSystemFunctionListData
    field_path: hvacSystemFunctionData[systemFunctionId=0].currentOperationModeId
    descriptor:
      system_function_id: 0
      system_function_type: dhw
    unit: null
    exact_mapping:
      0: auto
      1: "on"
      2: "off"
    comparator_class: ENUM_EXACT_MAPPING
    protocol_eligibility: ELIGIBLE
  - candidate_id: m7-candidate-0008
    semantic_path: /dhw/operation_mode_changeable
    validation_mode: EEBUS_NATIVE_CAPABILITY
    entity_slot: dhw_circuit
    entity_type: DHWCircuit
    feature_type: HVAC
    feature_role: server
    description_function: hvacSystemFunctionDescriptionListData
    value_function: hvacSystemFunctionListData
    field_path: hvacSystemFunctionData[systemFunctionId=0].isOperationModeIdChangeable
    descriptor:
      system_function_id: 0
      system_function_type: dhw
    unit: null
    exact_mapping: {false: false, true: true}
    comparator_class: BOOLEAN_EXACT_MAPPING
    protocol_eligibility: EEBUS_NATIVE
  - candidate_id: m7-candidate-0009
    semantic_path: /dhw/overrun_active
    entity_slot: dhw_circuit
    entity_type: DHWCircuit
    feature_type: HVAC
    feature_role: server
    description_functions:
      - hvacSystemFunctionDescriptionListData
      - hvacOverrunDescriptionListData
    value_functions:
      - hvacSystemFunctionListData
      - hvacOverrunListData
    field_path: hvacSystemFunctionData[systemFunctionId=0].isOverrunActive
    descriptor:
      system_function_id: 0
      system_function_type: dhw
      overrun_id: 0
      overrun_type: oneTimeDhw
      affected_system_function_ids: [0]
    unit: null
    exact_mapping:
      false: false
      true: true
    comparator_class: BOOLEAN_EXACT_MAPPING
    protocol_eligibility: ELIGIBLE
  - candidate_id: m7-candidate-0010
    semantic_path: /zones/zone_1/room_temperature_c
    entity_slot: zone_1_room
    entity_type: HVACRoom
    feature_type: Measurement
    feature_role: server
    description_function: measurementDescriptionListData
    constraints_function: measurementConstraintsListData
    value_function: measurementListData
    field_path: measurementData[measurementId=0].value
    descriptor:
      measurement_id: 0
      commodity_type: air
      measurement_type: temperature
      scope_type: roomAirTemperature
      unit: degC
    unit: degC
    declared_constraints:
      minimum: {number: 0, scale: -6}
      maximum: {number: 6, scale: 1}
      step: {number: 5, scale: -1}
    comparator_class: NUMERIC_DECLARED_GRANULARITY
    protocol_eligibility: ELIGIBLE
  - candidate_id: m7-candidate-0011
    semantic_path: /zones/zone_1/target_temperature_c
    entity_slot: zone_1_room
    entity_type: HVACRoom
    feature_type: Setpoint
    feature_role: server
    description_function: setpointDescriptionListData
    constraints_function: setpointConstraintsListData
    value_function: setpointListData
    field_path: setpointData[setpointId=1].value
    descriptor:
      measurement_id: 0
      setpoint_id: 1
      setpoint_type: valueAbsolute
      scope_type: roomAirTemperature
      unit: degC
    unit: degC
    declared_constraints:
      minimum: {number: 5, scale: 0}
      maximum: {number: 3, scale: 1}
      step: {number: 5, scale: -1}
    comparator_class: NUMERIC_DECLARED_GRANULARITY
    protocol_eligibility: ELIGIBLE
  - candidate_id: m7-candidate-0012
    semantic_path: /zones/zone_1/operating_mode
    entity_slot: zone_1_room
    entity_type: HVACRoom
    feature_type: HVAC
    feature_role: server
    description_functions:
      - hvacSystemFunctionDescriptionListData
      - hvacOperationModeDescriptionListData
      - hvacSystemFunctionOperationModeRelationListData
    value_function: hvacSystemFunctionListData
    field_path: hvacSystemFunctionData[systemFunctionId=0].currentOperationModeId
    descriptor:
      system_function_id: 0
      system_function_type: heating
    unit: null
    exact_mapping: {0: auto, 1: "on", 2: "off"}
    comparator_class: ENUM_EXACT_MAPPING
    protocol_eligibility: ELIGIBLE
  - candidate_id: m7-candidate-0013
    semantic_path: /zones/zone_1/operation_mode_changeable
    validation_mode: EEBUS_NATIVE_CAPABILITY
    entity_slot: zone_1_room
    entity_type: HVACRoom
    feature_type: HVAC
    feature_role: server
    description_function: hvacSystemFunctionDescriptionListData
    value_function: hvacSystemFunctionListData
    field_path: hvacSystemFunctionData[systemFunctionId=0].isOperationModeIdChangeable
    descriptor:
      system_function_id: 0
      system_function_type: heating
    unit: null
    exact_mapping: {false: false, true: true}
    comparator_class: BOOLEAN_EXACT_MAPPING
    protocol_eligibility: EEBUS_NATIVE
  - candidate_id: m7-candidate-0014
    semantic_path: /zones/zone_2/room_temperature_c
    entity_slot: zone_2_room
    entity_type: HVACRoom
    feature_type: Measurement
    feature_role: server
    description_function: measurementDescriptionListData
    constraints_function: measurementConstraintsListData
    value_function: measurementListData
    field_path: measurementData[measurementId=0].value
    descriptor:
      measurement_id: 0
      commodity_type: air
      measurement_type: temperature
      scope_type: roomAirTemperature
      unit: degC
    unit: degC
    declared_constraints:
      minimum: {number: 0, scale: -6}
      maximum: {number: 6, scale: 1}
      step: {number: 5, scale: -1}
    comparator_class: NUMERIC_DECLARED_GRANULARITY
    protocol_eligibility: ELIGIBLE
  - candidate_id: m7-candidate-0015
    semantic_path: /zones/zone_2/target_temperature_c
    entity_slot: zone_2_room
    entity_type: HVACRoom
    feature_type: Setpoint
    feature_role: server
    description_function: setpointDescriptionListData
    constraints_function: setpointConstraintsListData
    value_function: setpointListData
    field_path: setpointData[setpointId=1].value
    descriptor:
      measurement_id: 0
      setpoint_id: 1
      setpoint_type: valueAbsolute
      scope_type: roomAirTemperature
      unit: degC
    unit: degC
    declared_constraints:
      minimum: {number: 5, scale: 0}
      maximum: {number: 3, scale: 1}
      step: {number: 5, scale: -1}
    comparator_class: NUMERIC_DECLARED_GRANULARITY
    protocol_eligibility: ELIGIBLE
  - candidate_id: m7-candidate-0016
    semantic_path: /zones/zone_2/operating_mode
    entity_slot: zone_2_room
    entity_type: HVACRoom
    feature_type: HVAC
    feature_role: server
    description_functions:
      - hvacSystemFunctionDescriptionListData
      - hvacOperationModeDescriptionListData
      - hvacSystemFunctionOperationModeRelationListData
    value_function: hvacSystemFunctionListData
    field_path: hvacSystemFunctionData[systemFunctionId=0].currentOperationModeId
    descriptor:
      system_function_id: 0
      system_function_type: heating
    unit: null
    exact_mapping: {0: auto, 1: "on", 2: "off"}
    comparator_class: ENUM_EXACT_MAPPING
    protocol_eligibility: ELIGIBLE
  - candidate_id: m7-candidate-0017
    semantic_path: /zones/zone_2/operation_mode_changeable
    validation_mode: EEBUS_NATIVE_CAPABILITY
    entity_slot: zone_2_room
    entity_type: HVACRoom
    feature_type: HVAC
    feature_role: server
    description_function: hvacSystemFunctionDescriptionListData
    value_function: hvacSystemFunctionListData
    field_path: hvacSystemFunctionData[systemFunctionId=0].isOperationModeIdChangeable
    descriptor:
      system_function_id: 0
      system_function_type: heating
    unit: null
    exact_mapping: {false: false, true: true}
    comparator_class: BOOLEAN_EXACT_MAPPING
    protocol_eligibility: EEBUS_NATIVE
  - candidate_id: m7-candidate-0018
    semantic_path: /system/outside_air_temperature_c
    entity_slot: outside_sensor
    entity_type: TemperatureSensor
    feature_type: Measurement
    feature_role: server
    description_function: measurementDescriptionListData
    constraints_function: measurementConstraintsListData
    value_function: measurementListData
    field_path: measurementData[measurementId=0].value
    descriptor:
      measurement_id: 0
      commodity_type: air
      measurement_type: temperature
      scope_type: outsideAirTemperature
      unit: degC
    unit: degC
    declared_constraints:
      minimum: {number: -6, scale: 1}
      maximum: {number: 8, scale: 1}
      step: {number: 5, scale: -1}
    comparator_class: NUMERIC_DECLARED_GRANULARITY
    protocol_eligibility: ELIGIBLE
  - candidate_id: m7-candidate-0019
    semantic_path: /system/gateway_brand
    validation_mode: EEBUS_NATIVE_METADATA
    entity_slot: device_information
    entity_type: DeviceInformation
    feature_type: DeviceClassification
    feature_role: server
    value_function: deviceClassificationManufacturerData
    field_path: brandName
    descriptor: {classification_scope: device_information}
    unit: null
    comparator_class: STRING_EXACT_STABILITY
    protocol_eligibility: EEBUS_NATIVE
  - candidate_id: m7-candidate-0020
    semantic_path: /system/gateway_vendor
    validation_mode: EEBUS_NATIVE_METADATA
    entity_slot: device_information
    entity_type: DeviceInformation
    feature_type: DeviceClassification
    feature_role: server
    value_function: deviceClassificationManufacturerData
    field_path: vendorName
    descriptor: {classification_scope: device_information}
    unit: null
    comparator_class: STRING_EXACT_STABILITY
    protocol_eligibility: EEBUS_NATIVE
  - candidate_id: m7-candidate-0021
    semantic_path: /zones/zone_1/name
    validation_mode: EEBUS_NATIVE_METADATA
    entity_slot: zone_1
    entity_type: HeatingZone
    feature_type: DeviceClassification
    feature_role: server
    value_function: deviceClassificationUserData
    field_path: userLabel
    descriptor: {classification_scope: heating_zone}
    unit: null
    comparator_class: STRING_EXACT_STABILITY
    protocol_eligibility: EEBUS_NATIVE
  - candidate_id: m7-candidate-0022
    semantic_path: /zones/zone_2/name
    validation_mode: EEBUS_NATIVE_METADATA
    entity_slot: zone_2
    entity_type: HeatingZone
    feature_type: DeviceClassification
    feature_role: server
    value_function: deviceClassificationUserData
    field_path: userLabel
    descriptor: {classification_scope: heating_zone}
    unit: null
    comparator_class: STRING_EXACT_STABILITY
    protocol_eligibility: EEBUS_NATIVE
```

## Eligibility Interpretation

`protocol_eligibility: ELIGIBLE` means only that both protocol identities are closed
enough for a synchronized comparator. It does not mean the eBUS peer exists,
the source is currently readable, the values match, or the candidate is
promoted. Candidate `0006` may use its exact B555 fallback only because the
VR940f `temp_slots=1` read-back is protocol-grounded as the current B524 DHW
setpoint; B509 desired temperature is not an admitted substitute.

`protocol_eligibility: EEBUS_NATIVE` is limited to metadata or capability facts
which have no fabricated eBUS equivalent. Promotion requires the exact SPINE
identity and typed value in both PRE and POST windows, unchanged across the
restart. Numeric range checks and exact boolean/string typing still apply. This
proves a restart-stable native fact, not cross-protocol equivalence or universal
immutability across operating states. For `DeviceClassification` candidates,
`descriptor` is catalog context bound to the resolved entity slot, entity type,
feature role, value function, and field path. It is not claimed to originate
from a separate SPINE description function when the feature exposes none.

The four terminal records stay exactly terminal and cannot be relabeled by
rehashing an evidence bundle. They are retired from the semantic leaf count.
The promotable inventory is the 18 real sources `0005` through `0022`; a
validator must also preserve the four retired records and their original M7
states.

The exact validation partition is 11 synchronized cross-protocol candidates
(`0005`, `0006`, `0007`, `0009`, `0010`, `0011`, `0012`, `0014`, `0015`,
`0016`, `0018`) and seven eeBUS-native candidates (`0008`, `0013`, `0017`,
`0019`-`0022`). Cross-protocol comparator ownership, B555 identity validation,
campaign assembly, and promotion decisions remain in `helianthus-docs-ebus`;
this inventory owns only the eeBUS source facts and candidate bindings consumed
by that platform contract. The serialized companion is
[`helianthus-docs-ebus#418`](https://github.com/Project-Helianthus/helianthus-docs-ebus/issues/418).

## Evidence And Redaction

[`EV-20260811-002`](../../evidence/EV-20260811-002.md) records the owner-local
reads used to assemble this inventory. Public evidence may retain the
descriptor, function, field, unit, constraint and relation values above.
It must not retain peer SKI, SHIP ID, service id, device/entity/feature native
selectors, network coordinates, read tokens, private keys, PEM private
material, trust-store bytes, or a reverse map for redacted selectors.

The existing single-leaf
[outdoor-temperature evidence profile](msp-085-live-r2-outdoor-temperature-promotion-evidence.md)
remains the detailed capture contract for candidate `m7-candidate-0018`. This
inventory does not weaken or replace it.
