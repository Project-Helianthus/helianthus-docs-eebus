from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any

import yaml

REPO = Path(__file__).resolve().parents[1]
WORKFLOW = REPO / ".github" / "workflows" / "docs-ci.yml"
REGISTRY = Path("scripts/publication_channels.yaml")
RENDERER = REPO / "scripts" / "render_publication.py"
ATTESTER = REPO / "scripts" / "attest_publication.py"
COMPLETION_TOKEN = REPO / "scripts" / "publication_completion_token.py"
REPOSITORY = "Project-Helianthus/helianthus-docs-eebus"
MILESTONE = "MSP-DOCS-E2R-PUBLISH"
SOURCE_COMMIT = "1" * 40
PLATFORM_B_MERGE = "8872f65b888048db001b" "c640ae04a4f460ee8db1"
PLATFORM_B_COMPLETION_SHA256 = (
    "0b695b603f19dff35b857ddf47e03fe0"
    "ae02ac39ca89c353de8482872fd8c3de"
)
PLATFORM_B_MEMBERS = [
    "cross-runtime-platform-contracts",
    "eebus-api-v1",
    "eebus-architecture",
    "eebus-protocol",
    "platform-cross-runtime-envelope",
    "platform-hash-auth-binding",
    "platform-ownership-validation",
    "platform-promotion-consumer-contract",
    "platform-shared-registry-boundary",
]
CHANNELS = {
    "search": "api/search-index.json",
    "sitemap": "api/sitemap.xml",
    "versioned_bundle": "api/versioned-bundle.txt",
    "release_bundle": "api/release-bundle.txt",
}
MEMBERS = [
    "api/api-surface-v1.md",
    "architecture/README.md",
    "protocols/ship-spine-overview.md",
]
OUTPUT_ROOTS = ["api", "build", "dist", "exports", "output", "public", "release", "site"]


def requirement_blocks(text: str) -> list[str]:
    blocks: list[list[str]] = []
    current: list[str] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if raw_line[:1].isspace():
            if not current:
                raise AssertionError("orphan requirement continuation")
            current.append(line.removesuffix("\\").strip())
            continue
        if current:
            blocks.append(current)
        current = [line.removesuffix("\\").strip()]
    if current:
        blocks.append(current)
    return [" ".join(block) for block in blocks]

def copy_repo(parent: Path) -> Path:
    return Path(
        shutil.copytree(
            REPO,
            parent / "repo",
            ignore=shutil.ignore_patterns(".git", ".pytest_cache", "__pycache__"),
        )
    )

def run_tool(script: Path, *arguments: str, cwd: Path | None = None,
             env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(script), *arguments], cwd=cwd, env=env,
        check=False, text=True, capture_output=True,
    )

def load_registry(root: Path) -> dict[str, Any]:
    document = yaml.safe_load((root / REGISTRY).read_text(encoding="utf-8"))
    if not isinstance(document, dict):
        raise AssertionError("publication registry must be a mapping")
    return document

def expected_outputs(registry: dict[str, Any]) -> dict[str, bytes]:
    rendered: dict[str, bytes] = {}
    for channel, specification in registry["channels"].items():
        members = specification["members"]
        if channel == "search":
            text = json.dumps({"pages": members}, ensure_ascii=True, separators=(",", ":")) + "\n"
        elif channel == "sitemap":
            entries = "".join(f"<url><loc>{member}</loc></url>" for member in members)
            text = (
                '<?xml version="1.0" encoding="UTF-8"?>\n'
                '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
                f"{entries}</urlset>\n"
            )
        else:
            text = "".join(f"{member}\n" for member in members)
        rendered[specification["artifact"]] = text.encode("utf-8")
    return rendered

def tree_bytes(root: Path) -> dict[str, bytes]:
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in sorted(root.rglob("*")) if path.is_file()
    }

def render(repo: Path, output: Path, evidence: Path, commit: str = SOURCE_COMMIT,
           *, cwd: Path | None = None, env: dict[str, str] | None = None
           ) -> subprocess.CompletedProcess[str]:
    return run_tool(
        RENDERER, "render", "--repo", str(repo), "--output", str(output),
        "--evidence-core", str(evidence), "--source-commit", commit, cwd=cwd, env=env,
    )

