---
canonical_source: "Project-Helianthus/helianthus-docs-eebus:architecture/_candidate/msp-04a-persistent-store.md"
owner_domain: "architecture"
license: "AGPL-3.0-only"
publication_status: "candidate"
claim_status: "evidence-backed"
source_class: "derived_inference"
evidence_ids: "EV-20260711-001"
hypothesis_status: "draft"
falsifier: "A merged MSP-04A implementation or accepted architecture review demonstrates that this candidate cannot meet its durability, confinement, or secret-handling contract."
stable_navigation: "false"
search: "false"
sitemap: "false"
versioned_bundle: "false"
release_bundle: "false"
---

# Candidate MSP-04A Internal Persistent Store Contract

## Status And Authority

This document is the pre-implementation architecture contract for MSP-04A. Its
normative terms constrain the later implementation, but they do not claim that
the store, schema, migrations, or recovery behavior have landed.

The design provenance is the [MSP-04A documentation issue][docs-issue], the
[companion code issue][code-issue], the [locked MSP-04A execution-plan row][plan-row],
and the supported eeBUS architecture ownership boundary at
`architecture/README.md`. Those project decisions establish scope and
sequencing; they are not protocol evidence. This contract makes no protocol
claim and uses no protocol specification as a source.

Stable API, navigation, search, sitemap, versioned-bundle, and release-bundle
outputs intentionally omit this candidate.

## Normative Language

`MUST`, `MUST NOT`, `SHOULD`, and `MAY` describe implementation acceptance for
MSP-04A. Outcome labels and field names in this document are internal
conformance vocabulary. They do not create exported Go declarations, a public
file format, or a compatibility promise to consumers.

## Boundary

The store belongs to the eeBUS runtime implementation in
`helianthus-eebusreg`. It owns durable representation, validation, generation
commit, migration mechanics, and storage-integrity classification for
runtime-local state. It does not own protocol interpretation, pairing policy,
trust decisions, lifecycle transitions, semantic projection, or consumer
behavior.

The store is internal-only:

- no package outside the owning runtime receives direct filesystem paths,
  mutable records, private-key bytes, or store handles;
- no record name or value becomes a public raw view or public API field;
- callers provide and receive in-memory internal values only;
- the store never opens a listener or outbound socket; and
- the store never performs a pairing, trust, revocation, lifecycle, or semantic
  decision.

The integrity hashes below detect accidental corruption and bind manifests to
exact generation bytes. They do not claim protection from a hostile account
that can already replace every store file and its metadata.

## V1 Filesystem Layout

The v1 layout uses fixed ASCII names. No filename is derived from certificate
material, an SKI, a SHIP ID, a remote identity record, or any other sensitive
value.

```text
<root>/
  LOCK
  MANIFEST.A
  MANIFEST.B
  generations/
    g-<20-digit-generation>.json
```

`MANIFEST.A` and `MANIFEST.B` are alternating publication slots. A live slot
inode is never edited or truncated. Publication writes and fsyncs a new inode,
atomically replaces only the non-selected slot, and fsyncs `<root>`. Generation
files are immutable after publication. `LOCK` is persistent but empty; lock
ownership comes from the operating-system lock, never file presence or process
metadata written into it.

Temporary files use fixed, non-sensitive prefixes and implementation-created
random suffixes. A temporary generation is created inside `generations/`; a
temporary manifest is created in `<root>`. A temporary name MUST NOT include
record data, an identity digest, or a caller-supplied string. Recognized
temporary files and unreferenced generations are never adopted during open.

### Bootstrap Durability

Bootstrap is part of the durability contract, not an assumed deployment step:

1. The implementation traverses the configured absolute path using the
   platform backend and an already opened parent descriptor. If the final root
   does not exist, it creates only that final component with mode `0700`, opens
   and verifies it, and fsyncs the parent directory. Failure or unsupported
   parent-directory fsync returns `bootstrap_durability_unknown`; the new root
   is not used.
