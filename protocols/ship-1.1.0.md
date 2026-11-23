---
canonical_source: "Project-Helianthus/helianthus-docs-eebus:protocols/ship-1.1.0.md"
owner_domain: "protocols"
license: "CC0-1.0"
publication_status: "publishable"
claim_status: "evidence-backed"
source_class: "vendor_public"
evidence_ids: "EV-20260711-001"
hypothesis_status: "publishable"
falsifier: "A row states a number or duty the named clause does not state, or selects one side of a conflict the clauses leave open."
---

# SHIP Specification 1.1.0

Facts of this revision: identifiers, ranges, presence, and duties, each with its clause. Text of the specification is not reproduced. A conflict that the clauses both print stays unresolved.

## Parameters

| parameter | clause | value or range | unit |
| --- | --- | --- | --- |
| keyMaterialStateResponse timely sending | §12.1.3.2 | range ≤ 20s | seconds |
| keyMaterialState timeout (wait for keyMaterialStateResponse, then retransmission) | §12.1.3.2 | range ≥ 30s; recommendation 30s | seconds |
| Certificate-update connection retry wait | §12.1.3.2 | range ≥ 5 minutes | minutes |
| Certificate-update transition stage | §12.1.3.2 | range ≥ 1 month; recommendation one quarter of the lifetime, floored at 1 month | not printed |
| PIN-entry penalty, 6th failed try | §13.4.4.3 | range 60–90s; recommendation 90s | seconds |
| PIN-entry penalty, 3rd failed try | §13.4.4.3 | range 10–15s; recommendation 15s | seconds |
| Wait-For-Ready prolongation | §13.4.4.1 | range 60–240s; recommendation 120s | seconds |
| Wait-For-Ready initial | §13.4.4.1 | range 60–240s; recommendation 120s | seconds |
| CmiTimeout | §13.4 | range 10–30s; recommendation 30s | seconds |
| Commissioning gate (user trust or second-factor trust) | §12.3.2 | range ≥ 32 | not printed |
| General-communication gate (user trust) | §12.3.2 | range ≥ 8 | not printed |
| Auto-accept window, maximum | §12.3.1.1 | range ≤ 120s; recommendation 60s | seconds |
| PIN length | §12.5 | range 8 to 16 hex digits | hexadecimal digits |
| SKI length | §12.2 | range 20 bytes, 40 hex digits | bytes |
| Pong timeout | §10.4 | range 10s | seconds |
| Ping minimum interval | §10.4 | range 50s | seconds |
| Maximum fragment length | §9.2 | range 512 bytes | bytes |
| MTU | §8 | range 1500 bytes | bytes |
| Maximum TCP retransmission timeout | §8.4 | recommendation 120s | seconds |
| Initial TCP retransmission timeout | §8.4 | recommendation 1s | seconds |
| Initial TCP retransmission count | §8.3 | recommendation 2 | not printed |

## Discovery

| DNS-SD item or TXT key | type | presence | meaning (own words) | clause |
| --- | --- | --- | --- | --- |
| service name | DNS-SD service | mandatory | Local discovery uses mDNS/DNS-SD and advertises the service name ship. | SHIP Specification 1.1.0 §7 |
| DNS-SD TTL | record lifetime | recommended | The DNS-SD record TTL should be 2 minutes. | SHIP Specification 1.1.0 §7 |
| service label | DNS-SD name | mandatory | The service label is underscore, the service name, a dot, and _tcp. | SHIP Specification 1.1.0 §7 |
| instance | DNS-SD instance | mandatory | A user-facing name of at most 63 UTF-8 bytes. On a collision the node chooses a new name. A parenthesized decimal should be appended, starting at (2). | SHIP Specification 1.1.0 §7 |
| host name | mDNS host | mandatory | Unique, at most 63 bytes, and should use the TXT identifier. | SHIP Specification 1.1.0 §7 |
| A and AAAA | address record | mandatory | A carries IPv4 and AAAA carries IPv6. | SHIP Specification 1.1.0 §7 |
| SRV | service location | mandatory | Carries the service name, the host name, and the port. No fixed port number is printed. | SHIP Specification 1.1.0 §7 |
| TXT record | TXT | mandatory | One TXT format, at most 400 bytes. Unknown keys are ignored. | SHIP Specification 1.1.0 §7 |
| txtvers | TXT key | mandatory, first key | Value 1. A missing key or any other value causes the TXT record to be discarded. | SHIP Specification 1.1.0 §7 Table 2 |
| id | TXT key | mandatory | Globally unique identifier, at most 63 bytes, separate from the instance name. | SHIP Specification 1.1.0 §7 Table 2 |
| path | TXT key | mandatory | WebSocket path, 1 to 32 UTF-8 bytes. The shortest value is a single slash. | SHIP Specification 1.1.0 §7 Table 2 |
| ski | TXT key | mandatory | Identifies the secp256r1 subject key identifier without a trial handshake. A 0x prefix is omitted. Table 2 also prints 40 byte and 160 bit, which conflicts with the 20-byte length. | SHIP Specification 1.1.0 §7 Table 2, §12.2 |
| brand | TXT key | optional | UTF-8, at most 32 bytes. | SHIP Specification 1.1.0 §7 Table 3 |
| type | TXT key | optional | UTF-8, at most 32 bytes. Not required for a conformant announcement. | SHIP Specification 1.1.0 §7 Table 3 |
| model | TXT key | optional | UTF-8, at most 32 bytes. | SHIP Specification 1.1.0 §7 Table 3 |
| further optional keys | TXT key | optional | Further optional keys are permitted inside the 400-byte TXT limit. | SHIP Specification 1.1.0 §7 |
| register | TXT key | mandatory | Boolean that states whether auto accept is active. The node sets it true while auto accept is active and false when it is not. Only auto accept changes it. The runtime mark is dynamic. | SHIP Specification 1.1.0 §5, §7.3.2 Table 2 |
| ecc | TXT key | optional | True when an optional curve is supported besides secp256r1, otherwise false. A node of this revision does not require the key, because earlier revisions do not send it. | SHIP Specification 1.1.0 §7.3.2 |

## Transport

| layer | requirement (own words) | value | clause |
| --- | --- | --- | --- |
| TCP | SHIP communication uses TCP. | required | SHIP Specification 1.1.0 §8 |
| TCP | The server port is the port in the SRV record. No numeric port is printed. | no fixed port | SHIP Specification 1.1.0 §8 |
| TCP | The MTU stays at or below 1500 bytes. | 1500 bytes | SHIP Specification 1.1.0 §8 |
| TCP | Initial retransmission count. | recommendation 2 | SHIP Specification 1.1.0 §8.3 |
| TCP | Initial retransmission timeout. | recommendation 1 second | SHIP Specification 1.1.0 §8.4 |
| TCP | Maximum retransmission timeout. | recommendation 120 seconds | SHIP Specification 1.1.0 §8.4 |
| UDP | UDP is specified for mDNS discovery. A SHIP data path over UDP is not specified. | discovery only | SHIP Specification 1.1.0 §8 |
| TLS | TLS 1.2 is mandatory. | TLS 1.2 | SHIP Specification 1.1.0 §9 |
| TLS | Table 1 states the maximum fragment length. | 512 bytes | SHIP Specification 1.1.0 §9.2 Table 1 |
| TLS | When the fragment-length extension is used, the only offered length is 1024 bytes, and the outgoing plaintext length stays at or below that. | 1024 bytes | SHIP Specification 1.1.0 §9.2 |
| TLS | secp256r1 is required. brainpoolP256r1 and brainpoolP384r1 are permitted. Compression is forbidden. Server name indication is required. Renegotiation is not defined and is not implemented. | curves and handshake | SHIP Specification 1.1.0 §9, §9.7 |
| WebSocket | The opening handshake uses the version number 13, the subprotocol ship only, and no extensions. Data frames use the binary opcode. | subprotocol ship | SHIP Specification 1.1.0 §10 |
| WebSocket | The ping interval is not shorter than 50 seconds. The wait for pong is 10 seconds. | 50 seconds; 10 seconds | SHIP Specification 1.1.0 §10.4 |
| JSON | SHIP messages on the WebSocket use the JSON representation this revision defines for the message set. | JSON | SHIP Specification 1.1.0 §11 |

## Trust

Certificate and SKI rules are §12.1 and §12.2. The double-connection rule is §12.2.2. PIN assignment is §12.5. QR fields continue in §12.6.

| verification mode | trust level | clause |
| --- | --- | --- |
| auto accept | user trust 8 | SHIP Specification 1.1.0 §12.3 |
| user verify | user trust 32 | SHIP Specification 1.1.0 §12.3 |
| user input | user trust 64 | SHIP Specification 1.1.0 §12.3 |
| commissioning | user trust 32 to 96, depending on tool trustworthiness; no finer scale is printed | SHIP Specification 1.1.0 §12.3 |
| none | user trust 0 | SHIP Specification 1.1.0 §12.3 Table 10 |
| self-signed PKI | PKI trust 0 | SHIP Specification 1.1.0 §12.3 |
| PKI-signed | a value from 0 through 65535 set by node policy; no finer scale is printed | SHIP Specification 1.1.0 §12.3 |
| second factor, PIN | 16 or 32 in the mode table; the prose range is 16 to 32 | SHIP Specification 1.1.0 §12.3, §12.5 |
| PIN, first sender after factory default | second-factor trust 32 | SHIP Specification 1.1.0 §12.5 |
| PIN, every later sender | second-factor trust 16 | SHIP Specification 1.1.0 §12.5 |
| general communication | requires user trust of at least 8; below that the hello is aborted | SHIP Specification 1.1.0 §12.3.2, §13.4.4.1 |
| commissioning over SHIP | requires user trust of at least 32 or second-factor trust of at least 32 | SHIP Specification 1.1.0 §12.3.2 |
| SKI length | 20 bytes, 40 hexadecimal digits, in the parameter table and the SKI clause; the TXT value cell also prints 40 byte and 160 bit | SHIP Specification 1.1.0 §12.1, §12.2, §7 Table 2 |
| double connection | a second connection between the same two nodes is closed under the double-connection rule | SHIP Specification 1.1.0 §12.2.2 |
| PIN length | 8 to 16 hexadecimal digits | SHIP Specification 1.1.0 §12.5 |
| auto accept with PIN | §12.3.1 sets user trust 8 with a second-factor range 16 to 32; Table 10 prints user trust 32 for that row. Both are printed and neither is selected. | SHIP Specification 1.1.0 §12.3.1, §12.3.2 Table 10 |

## Connection states

| state | entered on | leaves on | timer | clause |
| --- | --- | --- | --- | --- |
| CMI_INIT_START | underlying connection is open | role-specific CMI outcome | CmiTimeout 10 to 30 seconds, recommendation 30 seconds | SHIP Specification 1.1.0 §13.4.3 |
| Connection data preparation | CMI completes | hello starts | none printed beyond CMI | SHIP Specification 1.1.0 §13.4.4 |
| hello pending or ready | hello exchange starts | hello ok, or abort and close | Wait-For-Ready initial and prolongation each 60 to 240 seconds, recommendation 120 seconds; waiting is in milliseconds and the T_hello constants are in seconds, with no conversion printed | SHIP Specification 1.1.0 §13.4.4.1 |
| protocol handshake | hello ok | PIN verification, or abort and close | none printed as a separate handshake timer | SHIP Specification 1.1.0 §13.4.4.2 |
| PIN verification | handshake selects a PIN check | data exchange under the enable rule, or close | penalty after the 3rd invalid attempt 10 to 15 seconds, recommendation 15 seconds; after the 6th, 60 to 90 seconds, recommendation 90 seconds | SHIP Specification 1.1.0 §13.4.4.3 |
| connection data exchange | PIN branch enables it | access methods and close may run beside it | none printed as a data-exchange timer | SHIP Specification 1.1.0 §13.4.5 |
| access methods | data exchange has been entered | identification completes or is refused | only after data exchange | SHIP Specification 1.1.0 §13.4.6 |
| key-material messages | data exchange has been entered; forbidden before that | key-material exchange completes or is refused | keyMaterialStateResponse at most 20 seconds; keyMaterialState wait recommendation 30 seconds and at least 30 seconds | SHIP Specification 1.1.0 §13.4.7, §12.1.3.2 |
| regular close | a node starts the close after data exchange | connection closes | this edition places regular close here | SHIP Specification 1.1.0 §13.4.8 |

## Messages

