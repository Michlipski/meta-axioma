"""Zero-Dependency Multi-Tenant HTTP Server for Axioma Crossword.

Binds port 8094, serving the multi-device cruciverbalist UI, partitioned session APIs,
and decoupled asynchronous CSP synthesis worker endpoints.
"""

from __future__ import annotations

from http.server import HTTPServer, ThreadingHTTPServer, BaseHTTPRequestHandler
import json
from pathlib import Path
import sys
import time
from urllib.parse import parse_qs, urlparse

APP_ROOT = Path(__file__).parent.parent
SRC_DIR = APP_ROOT / "src"
STATIC_DIR = APP_ROOT / "static"
DATA_DIR = APP_ROOT / "data"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from session_store import GLOBAL_STORE
from worker_pool import GLOBAL_WORKER_POOL


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


class CrosswordHttpHandler(BaseHTTPRequestHandler):
    def _send_json(self, data: dict, status: int = 200, headers: dict = None):
        body = json.dumps(data, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS, PATCH")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, If-Match")
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
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS, PATCH")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, If-Match")
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)

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

            # 2. Puzzles API
            elif path == "/api/puzzles":
                puzzles = GLOBAL_STORE.list_puzzles()
                self._send_json({"puzzles": puzzles, "count": len(puzzles)})
                return

            elif path.startswith("/api/puzzles/"):
                puzzle_id = path.split("/api/puzzles/")[1]
                puzzle = GLOBAL_STORE.get_puzzle(puzzle_id)
                if not puzzle:
                    self._send_json({"error": f"Puzzle {puzzle_id} not found"}, 404)
                    return
                # Edge caching header for immutable puzzle
                self._send_json(
                    puzzle.to_dict(),
                    200,
                    headers={"Cache-Control": "public, max-age=86400, immutable"},
                )
                return

            # 3. Solver Session API
            elif path.startswith("/api/sessions/"):
                parts = path.split("/")
                session_id = parts[3]
                p_id = query.get("puzzle_id", ["puzzle_quick_01"])[0]
                session = GLOBAL_STORE.get_or_create_session(session_id, puzzle_id=p_id)
                self._send_json(session.to_dict(), 200, headers={"ETag": f'"{session.version}"'})
                return

            # 4. Asynchronous Synthesis Job API
            elif path.startswith("/api/jobs/"):
                job_id = path.split("/api/jobs/")[1]
                job = GLOBAL_WORKER_POOL.get_job(job_id)
                if not job:
                    self._send_json({"error": f"Job {job_id} not found"}, 404)
                    return
                resp = job.to_dict()
                if job.result_grid:
                    resp["result_grid"] = job.result_grid.to_dict()
                self._send_json(resp)
                return

            elif path == "/api/jobs":
                jobs = [j.to_dict() for j in GLOBAL_WORKER_POOL.list_jobs().values()]
                self._send_json({"jobs": jobs, "total": len(jobs)})
                return

            # 5. Telemetry API
            elif path == "/api/telemetry":
                puzzles = GLOBAL_STORE.list_puzzles()
                jobs = GLOBAL_WORKER_POOL.list_jobs()
                total_joules = sum(j.joules_dissipated for j in jobs.values())
                total_backtracks = sum(j.backtracks_count for j in jobs.values())
                self._send_json({
                    "port": 8094,
                    "puzzles_count": len(puzzles),
                    "total_jobs": len(jobs),
                    "total_backtracks": total_backtracks,
                    "total_landauer_joules": total_joules,
                    "status": "HEALTHY",
                })
                return

        if enclave.caught:
            self._send_json({"error": enclave.caught, "enclave_witness": enclave.witness}, 500)
            return

        self._send_json({"error": "Route not found", "path": path}, 404)

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path

        content_len = int(self.headers.get("Content-Length", 0))
        body_bytes = self.rfile.read(content_len) if content_len > 0 else b"{}"
        try:
            payload = json.loads(body_bytes.decode("utf-8")) if body_bytes else {}
        except Exception:
            payload = {}

        with ExceptionEnclave("POST_ENCLAVE", path) as enclave:
            # 1. Delta Mutation Sync (L1-002, L1-011_3)
            if path.startswith("/api/sessions/") and path.endswith("/delta"):
                parts = path.split("/")
                session_id = parts[3]
                row = int(payload.get("row", 0))
                col = int(payload.get("col", 0))
                char = payload.get("char", "")
                expected_v = payload.get("expected_version")

                session, success = GLOBAL_STORE.apply_delta(
                    session_id=session_id,
                    row=row,
                    col=col,
                    char=char,
                    expected_version=expected_v,
                )
                status_code = 200 if success else 409  # 409 Conflict if desynced
                self._send_json(
                    {
                        "success": success,
                        "session": session.to_dict(),
                        "conflict": not success,
                        "version": session.version,
                    },
                    status_code,
                    headers={"ETag": f'"{session.version}"'},
                )
                return

            # 2. Asynchronous Synthesis Job Dispatch (L1-015_1)
            elif path == "/api/jobs/synthesize":
                grid_size = int(payload.get("grid_size", 7))
                job = GLOBAL_WORKER_POOL.enqueue_synthesis_job(grid_size=grid_size)
                # 202 Accepted with location header
                self._send_json(
                    {
                        "message": "Crossword synthesis job enqueued into worker pool",
                        "job": job.to_dict(),
                    },
                    202,
                    headers={"Location": f"/api/jobs/{job.job_id}"},
                )
                return

            # 3. Transgenerational User Feedback (L1-001 / FEEDBACK.md)
            elif path == "/api/feedback":
                cat = payload.get("category", "general")
                comment = payload.get("comment", "").strip()
                if not comment:
                    self._send_json({"error": "Empty comment not accepted"}, 400)
                    return

                feedback_record = {
                    "id": f"fb_cw_{int(time.time()*1000)}",
                    "category": cat,
                    "comment": comment,
                    "app": "axioma_crossword",
                    "timestamp": time.time(),
                    "generation": "gen_01",
                }

                # Save locally
                fb_path = DATA_DIR / "user_feedback.json"
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
                })
                return

        if enclave.caught:
            self._send_json({"error": enclave.caught, "enclave_witness": enclave.witness}, 500)
            return

        self._send_json({"error": "Route not found", "path": path}, 404)

    def log_message(self, format, *args):
        # Concise logging
        sys.stderr.write(f"[AxiomaCrossword:8094] {self.address_string()} - {format % args}\n")


def run_server(port: int = 8094):
    server_address = ("127.0.0.1", port)
    httpd = ThreadingHTTPServer(server_address, CrosswordHttpHandler)
    print(f"================================================================")
    print(f" Axioma Crossword Engine (Generation G1)")
    print(f" Port 8094 | http://localhost:{port}")
    print(f" Multi-Device Responsive | Optimistic Delta Sync | AC-3 Studio")
    print(f"================================================================")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down Axioma Crossword server cleanly.")
        httpd.server_close()


if __name__ == "__main__":
    run_server()
