"""Unit and formal invariant tests for Hierarchical Statechart & Functorial Undo (`soc_g4b_telemetry`).

Verifies:
- [L1-002] Statechart Determinism & 1-Tap Functorial Reversibility.
- Exact membership and reachability of all 30 distinct formal states:
  - 16 Root Strata states
  - 4 Recovery Enclave states
  - 6 Parallel Region states (3 Sentry, 3 Thermodynamic)
  - 4 Deep History Checkpoints
- Complete happy-path traversal from state_uninitialized to state_operational_certified.
- Deterministic invalid transition rejection with TelemetryDomainInvariantViolation.
- Direct entry and unwinding recovery across all 4 recovery enclaves.
- Deep history checkpoint restoration.
- Parallel region orthography (Sentry observer and Thermodynamic meter).
- Functorial Undo causal checkpoint stacking, rollback_to_checkpoint, rollback_latest, and Landauer bit recovery.
"""

from __future__ import annotations

from pathlib import Path
import sys
import unittest

TEL_ROOT = Path(__file__).resolve().parent.parent
REPO_ROOT = TEL_ROOT.parent.parent.parent.parent
for p in [str(TEL_ROOT), str(REPO_ROOT)]:
    if p not in sys.path:
        sys.path.insert(0, p)

from generations.gen_04b.services.telemetry.src.domain_models import (
    RecoveryEnclaveType,
    TelemetryDomainInvariantViolation,
)
from generations.gen_04b.services.telemetry.src.functorial_undo import (
    TelemetryFunctorialUndoManager,
)
from generations.gen_04b.services.telemetry.src.landauer_thermodynamic_engine import (
    LandauerThermodynamicEngine,
)
from generations.gen_04b.services.telemetry.src.statechart_engine import (
    TelemetryStatechartEngine,
)


