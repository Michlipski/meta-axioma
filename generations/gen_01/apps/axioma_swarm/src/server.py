"""Zero-Dependency Multi-Tenant HTTP Server for Axioma Swarm (Port 8098).

Exposes Edge ML Operations Dashboard, VRAM allocation APIs, model rack controls,
and failure-isolated task dispatch endpoints.
"""

from __future__ import annotations

import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import sys
import time
from typing import Any, Dict, Optional
from urllib.parse import parse_qs, urlparse

APP_ROOT = Path(__file__).parent.parent
SRC_DIR = APP_ROOT / "src"
STATIC_DIR = APP_ROOT / "static"
DATA_DIR = APP_ROOT / "data"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from models import ModelSpecialty, TaskPriority
from swarm_orchestrator import ExceptionEnclave, SwarmOrchestrator
from vram_manager import OomPreventionError, VramManager

# Initialize global orchestrator
GLOBAL_ORCHESTRATOR = SwarmOrchestrator(data_dir=DATA_DIR)

# Pre-load baseline model if pool is fresh
try:
    if GLOBAL_ORCHESTRATOR.vram.pool.allocated_vram_mb == 0:
        GLOBAL_ORCHESTRATOR.vram.allocate_model("llama-3.2-3b")
except Exception:
    pass


