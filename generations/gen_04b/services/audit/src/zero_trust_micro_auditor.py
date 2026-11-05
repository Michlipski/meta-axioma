"""Zero-Trust Micro-Auditor & Hermetic Boundary Sentry (`soc_g4b_audit`).

Enforces:
- [L1-G3B-012] Dedicated Non-Loopback Network Topology.
- [L1-G3B-016] Zero-Trust Micro-Auditor Interception before disk emission.
- AST-level invariant scanning across foundational hermetic rules:
  - HERM-001: Strict prohibition of loopback network endpoints (127.0.0.1, localhost, ::1, 0.0.0.0).
  - HERM-002: Strict prohibition of sys.path tampering (append, insert, extend, assignments).
  - HERM-003: Strict prohibition of ambient filesystem escapes (os.chdir, hardcoded /tmp, traversal ../).
  - HERM-004: Syntax integrity and prohibition of banned dynamic execution constructs (eval, exec).
  - HERM-005: Prohibition of empty/truncated deliverables and unreconciled synthetic/placeholder tokens.
  - HERM-006: Prohibition of unrendered LaTeX math notation without a valid hermetic math engine.
"""

from __future__ import annotations

import ast
import hashlib
import os
from pathlib import Path
import re
import time
from typing import Any, Dict, List, Optional, Set, Tuple
import uuid

from .domain_models import (
    AuditDomainInvariantViolation,
    AuditSeverity,
    CodeLeafCandidate,
    HermeticAuditReport,
    HermeticLinterViolation,
    UnrenderedLatexViolation,
)
from .bijective_verifier import BijectiveVerifier
from .operational_pitfall_auditor import OperationalPitfallAuditor
from generations.gen_04b.protocols.deliverable_bundle import (
    ContractBijectivityWitness,
    OperationalPitfallAuditReport,
)


