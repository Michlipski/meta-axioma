"""Unit and Adversarial Test Suite for Physical Mutation Falsifier & Anti-Mock Auditor.

Enforces:
- [INV-G4B-MUTATION-001]: Physical Mutation Falsification Invariant.
- Result(mutated_code) == FAIL => Certified Non-Tautological
- Result(mutated_code) == PASS => TautologicalTestViolation (REJECT)
"""

from __future__ import annotations

import hashlib
import os
from pathlib import Path
import sys
import tempfile
import time
import unittest

AUDIT_ROOT = Path(__file__).resolve().parent.parent
REPO_ROOT = AUDIT_ROOT.parent.parent.parent.parent
for p in [str(AUDIT_ROOT), str(AUDIT_ROOT / "src"), str(REPO_ROOT)]:
    if p not in sys.path:
        sys.path.insert(0, p)

from src.domain_models import (
    AuditDomainInvariantViolation,
    MutationWitness,
    SemanticStateSpoofingViolation,
    TautologicalTestViolation,
)
from src.mutation_fuzzer import (
    PhysicalMutationFalsifier,
    check_and_restore_stale_mutations,
)


class TestMutationWitness(unittest.TestCase):
    """Tests for MutationWitness domain model, serialization, and invariants."""

    def test_mutation_witness_roundtrip_and_hashing(self) -> None:
        h_orig = hashlib.sha256(b"original").hexdigest()
        h_mut = hashlib.sha256(b"mutated").hexdigest()
        h_rest = hashlib.sha256(b"original").hexdigest()

        witness = MutationWitness(
            witness_id="wit_test_001",
            target_file="/path/to/app.js",
            mutation_pattern=("render()", "console.log()"),
            test_command=["python3", "-m", "unittest"],
            exit_code=1,
            stdout_snippet="AssertionError: 1 != 2",
            stderr_snippet="",
            original_sha256=h_orig,
            mutated_sha256=h_mut,
            restored_sha256=h_rest,
            verified=True,
            timestamp_ns=1700000000000000000,
        )

        witness.validate_invariants()
        w_hash = witness.compute_witness_hash()
        self.assertEqual(len(w_hash), 64)
        self.assertEqual(w_hash, witness.compute_hash())

        d = witness.to_dict()
        restored = MutationWitness.from_dict(d)
        self.assertEqual(witness.witness_id, restored.witness_id)
        self.assertEqual(witness.target_file, restored.target_file)
        self.assertEqual(witness.mutation_pattern, restored.mutation_pattern)
        self.assertEqual(witness.exit_code, restored.exit_code)
        self.assertEqual(witness.original_sha256, restored.original_sha256)
        self.assertEqual(witness.mutated_sha256, restored.mutated_sha256)
        self.assertEqual(witness.restored_sha256, restored.restored_sha256)
        self.assertEqual(witness.compute_witness_hash(), restored.compute_witness_hash())

    def test_mutation_witness_invariant_violations(self) -> None:
        h1 = hashlib.sha256(b"a").hexdigest()
        h2 = hashlib.sha256(b"b").hexdigest()

        # Empty witness_id
        w_bad1 = MutationWitness(
            witness_id="",
            target_file="app.py",
            mutation_pattern=("a", "b"),
            test_command=[],
            exit_code=1,
            stdout_snippet="",
            stderr_snippet="",
            original_sha256=h1,
            mutated_sha256=h2,
            restored_sha256=h1,
            verified=True,
        )
        with self.assertRaises(AuditDomainInvariantViolation):
            w_bad1.validate_invariants()

        # Restored hash divergence
        w_bad2 = MutationWitness(
            witness_id="wit_bad",
            target_file="app.py",
            mutation_pattern=("a", "b"),
            test_command=[],
            exit_code=1,
            stdout_snippet="",
            stderr_snippet="",
            original_sha256=h1,
            mutated_sha256=h2,
            restored_sha256=h2,  # mismatch with original!
            verified=True,
        )
        with self.assertRaises(AuditDomainInvariantViolation):
            w_bad2.validate_invariants()


