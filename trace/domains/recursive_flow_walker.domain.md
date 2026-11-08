---
domain: RecursiveFlowWalker
related_domains:
  - AppSpecification
  - TelemetryAudit
  - AxiomRegistry
  - Generation05Thesis
---

# DOMAIN: Recursive Flow Graph (RFG) & Headless UI Journey Verification

Establishes the formal category-theoretic and graph-algorithmic invariants governing **Recursive Flow Graphs (RFGs)**, **Compositional Hierarchical Traversal**, and **Subprocess Headless Journey Execution** (`[L1-G4B-017]`, `[L1-G3B-013]`).

---

## CONSTRAINTS:

- **C1 (Recursive Module Composition):** Any compound or parallel state node $M \in \mathcal{N}_{macro}$ in a `StatechartIR` specification represents a discrete, self-contained sub-statechart $G_{micro}(M)$ bounded by explicit Entry Ports ($En_M$) and Exit Ports ($Ex_M$).
- **C2 (Compositional Non-Explosion Invariant):** Complete statechart covering tours MUST be synthesized hierarchically via modular entry/exit port contracts ($En_M \xrightarrow{\pi_M} Ex_M$) and orthogonal regional projections. Cartesian product flattening of parallel regions ($\prod_{i=1}^m |V_i|$) is strictly prohibited (`[NEG-COMPLEXITY-001]`).
- **C3 (Semantic Feasibility & SMT Guard Preamble):** A transition edge $t = (u \xrightarrow{e[g]} v)$ with guard predicate $g(context, event)$ must be verified for satisfiability prior to live subprocess execution. If $\neg g(\mathbf{x}_{curr})$, an inductive Weakest Precondition preamble $\pi_{pre}$ must be spliced to establish context feasibility.
- **C4 (Empirical State Delta Invariant [L1-G3B-013]):** Every journey step executed by the headless walker against a live application subprocess must observe a measurable change in external runtime state ($\Delta S \ne 0$) or DOM mutation. Steps asserting success without state modification are rejected as phantom steps (`PhantomJourneyStepViolation`).
- **C5 (Zero Application Hardcoding in Walker Engine):** The headless journey walker engine (`HeadlessUIJourneyWalker`) is strictly barred from containing application-specific string constants, hardcoded DOM selectors, or application route URLs. All interaction directives must be derived dynamically from `StatechartIR` and declarative flow contracts.
- **C6 (Universal Human Ergonomics Sinks [L1-G4B-015]):** Every traversed state in the generated tour must pass the 4 Universal Human Ergonomics Axioms:
  1. Axiom 1: Zero Console Panics & JS Syntax Errors.
  2. Axiom 2: Viewport Bounding Box Containment ($x \ge 0, y \ge 0, x+w \le W, y+h \le H$).
  3. Axiom 3: Sensory Liveness Guarantee (interactive feedback within $\le 200\text{ms}$).
  4. Axiom 4: Non-Occlusion & 1-Tap Functorial Escape Hatches (`[L1-002]`).

---

## GLOSSARY:

- **Recursive Flow Graph (RFG):** A hierarchical transition system $\mathcal{M}_{RFG} = \langle \mathcal{N}_{macro}, \mathcal{N}_{micro}, \Sigma, \mathcal{D}, \mathbf{x}_0, \delta, \mathcal{H} \rangle$ where macro-nodes encapsulate child statecharts and micro-nodes represent leaf states.
- **Compositional Hierarchical Traversal:** An algorithm computing an Eulerian covering path across nested modules without expanding into combinatorial Cartesian products, achieving 100% transition coverage in $O(|V| \log |V| + |E|)$ complexity.
- **Entry Port ($En_M$):** Designated initial entry state(s) of a nested micro-flow graph.
- **Exit Port ($Ex_M$):** Designated terminal or cross-boundary exit state(s) transferring control back to parent macro-graphs.
- **SMT Guard Preamble:** A minimal sequence of contextual setup actions synthesized via backward symbolic execution ($WP(\pi, g)$) to satisfy an otherwise blocked transition guard.
- **Bisimulation Witness:** A formal proof verifying bijectivity between statechart transition events and live HTML DOM event listeners (`HERM-UI-003`).

---

# ENTITY: RecursiveStateNode
MUST HAVE:
- node_id: String
- node_type: Enum (ATOMIC, COMPOUND, PARALLEL, HISTORY, FINAL)
- initial_substate: Optional[String]
- child_states: Dict[String, Any]
- transitions: List[Dict[String, Any]]
- entry_ports: List[String]
- exit_ports: List[String]

RULES:
- R1: If node_type == COMPOUND, initial_substate must be non-empty and present in child_states.
- R2: If node_type == PARALLEL, child_states must contain >= 2 orthogonal regions.
- R3: If node_type in {COMPOUND, PARALLEL}, entry_ports must be non-empty.

# ENTITY: GuardedTransition
MUST HAVE:
- transition_id: String
- source_state: String
- target_state: String
- event_name: String
- target_selector: String
- guard_expression: Optional[String]
- action_mutators: List[String]
- max_latency_ms: Integer

RULES:
- R1: max_latency_ms must be in range [10, 500].
- R2: target_selector must be a valid CSS selector (#id, .class, [data-action]).

# ENTITY: HierarchicalTourWitness
MUST HAVE:
- witness_id: String
- app_id: String
- statechart_id: String
- total_transitions_declared: Integer
- total_transitions_traversed: Integer
- coverage_percentage: Float
- steps_count: Integer
- is_certified: Boolean
- sha256_attestation_hash: String

RULES:
- R1: coverage_percentage must be >= 90.0 (target 100.0) for is_certified == True.
- R2: sha256_attestation_hash must be a valid 64-character hexadecimal digest.

---

# EVENT: RecursiveTourSynthesized
TRIGGER:
- Emitted when FlowParser compiles a minimal hierarchical covering path for a Recursive Flow Graph.
PAYLOAD:
- statechart_id: String
- total_steps: Integer
- coverage_pct: Float
- algorithm_mode: String (COMPOSITIONAL_HIERARCHICAL)

# EVENT: HeadlessJourneyCertified
TRIGGER:
- Emitted when HeadlessUIJourneyWalker executes the full covering path against a live OS subprocess with exit code 0, zero console panics, and 100% passing state assertions.
PAYLOAD:
- app_id: String
- walk_id: String
- port: Integer
- journey_report: Dict[str, Any]
