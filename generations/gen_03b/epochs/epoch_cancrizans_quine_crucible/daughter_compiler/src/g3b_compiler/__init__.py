"""Generation 3b: The Autonomous Universal Systems Compiler."""

from .thermodynamics import (
    BOLTZMANN_K,
    AMBIENT_T_KELVIN,
    PhysicalTokenMeter,
    BudgetEstimate,
    DynamicBudgetCalibrator,
    ThermodynamicLedger,
    ThermodynamicExhaustionError,
    ProtectedCapitalViolation,
)
from .emitter import (
    PhantomEmissionViolation,
    PostEmissionExecutionFailure,
    DynamicCodeEmitter,
)
from .routing import (
    CognitiveRole,
    ModelTier,
    CognitiveRoutingViolation,
    SubagentExecutionViolation,
    SubagentExecutionWitness,
    DualModelRouter,
)
from .telemetry import (
    GENESIS_HASH,
    ChainedTelemetryEvent,
    CryptographicTelemetryEngine,
)
from .compiler import SystemG3bCompiler

__all__ = [
    "BOLTZMANN_K",
    "AMBIENT_T_KELVIN",
    "PhysicalTokenMeter",
    "BudgetEstimate",
    "DynamicBudgetCalibrator",
    "ThermodynamicLedger",
    "ThermodynamicExhaustionError",
    "ProtectedCapitalViolation",
    "PhantomEmissionViolation",
    "PostEmissionExecutionFailure",
    "DynamicCodeEmitter",
    "CognitiveRole",
    "ModelTier",
    "CognitiveRoutingViolation",
    "SubagentExecutionViolation",
    "SubagentExecutionWitness",
    "DualModelRouter",
    "GENESIS_HASH",
    "ChainedTelemetryEvent",
    "CryptographicTelemetryEngine",
    "SystemG3bCompiler",
]
