#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

echo "==> verify markdown files are present"
find . -type f \( -iname '*.md' -o -iname '*.markdown' -o -iname '*.mdown' -o -iname '*.mkd' -o -iname '*.mkdn' \) -print -quit | grep -q .

echo "==> check markdown for tabs and trailing spaces"
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
markdown_suffixes = {".md", ".markdown", ".mdown", ".mkd", ".mkdn"}
for path in pathlib.Path(".").rglob("*"):
    if not path.is_file() or path.suffix.lower() not in markdown_suffixes:
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

echo "==> validate repository ownership policy"
python3 -c 'import yaml; assert yaml.__version__ == "6.0.3", yaml.__version__'
python3 scripts/validate_repository_policy.py

echo "==> validate API surface v1 contract"
python3 scripts/validate_api_surface_v1.py

echo "==> run policy validator tests"
python3 -m unittest discover -s tests -p 'test_*.py'

echo "==> docs-eebus local CI passed"
