"""Comprehensive Unit & Integration Test Suite for Axioma Mesh (SYS-09).

Tests all distributed operations:
- Bootstrap topology and node roles
- Sheaf consensus proposal and propagation
- Network partition cut and topological healing
- Zero-trust capability attenuation and privilege escalation denial
- Worker task dispatch and enclave blast containment
- CQRS checkpoints and functorial rollback morphisms
- Real-time Landauer cluster thermodynamic dissipation auditing
"""

import sys
import unittest
from pathlib import Path

# Add paths for both g3_compiler and axioma_mesh
app_dir = Path(__file__).parent
sys.path.insert(0, str(app_dir))
sys.path.insert(0, str(app_dir.parent.parent / "src"))

from core import AxiomaMeshRuntime
from models import TaskStatus


class TestAxiomaMesh(unittest.TestCase):
    """Test suite for Axioma Mesh runtime."""

    def setUp(self):
        self.mesh = AxiomaMeshRuntime()

    def test_bootstrap_topology(self):
        """Verifies initial 5+ node topology setup."""
        status = self.mesh.get_cluster_status()
        self.assertIn("gateway-01", status["topology"]["nodes"])
        self.assertIn("consensus-alpha", status["topology"]["nodes"])
        self.assertIn("consensus-beta", status["topology"]["nodes"])
        self.assertIn("consensus-gamma", status["topology"]["nodes"])
        self.assertIn("broker-01", status["topology"]["nodes"])
        self.assertIn("worker-01", status["topology"]["nodes"])

        # Cohomology gluing initially valid
        self.assertTrue(status["consensus"]["glued"])
        self.assertEqual(status["consensus"]["cocycle_error"], 0.0)

    def test_consensus_propose_and_propagation(self):
        """Tests L1-G3-001: Local section mutation and propagation."""
        res = self.mesh.propose_consensus_state("cluster_version", "v3.0.1")
        self.assertTrue(res["glued"])
        self.assertEqual(res["cocycle_error"], 0.0)

        # Check projection state in CQRS broker
        status = self.mesh.get_cluster_status()
        self.assertEqual(status["cqrs_projection"]["kv_store"].get("cluster_version"), "v3.0.1")

    def test_network_partition_split_and_heal(self):
        """Tests L1-G3-001: Partition simulation and cohomology reconciliation."""
        # 1. Simulate partition
        part_res = self.mesh.simulate_partition("consensus-alpha", "consensus-gamma")
        self.assertEqual(part_res["status"], "PARTITIONED")

        # Mutate while partitioned
        self.mesh.sheaf.update_local_section("consensus-alpha", "isolated_key", "diverged_alpha")

        # 2. Heal partition
        heal_res = self.mesh.heal_partition("consensus-alpha", "consensus-gamma")
        self.assertEqual(heal_res["status"], "HEALED")
        self.assertTrue(heal_res["glued"])
        self.assertEqual(heal_res["cocycle_error"], 0.0)

    def test_capability_token_delegation_and_denial(self):
        """Tests L1-G3-002: Attenuation and privilege escalation rejection."""
        # Issue attenuated token with only 'compute_task' permission
        tok_data = self.mesh.issue_client_token("test_client", ["compute_task"])
        tok_id = tok_data["token_id"]

        # Permitted action
        ok, msg = self.mesh.verify_action(tok_id, "worker-01", "compute_task")
        self.assertTrue(ok)

        # Forbidden action (privilege escalation attempt)
        denied, err_msg = self.mesh.verify_action(tok_id, "worker-01", "delete_cluster")
        self.assertFalse(denied)
        self.assertIn("not authorized", err_msg)

    def test_worker_task_dispatch_and_enclave_containment(self):
        """Tests L1-G3-003: Worker task dispatch and enclave blast isolation."""
        # 1. Normal task
        tok_data = self.mesh.issue_client_token("client_normal", ["compute_task"])
        norm_res = self.mesh.dispatch_task(
            action="compute_task",
            payload={"job": "matrix_multiply"},
            capability_token_id=tok_data["token_id"],
            simulate_error=False,
        )
        self.assertTrue(norm_res["success"])
        self.assertFalse(norm_res["healed"])
        self.assertEqual(norm_res["task"]["status"], TaskStatus.COMPLETED.value)

        # 2. Simulated faulty task inside Enclave
        fault_res = self.mesh.dispatch_task(
            action="compute_task",
            payload={"job": "bad_operation"},
            capability_token_id=tok_data["token_id"],
            simulate_error=True,
        )
        self.assertTrue(fault_res["success"])
        self.assertTrue(fault_res["healed"])
        self.assertTrue(fault_res["enclave_witness"]["blast_radius_contained"])

    def test_cqrs_checkpoint_and_rollback(self):
        """Tests L1-G3-004: CQRS projections and functorial rollback morphism."""
        # Mutation 1
        self.mesh.propose_consensus_state("account_balance", 1000)

        # Capture checkpoint
        cp_res = self.mesh.create_checkpoint("cp_baseline")
        self.assertEqual(cp_res["checkpoint_name"], "cp_baseline")

        # Mutation 2 (subsequent bad transaction)
        self.mesh.propose_consensus_state("account_balance", 999999)
        self.assertEqual(self.mesh.broker.get_projection_state()["kv_store"]["account_balance"], 999999)

        # Rollback to checkpoint
        rb_res = self.mesh.rollback_to_checkpoint("cp_baseline")
        self.assertTrue(rb_res["success"])
        self.assertEqual(self.mesh.broker.get_projection_state()["kv_store"]["account_balance"], 1000)

    def test_thermal_dissipation_auditing(self):
        """Tests L1-008 & L1-G3-005: Landauer thermodynamics auditing."""
        status = self.mesh.get_cluster_status()
        self.assertTrue(status["thermal_audit"]["compliance"])
        self.assertGreaterEqual(status["thermal_audit"]["total_erased_bits"], 0.0)


if __name__ == "__main__":
    unittest.main()
