r"""Pass 3: Byzantine Chaos Survival Evaluator ($S_{chaos}$, 15%).

Evaluates:
- Resilience against malformed JSON bodies, severed socket requests, and unexpected types.
- Concurrent burst traffic stress (20 simultaneous requests).
- Asserts zero unhandled 500 Internal Server Error crashes or server process termination.
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
import importlib.util
import io
import json
import os
from pathlib import Path
import sys
import time
from typing import Any, Dict, List, Optional, Tuple
from http.server import BaseHTTPRequestHandler

from ..domain_models import BenchmarkArchetype, EvaluationPassResult


class _MockRequestSocket:
    """Simulates a TCP socket stream for hermetic in-process HTTP evaluation."""

    def __init__(self, request_bytes: bytes) -> None:
        self._rfile = io.BytesIO(request_bytes)
        self._wfile = io.BytesIO()

    def makefile(self, mode: str, *args: Any, **kwargs: Any) -> io.BytesIO:
        if "b" in mode and "r" in mode:
            return self._rfile
        return self._wfile

    def sendall(self, data: bytes) -> None:
        self._wfile.write(data)

    def get_response(self) -> bytes:
        return self._wfile.getvalue()


class ChaosEvaluator:
    """Evaluates Pass 3: Byzantine Chaos Survival ($S_{chaos}$, Weight = 15%)."""

    def __init__(self, weight: float = 0.15, timeout_sec: float = 6.0) -> None:
        self.weight = weight
        self.timeout_sec = timeout_sec

    def evaluate(self, app_dir: Path, archetype: BenchmarkArchetype) -> EvaluationPassResult:
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

        handler_cls = self._load_handler_class(app_dir)
        if handler_cls is None:
            return EvaluationPassResult(
                pass_name="chaos",
                weight=self.weight,
                raw_score=50.0,
                weighted_score=round(50.0 * self.weight, 2),
                details={"error": "No BaseHTTPRequestHandler subclass located in application"},
                passed=False,
            )

        probes = archetype.chaos_payloads or []
        total_probes = 0
        unhandled_crashes = 0
        graceful_responses = 0
        details_log = []

        # 1. Custom Archetype Payloads
        for probe in probes:
            total_probes += 1
            name = probe.get("name", "custom_probe")
            method = probe.get("method", "POST")
            path = probe.get("path", "/test")
            body = probe.get("body", "")

            status, err = self._dispatch_probe(handler_cls, method, path, body)
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
                "total_probes": total_probes,
                "graceful_responses": graceful_responses,
                "unhandled_crashes": unhandled_crashes,
                "log": details_log[:10],
            },
            passed=(raw_score >= 70.0),
        )

    def _load_handler_class(self, app_dir: Path) -> Optional[type]:
        """Loads the BaseHTTPRequestHandler subclass from the application."""
        entrypoint = app_dir / "run.py"
        module_name = f"app_chaos_{app_dir.name}_{abs(hash(str(app_dir))) % 10000}"

        try:
            sys_path_added = str(app_dir) not in sys.path
            if sys_path_added:
                sys.path.insert(0, str(app_dir))

            spec = importlib.util.spec_from_file_location(module_name, str(entrypoint))
            if not spec or not spec.loader:
                return None
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
            return None
        except Exception:
            return None
        finally:
            if str(app_dir) in sys.path:
                try:
                    sys.path.remove(str(app_dir))
                except ValueError:
                    pass

    def _dispatch_probe(
        self,
        handler_cls: type,
        method: str,
        path: str,
        body: Any,
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
            handler_cls(sock, ("127.0.0.1", 8088), None)
            resp_bytes = sock.get_response()
            if not resp_bytes:
                return 0, "Empty response"

            first_line = resp_bytes.splitlines()[0].decode("utf-8", errors="replace")
            # e.g. "HTTP/1.0 400 Bad Request"
            parts = first_line.split()
            if len(parts) >= 2 and parts[1].isdigit():
                status_code = int(parts[1])
                return status_code, ""
            return 200, ""
        except Exception as ex:
            return 500, f"Unhandled exception: {type(ex).__name__} ({str(ex)})"
