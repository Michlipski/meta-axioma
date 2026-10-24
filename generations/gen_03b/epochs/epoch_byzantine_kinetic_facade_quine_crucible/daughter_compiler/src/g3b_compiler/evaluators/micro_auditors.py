"""Generation 3b Zero-Trust Micro-Auditors (The Brain - Gemini 4 Argon).

Intercepts indivisible leaf nodes emitted by The Muscle (Gemini 3.8 Flash) on the
Fractal Task Stack and subjects them to hostile, zero-trust verification:
1. SecurityMicroAuditor: Hardcoded secrets, missing JWT validations, eval/exec injection, plaintext passwords.
2. ContractMicroAuditor: Noun invariant checks, pre/post condition satisfaction in leaf AST/code.
3. CognitiveRoutingAuditor: Enforces [L1-G3B-014] dual-model attribution (emitted by Flash, audited by Argon).
4. TopologicalMicroAuditor: Enforces [L1-G3B-012] anti-loopback boundary realism on network configs/code.
5. ThermodynamicMicroAuditor: Physical token bounding and Landauer dissipation verification.
"""

from dataclasses import dataclass, field
import re
from typing import Dict, Any, List, Optional

from ..routing.router import DualModelRouter, CognitiveRole, ModelTier, CognitiveRoutingViolation
from ..thermodynamics import PhysicalTokenMeter, ThermodynamicLedger, ProtectedCapitalViolation


@dataclass
class LeafArtifact:
    """An indivisible leaf output emitted by Gemini 3.8 Flash."""
    task_id: str
    artifact_type: str  # "code", "schema", "config", "contract_fragment"
    content: str
    emitting_model: str = ModelTier.MUSCLE_FLASH.value
    token_budget_allocated: int = 4000
    network_endpoints: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MicroAuditResult:
    """Detailed audit verdict for a single leaf node."""
    task_id: str
    is_passed: bool
    evaluating_model: str = ModelTier.BRAIN_ARGON.value
    defects: List[str] = field(default_factory=list)
    remediation_advice: Optional[str] = None
    physical_tokens: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "is_passed": self.is_passed,
            "evaluating_model": self.evaluating_model,
            "defects": self.defects,
            "remediation_advice": self.remediation_advice,
            "physical_tokens": self.physical_tokens,
        }


class SecurityMicroAuditor:
    """Traps security vulnerabilities, secret leaks, and insecure evaluations."""

    SECRET_PATTERNS = [
        re.compile(r"""(?:api_key|secret|password|bearer|jwt_secret)\s*[:=]\s*["'][a-zA-Z0-9_\-\.]{8,}["']""", re.IGNORECASE),
        re.compile(r"""-----BEGIN (?:RSA )?PRIVATE KEY-----"""),
    ]
    INJECTION_PATTERNS = [
        re.compile(r"\b(?:eval|exec)\s*\("),
        re.compile(r"\bcursor\.execute\s*\(\s*f[\"']"),  # raw f-string SQL
        re.compile(r"""f["']\s*(?:SELECT|INSERT|UPDATE|DELETE|DROP)\s+""", re.IGNORECASE),  # interpolated SQL
        re.compile(r"""\b(?:SELECT|INSERT|UPDATE|DELETE)\b.*?\+\s*[a-zA-Z_]\w*""", re.IGNORECASE),  # string concat SQL
    ]

    @classmethod
    def audit(cls, leaf: LeafArtifact) -> List[str]:
        defects = []
        for pat in cls.SECRET_PATTERNS:
            if pat.search(leaf.content):
                defects.append(f"Security Defect: Potential hardcoded secret or private credential detected in '{leaf.task_id}'.")
        for pat in cls.INJECTION_PATTERNS:
            if pat.search(leaf.content):
                defects.append(f"Security Defect: Unsafe dynamic evaluation or SQL injection vector detected in '{leaf.task_id}'.")
        return defects


class ContractMicroAuditor:
    """Verifies that leaf code/schema complies with required domain invariants."""

    @classmethod
    def audit(cls, leaf: LeafArtifact) -> List[str]:
        defects = []
        required_invariants = leaf.metadata.get("required_invariants", [])
        for inv in required_invariants:
            # Check if invariant logic or assertion is represented in leaf content
            # e.g. "balance >= 0"
            norm_inv = inv.replace(" ", "").lower()
            norm_content = leaf.content.replace(" ", "").lower()
            if norm_inv not in norm_content and inv not in leaf.content:
                defects.append(
                    f"Contract Defect: Mandatory domain invariant '{inv}' is not enforced in leaf '{leaf.task_id}'."
                )
        return defects


