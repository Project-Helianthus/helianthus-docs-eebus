#!/usr/bin/env python3
"""Emit the reproducible PLATFORM-B post-merge completion token."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import pathlib
import re
import stat
import subprocess
import sys
import urllib.parse
from datetime import datetime, timezone
from typing import Any


EXPECTED_REPOSITORY = "Project-Helianthus/helianthus-docs"
PRODUCER_ID = "MSP-DOCS-E2R-PLATFORM"
CONSUMER_ID = "MSP-DOCS-E2R-PUBLISH"
ENFORCE_THROUGH = "MSP-DOCS-E2"
MANIFEST_PATH = "docs/platform/manifests/eebus-doc-ownership.yaml"
VALIDATOR_PATH = pathlib.Path(__file__).with_name("validate_platform_contracts.py")
OID = re.compile(r"[0-9a-f]{40}\Z")
OBSERVATION_SOURCE = re.compile(r"[a-z0-9][a-z0-9._+-]*\Z")


class TokenError(Exception):
    """A fail-closed token diagnostic without input disclosure."""

    def __init__(self, category: str) -> None:
        super().__init__(category)
        self.category = category


def _git(root: pathlib.Path, *args: str) -> str:
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
        value,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")


def _sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _directory_without_symlinks(path: pathlib.Path) -> bool:
    absolute = path.absolute()
    if not absolute.anchor:
        return False
    current = pathlib.Path(absolute.anchor)
    try:
        root_stat = current.lstat()
    except OSError:
        return False
    if stat.S_ISLNK(root_stat.st_mode) or not stat.S_ISDIR(root_stat.st_mode):
        return False
    for part in absolute.parts[1:]:
        current = current / part
        try:
            item_stat = current.lstat()
        except OSError:
            return False
        if stat.S_ISLNK(item_stat.st_mode) or not stat.S_ISDIR(item_stat.st_mode):
            return False
    return True


def _load_validator() -> Any:
    spec = importlib.util.spec_from_file_location(
        "platform_contract_validator_for_token", VALIDATOR_PATH
    )
    if spec is None or spec.loader is None:
        raise TokenError("publication-token.validator")
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except Exception:
        raise TokenError("publication-token.validator") from None
    return module


def _blob_at(root: pathlib.Path, commit: str, path: str) -> tuple[str, str, bytes]:
    listing = _git(root, "ls-tree", commit, "--", path)
    if "\n" in listing or "\t" not in listing:
        raise TokenError("publication-token.git-object")
    metadata, listed_path = listing.split("\t", 1)
    fields = metadata.split()
    if listed_path != path or len(fields) != 3:
        raise TokenError("publication-token.git-object")
    mode, object_type, blob_oid = fields
    if mode not in {"100644", "100755"} or object_type != "blob":
        raise TokenError("publication-token.git-object")
    raw = subprocess.run(
        ["git", "-C", str(root), "cat-file", "blob", blob_oid],
        check=False,
        capture_output=True,
    )
    if raw.returncode != 0:
        raise TokenError("publication-token.git-object")
    return mode, blob_oid, raw.stdout


def _manifest_at(
    root: pathlib.Path, commit: str, expected_version: int, validator: Any
) -> tuple[dict[str, Any], dict[str, Any]]:
    mode, blob_oid, raw = _blob_at(root, commit, MANIFEST_PATH)
    manifest = validator._parse_manifest_bytes(raw)
    if (
        not isinstance(manifest, dict)
        or manifest.get("version") != expected_version
        or not validator._schema_valid(manifest)
        or validator._manifest_categories(manifest)
        or validator._state_categories(manifest, {})
        or (
            expected_version == 2
            and validator._enforcement_categories(manifest, ENFORCE_THROUGH)
        )
    ):
        raise TokenError("publication-token.manifest")
    return manifest, {
        "mode": mode,
        "oid": blob_oid,
        "sha256": _sha256(raw),
        "version": expected_version,
    }


def _commit_time(root: pathlib.Path, merge_oid: str) -> datetime:
    raw = _git(root, "show", "-s", "--format=%cI", merge_oid)
    try:
        parsed = datetime.fromisoformat(raw)
    except ValueError:
        raise TokenError("publication-token.commit-time") from None
    if parsed.tzinfo is None:
        raise TokenError("publication-token.commit-time")
    utc = parsed.astimezone(timezone.utc).replace(microsecond=0)
    return utc


def _validate_expiry(manifest: dict[str, Any], evaluated_at: datetime) -> None:
    for entry in manifest["entries"]:
        if entry["state"] not in {"planned", "candidate"}:
            continue
        expires = datetime.fromisoformat(
            entry["lifecycle"]["expires_at"].removesuffix("Z") + "+00:00"
        )
        if evaluated_at >= expires:
            raise TokenError(f"publication-token.{entry['state']}-expired")


def _publisher_blobs(
    root: pathlib.Path, merge_oid: str, manifest: dict[str, Any]
) -> dict[str, dict[str, str]]:
    blobs: dict[str, dict[str, str]] = {}
    for entry in manifest["entries"]:
        owner = entry["owner"]
        if owner["repository"] != "helianthus-docs" or entry["state"] != "active":
            continue
        mode, blob_oid, raw = _blob_at(root, merge_oid, owner["path"])
        blobs[entry["id"]] = {
            "mode": mode,
            "oid": blob_oid,
            "path": owner["path"],
            "sha256": _sha256(raw),
        }
    return dict(sorted(blobs.items()))


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


def _repository_matches(root: pathlib.Path, repository: str) -> bool:
    remote = _git(root, "remote", "get-url", "origin")
    return _github_repository(remote) == repository.casefold()


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=pathlib.Path, required=True)
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
    repository = args.repository
    oids = (args.base_oid, args.head_oid, args.merge_oid)
    if (
        repository != EXPECTED_REPOSITORY
        or args.pr <= 0
        or len(set(oids)) != 3
        or any(OID.fullmatch(value) is None for value in oids)
        or OBSERVATION_SOURCE.fullmatch(args.observation_source) is None
        or not _directory_without_symlinks(root)
        or not _repository_matches(root, repository)
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
    head_tree = _git(root, "rev-parse", f"{args.head_oid}^{{tree}}")
    if tree_oid != head_tree or OID.fullmatch(tree_oid) is None:
        raise TokenError("publication-token.tree-drift")

    validator = _load_validator()
    prior_manifest, prior_identity = _manifest_at(root, args.base_oid, 1, validator)
    manifest, manifest_identity = _manifest_at(root, args.merge_oid, 2, validator)
    evaluated_at = validator._parse_instant(args.evaluated_at)
    if evaluated_at is None or evaluated_at < _commit_time(root, args.merge_oid):
        raise TokenError("publication-token.evaluation-time")
    _validate_expiry(manifest, evaluated_at)

    base_tree = _git(root, "rev-parse", f"{args.base_oid}^{{tree}}")
    prior_completion = {
        "producer_id": "MSP-DOCS-E2R-PLATFORM-A",
        "consumer_id": "MSP-DOCS-E2R-PLATFORM-B",
        "merge_oid": args.base_oid,
        "tree_oid": base_tree,
    }
    prior_token_digest = _sha256(_canonical_json(prior_completion))
    observation_source = args.observation_source
    collection_members = {
        entry["id"]: entry["members"]
        for entry in manifest["entries"]
        if entry["kind"] == "canonical_collection"
    }
    evidence_core = {
        "base_oid": args.base_oid,
        "candidate_inventory": sorted(
            entry["id"] for entry in manifest["entries"] if entry["state"] == "candidate"
        ),
        "channel_registry": manifest["channel_registry"],
        "collection_members": collection_members,
        "consumer_id": CONSUMER_ID,
        "eligible_channels": manifest["eligible_channels"],
        "evaluated_at": args.evaluated_at,
        "exact_memberships": manifest["exact_memberships"],
        "head_oid": args.head_oid,
        "manifest": manifest_identity,
        "merge_oid": args.merge_oid,
        "observation_source": observation_source,
        "prior_manifest": prior_identity,
        "prior_manifest_entry_count": len(prior_manifest["entries"]),
        "prior_token_digest": prior_token_digest,
        "pr": args.pr,
        "producer_id": PRODUCER_ID,
        "publisher_blobs": _publisher_blobs(root, args.merge_oid, manifest),
        "repository": repository,
        "result": "pass",
        "tree_oid": tree_oid,
    }
    evidence_core_sha256 = _sha256(_canonical_json(evidence_core))
    return {
        "base_oid": args.base_oid,
        "consumer_id": CONSUMER_ID,
        "evidence_core": evidence_core,
        "evidence_core_sha256": evidence_core_sha256,
        "head_oid": args.head_oid,
        "merge_oid": args.merge_oid,
        "observation_source": observation_source,
        "pr": args.pr,
        "prior_token_digest": prior_token_digest,
        "producer_id": PRODUCER_ID,
        "repository": repository,
        "schema_version": 2,
        "tree_oid": tree_oid,
    }


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    publication = build_token(args)
    sys.stdout.buffer.write(_canonical_json(publication) + b"\n")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except TokenError as exc:
        print(exc.category, file=sys.stderr)
        raise SystemExit(1) from None
    except (OSError, UnicodeError, ValueError, RecursionError, MemoryError):
        print("publication-token.input", file=sys.stderr)
        raise SystemExit(1) from None
