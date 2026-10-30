"""Empirical SLA Benchmarking & Evaluation Engine (`soc_g4b_telemetry`).

Enforces:
- Empirical SLA benchmark computation: P50, P90, P99 latency percentiles, error rate, throughput, and availability.
- Target SLA validation:
  - P99 latency <= 100.0 ms (or custom threshold).
  - Availability >= 99.0%.
  - Error rate <= 0.01 (1.0%).
- Rigorous domain validation and invariant checks.
"""

from __future__ import annotations

import math
import statistics
import time
from typing import Any, Dict, List, Optional
import uuid

from .domain_models import (
    ClusterMetricDatum,
    EmpiricalSLAReport,
    OTelSpanRecord,
    SpanStatusCode,
    TelemetryDomainInvariantViolation,
)


class EmpiricalSLABenchmarker:
    """Empirical SLA evaluator quantifying latency percentiles, throughput, and service availability."""

    DEFAULT_P99_THRESHOLD_MS: float = 100.0
    DEFAULT_AVAILABILITY_THRESHOLD_PCT: float = 99.0
    DEFAULT_MAX_ERROR_RATE: float = 0.01

    def __init__(
        self,
        p99_threshold_ms: float = DEFAULT_P99_THRESHOLD_MS,
        availability_threshold_pct: float = DEFAULT_AVAILABILITY_THRESHOLD_PCT,
        max_error_rate: float = DEFAULT_MAX_ERROR_RATE,
    ) -> None:
        self.p99_threshold_ms = p99_threshold_ms
        self.availability_threshold_pct = availability_threshold_pct
        self.max_error_rate = max_error_rate

    @staticmethod
    def compute_percentile(values: List[float], percentile: float) -> float:
        """Calculates percentile (0.0 to 100.0) using linear interpolation."""
        if not values:
            return 0.0
        if len(values) == 1:
            return float(values[0])
        if not (0.0 <= percentile <= 100.0):
            raise TelemetryDomainInvariantViolation(f"Percentile must be in [0, 100], got {percentile}.")

        sorted_vals = sorted(values)
        k = (len(sorted_vals) - 1) * (percentile / 100.0)
        f = math.floor(k)
        c = math.ceil(k)
        if f == c:
            return float(sorted_vals[int(k)])
        d0 = sorted_vals[int(f)] * (c - k)
        d1 = sorted_vals[int(c)] * (k - f)
        return float(d0 + d1)

    def evaluate_spans(
        self,
        spans: List[OTelSpanRecord],
        window_seconds: float = 1.0,
        report_id: Optional[str] = None,
        target_service: str = "telemetry_service",
    ) -> EmpiricalSLAReport:
        """Evaluates empirical SLA performance from a collection of OpenTelemetry execution spans."""
        if window_seconds <= 0:
            raise TelemetryDomainInvariantViolation("window_seconds must be positive.")

        rid = report_id or f"sla_rep_{uuid.uuid4().hex[:12]}"
        total_requests = len(spans)

        if total_requests == 0:
            report = EmpiricalSLAReport(
                report_id=rid,
                timestamp=int(time.time() * 1000),
                total_requests=0,
                successful_requests=0,
                failed_requests=0,
                error_rate=0.0,
                p50_latency_ms=0.0,
                p90_latency_ms=0.0,
                p99_latency_ms=0.0,
                throughput_rps=0.0,
                availability_pct=100.0,
                passes_sla=True,
                target_service=target_service,
            )
            report.validate_invariants()
            return report

        successful = 0
        failed = 0
        latencies: List[float] = []

        for span in spans:
            # Ensure duration is populated
            dur = span.duration_ms
            if dur <= 0.0 and span.end_time_ns > span.start_time_ns:
                dur = (span.end_time_ns - span.start_time_ns) / 1_000_000.0
            latencies.append(dur)

            if span.status_code == SpanStatusCode.ERROR:
                failed += 1
            else:
                successful += 1

        error_rate = float(failed) / float(total_requests)
        availability_pct = (float(successful) / float(total_requests)) * 100.0
        throughput_rps = float(total_requests) / float(window_seconds)

        p50 = self.compute_percentile(latencies, 50.0)
        p90 = self.compute_percentile(latencies, 90.0)
        p99 = self.compute_percentile(latencies, 99.0)

        report = EmpiricalSLAReport(
            report_id=rid,
            timestamp=int(time.time() * 1000),
            total_requests=total_requests,
            successful_requests=successful,
            failed_requests=failed,
            error_rate=round(error_rate, 6),
            p50_latency_ms=round(p50, 3),
            p90_latency_ms=round(p90, 3),
            p99_latency_ms=round(p99, 3),
            throughput_rps=round(throughput_rps, 2),
            availability_pct=round(availability_pct, 4),
            passes_sla=False,  # Evaluated below
            target_service=target_service,
        )

        report.evaluate_sla_criteria(
            p99_threshold_ms=self.p99_threshold_ms,
            availability_threshold_pct=self.availability_threshold_pct,
            max_error_rate=self.max_error_rate,
        )
        report.validate_invariants()
        return report

    def evaluate_metrics(self, metrics: List[ClusterMetricDatum]) -> Dict[str, Any]:
        """Aggregates high-frequency cluster metrics into statistical summaries."""
        if not metrics:
            return {"total_datums": 0, "metrics": {}}

        grouped: Dict[str, List[float]] = {}
        for m in metrics:
            if m.metric_name not in grouped:
                grouped[m.metric_name] = []
            grouped[m.metric_name].append(m.value)

        summary: Dict[str, Any] = {
            "total_datums": len(metrics),
            "metrics": {},
        }

        for metric_name, values in grouped.items():
            summary["metrics"][metric_name] = {
                "count": len(values),
                "min": min(values),
                "max": max(values),
                "mean": statistics.mean(values),
                "p50": self.compute_percentile(values, 50.0),
                "p90": self.compute_percentile(values, 90.0),
                "p99": self.compute_percentile(values, 99.0),
            }

        return summary
