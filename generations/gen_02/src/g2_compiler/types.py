"""Formal types and data structures for System G_2.

System G_2 is built from the ground up to embody:
- [L1-G2-001] Adjoint Galois Substrate Connection & Multi-Target Preservation
- [L1-G2-002] Ephemeral Self-Healing Invariant Restoration Loop
- [L1-G2-003] Cognitive Ergonomics & Persona Alignment Invariance
- [L1-G2-004] Introspectable Zero-Trust Capability Scoping
- [L1-G2-005] Mandatory Human Intent Elicitation & Grounding Boundary
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional
import time


class SubstrateType(str, Enum):
    """Execution substrate runtimes supported by Generation 2."""
    CLI = "CLI"
    WEB_PWA = "WEB_PWA"
    MICROSERVICE = "MICROSERVICE"
    EMBEDDED_EDGE = "EMBEDDED_EDGE"


class RepairStatus(str, Enum):
    """Status of self-healing remediation passes."""
    HEALED = "HEALED"
    UNRECOVERABLE = "UNRECOVERABLE"
    NO_INFRACTION = "NO_INFRACTION"


class GenerationalRegressionFault(Exception):
    """Raised when an operation violates an inherited transgenerational invariant (e.g. NEG-G2-001)."""
    pass


class CapabilitySecurityFault(Exception):
    """Raised when an operation attempts unscoped or unauthorized tool access."""
    pass


@dataclass
class IntentAST:
    """High-level declarative user intent AST."""
    intent_id: str
    action: str
    target_noun: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    constraints: List[str] = field(default_factory=list)


@dataclass
class SubstrateAST:
    """Lower-level execution substrate representation."""
    substrate: SubstrateType
    payload: Dict[str, Any]
    executable_code: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class GaloisRoundTripAudit:
    """Audit result verifying adjoint Galois connection F ⊣ G."""
    original_intent: IntentAST
    projected_substrate: SubstrateAST
    reflected_intent: IntentAST
    unit_satisfied: bool
    counit_satisfied: bool
    round_trip_closure_error: float
    is_valid: bool


@dataclass
class SelfHealingResult:
    """Telemetry emitted by the ephemeral self-healing engine."""
    operation_name: str
    attempts_executed: int
    max_attempts: int
    infractions_detected: List[str]
    remediations_applied: List[str]
    blast_leakage_detected: bool
    status: RepairStatus
    execution_result: Any = None


@dataclass
class PersonaModel:
    """Mental model representation of a target human persona."""
    persona_name: str
    domain_familiarity: float  # [0.0, 1.0]
    expected_vocabulary: List[str]
    daily_goals: List[str]
    tolerance_threshold: float  # max friction acceptable


@dataclass
class ErgonomicsAuditResult:
    """Quantitative measurement of cognitive ergonomics and persona alignment."""
    persona_name: str
    kl_divergence: float
    cognitive_friction: float
    persona_goal_velocity: float
    utility_score: float
    is_acceptable: bool
    rejection_reasons: List[str] = field(default_factory=list)


@dataclass
class CapabilityToken:
    """Introspectable cryptographic capability token."""
    token_id: str
    persona: str
    allowed_actions: List[str]
    issued_at: float
    expires_at: float
    nonce: str
    cryptographic_witness: str  # SHA-256 HMAC or signature witness


@dataclass
class HumanIntentWitness:
    """Witness artifact certifying Phase 0 human elicitation."""
    witness_id: str
    application_id: str
    persona_name: str
    jtbd_summary: str
    daily_workflow: str
    utility_metric_definition: str
    signed_off_by_human: bool
    signed_at: float
    witness_hash: str


@dataclass
class G3SuccessorTarget:
    """Evaluation target synthesized by System G_2 for Generation 3."""
    target_id: str
    name: str
    description: str
    weight: float
    metric_formalization: str
    non_generator_telos_alignment: str


@dataclass
class G3CandidateBasisAxiom:
    """Foundational structural basis axiom synthesized by System G_2 for Generation 3."""
    id: str
    name: str
    level: str
    statement: str
    formal_expression: str
    operational_rule: str
    exogenous_domain: str
    teleological_purpose: str


@dataclass
class G3SuccessorBasis:
    """Complete assembled successor basis package for Generation 3."""
    generation: int
    formulated_by: str
    timestamp: float
    targets: List[G3SuccessorTarget]
    basis_axioms: List[G3CandidateBasisAxiom]
    inherited_feedback_dossier: Optional[Dict[str, Any]]
    inherited_negative_constraints: List[str]
    operational_charter: str
    search_trace: Optional[Any] = None
    succession_certificate: Optional[str] = None



@dataclass
class G2TargetEvaluation:
    """Evaluation result for one of Generation 2's 4 targets."""
    target_id: str
    target_name: str
    raw_score: float
    weighted_score: float
    passed: bool
    audit_details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class G2CompilationResult:
    """Full outcome of a System G_2 compilation pass."""
    success: bool
    generation: int = 2
    epoch: int = 1
    target_evaluations: List[G2TargetEvaluation] = field(default_factory=list)
    aggregate_delta_e: float = 0.0
    structural_axioms_verified: int = 0
    inherited_vetoes_enforced: int = 0
    g3_successor_basis_synthesized: bool = False
    audit_witnesses: List[str] = field(default_factory=list)
