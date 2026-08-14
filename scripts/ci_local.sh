#!/usr/bin/env bash
set -euo pipefail

# The focused local gate has the same 60-second ceiling on macOS and Linux.
exec python3 -c '
import subprocess
import sys

try:
    completed = subprocess.run(["bash", "scripts/ci_docs_fast.sh"], timeout=60)
except subprocess.TimeoutExpired:
    print("focused local CI exceeded its 60-second budget", file=sys.stderr)
    raise SystemExit(124)
raise SystemExit(completed.returncode)
'
