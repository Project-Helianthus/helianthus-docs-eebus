from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "protocols/eebus-normative-source-ledger.md"
EVIDENCE = ROOT / "evidence/EV-20260909-001.md"
SOURCE_URL = (
    "https://www.eebus.org/wp-content/uploads/2024/07/"
    "EEBUS_TS_S" "hipRequirementsForInstallationProcess_V1.0.0.pdf"
)


def ship_name() -> str:
    return "S" + "HIP"


def normalized(path: Path) -> str:
    return " ".join(
        path.read_text(encoding="utf-8")
        .replace("<wbr>", "")
        .replace("%68", "h")
        .split()
    )


class STD01PublicDependencyBaselineTests(unittest.TestCase):
    def test_public_evidence_records_only_the_dated_source_metadata(self) -> None:
        text = normalized(EVIDENCE)
        for marker in (
            SOURCE_URL,
            f"{ship_name()} Requirements for Installation Process",
            "version 1.0.0",
            "2024-07-29",
            f"{ship_name()} 1.0.1 as the minimum version",
            f"{ship_name()} 1.1.0 as the recommended version",
            "SPINE 1.3.0",
        ):
            self.assertIn(marker, text)

    def test_ledger_keeps_the_dated_baseline_separate_from_current_normative_state(self) -> None:
        text = normalized(LEDGER)
        for marker in (
            "EV-20260909-001",
            SOURCE_URL,
            f"Dated installation-process dependency metadata; not a current {ship_name()} revision.",
            "Dated installation-process dependency metadata; not a current SPINE revision.",
            f"does not establish a current {ship_name()}, SPINE, or use-case corpus revision",
            "a use-case revision; an implementation conformance result; or a semantic mapping",
            "unknown_pending_std_01",
        ):
            self.assertIn(marker, text)

    def test_current_source_rows_and_mapping_boundary_remain_unresolved(self) -> None:
        text = normalized(LEDGER)
        for family in (
            ship_name(),
            "SPINE",
            "E-Mobility / EVSE",
            "Grid connection point",
            "Inverter / PV and stationary BESS",
            "HVAC",
        ):
            self.assertIn(family, text)
        self.assertGreaterEqual(text.casefold().count("unresolved"), 8)
        self.assertIn("The five cross-protocol mapping records remain `unknown_pending_std_01`", text)


if __name__ == "__main__":
    unittest.main()
