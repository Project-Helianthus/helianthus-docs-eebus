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
    assert job["with"]["docs_repository"] == "Project-Helianthus/helianthus-docs"
    assert job["with"]["docs_ref"] == (
        "ff8fccc7" + "d5fbcbfe1e156fce302549d04a2f6228"
    )
    assert job["with"]["docs_base_ref"] == (
        "${{ github.event_name == 'pull_request' && github.event.pull_request.base.sha "
        "|| github.event_name == 'schedule' && github.sha || github.event.before }}"
    )
    assert job["with"]["docs_eebus_repository"] == (
        "${{ github.event_name == 'pull_request' && "
        "github.event.pull_request.head.repo.full_name || github.repository }}"
    )
    assert job["with"]["docs_eebus_ref"] == (
        "${{ github.event_name == 'pull_request' && github.event.pull_request.head.sha "
        "|| github.sha }}"
    )


def test_combined_ref_job_always_runs_and_gates_every_step_after_classification():
    workflow = load(COMBINED_REF)
    assert "if" not in workflow["jobs"]["validate"]
    names = [step.get("name") for step in combined_ref_steps()]
    index = names.index("Classify platform input changes")
    assert names[index - 2:index] == [
        "Checkout trusted docs prior manifest",
        "Verify platform pin and prior owner",
    ]
    for step in combined_ref_steps()[:index + 1]:
        assert "if" not in step, step.get("name")
    later = combined_ref_steps()[index + 1:]
    assert later, "no validation steps follow the classification"
    for step in later:
        assert step.get("if") == GATE_CONDITION, step.get("name")
    assert classify_step()["env"] == {
        "EVENT_NAME": "${{ github.event_name }}",
        "SAME_REPOSITORY": "${{ inputs.docs_eebus_repository == github.repository }}",
    }


def write(root: pathlib.Path, relative: str, text: str) -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


@pytest.fixture
def workspace(tmp_path):
    for checkout in ("checkouts/docs-eebus-base", "checkouts/docs-eebus"):
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
    write(workspace / "checkouts/docs-eebus-base", "protocols/vaillant/page.md", "changed page\n")
    write(workspace / "checkouts/docs-eebus", "architecture/new.md", "new page\n")
    write(workspace / "checkouts/docs-eebus", "scripts/__pycache__/x.pyc", "cache\n")
    output, stdout = classify(workspace)
    assert output == "changed=false\n"
    assert "Skipping combined-ref validation" in stdout


def test_main_pushes_always_validate(workspace):
    write(workspace / "checkouts/docs-eebus-base", "protocols/vaillant/page.md", "changed page\n")
    output, stdout = classify(workspace, "push")
    assert output == "changed=true\n"
    assert "Combined-ref validation runs." in stdout


@pytest.mark.parametrize("relative", [
    "docs/platform/manifests/m.yaml", "docs/platform/new-fixture.json",
    "scripts/validate_platform_contracts.py", "scripts/new_helper.py",
    ".github/workflows/docs-ci.yml", "requirements-ci.txt",
])
def test_platform_input_change_validates(workspace, relative):
    write(workspace / "checkouts/docs-eebus", relative, "changed\n")
    output, _ = classify(workspace)
    assert output == "changed=true\n"


def test_deleted_or_missing_input_validates(workspace):
    (workspace / "checkouts/docs-eebus/requirements-ci.txt").unlink()
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


PLATFORM_PIN = "ff8fccc7" + "d5fbcbfe1e156fce302549d04a2f6228"
DONOR_PIN = "977614c9" + "44cd685bef75b5b12148e1110ed7653a"
MSP055_SOURCE = "7a5852e0" + "09bbdcba47f0a34ba866070a4ab35ef8"
OWNER_REPOSITORY = "Project-Helianthus/helianthus-docs-eebus"


def _step(name: str) -> dict:
    [step] = [item for item in combined_ref_steps() if item.get("name") == name]
    return step


def _commit(repo: pathlib.Path, files: dict[str, str]) -> str:
    repo.mkdir(parents=True, exist_ok=True)
    if not (repo / ".git").is_dir():
        subprocess.run(["git", "init", "--quiet"], cwd=repo, check=True)
        subprocess.run(
            ["git", "config", "user.email", "dev@example.com"], cwd=repo, check=True
        )
        subprocess.run(["git", "config", "user.name", "dev"], cwd=repo, check=True)
        subprocess.run(
            [
                "git",
                "remote",
                "add",
                "origin",
                f"https://github.com/{OWNER_REPOSITORY}.git",
            ],
            cwd=repo,
            check=True,
        )
    for relative, text in files.items():
        path = repo / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    subprocess.run(["git", "add", "--", *files], cwd=repo, check=True)
    subprocess.run(["git", "commit", "--quiet", "-m", "fixture"], cwd=repo, check=True)
    return subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=repo, text=True
    ).strip()


