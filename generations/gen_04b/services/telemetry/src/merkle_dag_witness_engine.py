"""Cryptographic Merkle-DAG Witness Engine (`soc_g4b_telemetry`).

Enforces:
- Invariant [L1-G3B-017]: SHA-256 Chained Cryptographic Telemetry & Merkle-DAG Witnessing.
- Immutable binary Merkle tree anchoring telemetry events (spans, metrics, dissipation events, SLA reports).
- Complete cryptographic inclusion proof generation and verification.
- Tamper-evident DAG witness validation and certified TelemetryAttestation minting.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import json
import time
from typing import Any, Dict, List, Optional, Tuple
import uuid

from .domain_models import (
    assert_non_loopback,
    MerkleTreeNode,
    TelemetryAttestation,
    TelemetryDomainInvariantViolation,
)


class TelemetryMerkleWitnessEngine:
    """Constructs, queries, and verifies cryptographic SHA-256 Merkle-DAG trees for telemetry events."""

    GENESIS_ROOT = hashlib.sha256(b"GENESIS_EMPTY_TELEMETRY_MERKLE_ROOT").hexdigest()

    def __init__(self, node_id: str = "node_telemetry_merkle_witness") -> None:
        self.node_id = node_id
        self._leaves: List[str] = []
        self._leaf_nodes: Dict[str, MerkleTreeNode] = {}
        self._all_nodes: Dict[str, MerkleTreeNode] = {}
        self._cached_root: Optional[str] = None
        self._event_history: List[Dict[str, Any]] = []

    def record_event(self, event_type: str, payload: Dict[str, Any]) -> str:
        """Records a new telemetry event leaf into the Merkle DAG and invalidates the cached root."""
        if not event_type:
            raise TelemetryDomainInvariantViolation("event_type must not be empty.")

        ts = int(time.time() * 1000)
        serialized = json.dumps(payload, sort_keys=True)
        raw_leaf_data = f"{event_type}:{ts}:{serialized}"
        leaf_hash = hashlib.sha256(raw_leaf_data.encode("utf-8")).hexdigest()

        node = MerkleTreeNode(
            node_hash=leaf_hash,
            leaf_data=raw_leaf_data,
            is_leaf=True,
        )
        node.validate_invariants()

        self._leaves.append(leaf_hash)
        self._leaf_nodes[leaf_hash] = node
        self._all_nodes[leaf_hash] = node
        self._cached_root = None  # Invalidate cache

        self._event_history.append({
            "leaf_hash": leaf_hash,
            "event_type": event_type,
            "payload": payload,
            "timestamp_ms": ts,
        })

        return leaf_hash

    def compute_root(self) -> str:
        """Computes pairwise SHA-256 binary Merkle root hash of all recorded leaves."""
        if not self._leaves:
            self._cached_root = self.GENESIS_ROOT
            return self.GENESIS_ROOT

        current_level = list(self._leaves)

        while len(current_level) > 1:
            next_level: List[str] = []
            for i in range(0, len(current_level), 2):
                left = current_level[i]
                if i + 1 < len(current_level):
                    right = current_level[i + 1]
                else:
                    right = left  # Duplicate last element if odd count

                combined = f"{left}:{right}"
                parent_hash = hashlib.sha256(combined.encode("utf-8")).hexdigest()

                parent_node = MerkleTreeNode(
                    node_hash=parent_hash,
                    left_child=left,
                    right_child=right,
                    is_leaf=False,
                )
                self._all_nodes[parent_hash] = parent_node
                next_level.append(parent_hash)

            current_level = next_level

        self._cached_root = current_level[0]
        return self._cached_root

    def generate_inclusion_proof(self, leaf_hash: str) -> List[Dict[str, str]]:
        """Generates an authentication path (inclusion proof) for a specific leaf."""
        if leaf_hash not in self._leaf_nodes:
            raise TelemetryDomainInvariantViolation(f"Leaf hash '{leaf_hash}' not found in Merkle DAG.")

        if not self._leaves:
            return []

        # Find leaf index
        target_idx = self._leaves.index(leaf_hash)
        proof: List[Dict[str, str]] = []

        current_level = list(self._leaves)
        idx = target_idx

        while len(current_level) > 1:
            # Determine sibling
            if idx % 2 == 0:
                # Target is left child, sibling is right child
                if idx + 1 < len(current_level):
                    sibling_hash = current_level[idx + 1]
                else:
                    sibling_hash = current_level[idx]
                proof.append({"position": "right", "hash": sibling_hash})
            else:
                # Target is right child, sibling is left child
                sibling_hash = current_level[idx - 1]
                proof.append({"position": "left", "hash": sibling_hash})

            # Next level
            next_level: List[str] = []
            for i in range(0, len(current_level), 2):
                left = current_level[i]
                right = current_level[i + 1] if i + 1 < len(current_level) else left
                combined = f"{left}:{right}"
                parent = hashlib.sha256(combined.encode("utf-8")).hexdigest()
                next_level.append(parent)

            idx = idx // 2
            current_level = next_level

        return proof

    @classmethod
    def verify_inclusion_proof(
        cls,
        leaf_hash: str,
        proof: List[Dict[str, str]],
        expected_root: str,
    ) -> bool:
        """Verifies that leaf_hash belongs to the tree represented by expected_root using the proof path."""
        if not leaf_hash or not expected_root:
            return False

        if not proof:
            return leaf_hash == expected_root

        current_hash = leaf_hash
        for step in proof:
            sibling = step.get("hash", "")
            pos = step.get("position", "")

            if pos == "right":
                combined = f"{current_hash}:{sibling}"
            elif pos == "left":
                combined = f"{sibling}:{current_hash}"
            else:
                return False

            current_hash = hashlib.sha256(combined.encode("utf-8")).hexdigest()

        return current_hash == expected_root

    def verify_chain_integrity(self) -> bool:
        """Verifies cryptographic DAG consistency, leaves existence, and recomputed root match."""
        if not self._leaves:
            return self.compute_root() == self.GENESIS_ROOT

        # Recompute root independently and compare
        cached = self._cached_root
        recomputed = self.compute_root()
        if cached is not None and cached != recomputed:
            return False

        for leaf_hash in self._leaves:
            if leaf_hash not in self._leaf_nodes:
                return False
            node = self._leaf_nodes[leaf_hash]
            if not node.is_leaf or not node.leaf_data:
                return False
            expected_hash = hashlib.sha256(node.leaf_data.encode("utf-8")).hexdigest()
            if expected_hash != leaf_hash:
                return False

        return True

    def mint_attestation(
        self,
        attestation_id: str,
        service_name: str,
        node_ip: str,
        port: int,
        sla_certified: bool,
        landauer_certified: bool,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> TelemetryAttestation:
        """Mints and signs a TelemetryAttestation anchoring current Merkle root and certifications."""
        assert_non_loopback(node_ip, f"TelemetryMerkleWitnessEngine.mint_attestation '{service_name}'")
        root = self.compute_root()

        signature_payload = (
            f"SIG:{attestation_id}:{service_name}:{node_ip}:{port}:{root}:"
            f"{sla_certified}:{landauer_certified}"
        )
        signature = hashlib.sha256(signature_payload.encode("utf-8")).hexdigest()

        attestation = TelemetryAttestation(
            attestation_id=attestation_id,
            service_name=service_name,
            node_ip=node_ip,
            port=port,
            Merkle_root=root,
            sla_certified=sla_certified,
            landauer_certified=landauer_certified,
            signature=signature,
            metadata=metadata or {},
        )
        attestation.validate_invariants()
        return attestation

    @property
    def leaves_count(self) -> int:
        return len(self._leaves)

    @property
    def leaves(self) -> List[str]:
        return list(self._leaves)
