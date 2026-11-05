"""Unit tests for Tier 0 Operational Liveness Gatekeeper ([NEG-G1B-002])."""

import os
from pathlib import Path
import shutil
import textwrap
import unittest

from benchmarks.macro_ablation.evaluators.liveness_gatekeeper import (
    LivenessGatekeeper,
    find_free_port,
)


class TestLivenessGatekeeper(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.workspace_root = Path(__file__).resolve().parent.parent.parent.parent
        cls.test_dir = cls.workspace_root / ".scratch" / "test_liveness"
        cls.test_dir.mkdir(parents=True, exist_ok=True)

    @classmethod
    def tearDownClass(cls):
        if cls.test_dir.exists():
            shutil.rmtree(cls.test_dir, ignore_errors=True)

    def test_find_free_port(self):
        port1 = find_free_port()
        port2 = find_free_port()
        self.assertIsInstance(port1, int)
        self.assertGreater(port1, 1024)
        self.assertIsInstance(port2, int)
        self.assertGreater(port2, 1024)

    def test_missing_entrypoint(self):
        app_dir = self.test_dir / "missing_app"
        app_dir.mkdir(parents=True, exist_ok=True)
        gatekeeper = LivenessGatekeeper(boot_timeout_sec=1.0)
        res = gatekeeper.evaluate(app_dir)
        self.assertFalse(res.passed)
        self.assertIn("does not exist", res.error_message or "")

    def test_crashing_script_fails_liveness(self):
        app_dir = self.test_dir / "crashing_app"
        app_dir.mkdir(parents=True, exist_ok=True)
        (app_dir / "run.py").write_text(
            "import sys\nsys.stderr.write('Fatal import error\\n')\nsys.exit(1)\n",
            encoding="utf-8",
        )
        gatekeeper = LivenessGatekeeper(boot_timeout_sec=2.0)
        res = gatekeeper.evaluate(app_dir)
        self.assertFalse(res.passed)
        self.assertEqual(res.exit_code, 1)

    def test_broken_relative_import_fails_liveness(self):
        app_dir = self.test_dir / "broken_import_app"
        app_dir.mkdir(parents=True, exist_ok=True)
        (app_dir / "run.py").write_text(
            "from ..phantom_pkg import phantom_symbol\n",
            encoding="utf-8",
        )
        gatekeeper = LivenessGatekeeper(boot_timeout_sec=2.0)
        res = gatekeeper.evaluate(app_dir)
        self.assertFalse(res.passed)
        self.assertNotEqual(res.exit_code, 0)

    def test_valid_server_passes_liveness(self):
        app_dir = self.test_dir / "valid_server_app"
        app_dir.mkdir(parents=True, exist_ok=True)
        server_code = textwrap.dedent("""\
            import argparse
            import sys

            if __name__ == '__main__':
                parser = argparse.ArgumentParser()
                parser.add_argument('--port', type=int, default=8088)
                parser.add_argument('--smoke-test', action='store_true')
                args = parser.parse_args()
                if args.smoke_test:
                    print("AXIOMA_HEALTH_OK: healthy", flush=True)
                    sys.exit(0)
                print(f"SERVER_ONLINE: port={args.port}", flush=True)
                sys.exit(0)
        """)
        (app_dir / "run.py").write_text(server_code, encoding="utf-8")

        gatekeeper = LivenessGatekeeper(boot_timeout_sec=3.0, teardown_timeout_sec=2.0)
        res = gatekeeper.evaluate(app_dir)
        self.assertTrue(res.passed, f"Liveness failed: {res.error_message}")
        self.assertTrue(res.clean_shutdown)
        self.assertGreater(res.startup_time_ms, 0.0)


if __name__ == "__main__":
    unittest.main()
