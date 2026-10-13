"""Axioma Generation 3 High-Level Jettison (HLJ) Gate.

Formally evaluates whether Generation 3 has converged to the High-Level Jettison,
terminating recursive compiler self-search and dedicating all future compute tokens
to production non-generator software systems per [L1-G3-005] and [L1-G3-006].
"""

from __future__ import annotations
import hashlib
import json
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


class JettisonConvergenceError(Exception):
    """Raised when prerequisites for the High-Level Jettison are not met."""
    pass


@dataclass(frozen=True)
class HighLevelJettisonCertificate:
    """Cryptographic certificate attesting completion of the High-Level Jettison."""
    certificate_id: str
    generation: int
    jettison_ratio: float
    target_scores: Dict[str, float]
    user_zero_verified: bool
    observability_verified: bool
    g2_successor_token: str
    timestamp: float
    certificate_hash: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "certificate_id": self.certificate_id,
            "generation": self.generation,
            "jettison_ratio": self.jettison_ratio,
            "target_scores": self.target_scores,
            "user_zero_verified": self.user_zero_verified,
            "observability_verified": self.observability_verified,
            "g2_successor_token": self.g2_successor_token,
            "timestamp": self.timestamp,
            "certificate_hash": self.certificate_hash,
        }


class HighLevelJettisonGate:
    """Mechanical gate evaluating convergence to the High-Level Jettison."""

    MIN_JETTISON_RATIO = 0.85
    MIN_AGGREGATE_DELTA = 0.90

    @classmethod
    def evaluate_jettison_readiness(
        cls,
        target_results: List[Dict[str, Any]],
        g2_certificate: str,
        user_zero_passed: bool,
        observability_valid: bool,
        meta_compiler_tokens: float,
        production_app_tokens: float,
    ) -> HighLevelJettisonCertificate:
        """Evaluate all formal prerequisites for executing the High-Level Jettison."""
        # 1. Verify G2 certificate lineage
        if not g2_certificate or not g2_certificate.startswith("CERT_G2_"):
            raise JettisonConvergenceError(
                f"[L1-G3-006 VETO]: Invalid or missing Generation 2 succession certificate '{g2_certificate}'."
            )

        # 2. Verify all targets passed
        failed_targets = [r["target_id"] for r in target_results if not r.get("passed", False)]
        if failed_targets:
            raise JettisonConvergenceError(
                f"[L1-G3-005 VETO]: Unmet G3 evaluation targets: {failed_targets}"
            )

        # 3. Check aggregate delta score
        aggregate_delta = sum(r.get("weighted_score", 0.0) for r in target_results)
        if aggregate_delta < cls.MIN_AGGREGATE_DELTA:
            raise JettisonConvergenceError(
                f"[L1-G3-005 VETO]: Aggregate target delta insufficient ({aggregate_delta:.3f} < {cls.MIN_AGGREGATE_DELTA})."
            )

        # 4. Check User Zero direct grounding
        if not user_zero_passed:
            raise JettisonConvergenceError(
                "[L1-G3-003 VETO]: User Zero interaction metrics not verified or synthetic fraud detected."
            )

        # 5. Check observability scaffolding
        if not observability_valid:
            raise JettisonConvergenceError(
                "[L1-G3-003 VETO]: Production OpenTelemetry / Prometheus export scaffolding not operational."
            )

        # 6. Calculate Jettison Ratio: Prod / (Prod + Meta)
        total_tokens = meta_compiler_tokens + production_app_tokens
        jettison_ratio = (production_app_tokens / total_tokens) if total_tokens > 0 else 0.0
        if jettison_ratio < cls.MIN_JETTISON_RATIO:
            raise JettisonConvergenceError(
                f"[L1-G3-005 VETO]: Jettison Ratio insufficient ({jettison_ratio:.3f} < {cls.MIN_JETTISON_RATIO}). "
                "Too much compute remains trapped in compiler recursion rather than production software."
            )

        # Generate cryptographic certificate
        now = time.time()
        scores = {r["target_id"]: r.get("weighted_score", 0.0) for r in target_results}
        payload = f"HLJ:GEN3:{jettison_ratio:.4f}:{g2_certificate}:{user_zero_passed}:{now}"
        cert_hash = hashlib.sha256(payload.encode("utf-8")).hexdigest()
        cert_id = f"CERT_HLJ_{cert_hash[:16].upper()}"

        return HighLevelJettisonCertificate(
            certificate_id=cert_id,
            generation=3,
            jettison_ratio=round(jettison_ratio, 4),
            target_scores=scores,
            user_zero_verified=user_zero_passed,
            observability_verified=observability_valid,
            g2_successor_token=g2_certificate,
            timestamp=now,
            certificate_hash=cert_hash,
        )
