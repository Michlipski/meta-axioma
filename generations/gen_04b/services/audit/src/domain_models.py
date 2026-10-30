"""Generation 4b Sovereign Audit & Formal Verification Service Domain Models (`soc_g4b_audit`).

Enforces:
- [L1-G4B-001] Service-Oriented Sovereign Mesh Protocol Standardization.
- [L1-G3B-011] Universal Compositional Contract IR & Formal Invariants.
- [L1-G3B-012] Dedicated Non-Loopback Network Topology (Absolute loopback ban).
- [L1-G3B-016] Zero-Trust Micro-Auditor Interception & Verification Attestations.
- Complete algebraic specification of all 5 Enums and 11 Domain Models with validation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
import hashlib
import json
import time
from typing import Any, Dict, List, Optional, Set, Tuple
import uuid


class AuditDomainInvariantViolation(Exception):
    """Raised when an algebraic domain invariant or boundary rule is violated in Audit service."""
    pass


# =========================================================================
# Enumerations (5 Core Enums)
# =========================================================================

class AuditSeverity(str, Enum):
    """Severity classification for audit diagnostics, violations, and sentry alerts."""
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    FATAL = "FATAL"
    SECURITY_BREACH = "SECURITY_BREACH"


class MorphismCheckStatus(str, Enum):
    """Status of category-theoretic contract morphism and statechart verification."""
    PROVEN_VALID = "PROVEN_VALID"
    COUNTER_EXAMPLE_FOUND = "COUNTER_EXAMPLE_FOUND"
    DEADLOCK_DETECTED = "DEADLOCK_DETECTED"
    UNSAT_CORE = "UNSAT_CORE"
    UNKNOWN_SOLVER_ERROR = "UNKNOWN_SOLVER_ERROR"


class FuzzVectorType(str, Enum):
    """Classification of Byzantine chaos vectors injected into enclaves."""
    PARTITION_DROP = "PARTITION_DROP"
    PACKET_CORRUPTION = "PACKET_CORRUPTION"
    MEMORY_PRESSURE = "MEMORY_PRESSURE"
    CONCURRENCY_RACE = "CONCURRENCY_RACE"
    FUZZ_PAYLOAD = "FUZZ_PAYLOAD"
    OUT_OF_ORDER_EVENT = "OUT_OF_ORDER_EVENT"


class QuorumVerdict(str, Enum):
    """Adjudicated verdict from the 3-peer Sheaf-Quorum consensus crucible."""
    UNANIMOUS_PASS = "UNANIMOUS_PASS"
    QUORUM_PASS = "QUORUM_PASS"
    SPLIT_FAIL = "SPLIT_FAIL"
    UNANIMOUS_FAIL = "UNANIMOUS_FAIL"
    REVERTED = "REVERTED"


class AuditVerificationStage(str, Enum):
    """Lifecycle stage of a code leaf undergoing formal verification."""
    INGRESS_STAGING = "INGRESS_STAGING"
    HERMETIC_LINTING = "HERMETIC_LINTING"
    SMT_MODEL_CHECKING = "SMT_MODEL_CHECKING"
    BYZANTINE_FUZZING = "BYZANTINE_FUZZING"
    SHEAF_QUORUM_CONSENSUS = "SHEAF_QUORUM_CONSENSUS"
    MERKLE_ATTESTATION = "MERKLE_ATTESTATION"
    RECOVERY_ENCLAVE = "RECOVERY_ENCLAVE"


# Helper function to check non-loopback endpoints
def assert_non_loopback(endpoint: str, context: str = "") -> None:
    """Verifies that an endpoint does not bind to prohibited loopback addresses."""
    if not endpoint:
        raise AuditDomainInvariantViolation(f"Endpoint must not be empty ({context}).")
    cleaned = endpoint.strip("[]")
    host = cleaned.split(":")[0].strip()
    if host.startswith("127.") or host in ("localhost", "::1", "0.0.0.0") or "::1" in endpoint:
        raise AuditDomainInvariantViolation(
            f"[L1-G3B-012 Violation] Prohibited loopback endpoint '{endpoint}' in {context}."
        )


# =========================================================================
# Domain Models (11 Core Typed Models)
# =========================================================================

@dataclass
class CodeLeafCandidate:
    """A synthesized code leaf submitted by Builder for sovereign adversarial audit."""
    leaf_id: str
    symbol_urn: str
    source_code: str
    ast_node_type: str = "MODULE"
    parent_contract_pre: Optional[str] = None
    parent_contract_post: Optional[str] = None
    child_contract_pre: Optional[str] = None
    child_contract_post: Optional[str] = None
    source_endpoint: str = "192.168.40.20:8443"
    created_at_unix_ms: int = field(default_factory=lambda: int(time.time() * 1000))
    metadata: Dict[str, Any] = field(default_factory=dict)

    def validate_invariants(self) -> None:
        if not self.leaf_id:
            raise AuditDomainInvariantViolation("leaf_id must not be empty.")
        if not self.symbol_urn or not self.symbol_urn.startswith("urn:meta_axioma:"):
            raise AuditDomainInvariantViolation(
                f"symbol_urn must follow 'urn:meta_axioma:*', got '{self.symbol_urn}'."
            )
        if not self.source_code:
            raise AuditDomainInvariantViolation("source_code must not be empty.")
        assert_non_loopback(self.source_endpoint, f"CodeLeafCandidate '{self.leaf_id}'")

    def compute_hash(self) -> str:
        payload = (
            f"{self.leaf_id}:{self.symbol_urn}:{self.ast_node_type}:"
            f"{self.source_endpoint}:{self.source_code}:{self.parent_contract_pre}:"
            f"{self.parent_contract_post}:{self.child_contract_pre}:{self.child_contract_post}"
        )
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "leaf_id": self.leaf_id,
            "symbol_urn": self.symbol_urn,
            "source_code": self.source_code,
            "ast_node_type": self.ast_node_type,
            "parent_contract_pre": self.parent_contract_pre,
            "parent_contract_post": self.parent_contract_post,
            "child_contract_pre": self.child_contract_pre,
            "child_contract_post": self.child_contract_post,
            "source_endpoint": self.source_endpoint,
            "created_at_unix_ms": self.created_at_unix_ms,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> CodeLeafCandidate:
        instance = cls(
            leaf_id=data["leaf_id"],
            symbol_urn=data["symbol_urn"],
            source_code=data["source_code"],
            ast_node_type=data.get("ast_node_type", "MODULE"),
            parent_contract_pre=data.get("parent_contract_pre"),
            parent_contract_post=data.get("parent_contract_post"),
            child_contract_pre=data.get("child_contract_pre"),
            child_contract_post=data.get("child_contract_post"),
            source_endpoint=data.get("source_endpoint", "192.168.40.20:8443"),
            created_at_unix_ms=int(data.get("created_at_unix_ms", int(time.time() * 1000))),
            metadata=dict(data.get("metadata", {})),
        )
        instance.validate_invariants()
        return instance


@dataclass
class HermeticLinterViolation:
    """An empirical violation detected during AST-level hermetic boundary scanning."""
    violation_id: str
    rule_id: str
    severity: AuditSeverity
    line_number: int
    column_offset: int
    description: str
    culprit_token: str

    def validate_invariants(self) -> None:
        if not self.violation_id:
            raise AuditDomainInvariantViolation("violation_id must not be empty.")
        if not self.rule_id:
            raise AuditDomainInvariantViolation("rule_id must not be empty.")
        if self.line_number < 1:
            raise AuditDomainInvariantViolation(f"line_number must be >= 1, got {self.line_number}.")
        if self.column_offset < 0:
            raise AuditDomainInvariantViolation(f"column_offset must be >= 0, got {self.column_offset}.")
        if not self.description:
            raise AuditDomainInvariantViolation("description must not be empty.")

    def compute_hash(self) -> str:
        payload = f"{self.violation_id}:{self.rule_id}:{self.severity.value}:{self.line_number}:{self.column_offset}:{self.culprit_token}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "violation_id": self.violation_id,
            "rule_id": self.rule_id,
            "severity": self.severity.value,
            "line_number": self.line_number,
            "column_offset": self.column_offset,
            "description": self.description,
            "culprit_token": self.culprit_token,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> HermeticLinterViolation:
        instance = cls(
            violation_id=data["violation_id"],
            rule_id=data["rule_id"],
            severity=AuditSeverity(data["severity"]),
            line_number=int(data["line_number"]),
            column_offset=int(data["column_offset"]),
            description=data["description"],
            culprit_token=data["culprit_token"],
        )
        instance.validate_invariants()
        return instance


@dataclass
class HermeticAuditReport:
    """Comprehensive AST and hermetic boundary report emitted by SentrySyntax."""
    report_id: str
    leaf_id: str
    is_hermetic: bool
    violations: List[HermeticLinterViolation] = field(default_factory=list)
    ast_nodes_scanned: int = 0
    banned_constructs_detected: int = 0
    auditor_node_id: str = "node_hermetic_sentry"
    scanned_at_unix_ms: int = field(default_factory=lambda: int(time.time() * 1000))

    def validate_invariants(self) -> None:
        if not self.report_id:
            raise AuditDomainInvariantViolation("report_id must not be empty.")
        if not self.leaf_id:
            raise AuditDomainInvariantViolation("leaf_id must not be empty.")
        if self.is_hermetic and len(self.violations) > 0:
            raise AuditDomainInvariantViolation(
                "HermeticAuditReport cannot be hermetic if violations exist."
            )
        if self.ast_nodes_scanned < 0:
            raise AuditDomainInvariantViolation("ast_nodes_scanned must be non-negative.")

    def compute_hash(self) -> str:
        violation_hashes = [v.compute_hash() for v in self.violations]
        payload = f"{self.report_id}:{self.leaf_id}:{self.is_hermetic}:{','.join(violation_hashes)}:{self.ast_nodes_scanned}:{self.banned_constructs_detected}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "report_id": self.report_id,
            "leaf_id": self.leaf_id,
            "is_hermetic": self.is_hermetic,
            "violations": [v.to_dict() for v in self.violations],
            "ast_nodes_scanned": self.ast_nodes_scanned,
            "banned_constructs_detected": self.banned_constructs_detected,
            "auditor_node_id": self.auditor_node_id,
            "scanned_at_unix_ms": self.scanned_at_unix_ms,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> HermeticAuditReport:
        instance = cls(
            report_id=data["report_id"],
            leaf_id=data["leaf_id"],
            is_hermetic=bool(data["is_hermetic"]),
            violations=[HermeticLinterViolation.from_dict(v) for v in data.get("violations", [])],
            ast_nodes_scanned=int(data.get("ast_nodes_scanned", 0)),
            banned_constructs_detected=int(data.get("banned_constructs_detected", 0)),
            auditor_node_id=data.get("auditor_node_id", "node_hermetic_sentry"),
            scanned_at_unix_ms=int(data.get("scanned_at_unix_ms", int(time.time() * 1000))),
        )
        instance.validate_invariants()
        return instance


@dataclass
class SMTModelCheckResult:
    """Formal verification result emitted by OracleSMT."""
    check_id: str
    leaf_id: str
    morphism_status: MorphismCheckStatus
    precondition_entailment_valid: bool
    postcondition_consequence_valid: bool
    is_deadlock_free: bool
    solver_engine: str = "NativeSMTProver_v4b"
    proof_steps_count: int = 0
    unsat_core: Optional[str] = None
    counter_example: Dict[str, Any] = field(default_factory=dict)
    checked_at_unix_ms: int = field(default_factory=lambda: int(time.time() * 1000))

    def validate_invariants(self) -> None:
        if not self.check_id:
            raise AuditDomainInvariantViolation("check_id must not be empty.")
        if not self.leaf_id:
            raise AuditDomainInvariantViolation("leaf_id must not be empty.")
        if self.morphism_status == MorphismCheckStatus.PROVEN_VALID:
            if not (self.precondition_entailment_valid and self.postcondition_consequence_valid and self.is_deadlock_free):
                raise AuditDomainInvariantViolation(
                    "PROVEN_VALID strictly requires valid precondition entailment, valid postcondition consequence, and deadlock freedom."
                )

    def compute_hash(self) -> str:
        payload = (
            f"{self.check_id}:{self.leaf_id}:{self.morphism_status.value}:"
            f"{self.precondition_entailment_valid}:{self.postcondition_consequence_valid}:"
            f"{self.is_deadlock_free}:{self.solver_engine}:{self.proof_steps_count}:{self.unsat_core}"
        )
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "check_id": self.check_id,
            "leaf_id": self.leaf_id,
            "morphism_status": self.morphism_status.value,
            "precondition_entailment_valid": self.precondition_entailment_valid,
            "postcondition_consequence_valid": self.postcondition_consequence_valid,
            "is_deadlock_free": self.is_deadlock_free,
            "solver_engine": self.solver_engine,
            "proof_steps_count": self.proof_steps_count,
            "unsat_core": self.unsat_core,
            "counter_example": self.counter_example,
            "checked_at_unix_ms": self.checked_at_unix_ms,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> SMTModelCheckResult:
        instance = cls(
            check_id=data["check_id"],
            leaf_id=data["leaf_id"],
            morphism_status=MorphismCheckStatus(data["morphism_status"]),
            precondition_entailment_valid=bool(data["precondition_entailment_valid"]),
            postcondition_consequence_valid=bool(data["postcondition_consequence_valid"]),
            is_deadlock_free=bool(data["is_deadlock_free"]),
            solver_engine=data.get("solver_engine", "NativeSMTProver_v4b"),
            proof_steps_count=int(data.get("proof_steps_count", 0)),
            unsat_core=data.get("unsat_core"),
            counter_example=dict(data.get("counter_example", {})),
            checked_at_unix_ms=int(data.get("checked_at_unix_ms", int(time.time() * 1000))),
        )
        instance.validate_invariants()
        return instance


@dataclass
class ByzantineFuzzVector:
    """An adversarial stress vector dispatched against code leaves and enclaves."""
    vector_id: str
    vector_type: FuzzVectorType
    target_channel: str
    payload_bytes_corrupted: int = 0
    delay_ms: float = 0.0
    injection_target: str = "enclave_ingress"
    entropy_seed: str = "seed_default"
    expected_enclave: str = "enclave_byzantine_leak"

    def validate_invariants(self) -> None:
        if not self.vector_id:
            raise AuditDomainInvariantViolation("vector_id must not be empty.")
        if not self.target_channel:
            raise AuditDomainInvariantViolation("target_channel must not be empty.")
        if self.payload_bytes_corrupted < 0:
            raise AuditDomainInvariantViolation("payload_bytes_corrupted must be non-negative.")
        if self.delay_ms < 0.0:
            raise AuditDomainInvariantViolation("delay_ms must be non-negative.")

    def compute_hash(self) -> str:
        payload = f"{self.vector_id}:{self.vector_type.value}:{self.target_channel}:{self.payload_bytes_corrupted}:{self.delay_ms}:{self.entropy_seed}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "vector_id": self.vector_id,
            "vector_type": self.vector_type.value,
            "target_channel": self.target_channel,
            "payload_bytes_corrupted": self.payload_bytes_corrupted,
            "delay_ms": self.delay_ms,
            "injection_target": self.injection_target,
            "entropy_seed": self.entropy_seed,
            "expected_enclave": self.expected_enclave,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ByzantineFuzzVector:
        instance = cls(
            vector_id=data["vector_id"],
            vector_type=FuzzVectorType(data["vector_type"]),
            target_channel=data["target_channel"],
            payload_bytes_corrupted=int(data.get("payload_bytes_corrupted", 0)),
            delay_ms=float(data.get("delay_ms", 0.0)),
            injection_target=data.get("injection_target", "enclave_ingress"),
            entropy_seed=data.get("entropy_seed", "seed_default"),
            expected_enclave=data.get("expected_enclave", "enclave_byzantine_leak"),
        )
        instance.validate_invariants()
        return instance


@dataclass
class ByzantineFuzzReport:
    """Summary of adversarial fuzzing outcomes emitted by AdversaryChaos."""
    report_id: str
    leaf_id: str
    vectors_dispatched: int
    vectors_trapped: int
    trap_rate: float
    unhandled_faults: int
    enclaves_engaged: List[str] = field(default_factory=list)
    fuzzer_node_id: str = "node_chaos_adversary"
    executed_at_unix_ms: int = field(default_factory=lambda: int(time.time() * 1000))

    def validate_invariants(self) -> None:
        if not self.report_id:
            raise AuditDomainInvariantViolation("report_id must not be empty.")
        if not self.leaf_id:
            raise AuditDomainInvariantViolation("leaf_id must not be empty.")
        if self.vectors_dispatched < 0 or self.vectors_trapped < 0:
            raise AuditDomainInvariantViolation("Vector counts must be non-negative.")
        if self.vectors_trapped > self.vectors_dispatched:
            raise AuditDomainInvariantViolation("vectors_trapped cannot exceed vectors_dispatched.")
        if not (0.0 <= self.trap_rate <= 1.0):
            raise AuditDomainInvariantViolation(f"trap_rate must be between 0.0 and 1.0, got {self.trap_rate}.")

    def compute_hash(self) -> str:
        payload = f"{self.report_id}:{self.leaf_id}:{self.vectors_dispatched}:{self.vectors_trapped}:{self.trap_rate:.4f}:{self.unhandled_faults}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "report_id": self.report_id,
            "leaf_id": self.leaf_id,
            "vectors_dispatched": self.vectors_dispatched,
            "vectors_trapped": self.vectors_trapped,
            "trap_rate": self.trap_rate,
            "unhandled_faults": self.unhandled_faults,
            "enclaves_engaged": self.enclaves_engaged,
            "fuzzer_node_id": self.fuzzer_node_id,
            "executed_at_unix_ms": self.executed_at_unix_ms,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ByzantineFuzzReport:
        instance = cls(
            report_id=data["report_id"],
            leaf_id=data["leaf_id"],
            vectors_dispatched=int(data["vectors_dispatched"]),
            vectors_trapped=int(data["vectors_trapped"]),
            trap_rate=float(data["trap_rate"]),
            unhandled_faults=int(data.get("unhandled_faults", 0)),
            enclaves_engaged=list(data.get("enclaves_engaged", [])),
            fuzzer_node_id=data.get("fuzzer_node_id", "node_chaos_adversary"),
            executed_at_unix_ms=int(data.get("executed_at_unix_ms", int(time.time() * 1000))),
        )
        instance.validate_invariants()
        return instance


@dataclass
class QuorumConsensusWitness:
    """Cryptographic consensus record adjudicated by the 3-peer Sheaf Quorum."""
    witness_id: str
    leaf_id: str
    verdict: QuorumVerdict
    sentry_syntax_vote: bool
    oracle_smt_vote: bool
    adversary_chaos_vote: bool
    consensus_ratio: float
    dissenting_nodes: List[str] = field(default_factory=list)
    quorum_timestamp_unix_ms: int = field(default_factory=lambda: int(time.time() * 1000))
    consensus_hash: str = ""

    def validate_invariants(self) -> None:
        if not self.witness_id:
            raise AuditDomainInvariantViolation("witness_id must not be empty.")
        if not self.leaf_id:
            raise AuditDomainInvariantViolation("leaf_id must not be empty.")
        if not (0.0 <= self.consensus_ratio <= 1.0):
            raise AuditDomainInvariantViolation(
                f"consensus_ratio must be between 0.0 and 1.0, got {self.consensus_ratio}."
            )

    def compute_hash(self) -> str:
        payload = (
            f"{self.witness_id}:{self.leaf_id}:{self.verdict.value}:"
            f"{self.sentry_syntax_vote}:{self.oracle_smt_vote}:{self.adversary_chaos_vote}:"
            f"{self.consensus_ratio:.4f}:{','.join(sorted(self.dissenting_nodes))}"
        )
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "witness_id": self.witness_id,
            "leaf_id": self.leaf_id,
            "verdict": self.verdict.value,
            "sentry_syntax_vote": self.sentry_syntax_vote,
            "oracle_smt_vote": self.oracle_smt_vote,
            "adversary_chaos_vote": self.adversary_chaos_vote,
            "consensus_ratio": self.consensus_ratio,
            "dissenting_nodes": self.dissenting_nodes,
            "quorum_timestamp_unix_ms": self.quorum_timestamp_unix_ms,
            "consensus_hash": self.consensus_hash or self.compute_hash(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> QuorumConsensusWitness:
        instance = cls(
            witness_id=data["witness_id"],
            leaf_id=data["leaf_id"],
            verdict=QuorumVerdict(data["verdict"]),
            sentry_syntax_vote=bool(data["sentry_syntax_vote"]),
            oracle_smt_vote=bool(data["oracle_smt_vote"]),
            adversary_chaos_vote=bool(data["adversary_chaos_vote"]),
            consensus_ratio=float(data["consensus_ratio"]),
            dissenting_nodes=list(data.get("dissenting_nodes", [])),
            quorum_timestamp_unix_ms=int(data.get("quorum_timestamp_unix_ms", int(time.time() * 1000))),
            consensus_hash=data.get("consensus_hash", ""),
        )
        instance.validate_invariants()
        return instance


@dataclass
class AuditAttestation:
    """Tamper-evident attestation sealing a verified code leaf into the sovereign Merkle DAG."""
    attestation_id: str
    leaf_id: str
    consensus_witness_id: str
    is_certified: bool
    merkle_leaf_hash: str
    merkle_root: str
    auditor_signatures: List[str] = field(default_factory=list)
    attestation_epoch: int = 1
    sealed_at_unix_ms: int = field(default_factory=lambda: int(time.time() * 1000))

    def validate_invariants(self) -> None:
        if not self.attestation_id:
            raise AuditDomainInvariantViolation("attestation_id must not be empty.")
        if not self.leaf_id:
            raise AuditDomainInvariantViolation("leaf_id must not be empty.")
        if not self.merkle_leaf_hash:
            raise AuditDomainInvariantViolation("merkle_leaf_hash must not be empty.")
        if not self.merkle_root:
            raise AuditDomainInvariantViolation("merkle_root must not be empty.")
        if self.is_certified and len(self.auditor_signatures) < 2:
            raise AuditDomainInvariantViolation(
                "Certified AuditAttestation requires at least 2 auditor signatures (2-of-3 quorum)."
            )

    def compute_hash(self) -> str:
        payload = (
            f"{self.attestation_id}:{self.leaf_id}:{self.consensus_witness_id}:{self.is_certified}:"
            f"{self.merkle_leaf_hash}:{self.merkle_root}:{','.join(self.auditor_signatures)}:{self.attestation_epoch}"
        )
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "attestation_id": self.attestation_id,
            "leaf_id": self.leaf_id,
            "consensus_witness_id": self.consensus_witness_id,
            "is_certified": self.is_certified,
            "merkle_leaf_hash": self.merkle_leaf_hash,
            "merkle_root": self.merkle_root,
            "auditor_signatures": self.auditor_signatures,
            "attestation_epoch": self.attestation_epoch,
            "sealed_at_unix_ms": self.sealed_at_unix_ms,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> AuditAttestation:
        instance = cls(
            attestation_id=data["attestation_id"],
            leaf_id=data["leaf_id"],
            consensus_witness_id=data["consensus_witness_id"],
            is_certified=bool(data["is_certified"]),
            merkle_leaf_hash=data["merkle_leaf_hash"],
            merkle_root=data["merkle_root"],
            auditor_signatures=list(data.get("auditor_signatures", [])),
            attestation_epoch=int(data.get("attestation_epoch", 1)),
            sealed_at_unix_ms=int(data.get("sealed_at_unix_ms", int(time.time() * 1000))),
        )
        instance.validate_invariants()
        return instance


@dataclass
class FunctorialUndoCheckpoint:
    """A causal rollback checkpoint preserving exact state hashes and Landauer thermodynamic counters."""
    checkpoint_id: str
    stage: AuditVerificationStage
    state_hash: str
    landauer_bits_checkpoint: int
    created_at_unix_ms: int = field(default_factory=lambda: int(time.time() * 1000))
    restoration_context: Dict[str, Any] = field(default_factory=dict)

    def validate_invariants(self) -> None:
        if not self.checkpoint_id:
            raise AuditDomainInvariantViolation("checkpoint_id must not be empty.")
        if not self.state_hash:
            raise AuditDomainInvariantViolation("state_hash must not be empty.")
        if self.landauer_bits_checkpoint < 0:
            raise AuditDomainInvariantViolation("landauer_bits_checkpoint must be non-negative.")

    def compute_hash(self) -> str:
        payload = f"{self.checkpoint_id}:{self.stage.value}:{self.state_hash}:{self.landauer_bits_checkpoint}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "checkpoint_id": self.checkpoint_id,
            "stage": self.stage.value,
            "state_hash": self.state_hash,
            "landauer_bits_checkpoint": self.landauer_bits_checkpoint,
            "created_at_unix_ms": self.created_at_unix_ms,
            "restoration_context": self.restoration_context,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> FunctorialUndoCheckpoint:
        instance = cls(
            checkpoint_id=data["checkpoint_id"],
            stage=AuditVerificationStage(data["stage"]),
            state_hash=data["state_hash"],
            landauer_bits_checkpoint=int(data["landauer_bits_checkpoint"]),
            created_at_unix_ms=int(data.get("created_at_unix_ms", int(time.time() * 1000))),
            restoration_context=dict(data.get("restoration_context", {})),
        )
        instance.validate_invariants()
        return instance


@dataclass
class LandauerThermodynamicLedger:
    """Thermodynamic capital ledger tracking compute tokens, bit erasure, and Landauer dissipation."""
    ledger_id: str = "ledger_g4b_audit_thermodynamics"
    total_bits_erased: int = 0
    heat_dissipated_joules: float = 0.0
    token_lease_budget: int = 923100  # Option C unified BPE token budget
    exploratory_capital: int = 553860  # 60%
    protected_capital: int = 369240    # 40%
    spent_exploratory_tokens: int = 0
    spent_protected_tokens: int = 0

    # Boltzmann constant: 1.380649e-23 J/K
    BOLTZMANN_K: float = 1.380649e-23
    LN_2: float = 0.69314718056

    def record_bit_erasure(self, bits: int, temp_kelvin: float = 300.0) -> float:
        """Records irreversible bit erasure and computes dissipated heat Q = k_B * T * ln(2) * bits."""
        if bits < 0:
            raise AuditDomainInvariantViolation("Bits erased must be non-negative.")
        self.total_bits_erased += bits
        # Q = k_B * T * ln(2) * N
        dissipated = self.BOLTZMANN_K * temp_kelvin * self.LN_2 * bits
        self.heat_dissipated_joules += dissipated
        return dissipated

    def record_bit_recovery(self, bits: int) -> None:
        """Adjoint functorial reversal recovers bits and reduces accumulated erasure tally."""
        if bits < 0:
            raise AuditDomainInvariantViolation("Recovered bits must be non-negative.")
        self.total_bits_erased = max(0, self.total_bits_erased - bits)

    def spend_tokens(self, amount: int, is_protected: bool = False) -> None:
        """Spends BPE tokens while enforcing the strict 60/40 thermodynamic boundary."""
        if amount < 0:
            raise AuditDomainInvariantViolation("Spend amount must be non-negative.")
        if is_protected:
            if self.spent_protected_tokens + amount > self.protected_capital:
                raise AuditDomainInvariantViolation(
                    f"Protected token sink limit exceeded: {self.spent_protected_tokens + amount} > {self.protected_capital}."
                )
            self.spent_protected_tokens += amount
        else:
            if self.spent_exploratory_tokens + amount > self.exploratory_capital:
                raise AuditDomainInvariantViolation(
                    f"Exploratory token lease ceiling exceeded: {self.spent_exploratory_tokens + amount} > {self.exploratory_capital}."
                )
            self.spent_exploratory_tokens += amount

    def validate_invariants(self) -> None:
        if self.token_lease_budget <= 0:
            raise AuditDomainInvariantViolation("token_lease_budget must be positive.")
        if self.exploratory_capital + self.protected_capital != self.token_lease_budget:
            raise AuditDomainInvariantViolation(
                f"60/40 capital partition must sum to total budget: {self.exploratory_capital} + {self.protected_capital} != {self.token_lease_budget}."
            )
        if self.total_bits_erased < 0:
            raise AuditDomainInvariantViolation("total_bits_erased must be non-negative.")

    def compute_hash(self) -> str:
        payload = (
            f"{self.ledger_id}:{self.total_bits_erased}:{self.heat_dissipated_joules:.12e}:"
            f"{self.spent_exploratory_tokens}:{self.spent_protected_tokens}"
        )
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ledger_id": self.ledger_id,
            "total_bits_erased": self.total_bits_erased,
            "heat_dissipated_joules": self.heat_dissipated_joules,
            "token_lease_budget": self.token_lease_budget,
            "exploratory_capital": self.exploratory_capital,
            "protected_capital": self.protected_capital,
            "spent_exploratory_tokens": self.spent_exploratory_tokens,
            "spent_protected_tokens": self.spent_protected_tokens,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> LandauerThermodynamicLedger:
        instance = cls(
            ledger_id=data.get("ledger_id", "ledger_g4b_audit_thermodynamics"),
            total_bits_erased=int(data.get("total_bits_erased", 0)),
            heat_dissipated_joules=float(data.get("heat_dissipated_joules", 0.0)),
            token_lease_budget=int(data.get("token_lease_budget", 923100)),
            exploratory_capital=int(data.get("exploratory_capital", 553860)),
            protected_capital=int(data.get("protected_capital", 369240)),
            spent_exploratory_tokens=int(data.get("spent_exploratory_tokens", 0)),
            spent_protected_tokens=int(data.get("spent_protected_tokens", 0)),
        )
        instance.validate_invariants()
        return instance


@dataclass
class AuditServiceTopologyState:
    """Network topology and channel routing state for the Sovereign Audit Service."""
    node_id: str = "node_audit_kernel"
    service_endpoint: str = "192.168.40.30:8444"
    builder_endpoint: str = "192.168.40.20:8443"
    research_endpoint: str = "192.168.40.10:8442"
    active_peers: List[str] = field(default_factory=lambda: [
        "node_hermetic_sentry",
        "node_smt_oracle",
        "node_chaos_adversary",
        "node_merkle_sheaf",
    ])
    is_partitioned: bool = False
    registered_channels: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    def validate_invariants(self) -> None:
        if not self.node_id:
            raise AuditDomainInvariantViolation("node_id must not be empty.")
        assert_non_loopback(self.service_endpoint, "AuditServiceTopologyState service_endpoint")
        assert_non_loopback(self.builder_endpoint, "AuditServiceTopologyState builder_endpoint")
        assert_non_loopback(self.research_endpoint, "AuditServiceTopologyState research_endpoint")

    def compute_hash(self) -> str:
        payload = f"{self.node_id}:{self.service_endpoint}:{self.builder_endpoint}:{self.research_endpoint}:{self.is_partitioned}:{len(self.registered_channels)}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_id": self.node_id,
            "service_endpoint": self.service_endpoint,
            "builder_endpoint": self.builder_endpoint,
            "research_endpoint": self.research_endpoint,
            "active_peers": self.active_peers,
            "is_partitioned": self.is_partitioned,
            "registered_channels": self.registered_channels,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> AuditServiceTopologyState:
        instance = cls(
            node_id=data.get("node_id", "node_audit_kernel"),
            service_endpoint=data.get("service_endpoint", "192.168.40.30:8444"),
            builder_endpoint=data.get("builder_endpoint", "192.168.40.20:8443"),
            research_endpoint=data.get("research_endpoint", "192.168.40.10:8442"),
            active_peers=list(data.get("active_peers", [])),
            is_partitioned=bool(data.get("is_partitioned", False)),
            registered_channels=dict(data.get("registered_channels", {})),
        )
        instance.validate_invariants()
        return instance
