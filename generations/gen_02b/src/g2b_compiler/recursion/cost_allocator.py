"""Thermodynamic Cost Allocator & Capital Partition Manager for System G2b."""

from typing import Any, Dict, Optional
from g2b_compiler.recursion.models import CapitalPartition, WorkerType


class OutOfProtectedCapitalError(Exception):
    """Raised when protected capital is exhausted."""
    pass


class OutOfExploratoryCapitalError(Exception):
    """Raised when exploratory capital is exhausted."""
    pass


class ThermodynamicCostAllocator:
    """Manages token leases, enforcing that exploratory ideation never starves terminal verification."""

    def __init__(self, total_tokens: int = 50000):
        self.capital = CapitalPartition.create(total_tokens)
        self.node_allocations: Dict[str, int] = {}
        self.node_usage: Dict[str, int] = {}
        self.total_used_protected: int = 0
        self.total_used_exploratory: int = 0

    def update_total_budget(self, total_tokens: int):
        """Updates total budget and re-partitions capital into 40% protected and 60% exploratory."""
        self.capital.total_budget = total_tokens
        self.capital.protected_capital = int(total_tokens * 0.40)
        self.capital.exploratory_capital = total_tokens - self.capital.protected_capital

    def lease_tokens(self, node_id: str, worker_type: WorkerType, requested_tokens: int) -> int:
        """Leases tokens from the appropriate capital partition."""
        if worker_type.is_terminal:
            # Must draw from protected capital
            avail = self.capital.protected_capital - self.capital.spent_protected
            if avail < requested_tokens:
                raise OutOfProtectedCapitalError(
                    f"Protected capital insufficient (requested {requested_tokens}, available {avail}/{self.capital.protected_capital}). Cannot execute verification."
                )
            self.capital.spent_protected += requested_tokens
            self.node_allocations[node_id] = self.node_allocations.get(node_id, 0) + requested_tokens
            return requested_tokens
        else:
            # Draw from exploratory capital
            avail = self.capital.exploratory_capital - self.capital.spent_exploratory
            if avail < requested_tokens:
                raise OutOfExploratoryCapitalError(
                    f"Exploratory token capital insufficient (requested {requested_tokens}, available {avail}/{self.capital.exploratory_capital}). Halting speculative branching."
                )
            self.capital.spent_exploratory += requested_tokens
            self.node_allocations[node_id] = self.node_allocations.get(node_id, 0) + requested_tokens
            return requested_tokens

    def record_usage(self, node_id: str, worker_type: WorkerType, tokens_used: int) -> int:
        """Records actual tokens consumed by a node vs its leased allotment."""
        self.node_usage[node_id] = self.node_usage.get(node_id, 0) + tokens_used
        if worker_type.is_terminal:
            self.total_used_protected += tokens_used
        else:
            self.total_used_exploratory += tokens_used
        return tokens_used

    def calculate_decayed_child_budget(self, parent_budget: int, worker_type: WorkerType, decay_rate: float = 0.5) -> int:
        """Applies worker-weight and Landauer decay to child budgets."""
        factor = worker_type.depth_weight * decay_rate
        return max(500, int(parent_budget * factor))

    def reconcile_with_tree(self, root: RecursionNode) -> Dict[str, Any]:
        """Synchronizes capital accounts with the audited recursion tree."""
        from g2b_compiler.recursion.token_meter import TokenMeter
        audit = TokenMeter.audit_recursion_tree(root)
        self.capital.total_budget = root.token_cost
        self.capital.protected_capital = int(root.token_cost * 0.40)
        self.capital.exploratory_capital = root.token_cost - self.capital.protected_capital
        
        self.capital.spent_protected = self.capital.protected_capital
        self.capital.spent_exploratory = self.capital.exploratory_capital
        self.total_used_protected = audit["protected_used"]
        self.total_used_exploratory = audit["exploratory_used"]
        return audit

    def get_summary(self) -> Dict[str, Any]:
        total_budget = self.capital.total_budget
        total_used = self.total_used_protected + self.total_used_exploratory
        total_allotted = self.capital.spent_protected + self.capital.spent_exploratory
        if total_allotted == 0 or total_allotted > total_budget:
            total_allotted = total_budget
        utilization = (total_used / total_allotted * 100.0) if total_allotted > 0 else 0.0
        return {
            "total_budget": total_budget,
            "protected_reserved": self.capital.protected_capital,
            "protected_spent": self.capital.spent_protected,
            "protected_used": self.total_used_protected,
            "protected_available": max(0, self.capital.protected_capital - self.total_used_protected),
            "exploratory_reserved": self.capital.exploratory_capital,
            "exploratory_spent": self.capital.spent_exploratory,
            "exploratory_used": self.total_used_exploratory,
            "exploratory_available": max(0, self.capital.exploratory_capital - self.total_used_exploratory),
            "total_allotted": total_allotted,
            "total_used": total_used,
            "utilization_pct": round(utilization, 1)
        }
