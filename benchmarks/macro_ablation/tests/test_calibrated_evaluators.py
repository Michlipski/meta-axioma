"""Calibrated regression & adversarial edge-case tests for Macro-Bench evaluators (Defects A, B, C)."""

from __future__ import annotations

from http.server import BaseHTTPRequestHandler
import inspect
from pathlib import Path
import shutil
import sys
import unittest
import uuid

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from benchmarks.macro_ablation.archetypes import axioma_kv, axioma_micro
from benchmarks.macro_ablation.domain_models import BenchmarkArchetype
from benchmarks.macro_ablation.evaluators.chaos_evaluator import (
    ChaosEvaluator,
    _MockDefaultEngine,
)
from benchmarks.macro_ablation.evaluators.efficiency_evaluator import EfficiencyEvaluator
from benchmarks.macro_ablation.evaluators.statechart_evaluator import StatechartEvaluator


def _make_scratch_dir(tag: str) -> Path:
    root = REPO_ROOT / ".scratch" / f"test_cal_{tag}_{uuid.uuid4().hex[:8]}"
    root.mkdir(parents=True, exist_ok=True)
    return root


def _write_module(path: Path, code: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(code, encoding="utf-8")


class TestCalibratedEfficiencyEvaluator(unittest.TestCase):
    """Regression tests for Defect A: EfficiencyEvaluator Landauer & test-bloat calibration."""

    def setUp(self) -> None:
        self.scratch_dir = _make_scratch_dir("eff")
        self.evaluator = EfficiencyEvaluator(weight=0.20)
        self.kv_arch = axioma_kv.get_archetype()
        self.micro_arch = axioma_micro.get_archetype()

    def tearDown(self) -> None:
        shutil.rmtree(self.scratch_dir, ignore_errors=True)

    def test_01_budget_aligned_modular_app_with_tests_passes_high(self) -> None:
        app_dir = self.scratch_dir / "modular_app"
        # ~240 prod LOC / ~24,000 bytes -> optimal_band for 15,000 token budget
        for idx in range(4):
            lines = [f'"""Module {idx} for axioma KV engine."""', ""]
            lines.append(f"class Component{idx}:")
            lines.append("    def __init__(self, namespace: str) -> None:")
            lines.append("        self.namespace = namespace")
            lines.append("        self.records = {}")
            for m in range(28):
                lines.append(f"    def operation_{idx}_{m}(self, key: str, value: str) -> str:")
                lines.append(
                    f"        payload = f'{{self.namespace}}:{{key}}:{{value}}:op_{idx}_{m}_verified_contract_payload'"
                )
                lines.append("        self.records[key] = payload")
                lines.append("        return payload")
            _write_module(app_dir / "src" / f"module_{idx}.py", "\n".join(lines) + "\n")

        _write_module(app_dir / "src" / "__init__.py", '"""Package init."""\n')
        _write_module(app_dir / "run.py", "def main() -> int:\n    return 0\n")

        # Substantial tests/ suite (~180 test LOC, well below 2.5x ceiling)
        test_lines = ["import unittest", "", "class TestSuite(unittest.TestCase):"]
        for t in range(45):
            test_lines.append(f"    def test_case_{t:02d}(self) -> None:")
            test_lines.append(f"        expected_token = 'namespace:key_{t}:value_{t}:verified'")
            test_lines.append("        self.assertTrue(len(expected_token) > 10)")
        _write_module(app_dir / "tests" / "test_suite.py", "\n".join(test_lines) + "\n")

        res = self.evaluator.evaluate(app_dir, self.kv_arch)
        self.assertTrue(res.passed, f"Expected pass, got details={res.details}")
        self.assertGreaterEqual(res.raw_score, 80.0)
        for key in (
            "estimated_token_spend",
            "target_token_budget",
            "prod_loc",
            "test_loc",
            "token_factor",
            "loc_factor",
            "test_bloat_factor",
            "calibration_zone",
        ):
            self.assertIn(key, res.details)
        self.assertEqual(res.details["calibration_zone"], "optimal_band")
        self.assertEqual(res.details["test_bloat_factor"], 1.0)

    def test_02_concise_viable_app_axioma_micro(self) -> None:
        app_dir = self.scratch_dir / "concise_micro"
        # ~75 prod LOC (< 0.4 * 8000 tokens = 3200 tokens, yet >= 0.5 * 120 = 60 LOC)
        lines = [
            "import json",
            "import sys",
            "",
            "class PercentileTracker:",
            "    def __init__(self, limit: int = 1000) -> None:",
            "        self.limit = limit",
            "        self.values = []",
            "    def push(self, val: float) -> None:",
            "        self.values.append(val)",
            "        if len(self.values) > self.limit:",
            "            self.values.pop(0)",
        ]
        for i in range(32):
            lines.append(f"def helper_{i}(x: int) -> int:")
            lines.append(f"    return x + {i}")
        _write_module(app_dir / "run.py", "\n".join(lines) + "\n")

        res = self.evaluator.evaluate(app_dir, self.micro_arch)
        self.assertTrue(res.passed, f"Expected concise pass, got {res.details}")
        self.assertGreaterEqual(res.raw_score, 85.0)
        self.assertIn(res.details["calibration_zone"], ("concise_viable", "optimal_band"))
        self.assertEqual(res.details["calibration_zone"], "concise_viable")

    def test_03_hollow_stub_fails(self) -> None:
        app_dir = self.scratch_dir / "hollow_stub"
        stub = "\n".join(f"x_{i} = {i}" for i in range(10)) + "\n"
        _write_module(app_dir / "run.py", stub)

        res = self.evaluator.evaluate(app_dir, self.kv_arch)
        self.assertFalse(res.passed)
        self.assertLess(res.raw_score, 60.0)

    def test_04_bloated_boilerplate_fails(self) -> None:
        app_dir = self.scratch_dir / "bloated_app"
        # > 4x LOC (target=350 -> >1400) and > 4x token budget (15000 -> >60000 tokens ~= 230KB)
        lines = ["def boilerplate() -> int:"]
        for i in range(1600):
            lines.append(
                f"    val_{i} = 'bloated_redundant_padding_string_segment_repeated_for_landauer_waste_{i:04d}_{'X' * 70}'"
            )
        lines.append("    return 0")
        _write_module(app_dir / "run.py", "\n".join(lines) + "\n")

        res = self.evaluator.evaluate(app_dir, self.kv_arch)
        self.assertFalse(res.passed)
        self.assertLess(res.raw_score, 60.0)
        self.assertEqual(res.details["calibration_zone"], "over_budget_waste")

    def test_05_tests_stuffing_attack_reduces_test_bloat_factor(self) -> None:
        app_dir = self.scratch_dir / "test_stuffed_app"
        prod_lines = [f"def prod_fn_{i}(v: int) -> int:\n    return v + {i}" for i in range(60)]
        _write_module(app_dir / "run.py", "\n".join(prod_lines) + "\n")

        # Stuff > 2.5x ceiling (max_reasonable_test_loc = max(600, 2.5 * 350) = 875)
        bloat_lines = ["import unittest", "", "class TestBloat(unittest.TestCase):"]
        for i in range(1200):
            bloat_lines.append(f"    def test_bloat_{i}(self) -> None:")
            bloat_lines.append(f"        self.assertEqual({i}, {i})")
        _write_module(app_dir / "tests" / "test_bloat.py", "\n".join(bloat_lines) + "\n")

        res = self.evaluator.evaluate(app_dir, self.kv_arch)
        self.assertLess(res.details["test_bloat_factor"], 1.0)


class TestCalibratedChaosEvaluator(unittest.TestCase):
    """Regression tests for Defect B: ChaosEvaluator engine discovery, payload normalization, and subprocess chaos."""

    def setUp(self) -> None:
        self.scratch_dir = _make_scratch_dir("chaos")
        self.evaluator = ChaosEvaluator(weight=0.15, timeout_sec=5.0)
        self.kv_arch = axioma_kv.get_archetype()
        self.micro_arch = axioma_micro.get_archetype()

    def tearDown(self) -> None:
        shutil.rmtree(self.scratch_dir, ignore_errors=True)

    def test_01_mock_default_engine_positional_and_keyword(self) -> None:
        eng = _MockDefaultEngine()
        self.assertTrue(eng.set("k1", "v1"))
        self.assertEqual(eng.get("k1"), "v1")
        self.assertTrue(eng.delete("k1"))
        self.assertIsNone(eng.get("k1"))

        self.assertTrue(eng.set(key="k2", value="v2"))
        self.assertEqual(eng.get(key="k2"), "v2")
        self.assertTrue(eng.delete(key="k2"))
        self.assertIsNone(eng.get(key="k2"))

    def test_02_non_storage_engine_discovery_and_property_preservation(self) -> None:
        for idx, (cls_name, extra_sig, alias_attr) in enumerate(
            [
                ("KVEngine", "data_dir: Path, node_id: str = 'n0'", "engine"),
                ("GatewayRouter", "data_dir: Path, node_id: str", "router"),
                ("RaftNode", "node_id: str, peers: list, data_dir: Path", "node"),
            ]
        ):
            app_dir = self.scratch_dir / f"custom_eng_{idx}"
            _write_module(app_dir / "src" / "__init__.py", "")
            _write_module(
                app_dir / "src" / "engine.py",
                f"""from pathlib import Path

class {cls_name}:
    def __init__(self, {extra_sig}) -> None:
        self.data_dir = Path(data_dir)
        self.node_id = node_id
        self.store = {{}}

    def get(self, key: str):
        return self.store.get(key)

    def set(self, key: str, value: str) -> bool:
        self.store[key] = value
        return True

    def route(self, path: str) -> str:
        return f"{{self.node_id}}:{{path}}"
""",
            )
            _write_module(
                app_dir / "run.py",
                f"""from http.server import BaseHTTPRequestHandler
import json
from src.engine import {cls_name}

class CustomHandler(BaseHTTPRequestHandler):
    @property
    def gateway(self) -> str:
        return "preserved_property_descriptor"

    def do_POST(self) -> None:
        length = int(self.headers.get("Content-Length", "0") or 0)
        if length > 1024 * 1024:
            self.send_response(413)
            self.end_headers()
            self.wfile.write(b'{{"error": "payload too large"}}')
            return
        raw = self.rfile.read(length)
        if length > 0 and len(raw) != length:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b'{{"error": "truncated body"}}')
            return
        eng = getattr(self, "{alias_attr}", None) or getattr(self.server, "{alias_attr}", None)
        if not isinstance(eng, {cls_name}):
            self.send_response(500)
            self.end_headers()
            self.wfile.write(b'{{"error": "engine not wired"}}')
            return
        if self.gateway != "preserved_property_descriptor":
            self.send_response(500)
            self.end_headers()
            self.wfile.write(b'{{"error": "property clobbered"}}')
            return
        try:
            data = json.loads(raw.decode("utf-8")) if raw else {{}}
        except Exception:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b'{{"error": "bad json"}}')
            return
        if isinstance(data, dict) and isinstance(data.get("ttl_seconds"), bool):
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b'{{"error": "bool not allowed for ttl_seconds"}}')
            return
        eng.set("probe", str(data))
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'{{"ok": true}}')

    def log_message(self, format, *args) -> None:
        pass
""",
            )

            res = self.evaluator.evaluate(app_dir, self.kv_arch)
            self.assertTrue(res.passed, f"{cls_name} failed chaos: {res.details}")
            self.assertEqual(res.raw_score, 100.0)
            self.assertEqual(res.details["chaos_mode"], "http_handler")

            # Also verify _prepare_server_context directly preserves @property descriptors
            pre_mods = set(sys.modules.keys())
            try:
                handler_cls = self.evaluator._load_handler_class(app_dir, pre_modules=pre_mods)
                self.assertIsNotNone(handler_cls)
                server, cleanup = self.evaluator._prepare_server_context(app_dir, handler_cls)
                try:
                    self.assertIsInstance(
                        inspect.getattr_static(handler_cls, "gateway"),
                        property,
                    )
                    self.assertIsInstance(getattr(handler_cls, alias_attr), object)
                    self.assertEqual(type(getattr(server, alias_attr)).__name__, cls_name)
                finally:
                    if cleanup:
                        cleanup()
            finally:
                from benchmarks.macro_ablation.evaluators.chaos_evaluator import _purge_app_modules

                _purge_app_modules(app_dir=app_dir, pre_modules=pre_mods)

    def test_03_probe_payload_and_body_delivered(self) -> None:
        app_dir = self.scratch_dir / "payload_vs_body"
        _write_module(
            app_dir / "run.py",
            """from http.server import BaseHTTPRequestHandler
import json

class PayloadEchoHandler(BaseHTTPRequestHandler):
    def do_POST(self) -> None:
        length = int(self.headers.get("Content-Length", "0") or 0)
        raw = self.rfile.read(length)
        if not raw:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(b'{"error": "missing payload"}')
            return
        data = json.loads(raw.decode("utf-8"))
        if not isinstance(data, dict) or not ({"mode", "burst_concurrent"} & set(data.keys())):
            self.send_response(500)
            self.end_headers()
            self.wfile.write(b'{"error": "unexpected payload"}')
            return
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'{"ok": true}')

    def log_message(self, format, *args) -> None:
        pass
""",
        )
        arch = BenchmarkArchetype(
            id="test_payload_arch",
            name="Payload Arch",
            domain="Test",
            prompt="test",
            specification={},
            expected_verbs=["handle"],
            expected_endpoints=["POST /test"],
            expected_models=[],
            state_transitions=[],
            chaos_payloads=[
                {"name": "body_probe", "method": "POST", "path": "/test", "body": {"mode": "body"}},
                {"name": "payload_probe", "method": "POST", "path": "/test", "payload": {"mode": "payload"}},
            ],
        )

        res = self.evaluator.evaluate(app_dir, arch)
        self.assertTrue(res.passed, f"Payload normalization failed: {res.details}")
        self.assertEqual(res.raw_score, 100.0)
        self.assertEqual(res.details["total_probes"], 22)

    def test_04_non_http_daemon_subprocess_chaos(self) -> None:
        app_dir = self.scratch_dir / "non_http_daemon"
        _write_module(
            app_dir / "run.py",
            """import argparse
import signal
import sys
import threading

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke-test", action="store_true")
    parser.add_argument("--port", type=int, default=9000)
    args = parser.parse_args()
    if args.smoke_test:
        print("DAEMON SMOKE OK", flush=True)
        return 0
    stop = threading.Event()
    signal.signal(signal.SIGTERM, lambda *_: stop.set())
    signal.signal(signal.SIGINT, lambda *_: stop.set())
    print(f"DAEMON LISTENING ON {args.port}", flush=True)
    stop.wait(timeout=5.0)
    return 0

if __name__ == "__main__":
    sys.exit(main())
""",
        )
        arch = BenchmarkArchetype(
            id="non_http_daemon",
            name="Non-HTTP Daemon",
            domain="Consensus",
            prompt="daemon",
            specification={},
            expected_verbs=["propose"],
            expected_endpoints=["POST /propose"],  # Non-empty, yet no BaseHTTPRequestHandler
            expected_models=[],
            state_transitions=[],
            chaos_payloads=[],
        )

        res = self.evaluator.evaluate(app_dir, arch)
        self.assertEqual(res.details["chaos_mode"], "subprocess_and_socketpair")
        self.assertTrue(res.passed, f"Non-HTTP daemon chaos failed: {res.details}")
        self.assertGreaterEqual(res.raw_score, 70.0)
        self.assertNotEqual(res.raw_score, 50.0)

    def test_05_non_http_streaming_cli_axioma_micro_style(self) -> None:
        app_dir = self.scratch_dir / "micro_cli"
        _write_module(
            app_dir / "run.py",
            """import argparse
import json
import sys

class StreamParser:
    def parse(self, line: str) -> dict | None:
        try:
            obj = json.loads(line)
            return obj if isinstance(obj, dict) else None
        except Exception:
            return None

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke-test", action="store_true")
    args, _ = parser.parse_known_args()
    if args.smoke_test:
        print("MICRO CLI SMOKE OK", flush=True)
        return 0
    sp = StreamParser()
    count = 0
    for raw in sys.stdin.buffer:
        text = raw.decode("utf-8", errors="replace").strip()
        if text and sp.parse(text) is not None:
            count += 1
    print(json.dumps({"processed": count}), flush=True)
    return 0

if __name__ == "__main__":
    sys.exit(main())
""",
        )

        res = self.evaluator.evaluate(app_dir, self.micro_arch)
        self.assertEqual(res.details["chaos_mode"], "subprocess_and_socketpair")
        self.assertTrue(res.passed, f"Streaming CLI chaos failed: {res.details}")
        self.assertGreaterEqual(res.raw_score, 70.0)
        self.assertNotEqual(res.raw_score, 50.0)

    def test_06_broken_daemon_fails_subprocess_chaos(self) -> None:
        app_dir = self.scratch_dir / "broken_daemon"
        _write_module(
            app_dir / "run.py",
            """import sys
raise RuntimeError("Intentional startup crash on malformed/smoke invocation")
""",
        )

        res = self.evaluator.evaluate(app_dir, self.micro_arch)
        self.assertEqual(res.details["chaos_mode"], "subprocess_and_socketpair")
        self.assertFalse(res.passed)
        self.assertLess(res.raw_score, 70.0)
        self.assertGreater(res.details["unhandled_crashes"], 0)

    def test_07_zero_sys_modules_and_sys_path_leakage(self) -> None:
        app_dir = self.scratch_dir / "leak_check"
        _write_module(app_dir / "src" / "__init__.py", "")
        _write_module(
            app_dir / "src" / "kv_engine.py",
            """class KVEngine:
    def get(self, key: str): return None
    def set(self, key: str, value: str) -> bool: return True
""",
        )
        _write_module(
            app_dir / "run.py",
            """from http.server import BaseHTTPRequestHandler
class SimpleHandler(BaseHTTPRequestHandler):
    def do_POST(self) -> None:
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"{}")
    def log_message(self, format, *args) -> None:
        pass
""",
        )

        pre_modules = set(sys.modules.keys())
        pre_path = list(sys.path)

        res = self.evaluator.evaluate(app_dir, self.kv_arch)
        self.assertTrue(res.passed)

        post_modules = set(sys.modules.keys())
        new_modules = post_modules - pre_modules
        leaked = [m for m in new_modules if m == "src" or m.startswith("src.") or m.startswith("app_chaos_")]
        self.assertEqual(leaked, [], f"Leaked modules in sys.modules: {leaked}")
        self.assertEqual(sys.path, pre_path)
        self.assertNotIn(str(app_dir.resolve()), sys.path)


class TestCalibratedStatechartEvaluator(unittest.TestCase):
    """Regression tests for Defect C: StatechartEvaluator typing, package loading, and tightened AST fallback."""

    def setUp(self) -> None:
        self.scratch_dir = _make_scratch_dir("sc")
        self.evaluator = StatechartEvaluator(weight=0.20)

    def tearDown(self) -> None:
        shutil.rmtree(self.scratch_dir, ignore_errors=True)

    def test_01_invoke_action_defaults_pep563_pep604_and_heuristics(self) -> None:
        app_dir = self.scratch_dir / "typed_engine"
        _write_module(app_dir / "src" / "__init__.py", "")
        _write_module(
            app_dir / "src" / "engine.py",
            """from __future__ import annotations
from pathlib import Path

class TypedEngine:
    def __init__(self) -> None:
        self.state = "IDLE"
        self.recorded = {}

    def transition_with_defaults(
        self,
        key: str,
        timeout: float = 2.5,
        *args: str,
        retries: int,
        interval: float | None,
        limit: int | None,
        meta: dict[str, str],
        tags: list[str],
        workdir: Path,
        port,
        term,
        index,
        count,
        **kwargs: str,
    ) -> str:
        # Must preserve default 2.5 and never receive 'test_arg' for numeric/generic params
        assert timeout == 2.5, f"Expected default 2.5, got {timeout!r}"
        assert isinstance(retries, int), f"Expected int retries, got {retries!r}"
        assert isinstance(interval, float), f"Expected float interval, got {interval!r}"
        assert isinstance(limit, int), f"Expected int limit, got {limit!r}"
        assert isinstance(meta, dict), f"Expected dict meta, got {meta!r}"
        assert isinstance(tags, list), f"Expected list tags, got {tags!r}"
        assert isinstance(workdir, Path), f"Expected Path workdir, got {workdir!r}"
        assert float(port) > 0, f"Expected numeric port, got {port!r}"
        assert int(term) >= 1, f"Expected numeric term, got {term!r}"
        assert int(index) >= 1, f"Expected numeric index, got {index!r}"
        assert int(count) >= 1, f"Expected numeric count, got {count!r}"
        self.recorded["timeout"] = timeout
        self.state = "ACTIVE"
        return self.state
""",
        )

        arch = BenchmarkArchetype(
            id="typed_arch",
            name="Typed Arch",
            domain="Test",
            prompt="test",
            specification={},
            expected_verbs=["transition_with_defaults"],
            expected_endpoints=[],
            expected_models=[],
            state_transitions=[
                {"from": "IDLE", "to": "ACTIVE", "action": "transition_with_defaults", "valid": True},
            ],
            chaos_payloads=[],
        )

        res = self.evaluator.evaluate(app_dir, arch)
        self.assertTrue(res.passed, f"Typed invocation failed: {res.details}")
        self.assertEqual(res.details["evaluation_mode"], "dynamic_execution")
        self.assertEqual(res.raw_score, 100.0)
        self.assertEqual(res.details["defects_detected"], 0)

    def test_02_package_aware_loading_enum_and_prerequisite_chains(self) -> None:
        app_dir = self.scratch_dir / "pkg_enum_engine"
        _write_module(app_dir / "src" / "__init__.py", "")
        _write_module(
            app_dir / "src" / "models.py",
            """from enum import Enum

class TxState(str, Enum):
    IDLE = "IDLE"
    IN_TRANSACTION = "IN_TRANSACTION"
    COMMITTED = "COMMITTED"
    ROLLED_BACK = "ROLLED_BACK"
""",
        )
        _write_module(
            app_dir / "src" / "engine.py",
            """from .models import TxState

class KVStoreEngine:
    def __init__(self) -> None:
        self.state = TxState.IDLE
        self.active_tx = None

    def begin_transaction(self) -> str:
        if self.state != TxState.IDLE:
            raise ValueError("Already in transaction")
        self.state = TxState.IN_TRANSACTION
        self.active_tx = "tx_1"
        return self.active_tx

    def commit_transaction(self) -> int:
        if self.state != TxState.IN_TRANSACTION:
            raise ValueError("Cannot commit outside transaction")
        self.state = TxState.COMMITTED
        self.active_tx = None
        return 1

    def rollback_transaction(self) -> bool:
        if self.state != TxState.IN_TRANSACTION or self.active_tx is None:
            raise ValueError("Cannot rollback without active transaction")
        self.state = TxState.ROLLED_BACK
        self.active_tx = None
        return True
""",
        )

        arch = BenchmarkArchetype(
            id="pkg_enum_arch",
            name="Pkg Enum Arch",
            domain="KV",
            prompt="test",
            specification={},
            expected_verbs=["begin_transaction", "commit_transaction", "rollback_transaction"],
            expected_endpoints=[],
            expected_models=["TxState"],
            state_transitions=[
                {"from": "IDLE", "to": "IN_TRANSACTION", "action": "begin_transaction", "valid": True},
                {"from": "IN_TRANSACTION", "to": "COMMITTED", "action": "commit_transaction", "valid": True},
                {"from": "IN_TRANSACTION", "to": "ROLLED_BACK", "action": "rollback_transaction", "valid": True},
                {"from": "IDLE", "to": "COMMITTED", "action": "commit_transaction", "valid": False},
            ],
            chaos_payloads=[],
        )

        res = self.evaluator.evaluate(app_dir, arch)
        self.assertTrue(res.passed, f"Package/Enum/prereq chain failed: {res.details}")
        self.assertEqual(res.details["evaluation_mode"], "dynamic_execution")
        self.assertEqual(res.details["engine_class"], "KVStoreEngine")
        self.assertEqual(res.raw_score, 100.0)
        self.assertEqual(res.details["valid_passed"], 3)
        self.assertEqual(res.details["invalid_rejected"], 1)

    def test_03_fake_ast_gaming_dummy_app_fails(self) -> None:
        app_dir = self.scratch_dir / "ast_gaming_dummy"
        _write_module(
            app_dir / "run.py",
            """STATES = ["IDLE", "ACTIVE", "COMMITTED"]

def run_dummy():
    if True:
        pass
    if 1 == 1:
        x = "IDLE"
    return x
""",
        )
        arch = BenchmarkArchetype(
            id="ast_dummy_arch",
            name="AST Dummy Arch",
            domain="Test",
            prompt="test",
            specification={},
            expected_verbs=["start", "commit"],
            expected_endpoints=[],
            expected_models=[],
            state_transitions=[
                {"from": "IDLE", "to": "ACTIVE", "action": "start", "valid": True},
                {"from": "ACTIVE", "to": "COMMITTED", "action": "commit", "valid": True},
            ],
            chaos_payloads=[],
        )

        res = self.evaluator.evaluate(app_dir, arch)
        self.assertEqual(res.details["evaluation_mode"], "static_ast_fallback")
        self.assertFalse(res.passed)
        self.assertLess(res.raw_score, 60.0)
        self.assertEqual(res.details["paired_guards_found"], 0)

    def test_04_legitimate_static_only_app_capped_at_75_and_ignores_tests(self) -> None:
        app_dir = self.scratch_dir / "legit_static"
        _write_module(app_dir / "src" / "__init__.py", "")
        # Pure functions (no *Engine class) with state constants + paired state guards + action funcs
        _write_module(
            app_dir / "src" / "workflow.py",
            """ALLOWED_TRANSITIONS = {
    "IDLE": {"ACTIVE"},
    "ACTIVE": {"COMMITTED"},
}

def start(current_state: str) -> str:
    if current_state != "IDLE":
        raise ValueError("Invalid state")
    current_state = "ACTIVE"
    return current_state

def commit(current_state: str) -> str:
    if current_state != "ACTIVE":
        raise ValueError("Invalid state")
    current_state = "COMMITTED"
    return current_state
""",
        )
        arch = BenchmarkArchetype(
            id="static_arch",
            name="Static Arch",
            domain="Test",
            prompt="test",
            specification={},
            expected_verbs=["start", "commit"],
            expected_endpoints=[],
            expected_models=[],
            state_transitions=[
                {"from": "IDLE", "to": "ACTIVE", "action": "start", "valid": True},
                {"from": "ACTIVE", "to": "COMMITTED", "action": "commit", "valid": True},
            ],
            chaos_payloads=[],
        )

        res = self.evaluator.evaluate(app_dir, arch)
        self.assertEqual(res.details["evaluation_mode"], "static_ast_fallback")
        self.assertLessEqual(res.raw_score, 75.0)
        self.assertTrue(res.passed)
        self.assertGreater(res.details["paired_guards_found"], 0)

        # Verify tests/ files are ignored by AST fallback
        tests_only_dir = self.scratch_dir / "tests_only_static"
        _write_module(tests_only_dir / "run.py", "def noop() -> None:\n    pass\n")
        _write_module(
            tests_only_dir / "tests" / "test_fake_states.py",
            (app_dir / "src" / "workflow.py").read_text(encoding="utf-8"),
        )
        res_tests_only = self.evaluator.evaluate(tests_only_dir, arch)
        self.assertEqual(res_tests_only.details["evaluation_mode"], "static_ast_fallback")
        self.assertFalse(res_tests_only.passed)
        self.assertEqual(res_tests_only.raw_score, 0.0)


if __name__ == "__main__":
    unittest.main()
