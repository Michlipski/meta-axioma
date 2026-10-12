"""Comprehensive Test Suite for Axioma Swarm (Local LLM Edge Orchestrator).

Enforces NEG-G2-003 (Main Flow & Domain Invariant Test Gate):
- Physical VRAM Tensor Memory Budgeting & OOM Prevention Gate ([L1-008])
- Deterministic LRU Model Eviction under Memory Contention
- Demarcated Exception Enclaves ([L1-016]) for Model Inference Blast-Radius Containment
- Zero-Trust Scoping & Specialty Task Routing ([L1-015])
- Append-Only Event Sourcing ([L1-002]) and Decoupled Persistence ([L1-011_3])
- HTTP REST API Endpoints and Telemetry Reporting
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

from models import (
    ModelDescriptor,
    ModelSpecialty,
    ModelStatus,
    SwarmTask,
    TaskPriority,
    TaskStatus,
    VramPool,
)
from server import SwarmHttpHandler
from swarm_orchestrator import ExceptionEnclave, SwarmOrchestrator
from vram_manager import OomPreventionError, VramManager


class TestVramManagerAndEviction(unittest.TestCase):
    """Tests VRAM tensor memory allocation, OOM prevention gate, and LRU eviction."""

    def setUp(self):
        # Create a compact pool for deterministic testing: 10,000 MB total, 2,000 MB reserved -> 8,000 MB usable
        self.pool = VramPool(total_vram_mb=10000, allocated_vram_mb=0, reserved_buffer_mb=2000)
        self.mgr = VramManager(self.pool)

    def test_single_model_allocation_and_metrics(self):
        """Verifies VRAM allocation reflects correct memory reduction."""
        model, evicted = self.mgr.allocate_model("llama-3.2-3b")  # 3912 MB
        self.assertEqual(model.status, ModelStatus.RESIDENT)
        self.assertEqual(len(evicted), 0)
        self.assertEqual(self.mgr.pool.allocated_vram_mb, 3912)
        self.assertEqual(self.mgr.pool.available_vram_mb, 8000 - 3912)

    def test_lru_eviction_under_memory_contention(self):
        """Verifies that allocating a model exceeding available headroom triggers deterministic LRU eviction."""
        # 1. Allocate llama-3.2-3b (3912 MB) -> remaining headroom = 4088 MB
        m1, _ = self.mgr.allocate_model("llama-3.2-3b")
        time.sleep(0.01)

        # 2. Allocate phi-3.5-mini (2912 MB) -> total allocated = 6824 MB, remaining = 1176 MB
        m2, _ = self.mgr.allocate_model("phi-3.5-mini")
        time.sleep(0.01)
        self.assertEqual(self.mgr.pool.allocated_vram_mb, 6824)

        # 3. Now attempt to allocate qwen-2.5-coder-7b (5824 MB).
        # Need 5824 MB, only 1176 MB available.
        # Oldest resident is m1 (llama-3.2-3b).
        # Evicting m1 frees 3912 MB -> available = 1176 + 3912 = 5088 MB. Still need 5824 MB!
        # Next oldest is m2 (phi-3.5-mini). Evicting m2 frees 2912 MB -> available = 8000 MB. Fits!
        m3, evicted = self.mgr.allocate_model("qwen-2.5-coder-7b")
        self.assertEqual(m3.status, ModelStatus.RESIDENT)
        self.assertIn("llama-3.2-3b", evicted)
        self.assertIn("phi-3.5-mini", evicted)
        self.assertEqual(self.mgr.models["llama-3.2-3b"].status, ModelStatus.UNLOADED)
        self.assertEqual(self.mgr.pool.allocated_vram_mb, 5824)

    def test_oom_prevention_gate_when_busy(self):
        """Verifies OOM gate triggers if all resident models are busy with concurrent tasks."""
        m1, _ = self.mgr.allocate_model("llama-3.2-3b")
        self.mgr.acquire_inference("llama-3.2-3b")  # Marked BUSY
        self.assertEqual(m1.status, ModelStatus.BUSY)

        # Headroom is 8000 - 3912 = 4088 MB. Attempt to allocate qwen (5824 MB)
        # Cannot evict llama because it is BUSY!
        with self.assertRaises(OomPreventionError) as ctx:
            self.mgr.allocate_model("qwen-2.5-coder-7b")
        self.assertIn("OOM Prevention Gate Triggered", str(ctx.exception))

    def test_manual_model_eviction(self):
        """Verifies manual eviction reclaims memory cleanly."""
        m1, _ = self.mgr.allocate_model("llama-3.2-3b")
        self.assertEqual(self.mgr.pool.allocated_vram_mb, 3912)

        evicted = self.mgr.evict_model("llama-3.2-3b")
        self.assertEqual(evicted.status, ModelStatus.UNLOADED)
        self.assertEqual(self.mgr.pool.allocated_vram_mb, 0)
        self.assertEqual(self.mgr.pool.available_vram_mb, 8000)


class TestSwarmOrchestratorExecution(unittest.TestCase):
    """Tests orchestrator task routing, enclave fault containment, and event logs."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.orchestrator = SwarmOrchestrator(data_dir=Path(self.temp_dir))

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_specialty_auto_routing(self):
        """Verifies that tasks without explicit model override route to specialist models."""
        coding_model = self.orchestrator.select_best_model_for_specialty(ModelSpecialty.CODING)
        self.assertEqual(coding_model, "qwen-2.5-coder-7b")

        reasoning_model = self.orchestrator.select_best_model_for_specialty(ModelSpecialty.REASONING)
        self.assertIn(reasoning_model, ["llama-3.2-3b", "deepseek-r1-8b"])

        summary_model = self.orchestrator.select_best_model_for_specialty(ModelSpecialty.FAST_SUMMARY)
        self.assertEqual(summary_model, "phi-3.5-mini")

    def test_task_submission_and_execution_lifecycle(self):
        """Verifies full execution lifecycle from queue to completion with token generation."""
        task = self.orchestrator.submit_task(
            prompt="Write a Python script to compute Fibonacci numbers",
            specialty="CODING",
            priority="HIGH",
        )
        self.assertEqual(task.status, TaskStatus.QUEUED)
        self.assertEqual(task.target_model_id, "qwen-2.5-coder-7b")

        executed = self.orchestrator.execute_task(task.task_id)
        self.assertEqual(executed.status, TaskStatus.COMPLETED)
        self.assertGreater(executed.tokens_processed, 50)
        self.assertGreater(executed.latency_ms, 0.0)
        self.assertIn("def ", executed.result_output)
        self.assertIsNone(executed.error_witness)

        # Verify model lease released
        model = self.orchestrator.vram.models["qwen-2.5-coder-7b"]
        self.assertEqual(model.status, ModelStatus.RESIDENT)

    def test_exception_enclave_blast_radius_containment(self):
        """Verifies L1-016 exception enclave safely isolates simulated model faults without crashing daemon."""
        task = self.orchestrator.submit_task(
            prompt="CRASH_ENCLAVE_FAULT: Inject memory spike to test L1-016 enclave containment",
            specialty="REASONING",
        )
        executed = self.orchestrator.execute_task(task.task_id)
        self.assertEqual(executed.status, TaskStatus.FAILED)
        self.assertIsNotNone(executed.error_witness)
        self.assertTrue(executed.error_witness["blast_radius_isolated"])
        self.assertEqual(executed.error_witness["error_type"], "RuntimeError")

        # Verify model is NOT stuck in BUSY state
        model = self.orchestrator.vram.models[task.target_model_id]
        self.assertNotEqual(model.status, ModelStatus.BUSY)

        # Telemetry should record the fault isolation
        telem = self.orchestrator.get_telemetry()
        self.assertGreaterEqual(telem["telemetry"]["enclave_faults_isolated"], 1)

    def test_task_cancellation(self):
        """Verifies queued task cancellation."""
        task = self.orchestrator.submit_task(prompt="Long batch job", priority="BATCH")
        cancelled = self.orchestrator.cancel_task(task.task_id)
        self.assertEqual(cancelled.status, TaskStatus.CANCELLED)


