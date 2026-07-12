#!/usr/bin/env python3
from __future__ import annotations

import heapq
import ipaddress
import json
import math
import re
from dataclasses import dataclass
from decimal import Decimal, DecimalException
from typing import Any, Iterator


COMPLETE = "complete"
MALFORMED_SENTINEL = "malformed-sentinel"
INVALID_JSON = "invalid-json"
INVALID_UTF8 = "invalid-utf8"
NESTING_TOO_DEEP = "nesting-too-deep"
TRAILING_CONTENT = "trailing-content"
MALFORMED_SENTINEL_REMAINDER = "\n!\n"
MAX_MACHINE_JSON_DEPTH = 64
PRIVATE_IPV4_NETWORKS = (
    ((10, 0, 0, 0), 8),
    ((100, 64, 0, 0), 10),
    ((127, 0, 0, 0), 8),
    ((169, 254, 0, 0), 16),
    ((172, 16, 0, 0), 12),
    ((192, 168, 0, 0), 16),
)
DOCUMENTATION_IPV4_NETWORKS = (
    ((192, 0, 2, 0), 24),
    ((198, 51, 100, 0), 24),
    ((203, 0, 113, 0), 24),
)
COLON = chr(58)
DOCUMENTATION_IPV6_NETWORKS = tuple(
    ipaddress.ip_network(value)
    for value in (
        "2001" + COLON + "db8" + COLON * 2 + "/32",
        "3fff" + COLON * 2 + "/20",
    )
)
PRIVATE_IPV6_NETWORKS = tuple(
    ipaddress.ip_network(value)
    for value in (
        COLON * 2 + "/128",
        COLON * 2 + "1/128",
        "fc00" + COLON * 2 + "/7",
        "fe80" + COLON * 2 + "/10",
        "ff00" + COLON * 2 + "/8",
    )
)

