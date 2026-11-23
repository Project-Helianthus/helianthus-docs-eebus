---
canonical_source: "Project-Helianthus/helianthus-docs-eebus:api/_candidate/eebus-remote-sources-v1.md"
owner_domain: "api"
license: "AGPL-3.0-only"
publication_status: "candidate"
claim_status: "evidence-backed"
source_class: "derived_inference"
evidence_ids: "EV-20260711-001"
hypothesis_status: "draft"
falsifier: "A trusted remote's watt-hour stays in watt-hours, a percent stays above 1, a consumption sample is stored negative, an unpaired remote is treated as trusted, or two units are joined without identification evidence or the operator's certification."
stable_navigation: "false"
search: "false"
sitemap: "false"
versioned_bundle: "false"
release_bundle: "false"
candidate_output: "true"
candidate_output_path: "api/_candidate/eebus-remote-sources-v1.md"
---

# Candidate remote eeBUS sources v1

## Status

This page states how a remote eeBUS device is a source: the actor this node
takes, the values it reads, and when the remote is the same asset as a native
one. Candidate status is the maturity level of this page. It is not a
condition on implementing or publishing the rule. The node's own entity role
stays CEM.

## Actors and use cases

The node takes the client actor below with every remote whose SHIP trust is
established (SHIP 1.0.1 section 13.4.4). A remote that is not paired is shown
with its SHIP state and has no trusted data flow.

| use case and version | actor this node takes | remote actor |
| --- | --- | --- |
| Monitoring of Grid Connection Point 1.0.0 | Monitoring Appliance | Grid Connection Point |
| Monitoring of Power Consumption 1.0.0 | Monitoring Appliance | Monitored Unit |
| EVSE Commissioning and Configuration 1.0.1 | CEM; discovery string `CEM` (section 3.2.2.1) | EVSE |
| EV Commissioning and Configuration 1.0.1 | CEM; discovery string `CEM` (section 3.2.2.1) | EV |
| EV Charging Electricity Measurement 1.0.1 | Energy Guard; discovery string `CEM` (section 3.2.2.1) | EV |
| EV State of Charge 1.0.0 RC1 | Monitoring Appliance; discovery string `MonitoringAppliance` (section 3.2.2.1) | EV |
| Visualization of Aggregated Photovoltaic Data 1.0.0 RC1 | Visualization Appliance; discovery string `VisualizationAppliance` (section 3.2.1.1) | the remote that serves the aggregate |
| Visualization of Aggregated Battery Data 1.0.0 RC1 | Visualization Appliance; discovery string `VisualizationAppliance` (section 3.2.1.1) | the remote that serves the aggregate |

For a trusted remote the node also takes the client actor of every command use
case the normative source record lists that the remote offers. The specification's own
mandatory, recommended or optional marking is the only selector. The node's
entity role remains CEM.

| command use case and version | client actor this node takes | remote server |
| --- | --- | --- |
| Limitation of Power Consumption 1.0.0 | Energy Guard | Controllable System |
| Limitation of Power Production 1.0.0 | Energy Guard | Controllable System |
| Coordinated EV Charging 1.0.1 | Energy Guard or Energy Broker, as that scenario names | EV |
| EV Charging Summary 1.0.1 | Energy Broker | EVSE |
| Optimization of Self-Consumption During EV Charging 1.0.1b | CEM | EV |
| Overload Protection by EV Charging Current Curtailment 1.0.1b | Energy Guard | EV |
| Incentive-Table based power consumption management 1.0.0 RC3 | CEM | Energy Consumer |
| Time of Use Tariff 1.0.0 | Energy Broker or Transmission Broker | CEM |
| Power Demand Forecast 1.0.0 | Energy Broker or Transmission Broker | CEM |
| Power Envelope 1.0.0 | Transmission Broker | CEM |
| Optimization of Self Consumption by Heat Pump Compressor Flexibility 1.0.0 | CEM | Compressor |
| Control of Battery 1.0.0 | CEM | Inverter |

## Values

A watt-hour becomes joule: 1 Wh is 3600 J. A percent becomes a ratio from 0 to
1: 50 percent is 0.5. Grid active power follows the use case: consumption is
positive and production is negative when `positiveEnergyDirection` is `consume`
(Monitoring of Grid Connection Point 1.0.0; Monitoring of Power Consumption
1.0.0 [MPC-001]). Voltage is not signed by that energy direction. A read is
the direction of every measurement below. A write is declared only for a
command use case whose own clause marks the element changeable.

