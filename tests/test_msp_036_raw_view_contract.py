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
            "SnapshotV1": ["Meta", "Status", "Pairing", "Services", "Sessions", "Devices", "Entities", "Features", "UseCases", "Opaque"],
            "RedactedSnapshotV1": ["Meta", "Status", "Pairing", "Services", "Sessions", "Devices", "Entities", "Features", "UseCases"],
            "SnapshotMetaV1": ["Contract", "Runtime", "LocalSKI", "MaskTier", "CapturedAt", "DataTimestamp", "DataHash"],
            "RedactedSnapshotMetaV1": ["Contract", "Runtime", "LocalSKI", "MaskTier", "CapturedAt", "DataTimestamp", "DataHash"],
            "RuntimeObservationV1": ["State", "Degradation"],
            "DegradationV1": ["Reason", "Since"],
            "PairingObservationV1": ["RemoteSKI", "State", "Since", "Opaque"],
            "ServiceV1": ["SKI", "SHIPID", "Kind", "Visible", "Paired", "Name", "Identifier", "Brand", "Type", "Model", "SecondaryDigest", "Opaque"],
            "SessionV1": ["ID", "RemoteSKI", "State", "Since", "Opaque"],
            "DeviceV1": ["SKI", "SHIPID", "Address", "Type", "Description", "Metadata", "SecondaryDigest", "Opaque"],
            "EntityV1": ["DeviceAddress", "EntityAddress", "Type", "Description", "SecondaryDigest", "Opaque"],
            "FeatureV1": ["DeviceAddress", "EntityAddress", "FeatureAddress", "Type", "Role", "Description", "SecondaryDigest", "Opaque"],
            "UseCaseV1": ["ContextAddress", "Name", "Actor", "ResolvedRole", "Scenarios", "Version", "Availability", "DocumentSubrevision", "SecondaryDigest", "Opaque"],
            "OpaqueObservationV1": ["Path", "Source", "Value"],
            "OpaqueValueV1": ["Scalar", "Array", "Object"],
            "OpaqueScalarV1": ["Null", "Boolean", "Integer", "String"],
            "MetadataV1": ["Values"],
            "MetadataValueV1": ["Null", "Boolean", "Integer", "String"],
            "RedactedServiceV1": ["ID", "Kind", "Visible", "Paired"],
            "RedactedSessionV1": ["ID", "Remote", "State", "Since"],
            "RedactedDeviceV1": ["ID", "Entities", "UseCaseClaims"],
            "RedactedEntityV1": ["ID", "Features"],
            "RedactedFeatureV1": ["ID", "Role"],
            "RedactedUseCaseV1": ["ID"],
        }
        self.assertEqual(markdown_table(body, "## Candidate Type Inventory"), expected_types)

        expected_field_types = {
            "SnapshotMetaV1.LocalSKI": ["string"],
            "RedactedSnapshotMetaV1.LocalSKI": ["RedactedID"],
            "ServiceV1.SKI": ["string"],
            "ServiceV1.SHIPID": ["*string"],
            "ServiceV1.Kind": ["ServiceKindV1"],
            "ServiceV1.Visible": ["bool"],
            "ServiceV1.Paired": ["bool"],
            "ServiceV1.Name": ["string"],
            "ServiceV1.Identifier": ["string"],
            "ServiceV1.Brand": ["string"],
            "ServiceV1.Type": ["string"],
            "ServiceV1.Model": ["string"],
            "ServiceV1.SecondaryDigest": ["*string"],
            "ServiceV1.Opaque": ["*[]OpaqueObservationV1"],
            "DeviceV1.SKI": ["string"],
            "DeviceV1.SHIPID": ["*string"],
            "DeviceV1.Address": ["string"],
            "DeviceV1.Type": ["string"],
            "DeviceV1.Description": ["*string"],
            "DeviceV1.Metadata": ["*MetadataV1"],
            "DeviceV1.SecondaryDigest": ["*string"],
            "DeviceV1.Opaque": ["*[]OpaqueObservationV1"],
            "EntityV1.DeviceAddress": ["string"],
            "EntityV1.EntityAddress": ["string"],
            "EntityV1.Type": ["string"],
            "EntityV1.Description": ["*string"],
            "EntityV1.SecondaryDigest": ["*string"],
            "EntityV1.Opaque": ["*[]OpaqueObservationV1"],
            "FeatureV1.DeviceAddress": ["string"],
            "FeatureV1.EntityAddress": ["string"],
            "FeatureV1.FeatureAddress": ["string"],
            "FeatureV1.Type": ["string"],
            "FeatureV1.Role": ["string"],
            "FeatureV1.Description": ["*string"],
            "FeatureV1.SecondaryDigest": ["*string"],
            "FeatureV1.Opaque": ["*[]OpaqueObservationV1"],
            "UseCaseV1.ContextAddress": ["string"],
            "UseCaseV1.Name": ["string"],
            "UseCaseV1.Actor": ["string"],
            "UseCaseV1.ResolvedRole": ["*string"],
            "UseCaseV1.Scenarios": ["*[]string"],
            "UseCaseV1.Version": ["*string"],
            "UseCaseV1.Availability": ["*bool"],
            "UseCaseV1.DocumentSubrevision": ["*string"],
            "UseCaseV1.SecondaryDigest": ["*string"],
            "UseCaseV1.Opaque": ["*[]OpaqueObservationV1"],
            "OpaqueObservationV1.Path": ["string"],
            "OpaqueObservationV1.Source": ["string"],
            "OpaqueObservationV1.Value": ["OpaqueValueV1"],
            "MetadataV1.Values": ["map[string]MetadataValueV1"],
        }
        self.assertEqual(
            markdown_table(body, "## Candidate Field Value Types"),
            expected_field_types,
        )
        self.assertEqual(
            markdown_table(body, "## Redacted Builder Inventory"),
            {"BuildRedactedSnapshotV1": ["SnapshotV1"]},
        )

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
        self.assertNotIn("eebusraw.RedactedID", body)
        self.assertNotIn("eebusevidence.ObjectV1", body)
        self.assertNotIn("eebusraw.UnknownField", body)

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
        mentioned_operations = set(re.findall(r"`([^`]+)`", operation_text))
        self.assertIn("PairingState", mentioned_operations)
        mentioned_operations.remove("PairingState")
        self.assertEqual(mentioned_operations, forbidden_operations)

        required_boundaries = (
            "no semantic device ID",
            "no public `Runtime`",
            "No public declaration may depend on an `enbility/eebus-go` type",
            "snapshot detachment and defensive-copy behavior",
            "only `captured_at` and `data_hash` are omitted",
            "`Validate` recomputes every non-empty `data_hash` and rejects a mismatch",
            "existing read-only `PairingState` API remains unchanged",
            "`OpaqueValueV1` accepts scalars and nested JSON arrays/objects",
            "present empty string, array, object, or false boolean remains an observed value",
        )
        for boundary in required_boundaries:
            self.assertIn(boundary, normalized)


if __name__ == "__main__":
    unittest.main()
