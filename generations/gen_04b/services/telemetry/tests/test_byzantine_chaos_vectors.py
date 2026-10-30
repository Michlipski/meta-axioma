"""Adversarial and Byzantine chaos fuzzing test suite (`soc_g4b_telemetry`).

Verifies:
- Containment of all 6 Byzantine vector types:
  1. SPAN_CORRUPTION -> syntax_breach_recovery
  2. TIMESTAMP_INVERSION -> byzantine_fuzz_quarantine
  3. THERMAL_FLOOD -> byzantine_fuzz_quarantine
  4. MERKLE_POISONING -> byzantine_fuzz_quarantine
  5. LOOPBACK_INJECTION -> network_loopback_emergency
  6. TOKEN_INFLATION -> byzantine_fuzz_quarantine
- 100% trapped fault containment ratio without catastrophic process panic.
- Cryptographic Merkle DAG audit trail of all trapped Byzantine vectors.
- Sentry observer alerting and automatic resolution.
- Enclave unwinding and return to ingress_standby state.
- Invariant enforcement on Byzantine vector construction.
"""

from __future__ import annotations

from pathlib import Path
import sys
import unittest

TEL_ROOT = Path(__file__).resolve().parent.parent
REPO_ROOT = TEL_ROOT.parent.parent.parent.parent
for p in [str(TEL_ROOT), str(REPO_ROOT)]:
    if p not in sys.path:
        sys.path.insert(0, p)

from generations.gen_04b.services.telemetry.src.domain_models import (
    ByzantineTelemetryVector,
    ByzantineVectorType,
    RecoveryEnclaveType,
    TelemetryDomainInvariantViolation,
)
from generations.gen_04b.services.telemetry.src.telemetry_kernel import (
    SovereignTelemetryKernel,
)


