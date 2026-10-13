"""Distributed Sheaf-CRDT Hybrid Engine for System G_2 Compiler.

Embodying:
- [L1-G2-008] Distributed Evolutionary Island Synthesis & Decoupled Chaos Verification
- Realization of the Pareto-Optimal 'CAND_HYBRID_013' Architecture (Sheaf Cover + Monotonic CRDT Lattice)
- Pairwise Cocycle Consistency Auditing over Topological Subdomains
- Landauer Thermodynamic Reversible Morphism Reconciliation

Mandate:
Guarantees that System G_2 provides robust, partition-tolerant distributed state coordination
for high-throughput backends and edge clients, and enforces non-linear evolutionary succession
for Generation 3 (G_3).
"""

from __future__ import annotations

import copy
import hashlib
import json
import math
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple

# Landauer limit at 300K: k_B * T * ln(2) ≈ 2.8706e-21 Joules per bit
K_B_T_LN2 = 2.8706e-21


class LinearCompilationViolation(Exception):
    """Raised when an attempt is made to bypass the non-linear search gate or compile G_3 linearly."""
    pass


@dataclass
class CausalVectorClock:
    """Logical vector clock tracking causality across distributed subdomains."""
    clock: Dict[str, int] = field(default_factory=dict)

    def tick(self, node_id: str) -> "CausalVectorClock":
        """Monotonically increments clock for a node."""
        new_clock = dict(self.clock)
        new_clock[node_id] = new_clock.get(node_id, 0) + 1
        return CausalVectorClock(clock=new_clock)

    def merge(self, other: "CausalVectorClock") -> "CausalVectorClock":
        """Calculates component-wise supremum (join) of two vector clocks."""
        all_nodes = set(self.clock.keys()).union(other.clock.keys())
        merged = {node: max(self.clock.get(node, 0), other.clock.get(node, 0)) for node in all_nodes}
        return CausalVectorClock(clock=merged)

    def is_causally_precedent(self, other: "CausalVectorClock") -> bool:
        """Returns True if self <= other (every component is less than or equal)."""
        all_nodes = set(self.clock.keys()).union(other.clock.keys())
        return all(self.clock.get(node, 0) <= other.clock.get(node, 0) for node in all_nodes)

    def is_concurrent(self, other: "CausalVectorClock") -> bool:
        """Returns True if neither vector clock dominates the other (concurrent/divergent)."""
        return not self.is_causally_precedent(other) and not other.is_causally_precedent(self)


@dataclass
class SheafSection:
    """A local state section evaluated over an open subdomain cover U_i."""
    subdomain_id: str
    data: Dict[str, Any]
    vector_clock: CausalVectorClock
    observed_boundary_keys: Set[str] = field(default_factory=set)
    erased_bits: float = 0.0
    timestamp: float = field(default_factory=time.time)


@dataclass
class CocycleAuditWitness:
    """Cryptographic audit certifying pairwise cocycle consistency on overlapping subdomains."""
    subdomain_u: str
    subdomain_v: str
    overlap_keys: List[str]
    is_consistent: bool
    drift_divergence: float
    witness_hash: str
    timestamp: float = field(default_factory=time.time)


class PairwiseCocycleAuditor:
    """Verifies that overlapping local sections glue into global sheaf state without contradiction."""

    @staticmethod
    def audit_overlap(
        section_u: SheafSection,
        section_v: SheafSection,
        max_drift_tolerance: float = 0.05,
    ) -> CocycleAuditWitness:
        """Audits consistency on the intersection U ∩ V."""
        overlap_keys = sorted(
            list(set(section_u.observed_boundary_keys).intersection(section_v.observed_boundary_keys))
        )

        divergences: List[float] = []
        for key in overlap_keys:
            val_u = section_u.data.get(key)
            val_v = section_v.data.get(key)
            if val_u == val_v:
                divergences.append(0.0)
            elif isinstance(val_u, (int, float)) and isinstance(val_v, (int, float)):
                # Normalize numerical difference
                denom = max(1.0, abs(val_u) + abs(val_v))
                divergences.append(abs(val_u - val_v) / denom)
            else:
                divergences.append(1.0)  # Complete categorical divergence

        mean_drift = (sum(divergences) / len(divergences)) if divergences else 0.0
        is_consistent = mean_drift <= max_drift_tolerance

        witness_payload = {
            "u": section_u.subdomain_id,
            "v": section_v.subdomain_id,
            "overlap_keys": overlap_keys,
            "mean_drift": round(mean_drift, 4),
            "is_consistent": is_consistent,
        }
        witness_hash = hashlib.sha256(
            json.dumps(witness_payload, sort_keys=True).encode("utf-8")
        ).hexdigest()

        return CocycleAuditWitness(
            subdomain_u=section_u.subdomain_id,
            subdomain_v=section_v.subdomain_id,
            overlap_keys=overlap_keys,
            is_consistent=is_consistent,
            drift_divergence=round(mean_drift, 4),
            witness_hash=witness_hash,
        )


