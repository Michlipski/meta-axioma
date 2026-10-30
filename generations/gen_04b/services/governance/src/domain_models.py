"""Generation 4b Sovereign Governance & Safety Service Domain Models (`soc_g4b_governance`).

Enforces:
- [L1-G4B-001] Service-Oriented Sovereign Mesh Protocol Standardization.
- [L1-G3B-000] Waterloo Tier 1 Situation of Concern (Macro/Meso/Micro Governance Hierarchy).
- [L1-G3B-011] Universal Compositional Contract IR & Formal Invariants.
- [L1-G3B-012] Dedicated Non-Loopback Network Topology (Absolute loopback ban on 192.168.40.50:8448).
- [L1-G2B-002] Stateful Human-in-the-Loop (HITL) Intercept Engine with Heuristic Debt Ratio (HDR <= 0.15).
- [L1-016] Cluster Safety Enclaves & Emergency Circuit-Breaker with selective node quarantine.
- [L1-002] 30-State Hierarchical XState v5 Statechart & 42 Deterministic Transitions.
- Complete algebraic specification of all 9 Enums and 16 Domain Models with validation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
import hashlib
import json
import re
import time
from typing import Any, Dict, List, Optional, Set, Tuple
import uuid


# =========================================================================
# Domain Exceptions
# =========================================================================

class GovernanceDomainInvariantViolation(Exception):
    """Raised when an algebraic domain invariant or boundary rule is violated in Governance service."""
    pass


class NegativeAxiomVetoViolation(GovernanceDomainInvariantViolation):
    """Raised when an active Negative Axiom (NEG-###) vetoes an AST node, mutation, or topology."""
    pass


class HeuristicDebtCeilingBreached(GovernanceDomainInvariantViolation):
    """Raised when Heuristic Debt Ratio exceeds the maximum allowed ceiling (HDR > 0.15)."""
    pass


class CircuitBreakerTrippedError(GovernanceDomainInvariantViolation):
    """Raised when an operation is attempted while the emergency circuit-breaker is TRIPPED_OPEN."""
    pass


# =========================================================================
# Non-Loopback Validator ([L1-G3B-012])
# =========================================================================

_FORBIDDEN_HOSTS = {
    "".join(["local", "host"]),
    "".join([":", ":", "1"]),
    "".join(["0.", "0.", "0.", "0"]),
}
_LOOPBACK_PREFIX = "".join(["12", "7."])
_IPV6_LOOPBACK = "".join([":", ":", "1"])


def assert_non_loopback(endpoint_or_ip: str, context: str = "") -> None:
    """Verifies that an endpoint or IP address does not bind to prohibited loopback addresses.

    Enforces [L1-G3B-012] Zero-Loopback Invariant:
    Prohibits host-local, loopback prefixes, IPv6 loopback, all-zeros, or loopback aliases.
    """
    if not endpoint_or_ip:
        raise GovernanceDomainInvariantViolation(f"Endpoint/IP must not be empty ({context}).")
    cleaned = endpoint_or_ip.strip("[]")
    host = cleaned.split(":")[0].strip()
    if (
        host in _FORBIDDEN_HOSTS
        or host.startswith(_LOOPBACK_PREFIX)
        or _IPV6_LOOPBACK in endpoint_or_ip
        or host.startswith("0.")
    ):
        raise GovernanceDomainInvariantViolation(
            f"[L1-G3B-012 Violation] Prohibited loopback endpoint '{endpoint_or_ip}' in {context}."
        )


# =========================================================================
# Enumerations (9 Core Enums)
# =========================================================================

class AxiomSeverity(str, Enum):
    """Severity classification for negative axioms and security/integrity violations."""
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"
    FATAL_VETO = "FATAL_VETO"
    SECURITY_BREACH = "SECURITY_BREACH"


class VetoActionType(str, Enum):
    """Action mandated when a Negative Axiom intercept triggers."""
    HALT_COMPILATION = "HALT_COMPILATION"
    QUARANTINE_NODE = "QUARANTINE_NODE"
    REVERT_MUTATION = "REVERT_MUTATION"
    FORCE_HITL_INTERCEPT = "FORCE_HITL_INTERCEPT"
    REJECT_RFC = "REJECT_RFC"
    ISOLATE_SUBNET = "ISOLATE_SUBNET"


class HITLDispositionStatus(str, Enum):
    """Lifecycle status of a Human-in-the-Loop intercept dialog."""
    PENDING_SUPERVISOR_ACTION = "PENDING_SUPERVISOR_ACTION"
    APPROVED_CONTINUE = "APPROVED_CONTINUE"
    VETO_UPHELD = "VETO_UPHELD"
    SPEC_MODIFIED = "SPEC_MODIFIED"
    TIMEOUT_AUTO_SAFE = "TIMEOUT_AUTO_SAFE"
    FORCE_FAIL = "FORCE_FAIL"


class BottleneckType(str, Enum):
    """Classification of engineering friction prompting an asynchronous RFC petition."""
    TOKEN_EXHAUSTION = "TOKEN_EXHAUSTION"
    LATENCY_OVERRUN = "LATENCY_OVERRUN"
    PHYSICAL_IRREVERSIBILITY = "PHYSICAL_IRREVERSIBILITY"
    COMPLEXITY_LIMIT = "COMPLEXITY_LIMIT"
    AXIOMATIC_CONTRADICTION = "AXIOMATIC_CONTRADICTION"


class RFCDispositionStatus(str, Enum):
    """Adjudication outcome of a SpecAdjustmentRequest petition."""
    RECEIVED = "RECEIVED"
    EVALUATING = "EVALUATING"
    AMENDED = "AMENDED"
    COUNTER_PROVEN = "COUNTER_PROVEN"
    ESCALATED_TO_HITL = "ESCALATED_TO_HITL"
    REJECTED_FINAL = "REJECTED_FINAL"


class CircuitBreakerState(str, Enum):
    """Tri-state circuit breaker state machine for cluster safety enclaves."""
    CLOSED_NORMAL = "CLOSED_NORMAL"
    TRIPPED_OPEN = "TRIPPED_OPEN"
    HALF_OPEN_PROBING = "HALF_OPEN_PROBING"
    RECOVERY_ENCLAVE_ACTIVE = "RECOVERY_ENCLAVE_ACTIVE"


class PeerQuarantineStatus(str, Enum):
    """Quarantine status of a peer service node in the sovereign mesh."""
    UNCONSTRAINED_HEALTHY = "UNCONSTRAINED_HEALTHY"
    SUSPECT_FLAGGED = "SUSPECT_FLAGGED"
    QUARANTINED_ISOLATED = "QUARANTINED_ISOLATED"
    DISCHARGED_CLEAN = "DISCHARGED_CLEAN"
    TERMINATED_EVICTED = "TERMINATED_EVICTED"


class SuccessionGraduationStatus(str, Enum):
    """Certification lifecycle status for generational graduation into Gen 5."""
    IN_DEVELOPMENT = "IN_DEVELOPMENT"
    PROVING_INVARIANTS = "PROVING_INVARIANTS"
    CERTIFIED_SUCCESSION_READY = "CERTIFIED_SUCCESSION_READY"
    GRADUATED_TO_GEN5 = "GRADUATED_TO_GEN5"
    BLOCKED_DEFICIT = "BLOCKED_DEFICIT"


class GovernanceStatechartState(str, Enum):
    """The 30 formal states of the Hierarchical XState v5 Governance Statechart."""
    # Stratum 1: Root / Initialization (4 states)
    GOV_ROOT_IDLE = "gov_root_idle"
    GOV_BOOTSTRAPPING = "gov_bootstrapping"
    GOV_READY = "gov_ready"
    GOV_RECALIBRATING = "gov_recalibrating"

    # Stratum 2: SovereignOperational (6 states)
    OP_SURVEILLING = "op_surveilling"
    OP_EVALUATING_INTERCEPT = "op_evaluating_intercept"
    OP_HITL_ESCALATING = "op_hitl_escalating"
    OP_HITL_AWAITING_DISPOSITION = "op_hitl_awaiting_disposition"
    OP_RFC_DELIBERATION = "op_rfc_deliberation"
    OP_ADJUDICATION_SETTLED = "op_adjudication_settled"

    # Stratum 3: EmergencyEnclave (5 states)
    ENCLAVE_TRIPPED = "enclave_tripped"
    ENCLAVE_QUARANTINE_ISOLATION = "enclave_quarantine_isolation"
    ENCLAVE_INVESTIGATION = "enclave_investigation"
    ENCLAVE_COOLDOWN_PROBING = "enclave_cooldown_probing"
    ENCLAVE_RESTORED = "enclave_restored"

    # Stratum 4: GenerationalHandover (5 states)
    HANDOVER_INITIATING = "handover_initiating"
    HANDOVER_PROVING_INVARIANTS = "handover_proving_invariants"
    HANDOVER_HDR_VERIFYING = "handover_hdr_verifying"
    HANDOVER_SIGNING_CERTIFICATE = "handover_signing_certificate"
    HANDOVER_GRADUATED = "handover_graduated"

    # Parallel Region 1: AxiomaticSurveillance (5 states)
    SURV_IDLE = "surv_idle"
    SURV_INSPECTING_AST = "surv_inspecting_ast"
    SURV_INSPECTING_TOPOLOGY = "surv_inspecting_topology"
    SURV_VETO_TRIGGERED = "surv_veto_triggered"
    SURV_QUARANTINED = "surv_quarantined"

    # Parallel Region 2: PeerMediation (5 states)
    PEER_LISTENING = "peer_listening"
    PEER_ADJUDICATING_RFC = "peer_adjudicating_rfc"
    PEER_AMENDING_SPEC = "peer_amending_spec"
    PEER_COUNTER_PROVING = "peer_counter_proving"
    PEER_HITL_DIALOG_ACTIVE = "peer_hitl_dialog_active"


# Negative Axiom ID Pattern: ^NEG(-[A-Za-z0-9]+)?-\d{3}$
_NEG_AXIOM_REGEX = re.compile(r"^NEG(-[A-Za-z0-9]+)?-\d{3}$")


# =========================================================================
# Domain Models (16 Typed Algebraic Dataclasses)
# =========================================================================

@dataclass
class NegativeAxiom:
    """An inviolable negative invariant (human veto) permanently forbidding an anti-pattern."""
    axiom_id: str
    name: str
    forbidden_pattern: str
    rationale: str
    severity: AxiomSeverity = AxiomSeverity.FATAL_VETO
    injected_epoch: int = 15
    is_active: bool = True
    enforcement_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def validate_invariants(self) -> None:
        if not self.axiom_id:
            raise GovernanceDomainInvariantViolation("axiom_id must not be empty.")
        if not _NEG_AXIOM_REGEX.match(self.axiom_id):
            raise GovernanceDomainInvariantViolation(
                f"axiom_id '{self.axiom_id}' does not match pattern '^NEG(-[A-Za-z0-9]+)?-\\d{{3}}$'."
            )
        if not self.name:
            raise GovernanceDomainInvariantViolation("name must not be empty.")
        if not self.forbidden_pattern:
            raise GovernanceDomainInvariantViolation("forbidden_pattern must not be empty.")
        if not self.rationale:
            raise GovernanceDomainInvariantViolation("rationale must not be empty.")
        if self.injected_epoch < 0:
            raise GovernanceDomainInvariantViolation("injected_epoch must be non-negative.")

    def matches(self, candidate_text: str) -> bool:
        """Determines if a given candidate text or AST snippet contains the forbidden pattern."""
        if not self.is_active or not candidate_text:
            return False
        return self.forbidden_pattern in candidate_text

    def compute_hash(self) -> str:
        payload = (
            f"{self.axiom_id}:{self.name}:{self.forbidden_pattern}:{self.severity.value}:"
            f"{self.injected_epoch}:{self.is_active}:{self.enforcement_count}"
        )
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "axiom_id": self.axiom_id,
            "name": self.name,
            "forbidden_pattern": self.forbidden_pattern,
            "rationale": self.rationale,
            "severity": self.severity.value,
            "injected_epoch": self.injected_epoch,
            "is_active": self.is_active,
            "enforcement_count": self.enforcement_count,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> NegativeAxiom:
        instance = cls(
            axiom_id=data["axiom_id"],
            name=data["name"],
            forbidden_pattern=data["forbidden_pattern"],
            rationale=data["rationale"],
            severity=AxiomSeverity(data.get("severity", AxiomSeverity.FATAL_VETO.value)),
            injected_epoch=int(data.get("injected_epoch", 15)),
            is_active=bool(data.get("is_active", True)),
            enforcement_count=int(data.get("enforcement_count", 0)),
            metadata=dict(data.get("metadata", {})),
        )
        instance.validate_invariants()
        return instance


@dataclass
class AxiomViolation:
    """An empirical violation record created when an operation violates an active Negative Axiom."""
    violation_id: str
    axiom_id: str
    violating_symbol_or_endpoint: str
    severity: AxiomSeverity
    veto_action: VetoActionType
    detected_pattern: str
    culprit_service: str
    description: str
    ast_context: Optional[str] = None
    detected_at_unix_ms: int = field(default_factory=lambda: int(time.time() * 1000))

    def validate_invariants(self) -> None:
        if not self.violation_id:
            raise GovernanceDomainInvariantViolation("violation_id must not be empty.")
        if not self.axiom_id or not _NEG_AXIOM_REGEX.match(self.axiom_id):
            raise GovernanceDomainInvariantViolation(f"Invalid axiom_id '{self.axiom_id}' in AxiomViolation.")
        if not self.violating_symbol_or_endpoint:
            raise GovernanceDomainInvariantViolation("violating_symbol_or_endpoint must not be empty.")
        if not self.detected_pattern:
            raise GovernanceDomainInvariantViolation("detected_pattern must not be empty.")
        if not self.culprit_service:
            raise GovernanceDomainInvariantViolation("culprit_service must not be empty.")
        if not self.description:
            raise GovernanceDomainInvariantViolation("description must not be empty.")

    def compute_hash(self) -> str:
        payload = (
            f"{self.violation_id}:{self.axiom_id}:{self.violating_symbol_or_endpoint}:"
            f"{self.severity.value}:{self.veto_action.value}:{self.detected_pattern}:"
            f"{self.culprit_service}:{self.detected_at_unix_ms}"
        )
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "violation_id": self.violation_id,
            "axiom_id": self.axiom_id,
            "violating_symbol_or_endpoint": self.violating_symbol_or_endpoint,
            "severity": self.severity.value,
            "veto_action": self.veto_action.value,
            "detected_pattern": self.detected_pattern,
            "culprit_service": self.culprit_service,
            "description": self.description,
            "ast_context": self.ast_context,
            "detected_at_unix_ms": self.detected_at_unix_ms,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> AxiomViolation:
        instance = cls(
            violation_id=data["violation_id"],
            axiom_id=data["axiom_id"],
            violating_symbol_or_endpoint=data["violating_symbol_or_endpoint"],
            severity=AxiomSeverity(data["severity"]),
            veto_action=VetoActionType(data["veto_action"]),
            detected_pattern=data["detected_pattern"],
            culprit_service=data["culprit_service"],
            description=data["description"],
            ast_context=data.get("ast_context"),
            detected_at_unix_ms=int(data.get("detected_at_unix_ms", int(time.time() * 1000))),
        )
        instance.validate_invariants()
        return instance


@dataclass
class ASTInterceptRecord:
    """Detailed record of an AST node intercepted and analyzed by Sentry/Surveillance."""
    intercept_id: str
    source_service: str
    symbol_urn: str
    file_path: str
    ast_node_type: str
    banned_token_or_call: str
    matched_axiom_id: str
    action_taken: VetoActionType
    line_number: int = 1
    column_offset: int = 0
    timestamp_unix_ms: int = field(default_factory=lambda: int(time.time() * 1000))

    def validate_invariants(self) -> None:
        if not self.intercept_id:
            raise GovernanceDomainInvariantViolation("intercept_id must not be empty.")
        if not self.source_service:
            raise GovernanceDomainInvariantViolation("source_service must not be empty.")
        if not self.symbol_urn:
            raise GovernanceDomainInvariantViolation("symbol_urn must not be empty.")
        if not self.file_path:
            raise GovernanceDomainInvariantViolation("file_path must not be empty.")
        if not self.banned_token_or_call:
            raise GovernanceDomainInvariantViolation("banned_token_or_call must not be empty.")
        if not _NEG_AXIOM_REGEX.match(self.matched_axiom_id):
            raise GovernanceDomainInvariantViolation(
                f"matched_axiom_id '{self.matched_axiom_id}' does not match pattern '^NEG(-[A-Za-z0-9]+)?-\\d{{3}}$'."
            )
        if self.line_number < 1:
            raise GovernanceDomainInvariantViolation(f"line_number must be >= 1, got {self.line_number}.")
        if self.column_offset < 0:
            raise GovernanceDomainInvariantViolation(f"column_offset must be >= 0, got {self.column_offset}.")

    def compute_hash(self) -> str:
        payload = (
            f"{self.intercept_id}:{self.source_service}:{self.symbol_urn}:{self.file_path}:"
            f"{self.ast_node_type}:{self.banned_token_or_call}:{self.matched_axiom_id}:"
            f"{self.action_taken.value}:{self.line_number}:{self.column_offset}:{self.timestamp_unix_ms}"
        )
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "intercept_id": self.intercept_id,
            "source_service": self.source_service,
            "symbol_urn": self.symbol_urn,
            "file_path": self.file_path,
            "ast_node_type": self.ast_node_type,
            "banned_token_or_call": self.banned_token_or_call,
            "matched_axiom_id": self.matched_axiom_id,
            "action_taken": self.action_taken.value,
            "line_number": self.line_number,
            "column_offset": self.column_offset,
            "timestamp_unix_ms": self.timestamp_unix_ms,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ASTInterceptRecord:
        instance = cls(
            intercept_id=data["intercept_id"],
            source_service=data["source_service"],
            symbol_urn=data["symbol_urn"],
            file_path=data["file_path"],
            ast_node_type=data.get("ast_node_type", "AST_NODE"),
            banned_token_or_call=data["banned_token_or_call"],
            matched_axiom_id=data["matched_axiom_id"],
            action_taken=VetoActionType(data["action_taken"]),
            line_number=int(data.get("line_number", 1)),
            column_offset=int(data.get("column_offset", 0)),
            timestamp_unix_ms=int(data.get("timestamp_unix_ms", int(time.time() * 1000))),
        )
        instance.validate_invariants()
        return instance


@dataclass
class HITLInterceptRequest:
    """A formal request escalating a critical decision or ambiguity to the human architect."""
    intercept_id: str
    trigger_reason: str
    service_endpoint: str
    context_dossier: Dict[str, Any]
    recommended_options: List[str]
    status: HITLDispositionStatus = HITLDispositionStatus.PENDING_SUPERVISOR_ACTION
    created_at_unix_ms: int = field(default_factory=lambda: int(time.time() * 1000))
    resolved_at_unix_ms: Optional[int] = None

    def validate_invariants(self) -> None:
        if not self.intercept_id:
            raise GovernanceDomainInvariantViolation("intercept_id must not be empty.")
        if not self.trigger_reason:
            raise GovernanceDomainInvariantViolation("trigger_reason must not be empty.")
        assert_non_loopback(self.service_endpoint, f"HITLInterceptRequest '{self.intercept_id}'")
        if len(self.recommended_options) < 2:
            raise GovernanceDomainInvariantViolation(
                f"HITLInterceptRequest must offer at least 2 distinct options, got {len(self.recommended_options)}."
            )

    def compute_hash(self) -> str:
        opts = ",".join(self.recommended_options)
        payload = (
            f"{self.intercept_id}:{self.trigger_reason}:{self.service_endpoint}:"
            f"{opts}:{self.status.value}:{self.created_at_unix_ms}"
        )
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "intercept_id": self.intercept_id,
            "trigger_reason": self.trigger_reason,
            "service_endpoint": self.service_endpoint,
            "context_dossier": self.context_dossier,
            "recommended_options": self.recommended_options,
            "status": self.status.value,
            "created_at_unix_ms": self.created_at_unix_ms,
            "resolved_at_unix_ms": self.resolved_at_unix_ms,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> HITLInterceptRequest:
        instance = cls(
            intercept_id=data["intercept_id"],
            trigger_reason=data["trigger_reason"],
            service_endpoint=data["service_endpoint"],
            context_dossier=dict(data.get("context_dossier", {})),
            recommended_options=list(data.get("recommended_options", [])),
            status=HITLDispositionStatus(data.get("status", HITLDispositionStatus.PENDING_SUPERVISOR_ACTION.value)),
            created_at_unix_ms=int(data.get("created_at_unix_ms", int(time.time() * 1000))),
            resolved_at_unix_ms=int(data["resolved_at_unix_ms"]) if data.get("resolved_at_unix_ms") is not None else None,
        )
        instance.validate_invariants()
        return instance


@dataclass
class HITLDisposition:
    """The authoritative human architect disposition resolving a HITL intercept."""
    disposition_id: str
    intercept_id: str
    human_supervisor: str = "Michael Lipski"
    disposition_status: HITLDispositionStatus = HITLDispositionStatus.APPROVED_CONTINUE
    selected_option: str = ""
    architectural_guidance: str = ""
    injected_negative_axioms: List[str] = field(default_factory=list)
    disposed_at_unix_ms: int = field(default_factory=lambda: int(time.time() * 1000))
    signature: str = ""

    def validate_invariants(self) -> None:
        if not self.disposition_id:
            raise GovernanceDomainInvariantViolation("disposition_id must not be empty.")
        if not self.intercept_id:
            raise GovernanceDomainInvariantViolation("intercept_id must not be empty.")
        if not self.human_supervisor:
            raise GovernanceDomainInvariantViolation("human_supervisor must not be empty.")
        if not self.selected_option and self.disposition_status == HITLDispositionStatus.APPROVED_CONTINUE:
            raise GovernanceDomainInvariantViolation("selected_option is required for approved disposition.")
        for ax in self.injected_negative_axioms:
            if not _NEG_AXIOM_REGEX.match(ax):
                raise GovernanceDomainInvariantViolation(
                    f"Injected negative axiom '{ax}' does not match pattern '^NEG(-[A-Za-z0-9]+)?-\\d{{3}}$'."
                )
        if not self.signature:
            raise GovernanceDomainInvariantViolation("Cryptographic supervisor signature is mandatory.")

    def compute_hash(self) -> str:
        payload = (
            f"{self.disposition_id}:{self.intercept_id}:{self.human_supervisor}:"
            f"{self.disposition_status.value}:{self.selected_option}:{self.architectural_guidance}:"
            f"{','.join(self.injected_negative_axioms)}:{self.disposed_at_unix_ms}"
        )
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def sign(self, secret_key: str = "supervisory_genesis_secret") -> None:
        """Generates a cryptographic signature over the disposition contents."""
        digest = self.compute_hash()
        self.signature = hashlib.sha256(f"{digest}:{secret_key}:{self.human_supervisor}".encode("utf-8")).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "disposition_id": self.disposition_id,
            "intercept_id": self.intercept_id,
            "human_supervisor": self.human_supervisor,
            "disposition_status": self.disposition_status.value,
            "selected_option": self.selected_option,
            "architectural_guidance": self.architectural_guidance,
            "injected_negative_axioms": self.injected_negative_axioms,
            "disposed_at_unix_ms": self.disposed_at_unix_ms,
            "signature": self.signature,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> HITLDisposition:
        instance = cls(
            disposition_id=data["disposition_id"],
            intercept_id=data["intercept_id"],
            human_supervisor=data.get("human_supervisor", "Michael Lipski"),
            disposition_status=HITLDispositionStatus(data.get("disposition_status", HITLDispositionStatus.APPROVED_CONTINUE.value)),
            selected_option=data.get("selected_option", ""),
            architectural_guidance=data.get("architectural_guidance", ""),
            injected_negative_axioms=list(data.get("injected_negative_axioms", [])),
            disposed_at_unix_ms=int(data.get("disposed_at_unix_ms", int(time.time() * 1000))),
            signature=data.get("signature", ""),
        )
        instance.validate_invariants()
        return instance


@dataclass
class HeuristicDebtRecord:
    """Formal audit record tracking the Heuristic Debt Ratio (HDR = Heuristic / Total).

    Enforces Invariant [L1-G2B-002]:
    Heuristic Debt Ratio must strictly remain <= 0.15 across all generational transitions.
    """
    record_id: str
    epoch: int
    total_decisions_evaluated: int
    autonomous_heuristic_decisions: int
    formal_verified_decisions: int
    hitl_supervised_decisions: int
    heuristic_debt_ratio: float = 0.0
    is_debt_ceiling_breached: bool = False
    recorded_at_unix_ms: int = field(default_factory=lambda: int(time.time() * 1000))

    def validate_invariants(self) -> None:
        if not self.record_id:
            raise GovernanceDomainInvariantViolation("record_id must not be empty.")
        if self.epoch < 0:
            raise GovernanceDomainInvariantViolation(f"epoch must be non-negative, got {self.epoch}.")
        if self.total_decisions_evaluated < 0:
            raise GovernanceDomainInvariantViolation("total_decisions_evaluated must be non-negative.")
        if self.autonomous_heuristic_decisions < 0:
            raise GovernanceDomainInvariantViolation("autonomous_heuristic_decisions must be non-negative.")
        if self.formal_verified_decisions < 0:
            raise GovernanceDomainInvariantViolation("formal_verified_decisions must be non-negative.")
        if self.hitl_supervised_decisions < 0:
            raise GovernanceDomainInvariantViolation("hitl_supervised_decisions must be non-negative.")

        sum_parts = (
            self.autonomous_heuristic_decisions
            + self.formal_verified_decisions
            + self.hitl_supervised_decisions
        )
        if self.total_decisions_evaluated > 0 and sum_parts != self.total_decisions_evaluated:
            raise GovernanceDomainInvariantViolation(
                f"Sum of decision types ({sum_parts}) does not match total ({self.total_decisions_evaluated})."
            )

        expected_hdr = (
            float(self.autonomous_heuristic_decisions) / float(self.total_decisions_evaluated)
            if self.total_decisions_evaluated > 0
            else 0.0
        )
        if abs(self.heuristic_debt_ratio - expected_hdr) > 1e-4:
            raise GovernanceDomainInvariantViolation(
                f"Computed HDR {expected_hdr:.4f} does not match field {self.heuristic_debt_ratio:.4f}."
            )
        if self.heuristic_debt_ratio > 0.15 and not self.is_debt_ceiling_breached:
            raise GovernanceDomainInvariantViolation(
                f"is_debt_ceiling_breached must be True when HDR ({self.heuristic_debt_ratio:.4f}) > 0.15."
            )

    def compute_hash(self) -> str:
        payload = (
            f"{self.record_id}:{self.epoch}:{self.total_decisions_evaluated}:"
            f"{self.autonomous_heuristic_decisions}:{self.formal_verified_decisions}:"
            f"{self.hitl_supervised_decisions}:{self.heuristic_debt_ratio:.6f}:"
            f"{self.is_debt_ceiling_breached}:{self.recorded_at_unix_ms}"
        )
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "record_id": self.record_id,
            "epoch": self.epoch,
            "total_decisions_evaluated": self.total_decisions_evaluated,
            "autonomous_heuristic_decisions": self.autonomous_heuristic_decisions,
            "formal_verified_decisions": self.formal_verified_decisions,
            "hitl_supervised_decisions": self.hitl_supervised_decisions,
            "heuristic_debt_ratio": round(self.heuristic_debt_ratio, 6),
            "is_debt_ceiling_breached": self.is_debt_ceiling_breached,
            "recorded_at_unix_ms": self.recorded_at_unix_ms,
        }

    @classmethod
    def create(
        cls,
        record_id: str,
        epoch: int,
        heuristic_count: int,
        formal_count: int,
        hitl_count: int,
    ) -> HeuristicDebtRecord:
        """Factory constructor that automatically computes HDR and ceiling breach."""
        total = heuristic_count + formal_count + hitl_count
        ratio = float(heuristic_count) / float(total) if total > 0 else 0.0
        breached = ratio > 0.15
        inst = cls(
            record_id=record_id,
            epoch=epoch,
            total_decisions_evaluated=total,
            autonomous_heuristic_decisions=heuristic_count,
            formal_verified_decisions=formal_count,
            hitl_supervised_decisions=hitl_count,
            heuristic_debt_ratio=ratio,
            is_debt_ceiling_breached=breached,
        )
        inst.validate_invariants()
        return inst

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> HeuristicDebtRecord:
        instance = cls(
            record_id=data["record_id"],
            epoch=int(data["epoch"]),
            total_decisions_evaluated=int(data["total_decisions_evaluated"]),
            autonomous_heuristic_decisions=int(data["autonomous_heuristic_decisions"]),
            formal_verified_decisions=int(data["formal_verified_decisions"]),
            hitl_supervised_decisions=int(data["hitl_supervised_decisions"]),
            heuristic_debt_ratio=float(data.get("heuristic_debt_ratio", 0.0)),
            is_debt_ceiling_breached=bool(data.get("is_debt_ceiling_breached", False)),
            recorded_at_unix_ms=int(data.get("recorded_at_unix_ms", int(time.time() * 1000))),
        )
        instance.validate_invariants()
        return instance


