---
canonical_source: "Project-Helianthus/helianthus-docs-eebus:protocols/ship-pairing-service-1.0.0.md"
owner_domain: "protocols"
license: "CC0-1.0"
publication_status: "publishable"
claim_status: "evidence-backed"
source_class: "vendor_public"
evidence_ids: "EV-20260711-001"
hypothesis_status: "publishable"
falsifier: "A row states a pairing input, algorithm, or field the named clause does not state, or fills the octet encoding or the chapter 9 conversion."
---

# SHIP Pairing Service 1.0.0

Roles, steps, DNS-SD keys, the request digest, and QR fields of this specification. The two unresolved encodings below stay unresolved.

## Roles

| role | does | clause |
| --- | --- | --- |
| devA | A SHIP node that receives and evaluates a shippairing request in order to trust the SHIP device named in that request, devZ (§4.1). | §4.1 |
| devA | In the installation example, devA is the user’s device. The examples named are an energy management system, a charging station, a heat pump, or similar (§1). Those examples are not a closed list of permitted device types. | §1 |
| devA | devA is not the sender of a shippairing request aimed at devZ (§4.1). | §4.1 |
| devA | devA holds devA-secret (§6.2). While receive-and-evaluate is activated, devA listens and searches for shippairing requests (§4.2; §9). | §6.2, §4.2, §9 |
| devA | After it accepts an addCu-request, devA trusts the SHIP node identified by trustId and both evaluates incoming SHIP attempts from devZ and initiates a SHIP connection to devZ (§4.2). | §4.2 |
| devA | devA trusts at most one current devZ from this service (§10.3; §11.4). | §10.3, §11.4 |
| devA | draws devA as the party that listens for shippairing and processes addCu-requests, then stops that processing. | clause not printed |
| devZ | A SHIP node configured by an administrator to trust devA and to send a shippairing request that carries what devA needs in order to trust devZ (§4.1). | §4.1 |
| devZ | In the installation example, devZ is the control unit of the metering-point operator (§1). The addCu note says “Cu” points at a control unit, or a similar device such as a smart meter gateway with control-unit-like behaviour, configured by people other than the devA user (§5.4). That note is informative. It does not limit type=addCu to one product class. | §1, §5.4 |
| devZ | A request originating at devA is not something devZ accepts under this document (§4.1). | §4.1 |
| devZ | Before it announces, devZ already trusts devA for SHIP in both directions and is responsible for establishing the SHIP connection (§4.2). | §4.2 |
| devZ | devZ creates, announces, and deletes its own shippairing instances and answers queries about them (§5.3). | §5.3 |
| devZ | draws devZ receiving configuration, announcing an authenticated shippairing service, and later stopping that service. | clause not printed |
| Administrator of devZ | Collects devA’s SHIP ID, the fingerprint of devA’s certificate, and devA-secret (§4.1). labels the scanned QR payload as SKI, FP, SHIP ID, secret, and an ellipsis. | §4.1 |
| Administrator of devZ | Loads SHIP trust toward devA into devZ (that SHIP ID, and the certificate whose fingerprint matches) and directs devZ to build the shippairing request (§4.2). | §4.2 |
| Administrator of devZ | If that administrator removes trust in devA while the instance for devA is still announced, devZ deletes the instance at once (§4.2). | §4.2 |
| Administrator of devZ | A long gap in SHIP traffic between devZ and devA is this administrator’s problem to handle. devZ is not required to start the service again by itself (§4.5). | §4.5 |
| User of devA | Optional manual actions at devA: return to factory defaults; remove devZ’s pairing from devA’s user interface; switch addCu-request processing back on from that interface (§4.3). | §4.3 |
| User of devA | May change devA-secret. The document says that change is permissive and should be avoided during an ongoing process (§6.2). | §6.2 |
| User of devA | May already have trusted devZ by a classic SHIP method before a shippairing request arrives (§10.4). Removing that trust reactivates this process, in the informative trust-store section (§10.4). | §10.4 |

## Steps

| step | does | clause |
| --- | --- | --- |

## DNS-SD records and TXT keys

