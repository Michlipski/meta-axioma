# Generation 2b Axioms & Invariants: The Recursive Multi-Tier Architecture

> **Generation:** $G_{2b}$ (The Recursive Multi-Tier Axiomatic Compiler)  
> **Status:** Scaffolding & Initial Operationalization  
> **Successor Lineage:** Bootstrapped from $G_{1b}$ (Model-Based Verification, Domain Baseline Research, Post-Emission Witness) and $G_2$ (Axiomatic Intent Boundaries & Exception Enclaves).

---

## 1. Core Invariants for Generation 2b

### `[L1-G2B-001]` Multi-Tier Interlocking Gate
Every feature, state transition, and view component must satisfy the interlocking conjunction of:
$$\text{Synthesize}(F) \iff \text{Valid}_{\text{T1}}(F) \land \big(\text{Valid}_{\text{T2}}(F) \lor \text{HasStatefulOverride}(F)\big) \land \text{Valid}_{\text{T3}}(F)$$
- **Tier 1 (Structural):** Hard $S_0$ axioms (Reachability, Decoupled Persistence `L1-011_3`, Functorial Undo `L1-002`, Enclaves `L1-016`, Thermodynamic Bounds `L1-008`).
- **Tier 2 (Universal Ergonomics):** Nielsen-Norman 10 Usability Heuristics, Fitts's Law ($\ge 44$px touch targets), Hick's Law ($\le 15$ cards / $\le 5$ primary actions), Miller's Law ($7 \pm 2$ chunks).
- **Tier 3 (Domain Archetypes):** Empirical cognitive science and category table stakes.
- **Tier 4 (Fusion):** Feature-level composite verification.

### `[L1-G2B-002]` Stateful Human Override Governance
- Tier 2 usability heuristics cannot be silently ignored or globally disabled.
- Any exemption requires a cryptographically tracked record in `trace/overrides/heuristic_overrides.json` specifying `component_hash`, `human_rationale`, `scope` (`COMPONENT_LOCAL` | `SUBDOMAIN` | `GLOBAL`), and `ttl_epochs`.
- **Anti-Creep Law:** If the Heuristic Debt Ratio ($\text{HDR} = \frac{\sum \text{Exemptions}}{\sum \text{Checkpoints}}$) exceeds $0.15$ ($15\%$), compilation enters `HeuristicCreepWarning` and blocks further unverified exemptions until an audit is conducted.

### `[L1-G2B-003]` Dynamic Weighted Recursion & Worker Taxonomy
- Compilation branches execute in a tree structure bounded by baseline depth $d=3$ (configurable via `G2B_MAX_RECURSION_DEPTH`).
- Worker types consume effective depth based on their structural volatility:
  - `EXPLORATORY_RESEARCH`: $0.5\times$ depth consumption.
  - `FRACTAL_DECOMPOSITION` / `SYNTHESIS`: $1.0\times$ depth consumption.
  - `TERMINAL_SINK` (Anti-Mock Linter, Model Checker, Substrate Runner): $\infty$ (cannot spawn subagents).
- **Boundary Opinion Audit:** When a branch reaches $d = \text{MAX\_DEPTH}$, the agent evaluates a formal reflection probe (`wants_depth_4`, confidence, rationale, estimated tokens) logged to `trace/telemetry/recursion_depth_opinions.jsonl` for offline calibration.
- **Live Tree Visualization:** Every run emits a live Mermaid/Markdown DAG (`recursion_tree.md`) capturing execution topology.

### `[L1-G2B-004]` Thermodynamic Capital Partitioning
Total compilation token budget $C_{\text{global}}$ is strictly partitioned:
1. **Protected Capital ($P_{\text{core}} = 40\%$):** Reserved exclusively for terminal verification nodes (Post-Emission Runtime Gate, Model Checker, Anti-Mock Linter, Clean-Slate Auditor). Never starved by upstream exploration.
2. **Exploratory Capital ($E_{\text{var}} = 60\%$):** Distributed dynamically across recursive branches with a $50\%$ decay factor per nested level:
   $$B_{d+1} = B_d \times \text{Weight}(\text{WorkerType}) \times 0.5$$

### `[L1-G2B-005]` Dynamic Project Proposals Protocol & Deliberate Scope-Cutting
- When processing an application pitch, the orchestrator begins with an **Ambitious Domain Expansion (Phase 0-A)** exploring the maximal domain possibility space.
- The orchestrator autonomously synthesizes a **Dynamic Spectrum of Project Proposals (Phase 0-B)** sized organically for the problem space (bounded within safety limits $[C_{\min}, C_{\max}]$) without hardcoding fixed tier counts or artificial intermediate budgets.
- Each proposal enforces the 40% protected / 60% exploratory capital split (`[L1-G2B-004]`) and explicitly outlines retained features vs. deliberately cut or deferred scope.
- Compilation pauses for human option selection via `ask_question` before contracts or code are emitted.

### `[NEG-G1B-001]` Anti-Phantom Emission & Mandatory Runtime Witness
Inherited from $G_{1b}$: It is strictly prohibited to declare compilation complete without physically emitting non-zero bytes to disk and running substrate tests with exit code 0, generating an empirical witness signature (`WITNESS_PE_...`).
