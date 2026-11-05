---
name: latest-self-evolution
description: >-
  Direct the latest generation compiler to inspect, refactor, optimize, or evolve its own architecture,
  internal services, and compiler passes, or execute generational succession to Generation 5.
  Imparts upon the researcher/compiler the dual-path choice: evolve current Gen 4b services or propose
  succession to Gen 5 when architectural limits are reached (requiring explicit human consultation).
---

# Mode 4: Compiler Self-Evolution (`/latest-self-evolution`)

The `/latest-self-evolution` mode directs the **latest generation compiler** (Generation 4b: `generations/gen_04b/`) to work on **itself** — refactoring internal services, extending compiler passes, hardening formal verification enclaves, or preparing generational succession to Generation 5.

---

## 1. The Fundamental Evolutionary Fork: Modifying $G_N$ vs. Proposing $G_{N+1}$

> [!IMPORTANT]
> **The Dual-Path Rule:** When tasked with self-evolution or adding new capabilities to the compiler, the researcher and compiler are **STRICTLY FORBIDDEN from assuming that all changes must be crammed into the current generation ($G_N$)**. 
> The system ALWAYS has two first-class architectural choices, and it **MUST ALWAYS seriously consider both**:
>
> 1. **Choice 1: Intra-Generational Service Modification (Evolve $G_N$ in `generations/gen_04b/`):**
>    - *When to choose:* When the requested feature, refactoring, or capability fits cleanly within the current generation's decoupled service mesh architecture (`services/research/`, `builder/`, `audit/`, `telemetry/`, `governance/`), async RFC bus, and non-loopback invariants without contorting service boundaries or accumulating structural debt.
>
> 2. **Choice 2: Inter-Generational Succession (Propose Advancing to $G_{N+1}$ / Generation 5):**
>    - *When to choose:* When the current architecture cannot soundly support the requested capability, or when supporting it requires monkey-patching, compromising decoupled service sovereignty (`[L1-G4B-001]`), breaking non-loopback invariants (`[L1-G3B-012]`), or forcing paradigm shifts that the current substrate was not designed to bear (e.g. distributed Byzantine consensus, kernel-level eBPF instrumentation, total protocol overhaul, or fundamental axiom shifts).
>    - **Mandatory Serious Consideration:** The researcher must never shy away from proposing generational succession. Meta-Axioma is fundamentally designed around autonomous generational succession ($S_0 \to G_1 \to G_2 \to G_3 \to G_{3b} \to G_4 \to G_{4b} \to G_5$). Proposing $G_{N+1}$ when $G_N$ reaches its structural ceiling is a sign of high architectural integrity, not failure.

---

## 2. Mandatory User Consultation Gate for Generational Succession ($G_{N+1}$)

If the researcher/compiler determines that Generation $N+1$ (Generation 5) should be considered or is the superior path:

1. **Strict Prohibition of Unilateral Succession:**
   - The compiler is **STRICTLY PROHIBITED** from unilaterally creating `generations/gen_05/` or deprecating Gen 4b without explicit human authorization.
2. **Mandatory Specific Ask to the Human Architect (`ask_question`):**
   - The researcher/compiler MUST formulate a clear, rigorous, and specific presentation to the user, both in `project_proposals.md` and directly via `ask_question`.
   - The presentation must explicitly detail its full technical reasoning:
     - **The Architectural Ceiling:** What specific limitation, topology constraint, or invariant bottleneck in Gen 4b prevents this feature from being cleanly implemented?
     - **The Debt of Forcing Gen 4b:** Why attempting to patch or stretch Gen 4b would degrade system invariants or accumulate architectural debt.
     - **The Gen 5 Thesis & Architectural Blueprint:** How Generation 5 will be architected from the ground up to solve this natively (new axioms, decoupled abstractions, upgraded protocols).
     - **The Handover & Coexistence Strategy:** How Gen 4b will scaffold Gen 5 via `/generational-orchestrator` and `trace/flows/generational_handover.flow.md` while maintaining operational continuity.
3. **Execution Only Upon User Approval:**
   - Proceed with generational succession **ONLY** if the user explicitly approves advancing to Gen 5.
   - If the user prefers to remain in Gen 4b, the compiler must adapt the design to fit within Gen 4b's existing constraints while explicitly documenting any trade-offs.

---

## 3. Operating Rules & Core Invariants

- **Mandatory Pre-Execution Governance Gate (`[NEG-GOV-GATE-001]` & Directive 3):**
  - Modifying compiler engine code (`generations/gen_04b/services/`, `protocols/`, etc.) without prior approval is **strictly blocked at runtime by `scripts/governance_pre_tool_guard.py`**.
  - Always emit `<appDataDir>/brain/<conversation-id>/project_proposals.md` via `write_file` and obtain human approval via `ask_question` before executing code modifications.
- **[L1-G4B-003] Quine Crucible & Isolated Daughter Staging:**
  - When synthesizing compiler self-modifications, changes must be staged and validated in isolated test enclaves or daughter branches without mutating the active running root until formal validation succeeds.
  - Zero circular import contamination: All service protocols must communicate via the decoupled asynchronous RFC bus (`protocols/rfc_protocol.py`).
- **[L1-G3B-012] Anti-Loopback Interface Invariant:**
  - All services must strictly bind to non-loopback addresses (`192.168.40.0/24`).
  - Loopback bindings (`127.0.0.1`, `localhost`) are formally proved UNSAT by `smt_mesh_verifier.py`.
- **Landauer Thermodynamic Budgeting:**
  - Allocate explicit token budgets for self-evolution phases, preserving the 60% Exploratory / 40% Protected capital ratio.

---

## 4. Standard Workflow for Compiler Evolution

1. **Architecture & Defect Analysis:**
   - Audit the compiler's current capability against the requested feature or architectural milestone.
   - Seriously evaluate both paths: **Path A (Evolve Gen 4b)** vs. **Path B (Succession to Gen 5)**.
2. **Pre-Execution Proposals Dossier (`project_proposals.md`):**
   - Emit `project_proposals.md` detailing:
     - The architectural motivation and Waterloo SoC of the compiler improvement.
     - Comparative options (including the generational succession option if applicable).
     - Adversarial Red Team critique (`[L1-G4B-009]`) analyzing backward compatibility risks.
   - Elicit human choice via `ask_question` (especially if proposing $G_{N+1}$).
3. **Staged Implementation:**
   - If Path A approved: Implement changes within `generations/gen_04b/services/` or `protocols/`.
   - If Path B approved: Engage `/generational-orchestrator` to initialize `generations/gen_05/`, evaluate predecessor axioms, and construct the successor from scratch.
4. **Empirical Substrate Verification:**
   - Run the full generational test discovery:
     ```bash
     python3 -m unittest discover -v -s generations/gen_04b/tests
     ```
   - Execute the cluster launcher smoke test (`python3 generations/gen_04b/run.py`).
