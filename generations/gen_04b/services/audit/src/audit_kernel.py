"""Sovereign Audit Kernel & Orchestration Engine (`soc_g4b_audit`).

Enforces:
- Invariant [L1-G4B-001]: Service-Oriented Sovereign Mesh Protocol Standardization.
- Invariant [L1-G3B-012]: Dedicated Non-Loopback Network Topology on 192.168.40.30:8444.
- Invariant [L1-G3B-016]: Zero-Trust Micro-Auditor Interception & Formal Verification Sinks.
- Invariant [NEG-PRIMITIVE-001]: Sheaf-Quorum 2-of-3 Non-Blocking Decentralized Consensus.
- Integrates all 10 core subsystems:
  1. ZeroTrustMicroAuditor (SentrySyntax)
  2. SMTModelChecker (OracleSMT)
  3. ByzantineChaosFuzzer (AdversaryChaos)
  4. SheafQuorumConsensusEngine (Peer consensus)
  5. AuditMerkleWitnessEngine (Merkle-DAG root ledger)
  6. AuditStatechartEngine (30-state deterministic state machine)
  7. AuditFunctorialUndoManager (Adjoint rollback engine)
  8. AuditRFCMediator (Inter-service RFC protocol negotiation)
  9. AuditServiceTopology (Dedicated network topology)
  10. LandauerThermodynamicLedger (60/40 capital accounting & Landauer dissipation)
"""

from __future__ import annotations

import hashlib
import time
from typing import Any, Dict, List, Optional, Tuple
import uuid

from generations.gen_04b.protocols.rfc_protocol import (
    SpecAdjustmentRequest,
    SpecAmendment,
)
from .domain_models import (
    AuditAttestation,
    AuditDomainInvariantViolation,
    AuditSeverity,
    AuditVerificationStage,
    ByzantineFuzzReport,
    CodeLeafCandidate,
    FunctorialUndoCheckpoint,
    HermeticAuditReport,
    LandauerThermodynamicLedger,
    MorphismCheckStatus,
    QuorumConsensusWitness,
    QuorumVerdict,
    SMTModelCheckResult,
    assert_non_loopback,
)
from .zero_trust_micro_auditor import ZeroTrustMicroAuditor
from .smt_model_checker import SMTModelChecker
from .byzantine_chaos_fuzzer import ByzantineChaosFuzzer
from .sheaf_quorum_consensus import SheafQuorumConsensusEngine
from .merkle_witness_engine import AuditMerkleWitnessEngine
from .statechart_engine import AuditStatechartEngine
from .functorial_undo import AuditFunctorialUndoManager
from .rfc_protocol_mediator import AuditRFCMediator
from .service_topology import AuditServiceTopology, PartitionPolicy


