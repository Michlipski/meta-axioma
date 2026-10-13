---
domain: EvaluationTargets
related_domains:
  - AxiomRegistry
  - SimulationDecay
  - TelemetryAudit
---

CONSTRAINTS:
- Candidates are evaluated strictly against the target suite active for the current generation and phase tier:
  - Generation 1 Phase 1 evaluates against Epistemic Targets (E1 Diversity, E2 Refutation Velocity, E3 Structural Yield).
  - Generation 1 Phase 2 evaluates against Structural Targets (S1 Self-Constructor, S2 Self-Evaluator, S3 Control Group, P1 Usability).
  - Generation 2 evaluates against the 4 Endogenous Successor Targets (G2-T1 Functorial Compilation, G2-T2 Self-Healing Enclaves, G2-T3 Cognitive Ergonomics & Utility, G2-T4 Landauer Concurrency Efficiency).
  - Generation 3 evaluates against the 4 Distributed Systems Targets (G3-T1 Distributed Sheaf Consensus, G3-T2 Zero-Downtime Cluster Hot-Patching, G3-T3 End-to-End Client Servicing & Ergonomics, G3-T4 Thermodynamic Cluster Dissipation).
- Compilation failures or invariant violations force negative aggregate penalty (-0.05 or lower).
- In Generation 1, Target S2 was responsible for synthesizing and formalizing the successor targets for Generation 2.
- In Generation 2, the compiler was responsible for synthesizing and formalizing the successor targets for Generation 3.
- In Generation 3, the compiler targets convergence toward the High-Level Jettison (HLJ).

GLOSSARY:
- Target S1 (Self-Constructor): Tests recursive compilation into the bootstrapper's own AST and modular architecture.
- Target S2 (Self-Evaluator): Tests telemetry stream signal-to-noise ratio, auditability, and successor evaluation synthesis.
- Target S3 (Control Group): Tests compilation against an orthogonal problem domain (distributed cache coherence / replicated state machines).
- Target P1 (Product Usability): Tests human-centric utility, persona goal velocity, cognitive friction reduction, and gentle error recovery.
- Target G2-T1 (Higher-Order Functorial Compilation): Tests Galois adjunctions and multi-substrate preservation.
- Target G2-T2 (Autonomous Self-Healing & Enclave Verification): Tests bounded multi-pass invariant restoration with zero blast leakage.
- Target G2-T3 (Teleological Non-Generator Utility & Ergonomics): Tests persona alignment, mental model KL divergence, and ergonomic goal velocity.
- Target G2-T4 (Landauer Thermodynamic Concurrency Efficiency): Tests dissipated erasure joules across concurrent execution pipelines.
- Target G3-T1 (Distributed Sheaf Consensus & Partition Coherence): Tests local-to-global state gluing under network partitions.
- Target G3-T2 (Zero-Downtime Cluster Hot-Patching): Tests live microservice hot-reloading with zero state corruption.
- Target G3-T3 (End-to-End Client Servicing & Ergonomics): Tests complex backends servicing reactive frontends with <100ms latency.
- Target G3-T4 (Thermodynamic Cluster Dissipation): Tests Landauer bit-erasure memory bounds across backend worker clusters.
- Successor Target Synthesis: The process by which Generation N formulates the evaluation landscape for Generation N+1.

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
