from __future__ import annotations

import re
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
DEVICE = ROOT / "devices" / "vr940f.md"
ARCHITECTURE = (
    ROOT
    / "architecture"
    / "_candidate"
    / "msp-085-live-r2-outdoor-temperature-promotion-evidence.md"
)
EVIDENCE = ROOT / "evidence" / "EV-20260811-001.md"


def front_matter(text: str) -> dict[str, str]:
    if not text.startswith("---\n"):
        raise AssertionError("page is missing YAML front matter")
    end = text.index("\n---\n", 4)
    metadata = yaml.safe_load(text[4:end])
    if not isinstance(metadata, dict):
        raise AssertionError("front matter must be a mapping")
    return metadata


def closed_profile(text: str) -> dict[str, object]:
    match = re.search(
        r"## Closed V1 Profile.*?```yaml\n(?P<profile>.*?)\n```",
        text,
        re.DOTALL,
    )
    if match is None:
        raise AssertionError("closed V1 profile is missing")
    profile = yaml.safe_load(match.group("profile"))
    if not isinstance(profile, dict):
        raise AssertionError("closed V1 profile must be a mapping")
    return profile


class Issue106OutdoorTemperaturePromotionEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.device = DEVICE.read_text(encoding="utf-8")
        cls.architecture = ARCHITECTURE.read_text(encoding="utf-8")
        cls.evidence = EVIDENCE.read_text(encoding="utf-8")
        cls.architecture_compact = " ".join(cls.architecture.split())
        cls.evidence_compact = " ".join(cls.evidence.split())
        cls.profile = closed_profile(cls.architecture)

    def test_candidate_is_unreleased_and_excluded_from_stable_channels(self) -> None:
        metadata = front_matter(self.architecture)
        self.assertEqual(metadata["publication_status"], "candidate")
        self.assertEqual(metadata["hypothesis_status"], "draft")
        for channel in (
            "stable_navigation",
            "search",
            "sitemap",
            "versioned_bundle",
            "release_bundle",
        ):
            self.assertEqual(metadata[channel], "false")

        self.assertEqual(self.profile["schema_version"], 1)
        self.assertEqual(self.profile["mode"], "read_only")
        self.assertIsNone(self.profile["mutable_proof"])
        for excluded in ("V2", "GraphQL", "Portal", "Home Assistant"):
            self.assertIn(excluded, self.architecture)

    def test_public_source_shape_discovers_and_privately_binds_selectors(self) -> None:
        source = self.profile["eebus_source"]
        self.assertEqual(
            source,
            {
                "entity_type": "TemperatureSensor",
                "feature_type": "Measurement",
                "feature_role": "server",
                "selector_binding": "exact_from_private_capture",
                "description_function": "measurementDescriptionListData",
                "value_function": "measurementListData",
                "measurement_id": 0,
                "scope_type": "outsideAirTemperature",
                "value_type": "DECIMAL",
                "unit": "degC",
                "value_representation": {
                    "number_field": "number",
                    "scale_field": "scale",
                    "value_type_field": "valueType",
                    "decimal_rule": "number_times_ten_to_scale",
                },
                "declared_constraints": {
                    "value_step_size": {"number": 5, "scale": -1},
                    "minimum_value": {"number": -6, "scale": 1},
                    "maximum_value": {"number": 8, "scale": 1},
                },
            },
        )
        for phrase in (
            "`TemperatureSensor`; native selector retained in the private capture",
            "`Measurement`, `server`; native selector retained in the private capture",
            "`measurementId=0`",
            "`outsideAirTemperature`, `degC`",
        ):
            self.assertIn(phrase, self.device)
        self.assertNotIn("raw_value", source)
        self.assertIn(
            "sample is evidence only and is not part of source identity",
            self.architecture_compact,
        )
        observed_entity_selector = "[" + "6" + "]"
        observed_feature_selector = "selector " + "11"
        self.assertNotIn(observed_entity_selector, self.architecture + self.device)
        self.assertNotIn(observed_feature_selector, self.architecture + self.device)

    def test_b524_identity_uses_the_admitted_capture_source(self) -> None:
        source = self.profile["ebus_source"]
        self.assertEqual(
            (source["opcode"], source["group"], source["instance"], source["register"]),
            ("0x02", "0x00", "0x00", "0x0073"),
        )
        self.assertEqual(source["source_address_binding"], "exact_from_private_capture")
        self.assertEqual(source["target_address_binding"], "exact_from_private_capture")
        self.assertEqual(source["target_product_class"], "BASV2")
        self.assertEqual(source["category"], "STATE")
        self.assertEqual(source["value_type"], "f32")
        self.assertIn(
            "exact admitted initiator and target addresses were corroborated and retained in the private record",
            self.evidence_compact,
        )
        old_fixture_source = "0x" + "F7"
        self.assertNotIn(
            old_fixture_source,
            self.architecture + self.evidence + self.device,
        )

    def test_capture_contract_owns_evidence_not_semantic_policy(self) -> None:
        capture = self.profile["capture"]
        self.assertEqual(
            capture,
            {
                "topology": "SAME_LAN",
                "slot_count": 6,
                "cadence_seconds": 10,
                "minimum_valid_pairs": 5,
                "maximum_missing_slots": 1,
                "maximum_pairing_skew_seconds": 5,
                "maximum_sample_age_seconds": 10,
                "require_single_capture_generation": True,
                "require_single_eebus_connection_generation": True,
                "require_single_ebus_poll_generation": True,
            },
        )
        for phrase in (
            "sample and poll identities",
            "capture-sample validity",
            "comparator execution and evidence",
            "Leaf Promotion Dossier assembly",
            "consumer freshness/stale/unavailable policy",
            "source precedence",
        ):
            self.assertIn(phrase, self.architecture)
        self.assertIn(
            "it is not a semantic freshness or unavailable policy",
            self.architecture_compact.lower(),
        )

    def test_numeric_window_is_closed_and_deterministic(self) -> None:
        comparator = self.profile["comparator"]
        self.assertEqual(
            comparator,
            {
                "id": "NUMERIC_WINDOW_OUTDOOR_TEMPERATURE_V1",
                "conversion": "identity_degC",
                "decision_rounding": "none",
                "report_rounding": "decimal_places_6_half_even",
                "tolerance_derivation": "eebus_declared_value_step_size",
                "tolerance_absolute_degC": "0.5",
                "equivalence_relation": "abs_delta_lte_declared_granularity",
                "metrological_accuracy_claim": False,
                "conflict_pair_threshold": 1,
                "match_requires_all_valid_pairs_in_tolerance": True,
            },
        )
        self.assertEqual(
            self.profile["terminal_precedence"],
            [
                "SOURCE_IDENTITY_MISMATCH",
                "GENERATION_CHANGED",
                "TYPE_MISMATCH",
                "UNIT_MISMATCH",
                "CAPTURE_SAMPLE_EXPIRED",
                "PAIRING_SKEW_EXCEEDED",
                "MISSING",
                "CONFLICT",
                "COEXISTENCE_DRIFT",
                "REPLAY_MISMATCH",
                "MATCH",
            ],
        )

    def test_dossier_requires_restart_replay_coexistence_and_no_mutable_proof(self) -> None:
        for phrase in (
            "second complete synchronized `MATCH` window after a full Home Assistant add-on restart",
            "passing M8 coexistence/no-drift evidence",
            "deterministic replay whose regenerated commitment equals the expected commitment",
            "`mutable_proof: null`",
            "rollback to zero-promotion",
        ):
            self.assertIn(phrase, self.architecture_compact)

    def test_publishable_observation_is_feasibility_not_promotion(self) -> None:
        metadata = front_matter(self.evidence)
        self.assertEqual(metadata["publication_status"], "publishable")
        self.assertEqual(metadata["source_class"], "observed_runtime")
        for phrase in (
            "`13 degC`",
            "`12.66796875 degC`",
            "`0.33203125 degC`",
            "`number=13`, `scale=0`, and `valueType=value`",
            "declared `0.5 degC` step",
            "seconds apart",
            "provides no comparator `MATCH`",
            "no Leaf Promotion Dossier",
            "no semantic promotion",
            "no metrological accuracy",
        ):
            self.assertIn(phrase, self.evidence_compact)

    def test_public_boundary_excludes_private_identity_and_consumer_leaks(self) -> None:
        for phrase in (
            "peer SKI",
            "SHIP ID",
            "SPINE device address",
            "fresh bundle-local pseudonyms",
            "private keys",
            "trust-store bytes",
            "`candidate_ref`",
            "`ebus.v1`",
        ):
            self.assertIn(phrase, self.architecture)

        self.assertIsNone(re.search(r"\b[0-9a-f]{40}\b", self.evidence, re.IGNORECASE))
        self.assertNotRegex(self.evidence, r"\b(?:10|127)\.\d+\.\d+\.\d+\b")
        self.assertNotRegex(self.evidence, r"\b192\.168\.\d+\.\d+\b")
        admitted_source = "0x" + "7F"
        target_address = "0x" + "15"
        self.assertNotIn(admitted_source, self.evidence)
        self.assertNotIn(target_address, self.evidence)
        self.assertIn("eBUS source and target addresses", self.architecture)


if __name__ == "__main__":
    unittest.main()
