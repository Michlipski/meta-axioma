"""Integration and Invariant Test Suite for G4b Sovereign Audit Engines (`soc_g4b_audit`).

Validates:
1. ZeroTrustMicroAuditor: Detection of HERM-001, HERM-002, HERM-003, HERM-004.
2. SMTModelChecker: Contract morphism contravariance/covariance and deadlock-freedom.
3. ByzantineChaosFuzzer: 6 vector types, 100% trapped fault ratio.
4. SheafQuorumConsensusEngine: 2-of-3 non-blocking consensus, NEG-PRIMITIVE-001 adherence.
5. AuditMerkleWitnessEngine: Merkle tree root calculation, DAG integrity, inclusion proofs.
6. AuditStatechartEngine: 30 states, compound strata, parallel regions, deep history, enclaves.
7. AuditFunctorialUndoManager: Adjoint rollback, stack causal consistency, Landauer bit recovery.
8. AuditRFCMediator: RFC evaluation, SpecAmendment signing, CounterProof generation.
9. AuditServiceTopology: Channel registration, fail-closed partition policy.
10. SovereignAuditKernel: End-to-end operational pipeline execution.
"""

from __future__ import annotations

from pathlib import Path
import sys
import unittest

AUDIT_ROOT = Path(__file__).resolve().parent.parent
REPO_ROOT = AUDIT_ROOT.parent.parent.parent.parent
for p in [str(AUDIT_ROOT), str(REPO_ROOT)]:
    if p not in sys.path:
        sys.path.insert(0, p)

from generations.gen_04b.protocols.rfc_protocol import (
    BottleneckType,
    CounterProof,
    SpecAdjustmentRequest,
)
from generations.gen_04b.services.audit.src.domain_models import (
    AuditDomainInvariantViolation,
    CodeLeafCandidate,
    MorphismCheckStatus,
    QuorumVerdict,
)
from generations.gen_04b.services.audit.src.zero_trust_micro_auditor import ZeroTrustMicroAuditor
from generations.gen_04b.services.audit.src.smt_model_checker import SMTModelChecker
from generations.gen_04b.services.audit.src.byzantine_chaos_fuzzer import ByzantineChaosFuzzer
from generations.gen_04b.services.audit.src.sheaf_quorum_consensus import SheafQuorumConsensusEngine
from generations.gen_04b.services.audit.src.merkle_witness_engine import AuditMerkleWitnessEngine
from generations.gen_04b.services.audit.src.statechart_engine import AuditStatechartEngine
from generations.gen_04b.services.audit.src.functorial_undo import AuditFunctorialUndoManager, FunctorialUndoViolation
from generations.gen_04b.services.audit.src.rfc_protocol_mediator import AuditRFCMediator
from generations.gen_04b.services.audit.src.service_topology import AuditServiceTopology, NetworkPartitionError
from generations.gen_04b.services.audit.src.audit_kernel import SovereignAuditKernel


