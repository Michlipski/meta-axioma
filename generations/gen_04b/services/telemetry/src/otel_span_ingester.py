"""OpenTelemetry Span & Metric Ingestion Engine (`soc_g4b_telemetry`).

Enforces:
- Invariant [L1-G3B-012]: Dedicated Non-Loopback Network Topology.
- Non-blocking ingestion of OTelSpanRecords, ClusterMetricDatums, and TelemetryIngestBatches.
- In-memory bounded ring buffers preventing buffer overrun and memory exhaustion.
- Bounded time-window query semantics for empirical SLA evaluation.
"""

from __future__ import annotations

from collections import deque
import time
from typing import Any, Dict, List, Optional

from .domain_models import (
    assert_non_loopback,
    ClusterMetricDatum,
    OTelSpanRecord,
    SpanStatusCode,
    TelemetryDomainInvariantViolation,
    TelemetryIngestBatch,
)


class OTelSpanIngester:
    """Non-blocking OpenTelemetry span and metric ingester with ring buffer storage."""

    def __init__(self, max_spans: int = 20000, max_metrics: int = 50000) -> None:
        if max_spans <= 0:
            raise TelemetryDomainInvariantViolation("max_spans must be positive.")
        if max_metrics <= 0:
            raise TelemetryDomainInvariantViolation("max_metrics must be positive.")

        self.max_spans = max_spans
        self.max_metrics = max_metrics

        self._span_buffer: deque[OTelSpanRecord] = deque(maxlen=max_spans)
        self._metric_buffer: deque[ClusterMetricDatum] = deque(maxlen=max_metrics)
        self._spans_by_id: Dict[str, OTelSpanRecord] = {}
        self._total_spans_ingested: int = 0
        self._total_metrics_ingested: int = 0

    def ingest_span(self, span: OTelSpanRecord) -> None:
        """Ingests a single OpenTelemetry span after strict non-loopback and invariant validation."""
        span.validate_invariants()
        assert_non_loopback(span.node_ip, f"OTelSpanIngester.ingest_span '{span.span_id}'")

        self._span_buffer.append(span)
        self._spans_by_id[span.span_id] = span
        self._total_spans_ingested += 1

    def ingest_metric(self, metric: ClusterMetricDatum) -> None:
        """Ingests a single cluster metric datum after non-loopback validation."""
        metric.validate_invariants()
        assert_non_loopback(metric.node_ip, f"OTelSpanIngester.ingest_metric '{metric.metric_id}'")

        self._metric_buffer.append(metric)
        self._total_metrics_ingested += 1

    def ingest_batch(self, batch: TelemetryIngestBatch) -> None:
        """Ingests an entire telemetry batch from a sovereign mesh service."""
        batch.validate_invariants()
        assert_non_loopback(batch.source_ip, f"OTelSpanIngester.ingest_batch '{batch.batch_id}'")

        for span in batch.spans:
            self.ingest_span(span)
        for metric in batch.metrics:
            self.ingest_metric(metric)

    def get_active_spans(self) -> List[OTelSpanRecord]:
        """Returns all currently buffered spans in ingestion order."""
        return list(self._span_buffer)

    def get_metrics_window(self, window_sec: float = 60.0) -> List[ClusterMetricDatum]:
        """Retrieves metric data points recorded within the designated time window in seconds."""
        if window_sec < 0:
            raise TelemetryDomainInvariantViolation("window_sec must be non-negative.")

        cutoff_timestamp_ms = int((time.time() - window_sec) * 1000)
        return [m for m in self._metric_buffer if m.timestamp >= cutoff_timestamp_ms]

    def get_all_metrics(self) -> List[ClusterMetricDatum]:
        """Returns all buffered metric data points."""
        return list(self._metric_buffer)

    def get_span_by_id(self, span_id: str) -> Optional[OTelSpanRecord]:
        """Retrieves a span by its unique identifier if present."""
        return self._spans_by_id.get(span_id)

    def get_spans_by_service(self, service_name: str) -> List[OTelSpanRecord]:
        """Retrieves all buffered spans for a designated service."""
        return [s for s in self._span_buffer if s.service_name == service_name]

    def clear(self) -> None:
        """Flushes in-memory ring buffers while retaining total historical counters."""
        self._span_buffer.clear()
        self._metric_buffer.clear()
        self._spans_by_id.clear()

    @property
    def total_spans_ingested(self) -> int:
        return self._total_spans_ingested

    @property
    def total_metrics_ingested(self) -> int:
        return self._total_metrics_ingested

    @property
    def buffer_occupancy(self) -> Dict[str, Any]:
        return {
            "spans_count": len(self._span_buffer),
            "spans_capacity": self.max_spans,
            "metrics_count": len(self._metric_buffer),
            "metrics_capacity": self.max_metrics,
            "total_spans_ingested": self._total_spans_ingested,
            "total_metrics_ingested": self._total_metrics_ingested,
        }
