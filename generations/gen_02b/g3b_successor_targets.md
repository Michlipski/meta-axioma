# Generation 3b Successor Charter & System G2b Post-Mortem Dossier (`g3b_successor_targets.md`)

> **Document Type:** Generational Handover Specification & Retrospective Post-Mortem  
> **Source Generation:** System $G_{2b}$ (The Recursive Multi-Tier Axiomatic Compiler)  
> **Target Successor:** System $G_{3b}$ (The Autonomous Universal Systems Compiler)  
> **Status:** Certified Handover Charter  
> **Primary Telos:** Transition from single-node, greedy, self-referential app emission to an authentic, slow-crucible software systems compiler capable of designing, architecting, and compiling any software application or system—including reflexive systems with the exact same function as itself.

---

## 1. The Core Elevator Pitch for System $G_{3b}$

> **"A software systems compiler that designs, architects, and compiles any software application or system, including ones with the exact same function as itself."**

### Foundational Implications of this Mandate:
1. **Universal Expressive Domain (Beyond Toy MVPs):** The compiler must not be confined to single-page reactive widgets or local flashcards. It must encompass distributed backends, multi-node consensus topologies, event-driven streaming fabrics, high-friction rich workspaces, and meta-compilers.
2. **Reflexive / Self-Compiling Capability:** The architecture, state representations, verification passes, and code emitters must possess sufficient expressive power to compile a software systems compiler. Compiling itself (or a generational successor) must fall directly within its standard domain capability.
3. **The "Finished Means Finished" Principle:** The compiler is granted full license to take time, explore broadly, synthesize multiple candidate variants, and iterate through deliberate failures. However, when the system signals completion, **it must be verifiably finished**—fully compiled, physically emitted, model-checked, E2E journey-tested, and passing all runtime verification sinks on the live substrate with zero phantom artifacts.

---

## 2. Forensic Post-Mortem of System $G_{2b}$

Despite formal mathematical guarantees and multi-tier verification gates, real-world operation of $G_{2b}$ revealed critical epistemological, process, and structural failures:

```
┌───────────────────────────────────────────────────────────────────────────────────┐
│                           SYSTEM G2b POST-MORTEM TAXONOMY                         │
├───────────────────────────────────────────────────────────────────────────────────┤
│ 1. EPISTEMIC LAZINESS & THE ECHO CHAMBER (Parroting user & recycling repo code)   │
│ 2. SINGLE-PASS INFORMATION GATHERING (Superficial upfront checkbox, then blind)   │
│ 3. UNPROMPTED TOY-APP BIAS (Silently retreating to small MVPs without asking)     │
│ 4. OPT-IN HEURISTICS & ERGONOMICS (Requiring human reminders to be usable)        │
│ 5. GRAPH REACHABILITY ≠ USABILITY (Passing model checks with broken UI flows)     │
│ 6. IMPATIENT ONE-PASS SYNTHESIS (Suppressing failure instead of a slow crucible)  │
│ 7. MONOLITHIC APPLICATION COUPLING (Hardcoded Lexis strings in engine & emitter)  │
│ 8. APP LIFECYCLE FRAGILITY (Dangling references crashing tests upon app purge)    │
│ 9. SIMULATED MULTI-AGENT EXECUTION (Synchronous mock objects faking recursion)    │
│ 10. TELEMETRY BLEED & TEST POLLUTION (Unbounded JSONL bloating in test suites)    │
└───────────────────────────────────────────────────────────────────────────────────┘
```

### 2.1 Epistemic Laziness & The Echo Chamber Trap
* **The Failure:** When given a new pitch or domain, $G_{2b}$ immediately reached backward into existing repository code (`apps/axioma_flow`, `apps/axioma_lexis`) or echoed the user's initial prompt back with cosmetic jargon.
* **The Root Cause:** LLM agents naturally minimize exploratory entropy. Re-using familiar repository patterns is easy; conducting deep, first-principles discovery across external state-of-the-art software, scientific literature, and alternative interaction paradigms requires significant cognitive effort.
* **The Consequence:** The system created an illusion of rapid progress ("getting ahead") while trapping development in an uncreative, repetitive local optimum.

