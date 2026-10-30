"""Unit and invariant tests for OpenTelemetry Span & Metric Ingestion Engine (`soc_g4b_telemetry`).

Verifies:
- [L1-G3B-012] Dedicated Non-Loopback Network Topology enforcement on span and batch ingestion.
- Rejection of loopback addresses (127.0.0.1, localhost, ::1, 0.0.0.0) with TelemetryDomainInvariantViolation.
- Single span and batch ingestion into bounded ring buffers.
- Bounded capacity eviction on buffer overflow.
- Windowed metric queries with temporal cutoff filtering.
- Lookup by span ID and service name.
- Buffer clear and occupancy accounting.
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
    ClusterMetricDatum,
    OTelSpanRecord,
    SpanStatusCode,
    TelemetryDomainInvariantViolation,
    TelemetryIngestBatch,
)
from generations.gen_04b.services.telemetry.src.otel_span_ingester import OTelSpanIngester


class TestOTelSpanIngester(unittest.TestCase):
    """Test suite for OTelSpanIngester non-blocking ring buffer ingestion."""

    def setUp(self):
        self.ingester = OTelSpanIngester(max_spans=10, max_metrics=20)

    def test_single_span_ingestion(self):
        span = OTelSpanRecord(
            span_id="span_101",
            trace_id="trace_101",
            service_name="research_service",
            node_ip="192.168.40.10",
            operation_name="explore_topology",
        )
        span.finish()
        self.ingester.ingest_span(span)

        self.assertEqual(self.ingester.total_spans_ingested, 1)
        active = self.ingester.get_active_spans()
        self.assertEqual(len(active), 1)
        self.assertEqual(active[0].span_id, "span_101")
        self.assertEqual(self.ingester.get_span_by_id("span_101"), span)

    def test_single_span_loopback_rejection(self):
        # Direct span with loopback IP
        bad_span = OTelSpanRecord(
            span_id="span_bad",
            trace_id="trace_bad",
            node_ip="127.0.0.1",
        )
        with self.assertRaises(TelemetryDomainInvariantViolation):
            self.ingester.ingest_span(bad_span)

        # Hostname loopback
        bad_span2 = OTelSpanRecord(
            span_id="span_bad2",
            trace_id="trace_bad2",
            node_ip="localhost",
        )
        with self.assertRaises(TelemetryDomainInvariantViolation):
            self.ingester.ingest_span(bad_span2)

        # IPv6 loopback
        bad_span3 = OTelSpanRecord(
            span_id="span_bad3",
            trace_id="trace_bad3",
            node_ip="::1",
        )
        with self.assertRaises(TelemetryDomainInvariantViolation):
            self.ingester.ingest_span(bad_span3)

    def test_single_metric_ingestion_and_loopback_rejection(self):
        metric = ClusterMetricDatum(
            metric_id="m_101",
            metric_name="heap_used_bytes",
            service_name="audit_service",
            node_ip="192.168.40.30",
            value=102400.0,
        )
        self.ingester.ingest_metric(metric)
        self.assertEqual(self.ingester.total_metrics_ingested, 1)
        self.assertEqual(len(self.ingester.get_all_metrics()), 1)

        bad_metric = ClusterMetricDatum(
            metric_id="m_bad",
            metric_name="heap_used_bytes",
            service_name="audit_service",
            node_ip="0.0.0.0",
            value=50.0,
        )
        with self.assertRaises(TelemetryDomainInvariantViolation):
            self.ingester.ingest_metric(bad_metric)

    def test_batch_ingestion_happy_path(self):
        spans = [
            OTelSpanRecord(
                span_id=f"batch_s_{i}",
                trace_id="trace_batch",
                service_name="builder_service",
                node_ip="192.168.40.20",
            )
            for i in range(3)
        ]
        metrics = [
            ClusterMetricDatum(
                metric_id=f"batch_m_{i}",
                metric_name="tokens_per_sec",
                service_name="builder_service",
                node_ip="192.168.40.20",
                value=float(100 * i),
            )
            for i in range(2)
        ]
        batch = TelemetryIngestBatch(
            batch_id="b_001",
            source_service="builder_service",
            source_ip="192.168.40.20",
            spans=spans,
            metrics=metrics,
        )
        self.ingester.ingest_batch(batch)

        self.assertEqual(self.ingester.total_spans_ingested, 3)
        self.assertEqual(self.ingester.total_metrics_ingested, 2)
        self.assertEqual(len(self.ingester.get_spans_by_service("builder_service")), 3)

    def test_batch_ingestion_loopback_source_rejection(self):
        batch = TelemetryIngestBatch(
            batch_id="b_bad_source",
            source_service="builder_service",
            source_ip="127.0.0.1",
            spans=[],
            metrics=[],
        )
        with self.assertRaises(TelemetryDomainInvariantViolation):
            self.ingester.ingest_batch(batch)

    def test_ring_buffer_eviction_on_overflow(self):
        small_ingester = OTelSpanIngester(max_spans=3, max_metrics=3)
        for i in range(5):
            s = OTelSpanRecord(
                span_id=f"s_{i}",
                trace_id="tr",
                node_ip="192.168.40.40",
            )
            small_ingester.ingest_span(s)

        # Buffer should only retain the last 3 spans (s_2, s_3, s_4)
        active = small_ingester.get_active_spans()
        self.assertEqual(len(active), 3)
        self.assertEqual([s.span_id for s in active], ["s_2", "s_3", "s_4"])
        # Total counter should still track all 5
        self.assertEqual(small_ingester.total_spans_ingested, 5)

    def test_windowed_metric_retrieval(self):
        now_ms = int(time.time() * 1000)
        m_old = ClusterMetricDatum(
            metric_id="m_old",
            metric_name="cpu",
            service_name="svc",
            node_ip="192.168.40.10",
            timestamp=now_ms - 100_000,  # 100 seconds ago
        )
        m_recent = ClusterMetricDatum(
            metric_id="m_recent",
            metric_name="cpu",
            service_name="svc",
            node_ip="192.168.40.10",
            timestamp=now_ms - 5_000,   # 5 seconds ago
        )
        self.ingester.ingest_metric(m_old)
        self.ingester.ingest_metric(m_recent)

        # 30-second window should include m_recent and exclude m_old
        window_30s = self.ingester.get_metrics_window(window_sec=30.0)
        self.assertEqual(len(window_30s), 1)
        self.assertEqual(window_30s[0].metric_id, "m_recent")

        # Negative window should raise invariant violation
        with self.assertRaises(TelemetryDomainInvariantViolation):
            self.ingester.get_metrics_window(window_sec=-10.0)

    def test_clear_buffer_and_occupancy(self):
        span = OTelSpanRecord(span_id="s_clr", trace_id="t", node_ip="192.168.40.40")
        self.ingester.ingest_span(span)
        occ_before = self.ingester.buffer_occupancy
        self.assertEqual(occ_before["spans_count"], 1)

        self.ingester.clear()
        occ_after = self.ingester.buffer_occupancy
        self.assertEqual(occ_after["spans_count"], 0)
        self.assertEqual(len(self.ingester.get_active_spans()), 0)
        # Historical counter preserved
        self.assertEqual(self.ingester.total_spans_ingested, 1)

    def test_invalid_constructor_bounds(self):
        with self.assertRaises(TelemetryDomainInvariantViolation):
            OTelSpanIngester(max_spans=0)
        with self.assertRaises(TelemetryDomainInvariantViolation):
            OTelSpanIngester(max_metrics=-5)


if __name__ == "__main__":
    unittest.main()
