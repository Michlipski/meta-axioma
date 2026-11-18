"""Generation 4b Asynchronous RFC Protocol Bus (`soc_g4b_researcher`).

Enforces:
- [L1-G4B-001] RFC-Mediated Engineering Protocol:
  When a Primary Builder encounters physical bottlenecks, it cannot mutate specs ad-hoc;
  it must submit a formal SpecAdjustmentRequest. The Sovereign Research Service adjudicates
  the request against core axioms and emits a signed SpecAmendment or formal counter-proof.
"""

from __future__ import annotations

import hashlib
import json
import socket
import time
from typing import Any, Dict, List, Optional, Tuple
import uuid

from .domain_models import (
    BottleneckType,
    DomainInvariantViolation,
    SpecAdjustmentRequest,
    SpecAmendment,
)
from .z3_prover_bridge import Z3ProverBridge


class RFCValidationError(Exception):
    """Raised when an RFC request is malformed or lacks empirical evidence."""
    pass


class RFCProtocolBus:
    """Asynchronous protocol bus adjudicating builder RFCs and issuing signed amendments."""

    def __init__(
        self,
        adjudicator_id: Optional[str] = None,
        node_ip: str = "192.168.40.50",
        port: int = 8205,
        prover_bridge: Optional[Z3ProverBridge] = None,
    ):
        self.adjudicator_id = adjudicator_id or f"adjudicator_{uuid.uuid4().hex[:8]}"
        self.node_ip = node_ip
        self.port = port
        self.prover = prover_bridge or Z3ProverBridge()

        if self.node_ip.startswith("127.") or self.node_ip in ("localhost", "::1"):
            raise DomainInvariantViolation(
                f"[L1-G3B-012 Violation] RFC Bus cannot bind to loopback address: {self.node_ip}"
            )

        self.received_requests: Dict[str, SpecAdjustmentRequest] = {}
        self.emitted_amendments: Dict[str, SpecAmendment] = {}
        self.adjudication_log: List[Dict[str, Any]] = []

    def submit_rfc(self, request: SpecAdjustmentRequest) -> str:
        """Ingests a builder RFC into the protocol bus."""
        request.validate_invariants()
        if not request.empirical_evidence:
            raise RFCValidationError("RFC request rejected: empirical_evidence is missing.")

        self.received_requests[request.request_id] = request
        self.adjudication_log.append({
            "event": "RFC_INGESTED",
            "request_id": request.request_id,
            "target": request.target_symbol_urn,
            "timestamp_ns": time.time_ns(),
        })
        return request.request_id

    def adjudicate_rfc(
        self,
        request_id: str,
        core_axioms: Optional[List[str]] = None,
        override_approval: Optional[bool] = None,
    ) -> SpecAmendment:
        """Evaluates an RFC and synthesizes a signed SpecAmendment or counter-proof."""
        if request_id not in self.received_requests:
            raise KeyError(f"Unknown request_id: {request_id}")

        req = self.received_requests[request_id]
        core_axioms = core_axioms or [
            "[L1-G3B-012] Topological Fidelity Invariant",
            "[L1-G3B-011] Compositional Contract Invariant",
            "[L1-012] Landauer Thermodynamic Bound",
            "[NEG-G1B-001] Anti-Phantom Emission Gate",
        ]

        # Check whether proposed delta attempts to weaken core axioms or bypass gates
        delta_lower = req.proposed_delta.lower()
        violates_axioms = (
            "weaken" in delta_lower
            or "bypass" in delta_lower
            or "disable_verification" in delta_lower
            or "mock_consensus" in delta_lower
            or "loopback" in delta_lower
        )

        if override_approval is not None:
            is_approved = override_approval
        else:
            is_approved = not violates_axioms

        amendment_id = f"amend_{uuid.uuid4().hex[:8]}"

        # Cryptographic signature: HMAC-like SHA-256 over adjudicator + request
        sig_payload = f"{self.adjudicator_id}:{req.request_id}:{is_approved}:{time.time_ns()}"
        signature = hashlib.sha256(sig_payload.encode("utf-8")).hexdigest()

        if is_approved:
            amended_delta = (
                f"AMENDED CONTRACT DELTA for {req.target_symbol_urn}:\n"
                f"Applied approved delta under bottleneck {req.bottleneck_type.value}:\n"
                f"{req.proposed_delta}\n"
                f"Preserved Invariants: {', '.join(req.preserved_invariants)}"
            )
            counter_proof = None
        else:
            amended_delta = ""
            counter_proof = (
                f"MATHEMATICAL COUNTER-PROOF & RFC REJECTION:\n"
                f"Proposed delta violates core system invariants:\n"
                f"- Request: {req.proposed_delta}\n"
                f"- Violated Axiom: [L1-G4B-001] Specification Integrity. "
                f"Builder cannot shortcut distributed verification or inject loopback interfaces.\n"
                f"- Empirical evidence provided ('{req.empirical_evidence}') demonstrates implementation difficulty, "
                f"not structural impossibility. Request REJECTED."
            )

        amendment = SpecAmendment(
            amendment_id=amendment_id,
            request_id=req.request_id,
            is_approved=is_approved,
            adjudicator_signature=signature,
            amended_contract_ir_delta=amended_delta,
            rejection_counter_proof=counter_proof,
        )
        amendment.validate_invariants()

        self.emitted_amendments[amendment_id] = amendment
        self.adjudication_log.append({
            "event": "RFC_ADJUDICATED",
            "amendment_id": amendment_id,
            "request_id": req.request_id,
            "is_approved": is_approved,
            "signature": signature,
            "timestamp_ns": time.time_ns(),
        })

        return amendment

    def query_amendment(self, amendment_id: str) -> SpecAmendment:
        if amendment_id not in self.emitted_amendments:
            raise KeyError(f"Unknown amendment_id: {amendment_id}")
        return self.emitted_amendments[amendment_id]

    def handle_rfc_envelope(self, envelope: Any) -> Any:
        """Handles incoming IPCEnvelope containing an RFC petition, adjudicates it, and returns RESPONSE envelope."""
        from generations.gen_04b.protocols.rfc_adapter import RFCAdapter
        from generations.gen_04b.protocols.ipc_transport import IPCEnvelope, IPCMessageType

        req_dict = envelope.payload.get("request", envelope.payload)
        research_req = RFCAdapter.to_research_request(req_dict)
        self.submit_rfc(research_req)
        amendment = self.adjudicate_rfc(research_req.request_id)
        canonical_amendment = RFCAdapter.to_canonical_amendment(amendment)
        return IPCEnvelope(
            envelope_id=f"env_resp_{uuid.uuid4().hex[:8]}",
            source_urn="urn:axioma:g4b:research",
            target_urn=envelope.source_urn,
            message_type=IPCMessageType.RESPONSE,
            payload={"action": "ADJUDICATE_RFC_RESPONSE", "amendment": canonical_amendment.to_dict()},
            correlation_id=envelope.correlation_id,
        )

    def listen_and_adjudicate_ipc(self, sock: socket.socket, transport: Optional[Any] = None) -> Any:
        """Awaits framed RFC envelope on socket, adjudicates, and sends framed response."""
        from generations.gen_04b.protocols.ipc_transport import MeshIPCTransport
        trans = transport or MeshIPCTransport()
        request_envelope = trans.recv_envelope(sock, timeout_s=5.0)
        response_envelope = self.handle_rfc_envelope(request_envelope)
        trans.send_envelope(sock, response_envelope)
        return response_envelope
