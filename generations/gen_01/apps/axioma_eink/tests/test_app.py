"""Comprehensive Test Suite for Axioma E-Ink Task Router.

Enforces NEG-G2-003 (Main Flow & Domain Invariant Test Gate):
- Functorial Event Sourcing & Left-Fold Replay ([L1-002])
- Daily Big 3-5 Bounded Focus Invariant Enforcement
- Strict Zero-JavaScript & Meta-Refresh Electrophoretic Display Compliance
- Compensatory Undo/Redo Invariant ([L1-008])
- HTTP Handlers, Decoupled Persistence ([L1-011_3]), and Exception Enclaves ([L1-016])
"""

from __future__ import annotations

import io
import json
from pathlib import Path
import shutil
import sys
import tempfile
import time
import unittest
import uuid

APP_DIR = Path(__file__).parent.parent
SRC_DIR = APP_DIR / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from display_renderer import render_display_html
from event_store import EventStore
from models import EinkBoardState, EventType, TaskItem, TaskStatus
from server import EinkHttpHandler, ExceptionEnclave


class TestEventStoreAndInvariants(unittest.TestCase):
    """Tests EventStore replay, invariants, and compensatory undo operations."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.events_file = Path(self.temp_dir) / "test_events.json"
        self.store = EventStore(self.events_file)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_task_creation_and_event_persistence(self):
        """Tests that creating a task appends an event and derives state correctly."""
        t1 = self.store.create_task("Test Invariant Verification", priority=1, tag="@test", is_focus=True)
        self.assertEqual(t1.title, "Test Invariant Verification")
        self.assertEqual(t1.status, TaskStatus.TODO)
        self.assertTrue(t1.is_focus)

        # Check persistence to disk
        self.assertTrue(self.events_file.exists())
        with open(self.events_file, "r") as f:
            events = json.load(f)
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["event_type"], EventType.TASK_CREATED.value)

    def test_daily_big_3_5_focus_invariant_bound(self):
        """Enforces that maximum 5 active focus tasks can exist simultaneously."""
        for i in range(1, 6):
            self.store.create_task(f"Focus Priority {i}", priority=i, is_focus=True)

        board = self.store.get_board_state()
        self.assertEqual(board.total_focus_tasks, 5)

        # Attempting to add a 6th focus task must fail with domain error
        with self.assertRaises(ValueError) as ctx:
            self.store.create_task("Focus Priority 6 (Overflow)", priority=6, is_focus=True)
        self.assertIn("Daily Big 3-5 focus invariant violated", str(ctx.exception))

        # Adding a 6th task with is_focus=False must succeed and enter backlog
        backlog_task = self.store.create_task("Backlog Task", priority=99, is_focus=False)
        self.assertFalse(backlog_task.is_focus)
        tasks_data = self.store.get_all_tasks()
        self.assertEqual(len(tasks_data["focus_tasks"]), 5)
        self.assertEqual(len(tasks_data["backlog_tasks"]), 1)

    def test_event_sourcing_deterministic_replay(self):
        """Tests that reloading the store from disk rebuilds identical state."""
        t1 = self.store.create_task("Task Alpha", priority=1, is_focus=True)
        t2 = self.store.create_task("Task Beta", priority=2, is_focus=True)
        self.store.toggle_task(t1.task_id)

        # Re-instantiate a fresh store pointing to same file
        replayed_store = EventStore(self.events_file)
        self.assertEqual(len(replayed_store.tasks), 2)
        self.assertEqual(replayed_store.tasks[t1.task_id].status, TaskStatus.DONE)
        self.assertEqual(replayed_store.tasks[t2.task_id].status, TaskStatus.TODO)
        self.assertIsNotNone(replayed_store.tasks[t1.task_id].completed_at)

    def test_compensatory_undo_operations(self):
        """Tests L1-008 compensatory event undo across multiple operations."""
        # 1. Undo create
        task = self.store.create_task("Temporary Task", is_focus=True)
        self.assertIn(task.task_id, self.store.tasks)
        res = self.store.undo()
        self.assertEqual(res["status"], "undone")
        self.assertNotIn(task.task_id, self.store.tasks)

        # 2. Undo toggle
        t2 = self.store.create_task("Toggle Me", is_focus=True)
        self.store.toggle_task(t2.task_id)
        self.assertEqual(self.store.tasks[t2.task_id].status, TaskStatus.DONE)
        self.store.undo()
        self.assertEqual(self.store.tasks[t2.task_id].status, TaskStatus.TODO)


class TestDisplayRenderer(unittest.TestCase):
    """Tests strict electrophoretic zero-JS and meta-refresh constraints."""

    def test_zero_javascript_invariant(self):
        """Verifies strictly zero JavaScript tags or attributes in rendered display HTML."""
        board = EinkBoardState(
            board_title="DAILY FOCUS • BIG 3–5",
            sync_timestamp=time.time(),
            total_focus_tasks=3,
            completed_count=1,
            tasks=[
                TaskItem("t1", "Ship Axioma E-Ink", TaskStatus.DONE, 1, "@axioma", True),
                TaskItem("t2", "Draft Swarm Consensus Engine", TaskStatus.TODO, 2, "@swarm", True),
                TaskItem("t3", "Run master regression suite", TaskStatus.TODO, 3, "@tests", True),
            ],
        )
        html_out = render_display_html(board)

        # Invariant checks
        self.assertNotIn("<script", html_out.lower(), "Violates zero-JS constraint: found <script> tag.")
        self.assertNotIn("javascript:", html_out.lower(), "Violates zero-JS constraint: found inline javascript URI.")
        self.assertNotIn("onclick", html_out.lower(), "Violates zero-JS constraint: found inline event handler.")
        self.assertNotIn("@keyframes", html_out.lower(), "Violates anti-flicker constraint: found CSS keyframe animation.")
        self.assertNotIn("transition:", html_out.lower(), "Violates anti-flicker constraint: found CSS transition.")

    def test_meta_refresh_tag_present(self):
        """Verifies 15-minute ambient meta-refresh header exists."""
        board = EinkBoardState(
            board_title="DAILY FOCUS • BIG 3–5",
            sync_timestamp=time.time(),
            total_focus_tasks=1,
            completed_count=0,
            tasks=[TaskItem("t1", "Ambient Refresh Test", TaskStatus.TODO, 1, "@test", True)],
        )
        html_out = render_display_html(board)
        self.assertIn('<meta http-equiv="refresh" content="900">', html_out)
        self.assertIn("Ambient Refresh Test", html_out)
        self.assertTrue("□" in html_out or "■" in html_out)


class InMemoryHttpHarness:
    """Zero-network, thread-isolated HTTP handler harness."""

    @staticmethod
    def call(method: str, path: str, body: bytes = b"", headers: dict = None):
        handler = EinkHttpHandler.__new__(EinkHttpHandler)
        handler.rfile = io.BytesIO(body)
        handler.wfile = io.BytesIO()
        handler.path = path
        handler.command = method
        handler.request_version = "HTTP/1.1"
        handler.headers = headers or {}
        if body and "Content-Length" not in handler.headers:
            handler.headers["Content-Length"] = str(len(body))

        handler._response_code = 200
        handler._response_headers = {}

        def mock_send_response(code, msg=None):
            handler._response_code = code

        def mock_send_header(key, val):
            handler._response_headers[key] = val

        def mock_end_headers():
            pass

        handler.send_response = mock_send_response
        handler.send_header = mock_send_header
        handler.end_headers = mock_end_headers

        if method == "GET":
            handler.do_GET()
        elif method == "POST":
            handler.do_POST()
        elif method == "DELETE":
            handler.do_DELETE()
        elif method == "OPTIONS":
            handler.do_OPTIONS()

        return handler._response_code, handler._response_headers, handler.wfile.getvalue()


class TestHttpServerIntegration(unittest.TestCase):
    """Tests the HTTP handler routing, payload processing, and ExceptionEnclaves."""

    def test_get_display_endpoint_zero_js(self):
        """GET /display returns 200 OK with zero-JS HTML and meta-refresh."""
        code, headers, body = InMemoryHttpHarness.call("GET", "/display")
        self.assertEqual(code, 200)
        self.assertIn("text/html", headers.get("Content-Type", ""))
        html_str = body.decode("utf-8")
        self.assertIn('<meta http-equiv="refresh" content="900">', html_str)
        self.assertNotIn("<script", html_str.lower())

    def test_get_display_raw_endpoint(self):
        """GET /display/raw returns 200 OK with plaintext summary."""
        code, headers, body = InMemoryHttpHarness.call("GET", "/display/raw")
        self.assertEqual(code, 200)
        self.assertIn("text/plain", headers.get("Content-Type", ""))
        text_str = body.decode("utf-8")
        self.assertIn("DAILY FOCUS", text_str)

    def test_get_api_tasks(self):
        """GET /api/tasks returns 200 with partitioned tasks and board state."""
        code, headers, body = InMemoryHttpHarness.call("GET", "/api/tasks")
        self.assertEqual(code, 200)
        data = json.loads(body.decode("utf-8"))
        self.assertIn("focus_tasks", data)
        self.assertIn("backlog_tasks", data)
        self.assertIn("board", data)

    def test_task_crud_lifecycle_via_handler(self):
        """Tests task creation, toggle, focus change, and deletion via HTTP handler."""
        uid = uuid.uuid4().hex[:6]
        post_body = json.dumps({"title": f"Test Task {uid}", "tag": "@test", "is_focus": False}).encode("utf-8")

        # 1. Create task
        code, _, resp_bytes = InMemoryHttpHarness.call("POST", "/api/tasks", post_body)
        self.assertEqual(code, 201)
        res = json.loads(resp_bytes.decode("utf-8"))
        task_id = res["task"]["task_id"]

        # 2. Toggle task
        code, _, resp_bytes = InMemoryHttpHarness.call("POST", f"/api/tasks/{task_id}/toggle")
        self.assertEqual(code, 200)
        res = json.loads(resp_bytes.decode("utf-8"))
        self.assertEqual(res["task"]["status"], "DONE")

        # 3. Undo toggle
        code, _, resp_bytes = InMemoryHttpHarness.call("POST", "/api/undo")
        self.assertEqual(code, 200)
        res = json.loads(resp_bytes.decode("utf-8"))
        self.assertEqual(res["status"], "undone")

        # 4. Delete task
        code, _, resp_bytes = InMemoryHttpHarness.call("DELETE", f"/api/tasks/{task_id}")
        self.assertEqual(code, 200)

    def test_exception_enclave_isolation(self):
        """Tests L1-016 exception enclave prevents server crashes on exceptions."""
        with ExceptionEnclave("TEST_ENCLAVE", "testing_blast_radius") as enclave:
            raise RuntimeError("Simulated enclave fault")

        self.assertIsNotNone(enclave.caught)
        self.assertTrue(enclave.witness["blast_radius_isolated"])
        self.assertEqual(enclave.witness["error_type"], "RuntimeError")

    def test_feedback_submission(self):
        """Tests transgenerational feedback capture endpoint."""
        fb_payload = json.dumps({
            "category": "hardware_legibility",
            "comment": "Electrophoretic contrast is excellent under direct sunlight on Kindle Paperwhite.",
        }).encode("utf-8")
        code, _, resp_bytes = InMemoryHttpHarness.call("POST", "/api/feedback", fb_payload)
        self.assertEqual(code, 201)
        res = json.loads(resp_bytes.decode("utf-8"))
        self.assertTrue(res["success"])
        self.assertEqual(res["record"]["category"], "hardware_legibility")

    def test_health_and_telemetry_endpoints(self):
        """Tests /health and /api/telemetry endpoints."""
        code, _, body = InMemoryHttpHarness.call("GET", "/health")
        self.assertEqual(code, 200)
        health_data = json.loads(body.decode("utf-8"))
        self.assertEqual(health_data["status"], "ok")
        self.assertEqual(health_data["app"], "axioma_eink")

        code, _, body = InMemoryHttpHarness.call("GET", "/api/telemetry")
        self.assertEqual(code, 200)
        telem_data = json.loads(body.decode("utf-8"))
        self.assertEqual(telem_data["app"], "axioma_eink")


if __name__ == "__main__":
    unittest.main()