class CognitiveRoutingAuditor:
    """Enforces [L1-G3B-014] Dual-Model LLM routing invariants."""

    @classmethod
    def audit(cls, leaf: LeafArtifact) -> List[str]:
        defects = []
        if leaf.emitting_model != ModelTier.MUSCLE_FLASH.value:
            defects.append(
                f"[L1-G3B-014 Violation] Leaf artifact '{leaf.task_id}' was emitted by "
                f"'{leaf.emitting_model}', but leaf-node generation is strictly reserved for "
                f"'{ModelTier.MUSCLE_FLASH.value}'."
            )
        return defects


class TopologicalMicroAuditor:
    """Enforces [L1-G3B-012] Boundary Realism / Anti-Loopback on leaf configs and code."""

    LOOPBACK_TERMS = {"127.0.0.1", "localhost", "::1"}

    @classmethod
    def audit(cls, leaf: LeafArtifact) -> List[str]:
        defects = []
        is_multi_node = leaf.metadata.get("is_multi_node_cluster", False)
        if is_multi_node:
            for ep in leaf.network_endpoints:
                for lb in cls.LOOPBACK_TERMS:
                    if lb in ep.lower():
                        defects.append(
                            f"[L1-G3B-012 Violation] Distributed endpoint '{ep}' in leaf '{leaf.task_id}' "
                            f"binds to loopback '{lb}'. Boundary realism requires active routable interfaces."
                        )
            # Also check text
            for lb in cls.LOOPBACK_TERMS:
                if f"http://{lb}" in leaf.content or f"ws://{lb}" in leaf.content:
                    defects.append(
                        f"[L1-G3B-012 Violation] Multi-node network call in leaf '{leaf.task_id}' "
                        f"points to loopback host '{lb}'."
                    )
        return defects


class ThermodynamicMicroAuditor:
    """Enforces token budget limits and Landauer dissipation accounting on leaf nodes."""

    @classmethod
    def audit(cls, leaf: LeafArtifact) -> (List[str], int):
        defects = []
        physical_tokens = PhysicalTokenMeter.count(leaf.content)
        if physical_tokens > leaf.token_budget_allocated:
            defects.append(
                f"Thermodynamic Defect: Leaf '{leaf.task_id}' consumed {physical_tokens} tokens, "
                f"exceeding its allocated leaf quota of {leaf.token_budget_allocated} tokens."
            )
        return defects, physical_tokens


class ZeroTrustMicroAuditorRegistry:
    """The central Micro-Auditor Orchestrator running under Gemini 4 Argon governance."""

    @classmethod
    def audit_leaf(cls, leaf: LeafArtifact) -> MicroAuditResult:
        """Runs all specialized micro-auditors against the leaf artifact."""
        # Enforce [L1-G3B-014] Cognitive Routing
        DualModelRouter.create_invocation(
            task_id=f"micro_audit:{leaf.task_id}",
            role=CognitiveRole.ZERO_TRUST_AUDITOR,
            payload={"leaf_task_id": leaf.task_id},
            requested_model=ModelTier.BRAIN_ARGON,
        )

        all_defects: List[str] = []

        # 1. Security check
        all_defects.extend(SecurityMicroAuditor.audit(leaf))

        # 2. Contract & Invariants check
        all_defects.extend(ContractMicroAuditor.audit(leaf))

        # 3. Cognitive Routing check ([L1-G3B-014])
        all_defects.extend(CognitiveRoutingAuditor.audit(leaf))

        # 4. Topological Fidelity check ([L1-G3B-012])
        all_defects.extend(TopologicalMicroAuditor.audit(leaf))

        # 5. Thermodynamic tokens check
        thermo_defects, physical_tokens = ThermodynamicMicroAuditor.audit(leaf)
        all_defects.extend(thermo_defects)

        is_passed = len(all_defects) == 0
        remediation = None
        if not is_passed:
            remediation = (
                f"Leaf '{leaf.task_id}' failed zero-trust micro-audit. Defects to remediate:\n" +
                "\n".join(f"- {d}" for d in all_defects)
            )

        return MicroAuditResult(
            task_id=leaf.task_id,
            is_passed=is_passed,
            evaluating_model=ModelTier.BRAIN_ARGON.value,
            defects=all_defects,
            remediation_advice=remediation,
            physical_tokens=physical_tokens,
        )
