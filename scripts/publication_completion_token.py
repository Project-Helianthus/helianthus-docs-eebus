#!/usr/bin/env python3
"""Emit the reproducible PUBLISH post-merge completion token."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat
import subprocess
import sys
import tempfile
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


EXPECTED_REPOSITORY = "Project-Helianthus/helianthus-docs-eebus"
PRODUCER_ID = "MSP-DOCS-E2R-PUBLISH"
CONSUMER_ID = "MSP-DOCS-E2R-AGGREGATE"
RENDERER_PATH = "scripts/render_publication.py"
ATTESTER_PATH = "scripts/attest_publication.py"
TOKEN_PATH = "scripts/publication_completion_token.py"
OID = re.compile(r"[0-9a-f]{40}\Z")
OBSERVATION_SOURCE = re.compile(r"[a-z0-9][a-z0-9._+-]*\Z")
INSTANT = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z\Z")


class TokenError(Exception):
    def __init__(self, category: str) -> None:
        super().__init__(category)
        self.category = category


def _git(root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(root), *args],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise TokenError("publication-token.git-object")
    return result.stdout.strip()


def _canonical_json(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=True, separators=(",", ":"), sort_keys=True
    ).encode("utf-8")


def _sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _directory_without_symlinks(path: Path) -> bool:
    absolute = path.absolute()
    temporary = Path(tempfile.gettempdir()).absolute()
    current = temporary if absolute == temporary or temporary in absolute.parents else Path(absolute.anchor)
    try:
        root_mode = current.lstat().st_mode
    except OSError:
        return False
    if stat.S_ISLNK(root_mode) or not stat.S_ISDIR(root_mode):
        return False
    for part in absolute.relative_to(current).parts:
        current /= part
        try:
            mode = current.lstat().st_mode
        except OSError:
            return False
        if stat.S_ISLNK(mode) or not stat.S_ISDIR(mode):
            return False
    return True


def _github_repository(remote: str) -> str | None:
    scp = re.fullmatch(r"(?:git@)?github\.com:(?P<path>[^?#]+)", remote, re.I)
    if scp is not None:
        path = scp.group("path")
    else:
        try:
            parsed = urllib.parse.urlsplit(remote)
            port = parsed.port
        except ValueError:
            return None
        scheme = parsed.scheme.casefold()
        if (
            scheme not in {"https", "ssh", "git"}
            or (parsed.hostname or "").casefold() != "github.com"
            or parsed.password is not None
            or parsed.query
            or parsed.fragment
        ):
            return None
        if scheme == "https" and (parsed.username is not None or port is not None):
            return None
        if scheme == "ssh" and (
            (parsed.username or "git").casefold() != "git" or port not in {None, 22}
        ):
            return None
        if scheme == "git" and (
            parsed.username is not None or port not in {None, 9418}
        ):
            return None
        path = parsed.path
    normalized = path.strip("/")
    if normalized.casefold().endswith(".git"):
        normalized = normalized[:-4]
    parts = normalized.split("/")
    if len(parts) != 2 or any(not part for part in parts):
        return None
    if any(re.fullmatch(r"[A-Za-z0-9_.-]+", part) is None for part in parts):
        return None
    return "/".join(parts).casefold()


def _blob_identity(root: Path, commit: str, path: str) -> dict[str, str]:
    listing = _git(root, "ls-tree", commit, "--", path)
    if "\n" in listing or "\t" not in listing:
        raise TokenError("publication-token.git-object")
    metadata, listed_path = listing.split("\t", 1)
    fields = metadata.split()
    if listed_path != path or len(fields) != 3:
        raise TokenError("publication-token.git-object")
    mode, object_type, oid = fields
    if mode not in {"100644", "100755"} or object_type != "blob":
        raise TokenError("publication-token.git-object")
    result = subprocess.run(
        ["git", "-C", str(root), "cat-file", "blob", oid],
        check=False,
        capture_output=True,
    )
    if result.returncode != 0:
        raise TokenError("publication-token.git-object")
    return {"mode": mode, "oid": oid, "path": path, "sha256": _sha256(result.stdout)}


def _commit_time(root: Path, merge_oid: str) -> datetime:
    raw = _git(root, "show", "-s", "--format=%cI", merge_oid)
    try:
        parsed = datetime.fromisoformat(raw)
    except ValueError:
        raise TokenError("publication-token.commit-time") from None
    if parsed.tzinfo is None:
        raise TokenError("publication-token.commit-time")
    return parsed.astimezone(timezone.utc).replace(microsecond=0)


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    document: dict[str, Any] = {}
    for key, value in pairs:
        if key in document:
            raise TokenError("publication-token.evidence")
        document[key] = value
    return document


def _strict_json(raw: bytes) -> dict[str, Any]:
    try:
        document = json.loads(raw, object_pairs_hook=_unique_object)
    except (UnicodeDecodeError, json.JSONDecodeError, TokenError):
        raise TokenError("publication-token.evidence") from None
    if not isinstance(document, dict):
        raise TokenError("publication-token.evidence")
    return document


def _publication_evidence(root: Path, merge_oid: str) -> tuple[dict[str, Any], str]:
    with tempfile.TemporaryDirectory(prefix="helianthus-publish-token-") as temporary:
        temp = Path(temporary)
        output = temp / "publication"
        evidence_path = temp / "evidence.json"
        attestation_path = temp / "attestation.json"
        render = subprocess.run(
            [
                sys.executable,
                str(root / RENDERER_PATH),
                "render",
                "--repo",
                str(root),
                "--output",
                str(output),
                "--evidence-core",
                str(evidence_path),
                "--source-commit",
                merge_oid,
            ],
            check=False,
            capture_output=True,
        )
        if render.returncode != 0:
            raise TokenError("publication-token.replay")
        verify = subprocess.run(
            [
                sys.executable,
                str(root / RENDERER_PATH),
                "verify",
                "--repo",
                str(root),
                "--output",
                str(output),
                "--source-commit",
                merge_oid,
            ],
            check=False,
            capture_output=True,
        )
        attest = subprocess.run(
            [
                sys.executable,
                str(root / ATTESTER_PATH),
                "--evidence-core",
                str(evidence_path),
                "--output",
                str(attestation_path),
            ],
            check=False,
            capture_output=True,
        )
        if verify.returncode != 0 or attest.returncode != 0:
            raise TokenError("publication-token.replay")
        try:
            raw = evidence_path.read_bytes()
            attestation = _strict_json(attestation_path.read_bytes())
        except OSError:
            raise TokenError("publication-token.evidence") from None
        evidence = _strict_json(raw)
        if (
            evidence.get("source")
            != {"repository": EXPECTED_REPOSITORY, "commit": merge_oid}
            or attestation.get("evidence_core_sha256") != _sha256(raw)
            or raw != _canonical_json(evidence) + b"\n"
        ):
            raise TokenError("publication-token.evidence")
        return evidence, _sha256(_canonical_json(evidence))


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--repository", required=True)
    parser.add_argument("--pr", type=int, required=True)
    parser.add_argument("--base-oid", required=True)
    parser.add_argument("--head-oid", required=True)
    parser.add_argument("--merge-oid", required=True)
    parser.add_argument("--evaluated-at", required=True)
    parser.add_argument("--observation-source", required=True)
    return parser


def build_token(args: argparse.Namespace) -> dict[str, Any]:
    root = args.root
    oids = (args.base_oid, args.head_oid, args.merge_oid)
    if (
        args.repository != EXPECTED_REPOSITORY
        or args.pr <= 0
        or len(set(oids)) != 3
        or any(OID.fullmatch(value) is None for value in oids)
        or OBSERVATION_SOURCE.fullmatch(args.observation_source) is None
        or INSTANT.fullmatch(args.evaluated_at) is None
        or not _directory_without_symlinks(root)
        or _github_repository(_git(root, "remote", "get-url", "origin"))
        != EXPECTED_REPOSITORY.casefold()
        or _git(root, "status", "--porcelain=v1", "--untracked-files=all")
        or _git(root, "rev-parse", "HEAD") != args.merge_oid
    ):
        raise TokenError("publication-token.identity")
    for oid in oids:
        if _git(root, "cat-file", "-t", oid) != "commit":
            raise TokenError("publication-token.git-object")
    ancestry = _git(root, "rev-list", "--parents", "-n", "1", args.merge_oid).split()
    if ancestry != [args.merge_oid, args.base_oid]:
        raise TokenError("publication-token.base-drift")
    ancestor = subprocess.run(
        ["git", "-C", str(root), "merge-base", "--is-ancestor", args.base_oid, args.head_oid],
        check=False,
        capture_output=True,
    )
    if ancestor.returncode != 0:
        raise TokenError("publication-token.base-drift")
    tree_oid = _git(root, "rev-parse", f"{args.merge_oid}^{{tree}}")
    if tree_oid != _git(root, "rev-parse", f"{args.head_oid}^{{tree}}") or OID.fullmatch(tree_oid) is None:
        raise TokenError("publication-token.tree-drift")
    evaluated_at = datetime.strptime(args.evaluated_at, "%Y-%m-%dT%H:%M:%SZ").replace(
        tzinfo=timezone.utc
    )
    if evaluated_at < _commit_time(root, args.merge_oid):
        raise TokenError("publication-token.evaluation-time")

    evidence, publication_evidence_sha256 = _publication_evidence(root, args.merge_oid)
    platform_contract = evidence.get("platform_contract")
    if not isinstance(platform_contract, dict):
        raise TokenError("publication-token.evidence")
    prior_token_digest = platform_contract.get("completion_proof_sha256")
    if not isinstance(prior_token_digest, str) or re.fullmatch(r"[0-9a-f]{64}", prior_token_digest) is None:
        raise TokenError("publication-token.evidence")
    evidence_core = {
        "base_oid": args.base_oid,
        "consumer_id": CONSUMER_ID,
        "evaluated_at": args.evaluated_at,
        "head_oid": args.head_oid,
        "merge_oid": args.merge_oid,
        "observation_source": args.observation_source,
        "pr": args.pr,
        "prior_token_digest": prior_token_digest,
        "producer_id": PRODUCER_ID,
        "publication_evidence": evidence,
        "publication_evidence_sha256": publication_evidence_sha256,
        "repository": args.repository,
        "result": "pass",
        "token_producer": _blob_identity(root, args.merge_oid, TOKEN_PATH),
        "tree_oid": tree_oid,
    }
    return {
        "base_oid": args.base_oid,
        "consumer_id": CONSUMER_ID,
        "evidence_core": evidence_core,
        "evidence_core_sha256": _sha256(_canonical_json(evidence_core)),
        "head_oid": args.head_oid,
        "merge_oid": args.merge_oid,
        "observation_source": args.observation_source,
        "pr": args.pr,
        "prior_token_digest": prior_token_digest,
        "producer_id": PRODUCER_ID,
        "repository": args.repository,
        "schema_version": 2,
        "tree_oid": tree_oid,
    }


def main(argv: list[str] | None = None) -> int:
    envelope = build_token(_parser().parse_args(argv))
    sys.stdout.buffer.write(_canonical_json(envelope) + b"\n")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except TokenError as error:
        print(error.category, file=sys.stderr)
        raise SystemExit(1) from None
    except (OSError, UnicodeError, ValueError, RecursionError, MemoryError):
        print("publication-token.input", file=sys.stderr)
        raise SystemExit(1) from None
