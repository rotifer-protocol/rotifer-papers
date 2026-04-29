# Where Capability Lives, and How Hardware Earns the Right to Run It

## A Position Paper on the Meta-Protocol Layer for Distributed Intelligence on Heterogeneous Hardware

> **Pre-arXiv Submission Notice**: This paper is released as a public draft so that its methodology and architecture can receive community critique before empirical results are produced. The argument involves protocol mechanisms that are not yet fully implemented (see the "Implementation Status Layering" convention and §8.1); the empirical validation plan (Petri Challenge v1) is in progress. Public release timing should be decided only after external citations and implementation-state claims have been independently verified.

**Version:** 0.1 (Public Draft)

**Date:** April 26, 2026

**Author:** Rotifer Foundation

**Status:** Public Draft — v1.0 to follow the empirical results of Petri Challenge v1.

**arXiv Category Plan:** cs.DC (primary), cs.CR, cs.AI

**Keywords:** meta-protocol, distributed intelligence, trusted execution environment, edge AI, capability declaration, substrate awareness, installed-base computing

**Protocol:** Rotifer Protocol Specification

**Companion Papers:**
- *The Philosophy of Digital Evolution* (v1.2, 2026) — philosophical grounding
- *Toward Protocol-Level Evaluation of Distributed AI Agent Evolution* (v0.1, 2026, forthcoming arXiv preprint) — protocol-level evaluation methodology (cs.MA)

**License:** CC BY-SA 4.0

---

## Table of Contents

