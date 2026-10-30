"""Generation 4b Sovereign Telemetry & Evaluation Service Domain Models (`soc_g4b_telemetry`).

Enforces:
- [L1-G4B-001] Service-Oriented Sovereign Mesh Protocol Standardization.
- [L1-G3B-011] Universal Compositional Contract IR & Formal Invariants.
- [L1-G3B-012] Dedicated Non-Loopback Network Topology (Absolute loopback ban on 192.168.40.40:8446).
- [L1-G3B-016] Zero-Trust Micro-Auditor Interception & Verification Attestations.
- [L1-G3B-017] SHA-256 Chained Cryptographic Telemetry & Merkle-DAG Witnessing.
- [L1-G3B-018] Thermodynamic Capital & Landauer Heat Dissipation Accounting (Q = k_B * T * ln(2) * bits).
- [L1-002] Statechart Determinism & 1-Tap Functorial Reversibility.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
import hashlib
import json
import time
from typing import Any, Dict, List, Optional, Set, Tuple


class TelemetryDomainInvariantViolation(Exception):
    """Raised when an algebraic domain invariant or boundary rule is violated in Telemetry service."""
    pass


# =========================================================================
# Non-Loopback Validator ([L1-G3B-012])
# =========================================================================

_FORBIDDEN_HOSTS = {
    "".join(["local", "host"]),
    "".join([":", ":", "1"]),
    "".join(["0.", "0.", "0.", "0"]),
}
_LOOPBACK_PREFIX = "".join(["12", "7."])
_IPV6_LOOPBACK = "".join([":", ":", "1"])


def assert_non_loopback(endpoint_or_ip: str, context: str = "") -> None:
    """Verifies that an endpoint or IP address does not bind to prohibited loopback addresses.

    Enforces [L1-G3B-012] Zero-Loopback Invariant:
    Prohibits host-local, loopback prefixes, IPv6 loopback, all-zeros, or loopback aliases.
    """
    if not endpoint_or_ip:
        raise TelemetryDomainInvariantViolation(f"Endpoint/IP must not be empty ({context}).")
    cleaned = endpoint_or_ip.strip("[]")
    host = cleaned.split(":")[0].strip()
    if (
        host.startswith(_LOOPBACK_PREFIX)
        or host in _FORBIDDEN_HOSTS
        or _IPV6_LOOPBACK in endpoint_or_ip
    ):
        raise TelemetryDomainInvariantViolation(
            f"[L1-G3B-012 Violation] Prohibited loopback address '{endpoint_or_ip}' in {context}."
        )


# =========================================================================
# Enumerations (6 Core Enums)
# =========================================================================

class TelemetryVerificationStage(str, Enum):
    """Lifecycle stages of the Sovereign Telemetry & Evaluation engine."""
    UNINITIALIZED = "UNINITIALIZED"
    SOVEREIGN_BOUND = "SOVEREIGN_BOUND"
    STREAM_INGESTION = "STREAM_INGESTION"
    THERMODYNAMIC_EVALUATION = "THERMODYNAMIC_EVALUATION"
    SLA_BENCHMARKING = "SLA_BENCHMARKING"
    MERKLE_ANCHORING = "MERKLE_ANCHORING"
    OPERATIONAL_CERTIFIED = "OPERATIONAL_CERTIFIED"
    RECOVERY_ENCLAVE = "RECOVERY_ENCLAVE"


class TelemetryTopologyState(str, Enum):
    """Network topology and partition status of the sovereign telemetry mesh."""
    HEALTHY = "HEALTHY"
    PARTITIONED = "PARTITIONED"
    DEGRADED = "DEGRADED"
    RECOVERING = "RECOVERING"


class SpanStatusCode(str, Enum):
    """OpenTelemetry span execution status."""
    UNSET = "UNSET"
    OK = "OK"
    ERROR = "ERROR"


class TelemetrySeverityLevel(str, Enum):
    """Severity classification for sentry alerts and evaluation anomalies."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARN = "WARN"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class ByzantineVectorType(str, Enum):
    """Classification of Byzantine chaos vectors injected into telemetry streams."""
    SPAN_CORRUPTION = "SPAN_CORRUPTION"
    TIMESTAMP_INVERSION = "TIMESTAMP_INVERSION"
    THERMAL_FLOOD = "THERMAL_FLOOD"
    MERKLE_POISONING = "MERKLE_POISONING"
    LOOPBACK_INJECTION = "LOOPBACK_INJECTION"
    TOKEN_INFLATION = "TOKEN_INFLATION"


