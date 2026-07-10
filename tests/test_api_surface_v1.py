from __future__ import annotations

import copy
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
    "duplicate-identity.json",
    "duplicate-json-key.json",
    "implementation-dependency-type.json",
    "internal-package.json",
    "invalid-ordering.json",
    "malformed.json",
    "non-nfc.json",
    "unexported-declaration.json",
    "unexported-receiver.json",
    "unknown-field.json",
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


def load_first_json_value(path: Path) -> tuple[Any, str]:
    text = path.read_bytes().decode("utf-8")
    document, end = json.JSONDecoder().raw_decode(text.lstrip())
    return document, text.lstrip()[end:]


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
    return bool(name) and "A" <= name[0] <= "Z"


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


def write_json(path: Path, document: Any) -> None:
    path.write_text(
        json.dumps(document, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def find_symbol(document: dict[str, Any], kind: str) -> dict[str, Any]:
    return next(
        symbol
        for package in document["packages"]
        for symbol in package["symbols"]
        if symbol["kind"] == kind
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

    def assert_document_mutation_rejected(
        self,
        mutation: Any,
        category: str,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = copy_repo(Path(tmp))
            target = (
                repo
                / "api"
                / "fixtures"
                / "v1"
                / "positive"
                / "kinds-types-signatures.json"
            )
            document = load_json_strict(target)
            mutation(document)
            write_json(target, document)

            result = run_validator(repo)

            self.assertEqual(result.returncode, 1, result.stderr)
            self.assertIn(category, result.stderr)

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
        self.assertEqual(schema["properties"]["schema_version"]["type"], "integer")
        self.assertEqual(schema["properties"]["schema_version"]["const"], SCHEMA_VERSION)
        self.assertEqual(
            schema["$defs"]["asciiGoIdentifier"]["pattern"],
            "^[A-Za-z_][A-Za-z0-9_]*$",
        )
        self.assertEqual(
            schema["$defs"]["exportedAsciiGoIdentifier"]["pattern"],
            "^[A-Z][A-Za-z0-9_]*$",
        )
        self.assertIn("func", schema["$defs"]["asciiGoIdentifier"]["not"]["enum"])
        self.assertEqual(
            schema["$defs"]["package"]["properties"]["name"]["$ref"],
            "#/$defs/asciiGoIdentifier",
        )
        self.assertEqual(
            schema["$defs"]["symbol"]["properties"]["name"]["$ref"],
            "#/$defs/exportedAsciiGoIdentifier",
        )
        self.assertIn(
            "[A-Za-z_]",
            schema["$defs"]["symbol"]["properties"]["receiver"]["pattern"],
        )
        self.assertIn("AST-backed producer", schema["$comment"])
        self.assertIn("does not prove Go semantics", schema["description"])

    def test_reference_defines_normative_normalization_and_exclusions(self) -> None:
        self.require_file(REFERENCE)
        text = REFERENCE.read_bytes().decode("utf-8")
        headings = set(re.findall(r"^## (.+?)\s*$", text, re.MULTILINE))
        self.assertTrue(
            {
                "Schema Identity and Version",
                "Producer and Consumer Boundary",
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
            "future ast-backed producer must prove go syntax",
            "does not parse go",
            "consumers may rely on the frozen representation and corpus invariants only",
            "json booleans are not numbers",
            "consumers must accept any schema-equivalent json number",
            "canonical producers and every committed fixture must emit the single json token `1`",
            "[a-za-z_][a-za-z0-9_]*",
            "deliberate v1 portability constraint",
            "never consults the python unicode database",
            "complete expected diagnostic set",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, normalized)

    def test_reference_reproduces_the_publication_marker_contract(self) -> None:
        self.require_file(REFERENCE)
        normalized = " ".join(REFERENCE.read_text(encoding="utf-8").lower().split())
        for phrase in (
            "raw utf-8 json text and every decoded object-key and value occurrence",
            "case-sensitive, regex-equivalent forms",
            "`/(?:users)/[^/\\s]+/`",
            "`/(?:home)/[^/\\s]+/`",
            "`/(?:tmp)/[^\\s]+`",
            "`/(?:var)/folders/[^\\s]+`",
            "`[a-za-z]:\\\\(?:users)\\\\[^\\\\\\s]+\\\\`",
            "four dot-separated groups of one to three decimal digits",
            "is_private`, `is_loopback`, or `is_link_local",
            "`%[a-za-z0-9_.-]+` zone suffix",
            "40 or more hexadecimal digits",
            "assignment labels are case-insensitive under python `re.ignorecase`",
            "identifier labels are `token`, `password`, `passphrase`, `credential`,",
            "zero or one `_`, hyphen, or ascii-space separator",
            "one or more `_`, hyphen, or ascii-space separators",
            "`vendor[_ -]restricted` and `restricted[ -]+source`",
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
                self.assertRegex(
                    path.read_text(encoding="utf-8"),
                    r'(?m)^  "schema_version": 1,$',
                )
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

    def test_negative_fixtures_retain_the_synthetic_no_runtime_boundary(self) -> None:
        _, negative = self.require_fixture_sets()
        for path in negative:
            with self.subTest(path=path.name):
                document, remainder = load_first_json_value(path)
                self.assertEqual(document["schema_id"], SCHEMA_ID)
                self.assertIs(type(document["schema_version"]), int)
                self.assertEqual(document["schema_version"], SCHEMA_VERSION)
                self.assertRegex(
                    path.read_text(encoding="utf-8"),
                    r'(?m)^  "schema_version": 1,$',
                )
                self.assertIs(document["fixture"]["synthetic"], True)
                self.assertIs(document["fixture"]["runtime_claims"], False)
                self.assertTrue(document["packages"])
                self.assertTrue(
                    all(
                        package["path"].startswith(SYNTHETIC_PACKAGE_PREFIX)
                        for package in document["packages"]
                    )
                )
                if path.name == "malformed.json":
                    self.assertEqual(remainder.strip(), "!")
                else:
                    self.assertFalse(remainder.strip())

    def test_validator_enforces_negative_fixture_boundaries(self) -> None:
        cases = {
            "schema version": lambda document: document.__setitem__("schema_version", True),
            "synthetic marker": lambda document: document["fixture"].__setitem__(
                "synthetic", False
            ),
            "runtime marker": lambda document: document["fixture"].__setitem__(
                "runtime_claims", True
            ),
            "package path": lambda document: document["packages"][0].__setitem__(
                "path", "example.invalid/non-synthetic/negative"
            ),
        }
        for name, mutation in cases.items():
            with self.subTest(name=name):
                with tempfile.TemporaryDirectory() as tmp:
                    repo = copy_repo(Path(tmp))
                    target = (
                        repo
                        / "api"
                        / "fixtures"
                        / "v1"
                        / "negative"
                        / "duplicate-identity.json"
                    )
                    document = load_json_strict(target)
                    mutation(document)
                    write_json(target, document)

                    result = run_validator(repo)

                    self.assertEqual(result.returncode, 1, result.stderr)
                    self.assertIn("negative fixture boundary mismatch", result.stderr)

    def test_duplicate_key_boundaries_check_every_occurrence(self) -> None:
        valid_path = SYNTHETIC_PACKAGE_PREFIX + "negative"
        cases = {
            "conflicting schema identity": lambda text: text.replace(
                f'"schema_id": "{SCHEMA_ID}"',
                '"schema_id": "invalid.synthetic.schema"',
                1,
            ),
            "shadowed schema version": lambda text: text.replace(
                '"schema_version": 1,',
                '"schema_version": false,\n  "schema_version": 1,',
                1,
            ),
            "shadowed fixture marker": lambda text: text.replace(
                '"synthetic": true,',
                '"synthetic": false,\n    "synthetic": true,',
                1,
            ),
            "shadowed package path": lambda text: text.replace(
                f'"path": "{valid_path}"',
                f'"path": "example.invalid/non-synthetic/negative",\n'
                f'      "path": "{valid_path}"',
                1,
            ),
        }
        for name, mutation in cases.items():
            with self.subTest(name=name):
                with tempfile.TemporaryDirectory() as tmp:
                    repo = copy_repo(Path(tmp))
                    target = negative_path("duplicate-json-key.json", repo)
                    target.write_text(
                        mutation(target.read_text(encoding="utf-8")),
                        encoding="utf-8",
                    )

                    result = run_validator(repo)

                    self.assertEqual(result.returncode, 1, result.stderr)
                    self.assertIn("negative fixture boundary mismatch", result.stderr)

    def test_publication_markers_cannot_hide_in_a_shadowed_duplicate_value(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = copy_repo(Path(tmp))
            target = negative_path("duplicate-json-key.json", repo)
            original = '"signature": "type Example struct{}"'
            hidden = (
                '"signature": "account\\u005fid: hidden-synthetic-value",\n'
                '          "signature": "type Example struct{}"'
            )
            target.write_text(
                target.read_text(encoding="utf-8").replace(original, hidden, 1),
                encoding="utf-8",
            )

            result = run_validator(repo)

            self.assertEqual(result.returncode, 1, result.stderr)
            self.assertIn("private identifier", result.stderr)
            self.assertNotIn("hidden-synthetic-value", result.stderr)
            self.assertNotIn(str(repo), result.stderr)

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

    def test_validator_rejects_bool_integer_ambiguity(self) -> None:
        cases = {
            "schema version": lambda document: document.__setitem__("schema_version", True),
            "synthetic marker": lambda document: document["fixture"].__setitem__("synthetic", 1),
            "runtime marker": lambda document: document["fixture"].__setitem__(
                "runtime_claims", 0
            ),
        }
        for name, mutation in cases.items():
            with self.subTest(name=name):
                expected = (
                    "schema identity mismatch"
                    if name == "schema version"
                    else "runtime claim or non-synthetic fixture"
                )
                self.assert_document_mutation_rejected(mutation, expected)

    def test_validator_accepts_schema_equivalent_numeric_version(self) -> None:
        targets = (
            Path("api/fixtures/v1/positive/kinds-types-signatures.json"),
            Path("api/fixtures/v1/negative/duplicate-identity.json"),
        )
        for relative_path in targets:
            with self.subTest(relative_path=relative_path.as_posix()):
                with tempfile.TemporaryDirectory() as tmp:
                    repo = copy_repo(Path(tmp))
                    target = repo / relative_path
                    document = load_json_strict(target)
                    document["schema_version"] = 1.0
                    write_json(target, document)

                    result = run_validator(repo)

                    self.assertEqual(result.returncode, 0, result.stderr)

        with tempfile.TemporaryDirectory() as tmp:
            repo = copy_repo(Path(tmp))
            target = first_positive(repo)
            target.write_text(
                target.read_text(encoding="utf-8").replace(
                    '"schema_version": 1,',
                    '"schema_version": 1e0,',
                    1,
                ),
                encoding="utf-8",
            )

            result = run_validator(repo)

            self.assertEqual(result.returncode, 0, result.stderr)

    def test_validator_does_not_round_non_integral_schema_version(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = copy_repo(Path(tmp))
            target = first_positive(repo)
            target.write_text(
                target.read_text(encoding="utf-8").replace(
                    '"schema_version": 1,',
                    '"schema_version": 1.0000000000000001,',
                    1,
                ),
                encoding="utf-8",
            )

            result = run_validator(repo)

            self.assertEqual(result.returncode, 1, result.stderr)
            self.assertIn("schema identity mismatch", result.stderr)

    def test_validator_rejects_missing_fields_and_invalid_kind(self) -> None:
        cases = {
            "root fixture": lambda document: document.pop("fixture"),
            "package name": lambda document: document["packages"][0].pop("name"),
            "symbol type": lambda document: document["packages"][0]["symbols"][0].pop(
                "type"
            ),
            "invalid kind": lambda document: document["packages"][0]["symbols"][0].__setitem__(
                "kind", "function"
            ),
        }
        for name, mutation in cases.items():
            with self.subTest(name=name):
                expected = "invalid symbol kind" if name == "invalid kind" else "missing required field"
                self.assert_document_mutation_rejected(mutation, expected)

    def test_validator_rejects_wrong_root_package_and_symbol_types(self) -> None:
        cases = (
            ("root", "invalid document shape"),
            ("package", "invalid package shape"),
            ("symbol", "invalid symbol shape"),
        )
        for level, expected in cases:
            with self.subTest(level=level):
                with tempfile.TemporaryDirectory() as tmp:
                    repo = copy_repo(Path(tmp))
                    target = first_positive(repo)
                    document = load_json_strict(target)
                    if level == "root":
                        document = []
                    elif level == "package":
                        document["packages"][0] = []
                    else:
                        document["packages"][0]["symbols"][0] = []
                    write_json(target, document)

                    result = run_validator(repo)

                    self.assertEqual(result.returncode, 1, result.stderr)
                    self.assertIn(expected, result.stderr)

    def test_validator_rejects_empty_collections_and_duplicate_packages(self) -> None:
        cases = {
            "packages": (
                lambda document: document.__setitem__("packages", []),
                "invalid package collection",
            ),
            "symbols": (
                lambda document: document["packages"][0].__setitem__("symbols", []),
                "invalid symbol collection",
            ),
            "duplicate package": (
                lambda document: document["packages"].append(
                    copy.deepcopy(document["packages"][0])
                ),
                "duplicate package identity",
            ),
        }
        for name, (mutation, expected) in cases.items():
            with self.subTest(name=name):
                self.assert_document_mutation_rejected(mutation, expected)

    def test_validator_rejects_invalid_package_paths(self) -> None:
        paths = (
            SYNTHETIC_PACKAGE_PREFIX + "/double",
            SYNTHETIC_PACKAGE_PREFIX + "../dot",
            SYNTHETIC_PACKAGE_PREFIX + "back\\slash",
            SYNTHETIC_PACKAGE_PREFIX + "white space",
            SYNTHETIC_PACKAGE_PREFIX + "trailing/",
        )
        for value in paths:
            with self.subTest(form=value.rsplit("/", 1)[-1]):
                self.assert_document_mutation_rejected(
                    lambda document, value=value: document["packages"][0].__setitem__(
                        "path", value
                    ),
                    "invalid package path",
                )

    def test_validator_checks_complete_go_identifiers_and_keywords(self) -> None:
        cases = {
            "symbol punctuation": lambda document: document["packages"][0]["symbols"][
                0
            ].__setitem__("name", "Bad-Name"),
            "symbol leading digit": lambda document: document["packages"][0]["symbols"][
                0
            ].__setitem__("name", "9Bad"),
            "package keyword": lambda document: document["packages"][0].__setitem__(
                "name", "func"
            ),
        }
        for name, mutation in cases.items():
            with self.subTest(name=name):
                self.assert_document_mutation_rejected(mutation, "invalid Go identifier")

    def test_unicode_database_versions_cannot_change_identifier_acceptance(self) -> None:
        # U+1C89 changed from unassigned to an uppercase letter in Unicode 16.0.
        version_sensitive = "\u1c89"
        cases = {
            "package name": (
                lambda document: document["packages"][0].__setitem__(
                    "name", version_sensitive + "package"
                ),
                "invalid Go identifier",
            ),
            "symbol name": (
                lambda document: find_symbol(document, "type").__setitem__(
                    "name", version_sensitive + "Symbol"
                ),
                "invalid Go identifier",
            ),
            "receiver base": (
                lambda document: find_symbol(document, "method").__setitem__(
                    "receiver", "*" + version_sensitive + "Catalog"
                ),
                "invalid receiver",
            ),
            "generic receiver identifier": (
                lambda document: find_symbol(document, "method").__setitem__(
                    "receiver", "*Catalog[" + version_sensitive + "T]"
                ),
                "invalid receiver",
            ),
        }
        for name, (mutation, expected) in cases.items():
            with self.subTest(name=name):
                self.assert_document_mutation_rejected(mutation, expected)

    def test_validator_enforces_receiver_grammar_and_exported_base(self) -> None:
        invalid_receivers = ("**Catalog", "pkg.Catalog", "Catalog[T,U]", "Catalog[func]")
        for receiver in invalid_receivers:
            with self.subTest(receiver=receiver):
                self.assert_document_mutation_rejected(
                    lambda document, receiver=receiver: find_symbol(document, "method").__setitem__(
                        "receiver", receiver
                    ),
                    "invalid receiver",
                )

        self.assert_document_mutation_rejected(
            lambda document: find_symbol(document, "method").__setitem__(
                "receiver", "catalog"
            ),
            "unexported receiver",
        )

    def test_validator_accepts_normalized_generic_receiver_representation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = copy_repo(Path(tmp))
            target = (
                repo
                / "api"
                / "fixtures"
                / "v1"
                / "positive"
                / "kinds-types-signatures.json"
            )
            document = load_json_strict(target)
            method = find_symbol(document, "method")
            method["receiver"] = "*Catalog[T, U]"
            method["signature"] = "func (*Catalog[T, U]) Lookup(string) (Entry, bool)"
            write_json(target, document)

            result = run_validator(repo)

            self.assertEqual(result.returncode, 0, result.stderr)

    def test_validator_leaves_go_syntax_proof_to_the_ast_producer(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = copy_repo(Path(tmp))
            target = (
                repo
                / "api"
                / "fixtures"
                / "v1"
                / "positive"
                / "kinds-types-signatures.json"
            )
            document = load_json_strict(target)
            symbol = find_symbol(document, "const")
            symbol["type"] = "not-a-go-type"
            symbol["signature"] = "const MaxEntries not-a-go-type"
            write_json(target, document)

            result = run_validator(repo)

            self.assertEqual(result.returncode, 0, result.stderr)

    def test_validator_rejects_receiver_misuse_and_missing_receiver(self) -> None:
        cases = {
            "receiver on function": (
                lambda document: find_symbol(document, "func").__setitem__(
                    "receiver", "Catalog"
                ),
                "receiver on non-method",
            ),
            "missing method receiver": (
                lambda document: find_symbol(document, "method").pop("receiver"),
                "missing required field",
            ),
        }
        for name, (mutation, expected) in cases.items():
            with self.subTest(name=name):
                self.assert_document_mutation_rejected(mutation, expected)

    def test_validator_rejects_non_normalized_text(self) -> None:
        values = (" uint16", "uint16 ", "uint  16", "uint\t16", "uint\n16")
        for value in values:
            with self.subTest(value=repr(value)):
                self.assert_document_mutation_rejected(
                    lambda document, value=value: document["packages"][0]["symbols"][
                        0
                    ].__setitem__("type", value),
                    "invalid normalized text",
                )

    def test_validator_rejects_portable_cross_field_mismatches(self) -> None:
        cases = {
            "declared name": lambda document: find_symbol(document, "func").__setitem__(
                "signature", "func Different([]Entry) *Catalog"
            ),
            "declared receiver": lambda document: find_symbol(document, "method").__setitem__(
                "receiver", "Catalog"
            ),
            "function type prefix": lambda document: find_symbol(document, "func").__setitem__(
                "type", "[]Entry"
            ),
            "declaration kind": lambda document: find_symbol(document, "var").__setitem__(
                "signature", "const ErrMissing error"
            ),
        }
        for name, mutation in cases.items():
            with self.subTest(name=name):
                self.assert_document_mutation_rejected(mutation, "cross-field mismatch")

    def test_validator_rejects_escaped_controls_and_surrogates_without_crashing(self) -> None:
        for name, value, expected in (
            ("control", "uint16\x00", "control character"),
            ("line separator", "uint16\u2028string", "line or paragraph separator"),
            ("paragraph separator", "uint16\u2029string", "line or paragraph separator"),
            ("surrogate", "uint16\ud800", "invalid Unicode scalar value"),
        ):
            with self.subTest(name=name):
                with tempfile.TemporaryDirectory() as tmp:
                    repo = copy_repo(Path(tmp))
                    target = (
                        repo
                        / "api"
                        / "fixtures"
                        / "v1"
                        / "positive"
                        / "kinds-types-signatures.json"
                    )
                    document = load_json_strict(target)
                    document["packages"][0]["symbols"][0]["type"] = value
                    target.write_text(
                        json.dumps(document, ensure_ascii=True, indent=2) + "\n",
                        encoding="utf-8",
                    )

                    result = run_validator(repo)

                    self.assertEqual(result.returncode, 1, result.stderr)
                    self.assertIn(expected, result.stderr)
                    self.assertNotIn("Traceback", result.stderr)

    def test_validator_rejects_each_declared_publication_marker_category(self) -> None:
        self.require_file(API_VALIDATOR)
        positive, _ = self.require_fixture_sets()
        cases = (
            ("macOS user path", "private path", "/Users/" + "example-user/project/input.go"),
            ("Unix home path", "private path", "/home/" + "example-user/project/input.go"),
            ("temporary path", "private path", "/tmp/" + "synthetic/input.go"),
            ("macOS temporary path", "private path", "/var/" + "folders/synthetic/input.go"),
            ("Windows user path", "private path", "C:\\Users\\example-user\\input.go"),
            ("private IPv4", "private network", "peer " + "192." + "168.7.9"),
            ("other IPv4", "network address", "peer " + "8." + "8.8.8"),
            ("IPv6", "network address", "peer 2001:" + "db8::1"),
            ("account label", "private identifier", "account_" + "id: private-account-value"),
            ("household label", "household data", "household " + "schedule: private-schedule-value"),
            ("raw label", "raw evidence", "raw " + "evidence: private-capture-value"),
            ("restricted marker", "source contamination", "vendor_" + "restricted"),
        )
        for name, expected, value in cases:
            with self.subTest(name=name):
                with tempfile.TemporaryDirectory() as tmp:
                    repo = copy_repo(Path(tmp))
                    target = repo / positive[0].relative_to(REPO)
                    replace_first_symbol_value(target, "signature", value)

                    result = run_validator(repo)

                    self.assertEqual(result.returncode, 1, result.stderr)
                    self.assertIn(expected, result.stderr.lower())
                    self.assertNotIn(value, result.stderr)

    def test_publication_marker_threshold_case_and_separators_match_the_contract(self) -> None:
        cases = (
            ("fingerprint below threshold", "a" * 39, None),
            ("invalid IPv4", "999.999.999.999", None),
            ("fingerprint at threshold", "a" * 40, "private identifier"),
            ("mixed-case private label", "ClIeNt-SeCrEt = synthetic", "private identifier"),
            ("household underscore", "HoUsEhOlD_ScHeDuLe: synthetic", "household data"),
            ("raw hyphen", "RaW-EvIdEnCe=synthetic", "raw evidence"),
            ("vendor marker", "VeNdOr-ReStRiCtEd", "source contamination"),
            ("source marker", "ReStRiCtEd- -SoUrCe", "source contamination"),
        )
        for name, value, expected in cases:
            with self.subTest(name=name):
                with tempfile.TemporaryDirectory() as tmp:
                    repo = copy_repo(Path(tmp))
                    target = (
                        repo
                        / "api"
                        / "fixtures"
                        / "v1"
                        / "positive"
                        / "kinds-types-signatures.json"
                    )
                    document = load_json_strict(target)
                    symbol = find_symbol(document, "const")
                    symbol["type"] = value
                    symbol["signature"] = f'const {symbol["name"]} {value}'
                    write_json(target, document)

                    result = run_validator(repo)

                    if expected is None:
                        self.assertEqual(result.returncode, 0, result.stderr)
                    else:
                        self.assertEqual(result.returncode, 1, result.stderr)
                        self.assertIn(expected, result.stderr)
                        self.assertNotIn(value, result.stderr)

    def test_publication_markers_cannot_hide_behind_json_escapes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = copy_repo(Path(tmp))
            target = (
                repo
                / "api"
                / "fixtures"
                / "v1"
                / "positive"
                / "kinds-types-signatures.json"
            )
            replace_first_symbol_value(
                target,
                "signature",
                "account_id: synthetic-private-value",
            )
            target.write_text(
                target.read_text(encoding="utf-8").replace(
                    "account_id",
                    "account\\u005fid",
                    1,
                ),
                encoding="utf-8",
            )

            result = run_validator(repo)

            self.assertEqual(result.returncode, 1, result.stderr)
            self.assertIn("private identifier", result.stderr)
            self.assertNotIn("synthetic-private-value", result.stderr)

    def test_failure_diagnostics_are_repeatable_and_path_value_safe(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = copy_repo(Path(tmp))
            target = (
                repo
                / "api"
                / "fixtures"
                / "v1"
                / "positive"
                / "kinds-types-signatures.json"
            )
            sensitive_value = "/Users/" + "diagnostic-secret/private.go"
            replace_first_symbol_value(target, "signature", sensitive_value)

            first = run_validator(repo)
            second = run_validator(repo)

            self.assertEqual(first.returncode, 1)
            self.assertEqual((first.stdout, first.stderr), (second.stdout, second.stderr))
            self.assertNotIn(sensitive_value, first.stderr)
            self.assertNotIn(str(repo), first.stderr)
            self.assertNotIn(str(Path(tmp)), first.stderr)
            for line in first.stderr.splitlines():
                self.assertRegex(line, r"^api/(?:schema|fixtures)/")

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
                    actual_artifact = next(
                        path
                        for path in (repo / "api").rglob("*")
                        if path.is_file() and path.name == artifact.name
                    )
                    actual_relative_path = actual_artifact.relative_to(repo).as_posix()

                    result = run_policy_validator(repo)

                    self.assertEqual(result.returncode, 1, result.stderr)
                    self.assertIn(actual_relative_path, result.stderr)
                    self.assertRegex(
                        result.stderr,
                        rf"{re.escape(actual_relative_path)}:.*"
                        r"(?:allowlist|machine artifact|Markdown extension)",
                    )
                    invented_variant = actual_relative_path.replace(
                        "/positive/", "/Positive/"
                    ).replace(
                        "/negative/", "/Negative/"
                    )
                    if invented_variant != actual_relative_path:
                        self.assertNotIn(invented_variant, result.stderr)

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

    def test_negative_fixture_rejects_unrelated_added_diagnostic(self) -> None:
        cases = (
            ("duplicate-identity.json", False),
            ("malformed.json", True),
        )
        for fixture_name, retain_malformed_suffix in cases:
            with self.subTest(fixture_name=fixture_name):
                with tempfile.TemporaryDirectory() as tmp:
                    repo = copy_repo(Path(tmp))
                    target = negative_path(fixture_name, repo)
                    if retain_malformed_suffix:
                        document, _ = load_first_json_value(target)
                    else:
                        document = load_json_strict(target)
                    document["unrelated_invalidity"] = "synthetic-marker"
                    write_json(target, document)
                    if retain_malformed_suffix:
                        target.write_text(
                            target.read_text(encoding="utf-8") + "!\n",
                            encoding="utf-8",
                        )

                    result = run_validator(repo)

                    self.assertEqual(result.returncode, 1, result.stderr)
                    self.assertIn(
                        f"api/fixtures/v1/negative/{fixture_name}: "
                        "unexpected negative category: unknown field",
                        result.stderr,
                    )
                    self.assertNotIn("synthetic-marker", result.stderr)

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
