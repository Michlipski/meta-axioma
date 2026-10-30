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
)
from .zero_trust_micro_auditor import ZeroTrustMicroAuditor
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
from .audit_kernel import SovereignAuditKernel

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
    # Verification Engines & Subsystems
    "ZeroTrustMicroAuditor",
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
]
