"""Project Proposal Models & Bounded Token Budgeting for System G2b."""

from dataclasses import dataclass, field
import datetime
from typing import Any, Dict, List, Optional

from g2b_compiler.recursion.models import WorkerType

MIN_BUDGET_FLOOR: int = 10_000
MAX_SAFETY_BUDGET: int = 1_000_000
PROTECTED_CAPITAL_RATIO: float = 0.40


@dataclass
class ProposalScopeTier:
    tier_id: str
    title: str
    target_persona_fit: str
    included_features: List[str]
    deferred_features: List[str]
    statechart_complexity: str
    verification_depth: str
    raw_estimated_tokens: int
    bounded_token_budget: int
    protected_capital: int
    exploratory_capital: int
    fractional_allocation: Dict[str, float]
    rationale: str
    workload_breakdown: Dict[str, int] = field(default_factory=dict)
    token_justification: str = ""

    def __post_init__(self):
        # Validate axiomatic bounding invariants
        if not (MIN_BUDGET_FLOOR <= self.bounded_token_budget <= MAX_SAFETY_BUDGET):
            raise ValueError(
                f"Bounded token budget {self.bounded_token_budget} violates safety bounds [{MIN_BUDGET_FLOOR}, {MAX_SAFETY_BUDGET}]"
            )
        expected_protected = int(self.bounded_token_budget * PROTECTED_CAPITAL_RATIO)
        if self.protected_capital != expected_protected:
            self.protected_capital = expected_protected
        self.exploratory_capital = self.bounded_token_budget - self.protected_capital

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tier_id": self.tier_id,
            "title": self.title,
            "target_persona_fit": self.target_persona_fit,
            "included_features": self.included_features,
            "deferred_features": self.deferred_features,
            "statechart_complexity": self.statechart_complexity,
            "verification_depth": self.verification_depth,
            "raw_estimated_tokens": self.raw_estimated_tokens,
            "bounded_token_budget": self.bounded_token_budget,
            "protected_capital": self.protected_capital,
            "exploratory_capital": self.exploratory_capital,
            "fractional_allocation": self.fractional_allocation,
            "rationale": self.rationale,
            "workload_breakdown": self.workload_breakdown,
            "token_justification": self.token_justification,
        }


@dataclass
class ProjectProposalDossier:
    app_id: str
    elevator_pitch: str
    research_summary: str
    min_budget_bound: int = MIN_BUDGET_FLOOR
    max_safety_budget_bound: int = MAX_SAFETY_BUDGET
    proposals: List[ProposalScopeTier] = field(default_factory=list)
    selected_proposal_id: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())

    @property
    def selected_proposal(self) -> Optional[ProposalScopeTier]:
        if not self.proposals:
            return None
        if self.selected_proposal_id:
            for p in self.proposals:
                if p.tier_id == self.selected_proposal_id:
                    return p
        # Default to middle / balanced proposal or first proposal
        for p in self.proposals:
            if "balanced" in p.tier_id.lower() or "standard" in p.tier_id.lower():
                return p
        return self.proposals[0]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "app_id": self.app_id,
            "elevator_pitch": self.elevator_pitch,
            "research_summary": self.research_summary,
            "min_budget_bound": self.min_budget_bound,
            "max_safety_budget_bound": self.max_safety_budget_bound,
            "proposals": [p.to_dict() for p in self.proposals],
            "selected_proposal_id": self.selected_proposal_id,
            "created_at": self.created_at,
        }
