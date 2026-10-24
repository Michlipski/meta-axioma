"""Dynamically Compiled Domain Models for Contract: contract_soc_biologics_cold_chain."""

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
    temperature_celsius: int = 8
    quorum_valid: bool = True

    def validate_invariants(self) -> bool:
        """Structurally enforces all ContractIR invariants for this noun."""
        if not (getattr(self, 'temperature_celsius') <= 8):
            raise DomainInvariantViolationError(f"Invariant violated on CoreEntity: temperature_celsius <= 8 (got {getattr(self, 'temperature_celsius')})")
        if not (getattr(self, 'quorum_valid') == True):
            raise DomainInvariantViolationError(f"Invariant violated on CoreEntity: quorum_valid == True (got {getattr(self, 'quorum_valid')})")
        return True

