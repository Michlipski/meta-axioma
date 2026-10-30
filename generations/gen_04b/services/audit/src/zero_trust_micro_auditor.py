"""Zero-Trust Micro-Auditor & Hermetic Boundary Sentry (`soc_g4b_audit`).

Enforces:
- [L1-G3B-012] Dedicated Non-Loopback Network Topology.
- [L1-G3B-016] Zero-Trust Micro-Auditor Interception before disk emission.
- AST-level invariant scanning across 4 foundational hermetic rules:
  - HERM-001: Strict prohibition of loopback network endpoints (127.0.0.1, localhost, ::1, 0.0.0.0).
  - HERM-002: Strict prohibition of sys.path tampering (append, insert, extend, assignments).
  - HERM-003: Strict prohibition of ambient filesystem escapes (os.chdir, hardcoded /tmp, traversal ../).
  - HERM-004: Syntax integrity and prohibition of banned dynamic execution constructs (eval, exec).
"""

from __future__ import annotations

import ast
import hashlib
import time
from typing import Any, Dict, List, Optional, Set, Tuple
import uuid

from .domain_models import (
    AuditDomainInvariantViolation,
    AuditSeverity,
    CodeLeafCandidate,
    HermeticAuditReport,
    HermeticLinterViolation,
)


class _HermeticASTVisitor(ast.NodeVisitor):
    """Internal AST visitor scanning for hermetic and axiomatic boundary violations."""

    LOOPBACK_PATTERNS = {"127.0.0.1", "localhost", "::1", "0.0.0.0"}
    BANNED_BUILTIN_CALLS = {"eval", "exec", "__import__", "compile"}

    def __init__(self, leaf_id: str) -> None:
        self.leaf_id = leaf_id
        self.violations: List[HermeticLinterViolation] = []
        self.ast_nodes_scanned: int = 0
        self.banned_constructs_detected: int = 0

    def visit(self, node: ast.AST) -> Any:
        self.ast_nodes_scanned += 1
        return super().visit(node)

    def visit_Constant(self, node: ast.Constant) -> None:
        if isinstance(node.value, str):
            val_lower = node.value.lower()

            # HERM-001: Prohibit loopback strings
            for pattern in self.LOOPBACK_PATTERNS:
                if pattern in val_lower:
                    self.violations.append(
                        HermeticLinterViolation(
                            violation_id=f"viol_herm001_{uuid.uuid4().hex[:8]}",
                            rule_id="HERM-001",
                            severity=AuditSeverity.FATAL,
                            line_number=node.lineno,
                            column_offset=node.col_offset,
                            description=f"Forbidden loopback network endpoint '{pattern}' detected in string literal.",
                            culprit_token=pattern,
                        )
                    )
                    self.banned_constructs_detected += 1

            # Check 127. subnet
            if "127." in node.value and not any(p in val_lower for p in self.LOOPBACK_PATTERNS):
                self.violations.append(
                    HermeticLinterViolation(
                        violation_id=f"viol_herm001_{uuid.uuid4().hex[:8]}",
                        rule_id="HERM-001",
                        severity=AuditSeverity.FATAL,
                        line_number=node.lineno,
                        column_offset=node.col_offset,
                        description=f"Forbidden loopback 127.x.x.x subnet endpoint detected: '{node.value}'.",
                        culprit_token=node.value,
                    )
                )
                self.banned_constructs_detected += 1

            # HERM-003: Prohibit ambient directory / filesystem escapes
            if "/tmp" in node.value:
                self.violations.append(
                    HermeticLinterViolation(
                        violation_id=f"viol_herm003_{uuid.uuid4().hex[:8]}",
                        rule_id="HERM-003",
                        severity=AuditSeverity.ERROR,
                        line_number=node.lineno,
                        column_offset=node.col_offset,
                        description="Prohibited hardcoded ambient path '/tmp' detected.",
                        culprit_token="/tmp",
                    )
                )
                self.banned_constructs_detected += 1

            if "../" in node.value or "..\\" in node.value:
                self.violations.append(
                    HermeticLinterViolation(
                        violation_id=f"viol_herm003_{uuid.uuid4().hex[:8]}",
                        rule_id="HERM-003",
                        severity=AuditSeverity.ERROR,
                        line_number=node.lineno,
                        column_offset=node.col_offset,
                        description="Prohibited ambient directory traversal '../' detected.",
                        culprit_token="../",
                    )
                )
                self.banned_constructs_detected += 1

        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        # Check direct calls (eval, exec, __import__)
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
            if func_name in self.BANNED_BUILTIN_CALLS:
                self.violations.append(
                    HermeticLinterViolation(
                        violation_id=f"viol_herm004_{uuid.uuid4().hex[:8]}",
                        rule_id="HERM-004",
                        severity=AuditSeverity.FATAL,
                        line_number=node.lineno,
                        column_offset=node.col_offset,
                        description=f"Forbidden dynamic execution call '{func_name}()' violates hermetic AST isolation.",
                        culprit_token=func_name,
                    )
                )
                self.banned_constructs_detected += 1

        # Check method calls (os.chdir, sys.path.append, sys.path.insert, sys.path.extend)
        elif isinstance(node.func, ast.Attribute):
            attr_name = node.func.attr
            # os.chdir
            if attr_name == "chdir":
                if isinstance(node.func.value, ast.Name) and node.func.value.id == "os":
                    self.violations.append(
                        HermeticLinterViolation(
                            violation_id=f"viol_herm003_{uuid.uuid4().hex[:8]}",
                            rule_id="HERM-003",
                            severity=AuditSeverity.FATAL,
                            line_number=node.lineno,
                            column_offset=node.col_offset,
                            description="Forbidden ambient directory mutation 'os.chdir()' detected.",
                            culprit_token="os.chdir",
                        )
                    )
                    self.banned_constructs_detected += 1

            # sys.path mutations
            if attr_name in ("append", "insert", "extend"):
                val = node.func.value
                if isinstance(val, ast.Attribute) and val.attr == "path":
                    if isinstance(val.value, ast.Name) and val.value.id == "sys":
                        self.violations.append(
                            HermeticLinterViolation(
                                violation_id=f"viol_herm002_{uuid.uuid4().hex[:8]}",
                                rule_id="HERM-002",
                                severity=AuditSeverity.ERROR,
                                line_number=node.lineno,
                                column_offset=node.col_offset,
                                description=f"Forbidden runtime sys.path mutation 'sys.path.{attr_name}()' detected.",
                                culprit_token=f"sys.path.{attr_name}",
                            )
                        )
                        self.banned_constructs_detected += 1

        self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign) -> None:
        # Check assignments to sys.path = [...]
        for target in node.targets:
            if isinstance(target, ast.Attribute) and target.attr == "path":
                if isinstance(target.value, ast.Name) and target.value.id == "sys":
                    self.violations.append(
                        HermeticLinterViolation(
                            violation_id=f"viol_herm002_{uuid.uuid4().hex[:8]}",
                            rule_id="HERM-002",
                            severity=AuditSeverity.FATAL,
                            line_number=node.lineno,
                            column_offset=node.col_offset,
                            description="Forbidden reassignment of 'sys.path' detected.",
                            culprit_token="sys.path",
                        )
                    )
                    self.banned_constructs_detected += 1
        self.generic_visit(node)


