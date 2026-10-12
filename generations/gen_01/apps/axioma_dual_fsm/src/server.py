"""Zero-Trust HTTP Gateway & Telemetry Server for Axioma Dual FSM.
Binds port 8092, providing deterministic state inspection, attack simulation, and live telemetry.
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
from pathlib import Path
import sys
import time
from urllib.parse import urlparse

APP_ROOT = Path(__file__).parent.parent
SRC_DIR = APP_ROOT / "src"
STATIC_DIR = APP_ROOT / "static"
DATA_DIR = APP_ROOT / "data"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from coupled_gateway import CoupledGateway, LANDAUER_LIMIT


class ExceptionEnclave:
    """[L1-016] Demarcated Exception Enclave isolating failure blast radiuses."""

    def __init__(self, enclave_id: str, context: str):
        self.enclave_id = enclave_id
        self.context = context
        self.caught: Optional[str] = None
        self.witness: Optional[dict] = None

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


gateway_kernel = CoupledGateway()


class AppHttpHandler(BaseHTTPRequestHandler):
    def _send_json(self, data: dict, status: int = 200):
        body = json.dumps(data, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        # 1. State API
        if path == "/api/state":
            self._send_json(gateway_kernel.get_full_state())
            return

        # 2. Audit Log API
        if path == "/api/audit":
            self._send_json({"audit_log": gateway_kernel.audit_log})
            return

        # 3. Static Assets
        if path == "/" or path == "/index.html":
            file_path = STATIC_DIR / "index.html"
            content_type = "text/html; charset=utf-8"
        elif path.endswith(".css"):
            file_path = STATIC_DIR / path.lstrip("/")
            content_type = "text/css; charset=utf-8"
        elif path.endswith(".js"):
            file_path = STATIC_DIR / path.lstrip("/")
            content_type = "application/javascript; charset=utf-8"
        else:
            file_path = STATIC_DIR / path.lstrip("/")
            content_type = "application/octet-stream"

        if file_path.exists() and file_path.is_file():
            with open(file_path, "rb") as f:
                content = f.read()
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length) if length > 0 else b"{}"
        try:
            payload = json.loads(body.decode("utf-8")) if body else {}
        except Exception:
            payload = {}

        with ExceptionEnclave("API_GATEWAY", f"Handling POST {path}") as enclave:
            # Execute Coupled Turn
            if path == "/api/step":
                text = payload.get("text", "")
                inner_event = payload.get("inner_event")
                inner_payload = payload.get("inner_payload", {})
                success, msg, state = gateway_kernel.execute_turn(
                    text=text,
                    inner_event=inner_event,
                    inner_payload=inner_payload,
                )
                self._send_json({
                    "success": success,
                    "message": msg,
                    "state": state,
                })
                return

            # Functorial Revert Morphism (L1-002)
            if path == "/api/revert":
                note = payload.get("note", "Manual Revert via UI")
                success, msg = gateway_kernel.revert_state(operator_note=note)
                self._send_json({
                    "success": success,
                    "message": msg,
                    "state": gateway_kernel.get_full_state(),
                })
                return

            # Active Generational Feedback Ingestion
            if path == "/api/feedback":
                fb_entry = {
                    "id": f"fb_{int(time.time()*1000)}",
                    "rating": payload.get("rating", 5),
                    "comment": payload.get("comment", ""),
                    "category": payload.get("category", "GENERAL"),
                    "context_view": payload.get("context_view", "dual_fsm_console"),
                    "timestamp": time.time(),
                }
                fb_file = DATA_DIR / "user_feedback.json"
                existing = []
                if fb_file.exists():
                    try:
                        with open(fb_file, "r", encoding="utf-8") as f:
                            existing = json.load(f)
                    except Exception:
                        existing = []
                existing.append(fb_entry)
                with open(fb_file, "w", encoding="utf-8") as f:
                    json.dump(existing, f, indent=2)
                self._send_json({"status": "FEEDBACK_RECORDED", "entry": fb_entry})
                return

        if enclave.caught:
            self._send_json({
                "error": enclave.caught,
                "witness": enclave.witness,
                "guidance": "Exception safely captured in Demarcated Exception Enclave.",
            }, status=400)


def run_server(port: int = 8092, host: str = "0.0.0.0"):
    server_address = (host, port)
    httpd = HTTPServer(server_address, AppHttpHandler)
    print(f"🛡️ Axioma Dual FSM running at http://{host}:{port}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server gracefully.")
        httpd.server_close()


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8092
    run_server(port=port)
