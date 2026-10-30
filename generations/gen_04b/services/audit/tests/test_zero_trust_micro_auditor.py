"""Unit & Adversarial Invariant Test Suite for Zero-Trust Micro-Auditor (`[L1-G3B-016]`).

Validates:
1. Clean source code passes with 0 violations and is_hermetic == True.
2. Interception of loopback addresses: '127.0.0.1', 'localhost', '::1', '0.0.0.0' (HERM-001).
3. Interception of sys.path.append, sys.path.insert, and sys.path = [...] (HERM-002).
4. Interception of os.chdir and hardcoded /tmp/ paths (HERM-003).
5. Python syntax error trapping and banned dynamic constructs: eval, exec (HERM-004).
"""

from __future__ import annotations

from pathlib import Path
import sys
import unittest

AUDIT_ROOT = Path(__file__).resolve().parent.parent
REPO_ROOT = AUDIT_ROOT.parent.parent.parent.parent
for p in [str(AUDIT_ROOT), str(AUDIT_ROOT / "src"), str(REPO_ROOT)]:
    if p not in sys.path:
        sys.path.insert(0, p)

from src.domain_models import (
    AuditSeverity,
    CodeLeafCandidate,
    HermeticAuditReport,
)
from src.zero_trust_micro_auditor import ZeroTrustMicroAuditor


