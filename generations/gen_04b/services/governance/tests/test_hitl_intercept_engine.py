"""Exhaustive Test Suite for Stateful Human-in-the-Loop (HITL) Intercept Engine (`soc_g4b_governance`).

Enforces:
- Invariant [L1-G2B-002]: Stateful Human Override Registry & Dialog Mediation.
- Invariant [L1-G2B-002]: Heuristic Debt Ratio ceiling constraint (HDR <= 0.15).
- Non-blocking asynchronous queueing and human supervisor disposition recording.
- Cryptographic signature validation and HeuristicDebtCeilingBreached exception mechanics.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
import sys
import time
import unittest

GOV_ROOT = Path(__file__).resolve().parent.parent
REPO_ROOT = GOV_ROOT.parent.parent.parent.parent
for p in [str(GOV_ROOT), str(GOV_ROOT / "src"), str(REPO_ROOT)]:
    if p not in sys.path:
        sys.path.insert(0, p)

from src.domain_models import (
    GovernanceDomainInvariantViolation,
    HITLDisposition,
    HITLDispositionStatus,
    HITLInterceptRequest,
    HeuristicDebtCeilingBreached,
    HeuristicDebtRecord,
)
from src.hitl_intercept_engine import HITLInterceptEngine


class TestHITLInterceptEngine(unittest.TestCase):
    """Exhaustive test cases for HITL intercepts, supervisor dispositions, and HDR governance."""

    def setUp(self) -> None:
        self.engine = HITLInterceptEngine(service_endpoint="192.168.40.50:8448", epoch=18)

    def test_initialization_non_loopback_and_healthy_baseline(self) -> None:
        """Engine rejects loopback and boots with healthy HDR <= 0.15 baseline."""
        with self.assertRaises(GovernanceDomainInvariantViolation):
            HITLInterceptEngine(service_endpoint="127.0.0.1:8448")

        hdr = self.engine.get_current_hdr()
        self.assertLessEqual(hdr.heuristic_debt_ratio, 0.15)
        self.assertFalse(hdr.is_debt_ceiling_breached)
        self.assertTrue(self.engine.is_debt_compliant())

    def test_create_intercept_request_success(self) -> None:
        """Creates and stores a valid HITL intercept request."""
        req = HITLInterceptRequest(
            intercept_id="hitl_req_001",
            trigger_reason="Decision required on island consensus quorum size.",
            service_endpoint="192.168.40.20:8442",
            context_dossier={"subsystem": "topology", "island": "island_01"},
            recommended_options=[
                "Option 1: 3-node BFT quorum (low compute, high throughput)",
                "Option 2: 5-node Sheaf CRDT quorum (high Byzantine tolerance)",
            ],
            status=HITLDispositionStatus.PENDING_SUPERVISOR_ACTION,
        )
        registered_id = self.engine.create_intercept(req)
        self.assertEqual(registered_id, "hitl_req_001")

        retrieved = self.engine.get_intercept("hitl_req_001")
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.status, HITLDispositionStatus.PENDING_SUPERVISOR_ACTION)

        pending = self.engine.get_pending_intercepts()
        self.assertEqual(len(pending), 1)
        self.assertEqual(pending[0].intercept_id, "hitl_req_001")

    def test_create_intercept_requires_at_least_two_options(self) -> None:
        """HITL request requires >= 2 selectable options."""
        with self.assertRaises(GovernanceDomainInvariantViolation):
            bad_req = HITLInterceptRequest(
                intercept_id="hitl_bad_options",
                trigger_reason="Only one option provided.",
                service_endpoint="192.168.40.30:8444",
                context_dossier={"subsystem": "audit"},
                recommended_options=["Sole Option"],
            )
            bad_req.validate_invariants()

    def test_duplicate_intercept_registration_rejected(self) -> None:
        """Registering duplicate intercept_id raises GovernanceDomainInvariantViolation."""
        req = HITLInterceptRequest(
            intercept_id="hitl_dup_001",
            trigger_reason="Duplication check",
            service_endpoint="192.168.40.10:8440",
            context_dossier={"subsystem": "research"},
            recommended_options=["Opt A", "Opt B"],
        )
        self.engine.create_intercept(req)
        with self.assertRaises(GovernanceDomainInvariantViolation):
            self.engine.create_intercept(req)

    def test_record_supervisor_disposition_success(self) -> None:
        """Records supervisor disposition with human signature and updates intercept status."""
        req = HITLInterceptRequest(
            intercept_id="hitl_disp_001",
            trigger_reason="Ratify new negative axiom NEG-999",
            service_endpoint="192.168.40.50:8448",
            context_dossier={"rule": "ratification"},
            recommended_options=["Approve Ratification", "Reject Ratification"],
        )
        self.engine.create_intercept(req)

        disp = HITLDisposition(
            disposition_id="disp_001",
            intercept_id="hitl_disp_001",
            disposition_status=HITLDispositionStatus.APPROVED_CONTINUE,
            selected_option="Approve Ratification",
            architectural_guidance="Proceed with deterministic state machine verification.",
            human_supervisor="Michael Lipski",
        )
        disp.sign("Michael Lipski")

        success = self.engine.record_disposition(disp)
        self.assertTrue(success)

        # Intercept should now be resolved
        updated_req = self.engine.get_intercept("hitl_disp_001")
        self.assertIsNotNone(updated_req)
        self.assertEqual(updated_req.status, HITLDispositionStatus.APPROVED_CONTINUE)
        self.assertGreater(updated_req.resolved_at_unix_ms, 0)

        # No longer in pending list
        pending = self.engine.get_pending_intercepts()
        self.assertEqual(len(pending), 0)

        # Disposition retrieved
        stored_disp = self.engine.get_disposition("disp_001")
        self.assertIsNotNone(stored_disp)
        self.assertEqual(stored_disp.human_supervisor, "Michael Lipski")

    def test_record_disposition_for_nonexistent_intercept_raises(self) -> None:
        """Applying disposition to unknown intercept raises GovernanceDomainInvariantViolation."""
        disp = HITLDisposition(
            disposition_id="disp_orphan",
            intercept_id="nonexistent_intercept",
            disposition_status=HITLDispositionStatus.VETO_UPHELD,
            selected_option="Option A",
            human_supervisor="Michael Lipski",
        )
        with self.assertRaises(GovernanceDomainInvariantViolation):
            self.engine.record_disposition(disp)

    def test_hdr_calculation_and_recovery_mechanics(self) -> None:
        """Verifies HDR calculation: HDR = heuristic / (heuristic + formal + hitl)."""
        initial_hdr = self.engine.get_current_hdr()
        initial_ratio = initial_hdr.heuristic_debt_ratio

        # Record formal verified decisions -> HDR decreases
        for _ in range(20):
            self.engine.record_formal_verified_decision()

        lower_hdr = self.engine.get_current_hdr()
        self.assertLess(lower_hdr.heuristic_debt_ratio, initial_ratio)
        self.assertTrue(self.engine.is_debt_compliant())

    def test_hdr_ceiling_breach_raises_exception(self) -> None:
        """Accumulating excessive autonomous heuristic decisions breaches ceiling and raises HeuristicDebtCeilingBreached."""
        # Drive heuristic decisions until HDR breaches 0.15
        with self.assertRaises(HeuristicDebtCeilingBreached):
            for _ in range(50):
                self.engine.record_autonomous_heuristic_decision()

        self.assertFalse(self.engine.is_debt_compliant())
        current_hdr = self.engine.get_current_hdr()
        self.assertGreater(current_hdr.heuristic_debt_ratio, 0.15)
        self.assertTrue(current_hdr.is_debt_ceiling_breached)

    def test_disposition_signing_verifies_signature_presence(self) -> None:
        """HITLDisposition requires valid human_supervisor and signature upon validation."""
        disp = HITLDisposition(
            disposition_id="disp_unsigned",
            intercept_id="hitl_req_test",
            disposition_status=HITLDispositionStatus.APPROVED_CONTINUE,
            selected_option="Option 1",
            human_supervisor="",
        )
        with self.assertRaises(GovernanceDomainInvariantViolation):
            disp.validate_invariants()

        # Valid supervisor but empty signature
        disp.human_supervisor = "Michael Lipski"
        with self.assertRaises(GovernanceDomainInvariantViolation):
            disp.validate_invariants()

        # Signing generates 64-char SHA-256 signature
        disp.sign("Michael Lipski")
        self.assertEqual(len(disp.signature), 64)
        disp.validate_invariants()


if __name__ == "__main__":
    unittest.main()