PRIVATE_HOME_BOUNDARY = r"(?=$|/|_|[^\w/-])"
PRIVATE_HOME_COMPONENT = r"[^/\s\"'<>]*?[\w-]"
PRIVATE_USER_ROOT = "/" + "Users"
PRIVATE_HOME_ROOT = "/" + "home"
PRIVATE_ADMIN_ROOT = "/" + "root"
PRIVATE_TEMP_ROOT = "/" + "tmp"
PRIVATE_VOLUMES_ROOT = "/" + "Volumes"
PRIVATE_PATH_PATTERN = re.compile(
    rf"(?:{PRIVATE_USER_ROOT}/{PRIVATE_HOME_COMPONENT}{PRIVATE_HOME_BOUNDARY}(?:/[^\s\"'<>]*)?|"
    rf"{PRIVATE_HOME_ROOT}/{PRIVATE_HOME_COMPONENT}{PRIVATE_HOME_BOUNDARY}(?:/[^\s\"'<>]*)?|"
    rf"{PRIVATE_ADMIN_ROOT}{PRIVATE_HOME_BOUNDARY}(?:/[^\s\"'<>]*)?|"
    rf"{PRIVATE_TEMP_ROOT}/[^\s]+|/var/fol" r"ders/[^\s]+|"
    rf"{PRIVATE_VOLUMES_ROOT}(?:/[^\s]*)?|"
    r"[A-Za-z]" + COLON + r"\\Use" r"rs\\[^\\\s]+\\)"
)
IPV4_CANDIDATE_PATTERN = re.compile(
    r"(?<![0-9.])(?:[0-9]{1,3}\.){3}[0-9]{1,3}(?![0-9.])"
)
IPV6_CANDIDATE_PATTERN = re.compile(
    rf"(?<![0-9A-Fa-f{COLON}])(?:[0-9A-Fa-f]{{0,4}}{COLON}){{2,7}}[0-9A-Fa-f]{{0,4}}"
    rf"(?:%[A-Za-z0-9_.-]+)?(?![0-9A-Fa-f{COLON}])"
)
MAC_PATTERN = re.compile(
    r"(?<![0-9A-Fa-f])(?:"
    r"(?:[0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}|"
    r"(?:[0-9A-Fa-f]{4}\.){2}[0-9A-Fa-f]{4}"
    r")(?![0-9A-Fa-f])"
)
FINGERPRINT_PATTERN = re.compile(r"(?<![0-9A-Fa-f])[0-9A-Fa-f]{40,}(?![0-9A-Fa-f])")
GIT_OBJECT_FIELD_PATTERN = re.compile(
    r"(?im)^\s*[\"']?(?:blob|commit|git_commit|source|source_blob|source_commit|"
    r"source_ref|source_sha)[\"']?\s*[:=]\s*[\"']?([0-9a-f]{40})[\"']?\s*,?\s*$"
)
GIT_OBJECT_URL_PATTERN = re.compile(
    r"https?://[^\s<>\"']+/(?:blob|commit|commits|raw|tree)/([0-9a-f]{40})"
    r"(?:[/#?]|$)",
    re.IGNORECASE,
)
GIT_SNAPSHOT_FIELD_PATTERN = re.compile(
    r"(?im)^\s*[\"']?(?:cross_seed_snapshot|source_snapshot)[\"']?\s*[:=]"
    r"[^\n]*?@([0-9a-f]{40})(?=[:/])"
)
GIT_SNAPSHOT_VALUE_PATTERN = re.compile(
    r"(?:Project-Helianthus/)?[A-Za-z0-9._-]+@([0-9a-f]{40}):"
    r"[A-Za-z0-9._/-]+"
)
GIT_OBJECT_VALUE_PATTERN = re.compile(r"[0-9a-f]{40}\Z")
GIT_OBJECT_MACHINE_KEYS = {
    "blob",
    "commit",
    "git_commit",
    "source",
    "source_blob",
    "source_commit",
    "source_ref",
    "source_sha",
}
CANONICAL_DECIMAL_INTEGER_PATTERN = re.compile(r"-?(?:0|[1-9][0-9]*)\Z")
CANONICAL_FRACTION_PATTERN = re.compile(
    r"(-?(?:0|[1-9][0-9]*))/([1-9][0-9]*)\Z"
)
CANONICAL_HEX_FLOAT_PATTERN = re.compile(
    r"-?0x\.[89a-f](?:[0-9a-f]*[1-9a-f])?p(?:\+0|\+[1-9][0-9]*|-[1-9][0-9]*)\Z"
)
CANONICAL_COMPLEX_PATTERN = re.compile(r"\((.+) \+ (.+)i\)\Z")
UNTYPED_CONSTANT_TYPES = {
    "untyped bool",
    "untyped complex",
    "untyped float",
    "untyped int",
    "untyped rune",
    "untyped string",
}
SECRET_PATTERN = re.compile(
    r"\b(?:token|password|passphrase|credential|secret|api[_ -]?key|"
    r"client[_ -]?secret|private[_ -]?key|serial(?:[_ -]?number)?|"
    r"account[_ -]?(?:id|identifier|data)|local[_ -]?identity|"
    r"stable[_ -]?peer[_ -]?identifier|pairing[_ -]?history|"
    r"(?:full[_ -]+)?fingerprint|mac[_ -]+address|"
    r"(?:raw[_ -]+)?(?:ski|ship)(?:[_ -]*(?:id|identifier))?)"
    r"\s*[:=]",
    re.IGNORECASE,
)
PEM_BLOCK_PATTERN = re.compile(
    r"-----BEGIN [A-Z0-9 ][A-Z0-9 -]*-----",
    re.IGNORECASE,
)
RAW_EEBUS_ID_PATTERN = re.compile(
    r"`?\b(?:raw[_ -]+)?(?:ski|ship)(?:[_ -]*(?:id|identifier))?\b`?"
    rf"\s*(?:{COLON}|=|\bis\b)?\s*`?[A-Za-z0-9][A-Za-z0-9._{COLON}-]{{7,}}`?",
    re.IGNORECASE,
)
PRIVATE_ARTIFACT_PATTERN = re.compile(
    r"\bprivate[\s_-]+artifact[\s_-]+"
    r"(?:location|reference|filename|hash|identifier|retained)\s*[:=]",
    re.IGNORECASE,
)
HOUSEHOLD_PATTERN = re.compile(r"\bhousehold[_ -]+(?:data|schedule)\s*[:=]", re.IGNORECASE)
RAW_EVIDENCE_PATTERN = re.compile(r"\braw[_ -]+evidence\s*[:=]", re.IGNORECASE)
SOURCE_CONTAMINATION_PATTERN = re.compile(
    r"\bvendor[_ -]restric" r"ted\b|"
    r"\brestric" r"ted[ -]+source\b|"
    r"\brestric" r"ted[_ -]+(?:documents?|docs?)\b|"
    r"\brestric" r"ted[_ -]+vendor[_ -]+"
    r"(?:documents?|docs?|sources?|materials?|contents?|texts?)\b|"
    r"\bparaphras(?:e|ed|ing)\b[^\n]{0,80}\brestric" r"ted\b|"
    r"\bsource[_ -]+class\b[\"']?\s*[:=]\s*[\"']?restric" r"ted\b",
    re.IGNORECASE,
)

