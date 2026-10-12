---
domain: EvaluationTargets
related_domains:
  - AxiomRegistry
  - SimulationDecay
  - TelemetryAudit
---

CONSTRAINTS:
- Candidates are evaluated strictly against the target suite active for the current phase tier:
  - Phase 1 evaluates against Epistemic Targets (E1 Diversity, E2 Refutation Velocity, E3 Structural Yield).
  - Phase 2 evaluates against Structural Targets (S1 Self-Constructor, S2 Self-Evaluator, S3 Control Group).
- Compilation failures or invariant violations force negative aggregate penalty (-0.05 or lower).
- In Generation 1, Target S2 is responsible for synthesizing and formalizing the successor targets for Generation 2.

GLOSSARY:
- Target S1 (Self-Constructor): Tests recursive compilation into the bootstrapper's own AST and modular architecture.
- Target S2 (Self-Evaluator): Tests telemetry stream signal-to-noise ratio, auditability, and successor evaluation synthesis.
- Target S3 (Control Group): Tests compilation against an orthogonal problem domain (distributed cache coherence / replicated state machines).
- Target P1 (Product Usability): Tests human-centric utility, persona goal velocity, cognitive friction reduction, and gentle error recovery.
- Successor Target Synthesis: The process by which Generation 1 formulates the evaluation landscape for Generation 2.

# ENTITY: TargetSimulationResult
MUST HAVE:
- target_id: String
- target_name: String
- raw_delta_e: Float
- compilation_success: Boolean
- invariant_violations: List of String
- depth_reached: Integer
- tokens_consumed: Integer

# ENTITY: TriFoldMetrics
MUST HAVE:
- delta_e1: Float
- delta_e2: Float
- delta_e3: Float
- aggregate_delta_e: Float
- delta_e4: Float (Optional, active when Target P1 is evaluated)
- target_details: Dictionary

RULES:
- R1: When Target P1 is evaluated, aggregate_delta_e = 0.25*delta_e1 + 0.25*delta_e2 + 0.25*delta_e3 + 0.25*delta_e4.
- R2: When evaluating tri-fold alone, weights default to: w1 = 0.35, w2 = 0.35, w3 = 0.30.
- R3: If any target compilation fails or violates an invariant, aggregate_delta_e <= -0.05.


# EVENT: SimulationCompleted
TRIGGER:
- Emitted after a candidate axiom has been simulated across all active targets.
PAYLOAD:
- candidate_id
- tri_fold_metrics
- aggregate_delta_e
- violations
