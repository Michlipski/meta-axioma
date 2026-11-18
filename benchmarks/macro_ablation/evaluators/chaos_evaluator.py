r"""Pass 3: Byzantine Chaos Survival Evaluator ($S_{chaos}$, 15%).

Evaluates:
- Resilience against malformed JSON bodies, severed socket requests, and unexpected types.
- Concurrent burst traffic stress (20 simultaneous requests) for HTTP handlers.
- Subprocess, malformed CLI/stdin fuzzing, POSIX socketpair framing chaos, and SIGTERM
  restartability probes for non-HTTP daemons and CLI utilities.
- Asserts zero unhandled 500 Internal Server Error crashes or unhandled tracebacks.
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from enum import Enum
from http.server import BaseHTTPRequestHandler
import importlib
import importlib.util
import inspect
import io
import json
import os
from pathlib import Path
import select
import shutil
import socket
import subprocess
import sys
from typing import Any, Callable, Dict, List, Optional, Tuple
import uuid

from ..domain_models import BenchmarkArchetype, EvaluationPassResult


_WORKSPACE_ROOT = Path(__file__).resolve().parents[3]


def _make_scratch_temp_dir(prefix: str = "chaos_eval_") -> Path:
    """Allocates a hermetic temporary directory strictly inside workspace .scratch/."""
    scratch_root = _WORKSPACE_ROOT / ".scratch"
    scratch_root.mkdir(parents=True, exist_ok=True)
    temp_dir = scratch_root / f"{prefix}{uuid.uuid4().hex[:10]}"
    temp_dir.mkdir(parents=True, exist_ok=True)
    return temp_dir


def _purge_app_modules(
    app_dir: Optional[Path] = None,
    pre_modules: Optional[set[str]] = None,
) -> None:
    """Purges cached application modules from sys.modules to prevent cross-contamination."""
    resolved_app = app_dir.resolve() if app_dir is not None else None
    for key in list(sys.modules.keys()):
        if key == "src" or key.startswith("src.") or key.startswith("app_chaos_"):
            sys.modules.pop(key, None)
            continue
        if pre_modules is not None and key not in pre_modules:
            mod = sys.modules.get(key)
            mod_file = getattr(mod, "__file__", None) if mod is not None else None
            if resolved_app is not None and mod_file:
                try:
                    mod_path = Path(mod_file).resolve()
                    if resolved_app == mod_path or resolved_app in mod_path.parents:
                        sys.modules.pop(key, None)
                        continue
                except Exception:
                    pass
            # Also evict any pure newly added top-level module loaded during app inspection
            if mod_file and resolved_app is not None and str(resolved_app) in str(mod_file):
                sys.modules.pop(key, None)


class _MockDefaultEngine:
    """Duck-typed default storage engine fallback for HTTP handlers."""

    def __init__(self) -> None:
        self._store: Dict[str, Any] = {}
        self._txs: Dict[str, Dict[str, Any]] = {}

    def get(
        self,
        k: Optional[str] = None,
        *args: Any,
        key: Optional[str] = None,
        **kwargs: Any,
    ) -> Any:
        actual_key = k if k is not None else key
        return self._store.get(actual_key)

    def set(
        self,
        k: Optional[str] = None,
        v: Any = None,
        *args: Any,
        key: Optional[str] = None,
        value: Any = None,
        **kwargs: Any,
    ) -> bool:
        actual_key = k if k is not None else key
        actual_val = v if v is not None else value
        if actual_key is not None:
            self._store[actual_key] = actual_val
        return True

    def delete(
        self,
        k: Optional[str] = None,
        *args: Any,
        key: Optional[str] = None,
        **kwargs: Any,
    ) -> bool:
        actual_key = k if k is not None else key
        return self._store.pop(actual_key, None) is not None

    def begin_transaction(self, *args: Any, **kwargs: Any) -> str:
        return "tx_mock_1"

    def tx_begin(self, *args: Any, **kwargs: Any) -> str:
        return "tx_mock_1"

    def commit_transaction(self, *args: Any, **kwargs: Any) -> int:
        return 1

    def tx_commit(self, *args: Any, **kwargs: Any) -> int:
        return 1

    def rollback_transaction(self, *args: Any, **kwargs: Any) -> bool:
        return True

    def tx_rollback(self, *args: Any, **kwargs: Any) -> bool:
        return True

    def stats(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return {"keys": len(self._store), "transactions": len(self._txs)}

    def health_check(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return {"status": "healthy"}

    def close(self) -> None:
        pass


class _MockHTTPServer:
    """Simulates an HTTPServer instance to satisfy handler.server references."""

    def __init__(self, engine: Any = None) -> None:
        self.engine = engine
        self.gateway = engine
        self.router = engine
        self.store = engine
        self.node = engine
        self.service = engine
        self.coordinator = engine
        self.executor = engine
        self.storage = engine
        self.server_address = ("127.0.0.1", 8088)
        self.server_name = "127.0.0.1"
        self.server_port = 8088


class _RetainingBytesIO(io.BytesIO):
    """BytesIO buffer that retains written response bytes even after StreamRequestHandler.finish() closes it."""

    def __init__(self) -> None:
        super().__init__()
        self._cached_bytes: bytes = b""

    def close(self) -> None:
        if not self.closed:
            self._cached_bytes = self.getvalue()
        super().close()

    def retained_value(self) -> bytes:
        if self.closed:
            return self._cached_bytes
        return self.getvalue()


class _MockRequestSocket:
    """Simulates a TCP socket stream for hermetic in-process HTTP evaluation."""

    def __init__(self, request_bytes: bytes) -> None:
        self._rfile = io.BytesIO(request_bytes)
        self._wfile = _RetainingBytesIO()

    def makefile(self, mode: str, *args: Any, **kwargs: Any) -> io.BytesIO:
        if "b" in mode and "r" in mode:
            return self._rfile
        return self._wfile

    def sendall(self, data: bytes) -> None:
        if not self._wfile.closed:
            self._wfile.write(data)

    def get_response(self) -> bytes:
        return self._wfile.retained_value()


class ChaosEvaluator:
    """Evaluates Pass 3: Byzantine Chaos Survival ($S_{chaos}$, Weight = 15%)."""

    _ENGINE_SUFFIXES = (
        "Engine",
        "Node",
        "Router",
        "Store",
        "Manager",
        "Service",
        "Gateway",
        "Coordinator",
        "Executor",
        "Storage",
    )
    _ENGINE_METHODS = {
        "get",
        "set",
        "delete",
        "begin_transaction",
        "route",
        "submit",
        "transition",
        "execute",
        "parse",
    }
    _SERVER_ALIASES = (
        "engine",
        "gateway",
        "router",
        "store",
        "node",
        "service",
        "coordinator",
        "executor",
    )

    def __init__(self, weight: float = 0.15, timeout_sec: float = 6.0) -> None:
        self.weight = weight
        self.timeout_sec = timeout_sec

    def evaluate(self, app_dir: Path, archetype: BenchmarkArchetype) -> EvaluationPassResult:
        app_dir = app_dir.resolve()
        entrypoint = (app_dir / "run.py").resolve()
        if not entrypoint.exists():
            return EvaluationPassResult(
                pass_name="chaos",
                weight=self.weight,
                raw_score=0.0,
                weighted_score=0.0,
                details={"error": "Entrypoint run.py does not exist"},
                passed=False,
            )

        pre_modules = set(sys.modules.keys())
        orig_sys_path = list(sys.path)
        cleanup_fn: Optional[Callable[[], None]] = None

        try:
            # CLI / non-HTTP archetypes route directly to subprocess + socketpair chaos
            if not getattr(archetype, "expected_endpoints", None):
                return self._evaluate_subprocess_chaos(app_dir, entrypoint, archetype)

            handler_cls = self._load_handler_class(app_dir, pre_modules=pre_modules)
            if handler_cls is None:
                return self._evaluate_subprocess_chaos(app_dir, entrypoint, archetype)

            server_instance, cleanup_fn = self._prepare_server_context(app_dir, handler_cls)

            probes = archetype.chaos_payloads or []
            total_probes = 0
            unhandled_crashes = 0
            graceful_responses = 0
            details_log: List[str] = []

            # 1. Custom Archetype Payloads (normalize body vs payload per VULN-CAL-03)
            for probe in probes:
                total_probes += 1
                name = probe.get("name", "custom_probe")
                method = probe.get("method", "POST")
                path = probe.get("path", "/test")
                body = probe.get("body", probe.get("payload", ""))

                status, err = self._dispatch_probe(
                    handler_cls, method, path, body, server=server_instance
                )
                if status == 500 or err:
                    unhandled_crashes += 1
                    details_log.append(f"Probe '{name}' triggered unhandled failure: {err or 'HTTP 500'}")
                else:
                    graceful_responses += 1
                    details_log.append(f"Probe '{name}' gracefully handled (HTTP {status})")

            # 2. Concurrency Burst Flood (20 concurrent requests)
            burst_count = 20
            burst_crashes = 0
            with ThreadPoolExecutor(max_workers=8) as executor:
                futures = [
                    executor.submit(
                        self._dispatch_probe,
                        handler_cls,
                        "POST",
                        "/healthz",
                        '{"burst_concurrent": true}',
                        server=server_instance,
                    )
                    for _ in range(burst_count)
                ]
                for fut in as_completed(futures):
                    total_probes += 1
                    status, err = fut.result()
                    if status == 500 or err:
                        burst_crashes += 1
                        unhandled_crashes += 1
                    else:
                        graceful_responses += 1

            if burst_crashes > 0:
                details_log.append(f"Burst concurrency test suffered {burst_crashes}/{burst_count} crashes")
            else:
                details_log.append(f"Burst concurrency test survived {burst_count}/{burst_count} requests")

            raw_score = (
                max(0.0, (1.0 - (unhandled_crashes / total_probes))) * 100.0
                if total_probes > 0
                else 100.0
            )
            raw_score = round(max(0.0, min(100.0, raw_score)), 2)
            weighted_score = round(raw_score * self.weight, 2)

            return EvaluationPassResult(
                pass_name="chaos",
                weight=self.weight,
                raw_score=raw_score,
                weighted_score=weighted_score,
                details={
                    "chaos_mode": "http_handler",
                    "total_probes": total_probes,
                    "graceful_responses": graceful_responses,
                    "unhandled_crashes": unhandled_crashes,
                    "log": details_log[:10],
                },
                passed=(raw_score >= 70.0),
            )
        finally:
            if cleanup_fn:
                try:
                    cleanup_fn()
                except Exception:
                    pass
            sys.path[:] = orig_sys_path
            _purge_app_modules(app_dir=app_dir, pre_modules=pre_modules)

    def _load_handler_class(
        self,
        app_dir: Path,
        pre_modules: Optional[set[str]] = None,
    ) -> Optional[type]:
        """Loads the BaseHTTPRequestHandler subclass from the application, scanning run.py and src submodules."""
        app_dir = app_dir.resolve()
        _purge_app_modules(app_dir=app_dir, pre_modules=pre_modules)

        if str(app_dir) not in sys.path:
            sys.path.insert(0, str(app_dir))

        # 1. Search run.py directly
        entrypoint = app_dir / "run.py"
        if entrypoint.exists():
            module_name = f"app_chaos_run_{app_dir.name}_{abs(hash(str(app_dir))) % 10000}"
            try:
                spec = importlib.util.spec_from_file_location(module_name, str(entrypoint))
                if spec and spec.loader:
                    mod = importlib.util.module_from_spec(spec)
                    sys.modules[module_name] = mod
                    spec.loader.exec_module(mod)
                    for attr in dir(mod):
                        val = getattr(mod, attr)
                        if (
                            isinstance(val, type)
                            and issubclass(val, BaseHTTPRequestHandler)
                            and val is not BaseHTTPRequestHandler
                        ):
                            return val
            except Exception:
                pass

        # 2. Search app_dir / "src" submodules (e.g. server.py, handlers.py, api.py)
        src_dir = app_dir / "src"
        if src_dir.exists():
            for py_file in sorted(src_dir.glob("*.py")):
                if py_file.name == "run.py" or py_file.name.startswith("test_") or py_file.name == "__init__.py":
                    continue
                module_path = f"src.{py_file.stem}"
                try:
                    mod = importlib.import_module(module_path)
                    for attr in dir(mod):
                        val = getattr(mod, attr)
                        if (
                            isinstance(val, type)
                            and issubclass(val, BaseHTTPRequestHandler)
                            and val is not BaseHTTPRequestHandler
                        ):
                            return val
                except Exception:
                    pass

        # 3. Search other top-level .py files in app_dir
        for py_file in sorted(app_dir.glob("*.py")):
            if py_file.name == "run.py" or py_file.name.startswith("test_"):
                continue
            sub_mod_name = f"app_chaos_top_{app_dir.name}_{py_file.stem}"
            try:
                spec = importlib.util.spec_from_file_location(sub_mod_name, str(py_file))
                if spec and spec.loader:
                    mod = importlib.util.module_from_spec(spec)
                    sys.modules[sub_mod_name] = mod
                    spec.loader.exec_module(mod)
                    for attr in dir(mod):
                        val = getattr(mod, attr)
                        if (
                            isinstance(val, type)
                            and issubclass(val, BaseHTTPRequestHandler)
                            and val is not BaseHTTPRequestHandler
                        ):
                            return val
            except Exception:
                pass

        return None

    def _discover_engine_candidates(self, app_dir: Path) -> List[type]:
        """Scans loaded app modules, app_dir/src/*.py, and top-level *.py for engine-like classes."""
        candidates: List[type] = []
        seen: set[type] = set()
        app_dir_resolved = app_dir.resolve()

        def _is_candidate_cls(val: Any) -> bool:
            if not isinstance(val, type):
                return False
            if issubclass(val, (BaseHTTPRequestHandler, BaseException, Enum)):
                return False
            name = getattr(val, "__name__", "")
            if name.startswith("_"):
                return False
            if name.endswith(self._ENGINE_SUFFIXES):
                return True
            public_methods = {
                m for m in dir(val)
                if not m.startswith("_") and callable(getattr(val, m, None))
            }
            return len(public_methods.intersection(self._ENGINE_METHODS)) >= 2

        def _collect_from_mod(mod: Any) -> None:
            mod_name = getattr(mod, "__name__", "")
            for attr in dir(mod):
                val = getattr(mod, attr, None)
                if not _is_candidate_cls(val):
                    continue
                if val in seen:
                    continue
                cls_mod = getattr(val, "__module__", "")
                if cls_mod == mod_name or cls_mod == "src" or cls_mod.startswith("src.") or cls_mod.startswith("app_chaos_"):
                    seen.add(val)
                    candidates.append(val)

        # 1. Check already-loaded app modules in sys.modules
        for mod_name, mod in list(sys.modules.items()):
            if mod is None:
                continue
            if mod_name == "src" or mod_name.startswith("src.") or mod_name.startswith("app_chaos_"):
                _collect_from_mod(mod)

        # 2. Scan app_dir/src/*.py
        src_dir = app_dir_resolved / "src"
        if src_dir.exists():
            if str(app_dir_resolved) not in sys.path:
                sys.path.insert(0, str(app_dir_resolved))
            for py_file in sorted(src_dir.glob("*.py")):
                if py_file.name.startswith("test_") or py_file.name == "__init__.py":
                    continue
                try:
                    mod = importlib.import_module(f"src.{py_file.stem}")
                    _collect_from_mod(mod)
                except Exception:
                    pass

        # 3. Scan top-level *.py (excluding tests/ and test_*.py)
        for py_file in sorted(app_dir_resolved.glob("*.py")):
            if py_file.name.startswith("test_") or py_file.name == "run.py":
                continue
            sub_mod_name = f"app_chaos_scan_{app_dir_resolved.name}_{py_file.stem}"
            try:
                if sub_mod_name in sys.modules:
                    mod = sys.modules[sub_mod_name]
                else:
                    spec = importlib.util.spec_from_file_location(sub_mod_name, str(py_file))
                    if not spec or not spec.loader:
                        continue
                    mod = importlib.util.module_from_spec(spec)
                    sys.modules[sub_mod_name] = mod
                    spec.loader.exec_module(mod)
                _collect_from_mod(mod)
            except Exception:
                pass

        return candidates

    def _safe_instantiate_engine(self, cls: type, temp_dir: Path) -> Optional[Any]:
        """Instantiates an engine class safely using inspect.signature."""
        try:
            sig = inspect.signature(cls.__init__)
        except (ValueError, TypeError):
            try:
                return cls()
            except Exception:
                return None

        kwargs: Dict[str, Any] = {}
        known_overrides: Dict[str, Any] = {
            "data_dir": Path(temp_dir),
            "storage_dir": Path(temp_dir),
            "wal_dir": Path(temp_dir),
            "wal_path": Path(temp_dir) / "chaos.wal",
            "db_path": Path(temp_dir) / "chaos.wal",
            "log_path": Path(temp_dir) / "chaos.wal",
            "wal_filename": "chaos.wal",
            "ttl_sweep_interval": 1.0,
            "enable_background_sweeper": False,
            "node_id": "chaos_node_1",
            "peers": [],
        }

        for p_name, p in sig.parameters.items():
            if p_name == "self" or p.kind in (
                inspect.Parameter.VAR_POSITIONAL,
                inspect.Parameter.VAR_KEYWORD,
            ):
                continue

            if p_name in known_overrides:
                kwargs[p_name] = known_overrides[p_name]
                continue

            if p.default is not inspect.Parameter.empty:
                continue

            # Required parameter without default: synthesize safe typed value
            ann = p.annotation
            ann_str = str(ann).lower() if ann is not inspect.Parameter.empty else ""
            if ann is Path or "path" in ann_str or "dir" in p_name.lower():
                kwargs[p_name] = Path(temp_dir)
            elif ann is bool or "bool" in ann_str:
                kwargs[p_name] = False
            elif ann is int or ann_str == "int":
                kwargs[p_name] = 1
            elif ann is float or ann_str == "float":
                kwargs[p_name] = 1.0
            elif ann is list or "list" in ann_str:
                kwargs[p_name] = []
            elif ann is dict or "dict" in ann_str:
                kwargs[p_name] = {}
            else:
                kwargs[p_name] = "chaos"

        try:
            return cls(**kwargs)
        except Exception:
            try:
                return cls()
            except Exception:
                return None

    def _prepare_server_context(
        self,
        app_dir: Path,
        handler_cls: type,
    ) -> Tuple[_MockHTTPServer, Optional[Callable[[], None]]]:
        """Discovers or instantiates the application's engine and prepares a mock server context."""
        temp_dir = _make_scratch_temp_dir(prefix="chaos_eval_")

        def cleanup() -> None:
            if temp_dir.exists():
                shutil.rmtree(temp_dir, ignore_errors=True)

        candidates = self._discover_engine_candidates(app_dir)
        engine_instance: Any = None
        for cls in candidates:
            engine_instance = self._safe_instantiate_engine(cls, temp_dir)
            if engine_instance is not None:
                break

        if engine_instance is None:
            engine_instance = _MockDefaultEngine()

        server_instance = _MockHTTPServer(engine=engine_instance)
        for alias in self._SERVER_ALIASES:
            try:
                existing = inspect.getattr_static(handler_cls, alias, None)
                if existing is None:
                    setattr(handler_cls, alias, engine_instance)
            except Exception:
                pass

        return server_instance, cleanup

    def _dispatch_probe(
        self,
        handler_cls: type,
        method: str,
        path: str,
        body: Any,
        server: Any = None,
    ) -> Tuple[int, str]:
        """Dispatches an HTTP request probe through the handler."""
        if isinstance(body, dict):
            payload_bytes = json.dumps(body).encode("utf-8")
        elif isinstance(body, str):
            payload_bytes = body.encode("utf-8")
        elif isinstance(body, bytes):
            payload_bytes = body
        else:
            payload_bytes = b""

        content_len = len(payload_bytes)
        req_lines = [
            f"{method} {path} HTTP/1.1",
            "Host: localhost",
            f"Content-Length: {content_len}",
            "Content-Type: application/json",
            "",
            "",
        ]
        headers_raw = "\r\n".join(req_lines).encode("utf-8")
        request_raw = headers_raw + payload_bytes

        sock = _MockRequestSocket(request_raw)
        try:
            handler_cls(sock, ("127.0.0.1", 8088), server)
            resp_bytes = sock.get_response()
            if not resp_bytes:
                return 0, "Empty response"

            first_line = resp_bytes.splitlines()[0].decode("utf-8", errors="replace")
            parts = first_line.split()
            if len(parts) >= 2 and parts[1].isdigit():
                status_code = int(parts[1])
                return status_code, ""
            return 200, ""
        except Exception as ex:
            return 500, f"Unhandled exception: {type(ex).__name__} ({str(ex)})"

    def _evaluate_subprocess_chaos(
        self,
        app_dir: Path,
        entrypoint: Path,
        archetype: BenchmarkArchetype,
    ) -> EvaluationPassResult:
        """Executes subprocess, CLI, stdin fuzzing, socketpair framing, and SIGTERM restartability chaos probes."""
        env = {
            **os.environ,
            "PYTHONUNBUFFERED": "1",
            "PYTHONPATH": str(app_dir),
        }
        try:
            entrypoint_src = entrypoint.read_text(encoding="utf-8", errors="replace")
        except Exception:
            entrypoint_src = ""

        total_probes = 0
        graceful_responses = 0
        unhandled_crashes = 0
        details_log: List[str] = []

        def _has_traceback(stderr_text: str) -> bool:
            return "Traceback (most recent call last):" in (stderr_text or "")

        # Probe 1: smoke_stability
        total_probes += 1
        try:
            p1 = subprocess.run(
                [sys.executable, "-u", str(entrypoint), "--smoke-test"],
                stdin=subprocess.DEVNULL,
                capture_output=True,
                text=True,
                timeout=self.timeout_sec,
                cwd=str(app_dir),
                env=env,
            )
            if p1.returncode == 0 and "Traceback" not in (p1.stderr or ""):
                graceful_responses += 1
                details_log.append("Probe 'smoke_stability' passed (exit=0)")
            else:
                unhandled_crashes += 1
                details_log.append(f"Probe 'smoke_stability' failed (exit={p1.returncode})")
        except Exception as exc:
            unhandled_crashes += 1
            details_log.append(f"Probe 'smoke_stability' errored: {type(exc).__name__}")

        # Probe 2: malformed_cli_flags
        total_probes += 1
        try:
            p2 = subprocess.run(
                [sys.executable, "-u", str(entrypoint), "--invalid-chaos-flag-xyz", "{bad"],
                stdin=subprocess.DEVNULL,
                capture_output=True,
                text=True,
                timeout=3.0,
                cwd=str(app_dir),
                env=env,
            )
            if not _has_traceback(p2.stderr):
                graceful_responses += 1
                details_log.append(f"Probe 'malformed_cli_flags' handled cleanly (exit={p2.returncode})")
            else:
                unhandled_crashes += 1
                details_log.append("Probe 'malformed_cli_flags' emitted unhandled Traceback")
        except Exception as exc:
            unhandled_crashes += 1
            details_log.append(f"Probe 'malformed_cli_flags' crashed/hung: {type(exc).__name__}")

        # Probe 3: malformed_stdin_fuzz
        total_probes += 1
        has_port_flag = "--port" in entrypoint_src
        malformed_bytes = (
            b"{truncated_json:\n\xff\xfe\x00binary_garbage\n" + (b"A" * 4096) + b"\n"
        )
        cmd_p3 = (
            [sys.executable, "-u", str(entrypoint), "--smoke-test"]
            if has_port_flag
            else [sys.executable, "-u", str(entrypoint)]
        )
        try:
            p3 = subprocess.run(
                cmd_p3,
                input=malformed_bytes,
                capture_output=True,
                timeout=3.0,
                cwd=str(app_dir),
                env=env,
            )
            stderr_p3 = (p3.stderr or b"").decode("utf-8", errors="replace")
            if not _has_traceback(stderr_p3) and p3.returncode in (0, 1, 2):
                graceful_responses += 1
                details_log.append(f"Probe 'malformed_stdin_fuzz' survived garbage stdin (exit={p3.returncode})")
            else:
                unhandled_crashes += 1
                details_log.append(f"Probe 'malformed_stdin_fuzz' failed (exit={p3.returncode})")
        except Exception as exc:
            unhandled_crashes += 1
            details_log.append(f"Probe 'malformed_stdin_fuzz' crashed/hung: {type(exc).__name__}")

        # Probe 4: socketpair_framing_chaos (AF_UNIX kernel IPC, zero network)
        total_probes += 1
        s1: Optional[socket.socket] = None
        s2: Optional[socket.socket] = None
        temp_eval_dir = _make_scratch_temp_dir(prefix="chaos_sock_")
        try:
            s1, s2 = socket.socketpair()
            s1.settimeout(1.0)
            s2.settimeout(1.0)
            wire_payload = b"*-5\r\n$9999\r\nbad_frame\x00\xff\n"
            s1.sendall(wire_payload)
            s1.shutdown(socket.SHUT_WR)
            received = bytearray()
            while True:
                chunk = s2.recv(4096)
                if not chunk:
                    break
                received.extend(chunk)
            wire_bytes = bytes(received)

            # Exercise any discovered engine/parser framing method if present
            parser_crashed = False
            parser_methods = ("parse", "feed", "handle_line", "process_line", "handle_request", "route")
            for cls in self._discover_engine_candidates(app_dir):
                inst = self._safe_instantiate_engine(cls, temp_eval_dir)
                if inst is None:
                    continue
                for m_name in parser_methods:
                    fn = getattr(inst, m_name, None)
                    if callable(fn):
                        try:
                            sig = inspect.signature(fn)
                            params = [
                                p for p in sig.parameters.values()
                                if p.kind not in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD)
                            ]
                            if params:
                                first_ann = str(params[0].annotation).lower()
                                arg: Any = wire_bytes if "bytes" in first_ann else wire_bytes.decode("utf-8", errors="replace")
                                fn(arg)
                            else:
                                fn()
                        except Exception as parser_exc:
                            exc_name = type(parser_exc).__name__
                            if exc_name in ("AttributeError", "NameError", "UnboundLocalError", "RecursionError", "MemoryError"):
                                parser_crashed = True
                                details_log.append(f"Probe 'socketpair_framing_chaos' parser bug: {exc_name}")
                        break

            if wire_bytes == wire_payload and not parser_crashed:
                graceful_responses += 1
                details_log.append("Probe 'socketpair_framing_chaos' passed clean EOF & framing resilience")
            else:
                unhandled_crashes += 1
                if not parser_crashed:
                    details_log.append("Probe 'socketpair_framing_chaos' failed payload integrity")
        except Exception as exc:
            unhandled_crashes += 1
            details_log.append(f"Probe 'socketpair_framing_chaos' errored: {type(exc).__name__}")
        finally:
            for sock_obj in (s1, s2):
                if sock_obj is not None:
                    try:
                        sock_obj.close()
                    except Exception:
                        pass
            if temp_eval_dir.exists():
                shutil.rmtree(temp_eval_dir, ignore_errors=True)

        # Probe 5: daemon_sigterm_and_restart (if --port) OR mixed_ndjson_burst (CLI)
        total_probes += 1
        if has_port_flag:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as ephem:
                    ephem.bind(("127.0.0.1", 0))
                    free_port = ephem.getsockname()[1]

                proc = subprocess.Popen(
                    [sys.executable, "-u", str(entrypoint), "--port", str(free_port)],
                    stdin=subprocess.DEVNULL,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    cwd=str(app_dir),
                    env=env,
                )
                try:
                    streams = [s for s in (proc.stdout, proc.stderr) if s is not None]
                    if streams:
                        select.select(streams, [], [], 0.6)
                    early_rc = proc.poll()
                    if early_rc is not None and early_rc != 0:
                        _, err_bytes = proc.communicate(timeout=2.0)
                        unhandled_crashes += 1
                        details_log.append(
                            f"Probe 'daemon_sigterm_and_restart' crashed on startup (exit={early_rc}): "
                            f"{(err_bytes or b'').decode('utf-8', errors='replace')[:120]}"
                        )
                    else:
                        if early_rc is None:
                            proc.terminate()
                        _, err_bytes = proc.communicate(timeout=3.0)
                        stderr_s = (err_bytes or b"").decode("utf-8", errors="replace")
                        clean_exit = proc.returncode in (0, -15, 143, 15, -2)
                        bad_tb = _has_traceback(stderr_s) and "KeyboardInterrupt" not in stderr_s
                        if not clean_exit or bad_tb:
                            unhandled_crashes += 1
                            details_log.append(f"Probe 'daemon_sigterm_and_restart' unclean shutdown (exit={proc.returncode})")
                        else:
                            # Restartability check via --smoke-test
                            restart_p = subprocess.run(
                                [sys.executable, "-u", str(entrypoint), "--smoke-test"],
                                stdin=subprocess.DEVNULL,
                                capture_output=True,
                                text=True,
                                timeout=self.timeout_sec,
                                cwd=str(app_dir),
                                env=env,
                            )
                            if restart_p.returncode == 0 and "Traceback" not in (restart_p.stderr or ""):
                                graceful_responses += 1
                                details_log.append("Probe 'daemon_sigterm_and_restart' passed SIGTERM + clean restart")
                            else:
                                unhandled_crashes += 1
                                details_log.append(f"Probe 'daemon_sigterm_and_restart' restart failed (exit={restart_p.returncode})")
                except subprocess.TimeoutExpired:
                    proc.kill()
                    proc.communicate()
                    unhandled_crashes += 1
                    details_log.append("Probe 'daemon_sigterm_and_restart' timed out on SIGTERM")
            except Exception as exc:
                unhandled_crashes += 1
                details_log.append(f"Probe 'daemon_sigterm_and_restart' errored: {type(exc).__name__}")
        else:
            # CLI burst: 20 mixed valid + malformed NDJSON lines
            burst_lines = []
            for idx in range(20):
                if idx % 4 == 0:
                    burst_lines.append(json.dumps({"timestamp": 1700000000 + idx, "latency_ms": 12.5 + idx}))
                elif idx % 4 == 1:
                    burst_lines.append("{corrupted_ndjson_" + str(idx))
                elif idx % 4 == 2:
                    burst_lines.append("")
                else:
                    burst_lines.append('{"timestamp": 1700000000, "msg": "héllo\\u0000world"}')
            burst_input = ("\n".join(burst_lines) + "\n").encode("utf-8")
            try:
                p_burst = subprocess.run(
                    [sys.executable, "-u", str(entrypoint)],
                    input=burst_input,
                    capture_output=True,
                    timeout=3.0,
                    cwd=str(app_dir),
                    env=env,
                )
                stderr_b = (p_burst.stderr or b"").decode("utf-8", errors="replace")
                if p_burst.returncode == 0 and not _has_traceback(stderr_b):
                    graceful_responses += 1
                    details_log.append("Probe 'mixed_ndjson_burst' survived 20-line mixed burst (exit=0)")
                else:
                    unhandled_crashes += 1
                    details_log.append(f"Probe 'mixed_ndjson_burst' failed (exit={p_burst.returncode})")
            except Exception as exc:
                unhandled_crashes += 1
                details_log.append(f"Probe 'mixed_ndjson_burst' errored: {type(exc).__name__}")

        raw_score = round((graceful_responses / total_probes) * 100.0, 2) if total_probes > 0 else 100.0
        weighted_score = round(raw_score * self.weight, 2)
        return EvaluationPassResult(
            pass_name="chaos",
            weight=self.weight,
            raw_score=raw_score,
            weighted_score=weighted_score,
            details={
                "chaos_mode": "subprocess_and_socketpair",
                "total_probes": total_probes,
                "graceful_responses": graceful_responses,
                "unhandled_crashes": unhandled_crashes,
                "log": details_log[:15],
            },
            passed=(raw_score >= 70.0),
        )