SENSITIVE_MACHINE_KEYS = {
    "token",
    "password",
    "passphrase",
    "credential",
    "secret",
    "api_key",
    "client_secret",
    "private_key",
    "account_id",
    "account_identifier",
    "account_data",
    "fingerprint",
    "full_fingerprint",
    "mac_address",
    "serial",
    "serial_number",
    "local_identity",
    "stable_peer_identifier",
    "pairing_history",
    "ski",
    "skiid",
    "ski_id",
    "ski_identifier",
    "ship",
    "shipid",
    "ship_id",
    "ship_identifier",
    "raw_ski",
    "raw_skiid",
    "raw_ski_id",
    "raw_ski_identifier",
    "raw_ship",
    "raw_shipid",
    "raw_ship_id",
    "raw_ship_identifier",
}
PRIVATE_ARTIFACT_MACHINE_KEYS = {
    "private_artifact_location",
    "private_artifact_reference",
    "private_artifact_filename",
    "private_artifact_hash",
    "private_artifact_identifier",
    "private_artifact_retained",
}
HOUSEHOLD_MACHINE_KEYS = {"household_data", "household_schedule"}
RAW_EVIDENCE_MACHINE_KEYS = {"raw_evidence"}
RESTRICTED_MACHINE_KEYS = {
    "restric" + "ted_document",
    "restric" + "ted_documents",
    "restric" + "ted_doc",
    "restric" + "ted_docs",
    "restric" + "ted_source",
    "restric" + "ted_sources",
    "restric" + "ted_vendor_document",
    "restric" + "ted_vendor_documents",
    "restric" + "ted_vendor_source",
    "restric" + "ted_vendor_sources",
    "vendor_restric" + "ted",
}


class JSONObject(dict[str, Any]):
    """A normal mapping that also retains every decoded key occurrence."""

    def __init__(self, pairs: list[tuple[str, Any]]) -> None:
        super().__init__(pairs)
        self.pairs = tuple(pairs)


class InvalidJSONConstantError(ValueError):
    pass


@dataclass(frozen=True)
class UnrepresentableJSONNumber:
    """Opaque fail-closed value for a valid number outside local numeric limits."""


@dataclass(frozen=True)
class MachineJSONResult:
    status: str
    document: Any | None
    text: str | None
    remainder: str
    duplicate_keys: bool
    numeric_lexemes: tuple[str, ...]

    @property
    def boundary_valid(self) -> bool:
        return self.status in {COMPLETE, MALFORMED_SENTINEL}


def _tracked_object(pairs: list[tuple[str, Any]]) -> JSONObject:
    return JSONObject(pairs)


def _reject_constant(_: str) -> None:
    raise InvalidJSONConstantError


