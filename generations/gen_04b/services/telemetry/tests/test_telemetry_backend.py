"""Unit and Integration Test Suite for Sovereign Telemetry Backend Modules (`soc_g4b_telemetry`)."""

from __future__ import annotations

import time
import unittest

from generations.gen_04b.protocols.rfc_protocol import (
    BottleneckType,
    CounterProof,
    SpecAdjustmentRequest,
)
from generations.gen_04b.services.telemetry.src.domain_models import (
    assert_non_loopback,
    ByzantineTelemetryVector,
    ByzantineVectorType,
    ClusterMetricDatum,
    EmpiricalSLAReport,
    FunctorialUndoCheckpoint,
    LandauerDissipationLedger,
    MerkleTreeNode,
    OTelSpanRecord,
    RecoveryEnclaveType,
    SpanStatusCode,
    TelemetryAttestation,
    TelemetryDomainInvariantViolation,
    TelemetryIngestBatch,
    TelemetrySeverityLevel,
    TelemetryTopologyState,
)
from generations.gen_04b.services.telemetry.src.otel_span_ingester import OTelSpanIngester
from generations.gen_04b.services.telemetry.src.landauer_thermodynamic_engine import LandauerThermodynamicEngine
from generations.gen_04b.services.telemetry.src.empirical_sla_evaluator import EmpiricalSLABenchmarker
from generations.gen_04b.services.telemetry.src.mesh_multi_source_aggregator import MeshMultiSourceAggregator
from generations.gen_04b.services.telemetry.src.merkle_dag_witness_engine import TelemetryMerkleWitnessEngine
from generations.gen_04b.services.telemetry.src.statechart_engine import TelemetryStatechartEngine
from generations.gen_04b.services.telemetry.src.functorial_undo import TelemetryFunctorialUndoManager
from generations.gen_04b.services.telemetry.src.service_topology import (
    NetworkPartitionError,
    PartitionPolicy,
    TelemetryServiceTopology,
)
from generations.gen_04b.services.telemetry.src.rfc_protocol_mediator import TelemetryRFCMediator
from generations.gen_04b.services.telemetry.src.telemetry_kernel import SovereignTelemetryKernel


