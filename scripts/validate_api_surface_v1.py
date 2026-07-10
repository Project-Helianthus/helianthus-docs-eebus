#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import unicodedata
from decimal import Decimal
from pathlib import Path
from typing import Any

from machine_publication_policy import (
    COMPLETE,
    INVALID_UTF8,
    MALFORMED_SENTINEL,
    TRAILING_CONTENT,
    JSONObject,
    MachineJSONResult,
    decode_machine_json,
    machine_publication_diagnostics,
    object_values,
)


SCHEMA_ID = "helianthus.eebus.api-surface.v1"
SCHEMA_URI = "urn:helianthus:eebus:api-surface:v1"
SCHEMA_VERSION = 1
SYNTHETIC_PREFIX = "example.invalid/helianthus/synthetic/"
SCHEMA_REL = Path("api/schema/helianthus.eebus.api-surface.v1.schema.json")
POSITIVE_REL = Path("api/fixtures/v1/positive")
NEGATIVE_REL = Path("api/fixtures/v1/negative")
SCHEMA_SHA256 = "08987ef7faabea579ccab4f5d296727ee1bab8e087607b467db024ceeea2bb65"

SYMBOL_KINDS = {"const", "func", "method", "type", "var"}
VALUE_KINDS = {"bool", "string", "int", "float", "complex"}
UNTYPED_VALUE_KINDS = {
    "untyped bool": "bool",
    "untyped rune": "int",
    "untyped int": "int",
    "untyped float": "float",
    "untyped complex": "complex",
    "untyped string": "string",
}
GO_KEYWORDS = {
    "break",
    "case",
    "chan",
    "const",
    "continue",
    "default",
    "defer",
    "else",
    "fallthrough",
    "for",
    "func",
    "go",
    "goto",
    "if",
    "import",
    "interface",
    "map",
    "package",
    "range",
    "return",
    "select",
    "struct",
    "switch",
    "type",
    "var",
}
SYMBOL_FIELDS = {
    "const": {
        "required": {"kind", "name", "type", "signature", "value_kind", "value"},
        "allowed": {"kind", "name", "type", "signature", "value_kind", "value"},
    },
    "func": {
        "required": {"kind", "name", "type", "signature", "type_parameters"},
        "allowed": {"kind", "name", "type", "signature", "type_parameters"},
    },
    "method": {
        "required": {"kind", "name", "type", "signature", "receiver"},
        "allowed": {"kind", "name", "type", "signature", "receiver"},
    },
    "type": {
        "required": {
            "kind",
            "name",
            "type",
            "signature",
            "type_form",
            "type_parameters",
        },
        "allowed": {
            "kind",
            "name",
            "type",
            "signature",
            "type_form",
            "type_parameters",
        },
    },
    "var": {
        "required": {"kind", "name", "type", "signature"},
        "allowed": {"kind", "name", "type", "signature"},
    },
}
REQUIRED_POSITIVE = {"packages-and-symbols.json", "kinds-types-signatures.json"}
EXPECTED_NEGATIVE_DIAGNOSTICS = {
    "duplicate-identity.json": frozenset({"duplicate symbol identity"}),
    "duplicate-json-key.json": frozenset({"duplicate key"}),
    "implementation-dependency-type.json": frozenset({"implementation dependency type"}),
    "internal-package.json": frozenset({"internal package"}),
    "invalid-ordering.json": frozenset({"non-canonical ordering"}),
    "malformed.json": frozenset({"malformed JSON"}),
    "non-nfc.json": frozenset(
        {"invalid Go identifier", "invalid normalized text", "non-NFC value"}
    ),
    "unexported-declaration.json": frozenset({"unexported declaration"}),
    "unexported-receiver.json": frozenset({"unexported receiver"}),
    "unknown-field.json": frozenset({"unknown field"}),
}
ASCII_GO_IDENTIFIER_PATTERN = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
WINDOWS_DRIVE_ABSOLUTE_PATTERN = re.compile(r"[A-Za-z]:[/\\]")


def _check_fields(value: dict[str, Any], required: set[str], allowed: set[str]) -> set[str]:
    diagnostics: set[str] = set()
    if set(value) - allowed:
        diagnostics.add("unknown field")
    if required - set(value):
        diagnostics.add("missing required field")
    return diagnostics


