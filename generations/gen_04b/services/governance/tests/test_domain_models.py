"""Exhaustive Unit & Invariant Test Suite for Governance Domain Models (`soc_g4b_governance`).

Enforces:
- [L1-G3B-000] Waterloo Tier 1 Situation of Concern.
- [L1-G3B-011] Universal Compositional Contract IR & Algebraic Invariants.
- [L1-G3B-012] Dedicated Non-Loopback Network Topology.
- [L1-G2B-002] Stateful HITL Intercept Engine with Heuristic Debt Ratio (HDR <= 0.15).
- [L1-016] Cluster Safety Enclaves & Emergency Circuit-Breaker.
- [L1-002] 30-State Hierarchical XState v5 Statechart & 42 Deterministic Transitions.
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
    ASTInterceptRecord,
    AxiomSeverity,
    AxiomViolation,
    BottleneckType,
    CircuitBreakerState,
    CircuitBreakerStateRecord,
    CounterProof,
    GenerationalHandoverCertificate,
    GovernanceDomainInvariantViolation,
    GovernanceEvent,
    GovernanceKernelState,
    GovernanceStatechartDefinition,
    GovernanceStatechartEngine,
    GovernanceStatechartState,
    HITLDisposition,
    HITLDispositionStatus,
    HITLInterceptRequest,
    HeuristicDebtCeilingBreached,
    HeuristicDebtRecord,
    NegativeAxiom,
    NegativeAxiomVetoViolation,
    PeerQuarantineStatus,
    QuarantineEvent,
    RFCDispositionStatus,
    SpecAdjustmentRequest,
    SpecAmendment,
    SuccessionGraduationStatus,
    SuccessionInvariantProof,
    VetoActionType,
    assert_non_loopback,
)


class TestGovernanceDomainModels(unittest.TestCase):
    """Exhaustive roundtrip, invariant, and boundary test suite for Governance service."""

    def setUp(self) -> None:
        self.sample_hash = hashlib.sha256(b"genesis_governance_witness").hexdigest()

    # 1. Non-Loopback Invariant ([L1-G3B-012])
    def test_assert_non_loopback_valid_and_invalid(self) -> None:
        valid_endpoints = [
            "192.168.40.50:8448",
            "192.168.40.10:8442",
            "10.0.1.5:9000",
            "172.16.0.2:8080",
        ]
        for ep in valid_endpoints:
            assert_non_loopback(ep, "Test Context")

        prohibited_endpoints = [
            "127.0.0.1:8000",
            "127.0.1.1:8448",
            "localhost:8448",
            "[::1]:8448",
            "0.0.0.0:8448",
            "",
        ]
        for ep in prohibited_endpoints:
            with self.assertRaises(GovernanceDomainInvariantViolation):
                assert_non_loopback(ep, "Test Prohibited Context")

    # 2. NegativeAxiom Invariant & Pattern Matching
    def test_negative_axiom_roundtrip_and_pattern_validation(self) -> None:
        axiom = NegativeAxiom(
            axiom_id="NEG-001",
            name="Prohibit Floating-Point Non-Determinism",
            forbidden_pattern="import random; math.sin",
            rationale="Formal state machine transitions require strict deterministic arithmetic.",
            severity=AxiomSeverity.FATAL_VETO,
            injected_epoch=15,
            is_active=True,
        )
        axiom.validate_invariants()
        self.assertEqual(len(axiom.compute_hash()), 64)
        self.assertTrue(axiom.matches("candidate code: import random; math.sin(x)"))
        self.assertFalse(axiom.matches("deterministic pure function"))

        # Roundtrip
        d = axiom.to_dict()
        reconstructed = NegativeAxiom.from_dict(d)
        self.assertEqual(reconstructed.axiom_id, axiom.axiom_id)
        self.assertEqual(reconstructed.forbidden_pattern, axiom.forbidden_pattern)

        # Invalid pattern regex
        with self.assertRaises(GovernanceDomainInvariantViolation):
            bad = NegativeAxiom(
                axiom_id="INVALID_ID_FORMAT",
                name="Bad ID",
                forbidden_pattern="pattern",
                rationale="rationale",
            )
            bad.validate_invariants()

    # 3. AxiomViolation Record
    def test_axiom_violation_roundtrip_and_validation(self) -> None:
        violation = AxiomViolation(
            violation_id="viol_test_001",
            axiom_id="NEG-002",
            violating_symbol_or_endpoint="127.0.0.1:8000",
            severity=AxiomSeverity.FATAL_VETO,
            veto_action=VetoActionType.QUARANTINE_NODE,
            detected_pattern="127.0.0.1",
            culprit_service="services/builder",
            description="Builder attempted loopback socket binding.",
        )
        violation.validate_invariants()
        self.assertEqual(len(violation.compute_hash()), 64)

        d = violation.to_dict()
        reconstructed = AxiomViolation.from_dict(d)
        self.assertEqual(reconstructed.violation_id, violation.violation_id)
        self.assertEqual(reconstructed.veto_action, VetoActionType.QUARANTINE_NODE)

    # 4. ASTInterceptRecord
    def test_ast_intercept_record_roundtrip(self) -> None:
        intercept = ASTInterceptRecord(
            intercept_id="ast_int_001",
            source_service="services/builder",
            symbol_urn="urn:axioma:builder:leaf:node_42",
            file_path="generations/gen_04b/services/builder/src/engine.py",
            ast_node_type="Call",
            banned_token_or_call="os.system",
            matched_axiom_id="NEG-004",
            action_taken=VetoActionType.HALT_COMPILATION,
            line_number=45,
            column_offset=12,
        )
        intercept.validate_invariants()
        self.assertEqual(len(intercept.compute_hash()), 64)

        d = intercept.to_dict()
        reconstructed = ASTInterceptRecord.from_dict(d)
        self.assertEqual(reconstructed.intercept_id, intercept.intercept_id)
        self.assertEqual(reconstructed.line_number, 45)

    # 5. HITL Intercept & Disposition
    def test_hitl_intercept_and_disposition(self) -> None:
        req = HITLInterceptRequest(
            intercept_id="hitl_req_001",
            trigger_reason="Heuristic Debt Ratio approaching ceiling threshold (HDR=0.142)",
            service_endpoint="192.168.40.50:8448",
            context_dossier={"current_hdr": 0.142, "candidate_modules": 4},
            recommended_options=["Option A: Increase formal SMT verification", "Option B: Reject candidate"],
        )
        req.validate_invariants()
        self.assertEqual(len(req.compute_hash()), 64)

        # Disposition
        disp = HITLDisposition(
            disposition_id="disp_001",
            intercept_id="hitl_req_001",
            human_supervisor="Michael Lipski",
            disposition_status=HITLDispositionStatus.APPROVED_CONTINUE,
            selected_option="Option A: Increase formal SMT verification",
            architectural_guidance="Mandate z3 SAT certificate on all 4 candidate modules.",
            injected_negative_axioms=["NEG-009"],
        )
        disp.sign()
        disp.validate_invariants()
        self.assertEqual(len(disp.signature), 64)

        d = disp.to_dict()
        reconstructed = HITLDisposition.from_dict(d)
        self.assertEqual(reconstructed.disposition_id, disp.disposition_id)
        self.assertEqual(reconstructed.signature, disp.signature)

    # 6. Heuristic Debt Ratio Accounting ([L1-G2B-002])
    def test_heuristic_debt_ratio_and_ceiling_enforcement(self) -> None:
        # Healthy ratio: 10 / 100 = 0.10 <= 0.15
        rec_healthy = HeuristicDebtRecord.create(
            record_id="hdr_rec_healthy",
            epoch=15,
            heuristic_count=10,
            formal_count=70,
            hitl_count=20,
        )
        self.assertAlmostEqual(rec_healthy.heuristic_debt_ratio, 0.10)
        self.assertFalse(rec_healthy.is_debt_ceiling_breached)

        # Breached ratio: 20 / 100 = 0.20 > 0.15
        rec_breached = HeuristicDebtRecord.create(
            record_id="hdr_rec_breached",
            epoch=15,
            heuristic_count=20,
            formal_count=60,
            hitl_count=20,
        )
        self.assertAlmostEqual(rec_breached.heuristic_debt_ratio, 0.20)
        self.assertTrue(rec_breached.is_debt_ceiling_breached)

        # Invariant check: inconsistent totals raise error
        with self.assertRaises(GovernanceDomainInvariantViolation):
            bad = HeuristicDebtRecord(
                record_id="hdr_bad",
                epoch=15,
                total_decisions_evaluated=100,
                autonomous_heuristic_decisions=10,
                formal_verified_decisions=10,
                hitl_supervised_decisions=10,  # Sum is 30 != 100
                heuristic_debt_ratio=0.10,
            )
            bad.validate_invariants()

    # 7. Asymmetric RFC Protocol (SpecAdjustmentRequest, SpecAmendment, CounterProof)
    def test_rfc_protocol_adjudication_models(self) -> None:
        rfc = SpecAdjustmentRequest(
            request_id="rfc_test_001",
            builder_node_id="node_builder_enclave",
            target_symbol_urn="urn:axioma:builder:leaf:network",
            bottleneck_type=BottleneckType.LATENCY_OVERRUN,
            empirical_evidence="Physical TCP handshake latency 125ms exceeds budget 100ms",
            proposed_delta="Permit persistent HTTP/2 connection pooling",
            preserved_invariants=["[L1-G3B-012]", "[L1-G4B-001]"],
        )
        rfc.validate_invariants()
        self.assertEqual(len(rfc.compute_hash()), 64)

        # CounterProof for rejection
        cp = CounterProof(
            counter_proof_id="cp_test_001",
            request_id="rfc_test_001",
            violated_axioms=["NEG-002"],
            z3_unsat_core="unsat_core(persistent_connection, loopback_leak)",
            counter_example_model={"loopback_detected": True},
        )
        cp.validate_invariants()

        # Rejection amendment requires CounterProof
        amendment_reject = SpecAmendment(
            amendment_id="amd_reject_001",
            request_id="rfc_test_001",
            is_approved=False,
            adjudicator_signature=self.sample_hash,
            rejection_counter_proof=cp,
        )
        amendment_reject.validate_invariants()
        self.assertEqual(len(amendment_reject.compute_hash()), 64)

        # Approved amendment
        amendment_approve = SpecAmendment(
            amendment_id="amd_approve_001",
            request_id="rfc_test_001",
            is_approved=True,
            adjudicator_signature=self.sample_hash,
            amended_contract_ir_delta="allow_h2_pooling=True",
        )
        amendment_approve.validate_invariants()

        # Rejection without CounterProof must fail
        with self.assertRaises(GovernanceDomainInvariantViolation):
            bad_amendment = SpecAmendment(
                amendment_id="amd_bad",
                request_id="rfc_test_001",
                is_approved=False,
                adjudicator_signature=self.sample_hash,
                rejection_counter_proof=None,
            )
            bad_amendment.validate_invariants()

    # 8. Circuit Breaker & Safety Enclaves ([L1-016])
    def test_circuit_breaker_record_lifecycle(self) -> None:
        cb = CircuitBreakerStateRecord(
            record_id="cb_test_001",
            failure_threshold=2,
            cooldown_seconds=10.0,
        )
        self.assertEqual(cb.current_state, CircuitBreakerState.CLOSED_NORMAL)

        # 1st failure: doesn't trip yet
        cb.trip("192.168.40.20:8443")
        self.assertEqual(cb.failure_count, 1)
        self.assertEqual(cb.current_state, CircuitBreakerState.CLOSED_NORMAL)

        # 2nd failure: trips open
        cb.trip("192.168.40.30:8444")
        self.assertEqual(cb.failure_count, 2)
        self.assertEqual(cb.current_state, CircuitBreakerState.TRIPPED_OPEN)
        self.assertIsNotNone(cb.last_tripped_unix_ms)

        # Reset clean
        cb.reset_clean()
        self.assertEqual(cb.current_state, CircuitBreakerState.CLOSED_NORMAL)
        self.assertEqual(cb.failure_count, 0)
        self.assertEqual(len(cb.quarantined_peer_endpoints), 0)

    # 9. Peer Quarantine Event
    def test_quarantine_event_lifecycle(self) -> None:
        qe = QuarantineEvent(
            event_id="qevent_001",
            node_id="node_builder_rogue",
            service_endpoint="192.168.40.20:8443",
            quarantine_status=PeerQuarantineStatus.QUARANTINED_ISOLATED,
            triggering_violation_id="viol_test_001",
            reason="Violation of NEG-002: Detected loopback socket probe",
        )
        qe.validate_invariants()
        self.assertEqual(len(qe.compute_hash()), 64)

        d = qe.to_dict()
        reconstructed = QuarantineEvent.from_dict(d)
        self.assertEqual(reconstructed.node_id, qe.node_id)
        self.assertEqual(reconstructed.quarantine_status, PeerQuarantineStatus.QUARANTINED_ISOLATED)

    # 10. Succession Certificate & Invariant Proofs (Gen 5 Graduation)
    def test_succession_certificate_validation(self) -> None:
        proof = SuccessionInvariantProof(
            proof_id="proof_001",
            target_generation="Generation 5",
            invariant_urn="urn:axioma:g4b:invariant:zero_loopback",
            mathematical_formalization="Forall e in Endpoints: host(e) != 127.0.0.1",
            empirical_witness_path="generations/gen_04b/tests/test_mesh.py",
            is_satisfied=True,
            z3_status="SAT",
        )
        proof.validate_invariants()

        cert = GenerationalHandoverCertificate(
            certificate_id="cert_gen5_handover_001",
            source_generation="Generation 4b",
            target_generation="Generation 5",
            graduation_status=SuccessionGraduationStatus.CERTIFIED_SUCCESSION_READY,
            invariant_proofs=[proof],
            governance_hash_chain_head=self.sample_hash,
            human_architect_approval_sig="sig_michael_lipski_approved",
            hdr_at_graduation=0.045,  # <= 0.15
            zero_loopback_certified=True,
        )
        cert.validate_invariants()
        self.assertEqual(len(cert.compute_hash()), 64)

        # High HDR at graduation must fail with HeuristicDebtCeilingBreached
        with self.assertRaises(HeuristicDebtCeilingBreached):
            bad_cert = GenerationalHandoverCertificate(
                certificate_id="cert_bad",
                source_generation="Generation 4b",
                target_generation="Generation 5",
                invariant_proofs=[proof],
                governance_hash_chain_head=self.sample_hash,
                human_architect_approval_sig="sig_approved",
                hdr_at_graduation=0.18,  # > 0.15
            )
            bad_cert.validate_invariants()

    # 11. GovernanceKernelState & GovernanceEvent
    def test_kernel_state_and_cryptographic_event_ledger(self) -> None:
        state = GovernanceKernelState(
            kernel_id="soc_g4b_governance",
            service_endpoint="192.168.40.50:8448",
            circuit_breaker=CircuitBreakerState.CLOSED_NORMAL,
            active_negative_axioms_count=8,
            total_violations_trapped=0,
            heuristic_debt_ratio=0.05,
            governance_chain_head=self.sample_hash,
        )
        state.validate_invariants()
        self.assertEqual(len(state.compute_hash()), 64)

        event = GovernanceEvent(
            event_id="ev_gov_001",
            event_type="AXIOM_COMMITTED",
            source_node_or_service="services/governance",
            payload={"axiom_id": "NEG-001", "action": "ENFORCE"},
            previous_event_hash=self.sample_hash,
        )
        event.validate_invariants()
        h = event.seal()
        self.assertEqual(len(h), 64)
        self.assertEqual(event.event_hash, h)

    # 12. 30-State Hierarchical XState v5 Statechart & 42 Transitions
    def test_statechart_specification_and_all_30_states(self) -> None:
        states = GovernanceStatechartDefinition.get_states()
        self.assertEqual(len(states), 30)

        compound = GovernanceStatechartDefinition.get_compound_strata()
        total_compound_states = sum(len(s) for s in compound.values())
        self.assertEqual(total_compound_states, 20)

        parallel = GovernanceStatechartDefinition.get_parallel_regions()
        total_parallel_states = sum(len(s) for s in parallel.values())
        self.assertEqual(total_parallel_states, 10)

        transitions = GovernanceStatechartDefinition.get_deterministic_transitions()
        self.assertEqual(len(transitions), 42)

    # 13. Statechart Engine Execution & Covering Paths
    def test_statechart_engine_covering_paths_and_deep_history(self) -> None:
        engine = GovernanceStatechartEngine(initial_state="gov_root_idle")

        # 1. Bootstrap to Ready
        engine.send("EV_BOOTSTRAP_INIT")
        self.assertEqual(engine.current_state, "gov_bootstrapping")
        engine.send("EV_AXIOMS_LOADED")
        self.assertEqual(engine.current_state, "gov_ready")

        # 2. Recalibration Cycle
        engine.send("EV_RECALIBRATE_START")
        self.assertEqual(engine.current_state, "gov_recalibrating")
        engine.send("EV_RECALIBRATE_COMPLETE")
        self.assertEqual(engine.current_state, "gov_ready")

        # 3. Enter Sovereign Operational
        engine.send("EV_ENTER_OPERATIONAL")
        self.assertEqual(engine.current_state, "op_surveilling")

        # 4. Intercept & HITL Escalation Path
        engine.send("EV_INTERCEPT_DETECTED")
        self.assertEqual(engine.current_state, "op_evaluating_intercept")
        engine.send("EV_ESCALATE_HITL")
        self.assertEqual(engine.current_state, "op_hitl_escalating")
        engine.send("EV_HITL_SUBMITTED")
        self.assertEqual(engine.current_state, "op_hitl_awaiting_disposition")
        engine.send("EV_SUPERVISOR_APPROVED")
        self.assertEqual(engine.current_state, "op_adjudication_settled")
        engine.send("EV_ADJUDICATION_DISPATCHED")
        self.assertEqual(engine.current_state, "op_surveilling")

        # 5. RFC Deliberation Path
        engine.send("EV_RFC_SUBMITTED")
        self.assertEqual(engine.current_state, "op_rfc_deliberation")
        engine.send("EV_RFC_APPROVE")
        self.assertEqual(engine.current_state, "op_adjudication_settled")
        engine.send("EV_ADJUDICATION_DISPATCHED")
        self.assertEqual(engine.current_state, "op_surveilling")

        # 6. Emergency Enclave & Deep History H* Restoration Path
        engine.send("EV_TRIP_CIRCUIT_BREAKER")
        self.assertEqual(engine.current_state, "enclave_tripped")
        engine.send("EV_ISOLATE_NODE")
        self.assertEqual(engine.current_state, "enclave_quarantine_isolation")
        engine.send("EV_BEGIN_INVESTIGATION")
        self.assertEqual(engine.current_state, "enclave_investigation")
        engine.send("EV_START_COOLDOWN_PROBE")
        self.assertEqual(engine.current_state, "enclave_cooldown_probing")
        engine.send("EV_PROBE_SUCCEEDED")
        self.assertEqual(engine.current_state, "enclave_restored")
        engine.send("EV_RESTORE_DEEP_HISTORY")  # Restores via H*
        self.assertEqual(engine.current_state, "op_surveilling")

        # 7. Generational Handover Path to Gen 5 Graduation
        engine.send("EV_INITIATE_HANDOVER")
        self.assertEqual(engine.current_state, "handover_initiating")
        engine.send("EV_VERIFY_INVARIANTS")
        self.assertEqual(engine.current_state, "handover_proving_invariants")
        engine.send("EV_INVARIANTS_SATISFIED")
        self.assertEqual(engine.current_state, "handover_hdr_verifying")
        engine.send("EV_HDR_VERIFIED_PASS")
        self.assertEqual(engine.current_state, "handover_signing_certificate")
        engine.send("EV_CERTIFICATE_SIGNED")
        self.assertEqual(engine.current_state, "handover_graduated")
        engine.send("EV_RETURN_TO_STANDBY")
        self.assertEqual(engine.current_state, "gov_root_idle")

        # 8. Parallel Region Transitions
        engine.send("EV_SURV_SCAN_AST")
        self.assertEqual(engine.parallel_surveillance_state, "surv_inspecting_ast")
        engine.send("EV_SURV_TRIGGER_VETO")
        self.assertEqual(engine.parallel_surveillance_state, "surv_veto_triggered")
        engine.send("EV_SURV_QUARANTINE_PEER")
        self.assertEqual(engine.parallel_surveillance_state, "surv_quarantined")
        engine.send("EV_SURV_DISCHARGE_CLEAN")
        self.assertEqual(engine.parallel_surveillance_state, "surv_idle")

        engine.send("EV_PEER_POLL_RFC")
        self.assertEqual(engine.parallel_mediation_state, "peer_adjudicating_rfc")
        engine.send("EV_PEER_GENERATE_COUNTER_PROOF")
        self.assertEqual(engine.parallel_mediation_state, "peer_counter_proving")
        engine.send("EV_PEER_RESET_LISTENING")
        self.assertEqual(engine.parallel_mediation_state, "peer_listening")

        # Total transitions logged
        self.assertGreaterEqual(len(engine.transition_log), 25)


if __name__ == "__main__":
    unittest.main()
