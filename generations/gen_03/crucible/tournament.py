"""Evolutionary Tournament Runner for Generation 3 Epoch 2.

Pits Candidate Alpha (Sheaf), Candidate Beta (Delta-CRDT), and Candidate Gamma (Raft)
against the Adversarial Crucible to empirically measure fitness, failure modes,
and thermodynamic dissipation.
"""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List

# Ensure crucible and candidates are importable
g3_root = Path(__file__).parent.parent
sys.path.insert(0, str(g3_root))

from crucible.harness import AdversarialCrucibleHarness
from crucible.metrics import CandidateFitnessScorecard
from candidates.candidate_sheaf import CandidateSheafProtocol
from candidates.candidate_crdt import CandidateDeltaCRDTProtocol
from candidates.candidate_raft import CandidateRaftQuorumProtocol
from candidates.candidate_hybrid import CandidateHybridSheafQuorumProtocol

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("Epoch3Tournament")


def run_tournament(epoch_num: int = 3) -> Dict[str, Any]:
    harness = AdversarialCrucibleHarness(random_seed=42)

    candidates = [
        CandidateSheafProtocol(),
        CandidateDeltaCRDTProtocol(),
        CandidateRaftQuorumProtocol(),
        CandidateHybridSheafQuorumProtocol(),
    ]

    scorecards: List[CandidateFitnessScorecard] = []

    logger.info("⚔️  Starting Evolutionary Crucible Tournament (Epoch 2)...")
    for cand in candidates:
        logger.info(f"👉 Evaluating {cand.name}...")
        card = harness.run_all_trials(cand)
        scorecards.append(card)
        logger.info(
            f"   Fitness: {card.overall_fitness:.4f} | "
            f"Consistency: {card.consistency_score:.2%} | "
            f"Partition: {card.partition_resilience:.2%} | "
            f"Erased Bits: {card.total_erased_bits:.1f}"
        )

    # Rank by composite fitness
    scorecards.sort(key=lambda c: c.overall_fitness, reverse=True)

    winner = scorecards[0]
    logger.info(f"🏆 Tournament Winner: {winner.candidate_name} (Fitness: {winner.overall_fitness:.4f})")

    # Serialize results to Epoch dataset
    results_dict = {
        "generation": "gen_03",
        "epoch": epoch_num,
        "phase": f"PHASE_{epoch_num}_EMPIRICAL_EVOLUTIONARY_TOURNAMENT",
        "crucible_version": "1.0.0",
        "candidates_count": len(candidates),
        "rankings": [c.to_dict() for c in scorecards],
        "winner": winner.to_dict(),
    }

    out_json = g3_root / "epochs" / "data" / f"epoch_{epoch_num:03d}.json"
    out_json.parent.mkdir(parents=True, exist_ok=True)
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(results_dict, f, indent=2)

    logger.info(f"📁 Telemetry saved to {out_json}")
    return results_dict


if __name__ == "__main__":
    run_tournament()
