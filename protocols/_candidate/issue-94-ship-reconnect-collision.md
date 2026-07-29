---
canonical_source: "Project-Helianthus/helianthus-docs-eebus:protocols/_candidate/issue-94-ship-reconnect-collision.md"
owner_domain: "protocols"
license: "CC0-1.0"
publication_status: "candidate"
claim_status: "evidence-backed"
source_class: "derived_inference"
evidence_ids: "EV-20260729-001"
hypothesis_status: "draft"
falsifier: "A final reviewed source or focused collision test for helianthus-ship-go pull request 23 shows that direction is not selected by the higher initiating identity key, that the losing inbound attempt reaches protocol activation while the winning outbound attempt is initiating, that inbound ownership follows data-pump startup, or that a pre-Run close permits a pump or more than one terminal close."
stable_navigation: "false"
search: "false"
sitemap: "false"
versioned_bundle: "false"
release_bundle: "false"
---

# Candidate Trusted Protocol Reconnect Collision Arbitration

## Status And Source Boundary

This candidate is tracked by [docs issue 94](https://github.com/Project-Helianthus/helianthus-docs-eebus/issues/94)
and accompanies [`helianthus-ship-go` issue 22](https://github.com/Project-Helianthus/helianthus-ship-go/issues/22)
and [pull request 23](https://github.com/Project-Helianthus/helianthus-ship-go/pull/23).
It records the implementation behavior inspected for that PR; it is neither a
general standardized requirement nor a claim of full SHIP section 12.2.2 compliance.

The inspection baseline is the published PR 23 head after focused lifecycle
remediation. Its full revision is retained only in the local review record and
is intentionally not published here. Exact-head CI, full normal and race
tests, vet, and repeated focused lifecycle tests pass. The source remains a PR
head rather than a merged release, and there is no bounded live
interoperability evidence in this document.

## Implemented Arbitration Rule

For simultaneous trusted reconnect attempts for one remote identity, the Hub
selects the direction initiated by the higher identity key. The key is the
Subject Key Identifier (SKI). The implementation compares normalized lexical
values; this page does not
define a new identity representation or ordering rule.

| Local vs remote identity key | Direction retained by the inspected implementation | Required disposition of the other direction |
| --- | --- | --- |
| Local is higher | Local outbound | A simultaneous trusted inbound attempt is rejected before protocol activation while the outbound attempt is initiating. |
| Remote is higher | Remote inbound | The inbound attempt becomes the retained direction; a competing local outbound attempt must not become a second active connection. |

This is an implementation arbitration rule, not an assertion that the
standard's complete collision algorithm, timing, replacement rules, or all
failure cases have been implemented. Equal SKIs, non-trusted admission,
multi-peer interoperability, and on-wire peer behavior are outside this
candidate's supported scope.

## Inbound Ownership And Activation Order

For a retained inbound connection, the inspected Hub path constructs the protocol
connection, registers it as the inbound owner, then calls `Run`. Registration
therefore precedes data-pump initialization. A connection rejected by the
collision rule is closed instead of entering that activation path.

The reviewed lifecycle follow-up adds the same boundary to the
registration-to-Run interval: if shutdown wins after registration, registration
closes and rejects the connection; `Run` must not initialize data processing
after that terminal close.

## Terminal Pre-Run Behavior

The candidate requires one terminal outcome for an inbound connection closed
before `Run`, whether shutdown or a competing replacement caused the close:

- terminal close is reported exactly once;
- a later `Run` does not initialize data processing; and
- no read or write data pump starts after the close.

The inspected websocket lifecycle initializes its channels before pump startup,
uses once-only startup and shutdown guards, and checks terminal state before
starting pumps. This makes a pre-start close safe to observe, but it does not
prove transport delivery, peer-visible close behavior, or a complete
conformance result.

## Evidence Status

| Claim | Evidence status | Boundary |
| --- | --- | --- |
| Higher-key initiated direction is selected during the inspected collision path. | Supported implementation evidence | Immutable source baseline and PR source inspection; no live run. |
| A losing trusted inbound is rejected before protocol activation while a higher-key outbound is initiating. | Supported implementation evidence | Published PR head and repeated focused tests. |
| Inbound ownership is registered before data-pump startup. | Supported implementation evidence | Published PR head and repeated focused tests. |
| Shutdown or competing replacement before `Run` has one terminal close and no post-close pump. | Supported candidate implementation evidence | Published PR head; focused tests pass normally and under the race detector. |
| Full SHIP 12.2.2 compliance or interoperable peer behavior. | Not established | Requires permitted specification evidence and bounded interoperability validation. |

## Exact Falsifiers

The following are direct falsifiers for this candidate:

1. In a focused trusted collision with the local identity key higher, an inbound attempt
   reaches `Run`, initializes data processing, accepts protocol traffic, or remains
   registered while the local outbound attempt is initiating.
2. In the inverse ordering, the remote-higher inbound direction is not retained,
   or the competing local outbound direction becomes a second active
   connection.
3. Instrumentation observes `InitDataProcessing`, a read pump, or a write pump
   before the inbound owner is registered.
4. After shutdown or a competing replacement closes an inbound connection before
   `Run`, invoking `Run` starts a pump, or either the data close or the Hub
   terminal callback occurs other than exactly once.

The corresponding source locators and their current evidence limits are kept
in [EV-20260729-001](../../evidence/EV-20260729-001.md). Promotion from this
candidate requires a final immutable merged or released source pin and
separate evidence sufficient for any interoperability or conformance claim.
