"""Generation 4b Systems Compiler Package (`generations/gen_04b/compiler`).

Exports:
- SystemG4bCompiler
- CompilationRequest
- CompilationReport
- CompilationPhase
- CompilationStatechart
- PhaseExecutionSequenceViolation
- main
"""

from __future__ import annotations

from .cli import main
from .orchestrator import (
    CompilationReport,
    CompilationRequest,
    PhaseExecutionSequenceViolation,
    SystemG4bCompiler,
)
from .statechart import (
    CompilationPhase,
    CompilationStatechart,
    StatechartTransitionError,
    TransitionRecord,
)

__all__ = [
    "CompilationPhase",
    "CompilationStatechart",
    "StatechartTransitionError",
    "TransitionRecord",
    "CompilationReport",
    "CompilationRequest",
    "PhaseExecutionSequenceViolation",
    "SystemG4bCompiler",
    "main",
]
