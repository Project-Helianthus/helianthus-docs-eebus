---
canonical_source: "Project-Helianthus/helianthus-docs-eebus:development/contributing.md"
owner_domain: "development"
license: "AGPL-3.0-only"
---

# Contributing To Helianthus eeBUS Docs

## Canonical Scope

This repo owns eeBUS-native facts and Helianthus eeBUS documentation policy:

- SHIP/SPINE observations;
- eeBUS service graphs;
- VR940f/myVaillant raw evidence;
- device-specific quirks;
- reverse-engineering hypotheses and falsification notes.

Path ownership is exact:

- `protocols/` owns eeBUS/SHIP/SPINE protocol behavior.
- `architecture/` owns Helianthus eeBUS runtime, adapter, trust, persistence,
  and lifecycle architecture.
- `api/` owns eeBUS-specific Go API schema, reference, and examples.
- `devices/`, `evidence/`, and `re-notes/` remain native owners for their
  device, evidence, and reverse-engineering records.
- `helianthus-docs-ebus/docs/platform/` owns only language-neutral
  cross-runtime platform contracts.

Cross-protocol contracts are linked from platform docs and are not duplicated
here. Code repositories are external-only for substantive docs: they may link to
canonical docs, but do not own publishable protocol, architecture, API, or
platform documentation.

Each publishable Markdown page must declare unique `canonical_source` metadata
in front matter. Repository control files such as `AGENTS.md` and GitHub issue
templates are exempt.

The current gateway import remains blocked. Do not document gateway import,
GraphQL parity, HA consumer rollout, or command routing as active behavior until
the later canonical docs and runtime contracts merge.

Historical `helianthus-eebusreg/docs/` pages are noncanonical
migration/adjudication inputs only. MSP-DOCS-E2 decides migration or discard;
MSP-DOCS-CLEAN later deletes the code-repo docs directory and installs the
absence gate.

Cross-seeding to `helianthus-docs-ebus/docs/platform/` is allowed only for
language-neutral cross-runtime contracts and must keep this repo summary-only.

## Provenance Classes

| Source class | Public use |
| --- | --- |
| `observed_runtime` | Publishable after redaction. |
| `derived_inference` | Publishable when tied to publishable evidence and falsifier. |
| `vendor_public` | Publishable with citation and limited quotation. |
| `vendor_restricted` | Quarantined; never public text, issue text, PR text, review text, or ADR rationale. |
| `app_observation` | Publishable after redaction when acquired by the operator. |
| `operator_note` | Context only; never sufficient for a protocol fact. |

## Restricted-Source Quarantine

Restricted material must not appear in public repositories, public issues,
public PR descriptions, public review comments, or public ADR rationale. If a
restricted source influenced investigation, the public record may only say the
claim was independently confirmed from publishable evidence.

Valid shape:

```text
This claim is supported by evidence ids EV-0001 and EV-0002.
```

## Promoted Claim Table

Every promoted claim must have:

| Field | Meaning |
| --- | --- |
| `claim_id` | Stable claim identifier. |
| `claim` | The publishable claim. |
| `canonical_page` | Owning page path. |
| `publishable_evidence_ids` | Evidence ids that support the claim. |
| `non_publishable_inputs_used` | `yes` or `no`; `yes` requires independent publishable confirmation. |
| `publication_status` | `draft`, `publishable`, `blocked`, or `withdrawn`. |

## Redaction Rules

Shareable evidence must remove or mask:

- PEM blocks and keys;
- tokens and account identifiers;
- full fingerprints;
- IP addresses, MAC addresses, and serial numbers;
- local identity and stable peer identifiers;
- pairing history;
- household schedules or occupancy patterns.

## Evidence Review

Evidence pages must state:

- capture date;
- firmware/app/runtime versions when known;
- acquisition method;
- source class;
- redaction mode;
- publication status;
- falsification criteria.