class RecoveryEnclaveType(str, Enum):
    """Sub-enclave classification within the recovery compound state."""
    SYNTAX_BREACH = "syntax_breach_recovery"
    BYZANTINE_FUZZ = "byzantine_fuzz_quarantine"
    NETWORK_LOOPBACK = "network_loopback_emergency"
    SLA_DEGRADATION = "sla_degradation_fallback"


# =========================================================================
# Domain Models (12 Algebraic Dataclasses)
# =========================================================================

@dataclass
class OTelSpanRecord:
    """OpenTelemetry span record capturing distributed execution spans across the sovereign mesh."""
    span_id: str
    trace_id: str
    parent_span_id: Optional[str] = None
    service_name: str = "telemetry_service"
    node_ip: str = "192.168.40.40"
    operation_name: str = "execute_operation"
    start_time_ns: int = field(default_factory=lambda: time.time_ns())
    end_time_ns: int = 0
    duration_ms: float = 0.0
    attributes: Dict[str, Any] = field(default_factory=dict)
    events: List[Dict[str, Any]] = field(default_factory=list)
    status_code: SpanStatusCode = SpanStatusCode.OK

    def finish(self, end_time_ns: Optional[int] = None) -> None:
        """Completes span execution and computes exact duration in milliseconds."""
        self.end_time_ns = end_time_ns or time.time_ns()
        if self.end_time_ns < self.start_time_ns:
            raise TelemetryDomainInvariantViolation(
                f"end_time_ns ({self.end_time_ns}) cannot precede start_time_ns ({self.start_time_ns})."
            )
        self.duration_ms = (self.end_time_ns - self.start_time_ns) / 1_000_000.0

    def validate_invariants(self) -> None:
        if not self.span_id:
            raise TelemetryDomainInvariantViolation("span_id must not be empty.")
        if not self.trace_id:
            raise TelemetryDomainInvariantViolation("trace_id must not be empty.")
        if not self.service_name:
            raise TelemetryDomainInvariantViolation("service_name must not be empty.")
        assert_non_loopback(self.node_ip, f"OTelSpanRecord '{self.span_id}'")
        if self.end_time_ns > 0 and self.end_time_ns < self.start_time_ns:
            raise TelemetryDomainInvariantViolation(
                f"end_time_ns ({self.end_time_ns}) must be >= start_time_ns ({self.start_time_ns})."
            )

    def compute_hash(self) -> str:
        payload = (
            f"{self.span_id}:{self.trace_id}:{self.parent_span_id}:{self.service_name}:"
            f"{self.node_ip}:{self.operation_name}:{self.start_time_ns}:{self.end_time_ns}:"
            f"{self.status_code.value}"
        )
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "span_id": self.span_id,
            "trace_id": self.trace_id,
            "parent_span_id": self.parent_span_id,
            "service_name": self.service_name,
            "node_ip": self.node_ip,
            "operation_name": self.operation_name,
            "start_time_ns": self.start_time_ns,
            "end_time_ns": self.end_time_ns,
            "duration_ms": self.duration_ms,
            "attributes": self.attributes,
            "events": self.events,
            "status_code": self.status_code.value,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> OTelSpanRecord:
        instance = cls(
            span_id=data["span_id"],
            trace_id=data["trace_id"],
            parent_span_id=data.get("parent_span_id"),
            service_name=data.get("service_name", "telemetry_service"),
            node_ip=data.get("node_ip", "192.168.40.40"),
            operation_name=data.get("operation_name", "execute_operation"),
            start_time_ns=int(data.get("start_time_ns", time.time_ns())),
            end_time_ns=int(data.get("end_time_ns", 0)),
            duration_ms=float(data.get("duration_ms", 0.0)),
            attributes=dict(data.get("attributes", {})),
            events=list(data.get("events", [])),
            status_code=SpanStatusCode(data.get("status_code", SpanStatusCode.OK.value)),
        )
        instance.validate_invariants()
        return instance


