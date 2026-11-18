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
        py_files = [p for p in app_dir.rglob("*.py") if "__pycache__" not in p.parts]
        prod_files = []
        test_files = []
        for p in py_files:
            rel_parts = p.relative_to(app_dir).parts if app_dir in p.parents or p == app_dir else p.parts
            if "tests" in rel_parts or p.name.startswith("test_") or p.name.endswith("_test.py"):
                test_files.append(p)
            else:
                prod_files.append(p)

        def _count_metrics(files: list[Path]) -> tuple[int, int, int]:
            raw_lines = 0
            loc = 0
            total_b = 0
            for py_file in files:
                try:
                    lines = py_file.read_text(encoding="utf-8").splitlines()
                    raw_lines += len(lines)
                    for line in lines:
                        stripped = line.strip()
                        if stripped and not stripped.startswith("#"):
                            loc += 1
                    total_b += py_file.stat().st_size
                except Exception:
                    pass
            return raw_lines, loc, total_b

        prod_raw_lines, prod_loc, prod_bytes = _count_metrics(prod_files)
        test_raw_lines, test_loc, test_bytes = _count_metrics(test_files)
        total_raw_lines = prod_raw_lines + test_raw_lines
        total_loc = prod_loc + test_loc
        total_bytes = prod_bytes + test_bytes

        target_loc = archetype.target_loc_budget or 350
        target_token_budget = archetype.target_token_budget or 15000

        # Effective token spend with 25% test weighting so thorough QA suites are not punished
        effective_bytes = prod_bytes + int(0.25 * test_bytes)
        estimated_token_spend = int(effective_bytes / 3.8) + 800
        raw_all_files_token_spend = int(total_bytes / 3.8) + 800

        # Token efficiency factor with Conciseness Protection (VULN-CAL-01)
        lower_band = 0.4 * target_token_budget
        upper_band = 1.25 * target_token_budget
        if estimated_token_spend < lower_band:
            if prod_loc >= max(30, int(0.5 * target_loc)):
                token_factor = 1.0
                calibration_zone = "concise_viable"
            else:
                token_factor = max(0.1, estimated_token_spend / lower_band)
                calibration_zone = "under_emitted_stub"
        elif estimated_token_spend <= upper_band:
            token_factor = 1.0
            calibration_zone = "optimal_band"
        else:
            token_factor = max(0.2, 1.0 - (estimated_token_spend - upper_band) / (2.0 * target_token_budget))
            calibration_zone = "over_budget_waste"

        # Production LOC factor (evaluated on prod_loc only)
        if prod_loc < 30:
            loc_factor = max(0.1, prod_loc / 100.0)
        elif prod_loc <= target_loc * 2.5:
            loc_factor = 1.0
        else:
            excess = prod_loc - (target_loc * 2.5)
            loc_factor = max(0.3, 1.0 - excess / max(1200.0, target_loc * 4.0))

        # Anti-stuffing secondary test-bloat guard (VULN-CAL-02)
        max_reasonable_test_loc = max(600, int(2.5 * max(prod_loc, target_loc)))
        if test_loc <= max_reasonable_test_loc:
            test_bloat_factor = 1.0
        else:
            test_bloat_factor = max(
                0.5,
                1.0 - (test_loc - max_reasonable_test_loc) / max(1500.0, max_reasonable_test_loc * 2.0),
            )

        capabilities = len(archetype.expected_verbs) + len(archetype.expected_models)
        raw_score = round(max(0.0, min(100.0, 100.0 * token_factor * loc_factor * test_bloat_factor)), 2)
        weighted_score = round(raw_score * self.weight, 2)

        return EvaluationPassResult(
            pass_name="efficiency",
            weight=self.weight,
            raw_score=raw_score,
            weighted_score=weighted_score,
            details={
                "total_loc": total_loc,
                "prod_loc": prod_loc,
                "test_loc": test_loc,
                "target_loc": target_loc,
                "total_raw_lines": total_raw_lines,
                "prod_raw_lines": prod_raw_lines,
                "total_bytes": total_bytes,
                "prod_bytes": prod_bytes,
                "test_bytes": test_bytes,
                "estimated_token_spend": estimated_token_spend,
                "estimated_bPE_spend": estimated_token_spend,
                "raw_all_files_token_spend": raw_all_files_token_spend,
                "target_token_budget": target_token_budget,
                "token_factor": round(token_factor, 4),
                "loc_factor": round(loc_factor, 4),
                "test_bloat_factor": round(test_bloat_factor, 4),
                "calibration_zone": calibration_zone,
                "capabilities_delivered": capabilities,
            },
            passed=(raw_score >= 60.0),
        )
