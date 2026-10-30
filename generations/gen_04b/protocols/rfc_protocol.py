"""Generation 4b Asynchronous RFC Protocol (`protocols/rfc_protocol.py`).

Enforces:
- [L1-G4B-001] Service-Oriented Sovereign Mesh Protocol Standardization.
- Asymmetric Negotiation: Builder petitions via SpecAdjustmentRequest; Research/Adjudicator responds
  with signed SpecAmendment or formal Z3 SMT CounterProof.
- Complete domain invariants and algebraic serialization roundtripping.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
import hashlib
import json
import time
from typing import Any, Dict, List, Optional


class RFCProtocolViolation(Exception):
    """Raised when an RFC protocol invariant is violated."""
    pass


class BottleneckType(str, Enum):
    """Classification of engineering bottleneck prompting a SpecAdjustmentRequest."""
    TOKEN_EXHAUSTION = "TOKEN_EXHAUSTION"
    LATENCY_OVERRUN = "LATENCY_OVERRUN"
    PHYSICAL_IRREVERSIBILITY = "PHYSICAL_IRREVERSIBILITY"
    COMPLEXITY_LIMIT = "COMPLEXITY_LIMIT"


class SolverResult(str, Enum):
    """SMT solver satisfaction result."""
    SAT = "SAT"
    UNSAT = "UNSAT"
    UNKNOWN = "UNKNOWN"


class RFCStatus(str, Enum):
    """Lifecycle status of a SpecAdjustmentRequest."""
    SUBMITTED = "SUBMITTED"
    ADJUDICATING = "ADJUDICATING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    WITHDRAWN = "WITHDRAWN"


@dataclass
class SpecAdjustmentRequest:
    """Builder-submitted petition requesting a specification delta under physical friction."""
    request_id: str
    builder_node_id: str
    target_symbol_urn: str
    bottleneck_type: BottleneckType
    empirical_evidence: str
    proposed_delta: str
    preserved_invariants: List[str]
    status: RFCStatus = RFCStatus.SUBMITTED
    submitted_at_unix_ms: int = field(default_factory=lambda: int(time.time() * 1000))

    def validate_invariants(self) -> None:
        if not self.request_id:
            raise RFCProtocolViolation("request_id must not be empty.")
        if not self.builder_node_id:
            raise RFCProtocolViolation("builder_node_id must not be empty.")
        if not self.target_symbol_urn:
            raise RFCProtocolViolation("target_symbol_urn must not be empty.")
        if len(self.preserved_invariants) < 1:
            raise RFCProtocolViolation("SpecAdjustmentRequest must preserve at least one core invariant.")
        if not self.empirical_evidence:
            raise RFCProtocolViolation("empirical_evidence is mandatory for an RFC request.")
        if not self.proposed_delta:
            raise RFCProtocolViolation("proposed_delta must not be empty.")

    def compute_request_hash(self) -> str:
        payload = f"{self.request_id}:{self.builder_node_id}:{self.target_symbol_urn}:{self.bottleneck_type.value}:{self.proposed_delta}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "request_id": self.request_id,
            "builder_node_id": self.builder_node_id,
            "target_symbol_urn": self.target_symbol_urn,
            "bottleneck_type": self.bottleneck_type.value,
            "empirical_evidence": self.empirical_evidence,
            "proposed_delta": self.proposed_delta,
            "preserved_invariants": self.preserved_invariants,
            "status": self.status.value,
            "submitted_at_unix_ms": self.submitted_at_unix_ms,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> SpecAdjustmentRequest:
        instance = cls(
            request_id=data["request_id"],
            builder_node_id=data["builder_node_id"],
            target_symbol_urn=data["target_symbol_urn"],
            bottleneck_type=BottleneckType(data["bottleneck_type"]),
            empirical_evidence=data["empirical_evidence"],
            proposed_delta=data["proposed_delta"],
            preserved_invariants=list(data.get("preserved_invariants", [])),
            status=RFCStatus(data.get("status", RFCStatus.SUBMITTED.value)),
            submitted_at_unix_ms=int(data.get("submitted_at_unix_ms", int(time.time() * 1000))),
        )
        instance.validate_invariants()
        return instance


@dataclass
class CounterProof:
    """Formal mathematical or empirical proof refuting a builder's RFC request."""
    counter_proof_id: str
    request_id: str
    violated_axioms: List[str]
    z3_unsat_core: Optional[str]
    counter_example_model: Dict[str, Any] = field(default_factory=dict)
    adjudicator_node_id: str = "node_research_kernel"

    def validate_invariants(self) -> None:
        if not self.counter_proof_id:
            raise RFCProtocolViolation("counter_proof_id must not be empty.")
        if not self.request_id:
            raise RFCProtocolViolation("request_id must not be empty.")
        if len(self.violated_axioms) < 1:
            raise RFCProtocolViolation("CounterProof must cite at least one violated axiom or invariant.")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "counter_proof_id": self.counter_proof_id,
            "request_id": self.request_id,
            "violated_axioms": self.violated_axioms,
            "z3_unsat_core": self.z3_unsat_core,
            "counter_example_model": self.counter_example_model,
            "adjudicator_node_id": self.adjudicator_node_id,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> CounterProof:
        instance = cls(
            counter_proof_id=data["counter_proof_id"],
            request_id=data["request_id"],
            violated_axioms=list(data.get("violated_axioms", [])),
            z3_unsat_core=data.get("z3_unsat_core"),
            counter_example_model=dict(data.get("counter_example_model", {})),
            adjudicator_node_id=data.get("adjudicator_node_id", "node_research_kernel"),
        )
        instance.validate_invariants()
        return instance


