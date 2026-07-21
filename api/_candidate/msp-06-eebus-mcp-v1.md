---
canonical_source: "Project-Helianthus/helianthus-docs-eebus:api/_candidate/msp-06-eebus-mcp-v1.md"
owner_domain: "api"
license: "AGPL-3.0-only"
publication_status: "candidate"
claim_status: "no-protocol-claims"
source_class: "derived_inference"
hypothesis_status: "draft"
falsifier: "The gateway implementation or contract tests require a different closed wire shape, binding, authorization policy, or deterministic hash view."
source_commit: "7a5852e009bbdcba47f0a34ba866070a4ab35ef8"
candidate_output: "true"
stable_navigation: "false"
search: "false"
sitemap: "false"
versioned_bundle: "false"
release_bundle: "false"
candidate_output_path: "api/_candidate/msp-06-eebus-mcp-v1.md"
---

# Candidate MSP-06 Read-Only eeBUS MCP v1

## Candidate Boundary

This candidate is tracked by [issue 43](https://github.com/Project-Helianthus/helianthus-docs-eebus/issues/43).
Its source is
`Project-Helianthus/helianthus-eebusreg@7a5852e009bbdcba47f0a34ba866070a4ab35ef8:eebusruntime`.
This candidate must not ingest restricted material and uses no vendor-restricted source.

This document freezes a proposed MCP wire contract only. It makes no eeBUS
protocol claim, no runtime deployment claim, and no supported API claim. It
does not establish consumer availability or authorize any protocol, trust,
pairing, semantic, or write behavior. All publication channels remain disabled
until a later promotion gate replaces this candidate.

## Stable Tool Inventory

| Tool | Scope | Required input | Optional input | Data |
| --- | --- | --- | --- | --- |
| `eebus.v1.runtime.status.get` | `runtime-status` | `none` | `evidence_ref` | `RuntimeStatusDataV1` |
| `eebus.v1.services.list` | `services` | `none` | `evidence_ref` | `ServicesListDataV1` |
| `eebus.v1.services.get` | `service` | `id_digest` | `evidence_ref` | `ServiceDataV1` |
| `eebus.v1.sessions.list` | `sessions` | `none` | `evidence_ref` | `SessionsListDataV1` |
| `eebus.v1.sessions.get` | `session` | `id_digest` | `evidence_ref` | `SessionDataV1` |
| `eebus.v1.topology.get` | `topology` | `none` | `evidence_ref` | `TopologyDataV1` |
| `eebus.v1.snapshot.capture` | `whole-root` | `none` | `none` | `CapturedRootV1` |
| `eebus.v1.snapshot.drop` | `whole-root` | `snapshot_ref` | `none` | `DropResultV1` |
| `eebus.v1.pairing.status.get` | `pairing-status` | `none` | `evidence_ref` | `PairingStatusDataV1` |

The table is the closed stable inventory. No pairing mutation, trust mutation,
raw write, command, or administrative tool is part of this contract.

## Observation Source Boundary

The `eebus.v1` family projects raw runtime observations only. The provider must
not synthesize a service, session, pairing row, topology row, or evidence
reference from an allowlist, protected identity, durable
SHIP ID, or open local registration window.

An mDNS observation may populate the service tools without populating the
session tools. A connection callback may then populate the session tools. A
transport-backed pairing callback may populate pairing status. Each stage is
independent, and an earlier stage cannot imply a later one.

This identity/discovery contract adds no tool, field, semantic object, GraphQL
field, Portal model, Home Assistant entity, or write path. Shareable
output remains raw, redacted, and limited to the closed stable inventory above.

`id_digest` is a redacted SHA-256 selector represented by the runtime-scoped
pseudonym defined below. It selects an already redacted ID and never accepts a
raw identity. An unrecognized argument, including an
authorization, mask, or principal selector, is rejected before provider access.

## Wire Object Schemas

| Object | Required fields | Optional fields | Additional properties |
| --- | --- | --- | --- |
| `EnvelopeV1` | `meta,data,error` | `none` | `false` |
| `MetaV1` | `contract,tool,scope,mask_tier,auth_scope,mode,data_timestamp,data_hash,runtime` | `none` | `false` |
| `ContractV1` | `name,major,minor` | `none` | `false` |
| `RuntimeMetaV1` | `state` | `degradation` | `false` |
| `ErrorV1` | `code,message,retriable,source_layer` | `none` | `false` |
| `IdentityDigestV1` | `kind,digest` | `none` | `false` |
| `EvidenceDescriptorV1` | `kind,digest,size,data_timestamp` | `none` | `false` |
| `DegradationDataV1` | `reason,since` | `none` | `false` |
| `RuntimeStatusDataV1` | `state` | `degradation` | `false` |
| `ServiceDataV1` | `id,kind,visible,paired` | `evidence` | `false` |
| `ServicesListDataV1` | `services` | `none` | `false` |
| `SessionDataV1` | `id,remote,state` | `since,evidence` | `false` |
| `SessionsListDataV1` | `sessions` | `none` | `false` |
| `PairingDataV1` | `remote,state` | `since,evidence` | `false` |
| `PairingStatusDataV1` | `pairing` | `none` | `false` |
| `FeatureDataV1` | `id,role` | `evidence` | `false` |
| `EntityDataV1` | `id,features` | `evidence` | `false` |
| `UseCaseClaimDataV1` | `id` | `evidence` | `false` |
| `DeviceDataV1` | `id,entities,usecase_claims` | `evidence` | `false` |
| `TopologyDataV1` | `devices` | `none` | `false` |
| `SnapshotMetaDataV1` | `contract,runtime,mask_tier,captured_at,data_timestamp,data_hash` | `none` | `false` |
| `SnapshotDataV1` | `meta,status,pairing,services,sessions,topology` | `evidence` | `false` |
| `EvidenceRefsV1` | `runtime_status_ref,services_list_ref,services_get_ref,sessions_list_ref,sessions_get_ref,topology_ref,pairing_status_ref` | `none` | `false` |
| `CapturedRootV1` | `snapshot_ref,expires_at,snapshot_content_hash,evidence_refs,snapshot` | `none` | `false` |
| `DropResultV1` | `status` | `none` | `false` |

Every response is one `EnvelopeV1` containing `meta`, `data`, and `error`.
Success requires non-null `data` and null `error`; failure requires null `data`
and non-null `error`. An omitted optional field is not serialized as null.
Raw runtime `Unknown` values are never copied to wire DTOs. Public error
messages are fixed by error code; backend error text is never copied into
`message`.

The normative candidate schema is
[`api/_candidate/msp-06/helianthus.eebus.mcp.v1.schema.json`](msp-06/helianthus.eebus.mcp.v1.schema.json).
It uses JSON Schema Draft 2020-12 and closes every object with
`additionalProperties=false`. Timestamps are UTC RFC 3339 strings with a
literal `Z`; hashes match `sha256:<64-lowercase-hex>`; reference tokens and
identity pseudonyms are 43-character unpadded base64url strings. Integers on
the wire are restricted to the portable JSON safe-integer range. The schema's
closed enum values are normative. In particular, runtime, session, pairing,
and feature-role `unknown` values are rejected instead of serialized.

## Collection Ordering

| Collection | Unique identity | Ascending order |
| --- | --- | --- |
| `services` | `id.digest,kind` | `id.digest,kind` |
| `sessions` | `id.digest` | `id.digest` |
| `pairing` | `remote.digest` | `remote.digest` |
| `devices` | `id.digest` | `id.digest` |
| `entities` | `id.digest` | `id.digest` |
| `features` | `id.digest` | `id.digest` |
| `usecase_claims` | `id.digest` | `id.digest` |
| `evidence` | `kind,digest,size,data_timestamp` | `kind,digest,size,data_timestamp` |

All comparisons are bytewise ascending over their serialized UTF-8 scalar
values. Providers must reject duplicate unique identities as
`contract_violation`; they must not silently retain one duplicate. These rules
apply recursively to live and captured responses before hashing.

The contract identity is `helianthus-eebus-mcp`, with major `1` and minor `0`.
The mode is `live` or `evidence`. A valid degraded snapshot is an explained
success: runtime state and degradation reason are carried in the closed wire
fields. In particular, no visible services is never represented as an
unexplained empty success.

## Opaque Reference Binding

| Reference | Tool binding | Scope binding | Consumer |
| --- | --- | --- | --- |
| `snapshot_ref` | `eebus.v1.snapshot.capture` | `whole-root` | `eebus.v1.snapshot.drop` |
| `runtime_status_ref` | `eebus.v1.runtime.status.get` | `runtime-status` | `eebus.v1.runtime.status.get` |
| `services_list_ref` | `eebus.v1.services.list` | `services` | `eebus.v1.services.list` |
| `services_get_ref` | `eebus.v1.services.get` | `service` | `eebus.v1.services.get` |
| `sessions_list_ref` | `eebus.v1.sessions.list` | `sessions` | `eebus.v1.sessions.list` |
| `sessions_get_ref` | `eebus.v1.sessions.get` | `session` | `eebus.v1.sessions.get` |
| `topology_ref` | `eebus.v1.topology.get` | `topology` | `eebus.v1.topology.get` |
| `pairing_status_ref` | `eebus.v1.pairing.status.get` | `pairing-status` | `eebus.v1.pairing.status.get` |

Each reference is bound when minted to runtime identity, MCP contract identity,
tool identity, scope, the `redacted` mask tier, and the effective
`eebus.raw.read` authorization scope. Callers supply only the opaque token;
they cannot supply, override, or request any binding component. Each token has
32 cryptographically random bytes encoded as unpadded base64url. Its canonical
wire syntax is exactly 43 ASCII characters matching `[A-Za-z0-9_-]{43}` and it
decodes to exactly 32 bytes; decoders reject non-canonical re-encodings.

Evidence references resolve only through the exact tool and scope in the
table. The internal drop operation is part of the MCP server implementation
and does not require a public `ToolDrop` declaration.

## Snapshot Lifecycle Constants

| Constant | Value |
| --- | --- |
| `active_ttl` | `5m` |
| `max_active` | `32` |
| `tombstone_ttl` | `5m` |
| `max_tombstones` | `256` |
| `token_entropy` | `256-bit` |

The store permits 32 active root captures and seven descendant evidence
references per root. Live reads allocate no store entry. A root and all of its
descendants expire when `now >= expires_at`. Capture first builds and validates
the detached root, then concurrent captures reserve quota atomically. Capture
failure consumes no active slot. A full active store returns `quota_exceeded`.

Quota and tombstone bounds count one root group regardless of its eight tokens.
All capture, lookup, drop, expiry, purge, and eviction transitions execute under
one store mutex. Each operation captures `now` once; after deterministic expiry
purge, the mutation or lookup is its linearization point. Capture builds its
detached snapshot before taking the mutex, then purges, checks quota, mints all
eight tokens, and inserts the complete root group atomically.

Drop or expiry moves the root and descendants to terminal tombstones and
invalidates every descendant evidence reference. Tombstone TTL starts at the
terminal transition. When the tombstone bound is reached, the oldest terminal
tombstone is evicted first, with the total tie break
`terminal_at then root token bytes`. While a descendant tombstone exists, it resolves as
`snapshot_gone`; after eviction, the same well-formed reference is unknown.

Every reference retains the policy version that minted it. Later policy changes
cannot reinterpret its binding, extend its lifetime, or alter its terminal
result.

An unknown well-formed evidence reference returns `not_found`.
`snapshot.drop` returns exactly `dropped` or `already_gone`, never returns
`not_found`, and is idempotent for expired, dropped, evicted, or unknown roots.

## Reference Resolution Matrix

| Condition | Result |
| --- | --- |
| `malformed-token` | `invalid_argument` |
| `unknown-evidence-token` | `not_found` |
| `known-wrong-binding` | `permission_denied` |
| `root-used-as-evidence` | `permission_denied` |
| `evidence-used-as-root` | `already_gone` |
| `expired-or-dropped-descendant` | `snapshot_gone` |
| `evicted-descendant-tombstone` | `not_found` |
| `active-root-drop` | `dropped` |
| `terminal-root-drop` | `already_gone` |
| `unknown-well-formed-root-drop` | `already_gone` |

## Authorization Policy

The production MCP HTTP route is currently unauthenticated and does not
authenticate an end user. Therefore v1 uses a fixed redacted-reader policy:
`mask_tier=redacted` and `auth_scope=eebus.raw.read`. Those values are never
accepted from tool arguments or headers. HTTP headers cannot alter the fixed
policy.

Authorization is evaluated after shape and syntax and before reference
lifecycle. The fail-closed input rule is: authorization, mask, or principal arguments return
`invalid_argument`. A future authenticated policy may replace that grant, but
it cannot reinterpret an already minted reference. A binding mismatch remains
fail-closed under the policy that minted the reference.

## Exhaustive Error Inventory

| Code | Meaning |
| --- | --- |
| `invalid_argument` | malformed tool input, token, or forbidden policy selector |
| `not_found` | unknown well-formed evidence reference or redacted selector |
| `permission_denied` | known reference used under the wrong binding |
| `admin_required` | a future authenticated policy requires stronger authority |
| `backend_unavailable` | the registered live provider is disconnected or unavailable |
| `timeout` | the live provider exceeded its bounded deadline |
| `snapshot_gone` | a known descendant belongs to an expired or dropped root |
| `quota_exceeded` | no active root slot is available |
| `contract_violation` | an impossible provider or wire invariant was detected |

Error messages are stable, redacted contract strings. The server never exposes
backend text, reference material, identity material, or stack details through
an error.

## Exact Error Mapping

| Code | Message | Retriable | Source layer |
| --- | --- | --- | --- |
| `invalid_argument` | `invalid argument` | `false` | `mcp` |
| `not_found` | `not found` | `false` | `mcp` |
| `permission_denied` | `permission denied` | `false` | `policy` |
| `admin_required` | `administrator authorization required` | `false` | `policy` |
| `backend_unavailable` | `eeBUS runtime unavailable` | `true` | `eebusruntime` |
| `timeout` | `eeBUS runtime request timed out` | `true` | `eebusruntime` |
| `snapshot_gone` | `snapshot no longer available` | `false` | `snapshot-store` |
| `quota_exceeded` | `snapshot quota exceeded` | `true` | `snapshot-store` |
| `contract_violation` | `eeBUS MCP contract violation` | `false` | `mcp` |

This table is exhaustive and normative. Implementations must emit the exact
message, retry flag, and source layer for the selected code.

## Error Precedence

| Stage | Rule |
| --- | --- |
| `shape-and-syntax` | validate tool shape, arguments, selectors, and token syntax |
| `authorization` | apply the fixed policy and exact binding requirement |
| `reference-lifecycle` | resolve active, terminal, evicted, or unknown state |
| `backend` | call the live provider subject to the bounded deadline |
| `invariant` | reject an impossible internal state as a contract violation |

Only the first failing stage is reported. Later stages are not evaluated and
cannot change the earlier error.

## Hash View

| Field | Hash source |
| --- | --- |
| `contract` | contract name and version |
| `tool` | exact stable tool name |
| `scope` | exact scope binding |
| `mask_tier` | fixed redacted tier |
| `auth_scope` | fixed effective read scope |
| `mode` | live or evidence |
| `data_timestamp` | observation timestamp |
| `runtime_state` | closed runtime state |
| `degradation` | closed degradation value or null |
| `data` | success data or null |
| `error` | stable public error or null |

`meta.data_hash` has the form `sha256:<64-lowercase-hex>` and is SHA-256 over
the RFC 8785/JCS serialization of exactly the table fields. Object keys are
ordered recursively by UTF-16 code units as required by JCS. The numeric rule
is: non-finite numbers and negative zero are rejected. Integers or exact decimals outside the
portable JSON safe-integer range are strings. The hash view distinguishes an
explicit null from an omitted field.

The excluded fields are: opaque reference tokens, capture time, expiry time,
and backend error text. They are excluded from hash material. Token
substitution therefore cannot change the
hash of otherwise identical captured content, while payload mutation must
change it. Stable public error normalization makes the hash independent of
backend message text.

For a capture, `snapshot_content_hash equals snapshot.meta.data_hash`. That
snapshot-content projection `excludes SnapshotMetaDataV1.data_hash` to avoid a
self-reference and excludes the opaque tokens, capture time, and expiry time
listed above. The `capture envelope meta.data_hash is a separate envelope hash`
over the capture response's own hash view and therefore generally differs from
the snapshot-content hash. The runtime's internal source hash is not copied to
the stable wire as a correlator. The executable candidate vectors live at
`api/_candidate/msp-06/jcs-hash-vectors-v1.json`.

## Runtime Registration And Replay

The tools are absent from `tools/list` until an enabled eeBUS runtime provider
is registered. The ordering invariant is: registration completes before the
MCP handler is mounted.
Registration happens once and is never removed during a transient disconnect;
a second registration is rejected.

There is exactly one `Snapshot()` call for each live read or capture, which
constructs one detached `SnapshotV1` per live tool call. There is no stale-live
fallback.
On disconnect, a live call returns `backend_unavailable`, previously captured
roots remain readable, and later live calls recover without re-registering
tools. There are zero provider calls for evidence reads and drop. Captured envelopes are
byte-identical after provider mutation, disconnect, and provider error.

This contract does not modify `ebus.v1.*`, does not modify GraphQL, does not
modify Portal, and does not modify Home Assistant. It does not register
semantic facts, does not expose a write or pairing mutation, and grants no
consumer authority.

## eeBUS Transport Gate v0 Mapping

| Case | Behavior |
| --- | --- |
| `EEBUS-G12` | `whole-root-capture` |
| `EEBUS-G13` | `byte-stable-tool-bound-replay` |
| `EEBUS-G14` | `exact-binding-and-fixed-policy` |
| `EEBUS-G15` | `drop-expiry-and-tombstones` |
| `EEBUS-G16` | `wire-log-error-artifact-redaction` |

G12 proves one immutable whole-root capture. G13 proves exact replay after live
mutation and disconnect. G14 proves reference binding and the fixed policy.
G15 proves quota, drop, expiry, tombstone, and eviction behavior. G16 proves
that PEM, token, full fingerprint, IP, MAC, serial, local identity, stable peer
id, and pairing history never enter shareable output.

Every `IdentityDigestV1.digest` is produced with a process-ephemeral
HMAC-SHA-256 key and encoded as an unpadded 43-character base64url
runtime-scoped pseudonym. The HMAC input is domain-separated by contract,
identity kind, runtime instance, and the raw identity bytes. A provider must
re-pseudonymize every raw SKI, raw SHIP ID, full fingerprint, or source-side
redacted identifier; it must never forward a stable source digest. The key is
never persisted, logged, returned, or reused after process restart.

The positive output allowlist consists only of fields declared in the closed
candidate JSON schema. Raw identity, certificate or authentication material,
network coordinates, trust-store content, and pairing history have no wire
field and must fail closed as `contract_violation` if encountered during DTO
construction. The fixed reader policy does not establish a trusted network
boundary: the unauthenticated route remains untrusted ingress, so masking and
pseudonymization are mandatory even on loopback or a private subnet.

Reference tokens are permitted only in designated direct MCP response fields.
The artifact rule is: logs, errors, and publishable gate artifacts contain no
reference token. The public API manifest contains no `ToolDrop` declaration.

## Rollback

Rollback is entirely in-memory and registration-scoped. Remove the eeBUS
provider registration and delete only the in-memory snapshot store. No
trust-store migration, no eBUS rollback, and no consumer rollback is required.
The candidate adds no persistent format, protocol behavior, or consumer state.