class SwarmHttpHandler(BaseHTTPRequestHandler):
    def _send_json(self, data: dict, status: int = 200, headers: dict = None):
        body = json.dumps(data, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        if headers:
            for k, v in headers.items():
                self.send_header(k, str(v))
        self.end_headers()
        self.wfile.write(body)

    def _serve_file(self, file_path: Path, content_type: str):
        if not file_path.exists():
            self._send_json({"error": "File not found"}, 404)
            return
        with open(file_path, "rb") as f:
            content = f.read()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(content)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(content)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        with ExceptionEnclave("GET_ENCLAVE", path) as enclave:
            # 1. Static Assets
            if path in ["/", "/index.html"]:
                self._serve_file(STATIC_DIR / "index.html", "text/html; charset=utf-8")
                return
            elif path == "/style.css":
                self._serve_file(STATIC_DIR / "style.css", "text/css; charset=utf-8")
                return
            elif path == "/app.js":
                self._serve_file(STATIC_DIR / "app.js", "application/javascript; charset=utf-8")
                return
            elif path.startswith("/static/"):
                subpath = path[len("/static/"):]
                fpath = STATIC_DIR / subpath
                ctype = "text/plain"
                if subpath.endswith(".html"):
                    ctype = "text/html; charset=utf-8"
                elif subpath.endswith(".css"):
                    ctype = "text/css; charset=utf-8"
                elif subpath.endswith(".js"):
                    ctype = "application/javascript; charset=utf-8"
                self._serve_file(fpath, ctype)
                return

            # 2. VRAM Pool State
            elif path == "/api/vram":
                vram_data = GLOBAL_ORCHESTRATOR.vram.get_vram_state()
                self._send_json(vram_data)
                return

            # 3. Model Catalog & Residency
            elif path == "/api/models":
                models_data = GLOBAL_ORCHESTRATOR.vram.get_models()
                self._send_json({"models": models_data})
                return

            # 4. Tasks Query
            elif path == "/api/tasks":
                tasks_data = GLOBAL_ORCHESTRATOR.get_all_tasks()
                self._send_json({"tasks": tasks_data})
                return

            # 5. Telemetry & Health Checks
            elif path in ["/health", "/api/health"]:
                self._send_json({
                    "status": "ok",
                    "app": "axioma_swarm",
                    "port": 8098,
                    "generation": "gen_01",
                    "invariants": ["L1-008", "L1-016", "L1-015", "L1-002", "L1-011_3", "L1-015_1"],
                })
                return

            elif path == "/api/telemetry":
                telem = GLOBAL_ORCHESTRATOR.get_telemetry()
                self._send_json(telem)
                return

            self._send_json({"error": "Not found", "path": path}, 404)

        if enclave.caught:
            self._send_json({"error": "Internal enclave fault", "witness": enclave.witness}, 500)

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path

        with ExceptionEnclave("POST_ENCLAVE", path) as enclave:
            # Read payload
            length = int(self.headers.get("Content-Length", 0))
            payload = {}
            if length > 0:
                body = self.rfile.read(length).decode("utf-8")
                try:
                    payload = json.loads(body)
                except Exception:
                    self._send_json({"error": "Malformed JSON payload"}, 400)
                    return

            # 1. Dispatch New Task
            if path == "/api/tasks/dispatch":
                prompt = payload.get("prompt", "").strip()
                if not prompt:
                    self._send_json({"error": "Prompt is required."}, 400)
                    return

                specialty = payload.get("specialty")
                target_model_id = payload.get("target_model_id")
                priority = payload.get("priority", "NORMAL")

                # Submit to queue
                task = GLOBAL_ORCHESTRATOR.submit_task(
                    prompt=prompt,
                    specialty=specialty,
                    target_model_id=target_model_id,
                    priority=priority,
                )

                # Immediately execute
                executed_task = GLOBAL_ORCHESTRATOR.execute_task(task.task_id)
                status_code = 200 if executed_task.status.value == "COMPLETED" else 422
                self._send_json({
                    "message": "Task processed",
                    "task": executed_task.to_dict(),
                    "vram": GLOBAL_ORCHESTRATOR.vram.get_vram_state(),
                }, status_code)
                return

            # 2. Cancel Task
            elif path.startswith("/api/tasks/") and path.endswith("/cancel"):
                parts = path.split("/")
                task_id = parts[3]
                try:
                    t = GLOBAL_ORCHESTRATOR.cancel_task(task_id)
                    self._send_json({"message": "Task cancelled", "task": t.to_dict()})
                except KeyError as ke:
                    self._send_json({"error": str(ke)}, 404)
                return

            # 3. Model Load
            elif path.startswith("/api/models/") and path.endswith("/load"):
                parts = path.split("/")
                model_id = parts[3]
                try:
                    model, evicted = GLOBAL_ORCHESTRATOR.vram.allocate_model(model_id)
                    self._send_json({
                        "message": f"Model {model_id} loaded into resident memory.",
                        "model": model.to_dict(),
                        "evicted_models": evicted,
                        "vram": GLOBAL_ORCHESTRATOR.vram.get_vram_state(),
                    })
                except OomPreventionError as oom:
                    self._send_json({"error": str(oom), "oom_gate_triggered": True}, 422)
                except KeyError as ke:
                    self._send_json({"error": str(ke)}, 404)
                return

            # 4. Model Evict
            elif path.startswith("/api/models/") and path.endswith("/evict"):
                parts = path.split("/")
                model_id = parts[3]
                try:
                    model = GLOBAL_ORCHESTRATOR.vram.evict_model(model_id)
                    self._send_json({
                        "message": f"Model {model_id} evicted from resident memory.",
                        "model": model.to_dict(),
                        "vram": GLOBAL_ORCHESTRATOR.vram.get_vram_state(),
                    })
                except KeyError as ke:
                    self._send_json({"error": str(ke)}, 404)
                except RuntimeError as re:
                    self._send_json({"error": str(re)}, 409)
                return

            # 5. Transgenerational Feedback
            elif path == "/api/feedback":
                cat = payload.get("category", "edge_orchestration")
                comment = payload.get("comment", "").strip()
                if not comment:
                    self._send_json({"error": "Empty comment not accepted"}, 400)
                    return

                feedback_record = {
                    "id": f"fb_swarm_{int(time.time()*1000)}",
                    "category": cat,
                    "comment": comment,
                    "app": "axioma_swarm",
                    "timestamp": time.time(),
                    "generation": "gen_01",
                }

                fb_path = DATA_DIR / "feedback.json"
                existing = []
                if fb_path.exists():
                    try:
                        with open(fb_path, "r", encoding="utf-8") as f:
                            existing = json.load(f)
                    except Exception:
                        pass
                existing.append(feedback_record)
                with open(fb_path, "w", encoding="utf-8") as f:
                    json.dump(existing, f, indent=2)

                self._send_json({
                    "success": True,
                    "message": "Feedback recorded into Generation G1/G2 stream.",
                    "record": feedback_record,
                }, 201)
                return

            self._send_json({"error": "Not found", "path": path}, 404)

        if enclave.caught:
            self._send_json({"error": "Internal enclave fault", "witness": enclave.witness}, 500)

    def log_message(self, format, *args):
        pass


def run_server(port: int = 8098, host: str = "0.0.0.0"):
    server_addr = (host, port)
    httpd = ThreadingHTTPServer(server_addr, SwarmHttpHandler)
    print(f"[Axioma Swarm] Daemon active on http://{host}:{port}")
    print(f"[Axioma Swarm] VRAM Allocation: {GLOBAL_ORCHESTRATOR.vram.pool.allocated_vram_mb}MB / {GLOBAL_ORCHESTRATOR.vram.pool.usable_vram_mb}MB")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[Axioma Swarm] Daemon shutting down cleanly.")
        httpd.server_close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Axioma Swarm Edge Orchestrator")
    parser.add_argument("--port", type=int, default=8098, help="Port to bind (default: 8098)")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host interface (default: 0.0.0.0)")
    args = parser.parse_args()
    run_server(port=args.port, host=args.host)
