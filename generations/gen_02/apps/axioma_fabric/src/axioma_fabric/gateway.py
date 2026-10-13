"""Axioma Fabric Asynchronous Gateway & Ingress Mesh.

Zero-external-dependency AsyncIO HTTP 1.1 & Streaming Ingress Gateway.
Provides REST and Server-Sent Event (SSE) endpoints for capability-scoped
pub/sub, cluster topology inspection, Landauer dissipation telemetry, and chaos injection.
"""

from __future__ import annotations
import asyncio
import json
import logging
import os
import time
import urllib.parse
from typing import Any, Dict, List, Optional, Tuple
from .chaos import FabricChaosCrucible
from .cocycle_auditor import FabricCocycleAuditor
from .models import CapabilityToken, CausalEvent
from .sheaf_broker import FabricBrokerNode, FabricSecurityError, FabricPartitionError
from .thermodynamics import ThermodynamicBackpressureError

logger = logging.getLogger("axioma_fabric.gateway")


class FabricGateway:
    """AsyncIO Ingress Gateway for Axioma Fabric distributed mesh."""

    def __init__(
        self,
        nodes: List[FabricBrokerNode],
        secret_key: str,
        host: str = "127.0.0.1",
        port: int = 8443,
        web_dir: Optional[str] = None,
    ) -> None:
        self.nodes = {n.node_id: n for n in nodes}
        self.node_list = list(nodes)
        self.secret_key = secret_key
        self.host = host
        self.port = port
        self.web_dir = web_dir
        self.auditor = FabricCocycleAuditor()
        self.chaos = FabricChaosCrucible(nodes)
        self.bound_port = self.port
        self._server: Optional[asyncio.Server] = None

    def create_capability_token(
        self,
        subject: str,
        topics: List[str],
        permissions: List[str],
        ttl_seconds: float = 3600.0,
    ) -> CapabilityToken:
        """Create and sign a zero-ambient capability token."""
        token_id = f"cap_{subject}_{int(time.time())}"
        return CapabilityToken.create_signed(
            token_id=token_id,
            subject=subject,
            allowed_topics=topics,
            permissions=permissions,
            ttl_seconds=ttl_seconds,
            secret_key=self.secret_key,
        )

    async def start(self) -> None:
        """Start AsyncIO HTTP server."""
        self._server = await asyncio.start_server(self._handle_client, self.host, self.port)
        if self._server.sockets:
            self.bound_port = self._server.sockets[0].getsockname()[1]
        logger.info("Fabric Gateway running on http://%s:%d", self.host, self.bound_port)

    async def stop(self) -> None:
        """Stop server gracefully."""
        if self._server:
            self._server.close()
            await self._server.wait_closed()
            self._server = None

    async def _handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        """Handle incoming HTTP/1.1 request."""
        try:
            request_line = await reader.readline()
            if not request_line:
                writer.close()
                await writer.wait_closed()
                return

            line_str = request_line.decode("utf-8").strip()
            parts = line_str.split()
            if len(parts) < 2:
                writer.close()
                await writer.wait_closed()
                return

            method, path_raw = parts[0], parts[1]
            headers: Dict[str, str] = {}
            while True:
                hdr = await reader.readline()
                if not hdr or hdr == b"\r\n" or hdr == b"\n":
                    break
                h_parts = hdr.decode("utf-8").strip().split(":", 1)
                if len(h_parts) == 2:
                    headers[h_parts[0].lower().strip()] = h_parts[1].strip()

            content_length = int(headers.get("content-length", "0"))
            body_bytes = await reader.readexactly(content_length) if content_length > 0 else b""
            body_str = body_bytes.decode("utf-8") if body_bytes else ""

            # Parse path and query
            parsed_url = urllib.parse.urlparse(path_raw)
            path = parsed_url.path
            query_params = urllib.parse.parse_qs(parsed_url.query)

            # Route request
            status_code, resp_headers, resp_body = await self._route_request(
                method, path, query_params, headers, body_str
            )

            # Send HTTP response
            status_text = {
                200: "OK",
                201: "Created",
                400: "Bad Request",
                401: "Unauthorized",
                403: "Forbidden",
                404: "Not Found",
                429: "Too Many Requests",
                500: "Internal Server Error",
            }.get(status_code, "OK")

            resp_bytes = resp_body.encode("utf-8") if isinstance(resp_body, str) else resp_body
            hdr_lines = [f"HTTP/1.1 {status_code} {status_text}"]
            resp_headers["Content-Length"] = str(len(resp_bytes))
            resp_headers["Connection"] = "close"
            for k, v in resp_headers.items():
                hdr_lines.append(f"{k}: {v}")
            hdr_lines.append("\r\n")

            writer.write("\r\n".join(hdr_lines).encode("utf-8") + resp_bytes)
            await writer.drain()
        except Exception as e:
            logger.exception("Error handling HTTP request: %s", e)
        finally:
            writer.close()
            try:
                await writer.wait_closed()
            except Exception:
                pass

    async def _route_request(
        self,
        method: str,
        path: str,
        query: Dict[str, List[str]],
        headers: Dict[str, str],
        body_str: str,
    ) -> Tuple[int, Dict[str, str], str]:
        cors_headers = {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, X-Capability-Token",
        }

        if method == "OPTIONS":
            return 200, cors_headers, ""

        # Serve static web dashboard
        if path in ("/", "/index.html"):
            return self._serve_dashboard()

        # 1. POST /api/v1/auth/token
        if path == "/api/v1/auth/token" and method == "POST":
            try:
                data = json.loads(body_str) if body_str else {}
                sub = data.get("subject", "operator")
                topics = data.get("topics", ["*"])
                perms = data.get("permissions", ["produce", "consume"])
                ttl = float(data.get("ttl_seconds", 3600))
                token = self.create_capability_token(sub, topics, perms, ttl)
                return 201, cors_headers, json.dumps({
                    "token_id": token.token_id,
                    "subject": token.subject,
                    "allowed_topics": token.allowed_topics,
                    "permissions": token.permissions,
                    "expires_at": token.expires_at,
                    "signature": token.signature,
                })
            except Exception as e:
                return 400, cors_headers, json.dumps({"error": str(e)})

        # 2. GET /api/v1/cluster/status
        if path == "/api/v1/cluster/status" and method == "GET":
            cluster_info = {}
            for nid, node in self.nodes.items():
                topics_stats = {}
                for t in list(node._sheaf_sections.keys()):
                    topics_stats[t] = {
                        "events_count": len(node.get_section(t)),
                        "thermodynamics": node.get_thermodynamics(t),
                    }
                cluster_info[nid] = {
                    "node_id": node.node_id,
                    "subdomain": node.subdomain,
                    "partition_state": node.partition_state.value,
                    "vector_clock": node.clock.to_dict(),
                    "severed_links": list(node._severed_links),
                    "topics": topics_stats,
                }
            return 200, cors_headers, json.dumps({
                "nodes": cluster_info,
                "timestamp": time.time(),
            })

        # 3. POST /api/v1/topics/{topic}/publish
        if path.startswith("/api/v1/topics/") and path.endswith("/publish") and method == "POST":
            parts = path.split("/")
            topic = parts[4]
            token = self._extract_token(headers, query)
            if not token:
                return 401, cors_headers, json.dumps({"error": "Missing capability token"})

            target_node_id = query.get("node", [self.node_list[0].node_id])[0]
            node = self.nodes.get(target_node_id, self.node_list[0])

            try:
                payload = json.loads(body_str) if body_str else {}
                event = node.publish(topic, payload, token)
                return 200, cors_headers, json.dumps({
                    "status": "published",
                    "event": event.to_dict(),
                })
            except FabricSecurityError as e:
                return 403, cors_headers, json.dumps({"error": str(e)})
            except ThermodynamicBackpressureError as e:
                return 429, cors_headers, json.dumps({"error": str(e)})
            except Exception as e:
                return 500, cors_headers, json.dumps({"error": str(e)})

        # 4. GET /api/v1/topics/{topic}/stream
        if path.startswith("/api/v1/topics/") and path.endswith("/stream") and method == "GET":
            parts = path.split("/")
            topic = parts[4]
            target_node_id = query.get("node", [self.node_list[0].node_id])[0]
            node = self.nodes.get(target_node_id, self.node_list[0])
            events = node.get_stream(topic)
            return 200, cors_headers, json.dumps({
                "topic": topic,
                "node_id": node.node_id,
                "events": [e.to_dict() for e in events],
            })

        # 5. POST /api/v1/cluster/chaos
        if path == "/api/v1/cluster/chaos" and method == "POST":
            try:
                data = json.loads(body_str) if body_str else {}
                action = data.get("action", "")
                if action == "partition":
                    grp_a = data.get("group_a", [])
                    grp_b = data.get("group_b", [])
                    self.chaos.partition_cluster(grp_a, grp_b)
                    return 200, cors_headers, json.dumps({"status": "partitioned", "group_a": grp_a, "group_b": grp_b})
                elif action == "isolate":
                    target = data.get("node_id", "")
                    self.chaos.isolate_node(target)
                    return 200, cors_headers, json.dumps({"status": "isolated", "node_id": target})
                elif action == "heal":
                    self.chaos.heal_all_partitions()
                    return 200, cors_headers, json.dumps({"status": "healed"})
                else:
                    return 400, cors_headers, json.dumps({"error": f"Unknown chaos action {action}"})
            except Exception as e:
                return 500, cors_headers, json.dumps({"error": str(e)})

        # 6. POST /api/v1/cluster/audit
        if path == "/api/v1/cluster/audit" and method == "POST":
            data = json.loads(body_str) if body_str else {}
            topic = data.get("topic", "default")
            auto_reconcile = bool(data.get("auto_reconcile", True))
            witnesses = self.auditor.audit_cluster(self.node_list, topic, auto_reconcile=auto_reconcile)
            return 200, cors_headers, json.dumps({
                "topic": topic,
                "witnesses": [w.to_dict() for w in witnesses],
                "all_reconciled": all(w.divergence_count == 0 for w in witnesses),
            })

        return 404, cors_headers, json.dumps({"error": "Not Found"})

    def _extract_token(self, headers: Dict[str, str], query: Dict[str, List[str]]) -> Optional[CapabilityToken]:
        """Extract and parse capability token from header or query param."""
        raw_header = headers.get("x-capability-token")
        if not raw_header and "token" in query:
            raw_header = query["token"][0]

        if not raw_header:
            return None

        try:
            data = json.loads(raw_header)
            return CapabilityToken(
                token_id=data["token_id"],
                subject=data["subject"],
                allowed_topics=data["allowed_topics"],
                permissions=data["permissions"],
                expires_at=data["expires_at"],
                signature=data.get("signature", ""),
            )
        except Exception:
            return None

    def _serve_dashboard(self) -> Tuple[int, Dict[str, str], str]:
        """Serve embedded single-file Web Dashboard."""
        if self.web_dir:
            idx_path = os.path.join(self.web_dir, "index.html")
            if os.path.exists(idx_path):
                with open(idx_path, "r", encoding="utf-8") as f:
                    content = f.read()
                return 200, {"Content-Type": "text/html; charset=utf-8"}, content

        # Default fallback HTML
        fallback = """<!DOCTYPE html>
<html><head><title>Axioma Fabric</title></head>
<body><h1>Axioma Fabric Distributed Mesh</h1><p>Gateway active.</p></body></html>"""
        return 200, {"Content-Type": "text/html; charset=utf-8"}, fallback
