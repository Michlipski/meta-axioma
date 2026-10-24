"""Generation 3b Universal Distributed Topology Intermediate Representation (IR).

Enforces:
- [L1-G3B-008] Distributed Topology & Consensus as First-Class IR:
  Models cluster nodes, network channels, interface bindings, and Sheaf-Quorum consensus.
- [L1-G3B-012] The Topological Fidelity Invariant (Boundary Realism Over Loopback Convenience):
  Bans the validation of cross-device or multi-node distributed contracts over single-machine
  loopback (127.0.0.1, localhost, ::1). Multi-node distributed systems must declare routable
  or virtual subnet interfaces and reject loopback shortcuts.
- Lossless serialization: f^-1(f(x)) == x.
"""

from dataclasses import dataclass, field
from enum import Enum
import json
from typing import List, Dict, Any, Optional, Set


class NodeRole(str, Enum):
    """The architectural role of a distributed topology node."""
    ORCHESTRATOR = "orchestrator"
    WORKER = "worker"
    STORAGE_LEAF = "storage_leaf"
    GATEWAY = "gateway"
    VERIFIER = "verifier"
    COMPILER_CORE = "compiler_core"


class ChannelType(str, Enum):
    """Transport protocol or medium of a network channel."""
    RPC = "rpc"
    STREAM = "stream"
    GOSSIP = "gossip"
    EVENT_BUS = "event_bus"
    INTER_PROCESS = "inter_process"


class ConsensusProtocol(str, Enum):
    """Consensus or replication protocol."""
    SHEAF_QUORUM = "sheaf_quorum"
    RAFT = "raft"
    CRDT_GOSSIP = "crdt_gossip"
    LOCAL_AUTHORITY = "local_authority"


class TopologicalLoopbackViolation(Exception):
    """Raised when a multi-node distributed topology improperly defaults to loopback addresses."""
    pass


@dataclass
class TopologyNode:
    """A computational node in the distributed topology."""
    node_id: str
    role: NodeRole
    host_interface: str  # E.g. "192.168.1.50", "cluster.local", "node-1.axiom"
    port: int
    capabilities: List[str] = field(default_factory=list)
    memory_mb_limit: int = 1024

    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_id": self.node_id,
            "role": self.role.value,
            "host_interface": self.host_interface,
            "port": self.port,
            "capabilities": list(self.capabilities),
            "memory_mb_limit": self.memory_mb_limit,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TopologyNode":
        return cls(
            node_id=data["node_id"],
            role=NodeRole(data.get("role", "worker")),
            host_interface=data["host_interface"],
            port=data.get("port", 8080),
            capabilities=data.get("capabilities", []),
            memory_mb_limit=data.get("memory_mb_limit", 1024),
        )


@dataclass
class NetworkChannel:
    """A communication link between two nodes in the topology."""
    channel_id: str
    source_node_id: str
    target_node_id: str
    channel_type: ChannelType
    port: int
    latency_ms_budget: int = 50
    tls_enforced: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "channel_id": self.channel_id,
            "source_node_id": self.source_node_id,
            "target_node_id": self.target_node_id,
            "channel_type": self.channel_type.value,
            "port": self.port,
            "latency_ms_budget": self.latency_ms_budget,
            "tls_enforced": self.tls_enforced,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "NetworkChannel":
        return cls(
            channel_id=data["channel_id"],
            source_node_id=data["source_node_id"],
            target_node_id=data["target_node_id"],
            channel_type=ChannelType(data.get("channel_type", "rpc")),
            port=data.get("port", 8080),
            latency_ms_budget=data.get("latency_ms_budget", 50),
            tls_enforced=data.get("tls_enforced", True),
        )


