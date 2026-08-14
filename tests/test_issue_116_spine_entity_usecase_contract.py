from __future__ import annotations

import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
API = ROOT / "api/_candidate/post-m9-operator-admin-v1.md"
EVIDENCE = ROOT / "evidence/EV-20260814-001.md"


def read_markdown(path: Path) -> tuple[dict[str, str], str]:
    text = path.read_text(encoding="utf-8")
    _, front_matter, body = text.split("---", 2)
    return yaml.safe_load(front_matter), body


class EntityScopedUseCaseContractTest(unittest.TestCase):
    def test_redacted_live_evidence_is_publishable_and_bounded(self) -> None:
        metadata, body = read_markdown(EVIDENCE)
        self.assertEqual(metadata["publication_status"], "publishable")
        self.assertEqual(metadata["claim_status"], "evidence-backed")
        self.assertEqual(metadata["source_class"], "observed_runtime")
        self.assertEqual(metadata["evidence_ids"], "EV-20260814-001")

        normalized = " ".join(body.split())
        for phrase in (
            "one remote device, eleven entities, twenty features, and twenty-two use-case claims",
            "canonical `context_address` exactly equalled one of the eleven entity addresses",
            "None equalled a feature address",
            "returned no contract error",
            "categorical `admin_boundary_unavailable` response and no partial tree",
            "does not promote a use case into semantic support",
            "contains no SKI, SHIP ID, device or SPINE address, endpoint, private network coordinate",
        ):
            self.assertIn(phrase, normalized)

    def test_lazy_tree_resolves_exact_feature_then_exact_entity_scope(self) -> None:
        metadata, body = read_markdown(API)
        self.assertIn("EV-20260814-001", metadata["evidence_ids"])
        normalized = " ".join(body.split())
        for phrase in (
            "Parent resolution is closed and deterministic",
            "an exact feature-address match makes the claim a child of that feature",
            "an exact entity-address match makes it a child of that entity",
            "entity-scoped claim, not a missing feature",
            "does not synthesize a feature, rewrite `context_address`, or copy an entity-scoped claim onto every feature",
            "matches neither one exact feature address nor one exact entity address",
            "fails closed as `admin_boundary_unavailable`",
            "Claims for another partner remain excluded",
        ):
            self.assertIn(phrase, normalized)


if __name__ == "__main__":
    unittest.main()