class TestZeroTrustMicroAuditor(unittest.TestCase):
    """Exhaustive tests for AST hermetic boundary sentry and zero-trust auditor."""

    def setUp(self) -> None:
        self.auditor = ZeroTrustMicroAuditor()

    # 1. Clean Source Code Passes
    def test_clean_source_passes_with_zero_violations(self) -> None:
        clean_code = """
def compute_hash(data: bytes) -> str:
    import hashlib
    return hashlib.sha256(data).hexdigest()
"""
        report = self.auditor.audit_source(clean_code, leaf_id="leaf_clean")
        self.assertTrue(report.is_hermetic)
        self.assertEqual(len(report.violations), 0)
        self.assertEqual(report.banned_constructs_detected, 0)
        self.assertGreater(report.ast_nodes_scanned, 0)

    # 2. Intercept Loopback: IPv4 (127.0.0.1, 0.0.0.0)
    def test_intercept_loopback_ipv4(self) -> None:
        dirty_code = """
def connect():
    host = "127.0.0.1"
    bind = "0.0.0.0"
"""
        report = self.auditor.audit_source(dirty_code, leaf_id="leaf_loopback_v4")
        self.assertFalse(report.is_hermetic)
        rules = [v.rule_id for v in report.violations]
        self.assertIn("HERM-001", rules)
        culprits = [v.culprit_token for v in report.violations]
        self.assertIn("127.0.0.1", culprits)
        self.assertIn("0.0.0.0", culprits)
        for v in report.violations:
            self.assertEqual(v.severity, AuditSeverity.FATAL)

    # 3. Intercept Loopback: localhost & IPv6 (::1)
    def test_intercept_loopback_localhost_and_ipv6(self) -> None:
        dirty_code = """
def endpoints():
    local = "http://localhost:8080"
    v6 = "::1"
"""
        report = self.auditor.audit_source(dirty_code, leaf_id="leaf_loopback_v6")
        self.assertFalse(report.is_hermetic)
        rules = [v.rule_id for v in report.violations]
        self.assertIn("HERM-001", rules)
        culprits = [v.culprit_token for v in report.violations]
        self.assertIn("localhost", culprits)
        self.assertIn("::1", culprits)

    # 4. Intercept sys.path.append (HERM-002)
    def test_intercept_sys_path_append(self) -> None:
        dirty_code = """
import sys
sys.path.append('/custom/path')
"""
        report = self.auditor.audit_source(dirty_code, leaf_id="leaf_sys_path_append")
        self.assertFalse(report.is_hermetic)
        rules = [v.rule_id for v in report.violations]
        self.assertIn("HERM-002", rules)
        culprits = [v.culprit_token for v in report.violations]
        self.assertIn("sys.path.append", culprits)

    # 5. Intercept sys.path.insert (HERM-002)
    def test_intercept_sys_path_insert(self) -> None:
        dirty_code = """
import sys
sys.path.insert(0, '/root/escape')
"""
        report = self.auditor.audit_source(dirty_code, leaf_id="leaf_sys_path_insert")
        self.assertFalse(report.is_hermetic)
        rules = [v.rule_id for v in report.violations]
        self.assertIn("HERM-002", rules)
        culprits = [v.culprit_token for v in report.violations]
        self.assertIn("sys.path.insert", culprits)

    # 6. Intercept sys.path Reassignment (HERM-002)
    def test_intercept_sys_path_reassignment(self) -> None:
        dirty_code = """
import sys
sys.path = ['/tampered']
"""
        report = self.auditor.audit_source(dirty_code, leaf_id="leaf_sys_path_assign")
        self.assertFalse(report.is_hermetic)
        rules = [v.rule_id for v in report.violations]
        self.assertIn("HERM-002", rules)
        culprits = [v.culprit_token for v in report.violations]
        self.assertIn("sys.path", culprits)

    # 7. Intercept os.chdir (HERM-003)
    def test_intercept_os_chdir(self) -> None:
        dirty_code = """
import os
os.chdir('/tmp')
"""
        report = self.auditor.audit_source(dirty_code, leaf_id="leaf_chdir")
        self.assertFalse(report.is_hermetic)
        rules = [v.rule_id for v in report.violations]
        self.assertIn("HERM-003", rules)
        culprits = [v.culprit_token for v in report.violations]
        self.assertIn("os.chdir", culprits)

    # 8. Intercept Ambient /tmp/ and Traversal ../ (HERM-003)
    def test_intercept_ambient_tmp_and_traversal(self) -> None:
        dirty_code = """
def write_scratch():
    path = "/tmp/scratch.log"
    parent = "../escape/secret"
"""
        report = self.auditor.audit_source(dirty_code, leaf_id="leaf_tmp_traversal")
        self.assertFalse(report.is_hermetic)
        rules = [v.rule_id for v in report.violations]
        self.assertIn("HERM-003", rules)
        culprits = [v.culprit_token for v in report.violations]
        self.assertIn("/tmp", culprits)
        self.assertIn("../", culprits)

    # 9. Trap Python Syntax Error (HERM-004)
    def test_trap_python_syntax_error(self) -> None:
        broken_code = """
def unclosed_function(
    x = 10
"""
        report = self.auditor.audit_source(broken_code, leaf_id="leaf_syntax_error")
        self.assertFalse(report.is_hermetic)
        self.assertEqual(len(report.violations), 1)
        v = report.violations[0]
        self.assertEqual(v.rule_id, "HERM-004")
        self.assertEqual(v.severity, AuditSeverity.FATAL)
        self.assertIn("SyntaxError", v.culprit_token)

    # 10. Intercept Banned Dynamic Constructs (HERM-004) & Candidate Audit
    def test_intercept_banned_dynamic_constructs_and_audit_candidate(self) -> None:
        dirty_code = """
def run_dynamic(payload: str):
    eval(payload)
    exec(payload)
"""
        report = self.auditor.audit_source(dirty_code, leaf_id="leaf_dynamic")
        self.assertFalse(report.is_hermetic)
        rules = [v.rule_id for v in report.violations]
        self.assertIn("HERM-004", rules)
        culprits = [v.culprit_token for v in report.violations]
        self.assertIn("eval", culprits)
        self.assertIn("exec", culprits)

        # Also test audit_candidate with typed CodeLeafCandidate
        candidate = CodeLeafCandidate(
            leaf_id="leaf_cand_001",
            symbol_urn="urn:meta_axioma:leaf:valid",
            source_code="def safe_fn(): return 42",
        )
        cand_report = self.auditor.audit_candidate(candidate)
        self.assertTrue(cand_report.is_hermetic)


if __name__ == "__main__":
    unittest.main()
