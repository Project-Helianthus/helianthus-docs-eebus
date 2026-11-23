# eeBUS HA Network Proof Gate

Canonical source: this page.

Plan provenance:
`helianthus-execution-plans/multi-runtime-semantic-platform.draft`.

Implementation hook:
`helianthus-ha-addon/EEBUS_HA_NETWORK_PROOF.md`.

## Scope

MSP-03C proves Home Assistant add-on runtime networking readiness for a future
raw eeBUS SHIP/SPINE sidecar. It does not enable eeBUS in production, import
the gateway eeBUS runtime, expose MCP tools, pair with VR940f, or persist
production trust.

This gate covers `eebus-transport-gate-v0` cases:

| Case | Required proof |
| --- | --- |
| `EEBUS-G05` | Listener binds only a configured interface or subnet. Wildcard bind and unexpected container-bridge exposure fail. |
| `EEBUS-G06` | An external LAN peer can browse and resolve the SHIP mDNS service `_ship._tcp`. Same-container and same-bridge checks are insufficient. |
| `EEBUS-G07` | Disabled mDNS, unavailable Avahi/DBus, and closed-pairing advertisement shutdown are explicit negative states. |
| `EEBUS-G08` | Manual endpoint fallback reaches the peer when discovery is unavailable. |
| `EEBUS-G09` | Disposable proof credentials survive restart without writing production trust state. |

## Contract Fixture vs Lab Evidence

The add-on repository may keep a CI contract fixture that validates artifact
shape, ordering, redaction, and fail-closed invariants. That fixture is not lab
evidence and cannot close MSP-03C by itself.

MSP-03C acceptance requires a redacted `lab_run` artifact collected from a real
Home Assistant runtime and an external LAN peer. The validator must reject
artifacts that claim LAN proof from only the same container, same host bridge,
or unredacted local identifiers. Merely changing a contract fixture from
`"mode": "contract_fixture"` to `"mode": "lab_run"` is invalid; lab artifacts
must include concrete redacted runtime references.

## Public Artifact Requirements

Public artifacts must include:

- repo, issue id, contract id, generated timestamp, and required case list;
- Home Assistant add-on network facts, including host-network and host-DBus
  posture;
- branch, 40-character commit SHA, add-on build id, and command-log reference;
- external LAN peer scope, with no raw private IP address;
- configured interface or subnet reference;
- listener bind policy and bridge/wildcard exposure results;
- listener socket reference, mDNS browse reference, and mDNS resolve reference
  for `_ship._tcp`;
- manual endpoint fallback result;
- disposable credential storage path, permission modes, restart continuity, and
  proof that production trust was not written.
- per-case evidence IDs for `EEBUS-G05` through `EEBUS-G09`.

Public artifacts must not include:

- PEM blocks, private keys, passwords, tokens, or secret-bearing values;
- private or link-local IP addresses;
- MAC addresses;
- device serials;
- full SKIs, fingerprints, stable peer ids, or pairing history;
- vendor-restricted protocol details.

Use short redacted hashes such as `sha256:<12-hex>` for continuity checks.
These hashes prove equality within the run only; they are not semantic facts and
must not be promoted into registries or consumer APIs.

## Negative States

Avahi/DBus unavailable is a degraded networking state, not an empty success.
If host DBus is unavailable to the add-on, the artifact must state that
explicitly and must also prove manual endpoint fallback.

Discovery disabled and pairing closed are different negative states. A valid
artifact records both when applicable:

- discovery disabled: no service is advertised or resolved;
- pairing closed: advertised pairing service is absent or expires after TTL.

## Credential Boundary

M3 uses disposable proof credentials only. The proof store lives under an
explicit proof path, uses directory mode `0700` and file mode `0600`, rejects
symlinks and path traversal, and is safe to remove after the proof.

Production trust-store semantics, clone/restore lockout, quarantine/backoff,
and first-trust confirmation are M4 work. MSP-03C evidence must not claim those
properties.

## Promotion Boundary

MSP-03C evidence is runtime feasibility evidence. It cannot:

- create candidate semantic facts;
- enrich B509/B524/B555 leaves;
- expose GraphQL, Portal, or Home Assistant entities;
- justify command routing or raw writes.

Those steps remain gated by later evidence recording, coexistence, and
per-leaf promotion dossiers.