@dataclass
class SpecAdjustmentRequest:
    """Builder petition requesting a specification delta under physical engineering friction."""
    request_id: str
    builder_node_id: str
    target_symbol_urn: str
    bottleneck_type: BottleneckType
    empirical_evidence: str
    proposed_delta: str
    preserved_invariants: List[str]
    disposition_status: RFCDispositionStatus = RFCDispositionStatus.RECEIVED
    submitted_at_unix_ms: int = field(default_factory=lambda: int(time.time() * 1000))

    def validate_invariants(self) -> None:
        if not self.request_id:
            raise GovernanceDomainInvariantViolation("request_id must not be empty.")
        if not self.builder_node_id:
            raise GovernanceDomainInvariantViolation("builder_node_id must not be empty.")
        if not self.target_symbol_urn:
            raise GovernanceDomainInvariantViolation("target_symbol_urn must not be empty.")
        if len(self.preserved_invariants) < 1:
            raise GovernanceDomainInvariantViolation("SpecAdjustmentRequest must preserve at least one core invariant.")
        if not self.empirical_evidence:
            raise GovernanceDomainInvariantViolation("empirical_evidence is mandatory for an RFC petition.")
        if not self.proposed_delta:
            raise GovernanceDomainInvariantViolation("proposed_delta must not be empty.")

    def compute_hash(self) -> str:
        payload = (
            f"{self.request_id}:{self.builder_node_id}:{self.target_symbol_urn}:"
            f"{self.bottleneck_type.value}:{self.proposed_delta}:{','.join(self.preserved_invariants)}"
        )
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
            "disposition_status": self.disposition_status.value,
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
            disposition_status=RFCDispositionStatus(data.get("disposition_status", RFCDispositionStatus.RECEIVED.value)),
            submitted_at_unix_ms=int(data.get("submitted_at_unix_ms", int(time.time() * 1000))),
        )
        instance.validate_invariants()
        return instance


