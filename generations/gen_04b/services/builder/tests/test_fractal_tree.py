"""Adversarial & Structural Boundary Test Suite for Fractal Subagent Tree (`[Layer A]`, `[L1-G3B-015]`).

Validates:
1. Strict Depth Bounds: Rejects recursion depth d > 4 via FractalDepthExceededViolation.
2. Strict Branching Bounds: Rejects branching factor b > 5 via FractalBranchingExceededViolation.
3. Hierarchical Fractional Budget Leasing: Enforces geometric decay lambda <= 0.80.
4. Landauer Cutoff Gate: Trips LandauerCutoffTripped when lease budget falls <= 1,024 tokens.
5. Subtree-Isolated Healing: Quarantines failed branches without unwinding ancestor contexts.
6. Hierarchical Merkle-DAG Witness Hash Propagation.
"""

from __future__ import annotations

from pathlib import Path
import sys
import unittest

BUILDER_ROOT = Path(__file__).resolve().parent.parent
REPO_ROOT = BUILDER_ROOT.parent.parent.parent
for p in [str(BUILDER_ROOT), str(REPO_ROOT)]:
    if p not in sys.path:
        sys.path.insert(0, p)

from src.budget_lease_engine import BudgetLeaseEngine, LandauerCutoffTripped
from src.diagnostic_tuples import DiagnosticEngine
from src.domain_models import (
    DiagnosticSeverity,
    DomainInvariantViolation,
    SubtreeHealingEnvelope,
    TaskExecutionStatus,
)
from src.fractal_orchestrator import (
    BoundedFractalOrchestrator,
    FractalBranchingExceededViolation,
    FractalDepthExceededViolation,
)


