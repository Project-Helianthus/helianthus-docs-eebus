---
canonical_source: "Project-Helianthus/helianthus-docs-eebus:protocols/_candidate/ship-spine-readiness.md"
owner_domain: "protocols"
license: "CC0-1.0"
publication_status: "candidate"
claim_status: "evidence-backed"
source_class: "derived_inference"
evidence_ids: "EV-20260714-001"
hypothesis_status: "draft"
falsifier: "A publishable upstream source or bounded redacted run demonstrates that SHIP-layer connection, SPINE Detailed Discovery, and NodeManagement use-case readiness have different ordering or evidence boundaries."
stable_navigation: "false"
search: "false"
sitemap: "false"
versioned_bundle: "false"
release_bundle: "false"
---

# Candidate SHIP-Layer Connection And SPINE Readiness Boundary

## Status And Source Boundary

This candidate is tracked by
[docs issue 62](https://github.com/Project-Helianthus/helianthus-docs-eebus/issues/62)
and governs
[runtime issue 72](https://github.com/Project-Helianthus/helianthus-eebusreg/issues/72).
It documents the observable ordering implemented by the public SHIP/SPINE
stack. The callback and event names below are source locators, not a stable
Helianthus API, wire contract, or consumer schema. No specification text is
reproduced.

The public source boundary is:

- the SHIP layer reports the remote protocol-service identity through
  `RemoteSKIConnected` before it
  proceeds to SPINE setup
  ([identity callback source](https://github.com/Project-Helianthus/helianthus-ship-go/blob/c4c452b2fddb49030eef30215f20edd60f32735e/hub/hub_shipconnection.go#L160-L165),
  [handshake ordering](https://github.com/Project-Helianthus/helianthus-ship-go/blob/c4c452b2fddb49030eef30215f20edd60f32735e/ship/hs_access.go#L67-L94));
- approved SHIP-layer completion calls `SetupRemoteDevice`, which installs the SPINE
  reader and then reaches the complete state
  ([setup source](https://github.com/Project-Helianthus/helianthus-ship-go/blob/c4c452b2fddb49030eef30215f20edd60f32735e/ship/handshake.go#L214-L257),
  [eeBUS bridge](https://github.com/Project-Helianthus/helianthus-eebus-go/blob/6f60de7d032987bc39b29dd5b375daf6c178e982/service/service_hub.go#L15-L31));
- SPINE setup creates the remote device and requests Detailed Discovery
  ([SPINE setup](https://github.com/Project-Helianthus/helianthus-spine-go/blob/2fdb4319c69e9afd4f4d1b78b3f40da43d976ce0/spine/device_local.go#L109-L130));
- a successful Detailed Discovery reply populates the device, entities, and
  features before publishing native device/entity add events
  ([Detailed Discovery reply](https://github.com/Project-Helianthus/helianthus-spine-go/blob/2fdb4319c69e9afd4f4d1b78b3f40da43d976ce0/spine/nodemanagement_detaileddiscovery.go#L52-L91));
- the native core handler requests NodeManagement use-case data only after the
  Detailed Discovery device-add event, and the later reply or notification
  publishes a separate data-update event
  ([post-discovery request](https://github.com/Project-Helianthus/helianthus-spine-go/blob/2fdb4319c69e9afd4f4d1b78b3f40da43d976ce0/spine/device_local.go#L70-L102),
  [use-case update](https://github.com/Project-Helianthus/helianthus-spine-go/blob/2fdb4319c69e9afd4f4d1b78b3f40da43d976ce0/spine/nodemanagement_usecase.go#L12-L59)).

The public
[EEBUS downloads page](https://www.eebus.org/media-downloads/) remains the
source for publicly distributed EEBUS material; this candidate makes no claim
beyond the cited library behavior and Helianthus evidence boundary.

## Readiness Sequence

| Stage | Native evidence | Allowed raw claim |
| --- | --- | --- |
| SHIP-layer connected | `RemoteSKIConnected` | One connected session for the observed remote. Topology and use-case readiness remain unknown. |
| SPINE setup | `SetupRemoteDevice` and Detailed Discovery request | SPINE exchange has started. No device, entity, feature, or use-case claim is ready. |
| Detailed Discovery complete | `DeviceChange` with `Add` after the graph is populated | The live remote device and its current entities/features are evidence-ready. |
| Incremental graph change | Native entity add/remove event | The affected live graph may be refreshed from the current remote device. |
| Use-case data ready | Data update carrying real NodeManagement use-case data | Use-case claims are refreshed from that data only. |

## Native Feature Role Vocabulary

The public SPINE model defines the feature roles `client`, `server`, and
`special`
([role vocabulary](https://github.com/Project-Helianthus/helianthus-spine-go/blob/2fdb4319c69e9afd4f4d1b78b3f40da43d976ce0/model/commondatatypes.go#L616-L622)).
`special` is an active native value; for example, the remote NodeManagement
feature is created with that role
([NodeManagement feature](https://github.com/Project-Helianthus/helianthus-spine-go/blob/2fdb4319c69e9afd4f4d1b78b3f40da43d976ce0/spine/device_remote.go#L40-L44)).

When Detailed Discovery makes the graph evidence-ready, the raw graph
preserves the exact native role. It must not convert `special` to an empty,
unspecified, client, or server value. An exporter that cannot represent a
native role keeps the raw observation distinct and reports that projection as
unrepresentable; it cannot emit a lossy substitute.

The initial raw API is not yet published. Its first contract freeze must
represent `client`, `server`, and `special` exactly; adding `special` here is
part of the initial contract, not a compatibility alias or a later API
version. Raw role preservation still authorizes no semantic promotion.

A connected session may therefore be published with an empty topology while
SPINE setup and Detailed Discovery are still in progress. Empty topology at
that stage is not a disconnect, protocol failure, or proof that the remote has
no entities or features.

Detailed Discovery is the first graph evidence boundary. The device-add event
is emitted only after the native remote device has been populated, so the
device, entity, and feature snapshot is read from that live object. SHIP-layer
state cannot be substituted for this event, and feature presence
cannot be synthesized from a device class, configured profile, or prior
connection.

NodeManagement use-case data has a later boundary. Detailed Discovery may
trigger its request, but it does not establish the response. Use-case claims
remain absent until the native data-update event carries real
NodeManagement use-case data; each such event refreshes the claims from the
active remote device. Feature combinations, local use-case registration,
device labels, and earlier sessions cannot synthesize use-case support.

## Observer And Publication Boundary

An application observer may consume the native SPINE event stream only as an
internal evidence adapter. Subscription and unsubscription are public
application capabilities of the stack
([event surface](https://github.com/Project-Helianthus/helianthus-spine-go/blob/2fdb4319c69e9afd4f4d1b78b3f40da43d976ce0/spine/events.go#L43-L104)).
The admitted-subscriber snapshot is race-safe in
[upstream PR 39](https://github.com/enbility/spine-go/pull/39) and its
[Helianthus closure](https://github.com/Project-Helianthus/helianthus-spine-go/pull/4);
unsubscription therefore stops later admission but does not erase a callback
already admitted by an in-flight publication.

Application callbacks admitted for one subscriber retain source publication
order while different subscribers remain independently dispatchable
([ordered application dispatcher](https://github.com/Project-Helianthus/helianthus-spine-go/pull/8)).
Launching one independent goroutine per event is not conformant because an
older graph capture could then complete after a newer lifecycle event.

Helianthus must bind observations to the configured remote, active service
instance, and current connection generation. A stale callback, unrelated
remote identity, foreign device object, or prior generation cannot alter the
current graph. Snapshot publication is revision-ordered across
SPINE refresh and transport lifecycle paths; a snapshot captured at an older graph
revision cannot become observable after a newer revision.

This candidate adds no `CandidateRef`, exported dependency type, stable public
API, semantic projection, GraphQL field, MCP schema, Portal field, or Home
Assistant entity. Raw entity, feature-role, and use-case evidence remains
non-semantic.
