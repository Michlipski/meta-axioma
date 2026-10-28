# Generation 2b Summary: The Recursive Multi-Tier Axiomatic Compiler

> **Generation:** $G_{2b}$ (The Recursive Multi-Tier Axiomatic Compiler)  
> **Status:** Operational & Certified  
> **Primary Telos:** Unify structural $S_0$ invariants with universal ergonomic heuristics (Nielsen-Norman 10, Fitts, Hick, Miller) and empirical cognitive science benchmarks into an interlocking multi-tier compile gate, governed by stateful human overrides, dynamic weighted recursion, and thermodynamic capital partitioning.  
> **Test Compliance:** 10/10 tests passing (`PYTHONPATH=generations/gen_02b/src python3 -m unittest discover -v -s generations/gen_02b/tests`). Emitted app execution suite: 6/6 tests passing (`python3 -m unittest discover -v -s apps/axioma_lexis/tests`). Global test suite: 22/22 tests passing (`PYTHONPATH=src python3 tests/test_all.py`).  
> **Dogfooding Target:** [`axioma_lexis`](apps/axioma_lexis/) (Ground-Up Reconstruction; Witness: `WITNESS_PE_028BC22B43E8AA57`).

---

## 1. Generational Mandate & Motivation

Generation 2b ($G_{2b}$) solves three critical architectural bottlenecks identified in prior generations:
1. **The Usability Heuristic False Dichotomy:**  
   In prior systems, usability heuristics were either treated as rigid compile-blocking gates (causing deadlock on innovative or compact UI layouts) or soft advisory warnings (causing silent heuristic rot and regression). $G_{2b}$ introduces **Stateful Human Override Governance (`[L1-G2B-002]`)** with an immutable audit registry and an anti-creep Heuristic Debt Index ($\text{HDR} \le 0.15$).
2. **Homogeneous Recursion Depth & Verification Starvation:**  
   Treating all worker agents equally leads to shallow research in complex domains and token starvation at verification time. $G_{2b}$ introduces **Dynamic Weighted Recursion & Worker Taxonomy (`[L1-G2B-003]`)** (0.5x exploratory research depth, 1.0x synthesis, terminal verification sinks) paired with **Thermodynamic Capital Partitioning (`[L1-G2B-004]`)** which strictly locks 40% of compute tokens as "Protected Capital" for runtime tests and model checkers.
3. **Premature Local Optimization vs. Ambitious Scope:**  
   Greedy problem-solving tends to shrink scope prematurely to fit token budgets. $G_{2b}$ establishes the **Ambitious Discovery & Deliberate Scope-Cutting Protocol (`[L1-G2B-005]`)**, where the orchestrator begins by mapping the maximal domain possibility space before deliberately cutting to a zero-bloat, high-conviction core.

---

## 2. Core Invariants Formalized

### `[L1-G2B-001]` Multi-Tier Interlocking Gate
Every feature, state transition, and view component must satisfy the interlocking conjunction:
$$\text{Synthesize}(F) \iff \text{Valid}_{\text{T1}}(F) \land \big(\text{Valid}_{\text{T2}}(F) \lor \text{HasStatefulOverride}(F)\big) \land \text{Valid}_{\text{T3}}(F)$$
- **Tier 1 (Structural Invariants):** Hard $S_0$ axioms (State reachability, Decoupled Persistence `L1-011_3`, Functorial Undo `L1-002`, Exception Enclaves `L1-016`, Landauer Bounds `L1-008`).
- **Tier 2 (Universal Ergonomics & Usability):** 10 Nielsen-Norman Usability Heuristics, Fitts's Law ($\ge 44$px touch targets), Hick's Law ($\le 15$ card review batches / $\le 5$ primary actions), Miller's Law ($7 \pm 2$ working memory chunks), and Calm Tech non-intrusive notifications.
- **Tier 3 (Domain Archetype Benchmarks):** Empirical cognitive science table stakes (e.g. for spaced repetition: Due-Queue Gating `AX-MEM-001`, Milestone Completion Closure `AX-MEM-002`, Cram Practice Isolation `AX-MEM-008`).
- **Tier 4 (Cross-Tier Fusion):** Composite end-to-end verification.

