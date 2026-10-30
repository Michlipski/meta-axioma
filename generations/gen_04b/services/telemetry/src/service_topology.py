"""Generation 4b Dedicated Non-Loopback Network Topology for Sovereign Telemetry (`[L1-G3B-012]`).

Enforces:
- Sovereign non-loopback LAN IP binding strictly on 192.168.40.40:8446.
- Absolute rejection of loopback bindings (host-local, loopback subnets, IPv6 loopback, all-zeros).
- Dedicated inter-service communication channels connecting Telemetry with Research, Builder, Audit, and Governance.
- Fail-closed partition policy: upon network partition, inter-service channel dispatch fails closed.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from enum import Enum
import json
import time
from typing import Any, Dict, List, Optional

from .domain_models import (
    assert_non_loopback,
    TelemetryDomainInvariantViolation,
    TelemetryTopologyState,
)


class PartitionPolicy(str, Enum):
    """Network partition tolerance policy."""
    FAIL_CLOSED = "FAIL_CLOSED"
    DEGRADED_LOCAL = "DEGRADED_LOCAL"


class NetworkPartitionError(Exception):
    """Raised when an inter-service channel operation fails under fail-closed partition policy."""
    pass


@dataclass
class TelemetryChannel:
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
            raise TelemetryDomainInvariantViolation("channel_id must not be empty.")
        if not self.channel_name:
            raise TelemetryDomainInvariantViolation("channel_name must not be empty.")
        assert_non_loopback(self.source_endpoint, f"TelemetryChannel '{self.channel_name}' source")
        assert_non_loopback(self.target_endpoint, f"TelemetryChannel '{self.channel_name}' target")


class TelemetryServiceTopology:
    """Manages Sovereign Telemetry network topology, dedicated channels, and non-loopback framing."""

    DEFAULT_NODE_IP: str = "192.168.40.40"
    DEFAULT_PORT: int = 8446

    DEDICATED_CHANNELS = [
        "channel_research_telemetry",
        "channel_builder_telemetry",
        "channel_audit_telemetry",
        "channel_governance_telemetry",
        "channel_merkle_attestation",
    ]

    def __init__(
        self,
        node_ip: str = DEFAULT_NODE_IP,
        port: int = DEFAULT_PORT,
        partition_policy: PartitionPolicy = PartitionPolicy.FAIL_CLOSED,
    ) -> None:
        assert_non_loopback(f"{node_ip}:{port}", "TelemetryServiceTopology initialization")

        self.node_ip = node_ip
        self.port = port
        self.endpoint = f"{node_ip}:{port}"
        self.partition_policy = partition_policy
        self.is_partitioned: bool = False

        self._channels: Dict[str, TelemetryChannel] = self._init_channels()

    def _init_channels(self) -> Dict[str, TelemetryChannel]:
        channels = {
            "channel_research_telemetry": TelemetryChannel(
                channel_id="chan_tel_01_research",
                channel_name="channel_research_telemetry",
                source_endpoint="192.168.40.10:8440",
                target_endpoint=self.endpoint,
                protocol="OTEL_TELEMETRY_V1",
            ),
            "channel_builder_telemetry": TelemetryChannel(
                channel_id="chan_tel_02_builder",
                channel_name="channel_builder_telemetry",
                source_endpoint="192.168.40.20:8442",
                target_endpoint=self.endpoint,
                protocol="OTEL_TELEMETRY_V1",
            ),
            "channel_audit_telemetry": TelemetryChannel(
                channel_id="chan_tel_03_audit",
                channel_name="channel_audit_telemetry",
                source_endpoint="192.168.40.30:8444",
                target_endpoint=self.endpoint,
                protocol="OTEL_TELEMETRY_V1",
            ),
            "channel_governance_telemetry": TelemetryChannel(
                channel_id="chan_tel_04_gov",
                channel_name="channel_governance_telemetry",
                source_endpoint="192.168.40.50:8448",
                target_endpoint=self.endpoint,
                protocol="GOV_ATTESTATION_V1",
            ),
            "channel_merkle_attestation": TelemetryChannel(
                channel_id="chan_tel_05_merkle",
                channel_name="channel_merkle_attestation",
                source_endpoint=self.endpoint,
                target_endpoint="192.168.40.254:8450",
                protocol="MERKLE_WITNESS_V1",
            ),
        }
        for ch in channels.values():
            ch.validate_invariants()
        return channels

    def simulate_partition(self, is_partitioned: bool = True) -> None:
        """Simulates a network partition condition across sovereign channels."""
        self.is_partitioned = is_partitioned
        for ch in self._channels.values():
            ch.is_active = not is_partitioned

    def encode_frame(self, message: Dict[str, Any]) -> bytes:
        """Encodes payload into framed byte sequence with length prefix."""
        payload_bytes = json.dumps(message, sort_keys=True).encode("utf-8")
        length_prefix = len(payload_bytes).to_bytes(4, byteorder="big")
        return length_prefix + payload_bytes

    def decode_frame(self, frame: bytes) -> Dict[str, Any]:
        """Decodes framed byte sequence."""
        if len(frame) < 4:
            raise TelemetryDomainInvariantViolation("Frame too short for length prefix.")
        length = int.from_bytes(frame[:4], byteorder="big")
        if len(frame) < 4 + length:
            raise TelemetryDomainInvariantViolation("Incomplete frame buffer.")
        payload_bytes = frame[4 : 4 + length]
        return json.loads(payload_bytes.decode("utf-8"))

    def send_message(self, channel_name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Dispatches an inter-service message over a dedicated sovereign channel."""
        if self.is_partitioned:
            if self.partition_policy == PartitionPolicy.FAIL_CLOSED:
                raise NetworkPartitionError(
                    f"Inter-service dispatch on '{channel_name}' blocked: Network partition active (FAIL_CLOSED)."
                )

        if channel_name not in self._channels:
            raise TelemetryDomainInvariantViolation(f"Unknown channel: '{channel_name}'.")

        ch = self._channels[channel_name]
        if not ch.is_active:
            raise NetworkPartitionError(f"Channel '{channel_name}' is inactive.")

        frame = self.encode_frame(payload)
        ch.bytes_transmitted += len(frame)
        ch.message_count += 1

        return {
            "channel": channel_name,
            "status": "DISPATCHED",
            "bytes": len(frame),
            "timestamp_ms": int(time.time() * 1000),
        }

    def get_channel(self, channel_name: str) -> Optional[TelemetryChannel]:
        return self._channels.get(channel_name)

    def get_all_channels(self) -> Dict[str, Dict[str, Any]]:
        return {
            name: {
                "channel_id": ch.channel_id,
                "source": ch.source_endpoint,
                "target": ch.target_endpoint,
                "protocol": ch.protocol,
                "is_active": ch.is_active,
                "bytes_transmitted": ch.bytes_transmitted,
                "message_count": ch.message_count,
            }
            for name, ch in self._channels.items()
        }
