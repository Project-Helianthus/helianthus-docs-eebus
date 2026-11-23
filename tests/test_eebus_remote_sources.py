from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import validate_repository_policy as repository_policy  # noqa: E402

PAGE = ROOT / "api" / "_candidate" / "eebus-remote-sources-v1.md"
README = ROOT / "api" / "README.md"
SECTIONS = (
    "## Actors and use cases",
    "## Values",
    "## Identity",
    "## Unchanged surfaces",
    "## Vectors",
)
EXPECTED = {
    "wh_to_joule": "3600 J",
    "percent_to_ratio": "0.5",
    "grid_consumption_positive": "stored positive consumption",
    "grid_production_negative": "stored negative production",
    "identity_without_proof": "separate asset",
    "identity_with_proof": "contributor of that native asset",
    "unpaired_remote": "reported SHIP state and no trusted data flow",
    "trusted_command_client": "Energy Guard client with the specification M/R/O",
}
WRONG = {
    "wh_to_joule": "1000 J",
    "percent_to_ratio": "50",
    "grid_consumption_positive": "stored negative consumption",
    "grid_production_negative": "stored positive production",
    "identity_without_proof": "joined asset",
    "identity_with_proof": "separate asset",
    "unpaired_remote": "trusted data flow",
    "trusted_command_client": "not taken",
}


def vector_outcomes(text: str) -> dict[str, str]:
    outcomes: dict[str, str] = {}
    for line in text.splitlines():
        if not line.startswith("| `"):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) < 4:
            continue
        outcomes[cells[0].strip("`")] = cells[3]
    return outcomes


def conforms(text: str) -> bool:
    outcomes = vector_outcomes(text)
    return all(outcomes.get(name) == value for name, value in EXPECTED.items())


class RemoteSourcesPageTests(unittest.TestCase):
    def test_page_has_the_required_sections_and_markers(self) -> None:
        text = " ".join(PAGE.read_text(encoding="utf-8").split())
        for section in SECTIONS:
            self.assertIn(section, text)
        for marker in repository_policy.ISSUE197_REMOTE_SOURCES_MARKERS:
            self.assertIn(marker, text)
        self.assertEqual(
            repository_policy.ISSUE197_REMOTE_SOURCES_REL.as_posix(),
            "api/_candidate/eebus-remote-sources-v1.md",
        )
        self.assertIn("eebus-remote-sources-v1.md", README.read_text(encoding="utf-8"))

    def test_unchanged_surfaces_name_the_three_pages(self) -> None:
        text = " ".join(PAGE.read_text(encoding="utf-8").split())
        for phrase in (
            "output pages",
            "normative source record",
            "inbound heating mapping",
        ):
            self.assertIn(phrase, text)
        self.assertNotIn("ledger", text)

    def test_vectors_match_the_conversion_sign_identity_and_trust_rules(self) -> None:
        self.assertEqual(vector_outcomes(PAGE.read_text(encoding="utf-8")), EXPECTED | {
            name: vector_outcomes(PAGE.read_text(encoding="utf-8"))[name]
            for name in vector_outcomes(PAGE.read_text(encoding="utf-8"))
            if name not in EXPECTED
        })
        self.assertTrue(conforms(PAGE.read_text(encoding="utf-8")))

    def test_each_vector_field_rejects_its_wrong_mutation(self) -> None:
        text = PAGE.read_text(encoding="utf-8")
        self.assertTrue(conforms(text))
        for name, wrong in WRONG.items():
            with self.subTest(vector=name, mutation=wrong):
                mutated = text.replace(f"| {EXPECTED[name]} |", f"| {wrong} |", 1)
                self.assertNotEqual(vector_outcomes(mutated).get(name), EXPECTED[name])
                self.assertFalse(conforms(mutated))


if __name__ == "__main__":
    unittest.main()
