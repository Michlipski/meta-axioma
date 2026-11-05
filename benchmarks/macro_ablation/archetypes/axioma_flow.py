r"""Axioma-Flow Archetype: Hierarchical DAG Job Workflow Orchestrator.

Benchmark Archetype 2 (`Axioma-Flow`).
Tests:
- XState v5 compound/parallel state machine transitions
- Acyclic graph topology validation & cycle rejection
- Non-blocking asynchronous task execution & retry backoff
- Real-time event streaming and health probing
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List
import textwrap

from ..domain_models import AblationMode, BenchmarkArchetype


def get_archetype() -> BenchmarkArchetype:
    """Returns the formal benchmark archetype specification for Axioma-Flow."""
    return BenchmarkArchetype(
        id="axioma_flow",
        name="Axioma-Flow (Hierarchical DAG Job Orchestrator)",
        domain="Distributed Workflow & Async Coordination",
        prompt=(
            "Synthesize a job execution engine that accepts acyclic workflow DAGs, executes tasks respecting dependencies, "
            "enforces exponential backoff retries on failure, transitions jobs through an explicit hierarchical state machine "
            "(PENDING -> RUNNING -> COMPLETED | FAILED | CANCELED), and streams real-time state events over SSE/HTTP."
        ),
        specification={
            "dag_validation": "TOPOLOGICAL_SORT_CYCLE_CHECK",
            "statechart_model": "HIERARCHICAL_XSTATE_V5",
            "retry_policy": "EXPONENTIAL_BACKOFF",
            "event_stream": "SSE_OR_LONG_POLL",
        },
        expected_verbs=[
            "submit_workflow",
            "execute_task",
            "retry_task",
            "cancel_workflow",
            "get_status",
            "stream_events",
            "detect_cycles",
            "health_check",
        ],
        expected_endpoints=[
            "GET /healthz",
            "POST /workflows",
            "GET /workflows/{id}",
            "POST /workflows/{id}/cancel",
            "GET /workflows/{id}/events",
            "GET /stats",
        ],
        expected_models=[
            "WorkflowTask",
            "WorkflowDAG",
            "TaskState",
            "WorkflowEvent",
            "WorkflowEngineState",
        ],
        state_transitions=[
            {"from": "PENDING", "to": "RUNNING", "action": "start", "valid": True},
            {"from": "RUNNING", "to": "COMPLETED", "action": "complete", "valid": True},
            {"from": "RUNNING", "to": "FAILED", "action": "fail", "valid": True},
            {"from": "RUNNING", "to": "CANCELED", "action": "cancel", "valid": True},
            {"from": "COMPLETED", "to": "RUNNING", "action": "restart", "valid": False},
            {"from": "FAILED", "to": "COMPLETED", "action": "force_complete", "valid": False},
            {"from": "PENDING", "to": "COMPLETED", "action": "skip_execution", "valid": False},
        ],
        chaos_payloads=[
            {
                "name": "circular_dag",
                "method": "POST",
                "path": "/workflows",
                "body": {
                    "workflow_id": "cycle_test",
                    "tasks": [
                        {"task_id": "t1", "dependencies": ["t2"]},
                        {"task_id": "t2", "dependencies": ["t1"]},
                    ],
                },
            },
            {"name": "malformed_json", "method": "POST", "path": "/workflows", "body": "INVALID_JSON"},
            {"name": "cancel_unknown", "method": "POST", "path": "/workflows/wf_404/cancel"},
            {"name": "missing_dependencies", "method": "POST", "path": "/workflows", "body": {"tasks": [{"task_id": "a", "dependencies": ["nonexistent"]}]}},
        ],
        target_loc_budget=380,
        target_token_budget=15000,
    )


def generate_candidate_app(mode: AblationMode, output_dir: Path) -> Path:
    """Generates an application target representing the requested ablation mode for Axioma-Flow."""
    output_dir.mkdir(parents=True, exist_ok=True)
    src_dir = output_dir / "src"
    src_dir.mkdir(parents=True, exist_ok=True)

    if mode == AblationMode.WO_SUBPROCESS_SMOKE:
        (output_dir / "run.py").write_text(
            "#!/usr/bin/env python3\nimport sys\nfrom ..missing_module import DAGCycle\nsys.exit(1)\n",
            encoding="utf-8",
        )
        return output_dir

    if mode == AblationMode.WO_AST_AUDITORS:
        run_code = textwrap.dedent("""\
            #!/usr/bin/env python3
            import argparse
            import os
            import sys
            from http.server import HTTPServer, BaseHTTPRequestHandler
            
            # HERM-004 violation
            SECRET_EXEC = eval("1 + 1")

            class FlowHandler(BaseHTTPRequestHandler):
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

            def run_server(port=8089):
                server = HTTPServer(('127.0.0.1', port), FlowHandler)
                print(f"SERVER_ONLINE: port={port}", flush=True)
                server.serve_forever()

            if __name__ == '__main__':
                parser = argparse.ArgumentParser()
                parser.add_argument('--port', type=int, default=8089)
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

            class FlawedFlowHandler(BaseHTTPRequestHandler):
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
                    data = json.loads(raw_body)
                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write(b'{"status":"submitted"}')

            def run_server(port=8089):
                server = HTTPServer(('127.0.0.1', port), FlawedFlowHandler)
                print(f"SERVER_ONLINE: port={port}", flush=True)
                server.serve_forever()

            if __name__ == '__main__':
                parser = argparse.ArgumentParser()
                parser.add_argument('--port', type=int, default=8089)
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

            workflows = {}

            class FlatFlowHandler(BaseHTTPRequestHandler):
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

            def run_server(port=8089):
                server = HTTPServer(('127.0.0.1', port), FlatFlowHandler)
                print(f"SERVER_ONLINE: port={port}", flush=True)
                server.serve_forever()

            if __name__ == '__main__':
                parser = argparse.ArgumentParser()
                parser.add_argument('--port', type=int, default=8089)
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
        class WorkflowTask:
            task_id: str
            dependencies: List[str] = field(default_factory=list)
            status: str = "PENDING"
            retries: int = 0
            max_retries: int = 3

        @dataclass
        class WorkflowDAG:
            workflow_id: str
            tasks: Dict[str, WorkflowTask] = field(default_factory=dict)
            status: str = "PENDING"
            created_at: float = field(default_factory=time.time)

        @dataclass
        class TaskState:
            state: str = "PENDING"

        @dataclass
        class WorkflowEvent:
            event_id: str
            workflow_id: str
            event_type: str
            timestamp: float = field(default_factory=time.time)

        @dataclass
        class WorkflowEngineState:
            current_state: str = "READY"
    """)
    (src_dir / "models.py").write_text(models_code, encoding="utf-8")

    engine_code = textwrap.dedent("""\
        from typing import Any, Dict, List, Optional
        from .models import WorkflowTask, WorkflowDAG, TaskState, WorkflowEvent, WorkflowEngineState

        class WorkflowEngine:
            def __init__(self):
                self.workflows: Dict[str, WorkflowDAG] = {}
                self.events: List[WorkflowEvent] = []
                self.state = WorkflowEngineState()

            def detect_cycles(self, tasks: Dict[str, WorkflowTask]) -> bool:
                visited = {}
                rec_stack = {}
                for tid in tasks:
                    visited[tid] = False
                    rec_stack[tid] = False

                def _has_cycle(v: str) -> bool:
                    visited[v] = True
                    rec_stack[v] = True
                    for dep in tasks[v].dependencies:
                        if dep not in tasks:
                            continue
                        if not visited[dep] and _has_cycle(dep):
                            return True
                        elif rec_stack[dep]:
                            return True
                    rec_stack[v] = False
                    return False

                for tid in tasks:
                    if not visited[tid]:
                        if _has_cycle(tid):
                            return True
                return False

            def submit_workflow(self, workflow_id: str = "wf_1", tasks_data: Optional[List[Dict[str, Any]]] = None) -> WorkflowDAG:
                tasks_data = tasks_data or []
                tasks = {}
                for td in tasks_data:
                    tid = td.get("task_id")
                    deps = td.get("dependencies", [])
                    tasks[tid] = WorkflowTask(task_id=tid, dependencies=deps)

                for tid, task in tasks.items():
                    for dep in task.dependencies:
                        if dep not in tasks:
                            raise ValueError(f"Missing dependency {dep} for task {tid}")

                if self.detect_cycles(tasks):
                    raise ValueError("Cyclic dependency detected in workflow DAG")

                dag = WorkflowDAG(workflow_id=workflow_id, tasks=tasks, status="PENDING")
                self.workflows[workflow_id] = dag
                self.events.append(WorkflowEvent(f"ev_{len(self.events)}", workflow_id, "SUBMITTED"))
                return dag

            def start(self, workflow_id: str = "wf_1") -> bool:
                dag = self.workflows.get(workflow_id)
                if not dag or dag.status != "PENDING":
                    raise RuntimeError("Can only start PENDING workflow")
                dag.status = "RUNNING"
                return True

            def complete(self, workflow_id: str = "wf_1") -> bool:
                dag = self.workflows.get(workflow_id)
                if not dag or dag.status != "RUNNING":
                    raise RuntimeError("Can only complete RUNNING workflow")
                dag.status = "COMPLETED"
                return True

            def fail(self, workflow_id: str = "wf_1") -> bool:
                dag = self.workflows.get(workflow_id)
                if not dag or dag.status != "RUNNING":
                    raise RuntimeError("Can only fail RUNNING workflow")
                dag.status = "FAILED"
                return True

            def cancel(self, workflow_id: str = "wf_1") -> bool:
                dag = self.workflows.get(workflow_id)
                if not dag or dag.status not in ("PENDING", "RUNNING"):
                    raise RuntimeError("Can only cancel PENDING or RUNNING workflow")
                dag.status = "CANCELED"
                return True

            def restart(self, workflow_id: str = "wf_1") -> bool:
                raise RuntimeError("Restarting completed workflow is forbidden")

            def force_complete(self, workflow_id: str = "wf_1") -> bool:
                raise RuntimeError("Force completing failed workflow is forbidden")

            def skip_execution(self, workflow_id: str = "wf_1") -> bool:
                raise RuntimeError("Skipping execution from PENDING to COMPLETED is forbidden")

            def execute_task(self, workflow_id: str = "wf_1", task_id: str = "t1") -> bool:
                dag = self.workflows.get(workflow_id)
                if not dag or task_id not in dag.tasks:
                    return False
                if dag.status == "PENDING":
                    dag.status = "RUNNING"
                dag.tasks[task_id].status = "COMPLETED"
                if all(t.status == "COMPLETED" for t in dag.tasks.values()):
                    dag.status = "COMPLETED"
                return True

            def retry_task(self, workflow_id: str = "wf_1", task_id: str = "t1") -> bool:
                dag = self.workflows.get(workflow_id)
                if not dag or task_id not in dag.tasks:
                    return False
                t = dag.tasks[task_id]
                if t.retries < t.max_retries:
                    t.retries += 1
                    t.status = "RUNNING"
                    return True
                t.status = "FAILED"
                dag.status = "FAILED"
                return False

            def cancel_workflow(self, workflow_id: str) -> bool:
                dag = self.workflows.get(workflow_id)
                if not dag:
                    raise KeyError(f"Workflow {workflow_id} not found")
                if dag.status in ("COMPLETED", "FAILED"):
                    raise RuntimeError("Cannot cancel completed or failed workflow")
                dag.status = "CANCELED"
                self.events.append(WorkflowEvent(f"ev_{len(self.events)}", workflow_id, "CANCELED"))
                return True

            def get_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
                dag = self.workflows.get(workflow_id)
                if not dag:
                    return None
                return {"workflow_id": dag.workflow_id, "status": dag.status, "task_count": len(dag.tasks)}

            def stream_events(self, workflow_id: str) -> List[Dict[str, Any]]:
                return [{"id": e.event_id, "type": e.event_type} for e in self.events if e.workflow_id == workflow_id]

            def health_check(self) -> Dict[str, Any]:
                return {"status": "healthy", "active_workflows": len(self.workflows)}
    """)
    (src_dir / "engine.py").write_text(engine_code, encoding="utf-8")

    server_code = textwrap.dedent("""\
        import argparse
        import json
        import sys
        from http.server import HTTPServer, BaseHTTPRequestHandler
        from src.engine import WorkflowEngine
        from src.models import WorkflowTask, WorkflowDAG, TaskState, WorkflowEvent, WorkflowEngineState

        engine = WorkflowEngine()

        class FlowRequestHandler(BaseHTTPRequestHandler):
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
                    self._send_json(200, {"workflows": len(engine.workflows)})
                    return
                if self.path.startswith('/workflows/') and self.path.endswith('/events'):
                    wf_id = self.path.split('/')[2]
                    self._send_json(200, {"events": engine.stream_events(wf_id)})
                    return
                if self.path.startswith('/workflows/'):
                    wf_id = self.path[11:]
                    status = engine.get_status(wf_id)
                    if status:
                        self._send_json(200, status)
                    else:
                        self._send_json(404, {"error": "Workflow not found"})
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

                if self.path == '/workflows':
                    wf_id = payload.get("workflow_id", f"wf_{len(engine.workflows)+1}")
                    tasks = payload.get("tasks", [])
                    try:
                        dag = engine.submit_workflow(wf_id, tasks)
                        self._send_json(200, {"status": "created", "workflow_id": dag.workflow_id})
                    except ValueError as e:
                        self._send_json(400, {"error": str(e)})
                    return

                if self.path.startswith('/workflows/') and self.path.endswith('/cancel'):
                    wf_id = self.path.split('/')[2]
                    try:
                        engine.cancel_workflow(wf_id)
                        self._send_json(200, {"status": "canceled", "workflow_id": wf_id})
                    except KeyError as e:
                        self._send_json(404, {"error": str(e)})
                    except RuntimeError as e:
                        self._send_json(409, {"error": str(e)})
                    return

                self._send_json(404, {"error": "Not found"})

            def log_message(self, format, *args):
                pass

        def run_server(port: int = 8089):
            server = HTTPServer(('127.0.0.1', port), FlowRequestHandler)
            print(f"SERVER_ONLINE: port={port}", flush=True)
            server.serve_forever()

        if __name__ == '__main__':
            parser = argparse.ArgumentParser()
            parser.add_argument('--port', type=int, default=8089)
            parser.add_argument('--smoke-test', action='store_true')
            args = parser.parse_args()
            if args.smoke_test:
                print("AXIOMA_HEALTH_OK:", json.dumps(engine.health_check()), flush=True)
                sys.exit(0)
            run_server(args.port)
    """)
    (output_dir / "run.py").write_text(server_code, encoding="utf-8")
    return output_dir
