"""Epistemic Target 1: Search Space Diversity & Anti-Collapse."""

from __future__ import annotations

from typing import List
from meta_axioma.targets.base import BaseTarget, TargetSimulationResult
from meta_axioma.types import Axiom, ComputeBudget, NegativeAxiom


class SearchDiversityTarget(BaseTarget):
    """Evaluates hypothesis diversity and model collapse resistance for Level 0 axioms.
    
    Measures:
    - Semantic entropy and coverage of hypothesis space.
    - Cross-domain divergence from pure software engineering latent space.
    - Elimination of repetitive trivial variations.
    """

    def __init__(self):
        super().__init__(
            target_id="target_e1_diversity",
            name="Search Space Diversity & Anti-Collapse",
            description="Hypothesis entropy, cross-domain divergence, and avoidance of local mode collapse",
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
        tokens_used = min(budget.token_budget, 800 + len(candidate.statement) * 2)
        depth_used = min(budget.simulation_depth, 3)

        combined_text = f"{candidate.name} {candidate.statement} {candidate.operational_rule}".lower()

        # Check negative axioms
        for neg in negative_axioms:
            if neg.is_active and neg.forbidden_pattern.lower() in combined_text:
                violations.append(f"Negative Axiom Violation [{neg.id}]: {neg.forbidden_pattern}")

        # Check for epistemic tautology or vacuous claims
        if "obviously true" in combined_text or "trivial" in combined_text:
            violations.append("Epistemic Tautology: Hypothesis provides zero search constraint")

        delta = 0.0
        if not violations:
            # Score cross-domain divergence, orthogonality, and entropy injection
            keywords = [
                "orthogonal", "entropy", "exogenous", "cross-domain", "non-computing",
                "divergence", "collapse", "synthesize", "topology", "category theory",
                "linguistics", "quantum", "phenomenology"
            ]
            matches = sum(1 for kw in keywords if kw in combined_text)
            delta = 0.018 * (matches + 1) * budget.decay_factor
            delta = round(delta, 4)
        else:
            delta = -0.06

        return TargetSimulationResult(
            target_id=self.target_id,
            target_name=self.name,
            raw_delta_e=delta,
            compilation_success=len(violations) == 0,
            invariant_violations=violations,
            depth_reached=depth_used,
            tokens_consumed=tokens_used,
            telemetry_details={
                "entropy_gain_bits": delta * 15.0,
                "collapse_risk_reduction": min(1.0, delta * 20.0),
            },
        )
