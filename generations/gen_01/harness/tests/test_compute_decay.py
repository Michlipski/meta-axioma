"""Unit tests for the inverse compute decay schedule."""

from meta_axioma.config import SystemConfig
from meta_axioma.simulation.decay import ComputeDecayManager


def test_inverse_compute_decay_scaling():
    config = SystemConfig(
        base_token_budget=10000,
        base_simulation_depth=8,
        decay_alpha=0.5,
        min_token_budget=1000,
        min_simulation_depth=2,
    )
    manager = ComputeDecayManager(config)

    # When n=1 active axiom
    b1 = manager.calculate_budget(1)
    assert b1.token_budget == 10000
    assert b1.simulation_depth == 8

    # When n=3 active axioms
    b3 = manager.calculate_budget(3)
    # decay_factor = 1 / (1 + 0.5 * 2) = 0.5
    assert b3.token_budget == 5000
    assert b3.simulation_depth == 4

    # When n=10 active axioms
    b10 = manager.calculate_budget(10)
    assert b10.token_budget < b3.token_budget
    assert b10.simulation_depth <= b3.simulation_depth
    assert b10.token_budget >= config.min_token_budget
