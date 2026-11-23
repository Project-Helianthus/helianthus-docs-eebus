---
canonical_source: "Project-Helianthus/helianthus-docs-eebus:protocols/spine-resources-1.3.0.md"
owner_domain: "protocols"
license: "CC0-1.0"
publication_status: "publishable"
claim_status: "evidence-backed"
source_class: "vendor_public"
evidence_ids: "EV-20260711-001"
hypothesis_status: "publishable"
falsifier: "A row drops a type, a length rule, or a conflict between the chapter and the annex."
---

# SPINE Resource Specification 1.3.0

Device, entity, and feature types, the functions of each feature, and the limits this specification prints. Chapter clauses and annex tables that state the same name with different wording both stay, each with its clause. The data file holds one row per data point.

## Device, entity and feature types

### Device types

| type | meaning (own words) | clause |
| --- | --- | --- |
| ChargingStation | A charging station, in the usual setting of electric-vehicle charging. | §4.1.1 |
| Dishwasher | A dishwasher. | §4.1.2 |
| Dryer | A dryer. | §4.1.3 |
| ElectricitySupplySystem | The electric-power sources or storages of a premises. Stated examples: a local PV system, the grid connection point, a battery storage. | §4.1.4 |
| EnergyManagementSystem | An EMS. | §4.1.5 |
| EnvironmentSensor | A sensor, typically for outdoor measurements. | §4.1.6 |
| Generic | A generic device, for client-only behaviour, or for development while no specific device type can be named. | §4.1.7 |
| HeatGenerationSystem | The heat-generating subsystem of an HVAC system. May be one generator (stated examples: gas boiler, heat pump), a cascade of generators, or a solar thermal system. Container for the entity types of the individual generators. | §4.1.8 |
| HeatSinkSystem | The HVAC sinks a person uses, and the system functions a person uses. Stated sink examples: heating circuits, DHW circuits, air conditioning. Stated function examples: heating of spaces, cooling of spaces, DHW, air conditioning. | §4.1.9 |
| HeatStorageSystem | Heat stores, one or several, or an appliance fixed to a store. Stated example: entity InstantDHWHeater (§4.2.34), a fresh-water station on a heating buffer. Every heat store in the HVAC installation ought to use this device type. | §4.1.10 |
| HVACController | The appliance that controls an HVAC installation from the centre. A device of this type carries installation-wide information. | §4.1.11 |
| Inverter | A power inverter. | §4.1.12 |
| SubMeter | A meter of demand or generation of a commodity. Electricity is the stated example. | §4.1.13 |
| Washer | A washing machine. | §4.1.14 |
| ChargingStation | clause not printed | SPINE Resource Specification 1.3.0 §4.1.1, Table 353 |
| Dishwasher | clause not printed | SPINE Resource Specification 1.3.0 §4.1.2, Table 353 |
| Dryer | clause not printed | SPINE Resource Specification 1.3.0 §4.1.3, Table 353 |
| ElectricitySupplySystem | clause not printed | SPINE Resource Specification 1.3.0 §4.1.4, Table 353 |
| EnergyManagementSystem | clause not printed | SPINE Resource Specification 1.3.0 §4.1.5, Table 353 |
| EnvironmentSensor | clause not printed | SPINE Resource Specification 1.3.0 §4.1.6, Table 353 |
| Generic | clause not printed | SPINE Resource Specification 1.3.0 §4.1.7, Table 353 |
| HeatGenerationSystem | clause not printed | SPINE Resource Specification 1.3.0 §4.1.8, Table 353 |
| HeatSinkSystem | clause not printed | SPINE Resource Specification 1.3.0 §4.1.9, Table 353 |
| HeatStorageSystem | clause not printed | SPINE Resource Specification 1.3.0 §4.1.10, Table 353 |
| HVACController | clause not printed | SPINE Resource Specification 1.3.0 §4.1.11, Table 353 |
| Inverter | clause not printed | SPINE Resource Specification 1.3.0 §4.1.12, Table 353 |
| SubMeter | clause not printed | SPINE Resource Specification 1.3.0 §4.1.13, Table 353 |
| Washer | clause not printed | SPINE Resource Specification 1.3.0 §4.1.14, Table 353 |

### Entity types

| type | meaning (own words) | clause |
| --- | --- | --- |
| Battery | One battery unit. | §4.2.1 |
| BatterySystem | Battery stores together with the inverters that serve them. Either side may be a single unit or several. | §4.2.2 |
| CEM | Abbreviation of customer energy manager. Typically an energy manager inside SPINE. | §4.2.3 |
| ChargingOutlet | One outlet on a ChargingStation. | §4.2.4 |
| Compressor | The compressor of an appliance, with an electrical heat pump given as the example. | §4.2.5 |
| ControllableSystem | What an energy manager is able to steer: a single appliance, or several acting together. | §4.2.6 |
| DeviceInformation | Special role: general information about the whole device. | §4.2.7 |
| DHWCircuit | The path that supplies domestic hot water: cold inlet, hot outlet, a loop that circulates, and the taps. Stores of that water belong in entity DHWStorage, not here. | §4.2.8 |
| DHWStorage | A heat storage for domestic hot water. | §4.2.9 |
| Dishwasher | A dishwasher. | §4.2.10 |
| Dryer | A dryer. | §4.2.11 |
| ElectricalImmersionHeater | An electrical resistance immersion heater. Stated placements: heat pump, heat-source unit, DHW storage. | §4.2.12 |
| ElectricalStorage | Marks an inverter as a battery-only inverter. The stated contrast is that no PV string is connected. | §4.2.13 |
| ElectricityGenerationSystem | On-site production of electric power. Stated examples: PV, wind turbines, and plants that supply both heat and power as a block. | §4.2.14 |
| ElectricityStorageSystem | Stores electric power and releases most of it again as electric power. Stated examples: a battery system, a capacitor. | §4.2.15 |
| EV | An electrical vehicle. | §4.2.16 |
| EVSE | Short name for equipment that supplies an electric vehicle. The usual purpose printed here is charging. | §4.2.17 |
| Fan | An air fan. Stated examples: air-water heat-pump unit, ventilation unit. | §4.2.18 |
| GasHeatingAppliance | A heating appliance that makes heat by burning natural gas. Stated purposes: heating, domestic hot water. | §4.2.19 |
| Generic | A generic entity, for client-only behaviour, or for development while no specific entity can be named. | §4.2.20 |
| GridConnectionPointOfPremises | The electrical joint between the utility grid and the premises circuit. | §4.2.21 |
| GridGuard | An energy manager that may sit in the building or elsewhere. It steers or limits appliances in order to keep the public grid stable. | §4.2.22 |
| HeatingBufferStorage | A heat storage for heating water. | §4.2.23 |
| HeatingCircuit | One circuit for space heating, or for space cooling (active or passive). Includes flow and return, optional mixing units on mixed circuits, and distribution either straight to one or more HVACRoom (§4.2.33) or to one or more HeatingZone (§4.2.26). | §4.2.24 |
| HeatingObject | A heating object. A radiator is the stated example. | §4.2.25 |
| HeatingZone | A zone that feeds heat, or cooling, into a single HVACRoom or into several. | §4.2.26 |
| HeatPumpAppliance | A whole heat pump, or only the indoor unit of a split that uses refrigerant. Stated whole-unit examples: brine-to-water indoors; air-to-water entirely indoors or entirely outdoors. | §4.2.27 |
| HeatSinkCircuit | A hydraulic circuit that carries heat from a generator to a heat sink. Stated example: a gas-heating circuit feeding a heating circuit. | §4.2.28 |
| HeatSourceCircuit | A hydraulic circuit, especially of a heat pump, that carries ambient heat to the generator. Stated example: a brine circuit. | §4.2.29 |
| HeatSourceUnit | An extra unit that brings environmental heat to the heat pump. Stated examples: an outdoor ventilation unit onto the indoor heat-source circuit (air-water split), or onto the refrigerant circuit (refrigerant split). | §4.2.30 |
| Household | A virtual entity for a whole household, aggregating household information. Complete energy demand is the stated example. | §4.2.31 |
| HVACController | The central HVAC controller appliance, as a SPINE entity. | §4.2.32 |
| HVACRoom | One room in a building. It can receive heat, cooling, ventilation, or air conditioning. | §4.2.33 |
| InstantDHWHeater | Instant domestic-hot-water generation. Stated example: heat taken from a heating buffer. | §4.2.34 |
| Inverter | A power inverter. | §4.2.35 |
| OilHeatingAppliance | A heating appliance that makes heat by burning oil. Stated purposes: heating, domestic hot water. | §4.2.36 |
| Pump | A pump that moves a medium. A heating circuit is the stated example. | §4.2.37 |
| PV | Marks an inverter as a PV-only inverter. The stated contrast is that no battery is connected. | §4.2.38 |
| PVESHybrid | Marks an inverter as a PV/battery hybrid. Both a battery bank and PV panels are attached. | §4.2.39 |
| PVString | A PV panel on the DC side, tied to an inverter. | §4.2.40 |
| PVSystem | PV modules plus the inverters that serve them, at least one of each. Presents the premises' PV equipment as one aggregated entity. | §4.2.41 |
| RefrigerantCircuit | Refrigerant loop inside a heat-pump appliance. | §4.2.42 |
| SmartEnergyAppliance | An appliance whose server-announced load a client may shift. Non-shiftable loads, called fixed forecasts, may also be provided. | §4.2.43 |
| SolarDHWStorage | A domestic-hot-water heat storage. Heat may come especially from solar thermal energy. Compared in the text with DHWStorage. | §4.2.44 |
| SolarThermalCircuit | A single solar-thermal loop: the collector field, pipes out and back, and the pump of that loop. | §4.2.45 |
| SubMeterElectricity | An electrical sub meter. | §4.2.46 |
| TemperatureSensor | Reports a measured temperature. | §4.2.47 |
| Washer | A laundry washer. | §4.2.48 |
| Battery | clause not printed | SPINE Resource Specification 1.3.0 §4.2.1, Table 354 |
| BatterySystem | clause not printed | SPINE Resource Specification 1.3.0 §4.2.2, Table 354 |
| CEM | clause not printed | SPINE Resource Specification 1.3.0 §4.2.3, Table 354 |
| ChargingOutlet | clause not printed | SPINE Resource Specification 1.3.0 §4.2.4, Table 354 |
| Compressor | clause not printed | SPINE Resource Specification 1.3.0 §4.2.5, Table 354 |
| ControllableSystem | clause not printed | SPINE Resource Specification 1.3.0 §4.2.6, Table 354 |
| DeviceInformation | clause not printed | SPINE Resource Specification 1.3.0 §4.2.7, Table 354 |
| DHWCircuit | clause not printed | SPINE Resource Specification 1.3.0 §4.2.8, Table 354 |
| DHWStorage | clause not printed | SPINE Resource Specification 1.3.0 §4.2.9, Table 354 |
| Dishwasher | clause not printed | SPINE Resource Specification 1.3.0 §4.2.10, Table 354 |
| Dryer | clause not printed | SPINE Resource Specification 1.3.0 §4.2.11, Table 354 |
| ElectricalImmersionHeater | clause not printed | SPINE Resource Specification 1.3.0 §4.2.12, Table 354 |
| ElectricalStorage | clause not printed | SPINE Resource Specification 1.3.0 §4.2.13, Table 354 |
| ElectricityGenerationSystem | clause not printed | SPINE Resource Specification 1.3.0 §4.2.14, Table 354 |
| ElectricityStorageSystem | clause not printed | SPINE Resource Specification 1.3.0 §4.2.15, Table 354 |
| EV | clause not printed | SPINE Resource Specification 1.3.0 §4.2.16, Table 354 |
| EVSE | clause not printed | SPINE Resource Specification 1.3.0 §4.2.17, Table 354 |
| Fan | clause not printed | SPINE Resource Specification 1.3.0 §4.2.18, Table 354 |
| GasHeatingAppliance | clause not printed | SPINE Resource Specification 1.3.0 §4.2.19, Table 354 |
| Generic | clause not printed | SPINE Resource Specification 1.3.0 §4.2.20, Table 354 |
| GridConnectionPointOfPremises | clause not printed | SPINE Resource Specification 1.3.0 §4.2.21, Table 354 |
| GridGuard | clause not printed | SPINE Resource Specification 1.3.0 §4.2.22, Table 354 |
| HeatingBufferStorage | clause not printed | SPINE Resource Specification 1.3.0 §4.2.23, Table 354 |
| HeatingCircuit | clause not printed | SPINE Resource Specification 1.3.0 §4.2.24, Table 354 |
| HeatingObject | clause not printed | SPINE Resource Specification 1.3.0 §4.2.25, Table 354 |
| HeatingZone | clause not printed | SPINE Resource Specification 1.3.0 §4.2.26, Table 354 |
| HeatPumpAppliance | clause not printed | SPINE Resource Specification 1.3.0 §4.2.27, Table 354 |
| HeatSinkCircuit | clause not printed | SPINE Resource Specification 1.3.0 §4.2.28, Table 354 |
| HeatSourceCircuit | clause not printed | SPINE Resource Specification 1.3.0 §4.2.29, Table 354 |
| HeatSourceUnit | clause not printed | SPINE Resource Specification 1.3.0 §4.2.30, Table 354 |
| Household | clause not printed | SPINE Resource Specification 1.3.0 §4.2.31, Table 354 |
| HVACController | clause not printed | SPINE Resource Specification 1.3.0 §4.2.32, Table 354 |
| HVACRoom | clause not printed | SPINE Resource Specification 1.3.0 §4.2.33, Table 354 |
| InstantDHWHeater | clause not printed | SPINE Resource Specification 1.3.0 §4.2.34, Table 354 |
| Inverter | clause not printed | SPINE Resource Specification 1.3.0 §4.2.35, Table 354 |
| OilHeatingAppliance | clause not printed | SPINE Resource Specification 1.3.0 §4.2.36, Table 354 |
| Pump | clause not printed | SPINE Resource Specification 1.3.0 §4.2.37, Table 354 |
| PV | clause not printed | SPINE Resource Specification 1.3.0 §4.2.38, Table 354 |
| PVESHybrid | clause not printed | SPINE Resource Specification 1.3.0 §4.2.39, Table 354 |
| PVString | clause not printed | SPINE Resource Specification 1.3.0 §4.2.40, Table 354 |
| PVSystem | clause not printed | SPINE Resource Specification 1.3.0 §4.2.41, Table 354 |
| RefrigerantCircuit | clause not printed | SPINE Resource Specification 1.3.0 §4.2.42, Table 354 |
| SmartEnergyAppliance | clause not printed | SPINE Resource Specification 1.3.0 §4.2.43, Table 354 |
| SolarDHWStorage | clause not printed | SPINE Resource Specification 1.3.0 §4.2.44, Table 354 |
| SolarThermalCircuit | clause not printed | SPINE Resource Specification 1.3.0 §4.2.45, Table 354 |
| SubMeterElectricity | clause not printed | SPINE Resource Specification 1.3.0 §4.2.46, Table 354 |
| TemperatureSensor | clause not printed | SPINE Resource Specification 1.3.0 §4.2.47, Table 354 |
| Washer | clause not printed | SPINE Resource Specification 1.3.0 §4.2.48, Table 354 |

### Feature types

| type | meaning (own words) | clause |
| --- | --- | --- |
| ActuatorLevel | none; not stated | §4.3.1 |
| ActuatorSwitch | none; not stated | §4.3.2 |
| Alarm | Threshold; not stated | §4.3.3 |
| Bill | none; Rules speak of a feature server (sign of totals) and of a client write. No actor. | §4.3.4 |
| DataTunneling | none; An instance with role server decides which header.purposeId values are permitted. Call only. | §4.3.5 |
| DeviceClassification | none; not stated | §4.3.6 |
| DeviceConfiguration | none; A server accepts or declines a value change. | §4.3.7 |
| DeviceDiagnosis | none; A device notifies subscribed clients. | §4.3.8 |
| DirectControl | OperatingConstraints, PowerSequences, SmartEnergyManagementPs; A server accepts or declines writes from an appropriate client. | §4.3.9 |
| ElectricalConnection | Measurement; not stated | §4.3.10 |
| Generic | none; SHALL be used only as a client feature. From it, reads, writes, and calls toward servers are all allowed. | §4.3.11 |
| HVAC | PowerSequences, Setpoint, SmartEnergyManagementPs, TimeTable; A server accepts or declines changes from an appropriate client. Definition continues past page 124. | §4.3.12 |
| ActuatorLevel | clause not printed | SPINE Resource Specification 1.3.0 §4.3.1, Table 355 |
| ActuatorSwitch | clause not printed | SPINE Resource Specification 1.3.0 §4.3.2, Table 355 |
| Alarm | clause not printed | SPINE Resource Specification 1.3.0 §4.3.3, Table 355 |
| Bill | clause not printed | SPINE Resource Specification 1.3.0 §4.3.4, Table 355 |
| DataTunneling | clause not printed | SPINE Resource Specification 1.3.0 §4.3.5, Table 355 |
| DeviceClassification | clause not printed | SPINE Resource Specification 1.3.0 §4.3.6, Table 355 |
| DeviceConfiguration | clause not printed | SPINE Resource Specification 1.3.0 §4.3.7, Table 355 |
| DeviceDiagnosis | clause not printed | SPINE Resource Specification 1.3.0 §4.3.8, Table 355 |
| DirectControl | clause not printed | SPINE Resource Specification 1.3.0 §4.3.9, Table 355 |
| ElectricalConnection | clause not printed | SPINE Resource Specification 1.3.0 §4.3.10, Table 355 |
| Generic | clause not printed | SPINE Resource Specification 1.3.0 §4.3.11, Table 355 |
| HVAC | clause not printed | SPINE Resource Specification 1.3.0 §4.3.12, Table 355 |
| Identification | clause not printed | SPINE Resource Specification 1.3.0 §4.3.13, Table 355 |
| IncentiveTable | clause not printed | SPINE Resource Specification 1.3.0 §4.3.14, Table 355 |
| LoadControl | clause not printed | SPINE Resource Specification 1.3.0 §4.3.15, Table 355 |
| Measurement | clause not printed | SPINE Resource Specification 1.3.0 §4.3.16, Table 355 |
| Messaging | clause not printed | SPINE Resource Specification 1.3.0 §4.3.17, Table 355 |
| NetworkManagement | clause not printed | SPINE Resource Specification 1.3.0 §4.3.18, Table 355 |
| NodeManagement | clause not printed | SPINE Resource Specification 1.3.0 §4.3.19, Table 355 |
| OperatingConstraints | clause not printed | SPINE Resource Specification 1.3.0 §4.3.20, Table 355 |
| PowerSequences | clause not printed | SPINE Resource Specification 1.3.0 §4.3.21, Table 355 |
| Sensing | clause not printed | SPINE Resource Specification 1.3.0 §4.3.22, Table 355 |
| Setpoint | clause not printed | SPINE Resource Specification 1.3.0 §4.3.23, Table 355 |
| SmartEnergyManagementPs | clause not printed | SPINE Resource Specification 1.3.0 §4.3.24, Table 355 |
| StateInformation | clause not printed | SPINE Resource Specification 1.3.0 §4.3.25, Table 355 |
| SupplyCondition | clause not printed | SPINE Resource Specification 1.3.0 §4.3.26, Table 355 |
| TariffInformation | clause not printed | SPINE Resource Specification 1.3.0 §4.3.27, Table 355 |
| TaskManagement | clause not printed | SPINE Resource Specification 1.3.0 §4.3.28, Table 355 |
| Threshold | clause not printed | SPINE Resource Specification 1.3.0 §4.3.29, Table 355 |
| TimeInformation | clause not printed | SPINE Resource Specification 1.3.0 §4.3.30, Table 355 |
| TimeSeries | clause not printed | SPINE Resource Specification 1.3.0 §4.3.31, Table 355 |
| TimeTable | clause not printed | SPINE Resource Specification 1.3.0 §4.3.32, Table 355 |

## Functions per feature

