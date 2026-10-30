"""Generation 4b Thermodynamic Capital & Budget Lease Engine (`[L1-G2B-004]`).

Enforces:
- 60% Exploratory Pool / 40% Protected Capital Partition.
- Geometric token decay down the fractal tree with lambda <= 0.80.
- Landauer Cutoff Gate at C_min = 1,024 tokens.
- Landauer heat dissipation accounting Q = k_B * T * ln(2) * bits.
- Hierarchical lease allocation, tracking, and settlement.
"""

from __future__ import annotations

import hashlib
import math
import time
from typing import Dict, List, Optional, Tuple

from .domain_models import (
    DomainInvariantViolation,
    HierarchicalBudgetLease,
    LeaseAllocationStatus,
)


class LandauerCutoffTripped(Exception):
    """Raised when exploratory token budget reaches Landauer cutoff threshold C_min."""
    pass


class BudgetLeaseEngine:
    """Thermodynamic capital manager governing fractal subagent budget leases."""

    LANDAUER_C_MIN: int = 1024  # Minimal Landauer cutoff threshold
    BOLTZMANN_K: float = 1.380649e-23  # J/K
    TEMPERATURE_KELVIN: float = 300.0   # Ambient temperature (300 K)

    def __init__(self, total_budget_tokens: int, decay_lambda: float = 0.80):
        if total_budget_tokens <= 0:
            raise DomainInvariantViolation("total_budget_tokens must be strictly positive.")
        if not (0.0 < decay_lambda <= 0.80):
            raise DomainInvariantViolation(f"decay_lambda must be in (0.0, 0.80], got {decay_lambda}")

        self.total_budget: int = total_budget_tokens
        self.decay_lambda: float = decay_lambda

        # 60/40 Partition
        self.protected_capital: int = int(total_budget_tokens * 0.40)
        self.initial_exploratory_capital: int = total_budget_tokens - self.protected_capital
        self.remaining_exploratory_capital: int = self.initial_exploratory_capital

        # Active leases: lease_id -> HierarchicalBudgetLease
        self._leases: Dict[str, HierarchicalBudgetLease] = {}
        # Cumulative Landauer accounting
        self.total_bits_erased: int = 0

    def allocate_root_lease(self, root_node_id: str, requested_tokens: Optional[int] = None) -> HierarchicalBudgetLease:
        """Allocates the primary root lease from the exploratory pool."""
        max_available = self.remaining_exploratory_capital - self.LANDAUER_C_MIN
        if max_available <= 0:
            raise LandauerCutoffTripped(
                f"Cannot allocate root lease: remaining capital ({self.remaining_exploratory_capital}) "
                f"<= Landauer cutoff C_min ({self.LANDAUER_C_MIN})."
            )
        if requested_tokens is not None and requested_tokens > max_available:
            raise LandauerCutoffTripped(
                f"Requested tokens ({requested_tokens}) exceed available exploratory capital ({max_available}) "
                f"above Landauer cutoff C_min ({self.LANDAUER_C_MIN})."
            )

        tokens = requested_tokens if requested_tokens is not None else max_available
        lease_id = f"lease_root_{hashlib.sha256(root_node_id.encode()).hexdigest()[:8]}"
        lease = HierarchicalBudgetLease(
            lease_id=lease_id,
            node_id=root_node_id,
            parent_lease_id=None,
            allocated_tokens=tokens,
            decay_rate_lambda=self.decay_lambda,
            remaining_tokens=tokens,
            status=LeaseAllocationStatus.ACTIVE,
        )
        lease.validate_invariants()
        self._leases[lease_id] = lease
        self.remaining_exploratory_capital -= tokens
        return lease

    def spawn_child_lease(
        self,
        child_node_id: str,
        parent_lease_id: str,
        branching_factor: int = 1,
    ) -> HierarchicalBudgetLease:
        """Spawns a child lease decayed by lambda and branching factor."""
        parent_lease = self._leases.get(parent_lease_id)
        if not parent_lease:
            raise ValueError(f"Parent lease '{parent_lease_id}' not found.")

        if parent_lease.remaining_tokens <= self.LANDAUER_C_MIN:
            parent_lease.status = LeaseAllocationStatus.EXHAUSTED
            raise LandauerCutoffTripped(
                f"Parent lease remaining tokens ({parent_lease.remaining_tokens}) "
                f"reached Landauer cutoff C_min ({self.LANDAUER_C_MIN})."
            )

        # Decay formula: (parent_remaining / branching_factor) * lambda
        branching = max(1, branching_factor)
        child_allocation = int((parent_lease.remaining_tokens / branching) * self.decay_lambda)
        child_allocation = max(child_allocation, 1)

        # Ensure parent has enough tokens
        if child_allocation > parent_lease.remaining_tokens:
            child_allocation = parent_lease.remaining_tokens

        parent_lease.remaining_tokens -= child_allocation

        lease_id = f"lease_child_{hashlib.sha256((child_node_id + parent_lease_id).encode()).hexdigest()[:8]}"
        child_lease = HierarchicalBudgetLease(
            lease_id=lease_id,
            node_id=child_node_id,
            parent_lease_id=parent_lease_id,
            allocated_tokens=child_allocation,
            decay_rate_lambda=self.decay_lambda,
            remaining_tokens=child_allocation,
            status=LeaseAllocationStatus.ACTIVE,
        )
        child_lease.validate_invariants()
        self._leases[lease_id] = child_lease
        return child_lease

    def spend_tokens(self, lease_id: str, tokens_spent: int) -> int:
        """Deducts tokens from an active lease, enforcing non-negative remaining."""
        lease = self._leases.get(lease_id)
        if not lease:
            raise ValueError(f"Lease '{lease_id}' not found.")

        if lease.remaining_tokens < tokens_spent:
            # Overspend clipped, status set to exhausted
            actual_spent = lease.remaining_tokens
            lease.remaining_tokens = 0
            lease.status = LeaseAllocationStatus.EXHAUSTED
        else:
            actual_spent = tokens_spent
            lease.remaining_tokens -= tokens_spent
            if lease.remaining_tokens <= self.LANDAUER_C_MIN:
                lease.status = LeaseAllocationStatus.EXHAUSTED

        return actual_spent

    def record_bit_erasure(self, bits_erased: int, lease_id: Optional[str] = None) -> float:
        """Records Landauer bit erasure and calculates dissipated heat Q in Joules."""
        if bits_erased < 0:
            raise ValueError("bits_erased cannot be negative.")
        self.total_bits_erased += bits_erased
        if lease_id and lease_id in self._leases:
            self._leases[lease_id].landauer_bits_erased += bits_erased

        # Q = k_B * T * ln(2) * bits
        joules = self.BOLTZMANN_K * self.TEMPERATURE_KELVIN * math.log(2) * bits_erased
        return joules

    def calculate_total_heat_joules(self) -> float:
        """Computes cumulative thermodynamic heat dissipated by all erasures."""
        return self.BOLTZMANN_K * self.TEMPERATURE_KELVIN * math.log(2) * self.total_bits_erased

    def settle_lease(self, lease_id: str) -> int:
        """Settles an active lease, returning unspent tokens back to parent or exploratory pool."""
        lease = self._leases.get(lease_id)
        if not lease:
            return 0

        unspent = lease.remaining_tokens
        lease.remaining_tokens = 0
        lease.status = LeaseAllocationStatus.SETTLED

        if lease.parent_lease_id and lease.parent_lease_id in self._leases:
            self._leases[lease.parent_lease_id].remaining_tokens += unspent
        else:
            self.remaining_exploratory_capital += unspent

        return unspent

    def get_lease(self, lease_id: str) -> Optional[HierarchicalBudgetLease]:
        return self._leases.get(lease_id)