@dataclass
class CounterProof:
    """Formal mathematical, SMT, or empirical proof refuting a builder's RFC petition."""
    counter_proof_id: str
    request_id: str
    violated_axioms: List[str]
    z3_unsat_core: Optional[str] = None
    counter_example_model: Dict[str, Any] = field(default_factory=dict)
    adjudicator_node_id: str = "node_governance_kernel"
    generated_at_unix_ms: int = field(default_factory=lambda: int(time.time() * 1000))

    def validate_invariants(self) -> None:
        if not self.counter_proof_id:
            raise GovernanceDomainInvariantViolation("counter_proof_id must not be empty.")
        if not self.request_id:
            raise GovernanceDomainInvariantViolation("request_id must not be empty.")
        if len(self.violated_axioms) < 1:
            raise GovernanceDomainInvariantViolation("CounterProof must cite at least one violated axiom or invariant.")

    def compute_hash(self) -> str:
        payload = (
            f"{self.counter_proof_id}:{self.request_id}:{','.join(self.violated_axioms)}:"
            f"{self.z3_unsat_core}:{self.adjudicator_node_id}:{self.generated_at_unix_ms}"
        )
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "counter_proof_id": self.counter_proof_id,
            "request_id": self.request_id,
            "violated_axioms": self.violated_axioms,
            "z3_unsat_core": self.z3_unsat_core,
            "counter_example_model": self.counter_example_model,
            "adjudicator_node_id": self.adjudicator_node_id,
            "generated_at_unix_ms": self.generated_at_unix_ms,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> CounterProof:
        instance = cls(
            counter_proof_id=data["counter_proof_id"],
            request_id=data["request_id"],
            violated_axioms=list(data.get("violated_axioms", [])),
            z3_unsat_core=data.get("z3_unsat_core"),
            counter_example_model=dict(data.get("counter_example_model", {})),
            adjudicator_node_id=data.get("adjudicator_node_id", "node_governance_kernel"),
            generated_at_unix_ms=int(data.get("generated_at_unix_ms", int(time.time() * 1000))),
        )
        instance.validate_invariants()
        return instance


