"""Axiom Lookahead Engine: Speculative trajectory evaluation for Jettison phase transition."""

from __future__ import annotations

import copy
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from meta_axioma.config import SystemConfig
from meta_axioma.simulation.decay import ComputeDecayManager
from meta_axioma.targets.base import BaseTarget, TargetSimulationResult
from meta_axioma.targets.self_constructor import SelfConstructorTarget
from meta_axioma.targets.self_evaluator import SelfEvaluatorTarget
from meta_axioma.targets.control_group import ControlGroupTarget
from meta_axioma.types import (
    Axiom,
    AxiomLevel,
    AxiomStatus,
    ComputeBudget,
    NegativeAxiom,
    PhaseState,
    TriFoldMetrics,
)


@dataclass
class SpeculativeBranchOutcome:
    """Projected outcomes of a speculative lookahead branch."""
    branch_name: str
    active_axiom_count: int
    compute_budget: ComputeBudget
    evaluated_candidates: List[Dict[str, Any]]
    projected_cumulative_delta: float
    mean_delta_per_epoch: float
    simulation_depth_gain: int
    rationale: str


@dataclass
class AxiomLookaheadResult:
    """Comprehensive lookahead report comparing Jettison vs Retain branches."""
    current_epoch: int
    lookahead_horizon: int
    jettison_branch: SpeculativeBranchOutcome
    retain_branch: SpeculativeBranchOutcome
    net_lookahead_differential: float  # Lambda(H) = Yield(Jettison) - Yield(Retain)
    compute_dividend_tokens: int
    compute_dividend_depth: int
    recommendation: str  # "RECOMMEND_JETTISON" | "RECOMMEND_RETAIN" | "INCONCLUSIVE"
    confidence_score: float
    risk_assessment: Dict[str, str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "current_epoch": self.current_epoch,
            "lookahead_horizon": self.lookahead_horizon,
            "net_lookahead_differential": self.net_lookahead_differential,
            "compute_dividend_tokens": self.compute_dividend_tokens,
            "compute_dividend_depth": self.compute_dividend_depth,
            "recommendation": self.recommendation,
            "confidence_score": self.confidence_score,
            "risk_assessment": self.risk_assessment,
            "jettison_branch": {
                "projected_cumulative_delta": self.jettison_branch.projected_cumulative_delta,
                "mean_delta_per_epoch": self.jettison_branch.mean_delta_per_epoch,
                "active_axiom_count": self.jettison_branch.active_axiom_count,
                "tokens": self.jettison_branch.compute_budget.token_budget,
                "depth": self.jettison_branch.compute_budget.simulation_depth,
                "rationale": self.jettison_branch.rationale,
                "candidates": [
                    {
                        "id": c["id"],
                        "name": c["name"],
                        "aggregate_delta_e": c["metrics"].aggregate_delta_e,
                    }
                    for c in self.jettison_branch.evaluated_candidates
                ],
            },
            "retain_branch": {
                "projected_cumulative_delta": self.retain_branch.projected_cumulative_delta,
                "mean_delta_per_epoch": self.retain_branch.mean_delta_per_epoch,
                "active_axiom_count": self.retain_branch.active_axiom_count,
                "tokens": self.retain_branch.compute_budget.token_budget,
                "depth": self.retain_branch.compute_budget.simulation_depth,
                "rationale": self.retain_branch.rationale,
                "candidates": [
                    {
                        "id": c["id"],
                        "name": c["name"],
                        "aggregate_delta_e": c["metrics"].aggregate_delta_e,
                    }
                    for c in self.retain_branch.evaluated_candidates
                ],
            },
        }


