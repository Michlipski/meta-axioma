"""Unit & Adversarial Invariant Test Suite for Hierarchical Statechart & Functorial Undo (`[L1-002]`).

Validates:
1. Exact membership and count of all 30 formal states.
2. Complete happy path traversal across all 4 strata to attestation_sealed and audit_terminal_certified.
3. Deep history checkpoint restoration for hp_pre_audit.
4. Deep history checkpoint restoration for hp_pre_smt.
5. Deep history checkpoint restoration for hp_pre_attestation.
6. Entry and healing exit of enclave_syntax_breach.
7. Entry and healing exit of enclave_smt_unsat_core.
8. Entry and healing exit of enclave_byzantine_leak.
9. Emergency interception and healing exit of enclave_network_loopback.
10. Functorial undo state restoration and Landauer bit recovery.
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
    AuditDomainInvariantViolation,
    AuditVerificationStage,
    FunctorialUndoCheckpoint,
    LandauerThermodynamicLedger,
)
from src.functorial_undo import AuditFunctorialUndoManager, FunctorialUndoViolation
from src.statechart_engine import AuditStatechartEngine


class TestStatechartAndUndo(unittest.TestCase):
    """Exhaustive tests for the 30-state XState v5 engine, deep history, enclaves, and functorial undo."""

    def setUp(self) -> None:
        self.fsm = AuditStatechartEngine()
        self.undo_mgr = AuditFunctorialUndoManager()

    # 1. Confirms Exact Membership of All 30 States
    def test_exact_membership_of_all_30_states(self) -> None:
        self.assertEqual(len(AuditStatechartEngine.STATES), 30)

        # Stratum 1: INGRESS (4)
        for s in ["ingress_idle", "ingress_receiving", "ingress_validating", "ingress_staged"]:
            self.assertIn(s, AuditStatechartEngine.STATES)

        # Stratum 2: CRUCIBLE (4)
        for s in ["crucible_hermetic_lint", "crucible_smt_check", "crucible_chaos_fuzz", "crucible_evaluating"]:
            self.assertIn(s, AuditStatechartEngine.STATES)

        # Stratum 3: SHEAF QUORUM (4)
        for s in ["quorum_collecting", "quorum_voting", "quorum_reached", "quorum_rejected"]:
            self.assertIn(s, AuditStatechartEngine.STATES)

        # Stratum 4: ATTESTATION (4)
        for s in ["attestation_merkle_anchor", "attestation_signing", "attestation_dispatch", "attestation_sealed"]:
            self.assertIn(s, AuditStatechartEngine.STATES)

        # Parallel Region 1: Sentry (3)
        for s in ["sentry_monitoring", "sentry_quarantining", "sentry_cleared"]:
            self.assertIn(s, AuditStatechartEngine.STATES)

        # Parallel Region 2: Thermodynamics (3)
        for s in ["thermo_accounting", "thermo_recovering", "thermo_settled"]:
            self.assertIn(s, AuditStatechartEngine.STATES)

        # Deep History (3)
        for s in ["hp_pre_audit", "hp_pre_smt", "hp_pre_attestation"]:
            self.assertIn(s, AuditStatechartEngine.STATES)

        # Recovery Enclaves (4)
        for s in ["enclave_syntax_breach", "enclave_smt_unsat_core", "enclave_byzantine_leak", "enclave_network_loopback"]:
            self.assertIn(s, AuditStatechartEngine.STATES)

        # Terminal (1)
        self.assertIn("audit_terminal_certified", AuditStatechartEngine.STATES)

    # 2. Complete Happy Path Traversal
    def test_complete_happy_path_traversal(self) -> None:
        self.assertEqual(self.fsm.current_state, "ingress_idle")

        # Stratum 1
        self.fsm.send("EV_RECEIVE_CANDIDATE")
        self.assertEqual(self.fsm.current_state, "ingress_receiving")
        self.fsm.send("EV_VALIDATE_ENDPOINT")
        self.assertEqual(self.fsm.current_state, "ingress_validating")
        self.fsm.send("EV_STAGE_READY")
        self.assertEqual(self.fsm.current_state, "ingress_staged")

        # Stratum 2
        self.fsm.send("EV_START_AUDIT")
        self.assertEqual(self.fsm.current_state, "crucible_hermetic_lint")
        self.fsm.send("EV_HERMETIC_PASS")
        self.assertEqual(self.fsm.current_state, "crucible_smt_check")
        self.fsm.send("EV_SMT_PASS")
        self.assertEqual(self.fsm.current_state, "crucible_chaos_fuzz")
        self.fsm.send("EV_CHAOS_PASS")
        self.assertEqual(self.fsm.current_state, "crucible_evaluating")

        # Stratum 3
        self.fsm.send("EV_EVALUATE_QUORUM")
        self.assertEqual(self.fsm.current_state, "quorum_collecting")
        self.fsm.send("EV_VOTES_COLLECTED")
        self.assertEqual(self.fsm.current_state, "quorum_voting")
        self.fsm.send("EV_QUORUM_APPROVED")
        self.assertEqual(self.fsm.current_state, "quorum_reached")

        # Stratum 4
        self.fsm.send("EV_INITIATE_ATTESTATION")
        self.assertEqual(self.fsm.current_state, "attestation_merkle_anchor")
        self.fsm.send("EV_MERKLE_ANCHORED")
        self.assertEqual(self.fsm.current_state, "attestation_signing")
        self.fsm.send("EV_SIGNATURES_COLLECTED")
        self.assertEqual(self.fsm.current_state, "attestation_dispatch")
        self.fsm.send("EV_DISPATCH_COMPLETE")
        self.assertEqual(self.fsm.current_state, "attestation_sealed")

        # Terminal
        self.fsm.send("EV_SEAL_FINAL")
        self.assertEqual(self.fsm.current_state, "audit_terminal_certified")

    # 3. Deep History Restoration for hp_pre_audit
    def test_deep_history_hp_pre_audit(self) -> None:
        self.fsm.send("EV_RECEIVE_CANDIDATE")
        self.fsm.send("EV_VALIDATE_ENDPOINT")
        self.fsm.send("EV_STAGE_READY")
        self.fsm.send("EV_START_AUDIT")  # Records hp_pre_audit = ingress_staged
        self.assertEqual(self.fsm.current_state, "crucible_hermetic_lint")

        # Jump back via deep history
        self.fsm.send("EV_RESTORE_HP_PRE_AUDIT")
        self.assertEqual(self.fsm.current_state, "ingress_staged")

    # 4. Deep History Restoration for hp_pre_smt
    def test_deep_history_hp_pre_smt(self) -> None:
        self.fsm.send("EV_RECEIVE_CANDIDATE")
        self.fsm.send("EV_VALIDATE_ENDPOINT")
        self.fsm.send("EV_STAGE_READY")
        self.fsm.send("EV_START_AUDIT")
        self.fsm.send("EV_HERMETIC_PASS")  # Records hp_pre_smt = crucible_hermetic_lint
        self.assertEqual(self.fsm.current_state, "crucible_smt_check")

        self.fsm.send("EV_RESTORE_HP_PRE_SMT")
        self.assertEqual(self.fsm.current_state, "crucible_hermetic_lint")

    # 5. Deep History Restoration for hp_pre_attestation
    def test_deep_history_hp_pre_attestation(self) -> None:
        fsm = AuditStatechartEngine(initial_state="quorum_reached")
        fsm.send("EV_INITIATE_ATTESTATION")
        self.assertEqual(fsm.current_state, "attestation_merkle_anchor")

        fsm.send("EV_RESTORE_HP_PRE_ATTESTATION")
        self.assertEqual(fsm.current_state, "quorum_reached")

    # 6. Entry and Exit of enclave_syntax_breach
    def test_recovery_enclave_syntax_breach_entry_and_exit(self) -> None:
        fsm = AuditStatechartEngine(initial_state="crucible_hermetic_lint")
        fsm.send("EV_HERMETIC_FAIL")
        self.assertEqual(fsm.current_state, "enclave_syntax_breach")

        # Heal syntax -> returns to crucible_hermetic_lint
        fsm.send("EV_HEAL_SYNTAX")
        self.assertEqual(fsm.current_state, "crucible_hermetic_lint")

    # 7. Entry and Exit of enclave_smt_unsat_core
    def test_recovery_enclave_smt_unsat_core_entry_and_exit(self) -> None:
        fsm = AuditStatechartEngine(initial_state="crucible_smt_check")
        fsm.send("EV_SMT_FAIL")
        self.assertEqual(fsm.current_state, "enclave_smt_unsat_core")

        # Heal SMT -> returns to crucible_smt_check
        fsm.send("EV_HEAL_SMT")
        self.assertEqual(fsm.current_state, "crucible_smt_check")

    # 8. Entry and Exit of enclave_byzantine_leak
    def test_recovery_enclave_byzantine_leak_entry_and_exit(self) -> None:
        fsm = AuditStatechartEngine(initial_state="crucible_chaos_fuzz")
        fsm.send("EV_CHAOS_FAIL")
        self.assertEqual(fsm.current_state, "enclave_byzantine_leak")

        # Heal Byzantine -> returns to crucible_chaos_fuzz
        fsm.send("EV_HEAL_BYZANTINE")
        self.assertEqual(fsm.current_state, "crucible_chaos_fuzz")

    # 9. Emergency Interception and Exit of enclave_network_loopback
    def test_recovery_enclave_network_loopback_emergency(self) -> None:
        fsm = AuditStatechartEngine(initial_state="crucible_smt_check")
        fsm.send("EV_LOOPBACK_DETECTED")
        self.assertEqual(fsm.current_state, "enclave_network_loopback")
        self.assertEqual(fsm.parallel_sentry_state, "sentry_quarantining")

        # Isolate loopback -> returns to ingress_idle with sentry cleared
        fsm.send("EV_ISOLATE_LOOPBACK")
        self.assertEqual(fsm.current_state, "ingress_idle")
        self.assertEqual(fsm.parallel_sentry_state, "sentry_cleared")

    # 10. Functorial Undo State Restoration & Landauer Bit Recovery
    def test_functorial_undo_checkpoint_and_bit_recovery(self) -> None:
        ledger = LandauerThermodynamicLedger()

        # Step 1: Base checkpoint at 1,000 bits erased
        ledger.record_bit_erasure(1000)
        h1 = hashlib.sha256(b"state_step_1").hexdigest()
        cp1 = self.undo_mgr.create_checkpoint(
            stage=AuditVerificationStage.INGRESS_STAGING,
            state_hash=h1,
            landauer_bits_checkpoint=ledger.total_bits_erased,
            context={"step": 1},
        )

        # Step 2: Second checkpoint at 2,500 bits erased (+1500)
        ledger.record_bit_erasure(1500)
        h2 = hashlib.sha256(b"state_step_2").hexdigest()
        cp2 = self.undo_mgr.create_checkpoint(
            stage=AuditVerificationStage.HERMETIC_LINTING,
            state_hash=h2,
            landauer_bits_checkpoint=ledger.total_bits_erased,
            context={"step": 2},
        )

        # Step 3: Additional erasure (+1000) -> total 3500 bits
        ledger.record_bit_erasure(1000)
        self.assertEqual(ledger.total_bits_erased, 3500)

        # Adjoint rollback to cp1: should restore bits to 1000 (-2500 recovered)
        restored_cp = self.undo_mgr.rollback_to_checkpoint(cp1.checkpoint_id, thermodynamic_ledger=ledger)
        self.assertEqual(restored_cp.checkpoint_id, cp1.checkpoint_id)
        self.assertEqual(ledger.total_bits_erased, 1000)
        self.assertEqual(self.undo_mgr.get_stack_depth(), 1)


if __name__ == "__main__":
    unittest.main()
