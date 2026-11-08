"""Keep frozen publication navigation distinct from the evolving source branch."""

from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
CURRENT_SOURCE = "https://github.com/Project-Helianthus/helianthus-eebusreg/tree/main"
NAVIGATION = {
    "README.md": {
        "Frozen eeBUS Runtime API v1 reference": "api/eebusruntime-v1/reference.md",
        "Current eeBUS runtime implementation": CURRENT_SOURCE,
    },
    "api/README.md": {
        "Frozen eeBUS Runtime API v1 reference": "eebusruntime-v1/reference.md",
        "Current eeBUS runtime implementation": CURRENT_SOURCE,
        "publication record": "eebusruntime-v1/publication-record.json",
        "frozen manifest": "eebusruntime-v1/manifest.json",
    },
}


class RuntimeReferenceStatusTests(unittest.TestCase):
    def assert_navigation(self, page, text):
        links = [
            (" ".join(label.split()), target)
            for label, target in re.findall(r"\[([^\]]+)\]\(([^)]+)\)", text)
        ]
        for label, target in NAVIGATION[page].items():
            self.assertEqual([href for name, href in links if name == label], [target])
            if not target.startswith("https://"):
                self.assertTrue((ROOT / page).parent.joinpath(target).is_file())

    def test_navigation_distinguishes_frozen_reference_and_current_source(self):
        for page in NAVIGATION:
            self.assert_navigation(page, (ROOT / page).read_text(encoding="utf-8"))

    def test_status_explains_publication_binding_and_known_divergence(self):
        text = " ".join((ROOT / "api/README.md").read_text(encoding="utf-8").split())
        for fact in (
            "source revision identified by its adjacent",
            "278 declarations",
            "not a live mirror",
            "has moved beyond that published pin",
            "MutationLabProfiles []eebusraw.MutationLabProfileV1",
            "RawFeatureRuntimeV1",
            "not an exhaustive current export inventory",
        ):
            with self.subTest(fact=fact):
                self.assertIn(fact, text)

    def test_each_navigation_label_and_target_is_enforced(self):
        # Vary both fields of every link identity on both navigation pages.
        for page, entries in NAVIGATION.items():
            text = (ROOT / page).read_text(encoding="utf-8")
            for label, target in entries.items():
                original = f"[{label}]({target})"
                self.assertIn(original, text)
                for field, replacement in (
                    ("label", f"[Unspecified API]({target})"),
                    ("target", f"[{label}](missing-reference.md)"),
                ):
                    with self.subTest(page=page, label=label, field=field):
                        mutated = text.replace(original, replacement)
                        links = re.findall(r"\[([^\]]+)\]\(([^)]+)\)", mutated)
                        self.assertNotIn((label, target), links)
                        with self.assertRaises(AssertionError):
                            self.assert_navigation(page, mutated)



if __name__ == "__main__":
    unittest.main()
