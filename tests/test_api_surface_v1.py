from __future__ import annotations

import json
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import unicodedata
import unittest
from pathlib import Path
from typing import Any


REPO = Path(__file__).resolve().parents[1]
POLICY_VALIDATOR = REPO / "scripts" / "validate_repository_policy.py"
API_VALIDATOR = REPO / "scripts" / "validate_api_surface_v1.py"
SCHEMA = REPO / "api" / "schema" / "helianthus.eebus.api-surface.v1.schema.json"
REFERENCE = REPO / "api" / "api-surface-v1.md"
POSITIVE_FIXTURES = REPO / "api" / "fixtures" / "v1" / "positive"
NEGATIVE_FIXTURES = REPO / "api" / "fixtures" / "v1" / "negative"

SCHEMA_ID = "helianthus.eebus.api-surface.v1"
SCHEMA_URI = "urn:helianthus:eebus:api-surface:v1"
SCHEMA_VERSION = 1
SYNTHETIC_PACKAGE_PREFIX = "example.invalid/helianthus/synthetic/"

REQUIRED_POSITIVE_FIXTURES = {
    "packages-and-symbols.json",
    "kinds-types-signatures.json",
}
REQUIRED_NEGATIVE_FIXTURES = {
    "malformed.json",
    "duplicate-json-key.json",
    "duplicate-identity.json",
    "invalid-ordering.json",
    "internal-package.json",
    "unexported-declaration.json",
    "unexported-receiver.json",
    "implementation-dependency-type.json",
}
SYMBOL_KINDS = {"const", "func", "method", "type", "var"}


class DuplicateJSONKeyError(ValueError):
    pass


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateJSONKeyError(f"duplicate key {key!r}")
        result[key] = value
    return result


def load_json_strict(path: Path) -> Any:
    text = path.read_bytes().decode("utf-8")
    return json.loads(text, object_pairs_hook=_unique_object)


def copy_repo(tmp_path: Path) -> Path:
    destination = tmp_path / "repo"
    ignore = shutil.ignore_patterns(".git", ".pytest_cache", "__pycache__")
    shutil.copytree(REPO, destination, ignore=ignore)
    return destination


def run_validator(repo: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(API_VALIDATOR), "--repo", str(repo)],
        cwd=repo,
        check=False,
        text=True,
        capture_output=True,
    )


def run_policy_validator(repo: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(POLICY_VALIDATOR), "--repo", str(repo)],
        cwd=repo,
        check=False,
        text=True,
        capture_output=True,
    )


def positive_paths(root: Path = REPO) -> list[Path]:
    return sorted((root / "api" / "fixtures" / "v1" / "positive").glob("*.json"))


def negative_path(name: str, root: Path = REPO) -> Path:
    return root / "api" / "fixtures" / "v1" / "negative" / name


def symbol_identity(package: dict[str, Any], symbol: dict[str, Any]) -> tuple[str, str, str, str]:
    return (
        package["path"],
        symbol["kind"],
        symbol.get("receiver", ""),
        symbol["name"],
    )


def symbol_order_key(symbol: dict[str, Any]) -> tuple[bytes, bytes, bytes]:
    return tuple(
        value.encode("utf-8")
        for value in (
            symbol["kind"],
            symbol.get("receiver", ""),
            symbol["name"],
        )
    )


def package_order_key(package: dict[str, Any]) -> tuple[bytes, bytes]:
    return (package["path"].encode("utf-8"), package["name"].encode("utf-8"))


def receiver_base(receiver: str) -> str:
    base = receiver.lstrip("*").split("[", 1)[0]
    return base.rsplit(".", 1)[-1]


def is_exported(name: str) -> bool:
    return bool(name) and unicodedata.category(name[0]) == "Lu"


def first_positive(root: Path = REPO) -> Path:
    paths = positive_paths(root)
    if not paths:
        raise AssertionError("no positive API surface v1 fixture exists")
    return paths[0]


