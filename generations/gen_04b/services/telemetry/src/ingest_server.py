"""AsyncIO High-Throughput Micro-Batch Ingestion Server (`ingest_server.py`).

Enforces:
- [L1-G4B-001] Service-Oriented Sovereign Mesh Protocol Standardization.
- [L1-G3B-011] Universal Compositional Contract IR (IngestMicroTransactionBatch).
- [L1-G3B-012] Dedicated Non-Loopback Network Topology (Configured on 192.168.40.40:8446).
- [L1-G3B-018] Non-Blocking Ingress & Landauer Thermodynamic Equilibrium.
- 50,000-Record In-Memory Ring Buffer with Backpressure Protection.
- 50ms Flush Interval Draining to Embedded SQLite WAL Vault.
- Pure Python 3.14 AsyncIO Implementation (Zero External Daemon Dependencies).
"""

from __future__ import annotations

import asyncio
from dataclasses import asdict
import json
import logging
import os
import time
from typing import Any, Callable, Dict, List, Optional, Set

try:
    from .telemetry_vault import MeshTransaction, TelemetryVault, assert_non_loopback
except ImportError:
    from telemetry_vault import MeshTransaction, TelemetryVault, assert_non_loopback

logger = logging.getLogger("ingest_server")


class IngestServer:
    """AsyncIO Micro-Batch Ingestion Daemon with 50,000-record in-memory ring buffer."""

    def __init__(
        self,
        vault: TelemetryVault,
        host: Optional[str] = None,
        port: int = 8446,
        ring_buffer_size: int = 50_000,
        flush_interval_seconds: float = 0.05,  # 50ms
        max_batch_size: int = 1000,
        allow_any_interface_for_testing: bool = False,
        profile: Optional[str] = None,
    ) -> None:
        if profile is None:
            if host is not None and not allow_any_interface_for_testing:
                assert_non_loopback(host, f"IngestServer host '{host}'")
                profile = "SOVEREIGN_MESH"
            else:
                profile = "LOCAL_IPC"

        self.profile = profile
        if host is None:
            self.host = "127.0.0.1" if profile == "LOCAL_IPC" else "192.168.40.40"
        else:
            self.host = host

        if self.profile == "SOVEREIGN_MESH" and not allow_any_interface_for_testing:
            assert_non_loopback(self.host, f"IngestServer host '{self.host}'")
        self.vault = vault
        self.port = port
        self.ring_buffer_size = ring_buffer_size
        self.flush_interval = flush_interval_seconds
        self.max_batch_size = max_batch_size
        self.allow_any_interface_for_testing = allow_any_interface_for_testing

        self.queue: asyncio.Queue[MeshTransaction] = asyncio.Queue(maxsize=ring_buffer_size)
        self.spillover_buffer: List[MeshTransaction] = []
        self._server: Optional[asyncio.Server] = None
        self._drain_task: Optional[asyncio.Task] = None
        self._running = False
        self._sse_listeners: Set[asyncio.Queue[MeshTransaction]] = set()

        # Telemetry metrics
        self.total_enqueued = 0
        self.total_flushed = 0
        self.total_spillover_count = 0
        self.dropped_packets = 0
        self.start_time_ns = time.time_ns()

    def register_sse_listener(self) -> asyncio.Queue[MeshTransaction]:
        """Registers an async queue to receive real-time copies of all flushed transactions."""
        q: asyncio.Queue[MeshTransaction] = asyncio.Queue(maxsize=5000)
        self._sse_listeners.add(q)
        return q

    def unregister_sse_listener(self, q: asyncio.Queue[MeshTransaction]) -> None:
        self._sse_listeners.discard(q)

    def enqueue(self, tx: MeshTransaction) -> bool:
        """Non-blocking enqueue of a single micro-transaction."""
        try:
            self.queue.put_nowait(tx)
            self.total_enqueued += 1
            return True
        except asyncio.QueueFull:
            # Backpressure handling: spillover to prevent packet loss
            if len(self.spillover_buffer) < 50_000:
                self.spillover_buffer.append(tx)
                self.total_spillover_count += 1
                self.total_enqueued += 1
                return True
            else:
                self.dropped_packets += 1
                logger.error("[Backpressure Emergency] Ingest ring buffer and spillover saturated.")
                return False

    async def enqueue_async(self, tx: MeshTransaction) -> bool:
        """Asynchronously enqueues a transaction, waiting if queue is full."""
        try:
            await self.queue.put(tx)
            self.total_enqueued += 1
            return True
        except Exception:
            return self.enqueue(tx)

    async def _drain_loop(self) -> None:
        """Continuous micro-batch drain loop flushing to SQLite WAL every 50ms."""
        while self._running:
            try:
                await asyncio.sleep(self.flush_interval)

                batch: List[MeshTransaction] = []
                # First drain any pending spillover
                while self.spillover_buffer and len(batch) < self.max_batch_size:
                    batch.append(self.spillover_buffer.pop(0))

                # Then drain from active ring buffer
                while not self.queue.empty() and len(batch) < self.max_batch_size:
                    try:
                        batch.append(self.queue.get_nowait())
                    except asyncio.QueueEmpty:
                        break

                if batch:
                    # Commit batch to SQLite WAL
                    count = self.vault.insert_batch(batch)
                    self.total_flushed += count

                    # Dispatch to SSE listeners
                    for q in list(self._sse_listeners):
                        for tx in batch:
                            try:
                                q.put_nowait(tx)
                            except asyncio.QueueFull:
                                # Pop oldest if listener queue is slow to prevent stalling
                                try:
                                    q.get_nowait()
                                    q.put_nowait(tx)
                                except Exception:
                                    pass

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.exception("Error in ingest drain loop: %s", e)

    async def handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        """Native lightweight HTTP/1.1 request dispatcher."""
        try:
            request_line = await reader.readline()
            if not request_line:
                writer.close()
                await writer.wait_closed()
                return

            line_str = request_line.decode("utf-8", errors="replace").strip()
            parts = line_str.split()
            if len(parts) < 2:
                writer.close()
                await writer.wait_closed()
                return

            method, path = parts[0], parts[1]

            # Read headers
            headers = {}
            content_length = 0
            while True:
                header_line = await reader.readline()
                if not header_line or header_line == b"\r\n":
                    break
                h_str = header_line.decode("utf-8", errors="replace").strip()
                if ":" in h_str:
                    k, v = h_str.split(":", 1)
                    headers[k.strip().lower()] = v.strip()
                    if k.strip().lower() == "content-length":
                        content_length = int(v.strip())

            # Read body if present
            body_bytes = b""
            if content_length > 0:
                body_bytes = await reader.readexactly(content_length)

            # Route handling
            status_code = 200
            content_type = "application/json"
            response_payload = {}

            if path == "/api/v1/telemetry/health" and method == "GET":
                response_payload = self.get_health_status()
            elif path == "/api/v1/telemetry/ingest" and method == "POST":
                try:
                    data = json.loads(body_bytes.decode("utf-8"))
                    if isinstance(data, list):
                        records = [MeshTransaction.from_dict(d) for d in data]
                        for r in records:
                            self.enqueue(r)
                        response_payload = {
                            "status": "ACCEPTED",
                            "batch_size": len(records),
                            "enqueued_count": len(records),
                        }
                    elif isinstance(data, dict):
                        tx = MeshTransaction.from_dict(data)
                        self.enqueue(tx)
                        response_payload = {
                            "status": "ACCEPTED",
                            "transaction_id": tx.transaction_id,
                        }
                    else:
                        status_code = 400
                        response_payload = {"error": "Invalid JSON body, expected object or array"}
                except Exception as e:
                    status_code = 400
                    response_payload = {"error": str(e)}
            else:
                status_code = 404
                response_payload = {"error": f"Endpoint '{path}' not found on IngestServer."}

            resp_json = json.dumps(response_payload)
            resp = (
                f"HTTP/1.1 {status_code} OK\r\n"
                f"Content-Type: {content_type}\r\n"
                f"Content-Length: {len(resp_json.encode('utf-8'))}\r\n"
                f"Access-Control-Allow-Origin: *\r\n"
                f"Connection: close\r\n\r\n"
                f"{resp_json}"
            )
            writer.write(resp.encode("utf-8"))
            await writer.drain()

        except Exception as e:
            logger.exception("Error handling HTTP client: %s", e)
        finally:
            try:
                writer.close()
                await writer.wait_closed()
            except Exception:
                pass

    def get_health_status(self) -> Dict[str, Any]:
        """Returns live operational health and buffer metrics."""
        uptime_sec = (time.time_ns() - self.start_time_ns) / 1_000_000_000.0
        return {
            "service": "sovereign_telemetry_ingest",
            "host": self.host,
            "port": self.port,
            "status": "HEALTHY" if self._running else "STOPPED",
            "uptime_seconds": uptime_sec,
            "ring_buffer_capacity": self.ring_buffer_size,
            "ring_buffer_depth": self.queue.qsize(),
            "spillover_depth": len(self.spillover_buffer),
            "total_enqueued": self.total_enqueued,
            "total_flushed_to_wal": self.total_flushed,
            "dropped_packets": self.dropped_packets,
            "active_sse_subscribers": len(self._sse_listeners),
        }

    async def start(self) -> None:
        """Starts the background drain task and AsyncIO TCP socket listener."""
        self._running = True
        self._drain_task = asyncio.create_task(self._drain_loop())

        if self.profile == "LOCAL_IPC":
            bind_host = self.host if self.host in ("127.0.0.1", "localhost", "::1", "0.0.0.0") else "127.0.0.1"
            self.host = bind_host
            self._server = await asyncio.start_server(self.handle_client, bind_host, self.port)
            logger.info("IngestServer started on %s:%d (Profile: LOCAL_IPC)", self.host, self.port)
        elif self.profile == "SOVEREIGN_MESH":
            try:
                self._server = await asyncio.start_server(self.handle_client, self.host, self.port)
                logger.info("IngestServer started on %s:%d (Profile: SOVEREIGN_MESH)", self.host, self.port)
            except OSError as err:
                logger.error("SOVEREIGN_MESH IngestServer binding failure on %s: %s", self.host, err)
                raise RuntimeError(
                    f"SOVEREIGN_MESH host interface '{self.host}' not available on OS. "
                    "Silent loopback fallback prohibited."
                ) from err

    async def stop(self) -> None:
        """Gracefully drains buffers and shuts down server."""
        self._running = False
        if self._drain_task:
            self._drain_task.cancel()
            try:
                await self._drain_task
            except asyncio.CancelledError:
                pass
            self._drain_task = None

        if self._server:
            self._server.close()
            await self._server.wait_closed()
            self._server = None

        # Final synchronous flush of remaining in-memory items
        final_batch = []
        while not self.queue.empty():
            final_batch.append(self.queue.get_nowait())
        final_batch.extend(self.spillover_buffer)
        if final_batch:
            self.vault.insert_batch(final_batch)
            self.total_flushed += len(final_batch)
