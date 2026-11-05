"""Comprehensive Byzantine Chaos & Property Fuzzing Test Suite (`test_byzantine_fuzz_mesh.py`).

Enforces:
- [NEG-G1B-001] Mandatory Substrate Test Execution (exit code 0, non-zero passing assertions).
- [L1-G4B-001] Sovereign Mesh Protocol Standardization & Nanosecond Monotonic Ordering.
- [L1-G3B-011] Universal Compositional Contract IR Invariants.
- [L1-G3B-012] Dedicated Non-Loopback Network Topology Bound to 192.168.40.0/24.
- [L1-G3B-017] SHA-256 Chained Cryptographic Witnessing & Merkle Integrity.
- [L1-G3B-018] Thermodynamic Capital & Landauer Heat Dissipation.
- [L1-002] Categorical 1-Tap Functorial Rollback Adjoint Inversion.

Byzantine Vectors Covered:
1. Timestamp Inversion & Logical Clock Regression (Lamport Monotonicity Breach).
2. Loopback Spoofing (127.0.0.1, localhost, ::1, 0.0.0.0, out-of-subnet IPs).
3. Corrupted Merkle Leaf Digests & Hash Poisoning.
4. Payload Floods & Ring Buffer Backpressure Containment.
5. Circuit-Breaker Triggers & Quarantine State Persistence.
6. Property-Based Randomized Fuzzing (100 Mutated Payload Invariants).
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import os
from pathlib import Path
import random
import sqlite3
import tempfile
import time
from typing import Any, Dict, List
import unittest

from generations.gen_04b.services.audit.src.smt_mesh_verifier import (
    SMTMeshProofWitness,
    SMTMeshVerifier,
)
from generations.gen_04b.services.telemetry.src.ingest_server import IngestServer
from generations.gen_04b.services.telemetry.src.rollback_engine import (
    FunctorialUndoCommand,
    RollbackEngine,
)
from generations.gen_04b.services.telemetry.src.telemetry_vault import (
    BOLTZMANN_K,
    LN_2,
    CockpitTimelineWindow,
    MeshTransaction,
    SystemStateKeyframe,
    TelemetryVault,
    assert_non_loopback,
)


class TestByzantineFuzzMesh(unittest.TestCase):
    """Rigorous Byzantine chaos and adversarial property fuzzing test suite."""

    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "byzantine_vault.db"
        self.vault = TelemetryVault(db_path=str(self.db_path), keyframe_interval=100)
        self.smt_verifier = SMTMeshVerifier(use_z3_if_available=True)
        self.rollback_engine = RollbackEngine(self.vault)

    def tearDown(self) -> None:
        self.vault.close()
        self.temp_dir.cleanup()

    def test_01_byzantine_timestamp_inversion_and_regression(self) -> None:
        """Injects timestamp inversion and clock regression Byzantine vectors."""
        t_base = time.time_ns()

        # Vector 1.1: Non-positive timestamp rejection
        with self.assertRaises(ValueError) as ctx:
            MeshTransaction.create(
                transaction_id="tx_byz_neg_time",
                prev_transaction_hash="0" * 64,
                logical_clock=1,
                causal_task_id="task_byz_01",
                step_index=0,
                phase="PHASE_2C_QA",
                source_service="services/audit",
                source_endpoint="192.168.40.30:8444",
                target_service="services/telemetry",
                target_endpoint="192.168.40.40:8446",
                channel_id="channel_audit_telemetry",
                verb="OP_EXEC",
                payload_summary="Byzantine negative timestamp",
                payload_data={"fuzz": True},
                timestamp_ns=-1000,
            )
        self.assertIn("Invalid timestamp_ns", str(ctx.exception))

        # Vector 1.2: Negative duration rejection
        with self.assertRaises(ValueError) as ctx:
            MeshTransaction.create(
                transaction_id="tx_byz_neg_dur",
                prev_transaction_hash="0" * 64,
                logical_clock=1,
                causal_task_id="task_byz_01",
                step_index=0,
                phase="PHASE_2C_QA",
                source_service="services/audit",
                source_endpoint="192.168.40.30:8444",
                target_service="services/telemetry",
                target_endpoint="192.168.40.40:8446",
                channel_id="channel_audit_telemetry",
                verb="OP_EXEC",
                payload_summary="Byzantine negative duration",
                payload_data={"fuzz": True},
                duration_ns=-50,
            )
        self.assertIn("Invalid duration_ns", str(ctx.exception))

        # Vector 1.3: SMT Monotonicity Prover refutes timestamp inversion (T2 < T1)
        inverted_chain = [
            {"transaction_id": "tx_ord_01", "logical_clock": 1, "timestamp_ns": 2000000},
            {"transaction_id": "tx_ord_02", "logical_clock": 2, "timestamp_ns": 1000000},  # Regressed
        ]
        witness_time = self.smt_verifier.verify_lamport_monotonicity(inverted_chain)
        self.assertFalse(witness_time.is_valid)
        self.assertIsNotNone(witness_time.counter_example)
        self.assertEqual(witness_time.counter_example.get("violation"), "TIMESTAMP_REGRESSION")
        self.assertEqual(witness_time.counter_example.get("transaction_id"), "tx_ord_02")

        # Vector 1.4: SMT Monotonicity Prover refutes logical clock regression (L2 < L1)
        regressed_clock_chain = [
            {"transaction_id": "tx_clk_01", "logical_clock": 10, "timestamp_ns": 1000},
            {"transaction_id": "tx_clk_02", "logical_clock": 5, "timestamp_ns": 2000},  # Regressed clock
        ]
        witness_clk = self.smt_verifier.verify_lamport_monotonicity(regressed_clock_chain)
        self.assertFalse(witness_clk.is_valid)
        self.assertIsNotNone(witness_clk.counter_example)
        self.assertEqual(witness_clk.counter_example.get("violation"), "LOGICAL_CLOCK_REGRESSION")

        # Vector 1.5: Timeline window query auto-normalizes inverted bounds without error
        tx_valid = MeshTransaction.create(
            transaction_id="tx_norm_01",
            prev_transaction_hash="0" * 64,
            logical_clock=1,
            causal_task_id="task_norm",
            step_index=0,
            phase="PHASE_2C_QA",
            source_service="services/audit",
            source_endpoint="192.168.40.30:8444",
            target_service="services/telemetry",
            target_endpoint="192.168.40.40:8446",
            channel_id="channel_audit_telemetry",
            verb="OP_EXEC",
            payload_summary="Normal transaction",
            payload_data={"val": 42},
            timestamp_ns=t_base,
        )
        self.vault.insert_transaction(tx_valid)

        # Query with start_ns > end_ns
        window = self.vault.query_temporal_window(start_ns=t_base + 1000, end_ns=t_base - 1000)
        self.assertLessEqual(window.start_ns, window.end_ns)
        self.assertLess(window.delta_fold_duration_ms, 15.0)

    def test_02_byzantine_loopback_spoofing_vectors(self) -> None:
        """Injects Byzantine loopback and out-of-subnet IP spoofing attack vectors."""
        # Vector 2.1: assert_non_loopback fuzzing across multiple formats
        loopback_payloads = [
            "127.0.0.1",
            "127.0.0.1:8446",
            "localhost",
            "localhost:8080",
            "::1",
            "[::1]:8446",
            "0.0.0.0",
            "0.0.0.0:8000",
            "127.128.0.1:9000",
        ]
        for bad_endpoint in loopback_payloads:
            with self.assertRaises(ValueError, msg=f"Failed to reject loopback: {bad_endpoint}") as ctx:
                assert_non_loopback(bad_endpoint, "test_fuzz")
            self.assertIn("[L1-G3B-012 Violation]", str(ctx.exception))

        # Vector 2.2: MeshTransaction rejects loopback endpoints on creation
        with self.assertRaises(ValueError) as ctx:
            MeshTransaction.create(
                transaction_id="tx_byz_loopback_src",
                prev_transaction_hash="0" * 64,
                logical_clock=1,
                causal_task_id="task_byz_02",
                step_index=0,
                phase="PHASE_2C_QA",
                source_service="services/attacker",
                source_endpoint="127.0.0.1:8440",  # SPOOFED
                target_service="services/telemetry",
                target_endpoint="192.168.40.40:8446",
                channel_id="channel_spoof",
                verb="OP_ATTACK",
                payload_summary="Spoofed loopback source",
                payload_data={},
            )
        self.assertIn("[L1-G3B-012 Violation]", str(ctx.exception))

        # Vector 2.3: IngestServer strict initialization non-loopback invariant
        with self.assertRaises(ValueError) as ctx:
            IngestServer(vault=self.vault, host="127.0.0.1", port=8446, allow_any_interface_for_testing=False)
        self.assertIn("[L1-G3B-012 Violation]", str(ctx.exception))

        # Vector 2.4: SMT mesh verifier refutes topologies with loopback or out-of-subnet nodes
        spoofed_topology = {
            "topology_id": "topology_spoofed",
            "consensus": {"protocol": "sheaf_quorum", "quorum_fraction": 0.67},
            "nodes": {
                "node_legit": {"host_interface": "192.168.40.10", "port": 8440},
                "node_byz_loopback": {"host_interface": "127.0.0.1", "port": 8442},
            },
            "channels": [
                {"channel_id": "chan_01", "source_node_id": "node_legit", "target_node_id": "node_byz_loopback", "port": 8442}
            ],
        }
        witness_topo = self.smt_verifier.verify_topology(spoofed_topology)
        self.assertFalse(witness_topo.is_valid)
        self.assertEqual(witness_topo.counter_example.get("violation"), "LOOPBACK_DETECTED")
        self.assertEqual(witness_topo.counter_example.get("node_id"), "node_byz_loopback")

        # Vector 2.5: SMT mesh verifier refutes out-of-subnet node (e.g. 10.0.0.1)
        spoofed_topology["nodes"]["node_byz_loopback"]["host_interface"] = "10.0.0.1"
        witness_subnet = self.smt_verifier.verify_topology(spoofed_topology)
        self.assertFalse(witness_subnet.is_valid)
        self.assertEqual(witness_subnet.counter_example.get("violation"), "SUBNET_OUT_OF_BOUNDS")

    def test_03_corrupted_merkle_leaf_and_hash_poisoning(self) -> None:
        """Injects corrupted Merkle leaf digests, tampered hashes, and Merkle root poisoning."""
        # Vector 3.1: Invalid transaction_hash length (< 64 or > 64 chars)
        with self.assertRaises(ValueError) as ctx:
            tx = MeshTransaction.create(
                transaction_id="tx_poison_01",
                prev_transaction_hash="0" * 64,
                logical_clock=1,
                causal_task_id="task_poison",
                step_index=0,
                phase="PHASE_2C_QA",
                source_service="services/builder",
                source_endpoint="192.168.40.20:8442",
                target_service="services/telemetry",
                target_endpoint="192.168.40.40:8446",
                channel_id="channel_builder_telemetry",
                verb="OP_EXEC",
                payload_summary="Hash length breach",
                payload_data={"valid": True},
            )
            # Mutate hash to corrupted 63-char length
            tx.transaction_hash = "f" * 63
            tx.validate_invariants()
        self.assertIn("Invalid transaction_hash length", str(ctx.exception))

        # Vector 3.2: Invalid merkle_leaf_hash length
        with self.assertRaises(ValueError) as ctx:
            tx = MeshTransaction.create(
                transaction_id="tx_poison_02",
                prev_transaction_hash="0" * 64,
                logical_clock=1,
                causal_task_id="task_poison",
                step_index=0,
                phase="PHASE_2C_QA",
                source_service="services/builder",
                source_endpoint="192.168.40.20:8442",
                target_service="services/telemetry",
                target_endpoint="192.168.40.40:8446",
                channel_id="channel_builder_telemetry",
                verb="OP_EXEC",
                payload_summary="Merkle leaf hash length breach",
                payload_data={"valid": True},
            )
            tx.merkle_leaf_hash = "a" * 65
            tx.validate_invariants()
        self.assertIn("Invalid merkle_leaf_hash length", str(ctx.exception))

        # Vector 3.3: SystemStateKeyframe Merkle root poisoning detection
        with self.assertRaises(ValueError) as ctx:
            kf = SystemStateKeyframe(
                keyframe_id="kf_corrupt_01",
                keyframe_tx_id="tx_01",
                timestamp_ns=time.time_ns(),
                logical_clock=1,
                active_nodes_json="{}",
                channel_states_json="{}",
                merkle_root="poisoned_short_root",
                total_tokens_burned=100,
                total_bits_erased=50,
                total_heat_dissipated_joules=1.2e-20,
            )
            kf.validate_invariants()
        self.assertIn("Invalid merkle_root length", str(ctx.exception))

        # Vector 3.4: Deterministic Merkle Root Divergence on Single-Bit Corruption
        tx1 = MeshTransaction.create(
            transaction_id="tx_merkle_orig",
            prev_transaction_hash="0" * 64,
            logical_clock=1,
            causal_task_id="task_avalanche",
            step_index=0,
            phase="PHASE_2C_QA",
            source_service="services/builder",
            source_endpoint="192.168.40.20:8442",
            target_service="services/telemetry",
            target_endpoint="192.168.40.40:8446",
            channel_id="channel_builder_telemetry",
            verb="OP_EXEC",
            payload_summary="Original payload",
            payload_data={"secret_seed": 100},
        )
        tx2_perturbed = MeshTransaction.create(
            transaction_id="tx_merkle_pert",
            prev_transaction_hash="0" * 64,
            logical_clock=1,
            causal_task_id="task_avalanche",
            step_index=0,
            phase="PHASE_2C_QA",
            source_service="services/builder",
            source_endpoint="192.168.40.20:8442",
            target_service="services/telemetry",
            target_endpoint="192.168.40.40:8446",
            channel_id="channel_builder_telemetry",
            verb="OP_EXEC",
            payload_summary="Perturbed payload",
            payload_data={"secret_seed": 101},  # 1 bit flipped
        )
        self.assertNotEqual(tx1.transaction_hash, tx2_perturbed.transaction_hash)
        self.assertNotEqual(tx1.merkle_leaf_hash, tx2_perturbed.merkle_leaf_hash)

        # Vector 3.5: FunctorialUndoCommand SMT proof witness length validation
        with self.assertRaises(ValueError) as ctx:
            cmd = FunctorialUndoCommand(
                command_id="undo_poison_01",
                target_tx_id="tx_01",
                target_timestamp_ns=time.time_ns(),
                adjoint_inverse_urn="urn:axioma:cluster:adjoint:state_revert",
                affected_service_urns="[]",
                smt_proof_witness="corrupted_hex",  # not 64 chars
                status="PENDING_SMT",
            )
            cmd.validate_invariants()
        self.assertIn("smt_proof_witness must be 64-char hex hash", str(ctx.exception))

    def test_04_payload_floods_and_backpressure_containment(self) -> None:
        """Injects high-velocity payload floods and validates ring buffer backpressure."""
        # Initialize IngestServer with a tiny ring buffer (50 records)
        server = IngestServer(
            vault=self.vault,
            host="192.168.40.40",
            port=8446,
            ring_buffer_size=50,
            flush_interval_seconds=0.01,
            max_batch_size=100,
            allow_any_interface_for_testing=True,
        )

        # Vector 4.1: High-velocity burst flood of 200 micro-transactions
        tx_flood: List[MeshTransaction] = []
        for i in range(200):
            tx = MeshTransaction.create(
                transaction_id=f"tx_flood_{i:04d}",
                prev_transaction_hash="0" * 64,
                logical_clock=i + 1,
                causal_task_id="task_flood",
                step_index=i,
                phase="PHASE_2C_QA",
                source_service="services/builder",
                source_endpoint="192.168.40.20:8442",
                target_service="services/telemetry",
                target_endpoint="192.168.40.40:8446",
                channel_id="channel_builder_telemetry",
                verb="OP_FLOOD",
                payload_summary=f"Flood packet #{i}",
                payload_data={"seq": i, "padding": "x" * 64},
            )
            tx_flood.append(tx)

        # Enqueue all 200 packets synchronously without draining
        success_count = 0
        for tx in tx_flood:
            if server.enqueue(tx):
                success_count += 1

        self.assertEqual(success_count, 200)
        self.assertEqual(server.total_enqueued, 200)
        # Ring buffer holds 50, remaining 150 must safely spill over into spillover buffer
        self.assertEqual(server.queue.qsize(), 50)
        self.assertEqual(len(server.spillover_buffer), 150)
        self.assertEqual(server.total_spillover_count, 150)
        self.assertEqual(server.dropped_packets, 0)

        # Vector 4.2: Health status metrics reflect buffer states accurately
        health = server.get_health_status()
        self.assertEqual(health["ring_buffer_depth"], 50)
        self.assertEqual(health["spillover_depth"], 150)
        self.assertEqual(health["dropped_packets"], 0)

        # Vector 4.3: Extreme saturation beyond maximum spillover capacity (50,000)
        # We simulate this safely by lowering spillover limit temporarily or setting full
        server.spillover_buffer = [tx_flood[0]] * 50_000
        # Next packet enqueue must drop packet and increment dropped_packets without crashing
        dropped_tx = tx_flood[0]
        accepted = server.enqueue(dropped_tx)
        self.assertFalse(accepted)
        self.assertGreater(server.dropped_packets, 0)

        # Clear spillover for clean test exit
        server.spillover_buffer.clear()

    def test_05_circuit_breaker_triggers_and_quarantine_enclaves(self) -> None:
        """Injects circuit-breaker triggers, quarantine states, and functorial rollback recovery."""
        t_base = time.time_ns()

        # Vector 5.1: Create transactions in CIRCUIT_BROKEN and QUARANTINE states
        tx_quarantine = MeshTransaction.create(
            transaction_id="tx_byz_quarantine_01",
            prev_transaction_hash="0" * 64,
            logical_clock=1,
            causal_task_id="task_circuit",
            step_index=0,
            phase="PHASE_2C_QA",
            source_service="services/audit",
            source_endpoint="192.168.40.30:8444",
            target_service="services/telemetry",
            target_endpoint="192.168.40.40:8446",
            channel_id="channel_audit_telemetry",
            verb="OP_QUARANTINE",
            payload_summary="Byzantine vector quarantined",
            payload_data={"violation": "SYNTAX_BREACH"},
            status="QUARANTINE",
            timestamp_ns=t_base,
        )
        tx_circuit_broken = MeshTransaction.create(
            transaction_id="tx_byz_circuit_02",
            prev_transaction_hash=tx_quarantine.transaction_hash,
            logical_clock=2,
            causal_task_id="task_circuit",
            step_index=1,
            phase="PHASE_2C_QA",
            source_service="services/builder",
            source_endpoint="192.168.40.20:8442",
            target_service="services/telemetry",
            target_endpoint="192.168.40.40:8446",
            channel_id="channel_builder_telemetry",
            verb="OP_TRIP",
            payload_summary="Circuit breaker tripped after repeated errors",
            payload_data={"threshold": 5, "current_errors": 6},
            status="CIRCUIT_BROKEN",
            timestamp_ns=t_base + 500_000,
        )

        # Insert into vault
        self.vault.insert_transaction(tx_quarantine)
        self.vault.insert_transaction(tx_circuit_broken)

        # Vector 5.2: Verify querying temporal window preserves circuit breaker metadata
        window = self.vault.query_temporal_window(start_ns=t_base - 100, end_ns=t_base + 1_000_000)
        self.assertGreaterEqual(window.transaction_count, 2)
        transactions = json.loads(window.transactions_json)
        statuses = [t["status"] for t in transactions]
        self.assertIn("QUARANTINE", statuses)
        self.assertIn("CIRCUIT_BROKEN", statuses)

        # Vector 5.3: RollbackEngine preview for circuit-broken transaction
        preview = self.rollback_engine.preview_rollback(
            target_tx_id="tx_byz_quarantine_01",
            target_timestamp_ns=t_base,
        )
        self.assertTrue(preview["can_rollback"])
        self.assertIn("smt_proof_witness", preview)
        self.assertEqual(len(preview["smt_proof_witness"]), 64)
        self.assertGreaterEqual(preview["transactions_to_revert_count"], 1)

        # Vector 5.4: Execute 1-tap Functorial Rollback and verify commit
        success, cmd = self.rollback_engine.execute_functorial_rollback(
            command_id="cmd_rollback_01",
            target_tx_id="tx_byz_quarantine_01",
            target_timestamp_ns=t_base,
        )
        self.assertTrue(success)
        self.assertEqual(cmd.status, "COMMITTED")
        self.assertEqual(len(cmd.smt_proof_witness), 64)

    def test_06_property_based_randomized_fuzzing(self) -> None:
        """Executes 100 randomized property fuzzing iterations over micro-transaction contracts."""
        random.seed(42)  # Deterministic seed for reproducible property fuzzing
        invalid_capital_partitions = ["UNPROTECTED", "SPECULATIVE", "", "100%", "exploratory", 12345]
        invalid_statuses = ["EXPLODED", "UNKNOWN", "", "FAIL", None, 999]
        invalid_hosts = ["127.0.0.1", "localhost", "::1", "0.0.0.0", "127.0.10.1:8080", ""]
        invalid_hashes = ["0" * 63, "f" * 65, "", "not_a_hash", 123456]

        fuzz_passes = 0
        total_fuzz_iterations = 100

        for i in range(total_fuzz_iterations):
            mutation_type = i % 5

            if mutation_type == 0:
                # Corrupt capital partition
                bad_capital = random.choice(invalid_capital_partitions)
                with self.assertRaises((ValueError, TypeError)):
                    tx = MeshTransaction.create(
                        transaction_id=f"tx_fuzz_{i:04d}",
                        prev_transaction_hash="0" * 64,
                        logical_clock=i + 1,
                        causal_task_id=f"task_fuzz_{i}",
                        step_index=i,
                        phase="PHASE_2C_QA",
                        source_service="services/builder",
                        source_endpoint="192.168.40.20:8442",
                        target_service="services/telemetry",
                        target_endpoint="192.168.40.40:8446",
                        channel_id="channel_builder_telemetry",
                        verb="OP_EXEC",
                        payload_summary="Fuzz invalid capital partition",
                        payload_data={"val": i},
                        capital_partition=bad_capital,  # type: ignore
                    )
                fuzz_passes += 1

            elif mutation_type == 1:
                # Corrupt status
                bad_status = random.choice(invalid_statuses)
                with self.assertRaises((ValueError, TypeError)):
                    tx = MeshTransaction.create(
                        transaction_id=f"tx_fuzz_{i:04d}",
                        prev_transaction_hash="0" * 64,
                        logical_clock=i + 1,
                        causal_task_id=f"task_fuzz_{i}",
                        step_index=i,
                        phase="PHASE_2C_QA",
                        source_service="services/builder",
                        source_endpoint="192.168.40.20:8442",
                        target_service="services/telemetry",
                        target_endpoint="192.168.40.40:8446",
                        channel_id="channel_builder_telemetry",
                        verb="OP_EXEC",
                        payload_summary="Fuzz invalid status",
                        payload_data={"val": i},
                        status=bad_status,  # type: ignore
                    )
                fuzz_passes += 1

            elif mutation_type == 2:
                # Corrupt source or target endpoint with loopback
                bad_host = random.choice(invalid_hosts)
                with self.assertRaises((ValueError, TypeError)):
                    tx = MeshTransaction.create(
                        transaction_id=f"tx_fuzz_{i:04d}",
                        prev_transaction_hash="0" * 64,
                        logical_clock=i + 1,
                        causal_task_id=f"task_fuzz_{i}",
                        step_index=i,
                        phase="PHASE_2C_QA",
                        source_service="services/builder",
                        source_endpoint=bad_host,  # type: ignore
                        target_service="services/telemetry",
                        target_endpoint="192.168.40.40:8446",
                        channel_id="channel_builder_telemetry",
                        verb="OP_EXEC",
                        payload_summary="Fuzz loopback endpoint",
                        payload_data={"val": i},
                    )
                fuzz_passes += 1

            elif mutation_type == 3:
                # Corrupt hash lengths
                bad_hash = random.choice(invalid_hashes)
                with self.assertRaises((ValueError, TypeError)):
                    tx = MeshTransaction.create(
                        transaction_id=f"tx_fuzz_{i:04d}",
                        prev_transaction_hash="0" * 64,
                        logical_clock=i + 1,
                        causal_task_id=f"task_fuzz_{i}",
                        step_index=i,
                        phase="PHASE_2C_QA",
                        source_service="services/builder",
                        source_endpoint="192.168.40.20:8442",
                        target_service="services/telemetry",
                        target_endpoint="192.168.40.40:8446",
                        channel_id="channel_builder_telemetry",
                        verb="OP_EXEC",
                        payload_summary="Fuzz corrupted hash",
                        payload_data={"val": i},
                    )
                    tx.transaction_hash = bad_hash  # type: ignore
                    tx.validate_invariants()
                fuzz_passes += 1

            elif mutation_type == 4:
                # Negative or zero timestamps and negative logical clocks
                bad_clock = -random.randint(1, 1000)
                with self.assertRaises((ValueError, TypeError)):
                    tx = MeshTransaction.create(
                        transaction_id=f"tx_fuzz_{i:04d}",
                        prev_transaction_hash="0" * 64,
                        logical_clock=bad_clock,
                        causal_task_id=f"task_fuzz_{i}",
                        step_index=i,
                        phase="PHASE_2C_QA",
                        source_service="services/builder",
                        source_endpoint="192.168.40.20:8442",
                        target_service="services/telemetry",
                        target_endpoint="192.168.40.40:8446",
                        channel_id="channel_builder_telemetry",
                        verb="OP_EXEC",
                        payload_summary="Fuzz negative clock",
                        payload_data={"val": i},
                    )
                fuzz_passes += 1

        self.assertEqual(fuzz_passes, total_fuzz_iterations)
        self.assertEqual(fuzz_passes, 100)


if __name__ == "__main__":
    unittest.main()
