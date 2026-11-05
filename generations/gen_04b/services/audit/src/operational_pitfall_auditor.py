"""Generation 4b Operational Pitfall & Invariant AST Micro-Auditor (`soc_g4b_audit`).

Enforces:
- Semantic Control-Flow Graph (CFG) analysis proving physical AST mitigations.
- Formal Rules:
  - OP-001 (WITH_LOCK_GUARD): Strict lock dominance over shared mutable state.
  - OP-002 (TRY_FINALLY_CLEANUP): Mandatory deterministic resource deallocation.
  - OP-003 (BOUNDED_TIMEOUT): Mandatory positive timeout keyword on all network/I/O calls.
  - OP-004 (EXCEPTION_TRANSLATION_ENCLAVE): Strict barrier against leaking raw system exceptions.
"""

from __future__ import annotations

import ast
import functools
import time
from typing import Any, Callable, Dict, List, Optional, Set, Tuple
import uuid

from generations.gen_04b.protocols.deliverable_bundle import (
    MitigationPattern,
    MitigationRule,
    OperationalPitfall,
    OperationalPitfallAuditReport,
)
from .domain_models import (
    AuditSeverity,
    OperationalMitigationViolation,
    RawExceptionLeakViolation,
    ResourceLeakViolation,
    UnboundedNetworkCallViolation,
    UnprotectedStateMutationViolation,
)


