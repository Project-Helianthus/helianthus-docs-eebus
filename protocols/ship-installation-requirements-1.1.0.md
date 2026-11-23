---
canonical_source: "Project-Helianthus/helianthus-docs-eebus:protocols/ship-installation-requirements-1.1.0.md"
owner_domain: "protocols"
license: "CC0-1.0"
publication_status: "publishable"
claim_status: "evidence-backed"
source_class: "vendor_public"
evidence_ids: "EV-20260711-001"
hypothesis_status: "publishable"
falsifier: "A row invents a requirement identifier, or fills a detail this document places in another document."
---

# SHIP Requirements for Installation Process 1.1.0

Numbered requirements keep the identifier, the capital-keyword obligation, and the clause. A subject is at most 20 words. Details this document places in SEIP, the SHIP specification, or the pairing service are named and not filled.

## Numbered requirements

| requirement id | category | obligation (SHALL, SHOULD, MAY) | subject (own words, at most 20) | clause |
| --- | --- | --- | --- | --- |
| SRIP-210/1 | address assignment | SHALL | The device SHALL start with an active DHCP client on IPv4 and on IPv6. | §2.1 |
| SRIP-210/2 | address assignment | SHALL | If DHCP fails, the device SHALL self-assign IPv4 link-local, or IPv6 SLAAC or link-local. | §2.1 |
| SRIP-210/3 | address assignment | SHOULD | The device SHOULD let the user choose a static IPv4 or IPv6 address. | §2.1 |
| SRIP-210/4 | address assignment | no capital keyword | Support of both IPv4 and IPv6 is recommended. No capital keyword is used. | §2.1 |
| SRIP-220/1 | identity and TXT | SHALL | Every TXT value SHALL be encoded as UTF-8. | §2.2 |
| SRIP-220/2 | identity and TXT | SHALL NOT | Whitespace SHALL NOT appear in TXT values. | §2.2 |
| SRIP-220/3 | identity and TXT | no capital keyword | Hyphen-minus U+002D is the recommended stand-in for whitespace. No capital keyword. | §2.2 |
| SRIP-220/4 | identity and TXT | SHOULD NOT | Devices already sold SHOULD NOT change their SHIP ID. | §2.2 |
| SRIP-220/5 | identity and TXT | SHALL | New devices whose firmware is not shared with sold devices SHALL adopt the new format of the SHIP ID. | §2.2 |
| SRIP-220/6 | identity and TXT | SHALL | The IANA PEN field SHALL be one to six characters of that manufacturer’s PEN. | §2.2 |
| SRIP-220/7 | identity and TXT | SHALL | VPID SHALL be globally unique for that PEN, and the pair SHALL identify the node. | §2.2 |
| SRIP-220/8 | identity and TXT | SHOULD | VPID SHOULD match the printed serial number or a similar on-device marking. | §2.2 |
| SRIP-220/9 | identity and TXT | SHALL NOT | A peer SHIP ID in a different format SHALL NOT be treated as an error. | §2.2 |
| SRIP-220/10 | identity and TXT | SHALL | If brand is set, it SHALL be the brand name, at most 32 characters. | §2.2 |
| SRIP-220/11 | identity and TXT | MAY | The brand MAY match the PEN brand, or it MAY be a different brand. | §2.2 |
| SRIP-220/12 | identity and TXT | SHOULD | Type SHOULD be a readable device-type string of at most 32 characters. | §2.2 |
| SRIP-220/13 | identity and TXT | SHOULD | Model SHOULD be a readable product-model string of at most 32 characters. | §2.2 |
| SRIP-220/14 | identity and TXT | SHOULD | Serial SHOULD be the printed serial or similar marking, at most 32 characters. | §2.2 |
| SRIP-220/15 | identity and TXT | SHALL | cat SHALL be set to the device categories that apply. | §2.2 |
| SRIP-220/16 | identity and TXT | SHALL | cat SHALL be comma-separated category numbers with no whitespace. | §2.2 |
| SRIP-220/17 | identity and TXT | SHALL NOT | cat SHALL NOT repeat a category number. | §2.2 |
| SRIP-220/18 | identity and TXT | SHALL | If categories change later, cat SHALL be changed to match. | §2.2 |
| SRIP-220/19 | identity and TXT | SHALL | A conforming implementation SHALL set brand in its own TXT record. | §2.2 |
| SRIP-220/20 | identity and TXT | SHALL NOT | Missing or empty brand in another node’s TXT record SHALL NOT be an error. | §2.2 |
| SRIP-220/21 | identity and TXT | SHALL | A conforming implementation SHALL set model in its own TXT record. | §2.2 |
| SRIP-220/22 | identity and TXT | SHALL NOT | Missing or empty model in another node’s TXT record SHALL NOT be an error. | §2.2 |
| SRIP-220/23 | identity and TXT | SHALL | A conforming implementation SHALL set cat in its own TXT record. | §2.2 |
| SRIP-220/24 | identity and TXT | SHALL NOT | Missing cat in another node’s TXT record SHALL NOT be an error. | §2.2 |
| SRIP-230/1 | announcement | no capital keyword | With SHIP activated, announce by mDNS while another connection can still be opened. | §2.3 |
| SRIP-310/1 | QR payload | SHALL | The SHIP QR payload SHALL be allowed as its own QR code. | §3.1 |
| SRIP-310/2 | QR payload | SHALL | The SHIP QR payload SHALL be allowed inside a QR code that also holds other data. | §3.1 |
| SRIP-310/3 | QR payload | MAY | A picture MAY sit at the centre of the QR symbol. | §3.1 |
| SRIP-310/4 | QR payload | SHALL | The QR symbol SHALL carry the SHIP ID plus the SKI for secp256r1. | §3.1 |
| SRIP-310/5 | QR payload | SHOULD | Error correction at medium level is a SHOULD. | §3.1 |
| SRIP-310/6 | QR payload | SHOULD | QR size SHOULD be the larger of 2 cm by 2 cm and 0.33 mm per module. | §3.1 |
| SRIP-310/7 | QR payload | SHALL | QR key-value pairs SHALL follow the specified order. | §3.1 |
| SRIP-310/8 | QR payload | SHALL NOT | A semicolon SHALL only separate QR pairs and SHALL NOT be used otherwise. | §3.1 |
| SRIP-310/9 | QR payload | SHALL | SKI and PIN SHALL be groups of four, with a space every four hex digits. | §3.1 |
| SRIP-310/10 | QR payload | MAY | The public key MAY be placed in the QR code instead of the SKI alone. | §3.1 |
| SRIP-310/11 | QR payload | MAY | The public certificate MAY be offered as a file at a URL. | §3.1 |
| SRIP-310/12 | QR payload | SHALL | NOMINALPOWER SHALL use the form a comma b, without quotation marks. | §3.1 |
| SRIP-310/13 | QR payload | SHALL | Component a SHALL be a negative integer or zero, magnitude in production watts. | §3.1 |
| SRIP-310/14 | QR payload | SHALL | Component b SHALL be zero or an integer above zero; its magnitude is consumption watts. | §3.1 |
| SRIP-310/15/1 | QR payload | no capital keyword | Where the pairing service applies, one or more fingerprint fields are mandatory. | §3.1 |
| SRIP-310/15/2 | QR payload | SHALL | Role devA SHALL provide FPH256, because SHIP mandates secp256r1. | §3.1 |
| SRIP-310/16 | QR payload | no capital keyword | Where the pairing service applies, SPSEC is mandatory. | §3.1 |
| SRIP-310/17 | QR payload | SHALL | A reader SHALL skip unknown content at the end of the QR payload. | §3.1 |
| SRIP-310/18 | QR payload | SHALL | A conforming implementation SHALL end SHIP QR data with ENDSHIP. | §3.1 |
| SRIP-310/19 | QR payload | SHALL NOT | A missing ENDSHIP mark SHALL NOT be treated as an error. | §3.1 |
| SRIP-321/1 | public key fields | SHALL | Public-key QR fields SHALL be unprefixed hex UTF-8, spaced every four digits. | §3.2.1 |
| SRIP-321/2 | public key fields | MAY | Those hex fields MAY use digits and either letter case A-F or a-f. | §3.2.1 |
| SRIP-322/1 | certificate URL | SHALL | The certificate URL SHALL be unique per device and SHOULD contain the SKI. | §3.2.2 |
| SRIP-322/2 | certificate URL | SHALL NOT | That certificate URL SHALL NOT contain a semicolon. | §3.2.2 |
| SRIP-322/3 | certificate URL | SHALL | The certificate file SHALL be PEM as specified by RFC7468. | §3.2.2 |
| SRIP-322/4 | certificate URL | MAY | The file MAY hold more than one certificate, as a chain. | §3.2.2 |
| SRIP-322/5 | certificate URL | SHALL | In a chain, the device’s own certificate SHALL be first. | §3.2.2 |
| SRIP-322/6 | certificate URL | SHALL | Each later certificate SHALL directly certify the certificate before it. | §3.2.2 |
| SRIP-A20/1 | user menu | SHALL | A SPINE-over-SHIP device SHALL provide a user menu. GCPH is excluded. | clause not printed |
| SRIP-A20/2 | user menu | SHOULD | That menu SHOULD be named EEBUS. | clause not printed |
| SRIP-A20/3 | user menu | SHOULD | The EEBUS menu SHOULD be located in general settings. | clause not printed |
| SRIP-A20/4 | user menu | SHALL | The EEBUS menu SHALL list SHIP nodes found on the network. | clause not printed |
| SRIP-A20/5 | user menu | SHALL | Selecting a node SHALL open details and a way to start a SHIP connection. | clause not printed |
| SRIP-A20/6 | user menu | MAY | The node list MAY be filtered to peers a useful connection can reach. | clause not printed |
| SRIP-A20/7 | user menu | SHALL | Displayed nodes SHALL state the SHIP ID plus the SKI. | clause not printed |
| SRIP-A20/8 | user menu | SHOULD | Those four strings, brand then type then model then serial, SHOULD be shown when the peer provides them. | clause not printed |
| SRIP-A20/9 | user menu | SHOULD | SHIP nodes SHOULD be ordered by type, under headings. | clause not printed |
| SRIP-A40/1 | cipher selection | SHOULD NOT | Cipher suite TLS_ECDHE_ECDSA_WITH_AES_128_CCM_8 SHOULD NOT be used. | clause not printed |
| SRIP-A40/2 | cipher selection | SHOULD NOT | Extension truncated_hmac is marked SHOULD NOT. | clause not printed |

