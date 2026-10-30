"""Exhaustive Test Suite for Functorial Undo & Categorical Adjoint State Reversal (`soc_g4b_governance`).

Enforces:
- Invariant [L1-002]: Statechart Determinism & 1-Tap Functorial Reversibility.
- Strict categorical adjoint state reversal: S_{t-1} = f^{-1}(S_t).
- Causal monotonicity preservation, deep-copy immutability, and bounded memory leases.
"""

from __future__ import annotations

import copy
from pathlib import Path
import sys
import unittest

GOV_ROOT = Path(__file__).resolve().parent.parent
REPO_ROOT = GOV_ROOT.parent.parent.parent.parent
for p in [str(GOV_ROOT), str(GOV_ROOT / "src"), str(REPO_ROOT)]:
    if p not in sys.path:
        sys.path.insert(0, p)

from src.domain_models import (
    CircuitBreakerState,
    GovernanceDomainInvariantViolation,
    GovernanceKernelState,
)
from src.functorial_undo import FunctorialUndoEngine


class TestFunctorialUndo(unittest.TestCase):
    """Exhaustive tests for functorial state snapshots, rollback adjoints, and stack invariants."""

    def setUp(self) -> None:
        self.undo_engine = FunctorialUndoEngine(max_depth=5)
        self.state_s0 = GovernanceKernelState(
            kernel_id="soc_g4b_governance",
            service_endpoint="192.168.40.50:8448",
            circuit_breaker=CircuitBreakerState.CLOSED_NORMAL,
            active_negative_axioms_count=10,
            total_violations_trapped=0,
            pending_hitl_count=0,
            heuristic_debt_ratio=0.04,
            quarantined_nodes=[],
            is_succession_ready=False,
            governance_chain_head="0" * 64,
        )

    def test_initial_state_empty(self) -> None:
        """New undo engine has 0 depth, can_undo() == False, peek_current() == None."""
        self.assertEqual(self.undo_engine.history_depth(), 0)
        self.assertFalse(self.undo_engine.can_undo())
        self.assertIsNone(self.undo_engine.peek_current())
        self.assertIsNone(self.undo_engine.undo())

    def test_single_state_cannot_undo(self) -> None:
        """With only 1 snapshot on stack, can_undo() is False and undo() returns None."""
        self.undo_engine.push_state(self.state_s0)
        self.assertEqual(self.undo_engine.history_depth(), 1)
        self.assertFalse(self.undo_engine.can_undo())
        self.assertIsNone(self.undo_engine.undo())

    def test_push_and_peek_current(self) -> None:
        """Pushing state returns SHA-256 hash and peek_current returns an identical snapshot."""
        h0 = self.undo_engine.push_state(self.state_s0)
        self.assertEqual(len(h0), 64)

        peeked = self.undo_engine.peek_current()
        self.assertIsNotNone(peeked)
        self.assertEqual(peeked.compute_hash(), h0)
        self.assertEqual(peeked.active_negative_axioms_count, 10)

    def test_deep_copy_isolation_on_push(self) -> None:
        """Mutating original state object does not alter the stored snapshot in the stack."""
        state = copy.deepcopy(self.state_s0)
        h_orig = self.undo_engine.push_state(state)

        # Mutate local state
        state.active_negative_axioms_count = 999
        state.total_violations_trapped = 555

        peeked = self.undo_engine.peek_current()
        self.assertIsNotNone(peeked)
        self.assertEqual(peeked.active_negative_axioms_count, 10)
        self.assertEqual(peeked.total_violations_trapped, 0)
        self.assertEqual(peeked.compute_hash(), h_orig)

    def test_sequential_push_and_adjoint_rollback(self) -> None:
        """Pushes S0 -> S1 -> S2, verifies rollbacks S2 -> S1 -> S0."""
        # Push S0
        h0 = self.undo_engine.push_state(self.state_s0)

        # Push S1 (violation trapped)
        s1 = copy.deepcopy(self.state_s0)
        s1.total_violations_trapped = 1
        s1.governance_chain_head = "1" * 64
        h1 = self.undo_engine.push_state(s1)

        # Push S2 (circuit breaker tripped)
        s2 = copy.deepcopy(s1)
        s2.circuit_breaker = CircuitBreakerState.TRIPPED_OPEN
        s2.quarantined_nodes = ["192.168.40.20:8442"]
        s2.governance_chain_head = "2" * 64
        h2 = self.undo_engine.push_state(s2)

        self.assertEqual(self.undo_engine.history_depth(), 3)
        self.assertTrue(self.undo_engine.can_undo())
        self.assertEqual(self.undo_engine.get_stack_hashes(), [h0, h1, h2])

        # Rollback 1: S2 -> S1
        restored_1 = self.undo_engine.undo()
        self.assertIsNotNone(restored_1)
        self.assertEqual(restored_1.compute_hash(), h1)
        self.assertEqual(restored_1.total_violations_trapped, 1)
        self.assertEqual(restored_1.circuit_breaker, CircuitBreakerState.CLOSED_NORMAL)
        self.assertEqual(self.undo_engine.history_depth(), 2)

        # Rollback 2: S1 -> S0
        restored_0 = self.undo_engine.undo()
        self.assertIsNotNone(restored_0)
        self.assertEqual(restored_0.compute_hash(), h0)
        self.assertEqual(restored_0.total_violations_trapped, 0)
        self.assertEqual(self.undo_engine.history_depth(), 1)

        # Rollback 3: S0 has no previous state -> returns None
        self.assertFalse(self.undo_engine.can_undo())
        self.assertIsNone(self.undo_engine.undo())

    def test_bounded_memory_capacity_lease(self) -> None:
        """Exceeding max_depth drops the oldest state to respect thermodynamic capacity."""
        engine = FunctorialUndoEngine(max_depth=3)
        hashes = []
        for i in range(5):
            st = copy.deepcopy(self.state_s0)
            st.total_violations_trapped = i
            st.governance_chain_head = f"{i}" * 64
            h = engine.push_state(st)
            hashes.append(h)

        self.assertEqual(engine.history_depth(), 3)
        # Oldest two (i=0, i=1) dropped; remaining should be i=2, 3, 4
        self.assertEqual(engine.get_stack_hashes(), hashes[2:])

    def test_clear_stack(self) -> None:
        """Clearing the stack resets depth to 0."""
        self.undo_engine.push_state(self.state_s0)
        self.undo_engine.push_state(self.state_s0)
        self.assertEqual(self.undo_engine.history_depth(), 2)

        self.undo_engine.clear()
        self.assertEqual(self.undo_engine.history_depth(), 0)
        self.assertFalse(self.undo_engine.can_undo())

    def test_push_invalid_state_raises_violation(self) -> None:
        """Pushing a state with violated domain invariants raises GovernanceDomainInvariantViolation."""
        invalid_state = copy.deepcopy(self.state_s0)
        invalid_state.heuristic_debt_ratio = 1.5  # Out of [0.0, 1.0] bound
        with self.assertRaises(GovernanceDomainInvariantViolation):
            self.undo_engine.push_state(invalid_state)


if __name__ == "__main__":
    unittest.main()
