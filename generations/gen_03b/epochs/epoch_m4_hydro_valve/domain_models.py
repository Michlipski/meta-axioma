"""Dynamically Compiled Domain Models for Contract: contract_soc_hydro_valve."""

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
    pressure_kpa: int = 250
    valve_locked: bool = True

    def validate_invariants(self) -> bool:
        """Structurally enforces all ContractIR invariants for this noun."""
        if not (getattr(self, 'pressure_kpa') <= 250):
            raise DomainInvariantViolationError(f"Invariant violated on CoreEntity: pressure_kpa <= 250 (got {getattr(self, 'pressure_kpa')})")
        if not (getattr(self, 'valve_locked') == True):
            raise DomainInvariantViolationError(f"Invariant violated on CoreEntity: valve_locked == True (got {getattr(self, 'valve_locked')})")
        return True

