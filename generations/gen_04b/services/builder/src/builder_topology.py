"""Generation 4b Dedicated Non-Loopback Network Topology (`[L1-G3B-012]`).

Enforces:
- Sovereign non-loopback LAN IP binding on 192.168.40.20:8442.
- Absolute rejection of loopback bindings (127.0.0.1, localhost, ::1, 0.0.0.0).
- 8 dedicated inter-service channels connecting Builder with Research, Audit, Telemetry, Governance, etc.
- Fail-closed partition policy: upon network partition or channel disruption, all inter-service operations fail-closed.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
import hashlib
import time
from typing import Any, Dict, List, Optional, Set, Tuple

from .domain_models import DomainInvariantViolation


class PartitionPolicy(str, Enum):
    """Network partition tolerance policy."""
    FAIL_CLOSED = "FAIL_CLOSED"
    DEGRADED_LOCAL = "DEGRADED_LOCAL"


class NetworkPartitionError(Exception):
    """Raised when an inter-service channel operation fails under fail-closed partition policy."""
    pass


@dataclass
class InterServiceChannel:
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
            raise DomainInvariantViolation("channel_id must not be empty.")
        if not self.channel_name:
            raise DomainInvariantViolation("channel_name must not be empty.")

        # Non-loopback check on source and target
        for ep in (self.source_endpoint, self.target_endpoint):
            ip = ep.split(":")[0].strip()
            if ip.startswith("127.") or ip in ("localhost", "::1", "0.0.0.0"):
                raise DomainInvariantViolation(
                    f"[L1-G3B-012 Violation] Prohibited loopback endpoint '{ep}' in channel '{self.channel_name}'."
                )


class BuilderTopologyManager:
    """Manages builder network topology, 8 dedicated channels, and fail-closed partition enforcement."""

    DEFAULT_BUILDER_IP: str = "192.168.40.20"
    DEFAULT_BUILDER_PORT: int = 8442

    DEDICATED_CHANNEL_NAMES: List[str] = [
        "channel_research_deliverables",
        "channel_rfc_petitions",
        "channel_audit_interception",
        "channel_telemetry_stream",
        "channel_governance_veto",
        "channel_merkle_attestation",
        "channel_quine_crucible_isolation",
        "channel_operator_hud",
    ]

    def __init__(
        self,
        node_ip: str = DEFAULT_BUILDER_IP,
        port: int = DEFAULT_BUILDER_PORT,
        partition_policy: PartitionPolicy = PartitionPolicy.FAIL_CLOSED,
    ):
        ip_clean = node_ip.strip()
        if ":" in ip_clean and not ip_clean.startswith("::"):
            ip_clean = ip_clean.split(":")[0].strip()
        if ip_clean.startswith("127.") or ip_clean in ("localhost", "::1", "0.0.0.0") or "::1" in node_ip:
            raise DomainInvariantViolation(
                f"[L1-G3B-012 Violation] Prohibited loopback binding '{node_ip}' for BuilderTopologyManager."
            )

        self.node_ip = node_ip
        self.port = port
        self.endpoint = f"{node_ip}:{port}"
        self.partition_policy = partition_policy
        self.is_partitioned: bool = False

        # Initialize the 8 dedicated inter-service channels
        self._channels: Dict[str, InterServiceChannel] = self._init_dedicated_channels()

    def _init_dedicated_channels(self) -> Dict[str, InterServiceChannel]:
        channels: Dict[str, InterServiceChannel] = {
            "channel_research_deliverables": InterServiceChannel(
                channel_id="chan_01_res_deliv",
                channel_name="channel_research_deliverables",
                source_endpoint="192.168.40.10:8440",
                target_endpoint=self.endpoint,
                protocol="DELIVERABLE_INGESTION_V1",
            ),
            "channel_rfc_petitions": InterServiceChannel(
                channel_id="chan_02_rfc_pet",
                channel_name="channel_rfc_petitions",
                source_endpoint=self.endpoint,
                target_endpoint="192.168.40.10:8440",
                protocol="RFC_ASYNC_NEGOTIATION_V1",
            ),
            "channel_audit_interception": InterServiceChannel(
                channel_id="chan_03_audit_int",
                channel_name="channel_audit_interception",
                source_endpoint=self.endpoint,
                target_endpoint="192.168.40.30:8444",
                protocol="PRE_EMISSION_AUDIT_V1",
            ),
            "channel_telemetry_stream": InterServiceChannel(
                channel_id="chan_04_telemetry",
                channel_name="channel_telemetry_stream",
                source_endpoint=self.endpoint,
                target_endpoint="192.168.40.40:8446",
                protocol="LANDAUER_METRIC_STREAM_V1",
            ),
            "channel_governance_veto": InterServiceChannel(
                channel_id="chan_05_gov_veto",
                channel_name="channel_governance_veto",
                source_endpoint="192.168.40.50:8448",
                target_endpoint=self.endpoint,
                protocol="NEGATIVE_AXIOM_VETO_V1",
            ),
            "channel_merkle_attestation": InterServiceChannel(
                channel_id="chan_06_merkle_att",
                channel_name="channel_merkle_attestation",
                source_endpoint=self.endpoint,
                target_endpoint="192.168.40.40:8446",
                protocol="MERKLE_ROOT_SEAL_V1",
            ),
            "channel_quine_crucible_isolation": InterServiceChannel(
                channel_id="chan_07_quine_iso",
                channel_name="channel_quine_crucible_isolation",
                source_endpoint=self.endpoint,
                target_endpoint="192.168.40.60:8450",
                protocol="SANDBOX_SELF_HOSTING_V1",
            ),
            "channel_operator_hud": InterServiceChannel(
                channel_id="chan_08_hud",
                channel_name="channel_operator_hud",
                source_endpoint=self.endpoint,
                target_endpoint="192.168.40.20:8080",
                protocol="LOCAL_HUD_SSE_V1",
            ),
        }

        # Validate all channels at startup
        for ch in channels.values():
            ch.validate_invariants()

        return channels

    def get_channel(self, channel_name: str) -> InterServiceChannel:
        """Retrieves a dedicated channel by name."""
        if channel_name not in self._channels:
            raise KeyError(f"Channel '{channel_name}' not found. Available: {list(self._channels.keys())}")
        return self._channels[channel_name]

    def list_channels(self) -> List[InterServiceChannel]:
        """Returns all 8 dedicated channels."""
        return list(self._channels.values())

    def simulate_partition(self, partitioned: bool = True) -> None:
        """Simulates network partition / split-brain conditions."""
        self.is_partitioned = partitioned
        for ch in self._channels.values():
            ch.is_active = not partitioned

    def transmit(self, channel_name: str, payload_bytes: bytes) -> bool:
        """Transmits payload over designated channel enforcing fail-closed partition policy."""
        if self.is_partitioned:
            if self.partition_policy == PartitionPolicy.FAIL_CLOSED:
                raise NetworkPartitionError(
                    f"Fail-closed partition policy active: transmission on '{channel_name}' strictly blocked."
                )
            return False

        ch = self.get_channel(channel_name)
        if not ch.is_active:
            raise NetworkPartitionError(f"Channel '{channel_name}' is inactive.")

        ch.bytes_transmitted += len(payload_bytes)
        ch.message_count += 1
        return True
