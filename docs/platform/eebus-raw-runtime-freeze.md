# eeBUS Raw Runtime Contract Freeze

Status: frozen V1 architecture and public API contract for MSP-035.

Canonical source: this page.

Implementation provenance:

- repository: `Project-Helianthus/helianthus-eebusreg`;
- issue: [`#18`](https://github.com/Project-Helianthus/helianthus-eebusreg/issues/18);
- code PR: [`#19`](https://github.com/Project-Helianthus/helianthus-eebusreg/pull/19);
- required code commit:
  [`f0ed9ad277a469b5a64cd975f8ab2473d2d1c36a`](https://github.com/Project-Helianthus/helianthus-eebusreg/commit/f0ed9ad277a469b5a64cd975f8ab2473d2d1c36a).

The field, enum, ordering, hashing, redaction, and boundary rules below are
normative for that exact code revision. A later change to any frozen item
requires a coordinated implementation and canonical-documentation change.

## Freeze Boundary And Versions

MSP-035 freezes two stable public roots and every type in their transitive
public closure:

| Package | Stable root | Contract identifier |
|---|---|---|
| `github.com/Project-Helianthus/helianthus-eebusreg/eebusraw` | `IdentityDocumentV1` | `helianthus.eebus.raw.identity.v1` |
| `github.com/Project-Helianthus/helianthus-eebusreg/eebusevidence` | `EnvelopeV1` | `helianthus.eebus.raw.evidence-envelope.v1` |

The stable identity root is a redacted raw runtime identity document. The
stable evidence root is a redacted raw snapshot envelope carrying zero or more
evidence descriptors. Neither root grants runtime authority or defines a final
MCP API.

Earlier exported draft surfaces remain in the codebase for compatibility, but
are not part of this freeze:

| Retained draft contract | Draft-only public surfaces | Stable V1 difference |
|---|---|---|
| `helianthus.eebus.raw.identity.v1alpha1` | `IdentityDocument`, `EndpointIdentity`, `PairingObservation`, `SessionIdentity`, `PairingState`, `SessionState` | `IdentityDocumentV1` uses `EndpointIdentityV1` and `SessionIdentityV1`; pairing and session lifecycle state are absent. |
| `helianthus.eebus.raw.evidence-envelope.v1alpha1` | `Envelope`, `Reference`, `Object`, `ToolID`, `Scope` | `EnvelopeV1` uses `ReferenceV1`, `ObjectV1`, `CaptureProvenanceV1`, and `RawSnapshotScopeV1`; final MCP tool identity and draft scope are absent. |

V1 and `v1alpha1` validators reject each other's contract identifiers. Draft
fields, enum values, or behavior do not become V1 merely because the Go
declarations remain exported. Shared types listed in the V1 tables below are
frozen only as members of the V1 closure; V1 root validation supplies any
stricter rule noted below.

## Stable Identity Types

The stable identity closure is entirely project-owned. String types have Go
underlying type `string`.

### Identity enums

| Go type | Go constant | Exact JSON/string value |
|---|---|---|
| `ContractVersion` | `IdentityContractV1` | `helianthus.eebus.raw.identity.v1` |
| `MaskTier` | `MaskTierRedacted` | `redacted` |
| `EndpointRoleV1` | `EndpointRoleV1Local` | `local` |
| `EndpointRoleV1` | `EndpointRoleV1Remote` | `remote` |
| `IDKind` | `IDKindLocalSKI` | `local-ski` |
| `IDKind` | `IDKindRemoteSKI` | `remote-ski` |
| `IDKind` | `IDKindCertificateFingerprint` | `certificate-fingerprint` |
| `IDKind` | `IDKindPeer` | `peer` |
| `IDKind` | `IDKindSession` | `session` |
| `UnknownPath` | `UnknownPathDocument` | `/document/unknown` |
| `UnknownPath` | `UnknownPathDevice` | `/device/unknown` |
| `UnknownPath` | `UnknownPathLocal` | `/local/unknown` |
| `UnknownPath` | `UnknownPathRemote` | `/remote/unknown` |
| `UnknownPath` | `UnknownPathSession` | `/session/unknown` |

No other `MaskTier`, `EndpointRoleV1`, `IDKind`, or `UnknownPath` value is
valid. `ContractVersion` also retains the draft constant, but a stable identity
field accepts only `IdentityContractV1`.

### Identity structs

Types in this table are declared in `eebusraw`; the field order shown is the Go
declaration and JSON output order.

| Go type | Go field | Declared Go field type | Exact JSON tag | Omission rule |
|---|---|---|---|---|
| `RedactedID` | `Kind` | `IDKind` | `json:"kind"` | never omitted |
| `RedactedID` | `Masked` | `string` | `json:"masked"` | never omitted |
| `RedactedID` | `Digest` | `string` | `json:"digest,omitempty"` | omitted only when empty; required in every V1 identity and V1 reference use |
| `OpaqueValue` | `Masked` | `string` | `json:"masked"` | never omitted |
| `OpaqueValue` | `Digest` | `string` | `json:"digest,omitempty"` | omitted when empty |
| `OpaqueValue` | `Size` | `int` | `json:"size,omitempty"` | omitted when zero |
| `UnknownField` | `Path` | `UnknownPath` | `json:"path"` | never omitted |
| `UnknownField` | `Value` | `OpaqueValue` | `json:"value"` | never omitted |
| `EndpointIdentityV1` | `Role` | `EndpointRoleV1` | `json:"role"` | never omitted |
| `EndpointIdentityV1` | `ID` | `RedactedID` | `json:"id"` | never omitted |
| `EndpointIdentityV1` | `Unknown` | `[]UnknownField` | `json:"unknown,omitempty"` | omitted when nil or empty |
| `SessionIdentityV1` | `ID` | `RedactedID` | `json:"id"` | never omitted |
| `SessionIdentityV1` | `RemoteID` | `RedactedID` | `json:"remote_id"` | never omitted |
| `SessionIdentityV1` | `Unknown` | `[]UnknownField` | `json:"unknown,omitempty"` | omitted when nil or empty |
| `IdentityDocumentV1` | `Contract` | `ContractVersion` | `json:"contract"` | never omitted |
| `IdentityDocumentV1` | `MaskTier` | `MaskTier` | `json:"mask_tier"` | never omitted |
| `IdentityDocumentV1` | `CapturedAt` | `time.Time` | `json:"captured_at"` | never omitted |
| `IdentityDocumentV1` | `Local` | `EndpointIdentityV1` | `json:"local"` | never omitted |
| `IdentityDocumentV1` | `Remotes` | `[]EndpointIdentityV1` | `json:"remotes,omitempty"` | omitted when nil or empty |
| `IdentityDocumentV1` | `Sessions` | `[]SessionIdentityV1` | `json:"sessions,omitempty"` | omitted when nil or empty |
| `IdentityDocumentV1` | `Unknown` | `[]UnknownField` | `json:"unknown,omitempty"` | omitted when nil or empty |

`IdentityDocumentV1` contains no pairing, trust, lifecycle state, readiness, or
availability field. `SessionIdentityV1.RemoteID` records a redacted association;
it does not establish trust, connection state, or authority.

## Stable Evidence Types

### Evidence enums

| Go type | Go constant | Exact JSON/string value |
|---|---|---|
| `ContractVersion` | `EnvelopeContractV1` | `helianthus.eebus.raw.evidence-envelope.v1` |
| `CaptureProvenanceV1` | `CaptureProvenanceRuntimeObservation` | `runtime-observation` |
| `RawSnapshotScopeV1` | `RawSnapshotScopeRoot` | `raw-root` |
| `RawSnapshotScopeV1` | `RawSnapshotScopeIdentity` | `raw-identity` |
| `RawSnapshotScopeV1` | `RawSnapshotScopeTopology` | `raw-topology` |
| `RawSnapshotScopeV1` | `RawSnapshotScopeServices` | `raw-services` |
| `RawSnapshotScopeV1` | `RawSnapshotScopeSessions` | `raw-sessions` |
| `RawSnapshotScopeV1` | `RawSnapshotScopeUnknown` | `raw-unknown` |
| `AuthScope` | `AuthScopeReadRaw` | `eebus.raw.read` |
| `ObjectKind` | `ObjectKindIdentity` | `identity` |
| `ObjectKind` | `ObjectKindTopology` | `topology` |
| `ObjectKind` | `ObjectKindService` | `service` |
| `ObjectKind` | `ObjectKindSession` | `session` |
| `ObjectKind` | `ObjectKindUnknown` | `unknown` |

No other `CaptureProvenanceV1`, `RawSnapshotScopeV1`, `AuthScope`, or
`ObjectKind` value is valid. `ContractVersion` also retains the draft constant,
but a stable reference accepts only `EnvelopeContractV1`.

### Evidence structs

Types in this table are declared in `eebusevidence`. Cross-package field types
are shown with the owning `eebusraw` package.

| Go type | Go field | Declared Go field type | Exact JSON tag | Omission rule |
|---|---|---|---|---|
| `ReferenceV1` | `Runtime` | `eebusraw.RedactedID` | `json:"runtime"` | never omitted; digest required |
| `ReferenceV1` | `Contract` | `ContractVersion` | `json:"contract"` | never omitted |
| `ReferenceV1` | `CaptureProvenance` | `CaptureProvenanceV1` | `json:"capture_provenance"` | never omitted |
| `ReferenceV1` | `Scope` | `RawSnapshotScopeV1` | `json:"scope"` | never omitted |
| `ReferenceV1` | `MaskTier` | `eebusraw.MaskTier` | `json:"mask_tier"` | never omitted |
| `ReferenceV1` | `AuthScope` | `AuthScope` | `json:"auth_scope"` | never omitted |
| `ObjectV1` | `Kind` | `ObjectKind` | `json:"kind"` | never omitted |
| `ObjectV1` | `Digest` | `string` | `json:"digest"` | never omitted and must be valid |
| `ObjectV1` | `Size` | `int` | `json:"size"` | never omitted, including zero |
| `ObjectV1` | `DataTimestamp` | `time.Time` | `json:"data_timestamp"` | never omitted |
| `ObjectV1` | `Unknown` | `[]eebusraw.UnknownField` | `json:"unknown,omitempty"` | omitted when nil or empty |
| `EnvelopeV1` | `Reference` | `ReferenceV1` | `json:"ref"` | never omitted |
| `EnvelopeV1` | `CapturedAt` | `time.Time` | `json:"captured_at"` | never omitted |
| `EnvelopeV1` | `DataTimestamp` | `time.Time` | `json:"data_timestamp"` | never omitted |
| `EnvelopeV1` | `Objects` | `[]ObjectV1` | `json:"objects,omitempty"` | omitted when nil or empty |
| `EnvelopeV1` | `DataHash` | `string` | `json:"data_hash,omitempty"` | omitted when empty; verified when present |

## Validation, Redaction, And Time

All V1 validation and JSON marshaling fail closed. Invalid enum values,
unredacted values, malformed digests, zero or unrepresentable timestamps,
incorrect local or remote roles, and a present but stale `data_hash` return an
error; invalid objects are not serialized.

The V1 rules are:

- every masked identity or opaque value has exact `masked` value
  `[redacted]`;
- every required digest, and every optional digest when present, has exact
  form `sha256:` followed by 64 lowercase hexadecimal characters;
- `RedactID` hashes the raw Go string bytes with SHA-256; `OpaqueBytes` and
  `DigestBytes` hash the supplied byte slice with SHA-256;
- `OpaqueBytes` also records the input byte length in `size`;
- identity and reference IDs require a non-empty digest even though the shared
  `RedactedID.Digest` field has `omitempty` for retained draft compatibility;
- `OpaqueValue.Size` and `ObjectV1.Size` must be non-negative;
- `CapturedAt`, envelope `DataTimestamp`, and object `DataTimestamp` must be
  non-zero and representable by Go's RFC3339 JSON time marshaler;
- constructors normalize timestamps to UTC, JSON marshaling emits UTC, and
  hash material formats time with `time.RFC3339Nano` after UTC conversion.

The shared standalone `RedactedID` and `OpaqueValue` validators retain draft
compatibility. The stable root validators add the lowercase and required-digest
checks, so data that passes a shared standalone validator can still be rejected
when embedded in a V1 root.

Public formatting never reveals caller-controlled raw fields. Exact composite
`String`, `GoString`, and `fmt.Formatter` outputs are:

| Type | Safe output or pattern |
|---|---|
| `IdentityDocumentV1` | `identity_document_v1:[redacted]` |
| `EndpointIdentityV1` | `endpoint_identity_v1:[redacted]` |
| `SessionIdentityV1` | `session_identity_v1:[redacted]` |
| `RedactedID` | `<validated-kind>:[redacted]` |
| `UnknownField` | `unknown_field:[redacted]` |
| `OpaqueValue` | `opaque:[redacted]` |
| `ReferenceV1` | `reference_v1:[redacted]` |
| `ObjectV1` | `object_v1:[redacted]` |
| `EnvelopeV1` | `envelope_v1:[redacted]` |

Invalid string enums return fixed `invalid-*` placeholders or fail JSON
marshaling; they never echo the invalid input.

## Identity Canonicalization

`IdentityDocumentV1.Validate` enforces one local endpoint with role `local` and
requires every `Remotes` member to have role `remote`.

Identity keys are the tuple `(ID.Kind, ID.Digest)`. Duplicate keys are rejected
independently within `Remotes` and within `Sessions`. A duplicate session key is
rejected even if its `RemoteID` or unknown evidence differs. This prevents
contradictory entries from becoming order-dependent. The contract does not add
an unstated requirement that each session `RemoteID` appear in `Remotes`.

Canonical JSON ordering is lexicographic unless a numeric comparison is stated:

1. each unknown-field list sorts by `Path`, `Value.Digest`, `Value.Masked`, then
   numeric `Value.Size`;
2. `Remotes` sorts by `Role`, identity key, then the canonical unknown-field
   sequence;
3. `Sessions` sorts by session identity key, remote identity key, then the
   canonical unknown-field sequence;
4. the local endpoint's unknown fields and the document-level unknown fields
   use the same unknown-field ordering.

`EndpointIdentityV1` and `SessionIdentityV1` apply their unknown-field ordering
when marshaled as standalone values, not only when nested in the document.
Canonical marshaling allocates sorted copies and does not mutate caller-visible
slice order.

## Evidence Reference Binding

`ReferenceV1` binds exactly these protocol-neutral capture dimensions:

1. `runtime`: a redacted runtime identity including a required digest;
2. `contract`: `helianthus.eebus.raw.evidence-envelope.v1`;
3. `capture_provenance`: `runtime-observation`;
4. `scope`: one exact `raw-*` scope from `RawSnapshotScopeV1`;
5. `mask_tier`: `redacted`;
6. `auth_scope`: effective authorization `eebus.raw.read`.

`ReferenceV1.Matches` compares all six fields for exact equality. The stable
reference deliberately has no `ToolID`, no draft `Scope`, and no final
`eebus_v1_*` dependency. Later MCP design may bind a tool independently, but it
cannot retroactively alter this frozen raw capture reference.

## Evidence Ordering And Hashing

Evidence object order is deterministic and independent of collection order.
Objects sort by this exact key:

1. `Kind`;
2. `Digest`;
3. UTC `DataTimestamp` formatted with `time.RFC3339Nano`;
4. numeric `Size`;
5. compact canonical JSON of the sorted `Unknown` sequence.

Unknown fields use the identity unknown-field ordering. Duplicate evidence
descriptors and a shared digest across different object kinds are allowed; the
full ordered descriptor remains hash material.

`ComputeDataHash` calculates lowercase SHA-256 over one compact, code-defined
canonical JSON byte sequence. It is not a generic serializer choice. The exact
top-level field order and material are:

```text
{"data_timestamp":<UTC RFC3339Nano string>,"objects":[<sorted canonical ObjectV1>],"ref":<canonical ReferenceV1>}
```

Each canonical object uses field order `data_timestamp`, `digest`, `kind`,
`size`, then optional `unknown`. Each unknown field uses `path`, then `value`.
Each opaque value uses optional `digest`, `masked`, then optional non-zero
`size`. The canonical reference uses field order `auth_scope`,
`capture_provenance`, `contract`, `mask_tier`, `runtime`, `scope`. The runtime
ID uses `digest`, `kind`, `masked`. Strings use Go `encoding/json` string
escaping.

Included hash material is therefore:

- envelope `data_timestamp`;
- every sorted object's kind, digest, size, data timestamp, and sorted unknown
  descriptors;
- reference runtime, contract, capture provenance, raw scope, mask tier, and
  effective raw-read authorization.

The exact exclusions are envelope `captured_at` and `data_hash`. There is no
tool identifier, draft scope, raw payload, unredacted identifier, pairing
state, lifecycle state, semantic value, or consumer value in the material.
Changing only `captured_at` does not change the hash. When `data_hash` is
present, `Validate` recomputes it and rejects any mismatch. `ComputeDataHash`
does not hash an existing `data_hash`; `WithDataHash` computes and sets it.

### Frozen replay vector

The MSP-035 replay fixture hashes the following exact one-line UTF-8 payload:

```json
{"data_timestamp":"2026-07-08T14:00:00Z","objects":[{"data_timestamp":"2026-07-08T14:00:00Z","digest":"sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa","kind":"identity","size":10},{"data_timestamp":"2026-07-08T14:00:00Z","digest":"sha256:bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb","kind":"unknown","size":20,"unknown":[{"path":"/document/unknown","value":{"digest":"sha256:dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd","masked":"[redacted]","size":12}},{"path":"/remote/unknown","value":{"digest":"sha256:eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee","masked":"[redacted]","size":10}}]}],"ref":{"auth_scope":"eebus.raw.read","capture_provenance":"runtime-observation","contract":"helianthus.eebus.raw.evidence-envelope.v1","mask_tier":"redacted","runtime":{"digest":"sha256:cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc","kind":"peer","masked":"[redacted]"},"scope":"raw-root"}}
```

Its frozen result is:

```text
sha256:b909695a848d7f1817711d46730bb511f510c3ad7bc517f3ee03e517076144e1
```

Comparisons are meaningful only when the stable contract, reference binding,
mask tier, authorization, raw scope, input descriptors, and data timestamps are
the same.

## Constructor And Standalone JSON Rules

Constructors establish stable identifiers and prevent caller-owned nested
storage from changing already-created values:

| Constructor or method | Exact ownership and normalization behavior |
|---|---|
| `NewIdentityDocumentV1` | sets `IdentityContractV1` and `MaskTierRedacted`, converts `capturedAt` to UTC, copies the supplied local endpoint's `Unknown` slice |
| `NewReferenceV1` | copies the value arguments, sets `EnvelopeContractV1` and `MaskTierRedacted` |
| `NewObjectV1` | copies scalar arguments and converts `dataTimestamp` to UTC |
| `NewEnvelopeV1` | converts envelope times to UTC and deep-copies the object slice plus every object's `Unknown` slice; copied object times are UTC and copied unknowns are sorted |
| `EnvelopeV1.WithDataHash` | returns a value with the computed hash and a fresh deep copy of objects and nested unknown fields |

Slices assigned directly to exported fields after construction remain ordinary
Go caller-managed values. Marshaling and hash computation nevertheless sort
copies and do not reorder the source slices.

Standalone JSON is canonical at every frozen structured boundary:

- `EndpointIdentityV1` and `SessionIdentityV1` validate and sort copied unknown
  fields;
- `IdentityDocumentV1` validates, UTC-normalizes its timestamp, and sorts local
  unknowns, remotes, sessions, and document unknowns;
- `ObjectV1` validates, UTC-normalizes its timestamp, and sorts copied unknowns;
- `EnvelopeV1` validates its complete graph, UTC-normalizes envelope times, and
  sorts copied objects and nested unknowns;
- `ReferenceV1`, `RedactedID`, `UnknownField`, and `OpaqueValue` validate before
  JSON serialization.

The JSON field order of a marshaled `EnvelopeV1` follows its public table:
`ref`, `captured_at`, `data_timestamp`, optional `objects`, optional
`data_hash`. This complete envelope JSON is distinct from the smaller canonical
hash payload defined above.

## API-Boundary Enforcement

The implementation's `scripts/api_boundary_gate.sh` and
`internal/apiboundary` enforce this freeze at the public Go boundary. The
machine-readable artifact has exact identity:

| Manifest field | Exact value |
|---|---|
| `schema` | `helianthus.api-boundary-manifest` |
| `version` | `1` |
| `module` | `github.com/Project-Helianthus/helianthus-eebusreg` |

The gate is fail closed:

- the public-package allowlist is exactly `eebusruntime`, `eebusraw`, and
  `eebusevidence`;
- canonical-module activation covers both stable roots; a missing package,
  root, transitive type, or enum constant produces failure;
- frozen-struct comparison covers exact field order, field name, declared Go
  type, and complete JSON tag; type aliases, embedded fields, and multi-name
  fields do not bypass the comparison;
- frozen-scalar comparison covers the underlying type;
- exact enums reject missing, renamed, changed, or additional exported values;
  `ContractVersion` is deliberately non-exact at declaration inventory so
  draft constants remain exported, while the exact V1 constant remains in the
  manifest and each V1 root validator accepts only its V1 identifier;
- any additional exported type whose name ends in `V1` in a stable package is
  rejected unless it is in the manifest;
- stable-package type checking precedes manifest emission;
- the deterministic manifest sorts packages, exports, stable contracts, types,
  enums, and enum values, and is compact JSON with one trailing newline;
- manifest output is limited to an absolute regular path outside the
  repository; repository-local, traversal, or symlink destinations are
  rejected, and the write is atomic;
- path, import, export-name, cross-runtime string, and premature mutation gates
  run before artifact emission. Any violation prevents the artifact.

Public packages cannot directly import `github.com/enbility/*` or internal
facade types. Gateway and Home Assistant integration imports are forbidden.
Exported names containing registry, projection, semantic, Enbility, SHIP,
SPINE, GraphQL, Portal, Home Assistant, command-routing, trust-store, or trust
mutation authority terms are rejected. Production public API strings beginning
with `ebus.v1.` are also rejected. These checks prevent raw eeBUS evidence from
leaking into `ebus_v1_*` or from exposing implementation-library types.

## Non-Authority And Deferred Surfaces

This freeze does not define, authorize, or promise:

- pairing, trust, certificate administration, or any administrative mutation;
- lifecycle start, shutdown, reconnect, readiness, or authority state;
- availability, liveness, freshness, persistence, or retention guarantees;
- final `eebus_v1_*` MCP tool identifiers, schemas, or dereference behavior;
- semantic identities, promoted leaves, projections, GraphQL, Portal, Home
  Assistant, Matter, or other consumer contracts;
- commands, command routing, raw writes, or semantic writes;
- Enbility, SHIP, or SPINE types as public API.

This contract supplies no route from raw eeBUS fields or evidence into
`ebus_v1_*`, the eBUS registry, semantic outputs, consumer outputs, command
paths, or write paths. Later milestones remain subject to separate
semantic-promotion, coexistence, documentation, consumer, and write-authority
gates.

This page records only public project-owned contract facts and publishable
code, test, issue, and PR evidence. It does not quote, reproduce, or depend on
restricted eeBUS specification content.
