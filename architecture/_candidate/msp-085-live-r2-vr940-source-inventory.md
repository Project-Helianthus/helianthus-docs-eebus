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

This page owns the eeBUS protocol identity for 18 candidate-bound VR940f
sources. It does not own terminal history, semantic paths, cross-protocol
comparators, campaign rules, or promotion decisions. The gateway must bind each
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
values use `number * 10^scale`. Numeric source entries bind the exact
descriptor, unit, and protocol-declared constraints. A platform comparator may
consume those facts, but its tolerance and conversion policy are not defined
here.

```yaml
contract: helianthus.eebus.vr940f-m7-source-inventory.v1
schema_version: 1
target_model: VR940f
selector_binding: exact_from_private_capture
decimal_rule: number_times_ten_to_scale
sources:
  - candidate_id: m7-candidate-0005
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
  - candidate_id: m7-candidate-0006
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
  - candidate_id: m7-candidate-0007
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
  - candidate_id: m7-candidate-0008
    source_classification: EEBUS_NATIVE_CAPABILITY
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
  - candidate_id: m7-candidate-0009
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
  - candidate_id: m7-candidate-0010
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
  - candidate_id: m7-candidate-0011
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
  - candidate_id: m7-candidate-0012
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
  - candidate_id: m7-candidate-0013
    source_classification: EEBUS_NATIVE_CAPABILITY
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
  - candidate_id: m7-candidate-0014
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
  - candidate_id: m7-candidate-0015
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
  - candidate_id: m7-candidate-0016
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
  - candidate_id: m7-candidate-0017
    source_classification: EEBUS_NATIVE_CAPABILITY
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
  - candidate_id: m7-candidate-0018
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
  - candidate_id: m7-candidate-0019
    source_classification: EEBUS_NATIVE_METADATA
    entity_slot: device_information
    entity_type: DeviceInformation
    feature_type: DeviceClassification
    feature_role: server
    value_function: deviceClassificationManufacturerData
    field_path: brandName
    descriptor: {classification_scope: device_information}
    unit: null
  - candidate_id: m7-candidate-0020
    source_classification: EEBUS_NATIVE_METADATA
    entity_slot: device_information
    entity_type: DeviceInformation
    feature_type: DeviceClassification
    feature_role: server
    value_function: deviceClassificationManufacturerData
    field_path: vendorName
    descriptor: {classification_scope: device_information}
    unit: null
  - candidate_id: m7-candidate-0021
    source_classification: EEBUS_NATIVE_METADATA
    entity_slot: zone_1
    entity_type: HeatingZone
    feature_type: DeviceClassification
    feature_role: server
    value_function: deviceClassificationUserData
    field_path: userLabel
    descriptor: {classification_scope: heating_zone}
    unit: null
  - candidate_id: m7-candidate-0022
    source_classification: EEBUS_NATIVE_METADATA
    entity_slot: zone_2
    entity_type: HeatingZone
    feature_type: DeviceClassification
    feature_role: server
    value_function: deviceClassificationUserData
    field_path: userLabel
    descriptor: {classification_scope: heating_zone}
    unit: null
```

## Source Ownership

The inventory contains exactly the 18 source references `0005` through `0022`.
Seven sources (`0008`, `0013`, `0017`, `0019`-`0022`) carry a local
`source_classification` because their typed capability or metadata fields are
directly inspectable without a second protocol. This classification does not
define a comparator, restart rule, semantic path, or promotion outcome.

Terminal provenance, cross-protocol comparator ownership, semantic paths,
fallback identity, campaign assembly, and promotion decisions remain in
`helianthus-docs-ebus`. The serialized companion is
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