def build_token_fixture(parent: Path) -> tuple[Path, str, str, str]:
    repo = copy_repo(parent)
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
    subprocess.run(
        ["git", "remote", "add", "origin", "https://github.com/Project-Helianthus/helianthus-docs-eebus.git"],
        cwd=repo,
        check=True,
    )
    env = os.environ.copy()
    env.update(
        {
            "GIT_AUTHOR_DATE": "2026-07-13T18:00:00Z",
            "GIT_COMMITTER_DATE": "2026-07-13T18:00:00Z",
        }
    )
    marker = repo / "fixture-phase.txt"
    marker.write_text("base\n", encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=repo, check=True)
    subprocess.run(
        ["git", "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid", "commit", "-qm", "base"],
        cwd=repo,
        check=True,
        env=env,
    )
    base_oid = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo, text=True).strip()
    marker.write_text("head\n", encoding="utf-8")
    subprocess.run(["git", "add", str(marker)], cwd=repo, check=True)
    subprocess.run(
        ["git", "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid", "commit", "-qm", "head"],
        cwd=repo,
        check=True,
        env=env,
    )
    head_oid = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo, text=True).strip()
    tree_oid = subprocess.check_output(["git", "rev-parse", "HEAD^{tree}"], cwd=repo, text=True).strip()
    merge_oid = subprocess.check_output(
        ["git", "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid", "commit-tree", tree_oid, "-p", base_oid, "-m", "squash merge"],
        cwd=repo,
        text=True,
        env=env,
    ).strip()
    subprocess.run(["git", "reset", "--hard", "-q", merge_oid], cwd=repo, check=True)
    return repo, base_oid, head_oid, merge_oid

def completion_token_command(repo: Path, base_oid: str, head_oid: str,
                             merge_oid: str) -> list[str]:
    return [
        sys.executable,
        str(repo / "scripts" / "publication_completion_token.py"),
        "--root", str(repo),
        "--repository", REPOSITORY,
        "--pr", "11",
        "--base-oid", base_oid,
        "--head-oid", head_oid,
        "--merge-oid", merge_oid,
        "--evaluated-at", "2026-07-13T18:00:01Z",
        "--observation-source", "test.fixture-clock",
    ]

