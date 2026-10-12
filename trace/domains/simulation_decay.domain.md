---
domain: SimulationDecay
related_domains:
  - AxiomRegistry
  - EvaluationTargets
---

CONSTRAINTS:
- SimulationDecay calculates compute token allocations and simulation depth limits per epoch.
- Active invariant count n is strictly derived from AxiomRegistry's ACTIVE axioms.
- Token budget can never drop below min_token_budget (1,000) or simulation depth below min_depth (2).
- Lookahead radar must never mutate active canonical state during speculative rollouts.

GLOSSARY:
- Compute Budget: The token and tree-depth limits allocated for simulation in a given epoch.
- Decay Coefficient (alpha): Rate of compute degradation as invariants accumulate (default 0.5).
- Speculative Lookahead: Branching rollout of counterfactual futures (Branch A Jettison vs Branch B Retain).
- Lookahead Differential (Lambda): Net efficacy advantage of executing an immediate phase transition over horizon H.

# ENTITY: ComputeBudget
MUST HAVE:
- epoch: Integer
- active_axiom_count: Integer
- token_budget: Integer
- simulation_depth: Integer
- decay_factor: Float

RULES:
- R1: token_budget = max(1000, round(10000 / (1 + 0.5 * (active_axiom_count - 2))))
- R2: simulation_depth = max(2, round(8 / (1 + 0.5 * (active_axiom_count - 2))))
- R3: decay_factor = token_budget / 10000

# ENTITY: LookaheadSpeculation
MUST HAVE:
- horizon_h: Integer
- branch_a_jettison_efficacy: Float
- branch_b_retain_efficacy: Float
- net_lookahead_differential: Float
- recommendation: Enum (EXECUTE_JETTISON, RETAIN_CURRENT_PHASE)

RULES:
- R1: Net lookahead differential Lambda = branch_a_jettison_efficacy - branch_b_retain_efficacy.
- R2: If Lambda > 0 and epoch >= 10 and n_epistemic >= 10, recommendation is EXECUTE_JETTISON.

# EVENT: BudgetCalculated
TRIGGER:
- Emitted at the start of each epoch before candidate generation.
PAYLOAD:
- epoch
- active_count
- token_budget
- simulation_depth
