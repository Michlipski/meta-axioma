"""Unit & Adversarial Invariant Test Suite for Sheaf-Quorum Consensus Engine (`[NEG-PRIMITIVE-001]`).

Validates:
1. 3-of-3 unanimous certification (UNANIMOUS_PASS).
2. 2-of-3 split quorum certification when Chaos fails (QUORUM_PASS).
3. 2-of-3 split quorum certification when SMT fails (QUORUM_PASS).
4. 1-of-3 rejection when only Syntax approves (SPLIT_FAIL).
5. 0-of-3 unanimous rejection (UNANIMOUS_FAIL).
6. Byzantine voter quarantine / unauthorized node rejection.
7. End-to-end adjudicate_triad with verified reports.
8. Rejection of mismatched leaf_ids during triad adjudication.
"""

from __future__ import annotations

from pathlib import Path
import sys
import unittest

AUDIT_ROOT = Path(__file__).resolve().parent.parent
REPO_ROOT = AUDIT_ROOT.parent.parent.parent.parent
for p in [str(AUDIT_ROOT), str(AUDIT_ROOT / "src"), str(REPO_ROOT)]:
    if p not in sys.path:
        sys.path.insert(0, p)

from src.domain_models import (
    AuditDomainInvariantViolation,
    ByzantineFuzzReport,
    HermeticAuditReport,
    MorphismCheckStatus,
    QuorumConsensusWitness,
    QuorumVerdict,
    SMTModelCheckResult,
)
from src.sheaf_quorum_consensus import SheafQuorumConsensusEngine


