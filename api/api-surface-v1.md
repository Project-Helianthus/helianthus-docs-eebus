---
canonical_source: "Project-Helianthus/helianthus-docs-eebus:api/api-surface-v1.md"
owner_domain: "api"
license: "AGPL-3.0-only"
publication_status: "api-contract"
claim_status: "no-protocol-claims"
---

# eeBUS Go API Surface v1

This page defines the documentation-owned input contract for a future public
API extractor. It defines representation, derivation, normalization, and
compatibility fingerprinting only. No runtime symbol is asserted to exist, and
no protocol or consumer behavior is declared available.

## Producer and Consumer Boundary

This milestone freezes the JSON representation, producer algorithm, and
synthetic corpus invariants. The portable validator checks strict JSON, closed
field sets, normalized text, identifier rules, type-parameter uniqueness,
receiver resolution and arity, declaration identity, cross-field signature
derivation, import structure and identity, ordering, exact exclusions,
publication markers, and fixture boundaries. It does not parse Go.

Before emitting this format, a future AST-backed producer must prove Go syntax
and apply the normative selection, qualifier allocation, and rendering
algorithm below. It must also prove `go/constant.Value.ExactString` and
source-value correctness, generic constraints and cross-parameter references,
defined and alias declarations, exported dependency visibility, and semantic
consistency. It derives every field for a symbol from one type-checked
declaration. Proving import use and completeness is producer-owned. Portable
validation checks import structure, ordering, uniqueness, and path rules only;
it is not proof that a Go declaration or import exists. Consumers may rely on the frozen
representation and corpus invariants only.

Normative machine artifacts use strict UTF-8 JSON. Duplicate object keys,
non-UTF-8 input, JSON constants outside RFC 8259, nulls, and fields not declared
by the closed schema are invalid.

The portable maximum machine-document nesting depth is 64 containers. The root
object has depth 1; every object or array entered outside a JSON string adds 1;
scalars add 0. The complete UTF-8 text, including trailing content, is checked
non-recursively before JSON decoding, duplicate-key detection, decoded marker
walking, or schema walking. Depth 64 is accepted and depth 65 is rejected as
`maximum nesting depth`. Decoder recursion and numeric-conversion failures are
also converted to deterministic category-only diagnostics without a traceback.

## Schema Identity and Version

The stable schema identity is `helianthus.eebus.api-surface.v1`, the schema URI
is `urn:helianthus:eebus:api-surface:v1`, and `schema_version` has the constant
integer value `1`. The v1 designation identifies the initial version of this
contract.

The machine contract is representation-strict at this identity boundary:
producers and consumers must use the single JSON integer token `1`. Decimal or
scientific spellings such as `1.0` and `1e0`, and JSON booleans, are rejected
even when a general JSON Schema implementation would consider a numeric value
equivalent to the constant.

The representation-level schema keeps `fixture` optional because it describes
both extracted documents and this repository's synthetic golden corpus. In the
corpus it has exactly `synthetic: true` and `runtime_claims: false`. Extracted
API documents omit `fixture`.

The portable validator's default document mode validates extracted output:
`python3 scripts/validate_api_surface_v1.py --document <path>`. In that mode,
any `fixture` field is rejected as `fixture forbidden in extracted document`,
and ordinary public package paths are accepted. The explicit `--corpus`
document mode, and the repository corpus gate, require the exact closed fixture
metadata and the `example.invalid/helianthus/synthetic/` prefix for every
package and imported package path. These modes are mutually exclusive trust
boundaries over the same representation schema.

## Package Normalization

Each package has exactly `path`, `name`, `imports`, and `symbols`. `imports` is
required and always present, including an empty array. Each entry is the closed
object `{qualifier,path}`. A qualifier uses the portable ASCII Go identifier
subset `[A-Za-z_][A-Za-z0-9_]*`, is not a Go keyword, and cannot be the blank
identifier `_`. An imported path follows the same rules as the current package
path, cannot contain an `internal` component, and cannot equal the current
package path. Qualifiers are unique within a package, and imported paths are
independently unique within a package.