2. With a verified root descriptor, bootstrap creates `generations/` as `0700`
   and `LOCK` as a `0600` regular file using exclusive descriptor-relative
   creation. It fsyncs the newly created `LOCK` file and then fsyncs the root
   directory after all new child entries exist.
3. No manifest or key-bearing generation is written until both directory fsync
   steps and the backend capability probe have succeeded. Directory fsync that
   is unsupported, ignored, or reported ambiguously is a fail-closed
   `filesystem_capability_unavailable` result.
4. An interrupted bootstrap may be resumed only when the root contains a safe
   subset of the fixed bootstrap objects and no manifest, generation, unknown
   entry, or non-empty `LOCK`. A missing `LOCK` in any non-bootstrap store is
   `layout_rejected`; it is never recreated around an existing store.

### Platform Backend And Object Safety

MSP-04A requires separate descriptor-relative Linux and Darwin backends. It
does not claim support for every filesystem exposed by either operating system.
Before store use, the selected backend MUST complete an explicit capability
probe for no-follow descriptor-relative open/create, same-directory atomic
replacement, regular-file and directory fsync, non-blocking process locking,
stable device/inode identity, and ACL/additional-access inspection. The backend
MUST reject unknown filesystem/backend combinations and any unavailable or
ambiguous capability with `filesystem_capability_unavailable`.

The implementation MUST enforce all of the following before reading record
content:

1. The configured root is an absolute, lexically clean native path. Empty or
   relative paths, `.` or `..` components, embedded NUL bytes, and non-native
   separator forms are rejected.
2. Existing path components are traversed from an opened directory descriptor
   without following symlinks. Descendant access uses `openat`/`fstatat`-class
   operations relative to the verified root or `generations/` descriptor; no
   descendant is reopened through a concatenated absolute path.
3. The root and `generations/` descriptors identify real directories owned by
   the effective runtime UID with exact mode `0700`. `LOCK`, manifests,
   generations, and temporary files are regular files owned by that UID with
   exact mode `0600` and `st_nlink == 1`.
4. For every pathname-addressed store object, the backend compares the
   no-follow pathname metadata with metadata from the opened descriptor. Device
   and inode numbers MUST match where the platform exposes them. A mismatch,
   symlink, hard link, device, socket, FIFO, or other unexpected type is
   `layout_rejected`.
5. Creation requests the exact mode and verifies the opened descriptor. The
   process umask is not a security control. Existing broader mode bits are
   rejected rather than repaired.
6. The Linux backend rejects POSIX or rich ACL entries, including directory
   default ACLs, that grant or inherit access beyond the owning UID. The Darwin
   backend performs the equivalent extended-ACL inspection. If the applicable
   ACL API cannot prove absence of additional access, the backend fails closed;
   mode-bit inspection alone is insufficient.
7. Directory enumeration occurs only after the exclusive lock is held. Only the
   fixed layout, generation grammar, and recognized temporary grammar are
   accepted. Unknown objects are never deleted and cause `layout_rejected`.

These checks apply on every open, migration, and commit. Safety failures do not
fall back to another root or expose rejected content. Remote, userspace,
overlay, or otherwise unusual filesystems are supported only after their exact
backend combination has conformance evidence for every required primitive;
otherwise the capability probe rejects them.

## V1 Logical Schema

V1 manifests and generations use the canonical JSON profile defined below.
JSON is an internal disk encoding only.

### Manifest Slots

Each slot contains a closed manifest envelope:

| Field | Type | Constraint |
| --- | --- | --- |
| `slot_format_version` | unsigned integer | Exactly `1`; this stable envelope enables epoch selection. |
| `manifest_epoch` | unsigned integer | Range `1` through the maximum signed 64-bit value. |
| `manifest_payload` | base64 string | Exact canonical bytes of one manifest payload, including its final newline. |
| `manifest_sha256` | string | Lowercase SHA-256 of the decoded `manifest_payload` bytes. |

The decoded v1 manifest payload has exactly these fields:

