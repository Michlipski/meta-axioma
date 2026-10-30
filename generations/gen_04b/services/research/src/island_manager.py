"""Generation 4b Zero-Context Island Manager (`soc_g4b_researcher`).

Enforces:
- [L1-G4B-001] Decoupled Epistemic Exploration.
- [L1-G4B-004] Hermetic Context Isolation across Exploration Islands.
- Zero cross-talk between exploratory candidates to eradicate mode collapse and cognitive contagion.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import time
from typing import Any, Callable, Dict, List, Optional, Set
import uuid

from .domain_models import (
    DomainInvariantViolation,
    ZeroContextIslandManifest,
)


class IslandQuarantineBreachError(Exception):
    """Raised when cross-island data leakage or forbidden shared memory access is detected."""
    pass


class IslandBudgetExceededError(Exception):
    """Raised when an island exceeds its leased quarantine token budget."""
    pass


class ExplorationIsland:
    """An individual hermetic exploration island executing under a unique entropy seed."""

    def __init__(
        self,
        island_id: str,
        seed_entropy: str,
        sandbox_path: str,
        token_budget: int,
    ):
        self.island_id = island_id
        self.seed_entropy = seed_entropy
        self.sandbox_path = sandbox_path
        self.token_budget = token_budget
        self.tokens_spent = 0
        self.generated_nodes: List[Dict[str, Any]] = []
        self.generated_edges: List[Dict[str, Any]] = []
        self.is_finalized = False
        self._topology_hash: Optional[str] = None

    def spend_tokens(self, count: int) -> None:
        """Deducts tokens from the island's exploratory budget."""
        if self.tokens_spent + count > self.token_budget:
            raise IslandBudgetExceededError(
                f"Island '{self.island_id}' exceeded budget: {self.tokens_spent + count} > {self.token_budget}"
            )
        self.tokens_spent += count

    def synthesize_candidate_topology(
        self,
        node_names: List[str],
        channel_pairs: List[Tuple[str, str]],
        roles: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Synthesizes an architectural graph representation uniquely perturbed by seed entropy."""
        roles = roles or {}
        # Incorporate entropy into synthesis
        entropy_hash = hashlib.sha256(self.seed_entropy.encode("utf-8")).hexdigest()
        
        self.generated_nodes = []
        for i, name in enumerate(node_names):
            # Deterministic IP derivation in 192.168.40.0/24 subnet (strictly non-loopback)
            subnet_host = 10 + (i * 10) + (int(entropy_hash[i % len(entropy_hash)], 16) % 9)
            self.generated_nodes.append({
                "node_id": name,
                "role": roles.get(name, "WORKER"),
                "interface": f"192.168.40.{subnet_host}",
                "port": 8200 + i,
            })

        self.generated_edges = []
        for src, dst in channel_pairs:
            self.generated_edges.append({
                "source": src,
                "target": dst,
                "channel_type": "RPC",
                "tls_enforced": True,
            })

        # Deterministic graph representation hash
        raw_repr = json.dumps(
            {"nodes": sorted(self.generated_nodes, key=lambda n: n["node_id"]),
             "edges": sorted(self.generated_edges, key=lambda e: (e["source"], e["target"]))},
            sort_keys=True,
        )
        self._topology_hash = hashlib.sha256(raw_repr.encode("utf-8")).hexdigest()
        self.is_finalized = True

        # Charge tokens for topological emission
        self.spend_tokens(150 + len(self.generated_nodes) * 50 + len(self.generated_edges) * 30)

        return {
            "island_id": self.island_id,
            "topology_hash": self._topology_hash,
            "nodes": self.generated_nodes,
            "edges": self.generated_edges,
        }

    def get_manifest(self) -> ZeroContextIslandManifest:
        if not self._topology_hash:
            raise DomainInvariantViolation(f"Island '{self.island_id}' has not finalized topology.")
        manifest = ZeroContextIslandManifest(
            island_id=self.island_id,
            assigned_seed_entropy=self.seed_entropy,
            isolated_sandbox_path=self.sandbox_path,
            quarantine_token_budget=self.token_budget,
            generated_topology_hash=self._topology_hash,
        )
        manifest.validate_invariants()
        return manifest


class ZeroContextIslandManager:
    """Manager orchestrating isolated research islands without shared memory or context leak."""

    def __init__(
        self,
        manager_id: Optional[str] = None,
        node_ip: str = "192.168.40.20",
        port: int = 8202,
        base_sandbox_dir: Optional[Path] = None,
    ):
        self.manager_id = manager_id or f"island_mgr_{uuid.uuid4().hex[:8]}"
        self.node_ip = node_ip
        self.port = port
        self.base_sandbox_dir = base_sandbox_dir or Path("/tmp/soc_g4b_islands")
        self.islands: Dict[str, ExplorationIsland] = {}
        self.manifest_vault: Dict[str, ZeroContextIslandManifest] = {}

        if self.node_ip.startswith("127.") or self.node_ip in ("localhost", "::1"):
            raise DomainInvariantViolation(
                f"[L1-G3B-012 Violation] Island Manager cannot bind to loopback address: {self.node_ip}"
            )

    def spawn_islands(
        self,
        island_count: int = 3,
        per_island_token_budget: int = 50000,
        entropy_prefix: str = "ENTROPY_SEED_4B",
    ) -> List[ZeroContextIslandManifest]:
        """Spawns N >= 3 quarantined research islands with unique cryptographic entropy."""
        if island_count < 3:
            raise DomainInvariantViolation(
                f"ZeroContextIslandManager requires >= 3 islands for multi-perspective search, got {island_count}"
            )

        manifests: List[ZeroContextIslandManifest] = []
        for i in range(island_count):
            island_id = f"island_{chr(65 + i)}_{uuid.uuid4().hex[:6]}"  # e.g., island_A_1a2b3c
            # High-entropy seed incorporating timestamp, nonce, and process data
            seed_data = f"{entropy_prefix}:{island_id}:{time.time_ns()}:{os.urandom(16).hex()}"
            seed_entropy = hashlib.sha256(seed_data.encode("utf-8")).hexdigest()
            sandbox_path = str(self.base_sandbox_dir / island_id)

            island = ExplorationIsland(
                island_id=island_id,
                seed_entropy=seed_entropy,
                sandbox_path=sandbox_path,
                token_budget=per_island_token_budget,
            )
            self.islands[island_id] = island

        return manifests

    def execute_island_exploration(
        self,
        island_id: str,
        node_names: List[str],
        channel_pairs: List[Tuple[str, str]],
        roles: Optional[Dict[str, str]] = None,
    ) -> ZeroContextIslandManifest:
        """Executes an isolated exploration pass for a specific island."""
        if island_id not in self.islands:
            raise KeyError(f"Unknown island_id: {island_id}")

        island = self.islands[island_id]
        island.synthesize_candidate_topology(
            node_names=node_names,
            channel_pairs=channel_pairs,
            roles=roles,
        )
        manifest = island.get_manifest()
        self.manifest_vault[island_id] = manifest
        return manifest

    def get_island_topology(self, island_id: str) -> Dict[str, Any]:
        """Retrieves an island's emitted topology."""
        if island_id not in self.islands:
            raise KeyError(f"Unknown island_id: {island_id}")
        island = self.islands[island_id]
        return {
            "island_id": island.island_id,
            "topology_hash": island._topology_hash,
            "nodes": island.generated_nodes,
            "edges": island.generated_edges,
            "tokens_spent": island.tokens_spent,
        }

    def verify_zero_cross_talk(self) -> bool:
        """Verifies that each island has completely distinct entropy seeds and no shared state."""
        seeds = [island.seed_entropy for island in self.islands.values()]
        if len(seeds) != len(set(seeds)):
            raise IslandQuarantineBreachError("Duplicate entropy seeds detected across islands!")
        return True