class ZeroTrustMicroAuditor:
    """Zero-Trust AST Micro-Auditor (`SentrySyntax` peer verifier)."""

    def __init__(self, auditor_node_id: str = "node_hermetic_sentry") -> None:
        self.auditor_node_id = auditor_node_id

    def audit_source(self, source_code: str, leaf_id: str = "leaf_anonymous") -> HermeticAuditReport:
        """Audits raw Python source code for hermetic compliance."""
        report_id = f"rpt_herm_{uuid.uuid4().hex[:12]}"

        # Syntax check
        try:
            tree = ast.parse(source_code)
        except SyntaxError as e:
            syntax_violation = HermeticLinterViolation(
                violation_id=f"viol_herm004_{uuid.uuid4().hex[:8]}",
                rule_id="HERM-004",
                severity=AuditSeverity.FATAL,
                line_number=e.lineno or 1,
                column_offset=e.offset or 0,
                description=f"Python syntax error in candidate leaf: {e.msg}",
                culprit_token="SyntaxError",
            )
            return HermeticAuditReport(
                report_id=report_id,
                leaf_id=leaf_id,
                is_hermetic=False,
                violations=[syntax_violation],
                ast_nodes_scanned=0,
                banned_constructs_detected=1,
                auditor_node_id=self.auditor_node_id,
            )

        # AST Inspection
        visitor = _HermeticASTVisitor(leaf_id=leaf_id)
        visitor.visit(tree)

        is_hermetic = (len(visitor.violations) == 0)
        return HermeticAuditReport(
            report_id=report_id,
            leaf_id=leaf_id,
            is_hermetic=is_hermetic,
            violations=visitor.violations,
            ast_nodes_scanned=visitor.ast_nodes_scanned,
            banned_constructs_detected=visitor.banned_constructs_detected,
            auditor_node_id=self.auditor_node_id,
        )

    def audit_candidate(self, candidate: CodeLeafCandidate) -> HermeticAuditReport:
        """Audits a typed CodeLeafCandidate and verifies both source and metadata."""
        candidate.validate_invariants()
        return self.audit_source(candidate.source_code, leaf_id=candidate.leaf_id)

    def audit_dashboard_deliverable(
        self, dashboard_content: str, deliverable_id: str = "dashboard"
    ) -> HermeticAuditReport:
        """Audits a development process telemetry dashboard deliverable ([L1-G4B-008] & HERM-005).

        Guarantees zero placeholder UUIDs, zero unreconciled synthetic estimations,
        and valid structure before declaring compilation complete.
        """
        report_id = f"rpt_dash_{uuid.uuid4().hex[:12]}"
        violations: List[HermeticLinterViolation] = []

        if not dashboard_content or len(dashboard_content.strip()) < 100:
            violations.append(
                HermeticLinterViolation(
                    violation_id=f"viol_herm005_{uuid.uuid4().hex[:8]}",
                    rule_id="HERM-005",
                    severity=AuditSeverity.FATAL,
                    line_number=1,
                    column_offset=0,
                    description="Dashboard deliverable is empty or truncated (< 100 bytes).",
                    culprit_token="EmptyDashboard",
                )
            )
            return HermeticAuditReport(
                report_id=report_id,
                leaf_id=deliverable_id,
                is_hermetic=False,
                violations=violations,
                ast_nodes_scanned=0,
                banned_constructs_detected=1,
                auditor_node_id=self.auditor_node_id,
            )

        # Check banned placeholder UUID patterns
        banned_uuid_patterns = [
            "00000000-0000-0000-0000-000000000000",
            "11111111-1111-1111-1111-111111111111",
            "placeholder_uuid",
            "synthetic_uuid",
            "dummy_uuid",
            "subagent_uuid_",
            "TODO_RECONCILE",
        ]

        content_lower = dashboard_content.lower()
        for pat in banned_uuid_patterns:
            if pat in content_lower:
                violations.append(
                    HermeticLinterViolation(
                        violation_id=f"viol_herm005_{uuid.uuid4().hex[:8]}",
                        rule_id="HERM-005",
                        severity=AuditSeverity.FATAL,
                        line_number=1,
                        column_offset=0,
                        description=f"Forbidden placeholder/synthetic token '{pat}' detected in dashboard ([L1-G4B-008]).",
                        culprit_token=pat,
                    )
                )

        # Check for active loopback network URLs or socket connections inside dashboard scripts
        active_loopback_patterns = [
            "http://127.0.0.1",
            "http://localhost",
            "https://127.0.0.1",
            "https://localhost",
            "ws://127.0.0.1",
            "ws://localhost",
            "connect('127.0.0.1",
            'connect("127.0.0.1',
        ]
        for pattern in active_loopback_patterns:
            if pattern in content_lower:
                violations.append(
                    HermeticLinterViolation(
                        violation_id=f"viol_herm001_{uuid.uuid4().hex[:8]}",
                        rule_id="HERM-001",
                        severity=AuditSeverity.ERROR,
                        line_number=1,
                        column_offset=0,
                        description=f"Active loopback network connection '{pattern}' detected in dashboard.",
                        culprit_token=pattern,
                    )
                )

        is_hermetic = (len(violations) == 0)
        return HermeticAuditReport(
            report_id=report_id,
            leaf_id=deliverable_id,
            is_hermetic=is_hermetic,
            violations=violations,
            ast_nodes_scanned=len(dashboard_content.splitlines()),
            banned_constructs_detected=len(violations),
            auditor_node_id=self.auditor_node_id,
        )
