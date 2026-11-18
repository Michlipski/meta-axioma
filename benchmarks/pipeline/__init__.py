"""Meta-Axioma Multi-Agent Benchmarking Pipeline Package.

Provides:
- Synthesis engines for single-agent controls and multi-agent causal mesh systems.
- Automated 3-Phase Causal Reactive Pipeline Runner ([INV-G4B-CAUSAL-001..003]).
- Cryptographic execution witnesses and provenance tracking.
"""

from .synthesis_engines import (
    BaseSynthesisEngine,
    SynthesisResult,
    VanillaSynthesisEngine,
    AxiomaCausalMeshEngine,
)
from .causal_pipeline_runner import (
    CausalPipelineRunner,
    BenchmarkTrialConfig,
    BenchmarkRunResult,
)

__all__ = [
    "BaseSynthesisEngine",
    "SynthesisResult",
    "VanillaSynthesisEngine",
    "AxiomaCausalMeshEngine",
    "CausalPipelineRunner",
    "BenchmarkTrialConfig",
    "BenchmarkRunResult",
]
