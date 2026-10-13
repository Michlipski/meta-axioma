"""Unit and Integration Tests for Generation 3 Distributed Systems Compiler.

Validates the full G3 Invariant & Target Suite:
- L1-G3-001 / G3-T1: Sheaf-Theoretic Distributed Consensus & Partition Healing
- L1-G3-002 / G3-T3: Zero-Ambient Capability Delegation & Attenuation
- L1-G3-003 / G3-T2: Cluster Blast Enclaves & Checkpoint Rollback
- L1-G3-004 / G3-T2: Distributed Event Sourcing & CQRS Projections
- L1-G3-005 / G3-T4: Thermodynamic Cluster Dissipation Auditing
"""

import time
import unittest
import sys
from pathlib import Path

# Ensure g3_compiler is in sys.path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from g3_compiler.models import (
    ClusterNodeMetadata,
    ClusterThermodynamicAudit,
    DistributedCapabilityToken,
    DistributedEvent,
    EventType,
    NodeHealth,
    NodeRole,
    SheafSection,
)
from g3_compiler.sheaf_consensus import SheafConsensusEngine
from g3_compiler.zero_trust_mesh import DistributedCapabilityAuthority
from g3_compiler.event_broker import DistributedEventBroker
from g3_compiler.cluster_topology import DistributedClusterMesh, ClusterExceptionEnclave
from g3_compiler.engine import G3DistributedCompilerEngine


