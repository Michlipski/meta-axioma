"""Metrics and Fitness Evaluation for the Evolutionary Crucible."""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass
from typing import Any, Dict, List

KB = 1.380649e-23
T_ROOM = 298.15
LN2 = math.log(2)
JOULES_PER_BIT = KB * T_ROOM * LN2  # ~ 2.853e-21 J


@dataclass
class TrialResult:
    trial_name: str
    passed: bool
    consistency_rate: float  # 0.0 to 1.0
    messages_routed: int
    duration_ms: float
    erased_bits: float
    joules_dissipated: float
    error_details: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class CandidateFitnessScorecard:
    candidate_name: str
    overall_fitness: float  # 0.0 to 1.0
    consistency_score: float  # weight 0.35
    partition_resilience: float  # weight 0.30
    latency_efficiency: float  # weight 0.20
    thermal_compliance: float  # weight 0.15
    total_erased_bits: float
    total_joules_dissipated: float
    trials: List[TrialResult]

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["trials"] = [t.to_dict() for t in self.trials]
        return d


def evaluate_candidate_fitness(
    candidate_name: str,
    trials: List[TrialResult],
) -> CandidateFitnessScorecard:
    """Computes multidimensional evolutionary fitness across Crucible trials."""
    avg_consistency = sum(t.consistency_rate for t in trials) / max(1, len(trials))
    partition_resilience = 1.0 if all(t.passed for t in trials) else (
        sum(1.0 for t in trials if t.passed) / max(1, len(trials))
    )

    avg_duration = sum(t.duration_ms for t in trials) / max(1, len(trials))
    # Latency efficiency: score degrades if duration > 50ms
    latency_efficiency = max(0.0, min(1.0, 1.0 - (avg_duration / 100.0)))

    total_bits = sum(t.erased_bits for t in trials)
    total_joules = total_bits * JOULES_PER_BIT
    # Thermal compliance: 1.0 if total_joules < 1e-16 J, decays down to 0
    thermal_compliance = max(0.0, min(1.0, 1.0 - (total_joules / 1e-15)))

    # Weighted Composite Fitness
    fitness = (
        0.35 * avg_consistency
        + 0.30 * partition_resilience
        + 0.20 * latency_efficiency
        + 0.15 * thermal_compliance
    )

    return CandidateFitnessScorecard(
        candidate_name=candidate_name,
        overall_fitness=round(fitness, 4),
        consistency_score=round(avg_consistency, 4),
        partition_resilience=round(partition_resilience, 4),
        latency_efficiency=round(latency_efficiency, 4),
        thermal_compliance=round(thermal_compliance, 4),
        total_erased_bits=round(total_bits, 2),
        total_joules_dissipated=total_joules,
        trials=trials,
    )
