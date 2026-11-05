"""Subprocess Entrypoint Smoke Verification Test (`test_subprocess_smoke.py`).

Enforces:
- [NEG-G1B-001] Mandatory Substrate Test Execution (exit code 0).
- [NEG-G1B-002] Anti-Mock Subprocess Entrypoint Smoke Invariant:
  Mandates programmatically spawning the actual entrypoint binary in an independent
  OS subprocess to prove zero import crashes, socket liveness, and clean teardown.
"""

from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys
import unittest


class TestTelemetrySubprocessSmoke(unittest.TestCase):
    """Verifies that the Sovereign Telemetry service entrypoint boots in an independent OS subprocess."""

    def setUp(self) -> None:
        self.telemetry_dir = Path(__file__).resolve().parent.parent
        self.run_script = self.telemetry_dir / "run.py"
        self.assertTrue(self.run_script.exists(), f"run.py not found at {self.run_script}")

    def test_subprocess_smoke_entrypoint(self) -> None:
        """Executes 'python3 run.py --smoke-test' in an independent OS subprocess."""
        cmd = [sys.executable, str(self.run_script), "--smoke-test"]
        env = dict(os.environ)

        proc = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=10,
            env=env,
        )

        # 1. Assert exit code 0 (zero startup import crashes or runtime panics)
        self.assertEqual(
            proc.returncode,
            0,
            f"Entrypoint failed with exit code {proc.returncode}.\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}",
        )

        # 2. Assert observable startup confirmation in stdout
        self.assertIn("[SMOKE TEST SUCCESS]", proc.stdout)
        self.assertIn("Cockpit and Ingest servers booted, bound, and verified with exit code 0", proc.stdout)

        # 3. Assert zero unhandled tracebacks in stderr
        self.assertNotIn("Traceback (most recent call last):", proc.stderr)
        self.assertNotIn("ImportError:", proc.stderr)


if __name__ == "__main__":
    unittest.main()