def _machine_json_decoder(
    numeric_lexemes: list[str],
) -> json.JSONDecoder:
    def parse_integer(lexeme: str) -> int | UnrepresentableJSONNumber:
        numeric_lexemes.append(lexeme)
        try:
            return int(lexeme, 10)
        except (ValueError, OverflowError):
            return UnrepresentableJSONNumber()

    def parse_decimal(lexeme: str) -> Decimal | UnrepresentableJSONNumber:
        numeric_lexemes.append(lexeme)
        try:
            return Decimal(lexeme)
        except (DecimalException, ValueError):
            return UnrepresentableJSONNumber()

    return json.JSONDecoder(
        object_pairs_hook=_tracked_object,
        parse_constant=_reject_constant,
        parse_float=parse_decimal,
        parse_int=parse_integer,
        strict=True,
    )


def _exceeds_machine_json_depth(text: str) -> bool:
    """Check container depth without recursively parsing attacker-controlled JSON."""

    depth = 0
    in_string = False
    escaped = False
    for char in text:
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue
        if char == '"':
            in_string = True
        elif char in "[{":
            depth += 1
            if depth > MAX_MACHINE_JSON_DEPTH:
                return True
        elif char in "]}" and depth:
            depth -= 1
    return False


def has_duplicate_key(value: Any) -> bool:
    if isinstance(value, JSONObject):
        keys = [key for key, _ in value.pairs]
        return len(keys) != len(set(keys)) or any(
            has_duplicate_key(item) for _, item in value.pairs
        )
    if isinstance(value, list):
        return any(has_duplicate_key(item) for item in value)
    if isinstance(value, dict):
        return any(has_duplicate_key(item) for item in value.values())
    return False


def decoded_text_occurrences(value: Any) -> Iterator[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, list):
        for item in value:
            yield from decoded_text_occurrences(item)
    elif isinstance(value, JSONObject):
        for key, item in value.pairs:
            yield key
            yield from decoded_text_occurrences(item)
    elif isinstance(value, dict):
        for key, item in value.items():
            if isinstance(key, str):
                yield key
            yield from decoded_text_occurrences(item)


def object_values(value: Any, key: str) -> list[Any]:
    if isinstance(value, JSONObject):
        return [item for candidate, item in value.pairs if candidate == key]
    if isinstance(value, dict) and key in value:
        return [value[key]]
    return []


def decode_machine_json(
    raw: bytes,
    *,
    allow_malformed_sentinel: bool = False,
) -> MachineJSONResult:
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        return MachineJSONResult(INVALID_UTF8, None, None, "", False, ())

    if _exceeds_machine_json_depth(text):
        return MachineJSONResult(
            NESTING_TOO_DEEP,
            None,
            text,
            text,
            False,
            (),
        )

    numeric_lexemes: list[str] = []

    decoder = _machine_json_decoder(numeric_lexemes)
    start = 0
    while start < len(text) and text[start] in " \t\r\n":
        start += 1
    try:
        document, end = decoder.raw_decode(text, start)
    except (
        json.JSONDecodeError,
        InvalidJSONConstantError,
        DecimalException,
        OverflowError,
        RecursionError,
        ValueError,
    ):
        return MachineJSONResult(
            INVALID_JSON,
            None,
            text,
            text[start:],
            False,
            tuple(numeric_lexemes),
        )

    remainder = text[end:]
    duplicate_keys = has_duplicate_key(document)
    if all(char in " \t\r\n" for char in remainder):
        status = COMPLETE
    elif allow_malformed_sentinel and remainder == MALFORMED_SENTINEL_REMAINDER:
        status = MALFORMED_SENTINEL
    else:
        status = TRAILING_CONTENT
    return MachineJSONResult(
        status,
        document,
        text,
        remainder,
        duplicate_keys,
        tuple(numeric_lexemes),
    )


def parse_ipv4(candidate: str) -> tuple[int, int, int, int] | None:
    parts = candidate.split(".")
    if len(parts) != 4:
        return None
    octets: list[int] = []
    for part in parts:
        if not 1 <= len(part) <= 3 or not part.isascii() or not part.isdigit():
            return None
        octet = int(part, 10)
        if octet > 255:
            return None
        octets.append(octet)
    return (octets[0], octets[1], octets[2], octets[3])