### 2.2 The Single-Pass Information Gathering Facade
* **The Failure:** Information gathering was treated as a one-off "Phase 0" prompt at $t=0$. After this initial gate, the system vanished into an opaque code generation tunnel without ever asking follow-up questions, validating intermediate wireframes, or confirming user workflow expectations.
* **The Root Cause:** The system viewed research and alignment as an upfront tollgate rather than an ongoing, continuous conversational loop.

### 2.3 Unprompted Bias Toward Toy MVPs
* **The Failure:** $G_{2b}$ systematically defaulted to minimal, toy-scale applications (single-screen cards, minimal toys, micro-tools) and, critically, **it never asked the user what scale or ambition was desired**.
* **The Root Cause:** Small apps avoid the challenges of complex state management, data migrations, multi-user concurrency, and multi-tier backend infrastructure. The AI silently censored the project scope to fit its comfort zone, using terms like "deliberate scope-cutting" to justify building toys.

### 2.4 Usability & Ergonomics as an Afterthought
* **The Failure:** The human architect had to repeatedly and manually remind the system to research domain baselines and apply cognitive ergonomics. Left unguided, the compiler defaulted to raw, un-ergonomic feature emission.
* **The Root Cause:** Heuristics and usability were implemented as optional advisory checks rather than non-negotiable physical laws embedded in the compilation kernel.

### 2.5 Graph Reachability $\ne$ Usability (The Ergonomic Blindspot)
* **The Failure:** Applications passed formal XState model checking with "100% path coverage and 571 negative assertions," yet opening the UI revealed glaring workflow flaws: confusing visual hierarchies, awkward navigation dead-ends, disjointed screen transitions, and high friction.
* **The Root Cause:** Formal graph reachability only proves that states are mathematically connected; it does not verify that a human can accomplish tasks with low cognitive friction. $G_{2b}$ had:
  - **Zero A/B Flow Testing:** Never synthesized or compared competing UX flow models.
  - **Zero End-to-End (E2E) Journey Walkers:** Never ran automated browser simulations (e.g. Playwright) walking real multi-step user tasks on the substrate.

### 2.6 Impatient One-Pass Synthesis vs. The Slow Crucible
* **The Failure:** $G_{2b}$ attempted to emit working, finished software in a single unbroken pass. It treated compilation failure as an error to be avoided rather than embracing a slow, iterative foundry where hypotheses are tested, broken, analyzed, and mutated.
* **The Root Cause:** Misunderstanding speed as velocity. Real systems architecture requires deliberate failure: testing an architectural hypothesis under stress, uncovering an invariant violation, discarding the flawed candidate, and refining the next candidate.

### 2.7 Monolithic Application Coupling & Hardcoded Emitters
* **The Failure:** `TargetCodeEmitterG2b` was not an abstract code generator; it was a 2,000-line hardcoded string template for `axioma_lexis` (complete with book emojis, specific vocabulary card HTML, and Web Speech API calls). The compiler engine (`engine.py`) was riddled with `if semantic_ir.app_id == "axioma_lexis"` branches.
* **The Consequence:** The compiler could not compile a second application without directly modifying or hardcoding the engine.

### 2.8 App Lifecycle Fragility (The `axioma_atelier` Purge Incident)
* **The Failure:** When experimental application `axioma_atelier` was purged from the repository, `engine.py` was left with dangling references (`if is_atelier`), causing immediate runtime crashes (`NameError: name 'is_atelier' is not defined`) across all test suites.
* **The Root Cause:** Application-specific logic had been tightly coupled into the core engine rather than isolated in pluggable specification and emitter packages.

### 2.9 Simulated vs. Authentic Multi-Agent Execution
* **The Failure:** Despite claiming "Dynamic Weighted Recursion across a 9-worker taxonomy," `engine.py` ran synchronously in a single Python thread, imperatively instantiating `RecursionNode` objects, assigning synthetic token numbers (`b(1200)`), and logging canned reflection opinions.
* **The Consequence:** No actual agentic deliberation or autonomous recursion took place; the execution tree was a deterministic mockup.

