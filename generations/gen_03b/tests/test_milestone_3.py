"""Milestone 3 Verification Suite: The Semantic Crucible.

Verifies on the live Python 3.14 substrate:
1. [L1-G3B-015] Stack Purity & Bounded Recursion Invariant (d_max, b_max, LIFO order, capital partitioning).
2. [L1-G3B-014] Stateless Subagent Transition Functions (Argon Brain vs. Flash Muscle).
3. [L1-G3B-016] Zero-Bypass Interception Invariant:
   - Clean E2E synthesis of ContractIR, StatechartIR, TopologyIR, and Code Module from a seed pitch.
   - Fault injection & isolated self-healing remediation loop with Landauer bit-erasure accounting.
   - Persistent defect circuit breaker tripping (LeafRemediationCircuitBreakerError) with exponential backoff.
   - Direct un-audited commit rejection (ZeroBypassInterceptionViolation).
4. Thermodynamic Grounding: Exact token separation between Argon deliberation, Flash emission, and Argon verification sinks.
"""

import sys
import unittest
from pathlib import Path

# Add src to sys.path
SRC_DIR = Path(__file__).resolve().parent.parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from g3b_compiler.soc import PitchInput
from g3b_compiler.evaluators import LeafArtifact, MicroAuditResult
from g3b_compiler.crucible import (
    TaskType,
    TaskNode,
    SubtaskSpec,
    DecompositionPlan,
    FractalTaskStack,
    StackRecursionDepthViolation,
    StackBranchingCeilingViolation,
    TaskBudgetAllocationViolation,
    ResearcherSubagent,
    DialecticalArchitectSubagent,
    LeafSynthesizerSubagent,
    CrucibleOrchestrator,
    LeafRemediationCircuitBreakerError,
    ZeroBypassInterceptionViolation,
)