class TestGeneration3Compiler(unittest.TestCase):
    """Test suite for Generation 3 Distributed Compiler Engine."""

    def setUp(self):
        self.engine = G3DistributedCompilerEngine(cluster_name="Test_Mesh")

    def test_sheaf_consensus_partition_heal(self):
        """Validates L1-G3-001 and G3-T1: Sheaf consensus and cohomology gluing."""
        sheaf = SheafConsensusEngine()
        sheaf.register_node("node-a", "core_submesh", {"cluster_epoch": 1, "status": "UP"})
        sheaf.register_node("node-b", "core_submesh", {"cluster_epoch": 1, "status": "UP"})
        sheaf.register_node("node-c", "core_submesh", {"cluster_epoch": 1, "status": "UP"})

        # Initial agreement
        glued, err = sheaf.compute_cohomology_h0("core_submesh")
        self.assertTrue(glued)
        self.assertEqual(err, 0.0)

        # Mutate node-a
        sheaf.update_local_section("node-a", "epoch_counter", 42)

        # Split node-c from node-a
        sheaf.simulate_partition("node-a", "node-c")
        self.assertTrue(sheaf.is_partitioned("node-a", "node-c"))

        sheaf.update_local_section("node-c", "isolated_key", "divergent_value")

        # Heal network partition
        healed = sheaf.heal_partition("node-a", "node-c")
        self.assertTrue(healed)
        self.assertFalse(sheaf.is_partitioned("node-a", "node-c"))

        # Cohomology gluing after partition healing
        glued_healed, err_healed = sheaf.compute_cohomology_h0("core_submesh")
        self.assertTrue(glued_healed)
        self.assertEqual(err_healed, 0.0)

        # Verify state was glued onto node-c
        sec_c = sheaf.get_section("node-c")
        self.assertIsNotNone(sec_c)
        self.assertEqual(sec_c.data.get("epoch_counter"), 42)

    def test_zero_trust_capability_delegation(self):
        """Validates L1-G3-002 and G3-T3: Capability tokens and HMAC attenuation."""
        auth = DistributedCapabilityAuthority(master_secret="test_axioma_secret")

        # 1. Issue root token
        root_tok = auth.issue_token(
            issuer_node_id="orchestrator",
            target_service="gateway-01",
            allowed_actions=["read_telemetry", "execute_task", "manage_cluster"],
            ttl_seconds=3600,
        )
        self.assertIsNotNone(root_tok.token_id)
        self.assertTrue(auth.verify_token(root_tok.token_id))

        # 2. Delegate with attenuation (monotone permission restriction)
        delegated_tok = auth.delegate_token(
            parent_token_id=root_tok.token_id,
            sub_target_service="worker-01",
            sub_actions=["execute_task"],
            ttl_seconds=600,
        )
        self.assertIsNotNone(delegated_tok)
        self.assertEqual(delegated_tok.delegated_from, root_tok.token_id)
        self.assertEqual(delegated_tok.allowed_actions, ("execute_task",))

        # 3. Verify permitted action
        ok, msg = auth.verify_action(delegated_tok.token_id, "worker-01", "execute_task")
        self.assertTrue(ok)

        # 4. Verify unauthorized action (privilege escalation attempt)
        denied, err_msg = auth.verify_action(delegated_tok.token_id, "worker-01", "manage_cluster")
        self.assertFalse(denied)
        self.assertIn("Action 'manage_cluster' not authorized", err_msg)

        # 5. Invalid delegation attempt (trying to delegate permission parent doesn't have)
        with self.assertRaises(PermissionError):
            auth.delegate_token(
                parent_token_id=root_tok.token_id,
                sub_target_service="worker-02",
                sub_actions=["unauthorized_superpower"],
                ttl_seconds=300,
            )

        # 6. Tampered signature check
        tampered_tok = auth.get_token(delegated_tok.token_id)
        # We replace in internal dictionary with tampered copy
        auth._tokens[delegated_tok.token_id] = DistributedCapabilityToken(
            token_id=tampered_tok.token_id,
            issuer_node_id=tampered_tok.issuer_node_id,
            target_service=tampered_tok.target_service,
            allowed_actions=tampered_tok.allowed_actions,
            signature_hmac="invalid_forged_signature",
            issued_at=tampered_tok.issued_at,
            expires_at=tampered_tok.expires_at,
            delegated_from=tampered_tok.delegated_from,
            attenuated_scope=tampered_tok.attenuated_scope,
        )
        self.assertFalse(auth.verify_token(delegated_tok.token_id))

    def test_event_broker_cqrs_and_rollback(self):
        """Validates L1-G3-004 and G3-T2: Event sourcing, vector clocks, and rollback."""
        broker = DistributedEventBroker()
        auth = DistributedCapabilityAuthority()
        tok = auth.issue_token("admin", "broker-01", ["*"], ttl_seconds=3600)

        # Register reducer for bank balance projection
        broker.register_reducer(
            EventType.TRANSACTION_COMMITTED,
            lambda state, payload: state.update({payload["account"]: state.get(payload["account"], 0) + payload["amount"]}),
        )

        # Append initial events
        broker.append_event(
            event_type=EventType.TRANSACTION_COMMITTED,
            origin_node_id="gateway-01",
            payload={"account": "alice", "amount": 100},
            capability_token_id=tok.token_id,
        )
        broker.append_event(
            event_type=EventType.TRANSACTION_COMMITTED,
            origin_node_id="gateway-01",
            payload={"account": "bob", "amount": 50},
            capability_token_id=tok.token_id,
        )

        self.assertEqual(broker.get_projection_state(), {"alice": 100, "bob": 50})

        # Create checkpoint
        broker.create_checkpoint("cp_after_initial_tx")

        # Append bad/corrupted event
        broker.append_event(
            event_type=EventType.TRANSACTION_COMMITTED,
            origin_node_id="gateway-01",
            payload={"account": "alice", "amount": 999999},
            capability_token_id=tok.token_id,
        )
        self.assertEqual(broker.get_projection_state()["alice"], 1000099)

        # Functorial rollback to checkpoint (L1-G3-004)
        rolled_back = broker.rollback_to_checkpoint("cp_after_initial_tx", tok.token_id)
        self.assertTrue(rolled_back)
        self.assertEqual(broker.get_projection_state(), {"alice": 100, "bob": 50})

    def test_cluster_enclave_blast_containment(self):
        """Validates L1-G3-003: Cluster exception enclave blast radius containment."""
        with ClusterExceptionEnclave("worker-01", "compute_sharding_task") as enclave:
            # Trigger deliberate simulated crash
            val = 100 / 0  # ZeroDivisionError

        self.assertTrue(enclave.healed)
        self.assertIsNotNone(enclave.witness)
        self.assertTrue(enclave.witness.get("blast_radius_contained"))
        self.assertEqual(enclave.witness.get("error_type"), "ZeroDivisionError")

    def test_thermodynamic_cluster_dissipation(self):
        """Validates L1-G3-005 and G3-T4: Landauer thermodynamic dissipation auditing."""
        mesh = DistributedClusterMesh()
        mesh.register_node("node-1", NodeRole.COMPUTE_WORKER, port=8210)
        mesh.record_node_heartbeat("node-1", erased_bits_increment=1024.0)

        audit = mesh.audit_cluster_thermodynamics(max_allowed_joules=1e-15)
        self.assertTrue(audit.thermal_compliance_passed)
        self.assertEqual(audit.total_cluster_erased_bits, 1024.0)
        # Expected Joules: 1024 * 1.380649e-23 * 298.15 * ln(2) ~= 2.92e-18 J
        self.assertGreater(audit.total_joules_dissipated, 1e-19)
        self.assertLess(audit.total_joules_dissipated, 1e-17)

    def test_g3_compiler_engine_full_suite(self):
        """Validates end-to-end execution of the G3 evaluation targets (G3-T1..T4)."""
        all_passed, delta, results = self.engine.run_full_suite_audit()
        self.assertTrue(all_passed)
        self.assertAlmostEqual(delta, 1.0, places=3)
        self.assertEqual(len(results), 4)

        for res in results:
            self.assertTrue(res["passed"], f"Target {res['target_id']} failed")


if __name__ == "__main__":
    unittest.main()
