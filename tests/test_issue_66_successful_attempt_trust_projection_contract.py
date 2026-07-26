from __future__ import annotations

import hashlib
import re
import unittest
from pathlib import Path
from unittest.mock import patch


REPO = Path(__file__).resolve().parents[1]
STABLE_PROTOCOL = REPO / "protocols/ship-spine-overview.md"
ATTEMPT_ARCHITECTURE = (
    REPO / "architecture/_candidate/msp-052-outbound-pairing-contract.md"
)
TRUST_ARCHITECTURE = (
    REPO / "architecture/_candidate/msp-045-trust-admin-projection.md"
)
API_BOUNDARY = REPO / "api/_candidate/msp-052-outbound-pairing-api.md"
SECTION_PATTERN = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)


def section(text: str, heading: str) -> str:
    matches = list(SECTION_PATTERN.finditer(text))
    for index, match in enumerate(matches):
        if match.group(1).casefold() != heading.casefold():
            continue
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        return text[start:end]
    raise AssertionError(f"missing section: {heading}")


def normalized(text: str) -> str:
    return " ".join(text.split())


def table_rows(text: str) -> list[dict[str, str]]:
    lines = text.splitlines()
    start = next(index for index, line in enumerate(lines) if line.startswith("|"))

    def cells(line: str) -> list[str]:
        return [
            cell.replace(r"\|", "|").strip()
            for cell in re.split(r"(?<!\\)\|", line.strip("|"))
        ]

    headers = cells(lines[start])
    separator = cells(lines[start + 1])
    if len(headers) != len(separator) or not all(
        re.fullmatch(r":?-{3,}:?", cell) for cell in separator
    ):
        raise AssertionError("section does not start with a valid Markdown table")

    rows: list[dict[str, str]] = []
    for line in lines[start + 2 :]:
        if not line.startswith("|"):
            break
        values = cells(line)
        if len(values) != len(headers):
            raise AssertionError(f"malformed Markdown table row: {line}")
        rows.append(dict(zip(headers, values, strict=True)))
    return rows


