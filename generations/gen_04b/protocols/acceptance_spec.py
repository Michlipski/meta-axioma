"""Generation 4b Acceptance Specification Intermediate Representation (`protocols/acceptance_spec.py`).

Enforces:
- [SPEC-G4B-RESEARCH-001] Machine-Readable Acceptance Contracts for Research & Downstream Enclaves.
- [L1-G4B-001] Service-Oriented Sovereign Mesh Protocol Standardization.
- [L1-G4B-002] Zero-Code Research Tool Boundary.
- [INV-G4B-CAUSAL-001] Physical Disk Grounding & Anti-Tautology Falsification Schema.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
import hashlib
import json
from typing import Any, Dict, List, Optional


class AcceptanceProtocolViolation(Exception):
    """Raised when an AcceptanceSpecIR or FalsificationVector violates invariant rules."""
    pass


class MutationType(str, Enum):
    """Permitted physical mutation primitives for non-tautological test falsification."""
    COMMENT_OUT = "COMMENT_OUT"
    RETURN_EMPTY = "RETURN_EMPTY"
    INVERT_CONDITION = "INVERT_CONDITION"


class DomainArchetype(str, Enum):
    """Application and system archetypes with standardized operational constraint profiles."""
    WEB_CANVAS_INTERACTIVE = "WEB_CANVAS_INTERACTIVE"
    DISTRIBUTED_MESH_BACKEND = "DISTRIBUTED_MESH_BACKEND"
    CLI_SYSTEM_TOOL = "CLI_SYSTEM_TOOL"
    FORMAL_VERIFICATION_KERNEL = "FORMAL_VERIFICATION_KERNEL"
    CUSTOM = "CUSTOM"


@dataclass(frozen=True)
class FalsificationVector:
    """Formal definition of a physical defect injection to prove test non-tautology.
    
    When executed by an audit engine, this mutation must cause test suites to fail
    with the expected exception, proving that the verification sink is not tautological.
    """
    vector_id: str
    target_file_relative_path: str
    target_symbol_or_pattern: str
    mutation_type: str
    expected_failure_exception: str
    reversion_witness_required: bool = True
    description: Optional[str] = None

    def validate_invariants(self) -> None:
        if not self.vector_id or not self.vector_id.strip():
            raise AcceptanceProtocolViolation("vector_id must not be empty.")
        if not self.target_file_relative_path or not self.target_file_relative_path.strip():
            raise AcceptanceProtocolViolation("target_file_relative_path must not be empty.")
        if not self.target_symbol_or_pattern or not self.target_symbol_or_pattern.strip():
            raise AcceptanceProtocolViolation("target_symbol_or_pattern must not be empty.")
        
        valid_mutations = {m.value for m in MutationType}
        if self.mutation_type not in valid_mutations:
            raise AcceptanceProtocolViolation(
                f"Invalid mutation_type '{self.mutation_type}'. Permitted types: {sorted(valid_mutations)}"
            )
            
        if not self.expected_failure_exception or not self.expected_failure_exception.strip():
            raise AcceptanceProtocolViolation("expected_failure_exception must not be empty.")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "vector_id": self.vector_id,
            "target_file_relative_path": self.target_file_relative_path,
            "target_symbol_or_pattern": self.target_symbol_or_pattern,
            "mutation_type": self.mutation_type,
            "expected_failure_exception": self.expected_failure_exception,
            "reversion_witness_required": self.reversion_witness_required,
            "description": self.description,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> FalsificationVector:
        instance = cls(
            vector_id=data["vector_id"],
            target_file_relative_path=data["target_file_relative_path"],
            target_symbol_or_pattern=data["target_symbol_or_pattern"],
            mutation_type=data["mutation_type"],
            expected_failure_exception=data["expected_failure_exception"],
            reversion_witness_required=bool(data.get("reversion_witness_required", True)),
            description=data.get("description"),
        )
        instance.validate_invariants()
        return instance


@dataclass(frozen=True)
class AcceptanceSpecIR:
    """Machine-readable contract defining empirical requirements for downstream synthesis and audit.
    
    Emitted by Research Service (192.168.40.10) alongside project proposals.
    Ingested by Builder Enclave for AST adherence and Audit Enclave for mechanical gate certification.
    """
    spec_id: str
    feature_name: str
    target_enclave_path: str
    domain_archetype: str = DomainArchetype.CUSTOM.value
    required_runtimes: List[str] = field(default_factory=list)
    banned_ast_patterns: List[Dict[str, str]] = field(default_factory=list)
    falsification_vectors: List[FalsificationVector] = field(default_factory=list)
    max_latency_per_step_ms: float = 200.0
    zero_console_panics_required: bool = True
    min_statechart_coverage_pct: float = 90.0
    telemetry_digest_required: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

    def validate_invariants(self) -> None:
        if not self.spec_id or not self.spec_id.strip():
            raise AcceptanceProtocolViolation("spec_id must not be empty.")
        if not self.feature_name or not self.feature_name.strip():
            raise AcceptanceProtocolViolation("feature_name must not be empty.")
        if not self.target_enclave_path or not self.target_enclave_path.strip():
            raise AcceptanceProtocolViolation("target_enclave_path must not be empty.")
        if self.max_latency_per_step_ms <= 0.0:
            raise AcceptanceProtocolViolation("max_latency_per_step_ms must be strictly positive.")
        if not (0.0 <= self.min_statechart_coverage_pct <= 100.0):
            raise AcceptanceProtocolViolation("min_statechart_coverage_pct must be between 0.0 and 100.0.")

        valid_archetypes = {a.value for a in DomainArchetype}
        if self.domain_archetype not in valid_archetypes:
            raise AcceptanceProtocolViolation(
                f"Invalid domain_archetype '{self.domain_archetype}'. Permitted: {sorted(valid_archetypes)}"
            )

        for pattern_entry in self.banned_ast_patterns:
            if not isinstance(pattern_entry, dict):
                raise AcceptanceProtocolViolation("Each banned_ast_pattern must be a dictionary.")
            if "pattern" not in pattern_entry or not pattern_entry["pattern"].strip():
                raise AcceptanceProtocolViolation("banned_ast_pattern missing non-empty 'pattern' key.")
            if "reason" not in pattern_entry or not pattern_entry["reason"].strip():
                raise AcceptanceProtocolViolation("banned_ast_pattern missing non-empty 'reason' key.")

        for vector in self.falsification_vectors:
            vector.validate_invariants()

    def compute_spec_hash(self) -> str:
        """Computes deterministic 64-character SHA-256 digest of normalized JSON representation."""
        raw_json = json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(raw_json.encode("utf-8")).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "spec_id": self.spec_id,
            "feature_name": self.feature_name,
            "target_enclave_path": self.target_enclave_path,
            "domain_archetype": self.domain_archetype,
            "required_runtimes": list(self.required_runtimes),
            "banned_ast_patterns": [dict(p) for p in self.banned_ast_patterns],
            "falsification_vectors": [
                v.to_dict() if hasattr(v, "to_dict") else v
                for v in self.falsification_vectors
            ],
            "max_latency_per_step_ms": self.max_latency_per_step_ms,
            "zero_console_panics_required": self.zero_console_panics_required,
            "min_statechart_coverage_pct": self.min_statechart_coverage_pct,
            "telemetry_digest_required": self.telemetry_digest_required,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> AcceptanceSpecIR:
        falsification_vectors = [
            v if isinstance(v, FalsificationVector) else FalsificationVector.from_dict(v)
            for v in data.get("falsification_vectors", [])
        ]
        instance = cls(
            spec_id=data["spec_id"],
            feature_name=data["feature_name"],
            target_enclave_path=data["target_enclave_path"],
            domain_archetype=data.get("domain_archetype", DomainArchetype.CUSTOM.value),
            required_runtimes=list(data.get("required_runtimes", [])),
            banned_ast_patterns=list(data.get("banned_ast_patterns", [])),
            falsification_vectors=falsification_vectors,
            max_latency_per_step_ms=float(data.get("max_latency_per_step_ms", 200.0)),
            zero_console_panics_required=bool(data.get("zero_console_panics_required", True)),
            min_statechart_coverage_pct=float(data.get("min_statechart_coverage_pct", 90.0)),
            telemetry_digest_required=bool(data.get("telemetry_digest_required", True)),
            metadata=dict(data.get("metadata", {})),
        )
        instance.validate_invariants()
        return instance
