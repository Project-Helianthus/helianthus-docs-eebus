---
canonical_source: "Project-Helianthus/helianthus-docs-eebus:api/_candidate/eebus-output-binding-contract-v1.md"
owner_domain: "api"
license: "AGPL-3.0-only"
publication_status: "candidate"
claim_status: "evidence-backed"
source_class: "derived_inference"
evidence_ids: "EV-20260711-001"
hypothesis_status: "draft"
falsifier: "A reviewed eeBUS output composes a SPINE entity from an index, or admits an operation because a capability is visible in a lens result, and the owning check accepts that output."
stable_navigation: "false"
search: "false"
sitemap: "false"
versioned_bundle: "false"
release_bundle: "false"
candidate_output: "true"
candidate_output_path: "api/_candidate/eebus-output-binding-contract-v1.md"
---

# Candidate eeBUS output-binding contract v1

## Status and scope

This page is the public candidate for an eeBUS output binding. It names the
input lens, which resources become SPINE entities, which elements become
features, which operations are admitted, how an entity address persists, what
loss is declared, and when a use case's element is explicit absence.

The page is a candidate. It is excluded from stable navigation, search, the
sitemap, versioned bundles and release bundles. It makes no runtime,
deployment, interoperability or device claim, and it performs no live device
action. Nothing here is an eeBUS, SHIP or SPINE specification statement.
Protocol text stays in `protocols/`. This page cites rule identifiers of the
common semantic contract and does not copy that contract's text.

Issue
[helianthus-docs-eebus#179](https://github.com/Project-Helianthus/helianthus-docs-eebus/issues/179).
The graph contract is owned by
[helianthus-docs-semantic#67](https://github.com/Project-Helianthus/helianthus-docs-semantic/issues/67).
This page does not decide that contract. The public text is
[the graph contract](https://github.com/Project-Helianthus/helianthus-docs-semantic/blob/main/api/v1/graph.md).

## Evidence class

Proven. The common semantic contract publishes the rule identifiers cited
below: CUT, ENT, TRV, LRS, SUM, API, PTL, TGT, CID and NTV, together with the
authority identifiers AUT-1 and AUT-3 that LRS-5 checks. `EV-20260711-001` is
the ownership record. It supports the publication boundary only.

Hypothesis. The binding rules in the sections below are this candidate's
application of those identifiers to an eeBUS output. No implementation in this
repository has exercised them.

Unknown. This page does not name native feature types. It does not list the
elements any use case requires. A lens that would carry both equipment
composition and medium `electrical` is not admitted here.

None of these classes is a device qualification.

## Ownership

- docs-semantic owns resources, elements, planes, lenses and the graph rules.
  This page admits no lens, plane, element or relation.
- This repository owns this public candidate.
- The native registry owns entity, feature and use-case records on the inbound
  side. This page does not change those records.
- A later runtime that composes an output consumes this candidate. This page
  does not claim that runtime.

## Input lens

The named input lens is `lens.equipment_composition`.

The target report accounts for what the output does with that one lens
(TGT-1). The retrieval starts at one device resource (ENT-1). The seeded root
kinds of that lens are inverter, battery, battery pack, charging station,
meter and generic equipment. Those names are families. A listing of resources
is discovery, and it is not the entity tree (ENT-2).

The report cites one served cut. Parts of two cuts are not combined into one
output (CUT-1). A partial cut stays partial and is not repaired by invented
entities. An empty lens result is no device and no invented entity (LRS-6).

## Entities

One resource in the lens result is one SPINE entity (CID-1).

Parent and child entities come only from a `contains` instance cited in this
target's own report. The containing resource is the parent. The contained
resource is the child. The cited instance is qualified, coherent, and in a
plane of the named lens (TRV-1, LRS-1, LRS-2, TGT-2). An instance that is not
coherent is not a current edge.

An entity composed from an index is rejected. An index is list position, name
order, or address order. A name and an address are rejected by the same rule
as an index.

A resource the traversal did not reach is not an entity. A frontier stop is
not filled in (TRV-6). A path through the result is not an entity identifier
(TRV-8).

## Features and electrical context

An element becomes a feature when this report cites that element on the
entity's resource (LRS-1, TGT-2).
A feature value key is the resource identifier, the element definition, and the qualifier dimension values.
CID-2 names that key.

Electrical context is medium `electrical` on a cited element, and it is never
taken from a second lens. Medium `electrical` is the energy-flow reading of
the common contract. This target retrieves the named lens only (TGT-1). A
native typed surface does not supply the medium (NTV-1). No thermal quantity
is placed on a resource.

A sum is not an entity and not a feature. This output computes no sum (SUM-1).

## Operations

An operation is admitted only through that resource's own capability. The
capability is that resource's own qualified capability, and the admission
chain is the kernel chain (AUT-3, LRS-5). Admission reads no lens result
(LRS-5, AUT-1).

Visibility of a capability is not admission. An operation admitted from
visibility alone is rejected. A controls relation does not admit an operation
on the controlled resource (AUT-3).

## Identity persistence

The persisted entity address is keyed by the resource identifier alone. The
entity-address key does not contain an address, an ordinal, a cut identifier,
a traversal path, or a plane. It does not contain an asset identifier (CID-1,
CID-2, CID-5, TRV-8).

The same resource identifier keeps the same entity address (CID-3). A
different resource identifier does not reuse that address. Replacing the
stored address for an existing resource identifier is rejected. The address is
an opaque token allocated for that resource identifier. It is not derived from
list position, a name, or an address order.

## Declared loss

A merge of two resources into one entity is declared loss in this target's own
report. Flattening a qualifier dimension, a frontier tail, and a partial cut
are declared loss of the same target (CID-4, TGT-3, TRV-6, CUT-4). A loss
names this target, `eebus-output`. A loss that does not name this target is
rejected. A loss does not decide membership (TGT-5).

The loss kinds are `merged_resources`, `flattened_qualifier`, `frontier` and
`partial_cut`.

## Explicit absence

An element a use case requires, cited as absent in this report, is explicit
absence and not a feature.
Where the report cites neither the element nor an absence, the element stays unknown and is not a feature.
LRS-3 is that rule. Unknown is not written as absence. Absence is not written as a feature. This page does
not invent the missing element.

## Unchanged surfaces

This candidate adds no GraphQL field and no MCP tool (API-1). The existing
semantic reads stay one answer on GraphQL and on MCP (API-2). This output
does not read through the Portal catalog (PTL-5).

The inbound contracts, the MCP wire schemas and the API surface freeze stay as
they are. No alias, compatibility shim or migration step is added. No contract
version is raised.

## Vectors

These rows are the contract's own vectors. `rejected` and `admitted` are the
outcomes of the rules above.

| Case | Given | Outcome |
| --- | --- | --- |
| `entity_from_index` | basis `index`, with the contains flags set | rejected |
| `operation_from_visibility` | capability visible in the lens result, without the resource's own qualified capability | rejected |
| `entity_from_cited_contains` | one qualified coherent in-plane `contains` instance cited in this report | admitted |
| `operation_through_own_capability` | the resource's own qualified capability, with lens visibility ignored | admitted |

## Promotion decision

Decision: **remain candidate**.

The page states the binding before an implementation exists. Source-specific
accuracy stays with the native owner's review. Promotion into a stable channel
is a later step of the publication procedure.
