---
canonical_source: "Project-Helianthus/helianthus-docs-eebus:api/_candidate/eebus-output-publication-v1.md"
owner_domain: "api"
license: "AGPL-3.0-only"
publication_status: "candidate"
claim_status: "evidence-backed"
source_class: "derived_inference"
evidence_ids: "EV-20260711-001"
hypothesis_status: "draft"
falsifier: "A reviewed eeBUS output publishes a heating or battery resource, adds a second advertisement, uses the CEM entity as a device Controllable System, or applies a watt limit without the measured voltage and active phases, and the owning check accepts that output."
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

Proven. The canonical discovery page states one advertisement for SHIP and device type EnergyManagementSystem.
That discovery page is the SHIP and SPINE overview already published in this
repository.
`EV-20260711-001` supports the publication boundary only.

Hypothesis. The actor selection and the announcement rule are this candidate.
No implementation in this repository has exercised them.

Unknown. The mandatory elements of each use case are not enumerated on this page.
Whether a trusted remote already announces Energy Guard is not known here.

None of these classes is a device qualification.

## Published resources

Publish every lens-admitted inverter, PV string and charger resource.
A heating resource is not published.
A battery resource is not published.
A lens-admitted resource is one entity of this output (CID-1).

A charger resource is the EVSE entity. A meter, generic equipment, heating
equipment and a battery stay outside this publication.

An input-dimension fact is not a string (CID-4).
A PV String entity is a child of the Inverter only through a cited contains instance (TRV-1).

Admitted inverter elements are inverter AC measurements, energy, temperature and operating state.
`pv.operation.set_active_power_limit` is admitted in watts.
String-dimension DC quantities are not admitted.
Inverter apparent power, inverter reactive power and line-to-line voltage are not admitted.
The admitted charger operation is `evse.operation.set_allocated_current`.
Canonical units are SI.

## Advertisement and entities

One advertisement for SHIP stays.
The device type is EnergyManagementSystem.
Reject a second advertisement for SHIP.
A second service is not added.
The node keeps one CEM entity.
The extra entities are Inverter, a PV String child of that Inverter, and EVSE.

A use case that forbids that device type is not announced, and the loss names the prohibition.

## Actors this node takes

The actor Inverter of Monitoring of Inverter V1.0.0 is taken on entity type Inverter.
The actor PV String of Monitoring of PV String V1.0.0 RC4 is taken when a string resource exists.
The actor Inverter is the Controllable System of Limitation of Power Production V1.0.0.
The actor EVSE of EVSE Commissioning and Configuration V1.0.1 is taken.
The actor EVSE is the Monitored Unit of Monitoring of Power Consumption V1.0.0.
The actor EVSE is the Controllable System of Limitation of Power Consumption V1.0.0.

The local CEM takes Energy Guard of a limitation use case only while no trusted remote already announces Energy Guard for that use case.
The CEM entity is never the Controllable System of one device.
The CEM entity is never the Monitored Unit.
A CEM-located Controllable System represents every device that CEM controls, not the CEM's own power.

Other entity types a cited use case permits are not taken on this node.
GridGuard is not an entity of this node. A heating entity is not added for a
consumption limit.

## Announcement and loss

A use case is announced only when every mandatory scenario can be served from admitted elements of that resource.
Otherwise the use case is not announced, and the loss names each missing element.
Where a mandatory element is cited as absent, the loss names it (LRS-3, TGT-3).
A partial resource stays partial. Missing elements are not invented.

Limitation of Power Consumption V1.0.0 is announced on the EVSE entity when the allocated-current operation is admitted for that resource and the host accepts limits; scenarios 1 to 3 are served, scenario 4 is not.
A use case whose device-side actor is EV is not announced.
This node is not an EV.
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
A phase is active while its measured current is above zero; when no phase carries current, every phase with a measured voltage counts. The measured voltage is the mean of the active phases' measured voltages.
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
A newer revision of SHIP is not cited.
Citing these revisions does not resolve a normative source row.

The cited use-case revisions are Monitoring of Inverter V1.0.0, Monitoring of
PV String V1.0.0 RC4, EVSE Commissioning and Configuration V1.0.1, Limitation
of Power Production V1.0.0, Limitation of Power Consumption V1.0.0 and
Monitoring of Power Consumption V1.0.0.

## Vectors

These rows are the contract's own vectors. The outcome column is the rule above.

| Case | Given | Outcome |
| --- | --- | --- |
| `heating_resource` | family heating, lens admitted, runtime enabled | not_published |
| `battery_resource` | family battery, lens admitted, runtime enabled | not_published |
| `inverter_resource` | family inverter, lens admitted, runtime enabled | published |
| `pv_string_resource` | family pv string, child of the inverter, lens admitted | published |
| `charger_resource` | family charger, lens admitted, runtime enabled | published |
| `second_ship_advertisement` | advertisement count 2 | rejected |
| `one_ship_advertisement` | advertisement count 1 and device type EnergyManagementSystem | kept |
| `cem_controllable_system` | CEM entity as Controllable System of one device | rejected |
| `inverter_controllable_system` | Inverter entity as Controllable System | taken |
| `watt_limit_as_current` | consumption limit in watts through allocated current | converted |
| `watt_limit_below_minimum` | consumption limit in watts that computes below 6 A | paused |
| `watt_limit_without_voltage` | consumption limit in watts with no measured voltage from the charging station or another promoted resource | refused |
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
