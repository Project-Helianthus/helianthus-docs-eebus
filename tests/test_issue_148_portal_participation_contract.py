from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "api" / "_candidate" / "portal-participation-contract-v1.md"
PINNED_COMMIT = "faa883237aedad306da0" "00a495af44a10d7248ce"


def normalized() -> str:
    return " ".join(PAGE.read_text(encoding="utf-8").split())


class PortalParticipationContractTest(unittest.TestCase):
    def test_page_is_candidate_only_and_pins_the_exact_source(self) -> None:
        text = normalized()
        for phrase in (
            'publication_status: "candidate"',
            'stable_navigation: "false"',
            'search: "false"',
            'sitemap: "false"',
            'versioned_bundle: "false"',
            'release_bundle: "false"',
            f"helianthus-eebusreg@{PINNED_COMMIT}:participation_contract_v1.go",
            f"helianthus-eebusreg@{PINNED_COMMIT}:participation_driver_v1.go",
        ):
            self.assertIn(phrase, text)

    def test_saved_applied_observed_split_and_control_eligibility(self) -> None:
        text = normalized()
        for phrase in (
            "Saved intent.",
            "Applied configuration.",
            "Observed state.",
            "exactly one entry for every binding ID in the union of saved and applied bindings",
            "Saved-only bindings are inert.",
            "Grants validated against applied permissions.",
            "the saved intent is enabled",
            "still present in the saved intent (still selected)",
            "the saved binding carries the `control` permission",
            "the selected peer controls the bound local capability",
        ):
            self.assertIn(phrase, text)

    def test_reviewer_flagged_semantics_and_boundaries_are_explicit(self) -> None:
        text = normalized()
        for phrase in (
            "Reuse of a removed binding ID for a different target is invalid for the owner",
            "**fails closed**",
            "no representation of a partially applied revision",
            "Working interpretation (to be confirmed",
            "**Meaning of an older applied snapshot.**",
            "in-process contract",
            "no wire shape and no persistence format",
            "makes no runtime, deployment, interoperability or device claim",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
