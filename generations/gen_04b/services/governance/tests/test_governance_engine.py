"""Unit and integration test suite for Sovereign Governance & Safety Service engines.

Enforces:
- Invariant [L1-G3B-012]: Dedicated Non-Loopback Network Topology.
- Invariant [L1-G3B-016]: Zero-Bypass Negative Axiom Interception.
- Invariant [L1-G2B-002]: Heuristic Debt Ratio (HDR <= 0.15) & Stateful HITL Mediation.
- Invariant [L1-016]: Tri-State Circuit-Breaker & Enclave Quarantine.
- Invariant [L1-002]: Deterministic Statechart Traversal & Functorial Reversal.
"""

from __future__ import annotations

import unittest

from generations.gen_04b.services.governance.src import (
    AxiomSeverity,
    BottleneckType,
    CircuitBreakerEnclave,
    CircuitBreakerState,
    CounterProof,
    FunctorialUndoEngine,
    GenerationalHandoverCertificate,
    GovernanceDomainInvariantViolation,
    GovernanceEvent,
    GovernanceKernel,
    GovernanceKernelState,
    GovernanceServiceTopology,
    GovernanceStatechartState,
    HITLDisposition,
    HITLDispositionStatus,
    HITLInterceptEngine,
    HITLInterceptRequest,
    HeuristicDebtCeilingBreached,
    HeuristicDebtRecord,
    NegativeAxiom,
    NegativeAxiomEnforcer,
    PeerQuarantineStatus,
    QuarantineEvent,
    RFCDispositionStatus,
    RFCProtocolAdjudicator,
    SpecAdjustmentRequest,
    SpecAmendment,
    StatechartEngine,
    SuccessionGatekeeper,
    SuccessionGraduationStatus,
    SuccessionInvariantProof,
    VetoActionType,
    assert_non_loopback,
)


class TestNegativeAxiomEnforcer(unittest.TestCase):
    """Tests zero-bypass AST and semantic scanning for negative axioms."""

    def setUp(self) -> None:
        self.enforcer = NegativeAxiomEnforcer(service_endpoint="192.168.40.50:8448")

    def test_seed_axioms_active(self) -> None:
        active = self.enforcer.get_active_axioms()
        self.assertGreaterEqual(len(active), 10)
        neg_001 = self.enforcer.get_negative_axiom("NEG-001")
        self.assertIsNotNone(neg_001)
        self.assertEqual(neg_001.name, "Ban Centralized Coordinator")

    def test_clean_source_code(self) -> None:
        code = "def add(a: int, b: int) -> int:\n    return a + b\n"
        violations = self.enforcer.scan_source_code(code, file_path="math.py")
        self.assertEqual(len(violations), 0)

    def test_toxic_ast_interception(self) -> None:
        toxic_code = (
            "import os\n"
            "def run():\n"
            "    eval('1+1')\n"
            "    os.system('ls')\n"
            "    flag = 'bypass_sandbox'\n"
        )
        violations = self.enforcer.scan_source_code(toxic_code, file_path="bad.py")
        self.assertGreaterEqual(len(violations), 3)
        detected_patterns = [v.detected_pattern for v in violations]
        self.assertTrue(any("eval" in p for p in detected_patterns))
        self.assertTrue(any("os.system" in p for p in detected_patterns))

    def test_hardcoded_credential_scanning(self) -> None:
        code_with_secret = 'api_key = "sk-abcdef1234567890abcdef1234567890"\n'
        violations = self.enforcer.scan_source_code(code_with_secret, file_path="auth.py")
        self.assertGreaterEqual(len(violations), 1)
        self.assertTrue(any(v.severity == AxiomSeverity.SECURITY_BREACH for v in violations))

    def test_topology_scanning(self) -> None:
        bad_topology = {
            "nodes": {
                "bad_node": {"endpoint": "127.0.0.1:8000", "role": "centralized_coordinator_master"}
            }
        }
        violations = self.enforcer.scan_topology(bad_topology)
        self.assertGreaterEqual(len(violations), 2)


