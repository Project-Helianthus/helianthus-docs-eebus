from __future__ import annotations

import re
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
CANDIDATE_REL = "architecture/_candidate/msp-04b-first-trust-admin-local.md"
CANDIDATE = ROOT / CANDIDATE_REL
STORE_CANDIDATE = ROOT / "architecture/_candidate/msp-04a-persistent-store.md"
MSP04A_IMPLEMENTATION_COMMIT = (
    "034c4cc5f7a58bdab08c" + "95d5b59fa8af13c5dd1d"
)
MSP04B_IMPLEMENTATION_COMMIT = (
    "18049eef059813c23d0a" + "3385115bfa61fcec635c"
)


def read_markdown(path: Path) -> tuple[dict[str, str], str]:
    text = path.read_text(encoding="utf-8")
    _, front_matter, body = text.split("---", 2)
    return yaml.safe_load(front_matter), body


def table_first_column(body: str, heading: str) -> set[str]:
    section = body.split(heading, 1)[1].split("\n## ", 1)[0]
    values: set[str] = set()
    in_table = False
    for line in section.splitlines():
        if line.startswith("| ---"):
            in_table = True
            continue
        if in_table and not line.startswith("|"):
            break
        if not in_table or not line.startswith("| `"):
            continue
        values.add(line.strip("|").split("|", 1)[0].strip().strip("`"))
    return values


def table_rows(body: str, heading: str) -> list[dict[str, str]]:
    lines = body.split(heading, 1)[1].splitlines()
    start = next(index for index, line in enumerate(lines) if line.startswith("|"))

    def cells(line: str) -> list[str]:
        return [cell.strip() for cell in line.strip("|").split("|")]

    headers = cells(lines[start])
    separator = cells(lines[start + 1])
    if len(headers) != len(separator) or not all(
        re.fullmatch(r":?-{3,}:?", cell) for cell in separator
    ):
        raise AssertionError(f"{heading} does not start with a valid Markdown table")

    rows: list[dict[str, str]] = []
    for line in lines[start + 2 :]:
        if not line.startswith("|"):
            break
        values = cells(line)
        if len(values) != len(headers):
            raise AssertionError(f"{heading} contains a malformed table row: {line}")
        rows.append(dict(zip(headers, values, strict=True)))
    return rows


def code_value(value: str) -> str:
    if not (value.startswith("`") and value.endswith("`")):
        raise AssertionError(f"expected one code value, got: {value}")
    return value[1:-1]


def state_values(value: str) -> set[str]:
    return {
        token
        for token in re.findall(r"`([^`]+)`", value)
        if re.fullmatch(r"[A-Z_]+", token)
    }


