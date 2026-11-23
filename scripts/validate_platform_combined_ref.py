#!/usr/bin/env python3
"""Canonical entry point for exact cross-repository platform validation."""

from __future__ import annotations

import argparse
import pathlib

import validate_platform_contracts as contracts


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser()
    result.add_argument("--docs-root", type=pathlib.Path, required=True)
    result.add_argument("--docs-eebus-root", type=pathlib.Path, required=True)
    result.add_argument("--eebusreg-root", type=pathlib.Path, required=True)
    result.add_argument("--docs-ref", required=True)
    result.add_argument("--docs-eebus-ref", required=True)
    result.add_argument("--eebusreg-ref", required=True)
    result.add_argument("--prior-manifest", type=pathlib.Path, required=True)
    result.add_argument("--m625-docs-eebus-root", type=pathlib.Path, required=True)
    result.add_argument(
        "--m625-execution-plans-root", type=pathlib.Path, required=True
    )
    result.add_argument("--enforce-through", choices=contracts.MILESTONES, required=True)
    result.add_argument(
        "--docs-repository",
        default="Project-Helianthus/helianthus-docs",
    )
    result.add_argument("--owner-manifest-root", type=pathlib.Path)
    result.add_argument(
        "--toolchain-mode",
        choices=tuple(sorted(contracts.TOOLCHAIN_MODES)),
        default="exact",
    )
    return result


def main() -> int:
    args = parser().parse_args()
    diagnostics = contracts.validate_workspace(
        docs_root=args.docs_root,
        docs_eebus_root=args.docs_eebus_root,
        eebusreg_root=args.eebusreg_root,
        mode="combined-ref",
        docs_ref=args.docs_ref,
        docs_eebus_ref=args.docs_eebus_ref,
        eebusreg_ref=args.eebusreg_ref,
        docs_repository=args.docs_repository,
        enforce_through=args.enforce_through,
        toolchain_mode=args.toolchain_mode,
        prior_manifest=args.prior_manifest,
        m625_docs_eebus_root=args.m625_docs_eebus_root,
        m625_execution_plans_root=args.m625_execution_plans_root,
        owner_manifest_root=args.owner_manifest_root,
    )
    for diagnostic in diagnostics:
        print(diagnostic)
    return 1 if diagnostics else 0


if __name__ == "__main__":
    raise SystemExit(main())