class TestByzantineChaosVectors(unittest.TestCase):
    """Test suite for Byzantine chaos vector trapping and recovery enclave containment."""

    def setUp(self):
        self.kernel = SovereignTelemetryKernel(node_ip="192.168.40.40", port=8446)
        self.kernel.initialize_kernel()

    def test_trap_span_corruption_vector(self):
        vec = ByzantineTelemetryVector(
            vector_id="byz_span_01",
            vector_type=ByzantineVectorType.SPAN_CORRUPTION,
            payload={"corrupted_field": "status_code", "raw": 99999},
            target_channel="stream_ingest",
        )
        res = self.kernel.trap_byzantine_chaos_vector(vec)

        self.assertEqual(res["status"], "CONTAINED_AND_RESOLVED")
        self.assertEqual(res["enclave"], RecoveryEnclaveType.SYNTAX_BREACH.value)
        self.assertTrue(vec.is_trapped)
        self.assertIsNotNone(vec.trapped_at_ms)
        self.assertEqual(self.kernel.statechart.current_state, "ingress_standby")

    def test_trap_timestamp_inversion_vector(self):
        vec = ByzantineTelemetryVector(
            vector_id="byz_time_02",
            vector_type=ByzantineVectorType.TIMESTAMP_INVERSION,
            payload={"start_ns": 1000000, "end_ns": 500000},
            target_channel="stream_ingest",
        )
        res = self.kernel.trap_byzantine_chaos_vector(vec)

        self.assertEqual(res["status"], "CONTAINED_AND_RESOLVED")
        self.assertEqual(res["enclave"], RecoveryEnclaveType.BYZANTINE_FUZZ.value)
        self.assertTrue(vec.is_trapped)

    def test_trap_thermal_flood_vector(self):
        vec = ByzantineTelemetryVector(
            vector_id="byz_therm_03",
            vector_type=ByzantineVectorType.THERMAL_FLOOD,
            payload={"flood_bits": 999999999999, "simulated_temp_k": 5000.0},
            target_channel="thermo_calc",
        )
        res = self.kernel.trap_byzantine_chaos_vector(vec)

        self.assertEqual(res["status"], "CONTAINED_AND_RESOLVED")
        self.assertEqual(res["enclave"], RecoveryEnclaveType.BYZANTINE_FUZZ.value)
        self.assertTrue(vec.is_trapped)

    def test_trap_merkle_poisoning_vector(self):
        vec = ByzantineTelemetryVector(
            vector_id="byz_merkle_04",
            vector_type=ByzantineVectorType.MERKLE_POISONING,
            payload={"fake_root": "0" * 64, "mutated_leaf_idx": 3},
            target_channel="merkle_anchor",
        )
        res = self.kernel.trap_byzantine_chaos_vector(vec)

        self.assertEqual(res["status"], "CONTAINED_AND_RESOLVED")
        self.assertEqual(res["enclave"], RecoveryEnclaveType.BYZANTINE_FUZZ.value)
        self.assertTrue(vec.is_trapped)

    def test_trap_loopback_injection_vector(self):
        vec = ByzantineTelemetryVector(
            vector_id="byz_loopback_05",
            vector_type=ByzantineVectorType.LOOPBACK_INJECTION,
            payload={"injected_ip": "127.0.0.1:8080", "target": "router"},
            target_channel="network_mesh",
        )
        res = self.kernel.trap_byzantine_chaos_vector(vec)

        self.assertEqual(res["status"], "CONTAINED_AND_RESOLVED")
        self.assertEqual(res["enclave"], RecoveryEnclaveType.NETWORK_LOOPBACK.value)
        self.assertTrue(vec.is_trapped)

    def test_trap_token_inflation_vector(self):
        vec = ByzantineTelemetryVector(
            vector_id="byz_token_06",
            vector_type=ByzantineVectorType.TOKEN_INFLATION,
            payload={"inflated_spend": 2000000, "bypass_limit": True},
            target_channel="capital_ledger",
        )
        res = self.kernel.trap_byzantine_chaos_vector(vec)

        self.assertEqual(res["status"], "CONTAINED_AND_RESOLVED")
        self.assertEqual(res["enclave"], RecoveryEnclaveType.BYZANTINE_FUZZ.value)
        self.assertTrue(vec.is_trapped)

    def test_100_percent_trapped_containment_ratio(self):
        all_vector_types = list(ByzantineVectorType)
        vectors = [
            ByzantineTelemetryVector(
                vector_id=f"chaos_batch_{vt.name.lower()}",
                vector_type=vt,
                payload={"simulated_chaos": True},
                target_channel="fuzz_crucible",
            )
            for vt in all_vector_types
        ]

        trapped_count = 0
        for v in vectors:
            res = self.kernel.trap_byzantine_chaos_vector(v)
            if res["status"] == "CONTAINED_AND_RESOLVED":
                trapped_count += 1

        self.assertEqual(trapped_count, len(all_vector_types))
        containment_ratio = float(trapped_count) / float(len(all_vector_types))
        self.assertEqual(containment_ratio, 1.0)
        self.assertEqual(len(self.kernel.trapped_byzantine_vectors), len(all_vector_types))

    def test_merkle_audit_trail_of_trapped_vectors(self):
        vec = ByzantineTelemetryVector(
            vector_id="byz_audited_07",
            vector_type=ByzantineVectorType.SPAN_CORRUPTION,
            payload={"corrupted": True},
        )
        self.kernel.trap_byzantine_chaos_vector(vec)

        # Ensure event was recorded into Merkle DAG
        self.assertGreater(self.kernel.merkle_engine.leaves_count, 0)
        self.assertTrue(self.kernel.merkle_engine.verify_chain_integrity())

    def test_invalid_byzantine_vector_invariants(self):
        with self.assertRaises(TelemetryDomainInvariantViolation):
            ByzantineTelemetryVector(vector_id="", vector_type=ByzantineVectorType.SPAN_CORRUPTION).validate_invariants()

        with self.assertRaises(TelemetryDomainInvariantViolation):
            ByzantineTelemetryVector(vector_id="v", vector_type=ByzantineVectorType.SPAN_CORRUPTION, target_channel="").validate_invariants()


if __name__ == "__main__":
    unittest.main()
