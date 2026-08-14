from __future__ import annotations

import stat
import unittest
from pathlib import Path
from typing import Any

import yaml


REPO = Path(__file__).resolve().parents[1]
WORKFLOWS = REPO / ".github" / "workflows"
DOCS_FAST = REPO / "scripts" / "ci_docs_fast.sh"
VALIDATOR_SELFTEST = REPO / "scripts" / "ci_validator_selftest.sh"
LOCAL_CI = REPO / "scripts" / "ci_local.sh"


def load_workflow(path: Path) -> dict[str, Any]:
    document = yaml.load(path.read_text(encoding="utf-8"), Loader=yaml.BaseLoader)
    if not isinstance(document, dict):
        raise AssertionError(f"workflow must be a mapping: {path.relative_to(REPO)}")
    return document


def workflow_pr_sources() -> list[Path]:
    sources: list[Path] = []
    workflow_paths = set(WORKFLOWS.glob("*.yml")) | set(WORKFLOWS.glob("*.yaml"))
    for path in sorted(workflow_paths):
        triggers = load_workflow(path).get("on", {})
        if (
            triggers == "pull_request"
            or isinstance(triggers, list) and "pull_request" in triggers
            or isinstance(triggers, dict) and "pull_request" in triggers
        ):
            sources.append(path)
    return sources


def require_executable(test: unittest.TestCase, path: Path) -> str:
    test.assertTrue(path.is_file(), f"missing CI script: {path.relative_to(REPO)}")
    test.assertTrue(
        path.stat().st_mode & stat.S_IXUSR,
        f"CI script must be executable: {path.relative_to(REPO)}",
    )
    return path.read_text(encoding="utf-8")


class Issue118CISplitContractTests(unittest.TestCase):
    def test_workflow_has_one_cancelable_pr_source_and_main_only_push(self) -> None:
        pr_sources = workflow_pr_sources()
        self.assertEqual(
            pr_sources,
            [WORKFLOWS / "docs-ci.yml"],
            "Docs CI must be the only workflow triggered by pull requests",
        )

        workflow = load_workflow(WORKFLOWS / "docs-ci.yml")
        triggers = workflow["on"]
        self.assertIn("pull_request", triggers)
        self.assertEqual(
            triggers.get("push", {}).get("branches"),
            ["main"],
            "push CI is reserved for main; PR validation has one source",
        )

        concurrency = workflow.get("concurrency")
        self.assertIsInstance(concurrency, dict)
        group = concurrency.get("group", "")
        self.assertIn("github.workflow", group)
        self.assertTrue(
            "github.event.pull_request.number" in group
            or "github.head_ref" in group,
            "concurrency key must distinguish a pull request from other refs",
        )
        self.assertIn("github.ref", group)
        self.assertEqual(concurrency.get("cancel-in-progress"), "true")

    def test_docs_fast_is_unconditional_and_keeps_current_publication_checks(self) -> None:
        workflow = load_workflow(WORKFLOWS / "docs-ci.yml")
        jobs = workflow.get("jobs", {})
        docs_fast = jobs.get("docs-fast", {})
        self.assertEqual(
            docs_fast.get("timeout-minutes"),
            "5",
            "docs-fast must be bounded to five minutes",
        )
        self.assertNotIn("if", docs_fast, "docs-fast must run for every pull request")

        docs_fast_text = require_executable(self, DOCS_FAST)
        self.assertEqual(
            docs_fast_text.count("scripts/validate_repository_policy.py"),
            1,
            "docs-fast must invoke the current policy validator exactly once",
        )
        self.assertIn("scripts/validate_api_surface_v1.py", docs_fast_text)
        self.assertIn("scripts/validate_msp_055_api_freeze.py", docs_fast_text)
        self.assertIn("test_issue_118_ci_split_contract", docs_fast_text)
        self.assertIn("MSP055APIFreezeStaticContractTests", docs_fast_text)
        for direct_contract in (
            "test_issue_112_operator_pairing_browsers_contract",
            "test_issue_114_operator_admin_v1_boundary",
            "test_issue_116_spine_entity_usecase_contract",
            "test_msp_036_raw_view_contract",
            "test_msp_06_mcp_wire_contract",
        ):
            self.assertIn(direct_contract, docs_fast_text)

    def test_validator_selftest_is_relevant_only_and_local_ci_stays_focused(self) -> None:
        workflow = load_workflow(WORKFLOWS / "docs-ci.yml")
        selftest = workflow.get("jobs", {}).get("validator-selftest", {})
        self.assertEqual(
            selftest.get("timeout-minutes"),
            "10",
            "validator self-tests must be bounded to ten minutes",
        )
        self.assertIn("if", selftest, "validator self-tests must be path-filtered")

        workflow_text = (WORKFLOWS / "docs-ci.yml").read_text(encoding="utf-8")
        for relevant_path in (
            "scripts/validate_repository_policy.py",
            "scripts/validate_msp_055_api_freeze.py",
            "scripts/machine_publication_policy.py",
            "tests/test_policy_validator.py",
            "tests/policy_test_support.py",
        ):
            self.assertIn(
                relevant_path,
                workflow_text,
                f"validator-selftest routing must include {relevant_path}",
            )

        local_ci = require_executable(self, LOCAL_CI)
        self.assertIn("scripts/ci_docs_fast.sh", local_ci)
        self.assertNotIn("unittest discover", local_ci)
        self.assertIn("60", local_ci, "focused local CI must document its 60-second bound")

        selftest_text = require_executable(self, VALIDATOR_SELFTEST)
        for test_module in (
            "test_policy_validator",
            "test_machine_publication_policy",
            "test_api_surface_v1",
            "test_msp_docs_e2_red",
            "test_msp_docs_e2_remediation",
            "test_msp_055_api_freeze",
        ):
            self.assertIn(test_module, selftest_text)

        policy_tests = (REPO / "tests" / "test_policy_validator.py").read_text(
            encoding="utf-8"
        )
        self.assertIn("from validate_repository_policy import", policy_tests)
        self.assertIn("check_repository", policy_tests)
        self.assertIn("policy_test_support", policy_tests)

        fixture_driven_tests = (
            "test_policy_validator.py",
            "test_machine_publication_policy.py",
            "test_api_surface_v1.py",
            "test_msp_docs_e2_red.py",
            "test_msp_docs_e2_remediation.py",
        )
        for filename in fixture_driven_tests:
            source = (REPO / "tests" / filename).read_text(encoding="utf-8")
            self.assertNotIn(
                "shutil.copytree",
                source,
                f"{filename} must use the minimal imported policy fixture",
            )
            self.assertIn("materialize_policy_fixture", source)


if __name__ == "__main__":
    unittest.main()
