#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${repo_root}"

pin_checkout() {
  local url="$1"
  local dest="$2"
  local rev="$3"
  if [[ -d "${dest}/.git" ]]; then
    local head
    head="$(git -C "${dest}" rev-parse HEAD)"
    if [[ "${head}" == "${rev}" ]]; then
      return 0
    fi
  fi
  rm -rf "${dest}"
  mkdir -p "${dest}"
  git -C "${dest}" init --quiet
  git -C "${dest}" remote add origin "${url}"
  git -C "${dest}" fetch --depth 1 --quiet origin "${rev}"
  git -C "${dest}" checkout --detach --quiet FETCH_HEAD
}

platform_rev="ff8fccc7""d5fbcbfe1e156fce302549d04a2f6228"
donor_rev="977614c9""44cd685bef75b5b12148e1110ed7653a"
trusted_rev="8215201a""4274db5310ee672619ba2f1d27b99bec"
provenance_rev="cedf238e""34f879815ba773e9cd76b2b31c2822a3"
plans_rev="fb384ab5""7d79f0020c54d2c66416e8a7666f0ceb"

export PLATFORM_CONTRACTS_ROOT="${repo_root}/.tmp/platform-contracts"
export DONOR_DOCS_ROOT="${repo_root}/.tmp/docs-ebus"
export M625_TRUSTED_BASE_ROOT="${repo_root}/.tmp/m625-trusted-base"
export PLATFORM_M625_DOCS_EEBUS_ROOT="${repo_root}/.tmp/m625-docs-eebus"
export PLATFORM_M625_EXECUTION_PLANS_ROOT="${repo_root}/.tmp/m625-execution-plans"

pin_checkout \
  "https://github.com/Project-Helianthus/helianthus-docs.git" \
  "${PLATFORM_CONTRACTS_ROOT}" \
  "${platform_rev}"
pin_checkout \
  "https://github.com/Project-Helianthus/helianthus-docs-ebus.git" \
  "${DONOR_DOCS_ROOT}" \
  "${donor_rev}"
pin_checkout \
  "https://github.com/Project-Helianthus/helianthus-docs-ebus.git" \
  "${M625_TRUSTED_BASE_ROOT}" \
  "${trusted_rev}"
pin_checkout \
  "https://github.com/Project-Helianthus/helianthus-docs-eebus.git" \
  "${PLATFORM_M625_DOCS_EEBUS_ROOT}" \
  "${provenance_rev}"
pin_checkout \
  "https://github.com/Project-Helianthus/helianthus-execution-plans.git" \
  "${PLATFORM_M625_EXECUTION_PLANS_ROOT}" \
  "${plans_rev}"

python3 scripts/assemble_m625_validation_root.py

python3 -m pytest -q tests/test_m625_cross_seed_contract.py
python3 -m pytest -q tests/test_platform_contracts.py -k trusted_prior_workflow
python3 -m pytest -q tests/test_platform_contracts.py -k 'not trusted_prior_workflow'
python3 -m pytest -q tests/test_synchronized_evidence_m625_contract.py
python3 -m pytest -q tests/test_eebus_operator_admin_contract.py
python3 -m pytest -q tests/test_docs_ci_run_cost_gates.py

echo "==> check cross-runtime platform contracts (MSP-DOCS-CLEAN)"
if [[ -n "${PLATFORM_PRIOR_MANIFEST:-}" ]]; then
  prior_manifest="${PLATFORM_PRIOR_MANIFEST}"
else
  prior_manifest="${repo_root}/.tmp/m625-donor-prior-manifest.yaml"
  git -C "${DONOR_DOCS_ROOT}" cat-file blob \
    "HEAD:docs/platform/manifests/eebus-doc-ownership.yaml" > "${prior_manifest}"
fi
python3 scripts/validate_platform_contracts.py \
  --mode repository \
  --docs-root "${PLATFORM_CONTRACTS_ROOT}" \
  --docs-repository "Project-Helianthus/helianthus-docs" \
  --owner-manifest-root . \
  --m625-docs-eebus-root "${PLATFORM_M625_DOCS_EEBUS_ROOT}" \
  --m625-execution-plans-root "${PLATFORM_M625_EXECUTION_PLANS_ROOT}" \
  --prior-manifest "${prior_manifest}" \
  --enforce-through MSP-DOCS-CLEAN \
  --toolchain-mode supported

if [[ -n "${PLATFORM_DOCS_EEBUS_ROOT:-}${PLATFORM_EEBUSREG_ROOT:-}${PLATFORM_DOCS_REF:-}${PLATFORM_DOCS_EEBUS_REF:-}${PLATFORM_EEBUSREG_REF:-}" ]]; then
  test -n "${PLATFORM_DOCS_EEBUS_ROOT}"
  test -n "${PLATFORM_EEBUSREG_ROOT}"
  test -n "${PLATFORM_DOCS_REF}"
  test -n "${PLATFORM_DOCS_EEBUS_REF}"
  test -n "${PLATFORM_EEBUSREG_REF}"
  python3 scripts/validate_platform_combined_ref.py \
    --docs-root "${PLATFORM_CONTRACTS_ROOT}" \
    --docs-eebus-root . \
    --eebusreg-root "${PLATFORM_EEBUSREG_ROOT}" \
    --docs-ref "${PLATFORM_DOCS_REF}" \
    --docs-eebus-ref "${PLATFORM_DOCS_EEBUS_REF}" \
    --eebusreg-ref "${PLATFORM_EEBUSREG_REF}" \
    --prior-manifest "${prior_manifest}" \
    --m625-docs-eebus-root "${PLATFORM_M625_DOCS_EEBUS_ROOT}" \
    --m625-execution-plans-root "${PLATFORM_M625_EXECUTION_PLANS_ROOT}" \
    --owner-manifest-root . \
    --enforce-through MSP-DOCS-CLEAN \
    --toolchain-mode supported
else
  echo "Combined Ref acceptance not run: platform combined-ref inputs are unset."
fi

if [[ "${CI_PLATFORM_ONLY:-}" == "1" ]]; then
  echo "==> copied platform contracts passed; docs fast checks run in their own job"
  exit 0
fi

# The focused local gate has the same 60-second ceiling on macOS and Linux.
exec python3 -c '
import subprocess
import sys

try:
    completed = subprocess.run(["bash", "-c", "python3 -m unittest tests.test_naming_contract && bash scripts/ci_docs_fast.sh"], timeout=60)
except subprocess.TimeoutExpired:
    print("focused local CI exceeded its 60-second budget", file=sys.stderr)
    raise SystemExit(124)
raise SystemExit(completed.returncode)
'
