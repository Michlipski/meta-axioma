"""Substrate Verification Test Suite for Zenith Telemetry Vault (`test_zenith_telemetry_vault.py`).

Enforces:
- [NEG-G1B-001] Mandatory Substrate Test Execution (exit code 0, non-zero passing assertions).
- [L1-G4B-001] Sovereign Mesh Protocol Standardization.
- [L1-G3B-011] Universal Compositional Contract IR Invariants.
- [L1-G3B-012] Dedicated Non-Loopback Network Topology.
- [L1-G3B-018] Thermodynamic Capital & Landauer Heat Dissipation.
- [L1-002] 1-Tap Functorial Rollback Adjoint Inversion.
"""

from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path
import sqlite3
import tempfile
import time
import unittest

from generations.gen_04b.services.telemetry.src.cockpit_server import CockpitServer
from generations.gen_04b.services.telemetry.src.ingest_server import IngestServer
from generations.gen_04b.services.telemetry.src.rollback_engine import RollbackEngine
from generations.gen_04b.services.telemetry.src.telemetry_vault import (
    BOLTZMANN_K,
    LN_2,
    CockpitTimelineWindow,
    MeshTransaction,
    SystemStateKeyframe,
    TelemetryVault,
    assert_non_loopback,
)


class TestZenithTelemetryVault(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test_vault.db"
        self.vault = TelemetryVault(db_path=str(self.db_path), keyframe_interval=500)

    def tearDown(self) -> None:
        self.vault.close()
        self.temp_dir.cleanup()

    def test_01_wal_pragmas_and_indices_initialization(self) -> None:
        """Verifies SQLite WAL mode, normal synchronous, composite indices, and DDL schema."""
        conn = self.vault._get_connection()
        journal_mode = conn.execute("PRAGMA journal_mode;").fetchone()[0]
        sync_mode = conn.execute("PRAGMA synchronous;").fetchone()[0]

        self.assertEqual(journal_mode.lower(), "wal")
        # 1 = NORMAL synchronous in SQLite
        self.assertEqual(sync_mode, 1)

        # Check tables exist
        tables = [
            r[0]
            for r in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table';"
            ).fetchall()
        ]
        self.assertIn("mesh_transactions", tables)
        self.assertIn("system_state_keyframes", tables)
        self.assertIn("undo_commands", tables)

        # Check composite indices
        indices = [
            r[0]
            for r in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='index';"
            ).fetchall()
        ]
        self.assertIn("idx_tx_time_clock", indices)
        self.assertIn("idx_tx_causal", indices)
        self.assertIn("idx_tx_trace", indices)
        self.assertIn("idx_tx_channel", indices)
        self.assertIn("idx_kf_time", indices)

    def test_02_high_throughput_batch_insert_and_keyframing(self) -> None:
        """Verifies batch insertion of 1,200 micro-transactions triggers automatic keyframe snapshots every 500 tx."""
        t_base = time.time_ns()
        tx_batch = []
        for i in range(1200):
            tx = MeshTransaction.create(
                transaction_id=f"tx_test_{i:05d}",
                prev_transaction_hash="0" * 64,
                logical_clock=i + 1,
                causal_task_id=f"task_batch_{i // 100}",
                step_index=i,
                phase="PHASE_2A_SYNTHESIS",
                source_service="services/builder",
                source_endpoint="192.168.40.20:8442",
                target_service="services/telemetry",
                target_endpoint="192.168.40.40:8446",
                channel_id="channel_builder_telemetry",
                verb="OP_EXEC",
                payload_summary=f"Synthetic micro-transaction #{i}",
                payload_data={"index": i, "payload": "sample_data"},
                bpe_tokens_in=10,
                bpe_tokens_out=20,
                bits_erased=40,
                capital_partition="EXPLORATORY" if i < 800 else "PROTECTED",
                status="SUCCESS",
                timestamp_ns=t_base + i * 1_000_000,
            )
            tx_batch.append(tx)

        inserted_count = self.vault.insert_batch(tx_batch)
        self.assertEqual(inserted_count, 1200)

        summary = self.vault.get_summary()
        self.assertEqual(summary["total_transactions"], 1200)
        # Should have captured at least 2 keyframes (at 500 and 1000)
        self.assertGreaterEqual(summary["total_keyframes"], 2)
        self.assertEqual(summary["cumulative_tokens_burned"], 1200 * 30)
        self.assertEqual(summary["cumulative_bits_erased"], 1200 * 40)

        expected_heat = 1200 * 40 * BOLTZMANN_K * 300.0 * LN_2
        self.assertAlmostEqual(summary["cumulative_heat_dissipated_joules"], expected_heat, places=15)

    def test_03_temporal_window_sub_millisecond_query(self) -> None:
        """Verifies QueryTemporalWindow executes under 15ms SLA and returns correct keyframe + deltas."""
        t_base = time.time_ns()
        txs = [
            MeshTransaction.create(
                transaction_id=f"tx_win_{i}",
                prev_transaction_hash="0" * 64,
                logical_clock=i + 1,
                causal_task_id="task_win",
                step_index=i,
                phase="PHASE_2A_SYNTHESIS",
                source_service="services/research",
                source_endpoint="192.168.40.10:8440",
                target_service="services/telemetry",
                target_endpoint="192.168.40.40:8446",
                channel_id="channel_research_telemetry",
                verb="QUERY_WIN",
                payload_summary="Window test",
                payload_data={"i": i},
                timestamp_ns=t_base + i * 10_000_000,
            )
            for i in range(100)
        ]
        self.vault.insert_batch(txs)

        # Query temporal window spanning the middle 50 transactions
        start_ns = t_base + 25 * 10_000_000
        end_ns = t_base + 75 * 10_000_000

        t0 = time.perf_counter()
        window = self.vault.query_temporal_window(start_ns, end_ns, max_delta_records=500)
        elapsed_ms = (time.perf_counter() - t0) * 1000.0

        self.assertLess(elapsed_ms, 15.0)
        self.assertLess(window.delta_fold_duration_ms, 15.0)
        self.assertGreater(window.transaction_count, 0)
        self.assertLessEqual(window.transaction_count, 55)

        recs = json.loads(window.transactions_json)
        self.assertEqual(len(recs), window.transaction_count)

    def test_04_zero_loopback_invariant_enforcement(self) -> None:
        """Verifies assert_non_loopback strictly rejects 127.0.0.1, localhost, ::1, and 0.0.0.0."""
        # Valid non-loopback IPs
        assert_non_loopback("192.168.40.10:8440")
        assert_non_loopback("192.168.40.20:8442")
        assert_non_loopback("192.168.40.40:8446")

        # Prohibited loopbacks
        for bad_ip in ["127.0.0.1:8000", "127.0.1.1", "localhost:8446", "::1", "0.0.0.0:8080"]:
            with self.assertRaises(ValueError):
                assert_non_loopback(bad_ip)

        # Prohibited in MeshTransaction
        with self.assertRaises(ValueError):
            MeshTransaction.create(
                transaction_id="tx_loopback_fail",
                prev_transaction_hash="0" * 64,
                logical_clock=1,
                causal_task_id="task_fail",
                step_index=0,
                phase="PHASE_2A_SYNTHESIS",
                source_service="services/builder",
                source_endpoint="127.0.0.1:8442",  # VIOLATION
                target_service="services/telemetry",
                target_endpoint="192.168.40.40:8446",
                channel_id="chan",
                verb="OP",
                payload_summary="bad",
                payload_data={},
            )

    def test_05_categorical_1_tap_functorial_rollback(self) -> None:
        """Verifies 1-tap Functorial Undo applies adjoint inverse delta^-1(T) to restore cluster state."""
        rollback_engine = RollbackEngine(self.vault)
        t_base = time.time_ns()

        txs = [
            MeshTransaction.create(
                transaction_id=f"tx_roll_{i}",
                prev_transaction_hash="0" * 64,
                logical_clock=i + 1,
                causal_task_id="task_rollback_test",
                step_index=i,
                phase="PHASE_2A_SYNTHESIS",
                source_service="services/builder",
                source_endpoint="192.168.40.20:8442",
                target_service="services/telemetry",
                target_endpoint="192.168.40.40:8446",
                channel_id="channel_builder_telemetry",
                verb="AST_SKELETONIZE",
                payload_summary=f"Tx #{i}",
                payload_data={"index": i},
                bits_erased=50,
                timestamp_ns=t_base + i * 5_000_000,
            )
            for i in range(10)
        ]
        self.vault.insert_batch(txs)

        # Roll back to tx_roll_5 (reverting tx_roll_6 through tx_roll_9)
        preview = rollback_engine.preview_rollback("tx_roll_5")
        self.assertEqual(preview["transactions_to_revert_count"], 4)
        self.assertEqual(preview["total_bits_to_recover"], 4 * 50)
        self.assertIn("adjoint", preview["adjoint_inverse_urn"])

        success, cmd = rollback_engine.execute_functorial_rollback(
            command_id="cmd_undo_test_01",
            target_tx_id="tx_roll_5",
            operator_notes="Unit test undo",
        )
        self.assertTrue(success)
        self.assertEqual(cmd.status, "COMMITTED")

        # Verify reverted transactions have status CIRCUIT_BROKEN
        reverted_tx = self.vault.get_transaction_by_id("tx_roll_8")
        self.assertIsNotNone(reverted_tx)
        self.assertEqual(reverted_tx.status, "CIRCUIT_BROKEN")

        # Verify target transaction was NOT reverted
        target_tx = self.vault.get_transaction_by_id("tx_roll_5")
        self.assertIsNotNone(target_tx)
        self.assertEqual(target_tx.status, "SUCCESS")

    def test_06_ingest_server_ring_buffer_and_drain(self) -> None:
        """Verifies IngestServer non-blocking ring buffer and background drain to WAL."""
        async def run_async_test() -> None:
            ingest = IngestServer(
                vault=self.vault,
                host="192.168.40.40",
                port=18446,  # Test port
                ring_buffer_size=1000,
                flush_interval_seconds=0.02,
                allow_any_interface_for_testing=True,
            )
            await ingest.start()

            tx = MeshTransaction.create(
                transaction_id="tx_async_ingest_01",
                prev_transaction_hash="0" * 64,
                logical_clock=1,
                causal_task_id="task_ingest",
                step_index=0,
                phase="PHASE_2A_SYNTHESIS",
                source_service="services/builder",
                source_endpoint="192.168.40.20:8442",
                target_service="services/telemetry",
                target_endpoint="192.168.40.40:8446",
                channel_id="channel_builder_telemetry",
                verb="INGEST_TEST",
                payload_summary="Testing async ring buffer",
                payload_data={"val": 42},
            )

            enqueued = ingest.enqueue(tx)
            self.assertTrue(enqueued)
            self.assertEqual(ingest.total_enqueued, 1)

            # Wait for 50ms drain loop to flush
            await asyncio.sleep(0.08)
            self.assertGreaterEqual(ingest.total_flushed, 1)

            # Verify in vault
            stored = self.vault.get_transaction_by_id("tx_async_ingest_01")
            self.assertIsNotNone(stored)
            self.assertEqual(stored.verb, "INGEST_TEST")

            await ingest.stop()

        asyncio.run(run_async_test())


if __name__ == "__main__":
    unittest.main()