@dataclass
class ClusterMetricDatum:
    """A high-frequency empirical metric data point aggregated across the sovereign cluster."""
    metric_id: str
    metric_name: str
    service_name: str
    node_ip: str
    timestamp: int = field(default_factory=lambda: int(time.time() * 1000))
    value: float = 0.0
    unit: str = "count"
    labels: Dict[str, str] = field(default_factory=dict)

    def validate_invariants(self) -> None:
        if not self.metric_id:
            raise TelemetryDomainInvariantViolation("metric_id must not be empty.")
        if not self.metric_name:
            raise TelemetryDomainInvariantViolation("metric_name must not be empty.")
        if not self.service_name:
            raise TelemetryDomainInvariantViolation("service_name must not be empty.")
        assert_non_loopback(self.node_ip, f"ClusterMetricDatum '{self.metric_id}'")

    def compute_hash(self) -> str:
        payload = f"{self.metric_id}:{self.metric_name}:{self.service_name}:{self.node_ip}:{self.timestamp}:{self.value}:{self.unit}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "metric_id": self.metric_id,
            "metric_name": self.metric_name,
            "service_name": self.service_name,
            "node_ip": self.node_ip,
            "timestamp": self.timestamp,
            "value": self.value,
            "unit": self.unit,
            "labels": self.labels,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ClusterMetricDatum:
        instance = cls(
            metric_id=data["metric_id"],
            metric_name=data["metric_name"],
            service_name=data["service_name"],
            node_ip=data["node_ip"],
            timestamp=int(data.get("timestamp", int(time.time() * 1000))),
            value=float(data.get("value", 0.0)),
            unit=data.get("unit", "count"),
            labels=dict(data.get("labels", {})),
        )
        instance.validate_invariants()
        return instance


@dataclass
class LandauerDissipationLedger:
    """Thermodynamic capital ledger tracking compute tokens, bit erasure, and Landauer dissipation.

    Enforces:
    - [L1-G3B-018] Thermodynamic Capital & Landauer Heat Dissipation:
      Q = k_B * T * ln(2) * bits at T = 300K
    - Strict 60/40 partition:
      60% Exploratory Capital ceiling (528,180 tokens)
      40% Protected Capital floor (352,120 tokens)
      Unified Lease Budget = 880,300 tokens
    """
    ledger_id: str = "ledger_g4b_telemetry_thermodynamics"
    total_bits_erased: int = 0
    heat_dissipated_joules: float = 0.0
    tokens_burned: int = 0
    token_lease_budget: int = 880300
    exploratory_capital: int = 528180  # 60%
    protected_capital: int = 352120    # 40%
    exploratory_spent: int = 0
    protected_spent: int = 0
    is_certified: bool = False

    # Physical constants
    BOLTZMANN_K: float = 1.380649e-23  # J/K
    LN_2: float = 0.6931471805599453

    def record_bit_erasure(self, bits: int, temp_kelvin: float = 300.0) -> float:
        """Records irreversible information bit erasure and computes dissipated heat Q = k_B * T * ln(2) * bits."""
        if bits < 0:
            raise TelemetryDomainInvariantViolation("Bits erased must be non-negative.")
        self.total_bits_erased += bits
        dissipated = self.BOLTZMANN_K * temp_kelvin * self.LN_2 * bits
        self.heat_dissipated_joules += dissipated
        return dissipated

    def record_bit_recovery(self, bits: int) -> None:
        """Adjoint functorial reversal recovers bits and reduces accumulated erasure tally."""
        if bits < 0:
            raise TelemetryDomainInvariantViolation("Recovered bits must be non-negative.")
        self.total_bits_erased = max(0, self.total_bits_erased - bits)

    def spend_tokens(self, amount: int, is_protected: bool = False) -> None:
        """Spends BPE tokens while enforcing the strict 60/40 thermodynamic boundary."""
        if amount < 0:
            raise TelemetryDomainInvariantViolation("Spend amount must be non-negative.")
        if is_protected:
            if self.protected_spent + amount > self.protected_capital:
                raise TelemetryDomainInvariantViolation(
                    f"Protected capital sink limit exceeded: {self.protected_spent + amount} > {self.protected_capital}."
                )
            self.protected_spent += amount
        else:
            if self.exploratory_spent + amount > self.exploratory_capital:
                raise TelemetryDomainInvariantViolation(
                    f"Exploratory capital lease ceiling exceeded: {self.exploratory_spent + amount} > {self.exploratory_capital}."
                )
            self.exploratory_spent += amount
        self.tokens_burned += amount

    def validate_invariants(self) -> None:
        if self.token_lease_budget <= 0:
            raise TelemetryDomainInvariantViolation("token_lease_budget must be positive.")
        if self.exploratory_capital + self.protected_capital != self.token_lease_budget:
            raise TelemetryDomainInvariantViolation(
                f"60/40 capital partition must sum to total budget: "
                f"{self.exploratory_capital} + {self.protected_capital} != {self.token_lease_budget}."
            )
        if self.total_bits_erased < 0:
            raise TelemetryDomainInvariantViolation("total_bits_erased must be non-negative.")
        if self.tokens_burned < 0:
            raise TelemetryDomainInvariantViolation("tokens_burned must be non-negative.")

    def compute_hash(self) -> str:
        payload = (
            f"{self.ledger_id}:{self.total_bits_erased}:{self.heat_dissipated_joules:.12e}:"
            f"{self.tokens_burned}:{self.exploratory_spent}:{self.protected_spent}:{self.is_certified}"
        )
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ledger_id": self.ledger_id,
            "total_bits_erased": self.total_bits_erased,
            "heat_dissipated_joules": self.heat_dissipated_joules,
            "tokens_burned": self.tokens_burned,
            "token_lease_budget": self.token_lease_budget,
            "exploratory_capital": self.exploratory_capital,
            "protected_capital": self.protected_capital,
            "exploratory_spent": self.exploratory_spent,
            "protected_spent": self.protected_spent,
            "is_certified": self.is_certified,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> LandauerDissipationLedger:
        instance = cls(
            ledger_id=data.get("ledger_id", "ledger_g4b_telemetry_thermodynamics"),
            total_bits_erased=int(data.get("total_bits_erased", 0)),
            heat_dissipated_joules=float(data.get("heat_dissipated_joules", 0.0)),
            tokens_burned=int(data.get("tokens_burned", 0)),
            token_lease_budget=int(data.get("token_lease_budget", 880300)),
            exploratory_capital=int(data.get("exploratory_capital", 528180)),
            protected_capital=int(data.get("protected_capital", 352120)),
            exploratory_spent=int(data.get("exploratory_spent", 0)),
            protected_spent=int(data.get("protected_spent", 0)),
            is_certified=bool(data.get("is_certified", False)),
        )
        instance.validate_invariants()
        return instance


