#!/usr/bin/env python3
"""
Zero-Trust AsyncIO & HTTP Server for Axioma Evolution Dashboard (Root Level, Port 8105).
Provides REST endpoints and static file serving for:
- 8-stage evolution spine
- Top-level project philosophy
- Generation 4b Sovereign Service Mesh
- Interactive sample app compilation simulation (axioma_go)
- Live side-by-side generational diff engine
- User feedback logging & telemetry
"""

from __future__ import annotations

import argparse
import asyncio
import json
import mimetypes
import sys
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, unquote, urlparse

APP_ROOT = Path(__file__).resolve().parent
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

from src.data_store import EvolutionDataStore  # noqa: E402

STATIC_DIR = APP_ROOT / "static"
DASHBOARD_FILE = APP_ROOT / "dashboard.html"


def process_http_request(
    method: str,
    raw_path: str,
    headers: dict[str, str],
    body_bytes: bytes,
    store: EvolutionDataStore,
) -> tuple[int, dict[str, str], bytes]:
    """Pure functional request processor mapping wire HTTP requests to status, headers, and body."""
    parsed = urlparse(raw_path)
    path = unquote(parsed.path)
    query_params = parse_qs(parsed.query)

    def make_json(data: Any, status: int = 200) -> tuple[int, dict[str, str], bytes]:
        payload = json.dumps(data, indent=2, ensure_ascii=False).encode("utf-8")
        resp_headers = {
            "Content-Type": "application/json; charset=utf-8",
            "Content-Length": str(len(payload)),
            "Cache-Control": "no-store, no-cache, must-revalidate",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Requested-With",
        }
        return status, resp_headers, payload

    def make_file(file_path: Path) -> tuple[int, dict[str, str], bytes]:
        if not file_path.is_file():
            return make_json({"error": "File not found", "path": str(file_path)}, status=404)
        mime, _ = mimetypes.guess_type(str(file_path))
        raw = file_path.read_bytes()
        resp_headers = {
            "Content-Type": (mime or "text/plain") + ("; charset=utf-8" if (mime or "").startswith("text/") else ""),
            "Content-Length": str(len(raw)),
            "Cache-Control": "no-cache",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Requested-With",
        }
        return 200, resp_headers, raw

    # Handle CORS preflight
    if method == "OPTIONS":
        return 204, {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Requested-With",
            "Access-Control-Max-Age": "86400",
            "Content-Length": "0",
        }, b""

    # Static routes: Root & Dashboard
    if method == "GET" and path in {"/", "/index.html", "/dashboard"}:
        index_file = STATIC_DIR / "index.html"
        if index_file.is_file():
            return make_file(index_file)
        if DASHBOARD_FILE.is_file():
            return make_file(DASHBOARD_FILE)
        return make_json({"status": "ok", "message": "Axioma Evolution Dashboard Ready", "path": "/"}, status=200)

    # API: Health
    if method == "GET" and path in {"/api/health", "/health"}:
        return make_json(store.get_health())

    # API: Zenith Architecture
    if method == "GET" and path in {"/api/zenith", "/api/zenith_architecture"}:
        return make_json(store.get_zenith())

    # API: Philosophy
    if method == "GET" and path in {"/api/philosophy", "/api/philosophy_data"}:
        return make_json(store.get_philosophy())

    # API: Generation 4b Architecture
    if method == "GET" and path in {"/api/g4b", "/api/g4b_architecture"}:
        return make_json(store.get_g4b_architecture())

    # API: Simulations Catalog & Specific App Simulation
    if method == "GET" and path in {"/api/simulations", "/api/simulation"}:
        return make_json(store.get_simulations())

    if method == "GET" and path.startswith("/api/simulations/"):
        app_id = path[len("/api/simulations/"):].strip()
        sim = store.get_simulation(app_id)
        if sim:
            return make_json(sim)
        return make_json({"error": f"Simulation not found for app '{app_id}'"}, status=404)

    # API: Generational Diff Engine (Option 3)
    if method == "GET" and path in {"/api/diff", "/api/generational_diff"}:
        stage_a = (query_params.get("a") or query_params.get("stage_a") or query_params.get("from") or ["s0"])[0]
        stage_b = (query_params.get("b") or query_params.get("stage_b") or query_params.get("to") or ["g4b"])[0]
        diff_result = store.get_generational_diff(stage_a, stage_b)
        return make_json(diff_result)

    # API: Stages
    if method == "GET" and path in {"/api/stages", "/api/stages/"}:
        return make_json(store.get_stages())

    if method == "GET" and path.startswith("/api/stages/"):
        st_id = path[len("/api/stages/"):].strip()
        stage = store.get_stage(st_id)
        if stage:
            return make_json(stage)
        return make_json({"error": f"Stage not found: '{st_id}'"}, status=404)

    # API: Transformations
    if method == "GET" and path in {"/api/transformations", "/api/transformations/"}:
        return make_json(store.get_transformations())

    if method == "GET" and path.startswith("/api/transformations/"):
        tr_id = path[len("/api/transformations/"):].strip()
        tr = store.get_transformation(tr_id)
        if tr:
            return make_json(tr)
        return make_json({"error": f"Transformation not found: '{tr_id}'"}, status=404)

    # API: Components / Subsystems
    if method == "GET" and path in {"/api/components", "/api/components/", "/api/subsystems"}:
        return make_json(store.get_components())

    if method == "GET" and (path.startswith("/api/components/") or path.startswith("/api/subsystems/")):
        prefix = "/api/components/" if path.startswith("/api/components/") else "/api/subsystems/"
        sub_id = path[len(prefix):].strip()
        comp = store.get_component(sub_id)
        if comp:
            return make_json(comp)
        return make_json({"error": f"Component lineage not found: '{sub_id}'"}, status=404)

    # API: Landauer Thermodynamic Calculation [L1-008]
    if method == "GET" and path in {"/api/landauer", "/api/landauer_heat"}:
        try:
            bits_param = query_params.get("bits", ["0"])[0]
            temp_param = query_params.get("temp", ["300.0"])[0]
            bits = float(bits_param)
            temp = float(temp_param)
            heat = store.calculate_landauer_heat(bits, temp)
            return make_json({
                "bits": bits,
                "temp_k": temp,
                "joules": heat,
                "joules_exp": f"{heat:.4e} J",
                "formula": "Q = bits * k_B * T * ln(2)",
                "invariant": "[L1-008]",
            })
        except ValueError as e:
            return make_json({"error": f"Invalid Landauer parameter: {e}"}, status=400)

    # API: Feedback (GET / POST)
    if path == "/api/feedback":
        if method == "GET":
            return make_json(store.get_feedback())
        if method == "POST":
            try:
                if not body_bytes or not body_bytes.strip():
                    return make_json({"error": "Empty feedback payload"}, status=400)
                entry = json.loads(body_bytes.decode("utf-8"))
                saved = store.add_feedback(entry)
                return make_json({"status": "created", "entry": saved}, status=201)
            except Exception as e:
                return make_json({"error": f"Invalid feedback payload: {e}"}, status=400)

    # Static assets: css, js, json, svg
    rel_path = path.lstrip("/")
    candidate_static = STATIC_DIR / rel_path
    if candidate_static.is_file() and not rel_path.startswith(".."):
        return make_file(candidate_static)

    candidate_root = APP_ROOT / rel_path
    if candidate_root.is_file() and rel_path.endswith((".html", ".json", ".js", ".css", ".svg", ".png")):
        return make_file(candidate_root)

    return make_json({"error": "Endpoint not found", "path": path}, status=404)


