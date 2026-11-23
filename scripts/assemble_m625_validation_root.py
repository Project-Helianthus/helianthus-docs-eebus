#!/usr/bin/env python3
"""Assemble the M6.25 registry root from pinned public schema owners.

The registry JSON and the protocol-neutral schemas come from the pinned
helianthus-docs checkout. The three eBUS source schemas come from the pinned
helianthus-docs-ebus donor. The vendored M6.25 schema comes from this
candidate. Every copied file is compared with its owner and the assembly
stops when any byte differs.
"""

from __future__ import annotations

import os
import pathlib
import sys


REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
EBUS_SCHEMA_NAMES = (
    "synchronized-evidence-source-ebus-b509-v1.schema.json",
    "synchronized-evidence-source-ebus-b524-v1.schema.json",
    "synchronized-evidence-source-ebus-b555-v1.schema.json",
)
VENDOR_SCHEMA = pathlib.Path(
    "vendor/helianthus.eebus.m625.public-redacted-evidence.v1.schema.json"
)


def _checkout(env_name: str, relative: str) -> pathlib.Path:
    override = os.environ.get(env_name)
    if override:
        return pathlib.Path(override)
    return REPO_ROOT / ".tmp" / relative


def platform_root() -> pathlib.Path:
    return _checkout("PLATFORM_CONTRACTS_ROOT", "platform-contracts")


def donor_root() -> pathlib.Path:
    return _checkout("DONOR_DOCS_ROOT", "docs-ebus")


def validation_root() -> pathlib.Path:
    return _checkout("M625_VALIDATION_ROOT", "m625-validation-root")


def _read_regular(path: pathlib.Path, owner: str) -> bytes:
    if path.is_symlink() or not path.is_file():
        raise RuntimeError(f"{owner}: schema is not a regular file: {path}")
    return path.read_bytes()


def _write_verified(source: pathlib.Path, dest: pathlib.Path, owner: str) -> None:
    payload = _read_regular(source, owner)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(payload)
    copied = _read_regular(dest, owner)
    if copied != payload:
        raise RuntimeError(f"{owner}: copied schema bytes differ: {dest}")


def assemble(destination: pathlib.Path | None = None) -> pathlib.Path:
    """Copy the registry schema tree and return the assembled validation root."""
    platform = platform_root()
    donor = donor_root()
    root = pathlib.Path(destination) if destination is not None else validation_root()
    source_schemas = platform / "docs/platform/schemas"
    if not source_schemas.is_dir() or source_schemas.is_symlink():
        raise RuntimeError(
            "helianthus-docs: pinned platform schema directory is missing: "
            f"{source_schemas}"
        )
    destination_schemas = root / "docs/platform/schemas"
    destination_schemas.mkdir(parents=True, exist_ok=True)
    for source in sorted(source_schemas.rglob("*")):
        relative = source.relative_to(source_schemas)
        dest = destination_schemas / relative
        if source.is_symlink():
            raise RuntimeError(f"helianthus-docs: refusing symlink {relative}")
        if source.is_dir():
            dest.mkdir(parents=True, exist_ok=True)
            continue
        if not source.is_file():
            raise RuntimeError(f"helianthus-docs: unsupported schema entry {relative}")
        _write_verified(source, dest, "helianthus-docs")

    donor_schemas = donor / "docs/platform/schemas"
    for name in EBUS_SCHEMA_NAMES:
        _write_verified(
            donor_schemas / name,
            destination_schemas / name,
            "helianthus-docs-ebus",
        )
    _write_verified(
        REPO_ROOT / "docs/platform/schemas" / VENDOR_SCHEMA,
        destination_schemas / VENDOR_SCHEMA,
        "helianthus-docs-eebus",
    )
    return root


def main() -> int:
    print(assemble())
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuntimeError as error:
        print(error, file=sys.stderr)
        raise SystemExit(1) from None
