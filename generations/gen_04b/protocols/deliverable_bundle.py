"""Generation 4b Standardized Research Deliverable Bundle Protocol (`protocols/deliverable_bundle.py`).

Enforces:
- [L1-G4B-001] Service-Oriented Sovereign Mesh Protocol Standardization.
- [L1-G4B-002] Zero-Code Research Tool Boundary.
- [L1-G4B-003] Hierarchical Merkle-DAG Witness Telemetry.
- Standardized schema for deliverables emitted by Research Service and ingested by Builder Enclave.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
import hashlib
import json
from typing import Any, Dict, List, Optional


class DeliverableProtocolViolation(Exception):
    """Raised when a deliverable bundle or sub-artifact violates its invariant rules."""
    pass


class OperationalPitfall(str, Enum):
    """Operational risk categories for backend and distributed services."""
    CONCURRENCY_STATE_RACE = "CONCURRENCY_STATE_RACE"
    RESOURCE_LEAK_UNCLOSED = "RESOURCE_LEAK_UNCLOSED"
    TRANSIENT_NETWORK_FAILURE = "TRANSIENT_NETWORK_FAILURE"
    UNHANDLED_BOUNDARY_EXCEPTION = "UNHANDLED_BOUNDARY_EXCEPTION"
    UNBOUNDED_QUEUE_BACKPRESSURE = "UNBOUNDED_QUEUE_BACKPRESSURE"
    DEADLOCK_CIRCULAR_WAIT = "DEADLOCK_CIRCULAR_WAIT"


class MitigationRule(str, Enum):
    """Required structural AST mitigations enforcing operational safety."""
    WITH_LOCK_GUARD = "WITH_LOCK_GUARD"
    TRY_FINALLY_CLEANUP = "TRY_FINALLY_CLEANUP"
    BOUNDED_TIMEOUT = "BOUNDED_TIMEOUT"
    EXPONENTIAL_BACKOFF_RETRY = "EXPONENTIAL_BACKOFF_RETRY"
    EXCEPTION_TRANSLATION_ENCLAVE = "EXCEPTION_TRANSLATION_ENCLAVE"
    BOUNDED_BUFFER_LIMIT = "BOUNDED_BUFFER_LIMIT"


@dataclass
class MitigationPattern:
    """Formal mapping between an operational pitfall and its required AST mitigation rule."""
    pitfall: OperationalPitfall
    rule: MitigationRule
    target_guard: Optional[str] = None
    cleanup_target: Optional[str] = None
    max_timeout_sec: Optional[float] = None

    def validate_invariants(self) -> None:
        if self.rule == MitigationRule.WITH_LOCK_GUARD and not self.target_guard:
            raise DeliverableProtocolViolation("WITH_LOCK_GUARD requires target_guard identifier.")
        if self.rule == MitigationRule.TRY_FINALLY_CLEANUP and not self.cleanup_target:
            raise DeliverableProtocolViolation("TRY_FINALLY_CLEANUP requires cleanup_target identifier.")
        if self.rule == MitigationRule.BOUNDED_TIMEOUT and self.max_timeout_sec is not None:
            if self.max_timeout_sec <= 0.0:
                raise DeliverableProtocolViolation("max_timeout_sec must be strictly positive.")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "pitfall": self.pitfall.value,
            "rule": self.rule.value,
            "target_guard": self.target_guard,
            "cleanup_target": self.cleanup_target,
            "max_timeout_sec": self.max_timeout_sec,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> MitigationPattern:
        instance = cls(
            pitfall=OperationalPitfall(data["pitfall"]),
            rule=MitigationRule(data["rule"]),
            target_guard=data.get("target_guard"),
            cleanup_target=data.get("cleanup_target"),
            max_timeout_sec=float(data["max_timeout_sec"]) if data.get("max_timeout_sec") is not None else None,
        )
        instance.validate_invariants()
        return instance


@dataclass
class ContractBijectivityWitness:
    """Attestation certifying a 100% bijective mapping between ContractIR and AST code structures."""
    witness_id: str
    contract_id: str
    source_file: str
    is_bijective: bool
    mapped_verbs: List[str] = field(default_factory=list)
    unmapped_verbs: List[str] = field(default_factory=list)
    rogue_functions: List[str] = field(default_factory=list)
    docstring_hash_matches: bool = True
    spec_hashes: Dict[str, str] = field(default_factory=dict)
    timestamp_unix_ms: int = 0

    def validate_invariants(self) -> None:
        if not self.witness_id:
            raise DeliverableProtocolViolation("witness_id must not be empty.")
        if not self.contract_id:
            raise DeliverableProtocolViolation("contract_id must not be empty.")
        if self.is_bijective:
            if len(self.unmapped_verbs) > 0 or len(self.rogue_functions) > 0 or not self.docstring_hash_matches:
                raise DeliverableProtocolViolation(
                    "Witness cannot be marked is_bijective when unmapped verbs, rogue functions, or hash drift exist."
                )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "witness_id": self.witness_id,
            "contract_id": self.contract_id,
            "source_file": self.source_file,
            "is_bijective": self.is_bijective,
            "mapped_verbs": list(self.mapped_verbs),
            "unmapped_verbs": list(self.unmapped_verbs),
            "rogue_functions": list(self.rogue_functions),
            "docstring_hash_matches": self.docstring_hash_matches,
            "spec_hashes": dict(self.spec_hashes),
            "timestamp_unix_ms": self.timestamp_unix_ms,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ContractBijectivityWitness:
        instance = cls(
            witness_id=data["witness_id"],
            contract_id=data["contract_id"],
            source_file=data.get("source_file", ""),
            is_bijective=bool(data["is_bijective"]),
            mapped_verbs=list(data.get("mapped_verbs", [])),
            unmapped_verbs=list(data.get("unmapped_verbs", [])),
            rogue_functions=list(data.get("rogue_functions", [])),
            docstring_hash_matches=bool(data.get("docstring_hash_matches", True)),
            spec_hashes=dict(data.get("spec_hashes", {})),
            timestamp_unix_ms=int(data.get("timestamp_unix_ms", 0)),
        )
        instance.validate_invariants()
        return instance


@dataclass
class OperationalPitfallAuditReport:
    """Report certifying physical AST-level mitigations for declared operational pitfalls."""
    report_id: str
    source_file: str
    is_compliant: bool
    violations: List[Dict[str, Any]] = field(default_factory=list)
    mitigations_verified: List[str] = field(default_factory=list)
    auditor_node_id: str = "node_hermetic_sentry"
    timestamp_unix_ms: int = 0

    def validate_invariants(self) -> None:
        if not self.report_id:
            raise DeliverableProtocolViolation("report_id must not be empty.")
        if self.is_compliant and len(self.violations) > 0:
            raise DeliverableProtocolViolation("Audit report cannot be compliant with active violations.")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "report_id": self.report_id,
            "source_file": self.source_file,
            "is_compliant": self.is_compliant,
            "violations": self.violations,
            "mitigations_verified": self.mitigations_verified,
            "auditor_node_id": self.auditor_node_id,
            "timestamp_unix_ms": self.timestamp_unix_ms,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> OperationalPitfallAuditReport:
        instance = cls(
            report_id=data["report_id"],
            source_file=data.get("source_file", ""),
            is_compliant=bool(data["is_compliant"]),
            violations=list(data.get("violations", [])),
            mitigations_verified=list(data.get("mitigations_verified", [])),
            auditor_node_id=data.get("auditor_node_id", "node_hermetic_sentry"),
            timestamp_unix_ms=int(data.get("timestamp_unix_ms", 0)),
        )
        instance.validate_invariants()
        return instance


@dataclass
class HypothesisDefinition:
    """A formal theoretical claim grounded in axioms and SMT conjectures."""
    hypothesis_id: str
    theoretical_claim: str
    governing_axioms: List[str]
    expected_complexity_class: str
    formal_conjecture_z3: str
    novelty_score: float = 0.0

    def validate_invariants(self) -> None:
        if not self.theoretical_claim:
            raise DeliverableProtocolViolation("theoretical_claim must not be empty.")
        if len(self.governing_axioms) < 1:
            raise DeliverableProtocolViolation("Hypothesis must bind to at least one governing axiom.")
        if not self.formal_conjecture_z3:
            raise DeliverableProtocolViolation("formal_conjecture_z3 must be defined.")
        if not (0.0 <= self.novelty_score <= 1.0):
            raise DeliverableProtocolViolation(
                f"novelty_score must be between 0.0 and 1.0, got {self.novelty_score}"
            )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "hypothesis_id": self.hypothesis_id,
            "theoretical_claim": self.theoretical_claim,
            "governing_axioms": self.governing_axioms,
            "expected_complexity_class": self.expected_complexity_class,
            "formal_conjecture_z3": self.formal_conjecture_z3,
            "novelty_score": self.novelty_score,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> HypothesisDefinition:
        instance = cls(
            hypothesis_id=data["hypothesis_id"],
            theoretical_claim=data["theoretical_claim"],
            governing_axioms=list(data.get("governing_axioms", [])),
            expected_complexity_class=data.get("expected_complexity_class", "O(1)"),
            formal_conjecture_z3=data["formal_conjecture_z3"],
            novelty_score=float(data.get("novelty_score", 0.0)),
        )
        instance.validate_invariants()
        return instance


@dataclass
class ConstraintAnalysis:
    """Formal analysis of physical, Landauer, and topological boundaries."""
    analysis_id: str
    physical_latency_budget_ms: int
    landauer_erasure_budget_bits: int
    topological_interfaces: List[str]
    vetoed_negative_axioms: List[str]

    def validate_invariants(self) -> None:
        if self.physical_latency_budget_ms <= 0:
            raise DeliverableProtocolViolation("physical_latency_budget_ms must be strictly positive.")
        if self.landauer_erasure_budget_bits < 0:
            raise DeliverableProtocolViolation("landauer_erasure_budget_bits cannot be negative.")
        for ip in self.topological_interfaces:
            clean_ip = ip.split(":")[0].strip()
            if clean_ip.startswith("127.") or clean_ip in ("localhost", "::1"):
                raise DeliverableProtocolViolation(
                    f"[L1-G3B-012 Violation] Loopback address {ip} strictly prohibited in topological_interfaces."
                )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "analysis_id": self.analysis_id,
            "physical_latency_budget_ms": self.physical_latency_budget_ms,
            "landauer_erasure_budget_bits": self.landauer_erasure_budget_bits,
            "topological_interfaces": self.topological_interfaces,
            "vetoed_negative_axioms": self.vetoed_negative_axioms,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ConstraintAnalysis:
        instance = cls(
            analysis_id=data["analysis_id"],
            physical_latency_budget_ms=int(data["physical_latency_budget_ms"]),
            landauer_erasure_budget_bits=int(data["landauer_erasure_budget_bits"]),
            topological_interfaces=list(data.get("topological_interfaces", [])),
            vetoed_negative_axioms=list(data.get("vetoed_negative_axioms", [])),
        )
        instance.validate_invariants()
        return instance


@dataclass
class FailureModeModel:
    """Adversarial modeling of Byzantine faults, partitions, and recovery enclaves."""
    model_id: str
    byzantine_vectors: List[str]
    partition_scenarios: List[str]
    deadlock_states: List[str]
    recovery_pipeline_urns: List[str]

    def validate_invariants(self) -> None:
        if len(self.byzantine_vectors) < 2:
            raise DeliverableProtocolViolation(
                f"FailureModeModel requires at least 2 Byzantine vectors, got {len(self.byzantine_vectors)}"
            )
        if len(self.partition_scenarios) < 1:
            raise DeliverableProtocolViolation("FailureModeModel requires at least 1 partition scenario.")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "model_id": self.model_id,
            "byzantine_vectors": self.byzantine_vectors,
            "partition_scenarios": self.partition_scenarios,
            "deadlock_states": self.deadlock_states,
            "recovery_pipeline_urns": self.recovery_pipeline_urns,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> FailureModeModel:
        instance = cls(
            model_id=data["model_id"],
            byzantine_vectors=list(data.get("byzantine_vectors", [])),
            partition_scenarios=list(data.get("partition_scenarios", [])),
            deadlock_states=list(data.get("deadlock_states", [])),
            recovery_pipeline_urns=list(data.get("recovery_pipeline_urns", [])),
        )
        instance.validate_invariants()
        return instance


@dataclass
class TradeoffMatrix:
    """Formal multi-objective tradeoff evaluation across candidate options."""
    matrix_id: str
    evaluated_options: List[str]
    pareto_frontier_options: List[str]
    scoring_weights: Dict[str, float]
    selection_proof: str

    def validate_invariants(self) -> None:
        if len(self.pareto_frontier_options) < 1:
            raise DeliverableProtocolViolation("TradeoffMatrix requires at least 1 Pareto frontier option.")
        total_weight = sum(self.scoring_weights.values())
        if abs(total_weight - 1.0) > 1e-4:
            raise DeliverableProtocolViolation(
                f"Scoring weights must sum to 1.0, got {total_weight:.6f}"
            )
        if not self.selection_proof:
            raise DeliverableProtocolViolation("selection_proof must not be empty.")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "matrix_id": self.matrix_id,
            "evaluated_options": self.evaluated_options,
            "pareto_frontier_options": self.pareto_frontier_options,
            "scoring_weights": self.scoring_weights,
            "selection_proof": self.selection_proof,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> TradeoffMatrix:
        instance = cls(
            matrix_id=data["matrix_id"],
            evaluated_options=list(data.get("evaluated_options", [])),
            pareto_frontier_options=list(data.get("pareto_frontier_options", [])),
            scoring_weights=dict(data.get("scoring_weights", {})),
            selection_proof=data.get("selection_proof", ""),
        )
        instance.validate_invariants()
        return instance


@dataclass
class TabooDistanceMatrix:
    """Topological graph edit distance matrix across isolated research islands."""
    matrix_id: str
    island_ids: List[str]
    distance_entries: Dict[str, float]  # Key: "island_i:island_j" -> float

    def validate_invariants(self) -> None:
        if len(self.island_ids) < 2:
            raise DeliverableProtocolViolation("TabooDistanceMatrix requires at least 2 island IDs.")
        for pair_key, dist in self.distance_entries.items():
            if not (0.0 <= dist <= 1.0):
                raise DeliverableProtocolViolation(
                    f"Graph taboo distance for {pair_key} must be in [0.0, 1.0], got {dist}"
                )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "matrix_id": self.matrix_id,
            "island_ids": self.island_ids,
            "distance_entries": self.distance_entries,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> TabooDistanceMatrix:
        instance = cls(
            matrix_id=data["matrix_id"],
            island_ids=list(data.get("island_ids", [])),
            distance_entries=dict(data.get("distance_entries", {})),
        )
        instance.validate_invariants()
        return instance


@dataclass
class ResearchDeliverableBundle:
    """The sovereign, immutable architectural specification emitted by G4b-Research."""
    bundle_id: str
    target_soc_id: str
    hypothesis_id: str
    constraint_analysis_id: str
    failure_mode_id: str
    tradeoff_matrix_id: str
    reference_architecture_hash: str  # 64-char SHA-256 hex
    merkle_root: str                  # 64-char SHA-256 hex
    is_certified: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

    def validate_invariants(self) -> None:
        if not self.bundle_id:
            raise DeliverableProtocolViolation("bundle_id must not be empty.")
        if not self.target_soc_id:
            raise DeliverableProtocolViolation("target_soc_id must not be empty.")
        if self.is_certified:
            if len(self.reference_architecture_hash) != 64:
                raise DeliverableProtocolViolation(
                    f"Certified bundle requires valid 64-char SHA-256 reference_architecture_hash, "
                    f"got {len(self.reference_architecture_hash)}"
                )
            if len(self.merkle_root) != 64:
                raise DeliverableProtocolViolation(
                    f"Certified bundle requires valid 64-char SHA-256 merkle_root, "
                    f"got {len(self.merkle_root)}"
                )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "bundle_id": self.bundle_id,
            "target_soc_id": self.target_soc_id,
            "hypothesis_id": self.hypothesis_id,
            "constraint_analysis_id": self.constraint_analysis_id,
            "failure_mode_id": self.failure_mode_id,
            "tradeoff_matrix_id": self.tradeoff_matrix_id,
            "reference_architecture_hash": self.reference_architecture_hash,
            "merkle_root": self.merkle_root,
            "is_certified": self.is_certified,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ResearchDeliverableBundle:
        instance = cls(
            bundle_id=data["bundle_id"],
            target_soc_id=data["target_soc_id"],
            hypothesis_id=data["hypothesis_id"],
            constraint_analysis_id=data["constraint_analysis_id"],
            failure_mode_id=data["failure_mode_id"],
            tradeoff_matrix_id=data["tradeoff_matrix_id"],
            reference_architecture_hash=data["reference_architecture_hash"],
            merkle_root=data["merkle_root"],
            is_certified=data.get("is_certified", False),
            metadata=data.get("metadata", {}),
        )
        instance.validate_invariants()
        return instance
