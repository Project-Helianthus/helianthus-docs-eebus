from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import validate_repository_policy as repository_policy  # noqa: E402

PAGE = ROOT / "api" / "_candidate" / "eebus-output-binding-contract-v1.md"
PAGE_REL = Path("api/_candidate/eebus-output-binding-contract-v1.md")
MARKERS = (
    "The named input lenses are `lens.equipment_composition` and `lens.installation_hierarchy`, both read on the one retained captured cut.",
    "Ordinary parent and child entities come from a `contains` instance cited in this target's own report, and an EV entity is nested under its EVSE through `evse.relation.evse_connector` and `evse.relation.connector_vehicle` of the same cut.",
    "An entity composed from an index is rejected.",
    "A name and an address are rejected by the same rule as an index.",
    "An operation is admitted only through that resource's own capability.",
    "Visibility of a capability is not admission.",
    "An operation admitted from visibility alone is rejected.",
    "The persisted entity address is keyed by the resource identifier alone.",
    "The entity-address key does not contain an address, an ordinal, a cut identifier, a traversal path, or a plane.",
    "A feature value key is the resource identifier, the element definition, and the qualifier dimension values.",
    "A merge of two resources into one entity is declared loss in this target's own report.",
    "A loss that does not name this target is rejected.",
    "An element a use case requires, cited as absent in this report, is explicit absence and not a feature.",
    "Where the report cites neither the element nor an absence, the element stays unknown and is not a feature.",
    "Electrical context is medium `electrical` on a cited element, and it is never taken from a second lens.",
    "A thermal value of a heating zone, hot water or system outdoor sensor is a feature value of its SemReg element in kelvin.",
    "A sum is not an entity and not a feature.",
    "The report cites one served cut.",
    "A partial cut stays partial and is not repaired by invented entities.",
)
STALE = (
    "An entity composed from an index is accepted.",
    "An operation admitted from visibility alone is accepted.",
    "The persisted entity address is keyed by list position.",
    "Visibility of a capability admits the operation.",
    "The named input lens is `lens.equipment_composition`.",
    "No thermal quantity is placed on a resource.",
    "Parent and child entities come only from a `contains` instance cited in this target's own report.",
)
ENTITY_KEY_FIELDS = ("resource_id",)
ENTITY_KEY_EXCLUDED = (
    "entity_address",
    "ordinal",
    "cut_id",
    "path",
    "plane",
    "asset_id",
)
FEATURE_KEY_FIELDS = ("resource_id", "definition_id", "qualifiers")
FEATURE_KEY_EXCLUDED = (
    "entity_address",
    "ordinal",
    "cut_id",
    "pack_version",
    "plane",
    "asset_id",
)
ADMITTED_ENTITY = {
    "basis": "cited_contains",
    "cited": True,
    "coherent": True,
    "in_plane": True,
    "qualified": True,
}
ADMITTED_OPERATION = {
    "visible_in_lens": False,
    "own_capability": True,
    "qualified": True,
    "same_resource": True,
}
VECTOR_ROWS = (
    ("entity_from_index", "rejected"),
    ("operation_from_visibility", "rejected"),
    ("entity_from_cited_contains", "admitted"),
    ("operation_through_own_capability", "admitted"),
    ("ev_under_evse_two_links", "admitted"),
    ("ev_under_evse_link_missing", "rejected"),
)


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


