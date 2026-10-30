"""Exhaustive Test Suite for Generational Succession & Handover Gatekeeper (`soc_g4b_governance`).

Enforces:
- Formal verification of all structural, empirical, and thermodynamic criteria for Generation 5 handover.
- Zero-Loopback verification across all cluster bindings ([L1-G3B-012]).
- Heuristic Debt Ratio constraint enforcement (HDR <= 0.15) ([L1-G2B-002]).
- Proof of invariant preservation across foundational tiers:
  - L1-001..016, L1-G3B-000..019, L1-G4B-001..008.
- Cryptographic emission of GenerationalHandoverCertificate with Michael Lipski signature.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
import sys
import unittest

GOV_ROOT = Path(__file__).resolve().parent.parent
REPO_ROOT = GOV_ROOT.parent.parent.parent.parent
for p in [str(GOV_ROOT), str(GOV_ROOT / "src"), str(REPO_ROOT)]:
    if p not in sys.path:
        sys.path.insert(0, p)

from src.domain_models import (
    GenerationalHandoverCertificate,
    GovernanceDomainInvariantViolation,
    HeuristicDebtRecord,
    SuccessionGraduationStatus,
    SuccessionInvariantProof,
)
from src.succession_gatekeeper import SuccessionGatekeeper


class TestSuccessionGatekeeper(unittest.TestCase):
    """Exhaustive tests for succession readiness, invariant proofs, and handover certificates."""

    def setUp(self) -> None:
        self.valid_cluster_bindings = [
            "192.168.40.10:8440",
            "192.168.40.20:8442",
            "192.168.40.30:8444",
            "192.168.40.40:8446",
            "192.168.40.50:8448",
        ]
        self.healthy_hdr = HeuristicDebtRecord.create(
            record_id="hdr_pass_001",
            epoch=18,
            heuristic_count=2,
            formal_count=40,
            hitl_count=8,  # HDR = 2 / 50 = 0.04 <= 0.15
        )
        self.gatekeeper = SuccessionGatekeeper(
            service_endpoint="192.168.40.50:8448",
            governance_hash_chain_head="a" * 64,
        )

    def test_initialization_rejects_loopback(self) -> None:
        """Gatekeeper rejects loopback service endpoints."""
        with self.assertRaises(GovernanceDomainInvariantViolation):
            SuccessionGatekeeper(service_endpoint="127.0.0.1:8448")

    def test_seeded_proofs_cover_all_required_tiers(self) -> None:
        """Verifies default initialization seeds proofs for L1-001..016, L1-G3B-000..019, L1-G4B-001..008."""
        is_ready, deficits = self.gatekeeper.verify_succession_readiness(
            current_hdr_record=self.healthy_hdr,
            cluster_network_bindings=self.valid_cluster_bindings,
        )
        self.assertTrue(is_ready, f"Expected ready, but got deficits: {deficits}")
        self.assertEqual(len(deficits), 0)

    def test_rejection_when_hdr_exceeds_ceiling(self) -> None:
        """Rejects readiness if HDR > 0.15."""
        high_hdr = HeuristicDebtRecord.create(
            record_id="hdr_fail_001",
            epoch=18,
            heuristic_count=20,
            formal_count=30,
            hitl_count=5,  # HDR = 20 / 55 = 0.3636 > 0.15
        )
        is_ready, deficits = self.gatekeeper.verify_succession_readiness(
            current_hdr_record=high_hdr,
            cluster_network_bindings=self.valid_cluster_bindings,
        )
        self.assertFalse(is_ready)
        self.assertTrue(any("Heuristic Debt Ratio" in d for d in deficits))

    def test_rejection_when_cluster_contains_loopback(self) -> None:
        """Rejects readiness if any cluster binding uses loopback."""
        dirty_bindings = [
            "192.168.40.10:8440",
            "127.0.0.1:8442",  # Loopback
            "192.168.40.50:8448",
        ]
        is_ready, deficits = self.gatekeeper.verify_succession_readiness(
            current_hdr_record=self.healthy_hdr,
            cluster_network_bindings=dirty_bindings,
        )
        self.assertFalse(is_ready)
        self.assertTrue(any("Prohibited endpoint" in d for d in deficits))

    def test_rejection_when_cluster_bindings_empty(self) -> None:
        """Rejects readiness if cluster bindings list is empty."""
        is_ready, deficits = self.gatekeeper.verify_succession_readiness(
            current_hdr_record=self.healthy_hdr,
            cluster_network_bindings=[],
        )
        self.assertFalse(is_ready)
        self.assertTrue(any("Cluster network bindings list is empty" in d for d in deficits))

    def test_rejection_when_required_proof_is_missing(self) -> None:
        """Rejects readiness if a required invariant proof is deleted/missing."""
        del self.gatekeeper._registered_proofs["urn:axioma:core:l1_001_to_016"]
        is_ready, deficits = self.gatekeeper.verify_succession_readiness(
            current_hdr_record=self.healthy_hdr,
            cluster_network_bindings=self.valid_cluster_bindings,
        )
        self.assertFalse(is_ready)
        self.assertTrue(any("Missing required invariant proof" in d for d in deficits))

    def test_rejection_when_proof_is_unsatisfied(self) -> None:
        """Rejects readiness if an invariant proof reports is_satisfied=False."""
        failing_proof = SuccessionInvariantProof(
            proof_id="proof_failed_001",
            target_generation="Generation 5",
            invariant_urn="urn:axioma:core:l1_001_to_016",
            mathematical_formalization="Forall i: Valid(i)",
            empirical_witness_path="witness/test.py",
            is_satisfied=False,
            z3_status="UNSAT",
        )
        self.gatekeeper.register_invariant_proof(failing_proof)

        is_ready, deficits = self.gatekeeper.verify_succession_readiness(
            current_hdr_record=self.healthy_hdr,
            cluster_network_bindings=self.valid_cluster_bindings,
        )
        self.assertFalse(is_ready)
        self.assertTrue(any("not satisfied" in d for d in deficits))

    def test_issue_handover_certificate_success(self) -> None:
        """Issues authoritative GenerationalHandoverCertificate when all criteria pass."""
        cert = self.gatekeeper.issue_handover_certificate(
            supervisor_signature="Michael Lipski - Certified Human Architecture Approval",
            current_hdr_record=self.healthy_hdr,
            cluster_network_bindings=self.valid_cluster_bindings,
        )
        self.assertIsNotNone(cert)
        self.assertEqual(cert.target_generation, "Generation 5")
        self.assertEqual(cert.graduation_status, SuccessionGraduationStatus.CERTIFIED_SUCCESSION_READY)
        self.assertTrue(cert.zero_loopback_certified)
        self.assertEqual(len(cert.compute_hash()), 64)

        # Retrievable from gatekeeper
        stored = self.gatekeeper.get_certificate()
        self.assertIsNotNone(stored)
        self.assertEqual(stored.certificate_id, cert.certificate_id)

    def test_issue_handover_certificate_without_signature_raises(self) -> None:
        """Issuing certificate without supervisor signature raises GovernanceDomainInvariantViolation."""
        with self.assertRaises(GovernanceDomainInvariantViolation):
            self.gatekeeper.issue_handover_certificate(
                supervisor_signature="",
                current_hdr_record=self.healthy_hdr,
                cluster_network_bindings=self.valid_cluster_bindings,
            )

    def test_issue_handover_certificate_when_not_ready_raises(self) -> None:
        """Attempting to issue certificate with high HDR raises GovernanceDomainInvariantViolation."""
        high_hdr = HeuristicDebtRecord.create(
            record_id="hdr_unready",
            epoch=18,
            heuristic_count=30,
            formal_count=10,
            hitl_count=2,
        )
        with self.assertRaises(GovernanceDomainInvariantViolation):
            self.gatekeeper.issue_handover_certificate(
                supervisor_signature="Michael Lipski",
                current_hdr_record=high_hdr,
                cluster_network_bindings=self.valid_cluster_bindings,
            )

    def test_set_governance_hash_chain_head_validation(self) -> None:
        """Hash chain head must be exactly 64 characters."""
        self.gatekeeper.set_governance_hash_chain_head("b" * 64)
        with self.assertRaises(GovernanceDomainInvariantViolation):
            self.gatekeeper.set_governance_hash_chain_head("invalid_short_hash")


if __name__ == "__main__":
    unittest.main()
