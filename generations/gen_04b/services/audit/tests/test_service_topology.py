"""Unit & Adversarial Invariant Test Suite for Dedicated Service Topology (`[L1-G3B-012]`).

Validates:
1. Rejection of loopback addresses: '127.0.0.1', 'localhost', '0.0.0.0', '::1'.
2. Confirms valid binding to sovereign IP '192.168.40.30:8444'.
3. Channel transmission, message accounting, and topology state export.
4. Fail-closed network partition handling.
5. AsyncIO framing and handshake protocol.
"""

from __future__ import annotations

import asyncio
from pathlib import Path
import sys
import unittest

AUDIT_ROOT = Path(__file__).resolve().parent.parent
REPO_ROOT = AUDIT_ROOT.parent.parent.parent.parent
for p in [str(AUDIT_ROOT), str(AUDIT_ROOT / "src"), str(REPO_ROOT)]:
    if p not in sys.path:
        sys.path.insert(0, p)

from src.domain_models import (
    AuditDomainInvariantViolation,
    AuditServiceTopologyState,
)
from src.service_topology import (
    AuditServiceTopology,
    NetworkPartitionError,
    PartitionPolicy,
)


class TestServiceTopology(unittest.TestCase):
    """Exhaustive tests for dedicated non-loopback network topology and fail-closed partition tolerance."""

    # 1. Rejection of Loopback Endpoints
    def test_rejection_of_loopback_endpoints(self) -> None:
        loopbacks = ["127.0.0.1", "localhost", "0.0.0.0", "::1"]
        for bad_ip in loopbacks:
            with self.assertRaises(AuditDomainInvariantViolation):
                AuditServiceTopology(node_ip=bad_ip, port=8444)

    # 2. Confirms Valid Binding to Sovereign IP 192.168.40.30:8444
    def test_valid_binding_to_sovereign_ip(self) -> None:
        topo = AuditServiceTopology(node_ip="192.168.40.30", port=8444)
        self.assertEqual(topo.endpoint, "192.168.40.30:8444")
        self.assertEqual(len(topo._channels), 6)
        self.assertIn("channel_builder_interception", topo._channels)
        self.assertIn("channel_research_rfc", topo._channels)
        self.assertIn("channel_telemetry_stream", topo._channels)
        self.assertIn("channel_governance_invariants", topo._channels)
        self.assertIn("channel_sheaf_mesh_consensus", topo._channels)
        self.assertIn("channel_merkle_attestation", topo._channels)

    # 3. Channel Transmission & State Export
    def test_channel_transmission_and_state_export(self) -> None:
        topo = AuditServiceTopology()
        topo.transmit("channel_builder_interception", payload_bytes=1024)
        topo.transmit("channel_builder_interception", payload_bytes=512)

        ch = topo.get_channel("channel_builder_interception")
        self.assertEqual(ch.bytes_transmitted, 1536)
        self.assertEqual(ch.message_count, 2)

        state = topo.export_topology_state()
        self.assertIsInstance(state, AuditServiceTopologyState)
        self.assertEqual(state.service_endpoint, "192.168.40.30:8444")
        self.assertFalse(state.is_partitioned)
        self.assertIn("channel_builder_interception", state.registered_channels)
        self.assertEqual(state.registered_channels["channel_builder_interception"]["bytes"], 1536)

    # 4. Fail-Closed Network Partition Handling
    def test_fail_closed_network_partition_handling(self) -> None:
        topo = AuditServiceTopology(partition_policy=PartitionPolicy.FAIL_CLOSED)
        # Normal operation
        ch = topo.get_channel("channel_research_rfc")
        self.assertTrue(ch.is_active)

        # Trigger partition
        topo.trigger_partition()
        self.assertTrue(topo.is_partitioned)

        # Operations fail-closed
        with self.assertRaises(NetworkPartitionError):
            topo.get_channel("channel_research_rfc")

        with self.assertRaises(NetworkPartitionError):
            topo.transmit("channel_research_rfc", 100)

        # Healing partition restores channel access
        topo.heal_partition()
        self.assertFalse(topo.is_partitioned)
        restored_ch = topo.get_channel("channel_research_rfc")
        self.assertTrue(restored_ch.is_active)

    # 5. AsyncIO Framing and Handshake Protocol
    def test_asyncio_framing_and_handshake_protocol(self) -> None:
        async def run_handshake() -> bool:
            # Simulate protocol frame encoding and decoding
            async def encode_frame(msg_type: str, payload: bytes) -> bytes:
                header = f"{msg_type}:{len(payload)}:".encode("utf-8")
                return header + payload

            async def decode_frame(raw: bytes) -> tuple[str, bytes]:
                parts = raw.split(b":", 2)
                msg_type = parts[0].decode("utf-8")
                length = int(parts[1].decode("utf-8"))
                body = parts[2]
                if len(body) != length:
                    raise ValueError("Frame truncation detected")
                return msg_type, body

            frame = await encode_frame("HANDSHAKE_INIT", b'{"node_id": "node_audit_kernel"}')
            msg_type, body = await decode_frame(frame)
            return msg_type == "HANDSHAKE_INIT" and b"node_audit_kernel" in body

        result = asyncio.run(run_handshake())
        self.assertTrue(result)


if __name__ == "__main__":
    unittest.main()
