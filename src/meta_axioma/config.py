"""System configuration and hyperparameter constants."""

from pathlib import Path
from dataclasses import dataclass, field


@dataclass(frozen=True)
class SystemConfig:
    """Hyperparameters and configuration for the Axiom Bootstrapper."""
    # Paths
    root_dir: Path = Path(__file__).resolve().parent.parent.parent
    axioms_path: Path = root_dir / "generation_01_axioms.md"
    architecture_path: Path = root_dir / "generation_01_architecture.md"
    active_generation: str = "gen_01"
    generations_dir: Path = root_dir / "generations"
    reports_dir: Path = root_dir / "generations" / "gen_01" / "epochs"

    # Compute Decay Hyperparameters T(n) ∝ 1/n
    base_token_budget: int = 10000
    base_simulation_depth: int = 8
    decay_alpha: float = 0.5  # Decay coefficient
    min_token_budget: int = 1000
    min_simulation_depth: int = 2

    # Efficacy Thresholds & Tri-Fold Weights
    target_1_weight: float = 0.35  # Self-Constructor
    target_2_weight: float = 0.35  # Self-Evaluator
    target_3_weight: float = 0.30  # Control Group
    strict_improvement_threshold: float = 0.0  # ΔE must be strictly > 0
    candidate_pool_size: int = 3  # Multi-candidate tournament batch size

    # Phase Transition (The Jettison)
    min_epistemic_axioms: int = 10  # Must establish at least 10 L0 epistemic axioms before Phase 2
    jettison_min_epoch: int = 10    # Earliest epoch permitted for jettison
    jettison_epsilon: float = 0.002 # Triggered only when rolling dE/dt < epsilon (true plateau)
    rolling_window_size: int = 3    # Window for derivative smoothing
