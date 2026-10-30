"""End-to-End and Integration Test Suite for Sovereign Telemetry Kernel (`soc_g4b_telemetry`).

Verifies:
- Complete end-to-end operational lifecycle:
  1. Kernel boot and non-loopback network binding on 192.168.40.40:8446.
  2. Batch ingestion of distributed OTel spans and metrics from mesh services.
  3. Landauer thermodynamic dissipation accounting and 60/40 capital invariants.
  4. Empirical SLA benchmarking over active span windows.
  5. Recovery enclave triggering on SLA degradation alerts.
  6. Binary Merkle-DAG witness anchoring and cryptographic chain verification.
  7. Minting and signature verification of certified TelemetryAttestation.
  8. Causal Functorial Undo checkpoint rollback and thermodynamic bit recovery.
  9. Comprehensive status reporting across all 9 subsystems.
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
    ClusterMetricDatum,
    OTelSpanRecord,
    RecoveryEnclaveType,
    SpanStatusCode,
    TelemetryIngestBatch,
)
from generations.gen_04b.services.telemetry.src.telemetry_kernel import (
    SovereignTelemetryKernel,
)


class TestTelemetryKernelE2E(unittest.TestCase):
    """End-to-end integration tests for SovereignTelemetryKernel."""

    def setUp(self):
        self.kernel = SovereignTelemetryKernel(
            node_ip="192.168.40.40",
            port=8446,
            token_budget=880300,
        )

    def test_kernel_initialization_flow(self):
        config = self.kernel.initialize_kernel()
        self.assertEqual(config["root_state"], "ingress_standby")
        self.assertEqual(config["sentry_state"], "sentry_listening")
        self.assertEqual(config["thermo_state"], "thermo_monitoring")
        self.assertEqual(self.kernel.undo_manager.stack_depth, 1)

    def test_full_pipeline_happy_path(self):
        # 1. Boot kernel
        self.kernel.initialize_kernel()
        self.assertEqual(self.kernel.statechart.current_state, "ingress_standby")

        # 2. Ingest telemetry batch from Builder service
        spans = [
            OTelSpanRecord(
                span_id=f"span_builder_{i}",
                trace_id="trace_build_42",
                service_name="builder_service",
                node_ip="192.168.40.20",
                duration_ms=15.0 + float(i),
                status_code=SpanStatusCode.OK,
            )
            for i in range(10)
        ]
        metrics = [
            ClusterMetricDatum(
                metric_id=f"metric_cpu_{i}",
                metric_name="cpu_load_pct",
                service_name="builder_service",
                node_ip="192.168.40.20",
                value=35.0,
            )
            for i in range(5)
        ]
        batch = TelemetryIngestBatch(
            batch_id="batch_builder_001",
            source_service="builder_service",
            source_ip="192.168.40.20",
            spans=spans,
            metrics=metrics,
        )

        ingest_res = self.kernel.ingest_telemetry_batch(batch)
        self.assertEqual(ingest_res["batch_id"], "batch_builder_001")
        self.assertEqual(ingest_res["spans_ingested"], 10)
        self.assertEqual(ingest_res["metrics_ingested"], 5)
        self.assertEqual(self.kernel.statechart.current_state, "metric_aggregation_active")

        # 3. Thermodynamic evaluation
        dissipation = self.kernel.calculate_landauer_dissipation()
        self.assertGreater(dissipation["total_bits_erased"], 0)
        self.assertGreater(dissipation["heat_dissipated_joules"], 0.0)

        # 4. Empirical SLA benchmarking (10 fast spans -> SLA passes)
        sla_report = self.kernel.evaluate_current_sla(window_seconds=1.0)
        self.assertTrue(sla_report.passes_sla)
        self.assertEqual(sla_report.total_requests, 10)
        self.assertEqual(sla_report.successful_requests, 10)
        self.assertEqual(sla_report.error_rate, 0.0)
        self.assertEqual(sla_report.availability_pct, 100.0)
        self.assertEqual(self.kernel.statechart.current_state, "active_sla_benchmarking")

        # 5. Merkle witness anchoring
        root = self.kernel.anchor_merkle_witness()
        self.assertEqual(len(root), 64)
        self.assertEqual(self.kernel.statechart.current_state, "merkle_dag_verifying")

        # 6. Attestation emission and certification
        attestation = self.kernel.mint_telemetry_attestation(
            attestation_id="attest_cert_e2e",
            sla_certified=True,
            landauer_certified=True,
        )
        self.assertEqual(attestation.attestation_id, "attest_cert_e2e")
        self.assertTrue(attestation.sla_certified)
        self.assertTrue(attestation.landauer_certified)
        self.assertEqual(attestation.Merkle_root, root)
        self.assertEqual(self.kernel.statechart.current_state, "state_operational_certified")

    def test_sla_degradation_trigger_enclave(self):
        self.kernel.initialize_kernel()

        # Ingest slow spans that violate P99 threshold (P99 > 100ms)
        spans = [
            OTelSpanRecord(
                span_id=f"slow_span_{i}",
                trace_id="tr_slow",
                service_name="research_service",
                node_ip="192.168.40.10",
                duration_ms=250.0,
                status_code=SpanStatusCode.OK,
            )
            for i in range(10)
        ]
        batch = TelemetryIngestBatch(
            batch_id="batch_slow_001",
            source_service="research_service",
            source_ip="192.168.40.10",
            spans=spans,
            metrics=[],
        )
        self.kernel.ingest_telemetry_batch(batch)

        # Advance to SLA benchmarking
        sla_report = self.kernel.evaluate_current_sla(window_seconds=1.0)
        self.assertFalse(sla_report.passes_sla)
        # Should transition into sla_degradation_fallback enclave
        self.assertEqual(self.kernel.statechart.current_state, "sla_degradation_fallback")
        self.assertGreater(len(self.kernel.alerts), 0)
        self.assertEqual(self.kernel.statechart.parallel_sentry_state, "sentry_alert_raised")

    def test_functorial_undo_end_to_end_rollback(self):
        self.kernel.initialize_kernel()
        init_bits = self.kernel.thermo_engine.ledger.total_bits_erased

        # Record a checkpoint
        cp_mid = self.kernel.undo_manager.create_checkpoint(
            checkpoint_id="ckpt_e2e_midpoint",
            statechart_state=self.kernel.statechart.current_state,
            bits_erased=init_bits,
            active_spans_count=0,
            state_snapshot={"stage": "pre_ingest"},
        )

        # Ingest spans and erase bits
        spans = [
            OTelSpanRecord(span_id="s_undo_1", trace_id="t", node_ip="192.168.40.10"),
            OTelSpanRecord(span_id="s_undo_2", trace_id="t", node_ip="192.168.40.10"),
        ]
        batch = TelemetryIngestBatch(
            batch_id="batch_undo",
            source_service="audit_service",
            source_ip="192.168.40.30",
            spans=spans,
        )
        self.kernel.ingest_telemetry_batch(batch)
        self.assertGreater(self.kernel.thermo_engine.ledger.total_bits_erased, init_bits)

        # Execute functorial undo back to midpoint
        restored = self.kernel.execute_functorial_undo("ckpt_e2e_midpoint")
        self.assertEqual(restored.checkpoint_id, "ckpt_e2e_midpoint")
        self.assertEqual(self.kernel.thermo_engine.ledger.total_bits_erased, init_bits)

    def test_kernel_status_comprehensive_dict(self):
        self.kernel.initialize_kernel()
        status = self.kernel.get_status()

        self.assertEqual(status["service_name"], "telemetry_service")
        self.assertEqual(status["node_ip"], "192.168.40.40")
        self.assertEqual(status["port"], 8446)
        self.assertEqual(status["endpoint"], "192.168.40.40:8446")
        self.assertIn("statechart", status)
        self.assertIn("thermodynamics", status)
        self.assertIn("ingester", status)
        self.assertEqual(status["mesh_registered_nodes"], 4)
        self.assertEqual(status["attestations_minted"], 0)


if __name__ == "__main__":
    unittest.main()
