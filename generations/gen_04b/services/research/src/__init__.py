"""Generation 4b Autonomous Epistemic Research Engine (`soc_g4b_researcher`)."""

from .domain_models import (
    BottleneckType,
    ByzantineFuzzVector,
    ConstraintAnalysis,
    DialecticalNegationSeed,
    DomainInvariantViolation,
    EmpiricalTelemetryReport,
    EpistemicCrucibleTarget,
    ExtremeBoundaryArchetype,
    FailureModeModel,
    FormalProofArtifact,
    FunctorialUndoCheckpoint,
    HypothesisDefinition,
    MerkleDagWitness,
    NoveltyArchiveEntry,
    ResearchDeliverableBundle,
    SolverResult,
    SpecAdjustmentRequest,
    SpecAmendment,
    StressDimension,
    TabooDistanceMatrix,
    TradeoffMatrix,
    ZeroContextIslandManifest,
)
from .research_kernel import SovereignResearchKernel, ZeroCodeBoundaryViolation
from .island_manager import ZeroContextIslandManager, ExplorationIsland
from .dynamic_persona import DynamicPersonaEngine, DynamicPersonaSpec
from .graph_taboo_engine import GraphTabooEngine, TabooDistanceViolation, ModeCollapseEnclaveTriggered
from .inversion_engine import DialecticalInversionEngine, NegatedPrimitiveViolation
from .boundary_stress_engine import BoundaryStressEngine, BoundaryStressFailure
from .pareto_frontier import ParetoFrontierOptimizer
from .z3_prover_bridge import Z3ProverBridge
from .rfc_protocol_bus import RFCProtocolBus, RFCValidationError
from .merkle_witness_engine import MerkleWitnessEngine, MerkleIntegrityTamperFault
from .statechart_engine import G4bStatechartEngine, StatechartTransitionError, FunctorialUndoError
from .auxiliary_hooks import AuditVerificationHook, TelemetryEvaluationHook, GovernanceSafetyHook

__all__ = [
    # Domain Models
    "BottleneckType",
    "ByzantineFuzzVector",
    "ConstraintAnalysis",
    "DialecticalNegationSeed",
    "DomainInvariantViolation",
    "EmpiricalTelemetryReport",
    "EpistemicCrucibleTarget",
    "ExtremeBoundaryArchetype",
    "FailureModeModel",
    "FormalProofArtifact",
    "FunctorialUndoCheckpoint",
    "HypothesisDefinition",
    "MerkleDagWitness",
    "NoveltyArchiveEntry",
    "ResearchDeliverableBundle",
    "SolverResult",
    "SpecAdjustmentRequest",
    "SpecAmendment",
    "StressDimension",
    "TabooDistanceMatrix",
    "TradeoffMatrix",
    "ZeroContextIslandManifest",
    # Engines
    "SovereignResearchKernel",
    "ZeroCodeBoundaryViolation",
    "ZeroContextIslandManager",
    "ExplorationIsland",
    "DynamicPersonaEngine",
    "DynamicPersonaSpec",
    "GraphTabooEngine",
    "TabooDistanceViolation",
    "ModeCollapseEnclaveTriggered",
    "DialecticalInversionEngine",
    "NegatedPrimitiveViolation",
    "BoundaryStressEngine",
    "BoundaryStressFailure",
    "ParetoFrontierOptimizer",
    "Z3ProverBridge",
    "RFCProtocolBus",
    "RFCValidationError",
    "MerkleWitnessEngine",
    "MerkleIntegrityTamperFault",
    "G4bStatechartEngine",
    "StatechartTransitionError",
    "FunctorialUndoError",
    "AuditVerificationHook",
    "TelemetryEvaluationHook",
    "GovernanceSafetyHook",
]