### `[L1-G2B-002]` Stateful Human Override Governance & Anti-Creep Law
- Any exemption from Tier 2 usability heuristics requires an explicit entry in `trace/overrides/heuristic_overrides.json` specifying `component_hash`, `human_rationale`, `scope` (`COMPONENT_LOCAL` | `SUBDOMAIN` | `GLOBAL`), and `ttl_epochs`.
- **Heuristic Debt Index:** If the ratio of active exemptions to total audit checkpoints exceeds $0.15$ ($15\%$), compilation triggers a `HeuristicCreepWarning` blocking further exemptions until an audit is conducted.

### `[L1-G2B-003]` Dynamic Weighted Recursion & Prescribed Worker Taxonomy
- Bounded recursion depth ($d=3$ by default, configurable via `G2B_MAX_RECURSION_DEPTH`).
- **Closed Prescribed Worker Taxonomy:** The orchestrator operates strictly over a formal closed set of specialized worker types:
  - Recursive Workers: `Orchestrator` (`1.0x`), `ResearchWorker` (`0.5x`), `SynthesisWorker` (`1.0x`).
  - Terminal Verification Sinks: `AntiMockLinter`, `ModelChecker`, `StructuralRegulator`, `UsabilityAuditor`, `AdversarialFalsifier`, `SubstrateRunner` (`0.0x` depth consumption; strictly forbidden from spawning child subagents).