class TestFractalTree(unittest.TestCase):
    """Rigorous verification of fractal subagent tree depth, branching, and budget bounds."""

    def setUp(self) -> None:
        # 250,000 total budget -> 150,000 exploratory, 100,000 protected
        self.budget_engine = BudgetLeaseEngine(total_budget_tokens=250000, decay_lambda=0.80)
        self.orchestrator = BoundedFractalOrchestrator(self.budget_engine)

    def test_root_node_initialization(self) -> None:
        root = self.orchestrator.create_root_node(
            task_description="Macro SoC Decomposition",
            assigned_persona="Lead Systems Architect",
            requested_tokens=50000,
        )
        self.assertEqual(root.depth, 0)
        self.assertIsNone(root.parent_id)
        self.assertEqual(root.allocated_lease_tokens, 50000)
        self.assertEqual(root.status, TaskExecutionStatus.ACTIVE)
        self.assertEqual(len(root.merkle_node_hash), 64)

        # Prohibit double root initialization
        with self.assertRaises(DomainInvariantViolation):
            self.orchestrator.create_root_node("Duplicate Root")

    def test_bounded_fractal_depth_limits(self) -> None:
        root = self.orchestrator.create_root_node("Root Task", requested_tokens=100000)
        
        # d = 1
        d1 = self.orchestrator.spawn_child_node(root.node_id, "Depth 1 Subsystem", "Subsystem Lead")
        self.assertEqual(d1.depth, 1)

        # d = 2
        d2 = self.orchestrator.spawn_child_node(d1.node_id, "Depth 2 Module", "Module Lead")
        self.assertEqual(d2.depth, 2)

        # d = 3
        d3 = self.orchestrator.spawn_child_node(d2.node_id, "Depth 3 Leaf", "Synthesizer")
        self.assertEqual(d3.depth, 3)

        # d = 4 (Maximum allowable depth)
        d4 = self.orchestrator.spawn_child_node(d3.node_id, "Depth 4 Micro Leaf", "AST Patcher")
        self.assertEqual(d4.depth, 4)

        # d = 5 (MUST be rejected by FractalDepthExceededViolation)
        with self.assertRaises(FractalDepthExceededViolation):
            self.orchestrator.spawn_child_node(d4.node_id, "Depth 5 Violation", "Illegal Worker")

    def test_bounded_branching_limits(self) -> None:
        root = self.orchestrator.create_root_node("Branching Test Root", requested_tokens=120000)

        # Spawn maximum allowable 5 child branches
        children = []
        for i in range(5):
            c = self.orchestrator.spawn_child_node(
                root.node_id,
                f"Child Branch {i + 1}",
                "Branch Worker",
            )
            children.append(c)

        self.assertEqual(len(root.child_ids), 5)

        # 6th child MUST raise FractalBranchingExceededViolation
        with self.assertRaises(FractalBranchingExceededViolation):
            self.orchestrator.spawn_child_node(root.node_id, "Branch 6 Violation", "Illegal Worker")

    def test_hierarchical_budget_leasing_decay(self) -> None:
        root = self.orchestrator.create_root_node("Root Lease Test", requested_tokens=80000)
        
        # Spawn child 1
        child_1 = self.orchestrator.spawn_child_node(root.node_id, "Child 1", "Synthesizer")
        
        # Child allocation must decay by lambda <= 0.80
        # child_tokens <= 80,000 * 0.80 = 64,000
        self.assertLessEqual(child_1.allocated_lease_tokens, int(80000 * 0.80))
        self.assertGreaterEqual(child_1.allocated_lease_tokens, 1024)

    def test_landauer_cutoff_gate_tripped(self) -> None:
        # Engine with budget where child 1 leaves parent remaining tokens < 1024
        calibrated_engine = BudgetLeaseEngine(total_budget_tokens=10000, decay_lambda=0.80)
        calibrated_orch = BoundedFractalOrchestrator(calibrated_engine)

        root = calibrated_orch.create_root_node("Calibrated Root", requested_tokens=2000)
        
        # Child 1 allocates 1600 tokens, leaving 400 tokens in parent lease (< 1024)
        calibrated_orch.spawn_child_node(root.node_id, "Child 1", "Worker")

        # Spawning child 2 when parent remaining tokens < 1024 trips LandauerCutoffTripped
        with self.assertRaises(LandauerCutoffTripped):
            calibrated_orch.spawn_child_node(root.node_id, "Child 2 Exhausted", "Worker")

    def test_subtree_healing_quarantine(self) -> None:
        root = self.orchestrator.create_root_node("Healing Test Root", requested_tokens=80000)
        parent = self.orchestrator.spawn_child_node(root.node_id, "Parent Node", "Subsystem Lead")
        child_a = self.orchestrator.spawn_child_node(parent.node_id, "Child A", "Worker A")
        child_b = self.orchestrator.spawn_child_node(parent.node_id, "Child B", "Worker B")

        # Failure occurs on parent node
        diag = DiagnosticEngine.create_diagnostic(
            file_path="src/engine.py",
            severity=DiagnosticSeverity.ERROR,
            rule_code="INVARIANT_BREACH",
            message="State invariant failure in parent",
            source_code="class Engine: pass",
            line=1,
            col=0,
        )

        envelope = self.orchestrator.heal_subtree(
            failing_node_id=parent.node_id,
            diagnostic=diag,
            healing_strategy="ISOLATE_AND_PATCH",
            reserved_healing_tokens=4096,
        )

        self.assertIsInstance(envelope, SubtreeHealingEnvelope)
        self.assertEqual(parent.status, TaskExecutionStatus.HEALING)
        self.assertEqual(child_a.status, TaskExecutionStatus.CANCELLED)
        self.assertEqual(child_b.status, TaskExecutionStatus.CANCELLED)
        self.assertIn(child_a.node_id, envelope.quarantined_child_ids)
        self.assertIn(child_b.node_id, envelope.quarantined_child_ids)

    def test_merkle_dag_propagation_on_execution(self) -> None:
        root = self.orchestrator.create_root_node("Merkle Test Root", requested_tokens=60000)
        initial_root_hash = root.merkle_node_hash

        child = self.orchestrator.spawn_child_node(root.node_id, "Child Execution", "Synthesizer")
        
        # Recording execution on child must update child and root hashes
        self.orchestrator.record_node_execution(
            node_id=child.node_id,
            tokens_spent=5000,
            emitted_artifacts=["src/synthesized_leaf.py"],
            success=True,
        )

        self.assertEqual(child.status, TaskExecutionStatus.COMPLETED)
        self.assertNotEqual(root.merkle_node_hash, initial_root_hash)


if __name__ == "__main__":
    unittest.main()
