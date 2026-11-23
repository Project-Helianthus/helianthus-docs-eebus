---
canonical_source: "Project-Helianthus/helianthus-docs-eebus:protocols/ship-1.0.1.md"
owner_domain: "protocols"
license: "CC0-1.0"
publication_status: "publishable"
claim_status: "evidence-backed"
source_class: "vendor_public"
evidence_ids: "EV-20260711-001"
hypothesis_status: "publishable"
falsifier: "A row states a number or duty the named clause does not state, or selects one side of a conflict the clauses leave open."
---

# SHIP Specification 1.0.1

Facts of this revision: identifiers, ranges, presence, and duties, each with its clause. Text of the specification is not reproduced. A conflict that the clauses both print stays unresolved.

## Parameters

| parameter | clause | value or range | unit |
| --- | --- | --- | --- |
| Initial TCP retransmission count | §8.3 | recommendation 2 | not printed |
| Initial TCP retransmission timeout | §8.4 | recommendation 1s | seconds |
| Maximum TCP retransmission timeout | §8.4 | recommendation 120s | seconds |
| MTU (Maximum Transmission Unit) | §8 | range 1500 bytes | bytes |
| Maximum fragment length | §9.2 | range 512 bytes | bytes |
| Connection Keepalive "ping" min interval | §10.4 | range 50s | seconds |
| Connection Keepalive "pong" timeout | §10.4 | range 10s | seconds |
| SKI length | §12.2 | range 20 bytes (40 digit hexadecimal string) | bytes |
| PIN length | §12.5 | range 8-16 digit hexadecimal string | not printed |
| Maximum "auto_accept" time window | §12.3.1.1 | range ≤120s; recommendation 60s | seconds |
| "User trust level" necessary for general SHIP communication | §12.3.2 | range ≥8 | not printed |
| "User trust level" or "second factor trust level" necessary for commissioning | §12.3.2 | range ≥32 | not printed |
| CmiTimeout | §13.4 | range 10-30s; recommendation 30s | seconds |
| Wait-For-Ready-Timer initial | §13.4.4.1 | range 60-240s; recommendation 120s | seconds |
| Wait-For-Ready-Timer prolongation | §13.4.4.1 | range 60-240s; recommendation 120s | seconds |
| PIN entry penalty after the 3rd invalid attempt | §13.4.4.3 | range 10-15s; recommendation 15s | seconds |
| PIN entry penalty after the 6th invalid attempt | §13.4.4.3 | range 60-90s; recommendation 90s | seconds |

## Discovery

| DNS-SD item or TXT key | type | presence | meaning (own words) | clause |
| --- | --- | --- | --- | --- |
| service name | DNS-SD service | mandatory | Local discovery uses mDNS/DNS-SD and advertises the service name ship. | SHIP Specification 1.0.1 §7 |
| DNS-SD TTL | record lifetime | recommended | The DNS-SD record TTL should be 2 minutes. | SHIP Specification 1.0.1 §7 |
| service label | DNS-SD name | mandatory | The service label is underscore, the service name, a dot, and _tcp. | SHIP Specification 1.0.1 §7 |
| instance | DNS-SD instance | mandatory | A user-facing name of at most 63 UTF-8 bytes. On a collision the node chooses a new name. A parenthesized decimal should be appended, starting at (2). | SHIP Specification 1.0.1 §7 |
| host name | mDNS host | mandatory | Unique, at most 63 bytes, and should use the TXT identifier. | SHIP Specification 1.0.1 §7 |
| A and AAAA | address record | mandatory | A carries IPv4 and AAAA carries IPv6. | SHIP Specification 1.0.1 §7 |
| SRV | service location | mandatory | Carries the service name, the host name, and the port. No fixed port number is printed. | SHIP Specification 1.0.1 §7 |
| TXT record | TXT | mandatory | One TXT format, at most 400 bytes. Unknown keys are ignored. | SHIP Specification 1.0.1 §7 |
| txtvers | TXT key | mandatory, first key | Value 1. A missing key or any other value causes the TXT record to be discarded. | SHIP Specification 1.0.1 §7 Table 2 |
| id | TXT key | mandatory | Globally unique identifier, at most 63 bytes, separate from the instance name. | SHIP Specification 1.0.1 §7 Table 2 |
| path | TXT key | mandatory | WebSocket path, 1 to 32 UTF-8 bytes. The shortest value is a single slash. | SHIP Specification 1.0.1 §7 Table 2 |
| ski | TXT key | mandatory | Identifies the secp256r1 subject key identifier without a trial handshake. A 0x prefix is omitted. Table 2 also prints 40 byte and 160 bit, which conflicts with the 20-byte length. | SHIP Specification 1.0.1 §7 Table 2, §12.2 |
| brand | TXT key | optional | UTF-8, at most 32 bytes. | SHIP Specification 1.0.1 §7 Table 3 |
| type | TXT key | optional | UTF-8, at most 32 bytes. Not required for a conformant announcement. | SHIP Specification 1.0.1 §7 Table 3 |
| model | TXT key | optional | UTF-8, at most 32 bytes. | SHIP Specification 1.0.1 §7 Table 3 |
| further optional keys | TXT key | optional | Further optional keys are permitted inside the 400-byte TXT limit. | SHIP Specification 1.0.1 §7 |
| register | TXT key | mandatory | Boolean that states whether auto accept is active. Only auto accept changes it. Table 2 prints the runtime column Static, while the registration clause requires the flag to follow auto accept. | SHIP Specification 1.0.1 §5, §7 Table 2 |

## Transport

| layer | requirement (own words) | value | clause |
| --- | --- | --- | --- |
| TCP | SHIP communication uses TCP. | required | SHIP Specification 1.0.1 §8 |
| TCP | The server port is the port in the SRV record. No numeric port is printed. | no fixed port | SHIP Specification 1.0.1 §8 |
| TCP | The MTU stays at or below 1500 bytes. | 1500 bytes | SHIP Specification 1.0.1 §8 |
| TCP | Initial retransmission count. | recommendation 2 | SHIP Specification 1.0.1 §8.3 |
| TCP | Initial retransmission timeout. | recommendation 1 second | SHIP Specification 1.0.1 §8.4 |
| TCP | Maximum retransmission timeout. | recommendation 120 seconds | SHIP Specification 1.0.1 §8.4 |
| UDP | UDP is specified for mDNS discovery. A SHIP data path over UDP is not specified. | discovery only | SHIP Specification 1.0.1 §8 |
| TLS | TLS 1.2 is mandatory. | TLS 1.2 | SHIP Specification 1.0.1 §9 |
| TLS | Table 1 states the maximum fragment length. | 512 bytes | SHIP Specification 1.0.1 §9.2 Table 1 |
| TLS | When the fragment-length extension is used, the only offered length is 1024 bytes, and the outgoing plaintext length stays at or below that. | 1024 bytes | SHIP Specification 1.0.1 §9.2 |
| TLS | secp256r1 is required. brainpoolP256r1 and brainpoolP384r1 are permitted. Compression is forbidden. Server name indication is required. Renegotiation is not defined and is not implemented. | curves and handshake | SHIP Specification 1.0.1 §9, §9.7 |
| WebSocket | The opening handshake uses the version number 13, the subprotocol ship only, and no extensions. Data frames use the binary opcode. | subprotocol ship | SHIP Specification 1.0.1 §10 |
| WebSocket | The ping interval is not shorter than 50 seconds. The wait for pong is 10 seconds. | 50 seconds; 10 seconds | SHIP Specification 1.0.1 §10.4 |
| JSON | SHIP messages on the WebSocket use the JSON representation this revision defines for the message set. | JSON | SHIP Specification 1.0.1 §11 |

## Trust

Certificate and SKI rules are §12.1 and §12.2. The double-connection rule is §12.2.2. PIN assignment is §12.5. QR fields continue in §12.6.