class SovereignAuditKernel:
    """Master sovereign audit pipeline orchestrator."""

    DEFAULT_NODE_IP: str = "192.168.40.30"
    DEFAULT_PORT: int = 8444

    def __init__(
        self,
        node_ip: str = DEFAULT_NODE_IP,
        port: int = DEFAULT_PORT,
        token_budget: int = 923100,  # Option C Zenith Apex Budget
    ) -> None:
        self.endpoint = f"{node_ip}:{port}"
        assert_non_loopback(self.endpoint, "SovereignAuditKernel initialization")

        self.node_ip = node_ip
        self.port = port

        # Initialize subsystems
        self.topology = AuditServiceTopology(node_ip=node_ip, port=port)
        self.thermo_ledger = LandauerThermodynamicLedger(token_lease_budget=token_budget)
        self.micro_auditor = ZeroTrustMicroAuditor(auditor_node_id="node_hermetic_sentry")
        self.smt_checker = SMTModelChecker(checker_node_id="node_smt_oracle")
        self.chaos_fuzzer = ByzantineChaosFuzzer(fuzzer_node_id="node_chaos_adversary")
        self.quorum_engine = SheafQuorumConsensusEngine(anchor_node_id="node_merkle_sheaf")
        self.merkle_engine = AuditMerkleWitnessEngine(node_id="node_merkle_sheaf")
        self.statechart = AuditStatechartEngine()
        self.undo_manager = AuditFunctorialUndoManager()
        self.rfc_mediator = AuditRFCMediator(node_id="node_audit_rfc_mediator", endpoint=self.endpoint)

        self.audited_attestations: List[AuditAttestation] = []

    def audit_code_leaf(
        self,
        candidate: CodeLeafCandidate,
        epoch: int = 1,
    ) -> AuditAttestation:
        """Executes full sovereign adversarial audit pipeline on a code leaf candidate."""
        candidate.validate_invariants()

        # Step 1: Ingress Staging
        self.statechart.send("EV_RECEIVE_CANDIDATE", {"leaf_id": candidate.leaf_id})
        self.statechart.send("EV_VALIDATE_ENDPOINT", {"source": candidate.source_endpoint})
        self.statechart.send("EV_STAGE_READY")

        # Record ingress thermodynamic spend & causal checkpoint
        self.thermo_ledger.spend_tokens(5000, is_protected=False)
        self.thermo_ledger.record_bit_erasure(128)
        ckpt_pre_audit = self.undo_manager.create_checkpoint(
            stage=AuditVerificationStage.INGRESS_STAGING,
            state_hash=candidate.compute_hash(),
            landauer_bits_checkpoint=self.thermo_ledger.total_bits_erased,
            context={"leaf_id": candidate.leaf_id, "stage": "INGRESS"},
        )

        # Step 2: Hermetic Boundary Micro-Audit (SentrySyntax)
        self.statechart.send("EV_START_AUDIT")
        hermetic_report = self.micro_auditor.audit_candidate(candidate)
        self.merkle_engine.record_event("HERMETIC_MICRO_AUDIT", hermetic_report.to_dict())
        self.thermo_ledger.spend_tokens(10000, is_protected=False)
        self.thermo_ledger.record_bit_erasure(256)

        if not hermetic_report.is_hermetic:
            self.statechart.send("EV_HERMETIC_FAIL", {"violations_count": len(hermetic_report.violations)})
            witness = self.quorum_engine.adjudicate_triad(
                hermetic_report,
                SMTModelCheckResult(
                    check_id="chk_bypassed",
                    leaf_id=candidate.leaf_id,
                    morphism_status=MorphismCheckStatus.UNKNOWN_SOLVER_ERROR,
                    precondition_entailment_valid=False,
                    postcondition_consequence_valid=False,
                    is_deadlock_free=False,
                ),
                ByzantineFuzzReport(
                    report_id="rpt_bypassed",
                    leaf_id=candidate.leaf_id,
                    vectors_dispatched=0,
                    vectors_trapped=0,
                    trap_rate=0.0,
                    unhandled_faults=1,
                ),
            )
            attestation = self.merkle_engine.mint_attestation(witness, candidate, epoch=epoch)
            self.audited_attestations.append(attestation)
            return attestation

        self.statechart.send("EV_HERMETIC_PASS")

        # Step 3: SMT Model Checking (OracleSMT)
        ckpt_pre_smt = self.undo_manager.create_checkpoint(
            stage=AuditVerificationStage.SMT_MODEL_CHECKING,
            state_hash=hermetic_report.compute_hash(),
            landauer_bits_checkpoint=self.thermo_ledger.total_bits_erased,
            context={"leaf_id": candidate.leaf_id, "stage": "PRE_SMT"},
        )
        statechart_graph = self.statechart.get_full_graph_definition()
        smt_result = self.smt_checker.check_candidate(candidate, statechart_graph=statechart_graph)
        self.merkle_engine.record_event("SMT_MODEL_CHECK", smt_result.to_dict())
        self.thermo_ledger.spend_tokens(20000, is_protected=False)
        self.thermo_ledger.record_bit_erasure(512)

        if smt_result.morphism_status != MorphismCheckStatus.PROVEN_VALID:
            self.statechart.send("EV_SMT_FAIL", {"status": smt_result.morphism_status.value})
            witness = self.quorum_engine.adjudicate_triad(
                hermetic_report,
                smt_result,
                ByzantineFuzzReport(
                    report_id="rpt_bypassed",
                    leaf_id=candidate.leaf_id,
                    vectors_dispatched=0,
                    vectors_trapped=0,
                    trap_rate=0.0,
                    unhandled_faults=1,
                ),
            )
            attestation = self.merkle_engine.mint_attestation(witness, candidate, epoch=epoch)
            self.audited_attestations.append(attestation)
            return attestation

        self.statechart.send("EV_SMT_PASS")

        # Step 4: Byzantine Chaos Fuzzing (AdversaryChaos)
        fuzz_report = self.chaos_fuzzer.fuzz_candidate(candidate, vectors_per_type=1)
        self.merkle_engine.record_event("BYZANTINE_CHAOS_FUZZ", fuzz_report.to_dict())
        self.thermo_ledger.spend_tokens(15000, is_protected=False)
        self.thermo_ledger.record_bit_erasure(384)

        if fuzz_report.trap_rate < 1.0 or fuzz_report.unhandled_faults > 0:
            self.statechart.send("EV_CHAOS_FAIL", {"trap_rate": fuzz_report.trap_rate})
        else:
            self.statechart.send("EV_CHAOS_PASS")

        # Step 5: Sheaf-Quorum Consensus Adjudication
        self.statechart.send("EV_EVALUATE_QUORUM")
        self.statechart.send("EV_VOTES_COLLECTED")
        witness = self.quorum_engine.adjudicate_triad(hermetic_report, smt_result, fuzz_report)

        if witness.verdict in (QuorumVerdict.UNANIMOUS_PASS, QuorumVerdict.QUORUM_PASS):
            self.statechart.send("EV_QUORUM_APPROVED", {"verdict": witness.verdict.value})
        else:
            self.statechart.send("EV_QUORUM_REJECTED", {"verdict": witness.verdict.value})

        # Step 6: Attestation Emission & Merkle Anchoring (Protected Sinks)
        self.thermo_ledger.spend_tokens(25000, is_protected=True)
        self.thermo_ledger.record_bit_erasure(1024)

        ckpt_pre_attest = self.undo_manager.create_checkpoint(
            stage=AuditVerificationStage.MERKLE_ATTESTATION,
            state_hash=witness.compute_hash(),
            landauer_bits_checkpoint=self.thermo_ledger.total_bits_erased,
            context={"leaf_id": candidate.leaf_id, "witness_id": witness.witness_id},
        )

        if witness.verdict in (QuorumVerdict.UNANIMOUS_PASS, QuorumVerdict.QUORUM_PASS):
            self.statechart.send("EV_INITIATE_ATTESTATION")
            self.statechart.send("EV_MERKLE_ANCHORED")
            self.statechart.send("EV_SIGNATURES_COLLECTED")
            self.statechart.send("EV_DISPATCH_COMPLETE")
            self.statechart.send("EV_SEAL_FINAL")

        attestation = self.merkle_engine.mint_attestation(witness, candidate, epoch=epoch)
        self.audited_attestations.append(attestation)

        # Transmit telemetry & attestation across non-loopback channels
        self.topology.transmit("channel_telemetry_stream", 1024)
        self.topology.transmit("channel_merkle_attestation", 2048)

        return attestation

    def adjudicate_rfc(
        self,
        request: SpecAdjustmentRequest,
        candidate_code: Optional[str] = None,
    ) -> SpecAmendment:
        """Adjudicates inter-service RFC request from Builder."""
        self.thermo_ledger.spend_tokens(5000, is_protected=False)
        self.topology.transmit("channel_research_rfc", 512)
        return self.rfc_mediator.adjudicate_rfc_request(request, candidate_code=candidate_code)

    def rollback_to_checkpoint(self, checkpoint_id: str) -> FunctorialUndoCheckpoint:
        """Rolls back verification pipeline to an adjoint causal checkpoint and recovers bits."""
        cp = self.undo_manager.rollback_to_checkpoint(checkpoint_id, self.thermo_ledger)
        self.statechart.send("EV_THERMO_RECOVER")
        return cp

    def get_audit_status(self) -> Dict[str, Any]:
        """Returns comprehensive diagnostic summary of the Sovereign Audit Kernel."""
        return {
            "endpoint": self.endpoint,
            "current_statechart_state": self.statechart.current_state,
            "parallel_sentry_state": self.statechart.parallel_sentry_state,
            "parallel_thermo_state": self.statechart.parallel_thermo_state,
            "merkle_root": self.merkle_engine.compute_merkle_root(),
            "attestations_sealed": len(self.audited_attestations),
            "thermodynamics": self.thermo_ledger.to_dict(),
            "topology_partitioned": self.topology.is_partitioned,
        }
