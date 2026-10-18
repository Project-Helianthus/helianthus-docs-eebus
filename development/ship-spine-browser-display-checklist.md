---
canonical_source: "Project-Helianthus/helianthus-docs-eebus:development/ship-spine-browser-display-checklist.md"
owner_domain: "development"
license: "AGPL-3.0-only"
publication_status: "candidate"
claim_status: "evidence-backed"
source_class: "derived_inference"
evidence_ids: "EV-20260711-001,EV-20260809-001"
hypothesis_status: "draft"
falsifier: "A checklist case contradicts an owning raw-view contract or treats incomplete, unsupported, stale, or redacted observations as current authority."
stable_navigation: "false"
search: "false"
sitemap: "false"
versioned_bundle: "false"
release_bundle: "false"
---

# Candidate SHIP/SPINE Browser Display Checklist

This is a bounded review and acceptance aid for raw browsing, not evidence of
implemented UI behavior, stable API support, protocol conformance, or live
acceptance. The cases below are proposed synthetic checks. They do not add a
wire envelope, output binding, semantic mapping, pairing workflow, or namespace.
All MCP namespaces remain pre-stable until 1.0; historical `v1` names are not
stability promises. Existing eBUS MCP behavior and MCP/GraphQL parity remain
outside this documentation-only change.

## Owning contracts and review boundary

Read these public native owners before applying a display rule:

