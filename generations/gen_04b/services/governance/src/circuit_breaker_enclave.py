"""Tri-State Cluster Safety Enclave & Emergency Circuit-Breaker (`soc_g4b_governance`).

Enforces:
- Invariant [L1-016]: Cluster Safety Enclaves & Emergency Circuit-Breaker.
- States: CLOSED_NORMAL, TRIPPED_OPEN, HALF_OPEN_PROBING, RECOVERY_ENCLAVE_ACTIVE.
- Directs quarantined peers to isolation subnet 192.168.40.240/28 while preserving healthy mesh traffic.
- Provides peer failure tracking, threshold tripping, cooldown probing, and clean discharge.
"""

from __future__ import annotations

import time
from typing import Any, Dict, List, Optional
import uuid

from .domain_models import (
    CircuitBreakerState,
    CircuitBreakerStateRecord,
    CircuitBreakerTrippedError,
    GovernanceDomainInvariantViolation,
    PeerQuarantineStatus,
    QuarantineEvent,
    assert_non_loopback,
)


class CircuitBreakerEnclave:
    """Manages the tri-state cluster safety enclave, node isolation, and circuit breakers."""

    DEFAULT_ISOLATION_SUBNET: str = "192.168.40.240/28"

    def __init__(
        self,
        failure_threshold: int = 3,
        cooldown_seconds: float = 10.0,
        isolation_subnet: str = DEFAULT_ISOLATION_SUBNET,
    ) -> None:
        self.failure_threshold = failure_threshold
        self.cooldown_seconds = cooldown_seconds
        self.isolation_subnet = isolation_subnet

        self._record = CircuitBreakerStateRecord(
            record_id=f"cb_rec_{uuid.uuid4().hex[:12]}",
            current_state=CircuitBreakerState.CLOSED_NORMAL,
            failure_count=0,
            failure_threshold=failure_threshold,
            cooldown_seconds=cooldown_seconds,
            quarantined_peer_endpoints=[],
        )
        self._record.validate_invariants()

        self._quarantines: Dict[str, QuarantineEvent] = {}  # endpoint -> QuarantineEvent
        self._peer_failure_counts: Dict[str, int] = {}

    @property
    def current_state(self) -> CircuitBreakerState:
        return self._record.current_state

    def record_peer_failure(self, peer_ip: str, reason: str = "") -> CircuitBreakerState:
        """Records an operational failure for a peer node and trips the breaker if threshold is met."""
        assert_non_loopback(peer_ip, "record_peer_failure")
        self._peer_failure_counts[peer_ip] = self._peer_failure_counts.get(peer_ip, 0) + 1
        self._record.trip(peer_ip)

        if self._record.current_state == CircuitBreakerState.TRIPPED_OPEN:
            if not self.is_peer_quarantined(peer_ip):
                self.quarantine_peer(peer_ip, reason=f"Failure threshold reached: {reason}")
            self._record.current_state = CircuitBreakerState.TRIPPED_OPEN

        return self._record.current_state

    def record_peer_success(self, peer_ip: str) -> None:
        """Records a successful operation for a peer node, resetting its consecutive failure counter."""
        assert_non_loopback(peer_ip, "record_peer_success")
        self._peer_failure_counts[peer_ip] = 0

        # If breaker was HALF_OPEN_PROBING and peer succeeds, transition back to CLOSED_NORMAL
        if self._record.current_state == CircuitBreakerState.HALF_OPEN_PROBING:
            self._record.current_state = CircuitBreakerState.CLOSED_NORMAL
            self._record.failure_count = 0

    def quarantine_peer(self, peer_ip: str, reason: str = "") -> QuarantineEvent:
        """Isolates a failing or adversarial peer node to the isolation subnet."""
        assert_non_loopback(peer_ip, "quarantine_peer")
        r = reason or "Quarantined by safety enclave"

        node_id = f"node_{peer_ip.replace('.', '_').replace(':', '_')}"
        event_id = f"quar_{uuid.uuid4().hex[:12]}"

        event = QuarantineEvent(
            event_id=event_id,
            node_id=node_id,
            service_endpoint=peer_ip,
            quarantine_status=PeerQuarantineStatus.QUARANTINED_ISOLATED,
            triggering_violation_id=f"viol_cb_{uuid.uuid4().hex[:8]}",
            isolation_subnet=self.isolation_subnet,
            reason=r,
            initiated_at_unix_ms=int(time.time() * 1000),
        )
        event.validate_invariants()

        self._quarantines[peer_ip] = event
        if peer_ip not in self._record.quarantined_peer_endpoints:
            self._record.quarantined_peer_endpoints.append(peer_ip)

        # Set enclave state to RECOVERY_ENCLAVE_ACTIVE if not already TRIPPED_OPEN
        if self._record.current_state != CircuitBreakerState.TRIPPED_OPEN:
            self._record.current_state = CircuitBreakerState.RECOVERY_ENCLAVE_ACTIVE

        return event

    def discharge_peer(self, peer_ip: str) -> None:
        """Discharges a remediated peer from quarantine back into healthy unconstrained pool."""
        assert_non_loopback(peer_ip, "discharge_peer")
        if peer_ip in self._quarantines:
            event = self._quarantines[peer_ip]
            event.quarantine_status = PeerQuarantineStatus.DISCHARGED_CLEAN
            event.released_at_unix_ms = int(time.time() * 1000)
            del self._quarantines[peer_ip]

        if peer_ip in self._record.quarantined_peer_endpoints:
            self._record.quarantined_peer_endpoints.remove(peer_ip)

        self._peer_failure_counts[peer_ip] = 0

        # If no peers remain quarantined, reset breaker to CLOSED_NORMAL
        if not self._quarantines:
            self._record.reset_clean()

    def is_peer_quarantined(self, peer_ip: str) -> bool:
        """Checks if a given peer endpoint is currently quarantined."""
        assert_non_loopback(peer_ip, "is_peer_quarantined")
        return peer_ip in self._quarantines

    def get_active_quarantines(self) -> List[QuarantineEvent]:
        """Returns all currently active peer quarantine records."""
        return list(self._quarantines.values())

    def start_probing(self) -> None:
        """Transitions from TRIPPED_OPEN to HALF_OPEN_PROBING when cooldown period elapses."""
        if self._record.current_state == CircuitBreakerState.TRIPPED_OPEN:
            self._record.current_state = CircuitBreakerState.HALF_OPEN_PROBING
            self._record.last_probed_unix_ms = int(time.time() * 1000)

    def get_state_record(self) -> CircuitBreakerStateRecord:
        """Returns the current state record of the circuit breaker."""
        return self._record
