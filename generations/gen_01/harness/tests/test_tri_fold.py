"""Unit tests for the Tri-Fold validation targets and efficacy evaluator."""

from meta_axioma.config import SystemConfig
from meta_axioma.evaluator.evaluator import EfficacyEvaluator
from meta_axioma.simulation.decay import ComputeDecayManager
from meta_axioma.simulation.sandbox import SimulationSandbox
from meta_axioma.types import Axiom, AxiomLevel, AxiomStatus


def test_tri_fold_simulation_and_evaluation():
    config = SystemConfig()
    decay_mgr = ComputeDecayManager(config)
    sandbox = SimulationSandbox()
    evaluator = EfficacyEvaluator(config)

    budget = decay_mgr.calculate_budget(active_axiom_count=2)

    candidate = Axiom(
        id="L1-001",
        level=AxiomLevel.LEVEL_1_STRUCTURAL,
        name="Deterministic State Transitions and Immutability",
        statement="Every architectural state modification must occur via pure deterministic transitions operating over immutable snapshots.",
        formal_expression=r"S_{t+1} = \delta(S_t, a)",
        operational_rule="State mutations without complete lineage and snapshot isolation are rejected.",
        status=AxiomStatus.CANDIDATE,
    )

    results = sandbox.run_simulation(
        candidate=candidate,
        active_axioms=[],
        negative_axioms=[],
        budget=budget,
    )

    assert "target_1_self_constructor" in results
    assert "target_2_self_evaluator" in results
    assert "target_3_control_group" in results

    metrics = evaluator.evaluate_simulation(candidate, results)
    assert metrics.delta_e1 > 0
    assert metrics.delta_e2 > 0
    assert metrics.delta_e3 > 0
    assert metrics.aggregate_delta_e > 0
    assert evaluator.is_strictly_improving(metrics)