- [Executive Summary](#executive-summary)
- [1. The Meta-Protocol Layer Nobody Owns](#1-the-meta-protocol-layer-nobody-owns)
- [2. The Hardware Question Distributed Intelligence Cannot Avoid](#2-the-hardware-question-distributed-intelligence-cannot-avoid)
- [3. The Information-Theoretic Reality Check](#3-the-information-theoretic-reality-check)
- [4. TEE as the Physical Entry Point of the Meta-Protocol](#4-tee-as-the-physical-entry-point-of-the-meta-protocol)
- [5. Capable Edge: When the Math Just Started Working](#5-capable-edge-when-the-math-just-started-working)
- [6. Phenotype, Fidelity, Imprinting, Adapter — The Substrate-Aware Vocabulary](#6-phenotype-fidelity-imprinting-adapter--the-substrate-aware-vocabulary)
- [7. The Smartphone as Anchor: Where the Story Crystallizes](#7-the-smartphone-as-anchor-where-the-story-crystallizes)
- [8. Sector-by-Sector Candidacy with Honest Layering](#8-sector-by-sector-candidacy-with-honest-layering)
- [9. The Hundred-Billion-Node Endgame](#9-the-hundred-billion-node-endgame)
- [10. Open Questions, Falsifiability, How to Engage](#10-open-questions-falsifiability-how-to-engage)
- [References](#references)

---

## Executive Summary

The next decade of AI will not be decided by model size alone. Equally consequential is whether the billions of devices already shipped — sitting in pockets, on factory floors, in vehicles — can credibly host the capabilities the cloud is now growing. Today, capability lives where it was trained — inside large data centers, behind opaque APIs, in models whose weights cannot be inspected, whose behavior cannot be evolved by anyone except their owners, and whose runtime is divorced from the substrate that has to honor what they claim. The result is a structural mismatch: AI capabilities grow in the cloud, while a large installed base of devices in the physical world — phones, vehicles, embedded controllers, industrial sensors, smart appliances, edge gateways — is slowly drifting from "possible to upgrade" to "expensive to discard."

Rotifer Protocol takes a different position. Capabilities should be expressible as transferable, evaluable, evolvable units (Genes), each carrying a structured Phenotype that declares what substrate honors it; protocols should not invent new neural networks but define how existing ones compose, evolve, and remain accountable to their hardware. We hypothesize — and welcome public scrutiny — that this protocol layer may be to AI capability what HTTP was to documents: HTTP did not invent TCP/IP, yet it defined how a composable Web could be built on it. How far the analogy holds is an empirical question that will take time to answer; Rotifer aims to be the meta-protocol layer on which distributed intelligence — across heterogeneous hardware, across observer classes, across time — can emerge without collapsing into a single vendor.

This report makes a single argument: **Trusted Execution Environments (TEE) are a reasonable physical entry point through which the installed base can become first-class nodes of this meta-protocol** — not the only viable path, but the one whose deployment surface most overlaps with consumer-grade hardware today. TEE is the interface where protocol-level capability declarations meet hardware-level integrity guarantees. When that interface is taken seriously, three things become possible at once: capability promises stop drifting from substrates, old hardware stops being marketing collateral and starts being computational citizens, and intelligence can emerge across observer classes without a single data center being the only honest layer.

We do not claim Rotifer Protocol has solved this. We claim that the protocol has been designed for this moment — that its core public mechanisms (Gene, Phenotype, Fidelity, Arena, Imprinting, Adapter) and its open trust-backend architecture are the substrate from which this story can be built, and that the empirical and theoretical foundations are now in place. The rest of this document describes what is already true, what is being engineered, and what remains a research question. The reader is invited to disagree on every page.

---

> **Implementation Status Layering (Key Reading Convention)**: The argument in this report spans three time windows — capabilities verifiable in the public implementation today, protocol layers currently being engineered, and longer-horizon roadmap items. **§8.1 lays out the full three-tier breakdown**; throughout the document, references to the Rotifer Protocol should be read against the "implemented / being engineered / longer-horizon" layering. Descriptions of undelivered features are explicitly marked as "target behavior."

---

## 1. The Meta-Protocol Layer Nobody Owns

### 1.1 What HTTP Did to Composability

In 1991, the Web did not exist. By 2001, it was rewriting commerce, journalism, education, and software itself. The shift had a single technical precondition: a protocol that did not own the content but defined how content could be linked, addressed, fetched, and rendered by any participant.

HTTP did not invent text. It did not invent images. It did not invent the underlying network. What HTTP did was define a coordination layer on top of TCP/IP at which two unrelated parties — the publisher and the reader, the server and the browser, the indexer and the citizen — could agree on what a document was, how to ask for it, and how to interpret what came back. The actual matter of the Web — HTML pages, image bytes, form submissions — flowed through HTTP, but HTTP itself remained light, specifiable, evolvable, and unowned.

That structural choice is why we now talk about a Web instead of a fragmented set of vendor protocols. Composability followed openness; openness followed protocol-level minimalism.

### 1.2 Why AI Needs Its Own Layer

Compare that to the current state of AI capability.

Capability lives inside model weights, inside SDK boundaries, inside corporate APIs, inside proprietary scaffolding. There is no agreed-upon way to ask another system "what can you do, and on what substrate, at what fidelity, with what verifiable guarantees." There is no agreed-upon way to compose a capability from a phone with a capability from a cloud and a capability from a robot, in a manner that any third participant can reason about. There is no analog of an HTML document for a unit of intelligence — no portable, inspectable, citable, evaluable artifact.

The closest available primitives — function-calling tool schemas, MCP-style tool descriptions, agent JSON cards — are improvements on the SDK layer, not at the protocol layer. They standardize a calling convention. They do not standardize the substrate-awareness that distinguishes a capability that can run from a capability that should run.

### 1.3 The Definition of "Meta-Protocol"

We use the term **meta-protocol** with a specific operational meaning: a protocol whose subject is not a single resource type (text, video, payment) but the rules under which capabilities themselves can be declared, evolved, evaluated, and composed. A meta-protocol does not invent the capabilities it carries; it defines the conditions under which capabilities from heterogeneous sources can interoperate.

Three properties identify a meta-protocol candidate:

1. **Substrate-awareness**: every capability declaration must carry the conditions under which it remains valid — what computational budget honors it, what trust backend backs it, what failure modes apply.
2. **Evolution-awareness**: capabilities must be expressible as units that can be evaluated, ranked, replaced, and composed without breaking interoperability with the rest of the network.
3. **Vendor-neutrality**: no single party — including the protocol's originating organization — can hold a privileged position that the protocol itself enforces.

Rotifer Protocol satisfies all three by design. Whether it succeeds in becoming a *de facto* meta-protocol depends on adoption, not on architecture. This document concerns itself with the architecture; adoption is the work that follows.

### 1.4 Why It Cannot Be Owned by a Vendor

The history of vendor-owned communication protocols is a history of eventual displacement. Closed messaging stacks lost to SMTP and XMPP. Closed network stacks lost to TCP/IP. Closed document formats lost to HTML and PDF (the latter only because Adobe eventually opened it under ISO 32000). The pattern is consistent: a sufficiently general layer cannot be sustained as proprietary infrastructure, because the moment a single party becomes essential to the layer's operation, every other participant has an incentive to route around them.

For an AI capability layer, this incentive is even stronger than for prior protocols. Capability is the central scarce resource of the AI era. A vendor-owned capability layer is a permanent rent. The market alternative is not a different vendor-owned layer; the market alternative is an open meta-protocol with multiple privileged nodes serving overlapping niches.

Rotifer's positioning is built around this observation. The protocol's core mechanisms are open and CC BY-SA licensed. The Foundation operates a privileged node, but the protocol is structurally indifferent to the Foundation's continued participation. A successful meta-protocol is one in which the originating organization can disappear without the protocol disappearing.

---

## 2. The Hardware Question Distributed Intelligence Cannot Avoid

### 2.1 The Trillion-Device Installed Base

There is a number that gets quoted casually in the AI industry but is rarely treated as a load-bearing fact: there are roughly seventy billion smartphones, several billion smart-home devices, hundreds of millions of vehicles, tens of billions of industrial IoT endpoints, and an even larger number of embedded controllers in active use across the physical world. Different analysts use different boundaries; the total order of magnitude — between 10^11 and 10^12 active electronic devices with some computational capacity — is not in dispute.

This is the installed base of intelligence-capable hardware. Most of it has shipped within the last ten years. Almost all of it will continue to operate for another five to twenty years, depending on category. By any honest measure, this installed base is the actual substrate on which AI capability has to live, if AI capability is going to live in physical reality at all.

It is not where AI capability currently lives.

### 2.2 Path A: Centralized Cloud Inference

The default industry response to this gap is to push capability into centralized cloud inference and route hardware queries to it. This works, and it works extremely well for many use cases. It is also structurally unable to support distributed intelligence at the scale of the installed base.

Three constraints bound centralized inference. First, latency: the round-trip from a device to a hyperscale data center is fundamentally bounded by the speed of light and the layout of internet infrastructure; many real-time control loops cannot tolerate that round-trip. Second, sovereignty: data flowing to a cloud crosses regulatory, organizational, and personal trust boundaries that a growing fraction of users will not accept for a growing fraction of their data. Third, long-tail accessibility: the trillion-device installed base includes devices in regions, networks, and operational conditions where reliable cloud access cannot be assumed.

These constraints do not mean centralized inference is wrong. They mean it is partial. A complete picture of distributed intelligence requires capability that can reside on the device, with cloud as one option among several, not as the only honest layer.

### 2.3 Path B: Aggressive OTA Promises

The second industry response is to promise capability upgrades through over-the-air updates without anchoring those promises to the substrates that have to honor them. This has produced a recurring failure mode visible across multiple consumer-facing categories: hardware shipped with marketing language describing capabilities that the hardware was never sized to deliver, and software updates that progressively widen the gap between what users were promised and what their device can actually run.

This pattern is older than AI and not unique to any one company. It exists in long-life consumer goods generally — automobiles with feature flags that never activate, smart appliances whose advertised "AI features" become subscription tiers, embedded controllers whose published spec sheets describe capabilities that only the next generation can perform. AI accelerates the pattern because the rate at which capability promises grow has decoupled from the rate at which hardware ships.

The structural problem is not the promises. The structural problem is that there is no protocol-level layer at which a promise must declare the substrate that makes it true. Without that layer, every promise eventually drifts.

### 2.4 Path C: Edge Autonomy in Isolation

The third response is to treat each edge device as an autonomous agent that does what it can with what it has. This avoids the latency and sovereignty problems of centralized inference and avoids the drift problem of aggressive OTA. But it loses something that distributed intelligence cannot afford to lose: cross-device knowledge transfer.

A device that fails on a corner case in Berlin learns nothing about a similar failure in Singapore. A pattern discovered on a high-end model never reaches the lower-tier model that needs it. The collective experience of the installed base evaporates the moment each device makes its own decision in its own session. Edge autonomy without a coordination layer produces an ecosystem of devices that get individually slightly better and collectively no better at all.

### 2.5 The Fourth Path

The three paths above are not wrong. Each has a real success region. What they cannot do, individually or in combination, is support distributed intelligence at the scale of the trillion-device installed base — because none of them defines a layer at which capability declarations remain accountable to the substrates that honor them, while still allowing capabilities to move, evolve, and accumulate across the network.

That layer is what this report calls a meta-protocol. The remaining sections describe what one specifically — Rotifer Protocol — proposes as the substrate-aware vocabulary, the trust-backend architecture, and the physical entry point through which the installed base can begin to participate.

---

## 3. The Information-Theoretic Reality Check

### 3.1 Three Sentences That Are Not the Same

Most capability drift originates from collapsing three different sentences into one.

> "X is possible."

means that, somewhere, on some configuration, the capability X has been demonstrated. This is the sentence that travels best in keynotes. It almost never specifies which configuration.

> "X is possible on this kind of hardware."

means that a class of devices similar to a deployed product can support X. This sentence is harder to make because it requires a class definition; it usually presupposes thermal envelopes, memory bandwidth, accelerator generation, and firmware version.

> "X is possible on the hardware in your hands right now."

means that the specific chip, the specific memory bandwidth, the specific thermal envelope, the specific firmware in a user's actual device can support X today. This sentence is the only one that has any binding force on a real product. It is also the sentence that protocols, marketing departments, and roadmaps are routinely under-specified to express.

A protocol that does not distinguish these three sentences will let any product compress them into one. The first one travels well. The third one is the only one that pays interest on the loan.

### 3.2 Epiplexity in One Paragraph

Recent information-theoretic work makes the distinction precise. Finzi, Qiu, Jiang, Izmailov, Kolter, and Wilson [7] introduce the notion of *epiplexity*: structural information available to a computationally bounded observer. Their formal framework defines epiplexity as a function of both the data and the observer's computational budget. Information that requires unbounded computation to extract is not epiplexity, however much entropy it contains. Two observers viewing the same environment with different computational budgets extract different reachable structures from it. Not slower. Different. Some reachable structure for one budget is not approximately reachable for another budget — it is structurally absent.

The companion paper [10] develops this distinction in the context of digital speciation. The key implication for the present discussion is operational: capability is not a property of a problem; it is a property of the pair (problem, observer). Two device generations facing the same problem are not running the same race at different speeds; they are running races whose finish lines are in different places.

### 3.3 What This Implies for Hardware Generations

Hardware generations differ along multiple axes — clock rate, memory bandwidth, accelerator architecture, energy envelope, sensor resolution, network access. Each axis is a constraint on the observer's computational budget. The aggregated effect is that two consecutive hardware generations sit in different observer classes.

For most workloads, the difference is invisible to the user. A web browser runs comparably well on a five-year-old device and a current device. The interesting workloads are the ones where a new capability is structurally reachable for the new observer class but structurally absent for the old one. That is where capability drift becomes visible, painful, and — without a protocol-level layer — without recourse.

The information-theoretic statement is not a metaphor. It is a constraint. Any protocol that anchors capability declarations to the marketing layer — to a single product name, to a roadmap sentence, to an SDK version — is a protocol that allows promises to migrate across observer classes silently. Any protocol that anchors capability declarations to the substrate that honors them produces capability claims that can be validated against the actual reachable structure of the actual hardware.

### 3.4 Why This Cannot Be Solved by More Software

A natural objection is that better software — smaller models, faster inference, smarter compilation — can close the gap. This is true and important within an observer class. It is not true across observer classes. No amount of software effort raises an observer's computational budget; it only redistributes how that budget is spent.

This is not pessimism. It is the foundation for the protocol's architectural posture: instead of pretending that hardware constraints will eventually disappear, the protocol exposes them as first-class structure that capability declarations must respect. Software gets better; substrates remain finite; the protocol mediates between the two.

---

## 4. TEE as the Physical Entry Point of the Meta-Protocol

### 4.1 TEE Today: A Quiet Universal Substrate

A Trusted Execution Environment is, in operational terms, a region of a processor in which code can run with hardware-enforced isolation from the rest of the system, and whose state can be cryptographically attested to remote parties. Different architectures implement this differently — some on the application processor, some on a dedicated security coprocessor, some at the package level, some across multiple silicon islands — but the externally visible properties converge on three: a *measurement* of what code is running, a *seal* on data that only that code can decrypt, and a *channel* through which a remote party can confirm both.

TEEs are not exotic infrastructure. Modern smartphones ship with hardware-rooted secure execution as a default. Modern automotive ECUs increasingly include trust-zone style isolation for security-critical workloads. Industrial IoT controllers use secure boot pipelines that share architectural primitives with TEE designs. Cloud providers expose hardware-attested confidential computing offerings backed by silicon-level isolation. The aggregate result is that, by 2026, a non-trivial majority of newly shipped consumer-facing computational hardware contains a TEE-class capability of some kind.

This is a quiet substrate, in the sense that most users have never heard of it and most software does not exercise it. It is also a universal substrate, in the sense that it is increasingly present *somewhere* in the silicon of *almost any* device that processes user-specific data.

### 4.2 What the Protocol Already Says About Trust Backends

Rotifer Protocol's specification, in its description of the L0 Kernel layer, defines the protocol's trust root through an abstract `Trust Anchor` interface that admits multiple concrete implementations. The four backend categories explicitly listed in the specification are distributed ledgers, trusted execution environments, cryptographic signature chains, and hardware security modules. Each is mapped to characteristic deployment scenarios — decentralized permissionless networks, enterprise high-performance contexts, lightweight controlled networks, and IoT/embedded devices respectively.

The protocol therefore makes no architectural commitment to TEE as a privileged backend. TEE is one of the four equal-stature options. This document does not propose modifying that specification. It proposes a complementary observation: among the four options, TEE is the one most naturally suited to be the *physical entry point* through which the trillion-device installed base can participate in the meta-protocol — not because the others are wrong, but because TEE is the only option whose deployment surface is co-extensive with consumer-facing physical hardware.

### 4.3 Three Properties That Make TEE the Right Entry Point

Three properties, taken together, distinguish TEE from the other trust backends in the role of installed-base entry point.

**Universal availability.** Distributed ledgers exist on a relatively small number of nodes by global hardware standards. HSMs exist in specialized deployments. Cryptographic signature chains exist wherever someone is willing to operate a CA. TEE-class capability exists in the silicon of devices that have already been shipped, paid for, and put into operational use in living rooms, vehicles, factories, and pockets. The integration question is not where to put new infrastructure; it is how to engage infrastructure that is already there.

**Integrity guarantees rooted in silicon.** A capability declaration that carries an attestation from a TEE makes a claim that is verifiable against silicon-level state, not against software-level assertions. This is qualitatively different from declarations rooted in self-signed manifests or in trust chains that can be re-issued by a sufficiently motivated party. Silicon-rooted attestations are not unforgeable; nothing is. They are the strongest available substrate-aware integrity guarantee, and they degrade gracefully — a fragile attestation is still better than no attestation.

**Identity rooted in a specific device.** The other trust backends produce identities rooted in keys, certificates, or chain history. TEE-rooted identity is anchored to a particular silicon instance. For a meta-protocol whose unit of participation is a *node* and not just an *account*, this anchoring is exactly the right primitive. It allows the protocol to reason about node-level reputation, node-level participation history, and node-level capability declarations with a degree of accountability that key-rooted systems cannot match.

These three properties together support the operational claim of this section: TEE is not the only legitimate trust backend, but under current installed-base conditions, it is the reasonable first choice for the meta-protocol to engage consumer-grade hardware — an operational trade-off, not an architectural exclusion.

### 4.4 What TEE Cannot Do Alone

A TEE, by itself, has no opinion about what a capability is. It can attest that a particular binary ran in a particular isolated state and produced a particular output. It cannot say whether that binary was an honest implementation of a published capability, whether the output was a faithful response to the input, whether the capability composes correctly with other capabilities, or whether its declared resource usage matches its actual resource usage.

The meta-protocol layer is what makes those questions answerable. Phenotype declarations, Fidelity ratings, fitness evaluations, Adapter contracts, and Imprinting state are all artifacts of the meta-protocol layer. They are *what is being attested*. Without them, the TEE produces strong guarantees about the wrong subject. Without the TEE, the meta-protocol layer has no way to bind its declarations to silicon-level reality.

The two layers are mutually necessary. The TEE provides hardware-level integrity. The meta-protocol provides substrate-aware vocabulary. A coherent system needs both.

### 4.5 TEE × Capability Anchoring: A Coherent Story

The argument now reads as a single arc. Capability promises drift because there is no protocol-level layer at which they must declare the substrate that makes them true (§2). Information theory provides the formal reason that this drift is not a fixable accident but a structural consequence of crossing observer classes (§3). The meta-protocol layer is the place where capability declarations can be substrate-aware (§1, §6 below). TEE is the physical interface where those declarations meet the silicon that has to honor them (§4.1–§4.3). And the two layers compose: TEE provides hardware-rooted integrity for what the meta-protocol declares (§4.4).

This is what makes the trillion-device installed base addressable. Not all at once. Not without years of integration work. But in principle and in architecture, the path exists, and the protocol mechanisms required to walk it have been specified.

### 4.6 What This Chapter Does Not Claim

To prevent the kind of capability drift this paper itself diagnoses, three claims must be explicitly excluded from the argument above.

First, this chapter does not claim that the engineering work to deploy a TEE-backed Binding for Rotifer Protocol is complete or imminent. Edge and TEE Bindings remain on the protocol's longer-horizon implementation track; the present argument is at the strategic and narrative layer, decoupled from the engineering priority of the protocol's near-term release schedule.

Second, this chapter does not claim that TEE heterogeneity is solved. The five major TEE families currently deployed — Intel TDX, ARM TrustZone, Apple Secure Enclave, Qualcomm-class trust environments, and AWS Nitro-class confidential computing — do not interoperate at the protocol layer today. Bridging them is the responsibility of the protocol's Adapter layer, not of TEE Binding design. §10 treats this as an open question.

Third, this chapter does not claim that TEE turns Rotifer into a hardware company. Rotifer remains a protocol layer. A Binding is a contract under which a runtime environment can host the protocol; a TEE-backed Binding would be one such contract. The Foundation does not propose to manufacture silicon, certify devices, or operate TEE infrastructure on behalf of OEMs.

These exclusions are not boilerplate. They are the substrate that the rest of the report depends on.

---

## 5. Capable Edge: When the Math Just Started Working

### 5.1 The Number Nobody Talks About

In 2024 and 2025, the number that mattered for on-device AI was *can the model fit*. Quantization, distillation, sparse decoding, and a generation of efficient small models eventually made on-device fit into a default rather than an achievement. The interesting number became *how fast*.

For multi-step agent workflows — the kind that involve tool calling, intermediate reasoning, structured output, and several rounds of decision — the threshold has become surprisingly concrete. Public reports for Google's Gemma 3 family indicate decode rates in the range of 7–8 tokens per second on Raspberry Pi 5 CPU for the smaller variants and decode rates in the range of 30+ tokens per second on Qualcomm-class mobile NPUs for the next variant up (numbers drawn from the Gemma 3 model card and third-party benchmarks on Raspberry Pi 5 / Qualcomm AI Engine; specific figures vary with quantization scheme, precision, and runtime implementation). These rates are sufficient to support a four-thousand-token input followed by two skill invocations within a wall-clock budget that users will accept as interactive.

These are not the rates of cloud-class inference. They are the rates that, for the first time, make complete agent workflows operationally feasible on hardware that already exists in the field.

### 5.2 Why This Is a Phase Transition, Not an Improvement

A continuous improvement in edge inference would not change the architectural conversation. Faster inference for the same workloads would only mean better user experience. What has actually happened is qualitatively different.

For most of the last five years, capable agent workflows required cloud round-trips because no available edge stack could close the loop in human-interactive time. The economic, latency, sovereignty, and accessibility consequences followed from that constraint. As of the most recent generation of edge LLMs, the constraint has been released. The same workload that previously could only be cloud-resident can now, within reasonable engineering effort, be edge-resident.

This is a phase transition because it changes which architectural patterns are available, not just which patterns are convenient. It is the moment the meta-protocol layer becomes physically inhabitable on the installed base, rather than a thought experiment about it.

### 5.3 What "Capable Edge" Means at the Protocol Level

The protocol previously distinguished two implementation profiles for runtimes — a constrained profile for resource-tight environments and a full profile for unrestricted runtimes. The 2026 generation of edge LLMs introduces a third profile situated between them. This *Capable Edge* profile describes runtimes that can host complete agent workflows with native inference, multi-tool coordination, and persistent local state, but that do so within a fixed silicon and energy envelope that distinguishes them from full-profile cloud runtimes.

The Capable Edge profile is not a new spec layer; it is a new operating point on the existing spec. It is where the substrate becomes rich enough that the meta-protocol's full vocabulary — Phenotype declarations, Fidelity ratings, Imprinting state, Adapter translation — can be exercised without compromise.

### 5.4 The Implication for Long-Lived Devices

The combination of the previous sections produces a counterintuitive implication. The trillion-device installed base is not a collection of devices that need to wait for a hardware refresh to participate in distributed intelligence. A meaningful fraction of it — recent-generation smartphones, current-generation vehicle infotainment systems, the higher tiers of industrial gateways — already crosses the Capable Edge threshold. For these devices, the bottleneck is not silicon. It is the absence of a protocol layer at which they can declare what they can do, attest the substrate they run on, and exchange capabilities with the rest of the network.

That bottleneck is what the meta-protocol exists to remove.

---

## 6. Phenotype, Fidelity, Imprinting, Adapter — The Substrate-Aware Vocabulary

### 6.1 Phenotype: The Receipt for Every Capability

A Gene in Rotifer Protocol is not just executable code. It carries a Phenotype: a structured declaration of the input shape it accepts, the output shape it returns, the resource budget it requires, the security properties it claims, the version it represents, and the fidelity at which it operates on the substrate currently hosting it. The Phenotype is the receipt. It says: this capability, on this Binding, at this fidelity level, was honored.

Two devices that publish a capability under the same name can carry the same capability with different Phenotype declarations underneath. One Native. One Wrapped. One on a Capable Edge profile, one on a Constrained profile. The product page may treat them as identical. The meta-protocol does not have to.

### 6.2 Fidelity: Three Honesty Levels

Fidelity has three levels, each operating on a different relationship to the protocol's evolutionary machinery.

A **Native** Gene is the protocol's own form. It can be evaluated, ranked, and composed directly. Its full evolutionary lifecycle applies — fitness scoring, Arena ranking, horizontal transfer, lineage tracking, immune-system review.

A **Hybrid** Gene is partially native and partially adapted from another substrate. Its evaluation is real but partial. Hybrid Genes are common during the migration of capabilities from external systems into the protocol; they are also common in deployments where some sub-capabilities have native implementations and others rely on existing infrastructure.

A **Wrapped** Gene is exposed through an adapter around an external or lower-fidelity system. Wrapped Genes can still participate in the protocol, but their receipt says, transparently: this capability did not originate within the protocol; it is being borrowed from beneath. Wrapped fidelity is honest, not pejorative.

The three-level distinction does not exist to make some Genes second-class. It exists so that no Gene's substrate is obscured.

### 6.3 Imprinting: Specialization Inside the Budget

The protocol's local-adaptation mechanism — referred to internally as *Imprinting* — addresses the problem that not all valuable structure is universal. A device whose computational budget cannot reach a general-purpose capability across all users may still extract enormous structure inside the narrow distribution it actually inhabits: this user's habits, this vehicle's route, this household's energy profile, this farm's soil cycle.

Imprinting is not a failed copy of global evolution. It is a different evolutionary direction, oriented from one Agent toward the local context that Agent will inhabit for the rest of its operational life. Global evolution selects across populations; Imprinting adapts within an instance. Both produce useful structure; they produce different useful structure.

For long-lived hardware, Imprinting is the mechanism through which a device can become more valuable over time inside its specific deployment, even when it cannot follow general capability into newer hardware classes. This is specialization, not deprecation. A device that loses the right to claim a universal high-autonomy Phenotype does not lose the right to evolve locally, and it does not lose the right to remain useful in the niche it occupies.

### 6.4 Adapter: Cross-Class Translation

An Adapter is a Gene whose function is to translate between substrates. It can translate a capability written for one Binding into a form executable on another. It can translate a pattern discovered on a Capable Edge profile into a simplified form runnable on a Constrained profile. It can translate a piece of native protocol vocabulary into a wrapped form for systems outside the protocol's direct reach.

Adapters are first-class participants in the protocol — they are evaluated, ranked, and composed like any other Gene. The implication is that translation quality itself becomes a property the protocol can optimize for, rather than a fixed engineering constant. Better adapters win against worse adapters in the same evolutionary competition that selects for better any-other-Genes.

For the installed base argument of this paper, Adapters are the mechanism that makes cross-class knowledge transfer possible. A failure pattern observed on a high-budget node does not have to migrate as native code to a low-budget node; the relevant *part* of that pattern — the warning, the heuristic, the failure signature — can migrate in a wrapped or simplified form that the low-budget node can honestly execute.

### 6.5 Collective Immunity: Failure Becomes Defense

The protocol's L4 layer treats certain kinds of failures as a population-level signal. When a node experiences a failure of a specific class — a malicious Gene, a coordinated attack, a degraded substrate — the failure is broadcast as a defensive signal that other nodes can subscribe to.

For the installed base, this is the mechanism through which the long tail of devices becomes more robust collectively than any individual device could be on its own. A single device's incident becomes a defensive Gene available to the population, but each hardware class receives the Gene in the form it can honestly run — Native where Native is feasible, Wrapped where it is not, simplified where simplification is required.

The five mechanisms in this section — Phenotype, Fidelity, Imprinting, Adapter, Collective Immunity — are not five independent tools. They are five facets of one architectural posture: the posture that capability is always paired with the substrate that honors it, and that the protocol's job is to keep that pairing visible through every operation in the network.

---

## 7. The Smartphone as Anchor: Where the Story Crystallizes

### 7.1 Why Smartphones Make the Best Anchor

The claims in §1–§6 are general. The most efficient way to evaluate them is to apply them to the single deployment surface where every component aligns: the modern smartphone.

Five reasons make the smartphone the cleanest evaluation surface for the meta-protocol-on-hardware story.

First, **TEE deployment is effectively universal**. Every recent-generation smartphone ships with hardware-rooted secure execution as a default capability. There is no installed base where the hardware integrity story has higher coverage.

Second, **the long-lifecycle tension is sharpest**. Users routinely keep smartphones for five to seven years across two or more software-promise cycles. The drift between what a device was promised to do at purchase and what its current OS update promises is most visible here.

Third, **user education cost is lowest**. Smartphone users are already accustomed to OTA updates, software-defined feature changes, and capabilities that arrive after purchase. The conceptual move from "your phone gets updates" to "your phone hosts a substrate-aware capability declaration" is small.

Fourth, **personalization data is naturally rich**. The kind of structure that Imprinting can extract on a phone — usage patterns, language preferences, navigation habits, accessibility settings — is data the device already has and that the user has already accepted being processed locally.

Fifth, **migration is a natural user behavior**. Users move from old phones to new phones routinely. The Adapter story (capability moves across substrates with a translation step) maps directly onto an action users already perform.

No other category in the installed base aligns this many components. Smartphones are not the only deployment target the protocol can serve, but they are the deployment target on which every protocol mechanism has the cleanest evaluation surface.

### 7.2 The Five-Year Phone in 2026

Consider, abstractly, a five-year-old smartphone in active use today. It carries TEE-class secure execution. It runs a recent operating system that supports modern model formats. Its NPU is several generations behind the current frontier; its memory is a fraction of the latest devices; its energy envelope precludes large model inference at competitive token rates.

Under current industry defaults, this device has two futures. Either it gets retired because newer capabilities cannot reach it, or it limps along on capability promises that progressively fail to match what the user was told at purchase. Both futures are wasteful, and both are recurrent.

The meta-protocol offers a third future. The device declares its actual Phenotype: which capabilities it can run Natively, which can run only Wrapped, which exceed its observer class entirely. Its TEE attests that those declarations are honest. The device does not pretend to support what it cannot, and the protocol does not let it. In return, the device receives capabilities sized to its substrate and accumulates Imprinted local value across its remaining operational life.

### 7.3 What Imprinting Would Look Like on a Phone

Concretely, on this device, Imprinting accumulates a few classes of structure: a model of the user's communication patterns, a model of the device's interaction with specific applications, a model of when and how the device is used, a model of the local network environment. This structure is held in TEE-protected local state, attested but not exfiltrated.

The capability that uses this structure is not a smaller, dumber version of a cloud-class assistant. It is a capability that knows this user better than any cloud-class assistant could, because it sees data the cloud will never see. It cannot generalize to other users. It does not need to. The Imprinted value is local by design.

### 7.4 The Migration Question

Eventually, the user replaces the device. The protocol mechanism that addresses this is the Adapter layer, treating cross-device migration as a form of cross-class translation. Imprinted state from the old device migrates to the new device in a form the new device can honestly run, attested by both endpoints' TEEs.

This part is currently a draft of the Adapter design with no production implementation — what is described here is **target behavior**, not delivered capability.

The target behavior is: the protocol does the translation, attestation, and state transfer at the edges, with no requirement that a cloud holds the user's history during the transition — the migration story users already expect.

### 7.5 Carrier and OEM Implications

The structural implication for the participants in the smartphone industry is that capability becomes a property the device can carry across vendors and OS versions, rather than a property the OEM controls through release management. This is uncomfortable for any OEM whose business model depends on capability being a release-management lever. It is constructive for any OEM whose business model depends on hardware quality, integration, or distribution.

The meta-protocol does not require OEM cooperation to succeed at the smartphone vertical, but it works far better with than without. The thesis for OEMs is straightforward: a meta-protocol-aware device is a more honest product, with longer effective lifespan and a clearer relationship between hardware investment and capability delivery.

---

## 8. Sector-by-Sector Candidacy with Honest Layering

### 8.1 The Implementation Honesty Section

This section lists candidate sectors for meta-protocol-on-hardware deployment. Before listing them, the protocol's current implementation state must be stated explicitly, because every candidacy claim must be readable against an honest description of what the protocol can already do, what it is engineering, and what remains research.

**Already implemented (publicly available)**: Gene compilation, Phenotype declaration, Fidelity rating (Native / Hybrid / Wrapped), Cloud Registry publication and discovery, local Arena ranking, dual-metric fitness evaluation `F(g)` and security verification `V(g)`, the L0 Kernel trust-backend abstraction with multiple admitted backends, three companion papers establishing the philosophical, architectural, and methodological basis. These are visible in the public protocol specification and in the publicly distributed implementation.

**Currently being engineered**: the protocol's local-adaptation interface and its associated memory architecture; the L4 collective-immunity layer; the Cloud Binding's full feature set; cross-Binding federation reconciliation. These are described in the protocol's design documents and are scheduled for delivery against the protocol's near-term version track.

**On the longer-horizon track**: real Edge and TEE Bindings; the L2/L3 market and negotiation layers in their full form; the protocol-network scale extensions for very large node counts; specialized binding spec work for verticals such as automotive infotainment. These represent multi-quarter to multi-year work and are not promised on a near-term timeline.

This three-tier honest layering is the substrate against which every candidacy in §8.2–§8.7 must be read. A sector being listed here does not imply the protocol is ready to support its production deployment today. It implies the sector is structurally amenable to the meta-protocol's architecture and that engagement at the appropriate engineering tier is invited.

### 8.2 Smartphones (Anchored Above)

Treated in detail in §7. Listed here for completeness as the primary anchor for SAM-level evaluation of the meta-protocol on hardware. Engagement tier: research collaboration; reference Binding design; OEM dialogue.

### 8.3 Smart Speakers and Home Devices

Smart speakers, smart displays, and home gateway devices represent the densest residential deployment of always-on edge computation. Their Phenotype is bounded and their Imprinting potential is high — these devices already model household routines as a side effect of operation. Their TEE status varies by generation and vendor, but the trend is upward. Engagement tier: open-source reference implementations; community-driven Binding sketches; integration through existing smart-home protocols.

### 8.4 Industrial IoT

Industrial IoT spans a spectrum from heavily constrained sensor nodes to fully capable industrial gateways. The high-value end of that spectrum — gateways, controllers, machine-monitoring units — increasingly includes secure-boot pipelines and TEE-class isolation. The Phenotype declaration model is particularly natural in industrial settings, where integrators routinely need to know exactly what a piece of edge equipment claims to do and under what conditions. Engagement tier: pilot deployments through industrial integrators; standards-track engagement; safety-domain consultation.

### 8.5 Connected Vehicles (Infotainment Domain Only)

This document explicitly limits its automotive treatment to the infotainment domain. ADAS and other safety-critical domains are excluded from the present discussion; those domains require a separate analysis under functional-safety frameworks (such as ISO 26262) that the meta-protocol does not address and is not designed to replace.

Within the infotainment domain, vehicles present the longest-lifecycle deployment in the consumer-facing installed base. Drivers keep vehicles for ten to twenty years. The drift between purchased capability and current capability is most user-visible in this category. The infotainment domain's TEE-class isolation is increasingly standard. Engagement tier: long-cycle engagement with Tier-1 suppliers; research-grade reference Binding; protocol-layer participation in industry consortia.

### 8.6 White-Goods AI

Smart appliances — refrigerators, ovens, washing machines, climate systems — operate on lifecycles that exceed even vehicles. The product-level promise of "AI features" in this category has historically had the weakest substrate accountability, because the install base is enormous and capability claims are minimally policed. Meta-protocol-style declaration is a particularly strong fit. Engagement tier: white-paper-stage discussion; selective pilot through interested OEMs; long-horizon standards work.

### 8.7 Industrial Robots and Cobots

Industrial robots and collaborative robots represent the high end of the embedded compute spectrum, with computational budgets that often exceed mid-range consumer devices. Their TEE adoption is mixed but trending. The unique structural property is that capability composition matters more here than in any other sector — a robot's value derives from coordinated capabilities, not from any individual one. The protocol's Composition primitives are particularly relevant. Engagement tier: research partnerships; reference Binding work for selected platforms.

### 8.8 Candidacy Checklist

For readers attempting to evaluate whether their own product or sector is a meta-protocol candidate, five questions form the practical checklist:

1. Does the product include hardware capable of supporting TEE-class isolation, even if it is not currently exercised?
2. Does the product have a long enough operational lifecycle that capability drift between purchase and current state is visible to users?
3. Does the product accumulate user-specific or environment-specific structure that a local-adaptation mechanism could plausibly compress into improved local capability?
4. Does the product have any cross-device knowledge-transfer story today, formal or informal, that benefits from a substrate-aware mediation layer?
5. Is the OEM open to capability declarations becoming inspectable rather than purely controlled by release management?

A "yes" to four of five questions is a strong indicator of meta-protocol candidacy. A "yes" to all five suggests early engagement is worth a conversation.

---

## 9. The Hundred-Billion-Node Endgame

### 9.1 Why the Endgame Is Not a Million Nodes

For most distributed systems, an endgame node count of one million is already ambitious. For the meta-protocol envisioned here, it is the wrong order of magnitude. The trillion-device installed base implies that any successful meta-protocol layer will eventually host node counts in the tens to hundreds of billions, when participation is counted by individual computationally capable instances rather than by participating organizations.

This is not a forecast about adoption rates. It is a constraint on architecture. A protocol whose mechanisms degrade above a million nodes is structurally incapable of becoming the installed base's coordination layer, regardless of adoption.

### 9.2 The Four-Layer Protocol Stack at That Scale

Rotifer's protocol-network design has been architected against this scale constraint. The four layers — referred to internally as Exchange, Foraging, Colony, and Evolution — are defined to operate without globally centralized state at any layer. Direct point-to-point execution at L1, gradient-search-based capability discovery at L2, self-organizing affinity clusters at L3, and hierarchical gossip-based ecosystem signals at L4 are each chosen because they retain coherent semantics at billion-node scales where centralized alternatives do not.

The implementation work to instantiate this design is multi-year and not the subject of this report. The architectural commitment to the design — the decision to build for that endgame rather than for a more comfortable smaller scale — is what allows §1–§8 to be made coherently.

### 9.3 What "Privileged Node" Means and What It Does Not

The Foundation operates infrastructure that participates in the protocol network. That infrastructure may serve a meaningful share of overall traffic at any given moment. None of that makes the Foundation a *platform* in the sense familiar from current internet incumbents.

The protocol's design treats Foundation-operated infrastructure as a privileged node — privileged in capacity, in centrality, in early-adopter access — but not as a *necessary* node. A privileged node is one whose disappearance would cause a transient performance regression but not a structural outage. A platform is one whose disappearance would cause the system to collapse. The architectural commitment is that the meta-protocol must remain in the privileged-node category and never drift into the platform category.

This matters because the alternative — a meta-protocol that requires its originating organization to remain operational and well-behaved indefinitely — has no historical example of long-term success at internet scale.

### 9.4 The Foundation's Role and What the Foundation Will Never Be

Rotifer Foundation maintains the protocol's specification, operates a Cloud Binding, and seeds early ecosystem development. That is its role. What the Foundation will not become, by architectural commitment, is the only legitimate operator, the gatekeeper of capability registration, the issuer of permissions, or the arbiter of what is allowed to participate.

The success criterion for the Foundation, paradoxically, is that the protocol becomes important enough for the Foundation itself to be replaceable. The most successful version of this story is one in which other privileged nodes — operated by partners, by communities, by competitors, by entities the Foundation has no relationship with — operate alongside the Foundation's node and the protocol thrives without distinguishing between them.

To be explicit: in the early protocol phase, the Foundation continues to carry critical engineering coordination and specification maintenance responsibilities. *"Replaceable"* is a long-term success marker, not a current state.

This is the open-protocol stance — HTTP outlasted its original commercial supporters because the protocol's value migrated away from any single party. The meta-protocol layer for distributed intelligence requires the same humility from its originating organization.

---

## 10. Open Questions, Falsifiability, How to Engage

> **Companion Blog Cross-Reference**: This section lists five open questions; readers may also consult the companion blog post *Where Should AI Capability Live?* §10, which articulates a complementary short-list around cross-TEE attestation, Phenotype-versus-behavior divergence, Imprinting migration fidelity, and long-term meta-protocol governance.

### 10.1 Five Open Questions

The argument of this paper rests on commitments that are not all settled. Five questions remain open and active.

**TEE heterogeneity.** The five major TEE families currently in deployment do not interoperate at the protocol layer. Bridging them via the Adapter layer is technically tractable but operationally non-trivial. The shape of the cross-TEE attestation story is the most concrete near-term open question.

**Export controls and regional regulation.** Some TEE implementations are subject to export-control regimes that vary by jurisdiction. A meta-protocol that depended on any single TEE family would inherit those constraints. The protocol's design assumption is that TEE-family neutrality through the Adapter layer makes the meta-protocol resilient to regulatory variation; that assumption needs to be tested operationally.

**Phenotype evaluation cost.** A capability declaration is only as useful as it is enforceable. Continuous evaluation of Phenotype claims against actual runtime behavior carries non-trivial computational overhead. Whether the overhead is acceptable in production deployments is not yet established and will be one of the signals the protocol's Petri Challenge experiment is designed to surface.

**Cross-class translation fidelity bounds.** Adapters translate capabilities across substrate classes, but the protocol does not yet have a formal characterization of what is preserved, what is lost, and under what conditions translation is unsafe. The information-theoretic framework of §3 suggests an approach; the empirical work has not been done.

**Governance structure of a cross-vendor meta-protocol network.** As the network grows, the governance question — who decides what becomes part of the protocol, who arbitrates disputes, how new privileged nodes are recognized — will become as important as the technical design. The protocol's specification includes a governance track; the operational practice is in early stages.

### 10.2 What Would Falsify This Report's Central Claim

The central claim of this report is that TEE × meta-protocol is the architectural path through which the trillion-device installed base can become first-class participants in distributed intelligence. Three classes of empirical outcome would falsify this claim or significantly weaken it.

If the protocol's local-adaptation mechanism, when deployed at scale on Capable Edge hardware, fails to produce stable convergence — if Imprinting state degrades faster than it accumulates — then the substrate-aware vocabulary outlined in §6 fails to deliver its promised value, and the architectural conclusion of this paper requires revision.

If TEE-rooted attestation, when stress-tested at the integration scale this paper proposes, exhibits failure modes that the Adapter layer cannot bridge, then the "physical entry point" claim of §4 collapses into a "trust backend among others" claim, and the strategic priority elevation does not survive.

If the privileged-node architecture of §9 produces operational realities indistinguishable from a platform architecture — if, in practice, the Foundation's node becomes the only viable place to run the protocol — then the open-protocol stance fails on its own terms, and the meta-protocol regresses into a vendor-owned layer despite its design intent.

These are real risks. They are stated explicitly because they are the conditions under which empirical experience would teach the protocol's contributors that the present analysis requires revision.

### 10.3 The Implementation Gap

The honest reading of §8.1 is that the protocol's current implementation lags this paper's argument. The mechanisms required to deliver the meta-protocol-on-hardware story — local adaptation, cross-Binding federation, real Edge/TEE Bindings, attested capability declaration — are at varying stages of design, engineering, and roadmap. Some are publicly available today. Some are months out. Some are years out.

The paper is being released ahead of full implementation because a methodology and architectural framework benefits from public critique before its first measurement is produced. The reader should evaluate the argument on its own terms, not on the implementation state. The implementation track will catch up; this paper will be revised when it does.

### 10.4 How to Engage

For readers who find the argument worth engaging with, four channels exist.

**Open-source community.** The protocol's specification, reference implementations, and companion papers are publicly available under permissive licenses. Implementation feedback, specification review, and Adapter contributions are welcome.

**Academic collaboration.** The information-theoretic framework underlying §3, the Capable Edge profile of §5, and the cross-class translation analysis of §6 each connect to active research traditions. The Foundation invites collaboration from population biologists, complex-systems theorists, mechanism designers, information theorists, and embedded-systems researchers whose tools we have adopted in this synthesis.

**Binding co-development.** The protocol's longer-horizon track includes Binding work for which OEM, Tier-1, and integrator participation is the only realistic engineering path. Conversations on this track do not assume immediate commercial commitments; they are about the shape of a Binding spec that could, on a multi-year horizon, support production deployment.

**Early ecosystem participation.** Investors, integrators, and platform operators interested in supporting the formation of a non-vendor-owned meta-protocol layer are invited to engage. The Foundation's commercial strategy is structured around being a privileged node within an open ecosystem rather than a platform that captures the ecosystem's value.

The protocol's contribution to distributed intelligence is not a product. It is a substrate. Substrates succeed by becoming things their originators do not control.

---

## References

[1] Rotifer Foundation. (2026). *Rotifer Protocol Specification*. Rotifer Foundation.

[2] Rotifer Foundation. (2026). *The Philosophy of Digital Evolution* (v1.2). Rotifer Foundation. CC BY-SA 4.0.

[3] Berners-Lee, T., Fielding, R., & Frystyk, H. (1996). *Hypertext Transfer Protocol — HTTP/1.0* (RFC 1945). Internet Engineering Task Force.

[4] Postel, J. (1981). *Transmission Control Protocol* (RFC 793). Internet Engineering Task Force.

[5] Sabt, M., Achemlal, M., & Bouabdallah, A. (2015). Trusted Execution Environment: What it is, and what it is not. *IEEE Trustcom/BigDataSE/ISPA*, 1, 57–64.

[6] Costan, V., & Devadas, S. (2016). *Intel SGX Explained*. IACR Cryptology ePrint Archive, Report 2016/086.

[7] Finzi, M., Qiu, S., Jiang, Y., Izmailov, P., Kolter, J. Z., & Wilson, A. G. (2026). From Entropy to Epiplexity: Rethinking Information for Computationally Bounded Intelligence. *arXiv preprint arXiv:2601.03220*. *(Note: cited as an arXiv preprint at time of writing; verify the final arXiv ID and version before public release.)*

[8] Polanyi, M. (1966). *The Tacit Dimension*. Doubleday & Company.

[9] Hassabis, D. (2024). *Accelerating Scientific Discovery with AI*. 2024 Nobel Prize Lecture in Chemistry, December 8, 2024. Stockholm, Sweden.

[10] Rotifer Foundation. (2026). *The Philosophy of Digital Evolution* (v1.2), §2.4 *Information-Theoretic Foundations: Epiplexity and the Computationally Bounded Observer*.

[11] Cover, T. M., & Thomas, J. A. (2006). *Elements of Information Theory* (2nd ed.). Wiley-Interscience.

[12] Mayr, E. (2001). *What Evolution Is*. Basic Books.

[13] Anderson, R. (2020). *Security Engineering: A Guide to Building Dependable Distributed Systems* (3rd ed.). Wiley.

---

**© 2026 Rotifer Foundation. This document is released under CC BY-SA 4.0.**

**Companion Materials:** The Philosophy of Digital Evolution · Rotifer Protocol Specification.