class TestHITLInterceptEngine(unittest.TestCase):
    """Tests stateful human override registry and HDR compliance."""

    def setUp(self) -> None:
        self.engine = HITLInterceptEngine(service_endpoint="192.168.40.50:8448")

    def test_initial_hdr_compliance(self) -> None:
        hdr = self.engine.get_current_hdr()
        self.assertLessEqual(hdr.heuristic_debt_ratio, 0.15)
        self.assertTrue(self.engine.is_debt_compliant())

    def test_create_and_resolve_intercept(self) -> None:
        req = HITLInterceptRequest(
            intercept_id="icpt_001",
            trigger_reason="Test intercept",
            service_endpoint="192.168.40.50:8448",
            context_dossier={"subsystem": "test"},
            recommended_options=["Opt 1", "Opt 2"],
        )
        self.engine.create_intercept(req)
        self.assertEqual(len(self.engine.get_pending_intercepts()), 1)

        disp = HITLDisposition(
            disposition_id="disp_001",
            intercept_id="icpt_001",
            human_supervisor="Michael Lipski",
            disposition_status=HITLDispositionStatus.APPROVED_CONTINUE,
            selected_option="Opt 1",
            architectural_guidance="Proceed",
        )
        disp.sign()
        self.engine.record_disposition(disp)

        self.assertEqual(len(self.engine.get_pending_intercepts()), 0)
        stored_req = self.engine.get_intercept("icpt_001")
        self.assertEqual(stored_req.status, HITLDispositionStatus.APPROVED_CONTINUE)


class TestCircuitBreakerEnclave(unittest.TestCase):
    """Tests tri-state circuit breaker, node quarantine, and recovery."""

    def setUp(self) -> None:
        self.breaker = CircuitBreakerEnclave(failure_threshold=3)

    def test_failure_tripping_and_quarantine(self) -> None:
        peer = "192.168.40.20:8442"
        self.assertEqual(self.breaker.current_state, CircuitBreakerState.CLOSED_NORMAL)

        # 1st failure
        self.breaker.record_peer_failure(peer, reason="Timeout 1")
        self.assertFalse(self.breaker.is_peer_quarantined(peer))

        # 2nd failure
        self.breaker.record_peer_failure(peer, reason="Timeout 2")
        self.assertFalse(self.breaker.is_peer_quarantined(peer))

        # 3rd failure: trips breaker
        st = self.breaker.record_peer_failure(peer, reason="Timeout 3")
        self.assertEqual(st, CircuitBreakerState.TRIPPED_OPEN)
        self.assertTrue(self.breaker.is_peer_quarantined(peer))

        # Verify quarantine details
        quarantines = self.breaker.get_active_quarantines()
        self.assertEqual(len(quarantines), 1)
        self.assertEqual(quarantines[0].service_endpoint, peer)
        self.assertEqual(quarantines[0].isolation_subnet, "192.168.40.240/28")

    def test_peer_discharge(self) -> None:
        peer = "192.168.40.20:8442"
        self.breaker.quarantine_peer(peer, reason="Forced isolation")
        self.assertTrue(self.breaker.is_peer_quarantined(peer))

        self.breaker.discharge_peer(peer)
        self.assertFalse(self.breaker.is_peer_quarantined(peer))
        self.assertEqual(self.breaker.current_state, CircuitBreakerState.CLOSED_NORMAL)


