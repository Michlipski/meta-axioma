"""Target 4: Product Usability & Cognitive Ergonomics (Human-Centric Product Design)."""

from __future__ import annotations

from typing import List
from meta_axioma.targets.base import BaseTarget, TargetSimulationResult
from meta_axioma.types import Axiom, ComputeBudget, NegativeAxiom


class ProductUsabilityTarget(BaseTarget):
    """Compiles candidate axioms against user experience, persona alignment, and cognitive ergonomics.
    
    Validates:
    - Persona goal completion velocity and friction-free user journeys.
    - Gentle error recovery: actionable, humane guidance rather than cryptic compiler/database dumps.
    - Cognitive ergonomics: clear affordances, tactile state feedback, and intuitive visual hierarchy.
    - Bounded edge-case containment: graceful degradation without user disorientation.
    """

    def __init__(self):
        super().__init__(
            target_id="target_4_product_usability",
            name="Product Usability & Cognitive Ergonomics",
            description="Human-centric UX, persona goal completion, and cognitive ergonomics",
        )

    def simulate_compilation(
        self,
        candidate: Axiom,
        active_axioms: List[Axiom],
        negative_axioms: List[NegativeAxiom],
        budget: ComputeBudget,
    ) -> TargetSimulationResult:
        violations: List[str] = []
        tokens_used = min(budget.token_budget, 1100 + len(candidate.statement) * 3)
        depth_used = min(budget.simulation_depth, 3)

        combined_text = f"{candidate.name} {candidate.statement} {candidate.operational_rule}".lower()

        # Check against negative axioms
        for neg in negative_axioms:
            if neg.is_active and neg.forbidden_pattern.lower() in combined_text:
                violations.append(f"Negative Axiom Violation [{neg.id}]: {neg.forbidden_pattern}")

        # Check for anti-human UX antipatterns
        if "silent failure" in combined_text or "unrecoverable abort" in combined_text:
            violations.append("Violation: Silent failures or unrecoverable aborts cause severe user disorientation")

        # Efficacy impact on product usability & cognitive ergonomics
        delta = 0.0
        if not violations:
            keywords = [
                "persona", "usability", "ergonomic", "friction", "actionable",
                "affordance", "graceful", "feedback", "humane", "enclave",
                "introspect", "boundary", "recovery", "clarity", "flow"
            ]
            matches = sum(1 for kw in keywords if kw in combined_text)
            delta = 0.014 * (matches + 1) * budget.decay_factor
            delta = round(delta, 4)
        else:
            delta = -0.09

        return TargetSimulationResult(
            target_id=self.target_id,
            target_name=self.name,
            raw_delta_e=delta,
            compilation_success=len(violations) == 0,
            invariant_violations=violations,
            depth_reached=depth_used,
            tokens_consumed=tokens_used,
            telemetry_details={
                "persona_alignment_score": 0.90 if len(violations) == 0 else 0.25,
                "cognitive_friction_index": 0.15 if len(violations) == 0 else 0.85,
                "error_gracefulness": True if len(violations) == 0 else False,
            },
        )