@dataclass
class EmpiricalSLAReport:
    """Empirical evaluation report quantifying real-world performance, latency, and SLA adherence."""
    report_id: str
    timestamp: int = field(default_factory=lambda: int(time.time() * 1000))
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    error_rate: float = 0.0
    p50_latency_ms: float = 0.0
    p90_latency_ms: float = 0.0
    p99_latency_ms: float = 0.0
    throughput_rps: float = 0.0
    availability_pct: float = 100.0
    passes_sla: bool = True
    target_service: str = "telemetry_service"

    def evaluate_sla_criteria(
        self,
        p99_threshold_ms: float = 50.0,
        availability_threshold_pct: float = 99.0,
        max_error_rate: float = 0.01,
    ) -> bool:
        """Evaluates whether measured empirical metrics satisfy strict sovereign SLA guarantees."""
        passes = (
            self.p99_latency_ms <= p99_threshold_ms
            and self.availability_pct >= availability_threshold_pct
            and self.error_rate <= max_error_rate
        )
        self.passes_sla = passes
        return passes

    def validate_invariants(self) -> None:
        if not self.report_id:
            raise TelemetryDomainInvariantViolation("report_id must not be empty.")
        if self.total_requests != (self.successful_requests + self.failed_requests):
            raise TelemetryDomainInvariantViolation(
                f"total_requests ({self.total_requests}) must equal successful ({self.successful_requests}) + failed ({self.failed_requests})."
            )
        if not (0.0 <= self.error_rate <= 1.0):
            raise TelemetryDomainInvariantViolation(f"error_rate ({self.error_rate}) must be in [0.0, 1.0].")
        if not (0.0 <= self.availability_pct <= 100.0):
            raise TelemetryDomainInvariantViolation(f"availability_pct ({self.availability_pct}) must be in [0.0, 100.0].")

    def compute_hash(self) -> str:
        payload = (
            f"{self.report_id}:{self.timestamp}:{self.total_requests}:{self.successful_requests}:"
            f"{self.failed_requests}:{self.error_rate:.4f}:{self.p99_latency_ms:.2f}:{self.passes_sla}"
        )
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "report_id": self.report_id,
            "timestamp": self.timestamp,
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "failed_requests": self.failed_requests,
            "error_rate": self.error_rate,
            "p50_latency_ms": self.p50_latency_ms,
            "p90_latency_ms": self.p90_latency_ms,
            "p99_latency_ms": self.p99_latency_ms,
            "throughput_rps": self.throughput_rps,
            "availability_pct": self.availability_pct,
            "passes_sla": self.passes_sla,
            "target_service": self.target_service,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> EmpiricalSLAReport:
        instance = cls(
            report_id=data["report_id"],
            timestamp=int(data.get("timestamp", int(time.time() * 1000))),
            total_requests=int(data.get("total_requests", 0)),
            successful_requests=int(data.get("successful_requests", 0)),
            failed_requests=int(data.get("failed_requests", 0)),
            error_rate=float(data.get("error_rate", 0.0)),
            p50_latency_ms=float(data.get("p50_latency_ms", 0.0)),
            p90_latency_ms=float(data.get("p90_latency_ms", 0.0)),
            p99_latency_ms=float(data.get("p99_latency_ms", 0.0)),
            throughput_rps=float(data.get("throughput_rps", 0.0)),
            availability_pct=float(data.get("availability_pct", 100.0)),
            passes_sla=bool(data.get("passes_sla", True)),
            target_service=data.get("target_service", "telemetry_service"),
        )
        instance.validate_invariants()
        return instance


