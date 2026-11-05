"""Anti-Mock Subprocess Entrypoint Smoke Suite (`[NEG-G1B-002]`, `test_service_subprocess_smoke.py`).

Enforces:
- [NEG-G1B-001] Mandatory Physical File Emission & Non-Zero Byte Verification.
- [NEG-G1B-002] Anti-Mock Subprocess Entrypoint Smoke Invariant:
  1. Programmatically boots each sovereign service entrypoint (`run.py`) in an independent OS subprocess.
  2. Asserts zero top-level import crashes (ImportError, ModuleNotFoundError, path resolution panics).
  3. Asserts clean operational verification exit (exit code 0) within bounded execution timeout (t <= 5.0s).
  4. Asserts clean signal response (SIGTERM) and clean process teardown without zombie or deadlock.
"""

from __future__ import annotations

import os
from pathlib import Path
import signal
import subprocess
import sys
import time
import unittest


REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
GEN_04B_DIR = REPO_ROOT / "generations" / "gen_04b"
SERVICES_DIR = GEN_04B_DIR / "services"


class TestServiceSubprocessSmoke(unittest.TestCase):
    """Rigorous empirical subprocess smoke test suite executing live entrypoints in isolated OS processes."""

    def setUp(self) -> None:
        self.services = {
            "research": SERVICES_DIR / "research" / "run.py",
            "builder": SERVICES_DIR / "builder" / "run.py",
            "audit": SERVICES_DIR / "audit" / "run.py",
            "telemetry": SERVICES_DIR / "telemetry" / "run.py",
            "governance": SERVICES_DIR / "governance" / "run.py",
        }
        for name, path in self.services.items():
            self.assertTrue(path.exists(), f"Entrypoint script missing: {path}")
            self.assertGreater(path.stat().st_size, 0, f"Zero-byte entrypoint script: {path}")

    # 1. Epistemic Research Service Subprocess Smoke
    def test_01_research_service_subprocess_smoke(self) -> None:
        script = self.services["research"]
        start_t = time.perf_counter()
        proc = subprocess.Popen(
            [sys.executable, str(script)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=str(REPO_ROOT),
        )
        stdout, stderr = proc.communicate(timeout=5.0)
        duration_s = time.perf_counter() - start_t

        self.assertEqual(
            proc.returncode, 0,
            f"Research service crashed in subprocess with exit code {proc.returncode}.\nSTDERR:\n{stderr}"
        )
        self.assertNotIn("ImportError", stderr)
        self.assertNotIn("ModuleNotFoundError", stderr)
        self.assertIn("ZENITH APEX CRUCIBLE VERIFICATION COMPLETE", stdout)
        self.assertLess(duration_s, 5.0)

    # 2. Sovereign Builder Service Subprocess Smoke
    def test_02_builder_service_subprocess_smoke(self) -> None:
        script = self.services["builder"]
        start_t = time.perf_counter()
        proc = subprocess.Popen(
            [sys.executable, str(script)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=str(REPO_ROOT),
        )
        stdout, stderr = proc.communicate(timeout=5.0)
        duration_s = time.perf_counter() - start_t

        self.assertEqual(
            proc.returncode, 0,
            f"Builder service crashed in subprocess with exit code {proc.returncode}.\nSTDERR:\n{stderr}"
        )
        self.assertNotIn("ImportError", stderr)
        self.assertNotIn("ModuleNotFoundError", stderr)
        self.assertIn("ALL 13 GENERATION 4b SOVEREIGN BUILDER MODULES CERTIFIED", stdout)
        self.assertLess(duration_s, 5.0)

    # 3. Sovereign Audit Service Subprocess Smoke
    def test_03_audit_service_subprocess_smoke(self) -> None:
        script = self.services["audit"]
        start_t = time.perf_counter()
        proc = subprocess.Popen(
            [sys.executable, str(script)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=str(REPO_ROOT),
        )
        stdout, stderr = proc.communicate(timeout=5.0)
        duration_s = time.perf_counter() - start_t

        self.assertEqual(
            proc.returncode, 0,
            f"Audit service crashed in subprocess with exit code {proc.returncode}.\nSTDERR:\n{stderr}"
        )
        self.assertNotIn("ImportError", stderr)
        self.assertNotIn("ModuleNotFoundError", stderr)
        self.assertIn("Sovereign Audit & Formal Verification Service (`soc_g4b_audit`) Certified Operational", stdout)
        self.assertLess(duration_s, 5.0)

    # 4. Sovereign Telemetry Service Subprocess Smoke
    def test_04_telemetry_service_subprocess_smoke(self) -> None:
        script = self.services["telemetry"]
        start_t = time.perf_counter()
        proc = subprocess.Popen(
            [sys.executable, str(script)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=str(REPO_ROOT),
        )
        stdout, stderr = proc.communicate(timeout=5.0)
        duration_s = time.perf_counter() - start_t

        self.assertEqual(
            proc.returncode, 0,
            f"Telemetry service crashed in subprocess with exit code {proc.returncode}.\nSTDERR:\n{stderr}"
        )
        self.assertNotIn("ImportError", stderr)
        self.assertNotIn("ModuleNotFoundError", stderr)
        self.assertIn("SOVEREIGN TELEMETRY & EVALUATION SERVICE CERTIFIED", stdout)
        self.assertLess(duration_s, 5.0)

    # 5. Sovereign Governance Service Subprocess Smoke
    def test_05_governance_service_subprocess_smoke(self) -> None:
        script = self.services["governance"]
        start_t = time.perf_counter()
        proc = subprocess.Popen(
            [sys.executable, str(script)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=str(REPO_ROOT),
        )
        stdout, stderr = proc.communicate(timeout=5.0)
        duration_s = time.perf_counter() - start_t

        self.assertEqual(
            proc.returncode, 0,
            f"Governance service crashed in subprocess with exit code {proc.returncode}.\nSTDERR:\n{stderr}"
        )
        self.assertNotIn("ImportError", stderr)
        self.assertNotIn("ModuleNotFoundError", stderr)
        self.assertIn("Sovereign Governance & Safety Service (`soc_g4b_governance`) Certified Operational", stdout)
        self.assertLess(duration_s, 5.0)

    # 6. Telemetry Smoke-Test Flag Mode Subprocess Execution
    def test_06_telemetry_smoke_test_flag_subprocess(self) -> None:
        script = self.services["telemetry"]
        start_t = time.perf_counter()
        proc = subprocess.Popen(
            [sys.executable, str(script), "--smoke-test"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=str(REPO_ROOT),
        )
        stdout, stderr = proc.communicate(timeout=5.0)
        duration_s = time.perf_counter() - start_t

        self.assertEqual(
            proc.returncode, 0,
            f"Telemetry --smoke-test crashed with code {proc.returncode}.\nSTDERR:\n{stderr}"
        )
        self.assertIn("[SMOKE TEST SUCCESS]", stdout)
        self.assertLess(duration_s, 5.0)

    # 7. Subprocess Clean SIGTERM Teardown Test
    def test_07_subprocess_sigterm_clean_teardown(self) -> None:
        script = self.services["telemetry"]
        proc = subprocess.Popen(
            [sys.executable, str(script), "--cockpit", "--port", "29447", "--ingest-port", "29446"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=str(REPO_ROOT),
        )

        # Allow daemon process to initialize event loop
        time.sleep(0.3)
        self.assertIsNone(proc.poll(), "Daemon process died prematurely before receiving SIGTERM")

        # Deliver SIGTERM
        proc.send_signal(signal.SIGTERM)
        try:
            stdout, stderr = proc.communicate(timeout=3.0)
        except subprocess.TimeoutExpired:
            proc.kill()
            self.fail("Subprocess hung on SIGTERM delivery and required SIGKILL (zombie violation)")

        # Verify clean exit: returncode should be 0 or -15 (SIGTERM)
        self.assertIn(
            proc.returncode, (0, -signal.SIGTERM),
            f"Expected clean SIGTERM exit code, got {proc.returncode}"
        )


if __name__ == "__main__":
    unittest.main()
