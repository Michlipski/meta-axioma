"""Generation 4b 5D Pareto Vector Optimizer & Novelty Search (`soc_g4b_researcher`).

Enforces:
- Multi-objective Pareto frontier optimization across 5 formal dimensions:
  1. Invariant Coverage (I_coverage in [0, 1])
  2. Byzantine Fault Tolerance (BFT in [0, 1])
  3. Steps-to-Value Ergonomics (Steps <= 3)
  4. Landauer Thermodynamic Efficiency
  5. Lehman & Stanley Novelty Search Sparsity Score
- Non-dominated sorting and historical novelty archive maintenance.
"""

from __future__ import annotations

import math
from typing import Any, Dict, List, Optional, Tuple
import uuid

from .domain_models import (
    DomainInvariantViolation,
    NoveltyArchiveEntry,
)


class ParetoFrontierOptimizer:
    """Multi-objective 5D Pareto vector optimizer and Lehman & Stanley novelty search engine."""

    DIMENSION_KEYS: List[str] = [
        "invariant_coverage",
        "byzantine_resilience",
        "steps_to_value_ergonomics",
        "landauer_efficiency",
        "topological_novelty",
    ]

    def __init__(self, k_nearest_neighbors: int = 3, novelty_threshold: float = 0.25):
        self.k_nn = k_nearest_neighbors
        self.novelty_threshold = novelty_threshold
        self.novelty_archive: List[NoveltyArchiveEntry] = []

    def compute_novelty_score(
        self,
        descriptor: List[float],
    ) -> float:
        """Calculates Lehman & Stanley (2011) novelty metric rho(x) against the archive.

        rho(x) = (1 / k) * sum_{i=1}^k dist(x, mu_i)
        """
        if not self.novelty_archive:
            # First candidate is novel by definition
            return 1.0

        distances: List[float] = []
        for entry in self.novelty_archive:
            other = entry.behavioral_descriptor
            # Euclidean distance across descriptor dimensions
            d_sq = sum((a - b) ** 2 for a, b in zip(descriptor, other))
            distances.append(math.sqrt(d_sq))

        distances.sort()
        k_used = min(self.k_nn, len(distances))
        avg_distance = sum(distances[:k_used]) / float(k_used)
        return float(avg_distance)

    def evaluate_5d_vector(
        self,
        candidate_data: Dict[str, Any],
    ) -> Dict[str, float]:
        """Extracts and normalizes the 5D objective vector for a candidate."""
        # 1. Invariant Coverage [0.0 - 1.0]
        i_cov = float(candidate_data.get("invariant_coverage", 1.0))

        # 2. Byzantine Resilience [0.0 - 1.0]
        bft = float(candidate_data.get("byzantine_resilience", 0.90))

        # 3. Steps-to-Value Ergonomics: min(Steps <= 3) -> 3 / max(3, steps)
        raw_steps = float(candidate_data.get("steps_to_value", 3))
        ergonomics = min(1.0, 3.0 / max(1.0, raw_steps))

        # 4. Landauer Thermodynamic Efficiency: 1.0 - (erased_bits / max_budget)
        erased = float(candidate_data.get("landauer_bits_erased", 5000))
        budget = float(candidate_data.get("landauer_budget_bits", 20000))
        landauer_eff = max(0.0, min(1.0, 1.0 - (erased / max(1.0, budget))))

        # 5. Topological Novelty Sparsity Score
        descriptor = candidate_data.get("behavioral_descriptor", [i_cov, bft, ergonomics, landauer_eff])
        novelty = self.compute_novelty_score(descriptor)

        vector = {
            "invariant_coverage": i_cov,
            "byzantine_resilience": bft,
            "steps_to_value_ergonomics": ergonomics,
            "landauer_efficiency": landauer_eff,
            "topological_novelty": novelty,
        }

        # Store candidate descriptor for potential archive addition
        if novelty >= self.novelty_threshold:
            self._add_to_archive(candidate_data, descriptor, novelty)

        return vector

    def dominates(self, vec_a: Dict[str, float], vec_b: Dict[str, float]) -> bool:
        """Pareto dominance test: A dominates B iff A >= B in all dimensions and A > B in at least one."""
        greater_or_equal = True
        strictly_greater = False

        for dim in self.DIMENSION_KEYS:
            val_a = vec_a.get(dim, 0.0)
            val_b = vec_b.get(dim, 0.0)
            if val_a < val_b:
                greater_or_equal = False
                break
            if val_a > val_b:
                strictly_greater = True

        return greater_or_equal and strictly_greater

    def filter_pareto_frontier(
        self,
        candidates: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Filters a set of candidates down to the non-dominated Pareto frontier."""
        if not candidates:
            return []

        # Evaluate vectors
        scored_candidates: List[Tuple[Dict[str, Any], Dict[str, float]]] = [
            (c, self.evaluate_5d_vector(c)) for c in candidates
        ]

        frontier: List[Dict[str, Any]] = []

        for candidate_a, vec_a in scored_candidates:
            is_dominated = False
            for _, vec_b in scored_candidates:
                if self.dominates(vec_b, vec_a):
                    is_dominated = True
                    break
            if not is_dominated:
                # Attach computed 5D vector to result metadata
                res = dict(candidate_a)
                res["pareto_vector"] = vec_a
                frontier.append(res)

        return frontier

    def rank_candidates(
        self,
        candidates: List[Dict[str, Any]],
        weights: Optional[Dict[str, float]] = None,
    ) -> List[Tuple[Dict[str, Any], float]]:
        """Ranks candidates by scalar weighted sum of their 5D Pareto vector."""
        if weights is None:
            weights = {k: 0.20 for k in self.DIMENSION_KEYS}

        total_weight = sum(weights.values())
        if abs(total_weight - 1.0) > 1e-4:
            raise DomainInvariantViolation(f"Scoring weights must sum to 1.0, got {total_weight}")

        ranked: List[Tuple[Dict[str, Any], float]] = []
        for cand in candidates:
            vec = self.evaluate_5d_vector(cand)
            score = sum(vec[dim] * weights[dim] for dim in self.DIMENSION_KEYS)
            ranked.append((cand, score))

        ranked.sort(key=lambda pair: pair[1], reverse=True)
        return ranked

    def _add_to_archive(
        self,
        candidate_data: Dict[str, Any],
        descriptor: List[float],
        novelty: float,
    ) -> None:
        """Internal helper to archive a behaviorally novel candidate."""
        entry_id = f"arch_{uuid.uuid4().hex[:8]}"
        entry = NoveltyArchiveEntry(
            archive_id=entry_id,
            topology_signature=candidate_data.get("topology_hash", "UNKNOWN_HASH"),
            weisfeiler_lehman_hash=candidate_data.get("wl_hash", "UNKNOWN_WL"),
            behavioral_descriptor=descriptor,
            novelty_score=novelty,
        )
        entry.validate_invariants()
        self.novelty_archive.append(entry)
