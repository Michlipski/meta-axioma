r"""Axioma-Raft Archetype: Distributed Leased Consensus Coordinator.

Benchmark Archetype (Crucible):
Tests:
- Distributed consensus statechart soundness (FOLLOWER -> CANDIDATE -> LEADER -> STEPPED_DOWN)
- Heartbeat-driven leader lease enforcement and term monotonicity
- Majority quorum log replication (2/3 nodes)
- Atomic multi-step rollback under simulated network drops
- Pure Python 3.14 standard library (asyncio, dataclasses)
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List
import textwrap

from ..domain_models import AblationMode, BenchmarkArchetype


def get_archetype() -> BenchmarkArchetype:
    """Returns the formal benchmark archetype specification for Axioma-Raft."""
    return BenchmarkArchetype(
        id="axioma_raft",
        name="Axioma-Raft (Distributed Consensus & Leader Lease Coordinator)",
        domain="Distributed Systems & Consensus",
        prompt=(
            "Synthesize an asynchronous 3-node distributed consensus coordinator implementing leader leases, "
            "term elections, heartbeat-driven log replication, and atomic multi-step rollback under simulated network drop."
        ),
        specification={
            "consensus_protocol": "Raft-Variant",
            "cluster_size": 3,
            "quorum_size": 2,
            "heartbeat_interval_sec": 0.5,
            "lease_duration_sec": 2.0,
            "persistence": "IN_MEMORY_WITH_WAL_SNAPSHOT",
        },
        expected_verbs=[
            "request_vote",
            "append_entries",
            "replicate_log",
            "heartbeat",
            "step_down",
            "commit_entry",
            "rollback_entry",
            "health_check",
        ],
        expected_endpoints=[
            "GET /health",
            "GET /status",
            "POST /vote",
            "POST /append",
            "POST /propose",
            "GET /log",
            "GET /stats",
        ],
        expected_models=[
            "RaftRole",
            "LogEntry",
            "VoteRequest",
            "VoteResponse",
            "AppendEntriesRequest",
            "AppendEntriesResponse",
            "RaftNode",
        ],
        state_transitions=[
            {"from": "FOLLOWER", "to": "CANDIDATE", "action": "election_timeout", "valid": True},
            {"from": "CANDIDATE", "to": "LEADER", "action": "receive_quorum_votes", "valid": True},
            {"from": "CANDIDATE", "to": "FOLLOWER", "action": "discover_higher_term", "valid": True},
            {"from": "LEADER", "to": "FOLLOWER", "action": "discover_higher_term", "valid": True},
            {"from": "LEADER", "to": "STEPPED_DOWN", "action": "lease_expired", "valid": True},
            {"from": "STEPPED_DOWN", "to": "FOLLOWER", "action": "reset", "valid": True},
        ],
        chaos_payloads=[
            {
                "name": "split_brain_simulated_drop",
                "method": "POST",
                "path": "/propose",
                "payload": {"entry": "simulated_split_payload"},
                "simulate_drop": True,
            },
            {
                "name": "stale_term_heartbeat",
                "method": "POST",
                "path": "/append",
                "payload": {"term": 0, "leader_id": "ghost_leader", "entries": []},
            },
            {
                "name": "corrupted_log_index",
                "method": "POST",
                "path": "/append",
                "payload": {"term": 100, "prev_log_index": -999, "entries": []},
            },
            {
                "name": "burst_concurrent_proposals",
                "burst_count": 25,
                "payload": {"key": "state_seq", "val": "tick"},
            },
        ],
        target_loc_budget=450,
        target_token_budget=20000,
    )