@dataclass
class SpecAmendment:
    """Cryptographically signed amendment or rejection counter-proof emitted by Research."""
    amendment_id: str
    request_id: str
    is_approved: bool
    adjudicator_signature: str
    amended_contract_ir_delta: str
    rejection_counter_proof: Optional[CounterProof | str] = None
    adjudicated_at_unix_ms: int = field(default_factory=lambda: int(time.time() * 1000))

    def validate_invariants(self) -> None:
        if not self.amendment_id:
            raise RFCProtocolViolation("amendment_id must not be empty.")
        if not self.request_id:
            raise RFCProtocolViolation("request_id must not be empty.")
        if not self.adjudicator_signature:
            raise RFCProtocolViolation("adjudicator_signature is mandatory.")
        if not self.is_approved:
            if not self.rejection_counter_proof:
                raise RFCProtocolViolation(
                    "Rejected SpecAmendment strictly requires a formal rejection_counter_proof."
                )

    def to_dict(self) -> Dict[str, Any]:
        counter_proof_dict = None
        if isinstance(self.rejection_counter_proof, CounterProof):
            counter_proof_dict = self.rejection_counter_proof.to_dict()
        elif isinstance(self.rejection_counter_proof, str):
            counter_proof_dict = self.rejection_counter_proof

        return {
            "amendment_id": self.amendment_id,
            "request_id": self.request_id,
            "is_approved": self.is_approved,
            "adjudicator_signature": self.adjudicator_signature,
            "amended_contract_ir_delta": self.amended_contract_ir_delta,
            "rejection_counter_proof": counter_proof_dict,
            "adjudicated_at_unix_ms": self.adjudicated_at_unix_ms,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> SpecAmendment:
        counter_proof_raw = data.get("rejection_counter_proof")
        counter_proof_obj = None
        if isinstance(counter_proof_raw, dict):
            counter_proof_obj = CounterProof.from_dict(counter_proof_raw)
        elif isinstance(counter_proof_raw, str):
            counter_proof_obj = counter_proof_raw

        instance = cls(
            amendment_id=data["amendment_id"],
            request_id=data["request_id"],
            is_approved=bool(data["is_approved"]),
            adjudicator_signature=data["adjudicator_signature"],
            amended_contract_ir_delta=data.get("amended_contract_ir_delta", ""),
            rejection_counter_proof=counter_proof_obj,
            adjudicated_at_unix_ms=int(data.get("adjudicated_at_unix_ms", int(time.time() * 1000))),
        )
        instance.validate_invariants()
        return instance
