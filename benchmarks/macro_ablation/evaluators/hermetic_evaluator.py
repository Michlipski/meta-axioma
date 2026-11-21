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
            auditor = ZeroTrustMicroAuditor(allow_local_ipc=True, runtime_profile="LOCAL_IPC")
        except Exception:
            auditor = None

        total_nodes_scanned = 0

        for py_file in py_files:
            try:
                code_text = py_file.read_text(encoding="utf-8")
                rel_path = str(py_file.relative_to(app_dir))
                parsed_tree = ast.parse(code_text, filename=rel_path)

                if auditor is not None:
                    report = auditor.audit_source(
                        code_text,
                        leaf_id=rel_path,
                        allow_local_ipc=True,
                        runtime_profile="LOCAL_IPC",
                    )
                    total_nodes_scanned += report.ast_nodes_scanned
                    for v in report.violations:
                        # Symmetric, layout-agnostic HERM-002 rule:
                        # Allow standard Path(__file__).resolve().parent bootstrap ONLY in entrypoints/tests,
                        # identically for single-file and multi-file (src/) layouts.
                        if v.rule_id == "HERM-002" and self._is_permitted_app_root_bootstrap(
                            parsed_tree, v.line_number, rel_path
                        ):
                            continue
                        violations.append({
                            "file": rel_path,
                            "rule_id": v.rule_id,
                            "line": v.line_number,
                            "desc": v.description,
                            "culprit": v.culprit_token,
                        })
                else:
                    # Robust built-in AST visitor fallback (mirrors primary HERM-002/003/004 symmetry)
                    nodes, file_viols = self._scan_ast_fallback(code_text, rel_path, parsed_tree=parsed_tree)
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

    @staticmethod
    def _is_entrypoint_or_test_path(rel_path: str) -> bool:
        """Returns True if rel_path is a top-level entrypoint (run.py) or test file."""
        norm = rel_path.replace("\\", "/").lstrip("./")
        parts = norm.split("/")
        fname = parts[-1]
        if norm == "run.py":
            return True
        if fname.startswith("test_") and fname.endswith(".py"):
            return True
        if len(parts) >= 2 and parts[0] == "tests" and fname.endswith(".py"):
            return True
        return False

    @staticmethod
    def _expr_is_file_parent_root(expr: ast.AST, root_vars: set[str]) -> bool:
        """Checks whether expr resolves purely to Path(__file__).resolve().parent[.parent] or os.path.dirname(__file__)."""
        # Unwrap str(...)
        if (
            isinstance(expr, ast.Call)
            and isinstance(expr.func, ast.Name)
            and expr.func.id == "str"
            and len(expr.args) == 1
        ):
            expr = expr.args[0]

        if isinstance(expr, ast.Name) and expr.id in root_vars:
            return True

        # Path(__file__).resolve().parent (or .parent.parent)
        cur = expr
        parent_hops = 0
        while isinstance(cur, ast.Attribute) and cur.attr == "parent":
            parent_hops += 1
            cur = cur.value
        if parent_hops in (1, 2):
            if (
                isinstance(cur, ast.Call)
                and isinstance(cur.func, ast.Attribute)
                and cur.func.attr == "resolve"
            ):
                cur = cur.func.value
            if (
                isinstance(cur, ast.Call)
                and (
                    (isinstance(cur.func, ast.Name) and cur.func.id == "Path")
                    or (isinstance(cur.func, ast.Attribute) and cur.func.attr == "Path")
                )
                and len(cur.args) == 1
                and isinstance(cur.args[0], ast.Name)
                and cur.args[0].id == "__file__"
            ):
                return True

        # os.path.dirname(os.path.abspath(__file__)) or os.path.dirname(__file__)
        if (
            isinstance(expr, ast.Call)
            and isinstance(expr.func, ast.Attribute)
            and expr.func.attr == "dirname"
            and len(expr.args) == 1
        ):
            arg0 = expr.args[0]
            if isinstance(arg0, ast.Name) and arg0.id == "__file__":
                return True
            if (
                isinstance(arg0, ast.Call)
                and isinstance(arg0.func, ast.Attribute)
                and arg0.func.attr in ("abspath", "realpath", "dirname")
                and len(arg0.args) == 1
            ):
                inner = arg0.args[0]
                if isinstance(inner, ast.Name) and inner.id == "__file__":
                    return True
                if (
                    isinstance(inner, ast.Call)
                    and isinstance(inner.func, ast.Attribute)
                    and inner.func.attr in ("abspath", "realpath")
                    and len(inner.args) == 1
                    and isinstance(inner.args[0], ast.Name)
                    and inner.args[0].id == "__file__"
                ):
                    return True
        return False

    @classmethod
    def _is_permitted_app_root_bootstrap(
        cls,
        tree: ast.AST,
        line_number: int,
        rel_path: str,
    ) -> bool:
        """Symmetric, layout-agnostic check allowing ONLY app-root sys.path.insert(0, ...) in entrypoints/tests."""
        if not cls._is_entrypoint_or_test_path(rel_path):
            return False

        # Collect module-level variable names assigned to Path(__file__).resolve().parent[.parent]
        root_vars: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign) and cls._expr_is_file_parent_root(node.value, root_vars):
                for tgt in node.targets:
                    if isinstance(tgt, ast.Name):
                        root_vars.add(tgt.id)
            elif (
                isinstance(node, ast.AnnAssign)
                and node.value is not None
                and isinstance(node.target, ast.Name)
                and cls._expr_is_file_parent_root(node.value, root_vars)
            ):
                root_vars.add(node.target.id)

        # Verify the offending call on line_number is specifically sys.path.insert(0, <app_root>)
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call) or getattr(node, "lineno", -1) != line_number:
                continue
            if (
                isinstance(node.func, ast.Attribute)
                and node.func.attr == "insert"
                and isinstance(node.func.value, ast.Attribute)
                and node.func.value.attr == "path"
                and isinstance(node.func.value.value, ast.Name)
                and node.func.value.value.id == "sys"
                and len(node.args) == 2
                and isinstance(node.args[0], ast.Constant)
                and node.args[0].value == 0
                and cls._expr_is_file_parent_root(node.args[1], root_vars)
            ):
                return True
        return False

    def _scan_ast_fallback(
        self,
        code_text: str,
        file_path: str,
        parsed_tree: ast.AST | None = None,
    ) -> Tuple[int, List[Dict[str, Any]]]:
        """Internal AST scanner when Gen 4b auditor module is not imported."""
        tree = parsed_tree if parsed_tree is not None else ast.parse(code_text)
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
                elif (
                    isinstance(func, ast.Attribute)
                    and func.attr in ("append", "insert", "extend")
                    and isinstance(func.value, ast.Attribute)
                    and func.value.attr == "path"
                    and isinstance(func.value.value, ast.Name)
                    and func.value.value.id == "sys"
                ):
                    lineno = getattr(node, "lineno", 1)
                    if not self._is_permitted_app_root_bootstrap(tree, lineno, file_path):
                        violations.append({
                            "file": file_path,
                            "rule_id": "HERM-002",
                            "line": lineno,
                            "desc": f"Forbidden runtime sys.path mutation 'sys.path.{func.attr}()' detected",
                            "culprit": f"sys.path.{func.attr}",
                        })
            elif isinstance(node, ast.Assign):
                for tgt in node.targets:
                    if (
                        isinstance(tgt, ast.Attribute)
                        and tgt.attr == "path"
                        and isinstance(tgt.value, ast.Name)
                        and tgt.value.id == "sys"
                    ):
                        violations.append({
                            "file": file_path,
                            "rule_id": "HERM-002",
                            "line": getattr(node, "lineno", 1),
                            "desc": "Forbidden reassignment of 'sys.path' detected",
                            "culprit": "sys.path",
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