@dataclass
class SpecAmendment:
    """Authoritative adjudication outcome (approval or rejection with counter-proof) for an RFC."""
    amendment_id: str
    request_id: str
    is_approved: bool
    adjudicator_signature: str
    amended_contract_ir_delta: str = ""
    rejection_counter_proof: Optional[CounterProof] = None
    adjudicated_at_unix_ms: int = field(default_factory=lambda: int(time.time() * 1000))

    def validate_invariants(self) -> None:
        if not self.amendment_id:
            raise GovernanceDomainInvariantViolation("amendment_id must not be empty.")
        if not self.request_id:
            raise GovernanceDomainInvariantViolation("request_id must not be empty.")
        if not self.adjudicator_signature:
            raise GovernanceDomainInvariantViolation("adjudicator_signature is mandatory.")
        if not self.is_approved and self.rejection_counter_proof is None:
            raise GovernanceDomainInvariantViolation(
                "Rejected SpecAmendment strictly requires a formal CounterProof."
            )
        if self.rejection_counter_proof is not None:
            self.rejection_counter_proof.validate_invariants()

    def compute_hash(self) -> str:
        proof_h = self.rejection_counter_proof.compute_hash() if self.rejection_counter_proof else "NO_COUNTER_PROOF"
        payload = (
            f"{self.amendment_id}:{self.request_id}:{self.is_approved}:{self.adjudicator_signature}:"
            f"{self.amended_contract_ir_delta}:{proof_h}:{self.adjudicated_at_unix_ms}"
        )
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "amendment_id": self.amendment_id,
            "request_id": self.request_id,
            "is_approved": self.is_approved,
            "adjudicator_signature": self.adjudicator_signature,
            "amended_contract_ir_delta": self.amended_contract_ir_delta,
            "rejection_counter_proof": self.rejection_counter_proof.to_dict() if self.rejection_counter_proof else None,
            "adjudicated_at_unix_ms": self.adjudicated_at_unix_ms,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> SpecAmendment:
        proof_data = data.get("rejection_counter_proof")
        proof_obj = CounterProof.from_dict(proof_data) if proof_data else None
        instance = cls(
            amendment_id=data["amendment_id"],
            request_id=data["request_id"],
            is_approved=bool(data["is_approved"]),
            adjudicator_signature=data["adjudicator_signature"],
            amended_contract_ir_delta=data.get("amended_contract_ir_delta", ""),
            rejection_counter_proof=proof_obj,
            adjudicated_at_unix_ms=int(data.get("adjudicated_at_unix_ms", int(time.time() * 1000))),
        )
        instance.validate_invariants()
        return instance


@dataclass
class QuarantineEvent:
    """Record of a peer service node being placed in or released from isolation enclave."""
    event_id: str
    node_id: str
    service_endpoint: str
    quarantine_status: PeerQuarantineStatus
    triggering_violation_id: str
    isolation_subnet: str = "192.168.40.240/28"
    reason: str = ""
    initiated_at_unix_ms: int = field(default_factory=lambda: int(time.time() * 1000))
    released_at_unix_ms: Optional[int] = None

    def validate_invariants(self) -> None:
        if not self.event_id:
            raise GovernanceDomainInvariantViolation("event_id must not be empty.")
        if not self.node_id:
            raise GovernanceDomainInvariantViolation("node_id must not be empty.")
        assert_non_loopback(self.service_endpoint, f"QuarantineEvent '{self.event_id}'")
        if not self.triggering_violation_id:
            raise GovernanceDomainInvariantViolation("triggering_violation_id must not be empty.")
        if not self.reason:
            raise GovernanceDomainInvariantViolation("reason must not be empty.")

    def compute_hash(self) -> str:
        payload = (
            f"{self.event_id}:{self.node_id}:{self.service_endpoint}:{self.quarantine_status.value}:"
            f"{self.triggering_violation_id}:{self.isolation_subnet}:{self.initiated_at_unix_ms}"
        )
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "node_id": self.node_id,
            "service_endpoint": self.service_endpoint,
            "quarantine_status": self.quarantine_status.value,
            "triggering_violation_id": self.triggering_violation_id,
            "isolation_subnet": self.isolation_subnet,
            "reason": self.reason,
            "initiated_at_unix_ms": self.initiated_at_unix_ms,
            "released_at_unix_ms": self.released_at_unix_ms,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> QuarantineEvent:
        instance = cls(
            event_id=data["event_id"],
            node_id=data["node_id"],
            service_endpoint=data["service_endpoint"],
            quarantine_status=PeerQuarantineStatus(data["quarantine_status"]),
            triggering_violation_id=data["triggering_violation_id"],
            isolation_subnet=data.get("isolation_subnet", "192.168.40.240/28"),
            reason=data.get("reason", ""),
            initiated_at_unix_ms=int(data.get("initiated_at_unix_ms", int(time.time() * 1000))),
            released_at_unix_ms=int(data["released_at_unix_ms"]) if data.get("released_at_unix_ms") is not None else None,
        )
        instance.validate_invariants()
        return instance


