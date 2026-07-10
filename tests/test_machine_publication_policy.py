from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any


REPO = Path(__file__).resolve().parents[1]
SCRIPTS = REPO / "scripts"
sys.path.insert(0, str(SCRIPTS))

from machine_publication_policy import (  # noqa: E402
    COMPLETE,
    INVALID_JSON,
    MALFORMED_SENTINEL,
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
