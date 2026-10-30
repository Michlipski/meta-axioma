"""Exhaustive Test Suite for RFC Protocol Adjudication Engine (`soc_g4b_governance`).

Enforces:
- Invariant [L1-G4B-001]: Service-Oriented Sovereign Mesh Protocol Standardization.
- Asymmetric negotiation between Builder enclaves and Sovereign Governance.
- Approval pathway: Invariant-preserving RFC emits signed SpecAmendment.
- Rejection pathway: Negative-axiom-violating RFC strictly requires and emits formal CounterProof.
- Invariant [HERM-004]: Rejecting without CounterProof violates domain invariants.
"""

from __future__ import annotations

from pathlib import Path
import sys
import unittest

GOV_ROOT = Path(__file__).resolve().parent.parent
REPO_ROOT = GOV_ROOT.parent.parent.parent.parent
for p in [str(GOV_ROOT), str(GOV_ROOT / "src"), str(REPO_ROOT)]:
    if p not in sys.path:
        sys.path.insert(0, p)

from src.domain_models import (
    BottleneckType,
    CounterProof,
    GovernanceDomainInvariantViolation,
    NegativeAxiom,
    RFCDispositionStatus,
    SpecAdjustmentRequest,
    SpecAmendment,
)
from src.negative_axiom_enforcer import NegativeAxiomEnforcer
from src.rfc_protocol_adjudicator import RFCProtocolAdjudicator


