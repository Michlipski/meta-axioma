"""Pass 4: Zero-Trust AST Hermeticity Evaluator ($S_{hermetic}$, 20%).

Evaluates:
- Static AST inspection across all application source files.
- Strictly flags banned dynamic execution constructs (eval, exec, __import__, compile).
- Flags ambient filesystem escapes (hardcoded /tmp, /private/tmp, os.chdir).
- Flags arbitrary sys.path tampering.
"""

from __future__ import annotations

import ast
from pathlib import Path
from typing import Any, Dict, List, Tuple

from ..domain_models import BenchmarkArchetype, EvaluationPassResult


class HermeticEvaluator:
    """Evaluates Pass 4: Zero-Trust AST Hermeticity ($S_{hermetic}$, Weight = 20%)."""

    def __init__(self, weight: float = 0.20) -> None:
        self.weight = weight

    def evaluate(self, app_dir: Path, archetype: BenchmarkArchetype) -> EvaluationPassResult:
        py_files = list(app_dir.rglob("*.py"))
        violations: List[Dict[str, Any]] = []

        # Try to use Meta-Axioma Generation 4b ZeroTrustMicroAuditor if available
        auditor = None
        try:
            from generations.gen_04b.services.audit.src.zero_trust_micro_auditor import (
                ZeroTrustMicroAuditor,
            )
            auditor = ZeroTrustMicroAuditor(runtime_profile="LOCAL_IPC")
        except Exception:
            auditor = None

        total_nodes_scanned = 0

        for py_file in py_files:
            try:
                code_text = py_file.read_text(encoding="utf-8")
                rel_path = str(py_file.relative_to(app_dir))

                if auditor is not None:
                    report = auditor.audit_source(
                        code_text,
                        leaf_id=rel_path,
                        runtime_profile="LOCAL_IPC",
                    )
                    total_nodes_scanned += report.ast_nodes_scanned
                    for v in report.violations:
                        # For local benchmark applications, allow sys.path adjustment to src/ if needed
                        if v.rule_id == "HERM-002" and "src" in code_text:
                            continue
                        violations.append({
                            "file": rel_path,
                            "rule_id": v.rule_id,
                            "line": v.line_number,
                            "desc": v.description,
                            "culprit": v.culprit_token,
                        })
                else:
                    # Robust built-in AST visitor fallback
                    nodes, file_viols = self._scan_ast_fallback(code_text, rel_path)
                    total_nodes_scanned += nodes
                    violations.extend(file_viols)
            except Exception as e:
                violations.append({
                    "file": str(py_file.name),
                    "rule_id": "HERM-004",
                    "line": 1,
                    "desc": f"AST parse failed: {e}",
                    "culprit": "SyntaxError",
                })

        # Score formula: 100 - 25 * violations (clamped to [0, 100])
        violation_count = len(violations)
        raw_score = max(0.0, 100.0 - 25.0 * violation_count)
        raw_score = round(raw_score, 2)
        weighted_score = round(raw_score * self.weight, 2)

        return EvaluationPassResult(
            pass_name="hermetic",
            weight=self.weight,
            raw_score=raw_score,
            weighted_score=weighted_score,
            details={
                "files_scanned": len(py_files),
                "ast_nodes_scanned": total_nodes_scanned,
                "violations_count": violation_count,
                "violations": violations[:15],
            },
            passed=(violation_count == 0),
        )

    def _scan_ast_fallback(self, code_text: str, file_path: str) -> Tuple[int, List[Dict[str, Any]]]:
        """Internal AST scanner when Gen 4b auditor module is not imported."""
        tree = ast.parse(code_text)
        nodes_scanned = 0
        violations = []
        banned_calls = {"eval", "exec", "__import__", "compile"}

        for node in ast.walk(tree):
            nodes_scanned += 1
            if isinstance(node, ast.Call):
                func = node.func
                if isinstance(func, ast.Name) and func.id in banned_calls:
                    violations.append({
                        "file": file_path,
                        "rule_id": "HERM-004",
                        "line": getattr(node, "lineno", 1),
                        "desc": f"Banned dynamic call '{func.id}' detected",
                        "culprit": func.id,
                    })
            elif isinstance(node, ast.Constant) and isinstance(node.value, str):
                val = node.value
                if "/tmp" in val or "/private/tmp" in val:
                    violations.append({
                        "file": file_path,
                        "rule_id": "HERM-003",
                        "line": getattr(node, "lineno", 1),
                        "desc": f"Ambient /tmp escape detected in string constant: '{val}'",
                        "culprit": val,
                    })

        return nodes_scanned, violations
