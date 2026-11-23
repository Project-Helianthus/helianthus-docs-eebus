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
unauthenticated catalogue. This page records the revisions below and declares
the mappings from those recorded revisions. It must not be read as a single
"eeBUS version". Fact pages:
[SHIP 1.0.1](ship-1.0.1.md),
[SHIP 1.1.0](ship-1.1.0.md),
[pairing service](ship-pairing-service-1.0.0.md),
[installation requirements](ship-installation-requirements-1.1.0.md),
[SPINE introduction](spine-introduction-1.3.0.md),
[SPINE protocol](spine-protocol-1.3.0.md),
[SPINE resources](spine-resources-1.3.0.md).

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

| Family | Recorded documents | Mapping |
| --- | --- | --- |
| SHIP | SHIP Specification 1.0.1 (2019-11-04); SHIP Specification 1.1.0 (2025-09-22); SHIP Pairing Service 1.0.0 (2025-12-03); SHIP Requirements for Installation Process 1.1.0 (2025-10-10). Helianthus declares SHIP 1.0.1. SHIP 1.1.0 is a documented later revision. | Declared from those recorded revisions. |
| SPINE | SPINE Introduction 1.3.0 (2023-08-31); SPINE Protocol Specification 1.3.0 (2023-08-31); SPINE Resource Specification 1.3.0 (2023-08-31). | Declared from those recorded revisions. |
| E-Mobility / EVSE | EVSE Commissioning and Configuration 1.0.1 (2019-07-01); EV Commissioning and Configuration 1.0.1 (2019-07-01); EV Charging Electricity Measurement 1.0.1 (2019-07-01); Coordinated EV Charging 1.0.1 (2019-07-01); EV Charging Summary 1.0.1 (2019-07-01); Optimization of Self-Consumption During EV Charging 1.0.1b (2019-07-01); Overload Protection by EV Charging Current Curtailment 1.0.1b (2019-07-01); EV State of Charge 1.0.0 RC1 (2020-05-18). A release-candidate token is recorded as printed and conditions nothing. | Declared from those recorded revisions. |
| Grid connection point | Monitoring of Grid Connection Point 1.0.0 (2022-12-22); Monitoring of Power Consumption 1.0.0 (2022-12-22); Limitation of Power Consumption 1.0.0 (2022-10-14); Limitation of Power Production 1.0.0 (2022-12-22); Incentive-Table based power consumption management 1.0.0 RC3 (2022-12-21); Time of Use Tariff 1.0.0 (2024-07-12); Power Demand Forecast 1.0.0 (2024-07-12); Power Envelope 1.0.0 (2024-07-19). Implementation Guideline Limitation of Power Consumption 1.0.0 (2024-07-09). High-level test specifications: Limitation of Power Consumption 1.0.1 (2025-11-29); Limitation of Power Production 1.0.1 (2025-11-29); Monitoring of Grid Connection Point 1.0.1 (2025-11-29); Monitoring of Power Consumption 1.0.1 (2025-11-29). | Declared from those recorded revisions. |
| Inverter / PV and stationary BESS | Monitoring of Inverter 1.0.0 (2023-12-31); Monitoring of Battery 1.0.0 (2023-12-31); Monitoring of PV String 1.0.0 RC4 (2022-12-22); Control of Battery 1.0.0 (2023-12-31); Visualization of Aggregated Photovoltaic Data 1.0.0 RC1 (2019-09-23); Visualization of Aggregated Battery Data 1.0.0 RC1 (2019-09-23). A release-candidate token is recorded as printed and conditions nothing. | Declared from those recorded revisions. |
| HVAC | HVAC Temperature use cases package 1.0.0 (2022-11-22); HVAC System Function use cases package 1.0.0 (2022-11-22); Configuration of DHW System Function 1.0.0 (2022-11-22); Configuration of Room Heating System Function 1.0.0 (2022-11-22); Configuration of Room Cooling System Function 1.0.0 (2022-11-22); Monitoring of DHW System Function 1.0.0 (2022-11-22); Monitoring of Room Heating System Function 1.0.0 (2022-11-22); Monitoring of Room Cooling System Function 1.0.0 (2022-11-22); Configuration of DHW Temperature 1.0.0 (2022-11-22); Configuration of Room Cooling Temperature 1.0.0 (2022-11-22); Configuration of Room Heating Temperature 1.0.0 (2022-11-22); Monitoring of DHW Temperature 1.0.0 (2022-11-22); Monitoring of Outdoor Temperature 1.0.0 (2022-11-22); Monitoring of Room Temperature 1.0.0 (2022-11-22); Visualization of Heating Area Name 1.0.0 (2022-11-22); Optimization of Self Consumption by Heat Pump Compressor Flexibility 1.0.0 (2022-11-22). | Declared from those recorded revisions. The thermal, temperature, hot-water and system-function mappings are declared and are not held back. |

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
Inverter / PV and stationary BESS, and HVAC rows record the revisions in the
table above. The recorded revisions declare the mappings. Flexible Load /
Smart Heater DHW is unavailable. Monitoring and Control of Smart Grid Ready
Conditions is unavailable. Nothing is built from assumptions about those two
drafts. What the documents do not give, including each open point named on the
fact pages, stays unknown.

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

## Declared mappings

The recorded revisions declare the mappings. A release-candidate token a
document prints is recorded as printed and conditions nothing. The dated
installation-process table and the implementation-comparison snapshot stay
dated evidence, separate from these recorded revisions.

This ledger does not make Matter and eeBUS equivalent. They remain separately
versioned native bindings with a deliberate mapping and loss record.

## Recorded revisions

The families SHIP, SPINE, E-Mobility / EVSE, Grid connection point, Inverter /
PV and stationary BESS, and HVAC record the titles, versions and cover dates
in the table above. The recorded revisions declare the mappings. What a
document does not give stays unknown.