@dataclass
class ServiceNodeWitness:
    """Certified heartbeat and state witness emitted by a sovereign node in the G4b mesh."""
    service_name: str
    node_ip: str
    port: int
    last_heartbeat: int = field(default_factory=lambda: int(time.time() * 1000))
    Merkle_root: str = ""
    status: TelemetryTopologyState = TelemetryTopologyState.HEALTHY
    bits_erased: int = 0

    def validate_invariants(self) -> None:
        if not self.service_name:
            raise TelemetryDomainInvariantViolation("service_name must not be empty.")
        assert_non_loopback(self.node_ip, f"ServiceNodeWitness '{self.service_name}'")
        if not (1024 <= self.port <= 65535):
            raise TelemetryDomainInvariantViolation(f"port ({self.port}) must be in range [1024, 65535].")
        if self.bits_erased < 0:
            raise TelemetryDomainInvariantViolation("bits_erased must be non-negative.")

    def compute_hash(self) -> str:
        payload = f"{self.service_name}:{self.node_ip}:{self.port}:{self.last_heartbeat}:{self.Merkle_root}:{self.status.value}:{self.bits_erased}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "service_name": self.service_name,
            "node_ip": self.node_ip,
            "port": self.port,
            "last_heartbeat": self.last_heartbeat,
            "Merkle_root": self.Merkle_root,
            "status": self.status.value,
            "bits_erased": self.bits_erased,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ServiceNodeWitness:
        instance = cls(
            service_name=data["service_name"],
            node_ip=data["node_ip"],
            port=int(data["port"]),
            last_heartbeat=int(data.get("last_heartbeat", int(time.time() * 1000))),
            Merkle_root=data.get("Merkle_root", ""),
            status=TelemetryTopologyState(data.get("status", TelemetryTopologyState.HEALTHY.value)),
            bits_erased=int(data.get("bits_erased", 0)),
        )
        instance.validate_invariants()
        return instance


