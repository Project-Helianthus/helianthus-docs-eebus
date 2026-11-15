from __future__ import annotations

import re
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import validate_repository_policy as repository_policy  # noqa: E402

PAGE = ROOT / "api" / "_candidate" / "portal-participation-contract-v1.md"
PAGE_REL = Path("api/_candidate/portal-participation-contract-v1.md")
INVENTORY_REL = Path("architecture/_candidate/msp-085-live-r2-vr940-source-inventory.md")
SELECTION_RULE = (
    "`Selection` resolves to exactly one element of the common element catalog, "
    "with disposition `member`, on one canonical resource."
)
SELECTION_NEGATIVE = "A selection that names no common element is rejected, and the binding fails closed."
LOSS_TARGET_RULE = (
    "Every loss names its declared target, the target and version against which it was assessed."
)
LOSS_NEGATIVE = "A loss recorded without a target is rejected."
LOSS_MEMBERSHIP_RULE = (
    "Losses are target projection accounting and are distinct from plane membership: "
    "a loss never decides membership or catalog disposition and never serves as an internal disposition."
)
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

    def test_selection_resolves_to_a_common_element_on_a_canonical_resource(self) -> None:
        text = normalized()
        for phrase in (
            SELECTION_RULE,
            SELECTION_NEGATIVE,
            "| Selection | `selection` | reference; resolves to one common catalog element on one canonical resource (see [Selection and losses](#selection-and-losses)) |",
        ):
            self.assertIn(phrase, text)
        for stale in (
            "reference to the semantic producer's selected result",
            "The contract references that producer's selected result",
        ):
            self.assertNotIn(stale, text)

    def test_losses_name_a_declared_target_distinct_from_membership(self) -> None:
        text = normalized()
        for phrase in (LOSS_TARGET_RULE, LOSS_NEGATIVE, LOSS_MEMBERSHIP_RULE):
            self.assertIn(phrase, text)
        self.assertNotIn("A non-null `losses` list is the producer's explicit projection assessment", text)

    def test_negative_cases_are_exactly_the_two_rejections(self) -> None:
        source = PAGE.read_text(encoding="utf-8")
        section = source[source.index("### Negative cases") :]
        section = section[: section.index("\n## ")]
        rows = re.findall(r"^\| `([a-z_]+)` \| ([^|]+) \| ([^|]+) \|$", section, re.MULTILINE)
        self.assertEqual(
            [(case, given.strip(), outcome.strip()) for case, given, outcome in rows],
            [
                ("selection_without_common_element", "a selection that names no common element", "rejected; the binding fails closed"),
                ("loss_without_target", "a loss recorded without a target", "rejected"),
            ],
        )

    def test_cross_protocol_semantics_defer_to_the_common_contract(self) -> None:
        text = normalized()
        self.assertIn(
            "Cross-protocol semantics, including elements, resources and plane membership, "
            "are owned by the common semantic contract in docs-semantic.",
            text,
        )
        self.assertNotIn("Cross-protocol platform contracts stay in `helianthus-docs-ebus/docs/platform/`", text)
        self.assertIn("registry follow-up", text)

    def test_repository_policy_accepts_the_current_pages(self) -> None:
        self.assertEqual(repository_policy.issue_178_relation_and_participation_errors(ROOT), [])

    def test_repository_policy_rejects_each_dropped_rule(self) -> None:
        mutations = {
            "selection rule": (PAGE_REL, SELECTION_RULE, "`Selection` is an opaque reference."),
            "selection negative": (PAGE_REL, SELECTION_NEGATIVE, "An unresolved selection is kept."),
            "loss target": (PAGE_REL, LOSS_TARGET_RULE, "Every loss names a native path."),
            "loss negative": (PAGE_REL, LOSS_NEGATIVE, "A loss without a target is kept."),
            "loss membership": (PAGE_REL, LOSS_MEMBERSHIP_RULE, "Losses decide the disposition."),
            "slot label local": (INVENTORY_REL, "Slot labels are local to their bundle.", "Slot labels are global."),
            "slot label join": (
                INVENTORY_REL,
                "A slot label is never an identity, an anchor or an ordinal to join on.",
                "A slot label may be joined on.",
            ),
            "relations section": (INVENTORY_REL, "## Observed Relations", "## Relations"),
        }
        for name, (relative, old, new) in mutations.items():
            with self.subTest(mutation=name), tempfile.TemporaryDirectory() as temporary:
                copied = Path(temporary)
                for rel in (PAGE_REL, INVENTORY_REL):
                    (copied / rel).parent.mkdir(parents=True, exist_ok=True)
                    content = " ".join((ROOT / rel).read_text(encoding="utf-8").split())
                    if rel == relative:
                        self.assertIn(old, content)
                        content = content.replace(old, new)
                    (copied / rel).write_text(content, encoding="utf-8")
                errors = repository_policy.issue_178_relation_and_participation_errors(copied)
            self.assertTrue(any(str(relative) in error for error in errors), (name, errors))

    def test_repository_policy_rejects_a_stale_owner_or_opaque_selection(self) -> None:
        for stale in (
            "reference to the semantic producer's selected result",
            "Cross-protocol platform contracts stay in `helianthus-docs-ebus/docs/platform/`",
        ):
            with self.subTest(stale=stale), tempfile.TemporaryDirectory() as temporary:
                copied = Path(temporary)
                for rel in (PAGE_REL, INVENTORY_REL):
                    (copied / rel).parent.mkdir(parents=True, exist_ok=True)
                    (copied / rel).write_text((ROOT / rel).read_text(encoding="utf-8"), encoding="utf-8")
                page = copied / PAGE_REL
                page.write_text(page.read_text(encoding="utf-8") + "\n" + stale + "\n", encoding="utf-8")
                errors = repository_policy.issue_178_relation_and_participation_errors(copied)
            self.assertTrue(any("stale" in error for error in errors), errors)


if __name__ == "__main__":
    unittest.main()
