from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
CANDIDATE = ROOT / "api/_candidate/raw-snapshot-view-v1.md"
CANDIDATE_REL = "api/_candidate/raw-snapshot-view-v1.md"
sys.path.insert(0, str(ROOT / "scripts"))

from validate_repository_policy import _contains_visible_candidate_destination


def read_candidate() -> tuple[dict[str, str], str]:
    text = CANDIDATE.read_text(encoding="utf-8")
    _, front_matter, body = text.split("---", 2)
    return yaml.safe_load(front_matter), body


def markdown_table(body: str, heading: str) -> dict[str, list[str]]:
    section = body.split(heading, 1)[1]
    rows: dict[str, list[str]] = {}
    in_table = False
    for line in section.splitlines():
        if line.startswith("| ---"):
            in_table = True
            continue
        if in_table and not line.startswith("|"):
            break
        if not in_table or not line.startswith("| `"):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        key = cells[0].strip("`")
        rows[key] = re.findall(r"`([^`]+)`", cells[1])
    return rows


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
            text = (ROOT / relative).read_text(encoding="utf-8")
            self.assertNotIn(CANDIDATE_REL, text)
            self.assertFalse(_contains_visible_candidate_destination(text, relative))
            self.assertNotIn("Candidate Immutable Raw Snapshot/View v1", text)

        registry = yaml.safe_load(
            (ROOT / "scripts/publication_channels.yaml").read_text(encoding="utf-8")
        )
        for specification in registry["channels"].values():
            self.assertNotIn(CANDIDATE_REL, specification["members"])

    def test_candidate_locks_the_versioned_raw_value_inventory(self) -> None:
        _, body = read_candidate()
        expected_types = {
            "SnapshotV1": ["Meta", "Status", "Pairing", "Services", "Sessions", "Topology", "Raw"],
            "SnapshotMetaV1": ["Contract", "Runtime", "LocalSKI", "MaskTier", "CapturedAt", "DataTimestamp", "DataHash"],
            "RuntimeObservationV1": ["State", "Degradation"],
            "DegradationV1": ["Reason", "Since"],
            "PairingObservationV1": ["Remote", "State", "Since", "Raw", "Unknown"],
            "ServiceV1": ["ID", "Kind", "Visible", "Paired", "Raw", "Unknown"],
            "SessionV1": ["ID", "Remote", "State", "Since", "Raw", "Unknown"],
            "TopologyV1": ["Devices"],
            "DeviceV1": ["ID", "Entities", "UseCaseClaims", "Raw", "Unknown"],
            "EntityV1": ["ID", "Features", "Raw", "Unknown"],
            "FeatureV1": ["ID", "Role", "Raw", "Unknown"],
            "UseCaseClaimV1": ["ID", "Raw", "Unknown"],
        }
        self.assertEqual(markdown_table(body, "## Candidate Type Inventory"), expected_types)

        expected_enums = {
            "SnapshotContractV1": ["helianthus.eebus.runtime.raw-snapshot.v1"],
            "ObservedRuntimeStateV1": ["unknown", "stopped", "starting", "ready", "degraded", "shutdown"],
            "DegradationReasonV1": ["missing-discovery", "denied-trust", "remote-disconnect", "certificate-unavailable", "no-visible-services", "no-data"],
            "ServiceKindV1": ["local", "remote"],
            "ObservedSessionStateV1": ["unknown", "connecting", "connected", "disconnected", "degraded"],
            "FeatureRoleV1": ["\"\"", "client", "server"],
        }
        enum_rows = markdown_table(body, "The exact closed candidate enum inventory is:")
        self.assertEqual(enum_rows, expected_enums)

        expected_operations = {
            "NewSnapshotV1",
            "Validate",
            "Clone",
            "ComputeDataHash",
            "MarshalJSON",
            "String",
            "GoString",
            "Format",
        }
        self.assertEqual(
            set(markdown_table(body, "## Allowed Operations")), expected_operations
        )
        self.assertIn("helianthus.eebus.runtime.raw-snapshot.v1", body)
        self.assertIn("eebusraw.RedactedID", body)
        self.assertIn("eebusevidence.ObjectV1", body)

    def test_candidate_forbids_premature_authority_surfaces(self) -> None:
        _, body = read_candidate()
        normalized = " ".join(body.split())
        forbidden_types = {
            "Runtime",
            "RuntimeV1",
            "View",
            "ViewV1",
            "SnapshotSource",
            "Store",
            "CaptureRef",
            "ViewResult",
        }
        forbidden_operations = {
            "Start",
            "Shutdown",
            "Snapshot",
            "PairingState",
            "RegisterRemoteSKI",
            "UnregisterRemoteSKI",
            "SetPairingWindow",
            "UpdateSnapshot",
            "Capture",
            "Drop",
            "CapturedSnapshot",
            "Dereference",
        }
        forbidden_section = body.split("## Forbidden Public Inventory", 1)[1].split(
            "\n## ", 1
        )[0]
        normalized_forbidden = " ".join(forbidden_section.split())
        type_text, operation_text = normalized_forbidden.split(
            "It also forbids public", 1
        )
        self.assertEqual(set(re.findall(r"`([^`]+)`", type_text)), forbidden_types)
        self.assertEqual(
            set(re.findall(r"`([^`]+)`", operation_text)), forbidden_operations
        )

        required_boundaries = (
            "no semantic device ID",
            "no public `Runtime`",
            "No public declaration may depend on an `enbility/eebus-go` type",
            "snapshot detachment and defensive-copy behavior",
            "only `captured_at` and `data_hash` are omitted",
            "`Validate` recomputes every non-empty `data_hash` and rejects a mismatch",
        )
        for boundary in required_boundaries:
            self.assertIn(boundary, normalized)


if __name__ == "__main__":
    unittest.main()
