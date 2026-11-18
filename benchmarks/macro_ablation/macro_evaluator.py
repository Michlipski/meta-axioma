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
    ProvenanceEvaluator,
    SpecFidelityEvaluator,
    StatechartEvaluator,
)


class MacroEvaluationGauntlet:
    """The unified multi-dimensional evaluation gauntlet for macro applications."""

    def __init__(
        self,
        liveness_timeout: float = 5.0,
        chaos_timeout: float = 6.0,
        enable_provenance: bool = False,
    ) -> None:
        self.enable_provenance = enable_provenance
        self.liveness_gatekeeper = LivenessGatekeeper(boot_timeout_sec=liveness_timeout)
        self.provenance_evaluator = ProvenanceEvaluator(weight=0.0)
        
        # Standardized 5 functional passes (always sum to 1.00)
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
        provenance_manifest: Optional[Dict[str, Any]] = None,
    ) -> MacroScorecard:
        """Executes the full evaluation gauntlet against an application directory."""
        start_time = time.time()
        app_dir = Path(app_dir).resolve()

        # Step 0: Tier 0 Operational Liveness Gatekeeper
        liveness = self.liveness_gatekeeper.evaluate(app_dir)
        tier0_multiplier = 1.0 if liveness.passed else 0.0

        pass_results: Dict[str, EvaluationPassResult] = {}
        provenance_multiplier = 1.0

        # Step 0B: Multi-Agent Provenance Binary Gatekeeper
        if self.enable_provenance:
            pass_prov = self.provenance_evaluator.evaluate(
                app_dir=app_dir,
                archetype=archetype,
                mode=mode,
                provenance_manifest=provenance_manifest,
            )
            pass_results["provenance"] = pass_prov
            if not pass_prov.passed:
                provenance_multiplier = 0.0

        # Pass 1: Spec Fidelity
        pass_spec = self.spec_evaluator.evaluate(app_dir, archetype)
        pass_results["spec_fidelity"] = pass_spec

        # Pass 2: Statechart Integrity
        pass_state = self.state_evaluator.evaluate(app_dir, archetype)
        pass_results["statechart"] = pass_state

        # Pass 3: Byzantine Chaos Survival (requires live server)
        if liveness.passed:
            pass_chaos = self.chaos_evaluator.evaluate(app_dir, archetype)
        else:
            pass_chaos = EvaluationPassResult(
                pass_name="chaos",
                weight=self.chaos_evaluator.weight,
                raw_score=0.0,
                weighted_score=0.0,
                details={"status": "skipped", "reason": "Tier 0 Liveness Gate failed to boot application"},
                passed=False,
            )
        pass_results["chaos"] = pass_chaos

        # Pass 4: Zero-Trust Hermeticity
        pass_herm = self.hermetic_evaluator.evaluate(app_dir, archetype)
        pass_results["hermetic"] = pass_herm

        # Pass 5: Landauer Efficiency
        pass_eff = self.efficiency_evaluator.evaluate(app_dir, archetype)
        pass_results["efficiency"] = pass_eff

        # Graded score is sum of weighted functional passes (Passes 1-5, total weight = 1.00)
        graded_score = round(
            sum(p.weighted_score for p in pass_results.values() if p.pass_name != "provenance"),
            2,
        )

        # Composite score strictly enforces Tier 0 Multiplier AND Provenance Gatekeeper Multiplier
        composite_score = round(tier0_multiplier * provenance_multiplier * graded_score, 2)
        exec_duration_ms = (time.time() - start_time) * 1000.0

        return MacroScorecard(
            archetype_id=archetype.id,
            ablation_mode=mode,
            tier0_liveness=liveness,
            tier0_multiplier=tier0_multiplier,
            pass_results=pass_results,
            graded_score=graded_score,
            composite_score=composite_score,
            provenance_multiplier=provenance_multiplier,
            execution_time_ms=exec_duration_ms,
            timestamp=time.time(),
            app_path=str(app_dir),
        )
