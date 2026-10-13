"""Evolutionary Island Generator for System G_1 Compiler.

Embodying [L1-017] Non-Linear Exploratory Trajectory & Tree Search Invariance:
Maintains orthogonal topological candidate branches across disjoint search islands,
guaranteeing multi-path exploration and lineage tracking over program AST space.
"""

from __future__ import annotations

import copy
import hashlib
import time
from typing import Any, Dict, List, Optional

from g1_compiler.types import CandidateArchitecture, SearchIsland


class IslandGenerator:
    """Maintains and evolves candidate system architectures across isolated topological islands."""

    DEFAULT_ISLANDS: List[SearchIsland] = [
        SearchIsland(
            island_id="ISLAND_SHEAF",
            name="Topological Sheaf Mesh",
            topology_type="Sheaf-Theoretic Local Sections Cover",
            core_thesis="Global distributed state emerges strictly through gluing mutually compatible local sections over open coverings.",
            description="Eliminates global locking; components publish local sections with pairwise cocycle consistency on overlaps.",
        ),
        SearchIsland(
            island_id="ISLAND_CRDT",
            name="Causal CRDT Lattice",
            topology_type="State-Based Monotonic Semi-Lattice",
            core_thesis="All state mutations commute monotonically across partial orderings via join-semilattices and causal vector clocks.",
            description="Permits asynchronous, disconnected writes with provable eventual convergence and zero coordination overhead.",
        ),
        SearchIsland(
            island_id="ISLAND_QUORUM",
            name="Quorum Consensus State Machine",
            topology_type="Term-Based Log Replicated Quorum",
            core_thesis="Strict linearizability maintained through majority quorums, lease-based leadership, and deterministic state transitions.",
            description="Guarantees CP consistency under network partitions by halting uncommitted transitions without majority quorum.",
        ),
        SearchIsland(
            island_id="ISLAND_ACTOR",
            name="Isolated Actor Event Bus",
            topology_type="Share-Nothing Actor Hierarchy",
            core_thesis="Zero shared mutable state; all interactions occur through capability-bounded asynchronous message mailboxes.",
            description="Isolates failure domains to actor supervision trees with automatic restarts and zero memory leakage.",
        ),
    ]

    def __init__(self, islands: Optional[List[SearchIsland]] = None):
        self.islands = {i.island_id: i for i in (islands or self.DEFAULT_ISLANDS)}
        self._candidate_counter = 0

    def get_islands(self) -> List[SearchIsland]:
        """Returns all active search islands."""
        return list(self.islands.values())

    def seed_candidate(self, island_id: str, name_suffix: str = "") -> CandidateArchitecture:
        """Seeds an initial candidate architecture for a given island."""
        if island_id not in self.islands:
            raise ValueError(f"Unknown island_id: {island_id}. Available: {list(self.islands.keys())}")

        island = self.islands[island_id]
        self._candidate_counter += 1
        cand_id = f"CAND_{island_id[:7]}_{self._candidate_counter:03d}{('_' + name_suffix) if name_suffix else ''}"

        base_ast: Dict[str, Any] = {
            "root_type": "DISTRIBUTED_COMPILER_NODE",
            "island_id": island_id,
            "topology_type": island.topology_type,
            "components": {
                "ingress": {
                    "type": "BoundedChannel",
                    "buffer_size": 1024,
                    "backpressure_strategy": "DROP_OLDEST",
                },
                "state_core": {
                    "model": island.topology_type,
                    "thesis": island.core_thesis,
                    "reversibility_enabled": True,
                    "enclave_wrapped": False,
                },
                "replication": {
                    "strategy": "ASYNC_GOSSIP" if island_id in ("ISLAND_SHEAF", "ISLAND_CRDT") else "MAJORITY_QUORUM",
                    "heartbeat_interval_ms": 100,
                    "quorum_size": 3,
                },
            },
            "invariants_embodied": ["L1-002", "L1-004", "L1-008", "L1-015"],
        }

        return CandidateArchitecture(
            candidate_id=cand_id,
            island_id=island_id,
            name=f"{island.name} Spec v1{(' ' + name_suffix) if name_suffix else ''}",
            topology_type=island.topology_type,
            specification_ast=base_ast,
            lineage=[],
            generation_step=1,
            mutations=["INITIAL_SEED"],
            timestamp=time.time(),
        )

    def mutate(
        self,
        candidate: CandidateArchitecture,
        mutation_type: str = "ConstraintTightening",
    ) -> CandidateArchitecture:
        """Applies an evolutionary mutation operator to a candidate's AST."""
        self._candidate_counter += 1
        new_id = f"CAND_{candidate.island_id[:7]}_{self._candidate_counter:03d}_MUT"
        new_ast = copy.deepcopy(candidate.specification_ast)
        mutations = list(candidate.mutations)

        if mutation_type == "ConstraintTightening":
            # Add strict timeouts and enclave boundaries
            new_ast["components"]["state_core"]["enclave_wrapped"] = True
            new_ast["components"]["replication"]["timeout_ms"] = 50
            new_ast["invariants_embodied"].append("L1-016")
            mutations.append("ConstraintTightening:EnclaveWrapped+StrictTimeout")

        elif mutation_type == "AstSubtreeSplice":
            # Splice in hybrid reconciliation mechanism
            new_ast["components"]["reconciliation"] = {
                "type": "PairwiseCocycleAudit",
                "max_drift_tolerance": 0.05,
                "entropy_reclamation_enabled": True,
            }
            new_ast["invariants_embodied"].append("L1-015_1")
            mutations.append("AstSubtreeSplice:PairwiseCocycleAudit")

        elif mutation_type == "InterfaceAttenuation":
            # Narrow ingress buffer and add capability token verification
            new_ast["components"]["ingress"]["capability_scoping"] = "HMAC_SHA256"
            new_ast["components"]["ingress"]["rate_limit_rps"] = 5000
            mutations.append("InterfaceAttenuation:HMACCapabilityScoping")

        else:
            mutations.append(f"GenericMutation:{mutation_type}")

        return CandidateArchitecture(
            candidate_id=new_id,
            island_id=candidate.island_id,
            name=f"{candidate.name} (Mutated: {mutation_type})",
            topology_type=candidate.topology_type,
            specification_ast=new_ast,
            lineage=candidate.lineage + [candidate.candidate_id],
            generation_step=candidate.generation_step + 1,
            mutations=mutations,
            timestamp=time.time(),
        )

    def recombine(
        self,
        parent_a: CandidateArchitecture,
        parent_b: CandidateArchitecture,
    ) -> CandidateArchitecture:
        """Performs crossover recombination between two parent candidate ASTs."""
        self._candidate_counter += 1
        hybrid_id = f"CAND_HYBRID_{self._candidate_counter:03d}"
        hybrid_ast = copy.deepcopy(parent_a.specification_ast)

        # Splice replication and state core from parent_b into hybrid
        if "reconciliation" in parent_b.specification_ast.get("components", {}):
            hybrid_ast["components"]["reconciliation"] = copy.deepcopy(
                parent_b.specification_ast["components"]["reconciliation"]
            )
        hybrid_ast["components"]["auxiliary_state_core"] = copy.deepcopy(
            parent_b.specification_ast["components"]["state_core"]
        )

        all_invariants = sorted(list(set(
            parent_a.specification_ast.get("invariants_embodied", [])
            + parent_b.specification_ast.get("invariants_embodied", [])
        )))
        hybrid_ast["invariants_embodied"] = all_invariants

        return CandidateArchitecture(
            candidate_id=hybrid_id,
            island_id=f"{parent_a.island_id}x{parent_b.island_id}",
            name=f"Hybrid({parent_a.name} x {parent_b.name})",
            topology_type=f"Hybrid({parent_a.topology_type} / {parent_b.topology_type})",
            specification_ast=hybrid_ast,
            lineage=list(set(parent_a.lineage + [parent_a.candidate_id] + parent_b.lineage + [parent_b.candidate_id])),
            generation_step=max(parent_a.generation_step, parent_b.generation_step) + 1,
            mutations=["CrossIslandRecombination"],
            timestamp=time.time(),
        )