## Obligations without an identifier

| obligation | subject | clause |
| --- | --- | --- |
| SHALL | Requirements of this document SHALL be marked with the SRIP-xyz form. | §1.3.2 |
| no capital keyword | TXT values forbid semicolon and Unicode categories Control, Format, and Separator. | §2.2 |
| no capital keyword | Uniqueness of id, and the 63-byte maximum, are kept from the cited SHIP text. | §2.2 |
| SHOULD | In every case other than the two tagged id bullets, a conforming node SHOULD match the new id format. | §2.2 |
| SHOULD NOT | Verification mode auto accept SHOULD NOT be implemented. | §2.5 |
| SHALL | An MPO control unit, or a smart-meter gateway, SHALL implement devZ. | §2.5 |
| SHALL | A consumer node that implements LPC or LPP SHALL implement devA. | §2.5 |
| SHOULD | A consumer node without LPC and LPP, but with a use case such as POEN or TOUT, SHOULD implement devA. | §2.5 |
| SHALL | A SPINE-over-SHIP device that is to take part in SEIP SHALL provide a QR code. GCPH is excluded. | §3.1 |
| no capital keyword | Inside SEIP a combined QR is allowed only as the sole code, or when labels identify the EEBUS content. | §3.1 |
| no capital keyword | A node that has a PIN puts it in the QR symbol, per SHIP as restated here. | §3.1 |
| SHALL | A QR public key SHALL use the same compressed or uncompressed form as the certificate. | §3.2.1 |
| no capital keyword | In post-trust, an unknown certificate is taken in during the TLS handshake, then dropped if the user rejects it. | clause not printed |
| no capital keyword | Trusted SKI: local SHA-1 of the public key. Trusted fingerprint: a local computation. | clause not printed |
| no capital keyword | If an operator requires a fingerprint or the whole certificate, the vendor has to let the user deliver it. | clause not printed |
| SHALL | Cipher suite TLS_ECDHE_ECDSA_WITH_AES_128_CBC_SHA256 SHALL be supported. | clause not printed |
| SHALL | A node aligned with SHIP release 1.1.0 SHALL implement the three key-material-state messages named in Annex A.6. | clause not printed |
| SHALL NOT | SHIP restated here: SHALL NOT remain in auto accept past two minutes, and avoid the mutual case. | clause not printed |
| no capital keyword | SHIP, as restated here, requires a node to search for other nodes. | clause not printed |
| no capital keyword | Required pre-trust: A aborts unknown B, may show the SKI, and may finish a retry after acceptance. | clause not printed |

