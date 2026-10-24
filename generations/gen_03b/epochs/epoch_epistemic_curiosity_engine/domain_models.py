"""Dynamically Compiled Domain Models for Contract: contract_soc_epistemic_curiosity_engine."""

from dataclasses import dataclass, field
from typing import Any, Dict, List


class DomainInvariantViolationError(AssertionError):
    """Raised when a domain noun invariant is breached at runtime."""
    pass


@dataclass
class EpistemicValidatorGate:
    """Formal validator certifying concept integration across Sheaf-Quorum nodes."""
    gate_id: str = ''
    target_state: str = ''
    quorum_valid: bool = True

    def validate_invariants(self) -> bool:
        """Structurally enforces all ContractIR invariants for this noun."""
        if not (getattr(self, 'quorum_valid') == True):
            raise DomainInvariantViolationError(f"Invariant violated on EpistemicValidatorGate: quorum_valid == True (got {getattr(self, 'quorum_valid')})")
        return True


@dataclass
class ExplorerKnowledgeBoundary:
    """Tracks the Explorer's verified category theory stratum and rollback count."""
    explorer_id: str = ''
    active_stratum: str = ''
    mastery_of_morphisms: bool = True
    exploring_functors_entered: bool = True
    dead_end_rollbacks: int = 0

    def validate_invariants(self) -> bool:
        """Structurally enforces all ContractIR invariants for this noun."""
        if not (getattr(self, 'mastery_of_morphisms') == True):
            raise DomainInvariantViolationError(f"Invariant violated on ExplorerKnowledgeBoundary: mastery_of_morphisms == True (got {getattr(self, 'mastery_of_morphisms')})")
        if not (getattr(self, 'dead_end_rollbacks') >= 0):
            raise DomainInvariantViolationError(f"Invariant violated on ExplorerKnowledgeBoundary: dead_end_rollbacks >= 0 (got {getattr(self, 'dead_end_rollbacks')})")
        return True


@dataclass
class SocraticProbeSession:
    """Local RTX 4060 Ollama (qwen2.5) dialectical probe session."""
    probe_id: str = ''
    ollama_endpoint: str = ''
    model_tag: str = ''
    latency_ms: int = 25
    vram_mb: int = 8192

    def validate_invariants(self) -> bool:
        """Structurally enforces all ContractIR invariants for this noun."""
        if not (getattr(self, 'latency_ms') <= 25):
            raise DomainInvariantViolationError(f"Invariant violated on SocraticProbeSession: latency_ms <= 25 (got {getattr(self, 'latency_ms')})")
        if not (getattr(self, 'vram_mb') >= 8192):
            raise DomainInvariantViolationError(f"Invariant violated on SocraticProbeSession: vram_mb >= 8192 (got {getattr(self, 'vram_mb')})")
        return True

