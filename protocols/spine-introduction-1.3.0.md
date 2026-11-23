---
canonical_source: "Project-Helianthus/helianthus-docs-eebus:protocols/spine-introduction-1.3.0.md"
owner_domain: "protocols"
license: "CC0-1.0"
publication_status: "publishable"
claim_status: "evidence-backed"
source_class: "vendor_public"
evidence_ids: "EV-20260711-001"
hypothesis_status: "publishable"
falsifier: "A row states an actor, scenario, or limit the introduction clause does not state."
---

# SPINE Introduction 1.3.0

The introduction names the three-level model, the feature roles, and the command vocabulary. It defines no heartbeat behaviour of its own. Where a later specification states a different number, both stay on the page that cites each clause.

## Document

| statement | clause |
| --- | --- |
| Cover title: EEBus SPINE Technical Report, subject Introduction. Version on the cover: 1.3.0. Running header: EEBus SPINE TR - Introduction, version V1.3.0. | clause not printed |
| Printed kind: Technical Report (header abbreviation TR). No status word (draft, final, or similar) is printed on the title page. | clause not printed |
| Publication line: Cologne, 2023-08-31. Publisher named on the cover: EEBus Initiative e.V. | clause not printed |
| Cover note: the EEBus concept came out of E-Energy. | clause not printed |
| Body pages carry a 2023 copyright line for EEBus Initiative e.V. and Page n of 23. | clause not printed |
| The document has 23 pages. Contents run from §1 through §3.10. The last section is §3.10 | §1, §3.10 |
| Page 2 is the terms-of-use page (general information, liability, copyright and exploitation). Those legal sentences are not specification rules and are not copied here. | clause not printed |
| Postal addresses, telephone, fax, email, web address, and the register line on the cover are omitted. | clause not printed |
| This report gives an overview of SPINE concepts. It states that the concepts are not fully described here, and that other SPINE documents hold the chapter-level detail. A later reminder says the same: the report does not cover every SPINE concept. §1.2, §2.3 | §1.2, §2.3 |
| Recommended path through this report: follow its chapters in order. §1.2 | §1.2 |
| Recommended path across documents, for a reader who goes through each document from front to back: this report, then [ProtocolSpecification], then [ResourceSpecification]. §1.2 | §1.2 |
| The report says its own sequence of chapter pointers is a faster way into SPINE than reading those other documents from the front. §1.2 | §1.2 |
| It also says some terms appear before they are explained, because of how large the concepts are. §1.2 | §1.2 |
| SPINE is printed in full as Smart Premises Interoperable Neutral-message Exchange. §1.1 | §1.1 |
| The data model is specified with XML Schema Definition files, extension .xsd. Graphical views of those schemas appear often in the SPINE documents. Reading those graphics is explained in [ResourceSpecification], section titled Graphical representation. §1.2 | §1.2 |
| The application-layer interface is a message protocol. A message is split into a header and a payload. Protocol aspects, including that header and payload structure, and some payload pieces, are in [ProtocolSpecification]. Most of the payload, including the whole SPINE resource model, is in [ResourceSpecification]. §1.2 | §1.2 |
| §1, what SPINE is, at overview level. §1.1, the name and role of SPINE. §1.2, how to start. §1.3, references. §1.3.1, SPINE documents from EEBus. §1.3.2, other EEBus documents. §1.3.3, websites. | §1, §1.1, §1.2, §1.3, §1.3.1, §1.3.2, §1.3.3 |
| §2, first steps. §2.1, general concepts. §2.2, the device model: devices, entities, features. §2.3, classes, functions, and elements. §2.4, where a function sits in the datagram and in the device. | §2, §2.1, §2.2, §2.3, §2.4 |
| §3, detailed information. §3.1, header and payload. §3.2, message classifiers. §3.3, standard class compared with complex class. §3.4, role concept. §3.5, acknowledgement and error messages. §3.6, binding and subscription. §3.7, device discovery. §3.8, addressing schema. §3.9, destination list. §3.10, partial data. | §3, §3.1, §3.2, §3.3, §3.4, §3.5, §3.6, §3.7, §3.8, §3.9, §3.10 |
| SPINE is a neutral layer for joining different communications technologies into a smart-home or smart-grid system. §1.1 | §1.1 |
| Messages and procedures sit only on ISO-OSI layer 7, the application layer. Transport is outside SPINE. The same limit is repeated later: nothing under layer 7 is specified, so the model and the protocol can sit on many technologies that carry any payload in both directions. §1.1, §2.1 | §1.1, §2.1 |
| A technology that can exchange arbitrary data in both directions can carry SPINE, with the printed hedge “more or less directly”. Named examples: SHIP, expanded as SmartHome IP, also from EEBus Initiative e.V., and Thread. §1.1 | §1.1 |
| Each communications technology still needs a mapping. For some technologies that mapping is very simple; SHIP is the case named for that. The mapping covers the data points and some protocol definitions. §1.1 | §1.1 |
| Mappings differ because existing technologies differ in capability. A mapping may leave some SPINE functions unsupported. §1.1 | §1.1 |
| The design is modular so that other technologies can be brought in. One SPINE application can afterwards be tied to a single mapping component, or to several. §1.1 | §1.1 |
| Figure 3 is the specification stack. The prose above it says the lowest part, in the ISO-OSI sense, is [SHIPSpecification]: a transport for SPINE messages, and other transports exist. Above that sits [ProtocolSpecification], which includes functional commissioning. Named pieces of that commissioning: binding, subscription, and detailed discovery. Resources are [ResourceSpecification], and they come from use-case requirements and from user stories. The drawing itself is not recorded. §1.2 | §1.2 |
| EEBus working groups build use cases in modules as well. One High-Level Use Case specifies one functionality. Its contents, as listed: a description; scenarios; diagrams, with sequence diagrams named; example XML. Authors use the Generic Use Case Toolbox, which supplies message blocks that can be reused. The report says the High-Level Use Cases hold what is needed both to implement and to test. The toolbox only makes the first draft easier. Figure 4 is that picture; its body is not recorded. §1.2 | §1.2 |
| The model includes metadata. Printed examples: the kind of device, and the constraints of the functionality. The stated result is that a node (an energy manager is the example) can communicate with devices that were not known while that node was being developed, and can still operate those devices usefully. Energy management is named as a setting where this matters. §1.2 | §1.2 |
| The report contrasts this modular specification with modelling every piece of information as one data point, and states the benefit as being able to extend the model for new market needs while interoperability and compatibility stay intact. §1.2 | §1.2 |
| The covered work is control, and also monitoring, for smart appliances. Named kinds, each as printed: White Goods; HVAC systems; batteries; electrical vehicles. Named sectors, each as printed: one sector is smart energy; one sector is smart home & building; one sector is connected devices; one sector is E-Mobility. §1.1 | §1.1 |
| AAL, expanded in the text as ambient assisted living, and home entertainment, are outside the present focus. The same passage says some use cases from those domains can still be realised with the data model that exists now. The model is described as still evolving, with further domains to be added. §1.1 | §1.1 |