| Owner | Checklist boundary |
| --- | --- |
| [SHIP/SPINE overview](../protocols/ship-spine-overview.md#observation-provenance) | Discovery, session callbacks, trust policy, and pairing evidence have separate provenance. Live validation remains pending. |
| Candidate raw snapshot: `api/_candidate/raw-snapshot-view-v1.md`, Boundary and Candidate Field Value Types | Detached observations, optional-value presence, deterministic ordering, and explicit non-authority. |
| Candidate redaction amendment: `api/_candidate/msp-068-raw-operator-redaction-amendment.md`, Raw Operator Fields And Opaque Values | Authorized raw fields, opaque unknowns, missing versus empty values, and boundary-selected redaction. |
| [Candidate browser contract](../architecture/_candidate/post-m9-operator-pairing-browsers-v1.md#spine-browser) | Canonical lazy tree and raw/semantic separation. Its connected-generation replacement section governs refresh and invalidation. |
| Candidate operator API: `api/_candidate/post-m9-operator-admin-v1.md` | Existing typed browser scope, snapshot/cursor lifetime, and fail-closed outcomes; this checklist defines no replacement binding. |
| [Normative source ledger](../protocols/eebus-normative-source-ledger.md#purpose-and-status) | Normative corpus provenance is separate from implementation dependencies and observed peer versions. |

Candidate API owners are cited as paths because repository publication policy
excludes them from clickable development-page navigation. The cited candidate
contracts remain candidates. Their evidence supports
bounded derivation of these review cases, not a claim that a browser or every
peer family already satisfies them. A conflict is a review blocker to resolve
with the owning contract, never permission to invent protocol behavior here.
Refs [documentation issue 153](https://github.com/Project-Helianthus/helianthus-docs-eebus/issues/153)
and [execution-plans issue 92](https://github.com/Project-Helianthus/helianthus-execution-plans/issues/92).
This partial child leaves the parent's implementation and live acceptance open.

## Independent labels

- [ ] Keep observed peer version, local supported decoder/schema revision, and
  normative corpus pin in three independent provenance categories. Distinguish
  SHIP, SPINE, use-case version, and document subrevision where supplied; there
  is no inferred single "eeBUS version". Do not copy a library revision,
  configured decoder, or corpus entry into an absent peer-version value.
- [ ] Missing peer version reads **Unknown**. A present but locally unsupported
  version retains its observed text and reads **unsupported by local decoder**.
  An unresolved corpus revision remains **unresolved**. This checklist selects
  no normative version or supported-revision set.
- [ ] Keep evidence grade (**Proven**, **Hypothesis**, **Unknown**) separate from
  decoder support, semantic qualification, acquisition/freshness, and authority.
  Proven presence proves only that bounded observation; it cannot qualify a
  semantic value. Do not invent a grade when its source supplies none.
- [ ] Preserve discovered, connected, paired, and durable-trust observations
  separately. A raw row, use-case claim, advertised registration window, or
  `paired` flag alone does not prove successful current pairing, durable trust,
  semantic admission, or write authority. Browsing never selects or trusts a
  peer or starts transport.
- [ ] Keep **partial**, **stale**, **redacted**, **unsupported**, and **unavailable**
  explicit wherever applicable, including child rows and exported display
  summaries. One label does not erase another. Redacted means withheld at the
  selected boundary, not absent at the peer; decoding failure is not an empty
  collection.

## Presence, refresh, and rendering

- [ ] Preserve unavailable optional fields separately from observed `""`, `[]`,
  `{}`, and `false`, including use-case availability and scenarios. A missing
  required collection or malformed snapshot is an invalid/unavailable result,
  not a valid empty inventory. A collection not yet fetched by lazy browsing is
  **not loaded**, not known empty. These are display descriptions, not new enums.
- [ ] Preserve canonical raw fields and bounded typed opaque observations.
  Render peer-controlled names, descriptions, versions, and opaque strings as
  inert text, including markup and link-like text. Do not execute markup,
  interpolate templates, auto-navigate, or normalize unknown data into semantics.
  Any bounded visual truncation is explicit and does not rewrite source data.
- [ ] Use the owning contract's ordering and snapshot binding. Replaying a
  fixed snapshot with differently ordered input yields the same tree order.
  Never combine pages from different snapshots, generations, partners, or mask
  tiers. Expired or cross-boundary references fail closed; do not retry through
  a less restrictive tier.
- [ ] An incomplete refresh is not a complete replacement or an authoritative
  removal. Keep the last accepted immutable snapshot separate from pending
  results; where still valid in the same connected generation, it can remain
  explicitly **stale; refresh partial**. Do not splice pending nodes into it or
  mark all retained nodes freshly observed. New valid partial evidence remains
  distinguishable from accepted complete inventory.
- [ ] Apply an accepted complete current-generation graph as exact replacement.
  A complete empty graph clears the tree. A disconnect, current-device removal,
  generation change, or snapshot invalidation clears invalid raw nodes and
  cursors. Never preserve raw topology across these boundaries as last-known-good
  data. Stale-generation callbacks cannot revive it. A connected session without
  matching inventory shows `spine_topology_unavailable`; invalid provider output
  uses the owning boundary's unavailable/error outcome.
- [ ] Semantic last-known-good values retain their own age and provenance under
  their consumer owner; they never refill the raw tree or imply connectivity.
  Keep raw data out of semantic payloads, `ebus.v1`, and unrelated GraphQL fields.
  No display state grants write or retry admission.
- [ ] Respect boundary-selected raw versus redacted views. Secret material is
  forbidden in both; public/shareable output cannot reconstruct hidden raw
  fields from a cache, digest, tooltip, error, or opaque value. Operator-only
  pairing comparison material never becomes a public raw-browser fixture.

## Deterministic synthetic acceptance cases

Use symbolic peers and families only. `peer-a`, `snapshot-a`, `snapshot-b`,
`generation-a`, `generation-b`, and node labels below are test descriptions,
not proposed serialized identifiers or real protocol addresses. Revision
symbols are deliberately not normative version numbers. No private captures,
identities, network coordinates, capture times, or device-specific cardinality
targets are required. Run each case from a fresh fixture and assert the visible
labels, retained/removed nodes, ordering, and absence of side effects.

| Case | Fixed synthetic input or sequence | Required display and rejection evidence |
| --- | --- | --- |
| V1 | Peer version omitted; local decoder revision `decoder-a`; corpus pin unresolved. | Peer **Unknown**, decoder `decoder-a`, corpus **unresolved** remain separate. No guessed version or conformance badge. |
| V2 | Peer reports `peer-revision-x`; fixture decoder explicitly does not support it. | Exact observed text plus **unsupported by local decoder**. Bounded opaque values remain inspectable where permitted; no semantic qualification or fallback version. |
| P1 | Optional description, scenarios, and availability omitted; repeat with `""`, `[]`, and `false` respectively. | First run shows unavailable; second shows observed empty text, empty scenarios, and false availability. False does not become missing or successful support. |
| P2 | First omit a required inventory collection; then supply a valid complete empty collection; separately leave a lazy child scope unfetched. | Invalid/unavailable, observed empty, and not loaded remain three different outcomes. No fabricated zero count for the invalid or unfetched scope. |
| T1 | Description is `<script>throw 1</script>`; opaque string is `[open](javascript:throw(1))`. | Both appear as inert text. No execution, automatic link, navigation, pairing, or transport action. Repeat rendering produces the same text. |
| R1 | Accept complete `snapshot-a` in `generation-a` with nodes `entity-a` and `entity-b`; begin a refresh that yields only `entity-a` before failing. | Last valid snapshot remains explicitly stale/partial while valid; `entity-b` is not inferred removed. Pending evidence is separate; no mixed snapshot or global fresh label. |
| R2 | After R1, accept complete `snapshot-b` in the same generation containing only `entity-a`; repeat with a complete empty graph. | Exact reduced replacement removes `entity-b`; complete empty clears all nodes. An event delta alone cannot trigger either complete replacement. |
| R3 | Accept `snapshot-a`; disconnect; connect `generation-b` without inventory; deliver a delayed `generation-a` callback. | Old tree/cursors are invalidated; current session shows topology unavailable. Delayed callback changes nothing; trust observation can remain separate from connectivity. |
| R4 | Request expired snapshot children, then try a reference from the other mask tier. | Owning boundary's expiry/permission outcome; no stale-tree resurrection, cache fill, or authorization widening. |
| A1 | Discovery-only service with raw use-case claim; separately provide trusted-but-offline state and an unknown future state value. | Discovery is not pairing or connection; offline trust has no browseable current topology; unknown state fails closed. Claim presence grants no semantic or write admission. |
| D1 | Render a boundary-redacted snapshot after an authorized raw view. | Explicit redacted label; no prior raw identity or opaque data leaks into rows, tooltips, errors, or shareable output. |
| O1 | Supply the same complete snapshot twice with reversed input collection order. | Same contract-defined tree order and preserved raw fields, unknowns, and presence distinctions; no derived semantic labels. |

## Recording acceptance

Record each case as pass, fail, or unverified, with the owning contract section
and sanitized outcome. These proposed cases are not executable tests added by
this page. Browser implementation checks must exercise actual rendering and
provider failure paths; a prose-presence assertion alone cannot establish them.
Offline synthetic results establish only those cases. Live pairing, hardware,
normative-corpus verification, output binding, and parent closure require their
own evidence and remain outside this checklist.