class MSP04BFirstTrustContractTest(unittest.TestCase):
    def test_candidate_metadata_and_publication_confinement(self) -> None:
        metadata, body = read_markdown(CANDIDATE)
        self.assertEqual(metadata["publication_status"], "candidate")
        self.assertEqual(metadata["claim_status"], "evidence-backed")
        self.assertEqual(metadata["source_class"], "derived_inference")
        self.assertEqual(metadata["hypothesis_status"], "draft")
        for channel in (
            "stable_navigation",
            "search",
            "sitemap",
            "versioned_bundle",
            "release_bundle",
        ):
            self.assertEqual(metadata[channel], "false")

        for relative in (
            "README.md",
            "architecture/README.md",
            "api/search-index.json",
            "api/sitemap.xml",
            "api/versioned-bundle.txt",
            "api/release-bundle.txt",
        ):
            self.assertNotIn(
                CANDIDATE_REL,
                (ROOT / relative).read_text(encoding="utf-8"),
            )

        self.assertIn(
            "https://github.com/Project-Helianthus/helianthus-docs-eebus/issues/22",
            body,
        )
        self.assertIn(
            "https://github.com/Project-Helianthus/helianthus-eebusreg/issues/26",
            body,
        )
        normalized = " ".join(body.split())
        self.assertIn("implementation merged in `helianthus-eebusreg`", normalized)
        self.assertIn(MSP04B_IMPLEMENTATION_COMMIT, normalized)
        self.assertIn("remains candidate and non-stable", normalized)
        self.assertIn("does not itself promote support", normalized)
        self.assertNotIn("pre-implementation architecture contract", normalized)
        self.assertNotIn("A merged MSP-04B implementation", metadata["falsifier"])

    def test_ownership_is_separated_and_public_surface_is_frozen(self) -> None:
        _, body = read_markdown(CANDIDATE)
        normalized = " ".join(body.split())
        self.assertEqual(
            table_first_column(body, "## Ownership Boundary"),
            {
                "internal/eebusstore",
                "private trust coordinator",
                "AF_UNIX admin transport",
                "facade/service adapter",
                "public Runtime/Snapshot/PairingState",
            },
        )

        required = (
            "policy-free validation",
            "opaque remote associations",
            "atomic generations",
            "deterministic commit outcomes",
            "no candidate selection, OOB decision, socket, pairing policy, or runtime transition",
            "one candidate slot",
            "same-UID peer authentication",
            "Default transport is AF_UNIX only",
            "no loopback fallback",
            "outside `StateRoot`",
            "unknown entries and socket objects",
            "`auto-accept` remains `false`",
            "`RegisterRemoteSKI` only after durable confirmation",
            "read-only",
            "no public mutation operation or candidate detail",
        )
        for phrase in required:
            self.assertIn(phrase, normalized)

    def test_confirmation_binding_and_state_machine_are_closed(self) -> None:
        _, body = read_markdown(CANDIDATE)
        normalized = " ".join(body.split())
        state_rows = table_rows(body, "## Coordinator State Machine")
        state_graph = {
            code_value(row["State"]): state_values(row["Allowed next state"])
            for row in state_rows
        }
        self.assertEqual(
            state_graph,
            {
                "DISABLED": {"PAIRING_CLOSED"},
                "PAIRING_CLOSED": {"OPEN_EMPTY"},
                "OPEN_EMPTY": {"CANDIDATE_PENDING", "PAIRING_CLOSED"},
                "CANDIDATE_PENDING": {
                    "COMMITTING",
                    "OPEN_EMPTY",
                    "PAIRING_CLOSED",
                },
                "COMMITTING": {"PAIRING_CLOSED", "DISABLED"},
            },
        )
        required = (
            "`fingerprint_v1` is the normalized, full 40-character lowercase hexadecimal encoding",
            "bytes in `remote_ski`",
            "`ServiceShipIDUpdate`",
            "`observed_remote_ship_id`",
            "same `remote_ski` and `connection_generation`",
            "`association_incomplete`",
            "candidate pending with no store write",
            "MUST NOT invent",
            "persists `remote_ski` and `observed_remote_ship_id` together",
            "exact constant-time comparison",
            "random candidate nonce",
            "idempotency key",
            "connection generation",
            "expiry",
            "starting store generation",
            "explicit confirmation of that exact candidate",
            "does not prove that a human used an independent OOB channel",
            "certificate-leaf SHA-256",
            "requires a redesigned confirmation contract",
            "First linearized eligible event wins",
            "`candidate_busy`",
            "Close the pairing window before beginning one commit",
        )
        for phrase in required:
            self.assertIn(phrase, normalized)

    def test_privileged_candidate_read_is_local_sensitive_and_not_public(self) -> None:
        _, body = read_markdown(CANDIDATE)
        section = body.split("### Privileged Candidate Read", 1)[1].split(
            "\n### ", 1
        )[0]
        normalized = " ".join(section.split())
        required = (
            "same-UID authenticated AF_UNIX",
            "`fingerprint_v1`",
            "`candidate_nonce`",
            "`expires_at`",
            "`connection_generation`",
            "`starting_store_generation`",
            "sensitive local-only response",
            "MUST NOT be logged, metriced, traced, captured, persisted, or shared",
            "does not return `observed_remote_ship_id`",
            "Public `Runtime`, MCP, GraphQL, Portal, and Home Assistant surfaces remain candidate-free",
        )
        for phrase in required:
            self.assertIn(phrase, normalized)

    def test_terminal_idempotency_cache_is_bounded_and_restart_volatile(self) -> None:
        _, body = read_markdown(CANDIDATE)
        normalized = " ".join(body.split())
        required = (
            "bounded volatile terminal-result cache",
            "bounded replay TTL",
            "never beyond the current process lifetime",
            "identical replay returns the cached stable result",
            "cannot produce a second commit",
            "cancelled or expired candidate returns its cached no-write result",
            "cannot resurrect the candidate",
            "Restart discards",
            "terminal-result cache",
        )
        for phrase in required:
            self.assertIn(phrase, normalized)

    def test_waiting_permission_is_bounded_liveness_not_approval(self) -> None:
        _, body = read_markdown(CANDIDATE)
        section = body.split("## Waiting Permission And Commit Ordering", 1)[1].split(
            "\n## ", 1
        )[0]
        normalized = " ".join(section.split())
        required = (
            "`UserIsAbleToApproveOrCancelPairingRequests` controls the global `AllowWaitingForTrust` permission",
            "does not approve a peer",
            "logically closes the pairing window before Commit",
            "admits no new candidate",
            "`auto-accept` remains `false`",
            "every competing peer is cancelled",
            "may keep `AllowWaitingForTrust` `true` only through the bounded `COMMITTING` interval for the winner",
            "set `false` before or atomically with the terminal effect",
            "Only `RegisterRemoteSKI` after `commit_durable` actually approves",
            "commit-wait bound",
            "no `RegisterRemoteSKI`",
            "trust outcome unknown",
            "reopen required",
        )
        for phrase in required:
            self.assertIn(phrase, normalized)

    def test_failures_races_restart_and_store_outcomes_fail_closed(self) -> None:
        _, body = read_markdown(CANDIDATE)
        normalized = " ".join(body.split())
        self.assertEqual(
            table_first_column(body, "## Store Commit Outcome Mapping"),
            {
                "commit_durable",
                "commit_not_published",
                "validation/provider failure",
                "commit_applied_maintenance_failed",
                "commit_durability_unknown",
            },
        )
        required = (
            "Wrong fingerprint, stale nonce, stale connection generation, stale store generation, or idempotency conflict",
            "store unchanged and the candidate intact",
            "Cancel or expiry clears the candidate",
            "Only `commit_durable`",
            "trusted and invoke `RegisterRemoteSKI`",
            "race losers and a peer arriving after window closure",
            "cancelled",
            "mutation is disabled",
            "reopen is required",
            "trust outcome is unknown",
            "Restart discards the volatile window, candidate, nonce, active idempotency state, and terminal-result cache",
            "durable remote association alone reloads trust",
        )
        for phrase in required:
            self.assertIn(phrase, normalized)

    def test_gate_matrix_and_adversarial_cases_are_falsifiable(self) -> None:
        _, body = read_markdown(CANDIDATE)
        gate_section = body.split("## Falsifiable Gate Matrix", 1)[1].split(
            "\n## ", 1
        )[0]
        self.assertEqual(
            table_first_column(body, "## Falsifiable Gate Matrix"),
            {"G02", "G03", "G04", "G16"},
        )
        rows: dict[str, str] = {}
        for gate in ("G02", "G03", "G04", "G16"):
            row = next(
                line
                for line in gate_section.splitlines()
                if line.startswith(f"| `{gate}`")
            )
            rows[gate] = row
            self.assertGreaterEqual(row.count("|"), 4)
            self.assertIn("Falsified", row)

        locked_meanings = {
            "G02": (
                "pairing is closed",
                "unknown peer is refused",
                "zero store writes",
            ),
            "G03": (
                "window is open",
                "exactly one ephemeral RAM candidate",
                "no persistent write before exact OOB confirmation",
            ),
            "G04": (
                "Two racing peers",
                "one candidate",
                "one deterministic `candidate_busy` denial",
                "wrong fingerprint leaves the store unchanged",
            ),
        }
        for gate, phrases in locked_meanings.items():
            for phrase in phrases:
                self.assertIn(phrase, rows[gate])

        normalized_gate_section = " ".join(gate_section.split())
        self.assertIn(
            "Store-boundary and AF_UNIX proofs remain separate required tests",
            normalized_gate_section,
        )
        self.assertIn(
            "are not substitutes for the locked gate meanings",
            normalized_gate_section,
        )

        normalized = " ".join(body.split())
        required = (
            "wrong UID",
            "symlink",
            "substitution",
            "stale socket",
            "malformed",
            "oversized",
            "replayed request",
            "confirm-versus-cancel",
            "confirm-versus-expiry",
            "every store commit outcome",
            "restart",
            "frozen public API",
        )
        for phrase in required:
            self.assertIn(phrase, normalized)

    def test_g16_public_artifacts_allow_only_ephemeral_safe_fields(self) -> None:
        _, body = read_markdown(CANDIDATE)
        privacy = body.split("### G16 Public Artifact Contract", 1)[1].split(
            "\n## ", 1
        )[0]
        normalized = " ".join(privacy.split())
        self.assertIn("random per-run labels, outcomes, and counts only", normalized)
        self.assertIn("shareable artifacts", normalized)
        forbidden_categories = (
            "raw or encoded SKI",
            "fingerprint",
            "PEM",
            "key",
            "token",
            "SHIP ID",
            "IP address",
            "MAC address",
            "serial",
            "local identity",
            "stable peer digest",
            "history",
        )
        for category in forbidden_categories:
            self.assertIn(category, normalized)

    def test_msp04a_keeps_pairing_policy_outside_the_store(self) -> None:
        metadata, body = read_markdown(STORE_CANDIDATE)
        normalized = " ".join(body.split())
        self.assertEqual(metadata["publication_status"], "candidate")
        self.assertEqual(metadata["stable_navigation"], "false")
        self.assertNotIn("pre-implementation architecture contract", normalized)
        self.assertNotIn(
            "do not claim that the store, schema, migrations, or recovery behavior have landed",
            normalized,
        )
        self.assertIn("implementation merged in `helianthus-eebusreg`", normalized)
        self.assertIn(MSP04A_IMPLEMENTATION_COMMIT, normalized)
        self.assertIn("remains candidate and non-stable", normalized)
        self.assertIn("does not itself promote support", normalized)
        self.assertNotIn("A merged MSP-04A implementation", metadata["falsifier"])
        self.assertNotIn(
            "Later milestones may add policy only through an explicit schema version",
            normalized,
        )
        self.assertIn("MSP-04B private trust coordinator", normalized)
        self.assertIn("store schema remains policy-free", normalized)


if __name__ == "__main__":
    unittest.main()
