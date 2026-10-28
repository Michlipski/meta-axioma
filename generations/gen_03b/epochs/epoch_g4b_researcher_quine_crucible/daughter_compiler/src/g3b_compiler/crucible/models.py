"""Generation 3b Adversarial Quorum Consensus Models.

Defines the strict Pydantic schemas for the Adversarial Quorum Consensus Gate
running under Gemini 4 Argon governance to physically trap generative feature-creep
and architectural hallucinations before IR synthesis begins.
"""

from typing import List, Dict, Any
from pydantic import BaseModel, Field, model_validator


class QuorumVerdict(BaseModel):
    """A formal audit verdict from a single Quorum subagent role."""
    role_id: str = Field(
        ...,
        description="The authoritative auditor role ID (e.g., 'PRODUCT_MANAGER', 'SYSTEMS_ARCHITECT', 'QA_ENGINEER')",
    )
    approved: bool = Field(
        ...,
        description="Whether the proposal passes this auditor's invariant gate.",
    )
    blocking_violations: List[str] = Field(
        default_factory=list,
        description="Actionable architectural or invariant breaches. Must be empty if approved is True.",
    )

    @model_validator(mode="after")
    def validate_violations_consistency(self) -> "QuorumVerdict":
        if self.approved and self.blocking_violations:
            raise ValueError(
                f"QuorumVerdict for role '{self.role_id}' has approved=True but non-empty blocking_violations: "
                f"{self.blocking_violations}. Violations must be empty if approved."
            )
        if not self.approved and not self.blocking_violations:
            raise ValueError(
                f"QuorumVerdict for role '{self.role_id}' has approved=False but blocking_violations is empty. "
                "Must state specific, actionable architectural or invariant breaches."
            )
        return self


class QuorumConsensusResult(BaseModel):
    """The aggregate consensus result across all Quorum subagent roles."""
    is_unanimous: bool
    verdicts: Dict[str, QuorumVerdict]
    all_blocking_violations: List[str] = Field(default_factory=list)
    iteration_count: int = 1
    total_audit_tokens: int = 0


class QuorumConsensusDeadlockError(Exception):
    """Raised when Quorum consensus fails to converge within max_iterations."""
    pass

