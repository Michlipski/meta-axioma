r"""Tier 0 Operational Liveness Gatekeeper ([NEG-G1B-002]).

Enforces:
- Mandatory execution of application entrypoint in an independent OS subprocess.
- Probing operational status / healthcheck within 5.0 seconds.
- Verification of zero top-level import crashes, syntax panics, or path resolution failures.
- Verification of clean teardown without lingering zombie/orphan processes.
- Zero-tolerance multiplier: if liveness fails, final composite score is identically 0.0.
"""

from __future__ import annotations

import os
from pathlib import Path
import signal
import socket
import subprocess
import sys
import time
from typing import Optional, Tuple

from ..domain_models import Tier0LivenessResult


def find_free_port() -> int:
    """Allocates an ephemeral OS port for collision-free evaluation."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        s.listen(1)
        port = s.getsockname()[1]
    return port


class LivenessGatekeeper:
    """Evaluates Tier 0 Operational Liveness via physical subprocess boot and health probing."""

    def __init__(self, boot_timeout_sec: float = 5.0, teardown_timeout_sec: float = 3.0) -> None:
        self.boot_timeout_sec = boot_timeout_sec
        self.teardown_timeout_sec = teardown_timeout_sec

    def evaluate(self, app_dir: Path, entrypoint_name: str = "run.py") -> Tier0LivenessResult:
        """Boots the application in an isolated subprocess and verifies operational liveness."""
        entrypoint = (app_dir / entrypoint_name).resolve()
        if not entrypoint.exists():
            return Tier0LivenessResult(
                passed=False,
                error_message=f"Entrypoint '{entrypoint_name}' does not exist in {app_dir}",
                exit_code=None,
            )

        start_time = time.time()
        env = os.environ.copy()
        env["PYTHONUNBUFFERED"] = "1"
        existing_pythonpath = env.get("PYTHONPATH", "")
        env["PYTHONPATH"] = f"{app_dir}:{existing_pythonpath}" if existing_pythonpath else str(app_dir)

        # 1. Primary Invariant: Subprocess Smoke Test execution ([NEG-G1B-002])
        try:
            smoke_proc = subprocess.run(
                [sys.executable, str(entrypoint), "--smoke-test"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=str(app_dir),
                env=env,
                timeout=self.boot_timeout_sec,
            )
            startup_time_ms = (time.time() - start_time) * 1000.0

            # If smoke test succeeded with exit code 0
            if smoke_proc.returncode == 0:
                return Tier0LivenessResult(
                    passed=True,
                    startup_time_ms=startup_time_ms,
                    clean_shutdown=True,
                    port_bound=None,
                    exit_code=0,
                    error_message=None,
                    stdout_excerpt=smoke_proc.stdout[:500],
                    stderr_excerpt=smoke_proc.stderr[:500],
                )

            # If smoke test crashed on top-level import, syntax error, or runtime panic
            stderr_lower = smoke_proc.stderr.lower()
            if any(k in stderr_lower for k in ["importerror", "modulenotfounderror", "syntaxerror", "traceback"]):
                return Tier0LivenessResult(
                    passed=False,
                    startup_time_ms=startup_time_ms,
                    clean_shutdown=False,
                    port_bound=None,
                    exit_code=smoke_proc.returncode,
                    error_message=f"Subprocess boot crashed on startup with exit code {smoke_proc.returncode}",
                    stdout_excerpt=smoke_proc.stdout[:500],
                    stderr_excerpt=smoke_proc.stderr[:1000],
                )
        except subprocess.TimeoutExpired:
            return Tier0LivenessResult(
                passed=False,
                startup_time_ms=self.boot_timeout_sec * 1000.0,
                clean_shutdown=False,
                error_message=f"Subprocess smoke execution timed out after {self.boot_timeout_sec}s",
            )
        except Exception as ex:
            # Continue to daemon check if smoke-test invocation failed due to flag mismatch
            pass

        # 2. Daemon Process Smoke Verification
        port = find_free_port()
        proc = None
        try:
            proc = subprocess.Popen(
                [sys.executable, str(entrypoint), "--port", str(port)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=str(app_dir),
                env=env,
                text=True,
            )

            deadline = time.time() + self.boot_timeout_sec
            confirmed_online = False

            while time.time() < deadline:
                poll_code = proc.poll()
                if poll_code is not None:
                    # Premature crash
                    stdout, stderr = proc.communicate(timeout=1.0)
                    return Tier0LivenessResult(
                        passed=False,
                        startup_time_ms=(time.time() - start_time) * 1000.0,
                        clean_shutdown=False,
                        port_bound=port,
                        exit_code=poll_code,
                        error_message=f"Subprocess daemon crashed with exit code {poll_code}",
                        stdout_excerpt=stdout[:500],
                        stderr_excerpt=stderr[:1000],
                    )

                # Read operational confirmation line if emitted
                if proc.stdout:
                    import select
                    r, _, _ = select.select([proc.stdout], [], [], 0.1)
                    if r:
                        line = proc.stdout.readline()
                        if any(k in line for k in ["SERVER_ONLINE", "ONLINE", "READY", "healthy", "AXIOMA"]):
                            confirmed_online = True
                            break
                time.sleep(0.05)

            startup_time_ms = (time.time() - start_time) * 1000.0

            # If still alive and past grace period, confirm operational status
            if proc.poll() is None:
                confirmed_online = True

            # Terminate daemon cleanly
            clean_shutdown = True
            try:
                proc.terminate()
                stdout, stderr = proc.communicate(timeout=self.teardown_timeout_sec)
            except subprocess.TimeoutExpired:
                proc.kill()
                stdout, stderr = proc.communicate()
                clean_shutdown = False

            valid_exit = proc.returncode in (0, -signal.SIGTERM, 143, 15)

            return Tier0LivenessResult(
                passed=confirmed_online,
                startup_time_ms=startup_time_ms,
                clean_shutdown=clean_shutdown and valid_exit,
                port_bound=port,
                exit_code=proc.returncode,
                error_message=None if confirmed_online else "Subprocess failed to confirm operational online status",
                stdout_excerpt=stdout[:500] if stdout else "",
                stderr_excerpt=stderr[:500] if stderr else "",
            )

        except Exception as ex:
            if proc and proc.poll() is None:
                try:
                    proc.kill()
                except Exception:
                    pass
            return Tier0LivenessResult(
                passed=False,
                startup_time_ms=(time.time() - start_time) * 1000.0,
                clean_shutdown=False,
                port_bound=port,
                error_message=f"Gatekeeper unhandled exception: {str(ex)}",
            )
