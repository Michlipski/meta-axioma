"""Zero-Dependency Multi-Tenant HTTP Server for Axioma E-Ink Task Router.

Binds port 8096, serving the ambient zero-JS electrophoretic glanceboard (/display),
the reactive mobile/desktop task management UI, and event-sourced REST endpoints.
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

from display_renderer import render_display_html
from event_store import EventStore
from models import FeedbackItem

# Global Event Store instance
GLOBAL_EVENT_STORE = EventStore(DATA_DIR / "events.json")

# Initialize seed data if empty
SEED_FILE = DATA_DIR / "seed.json"
if SEED_FILE.exists():
    try:
        with open(SEED_FILE, "r", encoding="utf-8") as f:
            seed_items = json.load(f)
            GLOBAL_EVENT_STORE.seed_if_empty(seed_items)
    except Exception:
        pass


class ExceptionEnclave:
    """[L1-016] Demarcated Exception Enclave isolating failure blast radiuses."""

    def __init__(self, enclave_id: str, context: str):
        self.enclave_id = enclave_id
        self.context = context
        self.caught = None
        self.witness = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_val is not None:
            self.caught = str(exc_val)
            self.witness = {
                "enclave_id": self.enclave_id,
                "context": self.context,
                "error_type": exc_type.__name__ if exc_type else "Unknown",
                "message": str(exc_val),
                "blast_radius_isolated": True,
                "timestamp": time.time(),
            }
            return True
            return False


class EinkHttpHandler(BaseHTTPRequestHandler):
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

    def _send_html(self, html_content: str, status: int = 200, headers: dict = None):
        body = html_content.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
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
            # 1. Zero-JS Electrophoretic E-Reader Display Endpoint
            if path == "/display":
                board_state = GLOBAL_EVENT_STORE.get_board_state()
                html_out = render_display_html(board_state)
                self._send_html(html_out)
                return

            # Raw text view for ultra low-spec devices / curl
            elif path == "/display/raw":
                board_state = GLOBAL_EVENT_STORE.get_board_state()
                lines = [f"=== {board_state.board_title} ==="]
                lines.append(f"Progress: {board_state.completed_count}/{board_state.total_focus_tasks} done\n")
                for idx, t in enumerate(board_state.tasks, start=1):
                    mark = "[X]" if t.status.value == "DONE" else "[ ]"
                    lines.append(f"{idx}. {mark} {t.title} ({t.tag})")
                lines.append(f"\nQuote: {board_state.quote_of_the_day}")
                raw_bytes = "\n".join(lines).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "text/plain; charset=utf-8")
                self.send_header("Content-Length", str(len(raw_bytes)))
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(raw_bytes)
                return

            # 2. Static Assets for Desktop & Mobile Task Manager
            elif path in ["/", "/index.html"]:
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
                elif subpath.endswith(".json"):
                    ctype = "application/json; charset=utf-8"
                self._serve_file(fpath, ctype)
                return

            # 3. Task Query APIs
            elif path == "/api/tasks":
                data = GLOBAL_EVENT_STORE.get_all_tasks()
                self._send_json(data)
                return

            elif path == "/api/board":
                board = GLOBAL_EVENT_STORE.get_board_state()
                self._send_json(board.to_dict())
                return

            # 4. Telemetry & Health Checks
            elif path in ["/health", "/api/health"]:
                self._send_json({
                    "status": "ok",
                    "app": "axioma_eink",
                    "port": 8096,
                    "generation": "gen_01",
                    "invariants": ["L1-002", "L1-004", "L1-011_3", "L1-008", "L1-015", "L1-016"],
                })
                return

            elif path == "/api/telemetry":
                self._send_json({
                    "app": "axioma_eink",
                    "version": "1.0.0",
                    "store_telemetry": GLOBAL_EVENT_STORE.telemetry,
                    "total_tasks": len(GLOBAL_EVENT_STORE.tasks),
                    "total_events": len(GLOBAL_EVENT_STORE.events),
                    "timestamp": time.time(),
                })
                return

            # If unhandled
            self._send_json({"error": "Not found", "path": path}, 404)

        if enclave.caught:
            self._send_json({"error": "Internal enclave fault", "witness": enclave.witness}, 500)

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path

        with ExceptionEnclave("POST_ENCLAVE", path) as enclave:
            # Read JSON payload
            length = int(self.headers.get("Content-Length", 0))
            payload = {}
            if length > 0:
                body = self.rfile.read(length).decode("utf-8")
                try:
                    payload = json.loads(body)
                except Exception:
                    self._send_json({"error": "Malformed JSON payload"}, 400)
                    return

            # 1. Create Task
            if path == "/api/tasks":
                title = payload.get("title", "").strip()
                if not title:
                    self._send_json({"error": "Task title is required."}, 400)
                    return
                priority = payload.get("priority")
                if priority is not None:
                    priority = int(priority)
                tag = payload.get("tag", "@focus")
                is_focus = payload.get("is_focus")

                try:
                    task = GLOBAL_EVENT_STORE.create_task(
                        title=title,
                        priority=priority,
                        tag=tag,
                        is_focus=is_focus,
                    )
                    self._send_json({"message": "Task created", "task": task.to_dict()}, 201)
                except ValueError as ve:
                    self._send_json({"error": str(ve)}, 422)
                return

            # 2. Toggle Task Status
            elif path.startswith("/api/tasks/") and path.endswith("/toggle"):
                parts = path.split("/")
                # /api/tasks/{task_id}/toggle
                task_id = parts[3]
                try:
                    task = GLOBAL_EVENT_STORE.toggle_task(task_id)
                    self._send_json({"message": "Task status toggled", "task": task.to_dict()})
                except KeyError as ke:
                    self._send_json({"error": str(ke)}, 404)
                return

            # 3. Focus Promotion / Demotion
            elif path.startswith("/api/tasks/") and path.endswith("/focus"):
                parts = path.split("/")
                task_id = parts[3]
                is_focus = payload.get("is_focus", True)
                try:
                    task = GLOBAL_EVENT_STORE.set_focus(task_id, bool(is_focus))
                    self._send_json({"message": "Task focus updated", "task": task.to_dict()})
                except KeyError as ke:
                    self._send_json({"error": str(ke)}, 404)
                except ValueError as ve:
                    self._send_json({"error": str(ve)}, 422)
                return

            # 4. Reorder Tasks
            elif path == "/api/tasks/reorder":
                task_ids = payload.get("task_ids", [])
                if not isinstance(task_ids, list):
                    self._send_json({"error": "task_ids must be a list"}, 400)
                    return
                try:
                    reordered = GLOBAL_EVENT_STORE.reorder_tasks(task_ids)
                    self._send_json({"message": "Tasks reordered", "tasks": [t.to_dict() for t in reordered]})
                except KeyError as ke:
                    self._send_json({"error": str(ke)}, 404)
                return

            # 5. Undo Previous Action
            elif path == "/api/undo":
                res = GLOBAL_EVENT_STORE.undo()
                self._send_json(res)
                return

            # 6. Transgenerational Feedback
            elif path == "/api/feedback":
                cat = payload.get("category", "general")
                comment = payload.get("comment", "").strip()
                if not comment:
                    self._send_json({"error": "Empty comment not accepted"}, 400)
                    return

                feedback_record = {
                    "id": f"fb_eink_{int(time.time()*1000)}",
                    "category": cat,
                    "comment": comment,
                    "app": "axioma_eink",
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

    def do_DELETE(self):
        parsed = urlparse(self.path)
        path = parsed.path

        with ExceptionEnclave("DELETE_ENCLAVE", path) as enclave:
            if path.startswith("/api/tasks/"):
                task_id = path[len("/api/tasks/"):]
                try:
                    res = GLOBAL_EVENT_STORE.delete_task(task_id)
                    self._send_json(res)
                except KeyError as ke:
                    self._send_json({"error": str(ke)}, 404)
                return

            self._send_json({"error": "Not found", "path": path}, 404)

        if enclave.caught:
            self._send_json({"error": "Internal enclave fault", "witness": enclave.witness}, 500)

    def log_message(self, format, *args):
        # Quiet standard logging to keep test & terminal output clean
        pass


def run_server(port: int = 8096, host: str = "0.0.0.0"):
    server_addr = (host, port)
    httpd = ThreadingHTTPServer(server_addr, EinkHttpHandler)
    print(f"[Axioma E-Ink Router] Serving on http://{host}:{port}")
    print(f"[Axioma E-Ink Router] Ambient Glanceboard: http://{host}:{port}/display")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[Axioma E-Ink Router] Shutting down cleanly.")
        httpd.server_close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Axioma E-Ink Task Router")
    parser.add_argument("--port", type=int, default=8096, help="Port to bind (default: 8096)")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host interface (default: 0.0.0.0)")
    args = parser.parse_args()
    run_server(port=args.port, host=args.host)