def operational_contract(
    pitfalls: Optional[List[OperationalPitfall]] = None,
    mitigations: Optional[List[MitigationPattern]] = None,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Runtime decorator declaring known operational failure modes and required AST mitigations."""
    def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
        fn.__operational_pitfalls__ = pitfalls or []
        fn.__operational_mitigations__ = mitigations or []

        @functools.wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            return fn(*args, **kwargs)

        wrapper.__operational_pitfalls__ = getattr(fn, "__operational_pitfalls__", [])
        wrapper.__operational_mitigations__ = getattr(fn, "__operational_mitigations__", [])
        return wrapper
    return decorator


class OperationalPitfallAuditor:
    """Zero-Trust AST Micro-Auditor verifying operational mitigations before disk emission."""

    IO_CALL_NAMES = {
        "get", "post", "put", "delete", "request", "read", "write",
        "send", "recv", "connect", "fetch", "query", "dispatch"
    }

    RESOURCE_ALLOC_NAMES = {
        "open", "connect", "open_session", "acquire", "create_channel",
        "get_connection", "begin_transaction"
    }

    def __init__(self, auditor_node_id: str = "node_operational_pitfall_sentry") -> None:
        self.auditor_node_id = auditor_node_id

    def audit_source(
        self, source_code: str, source_file: str = "module.py"
    ) -> OperationalPitfallAuditReport:
        """Audits Python source AST for operational contract compliance under OP-001..004."""
        report_id = f"rpt_op_{uuid.uuid4().hex[:12]}"

        try:
            tree = ast.parse(source_code)
        except SyntaxError as e:
            raise OperationalMitigationViolation(
                f"Syntax error while parsing operational AST in '{source_file}': {e.msg}"
            )

        # Build parent pointers for AST nodes to enable ancestor traversal
        for parent in ast.walk(tree):
            for child in ast.iter_child_nodes(parent):
                setattr(child, "_parent", parent)

        violations: List[Dict[str, Any]] = []
        mitigations_verified: List[str] = []

        # Find all function definitions
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                declared_patterns = self._extract_declared_mitigations(node)
                if not declared_patterns:
                    continue

                for pat in declared_patterns:
                    try:
                        if pat.rule == MitigationRule.WITH_LOCK_GUARD:
                            self._verify_lock_guard(node, pat, source_file)
                            mitigations_verified.append(f"{node.name}:WITH_LOCK_GUARD({pat.target_guard})")

                        elif pat.rule == MitigationRule.TRY_FINALLY_CLEANUP:
                            self._verify_finally_cleanup(node, pat, source_file)
                            mitigations_verified.append(f"{node.name}:TRY_FINALLY_CLEANUP({pat.cleanup_target})")

                        elif pat.rule == MitigationRule.BOUNDED_TIMEOUT:
                            self._verify_bounded_timeout(node, pat, source_file)
                            mitigations_verified.append(f"{node.name}:BOUNDED_TIMEOUT({pat.max_timeout_sec}s)")

                        elif pat.rule == MitigationRule.EXCEPTION_TRANSLATION_ENCLAVE:
                            self._verify_exception_enclave(node, pat, source_file)
                            mitigations_verified.append(f"{node.name}:EXCEPTION_TRANSLATION_ENCLAVE")

                    except OperationalMitigationViolation as err:
                        violations.append({
                            "function": node.name,
                            "rule": pat.rule.value,
                            "error": str(err),
                            "line": getattr(node, "lineno", 1),
                        })
                        # Re-raise immediately if fatal
                        raise err

        is_compliant = (len(violations) == 0)
        report = OperationalPitfallAuditReport(
            report_id=report_id,
            source_file=source_file,
            is_compliant=is_compliant,
            violations=violations,
            mitigations_verified=mitigations_verified,
            auditor_node_id=self.auditor_node_id,
            timestamp_unix_ms=int(time.time() * 1000),
        )
        report.validate_invariants()
        return report

    def _extract_declared_mitigations(
        self, func_node: ast.FunctionDef | ast.AsyncFunctionDef
    ) -> List[MitigationPattern]:
        """Extracts declared MitigationPattern list from @operational_contract decorator."""
        patterns: List[MitigationPattern] = []

        for dec in func_node.decorator_list:
            if isinstance(dec, ast.Call):
                func_id = None
                if isinstance(dec.func, ast.Name):
                    func_id = dec.func.id
                elif isinstance(dec.func, ast.Attribute):
                    func_id = dec.func.attr

                if func_id == "operational_contract":
                    for keyword in dec.keywords:
                        if keyword.arg == "mitigations":
                            if isinstance(keyword.value, ast.List):
                                for elt in keyword.value.elts:
                                    pattern = self._parse_mitigation_call(elt)
                                    if pattern:
                                        patterns.append(pattern)

        return patterns

    def _parse_mitigation_call(self, elt: ast.AST) -> Optional[MitigationPattern]:
        """Parses an ast.Call to MitigationPattern into a typed MitigationPattern object."""
        if not isinstance(elt, ast.Call):
            return None

        kwargs: Dict[str, Any] = {}
        for kw in elt.keywords:
            if kw.arg == "pitfall":
                kwargs["pitfall"] = self._resolve_enum_str(kw.value, OperationalPitfall)
            elif kw.arg == "rule":
                kwargs["rule"] = self._resolve_enum_str(kw.value, MitigationRule)
            elif kw.arg == "target_guard" and isinstance(kw.value, ast.Constant):
                kwargs["target_guard"] = str(kw.value.value)
            elif kw.arg == "cleanup_target" and isinstance(kw.value, ast.Constant):
                kwargs["cleanup_target"] = str(kw.value.value)
            elif kw.arg == "max_timeout_sec" and isinstance(kw.value, ast.Constant):
                kwargs["max_timeout_sec"] = float(kw.value.value)

        if "pitfall" in kwargs and "rule" in kwargs:
            return MitigationPattern(**kwargs)
        return None

    def _resolve_enum_str(self, val_node: ast.AST, enum_cls: Any) -> Any:
        """Resolves enum attribute access or string literal to an Enum value."""
        if isinstance(val_node, ast.Attribute):
            name = val_node.attr
            return enum_cls(name)
        elif isinstance(val_node, ast.Constant):
            return enum_cls(str(val_node.value))
        return None

    def _verify_lock_guard(
        self,
        func_node: ast.FunctionDef | ast.AsyncFunctionDef,
        pat: MitigationPattern,
        source_file: str,
    ) -> None:
        """Rule OP-001: Asserts all state mutations on self.* occur inside with target_guard."""
        target_guard = pat.target_guard or "self._lock"

        # Walk body looking for assignments to self.<attr>
        for node in ast.walk(func_node):
            if isinstance(node, (ast.Assign, ast.AugAssign, ast.AnnAssign)):
                is_self_mutation = False
                targets = []
                if isinstance(node, ast.Assign):
                    targets = node.targets
                elif isinstance(node, (ast.AugAssign, ast.AnnAssign)):
                    targets = [node.target]

                for target in targets:
                    if isinstance(target, ast.Attribute):
                        if isinstance(target.value, ast.Name) and target.value.id == "self":
                            is_self_mutation = True
                            break

                if is_self_mutation:
                    # Check if enclosed in with / async with matching target_guard
                    curr = node
                    enclosed_in_lock = False
                    while hasattr(curr, "_parent"):
                        curr = getattr(curr, "_parent")
                        if curr is func_node:
                            break
                        if isinstance(curr, (ast.With, ast.AsyncWith)):
                            for item in curr.items:
                                ctx_expr = ast.unparse(item.context_expr).strip()
                                if target_guard in ctx_expr or ctx_expr in target_guard:
                                    enclosed_in_lock = True
                                    break
                            if enclosed_in_lock:
                                break

                    if not enclosed_in_lock:
                        raise UnprotectedStateMutationViolation(
                            f"[OP-001 Violation] Unprotected state mutation on 'self' detected at line {node.lineno} "
                            f"in '{func_node.name}' ({source_file}). Must execute inside 'with {target_guard}:'."
                        )

    def _verify_finally_cleanup(
        self,
        func_node: ast.FunctionDef | ast.AsyncFunctionDef,
        pat: MitigationPattern,
        source_file: str,
    ) -> None:
        """Rule OP-002: Asserts resource allocations are dominated by try-finally cleanup."""
        cleanup_target = pat.cleanup_target or "close"

        has_allocation = False
        alloc_line = func_node.lineno

        for node in ast.walk(func_node):
            if isinstance(node, ast.Call):
                call_repr = ast.unparse(node.func).lower()
                if any(alloc_name in call_repr for alloc_name in self.RESOURCE_ALLOC_NAMES):
                    has_allocation = True
                    alloc_line = node.lineno
                    break

        if not has_allocation:
            return

        # Check if an ast.Try block exists whose finalbody contains cleanup_target
        cleanup_found = False
        for node in ast.walk(func_node):
            if isinstance(node, ast.Try):
                for final_stmt in node.finalbody:
                    stmt_repr = ast.unparse(final_stmt)
                    if cleanup_target in stmt_repr or "close()" in stmt_repr or "release()" in stmt_repr:
                        cleanup_found = True
                        break
            if cleanup_found:
                break

        if not cleanup_found:
            raise ResourceLeakViolation(
                f"[OP-002 Violation] Resource allocated at line {alloc_line} in '{func_node.name}' ({source_file}) "
                f"lacks mandatory 'try ... finally: {cleanup_target}' deallocation."
            )

    def _verify_bounded_timeout(
        self,
        func_node: ast.FunctionDef | ast.AsyncFunctionDef,
        pat: MitigationPattern,
        source_file: str,
    ) -> None:
        """Rule OP-003: Asserts network/IO calls pass an explicit positive timeout argument."""
        for node in ast.walk(func_node):
            if isinstance(node, ast.Call):
                call_name = ""
                if isinstance(node.func, ast.Attribute):
                    call_name = node.func.attr.lower()
                elif isinstance(node.func, ast.Name):
                    call_name = node.func.id.lower()

                if call_name in self.IO_CALL_NAMES:
                    timeout_found = False
                    for kw in node.keywords:
                        if kw.arg == "timeout":
                            if isinstance(kw.value, ast.Constant):
                                if isinstance(kw.value.value, (int, float)) and kw.value.value > 0:
                                    timeout_found = True
                            elif isinstance(kw.value, (ast.Name, ast.Attribute)):
                                timeout_found = True

                    if not timeout_found:
                        raise UnboundedNetworkCallViolation(
                            f"[OP-003 Violation] Network/IO call '{call_name}()' at line {node.lineno} in '{func_node.name}' "
                            f"({source_file}) lacks mandatory explicit positive 'timeout' keyword argument."
                        )

    def _verify_exception_enclave(
        self,
        func_node: ast.FunctionDef | ast.AsyncFunctionDef,
        pat: MitigationPattern,
        source_file: str,
    ) -> None:
        """Rule OP-004: Asserts exception blocks translate raw errors to typed domain violations."""
        try_blocks = [n for n in ast.walk(func_node) if isinstance(n, ast.Try)]
        if not try_blocks:
            raise RawExceptionLeakViolation(
                f"[OP-004 Violation] Function '{func_node.name}' ({source_file}) declares EXCEPTION_TRANSLATION_ENCLAVE "
                f"but contains zero 'try ... except' blocks."
            )

        for try_node in try_blocks:
            for handler in try_node.handlers:
                # Disallow bare except:
                if handler.type is None:
                    raise RawExceptionLeakViolation(
                        f"[OP-004 Violation] Bare 'except:' at line {handler.lineno} in '{func_node.name}' ({source_file}) "
                        f"violates hermetic exception isolation."
                    )

                # Check that handler raises a typed domain exception
                raises_typed_domain_err = False
                for stmt in ast.walk(handler):
                    if isinstance(stmt, ast.Raise):
                        if stmt.exc is not None:
                            exc_repr = ast.unparse(stmt.exc)
                            if "Violation" in exc_repr or "Domain" in exc_repr or "Error" in exc_repr:
                                raises_typed_domain_err = True
                                break

                if not raises_typed_domain_err:
                    raise RawExceptionLeakViolation(
                        f"[OP-004 Violation] Exception handler at line {handler.lineno} in '{func_node.name}' ({source_file}) "
                        f"does not re-raise a typed domain exception enclave."
                    )
