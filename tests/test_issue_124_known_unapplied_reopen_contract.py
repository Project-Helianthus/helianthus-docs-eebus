from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARCH = ROOT / "architecture/_candidate/msp-052-outbound-pairing-contract.md"
API = ROOT / "api/_candidate/post-m9-operator-admin-v1.md"


def normalized(path: Path) -> str:
    return " ".join(path.read_text(encoding="utf-8").split())


class KnownUnappliedAttemptReopenContractTest(unittest.TestCase):
    def test_exact_previous_selected_target_absent_is_reconciled_at_reopen(self) -> None:
        text = normalized(ARCH) + " " + normalized(API)
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
        text = normalized(ARCH) + " " + normalized(API)
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
        text = normalized(ARCH) + " " + normalized(API)
        for phrase in (
            "does not synthesize failure",
            "does not launch an automatic outbound attempt",
            "`AdminV1.RetryTrusted`",
            "one retry",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
