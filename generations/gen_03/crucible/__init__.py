"""The Evolutionary Crucible Package.

Provides protocol interfaces, metrics, and adversarial stress harness.
"""

from .harness import AdversarialCrucibleHarness
from .metrics import CandidateFitnessScorecard, TrialResult, evaluate_candidate_fitness
from .protocol import DistributedConsensusProtocol

__all__ = [
    "AdversarialCrucibleHarness",
    "CandidateFitnessScorecard",
    "DistributedConsensusProtocol",
    "TrialResult",
    "evaluate_candidate_fitness",
]
