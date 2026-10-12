"""Asynchronous Synthesis Worker Pool and Job Queue Manager.

Enforces Compositional Boundary Isolation ([L1-015_1]) by offloading CPU-bound
backtracking CSP searches to an isolated background thread pool, protecting web I/O responsiveness.
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
import threading
import time
import uuid
from typing import Dict, Optional

from csp_engine import (
    TEMPLATE_7X7_QUICK,
    TEMPLATE_9X9_MIDI,
    CrosswordCspEngine,
    LandauerBudgetExceededError,
)
from models import CrosswordGrid, JobStatus, SynthesisJob
from session_store import GLOBAL_STORE


class CrosswordWorkerPool:
    """Manages asynchronous puzzle synthesis jobs with concurrency limits and progress tracking."""

    def __init__(self, max_concurrent_workers: int = 2):
        self.max_concurrent_workers = max_concurrent_workers
        self.engine = CrosswordCspEngine()
        self._jobs: Dict[str, SynthesisJob] = {}
        self._executor = ThreadPoolExecutor(max_workers=max_concurrent_workers)
        self._lock = threading.Lock()

    def get_job(self, job_id: str) -> Optional[SynthesisJob]:
        with self._lock:
            return self._jobs.get(job_id)

    def list_jobs(self) -> Dict[str, SynthesisJob]:
        with self._lock:
            return dict(self._jobs)

    def enqueue_synthesis_job(self, grid_size: int = 7) -> SynthesisJob:
        """Enqueues a new crossword synthesis job into the isolated thread pool ([L1-015_1])."""
        job_id = f"job_{uuid.uuid4().hex[:8]}"

        job = SynthesisJob(
            job_id=job_id,
            status=JobStatus.PENDING,
            grid_size=grid_size,
            created_at=time.time(),
        )
        with self._lock:
            self._jobs[job_id] = job

        self._executor.submit(self._run_job_worker, job_id)
        return job

    def _run_job_worker(self, job_id: str) -> None:
        """Worker task executing on a background thread."""
        with self._lock:
            job = self._jobs.get(job_id)
            if not job:
                return
            job.status = JobStatus.RUNNING

        try:
            if job.grid_size == 9:
                template = TEMPLATE_9X9_MIDI
                grid_id = f"midi_9x9_{uuid.uuid4().hex[:6]}"
                title = "Axioma Midi 9x9 Cryptic"
            else:
                template = TEMPLATE_7X7_QUICK
                grid_id = f"quick_7x7_{uuid.uuid4().hex[:6]}"
                title = "Axioma Quick 7x7 Cryptic"

            def progress_cb(backtracks: int, pruned: int, joules: float) -> None:
                with self._lock:
                    job.backtracks_count = backtracks
                    job.pruned_candidates_count = pruned
                    job.joules_dissipated = joules
                    job.progress_pct = min(95.0, (backtracks / 2000.0) * 100.0)

            grid = self.engine.generate_puzzle(
                grid_id=grid_id,
                title=title,
                grid_template=template,
                max_backtracks=4000,
            )

            # Save synthesized grid to session store
            GLOBAL_STORE.save_puzzle(grid)

            with self._lock:
                job.status = JobStatus.COMPLETED
                job.progress_pct = 100.0
                job.result_grid = grid
                job.completed_at = time.time()

        except LandauerBudgetExceededError as e:
            with self._lock:
                job.status = JobStatus.TIMEOUT
                job.error = str(e)
                job.completed_at = time.time()
        except Exception as e:
            with self._lock:
                job.status = JobStatus.FAILED
                job.error = str(e)
                job.completed_at = time.time()


# Global singleton worker pool
GLOBAL_WORKER_POOL = CrosswordWorkerPool()
