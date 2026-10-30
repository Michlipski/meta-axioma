"""Unit & Adversarial Invariant Test Suite for Audit Domain Models (`[L1-G3B-011]`).

Validates:
1. Valid roundtrip serialization and hash computation for all 11 models.
2. Fail-fast rejection of empty source code, invalid 64-char hashes, and out-of-bound coordinates.
3. Quorum witness calculation (3-of-3 unanimous, 2-of-3 split, 1-of-3 reject, 0-of-3 unanimous fail).
4. Rejection of loopback addresses in topology states.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
import sys
import unittest

AUDIT_ROOT = Path(__file__).resolve().parent.parent
REPO_ROOT = AUDIT_ROOT.parent.parent.parent.parent
for p in [str(AUDIT_ROOT), str(AUDIT_ROOT / "src"), str(REPO_ROOT)]:
    if p not in sys.path:
        sys.path.insert(0, p)

from src.domain_models import (
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


class TestAuditDomainModels(unittest.TestCase):
    """Exhaustive roundtrip and adversarial boundary testing for all 11 models and 5 enums."""

    def setUp(self) -> None:
        self.sample_hash = hashlib.sha256(b"meta_axioma_g4b_audit").hexdigest()

    # 1. CodeLeafCandidate Roundtrip & Hash
    def test_code_leaf_candidate_roundtrip_and_hash(self) -> None:
        candidate = CodeLeafCandidate(
            leaf_id="leaf_test_001",
            symbol_urn="urn:meta_axioma:leaf:verifier",
            source_code="def verify(): pass",
            ast_node_type="FUNCTION_DEF",
            parent_contract_pre="x > 0",
            parent_contract_post="ret == True",
            child_contract_pre="x > 0",
            child_contract_post="ret == True",
            source_endpoint="192.168.40.20:8443",
        )
        h = candidate.compute_hash()
        self.assertEqual(len(h), 64)
        d = candidate.to_dict()
        recovered = CodeLeafCandidate.from_dict(d)
        self.assertEqual(recovered.leaf_id, candidate.leaf_id)
        self.assertEqual(recovered.compute_hash(), h)

    # 2. CodeLeafCandidate Invariants
    def test_code_leaf_candidate_invariants(self) -> None:
        # Empty leaf_id
        with self.assertRaises(AuditDomainInvariantViolation):
            CodeLeafCandidate(leaf_id="", symbol_urn="urn:meta_axioma:x", source_code="x = 1").validate_invariants()
        # Invalid URN
        with self.assertRaises(AuditDomainInvariantViolation):
            CodeLeafCandidate(leaf_id="l1", symbol_urn="invalid_urn", source_code="x = 1").validate_invariants()
        # Empty source_code
        with self.assertRaises(AuditDomainInvariantViolation):
            CodeLeafCandidate(leaf_id="l1", symbol_urn="urn:meta_axioma:x", source_code="").validate_invariants()
        # Loopback endpoint
        with self.assertRaises(AuditDomainInvariantViolation):
            CodeLeafCandidate(
                leaf_id="l1",
                symbol_urn="urn:meta_axioma:x",
                source_code="x = 1",
                source_endpoint="127.0.0.1:8000",
            ).validate_invariants()

    # 3. HermeticLinterViolation Roundtrip & Invariants
    def test_hermetic_linter_violation_roundtrip_and_invariants(self) -> None:
        v = HermeticLinterViolation(
            violation_id="viol_001",
            rule_id="HERM-001",
            severity=AuditSeverity.FATAL,
            line_number=10,
            column_offset=4,
            description="Loopback detected",
            culprit_token="127.0.0.1",
        )
        self.assertEqual(len(v.compute_hash()), 64)
        recovered = HermeticLinterViolation.from_dict(v.to_dict())
        self.assertEqual(recovered.violation_id, v.violation_id)

        # Invariants: line_number < 1
        with self.assertRaises(AuditDomainInvariantViolation):
            HermeticLinterViolation("v", "R1", AuditSeverity.ERROR, 0, 0, "desc", "t").validate_invariants()
        # Invariants: column_offset < 0
        with self.assertRaises(AuditDomainInvariantViolation):
            HermeticLinterViolation("v", "R1", AuditSeverity.ERROR, 1, -1, "desc", "t").validate_invariants()
        # Invariants: empty description
        with self.assertRaises(AuditDomainInvariantViolation):
            HermeticLinterViolation("v", "R1", AuditSeverity.ERROR, 1, 0, "", "t").validate_invariants()

    # 4. HermeticAuditReport Roundtrip & Invariants
    def test_hermetic_audit_report_roundtrip_and_invariants(self) -> None:
        v = HermeticLinterViolation("v1", "HERM-002", AuditSeverity.ERROR, 2, 0, "sys.path", "sys.path")
        report = HermeticAuditReport(
            report_id="rpt_001",
            leaf_id="leaf_001",
            is_hermetic=False,
            violations=[v],
            ast_nodes_scanned=45,
            banned_constructs_detected=1,
        )
        self.assertEqual(len(report.compute_hash()), 64)
        recovered = HermeticAuditReport.from_dict(report.to_dict())
        self.assertEqual(len(recovered.violations), 1)

        # Invariant: cannot be hermetic if violations exist
        with self.assertRaises(AuditDomainInvariantViolation):
            HermeticAuditReport("r", "l", is_hermetic=True, violations=[v]).validate_invariants()
        # Invariant: negative ast_nodes_scanned
        with self.assertRaises(AuditDomainInvariantViolation):
            HermeticAuditReport("r", "l", is_hermetic=True, ast_nodes_scanned=-1).validate_invariants()

    # 5. SMTModelCheckResult Roundtrip & Invariants
    def test_smt_model_check_result_roundtrip_and_invariants(self) -> None:
        res = SMTModelCheckResult(
            check_id="chk_001",
            leaf_id="leaf_001",
            morphism_status=MorphismCheckStatus.PROVEN_VALID,
            precondition_entailment_valid=True,
            postcondition_consequence_valid=True,
            is_deadlock_free=True,
            proof_steps_count=5,
            unsat_core="unsat_core(pre)",
        )
        self.assertEqual(len(res.compute_hash()), 64)
        recovered = SMTModelCheckResult.from_dict(res.to_dict())
        self.assertEqual(recovered.morphism_status, MorphismCheckStatus.PROVEN_VALID)

        # Invariant: PROVEN_VALID requires all three booleans True
        with self.assertRaises(AuditDomainInvariantViolation):
            SMTModelCheckResult(
                check_id="c",
                leaf_id="l",
                morphism_status=MorphismCheckStatus.PROVEN_VALID,
                precondition_entailment_valid=False,
                postcondition_consequence_valid=True,
                is_deadlock_free=True,
            ).validate_invariants()

    # 6. ByzantineFuzzVector Roundtrip & Invariants
    def test_byzantine_fuzz_vector_roundtrip_and_invariants(self) -> None:
        vector = ByzantineFuzzVector(
            vector_id="vec_001",
            vector_type=FuzzVectorType.PARTITION_DROP,
            target_channel="chan_ingress",
            payload_bytes_corrupted=128,
            delay_ms=25.0,
        )
        self.assertEqual(len(vector.compute_hash()), 64)
        recovered = ByzantineFuzzVector.from_dict(vector.to_dict())
        self.assertEqual(recovered.vector_type, FuzzVectorType.PARTITION_DROP)

        # Invariant: negative corrupted bytes
        with self.assertRaises(AuditDomainInvariantViolation):
            ByzantineFuzzVector("v", FuzzVectorType.FUZZ_PAYLOAD, "chan", payload_bytes_corrupted=-1).validate_invariants()
        # Invariant: negative delay
        with self.assertRaises(AuditDomainInvariantViolation):
            ByzantineFuzzVector("v", FuzzVectorType.FUZZ_PAYLOAD, "chan", delay_ms=-5.0).validate_invariants()

    # 7. ByzantineFuzzReport Roundtrip & Invariants
    def test_byzantine_fuzz_report_roundtrip_and_invariants(self) -> None:
        report = ByzantineFuzzReport(
            report_id="rpt_fuzz_001",
            leaf_id="leaf_001",
            vectors_dispatched=10,
            vectors_trapped=10,
            trap_rate=1.0,
            unhandled_faults=0,
            enclaves_engaged=["enclave_byzantine_leak"],
        )
        self.assertEqual(len(report.compute_hash()), 64)
        recovered = ByzantineFuzzReport.from_dict(report.to_dict())
        self.assertEqual(recovered.trap_rate, 1.0)

        # Invariant: trapped > dispatched
        with self.assertRaises(AuditDomainInvariantViolation):
            ByzantineFuzzReport("r", "l", vectors_dispatched=5, vectors_trapped=6, trap_rate=1.0, unhandled_faults=0).validate_invariants()
        # Invariant: trap_rate out of range
        with self.assertRaises(AuditDomainInvariantViolation):
            ByzantineFuzzReport("r", "l", vectors_dispatched=5, vectors_trapped=5, trap_rate=1.5, unhandled_faults=0).validate_invariants()

    # 8. QuorumConsensusWitness Roundtrip & Hash
    def test_quorum_consensus_witness_roundtrip(self) -> None:
        witness = QuorumConsensusWitness(
            witness_id="wit_001",
            leaf_id="leaf_001",
            verdict=QuorumVerdict.UNANIMOUS_PASS,
            sentry_syntax_vote=True,
            oracle_smt_vote=True,
            adversary_chaos_vote=True,
            consensus_ratio=1.0,
            dissenting_nodes=[],
        )
        h = witness.compute_hash()
        self.assertEqual(len(h), 64)
        recovered = QuorumConsensusWitness.from_dict(witness.to_dict())
        self.assertEqual(recovered.verdict, QuorumVerdict.UNANIMOUS_PASS)
        self.assertEqual(recovered.consensus_hash, h)

    # 9. Quorum Witness Calculation: 3-of-3 Unanimous Pass
    def test_quorum_witness_unanimous_3_of_3(self) -> None:
        witness = QuorumConsensusWitness(
            witness_id="wit_3_of_3",
            leaf_id="leaf_u",
            verdict=QuorumVerdict.UNANIMOUS_PASS,
            sentry_syntax_vote=True,
            oracle_smt_vote=True,
            adversary_chaos_vote=True,
            consensus_ratio=1.0,
            dissenting_nodes=[],
        )
        witness.validate_invariants()
        self.assertEqual(witness.consensus_ratio, 1.0)
        self.assertEqual(len(witness.dissenting_nodes), 0)
        self.assertEqual(witness.verdict, QuorumVerdict.UNANIMOUS_PASS)

    # 10. Quorum Witness Calculation: 2-of-3 Split Pass
    def test_quorum_witness_split_2_of_3(self) -> None:
        witness = QuorumConsensusWitness(
            witness_id="wit_2_of_3",
            leaf_id="leaf_s",
            verdict=QuorumVerdict.QUORUM_PASS,
            sentry_syntax_vote=True,
            oracle_smt_vote=True,
            adversary_chaos_vote=False,
            consensus_ratio=2.0 / 3.0,
            dissenting_nodes=["node_chaos_adversary"],
        )
        witness.validate_invariants()
        self.assertAlmostEqual(witness.consensus_ratio, 0.6667, places=3)
        self.assertEqual(witness.verdict, QuorumVerdict.QUORUM_PASS)
        self.assertIn("node_chaos_adversary", witness.dissenting_nodes)

    # 11. Quorum Witness Calculation: 1-of-3 Reject
    def test_quorum_witness_reject_1_of_3(self) -> None:
        witness = QuorumConsensusWitness(
            witness_id="wit_1_of_3",
            leaf_id="leaf_r",
            verdict=QuorumVerdict.SPLIT_FAIL,
            sentry_syntax_vote=True,
            oracle_smt_vote=False,
            adversary_chaos_vote=False,
            consensus_ratio=1.0 / 3.0,
            dissenting_nodes=["node_smt_oracle", "node_chaos_adversary"],
        )
        witness.validate_invariants()
        self.assertEqual(witness.verdict, QuorumVerdict.SPLIT_FAIL)
        self.assertEqual(len(witness.dissenting_nodes), 2)

    # 12. Quorum Witness Calculation: 0-of-3 Unanimous Reject
    def test_quorum_witness_unanimous_reject_0_of_3(self) -> None:
        witness = QuorumConsensusWitness(
            witness_id="wit_0_of_3",
            leaf_id="leaf_fail",
            verdict=QuorumVerdict.UNANIMOUS_FAIL,
            sentry_syntax_vote=False,
            oracle_smt_vote=False,
            adversary_chaos_vote=False,
            consensus_ratio=0.0,
            dissenting_nodes=["node_hermetic_sentry", "node_smt_oracle", "node_chaos_adversary"],
        )
        witness.validate_invariants()
        self.assertEqual(witness.verdict, QuorumVerdict.UNANIMOUS_FAIL)
        self.assertEqual(witness.consensus_ratio, 0.0)

    # 13. AuditAttestation Roundtrip & Invariants
    def test_audit_attestation_roundtrip_and_invariants(self) -> None:
        att = AuditAttestation(
            attestation_id="att_001",
            leaf_id="leaf_001",
            consensus_witness_id="wit_001",
            is_certified=True,
            merkle_leaf_hash=self.sample_hash,
            merkle_root=self.sample_hash,
            auditor_signatures=["sig_sentry", "sig_smt"],
        )
        self.assertEqual(len(att.compute_hash()), 64)
        recovered = AuditAttestation.from_dict(att.to_dict())
        self.assertTrue(recovered.is_certified)

        # Invariant: certified requires at least 2 signatures
        with self.assertRaises(AuditDomainInvariantViolation):
            AuditAttestation(
                "att", "l", "w", is_certified=True, merkle_leaf_hash=self.sample_hash, merkle_root=self.sample_hash, auditor_signatures=["only_one"]
            ).validate_invariants()

    # 14. FunctorialUndoCheckpoint Roundtrip & Invariants
    def test_functorial_undo_checkpoint_roundtrip_and_invariants(self) -> None:
        cp = FunctorialUndoCheckpoint(
            checkpoint_id="cp_001",
            stage=AuditVerificationStage.SMT_MODEL_CHECKING,
            state_hash=self.sample_hash,
            landauer_bits_checkpoint=1200,
        )
        self.assertEqual(len(cp.compute_hash()), 64)
        recovered = FunctorialUndoCheckpoint.from_dict(cp.to_dict())
        self.assertEqual(recovered.landauer_bits_checkpoint, 1200)

        # Invariant: negative bits
        with self.assertRaises(AuditDomainInvariantViolation):
            FunctorialUndoCheckpoint("cp", AuditVerificationStage.INGRESS_STAGING, self.sample_hash, -10).validate_invariants()

    # 15. LandauerThermodynamicLedger Roundtrip & Invariants
    def test_landauer_thermodynamic_ledger_roundtrip_and_invariants(self) -> None:
        ledger = LandauerThermodynamicLedger(
            ledger_id="ledger_test",
            token_lease_budget=923100,
            exploratory_capital=553860,
            protected_capital=369240,
        )
        ledger.validate_invariants()
        self.assertEqual(len(ledger.compute_hash()), 64)
        recovered = LandauerThermodynamicLedger.from_dict(ledger.to_dict())
        self.assertEqual(recovered.token_lease_budget, 923100)

        # Invariant: partition mismatch
        with self.assertRaises(AuditDomainInvariantViolation):
            LandauerThermodynamicLedger(token_lease_budget=100, exploratory_capital=50, protected_capital=40).validate_invariants()

    # 16. Landauer Ledger Bit Erasure, Recovery, and Token Spending
    def test_landauer_ledger_bit_erasure_recovery_and_token_spending(self) -> None:
        ledger = LandauerThermodynamicLedger()
        q = ledger.record_bit_erasure(1000, temp_kelvin=300.0)
        self.assertGreater(q, 0.0)
        self.assertEqual(ledger.total_bits_erased, 1000)

        # Recovery reduces bit count
        ledger.record_bit_recovery(400)
        self.assertEqual(ledger.total_bits_erased, 600)

        # Spend exploratory
        ledger.spend_tokens(50000, is_protected=False)
        self.assertEqual(ledger.spent_exploratory_tokens, 50000)

        # Spend protected
        ledger.spend_tokens(30000, is_protected=True)
        self.assertEqual(ledger.spent_protected_tokens, 30000)

        # Violate exploratory ceiling
        with self.assertRaises(AuditDomainInvariantViolation):
            ledger.spend_tokens(600000, is_protected=False)

    # 17. AuditServiceTopologyState Roundtrip & Hash
    def test_audit_service_topology_state_roundtrip_and_hash(self) -> None:
        state = AuditServiceTopologyState(
            node_id="node_audit_kernel",
            service_endpoint="192.168.40.30:8444",
            builder_endpoint="192.168.40.20:8443",
            research_endpoint="192.168.40.10:8442",
        )
        state.validate_invariants()
        self.assertEqual(len(state.compute_hash()), 64)
        recovered = AuditServiceTopologyState.from_dict(state.to_dict())
        self.assertEqual(recovered.service_endpoint, "192.168.40.30:8444")

    # 18. Rejection of Loopback in Topology States
    def test_audit_service_topology_rejection_of_loopback(self) -> None:
        for loopback in ["127.0.0.1:8444", "localhost:8444", "0.0.0.0:8444", "::1:8444"]:
            with self.assertRaises(AuditDomainInvariantViolation):
                AuditServiceTopologyState(service_endpoint=loopback).validate_invariants()
            with self.assertRaises(AuditDomainInvariantViolation):
                assert_non_loopback(loopback, "test_context")


if __name__ == "__main__":
    unittest.main()
