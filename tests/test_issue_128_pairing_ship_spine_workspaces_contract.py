import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARCH = ROOT / "architecture/_candidate/post-m9-operator-pairing-browsers-v1.md"
API = ROOT / "api/_candidate/post-m9-operator-admin-v1.md"


def normalized(path: Path) -> str:
    return " ".join(path.read_text(encoding="utf-8").split())


class PairingShipSpineWorkspaceContractTests(unittest.TestCase):
    def test_three_workspaces_have_disjoint_authority(self) -> None:
        arch = normalized(ARCH)
        for phrase in (
            "exactly three nested workspaces: `Pairing`, `SHIP`, and `SPINE`",
            "Pairing owns every first-trust mutation",
            "SHIP owns durable trust and live-session inspection",
            "SPINE is read-only and issues only `GET` requests",
            "Browse SPINE never retries, connects, selects, confirms, or otherwise starts transport",
        ):
            self.assertIn(phrase, arch)

    def test_trusted_offline_is_not_browseable(self) -> None:
        arch = normalized(ARCH)
        api = normalized(API)
        for document in (arch, api):
            self.assertIn("trusted-but-offline", document)
            self.assertIn("`disconnected`", document)
            self.assertIn("`spine_topology_unavailable`", document)
            self.assertIn("`admin_boundary_unavailable`", document)
        self.assertIn("Only a capability issued by the current `connected` view can open a SPINE root", api)
        self.assertIn("must not read the raw snapshot provider", api)
        self.assertIn("raw provider returned a valid snapshot, but it contains no matching current-partner device inventory", arch)
        self.assertIn("An unavailable or invalid raw-provider result is `admin_boundary_unavailable`", arch)

    def test_workspace_lifetimes_remain_fail_closed(self) -> None:
        arch = normalized(ARCH)
        for phrase in (
            "Leaving Pairing clears selection, candidate, OOB input, and Pairing-scoped pending state",
            "leaving SHIP clears armed untrust state",
            "leaving SPINE clears partner, snapshot, cursors, and every rendered raw node",
            "does not place SKI, endpoint, partner capability, snapshot identifier, or cursor in URL or browser history",
        ):
            self.assertIn(phrase, arch)


if __name__ == "__main__":
    unittest.main()
