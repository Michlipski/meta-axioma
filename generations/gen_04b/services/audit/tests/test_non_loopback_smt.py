"""Substrate Verification Test Suite for SMT Non-Loopback Verifier (`test_non_loopback_smt.py`).

Enforces:
- [NEG-G1B-001] Mandatory Substrate Test Execution (exit code 0, non-zero passing assertions).
- [L1-G3B-012] Dedicated Non-Loopback Network Topology Bound to 192.168.40.0/24.
- [L1-G3B-017] SHA-256 Chained Cryptographic SMT Proof Witnessing.
- Sheaf-Quorum Consensus Partition Safety: q > 0.67 implies |Q1 intersect Q2| >= 1.
"""

from __future__ import annotations

import unittest

from generations.gen_04b.services.audit.src.smt_mesh_verifier import (
    SMTMeshProofWitness,
    SMTMeshVerifier,
)


class TestNonLoopbackSMT(unittest.TestCase):
    def setUp(self) -> None:
        self.verifier = SMTMeshVerifier(use_z3_if_available=True)

        # Canonical G4b Sovereign Mesh Topology
        self.canonical_topology = {
            "topology_id": "topology_zenith_apex_mesh",
            "consensus": {
                "protocol": "sheaf_quorum",
                "quorum_fraction": 0.67,
                "heartbeat_interval_ms": 500,
            },
            "nodes": {
                "node_research": { "host_interface": "192.168.40.10", "port": 8440, "role": "orchestrator" },
                "node_builder": { "host_interface": "192.168.40.20", "port": 8442, "role": "compiler_core" },
                "node_audit": { "host_interface": "192.168.40.30", "port": 8444, "role": "verifier" },
                "node_telemetry": { "host_interface": "192.168.40.40", "port": 8446, "role": "storage_leaf" },
                "node_governance": { "host_interface": "192.168.40.50", "port": 8448, "role": "verifier" },
                "node_worker_21": { "host_interface": "192.168.40.21", "port": 8450, "role": "worker" },
            },
            "channels": [
                { "channel_id": "channel_research_builder", "source_node_id": "node_research", "target_node_id": "node_builder", "port": 8442 },
                { "channel_id": "channel_builder_audit", "source_node_id": "node_builder", "target_node_id": "node_audit", "port": 8444 },
                { "channel_id": "channel_builder_telemetry", "source_node_id": "node_builder", "target_node_id": "node_telemetry", "port": 8446 },
                { "channel_id": "channel_audit_telemetry", "source_node_id": "node_audit", "target_node_id": "node_telemetry", "port": 8446 },
            ],
        }

    def test_01_canonical_topology_formal_proof(self) -> None:
        """Verifies canonical 192.168.40.0/24 topology produces a valid SMT proof witness."""
        witness = self.verifier.verify_topology(self.canonical_topology)
        self.assertTrue(witness.is_valid)
        self.assertIn("L1-G3B-012", witness.axioms_verified)
        self.assertIn("SHEAF_CONSENSUS", witness.axioms_verified)
        self.assertEqual(len(witness.sha256_proof_digest), 64)
        self.assertGreater(witness.proof_steps_count, 0)
        self.assertIsNone(witness.counter_example)

    def test_02_loopback_injection_counterexample_detection(self) -> None:
        """Verifies SMT prover refutes topologies containing 127.0.0.1 or localhost."""
        # Inject loopback host into node_builder
        poisoned_topo = dict(self.canonical_topology)
        poisoned_nodes = dict(self.canonical_topology["nodes"])
        poisoned_nodes["node_builder"] = {
            "host_interface": "127.0.0.1",  # LOOPBACK INJECTION
            "port": 8442,
            "role": "compiler_core",
        }
        poisoned_topo["nodes"] = poisoned_nodes

        witness = self.verifier.verify_topology(poisoned_topo)
        self.assertFalse(witness.is_valid)
        self.assertIsNotNone(witness.counter_example)
        self.assertEqual(witness.counter_example.get("violation"), "LOOPBACK_DETECTED")
        self.assertEqual(witness.counter_example.get("node_id"), "node_builder")

    def test_03_out_of_subnet_ip_counterexample(self) -> None:
        """Verifies SMT prover refutes IP addresses outside 192.168.40.0/24."""
        poisoned_topo = dict(self.canonical_topology)
        poisoned_nodes = dict(self.canonical_topology["nodes"])
        poisoned_nodes["node_research"] = {
            "host_interface": "10.0.0.1",  # Outside 192.168.40.0/24
            "port": 8440,
            "role": "orchestrator",
        }
        poisoned_topo["nodes"] = poisoned_nodes

        witness = self.verifier.verify_topology(poisoned_topo)
        self.assertFalse(witness.is_valid)
        self.assertEqual(witness.counter_example.get("violation"), "SUBNET_OUT_OF_BOUNDS")

    def test_04_lamport_monotonicity_proof(self) -> None:
        """Verifies Lamport logical clock monotonicity proof over a transaction chain."""
        valid_chain = [
            {"transaction_id": "tx_01", "logical_clock": 1, "timestamp_ns": 1000},
            {"transaction_id": "tx_02", "logical_clock": 2, "timestamp_ns": 2000},
            {"transaction_id": "tx_03", "logical_clock": 3, "timestamp_ns": 3000},
        ]
        witness = self.verifier.verify_lamport_monotonicity(valid_chain)
        self.assertTrue(witness.is_valid)
        self.assertEqual(len(witness.sha256_proof_digest), 64)

        # Regressive logical clock chain
        regressive_chain = [
            {"transaction_id": "tx_01", "logical_clock": 5, "timestamp_ns": 1000},
            {"transaction_id": "tx_02", "logical_clock": 4, "timestamp_ns": 2000},  # Regression
        ]
        fail_witness = self.verifier.verify_lamport_monotonicity(regressive_chain)
        self.assertFalse(fail_witness.is_valid)
        self.assertEqual(fail_witness.counter_example.get("violation"), "LOGICAL_CLOCK_REGRESSION")

    def test_05_sheaf_quorum_pigeonhole_proof(self) -> None:
        """Verifies sheaf quorum fraction q=0.67 on 6 nodes guarantees overlap >= 2."""
        q_valid, cex, core = self.verifier.native_solver.check_sheaf_quorum_safety(
            node_count=6,
            quorum_fraction=0.67,
        )
        self.assertTrue(q_valid)
        self.assertIsNone(cex)
        # ceil(0.67 * 6) = 5 nodes per quorum; 2 * 5 - 6 = 4 node overlap!
        self.assertIn("unsat_core", core)


if __name__ == "__main__":
    unittest.main()
