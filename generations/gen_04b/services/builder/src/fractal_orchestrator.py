"""Generation 4b Bounded Fractal Subagent Tree Orchestrator (`[Layer A]`, `[L1-G3B-015]`).

Enforces:
- Strict bounds: Depth d <= 4, Branching factor b <= 5.
- Hierarchical budget leasing with geometric decay lambda <= 0.80.
- Subtree failure isolation and healing via SubtreeHealingEnvelope.
- Cryptographic Merkle-DAG node hash aggregation.
"""

from __future__ import annotations

import hashlib
import time
from typing import Dict, List, Optional, Set, Tuple

from .budget_lease_engine import BudgetLeaseEngine, LandauerCutoffTripped
from .diagnostic_tuples import DiagnosticEngine
from .domain_models import (
    DiagnosticSeverity,
    DiagnosticTuple,
    DomainInvariantViolation,
    FractalTreeNode,
    SubtreeHealingEnvelope,
    TaskExecutionStatus,
)


class FractalDepthExceededViolation(DomainInvariantViolation):
    """Raised when attempting to spawn a subagent node beyond max depth d=4."""
    pass


class FractalBranchingExceededViolation(DomainInvariantViolation):
    """Raised when a fractal parent exceeds max branching factor b=5."""
    pass


class BoundedFractalOrchestrator:
    """Orchestrates bounded fractal subagent trees with strict depth, branching, and budget limits."""

    MAX_DEPTH: int = 4
    MAX_BRANCHING: int = 5

    def __init__(self, budget_engine: BudgetLeaseEngine):
        self.budget_engine = budget_engine
        # Node storage: node_id -> FractalTreeNode
        self._nodes: Dict[str, FractalTreeNode] = {}
        # Node to lease mapping: node_id -> lease_id
        self._node_leases: Dict[str, str] = {}
        # Root node ID
        self.root_node_id: Optional[str] = None
        # Healing envelopes: envelope_id -> SubtreeHealingEnvelope
        self._healing_envelopes: Dict[str, SubtreeHealingEnvelope] = {}

    def create_root_node(
        self,
        task_description: str,
        assigned_persona: str = "Lead Systems Architect",
        requested_tokens: Optional[int] = None,
    ) -> FractalTreeNode:
        """Initializes the depth-0 root node of the fractal execution tree."""
        if self.root_node_id is not None:
            raise DomainInvariantViolation("Root node already initialized in this orchestrator instance.")

        node_id = f"node_root_{hashlib.sha256(task_description.encode()).hexdigest()[:8]}"
        lease = self.budget_engine.allocate_root_lease(node_id, requested_tokens)

        root = FractalTreeNode(
            node_id=node_id,
            parent_id=None,
            depth=0,
            assigned_persona_role=assigned_persona,
            task_description=task_description,
            allocated_lease_tokens=lease.allocated_tokens,
            status=TaskExecutionStatus.ACTIVE,
        )
        root.merkle_node_hash = root.compute_merkle_hash()
        root.validate_invariants()

        self.root_node_id = node_id
        self._nodes[node_id] = root
        self._node_leases[node_id] = lease.lease_id
        return root

    def spawn_child_node(
        self,
        parent_node_id: str,
        task_description: str,
        assigned_persona: str,
    ) -> FractalTreeNode:
        """Spawns a child node, enforcing depth d <= 4 and branching b <= 5 bounds."""
        parent = self._nodes.get(parent_node_id)
        if not parent:
            raise ValueError(f"Parent node '{parent_node_id}' does not exist.")

        # Depth bound: d <= 4
        new_depth = parent.depth + 1
        if new_depth > self.MAX_DEPTH:
            raise FractalDepthExceededViolation(
                f"[Fractal Depth Violation] Attempted depth {new_depth} exceeds maximum allowable depth {self.MAX_DEPTH}."
            )

        # Branching bound: b <= 5
        if len(parent.child_ids) >= self.MAX_BRANCHING:
            raise FractalBranchingExceededViolation(
                f"[Fractal Branching Violation] Parent {parent_node_id} already has {len(parent.child_ids)} children "
                f"(max {self.MAX_BRANCHING})."
            )

        parent_lease_id = self._node_leases[parent_node_id]
        child_node_id = f"node_d{new_depth}_{hashlib.sha256((parent_node_id + task_description).encode()).hexdigest()[:8]}"

        # Allocate child lease decayed by lambda and branching factor
        child_lease = self.budget_engine.spawn_child_lease(
            child_node_id=child_node_id,
            parent_lease_id=parent_lease_id,
            branching_factor=max(1, len(parent.child_ids) + 1),
        )

        child = FractalTreeNode(
            node_id=child_node_id,
            parent_id=parent_node_id,
            depth=new_depth,
            assigned_persona_role=assigned_persona,
            task_description=task_description,
            allocated_lease_tokens=child_lease.allocated_tokens,
            status=TaskExecutionStatus.ACTIVE,
        )
        child.merkle_node_hash = child.compute_merkle_hash()
        child.validate_invariants()

        self._nodes[child_node_id] = child
        self._node_leases[child_node_id] = child_lease.lease_id
        parent.child_ids.append(child_node_id)
        parent.merkle_node_hash = parent.compute_merkle_hash()

        return child

    def record_node_execution(
        self,
        node_id: str,
        tokens_spent: int,
        emitted_artifacts: Optional[List[str]] = None,
        success: bool = True,
    ) -> None:
        """Records task execution result, updates token spend, and settles lease."""
        node = self._nodes.get(node_id)
        if not node:
            raise ValueError(f"Node '{node_id}' not found.")

        lease_id = self._node_leases[node_id]
        actual_spent = self.budget_engine.spend_tokens(lease_id, tokens_spent)
        node.spent_tokens += actual_spent

        if emitted_artifacts:
            node.emitted_artifacts.extend(emitted_artifacts)

        node.status = TaskExecutionStatus.COMPLETED if success else TaskExecutionStatus.FAILED
        node.merkle_node_hash = node.compute_merkle_hash()

        # Update parent hash hierarchically
        self._propagate_merkle_update(node_id)

    def heal_subtree(
        self,
        failing_node_id: str,
        diagnostic: DiagnosticTuple,
        healing_strategy: str = "ISOLATE_AND_PATCH",
        reserved_healing_tokens: int = 2048,
    ) -> SubtreeHealingEnvelope:
        """Isolates a failed branch, quarantines its descendants, and applies healing."""
        node = self._nodes.get(failing_node_id)
        if not node:
            raise ValueError(f"Failing node '{failing_node_id}' not found.")

        # Quarantine all child IDs
        quarantined = list(node.child_ids)
        for child_id in quarantined:
            if child_id in self._nodes:
                self._nodes[child_id].status = TaskExecutionStatus.CANCELLED

        envelope_id = f"env_{hashlib.sha256((failing_node_id + diagnostic.diagnostic_id).encode()).hexdigest()[:10]}"
        envelope = SubtreeHealingEnvelope(
            envelope_id=envelope_id,
            failing_node_id=failing_node_id,
            root_cause_diagnostic=diagnostic,
            healing_strategy=healing_strategy,
            quarantined_child_ids=quarantined,
            reserved_healing_tokens=reserved_healing_tokens,
            resolved=False,
        )
        envelope.validate_invariants()
        self._healing_envelopes[envelope_id] = envelope

        # Transition failing node to HEALING
        node.status = TaskExecutionStatus.HEALING
        node.merkle_node_hash = node.compute_merkle_hash()

        return envelope

    def resolve_healing(self, envelope_id: str) -> None:
        """Marks healing envelope resolved and returns repaired node to ACTIVE or COMPLETED."""
        env = self._healing_envelopes.get(envelope_id)
        if not env:
            raise ValueError(f"Healing envelope '{envelope_id}' not found.")
        env.resolved = True
        node = self._nodes.get(env.failing_node_id)
        if node:
            node.status = TaskExecutionStatus.COMPLETED
            node.merkle_node_hash = node.compute_merkle_hash()
            self._propagate_merkle_update(node.node_id)

    def _propagate_merkle_update(self, node_id: str) -> None:
        """Recalculates Merkle hashes up to the tree root."""
        curr = self._nodes.get(node_id)
        while curr and curr.parent_id:
            parent = self._nodes.get(curr.parent_id)
            if parent:
                parent.merkle_node_hash = parent.compute_merkle_hash()
                curr = parent
            else:
                break

    def get_root_merkle_hash(self) -> str:
        """Returns the Merkle root hash of the entire fractal tree."""
        if not self.root_node_id or self.root_node_id not in self._nodes:
            return hashlib.sha256(b"EMPTY_TREE").hexdigest()
        return self._nodes[self.root_node_id].merkle_node_hash

    def get_all_nodes(self) -> List[FractalTreeNode]:
        return list(self._nodes.values())

    def get_node(self, node_id: str) -> Optional[FractalTreeNode]:
        return self._nodes.get(node_id)
