"""Generation 4b Domain Models & Typed Nouns (`soc_g4b_researcher`).

Enforces:
- [L1-G3B-011] Universal Compositional Contract IR & Domain Invariants.
- [L1-G4B-001] Decoupled Research Service Invariants.
- [L1-G4B-002] Zero-Code Research Tool Boundary.
- [L1-G4B-003] Hierarchical Merkle-DAG Telemetry.
- Complete specification of all 18 Domain Nouns with algebraic validation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
import hashlib
import json
import time
from typing import Any, Dict, List, Optional, Set, Tuple
import uuid


class DomainInvariantViolation(Exception):
    """Raised when an algebraic domain invariant or boundary rule is violated."""
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


class StressDimension(str, Enum):
    """Adversarial stress dimensions for boundary testing."""
    LATENCY = "LATENCY"
    PACKET_LOSS = "PACKET_LOSS"
    BYZANTINE_RATIO = "BYZANTINE_RATIO"
    MEMORY_STARVATION = "MEMORY_STARVATION"


# =========================================================================
# 1. ResearchDeliverableBundle
# =========================================================================
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
            raise DomainInvariantViolation("bundle_id must not be empty.")
        if not self.target_soc_id:
            raise DomainInvariantViolation("target_soc_id must not be empty.")
        if self.is_certified:
            if len(self.reference_architecture_hash) != 64:
                raise DomainInvariantViolation(
                    f"Certified bundle requires valid 64-char SHA-256 reference_architecture_hash, "
                    f"got {len(self.reference_architecture_hash)}"
                )
            if len(self.merkle_root) != 64:
                raise DomainInvariantViolation(
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


# =========================================================================
# 2. HypothesisDefinition
# =========================================================================
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
            raise DomainInvariantViolation("theoretical_claim must not be empty.")
        if len(self.governing_axioms) < 1:
            raise DomainInvariantViolation("Hypothesis must bind to at least one governing axiom.")
        if not self.formal_conjecture_z3:
            raise DomainInvariantViolation("formal_conjecture_z3 must be defined.")
        if not (0.0 <= self.novelty_score <= 1.0):
            raise DomainInvariantViolation(
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


# =========================================================================
# 3. ConstraintAnalysis
# =========================================================================
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
            raise DomainInvariantViolation("physical_latency_budget_ms must be strictly positive.")
        if self.landauer_erasure_budget_bits < 0:
            raise DomainInvariantViolation("landauer_erasure_budget_bits cannot be negative.")
        for ip in self.topological_interfaces:
            clean_ip = ip.split(":")[0].strip()
            if clean_ip.startswith("127.") or clean_ip in ("localhost", "::1"):
                raise DomainInvariantViolation(
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


# =========================================================================
# 4. FailureModeModel
# =========================================================================
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
            raise DomainInvariantViolation(
                f"FailureModeModel requires at least 2 Byzantine vectors, got {len(self.byzantine_vectors)}"
            )
        if len(self.partition_scenarios) < 1:
            raise DomainInvariantViolation("FailureModeModel requires at least 1 partition scenario.")

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


# =========================================================================
# 5. TradeoffMatrix
# =========================================================================
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
            raise DomainInvariantViolation("TradeoffMatrix requires at least 1 Pareto frontier option.")
        total_weight = sum(self.scoring_weights.values())
        if abs(total_weight - 1.0) > 1e-4:
            raise DomainInvariantViolation(
                f"Scoring weights must sum to 1.0, got {total_weight:.6f}"
            )
        if not self.selection_proof:
            raise DomainInvariantViolation("selection_proof must not be empty.")

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


# =========================================================================
# 6. SpecAdjustmentRequest
# =========================================================================
@dataclass
class SpecAdjustmentRequest:
    """Builder-submitted RFC requesting a specification adjustment under physical friction."""
    request_id: str
    builder_node_id: str
    target_symbol_urn: str
    bottleneck_type: BottleneckType
    empirical_evidence: str
    proposed_delta: str
    preserved_invariants: List[str]

    def validate_invariants(self) -> None:
        if len(self.preserved_invariants) < 1:
            raise DomainInvariantViolation("SpecAdjustmentRequest must preserve at least one core invariant.")
        if not self.empirical_evidence:
            raise DomainInvariantViolation("empirical_evidence is mandatory for an RFC request.")
        if not self.proposed_delta:
            raise DomainInvariantViolation("proposed_delta must not be empty.")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "request_id": self.request_id,
            "builder_node_id": self.builder_node_id,
            "target_symbol_urn": self.target_symbol_urn,
            "bottleneck_type": self.bottleneck_type.value,
            "empirical_evidence": self.empirical_evidence,
            "proposed_delta": self.proposed_delta,
            "preserved_invariants": self.preserved_invariants,
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
        )
        instance.validate_invariants()
        return instance


# =========================================================================
# 7. SpecAmendment
# =========================================================================
@dataclass
class SpecAmendment:
    """Formal signed amendment or mathematical counter-proof from the RFC adjudicator."""
    amendment_id: str
    request_id: str
    is_approved: bool
    adjudicator_signature: str
    amended_contract_ir_delta: str
    rejection_counter_proof: Optional[str] = None

    def validate_invariants(self) -> None:
        if not self.is_approved:
            if not self.rejection_counter_proof or len(self.rejection_counter_proof.strip()) == 0:
                raise DomainInvariantViolation(
                    "Rejected SpecAmendment requires a formal rejection_counter_proof."
                )
        if not self.adjudicator_signature:
            raise DomainInvariantViolation("adjudicator_signature is mandatory.")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "amendment_id": self.amendment_id,
            "request_id": self.request_id,
            "is_approved": self.is_approved,
            "adjudicator_signature": self.adjudicator_signature,
            "amended_contract_ir_delta": self.amended_contract_ir_delta,
            "rejection_counter_proof": self.rejection_counter_proof,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> SpecAmendment:
        instance = cls(
            amendment_id=data["amendment_id"],
            request_id=data["request_id"],
            is_approved=bool(data["is_approved"]),
            adjudicator_signature=data["adjudicator_signature"],
            amended_contract_ir_delta=data.get("amended_contract_ir_delta", ""),
            rejection_counter_proof=data.get("rejection_counter_proof"),
        )
        instance.validate_invariants()
        return instance


# =========================================================================
# 8. TabooDistanceMatrix
# =========================================================================
@dataclass
class TabooDistanceMatrix:
    """Topological graph edit distance matrix across isolated research islands."""
    matrix_id: str
    island_ids: List[str]
    distance_entries: Dict[str, float]  # Key: "island_i:island_j" -> float
    min_distance_threshold: float = 0.40

    def validate_invariants(self) -> None:
        if self.min_distance_threshold < 0.40:
            raise DomainInvariantViolation(
                f"min_distance_threshold cannot be weakened below 0.40, got {self.min_distance_threshold}"
            )
        for pair, d in self.distance_entries.items():
            if d < self.min_distance_threshold:
                raise DomainInvariantViolation(
                    f"Taboo breach between {pair}: distance {d:.4f} < threshold {self.min_distance_threshold}"
                )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "matrix_id": self.matrix_id,
            "island_ids": self.island_ids,
            "distance_entries": self.distance_entries,
            "min_distance_threshold": self.min_distance_threshold,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> TabooDistanceMatrix:
        instance = cls(
            matrix_id=data["matrix_id"],
            island_ids=list(data.get("island_ids", [])),
            distance_entries=dict(data.get("distance_entries", {})),
            min_distance_threshold=float(data.get("min_distance_threshold", 0.40)),
        )
        instance.validate_invariants()
        return instance


# =========================================================================
# 9. MerkleDagWitness
# =========================================================================
@dataclass
class MerkleDagWitness:
    """Cryptographic tamper-evident leaf or interior node in the hierarchical Merkle DAG."""
    node_hash: str
    parent_hashes: List[str]
    task_id: str
    actor_id: str
    payload_signature: str
    timestamp_ns: int

    def validate_invariants(self) -> None:
        if len(self.node_hash) != 64:
            raise DomainInvariantViolation(f"node_hash must be 64-char SHA-256 hex, got {len(self.node_hash)}")
        if self.timestamp_ns <= 0:
            raise DomainInvariantViolation("timestamp_ns must be strictly positive.")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_hash": self.node_hash,
            "parent_hashes": self.parent_hashes,
            "task_id": self.task_id,
            "actor_id": self.actor_id,
            "payload_signature": self.payload_signature,
            "timestamp_ns": self.timestamp_ns,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> MerkleDagWitness:
        instance = cls(
            node_hash=data["node_hash"],
            parent_hashes=list(data.get("parent_hashes", [])),
            task_id=data["task_id"],
            actor_id=data["actor_id"],
            payload_signature=data.get("payload_signature", ""),
            timestamp_ns=int(data["timestamp_ns"]),
        )
        instance.validate_invariants()
        return instance


# =========================================================================
# 10. EmpiricalTelemetryReport
# =========================================================================
@dataclass
class EmpiricalTelemetryReport:
    """Real-time empirical execution and thermodynamic ledger report."""
    report_id: str
    epoch_id: str
    total_bpe_tokens_spent: int
    landauer_bits_erased: int
    landauer_heat_joules: float
    module_retry_counts: Dict[str, int]
    substrate_test_exit_code: int

    def validate_invariants(self) -> None:
        if self.substrate_test_exit_code != 0:
            raise DomainInvariantViolation(
                f"[NEG-G1B-001 Violation] substrate_test_exit_code must be 0, got {self.substrate_test_exit_code}"
            )
        if self.landauer_bits_erased < 0:
            raise DomainInvariantViolation("landauer_bits_erased cannot be negative.")
        if self.total_bpe_tokens_spent < 0:
            raise DomainInvariantViolation("total_bpe_tokens_spent cannot be negative.")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "report_id": self.report_id,
            "epoch_id": self.epoch_id,
            "total_bpe_tokens_spent": self.total_bpe_tokens_spent,
            "landauer_bits_erased": self.landauer_bits_erased,
            "landauer_heat_joules": self.landauer_heat_joules,
            "module_retry_counts": self.module_retry_counts,
            "substrate_test_exit_code": self.substrate_test_exit_code,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> EmpiricalTelemetryReport:
        instance = cls(
            report_id=data["report_id"],
            epoch_id=data["epoch_id"],
            total_bpe_tokens_spent=int(data["total_bpe_tokens_spent"]),
            landauer_bits_erased=int(data["landauer_bits_erased"]),
            landauer_heat_joules=float(data["landauer_heat_joules"]),
            module_retry_counts=dict(data.get("module_retry_counts", {})),
            substrate_test_exit_code=int(data["substrate_test_exit_code"]),
        )
        instance.validate_invariants()
        return instance


# =========================================================================
# 11. EpistemicCrucibleTarget
# =========================================================================
@dataclass
class EpistemicCrucibleTarget:
    """Target specification initiating an epistemic crucible research campaign."""
    target_id: str
    problem_statement: str
    waterloo_soc_urn: str
    exploratory_token_lease: int
    required_island_count: int = 3

    def validate_invariants(self) -> None:
        if self.required_island_count < 3:
            raise DomainInvariantViolation(
                f"required_island_count must be >= 3, got {self.required_island_count}"
            )
        if self.exploratory_token_lease < 10000:
            raise DomainInvariantViolation(
                f"exploratory_token_lease must be >= 10,000 BPE tokens, got {self.exploratory_token_lease}"
            )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "target_id": self.target_id,
            "problem_statement": self.problem_statement,
            "waterloo_soc_urn": self.waterloo_soc_urn,
            "exploratory_token_lease": self.exploratory_token_lease,
            "required_island_count": self.required_island_count,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> EpistemicCrucibleTarget:
        instance = cls(
            target_id=data["target_id"],
            problem_statement=data["problem_statement"],
            waterloo_soc_urn=data["waterloo_soc_urn"],
            exploratory_token_lease=int(data["exploratory_token_lease"]),
            required_island_count=int(data.get("required_island_count", 3)),
        )
        instance.validate_invariants()
        return instance


# =========================================================================
# 12. ZeroContextIslandManifest
# =========================================================================
@dataclass
class ZeroContextIslandManifest:
    """Quarantine configuration for an isolated research subagent island."""
    island_id: str
    assigned_seed_entropy: str
    isolated_sandbox_path: str
    quarantine_token_budget: int
    generated_topology_hash: str

    def validate_invariants(self) -> None:
        if self.quarantine_token_budget <= 0:
            raise DomainInvariantViolation("quarantine_token_budget must be strictly positive.")
        if len(self.generated_topology_hash) != 64:
            raise DomainInvariantViolation(
                f"generated_topology_hash must be 64-char SHA-256, got {len(self.generated_topology_hash)}"
            )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "island_id": self.island_id,
            "assigned_seed_entropy": self.assigned_seed_entropy,
            "isolated_sandbox_path": self.isolated_sandbox_path,
            "quarantine_token_budget": self.quarantine_token_budget,
            "generated_topology_hash": self.generated_topology_hash,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ZeroContextIslandManifest:
        instance = cls(
            island_id=data["island_id"],
            assigned_seed_entropy=data["assigned_seed_entropy"],
            isolated_sandbox_path=data["isolated_sandbox_path"],
            quarantine_token_budget=int(data["quarantine_token_budget"]),
            generated_topology_hash=data["generated_topology_hash"],
        )
        instance.validate_invariants()
        return instance


# =========================================================================
# 13. NoveltyArchiveEntry
# =========================================================================
@dataclass
class NoveltyArchiveEntry:
    """Historical archive entry in Lehman & Stanley novelty search space."""
    archive_id: str
    topology_signature: str
    weisfeiler_lehman_hash: str
    behavioral_descriptor: List[float]
    novelty_score: float

    def validate_invariants(self) -> None:
        if self.novelty_score < 0.0:
            raise DomainInvariantViolation(f"novelty_score cannot be negative, got {self.novelty_score}")
        if len(self.behavioral_descriptor) < 3:
            raise DomainInvariantViolation(
                f"behavioral_descriptor requires at least 3 dimensions, got {len(self.behavioral_descriptor)}"
            )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "archive_id": self.archive_id,
            "topology_signature": self.topology_signature,
            "weisfeiler_lehman_hash": self.weisfeiler_lehman_hash,
            "behavioral_descriptor": self.behavioral_descriptor,
            "novelty_score": self.novelty_score,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> NoveltyArchiveEntry:
        instance = cls(
            archive_id=data["archive_id"],
            topology_signature=data["topology_signature"],
            weisfeiler_lehman_hash=data["weisfeiler_lehman_hash"],
            behavioral_descriptor=list(data.get("behavioral_descriptor", [])),
            novelty_score=float(data["novelty_score"]),
        )
        instance.validate_invariants()
        return instance


# =========================================================================
# 14. DialecticalNegationSeed
# =========================================================================
@dataclass
class DialecticalNegationSeed:
    """Negative invariant injected to compel synthesis of orthogonal architectures."""
    seed_id: str
    default_primitive: str
    negated_invariant: str
    forced_alternative_archetype: str

    def validate_invariants(self) -> None:
        if not self.negated_invariant:
            raise DomainInvariantViolation("negated_invariant must not be empty.")
        if self.default_primitive == self.forced_alternative_archetype:
            raise DomainInvariantViolation(
                f"default_primitive '{self.default_primitive}' must differ from forced_alternative_archetype."
            )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "seed_id": self.seed_id,
            "default_primitive": self.default_primitive,
            "negated_invariant": self.negated_invariant,
            "forced_alternative_archetype": self.forced_alternative_archetype,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> DialecticalNegationSeed:
        instance = cls(
            seed_id=data["seed_id"],
            default_primitive=data["default_primitive"],
            negated_invariant=data["negated_invariant"],
            forced_alternative_archetype=data["forced_alternative_archetype"],
        )
        instance.validate_invariants()
        return instance


# =========================================================================
# 15. ExtremeBoundaryArchetype
# =========================================================================
@dataclass
class ExtremeBoundaryArchetype:
    """Stress profile applied during adversarial boundary fuzzing."""
    archetype_id: str
    stress_dimension: StressDimension
    stress_magnitude: float
    adversarial_invariants: List[str]

    def validate_invariants(self) -> None:
        if self.stress_magnitude <= 0.0:
            raise DomainInvariantViolation("stress_magnitude must be strictly positive.")
        if len(self.adversarial_invariants) < 1:
            raise DomainInvariantViolation("ExtremeBoundaryArchetype requires at least one adversarial invariant.")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "archetype_id": self.archetype_id,
            "stress_dimension": self.stress_dimension.value,
            "stress_magnitude": self.stress_magnitude,
            "adversarial_invariants": self.adversarial_invariants,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ExtremeBoundaryArchetype:
        instance = cls(
            archetype_id=data["archetype_id"],
            stress_dimension=StressDimension(data["stress_dimension"]),
            stress_magnitude=float(data["stress_magnitude"]),
            adversarial_invariants=list(data.get("adversarial_invariants", [])),
        )
        instance.validate_invariants()
        return instance


# =========================================================================
# 16. ByzantineFuzzVector
# =========================================================================
@dataclass
class ByzantineFuzzVector:
    """Chaotic network frame injected into channels to verify enclave trapping."""
    vector_id: str
    target_channel_id: str
    mutation_payload: str
    expected_trap_predicate: str
    is_trapped: bool = False

    def validate_invariants(self) -> None:
        if not self.target_channel_id:
            raise DomainInvariantViolation("target_channel_id cannot be empty.")
        if not self.mutation_payload:
            raise DomainInvariantViolation("mutation_payload cannot be empty.")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "vector_id": self.vector_id,
            "target_channel_id": self.target_channel_id,
            "mutation_payload": self.mutation_payload,
            "expected_trap_predicate": self.expected_trap_predicate,
            "is_trapped": self.is_trapped,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ByzantineFuzzVector:
        instance = cls(
            vector_id=data["vector_id"],
            target_channel_id=data["target_channel_id"],
            mutation_payload=data["mutation_payload"],
            expected_trap_predicate=data.get("expected_trap_predicate", "is_trapped == True"),
            is_trapped=bool(data.get("is_trapped", False)),
        )
        instance.validate_invariants()
        return instance


# =========================================================================
# 17. FormalProofArtifact
# =========================================================================
@dataclass
class FormalProofArtifact:
    """SMT solver bridge output certifying category-theoretic contract composition."""
    proof_id: str
    contract_id: str
    verb_morphism: str
    solver_engine: str
    solver_result: SolverResult
    proof_tree_repr: str
    counter_example: Optional[str] = None

    def validate_invariants(self) -> None:
        if self.solver_result == SolverResult.UNSAT and len(self.proof_tree_repr.strip()) == 0:
            raise DomainInvariantViolation(
                "UNSAT solver result requires a non-empty proof_tree_repr certifying validity."
            )
        if self.solver_result == SolverResult.SAT and not self.counter_example:
            # SAT indicates a counter-example to an invariant formula
            pass

    def to_dict(self) -> Dict[str, Any]:
        return {
            "proof_id": self.proof_id,
            "contract_id": self.contract_id,
            "verb_morphism": self.verb_morphism,
            "solver_engine": self.solver_engine,
            "solver_result": self.solver_result.value,
            "proof_tree_repr": self.proof_tree_repr,
            "counter_example": self.counter_example,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> FormalProofArtifact:
        instance = cls(
            proof_id=data["proof_id"],
            contract_id=data["contract_id"],
            verb_morphism=data["verb_morphism"],
            solver_engine=data.get("solver_engine", "NativeSMTProver"),
            solver_result=SolverResult(data["solver_result"]),
            proof_tree_repr=data.get("proof_tree_repr", ""),
            counter_example=data.get("counter_example"),
        )
        instance.validate_invariants()
        return instance


# =========================================================================
# 18. FunctorialUndoCheckpoint
# =========================================================================
@dataclass
class FunctorialUndoCheckpoint:
    """Snapshot for deterministic 1-tap Functorial Undo / Calibrated Unwind."""
    checkpoint_id: str
    step_index: int
    statechart_snapshot_hash: str
    context_delta: Dict[str, Any]
    erased_bits_to_revert: int

    def validate_invariants(self) -> None:
        if self.step_index < 0:
            raise DomainInvariantViolation(f"step_index cannot be negative, got {self.step_index}")
        if self.erased_bits_to_revert < 0:
            raise DomainInvariantViolation(
                f"erased_bits_to_revert cannot be negative, got {self.erased_bits_to_revert}"
            )
        if len(self.statechart_snapshot_hash) != 64:
            raise DomainInvariantViolation("statechart_snapshot_hash must be 64-char SHA-256.")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "checkpoint_id": self.checkpoint_id,
            "step_index": self.step_index,
            "statechart_snapshot_hash": self.statechart_snapshot_hash,
            "context_delta": self.context_delta,
            "erased_bits_to_revert": self.erased_bits_to_revert,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> FunctorialUndoCheckpoint:
        instance = cls(
            checkpoint_id=data["checkpoint_id"],
            step_index=int(data["step_index"]),
            statechart_snapshot_hash=data["statechart_snapshot_hash"],
            context_delta=dict(data.get("context_delta", {})),
            erased_bits_to_revert=int(data["erased_bits_to_revert"]),
        )
        instance.validate_invariants()
        return instance