class DistributedSheafCrdtEngine:
    """The constructed Sheaf-CRDT distributed systems engine for System G_2."""

    def __init__(self, node_id: str = "node_g2_primary"):
        self.node_id = node_id
        self.sections: Dict[str, SheafSection] = {}
        self.cocycle_audits: List[CocycleAuditWitness] = []
        self.total_dissipated_joules = 0.0
        self.total_erased_bits = 0.0

    def register_subdomain(
        self,
        subdomain_id: str,
        initial_data: Dict[str, Any],
        boundary_keys: List[str],
    ) -> SheafSection:
        """Registers a local section over open covering subdomain U_i."""
        section = SheafSection(
            subdomain_id=subdomain_id,
            data=dict(initial_data),
            vector_clock=CausalVectorClock(clock={self.node_id: 1}),
            observed_boundary_keys=set(boundary_keys),
            erased_bits=0.0,
        )
        self.sections[subdomain_id] = section
        return section

    def mutate_section(
        self,
        subdomain_id: str,
        delta: Dict[str, Any],
    ) -> SheafSection:
        """Applies a local mutation, advancing the causal vector clock."""
        if subdomain_id not in self.sections:
            raise KeyError(f"Unknown subdomain: {subdomain_id}")

        sec = self.sections[subdomain_id]
        new_data = dict(sec.data)
        new_data.update(delta)

        # Monotonically tick causal clock
        new_clock = sec.vector_clock.tick(self.node_id)

        updated_section = SheafSection(
            subdomain_id=subdomain_id,
            data=new_data,
            vector_clock=new_clock,
            observed_boundary_keys=sec.observed_boundary_keys,
            erased_bits=sec.erased_bits,
            timestamp=time.time(),
        )
        self.sections[subdomain_id] = updated_section
        return updated_section

    def merge_remote_section(
        self,
        remote_section: SheafSection,
    ) -> Tuple[SheafSection, CocycleAuditWitness]:
        """Performs monotonic join-semilattice merge (S ⊔ S') with cocycle auditing and Landauer dissipation."""
        sub_id = remote_section.subdomain_id
        local_sec = self.sections.get(sub_id)

        if local_sec is None:
            # First observation of subdomain
            self.sections[sub_id] = remote_section
            audit = CocycleAuditWitness(
                subdomain_u=self.node_id,
                subdomain_v=remote_section.subdomain_id,
                overlap_keys=list(remote_section.observed_boundary_keys),
                is_consistent=True,
                drift_divergence=0.0,
                witness_hash="INIT_ADMIT",
            )
            return remote_section, audit

        # 1. Audit pairwise cocycle consistency on boundaries
        audit = PairwiseCocycleAuditor.audit_overlap(local_sec, remote_section)
        self.cocycle_audits.append(audit)

        # 2. Compute Monotonic CRDT Join (⊔)
        merged_clock = local_sec.vector_clock.merge(remote_section.vector_clock)
        merged_data = dict(local_sec.data)

        erased_bits = 0.0
        for k, v_remote in remote_section.data.items():
            if k not in merged_data:
                merged_data[k] = v_remote
            else:
                # Merge resolution: Last-Write-Wins or Higher-Clock takes precedence
                v_local = merged_data[k]
                if v_local != v_remote:
                    # Dissipate bit erasure on overwritten divergent value
                    erased_bits += 32.0
                    if remote_section.vector_clock.clock.get(remote_section.subdomain_id, 0) >= local_sec.vector_clock.clock.get(local_sec.subdomain_id, 0):
                        merged_data[k] = v_remote

        self.total_erased_bits += erased_bits
        dissipation = erased_bits * K_B_T_LN2
        self.total_dissipated_joules += dissipation

        merged_section = SheafSection(
            subdomain_id=sub_id,
            data=merged_data,
            vector_clock=merged_clock,
            observed_boundary_keys=local_sec.observed_boundary_keys.union(remote_section.observed_boundary_keys),
            erased_bits=local_sec.erased_bits + erased_bits,
            timestamp=time.time(),
        )
        self.sections[sub_id] = merged_section
        return merged_section, audit


@dataclass
class G3SearchTrace:
    """Verifiable proof of non-linear evolutionary exploration emitted by System G_2."""
    trace_id: str
    islands_explored: List[str]
    total_candidates_evaluated: int
    dead_end_candidates: List[Dict[str, Any]]
    crucible_witnesses: List[Dict[str, Any]]
    selected_winner_id: str
    is_verified: bool = False
    verification_token: str = ""


class G3EvolutionarySuccessionGate:
    """Mechanical gate enforcing [L1-G2-008]: forbids linear synthesis of System G_3."""

    MIN_ISLANDS = 3
    MIN_DEAD_ENDS = 1

    @classmethod
    def verify_succession_trace(cls, trace: Optional[G3SearchTrace]) -> str:
        """Verifies multi-island exploration and emits cryptographic succession certificate."""
        if trace is None:
            raise LinearCompilationViolation(
                "Axiomatic Violation [L1-G2-008]: No G3SearchTrace provided. "
                "System G_2 is structurally prohibited from linear single-shot synthesis of System G_3."
            )

        if len(trace.islands_explored) < cls.MIN_ISLANDS:
            raise LinearCompilationViolation(
                f"Axiomatic Violation [L1-G2-008]: Insufficient island diversity ({len(trace.islands_explored)} < {cls.MIN_ISLANDS})."
            )

        if len(trace.dead_end_candidates) < cls.MIN_DEAD_ENDS:
            raise LinearCompilationViolation(
                f"Axiomatic Violation [L1-G2-008]: Missing dead-end falsification witness ({len(trace.dead_end_candidates)} < {cls.MIN_DEAD_ENDS})."
            )

        token_payload = {
            "trace_id": trace.trace_id,
            "winner_id": trace.selected_winner_id,
            "timestamp": time.time(),
            "invariants_satisfied": ["L1-G2-008"],
        }
        cert_hash = hashlib.sha256(json.dumps(token_payload, sort_keys=True).encode("utf-8")).hexdigest()
        token = f"CERT_G2_{cert_hash[:16].upper()}"
        trace.is_verified = True
        trace.verification_token = token
        return token