| verification mode | trust level | clause |
| --- | --- | --- |
| auto accept | user trust 8 | SHIP Specification 1.0.1 §12.3 |
| user verify | user trust 32 | SHIP Specification 1.0.1 §12.3 |
| user input | user trust 64 | SHIP Specification 1.0.1 §12.3 |
| commissioning | user trust 32 to 96, depending on tool trustworthiness; no finer scale is printed | SHIP Specification 1.0.1 §12.3 |
| none | user trust 0 | SHIP Specification 1.0.1 §12.3 Table 10 |
| self-signed PKI | PKI trust 0 | SHIP Specification 1.0.1 §12.3 |
| PKI-signed | a value from 0 through 65535 set by node policy; no finer scale is printed | SHIP Specification 1.0.1 §12.3 |
| second factor, PIN | 16 or 32 in the mode table; the prose range is 16 to 32 | SHIP Specification 1.0.1 §12.3, §12.5 |
| PIN, first sender after factory default | second-factor trust 32 | SHIP Specification 1.0.1 §12.5 |
| PIN, every later sender | second-factor trust 16 | SHIP Specification 1.0.1 §12.5 |
| general communication | requires user trust of at least 8; below that the hello is aborted | SHIP Specification 1.0.1 §12.3.2, §13.4.4.1 |
| commissioning over SHIP | requires user trust of at least 32 or second-factor trust of at least 32 | SHIP Specification 1.0.1 §12.3.2 |
| SKI length | 20 bytes, 40 hexadecimal digits, in the parameter table and the SKI clause; the TXT value cell also prints 40 byte and 160 bit | SHIP Specification 1.0.1 §12.1, §12.2, §7 Table 2 |
| double connection | a second connection between the same two nodes is closed under the double-connection rule | SHIP Specification 1.0.1 §12.2.2 |
| PIN length | 8 to 16 hexadecimal digits | SHIP Specification 1.0.1 §12.5 |

## Connection states

| state | entered on | leaves on | timer | clause |
| --- | --- | --- | --- | --- |
| CMI_INIT_START | underlying connection is open | role-specific CMI outcome | CmiTimeout 10 to 30 seconds, recommendation 30 seconds | SHIP Specification 1.0.1 §13.4.3 |
| Connection data preparation | CMI completes | hello starts | none printed beyond CMI | SHIP Specification 1.0.1 §13.4.4 |
| hello pending or ready | hello exchange starts | hello ok, or abort and close | Wait-For-Ready initial and prolongation each 60 to 240 seconds, recommendation 120 seconds; waiting is in milliseconds and the T_hello constants are in seconds, with no conversion printed | SHIP Specification 1.0.1 §13.4.4.1 |
| protocol handshake | hello ok | PIN verification, or abort and close | none printed as a separate handshake timer | SHIP Specification 1.0.1 §13.4.4.2 |
| PIN verification | handshake selects a PIN check | data exchange under the enable rule, or close | penalty after the 3rd invalid attempt 10 to 15 seconds, recommendation 15 seconds; after the 6th, 60 to 90 seconds, recommendation 90 seconds | SHIP Specification 1.0.1 §13.4.4.3 |
| connection data exchange | PIN branch enables it | access methods and close may run beside it | none printed as a data-exchange timer | SHIP Specification 1.0.1 §13.4.5 |
| access methods | data exchange has been entered | identification completes or is refused | only after data exchange | SHIP Specification 1.0.1 §13.4.6 |
| connection termination | data exchange has been entered | connection closes | regular close of this edition | SHIP Specification 1.0.1 §13.4.7 |

## Messages

| message | field | type | presence | clause |
| --- | --- | --- | --- | --- |
| accessMethods | accessMethods.dns.uri | URI | SHIP V1.0.1: M in the table | SHIP Specification 1.0.1 §13.4.6.2, Table 24 |
| accessMethods | accessMethods.dns | parent | SHIP V1.0.1: O | SHIP Specification 1.0.1 §13.4.6.2, Table 24 |
| accessMethods | accessMethods.dnsSd_mDns | not stated; no children in this version | SHIP V1.0.1: O | SHIP Specification 1.0.1 §13.4.6.2, Table 24 |
| accessMethods | accessMethods.id | string (empty string is specified) | SHIP V1.0.1: M | SHIP Specification 1.0.1 §13.4.6.2, Table 24 |
| accessMethods | accessMethods | root | SHIP V1.0.1: M | SHIP Specification 1.0.1 §13.4.6.2, Table 24 |
| accessMethods | MessageType | octet; value %x01 | SHIP V1.0.1: fixed for this message | SHIP Specification 1.0.1 §13.4.6.2 |
| accessMethodsRequest | accessMethodsRequest | root; this version prints no children | SHIP V1.0.1: M | SHIP Specification 1.0.1 §13.4.6.2, Table 23 |
| accessMethodsRequest | MessageType | octet; value %x01 | SHIP V1.0.1: fixed for this message | SHIP Specification 1.0.1 §13.4.6.2 |
| CMI | CmiHead | octet | SHIP V1.0.1: analysed; remainder not analysed in this version | SHIP Specification 1.0.1 §13.4.3 |
| CMI | CmiRemainder | *OCTET | SHIP V1.0.1: not used for decisions in this version | SHIP Specification 1.0.1 §13.4.3 |
| CMI | MessageType | octet; value %x00 | SHIP V1.0.1: fixed for this message | SHIP Specification 1.0.1 §13.4.3 |
| connectionClose | connectionClose.maxTime | not in the sources | SHIP V1.0.1: O | SHIP Specification 1.0.1 §13.4.7.1, Table 25, §13.4.7.1.2 |
| connectionClose | connectionClose.phase | not in the sources | SHIP V1.0.1: M | SHIP Specification 1.0.1 §13.4.7.1, Table 25 |
| connectionClose | connectionClose.reason | not in the sources | SHIP V1.0.1: O | SHIP Specification 1.0.1 §13.4.7.1, Table 25, §13.4.7.1.1 |
| connectionClose | MessageType | octet; value %x03 | SHIP V1.0.1: fixed for this message | SHIP Specification 1.0.1 §13.4.7.1 |
| connectionHello | connectionHello.phase | not in the sources | SHIP V1.0.1: M | SHIP Specification 1.0.1 §13.4.4.1.1, Table 14 |
| connectionHello | connectionHello.prolongationRequest | not in the sources | SHIP V1.0.1: O | SHIP Specification 1.0.1 §13.4.4.1.1, Table 14, §13.4.4.1.3 |
| connectionHello | connectionHello.waiting | not in the sources | SHIP V1.0.1: O | SHIP Specification 1.0.1 §13.4.4.1.1, Table 14 |
| connectionHello | MessageType | octet; value %x01 | SHIP V1.0.1: fixed for this message | SHIP Specification 1.0.1 §13.4.4.1.1 |
| connectionPinError | connectionPinError.error | error number | SHIP V1.0.1: M | SHIP Specification 1.0.1 §13.4.4.3.2, Table 20, Table 21 |
| connectionPinError | MessageType | octet; value %x01 | SHIP V1.0.1: fixed for this message | SHIP Specification 1.0.1 §13.4.4.3.2 |
| connectionPinInput | connectionPinInput.pin | string of contiguous hexadecimal characters | SHIP V1.0.1: M | SHIP Specification 1.0.1 §13.4.4.3.2, Table 19 |
| connectionPinInput | MessageType | octet; value %x01 | SHIP V1.0.1: fixed for this message | SHIP Specification 1.0.1 §13.4.4.3.2, §13.4.4.3.3 |
| connectionPinState | connectionPinState.inputPermission | not in the sources | SHIP V1.0.1: O in the table; presence is constrained by pinState | SHIP Specification 1.0.1 §13.4.4.3.2, Table 18, §13.4.4.3.5.1 |
| connectionPinState | connectionPinState.pinState | not in the sources | SHIP V1.0.1: M | SHIP Specification 1.0.1 §13.4.4.3.2, Table 18, §13.4.4.3.5.1 |
| connectionPinState | MessageType | octet; value %x01 | SHIP V1.0.1: fixed for this message | SHIP Specification 1.0.1 §13.4.4.3.2 |
| data | data.extension.binary | binary | SHIP V1.0.1: O | SHIP Specification 1.0.1 §13.4.5.2.1, Table 22 |
| data | data.extension.extensionId | not in the sources | SHIP V1.0.1: O | SHIP Specification 1.0.1 §13.4.5.2.1, Table 22, §13.4.5.2.6 |
| data | data.extension.string | text | SHIP V1.0.1: O | SHIP Specification 1.0.1 §13.4.5.2.1, Table 22 |
| data | data.extension | parent for manufacturer-specific content | SHIP V1.0.1: O | SHIP Specification 1.0.1 §13.4.5.2.1, Table 22, §13.4.5.2.6 |
| data | data.header.protocolId | not in the sources | SHIP V1.0.1: M | SHIP Specification 1.0.1 §13.4.5.2.1, Table 22, §13.4.5.2.4, §14 |
| data | data.header | parent | SHIP V1.0.1: M | SHIP Specification 1.0.1 §13.4.5.2.1, Table 22 |
| data | data.payload | not stated; the agreed handshake format applies to the container | SHIP V1.0.1: M | SHIP Specification 1.0.1 §13.4.5.2.1, Table 22, §13.4.5.2.5 |
| data | MessageType | octet; value %x02 | SHIP V1.0.1: fixed for this message | SHIP Specification 1.0.1 §13.4.5.2.1 |
| messageProtocolHandshake | messageProtocolHandshake.formats.format | not in the sources | SHIP V1.0.1: M inside the list | SHIP Specification 1.0.1 §13.4.4.2.1 |
| messageProtocolHandshake | messageProtocolHandshake.formats | list | SHIP V1.0.1: M | SHIP Specification 1.0.1 §13.4.4.2.1, Table 15 |
| messageProtocolHandshake | messageProtocolHandshake.handshakeType | not in the sources | SHIP V1.0.1: M | SHIP Specification 1.0.1 §13.4.4.2.1, Table 15 |
| messageProtocolHandshake | messageProtocolHandshake.version.major | not in the sources | SHIP V1.0.1: M | SHIP Specification 1.0.1 §13.4.4.2.1, Table 15, §13.4.4.2.3 |
| messageProtocolHandshake | messageProtocolHandshake.version.minor | not in the sources | SHIP V1.0.1: M | SHIP Specification 1.0.1 §13.4.4.2.1, Table 15, §13.4.4.2.3 |
| messageProtocolHandshake | messageProtocolHandshake.version | parent | SHIP V1.0.1: M | SHIP Specification 1.0.1 §13.4.4.2.1, Table 15 |
| messageProtocolHandshake | MessageType | octet; value %x01 | SHIP V1.0.1: fixed for this message | SHIP Specification 1.0.1 §13.4.4.2.1 |
| messageProtocolHandshakeError | messageProtocolHandshakeError.error | error number | SHIP V1.0.1: M | SHIP Specification 1.0.1 §13.4.4.2.1, Table 16, Table 17 |
| messageProtocolHandshakeError | MessageType | octet; value %x01 | SHIP V1.0.1: fixed for this message | SHIP Specification 1.0.1 §13.4.4.2.1, §13.4.4.2.3 |


