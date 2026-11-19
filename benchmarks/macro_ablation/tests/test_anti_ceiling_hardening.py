"""Unit & Regression Tests for Anti-Ceiling Hardening of MacroEvaluationGauntlet.

Verifies:
- Symmetric, layout-agnostic `HERM-002` app-root bootstrap rule (single-file == multi-file `src/`).
- Removal of `ChaosEvaluator` Probe 4 loopback-echo free pass.
- Real domain chaos probes: CLI/NDJSON (`10**400` overflow + open-stdin `SIGINT` PEP 475),
  RESP2 (nested array, CRLF injection, 64-bit / 4500-digit `INCR`), HTTP (oversized `Content-Length`,
  truncated body mismatch, `bool`-as-`int`).
- `AdversarialIntegrityEvaluator`: unresolved Red Team criticals and tautological tests
  prevent `100.00` ceiling while keeping evaluated `app_dir` bit-identical on disk.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil
import sys
import unittest
import uuid

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from benchmarks.macro_ablation.archetypes import axioma_kv, axioma_micro, axioma_resp
from benchmarks.macro_ablation.domain_models import AblationMode
from benchmarks.macro_ablation.evaluators import (
    AdversarialIntegrityEvaluator,
    ChaosEvaluator,
    HermeticEvaluator,
)
from benchmarks.macro_ablation.macro_evaluator import MacroEvaluationGauntlet


class TestAntiCeilingHardening(unittest.TestCase):
    """Tests anti-ceiling hardening across Hermetic, Chaos, and AdversarialIntegrity evaluators."""

    def setUp(self) -> None:
        self.scratch = REPO_ROOT / ".scratch" / f"test_anti_ceil_{uuid.uuid4().hex[:8]}"
        self.scratch.mkdir(parents=True, exist_ok=True)
        self.micro_arch = axioma_micro.get_archetype()
        self.resp_arch = axioma_resp.get_archetype()
        self.kv_arch = axioma_kv.get_archetype()

    def tearDown(self) -> None:
        shutil.rmtree(self.scratch, ignore_errors=True)

    def test_01_hermetic_herm002_symmetry_single_file_vs_src(self) -> None:
        """Single-file and multi-file src/ apps are judged identically for HERM-002."""
        evaluator = HermeticEvaluator(weight=0.20)

        # Single-file app with standard Path(__file__).resolve().parent bootstrap in run.py
        single_dir = self.scratch / "single_file_app"
        single_dir.mkdir()
        (single_dir / "logfilter.py").write_text("def process_line(x: str) -> bool:\n    return bool(x)\n", encoding="utf-8")
        (single_dir / "run.py").write_text(
            "from pathlib import Path\nimport sys\n"
            "_HERE = Path(__file__).resolve().parent\n"
            "if str(_HERE) not in sys.path:\n"
            "    sys.path.insert(0, str(_HERE))\n"
            "from logfilter import process_line\n",
            encoding="utf-8",
        )

        # Multi-file src/ app with identical bootstrap
        src_dir = self.scratch / "multi_src_app"
        (src_dir / "src").mkdir(parents=True)
        (src_dir / "src" / "__init__.py").write_text("", encoding="utf-8")
        (src_dir / "src" / "engine.py").write_text("def process_line(x: str) -> bool:\n    return bool(x)\n", encoding="utf-8")
        (src_dir / "run.py").write_text(
            "from pathlib import Path\nimport sys\n"
            "_HERE = Path(__file__).resolve().parent\n"
            "if str(_HERE) not in sys.path:\n"
            "    sys.path.insert(0, str(_HERE))\n"
            "from src.engine import process_line\n",
            encoding="utf-8",
        )

        res_single = evaluator.evaluate(single_dir, self.micro_arch)
        res_src = evaluator.evaluate(src_dir, self.micro_arch)
        self.assertEqual(res_single.raw_score, 100.0, f"Single-file penalized unfairly: {res_single.details}")
        self.assertEqual(res_src.raw_score, 100.0, f"Multi-file failed: {res_src.details}")

        # Arbitrary sys.path tampering MUST be penalized even if "src" appears in code_text!
        evil_src_dir = self.scratch / "evil_src_app"
        (evil_src_dir / "src").mkdir(parents=True)
        (evil_src_dir / "src" / "engine.py").write_text(
            "import sys\n# contains src word\nsys.path.insert(0, '/etc/evil')\n",
            encoding="utf-8",
        )
        res_evil = evaluator.evaluate(evil_src_dir, self.micro_arch)
        self.assertFalse(res_evil.passed)
        self.assertLess(res_evil.raw_score, 100.0)

        # Fallback AST scanner matches primary symmetry
        _, fb_clean = evaluator._scan_ast_fallback((single_dir / "run.py").read_text(encoding="utf-8"), "run.py")
        _, fb_evil = evaluator._scan_ast_fallback((evil_src_dir / "src" / "engine.py").read_text(encoding="utf-8"), "src/engine.py")
        self.assertEqual(fb_clean, [])
        self.assertTrue(any(v["rule_id"] == "HERM-002" for v in fb_evil))

    def test_02_chaos_removes_probe4_echo_free_pass(self) -> None:
        """Probe 4 must NOT award a free pass when no framing/parser method is discovered."""
        app_dir = self.scratch / "no_parser_cli"
        app_dir.mkdir()
        (app_dir / "run.py").write_text(
            "import argparse, sys\n"
            "p = argparse.ArgumentParser()\n"
            "p.add_argument('--smoke-test', action='store_true')\n"
            "a = p.parse_args()\n"
            "print('{\"ok\": true}', flush=True)\n",
            encoding="utf-8",
        )
        ev = ChaosEvaluator(weight=0.15, timeout_sec=4.0)
        res = ev.evaluate(app_dir, self.micro_arch)
        self.assertTrue(
            any("no framing/parser method exercised" in line for line in res.details.get("log", [])),
            f"Expected Probe 4 to reject echo free pass, got: {res.details}",
        )

    def test_03_chaos_catches_cli_overflow_and_pep475_sigint_hang(self) -> None:
        """ChaosEvaluator catches 10**400 OverflowError and PEP 475 open-stdin SIGINT hang."""
        buggy_dir = self.scratch / "buggy_micro"
        buggy_dir.mkdir()
        (buggy_dir / "run.py").write_text(
            "import argparse, json, signal, sys\n"
            "class DummyEngine:\n"
            "    def process_line(self, line: str) -> bool:\n"
            "        try:\n"
            "            obj = json.loads(line)\n"
            "            if isinstance(obj, dict) and 'latency_ms' in obj:\n"
            "                float(obj['latency_ms'])\n"
            "        except (ValueError, TypeError):\n"
            "            return False\n"
            "        return True\n"
            "def main() -> int:\n"
            "    p = argparse.ArgumentParser()\n"
            "    p.add_argument('--smoke-test', action='store_true')\n"
            "    a = p.parse_args()\n"
            "    eng = DummyEngine()\n"
            "    if a.smoke_test:\n"
            "        print('{\"ok\": true}', flush=True)\n"
            "        return 0\n"
            "    # PEP 475 trap: handler returns without raising, so sys.stdin read retries forever\n"
            "    signal.signal(signal.SIGINT, lambda *_: None)\n"
            "    for line in sys.stdin:\n"
            "        eng.process_line(line)\n"
            "    print('{\"ok\": true}', flush=True)\n"
            "    return 0\n"
            "if __name__ == '__main__':\n"
            "    raise SystemExit(main())\n",
            encoding="utf-8",
        )
        ev = ChaosEvaluator(weight=0.15, timeout_sec=4.0)
        res = ev.evaluate(buggy_dir, self.micro_arch)
        logs = "\n".join(res.details.get("log", []))
        self.assertIn("ndjson_numeric_overflow", logs)
        self.assertIn("OverflowError", logs)
        self.assertIn("open_stdin_sigint_pep475", logs)
        self.assertIn("PEP 475", logs)
        self.assertLess(res.raw_score, 100.0)

    def test_04_chaos_catches_resp2_nested_array_crlf_and_incr_overflow(self) -> None:
        """ChaosEvaluator catches RESP2 nested arrays, CRLF error injection, and 64-bit/4500-digit INCR."""
        buggy_resp = self.scratch / "buggy_resp"
        (buggy_resp / "src").mkdir(parents=True)
        (buggy_resp / "src" / "__init__.py").write_text("", encoding="utf-8")
        (buggy_resp / "src" / "engine.py").write_text(
            "class RespEngine:\n"
            "    def __init__(self):\n"
            "        self.store = {}\n"
            "    def parse_resp(self, buf):\n"
            "        if isinstance(buf, str): buf = buf.encode()\n"
            "        if buf.startswith(b'*1\\r\\n*0\\r\\n'): return (['NESTED', []], len(buf))\n"
            "        parts = buf.split(b'\\r\\n')\n"
            "        items = []\n"
            "        i = 1\n"
            "        while i < len(parts):\n"
            "            if parts[i].startswith(b'$'):\n"
            "                ln = int(parts[i][1:])\n"
            "                idx = buf.find(parts[i] + b'\\r\\n') + len(parts[i]) + 2\n"
            "                items.append(buf[idx:idx+ln])\n"
            "                break\n"
            "            i += 1\n"
            "        if b'SET' in buf:\n"
            "            toks = [p for p in parts if p and not p.startswith((b'*', b'$'))]\n"
            "            return (toks, len(buf))\n"
            "        if b'INCR' in buf:\n"
            "            toks = [p for p in parts if p and not p.startswith((b'*', b'$'))]\n"
            "            return (toks, len(buf))\n"
            "        return (items or [b'BAD\\r\\n+PONG'], len(buf))\n"
            "    def handle_command(self, msg):\n"
            "        if msg and msg[0] == 'NESTED':\n"
            "            raise RuntimeError('uncaught nested array')\n"
            "        cmd = msg[0].decode('utf-8', errors='replace') if msg else ''\n"
            "        if cmd.upper() == 'SET':\n"
            "            self.store[msg[1]] = msg[2]\n"
            "            return b'+OK\\r\\n'\n"
            "        if cmd.upper() == 'INCR':\n"
            "            v = int(self.store.get(msg[1], b'0')) + 1\n"
            "            self.store[msg[1]] = str(v).encode()\n"
            "            return f':{v}\\r\\n'.encode()\n"
            "        return f'-ERR unknown {cmd}\\r\\n'.encode()\n"
            "    def serialize_resp(self, reply):\n"
            "        return reply\n",
            encoding="utf-8",
        )
        (buggy_resp / "run.py").write_text(
            "import argparse\n"
            "p = argparse.ArgumentParser()\n"
            "p.add_argument('--smoke-test', action='store_true')\n"
            "p.parse_args()\n"
            "print('OK', flush=True)\n",
            encoding="utf-8",
        )
        ev = ChaosEvaluator(weight=0.15, timeout_sec=4.0)
        res = ev.evaluate(buggy_resp, self.resp_arch)
        logs = "\n".join(res.details.get("log", []))
        self.assertIn("resp2_nested_array", logs)
        self.assertIn("resp2_crlf_error_injection", logs)
        self.assertIn("resp2_incr_bounds_and_4300_digits", logs)
        self.assertGreaterEqual(res.details["unhandled_crashes"], 3)

    def test_05_adversarial_integrity_blocks_100_on_red_team_crits_and_tautological_tests(self) -> None:
        """Unresolved Red Team criticals AND tautological tests prevent 100.00 without mutating app_dir."""
        app_dir = self.scratch / "tautological_app"
        axioma_kv.generate_candidate_app(AblationMode.FULL_G4B, app_dir)
        (app_dir / "tests").mkdir(exist_ok=True)
        (app_dir / "tests" / "__init__.py").write_text("", encoding="utf-8")
        # Tautological test: passes even when src/engine.py is mutated!
        (app_dir / "tests" / "test_tautology.py").write_text(
            "import unittest\n"
            "class TestDummy(unittest.TestCase):\n"
            "    def test_always_true(self):\n"
            "        self.assertTrue(True)\n",
            encoding="utf-8",
        )
        (app_dir / "red_team_verdict.json").write_text(
            json.dumps({
                "red_team_pass": False,
                "critical_vulnerabilities_found": 2,
                "findings": ["[CRIT-01] Torn WAL", "[CRIT-02] TX leak"],
            }),
            encoding="utf-8",
        )
        engine_before = hashlib.sha256((app_dir / "src" / "engine.py").read_bytes()).hexdigest()

        gauntlet = MacroEvaluationGauntlet(enable_provenance=False, enable_adversarial_integrity=True)
        sc = gauntlet.evaluate_app(app_dir, self.kv_arch, mode=AblationMode.FULL_G4B)

        engine_after = hashlib.sha256((app_dir / "src" / "engine.py").read_bytes()).hexdigest()
        self.assertEqual(engine_before, engine_after, "Evaluator must NEVER mutate original app_dir on disk")

        adv = sc.pass_results["adversarial_integrity"]
        self.assertFalse(adv.passed)
        self.assertIs(adv.details["red_team_pass"], False)
        self.assertEqual(adv.details["critical_vulnerabilities_found"], 2)
        self.assertTrue(adv.details["tautological_tests_detected"])
        self.assertEqual(adv.details["kill_rate"], 0.0)
        self.assertLessEqual(sc.composite_score, 85.0)
        self.assertLess(sc.composite_score, 100.0)


if __name__ == "__main__":
    unittest.main()