| message | field | type | presence | clause |
| --- | --- | --- | --- | --- |
| access methods | accessMethods.dns.uri | URI as in IETF RFC 7320; WebSocket use as in IETF RFC 6455 | SHIP V1.1.0: M when accessMethods.dns is present | SHIP Specification 1.1.0 Table 22 |
| access methods | accessMethods.dns | parent | SHIP V1.1.0: O in the column; required when unicast DNS is used | SHIP Specification 1.1.0 Table 22 |
| access methods | accessMethods.dnsSd_mDns | no child defined in this version | SHIP V1.1.0: O in the column; required when that discovery is offered | SHIP Specification 1.1.0 Table 22 |
| access methods | accessMethods.id | string | SHIP V1.1.0: M | SHIP Specification 1.1.0 Table 22 |
| access methods | accessMethods | structure | SHIP V1.1.0: M | SHIP Specification 1.1.0 Table 22 |
| access methods request | accessMethodsRequest | structure; no child defined in this version; format is the handshake result | SHIP V1.1.0: M | SHIP Specification 1.1.0 Table 21 |
| identity | SKI | octet string shown as hex | SHIP V1.1.0: SHALL; no scenario | SHIP Specification 1.1.0 §12.2, §4.2 |
| presentation | PIN | hexadecimal | SHIP V1.1.0: SHALL for the graphical prefix and the 8–16 digit form; spaces are a lowercase should; no scenario | SHIP Specification 1.1.0 §12.5, §4.2 |
| presentation | SKI prefix | label | SHIP V1.1.0: SHALL for the user presentation; versions before 1.1 had no prefix on secp256r1; no scenario | SHIP Specification 1.1.0 §12.2.1 |
| state | certificate role | certificate | SHIP V1.1.0: defined; no scenario | SHIP Specification 1.1.0 §12.1.3.1 |
| init | CmiHead | OCTET | SHIP V1.1.0: M as the first byte of MessageValue | SHIP Specification 1.1.0 §13.4.3 |
| init | CmiRemainder | *OCTET | SHIP V1.1.0: present in the grammar; ignored | SHIP Specification 1.1.0 §13.4.3 |
| init | whole MessageValue sent by a V1.1.0 speaker | as above | SHIP V1.1.0: M for the client’s first message and for every server reply described here | SHIP Specification 1.1.0 §13.4.3 |
| commissioning request | commissioningRequest | structure; no child defined; MessageType %x01; format is the handshake result | SHIP V1.1.0: M | SHIP Specification 1.1.0 Table 23 |
| commissioning response | commissioningResponse.accept | not in the sources | SHIP V1.1.0: M | SHIP Specification 1.1.0 Table 24, §12.6 |
| commissioning response | commissioningResponse | structure | SHIP V1.1.0: M | SHIP Specification 1.1.0 Table 24 |
| close | connectionClose.maxTime | not in the sources | SHIP V1.1.0: O. Required in the announce the initiator sends. Forbidden on confirm | SHIP Specification 1.1.0 Table 33, §13.4.8.1.2 |
| close | connectionClose.phase | enumeration; JSON-UTF8 even after the handshake | SHIP V1.1.0: M | SHIP Specification 1.1.0 Table 33 |
| close | connectionClose.reason | enumeration | SHIP V1.1.0: O. Required in announce. Forbidden on confirm | SHIP Specification 1.1.0 Table 33 |
| SME hello | connectionHello.keyMaterialState | not in the sources | SHIP V1.1.0: M/O*1 | SHIP Specification 1.1.0 Table 12 |
| SME hello | connectionHello.keyMaterialState.updateCounter | not in the sources | SHIP V1.1.0: M/O*1. Footnote: for SHIP ≥ 1.1 sending the field is mandatory; for SHIP &lt; 1.1 the field is undefined and therefore optional. A receiver must not treat absence as an error | SHIP Specification 1.1.0 Table 12 |
| SME hello | connectionHello.phase | enumeration; JSON-UTF8 | SHIP V1.1.0: M | SHIP Specification 1.1.0 Table 12, §13.4.4.1 |
| SME hello | connectionHello.prolongationRequest | not in the sources | SHIP V1.1.0: O | SHIP Specification 1.1.0 Table 12 |
| SME hello | connectionHello.waiting | not in the sources | SHIP V1.1.0: O. Process sets it only while Wait-For-Ready-Timer is running, and forbids it when that timer is inactive | SHIP Specification 1.1.0 Table 12, §13.4.4.1.3 |
| PIN error | connectionPinError.error | error number; format is the handshake result | SHIP V1.1.0: M | SHIP Specification 1.1.0 Table 18, Table 19 |
| PIN input | connectionPinInput.pin | string of hexadecimal characters; format is the handshake result | SHIP V1.1.0: M | SHIP Specification 1.1.0 Table 17 |
| PIN state | connectionPinState.inputPermission | enumeration | SHIP V1.1.0: O in the table. Must be absent when pinState is pinOk or none. Must be present when pinState is required or optional | SHIP Specification 1.1.0 Table 16 |
| PIN state | connectionPinState.pinState | enumeration; format is the handshake result | SHIP V1.1.0: M | SHIP Specification 1.1.0 Table 16, §13.4.4.3.5.1 |
| data | data.extension.binary | not stated beyond the name | SHIP V1.1.0: O | SHIP Specification 1.1.0 Table 20 |
| data | data.extension.extensionId | not in the sources | SHIP V1.1.0: O | SHIP Specification 1.1.0 Table 20 |
| data | data.extension.string | textual | SHIP V1.1.0: O | SHIP Specification 1.1.0 Table 20 |
| data | data.extension | structure | SHIP V1.1.0: O. Default structure extensibility on this element’s first level | SHIP Specification 1.1.0 Table 20 |
| data | data.header | structure; format is the handshake result | SHIP V1.1.0: M. Default structure extensibility, recursive | SHIP Specification 1.1.0 Table 20, §13.4.5.2.2 |
| data | data.header.protocolId | not in the sources | SHIP V1.1.0: M | SHIP Specification 1.1.0 Table 20, §13.4.5.2.4, §14 |
| data | data.payload | container; JSON value type is not fixed by SHIP | SHIP V1.1.0: M | SHIP Specification 1.1.0 Table 20, §13.4.5.2.5 |
| DNS | A | IPv4 address | SHIP V1.1.0: default DNS-SD record; no scenario | SHIP Specification 1.1.0 §7.3.1 |
| DNS | AAAA | IPv6 address | SHIP V1.1.0: default DNS-SD record; no scenario | SHIP Specification 1.1.0 §7.3.1 |
| DNS-SD | SRV | SRV | SHIP V1.1.0: SHALL include those three; port MUST match the real server port; no scenario | SHIP Specification 1.1.0 §7.3.1 |
| DNS-SD | TTL | time | SHIP V1.1.0: SHOULD; no scenario | SHIP Specification 1.1.0 §7 |
| DNS-SD service | Instance | UTF-8 | SHIP V1.1.0: SHALL assign one per SRV/TXT pair; no scenario | SHIP Specification 1.1.0 §7.1 |
| DNS-SD service | service name | DNS label | SHIP V1.1.0: SHALL; no scenario | SHIP Specification 1.1.0 §7, §7.2 |
| DNS-SD service | service type | DNS labels | SHIP V1.1.0: service name SHALL be ship; no scenario | SHIP Specification 1.1.0 §7.2 |
| mDNS | host name | DNS name | SHIP V1.1.0: SHALL assign; SHOULD use the TXT id; no scenario | SHIP Specification 1.1.0 §7.3 |
| TXT | brand | UTF-8 string | SHIP V1.1.0: Optional; static; no scenario | SHIP Specification 1.1.0 §7.3.2 |
| TXT | ecc | Boolean | SHIP V1.1.0: Mandatory for SHIP version ≥ 1.1; dynamic; nodes of version ≥ 1.1 SHALL NOT assume the key is always present; no scenario | SHIP Specification 1.1.0 §7.3.2 |
| TXT | id | UTF-8 identifier | SHIP V1.1.0: Mandatory; static; no scenario | SHIP Specification 1.1.0 §7.3.2 |
| TXT | model | UTF-8 string | SHIP V1.1.0: Optional; static; no scenario | SHIP Specification 1.1.0 §7.3.2 |
| TXT | path | UTF-8 string, wss path | SHIP V1.1.0: Mandatory; static; no scenario | SHIP Specification 1.1.0 §7.3.2 |
| TXT | record | TXT | SHIP V1.1.0: SHALL; no scenario | SHIP Specification 1.1.0 §7.3.2 |
| TXT | register | Boolean | SHIP V1.1.0: Mandatory; dynamic; no scenario | SHIP Specification 1.1.0 §7.3.2, §5 |
| TXT | ski | hexadecimal string | SHIP V1.1.0: Mandatory; dynamic; no scenario | SHIP Specification 1.1.0 §7.3.2 |
| TXT | txtvers | version number | SHIP V1.1.0: Mandatory; static; SHALL be the first key; no scenario | SHIP Specification 1.1.0 §7.3.2 |
| TXT | type | UTF-8 string | SHIP V1.1.0: Optional; static; no scenario | SHIP Specification 1.1.0 §7.3.2 |
| TXT | unknown keys | key-value | SHIP V1.1.0: not a requirement to send; no scenario | SHIP Specification 1.1.0 §7.3.2 |
| encoding | wire text | JSON | SHIP V1.1.0: basis for many SHIP messages; no scenario | SHIP Specification 1.1.0 §11.1, §4 |
| type map | xs:boolean | Boolean | SHIP V1.1.0: mapping; no scenario | SHIP Specification 1.1.0 §11.4.2 |
| type map | xs:dateTime, xs:duration, xs:time, xs:language, xs:string, xs:hexBinary | String | SHIP V1.1.0: mapping; no scenario | SHIP Specification 1.1.0 §11.4.2 |
| type map | xs:list | Array | SHIP V1.1.0: mapping; no scenario | SHIP Specification 1.1.0 §11.4.4 |
| type map | xs:restriction | base type, values restricted | SHIP V1.1.0: mapping; no scenario | SHIP Specification 1.1.0 §11.4.4 |
| type map | xs:union | String | SHIP V1.1.0: mapping; no scenario | SHIP Specification 1.1.0 §11.4.4 |
| type map | xs:unsignedLong, xs:nonNegativeInteger, xs:unsignedInt, xs:integer, xs:unsignedShort, xs:short, xs:unsignedByte, xs:byte, xs:double | Number | SHIP V1.1.0: mapping; no scenario | SHIP Specification 1.1.0 §11.4.2 |
| key material | keyMaterial.entry.commissioningTool | not in the sources | SHIP V1.1.0: O. Required for that introduction | SHIP Specification 1.1.0 Table 26, §12.6 |
| key material | keyMaterial.entry.curve | number from the IANA TLS Supported Groups enumeration | SHIP V1.1.0: M | SHIP Specification 1.1.0 Table 26 |
| key material | keyMaterial.entry.id | not in the sources | SHIP V1.1.0: M | SHIP Specification 1.1.0 Table 26 |
| key material | keyMaterial.entry.note | characters | SHIP V1.1.0: O | SHIP Specification 1.1.0 Table 26 |
| key material | keyMaterial.entry.publicKey | xs:hexBinary | SHIP V1.1.0: O | SHIP Specification 1.1.0 Table 26 |
| key material | keyMaterial.entry.ski | xs:hexBinary | SHIP V1.1.0: M | SHIP Specification 1.1.0 Table 26 |
| key material | keyMaterial.entry.userTrust | not in the sources | SHIP V1.1.0: M | SHIP Specification 1.1.0 Table 26 |
| key material | keyMaterial.entry | list item | SHIP V1.1.0: cardinality 0... Zero entries are required when a tool has no relevant SKI to give (§12.6) | SHIP Specification 1.1.0 Table 26 |
| key material | keyMaterial.maxEntries | not in the sources | SHIP V1.1.0: M if the sender supports SHIP commissioning; O otherwise | SHIP Specification 1.1.0 Table 26, §12.6 |
| key material | keyMaterial | structure | SHIP V1.1.0: M | SHIP Specification 1.1.0 Table 26 |
| key material delete | keyMaterialDelete.entry.curve | IANA TLS Supported Groups number | SHIP V1.1.0: M | SHIP Specification 1.1.0 Table 28 |
| key material delete | keyMaterialDelete.entry.note | characters | SHIP V1.1.0: O | SHIP Specification 1.1.0 Table 28 |
| key material delete | keyMaterialDelete.entry.ski | xs:hexBinary | SHIP V1.1.0: M | SHIP Specification 1.1.0 Table 28 |
| key material delete | keyMaterialDelete.entry | list item | SHIP V1.1.0: cardinality 1.. | SHIP Specification 1.1.0 Table 28 |
| key material delete | keyMaterialDelete | structure | SHIP V1.1.0: M | SHIP Specification 1.1.0 Table 28 |
| key material delete response | keyMaterialDeleteResponse.entry.curve | IANA TLS Supported Groups number | SHIP V1.1.0: M | SHIP Specification 1.1.0 Table 29 |
| key material delete response | keyMaterialDeleteResponse.entry.id | not in the sources | SHIP V1.1.0: O | SHIP Specification 1.1.0 Table 29 |
| key material delete response | keyMaterialDeleteResponse.entry.note | characters | SHIP V1.1.0: O | SHIP Specification 1.1.0 Table 29 |
| key material delete response | keyMaterialDeleteResponse.entry.publicKey | xs:hexBinary | SHIP V1.1.0: O | SHIP Specification 1.1.0 Table 29 |
| key material delete response | keyMaterialDeleteResponse.entry.ski | xs:hexBinary | SHIP V1.1.0: M | SHIP Specification 1.1.0 Table 29 |
| key material delete response | keyMaterialDeleteResponse.entry.userTrust | not in the sources | SHIP V1.1.0: M | SHIP Specification 1.1.0 Table 29 |
| key material delete response | keyMaterialDeleteResponse.entry | list item | SHIP V1.1.0: cardinality 1.. | SHIP Specification 1.1.0 Table 29 |
| key material delete response | keyMaterialDeleteResponse | structure | SHIP V1.1.0: M | SHIP Specification 1.1.0 Table 29 |
| key material request | keyMaterialRequest | structure; no child defined | SHIP V1.1.0: M | SHIP Specification 1.1.0 Table 25 |
| key material response | keyMaterialResponse.entry.curve | IANA TLS Supported Groups number | SHIP V1.1.0: M | SHIP Specification 1.1.0 Table 27 |
| key material response | keyMaterialResponse.entry.id | not in the sources | SHIP V1.1.0: O | SHIP Specification 1.1.0 Table 27 |
| key material response | keyMaterialResponse.entry.note | characters | SHIP V1.1.0: O | SHIP Specification 1.1.0 Table 27 |
| key material response | keyMaterialResponse.entry.publicKey | xs:hexBinary | SHIP V1.1.0: O | SHIP Specification 1.1.0 Table 27 |
| key material response | keyMaterialResponse.entry.ski | not in the sources | SHIP V1.1.0: M | SHIP Specification 1.1.0 Table 27 |
| key material response | keyMaterialResponse.entry.userTrust | not in the sources | SHIP V1.1.0: M | SHIP Specification 1.1.0 Table 27 |
| key material response | keyMaterialResponse.entry | list item | SHIP V1.1.0: cardinality 0.. | SHIP Specification 1.1.0 Table 27 |
| key material response | keyMaterialResponse | structure | SHIP V1.1.0: M | SHIP Specification 1.1.0 Table 27 |
| key material state | keyMaterialState.entry.currentState | enumeration | SHIP V1.1.0: M | SHIP Specification 1.1.0 Table 30 |
| key material state | keyMaterialState.entry.curve | IANA TLS Supported Groups number | SHIP V1.1.0: M | SHIP Specification 1.1.0 Table 30 |
| key material state | keyMaterialState.entry.publicKey | xs:hexBinary | SHIP V1.1.0: O | SHIP Specification 1.1.0 Table 30 |
| key material state | keyMaterialState.entry.ski | xs:hexBinary | SHIP V1.1.0: M | SHIP Specification 1.1.0 Table 30 |
| key material state | keyMaterialState.entry | list item | SHIP V1.1.0: cardinality 1..256 | SHIP Specification 1.1.0 Table 30 |
| key material state | keyMaterialState.updateCounter | numeric range printed on the cell | SHIP V1.1.0: M | SHIP Specification 1.1.0 Table 30 |
| key material state | keyMaterialState | structure | SHIP V1.1.0: M | SHIP Specification 1.1.0 Table 30 |
| key material state request | keyMaterialStateRequest.knownUpdateCounter | not in the sources | SHIP V1.1.0: M | SHIP Specification 1.1.0 Table 32 |
| key material state request | keyMaterialStateRequest | structure | SHIP V1.1.0: M | SHIP Specification 1.1.0 Table 32 |
| key material state response | keyMaterialStateResponse.accept | not in the sources | SHIP V1.1.0: M | SHIP Specification 1.1.0 Table 31 |
| key material state response | keyMaterialStateResponse | structure | SHIP V1.1.0: M | SHIP Specification 1.1.0 Table 31 |
| protocol handshake | messageProtocolHandshake.formats.format | string | SHIP V1.1.0: M inside the list | SHIP Specification 1.1.0 Table 13 |
| protocol handshake | messageProtocolHandshake.formats | list | SHIP V1.1.0: M | SHIP Specification 1.1.0 Table 13 |
| protocol handshake | messageProtocolHandshake.handshakeType | enumeration; JSON-UTF8 | SHIP V1.1.0: M | SHIP Specification 1.1.0 Table 13 |
| protocol handshake | messageProtocolHandshake.version.major | not in the sources | SHIP V1.1.0: M | SHIP Specification 1.1.0 Table 13 |
| protocol handshake | messageProtocolHandshake.version.minor | not in the sources | SHIP V1.1.0: M | SHIP Specification 1.1.0 Table 13 |
| protocol handshake | messageProtocolHandshake.version | structure | SHIP V1.1.0: M | SHIP Specification 1.1.0 Table 13 |
| protocol handshake error | messageProtocolHandshakeError.error | error number; JSON-UTF8 | SHIP V1.1.0: M | SHIP Specification 1.1.0 Table 14, Table 15 |
| well-known protocolId | ee1.0 | identifier | SHIP V1.1.0: assigned value | SHIP Specification 1.1.0 §14 |
| label encoding | B2SKI: | UTF-8; tag is 6 bytes; ends with | SHIP V1.1.0: O, after BSKI | SHIP Specification 1.1.0 §12.7 |
| label encoding | BRAND: | UTF-8; tag is 6 bytes; ends with | SHIP V1.1.0: O, after ID | SHIP Specification 1.1.0 §12.7 |
| label encoding | BSKI: | UTF-8; tag is 5 bytes; ends with | SHIP V1.1.0: O, after MODEL | SHIP Specification 1.1.0 §12.7 |
| label encoding | ID: | UTF-8; tag is 3 bytes; ends with | SHIP V1.1.0: R. Follows PIN if PIN is present, otherwise follows SKI | SHIP Specification 1.1.0 §12.7 |
| label encoding | MODEL: | UTF-8; tag is 6 bytes; ends with | SHIP V1.1.0: O, after TYPE | SHIP Specification 1.1.0 §12.7 |
| label encoding | PIN: | UTF-8; tag is 4 bytes; ends with | SHIP V1.1.0: M if the node has a PIN; follows the SKI field | SHIP Specification 1.1.0 §12.7 |
| label encoding | prefix | UTF-8 string | SHIP V1.1.0: M if SHIP data is integrated. Integrating SHIP data: O. Model 2 with ECC level at least low: R | SHIP Specification 1.1.0 §12.7 |
| label encoding | SKI: | UTF-8; tag is 4 bytes; ends with one; byte | SHIP V1.1.0: M when SHIP data is integrated | SHIP Specification 1.1.0 §12.7 |
| label encoding | TYPE: | UTF-8; tag is 5 bytes; ends with | SHIP V1.1.0: O, after BRAND | SHIP Specification 1.1.0 §12.7 |
| framing | MessageType | OCTET | SHIP V1.1.0: M on every SHIP message. Unknown type: discard the message or close the channel (either is allowed) | SHIP Specification 1.1.0 §13.4.2, Table 11 |
| framing | MessageValue | 1*OCTET | SHIP V1.1.0: M | SHIP Specification 1.1.0 §13.4.2 |
| access methods | accessMethods.id | identifier | SHIP V1.1.0: named; schema not on these pages | SHIP Specification 1.1.0 §7.4 |
| commissioning response | commissioningResponse.accept | Boolean | SHIP V1.1.0: SHOULD when trust conditions hold; no scenario | SHIP Specification 1.1.0 §12.3.1.6 |
| data | data.payload | external payload | SHIP V1.1.0: optional external content; no scenario | SHIP Specification 1.1.0 §11.4.1 |
| data | protocolId | identifier | SHIP V1.1.0: named; value list not on these pages | SHIP Specification 1.1.0 §11.4.1 |
| hello | connection state hello | SME message | SHIP V1.1.0: named on these pages; schema not on these pages | SHIP Specification 1.1.0 §5, §12.1.3.1, §12.1.3.4 |
| key material | entry | list item | SHIP V1.1.0: conditional; no scenario | SHIP Specification 1.1.0 §12.3.1.6 |
| key material | keyMaterial.entry.id | identifier | SHIP V1.1.0: named; schema not on these pages | SHIP Specification 1.1.0 §7.4 |
| key material | keyMaterial.maxEntries | count of SKIs and related data | SHIP V1.1.0: expressed by a node that supports commissioning; no scenario | SHIP Specification 1.1.0 §12.2.2, §12.3.1.6 |
| keyMaterialState | SKI categories | SKI | SHIP V1.1.0: see section 6; no scenario | SHIP Specification 1.1.0 §12.1.3.2 |
| keyMaterialState | updateCounter | counter | SHIP V1.1.0: SHALL be comparable with a previously received value; no scenario | SHIP Specification 1.1.0 §12.1.3.2, §12.1.3.3, §12.1.3.4 |
| pin | connectionPinState.pinState | enumeration | SHIP V1.1.0: MAY be required if commissioning is supported; SHALL NOT be required if commissioning is not supported; no scenario | SHIP Specification 1.1.0 §12.3.1.2 |
| protocol handshake | Protocol Handshake | SME message | SHIP V1.1.0: named; schema not on these pages | SHIP Specification 1.1.0 §12.1.3, §6 |
| server | port | TCP port | SHIP V1.1.0: MAY choose; MUST publish the chosen port in SRV; each logical node on one device MUST use a distinct port; no scenario | SHIP Specification 1.1.0 §7.3.1, §3 |
| cipher | suite | cipher suite | SHIP V1.1.0: MUST; no scenario | SHIP Specification 1.1.0 §9.1 |
| cipher | suite | cipher suite | SHIP V1.1.0: OPTIONAL; no scenario | SHIP Specification 1.1.0 §9.1 |
| cipher | suite | cipher suite | SHIP V1.1.0: OPTIONAL; no scenario | SHIP Specification 1.1.0 §9.1 |
| compression | method | not in the sources | SHIP V1.1.0: MUST NOT; no scenario | SHIP Specification 1.1.0 §9.3 |
| curve | named curve | ECC curve | SHIP V1.1.0: MAY; no scenario | SHIP Specification 1.1.0 §9.1, §9.7 |
| curve | named curve | ECC curve | SHIP V1.1.0: MAY; no scenario | SHIP Specification 1.1.0 §9.1, §9.7 |
| curve | named curve | ECC curve | SHIP V1.1.0: SHALL; no scenario | SHIP Specification 1.1.0 §9.1, §9.7 |
| extension | SNI | ASCII server name, no trailing dot | SHIP V1.1.0: MUST send (client); no scenario | SHIP Specification 1.1.0 §9.4, §10.1 |
| fragment | TLSPlaintext.length | length | SHIP V1.1.0: SHALL for 1024; SHOULD support the extension; no scenario | SHIP Specification 1.1.0 §9.2, §4.2 |
| handshake | version | protocol version | SHIP V1.1.0: MANDATORY; no scenario | SHIP Specification 1.1.0 §9 |
| session | session id and master secret | TLS session state | SHIP V1.1.0: SHOULD store and reuse; MAY discard; no scenario | SHIP Specification 1.1.0 §9.6, §12.4 |
| category | PKI trust | integer level | SHIP V1.1.0: optional; communication SHALL remain possible at 0; no scenario | SHIP Specification 1.1.0 §12.3.2 |
| category | second factor trust | integer level | SHIP V1.1.0: MAY; no scenario | SHIP Specification 1.1.0 §12.3.2, §12.5 |
| category | user trust | integer level | SHIP V1.1.0: per mechanism; no scenario | SHIP Specification 1.1.0 §12.3.1, §12.3.2 |
| gate | general communication | user trust | SHIP V1.1.0: MUST meet; no scenario | SHIP Specification 1.1.0 §12.3.2, §4.2 |
| gate | SHIP commissioning | user trust or second factor trust | SHIP V1.1.0: MUST meet; no scenario | SHIP Specification 1.1.0 §12.3.2, §4.2 |
| frame | opcode 0x1 | close status | SHIP V1.1.0: MUST terminate; no scenario | SHIP Specification 1.1.0 §10.3 |
| frame | opcode | binary data frame | SHIP V1.1.0: MUST; no scenario | SHIP Specification 1.1.0 §10.3 |
| frame | opcodes 0x3–0x7, 0xB–0xF | close status | SHIP V1.1.0: MUST terminate; no scenario | SHIP Specification 1.1.0 §10.3 |
| frame | reserved bits | bits | SHIP V1.1.0: MUST; no scenario | SHIP Specification 1.1.0 §10.3 |
| keepalive | ping interval | duration | SHIP V1.1.0: MUST NOT below 50s; no scenario | SHIP Specification 1.1.0 §10.4, §4.2 |
| keepalive | pong wait | duration | SHIP V1.1.0: SHALL; no scenario | SHIP Specification 1.1.0 §10.4, §4.2 |
| opening | origin | origin | SHIP V1.1.0: MAY; no scenario | SHIP Specification 1.1.0 §10.2 |
| opening | scheme | URI scheme | SHIP V1.1.0: MUST; no scenario | SHIP Specification 1.1.0 §10.2 |
| opening | Sec-WebSocket-Extensions | header | SHIP V1.1.0: MUST NOT; no scenario | SHIP Specification 1.1.0 §10.2 |
| opening | Sec-WebSocket-Protocol | subprotocol | SHIP V1.1.0: MUST; no scenario | SHIP Specification 1.1.0 §10.2 |
| opening | Sec-WebSocket-Version | header | SHIP V1.1.0: MUST; no scenario | SHIP Specification 1.1.0 §10.2 |


