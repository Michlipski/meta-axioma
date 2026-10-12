"""Validation target architectures for tri-fold verification."""

from meta_axioma.targets.base import BaseTarget, TargetSimulationResult
from meta_axioma.targets.self_constructor import SelfConstructorTarget
from meta_axioma.targets.self_evaluator import SelfEvaluatorTarget
from meta_axioma.targets.control_group import ControlGroupTarget
from meta_axioma.targets.epistemic_diversity import SearchDiversityTarget
from meta_axioma.targets.epistemic_velocity import RefutationVelocityTarget
from meta_axioma.targets.epistemic_yield import StructuralYieldTarget
from meta_axioma.targets.product_usability import ProductUsabilityTarget

__all__ = [
    "BaseTarget",
    "TargetSimulationResult",
    "SelfConstructorTarget",
    "SelfEvaluatorTarget",
    "ControlGroupTarget",
    "ProductUsabilityTarget",
    "SearchDiversityTarget",
    "RefutationVelocityTarget",
    "StructuralYieldTarget",
]