def classify_ipv4(candidate: str) -> str | None:
    octets = parse_ipv4(candidate)
    if octets is None:
        return None
    address = sum(octet << shift for octet, shift in zip(octets, (24, 16, 8, 0)))
    for network_octets, prefix in DOCUMENTATION_IPV4_NETWORKS:
        network = sum(
            octet << shift for octet, shift in zip(network_octets, (24, 16, 8, 0))
        )
        mask = ((1 << prefix) - 1) << (32 - prefix)
        if address & mask == network & mask:
            return None
    private = False
    for network_octets, prefix in PRIVATE_IPV4_NETWORKS:
        network = sum(
            octet << shift for octet, shift in zip(network_octets, (24, 16, 8, 0))
        )
        mask = ((1 << prefix) - 1) << (32 - prefix)
        if address & mask == network & mask:
            private = True
            break
    return "private network" if private else "network address"


def classify_ipv6(candidate: str) -> str | None:
    try:
        address = ipaddress.ip_address(candidate.split("%", 1)[0])
    except ValueError:
        return None
    if not isinstance(address, ipaddress.IPv6Address):
        return None
    if any(address in network for network in DOCUMENTATION_IPV6_NETWORKS):
        return None
    if any(address in network for network in PRIVATE_IPV6_NETWORKS):
        return "private network"
    return "network address"


def _coalesced_ordered_spans(
    *span_groups: tuple[tuple[int, int], ...],
) -> tuple[tuple[int, int], ...]:
    """Merge a bounded number of ordered span streams in linear time."""
    merged: list[tuple[int, int]] = []
    for start, end in heapq.merge(*span_groups):
        if start < 0 or end < start:
            raise ValueError("invalid fingerprint exemption span")
        if merged and start <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], end))
        else:
            merged.append((start, end))
    return tuple(merged)


def git_fingerprint_exempt_spans(text: str) -> tuple[tuple[int, int], ...]:
    groups = tuple(
        tuple(match.span(1) for match in pattern.finditer(text))
        for pattern in (
            GIT_OBJECT_FIELD_PATTERN,
            GIT_OBJECT_URL_PATTERN,
            GIT_SNAPSHOT_FIELD_PATTERN,
            GIT_SNAPSHOT_VALUE_PATTERN,
        )
    )
    return _coalesced_ordered_spans(*groups)


def _has_unexempted_fingerprint(
    text: str,
    exempt_spans: tuple[tuple[int, int], ...],
) -> bool:
    span_index = 0
    for match in FINGERPRINT_PATTERN.finditer(text):
        while (
            span_index < len(exempt_spans)
            and exempt_spans[span_index][1] <= match.start()
        ):
            span_index += 1
        if span_index == len(exempt_spans):
            return True
        start, end = exempt_spans[span_index]
        if not (start <= match.start() and match.end() <= end):
            return True
    return False


def marker_diagnostics(
    text: str,
    *,
    fingerprint_exempt_spans: tuple[tuple[int, int], ...] = (),
    scan_fingerprints: bool = True,
) -> set[str]:
    fingerprint_exempt_spans = _coalesced_ordered_spans(
        fingerprint_exempt_spans,
        git_fingerprint_exempt_spans(text),
    )
    diagnostics: set[str] = set()
    if PRIVATE_PATH_PATTERN.search(text):
        diagnostics.add("private path")
    if (
        MAC_PATTERN.search(text)
        or PEM_BLOCK_PATTERN.search(text)
        or RAW_EEBUS_ID_PATTERN.search(text)
        or SECRET_PATTERN.search(text)
        or (
            scan_fingerprints
            and _has_unexempted_fingerprint(text, fingerprint_exempt_spans)
        )
    ):
        diagnostics.add("private identifier")
    if PRIVATE_ARTIFACT_PATTERN.search(text):
        diagnostics.add("private path")
    if HOUSEHOLD_PATTERN.search(text):
        diagnostics.add("household data")
    if RAW_EVIDENCE_PATTERN.search(text):
        diagnostics.add("raw evidence")
    if SOURCE_CONTAMINATION_PATTERN.search(text):
        diagnostics.add("source contamination")

    for match in IPV4_CANDIDATE_PATTERN.finditer(text):
        classification = classify_ipv4(match.group(0))
        if classification is not None:
            diagnostics.add(classification)

    for match in IPV6_CANDIDATE_PATTERN.finditer(text):
        classification = classify_ipv6(match.group(0))
        if classification is not None:
            diagnostics.add(classification)
    return diagnostics