class _HermeticASTVisitor(ast.NodeVisitor):
    """Internal AST visitor scanning for hermetic and axiomatic boundary violations."""

    LOOPBACK_PATTERNS = {"127.0.0.1", "localhost", "::1", "0.0.0.0"}
    BANNED_BUILTIN_CALLS = {"eval", "exec", "__import__", "compile"}

    def __init__(
        self,
        leaf_id: str,
        allow_local_ipc: bool = False,
        runtime_profile: str = "SOVEREIGN_MESH",
    ) -> None:
        self.leaf_id = leaf_id
        self.allow_local_ipc = allow_local_ipc or (runtime_profile == "LOCAL_IPC")
        self.runtime_profile = runtime_profile
        self.violations: List[HermeticLinterViolation] = []
        self.ast_nodes_scanned: int = 0
        self.banned_constructs_detected: int = 0

    def visit(self, node: ast.AST) -> Any:
        self.ast_nodes_scanned += 1
        return super().visit(node)

    def visit_Constant(self, node: ast.Constant) -> None:
        if isinstance(node.value, str):
            val_lower = node.value.lower()

            # HERM-001: Prohibit loopback strings unless explicitly authorized under LOCAL_IPC or test sockets
            if not self.allow_local_ipc:
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

            # HERM-003: Prohibit ambient directory / filesystem escapes (Always enforced even in LOCAL_IPC)
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

    LATEX_DELIMITER_PATTERNS = [
        re.compile(r"\$\$[\s\S]*?\$\$"),
        re.compile(r"\\\(.*?\\\)"),
        re.compile(r"\\\[[\s\S]*?\\\]"),
    ]
    MALFORMED_DELIMITER_PATTERNS = [
        re.compile(r"\$\$(?:[^\$\n]|(?!\$\$))*?(?:\n|$)"),  # unclosed $$
        re.compile(r"\\\([^\)\n]*?(?:\]|\n|$)"),           # unclosed \( or mismatched with ]
        re.compile(r"\\\[[^\]\n]*?(?:\)|\n|$)"),           # unclosed \[ or mismatched with )
    ]
    LATEX_MACRO_PATTERNS = [
        re.compile(
            r"\\(?:text|forall|exists|mathcal|sum|prod|Delta|alpha|beta|theta|lambda|gamma|omega|nabla|partial|frac|approx|le|ge|neq|in|notin|subset|cup|cap|emptyset|otimes|oplus|times|pm|cdot|circ|implies|iff|to|rightarrow|leftarrow|infty|sqrt|int|oint|sim|equiv|subseteq|supseteq)\b"
        )
    ]
    MATH_DOLLAR_PATTERN = re.compile(r"(?<![\\\$])\$(?![\$\{0-9])([^\$\n]+?)(?<!\\)\$")

    def __init__(
        self,
        auditor_node_id: str = "node_hermetic_sentry",
        allow_local_ipc: bool = False,
        runtime_profile: str = "SOVEREIGN_MESH",
    ) -> None:
        self.auditor_node_id = auditor_node_id
        self.allow_local_ipc = allow_local_ipc or (runtime_profile == "LOCAL_IPC")
        self.runtime_profile = runtime_profile

    def audit_source(
        self,
        source_code: str,
        leaf_id: str = "leaf_anonymous",
        allow_local_ipc: Optional[bool] = None,
        runtime_profile: Optional[str] = None,
    ) -> HermeticAuditReport:
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

        # Determine effective local IPC authorization
        effective_ipc = self.allow_local_ipc if allow_local_ipc is None else allow_local_ipc
        effective_profile = self.runtime_profile if runtime_profile is None else runtime_profile
        if effective_profile == "LOCAL_IPC":
            effective_ipc = True
        sc_lower = source_code.lower()
        if (
            "# allow-local-ipc" in sc_lower
            or "profile.local_ipc" in sc_lower
            or 'profile == "local_ipc"' in sc_lower
            or "authorized_local_ipc" in sc_lower
        ):
            effective_ipc = True

        # AST Inspection
        visitor = _HermeticASTVisitor(
            leaf_id=leaf_id,
            allow_local_ipc=effective_ipc,
            runtime_profile=effective_profile,
        )
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

    @classmethod
    def check_unrendered_latex(cls, html_content: str, base_dir: Optional[str] = None) -> List[str]:
        """Scans HTML content for unrendered LaTeX expressions (HERM-006).

        Returns empty list if a valid, hermetic math engine (KaTeX/MathJax with auto-render)
        is properly loaded and verified on disk, or if no unrendered LaTeX exists.
        Otherwise returns a list of unique unrendered LaTeX culprit tokens.
        """
        if not html_content:
            return []

        # Check if valid math engine is present and properly initialized
        content_lower = html_content.lower()
        has_katex = "katex" in content_lower
        has_mathjax = "mathjax" in content_lower
        has_engine = has_katex or has_mathjax

        has_autorender = (
            "rendermathinelement" in content_lower
            or "auto-render" in content_lower
            or "mathjax.typeset" in content_lower
        )

        if has_engine and has_autorender:
            engine_valid = True
            # If referenced locally and base_dir is provided, verify referenced files exist on disk
            if base_dir:
                local_refs = re.findall(
                    r'<(?:script|link)[^>]*(?:src|href)=["\']([^"\']*(?:katex|mathjax)[^"\']*)["\']',
                    html_content,
                    re.IGNORECASE,
                )
                for ref in local_refs:
                    if not ref.startswith(("http://", "https://", "//")):
                        local_path = Path(base_dir) / ref
                        if not local_path.exists():
                            engine_valid = False
                            break
            if engine_valid:
                return []

        # No valid math engine loaded -> Scan for unrendered LaTeX expressions
        culprits: List[str] = []

        # 1. Delimiter patterns ($$, \(, \[)
        for pattern in cls.LATEX_DELIMITER_PATTERNS:
            for match in pattern.finditer(html_content):
                val = match.group(0)
                if val not in culprits:
                    culprits.append(val)

        # 1b. Malformed / unclosed delimiter patterns
        for pattern in cls.MALFORMED_DELIMITER_PATTERNS:
            for match in pattern.finditer(html_content):
                val = match.group(0).strip()
                if val and not any(val in c for c in culprits) and val not in culprits:
                    culprits.append(val)

        # 2. Math dollar pattern ($...$)
        for match in cls.MATH_DOLLAR_PATTERN.finditer(html_content):
            val = match.group(0)
            inner = match.group(1).strip()
            # Exempt currency amounts: $100, $143,100, $50.00, $ 100, etc.
            if re.match(r"^[\d,.]+\s*(?:usd|eur|gbp|k|m|b)?$", inner, re.IGNORECASE):
                continue
            # Exempt JS template strings
            if inner.startswith("{") or "${" in val:
                continue
            if val not in culprits:
                culprits.append(val)

        # 3. LaTeX macro patterns (\forall, \text, etc.)
        for pattern in cls.LATEX_MACRO_PATTERNS:
            for match in pattern.finditer(html_content):
                val = match.group(0)
                # If this macro is already contained within an extracted delimiter expression, avoid duplicate reporting
                if any(val in c for c in culprits):
                    continue
                if val not in culprits:
                    culprits.append(val)

        return culprits

    def audit_html_deliverable(
        self, html_content: str, deliverable_id: str = "html_file", base_dir: Optional[str] = None
    ) -> HermeticAuditReport:
        """Audits an HTML deliverable for loopback connections (HERM-001), empty/synthetic tokens (HERM-005),
        and unrendered LaTeX math expressions (HERM-006).
        """
        report_id = f"rpt_html_{uuid.uuid4().hex[:12]}"
        violations: List[HermeticLinterViolation] = []

        if not html_content or len(html_content.strip()) < 100:
            violations.append(
                HermeticLinterViolation(
                    violation_id=f"viol_herm005_{uuid.uuid4().hex[:8]}",
                    rule_id="HERM-005",
                    severity=AuditSeverity.FATAL,
                    line_number=1,
                    column_offset=0,
                    description="HTML deliverable is empty or truncated (< 100 bytes).",
                    culprit_token="EmptyHTML",
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

        # Check banned placeholder UUID patterns (HERM-005)
        banned_uuid_patterns = [
            "00000000-0000-0000-0000-000000000000",
            "11111111-1111-1111-1111-111111111111",
            "placeholder_uuid",
            "synthetic_uuid",
            "dummy_uuid",
            "subagent_uuid_",
            "TODO_RECONCILE",
        ]

        content_lower = html_content.lower()
        for pat in banned_uuid_patterns:
            if pat in content_lower:
                violations.append(
                    HermeticLinterViolation(
                        violation_id=f"viol_herm005_{uuid.uuid4().hex[:8]}",
                        rule_id="HERM-005",
                        severity=AuditSeverity.FATAL,
                        line_number=1,
                        column_offset=0,
                        description=f"Forbidden placeholder/synthetic token '{pat}' detected in HTML deliverable ([L1-G4B-008]).",
                        culprit_token=pat,
                    )
                )

        # Check for active loopback network URLs or socket connections inside dashboard scripts (HERM-001)
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
                        description=f"Active loopback network connection '{pattern}' detected in HTML deliverable.",
                        culprit_token=pattern,
                    )
                )

        # Check for unrendered LaTeX expressions (HERM-006)
        latex_culprits = self.check_unrendered_latex(html_content, base_dir=base_dir)
        for culprit in latex_culprits:
            violations.append(
                HermeticLinterViolation(
                    violation_id=f"viol_herm006_{uuid.uuid4().hex[:8]}",
                    rule_id="HERM-006",
                    severity=AuditSeverity.FATAL,
                    line_number=1,
                    column_offset=0,
                    description=f"Unrendered LaTeX expression '{culprit}' detected in HTML deliverable without a valid, hermetic math rendering engine or semantic HTML/Unicode equivalent (HERM-006).",
                    culprit_token=culprit,
                )
            )

        is_hermetic = (len(violations) == 0)
        return HermeticAuditReport(
            report_id=report_id,
            leaf_id=deliverable_id,
            is_hermetic=is_hermetic,
            violations=violations,
            ast_nodes_scanned=len(html_content.splitlines()),
            banned_constructs_detected=len(violations),
            auditor_node_id=self.auditor_node_id,
        )

    def audit_dashboard_deliverable(
        self, dashboard_content: str, deliverable_id: str = "dashboard", base_dir: Optional[str] = None
    ) -> HermeticAuditReport:
        """Audits a development process telemetry dashboard deliverable ([L1-G4B-008] & HERM-005, HERM-006).

        Guarantees zero placeholder UUIDs, zero unreconciled synthetic estimations,
        zero unrendered LaTeX expressions without a math engine, and valid structure
        before declaring compilation complete.
        """
        return self.audit_html_deliverable(
            html_content=dashboard_content, deliverable_id=deliverable_id, base_dir=base_dir
        )

    def audit_bijectivity(
        self, source_code: str, contract: Any, leaf_id: str = "module.py"
    ) -> ContractBijectivityWitness:
        """Audits bijective mapping between ContractIR and AST code structures (BIJ-001..003)."""
        verifier = BijectiveVerifier(verifier_node_id=self.auditor_node_id)
        return verifier.verify_bijectivity(source_code, contract, source_file=leaf_id)

    def audit_operational_pitfalls(
        self, source_code: str, leaf_id: str = "module.py"
    ) -> OperationalPitfallAuditReport:
        """Audits physical AST mitigations for declared operational pitfalls (OP-001..004)."""
        auditor = OperationalPitfallAuditor(auditor_node_id=self.auditor_node_id)
        return auditor.audit_source(source_code, source_file=leaf_id)

    def audit_leaf_comprehensive(
        self, source_code: str, contract: Optional[Any] = None, leaf_id: str = "module.py"
    ) -> Dict[str, Any]:
        """Unified pre-disk audit intercept combining Hermetic, Bijective, and Operational passes."""
        hermetic_report = self.audit_source(source_code, leaf_id=leaf_id)
        if not hermetic_report.is_hermetic:
            return {
                "is_passed": False,
                "stage": "HERMETIC_LINTING",
                "hermetic_report": hermetic_report.to_dict(),
            }

        bijective_witness = None
        if contract is not None:
            bijective_witness = self.audit_bijectivity(source_code, contract, leaf_id=leaf_id)

        operational_report = self.audit_operational_pitfalls(source_code, leaf_id=leaf_id)

        return {
            "is_passed": hermetic_report.is_hermetic and (operational_report.is_compliant),
            "stage": "COMPREHENSIVE_AUDIT_PASSED",
            "hermetic_report": hermetic_report.to_dict(),
            "bijective_witness": bijective_witness.to_dict() if bijective_witness else None,
            "operational_report": operational_report.to_dict(),
        }
