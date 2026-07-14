from __future__ import annotations

import re
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
CANDIDATE = ROOT / "api/_candidate/raw-snapshot-view-v1.md"
CANDIDATE_REL = "api/_candidate/raw-snapshot-view-v1.md"


def read_candidate() -> tuple[dict[str, str], str]:
    text = CANDIDATE.read_text(encoding="utf-8")
    _, front_matter, body = text.split("---", 2)
    return yaml.safe_load(front_matter), body


class MSP036RawViewContractTest(unittest.TestCase):
    def test_candidate_is_hidden_from_every_stable_channel(self) -> None:
        metadata, _ = read_candidate()
        self.assertEqual(metadata["publication_status"], "candidate")
        self.assertEqual(metadata["candidate_output"], "true")
        self.assertEqual(metadata["candidate_output_path"], CANDIDATE_REL)
        for channel in (
            "stable_navigation",
            "search",
            "sitemap",
            "versioned_bundle",
            "release_bundle",
        ):
            self.assertEqual(metadata[channel], "false")

        for relative in (
            "README.md",
            "api/README.md",
            "api/search-index.json",
            "api/sitemap.xml",
            "api/versioned-bundle.txt",
            "api/release-bundle.txt",
        ):
            self.assertNotIn(CANDIDATE_REL, (ROOT / relative).read_text(encoding="utf-8"))

    def test_candidate_locks_the_versioned_raw_value_inventory(self) -> None:
        _, body = read_candidate()
        required = {
            "SnapshotV1",
            "SnapshotMetaV1",
            "RuntimeObservationV1",
            "DegradationV1",
            "PairingObservationV1",
            "ServiceV1",
            "SessionV1",
            "TopologyV1",
            "DeviceV1",
            "EntityV1",
            "FeatureV1",
            "UseCaseClaimV1",
            "NewSnapshotV1",
            "ComputeDataHash",
        }
        missing = sorted(symbol for symbol in required if f"`{symbol}`" not in body)
        self.assertEqual(missing, [])
        self.assertIn("helianthus.eebus.runtime.raw-snapshot.v1", body)
        self.assertIn("eebusraw.RedactedID", body)
        self.assertIn("eebusevidence.ObjectV1", body)

    def test_candidate_forbids_premature_authority_surfaces(self) -> None:
        _, body = read_candidate()
        normalized = " ".join(body.split())
        for signature in (
            r"`Start\s*\(",
            r"`Shutdown\s*\(",
            r"`RegisterRemoteSKI\s*\(",
            r"`UnregisterRemoteSKI\s*\(",
            r"`SetPairingWindow\s*\(",
        ):
            self.assertIsNone(re.search(signature, body))

        required_boundaries = (
            "no semantic device ID",
            "no public `Runtime`",
            "No public declaration may depend on an `enbility/eebus-go` type",
            "snapshot detachment and defensive-copy behavior",
            "with `data_hash` itself omitted",
        )
        for boundary in required_boundaries:
            self.assertIn(boundary, normalized)


if __name__ == "__main__":
    unittest.main()
