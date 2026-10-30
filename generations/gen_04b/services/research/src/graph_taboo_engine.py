"""Generation 4b Graph Taboo & Weisfeiler-Lehman Distance Engine (`soc_g4b_researcher`).

Enforces:
- [L1-G4B-004] Prevention of Mode Collapse & Cosmetic Plagiarism across candidate architectures.
- Weisfeiler-Lehman (WL) topological graph hashing.
- Normalized graph edit distance threshold D(G_i, G_j) >= 0.40.
- Automatic routing to Mode Collapse Enclave if D(G_i, G_j) < 0.40.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import hashlib
import json
from typing import Any, Dict, List, Optional, Set, Tuple
import uuid

from .domain_models import (
    DomainInvariantViolation,
    TabooDistanceMatrix,
)


class TabooDistanceViolation(Exception):
    """Raised when two candidate architectures violate the structural diversity threshold D >= 0.40."""
    pass


class ModeCollapseEnclaveTriggered(Exception):
    """Raised when mode collapse is trapped, mandating dialectical inversion."""
    pass


class GraphTabooEngine:
    """Weisfeiler-Lehman graph hash calculator and normalized topological distance engine."""

    def __init__(
        self,
        min_distance_threshold: float = 0.40,
        wl_iterations: int = 3,
        node_ip: str = "192.168.40.30",
        port: int = 8203,
    ):
        if node_ip in ("127.0.0.1", "localhost", "::1", "127.0.1.1") or node_ip.startswith("127."):
            raise DomainInvariantViolation(
                f"[L1-G3B-012] Anti-Loopback Invariant: GraphTabooEngine node_ip cannot bind to loopback ({node_ip}). "
                f"Must bind to routable cluster subnet (e.g., 192.168.40.x)."
            )
        if min_distance_threshold < 0.40:
            raise DomainInvariantViolation(
                f"min_distance_threshold cannot be set below 0.40, got {min_distance_threshold}"
            )
        self.min_distance_threshold = min_distance_threshold
        self.wl_iterations = wl_iterations
        self.node_ip = node_ip
        self.port = port
        self.history_archive: List[Dict[str, Any]] = []

    def compute_wl_hash_and_features(self, topology: Dict[str, Any]) -> Tuple[str, Counter]:
        """Computes the Weisfeiler-Lehman graph hash and multiset feature vector.

        Algorithm:
        1. Base color: node role + degree.
        2. Iterative aggregation: c^(t+1)(v) = H(c^(t)(v) || sorted([c^(t)(u) for u in neighbors])).
        3. Multiset accumulation across all iterations.
        """
        nodes = topology.get("nodes", [])
        edges = topology.get("edges", [])

        if not nodes:
            empty_hash = hashlib.sha256(b"EMPTY_GRAPH").hexdigest()
            return empty_hash, Counter({"EMPTY": 1})

        # Build adjacency map
        adj: Dict[str, List[str]] = {n["node_id"]: [] for n in nodes}
        for e in edges:
            src = e.get("source")
            dst = e.get("target")
            if src in adj and dst in adj:
                adj[src].append(dst)
                adj[dst].append(src)  # Treat as undirected for topological neighborhood

        # Step 1: Initial coloring
        colors: Dict[str, str] = {}
        for n in nodes:
            nid = n["node_id"]
            role = n.get("role", "WORKER")
            deg = len(adj[nid])
            colors[nid] = hashlib.sha256(f"INIT:{role}:DEG{deg}".encode("utf-8")).hexdigest()[:12]

        feature_multiset: Counter = Counter(colors.values())

        # Step 2: WL Iterations
        for it in range(self.wl_iterations):
            new_colors: Dict[str, str] = {}
            for nid in adj:
                neighbor_colors = sorted([colors[neighbor] for neighbor in adj[nid]])
                compressed = f"{colors[nid]}|" + ",".join(neighbor_colors)
                new_c = hashlib.sha256(f"IT{it}:{compressed}".encode("utf-8")).hexdigest()[:12]
                new_colors[nid] = new_c
            colors = new_colors
            feature_multiset.update(colors.values())

        # Step 3: Full graph signature
        sorted_features = sorted(f"{k}:{v}" for k, v in feature_multiset.items())
        final_hash = hashlib.sha256(":".join(sorted_features).encode("utf-8")).hexdigest()

        return final_hash, feature_multiset

    def compute_normalized_graph_distance(
        self,
        features_1: Counter,
        features_2: Counter,
    ) -> float:
        """Computes the normalized multiset distance: D(G1, G2) = 1.0 - (2 * |G1 ∩ G2|) / (|G1| + |G2|)."""
        intersection_size = sum((features_1 & features_2).values())
        total_size = sum(features_1.values()) + sum(features_2.values())

        if total_size == 0:
            return 0.0

        similarity = (2.0 * intersection_size) / float(total_size)
        distance = 1.0 - similarity
        return max(0.0, min(1.0, distance))

    def evaluate_pair(
        self,
        topo_a: Dict[str, Any],
        topo_b: Dict[str, Any],
    ) -> float:
        """Evaluates normalized topological distance between two candidate graphs."""
        _, f_a = self.compute_wl_hash_and_features(topo_a)
        _, f_b = self.compute_wl_hash_and_features(topo_b)
        return self.compute_normalized_graph_distance(f_a, f_b)

    def compute_normalized_distance(
        self,
        g1: Any,
        g2: Any,
    ) -> float:
        """Computes normalized topological distance between two topologies or feature counters."""
        if isinstance(g1, dict) and isinstance(g2, dict):
            return self.evaluate_pair(g1, g2)
        if isinstance(g1, Counter) and isinstance(g2, Counter):
            return self.compute_normalized_graph_distance(g1, g2)
        return self.evaluate_pair(g1, g2)

    def evaluate_candidate_diversity(
        self,
        candidate_topo: Dict[str, Any],
        existing_topologies: List[Dict[str, Any]],
    ) -> float:
        """Evaluates a candidate topology against existing topologies.

        Raises TabooDistanceViolation if min distance < min_distance_threshold.
        Returns the minimum distance observed.
        """
        if not existing_topologies:
            return 1.0

        min_dist = 1.0
        for existing in existing_topologies:
            dist = self.evaluate_pair(candidate_topo, existing)
            if dist < min_dist:
                min_dist = dist
            if dist < self.min_distance_threshold:
                raise TabooDistanceViolation(
                    f"[Mode Collapse Trap] Candidate distance {dist:.4f} < {self.min_distance_threshold:.4f}. "
                    f"Structural diversity invariant violated!"
                )
        return min_dist

    def compute_taboo_matrix(
        self,
        topologies: List[Dict[str, Any]],
        island_ids: Optional[List[str]] = None,
        matrix_id: Optional[str] = None,
    ) -> TabooDistanceMatrix:
        """Calculates the full all-pairs distance matrix across candidate topologies."""
        if len(topologies) < 2:
            raise DomainInvariantViolation("Taboo matrix requires at least 2 candidate topologies.")

        num_graphs = len(topologies)
        ids = island_ids or [t.get("island_id", f"island_{i}") for i, t in enumerate(topologies)]

        # Precompute features
        features = [self.compute_wl_hash_and_features(t)[1] for t in topologies]

        distance_entries: Dict[str, float] = {}
        breaches: List[Tuple[str, str, float]] = []

        for i in range(num_graphs):
            for j in range(i + 1, num_graphs):
                pair_key = f"{ids[i]}:{ids[j]}"
                dist = self.compute_normalized_graph_distance(features[i], features[j])
                distance_entries[pair_key] = dist
                if dist < self.min_distance_threshold:
                    breaches.append((ids[i], ids[j], dist))

        if breaches:
            first_breach = breaches[0]
            raise TabooDistanceViolation(
                f"[Mode Collapse Trap] Distance between {first_breach[0]} and {first_breach[1]} "
                f"is {first_breach[2]:.4f} < threshold {self.min_distance_threshold:.4f}. "
                f"Candidate exhibits cosmetic plagiarism!"
            )

        m_id = matrix_id or f"tdm_{uuid.uuid4().hex[:8]}"
        matrix = TabooDistanceMatrix(
            matrix_id=m_id,
            island_ids=ids,
            distance_entries=distance_entries,
            min_distance_threshold=self.min_distance_threshold,
        )
        matrix.validate_invariants()
        return matrix

    def check_candidate_against_archive(
        self,
        candidate_topo: Dict[str, Any],
    ) -> Tuple[bool, float, Optional[str]]:
        """Checks a newly synthesized candidate against past accepted topologies."""
        _, cand_features = self.compute_wl_hash_and_features(candidate_topo)

        min_dist = 1.0
        closest_id = None

        for archived in self.history_archive:
            _, arch_features = self.compute_wl_hash_and_features(archived)
            d = self.compute_normalized_graph_distance(cand_features, arch_features)
            if d < min_dist:
                min_dist = d
                closest_id = archived.get("topology_hash")

        is_novel = (min_dist >= self.min_distance_threshold) or (len(self.history_archive) == 0)
        return is_novel, min_dist, closest_id

    def register_in_archive(self, topology: Dict[str, Any]) -> str:
        """Stores an approved topology into the historical archive."""
        wl_hash, _ = self.compute_wl_hash_and_features(topology)
        record = dict(topology)
        record["wl_hash"] = wl_hash
        self.history_archive.append(record)
        return wl_hash