| key | type | presence | meaning | clause |
| --- | --- | --- | --- | --- |
| txtvers | UTF-8 string | M, Static, active instance | version of the TXT format; SHALL be the first key; 1 | Table 1, §5.4, §9 |
| parType | UTF-8 string | M, Static | kind of authentication parameter; fpSha256 (SHA-256 certificate fingerprint). This version has no other authentication parameter | Table 1, §8, §9 |
| forId | UTF-8 string, type SHIP_ID, not empty | M, Static | devA SHIP ID; a valid SHIP ID. The pattern is not defined here | Table 1, §5.4, §6.1, §9 |
| forPar | UTF-8 string | M, Static | SHA-256 fingerprint of devA’s certificate; [0-9A-F]{64} (256-bit value, uppercase hex) | Table 1, §5.4, §6.2, §9 |
| trustId | UTF-8 string, type SHIP_ID, not empty | M, Static | devZ SHIP ID; a valid SHIP ID. The pattern is not defined here | Table 1, §5.4, §6.1, §4.2 |
| trustPar | UTF-8 string | M, Static | SHA-256 fingerprint of devZ’s certificate; [0-9A-F]{64} | Table 1, §6.2, §10.2 |
| trustCurve | UTF-8 string | M, Static | curve of devZ’s certificate public key; secp256r1, brainpoolP256r1, or brainpoolP384r1. The two brainpool names are marked [SHIP]1.1.0 | Table 1, §5.4, §6.2 |
| type | UTF-8 string | M, Static | command; addCu (this version’s only command) | Table 1, §3, §5.4, §9 |
| trustNonce | UTF-8 string | M, Static | devZ-nonce; [0-9A-F]{32} (128-bit value, uppercase hex); integer range in the timing section | Table 1, §5.4, §6.2, §7.3 |
| alg | UTF-8 string | M, Static | digest algorithm; hmacSha256 only, in this version | Table 1, §7.2, §9 |
| digest | UTF-8 string | M, Static | HMAC result; [0-9A-F]{64} | Table 1, §7.5, §9 |
| keys not in Table 1 | — | not M | —; ignored by devA; devZ does not add a key that carries devA-secret | §5.4 |
| K | binary concatenation of the two values’ octets | required for the digest | devA-secret then devZ-nonce; each input is a 128-bit integer; K is temporary and is not placed in the TXT record | §7.2, §7.3 |
| M | UTF-8 string; each entry is name=value and entries are separated by; a trailing; follows alg | required for the digest | fixed key order: txtvers, parType, forId, forPar, trustId, trustPar, trustCurve, type, trustNonce, alg; values use the same encoding as the TXT record; order is fixed; entries are not added or removed | §7.4 |
| HMAC result | HMAC output, then uppercase hex in digest | required | algorithm HMAC-SHA256, written HMAC with key K and message M; hex form matches [0-9A-F]{64} | §7.2, §7.5 |
| entry { alg, digest } | pair, or unset | SHALL | index from 1 upward; 10 or more slots | §9, §11.2 |
| next | index | SHALL, persistent | index where the next pair would be stored; 1 through the last index; wraps to 1 | §11.2, §11.3 |
| current | derived index | defined, not separately stored | next minus 1, or the last index when that result is below 1; — | §11.4 |

## Request and digest

Chapters 7 to 9 name the digest inputs and the algorithm. K is the concatenation of the devA-secret octets and the devZ-nonce octets. M is the fixed key order of the TXT values. The algorithm is HMAC-SHA256.

| input or algorithm | what is named | clause |
| --- | --- | --- |

## QR code fields

| field | meaning | clause |
| --- | --- | --- |
| FPH256:<64 uppercase hex> | certificate on secp256r1; 64 digits | Table 2, §12 |
| BFPH256:<64 uppercase hex> | certificate on brainpoolP256r1; 64 digits | Table 2, §12 |
| B2FPH256:<64 uppercase hex> | certificate on brainpoolP384r1; 64 digits | Table 2, §12 |
| SKI | curve secp256r1; — | Table 2, §12 |
| BSKI | curve brainpoolP256r1; defined since SHIP 1.1.0; — | Table 2, §12 |
| B2SKI | curve brainpoolP384r1; defined since SHIP 1.1.0; — | Table 2, §12 |
| SPSEC:<devA-secret> | devA-secret; 32 uppercase hex digits | §12, §6.2 |

## Commands, limits and timing

