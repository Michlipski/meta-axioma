"""Epistemic Target 3: Structural Translation Yield & Viability Rate."""

from __future__ import annotations

from typing import List
from meta_axioma.targets.base import BaseTarget, TargetSimulationResult
from meta_axioma.types import Axiom, ComputeBudget, NegativeAxiom


class StructuralYieldTarget(BaseTarget):
    """Evaluates the yield rate of actionable Level 1 structural systems axioms produced by this meta-rule.
    
    Measures:
    - Downstream translation viability: Does this rule produce concrete code invariants?
    - Elimination of floating philosophical abstractions with zero implementation mappings.
    - Transferability across heterogeneous architectural domains.
    """

    def __init__(self):
        super().__init__(
            target_id="target_e3_yield",
            name="Structural Translation Yield",
            description="Conversion efficiency of epistemic principles into viable Level 1 structural systems axioms",
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
        tokens_used = min(budget.token_budget, 1100 + len(candidate.statement) * 3)
        depth_used = min(budget.simulation_depth, 3)

        combined_text = f"{candidate.name} {candidate.statement} {candidate.operational_rule}".lower()

        # Check negative axioms
        for neg in negative_axioms:
            if neg.is_active and neg.forbidden_pattern.lower() in combined_text:
                violations.append(f"Negative Axiom Violation [{neg.id}]: {neg.forbidden_pattern}")

        # Check for un-translatable abstractions
        if "pure theory" in combined_text or "non-implementable" in combined_text:
            violations.append("Violation: Candidate explicitly resists systems architectural implementation")

        delta = 0.0
        if not violations:
            # Score translation clarity, concrete architectural projection, and cross-domain mapping
            keywords = [
                "topological", "translation", "architecture", "systems", "invariant",
                "structural", "principle", "extract", "synthesize", "domain", "construct"
            ]
            matches = sum(1 for kw in keywords if kw in combined_text)
            delta = 0.015 * (matches + 1) * budget.decay_factor
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
                "projected_l1_yield_percentage": 75.0 + (delta * 500.0),
                "untranslatable_abstractness_penalty": 0.0 if len(violations) == 0 else 0.8,
            },
        )
