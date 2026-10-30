"""Generation 4b Domain Models & Typed Nouns (`soc_g4b_builder`).

Enforces:
- [L1-G4B-001] Service-Oriented Sovereign Mesh Protocol Standardization.
- [L1-G3B-011] Universal Compositional Contract IR & Domain Invariants.
- [L1-002] Statechart Determinism & Functorial Undo Invariant.
- Complete specification of all 16 Domain Nouns and Enums with algebraic validation.
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


# =========================================================================
# Enumerations (4 Core Enums)
# =========================================================================

class TaskExecutionStatus(str, Enum):
    """Execution lifecycle status of builder tasks and fractal nodes."""
    PENDING = "PENDING"
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    HEALING = "HEALING"
    CANCELLED = "CANCELLED"
    REROUTED = "REROUTED"


class DiagnosticSeverity(str, Enum):
    """Severity classification of AST and hermetic boundary diagnostics."""
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    FATAL = "FATAL"
    SECURITY_VIOLATION = "SECURITY_VIOLATION"


class ASTNodeType(str, Enum):
    """Classification of AST and Interface Skeleton nodes."""
    MODULE = "MODULE"
    CLASS_DEF = "CLASS_DEF"
    FUNCTION_DEF = "FUNCTION_DEF"
    ASYNC_FUNCTION_DEF = "ASYNC_FUNCTION_DEF"
    IMPORT = "IMPORT"
    EXPR = "EXPR"
    ASSIGN = "ASSIGN"
    CONTRACT_SPEC = "CONTRACT_SPEC"
    INVARIANT_ASSERT = "INVARIANT_ASSERT"


class LeaseAllocationStatus(str, Enum):
    """Lifecycle status of hierarchical thermodynamic budget leases."""
    ALLOCATED = "ALLOCATED"
    ACTIVE = "ACTIVE"
    SETTLED = "SETTLED"
    REVOKED = "REVOKED"
    EXHAUSTED = "EXHAUSTED"
    UNWOUND = "UNWOUND"


# =========================================================================
# 1. BuilderExecutionBundle
# =========================================================================
@dataclass
class BuilderExecutionBundle:
    """The master execution manifest coordinating sovereign code synthesis."""
    bundle_id: str
    target_soc_id: str
    research_bundle_hash: str
    total_budget_tokens: int
    protected_capital_tokens: int
    exploratory_capital_tokens: int
    emitted_module_count: int = 0
    status: TaskExecutionStatus = TaskExecutionStatus.PENDING
    created_at_unix_ms: int = field(default_factory=lambda: int(time.time() * 1000))
    metadata: Dict[str, Any] = field(default_factory=dict)

    def validate_invariants(self) -> None:
        if not self.bundle_id:
            raise DomainInvariantViolation("bundle_id must not be empty.")
        if not self.target_soc_id:
            raise DomainInvariantViolation("target_soc_id must not be empty.")
        if len(self.research_bundle_hash) != 64:
            raise DomainInvariantViolation(
                f"research_bundle_hash must be a 64-char SHA-256 hex string, got {len(self.research_bundle_hash)}"
            )
        if self.total_budget_tokens <= 0:
            raise DomainInvariantViolation("total_budget_tokens must be strictly positive.")
        
        # 60/40 Thermodynamic Capital Invariant
        expected_min_protected = int(self.total_budget_tokens * 0.40)
        if self.protected_capital_tokens < expected_min_protected:
            raise DomainInvariantViolation(
                f"protected_capital_tokens ({self.protected_capital_tokens}) violates 40% floor ({expected_min_protected})."
            )
        if self.exploratory_capital_tokens > (self.total_budget_tokens - self.protected_capital_tokens):
            raise DomainInvariantViolation(
                f"exploratory_capital_tokens ({self.exploratory_capital_tokens}) exceeds remaining exploratory ceiling."
            )
        if self.emitted_module_count < 0:
            raise DomainInvariantViolation("emitted_module_count cannot be negative.")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "bundle_id": self.bundle_id,
            "target_soc_id": self.target_soc_id,
            "research_bundle_hash": self.research_bundle_hash,
            "total_budget_tokens": self.total_budget_tokens,
            "protected_capital_tokens": self.protected_capital_tokens,
            "exploratory_capital_tokens": self.exploratory_capital_tokens,
            "emitted_module_count": self.emitted_module_count,
            "status": self.status.value,
            "created_at_unix_ms": self.created_at_unix_ms,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> BuilderExecutionBundle:
        instance = cls(
            bundle_id=data["bundle_id"],
            target_soc_id=data["target_soc_id"],
            research_bundle_hash=data["research_bundle_hash"],
            total_budget_tokens=int(data["total_budget_tokens"]),
            protected_capital_tokens=int(data["protected_capital_tokens"]),
            exploratory_capital_tokens=int(data["exploratory_capital_tokens"]),
            emitted_module_count=int(data.get("emitted_module_count", 0)),
            status=TaskExecutionStatus(data.get("status", TaskExecutionStatus.PENDING.value)),
            created_at_unix_ms=int(data.get("created_at_unix_ms", int(time.time() * 1000))),
            metadata=dict(data.get("metadata", {})),
        )
        instance.validate_invariants()
        return instance


# =========================================================================
# 2. FractalTreeNode
# =========================================================================
@dataclass
class FractalTreeNode:
    """A bounded node within the hierarchical subagent execution tree."""
    node_id: str
    parent_id: Optional[str]
    depth: int
    child_ids: List[str] = field(default_factory=list)
    assigned_persona_role: str = ""
    task_description: str = ""
    allocated_lease_tokens: int = 0
    spent_tokens: int = 0
    status: TaskExecutionStatus = TaskExecutionStatus.PENDING
    emitted_artifacts: List[str] = field(default_factory=list)
    merkle_node_hash: str = ""

    def validate_invariants(self) -> None:
        if not self.node_id:
            raise DomainInvariantViolation("node_id must not be empty.")
        if not (0 <= self.depth <= 4):
            raise DomainInvariantViolation(
                f"[Layer A Violation] FractalTreeNode depth must be in [0, 4], got {self.depth}"
            )
        if len(self.child_ids) > 5:
            raise DomainInvariantViolation(
                f"[Layer A Violation] FractalTreeNode branching factor b <= 5 exceeded: got {len(self.child_ids)}"
            )
        if self.allocated_lease_tokens < 0:
            raise DomainInvariantViolation("allocated_lease_tokens cannot be negative.")
        if self.spent_tokens < 0:
            raise DomainInvariantViolation("spent_tokens cannot be negative.")

    def compute_merkle_hash(self) -> str:
        payload = f"{self.node_id}:{self.parent_id}:{self.depth}:{self.status.value}:{self.spent_tokens}:{','.join(self.child_ids)}:{','.join(self.emitted_artifacts)}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_id": self.node_id,
            "parent_id": self.parent_id,
            "depth": self.depth,
            "child_ids": self.child_ids,
            "assigned_persona_role": self.assigned_persona_role,
            "task_description": self.task_description,
            "allocated_lease_tokens": self.allocated_lease_tokens,
            "spent_tokens": self.spent_tokens,
            "status": self.status.value,
            "emitted_artifacts": self.emitted_artifacts,
            "merkle_node_hash": self.merkle_node_hash or self.compute_merkle_hash(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> FractalTreeNode:
        instance = cls(
            node_id=data["node_id"],
            parent_id=data.get("parent_id"),
            depth=int(data["depth"]),
            child_ids=list(data.get("child_ids", [])),
            assigned_persona_role=data.get("assigned_persona_role", ""),
            task_description=data.get("task_description", ""),
            allocated_lease_tokens=int(data.get("allocated_lease_tokens", 0)),
            spent_tokens=int(data.get("spent_tokens", 0)),
            status=TaskExecutionStatus(data.get("status", TaskExecutionStatus.PENDING.value)),
            emitted_artifacts=list(data.get("emitted_artifacts", [])),
            merkle_node_hash=data.get("merkle_node_hash", ""),
        )
        instance.validate_invariants()
        return instance


# =========================================================================
# 3. HierarchicalBudgetLease
# =========================================================================
@dataclass
class HierarchicalBudgetLease:
    """Thermodynamic lease managing token allocation and decay down the fractal tree."""
    lease_id: str
    node_id: str
    parent_lease_id: Optional[str] = None
    allocated_tokens: int = 0
    decay_rate_lambda: float = 0.80
    remaining_tokens: int = 0
    landauer_bits_erased: int = 0
    status: LeaseAllocationStatus = LeaseAllocationStatus.ALLOCATED
    allocated_at_unix_ms: int = field(default_factory=lambda: int(time.time() * 1000))

    def validate_invariants(self) -> None:
        if not self.lease_id:
            raise DomainInvariantViolation("lease_id must not be empty.")
        if not self.node_id:
            raise DomainInvariantViolation("node_id must not be empty.")
        if not (0.0 < self.decay_rate_lambda <= 0.80):
            raise DomainInvariantViolation(
                f"decay_rate_lambda must be in (0.0, 0.80], got {self.decay_rate_lambda}"
            )
        if self.allocated_tokens < 0:
            raise DomainInvariantViolation("allocated_tokens cannot be negative.")
        if self.remaining_tokens < 0:
            raise DomainInvariantViolation("remaining_tokens cannot be negative.")
        if self.remaining_tokens > self.allocated_tokens:
            raise DomainInvariantViolation("remaining_tokens cannot exceed allocated_tokens.")
        if self.landauer_bits_erased < 0:
            raise DomainInvariantViolation("landauer_bits_erased cannot be negative.")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "lease_id": self.lease_id,
            "node_id": self.node_id,
            "parent_lease_id": self.parent_lease_id,
            "allocated_tokens": self.allocated_tokens,
            "decay_rate_lambda": self.decay_rate_lambda,
            "remaining_tokens": self.remaining_tokens,
            "landauer_bits_erased": self.landauer_bits_erased,
            "status": self.status.value,
            "allocated_at_unix_ms": self.allocated_at_unix_ms,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> HierarchicalBudgetLease:
        instance = cls(
            lease_id=data["lease_id"],
            node_id=data["node_id"],
            parent_lease_id=data.get("parent_lease_id"),
            allocated_tokens=int(data.get("allocated_tokens", 0)),
            decay_rate_lambda=float(data.get("decay_rate_lambda", 0.80)),
            remaining_tokens=int(data.get("remaining_tokens", 0)),
            landauer_bits_erased=int(data.get("landauer_bits_erased", 0)),
            status=LeaseAllocationStatus(data.get("status", LeaseAllocationStatus.ALLOCATED.value)),
            allocated_at_unix_ms=int(data.get("allocated_at_unix_ms", int(time.time() * 1000))),
        )
        instance.validate_invariants()
        return instance


# =========================================================================
# 4. ASTSkeletonSnapshot
# =========================================================================
@dataclass
class ASTSkeletonSnapshot:
    """Interface skeleton stripped of function/class bodies for prompt payload minimization."""
    snapshot_id: str
    source_module_path: str
    symbol_urn: str
    skeleton_code: str
    stripped_byte_count: int
    preserved_signatures: List[str] = field(default_factory=list)
    estimated_bpe_tokens: int = 0
    created_at_unix_ms: int = field(default_factory=lambda: int(time.time() * 1000))

    def validate_invariants(self) -> None:
        if not self.snapshot_id:
            raise DomainInvariantViolation("snapshot_id must not be empty.")
        if not self.source_module_path:
            raise DomainInvariantViolation("source_module_path must not be empty.")
        if not self.symbol_urn.startswith("urn:axioma:g4b:"):
            raise DomainInvariantViolation(
                f"symbol_urn must conform to urn:axioma:g4b:..., got {self.symbol_urn}"
            )
        if not self.skeleton_code:
            raise DomainInvariantViolation("skeleton_code must not be empty.")
        if self.estimated_bpe_tokens > 4096:
            raise DomainInvariantViolation(
                f"[Layer A Violation] Interface skeleton estimated tokens ({self.estimated_bpe_tokens}) exceeds 4,096 BPE limit."
            )
        if self.stripped_byte_count < 0:
            raise DomainInvariantViolation("stripped_byte_count cannot be negative.")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "snapshot_id": self.snapshot_id,
            "source_module_path": self.source_module_path,
            "symbol_urn": self.symbol_urn,
            "skeleton_code": self.skeleton_code,
            "stripped_byte_count": self.stripped_byte_count,
            "preserved_signatures": self.preserved_signatures,
            "estimated_bpe_tokens": self.estimated_bpe_tokens,
            "created_at_unix_ms": self.created_at_unix_ms,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ASTSkeletonSnapshot:
        instance = cls(
            snapshot_id=data["snapshot_id"],
            source_module_path=data["source_module_path"],
            symbol_urn=data["symbol_urn"],
            skeleton_code=data["skeleton_code"],
            stripped_byte_count=int(data.get("stripped_byte_count", 0)),
            preserved_signatures=list(data.get("preserved_signatures", [])),
            estimated_bpe_tokens=int(data.get("estimated_bpe_tokens", 0)),
            created_at_unix_ms=int(data.get("created_at_unix_ms", int(time.time() * 1000))),
        )
        instance.validate_invariants()
        return instance


# =========================================================================
# 5. DiagnosticTuple
# =========================================================================
@dataclass
class DiagnosticTuple:
    """Byte-indexed surgical error diagnostic enabling automated AST node patching."""
    diagnostic_id: str
    file_path: str
    severity: DiagnosticSeverity
    start_byte: int
    end_byte: int
    line_number: int
    column_number: int
    rule_code: str
    message: str
    suggested_patch: Optional[str] = None

    def validate_invariants(self) -> None:
        if not self.diagnostic_id:
            raise DomainInvariantViolation("diagnostic_id must not be empty.")
        if not self.file_path:
            raise DomainInvariantViolation("file_path must not be empty.")
        if self.start_byte < 0:
            raise DomainInvariantViolation("start_byte cannot be negative.")
        if self.end_byte < self.start_byte:
            raise DomainInvariantViolation(
                f"end_byte ({self.end_byte}) cannot precede start_byte ({self.start_byte})."
            )
        if self.line_number < 1:
            raise DomainInvariantViolation("line_number must be >= 1.")
        if self.column_number < 0:
            raise DomainInvariantViolation("column_number cannot be negative.")
        if not self.rule_code:
            raise DomainInvariantViolation("rule_code must not be empty.")
        if not self.message:
            raise DomainInvariantViolation("message must not be empty.")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "diagnostic_id": self.diagnostic_id,
            "file_path": self.file_path,
            "severity": self.severity.value,
            "start_byte": self.start_byte,
            "end_byte": self.end_byte,
            "line_number": self.line_number,
            "column_number": self.column_number,
            "rule_code": self.rule_code,
            "message": self.message,
            "suggested_patch": self.suggested_patch,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> DiagnosticTuple:
        instance = cls(
            diagnostic_id=data["diagnostic_id"],
            file_path=data["file_path"],
            severity=DiagnosticSeverity(data["severity"]),
            start_byte=int(data["start_byte"]),
            end_byte=int(data["end_byte"]),
            line_number=int(data["line_number"]),
            column_number=int(data["column_number"]),
            rule_code=data["rule_code"],
            message=data["message"],
            suggested_patch=data.get("suggested_patch"),
        )
        instance.validate_invariants()
        return instance


# =========================================================================
# 6. HermeticLinterReport
# =========================================================================
@dataclass
class HermeticLinterReport:
    """Compile-time boundary audit report for hermetic security guarantees."""
    report_id: str
    module_path: str
    passed: bool
    violations: List[DiagnosticTuple] = field(default_factory=list)
    loopback_prohibited_checks: int = 0
    sys_path_tampering_checks: int = 0
    filesystem_confinement_checks: int = 0
    checked_at_unix_ms: int = field(default_factory=lambda: int(time.time() * 1000))

    def validate_invariants(self) -> None:
        if not self.report_id:
            raise DomainInvariantViolation("report_id must not be empty.")
        if not self.module_path:
            raise DomainInvariantViolation("module_path must not be empty.")
        has_fatal_or_security = any(
            v.severity in (DiagnosticSeverity.ERROR, DiagnosticSeverity.FATAL, DiagnosticSeverity.SECURITY_VIOLATION)
            for v in self.violations
        )
        if self.passed and has_fatal_or_security:
            raise DomainInvariantViolation(
                "HermeticLinterReport marked passed=True despite presence of error/fatal/security violations."
            )
        if not self.passed and not self.violations:
            raise DomainInvariantViolation(
                "HermeticLinterReport marked passed=False but zero violations were recorded."
            )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "report_id": self.report_id,
            "module_path": self.module_path,
            "passed": self.passed,
            "violations": [v.to_dict() for v in self.violations],
            "loopback_prohibited_checks": self.loopback_prohibited_checks,
            "sys_path_tampering_checks": self.sys_path_tampering_checks,
            "filesystem_confinement_checks": self.filesystem_confinement_checks,
            "checked_at_unix_ms": self.checked_at_unix_ms,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> HermeticLinterReport:
        instance = cls(
            report_id=data["report_id"],
            module_path=data["module_path"],
            passed=bool(data["passed"]),
            violations=[DiagnosticTuple.from_dict(v) for v in data.get("violations", [])],
            loopback_prohibited_checks=int(data.get("loopback_prohibited_checks", 0)),
            sys_path_tampering_checks=int(data.get("sys_path_tampering_checks", 0)),
            filesystem_confinement_checks=int(data.get("filesystem_confinement_checks", 0)),
            checked_at_unix_ms=int(data.get("checked_at_unix_ms", int(time.time() * 1000))),
        )
        instance.validate_invariants()
        return instance


# =========================================================================
# 7. DynamicPersonaManifest
# =========================================================================
@dataclass
class DynamicPersonaManifest:
    """Specialized dynamic subagent persona synthesized at runtime via define_subagent."""
    persona_id: str
    role_title: str
    cognitive_role: str
    model_tier: str
    system_prompt: str
    governing_axioms: List[str] = field(default_factory=list)
    banned_antipatterns: List[str] = field(default_factory=list)
    created_at_unix_ms: int = field(default_factory=lambda: int(time.time() * 1000))

    def validate_invariants(self) -> None:
        if not self.persona_id:
            raise DomainInvariantViolation("persona_id must not be empty.")
        if not self.role_title:
            raise DomainInvariantViolation("role_title must not be empty.")
        if not self.system_prompt:
            raise DomainInvariantViolation("system_prompt must not be empty.")
        if len(self.governing_axioms) < 1:
            raise DomainInvariantViolation("Dynamic persona must bind to at least one governing axiom.")
        if self.model_tier not in ("flash", "pro", "flash_lite", "inherit"):
            raise DomainInvariantViolation(
                f"Invalid model_tier: '{self.model_tier}'. Expected one of: flash, pro, flash_lite, inherit"
            )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "persona_id": self.persona_id,
            "role_title": self.role_title,
            "cognitive_role": self.cognitive_role,
            "model_tier": self.model_tier,
            "system_prompt": self.system_prompt,
            "governing_axioms": self.governing_axioms,
            "banned_antipatterns": self.banned_antipatterns,
            "created_at_unix_ms": self.created_at_unix_ms,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> DynamicPersonaManifest:
        instance = cls(
            persona_id=data["persona_id"],
            role_title=data["role_title"],
            cognitive_role=data.get("cognitive_role", ""),
            model_tier=data.get("model_tier", "flash"),
            system_prompt=data["system_prompt"],
            governing_axioms=list(data.get("governing_axioms", [])),
            banned_antipatterns=list(data.get("banned_antipatterns", [])),
            created_at_unix_ms=int(data.get("created_at_unix_ms", int(time.time() * 1000))),
        )
        instance.validate_invariants()
        return instance


# =========================================================================
# 8. SubtreeHealingEnvelope
# =========================================================================
@dataclass
class SubtreeHealingEnvelope:
    """Quarantine and self-healing envelope isolating failed fractal branches."""
    envelope_id: str
    failing_node_id: str
    root_cause_diagnostic: DiagnosticTuple
    healing_strategy: str
    quarantined_child_ids: List[str] = field(default_factory=list)
    reserved_healing_tokens: int = 0
    resolved: bool = False

    def validate_invariants(self) -> None:
        if not self.envelope_id:
            raise DomainInvariantViolation("envelope_id must not be empty.")
        if not self.failing_node_id:
            raise DomainInvariantViolation("failing_node_id must not be empty.")
        if not self.healing_strategy:
            raise DomainInvariantViolation("healing_strategy must not be empty.")
        if self.reserved_healing_tokens < 0:
            raise DomainInvariantViolation("reserved_healing_tokens cannot be negative.")
        self.root_cause_diagnostic.validate_invariants()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "envelope_id": self.envelope_id,
            "failing_node_id": self.failing_node_id,
            "root_cause_diagnostic": self.root_cause_diagnostic.to_dict(),
            "healing_strategy": self.healing_strategy,
            "quarantined_child_ids": self.quarantined_child_ids,
            "reserved_healing_tokens": self.reserved_healing_tokens,
            "resolved": self.resolved,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> SubtreeHealingEnvelope:
        instance = cls(
            envelope_id=data["envelope_id"],
            failing_node_id=data["failing_node_id"],
            root_cause_diagnostic=DiagnosticTuple.from_dict(data["root_cause_diagnostic"]),
            healing_strategy=data["healing_strategy"],
            quarantined_child_ids=list(data.get("quarantined_child_ids", [])),
            reserved_healing_tokens=int(data.get("reserved_healing_tokens", 0)),
            resolved=bool(data.get("resolved", False)),
        )
        instance.validate_invariants()
        return instance


# =========================================================================
# 9. QuineDaughterManifest
# =========================================================================
@dataclass
class QuineDaughterManifest:
    """Certification record of an isolated, self-hosting daughter compiler daughter."""
    manifest_id: str
    daughter_generation_id: str
    sandbox_root_dir: str
    emitted_compiler_files: List[str] = field(default_factory=list)
    daughter_hash: str = ""
    boot_success: bool = False
    self_hosting_certified: bool = False
    timestamp_unix_ms: int = field(default_factory=lambda: int(time.time() * 1000))

    def validate_invariants(self) -> None:
        if not self.manifest_id:
            raise DomainInvariantViolation("manifest_id must not be empty.")
        if not self.daughter_generation_id:
            raise DomainInvariantViolation("daughter_generation_id must not be empty.")
        if not self.sandbox_root_dir:
            raise DomainInvariantViolation("sandbox_root_dir must not be empty.")
        if len(self.emitted_compiler_files) < 1:
            raise DomainInvariantViolation("Quine daughter requires at least 1 emitted compiler source file.")
        if len(self.daughter_hash) != 64:
            raise DomainInvariantViolation(
                f"daughter_hash must be a 64-char SHA-256 hash, got {len(self.daughter_hash)}"
            )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "manifest_id": self.manifest_id,
            "daughter_generation_id": self.daughter_generation_id,
            "sandbox_root_dir": self.sandbox_root_dir,
            "emitted_compiler_files": self.emitted_compiler_files,
            "daughter_hash": self.daughter_hash,
            "boot_success": self.boot_success,
            "self_hosting_certified": self.self_hosting_certified,
            "timestamp_unix_ms": self.timestamp_unix_ms,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> QuineDaughterManifest:
        instance = cls(
            manifest_id=data["manifest_id"],
            daughter_generation_id=data["daughter_generation_id"],
            sandbox_root_dir=data["sandbox_root_dir"],
            emitted_compiler_files=list(data.get("emitted_compiler_files", [])),
            daughter_hash=data.get("daughter_hash", ""),
            boot_success=bool(data.get("boot_success", False)),
            self_hosting_certified=bool(data.get("self_hosting_certified", False)),
            timestamp_unix_ms=int(data.get("timestamp_unix_ms", int(time.time() * 1000))),
        )
        instance.validate_invariants()
        return instance


# =========================================================================
# 10. RFCSubmissionRecord
# =========================================================================
@dataclass
class RFCSubmissionRecord:
    """Historical ledger entry for SpecAdjustmentRequest and SpecAmendment transactions."""
    rfc_record_id: str
    request_id: str
    target_symbol_urn: str
    bottleneck_type: str
    proposed_delta: str
    submission_status: str
    associated_amendment_id: Optional[str] = None
    counter_proof_id: Optional[str] = None
    submitted_at_unix_ms: int = field(default_factory=lambda: int(time.time() * 1000))

    def validate_invariants(self) -> None:
        if not self.rfc_record_id:
            raise DomainInvariantViolation("rfc_record_id must not be empty.")
        if not self.request_id:
            raise DomainInvariantViolation("request_id must not be empty.")
        if not self.target_symbol_urn.startswith("urn:axioma:g4b:"):
            raise DomainInvariantViolation(
                f"target_symbol_urn must conform to urn:axioma:g4b:..., got {self.target_symbol_urn}"
            )
        if not self.proposed_delta:
            raise DomainInvariantViolation("proposed_delta must not be empty.")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "rfc_record_id": self.rfc_record_id,
            "request_id": self.request_id,
            "target_symbol_urn": self.target_symbol_urn,
            "bottleneck_type": self.bottleneck_type,
            "proposed_delta": self.proposed_delta,
            "submission_status": self.submission_status,
            "associated_amendment_id": self.associated_amendment_id,
            "counter_proof_id": self.counter_proof_id,
            "submitted_at_unix_ms": self.submitted_at_unix_ms,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> RFCSubmissionRecord:
        instance = cls(
            rfc_record_id=data["rfc_record_id"],
            request_id=data["request_id"],
            target_symbol_urn=data["target_symbol_urn"],
            bottleneck_type=data["bottleneck_type"],
            proposed_delta=data["proposed_delta"],
            submission_status=data["submission_status"],
            associated_amendment_id=data.get("associated_amendment_id"),
            counter_proof_id=data.get("counter_proof_id"),
            submitted_at_unix_ms=int(data.get("submitted_at_unix_ms", int(time.time() * 1000))),
        )
        instance.validate_invariants()
        return instance


# =========================================================================
# 11. MerkleTreeRootAttestation
# =========================================================================
@dataclass
class MerkleTreeRootAttestation:
    """Cryptographic tamper-evident Merkle-tree root certifying synthesized artifacts."""
    attestation_id: str
    merkle_root: str
    leaf_count: int
    leaf_hashes: List[str] = field(default_factory=list)
    builder_signature: str = ""
    certified_at_unix_ms: int = field(default_factory=lambda: int(time.time() * 1000))

    def validate_invariants(self) -> None:
        if not self.attestation_id:
            raise DomainInvariantViolation("attestation_id must not be empty.")
        if len(self.merkle_root) != 64:
            raise DomainInvariantViolation(
                f"merkle_root must be a 64-char SHA-256 hash, got {len(self.merkle_root)}"
            )
        if self.leaf_count <= 0:
            raise DomainInvariantViolation("leaf_count must be strictly positive.")
        if len(self.leaf_hashes) != self.leaf_count:
            raise DomainInvariantViolation(
                f"leaf_hashes count ({len(self.leaf_hashes)}) must equal leaf_count ({self.leaf_count})."
            )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "attestation_id": self.attestation_id,
            "merkle_root": self.merkle_root,
            "leaf_count": self.leaf_count,
            "leaf_hashes": self.leaf_hashes,
            "builder_signature": self.builder_signature,
            "certified_at_unix_ms": self.certified_at_unix_ms,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> MerkleTreeRootAttestation:
        instance = cls(
            attestation_id=data["attestation_id"],
            merkle_root=data["merkle_root"],
            leaf_count=int(data["leaf_count"]),
            leaf_hashes=list(data.get("leaf_hashes", [])),
            builder_signature=data.get("builder_signature", ""),
            certified_at_unix_ms=int(data.get("certified_at_unix_ms", int(time.time() * 1000))),
        )
        instance.validate_invariants()
        return instance


# =========================================================================
# 12. FunctorialUndoCheckpoint
# =========================================================================
@dataclass
class FunctorialUndoCheckpoint:
    """State snapshot register enabling 1-tap reversible unwinding and bit-recovery."""
    checkpoint_id: str
    parent_checkpoint_id: Optional[str] = None
    state_label: str = ""
    state_context: Dict[str, Any] = field(default_factory=dict)
    erased_bits_at_checkpoint: int = 0
    active_node_id: str = ""
    merkle_root: str = ""
    created_at_unix_ms: int = field(default_factory=lambda: int(time.time() * 1000))

    def validate_invariants(self) -> None:
        if not self.checkpoint_id:
            raise DomainInvariantViolation("checkpoint_id must not be empty.")
        if not self.state_label:
            raise DomainInvariantViolation("state_label must not be empty.")
        if self.erased_bits_at_checkpoint < 0:
            raise DomainInvariantViolation("erased_bits_at_checkpoint cannot be negative.")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "checkpoint_id": self.checkpoint_id,
            "parent_checkpoint_id": self.parent_checkpoint_id,
            "state_label": self.state_label,
            "state_context": self.state_context,
            "erased_bits_at_checkpoint": self.erased_bits_at_checkpoint,
            "active_node_id": self.active_node_id,
            "merkle_root": self.merkle_root,
            "created_at_unix_ms": self.created_at_unix_ms,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> FunctorialUndoCheckpoint:
        instance = cls(
            checkpoint_id=data["checkpoint_id"],
            parent_checkpoint_id=data.get("parent_checkpoint_id"),
            state_label=data.get("state_label", ""),
            state_context=dict(data.get("state_context", {})),
            erased_bits_at_checkpoint=int(data.get("erased_bits_at_checkpoint", 0)),
            active_node_id=data.get("active_node_id", ""),
            merkle_root=data.get("merkle_root", ""),
            created_at_unix_ms=int(data.get("created_at_unix_ms", int(time.time() * 1000))),
        )
        instance.validate_invariants()
        return instance


# =========================================================================
# 13. PhysicalDiskWitness
# =========================================================================
@dataclass
class PhysicalDiskWitness:
    """Empirical disk presence and non-zero-byte proof ([NEG-G1B-001])."""
    witness_id: str
    file_path: str
    byte_size: int
    sha256_hash: str
    verified_at_unix_ms: int = field(default_factory=lambda: int(time.time() * 1000))
    is_present: bool = True

    def validate_invariants(self) -> None:
        if not self.witness_id:
            raise DomainInvariantViolation("witness_id must not be empty.")
        if not self.file_path:
            raise DomainInvariantViolation("file_path must not be empty.")
        if self.byte_size <= 0:
            raise DomainInvariantViolation(
                f"[NEG-G1B-001 Violation] byte_size must be strictly positive, got {self.byte_size}"
            )
        if len(self.sha256_hash) != 64:
            raise DomainInvariantViolation(
                f"sha256_hash must be a 64-char hex string, got {len(self.sha256_hash)}"
            )
        if not self.is_present:
            raise DomainInvariantViolation("is_present must be True for PhysicalDiskWitness.")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "witness_id": self.witness_id,
            "file_path": self.file_path,
            "byte_size": self.byte_size,
            "sha256_hash": self.sha256_hash,
            "verified_at_unix_ms": self.verified_at_unix_ms,
            "is_present": self.is_present,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> PhysicalDiskWitness:
        instance = cls(
            witness_id=data["witness_id"],
            file_path=data["file_path"],
            byte_size=int(data["byte_size"]),
            sha256_hash=data["sha256_hash"],
            verified_at_unix_ms=int(data.get("verified_at_unix_ms", int(time.time() * 1000))),
            is_present=bool(data.get("is_present", True)),
        )
        instance.validate_invariants()
        return instance


# =========================================================================
# 14. LeafEmissionEvent
# =========================================================================
@dataclass
class LeafEmissionEvent:
    """Record of physical code leaf emission with disk witness."""
    event_id: str
    leaf_symbol_urn: str
    source_path: str
    disk_witness: PhysicalDiskWitness
    bpe_token_count: int = 0
    emitted_at_unix_ms: int = field(default_factory=lambda: int(time.time() * 1000))

    def validate_invariants(self) -> None:
        if not self.event_id:
            raise DomainInvariantViolation("event_id must not be empty.")
        if not self.leaf_symbol_urn.startswith("urn:axioma:g4b:"):
            raise DomainInvariantViolation(
                f"leaf_symbol_urn must conform to urn:axioma:g4b:..., got {self.leaf_symbol_urn}"
            )
        if not self.source_path:
            raise DomainInvariantViolation("source_path must not be empty.")
        if self.bpe_token_count < 0:
            raise DomainInvariantViolation("bpe_token_count cannot be negative.")
        self.disk_witness.validate_invariants()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "leaf_symbol_urn": self.leaf_symbol_urn,
            "source_path": self.source_path,
            "disk_witness": self.disk_witness.to_dict(),
            "bpe_token_count": self.bpe_token_count,
            "emitted_at_unix_ms": self.emitted_at_unix_ms,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> LeafEmissionEvent:
        instance = cls(
            event_id=data["event_id"],
            leaf_symbol_urn=data["leaf_symbol_urn"],
            source_path=data["source_path"],
            disk_witness=PhysicalDiskWitness.from_dict(data["disk_witness"]),
            bpe_token_count=int(data.get("bpe_token_count", 0)),
            emitted_at_unix_ms=int(data.get("emitted_at_unix_ms", int(time.time() * 1000))),
        )
        instance.validate_invariants()
        return instance


# =========================================================================
# 15. ReactiveVerificationGate
# =========================================================================
@dataclass
class ReactiveVerificationGate:
    """Reactive verification checkpoint evaluating causal leaf validity."""
    gate_id: str
    target_urn: str
    passed: bool
    checks_run: int = 0
    failures: List[str] = field(default_factory=list)
    evaluated_at_unix_ms: int = field(default_factory=lambda: int(time.time() * 1000))

    def validate_invariants(self) -> None:
        if not self.gate_id:
            raise DomainInvariantViolation("gate_id must not be empty.")
        if not self.target_urn.startswith("urn:axioma:g4b:"):
            raise DomainInvariantViolation(
                f"target_urn must conform to urn:axioma:g4b:..., got {self.target_urn}"
            )
        if self.checks_run < 0:
            raise DomainInvariantViolation("checks_run cannot be negative.")
        if self.passed and len(self.failures) > 0:
            raise DomainInvariantViolation(
                f"ReactiveVerificationGate marked passed=True despite failures: {self.failures}"
            )
        if not self.passed and len(self.failures) == 0:
            raise DomainInvariantViolation(
                "ReactiveVerificationGate marked passed=False but zero failures were recorded."
            )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "gate_id": self.gate_id,
            "target_urn": self.target_urn,
            "passed": self.passed,
            "checks_run": self.checks_run,
            "failures": list(self.failures),
            "evaluated_at_unix_ms": self.evaluated_at_unix_ms,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ReactiveVerificationGate:
        instance = cls(
            gate_id=data["gate_id"],
            target_urn=data["target_urn"],
            passed=bool(data["passed"]),
            checks_run=int(data.get("checks_run", 0)),
            failures=list(data.get("failures", [])),
            evaluated_at_unix_ms=int(data.get("evaluated_at_unix_ms", int(time.time() * 1000))),
        )
        instance.validate_invariants()
        return instance


# =========================================================================
# 16. ReactiveAuditReport
# =========================================================================
@dataclass
class ReactiveAuditReport:
    """Audit evaluation ensuring zero-bypass micro-auditing and loopback isolation."""
    report_id: str
    module_path: str
    passed: bool
    diagnostics: List[DiagnosticTuple] = field(default_factory=list)
    loopback_clean: bool = True
    functorial_purity_verified: bool = True
    audited_at_unix_ms: int = field(default_factory=lambda: int(time.time() * 1000))

    def validate_invariants(self) -> None:
        if not self.report_id:
            raise DomainInvariantViolation("report_id must not be empty.")
        if not self.module_path:
            raise DomainInvariantViolation("module_path must not be empty.")
        has_blocking = any(
            d.severity in (DiagnosticSeverity.ERROR, DiagnosticSeverity.FATAL, DiagnosticSeverity.SECURITY_VIOLATION)
            for d in self.diagnostics
        )
        if self.passed and (has_blocking or not self.loopback_clean or not self.functorial_purity_verified):
            raise DomainInvariantViolation(
                "ReactiveAuditReport marked passed=True despite failing invariants."
            )
        if not self.passed and not (has_blocking or not self.loopback_clean or not self.functorial_purity_verified):
            raise DomainInvariantViolation(
                "ReactiveAuditReport marked passed=False but all checks were clean."
            )
        for d in self.diagnostics:
            d.validate_invariants()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "report_id": self.report_id,
            "module_path": self.module_path,
            "passed": self.passed,
            "diagnostics": [d.to_dict() for d in self.diagnostics],
            "loopback_clean": self.loopback_clean,
            "functorial_purity_verified": self.functorial_purity_verified,
            "audited_at_unix_ms": self.audited_at_unix_ms,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ReactiveAuditReport:
        instance = cls(
            report_id=data["report_id"],
            module_path=data["module_path"],
            passed=bool(data["passed"]),
            diagnostics=[DiagnosticTuple.from_dict(d) for d in data.get("diagnostics", [])],
            loopback_clean=bool(data.get("loopback_clean", True)),
            functorial_purity_verified=bool(data.get("functorial_purity_verified", True)),
            audited_at_unix_ms=int(data.get("audited_at_unix_ms", int(time.time() * 1000))),
        )
        instance.validate_invariants()
        return instance


# =========================================================================
# 17. ByzantineChaosReport
# =========================================================================
@dataclass
class ByzantineChaosReport:
    """Report from Byzantine chaos injection & property fuzzing verification."""
    report_id: str
    target_module: str
    chaos_scenarios_tested: int
    passed: bool
    injected_fault_count: int = 0
    recovered_fault_count: int = 0
    chaos_seed: int = 42
    executed_at_unix_ms: int = field(default_factory=lambda: int(time.time() * 1000))

    def validate_invariants(self) -> None:
        if not self.report_id:
            raise DomainInvariantViolation("report_id must not be empty.")
        if not self.target_module:
            raise DomainInvariantViolation("target_module must not be empty.")
        if self.chaos_scenarios_tested < 1:
            raise DomainInvariantViolation("chaos_scenarios_tested must be >= 1.")
        if self.injected_fault_count < 0:
            raise DomainInvariantViolation("injected_fault_count cannot be negative.")
        if self.recovered_fault_count < 0:
            raise DomainInvariantViolation("recovered_fault_count cannot be negative.")
        if self.passed and (self.recovered_fault_count != self.injected_fault_count):
            raise DomainInvariantViolation(
                f"ByzantineChaosReport passed=True requires recovered ({self.recovered_fault_count}) == injected ({self.injected_fault_count})."
            )
        if not self.passed and (self.recovered_fault_count == self.injected_fault_count and self.injected_fault_count > 0):
            raise DomainInvariantViolation(
                "ByzantineChaosReport marked passed=False but all injected faults recovered."
            )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "report_id": self.report_id,
            "target_module": self.target_module,
            "chaos_scenarios_tested": self.chaos_scenarios_tested,
            "passed": self.passed,
            "injected_fault_count": self.injected_fault_count,
            "recovered_fault_count": self.recovered_fault_count,
            "chaos_seed": self.chaos_seed,
            "executed_at_unix_ms": self.executed_at_unix_ms,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ByzantineChaosReport:
        instance = cls(
            report_id=data["report_id"],
            target_module=data["target_module"],
            chaos_scenarios_tested=int(data["chaos_scenarios_tested"]),
            passed=bool(data["passed"]),
            injected_fault_count=int(data.get("injected_fault_count", 0)),
            recovered_fault_count=int(data.get("recovered_fault_count", 0)),
            chaos_seed=int(data.get("chaos_seed", 42)),
            executed_at_unix_ms=int(data.get("executed_at_unix_ms", int(time.time() * 1000))),
        )
        instance.validate_invariants()
        return instance


# =========================================================================
# 18. CausalConvergenceAttestation
# =========================================================================
@dataclass
class CausalConvergenceAttestation:
    """Tamper-evident attestation of causal DAG convergence and physical disk witnessing."""
    attestation_id: str
    dag_root_urn: str
    converged_leaf_count: int
    leaf_witnesses: List[PhysicalDiskWitness] = field(default_factory=list)
    merkle_causal_hash: str = ""
    certified: bool = True
    certified_at_unix_ms: int = field(default_factory=lambda: int(time.time() * 1000))

    def validate_invariants(self) -> None:
        if not self.attestation_id:
            raise DomainInvariantViolation("attestation_id must not be empty.")
        if not self.dag_root_urn.startswith("urn:axioma:g4b:"):
            raise DomainInvariantViolation(
                f"dag_root_urn must conform to urn:axioma:g4b:..., got {self.dag_root_urn}"
            )
        if self.converged_leaf_count <= 0:
            raise DomainInvariantViolation("converged_leaf_count must be strictly positive.")
        if len(self.leaf_witnesses) != self.converged_leaf_count:
            raise DomainInvariantViolation(
                f"leaf_witnesses count ({len(self.leaf_witnesses)}) must match converged_leaf_count ({self.converged_leaf_count})."
            )
        if len(self.merkle_causal_hash) != 64:
            raise DomainInvariantViolation(
                f"merkle_causal_hash must be a 64-char hex string, got {len(self.merkle_causal_hash)}"
            )
        for w in self.leaf_witnesses:
            w.validate_invariants()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "attestation_id": self.attestation_id,
            "dag_root_urn": self.dag_root_urn,
            "converged_leaf_count": self.converged_leaf_count,
            "leaf_witnesses": [w.to_dict() for w in self.leaf_witnesses],
            "merkle_causal_hash": self.merkle_causal_hash,
            "certified": self.certified,
            "certified_at_unix_ms": self.certified_at_unix_ms,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> CausalConvergenceAttestation:
        instance = cls(
            attestation_id=data["attestation_id"],
            dag_root_urn=data["dag_root_urn"],
            converged_leaf_count=int(data["converged_leaf_count"]),
            leaf_witnesses=[PhysicalDiskWitness.from_dict(w) for w in data.get("leaf_witnesses", [])],
            merkle_causal_hash=data.get("merkle_causal_hash", ""),
            certified=bool(data.get("certified", True)),
            certified_at_unix_ms=int(data.get("certified_at_unix_ms", int(time.time() * 1000))),
        )
        instance.validate_invariants()
        return instance


# =========================================================================
# 19. QuineReactiveManifest
# =========================================================================
@dataclass
class QuineReactiveManifest:
    """Certification manifest for Quine daughter self-hosting with reactive DAG verification."""
    manifest_id: str
    daughter_gen_id: str
    reactive_dag_verified: bool
    self_hosting_certified: bool
    crucible_score: float
    emitted_artifacts: List[str] = field(default_factory=list)
    merkle_signature: str = ""
    sealed_at_unix_ms: int = field(default_factory=lambda: int(time.time() * 1000))

    def validate_invariants(self) -> None:
        if not self.manifest_id:
            raise DomainInvariantViolation("manifest_id must not be empty.")
        if not self.daughter_gen_id:
            raise DomainInvariantViolation("daughter_gen_id must not be empty.")
        if not (0.0 <= self.crucible_score <= 1.0):
            raise DomainInvariantViolation(
                f"crucible_score must be in [0.0, 1.0], got {self.crucible_score}"
            )
        if len(self.emitted_artifacts) < 1:
            raise DomainInvariantViolation("emitted_artifacts must contain at least 1 artifact path.")
        if len(self.merkle_signature) != 64:
            raise DomainInvariantViolation(
                f"merkle_signature must be a 64-char hex string, got {len(self.merkle_signature)}"
            )
        if self.self_hosting_certified:
            if not self.reactive_dag_verified:
                raise DomainInvariantViolation(
                    "self_hosting_certified requires reactive_dag_verified=True."
                )
            if self.crucible_score < 0.95:
                raise DomainInvariantViolation(
                    f"self_hosting_certified requires crucible_score >= 0.95, got {self.crucible_score}"
                )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "manifest_id": self.manifest_id,
            "daughter_gen_id": self.daughter_gen_id,
            "reactive_dag_verified": self.reactive_dag_verified,
            "self_hosting_certified": self.self_hosting_certified,
            "crucible_score": self.crucible_score,
            "emitted_artifacts": list(self.emitted_artifacts),
            "merkle_signature": self.merkle_signature,
            "sealed_at_unix_ms": self.sealed_at_unix_ms,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> QuineReactiveManifest:
        instance = cls(
            manifest_id=data["manifest_id"],
            daughter_gen_id=data["daughter_gen_id"],
            reactive_dag_verified=bool(data["reactive_dag_verified"]),
            self_hosting_certified=bool(data["self_hosting_certified"]),
            crucible_score=float(data["crucible_score"]),
            emitted_artifacts=list(data.get("emitted_artifacts", [])),
            merkle_signature=data.get("merkle_signature", ""),
            sealed_at_unix_ms=int(data.get("sealed_at_unix_ms", int(time.time() * 1000))),
        )
        instance.validate_invariants()
        return instance