## Fields

| field | type | bounds | clause |
| --- | --- | --- | --- |
| TXT key txtvers | version number | not in the sources | §2.2, Table 2 |
| TXT key id | identifier string | maximum length 63 bytes, kept from the cited SHIP text; uniqueness kept; PEN 1–6 characters; VPID globally unique for that PEN | §2.2, Table 2 |
| TXT key path | string, a wss path | not in the sources | §2.2, Table 2 |
| TXT key ski | 40-digit hexadecimal string; 160-bit SKI | 40 hex digits | §2.2, Table 2 |
| TXT key register | Boolean | Boolean literals not enumerated | §2.2, Table 2 |
| TXT key ecc | Boolean | Boolean literals not enumerated | §2.2, Table 2 |
| TXT key brand | string, brand name | at most 32 characters | §2.2, Table 2 |
| TXT key type | human-readable string, device type | at most 32 characters | §2.2, Table 2 |
| TXT key model | human-readable string, product model | at most 32 characters | §2.2, Table 2 |
| TXT key serial | string; serial number or similar marking printed on the device | at most 32 characters | §2.2, Table 2 |
| TXT key cat | string matching <dc>[,<dc>]* | comma-separated; no whitespace; no repeated number | §2.2, Table 1, Table 2 |
| QR item 1 SHIP | structure marker, no value defined here | fixed token SHIP | §3.1 |
| QR item 2 SKI | SKI, grouped as in SRIP-310/9 | space after every four hex digits; groups of four characters | §3.1 |
| QR item 3 PIN | PIN, grouped as in SRIP-310/9 | grouping only; repertoire and length not in the sources | §3.1 |
| QR item 4 ID | string | see TXT id | §3.1 |
| QR item 5 BRAND | string | at most 32 characters when the TXT rule is applied | §3.1 |
| QR item 6 TYPE | string | at most 32 characters when the TXT rule is applied | §3.1 |
| QR item 7 MODEL | string | at most 32 characters when the TXT rule is applied | §3.1 |
| QR item 8 BSKI | SKI | not in the sources | §3.1 |
| QR item 9 B2SKI | SKI | not in the sources | §3.1 |
| QR item 10 PKEY | unprefixed hexadecimal UTF-8 of subjectPublicKey | space after every fourth hex digit; letter case 0-9, A-F, a-f; compressed or uncompressed form must match the certificate; length depends on curve and form | §3.1, §3.2.1 |
| QR item 11 PBKEY | same encoding as PKEY | same encoding bounds as PKEY; bit length not stated | §3.1, §3.2.1 |
| QR item 12 PB2KEY | same encoding as PKEY | same encoding bounds as PKEY; bit length not stated | §3.1, §3.2.1 |
| QR item 13 CERTURL | URL; file is PEM per [RFC7468] | URL unique for the device; SHOULD contain the matching SKI; semicolon forbidden in the URL | §3.1, §3.2.2 |
| QR item 14 CERTBURL | URL; PEM file | same URL and PEM rules as CERTURL | §3.1, §3.2.2 |
| QR item 15 CERTB2URL | URL; PEM file | same URL and PEM rules as CERTURL | §3.1, §3.2.2 |
| QR item 16 SERIAL | string | at most 32 characters when the TXT rule is applied | §3.1 |
| QR item 17 CAT | string | see TXT cat | §3.1 |
| QR item 18 NOMINALPOWER | two integers written <a>,<b> | a SHALL be a negative integer or zero; b SHALL be zero or an integer above zero; magnitudes are absolute electrical nominal power | §3.1 |
| QR item 19 FPH256 | fingerprint; encoding not stated here | not in the sources | §3.1 |
| QR item 20 BFPH256 | fingerprint; encoding not stated here | not in the sources | §3.1 |
| QR item 21 B2FPH256 | fingerprint; encoding not stated here | not in the sources | §3.1 |
| QR item 22 SPSEC | not in the sources | not in the sources | §3.1 |
| QR item 23 further pairs | not in the sources | not in the sources | §3.1 |
| QR item 24 ENDSHIP | token | mark printed as ENDSHIP | §3.1 |