## Changes from 1.0.1

| topic | 1.0.1 | 1.1.0 | clause |
| --- | --- | --- | --- |
| fragment length | Table 1 prints 512 bytes and §9.2 prints 1024 bytes | the same pair of numbers is printed | SHIP Specification 1.0.1 §9.2; SHIP Specification 1.1.0 §9.2 |
| register runtime mark | Table 2 prints Static, while §5 requires the flag to follow auto accept | the flag is dynamic and follows auto accept | SHIP Specification 1.0.1 §5, §7 Table 2; SHIP Specification 1.1.0 §7.3.2 |
| ecc TXT key | not printed | optional Boolean for an extra curve besides secp256r1; absence is not an error | SHIP Specification 1.1.0 §7.3.2 |
| auto accept with PIN | auto accept is user trust 8; no separate PIN row in that mode | §12.3.1 prints user trust 8 and Table 10 prints user trust 32 | SHIP Specification 1.1.0 §12.3.1, §12.3.2 Table 10 |
| key-material timers | not in Table 1 | response at most 20 seconds; wait recommendation 30 seconds and at least 30 seconds | SHIP Specification 1.1.0 §12.1.3.2 |
| certificate-update retry | not in Table 1 | at least 5 minutes | SHIP Specification 1.1.0 §12.1.3.2 |
| certificate-update transition | not in Table 1 | one quarter of the lifetime floored at 1 month, and a range of at least 1 month; the successor marking is also described as one month | SHIP Specification 1.1.0 §12.1.3 |
| late connection phase | connection termination is §13.4.7 | key-material messages are §13.4.7 and regular close is §13.4.8 | SHIP Specification 1.0.1 §13.4.7; SHIP Specification 1.1.0 §13.4.7, §13.4.8 |
| commissioningRequest | not given this duty pair | one clause says it should go out on every connection; a later clause forbids key-material messages before data exchange | SHIP Specification 1.1.0 §12.6, §13.4.7 |
| hello sub-elements | no keyMaterialState.updateCounter duty is printed | some hello messages forbid further sub-elements, while Table 12 makes keyMaterialState.updateCounter mandatory to send for this revision | SHIP Specification 1.1.0 §13.4.4, Table 12 |

## Commands, limits and timing

