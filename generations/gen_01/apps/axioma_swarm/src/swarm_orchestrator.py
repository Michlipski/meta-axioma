"""Local LLM Swarm Orchestration Engine for Axioma Swarm.

Enforces:
- Physical Resource Bounds ([L1-008]) via VramManager
- Demarcated Exception Enclaves ([L1-016]) for inference blast-radius containment
- Functorial Event Sourcing ([L1-002]) with immutable audit logs
- Decoupled Persistence ([L1-011_3]) across Boundary 3
"""

from __future__ import annotations

import json
from pathlib import Path
import threading
import time
from typing import Any, Dict, List, Optional, Tuple
import uuid

from models import (
    EventType,
    FeedbackItem,
    ModelDescriptor,
    ModelSpecialty,
    ModelStatus,
    SwarmEvent,
    SwarmTask,
    TaskPriority,
    TaskStatus,
)
from vram_manager import OomPreventionError, VramManager


class ExceptionEnclave:
    """[L1-016] Demarcated Exception Enclave isolating runtime model faults."""

    def __init__(self, enclave_id: str, context: str):
        self.enclave_id = enclave_id
        self.context = context
        self.caught: Optional[str] = None
        self.witness: Optional[Dict[str, Any]] = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_val is not None:
            self.caught = str(exc_val)
            self.witness = {
                "enclave_id": self.enclave_id,
                "context": self.context,
                "error_type": exc_type.__name__ if exc_type else "Unknown",
                "message": str(exc_val),
                "blast_radius_isolated": True,
                "timestamp": time.time(),
                "recovery_guidance": "Inference fault contained. VRAM lease safely released back to pool.",
            }
            return True
        return False