class TestTelemetryBackendModules(unittest.TestCase):
    """Rigorous tests covering all 10 core backend modules."""

    def test_otel_span_ingester(self) -> None:
        ingester = OTelSpanIngester(max_spans=100, max_metrics=100)
        span = OTelSpanRecord(
            span_id="span_01",
            trace_id="tr_01",
            service_name="test_svc",
            node_ip="192.168.40.10",
        )
        ingester.ingest_span(span)
        self.assertEqual(len(ingester.get_active_spans()), 1)
        self.assertEqual(ingester.get_span_by_id("span_01"), span)

        # Loopback rejection
        bad_span = OTelSpanRecord(
            span_id="span_bad",
            trace_id="tr_02",
            node_ip="127.0.0.1",
        )
        with self.assertRaises(TelemetryDomainInvariantViolation):
            ingester.ingest_span(bad_span)

        # Metric ingestion
        metric = ClusterMetricDatum(
            metric_id="m_01",
            metric_name="cpu",
            service_name="test_svc",
            node_ip="192.168.40.20",
            value=22.5,
        )
        ingester.ingest_metric(metric)
        self.assertEqual(len(ingester.get_metrics_window(window_sec=10.0)), 1)
        ingester.clear()
        self.assertEqual(len(ingester.get_active_spans()), 0)

    def test_landauer_thermodynamic_engine(self) -> None:
        engine = LandauerThermodynamicEngine(token_lease_budget=880300)
        self.assertEqual(engine.ledger.exploratory_capital, 528180)
        self.assertEqual(engine.ledger.protected_capital, 352120)

        # Bit erasure
        q = engine.record_bit_erasure(1000, operation="erasure_test")
        self.assertGreater(q, 0.0)
        self.assertEqual(engine.ledger.total_bits_erased, 1000)

        # Bit recovery
        engine.record_bit_recovery(400)
        self.assertEqual(engine.ledger.total_bits_erased, 600)

        # Spend tokens within bounds
        engine.spend_tokens(10000, is_protected=False)
        engine.spend_tokens(5000, is_protected=True)
        self.assertTrue(engine.verify_capital_invariants())
        self.assertTrue(engine.certify_ledger())

    def test_empirical_sla_evaluator(self) -> None:
        evaluator = EmpiricalSLABenchmarker(p99_threshold_ms=50.0)
        spans = [
            OTelSpanRecord(
                span_id=f"sp_{i}",
                trace_id="tr_sla",
                service_name="test_svc",
                node_ip="192.168.40.30",
                duration_ms=float(i * 2),
                status_code=SpanStatusCode.OK,
            )
            for i in range(20)
        ]
        report = evaluator.evaluate_spans(spans, window_seconds=1.0)
        self.assertEqual(report.total_requests, 20)
        self.assertEqual(report.successful_requests, 20)
        self.assertEqual(report.error_rate, 0.0)
        self.assertTrue(report.passes_sla)

        # Percentile computation edge cases
        self.assertEqual(evaluator.compute_percentile([], 50.0), 0.0)
        self.assertEqual(evaluator.compute_percentile([42.0], 90.0), 42.0)

    def test_mesh_multi_source_aggregator(self) -> None:
        aggregator = MeshMultiSourceAggregator()
        registered = aggregator.get_registered_nodes()
        self.assertIn("research_service", registered)
        self.assertIn("builder_service", registered)
        self.assertIn("audit_service", registered)
        self.assertIn("telemetry_service", registered)

        aggregator.record_node_heartbeat("research_service", "root_res_01", bits_erased=500)
        dissipation = aggregator.aggregate_mesh_dissipation()
        self.assertGreaterEqual(dissipation["total_mesh_bits_erased"], 500)

    def test_merkle_dag_witness_engine(self) -> None:
        engine = TelemetryMerkleWitnessEngine()
        self.assertEqual(engine.compute_root(), engine.GENESIS_ROOT)

        h1 = engine.record_event("EVENT_A", {"key": "val1"})
        h2 = engine.record_event("EVENT_B", {"key": "val2"})
        h3 = engine.record_event("EVENT_C", {"key": "val3"})

        root = engine.compute_root()
        self.assertNotEqual(root, engine.GENESIS_ROOT)
        self.assertTrue(engine.verify_chain_integrity())

        # Inclusion proof
        proof = engine.generate_inclusion_proof(h1)
        self.assertTrue(TelemetryMerkleWitnessEngine.verify_inclusion_proof(h1, proof, root))
        self.assertFalse(TelemetryMerkleWitnessEngine.verify_inclusion_proof(h1, proof, "fake_root"))

        # Mint attestation
        attest = engine.mint_attestation(
            attestation_id="attest_test",
            service_name="telemetry_service",
            node_ip="192.168.40.40",
            port=8446,
            sla_certified=True,
            landauer_certified=True,
        )
        self.assertEqual(attest.Merkle_root, root)

    def test_statechart_engine_30_states(self) -> None:
        sc = TelemetryStatechartEngine()
        self.assertEqual(len(sc.ALL_STATES), 30)
        self.assertEqual(sc.current_state, "state_uninitialized")

        # Standard forward transitions
        sc.send("EV_BIND_LAN")
        self.assertEqual(sc.current_state, "state_binding_lan")
        sc.send("EV_LAN_BOUND")
        self.assertEqual(sc.current_state, "state_sovereign_bound")
        sc.send("EV_STANDBY")
        self.assertEqual(sc.current_state, "ingress_standby")

        # Deep history restore
        sc.restore_deep_history("hist_pre_benchmark")
        self.assertEqual(sc.current_state, "active_sla_benchmarking")

        # Recovery enclave trigger
        sc.trigger_enclave(RecoveryEnclaveType.SYNTAX_BREACH)
        self.assertEqual(sc.current_state, "syntax_breach_recovery")
        sc.send("EV_RESTORE")
        self.assertEqual(sc.current_state, "enclave_unwind_restoring")
        sc.send("EV_UNWIND_COMPLETE")
        self.assertEqual(sc.current_state, "ingress_standby")

    def test_functorial_undo(self) -> None:
        undo = TelemetryFunctorialUndoManager()
        engine = LandauerThermodynamicEngine()
        engine.record_bit_erasure(1000)

        cp1 = undo.create_checkpoint("cp1", "ingress_standby", 1000, 5, {})
        engine.record_bit_erasure(5000)
        self.assertEqual(engine.ledger.total_bits_erased, 6000)

        cp_restored = undo.rollback_to_checkpoint("cp1", thermodynamic_engine=engine)
        self.assertEqual(cp_restored.checkpoint_id, "cp1")
        self.assertEqual(engine.ledger.total_bits_erased, 1000)

    def test_service_topology(self) -> None:
        topo = TelemetryServiceTopology()
        frame = topo.encode_frame({"test": "data"})
        decoded = topo.decode_frame(frame)
        self.assertEqual(decoded["test"], "data")

        # Send over channel
        res = topo.send_message("channel_research_telemetry", {"msg": "ping"})
        self.assertEqual(res["status"], "DISPATCHED")

        # Partition simulation
        topo.simulate_partition(True)
        with self.assertRaises(NetworkPartitionError):
            topo.send_message("channel_research_telemetry", {"msg": "ping"})

    def test_rfc_mediator(self) -> None:
        mediator = TelemetryRFCMediator()
        valid_req = SpecAdjustmentRequest(
            request_id="req_01",
            builder_node_id="builder_01",
            target_symbol_urn="urn:meta-axioma:g4b:telemetry",
            bottleneck_type=BottleneckType.LATENCY_OVERRUN,
            empirical_evidence="Benchmarked SLA",
            proposed_delta="SET TIMEOUT = 200",
            preserved_invariants=["[L1-G3B-012]"],
        )
        amend = mediator.adjudicate_rfc_request(valid_req)
        self.assertTrue(amend.is_approved)

        bad_req = SpecAdjustmentRequest(
            request_id="req_02",
            builder_node_id="builder_02",
            target_symbol_urn="urn:meta-axioma:g4b:telemetry",
            bottleneck_type=BottleneckType.COMPLEXITY_LIMIT,
            empirical_evidence="Testing loopback",
            proposed_delta="BIND localhost",
            preserved_invariants=["[L1-G3B-011]"],
        )
        amend_bad = mediator.adjudicate_rfc_request(bad_req)
        self.assertFalse(amend_bad.is_approved)

    def test_telemetry_kernel_integration(self) -> None:
        kernel = SovereignTelemetryKernel()
        kernel.initialize_kernel()
        status = kernel.get_status()
        self.assertEqual(status["endpoint"], "192.168.40.40:8446")
        self.assertEqual(status["statechart"]["root_state"], "ingress_standby")


if __name__ == "__main__":
    unittest.main()