- **Genuinely Recursive Pathways:**
  - `Orchestrator` $\to$ `ResearchWorker` $\to$ `ResearchWorker` $\to$ `ResearchWorker` (domain grounding $\to$ cognitive benchmarks $\to$ SM-2 calibration).
  - `ResearchWorker` $\to$ `UsabilityAuditor` (Nielsen-Norman 10 & Fitts's law audit).
  - `Orchestrator` $\to$ `SynthesisWorker` $\to$ `SynthesisWorker` $\to$ `SynthesisWorker` (architecture $\to$ scope negotiation $\to$ deliberate scope-cutting).
  - `SynthesisWorker` $\to$ `StructuralRegulator`, `ModelChecker`, `AdversarialFalsifier`.
  - `SynthesisWorker` $\to$ `SynthesisWorker` (component code emission) $\to$ `AntiMockLinter`, `SubstrateRunner`.
- **Boundary Reflection Opinion Probe:** When a recursive worker reaches boundary depth ($d \ge 3$), a formal reflection probe (`wants_depth_4`, confidence, rationale, estimated tokens) is evaluated and logged to `trace/telemetry/recursion_depth_opinions.jsonl` for offline auditability.
- **Live Tree Visualization:** Every run emits a live Mermaid DAG ([`recursion_tree.md`](apps/axioma_lexis/recursion_tree.md)) capturing execution topology, worker roles, subgoals, effective depths, and token burn.

### `[L1-G2B-004]` Thermodynamic Capital Partitioning
Total compilation token budget $C_{\text{global}}$ is partitioned into:
1. **Protected Capital ($P_{\text{core}} = 40\%$):** Strictly reserved for terminal verification nodes. Never starved by upstream exploration.
2. **Exploratory Capital ($E_{\text{var}} = 60\%$):** Dynamically leased with Landauer decay per nested recursion level:
   $$B_{d+1} = B_d \times \text{Weight}(\text{WorkerType}) \times 0.5$$

### `[L1-G2B-005]` Ambitious Discovery & Deliberate Scope-Cutting Protocol
- **Phase 0-A (Ambitious Expansion):** Synthesizes maximal domain feature proposals across cognitive science and industry benchmarks.
- **Phase 0-B (Structured Scope Alignment):** Features are deliberately triaged into core retaining features vs deliberate scope cuts before code generation.

### `[NEG-G1B-001]` Anti-Phantom Emission Gate & Mandatory Runtime Witness
Inherited and enforced: Mandatory physical non-zero file emission and concrete runtime execution of test suites on the substrate resulting in an empirical witness signature (`WITNESS_PE_...`).

---

## 3. Compiler Architecture Overview

```
generations/gen_02b/src/g2b_compiler/
├── __init__.py
├── engine.py                  # Main SystemG2bCompiler pipeline orchestrator
├── lexis_spec.py              # Full ground-up domain IR formulations for Axioma Lexis
├── thermodynamics.py          # Landauer thermodynamic bounds and bit-erasure calculation
├── enclaves.py                # Demarcated exception enclaves
├── matrix/                    # Multi-Tier Usability & Axiom Matrix Substrate
│   ├── models.py              # Tier1StructuralRule, Tier2UsabilityHeuristic, MultiTierAuditResult
│   └── heuristics.py          # Nielsen-Norman 10, Fitts, Hick, Miller, UsabilityHeuristicAuditor
├── overrides/                 # Stateful Human Override Governance
│   └── registry.py            # StatefulOverrideRegistry & Heuristic Debt Index calculator
├── recursion/                 # Dynamic Weighted Recursion & Worker Taxonomy
│   ├── models.py              # WorkerType, RecursionNode, BoundaryOpinion, CapitalPartition
│   ├── cost_allocator.py      # ThermodynamicCostAllocator enforcing 40% protected capital
│   └── tree_visualizer.py     # Live Mermaid DAG generator & boundary reflection logger
├── negotiation/               # Scope Negotiation Protocol
│   └── protocol.py            # Phase 0-A Ambitious Expansion & Deliberate Scope Cutting
├── ir/
│   ├── semantic_ir.py         # Semantic Domain IR
│   ├── statechart_ir.py       # Formal XState v5 Statechart IR & JSON exporter
│   └── contract_ir.py         # Dual-Boundary Contract IR (Nouns + Verbs)
├── isolation/
│   ├── regulator.py           # Structural Axiom Regulator (S0 Invariants, 0 LOC emitted)
│   └── falsifier.py           # Adversarial Falsifier (Chaos assertions, 0 LOC proposed)
├── verification/
│   ├── multi_tier_gate.py     # MultiTierInterlockingGate (Conjunction of T1, T2, T3)
│   ├── model_checker.py       # XState graph reachability & 100% edge traversal engine
│   ├── viability_gate.py      # Steps-to-value (<=3) & reversible error recovery gate
│   ├── substrate_linter.py    # Anti-Mock (NEG-G2-005) & Clean-Slate (NEG-G2-006) linter
│   └── post_emission_gate.py  # Phase 7 Manifest audit & empirical runtime test runner [NEG-G1B-001]
└── emission/
    ├── ast_emitter.py         # TargetCodeEmitterG2b (Full frontend, server, tests, app.json)
    └── release_cleaner.py     # Clean-Slate release directory sanitizer
```

---

## 4. Ground-Up Dogfooding Target: Axioma Lexis ($G_{2b}$)

Axioma Lexis was completely rebuilt from the ground up starting from the ambitious elevator pitch:
> *"A fast, distraction-free, local-first vocabulary and spaced repetition studio. Type just the word -> auto-hydrate definition, pronunciation, and example. Bite-sized daily reviews with adaptive spaced repetition, 1-tap undo, multi-deck tagging, retention curve analytics, and calm local-first sync."*

### Key Features Synthesized:
1. **Instant 2-Second Word Capture:** Type headword $\to$ auto-hydrates definition, IPA phonetics, part-of-speech, and contextual sentence with 1-click accept.
2. **Native Web Speech Audio Pronunciation:** Real browser Web Speech API pronunciation synthesis (zero mock, `[NEG-G2-005]`).
3. **Adaptive SM-2 Spaced Repetition (Due-Queue Gating `AX-MEM-001`):** Strict due-queue pacing: cards only appear in active review when `next_review <= now`.
4. **Celebratory Inbox-Zero Milestone Closure (`AX-MEM-002`):** When the due queue reaches zero, displays a completion celebration card with session retention stats.
5. **Functorial Undo Morphism (`AX-MEM-004`, `[L1-002]`):** 1-tap `Cmd+Z` / Undo button rolls back accidental ratings and restores prior card state without side-effect leaks.
6. **Practice Cram Mode (`AX-MEM-008`):** Separate un-due card exploration mode that allows users to review vocabulary without corrupting SM-2 scheduling intervals.
7. **Multi-Deck Organization & Tagging:** Topic decks with custom color accents and tag filtering.
8. **Retention Analytics & Ebbinghaus Forgetting Curve:** Interactive SVG visualization showing mastery breakdown and retention curves.
9. **Calm Local-First Sync Modal:** Clean JSON export and import for user data sovereignty.
10. **Calm Daily Habit Reminders (`AX-MEM-005`):** Non-intrusive notifications respecting cognitive focus.

### Formal Verification Metrics:
- **Total State Nodes:** 16 states (`idle`, `capturing.{typing, hydrating, preview, offline_fallback}`, `reviewing.{prompt, revealed, advancing, completed}`, `cramming.{prompt, revealed}`, `decks.{list, creating}`, `analytics.viewing`, `sync.viewing`, `settings.viewing`).
- **State Reachability:** 100% reachable from `idle` ($0$ unreachable states).
- **Transitions Verified:** 53 total transitions.
- **Covering Paths Traversed:** 24 distinct execution paths traversing 100% of transitions.
- **Negative Assertions Synthesized:** 571 negative transition test cases.
- **Steps to Value:** **3 steps** (`idle` $\to$ `reviewing` $\to$ `reviewing.prompt` $\to$ `reviewing.revealed`).
- **Reversible Recovery Cycles:** Verified for `offline_fallback` $\to$ `idle` / `hydrating`.
- **Touch Target Ergonomics (Fitts's Law):** `--touch-target: 48px` verified ($\ge 44$px).
- **Post-Emission Substrate Tests:** 6 passing tests on live substrate (`test_runtime.py`, `test_statechart_execution.py`).
- **Anti-Mock Substrate Audit:** 100% compliant (`anti_mock=True`, `clean_slate=True`, `visual_dignity=True`, `violations=0`).
- **Execution DAG & Recursion Topology:** Strict prescribed taxonomy across 15 recursive and terminal nodes (max depth: 3, total tokens: 10,900 allotted, 10,430 used, 95.7% efficiency) rendered in [`recursion_tree.md`](apps/axioma_lexis/recursion_tree.md).
- **Boundary Reflection Telemetry:** 4 depth-3 boundary opinions evaluated and recorded in [`trace/telemetry/recursion_depth_opinions.jsonl`](trace/telemetry/recursion_depth_opinions.jsonl).
- **Orchestrator Subagent Selection & Token Allotment Telemetry:** 65 decisions evaluated with explicit rationale for why each candidate role was selected or rejected, with token allotment vs actual consumption, logged in [`trace/telemetry/orchestration_decisions.jsonl`](trace/telemetry/orchestration_decisions.jsonl).
- **Interactive Telemetry UI Dashboard:** Standalone, dark-mode visual dashboard generated at [`telemetry_dashboard.html`](apps/axioma_lexis/telemetry_dashboard.html) featuring interactive Mermaid DAG, token budget meters, and filterable decision cards.

---

## 5. Verification & Integrity Matrix

| Test Suite | Scope | Tests Run | Result |
| :--- | :--- | :---: | :---: |
| **`test_g2b_compiler.py`** | Multi-Tier Matrix, Usability heuristics (NN 10, Fitts, Hick, Miller), Stateful override registry & Heuristic Debt Index, Worker depth weighting, Thermodynamic capital partitioning (40% protected), Boundary reflection probe, Scope negotiation protocol | 9/9 | ✅ **PASSED** |
| **`test_compile_lexis.py`** | End-to-end $G_{2b}$ ground-up compilation pipeline with physical emission, 16-state model check, multi-tier audit, live substrate runtime test discovery | 1/1 | ✅ **PASSED** (`WITNESS_PE_028BC22B43E8AA57`) |
| **`apps/axioma_lexis/tests`** | Emitted standalone application test suite (Manifest, clean slate, app.json config, 100% edge coverage, 571 negative assertions, functorial undo) | 6/6 | ✅ **PASSED** |
| **`test_all.py` (Root)** | Core Meta-Axioma structural axioms, thermodynamic accounting, exception enclaves | 22/22 | ✅ **PASSED** |
| **`gen_01b/tests`** | Regression check across Generation 1b model-based compiler | 14/14 | ✅ **PASSED** |