class TestRFCProtocolAdjudicator(unittest.TestCase):
    """Tests asymmetric RFC protocol adjudication."""

    def setUp(self) -> None:
        self.adjudicator = RFCProtocolAdjudicator(service_endpoint="192.168.40.50:8448")

    def test_approve_valid_rfc(self) -> None:
        req = SpecAdjustmentRequest(
            request_id="rfc_valid",
            builder_node_id="builder_01",
            target_symbol_urn="urn:meta_axioma:test:buffer",
            bottleneck_type=BottleneckType.TOKEN_EXHAUSTION,
            empirical_evidence="High token demand",
            proposed_delta="Increase lease size",
            preserved_invariants=["[L1-002]"],
        )
        amendment, counter_proof = self.adjudicator.adjudicate_rfc(req)
        self.assertIsNotNone(amendment)
        self.assertTrue(amendment.is_approved)
        self.assertIsNone(counter_proof)
        self.assertEqual(req.disposition_status, RFCDispositionStatus.AMENDED)

    def test_reject_toxic_rfc_with_counter_proof(self) -> None:
        req = SpecAdjustmentRequest(
            request_id="rfc_invalid",
            builder_node_id="builder_02",
            target_symbol_urn="urn:meta_axioma:test:binding",
            bottleneck_type=BottleneckType.COMPLEXITY_LIMIT,
            empirical_evidence="Need local loopback",
            proposed_delta="Bind to 127.0.0.1",
            preserved_invariants=["[L1-002]"],
        )
        amendment, counter_proof = self.adjudicator.adjudicate_rfc(req)
        self.assertIsNotNone(amendment)
        self.assertFalse(amendment.is_approved)
        self.assertIsNotNone(counter_proof)
        self.assertIn("NEG-G2B-001", counter_proof.violated_axioms[0])
        self.assertEqual(req.disposition_status, RFCDispositionStatus.COUNTER_PROVEN)


class TestSuccessionGatekeeper(unittest.TestCase):
    """Tests succession invariant verification and handover certificate issuance."""

    def setUp(self) -> None:
        self.gatekeeper = SuccessionGatekeeper(
            service_endpoint="192.168.40.50:8448",
            governance_hash_chain_head="a" * 64,
        )

    def test_succession_verification_and_certificate(self) -> None:
        hdr_rec = HeuristicDebtRecord.create("hdr_01", 18, 2, 40, 8)
        bindings = ["192.168.40.10:8440", "192.168.40.20:8442", "192.168.40.50:8448"]

        is_ready, deficits = self.gatekeeper.verify_succession_readiness(hdr_rec, bindings)
        self.assertTrue(is_ready)
        self.assertEqual(len(deficits), 0)

        cert = self.gatekeeper.issue_handover_certificate("SIG_MICHAEL_LIPSKI", hdr_rec, bindings)
        self.assertEqual(cert.graduation_status, SuccessionGraduationStatus.CERTIFIED_SUCCESSION_READY)
        self.assertEqual(cert.target_generation, "Generation 5")
        self.assertTrue(cert.zero_loopback_certified)


class TestGovernanceServiceTopology(unittest.TestCase):
    """Tests network topology, non-loopback bindings, and fail-closed partition policy."""

    def setUp(self) -> None:
        self.topology = GovernanceServiceTopology(node_ip="192.168.40.50", port=8448)

    def test_channels_and_transmission(self) -> None:
        ch = self.topology.get_channel("channel_audit_surveillance")
        self.assertTrue(ch.is_active)
        self.topology.transmit("channel_audit_surveillance", 512)
        self.assertEqual(ch.bytes_transmitted, 512)
        self.assertEqual(ch.message_count, 1)

    def test_fail_closed_partition(self) -> None:
        self.topology.trigger_partition()
        self.assertTrue(self.topology.is_partitioned)

        from generations.gen_04b.services.governance.src.service_topology import NetworkPartitionError
        with self.assertRaises(NetworkPartitionError):
            self.topology.get_channel("channel_audit_surveillance")

        self.topology.heal_partition()
        self.assertFalse(self.topology.is_partitioned)
        ch = self.topology.get_channel("channel_audit_surveillance")
        self.assertTrue(ch.is_active)