class Issue66SuccessfulAttemptTrustProjectionTests(unittest.TestCase):
    def test_stable_protocol_remains_byte_identical(self) -> None:
        self.assertEqual(
            hashlib.sha256(STABLE_PROTOCOL.read_bytes()).hexdigest(),
            "734c5668cd1937b088cbb12c7c4dd6b78c0fc76cc76873dc2d49092aded65b3b",
        )

    def test_success_linearization_and_later_close_are_distinct_and_ordered(self) -> None:
        body = section(
            ATTEMPT_ARCHITECTURE.read_text(encoding="utf-8"),
            "Successful Attempt And Session Close",
        )
        compact = normalized(body)
        ordered = (
            "acceptance of `SmeStateComplete` for the exact authorized outbound attempt",
            "publishes `ConnectionStateCompleted` first",
            "resnapshots the latest control/store generation",
            "durably retire the exact authorized attempt reservation",
            "reset that attempt's retry/backoff state",
        )
        positions = [compact.index(marker) for marker in ordered]
        self.assertEqual(positions, sorted(positions))
        for required in (
            "`SmeStateComplete` closes the attempt, not the live connection or session",
            "success handler MUST NOT invoke attempt cancellation",
            "The connection owner retains that context while the connection remains live",
            "one bounded volatile post-success marker",
            "At most one marker exists per live connection",
            "cannot exceed the existing bound on live outbound connection owners",
            "Duplicate or stale callbacks cannot allocate a marker",
            "After SHIP has disabled its close `context.AfterFunc`",
            "cancels the live permit context once",
            "performs the ordinary exact MSP-04B candidate-terminal handoff",
            "publishes disconnect once",
            "neither recreates nor fails the retired attempt",
            "Neither ordering may mutate a newer attempt generation",
        ):
            self.assertIn(required, compact)

    def test_success_lease_close_and_stale_falsifiers_are_exact(self) -> None:
        body = section(
            ATTEMPT_ARCHITECTURE.read_text(encoding="utf-8"),
            "Successful Attempt Falsifiers",
        )
        rows: list[tuple[str, str, str]] = []
        seen_ids: set[str] = set()
        for row in table_rows(body):
            raw_id = row["Falsifier"]
            self.assertRegex(raw_id, r"^`A66-[A-Z-]+`$")
            falsifier_id = raw_id[1:-1]
            self.assertNotIn(falsifier_id, seen_ids)
            seen_ids.add(falsifier_id)
            rows.append(
                (
                    falsifier_id,
                    row["Required result"],
                    row["Contract is falsified if"],
                )
            )

        self.assertEqual(
            rows,
            [
                (
                    "A66-SUCCESS-BEFORE-LEASE",
                    "Exact `SmeStateComplete` publishes `ConnectionStateCompleted`, "
                    "then durably removes the exact reservation and resets retry "
                    "state while the live context remains uncancelled. Advancing "
                    "beyond the retired lease has no effect.",
                    "The attempt remains authorized or durable, retry is charged, "
                    "the live context is cancelled, ordering differs, or the old "
                    "lease mutates any state.",
                ),
                (
                    "A66-LEASE-BEFORE-SUCCESS",
                    "Exact lease expiry settles failure once; later "
                    "`SmeStateComplete` and duplicate error/lease callbacks are "
                    "stale no-ops.",
                    "Completion resurrects or succeeds the expired attempt, a "
                    "terminal effect repeats, or a newer generation changes.",
                ),
                (
                    "A66-HANDOFF-GENERATION",
                    "A synchronous `ConnectionStateCompleted` handoff advances "
                    "durable trust/control generation; post-publication resnapshot "
                    "retires only the exact successful reservation on that latest "
                    "generation and preserves the trust commit.",
                    "Retirement uses a pre-publication snapshot, conflicts with or "
                    "overwrites the trust commit, leaves the exact attempt "
                    "authorized, or charges retry.",
                ),
                (
                    "A66-RETIREMENT-DURABILITY",
                    "Known-unapplied retirement is retried from a fresh snapshot; "
                    "ambiguous retirement enters `DURABILITY_UNKNOWN`, blocks "
                    "launch/retry, preserves the live context and newer trust, and "
                    "reconciles the exact attempt only as success.",
                    "An unproven retirement reports normal settlement, enables "
                    "another launch, charges failure, cancels the live context, or "
                    "overwrites newer trust.",
                ),
                (
                    "A66-CLOSE-AFTER-SUCCESS",
                    "Exact later close consumes one bounded post-success marker "
                    "after the SHIP close `context.AfterFunc` is disabled, cancels "
                    "the live permit once, performs exact candidate-terminal "
                    "cleanup, and publishes one disconnect without retry or "
                    "durable-trust mutation.",
                    "Success closes the session, close is lost, cleanup or "
                    "disconnect repeats, retry increments, or the durable "
                    "association degrades.",
                ),
                (
                    "A66-PRECONF-CLOSE-AFTER-SUCCESS",
                    "Pre-confirm completion retires the attempt; if exact OOB later "
                    "activates transient trust but close wins before durable "
                    "commit, marker consumption clears the candidate/latches and "
                    "invokes one matching `UnregisterRemoteSKI`.",
                    "Transient trust or a candidate latch survives close, "
                    "unregister repeats, the retired attempt is failed, or durable "
                    "state changes.",
                ),
                (
                    "A66-STALE-GENERATION",
                    "Duplicate, stale, error, lease, and close callbacks for the "
                    "retired attempt cannot mutate a newer attempt or connection "
                    "generation.",
                    "Any stale callback cancels, retires, resets, charges, "
                    "publishes for, or otherwise changes a newer generation.",
                ),
            ],
        )

    def test_reversed_retirement_durability_falsifier_is_rejected(self) -> None:
        original_read_text = Path.read_text
        architecture = original_read_text(ATTEMPT_ARCHITECTURE, encoding="utf-8")
        mutated = architecture.replace(
            "preserves the live context and newer trust, and reconciles the "
            "exact attempt only as success.",
            "cancels the live context and overwrites newer trust, and reconciles "
            "the exact attempt as failure.",
            1,
        )
        self.assertNotEqual(mutated, architecture)

        def read_text(path: Path, *args, **kwargs) -> str:
            if path == ATTEMPT_ARCHITECTURE:
                return mutated
            return original_read_text(path, *args, **kwargs)

        with patch.object(Path, "read_text", read_text), self.assertRaises(
            AssertionError
        ):
            self.test_success_lease_close_and_stale_falsifiers_are_exact()

    def test_retry_projection_preserves_trust_only_for_usable_association(self) -> None:
        text = TRUST_ARCHITECTURE.read_text(encoding="utf-8")
        precedence = section(text, "Closed Projection Precedence")
        compact = normalized(precedence)
        self.assertIn(
            "`no-row-1-through-3-condition+usable-current-lineage-durable-association+(retry-control=IDLE\\|BACKOFF_ACTIVE\\|RETRY_READY)` | `paired` | `true`",
            compact,
        )
        self.assertIn(
            "`no-row-1-through-3-condition+(UNPAIRED_LOCKED\\|PAIRING_CLOSED\\|OPEN_EMPTY\\|association_incomplete\\|CANDIDATE_PENDING\\|COMMITTING-before-store-and-anchor-durable\\|BACKOFF_ACTIVE-without-usable-durable-association\\|RETRY_READY-without-usable-durable-association)` | `unpaired` | `false`",
            compact,
        )
        self.assertIn(
            "`REVOKED\\|TOMBSTONED\\|ADMIN_HOLD\\|terminal_security_quarantine` | `denied` | `false` | `denied-trust`",
            compact,
        )
        self.assertNotIn(
            "`ADMIN_HOLD\\|BACKOFF_ACTIVE` | `denied`",
            compact,
        )
        self.assertIn(
            "classifies a recognized persistent quarantine reason as exactly one of `terminal_security_quarantine` or `retry_control_quarantine`",
            normalized(section(text, "Combined State Product")),
        )

        cross_product = normalized(section(text, "Retry And Trust Cross-Product"))
        for required in (
            "`none` | `yes` | `BACKOFF_ACTIVE` | `paired+paired_true`",
            "`none` | `yes` | `RETRY_READY` | `paired+paired_true`",
            "`none` | `no` | `IDLE\\|BACKOFF_ACTIVE\\|RETRY_READY` | `unpaired+paired_false`",
            "`terminal_denial` | `either` | `IDLE\\|BACKOFF_ACTIVE\\|RETRY_READY` | `denied+paired_false`",
        ):
            self.assertIn(required, cross_product)

        falsifiers = section(text, "Retry-State Trust Falsifiers")
        for falsifier in (
            "A66-RETRY-USABLE",
            "A66-RETRY-ABSENT",
            "A66-RETRY-FAIL-CLOSED",
        ):
            self.assertEqual(falsifiers.count(f"`{falsifier}`"), 1)
        self.assertIn(
            "Structural uncertainty wins first",
            normalized(falsifiers),
        )

    def test_experimental_candidate_symbols_and_success_marker_remain_internal(self) -> None:
        text = API_BOUNDARY.read_text(encoding="utf-8")
        compact = normalized(text)
        for required in (
            "`PairingCandidateQueuer` and `CandidateRef` are private experimental process-local dependency capabilities only",
            "does not promote `candidate_ref` into stable `helianthus-eebusreg` state",
            "Exact outbound `SmeStateComplete` is an internal dependency callback",
            "add no declaration or field to stable eebusreg, MCP, GraphQL, `Runtime`, `Snapshot`, or `PairingState`",
        ):
            self.assertIn(required, compact)

        stable_surfaces = (
            REPO / "api/eebusruntime-v1/reference.md",
            REPO / "api/eebusruntime-v1/manifest.json",
            REPO / "api/api-surface-v1.md",
            REPO / "api/_candidate/msp-06-eebus-mcp-v1.md",
            REPO / "api/_candidate/msp-06/helianthus.eebus.mcp.v1.schema.json",
        )
        forbidden = ("candidate_ref", "PairingCandidateQueuer", "CandidateRef")
        for path in stable_surfaces:
            payload = path.read_text(encoding="utf-8")
            for symbol in forbidden:
                with self.subTest(path=path, symbol=symbol):
                    self.assertNotIn(symbol, payload)


if __name__ == "__main__":
    unittest.main()