def _is_nfc(value: str) -> bool:
    return value == unicodedata.normalize("NFC", value)


def _is_schema_integer(value: Any, expected: int) -> bool:
    return (type(value) is int and value == expected) or (
        isinstance(value, Decimal) and value == Decimal(expected)
    ) or (type(value) is float and value == float(expected))


def _has_control(value: str) -> bool:
    return any(unicodedata.category(char) == "Cc" for char in value)


def _has_line_or_paragraph_separator(value: str) -> bool:
    return any(unicodedata.category(char) in {"Zl", "Zp"} for char in value)


def _has_surrogate(value: str) -> bool:
    return any(unicodedata.category(char) == "Cs" for char in value)


def _text_diagnostics(value: str) -> set[str]:
    diagnostics: set[str] = set()
    if _has_surrogate(value):
        diagnostics.add("invalid Unicode scalar value")
    elif not _is_nfc(value):
        diagnostics.add("non-NFC value")
    if _has_control(value):
        diagnostics.add("control character")
    if _has_line_or_paragraph_separator(value):
        diagnostics.add("line or paragraph separator")
    return diagnostics


def _lossless_text_diagnostics(value: str) -> set[str]:
    diagnostics: set[str] = set()
    if _has_surrogate(value):
        diagnostics.add("invalid Unicode scalar value")
    if _has_control(value):
        diagnostics.add("control character")
    if _has_line_or_paragraph_separator(value):
        diagnostics.add("line or paragraph separator")
    return diagnostics


def _contains_null(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, JSONObject):
        return any(_contains_null(item) for _, item in value.pairs)
    if isinstance(value, list):
        return any(_contains_null(item) for item in value)
    if isinstance(value, dict):
        return any(_contains_null(item) for item in value.values())
    return False


def _is_go_identifier(value: str) -> bool:
    return (
        ASCII_GO_IDENTIFIER_PATTERN.fullmatch(value) is not None
        and value not in GO_KEYWORDS
    )


def _is_exported(value: str) -> bool:
    return _is_go_identifier(value) and "A" <= value[0] <= "Z"


def _normalized_text(value: Any, *, allow_repeated_spaces: bool = False) -> bool:
    return (
        isinstance(value, str)
        and bool(value)
        and value == value.strip()
        and not _has_surrogate(value)
        and _is_nfc(value)
        and not _has_control(value)
        and not _has_line_or_paragraph_separator(value)
        and (allow_repeated_spaces or "  " not in value)
    )


def _lossless_exact_text(value: Any) -> bool:
    return (
        isinstance(value, str)
        and bool(value)
        and value == value.strip()
        and not _has_surrogate(value)
        and not _has_control(value)
        and not _has_line_or_paragraph_separator(value)
    )


def _package_path_diagnostics(
    value: Any,
    *,
    path_kind: str,
    current_package_path: Any = None,
) -> set[str]:
    invalid_category = f"invalid {path_kind} path"
    internal_category = f"internal {path_kind}"
    diagnostics: set[str] = set()
    if not isinstance(value, str) or not value:
        return {invalid_category}

    diagnostics |= _text_diagnostics(value)
    components = value.split("/")
    if (
        value.startswith("/")
        or value.endswith("/")
        or WINDOWS_DRIVE_ABSOLUTE_PATTERN.match(value) is not None
        or "\\" in value
        or any(component in {"", ".", ".."} for component in components)
        or any(
            char.isspace() or unicodedata.category(char) in {"Cc", "Cs"}
            for char in value
        )
    ):
        diagnostics.add(invalid_category)
    if "internal" in components:
        diagnostics.add(internal_category)
    if path_kind == "import" and value == current_package_path:
        diagnostics.add("self import")
    return diagnostics


