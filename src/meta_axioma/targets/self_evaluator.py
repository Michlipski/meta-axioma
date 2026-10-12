"""Target 2: The Self-Evaluator (The auditing and telemetry system)."""

from __future__ import annotations

from typing import List
from meta_axioma.targets.base import BaseTarget, TargetSimulationResult
from meta_axioma.types import Axiom, ComputeBudget, NegativeAxiom


class SelfEvaluatorTarget(BaseTarget):
    """Compiles candidate axioms into the auditing, telemetry, and HITL veto subsystem.
    
    Validates:
    - Invariant observability and audit logging fidelity.
    - Signal-to-noise ratio in telemetry streams.
    - Low-latency HITL interrupt dispatch and non-blocking safety.
    """

    def __init__(self):
        super().__init__(
            target_id="target_2_self_evaluator",
            name="Self-Evaluator",
            description="Auditing, observability, and telemetry system",
        )

    def simulate_compilation(
        self,
        candidate: Axiom,
        active_axioms: List[Axiom],
        negative_axioms: List[NegativeAxiom],
        budget: ComputeBudget,
    ) -> TargetSimulationResult:
        violations: List[str] = []
        tokens_used = min(budget.token_budget, 1000 + len(candidate.statement) * 3)
        depth_used = min(budget.simulation_depth, 3)

        combined_text = f"{candidate.name} {candidate.statement} {candidate.operational_rule}".lower()

        # Check against negative axioms
        for neg in negative_axioms:
            if neg.is_active and neg.forbidden_pattern.lower() in combined_text:
                violations.append(f"Negative Axiom Violation [{neg.id}]: {neg.forbidden_pattern}")

        # Check for unobservable state mutation
        if "hidden state" in combined_text or "untraced mutation" in combined_text:
            violations.append("Violation: Untraced internal state introduces audit blind spots")

        # Telemetry efficacy scoring
        delta = 0.0
        if not violations:
            keywords = ["observable", "audit", "telemetry", "metric", "signal", "trace", "entropy", "gradient"]
            matches = sum(1 for kw in keywords if kw in combined_text)
            delta = 0.015 * (matches + 1) * budget.decay_factor
            delta = round(delta, 4)
        else:
            delta = -0.08

        return TargetSimulationResult(
            target_id=self.target_id,
            target_name=self.name,
            raw_delta_e=delta,
            compilation_success=len(violations) == 0,
            invariant_violations=violations,
            depth_reached=depth_used,
            tokens_consumed=tokens_used,
            telemetry_details={
                "observability_gain": delta * 10,
                "audit_gap_detected": any("audit" in v for v in violations),
            },
        )