@dataclass
class ConsensusContract:
    """Consensus and replication rules across nodes."""
    protocol: ConsensusProtocol = ConsensusProtocol.LOCAL_AUTHORITY
    quorum_fraction: float = 0.67  # e.g. 2/3 supermajority for Byzantine / Sheaf
    heartbeat_interval_ms: int = 1000
    partition_strategy: str = "fail_closed"  # "fail_closed" or "crdt_eventual"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "protocol": self.protocol.value,
            "quorum_fraction": self.quorum_fraction,
            "heartbeat_interval_ms": self.heartbeat_interval_ms,
            "partition_strategy": self.partition_strategy,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ConsensusContract":
        return cls(
            protocol=ConsensusProtocol(data.get("protocol", "local_authority")),
            quorum_fraction=data.get("quorum_fraction", 0.67),
            heartbeat_interval_ms=data.get("heartbeat_interval_ms", 1000),
            partition_strategy=data.get("partition_strategy", "fail_closed"),
        )


@dataclass
class TopologyIR:
    """The Universal Distributed Topology IR.

    Captures nodes, network channels, consensus contracts, and verifies topological fidelity.
    """
    topology_id: str
    nodes: Dict[str, TopologyNode] = field(default_factory=dict)
    channels: List[NetworkChannel] = field(default_factory=list)
    consensus: ConsensusContract = field(default_factory=ConsensusContract)

    LOOPBACK_HOSTS = {"127.0.0.1", "localhost", "::1", "0.0.0.0"}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "topology_id": self.topology_id,
            "nodes": {k: v.to_dict() for k, v in self.nodes.items()},
            "channels": [c.to_dict() for c in self.channels],
            "consensus": self.consensus.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TopologyIR":
        return cls(
            topology_id=data["topology_id"],
            nodes={k: TopologyNode.from_dict(v) for k, v in data.get("nodes", {}).items()},
            channels=[NetworkChannel.from_dict(c) for c in data.get("channels", [])],
            consensus=ConsensusContract.from_dict(data.get("consensus", {})),
        )

    def to_json(self, indent: int = 2) -> str:
        """Lossless JSON serialization."""
        return json.dumps(self.to_dict(), indent=indent, sort_keys=True)

    @classmethod
    def from_json(cls, json_str: str) -> "TopologyIR":
        """Lossless JSON deserialization: f^-1(f(x)) == x."""
        return cls.from_dict(json.loads(json_str))

    def add_node(self, node: TopologyNode) -> "TopologyIR":
        self.nodes[node.node_id] = node
        return self

    def add_channel(self, channel: NetworkChannel) -> "TopologyIR":
        self.channels.append(channel)
        return self

    def validate_topological_fidelity(self, allow_single_node: bool = False) -> List[str]:
        """Enforces [L1-G3B-012] Boundary Realism Over Loopback Convenience:

        - If the topology declares multiple distinct nodes, none of them can be bound to loopback.
        - Channels between distinct nodes cannot point to loopback.
        - All channel source and target nodes must exist in self.nodes.
        """
        errors: List[str] = []
        is_multi_node = len(self.nodes) > 1

        if is_multi_node:
            for nid, node in self.nodes.items():
                host_norm = node.host_interface.strip().lower()
                if host_norm in self.LOOPBACK_HOSTS:
                    msg = (
                        f"[L1-G3B-012 Violation] Multi-node topology '{self.topology_id}' node '{nid}' "
                        f"binds to loopback host '{node.host_interface}'. "
                        f"Boundary realism requires distinct routable or virtual cluster network interfaces."
                    )
                    errors.append(msg)

        # Channel integrity
        for ch in self.channels:
            if ch.source_node_id not in self.nodes:
                errors.append(f"Channel '{ch.channel_id}' source node '{ch.source_node_id}' does not exist.")
            if ch.target_node_id not in self.nodes:
                errors.append(f"Channel '{ch.channel_id}' target node '{ch.target_node_id}' does not exist.")

        return errors

    def assert_topological_fidelity(self, allow_single_node: bool = False):
        """Raises TopologicalLoopbackViolation if [L1-G3B-012] is violated."""
        errs = self.validate_topological_fidelity(allow_single_node=allow_single_node)
        if errs:
            raise TopologicalLoopbackViolation("; ".join(errs))