def _run_step(name: str, workspace: pathlib.Path, env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    output = workspace / "github-output"
    output.write_text("", encoding="utf-8")
    full_env = dict(os.environ)
    full_env.update(env)
    full_env["GITHUB_WORKSPACE"] = str(workspace)
    full_env["GITHUB_OUTPUT"] = str(output)
    return subprocess.run(
        ["bash", "-c", _step(name)["run"]],
        env=full_env,
        cwd=workspace,
        capture_output=True,
        text=True,
        check=False,
    )


def _select_env(base: str, *, event: str = "pull_request") -> dict[str, str]:
    return {
        "DOCS_BASE_REF": base,
        "DOCS_REF": PLATFORM_PIN,
        "DOCS_REPOSITORY": "Project-Helianthus/helianthus-docs",
        "EVENT_NAME": event,
        "GITHUB_REPOSITORY": OWNER_REPOSITORY,
        "GITHUB_SHA": base,
        "PR_BASE_SHA": base,
        "PUSH_BEFORE": base,
        "HEAD_REPOSITORY": OWNER_REPOSITORY,
        "HEAD_SHA": base,
    }


def test_trusted_inputs_use_platform_pin_then_owner_base(tmp_path):
    owner = tmp_path / "checkouts" / "docs-eebus-base"
    first = _commit(owner, {"README.md": "no manifest yet\n"})
    result = _run_step("Select trusted validator and prior", tmp_path, _select_env(first))
    assert result.returncode == 0, result.stderr
    output = (tmp_path / "github-output").read_text(encoding="utf-8")
    assert "validator_repository=Project-Helianthus/helianthus-docs\n" in output
    assert f"validator_ref={PLATFORM_PIN}\n" in output
    assert "prior_repository=Project-Helianthus/helianthus-docs-ebus\n" in output
    assert f"prior_ref={DONOR_PIN}\n" in output
    assert "mode=first\n" in output

    later = _commit(
        owner,
        {"docs/platform/manifests/eebus-doc-ownership.yaml": "manifest: owned\n"},
    )
    result = _run_step("Select trusted validator and prior", tmp_path, _select_env(later))
    assert result.returncode == 0, result.stderr
    output = (tmp_path / "github-output").read_text(encoding="utf-8")
    assert f"validator_repository={OWNER_REPOSITORY}\n" in output
    assert f"validator_ref={later}\n" in output
    assert f"prior_repository={OWNER_REPOSITORY}\n" in output
    assert f"prior_ref={later}\n" in output
    assert "mode=later\n" in output

    rejected = _select_env(later)
    rejected["DOCS_REF"] = later
    rejected["DOCS_REPOSITORY"] = OWNER_REPOSITORY
    result = _run_step("Select trusted validator and prior", tmp_path, rejected)
    assert result.returncode != 0


def test_docs_eebus_head_must_match_the_event(tmp_path):
    head = _commit(tmp_path / "checkouts" / "docs-eebus", {"README.md": "head\n"})
    env = _select_env(head)
    env["DOCS_EEBUS_REF"] = head
    env["DOCS_EEBUS_REPOSITORY"] = OWNER_REPOSITORY
    env["HEAD_SHA"] = head
    env["GITHUB_SHA"] = head
    result = _run_step("Verify docs-eebus head", tmp_path, env)
    assert result.returncode == 0, result.stderr

    env["DOCS_EEBUS_REF"] = PLATFORM_PIN
    result = _run_step("Verify docs-eebus head", tmp_path, env)
    assert result.returncode != 0


def test_docs_fast_creates_contract_output_parent(tmp_path):
    text = (ROOT / "scripts" / "ci_docs_fast.sh").read_text(encoding="utf-8")
    selected = [
        line
        for line in text.splitlines()
        if "mkdir -p .tmp" in line or "docs-fast-contracts" in line
    ]
    assert any("mkdir -p .tmp" in line for line in selected)
    assert selected.index(next(line for line in selected if "mkdir -p .tmp" in line)) < (
        selected.index(next(line for line in selected if "mktemp -d .tmp/docs-fast-contracts" in line))
    )
    result = subprocess.run(
        ["bash", "-c", "set -euo pipefail\n" + "\n".join(selected)],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert any((tmp_path / ".tmp").iterdir())


def test_markdown_checks_provisions_msp055_source():
    steps = load(DOCS_CI)["jobs"]["markdown-checks"]["steps"]
    source = next(step for step in steps if step.get("name") == "Checkout exact MSP-055 source")
    assert source["with"]["repository"] == "Project-Helianthus/helianthus-eebusreg"
    assert source["with"]["ref"] == MSP055_SOURCE
    assert source["with"]["path"] == "checkouts/msp055-source"
    run = next(step for step in steps if step.get("run") == "./scripts/ci_local.sh")
    assert run["env"]["MSP055_SOURCE_CHECKOUT"] == (
        "${{ github.workspace }}/" + source["with"]["path"]
    )
    assert steps.index(source) < steps.index(run)
