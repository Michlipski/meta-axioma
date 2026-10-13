"""Axioma Fabric Chaos Crucible & Fault Injection Harness.

Executes adversarial stress testing: netsplits, asymmetric network partitions,
route flapping, and concurrent write storms across distributed broker nodes.
"""

from __future__ import annotations
import random
import time
from typing import Dict, List, Set, Tuple
from .cocycle_auditor import FabricCocycleAuditor
from .models import CapabilityToken
from .sheaf_broker import FabricBrokerNode


class FabricChaosCrucible:
    """Orchestrates network partition faults and stress injection across broker clusters."""

    def __init__(self, nodes: List[FabricBrokerNode]) -> None:
        self.nodes = {n.node_id: n for n in nodes}
        self.node_list = list(nodes)
        self.auditor = FabricCocycleAuditor()

    def partition_cluster(self, group_a_ids: List[str], group_b_ids: List[str]) -> None:
        """Create a strict bipartite network partition (netsplit) between group A and B."""
        for a_id in group_a_ids:
            node_a = self.nodes.get(a_id)
            if not node_a:
                continue
            for b_id in group_b_ids:
                node_b = self.nodes.get(b_id)
                if not node_b:
                    continue
                node_a.sever_link_to(b_id)
                node_b.sever_link_to(a_id)

    def isolate_node(self, node_id: str) -> None:
        """Completely isolate a single node from all peers."""
        node = self.nodes.get(node_id)
        if not node:
            return
        for peer_id, peer in self.nodes.items():
            if peer_id != node_id:
                node.sever_link_to(peer_id)
                peer.sever_link_to(node_id)

    def heal_all_partitions(self) -> None:
        """Restore all severed links across the entire cluster."""
        for node in self.node_list:
            for peer_id in list(self.nodes.keys()):
                if peer_id != node.node_id:
                    node.restore_link_to(peer_id)

    def run_partition_tournament(
        self,
        topic: str,
        token: CapabilityToken,
        messages_per_partition: int = 20,
    ) -> Dict[str, Any]:
        """Execute complete adversarial partition-recovery tournament:
        1. Bipartite split: [Node 0] vs [Node 1, Node 2]
        2. Concurrent writes into both isolated subdomains
        3. Verify local write availability without stalling
        4. Heal partition
        5. Run cocycle audit and verify 100% convergence
        """
        if len(self.node_list) < 2:
            raise ValueError("Need at least 2 nodes for partition tournament")

        n0 = self.node_list[0]
        n_rest = self.node_list[1:]
        group_b_ids = [n.node_id for n in n_rest]

        # 1. Partition cluster
        self.partition_cluster([n0.node_id], group_b_ids)

        # 2. Concurrent writes to partitioned sides
        events_n0: List[str] = []
        for i in range(messages_per_partition):
            ev = n0.publish(topic, {"source": n0.node_id, "idx": i, "val": f"payload_a_{i}"}, token)
            events_n0.append(ev.event_id)

        events_rest: List[str] = []
        for i in range(messages_per_partition):
            target_node = random.choice(n_rest)
            ev = target_node.publish(topic, {"source": target_node.node_id, "idx": i, "val": f"payload_b_{i}"}, token)
            events_rest.append(ev.event_id)

        # Verify isolation during split
        sec_n0_during = n0.get_section(topic)
        sec_rest_during = n_rest[0].get_section(topic)
        
        # None of the events from group B should be in n0 during split
        leaked_to_a = set(events_rest) & set(sec_n0_during.keys())
        leaked_to_b = set(events_n0) & set(sec_rest_during.keys())

        # 3. Heal partition
        self.heal_all_partitions()

        # 4. Cocycle reconciliation audit
        witnesses = self.auditor.audit_cluster(self.node_list, topic, auto_reconcile=True)

        # 5. Check post-healing consistency
        final_sections = [n.get_section(topic) for n in self.node_list]
        first_keys = set(final_sections[0].keys())
        all_identical = all(set(s.keys()) == first_keys for s in final_sections)

        return {
            "partition_successful": len(leaked_to_a) == 0 and len(leaked_to_b) == 0,
            "writes_during_split_n0": len(events_n0),
            "writes_during_split_rest": len(events_rest),
            "total_cluster_events": len(first_keys),
            "all_nodes_converged": all_identical,
            "witnesses_count": len(witnesses),
            "latest_witness": witnesses[-1].to_dict() if hasattr(witnesses[-1], "to_dict") else witnesses[-1],
        }
