#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import html
import json
import os
import posixpath
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import urllib.parse
from pathlib import Path, PurePosixPath
from typing import Any

REGISTRY_PATH = "scripts/publication_channels.yaml"
REPOSITORY = "Project-Helianthus/helianthus-docs-eebus"
MILESTONE = "MSP-DOCS-E2R-PUBLISH"
MAX_CONTROL_BYTES = 1024 * 1024
MAX_MEMBER_BYTES = 2 * 1024 * 1024
CHANNELS = {"search", "sitemap", "versioned_bundle", "release_bundle"}
PATH_PATTERN = re.compile(r"[A-Za-z0-9._/-]+")
COMMIT_PATTERN = re.compile(r"[0-9a-f]{40}")
UNICODE_ESCAPE = re.compile(r"\\u([0-9a-fA-F]{4})")
HEX_ESCAPE = re.compile(r"\\x([0-9a-fA-F]{2})")
PLATFORM_CONTRACT = {
    "source_repository": "Project-Helianthus/helianthus-docs-ebus",
    "source_merge": "8872f65b888048db001bc640ae04a4f460ee8db1",
    "source_manifest_path": "docs/platform/manifests/eebus-doc-ownership.yaml",
    "source_manifest_blob_mode": "100644",
    "source_manifest_oid": "1f7c7c0a94504614949e3478387fca4def079c2e",
    "source_manifest_sha256": "3f7b16f32ded7f16b12ecd644d361f315df1ba6d10d462a9c9054585774fd04e",
    "completion_proof_sha256": "0b695b603f19dff35b857ddf47e03fe0ae02ac39ca89c353de8482872fd8c3de",
    "channel_registry": {
        "canonical": {
            "visibility": "stable",
            "owner": "canonical_documentation_owner",
        }
    },
    "eligible_channels": {
        member: ["canonical"]
        for member in [
            "cross-runtime-platform-contracts",
            "eebus-api-v1",
            "eebus-architecture",
            "eebus-protocol",
            "platform-cross-runtime-envelope",
            "platform-hash-auth-binding",
            "platform-ownership-validation",
            "platform-promotion-consumer-contract",
            "platform-shared-registry-boundary",
        ]
    },
    "exact_memberships": {
        "canonical": [
            "cross-runtime-platform-contracts",
            "eebus-api-v1",
            "eebus-architecture",
            "eebus-protocol",
            "platform-cross-runtime-envelope",
            "platform-hash-auth-binding",
            "platform-ownership-validation",
            "platform-promotion-consumer-contract",
            "platform-shared-registry-boundary",
        ]
    },
    "candidate_inventory": [],
}


class PublicationError(ValueError):
    pass


def _yaml_scalar(value: str, line_number: int) -> Any:
    if value == "[]":
        return []
    if value == "{}":
        return {}
    if value in {"null", "Null", "NULL", "~"}:
        return None
    if value in {"true", "True", "TRUE"}:
        return True
    if value in {"false", "False", "FALSE"}:
        return False
    if value.startswith("'"):
        if len(value) < 2 or not value.endswith("'"):
            raise PublicationError(f"registry line {line_number}: invalid quoted scalar")
        return value[1:-1].replace("''", "'")
    if value.startswith('"'):
        try:
            decoded = json.loads(value)
        except json.JSONDecodeError as error:
            raise PublicationError(
                f"registry line {line_number}: invalid quoted scalar"
            ) from error
        if not isinstance(decoded, str):
            raise PublicationError(f"registry line {line_number}: scalar must be text")
        return decoded
    if any(token in value for token in (" #", " &", " *", "!", "<<")):
        raise PublicationError(f"registry line {line_number}: YAML extensions are forbidden")
    return value


