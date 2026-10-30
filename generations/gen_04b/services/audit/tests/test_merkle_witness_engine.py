"""Unit & Adversarial Invariant Test Suite for Cryptographic Merkle Witness Engine (`[L1-G4B-003]`).

Validates:
1. Witness node chaining and deterministic root computation.
2. Genesis empty Merkle root computation.
3. Cryptographic DAG integrity verification.
4. Merkle inclusion proof generation and mathematical verification.
5. Tamper detection on corrupted leaf, sibling, or root hash.
6. Attestation minting and audit trail logging.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
import sys
import unittest

AUDIT_ROOT = Path(__file__).resolve().parent.parent
REPO_ROOT = AUDIT_ROOT.parent.parent.parent.parent
for p in [str(AUDIT_ROOT), str(AUDIT_ROOT / "src"), str(REPO_ROOT)]:
    if p not in sys.path:
        sys.path.insert(0, p)

from src.domain_models import (
    AuditAttestation,
    AuditDomainInvariantViolation,
    CodeLeafCandidate,
    QuorumConsensusWitness,
    QuorumVerdict,
)
from src.merkle_witness_engine import AuditMerkleWitnessEngine


class TestMerkleWitnessEngine(unittest.TestCase):
    """Exhaustive unit and adversarial test suite for Merkle DAG witness chaining and proofs."""

    def setUp(self) -> None:
        self.engine = AuditMerkleWitnessEngine()

    # 1. Witness Node Chaining & Deterministic Root Computation
    def test_record_events_and_deterministic_root_computation(self) -> None:
        h1 = self.engine.record_event("EVENT_A", {"key": "val1"})
        h2 = self.engine.record_event("EVENT_B", {"key": "val2"})
        h3 = self.engine.record_event("EVENT_C", {"key": "val3"})

        root1 = self.engine.compute_merkle_root()
        self.assertEqual(len(root1), 64)
        # Calling compute_merkle_root again produces exact same root
        root2 = self.engine.compute_merkle_root()
        self.assertEqual(root1, root2)
        self.assertEqual(len(self.engine._leaves), 3)

    # 2. Genesis Empty Merkle Root
    def test_genesis_empty_merkle_root(self) -> None:
        empty_root = self.engine.compute_merkle_root()
        expected = hashlib.sha256(b"GENESIS_EMPTY_AUDIT_MERKLE_ROOT").hexdigest()
        self.assertEqual(empty_root, expected)

    # 3. Cryptographic DAG Integrity Verification
    def test_dag_integrity_verification(self) -> None:
        self.engine.record_event("EVENT_INIT", {"status": "ok"})
        self.engine.record_event("EVENT_LINT", {"violations": 0})
        self.assertTrue(self.engine.verify_integrity())

    # 4. Merkle Inclusion Proof Generation & Verification
    def test_merkle_inclusion_proof_verification(self) -> None:
        leaves = [
            self.engine.record_event(f"EVENT_{i}", {"seq": i})
            for i in range(4)
        ]
        root = self.engine.compute_merkle_root()

        for leaf in leaves:
            proof = self.engine.generate_inclusion_proof(leaf)
            self.assertGreater(len(proof), 0)
            verified = AuditMerkleWitnessEngine.verify_inclusion_proof(
                target_leaf_hash=leaf,
                proof=proof,
                expected_root=root,
            )
            self.assertTrue(verified)

    # 5. Tamper Detection on Corrupted Payload / Root Hash
    def test_tamper_detection_on_payload_or_root_corruption(self) -> None:
        leaves = [self.engine.record_event(f"EVENT_{i}", {"seq": i}) for i in range(4)]
        root = self.engine.compute_merkle_root()
        proof = self.engine.generate_inclusion_proof(leaves[0])

        # Verification with forged / corrupted root fails
        fake_root = hashlib.sha256(b"tampered_root_hash").hexdigest()
        self.assertFalse(
            AuditMerkleWitnessEngine.verify_inclusion_proof(leaves[0], proof, fake_root)
        )

        # Verification with corrupted sibling hash fails
        corrupted_proof = [(hashlib.sha256(b"bad_sibling").hexdigest(), proof[0][1])] + proof[1:]
        self.assertFalse(
            AuditMerkleWitnessEngine.verify_inclusion_proof(leaves[0], corrupted_proof, root)
        )

    # 6. Attestation Minting & Audit Trail Logging
    def test_mint_attestation_integration(self) -> None:
        leaf = CodeLeafCandidate(
            leaf_id="leaf_attest_test",
            symbol_urn="urn:meta_axioma:leaf:model",
            source_code="def model(): return True",
        )
        witness = QuorumConsensusWitness(
            witness_id="wit_attest_test",
            leaf_id=leaf.leaf_id,
            verdict=QuorumVerdict.UNANIMOUS_PASS,
            sentry_syntax_vote=True,
            oracle_smt_vote=True,
            adversary_chaos_vote=True,
            consensus_ratio=1.0,
            dissenting_nodes=[],
        )
        witness.consensus_hash = witness.compute_hash()

        attestation = self.engine.mint_attestation(witness, leaf, epoch=2)
        self.assertTrue(attestation.is_certified)
        self.assertEqual(attestation.attestation_epoch, 2)
        self.assertGreaterEqual(len(attestation.auditor_signatures), 2)
        self.assertEqual(len(attestation.merkle_leaf_hash), 64)
        self.assertEqual(len(attestation.merkle_root), 64)

        # Audit trail must contain this event
        trail = self.engine.get_audit_trail()
        self.assertGreater(len(trail), 0)
        last_event = trail[-1]
        self.assertEqual(last_event["event_type"], "AUDIT_ATTESTATION_SEALED")
        self.assertEqual(last_event["payload"]["leaf_id"], leaf.leaf_id)


if __name__ == "__main__":
    unittest.main()
