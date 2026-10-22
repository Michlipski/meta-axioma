"""Dynamic Weighted Recursion & Worker Taxonomy Models for System G2b."""

from dataclasses import dataclass, field
from enum import Enum
import os
from typing import Any, Dict, List, Optional


class WorkerType(str, Enum):
    # Closed Prescribed Worker Taxonomy
    ORCHESTRATOR = "orchestrator"
    RESEARCH = "research"
    SYNTHESIS = "synthesis"
    ANTI_MOCK_LINTER = "anti_mock_linter"
    MODEL_CHECKER = "model_checker"
    STRUCTURAL_REGULATOR = "structural_regulator"
    USABILITY_AUDITOR = "usability_auditor"
    ADVERSARIAL_FALSIFIER = "adversarial_falsifier"
    SUBSTRATE_RUNNER = "substrate_runner"

    # Category Aliases for backwards compatibility
    EXPLORATORY_RESEARCH = "research"
    FRACTAL_DECOMPOSITION = "orchestrator"
    TERMINAL_SINK = "terminal_sink"

    @property
    def depth_weight(self) -> float:
        """Effective stack depth consumption per invocation."""
        if self in (WorkerType.RESEARCH, WorkerType.EXPLORATORY_RESEARCH):
            return 0.5
        elif self in (WorkerType.ORCHESTRATOR, WorkerType.SYNTHESIS, WorkerType.FRACTAL_DECOMPOSITION):
            return 1.0
        return 0.0  # Terminal sinks execute and conclude without stack propagation

    @property
    def is_terminal(self) -> bool:
        """Terminal nodes are strictly forbidden from spawning child subagents."""
        return self in (
            WorkerType.TERMINAL_SINK,
            WorkerType.ANTI_MOCK_LINTER,
            WorkerType.MODEL_CHECKER,
            WorkerType.STRUCTURAL_REGULATOR,
            WorkerType.USABILITY_AUDITOR,
            WorkerType.ADVERSARIAL_FALSIFIER,
            WorkerType.SUBSTRATE_RUNNER,
        )


@dataclass
class BoundaryOpinion:
    wants_depth_extension: bool
    confidence: float
    rationale: str
    estimated_token_cost: int
    worker_type: WorkerType
    subgoal: str


@dataclass
class SubagentSelectionDecision:
    worker_type: WorkerType
    chosen: bool
    rationale: str
    allotted_tokens: int = 0
    used_tokens: int = 0
    self_used_tokens: int = 0
    subgoal: str = ""


PRESCRIBED_TAXONOMY: List[WorkerType] = [
    WorkerType.ORCHESTRATOR,
    WorkerType.RESEARCH,
    WorkerType.SYNTHESIS,
    WorkerType.ANTI_MOCK_LINTER,
    WorkerType.MODEL_CHECKER,
    WorkerType.STRUCTURAL_REGULATOR,
    WorkerType.USABILITY_AUDITOR,
    WorkerType.ADVERSARIAL_FALSIFIER,
    WorkerType.SUBSTRATE_RUNNER,
]


def build_taxonomic_selection_evaluations(
    parent_node: 'RecursionNode',
    chosen_decisions: List[SubagentSelectionDecision],
    rejection_rationales: Dict[WorkerType, str],
) -> List[SubagentSelectionDecision]:
    """Guarantees every candidate worker in the closed prescribed taxonomy is evaluated.
    
    If a worker type is chosen, its chosen decisions are recorded.
    If a worker type is not chosen, its rejection rationale is recorded.
    Enforces that all 9 worker types are evaluated without omission.
    """
    evaluations: List[SubagentSelectionDecision] = []
    chosen_types = {d.worker_type for d in chosen_decisions}

    for worker_type in PRESCRIBED_TAXONOMY:
        if worker_type in chosen_types:
            for d in chosen_decisions:
                if d.worker_type == worker_type:
                    evaluations.append(d)
        else:
            rationale = rejection_rationales.get(
                worker_type,
                f"Candidate {worker_type.value} not required for {parent_node.name} ({parent_node.subgoal or parent_node.node_id}) at depth {parent_node.depth}."
            )
            evaluations.append(
                SubagentSelectionDecision(
                    worker_type=worker_type,
                    chosen=False,
                    rationale=rationale,
                )
            )

    evaluated_types = {d.worker_type for d in evaluations}
    missing = set(PRESCRIBED_TAXONOMY) - evaluated_types
    if missing:
        raise ValueError(f"Prescribed worker taxonomy incomplete: missing {missing}")

    return evaluations


@dataclass
class RecursionNode:
    node_id: str
    name: str
    worker_type: WorkerType
    subgoal: str = ""
    depth: int = 0
    effective_depth: float = 0.0
    token_cost: int = 0  # Inclusive allotment for this node and its descendants
    self_allotted: int = 0  # Tokens allotted for this node's own direct execution
    self_used: int = 0  # Tokens consumed directly by this node itself
    tokens_used: int = 0  # Total tokens consumed by this node and all its descendants
    status: str = "PENDING"  # "PENDING" | "RUNNING" | "SUCCESS" | "FAILED" | "REPAIRED"
    parent_id: Optional[str] = None
    children: List['RecursionNode'] = field(default_factory=list)
    boundary_opinion: Optional[BoundaryOpinion] = None
    selection_decisions: List[SubagentSelectionDecision] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def reconcile_totals(self) -> int:
        """Recursively reconciles tokens_used = self_used + sum(child.tokens_used)."""
        for c in self.children:
            c.reconcile_totals()
        child_sum = sum(c.tokens_used for c in self.children)
        self.tokens_used = (self.self_used or 0) + child_sum
        return self.tokens_used


@dataclass
class CapitalPartition:
    total_budget: int
    protected_capital: int  # 40% reserved strictly for terminal verification
    exploratory_capital: int  # 60% dynamically leased with decay
    spent_protected: int = 0
    spent_exploratory: int = 0

    @classmethod
    def create(cls, total_tokens: int = 50000) -> 'CapitalPartition':
        protected = int(total_tokens * 0.40)
        exploratory = total_tokens - protected
        return cls(
            total_budget=total_tokens,
            protected_capital=protected,
            exploratory_capital=exploratory
        )


def get_max_recursion_depth() -> int:
    """Reads maximum baseline recursion depth from environment or defaults to 3."""
    env_val = os.getenv("G2B_MAX_RECURSION_DEPTH", "3")
    try:
        return int(env_val)
    except ValueError:
        return 3
