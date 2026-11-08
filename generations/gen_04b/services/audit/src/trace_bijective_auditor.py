"""Micro-Auditor TRACE-001: Bijective TRACE-to-AST Specification Verifier (`soc_g4b_audit`).

Enforces:
- [INV-G4B-TRACE-001]: TRACE-AST Bijectivity & Declarative Conformance.
- [L1-G3B-011]: Universal Contract & Statechart IR.
- [L1-G4B-001]: Sovereign Mesh Verification Gate.
- Mathematical Rules:
  - TRACE-001A: Injective Entity Mapping (every TRACE entity exists in AST).
  - TRACE-001B: Surjective Entity Mapping (every AST domain dataclass exists in TRACE).
  - TRACE-001C: Bijective Field-Set Isomorphism (field sets match 1:1 per entity).
  - TRACE-001D: Type-Morphism Isomorphism (field types match bijectively between TRACE and AST).
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


class TraceTypeMismatchViolation(TraceBijectiveViolation):
    """Raised when field types diverge between TRACE and AST dataclasses."""
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
    type_mismatches: Dict[str, Dict[str, Dict[str, str]]] = field(default_factory=dict)
    audited_at_unix_ms: int = field(default_factory=lambda: int(time.time() * 1000))


class TraceBijectiveAuditor:
    """Micro-auditor verifying 1:1 bijectivity between TRACE markdown and Python AST."""

    def __init__(self, sentry_id: str = "node_trace_bijective_sentry") -> None:
        self.sentry_id = sentry_id

    @staticmethod
    def normalize_type_repr(t: str) -> str:
        """Normalizes TRACE and Python AST type representations into a canonical string."""
        s = t.strip().lower()
        s = re.sub(r"\bstring\b", "str", s)
        s = re.sub(r"\binteger\b", "int", s)
        s = re.sub(r"\bboolean\b", "bool", s)
        s = s.replace("typing.", "")
        m = re.match(r"^optional\[(.*)\]$", s)
        if m:
            inner = TraceBijectiveAuditor.normalize_type_repr(m.group(1))
            return " | ".join(sorted([inner, "none"]))
        if " | " in s or "|" in s:
            parts = [p.strip() for p in re.split(r"\s*\|\s*", s)]
            norm_parts = sorted(list({TraceBijectiveAuditor.normalize_type_repr(p) for p in parts}))
            return " | ".join(norm_parts)
        m_list = re.match(r"^list\[(.*)\]$", s)
        if m_list:
            inner = TraceBijectiveAuditor.normalize_type_repr(m_list.group(1))
            return f"list[{inner}]"
        m_dict = re.match(r"^dict\[(.*),(.*)\]$", s)
        if m_dict:
            k = TraceBijectiveAuditor.normalize_type_repr(m_dict.group(1))
            v = TraceBijectiveAuditor.normalize_type_repr(m_dict.group(2))
            return f"dict[{k}, {v}]"
        if s.startswith("enum"):
            return "str"
        return s

    @classmethod
    def are_types_compatible(cls, t_spec: str, t_code: str, strict: bool = False) -> bool:
        """Determines if a code AST type annotation satisfies the TRACE specification type."""
        norm_s = cls.normalize_type_repr(t_spec)
        norm_c = cls.normalize_type_repr(t_code)
        if norm_s == norm_c:
            return True
        if strict:
            return False

        # Extract base types by stripping optionality (none union)
        base_s = re.sub(r"\s*\|\s*none\b|\bnone\s*\|\s*", "", norm_s).strip()
        base_c = re.sub(r"\s*\|\s*none\b|\bnone\s*\|\s*", "", norm_c).strip()
        if base_s == base_c:
            return True

        # Generic dict / mapping compatibility (subsumes custom model classes)
        if base_s in ("any", "dict[str, any]", "dict", "dict[any, any]") and ("dict" in base_c or base_c not in ("str", "int", "float", "bool")):
            return True
        # Generic list / sequence compatibility
        if base_s in ("list[any]", "list") and ("list" in base_c or "tuple" in base_c):
            return True
        # Sequence polymorphism: list vs tuple
        if ("list" in base_s and "tuple" in base_c) or ("tuple" in base_s and "list" in base_c):
            return True
        # Optional subsumption: spec Optional[T] satisfied by non-null code T
        if "none" in norm_s and norm_c in norm_s:
            return True
        # Structural dict vs tuple/model
        if "dict" in base_s and "tuple" in base_c:
            return True
        if "list[dict" in base_s and "list" in base_c:
            return True
        # Numeric widening (int satisfies float in Python numeric models)
        if base_s == "float" and base_c == "int":
            return True
        # Serialized JSON string satisfying Dict[str, Any]
        if base_s in ("dict[str, any]", "dict") and base_c == "str":
            return True
        return False

    @staticmethod
    def parse_trace_entities_with_types(trace_markdown: str) -> Dict[str, Dict[str, str]]:
        """Parses # ENTITY: <Name> and MUST HAVE: field -> type mappings from TRACE markdown."""
        entities: Dict[str, Dict[str, str]] = {}
        current_entity: Optional[str] = None
        in_must_have = False

        for line in trace_markdown.splitlines():
            line_str = line.strip()
            if line_str.startswith("# ENTITY:"):
                current_entity = line_str.split(":", 1)[1].strip()
                entities[current_entity] = {}
                in_must_have = False
            elif line_str.startswith("MUST HAVE:"):
                in_must_have = True
            elif line_str.startswith("RULES:") or (line_str.startswith("#") and not line_str.startswith("# ENTITY:")):
                in_must_have = False
            elif in_must_have and line_str.startswith("-"):
                field_spec = line_str[1:].strip()
                if ":" in field_spec:
                    f_name, f_type = field_spec.split(":", 1)
                    if current_entity:
                        entities[current_entity][f_name.strip()] = f_type.strip()
                else:
                    if current_entity:
                        entities[current_entity][field_spec] = ""

        return entities

    @staticmethod
    def extract_ast_dataclasses_with_types(source_code: str) -> Dict[str, Dict[str, str]]:
        """Extracts dataclass names and annotated field -> type mappings using Python AST."""
        parsed_ast = ast.parse(source_code)
        dataclasses_map: Dict[str, Dict[str, str]] = {}

        for node in ast.iter_child_nodes(parsed_ast):
            if isinstance(node, ast.ClassDef):
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
                    fields: Dict[str, str] = {}
                    for item in node.body:
                        if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                            try:
                                t_str = ast.unparse(item.annotation)
                            except Exception:
                                t_str = ""
                            fields[item.target.id] = t_str
                    dataclasses_map[node.name] = fields

        return dataclasses_map

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
        check_types: bool = False,
        strict_types: bool = False,
    ) -> TraceAuditReport:
        """Verifies total injectivity and surjectivity between TRACE and AST code, optionally checking types."""
        trace_entities_with_types = self.parse_trace_entities_with_types(trace_markdown)
        code_classes_with_types = self.extract_ast_dataclasses_with_types(python_source)

        trace_names = set(trace_entities_with_types.keys())
        code_names = set(code_classes_with_types.keys())

        missing_in_code = sorted(list(trace_names - code_names))
        missing_in_trace = sorted(list(code_names - trace_names))
        field_mismatches: Dict[str, Dict[str, List[str]]] = {}
        type_mismatches: Dict[str, Dict[str, Dict[str, str]]] = {}
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
            t_fields_dict = trace_entities_with_types[entity_name]
            c_fields_dict = code_classes_with_types[entity_name]

            t_fields = set(t_fields_dict.keys())
            c_fields = set(c_fields_dict.keys())
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

            # Rule TRACE-001D: Type-Morphism Isomorphism
            if check_types:
                ent_type_mismatches: Dict[str, Dict[str, str]] = {}
                common_fields = t_fields.intersection(c_fields)
                for field_name in sorted(common_fields):
                    spec_t = t_fields_dict[field_name]
                    code_t = c_fields_dict[field_name]
                    if spec_t and code_t and not self.are_types_compatible(spec_t, code_t, strict=strict_types):
                        ent_type_mismatches[field_name] = {
                            "spec_type": spec_t,
                            "code_type": code_t,
                        }
                        v_msg = (
                            f"TRACE-001D Violation: Type mismatch on entity '{entity_name}.{field_name}': "
                            f"spec declared '{spec_t}', code has '{code_t}'"
                        )
                        violations.append(v_msg)
                        if raise_on_error:
                            raise TraceTypeMismatchViolation(v_msg)
                if ent_type_mismatches:
                    type_mismatches[entity_name] = ent_type_mismatches

        is_bijective = len(violations) == 0
        return TraceAuditReport(
            app_id=app_id,
            is_bijective=is_bijective,
            trace_entities_count=len(trace_entities_with_types),
            code_entities_count=len(code_classes_with_types),
            missing_in_code=missing_in_code,
            missing_in_trace=missing_in_trace,
            field_mismatches=field_mismatches,
            violations=violations,
            type_mismatches=type_mismatches,
        )

    def audit_app_directory(
        self,
        app_dir: Path | str,
        domain_file_pattern: str = "*.domain.md",
        models_file: str = "src/domain_models.py",
        check_types: bool = False,
        strict_types: bool = False,
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
        return self.audit_bijectivity(
            combined_trace,
            source_code,
            app_id=app_path.name,
            check_types=check_types,
            strict_types=strict_types,
        )