def _type_parameter_diagnostics(value: Any) -> tuple[set[str], list[str] | None]:
    diagnostics: set[str] = set()
    if not isinstance(value, list):
        return {"invalid type parameters"}, None

    names: list[str] = []
    structurally_valid = True
    for parameter in value:
        if not isinstance(parameter, dict):
            diagnostics.add("invalid type parameters")
            structurally_valid = False
            continue
        diagnostics |= _check_fields(
            parameter,
            {"name", "constraint"},
            {"name", "constraint"},
        )
        name = parameter.get("name")
        constraint = parameter.get("constraint")
        if not isinstance(name, str) or not _is_go_identifier(name):
            diagnostics.add("invalid Go identifier")
            structurally_valid = False
        else:
            diagnostics |= _text_diagnostics(name)
            names.append(name)
        if not _normalized_text(constraint):
            diagnostics.add("invalid normalized text")
            structurally_valid = False
            if isinstance(constraint, str):
                diagnostics |= _text_diagnostics(constraint)
        if isinstance(constraint, str) and "implementation.invalid/" in constraint:
            diagnostics.add("implementation dependency type")

    if len(names) != len(set(names)):
        diagnostics.add("duplicate type parameter")
    return diagnostics, names if structurally_valid and len(names) == len(value) else None


def _receiver_diagnostics(value: Any) -> tuple[set[str], dict[str, Any] | None]:
    diagnostics: set[str] = set()
    if not isinstance(value, dict):
        return {"invalid receiver"}, None
    diagnostics |= _check_fields(
        value,
        {"base", "pointer", "type_parameters"},
        {"base", "pointer", "type_parameters"},
    )
    base = value.get("base")
    pointer = value.get("pointer")
    parameters = value.get("type_parameters")
    valid = True
    if not isinstance(base, str) or not _is_go_identifier(base):
        diagnostics.add("invalid receiver")
        valid = False
    else:
        diagnostics |= _text_diagnostics(base)
        if not _is_exported(base):
            diagnostics.add("unexported receiver")
    if type(pointer) is not bool:
        diagnostics.add("invalid receiver")
        valid = False
    if not isinstance(parameters, list):
        diagnostics.add("invalid receiver")
        valid = False
    else:
        valid_parameters: list[str] = []
        for parameter in parameters:
            if not isinstance(parameter, str) or not _is_go_identifier(parameter):
                diagnostics.add("invalid receiver")
                valid = False
            else:
                diagnostics |= _text_diagnostics(parameter)
                valid_parameters.append(parameter)
        if len(valid_parameters) != len(set(valid_parameters)):
            diagnostics.add("duplicate type parameter")
    return diagnostics, value if valid else None


def _render_type_parameters(parameters: Any) -> str | None:
    diagnostics, names = _type_parameter_diagnostics(parameters)
    if diagnostics or names is None:
        return None
    if not parameters:
        return ""
    rendered = ", ".join(
        f"{parameter['name']} {parameter['constraint']}" for parameter in parameters
    )
    return f"[{rendered}]"


def _render_receiver(receiver: Any) -> str | None:
    diagnostics, valid = _receiver_diagnostics(receiver)
    if diagnostics & {
        "unknown field",
        "missing required field",
        "invalid receiver",
        "duplicate type parameter",
    } or valid is None:
        return None
    parameters = valid["type_parameters"]
    arguments = f"[{', '.join(parameters)}]" if parameters else ""
    pointer = "*" if valid["pointer"] else ""
    return f"{pointer}{valid['base']}{arguments}"


def _expected_signature(symbol: dict[str, Any]) -> str | None:
    kind = symbol.get("kind")
    name = symbol.get("name")
    type_text = symbol.get("type")
    if not isinstance(kind, str) or not isinstance(name, str) or not isinstance(type_text, str):
        return None
    if kind == "const":
        value = symbol.get("value")
        if not isinstance(value, str):
            return None
        if type_text in UNTYPED_VALUE_KINDS:
            return f"const {name} = {value}"
        return f"const {name} {type_text} = {value}"
    if kind == "var":
        return f"var {name} {type_text}"
    if kind == "type":
        parameters = _render_type_parameters(symbol.get("type_parameters"))
        type_form = symbol.get("type_form")
        if (
            parameters is None
            or not isinstance(type_form, str)
            or type_form not in {"defined", "alias"}
        ):
            return None
        operator = " =" if type_form == "alias" else ""
        return f"type {name}{parameters}{operator} {type_text}"
    if kind == "func" and type_text.startswith("func("):
        parameters = _render_type_parameters(symbol.get("type_parameters"))
        if parameters is None:
            return None
        return f"func {name}{parameters}{type_text[4:]}"
    if kind == "method" and type_text.startswith("func("):
        receiver = _render_receiver(symbol.get("receiver"))
        if receiver is None:
            return None
        return f"func ({receiver}) {name}{type_text[4:]}"
    return None


