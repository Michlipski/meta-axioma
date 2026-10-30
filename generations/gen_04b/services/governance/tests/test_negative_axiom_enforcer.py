"""Adversarial & Zero-Bypass Test Suite for Negative Axiom Enforcer (`soc_g4b_governance`).

Enforces:
- Invariant [L1-G3B-016]: Zero-Bypass Micro-Auditor Interception.
- Invariant [L1-G3B-012]: Dedicated Non-Loopback Network Topology.
- Invariant [NEG-G1B-001]: Anti-Phantom Emission Gate.
- Canonical Human Negative Axioms NEG-001 through NEG-G4B-001.
"""

from __future__ import annotations

import ast
from pathlib import Path
import sys
import unittest

GOV_ROOT = Path(__file__).resolve().parent.parent
REPO_ROOT = GOV_ROOT.parent.parent.parent.parent
for p in [str(GOV_ROOT), str(GOV_ROOT / "src"), str(REPO_ROOT)]:
    if p not in sys.path:
        sys.path.insert(0, p)

from src.domain_models import (
    AxiomSeverity,
    GovernanceDomainInvariantViolation,
    NegativeAxiom,
    VetoActionType,
)
from src.negative_axiom_enforcer import (
    NegativeAxiomASTVisitor,
    NegativeAxiomEnforcer,
)


