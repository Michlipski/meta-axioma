"""Dynamically Compiled Domain Models for Contract: contract_soc_heliotropic_microclimate_studio."""

from dataclasses import dataclass, field
from typing import Any, Dict, List


class DomainInvariantViolationError(AssertionError):
    """Raised when a domain noun invariant is breached at runtime."""
    pass


@dataclass
class CoreEntity:
    """Primary domain entity"""
    entity_id: str = ''
    status: str = ''
    parcel_width_m: float = 30.0
    parcel_length_m: float = 20.0
    grid_resolution_m: float = 1.0
    total_cells_count: int = 600
    shadow_length: float = 0.0
    undo_stack_depth: int = 0

    def validate_invariants(self) -> bool:
        """Structurally enforces all ContractIR invariants for this noun."""
        if not (getattr(self, 'parcel_width_m') == 30.0):
            raise DomainInvariantViolationError(f"Invariant violated on CoreEntity: parcel_width_m == 30.0 (got {getattr(self, 'parcel_width_m')})")
        if not (getattr(self, 'parcel_length_m') == 20.0):
            raise DomainInvariantViolationError(f"Invariant violated on CoreEntity: parcel_length_m == 20.0 (got {getattr(self, 'parcel_length_m')})")
        if not (getattr(self, 'grid_resolution_m') == 1.0):
            raise DomainInvariantViolationError(f"Invariant violated on CoreEntity: grid_resolution_m == 1.0 (got {getattr(self, 'grid_resolution_m')})")
        if not (getattr(self, 'total_cells_count') == 600):
            raise DomainInvariantViolationError(f"Invariant violated on CoreEntity: total_cells_count == 600 (got {getattr(self, 'total_cells_count')})")
        if not (getattr(self, 'shadow_length') >= 0.0):
            raise DomainInvariantViolationError(f"Invariant violated on CoreEntity: shadow_length >= 0.0 (got {getattr(self, 'shadow_length')})")
        if not (getattr(self, 'undo_stack_depth') >= 0):
            raise DomainInvariantViolationError(f"Invariant violated on CoreEntity: undo_stack_depth >= 0 (got {getattr(self, 'undo_stack_depth')})")
        return True