| use case | value | SemReg element | subject | unit conversion (Wh to J, percent to ratio 0–1) | sign rule |
| --- | --- | --- | --- | --- | --- |
| Monitoring of Grid Connection Point 1.0.0 | total active power, scope `acPowerTotal` | `infrastructure.power.pcc` | `resource.grid_connection` | watt | positive consumption |
| Monitoring of Grid Connection Point 1.0.0 | grid consumed energy, scope `gridConsumption` | `infrastructure.energy.import` | `resource.meter` | 1 Wh is 3600 J | import only; feed-in does not reduce it |
| Monitoring of Grid Connection Point 1.0.0 | grid feed-in energy, scope `gridFeedIn` | `infrastructure.energy.export` | `resource.meter` | 1 Wh is 3600 J | feed-in only; import does not reduce it |
| EV Charging Electricity Measurement 1.0.1 | phase active power, scope `acPower` | `evse.ac.active_power` | `resource.phase` | watt | consumption positive |
| EV Charging Electricity Measurement 1.0.1 | phase current, scope `acCurrent` | `evse.ac.current` | `resource.phase` | ampere | consumption positive |
| EV Charging Electricity Measurement 1.0.1 | charged energy, scope `charge` | `evse.energy.session` | `resource.charging_session` | 1 Wh is 3600 J | not an energy-direction sign |

Values with no SemReg element yet stay native in the eebusreg namespace. They
are still converted when a later element is added, and they are not invented
here: Monitoring of Power Consumption totals and phase powers other than the
EVSE phase row; the PV curtailment factor (percent to ratio); EV state of
charge and state of health (50 percent is 0.5) and travel range; the
aggregated photovoltaic and aggregated battery visualization values; incentive
costs and durations; and every command-use-case limit, failsafe, setpoint and
heartbeat that has no element on this page.

## Identity

A remote unit is its own asset. It is a contributor source of the native asset
only when matching identification evidence, such as the SKI a vendor gateway
exposes, or the operator's certification says so. Nothing else joins them. A
remote with no such proof stays a separate asset. An unpaired remote is shown
with its reported SHIP state and supplies no trusted data flow.

## Unchanged surfaces

This page does not change the output pages, the normative source record, or
the inbound heating mapping.

## Vectors

| id | use case, actor and feature | synthetic input | expected outcome | clause |
| --- | --- | --- | --- | --- |
| `wh_to_joule` | EV Charging Electricity Measurement 1.0.1, Energy Guard, Measurement `charge` | 1 Wh | 3600 J | EV Charging Electricity Measurement 1.0.1 |
| `percent_to_ratio` | EV State of Charge 1.0.0 RC1, Monitoring Appliance, Measurement `stateOfCharge` | 50 percent | 0.5 | EV State of Charge 1.0.0 RC1 |
| `grid_consumption_positive` | Monitoring of Grid Connection Point 1.0.0, Monitoring Appliance, Measurement `acPowerTotal` | consumption sample, `positiveEnergyDirection` consume | stored positive consumption | Monitoring of Grid Connection Point 1.0.0 |
| `grid_production_negative` | Monitoring of Power Consumption 1.0.0, Monitoring Appliance, Measurement `acPowerTotal` | production sample | stored negative production | Monitoring of Power Consumption 1.0.0 [MPC-001] |
| `identity_without_proof` | remote unit, no feature | no identification evidence | separate asset | a remote stays its own asset without proof |
| `identity_with_proof` | remote unit, no feature | matching identification or the operator's certification | contributor of that native asset | identification evidence or the operator's certification |
| `unpaired_remote` | remote unit, no feature | SHIP trust is not established | reported SHIP state and no trusted data flow | SHIP 1.0.1 section 13.4.4 |
| `trusted_command_client` | Limitation of Power Consumption 1.0.0, Energy Guard, LoadControl | a trusted remote offers the use case | Energy Guard client with the specification M/R/O | Limitation of Power Consumption 1.0.0 |

## Open points

Where a listed value has no SemReg element yet, the element stays unknown.
Flexible Load / Smart Heater DHW and the Smart Grid Ready conditions use cases
are unavailable, and nothing on this page is taken from them.
