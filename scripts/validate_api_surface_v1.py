#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import ipaddress
import json
import re
import sys
import unicodedata
from pathlib import Path
from typing import Any


SCHEMA_ID = "helianthus.eebus.api-surface.v1"
SCHEMA_URI = "urn:helianthus:eebus:api-surface:v1"
SCHEMA_VERSION = 1
SYNTHETIC_PREFIX = "example.invalid/helianthus/synthetic/"
SCHEMA_REL = Path("api/schema/helianthus.eebus.api-surface.v1.schema.json")
POSITIVE_REL = Path("api/fixtures/v1/positive")
NEGATIVE_REL = Path("api/fixtures/v1/negative")
SCHEMA_SHA256 = "163cd29ffa47ec4ead541e179aeca36974f98086d0d71db507244630717a8001"

SYMBOL_KINDS = {"const", "func", "method", "type", "var"}
REQUIRED_POSITIVE = {"packages-and-symbols.json", "kinds-types-signatures.json"}
EXPECTED_NEGATIVE = {
    "duplicate-identity.json": "duplicate symbol identity",
    "duplicate-json-key.json": "duplicate key",
    "implementation-dependency-type.json": "implementation dependency type",
    "internal-package.json": "internal package",
    "invalid-ordering.json": "non-canonical ordering",
    "malformed.json": "malformed JSON",
    "non-nfc.json": "non-NFC value",
    "unexported-declaration.json": "unexported declaration",
    "unexported-receiver.json": "unexported receiver",
    "unknown-field.json": "unknown field",
}
SENSITIVE_CATEGORIES = {
    "private identifier",
    "private network",
    "network address",
    "private path",
    "source contamination",
}

PRIVATE_PATH_PATTERN = re.compile(
    r"(?:/Users/[^/\s]+/|/home/[^/\s]+/|/tmp/[^\s]+|/var/folders/[^\s]+|"
    r"[A-Za-z]:\\Users\\[^\\\s]+\\)"
)
IPV4_PATTERN = re.compile(r"\b(?:(?:\d{1,3})\.){3}(?:\d{1,3})\b")
IPV6_PATTERN = re.compile(
    r"(?<![0-9A-Fa-f:])(?:[0-9A-Fa-f]{0,4}:){2,7}[0-9A-Fa-f]{0,4}"
    r"(?:%[A-Za-z0-9_.-]+)?(?![0-9A-Fa-f:])"
)
MAC_PATTERN = re.compile(
    r"(?<![0-9A-Fa-f])(?:"
    r"(?:[0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}|"
    r"(?:[0-9A-Fa-f]{4}\.){2}[0-9A-Fa-f]{4}"
    r")(?![0-9A-Fa-f])"
)
FINGERPRINT_PATTERN = re.compile(r"(?<![0-9A-Fa-f])[0-9A-Fa-f]{40,}(?![0-9A-Fa-f])")
SECRET_PATTERN = re.compile(
    r"\b(?:token|password|passphrase|credential|secret|api[_ -]?key|"
    r"client[_ -]?secret|serial[_ -]?number)\s*[:=]",
    re.IGNORECASE,
)
SOURCE_CONTAMINATION_PATTERN = re.compile(
    r"\bvendor[_ -]restricted\b|\brestricted[ -]+source\b",
    re.IGNORECASE,
)


class DuplicateKeyError(ValueError):
    pass


class InvalidConstantError(ValueError):
    pass


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateKeyError
        result[key] = value
    return result


def _reject_constant(_: str) -> None:
    raise InvalidConstantError


def _sensitive_diagnostics(text: str) -> set[str]:
    diagnostics: set[str] = set()
    if PRIVATE_PATH_PATTERN.search(text):
        diagnostics.add("private path")
    if MAC_PATTERN.search(text) or FINGERPRINT_PATTERN.search(text) or SECRET_PATTERN.search(text):
        diagnostics.add("private identifier")
    if SOURCE_CONTAMINATION_PATTERN.search(text):
        diagnostics.add("source contamination")

    for match in IPV4_PATTERN.finditer(text):
        try:
            address = ipaddress.ip_address(match.group(0))
        except ValueError:
            continue
        if address.is_private or address.is_loopback or address.is_link_local:
            diagnostics.add("private network")
        else:
            diagnostics.add("network address")

    for match in IPV6_PATTERN.finditer(text):
        candidate = match.group(0).split("%", 1)[0]
        try:
            ipaddress.ip_address(candidate)
        except ValueError:
            continue
        diagnostics.add("network address")
    return diagnostics


