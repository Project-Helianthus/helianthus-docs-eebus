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
receiver resolution to defined types, canonical receiver parameter names and
arity, declaration identity, cross-field signature derivation, import structure
and dependency classification, ordering, canonical exact numeric shapes, exact
exclusions, publication markers, and fixture boundaries. It does not parse Go.

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
object `{dependency_kind,qualifier,path}`. `dependency_kind` is
`public_contract` or `standard_library` and records the producer's exact
classification under the dependency predicate below. A qualifier uses the
portable ASCII Go identifier subset `[A-Za-z_][A-Za-z0-9_]*`, is not a Go
keyword, and cannot be the blank identifier `_`. An imported path follows the
same rules as the current package path, cannot contain an `internal` component,
and cannot equal the current package path. Qualifiers are unique within a
package, and imported paths are independently unique within a package.

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
each exported method. This `Named.NumMethods` set is the sole method inventory.
Associate each selected `*types.Func` with exactly one matching AST
`*ast.FuncDecl` by `types.Info.Defs[decl.Name]` object identity, and emit that
method object exactly once. Missing, ambiguous, or multiply owned associations
reject the method. Do not use a method set: promoted methods are not emitted.
An alias declaration is never an independent method owner and is never
enumerated for methods. A method present in the selected defined owner's
`Named.NumMethods` is nevertheless emitted when its AST receiver legally spells
that owner through a receiver alias; normalize that spelling as specified
below. Methods on unselected or unexported ultimate defined receiver bases,
local declarations, fields as standalone symbols, builtins, instantiated
synthetic objects, and compiler-generated wrappers are not emitted.

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

### Dependency classification and type predicate

Dependency classification is exact-path, explicit, and default-deny. A producer
run receives two disjoint contract-owned sets of complete import paths:
`approved_standard_library_paths` and `approved_public_contract_paths`. The
sets, including an empty set, are fixed producer policy inputs for that run;
the producer must not infer approval from a repository owner, module prefix,
package name, exported spelling, source import alias, or transitive dependency.
The first set may contain a path only when that path is also identified as a
standard-library package by the selected Go toolchain. The second set contains
only packages that the API contract owner explicitly designates as public
contracts.

Classify a package path before walking a type. The current package is `current`.
An exact member of `approved_standard_library_paths` is `standard_library`, and
an exact member of `approved_public_contract_paths` is `public_contract`. The
following hard denials override both sets: an empty path, a path with an
`internal` component, and any path beginning exactly
`github.com/enbility/` are `implementation`. Every other non-current path is
also `implementation`. Approval sets must be disjoint and must not contain a
hard-denied path. `unsafe.Pointer` is treated as a reference to package path
`unsafe`, so it is allowed only when `unsafe` is an approved standard-library
path. For every rendered non-current package the producer emits the resulting
allowed class as `imports[].dependency_kind`; implementation-class imports and
types are rejected rather than emitted.

There is one exact pre-classification exception for aliases owned by the
predeclared universe. A package-less `*types.Alias` whose object has
`Alias.Obj().Pkg() == nil` and `Alias.Obj().Parent() == types.Universe` is not
package-classified and is not subjected to the non-current exported-object
check. Its type arguments and `Alias.Rhs()` are still traversed under the normal
alias rule. In Go 1.24 mode this admits the predeclared alias `any` by walking
its right-hand side. If the selected toolchain exposes other predeclared
aliases whose objects belong to `types.Universe`, handle them identically. This
does not exempt an arbitrary package-less alias or object whose parent is not
`types.Universe`, nor an object with a non-nil package whose path is empty;
those cases remain invalid and reject the declaration.

Apply the following `go/types` walk independently to every selected constant or
variable type; every defined-type underlying type or alias right-hand side;
every declaration type-parameter constraint; and every selected function or
method signature, including its receiver and receiver type parameters. The walk
uses a visited set keyed by `types.Type` object identity. Mark a node before
descending; revisiting a marked node terminates that edge successfully, because
the first visit checks the node and every outgoing edge. An invalid, unknown, or
unsupported type node rejects the declaration.

