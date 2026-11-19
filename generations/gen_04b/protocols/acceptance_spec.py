"""Generation 4b Acceptance Specification Intermediate Representation (`protocols/acceptance_spec.py`).

Enforces:
- [SPEC-G4B-RESEARCH-001] Machine-Readable Acceptance Contracts for Research & Downstream Enclaves.
- [L1-G4B-001] Service-Oriented Sovereign Mesh Protocol Standardization.
- [L1-G4B-002] Zero-Code Research Tool Boundary.
- [INV-G4B-CAUSAL-001] Physical Disk Grounding & Anti-Tautology Falsification Schema.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
import hashlib
import json
from pathlib import Path
import re
from typing import Any, Dict, List, Optional, Tuple, Union


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


@dataclass
class RedTeamVerdict:
    """Structured Phase 3 Socratic Red Team verdict governing certification and self-healing."""
    red_team_pass: bool
    critical_vulnerabilities_found: int
    findings: List[str] = field(default_factory=list)
    cycle: int = 0
    verdict_source: str = "EXPLICIT_VERDICT"
    conversation_id: Optional[str] = None

    def __post_init__(self) -> None:
        self.critical_vulnerabilities_found = max(0, int(self.critical_vulnerabilities_found))
        self.findings = [str(f).strip() for f in (self.findings or []) if str(f).strip()]
        # Fail closed: any positive critical count forces red_team_pass = False
        if self.critical_vulnerabilities_found > 0:
            self.red_team_pass = False
        elif not self.red_team_pass and self.critical_vulnerabilities_found == 0:
            # Ensure unresolved failing verdict always carries non-zero critical count
            self.critical_vulnerabilities_found = max(1, len(self.findings))

    @property
    def is_blocking(self) -> bool:
        """Returns True when unresolved critical findings require remediation or fail-closed halt."""
        return (not self.red_team_pass) or (self.critical_vulnerabilities_found > 0)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any], default_cycle: int = 0) -> RedTeamVerdict:
        raw_pass = data.get("red_team_pass")
        if raw_pass is None:
            raw_pass = data.get("red_team_passed")
        raw_crit = data.get("critical_vulnerabilities_found")
        if raw_crit is None:
            raw_crit = data.get("critical_count")
        findings = data.get("findings") or data.get("blocking_findings") or data.get("key_findings") or []
        if isinstance(findings, str):
            findings = [findings]

        if raw_pass is None:
            if raw_crit is not None:
                parsed_pass = int(raw_crit) == 0
            else:
                parsed_pass = False
        elif isinstance(raw_pass, str):
            parsed_pass = raw_pass.strip().lower() in ("true", "pass", "passed", "yes", "1")
        else:
            parsed_pass = bool(raw_pass)

        parsed_crit = int(raw_crit) if raw_crit is not None else (0 if parsed_pass else max(1, len(findings)))
        return cls(
            red_team_pass=parsed_pass,
            critical_vulnerabilities_found=parsed_crit,
            findings=list(findings),
            cycle=int(data.get("cycle", default_cycle)),
            verdict_source=str(data.get("verdict_source", "EXPLICIT_VERDICT")),
            conversation_id=data.get("conversation_id"),
        )


def parse_red_team_verdict(
    raw_return: Any,
    target_dir: Union[Path, str],
    cycle: int = 0,
    strict_required: bool = False,
) -> Tuple[Optional[str], RedTeamVerdict]:
    """Extracts (conversation_id, RedTeamVerdict) from Phase 3 Red Team output or physical verdict file.

    Resolution order:
    1. Structured return value (`RedTeamVerdict`, `dict`, tuple `(cid, verdict)`, or JSON string).
    2. Physical `{target_dir}/red_team_verdict.json` written by the Red Team witness.
    3. Structured text markers inside string return (`red_team_pass`, `critical_vulnerabilities_found`).
    4. Plain conversation ID string (legacy test stub compatibility when `strict_required=False`;
       fails closed when `strict_required=True`).
    """
    target_path = Path(target_dir).resolve()
    verdict_file = target_path / "red_team_verdict.json"

    cid: Optional[str] = None
    verdict: Optional[RedTeamVerdict] = None

    # 1. Structured return from subagent_invoker
    if isinstance(raw_return, RedTeamVerdict):
        verdict = RedTeamVerdict(
            red_team_pass=raw_return.red_team_pass,
            critical_vulnerabilities_found=raw_return.critical_vulnerabilities_found,
            findings=list(raw_return.findings),
            cycle=cycle,
            verdict_source=raw_return.verdict_source or "STRUCTURED_RETURN",
            conversation_id=raw_return.conversation_id,
        )
        cid = raw_return.conversation_id
    elif isinstance(raw_return, tuple) and len(raw_return) == 2:
        first, second = raw_return
        cid = str(first) if first else None
        if isinstance(second, RedTeamVerdict):
            verdict = RedTeamVerdict(
                red_team_pass=second.red_team_pass,
                critical_vulnerabilities_found=second.critical_vulnerabilities_found,
                findings=list(second.findings),
                cycle=cycle,
                verdict_source=second.verdict_source or "STRUCTURED_TUPLE",
                conversation_id=cid or second.conversation_id,
            )
        elif isinstance(second, dict):
            payload = dict(second)
            payload.setdefault("verdict_source", "STRUCTURED_TUPLE")
            payload.setdefault("conversation_id", cid)
            verdict = RedTeamVerdict.from_dict(payload, default_cycle=cycle)
    elif isinstance(raw_return, dict):
        cid = raw_return.get("conversation_id") or raw_return.get("cid")
        if any(k in raw_return for k in ("red_team_pass", "red_team_passed", "critical_vulnerabilities_found", "findings")):
            payload = dict(raw_return)
            payload.setdefault("verdict_source", "STRUCTURED_DICT")
            payload.setdefault("conversation_id", cid)
            verdict = RedTeamVerdict.from_dict(payload, default_cycle=cycle)
    elif isinstance(raw_return, str):
        stripped = raw_return.strip()
        if stripped.startswith("{") and stripped.endswith("}"):
            try:
                parsed = json.loads(stripped)
                if isinstance(parsed, dict):
                    cid = parsed.get("conversation_id") or parsed.get("cid")
                    if any(k in parsed for k in ("red_team_pass", "red_team_passed", "critical_vulnerabilities_found", "findings")):
                        parsed.setdefault("verdict_source", "STRUCTURED_JSON_STRING")
                        parsed.setdefault("conversation_id", cid)
                        verdict = RedTeamVerdict.from_dict(parsed, default_cycle=cycle)
            except Exception:
                pass
        if verdict is None:
            # Check for inline structured witness markers in text
            pass_m = re.search(r"red_team_pass[`'\":\s=]+(true|false)", stripped, re.IGNORECASE)
            crit_m = re.search(r"critical_vulnerabilities_found[`'\":\s=]+(\d+)", stripped, re.IGNORECASE)
            if pass_m or crit_m:
                parsed_pass = (pass_m.group(1).lower() == "true") if pass_m else (int(crit_m.group(1)) == 0)
                parsed_crit = int(crit_m.group(1)) if crit_m else (0 if parsed_pass else 1)
                findings = [
                    line.strip().lstrip("-* ").strip()
                    for line in stripped.splitlines()
                    if re.search(r"\[CRIT-\d+\]|critical|vulnerability|finding", line, re.IGNORECASE)
                ]
                verdict = RedTeamVerdict(
                    red_team_pass=parsed_pass,
                    critical_vulnerabilities_found=parsed_crit,
                    findings=findings[:20],
                    cycle=cycle,
                    verdict_source="STRUCTURED_TEXT_MARKERS",
                    conversation_id=cid,
                )
            else:
                cid = stripped or None

    # 2. Physical red_team_verdict.json artifact takes precedence if no structured return verdict
    if verdict is None and verdict_file.exists():
        try:
            file_data = json.loads(verdict_file.read_text(encoding="utf-8"))
            if not isinstance(file_data, dict):
                raise ValueError("red_team_verdict.json must contain a JSON object")
            if "red_team_pass" not in file_data and "red_team_passed" not in file_data and "critical_vulnerabilities_found" not in file_data:
                raise ValueError("red_team_verdict.json missing required verdict fields")
            file_data.setdefault("verdict_source", "PHYSICAL_VERDICT_FILE")
            file_data.setdefault("conversation_id", cid)
            verdict = RedTeamVerdict.from_dict(file_data, default_cycle=cycle)
            if not cid and verdict.conversation_id:
                cid = verdict.conversation_id
        except Exception as exc:
            # Fail closed on malformed physical verdict artifact
            verdict = RedTeamVerdict(
                red_team_pass=False,
                critical_vulnerabilities_found=1,
                findings=[f"Malformed red_team_verdict.json (fail-closed): {exc}"],
                cycle=cycle,
                verdict_source="MALFORMED_VERDICT_FILE",
                conversation_id=cid,
            )

    # 3. Fallback when neither structured return nor verdict file exists
    if verdict is None:
        if strict_required:
            verdict = RedTeamVerdict(
                red_team_pass=False,
                critical_vulnerabilities_found=1,
                findings=["Missing explicit RedTeamVerdict under strict_red_team_verdict=True (fail-closed)."],
                cycle=cycle,
                verdict_source="MISSING_VERDICT_FAIL_CLOSED",
                conversation_id=cid,
            )
        else:
            verdict = RedTeamVerdict(
                red_team_pass=True,
                critical_vulnerabilities_found=0,
                findings=[],
                cycle=cycle,
                verdict_source="IMPLICIT_PASS_LEGACY_STUB",
                conversation_id=cid,
            )

    return cid, verdict
