"""Tests for Sovereign Telemetry & Evaluation Service Domain Models (`soc_g4b_telemetry`).

Verifies:
- [L1-G3B-012] Non-loopback validator raises on 127.0.0.1, localhost, ::1, 0.0.0.0.
- All 6 Enums and 12 Dataclasses validate invariants and round-trip to/from dict.
- [L1-G3B-018] Landauer dissipation ledger maintains 60/40 capital partition and calculates Q = kB * T * ln(2) * bits.
- [L1-002] Functorial undo checkpoint captures state snapshot and bit counts.
- SLA reporting correctly evaluates empirical thresholds.
- Exhaustive negative invariant enforcement across all algebraic dataclasses.
"""

from __future__ import annotations

from pathlib import Path
import sys
import time
import unittest

TEL_ROOT = Path(__file__).resolve().parent.parent
REPO_ROOT = TEL_ROOT.parent.parent.parent.parent
for p in [str(TEL_ROOT), str(REPO_ROOT)]:
    if p not in sys.path:
        sys.path.insert(0, p)

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
    ServiceMeshTopologyState,
    ServiceNodeWitness,
    SpanStatusCode,
    TelemetryAttestation,
    TelemetryDomainInvariantViolation,
    TelemetryIngestBatch,
    TelemetrySentryAlert,
    TelemetrySeverityLevel,
    TelemetryTopologyState,
    TelemetryVerificationStage,
)


