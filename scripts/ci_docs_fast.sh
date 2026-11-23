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
    with os.scandir(directory) as entries:
        for entry in sorted(entries, key=lambda item: os.fsencode(item.name)):
            path = Path(entry.path)
            relative = path.as_posix().removeprefix("./")
            if relative == ".git" or relative.startswith(".git/"):
                continue
            if relative == ".tmp" or relative.startswith(".tmp/"):
                continue
            mode = entry.stat(follow_symlinks=False).st_mode
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

echo "==> verify markdown formatting"
find . -path './.tmp' -prune -o -type f \( -iname '*.md' -o -iname '*.markdown' -o -iname '*.mdown' -o -iname '*.mkd' -o -iname '*.mkdn' \) -print -quit | grep -q .
if grep -RIn --exclude-dir=.tmp $'\t' --include='*.[mM][dD]' --include='*.[mM][aA][rR][kK][dD][oO][wW][nN]' --include='*.[mM][dD][oO][wW][nN]' --include='*.[mM][kK][dD]' --include='*.[mM][kK][dD][nN]' .; then
  echo "Tab characters are not allowed in markdown files." >&2
  exit 1
fi
if grep -RInE --exclude-dir=.tmp ' +$' --include='*.[mM][dD]' --include='*.[mM][aA][rR][kK][dD][oO][wW][nN]' --include='*.[mM][dD][oO][wW][nN]' --include='*.[mM][kK][dD]' --include='*.[mM][kK][dD][nN]' .; then
  echo "Trailing spaces are not allowed in markdown files." >&2
  exit 1
fi

echo "==> reject private IPv4 addresses"
python3 - <<'PY'
from pathlib import Path
import sys

sys.path.insert(0, str(Path("scripts").resolve()))
from machine_publication_policy import IPV4_CANDIDATE_PATTERN, classify_ipv4

suffixes = {".md", ".markdown", ".mdown", ".mkd", ".mkdn"}
failed = False
for path in sorted(Path(".").rglob("*")):
    if not path.is_file() or path.suffix.lower() not in suffixes:
        continue
    if ".tmp" in path.parts:
        continue
    text = path.read_text(encoding="utf-8")
    for match in IPV4_CANDIDATE_PATTERN.finditer(text):
        if classify_ipv4(match.group(0)) == "private network":
            line = text.count("\n", 0, match.start()) + 1
            print(f"{path}:{line}: private IPv4 address found", file=sys.stderr)
            failed = True
if failed:
    raise SystemExit(1)
PY

echo "==> python readability ratchet"
python3 scripts/check_readability.py --self-test
python3 scripts/check_readability.py --check

echo "==> validate API surface v1 contract"
python3 scripts/validate_api_surface_v1.py

echo "==> validate MSP-055 frozen API publication"
if [ -z "${MSP055_SOURCE_CHECKOUT:-}" ]; then
  echo "MSP055_SOURCE_CHECKOUT must name the exact detached source checkout." >&2
  exit 1
fi
python3 scripts/validate_msp_055_api_freeze.py --source-checkout "$MSP055_SOURCE_CHECKOUT"

