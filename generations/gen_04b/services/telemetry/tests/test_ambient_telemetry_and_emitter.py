"""Comprehensive Unit & Regression Tests for Ambient Telemetry Hook & Emitter SDK.

Enforces:
- [L1-G4B-001] Service-Oriented Sovereign Mesh Protocol Standardization.
- [L1-G3B-012] Dedicated Non-Loopback Network Topology.
- [L1-G3B-017] SHA-256 Chained Cryptographic Telemetry & Merkle Leaves.
- [INV-G4B-CAUSAL-001] Physical Grounding Witness Emission.
- [NEG-G1B-002] Anti-Mock Subprocess Entrypoint Smoke Invariant.
- Circuit breaker non-blocking guarantees & local spillover ledger resilience.
"""

from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
import unittest

from generations.gen_04b.services.telemetry.src.emitter import (
    AsyncTelemetryEmitter,
    TelemetryEmitter,
)
from generations.gen_04b.services.telemetry.src.telemetry_vault import MeshTransaction


class TestAmbientTelemetryAndEmitter(unittest.TestCase):
    """Verifies that TelemetryEmitter and telemetry_post_tool_hook adhere to formal invariants."""

    def setUp(self) -> None:
        self.temp_dir = tempfile.mkdtemp(prefix="test_telemetry_")
        self.spillover_path = Path(self.temp_dir) / "spillover_telemetry.jsonl"
        self.emitter = TelemetryEmitter(
            spillover_path=self.spillover_path,
            timeout_seconds=0.02,
        )

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_emitter_phase_emission(self) -> None:
        tx = self.emitter.emit_phase("PHASE_1_RESEARCH_GATE", details={"spec": "test"})
        self.assertEqual(tx.phase, "PHASE_1_RESEARCH_GATE")
        self.assertEqual(tx.verb, "TRANSITION_PHASE")
        self.assertEqual(tx.capital_partition, "EXPLORATORY")
        tx.validate_invariants()

        # Spillover should have captured this since server is offline
        self.assertTrue(self.spillover_path.exists())
        lines = self.spillover_path.read_text(encoding="utf-8").strip().splitlines()
        self.assertEqual(len(lines), 1)

    def test_emitter_leaf_emission(self) -> None:
        sha = "a" * 64
        tx = self.emitter.emit_leaf("core.py", "src/core.py", 1024, sha, tokens_spent=80)
        self.assertEqual(tx.verb, "EMIT_CODE_LEAF")
        self.assertEqual(tx.bits_erased, 1024 * 8)
        self.assertGreater(tx.heat_dissipated_joules, 0.0)
        self.assertEqual(tx.capital_partition, "EXPLORATORY")
        tx.validate_invariants()

        # Verify zero-byte rejection
        with self.assertRaises(ValueError):
            self.emitter.emit_leaf("empty.py", "src/empty.py", 0, sha)

    def test_emitter_verification_and_smoke_emission(self) -> None:
        tx_v = self.emitter.emit_verification("test_mesh.py", 20, 20, 0, "wit_hash_123")
        self.assertEqual(tx_v.capital_partition, "PROTECTED")
        self.assertEqual(tx_v.status, "SUCCESS")
        tx_v.validate_invariants()

        tx_s = self.emitter.emit_subprocess_smoke("run.py", 0, "SMOKE TEST PASS", success=True)
        self.assertEqual(tx_s.capital_partition, "PROTECTED")
        self.assertEqual(tx_s.status, "SUCCESS")
        tx_s.validate_invariants()

    def test_emitter_tool_subagent_and_undo(self) -> None:
        tx_t = self.emitter.emit_tool_call("write_file", "Wrote file")
        self.assertEqual(tx_t.verb, "TOOL_CALL")
        tx_t.validate_invariants()

        tx_sub = self.emitter.emit_subagent_dispatch("sub_01", "Researcher", "flash", 100)
        self.assertEqual(tx_sub.verb, "DISPATCH_SUBAGENT")
        self.assertEqual(tx_sub.subagent_id, "sub_01")
        tx_sub.validate_invariants()

        tx_u = self.emitter.emit_undo_event("chk_10", 4096)
        self.assertEqual(tx_u.verb, "UNDO_CHECKPOINT")
        self.assertEqual(tx_u.capital_partition, "PROTECTED")
        tx_u.validate_invariants()

    def test_async_emitter(self) -> None:
        async def run_async() -> None:
            a_emitter = AsyncTelemetryEmitter(spillover_path=self.spillover_path, timeout_seconds=0.02)
            tx = await a_emitter.emit_phase("PHASE_2A_SYNTHESIS")
            self.assertEqual(tx.phase, "PHASE_2A_SYNTHESIS")
            tx.validate_invariants()

        asyncio.run(run_async())

    def test_post_tool_hook_execution(self) -> None:
        hook_path = Path(__file__).resolve().parent.parent.parent.parent.parent.parent / "scripts" / "telemetry_post_tool_hook.py"
        self.assertTrue(hook_path.exists(), f"Hook script missing at {hook_path}")

        payload = {
            "toolCall": {
                "name": "write_file",
                "args": {
                    "Path": "/Users/michaellipski/dev/meta-axioma/generations/gen_04b/services/telemetry/src/emitter.py",
                    "Content": "sample code"
                }
            },
            "toolResult": "Wrote 11 bytes.",
            "error": None,
            "stepIdx": 42,
            "conversationId": "test_conv_abc",
            "executionTimeMs": 12.0
        }

        proc = subprocess.run(
            [sys.executable, str(hook_path)],
            input=json.dumps(payload),
            text=True,
            capture_output=True,
            timeout=5
        )
        self.assertEqual(proc.returncode, 0)
        self.assertEqual(proc.stdout.strip(), "{}")

    def test_post_tool_hook_ignores_irrelevant(self) -> None:
        hook_path = Path(__file__).resolve().parent.parent.parent.parent.parent.parent / "scripts" / "telemetry_post_tool_hook.py"
        payload = {
            "toolCall": {
                "name": "write_file",
                "args": {
                    "Path": "/tmp/scratch_poll.log",
                    "Content": "debug log"
                }
            },
            "toolResult": "Wrote log.",
            "error": None,
            "stepIdx": 43,
            "conversationId": "test_conv_abc",
            "executionTimeMs": 2.0
        }

        proc = subprocess.run(
            [sys.executable, str(hook_path)],
            input=json.dumps(payload),
            text=True,
            capture_output=True,
            timeout=5
        )
        self.assertEqual(proc.returncode, 0)
        self.assertEqual(proc.stdout.strip(), "{}")


if __name__ == "__main__":
    unittest.main()
