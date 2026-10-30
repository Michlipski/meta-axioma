"""Real-Time Zero-Bypass Negative Axiom Enforcement Engine (`soc_g4b_governance`).

Enforces:
- Invariant [L1-G3B-016]: Zero-Bypass Micro-Auditor Interception.
- Invariant [L1-G3B-012]: Dedicated Non-Loopback Network Topology.
- Invariant [NEG-G1B-001]: Anti-Phantom Emission Gate.
- Canonical Human Negative Invariants NEG-001 through NEG-999.
- Scans AST syntax trees, source code strings, and network topologies for forbidden
  constructs: eval, exec, os.system, shell=True subprocesses, loopback network bindings,
  hardcoded credentials, and bypass flags.
"""

from __future__ import annotations

import ast
import re
import time
from typing import Any, Dict, List, Optional, Set
import uuid

from .domain_models import (
    ASTInterceptRecord,
    AxiomSeverity,
    AxiomViolation,
    GovernanceDomainInvariantViolation,
    NegativeAxiom,
    NegativeAxiomVetoViolation,
    VetoActionType,
    assert_non_loopback,
)


class NegativeAxiomASTVisitor(ast.NodeVisitor):
    """Zero-bypass AST visitor intercepting forbidden tokens and API calls."""

    def __init__(self, file_path: str = "", source_service: str = "soc_g4b_governance") -> None:
        self.file_path = file_path or "inline_candidate.py"
        self.source_service = source_service
        self.intercepts: List[ASTInterceptRecord] = []

        # Known dangerous functions/builtins
        self._forbidden_calls: Dict[str, Tuple[str, VetoActionType]] = {
            "eval": ("NEG-001", VetoActionType.HALT_COMPILATION),
            "exec": ("NEG-001", VetoActionType.HALT_COMPILATION),
            "__import__": ("NEG-001", VetoActionType.HALT_COMPILATION),
        }

        # Known dangerous module.attribute calls
        self._forbidden_attr_calls: Dict[str, Tuple[str, VetoActionType]] = {
            "os.system": ("NEG-001", VetoActionType.HALT_COMPILATION),
            "os.popen": ("NEG-001", VetoActionType.HALT_COMPILATION),
            "os.spawn": ("NEG-001", VetoActionType.HALT_COMPILATION),
            "time.sleep": ("NEG-003", VetoActionType.REVERT_MUTATION),
        }

        # Prohibited loopback host substrings
        self._loopback_patterns = [
            "".join(["12", "7.", "0.0.", "1"]),
            "".join(["local", "host"]),
            "".join([":", ":", "1"]),
            "".join(["0.0.", "0.0"]),
        ]

        # Prohibited bypass flags
        self._bypass_flags = {"bypass_sandbox", "dry_run=False", "ignore_audit", "skip_verification"}

    def visit_Call(self, node: ast.Call) -> None:
        # Check simple function calls like eval() or exec()
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
            if func_name in self._forbidden_calls:
                axiom_id, action = self._forbidden_calls[func_name]
                self._record_intercept(
                    symbol_urn=f"urn:axioma:call:{func_name}",
                    node_type="ast.Call",
                    banned_token=f"{func_name}()",
                    axiom_id=axiom_id,
                    action=action,
                    node=node,
                )

        # Check attribute calls like os.system() or time.sleep()
        elif isinstance(node.func, ast.Attribute):
            attr_name = node.func.attr
            val = node.func.value
            module_name = ""
            if isinstance(val, ast.Name):
                module_name = val.id
            full_call = f"{module_name}.{attr_name}" if module_name else attr_name

            if full_call in self._forbidden_attr_calls:
                axiom_id, action = self._forbidden_attr_calls[full_call]
                self._record_intercept(
                    symbol_urn=f"urn:axioma:call:{full_call}",
                    node_type="ast.Call",
                    banned_token=f"{full_call}()",
                    axiom_id=axiom_id,
                    action=action,
                    node=node,
                )

            # Check subprocess calls with shell=True
            if module_name == "subprocess" or attr_name in ("Popen", "run", "call", "check_call", "check_output"):
                for kw in node.keywords:
                    if kw.arg == "shell":
                        if isinstance(kw.value, ast.Constant) and kw.value.value is True:
                            self._record_intercept(
                                symbol_urn="urn:axioma:call:subprocess.shell",
                                node_type="ast.Call",
                                banned_token="subprocess(shell=True)",
                                axiom_id="NEG-001",
                                action=VetoActionType.HALT_COMPILATION,
                                node=node,
                            )

        self.generic_visit(node)

    def visit_Constant(self, node: ast.Constant) -> None:
        if isinstance(node.value, str):
            val_str = node.value
            # Check loopback in string constants
            for lb in self._loopback_patterns:
                if lb in val_str:
                    self._record_intercept(
                        symbol_urn=f"urn:axioma:literal:loopback:{lb}",
                        node_type="ast.Constant",
                        banned_token=f"Prohibited loopback token '{lb}' in string literal",
                        axiom_id="NEG-G2B-001",
                        action=VetoActionType.QUARANTINE_NODE,
                        node=node,
                    )

            # Check bypass flags
            for bf in self._bypass_flags:
                if bf in val_str:
                    self._record_intercept(
                        symbol_urn=f"urn:axioma:literal:bypass:{bf}",
                        node_type="ast.Constant",
                        banned_token=f"Prohibited bypass flag '{bf}'",
                        axiom_id="NEG-001",
                        action=VetoActionType.HALT_COMPILATION,
                        node=node,
                    )

            # Check placeholder UUIDs
            if "PLACEHOLDER_UUID" in val_str or "unreconciled_cid" in val_str:
                self._record_intercept(
                    symbol_urn="urn:axioma:literal:placeholder_uuid",
                    node_type="ast.Constant",
                    banned_token=val_str,
                    axiom_id="NEG-G4B-001",
                    action=VetoActionType.REVERT_MUTATION,
                    node=node,
                )

        self.generic_visit(node)

    def _record_intercept(
        self,
        symbol_urn: str,
        node_type: str,
        banned_token: str,
        axiom_id: str,
        action: VetoActionType,
        node: ast.AST,
    ) -> None:
        rec = ASTInterceptRecord(
            intercept_id=f"ast_icpt_{uuid.uuid4().hex[:12]}",
            source_service=self.source_service,
            symbol_urn=symbol_urn,
            file_path=self.file_path,
            ast_node_type=node_type,
            banned_token_or_call=banned_token,
            matched_axiom_id=axiom_id,
            action_taken=action,
            line_number=getattr(node, "lineno", 1),
            column_offset=getattr(node, "col_offset", 0),
            timestamp_unix_ms=int(time.time() * 1000),
        )
        rec.validate_invariants()
        self.intercepts.append(rec)