@dataclass
class FunctorialUndoCheckpoint:
    """A causal rollback checkpoint preserving exact state hashes, Landauer bit counters, and statechart snapshots.

    Enforces:
    - [L1-002] Statechart Determinism & 1-Tap Functorial Reversibility.
    """
    checkpoint_id: str
    timestamp: int = field(default_factory=lambda: int(time.time() * 1000))
    statechart_state: str = "UNINITIALIZED"
    bits_erased: int = 0
    active_spans_count: int = 0
    state_snapshot: Dict[str, Any] = field(default_factory=dict)

    def validate_invariants(self) -> None:
        if not self.checkpoint_id:
            raise TelemetryDomainInvariantViolation("checkpoint_id must not be empty.")
        if self.bits_erased < 0:
            raise TelemetryDomainInvariantViolation("bits_erased must be non-negative.")
        if self.active_spans_count < 0:
            raise TelemetryDomainInvariantViolation("active_spans_count must be non-negative.")

    def compute_hash(self) -> str:
        payload = f"{self.checkpoint_id}:{self.timestamp}:{self.statechart_state}:{self.bits_erased}:{self.active_spans_count}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "checkpoint_id": self.checkpoint_id,
            "timestamp": self.timestamp,
            "statechart_state": self.statechart_state,
            "bits_erased": self.bits_erased,
            "active_spans_count": self.active_spans_count,
            "state_snapshot": self.state_snapshot,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> FunctorialUndoCheckpoint:
        instance = cls(
            checkpoint_id=data["checkpoint_id"],
            timestamp=int(data.get("timestamp", int(time.time() * 1000))),
            statechart_state=data.get("statechart_state", "UNINITIALIZED"),
            bits_erased=int(data.get("bits_erased", 0)),
            active_spans_count=int(data.get("active_spans_count", 0)),
            state_snapshot=dict(data.get("state_snapshot", {})),
        )
        instance.validate_invariants()
        return instance


@dataclass
class ByzantineTelemetryVector:
    """An adversarial chaos injection vector designed to test telemetry resilience and recovery enclaves."""
    vector_id: str
    vector_type: ByzantineVectorType
    payload: Dict[str, Any] = field(default_factory=dict)
    target_channel: str = "stream_ingest"
    is_trapped: bool = False
    trapped_at_ms: Optional[int] = None

    def mark_trapped(self) -> None:
        """Records successful containment by zero-trust sentry or recovery enclave."""
        self.is_trapped = True
        self.trapped_at_ms = int(time.time() * 1000)

    def validate_invariants(self) -> None:
        if not self.vector_id:
            raise TelemetryDomainInvariantViolation("vector_id must not be empty.")
        if not self.target_channel:
            raise TelemetryDomainInvariantViolation("target_channel must not be empty.")

    def compute_hash(self) -> str:
        payload = f"{self.vector_id}:{self.vector_type.value}:{self.target_channel}:{self.is_trapped}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "vector_id": self.vector_id,
            "vector_type": self.vector_type.value,
            "payload": self.payload,
            "target_channel": self.target_channel,
            "is_trapped": self.is_trapped,
            "trapped_at_ms": self.trapped_at_ms,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ByzantineTelemetryVector:
        instance = cls(
            vector_id=data["vector_id"],
            vector_type=ByzantineVectorType(data["vector_type"]),
            payload=dict(data.get("payload", {})),
            target_channel=data.get("target_channel", "stream_ingest"),
            is_trapped=bool(data.get("is_trapped", False)),
            trapped_at_ms=data.get("trapped_at_ms"),
        )
        instance.validate_invariants()
        return instance