def _parse_yaml(raw: bytes) -> Any:
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as error:
        raise PublicationError("publication registry must be UTF-8") from error
    lines: list[tuple[int, str, int]] = []
    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        if "\t" in raw_line:
            raise PublicationError(f"registry line {line_number}: tabs are forbidden")
        content = raw_line.lstrip(" ")
        if not content or content.startswith("#"):
            continue
        indent = len(raw_line) - len(content)
        if indent % 2 or content.startswith(("---", "...")):
            raise PublicationError(f"registry line {line_number}: invalid indentation or marker")
        lines.append((indent, content, line_number))
    if not lines:
        raise PublicationError("publication registry is empty")

    def parse_block(index: int, indent: int) -> tuple[Any, int]:
        if index >= len(lines) or lines[index][0] != indent:
            raise PublicationError("publication registry indentation is invalid")
        sequence = lines[index][1].startswith("- ")
        result: Any = [] if sequence else {}
        while index < len(lines):
            current_indent, content, line_number = lines[index]
            if current_indent < indent:
                break
            if current_indent != indent:
                raise PublicationError(f"registry line {line_number}: unexpected indentation")
            if sequence:
                if not content.startswith("- "):
                    break
                item = content[2:].strip()
                if not item:
                    if index + 1 >= len(lines) or lines[index + 1][0] <= indent:
                        raise PublicationError(f"registry line {line_number}: empty sequence item")
                    value, index = parse_block(index + 1, lines[index + 1][0])
                    result.append(value)
                    continue
                result.append(_yaml_scalar(item, line_number))
                index += 1
                continue
            if content.startswith("- ") or ":" not in content:
                raise PublicationError(f"registry line {line_number}: mapping entry is invalid")
            key, remainder = content.split(":", 1)
            key = key.strip()
            if re.fullmatch(r"[A-Za-z0-9_.-]+", key) is None:
                raise PublicationError(f"registry line {line_number}: mapping key is invalid")
            if key in result:
                raise PublicationError(f"registry line {line_number}: duplicate key {key!r}")
            remainder = remainder.strip()
            if remainder:
                result[key] = _yaml_scalar(remainder, line_number)
                index += 1
                continue
            if index + 1 >= len(lines) or lines[index + 1][0] < indent:
                raise PublicationError(f"registry line {line_number}: mapping value is missing")
            if lines[index + 1][0] == indent and not lines[index + 1][1].startswith("- "):
                raise PublicationError(f"registry line {line_number}: mapping value is missing")
            result[key], index = parse_block(index + 1, lines[index + 1][0])
        return result, index

    document, final_index = parse_block(0, lines[0][0])
    if lines[0][0] != 0 or final_index != len(lines):
        raise PublicationError("publication registry has trailing or indented content")
    return document


def _read_regular(path: Path, limit: int) -> bytes:
    try:
        before = path.lstat()
    except OSError as error:
        raise PublicationError(f"{path}: required regular file is unavailable") from error
    if not stat.S_ISREG(before.st_mode):
        raise PublicationError(f"{path}: required path must be a regular file")
    if before.st_size > limit:
        raise PublicationError(f"{path}: file exceeds size limit")
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags)
    except OSError as error:
        raise PublicationError(f"{path}: regular file cannot be opened safely") from error
    try:
        after = os.fstat(descriptor)
        if not stat.S_ISREG(after.st_mode) or (before.st_dev, before.st_ino) != (
            after.st_dev,
            after.st_ino,
        ):
            raise PublicationError(f"{path}: file changed during validation")
        payload = b""
        while len(payload) <= limit:
            chunk = os.read(descriptor, min(65536, limit + 1 - len(payload)))
            if not chunk:
                break
            payload += chunk
    finally:
        os.close(descriptor)
    if len(payload) > limit:
        raise PublicationError(f"{path}: file exceeds size limit")
    return payload


