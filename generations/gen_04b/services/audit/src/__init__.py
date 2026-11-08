"""Generation 4b Sovereign Audit & Formal Verification Service (`soc_g4b_audit`).

Exports all domain models, verification engines, statechart, and sovereign kernel.
"""

from __future__ import annotations

from .domain_models import (
    AuditAttestation,
    AuditDomainInvariantViolation,
    AuditSeverity,
    AuditServiceTopologyState,
    AuditVerificationStage,
    ByzantineFuzzReport,
    ByzantineFuzzVector,
    CodeLeafCandidate,
    FunctorialUndoCheckpoint,
    FuzzVectorType,
    HermeticAuditReport,
    HermeticLinterViolation,
    LandauerThermodynamicLedger,
    MorphismCheckStatus,
    QuorumConsensusWitness,
    QuorumVerdict,
    SMTModelCheckResult,
    assert_non_loopback,
    BijectiveVerificationViolation,
    RogueSymbolViolation,
    UnimplementedVerbViolation,
    SpecificationDriftViolation,
    SignatureMismatchViolation,
    OperationalMitigationViolation,
    UnprotectedStateMutationViolation,
    ResourceLeakViolation,
    UnboundedNetworkCallViolation,
    RawExceptionLeakViolation,
    PresentationAuditViolation,
    DOMBijectivityViolation,
    ResponsiveCanvasViolation,
    StatechartDOMBisimulationViolation,
    HeadlessUIWalkerViolation,
    HeadlessUIErgonomicsViolation,
    TautologicalTestViolation,
    SemanticStateSpoofingViolation,
    MutationWitness,
)
from .bijective_verifier import BijectiveVerifier
from .operational_pitfall_auditor import OperationalPitfallAuditor, operational_contract
from .presentation_micro_auditor import (
    PresentationMicroAuditor,
    PresentationAuditReport,
    DOMQueryWitness,
    CanvasResponsivenessWitness,
    StatechartBisimulationWitness,
)
from .headless_ui_walker import (
    HeadlessUIWalker,
    HeadlessUIWalkReport,
    ErgonomicsAxiom,
    PurePythonJSSyntaxChecker,
)
from .journey_walker import (
    BoundingBox,
    DOMMutationTimeoutViolation,
    FlowParser,
    HeadlessUIJourneyWalker,
    JourneyReport,
    JourneyStep,
    JourneyStepResult,
    JourneyVerificationFailure,
    OcclusionViolation,
    ViewportClippingViolation,
    VisualOcclusionChecker,
)
from .zero_trust_micro_auditor import ZeroTrustMicroAuditor
from .mutation_fuzzer import PhysicalMutationFalsifier, check_and_restore_stale_mutations
from .smt_model_checker import SMTModelChecker, NativeSMTProver_v4b
from .byzantine_chaos_fuzzer import ByzantineChaosFuzzer
from .sheaf_quorum_consensus import SheafQuorumConsensusEngine, PeerVote
from .merkle_witness_engine import AuditMerkleWitnessEngine, MerkleNode
from .statechart_engine import AuditStatechartEngine
from .functorial_undo import AuditFunctorialUndoManager, FunctorialUndoViolation
from .rfc_protocol_mediator import AuditRFCMediator
from .service_topology import (
    AuditChannel,
    AuditServiceTopology,
    NetworkPartitionError,
    PartitionPolicy,
)
from .trace_bijective_auditor import (
    TraceBijectiveAuditor,
    TraceAuditReport,
    TraceBijectiveViolation,
    UnimplementedTraceEntityViolation,
    RogueCodeEntityViolation,
    TraceFieldMismatchViolation,
    TraceTypeMismatchViolation,
)
from .trilateral_completeness_auditor import (
    TrilateralCompletenessAuditor,
    TrilateralAuditReport,
    TriPlanarMerkleAttestation,
    TrilateralAuditViolation,
)
from .audit_kernel import SovereignAuditKernel
from .qfd_consistency_auditor import (
    QFDConsistencyAuditor,
    QFDConsistencyAuditResult,
    TemporalCausalityViolation,
    OrphanFeatureViolation,
    RoofCoverageViolation,
    RecommendationParityViolation,
)