| topic | statement | clause |
| --- | --- | --- |
| Parameter table | Parameter: keyMaterialStateResponse timely sending; Recommendation column: empty; Range column: ≤ 20s; Clause cited by the table: §12.1.3.2 | §12.1.3.2 |
| Parameter table | Parameter: keyMaterialState timeout (wait for keyMaterialStateResponse, then retransmission); Recommendation column: 30s; Range column: ≥ 30s; Clause cited by the table: §12.1.3.2 | §12.1.3.2 |
| Parameter table | Parameter: Certificate-update connection retry wait; Recommendation column: empty; Range column: ≥ 5 minutes; Clause cited by the table: §12.1.3.2 | §12.1.3.2 |
| Parameter table | Parameter: Certificate-update transition stage; Recommendation column: one quarter of the lifetime, floored at 1 month; Range column: ≥ 1 month; Clause cited by the table: §12.1.3.2 | §12.1.3.2 |
| Parameter table | Parameter: PIN-entry penalty, 6th failed try; Recommendation column: 90s; Range column: 60–90s; Clause cited by the table: §13.4.4.3 | §13.4.4.3 |
| Parameter table | Parameter: PIN-entry penalty, 3rd failed try; Recommendation column: 15s; Range column: 10–15s; Clause cited by the table: §13.4.4.3 | §13.4.4.3 |
| Parameter table | Parameter: Wait-For-Ready prolongation; Recommendation column: 120s; Range column: 60–240s; Clause cited by the table: §13.4.4.1 | §13.4.4.1 |
| Parameter table | Parameter: Wait-For-Ready initial; Recommendation column: 120s; Range column: 60–240s; Clause cited by the table: §13.4.4.1 | §13.4.4.1 |
| Parameter table | Parameter: CmiTimeout; Recommendation column: 30s; Range column: 10–30s; Clause cited by the table: §13.4 | §13.4 |
| Parameter table | Parameter: Commissioning gate (user trust or second-factor trust); Recommendation column: empty; Range column: ≥ 32; Clause cited by the table: §12.3.2 | §12.3.2 |
| Parameter table | Parameter: General-communication gate (user trust); Recommendation column: empty; Range column: ≥ 8; Clause cited by the table: §12.3.2 | §12.3.2 |
| Parameter table | Parameter: Auto-accept window, maximum; Recommendation column: 60s; Range column: ≤ 120s; Clause cited by the table: §12.3.1.1 | §12.3.1.1 |
| Parameter table | Parameter: PIN length; Recommendation column: empty; Range column: 8 to 16 hex digits; Clause cited by the table: §12.5 | §12.5 |
| Parameter table | Parameter: SKI length; Recommendation column: empty; Range column: 20 bytes, 40 hex digits; Clause cited by the table: §12.2 | §12.2 |
| Parameter table | Parameter: Pong timeout; Recommendation column: empty; Range column: 10s; Clause cited by the table: §10.4 | §10.4 |
| Parameter table | Parameter: Ping minimum interval; Recommendation column: empty; Range column: 50s; Clause cited by the table: §10.4 | §10.4 |
| Parameter table | Parameter: Maximum fragment length; Recommendation column: empty; Range column: 512 bytes; Clause cited by the table: §9.2 | §9.2 |
| Parameter table | Parameter: MTU; Recommendation column: empty; Range column: 1500 bytes; Clause cited by the table: §8 | §8 |
| Parameter table | Parameter: Maximum TCP retransmission timeout; Recommendation column: 120s; Range column: empty; Clause cited by the table: §8.4 | §8.4 |
| Parameter table | Parameter: Initial TCP retransmission timeout; Recommendation column: 1s; Range column: empty; Clause cited by the table: §8.4 | §8.4 |
| Parameter table | Parameter: Initial TCP retransmission count; Recommendation column: 2; Range column: empty; Clause cited by the table: §8.3 | §8.3 |
| Stack, addresses, and ports | prints OSI 3 as IPv4/IPv6 and IPv6 6LoWPAN, OSI 4 as UDP and TCP, and OSI 5–7 as mDNS, TLS and Websockets, with SHIP message exchange on the drawing. Physical-layer labels on the same figure are IEEE 802.15.4, Wifi, GreenPhy and Ethernet. §4 | §4 |
| Stack, addresses, and ports | Local discovery SHALL use mDNS/DNS-SD. TCP, TLS and WebSocket are the protocol base. JSON, as chapter 11 describes, is required for SHIP messages on that WebSocket. §4, §4 | §4 |
| Stack, addresses, and ports | IPv4 and IPv6 are both permitted. An address may be preconfigured, assigned by a DNS server, assigned by SLAAC, or assigned by any other appropriate means. Physical-layer choice, including WiFi or powerline, and the use of an IP router, are outside this specification. §4 | §4 |
| Stack, addresses, and ports | labels local nodes, two SHIP web services, a WAN, a router, IPv4/IPv6, and the examples LTE and WiFi. §4 | §4 |
| Stack, addresses, and ports | TCP SHALL be used for SHIP communication. UDP is specified only for mDNS discovery in this version. §8 | §8 |
| Stack, addresses, and ports | The MTU SHALL stay at or below 1500 bytes. §8 | §8 |
| Stack, addresses, and ports | No well-known port number is printed. A local server’s port SHALL be the port in the DNS-SD SRV record. The node MAY choose that port and MUST publish the port it actually uses. §8, §7.3.1 | §8, §7.3.1 |
| Stack, addresses, and ports | A node MUST support at least 1 simultaneously active connection. §8.1 | §8.1 |
| Stack, addresses, and ports | A node limited to 1 connection SHALL keep a listening TCP server, SHALL close that port only to open a TCP client connection, and after the client connection SHALL close the client as soon as possible and listen again. §8.1 | §8.1 |
| Stack, addresses, and ports | If the simultaneous-connection limit x is above 1, one slot SHALL stay available for the TCP server, leaving at most x-1 client slots, and one slot SHALL stay available for clients, leaving at most x-1 server slots. §8.1 | §8.1 |
| Stack, addresses, and ports | Once the connection limit is reached, the TCP server port MAY be shut, and it SHALL be opened again as soon as possible. Under the limit, that port SHALL remain open. §8.1 | §8.1 |
| Stack, addresses, and ports | During registration, a node that supports only one simultaneous connection MAY close the server port to place a client connection. It SHALL first wait X milliseconds. X SHOULD be a random value from 0 to 30000 milliseconds. The wait applies before closing the server port to connect to another node whose register flag is true. §5 | §5 |
| Online detection and TCP establishment | Before a local node opens TCP to another local node, the peer SHOULD be seen as online. An mDNS announcement whose TTL is not valid SHOULD be treated as offline. When that announcement is refreshed and the TTL is valid, the peer SHALL be treated as online again. §8.2 | §8.2 |
| Online detection and TCP establishment | A local node MAY send ICMP echo requests. If no ICMP echo reply arrives but mDNS announcements do, the peer SHALL be treated as ICMP-blocking: ICMP SHALL NOT be used as the offline signal, and the mDNS TTL SHOULD be the only offline signal. §8.2 | §8.2 |
| Online detection and TCP establishment | The offline check matters for connection-limited nodes. An attempt toward an offline peer can occupy the caller for 10 seconds (§8.3), during which others may be unable to reach the caller. §8.2 | §8.3, §8.2 |
| Online detection and TCP establishment | A SYN to a closed port SHALL be answered with RST, as RFC 793 section 3.4 / page 36 describes. The RST SHOULD NOT be blocked or filtered on the node. §8.3 | §8.3 |
| Online detection and TCP establishment | The initial SYN SHOULD be retransmitted twice if neither ACK nor RST arrives. With the §8.4 recommended timeouts the longest establishment is 1 + 3 + 6 = 10 seconds. §8.3 | §8.4, §8.3 |
| Online detection and TCP establishment | A node SHOULD run the RFC 6298 retransmission timer from measured round-trip time. A packet that was sent again MUST be left out of that measurement. §8.4 | §8.4 |
| Online detection and TCP establishment | RFC 6298’s minimum RTO of 1 second is cited; a SHIP node MAY use a smaller minimum. For the initial SYN the RTO SHOULD start at 1 second. A node MAY raise that initial value on a lossy network. §8.4 | §8.4 |
| Online detection and TCP establishment | After the first retransmission, RFC 6298 sets the RTO to at least the historical 3 seconds, then doubles it on every further retransmission. A SHIP node SHOULD cap the RTO at 120 seconds. §8.4 | §8.4 |
| TLS | TLS 1.2 is MANDATORY. Except for the fragment-length rule in §9.2, TLS MUST follow RFC 5246. TLS 1.3 is mentioned only as a possible later version and is not specified here. §9 | §9.2, §9 |
| TLS | Both ends MUST authenticate during the TLS 1.2 handshake. Client and server each MUST check the peer public key or certificate, following §12.3. §9 | §12.3, §9 |
| TLS | Figure 3 draws the complete mutually authenticated TLS 1.2 handshake. Figure 4 draws the shorter handshake that resumes a session. Step labels inside the drawings are not recorded. §9, §9.6 | §9, §9.6 |
| TLS | Authentication is ECDSA. Key exchange is ECDHE, which the text associates with forward secrecy. The only curves are brainpoolP384r1 (MAY), brainpoolP256r1 (MAY), and secp256r1 (SHALL). §9.1 | §9.1 |
| TLS | ECC extensions SHALL follow RFC 8422. That RFC orders curves by the client’s preference, favourite first. SHIP nodes SHALL instead use one shared ranking, which is not a security ranking: 1 brainpoolP384r1 (optional), 2 brainpoolP256r1 (optional), 3 secp256r1 (mandatory). Only secp256r1 is mandatory. The same ranking applies throughout the specification, including which of a peer’s SKIs is shown for verification. §9.7 | §9.7 |
| TLS | The RFC 6066 Maximum Fragment Length Negotiation Extension SHOULD be supported. If it is used, the only length it SHALL offer is 1024 bytes. Outgoing TLSPlaintext.length SHALL NOT exceed 1024 bytes even when the extension is not supported. Table 1’s range cell for this parameter prints 512 bytes. §9.2, §4.2 | Table 1, §9.2, §4.2 |
| TLS | Compression in TLS is forbidden. §9.3 | §9.3 |
| TLS | SNI MUST be supported, as RFC 6455 requires for WebSocket. A SHIP client MUST send SNI. A local SHIP node SHALL ignore the SNI value. A web server based node MAY use SNI when it has a fixed DNS host name. For a local connection the server name SHALL equal the server’s mDNS host name. For a web server it SHALL be that server’s DNS hostname. Per RFC 6066 the SNI name is ASCII without a trailing dot. A SHIP server SHOULD ignore a final trailing dot if the client added one. §9.4, §10.1 | §9.4, §10.1 |
| TLS | TLS renegotiation has no SHIP definition. A node SHALL NOT implement it, and it turns renegotiation requests away. §9.5 | §9.5 |
| TLS | Session resumption SHOULD be supported so the master secret and session id can be reused. A node MAY drop a session state, for example when latency does not matter, when the connection has been idle for an unspecified time, or when storage is full and a new connection has higher priority. Dropping the state forces a full handshake on the next connection. §9.6 | §9.6 |
| TLS | If TLS was used, that session state SHOULD be stored for reconnection and SHALL be stored together with the peer’s public key and trust level. §12.4 | §12.4 |
| TLS probing | The TXT record can publish only the secp256r1 SKI. When both peers support a further curve, the SKI that matters is the one of the curve the TLS ECC extension selects. A node that supports a further curve SHALL support TLS probing to learn which curve and SKI the other node uses. §9.8 | §9.8 |
| TLS probing | Probing SHALL open a connection, take the key material from the TLS Server Certificate message, and derive the SKI used on that connection. For user verification, that SKI SHALL be given to the user. The §9.7 ranking makes the SKI independent of which peer is the TLS client. §9.8 | §9.7, §9.8 |
| TLS probing | A probing TLS client SHALL abort after it has read the TLS Server Certificate, when the SKI it derived is still untrusted. The text’s reason: the peer could be in auto accept and would otherwise start trusting the prober. Probing is not itself a verification mode, and it is not allowed to disturb those modes. §9.8 | §9.8 |
| TLS probing | A node may be in auto accept while it probes. The two processes SHALL stay independent. A server certificate seen during probing is not, by itself, enough to finish auto accept. §9.8 | §9.8 |
| TLS probing | If the node has only one connection, or only a constrained number, probing may be impossible at that moment and SHALL be retried later. Such a node SHOULD NOT tear down an established connection in order to probe. §9.8 | §9.8 |
| WebSocket | WebSocket MUST be used above TCP and TLS, in strict compliance with RFC 6455. §10 | §10 |
| WebSocket | Host, port, and resource name are not fixed by this specification. A node learns them from discovery (chapter 7) and, if it connects, SHALL present them exactly as discovered. §10.2 | §10.2 |
| WebSocket | The origin MAY be absent. Sec-WebSocket-Version MUST be 13. Sec-WebSocket-Protocol MUST include ship and MUST NOT include any other subprotocol. Sec-WebSocket-Extensions MUST NOT be sent. §10.2 | §10.2 |
| WebSocket | SHIP messages are at least partly binary. Every data frame MUST be opcode 0x2. Opcode 0x1 MUST cause close status 1003. Opcodes 0x3–0x7 and 0xB–0xF MUST cause close status 1002. Reserved bits MUST be 0. Reserved opcodes MUST NOT be used. §10.3 | §10.3 |
| WebSocket | RFC 6455 requires clients to accept fragmented messages and to accept control frames between fragments, and it forbids interleaving fragments of different messages. This version does not add multiplexing. §10.3 | §10.3 |
| WebSocket | The WebSocket SHALL be left up when local resources allow. A node SHALL use ping and pong to check that the transport works. Ping on one connection MUST NOT be sent at an interval shorter than 50 seconds. The usual wait for pong SHALL be 10 seconds. §10.4 | §10.4 |
| Discovery and the register flag | Local nodes SHALL be found with mDNS/DNS-SD even when their host names and IP addresses are unknown. A node that speaks mDNS SHALL publish the service name ship. A TTL of 2 minutes is what DNS-SD records SHOULD carry. §7 | §7 |
| Discovery and the register flag | Each advertised SRV/TXT pair SHALL have an <Instance> label of at most 63 UTF-8 bytes. The label SHALL be a user-facing meaningful name. On a name conflict the node SHALL pick a new name until the conflict is gone, and SHOULD append a parenthesised decimal integer. §7.1 | §7.1 |
| Discovery and the register flag | The <Service> label is _ + ship + . + _tcp. The worked example uses local as the domain label. §7.2 | §7.2 |
| Discovery and the register flag | A local node SHALL assign a unique mDNS host name of at most 63 bytes, and SHOULD build it from the TXT unique id. §7.3 | §7.3 |
| Discovery and the register flag | Information that DNS-SD already carries in its default records MUST NOT be repeated in other records. A holds the IPv4 address, AAAA the IPv6 address. SRV SHALL hold the service name, the mDNS host name, and the port. §7.3.1 | §7.3.1 |
| Discovery and the register flag | There is one TXT format, at most 400 bytes. Mandatory keys are in Table 2; optional keys defined here are in Table 3. Further optional pairs are allowed inside the 400-byte limit. Unknown pairs SHALL be ignored. §7.3.2 | Table 2, Table 3, §7.3.2 |
| Discovery and the register flag | txtvers SHALL be the first key, SHALL be present, SHALL be non-empty, and SHALL be 1. A missing txtvers, or a value other than 1, SHALL cause the client to discard the TXT record silently. A response whose txtvers is not 1 SHALL make that TXT record ignored. §7.3.2 | §7.3.2 |
| Discovery and the register flag | id, ski, brand, type, and model SHALL be UTF-8. id is the globally unique SHIP ID, at most 63 bytes. Its first part SHOULD be a short form of the manufacturer name; the manufacturer defines the rest. Two nodes with the same id on one local network are not a regular setup. brand, type, and model are each at most 32 UTF-8 bytes. path is 1 to 32 UTF-8 bytes, and the shortest value is /. §7.3.2 | §7.3.2 |
| Discovery and the register flag | ski lets a peer recognise the secp256r1 SKI without a trial handshake. Version ≥ 1.1 SHALL publish that SKI in uppercase hex and SHALL still accept lowercase or mixed case. §7.3.2 | §7.3.2 |
| Discovery and the register flag | register tells whether auto accept is active. ecc SHALL be true when an optional curve is supported besides secp256r1, and false when secp256r1 is the only curve. Because versions below 1.1 do not emit ecc, a node of version ≥ 1.1 SHALL NOT require the key to be present. The value is usually static and changes only if support for additional curves changes. The ski value is usually static unless the secp256r1 certificate is updated. §7.3.2, §7.3.2 | §7.3.2 |
| Discovery and the register flag | The SHIP ID also appears as keyMaterial.entry.id (§13.4.7.5) and accessMethods.id (§13.4.6). After a foreign node is trusted, keeping a persistent record of that identifier is recommended, because non-secp256r1 SKIs are not in the TXT record and because SKIs can change. §7.4, §3 | §13.4.7.5, §13.4.6, §7.4, §3 |
| Discovery and the register flag | register moves only for auto accept. User verify, user input and commissioning leave that flag alone. §5 | §5 |
| Discovery and the register flag | While auto accept is active the node SHALL advertise register true and SHALL look for peers advertising the same. If several do, it SHALL pick one by whatever means fit. §5 | §5 |
| Discovery and the register flag | While auto accept is inactive the node SHALL advertise register false and SHALL end the search for peers with that flag set. §5 | §5 |
| Discovery and the register flag | If both peers use auto accept, neither verifies an SKI. The text says a third device can then read and change the traffic, and it strongly recommends supporting at least one other verification mode. §5 | §5 |
| Discovery and the register flag | During reconnection the register flag does not matter. It matters for registration with a new node. §6 | §6 |
| Registration and reconnection | Registration starts in a public-key verification mode (§12.3.1). §5 | §12.3.1, §5 |
| Registration and reconnection | Once trust came from user input, from SHIP commissioning, from a manufacturer’s commissioning, or from user verification, the node SHALL look up those trusted SKIs and connect. A trusted SKI on any curve besides secp256r1 also requires TLS probing. If setup does not reach the success condition in §5.1, the node SHALL keep retrying. These pages give that loop no period. §5 | §5.1, §5 |
| Registration and reconnection | If the peer aborts SME hello (§13.4.4.1), the node SHOULD wait until that peer’s register flag is true before trying again. If the flag is true and this node already holds the peer’s trusted SKI, it SHALL try again. §5 | §13.4.4.1, §5 |
| Registration and reconnection | A registration with a web server based node SHOULD follow this order: verify the server’s public key (§12.3); resolve IP and port with DNS when a URL or DNS host name is used, and skip that when an IP address is used; connect; check that the received public key matches a trusted SKI; SME Connection Mode Initialization; SME Connection Data Preparation. §5 | §12.3, §5 |
| Registration and reconnection | A registration with a local node SHOULD follow this order: verify the peer’s public key (§12.3), setting register true if auto accept is active and false otherwise; if auto accept finds the peer’s register true, switching to another verification mode is strongly recommended, while user verify, user input, or commissioning searches discovery for the SKI; connect to the discovered IP and port or accept an incoming connection; check the received public key against a trusted SKI; SME Connection Mode Initialization; SME Connection Data Preparation. §5 | §12.3, §5 |
| Registration and reconnection | With SME hello a node can confirm the peer (§13.4.4.1). If it trusts the peer, it SHALL store the peer’s credentials, including SKI and trust level (§12.2.2). §5 | §13.4.4.1, §12.2.2, §5 |
| Registration and reconnection | Registration is complete when both sides have confirmed each other with SME hello. Every later connection between those two devices MUST be treated as a reconnection, until one of them purposely aborts the hello handshake. §5.1 | §5.1 |
| Registration and reconnection | §5.2 (informative) allows two times at which A may decide to trust B’s SKI. Pre-trust: the SKI is trusted before any SME exchange, so the TLS handshake completes only when A already trusts B. Post-trust: the SKI may be accepted temporarily after TLS and trusted inside connection state hello, before SME connection-data exchange; the user is shown the SKI, and only acceptance allows further exchange; a refusal closes the connection. The §12.3.1 modes do not require either approach. Exchange of key material through a SHIP commissioning tool (§12.6) is always pre-trust. §5.2 | §5.2, §12.3.1, §12.6 |
| Registration and reconnection | On reconnection, a public key that still matches the key verified and trusted at registration SHALL be accepted again with no added wait. §6 | §6 |
| Registration and reconnection | Reconnection to a web server based node, in order: DNS for IP and port when a name is used; connect; check that the public key is still the registration key; SME. §6 | §6 |
| Registration and reconnection | Reconnection to a local node, described as the typical order: connect via discovery or accept an incoming connection; check that the public key is trusted and still the registration key; SME. §6 | §6 |
| Registration and reconnection | A reconnection should not need a user step, because trust ought to exist on both sides already. hello can confirm the peer immediately. What follows, in §13.4, is the protocol handshake, then PIN verification if it is used, then data exchange. §6 | §13.4, §6 |
| Registration and reconnection | §6.1 (informative) says a reconnection that must survive a key-material change depends on storing the SHIP ID (§7.4) and the foreign key material (§12.2.2), and on the update procedures in §12.1.3. More than one key-material set may exist for one SHIP ID. Adding a curve that was unsupported, or dropping a curve that was supported, has to be handled with care. §6.1 | §6.1, §7.4, §12.2.2, §12.1.3 |
| Closing a connection | §4.1 says manufacturers differ on how long a channel stays open, and that a connection limit or a duration limit can force a temporary close. A termination procedure exists so a sudden break can be told apart from a temporary disconnect. The procedure is §13.4.8, outside these pages. §4.1 | §4.1, §13.4.8 |
| Double connections | The public key SHALL also prevent double connections. After a successful TLS handshake, if two or more connections to the same peer exist at once, the node whose 160-bit SKI is larger SHALL keep only the most recent connection and close the others. The text says an earlier edition of this specification may allow a different preference. §12.2.3 | §12.2.3 |
| Double connections | If the older connection is already in SME connection data exchange, the node with the larger SKI SHOULD start the termination in §13.4.8. §12.2.3 | §13.4.8, §12.2.3 |
| Double connections | Either node, including the one with the smaller SKI, may close a connection if a timeout was detected or if the larger-SKI node does not close the extras within 3 seconds. After 3 seconds the smaller-SKI node SHALL send a WebSocket ping. A connection that does not return a proper Pong SHOULD be closed. If more than one connection still answers ping, the smaller-SKI node MAY close the older one, and SHOULD use the §13.4.8 termination if that older one is already in connection data exchange. §12.2.3 | §13.4.8, §12.2.3 |
| Double connections | The text does not say how a 160-bit SKI is ordered as an integer, and it does not set a separate Pong wait for this ping. The general pong wait is §10.4. | §10.4 |
| Certificates | A node MUST have a certificate and MUST present it in the TLS handshake whether it is client or server. The certificate MUST be self-signed or PKI-based, and MUST contain a SHIP-node-specific public key. No mandatory PKI is specified. §12.1.1 | §12.1.1 |
| Certificates | A key pair SHALL serve at most one certificate. A node certificate SHALL belong to at most one SHIP node. §12.1.1 | §12.1.1 |
| Certificates | Unknown PKI material is handled as self-signed, and the signature is not checked. SHIP interoperability is not tied to one PKI. §12.1.1 | §12.1.1 |
| Certificates | A revocation list MAY be fetched from a web server. With a synchronised clock, validity MAY be checked. Without that clock, a self-signed certificate SHOULD NOT carry a validity period. Where validity is absent, notAfter SHOULD be the RFC 5280 sentinel 99991231235959Z. Other checks MAY be applied; this version leaves them to the manufacturer. §12.1.1 | §12.1.1 |
| Certificates | The minimum check is a match between the certificate public key and an SKI that a verification mode trusts (§12.2). Lifetime checks and PKI checks are optional or left to the manufacturer. They SHALL leave ordinary SHIP authentication and communication unchanged. When they fail but the public key still authenticates, communication SHOULD continue. A PKI certificate that does not validate SHOULD be treated as self-signed, signature check excluded. That includes a PKI certificate whose lifetime does not validate: PKI trust is absent, and user trust MAY remain if the public key is trusted. The same applies when no synchronised clock exists to test lifetime. The user MAY be told why an optional check failed. §12.1.1 | §12.2, §12.1.1 |
| Certificates | Note 1 limits the interoperability baseline to the public key and the SKI, and warns that an expiry test can break that baseline. It also says a regulation or a proprietary rule may still demand the extra test, that SHIP does not cover that demand, and that interoperability with baseline devices can suffer. Note 2: a certificate that expires SHOULD have an update path from the manufacturer. §12.1.1 | §12.1.1 |
| Certificates | The certificate MAY be replaced, and with it the public key, the SKI and the private key (§12.1.3). If the user cannot be shown the new SKI, factory reset SHALL restore that earlier certificate and the public key, SKI and private key that belonged to it. §12.1.1 | §12.1.3, §12.1.1 |
| Certificates | Common name is outside this specification. Received certificates’ common names SHOULD be ignored. §12.1.1 | §12.1.1 |
| Certificates | A web server based node SHOULD have a PKI certificate. A node that wants to talk to it SHOULD hold the matching CA certificate. A CA certificate has no confidentiality requirement. The node MUST ensure that the stored CA certificate cannot be manipulated. §12.1.2 | §12.1.2 |
| Certificates | A public key need not be kept confidential and may travel in band. It checks signatures and takes part in ECDH. Its SKI identifies the node, supports user verification, and is what trust attaches to. The matching private key signs and takes part in ECDH. A note says that private key stays secret, is not sent, and is generally kept in a secure element. Symmetric keys are described as the material for mutual authentication and for encryption on a fast reconnect and while traffic flows. On these pages the only such material actually specified is the TLS session state in §12.4. The PIN is a second authentication step, separate from TLS, and optional; it exists to raise trust. §12 | §12.4, §12 |
| Certificate update states | §12.1.3 and its subsections cover reporting changes of a node’s own SHIP certificates to a peer. They were introduced in version 1.1.0 and are not supported by nodes built to an earlier version. They do not cover certificates of other protocols, root or intermediate certificates, or the means by which a node replaces its own certificate. The remote node’s SHIP version is taken from the SME Protocol Handshake (§13.4.4.2). §12.1.3 | §12.1.3, §13.4.4.2 |
| Certificate update states | An informative note says a vendor whose node A trusts a pre-1.1 node C should try not to let an update of A’s certificate break that link, and may skip the update when that is allowed; if the update cannot be skipped, the vendor should guide the user through establishing trust again with every connected pre-1.1 node. §12.1.3 | §12.1.3 |
| Certificate update states | Four certificate roles: initial certificate (the certificate delivered with the device), predecessor certificate (previously used, no longer used), current certificate (the one in the TLS handshake now), successor certificate (the next one, which other nodes must receive before it replaces the current one). §12.1.3.1 | §12.1.3.1 |
| Certificate update states | Each supported TLS curve SHALL have a current certificate. Replacing a current certificate SHALL use a successor on the same curve. An active connection need not be torn down merely because the certificate is replaced; the new certificate matters for new connections. §12.1.3.1 | §12.1.3.1 |
| Certificate update states | After a key-material update, trusted peers SHALL be told the new state. Connection state hello carries that state as well (§13.4.4.1). §12.1.3.1 | §13.4.4.1, §12.1.3.1 |
| Certificate update states | The transition stage lasts a minimum of 1 month. Sending keyMaterialState to trusted nodes is what starts it. When it ends, the new certificate SHALL take the place of the current one. A changed secp256r1 certificate SHALL be reflected in TXT ski (§7.3.2). The procedure also says the new material SHALL stay marked successor of current throughout one month, after which current SHALL be relabelled predecessor and successor SHALL be relabelled current. Table 1’s recommendation is a quarter of the lifetime, and not shorter than 1 month. §12.1.3.1, §12.1.3.2, §4.2 | §7.3.2, Table 1, §12.1.3.1, §12.1.3.2, §4.2 |
| Certificate update states | A node MAY add or drop curves at runtime, because further key material is carried on the basis of key material that was already trusted. Replacing one curve with another still needs the transition stage, and the new curve’s certificate has to be announced as successor, so peers do not fall back to secp256r1. Removing a curve completely is also a certificate update: keyMaterialState then omits that curve. Trust between two nodes then continues only if they had already trusted each other on another shared curve. §12.1.3.1 | §12.1.3.1 |
| Certificate update states | If a successor exists, trusted peers SHALL receive its SKI inside keyMaterialState, and the current SKIs SHALL be in that message too. Predecessor SKIs are optional content. SKIs that are foreign SHALL be left out. A trusted relationship has to exist already. Fresh from the factory, what is current is the initial certificate, and no predecessor exists. §12.1.3.2 | §12.1.3.2 |
| Certificate update states | All available predecessor, current, and successor certificates SHALL be sent in exactly one keyMaterialState. The message’s updateCounter stands for the whole key-material state. The peer must answer with keyMaterialStateResponse (§12.1.3.3). §12.1.3.2 | §12.1.3.3, §12.1.3.2 |
| Certificate update states | If a connection to that peer is already up, the node SHALL use it. If no keyMaterialStateResponse arrives within 30 seconds, the node SHOULD send keyMaterialState again. If another 30 seconds pass with no response, the node SHALL close the connection and SHOULD open a new one. The new attempt follows the rules below for a peer that is not connected. §12.1.3.2 | §12.1.3.2 |
| Certificate update states | With no connection up, the node SHALL attempt one in order to deliver the update. Attempts whose only purpose is this update SHALL be at least 5 minutes apart. Success uses the 30-second rules above. An open connection may carry keyMaterialState more than once in either direction. §12.1.3.2 | §12.1.3.2 |
| Certificate update states | Successor SKIs and current SKIs taken from a received keyMaterialState SHALL be kept for the curve that this TLS session negotiated with the sender, and with the trust level of that sender. Other curves’ SKIs SHOULD stay untrusted. If they are kept and trusted anyway, the trust level stored with them SHALL be the sender’s level from that keyMaterialState. Predecessor SKIs on a supported curve MAY be removed, and they SHALL not stay trusted. §12.1.3.3 | §12.1.3.3 |
| Certificate update states | A note says the sender should not expect the receiver to trust a different curve automatically, and that a later SHIP version may change that recommendation. §12.1.3.3 | §12.1.3.3 |
| Certificate update states | After receiving keyMaterialState, the receiver SHALL send keyMaterialStateResponse within 20 seconds. That response means the message was received. It does not mean the SKIs were accepted. §12.1.3.3 | §12.1.3.3 |
| Certificate update states | A node SHALL NOT keep trust in foreign key material of that sender once the material is absent from the received keyMaterialState. §12.1.3.3 | §12.1.3.3 |
| Certificate update states | Key material at the sender has changed when this updateCounter exceeds the one last stored from that sender. hello carries the same counter, so the change can show up the next time the peers connect. §12.1.3.3 | §12.1.3.3 |
| Certificate update states | A node MAY treat its stored copy of a peer’s key material as possibly outdated and MAY send keyMaterialStateRequest during SME connection data exchange. One stated reason is a higher keyMaterialState.updateCounter seen in hello. §12.1.3.4 | §12.1.3.4 |
| Certificate update states | A node that supports at least version 1.1 reports keyMaterialState.updateCounter in hello on every connection. If that value is higher than the stored counter for that trusted node, the receiver SHALL send keyMaterialStateRequest in the following connection data exchange. The request SHALL contain the updateCounter this node currently stores and trusts for the peer. §12.1.3.4 | §12.1.3.4 |
| Certificate update states | If the updateCounter inside a received keyMaterialStateRequest differs from the receiver’s current value, the receiver SHALL send keyMaterialState as in §12.1.3.2. §12.1.3.4 | §12.1.3.2, §12.1.3.4 |
| Certificate update states | A decrease of updateCounter is not treated as a valid trustworthy action. A keyMaterialState whose counter decreased SHALL be ignored. Downgrading certificates is not intended. §12.1.3.4 | §12.1.3.4 |
| Certificate update states | A certificate update can make a printed SKI on a label or QR code obsolete, so verification modes that need an SKI can no longer use it. That is called out as a particular problem when the other node supports only user verification with the pre-trust approach. It is strongly recommended that the user can obtain the updated SKIs, for example from a local or vendor web page, from an application, or from a display on the device. §12.1.3.5 | §12.1.3.5 |
| SKI and storage | Each certificate MUST have its own node-specific public key. The SKI SHALL be that key’s SHA-1, using method 1 of RFC 3280 clause 4.2.1.2. A received public key SHALL be compared with a trusted SKI. §12.2 | §12.2 |
| SKI and storage | The check extracts the public key, computes SHA-1, and requires a match both to an already trusted SKI and to the certificate’s own SKI (§12.2.1). A mismatch means the certificate is not valid and the communication must be aborted. §12.2 | §12.2.1, §12.2 |
| SKI and storage | The user MUST be able to see the whole SKI. For user verification, the SKI on display SHALL be the one in the certificate that TLS is using now. The subject-key-identifier extension has to equal the SKI the user trusts. That equality is required and does not finish the check; §12.2 still requires the public-key comparison. §12.2.1 | §12.2, §12.2.1 |
| SKI and storage | The 20-byte SKI SHALL be shown as 40 hexadecimal digits with a space after every four digits. A prefix and a separating space SHALL be added: SKI for secp256r1, BSKI for brainpoolP256r1, B2SKI for brainpoolP384r1. Versions before 1.1 used no prefix for secp256r1. The SKI MAY also be placed in a QR code with the PIN (§12.7, outside these pages). §12.2.1 | §12.7, §12.2.1 |
| SKI and storage | At least one of these MUST be provided: a label on the node; a user interface of the node; a local communication interface such as NFC, which must give easy access to the SKI; a cloud user interface, reached through the serial number or another node-specific distinction. §12.2.1 | §12.2.1 |
| SKI and storage | A note: if the only copy of the SKI is a label, that label has to change with the certificate. If a new label is not practical, the initial certificate should stay, or factory default should be able to bring it back. §12.2.1 | §12.2.1 |
| SKI and storage | Each trusted foreign SKI SHALL be stored with the trust level that belongs to it. Storing SKIs that arrived in keyMaterialState SHALL include the updateCounter from that message. One foreign node may have several sets, split by state and by curve, and those sets MAY carry different trust levels. Keeping mandatory key material across restarts is a strong recommendation. §12.2.2 | §12.2.2 |
| SKI and storage | Untrusted foreign SKIs MAY be stored and SHALL be given user trust 0. The user SHOULD be able to remove selected trusted foreign public keys. The node SHALL provide a way to delete every stored foreign public key, for example by factory reset. §12.2.2 | §12.2.2 |
| SKI and storage | Factory default SHALL let the user return the node to its as-new condition, and SHALL delete all data the node stored during operation. §3 | §3 |
| SKI and storage | Optional stored values, not required: the public key (SHIP public keys are 256 bits or longer, against a 160-bit SKI); the curve; a non-secp256r1 flag; the SHIP ID; the key-material state (successor, predecessor, current); the node’s own certificate, especially a PKI certificate. A note says persistent SHIP IDs might be required by a specification above SHIP, and might be required by a later SHIP version. §12.2.2.1 | §12.2.2.1 |
| SKI and storage | keyMaterial.maxEntries states how many SKIs, with the data kept beside them, the node can hold. The message layout is §13.4.7.5. §12.2.2 | §13.4.7.5, §12.2.2 |
| Verification modes and trust | A node that stores one or more CA certificates MAY decide whether what it received is a PKI certificate or a self-signed one. A PKI certificate that matches MAY add PKI trust, scaled by how far that CA is trusted. A PKI certificate that fails validation should be treated as self-signed, and its signature is not the basis of trust. One of the modes below MUST always be used for the public key. §12.3 | §12.3 |
| Verification modes and trust | Each mode produces a user-trust level, and each mode needs the user to act. Reuse of a stored public key MUST still expose that level. At least one mode is mandatory. Several modes MAY run at the same time. A later, stronger verification of the same key SHALL replace the stored level with the stronger mode’s level. §12.3.1 | §12.3.1 |
| Verification modes and trust | PKI trust is not a verification mode. §12.3.1 | §12.3.1 |
| Verification modes and trust | Levels named in §12.3.1, listed here from the last mode backward: SHIP commissioning is either user trust 32, or user trust 8 with second-factor trust 32. User input is user trust 64. Manufacturer commissioning is user trust 32 through 96, depending on the tool. User verify is user trust 32. Auto accept plus a PIN is user trust 8 with second-factor trust in the range 16–32. Auto accept alone is user trust 8. §12.3.1 | §12.3.1 |
| Verification modes and trust | Table 10, read from the bottom of the printed rows: optional PKI is PKI trust 0 through 65535, set by node policy. SHIP commissioning is either user trust 32, or user trust 8 together with second-factor trust 32. User input is user trust 64. Commissioned is user trust 32 through 96, depending on the tool. User verified is user trust 32. Auto accept plus a PIN is printed as user trust 32, with second-factor trust 16 or 32; the 32 is reserved for the first sender of the PIN (§12.5). Auto accept alone is user trust 8. Untrusted is user trust 0. §12.3.2 | Table 10, §12.5, §12.3.2 |
| Verification modes and trust | Item 2 of §12.3.1 sets user trust to 8 for auto accept plus a PIN. The Table 10 cell for that same row prints user trust 32. The worked figures in §12.3.1.6, for a tool accepted by auto accept plus a PIN, use a user-trust figure of 8 and a second-factor figure of 32. §12.3.1, §12.3.2, §12.3.1.6 | §12.3.1, Table 10, §12.3.1.6, §12.3.2 |
| Verification modes and trust | Trust gained through SHIP commissioning equals the trust already given to the tool’s public key. The named ways to trust that tool are user verification, and auto accept together with a PIN. §12.3.1, §12.3.2 | §12.3.1, §12.3.2 |
| Verification modes and trust | Where several mechanisms fall in one category, only the highest level in that category SHALL count. The printed case is auto accept together with user verify, which yields user trust 32. §12.3.2 | §12.3.2 |
| Verification modes and trust | User trust 8 is the minimum for general communication. If user trust is below 8, communication SHALL be aborted. §12.3.2 | §12.3.2 |
| Verification modes and trust | SHIP commissioning requires 32 or higher in user trust or in second-factor trust. Either a second-factor level of 32 or a user-trust level of 32 is enough. §12.3.2 | §12.3.2 |
| Verification modes and trust | General communication SHALL also be possible with PKI trust 0. PIN is the only second factor and MAY contribute 16–32 in that category (§12.5). A layer above SHIP MAY use the trust level to gate features; those requirements MAY depend on the feature, the application, and legal or device security requirements. §12.3.2 | §12.5, §12.3.2 |
| Verification modes and trust | No rule on these pages maps a commissioning tool’s trustworthiness onto a specific integer inside 32–96, or a PKI policy onto a specific integer inside 0–65535. | clause not printed |
| Auto accept | Auto accept should be implemented only by very simple nodes with no user interface. It is the least secure mode. A node that has a user interface able to support another mode, such as user verify, SHALL NOT implement auto accept. §12.3.1.1 | §12.3.1.1 |
| Auto accept | When the user triggers auto accept, for example with a push button, the node SHALL open a time window and MUST automatically accept one unknown foreign public key received during registration. If both peers support several curves, the highest-ranked curve and its SKI are the ones chosen. §12.3.1.1 | §12.3.1.1 |
| Auto accept | A single window SHALL take in one unknown foreign public key and no second one. Acceptance SHALL end auto accept immediately. §12.3.1.1 | §12.3.1.1 |
| Auto accept | Because the unknown key is not verified, the window SHALL be kept as short as usability allows and MUST be less than or equal to 2 minutes. Table 1 prints the range ≤ 120s and recommends 60s. §12.3.1.1, §4.2 | Table 1, §12.3.1.1, §4.2 |
| Auto accept with PIN | Using auto accept only together with a PIN is strongly recommended. A note says another verification procedure still needs to be supported, because other nodes may be unable to enter a PIN. §12.3.1.2 | §12.3.1.2 |
| Auto accept with PIN | If the node also supports SHIP commissioning, it MAY set connectionPinState.pinState to required. If it does not support SHIP commissioning, that field SHALL NOT be required, because most nodes may be unable to enter a PIN. A commissioning tool can then create trust between a node that cannot enter a PIN and a node that requires one, if the requiring node supports SHIP commissioning. §12.3.1.2 | §12.3.1.2 |
| Auto accept with PIN | Where a PIN is mandatory after every auto accept, the window MAY run past 2 minutes. An unknown public key or SKI SHALL be kept only if that key’s owner also supplied the right PIN. The window SHALL then close. A peer that did not supply the right PIN has its key thrown away, and throwing it away SHALL leave the window’s length unchanged. §12.3.1.2 | §12.3.1.2 |
| User verification | A node with a suitable display or user communication interface SHOULD implement user verification. If it also supports a curve other than secp256r1, it SHALL use TLS probing to see whether the peer’s TLS SKI belongs to another curve. §12.3.1.3 | §12.3.1.3 |
| User verification | An unknown foreign SKI seen in local mDNS, or in a TLS handshake, probing included, MUST be shown to the user, and the SKI itself MUST be part of what is shown. When several curves have SKIs, the one shown SHALL be the highest-ranked curve this node supports. §12.3.1.3 | §12.3.1.3 |
| User verification | Printed ranking examples: peers that share only secp256r1 show the secp256r1 SKI; peers that both support brainpoolP256r1, while one also supports brainpoolP384r1 and the other does not, show the brainpoolP256r1 SKI. §12.3.1.3 | §12.3.1.3 |
| User verification | User verification MAY also be applied to keys already stored, to raise user trust or to discard the key. §12.3.1.3 | §12.3.1.3 |
| Manufacturer-specific commissioning | This mode is called commissioning in the specification. It is a manufacturer’s own tool, limited to that manufacturer’s nodes, as distinct from interoperable SHIP commissioning. The resulting user trust depends on the tool. §12.3.1.4 | §12.3.1.4 |
| Manufacturer-specific commissioning | SKIs that arrive from the tool SHALL be kept across restarts, stamped with that tool’s user-trust level, and used when a public key has to be recognised. Nodes already known SHALL be checked for a public key that matches, and their trust level SHALL be updated. The tool MAY also deliver a revocation list or new key material. The user SHALL be in the procedure; consent is part of it, because this mode is user trust. §12.3.1.4 | §12.3.1.4 |
| User input | A node that is not a SHIP commissioning tool usually does not need this mode. It is useful for a commissioning tool (§12.6). §12.3.1.5 | §12.6, §12.3.1.5 |
| SHIP commissioning | Support for this mode is optional. Trusted SHIP key material moves on a SHIP connection that is already protected, between this node and a trusted peer in the commissioning-tool role. The messages are the SME exchange in §13.4.7. With auto accept plus a PIN, the node can do without a user interface of its own, because the tool provides the interface. §12.3.1.6, §12.6 | §13.4.7, §12.3.1.6, §12.6 |
| SHIP commissioning | A node A that supports the mode SHALL support these directions: receive commissioning request; send commissioning response; when providing key material that is foreign to A, receive key material request and send key material; when receiving key material that is foreign to A, send key material request, receive key material, send key material response, receive key material delete, and send key material delete response. §12.3.1.6 | §12.3.1.6 |
| SHIP commissioning | A commissioning request SHALL be refused unless user trust is 32 or more, or second-factor trust is 32 or more while user trust is 8 or more. Reaching that bar requires a second mode: either user verify, which yields user trust 32, or, after factory default, auto accept together with a PIN, which yields second-factor trust 32. Auto accept with no PIN cannot authenticate here; its user trust of 8 is below the bar. §12.3.1.6 | §12.3.1.6 |
| SHIP commissioning | Once a commissioning tool has been accepted, the node MAY turn off its other verification modes until factory default. §12.3.1.6 | §12.3.1.6 |
| SHIP commissioning | If the trust bar is met, the requester SHOULD be accepted in the commissioning-tool role, and commissioning response SHOULD carry commissioningResponse.accept true. That acceptance SHOULD be remembered, for example with a flag. Memory of it SHALL last at least as long as the TLS session. §12.3.1.6 | §12.3.1.6 |
| SHIP commissioning | The node SHALL add and update foreign SKIs and public keys from a key material message of an accepted, trustworthy tool, except when the curve is not supported, the curve is not used between the nodes, or memory does not allow it. If the message contains more entry items than this node’s keyMaterial.maxEntries, the node MAY drop entries that do not fit. The trust level of a rejected SKI SHALL be set to zero in key material response. The tool’s message may contain only a selection of entries. §12.3.1.6 | §12.3.1.6 |
| SHIP commissioning | The node SHALL delete every foreign SKI and public key named by a key material delete from an accepted, trustworthy tool. It MAY ask that tool for SKI updates with key material request. It cannot tell whether a received key material was requested or was sent unsolicited. On a key material request from an accepted, trustworthy tool, it SHALL reply with key material containing every foreign SKI and public key whose user trust is greater than 0. §12.3.1.6 | §12.3.1.6 |
| SHIP commissioning | For each received SKI S, the limit x SHALL be the highest of: (a) user trust of the tool’s SKI at this node, (b) second-factor trust of the tool’s SKI at this node, (c) the user trust this node already has for S, or 0 if S was unknown. If the received trust d is above x, it SHALL be cut down to x. The resulting user trust, cut down or not, is what key material response expresses. §12.3.1.6 | §12.3.1.6 |
| SHIP commissioning | The printed numerical case: an SKI entered by user input has user trust 64; the commissioned node trusted the tool by auto accept + PIN, so (a) is 8 and (b) is 32; the SKI is new, so (c) is 0; 64 is cut to 32. §12.3.1.6 | §12.3.1.6 |
| PIN | How the PIN is carried on the wire is §13.4.4.3, outside these pages. Here the PIN is tied to the node’s public keys and SKIs. It SHALL go only to the peer that cryptography shows holds the matching public key. The sender SHOULD drop the PIN once it has been sent. §12.5 | §13.4.4.3, §12.5 |
| PIN | The PIN SHALL NOT be sent when the peer’s public key has user trust below 32. §12.5 | §12.5 |
| PIN | The first peer after factory default that sends this node’s PIN MAY receive second-factor trust 32, and therefore MAY be allowed to act as a commissioning tool. Two peers cannot both hold second-factor trust 32 from this PIN. Every later sender SHALL receive only second-factor trust 16. Giving 32 to a different peer requires a factory reset; after that reset, the first sender MAY again receive 32. §12.5 | §12.5 |
| PIN | is captioned as mutual authentication with QR codes and a smart phone. Its visible labels are a commissioning app, a SHIP node, registration, and mutually authenticated. The QR contents are §12.7, outside these pages. §12.5 | §12.7, §12.5 |
| PIN | The PIN SHALL be shown to the user as 8 to 16 hexadecimal digits, equivalent to 32 to 64 bits. In a graphical presentation, spaces should be inserted every four digits, and the prefix PIN SHALL appear in front, separated by a space. The PIN MAY also be put in a QR code with the SKI (§12.7). §12.5 | §12.7, §12.5 |
| PIN | The user MAY change the PIN, for example through a user interface. Factory reset MUST restore the original PIN. A runtime change SHALL NOT change the trust level of nodes already trusted. To make other nodes enter the PIN again, the user MUST delete the trust relationship with that node, which forces a new registration. §12.5 | §12.5 |
| Commissioning tool, start of §12.6 | On the tool is a trusted node. It moves trusted key material on a protected SHIP connection to a node that implements the SHIP commissioning verification mode. That movement is the SME exchange of §13.4.7. §12.6 | §13.4.7, §12.6 |
| Commissioning tool, start of §12.6 | User input MAY be supported on the tool. If it is supported, the tool SHALL be able to scan labels and QR codes that carry SKIs and PINs. The requirement continues in the cited clause. §12.6 | §12.6 |
| JSON representation | The transformation rules apply to every data structure in §13.4 that is defined with XSD. Those are called explicit SHIP structures. data.payload may carry another specification, named by protocolId. That specification MAY use these rules, and each protocolId may define different rules for payload. §11.4.1 | §13.4, §11.4.1 |
| JSON representation | JSON’s six types are number, string, boolean, array, object, and null. The text is key/value pairs inside curly brackets, or an ordered sequence inside square brackets, with commas between members. §11.2 | §11.2 |
| JSON representation | A missing minOccurs is treated as 1, which makes the field mandatory. minOccurs of 0 allows the field to be left out. maxOccurs above 1 produces a JSON array no longer than that count; unbounded sets no cap. A missing maxOccurs is treated as 1, and no array is built. Both attributes at 0 mean the element drops out. §11.4.3 | §11.4.3 |
| JSON representation | Restriction facets such as minLength, maxLength, and enumeration limit values for JSON the same way as for XML. §11.4.4 | §11.4.4 |
| JSON representation | Inside xs:complexType, xs:sequence and xs:choice become a JSON array, xs:all becomes a JSON object, and no compositor becomes an array. Nested in xs:sequence or xs:choice, xs:sequence and xs:choice are merged into the parent with no extra level, and xs:all is not allowed. Nested in xs:all, only xs:all is merged; xs:sequence and xs:choice are not allowed. A mark of omission means the item is left out. “Not allowed” means XML Schema 1.0 forbids that combination. §11.4.5 | §11.4.5 |
| JSON representation | xs:restriction and xs:extension inside complex or simple content are not themselves JSON components. JSON MUST follow the derived type: restrictions apply, and elements added by an extension MUST be transformed. Extensions that only add attributes to simple content are omitted. §11.4.5 | §11.4.5 |
| JSON representation | Generation rules: element names become object names; numbers become JSON numbers; booleans become JSON booleans; an empty element becomes an empty JSON array; a nil element becomes JSON null; a repeated element becomes a JSON array; attributes are absorbed; groups are inlined, and a group whose maxOccurs is greater than 1 may be inlined more than once. §11.4.6 | §11.4.6 |
| JSON representation | For explicit SHIP structures, XML namespace declarations are not copied into JSON, and a SHIP namespace prefix including the colon is removed, so the JSON name has no SHIP prefix. §11.4.6 | §11.4.6 |
| JSON representation | For an external specification inside data.payload, whether namespace declarations or prefixes are transformed may be set per protocolId. The default is that they are not transformed. If a declaration is transformed, the recommended shape is a JSON object whose name is @xmlns: plus the prefix and whose value is the schema reference. If a prefix is transformed, the recommended JSON name keeps the prefix and the colon. §11.4.6 | §11.4.6 |
| JSON representation | Turning JSON back into XML undoes §11.4. An extra rule: a JSON array that is empty SHALL be skipped when the XSD element is allowed to repeat. Table 9 shows that case as two JSON shapes and one XML result. Those example documents are not copied here. §11.5 | §11.4, Table 9, §11.5 |
| JSON representation | Tables 7 and 8 are worked XML/JSON examples. They are not separate normative values beyond the rules above. | clause not printed |
| Named connection states | SME hello, also called connection state hello. Both peers’ hello messages complete registration. A purposeful abort of that handshake ends the “already registered” condition. hello carries key-material state for a node that updates certificates, and version ≥ 1.1 reports keyMaterialState.updateCounter there. §5.1, §12.1.3.1, §12.1.3.4 | §5.1, §12.1.3.1, §12.1.3.4 |
| Named connection states | On a reconnection, once hello has confirmed trust, the named follow-on steps are data exchange, PIN verification where it is used, and the protocol handshake. §6 | §6 |
| Named connection states | Registration also names the steps SME Connection Mode Initialization and SME Connection Data Preparation, without defining their messages here. §5, §5 | §5 |
| Named connection states | SME connection data exchange is the state in which keyMaterialStateRequest is sent, and it is the state used when deciding how to close a duplicate connection. §12.1.3.4, §12.2.3 | §12.1.3.4, §12.2.3 |
| Named connection states | Post-trust, if the user refuses the SKI, the connection closes before connection-data exchange. §5.2 | §5.2 |
| Named connection states | User trust below 8 aborts communication. §12.3.2 | §12.3.2 |
| Named connection states | A probing TLS client stops after the Server Certificate when the derived SKI is not yet trusted. §9.8 | §9.8 |
| Named connection states | Auto accept ends immediately after one unknown key is accepted. With a mandatory PIN, the window ends when the correct PIN arrives, and a missing or wrong PIN does not change the window. §12.3.1.1, §12.3.1.2 | §12.3.1.1, §12.3.1.2 |
| Named connection states | Certificate roles move from successor to current, and the old current to predecessor, at the end of the transition stage. A lower updateCounter does not move them; that message is ignored. §12.1.3.2, §12.1.3.4 | §12.1.3.2, §12.1.3.4 |
| Named connection states | A higher hello counter causes keyMaterialStateRequest in the following connection-data exchange. A request counter that differs from the receiver’s current counter causes keyMaterialState. No response within 30 seconds should cause a resend; another 30 seconds closes the connection. §12.1.3.4, §12.1.3.2 | §12.1.3.4, §12.1.3.2 |
| Named connection states | Two connections to the same peer collapse as in §12.2.3: the larger SKI keeps the newest; after 3 seconds the smaller SKI pings; a connection with no Pong should close. §12.2.3 | §12.2.3 |
| Named connection states | A data frame that is not opcode 0x2 terminates the WebSocket with 1003 or 1002 as in §10.3. §10.3 | §10.3 |
| Named connection states | The full set of SME message types is Table 11, outside these pages. Message names that these pages do use are: hello; Protocol Handshake; connectionPinState; keyMaterialState; keyMaterialStateResponse; keyMaterialStateRequest; commissioning request; commissioning response; key material request; key material; key material response; key material delete; key material delete response; and the data message that carries protocolId and data.payload. | Table 11 |
| Wire, transport, TLS, ports, discovery | A SHIP message, once it is on the wire, is size-bounded and has both a beginning and an ending. No octet limit is printed (§13.2). | §13.2 |
| Wire, transport, TLS, ports, discovery | Figure 9 names these layers from the application side downward: SHIP Application paired with SME User; then SHIP Message; then SHIP Message Exchange (SME); then SHIP Transport; then WebSocket; then TLS; then TCP. Which boxes are white and which are grey is not recorded. This chapter’s rules are the white boxes; the grey boxes are reference only. The drawing is not an implementation structure the specification demands. | clause not printed |
| Wire, transport, TLS, ports, discovery | This revision’s transport puts exactly one wire-format SHIP message in exactly one WebSocket message. FIN is set on the final fragment only. The sentence ties that framing to the security method in use. | clause not printed |
| Wire, transport, TLS, ports, discovery | No TCP or UDP port number is printed on these pages. | clause not printed |
| Wire, transport, TLS, ports, discovery | No mDNS service type and no TXT key are printed here. Chapter 7 is only cited. What is printed: a commissioning tool must show, on a display, every SKI of SHIP nodes found by mDNS. accessMethods.dnsSd_mDns is present when the sender offers the chapter 7 discovery, and then accessMethods.id must carry the unique ID (Table 22). | Table 22 |
| Wire, transport, TLS, ports, discovery | Unicast DNS, when used, is signalled by accessMethods.dns plus accessMethods.dns.uri. This version only uses URI scheme wss. No DNS record type is named. | clause not printed |
| Wire, transport, TLS, ports, discovery | Curves printed for key material, as IANA TLS Supported Groups numbers: 23 secp256r1, 26 brainpoolP256r1, 27 brainpoolP384r1 (Tables 26–30). No cipher suite, certificate profile, lifetime, or signature algorithm is printed on these pages. | clause not printed |
| Wire, transport, TLS, ports, discovery | A public key carried beside an SKI must match that SKI (Tables 26, 27, 29, 30). SKI and public key, where a type is printed, are xs:hexBinary. Lengths are not printed. | clause not printed |
| Wire, transport, TLS, ports, discovery | keyMaterialState.updateCounter starts at 1 in the factory-new condition and rises by 1 on each certificate change and each certificate addition (Table 30). §13.4.7.1 names certificate updates without a user action as a purpose, and points the behaviour at §12.1.3. | Table 30, §13.4.7.1, §12.1.3 |
| Wire, transport, TLS, ports, discovery | Hello’s updateCounter also points at §12.1.3 (Table 12). knownUpdateCounter repeats the newest value learned from hello or from keyMaterialState, or 0 if none has been learned (Table 32). | §12.1.3, Table 12, Table 32 |
| Extensibility rules that apply to the messages | RFU may be specified later only by the specification authority. It is not for manufacturer-specific use. A later release may assign a former RFU region regardless of any manufacturer use. | clause not printed |
| Extensibility rules that apply to the messages | By default a well-defined parent allows only known children. | clause not printed |
| Extensibility rules that apply to the messages | Where default structure extensibility is stated, a later specification may add children after the last known child, not before it and not between known children. The mark applies only to immediate children unless it is the recursive form. Manufacturer-specific children are not allowed by that mark. | clause not printed |
| Extensibility rules that apply to the messages | The mark is stated for: connectionHello, messageProtocolHandshake, messageProtocolHandshakeError, connectionPinState, connectionPinInput, connectionPinError, data (first level), data.header (recursive), data.extension (first level), accessMethodsRequest, accessMethods, commissioningRequest, commissioningResponse, keyMaterialRequest, keyMaterial, keyMaterialResponse, keyMaterialDelete, keyMaterialDeleteResponse, keyMaterialState, keyMaterialStateResponse, keyMaterialStateRequest, connectionClose. | clause not printed |
| Extensibility rules that apply to the messages | SHIP-defined payload content uses default structure extensibility (recursive). Other payload content follows the authority of the protocolId base. | clause not printed |
| Extensibility rules that apply to the messages | For one message variant, every allowed representation must be equivalent, including a lossless conversion. Representations named as permitted depending on scope: JSON-UTF8, JSON-UTF16, binary, and mixed or message-dependent. | clause not printed |
| Extensibility rules that apply to the messages | JSON-UTF8 is mandatory for the hello value, both handshake values, and connectionClose. PIN, data, access-methods, and all §13.4.7 values use the format the handshake selected (each message’s “format of this structure” sentence). | §13.4.7 |
| Extensibility rules that apply to the messages | This version runs the handshake exchange itself only in JSON-UTF8. After CLIENT_OK or SERVER_OK, the selected version and format apply. | clause not printed |
| Pairing and trust | User verification on a commissioning tool: show all mDNS SKIs; the user can select trusted SKIs. Updated SKIs, including invalid labels or QR codes, are deferred to §12.1.3.5. | §12.1.3.5 |
| Pairing and trust | Reverification: show trusted SKIs taken from commissioned nodes; if the user reverifies an SKI, the tool assigns a user trust level according to that verification; the user can delete untrusted or deprecated SKIs. The numeric trust scale is not printed on these pages. | clause not printed |
| Pairing and trust | Commissioning right: tool sends commissioningRequest. That message also tells the peer that the sender can act as a commissioning tool. It should be sent on every connection, subject to the §13.4.7 ban on sending before data exchange. | §13.4.7 |
| Pairing and trust | accept true: the tool is permitted to read, insert, or remove trustworthy key material on the node that answered. The printed verb is the lowercase word “may”. accept false: that node rejected the tool. The printed example cause is a trust level that was too low. No answer at all: the node might not support SHIP commissioning. | clause not printed |
| Pairing and trust | To reverify a commissioned node’s key material, the tool sends keyMaterialRequest. On keyMaterial, the tool shows that sender’s trustworthy SKIs to the user. | clause not printed |
| Pairing and trust | New key material is added only when a user acts on the SHIP node or on the commissioning tool. | clause not printed |
| Pairing and trust | A commissioning-capable node may ask a tool for key material. The tool answers with foreign trustworthy SKIs and public keys, or with zero entries if it has none relevant. | clause not printed |
| Pairing and trust | A tool that wants to add foreign SKIs sends keyMaterial. The peer’s keyMaterial.maxEntries is an upper bound on what that peer can store. The tool should fetch that bound, by a keyMaterialRequest, before the add. The bound’s definition is in §12.3.1.6. | §12.3.1.6 |
| Pairing and trust | Introducing another commissioning tool: send its SKI and public key with keyMaterial.entry.commissioningTool true. The printed purpose is redundancy if the other tool can no longer be used. | clause not printed |
| Pairing and trust | Deleting foreign SKIs: keyMaterialDelete carrying those SKIs. | clause not printed |
| Pairing and trust | Informative only: the tool is for user-controlled actions; automatic key changes are not the intent; this specification defines no synchronisation between two commissioning tools; if two tools act automatically on differing key state, they can keep changing keys, and neither a node nor the tools can tell which state is newer from these rules. | clause not printed |
| Pairing and trust | Hello trust flags, not a certificate check: basic state READY may be entered only when the peer is already trusted. PENDING means this side is not yet ready to leave Hello. Whether the peer is trusted is assumed known; lower layers define how trust is decided and whether it is stored. An informative remark ties that decision to certificate and public-key presentation in section 12, including the case of auto accept, and says it can finish before CMI. Auto accept is not given fields on these pages. | clause not printed |
| Pairing and trust | pinState required: this node’s own valid PIN must arrive before data exchange is reached. Note, not a SHALL: use this value only in certain cases, and the maker should also provide a SHIP commissioning tool that can enter a PIN. | clause not printed |
| Pairing and trust | pinState optional: data exchange may start without the PIN, limited to data that do not need the PIN; a later valid PIN opens all data. The attached note says the peer is not forced to send a PIN, the node keeps optional, and it keeps listening. | clause not printed |
| Pairing and trust | pinState pinOk: own valid PIN already received; unrestricted exchange; data exchange may be entered immediately. | clause not printed |
| Pairing and trust | pinState none: the node has no PIN; unrestricted exchange; data exchange may be entered immediately. | clause not printed |
| Pairing and trust | inputPermission busy: PIN input is not accepted for verification. ok: it is accepted. While a penalty toward that peer is in force, required or optional must use busy; otherwise they must use ok. | clause not printed |
| Pairing and trust | The PIN owner must not send its own PIN outward. Only the peer may send that PIN to the owner. Which devices need a PIN, how the user sees it, which values are too simple, and how a PIN changes a trust level are deferred to chapter 12. | clause not printed |
| Pairing and trust | removedConnection removes that node from the known or accepted set. The informative remark says a later connection treats it as a new or unknown device. unspecific is the reason when no other printed reason fits. The informative remark calls that reason a temporary disconnect, with examples of a single-connection device and a reboot, and says a later connection is likely. | clause not printed |
| Pairing and trust | If both sides start a close together, a received removedConnection outweighs a received unspecific. | clause not printed |
| QR code limits | Module size at least 330×10⁻⁶ m, stated to equal 4 pixels at 300 dpi. | clause not printed |
| QR code limits | Quiet zone at least 4 modules wide. | clause not printed |
| QR code limits | example, SKI and PIN only: 33 × 0.33 mm = 10.89 mm, quiet zone excluded. | clause not printed |
| QR code limits | example, with the optional text values: 47 × 0.33 mm = 15.51 mm, quiet zone excluded. The text says another example can differ because ID, BRAND, TYPE, and MODEL vary in length. | clause not printed |
| QR code limits | (both brainpool SKIs) has a caption and no printed millimetre size. | clause not printed |
| QR code limits | Field order that is printed: SHIP;, then SKI:, then PIN: if the node has a PIN, then ID: (after PIN if present, otherwise after SKI), then BRAND: after ID, TYPE: after BRAND, MODEL: after TYPE, BSKI: after MODEL, B2SKI: after BSKI. | clause not printed |
| CMI states | Step: CMI_STATE_CLIENT_SEND; Behaviour: Client sends CMI with MessageValue = 0, then immediately enters CMI_STATE_CLIENT_WAIT. | clause not printed |
| CMI states | Step: CMI_STATE_SERVER_WAIT; Behaviour: The server’s wait for the client’s CMI. | clause not printed |
| CMI states | Step: CMI_STATE_SERVER_EVALUATE; Behaviour: If MessageType is not 0: send CMI MessageValue = 0, then close. If CmiHead decimal is 0: send CMI MessageValue = 0 and enter connection data preparation. If CmiHead is greater than 0: send CMI MessageValue = 0, then close. | clause not printed |
| CMI states | Step: CMI_STATE_CLIENT_WAIT; Behaviour: The client’s wait for the server’s CMI. | clause not printed |
| CMI states | Step: CMI_STATE_CLIENT_EVALUATE; Behaviour: If MessageType is not 0: close immediately. If CmiHead is 0: enter connection data preparation. If CmiHead is greater than 0: close immediately. Those failure steps name a close and do not name a CMI send. | clause not printed |
| Hello states and timers | Name: T_hello_init; Printed value: a duration of at least 60 seconds; 240 seconds is inside the allowed top. Fixed for the life of the connection. Should also stay fixed from one connection to the next; Expiry: default of Wait-For-Ready-Timer | clause not printed |
| Hello states and timers | Name: T_hello_inc; Printed value: equals the duration chosen for T_hello_init; Expiry: added onto Wait-For-Ready-Timer when a prolongation is accepted | clause not printed |
| Hello states and timers | Name: T_hello_prolong_thr_inc; Printed value: threshold length 30 seconds; Expiry: compared with received waiting | clause not printed |
| Hello states and timers | Name: T_hello_prolong_waiting_gap; Printed value: gap length 15 seconds; Expiry: subtracted from received waiting to arm Send-Prolongation-Request-Timer | clause not printed |
| Hello states and timers | Name: T_hello_prolong_min; Printed value: 1 second; Expiry: if the subtraction result is lower than this, that send-timer is disabled | clause not printed |
| Hello states and timers | Name: Wait-For-Ready-Timer; Printed value: default T_hello_init; Expiry: peer must send ready, or a prolongation request, before expiry. The timer’s own unit is not named. waiting, which reports the timer’s current value, is in milliseconds | clause not printed |
| Hello states and timers | Name: Send-Prolongation-Request-Timer; Printed value: see subtraction above; Expiry: local request sent before the peer’s Wait-For-Ready-Timer expires | clause not printed |
| Hello states and timers | Name: Prolongation-Request-Reply-Timer; Printed value: last received waiting; if none has been received, 1.1 times the current Wait-For-Ready-Timer; Expiry: abort if the reply does not arrive | clause not printed |
| Hello states and timers | Sub-state: SME_HELLO_STATE_READY_INIT; Entry and exit: First state of READY. Start Wait-For-Ready-Timer at its default, stop both prolongation timers, send a hello update, go to READY_LISTEN. Messages that arrive before or during this sub-state are not evaluated here. | clause not printed |
| Hello states and timers | Sub-state: SME_HELLO_STATE_READY_LISTEN; Entry and exit: phase ready: go to HELLO_OK. pending and no prolongationRequest: ignore. pending and prolongationRequest true: run the accept/refuse procedure, then send a hello update. aborted: abort. Any non-hello message: abort. | clause not printed |
| Hello states and timers | Sub-state: SME_HELLO_STATE_READY_TIMEOUT; Entry and exit: Wait-For-Ready-Timer expired: abort. | clause not printed |
| Hello states and timers | Sub-state: SME_HELLO_STATE_PENDING_INIT; Entry and exit: Same four setup actions as READY_INIT, then PENDING_LISTEN. The “do not evaluate yet” sentence is printed only under READY_INIT. | clause not printed |
| Hello states and timers | Sub-state: SME_HELLO_STATE_PENDING_LISTEN; Entry and exit: ready and no waiting: abort. ready with waiting: stop Wait-For-Ready-Timer and the reply timer; if waiting meets or exceeds T_hello_prolong_thr_inc, arm Send-Prolongation-Request-Timer as above, otherwise stop it. pending with waiting and no prolongationRequest: stop the reply timer and apply the same arm/stop rule. pending, no waiting, prolongationRequest true: accept/refuse, then hello update. aborted: abort. Any other shape: abort. A non-hello message: abort. A local decision not to trust: abort. | clause not printed |
| Hello states and timers | Sub-state: SME_HELLO_STATE_PENDING_TIMEOUT; Entry and exit: Wait-For-Ready-Timer expired: abort. Send-Prolongation-Request-Timer expired: send hello with phase pending, prolongationRequest true, and no other sub-element; start the reply timer; return to the previous state. Reply timer expired: abort. | clause not printed |
| Hello states and timers | Sub-state: HELLO_OK; Entry and exit: Hello timers may be stopped. Continue with protocol handshake. | clause not printed |
| Protocol handshake states | State: SME_PROT_H_STATE_SERVER_INIT; Behaviour: Start Wait-Timer. Go to SME_PROT_H_STATE_SERVER_LISTEN_PROPOSAL. The server does not send first. | clause not printed |
| Protocol handshake states | State: SME_PROT_H_STATE_CLIENT_INIT; Behaviour: Send announceMax as above. Start Wait-Timer. Go to SME_PROT_H_STATE_CLIENT_LISTEN_CHOICE. | clause not printed |
| Protocol handshake states | State: SME_PROT_H_STATE_SERVER_LISTEN_PROPOSAL; Behaviour: On a valid handshake message: stop the timer, select version and one format, send handshakeType select with that version and that format, restart the timer, go to SME_PROT_H_STATE_SERVER_LISTEN_CONFIRM. Otherwise abort with unexpected message. | clause not printed |
| Protocol handshake states | State: SME_PROT_H_STATE_CLIENT_LISTEN_CHOICE; Behaviour: On a valid handshake message: stop the timer; handshakeType must be select; version must be inside the client’s capability; formats must contain a single format inside the client’s capability. Then send that same message back and enter SME_PROT_H_STATE_CLIENT_OK. A failed check aborts with selection mismatch. Any other message aborts with unexpected message. | clause not printed |
| Protocol handshake states | State: SME_PROT_H_STATE_SERVER_LISTEN_CONFIRM; Behaviour: On a valid handshake message: stop the timer; the message must be identical to the one this server sent in SERVER_LISTEN_PROPOSAL; then enter SME_PROT_H_STATE_SERVER_OK. A failed check aborts with selection mismatch. Any other message aborts with unexpected message. | clause not printed |
| Protocol handshake states | State: SME_PROT_H_STATE_TIMEOUT; Behaviour: Wait-Timer expired: abort with timeout. Table 15 prints the error type as Timeout. | Table 15 |
| Protocol handshake states | State: SME_PROT_H_STATE_CLIENT_OK and SME_PROT_H_STATE_SERVER_OK; Behaviour: Switch to the selected version and format, then enter PIN verification. | clause not printed |
| PIN states, penalties, and the data-exchange gate | Invalid-PIN count: less than 3; Penalty: none | clause not printed |
| PIN states, penalties, and the data-exchange gate | Invalid-PIN count: from 3 to 5; Penalty: enter SME_PIN_STATE_CHECK_BUSY_WAIT, and stay there at least 10 seconds. The period should pass 15 seconds only where security requirements are higher. What those requirements are is not printed | clause not printed |
| PIN states, penalties, and the data-exchange gate | Invalid-PIN count: greater than 5; Penalty: same state, lasting at least 60 seconds. The period should pass 90 seconds only where security requirements are higher | clause not printed |
| PIN states, penalties, and the data-exchange gate | Sub-state: SME_PIN_STATE_CHECK_INIT; Behaviour: Send the current PIN requirement. If pinState is required: data exchange must be disabled; go to CHECK_BUSY_WAIT if inputPermission is busy, else CHECK_LISTEN. If optional: run the enable procedure; then the same busy/listen choice. If pinOk or none: run the enable procedure and enter CHECK_OK. | clause not printed |
| PIN states, penalties, and the data-exchange gate | Sub-state: SME_PIN_STATE_CHECK_LISTEN; Behaviour: inputPermission is already ok. Only PIN-verification messages are considered. Matching PIN: set pinState to pinOk, remove inputPermission, send the PIN requirement, run the enable procedure, enter CHECK_OK. Mismatch: enter CHECK_ERROR. | clause not printed |
| PIN states, penalties, and the data-exchange gate | Sub-state: SME_PIN_STATE_CHECK_ERROR; Behaviour: Increment the invalid count, send PIN error wrong PIN, return to CHECK_LISTEN if no penalty applies, otherwise enter CHECK_BUSY_INIT. | clause not printed |
| PIN states, penalties, and the data-exchange gate | Sub-state: SME_PIN_STATE_CHECK_BUSY_INIT; Behaviour: Set inputPermission to busy, send the PIN requirement, enter CHECK_BUSY_WAIT. | clause not printed |
| PIN states, penalties, and the data-exchange gate | Sub-state: SME_PIN_STATE_CHECK_BUSY_WAIT; Behaviour: Stay until the penalty duration ends. Each received PIN input only causes the PIN requirement to be sent again. When the penalty ends: set inputPermission to ok, send the PIN requirement, enter CHECK_LISTEN. | clause not printed |
| PIN states, penalties, and the data-exchange gate | Sub-state: SME_PIN_STATE_CHECK_OK; Behaviour: Discard PIN input with no reply. This branch ends. | clause not printed |
| PIN states, penalties, and the data-exchange gate | Sub-state: SME_PIN_STATE_ASK_INIT; Behaviour: Wait for a PIN state message. Until it arrives, do not evaluate any other PIN-verification message. Then enter ASK_PROCESS. If this sub-state lasts more than 10 seconds, close the connection. | clause not printed |
| PIN states, penalties, and the data-exchange gate | Sub-state: SME_PIN_STATE_ASK_PROCESS; Behaviour: See the numbered rules below. The state stays active and keeps listening unless a rule leaves it. | clause not printed |
| PIN states, penalties, and the data-exchange gate | Sub-state: SME_PIN_STATE_ASK_RESTRICTED_OK; Behaviour: Discard PIN error messages. Keep only the latest PIN state, and drop it if the connection closes. The branch ends. A later PIN send may re-enter ASK_PROCESS using that saved PIN state. | clause not printed |
| PIN states, penalties, and the data-exchange gate | Sub-state: SME_PIN_STATE_ASK_OK; Behaviour: Discard PIN error and PIN state messages. The branch ends. | clause not printed |
| Data-exchange acceptance rules | A specification sequence has one origin, called the base specification. | clause not printed |
| Data-exchange acceptance rules | Each version has zero or one immediate successor, and zero or one immediate predecessor. | clause not printed |
| Data-exchange acceptance rules | The base must define how a later version adds content so that a base implementation can accept that content. Processing must cover at least the parts the base already defines, and may skip unknown parts. | clause not printed |
| Data-exchange acceptance rules | Each later compatible version must define forward compatibility too, and must not break the base rules. | clause not printed |
| Data-exchange acceptance rules | An implementation of a given version must accept content from a compatible predecessor and must process the whole of that content. | clause not printed |
| Data-exchange acceptance rules | protocolId names the base even when the payload uses a newer compatible version. An unknown protocolId is skipped in silence; the connection is not closed by this rule. | clause not printed |
| Data-exchange acceptance rules | Only the SHIP specification authority assigns protocolId values. A note says further SHIP requirements must be met before a specification can receive one. Those requirements are not listed here. | clause not printed |
| Data-exchange acceptance rules | The handshake format applies to the payload element and its contents. It does not choose the protocolId-specific types inside payload. An informative remark treats payload as an opaque container that is still well formed in the handshake format. | clause not printed |
| Data-exchange acceptance rules | extension is manufacturer-specific and is not specified further. | clause not printed |
| Access methods | Not entered before data exchange. Support is not mandatory in every case. The text says duties differ by role and then gives the recommendation below, not a second support matrix. | clause not printed |
| Access methods | There is no required occasion to send accessMethodsRequest. DEV-SERVER should ask for DEV-CLIENT’s access methods when DEV-SERVER must be able to open a later connection to that client and does not yet have the information. A note says this specification does not define binding or subscription; a higher-layer subscription is given as a typical reason. | clause not printed |
| Access methods | The recipient must answer with accessMethods. If no proper answer arrives within 60 seconds, the requester can close under §13.4.8. What “proper” means is not defined. | §13.4.8 |
| Access methods | Unsolicited accessMethods is forbidden. | clause not printed |
| Access methods | The recipient must store the received information persistently for a later connection it initiates. Lifetime and replacement rules are not printed. | clause not printed |
| Key-material message rules beyond the field table | The messages may run beside data exchange and must not be sent before data exchange is entered. | clause not printed |
| Key-material message rules beyond the field table | userTrust on keyMaterial.entry is greater than 0. Removing trust is a delete, not a zero in that message (Table 26). The delete response sets userTrust to 0 (Table 29). | Table 26, Table 29 |
| Key-material message rules beyond the field table | keyMaterialState.entry holds 1 to 256 SKIs owned by the sender. currentState distinguishes the key in use, an unused predecessor, and a successor that will be used soon (Table 30). | Table 30 |
| Key-material message rules beyond the field table | keyMaterialStateResponse.accept is true and only acknowledges receipt (Table 31). No false meaning is printed. | Table 31 |
| Key-material message rules beyond the field table | Send and receive of keyMaterialState, its response, and its request are mandatory for SHIP version ≥ 1.1. | clause not printed |
| Regular close | Does not cover a sudden break, and must not be used before data exchange. The SME close procedure does not depend on server or client. | clause not printed |
| Regular close | DEV-A sends phase announce, maxTime as the latest close instant in milliseconds counted from the send, and a reason. No range for maxTime is printed. | clause not printed |
| Regular close | DEV-A closes at the latest when maxTime elapses, even with no confirmation, and closes immediately if a confirmation arrives earlier. | clause not printed |
| Regular close | DEV-B prepares to stop data exchange before maxTime elapses. If that preparation finishes before maxTime and the connection has not yet closed, it sends phase confirm with no other sub-element and then closes. If it does not confirm in time, it treats the connection as closed when maxTime elapses. | clause not printed |
| Regular close | If both sides announce at nearly the same time, each is DEV-A and DEV-B, with its own maxTime. The first confirmation closes the connection; a confirmation from both sides is not required. | clause not printed |
| Regular close | Reconnection after this regular close should not be attempted immediately. Other reconnection behaviour is application-specific. No minimum wait is printed. | clause not printed |

