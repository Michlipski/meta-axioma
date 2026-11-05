"""Pass 1: Bijective Specification Fidelity Evaluator ($S_{spec}$, 25%).

Inspects:
- Bijective AST symbol correspondence between prompt specification and emitted code.
- AST parsing across application modules to extract declared functions, classes, and HTTP endpoints.
- Verifies physical presence of expected domain verbs, REST endpoints, and domain models.
"""

from __future__ import annotations

import ast
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple

from ..domain_models import BenchmarkArchetype, EvaluationPassResult


class ASTSymbolExtractor(ast.NodeVisitor):
    """Extracts function names, class definitions, and route string constants from AST."""

    def __init__(self) -> None:
        self.declared_functions: Set[str] = set()
        self.declared_classes: Set[str] = set()
        self.detected_route_literals: Set[str] = set()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self.declared_functions.add(node.name.lower())
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self.declared_functions.add(node.name.lower())
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self.declared_classes.add(node.name)
        self.generic_visit(node)

    def visit_Constant(self, node: ast.Constant) -> None:
        if isinstance(node.value, str):
            val = node.value.strip()
            if val.startswith("/") or "{" in val:
                self.detected_route_literals.add(val)
        self.generic_visit(node)


class SpecFidelityEvaluator:
    """Evaluates Pass 1: Bijective Specification Fidelity ($S_{spec}$, Weight = 25%)."""

    def __init__(self, weight: float = 0.25) -> None:
        self.weight = weight

    def evaluate(self, app_dir: Path, archetype: BenchmarkArchetype) -> EvaluationPassResult:
        extractor = ASTSymbolExtractor()
        py_files = list(app_dir.rglob("*.py"))

        for py_file in py_files:
            try:
                content = py_file.read_text(encoding="utf-8")
                tree = ast.parse(content, filename=str(py_file))
                extractor.visit(tree)
            except Exception:
                pass

        # 1. Verb Coverage
        expected_verbs = [v.lower() for v in archetype.expected_verbs]
        found_verbs = [v for v in expected_verbs if v in extractor.declared_functions]
        verb_coverage = len(found_verbs) / len(expected_verbs) if expected_verbs else 1.0

        # 2. Endpoint Coverage
        expected_endpoints = archetype.expected_endpoints
        found_endpoints = []
        for ep in expected_endpoints:
            # ep is formatted like "GET /healthz" or "POST /keys/{key}"
            parts = ep.split()
            path_part = parts[-1] if parts else ep
            # Normalize path base, e.g. /keys/{key} -> /keys/
            clean_base = path_part.split("{")[0]
            matched = any(
                clean_base in r or r.startswith(clean_base) or clean_base == r
                for r in extractor.detected_route_literals
            )
            if matched:
                found_endpoints.append(ep)

        endpoint_coverage = len(found_endpoints) / len(expected_endpoints) if expected_endpoints else 1.0

        # 3. Model Coverage
        expected_models = archetype.expected_models
        found_models = [m for m in expected_models if m in extractor.declared_classes]
        model_coverage = len(found_models) / len(expected_models) if expected_models else 1.0

        # Composite raw score (0-100)
        raw_score = 100.0 * (
            0.40 * verb_coverage + 0.40 * endpoint_coverage + 0.20 * model_coverage
        )
        raw_score = round(max(0.0, min(100.0, raw_score)), 2)
        weighted_score = round(raw_score * self.weight, 2)

        details = {
            "py_files_scanned": len(py_files),
            "verb_coverage_pct": round(verb_coverage * 100.0, 1),
            "endpoint_coverage_pct": round(endpoint_coverage * 100.0, 1),
            "model_coverage_pct": round(model_coverage * 100.0, 1),
            "found_verbs": sorted(found_verbs),
            "missing_verbs": sorted([v for v in expected_verbs if v not in found_verbs]),
            "found_endpoints": found_endpoints,
            "missing_endpoints": [ep for ep in expected_endpoints if ep not in found_endpoints],
            "found_models": sorted(found_models),
            "missing_models": sorted([m for m in expected_models if m not in found_models]),
        }

        return EvaluationPassResult(
            pass_name="spec_fidelity",
            weight=self.weight,
            raw_score=raw_score,
            weighted_score=weighted_score,
            details=details,
            passed=(raw_score >= 70.0),
        )
