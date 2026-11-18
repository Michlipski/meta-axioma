r"""Axioma-Repair Archetype: Concurrency Race Condition & Resource Leak Repair.

Benchmark Archetype (Reality Grounding & Anti-Mock Verification):
Tests:
- Identification of latent race condition in async connection pool
- Repair of unclosed socket file descriptor leaks in error paths
- Enforcement of bounded queue wait timeouts without deadlocks
- Verification that test suite uses real socketpairs rather than mock stubs
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from ..domain_models import BenchmarkArchetype


def get_archetype() -> BenchmarkArchetype:
    """Returns the formal benchmark archetype specification for Axioma-Repair."""
    return BenchmarkArchetype(
        id="axioma_repair",
        name="Axioma-Repair (Concurrency Race Condition & Leak Fix Gauntlet)",
        domain="Fault Diagnosis & Concurrency Repair",
        prompt=(
            "Diagnose and repair an asynchronous connection pool daemon (async_pool.py) "
            "suffering from two latent defects: a concurrency race condition during pool exhaustion "
            "under high contention, and an unclosed socket resource leak in error handling enclaves. "
            "Synthesize the patch, enforce bounded waiting, and provide non-mock regression tests."
        ),
        specification={
            "pool_max_size": 10,
            "acquire_timeout_sec": 2.0,
            "leak_prevention": "TRY_FINALLY_RESOURCE_GUARD",
            "concurrency_primitives": "asyncio.Semaphore_and_Lock",
        },
        expected_verbs=[
            "acquire_connection",
            "release_connection",
            "close_pool",
            "health_check",
            "diagnose_leak",
            "purge_idle",
        ],
        expected_endpoints=[],
        expected_models=[
            "PooledConnection",
            "PoolConfig",
            "PoolStats",
            "PoolState",
        ],
        state_transitions=[
            {"from": "READY", "to": "BUSY", "action": "acquire", "valid": True},
            {"from": "BUSY", "to": "EXHAUSTED", "action": "pool_full", "valid": True},
            {"from": "EXHAUSTED", "to": "READY", "action": "release", "valid": True},
            {"from": "READY", "to": "CLOSING", "action": "close", "valid": True},
            {"from": "CLOSING", "to": "CLOSED", "action": "drain_complete", "valid": True},
        ],
        chaos_payloads=[
            {
                "name": "contention_burst",
                "concurrent_clients": 50,
                "hold_time_ms": 10,
                "expect_zero_deadlocks": True,
            },
            {
                "name": "simulated_client_crash_leak",
                "crash_in_context_manager": True,
                "expect_clean_reclaim": True,
            },
        ],
        target_loc_budget=350,
        target_token_budget=16000,
    )