## Open points

| point | what is printed | clause |
| --- | --- | --- |
| maximum fragment length | Table 1 prints 512 bytes. §9.2 prints 1024 bytes. Both stay. Neither is selected. | SHIP Specification 1.1.0 §9.2 Table 1 |
| SKI length | The parameter table and §12.2 print 20 bytes and 40 hexadecimal digits. The TXT value cell prints 40 byte and 160 bit. Both stay. | SHIP Specification 1.1.0 §12.2, §7 Table 2 |
| TCP or UDP port number | No numeric port is printed. The server port is the SRV port. | SHIP Specification 1.1.0 §7, §8 |
| retry period | No retry period is printed. | SHIP Specification 1.1.0 §5 |
| TLS idle time | No TLS idle time is printed. | SHIP Specification 1.1.0 §9 |
| SKI integer encoding | The hexadecimal digit form is printed. An integer encoding is not. | SHIP Specification 1.1.0 §12.2 |
| commissioning trust scale | The range 32 to 96 is printed. No finer picking rule is printed. | SHIP Specification 1.1.0 §12.3 |
| PKI trust scale | The range 0 through 65535 is printed. No finer picking rule is printed. | SHIP Specification 1.1.0 §12.3 |
| hello unit conversion | waiting is in milliseconds. The T_hello constants are in seconds. No conversion is printed. | SHIP Specification 1.1.0 §13.4.4.1 |
| message size | A limited size is named. No numeric maximum is printed. | SHIP Specification 1.1.0 §13 |
| auto accept with PIN | User trust 8 is printed in §12.3.1. User trust 32 is printed in Table 10. Both stay. | SHIP Specification 1.1.0 §12.3.1, §12.3.2 Table 10 |
| certificate-update timing | Table 1, the one-month floor, and the one-month successor marking are all printed. Which figure applies when they differ is not printed. | SHIP Specification 1.1.0 §12.1.3 |
| commissioningRequest | One clause says the request should go out on every connection. A later clause forbids key-material messages before data exchange. No combined rule is printed. | SHIP Specification 1.1.0 §12.6, §13.4.7 |
| hello updateCounter | Some hello messages forbid further sub-elements. Table 12 makes keyMaterialState.updateCounter mandatory for this revision. No combined rule is printed. | SHIP Specification 1.1.0 §13.4.4 Table 12 |
| TLS maximum fragment length, SHIP 1.0.1 and SHIP 1.1.0. Table 1 range cell is 512 bytes. §9.2 says the fragment-length extension, when used, offers only 1024 bytes, and outgoing TLSPlaintext.length SHALL NOT exceed 1024 bytes. Both editions print both numbers. Table 1 and §9.2; Table 1 §4.2 and §9.2. | Table 1, §9.2, §4.2 | clause not printed |
| SHIP 1.1.0 auto accept together with a PIN. §12.3.1 item 2 sets user trust 8 and a second-factor range 16–32. Table 10 prints user trust 32 for that row (§12.3.2). The worked figures in §12.3.1.6 use user trust 8 and second-factor 32. These clauses do not pick one user-trust integer. SHIP 1.0.1’s mode table assigns auto accept user trust 8 and does not print that extra user-trust row; its second-factor PIN cell is 16 or 32 in Table 12 and 16-32 in the §12.3.2 paragraph. | §12.3.1, Table 10, §12.3.2, §12.3.1.6, Table 12 | clause not printed |
| SHIP 1.1.0 certificate-update timing. Table 1 recommends one quarter of the certificate lifetime, floored at 1 month, and a range of at least 1 month. §12.1.3.1 requires at least 1 month. §12.1.3.2 says the successor marking lasts one month. These clauses do not say which figure applies when they differ. | Table 1, §12.1.3.1, §12.1.3.2 | clause not printed |
| SHIP 1.1.0 §12.6 says commissioningRequest should go out on every connection. §13.4.7 forbids key-material messages, including that request, before data exchange. No combined sentence is printed. | §12.6, §13.4.7 | clause not printed |
| SHIP 1.1.0. Hello update, hello abort, and the prolongation-request hello forbid further sub-elements. Table 12 makes keyMaterialState.updateCounter mandatory to send for SHIP version 1.1 or higher. These clauses do not reconcile the two. | Table 12 | clause not printed |
| General-communication trust gate is user trust at least 8 in both SHIP editions. SHIP 1.0.1 says that below 8, hello is aborted, and points the abort procedure at §13.4.4.1. SHIP 1.1.0 says that below 8, communication SHALL be aborted (§12.3.2). The abort target is not the same sentence. | §13.4.4.1, §12.3.2 | clause not printed |
| Trusted-node cross-reference. SHIP 1.0.1 points chapter 12.2.2, and the heading of §12.2.2 on those pages is the double-connection rule. SHIP 1.1.0 points §12.2.3 (§3), and on those pages §12.2.3 is the double-connection close. Verification modes are §12.3 in both editions. | §12.2.2, §12.2.3, §3, §12.3 | clause not printed |
| Clause numbers for the same late SHIP phase differ by edition. SHIP 1.0.1 places connection termination in §13.4.7. SHIP 1.1.0 places key-material messages in §13.4.7 and regular close in §13.4.8. | §13.4.7, §13.4.8 | clause not printed |