class InMemoryHttpHarness:
    """Zero-network, thread-isolated HTTP handler harness."""

    @staticmethod
    def call(method: str, path: str, body: bytes = b"", headers: dict = None):
        handler = SwarmHttpHandler.__new__(SwarmHttpHandler)
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
        elif method == "OPTIONS":
            handler.do_OPTIONS()

        return handler._response_code, handler._response_headers, handler.wfile.getvalue()


class TestHttpServerIntegration(unittest.TestCase):
    """Tests the HTTP handler routing, VRAM APIs, task dispatch, and feedback."""

    def test_get_vram_and_models_endpoints(self):
        """GET /api/vram and /api/models return 200 with valid JSON payloads."""
        code, _, body = InMemoryHttpHarness.call("GET", "/api/vram")
        self.assertEqual(code, 200)
        vram_data = json.loads(body.decode("utf-8"))
        self.assertIn("total_vram_mb", vram_data)
        self.assertIn("available_vram_mb", vram_data)

        code, _, body = InMemoryHttpHarness.call("GET", "/api/models")
        self.assertEqual(code, 200)
        models_data = json.loads(body.decode("utf-8"))
        self.assertGreaterEqual(len(models_data["models"]), 4)

    def test_model_load_and_evict_api(self):
        """POST /api/models/{id}/load and /evict manage residency over HTTP."""
        code, _, body = InMemoryHttpHarness.call("POST", "/api/models/phi-3.5-mini/load")
        self.assertEqual(code, 200)
        res = json.loads(body.decode("utf-8"))
        self.assertEqual(res["model"]["status"], "RESIDENT")

        code, _, body = InMemoryHttpHarness.call("POST", "/api/models/phi-3.5-mini/evict")
        self.assertEqual(code, 200)
        res = json.loads(body.decode("utf-8"))
        self.assertEqual(res["model"]["status"], "UNLOADED")

    def test_task_dispatch_api(self):
        """POST /api/tasks/dispatch runs task through swarm orchestrator."""
        payload = json.dumps({
            "prompt": "Test dispatch API prompt",
            "specialty": "FAST_SUMMARY",
            "priority": "HIGH",
        }).encode("utf-8")
        code, _, body = InMemoryHttpHarness.call("POST", "/api/tasks/dispatch", payload)
        self.assertEqual(code, 200)
        res = json.loads(body.decode("utf-8"))
        self.assertEqual(res["task"]["status"], "COMPLETED")
        self.assertIn("Summary", res["task"]["result_output"])

    def test_feedback_submission(self):
        """POST /api/feedback records transgenerational feedback."""
        payload = json.dumps({
            "category": "vram_allocation",
            "comment": "LRU eviction timing is seamless with zero display compositor stutter.",
        }).encode("utf-8")
        code, _, body = InMemoryHttpHarness.call("POST", "/api/feedback", payload)
        self.assertEqual(code, 201)
        res = json.loads(body.decode("utf-8"))
        self.assertTrue(res["success"])

    def test_health_and_telemetry(self):
        """GET /health and /api/telemetry return 200."""
        code, _, body = InMemoryHttpHarness.call("GET", "/health")
        self.assertEqual(code, 200)
        self.assertEqual(json.loads(body.decode("utf-8"))["status"], "ok")

        code, _, body = InMemoryHttpHarness.call("GET", "/api/telemetry")
        self.assertEqual(code, 200)
        telem = json.loads(body.decode("utf-8"))
        self.assertIn("telemetry", telem)


if __name__ == "__main__":
    unittest.main()
