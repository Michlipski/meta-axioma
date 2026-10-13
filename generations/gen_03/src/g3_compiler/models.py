"""Core Typed AST Models and Mathematical Contracts for Generation 3 (G3).

Defines distributed system contracts for:
- L1-G3-001: Topological Sheaf Consensus & Partition Coherence
- L1-G3-002: Zero-Ambient Distributed Capability Mesh
- L1-G3-003: Distributed Blast Radius Containment & Enclaves
- L1-G3-004: Functorial Event Sourcing & CQRS Duality
- L1-G3-005: The High-Level Jettison Convergence
"""

from __future__ import annotations

import enum
import time
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple


class NodeRole(str, enum.Enum):
    INGRESS_GATEWAY = "INGRESS_GATEWAY"
    CONSENSUS_LEADER = "CONSENSUS_LEADER"
    CONSENSUS_FOLLOWER = "CONSENSUS_FOLLOWER"
    EVENT_BROKER = "EVENT_BROKER"
    COMPUTE_WORKER = "COMPUTE_WORKER"


class NodeHealth(str, enum.Enum):
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    PARTITIONED = "PARTITIONED"
    QUARANTINED = "QUARANTINED"


class EventType(str, enum.Enum):
    NODE_JOINED = "NODE_JOINED"
    NODE_HEARTBEAT = "NODE_HEARTBEAT"
    PARTITION_DETECTED = "PARTITION_DETECTED"
    PARTITION_RECONCILED = "PARTITION_RECONCILED"
    CAPABILITY_ISSUED = "CAPABILITY_ISSUED"
    TRANSACTION_COMMITTED = "TRANSACTION_COMMITTED"
    TASK_DISPATCHED = "TASK_DISPATCHED"
    TASK_COMPLETED = "TASK_COMPLETED"
    ENCLAVE_HEALED = "ENCLAVE_HEALED"
    ROLLBACK_EXECUTED = "ROLLBACK_EXECUTED"


@dataclass(frozen=True)
class DistributedCapabilityToken:
    """Introspectable, cryptographically signed capability token (L1-G3-002)."""
    token_id: str
    issuer_node_id: str
    target_service: str
    allowed_actions: Tuple[str, ...]
    signature_hmac: str
    issued_at: float
    expires_at: float
    delegated_from: Optional[str] = None
    attenuated_scope: Tuple[str, ...] = ()

    def is_valid(self, current_time: Optional[float] = None) -> bool:
        now = current_time or time.time()
        return now < self.expires_at

    def allows(self, action: str) -> bool:
        if "*" in self.allowed_actions:
            return True
        return action in self.allowed_actions

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class SheafSection:
    """Local state section over an open cover component U_i (L1-G3-001)."""
    node_id: str
    open_cover_id: str
    version: int
    data: Dict[str, Any]
    state_hash: str
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class DistributedEvent:
    """Immutable append-only event in the distributed log (L1-G3-004)."""
    event_id: str
    event_type: EventType
    origin_node_id: str
    payload: Dict[str, Any]
    capability_token_id: str
    timestamp: float = field(default_factory=time.time)
    vector_clock: Dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["event_type"] = self.event_type.value
        return d


@dataclass
class ClusterNodeMetadata:
    """Heartbeat and topology metadata for a distributed cluster node."""
    node_id: str
    role: NodeRole
    port: int
    health: NodeHealth = NodeHealth.HEALTHY
    assigned_cover_id: str = "cover_global"
    last_heartbeat: float = field(default_factory=time.time)
    erased_bits: float = 0.0
    joules_dissipated: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["role"] = self.role.value
        d["health"] = self.health.value
        return d


@dataclass
class ClusterThermodynamicAudit:
    """Cluster-wide Landauer dissipation and entropy budget accounting."""
    total_cluster_erased_bits: float
    total_joules_dissipated: float
    active_nodes_count: int
    partition_reconciliation_count: int
    thermal_compliance_passed: bool
