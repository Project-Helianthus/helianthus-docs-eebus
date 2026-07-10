from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any
from unittest import mock


REPO = Path(__file__).resolve().parents[1]
SCRIPTS = REPO / "scripts"
sys.path.insert(0, str(SCRIPTS))

from machine_publication_policy import (  # noqa: E402
    COMPLETE,
    INVALID_JSON,
    MALFORMED_SENTINEL,
    MAX_MACHINE_JSON_DEPTH,
    NESTING_TOO_DEEP,
    TRAILING_CONTENT,
    JSONObject,
    classify_ipv4,
    decode_machine_json,
    decoded_text_occurrences,
    machine_publication_diagnostics,
    marker_diagnostics,
)


API_VALIDATOR = SCRIPTS / "validate_api_surface_v1.py"
POLICY_VALIDATOR = SCRIPTS / "validate_repository_policy.py"
POSITIVE_REL = Path("api/fixtures/v1/positive/kinds-types-signatures.json")
MALFORMED_REL = Path("api/fixtures/v1/negative/malformed.json")


def ipv4(first: int, second: int, third: int, fourth: int) -> str:
    return f"{first}.{second}.{third}.{fourth}"


def copy_repo(tmp_path: Path) -> Path:
    destination = tmp_path / "repo"
    shutil.copytree(
        REPO,
        destination,
        ignore=shutil.ignore_patterns(".git", ".pytest_cache", "__pycache__"),
    )
    return destination


def run(script: Path, repo: Path) -> subprocess.CompletedProcess[str]:
    arguments = [sys.executable, str(script), "--repo", str(repo)] if script == API_VALIDATOR else [sys.executable, str(script), "--repo", str(repo)]
    return subprocess.run(
        arguments,
        cwd=repo,
        check=False,
        text=True,
        capture_output=True,
    )


