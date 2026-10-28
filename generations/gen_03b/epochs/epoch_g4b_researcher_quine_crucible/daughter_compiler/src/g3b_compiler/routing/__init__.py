"""Generation 3b Dual-Model Cognitive Routing Module."""

from .router import (
    CognitiveRole,
    ModelTier,
    CognitiveRoutingViolation,
    SubagentExecutionViolation,
    SubagentExecutionWitness,
    RoutedTaskInvocation,
    DualModelRouter,
)
from .personas import (
    PersonaSpec,
    PersonaRegistry,
)

__all__ = [
    "CognitiveRole",
    "ModelTier",
    "CognitiveRoutingViolation",
    "SubagentExecutionViolation",
    "SubagentExecutionWitness",
    "RoutedTaskInvocation",
    "DualModelRouter",
    "PersonaSpec",
    "PersonaRegistry",
]
