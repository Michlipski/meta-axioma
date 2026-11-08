"""Generation 4b Quality Function Deployment (QFD) Consistency Auditor.

Enforces:
- [L1-G4B-009]: Socratic Red Team Inversion and Dialectical Pre-Proposal Stress-Testing.
- [INV-G4B-REDTEAM-001]: Zero-bypass audit verification before code modification.
- [INV-G4B-CAUSAL-001]: Strict temporal causality between sealed research artifacts and project proposals.
- Four Core Verifications:
  (1) Temporal Causality: QFD matrix must be sealed before proposal timestamp.
  (2) Zero Orphan Features: All declared proposal features must trace to QFD included characteristics.
  (3) Roof Contradiction Coverage: Negative correlation roof contradictions must be addressed in proposal text.
  (4) Recommendation Parity: Recommended option must match MCDARanker Rank 1.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import time
from typing import Any, Dict, List, Optional

try:
    from generations.gen_04b.services.research.src.qfd_engine import (
        HouseOfQualityIR,
        CorrelationType,
    )
    from generations.gen_04b.services.research.src.mcda_ranker import (
        MCDARanker,
        CandidateOptionVector,
        MCDARankResult,
    )
except ImportError:
    from ...research.src.qfd_engine import (  # type: ignore
        HouseOfQualityIR,
        CorrelationType,
    )
    from ...research.src.mcda_ranker import (  # type: ignore
        MCDARanker,
        CandidateOptionVector,
        MCDARankResult,
    )


class TemporalCausalityViolation(Exception):
    """Raised when QFD matrix is unsealed or timestamp is >= proposal timestamp."""
    pass


class OrphanFeatureViolation(Exception):
    """Raised when declared feature has no lineage in QFD included characteristics."""
    pass


class RoofCoverageViolation(Exception):
    """Raised when negative correlation roof contradictions are unaddressed in proposal."""
    pass


class RecommendationParityViolation(Exception):
    """Raised when recommended option in proposal does not match MCDA Rank 1."""
    pass


@dataclass
class QFDConsistencyAuditResult:
    """Result of QFD Consistency and Traceability Audit."""
    passed: bool
    violations: List[str] = field(default_factory=list)
    checked_features_count: int = 0
    qfd_merkle_root: str = ""
    audit_timestamp_ms: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "passed": self.passed,
            "violations": list(self.violations),
            "checked_features_count": self.checked_features_count,
            "qfd_merkle_root": self.qfd_merkle_root,
            "audit_timestamp_ms": self.audit_timestamp_ms,
        }


class QFDConsistencyAuditor:
    """Sovereign Micro-Auditor verifying strict consistency between QFD and project proposals.

    Enforces:
    - [L1-G4B-009], [INV-G4B-REDTEAM-001]: Pre-proposal adversarial review and invariant verification.
    - [INV-G4B-CAUSAL-001]: Temporal causality between research artifacts and downstream specifications.
    - Zero orphan features: All declared proposal features must trace directly to QFD included characteristics.
    - Roof coverage: All negative correlation roof contradictions must be addressed in proposal text.
    - Recommendation parity: Recommended proposal option must strictly match MCDARanker rank 1.
    """

    def audit_proposal(
        self,
        hoq: HouseOfQualityIR,
        proposal_timestamp_ms: int,
        declared_features: List[str],
        proposal_text: str,
        recommended_option_id: Optional[str] = None,
        candidate_options: Optional[List[CandidateOptionVector]] = None,
        mcda_rank_results: Optional[List[MCDARankResult]] = None,
        raise_on_error: bool = False,
    ) -> QFDConsistencyAuditResult:
        """Executes full 4-barrier QFD consistency audit against a candidate proposal."""
        violations: List[str] = []

        # =========================================================================
        # Barrier 1: Temporal Causality Verification
        # =========================================================================
        if not hoq.is_sealed:
            msg = (
                f"Temporal Causality Violation: House of Quality matrix '{hoq.matrix_id}' "
                "is NOT cryptographically sealed."
            )
            violations.append(msg)
            if raise_on_error:
                raise TemporalCausalityViolation(msg)

        if hoq.timestamp_unix_ms >= proposal_timestamp_ms:
            msg = (
                f"Temporal Causality Violation: QFD timestamp ({hoq.timestamp_unix_ms}ms) "
                f"is not strictly prior to proposal timestamp ({proposal_timestamp_ms}ms)."
            )
            violations.append(msg)
            if raise_on_error:
                raise TemporalCausalityViolation(msg)

        # =========================================================================
        # Barrier 2: Zero Orphan Features (Traceability to QFD Included Characteristics)
        # =========================================================================
        included_set = set(hoq.included_characteristics)
        included_names = {c.name.lower() for c in hoq.characteristics if c.char_id in included_set}

        orphan_features: List[str] = []
        for feat in declared_features:
            feat_norm = feat.strip()
            feat_lower = feat_norm.lower()
            if (feat_norm not in included_set) and (feat_lower not in included_names):
                orphan_features.append(feat)

        if orphan_features:
            msg = (
                f"Orphan Feature Violation: Declared features {orphan_features} "
                f"have no grounding in QFD included characteristics: {list(included_set)}"
            )
            violations.append(msg)
            if raise_on_error:
                raise OrphanFeatureViolation(msg)

        # =========================================================================
        # Barrier 3: Roof Contradiction Coverage
        # =========================================================================
        proposal_text_lower = proposal_text.lower()
        char_map = {c.char_id: c for c in hoq.characteristics}

        negative_roof_edges = [
            edge for edge in hoq.roof_edges
            if edge.correlation in (CorrelationType.NEGATIVE, CorrelationType.STRONG_NEGATIVE)
        ]

        unaddressed_roof_edges: List[str] = []
        for edge in negative_roof_edges:
            char_a = char_map.get(edge.char_id_a)
            char_b = char_map.get(edge.char_id_b)
            name_a = char_a.name.lower() if char_a else ""
            name_b = char_b.name.lower() if char_b else ""
            id_a = edge.char_id_a.lower()
            id_b = edge.char_id_b.lower()

            found_a = (id_a in proposal_text_lower) or (name_a and name_a in proposal_text_lower)
            found_b = (id_b in proposal_text_lower) or (name_b and name_b in proposal_text_lower)

            if not (found_a and found_b):
                unaddressed_roof_edges.append(
                    f"{edge.char_id_a} ({char_a.name if char_a else 'Unknown'}) <-> "
                    f"{edge.char_id_b} ({char_b.name if char_b else 'Unknown'})"
                )

        if unaddressed_roof_edges:
            msg = (
                f"Roof Coverage Violation: Negative correlation roof contradictions "
                f"are unaddressed in proposal text: {unaddressed_roof_edges}"
            )
            violations.append(msg)
            if raise_on_error:
                raise RoofCoverageViolation(msg)

        # =========================================================================
        # Barrier 4: Recommendation Parity
        # =========================================================================
        if recommended_option_id is not None:
            # If rank results not pre-computed but candidates supplied, calculate via MCDARanker
            effective_rank_results = mcda_rank_results
            if effective_rank_results is None and candidate_options is not None:
                ranker = MCDARanker()
                effective_rank_results = ranker.score_topsis(hoq, candidate_options)

            if effective_rank_results:
                rank_1 = next((r for r in effective_rank_results if r.rank == 1), None)
                if rank_1 is None:
                    msg = "Recommendation Parity Violation: No MCDA Rank 1 result found in ranking"
                    violations.append(msg)
                    if raise_on_error:
                        raise RecommendationParityViolation(msg)
                elif not rank_1.is_recommended:
                    msg = (
                        f"Recommendation Parity Violation: MCDA Rank 1 option '{rank_1.option_id}' "
                        f"is NOT marked recommended (tie_detected={rank_1.tie_detected})"
                    )
                    violations.append(msg)
                    if raise_on_error:
                        raise RecommendationParityViolation(msg)
                elif rank_1.option_id != recommended_option_id:
                    msg = (
                        f"Recommendation Parity Violation: Proposal marked '{recommended_option_id}' "
                        f"as recommended, but MCDA Rank 1 is '{rank_1.option_id}' "
                        f"(composite_score={rank_1.composite_score})"
                    )
                    violations.append(msg)
                    if raise_on_error:
                        raise RecommendationParityViolation(msg)

        passed = (len(violations) == 0)
        return QFDConsistencyAuditResult(
            passed=passed,
            violations=violations,
            checked_features_count=len(declared_features),
            qfd_merkle_root=hoq.merkle_root,
            audit_timestamp_ms=int(time.time() * 1000),
        )
