from __future__ import annotations

import json
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "architecture" / "multi-runtime-coexistence.md"
PLATFORM_COMMIT = "9cede4c61a4f73019142b7418cf6f875" "37cf645c"
PLATFORM_PATH = "docs/platform/multi-runtime-coexistence-no-drift-v1.md"


def front_matter(text: str) -> dict[str, str]:
    if not text.startswith("---\n"):
        raise AssertionError("page is missing YAML front matter")
    end = text.index("\n---\n", 4)
    metadata = yaml.safe_load(text[4:end])
    if not isinstance(metadata, dict):
        raise AssertionError("front matter must be a mapping")
    return metadata


class Issue102M8CoexistenceCrossSeedTests(unittest.TestCase):
    def test_active_page_points_to_exact_canonical_contract(self) -> None:
        text = PAGE.read_text(encoding="utf-8")
        metadata = front_matter(text)

        self.assertEqual(metadata["publication_status"], "active")
        self.assertEqual(metadata["cross_seed_mode"], "summary-only")
        self.assertEqual(
            metadata["cross_seed_target"],
            f"Project-Helianthus/helianthus-docs-ebus:{PLATFORM_PATH}",
        )
        self.assertEqual(
            metadata["cross_seed_snapshot"],
            "Project-Helianthus/helianthus-docs-ebus@"
            f"{PLATFORM_COMMIT}:{PLATFORM_PATH}",
        )
        self.assertIn(
            "https://github.com/Project-Helianthus/helianthus-docs-ebus/blob/"
            f"{PLATFORM_COMMIT}/{PLATFORM_PATH}",
            text,
        )

    def test_page_records_m8_scope_without_consumer_promotion(self) -> None:
        body = " ".join(PAGE.read_text(encoding="utf-8").split())

        for expected in (
            "separate raw surfaces",
            "promoted eBUS leaves remain authoritative",
            "eeBUS candidate and conflict facts stay in raw/debug evidence",
            "no eBUS consumer drift",
            "does not authorize M8.5 or M9",
        ):
            self.assertIn(expected, body)

    def test_page_is_in_snapshot_and_every_stable_channel(self) -> None:
        snapshot = yaml.safe_load(
            (ROOT / "scripts" / "platform_cross_seed_snapshot.yaml").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(snapshot["commit"], PLATFORM_COMMIT)
        self.assertIn(PLATFORM_PATH, [target["path"] for target in snapshot["targets"]])

        channels = yaml.safe_load(
            (ROOT / "scripts" / "publication_channels.yaml").read_text(
                encoding="utf-8"
            )
        )
        for channel in ("search", "sitemap", "versioned_bundle", "release_bundle"):
            self.assertIn(
                "architecture/multi-runtime-coexistence.md",
                channels["channels"][channel]["members"],
            )

        search_index = json.loads(
            (ROOT / "api" / "search-index.json").read_text(encoding="utf-8")
        )
        self.assertIn("architecture/multi-runtime-coexistence.md", search_index["pages"])


if __name__ == "__main__":
    unittest.main()