| Field | Type | Constraint |
| --- | --- | --- |
| `manifest_version` | unsigned integer | Exactly `1`. |
| `current` | generation reference | The only generation eligible for normal runtime use. |
| `parent` | generation reference or `null` | The exact direct parent of `current`; `null` only for the first generation. |

A generation reference has exactly `generation`, `generation_file`,
`generation_sha256`, and `schema_version`. `generation` is in the range `1`
through the maximum signed 64-bit value. `generation_file` is exactly the fixed
filename implied by that value and contains no separator. `generation_sha256`
is lowercase SHA-256 of the complete generation bytes. `schema_version` is the
version encoded in those bytes.

A slot is publication-valid when its envelope is canonical and bounded, its
checksum matches, and its epoch and payload are structurally available. Open
selects the publication-valid slot with the greatest `manifest_epoch` before it
interprets the payload version or reads generation content. Equal epochs with
different bytes are `manifest_ambiguous`; byte-identical equal epochs select
`MANIFEST.A` deterministically. A future manifest payload therefore cannot be
bypassed by selecting an older epoch.

Each durable publication increments the selected epoch by exactly one and
targets the other slot. The selected slot is never modified by that attempt. A
failed new manifest publication may leave a temporary file or alter only the
previously non-selected slot; it MUST NOT alter the previously selected valid
slot.

### Generation Envelope

Every generation has exactly these top-level fields:

| Field | Type | Constraint |
| --- | --- | --- |
| `schema_version` | unsigned integer | Exactly `1` for the initial graph. |
| `generation` | generation metadata | Sequence and parent binding described below. |
| `local_identity` | local identity record or `null` | One atomic local identity record. |
| `remote_identities` | array of remote identity association records | At most 1024 records, in canonical record order. |

Generation metadata has exactly these fields:

| Field | Type | Constraint |
| --- | --- | --- |
| `sequence` | unsigned integer | Matches the filename and current manifest reference. |
| `parent_sequence` | unsigned integer or `null` | `null` only for the first generation; otherwise exactly the manifest parent sequence. |
| `parent_sha256` | string or `null` | `null` iff `parent_sequence` is `null`; otherwise exactly the manifest parent digest. |

The current generation metadata and selected manifest parent reference MUST
agree. Generation sequence is monotonic within one store. It is not a
timestamp, remote identifier, security epoch, or public revision.

### Protected Local Identity

The local identity record has exactly these fields:

| Field | Type | Constraint |
| --- | --- | --- |
| `certificate_chain_der` | array of base64 strings | Non-empty ordered DER certificate bytes. |
| `key_reference` | protected-key reference | Provider-versioned sealed material only. |
| `local_ski` | base64 string | Bounded opaque identifier bytes; never a filename or log field. |

The protected-key reference has exactly these fields:

| Field | Type | Constraint |
| --- | --- | --- |
| `provider_id` | string | Lowercase ASCII provider identifier matching `[a-z][a-z0-9.-]{0,63}`. |
| `provider_version` | unsigned integer | Nonzero provider contract version. |
| `sealed_blob` | base64 string | Opaque provider handle or sealed blob; never plaintext private-key bytes. |
| `certificate_spki_sha256` | string | Lowercase SHA-256 of the leaf certificate SubjectPublicKeyInfo DER. |

The owning runtime defines an internal protected-key capability with the
following provider-versioned operations; these operation names are contract
vocabulary, not public declarations:

- `probe(provider_id, provider_version)` attests that the provider can validate
  host or deployment binding, preserve non-exportability, unseal a signing
  capability, and compare its public key with certificate SPKI on this exact
  backend;
- `validate(sealed_blob, expected_spki)` validates the opaque blob, origin
  binding, provider version, and public-key binding without returning private
  bytes; and
- `unseal(sealed_blob)` returns only a non-exporting in-process signing
  capability. The runtime re-derives its public SPKI and compares it byte-for-byte
  with the leaf certificate and stored digest before open or commit succeeds.

Missing providers, unsupported versions, unavailable capabilities, wrong-host
or wrong-deployment blobs, public-key mismatch, and any path that would export
private bytes fail closed as `key_provider_unavailable` or
`key_material_unavailable`. A restore failure never generates a replacement
identity.

