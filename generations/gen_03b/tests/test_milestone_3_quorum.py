"""Milestone 3 Substrate Verification Suite: Adversarial Quorum Consensus Gate.

Verifies on the live Python 3.14 substrate:
1. Strict Pydantic v2 Schema validation for QuorumVerdict & QuorumConsensusResult.
2. ProductManagerAuditor traps unbudgeted feature-rich hallucinations (e.g., '8-voice networked WebSocket mesh').
3. ArchitectAuditor traps system invariant violations ([L1-G3B-017] bypassed Quine isolation, [L1-G3B-012] loopback leaks).
4. QAVerificationAuditor traps features and state transitions lacking mathematically testable invariants.
5. DialecticalArchitectSubagent synthesizes targeted Delta Updates resolving only specific violations under Argon governance.
6. End-to-end FSM Orchestrator Resolution Gate:
   - Injects mock proposal with '8-voice networked WebSocket mesh' and 'bypassed Quine isolation'.
   - Proves ProductManagerAuditor and ArchitectAuditor return approved=False with actionable violation strings.
   - Proves the FSM blocks progression, routes violations back to DialecticalArchitect, loops, and reaches
     unanimous consensus on iteration 2 before proceeding to clean IR synthesis.
7. QuorumConsensusDeadlockError trips when violations persist across max_iterations.
"""

import sys
import unittest
from pathlib import Path

# Add src to sys.path
SRC_DIR = Path(__file__).resolve().parent.parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from g3b_compiler.soc import PitchInput, SituationOfConcern
from g3b_compiler.crucible import (
    TaskType,
    TaskNode,
    SubtaskSpec,
    DecompositionPlan,
    CrucibleOrchestrator,
    QuorumVerdict,
    QuorumConsensusResult,
    QuorumConsensusDeadlockError,
    ProductManagerAuditor,
    ArchitectAuditor,
    QAVerificationAuditor,
    DialecticalArchitectSubagent,
)