| feature | function | clause |
| --- | --- | --- |
| ActuatorLevel | actuatorLevelData | SPINE Resource Specification 1.3.0 §4.3.1.2, §4.3.1.4.1 |
| ActuatorLevel | actuatorLevelDataElements | SPINE Resource Specification 1.3.0 |
| ActuatorLevel | actuatorLevelDescriptionData | SPINE Resource Specification 1.3.0 §4.3.1.5.1 |
| ActuatorLevel | actuatorLevelDescriptionDataElements | SPINE Resource Specification 1.3.0 |
| ActuatorLevel | not in the sources | SPINE Resource Specification 1.3.0 |
| ActuatorSwitch | actuatorSwitchData | SPINE Resource Specification 1.3.0 §4.3.2.2, §4.3.2.4.1 |
| ActuatorSwitch | actuatorSwitchDataElements | SPINE Resource Specification 1.3.0 |
| ActuatorSwitch | actuatorSwitchDescriptionData | SPINE Resource Specification 1.3.0 |
| ActuatorSwitch | actuatorSwitchDescriptionDataElements | SPINE Resource Specification 1.3.0 |
| ActuatorSwitch | not in the sources | SPINE Resource Specification 1.3.0 |
| Alarm | alarmData | SPINE Resource Specification 1.3.0 |
| Alarm | alarmDataElements | SPINE Resource Specification 1.3.0 |
| Alarm | alarmListData | SPINE Resource Specification 1.3.0 §5.3.3.2.3 |
| Alarm | alarmListDataSelectors | SPINE Resource Specification 1.3.0 |
| Alarm | not in the sources | SPINE Resource Specification 1.3.0 |
| Bill | billConstraintsData | SPINE Resource Specification 1.3.0 |
| Bill | billConstraintsDataElements | SPINE Resource Specification 1.3.0 |
| Bill | billConstraintsListData | SPINE Resource Specification 1.3.0 §5.3.4.3.3 |
| Bill | billConstraintsListDataSelectors | SPINE Resource Specification 1.3.0 |
| Bill | billData | SPINE Resource Specification 1.3.0 |
| Bill | billDataElements | SPINE Resource Specification 1.3.0 |
| Bill | billDescriptionData | SPINE Resource Specification 1.3.0 |
| Bill | billDescriptionDataElements | SPINE Resource Specification 1.3.0 |
| Bill | billDescriptionListData | SPINE Resource Specification 1.3.0 §5.3.4.4.3 |
| Bill | billDescriptionListDataSelectors | SPINE Resource Specification 1.3.0 |
| Bill | billListData | SPINE Resource Specification 1.3.0 §5.3.4.2.3 |
| Bill | billListDataSelectors | SPINE Resource Specification 1.3.0 |
| Bill | not in the sources | SPINE Resource Specification 1.3.0 |
| BindingManagement | bindingManagementDeleteCall | SPINE Resource Specification 1.3.0 Table 188, §5.3.5.4.1, §5.3.5.4.3 |
| BindingManagement | bindingManagementDeleteCallElements | SPINE Resource Specification 1.3.0 |
| BindingManagement | bindingManagementEntryData | SPINE Resource Specification 1.3.0 |
| BindingManagement | bindingManagementEntryDataElements | SPINE Resource Specification 1.3.0 |
| BindingManagement | bindingManagementEntryListData | SPINE Resource Specification 1.3.0 §5.3.5.2.3 |
| BindingManagement | bindingManagementEntryListDataSelectors | SPINE Resource Specification 1.3.0 |
| BindingManagement | bindingManagementRequestCall | SPINE Resource Specification 1.3.0 |
| BindingManagement | bindingManagementRequestCallElements | SPINE Resource Specification 1.3.0 |
| BindingManagement | not in the sources | SPINE Resource Specification 1.3.0 |
| CommandCommonDefinitions | actuatorLevelData | SPINE Resource Specification 1.3.0 |
| CommandCommonDefinitions | actuatorLevelDescriptionData | SPINE Resource Specification 1.3.0 |
| CommandCommonDefinitions | actuatorSwitchData | SPINE Resource Specification 1.3.0 |
| CommandCommonDefinitions | actuatorSwitchDescriptionData | SPINE Resource Specification 1.3.0 |
| CommandCommonDefinitions | alarmListData | SPINE Resource Specification 1.3.0 |
| CommandCommonDefinitions | billConstraintsListData | SPINE Resource Specification 1.3.0 |
| CommandCommonDefinitions | billDescriptionListData | SPINE Resource Specification 1.3.0 |
| CommandCommonDefinitions | billListData | SPINE Resource Specification 1.3.0 |
| CommandCommonDefinitions | bindingManagementDeleteCall | SPINE Resource Specification 1.3.0 |
| CommandCommonDefinitions | bindingManagementEntryListData | SPINE Resource Specification 1.3.0 |
| CommandCommonDefinitions | bindingManagementRequestCall | SPINE Resource Specification 1.3.0 |
| CommandCommonDefinitions | commodityListData | SPINE Resource Specification 1.3.0 |
| CommandCommonDefinitions | dataTunnelingCall | SPINE Resource Specification 1.3.0 |
| CommandCommonDefinitions | deviceClassificationManufacturerData | SPINE Resource Specification 1.3.0 |
| CommandCommonDefinitions | deviceClassificationUserData | SPINE Resource Specification 1.3.0 |
| CommandCommonDefinitions | deviceConfigurationKeyValueConstraintsListData | SPINE Resource Specification 1.3.0 |
| CommandCommonDefinitions | deviceConfigurationKeyValueDescriptionListData | SPINE Resource Specification 1.3.0 |
| CommandCommonDefinitions | deviceConfigurationKeyValueListData | SPINE Resource Specification 1.3.0 |
| CommandCommonDefinitions | deviceDiagnosisHeartbeatData | SPINE Resource Specification 1.3.0 |
| CommandCommonDefinitions | deviceDiagnosisServiceData | SPINE Resource Specification 1.3.0 |
| CommandCommonDefinitions | deviceDiagnosisStateData | SPINE Resource Specification 1.3.0 |
| CommandCommonDefinitions | directControlActivityListData | SPINE Resource Specification 1.3.0 |
| CommandCommonDefinitions | directControlDescriptionData | SPINE Resource Specification 1.3.0 |
| CommandCommonDefinitions | electricalConnectionCharacteristicListData | SPINE Resource Specification 1.3.0 |
| CommandCommonDefinitions | electricalConnectionDescriptionListData | SPINE Resource Specification 1.3.0 |
| CommandCommonDefinitions | electricalConnectionParameterDescriptionListData | SPINE Resource Specification 1.3.0 |
| CommandCommonDefinitions | electricalConnectionPermittedValueSetListData | SPINE Resource Specification 1.3.0 |
| CommandCommonDefinitions | electricalConnectionStateListData | SPINE Resource Specification 1.3.0 |
| CommandCommonDefinitions | hvacOperationModeDescriptionListData | SPINE Resource Specification 1.3.0 |
| CommandCommonDefinitions | hvacOverrunDescriptionListData | SPINE Resource Specification 1.3.0 |
| CommandCommonDefinitions | hvacOverrunListData | SPINE Resource Specification 1.3.0 |
| CommandCommonDefinitions | hvacSystemFunctionDescriptionListData | SPINE Resource Specification 1.3.0 |
| CommandCommonDefinitions | hvacSystemFunctionListData | SPINE Resource Specification 1.3.0 |
| CommandCommonDefinitions | hvacSystemFunctionOperationModeRelationListData | SPINE Resource Specification 1.3.0 |
| CommandCommonDefinitions | hvacSystemFunctionPowerSequenceRelationListData | SPINE Resource Specification 1.3.0 |
| CommandCommonDefinitions | hvacSystemFunctionSetpointRelationListData | SPINE Resource Specification 1.3.0 |
| CommandCommonDefinitions | identificationListData | SPINE Resource Specification 1.3.0 |
| CommandCommonDefinitions | incentiveDescriptionListData | SPINE Resource Specification 1.3.0 |
| CommandCommonDefinitions | incentiveListData | SPINE Resource Specification 1.3.0 |
| CommandCommonDefinitions | incentiveTableConstraintsData | SPINE Resource Specification 1.3.0 |
| CommandCommonDefinitions | incentiveTableData | SPINE Resource Specification 1.3.0 |
| CommandCommonDefinitions | incentiveTableDescriptionData | SPINE Resource Specification 1.3.0 |
| CommandCommonDefinitions | loadControlEventListData | SPINE Resource Specification 1.3.0 |
| CommandCommonDefinitions | loadControlLimitConstraintsListData | SPINE Resource Specification 1.3.0 |
| CommandCommonDefinitions | loadControlLimitDescriptionListData | SPINE Resource Specification 1.3.0 |
| CommandCommonDefinitions | loadControlLimitListData | SPINE Resource Specification 1.3.0 |
| CommandCommonDefinitions | loadControlNodeData | SPINE Resource Specification 1.3.0 |
| CommandCommonDefinitions | loadControlStateListData | SPINE Resource Specification 1.3.0 |
| CommandCommonDefinitions | measurementConstraintsListData | SPINE Resource Specification 1.3.0 |
| CommandCommonDefinitions | measurementDescriptionListData | SPINE Resource Specification 1.3.0 |
| CommandCommonDefinitions | measurementListData | SPINE Resource Specification 1.3.0 |
| CommandCommonDefinitions | measurementSeriesListData | SPINE Resource Specification 1.3.0 |
| CommandCommonDefinitions | measurementThresholdRelationListData | SPINE Resource Specification 1.3.0 |
| CommandCommonDefinitions | messagingListData | SPINE Resource Specification 1.3.0 |
| CommandCommonDefinitions | networkManagementAbortCall | SPINE Resource Specification 1.3.0 |
| CommandCommonDefinitions | networkManagementAddNodeCall | SPINE Resource Specification 1.3.0 |
| CommandCommonDefinitions | networkManagementDeviceDescriptionListData | SPINE Resource Specification 1.3.0 |
| CommandCommonDefinitions | networkManagementDiscoverCall | SPINE Resource Specification 1.3.0 |
| CommandCommonDefinitions | networkManagementEntityDescriptionListData | SPINE Resource Specification 1.3.0 |
| CommandCommonDefinitions | networkManagementFeatureDescriptionListData | SPINE Resource Specification 1.3.0 |
| CommandCommonDefinitions | networkManagementJoiningModeData | SPINE Resource Specification 1.3.0 |
| CommandCommonDefinitions | networkManagementModifyNodeCall | SPINE Resource Specification 1.3.0 |
| CommandCommonDefinitions | networkManagementProcessStateData | SPINE Resource Specification 1.3.0 |
| CommandCommonDefinitions | networkManagementRemoveNodeCall | SPINE Resource Specification 1.3.0 |
| CommandCommonDefinitions | networkManagementReportCandidateData | SPINE Resource Specification 1.3.0 |
| CommandCommonDefinitions | networkManagementScanNetworkCall | SPINE Resource Specification 1.3.0 |
| CommandCommonDefinitions | nodeManagementBindingData | SPINE Resource Specification 1.3.0 |
| CommandCommonDefinitions | nodeManagementBindingDeleteCall | SPINE Resource Specification 1.3.0 |
| CommandCommonDefinitions | nodeManagementBindingRequestCall | SPINE Resource Specification 1.3.0 |
| CommandCommonDefinitions | nodeManagementDestinationListData | SPINE Resource Specification 1.3.0 |
| CommandCommonDefinitions | nodeManagementDetailedDiscoveryData | SPINE Resource Specification 1.3.0 |
| CommandCommonDefinitions | nodeManagementSubscriptionData | SPINE Resource Specification 1.3.0 |
| CommandCommonDefinitions | nodeManagementSubscriptionDeleteCall | SPINE Resource Specification 1.3.0 |
| CommandCommonDefinitions | nodeManagementSubscriptionRequestCall | SPINE Resource Specification 1.3.0 |
| CommandCommonDefinitions | nodeManagementUseCaseData | SPINE Resource Specification 1.3.0 |
| CommandCommonDefinitions | not in the sources | SPINE Resource Specification 1.3.0 |
| CommandCommonDefinitions | operatingConstraintsDurationListData | SPINE Resource Specification 1.3.0 |
| CommandCommonDefinitions | operatingConstraintsInterruptListData | SPINE Resource Specification 1.3.0 |
| CommandCommonDefinitions | operatingConstraintsPowerDescriptionListData | SPINE Resource Specification 1.3.0 |
| CommandCommonDefinitions | operatingConstraintsPowerLevelListData | SPINE Resource Specification 1.3.0 |
| CommandCommonDefinitions | operatingConstraintsPowerRangeListData | SPINE Resource Specification 1.3.0 |
| CommandCommonDefinitions | operatingConstraintsResumeImplicationListData | SPINE Resource Specification 1.3.0 |
| CommandCommonDefinitions | powerSequenceAlternativesRelationListData | SPINE Resource Specification 1.3.0 |
| CommandCommonDefinitions | powerSequenceDescriptionListData | SPINE Resource Specification 1.3.0 |
| CommandCommonDefinitions | powerSequenceNodeScheduleInformationData | SPINE Resource Specification 1.3.0 |
| CommandCommonDefinitions | powerSequencePriceCalculationRequestCall | SPINE Resource Specification 1.3.0 |
| CommandCommonDefinitions | powerSequencePriceListData | SPINE Resource Specification 1.3.0 |
| CommandCommonDefinitions | powerSequenceScheduleConfigurationRequestCall | SPINE Resource Specification 1.3.0 |
| CommandCommonDefinitions | powerSequenceScheduleConstraintsListData | SPINE Resource Specification 1.3.0 |
| CommandCommonDefinitions | powerSequenceScheduleListData | SPINE Resource Specification 1.3.0 |
| CommandCommonDefinitions | powerSequenceSchedulePreferenceListData | SPINE Resource Specification 1.3.0 |
| CommandCommonDefinitions | powerSequenceStateListData | SPINE Resource Specification 1.3.0 |
| CommandCommonDefinitions | powerTimeSlotScheduleConstraintsListData | SPINE Resource Specification 1.3.0 |
| CommandCommonDefinitions | powerTimeSlotScheduleListData | SPINE Resource Specification 1.3.0 |
| CommandCommonDefinitions | powerTimeSlotValueListData | SPINE Resource Specification 1.3.0 |
| CommandCommonDefinitions | resultData | SPINE Resource Specification 1.3.0 |
| CommandCommonDefinitions | sensingDescriptionData | SPINE Resource Specification 1.3.0 |
| CommandCommonDefinitions | sensingListData | SPINE Resource Specification 1.3.0 |
| CommandCommonDefinitions | sessionIdentificationListData | SPINE Resource Specification 1.3.0 |
| CommandCommonDefinitions | sessionMeasurementRelationListData | SPINE Resource Specification 1.3.0 |
| CommandCommonDefinitions | setpointConstraintsListData | SPINE Resource Specification 1.3.0 |
| CommandCommonDefinitions | setpointDescriptionListData | SPINE Resource Specification 1.3.0 |
| CommandCommonDefinitions | setpointListData | SPINE Resource Specification 1.3.0 |
| CommandCommonDefinitions | smartEnergyManagementPsConfigurationRequestCall | SPINE Resource Specification 1.3.0 |
| CommandCommonDefinitions | smartEnergyManagementPsData | SPINE Resource Specification 1.3.0 |
| CommandCommonDefinitions | smartEnergyManagementPsPriceCalculationRequestCall | SPINE Resource Specification 1.3.0 |
| CommandCommonDefinitions | smartEnergyManagementPsPriceData | SPINE Resource Specification 1.3.0 |
| CommandCommonDefinitions | specificationVersionListData | SPINE Resource Specification 1.3.0 |
| CommandCommonDefinitions | stateInformationListData | SPINE Resource Specification 1.3.0 |
| CommandCommonDefinitions | subscriptionManagementDeleteCall | SPINE Resource Specification 1.3.0 |
| CommandCommonDefinitions | subscriptionManagementEntryListData | SPINE Resource Specification 1.3.0 |
| CommandCommonDefinitions | subscriptionManagementRequestCall | SPINE Resource Specification 1.3.0 |
| CommandCommonDefinitions | supplyConditionDescriptionListData | SPINE Resource Specification 1.3.0 |
| CommandCommonDefinitions | supplyConditionListData | SPINE Resource Specification 1.3.0 |
| CommandCommonDefinitions | supplyConditionThresholdRelationListData | SPINE Resource Specification 1.3.0 |
| CommandCommonDefinitions | tariffBoundaryRelationListData | SPINE Resource Specification 1.3.0 |
| CommandCommonDefinitions | tariffDescriptionListData | SPINE Resource Specification 1.3.0 |
| CommandCommonDefinitions | tariffListData | SPINE Resource Specification 1.3.0 |
| CommandCommonDefinitions | tariffOverallConstraintsData | SPINE Resource Specification 1.3.0 |
| CommandCommonDefinitions | tariffTierRelationListData | SPINE Resource Specification 1.3.0 |
| CommandCommonDefinitions | taskManagementJobDescriptionListData | SPINE Resource Specification 1.3.0 |
| CommandCommonDefinitions | taskManagementJobListData | SPINE Resource Specification 1.3.0 |
| CommandCommonDefinitions | taskManagementJobRelationListData | SPINE Resource Specification 1.3.0 |
| CommandCommonDefinitions | taskManagementOverviewData | SPINE Resource Specification 1.3.0 |
| CommandCommonDefinitions | thresholdConstraintsListData | SPINE Resource Specification 1.3.0 |
| CommandCommonDefinitions | thresholdDescriptionListData | SPINE Resource Specification 1.3.0 |
| CommandCommonDefinitions | thresholdListData | SPINE Resource Specification 1.3.0 |
| CommandCommonDefinitions | tierBoundaryDescriptionListData | SPINE Resource Specification 1.3.0 |
| CommandCommonDefinitions | tierBoundaryListData | SPINE Resource Specification 1.3.0 |
| CommandCommonDefinitions | tierDescriptionListData | SPINE Resource Specification 1.3.0 |
| CommandCommonDefinitions | tierIncentiveRelationListData | SPINE Resource Specification 1.3.0 |
| CommandCommonDefinitions | tierListData | SPINE Resource Specification 1.3.0 |
| CommandCommonDefinitions | timeDistributorData | SPINE Resource Specification 1.3.0 |
| CommandCommonDefinitions | timeDistributorEnquiryCall | SPINE Resource Specification 1.3.0 |
| CommandCommonDefinitions | timeInformationData | SPINE Resource Specification 1.3.0 |
| CommandCommonDefinitions | timePrecisionData | SPINE Resource Specification 1.3.0 |
| CommandCommonDefinitions | timeSeriesConstraintsListData | SPINE Resource Specification 1.3.0 |
| CommandCommonDefinitions | timeSeriesDescriptionListData | SPINE Resource Specification 1.3.0 |
| CommandCommonDefinitions | timeSeriesListData | SPINE Resource Specification 1.3.0 |
| CommandCommonDefinitions | timeTableConstraintsListData | SPINE Resource Specification 1.3.0 |
| CommandCommonDefinitions | timeTableDescriptionListData | SPINE Resource Specification 1.3.0 |
| CommandCommonDefinitions | timeTableListData | SPINE Resource Specification 1.3.0 |
| CommandCommonDefinitions | useCaseInformationListData | SPINE Resource Specification 1.3.0 |
| CommandFrame | cmdControl | SPINE Resource Specification 1.3.0 |
| CommandFrame | filter | SPINE Resource Specification 1.3.0 |
| CommandFrame | not in the sources | SPINE Resource Specification 1.3.0 |
| CommonDataTypes | not in the sources | SPINE Resource Specification 1.3.0 |
| Datagram | datagram | SPINE Resource Specification 1.3.0 |
| Datagram | header | SPINE Resource Specification 1.3.0 |
| Datagram | not in the sources | SPINE Resource Specification 1.3.0 |
| Datagram | payload | SPINE Resource Specification 1.3.0 |
| DataTunneling | dataTunnelingCall | SPINE Resource Specification 1.3.0 §4.3.5.2, §4.3.5.5 |
| DataTunneling | dataTunnelingCallElements | SPINE Resource Specification 1.3.0 |
| DataTunneling | not in the sources | SPINE Resource Specification 1.3.0 |
| DeviceClassification | deviceClassificationManufacturerData | SPINE Resource Specification 1.3.0 §4.3.6.2, §4.3.6.4.1, §4.3.6.4.2 |
| DeviceClassification | deviceClassificationManufacturerDataElements | SPINE Resource Specification 1.3.0 |
| DeviceClassification | deviceClassificationUserData | SPINE Resource Specification 1.3.0 §4.3.6.5.1, §4.3.6.5.2 |
| DeviceClassification | deviceClassificationUserDataElements | SPINE Resource Specification 1.3.0 |
| DeviceClassification | not in the sources | SPINE Resource Specification 1.3.0 |
| DeviceConfiguration | deviceConfigurationKeyValueConstraintsData | SPINE Resource Specification 1.3.0 |
| DeviceConfiguration | deviceConfigurationKeyValueConstraintsDataElements | SPINE Resource Specification 1.3.0 |
| DeviceConfiguration | deviceConfigurationKeyValueConstraintsListData | SPINE Resource Specification 1.3.0 §5.3.8.4.1 |
| DeviceConfiguration | deviceConfigurationKeyValueConstraintsListDataSelectors | SPINE Resource Specification 1.3.0 |
| DeviceConfiguration | deviceConfigurationKeyValueData | SPINE Resource Specification 1.3.0 |
| DeviceConfiguration | deviceConfigurationKeyValueDataElements | SPINE Resource Specification 1.3.0 |
| DeviceConfiguration | deviceConfigurationKeyValueDescriptionData | SPINE Resource Specification 1.3.0 |
| DeviceConfiguration | deviceConfigurationKeyValueDescriptionDataElements | SPINE Resource Specification 1.3.0 |
| DeviceConfiguration | deviceConfigurationKeyValueDescriptionListData | SPINE Resource Specification 1.3.0 §5.3.8.3.3 |
| DeviceConfiguration | deviceConfigurationKeyValueDescriptionListDataSelectors | SPINE Resource Specification 1.3.0 |
| DeviceConfiguration | deviceConfigurationKeyValueListData | SPINE Resource Specification 1.3.0 §5.3.8.2.3 |
| DeviceConfiguration | deviceConfigurationKeyValueListDataSelectors | SPINE Resource Specification 1.3.0 |
| DeviceConfiguration | not in the sources | SPINE Resource Specification 1.3.0 |
| DeviceDiagnosis | deviceDiagnosisHeartbeatData | SPINE Resource Specification 1.3.0 §4.3.8.5.1, §4.3.8.5.2 |
| DeviceDiagnosis | deviceDiagnosisHeartbeatDataElements | SPINE Resource Specification 1.3.0 |
| DeviceDiagnosis | deviceDiagnosisServiceData | SPINE Resource Specification 1.3.0 §4.3.8.6.1, §4.3.8.6.2 |
| DeviceDiagnosis | deviceDiagnosisServiceDataElements | SPINE Resource Specification 1.3.0 |
| DeviceDiagnosis | deviceDiagnosisStateData | SPINE Resource Specification 1.3.0 §4.3.8.2, §4.3.8.4.1, §4.3.8.4.2 |
| DeviceDiagnosis | deviceDiagnosisStateDataElements | SPINE Resource Specification 1.3.0 |
| DeviceDiagnosis | not in the sources | SPINE Resource Specification 1.3.0 |
| DirectControl | directControlActivityData | SPINE Resource Specification 1.3.0 |
| DirectControl | directControlActivityDataElements | SPINE Resource Specification 1.3.0 |
| DirectControl | directControlActivityListData | SPINE Resource Specification 1.3.0 Table 204, Table 205 |
| DirectControl | directControlActivityListDataSelectors | SPINE Resource Specification 1.3.0 |
| DirectControl | directControlDescriptionData | SPINE Resource Specification 1.3.0 |
| DirectControl | directControlDescriptionDataElements | SPINE Resource Specification 1.3.0 |
| DirectControl | not in the sources | SPINE Resource Specification 1.3.0 |
| ElectricalConnection | electricalConnectionCharacteristicData | SPINE Resource Specification 1.3.0 |
| ElectricalConnection | electricalConnectionCharacteristicDataElements | SPINE Resource Specification 1.3.0 |
| ElectricalConnection | electricalConnectionCharacteristicListData | SPINE Resource Specification 1.3.0 Table 59, Table 60 |
| ElectricalConnection | electricalConnectionCharacteristicListDataSelectors | SPINE Resource Specification 1.3.0 |
| ElectricalConnection | electricalConnectionDescriptionData | SPINE Resource Specification 1.3.0 |
| ElectricalConnection | electricalConnectionDescriptionDataElements | SPINE Resource Specification 1.3.0 |
| ElectricalConnection | electricalConnectionDescriptionListData | SPINE Resource Specification 1.3.0 Table 63, Table 217 |
| ElectricalConnection | electricalConnectionDescriptionListDataSelectors | SPINE Resource Specification 1.3.0 |
| ElectricalConnection | electricalConnectionParameterDescriptionData | SPINE Resource Specification 1.3.0 |
| ElectricalConnection | electricalConnectionParameterDescriptionDataElements | SPINE Resource Specification 1.3.0 |
| ElectricalConnection | electricalConnectionParameterDescriptionListData | SPINE Resource Specification 1.3.0 Table 52, Table 207 |
| ElectricalConnection | electricalConnectionParameterDescriptionListDataSelectors | SPINE Resource Specification 1.3.0 |
| ElectricalConnection | electricalConnectionPermittedValueSetData | SPINE Resource Specification 1.3.0 |
| ElectricalConnection | electricalConnectionPermittedValueSetDataElements | SPINE Resource Specification 1.3.0 |
| ElectricalConnection | electricalConnectionPermittedValueSetListData | SPINE Resource Specification 1.3.0 |
| ElectricalConnection | electricalConnectionPermittedValueSetListDataSelectors | SPINE Resource Specification 1.3.0 |
| ElectricalConnection | electricalConnectionStateData | SPINE Resource Specification 1.3.0 |
| ElectricalConnection | electricalConnectionStateDataElements | SPINE Resource Specification 1.3.0 |
| ElectricalConnection | electricalConnectionStateListData | SPINE Resource Specification 1.3.0 |
| ElectricalConnection | electricalConnectionStateListDataSelectors | SPINE Resource Specification 1.3.0 |
| ElectricalConnection | not in the sources | SPINE Resource Specification 1.3.0 |
| Generic | (none) | SPINE Resource Specification 1.3.0 §4.3.11 |
| HVAC | hvacOperationModeDescriptionData | SPINE Resource Specification 1.3.0 |
| HVAC | hvacOperationModeDescriptionDataElements | SPINE Resource Specification 1.3.0 |
| HVAC | hvacOperationModeDescriptionListData | SPINE Resource Specification 1.3.0 |
| HVAC | hvacOperationModeDescriptionListDataSelectors | SPINE Resource Specification 1.3.0 |
| HVAC | hvacOverrunData | SPINE Resource Specification 1.3.0 |
| HVAC | hvacOverrunDataElements | SPINE Resource Specification 1.3.0 |
| HVAC | hvacOverrunDescriptionData | SPINE Resource Specification 1.3.0 |
| HVAC | hvacOverrunDescriptionDataElements | SPINE Resource Specification 1.3.0 |
| HVAC | hvacOverrunDescriptionListData | SPINE Resource Specification 1.3.0 Table 228 |
| HVAC | hvacOverrunDescriptionListDataSelectors | SPINE Resource Specification 1.3.0 |
| HVAC | hvacOverrunListData | SPINE Resource Specification 1.3.0 |
| HVAC | hvacOverrunListData related to hvacSystemFunctionListData | SPINE Resource Specification 1.3.0 §4.3.12.12, Table 76 |
| HVAC | hvacOverrunListDataSelectors | SPINE Resource Specification 1.3.0 |
| HVAC | hvacSystemFunctionData | SPINE Resource Specification 1.3.0 |
| HVAC | hvacSystemFunctionDataElements | SPINE Resource Specification 1.3.0 |
| HVAC | hvacSystemFunctionDescriptionData | SPINE Resource Specification 1.3.0 |
| HVAC | hvacSystemFunctionDescriptionDataElements | SPINE Resource Specification 1.3.0 |
| HVAC | hvacSystemFunctionDescriptionListData | SPINE Resource Specification 1.3.0 |
| HVAC | hvacSystemFunctionDescriptionListDataSelectors | SPINE Resource Specification 1.3.0 |
| HVAC | hvacSystemFunctionListData | SPINE Resource Specification 1.3.0 |
| HVAC | hvacSystemFunctionListDataSelectors | SPINE Resource Specification 1.3.0 |
| HVAC | hvacSystemFunctionOperationModeRelationData | SPINE Resource Specification 1.3.0 |
| HVAC | hvacSystemFunctionOperationModeRelationDataElements | SPINE Resource Specification 1.3.0 |
| HVAC | hvacSystemFunctionOperationModeRelationListData | SPINE Resource Specification 1.3.0 |
| HVAC | hvacSystemFunctionOperationModeRelationListDataSelectors | SPINE Resource Specification 1.3.0 |
| HVAC | hvacSystemFunctionPowerSequenceRelationData | SPINE Resource Specification 1.3.0 |
| HVAC | hvacSystemFunctionPowerSequenceRelationDataElements | SPINE Resource Specification 1.3.0 |
| HVAC | hvacSystemFunctionPowerSequenceRelationListData | SPINE Resource Specification 1.3.0 |
| HVAC | hvacSystemFunctionPowerSequenceRelationListDataSelectors | SPINE Resource Specification 1.3.0 |
| HVAC | hvacSystemFunctionSetpointRelationData | SPINE Resource Specification 1.3.0 |
| HVAC | hvacSystemFunctionSetpointRelationDataElements | SPINE Resource Specification 1.3.0 |
| HVAC | hvacSystemFunctionSetpointRelationListData | SPINE Resource Specification 1.3.0 |
| HVAC | hvacSystemFunctionSetpointRelationListDataSelectors | SPINE Resource Specification 1.3.0 |
| HVAC | not in the sources | SPINE Resource Specification 1.3.0 |
| Identification | identificationData | SPINE Resource Specification 1.3.0 |
| Identification | identificationDataElements | SPINE Resource Specification 1.3.0 |
| Identification | identificationListData | SPINE Resource Specification 1.3.0 Table 77 |
| Identification | identificationListDataSelectors | SPINE Resource Specification 1.3.0 |
| Identification | not in the sources | SPINE Resource Specification 1.3.0 |
| Identification | sessionIdentificationData | SPINE Resource Specification 1.3.0 |
| Identification | sessionIdentificationDataElements | SPINE Resource Specification 1.3.0 |
| Identification | sessionIdentificationListData | SPINE Resource Specification 1.3.0 |
| Identification | sessionIdentificationListDataSelectors | SPINE Resource Specification 1.3.0 |
| Identification | sessionMeasurementRelationData | SPINE Resource Specification 1.3.0 |
| Identification | sessionMeasurementRelationDataElements | SPINE Resource Specification 1.3.0 |
| Identification | sessionMeasurementRelationListData | SPINE Resource Specification 1.3.0 |
| Identification | sessionMeasurementRelationListDataSelectors | SPINE Resource Specification 1.3.0 |
| IncentiveTable | (schema) | SPINE Resource Specification 1.3.0 |
| IncentiveTable | descriptive section | SPINE Resource Specification 1.3.0 §4.3.14.7 |
| IncentiveTable | incentiveTable | SPINE Resource Specification 1.3.0 §5.2.1.1 |
| IncentiveTable | incentiveTableConstraints | SPINE Resource Specification 1.3.0 §5.2.1.1 |
| IncentiveTable | incentiveTableConstraintsData | SPINE Resource Specification 1.3.0 §5.2.1.4.3 |
| IncentiveTable | incentiveTableConstraintsDataElements | SPINE Resource Specification 1.3.0 |
| IncentiveTable | incentiveTableConstraintsDataSelectors | SPINE Resource Specification 1.3.0 |
| IncentiveTable | incentiveTableData | SPINE Resource Specification 1.3.0 §5.2.1.2.3 |
| IncentiveTable | incentiveTableDataElements | SPINE Resource Specification 1.3.0 |
| IncentiveTable | incentiveTableDataSelectors | SPINE Resource Specification 1.3.0 |
| IncentiveTable | incentiveTableDescription | SPINE Resource Specification 1.3.0 §5.2.1.1 |
| IncentiveTable | incentiveTableDescriptionData | SPINE Resource Specification 1.3.0 §5.2.1.3.3 |
| IncentiveTable | incentiveTableDescriptionDataElements | SPINE Resource Specification 1.3.0 |
| IncentiveTable | incentiveTableDescriptionDataSelectors | SPINE Resource Specification 1.3.0 |
| LoadControl | descriptive section | SPINE Resource Specification 1.3.0 §4.3.15.10 |
| LoadControl | loadControlEventData | SPINE Resource Specification 1.3.0 |
| LoadControl | loadControlEventDataElements | SPINE Resource Specification 1.3.0 |
| LoadControl | loadControlEventListData | SPINE Resource Specification 1.3.0 |
| LoadControl | loadControlEventListDataSelectors | SPINE Resource Specification 1.3.0 |
| LoadControl | loadControlLimitConstraintsData | SPINE Resource Specification 1.3.0 |
| LoadControl | loadControlLimitConstraintsDataElements | SPINE Resource Specification 1.3.0 |
| LoadControl | loadControlLimitConstraintsListData | SPINE Resource Specification 1.3.0 |
| LoadControl | loadControlLimitConstraintsListDataSelectors | SPINE Resource Specification 1.3.0 |
| LoadControl | loadControlLimitData | SPINE Resource Specification 1.3.0 |
| LoadControl | loadControlLimitDataElements | SPINE Resource Specification 1.3.0 |
| LoadControl | loadControlLimitDescriptionData | SPINE Resource Specification 1.3.0 |
| LoadControl | loadControlLimitDescriptionDataElements | SPINE Resource Specification 1.3.0 |
| LoadControl | loadControlLimitDescriptionListData | SPINE Resource Specification 1.3.0 |
| LoadControl | loadControlLimitDescriptionListDataSelectors | SPINE Resource Specification 1.3.0 |
| LoadControl | loadControlLimitListData | SPINE Resource Specification 1.3.0 |
| LoadControl | loadControlLimitListDataSelectors | SPINE Resource Specification 1.3.0 |
| LoadControl | loadControlNodeData | SPINE Resource Specification 1.3.0 |
| LoadControl | loadControlNodeDataElements | SPINE Resource Specification 1.3.0 |
| LoadControl | loadControlStateData | SPINE Resource Specification 1.3.0 |
| LoadControl | loadControlStateDataElements | SPINE Resource Specification 1.3.0 |
| LoadControl | loadControlStateListData | SPINE Resource Specification 1.3.0 Table 237 |
| LoadControl | loadControlStateListDataSelectors | SPINE Resource Specification 1.3.0 |
| LoadControl | not in the sources | SPINE Resource Specification 1.3.0 |
| Measurement | descriptive section | SPINE Resource Specification 1.3.0 §4.3.16.9 |
| Measurement | measurementConstraintsData | SPINE Resource Specification 1.3.0 |
| Measurement | measurementConstraintsDataElements | SPINE Resource Specification 1.3.0 |
| Measurement | measurementConstraintsListData | SPINE Resource Specification 1.3.0 |
| Measurement | measurementConstraintsListDataSelectors | SPINE Resource Specification 1.3.0 |
| Measurement | measurementData | SPINE Resource Specification 1.3.0 |
| Measurement | measurementDataElements | SPINE Resource Specification 1.3.0 |
| Measurement | measurementDescriptionData | SPINE Resource Specification 1.3.0 |
| Measurement | measurementDescriptionDataElements | SPINE Resource Specification 1.3.0 |
| Measurement | measurementDescriptionListData | SPINE Resource Specification 1.3.0 Table 100 |
| Measurement | measurementDescriptionListDataSelectors | SPINE Resource Specification 1.3.0 |
| Measurement | measurementListData | SPINE Resource Specification 1.3.0 |
| Measurement | measurementListDataSelectors | SPINE Resource Specification 1.3.0 |
| Measurement | measurementSeriesData | SPINE Resource Specification 1.3.0 |
| Measurement | measurementSeriesDataElements | SPINE Resource Specification 1.3.0 |
| Measurement | measurementSeriesListData | SPINE Resource Specification 1.3.0 |
| Measurement | measurementSeriesListDataSelectors | SPINE Resource Specification 1.3.0 |
| Measurement | measurementThresholdRelationData | SPINE Resource Specification 1.3.0 |
| Measurement | measurementThresholdRelationDataElements | SPINE Resource Specification 1.3.0 |
| Measurement | measurementThresholdRelationListData | SPINE Resource Specification 1.3.0 |
| Measurement | measurementThresholdRelationListDataSelectors | SPINE Resource Specification 1.3.0 |
| Measurement | not in the sources | SPINE Resource Specification 1.3.0 |
| Messaging | descriptive section | SPINE Resource Specification 1.3.0 §4.3.17.5 |
| Messaging | messagingData | SPINE Resource Specification 1.3.0 |
| Messaging | messagingDataElements | SPINE Resource Specification 1.3.0 |
| Messaging | messagingListData | SPINE Resource Specification 1.3.0 |
| Messaging | messagingListDataSelectors | SPINE Resource Specification 1.3.0 |
| Messaging | not in the sources | SPINE Resource Specification 1.3.0 |
| NetworkManagement | networkManagementAbortCall | SPINE Resource Specification 1.3.0 |
| NetworkManagement | networkManagementAbortCallElements | SPINE Resource Specification 1.3.0 |
| NetworkManagement | networkManagementAddNodeCall | SPINE Resource Specification 1.3.0 |
| NetworkManagement | networkManagementAddNodeCallElements | SPINE Resource Specification 1.3.0 |
| NetworkManagement | networkManagementDeviceDescriptionData | SPINE Resource Specification 1.3.0 |
| NetworkManagement | networkManagementDeviceDescriptionDataElements | SPINE Resource Specification 1.3.0 |
| NetworkManagement | networkManagementDeviceDescriptionListData | SPINE Resource Specification 1.3.0 Table 265 |
| NetworkManagement | networkManagementDeviceDescriptionListDataSelectors | SPINE Resource Specification 1.3.0 |
| NetworkManagement | networkManagementDiscoverCall | SPINE Resource Specification 1.3.0 |
| NetworkManagement | networkManagementDiscoverCallElements | SPINE Resource Specification 1.3.0 |
| NetworkManagement | networkManagementEntityDescriptionData | SPINE Resource Specification 1.3.0 |
| NetworkManagement | networkManagementEntityDescriptionDataElements | SPINE Resource Specification 1.3.0 |
| NetworkManagement | networkManagementEntityDescriptionListData | SPINE Resource Specification 1.3.0 |
| NetworkManagement | networkManagementEntityDescriptionListDataSelectors | SPINE Resource Specification 1.3.0 |
| NetworkManagement | networkManagementFeatureDescriptionData | SPINE Resource Specification 1.3.0 |
| NetworkManagement | networkManagementFeatureDescriptionDataElements | SPINE Resource Specification 1.3.0 |
| NetworkManagement | networkManagementFeatureDescriptionListData | SPINE Resource Specification 1.3.0 |
| NetworkManagement | networkManagementFeatureDescriptionListDataSelectors | SPINE Resource Specification 1.3.0 |
| NetworkManagement | networkManagementJoiningModeData | SPINE Resource Specification 1.3.0 |
| NetworkManagement | networkManagementJoiningModeDataElements | SPINE Resource Specification 1.3.0 |
| NetworkManagement | networkManagementModifyNodeCall | SPINE Resource Specification 1.3.0 |
| NetworkManagement | networkManagementModifyNodeCallElements | SPINE Resource Specification 1.3.0 |
| NetworkManagement | networkManagementProcessStateData | SPINE Resource Specification 1.3.0 |
| NetworkManagement | networkManagementProcessStateDataElements | SPINE Resource Specification 1.3.0 |
| NetworkManagement | networkManagementRemoveNodeCall | SPINE Resource Specification 1.3.0 |
| NetworkManagement | networkManagementRemoveNodeCallElements | SPINE Resource Specification 1.3.0 |
| NetworkManagement | networkManagementReportCandidateData | SPINE Resource Specification 1.3.0 Table 264 |
| NetworkManagement | networkManagementReportCandidateDataElements | SPINE Resource Specification 1.3.0 |
| NetworkManagement | networkManagementScanNetworkCall | SPINE Resource Specification 1.3.0 |
| NetworkManagement | networkManagementScanNetworkCallElements | SPINE Resource Specification 1.3.0 |
| NetworkManagement | not in the sources | SPINE Resource Specification 1.3.0 |
| NodeManagement | (none defined here) | SPINE Resource Specification 1.3.0 §5.2.2 |
| NodeManagement | (schema) | SPINE Resource Specification 1.3.0 |
| NodeManagement | nodeManagementBindingData | SPINE Resource Specification 1.3.0 |
| NodeManagement | nodeManagementBindingDataElements | SPINE Resource Specification 1.3.0 |
| NodeManagement | nodeManagementBindingDataSelectors | SPINE Resource Specification 1.3.0 |
| NodeManagement | nodeManagementBindingDeleteCall | SPINE Resource Specification 1.3.0 |
| NodeManagement | nodeManagementBindingDeleteCallElements | SPINE Resource Specification 1.3.0 |
| NodeManagement | nodeManagementBindingRequestCall | SPINE Resource Specification 1.3.0 |
| NodeManagement | nodeManagementBindingRequestCallElements | SPINE Resource Specification 1.3.0 |
| NodeManagement | nodeManagementDestinationData | SPINE Resource Specification 1.3.0 |
| NodeManagement | nodeManagementDestinationDataElements | SPINE Resource Specification 1.3.0 |
| NodeManagement | nodeManagementDestinationListData | SPINE Resource Specification 1.3.0 |
| NodeManagement | nodeManagementDestinationListDataSelectors | SPINE Resource Specification 1.3.0 |
| NodeManagement | nodeManagementDetailedDiscoveryData | SPINE Resource Specification 1.3.0 |
| NodeManagement | nodeManagementDetailedDiscoveryDataElements | SPINE Resource Specification 1.3.0 |
| NodeManagement | nodeManagementDetailedDiscoveryDataSelectors | SPINE Resource Specification 1.3.0 |
| NodeManagement | nodeManagementSubscriptionData | SPINE Resource Specification 1.3.0 |
| NodeManagement | nodeManagementSubscriptionDataElements | SPINE Resource Specification 1.3.0 |
| NodeManagement | nodeManagementSubscriptionDataSelectors | SPINE Resource Specification 1.3.0 |
| NodeManagement | nodeManagementSubscriptionDeleteCall | SPINE Resource Specification 1.3.0 |
| NodeManagement | nodeManagementSubscriptionDeleteCallElements | SPINE Resource Specification 1.3.0 |
| NodeManagement | nodeManagementSubscriptionRequestCall | SPINE Resource Specification 1.3.0 |
| NodeManagement | nodeManagementSubscriptionRequestCallElements | SPINE Resource Specification 1.3.0 |
| NodeManagement | nodeManagementUseCaseData | SPINE Resource Specification 1.3.0 |
| NodeManagement | nodeManagementUseCaseDataElements | SPINE Resource Specification 1.3.0 |
| NodeManagement | nodeManagementUseCaseDataSelectors | SPINE Resource Specification 1.3.0 |
| NodeManagement | not in the sources | SPINE Resource Specification 1.3.0 §4.3.19 |
| OperatingConstraints | all xListData functions of §4.3.20 | SPINE Resource Specification 1.3.0 §4.3.20.10 |
| OperatingConstraints | not in the sources | SPINE Resource Specification 1.3.0 |
| OperatingConstraints | operatingConstraintsDurationData | SPINE Resource Specification 1.3.0 |
| OperatingConstraints | operatingConstraintsDurationDataElements | SPINE Resource Specification 1.3.0 |
| OperatingConstraints | operatingConstraintsDurationListData | SPINE Resource Specification 1.3.0 Table 106 |
| OperatingConstraints | operatingConstraintsDurationListDataSelectors | SPINE Resource Specification 1.3.0 |
| OperatingConstraints | operatingConstraintsInterruptData | SPINE Resource Specification 1.3.0 |
| OperatingConstraints | operatingConstraintsInterruptDataElements | SPINE Resource Specification 1.3.0 |
| OperatingConstraints | operatingConstraintsInterruptListData | SPINE Resource Specification 1.3.0 |
| OperatingConstraints | operatingConstraintsInterruptListDataSelectors | SPINE Resource Specification 1.3.0 |
| OperatingConstraints | operatingConstraintsPowerDescriptionData | SPINE Resource Specification 1.3.0 |
| OperatingConstraints | operatingConstraintsPowerDescriptionDataElements | SPINE Resource Specification 1.3.0 |
| OperatingConstraints | operatingConstraintsPowerDescriptionListData | SPINE Resource Specification 1.3.0 |
| OperatingConstraints | operatingConstraintsPowerDescriptionListDataSelectors | SPINE Resource Specification 1.3.0 |
| OperatingConstraints | operatingConstraintsPowerLevelData | SPINE Resource Specification 1.3.0 |
| OperatingConstraints | operatingConstraintsPowerLevelDataElements | SPINE Resource Specification 1.3.0 |
| OperatingConstraints | operatingConstraintsPowerLevelListData | SPINE Resource Specification 1.3.0 |
| OperatingConstraints | operatingConstraintsPowerLevelListDataSelectors | SPINE Resource Specification 1.3.0 |
| OperatingConstraints | operatingConstraintsPowerRangeData | SPINE Resource Specification 1.3.0 |
| OperatingConstraints | operatingConstraintsPowerRangeDataElements | SPINE Resource Specification 1.3.0 |
| OperatingConstraints | operatingConstraintsPowerRangeListData | SPINE Resource Specification 1.3.0 |
| OperatingConstraints | operatingConstraintsPowerRangeListDataSelectors | SPINE Resource Specification 1.3.0 |
| OperatingConstraints | operatingConstraintsResumeImplicationData | SPINE Resource Specification 1.3.0 |
| OperatingConstraints | operatingConstraintsResumeImplicationDataElements | SPINE Resource Specification 1.3.0 |
| OperatingConstraints | operatingConstraintsResumeImplicationListData | SPINE Resource Specification 1.3.0 |
| OperatingConstraints | operatingConstraintsResumeImplicationListDataSelectors | SPINE Resource Specification 1.3.0 |
| PowerSequence | powerSequenceNodeScheduleInformationData | SPINE Resource Specification 1.3.0 §5.3.19.15.2, Table 289 |
| PowerSequence | powerSequencePriceCalculationRequestCall | SPINE Resource Specification 1.3.0 §5.3.19.18.2, Table 291 |
| PowerSequence | powerSequencePriceListData | SPINE Resource Specification 1.3.0 §5.3.19.12.2, Table 287 |
| PowerSequence | powerSequenceScheduleConfigurationRequestCall | SPINE Resource Specification 1.3.0 §5.3.19.17.3, §5.3.19.17.1 |
| PowerSequence | powerSequenceSchedulePreferenceListData | SPINE Resource Specification 1.3.0 §5.3.19.13.2, Table 288 |
| PowerSequences | not in the sources | SPINE Resource Specification 1.3.0 |
| PowerSequences | powerSequenceAlternativesRelationData | SPINE Resource Specification 1.3.0 |
| PowerSequences | powerSequenceAlternativesRelationDataElements | SPINE Resource Specification 1.3.0 |
| PowerSequences | powerSequenceAlternativesRelationListData | SPINE Resource Specification 1.3.0 |
| PowerSequences | powerSequenceAlternativesRelationListDataSelectors | SPINE Resource Specification 1.3.0 |
| PowerSequences | powerSequenceDescriptionData | SPINE Resource Specification 1.3.0 |
| PowerSequences | powerSequenceDescriptionDataElements | SPINE Resource Specification 1.3.0 |
| PowerSequences | powerSequenceDescriptionListData | SPINE Resource Specification 1.3.0 |
| PowerSequences | powerSequenceDescriptionListDataSelectors | SPINE Resource Specification 1.3.0 |
| PowerSequences | powerSequenceNodeScheduleInformationData | SPINE Resource Specification 1.3.0 |
| PowerSequences | powerSequenceNodeScheduleInformationDataElements | SPINE Resource Specification 1.3.0 |
| PowerSequences | powerSequencePriceCalculationRequestCall | SPINE Resource Specification 1.3.0 |
| PowerSequences | powerSequencePriceCalculationRequestCallElements | SPINE Resource Specification 1.3.0 |
| PowerSequences | powerSequencePriceData | SPINE Resource Specification 1.3.0 |
| PowerSequences | powerSequencePriceDataElements | SPINE Resource Specification 1.3.0 |
| PowerSequences | powerSequencePriceListData | SPINE Resource Specification 1.3.0 |
| PowerSequences | powerSequencePriceListDataSelectors | SPINE Resource Specification 1.3.0 |
| PowerSequences | powerSequenceScheduleConfigurationRequestCall | SPINE Resource Specification 1.3.0 |
| PowerSequences | powerSequenceScheduleConfigurationRequestCallElements | SPINE Resource Specification 1.3.0 |
| PowerSequences | powerSequenceScheduleConstraintsData | SPINE Resource Specification 1.3.0 |
| PowerSequences | powerSequenceScheduleConstraintsDataElements | SPINE Resource Specification 1.3.0 |
| PowerSequences | powerSequenceScheduleConstraintsListData | SPINE Resource Specification 1.3.0 |
| PowerSequences | powerSequenceScheduleConstraintsListDataSelectors | SPINE Resource Specification 1.3.0 |
| PowerSequences | powerSequenceScheduleData | SPINE Resource Specification 1.3.0 |
| PowerSequences | powerSequenceScheduleDataElements | SPINE Resource Specification 1.3.0 |
| PowerSequences | powerSequenceScheduleListData | SPINE Resource Specification 1.3.0 |
| PowerSequences | powerSequenceScheduleListDataSelectors | SPINE Resource Specification 1.3.0 |
| PowerSequences | powerSequenceSchedulePreferenceData | SPINE Resource Specification 1.3.0 |
| PowerSequences | powerSequenceSchedulePreferenceDataElements | SPINE Resource Specification 1.3.0 |
| PowerSequences | powerSequenceSchedulePreferenceListData | SPINE Resource Specification 1.3.0 |
| PowerSequences | powerSequenceSchedulePreferenceListDataSelectors | SPINE Resource Specification 1.3.0 |
| PowerSequences | powerSequenceStateData | SPINE Resource Specification 1.3.0 |
| PowerSequences | powerSequenceStateDataElements | SPINE Resource Specification 1.3.0 |
| PowerSequences | powerSequenceStateListData | SPINE Resource Specification 1.3.0 |
| PowerSequences | powerSequenceStateListDataSelectors | SPINE Resource Specification 1.3.0 |
| PowerSequences | powerTimeSlotScheduleConstraintsData | SPINE Resource Specification 1.3.0 |
| PowerSequences | powerTimeSlotScheduleConstraintsDataElements | SPINE Resource Specification 1.3.0 |
| PowerSequences | powerTimeSlotScheduleConstraintsListData | SPINE Resource Specification 1.3.0 |
| PowerSequences | powerTimeSlotScheduleConstraintsListDataSelectors | SPINE Resource Specification 1.3.0 |
| PowerSequences | powerTimeSlotScheduleData | SPINE Resource Specification 1.3.0 |
| PowerSequences | powerTimeSlotScheduleDataElements | SPINE Resource Specification 1.3.0 |
| PowerSequences | powerTimeSlotScheduleListData | SPINE Resource Specification 1.3.0 |
| PowerSequences | powerTimeSlotScheduleListDataSelectors | SPINE Resource Specification 1.3.0 |
| PowerSequences | powerTimeSlotValueData | SPINE Resource Specification 1.3.0 |
| PowerSequences | powerTimeSlotValueDataElements | SPINE Resource Specification 1.3.0 |
| PowerSequences | powerTimeSlotValueListData | SPINE Resource Specification 1.3.0 |
| PowerSequences | powerTimeSlotValueListDataSelectors | SPINE Resource Specification 1.3.0 |
| Result | not in the sources | SPINE Resource Specification 1.3.0 |
| Result | resultData | SPINE Resource Specification 1.3.0 |
| Sensing | descriptive section | SPINE Resource Specification 1.3.0 §4.3.22.6 |
| Sensing | not in the sources | SPINE Resource Specification 1.3.0 |
| Sensing | sensingData | SPINE Resource Specification 1.3.0 |
| Sensing | sensingDataElements | SPINE Resource Specification 1.3.0 |
| Sensing | sensingDescriptionData | SPINE Resource Specification 1.3.0 |
| Sensing | sensingDescriptionDataElements | SPINE Resource Specification 1.3.0 |
| Sensing | sensingListData | SPINE Resource Specification 1.3.0 |
| Sensing | sensingListDataSelectors | SPINE Resource Specification 1.3.0 |
| Setpoint | descriptive section | SPINE Resource Specification 1.3.0 §4.3.23.7 |
| Setpoint | not in the sources | SPINE Resource Specification 1.3.0 |
| Setpoint | setpointConstraintsData | SPINE Resource Specification 1.3.0 |
| Setpoint | setpointConstraintsDataElements | SPINE Resource Specification 1.3.0 |
| Setpoint | setpointConstraintsListData | SPINE Resource Specification 1.3.0 |
| Setpoint | setpointConstraintsListDataSelectors | SPINE Resource Specification 1.3.0 |
| Setpoint | setpointData | SPINE Resource Specification 1.3.0 |
| Setpoint | setpointDataElements | SPINE Resource Specification 1.3.0 |
| Setpoint | setpointDescriptionData | SPINE Resource Specification 1.3.0 |
| Setpoint | setpointDescriptionDataElements | SPINE Resource Specification 1.3.0 |
| Setpoint | setpointDescriptionListData | SPINE Resource Specification 1.3.0 |
| Setpoint | setpointDescriptionListDataSelectors | SPINE Resource Specification 1.3.0 |
| Setpoint | setpointListData | SPINE Resource Specification 1.3.0 |
| Setpoint | setpointListDataSelectors | SPINE Resource Specification 1.3.0 |
| SmartEnergyManagementPs | (no global element on these pages) | SPINE Resource Specification 1.3.0 |
| SmartEnergyManagementPs | (schema) | SPINE Resource Specification 1.3.0 |
| SmartEnergyManagementPs | smartEnergyManagementPsConfigurationRequestCall | SPINE Resource Specification 1.3.0 §5.2.3.2.2.3 |
| SmartEnergyManagementPs | smartEnergyManagementPsConfigurationRequestCallElements | SPINE Resource Specification 1.3.0 |
| SmartEnergyManagementPs | smartEnergyManagementPsData | SPINE Resource Specification 1.3.0 Table 167 |
| SmartEnergyManagementPs | smartEnergyManagementPsDataElements | SPINE Resource Specification 1.3.0 |
| SmartEnergyManagementPs | smartEnergyManagementPsDataSelectors | SPINE Resource Specification 1.3.0 |
| SmartEnergyManagementPs | smartEnergyManagementPsPriceCalculationRequestCall | SPINE Resource Specification 1.3.0 §5.2.3.2.4.3 |
| SmartEnergyManagementPs | smartEnergyManagementPsPriceCalculationRequestCallElements | SPINE Resource Specification 1.3.0 |
| SmartEnergyManagementPs | smartEnergyManagementPsPriceData | SPINE Resource Specification 1.3.0 Table 170 |
| SmartEnergyManagementPs | smartEnergyManagementPsPriceDataElements | SPINE Resource Specification 1.3.0 |
| SmartEnergyManagementPs | smartEnergyManagementPsPriceDataSelectors | SPINE Resource Specification 1.3.0 |
| StateInformation | not in the sources | SPINE Resource Specification 1.3.0 |
| StateInformation | stateInformationData | SPINE Resource Specification 1.3.0 |
| StateInformation | stateInformationDataElements | SPINE Resource Specification 1.3.0 |
| StateInformation | stateInformationListData | SPINE Resource Specification 1.3.0 Table 129, Table 131 |
| StateInformation | stateInformationListDataSelectors | SPINE Resource Specification 1.3.0 |
| SubscriptionManagement | not in the sources | SPINE Resource Specification 1.3.0 |
| SubscriptionManagement | subscriptionManagementDeleteCall | SPINE Resource Specification 1.3.0 §5.3.22.4.2, Table 302 |
| SubscriptionManagement | subscriptionManagementDeleteCallElements | SPINE Resource Specification 1.3.0 |
| SubscriptionManagement | subscriptionManagementEntryData | SPINE Resource Specification 1.3.0 |
| SubscriptionManagement | subscriptionManagementEntryDataElements | SPINE Resource Specification 1.3.0 |
| SubscriptionManagement | subscriptionManagementEntryListData | SPINE Resource Specification 1.3.0 §5.3.22.2.2, Table 300 |
| SubscriptionManagement | subscriptionManagementRequestCall | SPINE Resource Specification 1.3.0 §5.3.22.3.2, Table 301, §5.3.22.3.1 |
| SubscriptionManagement | subscriptionManagementRequestCallElements | SPINE Resource Specification 1.3.0 |
| SupplyCondition | not in the sources | SPINE Resource Specification 1.3.0 |
| SupplyCondition | supplyConditionData | SPINE Resource Specification 1.3.0 |
| SupplyCondition | supplyConditionDataElements | SPINE Resource Specification 1.3.0 |
| SupplyCondition | supplyConditionDescriptionData | SPINE Resource Specification 1.3.0 |
| SupplyCondition | supplyConditionDescriptionDataElements | SPINE Resource Specification 1.3.0 |
| SupplyCondition | supplyConditionDescriptionListData | SPINE Resource Specification 1.3.0 Table 136 |
| SupplyCondition | supplyConditionDescriptionListDataSelectors | SPINE Resource Specification 1.3.0 |
| SupplyCondition | supplyConditionListData | SPINE Resource Specification 1.3.0 §5.3.24.2.2, Table 307 |
| SupplyCondition | supplyConditionListDataSelectors | SPINE Resource Specification 1.3.0 |
| SupplyCondition | supplyConditionThresholdRelationData | SPINE Resource Specification 1.3.0 |
| SupplyCondition | supplyConditionThresholdRelationDataElements | SPINE Resource Specification 1.3.0 |
| SupplyCondition | supplyConditionThresholdRelationListData | SPINE Resource Specification 1.3.0 §5.3.24.4.2, Table 312 |
| SupplyCondition | supplyConditionThresholdRelationListDataSelectors | SPINE Resource Specification 1.3.0 |
| TariffInformation | commodityData | SPINE Resource Specification 1.3.0 |
| TariffInformation | commodityDataElements | SPINE Resource Specification 1.3.0 |
| TariffInformation | commodityListData | SPINE Resource Specification 1.3.0 §5.3.25.12.2, Table 321 |
| TariffInformation | commodityListDataSelectors | SPINE Resource Specification 1.3.0 |
| TariffInformation | incentiveData | SPINE Resource Specification 1.3.0 |
| TariffInformation | incentiveDataElements | SPINE Resource Specification 1.3.0 |
| TariffInformation | incentiveDescriptionData | SPINE Resource Specification 1.3.0 |
| TariffInformation | incentiveDescriptionDataElements | SPINE Resource Specification 1.3.0 |
| TariffInformation | incentiveDescriptionListData | SPINE Resource Specification 1.3.0 §5.3.25.19.2, Table 328 |
| TariffInformation | incentiveDescriptionListDataSelectors | SPINE Resource Specification 1.3.0 |
| TariffInformation | incentiveListData | SPINE Resource Specification 1.3.0 §5.3.25.18.2, Table 326 |
| TariffInformation | incentiveListDataSelectors | SPINE Resource Specification 1.3.0 |
| TariffInformation | not in the sources | SPINE Resource Specification 1.3.0 |
| TariffInformation | tariffBoundaryRelationData | SPINE Resource Specification 1.3.0 |
| TariffInformation | tariffBoundaryRelationDataElements | SPINE Resource Specification 1.3.0 |
| TariffInformation | tariffBoundaryRelationListData | SPINE Resource Specification 1.3.0 §5.3.25.5.2, Table 315 |
| TariffInformation | tariffBoundaryRelationListDataSelectors | SPINE Resource Specification 1.3.0 |
| TariffInformation | tariffData | SPINE Resource Specification 1.3.0 |
| TariffInformation | tariffDataElements | SPINE Resource Specification 1.3.0 |
| TariffInformation | tariffDescriptionData | SPINE Resource Specification 1.3.0 |
| TariffInformation | tariffDescriptionDataElements | SPINE Resource Specification 1.3.0 |
| TariffInformation | tariffDescriptionListData | SPINE Resource Specification 1.3.0 §5.3.25.7.2, Table 317 |
| TariffInformation | tariffDescriptionListDataSelectors | SPINE Resource Specification 1.3.0 |
| TariffInformation | tariffListData | SPINE Resource Specification 1.3.0 §5.3.25.4.2, Table 314 |
| TariffInformation | tariffListDataSelectors | SPINE Resource Specification 1.3.0 |
| TariffInformation | tariffOverallConstraintsData | SPINE Resource Specification 1.3.0 §5.3.25.3.2, Table 313 |
| TariffInformation | tariffOverallConstraintsDataElements | SPINE Resource Specification 1.3.0 |
| TariffInformation | tariffTierRelationData | SPINE Resource Specification 1.3.0 |
| TariffInformation | tariffTierRelationDataElements | SPINE Resource Specification 1.3.0 |
| TariffInformation | tariffTierRelationListData | SPINE Resource Specification 1.3.0 §5.3.25.6.3 |
| TariffInformation | tariffTierRelationListDataSelectors | SPINE Resource Specification 1.3.0 |
| TariffInformation | tierBoundaryData | SPINE Resource Specification 1.3.0 |
| TariffInformation | tierBoundaryDataElements | SPINE Resource Specification 1.3.0 |
| TariffInformation | tierBoundaryDescriptionData | SPINE Resource Specification 1.3.0 |
| TariffInformation | tierBoundaryDescriptionDataElements | SPINE Resource Specification 1.3.0 |
| TariffInformation | tierBoundaryDescriptionListData | SPINE Resource Specification 1.3.0 §5.3.25.10.2, Table 319 |
| TariffInformation | tierBoundaryDescriptionListDataSelectors | SPINE Resource Specification 1.3.0 |
| TariffInformation | tierBoundaryListData | SPINE Resource Specification 1.3.0 §5.3.25.9.2, Table 318 |
| TariffInformation | tierBoundaryListDataSelectors | SPINE Resource Specification 1.3.0 |
| TariffInformation | tierData | SPINE Resource Specification 1.3.0 |
| TariffInformation | tierDataElements | SPINE Resource Specification 1.3.0 |
| TariffInformation | tierDescriptionData | SPINE Resource Specification 1.3.0 |
| TariffInformation | tierDescriptionDataElements | SPINE Resource Specification 1.3.0 |
| TariffInformation | tierDescriptionListData | SPINE Resource Specification 1.3.0 §5.3.25.16.2, Table 324 |
| TariffInformation | tierDescriptionListDataSelectors | SPINE Resource Specification 1.3.0 |
| TariffInformation | tierIncentiveRelationData | SPINE Resource Specification 1.3.0 |
| TariffInformation | tierIncentiveRelationDataElements | SPINE Resource Specification 1.3.0 |
| TariffInformation | tierIncentiveRelationListData | SPINE Resource Specification 1.3.0 §5.3.25.15.2, Table 323 |
| TariffInformation | tierIncentiveRelationListDataSelectors | SPINE Resource Specification 1.3.0 |
| TariffInformation | tierListData | SPINE Resource Specification 1.3.0 §5.3.25.14.2, Table 322 |
| TariffInformation | tierListDataSelectors | SPINE Resource Specification 1.3.0 |
| TaskManagement | not in the sources | SPINE Resource Specification 1.3.0 |
| TaskManagement | taskManagementJobData | SPINE Resource Specification 1.3.0 |
| TaskManagement | taskManagementJobDataElements | SPINE Resource Specification 1.3.0 |
| TaskManagement | taskManagementJobDescriptionData | SPINE Resource Specification 1.3.0 |
| TaskManagement | taskManagementJobDescriptionDataElements | SPINE Resource Specification 1.3.0 |
| TaskManagement | taskManagementJobDescriptionListData | SPINE Resource Specification 1.3.0 §5.3.26.4.3, §5.3.26.4.4.1 |
| TaskManagement | taskManagementJobDescriptionListDataSelectors | SPINE Resource Specification 1.3.0 |
| TaskManagement | taskManagementJobListData | SPINE Resource Specification 1.3.0 §5.3.26.2.2, Table 330 |
| TaskManagement | taskManagementJobListDataSelectors | SPINE Resource Specification 1.3.0 |
| TaskManagement | taskManagementJobRelationData | SPINE Resource Specification 1.3.0 |
| TaskManagement | taskManagementJobRelationDataElements | SPINE Resource Specification 1.3.0 |
| TaskManagement | taskManagementJobRelationListData | SPINE Resource Specification 1.3.0 §5.3.26.3.2, Table 331 |
| TaskManagement | taskManagementJobRelationListDataSelectors | SPINE Resource Specification 1.3.0 |
| TaskManagement | taskManagementOverviewData | SPINE Resource Specification 1.3.0 §5.3.26.5.3, §5.3.26.5.4.1 |
| TaskManagement | taskManagementOverviewDataElements | SPINE Resource Specification 1.3.0 |
| Threshold | not in the sources | SPINE Resource Specification 1.3.0 |
| Threshold | thresholdConstraintsData | SPINE Resource Specification 1.3.0 |
| Threshold | thresholdConstraintsDataElements | SPINE Resource Specification 1.3.0 |
| Threshold | thresholdConstraintsListData | SPINE Resource Specification 1.3.0 §5.3.27.3.3 |
| Threshold | thresholdConstraintsListDataSelectors | SPINE Resource Specification 1.3.0 |
| Threshold | thresholdData | SPINE Resource Specification 1.3.0 |
| Threshold | thresholdDataElements | SPINE Resource Specification 1.3.0 |
| Threshold | thresholdDescriptionData | SPINE Resource Specification 1.3.0 |
| Threshold | thresholdDescriptionDataElements | SPINE Resource Specification 1.3.0 |
| Threshold | thresholdDescriptionListData | SPINE Resource Specification 1.3.0 §5.3.27.4.3 |
| Threshold | thresholdDescriptionListDataSelectors | SPINE Resource Specification 1.3.0 |
| Threshold | thresholdListData | SPINE Resource Specification 1.3.0 §5.3.27.2.1 |
| Threshold | thresholdListDataSelectors | SPINE Resource Specification 1.3.0 |
| TimeInformation | not in the sources | SPINE Resource Specification 1.3.0 |
| TimeInformation | timeDistributorData | SPINE Resource Specification 1.3.0 §5.3.28.3.3, §5.3.28.3.4.1 |
| TimeInformation | timeDistributorDataElements | SPINE Resource Specification 1.3.0 |
| TimeInformation | timeDistributorEnquiryCall | SPINE Resource Specification 1.3.0 §5.3.28.5.2, §5.3.28.5.4.1 |
| TimeInformation | timeDistributorEnquiryCallElements | SPINE Resource Specification 1.3.0 |
| TimeInformation | timeInformationData | SPINE Resource Specification 1.3.0 §5.3.28.2.1 |
| TimeInformation | timeInformationDataElements | SPINE Resource Specification 1.3.0 |
| TimeInformation | timePrecisionData | SPINE Resource Specification 1.3.0 §5.3.28.4.3 |
| TimeInformation | timePrecisionDataElements | SPINE Resource Specification 1.3.0 |
| TimeSeries | not in the sources | SPINE Resource Specification 1.3.0 |
| TimeSeries | timeSeriesConstraintsData | SPINE Resource Specification 1.3.0 |
| TimeSeries | timeSeriesConstraintsDataElements | SPINE Resource Specification 1.3.0 |
| TimeSeries | timeSeriesConstraintsListData | SPINE Resource Specification 1.3.0 §5.3.29.4.3 |
| TimeSeries | timeSeriesConstraintsListDataSelectors | SPINE Resource Specification 1.3.0 |
| TimeSeries | timeSeriesData | SPINE Resource Specification 1.3.0 |
| TimeSeries | timeSeriesDataElements | SPINE Resource Specification 1.3.0 |
| TimeSeries | timeSeriesDescriptionData | SPINE Resource Specification 1.3.0 |
| TimeSeries | timeSeriesDescriptionDataElements | SPINE Resource Specification 1.3.0 |
| TimeSeries | timeSeriesDescriptionListData | SPINE Resource Specification 1.3.0 §5.3.29.3.3 |
| TimeSeries | timeSeriesDescriptionListDataSelectors | SPINE Resource Specification 1.3.0 |
| TimeSeries | timeSeriesListData | SPINE Resource Specification 1.3.0 §5.3.29.2.3 |
| TimeSeries | timeSeriesListDataSelectors | SPINE Resource Specification 1.3.0 |
| TimeTable | not in the sources | SPINE Resource Specification 1.3.0 |
| TimeTable | timeTableConstraintsData | SPINE Resource Specification 1.3.0 |
| TimeTable | timeTableConstraintsDataElements | SPINE Resource Specification 1.3.0 |
| TimeTable | timeTableConstraintsListData | SPINE Resource Specification 1.3.0 §5.3.30.3.3, §5.3.30.3.4.1 |
| TimeTable | timeTableConstraintsListDataSelectors | SPINE Resource Specification 1.3.0 |
| TimeTable | timeTableData | SPINE Resource Specification 1.3.0 |
| TimeTable | timeTableDataElements | SPINE Resource Specification 1.3.0 |
| TimeTable | timeTableDescriptionData | SPINE Resource Specification 1.3.0 |
| TimeTable | timeTableDescriptionDataElements | SPINE Resource Specification 1.3.0 |
| TimeTable | timeTableDescriptionListData | SPINE Resource Specification 1.3.0 §5.3.30.4.3 |
| TimeTable | timeTableDescriptionListDataSelectors | SPINE Resource Specification 1.3.0 |
| TimeTable | timeTableListData | SPINE Resource Specification 1.3.0 §5.3.30.2.3, §5.3.30.2.4.2 |
| TimeTable | timeTableListDataSelectors | SPINE Resource Specification 1.3.0 |
| UseCaseInformation | not in the sources | SPINE Resource Specification 1.3.0 |
| UseCaseInformation | useCaseInformationData | SPINE Resource Specification 1.3.0 |
| UseCaseInformation | useCaseInformationDataElements | SPINE Resource Specification 1.3.0 |
| UseCaseInformation | useCaseInformationListData | SPINE Resource Specification 1.3.0 §5.3.31.2.3 |
| UseCaseInformation | useCaseInformationListDataSelectors | SPINE Resource Specification 1.3.0 |
| Version | not in the sources | SPINE Resource Specification 1.3.0 |
| Version | specificationVersionData | SPINE Resource Specification 1.3.0 |
| Version | specificationVersionDataElements | SPINE Resource Specification 1.3.0 |
| Version | specificationVersionListData | SPINE Resource Specification 1.3.0 §5.3.32.2.3, §5.3.32.2.4.1 |
| Version | specificationVersionListDataSelectors | SPINE Resource Specification 1.3.0 |