V1 has no portable plaintext-key variant and no `backup_excluded` metadata
claim. Backup behavior may be accepted only from a deployment-specific provider
whose runtime attestation proves the property and whose backend has dedicated
conformance tests; otherwise that deployment variant is deferred. Linux and
Darwin providers are independent implementations, and this contract does not
claim that the operating systems share a native protected-key primitive.

### Remote Identity Associations

Each remote identity association has exactly these neutral opaque fields:

| Field | Type | Constraint |
| --- | --- | --- |
| `record_id` | base64 string | Store-local opaque identifier used only for canonical ordering. |
| `remote_ski` | base64 string | Bounded opaque identifier bytes. |
| `remote_ship_id` | string | Bounded NFC UTF-8 value with no Unicode control or format characters. |

Records are unique by `record_id`, `remote_ski`, and `remote_ship_id` and sort
by decoded `record_id` bytes. Duplicate, empty, or non-canonically ordered
records are malformed. Identity values remain inside generation content and
are never used in paths, errors, metrics, or diagnostic formatting. V1 stores
no pairing, trust, quarantine, retry, or lifecycle policy. Later milestones may
add policy only through an explicit schema version and migration edge.

### Record Ownership

| Record | Durable representation owner | Semantic or mutation owner |
| --- | --- | --- |
| Certificate chain and protected-key reference | MSP-04A store | Internal identity owner; no public mutation surface. |
| Local SKI | MSP-04A store | Internal identity owner; the store does not derive protocol meaning. |
| Remote SKI and remote SHIP ID | MSP-04A association record | Later trust/lifecycle owner; MSP-04A only validates and persists opaque values. |
| Generation sequence, parent binding, manifest epoch, and digests | MSP-04A store | Store commit and integrity classification only. |

## Canonical JSON Profile

Every manifest envelope, decoded manifest payload, and generation MUST use this
exact profile:

1. Bytes are UTF-8 without a byte-order mark. Documents contain exactly one JSON
   value followed by one LF byte and no other leading, trailing, or
   insignificant whitespace.
2. Object keys are sorted recursively in lexicographic order by their UTF-8
   bytes. Schemas define array order; unordered input is rejected rather than
   silently sorted by a reader.
3. Integers use the shortest unsigned decimal representation with no sign or
   leading zero. Floating-point and exponent forms are forbidden.
4. All strings contain only Unicode scalar values. Fields that permit Unicode
   MUST already be NFC; readers never normalize. Unicode general categories
   `Cc` and `Cf` are forbidden in schema string values. ASCII-constrained fields
   additionally enforce their declared grammar.
5. The only emitted string escapes are `\"` for quotation mark and `\\` for
   reverse solidus. Solidus is not escaped. Control-character escapes and
   `\uXXXX` escapes are never emitted because control characters are forbidden
   and other Unicode scalars are emitted as literal UTF-8. `<`, `>`, `&`,
   U+2028, and U+2029 are not HTML-escaped.
6. Binary values use RFC 4648 standard-alphabet base64 with canonical padding:
   padding is present exactly when required and no whitespace or alternate
   alphabet is accepted. Readers decode and re-encode to prove byte equality.
7. Hex digests contain exactly 64 lowercase ASCII hexadecimal characters.
8. Readers reject duplicate keys, unknown fields, and any parsed document whose
   canonical re-encoding is not byte-for-byte equal to the original bytes.

The implementation MUST commit versioned golden vectors for an empty
generation, a populated generation, non-ASCII NFC and escaping cases, both
manifest slots with known checksums, and each standard-base64 padding length.
Negative vectors MUST demonstrate that semantically equivalent but
non-canonical bytes are rejected.

## Parsing And Bounds

Parsing is bounded before allocation and fail-closed:

- a manifest envelope is at most 16 KiB and its decoded payload at most 8 KiB;
- a generation file is at most 4 MiB;
- at most 128 recognized temporary or unreferenced generation entries may be
  present at open;