- A basic type is allowed, subject to the special `unsafe.Pointer` rule above.
  A type parameter recursively checks its constraint. A tuple checks every
  variable type.
- A pointer, array, slice, map, or channel checks every reachable element, key,
  or value type. A union checks every term type. No composite is a visibility
  boundary.
- A struct checks every field type in declaration order, including named,
  unnamed, embedded, exported, and unexported fields. Tags contain no types.
- Complete an interface, then check every explicit method signature and every
  embedded type. A signature checks its receiver when present, all receiver and
  ordinary type-parameter constraints, every parameter, and every result. This
  rule covers anonymous function types and methods reached through interfaces as
  well as selected package functions and declared methods.
- For a `*types.Named`, check all type arguments first. A universe object is an
  allowed leaf. A named type declared in the current package then checks its
  underlying type; its selected declared methods are checked separately as
  roots. A non-current named type is allowed as a leaf only when its object is
  exported and its package class is `standard_library` or `public_contract`.
  At that approved exported named boundary, do not inspect the dependency's
  underlying type or method set. An unexported dependency name or an
  implementation-class package rejects immediately.
- A `*types.Alias` is never a leaf boundary. Check its type arguments. Apply the
  exact `types.Universe` exception above when its object is package-less and
  universe-owned; otherwise classify its package and require its object to be
  exported when it is non-current. Always check `Alias.Rhs()`, including for a
  universe-owned alias. Thus neither an approved alias nor a predeclared alias
  can conceal an enbility, internal, unapproved, unexported, or otherwise
  implementation type.

Checking type arguments before stopping at an approved named boundary prevents
an allowed generic contract such as `contract.Box[T]` from carrying an
implementation argument. Walking current named types and every alias prevents a
local facade name from hiding an implementation type. Cycles do not weaken
either rule because package classification and exported-name checks happen on
the first identity visit before traversal can terminate on a revisit.

The portable validator requires the closed dependency field, rejects any value
other than the two allowed classes, and independently rejects a
`github.com/enbility/` import even if mislabeled. It can check path shape,
`internal` components, exact import uniqueness, and the emitted class. Proving
toolchain standard-library provenance, membership in the contract-owned
approval sets, selector use, exported `go/types` object identity, recursive
reachability, and cycles remains producer-owned.

### Canonical package qualifiers

After the dependency predicate passes, walk every semantic type that will be
rendered in `type` or `constraint`.
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
allocation reserve `_`, every Go keyword, every name in `types.Universe`, every
emitted package-scope declaration name, and every retained declaration or
canonical receiver type-parameter name. Compute canonical receiver binders by
the positional algorithm below before this allocation. Sort all collected
packages by the bytewise UTF-8 tuple
`(base, full import path)`. In that order allocate the first identifier not in
the reserved or already allocated sets from `base`, `base_2`, `base_3`, and so
on. Testing availability is global to the package and suffix search starts at 2
for every collision. Thus a real declared name such as `shared_2` can itself
force a later suffix. Source aliases, dot imports, file order, and import
declaration order are ignored. Blank imports cannot be referenced by a
selected type and are absent.

`imports[]` is exactly this path-to-allocated-qualifier map plus the package's
dependency class, then sorted by the normal import ordering rule. Every
non-current package selector in every
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

- Dispatch a `*types.Basic` by `Basic.Kind()`. For `types.Uint8`, emit `uint8`;
  for `types.Int32`, emit `int32`; and for `types.UnsafePointer`, render the
  qualifier allocated to import path `unsafe` followed by `.Pointer`, including
  any collision suffix. For every other supported basic kind, emit
  `Basic.Name()`. The `Uint8` and `Int32` overrides are mandatory and apply
  regardless of `Basic.Name()`, so source `byte`/`uint8` and source
  `rune`/`int32` respectively converge. `types.UntypedRune` is not overridden
  and remains `untyped rune`.

  A `go/types` probe that type-checks package variables with
  `types.Config.GoVersion` set to `go1.24` observes the following API values.
  This is why a renderer based only on `Basic.Name()` is not canonical:

  | Source declaration | `Basic.Kind()` | `Basic.Name()` | `types.TypeString` | v1 rendering |
  |---|---|---|---|---|
  | `var FromByte byte` | `types.Uint8` | `byte` | `byte` | `uint8` |
  | `var FromUint8 uint8` | `types.Uint8` | `uint8` | `uint8` | `uint8` |
  | `var FromRune rune` | `types.Int32` | `rune` | `rune` | `int32` |
  | `var FromInt32 int32` | `types.Int32` | `int32` | `int32` | `int32` |
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

