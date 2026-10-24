"""Dynamically Compiled Domain Models for Contract: contract_soc_system_g3b_cancrizans_parent."""

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
    daughter_exit_code: int = 0
    downstream_app_verified: bool = True

    def validate_invariants(self) -> bool:
        """Structurally enforces all ContractIR invariants for this noun."""
        if not (getattr(self, 'daughter_exit_code') == 0):
            raise DomainInvariantViolationError(f'Invariant violated on CoreEntity: daughter_exit_code == 0 (got {getattr(self, 'daughter_exit_code')})')
        if not (getattr(self, 'downstream_app_verified') == True):
            raise DomainInvariantViolationError(f'Invariant violated on CoreEntity: downstream_app_verified == True (got {getattr(self, 'downstream_app_verified')})')
        return True

