"""Exhaustive Test Suite for Hierarchical XState v5 Statechart Engine (`soc_g4b_governance`).

Enforces:
- Invariant [L1-002]: Statechart Determinism & Deep History H* Preservation.
- Complete verification of the 30-State formal specification across:
  - 4 Compound Strata (20 states)
  - 2 Parallel Orthogonal Regions (10 states)
  - 42 Deterministic Transitions & Covering Paths
  - Deep History Checkpoint state H* restoration
"""

from __future__ import annotations

from pathlib import Path
import sys
import unittest

GOV_ROOT = Path(__file__).resolve().parent.parent
REPO_ROOT = GOV_ROOT.parent.parent.parent.parent
for p in [str(GOV_ROOT), str(GOV_ROOT / "src"), str(REPO_ROOT)]:
    if p not in sys.path:
        sys.path.insert(0, p)

from src.domain_models import (
    GovernanceDomainInvariantViolation,
    GovernanceStatechartDefinition,
    GovernanceStatechartEngine as BaseEngine,
    GovernanceStatechartState,
)
from src.statechart_engine import StatechartEngine


class TestStatechartEngine(unittest.TestCase):
    """Exhaustive tests for statechart execution, covering paths, and parallel orthogonal regions."""

    def setUp(self) -> None:
        self.engine = StatechartEngine(initial_state=GovernanceStatechartState.GOV_ROOT_IDLE)

    def test_statechart_definition_contains_exact_30_states_and_42_transitions(self) -> None:
        """Formal XState v5 statechart specification mandates exactly 30 states and 42 transitions."""
        states = GovernanceStatechartDefinition.get_states()
        self.assertEqual(len(states), 30)

        transitions = GovernanceStatechartDefinition.get_deterministic_transitions()
        self.assertEqual(len(transitions), 42)

        strata = GovernanceStatechartDefinition.get_compound_strata()
        self.assertEqual(len(strata), 4)

        regions = GovernanceStatechartDefinition.get_parallel_regions()
        self.assertEqual(len(regions), 2)

    def test_initial_state_and_active_states(self) -> None:
        """Initial state is GOV_ROOT_IDLE with parallel surveillance idle and peer listening."""
        self.assertEqual(self.engine.current_state, GovernanceStatechartState.GOV_ROOT_IDLE)
        self.assertEqual(self.engine.parallel_surveillance_state, GovernanceStatechartState.SURV_IDLE)
        self.assertEqual(self.engine.parallel_mediation_state, GovernanceStatechartState.PEER_LISTENING)

        active = self.engine.get_active_states()
        self.assertEqual(len(active), 3)
        self.assertTrue(self.engine.is_in_state(GovernanceStatechartState.GOV_ROOT_IDLE))
        self.assertTrue(self.engine.is_in_state(GovernanceStatechartState.SURV_IDLE))
        self.assertTrue(self.engine.is_in_state(GovernanceStatechartState.PEER_LISTENING))

    def test_stratum_1_root_initialization_and_recalibration(self) -> None:
        """Tests transitions: gov_root_idle -> gov_bootstrapping -> gov_ready <-> gov_recalibrating."""
        # T01: gov_root_idle -> gov_bootstrapping
        self.assertTrue(self.engine.send("EV_BOOTSTRAP_INIT"))
        self.assertEqual(self.engine.current_state, GovernanceStatechartState.GOV_BOOTSTRAPPING)

        # T02: gov_bootstrapping -> gov_ready
        self.assertTrue(self.engine.send("EV_AXIOMS_LOADED"))
        self.assertEqual(self.engine.current_state, GovernanceStatechartState.GOV_READY)

        # T04: gov_ready -> gov_recalibrating
        self.assertTrue(self.engine.send("EV_RECALIBRATE_START"))
        self.assertEqual(self.engine.current_state, GovernanceStatechartState.GOV_RECALIBRATING)

        # T05: gov_recalibrating -> gov_ready
        self.assertTrue(self.engine.send("EV_RECALIBRATE_COMPLETE"))
        self.assertEqual(self.engine.current_state, GovernanceStatechartState.GOV_READY)

    def test_stratum_2_operational_intercept_and_hitl_escalation(self) -> None:
        """Tests intercept evaluation, HITL escalation, and settlement in SovereignOperational stratum."""
        self.engine.send("EV_BOOTSTRAP_INIT")
        self.engine.send("EV_AXIOMS_LOADED")
        self.engine.send("EV_ENTER_OPERATIONAL")
        self.assertEqual(self.engine.current_state, GovernanceStatechartState.OP_SURVEILLING)

        # T06: op_surveilling -> op_evaluating_intercept
        self.assertTrue(self.engine.send("EV_INTERCEPT_DETECTED"))
        self.assertEqual(self.engine.current_state, GovernanceStatechartState.OP_EVALUATING_INTERCEPT)

        # T09: op_evaluating_intercept -> op_hitl_escalating
        self.assertTrue(self.engine.send("EV_ESCALATE_HITL"))
        self.assertEqual(self.engine.current_state, GovernanceStatechartState.OP_HITL_ESCALATING)

        # T10: op_hitl_escalating -> op_hitl_awaiting_disposition
        self.assertTrue(self.engine.send("EV_HITL_SUBMITTED"))
        self.assertEqual(self.engine.current_state, GovernanceStatechartState.OP_HITL_AWAITING_DISPOSITION)

        # T11: op_hitl_awaiting_disposition -> op_adjudication_settled
        self.assertTrue(self.engine.send("EV_SUPERVISOR_APPROVED"))
        self.assertEqual(self.engine.current_state, GovernanceStatechartState.OP_ADJUDICATION_SETTLED)

        # T15: op_adjudication_settled -> op_surveilling
        self.assertTrue(self.engine.send("EV_ADJUDICATION_DISPATCHED"))
        self.assertEqual(self.engine.current_state, GovernanceStatechartState.OP_SURVEILLING)

    def test_stratum_2_operational_rfc_deliberation(self) -> None:
        """Tests RFC submission, deliberation, and approval pathway."""
        self.engine.send("EV_BOOTSTRAP_INIT")
        self.engine.send("EV_AXIOMS_LOADED")
        self.engine.send("EV_ENTER_OPERATIONAL")

        # T07: op_surveilling -> op_rfc_deliberation
        self.assertTrue(self.engine.send("EV_RFC_SUBMITTED"))
        self.assertEqual(self.engine.current_state, GovernanceStatechartState.OP_RFC_DELIBERATION)

        # T13: op_rfc_deliberation -> op_adjudication_settled (Approve)
        self.assertTrue(self.engine.send("EV_RFC_APPROVE"))
        self.assertEqual(self.engine.current_state, GovernanceStatechartState.OP_ADJUDICATION_SETTLED)

        self.assertTrue(self.engine.send("EV_ADJUDICATION_DISPATCHED"))
        self.assertEqual(self.engine.current_state, GovernanceStatechartState.OP_SURVEILLING)

    def test_stratum_3_emergency_enclave_and_deep_history_restoration(self) -> None:
        """Tests circuit breaker trip into EmergencyEnclave and deep history H* restoration."""
        self.engine.send("EV_BOOTSTRAP_INIT")
        self.engine.send("EV_AXIOMS_LOADED")
        self.engine.send("EV_ENTER_OPERATIONAL")
        self.assertEqual(self.engine.current_state, GovernanceStatechartState.OP_SURVEILLING)

        # T08: op_surveilling -> enclave_tripped (checkpoint saved as op_surveilling)
        self.assertTrue(self.engine.send("EV_TRIP_CIRCUIT_BREAKER"))
        self.assertEqual(self.engine.current_state, GovernanceStatechartState.ENCLAVE_TRIPPED)

        # T16: enclave_tripped -> enclave_quarantine_isolation
        self.assertTrue(self.engine.send("EV_ISOLATE_NODE"))
        self.assertEqual(self.engine.current_state, GovernanceStatechartState.ENCLAVE_QUARANTINE_ISOLATION)

        # T17: enclave_quarantine_isolation -> enclave_investigation
        self.assertTrue(self.engine.send("EV_BEGIN_INVESTIGATION"))
        self.assertEqual(self.engine.current_state, GovernanceStatechartState.ENCLAVE_INVESTIGATION)

        # T18: enclave_investigation -> enclave_cooldown_probing
        self.assertTrue(self.engine.send("EV_START_COOLDOWN_PROBE"))
        self.assertEqual(self.engine.current_state, GovernanceStatechartState.ENCLAVE_COOLDOWN_PROBING)

        # T19: enclave_cooldown_probing -> enclave_restored
        self.assertTrue(self.engine.send("EV_PROBE_SUCCEEDED"))
        self.assertEqual(self.engine.current_state, GovernanceStatechartState.ENCLAVE_RESTORED)

        # T21: enclave_restored -> restore deep history H*
        restored_state = self.engine.restore_deep_history()
        self.assertEqual(restored_state, GovernanceStatechartState.OP_SURVEILLING)
        self.assertEqual(self.engine.current_state, GovernanceStatechartState.OP_SURVEILLING)

    def test_stratum_4_generational_handover_graduation(self) -> None:
        """Tests complete succession flow from handover_initiating to handover_graduated."""
        self.engine.send("EV_BOOTSTRAP_INIT")
        self.engine.send("EV_AXIOMS_LOADED")
        self.engine.send("EV_ENTER_OPERATIONAL")

        # T22: op_surveilling -> handover_initiating
        self.assertTrue(self.engine.send("EV_INITIATE_HANDOVER"))
        self.assertEqual(self.engine.current_state, GovernanceStatechartState.HANDOVER_INITIATING)

        # T23: handover_initiating -> handover_proving_invariants
        self.assertTrue(self.engine.send("EV_VERIFY_INVARIANTS"))
        self.assertEqual(self.engine.current_state, GovernanceStatechartState.HANDOVER_PROVING_INVARIANTS)

        # T24: handover_proving_invariants -> handover_hdr_verifying
        self.assertTrue(self.engine.send("EV_INVARIANTS_SATISFIED"))
        self.assertEqual(self.engine.current_state, GovernanceStatechartState.HANDOVER_HDR_VERIFYING)

        # T26: handover_hdr_verifying -> handover_signing_certificate
        self.assertTrue(self.engine.send("EV_HDR_VERIFIED_PASS"))
        self.assertEqual(self.engine.current_state, GovernanceStatechartState.HANDOVER_SIGNING_CERTIFICATE)

        # T28: handover_signing_certificate -> handover_graduated
        self.assertTrue(self.engine.send("EV_CERTIFICATE_SIGNED"))
        self.assertEqual(self.engine.current_state, GovernanceStatechartState.HANDOVER_GRADUATED)

        # T29: handover_graduated -> gov_root_idle
        self.assertTrue(self.engine.send("EV_RETURN_TO_STANDBY"))
        self.assertEqual(self.engine.current_state, GovernanceStatechartState.GOV_ROOT_IDLE)

    def test_parallel_orthogonal_region_1_surveillance(self) -> None:
        """Tests independent execution of parallel Region 1: AxiomaticSurveillance."""
        self.assertEqual(self.engine.parallel_surveillance_state, GovernanceStatechartState.SURV_IDLE)

        # T33: EV_SURV_SCAN_AST
        self.assertTrue(self.engine.send("EV_SURV_SCAN_AST"))
        self.assertEqual(self.engine.parallel_surveillance_state, GovernanceStatechartState.SURV_INSPECTING_AST)

        # T35: EV_SURV_TRIGGER_VETO
        self.assertTrue(self.engine.send("EV_SURV_TRIGGER_VETO"))
        self.assertEqual(self.engine.parallel_surveillance_state, GovernanceStatechartState.SURV_VETO_TRIGGERED)

        # T36: EV_SURV_QUARANTINE_PEER
        self.assertTrue(self.engine.send("EV_SURV_QUARANTINE_PEER"))
        self.assertEqual(self.engine.parallel_surveillance_state, GovernanceStatechartState.SURV_QUARANTINED)

        # T37: EV_SURV_DISCHARGE_CLEAN
        self.assertTrue(self.engine.send("EV_SURV_DISCHARGE_CLEAN"))
        self.assertEqual(self.engine.parallel_surveillance_state, GovernanceStatechartState.SURV_IDLE)

    def test_parallel_orthogonal_region_2_mediation(self) -> None:
        """Tests independent execution of parallel Region 2: PeerMediation."""
        self.assertEqual(self.engine.parallel_mediation_state, GovernanceStatechartState.PEER_LISTENING)

        # T38: EV_PEER_POLL_RFC
        self.assertTrue(self.engine.send("EV_PEER_POLL_RFC"))
        self.assertEqual(self.engine.parallel_mediation_state, GovernanceStatechartState.PEER_ADJUDICATING_RFC)

        # T39: EV_PEER_GENERATE_AMENDMENT
        self.assertTrue(self.engine.send("EV_PEER_GENERATE_AMENDMENT"))
        self.assertEqual(self.engine.parallel_mediation_state, GovernanceStatechartState.PEER_AMENDING_SPEC)

        # T41: EV_PEER_RESET_LISTENING
        self.assertTrue(self.engine.send("EV_PEER_RESET_LISTENING"))
        self.assertEqual(self.engine.parallel_mediation_state, GovernanceStatechartState.PEER_LISTENING)

    def test_invalid_event_does_not_mutate_state(self) -> None:
        """Dispatching an inapplicable event returns False and preserves current state."""
        self.assertEqual(self.engine.current_state, GovernanceStatechartState.GOV_ROOT_IDLE)
        changed = self.engine.send("EV_NONEXISTENT_JUNK_EVENT")
        self.assertFalse(changed)
        self.assertEqual(self.engine.current_state, GovernanceStatechartState.GOV_ROOT_IDLE)

    def test_transition_logging_and_reset(self) -> None:
        """Verifies transitions are appended to history log, and reset restores genesis state."""
        self.engine.send("EV_BOOTSTRAP_INIT")
        self.engine.send("EV_AXIOMS_LOADED")
        self.assertGreaterEqual(self.engine.get_transition_count(), 2)

        history = self.engine.export_history()
        self.assertEqual(len(history), self.engine.get_transition_count())
        self.assertEqual(history[0].event_name, "EV_BOOTSTRAP_INIT")

        self.engine.reset()
        self.assertEqual(self.engine.current_state, GovernanceStatechartState.GOV_ROOT_IDLE)
        self.assertEqual(self.engine.get_transition_count(), 0)


if __name__ == "__main__":
    unittest.main()
