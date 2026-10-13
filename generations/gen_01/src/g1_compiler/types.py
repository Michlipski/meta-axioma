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


class LinearCompilationViolation(Exception):
    """Raised when an attempt is made to bypass the non-linear search gate or perform 1-shot linear synthesis."""
    pass


class ChaosFaultType(str, Enum):
    """Types of adversarial chaos injected by the decoupled crucible."""
    ASYMMETRIC_NETSPLIT = "ASYMMETRIC_NETSPLIT"
    FLAPPING_PACKET_DROP = "FLAPPING_PACKET_DROP"
    CONCURRENCY_THRASH = "CONCURRENCY_THRASH"
    STATE_CORRUPTION = "STATE_CORRUPTION"


@dataclass
class SearchIsland:
    """An isolated search island maintaining an orthogonal architectural topology."""
    island_id: str
    name: str
    topology_type: str
    core_thesis: str
    description: str


@dataclass
class CandidateArchitecture:
    """A synthesized candidate architecture evolving along an island branch."""
    candidate_id: str
    island_id: str
    name: str
    topology_type: str
    specification_ast: Dict[str, Any]
    lineage: List[str] = field(default_factory=list)  # Ancestor candidate IDs
    generation_step: int = 0
    mutations: List[str] = field(default_factory=list)
    timestamp: float = field(default_factory=time.time)


@dataclass
class CrucibleReport:
    """Stress testing verdict emitted by the independent adversarial crucible."""
    candidate_id: str
    passed: bool
    consistency_rate: float            # 0.0 to 1.0 (target >= 0.85)
    partition_survival_rate: float     # 0.0 to 1.0
    erased_bits: float                 # Landauer bit erasure
    dissipated_joules: float           # Landauer heat dissipated: bits * k_B * T * ln(2)
    p99_latency_ms: float              # Latency under chaos contention
    faults_injected: List[Dict[str, Any]] = field(default_factory=list)
    witness_hash: str = ""             # Cryptographic SHA-256 witness
    failure_details: List[str] = field(default_factory=list)
    is_falsified: bool = False         # True if candidate was broken / proved dead end


@dataclass(frozen=True)
class BehavioralNiche:
    """Coordinates in the Quality-Diversity MAP-Elites behavioral grid."""
    consistency_bracket: int   # 0 to 4
    partition_bracket: int     # 0 to 4
    thermal_bracket: int       # 0 to 4 (based on dissipated energy)


@dataclass
class NonLinearSearchTrace:
    """Verifiable cryptographic proof of non-linear evolutionary exploration."""
    trace_id: str
    timestamp: float = field(default_factory=time.time)
    islands_explored: List[str] = field(default_factory=list)
    total_candidates_evaluated: int = 0
    candidate_history: List[CandidateArchitecture] = field(default_factory=list)
    dead_end_candidates: List[Dict[str, Any]] = field(default_factory=list)
    crucible_witnesses: List[CrucibleReport] = field(default_factory=list)
    map_elites_coverage: float = 0.0
    selected_winner_id: str = ""
    is_verified: bool = False
    verification_signature: str = ""


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
    search_trace: Optional[NonLinearSearchTrace] = None
    succession_certificate: Optional[str] = None