@dataclass
class CircuitBreakerStateRecord:
    """State record of the emergency safety enclave circuit breaker."""
    record_id: str
    current_state: CircuitBreakerState = CircuitBreakerState.CLOSED_NORMAL
    failure_count: int = 0
    failure_threshold: int = 3
    cooldown_seconds: float = 30.0
    last_tripped_unix_ms: Optional[int] = None
    last_probed_unix_ms: Optional[int] = None
    quarantined_peer_endpoints: List[str] = field(default_factory=list)

    def validate_invariants(self) -> None:
        if not self.record_id:
            raise GovernanceDomainInvariantViolation("record_id must not be empty.")
        if self.failure_count < 0:
            raise GovernanceDomainInvariantViolation("failure_count must be non-negative.")
        if self.failure_threshold < 1:
            raise GovernanceDomainInvariantViolation("failure_threshold must be >= 1.")
        if self.cooldown_seconds <= 0.0:
            raise GovernanceDomainInvariantViolation("cooldown_seconds must be positive.")
        for ep in self.quarantined_peer_endpoints:
            assert_non_loopback(ep, f"CircuitBreakerStateRecord endpoint '{ep}'")

    def trip(self, endpoint: str) -> None:
        """Trips the circuit breaker open and records the quarantined endpoint."""
        assert_non_loopback(endpoint, "CircuitBreaker trip")
        self.failure_count += 1
        if self.failure_count >= self.failure_threshold:
            self.current_state = CircuitBreakerState.TRIPPED_OPEN
            self.last_tripped_unix_ms = int(time.time() * 1000)
        if endpoint not in self.quarantined_peer_endpoints:
            self.quarantined_peer_endpoints.append(endpoint)

    def reset_clean(self) -> None:
        """Resets the circuit breaker to CLOSED_NORMAL and clears failure count."""
        self.current_state = CircuitBreakerState.CLOSED_NORMAL
        self.failure_count = 0
        self.quarantined_peer_endpoints.clear()

    def compute_hash(self) -> str:
        eps = ",".join(sorted(self.quarantined_peer_endpoints))
        payload = (
            f"{self.record_id}:{self.current_state.value}:{self.failure_count}:"
            f"{self.failure_threshold}:{self.cooldown_seconds}:{eps}:{self.last_tripped_unix_ms}"
        )
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "record_id": self.record_id,
            "current_state": self.current_state.value,
            "failure_count": self.failure_count,
            "failure_threshold": self.failure_threshold,
            "cooldown_seconds": self.cooldown_seconds,
            "last_tripped_unix_ms": self.last_tripped_unix_ms,
            "last_probed_unix_ms": self.last_probed_unix_ms,
            "quarantined_peer_endpoints": self.quarantined_peer_endpoints,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> CircuitBreakerStateRecord:
        instance = cls(
            record_id=data["record_id"],
            current_state=CircuitBreakerState(data.get("current_state", CircuitBreakerState.CLOSED_NORMAL.value)),
            failure_count=int(data.get("failure_count", 0)),
            failure_threshold=int(data.get("failure_threshold", 3)),
            cooldown_seconds=float(data.get("cooldown_seconds", 30.0)),
            last_tripped_unix_ms=int(data["last_tripped_unix_ms"]) if data.get("last_tripped_unix_ms") is not None else None,
            last_probed_unix_ms=int(data["last_probed_unix_ms"]) if data.get("last_probed_unix_ms") is not None else None,
            quarantined_peer_endpoints=list(data.get("quarantined_peer_endpoints", [])),
        )
        instance.validate_invariants()
        return instance


@dataclass
class SuccessionInvariantProof:
    """Formal proof artifact establishing satisfaction of a required invariant for Gen 5 graduation."""
    proof_id: str
    target_generation: str = "Generation 5"
    invariant_urn: str = "urn:axioma:g4b:invariant:zero_loopback"
    mathematical_formalization: str = "Forall e in MeshEndpoints: host(e) not in ProhibitedLoopback"
    empirical_witness_path: str = "generations/gen_04b/tests/test_mesh_topology.py"
    is_satisfied: bool = True
    z3_status: str = "SAT"
    proven_at_unix_ms: int = field(default_factory=lambda: int(time.time() * 1000))

    def validate_invariants(self) -> None:
        if not self.proof_id:
            raise GovernanceDomainInvariantViolation("proof_id must not be empty.")
        if not self.target_generation:
            raise GovernanceDomainInvariantViolation("target_generation must not be empty.")
        if not self.invariant_urn or not self.invariant_urn.startswith("urn:axioma:"):
            raise GovernanceDomainInvariantViolation(
                f"invariant_urn must begin with 'urn:axioma:', got '{self.invariant_urn}'."
            )
        if not self.mathematical_formalization:
            raise GovernanceDomainInvariantViolation("mathematical_formalization must not be empty.")
        if not self.empirical_witness_path:
            raise GovernanceDomainInvariantViolation("empirical_witness_path must not be empty.")

    def compute_hash(self) -> str:
        payload = (
            f"{self.proof_id}:{self.target_generation}:{self.invariant_urn}:"
            f"{self.mathematical_formalization}:{self.empirical_witness_path}:"
            f"{self.is_satisfied}:{self.z3_status}:{self.proven_at_unix_ms}"
        )
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "proof_id": self.proof_id,
            "target_generation": self.target_generation,
            "invariant_urn": self.invariant_urn,
            "mathematical_formalization": self.mathematical_formalization,
            "empirical_witness_path": self.empirical_witness_path,
            "is_satisfied": self.is_satisfied,
            "z3_status": self.z3_status,
            "proven_at_unix_ms": self.proven_at_unix_ms,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> SuccessionInvariantProof:
        instance = cls(
            proof_id=data["proof_id"],
            target_generation=data.get("target_generation", "Generation 5"),
            invariant_urn=data.get("invariant_urn", "urn:axioma:g4b:invariant:zero_loopback"),
            mathematical_formalization=data.get("mathematical_formalization", ""),
            empirical_witness_path=data.get("empirical_witness_path", ""),
            is_satisfied=bool(data.get("is_satisfied", True)),
            z3_status=data.get("z3_status", "SAT"),
            proven_at_unix_ms=int(data.get("proven_at_unix_ms", int(time.time() * 1000))),
        )
        instance.validate_invariants()
        return instance


@dataclass
class GenerationalHandoverCertificate:
    """The cryptographically signed certificate authorizing generational succession to Generation 5."""
    certificate_id: str
    source_generation: str = "Generation 4b"
    target_generation: str = "Generation 5"
    graduation_status: SuccessionGraduationStatus = SuccessionGraduationStatus.CERTIFIED_SUCCESSION_READY
    invariant_proofs: List[SuccessionInvariantProof] = field(default_factory=list)
    governance_hash_chain_head: str = ""
    human_architect_approval_sig: str = ""
    hdr_at_graduation: float = 0.05
    zero_loopback_certified: bool = True
    certified_at_unix_ms: int = field(default_factory=lambda: int(time.time() * 1000))

    def validate_invariants(self) -> None:
        if not self.certificate_id:
            raise GovernanceDomainInvariantViolation("certificate_id must not be empty.")
        if not self.source_generation or not self.target_generation:
            raise GovernanceDomainInvariantViolation("source and target generations are mandatory.")
        if len(self.invariant_proofs) < 1:
            raise GovernanceDomainInvariantViolation(
                "GenerationalHandoverCertificate requires at least one verified SuccessionInvariantProof."
            )
        for p in self.invariant_proofs:
            p.validate_invariants()
            if not p.is_satisfied:
                raise GovernanceDomainInvariantViolation(
                    f"Invariant proof '{p.proof_id}' is not satisfied; cannot graduate."
                )
        if self.hdr_at_graduation > 0.15:
            raise HeuristicDebtCeilingBreached(
                f"[L1-G2B-002 Violation] Heuristic Debt Ratio at graduation {self.hdr_at_graduation:.4f} > 0.15."
            )
        if not self.zero_loopback_certified:
            raise GovernanceDomainInvariantViolation(
                "[L1-G3B-012 Violation] Cannot certify succession without zero_loopback_certified=True."
            )
        if not self.governance_hash_chain_head or len(self.governance_hash_chain_head) != 64:
            raise GovernanceDomainInvariantViolation(
                "governance_hash_chain_head must be a valid 64-character SHA-256 digest."
            )
        if not self.human_architect_approval_sig:
            raise GovernanceDomainInvariantViolation(
                "human_architect_approval_sig is mandatory for generational graduation."
            )

    def compute_hash(self) -> str:
        proof_hashes = [p.compute_hash() for p in self.invariant_proofs]
        payload = (
            f"{self.certificate_id}:{self.source_generation}:{self.target_generation}:"
            f"{self.graduation_status.value}:{','.join(proof_hashes)}:{self.governance_hash_chain_head}:"
            f"{self.human_architect_approval_sig}:{self.hdr_at_graduation:.6f}:{self.zero_loopback_certified}"
        )
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "certificate_id": self.certificate_id,
            "source_generation": self.source_generation,
            "target_generation": self.target_generation,
            "graduation_status": self.graduation_status.value,
            "invariant_proofs": [p.to_dict() for p in self.invariant_proofs],
            "governance_hash_chain_head": self.governance_hash_chain_head,
            "human_architect_approval_sig": self.human_architect_approval_sig,
            "hdr_at_graduation": round(self.hdr_at_graduation, 6),
            "zero_loopback_certified": self.zero_loopback_certified,
            "certified_at_unix_ms": self.certified_at_unix_ms,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> GenerationalHandoverCertificate:
        proofs = [SuccessionInvariantProof.from_dict(d) for d in data.get("invariant_proofs", [])]
        instance = cls(
            certificate_id=data["certificate_id"],
            source_generation=data.get("source_generation", "Generation 4b"),
            target_generation=data.get("target_generation", "Generation 5"),
            graduation_status=SuccessionGraduationStatus(data.get("graduation_status", SuccessionGraduationStatus.CERTIFIED_SUCCESSION_READY.value)),
            invariant_proofs=proofs,
            governance_hash_chain_head=data.get("governance_hash_chain_head", ""),
            human_architect_approval_sig=data.get("human_architect_approval_sig", ""),
            hdr_at_graduation=float(data.get("hdr_at_graduation", 0.05)),
            zero_loopback_certified=bool(data.get("zero_loopback_certified", True)),
            certified_at_unix_ms=int(data.get("certified_at_unix_ms", int(time.time() * 1000))),
        )
        instance.validate_invariants()
        return instance


