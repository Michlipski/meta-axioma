"""Unit and network invariant tests for Sovereign Telemetry Service Topology (`soc_g4b_telemetry`).

Verifies:
- [L1-G3B-012] Dedicated Non-Loopback Network Topology binding strictly on 192.168.40.40:8446.
- Rejection of loopback bindings (127.0.0.1, localhost, ::1, 0.0.0.0).
- Dedicated sovereign inter-service communication channels:
  - channel_research_telemetry
  - channel_builder_telemetry
  - channel_audit_telemetry
  - channel_governance_telemetry
  - channel_merkle_attestation
- Fail-closed network partition policy enforcement (NetworkPartitionError).
- Length-prefixed binary framing encode/decode and buffer corruption detection.
"""

from __future__ import annotations

from pathlib import Path
import sys
import unittest

TEL_ROOT = Path(__file__).resolve().parent.parent
REPO_ROOT = TEL_ROOT.parent.parent.parent.parent
for p in [str(TEL_ROOT), str(REPO_ROOT)]:
    if p not in sys.path:
        sys.path.insert(0, p)

from generations.gen_04b.services.telemetry.src.domain_models import (
    TelemetryDomainInvariantViolation,
)
from generations.gen_04b.services.telemetry.src.service_topology import (
    NetworkPartitionError,
    PartitionPolicy,
    TelemetryChannel,
    TelemetryServiceTopology,
)


class TestTelemetryServiceTopology(unittest.TestCase):
    """Test suite for TelemetryServiceTopology non-loopback bindings and channels."""

    def setUp(self):
        self.topology = TelemetryServiceTopology(
            node_ip="192.168.40.40",
            port=8446,
            partition_policy=PartitionPolicy.FAIL_CLOSED,
        )

    def test_default_topology_binding(self):
        self.assertEqual(self.topology.node_ip, "192.168.40.40")
        self.assertEqual(self.topology.port, 8446)
        self.assertEqual(self.topology.endpoint, "192.168.40.40:8446")
        self.assertFalse(self.topology.is_partitioned)

    def test_prohibited_loopback_bindings(self):
        with self.assertRaises(TelemetryDomainInvariantViolation):
            TelemetryServiceTopology(node_ip="127.0.0.1", port=8446)

        with self.assertRaises(TelemetryDomainInvariantViolation):
            TelemetryServiceTopology(node_ip="localhost", port=8446)

        with self.assertRaises(TelemetryDomainInvariantViolation):
            TelemetryServiceTopology(node_ip="::1", port=8446)

        with self.assertRaises(TelemetryDomainInvariantViolation):
            TelemetryServiceTopology(node_ip="0.0.0.0", port=8446)

    def test_dedicated_channels_initialization(self):
        channels = self.topology.get_all_channels()
        self.assertEqual(len(channels), 5)
        for expected in TelemetryServiceTopology.DEDICATED_CHANNELS:
            self.assertIn(expected, channels)

        # Check endpoints and protocols
        ch_research = self.topology.get_channel("channel_research_telemetry")
        self.assertIsNotNone(ch_research)
        self.assertEqual(ch_research.source_endpoint, "192.168.40.10:8440")
        self.assertEqual(ch_research.target_endpoint, "192.168.40.40:8446")
        self.assertEqual(ch_research.protocol, "OTEL_TELEMETRY_V1")

        ch_merkle = self.topology.get_channel("channel_merkle_attestation")
        self.assertIsNotNone(ch_merkle)
        self.assertEqual(ch_merkle.source_endpoint, "192.168.40.40:8446")
        self.assertEqual(ch_merkle.target_endpoint, "192.168.40.254:8450")
        self.assertEqual(ch_merkle.protocol, "MERKLE_WITNESS_V1")

    def test_frame_encoding_and_decoding(self):
        payload = {"event": "HEARTBEAT", "status": "OK", "timestamp": 123456789}
        framed = self.topology.encode_frame(payload)

        # First 4 bytes are big-endian integer length
        length = int.from_bytes(framed[:4], byteorder="big")
        self.assertEqual(length, len(framed) - 4)

        decoded = self.topology.decode_frame(framed)
        self.assertEqual(decoded, payload)

    def test_frame_decoding_errors(self):
        # Too short for length prefix
        with self.assertRaises(TelemetryDomainInvariantViolation):
            self.topology.decode_frame(b"12")

        # Incomplete buffer
        length_prefix = (100).to_bytes(4, byteorder="big")
        with self.assertRaises(TelemetryDomainInvariantViolation):
            self.topology.decode_frame(length_prefix + b"short_data")

    def test_send_message_happy_path(self):
        payload = {"metric": "p99", "value": 24.5}
        result = self.topology.send_message("channel_research_telemetry", payload)
        self.assertEqual(result["channel"], "channel_research_telemetry")
        self.assertEqual(result["status"], "DISPATCHED")
        self.assertGreater(result["bytes"], 0)

        ch = self.topology.get_channel("channel_research_telemetry")
        self.assertEqual(ch.message_count, 1)
        self.assertEqual(ch.bytes_transmitted, result["bytes"])

    def test_send_message_unknown_channel(self):
        with self.assertRaises(TelemetryDomainInvariantViolation):
            self.topology.send_message("channel_unknown_xyz", {"msg": "hello"})

    def test_fail_closed_partition_behavior(self):
        # Simulate network partition
        self.topology.simulate_partition(is_partitioned=True)
        self.assertTrue(self.topology.is_partitioned)

        # Under FAIL_CLOSED policy, sending any message must raise NetworkPartitionError
        with self.assertRaises(NetworkPartitionError):
            self.topology.send_message("channel_research_telemetry", {"msg": "blocked"})

        # Restoring partition re-enables dispatch
        self.topology.simulate_partition(is_partitioned=False)
        self.assertFalse(self.topology.is_partitioned)
        res = self.topology.send_message("channel_research_telemetry", {"msg": "unblocked"})
        self.assertEqual(res["status"], "DISPATCHED")


if __name__ == "__main__":
    unittest.main()
