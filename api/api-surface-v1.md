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

## Producer and Consumer Boundary

This milestone freezes the JSON representation and the synthetic corpus
invariants. The corpus validator checks strict JSON, normalized text, declared
field relationships, ordering, exclusions with precise markers, and fixture
boundaries. It does not parse Go and does not prove that a `type` or
`signature` string is legal or canonically spelled Go.

Before emitting this format, a future AST-backed producer must prove Go syntax,
canonical spelling, exported status, dependency visibility, and semantic
cross-field consistency. It must derive `kind`, `name`, `receiver`, `type`, and
`signature` from the same declaration. The corpus validator independently
rejects the string-level mismatches described below, but that portable check is
not a substitute for AST validation. Consumers may rely on the frozen
representation and corpus invariants only; they must not treat validation by
this repository as proof that a Go declaration exists.

Normative machine artifacts use strict UTF-8 JSON. Duplicate object keys,
non-UTF-8 input, and fields not declared by the closed schema are invalid.

## Schema Identity and Version

The stable schema identity is `helianthus.eebus.api-surface.v1`, the schema URI
is `urn:helianthus:eebus:api-surface:v1`, and `schema_version` is the integer
`1`. A document contains `schema_id`, `schema_version`, and `packages`. The
version is a JSON integer; JSON booleans are not integers for this contract.

The optional `fixture` object is reserved for this repository's synthetic
golden corpus. When present, it must state `synthetic: true` and
`runtime_claims: false`. Extracted API documents omit this fixture marker.

## Package Normalization

Each package is represented by the closed fields `path`, `name`, and
`symbols`. Package paths and names use Unicode Normalization Form C (NFC).
Paths use forward slashes, contain no empty, dot, dot-dot, or `internal`
package component, contain no whitespace or control character, and do not
include a local filesystem location. Package names are complete Go identifiers
and must not be Go keywords.

Source layout, file names, build-cache paths, comments, and formatting do not
participate in package identity. A package path may occur only once.

## Symbol Normalization

The only symbol kinds are `const`, `func`, `method`, `type`, and `var`. Symbol
names use Unicode Normalization Form C and must be exported Go identifiers. The
complete identifier is validated, including every subsequent Unicode letter or
decimal digit, and keywords are rejected.

Methods additionally carry the normalized receiver spelling. The allowed
receiver representation is an optional single `*`, an exported unqualified
base identifier, and an optional bracketed list of Go identifiers separated by
comma-space, for example `*Catalog` or `Catalog[T, U]`. Non-method symbols must
not carry a receiver.

Exact symbol identity is the tuple `(package path, kind, receiver, name)`, with
the receiver represented by the empty string for non-method declarations. Two
symbols with the same identity are invalid even when their types or signatures
differ.

## Kind and Type Normalization

`type` is the producer-supplied canonical Go type spelling for the declaration.
It is the declared type for constants and variables, the underlying declaration
form for types, and the receiver-free function type for functions and methods.
It is trimmed, single-line NFC text with no Unicode `Cc` control characters,
`Zl` line separators, `Zp` paragraph separators, or repeated spaces. The
corpus validator enforces those text properties but does not prove Go type
syntax.

Only public contract types may appear. The AST-backed producer is responsible
for excluding a declaration that exposes an implementation dependency type.
The corpus validator machine-checks the exact synthetic sentinel
`implementation.invalid/` in `type` and `signature`; it does not infer real
dependency visibility from arbitrary text.

## Signature Normalization

`signature` is the producer-supplied canonical declaration spelling without a
body, comments, source positions, or source formatting. It includes the
declaration kind and name, and includes the receiver for a method. It is
trimmed, single-line NFC text with no Unicode `Cc` control characters, `Zl`
line separators, or `Zp` paragraph separators, and one ASCII space where
separation is required.

The corpus validator enforces portable string-level consistency. For `const`,
`type`, and `var`, `signature` is exactly `kind`, one space, `name`, one space,
and `type`. For `func`, `type` begins with `func(` and `signature` inserts the
declared name after `func`. For `method`, it additionally inserts the exact
declared receiver in parentheses. Any mismatch is rejected. Legal Go syntax
and canonical Go spelling remain producer obligations.

Parameter names are omitted unless they are required to distinguish a legal Go
type expression. The AST-backed producer ensures equivalent source declarations
produce identical type and signature strings.

## Canonical Ordering

Packages are sorted by the bytewise UTF-8 tuple `(path, name)`. Symbols within
each package are sorted by the bytewise UTF-8 tuple `(kind, receiver, name)`,
using an empty receiver for non-method declarations. Sorting is ascending and
is performed after NFC normalization. Input order is never preserved.

## Exclusions

The corpus contract excludes:

- fields for formatting, comments, source positions, file names, or build
  metadata;
- every path with an internal package component;
- every unexported declaration;
- every method on an unexported receiver;
- the exact `implementation.invalid/` synthetic dependency sentinel;
- malformed, duplicate-keyed, non-NFC, duplicate-identity, or unsorted input.

