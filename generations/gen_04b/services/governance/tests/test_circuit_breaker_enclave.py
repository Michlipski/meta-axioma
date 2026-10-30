"""Exhaustive Test Suite for Cluster Safety Enclave & Emergency Circuit-Breaker (`soc_g4b_governance`).

Enforces:
- Invariant [L1-016]: Cluster Safety Enclaves & Emergency Circuit-Breaker.
- Invariant [L1-G3B-012]: Dedicated Non-Loopback Network Topology.
- Tri-state lifecycle: CLOSED_NORMAL, TRIPPED_OPEN, HALF_OPEN_PROBING, RECOVERY_ENCLAVE_ACTIVE.
- Selective peer quarantine into 192.168.40.240/28 isolation subnet without disturbing healthy mesh peers.
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
    CircuitBreakerState,
    GovernanceDomainInvariantViolation,
    PeerQuarantineStatus,
    QuarantineEvent,
)
from src.circuit_breaker_enclave import CircuitBreakerEnclave


class TestCircuitBreakerEnclave(unittest.TestCase):
    """Exhaustive unit and invariant tests for CircuitBreakerEnclave."""

    def setUp(self) -> None:
        self.enclave = CircuitBreakerEnclave(
            failure_threshold=3,
            cooldown_seconds=5.0,
            isolation_subnet="192.168.40.240/28",
        )

    def test_initial_state_closed_normal(self) -> None:
        """Enclave initializes in CLOSED_NORMAL with zero active quarantines."""
        self.assertEqual(self.enclave.current_state, CircuitBreakerState.CLOSED_NORMAL)
        self.assertEqual(len(self.enclave.get_active_quarantines()), 0)
        self.assertFalse(self.enclave.is_peer_quarantined("192.168.40.20:8442"))

    def test_record_peer_failure_below_threshold(self) -> None:
        """Failures below threshold do not trip breaker."""
        s1 = self.enclave.record_peer_failure("192.168.40.20:8442", "Transient timeout")
        self.assertEqual(s1, CircuitBreakerState.CLOSED_NORMAL)

        s2 = self.enclave.record_peer_failure("192.168.40.20:8442", "Transient retryable 503")
        self.assertEqual(s2, CircuitBreakerState.CLOSED_NORMAL)
        self.assertFalse(self.enclave.is_peer_quarantined("192.168.40.20:8442"))

    def test_record_peer_failure_trips_to_open_at_threshold(self) -> None:
        """Trips to TRIPPED_OPEN when consecutive failure threshold (3) is reached."""
        self.enclave.record_peer_failure("192.168.40.20:8442", "Fail 1")
        self.enclave.record_peer_failure("192.168.40.20:8442", "Fail 2")
        state_tripped = self.enclave.record_peer_failure("192.168.40.20:8442", "Fail 3")

        self.assertEqual(state_tripped, CircuitBreakerState.TRIPPED_OPEN)
        self.assertEqual(self.enclave.current_state, CircuitBreakerState.TRIPPED_OPEN)
        self.assertTrue(self.enclave.is_peer_quarantined("192.168.40.20:8442"))

        # Verify quarantine event
        quarantines = self.enclave.get_active_quarantines()
        self.assertEqual(len(quarantines), 1)
        self.assertEqual(quarantines[0].service_endpoint, "192.168.40.20:8442")
        self.assertEqual(quarantines[0].isolation_subnet, "192.168.40.240/28")
        self.assertEqual(quarantines[0].quarantine_status, PeerQuarantineStatus.QUARANTINED_ISOLATED)

    def test_selective_peer_quarantine_does_not_affect_healthy_peers(self) -> None:
        """Only the failing peer is quarantined; healthy mesh peers remain unconstrained."""
        failing_peer = "192.168.40.20:8442"
        healthy_peers = [
            "192.168.40.10:8440",
            "192.168.40.30:8444",
            "192.168.40.40:8446",
        ]

        # Trip failing peer
        for i in range(3):
            self.enclave.record_peer_failure(failing_peer, f"Failure {i}")

        self.assertTrue(self.enclave.is_peer_quarantined(failing_peer))

        for hp in healthy_peers:
            self.assertFalse(
                self.enclave.is_peer_quarantined(hp),
                f"Healthy peer {hp} was mistakenly quarantined!",
            )

    def test_half_open_probing_and_recovery_to_closed(self) -> None:
        """Half-open probing transitions to CLOSED_NORMAL upon successful peer operation."""
        peer = "192.168.40.20:8442"
        for i in range(3):
            self.enclave.record_peer_failure(peer, f"Failure {i}")

        self.assertEqual(self.enclave.current_state, CircuitBreakerState.TRIPPED_OPEN)

        # Start probing
        self.enclave.start_probing()
        self.assertEqual(self.enclave.current_state, CircuitBreakerState.HALF_OPEN_PROBING)

        # Successful operation restores to CLOSED_NORMAL
        self.enclave.record_peer_success(peer)
        self.assertEqual(self.enclave.current_state, CircuitBreakerState.CLOSED_NORMAL)

    def test_discharge_peer_from_quarantine(self) -> None:
        """Remediated peer is cleanly discharged from quarantine."""
        peer = "192.168.40.30:8444"
        event = self.enclave.quarantine_peer(peer, reason="Manual safety isolation")
        self.assertTrue(self.enclave.is_peer_quarantined(peer))

        self.enclave.discharge_peer(peer)
        self.assertFalse(self.enclave.is_peer_quarantined(peer))
        self.assertEqual(event.quarantine_status, PeerQuarantineStatus.DISCHARGED_CLEAN)
        self.assertGreater(event.released_at_unix_ms, 0)

    def test_loopback_rejected_in_all_circuit_breaker_methods(self) -> None:
        """Enclave rejects loopback IP addresses across all operational methods."""
        loopbacks = ["127.0.0.1:8448", "localhost:8448", "::1:8448", "0.0.0.0:8448"]
        for lb in loopbacks:
            with self.assertRaises(GovernanceDomainInvariantViolation):
                self.enclave.record_peer_failure(lb)
            with self.assertRaises(GovernanceDomainInvariantViolation):
                self.enclave.record_peer_success(lb)
            with self.assertRaises(GovernanceDomainInvariantViolation):
                self.enclave.quarantine_peer(lb)
            with self.assertRaises(GovernanceDomainInvariantViolation):
                self.enclave.discharge_peer(lb)

    def test_state_record_roundtrip_and_hash(self) -> None:
        """State record serialization roundtrip and hash computation."""
        record = self.enclave.get_state_record()
        record.validate_invariants()
        h = record.compute_hash()
        self.assertEqual(len(h), 64)

        d = record.to_dict()
        self.assertEqual(d["current_state"], CircuitBreakerState.CLOSED_NORMAL.value)
        self.assertEqual(d["failure_threshold"], 3)


if __name__ == "__main__":
    unittest.main()
