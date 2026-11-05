# Generation 5 Sovereign Research Service Dossier (`services/research.md`)

> **Enclave Target:** `services/research/` (192.168.40.10)  
> **Target Successor:** Generation 5 Sovereign Research Enclave  
> **Source Directive:** [L1-G4B-001] Decoupled Research Sovereignty, [L1-G4B-002] Zero-Code Research Boundary  
> **Status:** Active Evolution Notes & Desiderata  

---

## 1. Context & Generation 4b Baseline

In Generation 4b, the **Sovereign Research Service** (`services/research/`) established two pivotal architectural victories:
1. **Decoupled Research Sovereignty (`[L1-G4B-001]`):** Research operates independently of synthesis, formalizing problem spaces before a single line of application code is drafted.
2. **The Zero-Code Boundary (`[L1-G4B-002]`):** The Researcher is physically prevented from modifying application code, emitting strictly `ResearchDeliverableBundle` specifications, domain models, and RFC protocols.

The Gen 4b Researcher currently features:
- Waterloo Tier 1 Situation of Concern (`[L1-G3B-000]`) parser (Macro/Meso/Micro).
- Z3 Prover Bridge (`z3_prover_bridge.py`) for checking contract invariants.
- Taboo distance matrices (`graph_taboo_engine.py`) to prevent repeating known architectural traps.
- Inversion Engine (`inversion_engine.py`) and Socratic Red Team (`[L1-G4B-009]`).

---

## 2. Generation 4b Friction Points & Limitations

1. **Static Invariant Checking vs. Dynamic Theorem Synthesis:** The Z3 bridge in Gen 4b checks manually crafted SMT formulas. It cannot autonomously synthesize new algebraic lemmas or generalize invariants from domain contracts.
2. **Synchronous Single-Agent Research Bottleneck:** In Gen 4b, research is still driven primarily through sequential subagent invocations. It lacks an internal dialectical adversarial debate engine where multiple specialized research agents (e.g. Socratic Inverter, UX Ergonomist, Distributed Systems Architect) autonomously debate until reaching Nash equilibrium.
3. **Local Knowledge Isolation:** Research bundles cannot query external academic papers, verified software pattern databases, or historical generation trace archives without explicit human intervention.
4. **Coarse-Grained Task DAG Estimation:** While `DynamicBudgetCalibrator` provides token bounds, it relies on static heuristics rather than dynamic entropy estimation of the problem space.

---

## 3. Generation 5 Desired Capabilities & Aspirations

### 3.1 Dialectical Multi-Agent Research Council
Instead of a single research synthesis pass, Gen 5 will execute an **Autonomous Socratic Council**:
- **Thesis Agent:** Formulates the primary Waterloo SoC and ContractIR.
- **Antithesis (Red Team) Agent:** Inverts every operational assumption, searches for boundary failure modes, and crafts adversarial counterexamples.
- **Synthesis Agent:** Merges valid counter-arguments into strengthened invariant contracts.
- The debate continues until reaching an ε-convergence threshold or proof of invariant preservation.

### 3.2 Automated Lemma & Contract Synthesis
- Deep integration with modern formal provers (Lean 4 / Z3 / Coq) to automatically generate proof obligations for domain statecharts.
- When domain nouns are defined, the engine automatically extracts category-theoretic properties (associativity, identity, functorial preservation) and emits them directly into `ContractIR`.

### 3.3 Dynamic Entropy-Based Token Calibrator
- Measures Kolmogorov complexity and state space graph entropy of the domain specification to compute precise Landauer token allowances for downstream Builder synthesis.

---

## 4. Proposed Invariants for Gen 5 Research

- **`[L1-G5-RES-001]` The Zero-Code Immutability Invariant:** Unconditional preservation of the Zero-Code Boundary (`[L1-G4B-002]`). The Research Service must never possess write access to code compilation targets.
- **`[L1-G5-RES-002]` Mandatory Dialectical Council Attestation:** No `ResearchDeliverableBundle` may be emitted to Builder without a cryptographic attestation of Socratic Red Team debate and resolution of all Tier 1 concerns.
- **`[L1-G5-RES-003]` Functorial IR Contract Preservation:** All emitted `ContractIR` schemas must prove identity and morphism preservation under category-theoretic composition.

---

## 5. Open Research Spikes & Inquiries

1. *Lean 4 vs Z3 in Async Python:* Can we embed lightweight Lean 4 proof verification into the asyncio service mesh without adding heavy external dependencies?
2. *Context-Preserving Compression:* How can the research council compress complex multi-turn debate transcripts into a compact, high-density deliverable bundle for Builder consumption?
