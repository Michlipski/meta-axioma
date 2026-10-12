"""Simulation sandbox with dual-tier target routing (Epistemic vs Structural)."""

from __future__ import annotations

from typing import Dict, List, Optional
from meta_axioma.targets.base import BaseTarget, TargetSimulationResult
from meta_axioma.targets.self_constructor import SelfConstructorTarget
from meta_axioma.targets.self_evaluator import SelfEvaluatorTarget
from meta_axioma.targets.control_group import ControlGroupTarget
from meta_axioma.targets.product_usability import ProductUsabilityTarget
from meta_axioma.targets.epistemic_diversity import SearchDiversityTarget
from meta_axioma.targets.epistemic_velocity import RefutationVelocityTarget
from meta_axioma.targets.epistemic_yield import StructuralYieldTarget
from meta_axioma.types import Axiom, AxiomLevel, ComputeBudget, NegativeAxiom


class SimulationSandbox:
    """Isolated execution sandbox routing candidates to Epistemic or Structural validation targets."""

    def __init__(
        self,
        structural_targets: Optional[List[BaseTarget]] = None,
        epistemic_targets: Optional[List[BaseTarget]] = None,
    ):
        self.structural_targets = structural_targets or [
            SelfConstructorTarget(),
            SelfEvaluatorTarget(),
            ControlGroupTarget(),
            ProductUsabilityTarget(),
        ]

        self.epistemic_targets = epistemic_targets or [
            SearchDiversityTarget(),
            RefutationVelocityTarget(),
            StructuralYieldTarget(),
        ]
        self.is_epistemic_jettisoned: bool = False

    def jettison_epistemic_targets(self) -> None:
        """Permanently deactivates and prunes epistemic targets upon Phase Transition."""
        self.is_epistemic_jettisoned = True
        self.epistemic_targets = []

    def get_active_targets_for(self, candidate: Axiom) -> List[BaseTarget]:
        """Routes candidate to appropriate tier of validation targets."""
        if candidate.level == AxiomLevel.LEVEL_0_EPISTEMIC:
            if self.is_epistemic_jettisoned:
                raise RuntimeError("Cannot simulate Level 0 candidate: Epistemic targets have been jettisoned.")
            return self.epistemic_targets
        return self.structural_targets

    def run_simulation(
        self,
        candidate: Axiom,
        active_axioms: List[Axiom],
        negative_axioms: List[NegativeAxiom],
        budget: ComputeBudget,
    ) -> Dict[str, TargetSimulationResult]:
        """Executes candidate validation across the appropriate target tier."""
        targets = self.get_active_targets_for(candidate)
        results: Dict[str, TargetSimulationResult] = {}

        for target in targets:
            result = target.simulate_compilation(
                candidate=candidate,
                active_axioms=active_axioms,
                negative_axioms=negative_axioms,
                budget=budget,
            )
            results[target.target_id] = result

        return results
