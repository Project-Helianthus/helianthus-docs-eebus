---
canonical_source: "Project-Helianthus/helianthus-docs-eebus:api/_candidate/msp-068-raw-operator-redaction-amendment.md"
owner_domain: "api"
license: "AGPL-3.0-only"
publication_status: "candidate"
claim_status: "evidence-backed"
source_class: "derived_inference"
evidence_ids: "EV-20260711-001"
hypothesis_status: "draft"
falsifier: "An authorized boundary or contract test does not preserve device identity plus useful protocol metadata, entity type/address/description, feature type/role/address/description, or every available use-case field; accepts cross-tier dereference; or exposes cryptographic secret material."
candidate_output: "true"
stable_navigation: "false"
search: "false"
sitemap: "false"
versioned_bundle: "false"
release_bundle: "false"
candidate_output_path: "api/_candidate/msp-068-raw-operator-redaction-amendment.md"
---

# Candidate Issue 68 Raw Operator And Shareable Redaction Amendment

This forward amendment corrects the unpublished initial MCP contract described
by [MSP-06](msp-06-eebus-mcp-v1.md) and the candidate raw snapshot view in this
repository. It defines a candidate contract only; it makes no deployed-runtime,
protocol, pairing, trust, or consumer-availability claim.

## Namespace And Boundary

There is one initial `eebus.v1.*` namespace. This amendment corrects that
unpublished namespace in place: it creates no second namespace, alias, legacy
surface, or separate API version.

An authorized local/operator default is `mask_tier=raw`. It is selected by the
authorization boundary, never by a tool argument, header, query parameter, or
client-supplied principal. A public/shareable export is explicit
`mask_tier=redacted`; it is a separate boundary-selected export of the same
`eebus.v1.*` contract, not a new tool family.

Authorization is enforced fail-closed at the boundary. A request that is not
authorized for the requested boundary receives no raw result. Tool inputs
cannot upgrade, downgrade, or otherwise choose the tier.

## Raw Operator Fields And Opaque Values

The authorized raw view preserves inspectable operational observations without
promoting them into semantic facts:

| Object | Required raw fields |
| --- | --- |
| Device | device fields: identity, useful protocol metadata |
| Entity | entity fields: type, address, description |
| Feature | feature fields: type, role, address, description |
| Use-case claim | use-case fields: name, actor, role, scenario, context, version |

SKI, SHIP ID, SPINE addresses, and protocol metadata are operational data
visible to the authorized local operator, not crypto secrets. Unknown protocol
fields remain inspectable raw or opaque values. They are not silently deleted,
normalized into premature semantics, or inferred from an allowlist.

## Reference And Tier Binding

Reference binding includes runtime, contract, tool, scope, mask_tier, and
auth_scope. A reference is minted only after the boundary selects its effective
authorization and tier. Dereference rejects a mismatched mask_tier or auth_scope
with `permission_denied`; a raw reference cannot be used for a redacted export,
and a redacted reference cannot be used for a raw operator read. The caller
supplies only the opaque token and cannot override any binding component.

## Public Redaction And Secret Exclusion

Public/shareable artifacts redact stable identities. They retain only the
redacted identity form required by the existing redacted export profile and do
not expose stable identifiers as correlators.

Private keys, private PEM material, tokens, trust-store bytes, and cryptographic
secrets are forbidden in every tier. This prohibition applies equally to raw
operator responses, redacted exports, references, logs, errors, evidence, and
fixtures. Raw operational visibility is not permission to disclose credentials
or cryptographic material.

`candidate_ref` is forbidden from the stable public API. Candidate provenance
may remain inside a candidate-only artifact when the repository publication
policy permits it, but cannot become part of a stable public contract.

## Historical Boundary

This is forward-only. It does not modify the historical M2 public API artifacts
or the historical G16 public-artifact contract. It also leaves
`protocols/ship-spine-overview.md` byte-identical. The candidate redacted export
schema remains the profile for explicit public/shareable output; this amendment
defines the additional authorized-local raw boundary of the same initial
`eebus.v1.*` namespace.
