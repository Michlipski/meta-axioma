"""Type definitions and data representations for System G_1 Compiler."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional
import time


class CompilerPhase(str, Enum):
    """Execution phases of the System G_1 compiler."""
    INITIALIZATION = "INITIALIZATION"
    PIPELINE_EXECUTION = "PIPELINE_EXECUTION"
    INVARIANT_AUDITING = "INVARIANT_AUDITING"
    BASIS_SYNTHESIS = "BASIS_SYNTHESIS"
    COMPLETED = "COMPLETED"


@dataclass(frozen=True)
class SystemState:
    """Immutable state snapshot adhering to Spinozan substance and functorial evolution."""
    state_id: str
    epoch: int
    payload: Dict[str, Any] = field(default_factory=dict)
    entropy_bits: float = 0.0
    timestamp: float = field(default_factory=time.time)

    def transition(self, delta: Dict[str, Any], entropy_delta: float = 0.0) -> "SystemState":
        """Pure deterministic transition yielding a new immutable snapshot."""
        new_payload = dict(self.payload)
        new_payload.update(delta)
        return SystemState(
            state_id=f"{self.state_id}_t{int(time.time()*1000)%100000}",
            epoch=self.epoch,
            payload=new_payload,
            entropy_bits=max(0.0, self.entropy_bits + entropy_delta),
            timestamp=time.time(),
        )


@dataclass
class AxiomVerificationResult:
    """Result of an invariant verification check."""
    axiom_id: str
    axiom_name: str
    passed: bool
    details: Dict[str, Any] = field(default_factory=dict)
    message: str = ""


@dataclass
class G2SuccessorTarget:
    """Evaluation target synthesized by System G_1 for Generation 2 (G_2)."""
    target_id: str
    name: str
    description: str
    weight: float
    metric_formalization: str
    non_generator_telos_alignment: str


@dataclass
class G2CandidateBasisAxiom:
    """Candidate foundational axiom formulated by System G_1 for Generation 2 (G_2)."""
    id: str
    name: str
    level: str  # e.g., "LEVEL_1_STRUCTURAL" or "LEVEL_0_EPISTEMIC"
    statement: str
    formal_expression: str
    operational_rule: str
    exogenous_domain: str
    teleological_purpose: str


@dataclass
class G2SuccessorBasis:
    """The complete basis and evaluation architecture synthesized by System G_1 for Generation 2."""
    generation: int = 2
    formulated_by: str = "System G_1 Autonomous Compiler"
    timestamp: float = field(default_factory=time.time)
    targets: List[G2SuccessorTarget] = field(default_factory=list)
    basis_axioms: List[G2CandidateBasisAxiom] = field(default_factory=list)
    inherited_feedback_dossier: Optional[Dict[str, Any]] = None
    inherited_negative_constraints: List[str] = field(default_factory=list)
    lessons_learned_summary: List[str] = field(default_factory=list)
    high_level_jettison_awareness: str = (
        "Active teleological orientation towards optimizing non-generator systems "
        "(production software that humans love, find useful, and control)."
    )
    operational_charter: str = ""