Declaration `type_parameters` retain declared order and object names and render
each constraint by the same rules. Go permits the blank identifier as a type
parameter declaration and permits more than one blank declaration parameter.
Preserve each `_` occurrence positionally in type and function declaration
arrays and in their source-like signatures. Nonblank declaration parameter
names remain unique; repeated `_` names are not a duplicate-name error.

A method receiver is derived from the AST declaration associated with the
selected method object, not from source text and not from
`Signature.Recv().Type()` alone. Require one receiver field and let `R` be the
`types.Info.TypeOf` value for that field's complete type expression. A missing,
nil, invalid, or ambiguous AST/type association rejects the method. Resolve `R`
with this exact loop while maintaining a total pointer count and a visited set
keyed by `*types.Alias` object identity:

1. For `*types.Pointer`, increment the total pointer count, reject immediately
   when it exceeds one, and continue with `Elem()`.
2. For `*types.Alias`, reject an identity revisit. Its object must be a
   package-scope object of the current package, and both `Alias.TypeParams()`
   and `Alias.TypeArgs()` must be empty. Continue with `Alias.Rhs()`. The alias
   spelling is source-only and never becomes the emitted receiver base.
3. For `*types.Named`, stop and retain both that occurrence and its `Origin()`.
4. Any other terminal, including a `*types.Basic` of kind `types.Invalid`, an
   interface, another basic or composite type, or a malformed object, rejects
   the method.

The retained origin must be the exact selected local defined `*types.Named`
from whose `Named.NumMethods` the method was obtained. Its object must belong to
the current package scope, satisfy the exported ASCII v1 rule, and be the
selected non-alias type declaration. A named type whose underlying type is a
pointer or interface is invalid as a receiver base. If at least one alias was
traversed, the retained named occurrence must be uninstantiated: its
`TypeArgs()` is empty and it equals its origin. Thus alias cycles, foreign alias
objects or bases, unselected or unexported ultimate bases, interface or defined
pointer bases, invalid terminals, instantiated alias targets, and more than one
total pointer all reject the method. An intermediate local alias does not
replace or alter the visibility of the ultimate defined owner.

Set `receiver.base` to the retained origin object's name and set
`receiver.pointer` from whether the total pointer count is one. This count is
semantic across the complete spelling: source `*U` contributes one pointer,
and `P` with `type P = *T` contributes one pointer through the alias right-hand
side. Do not copy an alias name from either the AST or the method signature into
JSON.

For a direct generic defined receiver, the retained named occurrence's
type-argument count and `Signature.RecvTypeParams()` count must both equal the
base declaration's `Named.TypeParams()` count, and each receiver type argument
must be the exact receiver `*types.TypeParam` object at the same index; comparing
only names is insufficient. A legally traversable receiver alias is
non-generic and therefore has zero receiver-bound type parameters. Otherwise
reject the method.

Generate the receiver's canonical binder list from the base declaration
parameters before qualifier allocation. Initialize `reserved` with `_`, every
Go keyword, every name in `types.Universe`, every emitted package-scope
declaration name, and every nonblank base declaration parameter name. Visit base
parameters in declaration order using one-based position `i`:

1. If the base name is nonblank, append that name unchanged.
2. If it is `_`, try `T<i>`. If reserved, try `T<i>_2`, then `T<i>_3`, and so
   on in increasing decimal order until an unreserved identifier is found.
3. Append the chosen generated binder and add it to `reserved` before visiting
   the next position.