class TestFractalTaskStackPurityAndBounds(unittest.TestCase):
    """Verifies [L1-G3B-015] Stack Purity, d_max, b_max, and thermodynamic capital partitioning."""

    def test_lifo_ordering_and_budget_partitioning(self):
        stack = FractalTaskStack(d_max=4, b_max=5)
        root = TaskNode(
            task_id="root",
            task_type=TaskType.MACRO_SOC_DECONSTRUCTION,
            description="Root task",
            allocated_token_budget=10000,
            depth=0,
            tokens_spent=2000,  # 8,000 remaining
        )
        stack.push_root(root)
        popped_root = stack.pop()
        self.assertEqual(popped_root.task_id, "root")
        self.assertEqual(popped_root.remaining_budget, 8000)

        plan = DecompositionPlan(
            parent_task_id="root",
            rationale="Split into 2 subtasks",
            subtasks=[
                SubtaskSpec("child_1", TaskType.LEAF_CONTRACT_FRAGMENT, "First", True, 0.60),
                SubtaskSpec("child_2", TaskType.LEAF_STATECHART_FRAGMENT, "Second", True, 0.40),
            ],
        )
        children = stack.push_decomposition(popped_root, plan)
        self.assertEqual(len(children), 2)
        self.assertEqual(children[0].allocated_token_budget, 4800)  # 60% of 8,000
        self.assertEqual(children[1].allocated_token_budget, 3200)  # 40% of 8,000

        # Verify child_1 is popped first (LIFO preservation of subtask order)
        first_pop = stack.pop()
        second_pop = stack.pop()
        self.assertEqual(first_pop.task_id, "child_1")
        self.assertEqual(second_pop.task_id, "child_2")
        self.assertEqual(first_pop.depth, 1)

    def test_trap_recursion_depth_violation(self):
        """[L1-G3B-015]: Exceeding d_max raises StackRecursionDepthViolation."""
        stack = FractalTaskStack(d_max=2, b_max=5)
        deep_node = TaskNode(
            task_id="node_at_limit",
            task_type=TaskType.SUBSYSTEM_DECOMPOSITION,
            description="Already at depth 2",
            allocated_token_budget=5000,
            depth=2,
        )
        plan = DecompositionPlan(
            parent_task_id="node_at_limit",
            rationale="Attempt depth 3",
            subtasks=[SubtaskSpec("too_deep", TaskType.LEAF_CODE_MODULE, "Leaf", True, 1.0)],
        )
        with self.assertRaises(StackRecursionDepthViolation):
            stack.push_decomposition(deep_node, plan)

    def test_trap_branching_ceiling_violation(self):
        """[L1-G3B-015]: Exceeding b_max raises StackBranchingCeilingViolation."""
        stack = FractalTaskStack(d_max=5, b_max=3)
        parent = TaskNode(
            task_id="parent",
            task_type=TaskType.DIALECTICAL_ARCH_DECOMPOSITION,
            description="Parent",
            allocated_token_budget=10000,
            depth=1,
        )
        # Propose 4 subtasks when b_max is 3
        plan = DecompositionPlan(
            parent_task_id="parent",
            rationale="Too many branches",
            subtasks=[
                SubtaskSpec(f"sub_{i}", TaskType.LEAF_CODE_MODULE, "Leaf", True, 0.20)
                for i in range(4)
            ],
        )
        with self.assertRaises(StackBranchingCeilingViolation):
            stack.push_decomposition(parent, plan)

    def test_trap_budget_fraction_over_unity(self):
        """Proposing subtask budget fractions summing > 1.0 raises TaskBudgetAllocationViolation."""
        stack = FractalTaskStack(d_max=5, b_max=5)
        parent = TaskNode("p", TaskType.MACRO_SOC_DECONSTRUCTION, "P", 1000, depth=0)
        plan = DecompositionPlan(
            parent_task_id="p",
            rationale="Over-allocated",
            subtasks=[
                SubtaskSpec("s1", TaskType.LEAF_CODE_MODULE, "L1", True, 0.70),
                SubtaskSpec("s2", TaskType.LEAF_CODE_MODULE, "L2", True, 0.50),  # 0.7 + 0.5 = 1.2 > 1.0!
            ],
        )
        with self.assertRaises(TaskBudgetAllocationViolation):
            stack.push_decomposition(parent, plan)


