#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

echo "==> run bounded validator and publication-policy self-tests"
python3 -m unittest \
  tests.test_issue_118_ci_split_contract \
  tests.test_policy_validator \
  tests.test_machine_publication_policy \
  tests.test_api_surface_v1 \
  tests.test_msp_docs_e2_red \
  tests.test_msp_docs_e2_remediation \
  tests.test_msp_055_api_freeze