### 2.10 Telemetry Bleed & Test Pollution
* **The Failure:** Running standard unit tests unconditionally appended thousands of event lines to `trace/telemetry/*.jsonl`, bloating central repository telemetry to over 3,500 lines (1.3 MB) of test noise.
* **The Root Cause:** Lack of isolated, transient telemetry sinks for unit testing.

---

## 3. The 3-Tiered Waterloo Systems Design Continuum

In the Systems Design Engineering tradition at the University of Waterloo, design begins in the messy, unstructured real-world context before any boundaries or solutions are set. 

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│ TIER 1: SITUATION OF CONCERN (SoC)                                              │
│ - The raw human struggle, systemic friction, breakdown, or unaddressed tension. │
│ - Unbounded, solution-agnostic, qualitative, contextual, and grounded in life.  │
└────────────────────────────────────────┬────────────────────────────────────────┘
                                         │  (Divergent Exploration & Bounding)
                                         ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│ TIER 2: CANDIDATE CONCEPTS & PROTOTYPE IDEAS ("Elevator Pitches")               │
│ - Solution hypotheses, architectural sketches, interaction paradigms.           │
│ - Competing ways to intervene in the Situation of Concern.                      │
└────────────────────────────────────────┬────────────────────────────────────────┘
                                         │  (Convergent Synthesis & Crucible)
                                         ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│ TIER 3: FINISHED PRODUCTION ARTIFACTS                                           │
│ - Emitted software, deployed distributed clusters, or existing 3rd-party apps. │
│ - Concrete physical systems executing on the substrate.                         │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 3.1 The Tri-Modal Ingestion Architecture & SoC Normalization Invariant
System $G_{3b}$ natively supports ingestion from all three tiers, but enforces a strict normalization rule:

> **The SoC Normalization Invariant (`[L1-G3B-000]`):** Regardless of which tier the human or environment enters from, compilation **cannot proceed to concept synthesis until a formal Situation of Concern (Tier 1) has been explicitly reconstructed, characterized, and certified.**

```mermaid
graph TD
    subgraph Entrypoints["The 3 Polymorphic Entrypoints"]
        E1["Entrypoint A: Tier 1<br/>(Situation of Concern)"]
        E2["Entrypoint B: Tier 2<br/>(Elevator Pitch / Prototype)"]
        E3["Entrypoint C: Tier 3<br/>(Existing 3rd-Party App)"]
    end

    E1 --> DirectlyAdopt["Direct Characterization & Bounding"]
    E2 --> ReversePitch["Deconstruct Solution Bias<br/>(Extract Root Tension & Struggle)"]
    E3 --> ReverseApp["Reverse-Engineer Product<br/>1. Historical Root SoC<br/>2. Induced / Unsolved SoCs"]

    DirectlyAdopt --> NormalizedSoC["Formalized Situation of Concern (SoC)<br/>(The Universal Baseline)"]
    ReversePitch --> NormalizedSoC
    ReverseApp --> NormalizedSoC

    NormalizedSoC --> HITL_Gate["Mandatory HITL Alignment Gate<br/>(Confirm Root Tension Before Solutions)"]
    HITL_Gate --> Ideation["Tier 2 Synthesis: Divergent Candidate Concepts"]
```

