from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARCH = ROOT / "architecture/_candidate/post-m9-operator-pairing-browsers-v1.md"
API = ROOT / "api/_candidate/post-m9-operator-admin-v1.md"


def normalized(path: Path) -> str:
    return " ".join(path.read_text(encoding="utf-8").split())


class RetryReadyRecoveryContractTest(unittest.TestCase):
    def test_retry_ready_starts_only_the_recovery_boundary(self) -> None:
        text = normalized(ARCH) + " " + normalized(API)
        for phrase in (
            "`RETRY_READY` / `RETRYABLE_FAILURE`",
            "one usable current-lineage durable association",
            "listener and discovery may start",
            "AdminV1 remains available",
            "does not launch an automatic outbound attempt",
            "does not erase or rewrite durable trust",
        ):
            self.assertIn(phrase, text)

    def test_explicit_retry_is_the_only_outbound_admission(self) -> None:
        text = normalized(ARCH) + " " + normalized(API)
        for phrase in (
            "`AdminV1.RetryTrusted` arms exactly one retry",
            "complete trusted-partner identity",
            "no caller-supplied endpoint",
            "library-owned current discovery observation",
            "automatic mDNS reconnect remains denied",
            "failed synchronous retry releases the volatile admission",
        ):
            self.assertIn(phrase, text)

    def test_generic_trusted_reconnect_rules_exclude_retry_ready(self) -> None:
        architecture = normalized(ARCH)
        for phrase in (
            "Fresh discovery alone does not authorize reconnect in the `RETRY_READY` / `RETRYABLE_FAILURE` product",
            "may reconnect after fresh discovery only when no retry-control admission is required",
        ):
            self.assertIn(phrase, architecture)
        self.assertNotIn(
            "Reconnect uses only the durable identity anchors plus fresh discovery.",
            architecture,
        )
        self.assertNotIn(
            "May reconnect after fresh discovery; does not imply currently connected.",
            architecture,
        )

    def test_every_other_recovery_product_remains_fail_closed(self) -> None:
        text = normalized(ARCH) + " " + normalized(API)
        for state in (
            "`BACKOFF_ACTIVE`",
            "`ADMIN_HOLD`",
            "`REVOKED`",
            "`CORRUPT_STORE`",
            "`NO_LOCAL_IDENTITY`",
            "structural quarantine",
            "terminal security quarantine",
        ):
            self.assertIn(state, text)
        self.assertIn("cannot start transport effects or arm retry", text)


if __name__ == "__main__":
    unittest.main()
