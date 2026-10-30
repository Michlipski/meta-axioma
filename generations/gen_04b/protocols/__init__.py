"""Generation 4b Shared Inter-Service Protocols (`generations/gen_04b/protocols`).

Enforces:
- [L1-G4B-001] Service-Oriented Sovereign Mesh Protocol Standardization.
- [L1-G4B-002] Zero-Code Research Tool Boundary.
- [L1-G4B-003] Hierarchical Merkle-DAG Witness Telemetry.
"""

from .deliverable_bundle import (
    ConstraintAnalysis,
    DeliverableProtocolViolation,
    FailureModeModel,
    HypothesisDefinition,
    ResearchDeliverableBundle,
    TabooDistanceMatrix,
    TradeoffMatrix,
)
from .rfc_protocol import (
    BottleneckType,
    CounterProof,
    RFCProtocolViolation,
    RFCStatus,
    SolverResult,
    SpecAdjustmentRequest,
    SpecAmendment,
)
from .urn_registry import (
    GLOBAL_URN_REGISTRY,
    SymbolURN,
    URNFormatError,
    URNRegistry,
)

__all__ = [
    "ConstraintAnalysis",
    "DeliverableProtocolViolation",
    "FailureModeModel",
    "HypothesisDefinition",
    "ResearchDeliverableBundle",
    "TabooDistanceMatrix",
    "TradeoffMatrix",
    "BottleneckType",
    "CounterProof",
    "RFCProtocolViolation",
    "RFCStatus",
    "SolverResult",
    "SpecAdjustmentRequest",
    "SpecAmendment",
    "GLOBAL_URN_REGISTRY",
    "SymbolURN",
    "URNFormatError",
    "URNRegistry",
]