## Actors

| statement | clause |
| --- | --- |
| nothing further is printed in this section | clause not printed |

## Scenarios

| statement | clause |
| --- | --- |
| A High-Level Use Case is said to contain scenarios, a description, diagrams, and example XML. No scenario of any use case is written out here. §1.2 | §1.2 |
| The letters M, R, and O are not used. Lower-case shall, may, and should, and one capital MAY, occur in the places collected in section 6. This report has no keyword glossary and does not cite a meaning for those verbs. | clause not printed |
| SPINE functions can be combined differently for different use cases. §2.1 | §2.1 |
| Some scenarios need a relation between functions. That is the lead-in to references and to complex classes. §3.3, | §3.3 |
| Application domains named in §1.1 are listed under Document. They are not scenarios. | §1.1 |

## Entities features and roles

| statement | clause |
| --- | --- |
| One device has N entities. | clause not printed |
| One entity belongs to one device. | clause not printed |
| Sub-entities under one entity: zero is allowed, and the upper count is N. | clause not printed |
| One sub-entity belongs to one entity. | clause not printed |
| One entity has M features. | clause not printed |
| One feature belongs to one entity. | clause not printed |
| Device discovery: the concept that returns what a device implements, including the levels device, entity, and feature. Section heading: Device discovery. §2.1, §3.7 | §2.1, §3.7 |
| Detailed discovery: after it has been done at the partner, finding a suitable partner can be automatic. Discovery data names the feature type, and with it the functions that are supported, and with those the operations each function allows. That sentence does not list the operation names. §2.2, §3.7 | §2.2, §3.7 |
| Use Case Discovery (prose spelling). The cross-reference spells the same concept Use Case discovery. §3.7 | §3.7 |
| Server functionality and detailed discovery: the printed verb is shall. That is how server functionality is made known. | clause not printed |
| Client functionality and the same discovery: the printed verb is may. | clause not printed |
| Client features and announcement: the printed verb is should, and the count is at least one. The printed example type is Generic, so a server can tell that the partner is able to act as a client. | clause not printed |
| After the underlying communications technology has connected (SHIP is the example), a device performs detailed discovery of the partner unless that partner is already known from an earlier connection. | clause not printed |
| After that discovery, the device may close the connection or leave it open. The printed example for closing is that no feature type matches. | clause not printed |
| Manufacturers are advised to add a user step. Printed examples: a push-button, or a configuration procedure (a web interface is the inner example). §3.7 | §3.7 |

