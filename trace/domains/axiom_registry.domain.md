---
domain: AxiomRegistry
related_domains:
  - SimulationDecay
  - EvaluationTargets
  - TelemetryAudit
---

CONSTRAINTS:
- AxiomRegistry owns canonical lifecycle states of all axioms, negative invariants, and system phases.
- An axiom can never be deleted from persistent memory; retired axioms transition to INACTIVE scaffolding.
- Candidates cannot be committed if they violate any active Negative Axiom or yield aggregate ΔE <= 0.
- Level 0 Epistemic Axioms cannot be added in Phase 2 (Structural Execution).

GLOSSARY:
- Active Axiom: An invariant actively governing runtime state and contributing to compute decay.
- Inactive Scaffolding: A retired axiom preserved in memory to guide generation without decaying runtime compute.
- Negative Axiom: A forbidden architectural pattern injected by human veto.
- Lifecycle Action: A state mutation (e.g., Committed, Rejected, Inactivated).

# ENTITY: Axiom
MUST HAVE:
- id: String (Pattern: ^(L0|L1)(-[A-Za-z0-9]+)?-\d{3}(_\d+)?$)
- name: String
- level: Enum (LEVEL_0_EPISTEMIC, LEVEL_1_STRUCTURAL)
- statement: String
- formal_expression: String
- operational_rule: String
- status: Enum (ACTIVE, INACTIVE, CANDIDATE, REJECTED, SUPERSEDED)
- origin_epoch: Integer
- delta_e: Float

RULES:
- R1: Axioms in ACTIVE status contribute to active invariant count n in compute decay.
- R2: Axioms in INACTIVE status are excluded from compute decay calculation.
- R3: Level 0 axioms transition to INACTIVE when PhaseTransitionJettison event occurs.

# ENTITY: NegativeAxiom
MUST HAVE:
- id: String (Pattern: ^NEG(-[A-Za-z0-9]+)?-\d{3}$)
- forbidden_pattern: String
- rationale: String
- injected_epoch: Integer
- is_active: Boolean

RULES:
- R1: Any candidate whose text or operational rule contains a forbidden_pattern is immediately rejected with -0.10 penalty.

# EVENT: AxiomCommitted
TRIGGER:
- Emitted when a candidate passes simulation with aggregate ΔE > 0 and is approved.
PAYLOAD:
- axiom_id
- epoch
- delta_e
- phase

# EVENT: AxiomJettisoned
TRIGGER:
- Emitted during The Jettison phase transition.
PAYLOAD:
- deactivated_axiom_ids
- epoch
- compute_dividend