class TestNegativeAxiomEnforcer(unittest.TestCase):
    """Exhaustive adversarial test cases for AST scanning, pattern detection, and topology audit."""

    def setUp(self) -> None:
        self.enforcer = NegativeAxiomEnforcer(service_endpoint="192.168.40.50:8448")

    def test_initialization_with_loopback_rejected(self) -> None:
        """Enforcer itself cannot be bound to loopback."""
        with self.assertRaises(GovernanceDomainInvariantViolation):
            NegativeAxiomEnforcer(service_endpoint="127.0.0.1:8448")
        with self.assertRaises(GovernanceDomainInvariantViolation):
            NegativeAxiomEnforcer(service_endpoint="localhost:8448")

    def test_canonical_axioms_seeded(self) -> None:
        """Verifies all 10 canonical negative axioms are seeded upon construction."""
        active = self.enforcer.get_active_axioms()
        self.assertGreaterEqual(len(active), 10)
        ids = {ax.axiom_id for ax in active}
        self.assertIn("NEG-001", ids)
        self.assertIn("NEG-002", ids)
        self.assertIn("NEG-003", ids)
        self.assertIn("NEG-004", ids)
        self.assertIn("NEG-005", ids)
        self.assertIn("NEG-G1B-001", ids)
        self.assertIn("NEG-G2B-001", ids)
        self.assertIn("NEG-G4B-001", ids)

    def test_ast_scan_detects_eval(self) -> None:
        """AST scanner intercepts eval() call."""
        code = "result = eval('2 + 2')"
        violations = self.enforcer.scan_source_code(code, "test_eval.py")
        self.assertTrue(any("eval" in v.detected_pattern for v in violations))
        self.assertTrue(any(v.axiom_id == "NEG-001" for v in violations))

    def test_ast_scan_detects_exec(self) -> None:
        """AST scanner intercepts exec() call."""
        code = "exec('import sys; sys.exit(1)')"
        violations = self.enforcer.scan_source_code(code, "test_exec.py")
        self.assertTrue(any("exec" in v.detected_pattern for v in violations))
        self.assertTrue(any(v.veto_action == VetoActionType.HALT_COMPILATION for v in violations))

    def test_ast_scan_detects_os_system(self) -> None:
        """AST scanner intercepts os.system() call."""
        code = "import os\nos.system('rm -rf /')"
        violations = self.enforcer.scan_source_code(code, "test_os_system.py")
        self.assertTrue(any("os.system" in v.detected_pattern for v in violations))

    def test_ast_scan_detects_subprocess_shell_true(self) -> None:
        """AST scanner intercepts subprocess with shell=True."""
        code = "import subprocess\nsubprocess.Popen(['ls', '-la'], shell=True)"
        violations = self.enforcer.scan_source_code(code, "test_subprocess.py")
        self.assertTrue(any("shell=True" in v.detected_pattern for v in violations))

    def test_ast_scan_allows_subprocess_shell_false(self) -> None:
        """Subprocess without shell=True or with shell=False is not flagged as shell violation."""
        code = "import subprocess\nsubprocess.run(['ls', '-la'], shell=False)"
        violations = self.enforcer.scan_source_code(code, "test_subprocess_safe.py")
        shell_violations = [v for v in violations if "shell=True" in v.detected_pattern]
        self.assertEqual(len(shell_violations), 0)

    def test_ast_scan_detects_loopback_in_literal_constants(self) -> None:
        """AST visitor flags loopback addresses inside string constants."""
        loopback_samples = [
            "HOST = '127.0.0.1'",
            "URL = 'http://localhost:8080/api'",
            "IPV6_LOCAL = '::1'",
            "BIND_ALL = '0.0.0.0'",
        ]
        for sample in loopback_samples:
            violations = self.enforcer.scan_source_code(sample, "test_loopback.py")
            self.assertTrue(
                any("loopback" in v.description.lower() or "loopback" in v.detected_pattern.lower() for v in violations),
                f"Failed to trap loopback in: {sample}",
            )

    def test_hardcoded_secret_detection(self) -> None:
        """Detects AWS access keys, OpenAI tokens, and hardcoded passwords."""
        leaks = [
            "AWS_KEY = 'AKIAIOSFODNN7EXAMPLE'",
            "openai_api_key = 'sk-abcdef1234567890abcdef1234567890'",
            "password = 'super_secret_admin_password_123'",
        ]
        for leak in leaks:
            violations = self.enforcer.scan_source_code(leak, "test_secrets.py")
            self.assertTrue(
                any(v.severity == AxiomSeverity.SECURITY_BREACH for v in violations),
                f"Failed to detect secret in: {leak}",
            )

    def test_bypass_flag_detection(self) -> None:
        """Detects attempts to bypass sandboxes, verification, or audits."""
        bypasses = [
            "config = {'bypass_sandbox': True}",
            "args = 'dry_run=False'",
            "options = {'ignore_audit': True}",
            "params = {'skip_verification': True}",
        ]
        for bp in bypasses:
            violations = self.enforcer.scan_source_code(bp, "test_bypass.py")
            self.assertTrue(
                any("bypass" in v.detected_pattern.lower() or "bypass" in v.description.lower() for v in violations),
                f"Failed to detect bypass in: {bp}",
            )

    def test_placeholder_uuid_detection(self) -> None:
        """Detects PLACEHOLDER_UUID and unreconciled_cid strings."""
        code = "subagent_id = 'PLACEHOLDER_UUID_0001'"
        violations = self.enforcer.scan_source_code(code, "test_uuid.py")
        self.assertTrue(any("PLACEHOLDER_UUID" in v.detected_pattern for v in violations))

    def test_syntax_error_handled_gracefully(self) -> None:
        """Syntax errors in candidate code are caught and emitted as fatal AST violations."""
        bad_syntax = "def broken_func(:\n    pass"
        violations = self.enforcer.scan_source_code(bad_syntax, "syntax_err.py")
        self.assertGreaterEqual(len(violations), 1)
        self.assertEqual(violations[0].detected_pattern, "SyntaxError")
        self.assertEqual(violations[0].severity, AxiomSeverity.FATAL_VETO)

    def test_topology_scanning_traps_loopback_and_centralization(self) -> None:
        """Topology scan rejects loopback bindings and centralized topologies."""
        bad_topo = {
            "nodes": {
                "builder": {"endpoint": "127.0.0.1:8442"},
                "governance": {"endpoint": "192.168.40.50:8448"},
            },
            "architecture": "centralized_master_slave",
        }
        violations = self.enforcer.scan_topology(bad_topo)
        self.assertGreaterEqual(len(violations), 1)
        self.assertTrue(any("loopback" in v.description.lower() or "127.0.0.1" in v.detected_pattern for v in violations))

    def test_topology_scanning_allows_clean_mesh(self) -> None:
        """Clean decentralized mesh topology passes with zero violations."""
        clean_topo = {
            "nodes": {
                "research": {"endpoint": "192.168.40.10:8440"},
                "builder": {"endpoint": "192.168.40.20:8442"},
                "audit": {"endpoint": "192.168.40.30:8444"},
                "telemetry": {"endpoint": "192.168.40.40:8446"},
                "governance": {"endpoint": "192.168.40.50:8448"},
            },
            "architecture": "sovereign_mesh_sheaf_crdt",
        }
        violations = self.enforcer.scan_topology(clean_topo)
        self.assertEqual(len(violations), 0)

    def test_custom_negative_axiom_registration_and_enforcement(self) -> None:
        """Registers a custom negative axiom and verifies pattern matching and enforcement count."""
        custom_axiom = NegativeAxiom(
            axiom_id="NEG-888",
            name="Prohibit Eval In Disguise",
            forbidden_pattern="__builtins__['eval']",
            rationale="Obfuscated builtins eval access is strictly forbidden.",
            severity=AxiomSeverity.FATAL_VETO,
            injected_epoch=18,
            is_active=True,
        )
        self.enforcer.register_negative_axiom(custom_axiom)

        retrieved = self.enforcer.get_negative_axiom("NEG-888")
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.name, "Prohibit Eval In Disguise")

        code_malicious = "fn = __builtins__['eval']"
        violations = self.enforcer.scan_source_code(code_malicious, "malicious.py")
        self.assertTrue(any(v.axiom_id == "NEG-888" for v in violations))
        self.assertGreaterEqual(retrieved.enforcement_count, 1)

    def test_clean_source_code_zero_violations(self) -> None:
        """Pure deterministic async code produces zero violations."""
        clean_code = (
            "async def calculate_landauer_heat(bits_erased: int, temp_kelvin: float = 300.0) -> float:\n"
            "    k_b = 1.380649e-23\n"
            "    ln2 = 0.6931471805599453\n"
            "    return bits_erased * k_b * temp_kelvin * ln2\n"
        )
        violations = self.enforcer.scan_source_code(clean_code, "clean_math.py")
        self.assertEqual(len(violations), 0)


if __name__ == "__main__":
    unittest.main()
