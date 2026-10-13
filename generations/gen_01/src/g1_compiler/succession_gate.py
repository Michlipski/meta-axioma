"""Non-Linear Succession Gate for System G_1 Compiler.

Embodying [L1-017] Non-Linear Exploratory Trajectory & Tree Search Invariance
and [L1-018] Independent Decoupled Adversarial Falsification:

Serves as the hard mechanical compiler boundary that verifies the presence of
authentic multi-branch exploration, dead-end falsification witnesses, and adversarial
crucible reports. Raises LinearCompilationViolation if a linear single-shot shortcut is attempted.
"""

from __future__ import annotations

import hashlib
import json
import time
from typing import Any, Dict, Optional

from g1_compiler.types import LinearCompilationViolation, NonLinearSearchTrace


class NonLinearSuccessionGate:
    """The hard mechanical enforcement gate for multi-branch evolutionary succession."""

    MIN_ISLANDS_EXPLORED = 3
    MIN_CANDIDATES_EVALUATED = 3
    MIN_DEAD_ENDS_WITNESSED = 1
    MIN_CONSISTENCY_THRESHOLD = 0.85

    @classmethod
    def verify_trace(cls, trace: Optional[NonLinearSearchTrace]) -> bool:
        """Formally verifies that a succession trace satisfies all non-linear search invariants."""
        if trace is None:
            raise LinearCompilationViolation(
                "Axiomatic Violation [L1-017]: No NonLinearSearchTrace provided. "
                "System G_1 strictly forbids linear single-shot succession synthesis."
            )

        # 1. Minimum Island Branching Rule
        if len(trace.islands_explored) < cls.MIN_ISLANDS_EXPLORED:
            raise LinearCompilationViolation(
                f"Axiomatic Violation [L1-017]: Insufficient island diversity. "
                f"Explored {len(trace.islands_explored)} islands, minimum required is {cls.MIN_ISLANDS_EXPLORED}."
            )

        # 2. Total Candidate Evaluations Rule
        if trace.total_candidates_evaluated < cls.MIN_CANDIDATES_EVALUATED:
            raise LinearCompilationViolation(
                f"Axiomatic Violation [L1-017]: Insufficient candidate depth. "
                f"Evaluated {trace.total_candidates_evaluated} candidates, minimum required is {cls.MIN_CANDIDATES_EVALUATED}."
            )

        # 3. Dead-End Witness Rule (Karl Popper / Lakatos demarcation)
        if len(trace.dead_end_candidates) < cls.MIN_DEAD_ENDS_WITNESSED:
            raise LinearCompilationViolation(
                f"Axiomatic Violation [L1-017]: Missing dead-end falsification witness. "
                f"Found {len(trace.dead_end_candidates)} dead ends, minimum required is {cls.MIN_DEAD_ENDS_WITNESSED}. "
                "Evolution requires documenting falsified hypotheses to prove authentic non-linear branching."
            )

        # 4. Decoupled Adversarial Crucible Witness Rule ([L1-018])
        if not trace.crucible_witnesses:
            raise LinearCompilationViolation(
                "Axiomatic Violation [L1-018]: No decoupled adversarial crucible witnesses found. "
                "Generator-verifier co-authorship is prohibited; an independent chaos witness is mandatory."
            )

        # Verify that the winner exists and survived the adversarial crucible
        winner_witness = next(
            (w for w in trace.crucible_witnesses if w.candidate_id == trace.selected_winner_id),
            None,
        )
        if winner_witness is None:
            raise LinearCompilationViolation(
                f"Axiomatic Violation [L1-018]: Selected winner '{trace.selected_winner_id}' "
                "lacks an independent adversarial crucible stress witness."
            )

        if winner_witness.is_falsified or not winner_witness.passed:
            raise LinearCompilationViolation(
                f"Axiomatic Violation [L1-018]: Selected winner '{trace.selected_winner_id}' "
                "failed adversarial chaos testing (consistency: {winner_witness.consistency_rate:.3f})."
            )

        if winner_witness.consistency_rate < cls.MIN_CONSISTENCY_THRESHOLD:
            raise LinearCompilationViolation(
                f"Axiomatic Violation [L1-018]: Selected winner consistency "
                f"({winner_witness.consistency_rate:.3f}) falls below threshold ({cls.MIN_CONSISTENCY_THRESHOLD})."
            )

        return True

    @classmethod
    def authorize_succession(cls, trace: Optional[NonLinearSearchTrace]) -> str:
        """Validates trace and produces a signed cryptographic succession certificate."""
        cls.verify_trace(trace)
        assert trace is not None

        cert_payload = {
            "trace_id": trace.trace_id,
            "islands_count": len(trace.islands_explored),
            "total_candidates": trace.total_candidates_evaluated,
            "dead_ends_count": len(trace.dead_end_candidates),
            "winner_id": trace.selected_winner_id,
            "authorized_at": time.time(),
            "invariants_satisfied": ["L1-017", "L1-018"],
        }
        cert_token = hashlib.sha256(
            json.dumps(cert_payload, sort_keys=True).encode("utf-8")
        ).hexdigest()

        trace.is_verified = True
        trace.verification_signature = f"CERT_G1_{cert_token[:16].upper()}"
        return trace.verification_signature
