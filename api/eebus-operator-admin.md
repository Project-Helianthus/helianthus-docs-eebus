# Post-M9 Shared Consumer Boundary

## Scope And Canonical Ownership

This page freezes only the shared gateway, Portal, Home Assistant, FM5, and
release-version responsibilities required by the post-M9 remediation. The
canonical protocol-specific contract remains exclusively in:

- [`post-m9-operator-pairing-browsers-v1.md`](https://github.com/Project-Helianthus/helianthus-docs-eebus/blob/main/architecture/_candidate/post-m9-operator-pairing-browsers-v1.md)
- [`post-m9-operator-admin-v1.md`](https://github.com/Project-Helianthus/helianthus-docs-eebus/blob/main/api/_candidate/post-m9-operator-admin-v1.md)

Those documents alone own protocol routes, partner views, certificate and OOB
identity, raw-tree traversal, error vocabulary, persistence, and coordinator
state-machine semantics. This page must not restate them; if a shared consumer
rule conflicts with either canonical document, the protocol repository wins for
that protocol concern. The shared boundary follows the linked canonical
docs-eebus contracts without copying their protocol details here.

For a stable external-integrator map of the already merged northbound boundary,
see [eeBUS Northbound External-Integrator Boundary](./eebus-northbound-integrator-reference.md).
It does not promote the protocol repository's candidate documents or define
pairing actions.

`eebus_v1_*` remains the only eeBUS MCP namespace. It stays read-only. There is
no v2 namespace, compatibility alias, public pairing tool, GraphQL mutation, or
Portal-private copy of raw protocol truth. Operator mutations use the
gateway-owned typed API defined by the canonical protocol contract.

## Shared Ownership Boundary

| Component | Shared responsibility | Forbidden responsibility |
| --- | --- | --- |
| eeBUS runtime/coordinator | All protocol-native discovery, identity, connection, trust, persistence, and raw-topology behavior defined by the canonical protocol documents. | Browser or Home Assistant authentication; semantic eBUS projection. |
| Gateway | Bounded request validation, replay-safe action admission, sanitized audit outcomes, and typed coordinator calls. | Parsing trust-store bytes in an HTTP handler; inventing a second protocol state machine, raw topology, or eeBUS-specific authentication system. |
| Portal | Full pairing and operator rendering through the gateway boundary. | Direct filesystem/store access, direct socket access, implicit trust, or semantic promotion of raw data. |
| Home Assistant | Native pairing flow and sanitized status through the same gateway boundary. | Direct trust-store/socket access, transport ownership, automatic trust, or a second pairing state machine. |

Portal and Home Assistant never read the trust store, its bytes, or the
owner-only operator socket. They are clients of the gateway boundary. Only the
gateway's typed adapter may reach the coordinator command boundary, and it may
not expose private socket framing or store representations.

## Consumer Boundary And Mutation Safety

This contract introduces no eeBUS-specific login, session, cookie, CSRF token,
owner credential, Home Assistant credential, or eeBUS reauthentication.
Generic Portal and Home Assistant authentication remain out of scope and are
neither replaced nor modified here. Pairing actions remain functional in both
Portal and Home Assistant; their availability is not deferred until a future
shared Portal login exists.

Both consumers submit the canonical closed action shapes to the gateway-owned
typed API. The gateway still enforces method and content type, bounded bodies,
exact state revision, idempotency binding, handle lifetime, exact OOB identity
comparison, action ordering, and deterministic non-mutating rejection before
coordinator invocation. Removing eeBUS-specific authentication does not allow
discovery to authorize a dial, automatic trust, implicit persistence, direct
store access, or a second pairing FSM. Route and error-code definitions remain
in the canonical protocol API.

## HTTP Access Boundary

The credential-free operator-admin HTTP boundary does not enforce a host-local
transport peer check. Gateway #818 removed that check; status, inspection, and
action admission must not be described as restricted to local peers by the
handler. Deployment network exposure belongs to the shared access boundary,
not an eeBUS-specific authentication mechanism. This does not grant direct
trust-store or operator-socket access or weaken the typed action checks above.

Responses, audit data, logs, metrics, traces, crash data, URLs, and shareable
evidence exclude private keys, tokens, private PEM, trust-store bytes,
credentials, private paths, and raw operator-socket frames. Concrete audit and
redaction fields remain owned by the canonical protocol API.

## Raw Operator Inspection Isolation

The shared stack preserves authorized inspection of lossless protocol-native
data through the gateway boundary. Both Portal and Home Assistant host operator
views may receive bounded raw SPINE and complete comparison identity through the
gateway typed boundary. They may render that bounded inspection data but may not
reinterpret unknown native values, infer semantic facts, retain it beyond the
canonical bounded view lifetime, or establish a second protocol truth source.
Public and shareable formatters receive no raw or operator-only identity data.
Raw protocol data must not enter `ebus.v1`, GraphQL semantic fields, or the
semantic registry. This does not grant either consumer direct trust-store or
operator-socket access, or expose keys, tokens, private PEM, trust-store bytes,
or private socket framing. The canonical protocol documents own all tree shape,
paging, identity, action, and live-cardinality requirements.

## FM5 Behavioral Verdict

FM5 interpretation is one runtime result, not a UI label. Structural FM5 mode
is independent from transient acquisition health. The provider publishes the
tuple:

```text
fm5_semantic_mode
fm5_semantic_degraded_reason
fm5_semantic_evidence_revision
```

The `fm5_semantic_degraded_reason` and
`fm5_semantic_evidence_revision` fields are inseparable from the mode result.

The closed structural modes remain `INTERPRETED`, `GPIO_ONLY`, and `ABSENT`:

- `INTERPRETED` means fresh coherent identity and configuration evidence
  classified the selected FM5 family as structurally interpretable. A known
  coherent `INTERPRETED` baseline remains `INTERPRETED` across a transient
  controller, configuration, solar, cylinder, freshness, or generation
  failure; retained values are not a new live acquisition.
- `GPIO_ONLY` requires fresh, coherent structural evidence that the live
  configuration is outside the interpreted FM5 profile. It carries exactly
  `CONFIGURATION_NOT_INTERPRETABLE`; a failed read, missing controller snapshot,
  stale observation, or generation race cannot create this mode.
- `ABSENT` requires a fresh coherent structural observation with no admissible
  FM5 identity. An incomplete or failed refresh does not prove absence and
  does not replace the previous coherent mode.

The closed degraded-reason set is:

```text
CONTROLLER_UNREACHABLE
CONFIGURATION_UNAVAILABLE
CONFIGURATION_NOT_INTERPRETABLE
SOLAR_ACQUISITION_FAILED
CYLINDER_ACQUISITION_FAILED
EVIDENCE_STALE
INCOHERENT_ACQUISITION
```

Before the first coherent structural classification there is no tuple to
publish. MCP returns a null result, GraphQL exposes a nullable
`fm5_interpretation`, and Portal omits the three optional FM5 verdict fields.
Consumers represent this as acquisition unavailable; they do not manufacture
`GPIO_ONLY`, `ABSENT`, a degraded reason, or an evidence revision.

The named codes are `CONTROLLER_UNREACHABLE`, `CONFIGURATION_UNAVAILABLE`,
`CONFIGURATION_NOT_INTERPRETABLE`, `SOLAR_ACQUISITION_FAILED`,
`CYLINDER_ACQUISITION_FAILED`, `EVIDENCE_STALE`, and
`INCOHERENT_ACQUISITION`; no unlisted reason is accepted.

Reason precedence follows the acquisition pipeline in the order above, except
that `EVIDENCE_STALE` precedes family reads and `INCOHERENT_ACQUISITION` is the
terminal catch for a generation mismatch. A healthy current `INTERPRETED`
sample and a fresh coherent `ABSENT` result carry no degraded reason. A
transient reason may accompany the unchanged previous coherent structural mode
and retained data, but it never changes that mode by itself. `GPIO_ONLY`
always carries exactly `CONFIGURATION_NOT_INTERPRETABLE`.

`CONTROLLER_UNREACHABLE` requires one current bounded acquisition attempt with
fresh attempted-acquisition timestamps and source identity. A neighbor-table
entry, an old log line, retained periodicity, or an uncorrelated status snapshot
is not such proof and must not be reported as a physical adapter outage. The
same freshness and correlation rule applies to every acquisition reason.

The gateway regression test uses the same corpus before and after eeBUS
activation. Once that corpus has produced a coherent interpreted family, a
transient acquisition failure never commits `GPIO_ONLY`; it retains the known
coherent `INTERPRETED` baseline and does not refresh, zero, or withdraw retained
solar or cylinder values. Only a later fresh coherent structural observation
may change the structural mode.

The post-M9 implementation sequence adds
`ebus_v1_semantic_fm5_interpretation_get` first; GraphQL
`fm5_interpretation`, Portal, and Home Assistant then consume that same tuple.
These additive surfaces are pending until their corresponding gateway and
consumer PRs merge; this docs gate freezes the target contract, not current
runtime availability. Consumers may format the reason but may not recalculate
it. The pre-existing `ebus_v1_semantic_fm5_mode_get` scalar stays stable but is
not sufficient to diagnose degradation. A failed refresh does not publish zero
solar/cylinder values or silently erase last-known data; freshness and the
degraded reason remain explicit. Repair is behavioral at the acquisition/
provider boundary, not a cosmetic Portal change.

## Single Release-Version Authority

Every release starts from a single injected build-time release version. The
release workflow uses that exact input to build/tag the image, generate the
add-on package metadata, and inject the gateway build-info object. The same
release version is reported by runtime health, Portal health, and add-on package metadata.
`build_id` may add immutable revision/digest identity but may
not replace or rewrite the release version.

The gateway constructs build information once at process startup. Every
runtime status and Portal handler receives that object; a hard-coded fallback
release number is forbidden. Development builds may explicitly report `dev`,
but a release binary may not silently fall back to an older numeric version.

The packaging gate compares the injected binary version, image tag, and add-on
metadata before publication. Add-on startup compares the immutable expected
package version with the binary build information before opening listeners;
startup fails closed for a release artifact whose injected version is empty or
mismatched. No UI cache, manifest constant, or independent Portal version is a
version authority.

## Acceptance And Isolation

Implementation acceptance requires focused RED/GREEN tests for gateway-boundary
isolation, request admission, raw-data non-leakage, the before-eeBUS/after-eeBUS
FM5 corpus, reason transitions, and version-mismatch startup denial. Protocol-specific identity,
topology, persistence, reconnect, and live-cardinality acceptance comes only
from the canonical protocol documents and the execution plan. Existing eBUS
operation must remain functional throughout eeBUS activity.