## Commands, limits and timing

| topic | statement | clause |
| --- | --- | --- |
| Table 1 parameter values | Parameter as printed: Initial TCP retransmission count; Chapter column: 8.3; Range column: empty; Recommendation column: 2 | clause not printed |
| Table 1 parameter values | Parameter as printed: Initial TCP retransmission timeout; Chapter column: 8.4; Range column: empty; Recommendation column: 1s | clause not printed |
| Table 1 parameter values | Parameter as printed: Maximum TCP retransmission timeout; Chapter column: 8.4; Range column: empty; Recommendation column: 120s | clause not printed |
| Table 1 parameter values | Parameter as printed: MTU (Maximum Transmission Unit); Chapter column: 8; Range column: 1500 bytes; Recommendation column: empty | clause not printed |
| Table 1 parameter values | Parameter as printed: Maximum fragment length; Chapter column: 9.2; Range column: 512 bytes; Recommendation column: empty | clause not printed |
| Table 1 parameter values | Parameter as printed: Connection Keepalive "ping" min interval; Chapter column: 10.4; Range column: 50s; Recommendation column: empty | clause not printed |
| Table 1 parameter values | Parameter as printed: Connection Keepalive "pong" timeout; Chapter column: 10.4; Range column: 10s; Recommendation column: empty | clause not printed |
| Table 1 parameter values | Parameter as printed: SKI length; Chapter column: 12.2; Range column: 20 bytes (40 digit hexadecimal string); Recommendation column: empty | clause not printed |
| Table 1 parameter values | Parameter as printed: PIN length; Chapter column: 12.5; Range column: 8-16 digit hexadecimal string; Recommendation column: empty | clause not printed |
| Table 1 parameter values | Parameter as printed: Maximum "auto_accept" time window; Chapter column: 12.3.1.1; Range column: ≤120s; Recommendation column: 60s | clause not printed |
| Table 1 parameter values | Parameter as printed: "User trust level" necessary for general SHIP communication; Chapter column: 12.3.2; Range column: ≥8; Recommendation column: empty | clause not printed |
| Table 1 parameter values | Parameter as printed: "User trust level" or "second factor trust level" necessary for commissioning; Chapter column: 12.3.2; Range column: ≥32; Recommendation column: empty | clause not printed |
| Table 1 parameter values | Parameter as printed: CmiTimeout; Chapter column: 13.4; Range column: 10-30s; Recommendation column: 30s | clause not printed |
| Table 1 parameter values | Parameter as printed: Wait-For-Ready-Timer initial; Chapter column: 13.4.4.1; Range column: 60-240s; Recommendation column: 120s | clause not printed |
| Table 1 parameter values | Parameter as printed: Wait-For-Ready-Timer prolongation; Chapter column: 13.4.4.1; Range column: 60-240s; Recommendation column: 120s | clause not printed |
| Table 1 parameter values | Parameter as printed: PIN entry penalty after the 3rd invalid attempt; Chapter column: 13.4.4.3; Range column: 10-15s; Recommendation column: 15s | clause not printed |
| Table 1 parameter values | Parameter as printed: PIN entry penalty after the 6th invalid attempt; Chapter column: 13.4.4.3; Range column: 60-90s; Recommendation column: 90s | clause not printed |
| Registration (§5) | The node SHALL look for nodes whose SKI it already trusts and connect to them. | clause not printed |
| Registration (§5) | If registration does not finish as in §5.1, the node SHALL keep retrying that SKI. | §5.1 |
| Registration (§5) | If the other local node aborts SME hello (procedure in §13.4.4.1), this node SHOULD NOT retry while the other node’s register flag is false. If that flag is true, a node that already holds the trusted SKI SHALL retry. | §13.4.4.1 |
| Registration (§5) | While the mode is active, the node SHALL set its own discovery register flag to true, and SHALL discover other nodes whose register flag is true. | clause not printed |
| Registration (§5) | If both sides use only auto accept, neither checks an SKI. The text says a man-in-the-middle cannot then be ruled out. Supporting at least one further verification mode is marked STRONGLY RECOMMENDED. | clause not printed |
| Registration (§5) | If more than one discovered node has register true, the node SHALL choose one by any means it finds appropriate, including other discovery data. | clause not printed |
| Registration (§5) | When auto accept is inactive, the node SHALL set its register flag to false and SHALL stop looking for nodes with register true. | clause not printed |
| Registration (§5) | Only auto accept changes the register flag. User verify, user input, and commissioning SHALL NOT change it. | clause not printed |
| Discovery, service name, port, TXT (§7) | Key: txtvers; Value rule on these pages: Version number. SHALL be 1.; Runtime column: Static; Required column: Mandatory | clause not printed |
| Discovery, service name, port, TXT (§7) | Key: id; Value rule on these pages: Identifier. Globally unique SHIP id, maximum 63 bytes.; Runtime column: Static; Required column: Mandatory | clause not printed |
| Discovery, service name, port, TXT (§7) | Key: path; Value rule on these pages: String carrying the wss path.; Runtime column: Static; Required column: Mandatory | clause not printed |
| Discovery, service name, port, TXT (§7) | Key: ski; Value rule on these pages: Printed value cell: 40 byte hexadecimal digits representing the 160 bit SKI value. See the conflict note below.; Runtime column: Static; Required column: Mandatory | clause not printed |
| Discovery, service name, port, TXT (§7) | Key: register; Value rule on these pages: Boolean. Indicates whether auto accept is active. (also); Runtime column: Static; Required column: Mandatory | clause not printed |
| TCP (§8) | A node MUST support at least 1 simultaneously active connection. | clause not printed |
| TCP (§8) | If the local node is limited to 1: it SHALL provide a listening TCP server, and SHALL close that server port only when it wants to connect out as a TCP client. After the client connection it SHALL close the client connection as soon as possible and listen on the server port again. | clause not printed |
| TCP (§8) | If the limit x is greater than 1: the node SHALL reserve one connection for the TCP server port, so at most x-1 connections are TCP clients. | clause not printed |
| TCP (§8) | If the limit x is greater than 1: the node SHALL also reserve one connection for TCP client connections, so at most x-1 connections are TCP server connections. | clause not printed |
| TCP (§8) | At the connection limit the TCP server port MAY be shut. It SHALL be opened again as soon as possible. Below the limit, a TCP server port SHALL stay open. | clause not printed |
| TCP (§8) | Before a local node opens TCP to another local node, the peer SHOULD be seen as online. | clause not printed |
| TCP (§8) | If the peer’s mDNS announcement TTL is not valid, the peer SHOULD be treated as offline. When the announcement is refreshed and the TTL is valid, the peer SHALL be treated as online again. | clause not printed |
| TCP (§8) | A local node MAY send ICMP echo requests. | clause not printed |
| TCP (§8) | Some environments block ICMP echo. If no echo reply arrives but mDNS announcements from that peer do arrive, the node SHALL treat the peer as ICMP-blocked, SHALL NOT use ICMP echo as an offline signal, and SHOULD use only the mDNS TTL as the offline signal. | clause not printed |
| TCP (§8) | The text notes that an attempt toward an offline peer can occupy about 10 seconds (§8.3), which matters for a node with few connections. | §8.3 |
| TCP (§8) | The client sends an initial SYN. An accepting server answers with SYN ACK, as in RFC 793. | clause not printed |
| TCP (§8) | A SYN to a closed port: the SHIP server SHALL answer with RST, citing RFC 793 chapter 3.4 / page 36. The RST SHOULD NOT be blocked or filtered on the SHIP node, the text’s example being a firewall. | clause not printed |
| TCP (§8) | The RST lets the client abort at once when the port is closed. | clause not printed |
| TCP (§8) | The initial SYN SHOULD be retransmitted twice if no response (the text’s examples are ACK or RST) arrives. With the §8.4 recommended timeouts, the stated maximum establishment time is 1 + 3 + 6 = 10 seconds. | §8.4 |
| TCP (§8) | A node SHOULD keep a retransmission timer as RFC 6298 defines it. RTT is send-time until the matching ACK. A packet that was retransmitted MUST NOT be used for that measurement. | clause not printed |
| TCP (§8) | The text says RFC 6298 recommends a minimum RTO of 1 second, and also says a SHIP node MAY use a smaller minimum. | clause not printed |
| TCP (§8) | For the initial SYN, RTO SHOULD start at 1 second. A node MAY raise that value on a lossy network. | clause not printed |
| TCP (§8) | The text says that after the first retransmission RFC 6298 requires the RTO to be at least the historical 3 seconds, then exponential back-off doubles the RTO on each further retransmission. A SHIP node SHOULD cap the RTO at 120 seconds. | clause not printed |
| TLS (§9) | TLS_ECDHE_ECDSA_WITH_AES_128_CBC_SHA256 (RFC 5289) MUST be supported. | clause not printed |
| TLS (§9) | OPTIONAL: TLS_ECDHE_ECDSA_WITH_AES_128_CCM_8 | clause not printed |
| TLS (§9) | OPTIONAL: TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256 | clause not printed |
| TLS (§9) | Authentication is ECDSA. Key exchange is ECDHE, with perfect forward secrecy. The text gives lower computation cost than RSA at similar security as the reason for ECC. | clause not printed |
| TLS (§9) | Curve secp256r1 MUST be used. Other curves are not allowed at this time. The text says other curves might be added later. | clause not printed |
| TLS (§9) | The Maximum Fragment Length Negotiation extension (RFC 6066) SHOULD be supported. | clause not printed |
| TLS (§9) | If it is used, it SHALL support only a length of 1024 bytes. | clause not printed |
| TLS (§9) | Outgoing TLSPlaintext.length SHALL NOT exceed 1024 bytes even when the extension is not supported. | clause not printed |
| TLS (§9) | Table 1’s range cell for this parameter is 512 bytes. Conflict: see Open points. | Table 1 |
| TLS (§9) | SNI MUST be supported, as WebSocket requires in RFC 6455. The client requirement is repeated in §10.1. | §10.1 |
| TLS (§9) | A local SHIP node SHALL ignore the SNI value. | clause not printed |
| TLS (§9) | A web-server SHIP node MAY use SNI when it has a fixed DNS host name. | clause not printed |
| TLS (§9) | For a local connection the server name SHALL equal the local server’s mDNS host name. | clause not printed |
| TLS (§9) | For a web-server connection the server name SHALL be the web server’s DNS hostname. | clause not printed |
| TLS (§9) | The text, citing RFC 6066, says the SNI name is an ASCII byte string with no trailing dot, so a trailing dot on an mDNS name should not be sent. A SHIP server SHOULD ignore a final trailing dot if a client sent one by mistake. | clause not printed |
| WebSocket (§10) | A valid SHIP request-URI MUST use the wss scheme whenever TLS is used, so the URI starts with wss://. | clause not printed |
| WebSocket (§10) | This specification states no assumption about host, port, or resource name. Those come from discovery (§7). A connecting node SHALL present them exactly as discovered. | §7 |
| WebSocket (§10) | The origin property MAY be absent. | clause not printed |
| WebSocket (§10) | Sec-WebSocket-Version MUST be present with the fixed value 13. Earlier draft versions are not allowed. | clause not printed |
| WebSocket (§10) | Sec-WebSocket-Protocol MUST include the value ship and MUST NOT include any other subprotocol name. This is how a node detects another SHIP node early. | clause not printed |
| WebSocket (§10) | No WebSocket extension is specified. The request MUST NOT contain Sec-WebSocket-Extensions. | clause not printed |
| WebSocket (§10) | Every data frame (non-control) MUST be type 0x2 (binary). | clause not printed |
| WebSocket (§10) | A received data frame of type 0x1 MUST end the connection with status code 1003 (unacceptable data). | clause not printed |
| WebSocket (§10) | Opcode in 0x3–0x7 or 0xB–0xF: the connection MUST be closed. Close status: 1002, name protocol error. | clause not printed |
| WebSocket (§10) | Reserved bits MUST be 0. Reserved opcodes MUST NOT be used. | clause not printed |
| WebSocket (§10) | The clause restates RFC 6455 on three points: clients handle fragmentation; a control frame may sit inside one fragmented message; pieces of two different messages must not be mixed. Lack of SHIP multiplexing is called unimportant here. No SHIP message-size cap is set in this clause. The clause only remarks that the messages are thought to be short. | clause not printed |
| WebSocket (§10) | The WebSocket SHALL stay up whenever local resources allow, to cut delay. | clause not printed |
| WebSocket (§10) | Wide-area setup is described as usually dial-out only. A local firewall or NAT is the stated cause. The socket then has to remain up if remote traffic is to arrive. No extra timer is defined for that case. | clause not printed |
| WebSocket (§10) | The node SHALL use ping and pong control frames to check the transport. | clause not printed |
| WebSocket (§10) | A node MUST NOT send ping messages on one connection at an interval smaller than 50 seconds. | clause not printed |
| WebSocket (§10) | The usual wait for pong after ping SHALL be 10 seconds. | clause not printed |
| WebSocket (§10) | Table 1 places 50s and 10s in the range column for these two parameters, chapter 10.4. | Table 1 |
| JSON representation (§11) | XSD types as printed: xs:boolean; JSON type as printed: Boolean | clause not printed |
| JSON representation (§11) | XSD types as printed: xs:double, xs:byte, xs:unsignedByte, xs:short, xs:unsignedShort, xs:integer, xs:unsignedInt, xs:nonNegativeInteger, xs:unsignedLong; JSON type as printed: Number | clause not printed |
| JSON representation (§11) | XSD types as printed: xs:dateTime, xs:duration, xs:time; JSON type as printed: String | clause not printed |
| JSON representation (§11) | XSD types as printed: xs:language, xs:string; JSON type as printed: String | clause not printed |
| JSON representation (§11) | XSD types as printed: xs:hexBinary; JSON type as printed: String | clause not printed |
| JSON representation (§11) | XSD types as printed: xs:anyType; JSON type as printed: Results in corresponding types | clause not printed |
| JSON representation (§11) | XSD types as printed: xs:simpleType; JSON type as printed: See §11.4.4 | §11.4.4 |
| JSON representation (§11) | XSD types as printed: xs:complexType; JSON type as printed: See §11.4.5 | §11.4.5 |
| JSON representation (§11) | minOccurs and maxOccurs set how often a field may or must appear. | clause not printed |
| JSON representation (§11) | A minOccurs of 0 marks an optional field. | clause not printed |
| JSON representation (§11) | If minOccurs is omitted it is implicitly 1, so the field is mandatory. | clause not printed |
| JSON representation (§11) | If maxOccurs is greater than 1, the element becomes a JSON array of that type. maxOccurs is the array’s maximum length. unbounded means no upper limit. | clause not printed |
| JSON representation (§11) | If maxOccurs is omitted it is implicitly 1, so no JSON array is produced; the JSON type is used directly. | clause not printed |
| JSON representation (§11) | If both are 0, the element is ignored. | clause not printed |
| JSON representation (§11) | Compositor: xs:sequence; in xs:complexType: Array; in xs:sequence: +; in xs:choice: +; in xs:all: Not allowed | clause not printed |
| JSON representation (§11) | Compositor: xs:choice; in xs:complexType: Array; in xs:sequence: +; in xs:choice: +; in xs:all: Not allowed | clause not printed |
| JSON representation (§11) | Compositor: xs:all; in xs:complexType: Object; in xs:sequence: Not allowed; in xs:choice: Not allowed; in xs:all: + | clause not printed |
| JSON representation (§11) | Compositor: None; in xs:complexType: Array; in xs:sequence: -; in xs:choice: -; in xs:all: - | clause not printed |
| Certificates (§12.1) | A node MUST have a certificate. Whether it is client or server, it MUST present a certificate in the TLS handshake for mutual authentication. | clause not printed |
| Certificates (§12.1) | A self-signed certificate or a PKI-based certificate MUST be used. | clause not printed |
| Certificates (§12.1) | The certificate MUST contain the node-specific public key. | clause not printed |
| Certificates (§12.1) | A public/private pair is limited to a single certificate (SHALL NOT be reused for a second one). | clause not printed |
| Certificates (§12.1) | A node certificate is limited to a single SHIP node (SHALL NOT be shared). | clause not printed |
| Certificates (§12.1) | No mandatory PKI is specified. | clause not printed |
| Certificates (§12.1) | If the node does not know the other node’s PKI, that PKI certificate is treated like a self-signed certificate. Interoperability does not depend on one particular PKI. | clause not printed |
| Certificates (§12.1) | A web server MAY supply a revocation list, which the node MAY keep. With a synchronized clock, a certificate’s validity MAY be checked. Other checks MAY be used. Extra evaluation is called manufacturer-specific for now. | clause not printed |
| Certificates (§12.1) | The node MUST at least verify the certificate’s public key by one of the four registration modes in §12.3.1. Any other certificate check is optional or manufacturer-specific and SHALL NOT affect ordinary SHIP authentication and communication. The text includes lifetime checks, PKI checks, and other certificate checks in that statement. | §12.3.1 |
| Certificates (§12.1) | Optional or manufacturer checks may fail. If the public key itself was authenticated, communication SHOULD still be allowed. A PKI certificate that fails those checks SHOULD be treated as self-signed: PKI trust is absent, but user trust MAY still exist when the public key is trusted. The same treatment applies when lifetime cannot be checked for lack of a synchronized clock. The user MAY be told why an optional check failed. | clause not printed |
| Certificates (§12.1) | Where a certificate expires, the manufacturer SHOULD supply an update path for it. | clause not printed |
| Certificates (§12.1) | The user MAY replace the certificate, the public key, the SKI, and the private key together. Printed routes for that change: the node's own UI, and a commissioning tool. Factory reset SHOULD put back the original certificate, private key, SKI, and public key, especially when that SKI is printed on a label. | clause not printed |
| Certificates (§12.1) | Certificate CN is outside this specification. Received CN values SHOULD be ignored. | clause not printed |
| Certificates (§12.1) | A web-server node is usually not a member of the private network and then cannot act as a client. | clause not printed |
| Certificates (§12.1) | It SHOULD have a PKI-based certificate. | clause not printed |
| Certificates (§12.1) | A node that wants to talk to it SHOULD hold the matching CA-certificate. | clause not printed |
| Certificates (§12.1) | A CA-certificate has no confidentiality requirement. The node MUST make sure the stored CA-certificate cannot be manipulated. | clause not printed |
| Public key and SKI (§12.2) | Label on the node. | clause not printed |
| Public key and SKI (§12.2) | User interface of the node, the text’s example being a display. | clause not printed |
| Public key and SKI (§12.2) | A local user communication interface, the text’s example being NFC. Access MUST be easy for the user. | clause not printed |
| Public key and SKI (§12.2) | A cloud user interface. The key must be reached via the serial number or some other distinctive property of that node. | clause not printed |
| Public key and SKI (§12.2) | Each verified public key of another node SHALL be stored with the trust level of the mode that verified it. | clause not printed |
| Public key and SKI (§12.2) | A public key that was not verified MAY be stored as an unknown public key. | clause not printed |
| Public key and SKI (§12.2) | The trusted key and its trust level SHOULD be stored persistently, so the user is not asked again. | clause not printed |
| Public key and SKI (§12.2) | An unknown public key SHALL be given user trust level 0. | clause not printed |
| Public key and SKI (§12.2) | The node SHOULD let the user remove particular trusted public keys at any time. | clause not printed |
| Public key and SKI (§12.2) | The node MUST let the user delete all stored partner public keys, the text’s example being a factory reset. | clause not printed |
| Verification modes and trust (§12.3) | Mode: Auto accept (Table 10: auto accept); User trust level: 8 | Table 10 |
| Verification modes and trust (§12.3) | Mode: User verify (Table 10: user verified); User trust level: 32 | Table 10 |
| Verification modes and trust (§12.3) | Mode: Commissioning (Table 10: commissioned); User trust level: 32–96, depending on how trustworthy the commissioning tool is | Table 10 |
| Verification modes and trust (§12.3) | Mode: User input (Table 10: user input); User trust level: 64 | Table 10 |
| Verification modes and trust (§12.3) | Mode: Table 10 also lists none; User trust level: 0 | Table 10 |
| Verification modes and trust (§12.3) | The text says this mode should be implemented only by very simple nodes with no user interface, and calls it the least secure mode. | clause not printed |
| Verification modes and trust (§12.3) | On the user trigger (push button is the printed example) the node SHALL start a window. Inside that window, an unknown public key seen during registration MUST be accepted on its own. | clause not printed |
| Verification modes and trust (§12.3) | The window takes a single unknown key (SHALL). Auto accept SHALL then switch off at once. | clause not printed |
| Verification modes and trust (§12.3) | Because the unknown key is not checked, the text warns of man-in-the-middle risk. The window SHALL be kept as short as usability allows, and MUST be less than or equal to 2 minutes. The text says a shorter window still does not remove that risk. | clause not printed |
| Verification modes and trust (§12.3) | Table 1: range ≤120s, recommended value 60s, under the printed name auto_accept, chapter 12.3.1.1. | Table 1 |
| Verification modes and trust (§12.3) | SHOULD be implemented on a node with a suitable display or other user communication interface. | clause not printed |
| Verification modes and trust (§12.3) | The node MUST tell the user when an unknown SKI appears in local mDNS discovery or in a TLS handshake. That notice MUST include the SKI. | clause not printed |
| Verification modes and trust (§12.3) | The same mode can be applied to a key already stored, either to raise user trust or to discard the key. | clause not printed |
| Verification modes and trust (§12.3) | SHOULD be implemented on a node that can be connected to a suitable commissioning tool. | clause not printed |
| Verification modes and trust (§12.3) | The resulting trust level depends on the trustworthiness of that tool. | clause not printed |
| Verification modes and trust (§12.3) | SKI values received from the tool SHALL be stored persistently together with the tool’s user-trust level, and SHALL be used to recognize matching public keys. The node SHALL also look for nodes it already knows with a matching key and adjust the trust level. | clause not printed |
| Verification modes and trust (§12.3) | The tool MAY also deliver a revocation list or update the node’s key material. | clause not printed |
| Verification modes and trust (§12.3) | Manufacturers may use their own commissioning solution. For business-to-business use and for the user, the text says an interoperable commissioning function should be used, on a trustworthy channel, with SHIP named as the example. Over SHIP that function may be reached by auto accept plus a PIN, or by user verify, user input, or commissioning. | clause not printed |
| Verification modes and trust (§12.3) | User consent is required, and the user SHALL take part, because this mode creates user trust. | clause not printed |
| Verification modes and trust (§12.3) | SHOULD be implemented on a node with a suitable out-of-band input, the text’s example being a user interface. | clause not printed |
| Verification modes and trust (§12.3) | SKI values entered on the node SHALL be stored persistently with the user-input trust level, and used to recognize matching public keys. The node SHALL also update trust for nodes it already knows when the key matches. | clause not printed |
| Verification modes and trust (§12.3) | PKI verification: self-signed; PKI trust level: 0 | clause not printed |
| Verification modes and trust (§12.3) | PKI verification: signed by PKI; PKI trust level: a value from 0 through 65535, set by node policy and by trust in that PKI | clause not printed |
| Verification modes and trust (§12.3) | Second factor: none; Level: 0 | clause not printed |
| Verification modes and trust (§12.3) | Second factor: PIN; Level: 16 or 32. The table says 32 is reserved for the first PIN transmitter. See §12.5. | §12.5 |
| Named exchanges that are not specified on these pages | SME hello | clause not printed |
| Named exchanges that are not specified on these pages | SME Connection Mode Initialization | clause not printed |
| Named exchanges that are not specified on these pages | SME Connection Data Preparation | clause not printed |
| Named exchanges that are not specified on these pages | SME protocol handshake | clause not printed |
| Named exchanges that are not specified on these pages | optional PIN verification | clause not printed |
| Named exchanges that are not specified on these pages | SME data exchange | clause not printed |
| Named exchanges that are not specified on these pages | connection termination (§13.4.7) | §13.4.7 |
| QR-code fields that finish on these pages (§12.6) | TYPE, optional, may follow BRAND. The first 5 bytes are the UTF-8 string TYPE:. The following bytes are a UTF-8 type string and must not contain;. The last byte is UTF-8;. §12.6. | §12.6 |
| QR-code fields that finish on these pages (§12.6) | MODEL, optional, may follow TYPE. The first 6 bytes are the UTF-8 string MODEL:. The following bytes are a UTF-8 model string and must not contain;. The last byte is UTF-8;. §12.6. | §12.6 |
| QR-code fields that finish on these pages (§12.6) | An example of a SKI-and-PIN payload is printed at. An example that also includes ID, BRAND, TYPE, and MODEL is printed at. The second example's field order is the SHIP prefix, then SKI, PIN, ID, BRAND, TYPE, MODEL. | clause not printed |
| QR-code fields that finish on these pages (§12.6) | draws a QR Code Model 2 symbol at ECC low and 0.33 mm per module, carrying SKI and PIN. Drawn size 33 × 0.33 mm = 10.89 mm, quiet zone excluded. | clause not printed |
| QR-code fields that finish on these pages (§12.6) |: same QR parameters with all values. Drawn size 47 × 0.33 mm = 15.51 mm, quiet zone excluded. Another payload can differ in size because ID, BRAND, TYPE, and MODEL vary in length. | clause not printed |
| Message model (§13.2) | server and client in this chapter are connection-technology roles, not functional roles. Details in §13.4.1. | §13.4.1 |
| Message model (§13.2) | A SHIP message has a definition. Description forms cited: XSD, binary structure, table. A message can also have a process for its use. | clause not printed |
| Message model (§13.2) | A message is parts. A part has a representation, called a wire format. Named representations: JSON-UTF8, JSON-UTF16, binary, and mixed or message-dependent. Which ones are allowed depends on the scope or the variant. For one variant, every allowed representation has a lossless conversion to the others. A later version may add representations. | clause not printed |
| Message model (§13.2) | The message wire format is the composition of the parts and must make every representation determinable. Unless a clause says otherwise, "SHIP message" means the wire format. In that format a message has a limited size, a start, and an end. No numeric size limit is printed. | clause not printed |
| Message model (§13.2) | Each wire format has a format descriptor, usable in the handshake to agree the later wire format. | clause not printed |
| Message model (§13.2) | A variant is fixed either by the transmission context or by a variant identifier in the message. Named examples: the CMI message (§13.4.3) and connectionHello (§13.4.4.1). Each variant belongs to one type in Table 13: init, control, data, end. | §13.4.3, §13.4.4.1, Table 13 |
| Message model (§13.2) | RFU regions can be specified later only by the specification authority, and must not be used for a manufacturer extension. A later release may assign a former RFU region even if a manufacturer has used it. | clause not printed |
| Message model (§13.2) | By default a well-defined parent allows only its known children. Where a clause states default structure extensibility, a later specification may add children after the last known child, as immediate children only, not before or between known children, and not as manufacturer children. The recursive form applies the same rule down through children that are themselves parents. | clause not printed |
| Stack (§13.3) | In ISO-OSI terms, SME-AP is SME-I's access point for services. It delivers received SHIP messages upward and accepts SHIP messages aimed at another SME-AP. The application sends and receives through SME-AP. | clause not printed |
| Stack (§13.3) | What SME-I speaks on the wire is the SHIP message. SME-I uses an access point on a SHIP Transport instance. Detail is §13.4. | §13.4 |
| Stack (§13.3) | A later version may add a SHIP Stream beside SME-I. Not defined here. | clause not printed |
| Stack (§13.3) | SHIP Transport extracts SHIP messages from received data for SME-I, and transmits data for messages taken from SME-I. | clause not printed |
| Stack (§13.3) | In this revision, transport uses the WebSocket message frame, depending on the security method in use. Exactly one wire-format SHIP message is carried in exactly one WebSocket message. The FIN bit is set on the last fragment of that SHIP message, and only there. | clause not printed |
| Stack (§13.3) | A remark says a later version may use something other than WebSocket, and that CMI is the prepared extension point. | clause not printed |
| SME connection (§13.4.1) | Opening the underlying connection is outside this specification. It assumes a lower layer or an internal mechanism supplies a connection that is open or closed. | clause not printed |
| SME connection (§13.4.1) | The SME connection follows that open or closed state. Each SME instance also has further states that change with SHIP messages. | clause not printed |
| SME connection (§13.4.1) | Roles: see Actors. | clause not printed |
| CMI (§13.4.3) | CMI_STATE_CLIENT_SEND: send CMI whose MessageValue is 0, then enter CMI_STATE_CLIENT_WAIT at once. | clause not printed |
| CMI (§13.4.3) | CMI_STATE_CLIENT_WAIT: wait for the server's CMI message. | clause not printed |
| CMI (§13.4.3) | CMI_STATE_CLIENT_EVALUATE: if MessageType is not 0, close at once. If CmiHead is decimal 0, enter Connection data preparation. If CmiHead is decimal greater than 0, close at once. | clause not printed |
| CMI (§13.4.3) | CMI_STATE_SERVER_WAIT: wait for the client's CMI message. | clause not printed |
| CMI (§13.4.3) | CMI_STATE_SERVER_EVALUATE: if MessageType is not 0, send CMI whose MessageValue is 0, then close. If CmiHead is decimal 0, send CMI whose MessageValue is 0 and enter Connection data preparation. If CmiHead is decimal greater than 0, send CMI whose MessageValue is 0, then close. | clause not printed |
| Hello (§13.4.4.1) | READY only if the partner is already trusted. The user will go on once the partner also reports ready, and will wait only a limited time. The partner can ask to extend that time. | clause not printed |
| Hello (§13.4.4.1) | PENDING means this side still withholds permission to continue. It still waits a limited time for the partner's READY, and the partner can ask to extend that time. Before the wait ends it must either move to READY and tell the partner, or ask the partner for more time, or abort if it decides not to trust the partner. | clause not printed |
| Hello (§13.4.4.1) | HELLO_OK is reached only under the conditions in the following subsections. | clause not printed |
| Hello (§13.4.4.1) | Wait-For-Ready-Timer. Default T_hello_init. The partner must send READY, or a prolongation request, before it expires. | clause not printed |
| Hello (§13.4.4.1) | Send-Prolongation-Request-Timer. Local timer so a prolongation request is sent before the partner's Wait-For-Ready-Timer expires. | clause not printed |
| Hello (§13.4.4.1) | Prolongation-Request-Reply-Timer. Detects a missing answer to a prolongation request. | clause not printed |
| Hello (§13.4.4.1) | T_hello_init: a duration chosen in the closed interval that starts at 60 seconds and ends at 240 seconds. The choice stays constant during a connection. It should also stay constant across connections. | clause not printed |
| Hello (§13.4.4.1) | T_hello_inc equals T_hello_init. | clause not printed |
| Hello (§13.4.4.1) | T_hello_prolong_thr_inc: 30 seconds. | clause not printed |
| Hello (§13.4.4.1) | T_hello_prolong_waiting_gap: 15 seconds. | clause not printed |
| Hello (§13.4.4.1) | T_hello_prolong_min: 1 second. | clause not printed |
| Hello (§13.4.4.1) | phase ready: enter HELLO_OK. | clause not printed |
| Hello (§13.4.4.1) | phase pending and no prolongationRequest: ignore. | clause not printed |
| Hello (§13.4.4.1) | phase pending and prolongationRequest true: run the incoming-prolongation procedure, then send a Hello update. | clause not printed |
| Hello (§13.4.4.1) | phase aborted: abort procedure. | clause not printed |
| Hello (§13.4.4.1) | Any non-Hello: abort procedure. | clause not printed |
| Hello (§13.4.4.1) | phase ready and no waiting: abort. | clause not printed |
| Hello (§13.4.4.1) | phase ready and waiting present: stop Wait-For-Ready-Timer and Prolongation-Request-Reply-Timer. When waiting meets or exceeds T_hello_prolong_thr_inc, set Send-Prolongation-Request-Timer to the calculated value and start it; otherwise deactivate it. | clause not printed |
| Hello (§13.4.4.1) | phase pending, waiting present, no prolongationRequest: stop Prolongation-Request-Reply-Timer, then the same threshold rule for Send-Prolongation-Request-Timer. | clause not printed |
| Hello (§13.4.4.1) | phase pending, no waiting, prolongationRequest true: incoming-prolongation procedure, then a Hello update. | clause not printed |
| Hello (§13.4.4.1) | phase aborted: abort. | clause not printed |
| Hello (§13.4.4.1) | Any other shape: abort. | clause not printed |
| Hello (§13.4.4.1) | A non-Hello: abort. | clause not printed |
| Hello (§13.4.4.1) | A final decision not to trust the partner: abort. | clause not printed |
| Hello (§13.4.4.1) | Wait-For-Ready-Timer: abort. | clause not printed |
| Hello (§13.4.4.1) | Send-Prolongation-Request-Timer: send a Hello with phase pending, prolongationRequest true, and no other child. Set Prolongation-Request-Reply-Timer to the partner's last waiting. If no waiting has been received, use 1.1 times the current Wait-For-Ready-Timer. Start Prolongation-Request-Reply-Timer and return to the previous state. | clause not printed |
| Hello (§13.4.4.1) | Prolongation-Request-Reply-Timer: abort. | clause not printed |
| PIN verification (§13.4.4.3) | Fewer than three invalid PINs: no penalty. | clause not printed |
| PIN verification (§13.4.4.3) | From three to five: enter SME_PIN_STATE_CHECK_BUSY_WAIT for at least 10 seconds. The period should go beyond 15 seconds only for a higher security need. | clause not printed |
| PIN verification (§13.4.4.3) | More than five: enter SME_PIN_STATE_CHECK_BUSY_WAIT for at least 60 seconds. The period should go beyond 90 seconds only for a higher security need. | clause not printed |
| PIN verification (§13.4.4.3) | required: the node must receive its own valid PIN. Connection data exchange is not reached until a received PIN checks successfully. A note says this value should be used only in some cases, that a node cannot know whether the peer can enter a PIN, and that a manufacturer who sets required should also provide a SHIP commissioning tool that can enter a PIN. | clause not printed |
| PIN verification (§13.4.4.3) | optional: the node's own PIN is not required, and data are limited. Connection data exchange can start without the PIN, restricted to data that do not need the PIN. A valid PIN then opens all data. The partner is not forced to send a PIN. The node can keep pinState optional, speak in Connection data exchange with the reduced set, and still listen for a later PIN. | clause not printed |
| PIN verification (§13.4.4.3) | pinOk: the valid PIN was already received; data are unrestricted; Connection data exchange can start at once. | clause not printed |
| PIN verification (§13.4.4.3) | none: the node has no PIN; data are unrestricted; Connection data exchange can start at once. | clause not printed |
| PIN verification (§13.4.4.3) | busy: a connectionPinInput is not accepted for checking now. | clause not printed |
| PIN verification (§13.4.4.3) | ok: a connectionPinInput is accepted for checking now. | clause not printed |
| PIN verification (§13.4.4.3) | If pinState is pinOk or none, inputPermission must be absent, and a PIN input is not accepted. | clause not printed |
| PIN verification (§13.4.4.3) | If pinState is required or optional, inputPermission must be present. It must be busy while a penalty toward that partner is in force, and ok otherwise. | clause not printed |
| PIN verification (§13.4.4.3) | Send the current PIN requirement. | clause not printed |
| PIN verification (§13.4.4.3) | If pinState is required: Connection data exchange stays disabled. Enter SME_PIN_STATE_CHECK_BUSY_WAIT when inputPermission is busy, otherwise SME_PIN_STATE_CHECK_LISTEN. | clause not printed |
| PIN verification (§13.4.4.3) | If pinState is optional: run the procedure that enables Connection data exchange, then the same busy or listen choice. | clause not printed |
| PIN verification (§13.4.4.3) | If pinState is pinOk or none: run that enable procedure and enter SME_PIN_STATE_CHECK_OK. | clause not printed |
| PIN verification (§13.4.4.3) | A received PIN that matches: set pinState to pinOk, remove inputPermission, send the PIN requirement, run the enable procedure, enter SME_PIN_STATE_CHECK_OK. | clause not printed |
| PIN verification (§13.4.4.3) | A received PIN that does not match: enter SME_PIN_STATE_CHECK_ERROR. | clause not printed |
| PIN verification (§13.4.4.3) | Close if a received message breaks the §13.4.4.3.5.1 child rules. | §13.4.4.3.5.1 |
| PIN verification (§13.4.4.3) | A PIN error for wrong PIN means a PIN input sent earlier was wrong. The user should wait for a new PIN-state message. | clause not printed |
| PIN verification (§13.4.4.3) | Every PIN-state message whose pinState is not required causes the enable procedure. | clause not printed |
| PIN verification (§13.4.4.3) | inputPermission busy: the partner is not ready to check a PIN input. The node ought to pause until the partner signals that readiness. The node can still send a PIN input before that. A remark says sending early is a way to obtain a state confirmation after a penalty that has run unexpectedly long. | clause not printed |
| PIN verification (§13.4.4.3) | inputPermission ok: the printed sentence says the partner is ready to evaluate a PIN-state message. The node also reads pinState and decides whether to send a PIN input. | clause not printed |
| PIN verification (§13.4.4.3) | pinState required or optional: also read inputPermission before choosing to transmit a PIN input. | clause not printed |
| PIN verification (§13.4.4.3) | pinState pinOk or none: enter SME_PIN_STATE_ASK_OK. | clause not printed |
| PIN verification (§13.4.4.3) | Decision when pinState is required: either send a PIN input, which requires inputPermission ok and a PIN on hand, or close. | clause not printed |
| PIN verification (§13.4.4.3) | Decision when pinState is optional: enter SME_PIN_STATE_ASK_RESTRICTED_OK if unrestricted data are not needed, or send a PIN input under the same two conditions, or close. | clause not printed |
| PIN verification (§13.4.4.3) | After a PIN input was sent in response to required or optional, the wait for a fresh PIN-state message has a floor of 30 seconds and a ceiling of 120 seconds, then the user either stays in this state or closes. This wait is separate from any choice to send the PIN again. It is about the lack of a PIN-state update, in particular inputPermission busy or ok. | clause not printed |
| PIN verification (§13.4.4.3) | This state stays active, and the user keeps listening, unless a rule says otherwise. | clause not printed |
| Connection data exchange (§13.4.5) | The base specifies forward compatibility: a later version can add content, and a base implementation accepts that content and processes at least the parts the base already defines. It may skip unknown parts. | clause not printed |
| Connection data exchange (§13.4.5) | Each compatible successor also specifies forward compatibility, and those rules must not break the base rules. | clause not printed |
| Connection data exchange (§13.4.5) | A version has zero or one immediate successor, and zero or one immediate predecessor. | clause not printed |
| Connection data exchange (§13.4.5) | An implementation of a given version accepts content from a compatible predecessor and processes that content as a whole. | clause not printed |
| Connection termination (§13.4.7) | unspecific is used when no other value fits better. A remark says this is typically a temporary disconnect, with examples of a node that can keep only one connection, or a reboot for a firmware update, and that a later connection is likely. | clause not printed |
| Connection termination (§13.4.7) | removedConnection means the peer was dropped from the node's known-device list or its accepted-device list. A remark says a later connection can still happen, and the device is then treated as new or unknown. | clause not printed |
| Connection termination (§13.4.7) | Send phase announce, maxTime as the millisecond duration from the send time until DEV-A will close at the latest even with no confirmation, and reason set. | clause not printed |
| Connection termination (§13.4.7) | Close at the latest when that maxTime ends, even with no confirmation. | clause not printed |
| Connection termination (§13.4.7) | If DEV-B's confirmation arrives before maxTime ends, close at once. | clause not printed |
| Connection termination (§13.4.7) | Get ready to halt the data-exchange state ahead of the announced maxTime. When that halt finishes inside the limit and the socket remains up, send phase confirm with no other child, then close. | clause not printed |
| Connection termination (§13.4.7) | If the confirmation is not sent in time, treat the connection as closed when the received maxTime ends. | clause not printed |