- JSON nesting depth is at most eight;
- a certificate chain contains at most 16 entries and at most 1 MiB decoded in
  total;
- a sealed provider blob is at most 256 KiB decoded;
- each SKI or record id is 1 through 128 decoded bytes; and
- a remote SHIP ID is 1 through 512 UTF-8 bytes.

The decoder rejects invalid UTF-8, duplicate keys, unknown fields, trailing
data, comments, non-integer numbers, negative or overflowing integers, invalid
or non-canonical base64, invalid NFC, disallowed Unicode categories, and any
value outside these limits. A new field requires a new version and migration
edge; readers never ignore it.

## Version And Migration Policy

Slot format, manifest payload version, generation schema version, and protected
key provider version are independent closed domains. V1 readers accept slot
format 1, manifest version 1, and generation schema 1 only.

The initial generation migration graph is the single vertex `v1`; no historical
on-disk format is implied. Future versions extend an explicit directed acyclic
graph. Every accepted older version MUST have exactly one path to the current
version. Branching paths, cycles, skipped mandatory versions, implicit
best-effort conversion, and downgrade migrations are forbidden.

Each migration edge is a pure deterministic transformation over a validated
selected generation. It performs no filesystem, network, clock, environment,
or random input. The result is validated against the target schema and key
provider before it is committed as a new generation whose exact parent is the
selected generation. Migration never edits existing generation or manifest
bytes. A failed migration leaves both selected manifest and current generation
unchanged.

Version handling is exact:

- current version: validate and load without rewriting;
- accepted older generation with one migration path: migrate through the normal
  durable commit state machine;
- older version without a path: `unsupported_legacy_version`;
- version greater than the reader's current version:
  `unsupported_future_version`; and
- an unsupported slot envelope version is `unsupported_future_version` when
  greater than 1 and `unsupported_legacy_version` otherwise.

Future-version state is not corruption. Open does not inspect or activate an
older manifest or parent generation after selecting a future-version epoch.

## One-Writer Contract

The runtime acquires one non-blocking, operating-system-backed exclusive lock
on `LOCK` and holds it for the store lifetime. Minimal root and `LOCK` safety is
verified before lock acquisition; child layout, manifests, generations, and
record content are not inspected first.

The implementation also prevents two store instances in one process from
owning the same root. If another process or local instance owns the lock, open
returns `writer_busy` immediately. It does not enumerate deep layout, read a
manifest or generation, create a temporary file, wait, steal, delete, rewrite,
or infer a stale owner from `LOCK`. Operating-system release after process
termination is the only stale-lock recovery. A platform without the required
lock primitive returns `lock_unavailable`.

## Open State Machine And Precedence

Open applies the following states in order. The first terminal result wins:

1. `open_path`: validate the configured path, select a platform backend, safely
   traverse the parent, and perform or resume the bounded bootstrap sequence.
2. `open_root_lock_safety`: verify only the opened root and `LOCK` descriptors,
   pathname-to-descriptor identity, exact ownership/mode/type/link count, ACL
   controls, and capabilities required to acquire and hold the lock.
3. `open_lock`: acquire the in-process guard and non-blocking process lock.
   `writer_busy` therefore precedes every deep-layout, manifest, generation,
   migration, and key-provider result.
4. `open_layout`: while locked, verify `generations/`, enumerate and validate the
   bounded fixed layout, and classify recognized temporary and orphan files
   without mutating or adopting them.
5. `open_select_manifest`: parse both slot envelopes independently, verify their
   checksums, and select the publication-valid slot with the greatest epoch. An
   exact empty bootstrap with no slot or generation may proceed to initial
   commit; an existing store with no selectable slot fails closed.
6. `open_current`: parse the selected payload, resolve only its fixed current
   reference, verify exact generation bytes and metadata, and apply version
   handling. A future version terminates here without inspecting older content.
7. `open_recovery_classification`: only when selected current bytes are missing
   or corrupt, validate the selected manifest's exact parent as an inactive
   recovery candidate. No records, store handle, or normal runtime state are
   returned from this state.
