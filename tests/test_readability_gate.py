"""Synthetic contracts for the offline readability ratchet."""

import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "readability", ROOT / "scripts/check_readability.py")
GATE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(GATE)


def baseline_document(entries):
    return dict(schema=1, ruff_version=GATE.RUFF_VERSION,
                generation="Measured synthetic fixtures", entries=entries)


def complex_source(branches):
    return "def inspect_value(value):\n" + "".join(
        f"    if value == {index}:\n        return {index}\n"
        for index in range(branches)) + "    return None\n"


class ReadabilityGateTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        (self.root / "scripts").mkdir()
        (self.root / "tests").mkdir()
        (self.root / "ruff.toml").write_text(
            (ROOT / "ruff.toml").read_text(encoding="utf-8"), encoding="utf-8")
        self.source = self.root / "scripts/sample.py"

    def findings(self, source):
        self.source.write_text(source, encoding="utf-8")
        return GATE.run_ruff(self.root)

    def test_clean_source_has_no_debt(self):
        self.assertEqual(self.findings("def read_value():\n    return 1\n"), {})
        self.assertEqual(GATE.compare_findings({}, {}), [])

    def test_docs_fast_runs_readability_with_hash_pinned_ruff(self):
        script = (ROOT / "scripts/ci_docs_fast.sh").read_text(encoding="utf-8")
        self.assertIn("python3 scripts/check_readability.py --self-test", script)
        self.assertIn("python3 scripts/check_readability.py --check", script)
        requirements = (ROOT / "requirements-ci.txt").read_text(encoding="utf-8")
        self.assertRegex(
            requirements, r"(?m)^ruff==0\.15\.10 \\\n(?:    --hash=sha256:[0-9a-f]{64})")

    def test_default_rules_and_reviewable_limits_are_enforced(self):
        defaults = self.findings("import os\nread_value = lambda: missing_value\n")
        self.assertEqual({key[2] for key in defaults}, {"F401", "E731", "F821"})
        self.assertEqual(self.findings(complex_source(9)), {})
        self.assertEqual(self.findings(complex_source(10))[
            ("scripts/sample.py", "inspect_value", "C901")], 11)
        self.assertEqual(self.findings("def count_values():\n" + "    value = 1\n" * 50
                                       + "    return value\n"), {})

    def test_new_complex_function_in_baselined_file_fails(self):
        source = complex_source(11)
        baseline = self.findings(source)
        current = self.findings(source + "\n" + source.replace(
            "inspect_value", "inspect_other"))
        self.assertTrue(any("new finding" in error for error in
                            GATE.compare_findings(current, baseline)))

    def test_grown_complexity_fails_and_reduced_complexity_passes(self):
        baseline = self.findings(complex_source(12))
        self.assertTrue(GATE.compare_findings(
            self.findings(complex_source(13)), baseline))
        self.assertEqual(GATE.compare_findings(
            self.findings(complex_source(11)), baseline), [])

    def test_deleted_debt_requires_removing_resolved_entry(self):
        baseline = self.findings(complex_source(11))
        current = self.findings("def inspect_value(value):\n    return value\n")
        self.assertTrue(GATE.compare_findings(current, baseline))
        self.assertEqual(GATE.compare_findings(current, {}), [])

    def test_moved_lines_preserve_symbol_identity(self):
        source = complex_source(11)
        baseline = self.findings(source)
        self.assertEqual(self.findings("\n\n\n" + source), baseline)

    def test_every_identity_field_and_count_affects_admission(self):
        key = ("scripts/sample.py", "Container.inspect_value", "C901")
        baseline = {key: 12}
        mutations = [
            ("tests/sample.py", key[1], key[2]),
            (key[0], "Other.inspect_value", key[2]),
            (key[0], key[1], "PLR0915"),
        ]
        for changed in mutations:
            with self.subTest(changed=changed):
                self.assertTrue(GATE.compare_findings({changed: 12}, baseline))
        self.assertTrue(GATE.compare_findings({key: 13}, baseline))
        self.assertEqual(GATE.compare_findings({key: 11}, baseline), [])

    def test_duplicate_records_and_json_keys_fail(self):
        record = dict(path="scripts/sample.py", symbol="inspect_value",
                      rule="C901", count=12)
        with self.assertRaises(ValueError):
            GATE.baseline_records(baseline_document([record, record]))
        with self.assertRaises(ValueError):
            json.loads('{"schema": 1, "schema": 1}',
                       object_pairs_hook=GATE.reject_duplicate_keys)

    def test_malformed_baseline_fails(self):
        record = dict(path="scripts/sample.py", symbol="inspect_value",
                      rule="C901", count=12)
        for field, value in [("path", "../sample.py"), ("symbol", ""),
                             ("rule", None), ("count", True), ("count", 0)]:
            with self.subTest(field=field, value=value), self.assertRaises(ValueError):
                GATE.baseline_records(baseline_document([{**record, field: value}]))
        with self.assertRaises(ValueError):
            GATE.baseline_records({})

    def test_naming_counts_and_statement_measurements(self):
        naming = self.findings("def BadName(BadArgument):\n    return BadArgument\n")
        self.assertEqual(naming[("scripts/sample.py", "BadName", "N802")], 1)
        self.assertEqual(naming[("scripts/sample.py", "BadName", "N803")], 1)
        statements = self.findings("def count_values():\n" + "    value = 1\n" * 51
                                   + "    return value\n")
        self.assertEqual(statements[("scripts/sample.py", "count_values", "PLR0915")], 51)

    def test_naming_occurrence_growth_fails_and_reduction_passes(self):
        source = "def BadName(BadFirst, BadSecond):\n    return BadFirst + BadSecond\n"
        baseline = self.findings(source)
        reduced = self.findings(source.replace("BadSecond", "second"))
        self.assertEqual(GATE.compare_findings(reduced, baseline), [])
        self.assertTrue(GATE.compare_findings(baseline, reduced))

    def test_qualified_symbols_keep_distinct_owners(self):
        source = "class First:\n    def BadName(self):\n        return 1\n"
        source += source.replace("First", "Second")
        findings = self.findings(source)
        self.assertIn(("scripts/sample.py", "First.BadName", "N802"), findings)
        self.assertIn(("scripts/sample.py", "Second.BadName", "N802"), findings)

    def test_ambiguous_symbols_fail(self):
        with self.assertRaises(ValueError):
            self.findings("def BadName():\n    pass\ndef BadName():\n    pass\n")

    def test_tool_failure_missing_tool_and_timeout_fail(self):
        version = subprocess.CompletedProcess([], 0, f"ruff {GATE.RUFF_VERSION}\n", "")
        failure = subprocess.CompletedProcess([], 2, "[]", "synthetic failure")
        with patch.object(GATE.subprocess, "run", side_effect=[version, failure]):
            with self.assertRaisesRegex(ValueError, "tool failure"):
                GATE.run_ruff(self.root)
        for error in (FileNotFoundError("ruff"), subprocess.TimeoutExpired("ruff", 15)):
            with patch.object(GATE.subprocess, "run", side_effect=error):
                with self.assertRaises(type(error)):
                    GATE.run_ruff(self.root)

    def test_wrong_tool_version_fails(self):
        result = subprocess.CompletedProcess([], 0, "ruff unexpected\n", "")
        with patch.object(GATE.subprocess, "run", return_value=result):
            with self.assertRaisesRegex(ValueError, "requires Ruff"):
                GATE.run_ruff(self.root)

    def test_malformed_json_and_status_disagreement_fail(self):
        version = subprocess.CompletedProcess([], 0, f"ruff {GATE.RUFF_VERSION}\n", "")
        for output in ("{", "{}", '[{}]', '[{"code": null}]',
                       '[{"code": "N802", "code": "N803"}]'):
            with self.subTest(output=output), self.assertRaises((ValueError, KeyError)):
                GATE.parse_findings(output, self.root)
        empty_failure = subprocess.CompletedProcess([], 1, "[]", "")
        with patch.object(GATE.subprocess, "run", side_effect=[version, empty_failure]):
            with self.assertRaisesRegex(ValueError, "disagrees"):
                GATE.run_ruff(self.root)


if __name__ == "__main__":
    unittest.main()