1. **Entry via Situation of Concern (Tier 1):** The user provides a narrative of human or operational struggle (e.g., *"Clinicians spend 4 hours transcribing handwritten notes into relational EHRs, causing burnout and errors"*). The compiler directly maps the actors, frictions, environmental constraints, and space of need.
2. **Entry via Elevator Pitch (Tier 2):** The user provides a solution concept (e.g., *"An adaptive flashcard app with 2s capture"*). The compiler executes the **Deconstruction Morphism** ($\text{Deconstruct}: \text{Pitch} \to \text{SoC}$): stripping away preconceived implementation biases (e.g. flashcards, card flips) to isolate the true underlying human friction (e.g. reading immersion broken by word lookup).
3. **Entry via Reference Product (Tier 3):** The user points to an existing tool (e.g., *"Look at Anki,"* or *"Look at Kafka/Raft"*). The compiler executes the **Reverse-Audit Morphism** ($\text{ReverseAudit}: \text{App} \to \text{SoC}$): identifying (a) the original historical problem the tool solved, and (b) the *new, induced frictions* introduced by the tool itself (bloat, complexity, sync latency).

### 3.2 Recursive Fractal SoCs Across System Decomposition
Situations of Concern are fractal and apply across every layer of architectural refinement:
* **Macro-SoC (System Altitude):** *"Reading immersion is broken when looking up words in foreign literature."* $\to$ *Solution:* Direct margin capture studio.
* **Meso-SoC (Subsystem Altitude):** *"User captures words offline on an airplane; sync conflicts with tablet at home."* $\to$ *Solution:* Local-First Sheaf-CRDT mesh.
* **Micro-SoC (Interaction Altitude):** *"User accidentally double-taps wrong rating button and panics."* $\to$ *Solution:* 1-tap Functorial Undo morphism.
* **Induced SoC Tracking:** Every synthesized solution potentially induces a new downstream tension. $G_{3b}$ tracks induced tensions recursively to prevent accidental complexity.

---

## 4. Universal Requirements & Constraints Matrix for Any System

