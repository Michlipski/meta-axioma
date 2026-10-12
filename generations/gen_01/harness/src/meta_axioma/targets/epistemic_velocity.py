"""Epistemic Target 2: Refutation Velocity & Empirical Falsifiability."""

from __future__ import annotations

from typing import List
from meta_axioma.targets.base import BaseTarget, TargetSimulationResult
from meta_axioma.types import Axiom, ComputeBudget, NegativeAxiom


class RefutationVelocityTarget(BaseTarget):
    """Evaluates empirical falsifiability and compute tokens to refute invalid claims.
    
    Measures:
    - Finite-step verifiability within budget T(n).
    - Rapid falsification of unpromising candidates (failing fast).
    - Penalty for unfalsifiable philosophical dogma.
    """

    def __init__(self):
        super().__init__(
            target_id="target_e2_velocity",
            name="Refutation Velocity & Falsifiability",
            description="Finite refutation bounds, verification token efficiency, and avoidance of unfalsifiable claims",
        )
        self.tier = "EPISTEMIC"

    def simulate_compilation(
        self,
        candidate: Axiom,
        active_axioms: List[Axiom],
        negative_axioms: List[NegativeAxiom],
        budget: ComputeBudget,
    ) -> TargetSimulationResult:
        violations: List[str] = []
        tokens_used = min(budget.token_budget, 900 + len(candidate.statement) * 3)
        depth_used = min(budget.simulation_depth, 3)

        combined_text = f"{candidate.name} {candidate.statement} {candidate.operational_rule}".lower()

        # Check negative axioms
        for neg in negative_axioms:
            if neg.is_active and neg.forbidden_pattern.lower() in combined_text:
                violations.append(f"Negative Axiom Violation [{neg.id}]: {neg.forbidden_pattern}")

        # Unfalsifiability trap: claims that cannot be disproven by simulation
        if "untestable" in combined_text or "dogma" in combined_text:
            violations.append("Violation: Unfalsifiable meta-axiom cannot be bound to finite compute checks")

        delta = 0.0
        if not violations:
            # Score operational clarity, falsification rules, and constraint bounds
            keywords = [
                "falsifiable", "refut", "constraint", "bound", "verif", "test",
                "operational", "rule", "reject", "metric", "gradient", "finite"
            ]
            matches = sum(1 for kw in keywords if kw in combined_text)
            delta = 0.016 * (matches + 1) * budget.decay_factor
            delta = round(delta, 4)
        else:
            delta = -0.07

        return TargetSimulationResult(
            target_id=self.target_id,
            target_name=self.name,
            raw_delta_e=delta,
            compilation_success=len(violations) == 0,
            invariant_violations=violations,
            depth_reached=depth_used,
            tokens_consumed=tokens_used,
            telemetry_details={
                "refutation_speedup_factor": 1.0 + (delta * 12.0),
                "unfalsifiable_degrees_of_freedom": 0 if len(violations) == 0 else 3,
            },
        )
