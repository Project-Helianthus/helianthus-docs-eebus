import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ADMIN = ROOT / "api" / "_candidate" / "post-m9-operator-admin-v1.md"
BROWSER = ROOT / "architecture" / "_candidate" / "post-m9-operator-pairing-browsers-v1.md"


def _normalized(path: Path) -> str:
    return " ".join(path.read_text(encoding="utf-8").split())


def _assert_connect_pin_is_optional_exact_and_secret_bounded() -> None:
    text = _normalized(ADMIN)
    for required in (
        "optional `pin` field",
        "existing selected-candidate `ConnectRequestV1`",
        "Omitting `pin` preserves the existing PIN-free connect flow",
        "exactly 8 through 16 ASCII hexadecimal bytes",
        "does not trim, case-normalize, Unicode-normalize",
        "ephemeral mutable bytes",
        "never persisted, logged, echoed, audited, metriced, traced, diagnosed",
        "MCP, GraphQL, semantic registry, or Home Assistant entity",
        "best-effort clears every buffer it owns",
    ):
        assert required in text


def _assert_connect_pin_replay_is_secret_safe_and_process_local() -> None:
    text = _normalized(ADMIN)
    for required in (
        "process-local keyed HMAC",
        "exact PIN bytes plus presence",
        "only the HMAC",
        "same exact request replays without a second launch or write",
        "different PIN presence or value is `idempotency_conflict`",
        "process restart invalidates every PIN-bearing replay entry",
        "must not enter the generic JSON/canonical-body replay cache",
        "Cache-Control: no-store",
        "no peer timing on POST",
    ):
        assert required in text
    for category in (
        "pin_required",
        "pin_optional",
        "pin_busy",
        "pin_rejected",
        "pin_unavailable",
        "pin_protocol_error",
    ):
        assert category in text


def _assert_pairing_ui_and_durable_lifecycle_remain_separate_from_pin() -> None:
    admin = _normalized(ADMIN)
    browser = _normalized(BROWSER)
    for required in (
        "does not add an arm operation, PIN store, or second connect operation",
        "durable-denial-first",
        "durable tombstone",
        "incomplete withdrawal remains revoked",
    ):
        assert required in admin
    for required in (
        "optional password field",
        "clears it immediately",
        "generic Home Assistant service remains PIN-free",
        "guided native pairing or repair flow",
        "SHIP `.16` -> eebus-go bridge -> eebusreg -> gateway/Portal -> Home Assistant",
    ):
        assert required in browser


def _assert_pin_requirement_is_identity_bound_but_terminal_outcome_is_action_local() -> None:
    admin = _normalized(ADMIN)
    browser = _normalized(BROWSER)
    for text in (admin, browser):
        for required in (
            "identity-bound requirement/baseline",
            "action-local identity-free terminal outcome",
            "pin_required",
            "pin_optional",
            "pin_busy",
            "pin_rejected",
            "pin_unavailable",
            "pin_protocol_error",
        ):
            assert required in text

    partner_rows = admin.split("Each partner row is the closed object:", 1)[1].split(
        "The `remote_ski` field", 1
    )[0]
    for forbidden in (
        "pin_outcome",
        "BUSY",
        "REJECTED",
        "UNAVAILABLE",
        "PROTOCOL",
        "pin_required",
        "pin_optional",
        "pin_busy",
        "pin_rejected",
        "pin_unavailable",
        "pin_protocol_error",
    ):
        assert forbidden not in partner_rows

    for text in (admin, browser):
        assert "must not appear in a partner or candidate row" in text


def _assert_portal_closed_outcomes_table_has_exact_pin_category_parity() -> None:
    text = BROWSER.read_text(encoding="utf-8")
    table = text.split("## Closed Operator Outcomes", 1)[1].split(
        "Unknown future state values", 1
    )[0]
    actual = set(re.findall(r"^\| `(pin_[a-z_]+)` \|", table, flags=re.MULTILINE))
    assert actual == {
        "pin_required",
        "pin_optional",
        "pin_busy",
        "pin_rejected",
        "pin_unavailable",
        "pin_protocol_error",
    }


def _assert_async_connect_action_is_identity_free_and_correlatable() -> None:
    admin = _normalized(ADMIN)
    browser = _normalized(BROWSER)
    for required in (
        "`200 connection_started` includes one opaque `action_id`",
        "same idempotency replay returns the same `action_id` and does not relaunch",
        "GET status returns exactly one bounded identity-free `active_action`",
        "kind`, `state`, `outcome`, `retryable`, and `expiry`",
        "volatile only",
        "clears on terminal observation, expiry, explicit flow abandonment, or process restart",
        "must not include SKI, selection, partner, candidate, endpoint, or PIN",
    ):
        assert required in admin
    for required in (
        "polls `active_action`",
        "correlates only by `action_id`",
        "clears the action state on terminal observation, expiry, abandonment, or restart",
    ):
        assert required in browser


class TransientPinContractTests(unittest.TestCase):
    def test_connect_pin_is_optional_exact_and_secret_bounded(self) -> None:
        _assert_connect_pin_is_optional_exact_and_secret_bounded()

    def test_connect_pin_replay_is_secret_safe_and_process_local(self) -> None:
        _assert_connect_pin_replay_is_secret_safe_and_process_local()

    def test_pairing_ui_and_durable_lifecycle_remain_separate_from_pin(self) -> None:
        _assert_pairing_ui_and_durable_lifecycle_remain_separate_from_pin()

    def test_pin_requirement_is_identity_bound_but_terminal_outcome_is_action_local(
        self,
    ) -> None:
        _assert_pin_requirement_is_identity_bound_but_terminal_outcome_is_action_local()

    def test_portal_closed_outcomes_table_has_exact_pin_category_parity(self) -> None:
        _assert_portal_closed_outcomes_table_has_exact_pin_category_parity()

    def test_async_connect_action_is_identity_free_and_correlatable(self) -> None:
        _assert_async_connect_action_is_identity_free_and_correlatable()
