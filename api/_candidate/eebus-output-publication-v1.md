---
canonical_source: "Project-Helianthus/helianthus-docs-eebus:api/_candidate/eebus-output-publication-v1.md"
owner_domain: "api"
license: "AGPL-3.0-only"
publication_status: "candidate"
claim_status: "evidence-backed"
source_class: "derived_inference"
evidence_ids: "EV-20260711-001"
hypothesis_status: "draft"
falsifier: "A reviewed eeBUS output withholds a lens-admitted heating, battery, grid-connection or meter resource, merges a meter into the grid connection, or applies a watt limit without the measured voltage and active phases, and the owning check accepts that output."
stable_navigation: "false"
search: "false"
sitemap: "false"
versioned_bundle: "false"
release_bundle: "false"
candidate_output: "true"
candidate_output_path: "api/_candidate/eebus-output-publication-v1.md"
---

# Candidate eeBUS output publication v1

## Status and scope

This page is the 0.7 publication rule for an eeBUS output. It states which
resources are published and which use cases are announced. It does not add a
lens, an element, or a switch.

The output is active when the eeBUS runtime is already enabled.
There is no new switch.

The page is a candidate. It is excluded from stable navigation, search, the
sitemap, versioned bundles and release bundles. It performs no bus request
and no device write. Protocol text stays in `protocols/`. Lens rules are
cited by identifier from
[the output-binding contract](eebus-output-binding-contract-v1.md).
This page does not copy that contract.

