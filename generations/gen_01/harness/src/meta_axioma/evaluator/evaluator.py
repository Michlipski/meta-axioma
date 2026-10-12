"""Efficacy Evaluator: computes tri-fold metrics, derivative tracking, and phase transitions."""

from __future__ import annotations

from typing import Dict, List
from meta_axioma.config import SystemConfig
from meta_axioma.targets.base import TargetSimulationResult
from meta_axioma.types import Axiom, AxiomLevel, TriFoldMetrics


class EfficacyEvaluator:
    """Evaluates aggregate ΔE across tri-fold validation targets and tracks derivative dE/dt."""

    def __init__(self, config: SystemConfig):
        self.config = config
        self.delta_history: List[float] = []

    def evaluate_simulation(
        self,
        candidate: Axiom,
        simulation_results: Dict[str, TargetSimulationResult],
    ) -> TriFoldMetrics:
        if candidate.level == AxiomLevel.LEVEL_0_EPISTEMIC:
            res1 = simulation_results.get("target_e1_diversity")
            res2 = simulation_results.get("target_e2_velocity")
            res3 = simulation_results.get("target_e3_yield")
        else:
            res1 = simulation_results.get("target_1_self_constructor")
            res2 = simulation_results.get("target_2_self_evaluator")
            res3 = simulation_results.get("target_3_control_group")

        res4 = simulation_results.get("target_4_product_usability")
        d1 = res1.raw_delta_e if res1 else 0.0
        d2 = res2.raw_delta_e if res2 else 0.0
        d3 = res3.raw_delta_e if res3 else 0.0
        d4 = res4.raw_delta_e if res4 else 0.0

        # Check for catastrophic failures or invariant violations
        has_violations = any(
            bool(r.invariant_violations) for r in simulation_results.values()
        )
        all_succeeded = all(
            r.compilation_success for r in simulation_results.values()
        )

        if res4 is not None:
            raw_aggregate = 0.25 * d1 + 0.25 * d2 + 0.25 * d3 + 0.25 * d4
        else:
            raw_aggregate = (
                self.config.target_1_weight * d1
                + self.config.target_2_weight * d2
                + self.config.target_3_weight * d3
            )

        if not all_succeeded or has_violations:
            aggregate = min(-0.05, raw_aggregate)
        else:
            aggregate = raw_aggregate

        aggregate = round(aggregate, 4)

        target_details = {
            t_id: {
                "success": r.compilation_success,
                "delta": r.raw_delta_e,
                "violations": r.invariant_violations,
                "tokens": r.tokens_consumed,
                "depth": r.depth_reached,
            }
            for t_id, r in simulation_results.items()
        }

        return TriFoldMetrics(
            delta_e1=round(d1, 4),
            delta_e2=round(d2, 4),
            delta_e3=round(d3, 4),
            delta_e4=round(d4, 4),
            aggregate_delta_e=aggregate,
            target_details=target_details,
        )


    def is_strictly_improving(self, metrics: TriFoldMetrics) -> bool:
        """Rule 2: ΔE > 0 strict increase requirement."""
        return metrics.aggregate_delta_e > self.config.strict_improvement_threshold

    def record_epoch_delta(self, aggregate_delta: float) -> None:
        """Maintains rolling history for derivative calculation."""
        self.delta_history.append(aggregate_delta)

    def compute_efficacy_derivative(self) -> float:
        """Calculates rolling derivative dE/dt over the rolling window."""
        if not self.delta_history:
            return 0.0
        window = self.delta_history[-self.config.rolling_window_size :]
        derivative = sum(window) / len(window)
        return round(derivative, 4)

    def should_trigger_jettison(
        self,
        current_epoch: int,
        active_l0_count: Optional[int] = None,
        lookahead_differential: Optional[float] = None,
    ) -> bool:
        """Rule 4: Check if efficacy derivative has dropped below threshold and minimum epistemic axioms met.
        
        Incorporates predictive Axiom Lookahead:
        - If lookahead_differential > 0.0020 (post-jettison unconstrained compute strictly dominates)
          and derivative has significantly decelerated, lookahead unlocks the phase transition.
        - If lookahead_differential < 0 (epistemic rules still providing superior guidance),
          premature jettison is suppressed to protect structural compilation quality.
        """
        if current_epoch < self.config.jettison_min_epoch:
            return False

        if active_l0_count is not None and active_l0_count < self.config.min_epistemic_axioms:
            return False

        derivative = self.compute_efficacy_derivative()
        derivative_threshold_met = derivative <= self.config.jettison_epsilon

        if lookahead_differential is not None:
            if lookahead_differential > 0.0020 and derivative <= (self.config.jettison_epsilon * 3.5):
                return True
            if lookahead_differential < 0:
                return False

        return derivative_threshold_met