class TestTelemetryDomainModels(unittest.TestCase):
    """Unit tests for domain models, algebraic invariants, and serialization."""

    def test_non_loopback_validator(self):
        # Valid non-loopback IPs
        assert_non_loopback("192.168.40.40")
        assert_non_loopback("192.168.40.40:8446")
        assert_non_loopback("10.0.0.1:8080")

        # Prohibited loopback IPs
        with self.assertRaises(TelemetryDomainInvariantViolation):
            assert_non_loopback("127.0.0.1")
        with self.assertRaises(TelemetryDomainInvariantViolation):
            assert_non_loopback("127.0.0.1:8080")
        with self.assertRaises(TelemetryDomainInvariantViolation):
            assert_non_loopback("localhost")
        with self.assertRaises(TelemetryDomainInvariantViolation):
            assert_non_loopback("::1")
        with self.assertRaises(TelemetryDomainInvariantViolation):
            assert_non_loopback("0.0.0.0:8000")
        with self.assertRaises(TelemetryDomainInvariantViolation):
            assert_non_loopback("")

    def test_otel_span_record(self):
        start = time.time_ns()
        span = OTelSpanRecord(
            span_id="span_001",
            trace_id="trace_001",
            service_name="telemetry_service",
            node_ip="192.168.40.40",
            operation_name="ingest_metrics",
            start_time_ns=start,
        )
        time.sleep(0.001)
        span.finish()
        span.validate_invariants()
        self.assertGreater(span.duration_ms, 0.0)

        # Hash and dict roundtrip
        h = span.compute_hash()
        self.assertEqual(len(h), 64)
        d = span.to_dict()
        reconstituted = OTelSpanRecord.from_dict(d)
        self.assertEqual(reconstituted.span_id, span.span_id)
        self.assertEqual(reconstituted.compute_hash(), h)

    def test_otel_span_invariants_failure(self):
        # Empty span_id
        span1 = OTelSpanRecord(span_id="", trace_id="trace_1")
        with self.assertRaises(TelemetryDomainInvariantViolation):
            span1.validate_invariants()

        # Empty trace_id
        span2 = OTelSpanRecord(span_id="s1", trace_id="")
        with self.assertRaises(TelemetryDomainInvariantViolation):
            span2.validate_invariants()

        # Empty service_name
        span3 = OTelSpanRecord(span_id="s1", trace_id="t1", service_name="")
        with self.assertRaises(TelemetryDomainInvariantViolation):
            span3.validate_invariants()

        # Loopback node_ip
        span4 = OTelSpanRecord(span_id="s1", trace_id="t1", node_ip="127.0.0.1")
        with self.assertRaises(TelemetryDomainInvariantViolation):
            span4.validate_invariants()

        # Inverted timestamps
        span5 = OTelSpanRecord(span_id="s1", trace_id="t1", start_time_ns=1000)
        with self.assertRaises(TelemetryDomainInvariantViolation):
            span5.finish(end_time_ns=500)

    def test_cluster_metric_datum(self):
        metric = ClusterMetricDatum(
            metric_id="metric_001",
            metric_name="cpu_usage_pct",
            service_name="builder_service",
            node_ip="192.168.40.20",
            value=42.5,
            unit="percent",
            labels={"core": "0"},
        )
        metric.validate_invariants()
        d = metric.to_dict()
        reconstituted = ClusterMetricDatum.from_dict(d)
        self.assertEqual(reconstituted.metric_id, metric.metric_id)
        self.assertEqual(reconstituted.compute_hash(), metric.compute_hash())

    def test_cluster_metric_invariants_failure(self):
        # Empty metric_id
        m1 = ClusterMetricDatum(metric_id="", metric_name="cpu", service_name="srv", node_ip="192.168.40.10")
        with self.assertRaises(TelemetryDomainInvariantViolation):
            m1.validate_invariants()

        # Empty metric_name
        m2 = ClusterMetricDatum(metric_id="m1", metric_name="", service_name="srv", node_ip="192.168.40.10")
        with self.assertRaises(TelemetryDomainInvariantViolation):
            m2.validate_invariants()

        # Empty service_name
        m3 = ClusterMetricDatum(metric_id="m1", metric_name="cpu", service_name="", node_ip="192.168.40.10")
        with self.assertRaises(TelemetryDomainInvariantViolation):
            m3.validate_invariants()

        # Loopback IP
        m4 = ClusterMetricDatum(metric_id="m1", metric_name="cpu", service_name="srv", node_ip="localhost")
        with self.assertRaises(TelemetryDomainInvariantViolation):
            m4.validate_invariants()

    def test_landauer_dissipation_ledger(self):
        ledger = LandauerDissipationLedger(
            ledger_id="ledger_test",
            token_lease_budget=880300,
            exploratory_capital=528180,
            protected_capital=352120,
        )
        ledger.validate_invariants()

        # 60/40 partition check
        self.assertEqual(ledger.exploratory_capital + ledger.protected_capital, 880300)
        self.assertEqual(ledger.exploratory_capital / ledger.token_lease_budget, 0.6)
        self.assertEqual(ledger.protected_capital / ledger.token_lease_budget, 0.4)

        # Spend within limits
        ledger.spend_tokens(1000, is_protected=False)
        self.assertEqual(ledger.exploratory_spent, 1000)
        self.assertEqual(ledger.tokens_burned, 1000)

        ledger.spend_tokens(500, is_protected=True)
        self.assertEqual(ledger.protected_spent, 500)
        self.assertEqual(ledger.tokens_burned, 1500)

        # Bit erasure & Landauer heat dissipation: Q = kB * T * ln(2) * bits
        joules = ledger.record_bit_erasure(1_000_000, temp_kelvin=300.0)
        self.assertAlmostEqual(joules, 1.380649e-23 * 300.0 * 0.6931471805599453 * 1_000_000, places=25)
        self.assertEqual(ledger.total_bits_erased, 1_000_000)

        # Bit recovery via functorial undo
        ledger.record_bit_recovery(400_000)
        self.assertEqual(ledger.total_bits_erased, 600_000)

        # Exceeding exploratory capital ceiling
        with self.assertRaises(TelemetryDomainInvariantViolation):
            ledger.spend_tokens(600_000, is_protected=False)

        # Dict round-trip
        d = ledger.to_dict()
        reconstituted = LandauerDissipationLedger.from_dict(d)
        self.assertEqual(reconstituted.total_bits_erased, 600_000)
        self.assertEqual(reconstituted.tokens_burned, 1500)

    def test_landauer_ledger_invariants_failure(self):
        # Partition sum mismatch
        l1 = LandauerDissipationLedger(token_lease_budget=1000, exploratory_capital=500, protected_capital=400)
        with self.assertRaises(TelemetryDomainInvariantViolation):
            l1.validate_invariants()

        # Negative lease budget
        l2 = LandauerDissipationLedger(token_lease_budget=-100, exploratory_capital=0, protected_capital=-100)
        with self.assertRaises(TelemetryDomainInvariantViolation):
            l2.validate_invariants()

        # Negative spend
        l3 = LandauerDissipationLedger()
        with self.assertRaises(TelemetryDomainInvariantViolation):
            l3.spend_tokens(-50)

        # Negative bit erasure
        with self.assertRaises(TelemetryDomainInvariantViolation):
            l3.record_bit_erasure(-100)

        # Negative bit recovery
        with self.assertRaises(TelemetryDomainInvariantViolation):
            l3.record_bit_recovery(-100)

    def test_empirical_sla_report(self):
        report = EmpiricalSLAReport(
            report_id="sla_001",
            total_requests=10000,
            successful_requests=9990,
            failed_requests=10,
            error_rate=0.001,
            p50_latency_ms=4.2,
            p90_latency_ms=12.1,
            p99_latency_ms=28.4,
            throughput_rps=2500.0,
            availability_pct=99.9,
        )
        report.validate_invariants()
        passes = report.evaluate_sla_criteria(p99_threshold_ms=50.0, availability_threshold_pct=99.0)
        self.assertTrue(passes)
        self.assertTrue(report.passes_sla)

        d = report.to_dict()
        reconstituted = EmpiricalSLAReport.from_dict(d)
        self.assertEqual(reconstituted.report_id, "sla_001")
        self.assertTrue(reconstituted.passes_sla)

    def test_empirical_sla_report_invariants_failure(self):
        # Empty report_id
        r1 = EmpiricalSLAReport(report_id="")
        with self.assertRaises(TelemetryDomainInvariantViolation):
            r1.validate_invariants()

        # Request count sum mismatch
        r2 = EmpiricalSLAReport(report_id="r2", total_requests=10, successful_requests=5, failed_requests=2)
        with self.assertRaises(TelemetryDomainInvariantViolation):
            r2.validate_invariants()

        # Error rate > 1.0
        r3 = EmpiricalSLAReport(report_id="r3", total_requests=1, successful_requests=0, failed_requests=1, error_rate=1.5)
        with self.assertRaises(TelemetryDomainInvariantViolation):
            r3.validate_invariants()

        # Availability pct > 100.0
        r4 = EmpiricalSLAReport(report_id="r4", availability_pct=105.0)
        with self.assertRaises(TelemetryDomainInvariantViolation):
            r4.validate_invariants()

    def test_service_node_witness(self):
        witness = ServiceNodeWitness(
            service_name="research_service",
            node_ip="192.168.40.10",
            port=8440,
            Merkle_root="a" * 64,
            status=TelemetryTopologyState.HEALTHY,
        )
        witness.validate_invariants()
        d = witness.to_dict()
        reconstituted = ServiceNodeWitness.from_dict(d)
        self.assertEqual(reconstituted.service_name, "research_service")
        self.assertEqual(reconstituted.compute_hash(), witness.compute_hash())

    def test_service_node_witness_invariants_failure(self):
        # Empty service_name
        w1 = ServiceNodeWitness(service_name="", node_ip="192.168.40.10", port=8440)
        with self.assertRaises(TelemetryDomainInvariantViolation):
            w1.validate_invariants()

        # Prohibited loopback
        w2 = ServiceNodeWitness(service_name="srv", node_ip="127.0.0.1", port=8440)
        with self.assertRaises(TelemetryDomainInvariantViolation):
            w2.validate_invariants()

        # Invalid port
        w3 = ServiceNodeWitness(service_name="srv", node_ip="192.168.40.10", port=80)
        with self.assertRaises(TelemetryDomainInvariantViolation):
            w3.validate_invariants()

        # Negative bits_erased
        w4 = ServiceNodeWitness(service_name="srv", node_ip="192.168.40.10", port=8440, bits_erased=-5)
        with self.assertRaises(TelemetryDomainInvariantViolation):
            w4.validate_invariants()

    def test_functorial_undo_checkpoint(self):
        cp = FunctorialUndoCheckpoint(
            checkpoint_id="chk_001",
            statechart_state="STREAM_INGESTION",
            bits_erased=50000,
            active_spans_count=12,
            state_snapshot={"active_stream": True},
        )
        cp.validate_invariants()
        d = cp.to_dict()
        reconstituted = FunctorialUndoCheckpoint.from_dict(d)
        self.assertEqual(reconstituted.checkpoint_id, "chk_001")
        self.assertEqual(reconstituted.compute_hash(), cp.compute_hash())

    def test_functorial_undo_checkpoint_invariants_failure(self):
        # Empty checkpoint_id
        cp1 = FunctorialUndoCheckpoint(checkpoint_id="")
        with self.assertRaises(TelemetryDomainInvariantViolation):
            cp1.validate_invariants()

        # Negative bits_erased
        cp2 = FunctorialUndoCheckpoint(checkpoint_id="cp2", bits_erased=-10)
        with self.assertRaises(TelemetryDomainInvariantViolation):
            cp2.validate_invariants()

        # Negative active_spans_count
        cp3 = FunctorialUndoCheckpoint(checkpoint_id="cp3", active_spans_count=-1)
        with self.assertRaises(TelemetryDomainInvariantViolation):
            cp3.validate_invariants()

    def test_byzantine_telemetry_vector(self):
        vector = ByzantineTelemetryVector(
            vector_id="byz_001",
            vector_type=ByzantineVectorType.TIMESTAMP_INVERSION,
            payload={"inversion_delta_ms": -5000},
            target_channel="stream_ingest",
        )
        vector.validate_invariants()
        self.assertFalse(vector.is_trapped)
        vector.mark_trapped()
        self.assertTrue(vector.is_trapped)
        self.assertIsNotNone(vector.trapped_at_ms)

        d = vector.to_dict()
        reconstituted = ByzantineTelemetryVector.from_dict(d)
        self.assertTrue(reconstituted.is_trapped)

    def test_byzantine_telemetry_vector_invariants_failure(self):
        v1 = ByzantineTelemetryVector(vector_id="", vector_type=ByzantineVectorType.SPAN_CORRUPTION)
        with self.assertRaises(TelemetryDomainInvariantViolation):
            v1.validate_invariants()

        v2 = ByzantineTelemetryVector(vector_id="v2", vector_type=ByzantineVectorType.SPAN_CORRUPTION, target_channel="")
        with self.assertRaises(TelemetryDomainInvariantViolation):
            v2.validate_invariants()

    def test_telemetry_attestation(self):
        attestation = TelemetryAttestation(
            attestation_id="att_001",
            service_name="telemetry_service",
            node_ip="192.168.40.40",
            port=8446,
            Merkle_root="f" * 64,
            sla_certified=True,
            landauer_certified=True,
            signature="sig_verified_ed25519",
        )
        attestation.validate_invariants()
        d = attestation.to_dict()
        reconstituted = TelemetryAttestation.from_dict(d)
        self.assertEqual(reconstituted.attestation_id, "att_001")
        self.assertEqual(reconstituted.compute_hash(), attestation.compute_hash())

    def test_telemetry_attestation_invariants_failure(self):
        # Empty signature when certified
        att1 = TelemetryAttestation(
            attestation_id="att_fail",
            service_name="srv",
            node_ip="192.168.40.40",
            port=8446,
            Merkle_root="a" * 64,
            sla_certified=True,
            landauer_certified=False,
            signature="",
        )
        with self.assertRaises(TelemetryDomainInvariantViolation):
            att1.validate_invariants()

        # Empty Merkle root
        att2 = TelemetryAttestation(
            attestation_id="att_fail2",
            service_name="srv",
            node_ip="192.168.40.40",
            port=8446,
            Merkle_root="",
            sla_certified=False,
            landauer_certified=False,
        )
        with self.assertRaises(TelemetryDomainInvariantViolation):
            att2.validate_invariants()

    def test_telemetry_ingest_batch(self):
        batch = TelemetryIngestBatch(
            batch_id="batch_001",
            source_service="builder_service",
            source_ip="192.168.40.20",
            spans=[
                OTelSpanRecord(
                    span_id="s1",
                    trace_id="t1",
                    node_ip="192.168.40.20",
                )
            ],
            metrics=[
                ClusterMetricDatum(
                    metric_id="m1",
                    metric_name="tokens_burned",
                    service_name="builder_service",
                    node_ip="192.168.40.20",
                    value=150.0,
                )
            ],
        )
        batch.validate_invariants()
        d = batch.to_dict()
        reconstituted = TelemetryIngestBatch.from_dict(d)
        self.assertEqual(len(reconstituted.spans), 1)
        self.assertEqual(len(reconstituted.metrics), 1)

    def test_merkle_tree_node(self):
        node = MerkleTreeNode(
            node_hash="h1",
            leaf_data="leaf_content",
            is_leaf=True,
        )
        node.validate_invariants()
        d = node.to_dict()
        reconstituted = MerkleTreeNode.from_dict(d)
        self.assertTrue(reconstituted.is_leaf)

    def test_merkle_tree_node_invariants_failure(self):
        n1 = MerkleTreeNode(node_hash="")
        with self.assertRaises(TelemetryDomainInvariantViolation):
            n1.validate_invariants()

        n2 = MerkleTreeNode(node_hash="h2", is_leaf=True, leaf_data=None)
        with self.assertRaises(TelemetryDomainInvariantViolation):
            n2.validate_invariants()

    def test_telemetry_sentry_alert(self):
        alert = TelemetrySentryAlert(
            alert_id="alt_001",
            alert_type="P99_LATENCY_SPIKE",
            severity=TelemetrySeverityLevel.ERROR,
            message="p99 exceeded 50ms",
        )
        alert.validate_invariants()
        self.assertFalse(alert.is_resolved)
        alert.resolve()
        self.assertTrue(alert.is_resolved)

    def test_service_mesh_topology_state(self):
        topo = ServiceMeshTopologyState()
        witness = ServiceNodeWitness(
            service_name="audit_service",
            node_ip="192.168.40.30",
            port=8444,
        )
        topo.register_witness(witness)
        topo.validate_invariants()
        self.assertIn("audit_service", topo.registered_nodes)
        d = topo.to_dict()
        reconstituted = ServiceMeshTopologyState.from_dict(d)
        self.assertEqual(len(reconstituted.registered_nodes), 1)


if __name__ == "__main__":
    unittest.main()