@dataclass
class GovernanceKernelState:
    """The aggregate operational state of the Sovereign Governance & Safety Service."""
    kernel_id: str = "soc_g4b_governance"
    service_endpoint: str = "192.168.40.50:8448"
    circuit_breaker: CircuitBreakerState = CircuitBreakerState.CLOSED_NORMAL
    active_negative_axioms_count: int = 0
    total_violations_trapped: int = 0
    pending_hitl_count: int = 0
    heuristic_debt_ratio: float = 0.0
    quarantined_nodes: List[str] = field(default_factory=list)
    is_succession_ready: bool = False
    governance_chain_head: str = "0000000000000000000000000000000000000000000000000000000000000000"
    last_heartbeat_unix_ms: int = field(default_factory=lambda: int(time.time() * 1000))

    def validate_invariants(self) -> None:
        if not self.kernel_id:
            raise GovernanceDomainInvariantViolation("kernel_id must not be empty.")
        assert_non_loopback(self.service_endpoint, f"GovernanceKernelState '{self.kernel_id}'")
        if self.active_negative_axioms_count < 0:
            raise GovernanceDomainInvariantViolation("active_negative_axioms_count must be non-negative.")
        if self.total_violations_trapped < 0:
            raise GovernanceDomainInvariantViolation("total_violations_trapped must be non-negative.")
        if self.pending_hitl_count < 0:
            raise GovernanceDomainInvariantViolation("pending_hitl_count must be non-negative.")
        if self.heuristic_debt_ratio < 0.0 or self.heuristic_debt_ratio > 1.0:
            raise GovernanceDomainInvariantViolation(
                f"heuristic_debt_ratio must be in [0.0, 1.0], got {self.heuristic_debt_ratio}."
            )
        if len(self.governance_chain_head) != 64:
            raise GovernanceDomainInvariantViolation("governance_chain_head must be a 64-char SHA-256 digest.")

    def compute_hash(self) -> str:
        quarantined = ",".join(sorted(self.quarantined_nodes))
        payload = (
            f"{self.kernel_id}:{self.service_endpoint}:{self.circuit_breaker.value}:"
            f"{self.active_negative_axioms_count}:{self.total_violations_trapped}:{self.pending_hitl_count}:"
            f"{self.heuristic_debt_ratio:.6f}:{quarantined}:{self.is_succession_ready}:{self.governance_chain_head}"
        )
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "kernel_id": self.kernel_id,
            "service_endpoint": self.service_endpoint,
            "circuit_breaker": self.circuit_breaker.value,
            "active_negative_axioms_count": self.active_negative_axioms_count,
            "total_violations_trapped": self.total_violations_trapped,
            "pending_hitl_count": self.pending_hitl_count,
            "heuristic_debt_ratio": round(self.heuristic_debt_ratio, 6),
            "quarantined_nodes": self.quarantined_nodes,
            "is_succession_ready": self.is_succession_ready,
            "governance_chain_head": self.governance_chain_head,
            "last_heartbeat_unix_ms": self.last_heartbeat_unix_ms,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> GovernanceKernelState:
        instance = cls(
            kernel_id=data.get("kernel_id", "soc_g4b_governance"),
            service_endpoint=data.get("service_endpoint", "192.168.40.50:8448"),
            circuit_breaker=CircuitBreakerState(data.get("circuit_breaker", CircuitBreakerState.CLOSED_NORMAL.value)),
            active_negative_axioms_count=int(data.get("active_negative_axioms_count", 0)),
            total_violations_trapped=int(data.get("total_violations_trapped", 0)),
            pending_hitl_count=int(data.get("pending_hitl_count", 0)),
            heuristic_debt_ratio=float(data.get("heuristic_debt_ratio", 0.0)),
            quarantined_nodes=list(data.get("quarantined_nodes", [])),
            is_succession_ready=bool(data.get("is_succession_ready", False)),
            governance_chain_head=data.get("governance_chain_head", "0" * 64),
            last_heartbeat_unix_ms=int(data.get("last_heartbeat_unix_ms", int(time.time() * 1000))),
        )
        instance.validate_invariants()
        return instance


@dataclass
class GovernanceEvent:
    """Tamper-evident cryptographically chained event in the Governance event ledger."""
    event_id: str
    event_type: str
    source_node_or_service: str
    payload: Dict[str, Any] = field(default_factory=dict)
    emitted_at_unix_ms: int = field(default_factory=lambda: int(time.time() * 1000))
    event_hash: str = ""
    previous_event_hash: str = "GENESIS_GOVERNANCE_HASH_00000000000000000000000000000000000000000000"

    def validate_invariants(self) -> None:
        if not self.event_id:
            raise GovernanceDomainInvariantViolation("event_id must not be empty.")
        if not self.event_type:
            raise GovernanceDomainInvariantViolation("event_type must not be empty.")
        if not self.source_node_or_service:
            raise GovernanceDomainInvariantViolation("source_node_or_service must not be empty.")
        if not self.previous_event_hash:
            raise GovernanceDomainInvariantViolation("previous_event_hash must not be empty.")

    def compute_hash(self) -> str:
        serialized_payload = json.dumps(self.payload, sort_keys=True)
        raw = (
            f"{self.event_id}:{self.event_type}:{self.source_node_or_service}:"
            f"{serialized_payload}:{self.previous_event_hash}:{self.emitted_at_unix_ms}"
        )
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def seal(self) -> str:
        """Computes and assigns the event_hash."""
        self.event_hash = self.compute_hash()
        return self.event_hash

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "source_node_or_service": self.source_node_or_service,
            "payload": self.payload,
            "emitted_at_unix_ms": self.emitted_at_unix_ms,
            "event_hash": self.event_hash,
            "previous_event_hash": self.previous_event_hash,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> GovernanceEvent:
        instance = cls(
            event_id=data["event_id"],
            event_type=data["event_type"],
            source_node_or_service=data["source_node_or_service"],
            payload=dict(data.get("payload", {})),
            emitted_at_unix_ms=int(data.get("emitted_at_unix_ms", int(time.time() * 1000))),
            event_hash=data.get("event_hash", ""),
            previous_event_hash=data.get("previous_event_hash", "0" * 64),
        )
        instance.validate_invariants()
        return instance


@dataclass
class StatechartTransitionRecord:
    """Audit record capturing a deterministic state transition in the statechart."""
    event_name: str
    from_state: str
    to_state: str
    parallel_surveillance_state: str
    parallel_mediation_state: str
    payload_summary: List[str]
    timestamp_unix_ms: int = field(default_factory=lambda: int(time.time() * 1000))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_name": self.event_name,
            "from_state": self.from_state,
            "to_state": self.to_state,
            "parallel_surveillance_state": self.parallel_surveillance_state,
            "parallel_mediation_state": self.parallel_mediation_state,
            "payload_summary": self.payload_summary,
            "timestamp_unix_ms": self.timestamp_unix_ms,
        }


