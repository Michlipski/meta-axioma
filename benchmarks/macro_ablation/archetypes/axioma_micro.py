r"""Axioma-Micro Archetype: Single-File Streaming NDJSON Log Filter.

Benchmark Archetype (Scalpel / Weakness Exposure):
Tests:
- Extreme LOC parsimony (target < 120 LOC)
- Single-file zero-dependency stream parsing
- Bounded O(K) memory reservoir / sliding-window percentiles
- Signal-driven flush (SIGINT / EOF)
- Thermodynamic Landauer efficiency (penalizes multi-file bloat)
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from ..domain_models import BenchmarkArchetype


def get_archetype() -> BenchmarkArchetype:
    """Returns the formal benchmark archetype specification for Axioma-Micro."""
    return BenchmarkArchetype(
        id="axioma_micro",
        name="Axioma-Micro (Single-File Streaming NDJSON Log Filter)",
        domain="CLI & High-Throughput Stream Parsing",
        prompt=(
            "Synthesize a zero-dependency, single-file streaming CLI utility (logfilter.py) "
            "that reads NDJSON log lines from stdin, computes sliding-window latency percentiles "
            "(p50, p95, p99) with bounded O(K) memory, and emits summary statistics upon EOF or SIGINT."
        ),
        specification={
            "execution_mode": "STREAMING_STDIN_CLI",
            "memory_bound_records": 1000,
            "window_size_sec": 60,
            "percentiles": [50, 95, 99],
            "single_file_target": "logfilter.py",
        },
        expected_verbs=[
            "process_line",
            "parse_ndjson",
            "update_percentiles",
            "emit_summary",
            "handle_sigint",
        ],
        expected_endpoints=[],
        expected_models=[
            "LogEntry",
            "SummaryReport",
            "PercentileTracker",
        ],
        state_transitions=[
            {"from": "IDLE", "to": "STREAMING", "action": "start_reading", "valid": True},
            {"from": "STREAMING", "to": "EMITTING", "action": "eof_or_sigint", "valid": True},
            {"from": "EMITTING", "to": "COMPLETED", "action": "finish", "valid": True},
        ],
        chaos_payloads=[
            {
                "name": "malformed_ndjson_line",
                "input_line": "{invalid_json_stream_line\n",
                "expect_skip": True,
            },
            {
                "name": "non_numeric_latency",
                "input_line": '{"timestamp": 1700000000, "latency_ms": "not_a_number"}\n',
                "expect_skip": True,
            },
            {
                "name": "empty_stream_eof",
                "input_line": "",
                "expect_empty_summary": True,
            },
        ],
        target_loc_budget=120,
        target_token_budget=8000,
    )
