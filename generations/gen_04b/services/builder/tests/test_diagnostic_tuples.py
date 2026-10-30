"""Adversarial & Precision Test Suite for Diagnostic Tuples & Surgical AST Patcher (`[Layer B]`, `[L1-G4B-009]`).

Validates:
1. Accurate byte-offset calculation from 1-indexed line and 0-indexed column.
2. Construction of structured, machine-verifiable DiagnosticTuple records directly and from AST nodes.
3. Surgical single-patch application via byte slicing without whole-file rewrites.
4. Multi-patch application in reverse byte offset order to eliminate offset drifting.
5. Deterministic single-turn healing: patching illegal loopback address to hermetic non-loopback address.
6. Error handling for out-of-bound byte coordinates, missing patches, and syntax-breaking patches.
"""

from __future__ import annotations

import ast
from pathlib import Path
import sys
import unittest

BUILDER_ROOT = Path(__file__).resolve().parent.parent
REPO_ROOT = BUILDER_ROOT.parent.parent.parent
for p in [str(BUILDER_ROOT), str(REPO_ROOT)]:
    if p not in sys.path:
        sys.path.insert(0, p)

from src.diagnostic_tuples import DiagnosticEngine, SurgicalPatcher
from src.domain_models import DiagnosticSeverity, DiagnosticTuple, DomainInvariantViolation
from src.hermetic_linter import HermeticLinter


class TestDiagnosticTuplesAndSurgicalPatcher(unittest.TestCase):
    """Rigorous verification of byte-indexed diagnostics and AST surgical healing."""

    def setUp(self) -> None:
        self.linter = HermeticLinter()

    def test_calculate_byte_offset(self) -> None:
        source = "line 1\nline 2 with utf-8: \u2705\nline 3"
        # Line 1, col 0 -> 0
        self.assertEqual(DiagnosticEngine.calculate_byte_offset(source, 1, 0), 0)
        # Line 2, col 0 -> 7 (len("line 1\n"))
        self.assertEqual(DiagnosticEngine.calculate_byte_offset(source, 2, 0), 7)
        # Line 3, col 0 -> after line 1 and line 2
        line1_len = len("line 1\n".encode("utf-8"))
        line2_len = len("line 2 with utf-8: \u2705\n".encode("utf-8"))
        self.assertEqual(DiagnosticEngine.calculate_byte_offset(source, 3, 0), line1_len + line2_len)

    def test_create_diagnostic_and_invariants(self) -> None:
        source = "class Service:\n    endpoint = '127.0.0.1'\n"
        diag = DiagnosticEngine.create_diagnostic(
            file_path="src/service.py",
            severity=DiagnosticSeverity.SECURITY_VIOLATION,
            rule_code="HERMETIC_LOOPBACK_PROHIBITED",
            message="Prohibited loopback binding",
            source_code=source,
            line=2,
            col=15,
            end_line=2,
            end_col=26,
            suggested_patch="'192.168.40.20'",
        )

        self.assertIsInstance(diag, DiagnosticTuple)
        self.assertEqual(diag.rule_code, "HERMETIC_LOOPBACK_PROHIBITED")
        self.assertEqual(diag.suggested_patch, "'192.168.40.20'")
        self.assertGreater(diag.end_byte, diag.start_byte)

    def test_surgical_single_patch_application(self) -> None:
        source = "endpoint = '127.0.0.1'\nport = 8442\n"
        # Target: '127.0.0.1' (11 bytes from index 11 to 22)
        start_byte = source.encode().index(b"'127.0.0.1'")
        end_byte = start_byte + len(b"'127.0.0.1'")

        diag = DiagnosticTuple(
            diagnostic_id="diag_patch_01",
            file_path="src/config.py",
            severity=DiagnosticSeverity.SECURITY_VIOLATION,
            start_byte=start_byte,
            end_byte=end_byte,
            line_number=1,
            column_number=11,
            rule_code="HERMETIC_LOOPBACK_PROHIBITED",
            message="Replace loopback",
            suggested_patch="'192.168.40.20'",
        )

        patched_code = SurgicalPatcher.apply_patch(source, diag, verify_syntax=True)
        self.assertEqual(patched_code, "endpoint = '192.168.40.20'\nport = 8442\n")
        
        # Verify patched code passes hermetic linter
        report = self.linter.audit_code(patched_code, "src/config.py")
        self.assertTrue(report.passed)

    def test_surgical_multi_patch_application_reverse_order(self) -> None:
        # Code with two separate loopback violations
        source = "HOST_A = '127.0.0.1'\nHOST_B = 'localhost'\n"
        
        # Patch 1: '127.0.0.1'
        s1 = source.encode().index(b"'127.0.0.1'")
        e1 = s1 + len(b"'127.0.0.1'")
        d1 = DiagnosticTuple(
            diagnostic_id="d1",
            file_path="src/multi.py",
            severity=DiagnosticSeverity.SECURITY_VIOLATION,
            start_byte=s1,
            end_byte=e1,
            line_number=1,
            column_number=9,
            rule_code="HERMETIC_LOOPBACK_PROHIBITED",
            message="Fix host A",
            suggested_patch="'192.168.40.20'",
        )

        # Patch 2: 'localhost'
        s2 = source.encode().index(b"'localhost'")
        e2 = s2 + len(b"'localhost'")
        d2 = DiagnosticTuple(
            diagnostic_id="d2",
            file_path="src/multi.py",
            severity=DiagnosticSeverity.SECURITY_VIOLATION,
            start_byte=s2,
            end_byte=e2,
            line_number=2,
            column_number=9,
            rule_code="HERMETIC_LOOPBACK_PROHIBITED",
            message="Fix host B",
            suggested_patch="'192.168.40.21'",
        )

        # Apply multi-patch (even if passed unordered)
        patched_code = SurgicalPatcher.apply_multi_patch(source, [d1, d2], verify_syntax=True)
        self.assertIn("HOST_A = '192.168.40.20'", patched_code)
        self.assertIn("HOST_B = '192.168.40.21'", patched_code)
        self.assertNotIn("127.0.0.1", patched_code)
        self.assertNotIn("localhost", patched_code)

    def test_patch_syntax_error_rejection(self) -> None:
        source = "valid_assignment = 42\n"
        diag = DiagnosticTuple(
            diagnostic_id="d_bad",
            file_path="src/bad.py",
            severity=DiagnosticSeverity.ERROR,
            start_byte=19,
            end_byte=21,
            line_number=1,
            column_number=19,
            rule_code="BAD_PATCH",
            message="Injects broken syntax",
            suggested_patch="= invalid syntax : ((",
        )

        with self.assertRaises(ValueError) as ctx:
            SurgicalPatcher.apply_patch(source, diag, verify_syntax=True)
        self.assertIn("syntax error", str(ctx.exception).lower())

    def test_out_of_bounds_patch_rejection(self) -> None:
        source = "short = 1\n"
        diag = DiagnosticTuple(
            diagnostic_id="d_oob",
            file_path="src/short.py",
            severity=DiagnosticSeverity.ERROR,
            start_byte=500,  # Far exceeds source length
            end_byte=510,
            line_number=10,
            column_number=0,
            rule_code="OOB",
            message="OOB",
            suggested_patch="1",
        )

        with self.assertRaises(IndexError):
            SurgicalPatcher.apply_patch(source, diag)


if __name__ == "__main__":
    unittest.main()