8. `open_key_capability`: for a valid current generation, probe, validate, and
   unseal every protected-key reference and verify certificate binding.
9. `open_migrate_or_return`: run the unique migration path through Commit or
   return the unchanged current in-memory state.

Deep layout errors cannot mask `writer_busy`; conversely, unsafe root or `LOCK`
objects are rejected before attempting to lock an attacker-controlled object.

## Commit State Machine And Durability

Commit requires the held lock and applies this separate precedence:

1. `commit_validate`: verify writer ownership, complete in-memory schema,
   canonical encodability, protected-key capabilities, next generation
   sequence, next manifest epoch, and exact parent binding before mutation.
2. `commit_pre_maintenance`: remove only recognized stale temporary files and
   unreferenced generations from earlier failed attempts, preserving every
   generation referenced by either publication-valid slot. Fsync each changed
   directory. Failure returns `maintenance_failed` with the selected manifest
   unchanged.
3. `commit_generation`: create a new `0600` temporary generation exclusively in
   `generations/`, write canonical bytes, reject short writes, fsync the file,
   atomically rename it to its immutable final name, and fsync `generations/`.
4. `commit_manifest_stage`: construct an epoch-plus-one manifest whose current
   reference binds the new generation and whose parent reference exactly equals
   the previously selected current. Write a new `0600` temporary envelope in
   the root, reject short writes, and fsync it.
5. `commit_manifest_publish`: atomically replace only the non-selected manifest
   slot and fsync the root directory. Completion of that directory fsync is the
   sole `commit_durable` publication point.
6. `commit_post_maintenance`: remove only recognized objects no longer
   referenced by either valid slot and fsync changed directories. Failure after
   durable publication returns `commit_applied_maintenance_failed`; the new
   commit remains authoritative, the handle stops normal use, and the caller
   must reopen instead of retrying the logical write.

All temporary files are on the same filesystem and in the same directory as
their atomic replacement target. Cross-filesystem rename, copy-and-delete
replacement, truncate-in-place, and write-in-place are forbidden.

Failure before atomic manifest replacement returns `commit_not_published`; the
previously selected valid slot remains byte-for-byte unchanged and
authoritative. Failure after atomic replacement but before successful root
directory fsync returns `commit_durability_unknown`. The process reports neither
success nor failure-as-unapplied, stops using the handle, and requires a fresh
Open to select the highest publication-valid epoch. No automatic retry occurs.

An interruption can leave only a recognized temporary file, an unreferenced
immutable generation, or an old/new complete non-selected manifest slot. Open
never adopts an orphan. Both possible manifest targets reference complete,
fsynced generation files because generation-directory durability precedes
manifest staging.

## Corruption And Inactive Recovery

Normal runtime use succeeds only from the current generation bound by the
selected highest-epoch manifest. If that current generation is missing, has a
hash mismatch, is non-canonical, has inconsistent parent metadata, or otherwise
fails current-schema validation, Open fails closed.

The exact parent reference in that same manifest MAY be validated to distinguish
`recovery_candidate_available` from `no_valid_current`. A recovery candidate is
inactive evidence only: its bytes are not returned as normal state, it is not
loaded by the runtime, no manifest is rewritten, and no trust, pairing,
lifecycle, or anti-rollback decision is made. Activation and anti-rollback
policy belong to MSP-04C.

The other manifest slot is used only by the epoch-selection rule for
crash-consistent publication. Once a highest publication-valid manifest is
selected, Open never chooses the lower epoch because current content is corrupt.
Future-version content also never takes the recovery-candidate path. The store
does not scan for or adopt unreferenced generations.

MSP-04A performs no automatic corruption quarantine, move, deletion, or
republish. Corrupt files remain untouched and sensitive. Only recognized stale
artifacts from interrupted commits are eligible for Commit maintenance, and
they are never interpreted as recovery content.