class TestPhysicalMutationFalsifier(unittest.TestCase):
    """Tests for PhysicalMutationFalsifier defect injection and test falsification."""

    def setUp(self) -> None:
        self.falsifier = PhysicalMutationFalsifier()
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_dir = Path(self.temp_dir.name)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_non_tautological_test_passes_falsification(self) -> None:
        """A test suite that properly tests logic will fail when that logic is broken."""
        code_file = self.test_dir / "math_mod.py"
        code_file.write_text("def add(a, b):\n    return a + b\n")

        # Test command asserts that add(2, 3) == 5
        test_cmd = [
            sys.executable,
            "-c",
            f"import sys; sys.path.insert(0, {str(self.test_dir)!r}); import math_mod; assert math_mod.add(2, 3) == 5",
        ]

        # Mutate "return a + b" -> "return a - b"
        witness = self.falsifier.assert_mutation_fails_test(
            target_file=code_file,
            mutation_pattern=("return a + b", "return a - b"),
            test_command=test_cmd,
            expected_failure_substring="AssertionError",
        )

        self.assertTrue(witness.verified)
        self.assertNotEqual(witness.exit_code, 0)
        self.assertEqual(code_file.read_text(), "def add(a, b):\n    return a + b\n")
        self.assertEqual(len(list(self.test_dir.glob(".*.bak.*"))), 0)

    def test_tautological_test_raises_violation(self) -> None:
        """A tautological test that passes regardless of code changes must raise TautologicalTestViolation."""
        code_file = self.test_dir / "useless_mod.py"
        code_file.write_text("def render():\n    return 'OK'\n")

        # Tautological test command: always exits 0 without testing anything real
        tautological_cmd = [
            sys.executable,
            "-c",
            "import sys; sys.exit(0)",
        ]

        with self.assertRaises(TautologicalTestViolation):
            self.falsifier.assert_mutation_fails_test(
                target_file=code_file,
                mutation_pattern=("return 'OK'", "return 'DAMAGED'"),
                test_command=tautological_cmd,
            )

        # Ensure file was safely restored even after TautologicalTestViolation was raised
        self.assertEqual(code_file.read_text(), "def render():\n    return 'OK'\n")
        self.assertEqual(len(list(self.test_dir.glob(".*.bak.*"))), 0)

    def test_expected_failure_substring_divergence_raises_violation(self) -> None:
        """If test fails with an unexpected error rather than the specified failure substring."""
        code_file = self.test_dir / "mod.py"
        code_file.write_text("def foo():\n    return 42\n")

        # Test raises ValueError, but we expect "ZeroDivisionError"
        test_cmd = [
            sys.executable,
            "-c",
            f"import sys; sys.path.insert(0, {str(self.test_dir)!r}); import mod; "
            f"if mod.foo() == 0: raise ValueError('bad value')",
        ]

        with self.assertRaises(AuditDomainInvariantViolation) as ctx:
            self.falsifier.assert_mutation_fails_test(
                target_file=code_file,
                mutation_pattern=("return 42", "return 0"),
                test_command=test_cmd,
                expected_failure_substring="ZeroDivisionError",
            )
        self.assertIn("expected failure substring 'ZeroDivisionError' was not found", str(ctx.exception))

    def test_check_and_restore_stale_mutations(self) -> None:
        """Verifies check_and_restore_stale_mutations restores orphaned backup files."""
        target_file = self.test_dir / "target.py"
        original_bytes = b"def original_logic(): return 1\n"
        orig_sha = hashlib.sha256(original_bytes).hexdigest()

        # Simulate orphaned state: target was mutated, backup exists
        target_file.write_bytes(b"def damaged_logic(): return 0\n")
        backup_file = self.test_dir / f".target.py.bak.{orig_sha}"
        backup_file.write_bytes(original_bytes)

        restored = check_and_restore_stale_mutations(self.test_dir)
        self.assertEqual(len(restored), 1)
        self.assertEqual(restored[0].resolve(), target_file.resolve())
        self.assertEqual(target_file.read_bytes(), original_bytes)
        self.assertFalse(backup_file.exists())


class TestSemanticStateSpoofingViolation(unittest.TestCase):
    """Verifies SemanticStateSpoofingViolation exception type."""

    def test_semantic_state_spoofing_violation_inheritance(self) -> None:
        viol = SemanticStateSpoofingViolation("In-memory DOM dictionary spoofing detected")
        self.assertIsInstance(viol, AuditDomainInvariantViolation)
        self.assertIn("spoofing", str(viol))


if __name__ == "__main__":
    unittest.main()