def _load_json(path: Path) -> tuple[Any | None, bytes | None, set[str]]:
    try:
        raw = path.read_bytes()
    except OSError:
        return None, None, {"missing regular artifact"}
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        return None, raw, {"invalid UTF-8"}

    diagnostics = _sensitive_diagnostics(text)
    try:
        document = json.loads(
            text,
            object_pairs_hook=_unique_object,
            parse_constant=_reject_constant,
        )
    except DuplicateKeyError:
        diagnostics.add("duplicate key")
        return None, raw, diagnostics
    except (json.JSONDecodeError, InvalidConstantError):
        diagnostics.add("malformed JSON")
        return None, raw, diagnostics
    return document, raw, diagnostics


def _check_fields(value: dict[str, Any], required: set[str], allowed: set[str]) -> set[str]:
    diagnostics: set[str] = set()
    if set(value) - allowed:
        diagnostics.add("unknown field")
    if required - set(value):
        diagnostics.add("missing required field")
    return diagnostics


def _is_nfc(value: str) -> bool:
    return value == unicodedata.normalize("NFC", value)


def _is_exported(value: str) -> bool:
    return bool(value) and unicodedata.category(value[0]) == "Lu"


def _receiver_base(receiver: str) -> str:
    base = receiver.lstrip("*").split("[", 1)[0]
    return base.rsplit(".", 1)[-1]


def _normalized_text(value: Any) -> bool:
    return (
        isinstance(value, str)
        and bool(value)
        and value == value.strip()
        and _is_nfc(value)
        and re.search(r"[\t\r\n]| {2}", value) is None
    )


def _package_order_key(package: dict[str, Any]) -> tuple[bytes, bytes]:
    return (package["path"].encode("utf-8"), package["name"].encode("utf-8"))


def _symbol_order_key(symbol: dict[str, Any]) -> tuple[bytes, bytes, bytes]:
    return tuple(
        value.encode("utf-8")
        for value in (symbol["kind"], symbol.get("receiver", ""), symbol["name"])
    )


