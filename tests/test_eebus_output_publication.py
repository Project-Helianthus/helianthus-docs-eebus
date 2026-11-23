from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import validate_repository_policy as repository_policy  # noqa: E402

PAGE = ROOT / "api" / "_candidate" / "eebus-output-publication-v1.md"
PAGE_REL = Path("api/_candidate/eebus-output-publication-v1.md")
MARKERS = (
    "The output is active when the eeBUS runtime is already enabled.",
    "There is no new switch.",
    "Publish every lens-admitted inverter, PV string, charger, battery, heating, grid-connection and meter resource.",
    "A heating resource is published.",
    "A battery resource is published.",
    "A meter resource is its own SubMeterElectricity entity beside the grid connection and is never merged into it.",
    "The EVSE total is the SemReg member sum of one cut and is marked derived.",
    "The node serves the heartbeat Limitation of Power Production V1.0.0 [LPP-031] defines.",
    "The EVSE operating state is a declared mapping from the EVSE statuses.",
    "| SemReg element | SPINE feature | scope | unit | conversion |",
    "A lens-admitted resource is one entity of this output (CID-1).",
    "An input-dimension fact is not a string (CID-4).",
    "A PV String entity is a child of the Inverter only through a cited contains instance (TRV-1).",
    "SHIP 1.0.1 §7 prints no fixed number of advertisements.",
    "The SPINE device type is a standard type of SPINE Resource Specification 1.3.0 Table 353 or a vendor-specific type matching SPINE Protocol Specification 1.3.0 §7.1.1.1.",
    "A second advertisement that meets SHIP 1.0.1 §7 is accepted.",
    "A second service that meets SHIP 1.0.1 §7 is accepted.",
    "The published entities include Inverter, a PV String child of that Inverter, EVSE, Battery, heating, the grid connection and a distinct meter.",
    "A use case that forbids that device type is not announced, and the loss names the prohibition.",
    "The actor Inverter of Monitoring of Inverter V1.0.0 is taken on entity type Inverter.",
    "The actor PV String of Monitoring of PV String V1.0.0 RC4 is taken when a string resource exists.",
    "The actor Inverter is the Controllable System of Limitation of Power Production V1.0.0.",
    "The actor EVSE of EVSE Commissioning and Configuration V1.0.1 is taken.",
    "The actor EVSE is the Monitored Unit of Monitoring of Power Consumption V1.0.0.",
    "The actor Inverter is the Monitored Unit of Monitoring of Power Consumption V1.0.0.",
    "The actor Battery of Monitoring of Battery V1.0.0 is taken.",
    "The HVAC monitoring actors of HVAC Temperature V1.0.0 and HVAC System Function V1.0.0 are taken.",
    "The actor Grid Connection Point of Monitoring of Grid Connection Point V1.0.0 is taken.",
    "The actor EVSE is the Controllable System of Limitation of Power Consumption V1.0.0.",
    "The local CEM takes Energy Guard of a limitation use case only while no trusted remote already announces Energy Guard for that use case.",
    "The CEM entity is never the Controllable System of one device.",
    "The CEM entity is never the Monitored Unit.",
    "A CEM-located Controllable System represents every device that CEM controls, not the CEM's own power.",
    "The node keeps one CEM entity.",
    "A use case is announced only when every mandatory scenario can be served from admitted elements of that resource.",
    "Otherwise the use case is not announced, and the loss names each missing element.",
    "Where a mandatory element is cited as absent, the loss names it (LRS-3, TGT-3).",
    "A mapped write is published only where that resource's own capability admits the operation (LRS-5, AUT-3).",
    "A production-limit write is mapped only through `pv.operation.set_active_power_limit` when that operation is admitted for that resource.",
    "A production-limit write is not mapped to the system export operation.",
    "A consumption-limit write is active power.",
    "The only admitted charger write is allocated current.",
    "A consumption-limit write on the EVSE entity is applied through `evse.operation.set_allocated_current`.",
    "Amperes = the limit in watts / (active phases × measured phase voltage), rounded down to a whole ampere and clamped to the station's range.",
    "A phase is active while its measured current is above zero; when no phase carries current and the charging session holds no remembered phase count, every phase with a measured voltage counts. The measured voltage is the mean of the active phases' measured voltages.",
    "While a charging session is paused by the limit, the conversion uses the number of phases that carried current when that pause began.",
    "The remembered phase count holds only for the same charging session; a new session, or an EV seen drawing on more phases, goes back to the phases that carry current and, with none yet, to every phase with a measured voltage, so a restart above the limit lasts at most one conversion cycle.",
    "Example: a single-phase EV on a station that measures 230 V on three phases is paused by a 1000 W limit; a limit raised to 3000 W in the same session gives 3000 / (1 × 230), rounded down to 13 A.",
    "While a consumption limit is effective, the allocated current is recomputed from each new measurement of phase current, measured voltage or configured current.",
    "While any phase carries current, every phase that has carried current since the EV connected also counts as active, so a phase that stops and later resumes is counted before it resumes.",
    "Where the charging station publishes no connection state, those phases are counted from the moment the consumption limit became effective.",
    "The measured phase voltage is the phase voltage the charging station publishes, when that resource publishes one.",
    "When the charging station publishes no phase voltage, the measured phase voltage is the measured AC phase voltage of another promoted resource of the same installation, an inverter AC side or a meter.",
    "Site and electrical relations select that resource when they exist.",
    "When the installation has exactly one other promoted source of AC phase voltage, that source is used.",
    "When more than one other promoted source publishes an AC phase voltage and no site or electrical relation selects one, the write is answered with a negative acknowledgement that names the missing measured voltage.",
    "From that other source, the measured voltage is the mean of the voltages it publishes on the charger's active phases, matched by phase.",
    "When the voltage source publishes no voltage on one of the charger's active phases, the write is answered with a negative acknowledgement that names the missing measured voltage.",
    "A nominal voltage is not a measured phase voltage.",
    "The station's range runs from 6 A to the station's configured current. A result below 6 A pauses charging: allocated current 0 A.",
    "A limit whose inputs are not published (measured voltage, phase current or configured current) is answered with a negative acknowledgement that names the missing input.",
    "When neither source publishes a phase voltage, the write is answered with a negative acknowledgement that names the missing measured voltage.",
    "Limitation of Power Consumption V1.0.0 is announced on the EVSE entity when the allocated-current operation is admitted for that resource and the host accepts limits, and the node serves the heartbeat Limitation of Power Consumption V1.0.0 [LPC-031] defines; each scenario keeps the specification's own mandatory, recommended or optional marking.",
    "The effective limit follows section 2.2 of the use case. A deactivated or expired limit releases the charger to the configured current. The failsafe values are pre-configured to 4200 W and 2 hours, stored, and may be changed by the Energy Guard.",
    "Unit conversion is display-only. The watt-to-ampere computation of a consumption limit is a control rule, not a unit conversion.",
    "A production-limit write on the Inverter entity is handed to the host and applied through `pv.operation.set_active_power_limit` in watts, with no conversion. Its effective limit follows the state machine of Limitation of Power Production V1.0.0; the failsafe production limit is pre-configured to the upper bound of `pv.limit.active_power` in the PV pack, which restricts nothing, and the failsafe duration minimum to 2 hours.",
    "An EV actor is announced when the SemReg elements its use case requires are present.",
    "The node presents the EV actor of each charging use case wherever SemReg has its elements.",
    "Overload protection, self-consumption during charging, and charging electricity measurement name the actor EV.",
    "Two overlapping writes are the existing conflict loss.",
    "The cited transport revision is SHIP 1.0.1.",
    "The cited data-model revision is SPINE 1.3.0.",
    "SHIP 1.1.0 is recorded as a later revision and is not the revision this node declares.",
    "The recorded revisions declare the mappings.",
    "Admitted inverter elements are inverter AC measurements, apparent power, reactive power, line-to-line voltage, energy, temperature and operating state.",
    "`pv.operation.set_active_power_limit` is admitted in watts.",
    "String-dimension DC quantities are admitted.",
    "Inverter apparent power, inverter reactive power and line-to-line voltage are admitted.",
    "The admitted charger operation is `evse.operation.set_allocated_current`.",
    "Canonical units are SI.",
    "or applies a watt limit without the measured voltage and active phases,",
    "No semantic element is added.",
    "No contract version is raised.",
    "Proven. Discovery follows SHIP 1.0.1 §7, and the SPINE device type follows SPINE Resource Specification 1.3.0 Table 353 or SPINE Protocol Specification 1.3.0 §7.1.1.1.",
    "Hypothesis. The actor selection and the announcement rule are this candidate.",
    "Unknown. The mandatory elements of each use case are not enumerated on this page.",
    "None of these classes is a device qualification.",
)
STALE = (
    "There is a new switch.",
    "One advertisement for SHIP stays.",
    "The device type is EnergyManagementSystem.",
    "Reject a second advertisement for SHIP.",
    "A second service is not added.",
    "A heating resource is not published.",
    "A battery resource is not published.",
    "Inverter apparent power, inverter reactive power and line-to-line voltage are not admitted.",
    "String-dimension DC quantities are not admitted.",
    "A use case whose device-side actor is EV is not announced.",
    "This node is not an EV.",
    "A meter, generic equipment, heating equipment and a battery stay outside this publication.",
    "The CEM entity is the Controllable System of one device.",
    "A watt limit is applied as allocated current.",
    "A newer revision of SHIP is cited.",
    "Watts are not converted to amperes.",
    "A watt limit is not applied as allocated current.",
    "Limitation of Power Consumption V1.0.0 is not announced while the write cannot be applied.",
    "An active-power limit is not an admitted charger write.",
    "Conversion is display-only.",
    "applies a watt limit as allocated current",
    "The mean of that other source is the mean of the phases it publishes.",
    "so the watt limit holds when the other phases resume.",
    "when no phase carries current, every phase with a measured voltage counts.",
)
VECTOR_ROWS = (
    ("heating_resource", "published"),
    ("battery_resource", "published"),
    ("inverter_resource", "published"),
    ("pv_string_resource", "published"),
    ("charger_resource", "published"),
    ("grid_connection_resource", "published"),
    ("meter_resource", "published"),
    ("grid_and_meter_one_cut", "both_published"),
    ("service_name_other", "rejected"),
    ("instance_name_over_63", "rejected"),
    ("mandatory_txt_missing", "rejected"),
    ("txtvers_other", "rejected"),
    ("txt_record_over_400", "rejected"),
    ("ship_id_not_unique", "rejected"),
    ("device_type_inverter", "accepted"),
    ("device_type_vendor", "accepted"),
    ("device_type_vendor_rejected", "rejected"),
    ("announcement_without_txt_type", "accepted"),
    ("extra_optional_key", "accepted"),
    ("instance_renamed_same_id", "accepted"),
    ("second_advertisement_meets_section_7", "accepted"),
    ("second_service_meets_section_7", "accepted"),
    ("cem_controllable_system", "rejected"),
    ("inverter_controllable_system", "taken"),
    ("inverter_monitored_unit", "taken"),
    ("evse_monitored_unit", "taken"),
    ("watt_limit_as_current", "converted"),
    ("watt_limit_below_minimum", "paused"),
    ("watt_limit_without_voltage", "refused"),
    ("watt_limit_paused_single_phase", "converted"),
    ("production_limit_write", "applied"),
)
RESOURCE_FIELDS = (
    "family",
    "lens_admitted",
    "runtime_enabled",
    "input_dimension",
    "parent",
)
SHIP_FIELDS = (
    "service_name",
    "instance_name_bytes",
    "mandatory_txt_complete",
    "txtvers",
    "txt_record_bytes",
    "ship_id_unique",
    "device_type",
    "txt_type_present",
    "extra_optional_key",
    "instance_renamed_same_id",
    "advertisement_count",
    "service_count",
)
ACTOR_FIELDS = (
    "use_case",
    "actor",
    "entity_type",
    "string_resource",
    "remote_energy_guard",
)
WRITE_FIELDS = (
    "limit_kind",
    "operation",
    "unit",
    "admitted",
    "converted",
    "voltage_source",
    "active_phase_voltages_published",
    "phase_current_published",
    "configured_current_published",
    "below_minimum",
)
ANNOUNCEMENT_FIELDS = (
    "use_case",
    "device_type_permitted",
    "device_type",
    "missing_elements",
    "device_actor",
    "allocated_current_admitted",
    "host_accepts_limits",
    "overlapping",
)
EXCLUDED = ("ordinal", "address", "plane")


