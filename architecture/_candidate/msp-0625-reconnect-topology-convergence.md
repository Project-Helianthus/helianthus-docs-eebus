---
canonical_source: "Project-Helianthus/helianthus-docs-eebus:architecture/_candidate/msp-0625-reconnect-topology-convergence.md"
owner_domain: "architecture"
license: "AGPL-3.0-only"
publication_status: "candidate"
claim_status: "evidence-backed"
source_class: "derived_inference"
evidence_ids: "EV-20260729-002"
hypothesis_status: "draft"
falsifier: "A focused ordering test or bounded replay shows that discarding a detailed SPINE topology event before connected-session publication still converges the raw snapshot, or that staging the event cannot bind it to the exact runtime generation, session, and remote device."
stable_navigation: "false"
search: "false"
sitemap: "false"
versioned_bundle: "false"
release_bundle: "false"
---

# Candidate Reconnect Topology Convergence

## Status And Boundary

This candidate records an M6.25 runtime ordering requirement discovered during
the bounded reconnect validation for
[`helianthus-ship-go` pull request 23](https://github.com/Project-Helianthus/helianthus-ship-go/pull/23).
It applies to the operator topology snapshot in `helianthus-eebusreg`; it does not
promote semantics, define a consumer surface, or change the transport collision
rule.

The raw runtime can receive a completed detailed SPINE discovery event before
its remote-connected callback has published the corresponding session
generation. Treating the absence of that session row as a reason to discard
the event can leave `topology.get` frozen at a partial device-only snapshot
even while exact live feature reads already succeed.

## Required Ordering Behavior

For an admitted remote identity, the runtime must preserve these invariants:

1. A topology-bearing SPINE event received before connected-session
   publication is retained as a pre-session observation rather than silently
   discarded.
2. Retention binds the observation to the active runtime generation and the
   exact remote-device instance that emitted it.
3. Session publication consumes only a retained observation that still matches
   the current remote device, then binds it to the newly allocated connection
   generation before snapshot publication.
4. If publication wins the race, the event updates that exact connected
   generation through the normal serialized refresh path.
5. Disconnect and runtime shutdown retire unconsumed observations. A stale
   observation cannot populate a later connection generation.

The implementation may coalesce repeated topology events, but it must preserve
the newest complete raw facts and deterministic snapshot ordering. It must not
fabricate entities, features, use cases, or protocol metadata from allowlist or
trust policy.

## Readiness And Degraded State

SHIP session readiness and topology convergence are distinct observations.
`runtime.status.get` may report a connected runtime while detailed SPINE
discovery is still progressing, but `topology.get` must not present a
permanently partial snapshot as successful convergence.

A bounded discovery interval that ends without topology convergence must
remain explicit and inspectable. This candidate does not freeze a timeout,
retry schedule, or semantic completeness threshold.

## Acceptance Proof

The implementation proof must include:

- event-before-connected and connected-before-event orderings;
- a concurrent crossing of event capture and session publication;
- disconnect and reconnect with a new connection generation;
- an event from a stale remote-device instance;
- deterministic merge and publication of device, entity, feature, use-case,
  description, metadata, and opaque raw fields; and
- a bounded deployed restart where the final raw snapshot and an exact
  read-only feature operation agree that the same topology is live.

No write is part of this proof.

## Exact Falsifiers

This candidate is falsified if any accepted test or bounded replay shows that:

1. an event captured before session publication is discarded and no later
   event repairs the raw topology;
2. a retained event from a previous runtime generation or remote-device
   instance populates the current session;
3. disconnect or shutdown leaves a retained event available to a later
   session;
4. the raw snapshot remains partial after the exact live feature graph is
   readable; or
5. the repair introduces policy-derived topology, a consumer API, promoted
   semantics, or a write path.
