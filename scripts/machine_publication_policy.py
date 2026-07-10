#!/usr/bin/env python3
from __future__ import annotations

import ipaddress
import json
import re
from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Iterator


COMPLETE = "complete"
MALFORMED_SENTINEL = "malformed-sentinel"
INVALID_JSON = "invalid-json"
INVALID_UTF8 = "invalid-utf8"
TRAILING_CONTENT = "trailing-content"
MALFORMED_SENTINEL_REMAINDER = "\n!\n"
PRIVATE_IPV4_NETWORKS = (
    ((10, 0, 0, 0), 8),
    ((100, 64, 0, 0), 10),
    ((127, 0, 0, 0), 8),
    ((169, 254, 0, 0), 16),
    ((172, 16, 0, 0), 12),
    ((192, 168, 0, 0), 16),
)

PRIVATE_PATH_PATTERN = re.compile(
    r"(?:/Users/[^/\s]+/|/home/[^/\s]+/|/tmp/[^\s]+|/var/folders/[^\s]+|"
    r"[A-Za-z]:\\Users\\[^\\\s]+\\)"
)
IPV4_CANDIDATE_PATTERN = re.compile(
    r"(?<![0-9.])(?:[0-9]{1,3}\.){3}[0-9]{1,3}(?![0-9.])"
)
IPV6_CANDIDATE_PATTERN = re.compile(
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
PORTABLE_DECIMAL_INTEGER_PATTERN = re.compile(r"[+-]?[0-9]+\Z")
SECRET_PATTERN = re.compile(
    r"\b(?:token|password|passphrase|credential|secret|api[_ -]?key|"
    r"client[_ -]?secret|serial[_ -]?number|account[_ -]?(?:id|identifier|data))"
    r"\s*[:=]",
    re.IGNORECASE,
)
HOUSEHOLD_PATTERN = re.compile(r"\bhousehold[_ -]+(?:data|schedule)\s*[:=]", re.IGNORECASE)
RAW_EVIDENCE_PATTERN = re.compile(r"\braw[_ -]+evidence\s*[:=]", re.IGNORECASE)
SOURCE_CONTAMINATION_PATTERN = re.compile(
    r"\bvendor[_ -]restricted\b|\brestricted[ -]+source\b",
    re.IGNORECASE,
)


class JSONObject(dict[str, Any]):
    """A normal mapping that also retains every decoded key occurrence."""

    def __init__(self, pairs: list[tuple[str, Any]]) -> None:
        super().__init__(pairs)
        self.pairs = tuple(pairs)


class InvalidJSONConstantError(ValueError):
    pass


@dataclass(frozen=True)
class MachineJSONResult:
    status: str
    document: Any | None
    text: str | None
    remainder: str
    duplicate_keys: bool

    @property
    def boundary_valid(self) -> bool:
        return self.status in {COMPLETE, MALFORMED_SENTINEL}


def _tracked_object(pairs: list[tuple[str, Any]]) -> JSONObject:
    return JSONObject(pairs)


def _reject_constant(_: str) -> None:
    raise InvalidJSONConstantError


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
        return MachineJSONResult(INVALID_UTF8, None, None, "", False)

    decoder = json.JSONDecoder(
        object_pairs_hook=_tracked_object,
        parse_constant=_reject_constant,
        parse_float=Decimal,
        strict=True,
    )
    start = 0
    while start < len(text) and text[start] in " \t\r\n":
        start += 1
    try:
        document, end = decoder.raw_decode(text, start)
    except (json.JSONDecodeError, InvalidJSONConstantError):
        return MachineJSONResult(INVALID_JSON, None, text, text[start:], False)

    remainder = text[end:]
    duplicate_keys = has_duplicate_key(document)
    if all(char in " \t\r\n" for char in remainder):
        status = COMPLETE
    elif allow_malformed_sentinel and remainder == MALFORMED_SENTINEL_REMAINDER:
        status = MALFORMED_SENTINEL
    else:
        status = TRAILING_CONTENT
    return MachineJSONResult(status, document, text, remainder, duplicate_keys)


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


def _has_unexempted_fingerprint(
    text: str,
    exempt_spans: tuple[tuple[int, int], ...],
) -> bool:
    return any(
        not any(start <= match.start() and match.end() <= end for start, end in exempt_spans)
        for match in FINGERPRINT_PATTERN.finditer(text)
    )


def marker_diagnostics(
    text: str,
    *,
    fingerprint_exempt_spans: tuple[tuple[int, int], ...] = (),
    scan_fingerprints: bool = True,
) -> set[str]:
    diagnostics: set[str] = set()
    if PRIVATE_PATH_PATTERN.search(text):
        diagnostics.add("private path")
    if (
        MAC_PATTERN.search(text)
        or SECRET_PATTERN.search(text)
        or (
            scan_fingerprints
            and _has_unexempted_fingerprint(text, fingerprint_exempt_spans)
        )
    ):
        diagnostics.add("private identifier")
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
        candidate = match.group(0).split("%", 1)[0]
        try:
            address = ipaddress.ip_address(candidate)
        except ValueError:
            continue
        if isinstance(address, ipaddress.IPv6Address):
            diagnostics.add("network address")
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


def _integer_constant_fingerprint_exemptions(
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
    if symbol.get("kind") != "const" or symbol.get("value_kind") != "int":
        return {}
    name = symbol.get("name")
    type_text = symbol.get("type")
    signature = symbol.get("signature")
    constant_value = symbol.get("value")
    if not all(
        isinstance(item, str)
        for item in (name, type_text, signature, constant_value)
    ):
        return {}
    if PORTABLE_DECIMAL_INTEGER_PATTERN.fullmatch(constant_value) is None:
        return {}

    if type_text.startswith("untyped "):
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
    if isinstance(value, (int, Decimal)):
        return marker_diagnostics(str(value))
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
        exemptions = _integer_constant_fingerprint_exemptions(
            value,
            path,
            duplicate_context=child_duplicate_context,
        )
        for key, item in _object_pairs(value):
            diagnostics |= marker_diagnostics(key)
            if isinstance(item, str) and key in exemptions:
                diagnostics |= marker_diagnostics(
                    item,
                    fingerprint_exempt_spans=exemptions[key],
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
    if result.document is None:
        return marker_diagnostics(text)

    diagnostics = marker_diagnostics(text, scan_fingerprints=False)
    diagnostics |= _decoded_marker_diagnostics(result.document)
    diagnostics |= marker_diagnostics(result.remainder)
    return diagnostics