class EvolutionHTTPHandler(BaseHTTPRequestHandler):
    """Standard HTTP request handler delegating to process_http_request."""

    store: EvolutionDataStore

    def do_OPTIONS(self) -> None:
        status, headers, body = process_http_request("OPTIONS", self.path, dict(self.headers), b"", self.store)
        self.send_response(status)
        for k, v in headers.items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        status, headers, body = process_http_request("GET", self.path, dict(self.headers), b"", self.store)
        self.send_response(status)
        for k, v in headers.items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self) -> None:
        content_len = int(self.headers.get("Content-Length", 0))
        body_bytes = self.rfile.read(content_len) if content_len > 0 else b""
        status, headers, body = process_http_request("POST", self.path, dict(self.headers), body_bytes, self.store)
        self.send_response(status)
        for k, v in headers.items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: Any) -> None:
        # Suppress noisy logs during unit tests
        pass


async def handle_async_http_client(
    reader: asyncio.StreamReader,
    writer: asyncio.StreamWriter,
    store: EvolutionDataStore,
) -> None:
    """AsyncIO raw stream handler for high-performance concurrent client connections."""
    try:
        req_line = await reader.readline()
        if not req_line:
            writer.close()
            await writer.wait_closed()
            return
        parts = req_line.decode("utf-8").strip().split()
        if len(parts) < 2:
            writer.close()
            await writer.wait_closed()
            return
        method, path = parts[0], parts[1]

        headers: dict[str, str] = {}
        content_length = 0
        while True:
            line = await reader.readline()
            if not line or line in (b"\r\n", b"\n"):
                break
            h_str = line.decode("utf-8").strip()
            if ":" in h_str:
                hk, hv = h_str.split(":", 1)
                hk_clean = hk.strip().lower()
                headers[hk_clean] = hv.strip()
                if hk_clean == "content-length":
                    content_length = int(hv.strip())

        body_bytes = b""
        if content_length > 0:
            body_bytes = await reader.readexactly(content_length)

        status, resp_headers, body = process_http_request(method, path, headers, body_bytes, store)
        status_phrase = HTTPStatus(status).phrase if status in HTTPStatus.__members__.values() else "OK"

        writer.write(f"HTTP/1.1 {status} {status_phrase}\r\n".encode("utf-8"))
        for k, v in resp_headers.items():
            writer.write(f"{k}: {v}\r\n".encode("utf-8"))
        writer.write(b"\r\n")
        writer.write(body)
        await writer.drain()
    except Exception:
        pass
    finally:
        try:
            writer.close()
            await writer.wait_closed()
        except Exception:
            pass