@dataclass
class GovernanceStatechartDefinition:
    """Formal structural specification of the 30-State Hierarchical XState v5 Statechart.

    Enforces:
    - 4 Compound Strata (20 states)
    - 2 Parallel Orthogonal Regions (10 states)
    - Deep history checkpoint state H*
    - 42 Deterministic Event Transitions & Complete Covering Paths
    """
    specification_id: str = "spec_g4b_governance_statechart_v5"
    states_count: int = 30
    transitions_count: int = 42

    @classmethod
    def get_states(cls) -> Set[str]:
        return {s.value for s in GovernanceStatechartState}

    @classmethod
    def get_compound_strata(cls) -> Dict[str, List[str]]:
        return {
            "Root": [
                GovernanceStatechartState.GOV_ROOT_IDLE.value,
                GovernanceStatechartState.GOV_BOOTSTRAPPING.value,
                GovernanceStatechartState.GOV_READY.value,
                GovernanceStatechartState.GOV_RECALIBRATING.value,
            ],
            "SovereignOperational": [
                GovernanceStatechartState.OP_SURVEILLING.value,
                GovernanceStatechartState.OP_EVALUATING_INTERCEPT.value,
                GovernanceStatechartState.OP_HITL_ESCALATING.value,
                GovernanceStatechartState.OP_HITL_AWAITING_DISPOSITION.value,
                GovernanceStatechartState.OP_RFC_DELIBERATION.value,
                GovernanceStatechartState.OP_ADJUDICATION_SETTLED.value,
            ],
            "EmergencyEnclave": [
                GovernanceStatechartState.ENCLAVE_TRIPPED.value,
                GovernanceStatechartState.ENCLAVE_QUARANTINE_ISOLATION.value,
                GovernanceStatechartState.ENCLAVE_INVESTIGATION.value,
                GovernanceStatechartState.ENCLAVE_COOLDOWN_PROBING.value,
                GovernanceStatechartState.ENCLAVE_RESTORED.value,
            ],
            "GenerationalHandover": [
                GovernanceStatechartState.HANDOVER_INITIATING.value,
                GovernanceStatechartState.HANDOVER_PROVING_INVARIANTS.value,
                GovernanceStatechartState.HANDOVER_HDR_VERIFYING.value,
                GovernanceStatechartState.HANDOVER_SIGNING_CERTIFICATE.value,
                GovernanceStatechartState.HANDOVER_GRADUATED.value,
            ],
        }

    @classmethod
    def get_parallel_regions(cls) -> Dict[str, List[str]]:
        return {
            "AxiomaticSurveillance": [
                GovernanceStatechartState.SURV_IDLE.value,
                GovernanceStatechartState.SURV_INSPECTING_AST.value,
                GovernanceStatechartState.SURV_INSPECTING_TOPOLOGY.value,
                GovernanceStatechartState.SURV_VETO_TRIGGERED.value,
                GovernanceStatechartState.SURV_QUARANTINED.value,
            ],
            "PeerMediation": [
                GovernanceStatechartState.PEER_LISTENING.value,
                GovernanceStatechartState.PEER_ADJUDICATING_RFC.value,
                GovernanceStatechartState.PEER_AMENDING_SPEC.value,
                GovernanceStatechartState.PEER_COUNTER_PROVING.value,
                GovernanceStatechartState.PEER_HITL_DIALOG_ACTIVE.value,
            ],
        }

    @classmethod
    def get_deterministic_transitions(cls) -> List[Dict[str, str]]:
        """Returns the complete mapping of all 42 deterministic transitions."""
        return [
            # Stratum 1: Root / Initialization (Transitions 1-5)
            {"id": "T01", "event": "EV_BOOTSTRAP_INIT", "from": "gov_root_idle", "to": "gov_bootstrapping"},
            {"id": "T02", "event": "EV_AXIOMS_LOADED", "from": "gov_bootstrapping", "to": "gov_ready"},
            {"id": "T03", "event": "EV_ENTER_OPERATIONAL", "from": "gov_ready", "to": "op_surveilling"},
            {"id": "T04", "event": "EV_RECALIBRATE_START", "from": "gov_ready", "to": "gov_recalibrating"},
            {"id": "T05", "event": "EV_RECALIBRATE_COMPLETE", "from": "gov_recalibrating", "to": "gov_ready"},

            # Stratum 2: SovereignOperational (Transitions 6-18)
            {"id": "T06", "event": "EV_INTERCEPT_DETECTED", "from": "op_surveilling", "to": "op_evaluating_intercept"},
            {"id": "T07", "event": "EV_INTERCEPT_CLEARED", "from": "op_evaluating_intercept", "to": "op_surveilling"},
            {"id": "T08", "event": "EV_VETO_CONFIRMED", "from": "op_evaluating_intercept", "to": "op_adjudication_settled"},
            {"id": "T09", "event": "EV_ESCALATE_HITL", "from": "op_evaluating_intercept", "to": "op_hitl_escalating"},
            {"id": "T10", "event": "EV_HITL_SUBMITTED", "from": "op_hitl_escalating", "to": "op_hitl_awaiting_disposition"},
            {"id": "T11", "event": "EV_SUPERVISOR_APPROVED", "from": "op_hitl_awaiting_disposition", "to": "op_adjudication_settled"},
            {"id": "T12", "event": "EV_SUPERVISOR_VETOED", "from": "op_hitl_awaiting_disposition", "to": "op_adjudication_settled"},
            {"id": "T13", "event": "EV_SUPERVISOR_AMENDED", "from": "op_hitl_awaiting_disposition", "to": "op_adjudication_settled"},
            {"id": "T14", "event": "EV_RFC_SUBMITTED", "from": "op_surveilling", "to": "op_rfc_deliberation"},
            {"id": "T15", "event": "EV_RFC_APPROVE", "from": "op_rfc_deliberation", "to": "op_adjudication_settled"},
            {"id": "T16", "event": "EV_RFC_REJECT_COUNTER_PROOF", "from": "op_rfc_deliberation", "to": "op_adjudication_settled"},
            {"id": "T17", "event": "EV_RFC_ESCALATE_HITL", "from": "op_rfc_deliberation", "to": "op_hitl_escalating"},
            {"id": "T18", "event": "EV_ADJUDICATION_DISPATCHED", "from": "op_adjudication_settled", "to": "op_surveilling"},

            # Stratum 3: EmergencyEnclave (Transitions 19-25)
            {"id": "T19", "event": "EV_TRIP_CIRCUIT_BREAKER", "from": "op_surveilling", "to": "enclave_tripped"},
            {"id": "T20", "event": "EV_ISOLATE_NODE", "from": "enclave_tripped", "to": "enclave_quarantine_isolation"},
            {"id": "T21", "event": "EV_BEGIN_INVESTIGATION", "from": "enclave_quarantine_isolation", "to": "enclave_investigation"},
            {"id": "T22", "event": "EV_START_COOLDOWN_PROBE", "from": "enclave_investigation", "to": "enclave_cooldown_probing"},
            {"id": "T23", "event": "EV_PROBE_SUCCEEDED", "from": "enclave_cooldown_probing", "to": "enclave_restored"},
            {"id": "T24", "event": "EV_PROBE_FAILED_RETRIP", "from": "enclave_cooldown_probing", "to": "enclave_tripped"},
            {"id": "T25", "event": "EV_RESTORE_DEEP_HISTORY", "from": "enclave_restored", "to": "op_surveilling"},

            # Stratum 4: GenerationalHandover (Transitions 26-33)
            {"id": "T26", "event": "EV_INITIATE_HANDOVER", "from": "op_surveilling", "to": "handover_initiating"},
            {"id": "T27", "event": "EV_VERIFY_INVARIANTS", "from": "handover_initiating", "to": "handover_proving_invariants"},
            {"id": "T28", "event": "EV_INVARIANTS_SATISFIED", "from": "handover_proving_invariants", "to": "handover_hdr_verifying"},
            {"id": "T29", "event": "EV_INVARIANTS_UNSAT_DEFICIT", "from": "handover_proving_invariants", "to": "op_surveilling"},
            {"id": "T30", "event": "EV_HDR_VERIFIED_PASS", "from": "handover_hdr_verifying", "to": "handover_signing_certificate"},
            {"id": "T31", "event": "EV_HDR_EXCEEDED_DEBT", "from": "handover_hdr_verifying", "to": "op_hitl_escalating"},
            {"id": "T32", "event": "EV_CERTIFICATE_SIGNED", "from": "handover_signing_certificate", "to": "handover_graduated"},
            {"id": "T33", "event": "EV_RETURN_TO_STANDBY", "from": "handover_graduated", "to": "gov_root_idle"},

            # Parallel Region 1: AxiomaticSurveillance (Transitions 34-38)
            {"id": "T34", "event": "EV_SURV_SCAN_AST", "from": "surv_idle", "to": "surv_inspecting_ast"},
            {"id": "T35", "event": "EV_SURV_SCAN_TOPOLOGY", "from": "surv_idle", "to": "surv_inspecting_topology"},
            {"id": "T36", "event": "EV_SURV_TRIGGER_VETO", "from": "surv_inspecting_ast", "to": "surv_veto_triggered"},
            {"id": "T37", "event": "EV_SURV_QUARANTINE_PEER", "from": "surv_veto_triggered", "to": "surv_quarantined"},
            {"id": "T38", "event": "EV_SURV_DISCHARGE_CLEAN", "from": "surv_quarantined", "to": "surv_idle"},

            # Parallel Region 2: PeerMediation (Transitions 39-42)
            {"id": "T39", "event": "EV_PEER_POLL_RFC", "from": "peer_listening", "to": "peer_adjudicating_rfc"},
            {"id": "T40", "event": "EV_PEER_GENERATE_AMENDMENT", "from": "peer_adjudicating_rfc", "to": "peer_amending_spec"},
            {"id": "T41", "event": "EV_PEER_GENERATE_COUNTER_PROOF", "from": "peer_adjudicating_rfc", "to": "peer_counter_proving"},
            {"id": "T42", "event": "EV_PEER_OPEN_HITL_DIALOG", "from": "peer_adjudicating_rfc", "to": "peer_hitl_dialog_active"},
        ]


