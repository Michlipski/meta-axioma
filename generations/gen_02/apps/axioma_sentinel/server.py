"""Axioma Sentinel HTTP Server & API Dispatcher (Port 8100).

Native Python HTTP server serving the reactive dashboard and REST endpoints:
- GET  /              -> Serves dashboard.html
- GET  /api/state     -> Emits reactive system state & tokens
- POST /api/action    -> Dispatches capability-scoped tool action
- POST /api/simulate-breach -> Injects simulated fault to trigger 3-pass enclave auto-healing
- POST /api/rollback  -> Functorial 1-click state rollback (Cmd+Z)
- POST /api/token/issue -> Issues new capability token
"""

from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any, Dict, Optional
import argparse
import json
import logging
import threading

from .core import SentinelCoreEngine
from .phenomenology import SentinelPhenomenologyCircuit

logger = logging.getLogger("AxiomaSentinel")


class SentinelRequestHandler(BaseHTTPRequestHandler):
    """HTTP request handler for Axioma Sentinel."""

    engine: SentinelCoreEngine = None  # Bound at server startup
    phenomenology: SentinelPhenomenologyCircuit = None
    html_content: str = ""

    def _send_json_response(self, data: Dict[str, Any], status_code: int = 200) -> None:
        """Sends JSON response."""
        payload = json.dumps(data).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self) -> None:
        """Handles GET requests."""
        if self.path in ("/", "/dashboard.html", "/index.html"):
            payload = self.html_content.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
        elif self.path in ("/epochs", "/epochs/", "/epochs/dashboard.html", "/epoch"):
            epoch_dash_path = Path(__file__).resolve().parents[2] / "epochs" / "dashboard.html"
            content = epoch_dash_path.read_text(encoding="utf-8") if epoch_dash_path.exists() else "<h1>Generation 2 Epoch Dashboard</h1>"
            payload = content.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
        elif self.path in ("/epochs/g1", "/epochs/g1/", "/epochs/gen_01"):
            g1_dash_path = Path(__file__).resolve().parents[3] / "gen_01" / "epochs" / "dashboard.html"
            content = g1_dash_path.read_text(encoding="utf-8") if g1_dash_path.exists() else "<h1>Generation 1 Epoch Dashboard</h1>"
            payload = content.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
        elif self.path == "/api/state":
            summary = self.engine.get_system_summary()
            self._send_json_response(summary, 200)
        elif self.path == "/api/phenomenology":
            if self.phenomenology is None:
                self.phenomenology = SentinelPhenomenologyCircuit()
            self._send_json_response(self.phenomenology.get_summary(), 200)
        else:
            self._send_json_response({"error": "Not Found", "path": self.path}, 404)

    def do_POST(self) -> None:
        """Handles POST requests."""
        content_length = int(self.headers.get("Content-Length", 0))
        body_bytes = self.rfile.read(content_length)
        body = {}
        if body_bytes:
            try:
                body = json.loads(body_bytes.decode("utf-8"))
            except Exception:
                body = {}

        if self.path == "/api/action":
            tool_name = body.get("tool_name", "read_telemetry")
            parameters = body.get("parameters", {})
            token_id = body.get("token_id")
            try:
                action = self.engine.dispatch_agent_action(
                    tool_name=tool_name,
                    parameters=parameters,
                    token_id=token_id,
                    simulate_fault=False,
                )
                self._send_json_response({
                    "success": True,
                    "action_id": action.action_id,
                    "status": action.status.value,
                    "erased_bits": action.erased_bits,
                    "witness_hash": action.witness_hash,
                })
            except Exception as e:
                self._send_json_response({"success": False, "error": str(e)}, 400)

        elif self.path == "/api/simulate-breach":
            token_id = body.get("token_id")
            try:
                # Dispatch tool with intentional non-integer string param to trigger Pass 1 coercion
                action = self.engine.dispatch_agent_action(
                    tool_name="simulate_breach",
                    parameters={"count": "42", "target_key": "healed_metric"},
                    token_id=token_id,
                    simulate_fault=True,
                )
                self._send_json_response({
                    "success": True,
                    "action_id": action.action_id,
                    "status": action.status.value,
                    "remediation_notes": action.remediation_notes,
                })
            except Exception as e:
                self._send_json_response({"success": False, "error": str(e)}, 400)

        elif self.path == "/api/rollback":
            rollback_result = self.engine.rollback_to_last_checkpoint()
            self._send_json_response(rollback_result, 200)

        elif self.path == "/api/token/issue":
            persona = body.get("persona", "Temporary_Agent")
            actions = body.get("actions", ["read_telemetry"])
            tok = self.engine.capability_authority.issue_new_token(persona=persona, allowed_actions=actions)
            self._send_json_response({
                "success": True,
                "token_id": tok.token_id,
                "persona": tok.persona,
                "allowed_actions": tok.allowed_actions,
            })

        elif self.path == "/api/phenomenology/interaction":
            if self.phenomenology is None:
                self.phenomenology = SentinelPhenomenologyCircuit()
            event = self.phenomenology.record_interaction(
                tool_name=body.get("tool_name", "unknown_tool"),
                dwell_seconds=float(body.get("dwell_seconds", 1.0)),
                undo_count_in_window=int(body.get("undo_count", 0)),
                erratic_input_switches=int(body.get("switches", 0)),
                unhandled_error_shown=bool(body.get("error_shown", False)),
            )
            self._send_json_response({"success": True, "event": event.to_dict()}, 200)

        else:
            self._send_json_response({"error": "Unknown Endpoint", "path": self.path}, 404)

    def log_message(self, format: str, *args: Any) -> None:
        """Suppresses default noisy stderr logs."""
        pass


def run_sentinel_server(port: int = 8100, host: str = "127.0.0.1") -> HTTPServer:
    """Initializes and runs the Axioma Sentinel HTTP server."""
    html_path = Path(__file__).parent / "dashboard.html"
    html_content = html_path.read_text(encoding="utf-8") if html_path.exists() else "<h1>Axioma Sentinel</h1>"

    engine = SentinelCoreEngine()
    SentinelRequestHandler.engine = engine
    SentinelRequestHandler.html_content = html_content

    server = HTTPServer((host, port), SentinelRequestHandler)
    print(f"[*] Axioma Sentinel running at http://{host}:{port}/")
    return server


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Axioma Sentinel Server")
    parser.add_argument("--port", type=int, default=8100, help="Port to bind (default: 8100)")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host interface")
    args = parser.parse_args()

    srv = run_sentinel_server(port=args.port, host=args.host)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\n[!] Shutting down Axioma Sentinel server.")
        srv.server_close()