class TestRFCProtocolAdjudicator(unittest.TestCase):
    """Exhaustive tests for RFC adjudication, formal proofs, and invariant gates."""

    def setUp(self) -> None:
        self.adjudicator = RFCProtocolAdjudicator(
            adjudicator_id="node_governance_adjudicator",
            service_endpoint="192.168.40.50:8448",
        )
        self.enforcer = NegativeAxiomEnforcer(service_endpoint="192.168.40.50:8448")
        self.active_axioms = self.enforcer.get_active_axioms()

    def test_adjudicator_initialization_rejects_loopback(self) -> None:
        """Adjudicator rejects loopback endpoints."""
        with self.assertRaises(GovernanceDomainInvariantViolation):
            RFCProtocolAdjudicator(service_endpoint="127.0.0.1:8448")

    def test_rfc_approval_pathway_emits_signed_amendment(self) -> None:
        """Clean invariant-preserving RFC petition receives approved SpecAmendment with signature."""
        petition = SpecAdjustmentRequest(
            request_id="rfc_req_valid_001",
            builder_node_id="node_builder_island_01",
            target_symbol_urn="urn:axioma:contract:topology_mesh",
            bottleneck_type=BottleneckType.LATENCY_OVERRUN,
            empirical_evidence="Observed P99 latency of 42ms under 100 concurrent peer gossip nodes.",
            proposed_delta="Increase gossip fanout degree from 3 to 5 to reduce hop count.",
            preserved_invariants=[
                "urn:axioma:invariant:anti_loopback",
                "urn:axioma:invariant:functorial_reversibility",
            ],
        )

        amendment, counter_proof = self.adjudicator.adjudicate_rfc(petition, active_axioms=self.active_axioms)

        self.assertIsNotNone(amendment)
        self.assertIsNone(counter_proof)
        self.assertTrue(amendment.is_approved)
        self.assertGreater(len(amendment.adjudicator_signature), 0)
        self.assertEqual(petition.disposition_status, RFCDispositionStatus.AMENDED)

    def test_rfc_rejection_pathway_violating_negative_axiom_emits_counter_proof(self) -> None:
        """RFC proposing centralized coordinator violates NEG-001 and emits formal CounterProof."""
        petition = SpecAdjustmentRequest(
            request_id="rfc_req_violating_001",
            builder_node_id="node_builder_island_02",
            target_symbol_urn="urn:axioma:consensus:coordinator",
            bottleneck_type=BottleneckType.COMPLEXITY_LIMIT,
            empirical_evidence="Decentralized gossip requires complex vector clock tracking.",
            proposed_delta="Introduce centralized coordinator to elect a single master leader.",
            preserved_invariants=["urn:axioma:invariant:anti_loopback"],
        )

        amendment, counter_proof = self.adjudicator.adjudicate_rfc(petition, active_axioms=self.active_axioms)

        self.assertIsNotNone(amendment)
        self.assertIsNotNone(counter_proof)
        self.assertFalse(amendment.is_approved)
        self.assertIsNotNone(amendment.rejection_counter_proof)
        self.assertEqual(petition.disposition_status, RFCDispositionStatus.COUNTER_PROVEN)

        # Counter proof invariants
        self.assertEqual(counter_proof.request_id, "rfc_req_violating_001")
        self.assertTrue(any("NEG-001" in ax for ax in counter_proof.violated_axioms))
        self.assertIn("unsat_core", counter_proof.z3_unsat_core)
        self.assertIn("refutation_reason", counter_proof.counter_example_model)

    def test_rfc_rejection_pathway_violating_loopback(self) -> None:
        """RFC proposing loopback binding triggers NEG-G2B-001 and emits CounterProof."""
        petition = SpecAdjustmentRequest(
            request_id="rfc_req_loopback_001",
            builder_node_id="node_builder_island_03",
            target_symbol_urn="urn:axioma:endpoint:debug",
            bottleneck_type=BottleneckType.LATENCY_OVERRUN,
            empirical_evidence="Testing on local developer machine.",
            proposed_delta="Bind debug channel to 127.0.0.1:8000 for local diagnostics.",
            preserved_invariants=["urn:axioma:invariant:functorial_reversibility"],
        )

        amendment, counter_proof = self.adjudicator.adjudicate_rfc(petition, active_axioms=self.active_axioms)

        self.assertFalse(amendment.is_approved)
        self.assertIsNotNone(counter_proof)
        self.assertTrue(any("NEG-G2B-001" in ax for ax in counter_proof.violated_axioms))

    def test_rfc_rejection_pathway_dynamic_exec(self) -> None:
        """RFC proposing dynamic execution (eval/exec) triggers violation and CounterProof."""
        petition = SpecAdjustmentRequest(
            request_id="rfc_req_eval_001",
            builder_node_id="node_builder_island_04",
            target_symbol_urn="urn:axioma:engine:dynamic_eval",
            bottleneck_type=BottleneckType.TOKEN_EXHAUSTION,
            empirical_evidence="AST parsing token overhead is high.",
            proposed_delta="Use eval('f(x)') to evaluate transition expressions directly.",
            preserved_invariants=["urn:axioma:invariant:functorial_reversibility"],
        )

        amendment, counter_proof = self.adjudicator.adjudicate_rfc(petition, active_axioms=self.active_axioms)

        self.assertFalse(amendment.is_approved)
        self.assertIsNotNone(counter_proof)
        self.assertTrue(any("eval/exec" in ax for ax in counter_proof.violated_axioms))

    def test_rejection_without_counter_proof_violates_invariant(self) -> None:
        """Directly instantiating a rejected SpecAmendment without CounterProof raises invariant violation."""
        with self.assertRaises(GovernanceDomainInvariantViolation):
            invalid_amendment = SpecAmendment(
                amendment_id="amend_illegal_001",
                request_id="req_001",
                is_approved=False,
                adjudicator_signature="sig_12345",
                rejection_counter_proof=None,  # Forbidden: rejected amendment MUST have CounterProof
            )
            invalid_amendment.validate_invariants()

    def test_retrieval_of_adjudicated_amendments_and_counter_proofs(self) -> None:
        """Adjudicated amendments and counter proofs can be retrieved by request_id and counter_proof_id."""
        petition = SpecAdjustmentRequest(
            request_id="rfc_req_test_retrieval",
            builder_node_id="node_builder_01",
            target_symbol_urn="urn:axioma:mesh",
            bottleneck_type=BottleneckType.PHYSICAL_IRREVERSIBILITY,
            empirical_evidence="Valid empirical study",
            proposed_delta="Pure functorial delta",
            preserved_invariants=["urn:axioma:inv"],
        )
        amendment, _ = self.adjudicator.adjudicate_rfc(petition)
        self.assertIsNotNone(amendment)

        retrieved = self.adjudicator.get_amendment(amendment.amendment_id)
        self.assertEqual(retrieved.amendment_id, amendment.amendment_id)


if __name__ == "__main__":
    unittest.main()
