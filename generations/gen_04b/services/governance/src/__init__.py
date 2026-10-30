"""Generation 4b Sovereign Governance & Safety Service (`soc_g4b_governance`).

Exports all domain models, enums, exceptions, subsystems, and the central governance kernel.
"""

from __future__ import annotations

from .domain_models import (
    ASTInterceptRecord,
    AxiomSeverity,
    AxiomViolation,
    BottleneckType,
    CircuitBreakerState,
    CircuitBreakerStateRecord,
    CircuitBreakerTrippedError,
    CounterProof,
    GenerationalHandoverCertificate,
    GovernanceDomainInvariantViolation,
    GovernanceEvent,
    GovernanceKernelState,
    GovernanceStatechartDefinition,
    GovernanceStatechartEngine,
    GovernanceStatechartState,
    HITLDisposition,
    HITLDispositionStatus,
    HITLInterceptRequest,
    HeuristicDebtCeilingBreached,
    HeuristicDebtRecord,
    NegativeAxiom,
    NegativeAxiomVetoViolation,
    PeerQuarantineStatus,
    QuarantineEvent,
    RFCDispositionStatus,
    SpecAdjustmentRequest,
    SpecAmendment,
    StatechartTransitionRecord,
    SuccessionGraduationStatus,
    SuccessionInvariantProof,
    VetoActionType,
    assert_non_loopback,
)

from .negative_axiom_enforcer import NegativeAxiomEnforcer
from .hitl_intercept_engine import HITLInterceptEngine
from .circuit_breaker_enclave import CircuitBreakerEnclave
from .rfc_protocol_adjudicator import RFCProtocolAdjudicator
from .succession_gatekeeper import SuccessionGatekeeper
from .service_topology import (
    GovernanceChannel,
    GovernanceServiceTopology,
    NetworkPartitionError,
    PartitionPolicy,
)
from .functorial_undo import FunctorialUndoEngine, FunctorialUndoViolation
from .statechart_engine import StatechartEngine
from .governance_kernel import GovernanceKernel

__all__ = [
    # Exceptions
    "GovernanceDomainInvariantViolation",
    "NegativeAxiomVetoViolation",
    "HeuristicDebtCeilingBreached",
    "CircuitBreakerTrippedError",
    "NetworkPartitionError",
    "FunctorialUndoViolation",
    # Helper
    "assert_non_loopback",
    # Enums
    "AxiomSeverity",
    "VetoActionType",
    "HITLDispositionStatus",
    "BottleneckType",
    "RFCDispositionStatus",
    "CircuitBreakerState",
    "PeerQuarantineStatus",
    "SuccessionGraduationStatus",
    "GovernanceStatechartState",
    "PartitionPolicy",
    # Domain Models
    "NegativeAxiom",
    "AxiomViolation",
    "ASTInterceptRecord",
    "HITLInterceptRequest",
    "HITLDisposition",
    "HeuristicDebtRecord",
    "SpecAdjustmentRequest",
    "CounterProof",
    "SpecAmendment",
    "QuarantineEvent",
    "CircuitBreakerStateRecord",
    "SuccessionInvariantProof",
    "GenerationalHandoverCertificate",
    "GovernanceKernelState",
    "GovernanceEvent",
    "StatechartTransitionRecord",
    "GovernanceStatechartDefinition",
    "GovernanceStatechartEngine",
    "GovernanceChannel",
    # Subsystems & Kernel
    "NegativeAxiomEnforcer",
    "HITLInterceptEngine",
    "CircuitBreakerEnclave",
    "RFCProtocolAdjudicator",
    "SuccessionGatekeeper",
    "GovernanceServiceTopology",
    "FunctorialUndoEngine",
    "StatechartEngine",
    "GovernanceKernel",
]
