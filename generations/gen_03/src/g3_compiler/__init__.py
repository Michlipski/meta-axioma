"""Generation 3 Distributed Systems Compiler Package.

Exports core primitives, consensus sheaves, zero-trust delegation,
event sourcing brokers, and cluster topology mesh.
"""

from .cluster_topology import ClusterExceptionEnclave, DistributedClusterMesh
from .engine import G3DistributedCompilerEngine
from .event_broker import DistributedEventBroker
from .models import (
    ClusterNodeMetadata,
    ClusterThermodynamicAudit,
    DistributedCapabilityToken,
    DistributedEvent,
    EventType,
    NodeHealth,
    NodeRole,
    SheafSection,
)
from .sheaf_consensus import SheafConsensusEngine
from .zero_trust_mesh import DistributedCapabilityAuthority

from .observability import (
    OTelSpan,
    ProductionObservabilityExporter,
    SyntheticSimulationFraudError,
    UserZeroAuditor,
)
from .hlj_gate import (
    HighLevelJettisonCertificate,
    HighLevelJettisonGate,
    JettisonConvergenceError,
)

__all__ = [
    "ClusterExceptionEnclave",
    "ClusterNodeMetadata",
    "ClusterThermodynamicAudit",
    "DistributedCapabilityAuthority",
    "DistributedCapabilityToken",
    "DistributedClusterMesh",
    "DistributedEvent",
    "DistributedEventBroker",
    "EventType",
    "G3DistributedCompilerEngine",
    "NodeHealth",
    "NodeRole",
    "SheafConsensusEngine",
    "SheafSection",
    "OTelSpan",
    "ProductionObservabilityExporter",
    "SyntheticSimulationFraudError",
    "UserZeroAuditor",
    "HighLevelJettisonCertificate",
    "HighLevelJettisonGate",
    "JettisonConvergenceError",
]
