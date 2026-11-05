#!/usr/bin/env python3
"""Comprehensive Empirical Test Suite for Mechanical Hook Interceptors (`tests/test_mechanical_hooks.py`).

Verifies:
- scripts/adversarial_plan_guard.py: Intercepts un-critiqued and cosmetic proposals.
- scripts/atomic_task_guard.py: Intercepts shell redirections, out-of-order task writes, and AST pitfalls.
- scripts/reality_coverage_runner.py: Executes subprocess smoke gates, detects mock contagion,
  and updates task manifests.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

from scripts.adversarial_plan_guard import evaluate_proposals_adversarial_rigor
from scripts.atomic_task_guard import (
    SHELL_REDIRECT_PATTERN,
    check_task_manifest_sequencing,
    verify_source_ast_pitfalls,
)
from scripts.reality_coverage_runner import (
    audit_test_mock_contagion,
    compute_file_sha256,
    execute_subprocess_smoke,
)


class TestAdversarialPlanGuard(unittest.TestCase):
    """Verifies that the adversarial plan guard blocks cosmetic compliance and requires real critique."""

    def test_cosmetic_proposal_rejected(self):
        cosmetic_content = """
        # Proposal
        ## Adversarial Risk & Red Team Critique
        Risk 1: High latency. Mitigated by clean architecture.
        """
        passed, msg = evaluate_proposals_adversarial_rigor(cosmetic_content)
        self.assertFalse(passed)
        self.assertIn("Cosmetic review detected", msg)

    def test_insufficient_vulnerabilities_rejected(self):
        shallow_content = """
        # Proposal
        ## Adversarial Risk & Red Team Critique
        VULN-001: Buffer overflow in parser.
        Mitigation: Added strict boundary length check.
        """
        passed, msg = evaluate_proposals_adversarial_rigor(shallow_content)
        self.assertFalse(passed)
        self.assertIn("Insufficient adversarial depth", msg)

    def test_rigorous_proposal_accepted(self):
        rigorous_content = """
        # Proposal
        ## Adversarial Risk & Red Team Critique
        ### Attack Vector 1: Distributed Partition & Split-Brain Commits
        Under a 90% microburst packet drop, the node could commit un-reconciled writes.
        Mitigation: Implemented Sheaf-Quorum consensus requiring supermajority signatures before commit.

        ### Attack Vector 2: Unbounded SQLite Lock Contention Under 10k Ingest
        Synchronous table locks cause thread pool starvation.
        Mitigation: Converted to SQLite WAL mode with asynchronous batch queue backpressure.

        ## Adversarial Red Team Certification Witness
        red_team_pass: true
        critical_vulnerabilities_found: 2
        """
        passed, msg = evaluate_proposals_adversarial_rigor(rigorous_content)
        self.assertTrue(passed, f"Failed with: {msg}")


class TestAtomicTaskGuard(unittest.TestCase):
    """Verifies that atomic task sequencing, shell redirection, and AST audits are physically enforced."""

    def test_shell_redirection_regex_detection(self):
        malicious_cmd = "echo 'corrupt' > apps/my_app/main.py"
        self.assertTrue(bool(SHELL_REDIRECT_PATTERN.search(malicious_cmd)))

        tee_cmd = "cat patch.py | tee apps/service/run.py"
        self.assertTrue(bool(SHELL_REDIRECT_PATTERN.search(tee_cmd)))

        safe_cmd = "git status"
        self.assertFalse(bool(SHELL_REDIRECT_PATTERN.search(safe_cmd)))

    def test_ast_micro_audit_catches_unbounded_network_call(self):
        bad_source = """
import requests
def fetch_data():
    return requests.get("https://api.external.com/data")
"""
        valid, msg = verify_source_ast_pitfalls(bad_source, "client.py")
        self.assertFalse(valid)
        self.assertIn("OP-003 Violation", msg)
        self.assertIn("timeout", msg)

    def test_ast_micro_audit_allows_bounded_network_call(self):
        good_source = """
import requests
def fetch_data():
    return requests.get("https://api.external.com/data", timeout=5.0)
"""
        valid, msg = verify_source_ast_pitfalls(good_source, "client.py")
        self.assertTrue(valid, msg)

    def test_task_sequencing_blocks_future_task(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            ws = Path(tmpdir)
            scratch = ws / ".scratch"
            scratch.mkdir(parents=True)
            manifest = scratch / "active_task_manifest.json"

            manifest_data = {
                "active_task_id": "T1",
                "tasks": [
                    {
                        "task_id": "T1",
                        "status": "IN_PROGRESS",
                        "allowed_files": ["apps/app/module1.py"],
                    },
                    {
                        "task_id": "T2",
                        "status": "PENDING",
                        "allowed_files": ["apps/app/module2.py"],
                    },
                ],
            }
            manifest.write_text(json.dumps(manifest_data), encoding="utf-8")

            # Writing to T1 file is valid
            valid_t1, _ = check_task_manifest_sequencing(ws / "apps/app/module1.py", [str(ws)])
            self.assertTrue(valid_t1)

            # Writing to T2 file while T1 is IN_PROGRESS is blocked
            valid_t2, msg_t2 = check_task_manifest_sequencing(ws / "apps/app/module2.py", [str(ws)])
            self.assertFalse(valid_t2)
            self.assertIn("ATOMIC TASK PROGRESSION VIOLATION", msg_t2)


class TestRealityCoverageRunner(unittest.TestCase):
    """Verifies subprocess entrypoint smoke and anti-mock analysis."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_subprocess_smoke_catches_import_crash(self):
        bad_entrypoint = Path(self.test_dir) / "broken_entrypoint.py"
        bad_entrypoint.write_text("import non_existent_super_package_xyz\n", encoding="utf-8")

        passed, msg = execute_subprocess_smoke(bad_entrypoint, timeout_seconds=2.0)
        self.assertFalse(passed)
        self.assertIn("Subprocess Entrypoint Smoke Crash", msg)

    def test_subprocess_smoke_passes_healthy_entrypoint(self):
        good_entrypoint = Path(self.test_dir) / "clean_entrypoint.py"
        good_entrypoint.write_text(
            "import sys\n"
            "if '--smoke-test' in sys.argv:\n"
            "    print('OK')\n"
            "    sys.exit(0)\n"
            "print('Ready')\n",
            encoding="utf-8",
        )

        passed, msg = execute_subprocess_smoke(good_entrypoint, timeout_seconds=3.0)
        self.assertTrue(passed, msg)

    def test_audit_mock_contagion_calculation(self):
        mock_test = Path(self.test_dir) / "test_mocked.py"
        mock_test.write_text(
            "from unittest.mock import patch, MagicMock\n"
            "def test_foo():\n"
            "    m = MagicMock()\n"
            "    assert m.called\n",
            encoding="utf-8",
        )

        ratio, assertions, mocks = audit_test_mock_contagion(mock_test)
        self.assertGreaterEqual(ratio, 0.5)
        self.assertGreaterEqual(mocks, 2)


if __name__ == "__main__":
    unittest.main()
