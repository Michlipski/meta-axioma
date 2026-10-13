"""Axioma Generation 3 Production Observability & User Zero Auditing.

Implements standard OpenTelemetry trace export, Prometheus metrics scraping,
and User Zero direct developer interaction auditing per [L1-G3-003].
Enforces zero synthetic persona fraud [NEG-G3-011].
"""

from __future__ import annotations
import json
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


class SyntheticSimulationFraudError(Exception):
    """Raised when synthetic mock personas are detected attempting to fabricate human utility metrics."""
    pass


@dataclass
class OTelSpan:
    """Standard OpenTelemetry span representation."""
    trace_id: str
    span_id: str
    name: str
    start_time_ns: int
    end_time_ns: int
    attributes: Dict[str, Any] = field(default_factory=dict)
    events: List[Dict[str, Any]] = field(default_factory=list)
    status_code: str = "OK"

    def to_otlp_json(self) -> Dict[str, Any]:
        return {
            "traceId": self.trace_id,
            "spanId": self.span_id,
            "name": self.name,
            "startTimeUnixNano": self.start_time_ns,
            "endTimeUnixNano": self.end_time_ns,
            "attributes": [{"key": k, "value": {"stringValue": str(v)}} for k, v in self.attributes.items()],
            "status": {"code": self.status_code},
        }


class ProductionObservabilityExporter:
    """Exports production-grade OpenTelemetry spans and Prometheus metrics."""

    def __init__(self, service_name: str = "axioma-g3-mesh") -> None:
        self.service_name = service_name
        self.spans: List[OTelSpan] = []
        self.metrics: Dict[str, float] = {}

    def record_span(
        self,
        trace_id: str,
        span_id: str,
        name: str,
        duration_ms: float,
        attributes: Optional[Dict[str, Any]] = None,
    ) -> OTelSpan:
        now_ns = int(time.time() * 1e9)
        dur_ns = int(duration_ms * 1e6)
        span = OTelSpan(
            trace_id=trace_id,
            span_id=span_id,
            name=name,
            start_time_ns=now_ns - dur_ns,
            end_time_ns=now_ns,
            attributes=attributes or {},
        )
        self.spans.append(span)
        return span

    def set_metric(self, name: str, value: float) -> None:
        self.metrics[name] = float(value)

    def export_prometheus_text(self) -> str:
        """Export metrics in standard Prometheus 0.0.4 text format."""
        lines = [f"# Observability metrics for service {self.service_name}"]
        for k, v in sorted(self.metrics.items()):
            sanitized = k.replace(".", "_").replace("-", "_")
            lines.append(f"# TYPE {sanitized} gauge")
            lines.append(f"{sanitized}{{service=\"{self.service_name}\"}} {v}")
        return "\n".join(lines) + "\n"

    def export_otlp_traces(self) -> str:
        """Export collected spans in standard OTLP JSON format."""
        payload = {
            "resourceSpans": [{
                "resource": {
                    "attributes": [{"key": "service.name", "value": {"stringValue": self.service_name}}]
                },
                "scopeSpans": [{
                    "scope": {"name": "axioma.g3.tracer", "version": "3.0.0"},
                    "spans": [s.to_otlp_json() for s in self.spans],
                }],
            }]
        }
        return json.dumps(payload, indent=2)


class UserZeroAuditor:
    """Audits real human developer interaction telemetry and enforces anti-fraud invariants."""

    def __init__(self, human_operator_id: str = "Michael Lipski") -> None:
        self.human_operator_id = human_operator_id
        self._interaction_events: List[Dict[str, Any]] = []
        self.synthetic_personas_detected: int = 0

    def record_operator_action(
        self,
        command_name: str,
        duration_ms: float,
        exit_code: int,
        is_human_direct: bool = True,
        persona_tag: Optional[str] = None,
    ) -> None:
        # Enforce NEG-G3-011: detect synthetic personas masquerading as human telemetry
        if persona_tag and ("synthetic" in persona_tag.lower() or "simulated_user" in persona_tag.lower()):
            self.synthetic_personas_detected += 1
            raise SyntheticSimulationFraudError(
                f"[NEG-G3-011 VETO]: Synthetic persona '{persona_tag}' detected. "
                "Generating simulated users to fabricate utility satisfaction metrics is strictly forbidden."
            )

        self._interaction_events.append({
            "operator": self.human_operator_id,
            "command": command_name,
            "duration_ms": duration_ms,
            "exit_code": exit_code,
            "is_human_direct": is_human_direct,
            "timestamp": time.time(),
        })

    def get_user_zero_metrics(self) -> Dict[str, Any]:
        total = len(self._interaction_events)
        if total == 0:
            return {
                "total_actions": 0,
                "friction_score": 0.0,
                "success_rate": 1.0,
                "synthetic_fraud_count": self.synthetic_personas_detected,
                "passed_grounded_gate": True,
            }

        successes = sum(1 for e in self._interaction_events if e["exit_code"] == 0)
        avg_duration = sum(e["duration_ms"] for e in self._interaction_events) / total
        friction = max(0.0, min(1.0, (1.0 - (successes / total)) + (avg_duration / 2000.0)))

        return {
            "total_actions": total,
            "avg_duration_ms": round(avg_duration, 2),
            "friction_score": round(friction, 4),
            "success_rate": round(successes / total, 4),
            "synthetic_fraud_count": self.synthetic_personas_detected,
            "passed_grounded_gate": friction <= 0.15 and self.synthetic_personas_detected == 0,
        }
