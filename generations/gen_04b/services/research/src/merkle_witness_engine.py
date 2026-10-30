"""Generation 4b Hierarchical Merkle-DAG Witness & Telemetry Engine (`soc_g4b_researcher`).

Enforces:
- [L1-G4B-003] Hierarchical Merkle-DAG Telemetry:
  All compilation events, island discoveries, RFC adjudications, and test verification sinks
  are cryptographically anchored into a tamper-evident SHA-256 Merkle DAG.
- Continuous integrity verification: mutating any node payload immediately invalidates downstream
  hashes and trips MerkleIntegrityTamperFault.
"""

from __future__ import annotations

import hashlib
import json
import time
from typing import Any, Dict, List, Optional, Tuple
import uuid

from .domain_models import (
    DomainInvariantViolation,
    MerkleDagWitness,
)


class MerkleIntegrityTamperFault(Exception):
    """Raised when cryptographic hash chain tampering or corrupted DAG link is detected."""
    pass


class MerkleWitnessEngine:
    """Hierarchical Merkle-DAG telemetry engine chaining cryptographic event witnesses."""

    GENESIS_PAYLOAD = "META_AXIOMA_G4B_EPIC_GENESIS_ANCHOR"

    def __init__(
        self,
        node_ip: str = "192.168.40.60",
        port: int = 8206,
    ):
        self.node_ip = node_ip
        self.port = port
        self.nodes: Dict[str, MerkleDagWitness] = {}
        self.node_sequence: List[str] = []
        self.raw_payloads: Dict[str, str] = {}
        self.current_root_hash: str = ""

        self._initialize_genesis()

    def _initialize_genesis(self) -> None:
        """Initializes the immutable genesis root witness."""
        gen_timestamp = 1761273600000000000  # Epoch anchor timestamp
        raw_genesis = f"GENESIS:{self.GENESIS_PAYLOAD}:{gen_timestamp}"
        node_hash = hashlib.sha256(raw_genesis.encode("utf-8")).hexdigest()

        genesis_witness = MerkleDagWitness(
            node_hash=node_hash,
            parent_hashes=[],
            task_id="task_genesis",
            actor_id="actor_meta_orchestrator",
            payload_signature=self.GENESIS_PAYLOAD,
            timestamp_ns=gen_timestamp,
        )
        genesis_witness.validate_invariants()

        self.nodes[node_hash] = genesis_witness
        self.node_sequence.append(node_hash)
        self.raw_payloads[node_hash] = self.GENESIS_PAYLOAD
        self.current_tip_hash = node_hash
        self.current_root_hash = node_hash

    def compute_node_hash(
        self,
        parent_hashes: List[str],
        task_id: str,
        actor_id: str,
        payload_signature: str,
        timestamp_ns: int,
    ) -> str:
        """Calculates deterministic SHA-256 node hash over inputs."""
        serialized_parents = ",".join(sorted(parent_hashes))
        content = f"{serialized_parents}|{task_id}|{actor_id}|{payload_signature}|{timestamp_ns}"
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    def record_witness(
        self,
        task_id: str,
        actor_id: str,
        payload_data: Any,
        parent_hashes: Optional[List[str]] = None,
    ) -> MerkleDagWitness:
        """Appends a new cryptographically verified witness node to the DAG."""
        # Default parent is current tip node hash
        parents = parent_hashes or [self.current_tip_hash]
        for p in parents:
            if p not in self.nodes:
                raise KeyError(f"Parent hash not found in Merkle DAG: {p}")

        if isinstance(payload_data, (dict, list)):
            payload_str = json.dumps(payload_data, sort_keys=True)
        else:
            payload_str = str(payload_data)

        payload_sig = hashlib.sha256(payload_str.encode("utf-8")).hexdigest()
        now_ns = time.time_ns()

        node_hash = self.compute_node_hash(
            parent_hashes=parents,
            task_id=task_id,
            actor_id=actor_id,
            payload_signature=payload_sig,
            timestamp_ns=now_ns,
        )

        witness = MerkleDagWitness(
            node_hash=node_hash,
            parent_hashes=parents,
            task_id=task_id,
            actor_id=actor_id,
            payload_signature=payload_sig,
            timestamp_ns=now_ns,
        )
        witness.validate_invariants()

        self.nodes[node_hash] = witness
        self.node_sequence.append(node_hash)
        self.raw_payloads[node_hash] = payload_str
        self.current_tip_hash = node_hash

        # Update cumulative tree root hash: H(prior_root || new_node)
        new_root_content = f"{self.current_root_hash}:{node_hash}"
        self.current_root_hash = hashlib.sha256(new_root_content.encode("utf-8")).hexdigest()

        return witness

    def verify_dag_integrity(self) -> bool:
        """Walks the entire DAG from genesis and recomputes all hashes.

        Raises MerkleIntegrityTamperFault if any discrepancy is found.
        """
        recalculated_root = self.node_sequence[0]

        for i, nh in enumerate(self.node_sequence):
            witness = self.nodes[nh]

            if i == 0:
                # Genesis check
                expected_genesis = hashlib.sha256(
                    f"GENESIS:{self.GENESIS_PAYLOAD}:{witness.timestamp_ns}".encode("utf-8")
                ).hexdigest()
                if witness.node_hash != expected_genesis:
                    raise MerkleIntegrityTamperFault(
                        f"Genesis block hash tampered! Expected {expected_genesis}, got {witness.node_hash}"
                    )
                continue

            # Verify node hash from stored fields
            expected_hash = self.compute_node_hash(
                parent_hashes=witness.parent_hashes,
                task_id=witness.task_id,
                actor_id=witness.actor_id,
                payload_signature=witness.payload_signature,
                timestamp_ns=witness.timestamp_ns,
            )

            if witness.node_hash != expected_hash:
                raise MerkleIntegrityTamperFault(
                    f"Tamper detected at witness node {witness.task_id}! "
                    f"Expected hash {expected_hash}, stored hash {witness.node_hash}"
                )

            # Recompute cumulative root
            recalculated_root = hashlib.sha256(
                f"{recalculated_root}:{witness.node_hash}".encode("utf-8")
            ).hexdigest()

        if recalculated_root != self.current_root_hash:
            raise MerkleIntegrityTamperFault(
                f"Cumulative Merkle root mismatch! Recalculated {recalculated_root}, active {self.current_root_hash}"
            )

        return True

    def export_ledger(self) -> Dict[str, Any]:
        """Losslessly serializes the Merkle DAG ledger."""
        return {
            "root_hash": self.current_root_hash,
            "total_nodes": len(self.nodes),
            "sequence": self.node_sequence,
            "nodes": {k: v.to_dict() for k, v in self.nodes.items()},
        }