def replace_first_symbol_value(path: Path, key: str, value: str) -> None:
    document = load_json_strict(path)
    document["packages"][0]["symbols"][0][key] = value
    path.write_text(
        json.dumps(document, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


class APISurfaceV1ContractTests(unittest.TestCase):
    def require_file(self, path: Path) -> None:
        self.assertTrue(path.is_file(), f"missing regular file: {path.relative_to(REPO)}")
        self.assertFalse(path.is_symlink(), f"symlink is forbidden: {path.relative_to(REPO)}")

    def require_fixture_sets(self) -> tuple[list[Path], list[Path]]:
        positive = positive_paths()
        negative = sorted(NEGATIVE_FIXTURES.glob("*.json"))
        self.assertTrue(positive, "missing positive API surface v1 fixtures")
        self.assertTrue(negative, "missing negative API surface v1 fixtures")
        return positive, negative

    def test_canonical_contract_paths_are_regular_files(self) -> None:
        for path in (SCHEMA, REFERENCE, API_VALIDATOR):
            with self.subTest(path=path.relative_to(REPO)):
                self.require_file(path)

        positive, negative = self.require_fixture_sets()
        self.assertTrue(REQUIRED_POSITIVE_FIXTURES.issubset({path.name for path in positive}))
        self.assertTrue(REQUIRED_NEGATIVE_FIXTURES.issubset({path.name for path in negative}))

    def test_schema_has_stable_identity_version_and_closed_root(self) -> None:
        self.require_file(SCHEMA)
        schema = load_json_strict(SCHEMA)

        self.assertEqual(schema["$schema"], "https://json-schema.org/draft/2020-12/schema")
        self.assertEqual(schema["$id"], SCHEMA_URI)
        self.assertEqual(schema["type"], "object")
        self.assertIs(schema["additionalProperties"], False)
        self.assertTrue(
            {"schema_id", "schema_version", "packages"}.issubset(schema["required"])
        )
        self.assertEqual(schema["properties"]["schema_id"]["const"], SCHEMA_ID)
        self.assertEqual(schema["properties"]["schema_version"]["const"], SCHEMA_VERSION)

    def test_reference_defines_normative_normalization_and_exclusions(self) -> None:
        self.require_file(REFERENCE)
        text = REFERENCE.read_bytes().decode("utf-8")
        headings = set(re.findall(r"^## (.+?)\s*$", text, re.MULTILINE))
        self.assertTrue(
            {
                "Schema Identity and Version",
                "Package Normalization",
                "Symbol Normalization",
                "Kind and Type Normalization",
                "Signature Normalization",
                "Canonical Ordering",
                "Exclusions",
                "Synthetic Golden Fixtures",
                "Privacy and Source Restrictions",
            }.issubset(headings)
        )

        normalized = " ".join(text.lower().split())
        for phrase in (
            SCHEMA_ID,
            "utf-8",
            "unicode normalization form c",
            "bytewise",
            "internal package",
            "unexported declaration",
            "unexported receiver",
            "implementation dependency type",
            "no runtime symbol",
            "publishable source",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, normalized)

    def test_positive_fixtures_are_explicitly_synthetic_and_make_no_runtime_claim(self) -> None:
        positive, _ = self.require_fixture_sets()
        for path in positive:
            with self.subTest(path=path.name):
                document = load_json_strict(path)
                self.assertEqual(document["schema_id"], SCHEMA_ID)
                self.assertEqual(document["schema_version"], SCHEMA_VERSION)
                self.assertIs(document["fixture"]["synthetic"], True)
                self.assertIs(document["fixture"]["runtime_claims"], False)
                self.assertTrue(document["packages"])
                for package in document["packages"]:
                    self.assertTrue(
                        package["path"].startswith(SYNTHETIC_PACKAGE_PREFIX),
                        f"{path.name} uses a non-synthetic package path",
                    )

                raw = path.read_text(encoding="utf-8").lower()
                self.assertNotIn("github.com/project-helianthus/helianthus-eebusreg", raw)
                self.assertNotIn("vendor_" + "restricted", raw)
                self.assertNotIn("restricted" + " source", raw)

    def test_positive_fixtures_cover_normalized_fields_kinds_and_ordering(self) -> None:
        positive, _ = self.require_fixture_sets()
        seen_kinds: set[str] = set()
        package_count = 0
        symbol_count = 0

        for path in positive:
            document = load_json_strict(path)
            packages = document["packages"]
            self.assertEqual(packages, sorted(packages, key=package_order_key), path.name)
            package_count += len(packages)
            for package in packages:
                self.assertEqual(package["path"], unicodedata.normalize("NFC", package["path"]))
                self.assertEqual(package["name"], unicodedata.normalize("NFC", package["name"]))
                self.assertNotRegex(package["path"], r"(?:^|/)(?:\.|\.\.|internal)(?:/|$)")
                symbols = package["symbols"]
                self.assertEqual(symbols, sorted(symbols, key=symbol_order_key), path.name)
                identities = [symbol_identity(package, symbol) for symbol in symbols]
                self.assertEqual(len(identities), len(set(identities)), path.name)

                for symbol in symbols:
                    seen_kinds.add(symbol["kind"])
                    symbol_count += 1
                    self.assertTrue(is_exported(symbol["name"]))
                    self.assertEqual(symbol["name"], unicodedata.normalize("NFC", symbol["name"]))
                    self.assertTrue(symbol["type"])
                    self.assertTrue(symbol["signature"])
                    for field in ("type", "signature"):
                        self.assertEqual(symbol[field], symbol[field].strip())
                        self.assertNotRegex(symbol[field], r"[\t\r\n]| {2}")
                    if symbol["kind"] == "method":
                        self.assertTrue(is_exported(receiver_base(symbol["receiver"])))
                    else:
                        self.assertNotIn("receiver", symbol)

        self.assertGreaterEqual(package_count, 2)
        self.assertGreaterEqual(symbol_count, len(SYMBOL_KINDS))
        self.assertEqual(seen_kinds, SYMBOL_KINDS)

    def test_negative_fixtures_target_each_required_failure_mode(self) -> None:
        _, negative = self.require_fixture_sets()
        self.assertTrue(REQUIRED_NEGATIVE_FIXTURES.issubset({path.name for path in negative}))

        with self.assertRaises(json.JSONDecodeError):
            load_json_strict(negative_path("malformed.json"))
        with self.assertRaises(DuplicateJSONKeyError):
            load_json_strict(negative_path("duplicate-json-key.json"))

        duplicate = load_json_strict(negative_path("duplicate-identity.json"))
        duplicate_ids = [
            symbol_identity(package, symbol)
            for package in duplicate["packages"]
            for symbol in package["symbols"]
        ]
        self.assertNotEqual(len(duplicate_ids), len(set(duplicate_ids)))

        unordered = load_json_strict(negative_path("invalid-ordering.json"))
        ordering_is_invalid = unordered["packages"] != sorted(
            unordered["packages"], key=package_order_key
        ) or any(
            package["symbols"] != sorted(package["symbols"], key=symbol_order_key)
            for package in unordered["packages"]
        )
        self.assertTrue(ordering_is_invalid)

        internal = load_json_strict(negative_path("internal-package.json"))
        self.assertTrue(
            any("internal" in package["path"].split("/") for package in internal["packages"])
        )

        unexported = load_json_strict(negative_path("unexported-declaration.json"))
        self.assertTrue(
            any(
                not is_exported(symbol["name"])
                for package in unexported["packages"]
                for symbol in package["symbols"]
            )
        )

        receiver = load_json_strict(negative_path("unexported-receiver.json"))
        self.assertTrue(
            any(
                symbol["kind"] == "method"
                and not is_exported(receiver_base(symbol["receiver"]))
                for package in receiver["packages"]
                for symbol in package["symbols"]
            )
        )

        leakage = load_json_strict(negative_path("implementation-dependency-type.json"))
        leaked_fields = "\n".join(
            symbol[field]
            for package in leakage["packages"]
            for symbol in package["symbols"]
            for field in ("type", "signature")
        )
        self.assertIn("implementation.invalid/", leaked_fields)

    def test_validator_accepts_the_corpus_deterministically(self) -> None:
        self.require_file(API_VALIDATOR)
        first = run_validator(REPO)
        second = run_validator(REPO)
        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertEqual(second.returncode, 0, second.stderr)
        self.assertEqual((first.stdout, first.stderr), (second.stdout, second.stderr))

    def test_validator_rejects_duplicate_keys_in_schema_and_fixture_json(self) -> None:
        self.require_file(API_VALIDATOR)
        self.require_file(SCHEMA)
        positive, _ = self.require_fixture_sets()

        targets = [SCHEMA.relative_to(REPO), positive[0].relative_to(REPO)]
        for relative_path in targets:
            with self.subTest(path=relative_path):
                with tempfile.TemporaryDirectory() as tmp:
                    repo = copy_repo(Path(tmp))
                    path = repo / relative_path
                    original = path.read_text(encoding="utf-8")
                    path.write_text(
                        original.replace("{", '{\n  "schema_id": "duplicate",', 1),
                        encoding="utf-8",
                    )

                    result = run_validator(repo)

                    self.assertEqual(result.returncode, 1, result.stderr)
                    self.assertIn(relative_path.as_posix(), result.stderr)
                    self.assertIn("duplicate key", result.stderr.lower())

    def test_validator_rejects_non_utf8_machine_artifacts(self) -> None:
        self.require_file(API_VALIDATOR)
        positive, _ = self.require_fixture_sets()
        with tempfile.TemporaryDirectory() as tmp:
            repo = copy_repo(Path(tmp))
            relative_path = positive[0].relative_to(REPO)
            (repo / relative_path).write_bytes(b'{"schema_id":"broken","value":"\xff"}\n')

            result = run_validator(repo)

            self.assertEqual(result.returncode, 1, result.stderr)
            self.assertIn(relative_path.as_posix(), result.stderr)
            self.assertIn("utf-8", result.stderr.lower())

    def test_validator_rejects_private_paths_network_data_and_source_contamination(self) -> None:
        self.require_file(API_VALIDATOR)
        positive, _ = self.require_fixture_sets()
        cases = {
            "private path": "/Users/" + "example-user/project/input.go",
            "private network": "peer " + "192." + "168.7.9",
            "source contamination": "vendor_" + "restricted",
        }
        for expected, value in cases.items():
            with self.subTest(expected=expected):
                with tempfile.TemporaryDirectory() as tmp:
                    repo = copy_repo(Path(tmp))
                    target = repo / positive[0].relative_to(REPO)
                    replace_first_symbol_value(target, "signature", value)

                    result = run_validator(repo)

                    self.assertEqual(result.returncode, 1, result.stderr)
                    self.assertIn(expected, result.stderr.lower())

    def test_repository_policy_allows_only_canonical_machine_artifact_patterns(self) -> None:
        self.require_file(SCHEMA)
        positive, negative = self.require_fixture_sets()
        allowed = {SCHEMA.relative_to(REPO)} | {
            path.relative_to(REPO) for path in positive + negative
        }
        actual = {
            path.relative_to(REPO)
            for path in (REPO / "api").rglob("*")
            if path.is_file() and path.suffix.lower() not in {".md", ".markdown", ".mdown", ".mkd", ".mkdn"}
        }
        self.assertEqual(actual, allowed)

        result = run_policy_validator(REPO)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_repository_policy_still_rejects_rogue_api_machine_artifacts(self) -> None:
        rogue_paths = (
            "api/api-surface-v1.json",
            "api/schema/extra.json",
            "api/fixtures/v2/positive/extra.json",
            "api/fixtures/v1/positive/nested/extra.json",
            "api/fixtures/v1/Positive/extra.json",
            "api/fixtures/v1/negative/extra.txt",
        )
        for relative_path in rogue_paths:
            with self.subTest(relative_path=relative_path):
                with tempfile.TemporaryDirectory() as tmp:
                    repo = copy_repo(Path(tmp))
                    artifact = repo / relative_path
                    artifact.parent.mkdir(parents=True, exist_ok=True)
                    artifact.write_text("{}\n", encoding="utf-8")

                    result = run_policy_validator(repo)

                    self.assertEqual(result.returncode, 1, result.stderr)
                    self.assertIn(relative_path, result.stderr)
                    self.assertRegex(
                        result.stderr,
                        rf"{re.escape(relative_path)}:.*(?:allowlist|machine artifact|Markdown extension)",
                    )

    def test_each_negative_fixture_must_remain_invalid(self) -> None:
        self.require_file(API_VALIDATOR)
        positive, negative = self.require_fixture_sets()
        valid_bytes = positive[0].read_bytes()
        for path in negative:
            with self.subTest(path=path.name):
                with tempfile.TemporaryDirectory() as tmp:
                    repo = copy_repo(Path(tmp))
                    relative_path = path.relative_to(REPO)
                    (repo / relative_path).write_bytes(valid_bytes)

                    result = run_validator(repo)

                    self.assertEqual(result.returncode, 1, result.stderr)
                    self.assertIn(relative_path.as_posix(), result.stderr)

    def test_ci_local_invokes_api_surface_validator_before_unit_tests(self) -> None:
        ci_local = REPO / "scripts" / "ci_local.sh"
        lines = ci_local.read_text(encoding="utf-8").splitlines()
        commands = [
            (index, shlex.split(line))
            for index, line in enumerate(lines)
            if line.strip() and not line.lstrip().startswith("#")
        ]
        invocations = [
            index
            for index, command in commands
            if "scripts/validate_api_surface_v1.py" in command
        ]
        unit_test_lines = [
            index
            for index, command in commands
            if command[:3] == ["python3", "-m", "unittest"]
        ]

        self.assertEqual(len(invocations), 1, "ci_local.sh must invoke the API validator once")
        self.assertEqual(len(unit_test_lines), 1, "ci_local.sh must invoke unittest once")
        self.assertLess(invocations[0], unit_test_lines[0])


if __name__ == "__main__":
    unittest.main()
