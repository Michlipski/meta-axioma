---
flow: DialecticalSystemDiagnosisFlow
persona: SovereignSystemsArchitect
domains:
  - MetaAxioma
  - AuditService
  - ResearchService
---

# WORKFLOW: Dialectical System Diagnosis & Functorial Roundtrip Closure

> GOAL: Given an observed localized defect or shortcut in the system, systematically elevate it to a higher-order architectural invariant, formulate a generalized structural remedy, project it back down to guarantee it completely cures the original micro-defect, and adversarially falsify the solution across isolated contexts to eliminate single-agent confirmation bias.

---

## 1. The Functorial Roundtrip Formalism

$$\begin{CD}
\text{Defect}_{\text{micro}} @>{\text{Elevation } (F)}>> \text{InvariantDeficit}_{\text{macro}} \\
@. @VV{\text{Architectural Remedy } (S)}V \\
\text{Specific Cure}_{\text{micro}} @<<{\text{Projection } (G)}< \text{Systemic Invariant}_{\text{macro}}
\end{CD}$$

**The Roundtrip Closure Condition:**
A diagnosis is valid if and only if:
$$G(S(F(\text{Defect}_{\text{micro}}))) \implies \text{Mechanical Remediation of } \text{Defect}_{\text{micro}}$$
**AND** the closure is certified by an orthogonal, adversarial evaluator context.

---

## 2. The 5-Step Dialectical Diagnosis Protocol

### STEP 1: Micro-Anomaly Isolation (Physical Grounding)
- **Rule:** Never start with abstract philosophy. Start with physical file paths, line numbers, and empirical stdout/stderr evidence.
- **Deliverables:**
  - `target_artifact`: Exact file path and line span (e.g. `runner.py:360-407`).
  - `observed_behavior`: What the code actually did (e.g. updated `dynamic_dom_elements` in-memory dict).
  - `expected_behavior`: What the formal specification required (e.g. executed client JS via embedded Node probe).
  - `divergence_signature`: Why the existing test suite failed to catch it (e.g. unit tests asserted the mock dict).

### STEP 2: Waterloo Abstraction Elevation (Upward Morphism $F$)
Deconstruct the failure across the Waterloo Tier 1 Situation of Concern hierarchy (`[L1-G3B-000]`):
- **Micro Level (Symptom):** The specific shortcut taken in code or data structures.
- **Meso Level (Mechanism):** The pipeline or protocol failure that allowed this code to be emitted, reviewed, and certified without raising an exception.
- **Macro Level (Incentive / Axiom):** The systemic force (e.g. the LLM simulation gradient, lack of negative feedback loops, single-context builder/tester collusion) that made this shortcut the path of least computational resistance.

### STEP 3: Higher-Order Architectural Remedy Formulation (Morphism $S$)
Design the systemic fix at the macro/meso level. The fix must be **mechanical and deterministic**, never a prompt suggestion or plea for better agent behavior:
- Define new declarative constraints or IR schemas (e.g. `AcceptanceSpecIR`).
- Introduce new automated gates into the compiler pipeline (e.g. Physical Mutation Falsification).
- Add new static AST invariants to the micro-auditor registry (e.g. `HERM-ANTIMOCK-001`).

### STEP 4: Downward Projection & Concrete Trace Walk (Downward Morphism $G$)
Project the higher-order remedy back down to the original micro defect and walk the concrete execution trace:
- **Trace Step 4.1:** If this new mechanism had been active during the original run, at what exact line of execution would it have triggered?
- **Trace Step 4.2:** What exact error class and diagnostic payload would have been raised?
- **Trace Step 4.3:** Does the remedy introduce new failure modes, port deadlocks, or Landauer compute budget overruns?

### STEP 5: Adversarial Epistemic Firewall (Mitigating Single-Context Bias)
To prevent the single-context "Self-Justification Loop", the diagnosis must pass three isolated falsification filters:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    ANTI-BIAS EPISTEMIC FIREWALL                             │
├──────────────────────────────────────┬──────────────────────────────────────┤
│  Filter A: Orthogonal Red Team       │  Filter B: The Lazy Builder Exploit  │
│  ─────────────────────────────       │  ─────────────────────────────────── │
│  Spawn an independent subagent with  │  Ask an isolated context:            │
│  an explicit adversarial mandate:    │  "How could a lazy agent bypass      │
│  'Prove this solution is cosmetic    │  this new gate without doing the     │
│  and fails to cure the original bug.'│  real work?" (Hardens loopholes).    │
├──────────────────────────────────────┴──────────────────────────────────────┤
│  Filter C: Physical Proof-of-Failure (The Acid Test)                        │
│  ───────────────────────────────────────────────────                        │
│  Must be capable of running against the unmodified buggy code and           │
│  demonstrating RED (failure) on the actual substrate.                       │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Operational Persona Contracts

| Persona | Permitted Responsibilities | Prohibited Actions |
| :--- | :--- | :--- |
| **Sovereign Researcher** | Identifies micro anomaly; derives Waterloo SoC; formulates macro IR contracts. | Writing implementation patches; authoring self-grading tests. |
| **Synthesizer Muscle** | Implements the projected patch down to disk. | Certifying its own work; authoring acceptance tests. |
| **Adversarial Red Team** | Stress-tests the roundtrip; invents counter-examples and bypass exploits. | Accepting hand-waving explanations; sharing context with the builder. |
| **Audit Kernel** | Executes physical mutation tests; verifies AST anti-mock rules; issues Merkle root. | Relaxing gates or converting hard errors to warnings. |
