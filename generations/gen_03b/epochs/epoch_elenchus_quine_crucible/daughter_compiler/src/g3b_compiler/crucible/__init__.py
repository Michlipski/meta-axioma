"""Generation 3b Semantic Crucible Module.

Exports:
- FractalTaskStack, TaskNode, TaskType, DecompositionPlan, SubtaskSpec
- StackRecursionDepthViolation, StackBranchingCeilingViolation, TaskBudgetAllocationViolation
- ResearcherSubagent, DialecticalArchitectSubagent, LeafSynthesizerSubagent
- CrucibleOrchestrator, CrucibleSynthesisResult
- LeafRemediationCircuitBreakerError, ZeroBypassInterceptionViolation
"""

from .stack import (
    TaskType,
    TaskNode,
    SubtaskSpec,
    DecompositionPlan,
    FractalTaskStack,
    StackRecursionDepthViolation,
    StackBranchingCeilingViolation,
    TaskBudgetAllocationViolation,
)
from .models import (
    QuorumVerdict,
    QuorumConsensusResult,
    QuorumConsensusDeadlockError,
)
from .subagents import (
    ResearcherSubagent,
    DialecticalArchitectSubagent,
    LeafSynthesizerSubagent,
    ProductManagerAuditor,
    ArchitectAuditor,
    QAVerificationAuditor,
)
from .orchestrator import (
    CrucibleOrchestrator,
    CrucibleSynthesisResult,
    LeafRemediationCircuitBreakerError,
    ZeroBypassInterceptionViolation,
)

__all__ = [
    # Models & Quorum
    "QuorumVerdict",
    "QuorumConsensusResult",
    "QuorumConsensusDeadlockError",
    # Stack
    "TaskType",
    "TaskNode",
    "SubtaskSpec",
    "DecompositionPlan",
    "FractalTaskStack",
    "StackRecursionDepthViolation",
    "StackBranchingCeilingViolation",
    "TaskBudgetAllocationViolation",
    # Subagents
    "ResearcherSubagent",
    "DialecticalArchitectSubagent",
    "LeafSynthesizerSubagent",
    "ProductManagerAuditor",
    "ArchitectAuditor",
    "QAVerificationAuditor",
    # Orchestrator
    "CrucibleOrchestrator",
    "CrucibleSynthesisResult",
    "LeafRemediationCircuitBreakerError",
    "ZeroBypassInterceptionViolation",
]

