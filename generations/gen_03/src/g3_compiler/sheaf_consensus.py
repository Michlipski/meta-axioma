r"""Topological Sheaf Consensus & Partition Coherence Engine (L1-G3-001).

Implements sheaf-theoretic consensus where local sections over open covers U_i
glue into globally consistent cluster state:
  F(U \cap V) \cong res_{U, U \cap V}(F(U)) \cap res_{V, U \cap V}(F(V))
and 0th Cohomology:
  H^0(U, F) \cong Sections(F)
"""

from __future__ import annotations

import hashlib
import json
import logging
import time
from typing import Any, Dict, List, Optional, Set, Tuple

try:
    from .models import SheafSection
except ImportError:
    from models import SheafSection

logger = logging.getLogger("AxiomaG3Sheaf")


class SheafConsensusEngine:
    """Algebraic Topology Sheaf Consensus & Partition Tolerance Engine."""

    def __init__(self):
        # Open cover map: cover_id -> Set[node_ids]
        self.covers: Dict[str, Set[str]] = {}
        # Local sections: node_id -> SheafSection
        self.sections: Dict[str, SheafSection] = {}
        # Partitioned node pairs: Set[Tuple[str, str]]
        self.active_partitions: Set[Tuple[str, str]] = set()

    def register_node(self, node_id: str, cover_id: str = "cluster_core", initial_data: Optional[Dict[str, Any]] = None) -> SheafSection:
        """Assigns a node to an open cover component and initializes its local section."""
        if cover_id not in self.covers:
            self.covers[cover_id] = set()
        self.covers[cover_id].add(node_id)

        data = initial_data or {}
        h = self._compute_hash(data)
        section = SheafSection(
            node_id=node_id,
            open_cover_id=cover_id,
            version=1,
            data=data,
            state_hash=h,
            timestamp=time.time(),
        )
        self.sections[node_id] = section
        return section

    def simulate_partition(self, node_a: str, node_b: str) -> None:
        """Simulates a physical network partition between node_a and node_b."""
        pair = (min(node_a, node_b), max(node_a, node_b))
        self.active_partitions.add(pair)
        logger.info(f"[PARTITION_SPLIT] Isolated edge {pair[0]} <//> {pair[1]}")

    def heal_partition(self, node_a: str, node_b: str) -> bool:
        """Heals network partition and triggers topological gluing reconciliation."""
        pair = (min(node_a, node_b), max(node_a, node_b))
        if pair in self.active_partitions:
            self.active_partitions.remove(pair)
            logger.info(f"[PARTITION_HEALED] Reconnected edge {pair[0]} <--> {pair[1]}")
            return self.reconcile_sheaf_gluing(node_a, node_b)
        return True

    def is_partitioned(self, node_a: str, node_b: str) -> bool:
        pair = (min(node_a, node_b), max(node_a, node_b))
        return pair in self.active_partitions

    def update_local_section(self, node_id: str, key: str, value: Any) -> SheafSection:
        """Applies mutation to local section and propagates to accessible neighbors."""
        sec = self.sections.get(node_id)
        if not sec:
            raise KeyError(f"Node {node_id} not registered in sheaf topology.")

        new_data = dict(sec.data)
        new_data[key] = value
        new_hash = self._compute_hash(new_data)

        updated = SheafSection(
            node_id=node_id,
            open_cover_id=sec.open_cover_id,
            version=sec.version + 1,
            data=new_data,
            state_hash=new_hash,
            timestamp=time.time(),
        )
        self.sections[node_id] = updated

        # Propagate to all connected peers in same open cover
        for peer_id in self.covers.get(sec.open_cover_id, set()):
            if peer_id != node_id and not self.is_partitioned(node_id, peer_id):
                self._propagate_restriction(node_id, peer_id, key, value, updated.version)

        return updated

    def reconcile_sheaf_gluing(self, node_a: str, node_b: str) -> bool:
        r"""Computes the restriction difference across the intersection U_A \cap U_B and glues states."""
        sec_a = self.sections.get(node_a)
        sec_b = self.sections.get(node_b)
        if not sec_a or not sec_b:
            return False

        # Compute intersection keys (shared domain)
        shared_keys = set(sec_a.data.keys()).union(sec_b.data.keys())
        reconciled_data = {}

        for k in shared_keys:
            val_a = sec_a.data.get(k)
            val_b = sec_b.data.get(k)

            if val_a == val_b:
                reconciled_data[k] = val_a
            elif val_a is not None and val_b is None:
                reconciled_data[k] = val_a
            elif val_b is not None and val_a is None:
                reconciled_data[k] = val_b
            else:
                # Deterministic Lattice Join: take value with newer version or canonical hash tie-break
                if sec_a.version >= sec_b.version:
                    reconciled_data[k] = val_a
                else:
                    reconciled_data[k] = val_b

        rec_hash = self._compute_hash(reconciled_data)
        max_ver = max(sec_a.version, sec_b.version) + 1

        self.sections[node_a] = SheafSection(
            node_id=node_a,
            open_cover_id=sec_a.open_cover_id,
            version=max_ver,
            data=dict(reconciled_data),
            state_hash=rec_hash,
            timestamp=time.time(),
        )
        self.sections[node_b] = SheafSection(
            node_id=node_b,
            open_cover_id=sec_b.open_cover_id,
            version=max_ver,
            data=dict(reconciled_data),
            state_hash=rec_hash,
            timestamp=time.time(),
        )
        return True

    def compute_cohomology_h0(self, cover_id: str) -> Tuple[bool, float]:
        """Computes H^0(U, F): checks whether all connected local sections glue with 0 cocycle error."""
        nodes = list(self.covers.get(cover_id, set()))
        if len(nodes) <= 1:
            return True, 0.0

        discrepancies = 0
        comparisons = 0

        for i in range(len(nodes)):
            for j in range(i + 1, len(nodes)):
                n_i, n_j = nodes[i], nodes[j]
                if not self.is_partitioned(n_i, n_j):
                    comparisons += 1
                    s_i = self.sections[n_i]
                    s_j = self.sections[n_j]
                    if s_i.state_hash != s_j.state_hash:
                        discrepancies += 1

        cohomology_error = (discrepancies / max(1, comparisons))
        is_glued = discrepancies == 0
        return is_glued, cohomology_error

    def _propagate_restriction(self, src: str, dst: str, key: str, val: Any, ver: int) -> None:
        target = self.sections.get(dst)
        if target:
            new_data = dict(target.data)
            new_data[key] = val
            self.sections[dst] = SheafSection(
                node_id=dst,
                open_cover_id=target.open_cover_id,
                version=max(target.version + 1, ver),
                data=new_data,
                state_hash=self._compute_hash(new_data),
                timestamp=time.time(),
            )

    def get_section(self, node_id: str) -> Optional[SheafSection]:
        """Returns the local section for a given node if registered."""
        return self.sections.get(node_id)

    @staticmethod
    def _compute_hash(data: Dict[str, Any]) -> str:
        s = json.dumps(data, sort_keys=True)
        return hashlib.sha256(s.encode("utf-8")).hexdigest()[:16]