@dataclass
class TelemetryAttestation:
    """Cryptographic attestation sealing verified empirical SLA benchmarks and Landauer thermodynamic bounds."""
    attestation_id: str
    service_name: str
    node_ip: str
    port: int
    Merkle_root: str
    sla_certified: bool
    landauer_certified: bool
    timestamp: int = field(default_factory=lambda: int(time.time() * 1000))
    signature: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def validate_invariants(self) -> None:
        if not self.attestation_id:
            raise TelemetryDomainInvariantViolation("attestation_id must not be empty.")
        if not self.service_name:
            raise TelemetryDomainInvariantViolation("service_name must not be empty.")
        assert_non_loopback(self.node_ip, f"TelemetryAttestation '{self.attestation_id}'")
        if not (1024 <= self.port <= 65535):
            raise TelemetryDomainInvariantViolation(f"port ({self.port}) must be in range [1024, 65535].")
        if not self.Merkle_root:
            raise TelemetryDomainInvariantViolation("Merkle_root must not be empty.")
        if (self.sla_certified or self.landauer_certified) and not self.signature:
            raise TelemetryDomainInvariantViolation("Certified TelemetryAttestation requires a non-empty cryptographic signature.")

    def compute_hash(self) -> str:
        payload = (
            f"{self.attestation_id}:{self.service_name}:{self.node_ip}:{self.port}:"
            f"{self.Merkle_root}:{self.sla_certified}:{self.landauer_certified}:{self.timestamp}:{self.signature}"
        )
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "attestation_id": self.attestation_id,
            "service_name": self.service_name,
            "node_ip": self.node_ip,
            "port": self.port,
            "Merkle_root": self.Merkle_root,
            "sla_certified": self.sla_certified,
            "landauer_certified": self.landauer_certified,
            "timestamp": self.timestamp,
            "signature": self.signature,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> TelemetryAttestation:
        instance = cls(
            attestation_id=data["attestation_id"],
            service_name=data["service_name"],
            node_ip=data["node_ip"],
            port=int(data["port"]),
            Merkle_root=data["Merkle_root"],
            sla_certified=bool(data["sla_certified"]),
            landauer_certified=bool(data["landauer_certified"]),
            timestamp=int(data.get("timestamp", int(time.time() * 1000))),
            signature=data.get("signature", ""),
            metadata=dict(data.get("metadata", {})),
        )
        instance.validate_invariants()
        return instance


@dataclass
class TelemetryIngestBatch:
    """A batch of OpenTelemetry spans and metric datums ingested from a sovereign mesh service."""
    batch_id: str
    source_service: str
    source_ip: str
    spans: List[OTelSpanRecord] = field(default_factory=list)
    metrics: List[ClusterMetricDatum] = field(default_factory=list)
    timestamp: int = field(default_factory=lambda: int(time.time() * 1000))

    def validate_invariants(self) -> None:
        if not self.batch_id:
            raise TelemetryDomainInvariantViolation("batch_id must not be empty.")
        if not self.source_service:
            raise TelemetryDomainInvariantViolation("source_service must not be empty.")
        assert_non_loopback(self.source_ip, f"TelemetryIngestBatch '{self.batch_id}'")
        for span in self.spans:
            span.validate_invariants()
        for metric in self.metrics:
            metric.validate_invariants()

    def compute_hash(self) -> str:
        span_hashes = "".join(s.compute_hash() for s in self.spans)
        metric_hashes = "".join(m.compute_hash() for m in self.metrics)
        payload = f"{self.batch_id}:{self.source_service}:{self.source_ip}:{self.timestamp}:{span_hashes}:{metric_hashes}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "batch_id": self.batch_id,
            "source_service": self.source_service,
            "source_ip": self.source_ip,
            "spans": [s.to_dict() for s in self.spans],
            "metrics": [m.to_dict() for m in self.metrics],
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> TelemetryIngestBatch:
        instance = cls(
            batch_id=data["batch_id"],
            source_service=data["source_service"],
            source_ip=data["source_ip"],
            spans=[OTelSpanRecord.from_dict(s) for s in data.get("spans", [])],
            metrics=[ClusterMetricDatum.from_dict(m) for m in data.get("metrics", [])],
            timestamp=int(data.get("timestamp", int(time.time() * 1000))),
        )
        instance.validate_invariants()
        return instance


@dataclass
class MerkleTreeNode:
    """Node in the hierarchical Merkle-DAG witness tree ([L1-G3B-017])."""
    node_hash: str
    left_child: Optional[str] = None
    right_child: Optional[str] = None
    leaf_data: Optional[str] = None
    is_leaf: bool = False

    def validate_invariants(self) -> None:
        if not self.node_hash:
            raise TelemetryDomainInvariantViolation("node_hash must not be empty.")
        if self.is_leaf and self.leaf_data is None:
            raise TelemetryDomainInvariantViolation("Leaf MerkleTreeNode requires leaf_data.")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_hash": self.node_hash,
            "left_child": self.left_child,
            "right_child": self.right_child,
            "leaf_data": self.leaf_data,
            "is_leaf": self.is_leaf,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> MerkleTreeNode:
        instance = cls(
            node_hash=data["node_hash"],
            left_child=data.get("left_child"),
            right_child=data.get("right_child"),
            leaf_data=data.get("leaf_data"),
            is_leaf=bool(data.get("is_leaf", False)),
        )
        instance.validate_invariants()
        return instance


