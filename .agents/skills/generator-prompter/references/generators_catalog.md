# Meta-Axioma Generators & Compilers Catalog

This catalog outlines the active compilers and generators within Meta-Axioma. Prompts synthesized by the `generator-prompter` skill automatically tailor their constraints and execution gates to the selected generator.

---

## 1. System G2b Compiler (`generations/gen_02b/src/g2b_compiler/`)
- **Archetype:** Multi-Tier Axiomatic & Usability Compiler
- **Reference Apps:** `axioma_lexis`
- **Governing Invariants:**
  - `[L1-G2B-001]` Multi-Tier Interlocking Gate (Tier 1 structural $S_0$ axioms $\land$ Tier 2 universal usability heuristics $\land$ Tier 3 domain archetype benchmarks).
  - `[L1-G2B-002]` Stateful Human Override Governance (Audit registry in `trace/overrides/`, Heuristic Debt Index $\le 0.15$).
  - `[L1-G2B-003]` Dynamic Weighted Recursion (Worker taxonomy: Orchestrator 1.0x, ResearchWorker 0.5x, SynthesisWorker 1.0x, Terminal Verification Sinks 0.0x).
  - `[L1-G2B-004]` Thermodynamic Capital Partitioning (Strictly locks 40% Protected Capital for verification; leases 60% Exploratory Capital).
  - `[L1-G2B-005]` Ambitious Discovery & Deliberate Scope-Cutting Protocol.
  - `[NEG-G1B-001]` Anti-Phantom Emission Gate (Mandatory physical non-zero file emission and substrate test runner execution witness `WITNESS_PE_...`).
- **Prompt Formulation Requirements:**
  - Must enforce **Directive 3**: High-level plan (persona, JTBD, user flow, UX architecture) + dynamic project proposal options ($C_{\min} \dots C_{\max}$ with 40% protected capital).
  - Must enforce **Mandatory Approval Gate**: Require human confirmation via `ask_question` before low-level code emission.

---

## 2. System G1 Compiler (`generations/gen_01/src/g1_compiler/`)
- **Archetype:** Foundational Structural Invariant Compiler
- **Reference Apps:** `axioma_flow`, `axioma_dual_fsm`, `axioma_eink`, `axioma_swarm`
- **Governing Invariants:**
  - `L1-002`: Functorial Undo/Redo (reversible state transitions).
  - `L1-004`: Structural isomorphism.
  - `L1-011_3`: Decoupled State Persistence (state snapshot distinct from operational engine).
  - `L1-008`: Landauer Bounds (dissipation audit, bounded working memory).
  - `L1-015`: Dual-Boundary Contract (`nouns.json` data schema and `verbs.json` state transitions).
  - `L1-016`: Demarcated Exception Enclaves.

---

## 3. System G1b Compiler (`generations/gen_01b/src/g1b_compiler/`)
- **Archetype:** Ergonomic Micro-Interaction & Symmetrical Grid Compiler
- **Reference Apps:** `axioma_crossword`
- **Governing Invariants:**
  - `L1-G1B-001`: Two-tier state machine (grid coordinate state + solver input workbench).
  - `L1-G1B-002`: Responsive dual-column workbench and soft mobile keyboard.
  - `NEG-G1B-001`: Anti-phantom emission gate and runtime test execution.

---

## 4. System G2 Compiler (`generations/gen_02/src/g2_compiler/`)
- **Archetype:** Distributed Sheaf-CRDT Event Streaming & Coordination Fabric
- **Reference Apps:** `axioma_fabric`, `axioma_sentinel`, `portfolio`
- **Governing Invariants:**
  - `L1-G2-001`: Sheaf-CRDT local event sections and restriction morphisms.
  - `L1-G2-002`: Zero-ambient authority HMAC capability tokens.
  - `L1-G2-004`: Autonomous multi-process daemon health sentinel.
  - `L1-G2-008`: Fixed Landauer ring buffers for streaming telemetry.

---

## 5. System G3 Compiler (`generations/gen_03/src/g3_compiler/`)
- **Archetype:** Distributed Consensus, OpenTelemetry, & User Zero Grounding
- **Reference Apps:** `axioma_mesh`, `axioma_morphic`
- **Governing Invariants:**
  - `L1-G3-001`: Transitive sheaf-quorum consensus across mesh nodes.
  - `L1-G3-002`: Zero-trust capability delegation.
  - `L1-G3-004`: Enclave self-healing and CQRS event replay.
  - `L1-G3-006`: OpenTelemetry distributed trace context propagation.
  - Canadian accessibility (AODA/WCAG 2.1 AA) and Official Languages parity.

