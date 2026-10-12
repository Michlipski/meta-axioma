"""Base interface and result containers for Tri-Fold validation targets."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List

from meta_axioma.types import Axiom, ComputeBudget, NegativeAxiom


@dataclass
class TargetSimulationResult:
    """Outcome of testing a candidate axiom against a target domain."""
    target_id: str
    target_name: str
    raw_delta_e: float
    compilation_success: bool
    invariant_violations: List[str] = field(default_factory=list)
    depth_reached: int = 0
    tokens_consumed: int = 0
    telemetry_details: Dict[str, Any] = field(default_factory=dict)


class BaseTarget(ABC):
    """Abstract specification for compilation target."""

    def __init__(self, target_id: str, name: str, description: str):
        self.target_id = target_id
        self.name = name
        self.description = description

    @abstractmethod
    def simulate_compilation(
        self,
        candidate: Axiom,
        active_axioms: List[Axiom],
        negative_axioms: List[NegativeAxiom],
        budget: ComputeBudget,
    ) -> TargetSimulationResult:
        """Simulates how the candidate axiom compiles into this target system."""
        pass