class TestAdversarialQuorumGate(unittest.TestCase):
    """End-to-end substrate verification of the Adversarial Quorum Consensus Gate."""

    def test_schema_validation_quorum_verdict(self):
        """1. Schema Definitions: Verifies strict Pydantic consistency in QuorumVerdict."""
        # Clean approval: must have empty blocking_violations
        clean_verdict = QuorumVerdict(
            role_id="PRODUCT_MANAGER",
            approved=True,
            blocking_violations=[],
        )
        self.assertTrue(clean_verdict.approved)
        self.assertEqual(len(clean_verdict.blocking_violations), 0)

        # Illegal: approved=True with non-empty blocking_violations must raise ValueError
        with self.assertRaises(ValueError):
            QuorumVerdict(
                role_id="PRODUCT_MANAGER",
                approved=True,
                blocking_violations=["Contradiction: Approved but has violations!"],
            )

        # Illegal: approved=False with empty blocking_violations must raise ValueError
        with self.assertRaises(ValueError):
            QuorumVerdict(
                role_id="PRODUCT_MANAGER",
                approved=False,
                blocking_violations=[],
            )

        # Clean rejection: approved=False with specific violations
        rejection_verdict = QuorumVerdict(
            role_id="SYSTEMS_ARCHITECT",
            approved=False,
            blocking_violations=["[L1-G3B-017] Bypassed Quine isolation"],
        )
        self.assertFalse(rejection_verdict.approved)
        self.assertEqual(len(rejection_verdict.blocking_violations), 1)

    def test_product_manager_auditor_traps_hallucinations(self):
        """2. ProductManagerAuditor: Relentlessly enforces scope boundaries and rejects unbudgeted hallucinations."""
        node = TaskNode(
            task_id="task_pm_test",
            task_type=TaskType.DIALECTICAL_ARCH_DECOMPOSITION,
            description="Dialectical arch decomposition",
            allocated_token_budget=10000,
            depth=1,
            payload={
                "soc": {
                    "soc_id": "soc_simple_sensor",
                    "title": "Simple Sensor Monitor",
                    "problem_statement": "Monitor pipeline temperature.",
                    "unmet_needs": ["Temperature threshold alerts"],
                    "frictions": [],
                }
            },
        )

        # Injected hallucination: '8-voice networked WebSocket mesh' not fundamentally required by Tier 1 SoC
        flawed_plan = DecompositionPlan(
            parent_task_id=node.task_id,
            rationale="Proposed architecture incorporating an unbudgeted 8-voice networked WebSocket mesh.",
            subtasks=[
                SubtaskSpec(
                    subtask_id=f"{node.task_id}.leaf_mesh",
                    task_type=TaskType.LEAF_CODE_MODULE,
                    description="Synthesize unbudgeted 8-voice networked WebSocket mesh and audio engine",
                    is_leaf=True,
                    budget_fraction=0.40,
                    payload={"feature": "8-voice networked WebSocket mesh", "unbudgeted": True},
                ),
                SubtaskSpec(
                    subtask_id=f"{node.task_id}.leaf_core",
                    task_type=TaskType.LEAF_CONTRACT_FRAGMENT,
                    description="Standard contract",
                    is_leaf=True,
                    budget_fraction=0.60,
                ),
            ],
        )

        verdict, tokens = ProductManagerAuditor.audit(node, flawed_plan)
        self.assertFalse(verdict.approved)
        self.assertGreater(tokens, 0)
        self.assertTrue(
            any("8-voice" in v or "websocket mesh" in v or "Unbudgeted" in v for v in verdict.blocking_violations),
            f"Expected violation not found in: {verdict.blocking_violations}",
        )

        # Clean proposal: approved=True
        clean_plan = DecompositionPlan(
            parent_task_id=node.task_id,
            rationale="Clean architecture for pipeline temperature monitoring.",
            subtasks=[
                SubtaskSpec(
                    subtask_id=f"{node.task_id}.leaf_core",
                    task_type=TaskType.LEAF_CONTRACT_FRAGMENT,
                    description="Standard contract",
                    is_leaf=True,
                    budget_fraction=1.00,
                )
            ],
        )
        clean_verdict, _ = ProductManagerAuditor.audit(node, clean_plan)
        self.assertTrue(clean_verdict.approved)
        self.assertEqual(len(clean_verdict.blocking_violations), 0)

    def test_architect_auditor_traps_isolation_bypass(self):
        """3. ArchitectAuditor: Enforces [L1-G3B-017] Quine Protocol and [L1-G3B-012] Topological Fidelity."""
        node = TaskNode(
            task_id="task_arch_test",
            task_type=TaskType.DIALECTICAL_ARCH_DECOMPOSITION,
            description="Dialectical arch decomposition",
            allocated_token_budget=10000,
            depth=1,
            payload={"is_multi_node_cluster": True},
        )

        # Injected violation: 'bypassed Quine isolation' and loopback binding
        flawed_plan = DecompositionPlan(
            parent_task_id=node.task_id,
            rationale="Proposed architecture with bypassed Quine isolation for direct execution.",
            subtasks=[
                SubtaskSpec(
                    subtask_id=f"{node.task_id}.leaf_topo",
                    task_type=TaskType.LEAF_TOPOLOGY_FRAGMENT,
                    description="Distributed topology bound to 127.0.0.1",
                    is_leaf=True,
                    budget_fraction=0.50,
                    payload={"host": "127.0.0.1", "bypass_quine_isolation": True},
                ),
                SubtaskSpec(
                    subtask_id=f"{node.task_id}.leaf_code",
                    task_type=TaskType.LEAF_CODE_MODULE,
                    description="Core module with bypassed Quine isolation",
                    is_leaf=True,
                    budget_fraction=0.50,
                ),
            ],
        )

        verdict, tokens = ArchitectAuditor.audit(node, flawed_plan)
        self.assertFalse(verdict.approved)
        self.assertGreater(tokens, 0)
        violations_str = " ".join(verdict.blocking_violations)
        self.assertIn("L1-G3B-017", violations_str)
        self.assertIn("bypassed quine isolation", violations_str.lower())
        self.assertIn("L1-G3B-012", violations_str)

    def test_qa_verification_auditor_traps_untestable_features(self):
        """4. QAVerificationAuditor: Rejects proposed features or transitions lacking testable invariants."""
        node = TaskNode(
            task_id="task_qa_test",
            task_type=TaskType.DIALECTICAL_ARCH_DECOMPOSITION,
            description="Dialectical arch decomposition",
            allocated_token_budget=10000,
            depth=1,
            payload={"required_invariants": ["temperature <= 100"]},
        )

        flawed_plan = DecompositionPlan(
            parent_task_id=node.task_id,
            rationale="Architecture with untestable heuristic optimization step.",
            subtasks=[
                SubtaskSpec(
                    subtask_id=f"{node.task_id}.leaf_untestable",
                    task_type=TaskType.LEAF_CODE_MODULE,
                    description="Synthesize untestable heuristic optimization",
                    is_leaf=True,
                    budget_fraction=1.00,
                    payload={"has_testable_invariant": False, "untestable": True},
                )
            ],
        )

        verdict, tokens = QAVerificationAuditor.audit(node, flawed_plan)
        self.assertFalse(verdict.approved)
        self.assertGreater(tokens, 0)
        self.assertTrue(any("testable invariant" in v for v in verdict.blocking_violations))

    def test_dialectical_architect_synthesizes_delta_update(self):
        """5. DialecticalArchitectSubagent: Synthesizes a Delta Update resolving only specific Quorum violations."""
        node = TaskNode(
            task_id="task_delta_test",
            task_type=TaskType.DIALECTICAL_ARCH_DECOMPOSITION,
            description="Dialectical arch decomposition",
            allocated_token_budget=10000,
            depth=1,
            payload={"soc": {"soc_id": "soc_clean_target"}},
        )

        flawed_plan = DecompositionPlan(
            parent_task_id=node.task_id,
            rationale="Draft containing unbudgeted 8-voice networked WebSocket mesh and bypassed Quine isolation.",
            subtasks=[
                SubtaskSpec(
                    subtask_id=f"{node.task_id}.leaf_contract",
                    task_type=TaskType.LEAF_CONTRACT_FRAGMENT,
                    description="Standard Contract",
                    is_leaf=True,
                    budget_fraction=0.40,
                ),
                SubtaskSpec(
                    subtask_id=f"{node.task_id}.leaf_mesh_hallucination",
                    task_type=TaskType.LEAF_CODE_MODULE,
                    description="Synthesize unbudgeted 8-voice networked WebSocket mesh with bypassed Quine isolation",
                    is_leaf=True,
                    budget_fraction=0.20,
                    payload={"feature": "8-voice networked WebSocket mesh", "bypass_quine_isolation": True, "unbudgeted": True},
                ),
                SubtaskSpec(
                    subtask_id=f"{node.task_id}.leaf_code",
                    task_type=TaskType.LEAF_CODE_MODULE,
                    description="Core domain module with bypassed Quine isolation",
                    is_leaf=True,
                    budget_fraction=0.40,
                ),
            ],
        )

        violations = [
            "[Scope Creep Violation] Unbudgeted feature-rich hallucination detected: '8-voice networked WebSocket mesh'.",
            "[L1-G3B-017 Quine Protocol Violation] Spec attempts to bypass Quine isolation boundaries: 'bypassed Quine isolation'.",
        ]

        purified_plan, delta_tokens = DialecticalArchitectSubagent.synthesize_delta_update(
            node=node,
            current_plan=flawed_plan,
            blocking_violations=violations,
        )

        self.assertGreater(delta_tokens, 0)
        # Offending hallucination subtask must be excised
        subtask_ids = [s.subtask_id for s in purified_plan.subtasks]
        self.assertNotIn(f"{node.task_id}.leaf_mesh_hallucination", subtask_ids)
        self.assertEqual(len(purified_plan.subtasks), 2)

        # Budget fractions must be re-normalized to 1.0
        total_fraction = sum(s.budget_fraction for s in purified_plan.subtasks)
        self.assertAlmostEqual(total_fraction, 1.0, places=3)

        # Quine isolation must be reinstated in payloads
        for sub in purified_plan.subtasks:
            self.assertTrue(sub.payload.get("isolation_enforced"))
            self.assertFalse(sub.payload.get("bypass_quine_isolation", False))
            self.assertNotIn("8-voice", sub.description)
            self.assertNotIn("bypassed Quine isolation", sub.description)

        # Rationale must reflect delta update
        self.assertIn("Delta Update", purified_plan.rationale)

    def test_end_to_end_adversarial_quorum_gate_traps_hallucinations_and_converges(self):
        """6. Full E2E Substrate Test: Proves the FSM traps hallucinations, loops, and yields verified artifacts.

        - Injects a mock proposal containing an unbudgeted '8-voice networked WebSocket mesh' and a 'bypassed Quine isolation'.
        - Asserts ProductManagerAuditor and ArchitectAuditor return approved=False with correct violation strings.
        - Asserts FSM routes violations back to generator, loops, and yields unanimous proposal before proceeding to IR synthesis.
        """
        pitch = PitchInput(
            title="Real-Time Clinical Telemetry Hub",
            elevator_pitch="Multi-node local telemetry collector for medical sensor streams.",
            target_audience="Biomedical Engineers",
            intended_features=["Packet verification", "Zero-downtime rollback"],
        )

        orchestrator = CrucibleOrchestrator(total_budget=600000, d_max=5, b_max=8)

        # Inject both hallucinations on first attempt:
        # 1. Unbudgeted '8-voice networked WebSocket mesh'
        # 2. 'bypassed Quine isolation'
        result = orchestrator.run_crucible(
            seed_input=pitch,
            soc_id="soc_clinical_hub",
            is_multi_node_cluster=True,
            required_invariants=["patient_id_valid == True"],
            inject_quorum_hallucinations=True,
        )

        # 1. Verify that the Quorum Consensus Gate recorded at least 2 iterations
        self.assertGreaterEqual(len(result.quorum_consensus_events), 2)

        # Iteration 1: Rejected!
        iter_1 = result.quorum_consensus_events[0]
        self.assertFalse(iter_1["is_unanimous"], "Iteration 1 must NOT be unanimous when hallucinations are present!")
        pm_verdict_1 = iter_1["verdicts"]["PRODUCT_MANAGER"]
        arch_verdict_1 = iter_1["verdicts"]["SYSTEMS_ARCHITECT"]

        # ProductManagerAuditor must have returned approved=False
        self.assertFalse(pm_verdict_1["approved"])
        self.assertTrue(
            any("8-voice" in v or "websocket mesh" in v or "Unbudgeted" in v for v in pm_verdict_1["blocking_violations"]),
            f"ProductManagerAuditor failed to flag 8-voice WebSocket mesh: {pm_verdict_1['blocking_violations']}",
        )

        # ArchitectAuditor must have returned approved=False
        self.assertFalse(arch_verdict_1["approved"])
        self.assertTrue(
            any("bypassed quine" in v.lower() or "L1-G3B-017" in v for v in arch_verdict_1["blocking_violations"]),
            f"ArchitectAuditor failed to flag bypassed Quine isolation: {arch_verdict_1['blocking_violations']}",
        )

        # Iteration 2: Purified and Unanimously Approved!
        iter_2 = result.quorum_consensus_events[1]
        self.assertTrue(iter_2["is_unanimous"], "Iteration 2 must reach unanimous consensus after Delta Update!")
        self.assertEqual(len(iter_2["all_blocking_violations"]), 0)
        self.assertTrue(iter_2["verdicts"]["PRODUCT_MANAGER"]["approved"])
        self.assertTrue(iter_2["verdicts"]["SYSTEMS_ARCHITECT"]["approved"])
        self.assertTrue(iter_2["verdicts"]["QA_ENGINEER"]["approved"])

        # 2. Verify progression to clean IR Synthesis and Leaf Emission
        self.assertEqual(len(result.verified_leaves), 4)
        self.assertEqual(len(result.audit_certificates), 4)
        for cert in result.audit_certificates.values():
            self.assertTrue(cert.is_passed)

        self.assertIsNotNone(result.verified_contract)
        self.assertIsNotNone(result.verified_statechart)
        self.assertIsNotNone(result.verified_topology)
        self.assertEqual(len(result.verified_code_modules), 1)

        # 3. Verify physical token accounting
        self.assertGreater(result.argon_verification_tokens, 0)
        self.assertGreater(result.argon_deliberation_tokens, 0)
        self.assertGreater(result.flash_emission_tokens, 0)

        print(
            f"\n[ADVERSARIAL QUORUM GATE CERTIFIED]: Trapped injected hallucinations on Iteration 1 "
            f"({len(iter_1['all_blocking_violations'])} violations), synthesized Argon Delta Update, "
            f"and achieved unanimous consensus on Iteration 2!"
        )

    def test_quorum_deadlock_circuit_breaker(self):
        """7. QuorumConsensusDeadlockError trips when violations cannot converge within max_iterations."""
        node = TaskNode(
            task_id="task_deadlock_test",
            task_type=TaskType.DIALECTICAL_ARCH_DECOMPOSITION,
            description="Deadlock test",
            allocated_token_budget=10000,
            depth=1,
            payload={"soc": {"soc_id": "soc_deadlock"}},
        )

        # A proposal whose delta update still returns persistent violations
        class MockPersistentViolator:
            @classmethod
            def audit(cls, node, plan, domain_spec=None):
                return QuorumVerdict(
                    role_id="PRODUCT_MANAGER",
                    approved=False,
                    blocking_violations=["Persistent irreconcilable scope breach"],
                ), 100

        # Replace temporarily
        orig_audit = ProductManagerAuditor.audit
        try:
            ProductManagerAuditor.audit = MockPersistentViolator.audit
            orchestrator = CrucibleOrchestrator(total_budget=50000)
            clean_plan = DecompositionPlan(
                parent_task_id=node.task_id,
                rationale="Stub plan",
                subtasks=[
                    SubtaskSpec(
                        subtask_id=f"{node.task_id}.leaf_1",
                        task_type=TaskType.LEAF_CONTRACT_FRAGMENT,
                        description="Test",
                        is_leaf=True,
                        budget_fraction=1.0,
                    )
                ],
            )
            with self.assertRaises(QuorumConsensusDeadlockError):
                orchestrator.run_adversarial_quorum_gate(node, clean_plan, max_iterations=2)
        finally:
            ProductManagerAuditor.audit = orig_audit


if __name__ == "__main__":
    unittest.main()
