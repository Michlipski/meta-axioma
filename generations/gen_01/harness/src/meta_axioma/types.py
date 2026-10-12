"""Domain types and data representations for the Axiom Bootstrapper."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class AxiomLevel(str, Enum):
    """Tiered hierarchy of axioms in the bootstrapper."""
    LEVEL_0_EPISTEMIC = "LEVEL_0_EPISTEMIC"  # Meta-axioms: How to research / synthesize
    LEVEL_1_STRUCTURAL = "LEVEL_1_STRUCTURAL"  # Structural axioms: Target systems design


class AxiomStatus(str, Enum):
    """Lifecycle status of an axiom."""
    ACTIVE = "ACTIVE"
    CANDIDATE = "CANDIDATE"
    INACTIVE = "INACTIVE"  # Retained in registry/UI as inactive scaffolding post-jettison
    PRUNED = "PRUNED"  # Permitted during The Jettison for Level 0
    REJECTED = "REJECTED"  # Failed ΔE > 0 or violated invariants
    VETOED = "VETOED"  # Rejected via HITL negative axiom injection


class PhaseState(str, Enum):
    """Macro phase of the self-constructing engine."""
    PHASE_1_META_EXPLORATION = "PHASE_1_META_EXPLORATION"  # Level 0 guiding Level 1 discovery
    PHASE_2_STRUCTURAL_EXECUTION = "PHASE_2_STRUCTURAL_EXECUTION"  # Post-jettison pure structural compilation


@dataclass
class Axiom:
    """Representation of an architectural or epistemic axiom."""
    id: str
    level: AxiomLevel
    name: str
    statement: str
    formal_expression: str
    operational_rule: str
    status: AxiomStatus = AxiomStatus.ACTIVE
    origin_epoch: int = 0
    delta_e: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "level": self.level.value,
            "name": self.name,
            "statement": self.statement,
            "formal_expression": self.formal_expression,
            "operational_rule": self.operational_rule,
            "status": self.status.value,
            "origin_epoch": self.origin_epoch,
            "delta_e": self.delta_e,
            "metadata": self.metadata,
        }


@dataclass
class NegativeAxiom:
    """Human-injected negative axiom (hard invariant / veto constraint)."""
    id: str
    name: str
    forbidden_pattern: str
    rationale: str
    injected_at_epoch: int
    is_active: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "forbidden_pattern": self.forbidden_pattern,
            "rationale": self.rationale,
            "injected_at_epoch": self.injected_at_epoch,
            "is_active": self.is_active,
        }


@dataclass
class ComputeBudget:
    """Inverse compute decay allocation for simulations."""
    active_axiom_count: int
    token_budget: int
    simulation_depth: int
    decay_factor: float


@dataclass
class TriFoldMetrics:
    """Efficacy outcomes across the validation targets."""
    delta_e1: float  # Target 1: Self-Constructor / Diversity
    delta_e2: float  # Target 2: Self-Evaluator / Velocity
    delta_e3: float  # Target 3: Control Group / Yield
    aggregate_delta_e: float
    delta_e4: float = 0.0  # Target 4: Product Usability & Ergonomics (when active)
    target_details: Dict[str, Any] = field(default_factory=dict)



class HitlAction(str, Enum):
    """Human-in-the-Loop decision actions."""
    APPROVE = "APPROVE"  # Default approve (commits top-ranked candidate with ΔE > 0)
    APPROVE_LLM = "APPROVE_LLM"  # Explicitly commit LLM candidate in comparative mode
    APPROVE_USER = "APPROVE_USER"  # Explicitly commit User seed candidate in comparative mode
    APPROVE_BOTH = "APPROVE_BOTH"  # Commit both if orthogonal and ΔE > 0
    APPROVE_SELECTED = "APPROVE_SELECTED"  # Explicitly commit a candidate by selected_candidate_id
    REJECT = "REJECT"
    REJECT_BOTH = "REJECT_BOTH"
    INJECT_NEGATIVE_AXIOM = "INJECT_NEGATIVE_AXIOM"
    FORCE_JETTISON = "FORCE_JETTISON"


@dataclass
class CandidateEvaluation:
    """Outcome of a single candidate's evaluation across the Tri-Fold targets."""
    candidate: Axiom
    metrics: TriFoldMetrics
    source: str  # "LLM" or "USER_SEED"
    is_strictly_improving: bool
    negative_violation: Optional[str] = None


@dataclass
class HitlVerdict:
    """Result of an asynchronous HITL interrupt."""
    action: HitlAction
    feedback: str = ""
    negative_axiom: Optional[NegativeAxiom] = None
    selected_candidate_id: Optional[str] = None


@dataclass
class EpochTelemetry:
    """Telemetry packet exposed at epoch boundaries."""
    epoch: int
    phase: PhaseState
    active_l0_count: int
    active_l1_count: int
    total_active: int
    current_efficacy: float
    efficacy_derivative: float
    compute_budget: ComputeBudget
    candidate_axiom: Optional[Axiom] = None
    tri_fold_metrics: Optional[TriFoldMetrics] = None
    user_candidate: Optional[Axiom] = None
    user_metrics: Optional[TriFoldMetrics] = None
    comparative_summary: Optional[Dict[str, Any]] = None
    candidate_pool: Optional[List[Axiom]] = None
    tournament_leaderboard: Optional[List[Dict[str, Any]]] = None
    decision: Optional[str] = None
    jettison_triggered: bool = False
    lookahead_analysis: Optional[Dict[str, Any]] = None
    timestamp: str = ""
