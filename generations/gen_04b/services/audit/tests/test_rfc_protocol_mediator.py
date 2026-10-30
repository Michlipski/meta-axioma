"""Unit & Adversarial Invariant Test Suite for Inter-Service RFC Protocol Mediator (`[L1-G4B-001]`).

Validates:
1. Issues signed SpecAmendment on valid petition.
2. Issues formal CounterProof on invalid delta containing loopback.
3. Issues formal CounterProof on candidate code violating AST hermetic boundary.
4. Rejection of empty invariant claims / malformed petitions.
5. Audit trail and RFC ledger logging.
"""

from __future__ import annotations

from pathlib import Path
import sys
import unittest

AUDIT_ROOT = Path(__file__).resolve().parent.parent
REPO_ROOT = AUDIT_ROOT.parent.parent.parent.parent
for p in [str(AUDIT_ROOT), str(AUDIT_ROOT / "src"), str(REPO_ROOT)]:
    if p not in sys.path:
        sys.path.insert(0, p)

from generations.gen_04b.protocols.rfc_protocol import (
    BottleneckType,
    CounterProof,
    RFCProtocolViolation,
    SpecAdjustmentRequest,
    SpecAmendment,
)
from src.rfc_protocol_mediator import AuditRFCMediator


class TestRFCProtocolMediator(unittest.TestCase):
    """Exhaustive tests for inter-service RFC protocol mediation and counter-proof generation."""

    def setUp(self) -> None:
        self.mediator = AuditRFCMediator()

    # 1. Issues Signed SpecAmendment on Valid Petition
    def test_issues_signed_spec_amendment_on_valid_petition(self) -> None:
        request = SpecAdjustmentRequest(
            request_id="rfc_req_001",
            builder_node_id="node_builder_kernel",
            target_symbol_urn="urn:meta_axioma:domain:kernel",
            bottleneck_type=BottleneckType.COMPLEXITY_LIMIT,
            empirical_evidence="State space exceeded limit",
            proposed_delta="Partition compound state into 2 parallel orthogonal regions.",
            preserved_invariants=["I_deadlock_freedom", "I_functorial_undo"],
        )
        candidate_code = "def state_region(): pass"

        amendment = self.mediator.adjudicate_rfc_request(request, candidate_code=candidate_code)
        self.assertTrue(amendment.is_approved)
        self.assertIsNone(amendment.rejection_counter_proof)
        self.assertGreater(len(amendment.adjudicator_signature), 0)
        self.assertIn("CERTIFIED_BY_SOVEREIGN_AUDIT", amendment.amended_contract_ir_delta)

    # 2. Issues Formal CounterProof on Invalid Delta (Loopback)
    def test_issues_formal_counter_proof_on_invalid_delta(self) -> None:
        request = SpecAdjustmentRequest(
            request_id="rfc_req_loopback",
            builder_node_id="node_builder_kernel",
            target_symbol_urn="urn:meta_axioma:domain:router",
            bottleneck_type=BottleneckType.LATENCY_OVERRUN,
            empirical_evidence="High RPC latency observed",
            proposed_delta="Route traffic through local proxy 127.0.0.1:8080",
            preserved_invariants=["I_throughput"],
        )

        amendment = self.mediator.adjudicate_rfc_request(request)
        self.assertFalse(amendment.is_approved)
        self.assertIsNotNone(amendment.rejection_counter_proof)
        cproof = amendment.rejection_counter_proof
        self.assertIn("[L1-G3B-012] Dedicated Non-Loopback Network Topology", cproof.violated_axioms)
        self.assertIn("127.0.0.1", cproof.counter_example_model["culprit_token"])

    # 3. Issues Formal CounterProof on AST Hermetic Violation
    def test_issues_formal_counter_proof_on_ast_violation(self) -> None:
        request = SpecAdjustmentRequest(
            request_id="rfc_req_ast_hack",
            builder_node_id="node_builder_kernel",
            target_symbol_urn="urn:meta_axioma:domain:importer",
            bottleneck_type=BottleneckType.TOKEN_EXHAUSTION,
            empirical_evidence="Missing symbol import error",
            proposed_delta="Dynamically adjust sys.path to find external libraries.",
            preserved_invariants=["I_memory_cap"],
        )
        candidate_code = """
import sys
sys.path.append('/untrusted/lib')
"""

        amendment = self.mediator.adjudicate_rfc_request(request, candidate_code=candidate_code)
        self.assertFalse(amendment.is_approved)
        self.assertIsNotNone(amendment.rejection_counter_proof)
        cproof = amendment.rejection_counter_proof
        self.assertIn("HERM-002", cproof.violated_axioms)

    # 4. Rejection of Empty Invariant Claims / Malformed Petitions
    def test_rejection_of_empty_invariant_claims(self) -> None:
        with self.assertRaises(RFCProtocolViolation):
            SpecAdjustmentRequest(
                request_id="rfc_bad",
                builder_node_id="node_builder",
                target_symbol_urn="urn:meta_axioma:domain:x",
                bottleneck_type=BottleneckType.COMPLEXITY_LIMIT,
                empirical_evidence="Evidence string",
                proposed_delta="delta",
                preserved_invariants=[],  # Empty invariant claims must raise RFCProtocolViolation
            ).validate_invariants()

        with self.assertRaises(RFCProtocolViolation):
            SpecAdjustmentRequest(
                request_id="",
                builder_node_id="node_builder",
                target_symbol_urn="urn:meta_axioma:domain:x",
                bottleneck_type=BottleneckType.COMPLEXITY_LIMIT,
                empirical_evidence="Evidence string",
                proposed_delta="delta",
                preserved_invariants=["inv1"],
            ).validate_invariants()

    # 5. Audit Trail and RFC Ledger Logging
    def test_audit_trail_and_ledger_logging(self) -> None:
        req1 = SpecAdjustmentRequest(
            request_id="rfc_log_1",
            builder_node_id="node_builder",
            target_symbol_urn="urn:meta_axioma:domain:one",
            bottleneck_type=BottleneckType.COMPLEXITY_LIMIT,
            empirical_evidence="Evidence 1",
            proposed_delta="Safe delta 1",
            preserved_invariants=["I1"],
        )
        self.mediator.adjudicate_rfc_request(req1)

        req2 = SpecAdjustmentRequest(
            request_id="rfc_log_2",
            builder_node_id="node_builder",
            target_symbol_urn="urn:meta_axioma:domain:two",
            bottleneck_type=BottleneckType.LATENCY_OVERRUN,
            empirical_evidence="Evidence 2",
            proposed_delta="Bad delta with localhost",
            preserved_invariants=["I2"],
        )
        self.mediator.adjudicate_rfc_request(req2)

        ledger = self.mediator.export_rfc_ledger()
        self.assertGreaterEqual(len(ledger), 2)
        req_ids = [entry["request_id"] for entry in ledger]
        self.assertIn("rfc_log_1", req_ids)
        self.assertIn("rfc_log_2", req_ids)


if __name__ == "__main__":
    unittest.main()
