---
name: generational-orchestrator
description: >-
  Orchestrates autonomous multi-generational succession for Meta-Axioma. Formulates successor
  evaluation targets, synthesizes Trace domain specifications for Generation N+1, initializes
  generational directories, and integrates asynchronous human idea injection.
---

# Generational Orchestrator Directive

This skill governs the autonomous lifecycle and succession protocol of the compiled Meta-Orchestrator.

## Directives

### 1. Generational Handover Verification
Before initiating a generational succession ($G_N \to G_{N+1}$):
1. Verify that Phase 2 Structural Execution has compiled all core target suites ($S_1$ Self-Constructor, $S_2$ Self-Evaluator).
2. Verify that unit test suite passes with 100% compliance (`PYTHONPATH=src python3 tests/test_all.py`).
3. Compile the complete generation summary (`generations/gen_{N:02d}/summary.md`) and sync to root level (`generation_{N:02d}_summary.md`).

### 2. Endogenous Successor Target Synthesis
1. Using Target $S_2$ (Self-Evaluator), synthesize the validation targets for Generation $N+1$.
2. Define the new target definitions, weights, and failure conditions.
3. Generate the Trace specification files for Generation $N+1$ in `trace/`.

### 3. Generational Environment Scaffolding
1. Create `generations/gen_{N+1:02d}/`.
2. Scaffold `epochs/` and `epochs/data/` subdirectories.
3. Initialize the generational README and baseline invariants snapshot.

### 4. Human-as-a-Resource Query Protocol
1. When exploratory entropy decays or when defining new generation boundaries, query the human architect via `ask_question` or structured prompt.
2. Ingest exogenous seeds as candidate priors.
3. Drive the automated compilation loop without requiring per-step human prompts.

### 5. Transgenerational Epistemic Feedback Compilation
1. Ingest all failure modes, post-mortems, and human rulings recorded in `generations/gen_{N:02d}/FEEDBACK.md` and `feedback/feedback.json`.
2. Ensure every high/critical severity lesson is translated into an inherited negative constraint (`NEG-G{N+1}-###`) or structural candidate axiom.
3. Verify that the successor basis generator binds these constraints into Generation $N+1$'s operational charter and compiler gates before initiating construction.

### 6. Mandatory Evolution Dashboard & Epistemic Tracking Synchronization ([L1-G3B-019])
Whenever a new generation $G_{N+1}$ is scaffolded, synthesized, or transitioned:
1. **Synchronize Evolutionary Dataset:** Update `apps/axioma_evolution_dashboard/data/evolution_data.json` and `data/evolution_data.py`:
   - Append the new generational stage with its 4-tier Beehive topology (`nodes`, `edges`).
   - Insert the new transformation node ($\Delta_{N \to N+1}$) with explicit Deltas (Added, Removed, Refactored) and Catalysts (Technical & Thermodynamic).
   - Elicit and record **Michael Lipski's Epistemic Contributions**: capture the foundational human thoughts, exogenous mathematical seeds, negative invariant vetoes (`NEG-###`), and strategic pivots.
   - Extend all 6 subsystem evolutionary lineages across the new generational boundary.
   - Update the Pinned Zenith Architecture HUD if $G_{N+1}$ establishes a new state of the art.
2. **Re-verify & Test Evolution Studio:**
   - Verify `apps/axioma_evolution_dashboard/dashboard.html` and `static/index.html`.
   - Run the empirical test suite: `python3 -m unittest discover -v -s apps/axioma_evolution_dashboard/tests` (must pass 100% with exit code 0).
   - Sync the brain Generative UI artifact `meta_axioma_evolution_dashboard.html`.
   - Update `SYSTEMS_PORTFOLIO.md` and `apps/README.md`.

