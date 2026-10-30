"""Dedicated Non-Loopback Network Topology for Sovereign Governance (`soc_g4b_governance`).

Enforces:
- Invariant [L1-G3B-012]: Dedicated Non-Loopback Network Topology.
- Sovereign non-loopback LAN IP binding strictly on 192.168.40.50:8448.
- Absolute rejection of loopback bindings (host-local prefixes, loopback aliases, all-zeros).
- Standardized cluster mesh topology mapping:
  - Research:   192.168.40.10:8440
  - Builder:    192.168.40.20:8442
  - Audit:      192.168.40.30:8444
  - Telemetry:  192.168.40.40:8446
  - Governance: 192.168.40.50:8448
- Fail-closed partition policy for safety enclave containment.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from enum import Enum
import hashlib
import time
from typing import Any, Dict, List, Optional, Set

from .domain_models import (
    GovernanceDomainInvariantViolation,
    assert_non_loopback,
)


class PartitionPolicy(str, Enum):
    """Network partition tolerance policy."""
    FAIL_CLOSED = "FAIL_CLOSED"
    DEGRADED_LOCAL = "DEGRADED_LOCAL"


class NetworkPartitionError(GovernanceDomainInvariantViolation):
    """Raised when an inter-service channel operation fails under fail-closed partition policy."""
    pass


@dataclass
class GovernanceChannel:
    """A verified inter-service communication channel across sovereign enclaves."""
    channel_id: str
    channel_name: str
    source_endpoint: str
    target_endpoint: str
    protocol: str
    is_active: bool = True
    bytes_transmitted: int = 0
    message_count: int = 0

    def validate_invariants(self) -> None:
        if not self.channel_id:
            raise GovernanceDomainInvariantViolation("channel_id must not be empty.")
        if not self.channel_name:
            raise GovernanceDomainInvariantViolation("channel_name must not be empty.")
        assert_non_loopback(self.source_endpoint, f"Channel '{self.channel_name}' source")
        assert_non_loopback(self.target_endpoint, f"Channel '{self.channel_name}' target")


class GovernanceServiceTopology:
    """Manages Sovereign Governance network topology, dedicated channels, and partition policies."""

    DEFAULT_GOVERNANCE_IP: str = "192.168.40.50"
    DEFAULT_GOVERNANCE_PORT: int = 8448

    STANDARD_CLUSTER_PEERS: Dict[str, str] = {
        "research": "192.168.40.10:8440",
        "builder": "192.168.40.20:8442",
        "audit": "192.168.40.30:8444",
        "telemetry": "192.168.40.40:8446",
        "governance": "192.168.40.50:8448",
    }

    def __init__(
        self,
        node_ip: str = DEFAULT_GOVERNANCE_IP,
        port: int = DEFAULT_GOVERNANCE_PORT,
        partition_policy: PartitionPolicy = PartitionPolicy.FAIL_CLOSED,
    ) -> None:
        endpoint = f"{node_ip}:{port}"
        assert_non_loopback(endpoint, "GovernanceServiceTopology initialization")

        self.node_ip = node_ip
        self.port = port
        self.endpoint = endpoint
        self.partition_policy = partition_policy
        self.is_partitioned: bool = False

        self._peers: Dict[str, str] = dict(self.STANDARD_CLUSTER_PEERS)
        self._channels: Dict[str, GovernanceChannel] = self._init_channels()

    def _init_channels(self) -> Dict[str, GovernanceChannel]:
        channels: Dict[str, GovernanceChannel] = {
            "channel_audit_surveillance": GovernanceChannel(
                channel_id="chan_gov_01_audit",
                channel_name="channel_audit_surveillance",
                source_endpoint=self.endpoint,
                target_endpoint=self._peers["audit"],
                protocol="AXIOM_SURVEILLANCE_V1",
            ),
            "channel_builder_rfc": GovernanceChannel(
                channel_id="chan_gov_02_builder",
                channel_name="channel_builder_rfc",
                source_endpoint=self._peers["builder"],
                target_endpoint=self.endpoint,
                protocol="RFC_ADJUDICATION_V1",
            ),
            "channel_research_invariants": GovernanceChannel(
                channel_id="chan_gov_03_research",
                channel_name="channel_research_invariants",
                source_endpoint=self._peers["research"],
                target_endpoint=self.endpoint,
                protocol="INVARIANT_LINEAGE_V1",
            ),
            "channel_telemetry_ledger": GovernanceChannel(
                channel_id="chan_gov_04_telemetry",
                channel_name="channel_telemetry_ledger",
                source_endpoint=self.endpoint,
                target_endpoint=self._peers["telemetry"],
                protocol="TELEMETRY_LEDGER_STREAM_V1",
            ),
            "channel_quarantine_enclave": GovernanceChannel(
                channel_id="chan_gov_05_quarantine",
                channel_name="channel_quarantine_enclave",
                source_endpoint=self.endpoint,
                target_endpoint="192.168.40.241:8448",
                protocol="ENCLAVE_ISOLATION_V1",
            ),
        }
        for ch in channels.values():
            ch.validate_invariants()
        return channels

    def get_peer_endpoint(self, service_name: str) -> str:
        """Retrieves the dedicated endpoint for a peer service."""
        if service_name not in self._peers:
            raise GovernanceDomainInvariantViolation(f"Peer service '{service_name}' not in cluster topology.")
        ep = self._peers[service_name]
        assert_non_loopback(ep, f"Peer service '{service_name}'")
        return ep

    def get_channel(self, channel_name: str) -> GovernanceChannel:
        """Retrieves a dedicated channel by name, honoring fail-closed partitions."""
        if self.is_partitioned and self.partition_policy == PartitionPolicy.FAIL_CLOSED:
            raise NetworkPartitionError(
                f"Fail-closed partition policy blocks access to channel '{channel_name}'."
            )
        if channel_name not in self._channels:
            raise GovernanceDomainInvariantViolation(f"Channel '{channel_name}' is not registered.")
        return self._channels[channel_name]

    def transmit(self, channel_name: str, payload_bytes: int) -> None:
        """Simulates byte transmission across an inter-service channel."""
        ch = self.get_channel(channel_name)
        if not ch.is_active:
            raise NetworkPartitionError(f"Channel '{channel_name}' is currently inactive.")
        ch.bytes_transmitted += payload_bytes
        ch.message_count += 1

    def trigger_partition(self) -> None:
        """Simulates network partition causing fail-closed isolation."""
        self.is_partitioned = True
        for ch in self._channels.values():
            ch.is_active = False

    def heal_partition(self) -> None:
        """Restores network connectivity after a partition."""
        self.is_partitioned = False
        for ch in self._channels.values():
            ch.is_active = True

    def get_cluster_bindings(self) -> List[str]:
        """Returns all registered cluster endpoint bindings."""
        return list(self._peers.values())

    def export_topology_dict(self) -> Dict[str, Any]:
        """Exports a dictionary representation of the cluster topology for auditing."""
        return {
            "service": "soc_g4b_governance",
            "endpoint": self.endpoint,
            "peers": self._peers,
            "is_partitioned": self.is_partitioned,
            "partition_policy": self.partition_policy.value,
            "channels": {
                name: {
                    "id": ch.channel_id,
                    "src": ch.source_endpoint,
                    "tgt": ch.target_endpoint,
                    "active": ch.is_active,
                    "bytes": ch.bytes_transmitted,
                    "messages": ch.message_count,
                }
                for name, ch in self._channels.items()
            },
        }