async def start_async_server(
    host: str = "0.0.0.0",
    port: int = 8105,
    store: EvolutionDataStore | None = None,
) -> asyncio.Server:
    """Launches an AsyncIO native stream server on (host, port)."""
    s = store or EvolutionDataStore()
    server = await asyncio.start_server(lambda r, w: handle_async_http_client(r, w, s), host, port)
    return server


async def run_async_server(host: str = "0.0.0.0", port: int = 8105) -> None:
    """Runs the pure AsyncIO server event loop."""
    server = await start_async_server(host, port)
    print(f"=============================================================")
    print(f" Axioma Evolution Dashboard AsyncIO Server Deployed")
    print(f" URL:  http://localhost:{port}/")
    print(f" HUD:  http://localhost:{port}/dashboard")
    print(f" API:  http://localhost:{port}/api/health")
    print(f" Invariants: [L1-G3B-018], [L1-G3B-019], [L1-G4B-001]")
    print(f"=============================================================")
    async with server:
        await server.serve_forever()


def run_server(host: str = "0.0.0.0", port: int = 8105) -> None:
    """Launches the Threading HTTP Server."""
    store = EvolutionDataStore()
    EvolutionHTTPHandler.store = store
    server = ThreadingHTTPServer((host, port), EvolutionHTTPHandler)
    print(f"=============================================================")
    print(f" Axioma Evolution Dashboard & G4b Studio Deployed")
    print(f" URL:  http://localhost:{port}/")
    print(f" HUD:  http://localhost:{port}/dashboard")
    print(f" API:  http://localhost:{port}/api/health")
    print(f" Invariants: [L1-G3B-018], [L1-G3B-019], [L1-G4B-001]")
    print(f"=============================================================")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer shutting down gracefully.")
    finally:
        server.server_close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Axioma Evolution Dashboard Server")
    parser.add_argument("--host", default="0.0.0.0", help="Binding host (default 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8105, help="Port to listen on (default 8105)")
    parser.add_argument("--async", dest="use_async", action="store_true", help="Run via AsyncIO event loop")
    args = parser.parse_args()
    if args.use_async:
        try:
            asyncio.run(run_async_server(args.host, args.port))
        except KeyboardInterrupt:
            print("\nAsyncIO server shutting down gracefully.")
    else:
        run_server(args.host, args.port)
