---
canonical_source: "Project-Helianthus/helianthus-docs-eebus:protocols/eebus-normative-source-ledger.md"
owner_domain: "protocols"
license: "CC0-1.0"
publication_status: "publishable"
claim_status: "evidence-backed"
source_class: "vendor_public"
evidence_ids: "EV-20260905-001,EV-20260909-001"
hypothesis_status: "publishable"
falsifier: "An authorised inventory of the exact current document metadata, or a changed public EEBUS catalogue or licence, contradicts a ledger row."
---

# STD-01 eeBUS Normative Source Ledger

## Purpose and status

This ledger is the publishable version record for STD-01. It separates the
normative eeBUS corpus from Helianthus implementation dependencies. It is not a
copy of a specification, a certification statement, or evidence that a mapping
is conformant.

The public [EEBUS Specifications & Media catalogue](https://www.eebus.org/specifications-media/)
was accessed on 2026-09-05. It names SHIP, SPINE, and the E-Mobility, Grid
Connection Point, Inverter, and HVAC collections, but requires registration to
download their current versions and does not expose their exact revisions in the
unauthenticated catalogue. Consequently, this page records each current exact
revision as **unresolved**. It must not be read as a single "eeBUS version".

The public catalogue evidence is recorded in
[EV-20260905-001](../evidence/EV-20260905-001.md). The Matter draft is owned
by its separate pin and is deliberately outside this ledger.

The dated public installation-process dependency baseline is recorded in
[EV-20260909-001](../evidence/EV-20260909-001.md). It is an additional public
source record; it does not resolve a current corpus row.

## Source and redistribution boundary

EEBUS says the listed specifications are free to use, while the catalogue
requires registration for current downloads. Its [terms of use](https://www.eebus.org/terms-of-use/)
state that specifications and tools are copyright-protected; they permit
informational use and products based on them, prohibit altered or misleading
dissemination, and reserve other use or exploitation unless expressly allowed.

This repository therefore publishes only source links, document-family names,
access observations, exact metadata that is independently publishable, and
derived Helianthus boundaries. It does not commit specification files, excerpts,
schemas, tables, screenshots, or a paraphrase of protected content. A future
authorised inventory may add exact metadata only after checking the applicable
terms and whether that metadata is itself publishable.

## Normative document-family ledger

| Family | Public source and access date | Public scope or catalogue maturity | Exact current revision | Source/access state | Mapping effect |
| --- | --- | --- | --- | --- | --- |
| SHIP | [Specifications & Media](https://www.eebus.org/specifications-media/), 2026-09-05 | Technical backbone transport specification; current document download requires registration. | **Unresolved** | Current revision was not visible to an unauthenticated reader. | Freeze SHIP-dependent lifecycle, transport, and conformance mappings only after an authorised metadata record identifies the revision. |
| SPINE | [Specifications & Media](https://www.eebus.org/specifications-media/), 2026-09-05 | Technical backbone data-model specification; current document download requires registration. | **Unresolved** | Current revision was not visible to an unauthenticated reader. | Freeze SPINE model and feature mappings only after an authorised metadata record identifies the revision. |
| E-Mobility / EVSE | [Solutions matrix](https://www.eebus.org/solutions/), 2026-09-05 | Released: LPC, MPC, CEVC, OSCEV, OPEV, EVCEM, EVCC, EVSECC. Release candidate: EVCS, EVSOC. In progress: SBEVC, DBEVC, NID. | **Unresolved for every collection/document** | Public matrix gives catalogue maturity, not exact current document metadata. | A mapping may name the individual use case and maturity; it cannot freeze a normative revision. In-progress and release-candidate rows require their own qualification gate. |
| Grid connection point | [Solutions matrix](https://www.eebus.org/solutions/), 2026-09-05 | Released: LPC, LPP, MGCP, MPC, TOUT, PODF, POEN. In progress: EPRQ, NID. | **Unresolved for every collection/document** | Public matrix gives catalogue maturity, not exact current document metadata. | Do not freeze grid behaviour, choreography, or failsafe semantics from catalogue labels alone. |
| Inverter / PV and stationary BESS | [Solutions matrix](https://www.eebus.org/solutions/), 2026-09-05 | Released: LPP, MOI, MOB, MPS. Release candidate: VAPD/VABD. The public catalogue groups photovoltaic and battery storage under Inverter; it does not expose a separate current BESS document revision. | **Unresolved for every collection/document** | Public matrix gives catalogue maturity, not exact current document metadata. | PV and BESS mappings stay separate by use case and capability. No BESS revision, topology, or control semantics may be inferred from an Inverter label. |
| HVAC | [Solutions matrix](https://www.eebus.org/solutions/), 2026-09-05 | Released: LPC, MPC, OHPCF, HVAC Temperature Package, HVAC System Function Package, CDSF. Release candidate: ITPCM, MCSGRC. In progress: FLOA, NID. | **Unresolved for every collection/document** | Public matrix gives catalogue maturity, not exact current document metadata. | Do not freeze thermal control, temperature, DHW, or system-function mappings until the relevant exact use-case revision is recorded. |

The public [EEBUS work page](https://www.eebus.org/our-work/) says SPINE is the
domain-unspecific data model used by the use cases and SHIP is the IP transport
used for SPINE transmission. That architecture statement does not supply a
revision, use-case conformance, or semantic equivalence between two protocols.

The matrix also links families to external standardisation references. Those
references are not treated as a substitute for the exact EEBUS collection
revision and are not pinned here; their own edition and applicability must be
verified by the consumer that relies on them.

## Dated public installation-process dependency baseline

The public EEBUS technical specification
[S<wbr>HIP Requirements for Installation Process, version 1.0.0, dated
2024-07-29](https://www.eebus.org/wp-content/uploads/2024/07/EEBUS_TS_S%68ipRequirementsForInstallationProcess_V1.0.0.pdf)
records the following dependency metadata for that document:

| Dependency | Baseline recorded by the 2024-07-29 public document | Status in this ledger |
| --- | --- | --- |
| S<wbr>HIP | minimum 1.0.1 | Dated installation-process dependency metadata; not a current S<wbr>HIP revision. |
| S<wbr>HIP | recommended 1.1.0 | Dated installation-process dependency metadata; not a current S<wbr>HIP revision. |
| SPINE | 1.3.0 | Dated installation-process dependency metadata; not a current SPINE revision. |

This source does not establish a current S<wbr>HIP, SPINE, or use-case corpus
revision; a use-case revision; an implementation conformance result; or a
semantic mapping. The S<wbr>HIP, SPINE, E-Mobility / EVSE, Grid connection point,
Inverter / PV and stationary BESS, and HVAC rows above therefore remain
**unresolved**. The five cross-protocol mapping records remain
`unknown_pending_std_01`; this source does not alter or promote them.

## Implementation comparison: immutable public Go sources

The following remote default-branch snapshot was verified on 2026-09-05. Each
commit link is an immutable public reference; the linked README and `go.mod`
files use the same commit. Module and repository versions express software
release and dependency state. They do not establish the newest normative EEBUS
specification.

| Component | Remote branch and immutable source | Declared implementation target | Consequence |
| --- | --- | --- | --- |
| `helianthus-ship-go` | `helianthus-v0.6`; [commit](https://github.com/Project-Helianthus/helianthus-ship-go/commit/9d38bfe04d57e7c8c73c59c1ddfc9b521e5045b0/); [README](https://github.com/Project-Helianthus/helianthus-ship-go/blob/9d38bfe04d57e7c8c73c59c1ddfc9b521e5045b0/README.md). | Its README declares an implementation of SHIP 1.0.1. | This is a code declaration, not evidence that SHIP 1.0.1 is the authorised current revision. |
| `helianthus-spine-go` | `helianthus-v0.7`; [commit](https://github.com/Project-Helianthus/helianthus-spine-go/commit/b0cdd8653ccc0c0d0133706172541e80179de818/); [README](https://github.com/Project-Helianthus/helianthus-spine-go/blob/b0cdd8653ccc0c0d0133706172541e80179de818/README.md). | Its README declares an implementation of SPINE 1.3. | This is a code declaration, not evidence that SPINE 1.3 is the authorised current revision. |
| `helianthus-eebus-go` | `helianthus-v0.7`; [commit](https://github.com/Project-Helianthus/helianthus-eebus-go/commit/c68cb5ee5d6bd9b2f8063bc4160325d3d183430a/); [README](https://github.com/Project-Helianthus/helianthus-eebus-go/blob/c68cb5ee5d6bd9b2f8063bc4160325d3d183430a/README.md); [`go.mod`](https://github.com/Project-Helianthus/helianthus-eebus-go/blob/c68cb5ee5d6bd9b2f8063bc4160325d3d183430a/go.mod). | The README declares SHIP 1.0.1 and SPINE 1.3.0 support. Its `go.mod` consumes `v0.6.1-helianthus.18.0.20260904230526-9d38bfe04d57` and SPINE module `v0.7.1-helianthus.9`. | A consumer must resolve the actual build list and module sums at its own exact HEAD. Neither the module versions nor the immutable source snapshot close a normative-document gap. |

The eebus-go README also records implementation limitations for parts of SHIP.
They are product compatibility constraints, not a licence to recreate the
normative document or to infer use-case coverage.

## Derived delivery boundary

`INT-04` and `INT-12` may continue conceptual design and independent work. They
must not freeze a SHIP/SPINE or use-case normative mapping until the affected
row has an exact authorised revision, a publishable source reference, and a
recorded compatibility decision. A candidate mapping must keep its use case,
role, lifecycle, control authority, loss, and unsupported states explicit.

This ledger does not make Matter and eeBUS equivalent. They remain separately
versioned native bindings with a deliberate mapping and loss record.

## Closure criterion for the unresolved rows

For each family needed by a proposed frozen mapping, an authorised reader must
record, without copying protected content:

1. document title, exact version/revision, maturity, and retrieval date;
2. a stable primary source reference and the access/licence boundary;
3. the exact Helianthus consumer and mapping decision, including loss and
   unsupported states; and
4. an independent review that confirms the public record contains no restricted
   text or identifiers.

The scoped STD-01 documentation delivery is complete when this ledger and its
unresolved rows are published and reviewed. The unresolved rows remain open
evidence work and do not claim that the full authorised normative package has
been inventoried.
