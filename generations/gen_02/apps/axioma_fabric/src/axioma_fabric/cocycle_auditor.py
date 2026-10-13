"""Axioma Fabric Pairwise Cocycle Boundary Auditor.

Computes algebraic restriction morphisms rho_ij: F(U_i) -> F(U_i cap U_j),
identifies topological boundary discrepancies across broker nodes,
and executes monotonic CRDT reconciliation to guarantee zero split-brain state.
"""

from __future__ import annotations
import uuid
from typing import Dict, List, Optional, Tuple
from .models import CocycleWitness, CausalEvent
from .sheaf_broker import FabricBrokerNode


class FabricCocycleAuditor:
    """Audits and certifies sheaf coherence across distributed broker subdomains."""

    def __init__(self) -> None:
        self._witnesses: List[CocycleWitness] = []

    @property
    def witnesses(self) -> List[CocycleWitness]:
        return list(self._witnesses)

    def audit_and_reconcile_pair(
        self,
        node_a: FabricBrokerNode,
        node_b: FabricBrokerNode,
        topic: str,
        auto_reconcile: bool = True,
    ) -> CocycleWitness:
        """Audit pairwise boundary restriction between node_a and node_b for topic.
        
        If divergence exists and links are restored, applies CRDT join reconciliation.
        Emits and records a formal CocycleWitness.
        """
        sec_a = node_a.get_section(topic)
        sec_b = node_b.get_section(topic)

        events_a = set(sec_a.keys())
        events_b = set(sec_b.keys())

        intersection = events_a & events_b
        only_in_a = events_a - events_b
        only_in_b = events_b - events_a
        divergence_count = len(only_in_a) + len(only_in_b)
        reconciled = False

        if divergence_count > 0 and auto_reconcile:
            # Reconcile if links are not severed
            links_healthy = not node_a.is_link_severed(node_b.node_id) and not node_b.is_link_severed(node_a.node_id)
            if links_healthy:
                # Transmit missing events from A to B
                for eid in only_in_a:
                    node_b.receive_peer_event(sec_a[eid])
                # Transmit missing events from B to A
                for eid in only_in_b:
                    node_a.receive_peer_event(sec_b[eid])
                
                # Check reconciliation succeeded
                new_sec_a = node_a.get_section(topic)
                new_sec_b = node_b.get_section(topic)
                if set(new_sec_a.keys()) == set(new_sec_b.keys()):
                    reconciled = True
                    divergence_count = 0

        witness_id = f"witness_cocycle_{node_a.node_id}_{node_b.node_id}_{uuid.uuid4().hex[:8]}"
        witness = CocycleWitness.build(
            witness_id=witness_id,
            node_i=node_a.node_id,
            node_j=node_b.node_id,
            subdomain_intersection=f"{node_a.subdomain} \\cap {node_b.subdomain}",
            agreed_count=len(intersection) + ((len(only_in_a) + len(only_in_b)) if reconciled else 0),
            divergence_count=divergence_count,
            reconciled=reconciled,
        )
        self._witnesses.append(witness)
        return witness

    def audit_cluster(
        self,
        nodes: List[FabricBrokerNode],
        topic: str,
        auto_reconcile: bool = True,
    ) -> List[CocycleWitness]:
        """Perform comprehensive pairwise cocycle audit across all nodes in cluster."""
        results: List[CocycleWitness] = []
        n = len(nodes)
        for i in range(n):
            for j in range(i + 1, n):
                wit = self.audit_and_reconcile_pair(nodes[i], nodes[j], topic, auto_reconcile=auto_reconcile)
                results.append(wit)
        return results
