"""Generation 3b Deterministic Fractal Task Stack Engine.

Enforces:
- [L1-G3B-015] Stack Purity & Bounded Recursion Invariant:
  1. The Fractal Task Stack is an explicit, deterministic Python data structure managed
     exclusively by the FSM orchestrator.
  2. Agents never directly invoke other agents. Non-leaf outputs are strictly constrained to a
     schema-validated DecompositionPlan containing discrete subtasks pushed onto the stack.
  3. Enforces an explicit recursion depth limit (d_max) and task branching ceiling (b_max)
     to guarantee termination and prevent infinite stack expansion.
- Thermodynamic Grounding:
  Every TaskNode carries its allocated_token_budget, which is partitioned across child subtasks
  after deducting parent exploratory deliberation tokens.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Any, Optional


class TaskType(str, Enum):
    """Classification of tasks within the Fractal Task Stack."""
    # Non-leaf cognitive tasks (The Brain - Gemini 4 Argon)
    MACRO_SOC_DECONSTRUCTION = "macro_soc_deconstruction"
    DIALECTICAL_ARCH_DECOMPOSITION = "dialectical_arch_decomposition"
    SUBSYSTEM_DECOMPOSITION = "subsystem_decomposition"

    # Indivisible primitive leaf tasks (The Muscle - Gemini 3.8 Flash)
    LEAF_CONTRACT_FRAGMENT = "leaf_contract_fragment"
    LEAF_STATECHART_FRAGMENT = "leaf_statechart_fragment"
    LEAF_TOPOLOGY_FRAGMENT = "leaf_topology_fragment"
    LEAF_CODE_MODULE = "leaf_code_module"


class StackRecursionDepthViolation(Exception):
    """Raised when task decomposition exceeds maximum allowed recursion depth (d_max)."""
    pass


class StackBranchingCeilingViolation(Exception):
    """Raised when a DecompositionPlan exceeds maximum allowed child subtasks (b_max)."""
    pass


class TaskBudgetAllocationViolation(Exception):
    """Raised when child task budget fractions exceed 1.0 or parent capital is depleted."""
    pass


@dataclass
class TaskNode:
    """A discrete unit of work on the Fractal Task Stack carrying thermodynamic capital."""
    task_id: str
    task_type: TaskType
    description: str
    allocated_token_budget: int
    depth: int = 0
    is_leaf: bool = False
    parent_task_id: Optional[str] = None
    tokens_spent: int = 0
    retry_count: int = 0
    max_retries: int = 3
    payload: Dict[str, Any] = field(default_factory=dict)
    remediation_context: Optional[str] = None

    @property
    def remaining_budget(self) -> int:
        return max(0, self.allocated_token_budget - self.tokens_spent)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "task_type": self.task_type.value,
            "description": self.description,
            "allocated_token_budget": self.allocated_token_budget,
            "tokens_spent": self.tokens_spent,
            "remaining_budget": self.remaining_budget,
            "depth": self.depth,
            "is_leaf": self.is_leaf,
            "parent_task_id": self.parent_task_id,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
            "remediation_context": self.remediation_context,
        }


@dataclass
class SubtaskSpec:
    """Specification for a child subtask inside a DecompositionPlan."""
    subtask_id: str
    task_type: TaskType
    description: str
    is_leaf: bool
    budget_fraction: float
    payload: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DecompositionPlan:
    """Schema-validated output of a non-leaf transition function."""
    parent_task_id: str
    rationale: str
    subtasks: List[SubtaskSpec] = field(default_factory=list)

    def validate(self, b_max: int):
        """Validates branching factor and thermodynamic budget partition."""
        if not self.subtasks:
            raise ValueError(f"DecompositionPlan for '{self.parent_task_id}' must contain at least 1 subtask.")
        if len(self.subtasks) > b_max:
            raise StackBranchingCeilingViolation(
                f"[L1-G3B-015 Violation] DecompositionPlan for '{self.parent_task_id}' proposes "
                f"{len(self.subtasks)} subtasks, exceeding branching ceiling b_max={b_max}."
            )
        total_fraction = sum(s.budget_fraction for s in self.subtasks)
        if total_fraction > 1.0 + 1e-6:
            raise TaskBudgetAllocationViolation(
                f"Subtask budget fractions for '{self.parent_task_id}' sum to {total_fraction:.4f} (> 1.0)."
            )
        for s in self.subtasks:
            if s.budget_fraction <= 0.0:
                raise TaskBudgetAllocationViolation(
                    f"Subtask '{s.subtask_id}' must have a strictly positive budget_fraction (got {s.budget_fraction})."
                )


class FractalTaskStack:
    """Explicit, deterministic LIFO task stack enforcing [L1-G3B-015] and capital partitioning."""

    def __init__(self, d_max: int = 5, b_max: int = 8):
        if d_max < 1:
            raise ValueError("d_max must be >= 1")
        if b_max < 1:
            raise ValueError("b_max must be >= 1")
        self.d_max = d_max
        self.b_max = b_max
        self._stack: List[TaskNode] = []
        self.execution_trace: List[Dict[str, Any]] = []

    def is_empty(self) -> bool:
        return len(self._stack) == 0

    def size(self) -> int:
        return len(self._stack)

    def push_root(self, root_node: TaskNode):
        """Pushes the initial root seed task onto the stack at depth 0."""
        if root_node.depth != 0:
            root_node.depth = 0
        if root_node.allocated_token_budget <= 0:
            raise TaskBudgetAllocationViolation("Root task must have a positive allocated_token_budget.")
        self._stack.append(root_node)
        self.execution_trace.append({"event": "PUSH_ROOT", "task_id": root_node.task_id, "depth": 0})

    def pop(self) -> Optional[TaskNode]:
        """Pops the next task node from the top of the stack."""
        if not self._stack:
            return None
        node = self._stack.pop()
        self.execution_trace.append({"event": "POP", "task_id": node.task_id, "depth": node.depth})
        return node

    def push_decomposition(self, parent: TaskNode, plan: DecompositionPlan) -> List[TaskNode]:
        """Validates a DecompositionPlan and pushes child TaskNodes onto the stack.

        Enforces:
        - Next depth <= d_max
        - Subtask count <= b_max
        - Remaining parent thermodynamic budget is partitioned across child tasks.
        """
        next_depth = parent.depth + 1
        if next_depth > self.d_max:
            raise StackRecursionDepthViolation(
                f"[L1-G3B-015 Violation] Task '{parent.task_id}' at depth {parent.depth} attempted "
                f"to decompose to depth {next_depth}, exceeding recursion depth limit d_max={self.d_max}."
            )

        plan.validate(self.b_max)

        available_budget = parent.remaining_budget
        if available_budget <= 0:
            raise TaskBudgetAllocationViolation(
                f"Parent task '{parent.task_id}' has 0 remaining token budget to allocate to children."
            )

        created_children: List[TaskNode] = []
        for spec in plan.subtasks:
            child_budget = max(1, int(available_budget * spec.budget_fraction))
            child_node = TaskNode(
                task_id=spec.subtask_id,
                task_type=spec.task_type,
                description=spec.description,
                allocated_token_budget=child_budget,
                depth=next_depth,
                is_leaf=spec.is_leaf,
                parent_task_id=parent.task_id,
                payload=dict(spec.payload),
            )
            created_children.append(child_node)

        # Push in reverse order so the first subtask in plan.subtasks is popped first (LIFO)
        for child in reversed(created_children):
            self._stack.append(child)
            self.execution_trace.append({
                "event": "PUSH_CHILD",
                "task_id": child.task_id,
                "parent_id": parent.task_id,
                "depth": child.depth,
                "is_leaf": child.is_leaf,
                "allocated_budget": child.allocated_token_budget,
            })

        return created_children

    def push_isolated_retry(self, failed_node: TaskNode, remediation_advice: str) -> TaskNode:
        """Pushes a failed leaf node back onto the stack with Argon remediation context."""
        failed_node.retry_count += 1
        failed_node.remediation_context = remediation_advice
        self._stack.append(failed_node)
        self.execution_trace.append({
            "event": "PUSH_ISOLATED_RETRY",
            "task_id": failed_node.task_id,
            "retry_count": failed_node.retry_count,
            "depth": failed_node.depth,
        })
        return failed_node