## Commands, limits and timing

The heartbeat counter increases after each heartbeatTimeout, not on every transmission, and a read does not increase it. LabelType should not exceed 256 characters and DescriptionType should not exceed 4096. A longer value may be shortened by the receiver, and the sender allows that (§§3.10.1.2–3.10.1.3). Annex §A.3.3 restricts both types as xs:string with no length facet. Both statements stay.

| topic | statement | clause |
| --- | --- | --- |
| heartbeat | heartbeatCounter increases after each heartbeatTimeout, not on every transmission. A read does not increase it. After each such period a notification goes to every subscribed client. | SPINE Resource Specification 1.3.0 §3 |
| failsafeDurationMinimum | When used, a duration. After heartbeats are lost, the appliance stays in the failsafe state at least that long. No numeric duration is printed. | SPINE Resource Specification 1.3.0 |
| failsafe keys | failsafeConsumptionActivePowerLimit and failsafeProductionActivePowerLimit in W; reactive limits in var; cos phi limits with unit 1; AC, DC, and PCC setpoints in W when used. | SPINE Resource Specification 1.3.0 |
| LabelType | Length should not exceed 256 characters. A longer value may be shortened by the receiver, and the sender allows that. | SPINE Resource Specification 1.3.0 §3.10.1.2 |
| DescriptionType | Length should not exceed 4096 characters. A longer value may be shortened by the receiver, and the sender allows that. | SPINE Resource Specification 1.3.0 §3.10.1.3 |
| LabelType and DescriptionType, annex | Both restrict xs:string with no length facet. This stays beside the length rules above. | SPINE Resource Specification 1.3.0 §A.3.3 |
| device address | Maximum 256 characters. | SPINE Resource Specification 1.3.0 §4, §A.3.3 |
| feature group | Maximum 128 characters. | SPINE Resource Specification 1.3.0 |
| defaultMaxResponseDelay | The annex restricts MaxResponseDelayType as xs:duration with no facet. The protocol specification states 10 seconds. | SPINE Resource Specification 1.3.0 §A.3.3; SPINE Protocol Specification 1.3.0 §5.2.5.3 |

