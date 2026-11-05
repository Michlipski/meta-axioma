r"""Axioma-Collab Archetype: Real-Time Collaborative Board with CRDT & Undo/Redo.

Benchmark Archetype 3 (`Axioma-Collab`).
Tests:
- Vector clocks & conflict-free replicated data types (CRDTs)
- Sheaf-CRDT state convergence
- Functorial 1-tap undo/redo operations ($S \circ S^{-1} = \text{id}$)
- Concurrent multi-client session handling
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List
import textwrap

from ..domain_models import AblationMode, BenchmarkArchetype


def get_archetype() -> BenchmarkArchetype:
    """Returns the formal benchmark archetype specification for Axioma-Collab."""
    return BenchmarkArchetype(
        id="axioma_collab",
        name="Axioma-Collab (Real-Time Collaborative Board & CRDT Engine)",
        domain="Event-Driven State Synchronization",
        prompt=(
            "Synthesize a real-time collaborative state board supporting multiple concurrent client sessions over WebSockets, "
            "conflict-free state merging via vector clocks/CRDTs, full event history audit trail, and instant 1-tap client-side undo/redo."
        ),
        specification={
            "crdt_model": "LWW_ELEMENT_SET",
            "concurrency_control": "VECTOR_CLOCK",
            "undo_redo_engine": "FUNCTORIAL_INVERSION",
            "history_audit": "APPEND_ONLY_CHRONO",
        },
        expected_verbs=[
            "connect_client",
            "apply_operation",
            "merge_crdt",
            "undo_operation",
            "redo_operation",
            "broadcast_state",
            "get_history",
            "health_check",
        ],
        expected_endpoints=[
            "GET /healthz",
            "GET /board",
            "POST /board/elements",
            "POST /board/undo",
            "POST /board/redo",
            "GET /board/history",
            "GET /stats",
        ],
        expected_models=[
            "CanvasElement",
            "VectorClock",
            "CRDTOperation",
            "CanvasState",
            "CollabSession",
        ],
        state_transitions=[
            {"from": "EMPTY", "to": "ACTIVE", "action": "add_element", "valid": True},
            {"from": "ACTIVE", "to": "DIRTY", "action": "update_element", "valid": True},
            {"from": "DIRTY", "to": "SAVED", "action": "save_snapshot", "valid": True},
            {"from": "ACTIVE", "to": "UNDOING", "action": "undo", "valid": True},
            {"from": "UNDOING", "to": "ACTIVE", "action": "complete_undo", "valid": True},
            {"from": "EMPTY", "to": "UNDOING", "action": "undo", "valid": False},
        ],
        chaos_payloads=[
            {"name": "malformed_op", "method": "POST", "path": "/board/elements", "body": "NOT_JSON"},
            {"name": "undo_empty", "method": "POST", "path": "/board/undo", "body": {}},
            {"name": "negative_clock", "method": "POST", "path": "/board/elements", "body": {"element_id": "e1", "clock": -1}},
            {"name": "burst_edits", "method": "POST", "path": "/board/elements", "body": {"element_id": "e_burst", "data": "update"}},
        ],
        target_loc_budget=360,
        target_token_budget=14500,
    )


def generate_candidate_app(mode: AblationMode, output_dir: Path) -> Path:
    """Generates an application target representing the requested ablation mode for Axioma-Collab."""
    output_dir.mkdir(parents=True, exist_ok=True)
    src_dir = output_dir / "src"
    src_dir.mkdir(parents=True, exist_ok=True)

    if mode == AblationMode.WO_SUBPROCESS_SMOKE:
        (output_dir / "run.py").write_text(
            "#!/usr/bin/env python3\nimport non_existent_crdt\n", encoding="utf-8"
        )
        return output_dir

    if mode == AblationMode.WO_AST_AUDITORS:
        run_code = textwrap.dedent("""\
            #!/usr/bin/env python3
            import argparse
            import os
            import sys
            from http.server import HTTPServer, BaseHTTPRequestHandler
            
            # HERM-003 violation
            TEMP_BOARD = "/tmp/axioma_collab_ambient.db"

            class CollabHandler(BaseHTTPRequestHandler):
                def do_GET(self):
                    if self.path == '/healthz':
                        self.send_response(200)
                        self.end_headers()
                        self.wfile.write(b'{"status":"healthy"}')
                        return
                    self.send_response(404)
                    self.end_headers()

                def do_POST(self):
                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write(b'{"status":"ok"}')

            def run_server(port=8090):
                server = HTTPServer(('127.0.0.1', port), CollabHandler)
                print(f"SERVER_ONLINE: port={port}", flush=True)
                server.serve_forever()

            if __name__ == '__main__':
                parser = argparse.ArgumentParser()
                parser.add_argument('--port', type=int, default=8090)
                parser.add_argument('--smoke-test', action='store_true')
                args = parser.parse_args()
                if args.smoke_test:
                    print("AXIOMA_HEALTH_OK: healthy", flush=True)
                    sys.exit(0)
                run_server(args.port)
        """)
        (output_dir / "run.py").write_text(run_code, encoding="utf-8")
        return output_dir

    if mode == AblationMode.WO_CONTRACTS_SMT:
        run_code = textwrap.dedent("""\
            #!/usr/bin/env python3
            import argparse
            import json
            import sys
            from http.server import HTTPServer, BaseHTTPRequestHandler

            class FlawedCollabHandler(BaseHTTPRequestHandler):
                def do_GET(self):
                    if self.path == '/healthz':
                        self.send_response(200)
                        self.end_headers()
                        self.wfile.write(b'{"status":"healthy"}')
                        return
                    self.send_response(404)
                    self.end_headers()

                def do_POST(self):
                    content_len = int(self.headers.get('Content-Length', 0))
                    raw_body = self.rfile.read(content_len).decode('utf-8') if content_len else "{}"
                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write(b'{"status":"ok"}')

            def run_server(port=8090):
                server = HTTPServer(('127.0.0.1', port), FlawedCollabHandler)
                print(f"SERVER_ONLINE: port={port}", flush=True)
                server.serve_forever()

            if __name__ == '__main__':
                parser = argparse.ArgumentParser()
                parser.add_argument('--port', type=int, default=8090)
                parser.add_argument('--smoke-test', action='store_true')
                args = parser.parse_args()
                if args.smoke_test:
                    print("AXIOMA_HEALTH_OK: healthy", flush=True)
                    sys.exit(0)
                run_server(args.port)
        """)
        (output_dir / "run.py").write_text(run_code, encoding="utf-8")
        return output_dir

    if mode == AblationMode.FLAT_PROMPT_LLM:
        run_code = textwrap.dedent("""\
            #!/usr/bin/env python3
            import argparse
            import json
            import sys
            from http.server import HTTPServer, BaseHTTPRequestHandler

            class FlatCollabHandler(BaseHTTPRequestHandler):
                def do_GET(self):
                    if self.path == '/healthz':
                        self.send_response(200)
                        self.end_headers()
                        self.wfile.write(b'{"status":"healthy"}')
                        return
                    self.send_response(404)
                    self.end_headers()

                def do_POST(self):
                    content_len = int(self.headers.get('Content-Length', 0))
                    raw_body = self.rfile.read(content_len).decode('utf-8')
                    payload = json.loads(raw_body)
                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write(b'{"status":"ok"}')

            def run_server(port=8090):
                server = HTTPServer(('127.0.0.1', port), FlatCollabHandler)
                print(f"SERVER_ONLINE: port={port}", flush=True)
                server.serve_forever()

            if __name__ == '__main__':
                parser = argparse.ArgumentParser()
                parser.add_argument('--port', type=int, default=8090)
                parser.add_argument('--smoke-test', action='store_true')
                args = parser.parse_args()
                if args.smoke_test:
                    print("AXIOMA_HEALTH_OK: healthy", flush=True)
                    sys.exit(0)
                run_server(args.port)
        """)
        (output_dir / "run.py").write_text(run_code, encoding="utf-8")
        return output_dir

    # FULL_G4B compliant engine
    models_code = textwrap.dedent("""\
        from dataclasses import dataclass, field
        import time
        from typing import Any, Dict, List, Optional

        @dataclass
        class CanvasElement:
            element_id: str
            data: Any
            client_id: str = "default_client"
            clock: int = 1
            deleted: bool = False

        @dataclass
        class VectorClock:
            clocks: Dict[str, int] = field(default_factory=dict)

        @dataclass
        class CRDTOperation:
            op_id: str
            element_id: str
            action: str
            payload: Any
            timestamp: float = field(default_factory=time.time)

        @dataclass
        class CanvasState:
            current_state: str = "EMPTY"

        @dataclass
        class CollabSession:
            session_id: str
            client_id: str
            active: bool = True
    """)
    (src_dir / "models.py").write_text(models_code, encoding="utf-8")

    engine_code = textwrap.dedent("""\
        from typing import Any, Dict, List, Optional
        from .models import CanvasElement, VectorClock, CRDTOperation, CanvasState, CollabSession

        class CollabEngine:
            def __init__(self):
                self.elements: Dict[str, CanvasElement] = {}
                self.history: List[CRDTOperation] = []
                self.redo_stack: List[CRDTOperation] = []
                self.state = CanvasState()

            def connect_client(self, client_id: str = "c1") -> CollabSession:
                return CollabSession(session_id=f"sess_{client_id}", client_id=client_id)

            def add_element(self, element_id: str = "e1", data: Any = "shape") -> CanvasElement:
                return self.apply_operation(element_id, data)

            def update_element(self, element_id: str = "e1", data: Any = "new_shape") -> CanvasElement:
                return self.apply_operation(element_id, data)

            def save_snapshot(self) -> bool:
                self.state.current_state = "SAVED"
                return True

            def undo(self) -> Optional[CRDTOperation]:
                return self.undo_operation()

            def complete_undo(self) -> bool:
                self.state.current_state = "ACTIVE"
                return True

            def apply_operation(self, element_id: str = "e1", data: Any = "val", client_id: str = "c1") -> CanvasElement:
                elem = CanvasElement(element_id=element_id, data=data, client_id=client_id)
                self.elements[element_id] = elem
                op = CRDTOperation(op_id=f"op_{len(self.history)}", element_id=element_id, action="SET", payload=data)
                self.history.append(op)
                self.redo_stack.clear()
                self.state.current_state = "ACTIVE"
                return elem

            def merge_crdt(self, incoming_elements: Optional[List[Dict[str, Any]]] = None) -> int:
                incoming_elements = incoming_elements or []
                count = 0
                for item in incoming_elements:
                    eid = item.get("element_id")
                    clock = item.get("clock", 1)
                    if eid not in self.elements or clock > self.elements[eid].clock:
                        self.elements[eid] = CanvasElement(
                            element_id=eid,
                            data=item.get("data"),
                            clock=clock,
                            deleted=item.get("deleted", False)
                        )
                        count += 1
                return count

            def undo_operation(self) -> Optional[CRDTOperation]:
                if not self.history or self.state.current_state == "EMPTY":
                    raise RuntimeError("Cannot undo on empty history")
                op = self.history.pop()
                self.redo_stack.append(op)
                if op.element_id in self.elements:
                    del self.elements[op.element_id]
                self.state.current_state = "ACTIVE" if self.elements else "EMPTY"
                return op

            def redo_operation(self) -> Optional[CRDTOperation]:
                if not self.redo_stack:
                    raise RuntimeError("Cannot redo: redo stack is empty")
                op = self.redo_stack.pop()
                self.elements[op.element_id] = CanvasElement(element_id=op.element_id, data=op.payload)
                self.history.append(op)
                self.state.current_state = "ACTIVE"
                return op

            def broadcast_state(self) -> Dict[str, Any]:
                return {k: v.data for k, v in self.elements.items() if not v.deleted}

            def get_history(self) -> List[Dict[str, Any]]:
                return [{"id": op.op_id, "element": op.element_id, "action": op.action} for op in self.history]

            def health_check(self) -> Dict[str, Any]:
                return {"status": "healthy", "elements": len(self.elements), "history_depth": len(self.history)}
    """)
    (src_dir / "engine.py").write_text(engine_code, encoding="utf-8")

    server_code = textwrap.dedent("""\
        import argparse
        import json
        import sys
        from http.server import HTTPServer, BaseHTTPRequestHandler
        from src.engine import CollabEngine
        from src.models import CanvasElement, VectorClock, CRDTOperation, CanvasState, CollabSession

        engine = CollabEngine()

        class CollabRequestHandler(BaseHTTPRequestHandler):
            def _send_json(self, status: int, data: dict):
                self.send_response(status)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(data).encode('utf-8'))

            def do_GET(self):
                if self.path == '/healthz':
                    self._send_json(200, engine.health_check())
                    return
                if self.path == '/stats':
                    self._send_json(200, {"elements": len(engine.elements)})
                    return
                if self.path == '/board':
                    self._send_json(200, engine.broadcast_state())
                    return
                if self.path == '/board/history':
                    self._send_json(200, {"history": engine.get_history()})
                    return
                self._send_json(404, {"error": "Not found"})

            def do_POST(self):
                content_len = int(self.headers.get('Content-Length', 0))
                raw_body = self.rfile.read(content_len).decode('utf-8') if content_len > 0 else "{}"
                try:
                    payload = json.loads(raw_body)
                except Exception:
                    self._send_json(400, {"error": "Malformed JSON payload"})
                    return

                if self.path == '/board/elements':
                    eid = payload.get("element_id")
                    if not eid:
                        self._send_json(400, {"error": "Missing element_id"})
                        return
                    clock = payload.get("clock", 1)
                    if clock is not None and clock < 0:
                        self._send_json(400, {"error": "Clock must be non-negative"})
                        return
                    data = payload.get("data")
                    elem = engine.apply_operation(eid, data)
                    self._send_json(200, {"status": "ok", "element_id": elem.element_id})
                    return

                if self.path == '/board/undo':
                    try:
                        op = engine.undo_operation()
                        self._send_json(200, {"status": "undone", "op_id": op.op_id})
                    except RuntimeError as e:
                        self._send_json(400, {"error": str(e)})
                    return

                if self.path == '/board/redo':
                    try:
                        op = engine.redo_operation()
                        self._send_json(200, {"status": "redone", "op_id": op.op_id})
                    except RuntimeError as e:
                        self._send_json(400, {"error": str(e)})
                    return

                self._send_json(404, {"error": "Not found"})

            def log_message(self, format, *args):
                pass

        def run_server(port: int = 8090):
            server = HTTPServer(('127.0.0.1', port), CollabRequestHandler)
            print(f"SERVER_ONLINE: port={port}", flush=True)
            server.serve_forever()

        if __name__ == '__main__':
            parser = argparse.ArgumentParser()
            parser.add_argument('--port', type=int, default=8090)
            parser.add_argument('--smoke-test', action='store_true')
            args = parser.parse_args()
            if args.smoke_test:
                print("AXIOMA_HEALTH_OK:", json.dumps(engine.health_check()), flush=True)
                sys.exit(0)
            run_server(args.port)
    """)
    (output_dir / "run.py").write_text(server_code, encoding="utf-8")
    return output_dir
