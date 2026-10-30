"""Generation 4b Byte-Indexed Diagnostic Tuple & Surgical AST Patcher (`[Layer B]`).

Enforces:
- Deterministic, byte-accurate error localization `(start_byte, end_byte, line, col)`.
- Machine-verifiable surgical AST node replacement without reformatting or comment loss.
- Reverse-offset multi-patch application preventing offset drifting.
- Validation of patched syntax via AST parsing.
"""

from __future__ import annotations

import ast
import hashlib
import uuid
from typing import List, Optional, Tuple

from .domain_models import (
    DiagnosticSeverity,
    DiagnosticTuple,
    DomainInvariantViolation,
)


class DiagnosticEngine:
    """Generates machine-verifiable byte-indexed diagnostic tuples."""

    @staticmethod
    def calculate_byte_offset(source_code: str, line: int, col: int) -> int:
        """Translates 1-indexed line and 0-indexed column into 0-indexed byte offset."""
        lines = source_code.splitlines(keepends=True)
        if line < 1 or line > len(lines):
            return len(source_code.encode("utf-8"))
        
        prefix = "".join(lines[: line - 1])
        prefix_bytes = len(prefix.encode("utf-8"))
        target_line = lines[line - 1]
        col_bytes = len(target_line[:col].encode("utf-8"))
        return prefix_bytes + col_bytes

    @classmethod
    def create_diagnostic(
        cls,
        file_path: str,
        severity: DiagnosticSeverity,
        rule_code: str,
        message: str,
        source_code: str,
        line: int,
        col: int,
        end_line: Optional[int] = None,
        end_col: Optional[int] = None,
        suggested_patch: Optional[str] = None,
    ) -> DiagnosticTuple:
        """Constructs a validated DiagnosticTuple using line and column coordinates."""
        start_byte = cls.calculate_byte_offset(source_code, line, col)
        if end_line is not None and end_col is not None:
            end_byte = cls.calculate_byte_offset(source_code, end_line, end_col)
        else:
            end_byte = start_byte + 1

        diag_id = f"diag_{hashlib.sha256(f'{file_path}:{line}:{col}:{rule_code}'.encode()).hexdigest()[:12]}"
        diag = DiagnosticTuple(
            diagnostic_id=diag_id,
            file_path=file_path,
            severity=severity,
            start_byte=start_byte,
            end_byte=max(start_byte, end_byte),
            line_number=line,
            column_number=col,
            rule_code=rule_code,
            message=message,
            suggested_patch=suggested_patch,
        )
        diag.validate_invariants()
        return diag

    @classmethod
    def create_from_ast_node(
        cls,
        file_path: str,
        source_code: str,
        node: ast.AST,
        severity: DiagnosticSeverity,
        rule_code: str,
        message: str,
        suggested_patch: Optional[str] = None,
    ) -> DiagnosticTuple:
        """Constructs a DiagnosticTuple directly from an ast.AST node location."""
        line = getattr(node, "lineno", 1)
        col = getattr(node, "col_offset", 0)
        end_line = getattr(node, "end_lineno", line)
        end_col = getattr(node, "end_col_offset", col + 1)
        return cls.create_diagnostic(
            file_path=file_path,
            severity=severity,
            rule_code=rule_code,
            message=message,
            source_code=source_code,
            line=line,
            col=col,
            end_line=end_line,
            end_col=end_col,
            suggested_patch=suggested_patch,
        )


class SurgicalPatcher:
    """Applies byte-exact surgical replacements to source files without full rewriting."""

    @staticmethod
    def apply_patch(source_code: str, diagnostic: DiagnosticTuple, verify_syntax: bool = True) -> str:
        """Applies a single diagnostic patch using byte slicing."""
        if diagnostic.suggested_patch is None:
            raise ValueError(f"Diagnostic {diagnostic.diagnostic_id} does not contain a suggested_patch.")

        source_bytes = source_code.encode("utf-8")
        if diagnostic.start_byte > len(source_bytes) or diagnostic.end_byte > len(source_bytes):
            raise IndexError(
                f"Diagnostic byte range [{diagnostic.start_byte}:{diagnostic.end_byte}] "
                f"exceeds source size ({len(source_bytes)} bytes)."
            )

        patch_bytes = diagnostic.suggested_patch.encode("utf-8")
        patched_bytes = source_bytes[: diagnostic.start_byte] + patch_bytes + source_bytes[diagnostic.end_byte :]
        patched_code = patched_bytes.decode("utf-8")

        if verify_syntax:
            try:
                ast.parse(patched_code, filename=diagnostic.file_path)
            except SyntaxError as err:
                raise ValueError(f"Surgical patch caused syntax error: {err.msg} at line {err.lineno}")

        return patched_code

    @classmethod
    def apply_multi_patch(cls, source_code: str, diagnostics: List[DiagnosticTuple], verify_syntax: bool = True) -> str:
        """Applies multiple non-overlapping patches in reverse byte order."""
        patchable = [d for d in diagnostics if d.suggested_patch is not None]
        if not patchable:
            return source_code

        # Sort descending by start_byte to maintain valid offsets
        sorted_diags = sorted(patchable, key=lambda d: d.start_byte, reverse=True)

        current_code = source_code
        for diag in sorted_diags:
            current_code = cls.apply_patch(current_code, diag, verify_syntax=False)

        if verify_syntax:
            try:
                ast.parse(current_code)
            except SyntaxError as err:
                raise ValueError(f"Multi-patch caused syntax error: {err.msg}")

        return current_code
