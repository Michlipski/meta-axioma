"""Generation 4b Dedicated Non-Loopback Network Topology for Sovereign Audit (`[L1-G3B-012]`).

Enforces:
- Sovereign non-loopback LAN IP binding strictly on 192.168.40.30:8444.
- Absolute rejection of loopback bindings (127.0.0.1, localhost, ::1, 0.0.0.0).
- Dedicated inter-service communication channels connecting Audit with Builder, Research, Telemetry, and Governance.
- Fail-closed partition policy: upon network partition or channel disruption, all operations fail-closed.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from enum import Enum
import hashlib
import time
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

from .domain_models import (
    AuditDomainInvariantViolation,
    AuditServiceTopologyState,
    assert_non_loopback,
)


class PartitionPolicy(str, Enum):
    """Network partition tolerance policy."""
    FAIL_CLOSED = "FAIL_CLOSED"
    DEGRADED_LOCAL = "DEGRADED_LOCAL"


class NetworkPartitionError(Exception):
    """Raised when an inter-service channel operation fails under fail-closed partition policy."""
    pass


@dataclass
class AuditChannel:
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
            raise AuditDomainInvariantViolation("channel_id must not be empty.")
        if not self.channel_name:
            raise AuditDomainInvariantViolation("channel_name must not be empty.")
        assert_non_loopback(self.source_endpoint, f"Channel '{self.channel_name}' source")
        assert_non_loopback(self.target_endpoint, f"Channel '{self.channel_name}' target")


class AuditServiceTopology:
    """Manages Sovereign Audit network topology, dedicated channels, and fail-closed partition enforcement."""

    DEFAULT_AUDIT_IP: str = "192.168.40.30"
    DEFAULT_AUDIT_PORT: int = 8444

    DEDICATED_CHANNELS: List[str] = [
        "channel_builder_interception",
        "channel_research_rfc",
        "channel_telemetry_stream",
        "channel_governance_invariants",
        "channel_sheaf_mesh_consensus",
        "channel_merkle_attestation",
    ]

    def __init__(
        self,
        node_ip: str = DEFAULT_AUDIT_IP,
        port: int = DEFAULT_AUDIT_PORT,
        partition_policy: PartitionPolicy = PartitionPolicy.FAIL_CLOSED,
    ) -> None:
        assert_non_loopback(f"{node_ip}:{port}", "AuditServiceTopology initialization")

        self.node_ip = node_ip
        self.port = port
        self.endpoint = f"{node_ip}:{port}"
        self.partition_policy = partition_policy
        self.is_partitioned: bool = False
        self._server: Optional[asyncio.Server] = None

        self._channels: Dict[str, AuditChannel] = self._init_channels()

    def _init_channels(self) -> Dict[str, AuditChannel]:
        channels: Dict[str, AuditChannel] = {
            "channel_builder_interception": AuditChannel(
                channel_id="chan_aud_01_builder",
                channel_name="channel_builder_interception",
                source_endpoint="192.168.40.20:8443",
                target_endpoint=self.endpoint,
                protocol="PRE_EMISSION_AUDIT_V1",
            ),
            "channel_research_rfc": AuditChannel(
                channel_id="chan_aud_02_research",
                channel_name="channel_research_rfc",
                source_endpoint=self.endpoint,
                target_endpoint="192.168.40.10:8442",
                protocol="RFC_ASYNC_NEGOTIATION_V1",
            ),
            "channel_telemetry_stream": AuditChannel(
                channel_id="chan_aud_03_telemetry",
                channel_name="channel_telemetry_stream",
                source_endpoint=self.endpoint,
                target_endpoint="192.168.40.40:8446",
                protocol="LANDAUER_METRIC_STREAM_V1",
            ),
            "channel_governance_invariants": AuditChannel(
                channel_id="chan_aud_04_governance",
                channel_name="channel_governance_invariants",
                source_endpoint="192.168.40.50:8448",
                target_endpoint=self.endpoint,
                protocol="NEGATIVE_AXIOM_VETO_V1",
            ),
            "channel_sheaf_mesh_consensus": AuditChannel(
                channel_id="chan_aud_05_sheaf",
                channel_name="channel_sheaf_mesh_consensus",
                source_endpoint=self.endpoint,
                target_endpoint=self.endpoint,
                protocol="SHEAF_QUORUM_PEER_V1",
            ),
            "channel_merkle_attestation": AuditChannel(
                channel_id="chan_aud_06_attestation",
                channel_name="channel_merkle_attestation",
                source_endpoint=self.endpoint,
                target_endpoint="192.168.40.40:8446",
                protocol="MERKLE_ROOT_SEAL_V1",
            ),
        }
        for ch in channels.values():
            ch.validate_invariants()
        return channels

    def get_channel(self, channel_name: str) -> AuditChannel:
        """Retrieves a dedicated channel by name."""
        if self.is_partitioned and self.partition_policy == PartitionPolicy.FAIL_CLOSED:
            raise NetworkPartitionError(
                f"Fail-closed partition policy blocks access to channel '{channel_name}'."
            )
        if channel_name not in self._channels:
            raise AuditDomainInvariantViolation(f"Channel '{channel_name}' is not registered.")
        return self._channels[channel_name]

    def transmit(self, channel_name: str, payload_bytes: int) -> None:
        """Simulates byte transmission across a channel."""
        ch = self.get_channel(channel_name)
        if not ch.is_active:
            raise NetworkPartitionError(f"Channel '{channel_name}' is inactive.")
        ch.bytes_transmitted += payload_bytes
        ch.message_count += 1

    def trigger_partition(self) -> None:
        """Simulates network partition event causing fail-closed behavior."""
        self.is_partitioned = True
        for ch in self._channels.values():
            ch.is_active = False

    def heal_partition(self) -> None:
        """Restores connectivity after partition."""
        self.is_partitioned = False
        for ch in self._channels.values():
            ch.is_active = True

    def export_topology_state(self) -> AuditServiceTopologyState:
        """Exports typed state snapshot of the network topology."""
        channels_dict = {
            name: {
                "id": ch.channel_id,
                "src": ch.source_endpoint,
                "tgt": ch.target_endpoint,
                "active": ch.is_active,
                "bytes": ch.bytes_transmitted,
                "messages": ch.message_count,
            }
            for name, ch in self._channels.items()
        }
        state = AuditServiceTopologyState(
            node_id="node_audit_kernel",
            service_endpoint=self.endpoint,
            builder_endpoint="192.168.40.20:8443",
            research_endpoint="192.168.40.10:8442",
            active_peers=[
                "node_hermetic_sentry",
                "node_smt_oracle",
                "node_chaos_adversary",
                "node_merkle_sheaf",
            ],
            is_partitioned=self.is_partitioned,
            registered_channels=channels_dict,
        )
        state.validate_invariants()
        return state
