"""Core Distributed Mesh Orchestrator for Axioma Mesh (SYS-09).

Embodies Generation 3 axioms:
- L1-G3-001: Sheaf Consensus with Cohomology Checking
- L1-G3-002: Zero-Trust Capability Mesh with Attenuation
- L1-G3-003: Cluster Exception Enclaves for Blast Containment
- L1-G3-004: Event Sourcing, Vector Clocks, and Checkpoint Rollbacks
- L1-G3-005: High-Level Jettison Convergence & Landauer Thermal Auditing
"""

from __future__ import annotations

import logging
import sys
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Ensure g3_compiler can be imported
mesh_dir = Path(__file__).resolve().parent
g3_src = mesh_dir.parent.parent / "src"
if str(g3_src) not in sys.path:
    sys.path.insert(0, str(g3_src))

from g3_compiler.cluster_topology import ClusterExceptionEnclave, DistributedClusterMesh
from g3_compiler.event_broker import DistributedEventBroker
from g3_compiler.models import EventType, NodeHealth, NodeRole
from g3_compiler.sheaf_consensus import SheafConsensusEngine
from g3_compiler.zero_trust_mesh import DistributedCapabilityAuthority
try:
    from .models import ClusterTask, TaskPriority, TaskStatus
except ImportError:
    from models import ClusterTask, TaskPriority, TaskStatus

logger = logging.getLogger("AxiomaMeshCore")