class MspDocsE2RPublishRedTests(unittest.TestCase):
    def test_ci_is_immutable_least_privilege_hash_locked_and_post_merge(self) -> None:
        workflow = yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))
        steps = workflow["jobs"]["docs-checks"]["steps"]
        errors: list[str] = []
        if workflow.get("permissions") != {"contents": "read"}:
            errors.append("workflow permissions must be exactly contents: read")
        for job_name, job in workflow["jobs"].items():
            if "permissions" in job and job["permissions"] != {"contents": "read"}:
                errors.append(f"{job_name} broadens workflow permissions")
        for step in steps:
            action = step.get("uses")
            if action and not re.fullmatch(r"[^@]+@[0-9a-f]{40}", action):
                errors.append(f"mutable action ref: {action}")
        checkout = next((step for step in steps if str(step.get("uses", "")).startswith("actions/checkout@")), {})
        if checkout.get("with", {}).get("persist-credentials") is not False:
            errors.append("checkout must set persist-credentials: false")
        setup = next((step for step in steps if str(step.get("uses", "")).startswith("actions/setup-python@")), {})
        if setup.get("with", {}).get("python-version") != "3.12.10":
            errors.append("Python must be pinned to 3.12.10")
        install_runs = [str(step.get("run", "")) for step in steps if "pip install" in str(step.get("run", ""))]
        if not any("--require-hashes" in command and "requirements-ci.txt" in command for command in install_runs):
            errors.append("dependency bootstrap must use --require-hashes")
        requirements = (REPO / "requirements-ci.txt").read_text(encoding="utf-8")
        for block in requirement_blocks(requirements):
            requirement = block.split()[0]
            if re.fullmatch(r"[A-Za-z0-9_.-]+==[^\s]+", requirement) is None:
                errors.append(f"dependency is not exactly pinned: {requirement}")
            if re.search(r"--hash=sha256:[0-9a-f]{64}(?:\s|$)", block) is None:
                errors.append(f"dependency lacks sha256 lock: {requirement}")
        post_merge = [
            step for step in steps
            if "github.event_name == 'push'" in str(step.get("if", ""))
            and "github.ref == 'refs/heads/main'" in str(step.get("if", ""))
        ]
        commands = "\n".join(str(step.get("run", "")) for step in post_merge)
        if "render_publication.py" not in commands or "attest_publication.py" not in commands or "GITHUB_SHA" not in commands:
            errors.append("main-push PUBLISH render and attestation step is missing")
        self.assertEqual(errors, [])

    def test_platform_b_v2_registry_preserves_membership_and_binds_publisher(self) -> None:
        registry = load_registry(REPO)
        errors: list[str] = []
        if set(registry) != {
            "schema",
            "version",
            "platform_contract",
            "public_output_roots",
            "publisher",
            "channels",
        }:
            errors.append("registry v2 has a non-closed top-level shape")
        if registry.get("schema") != "helianthus.publication-channels" or registry.get("version") != "2":
            errors.append("PLATFORM-B publication registry must be version 2")
        if registry.get("public_output_roots") != OUTPUT_ROOTS:
            errors.append("v2 must preserve public output roots")
        expected_platform_contract = {
            "source_repository": "Project-Helianthus/helianthus-docs-ebus",
            "source_merge": PLATFORM_B_MERGE,
            "source_manifest_path": (
                "docs/platform/manifests/eebus-doc-ownership.yaml"
            ),
            "source_manifest_blob_mode": "100644",
            "source_manifest_oid": "1f7c7c0a94504614949e" "3478387fca4def079c2e",
            "source_manifest_sha256": (
                "3f7b16f32ded7f16b12ecd644d361f31"
                "5df1ba6d10d462a9c9054585774fd04e"
            ),
            "completion_proof_sha256": PLATFORM_B_COMPLETION_SHA256,
            "channel_registry": {
                "canonical": {
                    "visibility": "stable",
                    "owner": "canonical_documentation_owner",
                }
            },
            "eligible_channels": {
                member: ["canonical"] for member in PLATFORM_B_MEMBERS
            },
            "exact_memberships": {"canonical": PLATFORM_B_MEMBERS},
            "candidate_inventory": [],
        }
        if registry.get("platform_contract") != expected_platform_contract:
            errors.append("exact PLATFORM-B completion semantics are not preserved")
        channels = registry.get("channels")
        if not isinstance(channels, dict) or set(channels) != set(CHANNELS):
            errors.append("v2 must preserve the four stable channels")
        else:
            for channel, artifact in CHANNELS.items():
                if channels[channel] != {"artifact": artifact, "members": MEMBERS}:
                    errors.append(f"{channel} artifact/member semantics changed")
        publisher = registry.get("publisher")
        if not isinstance(publisher, dict) or set(publisher) != {"repository", "path", "blob_mode", "oid", "sha256"}:
            errors.append("publisher binding is absent or open shaped")
        elif not RENDERER.is_file():
            errors.append("bound publication renderer is missing")
        else:
            payload = RENDERER.read_bytes()
            oid = hashlib.sha1(f"blob {len(payload)}\0".encode() + payload).hexdigest()
            expected = {
                "repository": REPOSITORY, "path": "scripts/render_publication.py",
                "blob_mode": "100755", "oid": oid,
                "sha256": hashlib.sha256(payload).hexdigest(),
            }
            if publisher != expected:
                errors.append("publisher repo/path/mode/OID/SHA-256 binding is invalid")
        self.assertEqual(errors, [])

    def test_renderer_regenerates_exact_inventory_and_is_deterministic(self) -> None:
        self.assertTrue(RENDERER.is_file(), "missing PUBLISH renderer interface")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = copy_repo(root)
            registry = load_registry(repo)
            for relative_path in expected_outputs(registry):
                (repo / relative_path).write_text("stale generated bytes\n", encoding="utf-8")
            first, second = root / "first", root / "second"
            evidence_a, evidence_b = root / "a.json", root / "b.json"
            result_a = render(repo, first, evidence_a)
            result_b = render(repo, second, evidence_b)
            self.assertEqual(result_a.returncode, 0, result_a.stderr)
            self.assertEqual(result_b.returncode, 0, result_b.stderr)
            self.assertEqual(tree_bytes(first), expected_outputs(registry))
            self.assertEqual(tree_bytes(second), tree_bytes(first))
            self.assertEqual(evidence_b.read_bytes(), evidence_a.read_bytes())
            verified = run_tool(RENDERER, "verify", "--repo", str(repo),
                                "--output", str(first), "--source-commit", SOURCE_COMMIT)
            self.assertEqual(verified.returncode, 0, verified.stderr)

    def test_renderer_is_hermetic_and_honors_the_supplied_root(self) -> None:
        self.assertTrue(RENDERER.is_file(), "missing PUBLISH renderer interface")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = copy_repo(root)
            registry = load_registry(repo)
            for value in registry["channels"].values():
                value["members"] = sorted([*value["members"], "README.md"], key=lambda item: item.encode())
            (repo / REGISTRY).write_text(yaml.safe_dump(registry, sort_keys=False), encoding="utf-8")
            guard = root / "guard"
            guard.mkdir()
            (guard / "sitecustomize.py").write_text(
                "import socket\n"
                "def blocked(*args, **kwargs): raise AssertionError('network access attempted')\n"
                "socket.socket.connect = blocked\nsocket.create_connection = blocked\n",
                encoding="utf-8",
            )
            outside = root / "outside"
            outside.mkdir()
            env = os.environ.copy()
            env.update({"PATH": "", "HOME": str(root / "home"), "PYTHONPATH": str(guard)})
            result = render(repo, root / "output", root / "evidence.json", cwd=outside, env=env)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(tree_bytes(root / "output"), expected_outputs(registry))

    def test_candidate_forms_are_rejected_in_members_redirects_and_generated_output(self) -> None:
        self.assertTrue(RENDERER.is_file(), "missing PUBLISH renderer interface")
        cases = {
            "encoded alternate-case member": ("API/%255fCaNdIdAtE/runtime-reference.md", "synthetic public page\n"),
            "encoded redirect": (
                "public/stable-redirect.html",
                '<meta http-equiv="refresh" content="0;url=api/%255FCaNdIdAtE/runtime-reference.md">\n',
            ),
        }
        for label, (member, content) in cases.items():
            with self.subTest(label=label), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                repo = copy_repo(root)
                target = repo / member
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(content, encoding="utf-8")
                registry = load_registry(repo)
                registry["channels"]["search"]["members"].append(member)
                (repo / REGISTRY).write_text(yaml.safe_dump(registry, sort_keys=False), encoding="utf-8")
                result = render(repo, root / "output", root / "evidence.json")
                self.assertNotEqual(result.returncode, 0, result.stderr)
                self.assertFalse((root / "evidence.json").exists())

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = copy_repo(root)
            result = render(repo, root / "output", root / "evidence.json")
            self.assertEqual(result.returncode, 0, result.stderr)
            (root / "output" / CHANNELS["search"]).write_text(
                '{"pages":["API\\u002f_CaNdIdAtE\\u002fruntime-reference.md"]}\n',
                encoding="utf-8",
            )
            verified = run_tool(RENDERER, "verify", "--repo", str(repo),
                                "--output", str(root / "output"),
                                "--source-commit", SOURCE_COMMIT)
            self.assertNotEqual(verified.returncode, 0, verified.stderr)
            self.assertIn("candidate", verified.stderr.lower())

    def test_readme_declares_e2_active_and_ownership_boundaries(self) -> None:
        text = (REPO / "README.md").read_text(encoding="utf-8")
        end = text.index("\n---\n", 4)
        metadata = yaml.safe_load(text[4:end])
        self.assertEqual(metadata.get("milestone"), "MSP-DOCS-E2")
        self.assertEqual(metadata.get("milestone_state"), "active")
        body = text[end + 5:]
        self.assertIn("eeBUS-native", body)
        self.assertIn("helianthus-docs-ebus/docs/platform/", body)
        self.assertRegex(body, r"(?s)`protocols/` owns eeBUS/SHIP/SPINE.*`architecture/` owns.*`api/` owns")

    def test_publish_evidence_token_is_canonical_bound_and_deterministic(self) -> None:
        self.assertTrue(RENDERER.is_file(), "missing PUBLISH renderer interface")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = copy_repo(root)
            evidence_a, evidence_b = root / "a.json", root / "b.json"
            first = render(repo, root / "first", evidence_a)
            second = render(repo, root / "second", evidence_b)
            self.assertEqual(first.returncode, 0, first.stderr)
            self.assertEqual(second.returncode, 0, second.stderr)
            self.assertEqual(evidence_a.read_bytes(), evidence_b.read_bytes())
            evidence = json.loads(evidence_a.read_bytes())
            self.assertEqual(set(evidence), {
                "schema", "version", "milestone", "state", "source", "publisher",
                "platform_contract", "artifacts", "completion_digest",
            })
            self.assertEqual(evidence["schema"], "helianthus.docs-publication-evidence")
            self.assertEqual((evidence["version"], evidence["milestone"], evidence["state"]), (1, MILESTONE, "PUBLISH"))
            self.assertEqual(evidence["source"], {"repository": REPOSITORY, "commit": SOURCE_COMMIT})
            self.assertEqual(evidence["publisher"], load_registry(repo)["publisher"])
            self.assertEqual(
                evidence["platform_contract"],
                load_registry(repo)["platform_contract"],
            )
            expected = expected_outputs(load_registry(repo))
            artifacts = [
                {
                    "channel": channel, "path": path,
                    "member_paths": load_registry(repo)["channels"][channel]["members"],
                    "sha256": hashlib.sha256(expected[path]).hexdigest(),
                }
                for channel, path in sorted(CHANNELS.items(), key=lambda item: item[0].encode())
            ]
            self.assertEqual(evidence["artifacts"], artifacts)
            completion_digest = evidence.pop("completion_digest")
            core = json.dumps(evidence, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode()
            self.assertEqual(
                completion_digest,
                "sha256:" + hashlib.sha256(core).hexdigest(),
            )
            evidence["completion_digest"] = completion_digest
            canonical = json.dumps(evidence, ensure_ascii=True, sort_keys=True, separators=(",", ":")) + "\n"
            self.assertEqual(evidence_a.read_text(encoding="utf-8"), canonical)

    def test_attestation_is_a_separate_closed_content_free_process(self) -> None:
        self.assertTrue(RENDERER.is_file(), "missing PUBLISH renderer interface")
        self.assertTrue(ATTESTER.is_file(), "missing separate PUBLISH attester interface")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = copy_repo(root)
            evidence, attestation = root / "evidence.json", root / "attestation.json"
            rendered = render(repo, root / "output", evidence)
            self.assertEqual(rendered.returncode, 0, rendered.stderr)
            result = run_tool(
                ATTESTER, "--evidence-core", str(evidence), "--output", str(attestation)
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            document = json.loads(attestation.read_bytes())
            self.assertEqual(set(document), {
                "schema", "version", "milestone", "state", "source",
                "completion_digest",
                "evidence_core_sha256", "artifact_count",
            })
            self.assertEqual(document["state"], "ATTESTED")
            self.assertEqual(
                document["completion_digest"],
                json.loads(evidence.read_bytes())["completion_digest"],
            )
            self.assertEqual(document["evidence_core_sha256"], hashlib.sha256(evidence.read_bytes()).hexdigest())
            self.assertEqual(document["artifact_count"], len(CHANNELS))
            marker = "SYNTHETIC-CONTENT-MUST-NOT-ESCAPE"
            contaminated = json.loads(evidence.read_bytes())
            contaminated["content"] = marker
            bad_evidence = root / "content-bearing.json"
            bad_evidence.write_text(json.dumps(contaminated), encoding="utf-8")
            rejected = run_tool(
                ATTESTER, "--evidence-core", str(bad_evidence),
                "--output", str(root / "rejected.json"),
            )
            self.assertNotEqual(rejected.returncode, 0, rejected.stderr)
            self.assertNotIn(marker, attestation.read_text(encoding="utf-8"))

    def test_post_merge_completion_token_binds_exact_git_objects_and_replay(self) -> None:
        self.assertTrue(COMPLETION_TOKEN.is_file(), "missing post-merge completion token")
        with tempfile.TemporaryDirectory() as tmp:
            repo, base_oid, head_oid, merge_oid = build_token_fixture(Path(tmp))
            command = completion_token_command(repo, base_oid, head_oid, merge_oid)
            first = subprocess.run(command, check=False, capture_output=True, text=True)
            second = subprocess.run(command, check=False, capture_output=True, text=True)
            self.assertEqual(first.returncode, 0, first.stderr)
            self.assertEqual(second.returncode, 0, second.stderr)
            self.assertEqual(first.stdout, second.stdout)
            envelope = json.loads(first.stdout)
            self.assertEqual(envelope["schema_version"], 2)
            self.assertEqual(envelope["producer_id"], MILESTONE)
            self.assertEqual(envelope["consumer_id"], "MSP-DOCS-E2R-AGGREGATE")
            self.assertEqual(envelope["repository"], REPOSITORY)
            self.assertEqual(envelope["pr"], 11)
            self.assertEqual(envelope["base_oid"], base_oid)
            self.assertEqual(envelope["head_oid"], head_oid)
            self.assertEqual(envelope["merge_oid"], merge_oid)
            self.assertEqual(
                envelope["tree_oid"],
                subprocess.check_output(
                    ["git", "rev-parse", f"{merge_oid}^{{tree}}"], cwd=repo, text=True
                ).strip(),
            )
            core = json.dumps(
                envelope["evidence_core"],
                ensure_ascii=True,
                separators=(",", ":"),
                sort_keys=True,
            ).encode()
            self.assertEqual(envelope["evidence_core_sha256"], hashlib.sha256(core).hexdigest())
            evidence = envelope["evidence_core"]["publication_evidence"]
            self.assertEqual(evidence["source"]["commit"], merge_oid)
            self.assertEqual(envelope["prior_token_digest"], PLATFORM_B_COMPLETION_SHA256)

            dirty = repo / "untracked.txt"
            dirty.write_text("drift\n", encoding="utf-8")
            rejected = subprocess.run(command, check=False, capture_output=True, text=True)
            self.assertEqual(rejected.returncode, 1)
            self.assertEqual(rejected.stderr, "publication-token.identity\n")

    def test_publication_outputs_reject_symlinked_ancestor_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = copy_repo(root)
            real = root / "real"
            real.mkdir()
            linked = root / "linked"
            linked.symlink_to(real, target_is_directory=True)
            rejected = render(repo, linked / "publication", root / "evidence.json")
            self.assertNotEqual(rejected.returncode, 0, rejected.stderr)
            self.assertIn("unsafe", rejected.stderr)

            evidence = root / "source-evidence.json"
            rendered = render(repo, real / "publication", evidence)
            self.assertEqual(rendered.returncode, 0, rendered.stderr)
            attested = run_tool(
                ATTESTER,
                "--evidence-core", str(evidence),
                "--output", str(linked / "attestation.json"),
            )
            self.assertNotEqual(attested.returncode, 0, attested.stderr)
            self.assertIn("unsafe", attested.stderr)

    def test_hash_locks_cover_linux_macos_and_source_fallbacks(self) -> None:
        blocks = requirement_blocks(
            (REPO / "requirements-ci.txt").read_text(encoding="utf-8")
        )
        locks = {block.split()[0]: block.count("--hash=sha256:") for block in blocks}
        self.assertEqual(
            locks,
            {"PyYAML==6.0.3": 5, "markdown-it-py==4.0.0": 2, "mdurl==0.1.2": 2},
        )
if __name__ == "__main__":
    unittest.main()
