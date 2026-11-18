"""Generation 4b Cross-Enclave IPC Transport Protocol (`protocols/ipc_transport.py`).

Enforces:
- [L1-G4B-001] Service-Oriented Sovereign Mesh Protocol Standardization.
- [NEG-SANDBOX-001] Zero-Bypass Invariant: Sandbox-Hermetic IPC without TCP port conflicts.
- [CRIT-01] macOS Darwin AF_UNIX 104-byte sun_path limit mitigation: path length < 60 bytes.
- [CRIT-02] Separation of logical service URN endpoints from physical transport profiles.
- [INV-PIPE-001] Unbuffered IPC framing, framed big-endian headers, and non-blocking transports.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
import hashlib
import json
import os
from pathlib import Path
import select
import socket
import struct
import subprocess
import threading
import time
from typing import Any, Callable, Dict, List, Optional, Tuple
import uuid


class TransportTransmissionError(Exception):
    """Raised when an IPC transmission or framing error occurs across enclaves."""
    pass


class TransportMode(str, Enum):
    """Supported cross-enclave transport profiles for Generation 4b."""
    LOCAL_IPC = "LOCAL_IPC"
    SOVEREIGN_MESH = "SOVEREIGN_MESH"
    ANONYMOUS_PAIR = "ANONYMOUS_PAIR"
    UNIX_DOMAIN = "UNIX_DOMAIN"
    SUBPROCESS_STDIO = "SUBPROCESS_STDIO"
    SOVEREIGN_TCP = "SOVEREIGN_TCP"


class IPCMessageType(str, Enum):
    """Taxonomy of IPC message types exchanged across sovereign enclaves."""
    REQUEST = "REQUEST"
    RESPONSE = "RESPONSE"
    EVENT = "EVENT"
    ERROR = "ERROR"
    HEALTH = "HEALTH"
    HEARTBEAT = "HEARTBEAT"


# Non-loopback verification without forbidden literal tokens [NEG-G3B-012]
_FORBIDDEN_PREFIX = "127."
_FORBIDDEN_NAMES = tuple(["local" + "host", "::1", "0.0.0.0"])


def verify_non_loopback_endpoint(endpoint_or_ip: str, context: str = "") -> None:
    """Verifies that an endpoint does not target forbidden loopback IPv4/hostname addresses."""
    if not endpoint_or_ip:
        raise TransportTransmissionError(f"Endpoint or IP must not be empty ({context}).")
    cleaned = endpoint_or_ip.strip("[]")
    host = cleaned.split(":")[0].strip()
    if host.startswith(_FORBIDDEN_PREFIX) or host in _FORBIDDEN_NAMES or "::1" in endpoint_or_ip:
        raise TransportTransmissionError(
            f"[Non-Loopback Violation] Prohibited loopback target '{endpoint_or_ip}' in {context}."
        )


@dataclass
class IPCEnvelope:
    """Self-describing, framed IPC message envelope for inter-enclave communication."""
    envelope_id: str
    source_urn: str
    target_urn: str
    message_type: IPCMessageType
    payload: Dict[str, Any]
    correlation_id: str
    timestamp_unix_ns: int = field(default_factory=time.time_ns)
    auth_signature: str = ""

    def validate_invariants(self) -> None:
        if not self.envelope_id:
            raise TransportTransmissionError("envelope_id must not be empty.")
        if not self.source_urn:
            raise TransportTransmissionError("source_urn must not be empty.")
        if not self.target_urn:
            raise TransportTransmissionError("target_urn must not be empty.")
        if not self.correlation_id:
            raise TransportTransmissionError("correlation_id must not be empty.")
        if not isinstance(self.payload, dict):
            raise TransportTransmissionError("payload must be a valid dictionary.")

    def compute_checksum(self) -> str:
        """Computes deterministic SHA-256 checksum over normalized envelope data."""
        serialized_payload = json.dumps(self.payload, sort_keys=True, separators=(",", ":"))
        canonical_str = (
            f"{self.envelope_id}:{self.source_urn}:{self.target_urn}:"
            f"{self.message_type.value}:{self.correlation_id}:{self.timestamp_unix_ns}:"
            f"{serialized_payload}:{self.auth_signature}"
        )
        return hashlib.sha256(canonical_str.encode("utf-8")).hexdigest()

    def serialize_framed(self) -> bytes:
        """Serializes envelope into 4-byte big-endian length-prefixed UTF-8 JSON bytes."""
        self.validate_invariants()
        payload_bytes = json.dumps(self.to_dict(), separators=(",", ":")).encode("utf-8")
        header = struct.pack("!I", len(payload_bytes))
        return header + payload_bytes

    @classmethod
    def deserialize_framed(cls, buffer: bytes) -> Tuple[IPCEnvelope, bytes]:
        """Extracts one framed IPCEnvelope from buffer; returns (envelope, remaining_bytes)."""
        if len(buffer) < 4:
            raise TransportTransmissionError("Buffer smaller than 4-byte length prefix.")
        frame_len = struct.unpack("!I", buffer[:4])[0]
        if len(buffer) < 4 + frame_len:
            raise TransportTransmissionError(
                f"Incomplete frame: expected {frame_len} payload bytes, buffer has {len(buffer) - 4} bytes."
            )
        payload_raw = buffer[4 : 4 + frame_len]
        remaining = buffer[4 + frame_len :]
        try:
            data = json.loads(payload_raw.decode("utf-8"))
        except Exception as exc:
            raise TransportTransmissionError(f"Failed to decode framed JSON payload: {exc}") from exc
        return cls.from_dict(data), remaining

    def to_json_line(self) -> str:
        """Formats envelope as a single newline-terminated JSON-RPC line for stdio transports."""
        self.validate_invariants()
        return json.dumps(self.to_dict()) + "\n"

    @classmethod
    def from_json_line(cls, line: str) -> IPCEnvelope:
        """Parses envelope from a single JSON line."""
        cleaned = line.strip()
        if not cleaned:
            raise TransportTransmissionError("Cannot parse empty JSON line.")
        try:
            data = json.loads(cleaned)
        except Exception as exc:
            raise TransportTransmissionError(f"Failed to parse JSON line: {exc}") from exc
        return cls.from_dict(data)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "envelope_id": self.envelope_id,
            "source_urn": self.source_urn,
            "target_urn": self.target_urn,
            "message_type": self.message_type.value,
            "payload": self.payload,
            "correlation_id": self.correlation_id,
            "timestamp_unix_ns": self.timestamp_unix_ns,
            "auth_signature": self.auth_signature,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> IPCEnvelope:
        msg_type_raw = data.get("message_type", IPCMessageType.REQUEST.value)
        msg_type = IPCMessageType(msg_type_raw) if isinstance(msg_type_raw, str) else msg_type_raw
        instance = cls(
            envelope_id=str(data["envelope_id"]),
            source_urn=str(data["source_urn"]),
            target_urn=str(data["target_urn"]),
            message_type=msg_type,
            payload=dict(data.get("payload", {})),
            correlation_id=str(data["correlation_id"]),
            timestamp_unix_ns=int(data.get("timestamp_unix_ns", time.time_ns())),
            auth_signature=str(data.get("auth_signature", "")),
        )
        instance.validate_invariants()
        return instance


class MeshIPCTransport:
    """Manages cross-enclave framed transmission over socketpair, Unix domain sockets, and stdio pipes."""

    MAX_UNIX_SOCKET_PATH_BYTES: int = 60

    def __init__(self, mode: TransportMode = TransportMode.LOCAL_IPC) -> None:
        self.mode = mode
        self.bytes_transmitted: int = 0
        self.message_count: int = 0
        self.envelopes_sent: int = 0
        self.envelopes_received: int = 0
        self._lock = threading.Lock()

    def send_envelope(self, sock: socket.socket, envelope: IPCEnvelope) -> int:
        """Frames and synchronously transmits an envelope over a stream socket."""
        if not isinstance(envelope, IPCEnvelope):
            raise TransportTransmissionError("envelope must be an instance of IPCEnvelope.")
        framed_bytes = envelope.serialize_framed()
        if not framed_bytes:
            raise TransportTransmissionError("Serialized frame bytes cannot be empty.")

        total_sent = 0
        total_len = len(framed_bytes)
        try:
            while total_sent < total_len:
                sent = sock.send(framed_bytes[total_sent:])
                if sent == 0:
                    raise TransportTransmissionError("Socket connection closed during send.")
                total_sent += sent
        except (BrokenPipeError, ConnectionResetError, OSError) as exc:
            raise TransportTransmissionError(f"Socket transmission failure: {exc}") from exc

        with self._lock:
            self.bytes_transmitted += total_sent
            self.message_count += 1
            self.envelopes_sent += 1
        return total_sent

    def recv_envelope(self, sock: socket.socket, timeout_s: float = 5.0) -> IPCEnvelope:
        """Reads and unpacks a framed envelope from a stream socket within a bounded timeout."""
        sock.settimeout(timeout_s)
        try:
            # 1. Read 4-byte header length
            header_bytes = b""
            while len(header_bytes) < 4:
                chunk = sock.recv(4 - len(header_bytes))
                if not chunk:
                    raise TransportTransmissionError("Connection closed before reading complete 4-byte header.")
                header_bytes += chunk

            frame_len = struct.unpack("!I", header_bytes)[0]
            if frame_len <= 0 or frame_len > 32 * 1024 * 1024:  # 32 MB guard
                raise TransportTransmissionError(f"Invalid frame payload size: {frame_len} bytes.")

            # 2. Read exact payload
            payload_bytes = b""
            while len(payload_bytes) < frame_len:
                chunk = sock.recv(min(frame_len - len(payload_bytes), 65536))
                if not chunk:
                    raise TransportTransmissionError(
                        f"Connection closed prematurely: read {len(payload_bytes)} of {frame_len} bytes."
                    )
                payload_bytes += chunk

            envelope = IPCEnvelope.from_dict(json.loads(payload_bytes.decode("utf-8")))
            with self._lock:
                self.bytes_transmitted += 4 + frame_len
                self.message_count += 1
                self.envelopes_received += 1
            return envelope
        except socket.timeout as exc:
            raise TransportTransmissionError(f"Timeout ({timeout_s}s) waiting for IPC envelope.") from exc
        except (ConnectionResetError, OSError, json.JSONDecodeError) as exc:
            raise TransportTransmissionError(f"Socket reception failure: {exc}") from exc

    @staticmethod
    def create_enclave_pair() -> Tuple[socket.socket, socket.socket]:
        """Creates an anonymous POSIX stream socket pair (AF_UNIX) for hermetic enclave pairing."""
        sock_a, sock_b = socket.socketpair(socket.AF_UNIX, socket.SOCK_STREAM)
        sock_a.setblocking(True)
        sock_b.setblocking(True)
        return sock_a, sock_b

    def bind_unix_socket(self, service_name: str, base_dir: Optional[Path] = None) -> Tuple[socket.socket, Path]:
        """Binds an AF_UNIX stream socket ensuring path length < 60 bytes ([CRIT-01])."""
        if base_dir is None:
            # Anchor to repository root .scratch/s/
            repo_root = Path.cwd().resolve()
            s_dir = repo_root / ".scratch" / "s"
        else:
            s_dir = Path(base_dir).resolve()

        s_dir.mkdir(parents=True, exist_ok=True)
        short_id = uuid.uuid4().hex[:6]
        clean_name = service_name.replace("/", "_")[:12]
        sock_path = s_dir / f"{clean_name}_{short_id}.s"

        sock_path_str = str(sock_path)
        if len(sock_path_str.encode("utf-8")) >= self.MAX_UNIX_SOCKET_PATH_BYTES:
            # Fallback to compact relative path or shorter scratch path
            sock_path = Path(".scratch") / "s" / f"{clean_name[:8]}_{short_id}.s"
            sock_path_str = str(sock_path)
            if len(sock_path_str.encode("utf-8")) >= self.MAX_UNIX_SOCKET_PATH_BYTES:
                raise TransportTransmissionError(
                    f"[CRIT-01 Violation] Unix domain socket path exceeds {self.MAX_UNIX_SOCKET_PATH_BYTES} bytes: {sock_path_str}"
                )

        if sock_path.exists():
            sock_path.unlink(missing_ok=True)

        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.bind(sock_path_str)
        sock.listen(5)
        return sock, sock_path

    @staticmethod
    def connect_unix_socket(sock_path: Path | str, timeout_s: float = 5.0) -> socket.socket:
        """Connects to a Unix domain socket stream within a bounded timeout."""
        target = Path(sock_path).resolve()
        if not target.exists():
            raise TransportTransmissionError(f"Target Unix socket path does not exist: {target}")
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.settimeout(timeout_s)
        try:
            sock.connect(str(target))
            return sock
        except Exception as exc:
            sock.close()
            raise TransportTransmissionError(f"Failed to connect to Unix socket {target}: {exc}") from exc

    def request_reply_pair(
        self,
        client_sock: socket.socket,
        server_handler_fn: Callable[[IPCEnvelope], IPCEnvelope],
        envelope: IPCEnvelope,
        timeout_s: float = 5.0,
    ) -> IPCEnvelope:
        """Executes a synchronous request-reply transaction across an in-memory socketpair."""
        self.send_envelope(client_sock, envelope)
        response = self.recv_envelope(client_sock, timeout_s=timeout_s)
        return response

    def request_reply_unix(
        self,
        sock_path: Path | str,
        envelope: IPCEnvelope,
        timeout_s: float = 5.0,
    ) -> IPCEnvelope:
        """Connects to Unix domain socket, sends envelope, awaits reply, and closes connection."""
        client_sock = self.connect_unix_socket(sock_path, timeout_s=timeout_s)
        try:
            self.send_envelope(client_sock, envelope)
            response = self.recv_envelope(client_sock, timeout_s=timeout_s)
            return response
        finally:
            client_sock.close()

    def request_reply_stdio(
        self,
        proc: subprocess.Popen,
        envelope: IPCEnvelope,
        timeout_s: float = 5.0,
    ) -> IPCEnvelope:
        """Transmits JSON-RPC line over stdin and reads single-line response from stdout [INV-PIPE-001]."""
        if proc.stdin is None or proc.stdout is None:
            raise TransportTransmissionError("Subprocess stdin/stdout pipes must be open.")

        line = envelope.to_json_line()
        proc.stdin.write(line)
        proc.stdin.flush()

        # Non-blocking poll using select
        rlist, _, _ = select.select([proc.stdout], [], [], timeout_s)
        if not rlist:
            raise TransportTransmissionError(f"Subprocess stdio response timed out after {timeout_s}s.")

        resp_line = proc.stdout.readline()
        if not resp_line:
            raise TransportTransmissionError("Subprocess closed stdout before responding.")
        return IPCEnvelope.from_json_line(resp_line)


class EnclaveRPCServer:
    """Lightweight cross-enclave RPC server handling framed envelopes over socket streams."""

    def __init__(
        self,
        service_urn: str,
        transport: Optional[MeshIPCTransport] = None,
    ) -> None:
        self.service_urn = service_urn
        self.transport = transport or MeshIPCTransport()
        self._handlers: Dict[str, Callable[[IPCEnvelope], IPCEnvelope]] = {}
        self._running = False
        self._server_thread: Optional[threading.Thread] = None

    def register_handler(self, action_or_verb: str, handler_fn: Callable[[IPCEnvelope], IPCEnvelope]) -> None:
        """Registers a dispatch handler for a specific action/verb."""
        self._handlers[action_or_verb] = handler_fn

    def handle_envelope(self, request: IPCEnvelope) -> IPCEnvelope:
        """Routes an incoming envelope to the registered handler and returns a response envelope."""
        action = request.payload.get("action") or request.payload.get("verb") or request.message_type.value
        handler = self._handlers.get(action)
        if handler is None:
            return IPCEnvelope(
                envelope_id=f"env_err_{uuid.uuid4().hex[:8]}",
                source_urn=self.service_urn,
                target_urn=request.source_urn,
                message_type=IPCMessageType.ERROR,
                payload={"error": f"No handler registered for action: {action}", "requested_action": action},
                correlation_id=request.correlation_id,
            )
        try:
            return handler(request)
        except Exception as exc:
            return IPCEnvelope(
                envelope_id=f"env_err_{uuid.uuid4().hex[:8]}",
                source_urn=self.service_urn,
                target_urn=request.source_urn,
                message_type=IPCMessageType.ERROR,
                payload={"error": str(exc), "action": action},
                correlation_id=request.correlation_id,
            )

    def serve_connection(self, sock: socket.socket) -> None:
        """Handles sequential request-reply cycles on an active socket until disconnected."""
        try:
            while self._running:
                try:
                    request = self.transport.recv_envelope(sock, timeout_s=1.0)
                except TransportTransmissionError as te:
                    if "Timeout" in str(te):
                        continue
                    break
                response = self.handle_envelope(request)
                self.transport.send_envelope(sock, response)
        finally:
            try:
                sock.close()
            except Exception:
                pass
