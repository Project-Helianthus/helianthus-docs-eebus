#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

echo "==> reject repository symlinks"
python3 - <<'PY'
import os
import stat
import sys
from pathlib import Path

pending = [Path(".")]
failed = False
while pending:
    directory = pending.pop()
    try:
        with os.scandir(directory) as entries:
            children = sorted(entries, key=lambda entry: os.fsencode(entry.name))
    except OSError:
        print(f"{directory}: repository directory is unreadable", file=sys.stderr)
        failed = True
        continue
    for entry in children:
        path = Path(entry.path)
        relative = path.as_posix().removeprefix("./")
        if relative == ".git" or relative.startswith(".git/"):
            continue
        try:
            mode = entry.stat(follow_symlinks=False).st_mode
        except OSError:
            print(f"{relative}: repository artifact is unreadable", file=sys.stderr)
            failed = True
            continue
        if stat.S_ISLNK(mode):
            print(f"{relative}: symlinks are forbidden", file=sys.stderr)
            failed = True
        elif stat.S_ISDIR(mode):
            pending.append(path)
if failed:
    sys.exit(1)
PY

echo "==> validate repository ownership policy"
python3 -c 'import importlib.metadata as m; import yaml; assert yaml.__version__ == "6.0.3", yaml.__version__; assert m.version("markdown-it-py") == "4.0.0"; assert m.version("mdurl") == "0.1.2"'
python3 scripts/validate_repository_policy.py

echo "==> verify markdown files are present"
find . -type f \( -iname '*.md' -o -iname '*.markdown' -o -iname '*.mdown' -o -iname '*.mkd' -o -iname '*.mkdn' \) -print -quit | grep -q .

echo "==> check markdown for tabs and trailing spaces"
python3 - <<'PY'
from pathlib import Path
import sys

MAX_MARKDOWN_BYTES = 2 * 1024 * 1024
markdown_suffixes = {".md", ".markdown", ".mdown", ".mkd", ".mkdn"}
failed = False
for path in sorted(Path(".").rglob("*")):
    if not path.is_file() or path.suffix.lower() not in markdown_suffixes:
        continue
    try:
        size = path.stat().st_size
    except OSError:
        print(f"{path}: repository artifact is unreadable", file=sys.stderr)
        failed = True
        continue
    if size > MAX_MARKDOWN_BYTES:
        print(f"{path}: repository artifact exceeds scan size limit", file=sys.stderr)
        failed = True
if failed:
    sys.exit(1)
PY
failed=0
if grep -RIn $'\t' --include='*.[mM][dD]' --include='*.[mM][aA][rR][kK][dD][oO][wW][nN]' --include='*.[mM][dD][oO][wW][nN]' --include='*.[mM][kK][dD]' --include='*.[mM][kK][dD][nN]' .; then
  echo "Tab characters are not allowed in markdown files." >&2
  failed=1
fi
if grep -RInE ' +$' --include='*.[mM][dD]' --include='*.[mM][aA][rR][kK][dD][oO][wW][nN]' --include='*.[mM][dD][oO][wW][nN]' --include='*.[mM][kK][dD]' --include='*.[mM][kK][dD][nN]' .; then
  echo "Trailing spaces are not allowed in markdown files." >&2
  failed=1
fi
if [ "$failed" -ne 0 ]; then
  exit 1
fi

echo "==> check for private IPv4 addresses"
python3 - <<'PY'
from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path("scripts").resolve()))

from machine_publication_policy import IPV4_CANDIDATE_PATTERN, classify_ipv4

failed = False
MAX_MARKDOWN_BYTES = 2 * 1024 * 1024
markdown_suffixes = {".md", ".markdown", ".mdown", ".mkd", ".mkdn"}
for path in pathlib.Path(".").rglob("*"):
    if not path.is_file() or path.suffix.lower() not in markdown_suffixes:
        continue
    try:
        size = path.stat().st_size
    except OSError:
        print(f"{path}: repository artifact is unreadable", file=sys.stderr)
        failed = True
        continue
    if size > MAX_MARKDOWN_BYTES:
        print(f"{path}: repository artifact exceeds scan size limit", file=sys.stderr)
        failed = True
        continue
    text = path.read_text(encoding="utf-8")
    for match in IPV4_CANDIDATE_PATTERN.finditer(text):
        if classify_ipv4(match.group(0)) == "private network":
            line = text.count("\n", 0, match.start()) + 1
            print(f"{path}:{line}: private IPv4 address found", file=sys.stderr)
            failed = True
if failed:
    sys.exit(1)
PY

echo "==> validate API surface v1 contract"
python3 scripts/validate_api_surface_v1.py

echo "==> validate MSP-055 frozen API publication"
if [ -z "${MSP055_SOURCE_CHECKOUT:-}" ]; then
  echo "MSP055_SOURCE_CHECKOUT must name the exact detached source checkout." >&2
  exit 1
fi
python3 scripts/validate_msp_055_api_freeze.py --source-checkout "$MSP055_SOURCE_CHECKOUT"

echo "==> run policy validator tests"
python3 -m unittest discover -s tests -p 'test_*.py'

echo "==> docs-eebus local CI passed"
