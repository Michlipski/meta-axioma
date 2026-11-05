"""Decoupled Presentation Cockpit & SSE Server (`cockpit_server.py`).

Enforces:
- [L1-G4B-001] Decoupled Presentation Plane Architecture (< 250KB Zero-CDN).
- [L1-G3B-011] Universal Compositional Contract IR (StreamLiveTelemetrySSE, QueryTemporalWindow, ExecuteFunctorialRollback).
- [L1-G3B-018] Real-Time Streaming HUD (< 50ms SSE push).
- Endpoints:
  - GET  /api/v1/telemetry/stream: Real-time Server-Sent Events (SSE).
  - GET  /api/v1/telemetry/window: Temporal slice query (< 5ms).
  - GET  /api/v1/telemetry/keyframe: State keyframe snapshot.
  - GET  /api/v1/telemetry/summary: Aggregated metrics & Landauer dissipation.
  - POST /api/v1/telemetry/rollback: Categorical 1-tap Functorial Undo delta^-1(T).
  - Static file serving for zenith_cockpit presentation assets.
"""

from __future__ import annotations

import asyncio
from dataclasses import asdict
from enum import Enum
import json
import logging
import mimetypes
import os
from pathlib import Path
import time
from typing import Any, Dict, List, Optional
import urllib.parse

try:
    from .ingest_server import IngestServer
    from .rollback_engine import RollbackEngine
    from .telemetry_vault import MeshTransaction, TelemetryVault, assert_non_loopback
except ImportError:
    from ingest_server import IngestServer
    from rollback_engine import RollbackEngine
    from telemetry_vault import MeshTransaction, TelemetryVault, assert_non_loopback

logger = logging.getLogger("cockpit_server")


class Profile(str, Enum):
    """Runtime networking profiles: Honest Local IPC vs Sovereign Distributed Mesh."""
    LOCAL_IPC = "LOCAL_IPC"
    SOVEREIGN_MESH = "SOVEREIGN_MESH"