class TestSemanticCrucibleOrchestrator(unittest.TestCase):
    """Verifies closed-loop synthesis, [L1-G3B-016] zero-bypass interception, and self-healing."""

    def test_clean_end_to_end_crucible_synthesis(self):
        """Proves full decomposition from Tier 2 Pitch to verified Contract, Statechart, Topology, and Code."""
        pitch = PitchInput(
            title="Distributed Telemetry Mesh",
            elevator_pitch="A local-first telemetry collector for clinical sensors.",
            target_audience="Biomedical Engineers",
            intended_features=["Sensor packet ingestion", "Instant rollback"],
        )
        orchestrator = CrucibleOrchestrator(total_budget=600000, d_max=5, b_max=8)
        result = orchestrator.run_crucible(
            seed_input=pitch,
            soc_id="soc_telemetry_mesh",
            is_multi_node_cluster=True,
            required_invariants=["balance >= 0"],
            inject_fault_on_first_try=False,
        )

        # Verify certified SoC
        self.assertEqual(result.certified_soc.soc_id, "soc_telemetry_mesh")

        # Verify all 4 leaf artifacts were emitted and audited
        self.assertEqual(len(result.verified_leaves), 4)
        self.assertEqual(len(result.audit_certificates), 4)
        for cert in result.audit_certificates.values():
            self.assertTrue(cert.is_passed)

        # Verify parsed and validated IR models
        self.assertIsNotNone(result.verified_contract)
        self.assertIsNotNone(result.verified_statechart)
        self.assertIsNotNone(result.verified_topology)
        self.assertEqual(len(result.verified_code_modules), 1)
        self.assertEqual(len(result.remediation_events), 0)

        # Verify thermodynamic token separation
        self.assertGreater(result.argon_deliberation_tokens, 0)
        self.assertGreater(result.flash_emission_tokens, 0)
        self.assertGreater(result.argon_verification_tokens, 0)

    def test_fault_injection_and_isolated_self_healing_remediation(self):
        """Proves [L1-G3B-016]: Micro-auditors trap leaf flaws and trigger isolated Argon-governed Flash retries."""
        pitch = PitchInput(
            title="Fault-Tolerant Ledger",
            elevator_pitch="Multi-node consensus ledger with strict balance invariants.",
            target_audience="Systems Architects",
            intended_features=["Quorum sync", "Zero-negative balance"],
        )
        orchestrator = CrucibleOrchestrator(total_budget=600000, d_max=5, b_max=8, max_leaf_retries=3)
        result = orchestrator.run_crucible(
            seed_input=pitch,
            soc_id="soc_healing_ledger",
            is_multi_node_cluster=True,
            required_invariants=["balance >= 0"],
            inject_fault_on_first_try=True,  # Injects loopback in topology & eval() + missing invariant in code!
        )

        # 2 leaf nodes failed on attempt 0 (leaf_topology and leaf_code) and healed on attempt 1!
        self.assertEqual(len(result.remediation_events), 2)
        for ev in result.remediation_events:
            self.assertEqual(ev["attempt"], 1)
            self.assertEqual(ev["backoff_delay_ms"], 100)
            self.assertGreater(ev["bits_erased"], 0)

        # Verify Landauer bit-erasure dissipation was recorded on the ledger
        self.assertGreater(result.thermodynamic_summary["bits_erased"], 0)
        self.assertGreater(result.thermodynamic_summary["dissipated_joules"], 0.0)

        # Verify all 4 leaves ultimately passed after isolated remediation!
        self.assertEqual(len(result.verified_leaves), 4)
        code_content = list(result.verified_code_modules.values())[0]
        self.assertNotIn("eval(", code_content)
        self.assertIn("assert balance >= 0", code_content)
        print(
            f"\n[SELF-HEALING CRUCIBLE CERTIFIED]: Trapped {len(result.remediation_events)} leaf defects, "
            f"erased {result.thermodynamic_summary['bits_erased']} bits, and converged to 100% verified IR!"
        )

    def test_circuit_breaker_trips_on_persistent_poison_leaf(self):
        """Proves [L1-G3B-016]: Persistent leaf failure trips LeafRemediationCircuitBreakerError after max_retries."""
        pitch = PitchInput(
            title="Unhealable Target",
            elevator_pitch="Test circuit breaker.",
            target_audience="Testers",
            intended_features=["Test"],
        )
        orchestrator = CrucibleOrchestrator(total_budget=600000, d_max=5, b_max=8, max_leaf_retries=2)

        # Custom generator that persistently emits unsafe eval() regardless of retry count
        def persistent_poison_generator(node: TaskNode) -> str:
            return "def poisoned(): return eval('os.system()')"

        with self.assertRaises(LeafRemediationCircuitBreakerError) as ctx:
            orchestrator.run_crucible(
                seed_input=pitch,
                soc_id="soc_breaker",
                custom_leaf_generator=persistent_poison_generator,
            )

        self.assertIn("Circuit Breaker Tripped", str(ctx.exception))

    def test_zero_bypass_direct_commit_rejection(self):
        """Proves [L1-G3B-016]: Attempting to commit an un-audited leaf raises ZeroBypassInterceptionViolation."""
        leaf = LeafArtifact(task_id="leaf_1", artifact_type="code", content="x = 1")
        failed_audit = MicroAuditResult(task_id="leaf_1", is_passed=False, defects=["Failed"])

        with self.assertRaises(ZeroBypassInterceptionViolation):
            CrucibleOrchestrator._commit_verified_leaf(
                leaf_artifact=leaf,
                audit_result=failed_audit,
                verified_leaves={},
                audit_certificates={},
            )


if __name__ == "__main__":
    unittest.main()
