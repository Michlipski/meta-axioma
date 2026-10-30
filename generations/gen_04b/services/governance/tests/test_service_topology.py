"""Exhaustive Test Suite for Dedicated Non-Loopback Network Topology (`soc_g4b_governance`).

Enforces:
- Invariant [L1-G3B-012]: Dedicated Non-Loopback Network Topology on 192.168.40.50:8448.
- Absolute rejection of loopback endpoints (127.0.0.1, localhost, ::1, 0.0.0.0).
- Standardized cluster mesh topology mapping across 192.168.40.0/24 subnet.
- Fail-closed network partition isolation and partition healing mechanics.
"""

from __future__ import annotations

from pathlib import Path
import sys
import unittest

GOV_ROOT = Path(__file__).resolve().parent.parent
REPO_ROOT = GOV_ROOT.parent.parent.parent.parent
for p in [str(GOV_ROOT), str(GOV_ROOT / "src"), str(REPO_ROOT)]:
    if p not in sys.path:
        sys.path.insert(0, p)

from src.domain_models import (
    GovernanceDomainInvariantViolation,
    assert_non_loopback,
)
from src.service_topology import (
    GovernanceChannel,
    GovernanceServiceTopology,
    NetworkPartitionError,
    PartitionPolicy,
)


class TestServiceTopology(unittest.TestCase):
    """Exhaustive unit and boundary tests for Governance network topology."""

    def setUp(self) -> None:
        self.topology = GovernanceServiceTopology(
            node_ip="192.168.40.50",
            port=8448,
            partition_policy=PartitionPolicy.FAIL_CLOSED,
        )

    def test_default_initialization_adheres_to_invariants(self) -> None:
        """Default initialization binds to 192.168.40.50:8448 and initializes active channels."""
        self.assertEqual(self.topology.endpoint, "192.168.40.50:8448")
        self.assertEqual(self.topology.node_ip, "192.168.40.50")
        self.assertEqual(self.topology.port, 8448)
        self.assertFalse(self.topology.is_partitioned)

        bindings = self.topology.get_cluster_bindings()
        self.assertEqual(len(bindings), 5)
        for b in bindings:
            assert_non_loopback(b, "Cluster Binding Verification")

    def test_rejection_of_loopback_node_ips(self) -> None:
        """Topology initialization rejects all forms of loopback or wildcard addresses."""
        prohibited = [
            ("127.0.0.1", 8448),
            ("localhost", 8448),
            ("::1", 8448),
            ("0.0.0.0", 8448),
            ("127.0.1.1", 9000),
        ]
        for ip, port in prohibited:
            with self.assertRaises(GovernanceDomainInvariantViolation):
                GovernanceServiceTopology(node_ip=ip, port=port)

    def test_peer_endpoint_resolution_across_mesh(self) -> None:
        """Resolves endpoints for all peer services on the 192.168.40.0/24 subnet."""
        expected = {
            "research": "192.168.40.10:8440",
            "builder": "192.168.40.20:8442",
            "audit": "192.168.40.30:8444",
            "telemetry": "192.168.40.40:8446",
            "governance": "192.168.40.50:8448",
        }
        for svc, expected_ep in expected.items():
            resolved = self.topology.get_peer_endpoint(svc)
            self.assertEqual(resolved, expected_ep)

    def test_unknown_peer_endpoint_raises_violation(self) -> None:
        """Attempting to resolve an unregistered peer raises GovernanceDomainInvariantViolation."""
        with self.assertRaises(GovernanceDomainInvariantViolation):
            self.topology.get_peer_endpoint("unknown_rogue_service")

    def test_channel_transmission_and_byte_accounting(self) -> None:
        """Transmitting over an active channel increments byte count and message count."""
        ch_name = "channel_audit_surveillance"
        ch = self.topology.get_channel(ch_name)
        initial_bytes = ch.bytes_transmitted
        initial_msgs = ch.message_count

        self.topology.transmit(ch_name, payload_bytes=1024)
        self.assertEqual(ch.bytes_transmitted, initial_bytes + 1024)
        self.assertEqual(ch.message_count, initial_msgs + 1)

    def test_network_partition_fail_closed_policy(self) -> None:
        """Triggering a partition blocks channel access and transmission under FAIL_CLOSED policy."""
        ch_name = "channel_telemetry_ledger"
        self.topology.trigger_partition()
        self.assertTrue(self.topology.is_partitioned)

        # Accessing channel raises NetworkPartitionError
        with self.assertRaises(NetworkPartitionError):
            self.topology.get_channel(ch_name)

        # Transmitting raises NetworkPartitionError
        with self.assertRaises(NetworkPartitionError):
            self.topology.transmit(ch_name, 512)

    def test_healing_partition_restores_channel_connectivity(self) -> None:
        """Healing a partition restores normal operation and allows transmissions."""
        ch_name = "channel_builder_rfc"
        self.topology.trigger_partition()
        self.topology.heal_partition()
        self.assertFalse(self.topology.is_partitioned)

        ch = self.topology.get_channel(ch_name)
        self.assertTrue(ch.is_active)
        self.topology.transmit(ch_name, 256)
        self.assertGreaterEqual(ch.bytes_transmitted, 256)

    def test_channel_invariants_reject_loopback_endpoints(self) -> None:
        """GovernanceChannel rejects loopback source or target endpoints."""
        with self.assertRaises(GovernanceDomainInvariantViolation):
            bad_ch = GovernanceChannel(
                channel_id="chan_bad",
                channel_name="bad_channel",
                source_endpoint="127.0.0.1:8448",
                target_endpoint="192.168.40.30:8444",
                protocol="TCP",
            )
            bad_ch.validate_invariants()

        with self.assertRaises(GovernanceDomainInvariantViolation):
            bad_ch2 = GovernanceChannel(
                channel_id="chan_bad2",
                channel_name="bad_channel2",
                source_endpoint="192.168.40.50:8448",
                target_endpoint="localhost:8444",
                protocol="TCP",
            )
            bad_ch2.validate_invariants()

    def test_export_topology_dict_format(self) -> None:
        """Exports full topology layout and channel diagnostics."""
        diag = self.topology.export_topology_dict()
        self.assertEqual(diag["service"], "soc_g4b_governance")
        self.assertEqual(diag["endpoint"], "192.168.40.50:8448")
        self.assertIn("channel_audit_surveillance", diag["channels"])
        self.assertIn("peers", diag)


if __name__ == "__main__":
    unittest.main()