def write_json(path: Path, document: Any) -> None:
    path.write_text(json.dumps(document, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


class MachinePublicationPolicyTests(unittest.TestCase):
    def test_portable_depth_limit_precedes_recursive_decoding_and_walks(self) -> None:
        shadowed = (
            b'{"safe":"clean","safe":"peer '
            b'\\u0031\\u0032\\u0037\\u002e0\\u002e0\\u002e1"}'
        )
        at_limit = (
            b"[" * (MAX_MACHINE_JSON_DEPTH - 1)
            + shadowed
            + b"]" * (MAX_MACHINE_JSON_DEPTH - 1)
        )
        accepted = decode_machine_json(at_limit)
        self.assertEqual(accepted.status, COMPLETE)
        self.assertTrue(accepted.duplicate_keys)
        self.assertEqual(machine_publication_diagnostics(accepted), {"private network"})

        for depth in (MAX_MACHINE_JSON_DEPTH + 1, 2000):
            with self.subTest(depth=depth):
                result = decode_machine_json(
                    b"[" * (depth - 1) + shadowed + b"]" * (depth - 1)
                )
                self.assertEqual(result.status, NESTING_TOO_DEEP)
                self.assertFalse(result.duplicate_keys)
                self.assertEqual(
                    machine_publication_diagnostics(result),
                    {"maximum nesting depth"},
                )

        braces_in_a_string = json.dumps("[" * 1000).encode("utf-8")
        self.assertEqual(decode_machine_json(braces_in_a_string).status, COMPLETE)

    def test_decoder_recursion_error_is_a_deterministic_invalid_json_result(self) -> None:
        with mock.patch.object(
            json.JSONDecoder,
            "raw_decode",
            side_effect=RecursionError,
        ):
            first = decode_machine_json(b'{"safe":true}')
            second = decode_machine_json(b'{"safe":true}')
        self.assertEqual(first, second)
        self.assertEqual(first.status, INVALID_JSON)
        self.assertEqual(machine_publication_diagnostics(first), set())

    def test_strict_decode_preserves_duplicate_key_occurrences(self) -> None:
        result = decode_machine_json(b'{"key":"first","key":"second"}\n')
        self.assertEqual(result.status, COMPLETE)
        self.assertTrue(result.duplicate_keys)
        self.assertIsInstance(result.document, JSONObject)
        self.assertEqual(result.document.pairs, (("key", "first"), ("key", "second")))
        self.assertEqual(list(decoded_text_occurrences(result.document)), ["key", "first", "key", "second"])

    def test_ordinary_artifact_requires_one_value_plus_json_whitespace(self) -> None:
        for suffix in (b"", b"\n", b" \t\r\n"):
            with self.subTest(suffix=suffix):
                result = decode_machine_json(b'{"ok":true}' + suffix)
                self.assertEqual(result.status, COMPLETE)
                self.assertTrue(result.boundary_valid)
        self.assertEqual(decode_machine_json(b"\xc2\xa0{\"ok\":true}").status, INVALID_JSON)

    def test_numeric_lexemes_drive_long_identifier_diagnostics(self) -> None:
        tokens = (
            "7" * 40,
            "0." + "8" * 40,
            "1" + "0" * 39 + "e-39",
            "1e" + "9" * 40,
            "1e-" + "9" * 40,
        )
        for token in tokens:
            with self.subTest(token=token[:12]):
                result = decode_machine_json(f'{{"value":{token}}}'.encode("ascii"))
                self.assertEqual(result.status, COMPLETE)
                self.assertEqual(result.numeric_lexemes, (token,))
                self.assertEqual(
                    machine_publication_diagnostics(result),
                    {"private identifier"},
                )

    def test_ordinary_numeric_lexemes_are_preserved_without_markers(self) -> None:
        result = decode_machine_json(b'{"values":[0,-12,1.25,6.02e23,1e-5]}')
        self.assertEqual(result.status, COMPLETE)
        self.assertEqual(
            result.numeric_lexemes,
            ("0", "-12", "1.25", "6.02e23", "1e-5"),
        )
        self.assertEqual(machine_publication_diagnostics(result), set())

    def test_only_exact_malformed_sentinel_is_boundary_valid_when_enabled(self) -> None:
        canonical = b'{"ok":true}\n!\n'
        enabled = decode_machine_json(canonical, allow_malformed_sentinel=True)
        disabled = decode_machine_json(canonical)
        self.assertEqual(enabled.status, MALFORMED_SENTINEL)
        self.assertTrue(enabled.boundary_valid)
        self.assertEqual(disabled.status, TRAILING_CONTENT)
        for tail in (b"!\n", b"\n!", b"\n!!\n", b"\r\n!\n", b"\n!\n "):
            with self.subTest(tail=tail):
                result = decode_machine_json(
                    b'{"ok":true}' + tail,
                    allow_malformed_sentinel=True,
                )
                self.assertEqual(result.status, TRAILING_CONTENT)
                self.assertFalse(result.boundary_valid)

    def test_second_values_and_escaped_tail_content_are_trailing_content(self) -> None:
        tails = (
            b"\n{}\n",
            b"\ntrue\n",
            b"\n\"second\"\n",
            b"\\u0021",
            b"\n\\u0021\n",
            b"\n\"\\u0021\"\n",
        )
        for tail in tails:
            with self.subTest(tail=tail):
                result = decode_machine_json(
                    b'{"ok":true}' + tail,
                    allow_malformed_sentinel=True,
                )
                self.assertEqual(result.status, TRAILING_CONTENT)

    def test_ipv4_candidate_boundaries_allow_underscore_and_letters(self) -> None:
        private = ipv4(127, 0, 0, 1)
        self.assertEqual(marker_diagnostics(f"_{private}_"), {"private network"})
        self.assertEqual(marker_diagnostics(f"x{private}y"), {"private network"})
        self.assertEqual(marker_diagnostics(f"9{private}"), set())
        self.assertEqual(marker_diagnostics(f"{private}.5"), set())

    def test_invalid_ipv4_octets_are_ignored(self) -> None:
        for candidate in (ipv4(256, 0, 0, 1), ipv4(999, 999, 999, 999)):
            with self.subTest(candidate=candidate):
                self.assertIsNone(classify_ipv4(candidate))
                self.assertEqual(marker_diagnostics(candidate), set())

    def test_leading_zero_ipv4_spellings_are_decimal_and_deterministic(self) -> None:
        private = ".".join(("010", "000", "000", "001"))
        public = ".".join(("008", "008", "008", "008"))
        self.assertEqual(classify_ipv4(private), "private network")
        self.assertEqual(classify_ipv4(public), "network address")

    def test_every_fixed_private_cidr_boundary_is_exact(self) -> None:
        private = (
            (10, 0, 0, 0),
            (10, 255, 255, 255),
            (100, 64, 0, 0),
            (100, 127, 255, 255),
            (127, 0, 0, 0),
            (127, 255, 255, 255),
            (169, 254, 0, 0),
            (169, 254, 255, 255),
            (172, 16, 0, 0),
            (172, 31, 255, 255),
            (192, 168, 0, 0),
            (192, 168, 255, 255),
        )
        outside = (
            (9, 255, 255, 255),
            (11, 0, 0, 0),
            (100, 63, 255, 255),
            (100, 128, 0, 0),
            (126, 255, 255, 255),
            (128, 0, 0, 0),
            (169, 253, 255, 255),
            (169, 255, 0, 0),
            (172, 15, 255, 255),
            (172, 32, 0, 0),
            (192, 167, 255, 255),
            (192, 169, 0, 0),
        )
        for octets in private:
            with self.subTest(private=octets):
                self.assertEqual(classify_ipv4(ipv4(*octets)), "private network")
        for octets in outside:
            with self.subTest(outside=octets):
                self.assertEqual(classify_ipv4(ipv4(*octets)), "network address")

    def test_reserved_and_special_use_ipv4_remain_network_addresses(self) -> None:
        addresses = (
            (0, 0, 0, 0),
            (192, 0, 2, 1),
            (198, 51, 100, 1),
            (203, 0, 113, 1),
            (224, 0, 0, 1),
            (255, 255, 255, 255),
        )
        for octets in addresses:
            with self.subTest(octets=octets):
                self.assertEqual(classify_ipv4(ipv4(*octets)), "network address")

    def test_raw_and_decoded_shadowed_markers_share_one_result_set(self) -> None:
        private = ipv4(127, 0, 0, 1)
        raw = (
            '{"value":"clean","value":"peer '
            + private.replace(".", "\\u002e")
            + '"}'
        ).encode("utf-8")
        result = decode_machine_json(raw)
        self.assertEqual(result.status, COMPLETE)
        self.assertEqual(machine_publication_diagnostics(result), {"private network"})

    def test_machine_policy_covers_markdown_credential_and_source_categories(self) -> None:
        cases = (
            ({"private_key": "synthetic"}, "private identifier"),
            ({"credential": "synthetic"}, "private identifier"),
            ({"note": "-----BEGIN CERTIFICATE-----"}, "private identifier"),
            ({"note": "00:11:22:33:44:55"}, "private identifier"),
            ({"note": "E" * 40}, "private identifier"),
            ({"local_identity": "synthetic"}, "private identifier"),
            ({"stable peer identifier": "synthetic"}, "private identifier"),
            ({"pairing-history": "synthetic"}, "private identifier"),
            ({"raw_ski_id": "synthetic"}, "private identifier"),
            ({"SHIPID": "synthetic"}, "private identifier"),
            ({"raw SKIID": "synthetic"}, "private identifier"),
            ({"note": "raw SHIP ID is ABCDEFGH"}, "private identifier"),
            ({"note": "/home/synthetic/private.json"}, "private path"),
            ({"private_artifact_reference": "redacted"}, "private path"),
            ({"private_artifact_retained": "private-store"}, "private path"),
            ({"note": "peer fd00::1"}, "network address"),
            ({"restricted_document": "synthetic"}, "source contamination"),
            ({"note": "restricted-document"}, "source contamination"),
            ({"note": "restricted vendor documents"}, "source contamination"),
            ({"note": "paraphrased from restricted material"}, "source contamination"),
            ({"source_class": "restricted"}, "source contamination"),
            ({"source-class": "vendor-restricted"}, "source contamination"),
        )
        for document, category in cases:
            with self.subTest(document=document):
                result = decode_machine_json(json.dumps(document).encode("utf-8"))
                self.assertIn(category, machine_publication_diagnostics(result))

    def test_escaped_keys_duplicates_and_trailing_values_cannot_bypass_policy(self) -> None:
        raw = (
            b'{"pass\\u0077ord":"first","pass\\u0077ord":"second"}'
            b' {"source_cl\\u0061ss":"restr\\u0069cted"}'
        )
        result = decode_machine_json(raw)
        self.assertEqual(result.status, TRAILING_CONTENT)
        self.assertTrue(result.duplicate_keys)
        self.assertEqual(
            machine_publication_diagnostics(result),
            {"private identifier", "source contamination"},
        )

    def test_exact_decimal_integer_value_and_derived_signature_exempt_only_fingerprint(self) -> None:
        for value in ("1" * 41, "+" + "2" * 101, "-" + "3" * 101):
            with self.subTest(value=value[:2]):
                document = {
                    "packages": [
                        {
                            "symbols": [
                                {
                                    "kind": "const",
                                    "name": "Large",
                                    "type": "untyped int",
                                    "signature": f"const Large = {value}",
                                    "value_kind": "int",
                                    "value": value,
                                }
                            ]
                        }
                    ]
                }
                result = decode_machine_json(json.dumps(document).encode("utf-8"))
                self.assertEqual(machine_publication_diagnostics(result), set())

    def test_large_digit_data_outside_exact_integer_slots_remains_private(self) -> None:
        digits = "4" * 50
        documents = (
            {"data": digits},
            {digits: "data"},
            {"data": int(digits)},
            {
                "packages": [
                    {
                        "symbols": [
                            {
                                "kind": "const",
                                "name": "Text",
                                "type": "untyped string",
                                "signature": f'const Text = "{digits}"',
                                "value_kind": "string",
                                "value": f'"{digits}"',
                            }
                        ]
                    }
                ]
            },
        )
        for document in documents:
            with self.subTest(document=document):
                result = decode_machine_json(json.dumps(document).encode("utf-8"))
                self.assertIn(
                    "private identifier",
                    machine_publication_diagnostics(result),
                )

    def test_hex_and_malformed_integer_text_are_not_exempt(self) -> None:
        for value in ("A" * 40, "5" * 50 + "g", "0x" + "B" * 40):
            with self.subTest(value=value[:3]):
                document = {
                    "packages": [
                        {
                            "symbols": [
                                {
                                    "kind": "const",
                                    "name": "Invalid",
                                    "type": "untyped int",
                                    "signature": f"const Invalid = {value}",
                                    "value_kind": "int",
                                    "value": value,
                                }
                            ]
                        }
                    ]
                }
                result = decode_machine_json(json.dumps(document).encode("utf-8"))
                self.assertIn(
                    "private identifier",
                    machine_publication_diagnostics(result),
                )

    def test_duplicate_shadowed_integer_value_fails_closed(self) -> None:
        fingerprint = "C" * 40
        raw = (
            '{"packages":[{"symbols":[{'
            '"kind":"const","name":"Shadowed","type":"untyped int",'
            '"signature":"const Shadowed = 1","value_kind":"int",'
            f'"value":"1","value":"{fingerprint}"'
            "}]}]}"
        ).encode("utf-8")
        result = decode_machine_json(raw)
        self.assertTrue(result.duplicate_keys)
        self.assertIn("private identifier", machine_publication_diagnostics(result))

    def test_other_markers_and_non_value_signature_fingerprints_are_not_exempt(self) -> None:
        value = "6" * 50
        cases = (
            ("/Users/synthetic/type/", "private path"),
            ("peer-" + ipv4(127, 0, 0, 1), "private network"),
            ("token=synthetic", "private identifier"),
            ("vendor_restricted", "source contamination"),
        )
        for type_text, category in cases:
            with self.subTest(category=category):
                document = {
                    "packages": [
                        {
                            "symbols": [
                                {
                                    "kind": "const",
                                    "name": "Large",
                                    "type": type_text,
                                    "signature": f"const Large {type_text} = {value}",
                                    "value_kind": "int",
                                    "value": value,
                                }
                            ]
                        }
                    ]
                }
                result = decode_machine_json(json.dumps(document).encode("utf-8"))
                self.assertIn(category, machine_publication_diagnostics(result))

        fingerprint = "D" * 40
        document["packages"][0]["symbols"][0]["name"] = fingerprint
        document["packages"][0]["symbols"][0]["signature"] = (
            f"const {fingerprint} vendor_restricted = {value}"
        )
        result = decode_machine_json(json.dumps(document).encode("utf-8"))
        self.assertIn("private identifier", machine_publication_diagnostics(result))

    def test_both_validators_report_the_same_shared_marker_category(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = copy_repo(Path(tmp))
            artifact = repo / POSITIVE_REL
            document = json.loads(artifact.read_text(encoding="utf-8"))
            constant = next(
                symbol
                for symbol in document["packages"][0]["symbols"]
                if symbol["kind"] == "const" and symbol["name"] == "TypedLimit"
            )
            value = "peer " + ipv4(127, 0, 0, 1)
            constant["value"] = value
            constant["signature"] = f"const TypedLimit uint64 = {value}"
            write_json(artifact, document)
            api = run(API_VALIDATOR, repo)
            policy = run(POLICY_VALIDATOR, repo)
            expected = f"{POSITIVE_REL.as_posix()}: private network"
            self.assertEqual(api.returncode, 1, api.stderr)
            self.assertEqual(policy.returncode, 1, policy.stderr)
            self.assertIn(expected, api.stderr)
            self.assertIn(expected, policy.stderr)

    def test_both_validators_reject_escaped_keys_shadowed_values_and_tails(self) -> None:
        mutations = (
            (
                lambda text: text.replace(
                    "{\n",
                    '{\n  "pass\\u0077ord": "synthetic",\n',
                    1,
                ),
                "private identifier",
            ),
            (
                lambda text: text.replace(
                    '"name": "TypedLimit",',
                    '"name": "TypedLimit",\n          "name": "private\\u005fkey: synthetic",',
                    1,
                ),
                "private identifier",
            ),
            (
                lambda text: text
                + '\n{"source_cl\\u0061ss":"restr\\u0069cted"}\n',
                "source contamination",
            ),
        )
        for mutate, category in mutations:
            with self.subTest(category=category), tempfile.TemporaryDirectory() as tmp:
                repo = copy_repo(Path(tmp))
                artifact = repo / POSITIVE_REL
                artifact.write_text(
                    mutate(artifact.read_text(encoding="utf-8")),
                    encoding="utf-8",
                )
                for result in (run(API_VALIDATOR, repo), run(POLICY_VALIDATOR, repo)):
                    self.assertEqual(result.returncode, 1, result.stderr)
                    self.assertIn(
                        f"{POSITIVE_REL.as_posix()}: {category}",
                        result.stderr,
                    )
                    self.assertNotIn("synthetic", result.stderr)
                    self.assertNotIn("Traceback", result.stderr)

    def test_repository_policy_rejects_second_values_and_escaped_tails(self) -> None:
        for tail in ("{}\n", "\\u0021\n", '"\\u0021"\n'):
            with self.subTest(tail=tail), tempfile.TemporaryDirectory() as tmp:
                repo = copy_repo(Path(tmp))
                artifact = repo / POSITIVE_REL
                artifact.write_text(artifact.read_text(encoding="utf-8") + tail, encoding="utf-8")
                result = run(POLICY_VALIDATOR, repo)
                self.assertEqual(result.returncode, 1, result.stderr)
                self.assertIn(f"{POSITIVE_REL.as_posix()}: machine publication boundary", result.stderr)

    def test_api_validator_reports_trailing_content_as_a_boundary_failure(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = copy_repo(Path(tmp))
            artifact = repo / POSITIVE_REL
            artifact.write_text(artifact.read_text(encoding="utf-8") + "{}\n", encoding="utf-8")
            result = run(API_VALIDATOR, repo)
            self.assertEqual(result.returncode, 1, result.stderr)
            self.assertIn(f"{POSITIVE_REL.as_posix()}: machine publication boundary", result.stderr)

    def test_repository_policy_requires_the_exact_malformed_fixture_sentinel(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = copy_repo(Path(tmp))
            artifact = repo / MALFORMED_REL
            text = artifact.read_text(encoding="utf-8")
            self.assertTrue(text.endswith("\n!\n"))
            artifact.write_text(text[:-3] + "\n!!\n", encoding="utf-8")
            result = run(POLICY_VALIDATOR, repo)
            self.assertEqual(result.returncode, 1, result.stderr)
            self.assertIn(f"{MALFORMED_REL.as_posix()}: machine publication boundary", result.stderr)

    def test_shared_policy_never_uses_dynamic_ipv4_private_classification(self) -> None:
        source = (SCRIPTS / "machine_publication_policy.py").read_text(encoding="utf-8")
        self.assertNotIn("is_" + "private", source)


if __name__ == "__main__":
    unittest.main()