Closed fields make source formatting, comments, positions, file names, and
build metadata unrepresentable. The corpus validator also rejects invalid Go
identifier strings, invalid receiver representations, empty package or symbol
collections, duplicate package paths, invalid path forms, control characters,
Unicode line or paragraph separators, invalid Unicode scalar values, and the
portable cross-field mismatches defined above. The future producer owns
exclusions that require Go semantic knowledge, including whether a real
dependency is implementation-only.

Exclusion is deterministic and applies to the complete declaration. A rejected
or excluded declaration is never partially represented.

## Synthetic Golden Fixtures

Files under `api/fixtures/v1/positive/` and `api/fixtures/v1/negative/` are
synthetic. Their package paths begin with
`example.invalid/helianthus/synthetic/`; no runtime symbol, package, or
availability claim is implied. Positive fixtures cover all symbol kinds,
normalized types and signatures, and canonical ordering.

Each negative fixture retains the valid schema identity, integer version,
`synthetic: true`, `runtime_claims: false`, and synthetic package-path prefix
while targeting its named rejection category. Even the malformed fixture begins
with a complete boundary-valid JSON document before its intentional trailing
syntax error.

The canonical duplicate-key fixture duplicates only `schema_id`, and both
occurrences equal `helianthus.eebus.api-surface.v1`. Duplicate-key recovery
retains every occurrence solely for boundary and publication checks. Every
occurrence of `schema_id`, `schema_version`, fixture markers, package
collections, and package paths must satisfy the synthetic no-runtime boundary;
a conflicting or shadowed invalid occurrence is rejected.

The validator emits deterministic categorical diagnostics. Diagnostics include
only the repository-relative artifact path and a category; they never echo
input values or absolute paths.

## Privacy and Source Restrictions

Extractor inputs must come from a publishable source. The corpus validator uses
an exact marker/category policy to avoid broad content inference. It scans the
raw UTF-8 JSON text and every decoded object-key and value occurrence, including
values shadowed by a duplicate key. The reproducible marker contract is:

- `private path` recognizes only these case-sensitive, regex-equivalent forms
  (non-capturing groups keep the examples from being path literals):
  `/(?:Users)/[^/\s]+/`, `/(?:home)/[^/\s]+/`,
  `/(?:tmp)/[^\s]+`, `/(?:var)/folders/[^\s]+`, and
  `[A-Za-z]:\\(?:Users)\\[^\\\s]+\\`. The first two require one
  non-empty user component and a following slash; the temporary forms consume
  one or more non-whitespace characters; the Windows form accepts either drive
  letter case but requires the literal component spelling `Users`.
- IPv4 candidates are word-bounded four dot-separated groups of one to three
  decimal digits. After standard-library address parsing, an address for which
  `is_private`, `is_loopback`, or `is_link_local` is true is `private network`;
  every other valid IPv4 address is `network address`. IPv6 candidates use the
  exact grammar `(?<![0-9A-Fa-f:])(?:[0-9A-Fa-f]{0,4}:){2,7}` followed by zero
  to four hexadecimal digits, an optional `%[A-Za-z0-9_.-]+` zone suffix, and
  `(?![0-9A-Fa-f:])`. After removing the zone suffix, every candidate accepted
  by standard-library address parsing is `network address` regardless of scope.
  Invalid IPv4 or IPv6 candidates do not match.
- `private identifier` recognizes a MAC address written as six two-hexadecimal
  groups with each separator independently a colon or hyphen, or as three
  four-hexadecimal groups separated by dots, in either case with no adjacent
  hexadecimal character. It also recognizes a contiguous fingerprint of 40 or
  more hexadecimal digits when neither adjacent character is hexadecimal.
- Assignment labels are case-insensitive under Python `re.IGNORECASE`, begin at
  a regex word boundary, and must be followed by zero or more Unicode
  whitespace characters and then `:` or `=`. The exact private identifier
  labels are `token`, `password`, `passphrase`, `credential`, `secret`, `api`
  plus zero or one `_`, hyphen, or ASCII-space separator plus `key`, `client`
  plus the same optional separator plus `secret`, `serial` plus the same
  optional separator plus `number`, and `account` plus the same optional
  separator plus one of `id`, `identifier`, or `data`.
- The `household data` category recognizes under the same case and word-boundary
  rules the label `household`, one or more `_`, hyphen, or ASCII-space
  separators, then `data` or `schedule`, followed by the assignment delimiter
  defined above. The `raw evidence` category recognizes `raw`, the same
  one-or-more separator rule, then `evidence`, followed by that delimiter.
- `source contamination` recognizes only the Python `re.IGNORECASE`,
  word-bounded marker grammars `vendor[_ -]restricted` and
  `restricted[ -]+source`. The first permits exactly one underscore, hyphen, or
  ASCII space; the second permits one or more ASCII spaces or hyphens in any
  sequence. No other phrase is inferred as a restricted-source marker.

Diagnostics contain only the repository-relative artifact path and category;
they never echo matched values or absolute temporary paths. The AST-backed
producer must additionally exclude private or restricted material that cannot
be identified reliably through this precise marker policy.

This contract remains canonical in `helianthus-docs-eebus/api`. Code
repositories consume or link to it and do not duplicate this specification.
