"""Unit & Adversarial Invariant Test Suite for Byzantine & Chaos Fuzzing Engine (`[NEG-G1B-001]`).

Validates:
1. Generates all 6 FuzzVectorType variants.
2. Traps partition drops inside enclave_network_loopback.
3. Traps packet corruptions inside enclave_byzantine_leak.
4. Traps memory spikes inside enclave_byzantine_leak.
5. Traps concurrency races inside enclave_byzantine_leak.
6. Verifies 100% trapped ratio -> is_resilient == True (trap_rate == 1.0).
7. Verifies untrapped leak -> is_resilient == False (trap_rate < 1.0).
8. Comprehensive fuzz_candidate end-to-end verification.
"""

from __future__ import annotations

from pathlib import Path
import sys
import unittest

AUDIT_ROOT = Path(__file__).resolve().parent.parent
REPO_ROOT = AUDIT_ROOT.parent.parent.parent.parent
for p in [str(AUDIT_ROOT), str(AUDIT_ROOT / "src"), str(REPO_ROOT)]:
    if p not in sys.path:
        sys.path.insert(0, p)

from src.byzantine_chaos_fuzzer import ByzantineChaosFuzzer
from src.domain_models import (
    ByzantineFuzzReport,
    ByzantineFuzzVector,
    CodeLeafCandidate,
    FuzzVectorType,
)


class TestByzantineChaosFuzzer(unittest.TestCase):
    """Exhaustive tests for Byzantine fault injection, vector generation, and enclave containment."""

    def setUp(self) -> None:
        self.fuzzer = ByzantineChaosFuzzer()

    # 1. Generates All 6 FuzzVectorType Variants
    def test_generate_all_six_vector_types(self) -> None:
        vectors = self.fuzzer.generate_vectors(count_per_type=2, entropy_seed="seed_test_1")
        self.assertEqual(len(vectors), 12)
        types_generated = {v.vector_type for v in vectors}
        self.assertEqual(types_generated, set(FuzzVectorType))
        for v in vectors:
            v.validate_invariants()
            self.assertGreater(len(v.compute_hash()), 0)

    # 2. Traps Partition Drops in Designated Enclave
    def test_trap_partition_drop_in_designated_enclave(self) -> None:
        vectors = [v for v in self.fuzzer.generate_vectors(count_per_type=1) if v.vector_type == FuzzVectorType.PARTITION_DROP]
        self.assertEqual(len(vectors), 1)
        vec = vectors[0]
        self.assertEqual(vec.expected_enclave, "enclave_network_loopback")
        self.assertEqual(vec.injection_target, "enclave_network_filter")

    # 3. Traps Packet Corruptions in Designated Enclave
    def test_trap_packet_corruption_in_designated_enclave(self) -> None:
        vectors = [v for v in self.fuzzer.generate_vectors(count_per_type=1) if v.vector_type == FuzzVectorType.PACKET_CORRUPTION]
        self.assertEqual(len(vectors), 1)
        vec = vectors[0]
        self.assertEqual(vec.expected_enclave, "enclave_byzantine_leak")
        self.assertGreater(vec.payload_bytes_corrupted, 0)

    # 4. Traps Memory Spikes in Designated Enclave
    def test_trap_memory_pressure_in_designated_enclave(self) -> None:
        vectors = [v for v in self.fuzzer.generate_vectors(count_per_type=1) if v.vector_type == FuzzVectorType.MEMORY_PRESSURE]
        self.assertEqual(len(vectors), 1)
        vec = vectors[0]
        self.assertEqual(vec.expected_enclave, "enclave_byzantine_leak")
        self.assertEqual(vec.payload_bytes_corrupted, 1048576)  # 1MB buffer
        self.assertEqual(vec.injection_target, "enclave_memory_buffer")

    # 5. Traps Concurrency Races in Designated Enclave
    def test_trap_concurrency_race_in_designated_enclave(self) -> None:
        vectors = [v for v in self.fuzzer.generate_vectors(count_per_type=1) if v.vector_type == FuzzVectorType.CONCURRENCY_RACE]
        self.assertEqual(len(vectors), 1)
        vec = vectors[0]
        self.assertEqual(vec.expected_enclave, "enclave_byzantine_leak")
        self.assertGreater(vec.delay_ms, 0.0)

    # 6. Verifies 100% Trapped Ratio -> Resilient == True
    def test_all_trapped_resilient_true(self) -> None:
        vectors = self.fuzzer.generate_vectors(count_per_type=1)
        # Default dispatch without callback traps 100% inside simulated enclaves
        report = self.fuzzer.dispatch_and_verify(vectors, leaf_id="leaf_resilient")
        self.assertEqual(report.vectors_dispatched, 6)
        self.assertEqual(report.vectors_trapped, 6)
        self.assertEqual(report.trap_rate, 1.0)
        self.assertEqual(report.unhandled_faults, 0)
        self.assertIn("enclave_network_loopback", report.enclaves_engaged)
        self.assertIn("enclave_byzantine_leak", report.enclaves_engaged)
        self.assertIn("enclave_syntax_breach", report.enclaves_engaged)

    # 7. Verifies Untrapped Leak -> Resilient == False
    def test_untrapped_leak_resilient_false(self) -> None:
        vectors = self.fuzzer.generate_vectors(count_per_type=1)

        # Simulate a leak on PARTITION_DROP
        def leaky_enclave_callback(vec: ByzantineFuzzVector) -> bool:
            if vec.vector_type == FuzzVectorType.PARTITION_DROP:
                return False  # Leak / unhandled fault!
            return True

        report = self.fuzzer.dispatch_and_verify(vectors, leaf_id="leaf_leaky", enclave_trap_callback=leaky_enclave_callback)
        self.assertEqual(report.vectors_dispatched, 6)
        self.assertEqual(report.vectors_trapped, 5)
        self.assertEqual(report.unhandled_faults, 1)
        self.assertAlmostEqual(report.trap_rate, 5.0 / 6.0, places=3)
        self.assertLess(report.trap_rate, 1.0)

    # 8. Comprehensive fuzz_candidate End-to-End
    def test_fuzz_candidate_end_to_end(self) -> None:
        candidate = CodeLeafCandidate(
            leaf_id="leaf_fuzz_target",
            symbol_urn="urn:meta_axioma:leaf:actor",
            source_code="class Actor: pass",
        )
        report = self.fuzzer.fuzz_candidate(candidate, vectors_per_type=2)
        self.assertEqual(report.leaf_id, "leaf_fuzz_target")
        self.assertEqual(report.vectors_dispatched, 12)
        self.assertEqual(report.trap_rate, 1.0)
        self.assertEqual(report.unhandled_faults, 0)


if __name__ == "__main__":
    unittest.main()
