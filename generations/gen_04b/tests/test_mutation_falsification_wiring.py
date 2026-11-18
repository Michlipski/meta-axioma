"""Physical Mutation Falsification Tests for Generation 4b Service Wiring ([INV-G4B-MUTATION-001]).

Executes PhysicalMutationFalsifier against the 3 production wiring targets specified in
`.scratch/spec_g4b_wiring_001.json`:
1. `generations/gen_04b/protocols/ipc_transport.py` (`send_envelope`)
2. `generations/gen_04b/compiler/orchestrator.py` (`PHASE_3_AUDIT` in `compile`)
3. `generations/gen_04b/services/audit/src/acceptance_gate.py` (`scan_banned_ast_patterns`)

Targets single isolated test methods in `test_g4b_compiler_e2e.py` to prevent infinite recursion
and asserts bit-identical SHA-256 restoration (`restored_sha256 == original_sha256`).
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
import time
import unittest

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from generations.gen_04b.services.audit.src.mutation_fuzzer import (
    PhysicalMutationFalsifier,
)


GEN_04B_DIR = REPO_ROOT / "generations" / "gen_04b"
E2E_TEST_FILE = GEN_04B_DIR / "tests" / "test_g4b_compiler_e2e.py"
SPEC_FILE = REPO_ROOT / ".scratch" / "spec_g4b_wiring_001.json"


class TestMutationFalsificationWiring(unittest.TestCase):
    """Proves E2E wiring test assertions fail under physical disk defect injection."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.falsifier = PhysicalMutationFalsifier(node_id="node_g4b_wiring_falsifier")
        cls.spec_data = json.loads(SPEC_FILE.read_text(encoding="utf-8"))
        cls.vector_ids = {v["vector_id"] for v in cls.spec_data.get("falsification_vectors", [])}

    def _assert_bit_identical_reversion(self, target_file: Path, expected_sha256: str) -> None:
        actual_sha256 = hashlib.sha256(target_file.read_bytes()).hexdigest()
        self.assertEqual(actual_sha256, expected_sha256)
        stale_backups = list(target_file.parent.glob(f".{target_file.name}.bak.*"))
        self.assertEqual(stale_backups, [], f"Orphaned backup files detected: {stale_backups}")

    def test_01_falsify_ipc_transport_send_envelope(self) -> None:
        """FV-IPC-001: Mutating send_envelope to return None must fail targeted IPC delivery test."""
        self.assertIn("FV-IPC-001", self.vector_ids)
        target_file = GEN_04B_DIR / "protocols" / "ipc_transport.py"
        t0 = time.perf_counter()

        witness = self.falsifier.assert_mutation_fails_test(
            target_file=target_file,
            mutation_pattern=(
                "        framed_bytes = envelope.serialize_framed()",
                "        return None  # FV-IPC-001 MUTATED_EMPTY",
            ),
            test_command=[
                sys.executable,
                "-u",
                str(E2E_TEST_FILE),
                "TestG4bCompilerE2E.test_01_ipc_envelope_roundtrip_and_socketpair_delivery",
            ],
            timeout_s=10.0,
        )
        elapsed_s = time.perf_counter() - t0

        self.assertTrue(witness.verified)
        self.assertNotEqual(witness.exit_code, 0)
        self.assertNotEqual(witness.mutated_sha256, witness.original_sha256)
        self.assertEqual(witness.restored_sha256, witness.original_sha256)
        self.assertLess(elapsed_s, 10.0)
        self._assert_bit_identical_reversion(target_file, witness.original_sha256)

    def test_02_falsify_compiler_orchestrator_phase3_audit(self) -> None:
        """FV-COMPILER-002: Disabling Phase 3 Audit transition in compile() must fail E2E test."""
        self.assertIn("FV-COMPILER-002", self.vector_ids)
        target_file = GEN_04B_DIR / "compiler" / "orchestrator.py"
        t0 = time.perf_counter()

        witness = self.falsifier.assert_mutation_fails_test(
            target_file=target_file,
            mutation_pattern=(
                '            statechart.transition(CompilationPhase.PHASE_3_AUDIT, event="EV_AUDIT_VERIFY")',
                '            # FV-COMPILER-002 MUTATED: statechart.transition(CompilationPhase.PHASE_3_AUDIT, event="EV_AUDIT_VERIFY")',
            ),
            test_command=[
                sys.executable,
                "-u",
                str(E2E_TEST_FILE),
                "TestG4bCompilerE2E.test_09_full_system_g4b_compiler_e2e_and_rfc_escalation",
            ],
            timeout_s=10.0,
        )
        elapsed_s = time.perf_counter() - t0

        self.assertTrue(witness.verified)
        self.assertNotEqual(witness.exit_code, 0)
        self.assertNotEqual(witness.mutated_sha256, witness.original_sha256)
        self.assertEqual(witness.restored_sha256, witness.original_sha256)
        self.assertLess(elapsed_s, 10.0)
        self._assert_bit_identical_reversion(target_file, witness.original_sha256)

    def test_03_falsify_acceptance_gate_scan_banned_ast_patterns(self) -> None:
        """FV-AUDIT-003: Inverting pattern check in scan_banned_ast_patterns must fail AcceptanceGate test."""
        self.assertIn("FV-AUDIT-003", self.vector_ids)
        target_file = GEN_04B_DIR / "services" / "audit" / "src" / "acceptance_gate.py"
        t0 = time.perf_counter()

        witness = self.falsifier.assert_mutation_fails_test(
            target_file=target_file,
            mutation_pattern=(
                "        if not normalized_patterns:\n            return violations",
                "        if normalized_patterns:\n            return []  # FV-AUDIT-003 MUTATED_INVERT",
            ),
            test_command=[
                sys.executable,
                "-u",
                str(E2E_TEST_FILE),
                "TestG4bCompilerE2E.test_05_acceptance_gate_compliant_and_breach_detection",
            ],
            timeout_s=10.0,
        )
        elapsed_s = time.perf_counter() - t0

        self.assertTrue(witness.verified)
        self.assertNotEqual(witness.exit_code, 0)
        self.assertNotEqual(witness.mutated_sha256, witness.original_sha256)
        self.assertEqual(witness.restored_sha256, witness.original_sha256)
        self.assertLess(elapsed_s, 10.0)
        self._assert_bit_identical_reversion(target_file, witness.original_sha256)


if __name__ == "__main__":
    unittest.main()
