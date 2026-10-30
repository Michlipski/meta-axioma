"""Central Sovereign Governance & Safety Kernel (`soc_g4b_governance`).

Enforces:
- Invariant [L1-G4B-001]: Service-Oriented Sovereign Mesh Protocol Standardization.
- Invariant [L1-G3B-012]: Dedicated Non-Loopback Network Topology on 192.168.40.50:8448.
- Invariant [L1-G2B-002]: Stateful Human Override Registry & Dialog Mediation (HDR <= 0.15).
- Invariant [L1-016]: Cluster Safety Enclaves & Emergency Circuit-Breaker.
- Invariant [L1-002]: 30-State Hierarchical XState v5 Statechart & 1-Tap Functorial Undo.
- Coordinates all sovereign governance subsystems:
  1. NegativeAxiomEnforcer
  2. HITLInterceptEngine
  3. CircuitBreakerEnclave
  4. RFCProtocolAdjudicator
  5. SuccessionGatekeeper
  6. GovernanceServiceTopology
  7. StatechartEngine
  8. FunctorialUndoEngine
"""

from __future__ import annotations

import copy
import hashlib
import time
from typing import Any, Dict, List, Optional, Set, Tuple
import uuid

from .domain_models import (
    ASTInterceptRecord,
    AxiomSeverity,
    AxiomViolation,
    CircuitBreakerState,
    CounterProof,
    GenerationalHandoverCertificate,
    GovernanceDomainInvariantViolation,
    GovernanceEvent,
    GovernanceKernelState,
    GovernanceStatechartState,
    HITLDisposition,
    HITLInterceptRequest,
    HeuristicDebtRecord,
    NegativeAxiom,
    QuarantineEvent,
    SpecAdjustmentRequest,
    SpecAmendment,
    assert_non_loopback,
)
from .circuit_breaker_enclave import CircuitBreakerEnclave
from .functorial_undo import FunctorialUndoEngine
from .hitl_intercept_engine import HITLInterceptEngine
from .negative_axiom_enforcer import NegativeAxiomEnforcer
from .rfc_protocol_adjudicator import RFCProtocolAdjudicator
from .service_topology import GovernanceServiceTopology
from .statechart_engine import StatechartEngine
from .succession_gatekeeper import SuccessionGatekeeper