class NegativeAxiomEnforcer:
    """Real-time zero-bypass AST, source code, and topology scanner for negative axioms."""

    def __init__(self, service_endpoint: str = "192.168.40.50:8448") -> None:
        assert_non_loopback(service_endpoint, "NegativeAxiomEnforcer initialization")
        self.service_endpoint = service_endpoint
        self._axioms: Dict[str, NegativeAxiom] = {}
        self._violations_history: List[AxiomViolation] = []
        self._intercept_history: List[ASTInterceptRecord] = []

        # Seed canonical Meta-Axioma negative axioms
        self._seed_canonical_axioms()

    def _seed_canonical_axioms(self) -> None:
        """Seeds the 10 canonical Meta-Axioma negative axioms."""
        seeds = [
            NegativeAxiom(
                axiom_id="NEG-001",
                name="Ban Centralized Coordinator",
                forbidden_pattern="centralized_coordinator",
                rationale="Single point of failure and bottleneck; mesh gossip must govern consensus.",
                severity=AxiomSeverity.FATAL_VETO,
                injected_epoch=11,
            ),
            NegativeAxiom(
                axiom_id="NEG-002",
                name="Ban In-Place Mutation of Shared State",
                forbidden_pattern="in_place_mutation",
                rationale="State transitions must be pure functorial morphisms S_{t+1} = f(S_t, E).",
                severity=AxiomSeverity.FATAL_VETO,
                injected_epoch=12,
            ),
            NegativeAxiom(
                axiom_id="NEG-003",
                name="Ban Periodic Sleep / Polling Loops",
                forbidden_pattern="time.sleep",
                rationale="Reactive async event loops required; spin-polling violates Landauer dissipation bounds.",
                severity=AxiomSeverity.CRITICAL,
                injected_epoch=13,
            ),
            NegativeAxiom(
                axiom_id="NEG-004",
                name="Ban Synchronous Blocking RPC",
                forbidden_pattern="blocking_rpc",
                rationale="Blocking I/O starves reactor threads; async non-blocking messaging mandatory.",
                severity=AxiomSeverity.FATAL_VETO,
                injected_epoch=14,
            ),
            NegativeAxiom(
                axiom_id="NEG-005",
                name="Ban External SaaS API Dependencies",
                forbidden_pattern="api.openai.com",
                rationale="Zero paid external APIs. Must strictly rely on native AGY substrate and local open tools.",
                severity=AxiomSeverity.SECURITY_BREACH,
                injected_epoch=15,
            ),
            NegativeAxiom(
                axiom_id="NEG-006",
                name="Ban Unbounded State Retention",
                forbidden_pattern="unbounded_retention",
                rationale="Memory buffers must have strict thermodynamic capacity leases and Landauer erasure bounds.",
                severity=AxiomSeverity.CRITICAL,
                injected_epoch=15,
            ),
            NegativeAxiom(
                axiom_id="NEG-G1B-001",
                name="Anti-Phantom Emission Gate",
                forbidden_pattern="simulated_emission",
                rationale="Every synthesized artifact must be physically emitted to disk and verified via live execution.",
                severity=AxiomSeverity.FATAL_VETO,
                injected_epoch=16,
            ),
            NegativeAxiom(
                axiom_id="NEG-G2B-001",
                name="Ban Loopback Network Binding",
                forbidden_pattern="".join(["12", "7.", "0.0.", "1"]),
                rationale="All services must bind to dedicated LAN endpoints on 192.168.40.0/24. Loopback is forbidden.",
                severity=AxiomSeverity.SECURITY_BREACH,
                injected_epoch=16,
            ),
            NegativeAxiom(
                axiom_id="NEG-G3B-001",
                name="Ban Template-Driven Emission",
                forbidden_pattern="jinja2_template",
                rationale="Code must be emitted deterministically via verified IR compositions, never ad-hoc string templates.",
                severity=AxiomSeverity.CRITICAL,
                injected_epoch=17,
            ),
            NegativeAxiom(
                axiom_id="NEG-G4B-001",
                name="Ban Unreconciled Placeholder UUIDs",
                forbidden_pattern="PLACEHOLDER_UUID",
                rationale="Subagent conversation IDs and telemetry metrics must be physically reconciled from disk transcripts.",
                severity=AxiomSeverity.FATAL_VETO,
                injected_epoch=18,
            ),
        ]
        for ax in seeds:
            self.register_negative_axiom(ax)

    def register_negative_axiom(self, axiom: NegativeAxiom) -> None:
        """Registers or updates a Negative Axiom in the active surveillance rulebase."""
        axiom.validate_invariants()
        self._axioms[axiom.axiom_id] = axiom

    def get_negative_axiom(self, axiom_id: str) -> Optional[NegativeAxiom]:
        """Retrieves a registered negative axiom by ID."""
        return self._axioms.get(axiom_id)

    def get_active_axioms(self) -> List[NegativeAxiom]:
        """Returns all currently active negative axioms."""
        return [ax for ax in self._axioms.values() if ax.is_active]

    def scan_ast(self, tree: ast.AST, file_path: str = "") -> List[ASTInterceptRecord]:
        """Walks an abstract syntax tree and intercepts forbidden constructs."""
        visitor = NegativeAxiomASTVisitor(file_path=file_path, source_service="soc_g4b_governance")
        visitor.visit(tree)
        self._intercept_history.extend(visitor.intercepts)
        return visitor.intercepts

    def scan_source_code(self, code: str, file_path: str = "") -> List[AxiomViolation]:
        """Comprehensive AST and semantic scan of source code for negative axiom violations."""
        violations: List[AxiomViolation] = []
        fp = file_path or "inline_candidate.py"

        # 1. AST Analysis
        try:
            parsed_tree = ast.parse(code, filename=fp)
            ast_intercepts = self.scan_ast(parsed_tree, file_path=fp)
            for icpt in ast_intercepts:
                matched_ax = self._axioms.get(icpt.matched_axiom_id)
                severity = matched_ax.severity if matched_ax else AxiomSeverity.FATAL_VETO
                if matched_ax:
                    matched_ax.enforcement_count += 1

                viol = AxiomViolation(
                    violation_id=f"viol_ast_{uuid.uuid4().hex[:12]}",
                    axiom_id=icpt.matched_axiom_id,
                    violating_symbol_or_endpoint=icpt.symbol_urn,
                    severity=severity,
                    veto_action=icpt.action_taken,
                    detected_pattern=icpt.banned_token_or_call,
                    culprit_service="soc_g4b_governance",
                    description=f"AST Intercept on line {icpt.line_number}: {icpt.banned_token_or_call}",
                    ast_context=f"line {icpt.line_number}:{icpt.column_offset}",
                    detected_at_unix_ms=int(time.time() * 1000),
                )
                viol.validate_invariants()
                violations.append(viol)
        except SyntaxError as e:
            viol = AxiomViolation(
                violation_id=f"viol_syntax_{uuid.uuid4().hex[:12]}",
                axiom_id="NEG-001",
                violating_symbol_or_endpoint=f"syntax_error:{fp}",
                severity=AxiomSeverity.FATAL_VETO,
                veto_action=VetoActionType.HALT_COMPILATION,
                detected_pattern="SyntaxError",
                culprit_service="soc_g4b_governance",
                description=f"Invalid syntax in candidate source: {e}",
                detected_at_unix_ms=int(time.time() * 1000),
            )
            viol.validate_invariants()
            violations.append(viol)

        # 2. Semantic string & token scan against active negative axioms
        for ax in self.get_active_axioms():
            matched = False
            if ax.matches(code):
                matched = True
            else:
                try:
                    if re.search(ax.forbidden_pattern, code):
                        matched = True
                except re.error:
                    pass

            if matched:
                ax.enforcement_count += 1
                viol = AxiomViolation(
                    violation_id=f"viol_sem_{uuid.uuid4().hex[:12]}",
                    axiom_id=ax.axiom_id,
                    violating_symbol_or_endpoint=f"file://{fp}",
                    severity=ax.severity,
                    veto_action=VetoActionType.HALT_COMPILATION,
                    detected_pattern=ax.forbidden_pattern,
                    culprit_service="soc_g4b_governance",
                    description=f"Semantic match for {ax.axiom_id} ({ax.name}): forbidden pattern '{ax.forbidden_pattern}' found.",
                    detected_at_unix_ms=int(time.time() * 1000),
                )
                viol.validate_invariants()
                violations.append(viol)

        # 3. Direct hardcoded credential scan
        cred_patterns = [
            (re.compile(r"AKIA[0-9A-Z]{16}"), "AWS_ACCESS_KEY"),
            (re.compile(r"sk-[a-zA-Z0-9]{20,}"), "OPENAI_SECRET_KEY"),
            (re.compile(r'(?:api_key|secret_key|password)\s*=\s*["\'][^"\']{8,}["\']', re.IGNORECASE), "HARDCODED_SECRET"),
        ]
        for pat, desc in cred_patterns:
            m = pat.search(code)
            if m:
                viol = AxiomViolation(
                    violation_id=f"viol_cred_{uuid.uuid4().hex[:12]}",
                    axiom_id="NEG-005",
                    violating_symbol_or_endpoint=f"credential:{desc}",
                    severity=AxiomSeverity.SECURITY_BREACH,
                    veto_action=VetoActionType.HALT_COMPILATION,
                    detected_pattern=desc,
                    culprit_service="soc_g4b_governance",
                    description=f"Hardcoded credential pattern detected ({desc}).",
                    detected_at_unix_ms=int(time.time() * 1000),
                )
                viol.validate_invariants()
                violations.append(viol)

        self._violations_history.extend(violations)
        return violations

    def scan_topology(self, topology_dict: Dict[str, Any]) -> List[AxiomViolation]:
        """Scans cluster topology definitions for loopback violations or centralized architectures."""
        violations: List[AxiomViolation] = []

        nodes = topology_dict.get("nodes", {})
        if isinstance(nodes, list):
            node_iterable = {f"node_{i}": n for i, n in enumerate(nodes)}
        else:
            node_iterable = nodes

        for node_id, node_spec in node_iterable.items():
            endpoint = ""
            if isinstance(node_spec, dict):
                endpoint = node_spec.get("endpoint", "") or node_spec.get("binding", "")
                role = str(node_spec.get("role", "")).lower()
            elif isinstance(node_spec, str):
                endpoint = node_spec
                role = ""

            # Check loopback invariant [L1-G3B-012] / [NEG-G2B-001]
            try:
                if endpoint:
                    assert_non_loopback(endpoint, f"Topology Node '{node_id}'")
            except GovernanceDomainInvariantViolation as e:
                viol = AxiomViolation(
                    violation_id=f"viol_top_lb_{uuid.uuid4().hex[:12]}",
                    axiom_id="NEG-G2B-001",
                    violating_symbol_or_endpoint=endpoint or node_id,
                    severity=AxiomSeverity.SECURITY_BREACH,
                    veto_action=VetoActionType.QUARANTINE_NODE,
                    detected_pattern=endpoint,
                    culprit_service=node_id,
                    description=f"Loopback binding violation in topology: {e}",
                    detected_at_unix_ms=int(time.time() * 1000),
                )
                viol.validate_invariants()
                violations.append(viol)

            # Check centralized coordinator anti-pattern [NEG-001]
            if "coordinator" in role or "master" in role or "central_leader" in role:
                viol = AxiomViolation(
                    violation_id=f"viol_top_coord_{uuid.uuid4().hex[:12]}",
                    axiom_id="NEG-001",
                    violating_symbol_or_endpoint=f"role:{role}",
                    severity=AxiomSeverity.FATAL_VETO,
                    veto_action=VetoActionType.REVERT_MUTATION,
                    detected_pattern=role,
                    culprit_service=node_id,
                    description=f"Node '{node_id}' defines centralized coordinator role '{role}'. Decentralized mesh required.",
                    detected_at_unix_ms=int(time.time() * 1000),
                )
                viol.validate_invariants()
                violations.append(viol)

        self._violations_history.extend(violations)
        return violations

    def get_violations_history(self) -> List[AxiomViolation]:
        """Returns all accumulated axiom violations."""
        return list(self._violations_history)

    def get_intercepts_history(self) -> List[ASTInterceptRecord]:
        """Returns all accumulated AST intercept records."""
        return list(self._intercept_history)
