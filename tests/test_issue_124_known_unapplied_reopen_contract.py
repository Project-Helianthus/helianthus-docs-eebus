from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARCH = ROOT / "architecture/_candidate/msp-052-outbound-pairing-contract.md"
API = ROOT / "api/_candidate/post-m9-operator-admin-v1.md"
PAIRING_API = ROOT / "api/_candidate/msp-052-outbound-pairing-api.md"
PAIRING_BROWSER = ROOT / "architecture/_candidate/post-m9-operator-pairing-browsers-v1.md"


def normalized(path: Path) -> str:
    return " ".join(path.read_text(encoding="utf-8").split())


class KnownUnappliedAttemptReopenContractTest(unittest.TestCase):
    def test_exact_previous_selected_target_absent_is_reconciled_at_reopen(self) -> None:
        text = normalized(ARCH) + " " + normalized(API) + " " + normalized(PAIRING_API)
        for phrase in (
            "`attempt_prepare`",
            "`exact_previous_selected_and_target_absent`",
            "protected-anchor compare-and-clear",
            "before listener or discovery startup",
            "unchanged selected store",
            "normal recovery classification",
        ):
            self.assertIn(phrase, text)

    def test_ambiguous_or_applied_publication_remains_fail_closed(self) -> None:
        text = normalized(ARCH) + " " + normalized(API) + " " + normalized(PAIRING_API)
        for phrase in (
            "exact target selected",
            "ambiguous observation",
            "descriptor mismatch",
            "compare-and-clear failure",
            "`DURABILITY_UNKNOWN`",
            "cannot start transport effects",
        ):
            self.assertIn(phrase, text)

    def test_reconciliation_does_not_create_outbound_authority(self) -> None:
        text = normalized(ARCH) + " " + normalized(API) + " " + normalized(PAIRING_API)
        for phrase in (
            "does not synthesize failure",
            "does not launch an automatic outbound attempt",
            "`AdminV1.RetryTrusted`",
            "one retry",
        ):
            self.assertIn(phrase, text)

    def test_all_normative_surfaces_define_the_same_exception(self) -> None:
        for path in (ARCH, API, PAIRING_API):
            text = normalized(path)
            for phrase in (
                "`attempt_prepare`",
                "`exact_previous_selected_and_target_absent`",
                "compare-and-clear",
                "terminal durable release-retry receipt",
                "`DURABILITY_UNKNOWN`",
                "does not launch an automatic outbound attempt",
            ):
                self.assertIn(phrase, text, path)

        browser = normalized(PAIRING_BROWSER)
        for phrase in (
            "`RETRY_READY` / `RETRYABLE_FAILURE`",
            "one usable current-lineage durable association",
            "one terminal durable release-retry receipt",
            "does not launch an automatic outbound attempt",
            "cannot start transport effects",
        ):
            self.assertIn(phrase, browser, PAIRING_BROWSER)

        self.assertNotIn(
            "successful-retirement durability-unknown case below is the sole exception",
            normalized(ARCH).lower(),
        )


if __name__ == "__main__":
    unittest.main()
