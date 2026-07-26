---
canonical_source: "Project-Helianthus/helianthus-docs-eebus:protocols/_candidate/msp-052-outbound-endpoint-selection.md"
owner_domain: "protocols"
license: "CC0-1.0"
publication_status: "candidate"
claim_status: "evidence-backed"
source_class: "derived_inference"
evidence_ids: "EV-20260726-001"
hypothesis_status: "draft"
falsifier: "A reviewed implementation or bounded publishable run shows that SHIP Hub endpoint ordering applies before persisted-trusted or actively authorized queued-pairing eligibility; that a configured service address may replace, prepend, or supplement the concrete addresses in the selected mDNS observation; that preserving the mDNS snapshot cannot provide concrete-address-first dialing with stable IPv4/IPv6 order and a final hostname fallback; or that an endpoint/path attempt can safely inherit authorization issued for a different endpoint or path."
stable_navigation: "false"
search: "false"
sitemap: "false"
versioned_bundle: "false"
release_bundle: "false"
---

# Candidate Outbound Endpoint Selection For SHIP

## Status And Source Boundary

This candidate is tracked by
[docs issue 64](https://github.com/Project-Helianthus/helianthus-docs-eebus/issues/64)
and accompanies
[`helianthus-ship-go` pull request 21](https://github.com/Project-Helianthus/helianthus-ship-go/pull/21).
It defines the Helianthus SHIP Hub endpoint plan after one mDNS-discovered
remote service has passed outbound reconnect eligibility. It is not a generic
SHIP or EEBUS requirement and does not claim current support while the
companion implementation remains under review.

The input is one immutable mDNS observation containing its host, concrete
addresses, port, and path. Discovery owns that observation. Endpoint planning
reads it without changing its address slice, field order, or shared snapshot.
Planning produces attempt-local values only.

## Eligibility Precondition

Endpoint planning starts only after SHIP Hub eligibility for either a
persisted-trusted reconnect or an actively authorized queued pairing attempt.
A passive mDNS observation grants no authority and cannot create either
eligibility state. When durable trust or active queued authorization already
exists, the callback may trigger or schedule connection initiation from the
current observation; every resulting dial remains subject to its per-attempt
gate. Authority, first-trust selection, and eebusreg lifecycle details remain in the
[MSP-052 outbound pairing architecture contract](../../architecture/_candidate/msp-052-outbound-pairing-contract.md).

## Candidate Endpoint Order

Before family ordering, the plan ignores nil addresses and values that cannot
be canonicalized as either IPv4 or IPv6. IPv4 uses its canonical 4-byte value,
so equivalent 4-byte and 16-byte representations are one address. IPv6 uses
its canonical 16-byte value. Canonical duplicates are removed first-seen:
the first occurrence supplies the attempt position and every later equivalent
value is ignored.

The outbound endpoint plan uses this deterministic order:

1. Every unique canonical IPv4 address, preserving first-seen IPv4 order.
2. Every unique canonical IPv6 address, preserving first-seen IPv6 order.
3. The observed hostname as the final fallback, unless it parses as an IP equal
   to an already planned concrete address.

Every endpoint uses the observed port. For each endpoint, the path attempt
order is the observed path first and then the empty path (root URL fallback) after
an ordinary first-path failure. The second attempt is explicit; it does not
rewrite the first attempt or change the frozen mDNS snapshot.

The selected mDNS observation is the sole endpoint-address input. A configured
service address cannot replace, prepend, or supplement its concrete addresses.
The plan adds no static address, configured hostname, peer-specific address, or
identity-specific route. It contains no device model, laboratory address, or
certificate identifier.

Failure of one concrete address advances only to the next ordered endpoint.
All concrete addresses may fail; the hostname remains the final fallback
rather than being discarded. When the snapshot has no concrete address, the
hostname is the sole endpoint. A hostname failure ends the plan.

## Discovery, Authorization, And Dial

Discovery and dialing remain distinct authority stages. An mDNS callback may
create or replace an observation and, when Hub eligibility already exists, may
trigger or schedule connection initiation. It does not grant authority, create
eligibility, or bypass the per-attempt gate. Hub eligibility binds either the
current persisted-trusted service authority or the actively authorized
queued-pairing authority before endpoint planning. The resulting endpoint list
does not itself authorize or launch a dial.

Before each network attempt, the outbound attempt gate must revalidate the
current Hub authority and authorize both the exact endpoint and the exact path
for that attempt. Authorization is not transferable: an IPv4 attempt, an IPv6
attempt, and the final hostname attempt each pass the gate separately. For one
endpoint, authorization and permit for the observed path do not authorize the
empty path (root URL fallback); that second path passes the gate separately.
Neither path may be inherited from another observation. The linked architecture
contract owns the detailed trust/admin rules.

## Falsifiers And Limits

The redacted runtime observation records a `.local` resolver blocked long
enough to retain outbound attempt ownership and prevent inbound convergence
during the bounded window. A same-runtime replay in which hostname resolution
reliably completes inside the attempt budget without retaining that ownership
would falsify that explanation.

The diagnostic address-first run connected to a concrete endpoint in about
275 ms and later produced non-empty SPINE topology. A bounded replay in which
the same concrete endpoint class cannot connect or cannot progress beyond the
hostname-first result would falsify that observed contrast.

Neither observation removes the hostname path. A run in which every concrete
address fails and the hostname succeeds is an expected fallback case and
would falsify any concrete-only design. Different networks may also make
IPv6, rather than IPv4, the first successful family; the candidate fixes
attempt order, not which endpoint must succeed.

Connection and non-empty raw topology are readiness evidence only. They do not
identify a device model, prove general resolver behavior, promote SPINE
semantics, or add GraphQL, MCP, Portal, Home Assistant, or other consumer
state.