class AxiomaMeshRuntime:
    """The live multi-node distributed runtime orchestrator."""

    def __init__(self):
        self.sheaf = SheafConsensusEngine()
        self.authority = DistributedCapabilityAuthority(master_secret="axioma_mesh_g3_secret_2026")
        self.broker = DistributedEventBroker()
        self.mesh = DistributedClusterMesh()

        # Task queue and execution history
        self.tasks: Dict[str, ClusterTask] = {}
        self.start_time = time.time()

        # Bootstrap canonical 5-node distributed topology
        self._bootstrap_cluster()

        # Issue root admin capability token for Ingress Gateway
        self.gateway_token = self.authority.issue_token(
            issuer_node_id="mesh_orchestrator",
            target_service="gateway-01",
            allowed_actions=["*"],
            ttl_seconds=86400.0,
        )

        # Register standard CQRS projection reducers
        self._register_reducers()

    def _bootstrap_cluster(self) -> None:
        """Initializes the multi-node backend topology."""
        # 1. Ingress Gateway
        self.mesh.register_node("gateway-01", NodeRole.INGRESS_GATEWAY, port=8200)

        # 2. Consensus Triad
        for nid, port, is_leader in [
            ("consensus-alpha", 8201, True),
            ("consensus-beta", 8202, False),
            ("consensus-gamma", 8203, False),
        ]:
            role = NodeRole.CONSENSUS_LEADER if is_leader else NodeRole.CONSENSUS_FOLLOWER
            self.mesh.register_node(nid, role, port=port)
            self.sheaf.register_node(
                nid,
                cover_id="cluster_core",
                initial_data={"cluster_epoch": 1, "state": "OPERATIONAL", "view_number": 0},
            )

        # 3. Distributed Event Broker
        self.mesh.register_node("broker-01", NodeRole.EVENT_BROKER, port=8204)

        # 4. Compute Worker Pool
        self.mesh.register_node("worker-01", NodeRole.COMPUTE_WORKER, port=8205)
        self.mesh.register_node("worker-02", NodeRole.COMPUTE_WORKER, port=8206)

    def _register_reducers(self) -> None:
        """Sets up deterministic left-fold CQRS projections for cluster state."""
        def tx_reducer(state: Dict[str, Any], payload: Dict[str, Any]) -> None:
            if "kv_store" not in state:
                state["kv_store"] = {}
            if "key" in payload and "value" in payload:
                state["kv_store"][payload["key"]] = payload["value"]
            state["last_tx_time"] = time.time()

        def task_reducer(state: Dict[str, Any], payload: Dict[str, Any]) -> None:
            state["completed_tasks_count"] = state.get("completed_tasks_count", 0) + 1

        self.broker.register_reducer(EventType.TRANSACTION_COMMITTED, tx_reducer)
        self.broker.register_reducer(EventType.TASK_COMPLETED, task_reducer)

    # ---------------------------------------------------------
    # Consensus & Sheaf Topological Operations (L1-G3-001)
    # ---------------------------------------------------------

    def propose_consensus_state(self, key: str, value: Any) -> Dict[str, Any]:
        """Proposes a cluster state mutation to the consensus leader (alpha)."""
        # Updates alpha's local section and propagates restriction to connected peers
        sec = self.sheaf.update_local_section("consensus-alpha", key, value)
        self.mesh.record_node_heartbeat("consensus-alpha", erased_bits_increment=64.0)

        # Check cohomology gluing across cluster_core open cover
        glued, cocycle_error = self.sheaf.compute_cohomology_h0("cluster_core")

        # Record in event broker
        self.broker.append_event(
            EventType.TRANSACTION_COMMITTED,
            origin_node_id="consensus-alpha",
            payload={"key": key, "value": value, "version": sec.version},
            capability_token_id=self.gateway_token.token_id,
        )

        return {
            "key": key,
            "value": value,
            "section_version": sec.version,
            "glued": glued,
            "cocycle_error": cocycle_error,
            "active_partitions": list(self.sheaf.active_partitions),
        }

    def simulate_partition(self, node_a: str, node_b: str) -> Dict[str, Any]:
        """Simulates physical network partition between two consensus nodes."""
        self.sheaf.simulate_partition(node_a, node_b)
        glued, cocycle_error = self.sheaf.compute_cohomology_h0("cluster_core")

        # Mark degraded health if partitioned
        for nid in (node_a, node_b):
            n = self.mesh.nodes.get(nid)
            if n:
                n.health = NodeHealth.PARTITIONED

        self.broker.append_event(
            EventType.PARTITION_DETECTED,
            origin_node_id="gateway-01",
            payload={"node_a": node_a, "node_b": node_b, "cocycle_error": cocycle_error},
            capability_token_id=self.gateway_token.token_id,
        )

        return {
            "status": "PARTITIONED",
            "edge": [node_a, node_b],
            "glued": glued,
            "cocycle_error": cocycle_error,
        }

    def heal_partition(self, node_a: str, node_b: str) -> Dict[str, Any]:
        """Heals network partition and triggers topological lattice gluing."""
        healed = self.sheaf.heal_partition(node_a, node_b)
        glued, cocycle_error = self.sheaf.compute_cohomology_h0("cluster_core")

        # Restore healthy status if no other partitions
        for nid in (node_a, node_b):
            n = self.mesh.nodes.get(nid)
            if n:
                n.health = NodeHealth.HEALTHY

        # Record bit erasure for state reconciliation (Landauer dissipation)
        self.mesh.record_node_heartbeat(node_a, erased_bits_increment=128.0)
        self.mesh.record_node_heartbeat(node_b, erased_bits_increment=128.0)

        self.broker.append_event(
            EventType.PARTITION_RECONCILED,
            origin_node_id="gateway-01",
            payload={"node_a": node_a, "node_b": node_b, "glued": glued, "cocycle_error": cocycle_error},
            capability_token_id=self.gateway_token.token_id,
        )

        return {
            "status": "HEALED",
            "edge": [node_a, node_b],
            "glued": glued,
            "cocycle_error": cocycle_error,
        }

    # ---------------------------------------------------------
    # Capability Mesh Operations (L1-G3-002)
    # ---------------------------------------------------------

    def issue_client_token(self, client_id: str, permissions: List[str], ttl: float = 3600.0) -> Dict[str, Any]:
        """Issues an attenuated client token delegated from the Ingress Gateway."""
        tok = self.authority.delegate_token(
            parent_token_id=self.gateway_token.token_id,
            sub_target_service="worker-01",
            sub_actions=permissions,
            ttl_seconds=ttl,
        )
        return tok.to_dict()

    def verify_action(self, token_id: str, service: str, action: str) -> Tuple[bool, str]:
        return self.authority.verify_action(token_id, service, action)

    # ---------------------------------------------------------
    # Worker Task Execution & Enclaves (L1-G3-003)
    # ---------------------------------------------------------

    def dispatch_task(
        self,
        action: str,
        payload: Dict[str, Any],
        capability_token_id: str,
        simulate_error: bool = False,
    ) -> Dict[str, Any]:
        """Dispatches compute task to worker pool inside isolated Exception Enclave."""
        # 1. Zero-trust capability authorization check
        authorized, reason = self.authority.verify_action(capability_token_id, "worker-01", action)
        if not authorized:
            return {
                "success": False,
                "error": f"Authorization denied: {reason}",
                "status": "DENIED",
            }

        task_id = f"task_{uuid.uuid4().hex[:8]}"
        task = ClusterTask(
            task_id=task_id,
            action=action,
            payload=payload,
            capability_token_id=capability_token_id,
            status=TaskStatus.RUNNING,
            worker_id="worker-01",
        )
        self.tasks[task_id] = task

        # 2. Execute within demarcated exception enclave
        with ClusterExceptionEnclave("worker-01", action) as enclave:
            if simulate_error:
                # Trigger deliberate arithmetic or schema fault
                raise ValueError("Simulated distributed worker computation divergence!")

            # Normal task execution
            exec_result = {
                "result": f"Executed action '{action}' on worker-01",
                "output_data": {k: f"processed_{v}" for k, v in payload.items()},
                "compute_time_ms": 0.42,
            }
            task.result = exec_result
            task.status = TaskStatus.COMPLETED
            task.completed_at = time.time()

        # Track Landauer dissipation
        self.mesh.record_node_heartbeat("worker-01", erased_bits_increment=32.0)

        if enclave.healed:
            task.status = TaskStatus.FAILED
            task.error = f"Handled by Enclave: {enclave.witness.get('remedy')}"
            task.result = {"enclave_witness": enclave.witness}
            self.broker.append_event(
                EventType.ENCLAVE_HEALED,
                origin_node_id="worker-01",
                payload=enclave.witness,
                capability_token_id=capability_token_id,
            )
            return {
                "success": True,
                "healed": True,
                "task": task.to_dict(),
                "enclave_witness": enclave.witness,
            }

        # Successful completion
        self.broker.append_event(
            EventType.TASK_COMPLETED,
            origin_node_id="worker-01",
            payload={"task_id": task_id, "action": action},
            capability_token_id=capability_token_id,
        )

        return {
            "success": True,
            "healed": False,
            "task": task.to_dict(),
        }

    # ---------------------------------------------------------
    # CQRS Checkpoints & Rollback Morphisms (L1-G3-004)
    # ---------------------------------------------------------

    def create_checkpoint(self, checkpoint_name: str) -> Dict[str, Any]:
        """Creates an immutable cluster checkpoint for instant rollback."""
        self.broker.create_checkpoint(checkpoint_name)
        return {
            "checkpoint_name": checkpoint_name,
            "event_count": len(self.broker.get_events()),
            "projection_state": self.broker.get_projection_state(),
            "timestamp": time.time(),
        }

    def rollback_to_checkpoint(self, checkpoint_name: str) -> Dict[str, Any]:
        """Rolls back the cluster state to a previously saved checkpoint."""
        ok = self.broker.rollback_to_checkpoint(checkpoint_name, self.gateway_token.token_id)
        return {
            "success": ok,
            "checkpoint_name": checkpoint_name,
            "reverted_projection_state": self.broker.get_projection_state(),
        }

    # ---------------------------------------------------------
    # Cluster Telemetry & Thermal Auditing (L1-008 & L1-G3-005)
    # ---------------------------------------------------------

    def get_cluster_status(self) -> Dict[str, Any]:
        """Returns unified cluster status, topology, events, and Landauer metrics."""
        # Auditing thermodynamics
        thermal_audit = self.mesh.audit_cluster_thermodynamics(max_allowed_joules=1e-15)

        # Sheaf cohomology
        glued, cocycle_error = self.sheaf.compute_cohomology_h0("cluster_core")

        # Consensus sections
        sections_summary = {
            nid: sec.to_dict()
            for nid, sec in self.sheaf.sections.items()
        }

        # Recent events
        recent_events = [ev.to_dict() for ev in self.broker.get_events()[-15:]]

        return {
            "cluster_name": "Axioma_Mesh_01",
            "generation": "gen_03",
            "uptime_seconds": round(time.time() - self.start_time, 2),
            "topology": self.mesh.get_topology_snapshot(),
            "consensus": {
                "cover_id": "cluster_core",
                "glued": glued,
                "cocycle_error": cocycle_error,
                "active_partitions": list(self.sheaf.active_partitions),
                "sections": sections_summary,
            },
            "cqrs_projection": self.broker.get_projection_state(),
            "checkpoints": list(self.broker._checkpoints.keys()),
            "recent_events": recent_events,
            "thermal_audit": {
                "total_erased_bits": thermal_audit.total_cluster_erased_bits,
                "joules_dissipated": thermal_audit.total_joules_dissipated,
                "compliance": thermal_audit.thermal_compliance_passed,
            },
            "tasks_summary": {
                "total": len(self.tasks),
                "running": sum(1 for t in self.tasks.values() if t.status == TaskStatus.RUNNING),
                "completed": sum(1 for t in self.tasks.values() if t.status == TaskStatus.COMPLETED),
                "failed": sum(1 for t in self.tasks.values() if t.status == TaskStatus.FAILED),
            },
        }