Issue
[helianthus-docs-eebus#186](https://github.com/Project-Helianthus/helianthus-docs-eebus/issues/186).
Issue
[helianthus-docs-eebus#189](https://github.com/Project-Helianthus/helianthus-docs-eebus/issues/189).

## Evidence class

Proven. Discovery follows SHIP 1.0.1 §7, and the SPINE device type follows SPINE Resource Specification 1.3.0 Table 353 or SPINE Protocol Specification 1.3.0 §7.1.1.1.
That discovery page is the SHIP and SPINE overview already published in this
repository.
`EV-20260711-001` supports the publication boundary only.

Hypothesis. The actor selection and the announcement rule are this candidate.
No implementation in this repository has exercised them.

Unknown. The mandatory elements of each use case are not enumerated on this page.
Whether a trusted remote already announces Energy Guard is not known here.

None of these classes is a device qualification.

## Published resources

Publish every lens-admitted inverter, PV string, charger, battery, heating, grid-connection and meter resource.
A heating resource is published.
A battery resource is published.
A lens-admitted resource is one entity of this output (CID-1).
A meter resource is its own SubMeterElectricity entity beside the grid connection and is never merged into it.
The EVSE total is the SemReg member sum of one cut and is marked derived.
The node serves the heartbeat Limitation of Power Production V1.0.0 [LPP-031] defines.
The EVSE operating state is a declared mapping from the EVSE statuses.

A charger resource is the EVSE entity. A thermal value of a heating zone, hot water or system outdoor sensor is a feature value of its SemReg element in kelvin.

An input-dimension fact is not a string (CID-4).
A PV String entity is a child of the Inverter only through a cited contains instance (TRV-1).

Admitted inverter elements are inverter AC measurements, apparent power, reactive power, line-to-line voltage, energy, temperature and operating state.
`pv.operation.set_active_power_limit` is admitted in watts.
String-dimension DC quantities are admitted.
Inverter apparent power, inverter reactive power and line-to-line voltage are admitted.
The admitted charger operation is `evse.operation.set_allocated_current`.
Canonical units are SI.

## Advertisement and entities

SHIP 1.0.1 §7 prints no fixed number of advertisements.
The SPINE device type is a standard type of SPINE Resource Specification 1.3.0 Table 353 or a vendor-specific type matching SPINE Protocol Specification 1.3.0 §7.1.1.1.
A second advertisement that meets SHIP 1.0.1 §7 is accepted.
A second service that meets SHIP 1.0.1 §7 is accepted.
The node keeps one CEM entity.
The published entities include Inverter, a PV String child of that Inverter, EVSE, Battery, heating, the grid connection and a distinct meter.
Where a use-case clause prints no device type for the role this node takes, that device type stays unknown.

A use case that forbids that device type is not announced, and the loss names the prohibition.

## Actors this node takes

The actor Inverter of Monitoring of Inverter V1.0.0 is taken on entity type Inverter.
The actor PV String of Monitoring of PV String V1.0.0 RC4 is taken when a string resource exists.
The actor Inverter is the Controllable System of Limitation of Power Production V1.0.0.
The actor EVSE of EVSE Commissioning and Configuration V1.0.1 is taken.
The actor EVSE is the Monitored Unit of Monitoring of Power Consumption V1.0.0.
The actor Inverter is the Monitored Unit of Monitoring of Power Consumption V1.0.0.
The actor Battery of Monitoring of Battery V1.0.0 is taken.
The HVAC monitoring actors of HVAC Temperature V1.0.0 and HVAC System Function V1.0.0 are taken.
The actor Grid Connection Point of Monitoring of Grid Connection Point V1.0.0 is taken.
The actor EVSE is the Controllable System of Limitation of Power Consumption V1.0.0.

The local CEM takes Energy Guard of a limitation use case only while no trusted remote already announces Energy Guard for that use case.
The CEM entity is never the Controllable System of one device.
The CEM entity is never the Monitored Unit.
A CEM-located Controllable System represents every device that CEM controls, not the CEM's own power.

GridGuard is not an entity of this node.

## Announcement and loss

A use case is announced only when every mandatory scenario can be served from admitted elements of that resource.
Otherwise the use case is not announced, and the loss names each missing element.
Where a mandatory element is cited as absent, the loss names it (LRS-3, TGT-3).
A partial resource stays partial. Missing elements are not invented.

Limitation of Power Consumption V1.0.0 is announced on the EVSE entity when the allocated-current operation is admitted for that resource and the host accepts limits, and the node serves the heartbeat Limitation of Power Consumption V1.0.0 [LPC-031] defines; each scenario keeps the specification's own mandatory, recommended or optional marking.
An EV actor is announced when the SemReg elements its use case requires are present.
The node presents the EV actor of each charging use case wherever SemReg has its elements.
Overload protection, self-consumption during charging, and charging electricity measurement name the actor EV.

Two overlapping writes are the existing conflict loss.

## Writes

A mapped write is published only where that resource's own capability admits the operation (LRS-5, AUT-3).
A production-limit write is mapped only through `pv.operation.set_active_power_limit` when that operation is admitted for that resource.
A production-limit write is not mapped to the system export operation.
A consumption-limit write is active power.
The only admitted charger write is allocated current.
A consumption-limit write on the EVSE entity is applied through `evse.operation.set_allocated_current`.
Amperes = the limit in watts / (active phases × measured phase voltage), rounded down to a whole ampere and clamped to the station's range.
A phase is active while its measured current is above zero; when no phase carries current and the charging session holds no remembered phase count, every phase with a measured voltage counts. The measured voltage is the mean of the active phases' measured voltages.
While a charging session is paused by the limit, the conversion uses the number of phases that carried current when that pause began.
The remembered phase count holds only for the same charging session; a new session, or an EV seen drawing on more phases, goes back to the phases that carry current and, with none yet, to every phase with a measured voltage, so a restart above the limit lasts at most one conversion cycle.
Example: a single-phase EV on a station that measures 230 V on three phases is paused by a 1000 W limit; a limit raised to 3000 W in the same session gives 3000 / (1 × 230), rounded down to 13 A.
While a consumption limit is effective, the allocated current is recomputed from each new measurement of phase current, measured voltage or configured current.
While any phase carries current, every phase that has carried current since the EV connected also counts as active, so a phase that stops and later resumes is counted before it resumes.
Where the charging station publishes no connection state, those phases are counted from the moment the consumption limit became effective.
The measured phase voltage is the phase voltage the charging station publishes, when that resource publishes one.
When the charging station publishes no phase voltage, the measured phase voltage is the measured AC phase voltage of another promoted resource of the same installation, an inverter AC side or a meter.
Site and electrical relations select that resource when they exist.
When the installation has exactly one other promoted source of AC phase voltage, that source is used.
When more than one other promoted source publishes an AC phase voltage and no site or electrical relation selects one, the write is answered with a negative acknowledgement that names the missing measured voltage.
From that other source, the measured voltage is the mean of the voltages it publishes on the charger's active phases, matched by phase.
When the voltage source publishes no voltage on one of the charger's active phases, the write is answered with a negative acknowledgement that names the missing measured voltage.
A nominal voltage is not a measured phase voltage.
The station's range runs from 6 A to the station's configured current. A result below 6 A pauses charging: allocated current 0 A.
A limit whose inputs are not published (measured voltage, phase current or configured current) is answered with a negative acknowledgement that names the missing input.
When neither source publishes a phase voltage, the write is answered with a negative acknowledgement that names the missing measured voltage.
The effective limit follows section 2.2 of the use case. A deactivated or expired limit releases the charger to the configured current. The failsafe values are pre-configured to 4200 W and 2 hours, stored, and may be changed by the Energy Guard.
Unit conversion is display-only. The watt-to-ampere computation of a consumption limit is a control rule, not a unit conversion.
A production-limit write on the Inverter entity is handed to the host and applied through `pv.operation.set_active_power_limit` in watts, with no conversion. Its effective limit follows the state machine of Limitation of Power Production V1.0.0; the failsafe production limit is pre-configured to the upper bound of `pv.limit.active_power` in the PV pack, which restricts nothing, and the failsafe duration minimum to 2 hours.

## Cited revisions

The cited transport revision is SHIP 1.0.1.
The cited data-model revision is SPINE 1.3.0.
SHIP 1.1.0 is recorded as a later revision and is not the revision this node declares.
The recorded revisions declare the mappings.

The cited use-case revisions are Monitoring of Inverter V1.0.0, Monitoring of
PV String V1.0.0 RC4, EVSE Commissioning and Configuration V1.0.1, Limitation
of Power Production V1.0.0, Limitation of Power Consumption V1.0.0 and
Monitoring of Power Consumption V1.0.0.

## Value mapping

| SemReg element | SPINE feature | scope | unit | conversion |
| --- | --- | --- | --- | --- |
| inverter AC active power | Measurement | acPowerTotal | W | none |
| inverter apparent power | Measurement | acPowerApparentTotal | VA | none; non-negative (Monitoring of Inverter 1.0.0) |
| inverter reactive power | Measurement | acPowerReactiveTotal | var | none |
| line-to-line voltage | Measurement | acVoltage phase-to-phase | V | none; voltage is not an energy-direction sign (Monitoring of Power Consumption 1.0.0) |
| string DC quantities | Measurement | string DC power, voltage and current | W, V, A | none |
| heating zone temperature | Measurement | room temperature | K | degree Celsius to kelvin |
| hot-water temperature | Measurement | DHW temperature | K | degree Celsius to kelvin |
| system outdoor temperature | Measurement | outsideAirTemperature | K | degree Celsius to kelvin |
| battery state of charge | Measurement | state of charge | ratio 0-1 | percent to ratio |
| grid active power | Measurement | acPowerTotal | W | positive sample is consumption where positiveEnergyDirection is consume |
| meter energy | Measurement | acEnergyConsumed | J | Wh to J, 1 Wh is 3600 J |
| EVSE total active power | Measurement | acPowerTotal | W | SemReg member sum of one cut, marked derived; valueSource admits calculatedValue (Monitoring of Power Consumption 1.0.0 section 3.2.2.2.3.3 Table 25) |

Monitoring of Grid Connection Point 1.0.0 scenarios, Monitoring Appliance then Grid Connection Point: 1 O/O, 2 R/M, 3 O/M, 4 O/M, 5 O/R, 6 O/O, 7 O/O. Each scenario keeps the specification's own mandatory, recommended or optional marking.

## Vectors

These rows are the contract's own vectors. The outcome column is the rule above.

| Case | Given | Outcome |
| --- | --- | --- |
| `heating_resource` | family heating, lens admitted, runtime enabled | published |
| `battery_resource` | family battery, lens admitted, runtime enabled | published |
| `inverter_resource` | family inverter, lens admitted, runtime enabled | published |
| `pv_string_resource` | family pv string, child of the inverter, lens admitted | published |
| `charger_resource` | family charger, lens admitted, runtime enabled | published |
| `grid_connection_resource` | family grid connection, lens admitted, runtime enabled | published |
| `meter_resource` | family meter, lens admitted, runtime enabled | published |
| `grid_and_meter_one_cut` | grid connection and meter of one cut, meter distinct | both_published |
| `service_name_other` | service name other than ship | rejected |
| `instance_name_over_63` | instance name over 63 bytes | rejected |
| `mandatory_txt_missing` | a mandatory TXT key is missing | rejected |
| `txtvers_other` | txtvers other than 1 | rejected |
| `txt_record_over_400` | TXT record over 400 bytes | rejected |
| `ship_id_not_unique` | id that is not unique | rejected |
| `device_type_inverter` | standard device type Inverter | accepted |
| `device_type_vendor` | vendor-specific type matching the protocol pattern | accepted |
| `device_type_vendor_rejected` | vendor-specific type that does not match the pattern | rejected |
| `announcement_without_txt_type` | announcement without the optional TXT type | accepted |
| `extra_optional_key` | a permitted additional optional key within 400 bytes | accepted |
| `instance_renamed_same_id` | instance renamed after a collision with the same SHIP id | accepted |
| `second_advertisement_meets_section_7` | a second advertisement that meets section 7 | accepted |
| `second_service_meets_section_7` | a second service that meets section 7 | accepted |
| `cem_controllable_system` | CEM entity as Controllable System of one device | rejected |
| `inverter_controllable_system` | Inverter entity as Controllable System | taken |
| `inverter_monitored_unit` | Monitored Unit of Monitoring of Power Consumption on an Inverter | taken |
| `evse_monitored_unit` | Monitored Unit of Monitoring of Power Consumption on an EVSE | taken |
| `watt_limit_as_current` | consumption limit in watts through allocated current | converted |
| `watt_limit_below_minimum` | consumption limit in watts that computes below 6 A | paused |
| `watt_limit_without_voltage` | consumption limit in watts with no measured voltage from the charging station or another promoted resource | refused |
| `watt_limit_paused_single_phase` | one phase carried current when a 1000 W limit paused the session, three phases measure 230 V, limit raised to 3000 W in the same session | converted |
| `production_limit_write` | admitted production limit in watts | applied |

## Unchanged surfaces

No semantic element is added.
No contract version is raised.
The output-binding contract, the inbound pages and the frozen API reference
stay as they are. No alias, compatibility shim or migration step is added.

## Promotion decision

Decision: **remain candidate**.

The page states the publication rule before an implementation exists.
Promotion into a stable channel is a later step of the publication procedure.
