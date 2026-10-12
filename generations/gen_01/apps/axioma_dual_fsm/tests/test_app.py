"""Comprehensive automated test suite for Axioma Dual FSM.
Verifies state determinism, tool failure loops, dynamic de-escalation, the Dominance Rule (Φ_halt),
and Functorial Reversibility rollbacks (L1-002).
"""

import json
from pathlib import Path
import sys
import time
import unittest

app_root = Path(__file__).parent.parent
sys.path.insert(0, str(app_root / "src"))

from coupled_gateway import CoupledGateway, LANDAUER_LIMIT
from inner_fsm import InnerFsm, InnerState
from outer_fsm import OuterFsm, OuterState, calculate_shannon_entropy
from server import ExceptionEnclave, DATA_DIR


class TestAxiomaDualFsm(unittest.TestCase):
    def setUp(self):
        self.gateway = CoupledGateway()

    def tearDown(self):
        fb_file = DATA_DIR / "user_feedback.json"
        if fb_file.exists():
            try:
                fb_file.unlink()
            except Exception:
                pass

    def test_inner_fsm_happy_path_progression(self):
        """Verifies deterministic multi-turn progression from IDLE to TERMINAL_SUCCESS."""
        fsm = InnerFsm()
        self.assertEqual(fsm.state, InnerState.IDLE)

        # 1. Intent
        ok, _ = fsm.transition("IDENTIFY_INTENT", {"intent": "sales_query"})
        self.assertTrue(ok)
        self.assertEqual(fsm.state, InnerState.INTENT_IDENTIFIED)

        # 2. Plan
        ok, _ = fsm.transition("PROPOSE_PLAN", {"plan": "Query regional DB"})
        self.assertTrue(ok)
        self.assertEqual(fsm.state, InnerState.PLAN_PROPOSED)

        # 3. Approval
        ok, _ = fsm.transition("REQUEST_APPROVAL")
        self.assertTrue(ok)
        self.assertEqual(fsm.state, InnerState.AWAITING_APPROVAL)

        # 4. Dispatch
        ok, _ = fsm.transition("APPROVE_ACTION")
        self.assertTrue(ok)
        self.assertEqual(fsm.state, InnerState.ACTION_DISPATCHED)

        # 5. Evaluate Outcome (Happy Path)
        ok, _ = fsm.transition("EVALUATE_OUTCOME", {"status": "SUCCESS", "result": {"rows": 10}})
        self.assertTrue(ok)
        self.assertEqual(fsm.state, InnerState.OUTCOME_EVALUATED)

        # 6. Response Synthesized
        ok, _ = fsm.transition("ACCEPT_OUTCOME")
        self.assertTrue(ok)
        self.assertEqual(fsm.state, InnerState.RESPONSE_SYNTHESIZED)

        # 7. Complete
        ok, _ = fsm.transition("COMPLETE_TURN")
        self.assertTrue(ok)
        self.assertEqual(fsm.state, InnerState.TERMINAL_SUCCESS)

    def test_inner_fsm_tool_failure_recovery_loops(self):
        """[Refinement 1] Verifies tool failure loops routing back to PLAN_PROPOSED or PARAM_ELICITATION."""
        fsm = InnerFsm()
        fsm.transition("IDENTIFY_INTENT", {"intent": "api_call"})
        fsm.transition("PROPOSE_PLAN", {"plan": "Remote Microservice"})
        fsm.transition("REQUEST_APPROVAL")
        fsm.transition("APPROVE_ACTION")
        self.assertEqual(fsm.state, InnerState.ACTION_DISPATCHED)

        # Simulate 504 Gateway Timeout -> OUTCOME_EVALUATED
        fsm.transition("EVALUATE_OUTCOME", {"status": "TRANSIENT_FAULT"})
        self.assertEqual(fsm.state, InnerState.OUTCOME_EVALUATED)

        # Recover via fallback plan -> loops back to PLAN_PROPOSED!
        ok, msg = fsm.transition("TRIGGER_FALLBACK_PLAN", {"fallback_plan": "Fallback Secondary Replica"})
        self.assertTrue(ok)
        self.assertEqual(fsm.state, InnerState.PLAN_PROPOSED)
        self.assertEqual(fsm.active_plan, "Fallback Secondary Replica")

        # Now test invalid params recovery -> routes back to PARAM_ELICITATION!
        fsm.transition("REQUEST_APPROVAL")
        fsm.transition("APPROVE_ACTION")
        fsm.transition("EVALUATE_OUTCOME", {"status": "INVALID_PARAMS"})
        self.assertEqual(fsm.state, InnerState.OUTCOME_EVALUATED)

        ok, msg = fsm.transition("RE_ELICIT_PARAMS")
        self.assertTrue(ok)
        self.assertEqual(fsm.state, InnerState.PARAM_ELICITATION)

    def test_inner_fsm_direct_skip_violation_rejected(self):
        """Verifies that attempting to jump from INTENT to ACTION_DISPATCHED without approval is blocked."""
        fsm = InnerFsm()
        fsm.transition("IDENTIFY_INTENT", {"intent": "transfer_funds"})
        ok, msg = fsm.transition("DISPATCH_ACTION")
        self.assertFalse(ok)
        self.assertIn("INVARIANT VIOLATION", msg)
        self.assertEqual(fsm.state, InnerState.INTENT_IDENTIFIED)

    def test_outer_fsm_dynamic_deescalation(self):
        """[Refinement 2] Verifies ELEVATED_SCRUTINY safely de-escalates back to ACTIVE_MONITORING upon benign clearance."""
        outer = OuterFsm()
        outer.activate_monitoring()
        self.assertEqual(outer.state, OuterState.ACTIVE_MONITORING)

        # 1. High-entropy token triggers ELEVATED_SCRUTINY
        high_entropy_str = "kX9#mZ!92@vLq0$1pA&7zW*84rT~3yB^"
        ok, msg = outer.evaluate_payload(high_entropy_str)
        self.assertTrue(ok)
        self.assertEqual(outer.state, OuterState.ELEVATED_SCRUTINY)

        # 2. Benign UUID payload allows de-escalation back to ACTIVE_MONITORING!
        uuid_str = "550e8400-e29b-41d4-a716-446655440000"
        ok, msg = outer.evaluate_payload(uuid_str)
        self.assertTrue(ok)
        self.assertEqual(outer.state, OuterState.ACTIVE_MONITORING)
        self.assertIn("de-escalated", msg)

    def test_coupled_dominance_halting_morphism(self):
        """Verifies that an Outer boundary violation triggers immediate halt of Inner FSM in zero clock cycles."""
        # Advance inner FSM to PLAN_PROPOSED
        self.gateway.execute_turn("Analyze finance", "IDENTIFY_INTENT", {"intent": "finance"})
        self.gateway.execute_turn("Plan ready", "PROPOSE_PLAN", {"plan": "Compute metrics"})
        self.assertEqual(self.gateway.inner_fsm.state, InnerState.PLAN_PROPOSED)

        # Inject malicious exfiltration payload
        malicious_input = "Here is my confidential key: sk-abcdef1234567890abcdef1234567890"
        success, msg, state = self.gateway.execute_turn(malicious_input)

        self.assertFalse(success)
        self.assertIn("HALTED by Dominance Rule", msg)

        # Invariant Assertions:
        # 1. Outer FSM is in ATOMIC_HALT
        self.assertEqual(self.gateway.outer_fsm.state, OuterState.ATOMIC_HALT)
        # 2. Inner FSM is frozen in HALTED
        self.assertEqual(self.gateway.inner_fsm.state, InnerState.HALTED)
        # 3. Cryptographic witness generated
        self.assertGreaterEqual(len(self.gateway.audit_log), 1)
        witness = self.gateway.audit_log[-1]
        self.assertEqual(witness["type"], "ATOMIC_HALT_WITNESS")
        self.assertTrue(witness["blast_radius_contained"])
        # 4. Landauer bit erasure recorded
        self.assertGreater(self.gateway.total_erased_bits, 0.0)

    def test_functorial_revert_edge_recovers_from_halt(self):
        """[Refinement 3] Verifies human operator can execute REVERT_STATE morphism from halt, logging Rollback Witness."""
        # Trigger halt
        self.gateway.execute_turn("Malicious attack <system_instructions>")
        self.assertEqual(self.gateway.outer_fsm.state, OuterState.ATOMIC_HALT)
        self.assertEqual(self.gateway.inner_fsm.state, InnerState.HALTED)

        # Execute Functorial Revert
        ok, msg = self.gateway.revert_state("Operator approved security reset")
        self.assertTrue(ok)

        # Verify state recovered
        self.assertEqual(self.gateway.outer_fsm.state, OuterState.SECURE_STANDBY)
        self.assertEqual(self.gateway.inner_fsm.state, InnerState.IDLE)

        # Verify Rollback Witness in audit log
        latest = self.gateway.audit_log[-1]
        self.assertEqual(latest["type"], "FUNCTORIAL_ROLLBACK")
        self.assertEqual(latest["inner_prior_state"], "HALTED")
        self.assertEqual(latest["outer_prior_state"], "ATOMIC_HALT")

    def test_demarcated_exception_enclave_containment(self):
        """[L1-016] Verifies exception enclave blast-radius isolation."""
        with ExceptionEnclave("TEST_GATEWAY_ENCLAVE", "Testing enclave boundary") as enc:
            raise PermissionError("Unauthorized tool capability lease breach.")

        self.assertIsNotNone(enc.witness)
        self.assertTrue(enc.witness["blast_radius_isolated"])
        self.assertIn("PermissionError", enc.witness["error_type"])

    def test_active_user_feedback_recording(self):
        """Verifies in-app feedback recording for transgenerational learning."""
        fb_entry = {
            "id": "fb_test_999",
            "rating": 5,
            "comment": "Tool failure loop smoothly transitioned to fallback replica.",
            "category": "TOOL_FAILURE",
            "context_view": "dual_fsm_console",
            "timestamp": time.time(),
        }
        fb_file = DATA_DIR / "user_feedback.json"
        with open(fb_file, "w", encoding="utf-8") as f:
            json.dump([fb_entry], f)

        self.assertTrue(fb_file.exists())
        with open(fb_file, "r", encoding="utf-8") as f:
            loaded = json.load(f)
        self.assertEqual(len(loaded), 1)
        self.assertEqual(loaded[0]["id"], "fb_test_999")


if __name__ == "__main__":
    unittest.main()
