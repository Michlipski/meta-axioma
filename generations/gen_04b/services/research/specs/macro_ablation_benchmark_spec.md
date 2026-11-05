# Sovereign Research Specification: Macro-Level Application Ablation Benchmark (Refined)
## Generation 4b Research Deliverable (`urn:axioma:g4b:spec:macro_ablation_benchmark:v2`)

> **Issuing Authority:** Sovereign Research Service (`services/research/`, `192.168.40.10:8201`)  
> **Status:** Refined Benchmark Archetypes & Tiered Evaluation Rubric  
> **Governance Authorization:** Research Iteration per Human Architect Feedback  

---

## 1. Executive Summary & Epistemic Thesis

A meaningful macro-level ablation benchmark must test an AI compiler's ability to produce **complete, living distributed software systems**, not merely syntactically valid code blocks. 

To prevent "metric gaming" (e.g. an application scoring 80/100 because it is token-efficient and has clean docstrings, despite crashing immediately on boot), the evaluation system adopts a **Tiered Gatekeeper Scoring Architecture**:
1. **Tier 0 Operational Liveness Multiplier:** If an emitted application fails to boot in an independent OS subprocess or crashes on startup, its composite score is **identically 0.0**.
2. **Tier 1 Functional & Invariant Soundness (60%):** Bijective specification coverage, formal statechart invariants, and resilience under Byzantine chaos.
3. **Tier 2 Structural & Thermodynamic Quality (40%):** Zero-trust AST hermeticity and Landauer token/LOC efficiency.

---

## 2. Refined Benchmark Application Archetypes

Each benchmark archetype is designed to trigger specific, well-known failure modes of unverified generative AI models:

### Archetype 1: `Axioma-KV` (Transactional Key-Value Store & WAL Engine)
- **Domain:** Storage & Concurrency
- **The Prompt Given to Compiler:**
  > "Synthesize a standalone, multi-threaded key-value storage daemon with Write-Ahead Logging (WAL), atomic multi-key transactions (`BEGIN`, `SET`, `COMMIT`, `ROLLBACK`), TTL eviction, and a REST HTTP interface (`/keys/{key}`, `/tx`, `/healthz`). It must persist data to disk and restore state upon restart."
- **Why It Stresses AI Compilers:**
  - *Flat LLM Failure Mode:* Standard LLMs implement in-memory dictionaries that lose state on restart, or botch transactional isolation under concurrent client mutations (partial commits, dirty reads, unhandled rollback exceptions).
  - *Meta-Axioma Invariants Tested:* Functorial state rollback ($S \circ S^{-1} = \text{id}$), crash-recovery consistency, and pure morphism state persistence.

### Archetype 2: `Axioma-Flow` (Hierarchical DAG Job Orchestrator)
- **Domain:** Distributed Workflow & Async Coordination
- **The Prompt Given to Compiler:**
  > "Synthesize a job execution engine that accepts acyclic workflow DAGs, executes tasks respecting dependencies, enforces exponential backoff retries on failure, transitions jobs through an explicit hierarchical state machine (`PENDING -> RUNNING -> COMPLETED | FAILED | CANCELED`), and streams real-time state events over SSE/HTTP."
- **Why It Stresses AI Compilers:**
  - *Flat LLM Failure Mode:* LLMs create infinite retry loops, fail to detect dependency cycles, or allow jobs to get stuck in dead-end states when a child task fails.
  - *Meta-Axioma Invariants Tested:* XState v5 compound/parallel state validity, transitive cycle detection via SMT prover, and non-blocking async task orchestration.

### Archetype 3: `Axioma-Collab` (Real-Time Collaborative Canvas / Board)
- **Domain:** Event-Driven State Synchronization
- **The Prompt Given to Compiler:**
  > "Synthesize a real-time collaborative state board supporting multiple concurrent client sessions over WebSockets, conflict-free state merging via vector clocks/CRDTs, full event history audit trail, and instant 1-tap client-side undo/redo."
- **Why It Stresses AI Compilers:**
  - *Flat LLM Failure Mode:* Race conditions in WebSocket message framing, diverging state across multiple clients, and memory leaks from unbounded event histories.
  - *Meta-Axioma Invariants Tested:* Sheaf-CRDT state convergence, AST micro-auditing against shared-state mutation, and headless journey walker validation.

### Archetype 4: `Axioma-Gateway` (Multi-Tenant Token-Bucket Rate Limiter & Reverse Proxy)
- **Domain:** Systems Security & High-Throughput Routing
- **The Prompt Given to Compiler:**
  > "Synthesize a high-throughput API gateway with multi-tenant token-bucket rate limiting, API key authentication, request path forwarding, SQLite telemetry logging, and dynamic rule reloading without daemon restart."
- **Why It Stresses AI Compilers:**
  - *Flat LLM Failure Mode:* Rate-limit bypass under burst concurrency, thread starvation from synchronous I/O, or hardcoded secret/ambient path leaks.
  - *Meta-Axioma Invariants Tested:* Zero-bypass micro-auditing, non-blocking AsyncIO socket management, and zero unhandled 500 exceptions under flood.

---

## 3. The Refined Tiered Scoring Architecture