The generated roots and suffixes are ASCII decimal with no zero padding. This
algorithm yields a unique nonblank valid Go binder at every receiver position,
while avoiding nonblank declaration names, package declarations, keywords, and
predeclared identifiers. Add the complete canonical binder list to the package
qualifier-allocation reserved set.

For a generic method, build a substitution map keyed by the actual
`*types.TypeParam` object identity in `Signature.RecvTypeParams()`. Receiver
parameter object at index `i` maps to canonical receiver binder at index `i`.
While rendering every receiver type argument, parameter, result, constraint,
and nested type reachable from that method signature, a type-parameter
occurrence consults this map before using its object name. Do not key this map by
text and do not map the distinct base `Named.TypeParams()` objects. `base` is
the selected ultimate origin name, `pointer` records the total pointer count,
and `receiver.type_parameters` contains the generated canonical binders in
declaration order. Source receiver variable and binder names are discarded.

For example, source `func (box *Box[R]) Put(value R) R` on `type Box[T any]`
emits `{"base":"Box","pointer":true,"type_parameters":["T"]}` and type
`func(T) T`, from which the normalized signature is
`func (*Box[T]) Put(T) T`. The blank/collision golden below shows the generated
case.

A `go/types` probe using `types.Config.GoVersion = "go1.24"` establishes the
legal boundary: `type Blank[_, _ any] struct{}` and receiver
`Blank[_, _]` are accepted; each declaration and receiver position has a
distinct `*types.TypeParam` identity even though every object name is `_`.
Named receiver binders are likewise distinct from the base declaration objects,
and each receiver type argument is identical to the corresponding
`Signature.RecvTypeParams()` object. `type Bad[T, T any]` is rejected as a
redeclaration, and a receiver with fewer binders than its generic base is
rejected for arity mismatch.

