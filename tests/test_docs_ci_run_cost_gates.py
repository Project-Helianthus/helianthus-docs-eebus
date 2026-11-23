"""Docs CI cost gates: main-push cancellation and the path-gated Combined Ref job on pull requests."""

from __future__ import annotations

import os
import pathlib
import subprocess

import pytest
import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOCS_CI = ROOT / ".github/workflows/docs-ci.yml"
DONOR_DOCS_CI = ROOT / ".tmp" / "docs-ebus" / ".github/workflows/docs-ci.yml"
COMBINED_REF = ROOT / ".github/workflows/platform-contracts-combined-ref.yml"
GATE_CONDITION = "steps.platform_inputs.outputs.changed == 'true'"
PLATFORM_INPUTS = ("docs/platform", "scripts", ".github/workflows", "requirements-ci.txt")


def load(path: pathlib.Path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def combined_ref_steps() -> list[dict]:
    return load(COMBINED_REF)["jobs"]["validate"]["steps"]


def classify_step() -> dict:
    [step] = [s for s in combined_ref_steps() if s.get("name") == "Classify platform input changes"]
    return step


def test_main_pushes_cancel_superseded_runs_but_never_the_nightly_run():
    donor = load(DONOR_DOCS_CI)
    concurrency = donor["concurrency"]
    assert concurrency["group"] == "${{ github.workflow }}-${{ github.event_name }}-${{ github.ref }}"
    assert concurrency["cancel-in-progress"] == (
        "${{ github.event_name == 'pull_request' || github.event_name == 'push' }}"
    )
    # Schedule and dispatch runs share no group with pushes and never cancel.
    triggers = donor[True]
    assert set(triggers) == {"pull_request", "push", "schedule", "workflow_dispatch"}
    assert triggers["push"]["branches"] == ["main"]

    receiver = load(DOCS_CI)
    receiver_triggers = receiver.get(True, receiver.get("on"))
    assert set(receiver_triggers) == {
        "pull_request",
        "push",
        "schedule",
        "workflow_dispatch",
    }
    assert receiver_triggers["push"]["branches"] == ["main"]
    assert receiver["concurrency"]["cancel-in-progress"] == (
        "${{ github.event_name == 'pull_request' }}"
    )
    assert "github.workflow" in receiver["concurrency"]["group"]
    assert "github.event.pull_request.number" in receiver["concurrency"]["group"]
    assert "github.ref" in receiver["concurrency"]["group"]


def test_nightly_run_validates_combined_refs_against_main_itself():
    job = load(DOCS_CI)["jobs"]["platform-contracts-combined-ref"]
    assert job["if"] == (
        "github.event_name == 'pull_request' || github.event_name == 'push' "
        "|| github.event_name == 'schedule'"
    )
    assert job["with"]["docs_base_ref"] == (
        "${{ github.event_name == 'pull_request' && github.event.pull_request.base.sha "
        "|| github.event_name == 'schedule' && github.sha || github.event.before }}"
    )
    assert job["with"]["docs_ref"] == (
        "${{ github.event_name == 'pull_request' && github.event.pull_request.head.sha "
        "|| github.sha }}"
    )


def test_combined_ref_job_always_runs_and_gates_every_step_after_classification():
    workflow = load(COMBINED_REF)
    assert "if" not in workflow["jobs"]["validate"]
    names = [step.get("name") for step in combined_ref_steps()]
    index = names.index("Classify platform input changes")
    assert names[index - 2:index] == ["Checkout docs ref", "Checkout trusted docs prior manifest"]
    for step in combined_ref_steps()[:index + 1]:
        assert "if" not in step, step.get("name")
    later = combined_ref_steps()[index + 1:]
    assert later, "no validation steps follow the classification"
    for step in later:
        assert step.get("if") == GATE_CONDITION, step.get("name")
    assert classify_step()["env"] == {
        "EVENT_NAME": "${{ github.event_name }}",
        "SAME_REPOSITORY": "${{ inputs.docs_repository == github.repository }}",
    }


def write(root: pathlib.Path, relative: str, text: str) -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


@pytest.fixture
def workspace(tmp_path):
    for checkout in ("checkouts/docs-base", "checkouts/docs"):
        root = tmp_path / checkout
        write(root, "docs/platform/manifests/m.yaml", "manifest\n")
        write(root, "scripts/validate_platform_contracts.py", "validator\n")
        write(root, ".github/workflows/docs-ci.yml", "workflow\n")
        write(root, "requirements-ci.txt", "pins\n")
        write(root, "protocols/vaillant/page.md", "page\n")
    return tmp_path


def classify(workspace: pathlib.Path, event: str = "pull_request", same: str = "true") -> tuple[str, str]:
    output = workspace / "github-output"
    output.write_text("", encoding="utf-8")
    env = dict(os.environ, EVENT_NAME=event, SAME_REPOSITORY=same,
               GITHUB_WORKSPACE=str(workspace), GITHUB_OUTPUT=str(output))
    result = subprocess.run(["bash", "-c", classify_step()["run"]], env=env,
                            capture_output=True, text=True, check=False)
    assert result.returncode == 0, result.stderr
    return output.read_text(encoding="utf-8"), result.stdout


def test_unrelated_change_skips_validation_on_pull_requests(workspace):
    write(workspace / "checkouts/docs-base", "protocols/vaillant/page.md", "changed page\n")
    write(workspace / "checkouts/docs", "architecture/new.md", "new page\n")
    write(workspace / "checkouts/docs", "scripts/__pycache__/x.pyc", "cache\n")
    output, stdout = classify(workspace)
    assert output == "changed=false\n"
    assert "Skipping combined-ref validation" in stdout


def test_main_pushes_always_validate(workspace):
    write(workspace / "checkouts/docs-base", "protocols/vaillant/page.md", "changed page\n")
    output, stdout = classify(workspace, "push")
    assert output == "changed=true\n"
    assert "Combined-ref validation runs." in stdout


@pytest.mark.parametrize("relative", [
    "docs/platform/manifests/m.yaml", "docs/platform/new-fixture.json",
    "scripts/validate_platform_contracts.py", "scripts/new_helper.py",
    ".github/workflows/docs-ci.yml", "requirements-ci.txt",
])
def test_platform_input_change_validates(workspace, relative):
    write(workspace / "checkouts/docs", relative, "changed\n")
    output, _ = classify(workspace)
    assert output == "changed=true\n"


def test_deleted_or_missing_input_validates(workspace):
    (workspace / "checkouts/docs/requirements-ci.txt").unlink()
    output, stdout = classify(workspace)
    assert output == "changed=true\n"
    assert "not comparable: requirements-ci.txt" in stdout


@pytest.mark.parametrize(("event", "same"), [
    ("schedule", "true"), ("workflow_dispatch", "true"), ("workflow_dispatch", "false"),
    ("pull_request", "false"),
])
def test_nightly_dispatch_and_fork_runs_always_validate(workspace, event, same):
    output, _ = classify(workspace, event, same)
    assert output == "changed=true\n"


def test_classifier_compares_exactly_the_documented_inputs():
    script = classify_step()["run"]
    assert f"for path in {' '.join(PLATFORM_INPUTS)}; do" in script
