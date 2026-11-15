---
canonical_source: "Project-Helianthus/helianthus-docs-eebus:architecture/_candidate/native-snapshot-v2.md"
owner_domain: "architecture"
license: "AGPL-3.0-only"
publication_status: "candidate"
claim_status: "evidence-backed"
source_class: "derived_inference"
evidence_ids: "EV-20260711-001"
hypothesis_status: "draft"
falsifier: "The public library declarations or validation rules of the native snapshot differ from this page."
stable_navigation: "false"
search: "false"
sitemap: "false"
versioned_bundle: "false"
release_bundle: "false"
---

# Candidate eeBUS Native SPINE Snapshot V2

This page describes the topology part of `NativeSnapshotV2` in the public
[eeBUS library](https://github.com/Project-Helianthus/helianthus-eebusreg/tree/main):
its node kinds, the containment relations between them and the rule that
validates them, the bounded absence records, and the identity basis of each
node kind. Field names are the library's Go names followed by their JSON keys.
The source file is
[native_snapshot_v2.go](https://github.com/Project-Helianthus/helianthus-eebusreg/blob/main/native_snapshot_v2.go).

This page is a candidate. It is excluded from stable navigation, search, the
sitemap and every bundle. Promotion into the stable channel is a later step of
the repository's publication procedure.

The page describes code, not new native evidence. It makes no device
qualification claim, grants no mutation authority and promotes nothing to a
semantic model. The snapshot keeps native text as reported, and it does not
redact SKIs, SHIP IDs or addresses. A consumer therefore reads it only
behind an authorization boundary that admits those identities.

## Native relations, not common-graph relations

Every relation on this page is a native SPINE relation between the
snapshot's own nodes. It is not a relation of the common semantic graph. The
common semantic contract in docs-semantic owns cross-protocol relations;
promotion into it is a separate step that selects what is promoted. Nothing on
this page creates, implies or replaces a common-graph relation.

## Node kinds

The snapshot carries four node lists. `Validate` requires each address and
name to be non-blank and at most 4096 bytes after trimming. Each type, role
and actor label may be at most 128 bytes.

| Node kind | Go type | JSON list | Node key | Required reported text |
| --- | --- | --- | --- | --- |
| device | `NativeDeviceV2` | `devices` | `Address` (`address`) | `SKI` (`ski`), `Address`, `Type` (`type`) |
| entity | `NativeEntityV2` | `entities` | `DeviceAddress` (`device_address`) and `EntityAddress` (`entity_address`) | both addresses and `Type` (`type`) |
| feature | `NativeFeatureV2` | `features` | `DeviceAddress`, `EntityAddress` and `FeatureAddress` (`feature_address`) | the three addresses, `Type` (`type`) and `Role` (`role`) |
| use-case claim | `NativeUseCaseV2` | `use_cases` | scope, `Name`, `Actor`, `Version` and `DocumentSubrevision` | `ContextAddress` (`context_address`), `Name` (`name`) and `Actor` (`actor`) |

`Role` is reported text and is not mapped to a closed role enumeration.
`ContextAddress` is the native address at which the claim was announced and
is kept as reported. A nil optional field means not announced. A nil
`Availability` therefore means unknown, not unavailable.

## Containment relations

Devices, entities, features and use-case claims form one containment graph.
Each relation endpoint names a device address. It may add an entity address
and then a feature address. Each endpoint must resolve to exactly one node of
the same snapshot.

| Relation | Carried by | Endpoint |
| --- | --- | --- |
| entity in device | `NativeEntityV2.DeviceAddress` | the device with that `Address` |
| entity in parent entity | `NativeEntityV2.ParentEntityAddress` (`parent_entity_address`) | another entity of the same device; nil for a top-level entity |
| feature in entity | `NativeFeatureV2.DeviceAddress` and `EntityAddress` | the entity with that address pair |
| claim scope | `NativeUseCaseV2.DeviceAddress` (`device_address`), `EntityAddress` (`entity_address`) and `FeatureAddress` (`feature_address`) | the device; narrowed to the entity when `EntityAddress` is set; narrowed to the feature when `FeatureAddress` is also set |

### Validation rule

`Validate` rejects a snapshot when any of these conditions holds:

- two devices share an `Address`;
- an entity names a device that is not in the snapshot, or two entities share
  a device and entity address pair;
- a parent entity address does not name another entity of the same device, or
  a parent chain does not end because it forms a cycle;
- a feature names an entity that is not in the snapshot, or two features share
  a device, entity and feature address triple;
- a claim scope does not resolve, or a claim sets `FeatureAddress` without
  `EntityAddress`;
- two claims share their scope, `Name`, `Actor`, `Version` and
  `DocumentSubrevision`.

The rule fails closed. A snapshot with an unresolved or ambiguous endpoint is
not admitted, and `NewNativeSnapshotV2` returns no copy of it.

## Absence records

`Absences` (`absences`) lists `NativeAbsence` records for native nodes that
the runtime observed but did not emit. `AbsencesOmitted` (`absences_omitted`)
counts further withheld nodes beyond the list. Absence records are not part of
the containment graph and are not nodes; they never satisfy a relation
endpoint.

| Field | JSON key | Meaning |
| --- | --- | --- |
| `Kind` | `kind` | `device`, `entity`, `feature` or `use_case` |
| `Reason` | `reason` | why the node was withheld |
| `DeviceAddress` | `device_address` | the device address; empty only as described below |
| `EntityAddress` | `entity_address` | the entity address, where known |
| `FeatureAddress` | `feature_address` | the feature address, where known |

| Reason | When |
| --- | --- |
| `missing_address`, `missing_type`, `missing_role`, `missing_name`, `missing_actor` | a required native value was not reported |
| `missing_container` | the enclosing device, entity or claim scope was not emitted |
| `ambiguous_address` | the node's address is not unique |

`DeviceAddress` may be empty only for a device that reported no address. Its
own record then has kind `device` and reason `missing_address`. The records of
the nodes it contained have reason `missing_container`. A set
`EntityAddress` or `FeatureAddress` must be non-blank.

### Bound

The list is deterministic in order and holds at most 1024 records.
`AbsencesOmitted` is nonzero only when the list holds exactly 1024 records.
`Validate` rejects a longer list, a count that does not meet that rule, an
unknown kind or reason, and a blank address. `Clone` returns an empty list,
never null, when the source list is nil.

## Identity basis per node kind

`NativeIdentityBasis` lists the native values on which the identity of a
device, an entity or a feature rests. `NativeDeviceV2` returns it from
`IdentityBasis`, `EntityIdentityBasis` and `FeatureIdentityBasis`.

| Field | JSON key | Meaning |
| --- | --- | --- |
| `Kind` | `kind` | `device`, `entity` or `feature` |
| `Source` | `source` | `ship_id` or `unresolved` |
| `SHIPID` | `ship_id` | the device's SHIP ID when `Source` is `ship_id` |
| `DeviceAddress` | `device_address` | the device's native address when `Source` is `unresolved` |
| `EntityAddress` | `entity_address` | the SPINE entity address path, for an entity or a feature |
| `FeatureAddress` | `feature_address` | the feature address, for a feature |

| Node kind | Identity basis |
| --- | --- |
| device | Source `ship_id` and `SHIPID` when the device reported a non-blank SHIP ID. Otherwise Source `unresolved` and `DeviceAddress`. Exactly one of the two is set. |
| entity | the device basis with its `Source`, plus `EntityAddress` |
| feature | the entity basis plus `FeatureAddress` |

A use-case claim has no identity basis of its own. Within the snapshot it is
unique by its scope and claim fields.

The SKI is a trust record, never identity. Neither an SKI nor a certificate
fingerprint is part of any identity basis, so a basis survives a certificate
replacement.

## Boundaries

- Native relations and absence records stay native evidence. Semantic
  promotion is a separate step that this page does not perform.
- Proven, Hypothesis and Unknown describe evidence, not qualification.
- The contract value, `helianthus.eebus.runtime.native-snapshot.v2`, is
  unchanged. No alias, compatibility shim, dual acceptance or migration step
  is provided.
- The frozen eeBUS runtime API v1 reference and the other candidate pages
  are unchanged.