---

## 6. System G3b Compiler (`generations/gen_03b/src/g3b_compiler/`)
- **Archetype:** The Autonomous Universal Systems Compiler (Hybrid Deterministic FSM + Fractal Task Stack + Dual-Model Cognitive Router)
- **Reference Apps & Proofs:** `epoch_m4_hydro_valve`, `epoch_m4_quine_crucible` (`soc_system_g3b_quine` $\to$ `soc_biologics_cold_chain`)
- **Governing Invariants:**
  - `[L1-G3B-000]` Waterloo SoC Normalization (Deconstructs Tier 1/2/3 inputs into solution-agnostic `SituationOfConcern` hierarchies: `MACRO`, `MESO`, `MICRO`).
  - `[L1-G3B-009]` Thermodynamic Capital & `DynamicBudgetCalibrator` (60% Exploratory / 40% Protected Capital calibrated against Task-DAG BPE unit costs).
  - `[L1-G3B-011]` Universal & Hierarchical IR (XState v5 `StatechartIR`, Compositional `ContractIR` with `ContractProofWitness`, and `TopologyIR`).
  - `[L1-G3B-012]` Topological Fidelity (Anti-Loopback boundary realism for multi-node topologies).
  - `[L1-G3B-013]` Empirical Journey Observation (`HeadlessJourneyWalker` rejecting zero-delta phantom steps, enforcing Steps-to-Value $\le 3$ and `[L1-002]` Functorial Undo).
  - `[L1-G3B-014]` Dual-Model Cognitive Routing (Gemini 4 Argon Brain for FSM/evaluators vs. Gemini 3.8 Flash Muscle for indivisible leaf emission).
  - `[L1-G3B-015]` Stack Purity & Bounded Recursion (`FractalTaskStack` enforcing $d_{\max}$, $b_{\max}$, and BPE-weighted child capital partitioning).
  - `[L1-G3B-016]` Zero-Bypass Micro-Auditor Interception & Self-Healing (`ZeroTrustMicroAuditorRegistry` with exponential backoff retries).
  - `[L1-G3B-017]` & `[NEG-G1B-001]` Zero-Template IR-Driven Emission, Subprocess Test Verification, and SHA-256 Chained Cryptographic Telemetry (`telemetry_ledger.json` + `telemetry_dashboard.md`).

---

## 7. System G4b Compiler (`generations/gen_04b/services/builder/`)
- **Archetype:** Service-Oriented Sovereign Mesh & Recursive Subagent Tree Compiler
- **Reference Services & Apps:** `soc_g4b_researcher`, `soc_g4b_builder`, `soc_g4b_audit`, `soc_g4b_telemetry`, `soc_g4b_governance`
- **Governing Invariants:**
  - `[L1-G4B-001]` Decoupled Research Sovereignty & Service Mesh Isolation (Research operates in independent enclave emitting immutable `ResearchDeliverableBundle`).
  - `[L1-G4B-002]` Hierarchical Fractional Budget Leasing & Landauer Decay (Recursive subagent tree depth $d \le 4$, branching factor $b \le 5$, leasing ratio $\lambda \le 0.80$, thermal cutoff $C_{\min} = 1,024$).
  - `[L1-G4B-003]` Merkle-DAG Cryptographic Telemetry Witness (Aggregates leaf execution witnesses into hierarchical Merkle roots sealed in `telemetry_ledger.json` and `telemetry_dashboard.html`).
  - `[L1-G4B-004]` Dynamic On-the-Fly Persona Specialization (`define_subagent` for domain-specific micro-subagents).
  - `[L1-G4B-005]` Subtree-Isolated Self-Healing Backpropagation (Local fault trapping and repair without unwinding ancestor contexts).
  - `[L1-G4B-008]` Mandatory Post-Synthesis Orchestrator Witness Reconciliation Gate (Physical `conversationId` injection, zero placeholder UUIDs).
  - `[L1-G3B-012]` Dedicated Non-Loopback Network Topology (`192.168.40.0/24`).
  - `[L1-G3B-018]` & `[NEG-G1B-001]` Standalone zero-CDN Development Process Telemetry Dashboard deliverable (`dashboard.html` / `telemetry_dashboard.html`) passing `HERM-001..005` with verified subprocess test suite (exit code 0).