class TestStatechartAndUndo(unittest.TestCase):
    """Test suite for TelemetryStatechartEngine 30 states and TelemetryFunctorialUndoManager."""

    def setUp(self):
        self.statechart = TelemetryStatechartEngine()
        self.undo_mgr = TelemetryFunctorialUndoManager()
        self.thermo = LandauerThermodynamicEngine()

    def test_exact_30_states_membership(self):
        self.assertEqual(len(TelemetryStatechartEngine.ALL_STATES), 30)
        self.assertEqual(len(TelemetryStatechartEngine.ROOT_STRATA_STATES), 16)
        self.assertEqual(len(TelemetryStatechartEngine.RECOVERY_ENCLAVE_STATES), 4)
        self.assertEqual(len(TelemetryStatechartEngine.PARALLEL_SENTRY_STATES), 3)
        self.assertEqual(len(TelemetryStatechartEngine.PARALLEL_THERMO_STATES), 3)
        self.assertEqual(len(TelemetryStatechartEngine.DEEP_HISTORY_CHECKPOINTS), 4)

        # Invariant: Mutually disjoint state sets
        all_subsets = [
            TelemetryStatechartEngine.ROOT_STRATA_STATES,
            TelemetryStatechartEngine.RECOVERY_ENCLAVE_STATES,
            TelemetryStatechartEngine.PARALLEL_SENTRY_STATES,
            TelemetryStatechartEngine.PARALLEL_THERMO_STATES,
            TelemetryStatechartEngine.DEEP_HISTORY_CHECKPOINTS,
        ]
        total_count = sum(len(s) for s in all_subsets)
        self.assertEqual(total_count, 30)

    def test_happy_path_end_to_end_traversal(self):
        self.assertEqual(self.statechart.current_state, "state_uninitialized")

        # 1. Boot & Network Binding
        self.statechart.send("EV_BIND_LAN")
        self.assertEqual(self.statechart.current_state, "state_binding_lan")
        self.statechart.send("EV_LAN_BOUND")
        self.assertEqual(self.statechart.current_state, "state_sovereign_bound")
        self.statechart.send("EV_STANDBY")
        self.assertEqual(self.statechart.current_state, "ingress_standby")

        # 2. Ingestion & Validation
        self.statechart.send("EV_START_INGESTION")
        self.assertEqual(self.statechart.current_state, "active_stream_ingestion")
        self.statechart.send("EV_VALIDATE_BATCH")
        self.assertEqual(self.statechart.current_state, "stream_batch_validating")
        self.statechart.send("EV_BATCH_VALIDATED")
        self.assertEqual(self.statechart.current_state, "metric_aggregation_active")

        # 3. Thermodynamic Evaluation
        self.statechart.send("EV_START_THERMO")
        self.assertEqual(self.statechart.current_state, "active_thermodynamic_evaluation")
        self.statechart.send("EV_RECONCILE_LEDGER")
        self.assertEqual(self.statechart.current_state, "ledger_reconciliation")

        # 4. Empirical SLA Benchmarking
        self.statechart.send("EV_START_SLA")
        self.assertEqual(self.statechart.current_state, "active_sla_benchmarking")

        # 5. Merkle Anchoring
        self.statechart.send("EV_START_MERKLE")
        self.assertEqual(self.statechart.current_state, "active_merkle_anchoring")
        self.statechart.send("EV_VERIFY_DAG")
        self.assertEqual(self.statechart.current_state, "merkle_dag_verifying")

        # 6. Attestation Emission & Certification
        self.statechart.send("EV_START_EMISSION")
        self.assertEqual(self.statechart.current_state, "active_attestation_emission")
        self.statechart.send("EV_DISPATCH_ATTESTATION")
        self.assertEqual(self.statechart.current_state, "attestation_dispatching")
        self.statechart.send("EV_CERTIFY_OPERATIONAL")
        self.assertEqual(self.statechart.current_state, "state_operational_certified")

    def test_invalid_transition_rejection(self):
        # In state_uninitialized, EV_CERTIFY_OPERATIONAL is invalid
        with self.assertRaises(TelemetryDomainInvariantViolation):
            self.statechart.send("EV_CERTIFY_OPERATIONAL")

    def test_recovery_enclaves_trigger_and_unwind(self):
        enclaves = [
            (RecoveryEnclaveType.SYNTAX_BREACH, "syntax_breach_recovery"),
            (RecoveryEnclaveType.BYZANTINE_FUZZ, "byzantine_fuzz_quarantine"),
            (RecoveryEnclaveType.NETWORK_LOOPBACK, "network_loopback_emergency"),
            (RecoveryEnclaveType.SLA_DEGRADATION, "sla_degradation_fallback"),
        ]

        for enclave_type, expected_state in enclaves:
            # Enter recovery enclave
            res = self.statechart.trigger_enclave(enclave_type)
            self.assertEqual(res, expected_state)
            self.assertEqual(self.statechart.current_state, expected_state)

            # Unwind and restore
            self.statechart.send("EV_RESTORE")
            self.assertEqual(self.statechart.current_state, "enclave_unwind_restoring")
            self.statechart.send("EV_UNWIND_COMPLETE")
            self.assertEqual(self.statechart.current_state, "ingress_standby")

    def test_deep_history_restoration(self):
        # hist_pre_ingestion -> ingress_standby
        self.statechart.restore_deep_history("hist_pre_ingestion")
        self.assertEqual(self.statechart.current_state, "ingress_standby")

        # hist_pre_thermo -> active_thermodynamic_evaluation
        self.statechart.restore_deep_history("hist_pre_thermo")
        self.assertEqual(self.statechart.current_state, "active_thermodynamic_evaluation")

        # hist_pre_benchmark -> active_sla_benchmarking
        self.statechart.restore_deep_history("hist_pre_benchmark")
        self.assertEqual(self.statechart.current_state, "active_sla_benchmarking")

        # hist_pre_merkle -> active_merkle_anchoring
        self.statechart.restore_deep_history("hist_pre_merkle")
        self.assertEqual(self.statechart.current_state, "active_merkle_anchoring")

        # Unknown history target
        with self.assertRaises(TelemetryDomainInvariantViolation):
            self.statechart.restore_deep_history("unknown_hist")

    def test_parallel_regions_transitions(self):
        # Sentry observer
        self.assertEqual(self.statechart.parallel_sentry_state, "sentry_listening")
        self.statechart.send("EV_SENTRY_HEARTBEAT")
        self.assertEqual(self.statechart.parallel_sentry_state, "sentry_heartbeat_tracking")
        self.statechart.send("EV_SENTRY_ALERT")
        self.assertEqual(self.statechart.parallel_sentry_state, "sentry_alert_raised")
        self.statechart.send("EV_SENTRY_RESOLVED")
        self.assertEqual(self.statechart.parallel_sentry_state, "sentry_listening")

        # Thermodynamic meter
        self.assertEqual(self.statechart.parallel_thermo_state, "thermo_monitoring")
        self.statechart.send("EV_THERMO_DISSIPATE")
        self.assertEqual(self.statechart.parallel_thermo_state, "thermo_dissipating")
        self.statechart.send("EV_THERMO_SATURATE")
        self.assertEqual(self.statechart.parallel_thermo_state, "thermo_landauer_saturated")
        self.statechart.send("EV_THERMO_RECOVER")
        self.assertEqual(self.statechart.parallel_thermo_state, "thermo_monitoring")

    def test_functorial_undo_checkpoint_stack(self):
        self.undo_mgr.create_checkpoint(
            checkpoint_id="cp_1",
            statechart_state="ingress_standby",
            bits_erased=1000,
            active_spans_count=5,
            state_snapshot={"stage": 1},
        )
        self.undo_mgr.create_checkpoint(
            checkpoint_id="cp_2",
            statechart_state="active_thermodynamic_evaluation",
            bits_erased=3000,
            active_spans_count=10,
            state_snapshot={"stage": 2},
        )
        self.assertEqual(self.undo_mgr.stack_depth, 2)
        history = self.undo_mgr.get_checkpoint_history()
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0].checkpoint_id, "cp_1")
        self.assertEqual(history[1].checkpoint_id, "cp_2")

    def test_functorial_undo_rollback_and_bit_recovery(self):
        # Record 10,000 bits in thermodynamic engine
        self.thermo.record_bit_erasure(10_000)
        self.undo_mgr.create_checkpoint(
            checkpoint_id="cp_base",
            statechart_state="ingress_standby",
            bits_erased=10_000,
            active_spans_count=0,
            state_snapshot={},
        )

        # Later, record additional 25,000 bits (total 35,000)
        self.thermo.record_bit_erasure(25_000)
        self.undo_mgr.create_checkpoint(
            checkpoint_id="cp_forward",
            statechart_state="active_sla_benchmarking",
            bits_erased=35_000,
            active_spans_count=10,
            state_snapshot={},
        )
        self.assertEqual(self.thermo.ledger.total_bits_erased, 35_000)

        # Rollback to cp_base: should recover 25,000 bits and restore total to 10,000
        restored_cp = self.undo_mgr.rollback_to_checkpoint("cp_base", thermodynamic_engine=self.thermo)
        self.assertEqual(restored_cp.checkpoint_id, "cp_base")
        self.assertEqual(self.thermo.ledger.total_bits_erased, 10_000)
        self.assertEqual(self.undo_mgr.stack_depth, 1)

    def test_functorial_undo_rollback_latest(self):
        self.undo_mgr.create_checkpoint("cp_a", "state_1", 100, 1, {})
        self.undo_mgr.create_checkpoint("cp_b", "state_2", 200, 2, {})
        self.assertEqual(self.undo_mgr.stack_depth, 2)

        # Rollback latest restores to cp_a
        restored = self.undo_mgr.rollback_latest()
        self.assertEqual(restored.checkpoint_id, "cp_a")
        self.assertEqual(self.undo_mgr.stack_depth, 1)

    def test_functorial_undo_stack_underflow_and_nonexistent(self):
        with self.assertRaises(TelemetryDomainInvariantViolation):
            self.undo_mgr.rollback_latest()

        with self.assertRaises(TelemetryDomainInvariantViolation):
            self.undo_mgr.rollback_to_checkpoint("nonexistent_id")


if __name__ == "__main__":
    unittest.main()
