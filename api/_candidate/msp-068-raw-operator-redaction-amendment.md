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

There is one initial MCP `eebus.v1.*` namespace. This amendment corrects that
unpublished MCP namespace in place: it creates no second namespace, alias,
legacy surface, or separate API version.

An authorized local/operator default is `mask_tier=raw`. It is selected by the
authorization boundary, never by a tool argument, header, query parameter, or
client-supplied principal. A public/shareable export is explicit
`mask_tier=redacted`; it is a separate boundary-selected export of the same
`eebus.v1.*` contract, not a new tool family.

Authorization is enforced fail-closed at the boundary. The existing LAN HTTP
`/mcp` listener is always the explicit redacted boundary. The same nine MCP
tool names are also mounted on the owner-only AF_UNIX socket
`/data/eebus/operator-mcp.sock`, where the default is raw.

The AF_UNIX parent directory is mode `0700` and the socket is mode `0600`.
Where peer credentials are supported, the server proves a same-effective-UID
peer with the platform credential API before provider access. Startup fails
closed if the operator listener, file-mode proof, or required peer-credential
proof is unavailable. SSH or root administration reaches the operator
endpoint only through a bind-mounted socket. No header, query parameter, tool
argument, body field, client principal, or other caller input selects a tier.

## Raw Operator Fields And Opaque Values

The authorized raw view preserves inspectable operational observations without
promoting them into semantic facts:

| Object | Raw profile fields |
| --- | --- |
| Service | service fields: SKI, SHIP ID, kind, visible, paired, name, identifier, brand, type, model |
| Device | device fields: SKI, SHIP ID, address, type, description, metadata when present |
| Entity | entity fields: device address, entity address, type, description |
| Feature | feature fields: device address, entity address, feature address, type, role, description |
| Use-case claim | use-case fields: context address, name, actor, optional resolved role, scenarios, version, availability, document subrevision |

SKI, SHIP ID, SPINE addresses, and protocol metadata are operational data
visible to the authorized local operator, not crypto secrets. A secondary
digest is allowed only as an additional correlator and never replaces the raw
first-party field. Unknown protocol fields remain inspectable raw or opaque
values in bounded objects with exactly `path`, `source`, and `value`. They are
not silently deleted, normalized into premature semantics, or inferred from an
allowlist.

Service kind, visible, and paired are required observed state. Optional when
unavailable: SHIP ID. Device, entity, and feature descriptions are optional;
device metadata is optional. For a use case, context address, name, and actor
are required, while resolved role, scenarios, version, availability, and
document subrevision are optional when unavailable. Omission means unavailable;
a present empty string, array, or object and a present false boolean remain
distinct observed values.

Opaque values may contain scalars or bounded nested JSON arrays/objects.
Maximum depth is 3; each array and object is limited to 32 members; strings are
limited to 4096 UTF-8 bytes; each value is limited to 16384 canonical JCS
bytes; the list is limited to 256 observations and 262144 aggregate canonical
bytes. The recursive structured secret denylist is exactly `private_key`,
`private_pem`, `trust_store_bytes`, `credential_token`, `bearer_token`,
`session_token`, `authentication_token`, and `cryptographic_secret`.

The eebusreg-owned `SnapshotV1` is the secret-free raw source and keeps the
existing `PairingState` API. An eebusreg-owned public-view builder produces a
structurally separate `RedactedSnapshotV1` as the irreversible shareable
projection, with `RedactedServiceV1` retaining exactly ID, kind, visible, and
paired. There is no `RawSnapshotV1`, v2, alias, legacy, or compatibility surface.

Raw services order by SKI, optional SHIP ID, identifier, kind, visible, and
paired. All three service-state fields remain in the boundary-selected canonical
hash projection.

The two connected machine profiles are the
[`helianthus.eebus.mcp.v1.raw.schema.json`](msp-06/helianthus.eebus.mcp.v1.raw.schema.json)
raw operator profile and the existing
[`helianthus.eebus.mcp.v1.schema.json`](msp-06/helianthus.eebus.mcp.v1.schema.json)
redacted public profile.

## Reference And Tier Binding

Reference binding includes runtime, contract, tool, scope, mask_tier, auth_scope,
and authorization boundary. A shared server and store may serve both
transports, but a reference is minted only after the transport boundary selects
its effective authorization and tier. Dereference rejects a mismatched
mask_tier, auth_scope, or authorization boundary with `permission_denied`; a
raw reference cannot be used for a redacted export, and a redacted reference
cannot be used for a raw operator read. The caller supplies only the opaque
reference and cannot override any binding component.

## Public Redaction And Secret Exclusion

Public/shareable artifacts redact stable identities. They retain only the
redacted identity form required by the existing redacted export profile and do
not expose stable identifiers as correlators.

Private keys, private PEM material, trust-store bytes, credential tokens,
bearer tokens, session tokens, authentication tokens, and cryptographic secrets
are forbidden in every tier. This prohibition applies equally to raw operator
responses, redacted exports, logs, errors, evidence, and fixtures.
Server-generated opaque evidence references are allowed only in designated direct
MCP response fields and are never credentials, bearer/session/authentication
tokens, or cryptographic key material. Raw operational visibility is not
permission to disclose credentials or cryptographic material.

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
