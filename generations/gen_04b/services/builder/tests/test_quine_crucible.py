"""Adversarial & Self-Hosting Verification Test Suite for Quine Crucible (`[L1-016]`, `[L1-G3B-017]`).

Validates:
1. Isolated clean-room sandbox directory provisioning.
2. Physical emission of daughter compiler source files and test suites with non-zero bytes.
3. Deterministic composite SHA-256 hash calculation across emitted files.
4. Quine hash idempotency across identical emission passes.
5. Tamper detection: mutating daughter compiler byte stream alters daughter hash.
6. Live subprocess execution witness: executing test_daughter.py in isolated sandbox with exit code 0.
7. Emission and formal validation of QuineDaughterManifest with self_hosting_certified=True.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

BUILDER_ROOT = Path(__file__).resolve().parent.parent
REPO_ROOT = BUILDER_ROOT.parent.parent.parent
for p in [str(BUILDER_ROOT), str(REPO_ROOT)]:
    if p not in sys.path:
        sys.path.insert(0, p)

from src.domain_models import DomainInvariantViolation, QuineDaughterManifest
from src.quine_crucible import QuineCrucibleEngine


class TestQuineCrucible(unittest.TestCase):
    """Rigorous verification of clean-room daughter compiler emission and self-hosting."""

    def setUp(self) -> None:
        self.temp_dir = tempfile.mkdtemp(prefix="axioma_quine_test_")
        self.crucible = QuineCrucibleEngine(sandbox_base_dir=self.temp_dir)

    def tearDown(self) -> None:
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_provision_sandbox(self) -> None:
        sandbox = self.crucible.provision_sandbox("gen_05a")
        self.assertTrue(sandbox.exists())
        self.assertTrue(sandbox.is_dir())
        self.assertIn("gen_05a", str(sandbox))

    def test_emit_daughter_compiler_non_zero_bytes(self) -> None:
        sandbox = self.crucible.provision_sandbox("gen_05a")
        emitted_files = self.crucible.emit_daughter_compiler(sandbox, "gen_05a")

        self.assertEqual(len(emitted_files), 2)
        for f in emitted_files:
            self.assertTrue(f.exists(), f"File {f} must physically exist on disk.")
            self.assertGreater(f.stat().st_size, 0, f"File {f} must have non-zero bytes.")
            self.assertIn(".py", f.name)

    def test_compute_daughter_hash_and_idempotency(self) -> None:
        sandbox1 = self.crucible.provision_sandbox("gen_05a_1")
        files1 = self.crucible.emit_daughter_compiler(sandbox1, "gen_05a")
        hash1 = self.crucible.compute_daughter_hash(files1)

        # 64-char SHA-256 hash
        self.assertEqual(len(hash1), 64)

        # Re-emitting with identical parameters must yield identical hash
        sandbox2 = self.crucible.provision_sandbox("gen_05a_2")
        files2 = self.crucible.emit_daughter_compiler(sandbox2, "gen_05a")
        hash2 = self.crucible.compute_daughter_hash(files2)

        self.assertEqual(hash1, hash2)

    def test_tamper_detection(self) -> None:
        sandbox = self.crucible.provision_sandbox("gen_05a")
        files = self.crucible.emit_daughter_compiler(sandbox, "gen_05a")
        original_hash = self.crucible.compute_daughter_hash(files)

        # Tamper with one of the emitted files
        target_file = files[0]
        content = target_file.read_text(encoding="utf-8")
        target_file.write_text(content + "\n# Tampered payload", encoding="utf-8")

        mutated_hash = self.crucible.compute_daughter_hash(files)
        self.assertNotEqual(original_hash, mutated_hash)

    def test_certify_daughter_compiler_live_subprocess_witness(self) -> None:
        manifest = self.crucible.certify_daughter_compiler("gen_05a")

        self.assertIsInstance(manifest, QuineDaughterManifest)
        self.assertTrue(manifest.boot_success)
        self.assertTrue(manifest.self_hosting_certified)
        self.assertEqual(len(manifest.daughter_hash), 64)
        self.assertGreaterEqual(len(manifest.emitted_compiler_files), 2)
        
        # Verify physical existence of certified files
        for f_path in manifest.emitted_compiler_files:
            p = Path(f_path)
            self.assertTrue(p.exists())
            self.assertGreater(p.stat().st_size, 0)


if __name__ == "__main__":
    unittest.main()
