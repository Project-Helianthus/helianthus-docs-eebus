---
canonical_source: "Project-Helianthus/helianthus-docs-eebus:api/api-surface-v1.md"
owner_domain: "api"
license: "AGPL-3.0-only"
publication_status: "api-contract"
claim_status: "no-protocol-claims"
---

# eeBUS Go API Surface v1

This page defines the documentation-owned input contract for a future public
API extractor. It defines representation and normalization only. No runtime
symbol is asserted to exist, and no protocol or consumer behavior is declared
available.

Normative machine artifacts use strict UTF-8 JSON. Duplicate object keys,
non-UTF-8 input, and fields not declared by the closed schema are invalid.

## Schema Identity and Version

The stable schema identity is `helianthus.eebus.api-surface.v1`, the schema URI
is `urn:helianthus:eebus:api-surface:v1`, and `schema_version` is the integer
`1`. A document contains `schema_id`, `schema_version`, and `packages`.

The optional `fixture` object is reserved for this repository's synthetic
golden corpus. When present, it must state `synthetic: true` and
`runtime_claims: false`. Extracted API documents omit this fixture marker.

## Package Normalization

Each package is represented by the closed fields `path`, `name`, and
`symbols`. Package paths and names use Unicode Normalization Form C (NFC).
Paths use forward slashes, contain no empty, dot, dot-dot, or `internal`
package component, and do not include a local filesystem location.

Source layout, file names, build-cache paths, comments, and formatting do not
participate in package identity. A package path may occur only once.

## Symbol Normalization

The only symbol kinds are `const`, `func`, `method`, `type`, and `var`. Symbol
names use Unicode Normalization Form C and must be exported Go identifiers.
Methods additionally carry the normalized receiver spelling; the receiver's
base type and the method declaration must both be exported. Non-method symbols
must not carry a receiver.

Exact symbol identity is the tuple `(package path, kind, receiver, name)`, with
the receiver represented by the empty string for non-method declarations. Two
symbols with the same identity are invalid even when their types or signatures
differ.

## Kind and Type Normalization

`type` is the canonical Go type spelling for the declaration. It is the
declared type for constants and variables, the underlying declaration form for
types, and the receiver-free function type for functions and methods. It is
trimmed, single-line NFC text with no tabs or repeated spaces.

Only public contract types may appear. If a declaration exposes an
implementation dependency type, the entire declaration is excluded. The
`implementation.invalid/` package prefix in the negative corpus is a synthetic
sentinel for this rule; it does not identify a real dependency.

## Signature Normalization

`signature` is the canonical declaration spelling without a body, comments,
source positions, or source formatting. It includes the declaration kind and
name, and includes the receiver for a method. It is trimmed, single-line NFC
text with one ASCII space where separation is required.

Parameter names are omitted unless they are required to distinguish a legal Go
type expression. Equivalent source declarations therefore produce identical
type and signature strings.

## Canonical Ordering

Packages are sorted by the bytewise UTF-8 tuple `(path, name)`. Symbols within
each package are sorted by the bytewise UTF-8 tuple `(kind, receiver, name)`,
using an empty receiver for non-method declarations. Sorting is ascending and
is performed after NFC normalization. Input order is never preserved.

## Exclusions

The contract excludes:

- formatting, comments, source positions, file names, and build metadata;
- every internal package;
- every unexported declaration;
- every method on an unexported receiver;
- every declaration that leaks an implementation dependency type;
- malformed, duplicate-keyed, non-NFC, duplicate-identity, or unsorted input.

Exclusion is deterministic and applies to the complete declaration. A rejected
or excluded declaration is never partially represented.

## Synthetic Golden Fixtures

Files under `api/fixtures/v1/positive/` and `api/fixtures/v1/negative/` are
synthetic. Their package paths begin with
`example.invalid/helianthus/synthetic/`; no runtime symbol, package, or
availability claim is implied. Positive fixtures cover all symbol kinds,
normalized types and signatures, and canonical ordering. Each negative fixture
is bound to one named rejection category.

The validator emits deterministic categorical diagnostics. Diagnostics include
only the repository-relative artifact path and a category; they never echo
input values or absolute paths.

## Privacy and Source Restrictions

Extractor inputs must come from a publishable source. Machine artifacts must
not contain private identifiers, credentials, account data, household data,
absolute source paths, network addresses, full fingerprints, raw evidence, or
non-publishable source contamination. Failure diagnostics do not reflect those
values.

This contract remains canonical in `helianthus-docs-eebus/api`. Code
repositories consume or link to it and do not duplicate this specification.
