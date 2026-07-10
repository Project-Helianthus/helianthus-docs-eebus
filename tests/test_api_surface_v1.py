from __future__ import annotations

import copy
import hashlib
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
from typing import Any, Callable


REPO = Path(__file__).resolve().parents[1]
SCRIPTS = REPO / "scripts"
sys.path.insert(0, str(SCRIPTS))

from validate_api_surface_v1 import (  # noqa: E402
    compatibility_fingerprint,
    compatibility_projection,
    document_diagnostics,
)


POLICY_VALIDATOR = SCRIPTS / "validate_repository_policy.py"
API_VALIDATOR = SCRIPTS / "validate_api_surface_v1.py"
SHARED_POLICY = SCRIPTS / "machine_publication_policy.py"
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
SYMBOL_FIELDS = {
    "const": {"kind", "name", "type", "signature", "value_kind", "value"},
    "func": {"kind", "name", "type", "signature", "type_parameters"},
    "method": {"kind", "name", "type", "signature", "receiver"},
    "type": {
        "kind",
        "name",
        "type",
        "signature",
        "type_form",
        "type_parameters",
    },
    "var": {"kind", "name", "type", "signature"},
}
KNOWN_FINGERPRINTS = {
    "kinds-types-signatures.json": "1389d98ef6f7d6ad458cecc89f54f4769f6cd406004f0eaf3a405ab955f45771",
    "packages-and-symbols.json": "492c7ec2e865dc21afd5c0dba9778efa85eed443a105ccdc32efa128717c010e",
}


class DuplicateJSONKeyError(ValueError):
    pass


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateJSONKeyError(key)
        result[key] = value
    return result


def load_json_strict(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_unique_object)


def load_first_json_value(path: Path) -> tuple[Any, str]:
    text = path.read_text(encoding="utf-8")
    start = len(text) - len(text.lstrip(" \t\r\n"))
    document, end = json.JSONDecoder().raw_decode(text, start)
    return document, text[end:]


def copy_repo(tmp_path: Path) -> Path:
    destination = tmp_path / "repo"
    shutil.copytree(
        REPO,
        destination,
        ignore=shutil.ignore_patterns(".git", ".pytest_cache", "__pycache__"),
    )
    return destination


def run_validator(repo: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(API_VALIDATOR), "--repo", str(repo)],
        cwd=repo,
        check=False,
        text=True,
        capture_output=True,
    )