class SwarmOrchestrator:
    """Central daemon coordinating local model residency, task queues, and enclave execution."""

    def __init__(self, data_dir: Optional[Path] = None, vram_manager: Optional[VramManager] = None):
        self.lock = threading.RLock()
        self.data_dir = data_dir or (Path(__file__).parent.parent / "data")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.events_file = self.data_dir / "events.json"
        self.tasks_file = self.data_dir / "tasks.json"

        self.vram = vram_manager or VramManager()
        self.tasks: Dict[str, SwarmTask] = {}
        self.events: List[SwarmEvent] = []

        self.telemetry = {
            "tasks_dispatched": 0,
            "tasks_completed": 0,
            "tasks_failed": 0,
            "tokens_generated": 0,
            "enclave_faults_isolated": 0,
            "auto_evictions_triggered": 0,
            "avg_latency_ms": 0.0,
            "total_latency_ms": 0.0,
            "started_at": time.time(),
        }

        self._load_persisted_state()

    def _load_persisted_state(self) -> None:
        """Loads historical tasks and events from decoupled JSON files."""
        with self.lock:
            if self.events_file.exists():
                try:
                    with open(self.events_file, "r", encoding="utf-8") as f:
                        raw_evts = json.load(f)
                    for e in raw_evts:
                        self.events.append(SwarmEvent.from_dict(e))
                except Exception:
                    pass

            if self.tasks_file.exists():
                try:
                    with open(self.tasks_file, "r", encoding="utf-8") as f:
                        raw_tasks = json.load(f)
                    for t in raw_tasks:
                        task = SwarmTask.from_dict(t)
                        self.tasks[task.task_id] = task
                except Exception:
                    pass

    def _persist_events_locked(self) -> None:
        tmp = self.events_file.with_suffix(".tmp")
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump([e.to_dict() for e in self.events], f, indent=2)
        tmp.replace(self.events_file)

    def _persist_tasks_locked(self) -> None:
        tmp = self.tasks_file.with_suffix(".tmp")
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump([t.to_dict() for t in self.tasks.values()], f, indent=2)
        tmp.replace(self.tasks_file)

    def _record_event_locked(self, etype: EventType, payload: Dict[str, Any]) -> SwarmEvent:
        evt = SwarmEvent(
            event_id=f"evt_{uuid.uuid4().hex[:8]}",
            event_type=etype,
            payload=payload,
            timestamp=time.time(),
        )
        self.events.append(evt)
        self._persist_events_locked()
        return evt

    def select_best_model_for_specialty(self, specialty: ModelSpecialty) -> str:
        """Finds the most suitable model registered in the catalog for a task specialty."""
        with self.lock:
            # 1. Match specialty exactly
            matched = [m for m in self.vram.models.values() if m.specialty == specialty]
            if matched:
                # Prefer resident model if available
                resident = [m for m in matched if m.status == ModelStatus.RESIDENT]
                if resident:
                    return resident[0].model_id
                return matched[0].model_id

            # 2. Fallback to general reasoning model
            reasoning = [m for m in self.vram.models.values() if m.specialty == ModelSpecialty.REASONING]
            if reasoning:
                return reasoning[0].model_id

            # 3. Default to first in catalog
            return next(iter(self.vram.models.keys()))

    def submit_task(
        self,
        prompt: str,
        specialty: Optional[str] = None,
        target_model_id: Optional[str] = None,
        priority: str = "NORMAL",
    ) -> SwarmTask:
        """Queues a task in the orchestrator."""
        with self.lock:
            task_id = f"task_{uuid.uuid4().hex[:8]}"
            spec = ModelSpecialty(specialty) if specialty else ModelSpecialty.REASONING
            prio = TaskPriority(priority) if priority else TaskPriority.NORMAL

            if not target_model_id:
                target_model_id = self.select_best_model_for_specialty(spec)

            task = SwarmTask(
                task_id=task_id,
                prompt=prompt.strip(),
                specialty_required=spec,
                target_model_id=target_model_id,
                priority=prio,
                status=TaskStatus.QUEUED,
                created_at=time.time(),
            )
            self.tasks[task_id] = task
            self._record_event_locked(EventType.TASK_QUEUED, {"task": task.to_dict()})
            self._persist_tasks_locked()
            return task

    def execute_task(self, task_id: str) -> SwarmTask:
        """Executes a queued task inside an Exception Enclave, managing VRAM allocation and eviction."""
        with self.lock:
            if task_id not in self.tasks:
                raise KeyError(f"Task {task_id} not found.")
            task = self.tasks[task_id]
            model_id = task.target_model_id or self.select_best_model_for_specialty(task.specialty_required)

        # 1. Allocate model VRAM (outside lock to prevent deadlocks)
        try:
            model, evicted_ids = self.vram.allocate_model(model_id)
            if evicted_ids:
                with self.lock:
                    self.telemetry["auto_evictions_triggered"] += len(evicted_ids)
                    self._record_event_locked(EventType.MODEL_EVICTED, {"evicted_model_ids": evicted_ids})
            with self.lock:
                self._record_event_locked(EventType.MODEL_LOADED, {"model_id": model_id})
        except OomPreventionError as oom_err:
            with self.lock:
                task.status = TaskStatus.FAILED
                task.completed_at = time.time()
                task.error_witness = {
                    "error_type": "OomPreventionError",
                    "message": str(oom_err),
                    "blast_radius_isolated": True,
                    "timestamp": time.time(),
                }
                self.telemetry["tasks_failed"] += 1
                self.telemetry["enclave_faults_isolated"] += 1
                self._record_event_locked(EventType.TASK_FAILED, {"task_id": task_id, "error": str(oom_err)})
                self._persist_tasks_locked()
            return task

        # 2. Acquire inference lease
        self.vram.acquire_inference(model_id)
        start_time = time.time()

        with self.lock:
            task.status = TaskStatus.PROCESSING
            task.vram_lease_mb = model.total_memory_mb
            self.telemetry["tasks_dispatched"] += 1
            self._record_event_locked(EventType.TASK_DISPATCHED, {"task_id": task_id, "model_id": model_id})

        # 3. Execute inside Demarcated Exception Enclave [L1-016]
        with ExceptionEnclave("INFERENCE_ENCLAVE", f"task_{task_id}_on_{model_id}") as enclave:
            # Check for simulated fault triggers
            if "CRASH_ENCLAVE_FAULT" in task.prompt:
                raise RuntimeError("Simulated inference worker memory fault")

            # Simulate realistic local LLM generation
            time.sleep(0.015)  # 15ms simulated tensor processing latency
            response_text, token_count = self._synthesize_local_response(model, task.prompt)
            task.result_output = response_text
            task.tokens_processed = token_count

        latency = round((time.time() - start_time) * 1000.0, 2)
        task.latency_ms = latency
        task.completed_at = time.time()

        # 4. Safely release inference lease regardless of success or failure
        self.vram.release_inference(model_id)

        with self.lock:
            if enclave.caught:
                task.status = TaskStatus.FAILED
                task.error_witness = enclave.witness
                self.telemetry["tasks_failed"] += 1
                self.telemetry["enclave_faults_isolated"] += 1
                self._record_event_locked(EventType.TASK_FAILED, {"task_id": task_id, "witness": enclave.witness})
            else:
                task.status = TaskStatus.COMPLETED
                self.telemetry["tasks_completed"] += 1
                self.telemetry["tokens_generated"] += task.tokens_processed
                self.telemetry["total_latency_ms"] += latency
                if self.telemetry["tasks_completed"] > 0:
                    self.telemetry["avg_latency_ms"] = round(
                        self.telemetry["total_latency_ms"] / self.telemetry["tasks_completed"], 2
                    )
                self._record_event_locked(EventType.TASK_COMPLETED, {"task_id": task_id, "latency_ms": latency})

            self._persist_tasks_locked()

        return task

    def _synthesize_local_response(self, model: ModelDescriptor, prompt: str) -> Tuple[str, int]:
        """Generates realistic responses for local edge model execution."""
        p_lower = prompt.lower()
        if model.specialty == ModelSpecialty.CODING or "code" in p_lower or "python" in p_lower:
            resp = (
                f"[{model.name}] Optimized Implementation:\n\n"
                f"```python\n"
                f"def solve_constraint_graph(nodes, edges):\n"
                f"    # Bounded domain propagation with AC-3 arc consistency\n"
                f"    queue = list(edges)\n"
                f"    while queue:\n"
                f"        (xi, xj) = queue.pop(0)\n"
                f"        if revise_domain(xi, xj):\n"
                f"            if len(nodes[xi]) == 0:\n"
                f"                return None  # Domain wiped out\n"
                f"    return nodes\n"
                f"```\n"
                f"Generated in {model.context_length} context envelope with {model.quantization} precision."
            )
            tokens = 142
        elif model.specialty == ModelSpecialty.FAST_SUMMARY or "summar" in p_lower:
            resp = (
                f"[{model.name}] Executive Summary:\n"
                f"1. Unified memory allocation stabilized under {model.total_memory_mb}MB.\n"
                f"2. Physical Landauer dissipation bounds enforced with zero allocator faults.\n"
                f"3. Demarcated enclaves contained 100% of transient runtime perturbations."
            )
            tokens = 78
        elif model.specialty == ModelSpecialty.VISION_EMBEDDING:
            resp = f"[{model.name}] Generated 1024-dimensional dense vector embeddings with L2 normalization."
            tokens = 32
        else:
            resp = (
                f"[{model.name}] Reasoning Trace:\n"
                f"Premise verified: Memory safety invariant holds unconditionally via LRU cache eviction. "
                f"No global mutex contention detected across active subprocess enclaves."
            )
            tokens = 96
        return resp, tokens

    def cancel_task(self, task_id: str) -> SwarmTask:
        """Cancels a queued task."""
        with self.lock:
            if task_id not in self.tasks:
                raise KeyError(f"Task {task_id} not found.")
            task = self.tasks[task_id]
            if task.status == TaskStatus.QUEUED:
                task.status = TaskStatus.CANCELLED
                task.completed_at = time.time()
                self._record_event_locked(EventType.TASK_CANCELLED, {"task_id": task_id})
                self._persist_tasks_locked()
            return task

    def get_all_tasks(self) -> List[Dict[str, Any]]:
        """Returns all tasks sorted by priority and creation time."""
        with self.lock:
            items = list(self.tasks.values())
            prio_order = {TaskPriority.HIGH: 0, TaskPriority.NORMAL: 1, TaskPriority.BATCH: 2}
            items.sort(key=lambda t: (prio_order.get(t.priority, 1), -t.created_at))
            return [t.to_dict() for t in items]

    def get_telemetry(self) -> Dict[str, Any]:
        """Returns aggregate orchestrator telemetry."""
        with self.lock:
            vram_state = self.vram.get_vram_state()
            models_state = self.vram.get_models()
            resident_count = sum(1 for m in models_state if m["status"] in ["RESIDENT", "BUSY"])
            return {
                "daemon": "Axioma Swarm v1.0",
                "telemetry": self.telemetry,
                "vram": vram_state,
                "resident_models_count": resident_count,
                "total_models_catalog": len(models_state),
                "total_events": len(self.events),
                "timestamp": time.time(),
            }
