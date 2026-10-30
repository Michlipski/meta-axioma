"""Unit and property tests for Empirical SLA Benchmarking & Evaluation Engine (`soc_g4b_telemetry`).

Verifies:
- Accurate percentile calculations (P50, P90, P99) on uniform, skewed, and bursty latency distributions.
- SLA adherence evaluation against target thresholds:
  - P99 latency <= 100.0 ms.
  - Availability >= 99.0%.
  - Error rate <= 0.01 (1.0%).
- Failure detection on latency spikes, error bursts, and availability drops.
- High-frequency cluster metric statistical aggregation (count, min, max, mean, percentiles).
- Boundary conditions: empty spans/metrics, single-element arrays, negative windows.
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
    SpanStatusCode,
    TelemetryDomainInvariantViolation,
)
from generations.gen_04b.services.telemetry.src.empirical_sla_evaluator import (
    EmpiricalSLABenchmarker,
)


class TestEmpiricalSLABenchmarker(unittest.TestCase):
    """Test suite for EmpiricalSLABenchmarker percentile math and SLA adherence rules."""

    def setUp(self):
        self.benchmarker = EmpiricalSLABenchmarker(
            p99_threshold_ms=100.0,
            availability_threshold_pct=99.0,
            max_error_rate=0.01,
        )

    def test_compute_percentile_uniform(self):
        # 101 values from 0.0 to 100.0
        values = [float(i) for i in range(101)]
        p50 = self.benchmarker.compute_percentile(values, 50.0)
        p90 = self.benchmarker.compute_percentile(values, 90.0)
        p99 = self.benchmarker.compute_percentile(values, 99.0)

        self.assertAlmostEqual(p50, 50.0, places=2)
        self.assertAlmostEqual(p90, 90.0, places=2)
        self.assertAlmostEqual(p99, 99.0, places=2)

    def test_compute_percentile_skewed_and_bursty(self):
        # Bursty distribution: 95 requests at 4.0ms, 5 spikes at 350.0ms
        latencies = [4.0] * 95 + [350.0] * 5
        p50 = self.benchmarker.compute_percentile(latencies, 50.0)
        p90 = self.benchmarker.compute_percentile(latencies, 90.0)
        p99 = self.benchmarker.compute_percentile(latencies, 99.0)

        self.assertAlmostEqual(p50, 4.0, places=2)
        # P99 captures the burst spike
        self.assertGreater(p99, 100.0)
        self.assertAlmostEqual(p99, 350.0, places=1)

    def test_compute_percentile_boundary_conditions(self):
        # Empty array
        self.assertEqual(self.benchmarker.compute_percentile([], 50.0), 0.0)

        # Single element
        self.assertEqual(self.benchmarker.compute_percentile([42.0], 50.0), 42.0)
        self.assertEqual(self.benchmarker.compute_percentile([42.0], 99.0), 42.0)

        # Percentile out of bounds
        with self.assertRaises(TelemetryDomainInvariantViolation):
            self.benchmarker.compute_percentile([1.0, 2.0], -5.0)

        with self.assertRaises(TelemetryDomainInvariantViolation):
            self.benchmarker.compute_percentile([1.0, 2.0], 105.0)

    def test_evaluate_spans_happy_path_pass_sla(self):
        spans = []
        for i in range(100):
            s = OTelSpanRecord(
                span_id=f"s_{i}",
                trace_id="tr",
                duration_ms=12.5,
                status_code=SpanStatusCode.OK,
                node_ip="192.168.40.40",
            )
            spans.append(s)

        report = self.benchmarker.evaluate_spans(spans, window_seconds=1.0)
        self.assertEqual(report.total_requests, 100)
        self.assertEqual(report.successful_requests, 100)
        self.assertEqual(report.failed_requests, 0)
        self.assertEqual(report.error_rate, 0.0)
        self.assertEqual(report.availability_pct, 100.0)
        self.assertAlmostEqual(report.p99_latency_ms, 12.5, places=2)
        self.assertTrue(report.passes_sla)

    def test_evaluate_spans_latency_breach_fail_sla(self):
        spans = []
        # 95 normal spans at 20ms, 5 slow spans at 250ms
        for i in range(95):
            spans.append(OTelSpanRecord(span_id=f"ok_{i}", trace_id="t", duration_ms=20.0, node_ip="192.168.40.40"))
        for i in range(5):
            spans.append(OTelSpanRecord(span_id=f"slow_{i}", trace_id="t", duration_ms=250.0, node_ip="192.168.40.40"))

        report = self.benchmarker.evaluate_spans(spans, window_seconds=1.0)
        self.assertGreater(report.p99_latency_ms, 100.0)
        self.assertFalse(report.passes_sla)

    def test_evaluate_spans_availability_breach_fail_sla(self):
        spans = []
        # 95 successful, 5 failed -> 5% error rate, 95% availability (Threshold: <= 1% error, >= 99% avail)
        for i in range(95):
            spans.append(OTelSpanRecord(span_id=f"s_{i}", trace_id="t", duration_ms=10.0, status_code=SpanStatusCode.OK, node_ip="192.168.40.40"))
        for i in range(5):
            spans.append(OTelSpanRecord(span_id=f"err_{i}", trace_id="t", duration_ms=10.0, status_code=SpanStatusCode.ERROR, node_ip="192.168.40.40"))

        report = self.benchmarker.evaluate_spans(spans, window_seconds=1.0)
        self.assertEqual(report.successful_requests, 95)
        self.assertEqual(report.failed_requests, 5)
        self.assertAlmostEqual(report.error_rate, 0.05, places=4)
        self.assertAlmostEqual(report.availability_pct, 95.0, places=2)
        self.assertFalse(report.passes_sla)

    def test_evaluate_spans_empty_list(self):
        report = self.benchmarker.evaluate_spans([], window_seconds=1.0)
        self.assertEqual(report.total_requests, 0)
        self.assertEqual(report.error_rate, 0.0)
        self.assertEqual(report.availability_pct, 100.0)
        self.assertTrue(report.passes_sla)

    def test_evaluate_metrics_statistical_summary(self):
        metrics = [
            ClusterMetricDatum(metric_id="m1", metric_name="cpu_load", service_name="svc", node_ip="192.168.40.10", value=10.0),
            ClusterMetricDatum(metric_id="m2", metric_name="cpu_load", service_name="svc", node_ip="192.168.40.10", value=30.0),
            ClusterMetricDatum(metric_id="m3", metric_name="cpu_load", service_name="svc", node_ip="192.168.40.10", value=50.0),
            ClusterMetricDatum(metric_id="m4", metric_name="mem_used", service_name="svc", node_ip="192.168.40.10", value=1024.0),
        ]
        summary = self.benchmarker.evaluate_metrics(metrics)
        self.assertEqual(summary["total_datums"], 4)
        self.assertIn("cpu_load", summary["metrics"])
        self.assertIn("mem_used", summary["metrics"])

        cpu = summary["metrics"]["cpu_load"]
        self.assertEqual(cpu["count"], 3)
        self.assertEqual(cpu["min"], 10.0)
        self.assertEqual(cpu["max"], 50.0)
        self.assertEqual(cpu["mean"], 30.0)
        self.assertEqual(cpu["p50"], 30.0)

    def test_evaluate_metrics_empty(self):
        summary = self.benchmarker.evaluate_metrics([])
        self.assertEqual(summary["total_datums"], 0)
        self.assertEqual(summary["metrics"], {})

    def test_invalid_window_seconds_rejection(self):
        with self.assertRaises(TelemetryDomainInvariantViolation):
            self.benchmarker.evaluate_spans([], window_seconds=0.0)

        with self.assertRaises(TelemetryDomainInvariantViolation):
            self.benchmarker.evaluate_spans([], window_seconds=-5.0)


if __name__ == "__main__":
    unittest.main()