The same Go 1.24-mode AST/`go/types` probe establishes receiver-alias behavior.
For local non-generic `type U = T` and `type V = U`, methods declared on `U`
and `V` are accepted and occur in `T.Named.NumMethods`, while their method
signatures retain `U` and `V` as receiver types. `type P = *T` with receiver
`P` is accepted, as is explicit receiver `*U`; each has one total pointer.
Explicit receiver `*P` is rejected as a double pointer. Methods on a generic
alias and on an alias of an instantiated generic defined type are rejected.
The producer still performs the fail-closed checks above after successful type
checking and excludes a Go-legal exported method whose ultimate defined base is
unexported. The executable vector is `tests/go_receiver_alias_probe.go`; it also
pins checker rejection of alias cycles, foreign bases, interface and defined
pointer bases, invalid bases, and more than one pointer.

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
constraint}`. Every nonblank name is unique within the declaration; `_` is
preserved and may repeat where accepted by Go.

A method has no declaration-level `type_parameters` field. Its `receiver` is
the closed object `{base,pointer,type_parameters}`. `base` is an exported,
unqualified portable ASCII identifier, `pointer` is a JSON boolean, and
`type_parameters` is an always-present ordered array of unique portable ASCII
nonblank identifiers. The base must resolve to a type declaration in the same package,
that declaration must have `type_form: defined`, and receiver arity must equal
that declaration's type-parameter arity. The receiver parameter strings must
also exactly equal the positional canonical binder list derived from the
resolved declaration and package declaration names. Renamed, reordered, blank,
or otherwise noncanonical strings and alias bases are invalid. This remains
true when the source method receiver used an alias: portable JSON contains only
the canonical ultimate defined base, and the validator does not resolve alias
names supplied as `receiver.base`.

Package-scope declaration identity is `(package path, name)`, independent of
kind. A constant, variable, type, and function therefore cannot reuse the same
package-scope name. Method identity is `(package path, receiver.base, name)`,
independent of pointer choice. Canonical receiver parameter names participate
in representation, signature derivation, and the compatibility fingerprint,
but are not an additional method-identity component.

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
signature derivation. For `int`, `float`, and `complex`, it also enforces the
following exact structural grammar before a numeric span can receive the
publication-policy exemption below:

- an integer is `-?(0|[1-9][0-9]*)`;
- a real component is such an integer, a fraction `N/D`, or a normalized binary
  float. For a fraction, `N` is a nonzero canonical integer, `D` is a canonical
  positive integer greater than one, and `gcd(abs(N),D) = 1`. A normalized
  binary float matches
  `-?0x\.[89a-f](?:[0-9a-f]*[1-9a-f])?p(?:\+0|\+[1-9][0-9]*|-[1-9][0-9]*)`;
- a float uses one real component. A float whose exact value is integral still
  uses the integer form;
- a complex value is exactly `(R + Ii)`, where `R` and `I` are real components.
  The separator is always space-plus-space, so a negative imaginary component
  renders as `(R + -Ii)`.

These grammars describe the forms emitted by Go 1.24 `ExactString`; they do not
evaluate source expressions. A `go/types` probe in `go1.24` mode observes a
41-digit reduced float as
`77777777777777777777777777777777777777777/10000000000000000000000000000000000000000`,
the corresponding 101-digit fraction without abbreviation, and a complex value
as the two exact fractions wrapped in `(R + Ii)`. It also observes an integral
float's exact text as `10` and a negative imaginary component with the literal
` + -` separator. Boolean and string ExactString proof remains producer-owned
and never receives a numeric fingerprint exemption.

Only types admitted by the dependency classification and recursive predicate
may appear. The portable import field and hard enbility denial replace the old
synthetic type-text sentinel; ordinary type text is not searched for an invalid
path-shaped token.

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
`Name Constraint`, separated by comma-space, including each repeated `_`
declaration name. Receiver parameters render only their ordered canonical
binders, so a generic receiver is `Base[T, U]`; `pointer: true` adds the single
leading `*`. The value is intentionally duplicated in constant signatures so a
signature is never an invalid pseudo-declaration.

## Compatibility Fingerprint

The compatibility projection is the complete document after removing the root
`fixture` field and every symbol's derived `signature` field. No other field is
removed: package-level `imports`, including each qualifier-to-path identity,
dependency class, participate in the projection and fingerprint. Package, import, and symbol
arrays remain in canonical order, and type-parameter arrays retain declaration
order. Object member input order does not participate.

Fingerprinting occurs only after validation has accepted `schema_version` as
the exact JSON integer token `1`. Alternate numeric spellings such as `1.0` and
`1e0` fail validation and are not canonicalized for fingerprinting. Serialize
the projection as UTF-8 JSON with keys sorted by Unicode code point,
`ensure_ascii` disabled, no insignificant whitespace, and separators `,` and
`:`. The compatibility fingerprint is the lowercase hexadecimal SHA-256 digest
of those bytes. The fingerprint is computed externally; v1 has no
self-referential hash field. Corpus tests pin known digests for all three positive
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
duplicate identities, duplicate nonblank type-parameter names, malformed or duplicate
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
classes including rune, 41-digit and 101-digit exact rational and complex
values, decomposed Unicode ExactString data, generic defined and alias types,
cross-parameter function constraints, repeated blank declaration parameters,
generated receiver binders, value and pointer generic receivers, explicit
dependency classes, direct and chained receiver aliases, pointer aliases, and
canonical package, import, and symbol ordering.
`canonical-go-rendering.json` is the producer golden vector. Its two
paths ending in `collision/a` and `collision/b` both model packages whose
declared package name is `shared`; source aliases `left` and `right` therefore
disappear and the allocated qualifiers are `shared` and `shared_2`. Its
`Normalize` golden vectors include equivalent all-named and all-unnamed
parameter/result variants, but the golden type omits every parameter/result
name. Its source receiver binds `R` for the declaration parameter `T`, while
the receiver object, method type, and signature use the canonical declaration
name `T`. Its generic `Alias` repeats `Aggregate`'s constraint before
instantiating `Aggregate[T]`, so that declaration is type-checkable rather than
merely renderable. The `FromByte`, `FromRune`, `FromUint8`, and `FromInt32`
vectors pin the `Basic.Kind()` normalization above. The fixture also pins
aliases, defined types, builtins, pointers, arrays, slices, maps, all channel
directions, structs, interfaces, functions, variadics, embedded types, type
parameters, constraints, and generic receivers.

The same fixture defines `type BlankSlots[_, T1, _ any]` and package declaration
`T3`. The first blank's positional candidate `T1` collides with the nonblank
parameter, and the third position's candidate `T3` collides with the package
declaration. The canonical binders are therefore `T1_2`, `T1`, and `T3_2`.
The method golden substitutes its source receiver objects into every nested
occurrence by object identity; no source binder name survives.

It also defines `ReceiverDirect = ReceiverBase`,
`ReceiverChain = ReceiverDirect`, and `ReceiverPointer = *ReceiverBase`.
Methods declared with receivers `ReceiverDirect`, `ReceiverChain`,
`ReceiverPointer`, and `*ReceiverDirect` are all obtained exactly once from
`ReceiverBase.Named.NumMethods`. Their emitted receiver bases are uniformly
`ReceiverBase`; only the latter two normalize to `pointer: true`.

The input/output facts represented by that fixture are exact golden vectors:

| Type-checked source fact | Canonical machine fact |
|---|---|
| `import left "example.invalid/helianthus/synthetic/collision/a"` and `import right "example.invalid/helianthus/synthetic/collision/b"`, where both imported declarations say `package shared` | `imports` maps the first full path to `shared` and the second to `shared_2`; type text contains neither `left` nor `right` |
| `func Normalize[T interface{ ~string \| ~int }](first left.Value, second right.Value, rest ...T) (result T, err error)` | `type` is `func(shared.Value, shared_2.Value, ...T) (T, error)` and the sorted constraint is `interface{ ~int \| ~string }` |
| `func Normalize[T interface{ ~string \| ~int }](left.Value, right.Value, ...T) (T, error)` | The identical canonical `type`; only the declaration name and type-parameter fields remain named |
| `type Aggregate[T interface{ ~string \| ~int }] ...` with `func (a *Aggregate[R]) Apply(value left.Value, rest ...R) (result R, updates <-chan right.Value)` | receiver is `{base: Aggregate, pointer: true, type_parameters: [T]}`, `type` is `func(shared.Value, ...T) (T, <-chan shared_2.Value)`, and the signature uses `*Aggregate[T]` |
| `var T3 uint8; type BlankSlots[_, T1, _ any] struct{ Value T1 }; func (BlankSlots[A, B, C]) Bind(A, B, C) (A, B, C)` | declaration parameters remain `[_ any, T1 any, _ any]`; receiver parameters are `[T1_2, T1, T3_2]`; method `type` and signature substitute exactly those binders |
| `type Alias[T interface{ ~string \| ~int }] = *Aggregate[T]` | the alias constraint is identical to `Aggregate`'s canonical constraint, so every permitted `T` satisfies the instantiated target |
| `type ReceiverDirect = ReceiverBase; func (ReceiverDirect) AliasDirect(uint8) uint8` | method is emitted once from `ReceiverBase.Named.NumMethods` with receiver `{base: ReceiverBase, pointer: false, type_parameters: []}` and no alias spelling in its signature |
| `type ReceiverChain = ReceiverDirect; func (ReceiverChain) AliasChained(string) string` | the finite two-alias chain resolves to the same canonical value receiver |
| `type ReceiverPointer = *ReceiverBase; func (ReceiverPointer) AliasPointer(bool) bool` | the pointer in the alias right-hand side yields canonical `pointer: true` |
| `func (*ReceiverDirect) AliasExplicitPointer(int32) int32` | the explicit pointer outside the direct alias also yields canonical `pointer: true`; `*ReceiverPointer` is rejected because its total would be two |
| `var FromByte byte` and `var FromUint8 uint8` | both `type` fields and signatures use `uint8` |
| `var FromRune rune` and `var FromInt32 int32` | both `type` fields and signatures use `int32` |
| imported collision packages are in the producer's exact public-contract approval set | both import objects carry `dependency_kind: public_contract`; this field is fingerprinted |
| 41-digit and 101-digit reduced rational constants and their complex combinations | `value` and the exact signature suffix preserve the complete `ExactString`; negative imaginary text uses ` + -` |

Producer-only dependency vectors use abstract `go/types` constructor notation;
quoted object names such as `X` are synthetic placeholders and assert no runtime
API. They freeze the predicate independently of the portable sentinel-free
negative fixture:

| Type graph and policy input | Exact result |
|---|---|
| `Named("time","Time")`, with `time` in `approved_standard_library_paths` and confirmed standard by the toolchain | PASS after checking zero type arguments; stop at the exported approved named boundary |
| `Named("example.invalid/contract","Public")`, with that exact path in `approved_public_contract_paths` | PASS as an exported public-contract leaf |
| `Named("github.com/enbility/eebus-go/spine/model","X")`, even if either approval set incorrectly lists the path | REJECT because the hard enbility denial overrides approval |
| `Named("example.invalid/contract","Box",[Named("github.com/enbility/eebus-go/spine/model","X")])` | REJECT while checking the type argument before the otherwise approved named boundary |
| current-package `Alias("Facade", Named("github.com/enbility/eebus-go/spine/model","X"))` or an approved dependency alias with that right-hand side | REJECT because aliases always expand |
| Go 1.24 `any`, represented as a package-less `*types.Alias` whose object belongs to `types.Universe` | PASS without package classification or a non-current export check, but only after traversing `Alias.Rhs()`; any other universe-owned predeclared alias is handled the same way |
| a synthetic package-less alias whose object is not owned by `types.Universe`, or an alias whose object's non-nil package has an empty path | REJECT; neither invalid object receives the universe exception |
| `struct{ F []map[string]chan<- Named("unapproved.invalid/impl","X") }` | REJECT through field, slice, map, and channel traversal |
| `interface{ M(func(Named("unapproved.invalid/impl","X")) error) }` or a selected method signature with that type in its receiver, constraint, parameter, or result | REJECT through interface, method, signature, and receiver traversal |
| a current-package `Node` whose underlying struct contains `*Node` and an approved exported contract leaf | PASS; the identity-keyed revisit ends the cycle after all first-visit checks |

The exact negative allowlist has ten filenames. Each fixture retains the valid
schema identity, canonical version token, synthetic marker, no-runtime marker,
and synthetic package prefix while producing exactly its approved diagnostic
set. The duplicate-key fixture duplicates only `schema_id`, with equal values;
strict recovery retains every occurrence for boundary and publication checks.
`implementation-dependency-type.json` carries a synthetic enbility-model import
with negative-only `dependency_kind: implementation` and references its normal
allocated qualifier. It contains no path-shaped type-text sentinel; the exact
diagnostic is `implementation dependency type`.

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
SKI/SHIP ID forms. Assignment labels are case-insensitive; spaces, hyphens,
and underscores are equivalent separators where a label has multiple words,
including `full fingerprint` and `mac address`. It also recognizes
household-data/schedule labels,
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
The only context-aware fingerprint diagnosis exemption is one complete
canonical numeric ExactString span in `packages[*].symbols[*].value`, and the
identical suffix span in that symbol's exactly derived source-like `signature`.
The closed symbol object must have `kind: const`, `value_kind` equal to `int`,
`float`, or `complex`, and `value` must pass the exact kind-specific grammar
above. Its signature must be byte-for-byte the derivation from the same name,
type, and value. Any duplicate key in the object or an ancestor disables the
exemption.

The exemption suppresses only a fingerprint diagnosis for fingerprint matches
wholly contained in those two exact numeric spans. Private paths, network
addresses, credentials, source contamination, and every other marker class
still scan the complete value and signature. Boolean and string constants,
leading plus signs or zeroes, zero or reducible fractions, denominator one,
malformed complex separators, malformed binary floats, hexadecimal-looking
identifiers, all-digit data in any other field, duplicate contexts, and a
signature not exactly derived from the same value are not exempt. A canonical
binary float is numeric only when the whole value matches its exact grammar;
an arbitrary long hexadecimal string or identifier remains private.

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