## Functions and data points

| statement | clause |
| --- | --- |
| nothing further is printed in this section | clause not printed |

## Command limit and timing semantics

| statement | clause |
| --- | --- |
| A datagram is one SPINE message: a header and a payload. Figures 10, 11, and 12 draw that shape; their bodies are not recorded. §3.1 | §3.1 |
| The header is the first part. The prose says it contains elements for the source (the sender), the destination (the recipient), a classifier, and other elements (“etc.”). The prose list is therefore not closed. Detail: [ProtocolSpecification], SPINE Datagram, subsections Introduction, Header, and Payload. §3.1, | §3.1 |
| The payload holds the actual data and is described as a container, because the data varies. Figure 12 groups the constituents; the groups are not recorded. §3.1 | §3.1 |
| Names that appear in the worked datagram and are not given a separate definition in the prose (§3.3): header, specificationVersion (example fill 1.3.0), addressSource, addressDestination, device, entity, feature, msgCounter (example integer), msgCounterReference (example integer), cmdClassifier, payload, cmd, function, filter, cmdControl, partial (empty element in the example), measurementListData, measurementData. The example is an XML document. No rule on these pages says every SPINE message is XML or uses that schema file. §2.3, §3.3 | §3.3, §2.3 |
| Inside cmd, the example’s function element carries the function name measurementListData. §3.3 | §3.3 |
| The example’s cmdClassifier value is reply. §3.3 | §3.3 |
| Where writing is allowed, the server’s information may be written. What “allowed” means is not defined in that sentence. §2.1 | §2.1 |
| The server may accept or decline a write or a call. No error code, no reason list, and no partial-accept rule is printed for that choice. §3.4 | §3.4 |
| The receiver may send an acknowledgement. That tells the sender the message arrived at the destination successfully. The sender may ask for this acknowledgement. §3.5 | §3.5 |
| When a SPINE message fails while it is being received, or while it is being analysed, the receiver returns an error to the original sender. No error-code list is printed. §3.5 | §3.5 |
| A delay of an acknowledgement or of a response can be communicated. No duration, field name, or timer for that delay is printed. §3.5 | §3.5 |
| Detail is in [ProtocolSpecification], chapter SPINE Datagram, part Header, part Acknowledgement concept. §3.5 | §3.5 |
| A filter may go with a read when the whole resource is not wanted, so the payload is smaller. The same idea is used when a notification carries only changed data, and when a write changes only part of the data container at the destination. §2.1 | §2.1 |
| The usual method, called the “default” in this section, is to exchange a whole function instance. Printed example: a client read of deviceDiagnosisStateData, and the server returns that function in full. §3.10 | §3.10 |
| Exchanging only part of a function is sometimes preferable and sometimes required. The required cases are not listed. The name of the concept is restricted function exchange. §3.10 | §3.10 |
| One A write of the complete function is not permitted. The write contains only the children the server permits to be modified. The number two belongs to this §3.10 | §3.10 |
| A second For a large function, it may be favourable to notify only the parts that changed, rather than the whole function when a single child changed. §3.10 | §3.10 |
| The worked reply places an empty partial element under filter / cmdControl on a reply of measurementListData. The prose does not define that empty element. §3.3 | §3.3 |
| Detail is in [ProtocolSpecification], chapter SPINE Datagram, part Payload. The part title there is Restricted function exchange with cmdOptions. The annex title is Recommendations for Restricted Function Exchange. §3.10 | §3.10 |
| Message targets (printed examples: status updates, new sensor values) can be set by static configuration. That assumes an interface on the device, which the text says is often impractical. Binding and subscription are the other way. The partner is chosen using device discovery (§3.7). §3.6 | §3.7, §3.6 |
| Binding is described as process-related: a dedicated interaction of two devices. Example: on and off for a light are accepted only from the light switch bound to it. Binding can also limit other devices for one purpose. Example: a single energy manager is the one allowed to move that device’s demand. Both are examples. They are not a global rule about lights, and they are not a count of energy managers. §3.6 | §3.6 |
| Clients use a subscription to receive updates they did not solicit. New temperature values are the printed example. §3.6 | §3.6 |
| Detail is in [ProtocolSpecification], chapter Functional commissioning. Binding has its own part. Subscription has its own part. §3.6 | §3.6 |
| No failsafe value is printed. | clause not printed |
| No heartbeat send interval, no heartbeat state machine, and no meaning for heartbeatCounter or heartbeatTimeout is printed. fills heartbeatTimeout with PT15M and heartbeatCounter with 238. Those are example fills, not specified timers. | clause not printed |
| No acknowledgement timer and no response timer is printed. Delays can be communicated, without a number. §3.5 | §3.5 |
| No power, energy, or other engineering bound is printed. The measurement example’s number 225 and scale -1 are example fills. §3.3 | §3.3 |
| No state transition is printed. operatingState example literal normalOperation is an instance fill. | clause not printed |
| Address bounds that are printed: each entity element and each feature element is a 32-bit integer; the cardinalities in §3.8, including a sub-entity count from zero up to N; and the device-string ERE, including the excluded Unicode categories. §3.8 | §3.8 |
| Discovery verbs, all lower case, as already listed in section 4: shall for announcing server functionality; may for announcing client functionality; should for announcing one or more client features. After discovery, the device may close the connection or keep it open. §3.7 | §3.7 |
| The device-string character repertoire uses capital MAY. §3.8 | §3.8 |
| A datagram is one SPINE message: a header and a payload. Figures 10, 11, and 12 draw that shape; their bodies are not recorded. §3.1 | §3.1 |
| The header is the first part. The prose says it contains elements for the source (the sender), the destination (the recipient), a classifier, and other elements (“etc.”). The prose list is therefore not closed. Detail: [ProtocolSpecification], SPINE Datagram, subsections Introduction, Header, and Payload. §3.1, | §3.1 |
| The payload holds the actual data and is described as a container, because the data varies. Figure 12 groups the constituents; the groups are not recorded. §3.1 | §3.1 |
| Names that appear in the worked datagram and are not given a separate definition in the prose (§3.3): header, specificationVersion (example fill 1.3.0), addressSource, addressDestination, device, entity, feature, msgCounter (example integer), msgCounterReference (example integer), cmdClassifier, payload, cmd, function, filter, cmdControl, partial (empty element in the example), measurementListData, measurementData. The example is an XML document. No rule on these pages says every SPINE message is XML or uses that schema file. §2.3, §3.3 | §3.3, §2.3 |
| Inside cmd, the example’s function element carries the function name measurementListData. §3.3 | §3.3 |
| The example’s cmdClassifier value is reply. §3.3 | §3.3 |
| Classifier: read; What these pages say: Asks for information. A filter (§3.10) may be sent with it. When processing of that request succeeds, the answer uses reply; Locator: §3.2, §2.1 | §3.10, §3.2, §2.1 |
| Classifier: reply; What these pages say: Answer to a read that was processed. Also a server ability: answer a client that asked for information. The worked message uses reply; Locator: §3.2, §3.4, §3.3 | §3.2, §3.4, §3.3 |
| Classifier: write; What these pages say: A client sends this to change data on the server (the data owner). The server may accept or decline that change; Locator: §3.2, §3.4, §2.1 | §3.2, §3.4, §2.1 |
| Classifier: notify; What these pages say: Tells subscribed clients about changes of the server’s data; Locator: §3.2 | §3.2 |
| Classifier: call; What these pages say: Starts a remote procedure on the partner. The server may accept or decline that action; Locator: §3.2, §3.4 | §3.2, §3.4 |
| Classifier: result; What these pages say: Used within acknowledgement messages and error messages; Locator: §3.2 | §3.2 |
| Classifier: ack; What these pages say: Named in the classifier list. No separate behaviour sentence on these pages; Locator: §3.2 | §3.2 |
| Where writing is allowed, the server’s information may be written. What “allowed” means is not defined in that sentence. §2.1 | §2.1 |
| The server may accept or decline a write or a call. No error code, no reason list, and no partial-accept rule is printed for that choice. §3.4 | §3.4 |
| The receiver may send an acknowledgement. That tells the sender the message arrived at the destination successfully. The sender may ask for this acknowledgement. §3.5 | §3.5 |
| When a SPINE message fails while it is being received, or while it is being analysed, the receiver returns an error to the original sender. No error-code list is printed. §3.5 | §3.5 |
| A delay of an acknowledgement or of a response can be communicated. No duration, field name, or timer for that delay is printed. §3.5 | §3.5 |
| Detail is in [ProtocolSpecification], chapter SPINE Datagram, part Header, part Acknowledgement concept. §3.5 | §3.5 |
| A filter may go with a read when the whole resource is not wanted, so the payload is smaller. The same idea is used when a notification carries only changed data, and when a write changes only part of the data container at the destination. §2.1 | §2.1 |
| The usual method, called the “default” in this section, is to exchange a whole function instance. Printed example: a client read of deviceDiagnosisStateData, and the server returns that function in full. §3.10 | §3.10 |
| Exchanging only part of a function is sometimes preferable and sometimes required. The required cases are not listed. The name of the concept is restricted function exchange. §3.10 | §3.10 |
| One A write of the complete function is not permitted. The write contains only the children the server permits to be modified. The number two belongs to this §3.10 | §3.10 |
| A second For a large function, it may be favourable to notify only the parts that changed, rather than the whole function when a single child changed. §3.10 | §3.10 |
| The worked reply places an empty partial element under filter / cmdControl on a reply of measurementListData. The prose does not define that empty element. §3.3 | §3.3 |
| Detail is in [ProtocolSpecification], chapter SPINE Datagram, part Payload. The part title there is Restricted function exchange with cmdOptions. The annex title is Recommendations for Restricted Function Exchange. §3.10 | §3.10 |
| Message targets (printed examples: status updates, new sensor values) can be set by static configuration. That assumes an interface on the device, which the text says is often impractical. Binding and subscription are the other way. The partner is chosen using device discovery (§3.7). §3.6 | §3.7, §3.6 |
| Binding is described as process-related: a dedicated interaction of two devices. Example: on and off for a light are accepted only from the light switch bound to it. Binding can also limit other devices for one purpose. Example: a single energy manager is the one allowed to move that device’s demand. Both are examples. They are not a global rule about lights, and they are not a count of energy managers. §3.6 | §3.6 |
| Clients use a subscription to receive updates they did not solicit. New temperature values are the printed example. §3.6 | §3.6 |
| Detail is in [ProtocolSpecification], chapter Functional commissioning. Binding has its own part. Subscription has its own part. §3.6 | §3.6 |
| No failsafe value is printed. | clause not printed |
| No heartbeat send interval, no heartbeat state machine, and no meaning for heartbeatCounter or heartbeatTimeout is printed. fills heartbeatTimeout with PT15M and heartbeatCounter with 238. Those are example fills, not specified timers. | clause not printed |
| No acknowledgement timer and no response timer is printed. Delays can be communicated, without a number. §3.5 | §3.5 |
| No power, energy, or other engineering bound is printed. The measurement example’s number 225 and scale -1 are example fills. §3.3 | §3.3 |
| No state transition is printed. operatingState example literal normalOperation is an instance fill. | clause not printed |
| Address bounds that are printed: each entity element and each feature element is a 32-bit integer; the cardinalities in §3.8, including a sub-entity count from zero up to N; and the device-string ERE, including the excluded Unicode categories. §3.8 | §3.8 |
| Discovery verbs, all lower case, as already listed in section 4: shall for announcing server functionality; may for announcing client functionality; should for announcing one or more client features. After discovery, the device may close the connection or keep it open. §3.7 | §3.7 |
| The device-string character repertoire uses capital MAY. §3.8 | §3.8 |

