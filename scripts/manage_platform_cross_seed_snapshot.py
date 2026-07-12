#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml


DEFAULT_SNAPSHOT = Path(__file__).with_name("platform_cross_seed_snapshot.yaml")
SCHEMA = "helianthus.platform-cross-seed-snapshot"


def git_blob_id(content: bytes) -> str:
    header = f"blob {len(content)}\0".encode("ascii")
    return hashlib.sha1(header + content).hexdigest()


def load_snapshot(path: Path) -> dict[str, Any]:
    document = yaml.safe_load(path.read_text(encoding="utf-8"))
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
    if not isinstance(commit, str) or len(commit) != 40:
        errors.append("snapshot commit is not a full object id")
    sources = embedded_sources(document)
    if not sources:
        errors.append("snapshot has no embedded public sources")
    paths: set[str] = set()
    for path, blob, content in sources:
        if path in paths:
            errors.append(f"duplicate embedded source path: {path}")
        paths.add(path)
        actual = git_blob_id(content.encode("utf-8"))
        if actual != blob:
            errors.append(f"embedded content does not match pinned blob: {path}")
    return errors


def git(repo: Path, *args: str) -> bytes:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        capture_output=True,
    ).stdout


def source_errors(document: dict[str, Any], source_repo: Path) -> list[str]:
    errors: list[str] = []
    commit = document.get("commit")
    for path, blob, content in embedded_sources(document):
        try:
            actual_blob = git(source_repo, "rev-parse", f"{commit}:{path}").decode("ascii").strip()
            actual_content = git(source_repo, "show", f"{commit}:{path}").decode("utf-8")
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
        if not separator or not path or len(blob) != 40:
            raise ValueError("--accept-blob must be PATH=40_HEX_BLOB")
        accepted[path] = blob
    return accepted


def refreshed_snapshot(
    current: dict[str, Any],
    source_repo: Path,
    reviewed_commit: str,
    accepted: dict[str, str],
) -> dict[str, Any]:
    paths = [path for path, _, _ in embedded_sources(current)]
    if set(accepted) != set(paths):
        missing = sorted(set(paths) - set(accepted))
        extra = sorted(set(accepted) - set(paths))
        raise ValueError(f"explicit blob review mismatch; missing={missing}, extra={extra}")
    git(source_repo, "cat-file", "-e", f"{reviewed_commit}^{{commit}}")
    refreshed = dict(current)
    refreshed["commit"] = reviewed_commit
    material: dict[str, tuple[str, str]] = {}
    for path in paths:
        blob = git(source_repo, "rev-parse", f"{reviewed_commit}:{path}").decode("ascii").strip()
        if accepted[path] != blob:
            raise ValueError(f"reviewed blob does not match {path}: expected {blob}")
        content = git(source_repo, "show", f"{reviewed_commit}:{path}").decode("utf-8")
        material[path] = (blob, content)
    manifest_path = refreshed["source_manifest_path"]
    refreshed["source_manifest_blob"], refreshed["source_manifest_content"] = material[manifest_path]
    refreshed_targets = []
    for target in refreshed["targets"]:
        updated = dict(target)
        updated["blob"], updated["content"] = material[updated["path"]]
        refreshed_targets.append(updated)
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
