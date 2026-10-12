---
flow: EpochEvolutionFlow
persona: MetaOrchestrator
domains:
  - AxiomRegistry
  - SimulationDecay
  - EvaluationTargets
  - TelemetryAudit
---

# WORKFLOW: Recursive Epoch Evolution

> GOAL: Execute a single bootstrapping epoch—compute decay budgeting, multi-candidate generation, simulation tournament, HITL evaluation, invariant commitment, and report generation.

---

## STEP 1: Compute Budget & Decay Allocation
- Calculates active invariant count $n$ from AxiomRegistry.
- Computes token budget $T(n)$ and tree depth according to thermodynamic decay formula.
- Emits `BudgetCalculated` event.

## STEP 2: Candidate Generation & Speculative Lookahead
- Synthesizes candidate pool using LLM prompts constrained by inactive epistemic scaffolding and exogenous domain seeds.
- If in Phase 1 and approaching plateau ($n \ge 10$, Epoch $\ge 10$), runs 2-epoch lookahead radar ($\Lambda(H)$) to evaluate phase transition dividends.

## STEP 3: Multi-Candidate Simulation Tournament
- Simulates each candidate against active target sandbox ($E_1, E_2, E_3$ in Phase 1; $S_1, S_2, S_3$ in Phase 2).
- Enforces Negative Axiom boundaries: candidates violating active forbidden patterns are rejected.
- Computes TriFoldMetrics and ranks candidates by aggregate $\Delta E$.

## STEP 4: HITL Intercept & Supervisory Review
- Inspects HITL decision queue. If human supervisor requested intercept or injected user seed:
  - Compares user candidate against LLM tournament winner head-to-head.
  - Applies human verdict (`APPROVE_LLM`, `APPROVE_USER`, `APPROVE_BOTH`, `REJECT_ALL`, `FORCE_JETTISON`).
- Otherwise, proceeds with highest-ranked candidate where $\Delta E > 0$.

## STEP 5: Invariant Commitment & Jettison Trigger
- If candidate has strictly positive aggregate $\Delta E > 0$:
  - Commits axiom to `generation_{XX}_axioms.md` in ACTIVE status.
  - Updates global efficacy $E \gets E + \Delta E$.
  - Rejects remaining tournament candidates and logs reasons.
- Checks if Phase Transition (The Jettison) conditions are met:
  - If triggered: Deactivates all Level 0 Epistemic Axioms to INACTIVE scaffolding.
  - Jettisons Epistemic Targets and restores compute budget to base capacity.

## STEP 6: Telemetry Recording & Dashboard Generation
- Syncs persistent memories (`generation_{XX}_axioms.md`, `generation_{XX}_architecture.md`).
- Emits `EpochCompleted` event.
- Saves `epoch_XXX.json` and `epoch_XXX.md` into `generations/gen_XX/epochs/`.
- Recompiles `dashboard.html` with updated velocity curves.
