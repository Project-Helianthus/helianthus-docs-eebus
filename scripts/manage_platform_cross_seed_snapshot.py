#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml


DEFAULT_SNAPSHOT = Path(__file__).with_name("platform_cross_seed_snapshot.yaml")
SCHEMA = "helianthus.platform-cross-seed-snapshot"
MAX_SNAPSHOT_BYTES = 2 * 1024 * 1024
MAX_PUBLIC_SOURCE_BYTES = 512 * 1024
MAX_TOTAL_PUBLIC_SOURCE_BYTES = 2 * 1024 * 1024
MAX_GIT_METADATA_BYTES = 4096
CANONICAL_TARGETS = (
    "docs/platform/README.md",
    "docs/platform/cross-runtime-envelope.md",
    "docs/platform/eebus-ha-network-proof.md",
    "docs/platform/eebus-interop-smoke.md",
    "docs/platform/eebus-raw-first-contract.md",
    "docs/platform/hash-auth-binding.md",
    "docs/platform/ownership-and-doc-gates.md",
    "docs/platform/ownership-validation.md",
    "docs/platform/promotion-and-consumer-contract.md",
    "docs/platform/raw-correlation-and-leaf-promotion.md",
    "docs/platform/shared-registry-boundary.md",
)
OBJECT_ID_PATTERN = re.compile(r"[0-9a-f]{40}\Z")


def git_blob_id(content: bytes) -> str:
    header = f"blob {len(content)}\0".encode("ascii")
    return hashlib.sha1(header + content).hexdigest()


def load_snapshot(path: Path) -> dict[str, Any]:
    if not path.is_file() or path.is_symlink():
        raise ValueError("snapshot must be a regular file")
    if path.stat().st_size > MAX_SNAPSHOT_BYTES:
        raise ValueError("snapshot exceeds size limit")
    with path.open("rb") as stream:
        raw = stream.read(MAX_SNAPSHOT_BYTES + 1)
    if len(raw) > MAX_SNAPSHOT_BYTES:
        raise ValueError("snapshot exceeds size limit")
    document = yaml.safe_load(raw.decode("utf-8"))
    if not isinstance(document, dict):
        raise ValueError("snapshot must be a mapping")
    return document


def embedded_sources(document: dict[str, Any]) -> list[tuple[str, str, str]]:
    sources: list[tuple[str, str, str]] = []
    manifest_path = document.get("source_manifest_path")
    manifest_blob = document.get("source_manifest_blob")
    manifest_content = document.get("source_manifest_content")
    if all(isinstance(value, str) for value in (manifest_path, manifest_blob, manifest_content)):
        sources.append((manifest_path, manifest_blob, manifest_content))
    targets = document.get("targets")
    if isinstance(targets, list):
        for target in targets:
            if not isinstance(target, dict):
                continue
            path = target.get("path")
            blob = target.get("blob")
            content = target.get("content")
            if all(isinstance(value, str) for value in (path, blob, content)):
                sources.append((path, blob, content))
    return sources


