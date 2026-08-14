from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARCH = ROOT / "architecture/_candidate/post-m9-operator-pairing-browsers-v1.md"
API = ROOT / "api/_candidate/post-m9-operator-admin-v1.md"


def normalized(path: Path) -> str:
    return " ".join(path.read_text(encoding="utf-8").split())


class OperatorAdminV1BoundaryContractTest(unittest.TestCase):
    def test_runtime_stays_candidate_free_and_capability_is_creation_only(self) -> None:
        text = normalized(ARCH)
        for phrase in (
            "`NewOperatorRuntimeV1(Config) (Runtime, AdminV1, error)`",
            "Existing `New(Config)` callers continue to receive only the candidate-free public `Runtime`",
            "there is no exported accessor that accepts an existing runtime",
            "does not implement `AdminV1` or any exported admin-provider interface",
            "cannot recover the capability through a helper call or type assertion",
            "ordinary `Runtime.Snapshot`, `Runtime.PairingState`, raw MCP, GraphQL, Home Assistant",
            "cannot reach or serialize `AdminV1`",
        ):
            self.assertIn(phrase, text)
        self.assertNotIn("OperatorAdminV1(Runtime)", text)

    def test_every_mutation_has_closed_idempotency_and_revision_preconditions(self) -> None:
        text = normalized(API)
        for phrase in (
            "`MutationPreconditionV1`",
            "`idempotency_key` | string | 1..128 UTF-8 bytes",
            "`expected_state_revision` | unsigned integer | non-zero",
            "replay lookup precedes revision comparison",
            "same logical terminal result with `replayed=true`",
            "changed operation, handle, revision, or argument binding returns `idempotency_conflict`",
            "does not execute a second effect",
        ):
            self.assertIn(phrase, text)

    def test_select_connect_cancel_retry_and_untrust_are_distinct(self) -> None:
        text = normalized(API)
        for phrase in (
            "observation handle and the complete expected SKI",
            "returns a selection handle without dialing or trusting",
            "connect consumes only that selection handle",
            "POST /admin/eebus/v1/selections/{selection_id}:connect",
            "select response returns one opaque `selection_id`",
            "maps only to the returned in-process selection handle",
            "same authenticated Portal session and principal",
            "POST /admin/eebus/v1/candidate:cancel",
            "retry accepts only a partner handle and never an endpoint",
            "untrust resolves association, manifest, control, and store bindings internally",
        ):
            self.assertIn(phrase, text)
        self.assertNotIn(
            "POST /admin/eebus/v1/observations/{observation_id}:connect", text
        )

    def test_handles_and_admin_revision_are_bounded_and_non_serializable(self) -> None:
        text = normalized(ARCH) + " " + normalized(API)
        for phrase in (
            "four distinct opaque handle kinds",
            "two minutes",
            "128 live handles per kind",
            "512 live handles in total",
            "never evicts a still-valid handle",
            "invalidated on every admin revision change",
            "revision starts at 1",
            "must fail closed before unsigned 64-bit wrap",
            "generic JSON, text, formatting, logging, metrics, diagnostics, and shareable evidence",
        ):
            self.assertIn(phrase, text)

    def test_candidate_cancel_authorization_is_closed(self) -> None:
        text = normalized(API)
        self.assertIn("| Cancel current candidate | allow | deny |", text)


if __name__ == "__main__":
    unittest.main()
