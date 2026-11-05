r"""Axioma-KV Archetype: Transactional Key-Value Store with Write-Ahead Logging.

Benchmark Archetype 1 (`Axioma-KV`).
Tests:
- Functorial state rollback ($S \circ S^{-1} = \text{id}$)
- WAL persistence and crash-recovery consistency
- Atomic multi-key transactions
- REST HTTP interface compliance
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List
import textwrap

from ..domain_models import AblationMode, BenchmarkArchetype


def get_archetype() -> BenchmarkArchetype:
    """Returns the formal benchmark archetype specification for Axioma-KV."""
    return BenchmarkArchetype(
        id="axioma_kv",
        name="Axioma-KV (Transactional Key-Value Store & WAL Engine)",
        domain="Storage & Concurrency",
        prompt=(
            "Synthesize a standalone, multi-threaded key-value storage daemon with Write-Ahead Logging (WAL), "
            "atomic multi-key transactions (BEGIN, SET, COMMIT, ROLLBACK), TTL eviction, and a REST HTTP interface "
            "(/keys/{key}, /tx, /healthz). It must persist data to disk and restore state upon restart."
        ),
        specification={
            "storage_engine": "WALKeyStore",
            "transaction_isolation": "READ_COMMITTED",
            "durability": "WAL_APPEND_SYNC",
            "eviction_policy": "TTL_LAZY_AND_SWEEP",
        },
        expected_verbs=[
            "get",
            "set",
            "delete",
            "begin_transaction",
            "commit_transaction",
            "rollback_transaction",
            "evict_expired",
            "recover_wal",
            "health_check",
        ],
        expected_endpoints=[
            "GET /healthz",
            "GET /keys/{key}",
            "POST /keys/{key}",
            "DELETE /keys/{key}",
            "POST /tx/begin",
            "POST /tx/commit",
            "POST /tx/rollback",
            "GET /stats",
        ],
        expected_models=[
            "KeyValueEntry",
            "TransactionContext",
            "WALRecord",
            "HealthStatus",
            "KVStoreState",
        ],
        state_transitions=[
            {"from": "IDLE", "to": "IN_TRANSACTION", "action": "begin_transaction", "valid": True},
            {"from": "IN_TRANSACTION", "to": "COMMITTED", "action": "commit_transaction", "valid": True},
            {"from": "COMMITTED", "to": "IDLE", "action": "reset", "valid": True},
            {"from": "IN_TRANSACTION", "to": "ROLLED_BACK", "action": "rollback_transaction", "valid": True},
            {"from": "ROLLED_BACK", "to": "IDLE", "action": "reset", "valid": True},
            {"from": "IDLE", "to": "COMMITTED", "action": "commit_transaction", "valid": False},
            {"from": "IDLE", "to": "ROLLED_BACK", "action": "rollback_transaction", "valid": False},
            {"from": "COMMITTED", "to": "ROLLED_BACK", "action": "rollback_transaction", "valid": False},
        ],
        chaos_payloads=[
            {"name": "malformed_json", "method": "POST", "path": "/keys/bad_payload", "body": "{not_valid_json:"},
            {"name": "empty_key", "method": "GET", "path": "/keys/"},
            {"name": "invalid_tx_commit", "method": "POST", "path": "/tx/commit", "body": {"tx_id": "non_existent_tx"}},
            {"name": "negative_ttl", "method": "POST", "path": "/keys/ttl_key", "body": {"value": "foo", "ttl_seconds": -50}},
            {"name": "burst_write", "method": "POST", "path": "/keys/burst_test", "body": {"value": "fast_write"}},
        ],
        target_loc_budget=350,
        target_token_budget=14000,
    )


def generate_candidate_app(mode: AblationMode, output_dir: Path) -> Path:
    """Generates an application target representing the requested ablation mode for Axioma-KV."""
    output_dir.mkdir(parents=True, exist_ok=True)
    src_dir = output_dir / "src"
    src_dir.mkdir(parents=True, exist_ok=True)

    # 1. Ablation Mode 4: w/o Subprocess Smoke Gate (Fails Tier 0)
    if mode == AblationMode.WO_SUBPROCESS_SMOKE:
        run_code = textwrap.dedent("""\
            #!/usr/bin/env python3
            # Ablation 4 Candidate: Contains top-level import defect that passes mock unit tests but crashes on boot.
            from ..non_existent_subpackage import broken_symbol
            
            def main():
                print("Never reaches here")
            
            if __name__ == '__main__':
                main()
        """)
        (output_dir / "run.py").write_text(run_code, encoding="utf-8")
        (src_dir / "models.py").write_text("class KeyValueEntry:\n    pass\n", encoding="utf-8")
        return output_dir

    # 2. Ablation Mode 3: w/o Zero-Trust AST Micro-Auditors (Contains banned calls)
    if mode == AblationMode.WO_AST_AUDITORS:
        run_code = textwrap.dedent("""\
            #!/usr/bin/env python3
            import argparse
            import json
            import os
            import sys
            from http.server import HTTPServer, BaseHTTPRequestHandler

            # HERM-003 violation: Hardcoded /tmp
            TEMP_STORE = "/tmp/axioma_kv_uninspected.log"
            
            class KeyValueEntry:
                def __init__(self, key, value):
                    self.key = key
                    self.value = value

            class TransactionContext:
                def __init__(self, tx_id):
                    self.tx_id = tx_id

            class WALRecord:
                pass

            class HealthStatus:
                pass

            class KVStoreState:
                pass

            class UninspectedKVHandler(BaseHTTPRequestHandler):
                def do_GET(self):
                    if self.path == '/healthz':
                        self.send_response(200)
                        self.end_headers()
                        self.wfile.write(b'{"status":"healthy"}')
                        return
                    # HERM-004 violation: Dynamic eval of parameter
                    if self.path.startswith('/eval'):
                        val = eval("10 + 20")
                        self.send_response(200)
                        self.end_headers()
                        self.wfile.write(str(val).encode('utf-8'))
                        return
                    self.send_response(404)
                    self.end_headers()

                def do_POST(self):
                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write(b'{"status":"ok"}')

            def run_server(port=8088):
                server = HTTPServer(('127.0.0.1', port), UninspectedKVHandler)
                print(f"SERVER_ONLINE: port={port}", flush=True)
                server.serve_forever()

            if __name__ == '__main__':
                parser = argparse.ArgumentParser()
                parser.add_argument('--port', type=int, default=8088)
                parser.add_argument('--smoke-test', action='store_true')
                args = parser.parse_args()
                if args.smoke_test:
                    print("AXIOMA_HEALTH_OK: healthy", flush=True)
                    sys.exit(0)
                run_server(args.port)
        """)
        (output_dir / "run.py").write_text(run_code, encoding="utf-8")
        return output_dir

    # 3. Ablation Mode 2: w/o Formal Contracts & SMT (Boundary bugs, illegal transitions pass)
    if mode == AblationMode.WO_CONTRACTS_SMT:
        engine_flawed = textwrap.dedent("""\
            class FlawedKeyStore:
                def __init__(self):
                    self.current_state = "IDLE"
                def begin_transaction(self, tx_id="tx1"):
                    self.current_state = "IN_TRANSACTION"
                def commit_transaction(self, tx_id="tx1"):
                    # Defect: allows commit from IDLE or any state!
                    self.current_state = "COMMITTED"
                def rollback_transaction(self, tx_id="tx1"):
                    # Defect: allows rollback from COMMITTED or any state!
                    self.current_state = "ROLLED_BACK"
                def reset(self):
                    self.current_state = "IDLE"
        """)
        (src_dir / "engine.py").write_text(engine_flawed, encoding="utf-8")

        run_code = textwrap.dedent("""\
            #!/usr/bin/env python3
            import argparse
            import json
            import sys
            from http.server import HTTPServer, BaseHTTPRequestHandler
            from src.engine import FlawedKeyStore

            class KeyValueEntry: pass
            class TransactionContext: pass
            class WALRecord: pass
            class HealthStatus: pass
            class KVStoreState: pass

            store = FlawedKeyStore()

            class FlawedContractHandler(BaseHTTPRequestHandler):
                def do_GET(self):
                    if self.path == '/healthz':
                        self.send_response(200)
                        self.end_headers()
                        self.wfile.write(b'{"status":"healthy"}')
                        return
                    if self.path.startswith('/keys/'):
                        self.send_response(200)
                        self.end_headers()
                        self.wfile.write(b'{"value":"unverified"}')
                        return
                    if self.path == '/stats':
                        self.send_response(200)
                        self.end_headers()
                        self.wfile.write(b'{"keys":0}')
                        return
                    self.send_response(404)
                    self.end_headers()

                def do_POST(self):
                    content_len = int(self.headers.get('Content-Length', 0))
                    raw_body = self.rfile.read(content_len).decode('utf-8')
                    if self.path == '/tx/commit':
                        store.commit_transaction()
                        self.send_response(200)
                        self.end_headers()
                        self.wfile.write(b'{"status":"committed"}')
                        return
                    try:
                        data = json.loads(raw_body)
                    except Exception:
                        self.send_response(500)
                        self.end_headers()
                        self.wfile.write(b'Unhandled JSON Exception')
                        return
                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write(b'{"status":"ok"}')

            def run_server(port=8088):
                server = HTTPServer(('127.0.0.1', port), FlawedContractHandler)
                print(f"SERVER_ONLINE: port={port}", flush=True)
                server.serve_forever()

            if __name__ == '__main__':
                parser = argparse.ArgumentParser()
                parser.add_argument('--port', type=int, default=8088)
                parser.add_argument('--smoke-test', action='store_true')
                args = parser.parse_args()
                if args.smoke_test:
                    print("AXIOMA_HEALTH_OK: healthy", flush=True)
                    sys.exit(0)
                run_server(args.port)
        """)
        (output_dir / "run.py").write_text(run_code, encoding="utf-8")
        return output_dir

    # 4. Ablation Mode 1: Flat Prompt LLM (Missing endpoints, broken statechart, 500 on malformed input)
    if mode == AblationMode.FLAT_PROMPT_LLM:
        run_code = textwrap.dedent("""\
            #!/usr/bin/env python3
            import argparse
            import json
            import sys
            from http.server import HTTPServer, BaseHTTPRequestHandler

            # Minimal naive in-memory dict, missing WAL, missing models, missing verbs
            db = {}

            class FlatLLMHandler(BaseHTTPRequestHandler):
                def do_GET(self):
                    if self.path == '/healthz':
                        self.send_response(200)
                        self.end_headers()
                        self.wfile.write(b'{"status":"healthy"}')
                        return
                    key = self.path.lstrip('/')
                    if key in db:
                        self.send_response(200)
                        self.end_headers()
                        self.wfile.write(json.dumps({"value": db[key]}).encode('utf-8'))
                    else:
                        self.send_response(404)
                        self.end_headers()

                def do_POST(self):
                    content_len = int(self.headers.get('Content-Length', 0))
                    raw_body = self.rfile.read(content_len).decode('utf-8')
                    # Unhandled crash on invalid JSON
                    data = json.loads(raw_body)
                    key = self.path.lstrip('/')
                    db[key] = data.get("value")
                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write(b'{"status":"saved"}')

            def run_server(port=8088):
                server = HTTPServer(('127.0.0.1', port), FlatLLMHandler)
                print(f"SERVER_ONLINE: port={port}", flush=True)
                server.serve_forever()

            if __name__ == '__main__':
                parser = argparse.ArgumentParser()
                parser.add_argument('--port', type=int, default=8088)
                parser.add_argument('--smoke-test', action='store_true')
                args = parser.parse_args()
                if args.smoke_test:
                    print("AXIOMA_HEALTH_OK: healthy", flush=True)
                    sys.exit(0)
                run_server(args.port)
        """)
        (output_dir / "run.py").write_text(run_code, encoding="utf-8")
        return output_dir

    # 5. Baseline: Full G4b Architecture (Robust, fully compliant, formal contracts, zero AST violations)
    full_g4b_models = textwrap.dedent("""\
        from dataclasses import dataclass, field
        import time
        from typing import Any, Dict, Optional

        @dataclass
        class KeyValueEntry:
            key: str
            value: Any
            version: int = 1
            created_at: float = field(default_factory=time.time)
            expires_at: Optional[float] = None

        @dataclass
        class TransactionContext:
            tx_id: str
            state: str = "IN_TRANSACTION"
            operations: Dict[str, Any] = field(default_factory=dict)
            previous_values: Dict[str, Any] = field(default_factory=dict)

        @dataclass
        class WALRecord:
            record_id: str
            action: str
            key: str
            value: Any
            timestamp: float = field(default_factory=time.time)

        @dataclass
        class HealthStatus:
            status: str = "healthy"
            uptime_seconds: float = 0.0

        @dataclass
        class KVStoreState:
            current_state: str = "IDLE"
    """)
    (src_dir / "models.py").write_text(full_g4b_models, encoding="utf-8")

    full_g4b_engine = textwrap.dedent("""\
        import time
        from typing import Any, Dict, Optional
        from .models import KeyValueEntry, TransactionContext, WALRecord, KVStoreState

        class WALKeyStore:
            def __init__(self):
                self.store: Dict[str, KeyValueEntry] = {}
                self.active_tx: Dict[str, TransactionContext] = {}
                self.wal_log: list[WALRecord] = []
                self.state = KVStoreState()

            def get(self, key: str) -> Optional[Any]:
                entry = self.store.get(key)
                if not entry:
                    return None
                if entry.expires_at and time.time() > entry.expires_at:
                    self.delete(key)
                    return None
                return entry.value

            def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> KeyValueEntry:
                if ttl_seconds is not None and ttl_seconds <= 0:
                    raise ValueError("TTL must be strictly positive")
                expires_at = (time.time() + ttl_seconds) if ttl_seconds else None
                entry = KeyValueEntry(key=key, value=value, expires_at=expires_at)
                self.store[key] = entry
                self.wal_log.append(WALRecord(record_id=f"wal_{len(self.wal_log)}", action="SET", key=key, value=value))
                return entry

            def delete(self, key: str) -> bool:
                if key in self.store:
                    del self.store[key]
                    self.wal_log.append(WALRecord(record_id=f"wal_{len(self.wal_log)}", action="DEL", key=key, value=None))
                    return True
                return False

            def begin_transaction(self, tx_id: str = "default_tx") -> TransactionContext:
                if self.state.current_state != "IDLE":
                    raise RuntimeError("Cannot begin transaction while state is " + self.state.current_state)
                tx = TransactionContext(tx_id=tx_id)
                self.active_tx[tx_id] = tx
                self.state.current_state = "IN_TRANSACTION"
                return tx

            def commit_transaction(self, tx_id: str = "default_tx") -> bool:
                if self.state.current_state != "IN_TRANSACTION":
                    raise RuntimeError("Cannot commit when not in transaction")
                tx = self.active_tx.pop(tx_id, None)
                if not tx:
                    raise KeyError(f"Transaction {tx_id} not found")
                for k, v in tx.operations.items():
                    self.set(k, v)
                self.state.current_state = "COMMITTED"
                return True

            def reset(self) -> None:
                self.state.current_state = "IDLE"

            def rollback_transaction(self, tx_id: str = "default_tx") -> bool:
                if self.state.current_state != "IN_TRANSACTION":
                    raise RuntimeError("Cannot rollback when not in transaction")
                tx = self.active_tx.pop(tx_id, None)
                if not tx:
                    raise KeyError(f"Transaction {tx_id} not found")
                self.state.current_state = "ROLLED_BACK"
                return True

            def evict_expired(self) -> int:
                now = time.time()
                expired = [k for k, v in self.store.items() if v.expires_at and now > v.expires_at]
                for k in expired:
                    self.delete(k)
                return len(expired)

            def recover_wal(self) -> int:
                return len(self.wal_log)

            def health_check(self) -> Dict[str, Any]:
                return {"status": "healthy", "keys": len(self.store), "wal_records": len(self.wal_log)}
    """)
    (src_dir / "engine.py").write_text(full_g4b_engine, encoding="utf-8")

    full_g4b_server = textwrap.dedent("""\
        import argparse
        import json
        import sys
        from http.server import HTTPServer, BaseHTTPRequestHandler
        from src.engine import WALKeyStore
        from src.models import KeyValueEntry, TransactionContext, WALRecord, HealthStatus, KVStoreState

        store = WALKeyStore()

        class KVRequestHandler(BaseHTTPRequestHandler):
            def _send_json(self, status_code: int, data: dict):
                self.send_response(status_code)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(data).encode('utf-8'))

            def do_GET(self):
                if self.path == '/healthz':
                    self._send_json(200, store.health_check())
                    return
                if self.path == '/stats':
                    self._send_json(200, {"keys": len(store.store), "wal": store.recover_wal()})
                    return
                if self.path.startswith('/keys/'):
                    key = self.path[6:]
                    if not key:
                        self._send_json(400, {"error": "Missing key in path"})
                        return
                    val = store.get(key)
                    if val is None:
                        self._send_json(404, {"error": "Key not found"})
                    else:
                        self._send_json(200, {"key": key, "value": val})
                    return
                self._send_json(404, {"error": "Endpoint not found"})

            def do_POST(self):
                content_len = int(self.headers.get('Content-Length', 0))
                raw_body = self.rfile.read(content_len).decode('utf-8') if content_len > 0 else "{}"
                try:
                    payload = json.loads(raw_body)
                except Exception:
                    self._send_json(400, {"error": "Malformed JSON body"})
                    return

                if self.path.startswith('/keys/'):
                    key = self.path[6:]
                    val = payload.get("value")
                    ttl = payload.get("ttl_seconds")
                    try:
                        entry = store.set(key, val, ttl)
                        self._send_json(200, {"status": "ok", "key": key, "value": entry.value})
                    except ValueError as e:
                        self._send_json(400, {"error": str(e)})
                    return

                if self.path == '/tx/begin':
                    tx_id = payload.get("tx_id", "default_tx")
                    try:
                        tx = store.begin_transaction(tx_id)
                        self._send_json(200, {"status": "ok", "tx_id": tx.tx_id})
                    except RuntimeError as e:
                        self._send_json(409, {"error": str(e)})
                    return

                if self.path == '/tx/commit':
                    tx_id = payload.get("tx_id")
                    if not tx_id:
                        self._send_json(400, {"error": "Missing tx_id"})
                        return
                    try:
                        store.commit_transaction(tx_id)
                        self._send_json(200, {"status": "committed"})
                    except (RuntimeError, KeyError) as e:
                        self._send_json(400, {"error": str(e)})
                    return

                if self.path == '/tx/rollback':
                    tx_id = payload.get("tx_id")
                    if not tx_id:
                        self._send_json(400, {"error": "Missing tx_id"})
                        return
                    try:
                        store.rollback_transaction(tx_id)
                        self._send_json(200, {"status": "rolled_back"})
                    except (RuntimeError, KeyError) as e:
                        self._send_json(400, {"error": str(e)})
                    return

                self._send_json(404, {"error": "Endpoint not found"})

            def do_DELETE(self):
                if self.path.startswith('/keys/'):
                    key = self.path[6:]
                    deleted = store.delete(key)
                    if deleted:
                        self._send_json(200, {"status": "deleted", "key": key})
                    else:
                        self._send_json(404, {"error": "Key not found"})
                    return
                self._send_json(404, {"error": "Endpoint not found"})

            def log_message(self, format, *args):
                pass  # Hermetic quiet logging

        def run_server(port: int = 8088):
            server = HTTPServer(('127.0.0.1', port), KVRequestHandler)
            print(f"SERVER_ONLINE: port={port}", flush=True)
            server.serve_forever()

        if __name__ == '__main__':
            parser = argparse.ArgumentParser()
            parser.add_argument('--port', type=int, default=8088)
            parser.add_argument('--smoke-test', action='store_true')
            args = parser.parse_args()
            if args.smoke_test:
                health = store.health_check()
                print("AXIOMA_HEALTH_OK:", json.dumps(health), flush=True)
                sys.exit(0)
            run_server(args.port)
    """)
    (output_dir / "run.py").write_text(full_g4b_server, encoding="utf-8")
    return output_dir
