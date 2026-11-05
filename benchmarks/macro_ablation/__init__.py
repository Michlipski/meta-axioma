"""Meta-Axioma Macro-Level Application Ablation Benchmark Suite (`Axioma Macro-Bench`).

Implements:
- Formal empirical quantification of prompt-to-production compiler architectures.
- Tier 0 Operational Liveness Gatekeeper ([NEG-G1B-002]): Subprocess smoke test multiplier (0.0 if boot fails).
- 5-Dimensional Graded Evaluation Gauntlet:
    1. Spec Fidelity (25%): Bijective AST route & verb coverage
    2. Statechart Integrity (20%): Guard enforcement and illegal transition rejection
    3. Byzantine Chaos Survival (15%): Resilience under concurrent burst & malformed inputs
    4. Zero-Trust Hermeticity (20%): AST inspection against banned dynamic execution and ambient paths
    5. Landauer Efficiency (20%): Token spend efficiency and code density
"""

from .domain_models import (
    AblationMode,
    BenchmarkArchetype,
    EvaluationPassResult,
    MacroBenchmarkReport,
    MacroScorecard,
    Tier0LivenessResult,
)
from .macro_evaluator import MacroEvaluationGauntlet
from .macro_runner import MacroRunner

__all__ = [
    "AblationMode",
    "BenchmarkArchetype",
    "EvaluationPassResult",
    "MacroBenchmarkReport",
    "MacroScorecard",
    "Tier0LivenessResult",
    "MacroEvaluationGauntlet",
    "MacroRunner",
]