class OutputBindingContractTest(unittest.TestCase):
    def test_page_is_candidate_and_states_the_binding_rules(self) -> None:
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
            "Proven.",
            "Hypothesis.",
            "Unknown.",
            "None of these classes is a device qualification.",
            *MARKERS,
        ):
            self.assertIn(phrase, text)
        for stale in STALE:
            self.assertNotIn(stale, text)

    def test_marker_pins_match_the_policy_constants(self) -> None:
        self.assertEqual(repository_policy.ISSUE179_REQUIRED_MARKERS, MARKERS)
        self.assertEqual(repository_policy.ISSUE179_STALE_MARKERS, STALE)
        self.assertEqual(repository_policy.ISSUE179_ENTITY_KEY_FIELDS, ENTITY_KEY_FIELDS)
        self.assertEqual(repository_policy.ISSUE179_FEATURE_KEY_FIELDS, FEATURE_KEY_FIELDS)

    def test_stated_vectors_are_the_contract_table(self) -> None:
        self.assertEqual(vector_rows(PAGE.read_text(encoding="utf-8")), list(VECTOR_ROWS))

    def test_entity_address_key_varies_only_the_resource_identifier(self) -> None:
        base = {
            "resource_id": "resource.meter.one",
            "entity_address": "address-one",
            "ordinal": 0,
            "cut_id": "cut-one",
            "path": "device/meter",
            "plane": "physical",
            "asset_id": "asset-one",
        }
        key = repository_policy.entity_address_key(base)
        self.assertEqual(key, ("resource.meter.one",))
        changed = dict(base)
        changed["resource_id"] = "resource.inverter.one"
        self.assertNotEqual(repository_policy.entity_address_key(changed), key)
        for field in ENTITY_KEY_EXCLUDED:
            mutated = dict(base)
            mutated[field] = "changed"
            self.assertEqual(repository_policy.entity_address_key(mutated), key, field)

    def test_feature_value_key_varies_each_of_its_three_fields(self) -> None:
        base = {
            "resource_id": "resource.meter.one",
            "definition_id": "fact.power",
            "qualifiers": ("medium", "electrical"),
            "entity_address": "address-one",
            "ordinal": 0,
            "cut_id": "cut-one",
            "pack_version": "pack-one",
            "plane": "physical",
            "asset_id": "asset-one",
        }
        key = repository_policy.feature_value_key(base)
        self.assertEqual(key, ("resource.meter.one", "fact.power", ("medium", "electrical")))
        replacements = {
            "resource_id": "resource.battery.one",
            "definition_id": "fact.energy",
            "qualifiers": ("medium", "other"),
        }
        for field, value in replacements.items():
            mutated = dict(base)
            mutated[field] = value
            self.assertNotEqual(repository_policy.feature_value_key(mutated), key, field)
        for field in FEATURE_KEY_EXCLUDED:
            mutated = dict(base)
            mutated[field] = "changed"
            self.assertEqual(repository_policy.feature_value_key(mutated), key, field)

    def test_persisted_address_follows_the_resource_identifier(self) -> None:
        base = {
            "resource_id": "resource.meter.one",
            "entity_address": "ignored",
            "ordinal": 0,
            "cut_id": "cut-one",
            "path": "device/meter",
            "plane": "physical",
            "asset_id": "asset-one",
        }
        store: dict[str, str] = {}
        assign = repository_policy.assign_entity_address
        self.assertEqual(assign(store, base, "address-one"), "persisted")
        self.assertEqual(store, {"resource.meter.one": "address-one"})
        for field in ENTITY_KEY_EXCLUDED:
            mutated = dict(base)
            mutated[field] = "changed"
            self.assertEqual(assign(store, mutated, "address-one"), "persisted", field)
        self.assertEqual(store, {"resource.meter.one": "address-one"})
        self.assertEqual(assign(store, base, "address-two"), "rejected")
        self.assertEqual(store, {"resource.meter.one": "address-one"})
        other = dict(base)
        other["resource_id"] = "resource.inverter.one"
        self.assertEqual(assign(store, other, "address-one"), "rejected")
        self.assertEqual(assign(store, other, "address-two"), "persisted")
        self.assertEqual(
            store,
            {
                "resource.meter.one": "address-one",
                "resource.inverter.one": "address-two",
            },
        )
        self.assertEqual(assign(store, {"resource_id": ""}, "address-three"), "rejected")

    def test_entity_composition_rejects_each_field_that_is_not_a_cited_contains(self) -> None:
        outcome = repository_policy.entity_composition_outcome
        self.assertEqual(outcome(ADMITTED_ENTITY), "admitted")
        mutations = {
            "basis": ("index", "name", "address"),
            "cited": (False,),
            "coherent": (False,),
            "in_plane": (False,),
            "qualified": (False,),
        }
        for field, values in mutations.items():
            for value in values:
                mutated = dict(ADMITTED_ENTITY)
                mutated[field] = value
                with self.subTest(field=field, value=value):
                    self.assertEqual(outcome(mutated), "rejected")

    def test_ev_under_evse_uses_the_two_cited_links_of_one_cut(self) -> None:
        """EV nesting fields: basis, both links, cited, coherent, in_plane, qualified.

        basis cited_contains stays admitted.
        basis evse_connector_vehicle with both links is admitted.
        a missing connector_vehicle link is rejected.
        any other basis is rejected.
        """
        outcome = repository_policy.entity_composition_outcome
        admitted = {
            "basis": "evse_connector_vehicle",
            "links": (
                "evse.relation.evse_connector",
                "evse.relation.connector_vehicle",
            ),
            "cited": True,
            "coherent": True,
            "in_plane": True,
            "qualified": True,
        }
        self.assertEqual(outcome(admitted), "admitted")
        self.assertEqual(outcome(ADMITTED_ENTITY), "admitted")
        missing = dict(admitted)
        missing["links"] = ("evse.relation.evse_connector",)
        self.assertEqual(outcome(missing), "rejected")
        other = dict(admitted)
        other["basis"] = "index"
        self.assertEqual(outcome(other), "rejected")

    def test_binding_page_names_both_lenses_and_the_thermal_value(self) -> None:
        text = normalized_page()
        publication = " ".join(
            (ROOT / "api/_candidate/eebus-output-publication-v1.md").read_text(encoding="utf-8").split()
        )
        for phrase in (
            "lens.equipment_composition",
            "lens.installation_hierarchy",
            "both read on the one retained captured cut",
            "lens.energy_flow",
            "EntryResource",
            "SumMembers",
            "Parts of two cuts are not combined into one output (CUT-1)",
            "valueSource",
            "calculatedValue",
            "A thermal value of a heating zone, hot water or system outdoor sensor is a feature value of its SemReg element in kelvin.",
            "Electrical context is medium `electrical` on a cited element, and it is never taken from a second lens.",
            "This output computes no sum (SUM-1).",
            "A sum is not an entity and not a feature.",
        ):
            self.assertIn(phrase, text)
        self.assertNotIn("The named input lens is `lens.equipment_composition`.", text)
        self.assertIn(
            "A thermal value of a heating zone, hot water or system outdoor sensor is a feature value of its SemReg element in kelvin.",
            publication,
        )

    def test_operation_admission_ignores_visibility_and_requires_each_capability_field(self) -> None:
        outcome = repository_policy.operation_admission_outcome
        self.assertEqual(outcome(ADMITTED_OPERATION), "admitted")
        visible = dict(ADMITTED_OPERATION)
        visible["visible_in_lens"] = True
        self.assertEqual(outcome(visible), "admitted")
        for field in ("own_capability", "qualified", "same_resource"):
            mutated = dict(ADMITTED_OPERATION)
            mutated[field] = False
            with self.subTest(field=field):
                self.assertEqual(outcome(mutated), "rejected")
        self.assertEqual(
            outcome(
                {
                    "visible_in_lens": True,
                    "own_capability": False,
                    "qualified": False,
                    "same_resource": False,
                }
            ),
            "rejected",
        )

    def test_required_element_and_loss_vary_each_decision_field(self) -> None:
        element = repository_policy.required_element_outcome
        for presence, expected in (
            ("feature", "feature"),
            ("absence", "explicit_absence"),
            ("unknown", "unknown"),
            ("index", "rejected"),
        ):
            with self.subTest(presence=presence):
                self.assertEqual(element({"presence": presence}), expected)
        loss = repository_policy.loss_outcome
        for kind in ("merged_resources", "flattened_qualifier", "frontier", "partial_cut"):
            with self.subTest(kind=kind):
                self.assertEqual(loss({"target": "eebus-output", "kind": kind}), "declared")
        self.assertEqual(loss({"target": "", "kind": "merged_resources"}), "rejected")
        self.assertEqual(loss({"target": "eebus-output", "kind": "index"}), "rejected")

    def test_policy_executes_the_stated_vectors_and_wires_them(self) -> None:
        self.assertEqual(repository_policy.issue_179_vector_errors(), [])
        self.assertEqual(repository_policy.issue_179_output_binding_errors(ROOT), [])
        source = (ROOT / "scripts" / "validate_repository_policy.py").read_text(encoding="utf-8")
        self.assertIn("issue_179_vector_errors()", source)
        self.assertIn("issue_179_output_binding_errors(root)", source)

    def test_repository_policy_rejects_each_dropped_marker(self) -> None:
        original = " ".join(PAGE.read_text(encoding="utf-8").split())
        for marker in MARKERS:
            with self.subTest(marker=marker), tempfile.TemporaryDirectory() as temporary:
                copied = Path(temporary)
                destination = copied / PAGE_REL
                destination.parent.mkdir(parents=True, exist_ok=True)
                self.assertIn(marker, original)
                destination.write_text(original.replace(marker, "omitted rule."), encoding="utf-8")
                errors = repository_policy.issue_179_output_binding_errors(copied)
            self.assertTrue(any(str(PAGE_REL) in error and "missing" in error for error in errors), errors)

    def test_repository_policy_rejects_stale_wording(self) -> None:
        original = " ".join(PAGE.read_text(encoding="utf-8").split())
        for marker in STALE:
            with self.subTest(marker=marker), tempfile.TemporaryDirectory() as temporary:
                copied = Path(temporary)
                destination = copied / PAGE_REL
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_text(original + " " + marker, encoding="utf-8")
                errors = repository_policy.issue_179_output_binding_errors(copied)
            self.assertTrue(any("stale issue-179 wording" in error for error in errors), errors)


if __name__ == "__main__":
    unittest.main()