class TestSheafQuorumConsensus(unittest.TestCase):
    """Exhaustive tests for 2-of-3 Sheaf Quorum adversarial consensus."""

    def setUp(self) -> None:
        self.engine = SheafQuorumConsensusEngine()

    # 1. 3-of-3 Unanimous Certification
    def test_unanimous_certification_3_of_3(self) -> None:
        leaf_id = "leaf_unanimous"
        self.engine.cast_peer_vote("node_hermetic_sentry", leaf_id, True)
        self.engine.cast_peer_vote("node_smt_oracle", leaf_id, True)
        self.engine.cast_peer_vote("node_chaos_adversary", leaf_id, True)

        witness = self.engine.evaluate_quorum(leaf_id)
        self.assertEqual(witness.verdict, QuorumVerdict.UNANIMOUS_PASS)
        self.assertEqual(witness.consensus_ratio, 1.0)
        self.assertTrue(witness.sentry_syntax_vote)
        self.assertTrue(witness.oracle_smt_vote)
        self.assertTrue(witness.adversary_chaos_vote)
        self.assertEqual(len(witness.dissenting_nodes), 0)

    # 2. 2-of-3 Split Quorum Certification (Chaos fails)
    def test_split_quorum_certification_2_of_3_chaos_fails(self) -> None:
        leaf_id = "leaf_split_chaos_fails"
        self.engine.cast_peer_vote("node_hermetic_sentry", leaf_id, True)
        self.engine.cast_peer_vote("node_smt_oracle", leaf_id, True)
        self.engine.cast_peer_vote("node_chaos_adversary", leaf_id, False)

        witness = self.engine.evaluate_quorum(leaf_id)
        self.assertEqual(witness.verdict, QuorumVerdict.QUORUM_PASS)
        self.assertAlmostEqual(witness.consensus_ratio, 2.0 / 3.0, places=3)
        self.assertEqual(witness.dissenting_nodes, ["node_chaos_adversary"])

    # 3. 2-of-3 Split Quorum Certification (SMT fails)
    def test_split_quorum_certification_2_of_3_smt_fails(self) -> None:
        leaf_id = "leaf_split_smt_fails"
        self.engine.cast_peer_vote("node_hermetic_sentry", leaf_id, True)
        self.engine.cast_peer_vote("node_smt_oracle", leaf_id, False)
        self.engine.cast_peer_vote("node_chaos_adversary", leaf_id, True)

        witness = self.engine.evaluate_quorum(leaf_id)
        self.assertEqual(witness.verdict, QuorumVerdict.QUORUM_PASS)
        self.assertAlmostEqual(witness.consensus_ratio, 2.0 / 3.0, places=3)
        self.assertEqual(witness.dissenting_nodes, ["node_smt_oracle"])

    # 4. 1-of-3 Rejection (Only Syntax Approves)
    def test_rejection_1_of_3_only_syntax_approves(self) -> None:
        leaf_id = "leaf_reject_1_of_3"
        self.engine.cast_peer_vote("node_hermetic_sentry", leaf_id, True)
        self.engine.cast_peer_vote("node_smt_oracle", leaf_id, False)
        self.engine.cast_peer_vote("node_chaos_adversary", leaf_id, False)

        witness = self.engine.evaluate_quorum(leaf_id)
        self.assertEqual(witness.verdict, QuorumVerdict.SPLIT_FAIL)
        self.assertAlmostEqual(witness.consensus_ratio, 1.0 / 3.0, places=3)
        self.assertEqual(len(witness.dissenting_nodes), 2)
        self.assertIn("node_smt_oracle", witness.dissenting_nodes)
        self.assertIn("node_chaos_adversary", witness.dissenting_nodes)

    # 5. 0-of-3 Unanimous Rejection
    def test_unanimous_rejection_0_of_3(self) -> None:
        leaf_id = "leaf_reject_0_of_3"
        self.engine.cast_peer_vote("node_hermetic_sentry", leaf_id, False)
        self.engine.cast_peer_vote("node_smt_oracle", leaf_id, False)
        self.engine.cast_peer_vote("node_chaos_adversary", leaf_id, False)

        witness = self.engine.evaluate_quorum(leaf_id)
        self.assertEqual(witness.verdict, QuorumVerdict.UNANIMOUS_FAIL)
        self.assertEqual(witness.consensus_ratio, 0.0)
        self.assertEqual(len(witness.dissenting_nodes), 3)

    # 6. Byzantine Voter Quarantine / Unauthorized Node Rejection
    def test_unauthorized_node_vote_rejection(self) -> None:
        with self.assertRaises(AuditDomainInvariantViolation):
            self.engine.cast_peer_vote("node_malicious_intruder", "leaf_hack", True)

    # 7. End-to-End adjudicate_triad
    def test_adjudicate_triad_end_to_end(self) -> None:
        leaf_id = "leaf_triad_verified"
        hermetic = HermeticAuditReport(
            report_id="rpt_h",
            leaf_id=leaf_id,
            is_hermetic=True,
            violations=[],
        )
        smt = SMTModelCheckResult(
            check_id="chk_s",
            leaf_id=leaf_id,
            morphism_status=MorphismCheckStatus.PROVEN_VALID,
            precondition_entailment_valid=True,
            postcondition_consequence_valid=True,
            is_deadlock_free=True,
        )
        fuzz = ByzantineFuzzReport(
            report_id="rpt_f",
            leaf_id=leaf_id,
            vectors_dispatched=6,
            vectors_trapped=6,
            trap_rate=1.0,
            unhandled_faults=0,
        )

        witness = self.engine.adjudicate_triad(hermetic, smt, fuzz)
        self.assertEqual(witness.leaf_id, leaf_id)
        self.assertEqual(witness.verdict, QuorumVerdict.UNANIMOUS_PASS)
        self.assertEqual(witness.consensus_ratio, 1.0)

    # 8. Rejection of Mismatched leaf_id in Triad
    def test_adjudicate_triad_leaf_id_mismatch_rejection(self) -> None:
        hermetic = HermeticAuditReport(report_id="r1", leaf_id="leaf_A", is_hermetic=True)
        smt = SMTModelCheckResult(
            check_id="r2",
            leaf_id="leaf_B",  # mismatch
            morphism_status=MorphismCheckStatus.PROVEN_VALID,
            precondition_entailment_valid=True,
            postcondition_consequence_valid=True,
            is_deadlock_free=True,
        )
        fuzz = ByzantineFuzzReport(
            report_id="r3",
            leaf_id="leaf_A",
            vectors_dispatched=1,
            vectors_trapped=1,
            trap_rate=1.0,
            unhandled_faults=0,
        )
        with self.assertRaises(AuditDomainInvariantViolation):
            self.engine.adjudicate_triad(hermetic, smt, fuzz)


if __name__ == "__main__":
    unittest.main()
