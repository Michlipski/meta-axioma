"""Micro-Auditor TRACE-001: Bijective TRACE-to-AST Specification Verifier (`soc_g4b_audit`).

Enforces:
- [INV-G4B-TRACE-001]: TRACE-AST Bijectivity & Declarative Conformance.
- [L1-G3B-011]: Universal Contract & Statechart IR.
- [L1-G4B-001]: Sovereign Mesh Verification Gate.
- Mathematical Rules:
  - TRACE-001A: Injective Entity Mapping (every TRACE entity exists in AST).
  - TRACE-001B: Surjective Entity Mapping (every AST domain dataclass exists in TRACE).
  - TRACE-001C: Bijective Field-Set Isomorphism (field sets match 1:1 per entity).
"""

from __future__ import annotations

import ast
from dataclasses import dataclass, field
import os
from pathlib import Path
import re
import time
from typing import Any, Dict, List, Optional, Set, Tuple


class TraceBijectiveViolation(Exception):
    """Base exception for TRACE-to-AST bijectivity discrepancies."""
    pass


class UnimplementedTraceEntityViolation(TraceBijectiveViolation):
    """Raised when an entity specified in TRACE has no corresponding AST class."""
    pass


class RogueCodeEntityViolation(TraceBijectiveViolation):
    """Raised when an AST dataclass exists without a corresponding TRACE specification."""
    pass


class TraceFieldMismatchViolation(TraceBijectiveViolation):
    """Raised when field sets diverge between TRACE and AST dataclasses."""
    pass


@dataclass(frozen=True)
class TraceAuditReport:
    """Audit report produced by TraceBijectiveAuditor."""
    app_id: str
    is_bijective: bool
    trace_entities_count: int
    code_entities_count: int
    missing_in_code: List[str]
    missing_in_trace: List[str]
    field_mismatches: Dict[str, Dict[str, List[str]]]
    violations: List[str]
    audited_at_unix_ms: int = field(default_factory=lambda: int(time.time() * 1000))


class TraceBijectiveAuditor:
    """Micro-auditor verifying 1:1 bijectivity between TRACE markdown and Python AST."""

    def __init__(self, sentry_id: str = "node_trace_bijective_sentry") -> None:
        self.sentry_id = sentry_id

    @staticmethod
    def parse_trace_entities(trace_markdown: str) -> Dict[str, List[str]]:
        """Parses # ENTITY: <Name> and MUST HAVE: fields from TRACE markdown."""
        entities: Dict[str, List[str]] = {}
        current_entity: Optional[str] = None
        in_must_have = False

        for line in trace_markdown.splitlines():
            line_str = line.strip()
            if line_str.startswith("# ENTITY:"):
                current_entity = line_str.split(":", 1)[1].strip()
                entities[current_entity] = []
                in_must_have = False
            elif line_str.startswith("MUST HAVE:"):
                in_must_have = True
            elif line_str.startswith("RULES:") or (line_str.startswith("#") and not line_str.startswith("# ENTITY:")):
                in_must_have = False
            elif in_must_have and line_str.startswith("-"):
                field_spec = line_str[1:].strip()
                field_name = field_spec.split(":", 1)[0].strip()
                if current_entity:
                    entities[current_entity].append(field_name)

        return entities

    @staticmethod
    def extract_ast_dataclasses(source_code: str) -> Dict[str, List[str]]:
        """Extracts dataclass names and annotated field names using Python AST parser."""
        parsed_ast = ast.parse(source_code)
        dataclasses_map: Dict[str, List[str]] = {}

        for node in ast.iter_child_nodes(parsed_ast):
            if isinstance(node, ast.ClassDef):
                # Check if decorated with dataclass
                is_dataclass = False
                for dec in node.decorator_list:
                    if isinstance(dec, ast.Name) and dec.id == "dataclass":
                        is_dataclass = True
                        break
                    elif isinstance(dec, ast.Call):
                        func = dec.func
                        if isinstance(func, ast.Name) and func.id == "dataclass":
                            is_dataclass = True
                            break

                if is_dataclass:
                    fields: List[str] = []
                    for item in node.body:
                        if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                            fields.append(item.target.id)
                    dataclasses_map[node.name] = fields

        return dataclasses_map

    def audit_bijectivity(
        self,
        trace_markdown: str,
        python_source: str,
        app_id: str = "app_under_audit",
        raise_on_error: bool = False,
    ) -> TraceAuditReport:
        """Verifies total injectivity and surjectivity between TRACE and AST code."""
        trace_entities = self.parse_trace_entities(trace_markdown)
        code_classes = self.extract_ast_dataclasses(python_source)

        trace_names = set(trace_entities.keys())
        code_names = set(code_classes.keys())

        missing_in_code = sorted(list(trace_names - code_names))
        missing_in_trace = sorted(list(code_names - trace_names))
        field_mismatches: Dict[str, Dict[str, List[str]]] = {}
        violations: List[str] = []

        if missing_in_code:
            v_msg = f"TRACE-001A Violation: Entities declared in TRACE but missing in AST: {missing_in_code}"
            violations.append(v_msg)
            if raise_on_error:
                raise UnimplementedTraceEntityViolation(v_msg)

        if missing_in_trace:
            v_msg = f"TRACE-001B Violation: AST dataclasses declared in code but missing in TRACE: {missing_in_trace}"
            violations.append(v_msg)
            if raise_on_error:
                raise RogueCodeEntityViolation(v_msg)

        common_entities = trace_names.intersection(code_names)
        for entity_name in sorted(common_entities):
            t_fields = set(trace_entities[entity_name])
            c_fields = set(code_classes[entity_name])
            extra_in_trace = sorted(list(t_fields - c_fields))
            extra_in_code = sorted(list(c_fields - t_fields))
            if extra_in_trace or extra_in_code:
                field_mismatches[entity_name] = {
                    "missing_in_code": extra_in_trace,
                    "missing_in_trace": extra_in_code,
                }
                v_msg = (
                    f"TRACE-001C Violation: Field mismatch on entity '{entity_name}': "
                    f"Trace extra: {extra_in_trace}, Code extra: {extra_in_code}"
                )
                violations.append(v_msg)
                if raise_on_error:
                    raise TraceFieldMismatchViolation(v_msg)

        is_bijective = len(violations) == 0
        return TraceAuditReport(
            app_id=app_id,
            is_bijective=is_bijective,
            trace_entities_count=len(trace_entities),
            code_entities_count=len(code_classes),
            missing_in_code=missing_in_code,
            missing_in_trace=missing_in_trace,
            field_mismatches=field_mismatches,
            violations=violations,
        )

    def audit_app_directory(
        self,
        app_dir: Path | str,
        domain_file_pattern: str = "*.domain.md",
        models_file: str = "src/domain_models.py",
    ) -> TraceAuditReport:
        """Audits an entire application root directory."""
        app_path = Path(app_dir).resolve()
        trace_domains_dir = app_path / "trace" / "domains"
        code_models_path = app_path / models_file

        if not trace_domains_dir.is_dir():
            raise FileNotFoundError(f"TRACE domains directory missing: {trace_domains_dir}")
        if not code_models_path.is_file():
            raise FileNotFoundError(f"Domain models source file missing: {code_models_path}")

        # Combine all domain.md files
        trace_md_parts: List[str] = []
        for df in sorted(trace_domains_dir.glob(domain_file_pattern)):
            trace_md_parts.append(df.read_text(encoding="utf-8"))
        combined_trace = "\n\n".join(trace_md_parts)

        source_code = code_models_path.read_text(encoding="utf-8")
        return self.audit_bijectivity(combined_trace, source_code, app_id=app_path.name)