echo "==> run direct workflow and frozen-publication contracts"
# Run the two longest independent modules beside the remaining direct contracts.
# All four groups must pass; their output is kept separate so failures stay readable.
# mktemp creates only the final component, and a fresh checkout has no .tmp yet.
mkdir -p .tmp
contract_output_dir="$(mktemp -d .tmp/docs-fast-contracts.XXXXXXXX)"
cleanup_contract_output() { rm -rf -- "$contract_output_dir"; }
trap cleanup_contract_output EXIT
contract_modules=(
  tests.test_issue_118_ci_split_contract
  tests.test_msp_055_api_freeze.MSP055APIFreezeStaticContractTests
  tests.test_issue_102_m8_coexistence_cross_seed
  tests.test_issue_104_ha_addon_runtime_wiring
  tests.test_issue_106_outdoor_temperature_promotion_evidence
  tests.test_issue_108_vr940_multi_leaf_source_inventory
  tests.test_issue_112_operator_pairing_browsers_contract
  tests.test_issue_114_operator_admin_v1_boundary
  tests.test_issue_116_spine_entity_usecase_contract
  tests.test_issue_122_retry_ready_recovery_contract
  tests.test_issue_124_known_unapplied_reopen_contract
  tests.test_issue_130_post_m9_closure_contract
  tests.test_issue_132_transient_pin_contract
  tests.test_issue_134_driver_manager_coexistence
  tests.test_issue_148_portal_participation_contract
  tests.test_issue_48_ship_identity_contract
  tests.test_issue_50_strict_inbound_current_schema_contract
  tests.test_issue_64_ship_endpoint_order_contract
  tests.test_issue_66_successful_attempt_trust_projection_contract
  tests.test_issue_68_raw_operator_redaction_contract
  tests.test_issue_76_m625_raw_feature_contract
  tests.test_issue_96_spine13_hvac_model_erratum_contract
  tests.test_issue_98_m65_live_redacted_source_contract
  tests.test_msp_036_raw_view_contract
  tests.test_msp_045_trust_admin_projection_contract
  tests.test_msp_04b_first_trust_contract
  tests.test_msp_04c_restore_quarantine_contract
  tests.test_msp_055_api_candidate
  tests.test_msp_05a_gateway_config_contract
  tests.test_msp_05p_production_activation_contract
  tests.test_msp_06_mcp_wire_contract
  tests.test_msp_docs_e2r_publish_red
)
spine_model_modules=(
  tests.test_issue_96_spine13_hvac_model_erratum_contract
)
raw_operator_tests=()
while IFS= read -r test_id; do
  raw_operator_tests+=("$test_id")
done < <(python3 - <<'PY'
import unittest

suite = unittest.defaultTestLoader.loadTestsFromName(
    "tests.test_issue_68_raw_operator_redaction_contract"
)

def test_ids(items):
    for item in items:
        if isinstance(item, unittest.TestSuite):
            yield from test_ids(item)
        else:
            yield item.id()

print("\n".join(test_ids(suite)))
PY
)
if (( ${#raw_operator_tests[@]} < 2 )); then
  echo 'The raw-operator contract suite could not be discovered.' >&2
  exit 1
fi
raw_operator_split=$(( (${#raw_operator_tests[@]} + 1) / 2 ))
raw_operator_first=("${raw_operator_tests[@]:0:raw_operator_split}")
raw_operator_second=("${raw_operator_tests[@]:raw_operator_split}")
remaining_modules=()
for module in "${contract_modules[@]}"; do
  case "$module" in
    tests.test_issue_68_raw_operator_redaction_contract|tests.test_issue_96_spine13_hvac_model_erratum_contract) ;;
    *) remaining_modules+=("$module") ;;
  esac
done
python3 -m unittest "${raw_operator_first[@]}" >"$contract_output_dir/raw-operator-first.log" 2>&1 &
raw_operator_first_pid=$!
python3 -m unittest "${raw_operator_second[@]}" >"$contract_output_dir/raw-operator-second.log" 2>&1 &
raw_operator_second_pid=$!
python3 -m unittest "${spine_model_modules[@]}" >"$contract_output_dir/spine-model.log" 2>&1 &
spine_model_pid=$!
python3 -m unittest "${remaining_modules[@]}" >"$contract_output_dir/remaining.log" 2>&1 &
remaining_pid=$!
raw_operator_first_status=0
raw_operator_second_status=0
spine_model_status=0
remaining_status=0
wait "$raw_operator_first_pid" || raw_operator_first_status=$?
wait "$raw_operator_second_pid" || raw_operator_second_status=$?
wait "$spine_model_pid" || spine_model_status=$?
wait "$remaining_pid" || remaining_status=$?
cat "$contract_output_dir/raw-operator-first.log" "$contract_output_dir/raw-operator-second.log" "$contract_output_dir/spine-model.log" "$contract_output_dir/remaining.log"
if (( raw_operator_first_status != 0 || raw_operator_second_status != 0 || spine_model_status != 0 || remaining_status != 0 )); then
  exit 1
fi

echo "==> docs-eebus fast CI passed"
