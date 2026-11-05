r"""Pass 5: Landauer Token & LOC Efficiency Evaluator ($S_{eff}$, 20%).

Evaluates:
- Physical Lines of Code (LOC) conciseness excluding empty lines and pure comments.
- Token spend calibration relative to structural capability delivered.
- Penalizes Landauer thermal waste (bloated boilerplate LOC) and empty stubs (<50 LOC).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from ..domain_models import BenchmarkArchetype, EvaluationPassResult


class EfficiencyEvaluator:
    """Evaluates Pass 5: Landauer Token & LOC Efficiency ($S_{eff}$, Weight = 20%)."""

    def __init__(self, weight: float = 0.20) -> None:
        self.weight = weight

    def evaluate(self, app_dir: Path, archetype: BenchmarkArchetype) -> EvaluationPassResult:
        py_files = list(app_dir.rglob("*.py"))
        total_raw_lines = 0
        total_loc = 0  # non-blank, non-comment
        total_bytes = 0

        for py_file in py_files:
            try:
                lines = py_file.read_text(encoding="utf-8").splitlines()
                total_raw_lines += len(lines)
                for line in lines:
                    stripped = line.strip()
                    if stripped and not stripped.startswith("#"):
                        total_loc += 1
                total_bytes += py_file.stat().st_size
            except Exception:
                pass

        target_loc = archetype.target_loc_budget or 350
        target_token_budget = archetype.target_token_budget or 15000

        # Estimated token spend (roughly 3.8 characters per BPE token)
        estimated_token_spend = int(total_bytes / 3.8) + 800

        # Calculate LOC factor
        # Ideal LOC range is [0.5 * target_loc, 1.5 * target_loc]
        if total_loc < 30:
            # Under-emitted stub
            loc_factor = max(0.1, total_loc / 100.0)
        elif total_loc <= target_loc * 1.5:
            # Optimal zone
            loc_factor = 1.0
        else:
            # Over-bloated boilerplate penalty
            excess = total_loc - (target_loc * 1.5)
            loc_factor = max(0.3, 1.0 - (excess / 1000.0))

        # Capability delivery metric (verbs + models declared)
        capabilities = len(archetype.expected_verbs) + len(archetype.expected_models)
        eff_ratio = (capabilities * 25000.0) / max(3000, estimated_token_spend)
        raw_score = min(100.0, eff_ratio * loc_factor)
        raw_score = round(max(0.0, min(100.0, raw_score)), 2)
        weighted_score = round(raw_score * self.weight, 2)

        return EvaluationPassResult(
            pass_name="efficiency",
            weight=self.weight,
            raw_score=raw_score,
            weighted_score=weighted_score,
            details={
                "total_loc": total_loc,
                "target_loc": target_loc,
                "total_raw_lines": total_raw_lines,
                "total_bytes": total_bytes,
                "estimated_bPE_spend": estimated_token_spend,
                "loc_factor": round(loc_factor, 2),
                "capabilities_delivered": capabilities,
            },
            passed=(raw_score >= 60.0),
        )
