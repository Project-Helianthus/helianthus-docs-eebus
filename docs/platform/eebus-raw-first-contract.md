# eeBUS Raw-First Platform Contract

Canonical source: this page.

Plan provenance:
`helianthus-execution-plans/multi-runtime-semantic-platform.draft`.

## Scope

eeBUS enters Helianthus as raw SHIP/SPINE runtime visibility first. The first
target is VR940f/myVaillant inspection through read-only MCP. GraphQL, Portal,
Home Assistant, command routing, raw writes, and promoted semantics wait for
per-leaf promotion gates.

## Required Order

1. Control-plane issue matrix and `eebus-transport-gate v0`.
2. Platform ownership ADR and eeBUS docs bootstrap.
3. `helianthus-eebusreg` raw runtime/evidence repo bootstrap with no runtime
   contracts, no listeners, no trust store, and no `enbility` dependency.
4. Raw identity, snapshot, evidence, and correlation drafts.
5. `enbility/eebus-go v0.7.0` feasibility proof behind internal facades.
6. Home Assistant add-on networking proof for listener scope, mDNS, manual
   endpoint fallback, and disposable proof credential persistence.
7. Black-box fake-peer and live VR940f interop smoke.
8. Production trust and first-trust hardening.
9. Disabled-by-default gateway sidecar.
10. Read-only `eebus_v1_*` MCP.
11. Evidence recorder and draft candidate facts.
12. Coexistence proof and per-leaf promotion lock.
13. GraphQL, Portal, and HA only for promoted leaves.

## Stable MCP Rules

Stable eeBUS MCP tools are read-only. Snapshot refs bind to runtime, contract,
tool or scope, mask tier, and effective auth scope. Dereference requires an
exact binding match and never re-masks the same captured ref at read time.

Hash material uses RFC 8785 JSON canonicalization. Hashes are comparable only
for identical tool id, schema version, mask tier, auth scope, and snapshot
scope.

## Promotion Rule

M7 candidate facts do not promote leaves. M8 proves coexistence. M8.5 locks
individual leaf promotions with a dossier containing source identity,
comparator results, coexistence evidence, replay regeneration, terminal
negative-state handling, and redacted hashes.

The canonical correlation and dossier contract is
[`raw-correlation-and-leaf-promotion.md`](https://github.com/Project-Helianthus/helianthus-docs/blob/main/docs/platform/raw-correlation-and-leaf-promotion.md).

The canonical Home Assistant runtime networking proof gate is
[`eebus-ha-network-proof.md`](./eebus-ha-network-proof.md).

The canonical fake-peer and live VR940f smoke gate is
[`eebus-interop-smoke.md`](./eebus-interop-smoke.md).

The M3.5 raw identity, snapshot-envelope, and evidence-object freeze is
[`eebus-raw-runtime-freeze.md`](./eebus-raw-runtime-freeze.md).