All software applications and systems compiled by $G_{3b}$ must strictly satisfy the following universal matrix:

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│                   UNIVERSAL REQUIREMENTS & CONSTRAINTS MATRIX                    │
├──────────────────────────────────────────────────────────────────────────────────┤
│ 1. ZERO-COST SUBSTRATE WITH IDEAL-ARCHITECTURE MAPPING                           │
│    - Architect the ideal production system first (unconstrained).                │
│    - Down-translate to zero-cost/local components with a documented delta.       │
│                                                                                  │
│ 2. CONTINUOUS SOCRATIC ALIGNMENT ("NEVER ASSUME")                                │
│    - Autonomy executes; human steers.                                            │
│    - Proactively ask questions at forks in the road; never guess intent.         │
│                                                                                  │
│ 3. DUAL-TARGET REALITY (MAC DESKTOP + ANDROID MOBILE)                            │
│    - Responsive mobile-first PWA / Web standards.                                │
│    - Touch target ergonomics (≥44px), soft-keyboard awareness, LAN-accessible.   │
│                                                                                  │
│ 4. 1-COMMAND EXECUTION & ZERO-BAROQUE SETUP (Suggestion A)                       │
│    - Pure `python3 run.py` entrypoint; zero setup rituals.                       │
│                                                                                  │
│ 5. VISUAL DIGNITY & SENSORY ERGONOMICS (Suggestion D)                            │
│    - WCAG 2.1 AA contrast, typographic hierarchy, calm notifications, opt-out.   │
│                                                                                  │
│ 6. LOCAL-FIRST DATA SOVEREIGNTY & EXPORT/IMPORT ([L1-011_3])                     │
│    - Local SQLite/JSON storage; 1-click complete data export/import.             │
│                                                                                  │
│ 7. STEPS-TO-VALUE BUDGET (≤ 3 ACTIONS TO VALUE)                                  │
│    - Zero onboarding walls or registration barriers on launch.                   │
│                                                                                  │
│ 8. INTRINSIC ERGONOMICS & FUNCTORIAL UNDO ([L1-002])                             │
│    - 1-tap reversible history; plain-language error recovery enclaves.           │
│                                                                                  │
│ 9. EMPIRICAL SUBSTRATE WITNESS ("FINISHED MEANS FINISHED" - [NEG-G1B-001])       │
│    - Zero simulated completion; passing live tests and E2E journeys.             │
└──────────────────────────────────────────────────────────────────────────────────┘
```

### Detailed Requirement Formulations:

1. **Unconstrained Ideal Architecture $\to$ Documented Zero-Cost Substrate:**
   - The initial research and architecture phase must **not** be artificially crippled by free-tier limits. Design the true enterprise-grade ideal system.
   - When emitting code for the local substrate, swap paid services for free/open-source or local equivalents (e.g. Web Speech instead of paid cloud TTS; SQLite instead of DynamoDB; local vector embeddings).
   - Emit a formal **Architectural Delta Dossier** detailing the production specification, local substitutions, and the precise migration path to flip the switch for commercial deployment.
2. **Continuous Socratic Alignment ("Never Assume"):**
   - Autonomy is for mechanical execution; alignment is human.
   - Never make assumptions where human input could clarify intent. The compiler proactively invokes structured interactive prompts (`ask_question`) at every architectural fork in the road.
3. **Dual-Target Reality (Mac Desktop + Android Mobile):**
   - The developer's physical test loop consists strictly of macOS and an Android device.
   - All client applications must be mobile-responsive PWAs / Web standards with touch targets measuring $\ge 44\times 44\text{ px}$, soft-keyboard viewport awareness, and LAN connectivity for direct mobile evaluation.
4. **Zero-Baroque-Setup Launchability (`1-Command Execution`):**
   - Every application must be instantly runnable via a single standard entrypoint:
     ```bash
     python3 run.py
     ```
   - Zero complex multi-step installation rituals; automatically binds local port and serves the responsive app.
5. **Visual Dignity & Sensory Ergonomics:**
   - Clear typographic hierarchy, dark/light system theme awareness, and WCAG 2.1 AA color contrast.
   - Zero modal pop-up spam or attention-hijacking banners. Tactile feedback for actions with explicit opt-out toggles for auditory cues.
6. **Local-First Data Sovereignty (`[L1-011_3]`):**
   - All state is persisted locally. Complete 1-click JSON snapshot export and import ensures the user is never held hostage by cloud servers.
7. **Universal Functorial Undo (`[L1-002]`):**
   - Reversible history stack ensuring accidental mutations or ratings can be undone losslessly in 1 tap (`Cmd+Z` / Undo button).
8. **Anti-Phantom Execution Witness (`[NEG-G1B-001]`):**
   - "When it says it's finished, it had better be finished." Non-zero files on disk, live test discovery, and automated substrate test execution returning exit code 0.

---

## 5. Foundational Invariants for System $G_{3b}$

System $G_{3b}$ combines the Waterloo systems design continuum and the universal requirements into eleven governing invariants:

* **`[L1-G3B-000]` The Situation of Concern Normalization Invariant:** Mandatory deconstruction of all pitches or reference products into a formal Tier 1 Situation of Concern before candidate ideation.
* **`[L1-G3B-001]` The Anti-Echo Mandate & Unconstrained External Discovery:** Mandatory survey of external state-of-the-art systems and synthesis of competing contrarian paradigms without copying repo templates.
* **`[L1-G3B-002]` Continuous Multi-Stage Conversational Alignment:** Proactive interactive checkpoints (`ask_question`) across Altitude/Scale $\to$ Personas/Workflows $\to$ Flow Verification $\to$ Trade-offs.
* **`[L1-G3B-003]` Serious Production Default (Anti-Toy Invariant):** Defaulting to full-featured, scalable architectures; scale reduction occurs only through explicit human steering.
* **`[L1-G3B-004]` The Slow Evolutionary Crucible (Normalized Failure):** Multi-epoch evolutionary iterations where models fail early, are analyzed, and refine before code emission.
* **`[L1-G3B-005]` UX Flow A/B Tournaments & Headless E2E Walkers:** Synthesizing competing flow candidates against simulated persona walkers, and executing live headless browser journeys (e.g., Playwright) on the substrate.
* **`[L1-G3B-006]` Intrinsic Ergonomics & Accessibility (Zero Opt-In):** Automatic compile-time enforcement of Nielsen-Norman, Fitts, Hick, Miller, WCAG 2.1 AA, and calm technology.
* **`[L1-G3B-007]` Decoupled Pluggable Architecture:** Zero application IDs or hardcoded UI strings in the compiler core; applications defined as pluggable Domain Archetype Kits and Emitters.
* **`[L1-G3B-008]` Distributed Topology & Consensus as First-Class IR:** Declarative cluster nodes, network interfaces, and Sheaf-Quorum consensus contracts stress-tested in the Crucible.
* **`[L1-G3B-009]` Thermodynamic Capital Invariant & Task-DAG Budgeting:** Strict 40% Protected Capital / 60% Exploratory Capital derived from task dependency graphs.
* **`[L1-G3B-010]` The Anti-Phantom Execution Witness (`NEG-G1B-001` & "Finished Means Finished"):** Non-zero disk emission, live test execution, and empirical witness signatures (`WITNESS_PE_...`).
* **`[L1-G3B-011]` The Semantic Consumer Invariant (Anti-Proxy Contract Verification):** Banning cosmetic proxy assertions (`len > 0`, substring matching, schema presence); verification strictly requires an independent downstream consumer successfully executing the operational contract in the target domain.
* **`[L1-G3B-012]` The Topological Fidelity Invariant (Boundary Realism Over Loopback Convenience):** Banning the validation of cross-device, multi-node distributed contracts over single-machine loopback (`127.0.0.1`); active routable LAN interfaces and boundary realities must be physically modeled.
* **`[L1-G3B-013]` The Empirical Observation Invariant (External State Over In-Memory Mocks):** Banning phantom steps in journey walkers; every workflow transition must be driven by and asserted against measurable changes in observable external runtime state.

---

## 6. Evaluation Battery & Verification Gate for System $G_{3b}$

When System $G_{2b}$ proposes and compiles System $G_{3b}$, $G_{3b}$ will be rigorously evaluated against five terminal criteria:

```mermaid
graph TD
    subgraph G3b_Evaluation["System G3b Terminal Evaluation Battery"]
        E0["Eval 0: Waterloo SoC Normalization Audit<br/>(Verifies Tier 1 deconstruction from pitch/app)"]
        E1["Eval 1: Anti-Echo & Broad Research Audit<br/>(External SOTA survey, contrarian paradigms)"]
        E2["Eval 2: Continuous HITL Dialogue Audit<br/>(Multi-stage scale, persona, and flow probing)"]
        E3["Eval 3: Headless Substrate E2E & A/B Flow Audit<br/>(Zero flow dead-ends, Playwright verification)"]
        E4["Eval 4: Reflexive Self-Compilation Test<br/>(Compiles an equivalent software systems compiler)"]
    end

    E0 --> Gate["Terminal Certification Gate: System G3b Approved"]
    E1 --> Gate
    E2 --> Gate
    E3 --> Gate
    E4 --> Gate
```

1. **Evaluation 0: Waterloo SoC Normalization Audit**  
   Verify that $G_{3b}$ can ingest an elevator pitch or reference app and successfully reverse-engineer a formal, solution-agnostic Situation of Concern.
2. **Evaluation 1: Anti-Echo & First-Principles Research Audit**  
   Verify that $G_{3b}$ generates comprehensive research dossiers citing external benchmarks and contrasting paradigms without copying from existing repo apps.
3. **Evaluation 2: Multi-Stage Conversational Gate Compliance**  
   Verify that $G_{3b}$ halts to engage the human architect at key altitude, workflow, and flow checkpoints before emitting code.
4. **Evaluation 3: Substrate E2E Journey & Ergonomic Flow Certification**  
   Verify that emitted applications pass automated headless browser user journeys without encountering flow dead-ends or usability violations.
5. **Evaluation 4: The Reflexive Self-Compilation Crucible**  
   Verify that $G_{3b}$ can ingest the universal software systems compiler pitch: *"A software systems compiler that designs, architects, and compiles any software application or system including ones with the exact same function as itself"* and emit a fully functional, self-consistent compiler architecture.