### Tier 0: The Operational Liveness Gatekeeper ($\mathcal{G}_{\text{liveness}} \in \{0, 1\}$)
Before computing any graded metrics, the emitted application must pass the **Subprocess Smoke Gate ([NEG-G1B-002])**:
- The harness executes: `proc = subprocess.Popen([sys.executable, str(app_root / "run.py"), "--port", str(ephemeral_port)])`
- Probes `/healthz` or status endpoint within $5.0\text{s}$.
- Asserts zero top-level import crashes and operational listener binding.
- Sends `SIGTERM` and asserts clean exit within $3.0\text{s}$ without orphan processes.

$$\text{If } \mathcal{G}_{\text{liveness}} = 0 \implies \mathbf{\text{Final Composite Score } S = 0.0}$$

---

### Tier 1 & 2: Graded Multi-Factor Score ($0 \le S_{\text{graded}} \le 100$)

When $\mathcal{G}_{\text{liveness}} = 1$, the composite score is evaluated as:

$$S_{\text{graded}} = \underbrace{0.25 \cdot S_{\text{spec}} + 0.20 \cdot S_{\text{state}} + 0.15 \cdot S_{\text{chaos}}}_{\text{Tier 1: Functional & Invariant Soundness (60%)}} + \underbrace{0.20 \cdot S_{\text{hermetic}} + 0.20 \cdot S_{\text{eff}}}_{\text{Tier 2: Structural & Resource Quality (40%)}}$$

```
                                  [Emitted Application]
                                            |
                                  [Subprocess Smoke Gate]
                                   /                   \
                        (Crashes / Exit != 0)     (Healthy / Exit == 0)
                                 /                       \
                          Score = 0.0              [Graded Evaluation]
                                                /           |           \
                                       Functional      Robustness      Efficiency
                                         (45%)           (35%)           (20%)
```

### Detailed Evaluation Formulas:

| Metric | Weight | Measurement Method | Falsifiable Failure Mode Caught |
| :--- | :---: | :--- | :--- |
| **$S_{\text{spec}}$: Bijective Specification Fidelity** | **25%** | AST visitor extracts all declared routes, verbs, and data models; computes Jaccard similarity and coverage against the prompt specification: $$S_{\text{spec}} = \frac{|\text{Prompt Verbs} \cap \text{AST Endpoints}|}{|\text{Prompt Verbs}|} \times 100$$ | Hallucinated endpoints, omitted core verbs, missing data fields. |
| **$S_{\text{state}}$: Statechart & Invariant Integrity** | **20%** | Automated state-machine walker attempts all declared state transitions, asserting guard enforcement and checking rollback: $$S_{\text{state}} = \left(1 - \frac{\text{Invalid Transitions Allowed} + \text{Deadlocks}}{\text{Total Transitions Tested}}\right) \times 100$$ | Illegal state jumps (e.g. `COMPLETED -> RUNNING`), dead-end states, broken rollback. |
| **$S_{\text{chaos}}$: Byzantine Chaos Survival** | **15%** | Test harness injects 100 concurrent requests, malformed JSON, truncated bodies, and unexpected disconnections: $$S_{\text{chaos}} = \left(1 - \frac{\text{Unhandled 500 Exceptions} + \text{Crashes}}{\text{Total Chaos Probes}}\right) \times 100$$ | Server panics, process termination, thread deadlocks, corrupt state storage. |
| **$S_{\text{hermetic}}$: Zero-Trust AST Hermeticity** | **20%** | Static AST inspection via `ZeroTrustMicroAuditor` for prohibited constructs (`eval`, `exec`, `os.system`, hardcoded `/tmp`, ambient network calls): $$S_{\text{hermetic}} = \max\left(0, 100 - 25 \times \text{AST Violations}\right)$$ | Security vulnerabilities, ambient filesystem pollution, dynamic code injection. |
| **$S_{\text{eff}}$: Thermodynamic Landauer Efficiency** | **20%** | Evaluates token spend efficiency and code density relative to capability delivered: $$S_{\text{eff}} = \min\left(100, \frac{\text{Capabilities Delivered} \times 10,000}{\text{BPE Token Spend}}\right)$$ | Unconstrained prompt padding, bloated boilerplate LOC, Landauer thermal waste. |

---

## 4. The 5 Ablation Configurations Compared

By applying this exact scoring gauntlet across 5 compiler configurations, the benchmark isolates the marginal value of each architectural layer:

1. **Baseline (Full Meta-Axioma Stack):** Waterloo SoC $\to$ ContractIR $\to$ Z3 SMT $\to$ Statecharts $\to$ AST Micro-Auditing $\to$ Subprocess Smoke $\to$ Byzantine QA.
2. **Ablation 1 (Flat Prompt LLM):** Direct single-pass prompt-to-code generation (simulating standard Copilot/Claude/Devin generation without formal constraints).
3. **Ablation 2 (w/o Formal Contracts & SMT):** Multi-agent synthesis without invariant contracts or symbolic proofs.
4. **Ablation 3 (w/o Zero-Trust AST Micro-Auditors):** Synthesis without AST pre-emission linting or hermetic call interception.
5. **Ablation 4 (w/o Subprocess Smoke & Byzantine Chaos):** Synthesis relying strictly on mock in-memory unit tests.

---

## 5. Next Steps for Implementation

Upon human governance approval:
1. Initialize `benchmarks/macro_ablation/` test suite with the 4 archetype specifications.
2. Build the automated `MacroEvaluationGauntlet` implementing the Gatekeeper and 5 scoring passes.
3. Integrate real-time scoring output with the Telemetry Cockpit (`192.168.40.40`).
