"""Generation 4b Compiler Statechart Engine (`compiler/statechart.py`).

Enforces:
- [L1-002] Deterministic Statechart Transitions & Millisecond Latency Tracking.
- [L1-G4B-001] Service-Oriented Sovereign Mesh Protocol Standardization.
- [INV-G4B-CAUSAL-001..003] 3-Phase Causal Convergence & RFC Escalation Lifecycle.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
import time
from typing import Any, Dict, List, Optional, Set


class StatechartTransitionError(Exception):
    """Raised when an illegal state machine transition is attempted."""
    pass


class CompilationPhase(str, Enum):
    """Formal lifecycle phases for Generation 4b compilation."""
    IDLE = "IDLE"
    PHASE_1_RESEARCH = "PHASE_1_RESEARCH"
    PHASE_2A_BUILD = "PHASE_2A_BUILD"
    PHASE_2B_GROUNDING = "PHASE_2B_GROUNDING"
    PHASE_2C_QA = "PHASE_2C_QA"
    PHASE_3_AUDIT = "PHASE_3_AUDIT"
    PHASE_4_TELEMETRY_SEAL = "PHASE_4_TELEMETRY_SEAL"
    RFC_ESCALATION = "RFC_ESCALATION"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


@dataclass
class TransitionRecord:
    """Historical audit record of an enacted state transition."""
    from_phase: str
    to_phase: str
    event: str
    timestamp_unix_ns: int
    duration_ms: float
    payload: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class CompilationStatechart:
    """Deterministic hierarchical state machine governing SystemG4bCompiler orchestration."""

    LEGAL_TRANSITIONS: Dict[CompilationPhase, Set[CompilationPhase]] = {
        CompilationPhase.IDLE: {CompilationPhase.PHASE_1_RESEARCH, CompilationPhase.FAILED},
        CompilationPhase.PHASE_1_RESEARCH: {
            CompilationPhase.PHASE_2A_BUILD,
            CompilationPhase.RFC_ESCALATION,
            CompilationPhase.FAILED,
        },
        CompilationPhase.PHASE_2A_BUILD: {
            CompilationPhase.PHASE_2B_GROUNDING,
            CompilationPhase.RFC_ESCALATION,
            CompilationPhase.FAILED,
        },
        CompilationPhase.PHASE_2B_GROUNDING: {
            CompilationPhase.PHASE_2C_QA,
            CompilationPhase.RFC_ESCALATION,
            CompilationPhase.FAILED,
        },
        CompilationPhase.PHASE_2C_QA: {
            CompilationPhase.PHASE_3_AUDIT,
            CompilationPhase.RFC_ESCALATION,
            CompilationPhase.FAILED,
        },
        CompilationPhase.PHASE_3_AUDIT: {
            CompilationPhase.PHASE_4_TELEMETRY_SEAL,
            CompilationPhase.RFC_ESCALATION,
            CompilationPhase.FAILED,
        },
        CompilationPhase.PHASE_4_TELEMETRY_SEAL: {
            CompilationPhase.COMPLETED,
            CompilationPhase.FAILED,
        },
        CompilationPhase.RFC_ESCALATION: {
            CompilationPhase.PHASE_1_RESEARCH,
            CompilationPhase.PHASE_2A_BUILD,
            CompilationPhase.FAILED,
        },
        CompilationPhase.COMPLETED: {CompilationPhase.IDLE},
        CompilationPhase.FAILED: {CompilationPhase.IDLE},
    }

    CORE_COMPILATION_PHASES: Set[CompilationPhase] = {
        CompilationPhase.PHASE_1_RESEARCH,
        CompilationPhase.PHASE_2A_BUILD,
        CompilationPhase.PHASE_2B_GROUNDING,
        CompilationPhase.PHASE_2C_QA,
        CompilationPhase.PHASE_3_AUDIT,
        CompilationPhase.PHASE_4_TELEMETRY_SEAL,
        CompilationPhase.COMPLETED,
    }

    def __init__(self, initial_phase: CompilationPhase = CompilationPhase.IDLE) -> None:
        self.current_phase = initial_phase
        self.history: List[TransitionRecord] = []
        self.visited_phases: Set[CompilationPhase] = {initial_phase}
        self.last_transition_time_ns: int = time.time_ns()

    def transition(
        self,
        to_phase: CompilationPhase,
        event: str = "",
        payload: Optional[Dict[str, Any]] = None,
    ) -> TransitionRecord:
        """Enacts a validated transition to the target phase, recording latency."""
        allowed = self.LEGAL_TRANSITIONS.get(self.current_phase, set())
        if to_phase not in allowed and to_phase != CompilationPhase.FAILED:
            raise StatechartTransitionError(
                f"Illegal state transition from {self.current_phase.value} to {to_phase.value}. "
                f"Permitted next phases: {[p.value for p in allowed]}"
            )

        now_ns = time.time_ns()
        duration_ms = (now_ns - self.last_transition_time_ns) / 1_000_000.0

        record = TransitionRecord(
            from_phase=self.current_phase.value,
            to_phase=to_phase.value,
            event=event or f"TRANSITION_TO_{to_phase.value}",
            timestamp_unix_ns=now_ns,
            duration_ms=duration_ms,
            payload=payload or {},
        )

        self.history.append(record)
        self.visited_phases.add(to_phase)
        self.current_phase = to_phase
        self.last_transition_time_ns = now_ns
        return record

    @property
    def coverage_pct(self) -> float:
        """Computes visited percentage of the canonical compilation phases."""
        visited_core = self.visited_phases.intersection(self.CORE_COMPILATION_PHASES)
        return (len(visited_core) / len(self.CORE_COMPILATION_PHASES)) * 100.0

    def get_timeline(self) -> List[Dict[str, Any]]:
        """Returns ordered timeline of all transitions."""
        return [r.to_dict() for r in self.history]