| topic | statement | clause |
| --- | --- | --- |
| TXT invalidity and secrecy (§5.4) | Unknown keys are ignored, not by themselves invalid. | clause not printed |
| TXT invalidity and secrecy (§5.4) | The record is invalid when any mandatory key is absent, or when a specified value breaks the permitted pattern. | clause not printed |
| TXT invalidity and secrecy (§5.4) | The record is invalid unless txtvers occupies the first position. | clause not printed |
| TXT invalidity and secrecy (§5.4) | The record is invalid when trustCurve names a curve devA cannot use on a SHIP connection. | clause not printed |
| TXT invalidity and secrecy (§5.4) | devZ does not use devA-secret to form trustNonce. | clause not printed |
| TXT invalidity and secrecy (§5.4) | devZ does not put devA-secret, or a part of it, into any other TXT key. | clause not printed |
| TXT invalidity and secrecy (§5.4) | devZ does not add an extra key that carries devA-secret in any way. | clause not printed |
| TXT invalidity and secrecy (§5.4) | The text says no known algorithm extracts devA-secret from digest faster than brute force. That is a statement of knowledge, not a numeric bound. | clause not printed |
| Correct a static value (§5.5) | Option 1, preferred: announce the corrected request under a different instance name. | clause not printed |
| Correct a static value (§5.5) | Option 2: wait at least 1.5*TTL_old, where TTL_old is that deleted request’s initial TTL, then create a new request, which may reuse the instance name. | clause not printed |
| Trust update (chapter 10) | A SHIP implementation already stores trust persistently. That store is called the trust store. | clause not printed |
| Trust update (chapter 10) | This service does not define or require a second trust store. The ring buffer is not a trust store. It exists to stop replay. | clause not printed |
| Trust update (chapter 10) | The SHIP implementation stores trust that came from a shippairing request in the same way as classic SHIP trust. | clause not printed |
| Trust update (chapter 10) | If the user already trusted that SHIP ID, a later successful request can add the fingerprint and the fact that the node was added by an addCu request, and devA updates the ring buffer. | clause not printed |
| Trust update (chapter 10) | SHIP communication may already succeed before the request is accepted. Receive-and-evaluate turns off only after acceptance (§10.4, pointing at §4.2). | §10.4, §4.2 |
| Trust update (chapter 10) | If the user removes trust in devZ, the process starts again. Removing this device from the trust store is what triggers addCu processing to start again. | clause not printed |
| Trust update (chapter 10) | The SHIP ID is not covered by the cryptographic algorithms. Stored SKI, fingerprint, and similar parameters are checked on every SHIP connection attempt. A failed check aborts the communication (lowercase “need”). | clause not printed |
| Trust update (chapter 10) | The SHIP ID is the unique identification for the life of the node and is treated as the primary identifier in the trust store. | clause not printed |
| addCu processing states (§4.3) | Condition: for at least 15 minutes devA, while it stays powered and running, cannot exchange SHIP messages with paired devZ1. | clause not printed |
| addCu processing states (§4.3) | If that condition holds, the text says exactly one of the next two cases occurs. | clause not printed |
| addCu processing states (§4.3) | A new valid addCu-request for devZ2 is received and evaluated successfully: untrust devZ1, trust devZ2, stop addCu processing. devZ2 becomes the current devZ. | clause not printed |
| addCu processing states (§4.3) | Otherwise, if a SHIP connection with devZ1 is possible again: stop addCu processing. Trust in devZ1 stays. | clause not printed |
| addCu processing states (§4.3) | Factory-default reset. | clause not printed |
| addCu processing states (§4.3) | The user deletes the pairing with devZ in the user interface. | clause not printed |
| addCu processing states (§4.3) | The user turns addCu processing on again in the user interface. For this last case, the two automatic outcomes above also apply. | clause not printed |
| Ring buffer state (§11) | Name digest-ring-buffer. At least 10 entries. Indexes are contiguous from 1 up, and the last index is at least 10. | clause not printed |
| Ring buffer state (§11) | An entry is unset, or it holds { alg, digest } for a received and verified digest. | clause not printed |
| Ring buffer state (§11) | next is the index that the next pair would occupy. | clause not printed |
| Ring buffer state (§11) | Both the buffer and next are stored persistently, including after each insert. | clause not printed |
| Ring buffer state (§11) | Insert: write the pair at next, add 1 to next, and if the result exceeds the last index set next to 1. | clause not printed |
| Ring buffer state (§11) | current = next − 1, or the last index if that result is less than 1. An unset entry at current means no devZ is trusted from a shippairing request. Otherwise that entry is the one that belongs to the currently trusted devZ. | clause not printed |
| Timers and numeric limits | Item: DNS-SD TTL; Value: 2 minutes; Who: devZ; Rule: SHOULD; Locator: §5.3 | §5.3 |
| Timers and numeric limits | Item: Announcement after SHIP is up; Value: 15 minutes without interruption; Who: devZ; Rule: SHOULD keep announcing from SME state connection data exchange until this elapses, then SHALL delete the instance for that devA; Locator: §4.2 | §4.2 |
| Timers and numeric limits | Item: Timer restart; Value: 0 seconds at the start of the next SHIP connection with devA; Who: devZ; Rule: A break before 15 minutes, including a break caused by reboot of devZ, starts the 15 minutes over. Until the successful 15 minutes, devZ should keep announcing; Locator: §4.2 | §4.2 |
| Timers and numeric limits | Item: Early stop of the announcement; Value: no minimum duration; Who: devZ; Rule: devZ can stop announcing before 15 uninterrupted minutes (lowercase “can”). The text says this lowers the chance that devA receives the instance; Locator: §4.2 | §4.2 |
| Timers and numeric limits | Item: After the required delete; Value: no re-announce; Who: devZ; Rule: That instance is not announced again after reboot or after another connection break; Locator: §4.2 | §4.2 |
| Timers and numeric limits | Item: Delete on untrust; Value: immediately; Who: devZ; Rule: SHALL, if the administrator removes trust in devA while the instance is still up; Locator: §4.2 | §4.2 |
| Timers and numeric limits | Item: Corrected instance, same name allowed; Value: at least 1.5*TTL_old after goodbye; Who: devZ; Rule: SHALL wait when option 2 reuses a name. Option 1 uses a new name and states no wait; Locator: §5.5 | §5.5 |
| Timers and numeric limits | Item: Reactivate addCu processing; Value: at least 15 minutes without SHIP message exchange with devZ1; Who: devA; Rule: Mandatory automatic condition. devA runs continuously through that period; Locator: §4.3 | §4.3 |
| Timers and numeric limits | Item: devA-secret; Value: integer in [0, 2^128−1]; Who: devA; Rule: SHALL. Superscript 128 on. Readable form: 32 hexadecimal digits; Locator: §6.2 | §6.2 |
| Timers and numeric limits | Item: trustNonce; Value: integer in [0, 2^128−1]; Who: devZ; Rule: SHALL. Superscript 128 on. TXT form: 32 uppercase hexadecimal digits; Locator: §6.2; Table 1 | §6.2, Table 1 |
| Timers and numeric limits | Item: Fingerprint and digest width; Value: 256-bit, 64 uppercase hex digits; Who: both; Rule: SHA-256 of the DER certificate; HMAC-SHA256 output; Locator: §5.4; §6.2 | §5.4, §6.2 |
| Timers and numeric limits | Item: Ring buffer length; Value: 10 or more entries; last index ≥ 10; Who: devA; Rule: SHALL; Locator: §11.2 | §11.2 |
| Timers and numeric limits | Item: Parallel evaluations; Value: 1 at a time; Who: devA; Rule: SHALL NOT run two or more at once; Locator: §9 | §9 |
| Timers and numeric limits | Item: Parallel requests to one devA; Value: not allowed; Who: devZ; Rule: SHALL NOT; Locator: §4.4 | §4.4 |
| Timers and numeric limits | Item: Requests to different receivers; Value: allowed together; Who: devZ; Rule: permissive, with distinct instance names; Locator: §4.4 | §4.4 |
| Curves and certificates (§6.2) | SHIP 1.0.x: only secp256r1. | clause not printed |
| Curves and certificates (§6.2) | SHIP 1.1.x: secp256r1, brainpoolP256r1, and brainpoolP384r1. | clause not printed |
| Annex C (informative background, not a protocol timer) | In SHIP, an SKI is SHA-1 of a public key. | clause not printed |
| Annex C (informative background, not a protocol timer) | SHA-1 second-preimage resistance, as of the time of writing, is 160 bits for short messages, written as 2^160 operations. The exponent 160 is a superscript. | clause not printed |
| Annex C (informative background, not a protocol timer) | secp256r1 has almost 2^256 points. | clause not printed |
| Annex C (informative background, not a protocol timer) | The printed ratio is 2^256 / 2^160 = 2^96. | clause not printed |
| Annex C (informative background, not a protocol timer) | The remaining count is printed as 2^256 − 2^96, described as closer to 2^256 than to 2^255. | clause not printed |
| Annex C (informative background, not a protocol timer) | The text says an adversary should expect more than 2^160 operations to find a matching private and public key for a wanted SKI. | clause not printed |