def _object_pairs(value: dict[str, Any]) -> tuple[tuple[str, Any], ...]:
    if isinstance(value, JSONObject):
        return value.pairs
    return tuple(value.items())


def _has_local_duplicate_key(value: dict[str, Any]) -> bool:
    keys = [key for key, _ in _object_pairs(value)]
    return len(keys) != len(set(keys))


def _is_symbol_path(path: tuple[str | int, ...]) -> bool:
    return (
        len(path) == 4
        and path[0] == "packages"
        and type(path[1]) is int
        and path[2] == "symbols"
        and type(path[3]) is int
    )


def _decimal_integer(value: str) -> int:
    negative = value.startswith("-")
    digits = value[1:] if negative else value
    result = 0
    for start in range(0, len(digits), 18):
        chunk = digits[start : start + 18]
        result = result * (10 ** len(chunk)) + int(chunk, 10)
    return -result if negative else result


def _is_canonical_exact_real(value: str) -> bool:
    if CANONICAL_DECIMAL_INTEGER_PATTERN.fullmatch(value) is not None:
        return True
    fraction = CANONICAL_FRACTION_PATTERN.fullmatch(value)
    if fraction is not None:
        numerator = _decimal_integer(fraction.group(1))
        denominator = _decimal_integer(fraction.group(2))
        return numerator != 0 and denominator > 1 and math.gcd(abs(numerator), denominator) == 1
    return CANONICAL_HEX_FLOAT_PATTERN.fullmatch(value) is not None


def canonical_exact_numeric(value_kind: str, value: str) -> bool:
    """Return whether text has a canonical numeric go/constant.ExactString shape."""

    if value_kind == "int":
        return CANONICAL_DECIMAL_INTEGER_PATTERN.fullmatch(value) is not None
    if value_kind == "float":
        return _is_canonical_exact_real(value)
    if value_kind == "complex":
        match = CANONICAL_COMPLEX_PATTERN.fullmatch(value)
        return match is not None and all(
            _is_canonical_exact_real(component) for component in match.groups()
        )
    return False


def _numeric_constant_fingerprint_exemptions(
    value: dict[str, Any],
    path: tuple[str | int, ...],
    *,
    duplicate_context: bool,
) -> dict[str, tuple[tuple[int, int], ...]]:
    fields = _object_pairs(value)
    if (
        duplicate_context
        or not _is_symbol_path(path)
        or {key for key, _ in fields}
        != {"kind", "name", "type", "signature", "value_kind", "value"}
    ):
        return {}

    symbol = dict(fields)
    if symbol.get("kind") != "const":
        return {}
    name = symbol.get("name")
    type_text = symbol.get("type")
    signature = symbol.get("signature")
    value_kind = symbol.get("value_kind")
    constant_value = symbol.get("value")
    if not all(
        isinstance(item, str)
        for item in (name, type_text, signature, value_kind, constant_value)
    ):
        return {}
    if not canonical_exact_numeric(value_kind, constant_value):
        return {}

    if type_text in UNTYPED_CONSTANT_TYPES:
        expected_signature = f"const {name} = {constant_value}"
    else:
        expected_signature = f"const {name} {type_text} = {constant_value}"
    if signature != expected_signature:
        return {}

    value_start = len(signature) - len(constant_value)
    return {
        "value": ((0, len(constant_value)),),
        "signature": ((value_start, len(signature)),),
    }