def run_document_validator(
    path: Path,
    *,
    corpus: bool = False,
) -> subprocess.CompletedProcess[str]:
    command = [sys.executable, str(API_VALIDATOR), "--document", str(path)]
    if corpus:
        command.append("--corpus")
    return subprocess.run(
        command,
        cwd=REPO,
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


def write_json(path: Path, document: Any) -> None:
    path.write_text(json.dumps(document, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def find_symbol(document: dict[str, Any], kind: str, name: str | None = None) -> dict[str, Any]:
    return next(
        symbol
        for package in document["packages"]
        for symbol in package["symbols"]
        if symbol["kind"] == kind and (name is None or symbol["name"] == name)
    )


def render_parameters(parameters: list[dict[str, str]]) -> str:
    if not parameters:
        return ""
    return "[" + ", ".join(f"{item['name']} {item['constraint']}" for item in parameters) + "]"


def derive_signature(symbol: dict[str, Any]) -> str:
    kind = symbol["kind"]
    name = symbol["name"]
    type_text = symbol["type"]
    if kind == "const":
        if type_text.startswith("untyped "):
            return f"const {name} = {symbol['value']}"
        return f"const {name} {type_text} = {symbol['value']}"
    if kind == "var":
        return f"var {name} {type_text}"
    if kind == "type":
        equals = " =" if symbol["type_form"] == "alias" else ""
        return f"type {name}{render_parameters(symbol['type_parameters'])}{equals} {type_text}"
    if kind == "func":
        return f"func {name}{render_parameters(symbol['type_parameters'])}{type_text[4:]}"
    receiver = symbol["receiver"]
    arguments = (
        "[" + ", ".join(receiver["type_parameters"]) + "]"
        if receiver["type_parameters"]
        else ""
    )
    pointer = "*" if receiver["pointer"] else ""
    return f"func ({pointer}{receiver['base']}{arguments}) {name}{type_text[4:]}"


def symbol_order_key(symbol: dict[str, Any]) -> tuple[bytes, bytes, bytes]:
    receiver = symbol.get("receiver", {})
    return tuple(
        value.encode("utf-8")
        for value in (symbol["kind"], receiver.get("base", ""), symbol["name"])
    )


def package_order_key(package: dict[str, Any]) -> tuple[bytes, bytes]:
    return (package["path"].encode("utf-8"), package["name"].encode("utf-8"))


def canonical_fingerprint_independent(document: dict[str, Any]) -> str:
    projection = copy.deepcopy(document)
    projection.pop("fixture", None)
    for package in projection["packages"]:
        for symbol in package["symbols"]:
            symbol.pop("signature")
    encoded = json.dumps(
        projection,
        ensure_ascii=False,
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def document_field_paths(value: Any, path: tuple[str | int, ...] = ()) -> list[tuple[str | int, ...]]:
    paths: list[tuple[str | int, ...]] = []
    if isinstance(value, dict):
        for key, item in value.items():
            item_path = path + (key,)
            paths.append(item_path)
            paths.extend(document_field_paths(item, item_path))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            item_path = path + (index,)
            paths.append(item_path)
            paths.extend(document_field_paths(item, item_path))
    return paths


def invalid_field_values(value: Any) -> tuple[Any, ...]:
    if isinstance(value, bool):
        return (None, 7, [], {}, "wrong")
    if type(value) is int:
        return (None, True, 7.5, [], {}, "wrong")
    if isinstance(value, str):
        return (None, True, 7, [], {}, "\twrong")
    if isinstance(value, list):
        return (None, True, 7, [None], {}, "wrong")
    if isinstance(value, dict):
        return (None, True, 7, [], {}, "wrong")
    raise AssertionError(f"unsupported fixture field type: {type(value)!r}")


def replace_document_path(
    document: dict[str, Any],
    path: tuple[str | int, ...],
    replacement: Any,
) -> None:
    target: Any = document
    for component in path[:-1]:
        target = target[component]
    target[path[-1]] = replacement


class APISurfaceV1ContractTests(unittest.TestCase):
    def assert_mutation_rejected(
        self,
        mutation: Callable[[dict[str, Any]], None],
        category: str,
        *,
        fixture: str = "kinds-types-signatures.json",
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = copy_repo(Path(tmp))
            target = repo / "api" / "fixtures" / "v1" / "positive" / fixture
            document = load_json_strict(target)
            mutation(document)
            write_json(target, document)
            result = run_validator(repo)
            self.assertEqual(result.returncode, 1, result.stderr)
            self.assertIn(category, result.stderr)

    def test_contract_paths_and_exact_fixture_allowlists(self) -> None:
        for path in (SCHEMA, REFERENCE, API_VALIDATOR, POLICY_VALIDATOR, SHARED_POLICY):
            self.assertTrue(path.is_file(), path)
            self.assertFalse(path.is_symlink(), path)
        self.assertEqual({path.name for path in positive_paths()}, REQUIRED_POSITIVE_FIXTURES)
        self.assertEqual(
            {path.name for path in NEGATIVE_FIXTURES.glob("*.json")},
            REQUIRED_NEGATIVE_FIXTURES,
        )

    def test_schema_identity_version_and_closed_root_are_stable(self) -> None:
        schema = load_json_strict(SCHEMA)
        self.assertEqual(schema["$schema"], "https://json-schema.org/draft/2020-12/schema")
        self.assertEqual(schema["$id"], SCHEMA_URI)
        self.assertEqual(schema["schema_id"], SCHEMA_ID)
        self.assertEqual(schema["schema_version"], SCHEMA_VERSION)
        self.assertEqual(schema["type"], "object")
        self.assertIs(schema["additionalProperties"], False)
        self.assertEqual(set(schema["required"]), {"schema_id", "schema_version", "packages"})
        self.assertEqual(schema["properties"]["schema_id"]["const"], SCHEMA_ID)
        self.assertEqual(schema["properties"]["schema_version"], {"type": "integer", "const": 1})

    def test_schema_uses_a_closed_oneof_for_every_symbol_kind(self) -> None:
        schema = load_json_strict(SCHEMA)
        definitions = schema["$defs"]
        refs = {item["$ref"] for item in definitions["symbol"]["oneOf"]}
        expected_refs = {
            f"#/$defs/{kind}Symbol" for kind in ("const", "func", "method", "type", "var")
        }
        self.assertEqual(refs, expected_refs)
        for kind, fields in SYMBOL_FIELDS.items():
            definition = definitions[f"{kind}Symbol"]
            with self.subTest(kind=kind):
                self.assertEqual(set(definition["required"]), fields)
                self.assertEqual(set(definition["properties"]), fields)
                self.assertIs(definition["additionalProperties"], False)

    def test_schema_closes_type_parameters_and_structured_receivers(self) -> None:
        definitions = load_json_strict(SCHEMA)["$defs"]
        parameter = definitions["typeParameter"]
        receiver = definitions["receiver"]
        self.assertEqual(set(parameter["required"]), {"name", "constraint"})
        self.assertEqual(set(parameter["properties"]), {"name", "constraint"})
        self.assertIs(parameter["additionalProperties"], False)
        self.assertEqual(set(receiver["required"]), {"base", "pointer", "type_parameters"})
        self.assertEqual(set(receiver["properties"]), {"base", "pointer", "type_parameters"})
        self.assertIs(receiver["additionalProperties"], False)
        self.assertEqual(receiver["properties"]["pointer"]["type"], "boolean")
        self.assertIs(receiver["properties"]["type_parameters"]["uniqueItems"], True)
        self.assertNotIn("type_parameters", definitions["methodSymbol"]["properties"])

    def test_schema_and_fixtures_contain_no_null_contract_values(self) -> None:
        def visit(value: Any) -> None:
            self.assertIsNotNone(value)
            if isinstance(value, dict):
                for item in value.values():
                    visit(item)
            elif isinstance(value, list):
                for item in value:
                    visit(item)

        visit(load_json_strict(SCHEMA))
        for path in positive_paths():
            visit(load_json_strict(path))

    def test_reference_records_every_approved_boundary(self) -> None:
        normalized = " ".join(REFERENCE.read_text(encoding="utf-8").lower().split())
        phrases = (
            "oneof` union of five closed object shapes",
            "package-scope declaration identity is `(package path, name)`",
            "method identity is `(package path, receiver.base, name)`",
            "go/constant.value.exactstring",
            "untyped rune has structural `value_kind` `int`",
            "type_form` is `defined` or `alias`",
            "future ast-backed producer must prove go syntax",
            "does not parse go",
            "receiver arity must equal",
            "compatibility projection",
            "no self-referential hash field",
            "exact remainder `\\n!\\n`",
            "classification never uses `ipaddress.is_private`",
            "windows drive-absolute forms",
            "colons in otherwise valid package/import path strings remain permitted",
        )
        for phrase in phrases:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, normalized)

    def test_positive_fixtures_are_synthetic_and_boundary_valid(self) -> None:
        for path in positive_paths():
            with self.subTest(path=path.name):
                document, remainder = load_first_json_value(path)
                self.assertFalse(remainder.strip())
                self.assertEqual(document["schema_id"], SCHEMA_ID)
                self.assertIs(type(document["schema_version"]), int)
                self.assertEqual(document["schema_version"], 1)
                self.assertEqual(document["fixture"], {"synthetic": True, "runtime_claims": False})
                self.assertTrue(
                    all(
                        package["path"].startswith(SYNTHETIC_PACKAGE_PREFIX)
                        for package in document["packages"]
                    )
                )

    def test_positive_symbols_use_the_exact_per_kind_field_matrix(self) -> None:
        seen: set[str] = set()
        for path in positive_paths():
            document = load_json_strict(path)
            for package in document["packages"]:
                for symbol in package["symbols"]:
                    seen.add(symbol["kind"])
                    self.assertEqual(set(symbol), SYMBOL_FIELDS[symbol["kind"]])
        self.assertEqual(seen, set(SYMBOL_FIELDS))

    def test_positive_corpus_covers_exactstring_constant_vectors(self) -> None:
        document = load_json_strict(POSITIVE_FIXTURES / "kinds-types-signatures.json")
        constants = {
            symbol["name"]: symbol
            for symbol in document["packages"][0]["symbols"]
            if symbol["kind"] == "const"
        }
        vectors = {
            "BooleanDefault": ("untyped bool", "bool", "true"),
            "ComplexExact": (
                "untyped complex",
                "complex",
                "(12345678901234567890123456789/10000000000000000000000000000 + "
                "98765432109876543210987654321/10000000000000000000000000000i)",
            ),
            "FloatExact": (
                "untyped float",
                "float",
                "12345678901234567890123456789/10000000000000000000000000000",
            ),
            "IntegerExact": (
                "untyped int",
                "int",
                "123456789012345678901234567890123456789",
            ),
            "RuneExact": ("untyped rune", "int", "955"),
            "StringExact": ("untyped string", "string", '"line\\n\\"quoted\\""'),
            "StringSpacesExact": ("untyped string", "string", '"left  right"'),
            "TypedLimit": ("uint64", "int", "18446744073709551615"),
        }
        self.assertEqual(set(constants), set(vectors))
        for name, (type_text, value_kind, value) in vectors.items():
            with self.subTest(name=name):
                symbol = constants[name]
                self.assertEqual((symbol["type"], symbol["value_kind"], symbol["value"]), (type_text, value_kind, value))
                self.assertEqual(symbol["signature"], derive_signature(symbol))

    def test_positive_corpus_covers_generics_aliases_and_cross_parameter_constraints(self) -> None:
        document = load_json_strict(POSITIVE_FIXTURES / "kinds-types-signatures.json")
        convert = find_symbol(document, "func", "Convert")
        catalog = find_symbol(document, "type", "Catalog")
        pair = find_symbol(document, "type", "Pair")
        self.assertEqual(convert["type_parameters"][1], {"name": "S", "constraint": "interface{ ~[]T }"})
        self.assertEqual(catalog["type_form"], "defined")
        self.assertEqual(pair["type_form"], "alias")
        self.assertTrue(catalog["type_parameters"])
        self.assertTrue(pair["type_parameters"])
        for symbol in (convert, catalog, pair):
            self.assertEqual(symbol["signature"], derive_signature(symbol))

    def test_positive_corpus_covers_value_and_pointer_generic_receivers(self) -> None:
        document = load_json_strict(POSITIVE_FIXTURES / "kinds-types-signatures.json")
        methods = [
            symbol
            for symbol in document["packages"][0]["symbols"]
            if symbol["kind"] == "method"
        ]
        self.assertEqual({method["receiver"]["pointer"] for method in methods}, {False, True})
        types = {
            symbol["name"]: symbol
            for symbol in document["packages"][0]["symbols"]
            if symbol["kind"] == "type"
        }
        for method in methods:
            receiver = method["receiver"]
            self.assertIn(receiver["base"], types)
            self.assertEqual(len(receiver["type_parameters"]), len(types[receiver["base"]]["type_parameters"]))
            self.assertEqual(method["signature"], derive_signature(method))

    def test_positive_packages_and_symbols_are_canonically_ordered(self) -> None:
        for path in positive_paths():
            document = load_json_strict(path)
            self.assertEqual(document["packages"], sorted(document["packages"], key=package_order_key))
            for package in document["packages"]:
                self.assertEqual(package["symbols"], sorted(package["symbols"], key=symbol_order_key))
                self.assertEqual(package["path"], unicodedata.normalize("NFC", package["path"]))

    def test_negative_fixtures_retain_exact_boundary_and_no_runtime_markers(self) -> None:
        for path in sorted(NEGATIVE_FIXTURES.glob("*.json")):
            with self.subTest(path=path.name):
                document, remainder = load_first_json_value(path)
                self.assertEqual(document["schema_id"], SCHEMA_ID)
                self.assertEqual(document["schema_version"], 1)
                self.assertEqual(document["fixture"], {"synthetic": True, "runtime_claims": False})
                self.assertTrue(document["packages"])
                self.assertTrue(
                    all(package["path"].startswith(SYNTHETIC_PACKAGE_PREFIX) for package in document["packages"])
                )
                self.assertEqual(remainder, "\n!\n" if path.name == "malformed.json" else "\n")

    def test_negative_duplicate_identity_is_cross_kind_package_identity(self) -> None:
        document = load_json_strict(negative_path("duplicate-identity.json"))
        symbols = document["packages"][0]["symbols"]
        self.assertEqual({symbol["kind"] for symbol in symbols}, {"type", "var"})
        self.assertEqual({symbol["name"] for symbol in symbols}, {"Example"})

    def test_negative_duplicate_key_and_malformed_shapes_are_exact(self) -> None:
        with self.assertRaises(DuplicateJSONKeyError):
            load_json_strict(negative_path("duplicate-json-key.json"))
        with self.assertRaises(json.JSONDecodeError):
            load_json_strict(negative_path("malformed.json"))
        document, remainder = load_first_json_value(negative_path("malformed.json"))
        self.assertIsInstance(document, dict)
        self.assertEqual(remainder, "\n!\n")

    def test_standalone_validator_accepts_corpus_deterministically(self) -> None:
        first = run_validator(REPO)
        second = run_validator(REPO)
        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertEqual((first.stdout, first.stderr), (second.stdout, second.stderr))
        self.assertEqual(first.stdout.strip(), "api-surface-v1: valid")

    def test_extracted_document_mode_accepts_no_fixture_and_normal_package_path(self) -> None:
        document = load_json_strict(POSITIVE_FIXTURES / "kinds-types-signatures.json")
        document.pop("fixture")
        document["packages"][0]["path"] = "github.com/Project-Helianthus/helianthus-eebus/api"
        self.assertEqual(document_diagnostics(document), set())

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "extracted.json"
            write_json(path, document)
            result = run_document_validator(path)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout.strip(), "api-surface-v1 document: valid")

    def test_document_mode_rejects_drive_absolute_paths_without_fingerprinting(self) -> None:
        source = load_json_strict(POSITIVE_FIXTURES / "kinds-types-signatures.json")
        source.pop("fixture")
        for package_path in ("C:/module/pkg", "c:/module/pkg", "C:\\module\\pkg"):
            with self.subTest(package_path=package_path), tempfile.TemporaryDirectory() as tmp:
                document = copy.deepcopy(source)
                document["packages"][0]["path"] = package_path
                path = Path(tmp) / "document.json"
                write_json(path, document)

                result = run_document_validator(path)

                self.assertEqual(result.returncode, 1)
                self.assertEqual(result.stdout, "")
                self.assertEqual(result.stderr, "document.json: invalid package path\n")
                self.assertNotIn(str(path.parent), result.stderr)
                self.assertNotIn(package_path, result.stderr)
                with self.assertRaisesRegex(ValueError, r"^invalid package path$"):
                    compatibility_fingerprint(document)

    def test_document_mode_accepts_non_drive_colon_paths_and_fingerprints_them(self) -> None:
        source = load_json_strict(POSITIVE_FIXTURES / "kinds-types-signatures.json")
        source.pop("fixture")
        package_paths = (
            "C:module/pkg",
            "cc:/module/pkg",
            "example.com:8443/module/pkg",
        )
        for package_path in package_paths:
            with self.subTest(package_path=package_path), tempfile.TemporaryDirectory() as tmp:
                document = copy.deepcopy(source)
                document["packages"][0]["path"] = package_path
                path = Path(tmp) / "document.json"
                write_json(path, document)

                result = run_document_validator(path)

                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stdout.strip(), "api-surface-v1 document: valid")
                self.assertRegex(compatibility_fingerprint(document), r"^[0-9a-f]{64}$")

    def test_extracted_document_mode_rejects_invalid_optional_fixture(self) -> None:
        source = load_json_strict(POSITIVE_FIXTURES / "packages-and-symbols.json")
        invalid_fixtures = (
            None,
            {"synthetic": False, "runtime_claims": False},
            {"synthetic": True, "runtime_claims": False, "extra": True},
        )
        for fixture in invalid_fixtures:
            with self.subTest(fixture=fixture):
                document = copy.deepcopy(source)
                document["fixture"] = fixture
                self.assertTrue(document_diagnostics(document))

    def test_corpus_mode_requires_fixture_and_synthetic_package_prefix(self) -> None:
        document = load_json_strict(POSITIVE_FIXTURES / "kinds-types-signatures.json")
        document.pop("fixture")
        document["packages"][0]["path"] = "github.com/Project-Helianthus/helianthus-eebus/api"
        self.assertEqual(document_diagnostics(document), set())
        self.assertEqual(
            document_diagnostics(document, corpus=True),
            {"missing required field", "non-synthetic fixture package"},
        )

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "corpus.json"
            write_json(path, document)
            result = run_document_validator(path, corpus=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertNotIn(str(path.parent), result.stderr)
            self.assertEqual(
                set(result.stderr.splitlines()),
                {
                    "corpus.json: missing required field",
                    "corpus.json: non-synthetic fixture package",
                },
            )

    def test_every_negative_fixture_must_remain_invalid(self) -> None:
        valid_bytes = positive_paths()[0].read_bytes()
        for path in sorted(NEGATIVE_FIXTURES.glob("*.json")):
            with self.subTest(path=path.name), tempfile.TemporaryDirectory() as tmp:
                repo = copy_repo(Path(tmp))
                target = repo / path.relative_to(REPO)
                target.write_bytes(valid_bytes)
                result = run_validator(repo)
                self.assertEqual(result.returncode, 1, result.stderr)
                self.assertIn(path.relative_to(REPO).as_posix(), result.stderr)

    def test_negative_fixtures_reject_unrelated_added_diagnostics(self) -> None:
        for fixture_name in ("duplicate-identity.json", "malformed.json"):
            with self.subTest(fixture=fixture_name), tempfile.TemporaryDirectory() as tmp:
                repo = copy_repo(Path(tmp))
                target = negative_path(fixture_name, repo)
                document, _ = load_first_json_value(target)
                document["extra"] = "synthetic"
                write_json(target, document)
                if fixture_name == "malformed.json":
                    target.write_text(target.read_text(encoding="utf-8") + "!\n", encoding="utf-8")
                result = run_validator(repo)
                self.assertEqual(result.returncode, 1, result.stderr)
                self.assertIn("unexpected negative category: unknown field", result.stderr)

    def test_validator_rejects_a_null_at_every_structural_level(self) -> None:
        mutations = (
            lambda document: document.__setitem__("fixture", None),
            lambda document: document["packages"][0].__setitem__("name", None),
            lambda document: find_symbol(document, "const").__setitem__("value", None),
            lambda document: find_symbol(document, "method")["receiver"]["type_parameters"].__setitem__(0, None),
        )
        for mutation in mutations:
            with self.subTest(mutation=mutation):
                self.assert_mutation_rejected(mutation, "null value")

    def test_validator_enforces_each_per_kind_required_field(self) -> None:
        cases = (
            ("const", "value"),
            ("func", "type_parameters"),
            ("method", "receiver"),
            ("type", "type_form"),
            ("var", "signature"),
        )
        for kind, field in cases:
            with self.subTest(kind=kind, field=field):
                self.assert_mutation_rejected(
                    lambda document, kind=kind, field=field: find_symbol(document, kind).pop(field),
                    "missing required field",
                )

    def test_validator_rejects_cross_kind_extra_fields(self) -> None:
        cases = (
            ("const", "type_parameters", []),
            ("func", "receiver", {"base": "Catalog", "pointer": False, "type_parameters": ["T"]}),
            ("method", "type_parameters", []),
            ("type", "value", "1"),
            ("var", "value_kind", "int"),
        )
        for kind, field, value in cases:
            with self.subTest(kind=kind, field=field):
                self.assert_mutation_rejected(
                    lambda document, kind=kind, field=field, value=value: find_symbol(document, kind).__setitem__(field, value),
                    "unknown field",
                )

    def test_validator_rejects_duplicate_declaration_type_parameter_names(self) -> None:
        def mutation(document: dict[str, Any]) -> None:
            symbol = find_symbol(document, "func", "Convert")
            symbol["type_parameters"][1]["name"] = "T"
            symbol["signature"] = derive_signature(symbol)

        self.assert_mutation_rejected(mutation, "duplicate type parameter")

    def test_validator_rejects_duplicate_receiver_type_parameter_names(self) -> None:
        def mutation(document: dict[str, Any]) -> None:
            symbol = find_symbol(document, "method", "Values")
            symbol["receiver"]["type_parameters"] = ["T", "T"]
            symbol["signature"] = derive_signature(symbol)

        self.assert_mutation_rejected(mutation, "duplicate type parameter")

    def test_validator_preserves_ascii_identifier_and_keyword_rules(self) -> None:
        cases = (
            lambda document: find_symbol(document, "type").__setitem__("name", "Bad-Name"),
            lambda document: find_symbol(document, "func")["type_parameters"][0].__setitem__("name", "func"),
            lambda document: find_symbol(document, "method")["receiver"].__setitem__("base", "9Bad"),
        )
        for mutation in cases:
            with self.subTest(mutation=mutation):
                self.assert_mutation_rejected(mutation, "invalid")

    def test_validator_rejects_unresolved_receivers(self) -> None:
        def mutation(document: dict[str, Any]) -> None:
            method = find_symbol(document, "method", "Lookup")
            method["receiver"]["base"] = "Missing"
            method["signature"] = derive_signature(method)

        self.assert_mutation_rejected(mutation, "unresolved receiver")

    def test_validator_rejects_receiver_arity_mismatch(self) -> None:
        def mutation(document: dict[str, Any]) -> None:
            method = find_symbol(document, "method", "Lookup")
            method["receiver"]["type_parameters"] = []
            method["signature"] = derive_signature(method)

        self.assert_mutation_rejected(mutation, "receiver arity mismatch")

    def test_validator_package_identity_is_independent_of_kind(self) -> None:
        def mutation(document: dict[str, Any]) -> None:
            variable = find_symbol(document, "var")
            variable["name"] = "Catalog"
            variable["signature"] = derive_signature(variable)

        self.assert_mutation_rejected(mutation, "duplicate symbol identity")

    def test_validator_method_identity_is_independent_of_pointer_and_receiver_names(self) -> None:
        def mutation(document: dict[str, Any]) -> None:
            method = find_symbol(document, "method", "Values")
            method["name"] = "Lookup"
            method["receiver"] = {
                "base": "Catalog",
                "pointer": False,
                "type_parameters": ["Element"],
            }
            method["signature"] = derive_signature(method)

        self.assert_mutation_rejected(mutation, "duplicate symbol identity")

    def test_validator_derives_every_kind_signature(self) -> None:
        for kind in SYMBOL_FIELDS:
            with self.subTest(kind=kind):
                self.assert_mutation_rejected(
                    lambda document, kind=kind: find_symbol(document, kind).__setitem__(
                        "signature", "var Different invalid"
                    ),
                    "cross-field mismatch",
                )

    def test_validator_derives_untyped_and_typed_constant_signatures(self) -> None:
        document = load_json_strict(POSITIVE_FIXTURES / "kinds-types-signatures.json")
        untyped = find_symbol(document, "const", "IntegerExact")
        typed = find_symbol(document, "const", "TypedLimit")
        self.assertEqual(untyped["signature"], f"const IntegerExact = {untyped['value']}")
        self.assertEqual(typed["signature"], f"const TypedLimit uint64 = {typed['value']}")

    def test_exactstring_repeated_spaces_are_lossless_only_inside_constant_values(self) -> None:
        document = load_json_strict(POSITIVE_FIXTURES / "kinds-types-signatures.json")
        constant = find_symbol(document, "const", "StringSpacesExact")
        self.assertEqual(constant["value"], '"left  right"')
        self.assertEqual(constant["signature"], 'const StringSpacesExact = "left  right"')
        self.assertEqual(document_diagnostics(document, corpus=True), set())

        cases = (
            (
                lambda candidate: find_symbol(candidate, "const", "BooleanDefault").__setitem__(
                    "signature", "const  BooleanDefault = true"
                ),
                "cross-field mismatch",
            ),
            (
                lambda candidate: find_symbol(candidate, "const", "TypedLimit").__setitem__(
                    "type", "uint64  alias"
                ),
                "invalid normalized text",
            ),
            (
                lambda candidate: find_symbol(candidate, "func", "NewCatalog").__setitem__(
                    "signature", "func  NewCatalog[T any]([]T) *Catalog[T]"
                ),
                "invalid normalized text",
            ),
            (
                lambda candidate: find_symbol(candidate, "func", "Convert")["type_parameters"][0].__setitem__(
                    "constraint", "interface{  any }"
                ),
                "invalid normalized text",
            ),
        )
        for mutation, category in cases:
            with self.subTest(category=category):
                candidate = copy.deepcopy(document)
                mutation(candidate)
                self.assertIn(category, document_diagnostics(candidate, corpus=True))

    def test_constant_value_and_signature_reject_non_lossless_text(self) -> None:
        source = load_json_strict(POSITIVE_FIXTURES / "kinds-types-signatures.json")
        invalid_values = (
            ' "trimmed" ',
            '"control\tcharacter"',
            '"line\u2028separator"',
            '"paragraph\u2029separator"',
            '"non-nfc e\u0301"',
            '"surrogate \ud800"',
        )
        for value in invalid_values:
            with self.subTest(value=ascii(value)):
                document = copy.deepcopy(source)
                constant = find_symbol(document, "const", "StringExact")
                constant["value"] = value
                constant["signature"] = derive_signature(constant)
                diagnostics = document_diagnostics(document, corpus=True)
                self.assertIn("invalid constant value", diagnostics)

    def test_document_diagnostics_wrong_type_sweep_is_total_and_deterministic(self) -> None:
        source = load_json_strict(POSITIVE_FIXTURES / "kinds-types-signatures.json")
        mutation_count = 0
        replacement_types: set[str] = set()
        for path in document_field_paths(source):
            target: Any = source
            for component in path:
                target = target[component]
            for replacement in invalid_field_values(target):
                with self.subTest(path=path, replacement=type(replacement).__name__):
                    document = copy.deepcopy(source)
                    replace_document_path(document, path, copy.deepcopy(replacement))
                    first = document_diagnostics(document, corpus=True)
                    second = document_diagnostics(document, corpus=True)
                    self.assertEqual(first, second)
                    self.assertGreater(len(first), 0)
                    for category in first:
                        self.assertNotIn("Traceback", category)
                        self.assertNotIn(str(REPO), category)
                        self.assertNotIn(":", category)
                    mutation_count += 1
                    if replacement is None:
                        replacement_types.add("null")
                    elif isinstance(replacement, bool):
                        replacement_types.add("bool")
                    elif isinstance(replacement, (int, float)):
                        replacement_types.add("number")
                    elif isinstance(replacement, list):
                        replacement_types.add("list")
                    elif isinstance(replacement, dict):
                        replacement_types.add("object")
                    elif isinstance(replacement, str):
                        replacement_types.add("wrong string")
        self.assertGreater(mutation_count, 700)
        self.assertEqual(
            replacement_types,
            {"null", "bool", "number", "list", "object", "wrong string"},
        )

    def test_validator_rejects_untyped_type_to_value_kind_mismatch(self) -> None:
        self.assert_mutation_rejected(
            lambda document: find_symbol(document, "const", "RuneExact").__setitem__("value_kind", "string"),
            "cross-field mismatch",
        )

    def test_validator_leaves_go_syntax_and_exactstring_proof_to_ast_producer(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = copy_repo(Path(tmp))
            target = repo / "api" / "fixtures" / "v1" / "positive" / "kinds-types-signatures.json"
            document = load_json_strict(target)
            constant = find_symbol(document, "const", "TypedLimit")
            constant["type"] = "not-a-go-type"
            constant["value"] = "not a go constant"
            constant["signature"] = derive_signature(constant)
            function = find_symbol(document, "func", "Convert")
            function["type_parameters"][0]["constraint"] = "not a constraint"
            function["signature"] = derive_signature(function)
            write_json(target, document)
            result = run_validator(repo)
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_symbol_ordering_uses_receiver_base_not_pointer_or_parameter_spelling(self) -> None:
        document = load_json_strict(POSITIVE_FIXTURES / "kinds-types-signatures.json")
        lookup = find_symbol(document, "method", "Lookup")
        original = symbol_order_key(lookup)
        lookup["receiver"]["pointer"] = False
        lookup["receiver"]["type_parameters"] = ["Element"]
        self.assertEqual(symbol_order_key(lookup), original)

    def test_known_compatibility_fingerprints_are_pinned_independently(self) -> None:
        for path in positive_paths():
            document = load_json_strict(path)
            expected = KNOWN_FINGERPRINTS[path.name]
            with self.subTest(path=path.name):
                self.assertEqual(canonical_fingerprint_independent(document), expected)
                self.assertEqual(compatibility_fingerprint(document), expected)

    def test_projection_excludes_only_fixture_and_derived_signature(self) -> None:
        document = load_json_strict(POSITIVE_FIXTURES / "packages-and-symbols.json")
        projection = compatibility_projection(document)
        self.assertNotIn("fixture", projection)
        for package in projection["packages"]:
            for symbol in package["symbols"]:
                self.assertNotIn("signature", symbol)
        source_symbol = find_symbol(document, "const")
        projected_symbol = next(
            symbol
            for package in projection["packages"]
            for symbol in package["symbols"]
            if symbol["kind"] == "const"
        )
        self.assertEqual(set(projected_symbol), set(source_symbol) - {"signature"})

    def test_fingerprint_ignores_fixture_and_signature_but_changes_for_contract_fields(self) -> None:
        document = load_json_strict(POSITIVE_FIXTURES / "packages-and-symbols.json")
        expected = compatibility_fingerprint(document)
        derived_only = copy.deepcopy(document)
        derived_only["fixture"] = {"synthetic": False, "runtime_claims": True}
        find_symbol(derived_only, "func")["signature"] = "not derived"
        self.assertEqual(compatibility_fingerprint(derived_only), expected)
        changed = copy.deepcopy(document)
        find_symbol(changed, "const")["value"] = "4"
        self.assertNotEqual(compatibility_fingerprint(changed), expected)

    def test_fingerprint_canonicalizes_schema_equivalent_version_numbers(self) -> None:
        document = load_json_strict(POSITIVE_FIXTURES / "packages-and-symbols.json")
        equivalent = copy.deepcopy(document)
        equivalent["schema_version"] = 1.0
        self.assertEqual(compatibility_fingerprint(equivalent), compatibility_fingerprint(document))

    def test_schema_has_no_self_referential_fingerprint_field(self) -> None:
        schema = load_json_strict(SCHEMA)
        self.assertNotIn("fingerprint", schema["properties"])
        self.assertNotIn("hash", schema["properties"])

    def test_duplicate_key_boundaries_check_every_occurrence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = copy_repo(Path(tmp))
            target = negative_path("duplicate-json-key.json", repo)
            text = target.read_text(encoding="utf-8")
            target.write_text(
                text.replace(
                    f'"schema_id": "{SCHEMA_ID}",\n  "schema_id": "{SCHEMA_ID}"',
                    f'"schema_id": "wrong",\n  "schema_id": "{SCHEMA_ID}"',
                    1,
                ),
                encoding="utf-8",
            )
            result = run_validator(repo)
            self.assertEqual(result.returncode, 1, result.stderr)
            self.assertIn("negative fixture boundary mismatch", result.stderr)

    def test_validator_rejects_non_utf8_machine_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = copy_repo(Path(tmp))
            target = repo / positive_paths()[0].relative_to(REPO)
            target.write_bytes(b"\xff")
            result = run_validator(repo)
            self.assertEqual(result.returncode, 1, result.stderr)
            self.assertIn("invalid UTF-8", result.stderr)

    def test_validator_accepts_schema_equivalent_numeric_version(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = copy_repo(Path(tmp))
            target = repo / positive_paths()[0].relative_to(REPO)
            target.write_text(
                target.read_text(encoding="utf-8").replace('"schema_version": 1,', '"schema_version": 1.0,', 1),
                encoding="utf-8",
            )
            result = run_validator(repo)
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_validator_rejects_boolean_version_ambiguity(self) -> None:
        self.assert_mutation_rejected(
            lambda document: document.__setitem__("schema_version", True),
            "schema identity mismatch",
        )

    def test_publication_markers_are_scanned_raw_and_after_json_decoding(self) -> None:
        cases = (
            ("private path", "/Users/" + "synthetic-user/input.go"),
            ("private network", "peer " + "127." + "0.0.1"),
            ("network address", "peer " + "203." + "0.113.1"),
            ("private identifier", "account_" + "id: synthetic"),
            ("household data", "household_" + "schedule: synthetic"),
            ("raw evidence", "raw-" + "evidence: synthetic"),
            ("source contamination", "vendor_" + "restricted"),
        )
        for category, value in cases:
            with self.subTest(category=category):
                def mutation(document: dict[str, Any], value: str = value) -> None:
                    symbol = find_symbol(document, "const", "TypedLimit")
                    symbol["value"] = value
                    symbol["signature"] = derive_signature(symbol)

                self.assert_mutation_rejected(mutation, category)

    def test_failure_diagnostics_are_repeatable_path_only_and_value_safe(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = copy_repo(Path(tmp))
            target = repo / positive_paths()[0].relative_to(REPO)
            document = load_json_strict(target)
            sensitive = "/Users/" + "diagnostic-secret/private.go"
            symbol = find_symbol(document, "const")
            symbol["value"] = sensitive
            symbol["signature"] = derive_signature(symbol)
            write_json(target, document)
            first = run_validator(repo)
            second = run_validator(repo)
            self.assertEqual((first.stdout, first.stderr), (second.stdout, second.stderr))
            self.assertNotIn(sensitive, first.stderr)
            self.assertNotIn(str(repo), first.stderr)
            for line in first.stderr.splitlines():
                self.assertRegex(line, r"^api/(?:schema|fixtures)/")

    def test_repository_policy_accepts_only_the_exact_api_machine_allowlist(self) -> None:
        expected = {SCHEMA.relative_to(REPO)} | {
            path.relative_to(REPO)
            for path in list(positive_paths()) + list(NEGATIVE_FIXTURES.glob("*.json"))
        }
        actual = {
            path.relative_to(REPO)
            for path in (REPO / "api").rglob("*")
            if path.is_file() and path.suffix.lower() not in {".md", ".markdown", ".mdown", ".mkd", ".mkdn"}
        }
        self.assertEqual(actual, expected)
        result = run_policy_validator(REPO)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_repository_policy_rejects_rogue_api_machine_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = copy_repo(Path(tmp))
            target = repo / "api" / "schema" / "extra.json"
            target.write_text("{}\n", encoding="utf-8")
            result = run_policy_validator(repo)
            self.assertEqual(result.returncode, 1, result.stderr)
            self.assertIn("api/schema/extra.json: path is not in the API machine artifact allowlist", result.stderr)

    def test_ci_local_runs_api_validator_before_unit_tests(self) -> None:
        lines = (REPO / "scripts" / "ci_local.sh").read_text(encoding="utf-8").splitlines()
        commands = [
            (index, shlex.split(line))
            for index, line in enumerate(lines)
            if line.strip() and not line.lstrip().startswith("#")
        ]
        validator_lines = [index for index, command in commands if "scripts/validate_api_surface_v1.py" in command]
        test_lines = [index for index, command in commands if command[:3] == ["python3", "-m", "unittest"]]
        self.assertEqual(len(validator_lines), 1)
        self.assertEqual(len(test_lines), 1)
        self.assertLess(validator_lines[0], test_lines[0])


if __name__ == "__main__":
    unittest.main()