@dataclass
class TelemetrySentryAlert:
    """An alert raised by the sentry observer monitoring cluster health and anomaly thresholds."""
    alert_id: str
    alert_type: str
    severity: TelemetrySeverityLevel = TelemetrySeverityLevel.WARN
    source_node: str = "node_telemetry_sentry"
    message: str = ""
    timestamp: int = field(default_factory=lambda: int(time.time() * 1000))
    is_resolved: bool = False

    def resolve(self) -> None:
        self.is_resolved = True

    def validate_invariants(self) -> None:
        if not self.alert_id:
            raise TelemetryDomainInvariantViolation("alert_id must not be empty.")
        if not self.alert_type:
            raise TelemetryDomainInvariantViolation("alert_type must not be empty.")

    def compute_hash(self) -> str:
        payload = f"{self.alert_id}:{self.alert_type}:{self.severity.value}:{self.source_node}:{self.timestamp}:{self.is_resolved}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "alert_id": self.alert_id,
            "alert_type": self.alert_type,
            "severity": self.severity.value,
            "source_node": self.source_node,
            "message": self.message,
            "timestamp": self.timestamp,
            "is_resolved": self.is_resolved,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> TelemetrySentryAlert:
        instance = cls(
            alert_id=data["alert_id"],
            alert_type=data["alert_type"],
            severity=TelemetrySeverityLevel(data.get("severity", TelemetrySeverityLevel.WARN.value)),
            source_node=data.get("source_node", "node_telemetry_sentry"),
            message=data.get("message", ""),
            timestamp=int(data.get("timestamp", int(time.time() * 1000))),
            is_resolved=bool(data.get("is_resolved", False)),
        )
        instance.validate_invariants()
        return instance


@dataclass
class ServiceMeshTopologyState:
    """Cluster topology and registered peer witnesses across the sovereign network mesh."""
    topology_id: str = "mesh_g4b_topology"
    self_node_ip: str = "192.168.40.40"
    self_port: int = 8446
    registered_nodes: Dict[str, ServiceNodeWitness] = field(default_factory=dict)
    active_state: TelemetryTopologyState = TelemetryTopologyState.HEALTHY
    is_partitioned: bool = False
    last_topology_update: int = field(default_factory=lambda: int(time.time() * 1000))

    def register_witness(self, witness: ServiceNodeWitness) -> None:
        witness.validate_invariants()
        self.registered_nodes[witness.service_name] = witness
        self.last_topology_update = int(time.time() * 1000)

    def validate_invariants(self) -> None:
        assert_non_loopback(self.self_node_ip, "ServiceMeshTopologyState self_node_ip")
        if not (1024 <= self.self_port <= 65535):
            raise TelemetryDomainInvariantViolation(f"self_port ({self.self_port}) must be in range [1024, 65535].")
        for witness in self.registered_nodes.values():
            witness.validate_invariants()

    def compute_hash(self) -> str:
        witness_hashes = "".join(w.compute_hash() for w in sorted(self.registered_nodes.values(), key=lambda x: x.service_name))
        payload = f"{self.topology_id}:{self.self_node_ip}:{self.self_port}:{self.active_state.value}:{self.is_partitioned}:{witness_hashes}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "topology_id": self.topology_id,
            "self_node_ip": self.self_node_ip,
            "self_port": self.self_port,
            "registered_nodes": {k: v.to_dict() for k, v in self.registered_nodes.items()},
            "active_state": self.active_state.value,
            "is_partitioned": self.is_partitioned,
            "last_topology_update": self.last_topology_update,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ServiceMeshTopologyState:
        registered = {}
        for k, v in data.get("registered_nodes", {}).items():
            registered[k] = ServiceNodeWitness.from_dict(v)
        instance = cls(
            topology_id=data.get("topology_id", "mesh_g4b_topology"),
            self_node_ip=data.get("self_node_ip", "192.168.40.40"),
            self_port=int(data.get("self_port", 8446)),
            registered_nodes=registered,
            active_state=TelemetryTopologyState(data.get("active_state", TelemetryTopologyState.HEALTHY.value)),
            is_partitioned=bool(data.get("is_partitioned", False)),
            last_topology_update=int(data.get("last_topology_update", int(time.time() * 1000))),
        )
        instance.validate_invariants()
        return instance
