"""Unit & Adversarial Invariant Test Suite for SMT Formal Model Checker (`[L1-G3B-011]`).

Validates:
1. Proves valid contract morphism composition entails UNSAT (Valid: True).
2. Detects broken pre-conditions (refuting morphism).
3. Detects broken post-conditions (refuting morphism).
4. Proves deadlock-free statechart transitions and reachability.
5. Detects statechart deadlocks (unreachable sink states).
6. Comprehensive candidate verification with statechart integration.
7. UNSAT core extraction verification.
8. SAT counterexample modeling on invalid entailments.
9. Tautological and constant implications handling.
10. Native SMT solver pure Python execution and boolean normalization.
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
    CodeLeafCandidate,
    MorphismCheckStatus,
    SMTModelCheckResult,
)
from src.smt_model_checker import NativeSMTProver_v4b, SMTModelChecker


class TestSMTModelChecker(unittest.TestCase):
    """Exhaustive unit and adversarial test suite for SMT model checking and morphism proofs."""

    def setUp(self) -> None:
        self.checker = SMTModelChecker()
        self.prover = NativeSMTProver_v4b()

    # 1. Proves Valid Contract Morphism Composition Entails UNSAT
    def test_valid_contract_morphism_entails_unsat(self) -> None:
        # Pre_parent (x and y) |= Pre_child (x)  [Contravariance: stronger pre to weaker pre]
        # Post_child (a and b) |= Post_parent (a) [Covariance: stronger post to weaker post]
        res = self.checker.verify_contract_morphism(
            parent_pre="x and y",
            parent_post="a",
            child_pre="x",
            child_post="a and b",
            leaf_id="leaf_morphism_valid",
        )
        self.assertEqual(res.morphism_status, MorphismCheckStatus.PROVEN_VALID)
        self.assertTrue(res.precondition_entailment_valid)
        self.assertTrue(res.postcondition_consequence_valid)
        self.assertTrue(res.is_deadlock_free)
        self.assertIsNotNone(res.unsat_core)
        self.assertIn("unsat_core", res.unsat_core)
        self.assertEqual(len(res.counter_example), 0)

    # 2. Detects Broken Precondition Refuting Morphism
    def test_detect_broken_precondition_refuting_morphism(self) -> None:
        # Pre_parent (x) does NOT entail Pre_child (x and y)
        res = self.checker.verify_contract_morphism(
            parent_pre="x",
            parent_post="a",
            child_pre="x and y",
            child_post="a",
            leaf_id="leaf_broken_pre",
        )
        self.assertEqual(res.morphism_status, MorphismCheckStatus.COUNTER_EXAMPLE_FOUND)
        self.assertFalse(res.precondition_entailment_valid)
        self.assertIn("y", res.counter_example)
        self.assertFalse(res.counter_example["y"])

    # 3. Detects Broken Postcondition Refuting Morphism
    def test_detect_broken_postcondition_refuting_morphism(self) -> None:
        # Post_child (a) does NOT entail Post_parent (a and b)
        res = self.checker.verify_contract_morphism(
            parent_pre="x",
            parent_post="a and b",
            child_pre="x",
            child_post="a",
            leaf_id="leaf_broken_post",
        )
        self.assertEqual(res.morphism_status, MorphismCheckStatus.COUNTER_EXAMPLE_FOUND)
        self.assertTrue(res.precondition_entailment_valid)
        self.assertFalse(res.postcondition_consequence_valid)
        self.assertIn("b", res.counter_example)
        self.assertFalse(res.counter_example["b"])

    # 4. Proves Deadlock-Free Statechart Reachability
    def test_deadlock_free_statechart_reachability(self) -> None:
        states = ["init", "parsing", "verifying", "sealed"]
        transitions = [
            ("init", "ev_start", "parsing"),
            ("parsing", "ev_parsed", "verifying"),
            ("verifying", "ev_verified", "sealed"),
            ("verifying", "ev_retry", "parsing"),
        ]
        terminal_states = ["sealed"]
        is_free, err = self.checker.verify_statechart_deadlock_freedom(
            states=states,
            transitions=transitions,
            terminal_states=terminal_states,
            initial_state="init",
        )
        self.assertTrue(is_free)
        self.assertIsNone(err)

    # 5. Detects Statechart Deadlocks (Absorbing Sink State)
    def test_detect_statechart_deadlock_absorbing_sink(self) -> None:
        states = ["init", "parsing", "stuck_loop", "sealed"]
        transitions = [
            ("init", "ev_start", "parsing"),
            ("parsing", "ev_fail", "stuck_loop"),
            ("stuck_loop", "ev_spin", "stuck_loop"),  # absorbing, cannot reach 'sealed'
            ("parsing", "ev_ok", "sealed"),
        ]
        terminal_states = ["sealed"]
        is_free, err = self.checker.verify_statechart_deadlock_freedom(
            states=states,
            transitions=transitions,
            terminal_states=terminal_states,
            initial_state="init",
        )
        self.assertFalse(is_free)
        self.assertIsNotNone(err)
        self.assertIn("stuck_loop", err)

    # 6. Comprehensive Candidate Check with Statechart Integration
    def test_candidate_check_with_deadlock_detection(self) -> None:
        candidate = CodeLeafCandidate(
            leaf_id="leaf_fsm_candidate",
            symbol_urn="urn:meta_axioma:leaf:fsm",
            source_code="def run_fsm(): pass",
            parent_contract_pre="x",
            parent_contract_post="y",
            child_contract_pre="x",
            child_contract_post="y",
        )
        deadlocked_fsm = {
            "states": ["s1", "s2_sink"],
            "transitions": [("s1", "e", "s2_sink"), ("s2_sink", "e", "s2_sink")],
            "terminal_states": ["s_terminal_unreachable"],
        }
        res = self.checker.check_candidate(candidate, statechart_graph=deadlocked_fsm)
        self.assertEqual(res.morphism_status, MorphismCheckStatus.DEADLOCK_DETECTED)
        self.assertFalse(res.is_deadlock_free)

    # 7. Verifies UNSAT Core Extraction
    def test_unsat_core_extraction(self) -> None:
        is_valid, cex, unsat_core = self.prover.check_implication("p and q", "p")
        self.assertTrue(is_valid)
        self.assertIsNone(cex)
        self.assertIsNotNone(unsat_core)
        self.assertIn("unsat_core", unsat_core)
        self.assertIn("p", unsat_core)

    # 8. Verifies SAT Counterexample Modeling
    def test_sat_counterexample_modeling(self) -> None:
        # a implies (a and b) is falsified by a=True, b=False
        is_valid, cex, unsat_core = self.prover.check_implication("a", "a and b")
        self.assertFalse(is_valid)
        self.assertIsNone(unsat_core)
        self.assertIsNotNone(cex)
        self.assertTrue(cex.get("a"))
        self.assertFalse(cex.get("b"))

    # 9. Tautological and Constant Implications
    def test_tautological_and_constant_implications(self) -> None:
        # True implies True
        valid, cex, core = self.prover.check_implication("True", "True")
        self.assertTrue(valid)

        # None/empty implies True
        valid, cex, core = self.prover.check_implication("", "True")
        self.assertTrue(valid)

        # False implies False
        valid, cex, core = self.prover.check_implication("False", "False")
        self.assertTrue(valid)

    # 10. Native SMT Solver Pure Python Execution & Expression Normalization
    def test_native_smt_prover_normalization_and_pure_execution(self) -> None:
        # Test C-style &&, ||, ! operators
        valid, cex, core = self.prover.check_implication("x && y", "x || z")
        self.assertTrue(valid)

        # Test uppercase AND, OR, NOT
        valid, cex, core = self.prover.check_implication("X AND NOT Y", "X")
        self.assertTrue(valid)

        # Test implication operator ->
        norm = self.prover._normalize_expr("a -> b")
        self.assertEqual(" ".join(norm.split()), "a <= b")


if __name__ == "__main__":
    unittest.main()