| topic | statement | clause |
| --- | --- | --- |
| Time | Nearly every time value is AbsoluteOrRelativeTimeType, which joins xs:dateTime with xs:duration. §3.2 | §3.2 |
| Time | Exceptions named here, whose types are not given here: timeInformationData element utc; timePrecisionData element lastSyncAt. | clause not printed |
| Time | A duration-based value means "now", unless a clause says otherwise. | clause not printed |
| Time | An absolute time SHALL be UTC and SHALL end with Z. | clause not printed |
| Time | Recurring times use AbsoluteOrRecurringTimeType, §3.10.2.13. | §3.10.2.13 |
| Time | TimePeriodType has startTime and endTime, both AbsoluteOrRelativeTimeType. The clause stops at. The notation example calls both optional. §3.10.2.1, §1.4.1.2.10 | §3.10.2.1, §1.4.1.2.10 |
| Timestamp used as an identifier | In a notification or a reply, the value may be xs:duration or xs:dateTime. The modal verb in the text is lowercase. | clause not printed |
| Timestamp used as an identifier | On a write that means "now", two forms are described: duration zero, example PT0S; or xs:dateTime equal to the current date and time. | clause not printed |
| Timestamp used as an identifier | Client and server time bases may differ, so a write that means "now" SHOULD use a relative time. The server may still send absolute times in a notify or a reply. That second "may" is lowercase. | clause not printed |
| Timestamp used as an identifier | For a time other than "now", the client SHALL use only a form, absolute or relative, that the server supports. The text says that support, for now, is discovered only by inspecting messages the server has sent. | clause not printed |
| Timestamp used as an identifier | For a historical value that is writable, only an absolute time SHOULD be used. | clause not printed |
| Timestamp used as an identifier | A binary compare of timestamp identifiers is not sufficient, because the same instant may be absolute or relative. | clause not printed |
| Timestamp used as an identifier | The feature type may add rules, including a restriction to only xs:duration or only xs:dateTime, and a restriction of the value range. That "may" is lowercase. | clause not printed |
| Identifier rules | PRIMARY IDENTIFIER: unique across that feature. It is used only as that main identifier (the text's words are primary, or top-level), not as a lower one. It MAY be combined with SUB IDENTIFIERs when a list has more than one dimension. A feature type is allowed to name more than one PRIMARY IDENTIFIER; in that case it also states how they relate. | clause not printed |
| Identifier rules | SUB IDENTIFIER: one or more MAY identify further dimensions of a list entry. Example: parameterId in electricalConnectionParameterDescriptionListData. | clause not printed |
| Identifier rules | FOREIGN IDENTIFIER: points at functionality elsewhere on this entity. It does not add a dimension of the list entry. It usually carries a value that is a primary identifier in another function. A use case may use foreign identifiers with no list entry where that value is the primary identifier; entries that share the foreign value still express a relationship. | clause not printed |
| Identifier rules | The order printed in the feature-type function description is the identifier order. If a class data model places a sub-identifier before a primary identifier, the order used is still primary, then sub, then any further subs. §3.4.2.2 | §3.4.2.2 |
| Identifier rules | Skipping an identifier MAY be allowed. The feature type is where that permission is stated. | clause not printed |
| Identifier rules | Every primary identifier SHALL be set unless the feature type says otherwise. A non-primary identifier SHOULD be set when it is available, unless the feature type says otherwise. §3.4.2.4 | §3.4.2.4 |
| Identifier rules | Within a list, the PRIMARY IDENTIFIERs and SUB IDENTIFIERs together SHALL pick out exactly one xData row of that xListData. | clause not printed |
| Identifier rules | Primary identifiers are those used to reference the class from inside the class and from other features, and they are unique within the feature. | clause not printed |
| Identifier rules | FOREIGN IDENTIFIERs SHALL NOT be axes of the multidimensional space described in §3.5. | §3.5 |
| Identifier rules | An identifier of lower priority is invalid unless every required identifier of higher priority is present too. In the measurement §3.5 | §3.5 |
| Optional identifiers | Some feature types define a default, so the identifier may be omitted when the feature contains at most one value of that identifier. The example named is valueId of feature type Bill. The default then applies. | clause not printed |
| Optional identifiers | If an identifier is present, it SHALL be evaluated. A later use can start sending an identifier that used to be absent, once two or more values exist. | clause not printed |
| Optional identifiers | As soon as one list entry sets an identifier, every list entry SHALL set it. | clause not printed |
| Optional identifiers | Where a server omits a primary or sub identifier and applies a default internally, a foreign identifier that points at those entries is required to carry that default. The text uses lowercase "must". | clause not printed |
| Optional identifiers | When a second identifier value appears, the entries that used the default SHALL then contain the identifier explicitly. The | clause not printed |
| Optional identifiers | The text recommends not omitting an identifier that equals its default. This is a recommendation, not the keyword SHOULD. | clause not printed |
| Optional identifiers | If the identifier is omitted, it SHALL be omitted in every list entry. Particular entries of that list then cannot be submitted or referenced. | clause not printed |
| Optional identifiers | If it is present, it SHALL be present in every list entry, and it identifies entries. | clause not printed |
| Optional identifiers | Changing between the omitted form and the present form replaces the former list with the new one. | clause not printed |
| List data and restricted exchange | A list function holds 0 to unbounded entries and nothing else. Where list data is defined, only the list is the resource. The non-list type is only the entry type referenced by the list. §3.3 | §3.3 |
| List data and restricted exchange | Restricted exchange is defined in [ProtocolSpecification], sections "Restricted function exchange with cmdOptions" and "Minimum restricted function exchange support". This document adds default rules for feature types that use standard-class functions. Feature types may impose stricter restrictions. §3.6 | §3.6 |
| List data and restricted exchange | Write with cmdControl partial: the server SHALL accept an xListData that contains at least one xData. It MAY accept an xListData with more than one xData. | clause not printed |
| List data and restricted exchange | Write with cmdControl delete: the server SHALL accept a deletion, using <SELECTORS>, of at least one xData. It MAY support deletion of more than one xData. | clause not printed |
| List data and restricted exchange | Read with cmdControl partial: the server SHALL accept a read, using <SELECTORS>, of at least one xData. It MAY return more than one xData. | clause not printed |
| List data and restricted exchange | Exchange of the complete function SHALL be supported in every case (operations on the whole xListData). | clause not printed |
| List data and restricted exchange | partial on PossibleOperationsClassifierType: present means filtering is permitted; absent means only a full operation. §3.10.1.37 | §3.10.1.37 |
| List data and restricted exchange | Presence of read on PossibleOperationsType means read is permitted. Presence of write means write is permitted. §3.10.1.38, §3.10.1.39, §3.10.1.40 | §3.10.1.38, §3.10.1.39, §3.10.1.40 |
| Scaled numbers, signs, and modes | scaledNumber = number * 10^scale. Omitted scale SHALL be read as 0, so the value equals number. number SHALL be set. These rules apply unless a clause says otherwise. §3.10.1.8.1 | §3.10.1.8.1 |
| Scaled numbers, signs, and modes | ScaledNumberSetType MAY contain gaps. The example value list is [1, 3, 7] and the example range list is [3..5, 8..13, 18..20]. §3.10.1.9.1 | §3.10.1.9.1 |
| Scaled numbers, signs, and modes | ScaledNumberRangeType: every scaled number from min to max is supported, unless a further constraint applies. A step size is given as an example of such a constraint and is not an element of this type. §3.10.1.10 | §3.10.1.10 |
| Scaled numbers, signs, and modes | EnergyDirectionEnumType consume: positive SHALL mean consumption and negative SHALL mean production. produce: positive SHALL mean production and negative SHALL mean consumption. The type may be applied to measurands other than energy, such as power or current. §3.10.1.14 | §3.10.1.14 |
| Scaled numbers, signs, and modes | EnergyModeEnumType: consume SHALL only consume; produce SHALL only produce; idle SHALL neither consume nor produce; auto MAY consume, produce, or be idle, on its own decision. §3.10.1.16.1 Table 6 | §3.10.1.16.1, Table 6 |
| Other value rules on these pages | label and description MAY carry human-readable strings, are always optional, and SHALL NOT be used for automation. The label is the short string; the description is the longer one. Length limits are in §5. §3.8 | §5, §3.8 |
| Other value rules on these pages | An empty element (ElementTagType) is a tag: present means true, absent means false. In this version the element SHALL have no content. Content added by a later version SHALL be ignored by a device that implements this version. §3.9, §3.10.1.1.1 | §3.9, §3.10.1.1.1 |
| Other value rules on these pages | Compatibility, as stated here, follows message content, not type names. A later version may rename types if the message stays compatible, and may add children to an element that was empty. The0.0 and type NewFooType with children in version 1.1.0. Those two version strings are the §3.9 | §3.9 |
| Other value rules on these pages | A server can notify its data to clients. §1.2 Subscription is how a device receives messages of interest without polling; the mechanism is in [ProtocolSpecification]. Binding connects functionally matching features; the mechanism is in [ProtocolSpecification]. | §1.2 |
| Other value rules on these pages | When DirectControl is used, OperatingConstraints SHALL also be considered if the same feature group links them. §3.7.2 | §3.7.2 |
| Other value rules on these pages | Vendor enumeration values SHALL use the EnumExtendType marker; the IANA PEN SHOULD be used. §3.10.1.5.1 | §3.10.1.5.1 |
| Other value rules on these pages | Vendor-defined device, entity, and feature types SHALL be marked vendor-specific. §2.1.3 | §2.1.3 |
| Other value rules on these pages | No acceptance or rejection codes are defined on these pages. resultData and errorNumber are indexed as Table 18 and Table 19 at. | Table 18, Table 19 |
| Time values | A zero xs:duration means now, unless the clause that uses it says otherwise. Negative durations are in the past and positive durations are in the future, relative to now. | clause not printed |
| Time values | AbsoluteOrRecurringTimeType is normally either dateTime alone, or one of these sets: month + dayOfMonth + time (one day, once a year); dayOfMonth + time (one day, once a month); calendarWeek + daysOfWeek + time (a weekday, once a year); month + dayOfWeekOccurrence + daysOfWeek + time (the n-th weekday of one month, once a year); daysOfWeek + time (a weekday, once a week); time alone (every day at that time). | clause not printed |
| Time values | dayOfWeekOccurrence is meaningful together with daysOfWeek when calendarWeek is not set. It selects which week of the month. At the unset element is spelled calenderWeek. | clause not printed |
| Time values | daysOfWeek may carry several days at once. | clause not printed |
| Time values | recurringIntervalStep selects a stride when not every occurrence is active. executionCount ends the series after that many occurrences. lastExecution ends it after an instant, and that instant need not be an occurrence. firstExecution sets a first time other than the next occurrence. | clause not printed |
| Time values | DayOfMonthType is 1 through 31. CalendarWeekType is 1 through 53.. | clause not printed |
| Time values | AddressDeviceType strings are limited to 256 characters and must match the pattern in section 5.. | clause not printed |
| resultData | Notifies an error that belongs to another function. A failed write is the stated example. | clause not printed |
| resultData | May stand in for an ordinary reply when no well-formed reply can be built in the same function group as that read. | clause not printed |
| resultData | errorNumber 0 is no error. Any value greater than 0 is an error. The named codes are in Table 19 (section 5). | Table 19 |
| resultData | Code 7 is a rejected command. Code 6 is a command that is not supported. Code 9 says binding is necessary for this command. Code 2 is timeout. Code 8 is an unsupported restricted combination of function exchange. | clause not printed |
| resultData | The text says further error numbers will be added later. It does not list them. | clause not printed |
| Actuator commands | actuatorLevelData.function is always present. value is required only for some functions; percentageAbsolute is the stated case. | clause not printed |
| Actuator commands | start, up, down, and stop are the motion or run commands. percentageAbsolute and absolute set a position or value. percentageRelative and relative change the current value. No acceptance or rejection rule is printed for this function. | clause not printed |
| Actuator commands | ActuatorSwitch on, on an accepted write, activates the actuator. In a notify or a reply, on means the actuator is active. off deactivates on an accepted write, and in a notify or reply means the actuator is not active. | clause not printed |
| Actuator commands | toggle is forbidden outside a write. An accepted write activates an inactive actuator and deactivates an active one. | clause not printed |
| Actuator commands | What on and off switch (the device, or one function of it) is an implementation choice. | clause not printed |
| Alarm | alarmCancelled withdraws an earlier alarm. underThreshold and overThreshold require thresholdId. | clause not printed |
| Alarm | alarmId is always the primary identifier. thresholdId is omitted when the alarm is not tied to a threshold. timestamp and alarmType should be present. | clause not printed |
| Bill write, signs, and update | From the feature server's point of view, a sale in total.value.value is negative and a purchase is positive. Position sales and purchases are accumulated into total. | clause not printed |
| Bill write, signs, and update | A single position, a single total value, or a single total cost may omit its sub-identifier. The omitted identifier equals "1". More than one requires the identifier., Table 28. | Table 28 |
| Bill write, signs, and update | positionCountMin and positionCountMax bound how many positions a related billData may contain. | clause not printed |
| Bill write, signs, and update | If billWriteable is "true", a client MAY write the related billData. If no billData with that billId exists yet, the client MAY still write the whole entry. The server has to take that write when it follows the rules of the matching billDescriptionData and billConstraintsData for that billId. | clause not printed |
| Bill write, signs, and update | updateRequired lets the server ask for an update of writable or changeable data that shares the primary identifier. The server SHALL allow only one responsible client to update that data. To ask, the server SHALL set updateRequired to "true". | clause not printed |
| Bill write, signs, and update | Even when updateRequired is "false", the server SHOULD still allow the responsible client to update the data. | clause not printed |
| Bill write, signs, and update | The server SHALL return updateRequired to "false" once billDescriptionData was updated successfully (if that data is writable or changeable), or once the other writable or changeable data for the same primary identifier was updated successfully. | clause not printed |
| Bill write, signs, and update | The server MAY withdraw the request at any time by setting updateRequired back to "false". The client does not have to stop an update already under way (the stated case is a write of several functions). | clause not printed |
| Bill write, signs, and update | chargingSummary should not be used to bill the customer, because it may hold approximated values. | clause not printed |
| Data tunnelling | Only call. No read-reply and no write. | clause not printed |
| Data tunnelling | header, header.purposeId, header.channelId, header.sequenceId, and payload SHALL be set. | clause not printed |
| Data tunnelling | The triple { purposeId, channelId, sequenceId } should be treated as unique for a communication from one node to another. Several communications in one system (a house is the stated setting) may run in parallel, and their triples are in general independent. | clause not printed |
| Data tunnelling | One dataTunnelingCall instance may exchange messages in both directions. Setup may still be one-sided: one side may decide which purposeId values it accepts and wait for a first incoming message before it sends. The other device may expose its own listening instance with its own purposeId values. | clause not printed |
| Data tunnelling | The server instance defines which data are exchanged, specifically the permitted header.purposeId values. The element rule says purposeId SHALL be set; that paragraph says "if used". | clause not printed |
| Data tunnelling | purposeId longer than 128 characters may be shortened by the receiver; the sender must allow for that. | clause not printed |
| Device configuration writes, bounds, and failsafe keys | value has exactly one child, and that child matches valueType., Table 39. | Table 39 |
| Device configuration writes, bounds, and failsafe keys | isValueChangeable "true": the server accepts changes of value from an appropriate client. Otherwise it declines. The bound client is the example of an appropriate client. | clause not printed |
| Device configuration writes, bounds, and failsafe keys | value.string longer than 512 characters may be shortened by the receiver. | clause not printed |
| Device configuration writes, bounds, and failsafe keys | Constraints, when present: valueRangeMin lower bound, valueRangeMax upper bound, valueStepSize step. The child type matches valueType. | clause not printed |
| Device configuration writes, bounds, and failsafe keys | pvCurtailmentLimitFactor is 0 to 100 percent (pct) of PV peak power that may be fed in at the grid connection point. peakPowerOfPvSystem is zero or positive, in W. | clause not printed |
| Device configuration writes, bounds, and failsafe keys | timeToAcChargePowerMax and timeToAcDischargePowerMax are zero or positive seconds (s): time now needed to reach the present maximum AC charge power, or discharge power. | clause not printed |
| Device configuration writes, bounds, and failsafe keys | maxCycleCountPerDay is zero or positive. Unit token 1. incentivesSimulationCyclesMax is a non-negative integer. | clause not printed |
| Device configuration writes, bounds, and failsafe keys | Failsafe keys, each scaledNumber when the row requires that type: failsafeConsumptionActivePowerLimit and failsafeProductionActivePowerLimit in W; failsafePositiveReactivePowerLimit and failsafeNegativeReactivePowerLimit in var; failsafePositiveCosPhiLimit and failsafeNegativeCosPhiLimit with unit 1; failsafeAcPowerSetpoint, failsafeDcPowerSetpoint, and failsafePccPowerSetpoint in W when used. These pages do not say when a failsafe value is applied, except failsafeDurationMinimum. | clause not printed |
| Device configuration writes, bounds, and failsafe keys | failsafeDurationMinimum, when used, is a duration with no unit. After heartbeats are lost, the appliance SHALL stay in the failsafe state at least that long. | clause not printed |
| Device configuration writes, bounds, and failsafe keys | communicationsStandard allows only iso15118-2ed1, iso15118-2ed2, or iec61851 in value.string. | clause not printed |
| Device configuration writes, bounds, and failsafe keys | Availability strings for PV strings and for batteries are Unknown, Disconnected, Connected, Available, and In operation, with the meanings in section 5. Grid connection is Unknown, Disconnected, or Connected. Inverter control mode is Power, PCC, or Auto. Battery chemistry strings are liIon, leadAcid, redoxFlow, and sodiumIon. | clause not printed |
| Device configuration writes, bounds, and failsafe keys | incentivesTimeoutIncentiveRequest is the longest wait for a usable refresh of the simple incentive table that is already committed. incentivesWaitIncentiveWriteable is how long the appliance waits before it allows a fresh copy of that table to be fetched. incentivesSimulationConcurrent "true" means a simulation-data scenario may run beside a committed-data scenario. | clause not printed |
| Device configuration writes, bounds, and failsafe keys | dischargingBelowTargetEnergyRequestPermitted says whether discharge below the target state of charge is allowed. | clause not printed |
| Device diagnosis states, heartbeat, and service time | normalOperation: ordinary operation, with no error or limitation stated. standby: waiting for a user, and listening for external commands. failure: a fault; normal function is likely absent. serviceNeeded: service is required; normal function may be absent. overrideDetected: an override was seen; ordinary operation or a safe mode may apply. inAlarm: an alarm or emergency; a user must act; ordinary operation or a safe mode may apply. notReachable: not reachable on its non-SPINE protocol; only a technology gateway that handles the usual link to the device may set this. finished: a temporary operation has ended; while this state lasts, ordinary operation is not in effect. temporarilyNotReady: not ready for ordinary operation for a time; maintenance is the stated example. off: the device is off and cannot operate. | clause not printed |
| Device diagnosis states, heartbeat, and service time | lastErrorCode should stay after a return to ordinary operation. The rule names operationState; the element is operatingState. | clause not printed |
| Device diagnosis states, heartbeat, and service time | upTime and totalUpTime cover the whole device when they sit on DeviceInformation, and otherwise only that entity's functionality, including nested children. Total time is since installation. Up time is since the last start. | clause not printed |
| Device diagnosis states, heartbeat, and service time | heartbeatCounter increases after each heartbeatTimeout, not on every transmission. If another device requests the function, the counter SHALL NOT increase, and heartbeatTimeout stays the fixed period rather than the time left until the next automatic notification. | clause not printed |
| Device diagnosis states, heartbeat, and service time | After each heartbeatTimeout period, a notification of this function SHALL be sent to every subscribed client. The element is that period, not the remaining time. | clause not printed |
| Device diagnosis states, heartbeat, and service time | nextService is either the next service instant or a duration that counts down to it. bootCounter counts boots finished since installationTime. | clause not printed |
| Device diagnosis states, heartbeat, and service time | powerSupplyCondition low and critical are capacity warnings. critical advises a battery change when the supply is a battery. | clause not printed |
| Direct control | Current values are the list entry whose timestamp is a zero-length duration (PT0S and PT0H are the The most recent entry SHALL have that zero duration. The server SHALL accept a write that adjusts current values only on such an instance., Table 49. | Table 49 |
| Direct control | A partial write is the stated way a client modifies power, energy, and the other changeable fields. | clause not printed |
| Direct control | If the matching is…Changeable element is true, the server accepts the change from an appropriate client and otherwise declines it. The bound client is the example. This pattern covers activityState, energyMode, power, and energy. | clause not printed |
| Direct control | power and energy are targets that should be followed as well as possible. power is the overall value; phases are not in this element. | clause not printed |
| Direct control | running: the activity is running. If changeable, a client MAY pause it or deactivate it. If sequenceId is set, the linked sequence's extra data must be taken into account. paused: paused; a client MAY activate or deactivate it, with the same sequence caveat. inactive: inactive; a client MAY activate it, with the same caveat. | clause not printed |
| Direct control | positiveEnergyDirection should be set on the description. Its allowed values are not listed on these pages. | clause not printed |
| Electrical connection | When powerSupplyType is dc, voltageType MAY be omitted, or if present SHALL be dc. When powerSupplyType is ac, voltageType MAY be omitted and then means ac, or it must be dc when the measured quantity is that AC link's DC offset. ac is forbidden when powerSupplyType is dc., Table 53. | Table 53 |
| Electrical connection | acMeasuredPhases, acMeasuredInReferenceTo, acMeasurementType, acMeasurementVariant, and acMeasuredHarmonic SHALL be omitted when powerSupplyType is dc. | clause not printed |
| Electrical connection | Harmonic "1" means the normal value, not a numbered harmonic, is measured. | clause not printed |
| Electrical connection | At least one permittedValuesSet is required when that function is used. The set type is ScaledNumberSetType. | clause not printed |
| Electrical connection | Characteristic meanings, all rule None: powerConsumptionMin / powerConsumptionMax minimum and maximum active power the related function can consume. powerConsumptionNominalMin / powerConsumptionNominalMax the nominal minimum and maximum consumption from the manufacturer's data sheet. powerProductionMin / powerProductionMax minimum and maximum active power it can produce. powerProductionNominalMin / powerProductionNominalMax the nominal production bounds from the data sheet. energyCapacityNominalMax nominal capacity from the data sheet. contractualConsumptionNominalMax / contractualProductionNominalMax nominal maximum active power allowed by contract, for consumption and for production. apparentPowerProductionNominalMax / apparentPowerConsumptionNominalMax nominal maximum apparent power from the data sheet, for production and for consumption. | clause not printed |
| Electrical connection | characteristicContext says which scope that characteristic applies to: the whole device including its entities, the entity, or the inverter, PV-string, or battery sub-entities. | clause not printed |
| Electrical connection | If positiveEnergyDirection is omitted on the connection description, it SHALL be read as consume. | clause not printed |
| Electrical connection | consumptionTime should be time in mode consume since the last reboot. productionTime should be time in mode produce since the last reboot. totalConsumptionTime should be time in consume since installation. totalProductionTime should be time in producing since installation. | clause not printed |
| Electrical connection | acConnectedPhases, when the supply is ac, should give the phase count, typically 1, 2, or 3.. | clause not printed |
| Electrical connection | acRmsPeriodDuration is the window over which an RMS value is computed, when the variant is rms. | clause not printed |
| HVAC commands present before the page break | currentOperationModeId SHALL be an operation mode, and if the relation list is used it SHALL be one of the modes that list attaches to the same systemFunctionId. A "true" changeable flag means the server accepts a change from an appropriate client; otherwise it declines. | clause not printed |
| HVAC commands present before the page break | currentSetpointId follows the same pattern against hvacSystemFunctionSetpointRelationListData. | clause not printed |
| HVAC commands present before the page break | Each system function's relation list SHALL name at least one operationModeId. | clause not printed |
| HVAC commands present before the page break | isOverrunActive should be "true" when an overrun affects that system function. The overrun model may be on another feature, entity, or device. | clause not printed |
| HVAC commands present before the page break | No operation-mode enumeration and no system-function-type enumeration are completed on these pages. | clause not printed |
| Generic client | A Generic client feature holds no data. Reads, writes, and calls toward servers are all permitted from it. | clause not printed |
| HVAC operation modes | auto, for heating, cooling, dhw and ventilation: the function follows a timetable, including its current setpoint. | clause not printed |
| HVAC operation modes | on, for those four functions: the function, setpoint included, does not follow a timetable. | clause not printed |
| HVAC operation modes | off, for heating and dhw: freeze protection, and not a physical switch-off. The freeze-protection setpoint may be given by a setpointId. | clause not printed |
| HVAC operation modes | off, for cooling: space cooling is not active. | clause not printed |
| HVAC operation modes | off, for ventilation: ventilation is not active. Humidity protection may stay active. | clause not printed |
| HVAC operation modes | eco, for those four functions: control, setpoint included, does not follow a timetable, and the setpoint differs from the one used for on. | clause not printed |
| HVAC overrun | While an overrun is active, some system functions (not all; the text cites §5.3.12.9) leave normal behaviour. When the overrun is inactive again, the system returns to normal operation. | §5.3.12.9 |
| HVAC overrun | active: triggered, not started. Matching isOverrunActive is false. | clause not printed |
| HVAC overrun | running: in progress. Matching isOverrunActive is true. | clause not printed |
| HVAC overrun | finished: MAY be used only as a notification immediately after completion. overrunStatus SHALL then become inactive. SHOULD NOT appear in a reply. Matching isOverrunActive is false. | clause not printed |
| HVAC overrun | inactive: MAY be a reply or a notification. A notification is allowed only when the overrun did not finish in the usual way, user deactivation given as the example. Matching isOverrunActive is false. | clause not printed |
| HVAC overrun | oneTimeDhw: one domestic-hot-water load, independent of the current mode or timetable. | clause not printed |
| HVAC overrun | party: remains in ordinary daytime running instead of stopping when the schedule would normally end it. | clause not printed |
| HVAC overrun | sgReadyCondition1, sgReadyCondition3, sgReadyCondition4: that SG Ready condition is applied. The text says to consider [SGReady]. sgReadyCondition2 is not a listed literal. | clause not printed |
| HVAC overrun | oneDayAway: replaces the normal daily routine with an out-of-home configuration. The text gives eco mode for the whole day as an example. | clause not printed |
| HVAC overrun | oneDayAtHome: replaces it with an at-home configuration. The text gives on mode for the whole day as an example. | clause not printed |
| HVAC overrun | oneTimeVentilation: one ventilation run, independent of the configured routine. | clause not printed |
| HVAC overrun | hvacSystemOff: HVAC system deactivated. Frost protection stays active. The system stays reachable, in a network-standby mode, for another configuration. | clause not printed |
| HVAC overrun | Vendor-specific overrun types may be added and are then outside the interoperability scope. | clause not printed |
| Identification patterns and sessions | eui48: identificationValue SHALL be read as an EUI-48 MAC address. Pattern SHALL be (([A-F]/[0-9]){2}\-){5}([A-F]/[0-9]){2}. | [A-F] |
| Identification patterns and sessions | eui64: identificationValue SHALL be read as an EUI-64 MAC address. Pattern SHALL be (([A-F]/[0-9]){2}\-){7}([A-F]/[0-9]){2}. | [A-F] |
| Identification patterns and sessions | userRfidTag: rule None. An RFID tag used for identification. | clause not printed |
| Identification patterns and sessions | A current session has a start and no end. A past session has both. | clause not printed |
| IncentiveTable tiers, boundaries and incentives | Unless an application says otherwise, tiers SHALL be read as stacked tiers. | clause not printed |
| IncentiveTable tiers, boundaries and incentives | Stacked: each tier's supply is upperBoundaryValue minus lowerBoundaryValue, available at that tier's incentives. Negative boundaries mean production; positive boundaries mean consumption. A tier's supply is available only after the supply of the tiers between it and zero is already used. If the actual value passes the upper end, the whole supply of that tier is used at its incentives. If the actual value is below the upper end and at least the lower end, the used part is the actual value minus the lower end. For production, the end that is farther from zero is lowerBoundaryValue, and the two ends swap the roles they have for consumption. | clause not printed |
| IncentiveTable tiers, boundaries and incentives | Unique, when an application uses that reading: only one tier's supply SHALL be active at a time. The boundary says when the tier is active, and its incentives then apply to the whole consumption or production, not only the slice inside the boundary. Negative boundaries mean production; positive mean consumption. Tier x applies only while consumption is below its upper end and at least its lower end. Below the lower end, a different matching tier applies. At or above the upper end, a different matching tier applies. | clause not printed |
| IncentiveTable tiers, boundaries and incentives | powerBoundary: electrical power. Positive values are power that can be consumed with the stated incentives. Negative values are power that can be produced with them. | clause not printed |
| IncentiveTable tiers, boundaries and incentives | energyBoundary: electrical energy, with the same positive and negative reading. | clause not printed |
| IncentiveTable tiers, boundaries and incentives | countBoundary: a count. | clause not printed |
| IncentiveTable tiers, boundaries and incentives | absoluteCost: an absolute cost in a stated currency. Positive values SHALL be costs. Negative values SHALL be profits. If a unit is also set, the cost SHALL be per that unit. | clause not printed |
| IncentiveTable tiers, boundaries and incentives | relativeCost: no currency. Unit SHALL be percentage (pct). Value SHALL be from 0% to 100%. | clause not printed |
| IncentiveTable tiers, boundaries and incentives | renewableEnergyPercentage: unit SHALL be percentage (pct). Value SHALL be from 0% to 100%. | clause not printed |
| IncentiveTable tiers, boundaries and incentives | co2Emission: unit SHALL be kg/Wh. Only positive values SHALL be used. | clause not printed |
| IncentiveTable tiers, boundaries and incentives | updateRequired "true": the server is asking the one responsible client to refresh writable or changeable data that share that primary identifier. The client must disregard the flag until such a refresh has succeeded. On success the server must clear the flag to "false". Only that one client may perform the refresh. With the flag already "false", the server still ought, in general, to take refreshes from that client. The server may drop the request whenever it chooses, by clearing the flag. §4.3.14.5.3. | §4.3.14.5.3 |
| LoadControl limits | Two approaches are named. Event-based control (loadControlEvent, loadControlState) is reserved. Limit-based control is the one specified here: a client-changeable limit affects the node. The household-overload case is an example, not a fixed limit. | clause not printed |
| LoadControl limits | If measurementId matches an electricalConnectionPermittedValueSetData entry, loadControlLimitData.value SHOULD contain only values from that permitted set. | clause not printed |
| LoadControl limits | If it matches an electricalConnectionParameterDescriptionData entry, that entry's elements SHOULD be considered for the limit. | clause not printed |
| LoadControl limits | If it matches a measurementDescriptionData entry, that entry's unit SHALL be ignored for the limit. | clause not printed |
| LoadControl limits | minValueLimit: the limit is a minimum. The corresponding value SHALL stay at or above it when isLimitActive is true and the printed condition limitType = obligation holds. The description column says the value of the matching loadControlLimitData should not go below the limit (value greater than or equal to minValueLimit). obligation is not a limitType literal; see open points. | clause not printed |
| LoadControl limits | maxValueLimit: the limit is a maximum. The corresponding value SHALL stay at or below it under the same printed condition. The description column uses value less than or equal to maxValueLimit. | clause not printed |
| LoadControl limits | signDependentAbsValueLimit: follow the passive sign convention. If a use case applies the active sign convention, the logic SHALL be reversed. A positive value limits only consumption. A negative value limits only the absolute value of production. | clause not printed |
| LoadControl limits | obligation: the limit must be held in every circumstance. Giving up comfort is allowed for however long that takes. Ordinary running is broken if holding the limit requires it. | clause not printed |
| LoadControl limits | recommendation: the limit ought to be held where that is possible. Giving up comfort is allowed briefly. Ordinary running ought to continue. | clause not printed |
| LoadControl limits | optimization: the limit MAY be considered as far as possible. Comfort loss SHOULD NOT be accepted. Normal operation shall not be interrupted. | clause not printed |
| LoadControl limits | Absent loadControlNodeData, or an absent isNodeRemoteControllable, means remote control is allowed ("true"). "false" refuses writes on the feature. | clause not printed |
| Measurement value state | valueState "outOfRange" and value at or above valueRangeMax: value SHALL be read as greater than valueRangeMax. | clause not printed |
| Measurement value state | valueState "outOfRange" and value at or below valueRangeMin: value SHALL be read as lower than valueRangeMin. | clause not printed |
| Measurement value state | The out-of-range rule cites §5.3.15.4.2 for the range elements. On these pages the range elements are in §4.3.16.6. | §5.3.15.4.2, §4.3.16.6 |
| Measurement value state | valueSource measuredValue is the sensor reading and is described as the more exact origin. calculatedValue is derived from other parameters and is less exact. empiricalValue may differ strongly and has no exact calculable relation. Those are the printed characterisations; no numeric error bound is given. | clause not printed |
| Measurement value state | Constraint applicability: full constraints for value and therefore for minValue and maxValue; only the two range ends for averageValue; no constraints for standardDeviation. | clause not printed |
| Messaging classes | logging: to be stored in a log. | clause not printed |
| Messaging classes | information: shown to the customer; lower priority. | clause not printed |
| Messaging classes | warning: shown to the customer; medium priority. | clause not printed |
| Messaging classes | alarm: shown to the customer; high priority. | clause not printed |
| Messaging classes | emergency: shown to the customer; very high priority. | clause not printed |
| Messaging classes | obsolete: marks an earlier message so that it need not stay on display. text SHOULD be omitted. | clause not printed |
| OperatingConstraints sequence shapes | For each supported xListData, exactly one of "no sequenceId", "all sequenceId" and "currently no sequence" SHALL hold. See the catalogue row. | clause not printed |
| OperatingConstraints sequence shapes | When sequenceId is set, the other elements of that xData relate to the matching power sequence, except maxCyclesPerDay, which never relates to a power sequence. | clause not printed |
| OperatingConstraints sequence shapes | The same entity may hold one feature instance under the "no sequenceId" rule and another under the "all sequenceId" / "currently no sequence" rules for the same functionality. Their xData children SHALL be disjoint and SHALL NOT contradict each other. | clause not printed |
| OperatingConstraints sequence shapes | For the "no sequenceId" case, the feature-group concept (§2.1.4, outside these pages) is recommended so the constraints stay tied to the real function. | §2.1.4 |
| OperatingConstraints sequence shapes | Duration example only: a compressor can be harmed by a start followed by too early a stop. No numeric duration is printed. | clause not printed |
| OperatingConstraints sequence shapes | Power range and power level are alternative models. Supporting either requires the power-description function. | clause not printed |
| Setpoint acceptance and rounding | A missing isSetpointChangeable means the server SHOULD accept changes. "false" means it SHALL refuse. "true" means it SHALL accept changes from an appropriate client. | clause not printed |
| Setpoint acceptance and rounding | A missing or "true" isSetpointActive means the setpoint is active. "false" means it is inactive. | clause not printed |
| Setpoint acceptance and rounding | A missing setpointType SHALL be read as valueAbsolute. | clause not printed |
| Setpoint acceptance and rounding | When setpointStepSize applies, the server must round a write that misses the step grid. | clause not printed |
| Setpoint acceptance and rounding | Absolute tolerance is added and subtracted. Percentage tolerance is multiplied by value and then added and subtracted. Both tolerances SHALL be positive; the percentage one MAY be zero. | clause not printed |
| SmartEnergyManagementPs binding, slots and sequences | Configuration is allowed only for the client that holds the server's binding. Each server has exactly one such client. A client may hold bindings to more than one server. A subscription is a separate step, and is recommended for a client that wants change updates. | clause not printed |
| SmartEnergyManagementPs binding, slots and sequences | If sequences contain flexibilities or alternatives, the server sends powerSequences configuration request call. The client may write a configuration or ignore the call, for a time or permanently. If the client does not configure, the server follows the configuration it first exposed, called its own preference. A received configuration that the server should consider is checked against the server's constraints. A valid one is taken over. | clause not printed |
| SmartEnergyManagementPs binding, slots and sequences | The two sides may agree a new configuration more than once, and also after the sequence has started, when the server allows it. Subscribed nodes are updated whenever sequence information, configuration or state changes. | clause not printed |
| SmartEnergyManagementPs binding, slots and sequences | A device that cannot freely change mode does not publish sequences it cannot switch to at that moment, until the situation is resolved. | clause not printed |
| SmartEnergyManagementPs binding, slots and sequences | Restrictions stated in the theory section, which the text says the later rules impose: a sequence has at least one slot and may have as many as needed; slot order cannot be swapped, and shifting one slot shifts the following slots; each pause or gap is an ordinary slot whose energy value is "0"; a fixed forecast has no constraints because shifting is not permitted (detail cited at §4.3.24.3.5.5.2). The list ends with "etc.", so it is not closed on this page. | §4.3.24.3.5.5.2 |
| SmartEnergyManagementPs binding, slots and sequences | A slot is determined only when slotNumber and defaultDuration are present, activation or deactivation is explicit or implicit, and the value forecast is determined. defaultDuration SHALL be greater than 0.. | clause not printed |
| SmartEnergyManagementPs binding, slots and sequences | A slot is undetermined when it is not determined, slotNumber is present, defaultDuration is absent, and the value forecast is determined. It has no activation flag of its own; execution follows the sequence state. | clause not printed |
| SmartEnergyManagementPs binding, slots and sequences | Any other slot is malformed and is not allowed. | clause not printed |
| SmartEnergyManagementPs binding, slots and sequences | Slot numbers SHALL ascend in time order. | clause not printed |
| SmartEnergyManagementPs binding, slots and sequences | A deactivated determined slot does not contribute. The sequence is scheduled as if that slot were absent. Applies to determined slots only. | clause not printed |
| SmartEnergyManagementPs binding, slots and sequences | An implicit schedule cannot change duration, start or end directly, and cannot be deactivated on its own. Start is the end of the previous slot, or the sequence start when there is no previous slot. | clause not printed |
| SmartEnergyManagementPs binding, slots and sequences | A schedule is configurable when it is constrained and the sequence permits configuration. Duration is configurable when minDuration and maxDuration are both present. optionalSlot "true" allows deactivation. An implicit schedule is not configurable. | clause not printed |
| SmartEnergyManagementPs binding, slots and sequences | Configuration list (alternatives.powerSequence inside a powerSequences configuration message; message definition cited at §4.3.24.4.4): slot numbers unique and ordered; a non-configurable slot need not be listed unless a later rule requires it; if listed, its schedule MAY be empty apart from slotNumber and SHOULD NOT contradict the slot information; if evaluated, that configuration SHALL be ignored. A configurable slot's schedule entry SHALL configure every option the slot allows. | §4.3.24.4.4 |
| SmartEnergyManagementPs binding, slots and sequences | A slot that has already finished cannot be configured, including one that could be configured earlier. Its schedule entry may still be present, and this specification gives that entry no further role. | clause not printed |
| SmartEnergyManagementPs binding, slots and sequences | The current slot SHALL be listed, SHALL NOT be deactivated, and MAY stay configurable or become non-configurable (server-specific). Future slots SHALL be listed whether or not they are configurable. | clause not printed |
| SmartEnergyManagementPs binding, slots and sequences | defaultDuration of the current slot covers the slot from its beginning to its end. It SHALL NOT shrink merely because part of the slot is already done. Paused phases do not by themselves require an update of defaultDuration. | clause not printed |
| SmartEnergyManagementPs binding, slots and sequences | Configurable duration with an energy valueType: energy stays nearly the same for every offered duration, so power falls when the duration grows and rises when it shrinks. With a power valueType: power stays nearly the same, so energy follows the duration. Both families SHALL NOT be provided on the same configurable-duration slot. | clause not printed |
| SmartEnergyManagementPs binding, slots and sequences | Duration combinations that are possible for both optional and non-optional determined slots: exact and not configurable; uncertain and not configurable; exact and configurable; uncertain and configurable. | clause not printed |
| SmartEnergyManagementPs binding, slots and sequences | Repetition: a sequence may repeat a short slot list, with a repetition counter, instead of unrolling every occurrence. This is said not to contradict §4.3.24.3.2. Detail is in §4.3.24.3.5.3, after these pages. | §4.3.24.3.2, §4.3.24.3.5.3 |
| SmartEnergyManagementPs binding, slots and sequences | Past sequence: was processed or at least offered, and is not offered now or later. state SHALL be completed or invalid. | clause not printed |
| SmartEnergyManagementPs binding, slots and sequences | Pre-announced sequence: can matter no earlier than now, and is not the current sequence. state SHALL be scheduled, scheduledPaused or inactive. | clause not printed |
| SmartEnergyManagementPs binding, slots and sequences | Current sequence: being processed. state SHALL be running or paused. The stated natural transition is scheduled to running, and scheduledPaused to paused. | clause not printed |
| SmartEnergyManagementPs binding, slots and sequences | Past group: only past sequences. Pre-announced group: only pre-announced sequences. Current group: exactly one current sequence SHALL be present; any number of past sequences MAY be present; a pre-announced sequence SHOULD NOT be present. | clause not printed |
| SmartEnergyManagementPs binding, slots and sequences | Once a pre-announced sequence turns into a past sequence, later refreshes of its former alternatives group must leave it out. Notifying that sequence's state by itself is still allowed. | clause not printed |
| SmartEnergyManagementPs binding, slots and sequences | A sequence has schedule information once alternatives.powerSequence.schedule exists and that element also has startTime. | clause not printed |
| SmartEnergyManagementPs binding, slots and sequences | The selection types in this subsection are limited to groups classed as pre-announced or current. | clause not printed |
| SmartEnergyManagementPs binding, slots and sequences | Chosen sequence: has schedule information. A pre-announced one SHALL be scheduled or scheduledPaused. A current one SHALL be running or paused. The server must start that pre-announced chosen sequence by itself when startTime arrives, while the sequence remains valid, unless some different sequence of the same group was already picked as chosen. The picker may be the bound client, via configuration, or the server, for an internal cause or because a user picked it. That start MAY enter paused at once if the previous state was scheduledPaused. Every current sequence SHALL be chosen. At most one sequence in a group can be chosen. | clause not printed |
| SmartEnergyManagementPs binding, slots and sequences | Optional sequence: no schedule information, and state is inactive. The server SHALL NOT start it on its own. Starting it requires a modification that makes it chosen. A pre-announced group MAY contain only optional sequences. | clause not printed |
| SmartEnergyManagementPs binding, slots and sequences | Unavailable sequence: neither chosen nor optional. It SHALL NOT have schedule information and SHALL be a past sequence. This definition is not about past groups. The server SHALL NOT execute it. | clause not printed |
| SmartEnergyManagementPs binding, slots and sequences | Modifiability, introduction only on these pages and marked informative: needed when the bound client changes startTime or endTime, the sequence state (pause, resume or abort of a current sequence), or slot data (durations, activation, energy or power), and also when an optional sequence is made chosen. Further conditions may depend on the data. The subsection continues after. | clause not printed |
| Sequence properties | A sequence is modifiable when sequenceRemoteControllable is available and true. Otherwise it is not. §c4.3.24.3.3.5.2 | clause not printed |
| Sequence properties | A sequence is interruptible when it is modifiable and operatingConstraintsInterrupt is present and at least one of isPausable and isStoppable is true. Otherwise it is not. Missing interrupt constraints assign both flags false. §c4.3.24.3.3.6.1 | clause not printed |
| Sequence properties | Only a current sequence, and partly a pre-announced sequence, may be interrupted and later continued by the bound client. Pause, resume, and abort of a current sequence follow the interrupt data and the state rules. A chosen sequence inside a pre-announced group may change as follows: scheduled may become scheduledPaused when the sequence is interruptible and isPausable is true; scheduledPaused may return to scheduled; and it may become an unavailable sequence by setting state to invalid when the sequence is interruptible and isStoppable is true. Those are direct changes. Indirect changes, such as configuring another sequence, are outside that list. §c4.3.24.3.3.6.2 | clause not printed |
| Sequence properties | Interrupting or resuming requires the bound client to tell the server to change state. The server accepts such a command only when the interruptibility above allows it. That process is in general independent of a client configuration. | clause not printed |
| Sequence properties | When a sequence is interruptible, constraints in operatingConstraintsInterrupt or operatingConstraintsDuration are considered by the bound client, in particular to avoid damage to the server. | clause not printed |
| Sequence properties | operatingConstraintsResumeImplication is available only when interrupt constraints are available and isPausable is available, and it is not considered when isPausable is false. | clause not printed |
| Sequence properties | A sequence has a modifiable sequence schedule when it is a chosen or an optional sequence, it is modifiable, and scheduleConstraints is available. Otherwise the schedule information is not modifiable. §c4.3.24.3.3.7.2 | clause not printed |
| Sequence properties | A bound client may modify the schedule information of a chosen sequence that has a modifiable schedule, and may assign schedule information to an optional sequence that has one. §c4.3.24.3.3.7.3 | clause not printed |
| Sequence properties | A sequence is configurable when it has a modifiable sequence schedule and it belongs to a current group or a pre-announced group. Otherwise it is not configurable. §c4.3.24.3.3.8.2 | clause not printed |
| Sequence properties | Configuration process, limited to current and pre-announced groups and to their chosen and optional sequences, called applicable sequences in that section: every optional sequence of a pre-announced group is configurable. Assigning schedule information to a configurable optional sequence makes it the chosen sequence; another chosen sequence of that group then becomes optional or, as an implementation choice, a past sequence. A current sequence does not become optional because another optional sequence of the group was configured; it stays the current sequence until it completes or is finally aborted. An applicable configurable sequence may be interruptible. It may have configurable slots; if it needs configurable slots, the sequence itself is configurable. A sequence may become configurable or stop being configurable at any time; that is up to the server and is implementation-specific, subject to process rules that restrict such a change. §c4.3.24.3.3.8.3 | clause not printed |
| Sequence properties | Becoming optional, or unavailable, changes the sequence’s information and can remove schedule information. Client configuration is in general independent of interruptibility, though an implementation or a further process rule may change interruptibility as a result. | clause not printed |
| Sequence properties | The server is remote controllable exactly when it has at least one configurable sequence. §4.3.24.3.4 | §4.3.24.3.4 |
| Sequence properties | nodeScheduleInformation does not contradict, and does not supersede, sequence-specific or slot-specific information. | clause not printed |
| Sequence properties | A sequence with schedule flexibility contains schedule constraints. A fixed forecast does not. §c4.3.24.4.1.1.4 | clause not printed |
| Permitted sequence types | fixed forecast: the client is given no control; the server schedule is autonomous. Announced before execution as the only pre-announced sequence of its group, or as the only current sequence if it was created suddenly and starts at once. It is a chosen sequence and schedule.endTime is set. It is not interruptible and not configurable. At least one slot; every slot is determined and has an implicit slot schedule, so the slots are not configurable. Once current, it stays non-interruptible and non-configurable. Slot-duration uncertainty can affect how precise the sequence end is. §c4.3.24.3.5.5.2 | clause not printed |
| Permitted sequence types | flexible chosen forecast: the server’s preference or current configuration, which it will run on its own unless the client changes schedule or state. Announced before execution as a chosen sequence inside a pre-announced group only. endTime may be set. It may be interruptible and it is configurable. At least one slot; every slot is determined; each slot's schedule is either constrained or implicit, under §4.3.24.3.2.7. Once current, the server may change interruptibility and configurability. §c4.3.24.3.5.5.3 | §4.3.24.3.2.7 |
| Permitted sequence types | flexible optional forecast: an option the server will not run on its own. The client can make it chosen. Announced as an optional sequence inside a pre-announced group only. It may be interruptible and it is configurable. Slot rules match the flexible chosen forecast. Becoming chosen corresponds to a change into that type. §c4.3.24.3.5.5.4 | clause not printed |
| Permitted sequence types | optional sequence-based immediate control: for a device that cannot forecast with the precision the text calls sufficient, yet can publish an optional task bounded above, below, or both. The client configures it before it starts, then may pause and resume within server constraints. Announced as an optional sequence inside a pre-announced group only. It is interruptible and configurable. Exactly one slot, and that slot is undetermined, so the slot itself is not configurable. schedule.endTime is not set unless the sequence has become a past sequence: the server does not announce it in advance or after schedule configuration, and the client does not configure it. Lack of a duration prevents a price forecast. Once current, it is no longer configurable. The server may change interruptibility for a time. The text says an abort by the server, on its own, is the more typical outcome for this type. §c4.3.24.3.5.5.5 | clause not printed |
| Identifiers, slots, overlap, consistency | Each alternatives group has a unique alternativesId among groups that are valid at the same time. A value is not reused immediately after the group is gone. The id is required for evaluation in restricted function exchange, in particular when a new sequence is notified into an existing group. The mechanism is in the protocol specification. §4.3.24.3.5.1 | §4.3.24.3.5.1 |
| Identifiers, slots, overlap, consistency | Each sequence has a unique sequenceId among sequences that are valid at the same time. An id is not reused immediately after sequences with that id have completed. The id is only a selector. It is not read as carrying order or any other extra information. §4.3.24.3.5.2 | §4.3.24.3.5.2 |
| Identifiers, slots, overlap, consistency | Every sequence has at least one slot. Slots of a sequence are all determined, or the sequence holds a single undetermined slot and no further slot. In a sequence that has at least one determined slot, at least one slot cannot be deactivated and always has a duration greater than 0 seconds. That does not limit deactivating the sequence itself. §c4.3.24.3.5.3.1 | clause not printed |
| Identifiers, slots, overlap, consistency | Under the repetition concept, repetitionsTotal is the number of executions and activeRepetitionNumber is the current one. In smartEnergyManagementPsData, slot information is read as the repetition now underway, except where a rule says something else, and that includes an already finished lower slot number while a later slot of that same repetition is current. Constraints usually, though not always, apply to each repetition. A slot configuration is treated as applying to every repetition. §c4.3.24.3.5.3.2 | clause not printed |
| Identifiers, slots, overlap, consistency | Pre-announced groups do not share a time range with each other, and a pre-announced group does not share a time range with a current group. A schedule, or the constraints on a schedule, of a sequence in one group must not meet a schedule, or the constraints on a schedule, of a sequence in a different group. Sequences inside one group may overlap. When one current group is present together with one or more pre-announced groups, or when two or more pre-announced groups are present, every pre-announced sequence in the later group carries both startTime and endTime on its schedule, or carries both earliestStartTime and latestEndTime on its sequence schedule constraints. §4.3.24.3.5.4 | §4.3.24.3.5.4 |
| Identifiers, slots, overlap, consistency | For a flexible schedule with determined slots, earliest start and latest end always frame the slots: the sum of slot durations fits that frame. A configuration that extends durations so the sum exceeds the frame is invalid and is rejected. At least one duration configuration of all slots fits the frame. §c4.3.24.4.1.1.5 | clause not printed |
| Identifiers, slots, overlap, consistency | A client orders received groups chronologically by §4.3.24.3.3.2, then orders current and pre-announced groups by the overlap rules, then applies §4.3.24.3.5 inside each group. §4.3.24.3.6 | §4.3.24.3.3.2, §4.3.24.3.5, §4.3.24.3.6 |
| Sign, time refresh, message shape | For this complex class, power and energy below zero are production and power and energy above zero are consumption. That is an implicit positiveEnergyDirection = consume. The basic PowerSequences class element positiveEnergyDirection is not used explicitly here. §4.3.24.3.7.1 | §4.3.24.3.7.1 |
| Sign, time refresh, message shape | Time-series slot values use the same sign for the server: positive consumption, negative production. Table 150 | Table 150 |
| Sign, time refresh, message shape | Supply-condition positiveEnergyDirection is a separate element, with consume and produce as in Table 136. | Table 136 |
| Sign, time refresh, message shape | Every time value that identifies an instant is updated on every message. A duration that does not change keeps the same value. §4.3.24.3.7.2 | §4.3.24.3.7.2 |
| Sign, time refresh, message shape | Inside one message, one sequence’s information is contiguous and is split into as few data groups as possible unless that message’s definition says otherwise. §4.3.24.3.7.3 | §4.3.24.3.7.3 |
| Binding, acknowledgement, classifiers | A server accepts one binding to a client for each server-entity instance. Further binding requests for that instance are rejected. §4.3.24.3.9 | §4.3.24.3.9 |
| Binding, acknowledgement, classifiers | If the bound client is no longer accessible, deleting the binding or continuing to wait is vendor-specific. Re-binding may then be possible only after a factory reset by the device owner. | clause not printed |
| Binding, acknowledgement, classifiers | A device that wants the data and does not configure flexibilities uses subscription or an explicit read, and does not create a binding. | clause not printed |
| Binding, acknowledgement, classifiers | Further binding detail is in the protocol specification. | clause not printed |
| Binding, acknowledgement, classifiers | The protocol specification’s acknowledgement concept applies. Bound peers should explicitly request acknowledgement when the message type permits it. §4.3.24.3.10.1 | §4.3.24.3.10.1 |
| Binding, acknowledgement, classifiers | Classifiers named in a message’s “When to send” subsection are the valid ones. Other classifiers are invalid for that message. “When received” usually names valid classifiers only. The overview is Table 119, not on these pages. §4.3.24.3.10.2 | Table 119, §4.3.24.3.10.2 |
| Information, cancellation, reads | Mutually exclusive processes are exposed in one alternatives element. Processes that run one after another, and cannot run together, are exposed in different alternatives elements. A server may combine both. §c4.3.24.4.1.1.1 | clause not printed |
| Information, cancellation, reads | One server instance does not expose processes that run at the same time, even partly. Those are separate server instances on different entities. §c4.3.24.4.1.1.3 | clause not printed |
| Information, cancellation, reads | A sequence that is no longer valid is cancelled. The server sends powerSequences information with classifier notify and sets that sequence to invalid, then removes the sequence id and obeys the reuse rule. A delete-notification may follow from restricted function exchange and is not recommended. The server cancels every announced sequence, including one already configured, that is no longer valid. A client that may have missed the notification should allow for lost packets and should explicitly request the sequences that are available. §c4.3.24.4.1.1.2 | clause not printed |
| Information, cancellation, reads | Allowed state.state values and their printed roles: running is executing now; paused is paused; scheduled will execute at the scheduled time and will then usually be running; scheduledPaused will execute at the scheduled time and will then usually be paused; inactive was offered as an optional choice and has not been configured; completed has finished; invalid has been cancelled. §c4.3.24.4.1.1.6 | clause not printed |
| Information, cancellation, reads | The server treats receipt of powerSequences information as erroneous. It sends notify to subscribers when data of one sequence on that instance change. It sends reply to a read, and that reply may be a complete or a restricted exchange. §4.3.24.4.1.2, §4.3.24.4.1.3 | §4.3.24.4.1.2, §4.3.24.4.1.3 |
| Information, cancellation, reads | A read uses classifier read and an empty smartEnergyManagementPsData. A restricted read may use Table 121. The server answers even when most traffic is unsolicited. The server never produces the request. A matching restricted reply contains only the sequence whose id equals the selector. An unknown sequenceId is an erroneous receipt. §4.3.24.4.2 | Table 121, §4.3.24.4.2 |
| Configuration request and configuration write | The call is a trigger from the server to its bound client, which may then write a configuration. Classifier call, and never to a client that is only subscribed. It may be sent once a client is bound and at least one sequence has flexibilities. If none have flexibilities, it is not sent. A sequenceId may name one sequence, or any permissive sequence of the same group, and is not used for a fixed forecast. Omitting sequenceId asks for a configuration of each alternatives group except fixed forecasts. §4.3.24.4.3 | §4.3.24.4.3 |
| Configuration request and configuration write | The server treats receipt of this call as erroneous. A failed transmission should be read as the client being unreachable or unable to process it, so no configuration will come. Absence of a configuration is not itself a problem. If none has arrived within 15 minutes, the server may re-announce its sequences and call again, or run as it would when standing alone, if it lacks time to keep waiting. Error handling is the manufacturer’s. For the user, the server should not behave differently from stand-alone operation. The printed recommendations are that a washing machine should start a cycle on its own configuration, and a battery storage may idle or run a maintenance cycle. §4.3.24.4.3.2, §4.3.24.4.3.4 | §4.3.24.4.3.2, §4.3.24.4.3.4 |
| Configuration request and configuration write | A configuration is a write with restriction information, from the bound client only. One command configures one sequence. Choosing one of several mutual alternatives selects that sequence. A later configuration of another alternative supersedes that choice. §4.3.24.4.4.1 | §4.3.24.4.4.1 |
| Configuration request and configuration write | Option A sets the start of the whole sequence. The server starts at that time and uses its own slot durations. The client uses this only when every slot duration is already set by the server. | clause not printed |
| Configuration request and configuration write | Option B sets the end of the whole sequence. The server deducts every slot's expected length, repetitions included, from that end, starts at the calculated time, and uses its own slot durations. The sum of expected durations should include slot-duration uncertainties so the sequence finishes no later than the configured end. The client uses this only when every slot duration is already set. | clause not printed |
| Configuration request and configuration write | Option C sets every configurable slot. The server applies those durations when the constraints meet its requirements. The client keeps the slot-number order from the server’s information, and sets at least the sequence start or the sequence end. This is the only option that can reconfigure a sequence that has already begun, while flexibilities remain. A configurable slot is one whose duration can change, one marked optional so it can be activated or deactivated, or both. | clause not printed |
| Configuration request and configuration write | A state change is a different operation from configuration. | clause not printed |
| Configuration request and configuration write | Write composition: classifier write; destination is the server’s smartEnergyManagementPsData; restricted function exchange, with payload cmd.function set to smartEnergyManagementPsData; cmdControl contains partial; the curtailed function contains only the data to modify, as Table 123. | Table 123 |
| Configuration request and configuration write | The server processes a configuration only when the classifier is write and the restriction elements are proper. It accepts data that fit the constraints of that sequenceId within the tolerance below, and only a write that configures all flexibilities offered for that one sequence. A configuration the sequence cannot fulfil is an erroneous receipt and, when an acknowledgement is to be sent, a negative acknowledgement with error number 7 (command rejected). A delayed configuration may miss a time constraint slightly; the server should accept that and correct it without announcing the correction, while the miss stays slight. The usual allowance on a time bound is 30 seconds. A configuration that is valid and changes nothing is not an error. An unknown sequenceId is an erroneous receipt. The server never produces this message. §4.3.24.4.4.2, §4.3.24.4.4.3, §4.3.24.4.4.4 | §4.3.24.4.4.2, §4.3.24.4.4.3, §4.3.24.4.4.4 |
| Direct state change | This is the direct control, as distinct from configuration. The bound client may request run, pause, or invalid in the introduction’s words. The permitted transitions in §c4.3.24.4.5.1.2 use the enumeration literals below. Indirect changes, including a chosen sequence becoming inactive because another sequence was configured, are outside this section. §c4.3.24.4.5.1.1 | clause not printed |
| Direct state change | The client may request a direct change only in these cases. Any other direct change is not requested. §c4.3.24.4.5.1.2 | clause not printed |
| Direct state change | Write composition matches the configuration write, with destination and cmd.function equal to smartEnergyManagementPsData, cmdControl containing partial, and the curtailed content of Table 124. | Table 124 |
| Direct state change | The server checks the request against those rules. A change that is not allowed is an erroneous receipt. The server never generates this message. §4.3.24.4.5.2, §4.3.24.4.5.3 | §4.3.24.4.5.2, §4.3.24.4.5.3 |
| Price | Price support is optional. The server treats a received notify or reply of price information as erroneous. write is the change in §4.3.24.4.8. The server sends notify to subscribers when a price on that instance changes, and reply to a read, complete or restricted. §4.3.24.4.6 | §4.3.24.4.8, §4.3.24.4.6 |
| Price | A price read uses read and an empty smartEnergyManagementPsPriceData, optionally the Table 126 selectors. The server answers if it supports price information. What it does when it does not support prices is not stated. The server never produces the request. A restricted reply contains only the price of the selected sequence. A sequenceId for which no price is available is an erroneous receipt. §4.3.24.4.7 | Table 126, §4.3.24.4.7 |
| Price | A price change is usually the answer after a calculation call. The client is then obliged to use the server’s current schedule in smartEnergyManagementPsData. A whole-sequence price needs complete sequence information. After start, the server may drop past slots, so the calculation should be requested and delivered before start. After a whole-sequence price has been delivered, a later calculation should still be possible if the server keeps past slots. §c4.3.24.4.8.1.1 | clause not printed |
| Price | The change is a write to smartEnergyManagementPsPriceData, restricted exchange, cmd.function set to that function, cmdControl containing partial, content as Table 127. The server never generates this message. §c4.3.24.4.8.1.2 | Table 127 |
| Price | A change from a device that is not the bound client may be treated as erroneous. The server should accept one only from its bound client. A valid answer to its own calculation request is evaluated, and later price changes should not be accepted; those extras should be treated as erroneous, and the server may start a new calculation request. A change with no prior calculation call should be treated as erroneous. A sequenceId the server did not ask for is an erroneous receipt. Use of a valid price is manufacturer-specific; the printed example is showing it on a device display. §4.3.24.4.8.2 | §4.3.24.4.8.2 |
| Price | The calculation call asks the bound client to price one sequence id. The sentence that names the answer calls it a power-sequences price-calculation response call. The data model given for the client’s answer is the price-information change. The sequence needs schedule information and every slot determined. Dispatch that call early enough that it arrives before the sequence starts. Classifier call. The server does not change a configuration the bound client already set, merely to obtain prices for other configurations. The server treats receipt of this call as erroneous. The server has to cope with errors returned to a request it issued; how it does so is up to the manufacturer. A negative acknowledgement may mean the client cannot calculate yet, for example because it does not yet have valid prices for the whole sequence period. §4.3.24.4.9 | §4.3.24.4.9 |
| Other feature behaviour on these pages | StateInformation has no rules section. isActive true means that entry is active. §4.3.25.3, Table 129 | §4.3.25.3, Table 129 |
| Other feature behaviour on these pages | SupplyCondition has no rules section. Relation cardinality is one condition to zero or more thresholds. §4.3.26.3, §4.3.26.6.1 | §4.3.26.3, §4.3.26.6.1 |
| Other feature behaviour on these pages | TaskManagement lists jobs of the named classes and is not the place those jobs are modified. This version’s tasks are jobs. A later version may add tasks that are not jobs; that sentence is about the future, not a data element here. Each relation entry sets exactly one of directControlRelated, hvacRelated, loadControlReleated, powerSequencesRelated, and smartEnergyManagementPsRelated. §4.3.28.2, §4.3.28.5.2 | §4.3.28.2, §4.3.28.5.2 |
| Other feature behaviour on these pages | If taskManagementOverviewData.remoteControllable is false, writes to features linked through the relation list are declined. If the element is absent, the default is true. Table 142 | Table 142 |
| Other feature behaviour on these pages | Support for threshold constraints is recommended when thresholds accept writes, and is permitted in other cases. Threshold rules are read mathematically. | clause not printed |
| Other feature behaviour on these pages | A printed time-discovery sequence: a new device calls timeDistributorEnquiryCall with isTimeDistributor true toward all devices; each distributor notifies timeDistributorData; the new device picks the highest priority and reads timeInformationData; the distributor replies with its current time. The class does not itself specify a synchronisation method that includes a precision, because of delays. An application may measure delays and synchronise using this class. The owner of a datum applies its own SPINE time to that datum. §4.3.30.2 | §4.3.30.2 |
| Other feature behaviour on these pages | isSynchronised is judged against the highest-priority distributor. Time should stay within 10 seconds of a commonly used internet NTP server. The printed example host is ptbtime1.ptb.de. If clockDrift is 1, the device should synchronise at least every 10 days, and after that interval it sets isSynchronised to false. §4.3.30.6.2 | §4.3.30.6.2 |
| Other feature behaviour on these pages | Devices that do not support timeDistributor should not be destinations of the enquiry call. The call has no elements. §4.3.30.7.2 | §4.3.30.7.2 |
| Other feature behaviour on these pages | A time series should be approached by reading the description first. updateRequired true means the server wants the client in charge to refresh the writeable or changeable data of that primary identifier. Until that update succeeds, the client ignores updateRequired. The server sets the flag back to false when the update succeeds. Only one responsible client can update that data. Even when the flag is false, the server should in general still allow updates from that client. The server may withdraw the request at any time by setting the flag back to false. Table 151 | Table 151 |
| Other feature behaviour on these pages | Time-table slot count and slot times are changeable only when the matching description flag is true. Added slots do not overlap existing slots. Slot count and times may instead be static and device-specific. §4.3.32.2, Table 156 | §4.3.32.2, Table 156 |
| Other feature behaviour on these pages | Chapter 5 is the class catalogue, to be read as equivalent to the XSD. Function and element rules that give a class a more specific meaning are in the feature types. Standard classes and complex classes are §2.2, not on these pages. §5.1 | §2.2, §5.1 |
| Other feature behaviour on these pages | An incentive table defines tiers. Inside a tier’s boundaries, that tier’s incentive applies. A price incentive can be read as a price table. Other incentives exist; the printed example is CO2 emission. §5.2.1.1 | §5.2.1.1 |
| IncentiveTable | incentiveTableDescriptionData carries the tier, boundary, and incentive kinds, plus further elements. §5.2.1.3.1 | §5.2.1.3.1 |
| IncentiveTable | tariffWriteable records whether a client may write that incentive table. §5.2.1.3 Table 160 | §5.2.1.3, Table 160 |
| IncentiveTable | updateRequired asks the bound client for an update. Table 160 | Table 160 |
| IncentiveTable | slotIdSupport records whether timeSlotId is supported for the matching tariff in incentiveTableData. Table 160 | Table 160 |
| IncentiveTable | switchToTierIdWhenLower: the linked tier becomes active if lowerBoundaryValue is gone below. switchToTierIdWhenHigher: the linked tier becomes active if upperBoundaryValue is gone above. Table 161 | Table 161 |
| IncentiveTable | fixedCost: the cost incentive SHALL NOT vary over time. dynamicCost: it MAY vary over time. Table 162 | Table 162 |
| IncentiveTable | A powerBoundary SHALL be electrical power. An energyBoundary SHALL be electrical energy. A countBoundary SHALL be a count. Table 163 | Table 163 |
| IncentiveTable | Incentive-type rules print None for absoluteCost, relativeCost, renewableEnergyPercentage, and co2Emission. Table 164 | Table 164 |
| IncentiveTable | incentiveTableConstraintsData is where the server states how many tiers, boundaries, incentives, and slots are allowed. The constraint counts matter when a client writes a table: maxTiersPerTariff, maxBoundariesPerTier, maxIncentivesPerTier, slotCountMax. §5.2.1.4.1; Table 165 | §5.2.1.4.1, Table 165 |
| IncentiveTable | No numeric default, heartbeat, or timeout for an incentive table is printed on these pages. The device-configuration keys that mention an incentive table are under DeviceConfiguration below. They do not print a number either. | clause not printed |
| SmartEnergyManagementPs — model (element table, not marked informative) | The class groups pieces of PowerSequences (§5.3.19) and of OperatingConstraints so that related parts travel together. The term power sequence is still used. §5.2.3.1.2 | §5.3.19, §5.2.3.1.2 |
| SmartEnergyManagementPs — model (element table, not marked informative) | Formal relation printed in the informative theory section, and matched by the element cardinalities: one sequence has 1..m slots; one slot belongs to exactly one sequence; one pair of sequenceId and slotNumber identifies a slot. Slot numbers are independent across sequences. §5.2.3.1.3; Table 166 | §5.2.3.1.3, Table 166 |
| SmartEnergyManagementPs — model (element table, not marked informative) | alternatives.powerSequence is 1..unbounded. powerTimeSlot is 1..unbounded. valueList.value is 0..unbounded. price on the price function is 0..unbounded. Table 166; Table 169 | Table 166, Table 169 |
| SmartEnergyManagementPs — model (element table, not marked informative) | Sequence description text is xs:string of 1..60 characters. Slot description length SHALL NOT exceed 60 characters. Table 166 | Table 166 |
| SmartEnergyManagementPs — model (element table, not marked informative) | supportsSingleSlotSchedulingOnly true: one client configuration command may modify only one slot. Table 166 | Table 166 |
| SmartEnergyManagementPs — model (element table, not marked informative) | supportsReselection false: inside one alternatives group the client may select a sequence only once. True: the server does not cap reselection, while process rules and data still allow configuration. Table 166 | Table 166 |
| SmartEnergyManagementPs — model (element table, not marked informative) | totalSequencesCountMax counts every sequence in the message, in any state. Table 166 | Table 166 |
| SmartEnergyManagementPs — model (element table, not marked informative) | nodeRemoteControllable false disables remote energy management; any other value enables it. It reflects the user's own remote-control choice. Table 166 | Table 166 |
| SmartEnergyManagementPs — model (element table, not marked informative) | sequenceRemoteControllable is the per-sequence client-configuration flag. Table 166 | Table 166 |
| SmartEnergyManagementPs — model (element table, not marked informative) | elapsedSlotTime and remainingSlotTime count running time and stay constant during paused. remainingPauseTime is how long the active slot may still be paused. Table 166 | Table 166 |
| SmartEnergyManagementPs — model (element table, not marked informative) | Duration limits: activeDurationMin and activeDurationMax bound an uninterrupted run; pauseDurationMin and pauseDurationMax bound the pause after an activity; activeDurationSumMin and activeDurationSumMax bound total active time. Table 166 | Table 166 |
| SmartEnergyManagementPs — model (element table, not marked informative) | maxCyclesPerDay is the maximum number of starts per day. Table 166 | Table 166 |
| SmartEnergyManagementPs — model (element table, not marked informative) | Slot window: earliestStartTime, latestEndTime, and, when duration is configurable, minDuration and maxDuration. Table 166 | Table 166 |
| SmartEnergyManagementPs — model (element table, not marked informative) | optionalSlot true allows slotActivated to keep or drop the slot. Table 166 | Table 166 |
| SmartEnergyManagementPs — model (element table, not marked informative) | resumeEnergyEstimated is an estimate of extra energy before normal operation resumes after a pause, and it is not added to slot values. resumeCostEstimated is the estimated extra cost. Table 166 | Table 166 |
| SmartEnergyManagementPs — model (element table, not marked informative) | greenest true: the client should aim at minimum non-renewable energy. cheapest true: the client should aim at the lowest energy cost of this sequence. Table 166 | Table 166 |
| SmartEnergyManagementPs — model (element table, not marked informative) | valueSource is said to express how reliable the forecast is. The literal list is Table 246. Table 166 | Table 246, Table 166 |
| SmartEnergyManagementPs — model (element table, not marked informative) | alternativesId is not a function identifier. The identifiers are description.sequenceId and powerTimeSlot.schedule.slotNumber. §5.2.3.2.1.3 | §5.2.3.2.1.3 |
| SmartEnergyManagementPs — model (element table, not marked informative) | Schedule startTime and endTime, for both the sequence and the slot, are typed xs:duration. These pages do not say whether that duration is relative to now. Table 166 | Table 166 |
| SmartEnergyManagementPs — model (element table, not marked informative) | The configuration-request call carries one sequenceId, the sequence the server prefers. The prose also says the server may ask for one sequence or for all. No second element encodes all. §5.2.3.2.2.1; Table 168 | §5.2.3.2.2.1, Table 168 |
| SmartEnergyManagementPs — model (element table, not marked informative) | The price-calculation call asks a client to price a sequence the server cannot price. The client may then write that price to the server. §5.2.3.2.4.1. The same paragraph names powerSequencePriceCalculationRequestCall, while the function defined here is smartEnergyManagementPsPriceCalculationRequestCall. | §5.2.3.2.4.1 |
| SmartEnergyManagementPs — model (element table, not marked informative) | Both call functions print identifiers None and selectors None. | clause not printed |
| SmartEnergyManagementPs — model (element table, not marked informative) | No failsafe number, heartbeat interval, or timeout number for this class is printed on these pages. | clause not printed |
| SmartEnergyManagementPs — informative guidance | A sequence is either a fixed energy or power forecast, or a forecast a client may shift, choose, or configure. | clause not printed |
| SmartEnergyManagementPs — informative guidance | The server exposes at least one sequence when a process is about to start: fixed, flexible (with or without alternatives), or a mixture. | clause not printed |
| SmartEnergyManagementPs — informative guidance | The server should notify configuration and state changes. | clause not printed |
| SmartEnergyManagementPs — informative guidance | If there is flexibility or an alternative, the server can send a configuration-request call. The client may configure, or ignore the call for a time or for good. If the client does not configure, the server keeps the configuration it first exposed. | clause not printed |
| SmartEnergyManagementPs — informative guidance | If the client writes a configuration, the server checks it against the constraints the server laid out. A valid configuration is taken over. | clause not printed |
| SmartEnergyManagementPs — informative guidance | Client and server may renegotiate after that sequence has already started, when the server allows another round. On each change of information, configuration, or state, and when a sequence completes, the server should update subscribed nodes. | clause not printed |
| SmartEnergyManagementPs — informative guidance | A new process repeats the same mechanisms. | clause not printed |
| SmartEnergyManagementPs — informative guidance | Pausing: the sequence is pausable when operatingConstraintsInterrupt.isPausable is true, remotely controllable when state.sequenceRemoteControllable is true, and the node allows configuration when nodeScheduleInformation.nodeRemoteControllable is true. The client may then halt the running sequence and continue it later, provided the constraints still hold. | clause not printed |
| SmartEnergyManagementPs — informative guidance | The device itself may start again so that its configured limits stay satisfied. It then SHALL tell every subscribed client. That SHALL is inside the informative section. | clause not printed |
| SmartEnergyManagementPs — informative guidance | Slot times the informative section says to consider: startTime, endTime, defaultDuration, durationUncertainty, earliestStartTime, latestEndTime. Actual duration may lie between defaultDuration - durationUncertainty and defaultDuration + durationUncertainty. | clause not printed |
| SmartEnergyManagementPs — informative guidance | earliestStartTime is the low end of a shift. latestEndTime is the high end. | clause not printed |
| SmartEnergyManagementPs — informative guidance | Slots may be mandatory or optional. A time gap between slots is permitted; the text prefers a normal slot whose energy value is 0. | clause not printed |
| SmartEnergyManagementPs — informative guidance | How many slots and which value types a manufacturer models is the manufacturer's choice. | clause not printed |
| SmartEnergyManagementPs — informative guidance | Three uses of several sequences: alternatives the client chooses; behaviour in different time frames; or a mixture. The alternatives group is the root element alternatives of smartEnergyManagementPsData, same idea as PowerSequences §5.3.19.1.3. | §5.3.19.1.3 |
| SmartEnergyManagementPs — informative guidance | Flexibility is said to come from configuration flags, from how many sequences sit in an alternatives group, and from whether a sequence or its slots can shift. | clause not printed |
| SmartEnergyManagementPs — informative guidance | The server may ask for a price calculation, for example to show a price. A sequence may be a fixed forecast with no flexibility. | clause not printed |
| ActuatorLevel and ActuatorSwitch | actuatorLevelData sets the wanted mode or reads the actual mode. value is required only for some function literals; percentageAbsolute is the case the element text names. §5.3.1.2.1; Table 172 | §5.3.1.2.1, Table 172 |
| ActuatorLevel and ActuatorSwitch | Description data are the non-changing part and can hold levelDefaultUnit, which the text ties to some absolute commands. §5.3.1.3.1 | §5.3.1.3.1 |
| ActuatorLevel and ActuatorSwitch | Both actuator-level functions have no selectors. | clause not printed |
| ActuatorLevel and ActuatorSwitch | ActuatorSwitch models on, off, and toggle. Whether that affects the whole device or one feature is an implementation matter. Separate features may be separate instances on different node addresses. §5.3.2.1 | §5.3.2.1 |
| ActuatorLevel and ActuatorSwitch | The switch description is typically non-changing. No selectors. §5.3.2.3.1 | §5.3.2.3.1 |
| ActuatorLevel and ActuatorSwitch | No range, timeout, or failsafe for either class is printed. | clause not printed |
| Alarm | An alarm may come from crossing a threshold (class Threshold, §5.3.27) or from some other event that a later version of this specification would model. §5.3.3.1 | §5.3.27, §5.3.3.1 |
| Alarm | alarmListData is used to notify, or as the body of a read reply. Which elements apply depends on the alarm type. §5.3.3.2.1 | §5.3.3.2.1 |
| Alarm | alarmCancelled, underThreshold, and overThreshold are the only literals in Table 179. | Table 179 |
| Alarm | measuredValue is the measured value that exceeded the threshold. evaluationPeriod is the period in which the alarm is valid, when one can be stated. timestamp is the creation time. Table 178 | Table 178 |
| Alarm | Selectors: alarmId, scopeType. | clause not printed |
| Alarm | No acknowledgement rule, timeout, or latch duration is printed. | clause not printed |
| Bill | A bill has a total and zero or more position entries that compose that total. valueId and costId link values and costs inside one billData. billId is the id used by the other bill functions and outside the class. §5.3.4.2.1 | §5.3.4.2.1 |
| Bill | The descriptive fields sit on billData so a client can write a bill in one write. | clause not printed |
| Bill | position.timePeriod is for a position whose time is not the total's time. Table 180 | Table 180 |
| Bill | position.value.value and position.cost.cost can be negative. valuePercentage and costPercentage are shares of the total and, the text says, cannot express mixed signs. Table 180 | Table 180 |
| Bill | chargingSummary may be sent while charging is still going on, and more than once. Table 181 | Table 181 |
| Bill | Constraints (positionCountMin, positionCountMax) matter when the linked bill is writable. The client compares them with its own constraints and then writes. §5.3.4.3.1 | §5.3.4.3.1 |
| Bill | The description says whether that bill is writable, which billType values billId supports, and whether updateRequired asks the client for an update. sessionId names the session that produced the bill. §5.3.4.4.1; Table 185 | §5.3.4.4.1, Table 185 |
| Bill | No currency default, scale default, or timeout is printed. Selectors are billId and scopeType on billListData, and billId on the other two functions. | clause not printed |
| BindingManagement | A binding joins the binding client with the binding server. It is there to make partner choice easier than configuration done only by hand. §5.3.5.1 | §5.3.5.1 |
| BindingManagement | Only a client may initiate a binding. After it exists, the client may act on the server according to the bound functionality. An example in the text is a server that accepts load-management configuration and tells the client when parameters change. The exact proceedings are out of scope of this document. | clause not printed |
| BindingManagement | bindingManagementEntryListData can store the bindings on the device. If another device reads the list, only bindings with that requester should be returned. §5.3.5.2.1 | §5.3.5.2.1 |
| BindingManagement | bindingManagementRequestCall is sent by a node-management-capable entity to a node-management-capable entity on another device. clientAddress is one of the sender's client-role features. serverAddress is a server-role feature of the other device. serverFeatureType is included for verification. §5.3.5.3.1; Table 187 | §5.3.5.3.1, Table 187 |
| BindingManagement | The receiver accepts or declines and answers with an acknowledgement that carries resultData. errorNumber 0 accepts. Any other value declines. The meaning of those other codes is out of scope; the acknowledgement is defined in [ProtocolSpecification], section Acknowledgement message. | clause not printed |
| BindingManagement | bindingManagementDeleteCall deletes a binding between the sender and another device. Clients and servers may both send it. §5.3.5.4.1 | §5.3.5.4.1 |
| BindingManagement | Both call functions have no selectors. | clause not printed |
| BindingManagement | No binding lifetime, heartbeat, or retry timing is printed. | clause not printed |
| DataTunneling | The model carries proprietary protocol data and can address other nodes. SPINE will not define a specific protocol for it. The use of purposeId, channelId, sequenceId, and payload is proprietary. §5.3.6.1 | §5.3.6.1 |
| DataTunneling | It is not a way to extend SPINE classes. A technology mapping would not be standardisable, and tunnelled data is supposed to stay visibly proprietary. Committees may instead add real classes when a mapping is needed. The text names messagingListData and timeInformationData as that kind of class. | clause not printed |
| DataTunneling | The set { purposeId, channelId, sequenceId } should be treated as unique for traffic from one node to another. Other conversations in the same system are independent. | clause not printed |
| DataTunneling | A call instance is in general bidirectional. Setup can still be one-sided: one side may accept only some purposeId values and may wait for a first inbound call before it sends. The other device may expose its own listening functionality with its own purposeId values. | clause not printed |
| DataTunneling | Calls only. Read-reply and write are not supported. | clause not printed |
| DataTunneling | sequenceId orders payloads for one purposeId plus channelId, and is not another class's sequenceId. Table 189 | Table 189 |
| DataTunneling | No length limit, timeout, or checksum rule for payload is printed. Selectors: none. | clause not printed |
| DeviceClassification | Manufacturer data are usually not writable (hard-coded or preconfigured). User data are usually writable by a user or application. §5.3.7.2.1; §5.3.7.3.1 | §5.3.7.2.1, §5.3.7.3.1 |
| DeviceClassification | Except powerSource, the string elements have no format imposed by the model. | clause not printed |
| DeviceClassification | powerSource is informative: the source the device is designed for, not the source it ends up connected to. Table 190 | Table 190 |
| DeviceClassification | manufacturerNodeIdentification can still identify a device after it leaves the network and returns with a different node address. The three user elements mirror the three manufacturer counterparts. Table 190; Table 192 | Table 190, Table 192 |
| DeviceClassification | No selectors on either function. | clause not printed |
| DeviceClassification | No length facet is printed for DeviceClassificationStringType. | clause not printed |
| DeviceConfiguration | Used for interoperable facts that the ordinary classes do not carry, instead of DataTunneling or another proprietary model. Some keys are already defined and listed in Table 196. The static part is §5.3.8.3; the live value is §5.3.8.2. §5.3.8.1 | Table 196, §5.3.8.3, §5.3.8.2, §5.3.8.1 |
| DeviceConfiguration | A vendor may add a keyName, and must mark it vendor-specific. The marking rule is in the protocol specification, section title "Rules for vendor specific extensions". Table 195 | Table 195 |
| DeviceConfiguration | valueType chooses exactly one arm. isValueChangeable says whether a client may change that key. Table 195; Table 193 | Table 195, Table 193 |
| DeviceConfiguration | unit is optional: not every key has one. Table 195 | Table 195 |
| DeviceConfiguration | When a value has a range, deviceConfigurationKeyValueConstraintsListData can carry an upper bound, a lower bound, and a step size. The elements of that function are not on these pages. §5.3.8.4.1 | §5.3.8.4.1 |
| DeviceConfiguration | Subscribed clients are notified when a value changes. The notify example is §5.3.8.2.4.2 | §5.3.8.2.4.2 |
| DeviceConfiguration | Key meanings that are limits, defaults, failsafe values, or waits (no numeric value is printed for any of them): | clause not printed |
| DeviceConfiguration | Locators: Table 196. | Table 196 |
| Partial filters in labelled examples | alarmListData notify, partial filter abbreviated in the extract. §5.3.3.2.4.1 | §5.3.3.2.4.1 |
| Partial filters in labelled examples | billConstraintsListData read. §5.3.4.3.4.1 | §5.3.4.3.4.1 |
| Partial filters in labelled examples | deviceConfigurationKeyValueListData read. §5.3.8.2.4.1 | §5.3.8.2.4.1 |
| Device diagnosis states | Literal: normalOperation; Meaning on these pages: Ordinary operation, with no error and no limitation. | clause not printed |
| Device diagnosis states | Literal: standby; Meaning on these pages: The device waits for a person and for external commands on its communications protocol. | clause not printed |
| Device diagnosis states | Literal: failure; Meaning on these pages: A failure is present. The device cannot run as intended, and ordinary function is likely absent. | clause not printed |
| Device diagnosis states | Literal: serviceNeeded; Meaning on these pages: Some service is required. Ordinary function may be absent. | clause not printed |
| Device diagnosis states | Literal: overrideDetected; Meaning on these pages: An override was detected. Ordinary operation may continue, or a safe mode may apply. | clause not printed |
| Device diagnosis states | Literal: inAlarm; Meaning on these pages: An alarm or emergency needs a person. Ordinary operation may continue, or a safe mode may apply. | clause not printed |
| Device diagnosis states | Literal: notReachable; Meaning on these pages: Unreachable on the device's non-SPINE protocol. Only a technology gateway that carries that device's ordinary communication may set this state. | clause not printed |
| Device diagnosis states | Literal: finished; Meaning on these pages: A temporary operation has ended. Ordinary operation stays absent while this state remains. | clause not printed |
| Device diagnosis states | Literal: temporarilyNotReady; Meaning on these pages: Not ready for ordinary operation for a while. Maintenance is the printed example. | clause not printed |
| Device diagnosis states | Literal: off; Meaning on these pages: The device is off and cannot operate. | clause not printed |
| Electrical connection | Literal: powerConsumptionMin; Meaning on these pages: Lowest active power the related function can take. | clause not printed |
| Electrical connection | Literal: powerConsumptionMax; Meaning on these pages: Highest active power the related function can take. | clause not printed |
| Electrical connection | Literal: powerConsumptionNominalMin; Meaning on these pages: Datasheet nominal minimum active consumption. | clause not printed |
| Electrical connection | Literal: powerConsumptionNominalMax; Meaning on these pages: Datasheet nominal maximum active consumption. | clause not printed |
| Electrical connection | Literal: powerProductionMin; Meaning on these pages: Lowest active power the related function can produce. | clause not printed |
| Electrical connection | Literal: powerProductionMax; Meaning on these pages: Highest active power the related function can produce. | clause not printed |
| Electrical connection | Literal: powerProductionNominalMin; Meaning on these pages: Datasheet nominal minimum active production. | clause not printed |
| Electrical connection | Literal: powerProductionNominalMax; Meaning on these pages: Datasheet nominal maximum active production. | clause not printed |
| Electrical connection | Literal: energyCapacityNominalMax; Meaning on these pages: Datasheet nominal capacity. | clause not printed |
| Electrical connection | Literal: contractualConsumptionNominalMax; Meaning on these pages: Contractual cap on active consumption. | clause not printed |
| Electrical connection | Literal: contractualProductionNominalMax; Meaning on these pages: Contractual cap on active production. | clause not printed |
| Electrical connection | Literal: apparentPowerProductionNominalMax; Meaning on these pages: Datasheet nominal maximum apparent production. | clause not printed |
| Electrical connection | Literal: apparentPowerConsumptionNominalMax; Meaning on these pages: Datasheet nominal maximum apparent consumption. | clause not printed |
| HVAC | Literal: auto; System functions named: heating, cooling, dhw, ventilation; Meaning on these pages: The function follows a time table, and the active setpoint changes with that table. | clause not printed |
| HVAC | Literal: on; System functions named: heating, cooling, dhw, ventilation; Meaning on these pages: Control, a setpoint being the printed case, does not follow a time table. | clause not printed |
| HVAC | Literal: off; System functions named: heating, dhw; Meaning on these pages: Freeze protection, rather than a physical switch-off. A setpointId may carry the freeze-protection temperature. | clause not printed |
| HVAC | Literal: off; System functions named: cooling; Meaning on these pages: Space cooling is not active. | clause not printed |
| HVAC | Literal: off; System functions named: ventilation; Meaning on these pages: Ventilation is not active. Protection such as humidity protection may still be active. | clause not printed |
| HVAC | Literal: eco; System functions named: heating, cooling, dhw, ventilation; Meaning on these pages: Control does not follow a time table, and the setpoint differs from the one used for on. The printed function cell capitalises Heating. | clause not printed |
| HVAC | Literal: oneTimeDhw; Meaning on these pages: One domestic-hot-water load, independent of the current mode and of a time table. | clause not printed |
| HVAC | Literal: party; Meaning on these pages: Day operation continues instead of turning off at the usual time. The printed case is heating held on the day setpoint until this overrun finishes, regardless of mode and time table. | clause not printed |
| HVAC | Literal: sgReadyCondition1; Meaning on these pages: SG Ready condition 1 is applied. The definition is [SGReady], not on these pages. | clause not printed |
| HVAC | Literal: sgReadyCondition3; Meaning on these pages: SG Ready condition 3 is applied. Same external reference. | clause not printed |
| HVAC | Literal: sgReadyCondition4; Meaning on these pages: SG Ready condition 4 is applied. Same external reference. | clause not printed |
| HVAC | Literal: oneDayAway; Meaning on these pages: The usual daily routine is replaced by an away setup. Eco mode for the whole day is the printed example. | clause not printed |
| HVAC | Literal: oneDayAtHome; Meaning on these pages: The usual daily routine is replaced by an at-home setup. On mode for the whole day is the printed example. | clause not printed |
| HVAC | Literal: oneTimeVentilation; Meaning on these pages: Ventilation runs once, independent of the configured routine. | clause not printed |
| HVAC | Literal: hvacSystemOff; Meaning on these pages: The HVAC system is deactivated. Freeze protection remains. The system stays in the printed network-standby condition and can still be reached for configuration. | clause not printed |
| Load control | Event-based, using loadControlEventListData and loadControlStateListData. An external contract partner or an energy manager changes demand or production. The household or the device owner may reject the change. The text says a rejection may cost more or earn a smaller reward. Prices and the allowed number of rejections are not specified; the state text says the number depends on the household owner's contract (Table 238). | Table 238 |
| Load control | Limit-based, using loadControlLimitListData and loadControlLimitDescriptionListData. A client-changeable limit is meant to affect the node on its own. The printed case is capping demand so the household is not overloaded. | clause not printed |
| Load control | Literal: eventAccepted; Meaning on these pages: The server accepted the command. It has not started. | clause not printed |
| Load control | Literal: eventStarted; Meaning on these pages: The server has started it. The printed cases are reducing consumption or increasing production. | clause not printed |
| Load control | Literal: eventStopped; Meaning on these pages: Stopped because the event reached the end time in its timePeriod. | clause not printed |
| Load control | Literal: eventRejected; Meaning on these pages: Rejected. The reason is not carried in this element. | clause not printed |
| Load control | Literal: eventCancelled; Meaning on these pages: Cancelled. The reason is not carried in this element. | clause not printed |
| Load control | Literal: eventError; Meaning on these pages: An error happened while the event was carried out. | clause not printed |
| Measurement description | calibrationValue is added automatically to the sensor's internal reading. The value carried in measurementListData is already the corrected one (Table 251). measurementListData itself is not defined on these pages. | Table 251 |
| Measurement description | unit applies to the normal value. A different valueType, with averageDerivativeValue named as an example, may use a unit derived from unit (Table 251). | Table 251 |
| Messaging | The class carries simple text for displays and for users. The text is not for automatisms. It is for information that is tied to events or that otherwise changes over time (§5.3.16.1). | §5.3.16.1 |
| Messaging | obsolete marks an earlier message so that it is no longer shown. messagingNumber identifies that earlier message (Table 255; Table 254). | Table 255, Table 254 |
| Messaging | Priority order printed for display types, from lower to higher: information, warning, alarm, emergency (Table 255). No numeric priority is printed. | Table 255 |
| Messaging | Examples show a full notify, a notify whose partial-filter markup is elided, a full read reply, and a read that sends cmdControl/partial plus timestampInterval or messagingNumber (§5.3.16.2.4). No period is specified. Sample intervals in those examples are not limits. | §5.3.16.2.4 |
| Network management calls | The call group adds, modifies, or removes nodes, usually on gateways, or tells a node to scan, to discover one node, or to abort the current task (§5.3.17.2). | §5.3.17.2 |
| Network management calls | Add places another node into the caller's own SPINE network (§5.3.17.3.1). The add procedure shall be aborted at the latest when timeout has elapsed (Table 256). | §5.3.17.3.1, Table 256 |
| Network management calls | Remove takes a node out of the caller's own SPINE network. The remove procedure will be aborted at the latest when timeout has elapsed (Table 257). The remove example says that when the whole device goes, and not one entity or one feature, only the device address component is filled. | Table 257 |
| Network management calls | Modify changes a node that already has a node address. The modify procedure will be aborted at the latest when timeout has elapsed (Table 258). nativeSetup does not identify the node; nodeAddress does (Table 258). The modify example says that a change to the physical device's label fills only the device part. | Table 258 |
| Network management calls | Scan asks a technology that can look for accessible devices to do so, when the technology and the implementation support it. The scan is not itself an add. It is a report. The report is networkManagementReportCandidateData. Those reports may afterwards be used to add nodes (§5.3.17.6.1). The scan will be aborted at the latest when timeout has elapsed (Table 259). | §5.3.17.6.1, Table 259 |
| Network management calls | Discover is the alternative to pushing every detail of a functionality change to every interested node. It names the address to discover again. Each recipient may still ask for the details (§5.3.17.7.1). This call has no timeout element (Table 260). | §5.3.17.7.1, Table 260 |
| Network management calls | Abort asks to stop every ongoing process that was started by add, remove, modify, scan, or discover. In this edition the call has no child elements. | clause not printed |
| Network management calls | The data-function group reports the state of those call-driven processes, sets or reports joining behaviour, and reports candidates found by scan. Device, entity, and feature descriptions carry the node graph and the per-entity and per-feature detail (§5.3.17.9). | §5.3.17.9 |
| Network management calls | Examples of a finished add, remove, modify, scan, or abort say that a networkManagementProcessStateData notification goes to the user interface. The add example also creates device, entity, and feature description notifications. The remove and modify examples create a device-description notification. Those sentences sit in the examples. | clause not printed |
| Process state, joining, candidates | networkManagementProcessStateData models the state of a process started by add, remove, modify, scan, or discover. This data-model revision supports only notification. Read, write, and reply are not supported. | clause not printed |
| Process state, joining, candidates | The function cannot name which process it belongs to. Parallel processes need care because of that. | clause not printed |
| Process state, joining, candidates | Advice, not a shall: notify a process-state instance only to the originator of that process. | clause not printed |
| Process state, joining, candidates | Outcomes are only succeeded, failed, and aborted (Table 262). No in-progress literal is printed. | Table 262 |
| Process state, joining, candidates | Joining does not apply to scan. An add started on another device may arrive locally as a join request. | clause not printed |
| Process state, joining, candidates | Joining configuration decides among three treatments of that request: skip it, which the clause equates with reject; report it (networkManagementReportCandidateData, §5.3.17.12); or add it automatically (the clause points at example §5.3.17.13.4.2). Some technologies or implementations allow temporary or permanent acceptance, or only a discovery report. | §5.3.17.12, §5.3.17.13.4.2 |
| Process state, joining, candidates | networkManagementReportCandidateData is only a notification in this data-model revision. Read, write, and reply are not supported. What is reported depends strongly on the implementation and the technology. | clause not printed |
| Process state, joining, candidates | candidateSetup is information intended for a later add. It may be copied unchanged into add nativeSetup only when setupUsableForAdd is true (Table 264). | Table 264 |
| Process state, joining, candidates | Device-description instances should be notified to every part that needs to know of any added, removed, or modified device, so each such part can see whether the change affects its own work. | clause not printed |
| Process state, joining, candidates | communicationsTechnologyInformation is treated as mostly not written, though a configuration change can still alter it (Table 265). | Table 265 |
| Process state, joining, candidates | maxResponseDelay is how long the server commonly takes before it has a reply ready (Table 269). No failure rule for exceeding it is printed. | Table 269 |
| Process state, joining, candidates | Presence of possibleOperations.read means the feature can receive read for that function and creates replies. Presence of read.partial means a curtailed reply is allowed. Presence of write means the feature can receive write and adjusts its own data. Presence of write.partial means a curtailed write is accepted (Table 269). What absence means is not printed. | Table 269 |
| Process state, joining, candidates | Sample notifies of device and entity descriptions are addressed to subscribed instances. The sample feature-description notify is addressed to bound instances. Subscription and binding rules are not defined in this class. | clause not printed |
| Operating constraints | The class states what a controller has to take into account. It does not itself control the device (§5.3.18.1). | §5.3.18.1 |
| Operating constraints | With no sequenceId, the functions usually describe the current state ("now"). With a sequenceId, they apply for the time of that power sequence. | clause not printed |
| Operating constraints | If some constraints depend on a sequence and others are global, the feature's use should be defined clearly enough to avoid ambiguity. | clause not printed |
| Operating constraints | Two recommendations, for operatingConstraintsInterruptListData only: do not mix items that have sequenceId with items that lack it; do not let one child depend on sequenceId in some items and be independent of it in others. | clause not printed |
| Operating constraints | isPausable and isStoppable: true means the task can be paused or stopped, false means it cannot (Table 270). | Table 270 |
| Operating constraints | notInterruptibleAtHighPower true means the task is not interruptible while it consumes or produces energy. false means it can still be interrupted then (Table 270). | Table 270 |
| Operating constraints | maxCyclesPerDay is present when the task may be started only up to a stated count per day (Table 270). No count is specified. | Table 270 |
| Operating constraints | Active and pause durations constrain uninterrupted on-time and the following off-time. Sum fields constrain total active time of one task, adding every active interval (Table 271; general). | Table 271 |
| Operating constraints | positiveEnergyDirection, powerUnit, and energyUnit on the power-description list apply to both the power-range list and the power-level list (Table 272). | Table 272 |
| Operating constraints | The range list is a span of power and of energy. The level list is discrete power values. Each is an alternative to the other. | clause not printed |
| Operating constraints | Resume figures cover extra energy before normal operation returns, and extra cost of that return. They are typically empirical and should not be treated as precise (; Table 275). | Table 275 |
| Power sequences, slots, and schedules | A sequence is a task, the coarse view. A slot is one step of that task, the fine view in time (§5.3.19.1.1). | §5.3.19.1.1 |
| Power sequences, slots, and schedules | Slot numbers of different sequences are independent. The same slot number under two sequence ids is two slots. | clause not printed |
| Power sequences, slots, and schedules | Printed relations: a sequence contains 0..m slots; a slot is attached to at most one sequence (printed bound 0..1); the pair { sequenceId, slotNumber } picks out a single slot. | clause not printed |
| Power sequences, slots, and schedules | Those relations allow a sequence that has no slot, and a slot that has no sequence. For most applications the text expects a tighter rule: every sequence includes one or more slots, and each slot is tied to one sequence only. | clause not printed |
| Power sequences, slots, and schedules | A Smart Device, whether it consumes or produces, announces expected consumption or generation, called a power profile, so that energy can be allocated in the premises. Sequences may be for consumption or for production. | clause not printed |
| Power sequences, slots, and schedules | The smallest announcement named is one sequence, one timeframe, one power value over that timeslot. | clause not printed |
| Power sequences, slots, and schedules | Without repetition, the announced slots run in order, and the sequence is done when the last of them finishes (§5.3.19.1.2). With repetition, that pass runs a stated number of times. repetitionsTotal is that count (Table 281). activeRepetitionNumber is the pass now running (Table 283). | §5.3.19.1.2, Table 281, Table 283 |
| Power sequences, slots, and schedules | Two or more sequences may be offered so that an energy management system selects none, or exactly one, to run (§5.3.19.1.3). Inside one alternatives group, at most one sequence is finally chosen. The relation still allows 0..m sequences in a group; day-to-day groups ought to include one or more. | §5.3.19.1.3 |
| Power sequences, slots, and schedules | Sequence state can separate the chosen alternative from the others. Which literal means chosen is not stated here; the clause points at §5.3.19.9. | §5.3.19.9 |
| Power sequences, slots, and schedules | Alternatives may also be grouped, with the groups taken in order. The group function is powerSequenceAlternativesRelationListData. | clause not printed |
| Power sequences, slots, and schedules | A single power or energy value may be enriched with facets. The clause names timestamp, durations, dependency on other values, and precision, and says there are more. Lists of those values can be a curve over time, or several variants at one time. Scheduling of periods or of whole curves, and constraints on that scheduling, can be modelled. | clause not printed |
| Power sequences, slots, and schedules | Curves are not limited to one purpose. Named purposes: announce planned consumption; present a calculated or potential availability. Further meaning of a slot may come from PowerSequence. | clause not printed |
| Power sequences, slots, and schedules | powerTimeSlotScheduleListData is actual schedule information, not the constraint function. A write on it configures a slot schedule. | clause not printed |
| Power sequences, slots, and schedules | An absolute schedule uses timePeriod and is described as the usual and the most relevant form. It fits a curve whose times are known or already decided. Sub-elements use AbsoluteOrRelativeTimeType, so each time is either UTC or an offset from the present. | clause not printed |
| Power sequences, slots, and schedules | A differential schedule models a theoretical curve that does not yet have an absolute schedule. No separate element is named for the differential form on these pages. | clause not printed |
| Power sequences, slots, and schedules | Slot intervals on one curve are forbidden to intersect. Later slots may still leave a gap. Within one sequence the schedules share no common instant, and gaps between them are allowed. | clause not printed |
| Power sequences, slots, and schedules | durationUncertainty places the actual duration in the closed span from defaultDuration minus that uncertainty through defaultDuration plus that uncertainty (Table 276). | Table 276 |
| Power sequences, slots, and schedules | optionalSlot true means the slot is optional. slotActivated true means that optional slot is used; false means it is not (Table 279; Table 276). | Table 279, Table 276 |
| Power sequences, slots, and schedules | Slot schedule constraints are for a device that allows a schedule to be configured or changed. A configuration has to meet them. | clause not printed |
| Power sequences, slots, and schedules | scope forecast or measurement typically comes from the device that runs the task. scope recommendation is rather a configuration sent into a device that is to run the task (Table 281). recommendation is a target profile the device should follow for that task when it can (Table 282). | Table 281, Table 282 |
| Power sequences, slots, and schedules | positiveEnergyDirection consume: energy values are positive while consuming and negative while producing. produce: energy values are negative while consuming and positive while producing (Table 281). is an example drawing in which consumption is the positive direction. It does not replace the element rule. | Table 281 |
| Power sequences, slots, and schedules | Power and energy units for slot values are those of the PowerSequence description (; Table 281). | Table 281 |
| Power sequences, slots, and schedules | elapsedSlotTime counts time already spent in running and stays constant during paused. remainingSlotTime counts time still required in running and also stays constant during paused (Table 283). | Table 283 |
| Power sequences, slots, and schedules | remainingPauseTime is how long the slot named by activeSlotNumber permits a pause (Table 283). | Table 283 |
| Power sequences, slots, and schedules | sequenceRemoteControllable false means the sequence runs on its own and cannot be changed by SPINE commands from external nodes (Table 283). The source wording is "commands received external nodes". The true case is not defined in this table. The clause also points at nodeRemoteControllable of powerSequenceNodeScheduleInformationData in Table 289. | Table 283, Table 289 |
| Power sequences, slots, and schedules | scheduled moves to running at the scheduled time, done by the power-sequences server. scheduledPaused moves to paused at that time (Table 284). | Table 284 |
| Power sequences, slots, and schedules | pending is preferred by that server and is not started by the server on its own. It fits a task that is about to become valid and still needs configuration or advice. It is the state most suited to powerSequenceScheduleConfigurationRequestCall, which is not defined on these pages (Table 284). | Table 284 |
| Power sequences, slots, and schedules | inactive is an optional task: not invalid, and not yet running or scheduled. It may later become running, scheduled, or scheduledPaused (Table 284). | Table 284 |
| Power sequences, slots, and schedules | invalid shall not be considered any longer (Table 284). | Table 284 |
| Power sequences, slots, and schedules | Sequence schedule constraints are the overall bounds. Slot bounds are §5.3.19.5. Both kinds may be applied together. Constraint data and schedule data should not contradict each other. | §5.3.19.5 |
| Power sequences, slots, and schedules | If energy-management software ignores those time constraints while shifting demand, the appliance could reject the requested schedule change. No rejection code or rejection procedure is printed. | clause not printed |
| Power sequences, slots, and schedules | Start and end constraints bound the start and the end. In general the sequence may last less than the window those bounds describe. | clause not printed |
| Power sequences, slots, and schedules | optionalSequence may be set true when a use case explicitly tags the sequence as an optional task (Table 286). | Table 286 |
| Power sequences, slots, and schedules | A sequence may carry a price because running it can cause cost or earnings. The price may depend on when it runs, because energy availability can change with time. powerSequencePriceListData models a price per assumed start. That assumed start may differ from the final start. | clause not printed |
| Power sequences, slots, and schedules | How the appliance learns that price is explicitly not specified in detail. Three sketches: a fixed price stored in the appliance; a local calculation from price information applied to consumption; a query to another node through powerSequencePriceCalculationRequestCall in §5.3.19.18. That call, and the price elements, are cited at that clause. | §5.3.19.18 |
| Address and trust | Address parts, root-first entity list, and the node term are in section 4 (§5.3.17.1.1). | §5.3.17.1.1 |
| Address and trust | minimumTrustLevel is the smallest trust level that still permits traffic with the described node (Tables 265, 268, 269). No comparison rule and no scale are printed. | clause not printed |
| Power sequence price, preference, and node schedule | A price record belongs to potentialStartTime. That instant can differ from the sequence’s final start, for example after a time shift if the price was not refreshed. The stored price can then differ from the price that actually applies (§5.3.19.12.2 Table 287). | §5.3.19.12.2, Table 287 |
| Power sequence price, preference, and node schedule | greenest true asks optimisation to reduce use of non-renewable energy for that sequence. cheapest true asks optimisation to reduce the user’s energy bill for that sequence. Both can be carried on the same record; no priority between them is stated (§5.3.19.13.1; Table 288). | §5.3.19.13.1, Table 288 |
| Power sequence price, preference, and node schedule | Sub-class PowerSequenceNode carries schedule facts for the whole node, not for one sequence. The text says this information can change at run time, and names nodeRemoteControllable in particular (§5.3.19.14; §5.3.19.15.1). | §5.3.19.14, §5.3.19.15.1 |
| Power sequence price, preference, and node schedule | nodeRemoteControllable true allows a remote device to schedule the node. False does not (§5.3.19.15.2 Table 289). | §5.3.19.15.2, Table 289 |
| Power sequence price, preference, and node schedule | Slot configuration uses the PowerTimeSlot sub-class, whose functions are not defined on these pages. Several slots may be sent in one function instance. supportsSingleSlotSchedulingOnly true means the appliance does not accept a change of more than one slot in one configuration command; each slot is then sent as its own write (§5.3.19.15.2 Table 289). | §5.3.19.15.2, Table 289 |
| Power sequence price, preference, and node schedule | alternativesCount is the number of alternatives groups (the text points at §5.3.19.1.3 and §5.3.19.7). If powerSequenceAlternativesRelationListData is used, this element is the size of that list (§5.3.19.15.2 Table 289). | §5.3.19.1.3, §5.3.19.7, §5.3.19.15.2, Table 289 |
| Power sequence price, preference, and node schedule | totalSequencesCountMax is the most sequences the device may offer at one moment. Counting every sequence the appliance currently knows, across alternatives groups and without regard to sequence state, does not exceed this value. The stated purpose is to let an energy-management system judge how complex the schedule is (§5.3.19.15.2 Table 289). | §5.3.19.15.2, Table 289 |
| Power sequence price, preference, and node schedule | An appliance may let an energy-management system choose one sequence out of an alternatives group and run that sequence (the text points at §5.3.19.1.3). supportsReselection false means that choice may be made only once per alternatives group. True means the selection may be changed (§5.3.19.15.2 Table 289). | §5.3.19.1.3, §5.3.19.15.2, Table 289 |
| Power sequence calls | §5.3.19.16 introduces the calls of the PowerSequence class. The class name is also printed as PowerSequences in the call text (§5.3.19.16; §5.3.19.17.1). | §5.3.19.16, §5.3.19.17.1 |
| Power sequence calls | Notices of new or changed sequences do not, by themselves, require the receiver to do anything. powerSequenceScheduleConfigurationRequestCall is an explicit request that the named sequence be configured. The server (sequence owner) sends it. A client that is able to write sequence configuration is described as then knowing that it needs to act (§5.3.19.17.1). The call carries only sequenceId. Selectors: none. The example uses classifier call (§5.3.19.17.4.1). | §5.3.19.17.1, §5.3.19.17.4.1 |
| Power sequence calls | powerSequencePriceCalculationRequestCall lets the sequence owner ask an external node to determine a price. The text says this fits when the sequence states an energy or power demand and the owner knows an external node that can price it. The call carries sequenceId and a potential start for which the price is to be determined (§5.3.19.18.1; Table 291). The same paragraph uses two names that do not match the headings on these pages: it says the owner submits powerSequencePriceCalculationResponseCall, and that the external node may return the price with powerSequencePriceData under §5.3.19.12. The defined function names here are powerSequencePriceCalculationRequestCall and powerSequencePriceListData. See Open points. | §5.3.19.18.1, Table 291, §5.3.19.12 |
| Power sequence calls | How the owner learns a price is only summarised here. The detailed general clause is §5.3.19.12.1. | §5.3.19.12.1 |
| Sensing | Sensing is for state-like sensors, with contact sensors, switches, and buttons named. Value-like sensors, with temperature and humidity named, belong to the Measurement class (§5.3.20.1). | §5.3.20.1 |
| Sensing | sensingListData can hold sensor information over time. A sensor may store only the latest value and then allow only one list entry. An interface may cache older states for a simple sensor that has only a single data function. That cache is not mandatory. The single data function itself is not defined on these pages (§5.3.20.2.1). | §5.3.20.2.1 |
| Sensing | timestamp is when that sensingData instance was created (§5.3.20.2.2 Table 292). | §5.3.20.2.2, Table 292 |
| Sensing | Sensing state literals and what the text adds beyond the name (Table 293): | Table 293 |
| Sensing | Sensor-type literals and the states the text associates with them (Table 295): switch usually on and off; button can be pressed and may also support longPressed and released; level supports one or more level-related states; levelSwitch adds on and off; windowHandle has different positions; contactSensor detects open or closed; occupancySensor uses detected or notDetected for presence in a room; motionDetector, fireDetector, smokeDetector, heatDetector, waterDetector, and gasDetector use detected or notDetected; alarmSensor and powerAlarmSensor use alarmed or notAlarmed; dayNightIndicator detects day or night. | Table 295 |
| Sensing | A notify example puts opened in state. That token is not a Table 293 literal (the listed literal is open) (§5.3.20.2.4.1). See Open points. | Table 293, §5.3.20.2.4.1 |
| Sensing | The read example selects timestampInterval and nests startTime and endTime under it, with cmdControl / partial (§5.3.20.2.4.2). The selector’s type is not defined in the element table. | §5.3.20.2.4.2 |
| Setpoint | The class is for controlling a function by a setpoint, with home automation and HVAC named as typical users. Links to Measurement and TimeTable support holding a measurand for a time span (§5.3.21.1). | §5.3.21.1 |
| Setpoint | A setpoint record can carry one target value, or a band valueMin to valueMax that is not to be left. Absolute and percentage tolerances say how far the actual value may sit from the target, in either direction (§5.3.21.2.1; Table 296). | §5.3.21.2.1, Table 296 |
| Setpoint | isSetpointChangeable says whether a client may change it. isSetpointActive says whether it is active. timePeriod is when it is supposed to be active (§5.3.21.2.2 Table 296). | §5.3.21.2.2, Table 296 |
| Setpoint | Constraints are separate: setpointRangeMin and setpointRangeMax bound what the setpoint may be set to, and setpointStepSize is the smallest step between two values (§5.3.21.3.1; Table 297). No rejection procedure is stated on these pages. | §5.3.21.3.1, Table 297 |
| Setpoint | valueAbsolute is an absolute quantity and a unit is usual. valueRelative is a percentage; the enumeration names pct as the usual unit (Table 299). | Table 299 |
| Setpoint | The description type of timeTableId is printed timeTableIdType. Later tariff and incentive tables print TimeTableIdType (Table 298; Table 318; Table 322; Table 326). | Table 298, Table 318, Table 322, Table 326 |
| Subscription | Each subscription joins one subscription client with one subscription server. Only the client may create it. Once it is in place, the server reports changes in the subscribed feature, covering that feature’s values and its parameters, and only for the subscribed function. This section leaves the precise procedure unspecified (§5.3.22.1). The class covers creation, reading, and deletion of subscriptions. Figures 176 and 177 separate data functions from call functions. | §5.3.22.1 |
| Subscription | The entry list may be stored on the device. Asked for the list, the device may return only subscriptions that involve the asker, or all of them (§5.3.22.2.1). | §5.3.22.2.1 |
| Subscription | A new subscription is subscriptionManagementRequestCall from a node-management-capable entity on the client to one on the server. clientAddress is one of the sender’s client-role features. serverAddress is a server-role feature of the other device. serverFeatureType is that server feature’s type, stated for verification (§5.3.22.3.1; Table 301). | §5.3.22.3.1, Table 301 |
| Subscription | The server accepts or refuses. The response is an acknowledgement, as defined in the protocol specification’s acknowledgement section, carrying function resultData. errorNumber 0 accepts. Any other value refuses. What those other numbers mean is out of scope here (§5.3.22.3.1). | §5.3.22.3.1 |
| Subscription | subscriptionManagementDeleteCall deletes a subscription between the sender and another device. It carries subscriptionId, clientAddress, and serverAddress (§5.3.22.4.1; Table 302). No acceptance rule is stated for the delete call on these pages. | §5.3.22.4.1, Table 302 |
| Subscription | Entry, request, and delete examples show FeatureAddressType with child elements named device, entity, and feature. The call example sets serverFeatureType to ActuatorSwitch. Those instance strings are not a definition of FeatureTypeType or of the address type (§5.3.22.3.4.1; type definition §3.10.3.6 and §3.10.1.29). | §5.3.22.3.4.1, §3.10.3.6, §3.10.1.29 |
| State information | The list helps a reader see which operation or failure to expect from an entity. A failure may mean operation is not normal (§5.3.23.1). | §5.3.23.1 |
| State information | Each entry is one functionality or one failure. The entry remains while that state is supported, not only while it is active. isActive true means active; otherwise inactive (§5.3.23.1; §5.3.23.2.1; Table 303). | §5.3.23.1, §5.3.23.2.1, Table 303 |
| State information | category functionality is the normal-operation group. category failure is the group that is most likely not normal operation (Table 306). | Table 306 |
| State information | Functionality literals, in short (Table 304): externalOverrideFromGrid means a grid-side command has overwritten the appliance’s function; autonomousGridSupport means the appliance supports grid stability; islandingMode means it runs without the electricity grid; balancing and trickleCharging are battery modes; calibration means it is calibrating; commissioningMissing means it is waiting to be commissioned; sleeping, starting, shuttingDown are those phases; manualShutdown is a shutdown started by hand; mppt is the inverter’s maximum-power-point-tracker mode, expanded in the text as Maximum Power Point Tracker; throttled means consumption or production has been reduced. | Table 304 |
| State information | Failure literals name detected conditions (Table 305): inverter defect; battery overcurrent protection; PV-string overcurrent protection; grid fault; ground fault; AC disconnected; DC disconnected; cabinet open; temperature, frequency, AC voltage, or DC voltage above or below a limit; a hardware test failed; an internal error with no further classification. | Table 305 |
| State information | No transition table among these states is printed. timeOfLastChange is only the time of the last change (Table 303). | Table 303 |
| Supply condition | The class indicates a supply that is temporarily impaired. Causes named include announced work on the supply line, overload of the supply network, and a local store running down, with a battery given as a case. Electricity and water are named as supplies. The text says the concept is aimed at telling users, and is less aimed at automatisms (§5.3.24.1). | §5.3.24.1 |
| Supply condition | Events may be written by a distribution-system operator, acting as client, into data owned by the household (§5.3.24.2.1). The printed example of this function is a notify, not a write (§5.3.24.2.4.1). | §5.3.24.2.1, §5.3.24.2.4.1 |
| Supply condition | Event literals (Table 308): thesholdExceeded means the related threshold was passed, and that may be favourable or not; fallenBelowThreshold means the value went below the related threshold, likewise favourable or not. Both point at thresholdType in §5.3.27.4.2. supplyInterrupt means the commodity’s supply was interrupted. releaseOfLimitations means a return to normal, with no current limitation and no threshold violation. otherProblem means a supply problem with no further detail. The literal thesholdExceeded is printed without the second r. | Table 308, §5.3.27.4.2 |
| Supply condition | Originator literals (Table 309): externDSO is the distribution system operator; externSupplier is the energy supplier; internalLimit is a limit inside the premises; internalService is service work inside the premises; internalUser is a user action. | Table 309 |
| Supply condition | Grid literals (Table 310): consumptionRed and consumptionYellow are the red and yellow conditions for taking electricity from the grid; good is the good condition; productionYellow and productionRed are the yellow and red conditions for feeding electricity into the grid. No numeric threshold for red, yellow, or good is printed here. | Table 310 |
| Supply condition | thresholdPercentage relates the current situation to the configured threshold, when that comparison exists. relevantPeriod is available in particular so a maintenance notice can say when the work is planned (Table 307). | Table 307 |
| Supply condition | One condition relates to zero or more thresholds: the text prints 1 conditionId -> 0..m thresholdId (§5.3.24.4.1). The read example for that relation puts an empty messagingListData element in the request while the function element is supplyConditionThresholdRelationListData (§5.3.24.4.4.1). See Open points. | §5.3.24.4.1, §5.3.24.4.4.1 |
| Tariff structure, bounds, and tier changes | A tariff has one commodity and tiers, and the tiers have boundaries. Each tier has incentives. Identifiers link those parts (§5.3.25.1). | §5.3.25.1 |
| Tariff structure, bounds, and tier changes | Parts named on these pages (§5.3.25.1): overall limits tariffOverallConstraintsData; dynamic tariffListData; static tariffDescriptionListData; boundary relation; tier relation; dynamic tierBoundaryListData and static tierBoundaryDescriptionListData; dynamic tierListData, static tierDescriptionListData, and tierIncentiveRelationListData; dynamic incentiveListData and a static incentive description; commodity only as commodityListData. Two of those names are truncated in the prose: tariffBoundaryRelationListDat and incentiveDescriptionListDat. The function headings spell both with a final a. | §5.3.25.1 |
| Tariff structure, bounds, and tier changes | Sub-class Tariff holds the tariff’s own information (§5.3.25.2). tariffOverallConstraintsData holds limits that apply to every tariff on that feature (§5.3.25.3.1). Each max… element is a maximum the server supports. This text does not fix a universal number. The eight limits are: tariffs, tier boundaries, tiers, and incentives on the feature; boundaries per tariff; tiers per tariff; distinct boundaryId values per tier; incentives per tier (Table 313). | §5.3.25.2, §5.3.25.3.1, Table 313 |
| Tariff structure, bounds, and tier changes | tariffListData says which tiers are active now (activeTierId is a list) (§5.3.25.4.1; Table 314). | §5.3.25.4.1, Table 314 |
| Tariff structure, bounds, and tier changes | tariffWriteable says whether that tariff may be written. updateRequired true means some bound client is required to update that tariff (Table 317). No write-reject rule is stated. | Table 317 |
| Tariff structure, bounds, and tier changes | A tier boundary says which span of values makes a tier valid. That validity may also be limited by a period or by a timetable (§5.3.25.9.1). | §5.3.25.9.1 |
| Tariff structure, bounds, and tier changes | switchToTierIdWhenLower is the tier that becomes valid if the quantity named by boundaryType falls below lowerBoundaryValue of tierBoundaryListData. switchToTierIdWhenHigher is the tier that becomes valid if that quantity rises above upperBoundaryValue (Table 319). Boundary kinds are power, energy, or a count (powerBoundary, energyBoundary, countBoundary, Table 320). | Table 319, Table 320 |
| Tariff structure, bounds, and tier changes | Tiers are the levels inside a tariff. The introduction gives time-based day and night prices, and a boundary-based rise in payment as consumption rises, as3.25.13). fixedCost is paid independent of energy consumed. dynamicCost depends linearly on energy consumed (Table 325). | §5.3.25.13, Table 325 |
| Tariff structure, bounds, and tier changes | Incentives are the actual costs. Monetary cost is one case; co2Emission is named as another (§5.3.25.17). | §5.3.25.17 |
| Tariff structure, bounds, and tier changes | absoluteCost is a money amount, stated in a currency together with a unit of measure. relativeCost cannot be read as money. renewableEnergyPercentage is the share of renewable energy in the energy obtained, described as an ecological incentive so that renewable use can be preferred over price. co2Emission is the CO2 related to the energy obtained, described the same way for emissions rather than price (Table 329). | Table 329 |
| Tariff structure, bounds, and tier changes | incentivePriority is an xs:unsignedInt restriction. No ordering rule (lower number wins, or the reverse) is stated (Table 328). | Table 328 |
| Tariff structure, bounds, and tier changes | value, averageValue, minValue, and maxValue say whether the incentive number is the ordinary cost, only an average, the minimum, or the maximum (Table 327). | Table 327 |
| Tasks | TaskManagement lists tasks that currently matter on an entity, so a reader can see tasks of related classes. It is not for changing those tasks. Detail comes from the class that owns the function (§5.3.26.1). | §5.3.26.1 |
| Tasks | In this edition a task is a job, as in DirectControl and in PowerSequences / SmartEnergyManagementPs (§5.3.26.1). A remark says later editions may add tasks that are not jobs. | §5.3.26.1 |
| Tasks | elapsedTime is how long the job has already been active; pause time is normally not counted. remainingTime is how long the job is expected to remain active before it ends (Table 330). Neither value is defined as a timeout or a failsafe. | Table 330 |
| Tasks | jobState reuses four enumerations from other classes (Tables 205, 227, 238, and 284), or an extended enumeration. Those literal lists are not on these pages (Table 330). | Table 330 |
| Tasks | A relation record says which class the job comes from. If that class can hold more than one job, the matching identifier is included (§5.3.26.3.1). The flags are complex types: directControlRelated (no child listed; the example shows an empty element), hvacRelated with overrunId, loadControlReleated with eventId, powerSequencesRelated with sequenceId, and smartEnergyManagementPsRelated with sequenceId (Table 331). | §5.3.26.3.1, Table 331 |
| Tasks | The static job description begins with jobId and jobSource and does not finish. No job-source literal, label, description, selector, or operation for taskManagementJobDescriptionListData is printed. | clause not printed |
| Task management | taskManagementOverviewData says whether remote control is permitted at this moment, and whether any job is currently active. §5.3.26.5.1, Table 334 | §5.3.26.5.1, Table 334 |
| Task management | remoteControllable: remote control of the device or the entity is or is not permitted. Table 334 | Table 334 |
| Task management | jobsActive: jobs are or are not active on the device or the entity. Table 334 | Table 334 |
| Task management | TaskManagementJobSourceEnumType (Table 333): | Table 333 |
| Threshold | thresholdListData reads or writes the configured value of a threshold identified by thresholdId. §5.3.27.2.1 | §5.3.27.2.1 |
| Threshold | thresholdValue is the level that is not to be gone under, or not to be gone over. Which of those applies depends on thresholdType. Table 335, §5.3.27.4.2 | Table 335, §5.3.27.4.2 |
| Threshold | thresholdConstraintsListData may limit the configurable value by a minimum, a maximum, and a step. The text allows only values on that step between the minimum and the maximum. §5.3.27.3.1, Table 336 | §5.3.27.3.1, Table 336 |
| Threshold | ThresholdTypeEnumType (Table 338): | Table 338 |
| Threshold | The introduction says a threshold can drive configured behaviour, can keep a measurand in a working range, and can raise an alarm when it is reached. §5.3.27.1. No alarm state machine is printed here. | §5.3.27.1 |
| Time information | timeInformationData carries the SPINE time. The text calls it a command. §5.3.28.2.1 | §5.3.28.2.1 |
| Time information | This data-model revision prints no sync method that names a precision. The stated reason is delay, which differs by technology and by platform. An application can measure those delays and sync with class TimeInformation. §5.3.28.1 | §5.3.28.1 |
| Time information | The owner of a value applies that node's own SPINE time to the value. The text says this matters when two nodes disagree substantially about SPINE time. | clause not printed |
| Time information | A usual order in the text: a new device sends timeDistributorEnquiryCall toward every device; distributors notify timeDistributorData; the new device picks the highest distributorPriority and reads that distributor's timeInformationData; the reply carries the current time. The same paragraph says the enquiry is sent with isTimeDistributor true. Section 5.3.28.5.2 gives that call no child elements, and isTimeDistributor is a child of timeDistributorData. Both statements are printed. See §8. | §8 |
| Time information | The enquiry can be sent to each device whose isTimeDistributor is true. The sentence names the function timeDistributor and points at §5.3.28.3, whose function name is timeDistributorData. | §5.3.28.3 |
| Time information | call is stated as the only classifier allowed for timeDistributorEnquiryCall. | clause not printed |
| Time information | A notify of timeDistributorData is described as a typical follow-up to that enquiry. | clause not printed |
| Time information | utc: current time in UTC. xs:dateTime. Table 339 | Table 339 |
| Time information | utcOffset: configured offset from UTC. xs:duration. Table 339 | Table 339 |
| Time information | dayOfWeek: local weekday, described as Monday through Sunday. If utcOffset is absent, local time is taken to be UTC. Table 339 | Table 339 |
| Time information | calendarWeek: local week number, limited to the integers 1 through 53. The same absent-offset assumption applies. Table 339 | Table 339 |
| Time information | isTimeDistributor: whether this device is able to distribute SPINE time. Table 340 | Table 340 |
| Time information | distributorPriority: a configured priority. xs:unsignedInt. No numeric range is printed. The discovery sketch says to choose the highest priority. Table 340 | Table 340 |
| Time information | isSynchronised: whether the device's SPINE time is aligned with the network, in the sense that it could take time from a distributor and the time is still precise enough. No numeric bound for that precision is printed. Table 341 | Table 341 |
| Time information | lastSyncAt: timestamp of the latest sync with a distributor. On a distributor, timestamp of the latest official date and time it obtained. An NTP server is the example. Table 341 | Table 341 |
| Time information | clockDrift: internal clock drift, in seconds per day. xs:integer. No allowed range is printed. Table 341 | Table 341 |
| Time series | timeSeriesListData carries the value of a series over time. §5.3.29.2.1 | §5.3.29.2.1 |
| Time series | On a slot, value is the expected value, minValue a lower limit, maxValue an upper limit, duration the slot length. The slot timePeriod can also express a gap between slots. recurrenceInformation is used when the slot recurs. The series-level timePeriod is the period of the whole series. Table 342, Table 343 | Table 342, Table 343 |
| Time series | TimeSeriesTypeEnumType (Table 345): | Table 345 |
| Time series | timeSeriesWriteable: whether that series may be written. Table 344 | Table 344 |
| Time series | updateRequired: asks the bound client to write timeSeriesData. Table 344. The value function printed in this class is timeSeriesListData. See §8. | Table 344, §8 |
| Time series | measurementId: link from the series to data of another feature. Measurement and ElectricalConnection are the examples named. Table 344 | Table 344 |
| Time series | timeSeriesConstraintsListData states limits such as how many slots are allowed. The text says this matters especially when the series values are writable and the server has limits: the client can line its own limits up with the server limits and form a write that meets them. §5.3.29.4.1 | §5.3.29.4.1 |
| Time series | Recurring slots count as one toward slotCountMin and toward slotCountMax. Table 346 | Table 346 |
| Time series | slotDurationMin, slotDurationMax, and slotDurationStepSize bound the slot length and its step. Table 346 | Table 346 |
| Time series | earliestTimeSeriesStartTime: earliest start the series is allowed to use. latestTimeSeriesEndTime: latest end it is allowed to use. Table 346 | Table 346 |
| Time series | Slot values are not allowed below slotValueMin or above slotValueMax. slotValueStepSize is the smallest step between two different slot values. Table 346 | Table 346 |
| Time table | This class is what time-dependent behaviour, setpoint configuration among it, builds on. Each table holds slots. A slot has a start and an end. The time is either an absolute date-time or a recurring pattern. The pattern uses weekday elements and a clock time, and it uses the interval-step elements when the table needs them. How many slots exist, and those endpoints, may be client-configurable or fixed by the device. Another class refers only to timeTableId. §5.3.30.1 | §5.3.30.1 |
| Time table | A write example uses classifier write with partial, for the case where writing new slot times is allowed. §5.3.30.2.4.2 | §5.3.30.2.4.2 |
| Time table | timeSlotCountChangeable: whether a client may change how many slots that table has. Table 349 | Table 349 |
| Time table | timeSlotTimesChangeable: whether a client may change the times of the slots. Table 349 | Table 349 |
| Time table | TimeSlotTimeModeEnumType (Table 350): absolute allows only absolute times; recurring allows only recurring times; both allows either. | Table 350 |
| Time table | Constraints may differ per table, including minimum and maximum slot count. §5.3.30.3.1 | §5.3.30.3.1 |
| Time table | Recurring slots count as one toward slotCountMin and slotCountMax. Table 348 | Table 348 |
| Time table | slotDurationMin, slotDurationMax, slotDurationStepSize: minimum, maximum, and step of slot length. slotShiftStepSize: step by which a slot may be shifted. Table 348 | Table 348 |
| Time table | firstSlotBeginsAt: when, on a day, the pattern given by slotDurationStepSize begins. For a fixed 15-minute pattern the text calls 00:00:00 the default start and gives 00:10:00 as another possible start. Table 348. The schema print is not in this class section; no default attribute is printed on the element in the prose table. | Table 348 |
| Time table | The constraints example is a notify to every device bound on that feature. §5.3.30.3.4.1 | §5.3.30.3.4.1 |
| Time table | The general line for the description function says timeTableDescriptionData, while the heading and the element are timeTableDescriptionListData. See §8. | §8 |
| Use case information and version | UseCaseInformation models which use cases a node supports. §5.3.31.1 | §5.3.31.1 |
| Use case information and version | useCaseAvailable: whether that use case is available at this moment. Table 351 | Table 351 |
| Use case information and version | useCaseDocumentSubRevision extends useCaseVersion with the release state of the underlying use-case specification, so an implementation of a pre-release can be recognised. Table 351 | Table 351 |
| Use case information and version | A version has three parts, in order major, then minor, then revision. A dot stands between the parts. The shape shown is 1.0.0. §5.3.32.1 | §5.3.32.1 |
| Use case information and version | major: increased for fundamental changes. Changes that break mandatory compatibility are in that group. | clause not printed |
| Use case information and version | minor: increased for optional additions relative to the previous specification version. | clause not printed |
| Use case information and version | revision: increased for smaller changes that leave major and minor unchanged. | clause not printed |
| Use case information and version | specificationVersionListData exists so a partner can know which SPINE data-model versions the other side supports. The text says the compatibility rules of [ProtocolSpecification] can be applied only with that knowledge. Those rules are not printed here. §5.3.32.2.1 | §5.3.32.2.1 |
| Use case information and version | The version is also used in the datagram header; that definition is in [ProtocolSpecification]. This section defines Version as a SPINE class. §5.3.32.1 | §5.3.32.1 |
| Use case information and version | The printed notify example is a complete notification of every supported version. | clause not printed |
| Annex A complex classes | IncentiveTable, NodeManagement, and SmartEnergyManagementPs are printed as schemas that restrict fields of other classes down to a kept set. A kept field, its type, and its printed cardinality are in §5. Fields of the base type that are not in the restriction are not listed on these pages. | §5 |
| Annex A complex classes | Two description particles in SmartEnergyManagementPs restrict DescriptionType with minLength 1 and maxLength 60: the power-sequence description and the slot description. The matching element-tag particles use ElementTagType and do not repeat those facets. | clause not printed |
| Annex A complex classes | In this schema, sequence and slot schedule times that are printed as xs:duration are xs:duration (startTime, endTime, earliestStartTime, latestEndTime, defaultDuration, durationUncertainty, minDuration, maxDuration, elapsedSlotTime, remainingSlotTime, remainingPauseTime, and the active and pause duration fields). | clause not printed |
| Annex A complex classes | nodeManagementBindingRequestCall keeps clientAddress, serverAddress, and serverFeatureType. nodeManagementBindingDeleteCall keeps bindingId, clientAddress, and serverAddress. The subscription request and delete calls keep the same shapes with subscriptionId on delete. No accept, reject, timeout, or failsafe rule for those calls is printed here. | clause not printed |
| Annex A complex classes | The binding selector restriction prints no child elements. The subscription selector restriction prints subscriptionId, clientAddress, and serverAddress. | clause not printed |
| Annex A complex classes | nodeManagementUseCaseDataSelectors keeps useCaseName, useCaseVersion, and scenarioSupport under useCaseSupport. It does not print useCaseAvailable or useCaseDocumentSubRevision as selector particles. | clause not printed |
| Annex A complex classes | The price-calculation call type is opened at and the print ends at inside an open restriction of PowerSequencePriceCalculationRequestCallType. No child of that restriction, and no global element for that call, is on these pages. | clause not printed |
| Command, limit and timing semantics | heartbeatCounter is xs:unsignedLong with no facet. heartbeatTimeout is xs:duration with no facet. Both carry minOccurs 0 on deviceDiagnosisHeartbeatData. §A.2.9, §A.2.9 | clause not printed |
| Command, limit and timing semantics | NetworkManagementProcessTimeoutType restricts xs:duration with no facet. §A.2.17. It types timeout (minOccurs 0) on networkManagementAddNodeCall (§A.2.17), networkManagementRemoveNodeCall (§A.2.17), networkManagementModifyNodeCall (§A.2.17), and networkManagementScanNetworkCall (§A.2.17). | clause not printed |
| Command, limit and timing semantics | Further fields typed xs:duration with no facet include defaultDuration (§A.2.19), durationUncertainty (§A.2.19), minDuration (§A.2.19), maxDuration (§A.2.19), activeDurationMin (§A.2.18), and activeDurationMax (§A.2.18). | clause not printed |
| Command, limit and timing semantics | LoadControlLimitTypeEnumType literals, in order: minValueLimit, maxValueLimit, signDependentAbsValueLimit. §A.2.14. LoadControlLimitIdType restricts xs:unsignedInt with no facet. §A.2.14. isLimitChangeable is xs:boolean. §A.2.14. isLimitActive is xs:boolean. §A.2.14. | clause not printed |
| Command, limit and timing semantics | DeviceDiagnosisOperatingStateEnumType literals, in order: normalOperation, standby, failure, serviceNeeded, overrideDetected, inAlarm, notReachable, finished, temporarilyNotReady, off. §A.2.9. StateInformationFunctionalityEnumType and StateInformationFailureEnumType literals are in section 5. §A.2.22, §A.2.22. | clause not printed |
| Command vocabulary | CmdClassifierType restricts xs:string with no EnumExtendType union. Literals: read, reply, notify, write, call, result. §A.3.2. No prose on these pages defines those six words. Global element cmdClassifier has that type. | clause not printed |
| Command vocabulary | CmdControlType is a sequence of optional delete and optional partial, both ElementTagType. | clause not printed |
| Command vocabulary | PossibleOperationsClassifierType has one optional element, partial, of type ElementTagType. PossibleOperationsReadType and PossibleOperationsWriteType extend that type and add no particle. PossibleOperationsType is optional read plus optional write. FunctionPropertyType is optional function (FunctionType) plus optional possibleOperations. notify, subscribe, and bind are not fields of this operations type. subscribe and bind appear only as class and function names. | clause not printed |
| Command vocabulary | FilterType: optional filterId (FilterIdType, itself an xs:unsignedInt restriction); optional ref cmdControl; optional unbounded group DataSelectorsChoiceGroup; optional group DataElementsChoiceGroup. | clause not printed |
| Command vocabulary | CmdOptionGroup: sequence of optional ref function and optional unbounded ref filter. | clause not printed |
| Command vocabulary | DataExtendGroup: sequence of optional ref manufacturerSpecificExtension (global type xs:hexBinary) and optional ref lastUpdateAt (global type AbsoluteOrRelativeTimeType). | clause not printed |
| Command vocabulary | PayloadContributionGroup: sequence of optional group CmdOptionGroup, optional group DataChoiceGroup, optional group DataExtendGroup. | clause not printed |
| Command vocabulary | CmdType contains group PayloadContributionGroup with minOccurs not printed. | clause not printed |
| Command vocabulary | HeaderType (§A.3.4), every child minOccurs 0: specificationVersion (SpecificationVersionType), addressSource, addressDestination, addressOriginator (each FeatureAddressType), msgCounter and msgCounterReference (MsgCounterType, an xs:unsignedLong restriction, §A.3.2), cmdClassifier, ackRequest (xs:boolean), timestamp (AbsoluteOrRelativeTimeType). No rule says when ackRequest is true or how msgCounter is allocated. | clause not printed |
| Command vocabulary | PayloadType.cmd is optional and unbounded, type CmdType. DatagramType refs header and payload with minOccurs not printed. Global element datagram has type DatagramType. | clause not printed |
| Command vocabulary | ResultDataType (§A.3.5): optional errorNumber (ErrorNumberType, restriction of xs:unsignedInt with no further facet) and optional description (DescriptionType). No error-code list and no success value are printed. Global element resultData is also a FunctionEnumType literal and a DataChoiceGroup member, and it has no elements-choice partner. | clause not printed |
| Patterns and numeric facets | SpecificationVersionType pattern [1-9][0-9]*\.[0-9]+\.[0-9]+. §A.3.3. | clause not printed |
| Patterns and numeric facets | SpecificationVersionType maxLength 128. §A.3.3. | clause not printed |
| Patterns and numeric facets | EnumExtendType pattern _(i:[1-9][0-9]*/n:[a-zA-Z0-9-]+)_[^\p{Cc}\p{Cf}\p{Z}]+. §A.3.3. | clause not printed |
| Patterns and numeric facets | EnumExtendType maxLength 256. §A.3.3. | clause not printed |
| Patterns and numeric facets | DayOfMonthType minInclusive 1. §A.3.3. | clause not printed |
| Patterns and numeric facets | DayOfMonthType maxInclusive 31. §A.3.3. | clause not printed |
| Patterns and numeric facets | CalendarWeekType minInclusive 1. §A.3.3. | clause not printed |
| Patterns and numeric facets | CalendarWeekType maxInclusive 53. §A.3.3. | clause not printed |
| Patterns and numeric facets | AddressDeviceType pattern d:_(i:[1-9][0-9]*/n:[a-zA-Z0-9-]+)_[^\p{Cc}\p{Cf}\p{Z}]+. §A.3.3. | clause not printed |
| Patterns and numeric facets | AddressDeviceType maxLength 256. §A.3.3. | clause not printed |
| Patterns and numeric facets | FeatureGroupType pattern (#[1-9][0-9]*)*. §A.3.3. | clause not printed |
| Patterns and numeric facets | FeatureGroupType maxLength 128. §A.3.3. | clause not printed |
| Duration, clock, and bound fields | TaskManagementJobDataType.elapsedTime type xs:duration; minOccurs=0; maxOccurs not printed. §A.2.26. | clause not printed |
| Duration, clock, and bound fields | TaskManagementJobDataType.remainingTime type xs:duration; minOccurs=0; maxOccurs not printed. §A.2.26. | clause not printed |
| Duration, clock, and bound fields | TimeInformationDataType.utcOffset type xs:duration; minOccurs=0; maxOccurs not printed. §A.2.28. | clause not printed |
| Duration, clock, and bound fields | TimeSeriesSlotType.duration type xs:duration; minOccurs=0; maxOccurs not printed. §A.2.29. | clause not printed |
| Duration, clock, and bound fields | TimeSeriesConstraintsDataType.slotDurationMin type xs:duration; minOccurs=0; maxOccurs not printed. §A.2.29. | clause not printed |
| Duration, clock, and bound fields | TimeSeriesConstraintsDataType.slotDurationMax type xs:duration; minOccurs=0; maxOccurs not printed. §A.2.29. | clause not printed |
| Duration, clock, and bound fields | TimeSeriesConstraintsDataType.slotDurationStepSize type xs:duration; minOccurs=0; maxOccurs not printed. §A.2.29. | clause not printed |
| Duration, clock, and bound fields | TimeTableConstraintsDataType.slotDurationMin type xs:duration; minOccurs=0; maxOccurs not printed. §A.2.30. | clause not printed |
| Duration, clock, and bound fields | TimeTableConstraintsDataType.slotDurationMax type xs:duration; minOccurs=0; maxOccurs not printed. §A.2.30. | clause not printed |
| Duration, clock, and bound fields | TimeTableConstraintsDataType.slotDurationStepSize type xs:duration; minOccurs=0; maxOccurs not printed. §A.2.30. | clause not printed |
| Duration, clock, and bound fields | TimeTableConstraintsDataType.slotShiftStepSize type xs:duration; minOccurs=0; maxOccurs not printed. §A.2.30. | clause not printed |
| Duration, clock, and bound fields | AbsoluteOrRecurringTimeType.relative type xs:duration; minOccurs=0; maxOccurs not printed. §A.3.3. | clause not printed |
| Duration, clock, and bound fields | TimeInformationDataType.utc type xs:dateTime; minOccurs=0; maxOccurs not printed. §A.2.28. | clause not printed |
| Duration, clock, and bound fields | TimePrecisionDataType.lastSyncAt type xs:dateTime; minOccurs=0; maxOccurs not printed. §A.2.28. | clause not printed |
| Duration, clock, and bound fields | TimeTableConstraintsDataType.firstSlotBeginsAt type xs:time; minOccurs=0; maxOccurs not printed. §A.2.30. | clause not printed |
| Duration, clock, and bound fields | AbsoluteOrRecurringTimeType.dateTime type xs:dateTime; minOccurs=0; maxOccurs not printed. §A.3.3. | clause not printed |
| Duration, clock, and bound fields | AbsoluteOrRecurringTimeType.time type xs:time; minOccurs=0; maxOccurs not printed. §A.3.3. | clause not printed |
| Duration, clock, and bound fields | RecurrenceInformationType.firstExecution type xs:dateTime; minOccurs=0; maxOccurs not printed. §A.3.3. | clause not printed |
| Duration, clock, and bound fields | RecurrenceInformationType.lastExecution type xs:dateTime; minOccurs=0; maxOccurs not printed. §A.3.3. | clause not printed |
| Duration, clock, and bound fields | ThresholdConstraintsDataType.thresholdRangeMin type ScaledNumberType; minOccurs=0; maxOccurs not printed. §A.2.27. | clause not printed |
| Duration, clock, and bound fields | ThresholdConstraintsDataType.thresholdRangeMax type ScaledNumberType; minOccurs=0; maxOccurs not printed. §A.2.27. | clause not printed |
| Duration, clock, and bound fields | ThresholdConstraintsDataType.thresholdStepSize type ScaledNumberType; minOccurs=0; maxOccurs not printed. §A.2.27. | clause not printed |
| Duration, clock, and bound fields | ThresholdConstraintsDataElementsType.thresholdRangeMin type ScaledNumberElementsType; minOccurs=0; maxOccurs not printed. §A.2.27. | clause not printed |
| Duration, clock, and bound fields | ThresholdConstraintsDataElementsType.thresholdRangeMax type ScaledNumberElementsType; minOccurs=0; maxOccurs not printed. §A.2.27. | clause not printed |
| Duration, clock, and bound fields | ThresholdConstraintsDataElementsType.thresholdStepSize type ScaledNumberElementsType; minOccurs=0; maxOccurs not printed. §A.2.27. | clause not printed |
| Duration, clock, and bound fields | TimeSeriesConstraintsDataType.slotCountMin type TimeSeriesSlotCountType; minOccurs=0; maxOccurs not printed. §A.2.29. | clause not printed |
| Duration, clock, and bound fields | TimeSeriesConstraintsDataType.slotCountMax type TimeSeriesSlotCountType; minOccurs=0; maxOccurs not printed. §A.2.29. | clause not printed |
| Duration, clock, and bound fields | TimeSeriesConstraintsDataType.slotDurationMin type xs:duration; minOccurs=0; maxOccurs not printed. §A.2.29. | clause not printed |
| Duration, clock, and bound fields | TimeSeriesConstraintsDataType.slotDurationMax type xs:duration; minOccurs=0; maxOccurs not printed. §A.2.29. | clause not printed |
| Duration, clock, and bound fields | TimeSeriesConstraintsDataType.slotDurationStepSize type xs:duration; minOccurs=0; maxOccurs not printed. §A.2.29. | clause not printed |
| Duration, clock, and bound fields | TimeSeriesConstraintsDataType.slotValueMin type ScaledNumberType; minOccurs=0; maxOccurs not printed. §A.2.29. | clause not printed |
| Duration, clock, and bound fields | TimeSeriesConstraintsDataType.slotValueMax type ScaledNumberType; minOccurs=0; maxOccurs not printed. §A.2.29. | clause not printed |
| Duration, clock, and bound fields | TimeSeriesConstraintsDataType.slotValueStepSize type ScaledNumberType; minOccurs=0; maxOccurs not printed. §A.2.29. | clause not printed |
| Duration, clock, and bound fields | TimeSeriesConstraintsDataElementsType.slotCountMin type ElementTagType; minOccurs=0; maxOccurs not printed. §A.2.29. | clause not printed |
| Duration, clock, and bound fields | TimeSeriesConstraintsDataElementsType.slotCountMax type ElementTagType; minOccurs=0; maxOccurs not printed. §A.2.29. | clause not printed |
| Duration, clock, and bound fields | TimeSeriesConstraintsDataElementsType.slotDurationMin type ElementTagType; minOccurs=0; maxOccurs not printed. §A.2.29. | clause not printed |
| Duration, clock, and bound fields | TimeSeriesConstraintsDataElementsType.slotDurationMax type ElementTagType; minOccurs=0; maxOccurs not printed. §A.2.29. | clause not printed |
| Duration, clock, and bound fields | TimeSeriesConstraintsDataElementsType.slotDurationStepSize type ElementTagType; minOccurs=0; maxOccurs not printed. §A.2.29. | clause not printed |
| Duration, clock, and bound fields | TimeSeriesConstraintsDataElementsType.slotValueMin type ScaledNumberElementsType; minOccurs=0; maxOccurs not printed. §A.2.29. | clause not printed |
| Duration, clock, and bound fields | TimeSeriesConstraintsDataElementsType.slotValueMax type ScaledNumberElementsType; minOccurs=0; maxOccurs not printed. §A.2.29. | clause not printed |
| Duration, clock, and bound fields | TimeSeriesConstraintsDataElementsType.slotValueStepSize type ScaledNumberElementsType; minOccurs=0; maxOccurs not printed. §A.2.29. | clause not printed |
| Duration, clock, and bound fields | TimeTableConstraintsDataType.slotCountMin type TimeSlotCountType; minOccurs=0; maxOccurs not printed. §A.2.30. | clause not printed |
| Duration, clock, and bound fields | TimeTableConstraintsDataType.slotCountMax type TimeSlotCountType; minOccurs=0; maxOccurs not printed. §A.2.30. | clause not printed |
| Duration, clock, and bound fields | TimeTableConstraintsDataType.slotDurationMin type xs:duration; minOccurs=0; maxOccurs not printed. §A.2.30. | clause not printed |
| Duration, clock, and bound fields | TimeTableConstraintsDataType.slotDurationMax type xs:duration; minOccurs=0; maxOccurs not printed. §A.2.30. | clause not printed |
| Duration, clock, and bound fields | TimeTableConstraintsDataType.slotDurationStepSize type xs:duration; minOccurs=0; maxOccurs not printed. §A.2.30. | clause not printed |
| Duration, clock, and bound fields | TimeTableConstraintsDataType.slotShiftStepSize type xs:duration; minOccurs=0; maxOccurs not printed. §A.2.30. | clause not printed |
| Duration, clock, and bound fields | TimeTableConstraintsDataElementsType.slotCountMin type ElementTagType; minOccurs=0; maxOccurs not printed. §A.2.30. | clause not printed |
| Duration, clock, and bound fields | TimeTableConstraintsDataElementsType.slotCountMax type ElementTagType; minOccurs=0; maxOccurs not printed. §A.2.30. | clause not printed |
| Duration, clock, and bound fields | TimeTableConstraintsDataElementsType.slotDurationMin type ElementTagType; minOccurs=0; maxOccurs not printed. §A.2.30. | clause not printed |
| Duration, clock, and bound fields | TimeTableConstraintsDataElementsType.slotDurationMax type ElementTagType; minOccurs=0; maxOccurs not printed. §A.2.30. | clause not printed |
| Duration, clock, and bound fields | TimeTableConstraintsDataElementsType.slotDurationStepSize type ElementTagType; minOccurs=0; maxOccurs not printed. §A.2.30. | clause not printed |
| Duration, clock, and bound fields | TimeTableConstraintsDataElementsType.slotShiftStepSize type ElementTagType; minOccurs=0; maxOccurs not printed. §A.2.30. | clause not printed |
| Duration, clock, and bound fields | TariffDescriptionDataType.tariffWriteable §A.2.25. | clause not printed |
| Duration, clock, and bound fields | TariffDescriptionDataType.updateRequired §A.2.25. | clause not printed |
| Duration, clock, and bound fields | TariffDescriptionDataType.slotIdSupport §A.2.25. | clause not printed |
| Duration, clock, and bound fields | TaskManagementOverviewDataType.remoteControllable §A.2.26. | clause not printed |
| Duration, clock, and bound fields | TaskManagementOverviewDataType.jobsActive §A.2.26. | clause not printed |
| Duration, clock, and bound fields | TimeDistributorDataType.isTimeDistributor §A.2.28. | clause not printed |
| Duration, clock, and bound fields | TimePrecisionDataType.isSynchronised §A.2.28. | clause not printed |
| Duration, clock, and bound fields | TimeSeriesDescriptionDataType.timeSeriesWriteable §A.2.29. | clause not printed |
| Duration, clock, and bound fields | TimeSeriesDescriptionDataType.updateRequired §A.2.29. | clause not printed |
| Duration, clock, and bound fields | TimeTableDescriptionDataType.timeSlotCountChangeable §A.2.30. | clause not printed |
| Duration, clock, and bound fields | TimeTableDescriptionDataType.timeSlotTimesChangeable §A.2.30. | clause not printed |
| Duration, clock, and bound fields | UseCaseSupportType.useCaseAvailable §A.2.31. | clause not printed |
| Duration, clock, and bound fields | HeaderType.ackRequest §A.3.4. | clause not printed |

## Data file

protocols/spine-resources-1.3.0-data-points.tsv has one row for each of the 6507 data points. The columns are feature, function, element / identifier values, type, unit / scale, use cases and scenarios (M/R/O), server actor, client actor, operations, and shard locators. Ranges stay in the element cell. Server actor and client actor are not in the sources on every row. The locator cell cites the specification by title, version, and clause. An illustration value is not copied.

## Open points

| point | clause |
| --- | --- |
| ScaledNumberType. §3.10.1.7 and §3.10.1.8: scaledNumber = number * 10^scale; omitted scale means the value equals number; number SHALL be set; omitted scale uses 0. (§3.10.1.7, §3.10.1.8). The annex: the type is optional number plus optional scale, and no formula that combines them is printed. | §3.10.1.7, §3.10.1.8 |
| LabelType and DescriptionType. §3.10.1.2 and §3.10.1.3: label length SHOULD NOT exceed 256 characters; description SHOULD NOT exceed 4096; a longer value may be shortened by the receiver, and the sender SHALL allow that. (§3.10.1.2, §3.10.1.3). The annex: both types restrict xs:string with no facet. | §3.10.1.2, §3.10.1.3 |
| Datagram header presence. Table 3 marks header children such as specificationVersion, addresses, msgCounter, and cmdClassifier as M, with stated exceptions for optional children. Resource annex HeaderType gives every child minOccurs 0. (§A.3.4). | Table 3 |
| Payload cmd cardinality. Protocol: the model allows more than one cmd; this edition SHALL use exactly one, the first and the command section (§5.3.2). Annex: PayloadType.cmd is optional and unbounded. | §5.3.2 |
| errorNumber. On a result, 0 is a positive acknowledgement and every other value is negative; the code list is not printed with that rule. The resource specification names 0 no error, and codes 2 timeout, 6 command not supported, 7 rejected command, 8 unsupported restricted combination, 9 binding necessary. §7.3.2 and §7.3.5 use 7 for a refused binding request and 9 when a binding entry is required and missing (§7.3.2, §7.3.5). Annex ErrorNumberType is an xs:unsignedInt restriction with no further facet and no code list. | §7.3.2, §7.3.5 |
| minimumTrustLevel. Absence means unknown, and §7.1.1.5.4 says this edition uses the element only at feature level. Table 11 marks it reserved, and Annex B describes it as the level required before data exchange. The clauses say both are printed. | §7.1.1.5.4, Table 11, Annex B |
| CommodityTypeType clause number. One clause places it at §3.10.1.11 and places ScaledNumberSetType at §3.10.1.9. The common-type list cites CommodityTypeType at §3.10.1.9. | §3.10.1.11, §3.10.1.9 |
| Class name spelling. One heading prints SmartEnergManagementPs. Other sentences, and the later clauses of the resource specification, print SmartEnergyManagementPs. | clause not printed |
| Annex D of the protocol (informative recommendations) allows device A to drop a link after 30 seconds with no qualifying command and no detailed-discovery request, and to restart that 30 seconds if only detailed discovery arrived. No other cited clause prints that 30-second link timer. SHIP’s 30-second figures are different timers (CmiTimeout recommendation, keyMaterialState wait, T_hello_prolong_thr_inc). | Annex D |