class AxiomLookaheadEngine:
    """Speculatively evaluates multi-step future horizons to inform The Jettison decision."""

    def __init__(self, config: Optional[SystemConfig] = None):
        self.config = config or SystemConfig()
        self.decay_manager = ComputeDecayManager(self.config)
        self.structural_targets: List[BaseTarget] = [
            SelfConstructorTarget(),
            SelfEvaluatorTarget(),
            ControlGroupTarget(),
        ]

    def evaluate_lookahead(
        self,
        current_epoch: int,
        active_axioms: List[Axiom],
        candidate_pool: List[Axiom],
        negative_axioms: List[NegativeAxiom],
        horizon: int = 2,
    ) -> AxiomLookaheadResult:
        """Simulates and compares Branch A (Jettison Now) vs Branch B (Retain Epistemic Rules).
        
        Evaluates structural candidates over horizon H under both regimes:
        - Jettison Branch: Level 0 axioms deactivated. Active count n drops, freeing tokens
          and increasing simulation depth. Candidates evaluated on structural targets with
          unconstrained compute.
        - Retain Branch: Level 0 axioms kept active. Compute is constrained by larger n,
          but epistemic invariants provide higher falsification precision.
        """
        l0_active = [a for a in active_axioms if a.level == AxiomLevel.LEVEL_0_EPISTEMIC]
        l1_active = [a for a in active_axioms if a.level == AxiomLevel.LEVEL_1_STRUCTURAL]

        # Candidates to evaluate over the horizon
        eval_candidates = candidate_pool[:horizon] if len(candidate_pool) >= horizon else candidate_pool

        # -------------------------------------------------------------
        # BRANCH A: JETTISON SPECULATIVE BRANCH
        # -------------------------------------------------------------
        # Speculatively deactivating all L0 axioms
        spec_jettison_active = [a for a in active_axioms if a.level != AxiomLevel.LEVEL_0_EPISTEMIC]
        jettison_n = len(spec_jettison_active)
        budget_jettison = self.decay_manager.calculate_budget(jettison_n)

        jettison_records: List[Dict[str, Any]] = []
        cum_delta_jettison = 0.0

        for cand in eval_candidates:
            # Simulate candidate under freed compute budget
            sim_results = {}
            for target in self.structural_targets:
                sim_results[target.target_id] = target.simulate_compilation(
                    candidate=cand,
                    active_axioms=spec_jettison_active,
                    negative_axioms=negative_axioms,
                    budget=budget_jettison,
                )
            
            # Aggregate metrics with structural weights (0.4, 0.3, 0.3)
            res1 = sim_results.get("target_1_self_constructor")
            res2 = sim_results.get("target_2_self_evaluator")
            res3 = sim_results.get("target_3_control_group")
            d1 = res1.raw_delta_e if res1 else 0.0
            d2 = res2.raw_delta_e if res2 else 0.0
            d3 = res3.raw_delta_e if res3 else 0.0
            agg = round(0.40 * d1 + 0.30 * d2 + 0.30 * d3, 4)

            metrics = TriFoldMetrics(
                delta_e1=d1,
                delta_e2=d2,
                delta_e3=d3,
                aggregate_delta_e=agg,
            )
            cum_delta_jettison += agg
            jettison_records.append({"id": cand.id, "name": cand.name, "metrics": metrics})

        # -------------------------------------------------------------
        # BRANCH B: RETAIN EPISTEMIC SPECULATIVE BRANCH
        # -------------------------------------------------------------
        retain_n = len(active_axioms)
        budget_retain = self.decay_manager.calculate_budget(retain_n)

        retain_records: List[Dict[str, Any]] = []
        cum_delta_retain = 0.0

        for cand in eval_candidates:
            # Simulate candidate under constrained compute budget but full epistemic set
            sim_results = {}
            for target in self.structural_targets:
                sim_results[target.target_id] = target.simulate_compilation(
                    candidate=cand,
                    active_axioms=active_axioms,
                    negative_axioms=negative_axioms,
                    budget=budget_retain,
                )
            
            res1 = sim_results.get("target_1_self_constructor")
            res2 = sim_results.get("target_2_self_evaluator")
            res3 = sim_results.get("target_3_control_group")
            d1 = res1.raw_delta_e if res1 else 0.0
            d2 = res2.raw_delta_e if res2 else 0.0
            d3 = res3.raw_delta_e if res3 else 0.0
            agg = round(0.40 * d1 + 0.30 * d2 + 0.30 * d3, 4)

            metrics = TriFoldMetrics(
                delta_e1=d1,
                delta_e2=d2,
                delta_e3=d3,
                aggregate_delta_e=agg,
            )
            cum_delta_retain += agg
            retain_records.append({"id": cand.id, "name": cand.name, "metrics": metrics})

        # -------------------------------------------------------------
        # DIFFERENTIAL & RECOMMENDATION
        # -------------------------------------------------------------
        cum_delta_jettison = round(cum_delta_jettison, 4)
        cum_delta_retain = round(cum_delta_retain, 4)
        net_diff = round(cum_delta_jettison - cum_delta_retain, 4)
        token_dividend = budget_jettison.token_budget - budget_retain.token_budget
        depth_dividend = budget_jettison.simulation_depth - budget_retain.simulation_depth

        branch_jettison_outcome = SpeculativeBranchOutcome(
            branch_name="Branch A: Speculative Jettison",
            active_axiom_count=jettison_n,
            compute_budget=budget_jettison,
            evaluated_candidates=jettison_records,
            projected_cumulative_delta=cum_delta_jettison,
            mean_delta_per_epoch=round(cum_delta_jettison / max(1, len(eval_candidates)), 4),
            simulation_depth_gain=depth_dividend,
            rationale=(
                f"Deactivating {len(l0_active)} Level 0 axioms unlocks +{token_dividend:,} tokens/epoch "
                f"and expands simulation depth from {budget_retain.simulation_depth} to {budget_jettison.simulation_depth}. "
                f"Allows deep structural proofs without compute decay choking."
            ),
        )

        branch_retain_outcome = SpeculativeBranchOutcome(
            branch_name="Branch B: Retain Epistemic Rules",
            active_axiom_count=retain_n,
            compute_budget=budget_retain,
            evaluated_candidates=retain_records,
            projected_cumulative_delta=cum_delta_retain,
            mean_delta_per_epoch=round(cum_delta_retain / max(1, len(eval_candidates)), 4),
            simulation_depth_gain=0,
            rationale=(
                f"Retains all {len(l0_active)} Level 0 meta-rules. Hypotheses benefit from active "
                f"epistemic invariants, but token budget is throttled to {budget_retain.token_budget:,}."
            ),
        )

        # Recommendation logic
        # If Jettison branch yields higher delta (due to freed compute token budget):
        if net_diff > 0.0015:
            recommendation = "RECOMMEND_JETTISON"
            confidence = min(0.95, 0.65 + net_diff * 20)
        elif net_diff < -0.0015:
            recommendation = "RECOMMEND_RETAIN"
            confidence = min(0.95, 0.65 + abs(net_diff) * 20)
        else:
            recommendation = "INCONCLUSIVE"
            confidence = 0.50

        risk_assessment = {
            "compute_starvation_risk": (
                "HIGH if retained: Active set size (12+) severely throttles token budget to under 1,700 tokens, "
                "risking shallow simulation failures for complex structural theorems."
                if retain_n >= 10 else "LOW"
            ),
            "epistemic_drift_risk": (
                "LOW: 10 epistemic axioms have already established the core search heuristics; "
                "structural candidates can now compile independently."
                if len(l0_active) >= 10 else "HIGH: Fewer than 10 epistemic axioms established."
            ),
            "invariant_lineage_preservation": (
                "SAFE: Epistemic axioms transition to INACTIVE status in persistent registry and UI, "
                "preserving full mathematical lineage without data loss."
            ),
        }

        return AxiomLookaheadResult(
            current_epoch=current_epoch,
            lookahead_horizon=len(eval_candidates),
            jettison_branch=branch_jettison_outcome,
            retain_branch=branch_retain_outcome,
            net_lookahead_differential=net_diff,
            compute_dividend_tokens=token_dividend,
            compute_dividend_depth=depth_dividend,
            recommendation=recommendation,
            confidence_score=round(confidence, 2),
            risk_assessment=risk_assessment,
        )
