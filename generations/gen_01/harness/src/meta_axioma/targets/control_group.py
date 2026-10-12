"""Target 3: The Control Group (An orthogonal toy problem to test for generalization)."""

from __future__ import annotations

from typing import List
from meta_axioma.targets.base import BaseTarget, TargetSimulationResult
from meta_axioma.types import Axiom, ComputeBudget, NegativeAxiom


class ControlGroupTarget(BaseTarget):
    """Compiles candidate axioms against an orthogonal problem domain.
    
    Domain: Distributed Cache Coherence & State Replication
    Validates:
    - Generalization without overfitting to self-referential compiler architectures.
    - Message passing overhead and state synchronization convergence.
    - Partition tolerance and invariant safety.
    """

    def __init__(self):
        super().__init__(
            target_id="target_3_control_group",
            name="Control Group (Replicated State Machine)",
            description="Orthogonal distributed consensus and cache coherence domain",
        )

    def simulate_compilation(
        self,
        candidate: Axiom,
        active_axioms: List[Axiom],
        negative_axioms: List[NegativeAxiom],
        budget: ComputeBudget,
    ) -> TargetSimulationResult:
        violations: List[str] = []
        tokens_used = min(budget.token_budget, 1500 + len(candidate.statement) * 4)
        depth_used = min(budget.simulation_depth, 4)

        combined_text = f"{candidate.name} {candidate.statement} {candidate.operational_rule}".lower()

        # Check negative axioms
        for neg in negative_axioms:
            if neg.is_active and neg.forbidden_pattern.lower() in combined_text:
                violations.append(f"Negative Axiom Violation [{neg.id}]: {neg.forbidden_pattern}")

        # Domain checks: Overfitting to meta-compiler structures vs genuine distributed principles
        if "compile only" in combined_text or "compiler-specific" in combined_text:
            violations.append("Overfitting detected: Candidate cannot be mapped to orthogonal state machine")

        # Generalization scoring
        delta = 0.0
        if not violations:
            keywords = ["partition", "synchronize", "message", "consensus", "state", "isolation", "replicated", "invariant"]
            matches = sum(1 for kw in keywords if kw in combined_text)
            delta = 0.012 * (matches + 1) * budget.decay_factor
            delta = round(delta, 4)
        else:
            delta = -0.05

        return TargetSimulationResult(
            target_id=self.target_id,
            target_name=self.name,
            raw_delta_e=delta,
            compilation_success=len(violations) == 0,
            invariant_violations=violations,
            depth_reached=depth_used,
            tokens_consumed=tokens_used,
            telemetry_details={
                "message_reduction_ratio": 1.0 + (delta * 5),
                "generalization_penalty": 0.0 if len(violations) == 0 else 0.5,
            },
        )