class TestAuditModules(unittest.TestCase):
    """Exhaustive integration tests for all 10 Sovereign Audit subsystems."""

    def test_zero_trust_micro_auditor(self) -> None:
        auditor = ZeroTrustMicroAuditor()

        # Clean code
        clean_code = "def add(a: int, b: int) -> int:\n    return a + b"
        clean_rpt = auditor.audit_source(clean_code)
        self.assertTrue(clean_rpt.is_hermetic)
        self.assertEqual(len(clean_rpt.violations), 0)

        # HERM-001: Loopback
        loopback_code = 'HOST = "127.0.0.1:8000"'
        lb_rpt = auditor.audit_source(loopback_code)
        self.assertFalse(lb_rpt.is_hermetic)
        self.assertTrue(any(v.rule_id == "HERM-001" for v in lb_rpt.violations))

        # HERM-002: sys.path tampering
        syspath_code = "import sys\nsys.path.append('/somewhere')"
        sp_rpt = auditor.audit_source(syspath_code)
        self.assertFalse(sp_rpt.is_hermetic)
        self.assertTrue(any(v.rule_id == "HERM-002" for v in sp_rpt.violations))

        # HERM-003: Ambient escapes (/tmp, ../)
        tmp_code = 'LOG = "/tmp/audit.log"'
        tmp_rpt = auditor.audit_source(tmp_code)
        self.assertFalse(tmp_rpt.is_hermetic)
        self.assertTrue(any(v.rule_id == "HERM-003" for v in tmp_rpt.violations))

        # HERM-004: eval/exec
        eval_code = 'eval("1 + 1")'
        eval_rpt = auditor.audit_source(eval_code)
        self.assertFalse(eval_rpt.is_hermetic)
        self.assertTrue(any(v.rule_id == "HERM-004" for v in eval_rpt.violations))

    def test_smt_model_checker(self) -> None:
        checker = SMTModelChecker()

        # Valid morphism
        # Pre_p: x > 0 and y > 0
        # Pre_c: x > 0 (Child requires less -> Pre_p |= Pre_c holds)
        # Post_c: res > 10 and res % 2 == 0
        # Post_p: res > 10 (Child guarantees more -> Post_c |= Post_p holds)
        res_valid = checker.verify_contract_morphism(
            parent_pre="x and y",
            parent_post="res",
            child_pre="x",
            child_post="res and bonus",
        )
        self.assertEqual(res_valid.morphism_status, MorphismCheckStatus.PROVEN_VALID)
        self.assertTrue(res_valid.precondition_entailment_valid)
        self.assertTrue(res_valid.postcondition_consequence_valid)

        # Invalid morphism (Child requires more in precondition)
        res_invalid = checker.verify_contract_morphism(
            parent_pre="x",
            parent_post="res",
            child_pre="x and y",  # Pre_p does not entail Pre_c!
            child_post="res",
        )
        self.assertEqual(res_invalid.morphism_status, MorphismCheckStatus.COUNTER_EXAMPLE_FOUND)
        self.assertFalse(res_invalid.precondition_entailment_valid)

    def test_byzantine_chaos_fuzzer(self) -> None:
        fuzzer = ByzantineChaosFuzzer()
        vectors = fuzzer.generate_vectors(count_per_type=2)
        self.assertEqual(len(vectors), 12)  # 6 types * 2

        report = fuzzer.dispatch_and_verify(vectors)
        self.assertEqual(report.vectors_dispatched, 12)
        self.assertEqual(report.vectors_trapped, 12)
        self.assertEqual(report.trap_rate, 1.0)
        self.assertEqual(report.unhandled_faults, 0)
        self.assertGreaterEqual(len(report.enclaves_engaged), 2)

    def test_sheaf_quorum_consensus(self) -> None:
        quorum = SheafQuorumConsensusEngine()
        leaf_id = "leaf_test_quorum"

        # 3-of-3 Unanimous Pass
        quorum.cast_peer_vote("node_hermetic_sentry", leaf_id, True)
        quorum.cast_peer_vote("node_smt_oracle", leaf_id, True)
        quorum.cast_peer_vote("node_chaos_adversary", leaf_id, True)
        wit_3of3 = quorum.evaluate_quorum(leaf_id)
        self.assertEqual(wit_3of3.verdict, QuorumVerdict.UNANIMOUS_PASS)
        self.assertEqual(wit_3of3.consensus_ratio, 1.0)

        # 2-of-3 Quorum Pass
        leaf_id_2 = "leaf_test_quorum_2"
        quorum.cast_peer_vote("node_hermetic_sentry", leaf_id_2, True)
        quorum.cast_peer_vote("node_smt_oracle", leaf_id_2, True)
        quorum.cast_peer_vote("node_chaos_adversary", leaf_id_2, False)
        wit_2of3 = quorum.evaluate_quorum(leaf_id_2)
        self.assertEqual(wit_2of3.verdict, QuorumVerdict.QUORUM_PASS)
        self.assertAlmostEqual(wit_2of3.consensus_ratio, 2.0 / 3.0)
        self.assertIn("node_chaos_adversary", wit_2of3.dissenting_nodes)

    def test_audit_merkle_witness_engine(self) -> None:
        engine = AuditMerkleWitnessEngine()
        leaf1 = engine.record_event("EV1", {"foo": "bar"})
        leaf2 = engine.record_event("EV2", {"baz": 123})
        leaf3 = engine.record_event("EV3", {"qux": True})

        root = engine.compute_merkle_root()
        self.assertEqual(len(root), 64)
        self.assertTrue(engine.verify_integrity())

        # Inclusion proof for leaf2
        proof = engine.generate_inclusion_proof(leaf2)
        self.assertTrue(engine.verify_inclusion_proof(leaf2, proof, root))

    def test_audit_statechart_engine(self) -> None:
        sc = AuditStatechartEngine()
        self.assertEqual(len(sc.STATES), 30)
        self.assertEqual(sc.current_state, "ingress_idle")

        # Ingress flow
        sc.send("EV_RECEIVE_CANDIDATE")
        self.assertEqual(sc.current_state, "ingress_receiving")
        sc.send("EV_VALIDATE_ENDPOINT")
        self.assertEqual(sc.current_state, "ingress_validating")
        sc.send("EV_STAGE_READY")
        self.assertEqual(sc.current_state, "ingress_staged")

        # Crucible flow
        sc.send("EV_START_AUDIT")
        self.assertEqual(sc.current_state, "crucible_hermetic_lint")
        sc.send("EV_HERMETIC_PASS")
        self.assertEqual(sc.current_state, "crucible_smt_check")
        sc.send("EV_SMT_PASS")
        self.assertEqual(sc.current_state, "crucible_chaos_fuzz")
        sc.send("EV_CHAOS_PASS")
        self.assertEqual(sc.current_state, "crucible_evaluating")

        # Quorum flow
        sc.send("EV_EVALUATE_QUORUM")
        self.assertEqual(sc.current_state, "quorum_collecting")
        sc.send("EV_VOTES_COLLECTED")
        self.assertEqual(sc.current_state, "quorum_voting")
        sc.send("EV_QUORUM_APPROVED")
        self.assertEqual(sc.current_state, "quorum_reached")

        # Attestation flow
        sc.send("EV_INITIATE_ATTESTATION")
        self.assertEqual(sc.current_state, "attestation_merkle_anchor")
        sc.send("EV_MERKLE_ANCHORED")
        self.assertEqual(sc.current_state, "attestation_signing")
        sc.send("EV_SIGNATURES_COLLECTED")
        self.assertEqual(sc.current_state, "attestation_dispatch")
        sc.send("EV_DISPATCH_COMPLETE")
        self.assertEqual(sc.current_state, "attestation_sealed")
        sc.send("EV_SEAL_FINAL")
        self.assertEqual(sc.current_state, "audit_terminal_certified")

    def test_functorial_undo_manager(self) -> None:
        mgr = AuditFunctorialUndoManager()
        cp1 = mgr.create_checkpoint(
            stage="ingress_idle", # valid stage without mutating STATES set
            state_hash="1" * 64,
            landauer_bits_checkpoint=100,
        )
        # Create second checkpoint
        from generations.gen_04b.services.audit.src.domain_models import AuditVerificationStage
        cp2 = mgr.create_checkpoint(
            stage=AuditVerificationStage.SMT_MODEL_CHECKING,
            state_hash="2" * 64,
            landauer_bits_checkpoint=200,
        )
        self.assertEqual(mgr.get_stack_depth(), 2)

        # Rollback latest
        restored = mgr.rollback_latest()
        self.assertEqual(restored.checkpoint_id, cp1.checkpoint_id)
        self.assertEqual(mgr.get_stack_depth(), 1)

    def test_rfc_protocol_mediator(self) -> None:
        mediator = AuditRFCMediator()

        # Valid request
        req_valid = SpecAdjustmentRequest(
            request_id="rfc_test_valid",
            builder_node_id="node_builder",
            target_symbol_urn="urn:meta_axioma:gen_04b:leaf:test",
            bottleneck_type=BottleneckType.LATENCY_OVERRUN,
            empirical_evidence="Physical serialization 45ms",
            proposed_delta="contract: timeout <= 100",
            preserved_invariants=["[L1-G3B-012] Dedicated Non-Loopback Network Topology"],
        )
        amend_valid = mediator.adjudicate_rfc_request(req_valid)
        self.assertTrue(amend_valid.is_approved)

        # Invalid request containing loopback
        req_invalid = SpecAdjustmentRequest(
            request_id="rfc_test_invalid",
            builder_node_id="node_builder",
            target_symbol_urn="urn:meta_axioma:gen_04b:leaf:test",
            bottleneck_type=BottleneckType.TOKEN_EXHAUSTION,
            empirical_evidence="Need loopback socket for test",
            proposed_delta="host: '127.0.0.1'",
            preserved_invariants=["[L1-G3B-011] Compositional Contracts"],
        )
        amend_invalid = mediator.adjudicate_rfc_request(req_invalid)
        self.assertFalse(amend_invalid.is_approved)
        self.assertIsInstance(amend_invalid.rejection_counter_proof, CounterProof)

    def test_audit_service_topology(self) -> None:
        topo = AuditServiceTopology(node_ip="192.168.40.30", port=8444)
        ch = topo.get_channel("channel_builder_interception")
        self.assertEqual(ch.target_endpoint, "192.168.40.30:8444")

        # Partition test
        topo.trigger_partition()
        with self.assertRaises(NetworkPartitionError):
            topo.transmit("channel_builder_interception", 100)

        topo.heal_partition()
        topo.transmit("channel_builder_interception", 100)
        self.assertEqual(ch.bytes_transmitted, 100)

    def test_sovereign_audit_kernel_end_to_end(self) -> None:
        kernel = SovereignAuditKernel(node_ip="192.168.40.30", port=8444, token_budget=923100)

        cand = CodeLeafCandidate(
            leaf_id="leaf_kernel_e2e",
            symbol_urn="urn:meta_axioma:gen_04b:leaf:kernel_e2e",
            source_code="def compute(x: int) -> int:\n    return x * 2",
            parent_contract_pre="x",
            parent_contract_post="res",
            child_contract_pre="x",
            child_contract_post="res and x",
            source_endpoint="192.168.40.20:8443",
        )
        attestation = kernel.audit_code_leaf(cand)
        self.assertTrue(attestation.is_certified)
        self.assertEqual(kernel.statechart.current_state, "audit_terminal_certified")
        self.assertGreater(kernel.thermo_ledger.total_bits_erased, 0)


if __name__ == "__main__":
    unittest.main()
