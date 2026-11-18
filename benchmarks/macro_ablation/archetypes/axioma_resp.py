r"""Axioma-RESP Archetype: Redis RESP2 Wire Protocol Server.

Benchmark Archetype (Ontological Drift & Protocol Conformance):
Tests:
- Exact byte-level RESP2 wire protocol framing:
  Simple Strings (+), Errors (-), Integers (:), Bulk Strings ($), Arrays (*)
- Pipelined command execution over raw socket streams
- 5 core commands: PING, SET, GET, INCR, DEL
- Buffer chunking & incomplete frame recovery
- Interoperability with standard redis client wire formats
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from ..domain_models import BenchmarkArchetype


def get_archetype() -> BenchmarkArchetype:
    """Returns the formal benchmark archetype specification for Axioma-RESP."""
    return BenchmarkArchetype(
        id="axioma_resp",
        name="Axioma-RESP (Redis RESP2 Wire Protocol Server)",
        domain="Wire Protocols & Socket Framing",
        prompt=(
            "Synthesize an asynchronous Redis RESP2 wire protocol server supporting raw TCP socket framing, "
            "pipelined binary requests, exact RESP serialization (simple strings +, errors -, integers :, "
            "bulk strings $, arrays *), and five core commands (PING, SET, GET, INCR, DEL)."
        ),
        specification={
            "protocol_version": "RESP2",
            "supported_commands": ["PING", "SET", "GET", "INCR", "DEL"],
            "max_bulk_string_len": 512 * 1024 * 1024,
            "pipelining_supported": True,
        },
        expected_verbs=[
            "parse_resp",
            "serialize_resp",
            "handle_command",
            "cmd_ping",
            "cmd_set",
            "cmd_get",
            "cmd_incr",
            "cmd_del",
        ],
        expected_endpoints=[],
        expected_models=[
            "RespType",
            "RespMessage",
            "RedisCommand",
            "RespParserState",
        ],
        state_transitions=[
            {"from": "CONNECTED", "to": "PARSING", "action": "bytes_received", "valid": True},
            {"from": "PARSING", "to": "EXECUTING", "action": "frame_complete", "valid": True},
            {"from": "EXECUTING", "to": "SERIALIZING", "action": "command_done", "valid": True},
            {"from": "SERIALIZING", "to": "DRAINING", "action": "send_bytes", "valid": True},
            {"from": "DRAINING", "to": "PARSING", "action": "drain_complete", "valid": True},
        ],
        chaos_payloads=[
            {
                "name": "partial_chunk_framing",
                "raw_bytes_chunks": [b"*2\r\n$4\r\nPI", b"NG\r\n$4\r\nPONG\r\n"],
                "expect_response": b"$4\r\nPONG\r\n",
            },
            {
                "name": "unknown_command_error",
                "raw_bytes": b"*1\r\n$7\r\nUNKNOWN\r\n",
                "expect_error_prefix": b"-ERR",
            },
            {
                "name": "corrupted_array_length",
                "raw_bytes": b"*-5\r\n",
                "expect_error_or_close": True,
            },
        ],
        target_loc_budget=300,
        target_token_budget=15000,
    )