Package and imported paths use Unicode Normalization Form C (NFC), forward
slashes, no empty, dot, dot-dot, or `internal` component, and no whitespace or
control character. They cannot start or end with `/` or contain `\`. Windows
drive-absolute forms beginning with one uppercase or lowercase ASCII letter
followed by `:/` or `:\` are invalid. Colons in otherwise valid package/import
path strings remain permitted when they do not form that leading drive-absolute
prefix. Package names use the portable ASCII Go identifier subset and must not
be Go keywords.

Source layout, file names, build-cache paths, comments, and formatting do not
participate in package identity. A package path may occur only once.

## Normative Go Producer Algorithm

### Type-checking and declaration selection

The producer operates on one successfully type-checked `go/types.Package` and
its matching `go/ast` and `go/types.Info` for one explicit build configuration.
The module's selected files, build tags, GOOS, GOARCH, and Go language version
are producer inputs, not document fields. Packages from different build
configurations are separate producer runs and are never unioned. The reference
facility baseline is the Go 1.24 `go/types` API with `*types.Alias` enabled;
newer toolchains are conforming only when they emit the same v1 text. Generic
aliases require a package language version that permits them. No `go/format`,
`go/printer`, source import spelling, or source position contributes output.

For each package, inspect `types.Package.Scope()` and select each object whose
parent is that package scope, whose name is exported under the ASCII v1 rule,
and whose dynamic type is `*types.Const`, `*types.Var`, `*types.TypeName`, or a
receiver-free `*types.Func`. A multi-name `const` or `var` declaration produces
one symbol per selected object. `TypeName.IsAlias()` selects `type_form: alias`;
all other selected type names are `defined`. For every selected defined
`*types.Named`, inspect its declared methods with `Named.NumMethods` and include
each exported method. Do not use a method set: promoted methods are not emitted.
Methods of aliases, methods on unselected or unexported receiver bases, local
declarations, fields as standalone symbols, builtins, instantiated synthetic
objects, and compiler-generated wrappers are not emitted.

For a selected package function, declaration `type_parameters` come from
`Signature.TypeParams()` in index order. For a selected defined type they come
from `Named.TypeParams()`, and for a selected alias they come from
`Alias.TypeParams()`, again in index order. A method cannot declare independent
type parameters; a non-empty `Signature.TypeParams()` on a method is rejected.
Receiver-bound type parameters are handled separately below and never become a
method `type_parameters` field.

The AST declaration is used to associate an object with its source declaration
and to prove alias form and constant source correctness; semantic types always
come from the matching `go/types` object. If this association is missing or
ambiguous, or a selected declaration exposes a non-public implementation
dependency, reject the complete declaration. Never reconstruct a declaration
from source tokens alone.

### Canonical package qualifiers

First walk every semantic type that will be rendered in `type` or `constraint`.
Collect exactly the distinct non-current packages referenced by named or alias
type identities; also treat a `*types.Basic` whose kind is
`types.UnsafePointer` as package path and declared name `unsafe`. Do not expand
the underlying type of a named occurrence merely to collect imports. Type
arguments, alias right-hand sides
when those right-hand sides are being rendered, struct fields, interface
elements, function parameters/results, receiver-free method signatures, and
constraints are walked recursively. Exact constant values and derived
signatures introduce no additional imports.

For each collected path, take the package's declared `types.Package.Name`, not
any source import alias. If that name is a permitted non-blank ASCII Go
identifier, it is the allocation base; otherwise the base is `pkg`. Before
allocation reserve `_`, every name in `types.Universe`, every emitted
package-scope declaration name, and every retained declaration or receiver
type-parameter name. Sort all collected packages by the bytewise UTF-8 tuple
`(base, full import path)`. In that order allocate the first identifier not in
the reserved or already allocated sets from `base`, `base_2`, `base_3`, and so
on. Testing availability is global to the package and suffix search starts at 2
for every collision. Thus a real declared name such as `shared_2` can itself
force a later suffix. Source aliases, dot imports, file order, and import
declaration order are ignored. Blank imports cannot be referenced by a
selected type and are absent.

`imports[]` is exactly this path-to-allocated-qualifier map, then sorted by the
normal import ordering rule. Every non-current package selector in every
`type`, constraint, and derived signature uses that allocated qualifier, and
every `imports[]` entry must be used by at least one such semantic type. The
same path always has the same qualifier throughout one package. An unused,
missing, differently qualified, or source-alias-derived entry is a producer
error. The portable schema admits the allocation grammar, while the portable
validator intentionally cannot prove type-text use or package declared names.

### Canonical semantic type renderer

Render recursively from `go/types` values using the allocated qualifier
function. `types.TypeString` with that qualifier may be used only where its
result is byte-for-byte identical to these rules. Unsupported or invalid type
nodes reject the declaration.

- A `*types.Basic` is `Basic.Name()` (`bool`, `int`, `string`, the other
  numeric builtins, or an untyped name). This deliberately normalizes source
  `byte` and `rune` occurrences to `uint8` and `int32`; untyped rune constants
  remain `untyped rune`. If `Basic.Kind()` is `types.UnsafePointer`, ignore
  `Basic.Name()` and render the qualifier allocated to import path `unsafe`
  followed by `.Pointer`, including any collision suffix.
- A `*types.Named` or `*types.Alias` occurrence is `Name` for the current or
  universe package and `qualifier.Name` otherwise. Non-empty type arguments
  follow as `[T, U]`, rendered recursively. Alias identity is preserved at an
  occurrence; it is expanded only when rendering that alias declaration's
  `type` field.
- A type parameter is its declared object name. Declaration type-parameter
  names are retained because constraints and types refer to them. Its
  constraint is rendered separately with this same renderer.
- Pointers, arrays, slices, and maps are `*T`, `[N]T`, `[]T`, and `map[K]V`.
  `N` is the base-10 `types.Array.Len()` value with no leading sign or zero
  padding. Channels are `chan T`, `chan<- T`, or `<-chan T` for send/receive,
  send-only, or receive-only direction.
- A non-empty struct is `struct{ F T; Embedded; G U "tag" }`; an empty struct
  is `struct{}`. Preserve field declaration order because it is semantic.
  Render every non-embedded field name and type separately, even when source
  names shared one type expression. Render an embedded field as only its type.
  Omit an empty tag; otherwise append one space and `strconv.Quote` of the exact
  `types.Struct.Tag` string.
- Complete a `*types.Interface` before rendering. Enumerate only
  `NumExplicitMethods`/`ExplicitMethod`; each explicit method renders as `Name`
  followed by its receiver-free signature with the leading `func` removed.
  Enumerate `NumEmbeddeds`/`EmbeddedType` separately and render each embedded
  type as a type. Sort all rendered explicit-method and embedded-type elements
  by bytewise UTF-8 text, then join them with `; `.
  The results are `interface{}` or `interface{ Element; Method(T) U }`.
  A `*types.Union` renders each term as optional `~` plus its type, sorts terms
  by bytewise UTF-8 text, and joins them with ` | `.
- A signature is `func(P)` followed by its results. Parameter and result names
  are always omitted, whether a source list is named, unnamed, or grouped.
  Parameters are joined with `, `. For a variadic signature, render
  the last slice parameter as `...E`; any other variadic shape is rejected.
  Zero results append nothing, one result appends one space and its type, and
  two or more append ` (` plus comma-space joined types plus `)`. Signature
  type parameters are not rendered here because package-function declaration
  parameters have their own ordered field. Function types nested in other
  types use the same name-omitting signature rule.

For a defined type declaration, `type` is the rendering of
`Named.Underlying()`. For an alias it is the rendering of `Alias.Rhs()`. For a
variable or constant it is the rendering of the object's semantic type, except
that the six contract untyped names use their exact documented spelling. For a
function or method it is a copy of its `*types.Signature` with receiver and
signature type parameters omitted, rendered as above.

Declaration `type_parameters` retain the declared order and names and render
each constraint by the same rules. A method receiver is derived from the
declared receiver type after stripping one optional pointer. The remainder must
be a `*types.Named` whose `Origin()` is the selected local defined type. Its
type-argument count and `Signature.RecvTypeParams()` count must both equal the
base declaration's `Named.TypeParams()` count, and each receiver type argument
must be the receiver type parameter at the same index; otherwise reject the
method.

For a generic method, build a substitution map keyed by `*types.TypeParam`
object identity. Receiver parameter at index `i` maps to the base declaration
parameter name at index `i`. While rendering every parameter, result, and
nested type reachable from that method signature, a type-parameter occurrence
consults this map before using its own object name. This makes receiver binding
spelling irrelevant even when it is used in the method type. `base` is the
selected origin name, `pointer` records the stripped pointer, and
`receiver.type_parameters` contains the base declaration names in order.
Source receiver variable names and receiver binding names are discarded. For
example, source `func (box *Box[R]) Put(value R) R` on `type Box[T any]`
emits `{"base":"Box","pointer":true,"type_parameters":["T"]}` and type
`func(T) T`, from which the normalized signature is
`func (*Box[T]) Put(T) T`.

Finally derive `signature` only from the normalized fields as specified below,
sort imports and symbols, and validate the complete document. Because
`signature` is derived and removed from the compatibility projection, its type
selectors must exactly repeat the selectors already represented by `type`,
constraints, and `receiver`. `imports[]`, all normalized type text, receiver
objects, declaration parameters, and symbol ordering remain in the projection
and therefore participate in the compatibility fingerprint.

## Symbol Normalization

`symbols` is a `oneOf` union of five closed object shapes. Every shape requires
`kind`, `name`, `type`, and `signature`; no field accepts null.

| Kind | Additional required fields | Meaning |
|---|---|---|
| `const` | `value_kind`, `value` | Semantic constant type and exact value |
| `var` | none | Package variable |
| `type` | `type_form`, `type_parameters` | Defined type or alias |
| `func` | `type_parameters` | Package function |
| `method` | `receiver` | Method with a structured receiver |

`value_kind` is one of `bool`, `string`, `int`, `float`, or `complex` and
records the structural `go/constant` kind. The semantic constant types include
`untyped bool`, `untyped rune`, `untyped int`, `untyped float`,
`untyped complex`, and `untyped string`; an untyped rune has structural
`value_kind` `int`.

`type_form` is `defined` or `alias`. Every type and function has an
always-present ordered `type_parameters` array, including an empty array for a
non-generic declaration. Each parameter is the closed object `{name,
constraint}`. Names are unique within the declaration.

A method has no declaration-level `type_parameters` field. Its `receiver` is
the closed object `{base,pointer,type_parameters}`. `base` is an exported,
unqualified portable ASCII identifier, `pointer` is a JSON boolean, and
`type_parameters` is an always-present ordered array of unique portable ASCII
identifiers. The base must resolve to a type declaration in the same package,
and receiver arity must equal that declaration's type-parameter arity.

Package-scope declaration identity is `(package path, name)`, independent of
kind. A constant, variable, type, and function therefore cannot reuse the same
package-scope name. Method identity is `(package path, receiver.base, name)`,
independent of pointer choice, receiver parameter names, or receiver spelling.

All package, symbol, type-parameter, and receiver identifiers use the portable
ASCII Go identifier subset and exclude Go keywords. Exported declaration and
receiver names begin with ASCII `A-Z`. This deliberate v1 portability
constraint never consults the Python Unicode database for identifier
classification. Unicode remains permitted in normalized type, constraint,
value, and signature text where identifier classification is not inferred.

## Kind and Type Normalization

`type` is the producer-supplied canonical semantic Go type. For a constant it
is the semantic type, including the six untyped forms listed above. For a
variable it is the declared type. For a type declaration it is the defined
underlying type or alias target without the declaration name, parameters, or
equals sign. For functions and methods it is the receiver-free function type.

`type`, constraints, and non-constant signatures are trimmed, single-line NFC
text with no Unicode `Cc` control characters, `Zl` line separators, `Zp`
paragraph separators, or repeated spaces. Constant `value` and `signature`
remain trimmed and reject actual `Cc`, `Zl`, `Zp`, and surrogate code points,
but deliberately skip NFC and repeated-space normalization. This preserves the
ExactString byte sequence, including decomposed non-NFC Unicode, in both
`value` and the value-derived substring of `signature`. Exact derived-signature
equality rejects any change outside or inside that duplicated value. The
portable validator enforces those representation properties but does not prove
Go syntax or constraint meaning.

`value` is exactly `go/constant.Value.ExactString`. It remains a JSON string
for every constant class, even when it represents a boolean or number. The
future AST producer proves ExactString and source-value correctness; the
portable validator enforces the field shape, untyped type-to-kind mapping, and
signature derivation.

Only public contract types may appear. The future producer excludes declarations
that expose implementation dependencies. The portable validator checks the
exact synthetic sentinel `implementation.invalid/` in type-bearing fields and
signatures; it does not infer real dependency visibility from arbitrary text.

## Signature Normalization

`signature` is a deterministic, source-like declaration without a body,
comments, source positions, or source formatting. It is derived as follows:

- untyped constant: `const Name = Value`;
- typed constant: `const Name Type = Value`;
- variable: `var Name Type`;
- defined type: `type Name[parameters] Type`;
- alias: `type Name[parameters] = Type`;
- function: insert `Name[parameters]` after `func` in the receiver-free
  function type;
- method: render the structured receiver exactly, then insert the method name
  after it in the receiver-free function type.

Empty parameter lists omit brackets. Declaration parameters render in order as
`Name Constraint`, separated by comma-space. Receiver parameters render only
their ordered names, so a generic receiver is `Base[T, U]`; `pointer: true`
adds the single leading `*`. The value is intentionally duplicated in constant
signatures so a signature is never an invalid pseudo-declaration.

## Compatibility Fingerprint

The compatibility projection is the complete document after removing the root
`fixture` field and every symbol's derived `signature` field. No other field is
removed: package-level `imports`, including each qualifier-to-path identity,
participate in the projection and fingerprint. Package, import, and symbol
arrays remain in canonical order, and type-parameter arrays retain declaration
order. Object member input order does not participate.

Fingerprinting occurs only after validation has accepted `schema_version` as
the exact JSON integer token `1`. Alternate numeric spellings such as `1.0` and
`1e0` fail validation and are not canonicalized for fingerprinting. Serialize
the projection as UTF-8 JSON with keys sorted by Unicode code point,
`ensure_ascii` disabled, no insignificant whitespace, and separators `,` and
`:`. The compatibility fingerprint is the lowercase hexadecimal SHA-256 digest
of those bytes. The fingerprint is computed externally; v1 has no
self-referential hash field. Corpus tests pin known digests for both positive
fixtures and prove that changing only `fixture` or a correctly derived
`signature` does not change the digest. Fingerprinting refuses any package path
rejected by package-path validation and returns no digest for that document.

The fingerprint is an integrity summary of the complete compatibility
projection and changes for any projected data change, whether additive or
breaking. Hash inequality alone is not the compatibility classifier;
compatibility classification is identity-aware under the v1 evolution policy.

## Canonical Ordering

Packages are sorted by the bytewise UTF-8 tuple `(path, name)`. Imports within a
package are sorted by the bytewise UTF-8 tuple `(qualifier, path)`. Symbols
within each package are sorted by the bytewise UTF-8 tuple `(kind,
receiver.base or empty, name)`. Sorting is ascending and occurs after NFC
normalization of fields for which NFC is required. Pointer choice and receiver
parameter spelling do not participate in ordering.

## Exclusions

The corpus excludes formatting, comments, source positions, file names, build
metadata, internal package paths, unexported declarations, methods on
unexported or unresolved receivers, implementation dependency types,
duplicate identities, duplicate type-parameter names, malformed or duplicate
JSON keys, non-NFC text outside ExactString-derived constant data, nulls,
unknown fields, and non-canonical ordering.

Exclusion is deterministic and applies to the complete declaration. A rejected
or excluded declaration is never partially represented.

## Synthetic Golden Fixtures

Files under `api/fixtures/v1/positive/` and `api/fixtures/v1/negative/` are
synthetic. Their package paths begin with
`example.invalid/helianthus/synthetic/`; no runtime symbol, package, or
availability claim is implied. Imported package paths use the same synthetic
prefix. Positive fixtures cover all five kinds, typed and all untyped constant
classes including rune, exact large values, decomposed Unicode ExactString
data, generic defined and alias types, cross-parameter function constraints,
value and pointer generic receivers, and canonical package, import, and symbol
ordering. `canonical-go-rendering.json` is the producer golden vector. Its two
paths ending in `collision/a` and `collision/b` both model packages whose
declared package name is `shared`; source aliases `left` and `right` therefore
disappear and the allocated qualifiers are `shared` and `shared_2`. Its
`Normalize` golden vectors include equivalent all-named and all-unnamed
parameter/result variants, but the golden type omits every parameter/result
name. Its source receiver binds `R` for the declaration parameter `T`, while
the receiver object, method type, and signature use the canonical declaration
name `T`. The fixture also pins aliases, defined
types, builtins, pointers, arrays, slices, maps, all channel directions,
structs, interfaces, functions, variadics, embedded types, type parameters,
constraints, and generic receivers.

The input/output facts represented by that fixture are exact golden vectors:

| Type-checked source fact | Canonical machine fact |
|---|---|
| `import left "example.invalid/helianthus/synthetic/collision/a"` and `import right "example.invalid/helianthus/synthetic/collision/b"`, where both imported declarations say `package shared` | `imports` maps the first full path to `shared` and the second to `shared_2`; type text contains neither `left` nor `right` |
| `func Normalize[T interface{ ~string \| ~int }](first left.Value, second right.Value, rest ...T) (result T, err error)` | `type` is `func(shared.Value, shared_2.Value, ...T) (T, error)` and the sorted constraint is `interface{ ~int \| ~string }` |
| `func Normalize[T interface{ ~string \| ~int }](left.Value, right.Value, ...T) (T, error)` | The identical canonical `type`; only the declaration name and type-parameter fields remain named |
| `type Aggregate[T interface{ ~string \| ~int }] ...` with `func (a *Aggregate[R]) Apply(value left.Value, rest ...R) (result R, updates <-chan right.Value)` | receiver is `{base: Aggregate, pointer: true, type_parameters: [T]}`, `type` is `func(shared.Value, ...T) (T, <-chan shared_2.Value)`, and the signature uses `*Aggregate[T]` |

The exact negative allowlist has ten filenames. Each fixture retains the valid
schema identity, canonical version token, synthetic marker, no-runtime marker,
and synthetic package prefix while producing exactly its approved diagnostic
set. The duplicate-key fixture duplicates only `schema_id`, with equal values;
strict recovery retains every occurrence for boundary and publication checks.

Ordinary machine artifacts contain exactly one complete JSON value followed
only by JSON whitespace. The canonical malformed fixture alone contains one
complete, boundary-valid JSON value followed by the exact remainder `\n!\n`.
Any other tail, a second JSON value, or escaped content in a tail is a boundary
and publication failure. Diagnostics are deterministic, repository-relative,
category-only, and never echo input values or absolute paths.

## V1 Evolution Policy

Compatibility classification is identity-aware. An additive data change adds a
new package identity or a new symbol identity while every existing identity
projection stays byte-for-byte and semantically equivalent. Import-map additions
are additive only when used exclusively by new identities and do not change the
resolution or projection of any existing identity.

A breaking data change removes an existing identity or modifies the projection
of an existing identity. This includes qualifier-to-path mapping changes that
affect the resolution or projection of existing identities. The additive and
breaking classes are non-overlapping: any projected change that affects an
existing identity is breaking, while an additive change is confined to new
identities.

Any schema change, including a field, requiredness, or enum change, and any
normalization, identity, order, compatibility-projection, fingerprint, or
diagnostic-contract change requires v2 and parallel artifacts. The v1 schema,
reference, validator, and corpus remain available beside the new version.

Only nonnormative clarification and validator fixes that enforce
already-normative behavior without changing valid-document or fingerprint
semantics may patch v1. v1 is additive-only as a contract; there is no silent
redefinition.

## Privacy and Source Restrictions

Both validators import `scripts/machine_publication_policy.py` for strict,
duplicate-preserving JSON decoding, decoded key and value traversal, malformed
tail classification, and machine publication markers. The shared policy scans
raw UTF-8 JSON and every decoded occurrence, including keys, strings, numeric
data, shadowed duplicate values, and escaped content. When no decoded structure
is available, fingerprint detection remains fail-closed over the complete raw
text. When decoding succeeds, the raw scan still applies every non-fingerprint
marker class to the complete text, while fingerprint classification uses the
decoded structure, every original numeric token spelling, and any undecoded
trailing content instead of blindly classifying digit runs in the JSON
rendering. Numeric classification never relies on a reformatted decoded value;
valid numbers outside the decoder's representable range fail closed without
exposing their value in diagnostics.

The shared marker contract recognizes the documented private path forms,
private-artifact location/reference/filename/hash/identifier/retained labels,
PEM block markers, MAC addresses, contiguous hexadecimal fingerprints of
at least 40 digits, and every repository credential/identifier assignment
label: token, password, passphrase, credential, secret, API key, client secret,
private key, account ID/identifier/data, fingerprint, MAC address, serial,
local identity, stable peer identifier, pairing history, and raw or ordinary
SKI/SHIP ID forms. It also recognizes household-data/schedule labels,
raw-evidence labels, the explicit `vendor[_ -]restricted` and
`restricted[ -]+source` grammars, restricted-vendor document/source/material
forms, restricted-paraphrase forms, restricted document/source keys, and a
`source_class` value of `restricted` or `vendor_restricted`, plus valid IPv4
and IPv6 candidates.

Decoded object policy is pair-aware: credential, private-artifact, household,
raw-evidence, restricted-document, and source-class keys are classified with
their values, including every duplicate or shadowed pair. Raw text and decoded
strings are both checked, so JSON escapes in keys or values do not bypass a
category. If boundary-invalid trailing content begins with one or more complete
JSON values, each value is decoded iteratively and checked as well; malformed
tail bytes still receive the raw scan. Matched keys and values are never copied
into diagnostics.

Full fingerprints remain prohibited in every ordinary decoded key, string,
number, package or import path, symbol name, type, constraint, receiver,
signature, and constant representation, including duplicate or shadowed data.
The only context-aware fingerprint diagnosis exemption is the exact decimal
integer occurrence in `packages[*].symbols[*].value`, and the identical suffix
occurrence in that symbol's exactly derived source-like `signature`, when the
closed symbol object has `kind` equal to `const`, `value_kind` equal to `int`,
and `value` matches `[+-]?[0-9]+` using ASCII digits. Any duplicate key in the
object or an ancestor disables the exemption. The exemption suppresses only a
fingerprint diagnosis for those two exact spans: private paths, network
addresses, credentials, source contamination, and every other marker class
still scan the complete value and signature. Hexadecimal-looking text,
malformed decimal text, float, complex, and string constants,
all-digit data in any other slot, and a signature not exactly derived from the
same value are not exempt.

IPv4 candidates use the exact pattern
`(?<![0-9.])(?:[0-9]{1,3}\.){3}[0-9]{1,3}(?![0-9.])`. Octets are parsed
manually as decimal values from zero through 255, including leading-zero
spellings. The fixed private table is exactly `10/8`, `100.64/10`, `127/8`,
`169.254/16`, `172.16/12`, and `192.168/16`. Every other valid IPv4 candidate,
including reserved or special-use space, is classified as `network address`.
Classification never uses `ipaddress.is_private`.

IPv6 candidates use the exact shared grammar with an optional
`%[A-Za-z0-9_.-]+` zone suffix. After removing that suffix, every candidate
accepted as IPv6 by the standard library is `network address`, regardless of
scope. General Markdown publication policy remains repository-specific and is
not part of this machine contract.

This contract remains canonical in `helianthus-docs-eebus/api`. Code
repositories consume or link to it and do not duplicate this specification.