A newly bootstrapped root may initialize the canonical empty v1 generation and
return `opened_empty` only after its initial Commit is durable. Any manifest,
generation, unknown object, or non-bootstrap content makes this an existing
store and prevents empty initialization.

## Secret Handling

Certificate material, protected-key references, local SKI, remote SKI, remote
SHIP ID, remote identity records, and corrupt payloads are sensitive. The
implementation MUST satisfy all of these controls:

- secret values enter and leave the store only as in-memory values or opaque
  provider capabilities; plaintext private-key bytes never enter the schema;
- no secret or encoded secret appears in environment variables, command-line
  arguments, filenames, lock metadata, temporary names, metrics, traces, or
  process titles;
- errors contain a stable outcome and safe operation label only, without raw
  values, full paths, record ids, hashes of identity values, or nested decoder
  text that could echo input;
- default, debug, structured, and panic formatting of record and error types is
  redacted; no text-marshalling method exposes record content;
- logs may report the outcome label, schema version, generation sequence, and
  manifest epoch, but not record values, identity digests, certificate
  fingerprints, payload hashes, or an absolute store path; and
- test failures and fuzz output use synthetic fixtures and redacted summaries.

Protected material is never converted to a portable key for backup, migration,
diagnostics, or testing. Provider attestation is checked on every Open and
key-bearing Commit rather than persisted as a trusted metadata assertion.

## Deterministic Outcomes

Every operation returns exactly one internal outcome under its state-machine
precedence.

| Outcome | Meaning |
| --- | --- |
| `opened_empty` | A new empty v1 store was durably initialized. |
| `opened_current` | The selected current generation was loaded unchanged. |
| `opened_migrated` | One unique migration path produced a durable selected generation. |
| `recovery_candidate_available` | Current is unusable; the exact parent validates as inactive evidence, and no runtime state is returned. |
| `commit_durable` | New generation and manifest publication reached directory durability. |
| `commit_applied_maintenance_failed` | Manifest publication is durable, but post-publication cleanup failed; reopen is required. |
| `path_rejected` | Root input or descriptor-relative confinement failed. |
| `bootstrap_durability_unknown` | Root creation could not be proven durable. |
| `filesystem_capability_unavailable` | The platform/filesystem backend cannot prove every required primitive. |
| `permissions_rejected` | Descriptor ownership, exact mode, or ACL/additional-access validation failed. |
| `layout_rejected` | A symlink, identity mismatch, wrong type, hard link, unknown object, or invalid layout was found. |
| `writer_busy` | Another local writer owns the safely opened root. |
| `lock_unavailable` | Required one-writer locking cannot be enforced. |
| `manifest_ambiguous` | Equal highest epochs contain different manifest bytes. |
| `no_valid_manifest` | An existing store has no publication-valid manifest slot. |
| `unsupported_legacy_version` | No unique migration path exists from an older accepted domain. |
| `unsupported_future_version` | State uses a newer slot, manifest, or generation version. |
| `malformed_state` | Strict parsing or record validation failed. |
| `no_valid_current` | Selected current is invalid and its exact parent is absent or invalid. |
| `key_provider_unavailable` | Required provider/version/capability or attestation is unavailable. |
| `key_material_unavailable` | Protected material is wrong-host, invalid, non-unsealable, or certificate-mismatched. |
| `migration_failed` | A migration edge failed; manifest slots remain unchanged. |
| `maintenance_failed` | Pre-publication cleanup failed with selected state unchanged. |
| `commit_not_published` | A write failed before manifest-slot replacement; selected state is unchanged. |
| `commit_durability_unknown` | The target slot was replaced but root-directory fsync failed; reopen is required. |
| `io_failed` | A bounded non-publication filesystem operation failed. |

Errors with the same observable store state produce the same outcome regardless
of map iteration order, directory enumeration order, scheduler order, locale,
wall clock, or decoder wording. No automatic retry changes a terminal outcome.

## Test Obligations

