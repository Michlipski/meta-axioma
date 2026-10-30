"""Unit, cryptographic, and invariant tests for Merkle-DAG Witness Engine (`soc_g4b_telemetry`).

Verifies:
- [L1-G3B-017] SHA-256 Chained Cryptographic Telemetry & Merkle-DAG Witnessing.
- Deterministic Merkle root calculation across 0, 1, odd, and even leaf counts.
- Genesis empty root consistency.
- Cryptographic inclusion proof generation and verification paths.
- Tamper detection on modified payloads, mutated siblings, or altered root hashes.
- Tamper-evident DAG chain integrity checks.
- Certified TelemetryAttestation minting, signing, and loopback rejection.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
import sys
import unittest

TEL_ROOT = Path(__file__).resolve().parent.parent
REPO_ROOT = TEL_ROOT.parent.parent.parent.parent
for p in [str(TEL_ROOT), str(REPO_ROOT)]:
    if p not in sys.path:
        sys.path.insert(0, p)

from generations.gen_04b.services.telemetry.src.domain_models import (
    TelemetryDomainInvariantViolation,
)
from generations.gen_04b.services.telemetry.src.merkle_dag_witness_engine import (
    TelemetryMerkleWitnessEngine,
)


class TestTelemetryMerkleWitnessEngine(unittest.TestCase):
    """Test suite for TelemetryMerkleWitnessEngine binary Merkle DAG and inclusion proofs."""

    def setUp(self):
        self.engine = TelemetryMerkleWitnessEngine(node_id="test_merkle_node")

    def test_genesis_empty_root(self):
        root = self.engine.compute_root()
        self.assertEqual(root, TelemetryMerkleWitnessEngine.GENESIS_ROOT)
        self.assertEqual(self.engine.leaves_count, 0)
        self.assertTrue(self.engine.verify_chain_integrity())

    def test_single_leaf_root_and_proof(self):
        leaf_hash = self.engine.record_event("SPAN_INGEST", {"span_id": "s_single", "duration": 5.0})
        self.assertEqual(self.engine.leaves_count, 1)

        root = self.engine.compute_root()
        # Single leaf root is the leaf itself
        self.assertEqual(root, leaf_hash)

        proof = self.engine.generate_inclusion_proof(leaf_hash)
        self.assertEqual(len(proof), 0)
        # Empty proof against identical leaf and root evaluates True
        self.assertTrue(TelemetryMerkleWitnessEngine.verify_inclusion_proof(leaf_hash, proof, root))

    def test_even_count_leaves_merkle_tree(self):
        leaf_hashes = []
        for i in range(4):
            lh = self.engine.record_event("METRIC_INGEST", {"metric_idx": i, "val": i * 10})
            leaf_hashes.append(lh)

        self.assertEqual(self.engine.leaves_count, 4)
        root = self.engine.compute_root()
        self.assertEqual(len(root), 64)

        # Independent manual calculation:
        # p01 = H(lh0:lh1), p23 = H(lh2:lh3), root = H(p01:p23)
        p01 = hashlib.sha256(f"{leaf_hashes[0]}:{leaf_hashes[1]}".encode("utf-8")).hexdigest()
        p23 = hashlib.sha256(f"{leaf_hashes[2]}:{leaf_hashes[3]}".encode("utf-8")).hexdigest()
        expected_root = hashlib.sha256(f"{p01}:{p23}".encode("utf-8")).hexdigest()
        self.assertEqual(root, expected_root)

        # Verify inclusion proof for all 4 leaves
        for lh in leaf_hashes:
            proof = self.engine.generate_inclusion_proof(lh)
            self.assertEqual(len(proof), 2)
            self.assertTrue(TelemetryMerkleWitnessEngine.verify_inclusion_proof(lh, proof, root))

    def test_odd_count_leaves_merkle_tree(self):
        leaf_hashes = []
        for i in range(3):
            lh = self.engine.record_event("EVENT_ODD", {"idx": i})
            leaf_hashes.append(lh)

        root = self.engine.compute_root()
        self.assertEqual(self.engine.leaves_count, 3)

        # Verify inclusion proofs for all 3 leaves under duplication semantics
        for lh in leaf_hashes:
            proof = self.engine.generate_inclusion_proof(lh)
            self.assertTrue(TelemetryMerkleWitnessEngine.verify_inclusion_proof(lh, proof, root))

    def test_inclusion_proof_verification_tamper_detection(self):
        l1 = self.engine.record_event("EV1", {"data": 1})
        l2 = self.engine.record_event("EV2", {"data": 2})
        root = self.engine.compute_root()
        proof = self.engine.generate_inclusion_proof(l1)

        # Tampered leaf hash
        tampered_leaf = "0" * 64
        self.assertFalse(TelemetryMerkleWitnessEngine.verify_inclusion_proof(tampered_leaf, proof, root))

        # Tampered root hash
        tampered_root = "f" * 64
        self.assertFalse(TelemetryMerkleWitnessEngine.verify_inclusion_proof(l1, proof, tampered_root))

        # Tampered proof sibling
        tampered_proof = [{"position": proof[0]["position"], "hash": "e" * 64}]
        self.assertFalse(TelemetryMerkleWitnessEngine.verify_inclusion_proof(l1, tampered_proof, root))

    def test_chain_integrity_verification_and_tampering(self):
        l1 = self.engine.record_event("EV_CHAIN_1", {"v": 10})
        l2 = self.engine.record_event("EV_CHAIN_2", {"v": 20})
        self.engine.compute_root()

        self.assertTrue(self.engine.verify_chain_integrity())

        # Tamper with internal leaf node data
        self.engine._leaf_nodes[l1].leaf_data = "CORRUPTED_LEAF_DATA"
        self.assertFalse(self.engine.verify_chain_integrity())

    def test_mint_attestation_happy_path(self):
        self.engine.record_event("SLA_RUN", {"sla": True})
        attestation = self.engine.mint_attestation(
            attestation_id="att_test_101",
            service_name="telemetry_service",
            node_ip="192.168.40.40",
            port=8446,
            sla_certified=True,
            landauer_certified=True,
            metadata={"build": "g4b_phase4"},
        )
        self.assertEqual(attestation.attestation_id, "att_test_101")
        self.assertEqual(attestation.service_name, "telemetry_service")
        self.assertEqual(attestation.node_ip, "192.168.40.40")
        self.assertEqual(attestation.port, 8446)
        self.assertTrue(attestation.sla_certified)
        self.assertTrue(attestation.landauer_certified)
        self.assertEqual(len(attestation.signature), 64)
        self.assertEqual(attestation.Merkle_root, self.engine.compute_root())

    def test_mint_attestation_loopback_rejection(self):
        with self.assertRaises(TelemetryDomainInvariantViolation):
            self.engine.mint_attestation(
                attestation_id="att_bad",
                service_name="telemetry_service",
                node_ip="127.0.0.1",
                port=8446,
                sla_certified=True,
                landauer_certified=True,
            )

    def test_record_event_empty_type_rejection(self):
        with self.assertRaises(TelemetryDomainInvariantViolation):
            self.engine.record_event("", {"data": "test"})

    def test_proof_for_nonexistent_leaf_rejection(self):
        with self.assertRaises(TelemetryDomainInvariantViolation):
            self.engine.generate_inclusion_proof("nonexistent_leaf_hash")


if __name__ == "__main__":
    unittest.main()