def _package_order_key(package: dict[str, Any]) -> tuple[bytes, bytes]:
    return (package["path"].encode("utf-8"), package["name"].encode("utf-8"))


def _import_order_key(package_import: dict[str, Any]) -> tuple[bytes, bytes]:
    return (
        package_import["qualifier"].encode("utf-8"),
        package_import["path"].encode("utf-8"),
    )


def _symbol_order_key(symbol: dict[str, Any]) -> tuple[bytes, bytes, bytes]:
    receiver = symbol.get("receiver")
    receiver_base = receiver.get("base", "") if isinstance(receiver, dict) else ""
    return tuple(
        value.encode("utf-8")
        for value in (symbol["kind"], receiver_base, symbol["name"])
    )


def compatibility_projection(document: dict[str, Any]) -> dict[str, Any]:
    packages: list[dict[str, Any]] = []
    for package in document["packages"]:
        symbols = [
            {key: value for key, value in symbol.items() if key != "signature"}
            for symbol in package["symbols"]
        ]
        packages.append(
            {
                "path": package["path"],
                "name": package["name"],
                "imports": package["imports"],
                "symbols": symbols,
            }
        )
    return {
        "schema_id": document["schema_id"],
        "schema_version": (
            SCHEMA_VERSION
            if _is_schema_integer(document["schema_version"], SCHEMA_VERSION)
            else document["schema_version"]
        ),
        "packages": packages,
    }