## Open points

| point | what is printed | clause |
| --- | --- | --- |
| maximum fragment length | Table 1 prints 512 bytes. §9.2 prints 1024 bytes. Both stay. Neither is selected. | SHIP Specification 1.0.1 §9.2 Table 1 |
| SKI length | The parameter table and §12.2 print 20 bytes and 40 hexadecimal digits. The TXT value cell prints 40 byte and 160 bit. Both stay. | SHIP Specification 1.0.1 §12.2, §7 Table 2 |
| TCP or UDP port number | No numeric port is printed. The server port is the SRV port. | SHIP Specification 1.0.1 §7, §8 |
| retry period | No retry period is printed. | SHIP Specification 1.0.1 §5 |
| TLS idle time | No TLS idle time is printed. | SHIP Specification 1.0.1 §9 |
| SKI integer encoding | The hexadecimal digit form is printed. An integer encoding is not. | SHIP Specification 1.0.1 §12.2 |
| commissioning trust scale | The range 32 to 96 is printed. No finer picking rule is printed. | SHIP Specification 1.0.1 §12.3 |
| PKI trust scale | The range 0 through 65535 is printed. No finer picking rule is printed. | SHIP Specification 1.0.1 §12.3 |
| hello unit conversion | waiting is in milliseconds. The T_hello constants are in seconds. No conversion is printed. | SHIP Specification 1.0.1 §13.4.4.1 |
| message size | A limited size is named. No numeric maximum is printed. | SHIP Specification 1.0.1 §13 |
| register runtime column | Table 2 prints Static. §5 requires the flag to change with auto accept. Both are printed. | SHIP Specification 1.0.1 §5, §7 Table 2 |
| TLS maximum fragment length, SHIP 1.0.1 and SHIP 1.1.0. Table 1 range cell is 512 bytes. §9.2 says the fragment-length extension, when used, offers only 1024 bytes, and outgoing TLSPlaintext.length SHALL NOT exceed 1024 bytes. Both editions print both numbers. Table 1 and §9.2; Table 1 §4.2 and §9.2. | Table 1, §9.2, §4.2 | clause not printed |
| SHIP 1.1.0 auto accept together with a PIN. §12.3.1 item 2 sets user trust 8 and a second-factor range 16–32. Table 10 prints user trust 32 for that row (§12.3.2). These clauses do not pick one user-trust integer. SHIP 1.0.1’s mode table assigns auto accept user trust 8 and does not print that extra user-trust row; its second-factor PIN cell is 16 or 32 in Table 12 and 16-32 in the §12.3.2 paragraph. | §12.3.1, Table 10, §12.3.2, Table 12 | clause not printed |
| SHIP 1.0.1 SKI length. Table 1 and §12.2 say 20 bytes and 40 hexadecimal digits. Table 2’s value cell says “40 byte hexadecimal digits” and also “160 bit”. These clauses do not choose a reading. | Table 1, §12.2, Table 2 | clause not printed |
| General-communication trust gate is user trust at least 8 in both SHIP editions. SHIP 1.0.1 says that below 8, hello is aborted, and points the abort procedure at §13.4.4.1. SHIP 1.1.0 says that below 8, communication SHALL be aborted (§12.3.2). The abort target is not the same sentence. | §13.4.4.1, §12.3.2 | clause not printed |
| Trusted-node cross-reference. SHIP 1.0.1 points chapter 12.2.2, and the heading of §12.2.2 on those pages is the double-connection rule. SHIP 1.1.0 points §12.2.3 (§3), and on those pages §12.2.3 is the double-connection close. Verification modes are §12.3 in both editions. | §12.2.2, §12.2.3, §3, §12.3 | clause not printed |
| Clause numbers for the same late SHIP phase differ by edition. SHIP 1.0.1 places connection termination in §13.4.7. SHIP 1.1.0 places key-material messages in §13.4.7 and regular close in §13.4.8. | §13.4.7, §13.4.8 | clause not printed |
