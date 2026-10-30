"""Generation 4b Sovereign Telemetry & Evaluation Service (`soc_g4b_telemetry`).

Exports all domain models, enums, exceptions, non-loopback invariants,
and sovereign engine modules:
- OTelSpanIngester
- LandauerThermodynamicEngine
- EmpiricalSLABenchmarker
- MeshMultiSourceAggregator
- TelemetryMerkleWitnessEngine
- TelemetryStatechartEngine
- TelemetryFunctorialUndoManager
- TelemetryServiceTopology, PartitionPolicy, NetworkPartitionError
- TelemetryRFCMediator
- SovereignTelemetryKernel
"""

from __future__ import annotations

from .domain_models import (
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
from .otel_span_ingester import OTelSpanIngester
from .landauer_thermodynamic_engine import LandauerThermodynamicEngine
from .empirical_sla_evaluator import EmpiricalSLABenchmarker
from .mesh_multi_source_aggregator import MeshMultiSourceAggregator
from .merkle_dag_witness_engine import TelemetryMerkleWitnessEngine
from .statechart_engine import TelemetryStatechartEngine
from .functorial_undo import TelemetryFunctorialUndoManager
from .service_topology import (
    NetworkPartitionError,
    PartitionPolicy,
    TelemetryChannel,
    TelemetryServiceTopology,
)
from .rfc_protocol_mediator import TelemetryRFCMediator
from .telemetry_kernel import SovereignTelemetryKernel

__all__ = [
    # Invariant validator & exceptions
    "assert_non_loopback",
    "TelemetryDomainInvariantViolation",
    "NetworkPartitionError",
    # Enums
    "ByzantineVectorType",
    "PartitionPolicy",
    "RecoveryEnclaveType",
    "SpanStatusCode",
    "TelemetrySeverityLevel",
    "TelemetryTopologyState",
    "TelemetryVerificationStage",
    # Dataclasses
    "ByzantineTelemetryVector",
    "ClusterMetricDatum",
    "EmpiricalSLAReport",
    "FunctorialUndoCheckpoint",
    "LandauerDissipationLedger",
    "MerkleTreeNode",
    "OTelSpanRecord",
    "ServiceMeshTopologyState",
    "ServiceNodeWitness",
    "TelemetryAttestation",
    "TelemetryChannel",
    "TelemetryIngestBatch",
    "TelemetrySentryAlert",
    # Subsystems & Kernel
    "OTelSpanIngester",
    "LandauerThermodynamicEngine",
    "EmpiricalSLABenchmarker",
    "MeshMultiSourceAggregator",
    "TelemetryMerkleWitnessEngine",
    "TelemetryStatechartEngine",
    "TelemetryFunctorialUndoManager",
    "TelemetryServiceTopology",
    "TelemetryRFCMediator",
    "SovereignTelemetryKernel",
]
