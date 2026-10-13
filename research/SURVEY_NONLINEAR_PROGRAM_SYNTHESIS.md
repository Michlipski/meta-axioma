# Literature Survey: Non-Linear Program Synthesis & Architectural Evolution

- **Document ID:** `RES-LIT-001`
- **Topic:** Algorithmic & Evolutionary Mechanisms for Exploring Software Design Spaces
- **Author:** Meta-Axioma Systems Research

---

## 1. Introduction

Traditional software engineering relies on manual iterative design. Autonomous AI software engineering, however, frequently collapses into greedy gradient following or static one-shot completion. This survey examines established methods in computational intelligence and formal methods that prevent linear search collapse.

---

## 2. The FunSearch Architecture (DeepMind / Nature 2023)

### A. Architectural Overview
FunSearch combines pre-trained Large Language Models with automated evaluators in an evolutionary loop designed to search the space of executable functions rather than direct answer strings:

```text
┌─────────────────┐       Candidate Programs       ┌───────────────────┐
│                 ├───────────────────────────────>│                   │
│  LLM Generator  │                                │ Isolated Sandbox  │
│                 │<───────────────────────────────┤     Evaluator     │
└────────┬────────┘         Fitness Feedback       └─────────┬─────────┘
         │                                                   │
         │ Prompts (Top Solutions)                           │ Validated Scores
         │                                                   ▼
┌────────┴─────────────────────────────────────────────────────────────┐
│             Evolutionary Islands Database (MAP-Elites)               │
│                                                                      │
│   [Island 0]           [Island 1]           [Island 2]      ...     │
│   Diverse Pops         Diverse Pops         Diverse Pops             │
└──────────────────────────────────────────────────────────────────────┘
```

### B. Core Mathematical & Operational Principles
1. **Separation of Generation and Verification:**  
   The LLM operates as a probabilistic creativity engine. It is completely untrusted. The evaluator executes the generated code in a sealed sandbox against rigid mathematical assertions.
2. **Island Model Topology:**  
   Solutions are grouped into independent clusters ("islands"). Evolution proceeds in parallel on each island. Periodically, high-performing individuals migrate between islands. This guarantees that if Island 0 gets trapped in a local basin, Island 1 and 2 continue exploring orthogonal evolutionary trajectories.
3. **Prompt Sampling with Recency & Performance Bias:**  
   When querying the LLM for a mutation, FunSearch samples parents from the island using an energy function that balances score with diversity, preventing the LLM from repeatedly regurgitating the same syntax.

---

## 3. Quality-Diversity & MAP-Elites (Mouret & Clune 2015)

### A. Beyond Objective Optimization
Standard genetic algorithms optimize a scalar fitness function:
$$x^* = \arg\max_{x \in \mathcal{X}} f(x)$$
In software architecture, scalar optimization fails because software design spaces are deceptive: a modification that temporarily reduces throughput or increases latency might be an essential stepping stone to a design that later achieves partition immunity or zero-downtime hot-patching.

### B. The MAP-Elites Formulation
MAP-Elites defines a behavioral feature space $\mathcal{B} = \mathbb{R}^d$ and discretizes it into an $n$-dimensional grid of cells:
$$\mathcal{C} = \{ c_1, c_2, \dots, c_K \}$$
For every candidate system $x$:
1. Compute fitness $f(x)$ (e.g. Invariant Preservation & Correctness).
2. Compute behavioral descriptor $b(x) \in \mathcal{B}$ (e.g. $[ \text{Latency}, \text{Throughput}, \text{Landauer Dissipation}, \text{Message Complexity} ]$).
3. Identify grid cell $c = \text{MapToCell}(b(x))$.
4. If cell $c$ is empty, store $x$ in $c$. If cell $c$ already contains occupant $x_{\text{current}}$, replace it if and only if $f(x) > f(x_{\text{current}})$.

### C. Implications for Meta-Axioma
When $G_1$ searches for $G_2$'s architecture:
- It must not simply ask: *"Does this candidate pass the tests?"*
- It must map candidates across an archive of behavioral dimensions:
  - Axis 1: **Consistency Model** (Linearizable Quorum vs. Causal CRDT vs. Topological Sheaf).
  - Axis 2: **Thermodynamic Footprint** (Joules dissipated per 1,000 transactions).
  - Axis 3: **Partition Tolerance** (Symmetric vs. Asymmetric vs. Flapping Link Survival).
- This guarantees that distinct architectural paradigms are preserved as live alternatives rather than greedily discarded.

---

## 4. Genetic Improvement of Software (Petke et al. 2017)

Genetic Improvement (GI) uses evolutionary computation to optimize existing software properties (speed, energy, bug fixing) while preserving semantic functionality:
- **Grammar-Based Mutation:** Mutates Abstract Syntax Trees (ASTs) rather than raw text, ensuring that generated candidates remain syntactically well-formed.
- **Oracle Verification:** Applies property-based test suites to weed out regressive mutations.
- **Pareto Multi-Objective Selection:** Optimizes execution speed against memory consumption without sacrificing functional accuracy.

---

## 5. Synthesis: Mandatory Requirements for System $G_1$

To enforce non-linear evolution in $G_1$, the compiler must incorporate:
1. **An Island Database:** Maintaining at least 3 isolated candidate populations for any subsystem target.
2. **Behavioral Feature Mapping:** Evaluating candidates across latency, fault tolerance, and thermodynamic dissipation.
3. **An Anti-Linear Execution Barrier:** Refusing to emit an architectural specification without a cryptographic trace proving that candidate branches competed, failed, and mutated across multiple generations.
