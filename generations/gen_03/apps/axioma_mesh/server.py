"""Axioma Mesh Ingress Gateway & HTTP Server (server.py).

Serves the Ingress Gateway API on port 8200 and the glassmorphic
Cluster Operations Dashboard PWA.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any, Dict

# Ensure local and compiler imports work cleanly
mesh_dir = Path(__file__).resolve().parent
g3_src = mesh_dir.parent.parent / "src"
if str(g3_src) not in sys.path:
    sys.path.insert(0, str(g3_src))
if str(mesh_dir) not in sys.path:
    sys.path.insert(0, str(mesh_dir))

try:
    from .core import AxiomaMeshRuntime
except ImportError:
    from core import AxiomaMeshRuntime

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("AxiomaMeshServer")

# Global runtime instance
runtime = AxiomaMeshRuntime()


class AxiomaMeshRequestHandler(BaseHTTPRequestHandler):
    """HTTP Request Handler implementing Ingress Gateway & REST API."""

    def log_message(self, format: str, *args: Any) -> None:
        """Suppress standard HTTP access spam unless error."""
        if args and str(args[1])[0] in ("4", "5"):
            super().log_message(format, *args)

    def _send_json(self, data: Dict[str, Any], status_code: int = 200) -> None:
        payload = json.dumps(data).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(payload)

    def _read_json(self) -> Dict[str, Any]:
        content_length = int(self.headers.get("Content-Length", 0))
        if content_length <= 0:
            return {}
        body = self.rfile.read(content_length).decode("utf-8")
        try:
            return json.loads(body)
        except json.JSONDecodeError:
            return {}

    def do_OPTIONS(self) -> None:
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self) -> None:
        path = self.path.split("?")[0]

        if path in ("/", "/dashboard", "/index.html"):
            html_path = Path(__file__).parent / "dashboard.html"
            if html_path.exists():
                content = html_path.read_bytes()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(content)))
                self.end_headers()
                self.wfile.write(content)
            else:
                self.send_error(404, "dashboard.html not found")
            return

        if path == "/api/status":
            self._send_json(runtime.get_cluster_status())
            return

        if path == "/api/health":
            self._send_json({"status": "HEALTHY", "node": "gateway-01", "port": 8200})
            return

        self.send_error(404, f"Unknown endpoint {path}")

    def do_POST(self) -> None:
        path = self.path.split("?")[0]
        data = self._read_json()

        if path == "/api/propose_consensus":
            key = data.get("key", "default_key")
            val = data.get("value", "default_val")
            res = runtime.propose_consensus_state(key, val)
            self._send_json(res)
            return

        if path == "/api/simulate_partition":
            node_a = data.get("node_a", "consensus-alpha")
            node_b = data.get("node_b", "consensus-gamma")
            res = runtime.simulate_partition(node_a, node_b)
            self._send_json(res)
            return

        if path == "/api/heal_partition":
            node_a = data.get("node_a", "consensus-alpha")
            node_b = data.get("node_b", "consensus-gamma")
            res = runtime.heal_partition(node_a, node_b)
            self._send_json(res)
            return

        if path == "/api/issue_token":
            client_id = data.get("client_id", "client_unknown")
            permissions = data.get("permissions", ["compute_task"])
            tok = runtime.issue_client_token(client_id, permissions)
            self._send_json({"success": True, "token": tok})
            return

        if path == "/api/dispatch_task":
            action = data.get("action", "compute_task")
            payload = data.get("payload", {})
            tok_id = data.get("capability_token_id") or runtime.gateway_token.token_id
            fault = bool(data.get("simulate_error", False))
            res = runtime.dispatch_task(action, payload, tok_id, simulate_error=fault)
            self._send_json(res)
            return

        if path == "/api/create_checkpoint":
            cp_name = data.get("checkpoint_name", f"checkpoint_{int(runtime.start_time)}")
            res = runtime.create_checkpoint(cp_name)
            self._send_json(res)
            return

        if path == "/api/rollback_checkpoint":
            cp_name = data.get("checkpoint_name", "")
            res = runtime.rollback_to_checkpoint(cp_name)
            self._send_json(res)
            return

        self.send_error(404, f"Unknown endpoint {path}")


def run_server(port: int = 8200) -> None:
    server_address = ("127.0.0.1", port)
    httpd = HTTPServer(server_address, AxiomaMeshRequestHandler)
    logger.info(f"🚀 Axioma Mesh Ingress Gateway running at http://127.0.0.1:{port}/")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info("Axioma Mesh Gateway shutting down.")
        httpd.server_close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Axioma Mesh Distributed Ingress Gateway")
    parser.add_argument("--port", type=int, default=8200, help="Ingress gateway port (default: 8200)")
    args = parser.parse_args()
    run_server(args.port)