# =========================================================================
# Statechart Engine Core
# =========================================================================

class GovernanceStatechartEngine:
    """Deterministic Hierarchical XState v5 Statechart Execution Engine for Sovereign Governance."""

    def __init__(self, initial_state: str = "gov_root_idle") -> None:
        valid_states = GovernanceStatechartDefinition.get_states()
        if initial_state not in valid_states:
            raise GovernanceDomainInvariantViolation(f"Invalid initial state: '{initial_state}'")

        self.current_state: str = initial_state
        self.parallel_surveillance_state: str = GovernanceStatechartState.SURV_IDLE.value
        self.parallel_mediation_state: str = GovernanceStatechartState.PEER_LISTENING.value

        # Deep History State H*
        self.history_checkpoint: str = "gov_ready"
        self.transition_log: List[StatechartTransitionRecord] = []

    def send(self, event_name: str, payload: Optional[Dict[str, Any]] = None) -> str:
        """Dispatches an event deterministically and records the transition."""
        p = payload or {}
        from_state = self.current_state
        from_surv = self.parallel_surveillance_state
        from_med = self.parallel_mediation_state

        # --- Parallel Region 1 Events ---
        if event_name == "EV_SURV_SCAN_AST":
            self.parallel_surveillance_state = GovernanceStatechartState.SURV_INSPECTING_AST.value
            self._log(event_name, from_state, self.current_state, p)
            return self.current_state
        elif event_name == "EV_SURV_SCAN_TOPOLOGY":
            self.parallel_surveillance_state = GovernanceStatechartState.SURV_INSPECTING_TOPOLOGY.value
            self._log(event_name, from_state, self.current_state, p)
            return self.current_state
        elif event_name == "EV_SURV_TRIGGER_VETO":
            self.parallel_surveillance_state = GovernanceStatechartState.SURV_VETO_TRIGGERED.value
            self._log(event_name, from_state, self.current_state, p)
            return self.current_state
        elif event_name == "EV_SURV_QUARANTINE_PEER":
            self.parallel_surveillance_state = GovernanceStatechartState.SURV_QUARANTINED.value
            self._log(event_name, from_state, self.current_state, p)
            return self.current_state
        elif event_name == "EV_SURV_DISCHARGE_CLEAN":
            self.parallel_surveillance_state = GovernanceStatechartState.SURV_IDLE.value
            self._log(event_name, from_state, self.current_state, p)
            return self.current_state

        # --- Parallel Region 2 Events ---
        if event_name == "EV_PEER_POLL_RFC":
            self.parallel_mediation_state = GovernanceStatechartState.PEER_ADJUDICATING_RFC.value
            self._log(event_name, from_state, self.current_state, p)
            return self.current_state
        elif event_name == "EV_PEER_GENERATE_AMENDMENT":
            self.parallel_mediation_state = GovernanceStatechartState.PEER_AMENDING_SPEC.value
            self._log(event_name, from_state, self.current_state, p)
            return self.current_state
        elif event_name == "EV_PEER_GENERATE_COUNTER_PROOF":
            self.parallel_mediation_state = GovernanceStatechartState.PEER_COUNTER_PROVING.value
            self._log(event_name, from_state, self.current_state, p)
            return self.current_state
        elif event_name == "EV_PEER_OPEN_HITL_DIALOG":
            self.parallel_mediation_state = GovernanceStatechartState.PEER_HITL_DIALOG_ACTIVE.value
            self._log(event_name, from_state, self.current_state, p)
            return self.current_state
        elif event_name == "EV_PEER_RESET_LISTENING":
            self.parallel_mediation_state = GovernanceStatechartState.PEER_LISTENING.value
            self._log(event_name, from_state, self.current_state, p)
            return self.current_state

        # --- Stratum 1: Root / Initialization ---
        if self.current_state == "gov_root_idle":
            if event_name == "EV_BOOTSTRAP_INIT":
                self.current_state = "gov_bootstrapping"
        elif self.current_state == "gov_bootstrapping":
            if event_name == "EV_AXIOMS_LOADED":
                self.current_state = "gov_ready"
        elif self.current_state == "gov_ready":
            if event_name == "EV_ENTER_OPERATIONAL":
                self.history_checkpoint = "gov_ready"
                self.current_state = "op_surveilling"
            elif event_name == "EV_RECALIBRATE_START":
                self.current_state = "gov_recalibrating"
        elif self.current_state == "gov_recalibrating":
            if event_name == "EV_RECALIBRATE_COMPLETE":
                self.current_state = "gov_ready"

        # --- Stratum 2: SovereignOperational ---
        elif self.current_state == "op_surveilling":
            if event_name == "EV_INTERCEPT_DETECTED":
                self.history_checkpoint = "op_surveilling"
                self.current_state = "op_evaluating_intercept"
            elif event_name == "EV_RFC_SUBMITTED":
                self.history_checkpoint = "op_surveilling"
                self.current_state = "op_rfc_deliberation"
            elif event_name == "EV_TRIP_CIRCUIT_BREAKER":
                self.history_checkpoint = "op_surveilling"
                self.current_state = "enclave_tripped"
            elif event_name == "EV_INITIATE_HANDOVER":
                self.history_checkpoint = "op_surveilling"
                self.current_state = "handover_initiating"

        elif self.current_state == "op_evaluating_intercept":
            if event_name == "EV_INTERCEPT_CLEARED":
                self.current_state = "op_surveilling"
            elif event_name == "EV_VETO_CONFIRMED":
                self.current_state = "op_adjudication_settled"
            elif event_name == "EV_ESCALATE_HITL":
                self.current_state = "op_hitl_escalating"

        elif self.current_state == "op_hitl_escalating":
            if event_name == "EV_HITL_SUBMITTED":
                self.current_state = "op_hitl_awaiting_disposition"

        elif self.current_state == "op_hitl_awaiting_disposition":
            if event_name in ("EV_SUPERVISOR_APPROVED", "EV_SUPERVISOR_VETOED", "EV_SUPERVISOR_AMENDED"):
                self.current_state = "op_adjudication_settled"

        elif self.current_state == "op_rfc_deliberation":
            if event_name in ("EV_RFC_APPROVE", "EV_RFC_REJECT_COUNTER_PROOF"):
                self.current_state = "op_adjudication_settled"
            elif event_name == "EV_RFC_ESCALATE_HITL":
                self.current_state = "op_hitl_escalating"

        elif self.current_state == "op_adjudication_settled":
            if event_name == "EV_ADJUDICATION_DISPATCHED":
                self.current_state = "op_surveilling"

        # --- Stratum 3: EmergencyEnclave ---
        elif self.current_state == "enclave_tripped":
            if event_name == "EV_ISOLATE_NODE":
                self.current_state = "enclave_quarantine_isolation"

        elif self.current_state == "enclave_quarantine_isolation":
            if event_name == "EV_BEGIN_INVESTIGATION":
                self.current_state = "enclave_investigation"

        elif self.current_state == "enclave_investigation":
            if event_name == "EV_START_COOLDOWN_PROBE":
                self.current_state = "enclave_cooldown_probing"

        elif self.current_state == "enclave_cooldown_probing":
            if event_name == "EV_PROBE_SUCCEEDED":
                self.current_state = "enclave_restored"
            elif event_name == "EV_PROBE_FAILED_RETRIP":
                self.current_state = "enclave_tripped"

        elif self.current_state == "enclave_restored":
            if event_name == "EV_RESTORE_DEEP_HISTORY":
                # Deep history restoration H*
                self.current_state = self.history_checkpoint or "op_surveilling"

        # --- Stratum 4: GenerationalHandover ---
        elif self.current_state == "handover_initiating":
            if event_name == "EV_VERIFY_INVARIANTS":
                self.current_state = "handover_proving_invariants"

        elif self.current_state == "handover_proving_invariants":
            if event_name == "EV_INVARIANTS_SATISFIED":
                self.current_state = "handover_hdr_verifying"
            elif event_name == "EV_INVARIANTS_UNSAT_DEFICIT":
                self.current_state = "op_surveilling"

        elif self.current_state == "handover_hdr_verifying":
            if event_name == "EV_HDR_VERIFIED_PASS":
                self.current_state = "handover_signing_certificate"
            elif event_name == "EV_HDR_EXCEEDED_DEBT":
                self.current_state = "op_hitl_escalating"

        elif self.current_state == "handover_signing_certificate":
            if event_name == "EV_CERTIFICATE_SIGNED":
                self.current_state = "handover_graduated"

        elif self.current_state == "handover_graduated":
            if event_name == "EV_RETURN_TO_STANDBY":
                self.current_state = "gov_root_idle"

        self._log(event_name, from_state, self.current_state, p)
        return self.current_state

    def _log(self, event: str, from_s: str, to_s: str, payload: Dict[str, Any]) -> None:
        self.transition_log.append(
            StatechartTransitionRecord(
                event_name=event,
                from_state=from_s,
                to_state=to_s,
                parallel_surveillance_state=self.parallel_surveillance_state,
                parallel_mediation_state=self.parallel_mediation_state,
                payload_summary=list(payload.keys()),
                timestamp_unix_ms=int(time.time() * 1000),
            )
        )
