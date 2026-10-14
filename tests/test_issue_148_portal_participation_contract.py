from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "api" / "_candidate" / "portal-participation-contract-v1.md"
PINNED_COMMIT = "a9af3ac6387abada81e9" "5972bdc9639de5aeaee0"


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

    def test_promotion_decision_keeps_the_page_candidate_with_reasons(self) -> None:
        text = normalized()
        for phrase in (
            "## Promotion decision",
            "Decision: **remain candidate**.",
            'hypothesis_status: "draft"',
            "reviewed supported-API claim registry",
            "squash-merge commit of pull request 138",
            "have the same Git blob identity at the merge commit",
        ):
            self.assertIn(phrase, text)
        self.assertNotIn("candidate pin to a pull-request head", text)
        self.assertNotIn("faa883237aedad306da0", text)

    def test_saved_applied_observed_split_and_grant_ceiling(self) -> None:
        text = normalized()
        for phrase in (
            "Saved intent.",
            "Applied configuration.",
            "Observed state.",
            "The observation list must contain exactly one entry for every binding ID in the union of saved and applied bindings",
            "An observation of a binding that is not applied cannot report a grant, native negotiation or the `active` state.",
            "Every native grant must be a subset of the permissions of the binding as applied (or, for saved-only bindings, none).",
            "it does not restore control eligibility",
            "The applied revision may never exceed the saved revision.",
            "If both revisions are equal the two configurations must be equal",
        ):
            self.assertIn(phrase, text)

    def test_control_prerequisites_and_receive_direction(self) -> None:
        text = normalized()
        for phrase in (
            "Control is eligible for a binding only when all of these hold: 1. the whole contribution validates; 2. the saved intent is enabled; "
            "3. the same binding ID is still present in the saved intent (still selected) with the same target as the operating binding; "
            "4. the saved binding carries the `control` permission; "
            "5. the observation is `active` and holds a native `control` grant; and "
            "6. no loss on that observation has `control_safe` false.",
            "Saved removal, revocation or disable therefore rejects control even while the older applied binding is truthfully observed as active.",
            "Control is never inferred from observation permission, a functional mapping or peer trust.",
            "On a `send` binding, the local participant may control the selected peer capability.",
            "On a **`receive` binding, the selected peer controls the bound local capability.**",
            "A receive grant does not authorize Portal to issue control to that peer.",
        ):
            self.assertIn(phrase, text)

    def test_reviewer_flagged_semantics_and_boundaries_are_explicit(self) -> None:
        text = normalized()
        for phrase in (
            "Reuse of a removed binding ID for a different target is invalid for the owner",
            "the contribution validator rejects the **whole** contribution",
            "**fails closed**",
            "cannot detect reuse across a removal",
            "means the saved revision has **not been applied**",
            "v1 has **no representation of a partially applied revision**",
            "Working interpretation (to be confirmed",
            "**Meaning of an older applied snapshot.**",
            "in-process contract",
            "no wire shape and no persistence format",
            "makes no runtime, deployment, interoperability or device claim",
        ):
            self.assertIn(phrase, text)

    def test_validator_constraints_are_manifested_and_reset_is_not_a_rule(self) -> None:
        text = normalized()
        for phrase in (
            "**`incompatible` exists in the enum but is rejected here**",
            "unlike the listener state, `incompatible` is accepted here",
            "not `none` exactly when the state is `error`",
            "nonzero when `state` is `active`",
            "at most 256 characters",
            "**Consequence of an identity reset.**",
            "unverified hypothesis, not a contract rule",
        ):
            self.assertIn(phrase, text)
        self.assertNotIn("a reset leaves no valid contribution", text)


if __name__ == "__main__":
    unittest.main()