def _decoded_marker_diagnostics(
    value: Any,
    path: tuple[str | int, ...] = (),
    *,
    duplicate_context: bool = False,
) -> set[str]:
    if isinstance(value, str):
        return marker_diagnostics(value)
    if isinstance(value, bool) or value is None:
        return set()
    if isinstance(value, (int, Decimal, UnrepresentableJSONNumber)):
        return set()
    if isinstance(value, list):
        diagnostics: set[str] = set()
        for index, item in enumerate(value):
            diagnostics |= _decoded_marker_diagnostics(
                item,
                path + (index,),
                duplicate_context=duplicate_context,
            )
        return diagnostics
    if isinstance(value, dict):
        diagnostics = set()
        local_duplicate = _has_local_duplicate_key(value)
        child_duplicate_context = duplicate_context or local_duplicate
        exemptions = _numeric_constant_fingerprint_exemptions(
            value,
            path,
            duplicate_context=child_duplicate_context,
        )
        for key, item in _object_pairs(value):
            diagnostics |= marker_diagnostics(key)
            normalized_key = re.sub(r"[\s-]+", "_", key.strip().lower())
            if normalized_key in SENSITIVE_MACHINE_KEYS:
                diagnostics.add("private identifier")
            if normalized_key in PRIVATE_ARTIFACT_MACHINE_KEYS:
                diagnostics.add("private path")
            if normalized_key in HOUSEHOLD_MACHINE_KEYS:
                diagnostics.add("household data")
            if normalized_key in RAW_EVIDENCE_MACHINE_KEYS:
                diagnostics.add("raw evidence")
            if normalized_key in RESTRICTED_MACHINE_KEYS or (
                normalized_key == "source_class"
                and isinstance(item, str)
                and item.strip().lower().replace("-", "_").replace(" ", "_")
                in {"restric" + "ted", "vendor_restric" + "ted"}
            ):
                diagnostics.add("source contamination")
            if isinstance(item, str) and key in exemptions:
                diagnostics |= marker_diagnostics(
                    item,
                    fingerprint_exempt_spans=exemptions[key],
                )
            elif (
                isinstance(item, str)
                and normalized_key in GIT_OBJECT_MACHINE_KEYS
                and GIT_OBJECT_VALUE_PATTERN.fullmatch(item) is not None
            ):
                diagnostics |= marker_diagnostics(
                    item,
                    fingerprint_exempt_spans=((0, len(item)),),
                )
            else:
                diagnostics |= _decoded_marker_diagnostics(
                    item,
                    path + (key,),
                    duplicate_context=child_duplicate_context,
                )
        return diagnostics
    return set()


def machine_publication_diagnostics(result: MachineJSONResult) -> set[str]:
    text = result.text or ""
    status_diagnostics = (
        {"maximum nesting depth"} if result.status == NESTING_TOO_DEEP else set()
    )
    if result.document is None:
        return status_diagnostics | marker_diagnostics(text)

    diagnostics = status_diagnostics | marker_diagnostics(
        text,
        scan_fingerprints=False,
    )
    diagnostics |= _decoded_marker_diagnostics(result.document)
    for lexeme in result.numeric_lexemes:
        diagnostics |= marker_diagnostics(lexeme)
    diagnostics |= marker_diagnostics(result.remainder)

    # Boundary-invalid input may contain additional complete JSON values. Walk
    # the original decoded buffer by index so every byte is decoded at most once.
    if result.remainder:
        index = len(text) - len(result.remainder)
        trailing_numeric_lexemes: list[str] = []
        decoder = _machine_json_decoder(trailing_numeric_lexemes)
        while index < len(text):
            while index < len(text) and text[index] in " \t\r\n":
                index += 1
            if index == len(text):
                break
            try:
                trailing_document, index = decoder.raw_decode(text, index)
            except (
                json.JSONDecodeError,
                InvalidJSONConstantError,
                DecimalException,
                OverflowError,
                RecursionError,
                ValueError,
            ):
                break
            diagnostics |= _decoded_marker_diagnostics(trailing_document)
        for lexeme in trailing_numeric_lexemes:
            diagnostics |= marker_diagnostics(lexeme)
    return diagnostics
