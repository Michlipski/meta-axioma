# Generation 1b Active Axiom Registry (`generation_01b_axioms.md`)

> **Persistent Invariant Registry for Generation 1b ($G_{1b}$)**  
> Grounded in $S_0$'s foundational structural axioms to eradicate greedy one-pass LLM code emission and phantom verification.  
> Status: **OPERATIONAL**

---

## Registry Metadata

- **Generation:** $G_{1b}$ (Deterministic Model-Based Compiler)
- **Status:** Operational
- **Focus:** Deterministic Guardrails, Model-Based Statechart Verification, Strict Epistemic Isolation, Anti-Phantom Emission
- **Total Active Structural Axioms:** 5
- **Total Negative Invariants:** 3
- **Root Reference Applications:** Axioma Lexis (Port 8090), Axioma Crossword (Port 8094)

---

## Active Level 1 Structural Basis Axioms

### [L1-G1B-001] Model-Based Statechart Reachability & Edge Coverage (XState v5)
- **Level:** Level 1 (Structural)
- **Status:** **ACTIVE**
- **Domain:** Formal Automata Theory & Model-Based Testing
- **Statement:** Every user, operational, and system journey synthesized by the compiler must be modeled as an executable, edge-connected hierarchical state machine adhering to the XState v5 specification.
- **Formal Expression:**
  $$\forall s \in \mathcal{S}, \; \text{Reach}(s_0 \to s) \neq \emptyset \quad \land \quad \text{Coverage}(\mathcal{E}_{\text{valid}}) = 1.0 \quad \land \quad \forall (s, e_{\text{neg}}) \notin \mathcal{E}, \; \delta(s, e_{\text{neg}}) = \bot$$
- **Operational Rule:**
  1. BFS reachability must prove 100% of declared product states are reachable from initial root. Unreachable orphan states abort compilation.
  2. The compiler must synthesize covering paths that traverse 100% of valid transitions.
  3. The compiler must synthesize negative transition assertions verifying that unhandled events produce zero state mutation.

---

### [L1-G1B-002] Anti-Greedy Multi-Phase Intermediate Representation Decoupling
- **Level:** Level 1 (Structural)
- **Status:** **ACTIVE**
- **Domain:** Compiler Construction & Dialectic Translation
- **Statement:** The compiler is strictly prohibited from mapping high-level product intent directly to source code in a single pass. Translation must proceed through explicit, verifiable intermediate representations.
- **Formal Expression:**
  $$\text{Spec} \xrightarrow{\mathcal{T}_1} \text{Semantic IR} \xrightarrow{\mathcal{T}_2} \text{Statechart IR} \xrightarrow{\mathcal{T}_3} \text{Contract IR} \xrightarrow{\mathcal{T}_4} \text{Target Code}$$
- **Operational Rule:** Direct prompt-to-code shortcuts raise `GreedyCompilationViolation`. Each IR must be independently serializable, introspectable, and verified before the subsequent stage executes.

---

### [L1-G1B-003] Strict Epistemic Isolation Triad
- **Level:** Level 1 (Structural)
- **Status:** **ACTIVE**
- **Domain:** Information Theory & Information-Barrier Subagent Systems
- **Statement:** Modules within the compiler must operate under strict epistemic isolation:
  - **Structural Axiom Regulator:** Bounds architecture and audits constraints; prohibited from generating code.
  - **Adversarial Falsifier:** Synthesizes invariant assertion suites and chaos edge cases; prohibited from proposing candidate code solutions.
  - **Synthesis Workers:** Implement concrete local AST components against isolated interface contracts; blind to ambient global prompts.
- **Operational Rule:** Any module violating its epistemic role raises `EpistemicIsolationBreachError`.

---