## Requirements

| statement | clause |
| --- | --- |
| nothing further is printed in this section | clause not printed |

## Open points

| statement | clause |
| --- | --- |
| Page 2 says, in general, that specifications not submitted to a standards body (examples named: DKE/DIN-VDE, IEC/CENELEC/ETSI) are preliminary information, and that versions already issued through such bodies can still contain errors and may be updated. This report does not say which of those situations applies to itself. No status was taken from that page. | clause not printed |
| §2.3 cites [SHIP] for JSON. The reference list defines [SHIPSpecification], not [SHIP]. §2.3, §1.3.2 | §2.3, [SHIP], §1.3.2 |
| §2.2 says a feature type’s class is “simple or complex” and points at §3.3. §3.3’s heading is “Standard class vs. complex class”, and another sentence says each complex class is released like “normal classes”. The report does not equate simple, standard, and normal. §2.2, §3.3 | §2.2, §3.3 |
| Prose names actuatorLevel and actuatorLevelDescription as the only information defined for class ActuatorLevel. names actuatorLevelData and element value. Both are printed. §2.3 | §2.3 |
| Figure 6 prints 1 and n beside the function band and beside the element band. Which side is 1 and which side is n is not recorded. | §2.3 |
| ack is in the classifier list and has no behaviour sentence. result is the classifier tied to acknowledgement and error messages. The report does not say whether ack and that acknowledgement are the same classifier. §3.2, §3.5 | §3.2, §3.5 |
| §3.4 “inform clients about updates” and §3.2 notify to subscribed clients are separate sentences. The report does not state that they are the same mechanism. §3.4, §3.2 | §3.4, §3.2 |
| A filter is described with a read, with a notification of only what changed, and with a partial write. The worked message puts filter / cmdControl / partial on a reply. The report does not explain that combination. §2.1, §3.2, §3.3 | §2.1, §3.2, §3.3 |
| §3.7 says client functionality may be announced in detailed discovery, and that one or more client features should be announced (Generic is the example). The same section says detailed discovery can miss client functionality, and then Use Case Discovery is available. Both are printed. §3.7, | §3.7 |
| “Possible operations” published in discovery are not enumerated. The classifier list is in another section and is not tied by the text to that discovery field. §2.2, §3.2 | §2.2, §3.2 |
| Repeating the entity element is shown in the worked address (three on the source, one on the destination) and is not stated as the rule for sub-entities. Sub-entity cardinality is 0..N. §3.3, §3.8, §2.4 | §3.3, §3.8, §2.4 |
| The device-string branches i: and n: are not glossed. Only i: examples are printed. §3.8, | §3.8 |
| Restricted exchange is sometimes required. The cases are not listed. The two-child write limit is one unnamed §3.10 | §3.10 |
| Common data types are said to be in [ResourceSpecification] Common technical details and are not printed here. §2.3 | §2.3 |
| SmartEnergyManagementPs element names exist only inside Figures 14 and 15. §3.3 | §3.3 |
| No M, R, or O support level, no requirement identifier, no failsafe, and no numeric timeout is printed. Example fills in and in the worked datagram are not those missing rules. | clause not printed |
