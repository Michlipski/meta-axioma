# Generation 3b Formal Axiom & Invariant Registry (`generation_03b_axioms.md`)

> **System:** Generation 3b ($G_{3b}$) — The Autonomous Universal Systems Compiler  
> **Architecture:** Hybrid Deterministic FSM + Fractal Task Stack + Dual-Model Cognitive Router  
> **Verification Status:** 100% Certified on Python 3.14 (`39/39` tests passing across Milestones 1–4)  

---

## 1. Foundational Waterloo & Epistemic Invariants

* **`[L1-G3B-000]` The Situation of Concern Normalization Invariant:**
  Regardless of entry tier (Tier 1 SoC, Tier 2 Pitch, Tier 3 Reference Product), compilation cannot proceed to concept synthesis until a formal, solution-agnostic Tier 1 Situation of Concern (`SituationOfConcern`) has been reconstructed, stripped of solution bias, and certified via `SoCNormalizer`.
* **`[L1-G3B-008]` Distributed Topology & Consensus as First-Class IR:**
  Cluster nodes, network channels, latency budgets, and Sheaf-Quorum consensus contracts are modeled as first-class citizens in `TopologyIR`.
* **`[L1-G3B-009]` Thermodynamic Capital Invariant (60/40 Partition):**
  Every compilation budget (Option C: $600,000$ tokens) strictly partitions $60\%$ Exploratory Capital ($360,000$ tokens) and $40\%$ Protected Capital ($240,000$ tokens reserved exclusively for terminal verification sinks), grounded in BPE physical token measurement (`PhysicalTokenMeter`) and Landauer bit-erasure dissipation ($Q = k_B T \ln 2 \cdot \text{bits}$).

---

## 2. Hostile Zero-Trust & Anti-Phantom Invariants

* **`[NEG-G1B-001]` / `[L1-G3B-010]` The Anti-Phantom Execution Witness:**
  Simulated in-memory completion is strictly forbidden (`PhantomEmissionViolation`). Every compiled system must emit non-zero-byte files to disk and pass its generated `unittest` suite in a live Python 3.14 subprocess with `exit_code == 0` and non-zero passing assertions (`PostEmissionExecutionFailure`).
* **`[L1-G3B-011]` The Semantic Consumer Invariant (Round-Trip Fidelity):**
  All Intermediate Representations (`StatechartIR`, `ContractIR`, `TopologyIR`) enforce lossless round-trip serialization ($f^{-1}(f(x)) == x$) and formal compositional verification (`ContractProofWitness`).
* **`[L1-G3B-012]` The Topological Fidelity Invariant (Anti-Loopback Gate):**
  Multi-node distributed topologies are strictly forbidden from binding to single-machine loopback interfaces (`127.0.0.1`, `localhost`, `::1`), raising `TopologicalLoopbackViolation`.
* **`[L1-G3B-013]` The Empirical Observation Invariant (No Phantom Journey Steps):**
  E2E journey steps in `HeadlessJourneyWalker` must demonstrate a non-empty observable state delta ($\Delta(\text{state}) \ne \emptyset$), raising `PhantomJourneyStepViolation` on zero-delta steps, while enforcing Steps-to-Value ($\le 3$) and Functorial Undo (`[L1-002]`).

---

## 3. Escrow Architecture & Quine Crucible Invariants

* **`[L1-G3B-014]` Cognitive Routing Invariant (Dual-Model LLM Router):**
  Enforced mechanically by `DualModelRouter`:
  - **The Brain (`Gemini 4 Argon`):** Exclusively reserved for the outer deterministic FSM orchestrator, Waterloo SoC normalization, dialectical architecture decomposition, and all Zero-Trust Evaluators (`checker.py`, `journey_walker.py`, `micro_auditors.py`).
  - **The Muscle (`Gemini 3.8 Flash`):** Exclusively utilized for indivisible primitive leaf-node synthesis on the task stack. Cross-tier routing raises `CognitiveRoutingViolation`.
* **`[L1-G3B-015]` Stack Purity & Bounded Recursion Invariant:**
  `FractalTaskStack` is an explicit, deterministic LIFO data structure managed solely by the outer FSM. Subagents never invoke other subagents; non-leaf agents return only schema-validated `DecompositionPlan`s bounded by recursion depth ceiling $d_{\max}$ (`StackRecursionDepthViolation`) and branching ceiling $b_{\max}$ (`StackBranchingCeilingViolation`).
* **`[L1-G3B-016]` Zero-Bypass Interception & Self-Healing Circuit Breaker:**
  Zero leaf artifacts emitted by Gemini 3.8 Flash may be committed without a passing `MicroAuditResult` from `ZeroTrustMicroAuditorRegistry` (`ZeroBypassInterceptionViolation`). Failed leaves undergo isolated Argon-governed Flash retries with exponential backoff up to `max_retries` before tripping `LeafRemediationCircuitBreakerError`.
* **`[L1-G3B-017]` Zero-Template IR-Driven Emission & Daughter Isolation Protocol:**
  `DynamicCodeEmitter` synthesizes executable code directly by walking the verified `ContractIR`, `StatechartIR`, and `TopologyIR` object graphs. Reflexive self-compilation is proven by emitting a self-hosting Daughter Compiler ($G_{3b}'$) into an isolated sandbox, booting it in a separate subprocess (`compile_seed.py`), compiling a novel Tier 1 SoC into a tested downstream application, and sealing a SHA-256 hash-chained `CryptographicTelemetryEngine` ledger.