def normalized_page() -> str:
    return " ".join(PAGE.read_text(encoding="utf-8").split())


def vector_rows(text: str) -> list[tuple[str, str]]:
    section = text.split("## Vectors", 1)[1]
    section = section.split("\n## ", 1)[0]
    rows: list[tuple[str, str]] = []
    for line in section.splitlines():
        if not line.startswith("| `"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        rows.append((cells[0].strip("`"), cells[2].strip()))
    return rows


def resource_record(**overrides: object) -> dict[str, object]:
    record: dict[str, object] = {
        "family": "inverter",
        "lens_admitted": True,
        "runtime_enabled": True,
        "input_dimension": False,
        "parent": "",
    }
    record.update(overrides)
    return record


def ship_record(**overrides: object) -> dict[str, object]:
    record: dict[str, object] = {
        "service_name": "ship",
        "instance_name_bytes": 32,
        "mandatory_txt_complete": True,
        "txtvers": "1",
        "txt_record_bytes": 120,
        "ship_id_unique": True,
        "device_type": "EnergyManagementSystem",
        "txt_type_present": False,
        "extra_optional_key": False,
        "instance_renamed_same_id": False,
        "advertisement_count": 1,
        "service_count": 1,
    }
    record.update(overrides)
    return record


def actor_record(**overrides: object) -> dict[str, object]:
    record: dict[str, object] = {
        "use_case": "limitation_of_power_production",
        "actor": "Controllable System",
        "entity_type": "Inverter",
        "string_resource": False,
        "remote_energy_guard": False,
    }
    record.update(overrides)
    return record


def write_record(**overrides: object) -> dict[str, object]:
    record: dict[str, object] = {
        "limit_kind": "production",
        "operation": "pv.operation.set_active_power_limit",
        "unit": "W",
        "admitted": True,
        "converted": False,
        "voltage_source": "station",
        "active_phase_voltages_published": True,
        "phase_current_published": True,
        "configured_current_published": True,
        "below_minimum": False,
    }
    record.update(overrides)
    return record


def announcement_record(**overrides: object) -> dict[str, object]:
    record: dict[str, object] = {
        "use_case": "monitoring_of_inverter",
        "device_type_permitted": True,
        "device_type": "Inverter",
        "missing_elements": (),
        "device_actor": "Inverter",
        "allocated_current_admitted": True,
        "host_accepts_limits": True,
        "overlapping": False,
    }
    record.update(overrides)
    return record


def assert_key_changes(test: unittest.TestCase, key, base: dict[str, object], replacements: dict[str, object]) -> None:
    original = key(base)
    for field, value in replacements.items():
        mutated = dict(base)
        mutated[field] = value
        test.assertNotEqual(key(mutated), original, field)
    for field in EXCLUDED:
        mutated = dict(base)
        mutated[field] = "changed"
        test.assertEqual(key(mutated), original, field)


class OutputPublicationTest(unittest.TestCase):
    def test_page_is_candidate_and_states_the_publication_rule(self) -> None:
        text = normalized_page()
        for phrase in (
            'publication_status: "candidate"',
            'stable_navigation: "false"',
            'search: "false"',
            'sitemap: "false"',
            'versioned_bundle: "false"',
            'release_bundle: "false"',
            'candidate_output: "true"',
            "## Evidence class",
            "SHIP 1.0.1",
            "SPINE 1.3.0",
            *MARKERS,
        ):
            self.assertIn(phrase, text)
        for stale in STALE:
            self.assertNotIn(stale, text)
        cited = text.replace("SHIP 1.0.1", "").replace("SHIP 1.1.0", "")
        self.assertNotIn("SHIP 1.", cited)

    def test_marker_pins_match_the_policy_constants(self) -> None:
        self.assertEqual(repository_policy.ISSUE186_REQUIRED_MARKERS, MARKERS)
        self.assertEqual(repository_policy.ISSUE186_STALE_MARKERS, STALE)
        self.assertEqual(repository_policy.ISSUE186_RESOURCE_KEY_FIELDS, RESOURCE_FIELDS)
        self.assertEqual(repository_policy.ISSUE186_SHIP_KEY_FIELDS, SHIP_FIELDS)
        self.assertEqual(repository_policy.ISSUE186_ACTOR_KEY_FIELDS, ACTOR_FIELDS)
        self.assertEqual(repository_policy.ISSUE186_WRITE_KEY_FIELDS, WRITE_FIELDS)
        self.assertEqual(
            repository_policy.ISSUE186_ANNOUNCEMENT_KEY_FIELDS,
            ANNOUNCEMENT_FIELDS,
        )
        self.assertEqual(
            repository_policy.ISSUE186_PUBLISHED_FAMILIES,
            frozenset(
                {
                    "battery",
                    "charger",
                    "grid_connection",
                    "heating",
                    "inverter",
                    "meter",
                    "pv_string",
                }
            ),
        )
        self.assertEqual(repository_policy.ISSUE186_REJECTED_FAMILIES, frozenset())

    def test_stated_vectors_are_the_contract_table(self) -> None:
        rows = vector_rows(PAGE.read_text(encoding="utf-8"))
        self.assertEqual(rows, list(VECTOR_ROWS))
        policy_rows = [
            (name, expected)
            for name, _function, _record, expected in repository_policy.ISSUE186_VECTORS
        ]
        self.assertEqual(policy_rows, list(VECTOR_ROWS))

    def test_resource_identity_varies_each_field(self) -> None:
        """Resource fields: family, lens_admitted, runtime_enabled, input_dimension, parent.

        family: generic equipment is not published.
        lens_admitted: false is not published.
        runtime_enabled: false is not published.
        input_dimension: true on a PV string is not published.
        parent: a PV string without the inverter parent is not published.
        """
        outcome = repository_policy.published_resource_outcome
        base = resource_record()
        self.assertEqual(outcome(base), "published")
        assert_key_changes(
            self,
            repository_policy.publication_resource_key,
            base,
            {
                "family": "generic",
                "lens_admitted": False,
                "runtime_enabled": False,
                "input_dimension": True,
                "parent": "inverter",
            },
        )
        self.assertEqual(outcome(resource_record(family="heating")), "published")
        self.assertEqual(outcome(resource_record(family="battery")), "published")
        self.assertEqual(outcome(resource_record(family="grid_connection")), "published")
        self.assertEqual(outcome(resource_record(family="meter")), "published")
        self.assertEqual(outcome(resource_record(family="generic")), "not_published")
        both = repository_policy.same_cut_entities_outcome(
            {
                "families": ("grid_connection", "meter"),
                "same_cut": True,
                "meter_distinct": True,
            }
        )
        self.assertEqual(both, "both_published")
        merged = repository_policy.same_cut_entities_outcome(
            {
                "families": ("grid_connection", "meter"),
                "same_cut": True,
                "meter_distinct": False,
            }
        )
        self.assertEqual(merged, "not_published")
        self.assertEqual(outcome(resource_record(lens_admitted=False)), "not_published")
        self.assertEqual(outcome(resource_record(runtime_enabled=False)), "not_published")
        string = resource_record(family="pv_string", parent="inverter")
        self.assertEqual(outcome(string), "published")
        self.assertEqual(
            outcome(resource_record(family="pv_string", parent="inverter", input_dimension=True)),
            "not_published",
        )
        self.assertEqual(outcome(resource_record(family="pv_string", parent="")), "not_published")
        self.assertEqual(outcome(resource_record(family="charger")), "published")

    def test_ship_identity_varies_each_field(self) -> None:
        """SHIP fields: service_name, instance_name_bytes, mandatory_txt_complete, txtvers, txt_record_bytes, ship_id_unique, device_type, txt_type_present, extra_optional_key, instance_renamed_same_id, advertisement_count, service_count.

        service_name: a name other than ship is rejected.
        instance_name_bytes: 64 is rejected.
        mandatory_txt_complete: false is rejected.
        txtvers: a value other than 1 is rejected.
        txt_record_bytes: 401 is rejected.
        ship_id_unique: false is rejected.
        device_type: Inverter is accepted; GridGuard is rejected.
        txt_type_present: false is accepted.
        extra_optional_key: true within 400 bytes is accepted.
        instance_renamed_same_id: true is accepted.
        advertisement_count: 2 that meets section 7 is accepted.
        service_count: 2 that meets section 7 is accepted.
        """
        outcome = repository_policy.ship_advertisement_outcome
        base = ship_record()
        self.assertEqual(outcome(base), "accepted")
        assert_key_changes(
            self,
            repository_policy.ship_advertisement_key,
            base,
            {
                "service_name": "other",
                "instance_name_bytes": 64,
                "mandatory_txt_complete": False,
                "txtvers": "2",
                "txt_record_bytes": 401,
                "ship_id_unique": False,
                "device_type": "Inverter",
                "txt_type_present": True,
                "extra_optional_key": True,
                "instance_renamed_same_id": True,
                "advertisement_count": 2,
                "service_count": 2,
            },
        )
        self.assertEqual(outcome(ship_record(service_name="other")), "rejected")
        self.assertEqual(outcome(ship_record(instance_name_bytes=64)), "rejected")
        self.assertEqual(outcome(ship_record(mandatory_txt_complete=False)), "rejected")
        self.assertEqual(outcome(ship_record(txtvers="2")), "rejected")
        self.assertEqual(outcome(ship_record(txt_record_bytes=401)), "rejected")
        self.assertEqual(outcome(ship_record(ship_id_unique=False)), "rejected")
        self.assertEqual(outcome(ship_record(device_type="Inverter")), "accepted")
        self.assertEqual(outcome(ship_record(device_type="_n:acme_HeatPump")), "accepted")
        self.assertEqual(outcome(ship_record(device_type="GridGuard")), "rejected")
        self.assertEqual(outcome(ship_record(txt_type_present=False)), "accepted")
        self.assertEqual(outcome(ship_record(extra_optional_key=True)), "accepted")
        self.assertEqual(outcome(ship_record(instance_renamed_same_id=True)), "accepted")
        self.assertEqual(outcome(ship_record(advertisement_count=2)), "accepted")
        self.assertEqual(outcome(ship_record(service_count=2)), "accepted")

    def test_actor_identity_varies_each_field(self) -> None:
        """Actor fields: use_case, actor, entity_type, string_resource, remote_energy_guard.

        use_case: an inverter controllable system of consumption is not taken.
        actor: CEM as Controllable System is rejected; CEM as Energy Guard is taken.
        entity_type: CEM as Controllable System is rejected; Inverter is taken.
        string_resource: false on the PV string binding is not taken.
        remote_energy_guard: true blocks the local CEM Energy Guard.
        """
        outcome = repository_policy.actor_binding_outcome
        base = actor_record()
        self.assertEqual(outcome(base), "taken")
        assert_key_changes(
            self,
            repository_policy.actor_binding_key,
            base,
            {
                "use_case": "limitation_of_power_consumption",
                "actor": "Energy Guard",
                "entity_type": "CEM",
                "string_resource": True,
                "remote_energy_guard": True,
            },
        )
        self.assertEqual(
            outcome(actor_record(use_case="limitation_of_power_consumption")),
            "not_taken",
        )
        self.assertEqual(outcome(actor_record(entity_type="CEM")), "rejected")
        self.assertEqual(
            outcome(actor_record(actor="Energy Guard", entity_type="CEM")),
            "taken",
        )
        self.assertEqual(
            outcome(
                actor_record(
                    use_case="monitoring_of_power_consumption",
                    actor="Monitored Unit",
                    entity_type="CEM",
                )
            ),
            "rejected",
        )
        self.assertEqual(
            outcome(
                actor_record(
                    use_case="monitoring_of_pv_string",
                    actor="PV String",
                    entity_type="PV String",
                    string_resource=True,
                )
            ),
            "taken",
        )
        self.assertEqual(
            outcome(
                actor_record(
                    use_case="monitoring_of_pv_string",
                    actor="PV String",
                    entity_type="PV String",
                    string_resource=False,
                )
            ),
            "not_taken",
        )
        self.assertEqual(
            outcome(
                actor_record(
                    actor="Energy Guard",
                    entity_type="CEM",
                    remote_energy_guard=True,
                )
            ),
            "not_taken",
        )
        self.assertEqual(outcome(actor_record(actor="EV", entity_type="EV")), "not_taken")
        self.assertEqual(
            outcome(
                actor_record(
                    use_case="ev_commissioning_and_configuration",
                    actor="EV",
                    entity_type="EV",
                )
            ),
            "taken",
        )
        self.assertEqual(
            outcome(
                actor_record(
                    use_case="monitoring_of_power_consumption",
                    actor="Monitored Unit",
                    entity_type="Inverter",
                )
            ),
            "taken",
        )

    def test_write_identity_varies_each_field(self) -> None:
        """Write fields: limit_kind, operation, unit, admitted, converted, voltage_source, active_phase_voltages_published, phase_current_published, configured_current_published, below_minimum.

        limit_kind: a consumption write through the production operation is rejected.
        operation: a system-export write is rejected; allocated current converts a watt limit.
        unit: amperes are rejected.
        admitted: false is not applied.
        converted: a display unit conversion is rejected.
        voltage_source: an empty source refuses the watt limit; the installation source converts it.
        active_phase_voltages_published: false refuses the watt limit and names measured voltage.
        phase_current_published: false refuses the watt limit and names phase current.
        configured_current_published: false refuses the watt limit and names configured current.
        below_minimum: true pauses a complete watt limit at allocated current 0 A.
        """
        outcome = repository_policy.write_mapping_outcome
        base = write_record()
        self.assertEqual(outcome(base), "applied")
        assert_key_changes(
            self,
            repository_policy.write_mapping_key,
            base,
            {
                "limit_kind": "consumption",
                "operation": "system export",
                "unit": "A",
                "admitted": False,
                "converted": True,
                "voltage_source": "",
                "active_phase_voltages_published": False,
                "phase_current_published": False,
                "configured_current_published": False,
                "below_minimum": True,
            },
        )
        self.assertEqual(outcome(write_record(limit_kind="consumption")), "rejected")
        self.assertEqual(outcome(write_record(operation="system export")), "rejected")
        self.assertEqual(outcome(write_record(unit="A")), "rejected")
        self.assertEqual(outcome(write_record(admitted=False)), "not_applied")
        self.assertEqual(outcome(write_record(converted=True)), "rejected")
        self.assertEqual(outcome(write_record(voltage_source="")), "applied")
        self.assertEqual(outcome(write_record(active_phase_voltages_published=False)), "applied")
        self.assertEqual(outcome(write_record(phase_current_published=False)), "applied")
        self.assertEqual(outcome(write_record(configured_current_published=False)), "applied")
        self.assertEqual(outcome(write_record(below_minimum=True)), "applied")
        self.assertEqual(outcome(self._consumption()), "converted")

    def _consumption(self, **overrides: object) -> dict[str, object]:
        record = write_record(
            limit_kind="consumption",
            operation="evse.operation.set_allocated_current",
        )
        record.update(overrides)
        return record

    def test_consumption_limit_varies_voltage_phases_and_range(self) -> None:
        """Consumption inputs: voltage_source, phase_current_published, configured_current_published, below_minimum.

        voltage_source station: the charging station's phase voltage converts the limit.
        voltage_source installation: the one other promoted AC source converts the limit.
        voltage_source empty, nominal, or several: the write is refused and names measured voltage.
        active_phase_voltages_published false: a source without a voltage on one of the charger's active phases refuses and names measured voltage.
        phase_current_published false: the write is refused and names phase current.
        configured_current_published false: the write is refused and names configured current.
        below_minimum true: a complete limit pauses; a missing voltage still refuses.
        """
        outcome = repository_policy.write_mapping_outcome
        missing = repository_policy.consumption_missing_input
        station = self._consumption()
        installation = self._consumption(voltage_source="installation")
        self.assertEqual(outcome(station), "converted")
        self.assertEqual(missing(station), "")
        self.assertEqual(outcome(installation), "converted")
        self.assertEqual(missing(installation), "")
        self.assertEqual(outcome(self._consumption(below_minimum=True, voltage_source="installation")), "paused")
        absent = self._consumption(voltage_source="")
        nominal = self._consumption(voltage_source="nominal")
        self.assertEqual(outcome(absent), "refused")
        self.assertEqual(missing(absent), "measured_voltage")
        self.assertEqual(outcome(nominal), "refused")
        self.assertEqual(missing(nominal), "measured_voltage")
        unmatched = self._consumption(voltage_source="installation", active_phase_voltages_published=False)
        self.assertEqual(outcome(unmatched), "refused")
        self.assertEqual(missing(unmatched), "measured_voltage")
        unmatched_station = self._consumption(active_phase_voltages_published=False)
        self.assertEqual(outcome(unmatched_station), "refused")
        self.assertEqual(missing(unmatched_station), "measured_voltage")
        several = self._consumption(voltage_source="several")
        self.assertEqual(outcome(several), "refused")
        self.assertEqual(missing(several), "measured_voltage")
        no_phase = self._consumption(phase_current_published=False, voltage_source="installation")
        self.assertEqual(outcome(no_phase), "refused")
        self.assertEqual(missing(no_phase), "phase_current")
        no_configured = self._consumption(configured_current_published=False)
        self.assertEqual(outcome(no_configured), "refused")
        self.assertEqual(missing(no_configured), "configured_current")
        self.assertEqual(outcome(self._consumption(below_minimum=True)), "paused")
        self.assertEqual(missing(self._consumption(below_minimum=True)), "")
        self.assertEqual(outcome(self._consumption(below_minimum=True, voltage_source="")), "refused")
        self.assertEqual(outcome(self._consumption(operation="active power")), "rejected")
        self.assertEqual(outcome(self._consumption(unit="A")), "rejected")
        self.assertEqual(outcome(self._consumption(admitted=False)), "not_applied")
        self.assertEqual(outcome(self._consumption(converted=True)), "rejected")
        both_missing = self._consumption(voltage_source="", phase_current_published=False)
        self.assertEqual(missing(both_missing), "measured_voltage")

    def _paused(self, **overrides: object) -> dict[str, object]:
        record: dict[str, object] = {
            "limit_w": 3000,
            "phase_currents": (0, 0, 0),
            "phase_voltages": (230, 230, 230),
            "measured_voltage": 230,
            "configured_current": 16,
            "paused_phase_count": 1,
            "same_session": True,
        }
        record.update(overrides)
        return record

    def test_paused_single_phase_session_keeps_its_phase_count(self) -> None:
        """A single-phase EV paused by a 1000 W limit restarts when the limit allows it.

        Pause: one phase at 230 V carries current; 1000 W gives 4 A, below 6 A, so 0 A.
        Same session, limit raised to 3000 W, no phase carries current: the remembered
        single phase gives 13 A, not the 4 A of three phases with a measured voltage.
        New session: the remembered count is dropped and three phases count again.
        An EV seen drawing on more phases counts those phases.
        """
        phases = repository_policy.consumption_active_phase_count
        amperes = repository_policy.consumption_allocated_current
        outcome = repository_policy.consumption_conversion_outcome
        pause = self._paused(limit_w=1000, phase_currents=(10, 0, 0), paused_phase_count=0)
        self.assertEqual(phases(pause), 1)
        self.assertEqual(amperes(pause), 0)
        self.assertEqual(outcome(pause), "paused")
        raised = self._paused()
        self.assertEqual(phases(raised), 1)
        self.assertEqual(amperes(raised), 13)
        self.assertEqual(outcome(raised), "converted")
        new_session = self._paused(same_session=False)
        self.assertEqual(phases(new_session), 3)
        self.assertEqual(amperes(new_session), 0)
        self.assertEqual(outcome(new_session), "paused")
        nothing_remembered = self._paused(paused_phase_count=0)
        self.assertEqual(phases(nothing_remembered), 3)
        self.assertEqual(outcome(nothing_remembered), "paused")
        more_phases = self._paused(phase_currents=(13, 13, 13))
        self.assertEqual(phases(more_phases), 3)
        self.assertEqual(amperes(more_phases), 0)
        clamped = self._paused(limit_w=7000)
        self.assertEqual(amperes(clamped), 16)

    def test_announcement_identity_varies_each_field(self) -> None:
        """Announcement fields: use_case, device_type_permitted, device_type, missing_elements, device_actor, allocated_current_admitted, host_accepts_limits, overlapping.

        use_case: a name outside the membership is not announced.
        device_type_permitted: false is not announced.
        device_type: the loss names the forbidden type.
        missing_elements: the loss names each element.
        device_actor: an EV actor with its required elements is announced.
        allocated_current_admitted: false withholds Limitation of Power Consumption and names the operation.
        host_accepts_limits: false withholds Limitation of Power Consumption and names the host.
        overlapping: true is the conflict loss.
        """
        outcome = repository_policy.use_case_announcement_outcome
        loss = repository_policy.publication_loss
        base = announcement_record()
        self.assertEqual(outcome(base), "announced")
        self.assertEqual(loss(base), ())
        assert_key_changes(
            self,
            repository_policy.use_case_announcement_key,
            base,
            {
                "use_case": "unrecorded_use_case",
                "device_type_permitted": False,
                "device_type": "GridGuard",
                "missing_elements": ("energy",),
                "device_actor": "EV",
                "allocated_current_admitted": False,
                "host_accepts_limits": False,
                "overlapping": True,
            },
        )
        self.assertEqual(outcome(announcement_record(use_case="unrecorded_use_case")), "not_announced")
        denied = announcement_record(device_type_permitted=False)
        self.assertEqual(outcome(denied), "not_announced")
        self.assertEqual(loss(denied), ("device_type_prohibition", "Inverter"))
        other_type = announcement_record(device_type_permitted=False, device_type="GridGuard")
        self.assertEqual(loss(other_type), ("device_type_prohibition", "GridGuard"))
        one_missing = announcement_record(missing_elements=("energy",))
        two_missing = announcement_record(missing_elements=("energy", "temperature"))
        self.assertEqual(loss(one_missing), ("energy",))
        self.assertEqual(loss(two_missing), ("energy", "temperature"))
        ev_actor = announcement_record(
            device_actor="EV",
            use_case="ev_commissioning_and_configuration",
        )
        self.assertEqual(outcome(ev_actor), "announced")
        self.assertEqual(loss(ev_actor), ())
        ev_missing = announcement_record(
            device_actor="EV",
            use_case="ev_commissioning_and_configuration",
            missing_elements=("state_of_charge",),
        )
        self.assertEqual(outcome(ev_missing), "not_announced")
        self.assertEqual(loss(ev_missing), ("state_of_charge",))
        battery = announcement_record(
            use_case="monitoring_of_battery",
            device_actor="Battery",
            device_type="Generic",
        )
        self.assertEqual(outcome(battery), "announced")
        overlap = announcement_record(overlapping=True)
        self.assertEqual(outcome(overlap), "conflict")
        self.assertEqual(loss(overlap), ("conflict",))
        applied = announcement_record(
            use_case="limitation_of_power_consumption",
            device_actor="EVSE",
            write_outcome="refused",
        )
        self.assertEqual(outcome(applied), "announced")
        self.assertEqual(loss(applied), ())
        paused = announcement_record(
            use_case="limitation_of_power_consumption",
            device_actor="EVSE",
            write_outcome="paused",
        )
        self.assertEqual(outcome(paused), "announced")
        not_admitted = announcement_record(
            use_case="limitation_of_power_consumption",
            device_actor="EVSE",
            allocated_current_admitted=False,
        )
        self.assertEqual(outcome(not_admitted), "not_announced")
        self.assertEqual(loss(not_admitted), ("allocated_current_not_admitted",))
        host_rejects = announcement_record(
            use_case="limitation_of_power_consumption",
            device_actor="EVSE",
            host_accepts_limits=False,
        )
        self.assertEqual(outcome(host_rejects), "not_announced")
        self.assertEqual(loss(host_rejects), ("host_rejects_limits",))
        both = announcement_record(
            use_case="limitation_of_power_consumption",
            device_actor="EVSE",
            allocated_current_admitted=False,
            host_accepts_limits=False,
        )
        self.assertEqual(loss(both), ("allocated_current_not_admitted",))

    def test_policy_executes_the_stated_vectors_and_wires_them(self) -> None:
        self.assertEqual(repository_policy.issue_186_vector_errors(), [])
        self.assertEqual(repository_policy.issue_186_output_publication_errors(ROOT), [])
        source = (ROOT / "scripts" / "validate_repository_policy.py").read_text(encoding="utf-8")
        self.assertIn("issue_186_vector_errors()", source)
        self.assertIn("issue_186_output_publication_errors(root)", source)

    def test_repository_policy_rejects_each_dropped_marker(self) -> None:
        original = normalized_page()
        for marker in MARKERS:
            with self.subTest(marker=marker), tempfile.TemporaryDirectory() as temporary:
                copied = Path(temporary)
                destination = copied / PAGE_REL
                destination.parent.mkdir(parents=True, exist_ok=True)
                self.assertIn(marker, original)
                destination.write_text(original.replace(marker, "omitted rule."), encoding="utf-8")
                errors = repository_policy.issue_186_output_publication_errors(copied)
            self.assertTrue(any(str(PAGE_REL) in error and "missing" in error for error in errors), errors)

    def test_repository_policy_rejects_stale_wording(self) -> None:
        original = normalized_page()
        for marker in STALE:
            with self.subTest(marker=marker), tempfile.TemporaryDirectory() as temporary:
                copied = Path(temporary)
                destination = copied / PAGE_REL
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_text(original + " " + marker, encoding="utf-8")
                errors = repository_policy.issue_186_output_publication_errors(copied)
            self.assertTrue(any("stale issue-186 wording" in error for error in errors), errors)


if __name__ == "__main__":
    unittest.main()
