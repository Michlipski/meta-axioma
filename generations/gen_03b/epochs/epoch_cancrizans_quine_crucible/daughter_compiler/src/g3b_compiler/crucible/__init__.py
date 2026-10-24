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
from .subagents import (
    ResearcherSubagent,
    DialecticalArchitectSubagent,
    LeafSynthesizerSubagent,
)
from .orchestrator import (
    CrucibleOrchestrator,
    CrucibleSynthesisResult,
    LeafRemediationCircuitBreakerError,
    ZeroBypassInterceptionViolation,
)

__all__ = [
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
    # Orchestrator
    "CrucibleOrchestrator",
    "CrucibleSynthesisResult",
    "LeafRemediationCircuitBreakerError",
    "ZeroBypassInterceptionViolation",
]
