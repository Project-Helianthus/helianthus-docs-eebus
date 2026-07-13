#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat
import sys
import tempfile
from pathlib import Path
from typing import Any


MILESTONE = "MSP-DOCS-E2R-PUBLISH"
REPOSITORY = "Project-Helianthus/helianthus-docs-eebus"
MAX_EVIDENCE_BYTES = 1024 * 1024
SHA256_PATTERN = re.compile(r"[0-9a-f]{64}")
COMMIT_PATTERN = re.compile(r"[0-9a-f]{40}")
EVIDENCE_KEYS = {
    "schema", "version", "milestone", "state", "source", "publisher",
    "platform_contract", "artifacts", "completion_digest",
}


class AttestationError(ValueError):
    pass


def _temporary_directory_chain(path: Path, *, create: bool) -> None:
    absolute = path.absolute()
    candidates = {Path(tempfile.gettempdir()).absolute()}
    for name in ("RUNNER_TEMP", "TMPDIR"):
        if os.environ.get(name):
            candidates.add(Path(os.environ[name]).absolute())
    matches = [
        candidate
        for candidate in candidates
        if absolute == candidate or candidate in absolute.parents
    ]
    if not matches:
        raise AttestationError("attestation paths must be under a temporary root")
    current = max(matches, key=lambda item: len(item.parts))
    if not current.is_dir():
        raise AttestationError("attestation path is unsafe")
    for part in absolute.relative_to(current).parts:
        current /= part
        try:
            mode = current.lstat().st_mode
        except FileNotFoundError:
            if not create:
                raise AttestationError("attestation path is unavailable") from None
            try:
                current.mkdir()
            except FileExistsError:
                pass
            mode = current.lstat().st_mode
        if stat.S_ISLNK(mode) or not stat.S_ISDIR(mode):
            raise AttestationError("attestation path is unsafe")


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    document: dict[str, Any] = {}
    for key, value in pairs:
        if key in document:
            raise AttestationError(f"duplicate JSON key: {key}")
        document[key] = value
    return document


def _read_regular(path: Path) -> bytes:
    _temporary_directory_chain(path.parent, create=False)
    try:
        before = path.lstat()
    except OSError as error:
        raise AttestationError("evidence core is unavailable") from error
    if not stat.S_ISREG(before.st_mode) or before.st_size > MAX_EVIDENCE_BYTES:
        raise AttestationError("evidence core must be a bounded regular file")
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags)
    except OSError as error:
        raise AttestationError("evidence core cannot be opened safely") from error
    try:
        after = os.fstat(descriptor)
        if not stat.S_ISREG(after.st_mode) or (before.st_dev, before.st_ino) != (
            after.st_dev,
            after.st_ino,
        ):
            raise AttestationError("evidence core changed during validation")
        payload = os.read(descriptor, MAX_EVIDENCE_BYTES + 1)
    finally:
        os.close(descriptor)
    if len(payload) > MAX_EVIDENCE_BYTES:
        raise AttestationError("evidence core exceeds size limit")
    return payload


def _validate_evidence(raw: bytes) -> dict[str, Any]:
    try:
        document = json.loads(raw, object_pairs_hook=_unique_object)
    except (UnicodeDecodeError, json.JSONDecodeError, AttestationError) as error:
        raise AttestationError("evidence core is not strict JSON") from error
    if not isinstance(document, dict) or set(document) != EVIDENCE_KEYS:
        raise AttestationError("evidence core has an open or invalid shape")
    if (
        document["schema"] != "helianthus.docs-publication-evidence"
        or document["version"] != 1
        or document["milestone"] != MILESTONE
        or document["state"] != "PUBLISH"
    ):
        raise AttestationError("evidence core identity is invalid")
    source = document["source"]
    if (
        not isinstance(source, dict)
        or set(source) != {"repository", "commit", "verification"}
        or source.get("repository") != REPOSITORY
        or COMMIT_PATTERN.fullmatch(str(source.get("commit", ""))) is None
        or source.get("verification") not in {"git_object", "synthetic_fixture"}
    ):
        raise AttestationError("evidence source binding is invalid")
    artifacts = document["artifacts"]
    if not isinstance(artifacts, list) or not artifacts:
        raise AttestationError("evidence artifact inventory is invalid")
    for artifact in artifacts:
        if (
            not isinstance(artifact, dict)
            or set(artifact) != {"channel", "path", "member_paths", "sha256"}
            or not isinstance(artifact["channel"], str)
            or not isinstance(artifact["path"], str)
            or not isinstance(artifact["member_paths"], list)
            or any(not isinstance(member, str) for member in artifact["member_paths"])
            or SHA256_PATTERN.fullmatch(str(artifact["sha256"])) is None
        ):
            raise AttestationError("evidence artifact entry is invalid")
    completion_digest = document.pop("completion_digest")
    canonical_core = json.dumps(
        document, ensure_ascii=True, sort_keys=True, separators=(",", ":")
    ).encode()
    document["completion_digest"] = completion_digest
    if completion_digest != "sha256:" + hashlib.sha256(canonical_core).hexdigest():
        raise AttestationError("evidence completion digest differs")
    canonical_evidence = (
        json.dumps(document, ensure_ascii=True, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode()
    if raw != canonical_evidence:
        raise AttestationError("evidence core is not canonical JSON")
    return document


def _write_atomic(path: Path, payload: bytes) -> None:
    absolute_parent = path.parent.absolute()
    _temporary_directory_chain(absolute_parent, create=True)
    if path.is_symlink() or path.exists() and not path.is_file():
        raise AttestationError("attestation output path is unsafe")
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary_path = Path(temporary)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary_path, path)
    finally:
        temporary_path.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Attest a closed publication evidence core")
    parser.add_argument("--evidence-core", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        evidence_path = args.evidence_core.absolute()
        output_path = args.output.absolute()
        if evidence_path == output_path:
            raise AttestationError("attestation output must differ from evidence core")
        raw = _read_regular(evidence_path)
        evidence = _validate_evidence(raw)
        attestation = {
            "schema": "helianthus.docs-publication-attestation",
            "version": 1,
            "milestone": MILESTONE,
            "state": "ATTESTED",
            "source": evidence["source"],
            "completion_digest": evidence["completion_digest"],
            "evidence_core_sha256": hashlib.sha256(raw).hexdigest(),
            "artifact_count": len(evidence["artifacts"]),
        }
        payload = (
            json.dumps(attestation, ensure_ascii=True, sort_keys=True, separators=(",", ":"))
            + "\n"
        ).encode()
        _write_atomic(output_path, payload)
    except (OSError, AttestationError) as error:
        print(f"attestation failed: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
