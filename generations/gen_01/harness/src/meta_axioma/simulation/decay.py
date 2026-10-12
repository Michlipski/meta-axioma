"""Inverse compute decay manager: T(n) ∝ 1/n."""

from __future__ import annotations

import math
from meta_axioma.config import SystemConfig
from meta_axioma.types import ComputeBudget


class ComputeDecayManager:
    """Calculates compute token budget and simulation depth inversely to active axiom count."""

    def __init__(self, config: SystemConfig):
        self.config = config

    def calculate_budget(self, active_axiom_count: int) -> ComputeBudget:
        """Computes T(n) inversely proportional to active axiom count n.
        
        Formula:
            T(n) = max(T_min, int(T_0 / (1 + alpha * max(0, n - 1))))
            Depth(n) = max(D_min, int(D_0 / (1 + alpha * max(0, n - 1))))
        """
        n = max(1, active_axiom_count)
        decay_factor = 1.0 / (1.0 + self.config.decay_alpha * (n - 1))

        tokens = max(
            self.config.min_token_budget,
            int(self.config.base_token_budget * decay_factor),
        )
        depth = max(
            self.config.min_simulation_depth,
            int(self.config.base_simulation_depth * decay_factor),
        )

        return ComputeBudget(
            active_axiom_count=n,
            token_budget=tokens,
            simulation_depth=depth,
            decay_factor=decay_factor,
        )