def internal_errors(document: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if document.get("schema") != SCHEMA or document.get("version") != "1":
        errors.append("snapshot schema/version is invalid")
    commit = document.get("commit")
    if not isinstance(commit, str) or OBJECT_ID_PATTERN.fullmatch(commit) is None:
        errors.append("snapshot commit is not a full object id")
    sources = embedded_sources(document)
    if not sources:
        errors.append("snapshot has no embedded public sources")
    paths: set[str] = set()
    for path, blob, content in sources:
        if path in paths:
            errors.append(f"duplicate embedded source path: {path}")
        paths.add(path)
        if OBJECT_ID_PATTERN.fullmatch(blob) is None:
            errors.append(f"embedded source blob is not a full object id: {path}")
        actual = git_blob_id(content.encode("utf-8"))
        if actual != blob:
            errors.append(f"embedded content does not match pinned blob: {path}")
    targets = document.get("targets")
    target_paths = (
        tuple(target.get("path") for target in targets if isinstance(target, dict))
        if isinstance(targets, list)
        else ()
    )
    if target_paths != CANONICAL_TARGETS:
        errors.append("snapshot does not contain the complete canonical platform corpus")
    try:
        manifest = yaml.safe_load(document.get("source_manifest_content", ""))
    except yaml.YAMLError:
        manifest = None
    entries = manifest.get("entries") if isinstance(manifest, dict) else None
    envelope = next(
        (
            entry
            for entry in entries or []
            if isinstance(entry, dict)
            and entry.get("id") == "cross-runtime-platform-contracts"
        ),
        None,
    )
    if (
        not isinstance(envelope, dict)
        or envelope.get("canonical") is not True
        or envelope.get("state") != "active"
        or envelope.get("owner")
        != {
            "repository": "helianthus-docs-ebus",
            "path": "docs/platform/cross-runtime-envelope.md",
        }
    ):
        errors.append("source manifest does not canonically bind cross-runtime-envelope")
    return errors


def git(repo: Path, *args: str, max_output: int = MAX_GIT_METADATA_BYTES) -> bytes:
    command = ["git", "-C", str(repo), *args]
    result = subprocess.run(
        command,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )
    if result.returncode != 0:
        raise subprocess.CalledProcessError(result.returncode, command)
    if len(result.stdout) > max_output:
        raise ValueError("git output exceeds size limit")
    return result.stdout


def public_git_blob(repo: Path, commit: str, path: str) -> tuple[str, bytes]:
    blob = git(repo, "rev-parse", f"{commit}:{path}").decode("ascii").strip()
    if OBJECT_ID_PATTERN.fullmatch(blob) is None:
        raise ValueError(f"public source blob id is invalid: {path}")
    size_text = git(repo, "cat-file", "-s", blob).decode("ascii").strip()
    try:
        size = int(size_text)
    except ValueError as error:
        raise ValueError(f"public source size is invalid: {path}") from error
    if size < 0 or size > MAX_PUBLIC_SOURCE_BYTES:
        raise ValueError(f"public source exceeds size limit: {path}")
    content = git(repo, "cat-file", "blob", blob, max_output=size)
    if len(content) != size:
        raise ValueError(f"public source size changed while reading: {path}")
    return blob, content


def source_errors(document: dict[str, Any], source_repo: Path) -> list[str]:
    errors: list[str] = []
    commit = document.get("commit")
    total_size = 0
    for path, blob, content in embedded_sources(document):
        try:
            actual_blob, raw_content = public_git_blob(source_repo, commit, path)
            total_size += len(raw_content)
            if total_size > MAX_TOTAL_PUBLIC_SOURCE_BYTES:
                errors.append("pinned public sources exceed aggregate size limit")
                break
            actual_content = raw_content.decode("utf-8")
        except ValueError as error:
            errors.append(str(error))
            continue
        except (subprocess.CalledProcessError, UnicodeDecodeError):
            errors.append(f"pinned public source is unavailable: {path}")
            continue
        if actual_blob != blob:
            errors.append(f"public source blob differs from snapshot: {path}")
        if actual_content != content:
            errors.append(f"public source content differs from snapshot: {path}")
    return errors


def parse_acceptances(values: list[str]) -> dict[str, str]:
    accepted: dict[str, str] = {}
    for value in values:
        path, separator, blob = value.partition("=")
        if (
            not separator
            or not path
            or OBJECT_ID_PATTERN.fullmatch(blob) is None
        ):
            raise ValueError("--accept-blob must be PATH=40_HEX_BLOB")
        accepted[path] = blob
    return accepted


def refreshed_snapshot(
    current: dict[str, Any],
    source_repo: Path,
    reviewed_commit: str,
    accepted: dict[str, str],
) -> dict[str, Any]:
    if OBJECT_ID_PATTERN.fullmatch(reviewed_commit) is None:
        raise ValueError("--reviewed-commit must be a canonical 40-hex commit id")
    manifest_path = current.get("source_manifest_path")
    if not isinstance(manifest_path, str):
        raise ValueError("snapshot source manifest path is invalid")
    paths = [manifest_path, *CANONICAL_TARGETS]
    if set(accepted) != set(paths):
        missing = sorted(set(paths) - set(accepted))
        extra = sorted(set(accepted) - set(paths))
        raise ValueError(f"explicit blob review mismatch; missing={missing}, extra={extra}")
    resolved_commit = git(
        source_repo,
        "rev-parse",
        f"{reviewed_commit}^{{commit}}",
    ).decode("ascii").strip()
    if resolved_commit != reviewed_commit:
        raise ValueError("--reviewed-commit must be a canonical 40-hex commit id")
    refreshed = dict(current)
    refreshed["commit"] = reviewed_commit
    material: dict[str, tuple[str, str]] = {}
    total_size = 0
    for path in paths:
        blob, raw_content = public_git_blob(source_repo, reviewed_commit, path)
        total_size += len(raw_content)
        if total_size > MAX_TOTAL_PUBLIC_SOURCE_BYTES:
            raise ValueError("public sources exceed aggregate size limit")
        if accepted[path] != blob:
            raise ValueError(f"reviewed blob does not match {path}: expected {blob}")
        content = raw_content.decode("utf-8")
        material[path] = (blob, content)
    refreshed["source_manifest_blob"], refreshed["source_manifest_content"] = material[manifest_path]
    refreshed_targets = [
        {"path": path, "blob": material[path][0], "content": material[path][1]}
        for path in CANONICAL_TARGETS
    ]
    refreshed["targets"] = refreshed_targets
    return refreshed


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(
        description=(
            "Check the embedded pinned public blobs, or explicitly refresh them after "
            "reviewing every commit/path blob id. Refresh never changes the canonical "
            "snapshot unless --output names it explicitly."
        )
    )
    result.add_argument("--snapshot", type=Path, default=DEFAULT_SNAPSHOT)
    subcommands = result.add_subparsers(dest="command", required=True)
    check = subcommands.add_parser("check", help="verify embedded blobs and optionally a public git checkout")
    check.add_argument("--source-repo", type=Path)
    refresh = subcommands.add_parser("refresh", help="render a review-gated snapshot to --output")
    refresh.add_argument("--source-repo", type=Path, required=True)
    refresh.add_argument("--reviewed-commit", required=True)
    refresh.add_argument("--accept-blob", action="append", default=[], metavar="PATH=40_HEX_BLOB")
    refresh.add_argument("--output", type=Path, required=True)
    return result


def main() -> int:
    args = parser().parse_args()
    try:
        document = load_snapshot(args.snapshot)
        if args.command == "check":
            errors = internal_errors(document)
            if args.source_repo is not None:
                errors.extend(source_errors(document, args.source_repo))
            for error in sorted(set(errors)):
                print(error, file=sys.stderr)
            return 1 if errors else 0

        accepted = parse_acceptances(args.accept_blob)
        refreshed = refreshed_snapshot(
            document,
            args.source_repo,
            args.reviewed_commit,
            accepted,
        )
        rendered = yaml.safe_dump(refreshed, sort_keys=False, allow_unicode=False)
        args.output.write_text(rendered, encoding="utf-8")
        print(f"wrote review candidate {args.output}")
        print(f"sha256 {hashlib.sha256(rendered.encode('utf-8')).hexdigest()}")
        print("review the diff, then update the validator snapshot digest explicitly")
        return 0
    except (OSError, ValueError, subprocess.CalledProcessError, UnicodeDecodeError) as error:
        print(f"snapshot operation failed: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