def compatibility_fingerprint(document: dict[str, Any]) -> str:
    projection = compatibility_projection(document)
    for package in projection["packages"]:
        package_path = package["path"]
        if _package_path_diagnostics(package_path, path_kind="package"):
            raise ValueError("invalid package path")
        imports = package["imports"]
        if not isinstance(imports, list):
            raise ValueError("invalid import collection")
        for package_import in imports:
            if not isinstance(package_import, dict):
                raise ValueError("invalid import shape")
            qualifier = package_import.get("qualifier")
            import_path = package_import.get("path")
            if (
                not isinstance(qualifier, str)
                or not _is_go_identifier(qualifier)
                or qualifier == "_"
            ):
                raise ValueError("invalid import qualifier")
            if _package_path_diagnostics(
                import_path,
                path_kind="import",
                current_package_path=package_path,
            ):
                raise ValueError("invalid import path")
    encoded = json.dumps(
        projection,
        ensure_ascii=False,
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def document_diagnostics(document: Any, *, corpus: bool = False) -> set[str]:
    diagnostics: set[str] = set()
    if not isinstance(document, dict):
        return {"invalid document shape"}
    null_scope = (
        document
        if corpus or "fixture" not in document
        else {key: value for key, value in document.items() if key != "fixture"}
    )
    if _contains_null(null_scope):
        diagnostics.add("null value")

    required_fields = {"schema_id", "schema_version", "packages"}
    if corpus:
        required_fields.add("fixture")
    diagnostics |= _check_fields(
        document,
        required_fields,
        {"schema_id", "schema_version", "fixture", "packages"},
    )
    if (
        document.get("schema_id") != SCHEMA_ID
        or not _is_schema_integer(document.get("schema_version"), SCHEMA_VERSION)
    ):
        diagnostics.add("schema identity mismatch")

    if "fixture" in document and not corpus:
        diagnostics.add("fixture forbidden in extracted document")
    elif corpus and "fixture" in document:
        fixture = document.get("fixture")
        if not isinstance(fixture, dict):
            diagnostics.add("invalid fixture metadata")
        else:
            diagnostics |= _check_fields(
                fixture,
                {"synthetic", "runtime_claims"},
                {"synthetic", "runtime_claims"},
            )
            if (
                fixture.get("synthetic") is not True
                or fixture.get("runtime_claims") is not False
            ):
                diagnostics.add("runtime claim or non-synthetic fixture")

    packages = document.get("packages")
    if not isinstance(packages, list) or not packages:
        diagnostics.add("invalid package collection")
        return diagnostics

    sortable_packages: list[dict[str, Any]] = []
    package_paths: set[str] = set()
    package_symbol_identities: set[tuple[str, str]] = set()
    method_identities: set[tuple[str, str, str]] = set()

    for package in packages:
        if not isinstance(package, dict):
            diagnostics.add("invalid package shape")
            continue
        diagnostics |= _check_fields(
            package,
            {"path", "name", "imports", "symbols"},
            {"path", "name", "imports", "symbols"},
        )
        path = package.get("path")
        name = package.get("name")
        imports = package.get("imports")
        symbols = package.get("symbols")

        diagnostics |= _package_path_diagnostics(path, path_kind="package")
        if not isinstance(path, str) or not path or not isinstance(name, str) or not name:
            diagnostics.add("invalid package identity")
        else:
            diagnostics |= _text_diagnostics(name)
            if corpus and not path.startswith(SYNTHETIC_PREFIX):
                diagnostics.add("non-synthetic fixture package")
            if not _is_go_identifier(name):
                diagnostics.add("invalid Go identifier")
            if path in package_paths:
                diagnostics.add("duplicate package identity")
            package_paths.add(path)

        if (
            isinstance(path, str)
            and isinstance(name, str)
            and not _has_surrogate(path)
            and not _has_surrogate(name)
        ):
            sortable_packages.append(package)

        if not isinstance(imports, list):
            diagnostics.add("invalid import collection")
        else:
            import_qualifiers: set[str] = set()
            import_paths: set[str] = set()
            sortable_imports: list[dict[str, Any]] = []
            for package_import in imports:
                if not isinstance(package_import, dict):
                    diagnostics.add("invalid import shape")
                    continue
                diagnostics |= _check_fields(
                    package_import,
                    {"qualifier", "path"},
                    {"qualifier", "path"},
                )
                qualifier = package_import.get("qualifier")
                import_path = package_import.get("path")

                if (
                    not isinstance(qualifier, str)
                    or not _is_go_identifier(qualifier)
                    or qualifier == "_"
                ):
                    diagnostics.add("invalid import qualifier")
                else:
                    diagnostics |= _text_diagnostics(qualifier)
                    if qualifier in import_qualifiers:
                        diagnostics.add("duplicate import qualifier")
                    import_qualifiers.add(qualifier)

                diagnostics |= _package_path_diagnostics(
                    import_path,
                    path_kind="import",
                    current_package_path=path,
                )
                if isinstance(import_path, str) and import_path:
                    if corpus and not import_path.startswith(SYNTHETIC_PREFIX):
                        diagnostics.add("non-synthetic fixture package")
                    if import_path in import_paths:
                        diagnostics.add("duplicate import path")
                    import_paths.add(import_path)

                if (
                    isinstance(qualifier, str)
                    and isinstance(import_path, str)
                    and not _has_surrogate(qualifier)
                    and not _has_surrogate(import_path)
                ):
                    sortable_imports.append(package_import)

            if len(sortable_imports) == len(imports):
                try:
                    if imports != sorted(imports, key=_import_order_key):
                        diagnostics.add("non-canonical import ordering")
                except (KeyError, AttributeError, TypeError, UnicodeEncodeError):
                    diagnostics.add("invalid import shape")

        if not isinstance(symbols, list) or not symbols:
            diagnostics.add("invalid symbol collection")
            continue

        type_declarations = {
            symbol.get("name"): symbol
            for symbol in symbols
            if isinstance(symbol, dict)
            and symbol.get("kind") == "type"
            and isinstance(symbol.get("name"), str)
        }
        sortable_symbols: list[dict[str, Any]] = []
        for symbol in symbols:
            if not isinstance(symbol, dict):
                diagnostics.add("invalid symbol shape")
                continue
            kind = symbol.get("kind")
            valid_kind = isinstance(kind, str) and kind in SYMBOL_KINDS
            if not valid_kind:
                diagnostics.add("invalid symbol kind")
                diagnostics |= _check_fields(
                    symbol,
                    {"kind", "name", "type", "signature"},
                    {"kind", "name", "type", "signature"},
                )
            else:
                fields = SYMBOL_FIELDS[kind]
                diagnostics |= _check_fields(symbol, fields["required"], fields["allowed"])

            symbol_name = symbol.get("name")
            if not isinstance(symbol_name, str) or not symbol_name:
                diagnostics.add("invalid symbol name")
            else:
                diagnostics |= _text_diagnostics(symbol_name)
                if not _is_go_identifier(symbol_name):
                    diagnostics.add("invalid Go identifier")
                elif not _is_exported(symbol_name):
                    diagnostics.add("unexported declaration")

            for field in ("type", "signature"):
                value = symbol.get(field)
                lossless = kind == "const" and field == "signature"
                valid_text = (
                    _lossless_exact_text(value)
                    if lossless
                    else _normalized_text(value)
                )
                if not valid_text:
                    diagnostics.add("invalid normalized text")
                    if isinstance(value, str):
                        diagnostics |= (
                            _lossless_text_diagnostics(value)
                            if lossless
                            else _text_diagnostics(value)
                        )
                if isinstance(value, str) and "implementation.invalid/" in value:
                    diagnostics.add("implementation dependency type")

            parameter_names: list[str] | None = None
            if valid_kind and kind in {"func", "type"}:
                parameter_diagnostics, parameter_names = _type_parameter_diagnostics(
                    symbol.get("type_parameters")
                )
                diagnostics |= parameter_diagnostics

            receiver: dict[str, Any] | None = None
            if kind == "method":
                receiver_diagnostics, receiver = _receiver_diagnostics(symbol.get("receiver"))
                diagnostics |= receiver_diagnostics

            if kind == "const":
                value_kind = symbol.get("value_kind")
                value = symbol.get("value")
                if not isinstance(value_kind, str) or value_kind not in VALUE_KINDS:
                    diagnostics.add("invalid value kind")
                if not _lossless_exact_text(value):
                    diagnostics.add("invalid constant value")
                if isinstance(value, str):
                    diagnostics |= _lossless_text_diagnostics(value)
                type_text = symbol.get("type")
                if (
                    isinstance(type_text, str)
                    and type_text in UNTYPED_VALUE_KINDS
                    and value_kind != UNTYPED_VALUE_KINDS[type_text]
                ):
                    diagnostics.add("cross-field mismatch")
            if kind == "type":
                type_form = symbol.get("type_form")
                if not isinstance(type_form, str) or type_form not in {"defined", "alias"}:
                    diagnostics.add("invalid type form")

            if (
                valid_kind
                and isinstance(symbol_name, str)
                and _is_go_identifier(symbol_name)
                and _normalized_text(symbol.get("type"))
                and (
                    _lossless_exact_text(symbol.get("signature"))
                    if kind == "const"
                    else _normalized_text(symbol.get("signature"))
                )
            ):
                expected_signature = _expected_signature(symbol)
                if expected_signature is None or symbol["signature"] != expected_signature:
                    diagnostics.add("cross-field mismatch")

            if isinstance(path, str) and isinstance(symbol_name, str):
                if kind == "method" and receiver is not None:
                    base = receiver.get("base")
                    if isinstance(base, str):
                        identity = (path, base, symbol_name)
                        if identity in method_identities:
                            diagnostics.add("duplicate symbol identity")
                        method_identities.add(identity)
                elif valid_kind and kind != "method":
                    identity = (path, symbol_name)
                    if identity in package_symbol_identities:
                        diagnostics.add("duplicate symbol identity")
                    package_symbol_identities.add(identity)

            if kind == "method" and receiver is not None:
                base = receiver.get("base")
                if isinstance(base, str) and _is_exported(base):
                    declaration = type_declarations.get(base)
                    if declaration is None:
                        diagnostics.add("unresolved receiver")
                    else:
                        declared_parameters = declaration.get("type_parameters")
                        if isinstance(declared_parameters, list) and isinstance(
                            receiver.get("type_parameters"), list
                        ):
                            if len(receiver["type_parameters"]) != len(declared_parameters):
                                diagnostics.add("receiver arity mismatch")

            if (
                valid_kind
                and isinstance(symbol_name, str)
                and not _has_surrogate(symbol_name)
                and (
                    kind != "method"
                    or (
                        isinstance(symbol.get("receiver"), dict)
                        and isinstance(symbol["receiver"].get("base"), str)
                        and not _has_surrogate(symbol["receiver"]["base"])
                    )
                )
            ):
                sortable_symbols.append(symbol)

        if len(sortable_symbols) == len(symbols):
            try:
                if symbols != sorted(symbols, key=_symbol_order_key):
                    diagnostics.add("non-canonical ordering")
            except (KeyError, AttributeError, TypeError, UnicodeEncodeError):
                diagnostics.add("invalid symbol shape")

    if len(sortable_packages) == len(packages):
        try:
            if packages != sorted(packages, key=_package_order_key):
                diagnostics.add("non-canonical ordering")
        except (KeyError, AttributeError, TypeError, UnicodeEncodeError):
            diagnostics.add("invalid package shape")
    return diagnostics


def validate_document(path: Path, *, corpus: bool = False) -> list[str]:
    label = path.name
    if not path.is_file() or path.is_symlink():
        return [f"{label}: missing regular artifact"]
    result, _, diagnostics = _load_machine_json(path)
    if result is not None and result.status == COMPLETE:
        diagnostics |= document_diagnostics(result.document, corpus=corpus)
    return [f"{label}: {category}" for category in sorted(diagnostics)]


def _load_machine_json(
    path: Path,
    *,
    allow_malformed_sentinel: bool = False,
) -> tuple[MachineJSONResult | None, bytes | None, set[str]]:
    try:
        raw = path.read_bytes()
    except OSError:
        return None, None, {"missing regular artifact"}
    result = decode_machine_json(
        raw,
        allow_malformed_sentinel=allow_malformed_sentinel,
    )
    if result.status == INVALID_UTF8:
        return result, raw, {"invalid UTF-8"}
    diagnostics = machine_publication_diagnostics(result)
    if result.status != COMPLETE:
        diagnostics.add("malformed JSON")
    if result.status == TRAILING_CONTENT:
        diagnostics.add("machine publication boundary")
    if result.duplicate_keys:
        diagnostics.add("duplicate key")
    return result, raw, diagnostics


def _negative_fixture_boundary_diagnostics(
    result: MachineJSONResult | None,
    *,
    expect_malformed_sentinel: bool,
) -> set[str]:
    if result is None:
        return {"negative fixture boundary mismatch"}
    expected_status = MALFORMED_SENTINEL if expect_malformed_sentinel else COMPLETE
    if result.status != expected_status or not isinstance(result.document, dict):
        return {"negative fixture boundary mismatch"}
    document = result.document

    schema_ids = object_values(document, "schema_id")
    schema_versions = object_values(document, "schema_version")
    if not schema_ids or any(value != SCHEMA_ID for value in schema_ids):
        return {"negative fixture boundary mismatch"}
    if not schema_versions or any(
        not _is_schema_integer(value, SCHEMA_VERSION) for value in schema_versions
    ):
        return {"negative fixture boundary mismatch"}

    fixtures = object_values(document, "fixture")
    if not fixtures:
        return {"negative fixture boundary mismatch"}
    for fixture in fixtures:
        if not isinstance(fixture, dict):
            return {"negative fixture boundary mismatch"}
        synthetic = object_values(fixture, "synthetic")
        runtime_claims = object_values(fixture, "runtime_claims")
        if not synthetic or any(value is not True for value in synthetic):
            return {"negative fixture boundary mismatch"}
        if not runtime_claims or any(value is not False for value in runtime_claims):
            return {"negative fixture boundary mismatch"}

    package_collections = object_values(document, "packages")
    if not package_collections:
        return {"negative fixture boundary mismatch"}
    for packages in package_collections:
        if not isinstance(packages, list) or not packages:
            return {"negative fixture boundary mismatch"}
        for package in packages:
            if not isinstance(package, dict):
                return {"negative fixture boundary mismatch"}
            paths = object_values(package, "path")
            if not paths or any(
                not isinstance(path, str) or not path.startswith(SYNTHETIC_PREFIX)
                for path in paths
            ):
                return {"negative fixture boundary mismatch"}
    return set()


def _regular_json_files(directory: Path) -> list[Path]:
    if not directory.is_dir() or directory.is_symlink():
        return []
    return sorted(
        (path for path in directory.iterdir() if path.name.endswith(".json")),
        key=lambda path: path.name.encode("utf-8"),
    )


def validate_repository(root: Path) -> list[str]:
    errors: list[str] = []
    schema_path = root / SCHEMA_REL
    schema_rel = SCHEMA_REL.as_posix()
    if not schema_path.is_file() or schema_path.is_symlink():
        errors.append(f"{schema_rel}: missing regular artifact")
    else:
        result, raw, diagnostics = _load_machine_json(schema_path)
        for category in sorted(diagnostics):
            errors.append(f"{schema_rel}: {category}")
        schema = result.document if result is not None and result.status == COMPLETE else None
        if schema is not None and raw is not None:
            if hashlib.sha256(raw).hexdigest() != SCHEMA_SHA256:
                errors.append(f"{schema_rel}: schema contract mismatch")
            if not isinstance(schema, dict):
                errors.append(f"{schema_rel}: invalid schema shape")
            else:
                if schema.get("$id") != SCHEMA_URI:
                    errors.append(f"{schema_rel}: schema identity mismatch")
                properties = schema.get("properties")
                if not isinstance(properties, dict):
                    errors.append(f"{schema_rel}: invalid schema shape")
                else:
                    schema_id = properties.get("schema_id")
                    schema_version = properties.get("schema_version", {})
                    if (
                        not isinstance(schema_id, dict)
                        or schema_id.get("const") != SCHEMA_ID
                        or not isinstance(schema_version, dict)
                        or schema_version.get("type") != "integer"
                        or type(schema_version.get("const")) is not int
                        or schema_version.get("const") != SCHEMA_VERSION
                    ):
                        errors.append(f"{schema_rel}: schema identity mismatch")

    positive_dir = root / POSITIVE_REL
    positive = _regular_json_files(positive_dir)
    positive_names = {path.name for path in positive}
    for missing in sorted(REQUIRED_POSITIVE - positive_names):
        errors.append(f"{(POSITIVE_REL / missing).as_posix()}: missing regular artifact")
    for path in positive:
        rel = path.relative_to(root).as_posix()
        if not path.is_file() or path.is_symlink():
            errors.append(f"{rel}: missing regular artifact")
            continue
        result, _, diagnostics = _load_machine_json(path)
        if result is not None and result.status == COMPLETE:
            diagnostics |= document_diagnostics(result.document, corpus=True)
        for category in sorted(diagnostics):
            errors.append(f"{rel}: {category}")

    negative_dir = root / NEGATIVE_REL
    negative = _regular_json_files(negative_dir)
    negative_names = {path.name for path in negative}
    for missing in sorted(set(EXPECTED_NEGATIVE_DIAGNOSTICS) - negative_names):
        errors.append(f"{(NEGATIVE_REL / missing).as_posix()}: missing regular artifact")
    for unexpected in sorted(negative_names - set(EXPECTED_NEGATIVE_DIAGNOSTICS)):
        errors.append(f"{(NEGATIVE_REL / unexpected).as_posix()}: unknown negative fixture")
    for path in negative:
        rel = path.relative_to(root).as_posix()
        if path.name not in EXPECTED_NEGATIVE_DIAGNOSTICS:
            continue
        if not path.is_file() or path.is_symlink():
            errors.append(f"{rel}: missing regular artifact")
            continue
        expect_malformed = path.name == "malformed.json"
        result, _, diagnostics = _load_machine_json(
            path,
            allow_malformed_sentinel=expect_malformed,
        )
        diagnostics |= _negative_fixture_boundary_diagnostics(
            result,
            expect_malformed_sentinel=expect_malformed,
        )
        if result is not None and result.document is not None:
            diagnostics |= document_diagnostics(result.document, corpus=True)
        expected = EXPECTED_NEGATIVE_DIAGNOSTICS[path.name]
        for category in sorted(expected - diagnostics):
            errors.append(f"{rel}: expected negative category missing: {category}")
        for category in sorted(diagnostics - expected):
            errors.append(f"{rel}: unexpected negative category: {category}")

    return sorted(set(errors), key=lambda value: value.encode("utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser()
    source = parser.add_mutually_exclusive_group()
    source.add_argument("--repo", type=Path)
    source.add_argument("--document", type=Path)
    parser.add_argument(
        "--corpus",
        action="store_true",
        help="require fixture metadata and synthetic package paths in --document mode",
    )
    args = parser.parse_args()

    if args.document is not None:
        errors = validate_document(args.document, corpus=args.corpus)
        success = "api-surface-v1 document: valid"
    else:
        if args.corpus:
            parser.error("--corpus requires --document")
        root = args.repo or Path(__file__).resolve().parents[1]
        errors = validate_repository(root.resolve())
        success = "api-surface-v1: valid"
    for error in errors:
        print(error, file=sys.stderr)
    if errors:
        return 1
    print(success)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