## Open points

The octet encoding of devA-secret and devZ-nonce when building K is not stated. The conversion named in chapter 9 is not stated. Both stay unresolved.

| point | clause |
| --- | --- |
| [SHIP], [SRIP], [FIPS 180-4], [N-SP800-90A], [RFC 2104], [RFC 2119], [RFC 6234], [RFC 6762], [RFC 6763], [SrvNames], [X.690], and ISO/IEC 18004:2015 are cited. None of those documents is reproduced here (§2; §3). | [SHIP], [SRIP], [N-SP800-90A], §2, §3 |
| The SHIP ID pattern is not defined here. §6.1 points at [SHIP] for identity and at [SRIP] for a recommended pattern. Table 1 only says type SHIP_ID. | §6.1, [SHIP], [SRIP], Table 1 |
| SME state connection data exchange is a trigger and is not defined here (§4.2). | §4.2 |
| Which certificate fields [SHIP] requires, and the full curve rules inside each SHIP version, are not copied here (§6.2). | [SHIP], §6.2 |
| Goodbye encoding is deferred to [RFC 6762] (§5.4). | §5.4 |
| Mandatory QR parts other than chapter 12’s extensions stay in [SHIP] and [SRIP] (§12). The Annex A.1 example string adds further QR parts that this document does not define. | [SHIP], [SRIP], §12, Annex A.1 |
| How the integer devA-secret and the integer devZ-nonce become octets before concatenation is not stated. Width and byte order are not stated. The readable forms are 32 hexadecimal digits (§6.2; §7.3). Annex A shows one worked concatenation and is an example (§A.3). | §6.2, §7.3, Annex A |
| Evaluation step 3 says the computed digest must be identical to the converted TXT digest (§9). What conversion is applied is not defined in that sentence. §7.5 says both sides use the hexadecimal HMAC (§7.5). | §9, §7.5 |
| <Delimiter> is any separating character (§5.2). No single character is required. An example on uses one particular character. | §5.2 |
| “Any unused port number” is not given a range or a reservation procedure (§5.3). | §5.3 |
| “Practically unique”, “sufficient entropy”, “best effort”, “almost fulfils”, and “generally accepted manner” have no numeric test (§6.2; §6.3). How far a practical generator may depart from the ideal is explicitly not prescribed (§6.3). | §6.2, §6.3 |
| No message tells devZ that devA rejected a TXT record, a digest, a curve, or a replay (§5.3; §9). | §5.3, §9 |
| The ring buffer stores { alg, digest } only (§11.2). §11.4 still says the entry at current belongs to the currently trusted devZ. It does not say that trustId is stored there. | §11.2, §11.4 |
| The initial value of next, and whether every entry starts unset, are not stated (§11.2). | §11.2 |
| Whether receive-and-evaluate is on before the first accepted request is not stated (§4.2; §4.3). | §4.2, §4.3 |
| Factory reset and deleting the pairing are optional manual procedures (§4.3). The document does not say whether either clears devA-secret, the ring buffer, or the trust store. The sentence that applies the automatic follow-up cases is printed immediately after the user-interface reactivation item. It does not clearly attach to factory reset or to deletion. | §4.3 |
| §10.4 says removing trust reactivates the process, and the section is informative. §4.3 makes the manual procedures optional. The document does not say which section wins if they are read apart. | §10.4, §4.3 |
| “SHIP message exchange”, used for the 15-minute reactivation test and in §4.5, is not defined here (§4.3; §4.5). | §4.5, §4.3 |
| §4.2 prints “dev A” with a space. Neighbouring sentences use devA. This page treats that as the same role. | §4.2 |
| §5.3 prints “SHALL not” with a lowercase “not”. Other prohibitions use SHALL NOT. | §5.3 |
| §6.2 prints shipPairing once. Other uses on these pages are shippairing. | §6.2 |
| §4.1 does not specify a request that is sent by a tool or device other than devZ. | §4.1 |
| §4.5 leaves devZ’s reaction to a long absence of SHIP message exchange unspecified, and recommends against an automatic new request. | §4.5 |
| A later version is expected to add request types beyond addCu (§4.2; §10.3). Those types are not defined here. | §4.2, §10.3 |
| The word Dynamic is defined and no Table 1 key uses it (§5.4). The legend defines O and no Table 1 key is O. | Table 1, §5.4 |
| includes SKI in the scanned QR list. Note 1 says that SKI is not used by this service’s process (§4.1). Chapter 12 and §C.3 still require SKI material on the QR code (§12;). The figure has no separate line numbers; labels are taken from the drawing. | §4.1, §12 |
| is a picture of the Annex A example QR code. It adds no separate normative field. | Annex A |
| The printed clauses of this document are the ones cited above. There is no later clause of this document. Clauses that point outside the document are those citations. | clause not printed |
| No heartbeat, failsafe, polling period, subscription maximum, or SPINE bind rule is printed. | clause not printed |
