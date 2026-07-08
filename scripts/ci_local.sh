#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

echo "==> verify markdown files are present"
find . -name '*.md' -print | grep -q .

echo "==> check markdown for tabs and trailing spaces"
failed=0
if grep -RIn $'\t' --include='*.md' .; then
  echo "Tab characters are not allowed in markdown files." >&2
  failed=1
fi
if grep -RInE ' +$' --include='*.md' .; then
  echo "Trailing spaces are not allowed in markdown files." >&2
  failed=1
fi
if [ "$failed" -ne 0 ]; then
  exit 1
fi

echo "==> check for private IPv4 addresses"
python3 - <<'PY'
from __future__ import annotations

import ipaddress
import pathlib
import re
import sys

private_nets = [
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("100.64.0.0/10"),
    ipaddress.ip_network("169.254.0.0/16"),
]

failed = False
pattern = re.compile(r"\b(?:(?:\d{1,3})\.){3}(?:\d{1,3})\b")
for path in pathlib.Path(".").rglob("*.md"):
    text = path.read_text(encoding="utf-8")
    for match in pattern.finditer(text):
        try:
            addr = ipaddress.ip_address(match.group(0))
        except ValueError:
            continue
        if any(addr in net for net in private_nets):
            line = text.count("\n", 0, match.start()) + 1
            print(f"{path}:{line}: private IPv4 address found", file=sys.stderr)
            failed = True
if failed:
    sys.exit(1)
PY

echo "==> docs-eebus local CI passed"
