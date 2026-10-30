"""Sovereign Telemetry Kernel & Orchestration Engine (`soc_g4b_telemetry`).

Enforces:
- Invariant [L1-G4B-001]: Service-Oriented Sovereign Mesh Protocol Standardization.
- Invariant [L1-G3B-012]: Dedicated Non-Loopback Network Topology on 192.168.40.40:8446.
- Invariant [L1-G3B-017]: SHA-256 Chained Cryptographic Telemetry & Merkle-DAG Witnessing.
- Invariant [L1-G3B-018]: Thermodynamic Capital & Landauer Heat Dissipation Accounting.
- Invariant [L1-002]: Statechart Determinism & 1-Tap Functorial Reversibility.
- Coordinates all 9 sovereign telemetry subsystems:
  1. OTelSpanIngester
  2. LandauerThermodynamicEngine
  3. EmpiricalSLABenchmarker
  4. MeshMultiSourceAggregator
  5. TelemetryMerkleWitnessEngine
  6. TelemetryStatechartEngine
  7. TelemetryFunctorialUndoManager
  8. TelemetryServiceTopology
  9. TelemetryRFCMediator
"""

from __future__ import annotations

import hashlib
import time
from typing import Any, Dict, List, Optional
import uuid

from generations.gen_04b.protocols.rfc_protocol import (
    SpecAdjustmentRequest,
    SpecAmendment,
)
from .domain_models import (
    assert_non_loopback,
    ByzantineTelemetryVector,
    ByzantineVectorType,
    ClusterMetricDatum,
    EmpiricalSLAReport,
    FunctorialUndoCheckpoint,
    LandauerDissipationLedger,
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
from .otel_span_ingester import OTelSpanIngester
from .landauer_thermodynamic_engine import LandauerThermodynamicEngine
from .empirical_sla_evaluator import EmpiricalSLABenchmarker
from .mesh_multi_source_aggregator import MeshMultiSourceAggregator
from .merkle_dag_witness_engine import TelemetryMerkleWitnessEngine
from .statechart_engine import TelemetryStatechartEngine
from .functorial_undo import TelemetryFunctorialUndoManager
from .service_topology import PartitionPolicy, TelemetryServiceTopology
from .rfc_protocol_mediator import TelemetryRFCMediator


class SovereignTelemetryKernel:
    """Master sovereign telemetry and empirical evaluation coordinator."""

    DEFAULT_NODE_IP: str = "192.168.40.40"
    DEFAULT_PORT: int = 8446
    SERVICE_NAME: str = "telemetry_service"

    def __init__(
        self,
        node_ip: str = DEFAULT_NODE_IP,
        port: int = DEFAULT_PORT,
        token_budget: int = 880300,  # Option C Zenith Apex Lease Budget
    ) -> None:
        self.endpoint = f"{node_ip}:{port}"
        assert_non_loopback(self.endpoint, "SovereignTelemetryKernel initialization")

        self.node_ip = node_ip
        self.port = port
        self.token_budget = token_budget

        # 1. Statechart Engine (30 states)
        self.statechart = TelemetryStatechartEngine()

        # 2. Topology Management
        self.topology = TelemetryServiceTopology(node_ip=node_ip, port=port)

        # 3. Thermodynamic Engine (60/40 partition)
        self.thermo_engine = LandauerThermodynamicEngine(token_lease_budget=token_budget)

        # 4. Ingestion Engine
        self.ingester = OTelSpanIngester()

        # 5. SLA Benchmarking
        self.sla_benchmarker = EmpiricalSLABenchmarker()

        # 6. Multi-Source Mesh Aggregator
        self.mesh_aggregator = MeshMultiSourceAggregator(self_node_ip=node_ip, self_port=port)

        # 7. Merkle-DAG Witness Engine
        self.merkle_engine = TelemetryMerkleWitnessEngine(node_id="node_telemetry_merkle_witness")

        # 8. Functorial Undo Manager
        self.undo_manager = TelemetryFunctorialUndoManager()

        # 9. RFC Protocol Mediator
        self.rfc_mediator = TelemetryRFCMediator(node_id="node_telemetry_rfc_mediator", endpoint=self.endpoint)

        # Alerts and attestations history
        self.alerts: List[TelemetrySentryAlert] = []
        self.attestations: List[TelemetryAttestation] = []
        self.trapped_byzantine_vectors: List[ByzantineTelemetryVector] = []

    def initialize_kernel(self) -> Dict[str, str]:
        """Boots sovereign kernel, bounds dedicated non-loopback network, and enters standby."""
        # state_uninitialized -> state_binding_lan -> state_sovereign_bound -> ingress_standby
        self.statechart.send("EV_BIND_LAN")
        self.statechart.send("EV_LAN_BOUND")
        self.statechart.send("EV_STANDBY")

        # Create pre-ingestion causal checkpoint
        self.undo_manager.create_checkpoint(
            checkpoint_id="ckpt_init_standby",
            statechart_state=self.statechart.current_state,
            bits_erased=self.thermo_engine.ledger.total_bits_erased,
            active_spans_count=len(self.ingester.get_active_spans()),
            state_snapshot={"stage": "ingress_standby", "endpoint": self.endpoint},
        )

        return self.statechart.get_active_configuration()

    def ingest_telemetry_batch(self, batch: TelemetryIngestBatch) -> Dict[str, Any]:
        """Ingests, validates, and processes a batch of telemetry spans and metrics."""
        batch.validate_invariants()
        assert_non_loopback(batch.source_ip, f"ingest_telemetry_batch '{batch.batch_id}'")

        # Advance statechart through ingestion strata
        if self.statechart.current_state in ("ingress_standby", "state_operational_certified", "state_sovereign_bound"):
            self.statechart.send("EV_START_INGESTION")

        self.statechart.send("EV_VALIDATE_BATCH")

        # Ingest into buffer
        self.ingester.ingest_batch(batch)

        # Compute bits erased for batch ingestion and record in thermodynamic engine
        batch_bits = len(batch.spans) * 64 + len(batch.metrics) * 32
        self.thermo_engine.record_bit_erasure(batch_bits, operation=f"ingest_batch_{batch.batch_id}")
        self.statechart.send("EV_THERMO_DISSIPATE")
        self.statechart.send("EV_THERMO_COOL")

        # Record in Merkle DAG
        leaf_hash = self.merkle_engine.record_event("TELEMETRY_INGEST_BATCH", batch.to_dict())

        # Update sentry observer
        self.statechart.send("EV_SENTRY_HEARTBEAT")
        self.statechart.send("EV_SENTRY_OK")

        self.statechart.send("EV_BATCH_VALIDATED")

        return {
            "batch_id": batch.batch_id,
            "spans_ingested": len(batch.spans),
            "metrics_ingested": len(batch.metrics),
            "leaf_hash": leaf_hash,
            "thermodynamic_bits_erased": batch_bits,
            "current_statechart": self.statechart.current_state,
        }

    def evaluate_current_sla(self, window_seconds: float = 1.0) -> EmpiricalSLAReport:
        """Executes empirical SLA benchmarking over active spans and reconciles state."""
        if self.statechart.current_state == "metric_aggregation_active":
            self.statechart.send("EV_START_THERMO")

        if self.statechart.current_state == "active_thermodynamic_evaluation":
            self.statechart.send("EV_RECONCILE_LEDGER")
            self.statechart.send("EV_START_SLA")
        elif self.statechart.current_state == "ledger_reconciliation":
            self.statechart.send("EV_START_SLA")

        spans = self.ingester.get_active_spans()
        report = self.sla_benchmarker.evaluate_spans(
            spans,
            window_seconds=window_seconds,
            target_service=self.SERVICE_NAME,
        )

        # Record SLA report in Merkle DAG
        self.merkle_engine.record_event("EMPIRICAL_SLA_REPORT", report.to_dict())

        # If SLA degraded, trigger recovery enclave
        if not report.passes_sla:
            self.statechart.send("EV_SLA_DEGRADED")
            alert = TelemetrySentryAlert(
                alert_id=f"alert_sla_{uuid.uuid4().hex[:8]}",
                alert_type="SLA_DEGRADATION",
                severity=TelemetrySeverityLevel.ERROR,
                message=f"P99 latency {report.p99_latency_ms}ms or Error rate {report.error_rate} violated SLA.",
            )
            self.alerts.append(alert)
            self.statechart.send("EV_SENTRY_ALERT")

        return report

    def calculate_landauer_dissipation(self) -> Dict[str, Any]:
        """Reconciles thermodynamic dissipation ledger and verifies capital invariants."""
        self.thermo_engine.verify_capital_invariants()
        metrics = self.thermo_engine.dissipation_metrics

        # Record thermodynamic reconciliation in Merkle DAG
        self.merkle_engine.record_event("LANDAUER_THERMODYNAMICS_RECONCILIATION", metrics)
        return metrics

    def anchor_merkle_witness(self) -> str:
        """Anchors all recorded events into SHA-256 Merkle-DAG root."""
        if self.statechart.current_state in ("ingress_standby", "active_sla_benchmarking"):
            self.statechart.send("EV_START_MERKLE")

        if self.statechart.current_state == "active_merkle_anchoring":
            self.statechart.send("EV_VERIFY_DAG")

        root = self.merkle_engine.compute_root()
        if not self.merkle_engine.verify_chain_integrity():
            raise TelemetryDomainInvariantViolation("Merkle-DAG integrity verification failed.")

        return root

    def mint_telemetry_attestation(
        self,
        attestation_id: Optional[str] = None,
        sla_certified: bool = True,
        landauer_certified: bool = True,
    ) -> TelemetryAttestation:
        """Mints and dispatches certified cryptographic TelemetryAttestation."""
        aid = attestation_id or f"attest_tel_{uuid.uuid4().hex[:12]}"

        if self.statechart.current_state == "merkle_dag_verifying":
            self.statechart.send("EV_START_EMISSION")

        if self.statechart.current_state == "active_attestation_emission":
            self.statechart.send("EV_DISPATCH_ATTESTATION")

        attestation = self.merkle_engine.mint_attestation(
            attestation_id=aid,
            service_name=self.SERVICE_NAME,
            node_ip=self.node_ip,
            port=self.port,
            sla_certified=sla_certified,
            landauer_certified=landauer_certified,
            metadata={
                "statechart_state": self.statechart.current_state,
                "bits_erased": self.thermo_engine.ledger.total_bits_erased,
                "spans_count": len(self.ingester.get_active_spans()),
            },
        )
        self.attestations.append(attestation)

        # Transition to state_operational_certified
        if self.statechart.current_state in ("attestation_dispatching", "active_attestation_emission"):
            self.statechart.send("EV_CERTIFY_OPERATIONAL")
        return attestation

    def trap_byzantine_chaos_vector(self, vector: ByzantineTelemetryVector) -> Dict[str, Any]:
        """Intercepts adversarial Byzantine vector and contains it within recovery enclaves."""
        vector.validate_invariants()

        enclave_map = {
            ByzantineVectorType.SPAN_CORRUPTION: RecoveryEnclaveType.SYNTAX_BREACH,
            ByzantineVectorType.TIMESTAMP_INVERSION: RecoveryEnclaveType.BYZANTINE_FUZZ,
            ByzantineVectorType.THERMAL_FLOOD: RecoveryEnclaveType.BYZANTINE_FUZZ,
            ByzantineVectorType.MERKLE_POISONING: RecoveryEnclaveType.BYZANTINE_FUZZ,
            ByzantineVectorType.LOOPBACK_INJECTION: RecoveryEnclaveType.NETWORK_LOOPBACK,
            ByzantineVectorType.TOKEN_INFLATION: RecoveryEnclaveType.BYZANTINE_FUZZ,
        }

        enclave_type = enclave_map.get(vector.vector_type, RecoveryEnclaveType.BYZANTINE_FUZZ)
        self.trigger_recovery_enclave(enclave_type, reason=f"Trapped Byzantine vector {vector.vector_id} ({vector.vector_type.value})")

        vector.mark_trapped()
        self.trapped_byzantine_vectors.append(vector)

        # Sentry alert
        self.statechart.send("EV_SENTRY_ALERT")

        # Record in Merkle DAG
        self.merkle_engine.record_event("BYZANTINE_CHAOS_TRAPPED", vector.to_dict())

        # Restore from recovery enclave via unwinding
        self.statechart.send("EV_RESTORE")
        self.statechart.send("EV_UNWIND_COMPLETE")
        self.statechart.send("EV_SENTRY_RESOLVED")

        return {
            "vector_id": vector.vector_id,
            "status": "CONTAINED_AND_RESOLVED",
            "enclave": enclave_type.value,
            "trapped_at_ms": vector.trapped_at_ms,
        }

    def trigger_recovery_enclave(self, enclave_type: RecoveryEnclaveType, reason: str = "") -> str:
        """Forces immediate transition into designated recovery enclave."""
        state = self.statechart.trigger_enclave(enclave_type)
        alert = TelemetrySentryAlert(
            alert_id=f"alert_enc_{uuid.uuid4().hex[:8]}",
            alert_type=enclave_type.name,
            severity=TelemetrySeverityLevel.CRITICAL,
            message=reason or f"Emergency enclave triggered: {enclave_type.value}",
        )
        self.alerts.append(alert)
        return state

    def execute_functorial_undo(self, checkpoint_id: str) -> FunctorialUndoCheckpoint:
        """Executes causal adjoint rollback and bit-reversal to the specified checkpoint."""
        checkpoint = self.undo_manager.rollback_to_checkpoint(
            checkpoint_id,
            thermodynamic_engine=self.thermo_engine,
        )

        # Restore statechart state
        if checkpoint.statechart_state in self.statechart.ALL_STATES:
            self.statechart.current_state = checkpoint.statechart_state

        return checkpoint

    def get_status(self) -> Dict[str, Any]:
        """Returns comprehensive sovereign telemetry service status."""
        config = self.statechart.get_active_configuration()
        return {
            "service_name": self.SERVICE_NAME,
            "node_ip": self.node_ip,
            "port": self.port,
            "endpoint": self.endpoint,
            "statechart": config,
            "thermodynamics": self.thermo_engine.dissipation_metrics,
            "ingester": self.ingester.buffer_occupancy,
            "merkle_leaves_count": self.merkle_engine.leaves_count,
            "undo_checkpoints_depth": self.undo_manager.stack_depth,
            "mesh_registered_nodes": len(self.mesh_aggregator.get_registered_nodes()),
            "attestations_minted": len(self.attestations),
            "alerts_count": len(self.alerts),
            "byzantine_trapped_count": len(self.trapped_byzantine_vectors),
        }
