"""Generation 3b Zero-Trust Evaluators Module (The Brain - Gemini 4 Argon).

Exports:
- FormalModelChecker & ModelCheckingReport (Statechart Reachability, Dead-Ends, Conflicts)
- HeadlessJourneyWalker & JourneyAuditReport (Empirical State Observation, Functorial Undo)
- ZeroTrustMicroAuditorRegistry & MicroAuditResult (Leaf-Level Hostile Auditing)
- Custom Exceptions: ModelCheckingFailure, PhantomJourneyStepViolation, JourneyAuditFailure
"""

from .checker import (
    FormalModelChecker,
    ModelCheckingReport,
    ModelCheckingFailure,
)
from .journey_walker import (
    HeadlessJourneyWalker,
    JourneyStep,
    JourneyAuditReport,
    PhantomJourneyStepViolation,
    JourneyAuditFailure,
)
from .micro_auditors import (
    LeafArtifact,
    MicroAuditResult,
    SecurityMicroAuditor,
    ContractMicroAuditor,
    CognitiveRoutingAuditor,
    TopologicalMicroAuditor,
    ThermodynamicMicroAuditor,
    ZeroTrustMicroAuditorRegistry,
)

__all__ = [
    # Model Checker
    "FormalModelChecker",
    "ModelCheckingReport",
    "ModelCheckingFailure",
    # Journey Walker
    "HeadlessJourneyWalker",
    "JourneyStep",
    "JourneyAuditReport",
    "PhantomJourneyStepViolation",
    "JourneyAuditFailure",
    # Micro Auditors
    "LeafArtifact",
    "MicroAuditResult",
    "SecurityMicroAuditor",
    "ContractMicroAuditor",
    "CognitiveRoutingAuditor",
    "TopologicalMicroAuditor",
    "ThermodynamicMicroAuditor",
    "ZeroTrustMicroAuditorRegistry",
]
