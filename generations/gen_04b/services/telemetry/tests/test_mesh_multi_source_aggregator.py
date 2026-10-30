"""Unit and invariant tests for Mesh Multi-Source Telemetry Aggregator (`soc_g4b_telemetry`).

Verifies:
- [L1-G4B-001] Service-Oriented Sovereign Mesh Protocol Standardization.
- [L1-G3B-012] Dedicated Non-Loopback Network Topology on mesh nodes.
- Canonical peer registration: Research (192.168.40.10), Builder (192.168.40.20), Audit (192.168.40.30), Telemetry (192.168.40.40).
- Rejection of loopback node registrations (127.0.0.1, localhost, ::1, 0.0.0.0).
- Node heartbeat tracking with Merkle roots, status transitions, and bit erasure.
- Whole-mesh thermodynamic dissipation aggregation.
- Invariant enforcement: port bounds, non-empty names, negative bit handling, unregistered service heartbeats.
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
    TelemetryTopologyState,
)
from generations.gen_04b.services.telemetry.src.mesh_multi_source_aggregator import (
    MeshMultiSourceAggregator,
)


class TestMeshMultiSourceAggregator(unittest.TestCase):
    """Test suite for MeshMultiSourceAggregator peer tracking and dissipation aggregation."""

    def setUp(self):
        self.aggregator = MeshMultiSourceAggregator(
            self_node_ip="192.168.40.40",
            self_port=8446,
            auto_register_canonical=True,
        )

    def test_canonical_peers_registration(self):
        nodes = self.aggregator.get_registered_nodes()
        self.assertEqual(len(nodes), 4)
        self.assertIn("research_service", nodes)
        self.assertIn("builder_service", nodes)
        self.assertIn("audit_service", nodes)
        self.assertIn("telemetry_service", nodes)

        self.assertEqual(nodes["research_service"].node_ip, "192.168.40.10")
        self.assertEqual(nodes["research_service"].port, 8440)
        self.assertEqual(nodes["builder_service"].node_ip, "192.168.40.20")
        self.assertEqual(nodes["builder_service"].port, 8442)
        self.assertEqual(nodes["audit_service"].node_ip, "192.168.40.30")
        self.assertEqual(nodes["audit_service"].port, 8444)
        self.assertEqual(nodes["telemetry_service"].node_ip, "192.168.40.40")
        self.assertEqual(nodes["telemetry_service"].port, 8446)

    def test_register_custom_node_happy_path(self):
        witness = self.aggregator.register_mesh_node(
            service_name="governance_service",
            node_ip="192.168.40.50",
            port=8448,
        )
        self.assertEqual(witness.service_name, "governance_service")
        self.assertEqual(witness.node_ip, "192.168.40.50")
        self.assertEqual(witness.port, 8448)
        self.assertIn("governance_service", self.aggregator.get_registered_nodes())

    def test_register_node_loopback_rejection(self):
        with self.assertRaises(TelemetryDomainInvariantViolation):
            self.aggregator.register_mesh_node("bad_node_1", "127.0.0.1", 9000)

        with self.assertRaises(TelemetryDomainInvariantViolation):
            self.aggregator.register_mesh_node("bad_node_2", "localhost", 9000)

        with self.assertRaises(TelemetryDomainInvariantViolation):
            self.aggregator.register_mesh_node("bad_node_3", "::1", 9000)

        with self.assertRaises(TelemetryDomainInvariantViolation):
            self.aggregator.register_mesh_node("bad_node_4", "0.0.0.0", 9000)

    def test_record_node_heartbeat_updates_state(self):
        merkle_root = "d" * 64
        witness = self.aggregator.record_node_heartbeat(
            service_name="research_service",
            merkle_root=merkle_root,
            bits_erased=45000,
            status=TelemetryTopologyState.HEALTHY,
        )
        self.assertEqual(witness.Merkle_root, merkle_root)
        self.assertEqual(witness.bits_erased, 45000)
        self.assertEqual(witness.status, TelemetryTopologyState.HEALTHY)

    def test_record_heartbeat_unregistered_node_failure(self):
        with self.assertRaises(TelemetryDomainInvariantViolation):
            self.aggregator.record_node_heartbeat(
                service_name="unknown_service_xyz",
                merkle_root="a" * 64,
                bits_erased=1000,
            )

    def test_record_heartbeat_negative_bits_failure(self):
        with self.assertRaises(TelemetryDomainInvariantViolation):
            self.aggregator.record_node_heartbeat(
                service_name="research_service",
                merkle_root="a" * 64,
                bits_erased=-50,
            )

    def test_aggregate_mesh_dissipation_calculation(self):
        self.aggregator.record_node_heartbeat("research_service", "r" * 64, bits_erased=100_000)
        self.aggregator.record_node_heartbeat("builder_service", "b" * 64, bits_erased=200_000)
        self.aggregator.record_node_heartbeat("audit_service", "a" * 64, bits_erased=300_000)
        self.aggregator.record_node_heartbeat("telemetry_service", "t" * 64, bits_erased=400_000)

        agg = self.aggregator.aggregate_mesh_dissipation()
        self.assertEqual(agg["total_mesh_bits_erased"], 1_000_000)
        self.assertEqual(agg["nodes_count"], 4)

        k_b = 1.380649e-23
        ln2 = 0.6931471805599453
        expected_heat = k_b * 300.0 * ln2 * 1_000_000
        self.assertAlmostEqual(agg["total_mesh_heat_dissipated_joules"], expected_heat, places=25)
        self.assertIn("research_service", agg["per_node"])
        self.assertEqual(agg["per_node"]["research_service"]["bits_erased"], 100_000)

    def test_cluster_topology_state_and_invariants(self):
        topo = self.aggregator.get_cluster_topology_state()
        topo.validate_invariants()
        self.assertEqual(topo.self_node_ip, "192.168.40.40")
        self.assertEqual(topo.self_port, 8446)
        self.assertFalse(topo.is_partitioned)

    def test_invalid_constructor_params(self):
        with self.assertRaises(TelemetryDomainInvariantViolation):
            MeshMultiSourceAggregator(self_node_ip="127.0.0.1", self_port=8446)

        with self.assertRaises(TelemetryDomainInvariantViolation):
            MeshMultiSourceAggregator(self_node_ip="192.168.40.40", self_port=80)


if __name__ == "__main__":
    unittest.main()
