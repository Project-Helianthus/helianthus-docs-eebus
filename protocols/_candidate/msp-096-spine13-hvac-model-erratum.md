---
canonical_source: "Project-Helianthus/helianthus-docs-eebus:protocols/_candidate/msp-096-spine13-hvac-model-erratum.md"
owner_domain: "protocols"
license: "CC0-1.0"
publication_status: "candidate"
claim_status: "evidence-backed"
source_class: "derived_inference"
evidence_ids: "EV-20260730-001,EV-20260730-002"
hypothesis_status: "draft"
falsifier: "A bounded raw READ validation shows that the listed scalar/list, enum/scaled-number, identifier value-type, or description-list assumptions are not accepted by the remote; that an excluded SPINE 1.4, wholesale-merge, or 9970150 key-tag/update-engine change is necessary; or that the retained public baseline differs from 49 declared READ operations, 26 successes, and 23 failures."
stable_navigation: "false"
search: "false"
sitemap: "false"
versioned_bundle: "false"
release_bundle: "false"
---

# Candidate MSP-096: Bounded SPINE 1.3 HVAC Model Erratum

## Status, Evidence, And Boundary

This candidate is tracked by
[docs issue 96](https://github.com/Project-Helianthus/helianthus-docs-eebus/issues/96).
It documents a narrow model correction for the VR940 raw-READ path before a
runtime patch ships. It is not a deployed-runtime claim, a semantic mapping, a
consumer-availability claim, or an independent normative-conformance claim.

The basis is the public upstream implementation record in
[EV-20260730-001](../../evidence/EV-20260730-001.md), together with the
redacted comparison baseline in
[EV-20260730-002](../../evidence/EV-20260730-002.md). Public upstream
implementation evidence can justify this bounded implementation candidate; it
does not independently prove conformance to a normative SPINE specification.

Only SPINE 1.3 model corrections named below are candidates. SPINE 1.4 and a
wholesale upstream-dev merge are outside this patch.
The candidate must not use vendor-restricted specifications. From
`9970150f6d81ffa06605fecddedcdf0e38174543`, only the `MeasurementIdType` and
`TimeTableIdType` identifier value-type correction is admitted; key-tag and
update-engine changes are excluded.

## Affected Setpoint Description Models And Selectors

The candidate applies these public-upstream model shapes:

| Model or selector | Candidate correction | Public provenance |
| --- | --- | --- |
| `SetpointDescriptionDataType` | `unit` is `UnitOfMeasurementType`; `scopeType` is `ScopeTypeType`; `setpointType` is `SetpointTypeType`; `measurementId` is `MeasurementIdType`; `timeTableId` is `TimeTableIdType`. | [`d5f89c767706ef411fc622cd6771c479b7fd1b26`](https://github.com/enbility/spine-go/commit/d5f89c767706ef411fc622cd6771c479b7fd1b26), identifier portion only of [`9970150f6d81ffa06605fecddedcdf0e38174543`](https://github.com/enbility/spine-go/commit/9970150f6d81ffa06605fecddedcdf0e38174543) |
| `SetpointDescriptionListDataSelectorsType` | `setpointId`, `measurementId`, `timeTableId`, `setpointType`, and `scopeType` retain their respective scalar identifier or enum types; they are not substituted scaled numbers or unrelated identifier types. | [`d5f89c767706ef411fc622cd6771c479b7fd1b26`](https://github.com/enbility/spine-go/commit/d5f89c767706ef411fc622cd6771c479b7fd1b26) |

These rows are source-derived implementation corrections, not a transcription
of a vendor specification.

## Affected HVAC Description, Relation, And Selector Models

| Model, selector, or function | Candidate correction | Public provenance |
| --- | --- | --- |
| `FunctionTypeHvacOperationModeDescriptionListData` | The function-data factory selects `HvacOperationModeDescriptionListDataType`, not a single description data type. | [`d5f89c767706ef411fc622cd6771c479b7fd1b26`](https://github.com/enbility/spine-go/commit/d5f89c767706ef411fc622cd6771c479b7fd1b26) |
| `FunctionTypeHvacSystemFunctionDescriptionListData` | The function-data factory selects `HvacSystemFunctionDescriptionListDataType`, not a single description data type. | [`d5f89c767706ef411fc622cd6771c479b7fd1b26`](https://github.com/enbility/spine-go/commit/d5f89c767706ef411fc622cd6771c479b7fd1b26) |
| `HvacSystemFunctionSetpointRelationDataType` | `setpointId` is a list. | [`d5f89c767706ef411fc622cd6771c479b7fd1b26`](https://github.com/enbility/spine-go/commit/d5f89c767706ef411fc622cd6771c479b7fd1b26) |
| `HvacSystemFunctionOperationModeRelationDataType` | `operationModeId` is a list. | [`a6cb0727a1509dd04454c8e8edce899f4111fb3a`](https://github.com/enbility/spine-go/commit/a6cb0727a1509dd04454c8e8edce899f4111fb3a) |
| `HvacSystemFunctionListDataSelectorsType` | `systemFunctionId` is scalar. | [`a6cb0727a1509dd04454c8e8edce899f4111fb3a`](https://github.com/enbility/spine-go/commit/a6cb0727a1509dd04454c8e8edce899f4111fb3a) |
| `HvacSystemFunctionOperationModeRelationListDataSelectorsType` | `systemFunctionId` is scalar; no other hunk from this commit is admitted. | [selector hunk only in `4f986b14324a0d9ed719121b82c2621d50f58303`](https://github.com/enbility/spine-go/commit/4f986b14324a0d9ed719121b82c2621d50f58303) |

## Preserved Baseline And Classification Boundaries

The preserved public baseline is exactly **49 READ declared / 26 success / 23
failure**. It is an aggregate regression reference, not a per-function verdict.

Each attempted READ must be classified exactly once at the raw/operator
boundary before any public summary is emitted:

| Classification | Exact boundary | What it does not establish |
| --- | --- | --- |
| `scalar_vs_list` | A bounded request or reply reaches the affected field and demonstrates scalar-versus-list incompatibility for one listed relation or selector. | A normative requirement, another field's shape, or a general HVAC rule. |
| `enum_vs_scaled_number` | A bounded request or reply reaches `unit`, `scopeType`, or a corresponding selector and demonstrates enum-versus-scaled-number incompatibility. | The semantic meaning or permitted value range of the enum. |
| `identifier_value_type` | A bounded value reaches `measurementId` or `timeTableId` and distinguishes its named identifier type from `SetpointIdType`. | Any 9970150 change other than this identifier value-type portion. |
| `typed_empty` | The function and model decode without a remote error but produce an empty typed list or relation. | Remote acceptance of a non-empty model, feature support, or success for a semantic operation. |
| `remote_rejection` | The remote returns an explicit rejection for the bounded request. | The rejected field or selector is the cause unless independently isolated. |
| `unknown_field` | The remote reports an unknown field or selector, or the raw decoder cannot bind one. | That the field may be deleted, ignored, or generalized from another function. |
| `non_empty_reply_observed` | A bounded non-empty reply is retained and decoded at the raw/operator boundary. | A public payload, semantic promotion, or independent normative conformance. |

No attempt may be recategorized from `remote_rejection`, `unknown_field`, or
`typed_empty` into a model-shape success without a new bounded observation.
`non_empty_reply_observed` is the only classification that can support a
function-specific raw interoperability observation, and it still cannot promote
a canonical semantic claim.

## Falsifiers

The candidate is falsified if any listed scalar/list or enum/scaled-number
correction is rejected in an isolated bounded READ while its prior shape is
accepted; if the named identifier value types cannot be distinguished from the
prior `SetpointIdType`; or if the function-data factory requires a single
description model where this candidate requires its list model.

It is also falsified if a non-empty decoded reply cannot be retained at the
raw/operator boundary, if a typed-empty result is treated as a successful
non-empty reply, if a remote rejection or unknown-field result is silently
reclassified as success, or if a public redacted record reports counts other
than 49 declared READ operations, 26 successes, and 23 failures.

## Operator Raw And Public Redaction

Existing raw/operator versus public-redacted rules remain unchanged. An
owner-authorized raw investigation may preserve the exact model classification,
correlation, and bounded protocol observation under its existing authorization
boundary. Public documentation may publish only redacted aggregate facts such
as the preserved baseline; it must not publish a stable identity, address, raw
request, raw reply, error payload, or topology content.

This candidate creates no MCP, GraphQL, Portal, Home Assistant, or semantic
surface. It neither changes the public-redacted profile nor authorizes a
consumer rollout.
