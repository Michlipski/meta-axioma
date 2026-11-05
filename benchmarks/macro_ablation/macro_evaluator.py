"""Macro-Evaluation Gauntlet (`Axioma Macro-Bench`).

Coordinates:
- Tier 0 Operational Liveness Gatekeeper ([NEG-G1B-002])
- Pass 1: Bijective Specification Fidelity (25%)
- Pass 2: Statechart & Invariant Integrity (20%)
- Pass 3: Byzantine Chaos Survival (15%)
- Pass 4: Zero-Trust AST Hermeticity (20%)
- Pass 5: Landauer Token & LOC Efficiency (20%)

Enforces the canonical composite score equation:
Composite Score = Tier0_Multiplier * (0.25 * S_spec + 0.20 * S_state + 0.15 * S_chaos + 0.20 * S_hermetic + 0.20 * S_eff)
"""

from __future__ import annotations

from pathlib import Path
import time
from typing import Dict, Optional

from .domain_models import (
    AblationMode,
    BenchmarkArchetype,
    EvaluationPassResult,
    MacroScorecard,
    Tier0LivenessResult,
)
from .evaluators import (
    ChaosEvaluator,
    EfficiencyEvaluator,
    HermeticEvaluator,
    LivenessGatekeeper,
    SpecFidelityEvaluator,
    StatechartEvaluator,
)


class MacroEvaluationGauntlet:
    """The unified 5-dimensional evaluation gauntlet for macro applications."""

    def __init__(
        self,
        liveness_timeout: float = 5.0,
        chaos_timeout: float = 6.0,
    ) -> None:
        self.liveness_gatekeeper = LivenessGatekeeper(boot_timeout_sec=liveness_timeout)
        self.spec_evaluator = SpecFidelityEvaluator(weight=0.25)
        self.state_evaluator = StatechartEvaluator(weight=0.20)
        self.chaos_evaluator = ChaosEvaluator(weight=0.15, timeout_sec=chaos_timeout)
        self.hermetic_evaluator = HermeticEvaluator(weight=0.20)
        self.efficiency_evaluator = EfficiencyEvaluator(weight=0.20)

    def evaluate_app(
        self,
        app_dir: Path,
        archetype: BenchmarkArchetype,
        mode: AblationMode = AblationMode.FULL_G4B,
    ) -> MacroScorecard:
        """Executes the full evaluation gauntlet against an application directory."""
        start_time = time.time()
        app_dir = Path(app_dir).resolve()

        # Step 0: Tier 0 Operational Liveness Gatekeeper
        liveness = self.liveness_gatekeeper.evaluate(app_dir)
        tier0_multiplier = 1.0 if liveness.passed else 0.0

        # Pass 1: Spec Fidelity
        pass_spec = self.spec_evaluator.evaluate(app_dir, archetype)

        # Pass 2: Statechart Integrity
        pass_state = self.state_evaluator.evaluate(app_dir, archetype)

        # Pass 3: Byzantine Chaos Survival (requires live server)
        if liveness.passed:
            pass_chaos = self.chaos_evaluator.evaluate(app_dir, archetype)
        else:
            pass_chaos = EvaluationPassResult(
                pass_name="chaos",
                weight=0.15,
                raw_score=0.0,
                weighted_score=0.0,
                details={"status": "skipped", "reason": "Tier 0 Liveness Gate failed to boot application"},
                passed=False,
            )

        # Pass 4: Zero-Trust Hermeticity
        pass_herm = self.hermetic_evaluator.evaluate(app_dir, archetype)

        # Pass 5: Landauer Efficiency
        pass_eff = self.efficiency_evaluator.evaluate(app_dir, archetype)

        pass_results: Dict[str, EvaluationPassResult] = {
            "spec_fidelity": pass_spec,
            "statechart": pass_state,
            "chaos": pass_chaos,
            "hermetic": pass_herm,
            "efficiency": pass_eff,
        }

        # Graded score is sum of weighted pass scores (0.0 - 100.0)
        graded_score = round(
            pass_spec.weighted_score
            + pass_state.weighted_score
            + pass_chaos.weighted_score
            + pass_herm.weighted_score
            + pass_eff.weighted_score,
            2,
        )

        # Composite score strictly enforces Tier 0 Multiplier
        composite_score = round(tier0_multiplier * graded_score, 2)
        exec_duration_ms = (time.time() - start_time) * 1000.0

        return MacroScorecard(
            archetype_id=archetype.id,
            ablation_mode=mode,
            tier0_liveness=liveness,
            tier0_multiplier=tier0_multiplier,
            pass_results=pass_results,
            graded_score=graded_score,
            composite_score=composite_score,
            execution_time_ms=exec_duration_ms,
            timestamp=time.time(),
            app_path=str(app_dir),
        )
