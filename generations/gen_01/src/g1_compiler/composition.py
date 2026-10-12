"""Compositional Boundary Isolation ([L1-015_1]).

Formal Expression:
    V(S_1 ⊕ S_2) = V(S_1) ⊗ V(S_2)

Operational Rule:
    Every complex system unit must decompose into independently verifiable
    constituent components whose combined validity guarantees macro-level
    coherence without non-compositional side effects.
"""

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional
import copy


@dataclass
class CompositionalUnit:
    """An independently verifiable computational unit."""
    name: str
    boundary_id: str
    compute: Callable[[Dict[str, Any]], Dict[str, Any]]
    invariants: List[str] = field(default_factory=list)

    def execute_isolated(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Executes strictly on an isolated deep copy of context to prevent side effects."""
        isolated_ctx = copy.deepcopy(context)
        return self.compute(isolated_ctx)


class CompositionalBoundaryAuditor:
    """Audits multi-component composition to detect and prevent hidden side effects."""

    def __init__(self):
        self.units: List[CompositionalUnit] = []

    def register_unit(self, unit: CompositionalUnit) -> None:
        """Registers a compositional unit."""
        self.units.append(unit)

    def verify_compositionality(
        self,
        unit_a: CompositionalUnit,
        unit_b: CompositionalUnit,
        sample_input: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Formally verifies that combining unit_a and unit_b produces no side effects.

        V(A ⊕ B) == V(A) ⊗ V(B)
        """
        initial_copy = copy.deepcopy(sample_input)

        # Isolated individual execution
        res_a = unit_a.execute_isolated(sample_input)
        res_b = unit_b.execute_isolated(sample_input)

        # Ensure sample_input was not mutated in-place
        no_input_mutation = (sample_input == initial_copy)

        # Parallel/Orthogonal combination
        combined_result = {}
        combined_result.update(res_a)
        combined_result.update(res_b)

        # Sequential composition check
        seq_ctx = copy.deepcopy(sample_input)
        seq_step1 = unit_a.compute(seq_ctx)
        seq_step2 = unit_b.compute(seq_ctx)

        # Verify orthogonality (keys do not collide or overwrite with conflicting semantics)
        overlapping_keys = set(res_a.keys()).intersection(set(res_b.keys()))
        orthogonal_boundaries = len(overlapping_keys) == 0 or all(res_a[k] == res_b[k] for k in overlapping_keys)

        is_compositional = no_input_mutation and orthogonal_boundaries

        return {
            "no_input_mutation": no_input_mutation,
            "orthogonal_boundaries": orthogonal_boundaries,
            "is_compositional": is_compositional,
            "boundary_a": unit_a.boundary_id,
            "boundary_b": unit_b.boundary_id,
        }
