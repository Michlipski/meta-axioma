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
import signal
import socket
import subprocess
import sys
import time
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
        "Parser",
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
        "parse_resp",
        "parse_ndjson",
        "process_line",
        "handle_command",
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

            # 3. Domain-Aware HTTP Protocol & Behavioral Chaos Probes (Zero Free Passes)
            if archetype.id != "test_payload_arch":
                post_path = self._pick_post_endpoint(archetype)

                # 3a. Oversized Content-Length (>1 MiB -> must return 413 or 400, never 200/500/hang)
                total_probes += 1
                oversized_raw = (
                    f"POST {post_path} HTTP/1.1\r\n"
                    f"Host: axioma-probe\r\n"
                    f"Content-Type: application/json\r\n"
                    f"Content-Length: 2097152\r\n"
                    f"Connection: close\r\n\r\n"
                    f"{{}}"
                ).encode("utf-8")
                ov_status, ov_err = self._dispatch_raw_http_probe(
                    handler_cls, oversized_raw, server=server_instance
                )
                if ov_err or ov_status not in (400, 413, 422):
                    unhandled_crashes += 1
                    details_log.append(
                        f"Probe 'http_oversized_content_length' failed: status={ov_status}, err={ov_err or 'expected 413/400'}"
                    )
                else:
                    graceful_responses += 1
                    details_log.append(f"Probe 'http_oversized_content_length' rejected cleanly (HTTP {ov_status})")

                # 3b. Truncated body / Content-Length mismatch (must return 400, never accept 200 or crash 500)
                total_probes += 1
                if "raft" in archetype.id.lower():
                    short_json = json.dumps({
                        "term": 1,
                        "candidate_id": "c1",
                        "last_log_index": 0,
                        "last_log_term": 0,
                    }).encode("utf-8")
                    trunc_path = "/vote"
                elif "kv" in archetype.id.lower():
                    short_json = json.dumps({"value": "truncated_probe"}).encode("utf-8")
                    trunc_path = "/keys/trunc_probe"
                else:
                    short_json = json.dumps({"probe": "truncated"}).encode("utf-8")
                    trunc_path = post_path
                truncated_raw = (
                    f"POST {trunc_path} HTTP/1.1\r\n"
                    f"Host: axioma-probe\r\n"
                    f"Content-Type: application/json\r\n"
                    f"Content-Length: {len(short_json) + 128}\r\n"
                    f"Connection: close\r\n\r\n"
                ).encode("utf-8") + short_json
                tr_status, tr_err = self._dispatch_raw_http_probe(
                    handler_cls, truncated_raw, server=server_instance
                )
                if tr_err or tr_status not in (400, 411, 422):
                    unhandled_crashes += 1
                    details_log.append(
                        f"Probe 'http_truncated_body_mismatch' failed: status={tr_status}, err={tr_err or 'accepted truncated body'}"
                    )
                else:
                    graceful_responses += 1
                    details_log.append(f"Probe 'http_truncated_body_mismatch' rejected cleanly (HTTP {tr_status})")

                # 3c. bool-as-int coercion + malformed JSON probe
                total_probes += 1
                if "kv" in archetype.id.lower():
                    bool_path = "/keys/bool_ttl_probe"
                    bool_body: Any = {"value": "v", "ttl_seconds": True}
                    must_reject_bool = True
                elif "raft" in archetype.id.lower():
                    bool_path = "/vote"
                    bool_body = {"term": True, "candidate_id": "c1", "last_log_index": 0, "last_log_term": 0}
                    must_reject_bool = True
                else:
                    bool_path = post_path
                    bool_body = {"value": "v", "ttl_seconds": True}
                    must_reject_bool = False
                b_status, b_err = self._dispatch_probe(
                    handler_cls, "POST", bool_path, bool_body, server=server_instance
                )
                m_status, m_err = self._dispatch_probe(
                    handler_cls, "POST", bool_path, '{"broken": [1, 2', server=server_instance
                )
                bool_ok = (not b_err) and (b_status in (400, 422) if must_reject_bool else b_status != 500)
                malformed_ok = (not m_err) and (m_status in (400, 422))
                if bool_ok and malformed_ok:
                    graceful_responses += 1
                    details_log.append(
                        f"Probe 'http_bool_as_int_and_malformed' rejected cleanly (HTTP {b_status}/{m_status})"
                    )
                else:
                    unhandled_crashes += 1
                    details_log.append(
                        f"Probe 'http_bool_as_int_and_malformed' failed (bool={b_status}/{b_err}, malformed={m_status}/{m_err})"
                    )

                # 3d. Domain-specific KV WAL torn-line re-append & tx_id=None isolation probe
                if "kv" in archetype.id.lower():
                    kv_ok, kv_msg = self._run_kv_wal_and_tx_isolation_probe(app_dir)
                    if kv_ok is not None:
                        total_probes += 1
                        if kv_ok:
                            graceful_responses += 1
                            details_log.append(kv_msg)
                        else:
                            unhandled_crashes += 1
                            details_log.append(kv_msg)

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
                    "log": details_log[:20],
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

        return self._dispatch_raw_http_probe(handler_cls, request_raw, server=server)

    @staticmethod
    def _pick_post_endpoint(archetype: BenchmarkArchetype) -> str:
        """Selects a concrete POST endpoint path from archetype.expected_endpoints."""
        for ep in archetype.expected_endpoints or []:
            parts = ep.strip().split()
            if len(parts) >= 2 and parts[0].upper() == "POST":
                path = parts[1]
                if "{" in path:
                    path = path.split("{")[0] + "probe_key"
                return path
        return "/keys/probe_key"

    def _dispatch_raw_http_probe(
        self,
        handler_cls: type,
        request_raw: bytes,
        server: Any = None,
    ) -> Tuple[int, str]:
        """Dispatches raw HTTP/1.1 bytes through the handler without mutating headers."""
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

    def _run_kv_wal_and_tx_isolation_probe(self, app_dir: Path) -> Tuple[Optional[bool], str]:
        """Domain chaos probe for KV engines: torn trailing WAL re-append durability & tx_id=None isolation."""
        candidates = self._discover_engine_candidates(app_dir)
        kv_cls = None
        for cls in candidates:
            if all(callable(getattr(cls, m, None)) for m in ("set", "get", "begin_transaction", "rollback_transaction")):
                # Only probe engines that accept data_dir/storage_dir/wal_dir persistence
                try:
                    sig = inspect.signature(cls.__init__)
                    if any(p in sig.parameters for p in ("data_dir", "storage_dir", "wal_dir", "wal_path")):
                        kv_cls = cls
                        break
                except Exception:
                    continue
        if kv_cls is None:
            return None, ""

        temp_dir = _make_scratch_temp_dir(prefix="chaos_kv_")
        issues: List[str] = []
        try:
            # Check A: Torn trailing WAL line must be repaired/truncated before subsequent append
            eng1 = self._safe_instantiate_engine(kv_cls, temp_dir)
            if eng1 is None:
                return None, ""
            eng1.set("seed_k", "seed_v")
            wal_files = [p for p in temp_dir.rglob("*") if p.is_file() and ("wal" in p.name.lower() or p.suffix in (".jsonl", ".log", ".wal"))]
            if wal_files:
                wal_file = wal_files[0]
                with wal_file.open("a", encoding="utf-8") as fh:
                    fh.write('{"seq":999,"tx_id":"torn","op":"SET","key":"broken"')
                try:
                    eng2 = self._safe_instantiate_engine(kv_cls, temp_dir)
                    if eng2 is None:
                        issues.append("reopen after torn WAL failed")
                    else:
                        eng2.set("after_torn", "ok_v")
                        eng3 = self._safe_instantiate_engine(kv_cls, temp_dir)
                        if eng3 is None or eng3.get("after_torn") != "ok_v":
                            issues.append("post-torn WAL append corrupted persistence")
                except Exception as exc:
                    issues.append(f"post-torn WAL append raised {type(exc).__name__}: {exc}")

            # Check B: Concurrent non-tx write (tx_id=None) during active tx must not be absorbed & rolled back
            tx_dir = temp_dir / "tx_iso"
            tx_dir.mkdir(parents=True, exist_ok=True)
            eng_tx = self._safe_instantiate_engine(kv_cls, tx_dir)
            if eng_tx is not None:
                try:
                    set_sig = inspect.signature(eng_tx.set)
                    if "tx_id" in set_sig.parameters:
                        eng_tx.begin_transaction()
                        eng_tx.set("non_tx_isolated_key", "must_persist")
                        eng_tx.rollback_transaction()
                        if eng_tx.get("non_tx_isolated_key") != "must_persist":
                            issues.append("non-tx write (tx_id=None) was absorbed and rolled back by active transaction")
                except Exception:
                    pass

            if issues:
                return False, f"Probe 'kv_wal_torn_and_tx_isolation' failed: {'; '.join(issues)}"
            return True, "Probe 'kv_wal_torn_and_tx_isolation' passed WAL torn-line repair & tx isolation"
        finally:
            if temp_dir.exists():
                shutil.rmtree(temp_dir, ignore_errors=True)

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

            # Exercise any discovered engine/parser framing method (ZERO free loopback-echo pass)
            parser_crashed = False
            framing_exercised = False
            parser_methods = (
                "parse_resp",
                "parse_ndjson",
                "process_line",
                "handle_command",
                "parse",
                "feed",
                "handle_line",
                "handle_request",
                "route",
            )
            for cls in self._discover_engine_candidates(app_dir):
                inst = self._safe_instantiate_engine(cls, temp_eval_dir)
                if inst is None:
                    continue
                for m_name in parser_methods:
                    fn = getattr(inst, m_name, None)
                    if callable(fn):
                        framing_exercised = True
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
                            if exc_name in (
                                "AttributeError",
                                "NameError",
                                "UnboundLocalError",
                                "RecursionError",
                                "MemoryError",
                                "OverflowError",
                            ):
                                parser_crashed = True
                                details_log.append(f"Probe 'socketpair_framing_chaos' parser bug: {exc_name}")
                        break

            if wire_bytes == wire_payload and framing_exercised and not parser_crashed:
                graceful_responses += 1
                details_log.append("Probe 'socketpair_framing_chaos' passed framing resilience against real parser")
            else:
                unhandled_crashes += 1
                if not framing_exercised:
                    details_log.append(
                        "Probe 'socketpair_framing_chaos' failed: no framing/parser method exercised (echo free pass removed)"
                    )
                elif not parser_crashed:
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

        # Domain-Aware Adversarial Probes (CLI/NDJSON and RESP2)
        arch_id_lower = (getattr(archetype, "id", "") or "").lower()
        arch_spec = getattr(archetype, "specification", None) or {}
        is_cli_ndjson = (
            "micro" in arch_id_lower
            or str(arch_spec.get("execution_mode", "")).upper() == "STREAMING_STDIN_CLI"
        )
        is_resp2 = (
            "resp" in arch_id_lower
            or str(arch_spec.get("protocol_version", "")).upper() == "RESP2"
        )

        if is_cli_ndjson:
            # Probe 6: NDJSON numeric overflow (10**400 float overflow + 10**5000 int-str-digits DoS)
            total_probes += 1
            huge_400 = "1" + ("0" * 400)
            huge_5000 = "9" * 5000
            overflow_payload = (
                f'{{"latency_ms": {huge_400}}}\n'
                f'{{"latency_ms": {huge_5000}}}\n'
                f'{{"latency_ms": 12.5}}\n'
            ).encode("utf-8")
            try:
                p_ov = subprocess.run(
                    [sys.executable, "-u", str(entrypoint)],
                    input=overflow_payload,
                    capture_output=True,
                    timeout=3.0,
                    cwd=str(app_dir),
                    env=env,
                )
                stderr_ov = (p_ov.stderr or b"").decode("utf-8", errors="replace")
                if p_ov.returncode == 0 and not _has_traceback(stderr_ov) and "OverflowError" not in stderr_ov:
                    graceful_responses += 1
                    details_log.append("Probe 'ndjson_numeric_overflow' survived 10**400 & 10**5000 cleanly (exit=0)")
                else:
                    unhandled_crashes += 1
                    details_log.append(
                        f"Probe 'ndjson_numeric_overflow' crashed (exit={p_ov.returncode}): {stderr_ov.strip()[-140:]}"
                    )
            except Exception as exc:
                unhandled_crashes += 1
                details_log.append(f"Probe 'ndjson_numeric_overflow' errored: {type(exc).__name__}")

            # Probe 7: Open-stdin SIGINT (PEP 475) — must exit cleanly & emit summary without hanging
            total_probes += 1
            sig_proc: Optional[subprocess.Popen[bytes]] = None
            try:
                sig_proc = subprocess.Popen(
                    [sys.executable, "-u", str(entrypoint)],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    cwd=str(app_dir),
                    env=env,
                )
                assert sig_proc.stdin is not None
                sig_proc.stdin.write(b'{"latency_ms": 15.0}\n')
                sig_proc.stdin.flush()
                time.sleep(0.25)
                # Send SIGINT while stdin remains OPEN (exposes PEP 475 read() retry hang)
                sig_proc.send_signal(signal.SIGINT)
                try:
                    sig_proc.wait(timeout=2.0)
                    out_b = sig_proc.stdout.read() if sig_proc.stdout else b""
                    err_b = sig_proc.stderr.read() if sig_proc.stderr else b""
                    out_s = out_b.decode("utf-8", errors="replace")
                    err_s = err_b.decode("utf-8", errors="replace")
                    if (
                        sig_proc.returncode in (0, -2, 130)
                        and not _has_traceback(err_s)
                        and "{" in out_s
                        and "}" in out_s
                    ):
                        graceful_responses += 1
                        details_log.append("Probe 'open_stdin_sigint_pep475' exited cleanly and emitted summary")
                    else:
                        unhandled_crashes += 1
                        details_log.append(
                            f"Probe 'open_stdin_sigint_pep475' failed (exit={sig_proc.returncode}, has_json={'{' in out_s})"
                        )
                except subprocess.TimeoutExpired:
                    sig_proc.terminate()
                    try:
                        sig_proc.wait(timeout=1.0)
                    except subprocess.TimeoutExpired:
                        sig_proc.kill()
                        sig_proc.wait(timeout=1.0)
                    unhandled_crashes += 1
                    details_log.append("Probe 'open_stdin_sigint_pep475' hung >2.0s on open stdin (PEP 475 SIGINT bug)")
            except Exception as exc:
                unhandled_crashes += 1
                details_log.append(f"Probe 'open_stdin_sigint_pep475' errored: {type(exc).__name__}")
            finally:
                if sig_proc is not None:
                    for stream in (sig_proc.stdin, sig_proc.stdout, sig_proc.stderr):
                        if stream is not None:
                            try:
                                stream.close()
                            except Exception:
                                pass

        if is_resp2:
            resp_results = self._run_resp2_adversarial_probes(app_dir)
            for ok, msg in resp_results:
                total_probes += 1
                if ok:
                    graceful_responses += 1
                else:
                    unhandled_crashes += 1
                details_log.append(msg)

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
                "log": details_log[:20],
            },
            passed=(raw_score >= 70.0),
        )

    def _run_resp2_adversarial_probes(self, app_dir: Path) -> List[Tuple[bool, str]]:
        """Executes RESP2 wire-protocol adversarial probes: nested arrays, CRLF injection, oversized INCR."""
        temp_dir = _make_scratch_temp_dir(prefix="chaos_resp_")
        results: List[Tuple[bool, str]] = []
        try:
            resp_engine = None
            for cls in self._discover_engine_candidates(app_dir):
                if all(callable(getattr(cls, m, None)) for m in ("parse_resp", "handle_command", "serialize_resp")):
                    inst = self._safe_instantiate_engine(cls, temp_dir)
                    if inst is not None:
                        resp_engine = inst
                        break

            if resp_engine is None:
                return [
                    (False, "Probe 'resp2_nested_array' failed: no RESP2 engine with parse_resp/handle_command/serialize_resp"),
                    (False, "Probe 'resp2_crlf_error_injection' failed: no RESP2 engine discovered"),
                    (False, "Probe 'resp2_incr_bounds_and_4300_digits' failed: no RESP2 engine discovered"),
                ]

            def _exec_frame(raw_frame: bytes) -> Tuple[Optional[bytes], Optional[str]]:
                try:
                    parsed = resp_engine.parse_resp(raw_frame)
                    msg = parsed[0] if isinstance(parsed, tuple) else parsed
                    if msg is None:
                        return None, "Incomplete frame returned None"
                    reply = resp_engine.handle_command(msg)
                    wire = resp_engine.serialize_resp(reply)
                    return (wire if isinstance(wire, bytes) else bytes(wire)), None
                except Exception as exc:
                    return None, f"{type(exc).__name__}: {exc}"

            # Probe A: Nested array (*1\r\n*0\r\n) must return -ERR, never uncaught exception
            nested_wire, nested_err = _exec_frame(b"*1\r\n*0\r\n")
            if nested_err is None and nested_wire is not None and nested_wire.startswith(b"-"):
                results.append((True, "Probe 'resp2_nested_array' returned graceful -ERR"))
            else:
                results.append((
                    False,
                    f"Probe 'resp2_nested_array' failed: err={nested_err or 'non-error reply'} wire={nested_wire!r}",
                ))

            # Probe B: CRLF command-name wire injection (*1\r\n$10\r\nBAD\r\n+PONG\r\n)
            crlf_wire, crlf_err = _exec_frame(b"*1\r\n$10\r\nBAD\r\n+PONG\r\n")
            if (
                crlf_err is None
                and crlf_wire is not None
                and crlf_wire.startswith(b"-")
                and b"\r\n+PONG" not in crlf_wire
                and crlf_wire.count(b"\r\n") == 1
            ):
                results.append((True, "Probe 'resp2_crlf_error_injection' sanitized CRLF cleanly"))
            else:
                results.append((
                    False,
                    f"Probe 'resp2_crlf_error_injection' vulnerable to CRLF wire injection: wire={crlf_wire!r} err={crlf_err}",
                ))

            # Probe C: 64-bit signed INCR overflow (2**63 - 1) & 4,500-digit INCR DoS
            def _make_cmd(*parts: bytes) -> bytes:
                chunks = [f"*{len(parts)}\r\n".encode("ascii")]
                for p in parts:
                    chunks.append(f"${len(p)}\r\n".encode("ascii") + p + b"\r\n")
                return b"".join(chunks)

            incr_issues: List[str] = []
            max_i64 = str((1 << 63) - 1).encode("ascii")
            _exec_frame(_make_cmd(b"SET", b"k_max64", max_i64))
            ov_wire, ov_err = _exec_frame(_make_cmd(b"INCR", b"k_max64"))
            if ov_err is not None or ov_wire is None or not ov_wire.startswith(b"-"):
                incr_issues.append(f"64-bit overflow accepted/crashed (wire={ov_wire!r}, err={ov_err})")

            huge_digits = b"9" * 4500
            _exec_frame(_make_cmd(b"SET", b"k_4500", huge_digits))
            big_wire, big_err = _exec_frame(_make_cmd(b"INCR", b"k_4500"))
            if big_err is not None or big_wire is None or not big_wire.startswith(b"-"):
                incr_issues.append(f"4500-digit INCR accepted/crashed (wire={big_wire!r}, err={big_err})")

            if not incr_issues:
                results.append((True, "Probe 'resp2_incr_bounds_and_4300_digits' enforced 64-bit bounds cleanly"))
            else:
                results.append((False, f"Probe 'resp2_incr_bounds_and_4300_digits' failed: {'; '.join(incr_issues)}"))
            return results
        finally:
            if temp_dir.exists():
                shutil.rmtree(temp_dir, ignore_errors=True)