The code issue starts with a CI-observed failing test or fixture before
implementation. Tests use pure parsers and a thin syscall adapter over real
temporary directories; they do not implement an in-memory mock filesystem.
The adapter exposes only the calls needed for deterministic short-write, fsync,
rename, lock, metadata, ACL, and process-boundary fault injection.

MSP-04A is not complete until these bounded suites pass with synthetic data:

1. Pure schema and canonicalization tests cover all golden vectors, recursive
   UTF-8-byte key ordering, exact escaping, NFC, standard padded base64,
   re-encode equality, duplicate/unknown keys, bounds, and manifest checksums.
2. Pure version-graph tests cover current v1, no-path legacy, future slot,
   manifest and schema versions, graph cycles/branches, and the rule that future
   versions never select an older generation.
3. Default Linux and Darwin filesystem tests use real temporary directories for
   root/child symlinks, traversal, wrong mode, hard links, non-regular objects,
   pathname-to-fd substitution, unknown entries, descriptor confinement,
   bootstrap fsync ordering, and capability-probe failure.
4. Cross-process lock tests use subprocesses against one real temporary root;
   exactly one process succeeds and each loser returns `writer_busy` before deep
   parsing or mutation. Separate in-process tests cover the local guard and
   process termination releases the operating-system lock without deleting
   `LOCK`.
5. Durability tests inject failure at every real syscall-adapter boundary and
   use subprocess termination at publication boundaries. They prove manifest
   epoch selection, preservation of the previously selected slot, no orphan
   adoption, `commit_durability_unknown`, and
   `commit_applied_maintenance_failed`.
6. Open/recovery tests cover malformed slots, equal-epoch ambiguity, corrupt
   current bytes, exact-parent validation as inactive evidence, invalid parent,
   no automatic activation or mutation, and interrupted empty initialization.
7. Protected-key tests use deterministic fake providers for unit outcomes and
   platform-specific provider capability lanes for host/deployment binding,
   wrong-host failure, Validate/Unseal availability, certificate SPKI binding,
   non-exportability, and attested deployment properties.
8. Migration tests cover pure deterministic transformation, before/after schema
   validation, failure without slot mutation, and normal two-slot publication
   when the first real edge is introduced.
9. Secret and determinism tests scan errors, logs, formatting, fuzz summaries,
   temporary names, environment, argv, metrics, and traces against every
   sensitive synthetic value and encoded form, then repeat schedules and faults
   to verify byte-identical output and one terminal outcome.

Wrong-owner setup, ACL states requiring elevated privileges, filesystem-type
coverage, and native protected-key integrations run only in explicitly labeled
privileged or capability-specific CI lanes. The default unprivileged lane MUST
not require changing file ownership or pretending that an unsupported host
capability exists. A missing required platform lane blocks claiming support for
that backend; it does not become a skipped passing assertion.

The authoritative repository CI and local race-enabled tests MUST pass. No live
device, network, protocol, consumer, or Home Assistant smoke test belongs to
MSP-04A.

## Explicit Exclusions

MSP-04A adds none of the following:

- public raw view or immutable raw-view export;
- lifecycle facade or availability authority;
- listener, outbound socket, discovery, or network behavior;
- pairing API, trust mutation API, revocation API, recovery activation API, or
  admin surface;
- semantic device id or cross-runtime identity;
- MCP tool or resource;
- GraphQL schema or resolver;
- Portal behavior;
- Home Assistant integration or add-on behavior;
- command routing, command execution, or other consumer behavior; or
- public API declaration, stable file-format promise, or protocol
  documentation.

Those surfaces remain assigned to later separately reviewed milestones. A
later implementation revision may be linked from this candidate only after it
exists; this document does not invent one.

[docs-issue]: https://github.com/Project-Helianthus/helianthus-docs-eebus/issues/14
[code-issue]: https://github.com/Project-Helianthus/helianthus-eebusreg/issues/20
[plan-row]: https://github.com/Project-Helianthus/helianthus-execution-plans/blob/97b22b342688a7fc3b1f0bc384f61f359aadf17f/multi-runtime-semantic-platform.locked/92-m0-issue-matrix.yaml#L849-L872