### [L1-G1B-004] Pareto Steps-to-Value Budget & Reversible Error Recovery Cycles
- **Level:** Level 1 (Structural)
- **Status:** **ACTIVE**
- **Domain:** Cognitive Ergonomics & Fault-Tolerant Dynamic Systems
- **Statement:** Every synthesized application must satisfy human usability budgets and preserve invariant reversibility across operational errors.
- **Formal Expression:**
  $$\text{dist}(s_0 \to s_{\text{value}}) \le K \quad (K=3) \quad \land \quad \forall s_{\text{err}} \in \mathcal{S}_{\text{err}}, \; \exists \text{Path}(s_{\text{err}} \to s_{\text{recover}}) \text{ where } s_{\text{recover}} \in \mathcal{S}_{\text{valid}}$$
- **Operational Rule:** Applications requiring $>3$ steps to primary value or lacking reversible recovery paths from error states are rejected at the viability gate.

---

### [L1-G1B-005] Transgenerational Substrate Quality Invariance
- **Level:** Level 1 (Structural)
- **Status:** **ACTIVE**
- **Domain:** Substrate Integrity & Anti-Mock Discipline
- **Statement:** Synthesized applications must respect inherited transgenerational substrate invariants:
  1. *Anti-Mock Discipline (`NEG-G2-005`):* No fake mock timers, simulated banners, or dummy notification loops.
  2. *Clean-Slate Initial State (`NEG-G2-006`):* Initial application data stores must be clean-slate (zero test mock fixtures in production decks or grids).
  3. *Visual Dignity Design Tokens (`NEG-G2-008`):* Responsive layout, legible typography, keyboard and touch ergonomics.

---

## Active Negative Invariants (Human Oracle Vetoes & Mechanical Gates)

### [NEG-G1B-001] The Anti-Simulated Completion Invariant (Anti-Phantom Emission)
- **Status:** **ACTIVE (Mechanical Gate Enforced)**
- **Domain:** Operational Truth & Autonomous Agent Safety
- **Forbidden Pattern:** Declaring compilation, verification, or application synthesis complete based solely on in-memory models, abstract BFS proofs, or unexecuted source files.
- **Formal Expression:**
  $$\text{CompilationStatus}(\mathcal{A}) = \text{Verified} \iff \text{PhysicalEmission}(\mathcal{A}) \land \text{Manifest}(\mathcal{A}) \land \text{ExecSubstrate}(\mathcal{T}_{\text{edge}}) = \text{PASS} \land |\mathcal{T}_{\text{edge}}| > 0$$
- **Operational Enforcement:**
  1. `SystemG1bCompiler.compile(...)` requires `target_output_dir` (or explicit `allow_dry_run=True`). Calling compilation without an output target raises `PhantomEmissionViolation`.
  2. `PostEmissionGate.verify_manifest` inspects disk: all 10 mandatory assets (`index.html`, `machine.js`, `app.js`, `style.css`, `server.py`, `run.py`, `app.json`, `app_state.json`, `test_runtime.py`, `test_statechart_execution.py`) must exist and have non-zero byte size (`st_size > 0`).
  3. `PostEmissionGate.execute_test_suite` programmatically executes the emitted test suite against the target Python 3.14 runtime. Zero tests discovered or any failing assertion raises `PostEmissionExecutionFailure` and immediately halts the compiler.
  4. Successful verification produces a cryptographic witness signature (`WITNESS_PE_...`) recorded in the compilation artifacts.

---

### [NEG-G1B-002] Negative Transition Non-Mutation Invariant
- **Status:** **ACTIVE**
- **Forbidden Pattern:** Allowing an unexpected or illegal event to mutate application state or trigger undefined side effects.
- **Operational Enforcement:** Statechart runtimes must explicitly drop unregistered events and maintain the exact current state configuration.

---

### [NEG-G1B-003] Excessive Friction & Steps-to-Value Budget Exceeded Veto
- **Status:** **ACTIVE**
- **Forbidden Pattern:** Emitting consumer workflows that demand configuration, onboarding hurdles, or more than 3 user interactions before delivering the primary core job-to-be-done.