class TestFunctorialUndoEngine(unittest.TestCase):
    """Tests categorical adjoint state rollback S_{t-1} = f^{-1}(S_t)."""

    def setUp(self) -> None:
        self.undo = FunctorialUndoEngine()

    def test_push_and_rollback(self) -> None:
        state_1 = GovernanceKernelState(
            kernel_id="soc_g4b_governance",
            service_endpoint="192.168.40.50:8448",
            total_violations_trapped=1,
        )
        state_2 = GovernanceKernelState(
            kernel_id="soc_g4b_governance",
            service_endpoint="192.168.40.50:8448",
            total_violations_trapped=2,
        )

        self.undo.push_state(state_1)
        self.undo.push_state(state_2)
        self.assertEqual(self.undo.history_depth(), 2)

        restored = self.undo.undo()
        self.assertIsNotNone(restored)
        self.assertEqual(restored.total_violations_trapped, 1)
        self.assertEqual(self.undo.history_depth(), 1)


class TestStatechartEngine(unittest.TestCase):
    """Tests hierarchical XState v5 state machine transitions and history."""

    def setUp(self) -> None:
        self.engine = StatechartEngine(initial_state=GovernanceStatechartState.GOV_ROOT_IDLE)

    def test_initial_state(self) -> None:
        self.assertEqual(self.engine.current_state, GovernanceStatechartState.GOV_ROOT_IDLE)
        self.assertTrue(self.engine.is_in_state(GovernanceStatechartState.GOV_ROOT_IDLE))

    def test_transitions_and_deep_history(self) -> None:
        # Bootstrap sequence
        self.engine.send("EV_BOOTSTRAP_INIT")
        self.assertEqual(self.engine.current_state, GovernanceStatechartState.GOV_BOOTSTRAPPING)
        self.engine.send("EV_AXIOMS_LOADED")
        self.assertEqual(self.engine.current_state, GovernanceStatechartState.GOV_READY)
        self.engine.send("EV_ENTER_OPERATIONAL")
        self.assertEqual(self.engine.current_state, GovernanceStatechartState.OP_SURVEILLING)

        # Trip to emergency enclave
        self.engine.send("EV_TRIP_CIRCUIT_BREAKER")
        self.assertEqual(self.engine.current_state, GovernanceStatechartState.ENCLAVE_TRIPPED)
        self.engine.send("EV_ISOLATE_NODE")
        self.assertEqual(self.engine.current_state, GovernanceStatechartState.ENCLAVE_QUARANTINE_ISOLATION)
        self.engine.send("EV_BEGIN_INVESTIGATION")
        self.engine.send("EV_START_COOLDOWN_PROBE")
        self.engine.send("EV_PROBE_SUCCEEDED")
        self.assertEqual(self.engine.current_state, GovernanceStatechartState.ENCLAVE_RESTORED)

        # Restore deep history H*
        self.engine.restore_deep_history()
        self.assertEqual(self.engine.current_state, GovernanceStatechartState.OP_SURVEILLING)


class TestGovernanceKernel(unittest.TestCase):
    """Tests end-to-end GovernanceKernel orchestration and event ledger chaining."""

    def setUp(self) -> None:
        self.kernel = GovernanceKernel(node_ip="192.168.40.50", port=8448)

    def test_bootstrap_and_event_chaining(self) -> None:
        state = self.kernel.bootstrap()
        self.assertEqual(state.service_endpoint, "192.168.40.50:8448")
        self.assertEqual(self.kernel.statechart.current_state, GovernanceStatechartState.OP_SURVEILLING)
        head_1 = self.kernel.get_ledger_head()
        self.assertNotEqual(head_1, GovernanceKernel.GENESIS_HASH)

        # Process a custom event
        ev = self.kernel.create_event("TEST_EVENT", "soc_g4b_governance", {"msg": "hello"})
        head_2 = self.kernel.process_event(ev)
        self.assertNotEqual(head_1, head_2)
        self.assertEqual(len(head_2), 64)

        status = self.kernel.get_status()
        self.assertEqual(status["endpoint"], "192.168.40.50:8448")
        self.assertTrue(status["is_debt_compliant"])


if __name__ == "__main__":
    unittest.main()