class CockpitServer:
    """Decoupled HTTP/SSE Cockpit Server serving the presentation layer and REST APIs."""

    def __init__(
        self,
        vault: TelemetryVault,
        ingest_server: IngestServer,
        rollback_engine: RollbackEngine,
        host: Optional[str] = None,
        port: int = 8447,
        static_dir: Optional[str] = None,
        allow_any_interface_for_testing: bool = False,
        profile: Optional[Profile] = None,
        unix_socket_path: Optional[str] = None,
    ) -> None:
        if profile is None:
            if host is not None and not allow_any_interface_for_testing:
                assert_non_loopback(host, f"CockpitServer host '{host}'")
                profile = Profile.SOVEREIGN_MESH
            else:
                profile = Profile.LOCAL_IPC

        self.profile = profile
        self.unix_socket_path = unix_socket_path

        if host is None:
            self.host = "127.0.0.1" if profile == Profile.LOCAL_IPC else "192.168.40.40"
        else:
            self.host = host

        if self.profile == Profile.SOVEREIGN_MESH and not allow_any_interface_for_testing:
            assert_non_loopback(self.host, f"CockpitServer host '{self.host}'")

        self.vault = vault
        self.ingest_server = ingest_server
        self.rollback_engine = rollback_engine
        self.port = port
        self.allow_any_interface_for_testing = allow_any_interface_for_testing

        # Locate static files directory
        if static_dir:
            self.static_dir = Path(static_dir).resolve()
        else:
            candidate = Path(__file__).resolve().parent.parent / "cockpit"
            if candidate.exists():
                self.static_dir = candidate
            else:
                self.static_dir = (
                    Path(__file__).resolve().parent.parent.parent.parent / "apps" / "zenith_cockpit"
                ).resolve()

        self._server: Optional[asyncio.Server] = None
        self._running = False
        self.active_sse_connections = 0

    async def handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        """Dispatches HTTP/1.1 requests including long-lived SSE connections and static assets."""
        try:
            req_line = await reader.readline()
            if not req_line:
                writer.close()
                await writer.wait_closed()
                return

            req_str = req_line.decode("utf-8", errors="replace").strip()
            parts = req_str.split()
            if len(parts) < 2:
                writer.close()
                await writer.wait_closed()
                return

            method, full_path = parts[0], parts[1]

            # Parse query parameters
            parsed = urllib.parse.urlparse(full_path)
            path = parsed.path
            query_params = urllib.parse.parse_qs(parsed.query)

            # Read headers
            headers = {}
            content_length = 0
            while True:
                line = await reader.readline()
                if not line or line == b"\r\n":
                    break
                h_str = line.decode("utf-8", errors="replace").strip()
                if ":" in h_str:
                    k, v = h_str.split(":", 1)
                    headers[k.strip().lower()] = v.strip()
                    if k.strip().lower() == "content-length":
                        content_length = int(v.strip())

            # Read body if present
            body_bytes = b""
            if content_length > 0:
                body_bytes = await reader.readexactly(content_length)

            # -------------------------------------------------------------
            # Route: Healthcheck Probe (Honest Liveness & Profile Introspection)
            # -------------------------------------------------------------
            if path == "/healthz" and method == "GET":
                await self._send_json(writer, {
                    "status": "ok",
                    "service": "telemetry",
                    "profile": self.profile.value,
                    "host": self.host,
                    "port": self.port,
                    "active_sse_connections": self.active_sse_connections,
                })
                return

            # -------------------------------------------------------------
            # Route: SSE Real-Time Telemetry Stream
            # -------------------------------------------------------------
            if path == "/api/v1/telemetry/stream" and method == "GET":
                await self._handle_sse_stream(writer)
                return

            # -------------------------------------------------------------
            # Route: Temporal Window Query
            # -------------------------------------------------------------
            if path == "/api/v1/telemetry/window" and method == "GET":
                self._drain_scratch_spillover_into_vault()
                start_ns = int(query_params.get("start_ns", [0])[0])
                end_ns = int(query_params.get("end_ns", [time.time_ns() + 3_600_000_000_000])[0])
                target_ns = query_params.get("target_timestamp_ns")
                max_records = int(query_params.get("max_records", [2000])[0])

                if target_ns:
                    window = self.vault.query_window_by_target(
                        target_timestamp_ns=int(target_ns[0]),
                        max_delta_records=max_records,
                    )
                else:
                    window = self.vault.query_temporal_window(
                        start_ns=start_ns,
                        end_ns=end_ns,
                        max_delta_records=max_records,
                    )
                resp_payload = window.to_dict()
                resp_payload["conversations"] = self._get_conversation_names()
                await self._send_json(writer, resp_payload)
                return

            # -------------------------------------------------------------
            # Route: Conversations Names Mapping
            # -------------------------------------------------------------
            if path == "/api/v1/telemetry/conversations" and method == "GET":
                names = self._get_conversation_names()
                await self._send_json(writer, {"conversations": names})
                return

            # -------------------------------------------------------------
            # Route: State Keyframe Snapshot
            # -------------------------------------------------------------
            if path == "/api/v1/telemetry/keyframe" and method == "GET":
                target_ns = query_params.get("timestamp_ns")
                if target_ns:
                    kf = self.vault.get_keyframe_before_or_at(int(target_ns[0]))
                else:
                    kf = self.vault.get_latest_keyframe()

                if kf:
                    await self._send_json(writer, kf.to_dict())
                else:
                    await self._send_json(writer, {"error": "No keyframe snapshots found"}, status=404)
                return

            # -------------------------------------------------------------
            # Route: Summary Metrics & Landauer Dissipation
            # -------------------------------------------------------------
            if path == "/api/v1/telemetry/summary" and method == "GET":
                vault_summary = self.vault.get_summary()
                ingest_health = self.ingest_server.get_health_status()
                payload = {
                    "vault": vault_summary,
                    "ingest": ingest_health,
                    "cockpit": {
                        "active_sse_connections": self.active_sse_connections,
                        "server_time_ns": time.time_ns(),
                    },
                }
                await self._send_json(writer, payload)
                return

            # -------------------------------------------------------------
            # Route: Categorical 1-Tap Functorial Rollback
            # -------------------------------------------------------------
            if path == "/api/v1/telemetry/rollback" and method == "POST":
                try:
                    data = json.loads(body_bytes.decode("utf-8")) if body_bytes else {}
                    target_tx_id = data.get("target_tx_id", "")
                    target_ns = data.get("target_timestamp_ns")
                    cmd_id = data.get("command_id", f"cmd_rollback_{int(time.time() * 1000)}")
                    preview_only = data.get("preview_only", False)

                    if preview_only:
                        preview = self.rollback_engine.preview_rollback(
                            target_tx_id=target_tx_id,
                            target_timestamp_ns=target_ns,
                        )
                        await self._send_json(writer, preview)
                    else:
                        success, cmd = self.rollback_engine.execute_functorial_rollback(
                            command_id=cmd_id,
                            target_tx_id=target_tx_id,
                            target_timestamp_ns=target_ns,
                            operator_notes=data.get("notes", "1-tap rollback initiated via cockpit"),
                        )
                        await self._send_json(
                            writer,
                            {
                                "success": success,
                                "command": cmd.to_dict(),
                                "restored_at_ns": cmd.target_timestamp_ns,
                            },
                        )
                except Exception as e:
                    await self._send_json(writer, {"error": str(e)}, status=400)
                return

            # -------------------------------------------------------------
            # Route: Static Assets (Presentation Cockpit)
            # -------------------------------------------------------------
            await self._handle_static_file(writer, path)

        except Exception as e:
            logger.exception("Error in CockpitServer dispatcher: %s", e)
            try:
                writer.close()
                await writer.wait_closed()
            except Exception:
                pass

    async def _handle_sse_stream(self, writer: asyncio.StreamWriter) -> None:
        """Handles continuous Server-Sent Events push to connected presentation clients."""
        self.active_sse_connections += 1
        listener_queue = self.ingest_server.register_sse_listener()

        headers = (
            "HTTP/1.1 200 OK\r\n"
            "Content-Type: text/event-stream\r\n"
            "Cache-Control: no-cache\r\n"
            "Connection: keep-alive\r\n"
            "Access-Control-Allow-Origin: *\r\n\r\n"
        )
        writer.write(headers.encode("utf-8"))
        await writer.drain()

        # Send initial handshake event with current vault summary and conversation names
        handshake_data = json.dumps({
            "event": "HANDSHAKE",
            "server_time_ns": time.time_ns(),
            "summary": self.vault.get_summary(),
            "conversations": self._get_conversation_names(),
        })
        writer.write(f"event: handshake\ndata: {handshake_data}\n\n".encode("utf-8"))
        await writer.drain()

        try:
            while self._running:
                try:
                    # Wait for next transaction or send periodic keepalive
                    tx = await asyncio.wait_for(listener_queue.get(), timeout=15.0)
                    tx_data = json.dumps(tx.to_dict())
                    msg = f"event: transaction\ndata: {tx_data}\n\n"
                    writer.write(msg.encode("utf-8"))
                    await writer.drain()
                except asyncio.TimeoutError:
                    # Keep-alive comment
                    writer.write(b": keepalive\n\n")
                    await writer.drain()

        except (ConnectionResetError, BrokenPipeError, asyncio.CancelledError):
            pass
        finally:
            self.active_sse_connections = max(0, self.active_sse_connections - 1)
            self.ingest_server.unregister_sse_listener(listener_queue)
            try:
                writer.close()
                await writer.wait_closed()
            except Exception:
                pass

    async def _handle_static_file(self, writer: asyncio.StreamWriter, path: str) -> None:
        """Serves zero-CDN static frontend files safely."""
        rel_path = path.lstrip("/")
        if rel_path == "cockpit" or rel_path == "cockpit/":
            rel_path = "index.html"
        elif rel_path.startswith("cockpit/"):
            rel_path = rel_path[len("cockpit/") :]

        if not rel_path or rel_path == "/":
            rel_path = "index.html"

        file_path = (self.static_dir / rel_path).resolve()

        # Security check: prevent directory traversal
        try:
            file_path.relative_to(self.static_dir)
        except ValueError:
            await self._send_json(writer, {"error": "Access Denied"}, status=403)
            return

        if not file_path.exists() or not file_path.is_file():
            # If requesting root or app assets that are still in apps/zenith_cockpit, handle gracefully
            await self._send_json(writer, {"error": f"File '{rel_path}' not found"}, status=404)
            return

        content_type, _ = mimetypes.guess_type(str(file_path))
        content_type = content_type or "application/octet-stream"
        if file_path.suffix == ".js":
            content_type = "application/javascript"
        elif file_path.suffix == ".css":
            content_type = "text/css"
        elif file_path.suffix == ".html":
            content_type = "text/html; charset=utf-8"

        try:
            content = file_path.read_bytes()
            resp = (
                f"HTTP/1.1 200 OK\r\n"
                f"Content-Type: {content_type}\r\n"
                f"Content-Length: {len(content)}\r\n"
                f"Access-Control-Allow-Origin: *\r\n"
                f"Connection: close\r\n\r\n"
            ).encode("utf-8") + content
            writer.write(resp)
            await writer.drain()
        except Exception as e:
            logger.error("Failed to read static file: %s", e)
        finally:
            try:
                writer.close()
                await writer.wait_closed()
            except Exception:
                pass

    async def _send_json(
        self,
        writer: asyncio.StreamWriter,
        data: Dict[str, Any],
        status: int = 200,
    ) -> None:
        try:
            body = json.dumps(data)
            resp = (
                f"HTTP/1.1 {status} OK\r\n"
                f"Content-Type: application/json\r\n"
                f"Content-Length: {len(body.encode('utf-8'))}\r\n"
                f"Access-Control-Allow-Origin: *\r\n"
                f"Connection: close\r\n\r\n"
                f"{body}"
            )
            writer.write(resp.encode("utf-8"))
            await writer.drain()
        except Exception:
            pass
        finally:
            try:
                writer.close()
                await writer.wait_closed()
            except Exception:
                pass

    def _get_conversation_names(self) -> Dict[str, Dict[str, Any]]:
        """Resolves subagent conversation IDs to their authentic declared roles on disk.

        Conversations that are not subagents (such as root sessions) are omitted
        so the UI can cleanly display their actual Conversation IDs without fabricated titles.
        """
        names: Dict[str, Dict[str, Any]] = {}
        brain_base = Path.home() / ".gemini" / "antigravity" / "brain"

        # 1. Scan brain directory for authentic subagent descriptors
        try:
            cur = self.vault._conn.cursor()
            cur.execute("SELECT DISTINCT trace_id FROM mesh_transactions")
            for (trace_id,) in cur.fetchall():
                if not trace_id:
                    continue
                subagents_dir = brain_base / str(trace_id) / ".system_generated" / "subagents"
                if subagents_dir.exists():
                    for sf in subagents_dir.glob("*.json"):
                        try:
                            data = json.loads(sf.read_text("utf-8"))
                            cid = data.get("conversationId")
                            desc = data.get("subagentDescriptor", {})
                            role = desc.get("role")
                            type_name = desc.get("typeName", "self")
                            if cid and role:
                                names[cid] = {
                                    "role": role,
                                    "type": type_name,
                                    "parent": trace_id,
                                }
                        except Exception:
                            pass
        except Exception as e:
            logger.debug("Vault trace_id query error: %s", e)

        # 2. Check hook state in .scratch/telemetry_hook_state.json for registered subagents
        scratch_hook = Path(".scratch/telemetry_hook_state.json")
        if scratch_hook.exists():
            try:
                state_data = json.loads(scratch_hook.read_text("utf-8"))
                for cid, info in state_data.get("subagents", {}).items():
                    if cid not in names and isinstance(info, dict) and info.get("role"):
                        names[cid] = {
                            "role": info.get("role"),
                            "type": info.get("type", "self"),
                            "parent": None,
                        }
            except Exception:
                pass

        # 3. Correlate DISPATCH_SUBAGENT dispatches from vault with child traces
        try:
            cur = self.vault._conn.cursor()
            # Fetch all trace activity windows
            cur.execute("""
                SELECT trace_id, MIN(timestamp_ns), MAX(timestamp_ns), COUNT(*)
                FROM mesh_transactions
                WHERE trace_id IS NOT NULL AND trace_id != ''
                GROUP BY trace_id
            """)
            trace_info = {r[0]: {"min_ts": r[1], "max_ts": r[2], "count": r[3]} for r in cur.fetchall()}

            for tr, info in trace_info.items():
                if tr not in names:
                    names[tr] = {
                        "role": None,
                        "type": "self",
                        "parent": None,
                        "latest_timestamp_ns": info["max_ts"],
                        "event_count": info["count"],
                    }
                else:
                    names[tr]["latest_timestamp_ns"] = info["max_ts"]
                    names[tr]["event_count"] = info["count"]

            # Fetch DISPATCH_SUBAGENT events
            cur.execute("""
                SELECT trace_id, subagent_role, timestamp_ns, payload_json
                FROM mesh_transactions
                WHERE verb = 'DISPATCH_SUBAGENT'
                ORDER BY timestamp_ns ASC
            """)
            for parent_trace, default_role, d_ts, pj in cur.fetchall():
                role_arg = default_role
                if pj:
                    try:
                        p = json.loads(pj)
                        role_arg = p.get("tool_args", {}).get("Role") or default_role
                    except Exception:
                        pass

                # Correlate with closest child trace that started shortly after d_ts
                best_child = None
                best_dt = 45_000_000_000  # 45 seconds window
                for tr, info in trace_info.items():
                    if tr != parent_trace and names[tr].get("parent") is None:
                        dt = info["min_ts"] - d_ts
                        if 0 <= dt < best_dt:
                            best_dt = dt
                            best_child = tr
                if best_child:
                    names[best_child]["parent"] = parent_trace
                    if role_arg and role_arg not in ("None", "Main Orchestrator", "Root Orchestrator"):
                        names[best_child]["role"] = role_arg

            # 4. Capture any explicit subagent_role fields recorded in non-dispatch transactions
            cur.execute("""
                SELECT DISTINCT trace_id, subagent_id, subagent_role
                FROM mesh_transactions
                WHERE verb != 'DISPATCH_SUBAGENT'
            """)
            for trace_id, sub_id, role in cur.fetchall():
                if trace_id in names and not names[trace_id].get("role"):
                    if role and role not in ("None", "Main Orchestrator", "Root Orchestrator"):
                        names[trace_id]["role"] = role
                        names[trace_id]["type"] = sub_id or "self"
        except Exception as e:
            logger.debug("Vault trace correlation error: %s", e)

        return names

    def _drain_scratch_spillover_into_vault(self) -> int:
        """Drains un-flushed spillover records from .scratch/spillover_telemetry.jsonl into the vault."""
        spillover_path = Path(".scratch/spillover_telemetry.jsonl")
        if not spillover_path.exists() or spillover_path.stat().st_size == 0:
            return 0
        try:
            records = []
            with open(spillover_path, "r", encoding="utf-8") as f:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        d = json.loads(line)
                        if "tx" in d and isinstance(d["tx"], dict):
                            d = d["tx"]
                        if "transaction_id" in d:
                            records.append(MeshTransaction.from_dict(d))
                    except Exception:
                        pass
            if records:
                self.vault.insert_batch(records)
            try:
                spillover_path.unlink()
            except Exception:
                with open(spillover_path, "w", encoding="utf-8") as f:
                    f.write("")
            return len(records)
        except Exception as e:
            logger.warning("Spillover drain error: %s", e)
            return 0

    async def start(self) -> None:
        """Starts the CockpitServer listener under the active runtime Profile."""
        self._running = True
        if self.unix_socket_path:
            sock_p = Path(self.unix_socket_path).resolve()
            sock_p.parent.mkdir(parents=True, exist_ok=True)
            if sock_p.exists():
                sock_p.unlink()
            self._server = await asyncio.start_unix_server(self.handle_client, path=str(sock_p))
            logger.info("CockpitServer active on Unix socket: %s (Profile: %s)", sock_p, self.profile.value)
            return

        if self.profile == Profile.LOCAL_IPC:
            bind_host = self.host if self.host in ("127.0.0.1", "localhost", "::1", "0.0.0.0") else "127.0.0.1"
            self.host = bind_host
            self._server = await asyncio.start_server(self.handle_client, bind_host, self.port)
            logger.info("CockpitServer active on %s:%d (Profile: LOCAL_IPC)", self.host, self.port)
        elif self.profile == Profile.SOVEREIGN_MESH:
            try:
                self._server = await asyncio.start_server(self.handle_client, self.host, self.port)
                logger.info("CockpitServer active on %s:%d (Profile: SOVEREIGN_MESH)", self.host, self.port)
            except OSError as err:
                logger.error(
                    "SOVEREIGN_MESH binding failure: Host interface %s is unavailable on this OS (%s). "
                    "Silent loopback fallback prohibited by [INV-G4B-HONEST-IPC].",
                    self.host, err,
                )
                raise RuntimeError(
                    f"SOVEREIGN_MESH host interface '{self.host}' is not bound on this OS. "
                    f"Silent loopback fallback prohibited. Use Profile.LOCAL_IPC for local dev."
                ) from err

    async def stop(self) -> None:
        self._running = False
        if self._server:
            self._server.close()
            await self._server.wait_closed()
            self._server = None
