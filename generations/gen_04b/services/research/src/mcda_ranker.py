"""Generation 4b Multi-Criteria Decision Analysis (MCDA) TOPSIS Ranker.

Enforces:
- [SPEC-G4B-RESEARCH-MCDA-001]: Rigorous TOPSIS multi-criteria decision ranking weighted by QFD importance.
- Pareto frontier filtering to eliminate dominated options, preventing TOPSIS rank reversal (VULN-QFD-004).
- Deterministic recommendation parity with strict tie detection thresholds.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import math
from typing import Any, Dict, List, Optional, Set

from .qfd_engine import HouseOfQualityIR, OptimizationDirection


@dataclass
class CandidateOptionVector:
    """Candidate proposal option vector with performance attributes and correlation roof penalty."""
    option_id: str
    option_name: str
    performance_vector: Dict[str, float]
    roof_penalty: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "option_id": self.option_id,
            "option_name": self.option_name,
            "performance_vector": dict(self.performance_vector),
            "roof_penalty": self.roof_penalty,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> CandidateOptionVector:
        return cls(
            option_id=str(data["option_id"]),
            option_name=str(data.get("option_name", "")),
            performance_vector={k: float(v) for k, v in data.get("performance_vector", {}).items()},
            roof_penalty=float(data.get("roof_penalty", 0.0)),
        )


@dataclass
class MCDARankResult:
    """Result of Multi-Criteria Decision Analysis (TOPSIS) ranking."""
    rank: int
    option_id: str
    option_name: str
    composite_score: float
    is_recommended: bool
    tie_detected: bool

    def to_dict(self) -> Dict[str, Any]:
        return {
            "rank": self.rank,
            "option_id": self.option_id,
            "option_name": self.option_name,
            "composite_score": self.composite_score,
            "is_recommended": self.is_recommended,
            "tie_detected": self.tie_detected,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> MCDARankResult:
        return cls(
            rank=int(data["rank"]),
            option_id=str(data["option_id"]),
            option_name=str(data.get("option_name", "")),
            composite_score=float(data.get("composite_score", 0.0)),
            is_recommended=bool(data.get("is_recommended", False)),
            tie_detected=bool(data.get("tie_detected", False)),
        )


class MCDARanker:
    """Multi-Criteria Decision Analysis (MCDA) Ranker using vector TOPSIS and Pareto filtering.

    Enforces:
    - [SPEC-G4B-RESEARCH-MCDA-001]
    - Pareto dominance pre-filtering to prevent rank reversal anomalies (VULN-QFD-004)
    - Normalized weighting derived from HouseOfQualityIR normalized_importance
    """

    def filter_pareto_frontier(
        self,
        candidates: List[CandidateOptionVector],
    ) -> List[CandidateOptionVector]:
        """Eliminates Pareto-dominated options to prevent TOPSIS rank reversal (VULN-QFD-004).

        Candidate A dominates Candidate B (A > B) if:
        - For all criteria k: A.performance_vector[k] >= B.performance_vector[k]
        - A.roof_penalty <= B.roof_penalty
        - And at least one inequality is strictly better.
        """
        if len(candidates) <= 1:
            return list(candidates)

        surviving: List[CandidateOptionVector] = []
        for i, cand_b in enumerate(candidates):
            is_dominated = False
            for j, cand_a in enumerate(candidates):
                if i == j:
                    continue

                keys = set(cand_a.performance_vector.keys()) | set(cand_b.performance_vector.keys())
                all_ge = True
                has_strict = False

                # Performance criteria: higher is better
                for k in keys:
                    val_a = cand_a.performance_vector.get(k, 0.0)
                    val_b = cand_b.performance_vector.get(k, 0.0)
                    if val_a < val_b:
                        all_ge = False
                        break
                    if val_a > val_b:
                        has_strict = True

                if not all_ge:
                    continue

                # Roof penalty: lower is better
                if cand_a.roof_penalty > cand_b.roof_penalty:
                    continue
                if cand_a.roof_penalty < cand_b.roof_penalty:
                    has_strict = True

                if all_ge and has_strict:
                    is_dominated = True
                    break

            if not is_dominated:
                surviving.append(cand_b)

        return surviving

    def score_topsis(
        self,
        hoq: HouseOfQualityIR,
        candidates: List[CandidateOptionVector],
        tie_threshold: float = 0.05,
    ) -> List[MCDARankResult]:
        """Executes TOPSIS multi-criteria decision analysis weighted by normalized importance.

        Assigns is_recommended = True strictly to rank 1 unless tie detected (|C_0 - C_1| <= tie_threshold).
        """
        if not candidates:
            return []

        # 1. Determine active criteria from House of Quality
        criteria = [
            cid for cid in hoq.included_characteristics
            if cid in hoq.normalized_importance and hoq.normalized_importance[cid] > 0
        ]
        if not criteria:
            criteria = list(hoq.normalized_importance.keys())
        if not criteria:
            criteria = sorted(list({k for c in candidates for k in c.performance_vector.keys()}))

        char_dir_map = {c.char_id: c.direction for c in hoq.characteristics}

        # 2. Vector normalization denominator: sqrt(sum(x_ij^2))
        denominators: Dict[str, float] = {}
        for crit in criteria:
            sum_sq = sum(c.performance_vector.get(crit, 0.0) ** 2 for c in candidates)
            denominators[crit] = math.sqrt(sum_sq)

        # 3. Calculate weighted normalized values v_ij
        weighted_matrix: List[Dict[str, float]] = []
        for cand in candidates:
            row: Dict[str, float] = {}
            for crit in criteria:
                raw_val = cand.performance_vector.get(crit, 0.0)
                denom = denominators[crit]
                norm_val = (raw_val / denom) if denom > 0.0 else 0.0
                weight = hoq.normalized_importance.get(crit, 1.0)
                row[crit] = norm_val * weight
            weighted_matrix.append(row)

        # 4. Determine Ideal Best (v_j^+) and Ideal Worst (v_j^-)
        ideal_best: Dict[str, float] = {}
        ideal_worst: Dict[str, float] = {}
        for crit in criteria:
            col_vals = [weighted_matrix[i][crit] for i in range(len(candidates))]
            direction = char_dir_map.get(crit, OptimizationDirection.MAXIMIZE)
            if direction == OptimizationDirection.MINIMIZE:
                ideal_best[crit] = min(col_vals) if col_vals else 0.0
                ideal_worst[crit] = max(col_vals) if col_vals else 0.0
            else:  # MAXIMIZE or TARGET
                ideal_best[crit] = max(col_vals) if col_vals else 0.0
                ideal_worst[crit] = min(col_vals) if col_vals else 0.0

        # 5. Calculate Euclidean separation and relative closeness C_i
        scored_candidates: List[tuple[CandidateOptionVector, float]] = []
        for i, cand in enumerate(candidates):
            row = weighted_matrix[i]
            d_plus_sq = sum((row[crit] - ideal_best[crit]) ** 2 for crit in criteria)
            d_minus_sq = sum((row[crit] - ideal_worst[crit]) ** 2 for crit in criteria)
            d_plus = math.sqrt(d_plus_sq)
            d_minus = math.sqrt(d_minus_sq)

            if (d_plus + d_minus) > 0.0:
                closeness = d_minus / (d_plus + d_minus)
            else:
                closeness = 0.5

            # Apply correlation roof contradiction penalty
            net_score = max(0.0, closeness - cand.roof_penalty)
            scored_candidates.append((cand, net_score))

        # 6. Sort descending by net score
        scored_candidates.sort(key=lambda item: item[1], reverse=True)

        # 7. Tie detection between Rank 1 and Rank 2
        tie_detected = False
        if len(scored_candidates) >= 2:
            score_diff = abs(scored_candidates[0][1] - scored_candidates[1][1])
            tie_detected = (score_diff <= tie_threshold)

        # 8. Build rank results
        results: List[MCDARankResult] = []
        for idx, (cand, score) in enumerate(scored_candidates):
            rank = idx + 1
            is_cand_tied = False
            if tie_detected and (idx <= 1 or abs(score - scored_candidates[0][1]) <= tie_threshold):
                is_cand_tied = True

            # Assign is_recommended strictly to rank 1 unless tie detected
            is_rec = (rank == 1 and not tie_detected)

            results.append(
                MCDARankResult(
                    rank=rank,
                    option_id=cand.option_id,
                    option_name=cand.option_name,
                    composite_score=round(score, 4),
                    is_recommended=is_rec,
                    tie_detected=is_cand_tied,
                )
            )

        return results
