"""Generation 4b Shared Inter-Service Protocols (`generations/gen_04b/protocols`).

Enforces:
- [L1-G4B-001] Service-Oriented Sovereign Mesh Protocol Standardization.
- [L1-G4B-002] Zero-Code Research Tool Boundary.
- [L1-G4B-003] Hierarchical Merkle-DAG Witness Telemetry.
- [NEG-SANDBOX-001] Sandbox-Hermetic Execution & Dual-Profile IPC Transport.
"""

from .acceptance_spec import (
    AcceptanceProtocolViolation,
    AcceptanceSpecIR,
    DomainArchetype,
    FalsificationVector,
    MutationType,
)
from .cognitive_routing import (
    BRAIN_ROLES,
    DISCOVERY_ROLES,
    MUSCLE_ROLES,
    RED_TEAM_ROLES,
    VALID_AGY_MODEL_PARAMS,
    Gemini4ModelTier,
    RoutingDecision,
    RoutingProtocolViolation,
    is_brain_model_label,
    resolve_role_routing,
)
from .deliverable_bundle import (
    ConstraintAnalysis,
    DeliverableProtocolViolation,
    FailureModeModel,
    HypothesisDefinition,
    ResearchDeliverableBundle,
    TabooDistanceMatrix,
    TradeoffMatrix,
)
from .ipc_transport import (
    EnclaveRPCServer,
    IPCEnvelope,
    IPCMessageType,
    MeshIPCTransport,
    TransportMode,
    TransportTransmissionError,
)
from .rfc_adapter import RFCAdapter
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
    "AcceptanceProtocolViolation",
    "AcceptanceSpecIR",
    "DomainArchetype",
    "FalsificationVector",
    "MutationType",
    "BRAIN_ROLES",
    "DISCOVERY_ROLES",
    "MUSCLE_ROLES",
    "RED_TEAM_ROLES",
    "VALID_AGY_MODEL_PARAMS",
    "Gemini4ModelTier",
    "RoutingDecision",
    "RoutingProtocolViolation",
    "is_brain_model_label",
    "resolve_role_routing",
    "ConstraintAnalysis",
    "DeliverableProtocolViolation",
    "FailureModeModel",
    "HypothesisDefinition",
    "ResearchDeliverableBundle",
    "TabooDistanceMatrix",
    "TradeoffMatrix",
    "EnclaveRPCServer",
    "IPCEnvelope",
    "IPCMessageType",
    "MeshIPCTransport",
    "TransportMode",
    "TransportTransmissionError",
    "RFCAdapter",
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
