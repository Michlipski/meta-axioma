"""Empirical Test Suite for Micro-Auditor TRACE-001 (TraceBijectiveAuditor).

Enforces:
- [INV-G4B-TRACE-001]: TRACE-AST Bijectivity & Declarative Conformance.
- [NEG-G1B-001]: Anti-Phantom Emission Gate.
"""

from __future__ import annotations

import os
from pathlib import Path
import unittest

from generations.gen_04b.services.audit.src.trace_bijective_auditor import (
    TraceBijectiveAuditor,
    UnimplementedTraceEntityViolation,
    RogueCodeEntityViolation,
    TraceFieldMismatchViolation,
)


class TestTraceBijectiveAuditor(unittest.TestCase):
    """Verifies mathematical correctness and error detection of TraceBijectiveAuditor."""

    def setUp(self) -> None:
        self.auditor = TraceBijectiveAuditor()
        self.repo_root = Path(__file__).resolve().parent.parent.parent.parent.parent.parent

    def test_bijective_match_synthetic(self) -> None:
        """Proves report is bijective when trace and code match perfectly."""
        trace_md = """
# ENTITY: UserSession
MUST HAVE:
- session_id: String
- user_id: String
- created_at: Integer

# ENTITY: AuthToken
MUST HAVE:
- token_str: String
- expires_at: Integer
"""
        code_py = """
from dataclasses import dataclass

@dataclass
class UserSession:
    session_id: str
    user_id: str
    created_at: int

@dataclass(frozen=True)
class AuthToken:
    token_str: str
    expires_at: int
"""
        report = self.auditor.audit_bijectivity(trace_md, code_py, "synthetic_app")
        self.assertTrue(report.is_bijective)
        self.assertEqual(len(report.violations), 0)
        self.assertEqual(report.trace_entities_count, 2)
        self.assertEqual(report.code_entities_count, 2)

    def test_missing_in_code_violation(self) -> None:
        """Detects TRACE-001A: entity declared in TRACE but missing in code."""
        trace_md = """
# ENTITY: RequiredEntity
MUST HAVE:
- id: String
"""
        code_py = "# Empty code"
        report = self.auditor.audit_bijectivity(trace_md, code_py)
        self.assertFalse(report.is_bijective)
        self.assertIn("RequiredEntity", report.missing_in_code)

        with self.assertRaises(UnimplementedTraceEntityViolation):
            self.auditor.audit_bijectivity(trace_md, code_py, raise_on_error=True)

    def test_missing_in_trace_violation(self) -> None:
        """Detects TRACE-001B: rogue dataclass in code without TRACE specification."""
        trace_md = "# No entities"
        code_py = """
from dataclasses import dataclass

@dataclass
class RogueDataclass:
    secret_key: str
"""
        report = self.auditor.audit_bijectivity(trace_md, code_py)
        self.assertFalse(report.is_bijective)
        self.assertIn("RogueDataclass", report.missing_in_trace)

        with self.assertRaises(RogueCodeEntityViolation):
            self.auditor.audit_bijectivity(trace_md, code_py, raise_on_error=True)

    def test_field_mismatch_violation(self) -> None:
        """Detects TRACE-001C: field set divergence between TRACE and code."""
        trace_md = """
# ENTITY: NodeState
MUST HAVE:
- node_id: String
- clock: Integer
"""
        code_py = """
from dataclasses import dataclass

@dataclass
class NodeState:
    node_id: str
    clock: int
    undocumented_field: str
"""
        report = self.auditor.audit_bijectivity(trace_md, code_py)
        self.assertFalse(report.is_bijective)
        self.assertIn("NodeState", report.field_mismatches)
        self.assertIn("undocumented_field", report.field_mismatches["NodeState"]["missing_in_trace"])

        with self.assertRaises(TraceFieldMismatchViolation):
            self.auditor.audit_bijectivity(trace_md, code_py, raise_on_error=True)

    def test_audit_live_gen04b_apps(self) -> None:
        """Audits all 5 live gen_04b applications and proves 100% bijectivity."""
        apps_root = self.repo_root / "generations" / "gen_04b" / "apps"
        target_apps = [
            "axioma_phenoflora",
            "axioma_canvas",
            "axioma_consensus",
            "axioma_crucible",
            "axioma_go",
        ]
        for app_name in target_apps:
            app_dir = apps_root / app_name
            report = self.auditor.audit_app_directory(app_dir)
            self.assertTrue(
                report.is_bijective,
                f"Application '{app_name}' failed TRACE-001 audit! Violations: {report.violations}"
            )
            self.assertGreater(report.trace_entities_count, 0)
            self.assertEqual(report.trace_entities_count, report.code_entities_count)


if __name__ == "__main__":
    unittest.main()