__all__ = [
    # Domain Models & Enums
    "AuditAttestation",
    "AuditDomainInvariantViolation",
    "AuditSeverity",
    "AuditServiceTopologyState",
    "AuditVerificationStage",
    "ByzantineFuzzReport",
    "ByzantineFuzzVector",
    "CodeLeafCandidate",
    "FunctorialUndoCheckpoint",
    "FuzzVectorType",
    "HermeticAuditReport",
    "HermeticLinterViolation",
    "LandauerThermodynamicLedger",
    "MorphismCheckStatus",
    "QuorumConsensusWitness",
    "QuorumVerdict",
    "SMTModelCheckResult",
    "assert_non_loopback",
    "BijectiveVerificationViolation",
    "RogueSymbolViolation",
    "UnimplementedVerbViolation",
    "SpecificationDriftViolation",
    "SignatureMismatchViolation",
    "OperationalMitigationViolation",
    "UnprotectedStateMutationViolation",
    "ResourceLeakViolation",
    "UnboundedNetworkCallViolation",
    "RawExceptionLeakViolation",
    "PresentationAuditViolation",
    "DOMBijectivityViolation",
    "ResponsiveCanvasViolation",
    "StatechartDOMBisimulationViolation",
    "HeadlessUIWalkerViolation",
    "HeadlessUIErgonomicsViolation",
    "TautologicalTestViolation",
    "SemanticStateSpoofingViolation",
    "MutationWitness",
    # Verification Engines & Subsystems
    "BijectiveVerifier",
    "OperationalPitfallAuditor",
    "operational_contract",
    "PresentationMicroAuditor",
    "PresentationAuditReport",
    "DOMQueryWitness",
    "CanvasResponsivenessWitness",
    "StatechartBisimulationWitness",
    "HeadlessUIWalker",
    "HeadlessUIWalkReport",
    "ErgonomicsAxiom",
    "PurePythonJSSyntaxChecker",
    "BoundingBox",
    "DOMMutationTimeoutViolation",
    "FlowParser",
    "HeadlessUIJourneyWalker",
    "JourneyReport",
    "JourneyStep",
    "JourneyStepResult",
    "JourneyVerificationFailure",
    "OcclusionViolation",
    "ViewportClippingViolation",
    "VisualOcclusionChecker",
    "ZeroTrustMicroAuditor",
    "PhysicalMutationFalsifier",
    "check_and_restore_stale_mutations",
    "SMTModelChecker",
    "NativeSMTProver_v4b",
    "ByzantineChaosFuzzer",
    "SheafQuorumConsensusEngine",
    "PeerVote",
    "AuditMerkleWitnessEngine",
    "MerkleNode",
    "AuditStatechartEngine",
    "AuditFunctorialUndoManager",
    "FunctorialUndoViolation",
    "AuditRFCMediator",
    "AuditChannel",
    "AuditServiceTopology",
    "NetworkPartitionError",
    "PartitionPolicy",
    # Master Sovereign Kernel
    "SovereignAuditKernel",
    # TRACE Bijective Auditor
    "TraceBijectiveAuditor",
    "TraceAuditReport",
    "TraceBijectiveViolation",
    "TraceTypeMismatchViolation",
    # Trilateral Completeness Auditor
    "TrilateralCompletenessAuditor",
    "TrilateralAuditReport",
    "TriPlanarMerkleAttestation",
    "TrilateralAuditViolation",
    # QFD Consistency Auditor & Violations
    "QFDConsistencyAuditor",
    "QFDConsistencyAuditResult",
    "TemporalCausalityViolation",
    "OrphanFeatureViolation",
    "RoofCoverageViolation",
    "RecommendationParityViolation",
]
