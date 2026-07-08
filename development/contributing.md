# Contributing To Helianthus eeBUS Docs

## Canonical Scope

This repo owns eeBUS-native facts:

- SHIP/SPINE observations;
- eeBUS service graphs;
- VR940f/myVaillant raw evidence;
- device-specific quirks;
- reverse-engineering hypotheses and falsification notes.

Cross-protocol contracts are linked from
`helianthus-docs-ebus/docs/platform/` and are not duplicated here.

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

Invalid example:

```text
This claim was paraphrased from a restricted vendor document.
```

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