## Commands, limits and timing

| topic | statement | clause |
| --- | --- | --- |
| TXT values, SHIP ID, categories | Already-sold devices: changing the SHIP ID is a SHOULD NOT. SRIP-220/4 §2.2 –209 See SHIP-ID change semantics below. | §2.2 |
| TXT values, SHIP ID, categories | Devices built newly, and not sharing firmware with units already sold: SHALL adopt the new format. SRIP-220/5 §2.2 –211 | §2.2 |
| TXT values, SHIP ID, categories | Every remaining case: a conforming node SHOULD use an id that matches the new format. This bullet has no SRIP id. The remaining cases are not listed. §2.2 –213 | §2.2 |
| TXT values, SHIP ID, categories | <IANA PEN> SHALL be one to six characters, the manufacturer’s [IANA PEN]. SRIP-220/6 §2.2 –218 | §2.2 |
| TXT values, SHIP ID, categories | <VPID> SHALL be globally unique for that PEN. The pair (PEN, VPID) SHALL identify this SHIP node globally. SRIP-220/7 §2.2 –221 | §2.2 |
| TXT values, SHIP ID, categories | VPID SHOULD be the device serial number, or similar information printed on the device. SRIP-220/8 §2.2 –223 | §2.2 |
| TXT values, SHIP ID, categories | A conforming node SHALL NOT treat a peer SHIP ID of a different format as an error. SRIP-220/9 §2.2 –225 | §2.2 |
| Trust states | Pre-trust: trust is in place before a TLS handshake starts, or before that handshake completes successfully. This is the preferred method. §2.4 –298 The terms are first defined in SHIP 1.1.0; the principles are said to apply since SHIP 1.0.0 because they are not tied to one protocol detail. §A.3 –530 | §2.4 |
| Trust states | For node A in pre-trust, applications on A accept an incoming SHIP attempt from B only after A’s user has already trusted B. §A.3 –532 | clause not printed |
| Trust states | Post-trust: trust is established after the TLS handshake has completed. §2.4 –298 If A allows post-trust, it first accepts an incoming attempt from a still-untrusted B, then asks the user to trust that node before further communication. §A.3 –546 | §2.4 |
| Trust states | As TLS server in that post-trust case, A accepts the received TLS client certificate during the handshake without checking its public key. §A.3 –548 | clause not printed |
| Trust states | State Hello, together with the messages of that state, gives the user time to check a certificate that is still untrusted. §A.3 –550 | clause not printed |
| Trust states | Post-trust means an unknown certificate is accepted automatically during the TLS handshake and is dropped when the user withholds acceptance of the node or of the certificate. The text says this needs careful implementation. §A.3 –553 | clause not printed |
| Trust states | SHIP Pairing Service is also a pre-trust mechanism. §2.4 | §2.4 |
| Trust states | Several curves on one node produce a distinct SKI per curve, and a distinct certificate or fingerprint per curve. Curve details and priority rules are in [SHIP]. §2.4 –301 | [SHIP], §2.4 |
| Pairing methodologies | That MPO control unit, or a smart-meter gateway, SHALL implement devZ from [SHIPPairingService]. §2.5 –315 | §2.5 |
| Pairing methodologies | A consumer node that implements at least one of LPC or LPP SHALL implement devA. §2.5 –317 | §2.5 |
| Pairing methodologies | A consumer node that implements neither LPC nor LPP, but has another use case aimed at such an MPO unit, with POEN and TOUT as the printed instances, SHOULD implement devA. §2.5 –321 | §2.5 |
| Pairing methodologies | A future extension of [SHIPPairingService] that could pair any SHIP node with any other might make SHIP Pairing Service mandatory for every SHIP node. That is not a present obligation. §2.5 –324 | §2.5 |
| Certificates, curves, cipher suites, regulation | TLS_ECDHE_ECDSA_WITH_AES_128_CBC_SHA256 SHALL be supported. For critical infrastructure it might be required only together with TLS extension encrypt_then_mac, per [RFC7366]. §A.4 –584 | [RFC7366] |
| Certificates, curves, cipher suites, regulation | TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256: support is recommended. The sentence uses an exclamation, not a capital SHOULD. §A.4 –586 | clause not printed |
| Certificates, curves, cipher suites, regulation | TLS_ECDHE_ECDSA_WITH_AES_128_CCM_8 is marked SHOULD NOT (SRIP-A40/1). The text says regulators are likely to forbid it for critical infrastructure, and that [RFC8447] no longer recommends it. §A.4 –590 | [RFC8447] |
| Certificates, curves, cipher suites, regulation | encrypt_then_MAC ([RFC7366]): recommended when CBC cipher suites are used, and possibly required by regulators in critical infrastructure. §A.4 –597 The earlier sentence spells the same extension encrypt_then_mac. §A.4 | [RFC7366] |
| Certificates, curves, cipher suites, regulation | truncated_hmac is marked SHOULD NOT (SRIP-A40/2). Regulators may forbid it in critical infrastructure. §A.4 –600 | clause not printed |
| Certificates, curves, cipher suites, regulation | topic: Permitted lifetime; what this publication says about SHIP: SHIP sets no upper bound.; what it says regulators may do: May require a lifetime of only a few years, or shorter. No integer is printed. | clause not printed |
| Certificates, curves, cipher suites, regulation | topic: Checking lifetime; what this publication says about SHIP: SHIP permits accepting an expired certificate, and then recommends treating it like a self-signed certificate.; what it says regulators may do: Usually stricter for a PKI. Sometimes a self-signed certificate is allowed for one node that an authorized role manages, that role staying responsible for communication security for the node’s life in that installation. In those cases the lifetime of that self-signed certificate need not be checked. | clause not printed |
| Certificates, curves, cipher suites, regulation | topic: Self-signed certificates; what this publication says about SHIP: Allowed.; what it says regulators may do: A PKI may be required. Self-signed certificates are still usually allowed when a particular role authenticates and maintains them. | clause not printed |
| Bounds collected | item: SHIP ID; bound: maximum 63 bytes; unique; new pattern i:<IANA PEN>_u:<VPID>; locator: §2.2 –221 | §2.2 |
| Bounds collected | item: IANA PEN in that pattern; bound: 1 to 6 characters; locator: SRIP-220/6 §2.2 –218 | §2.2 |
| Bounds collected | item: brand, type, model, serial; bound: at most 32 characters; locator: SRIP-220/10, SRIP-220/12, SRIP-220/13, SRIP-220/14 | clause not printed |
| Bounds collected | item: cat; bound: pattern <dc>[,<dc>]*; numbers 1–7; no whitespace; no duplicate; locator: SRIP-220/16, SRIP-220/17, Table 1 | Table 1 |
| Bounds collected | item: TXT ski; bound: 40 hex digits; 160-bit secp256r1 SKI; locator: Table 2 | Table 2 |
| Bounds collected | item: QR SKI and PIN; bound: groups of four; space every four hex digits; locator: SRIP-310/9 | clause not printed |
| Bounds collected | item: QR public keys; bound: unprefixed hex; space every four hex digits; case 0-9/A-F/a-f; form matches the certificate; locator: SRIP-321/1, SRIP-321/2, §3.2.1 –478 | §3.2.1 |
| Bounds collected | item: NOMINALPOWER; bound: <a>,<b>; a integer ≤ 0; b integer ≥ 0; watts; no scale factor; locator: SRIP-310/12–SRIP-310/14 | clause not printed |
| Bounds collected | item: QR size; bound: at least the larger of 2 cm by 2 cm and 0.33 mm per module; locator: SRIP-310/6 | clause not printed |
| Bounds collected | item: auto accept duration; bound: not more than 2 minutes, as restated from [SHIP]; locator: §B.1 –674 | [SHIP] |
| Bounds collected | item: Certificate lifetime; bound: no upper bound in SHIP, as restated in Table 3; locator: §A.5 Table 3 | Table 3 |

## Open points

| point | what is not filled | clause |
| --- | --- | --- |
| installation steps | The process steps are placed in SEIP and are not filled here. | SHIP Requirements for Installation Process 1.1.0 §1 |
| SHIP behaviour cited from the SHIP specification | Details that this document places in the SHIP specification are not copied here. | SHIP Requirements for Installation Process 1.1.0 §1.1.1 |
| pairing-service behaviour | Details that this document places in the pairing service are not copied here. | SHIP Requirements for Installation Process 1.1.0 §2.5 |
| LPP, POEN, and TOUT | The names are used and not expanded. | SHIP Requirements for Installation Process 1.1.0 §1.2 |