def _document_diagnostics(document: Any) -> set[str]:
    diagnostics: set[str] = set()
    if not isinstance(document, dict):
        return {"invalid document shape"}

    diagnostics |= _check_fields(
        document,
        {"schema_id", "schema_version", "fixture", "packages"},
        {"schema_id", "schema_version", "fixture", "packages"},
    )
    if document.get("schema_id") != SCHEMA_ID or document.get("schema_version") != SCHEMA_VERSION:
        diagnostics.add("schema identity mismatch")

    fixture = document.get("fixture")
    if not isinstance(fixture, dict):
        diagnostics.add("invalid fixture metadata")
    else:
        diagnostics |= _check_fields(
            fixture,
            {"synthetic", "runtime_claims"},
            {"synthetic", "runtime_claims"},
        )
        if fixture.get("synthetic") is not True or fixture.get("runtime_claims") is not False:
            diagnostics.add("runtime claim or non-synthetic fixture")

    packages = document.get("packages")
    if not isinstance(packages, list) or not packages:
        diagnostics.add("invalid package collection")
        return diagnostics

    sortable_packages: list[dict[str, Any]] = []
    package_paths: set[str] = set()
    symbol_identities: set[tuple[str, str, str, str]] = set()

    for package in packages:
        if not isinstance(package, dict):
            diagnostics.add("invalid package shape")
            continue
        diagnostics |= _check_fields(package, {"path", "name", "symbols"}, {"path", "name", "symbols"})
        path = package.get("path")
        name = package.get("name")
        symbols = package.get("symbols")

        if not isinstance(path, str) or not path or not isinstance(name, str) or not name:
            diagnostics.add("invalid package identity")
        else:
            if not _is_nfc(path) or not _is_nfc(name):
                diagnostics.add("non-NFC value")
            components = path.split("/")
            if (
                path.startswith("/")
                or path.endswith("/")
                or "\\" in path
                or any(component in {"", ".", ".."} for component in components)
            ):
                diagnostics.add("invalid package path")
            if "internal" in components:
                diagnostics.add("internal package")
            if not path.startswith(SYNTHETIC_PREFIX):
                diagnostics.add("non-synthetic fixture package")
            if path in package_paths:
                diagnostics.add("duplicate package identity")
            package_paths.add(path)

        if isinstance(path, str) and isinstance(name, str):
            sortable_packages.append(package)

        if not isinstance(symbols, list) or not symbols:
            diagnostics.add("invalid symbol collection")
            continue
        sortable_symbols: list[dict[str, Any]] = []
        for symbol in symbols:
            if not isinstance(symbol, dict):
                diagnostics.add("invalid symbol shape")
                continue
            kind = symbol.get("kind")
            required = {"kind", "name", "type", "signature"}
            if kind == "method":
                required.add("receiver")
            diagnostics |= _check_fields(
                symbol,
                required,
                {"kind", "receiver", "name", "type", "signature"},
            )
            if kind not in SYMBOL_KINDS:
                diagnostics.add("invalid symbol kind")
            if kind != "method" and "receiver" in symbol:
                diagnostics.add("receiver on non-method")

            symbol_name = symbol.get("name")
            receiver = symbol.get("receiver", "")
            if not isinstance(symbol_name, str) or not symbol_name:
                diagnostics.add("invalid symbol name")
            else:
                if not _is_nfc(symbol_name):
                    diagnostics.add("non-NFC value")
                if not _is_exported(symbol_name):
                    diagnostics.add("unexported declaration")

            if kind == "method":
                if not isinstance(receiver, str) or not receiver or re.search(r"\s", receiver):
                    diagnostics.add("invalid receiver")
                else:
                    if not _is_nfc(receiver):
                        diagnostics.add("non-NFC value")
                    if not _is_exported(_receiver_base(receiver)):
                        diagnostics.add("unexported receiver")

            for field in ("type", "signature"):
                value = symbol.get(field)
                if not _normalized_text(value):
                    diagnostics.add("invalid normalized text")
                    if isinstance(value, str) and not _is_nfc(value):
                        diagnostics.add("non-NFC value")
                if isinstance(value, str) and "implementation.invalid/" in value:
                    diagnostics.add("implementation dependency type")

            if (
                isinstance(kind, str)
                and isinstance(receiver, str)
                and isinstance(symbol_name, str)
                and isinstance(path, str)
            ):
                identity = (path, kind, receiver, symbol_name)
                if identity in symbol_identities:
                    diagnostics.add("duplicate symbol identity")
                symbol_identities.add(identity)
                sortable_symbols.append(symbol)

        if len(sortable_symbols) == len(symbols):
            try:
                if symbols != sorted(symbols, key=_symbol_order_key):
                    diagnostics.add("non-canonical ordering")
            except (KeyError, AttributeError):
                diagnostics.add("invalid symbol shape")

    if len(sortable_packages) == len(packages):
        try:
            if packages != sorted(packages, key=_package_order_key):
                diagnostics.add("non-canonical ordering")
        except (KeyError, AttributeError):
            diagnostics.add("invalid package shape")
    return diagnostics


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
        schema, raw, diagnostics = _load_json(schema_path)
        for category in sorted(diagnostics):
            errors.append(f"{schema_rel}: {category}")
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
                elif (
                    properties.get("schema_id", {}).get("const") != SCHEMA_ID
                    or properties.get("schema_version", {}).get("const") != SCHEMA_VERSION
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
        document, _, diagnostics = _load_json(path)
        if document is not None:
            diagnostics |= _document_diagnostics(document)
        for category in sorted(diagnostics):
            errors.append(f"{rel}: {category}")

    negative_dir = root / NEGATIVE_REL
    negative = _regular_json_files(negative_dir)
    negative_names = {path.name for path in negative}
    for missing in sorted(set(EXPECTED_NEGATIVE) - negative_names):
        errors.append(f"{(NEGATIVE_REL / missing).as_posix()}: missing regular artifact")
    for unexpected in sorted(negative_names - set(EXPECTED_NEGATIVE)):
        errors.append(f"{(NEGATIVE_REL / unexpected).as_posix()}: unknown negative fixture")
    for path in negative:
        rel = path.relative_to(root).as_posix()
        if path.name not in EXPECTED_NEGATIVE:
            continue
        if not path.is_file() or path.is_symlink():
            errors.append(f"{rel}: missing regular artifact")
            continue
        document, _, diagnostics = _load_json(path)
        sensitive = diagnostics & SENSITIVE_CATEGORIES
        for category in sorted(sensitive):
            errors.append(f"{rel}: {category}")
        if document is not None:
            diagnostics |= _document_diagnostics(document)
        expected = EXPECTED_NEGATIVE[path.name]
        if expected not in diagnostics:
            errors.append(f"{rel}: expected negative category missing")

    return sorted(set(errors), key=lambda value: value.encode("utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()

    errors = validate_repository(args.repo.resolve())
    for error in errors:
        print(error, file=sys.stderr)
    if errors:
        return 1
    print("api-surface-v1: valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