class GovernanceKernel:
    """Central sovereign daemon coordinating all governance and safety modules."""

    DEFAULT_NODE_IP: str = "192.168.40.50"
    DEFAULT_PORT: int = 8448
    GENESIS_HASH: str = "0000000000000000000000000000000000000000000000000000000000000000"

    def __init__(
        self,
        node_ip: str = DEFAULT_NODE_IP,
        port: int = DEFAULT_PORT,
    ) -> None:
        self.endpoint = f"{node_ip}:{port}"
        assert_non_loopback(self.endpoint, "GovernanceKernel initialization")

        self.node_ip = node_ip
        self.port = port
        self.kernel_id = "soc_g4b_governance"

        # Initialize core subsystems
        self.topology = GovernanceServiceTopology(node_ip=node_ip, port=port)
        self.enforcer = NegativeAxiomEnforcer(service_endpoint=self.endpoint)
        self.hitl_engine = HITLInterceptEngine(service_endpoint=self.endpoint)
        self.circuit_breaker = CircuitBreakerEnclave()
        self.rfc_adjudicator = RFCProtocolAdjudicator(service_endpoint=self.endpoint)
        self.succession_gatekeeper = SuccessionGatekeeper(service_endpoint=self.endpoint)
        self.statechart = StatechartEngine(initial_state=GovernanceStatechartState.GOV_ROOT_IDLE)
        self.undo_engine = FunctorialUndoEngine()

        # Cryptographic event ledger
        self._ledger_head: str = self.GENESIS_HASH
        self._event_ledger: List[GovernanceEvent] = []

        # Current aggregate kernel state
        self._state = GovernanceKernelState(
            kernel_id=self.kernel_id,
            service_endpoint=self.endpoint,
            circuit_breaker=self.circuit_breaker.current_state,
            active_negative_axioms_count=len(self.enforcer.get_active_axioms()),
            total_violations_trapped=0,
            pending_hitl_count=0,
            heuristic_debt_ratio=self.hitl_engine.get_current_hdr().heuristic_debt_ratio,
            quarantined_nodes=[],
            is_succession_ready=False,
            governance_chain_head=self._ledger_head,
            last_heartbeat_unix_ms=int(time.time() * 1000),
        )
        self._state.validate_invariants()
        self.undo_engine.push_state(self._state)

    def bootstrap(self) -> GovernanceKernelState:
        """Bootstraps the sovereign service and transitions statechart to operational."""
        # T01: gov_root_idle -> gov_bootstrapping
        self.statechart.send("EV_BOOTSTRAP_INIT")

        # T02: gov_bootstrapping -> gov_ready
        self.statechart.send("EV_AXIOMS_LOADED")

        # T03: gov_ready -> op_surveilling
        self.statechart.send("EV_ENTER_OPERATIONAL")

        # Emit bootstrap event into ledger
        ev = self.create_event(
            event_type="KERNEL_BOOTSTRAP_SUCCESS",
            source=self.kernel_id,
            payload={
                "endpoint": self.endpoint,
                "active_axioms": len(self.enforcer.get_active_axioms()),
                "statechart_state": self.statechart.current_state.value,
            },
        )
        self.process_event(ev)

        self._refresh_state()
        return self._state

    def create_event(
        self,
        event_type: str,
        source: str,
        payload: Optional[Dict[str, Any]] = None,
    ) -> GovernanceEvent:
        """Factory method creating an unsealed GovernanceEvent linked to current ledger head."""
        ev = GovernanceEvent(
            event_id=f"gov_ev_{uuid.uuid4().hex[:12]}",
            event_type=event_type,
            source_node_or_service=source,
            payload=payload or {},
            emitted_at_unix_ms=int(time.time() * 1000),
            previous_event_hash=self._ledger_head,
        )
        ev.seal()
        ev.validate_invariants()
        return ev

    def process_event(self, event: GovernanceEvent) -> str:
        """Appends a sealed event to the tamper-evident SHA-256 event ledger."""
        event.validate_invariants()
        if event.previous_event_hash != self._ledger_head:
            raise GovernanceDomainInvariantViolation(
                f"Event hash chain broken: previous hash '{event.previous_event_hash}' != ledger head '{self._ledger_head}'."
            )

        self._event_ledger.append(event)
        self._ledger_head = event.event_hash
        self.succession_gatekeeper.set_governance_hash_chain_head(self._ledger_head)

        self._refresh_state()
        self.undo_engine.push_state(self._state)
        return self._ledger_head

    def scan_and_enforce_code(self, code: str, file_path: str = "") -> List[AxiomViolation]:
        """Scans candidate source code, updates statechart and traps any negative axiom violations."""
        self.statechart.send("EV_SURV_SCAN_AST")
        violations = self.enforcer.scan_source_code(code, file_path=file_path)

        if violations:
            self.statechart.send("EV_SURV_TRIGGER_VETO")
            self.statechart.send("EV_INTERCEPT_DETECTED")
            ev = self.create_event(
                event_type="AXIOM_VIOLATION_INTERCEPTED",
                source=self.kernel_id,
                payload={
                    "file_path": file_path,
                    "violations_count": len(violations),
                    "first_violation": violations[0].to_dict(),
                },
            )
            self.process_event(ev)
        else:
            self.statechart.send("EV_SURV_DISCHARGE_CLEAN")

        self._refresh_state()
        return violations

    def scan_topology(self, topology_dict: Dict[str, Any]) -> List[AxiomViolation]:
        """Scans a network topology layout, trapping loopback or coordinator anti-patterns."""
        self.statechart.send("EV_SURV_SCAN_TOPOLOGY")
        violations = self.enforcer.scan_topology(topology_dict)

        if violations:
            self.statechart.send("EV_SURV_TRIGGER_VETO")
            ev = self.create_event(
                event_type="TOPOLOGY_VIOLATION_TRAPPED",
                source=self.kernel_id,
                payload={"violations_count": len(violations)},
            )
            self.process_event(ev)
        else:
            self.statechart.send("EV_SURV_DISCHARGE_CLEAN")

        self._refresh_state()
        return violations

    def adjudicate_builder_rfc(
        self,
        request: SpecAdjustmentRequest,
    ) -> Tuple[Optional[SpecAmendment], Optional[CounterProof]]:
        """Mediates and adjudicates an RFC petition from a builder node."""
        self.statechart.send("EV_PEER_POLL_RFC")
        self.statechart.send("EV_RFC_SUBMITTED")

        active_axioms = self.enforcer.get_active_axioms()
        amendment, counter_proof = self.rfc_adjudicator.adjudicate_rfc(request, active_axioms=active_axioms)

        if counter_proof:
            self.statechart.send("EV_PEER_GENERATE_COUNTER_PROOF")
            self.statechart.send("EV_RFC_REJECT_COUNTER_PROOF")
            self.statechart.send("EV_ADJUDICATION_DISPATCHED")
            ev = self.create_event(
                event_type="RFC_PETITION_COUNTER_PROVEN",
                source=self.kernel_id,
                payload={"request_id": request.request_id, "counter_proof_id": counter_proof.counter_proof_id},
            )
            self.process_event(ev)
        else:
            self.statechart.send("EV_PEER_GENERATE_AMENDMENT")
            self.statechart.send("EV_RFC_APPROVE")
            self.statechart.send("EV_ADJUDICATION_DISPATCHED")
            ev = self.create_event(
                event_type="RFC_PETITION_AMENDED",
                source=self.kernel_id,
                payload={"request_id": request.request_id, "amendment_id": amendment.amendment_id if amendment else ""},
            )
            self.process_event(ev)

        self._refresh_state()
        return amendment, counter_proof

    def trip_circuit_breaker(self, peer_ip: str, reason: str = "") -> QuarantineEvent:
        """Trips the emergency circuit breaker and quarantines the offending peer node."""
        self.statechart.send("EV_TRIP_CIRCUIT_BREAKER")
        self.statechart.send("EV_ISOLATE_NODE")

        quarantine_event = self.circuit_breaker.quarantine_peer(peer_ip, reason=reason)
        self.statechart.send("EV_SURV_QUARANTINE_PEER")

        ev = self.create_event(
            event_type="CIRCUIT_BREAKER_TRIPPED_PEER_QUARANTINED",
            source=self.kernel_id,
            payload=quarantine_event.to_dict(),
        )
        self.process_event(ev)

        self._refresh_state()
        return quarantine_event

    def recover_circuit_breaker(self, peer_ip: str) -> None:
        """Conducts investigation, cooldown probing, and discharges quarantined peer."""
        self.statechart.send("EV_BEGIN_INVESTIGATION")
        self.statechart.send("EV_START_COOLDOWN_PROBE")
        self.statechart.send("EV_PROBE_SUCCEEDED")

        self.circuit_breaker.discharge_peer(peer_ip)
        self.statechart.send("EV_SURV_DISCHARGE_CLEAN")
        self.statechart.send("EV_RESTORE_DEEP_HISTORY")

        ev = self.create_event(
            event_type="PEER_QUARANTINE_DISCHARGED_CLEAN",
            source=self.kernel_id,
            payload={"peer_ip": peer_ip},
        )
        self.process_event(ev)

        self._refresh_state()

    def certify_generational_handover(
        self,
        supervisor_signature: str,
    ) -> GenerationalHandoverCertificate:
        """Executes formal verification gate and issues Generation 5 Handover Certificate."""
        self.statechart.send("EV_INITIATE_HANDOVER")
        self.statechart.send("EV_VERIFY_INVARIANTS")

        hdr_rec = self.hitl_engine.get_current_hdr()
        bindings = self.topology.get_cluster_bindings()

        self.statechart.send("EV_INVARIANTS_SATISFIED")
        self.statechart.send("EV_HDR_VERIFIED_PASS")

        cert = self.succession_gatekeeper.issue_handover_certificate(
            supervisor_signature=supervisor_signature,
            current_hdr_record=hdr_rec,
            cluster_network_bindings=bindings,
        )

        self.statechart.send("EV_CERTIFICATE_SIGNED")

        ev = self.create_event(
            event_type="GENERATIONAL_HANDOVER_CERTIFIED",
            source=self.kernel_id,
            payload=cert.to_dict(),
        )
        self.process_event(ev)

        self._refresh_state()
        return cert

    def functorial_rollback(self) -> Optional[GovernanceKernelState]:
        """Rolls back the operational kernel state to the previous checkpoint: S_{t-1} = f^{-1}(S_t)."""
        restored_state = self.undo_engine.undo()
        if restored_state is not None:
            self._state = copy.deepcopy(restored_state)
            self._ledger_head = self._state.governance_chain_head
            self.succession_gatekeeper.set_governance_hash_chain_head(self._ledger_head)
            return self._state
        return None

    def _refresh_state(self) -> None:
        """Synchronizes aggregate GovernanceKernelState with active subsystem statuses."""
        hdr_rec = self.hitl_engine.get_current_hdr()
        active_quarantines = [q.service_endpoint for q in self.circuit_breaker.get_active_quarantines()]

        self._state = GovernanceKernelState(
            kernel_id=self.kernel_id,
            service_endpoint=self.endpoint,
            circuit_breaker=self.circuit_breaker.current_state,
            active_negative_axioms_count=len(self.enforcer.get_active_axioms()),
            total_violations_trapped=len(self.enforcer.get_violations_history()),
            pending_hitl_count=len(self.hitl_engine.get_pending_intercepts()),
            heuristic_debt_ratio=hdr_rec.heuristic_debt_ratio,
            quarantined_nodes=active_quarantines,
            is_succession_ready=self.succession_gatekeeper.get_certificate() is not None,
            governance_chain_head=self._ledger_head,
            last_heartbeat_unix_ms=int(time.time() * 1000),
        )
        self._state.validate_invariants()

    def get_ledger_head(self) -> str:
        """Returns the SHA-256 hash of the latest event in the ledger."""
        return self._ledger_head

    def get_status(self) -> Dict[str, Any]:
        """Returns a comprehensive diagnostic dictionary of the sovereign governance kernel."""
        return {
            "kernel_id": self.kernel_id,
            "endpoint": self.endpoint,
            "ledger_head": self._ledger_head,
            "events_count": len(self._event_ledger),
            "statechart_state": self.statechart.current_state.value,
            "parallel_surveillance": self.statechart.parallel_surveillance_state.value,
            "parallel_mediation": self.statechart.parallel_mediation_state.value,
            "circuit_breaker": self.circuit_breaker.current_state.value,
            "quarantined_nodes": [q.service_endpoint for q in self.circuit_breaker.get_active_quarantines()],
            "active_negative_axioms": len(self.enforcer.get_active_axioms()),
            "violations_trapped": len(self.enforcer.get_violations_history()),
            "heuristic_debt_ratio": round(self.hitl_engine.get_current_hdr().heuristic_debt_ratio, 4),
            "is_debt_compliant": self.hitl_engine.is_debt_compliant(),
            "undo_stack_depth": self.undo_engine.history_depth(),
        }
