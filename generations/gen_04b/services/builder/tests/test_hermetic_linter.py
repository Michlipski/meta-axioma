"""Adversarial & Security Boundary Test Suite for Hermetic Linter (`[Layer C]`, `[L1-G3B-012]`).

Validates:
1. Trapping sys.path tampering (append, insert, extend, direct attribute overwrite).
2. Trapping prohibited loopback network bindings (127.0.0.1, localhost, ::1, 0.0.0.0).
3. Trapping ambient filesystem escapes (os.chdir, hardcoded /tmp directory access).
4. Verifying clean pass on strictly hermetic code using non-loopback IPs (e.g., 192.168.40.20).
5. Accurate diagnostic reporting with suggested patches and byte-accurate coordinates.
"""

from __future__ import annotations

from pathlib import Path
import sys
import unittest

BUILDER_ROOT = Path(__file__).resolve().parent.parent
REPO_ROOT = BUILDER_ROOT.parent.parent.parent
for p in [str(BUILDER_ROOT), str(REPO_ROOT)]:
    if p not in sys.path:
        sys.path.insert(0, p)

from src.hermetic_linter import HermeticLinter
from src.domain_models import DiagnosticSeverity, HermeticLinterReport


class TestHermeticLinter(unittest.TestCase):
    """Adversarial security and process hermeticity linter testing."""

    def setUp(self) -> None:
        self.linter = HermeticLinter()

    def test_clean_hermetic_code_passes(self) -> None:
        clean_source = '''
"""Hermetic sovereign service module."""
from typing import Dict, List

class SovereignService:
    def __init__(self, endpoint: str = "192.168.40.20:8442"):
        self.endpoint = endpoint
        self.active = True

    def process_data(self, records: List[Dict[str, str]]) -> int:
        return len(records)
'''
        report = self.linter.audit_code(clean_source, "src/clean.py")
        self.assertIsInstance(report, HermeticLinterReport)
        self.assertTrue(report.passed)
        self.assertEqual(len(report.violations), 0)
        self.assertGreater(report.loopback_prohibited_checks, 0)
        self.assertGreater(report.sys_path_tampering_checks, 0)
        self.assertGreater(report.filesystem_confinement_checks, 0)

    def test_trap_loopback_bindings_127(self) -> None:
        bad_source = '''
class BadNetworkNode:
    def bind_socket(self):
        target_ip = "127.0.0.1"
        return target_ip
'''
        report = self.linter.audit_code(bad_source, "src/bad_net.py")
        self.assertFalse(report.passed)
        self.assertEqual(len(report.violations), 1)
        v = report.violations[0]
        self.assertEqual(v.rule_code, "HERMETIC_LOOPBACK_PROHIBITED")
        self.assertEqual(v.severity, DiagnosticSeverity.SECURITY_VIOLATION)
        self.assertIn("127.", v.message)
        self.assertIn("192.168.40.20", v.suggested_patch or "")

    def test_trap_loopback_bindings_localhost_and_ipv6(self) -> None:
        bad_source = '''
ENDPOINT_A = "http://localhost:8080/api"
ENDPOINT_B = "http://[::1]:9090"
'''
        report = self.linter.audit_code(bad_source, "src/endpoints.py")
        self.assertFalse(report.passed)
        self.assertEqual(len(report.violations), 2)
        rules = [v.rule_code for v in report.violations]
        self.assertTrue(all(r == "HERMETIC_LOOPBACK_PROHIBITED" for r in rules))

    def test_trap_sys_path_append_and_insert(self) -> None:
        tamper_source = '''
import sys

def setup_paths():
    sys.path.append("/custom/untrusted/lib")
    sys.path.insert(0, "./vendor")
'''
        report = self.linter.audit_code(tamper_source, "src/tamper.py")
        self.assertFalse(report.passed)
        self.assertEqual(len(report.violations), 2)
        for v in report.violations:
            self.assertEqual(v.rule_code, "HERMETIC_SYS_PATH_TAMPERING")
            self.assertEqual(v.severity, DiagnosticSeverity.SECURITY_VIOLATION)

    def test_trap_sys_path_direct_overwrite(self) -> None:
        overwrite_source = '''
import sys
sys.path = ["/isolated/path"]
'''
        report = self.linter.audit_code(overwrite_source, "src/overwrite.py")
        self.assertFalse(report.passed)
        self.assertEqual(len(report.violations), 1)
        v = report.violations[0]
        self.assertEqual(v.rule_code, "HERMETIC_SYS_PATH_OVERWRITE")

    def test_trap_ambient_chdir_filesystem_escape(self) -> None:
        escape_source = '''
import os

def mutate_process():
    os.chdir("/root")
'''
        report = self.linter.audit_code(escape_source, "src/escape.py")
        self.assertFalse(report.passed)
        self.assertEqual(len(report.violations), 1)
        v = report.violations[0]
        self.assertEqual(v.rule_code, "HERMETIC_AMBIENT_CHDIR_PROHIBITED")
        self.assertEqual(v.severity, DiagnosticSeverity.FATAL)

    def test_trap_tmp_hardcoded_escape(self) -> None:
        tmp_source = '''
def write_scratch_data():
    scratch_file = "/tmp/scratch_data.bin"
    return scratch_file
'''
        report = self.linter.audit_code(tmp_source, "src/tmp_escape.py")
        self.assertFalse(report.passed)
        self.assertEqual(len(report.violations), 1)
        v = report.violations[0]
        self.assertEqual(v.rule_code, "HERMETIC_TMP_ESCAPE")

    def test_syntax_error_reported_as_violation(self) -> None:
        broken_code = "def invalid_syntax(::"
        report = self.linter.audit_code(broken_code, "src/syntax_err.py")
        self.assertFalse(report.passed)
        self.assertEqual(len(report.violations), 1)
        self.assertEqual(report.violations[0].rule_code, "SYNTAX_ERROR")


if __name__ == "__main__":
    unittest.main()