def _relative_path(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value or "\\" in value:
        raise PublicationError(f"{label}: path is invalid")
    path = PurePosixPath(value)
    if (
        path.is_absolute()
        or value != posixpath.normpath(value)
        or any(part in {"", ".", ".."} for part in path.parts)
        or PATH_PATTERN.fullmatch(value) is None
    ):
        raise PublicationError(f"{label}: path is invalid")
    return value


def _file_under(root: Path, relative: str, limit: int) -> bytes:
    current = root
    parts = PurePosixPath(relative).parts
    for index, part in enumerate(parts):
        current /= part
        try:
            mode = current.lstat().st_mode
        except OSError as error:
            raise PublicationError(f"{relative}: required member is unavailable") from error
        if stat.S_ISLNK(mode):
            raise PublicationError(f"{relative}: symlinks are forbidden")
        if index < len(parts) - 1 and not stat.S_ISDIR(mode):
            raise PublicationError(f"{relative}: parent is not a directory")
    return _read_regular(current, limit)


def _decoded_variants(text: str) -> set[str]:
    variants = {text}
    for _ in range(32):
        expanded = set(variants)
        for value in variants:
            expanded.add(html.unescape(value))
            expanded.add(urllib.parse.unquote(value))
            expanded.add(UNICODE_ESCAPE.sub(lambda item: chr(int(item.group(1), 16)), value))
            expanded.add(HEX_ESCAPE.sub(lambda item: chr(int(item.group(1), 16)), value))
        if len(expanded) > 1024:
            raise PublicationError("encoded publication text exceeds normalization limits")
        if expanded == variants:
            return variants
        variants = expanded
    raise PublicationError("encoded publication text exceeds normalization depth")


def _normalized_url_paths(text: str) -> set[str]:
    normalized = text.replace("\\", "/").casefold()
    fragments = re.split(r"[\s\"'<>()[\]{};,=]+", normalized)
    paths: set[str] = set()
    for fragment in fragments:
        if not fragment:
            continue
        try:
            parsed = urllib.parse.urlsplit(fragment)
        except ValueError:
            raise PublicationError("publication text contains an invalid URL") from None
        raw_path = parsed.path or fragment
        canonical = posixpath.normpath("/" + raw_path.lstrip("/"))
        paths.add(canonical)
    return paths


def _reject_candidate(text: str, label: str) -> None:
    for variant in _decoded_variants(text):
        normalized = variant.replace("\\", "/").casefold()
        if re.search(r"api/+_candidate(?:/|$|[^a-z0-9_])", normalized):
            raise PublicationError(f"{label}: candidate publication reference is forbidden")
        for path in _normalized_url_paths(variant):
            if re.search(r"/api/+_candidate(?:/|$|[^a-z0-9_])", path):
                raise PublicationError(
                    f"{label}: normalized candidate publication reference is forbidden"
                )


def _load_registry(root: Path) -> dict[str, Any]:
    absolute = root.absolute()
    temporary = Path(tempfile.gettempdir()).absolute()
    current = (
        temporary
        if absolute == temporary or temporary in absolute.parents
        else Path(absolute.anchor)
    )
    try:
        for part in absolute.relative_to(current).parts:
            current /= part
            mode = current.lstat().st_mode
            if stat.S_ISLNK(mode) or not stat.S_ISDIR(mode):
                raise PublicationError(
                    "repository root must have no symlinked directory components"
                )
    except OSError as error:
        raise PublicationError("repository root is unavailable") from error
    root_mode = root.lstat().st_mode
    if stat.S_ISLNK(root_mode) or not stat.S_ISDIR(root_mode):
        raise PublicationError("repository root must be a non-symlink directory")
    raw = _file_under(root, REGISTRY_PATH, MAX_CONTROL_BYTES)
    document = _parse_yaml(raw)
    if not isinstance(document, dict) or set(document) != {
        "schema", "version", "platform_contract", "public_output_roots",
        "publisher", "channels",
    }:
        raise PublicationError("publication registry has an open or invalid shape")
    if document["schema"] != "helianthus.publication-channels" or document["version"] != "2":
        raise PublicationError("publication registry schema/version is invalid")
    if document["platform_contract"] != PLATFORM_CONTRACT:
        raise PublicationError("PLATFORM-B completion binding differs")

    roots = document["public_output_roots"]
    if (
        not isinstance(roots, list) or not roots
        or roots != sorted(roots, key=lambda item: item.encode("utf-8"))
        or len(set(roots)) != len(roots)
    ):
        raise PublicationError("public output roots are invalid")
    for value in roots:
        _relative_path(value, "public output root")

    publisher = document["publisher"]
    if not isinstance(publisher, dict) or set(publisher) != {
        "repository", "path", "blob_mode", "oid", "sha256",
    }:
        raise PublicationError("publisher binding is invalid")
    publisher_path = _relative_path(publisher.get("path"), "publisher")
    publisher_file = root / publisher_path
    payload = _file_under(root, publisher_path, MAX_CONTROL_BYTES)
    publisher_mode = publisher_file.lstat().st_mode
    measured_blob_mode = "100755" if publisher_mode & 0o111 else "100644"
    expected_publisher = {
        "repository": REPOSITORY,
        "path": "scripts/render_publication.py",
        "blob_mode": measured_blob_mode,
        "oid": hashlib.sha1(f"blob {len(payload)}\0".encode() + payload).hexdigest(),
        "sha256": hashlib.sha256(payload).hexdigest(),
    }
    if publisher != expected_publisher:
        raise PublicationError("publisher repo/path/mode/OID/SHA-256 binding differs")

    channels = document["channels"]
    if not isinstance(channels, dict) or set(channels) != CHANNELS:
        raise PublicationError("stable channel set is invalid")
    artifacts: set[str] = set()
    for channel, specification in channels.items():
        if not isinstance(specification, dict) or set(specification) != {"artifact", "members"}:
            raise PublicationError(f"{channel}: channel shape is invalid")
        artifact = specification["artifact"]
        _reject_candidate(str(artifact), channel)
        artifact = _relative_path(artifact, f"{channel} artifact")
        if artifact in artifacts or not any(
            artifact == value or artifact.startswith(value + "/") for value in roots
        ):
            raise PublicationError(f"{channel}: artifact path is invalid")
        artifacts.add(artifact)
        members = specification["members"]
        if (
            not isinstance(members, list) or not members
            or any(not isinstance(member, str) for member in members)
            or len(set(members)) != len(members)
            or members != sorted(members, key=lambda item: item.encode("utf-8"))
        ):
            raise PublicationError(f"{channel}: member paths are invalid")
        for member in members:
            _reject_candidate(member, f"{channel} member")
            member = _relative_path(member, f"{channel} member")
            member_raw = _file_under(root, member, MAX_MEMBER_BYTES)
            try:
                member_text = member_raw.decode("utf-8")
            except UnicodeDecodeError as error:
                raise PublicationError(f"{member}: member must be UTF-8") from error
            _reject_candidate(member_text, member)
    return document


def _render_outputs(registry: dict[str, Any]) -> dict[str, bytes]:
    outputs: dict[str, bytes] = {}
    for channel, specification in registry["channels"].items():
        members = specification["members"]
        if channel == "search":
            text = json.dumps({"pages": members}, ensure_ascii=True, separators=(",", ":")) + "\n"
        elif channel == "sitemap":
            entries = "".join(f"<url><loc>{member}</loc></url>" for member in members)
            text = (
                '<?xml version="1.0" encoding="UTF-8"?>\n'
                '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
                f"{entries}</urlset>\n"
            )
        else:
            text = "".join(f"{member}\n" for member in members)
        _reject_candidate(text, specification["artifact"])
        outputs[specification["artifact"]] = text.encode("utf-8")
    return outputs


def _trusted_temporary_root(path: Path) -> Path:
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
        raise PublicationError(f"{path}: output must be under a temporary root")
    return max(matches, key=lambda item: len(item.parts))


def _directory_chain(path: Path, *, create: bool) -> None:
    absolute = path.absolute()
    current = _trusted_temporary_root(absolute)
    if not current.is_dir():
        raise PublicationError(f"{path}: directory path is unsafe")
    for part in absolute.relative_to(current).parts:
        current /= part
        try:
            mode = current.lstat().st_mode
        except FileNotFoundError:
            if not create:
                raise PublicationError(f"{path}: directory path is unavailable") from None
            try:
                current.mkdir()
            except FileExistsError:
                pass
            mode = current.lstat().st_mode
        if stat.S_ISLNK(mode) or not stat.S_ISDIR(mode):
            raise PublicationError(f"{path}: directory path is unsafe")


def _ensure_directory(path: Path) -> None:
    _directory_chain(path, create=True)


def _write_atomic(path: Path, payload: bytes) -> None:
    _ensure_directory(path.parent)
    if path.is_symlink() or path.exists() and not path.is_file():
        raise PublicationError(f"{path}: output path is unsafe")
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


def _replace_output(output: Path, rendered: dict[str, bytes]) -> None:
    _ensure_directory(output.parent)
    if output.is_symlink() or output.exists() and not output.is_dir():
        raise PublicationError("publication output path is unsafe")
    staging = Path(tempfile.mkdtemp(prefix=f".{output.name}.", dir=output.parent))
    try:
        for relative, payload in rendered.items():
            destination = staging / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(payload)
        if output.exists():
            shutil.rmtree(output)
        os.replace(staging, output)
    finally:
        if staging.exists():
            shutil.rmtree(staging)


def _evidence(
    registry: dict[str, Any], rendered: dict[str, bytes], commit: str, *, synthetic: bool
) -> bytes:
    artifacts = [
        {
            "channel": channel,
            "path": specification["artifact"],
            "member_paths": specification["members"],
            "sha256": hashlib.sha256(rendered[specification["artifact"]]).hexdigest(),
        }
        for channel, specification in sorted(
            registry["channels"].items(), key=lambda item: item[0].encode("utf-8")
        )
    ]
    document = {
        "schema": "helianthus.docs-publication-evidence",
        "version": 1,
        "milestone": MILESTONE,
        "state": "PUBLISH",
        "source": {
            "repository": REPOSITORY,
            "commit": commit,
            "verification": "synthetic_fixture" if synthetic else "git_object",
        },
        "publisher": registry["publisher"],
        "platform_contract": registry["platform_contract"],
        "artifacts": artifacts,
    }
    core = json.dumps(document, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode()
    document["completion_digest"] = "sha256:" + hashlib.sha256(core).hexdigest()
    return (
        json.dumps(document, ensure_ascii=True, sort_keys=True, separators=(",", ":")) + "\n"
    ).encode()


def _actual_outputs(output: Path) -> dict[str, bytes]:
    _directory_chain(output, create=False)
    if output.is_symlink() or not output.is_dir():
        raise PublicationError("publication output must be a non-symlink directory")
    actual: dict[str, bytes] = {}
    pending = [output]
    while pending:
        directory = pending.pop()
        with os.scandir(directory) as entries:
            for entry in entries:
                mode = entry.stat(follow_symlinks=False).st_mode
                relative = Path(entry.path).relative_to(output).as_posix()
                if stat.S_ISLNK(mode):
                    raise PublicationError(f"{relative}: output symlinks are forbidden")
                if stat.S_ISDIR(mode):
                    pending.append(Path(entry.path))
                elif stat.S_ISREG(mode):
                    payload = _read_regular(Path(entry.path), MAX_MEMBER_BYTES)
                    try:
                        text = payload.decode("utf-8")
                    except UnicodeDecodeError as error:
                        raise PublicationError(f"{relative}: generated output must be UTF-8") from error
                    _reject_candidate(text, relative)
                    actual[relative] = payload
                else:
                    raise PublicationError(f"{relative}: unsupported output file type")
    return actual


def _verify_git_source(root: Path, commit: str) -> None:
    commands = (
        ("cat-file", "-e", f"{commit}^{{commit}}"),
        ("rev-parse", "HEAD"),
        ("status", "--porcelain=v1", "--untracked-files=all"),
    )
    results = [
        subprocess.run(
            ["git", "-C", str(root), *command],
            check=False,
            capture_output=True,
            text=True,
        )
        for command in commands
    ]
    if (
        any(result.returncode != 0 for result in results)
        or results[1].stdout.strip() != commit
        or results[2].stdout.strip()
    ):
        raise PublicationError("source commit is not the clean repository HEAD")


def main() -> int:
    parser = argparse.ArgumentParser(description="Render or verify the frozen publication closure")
    subparsers = parser.add_subparsers(dest="command", required=True)
    for command in ("render", "verify"):
        subparser = subparsers.add_parser(command)
        subparser.add_argument("--repo", type=Path, required=True)
        subparser.add_argument("--output", type=Path, required=True)
        subparser.add_argument("--source-commit", required=True)
        subparser.add_argument("--synthetic-source", action="store_true")
        if command == "render":
            subparser.add_argument("--evidence-core", type=Path, required=True)
    args = parser.parse_args()
    try:
        if COMMIT_PATTERN.fullmatch(args.source_commit) is None:
            raise PublicationError("source commit must be a lowercase full object id")
        repo = args.repo.absolute()
        output = args.output.absolute()
        if output == repo or repo in output.parents or output in repo.parents:
            raise PublicationError("publication output must be outside the repository")
        registry = _load_registry(repo)
        if not args.synthetic_source:
            _verify_git_source(repo, args.source_commit)
        rendered = _render_outputs(registry)
        if args.command == "render":
            evidence = args.evidence_core.absolute()
            if (
                evidence == output
                or output in evidence.parents
                or evidence == repo
                or repo in evidence.parents
                or evidence in repo.parents
            ):
                raise PublicationError(
                    "evidence core must be outside the repository and publication tree"
                )
            evidence_payload = _evidence(
                registry,
                rendered,
                args.source_commit,
                synthetic=args.synthetic_source,
            )
            _replace_output(output, rendered)
            _write_atomic(evidence, evidence_payload)
        else:
            actual = _actual_outputs(output)
            if set(actual) != set(rendered):
                raise PublicationError("generated output inventory differs from the registry")
            for relative, expected in rendered.items():
                if actual[relative] != expected:
                    raise PublicationError(f"{relative}: generated bytes differ")
    except (OSError, PublicationError) as error:
        print(f"publication failed: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
