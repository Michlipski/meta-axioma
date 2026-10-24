"""Milestone 2 Adversarial Verification Suite: The Adversaries.

Validates that all Zero-Trust Evaluators (governed by Gemini 4 Argon) successfully
trap 100% of hand-crafted poisonous IRs and structural defects:
1. Formal Model Checker traps: Dead-End traps, Unreachable states, Dangling targets, Parallel conflicts.
2. Headless Journey Walker traps: Phantom steps ([L1-G3B-013]), Steps-to-Value overrun, Missing Functorial Undo ([L1-002]).
3. Zero-Trust Micro-Auditors traps: Security/eval leaks, Missing contract invariants,
   Dual-Model Cognitive Routing violations ([L1-G3B-014]), Multi-node loopback leaks ([L1-G3B-012]),
   Thermodynamic token overruns, and Isolated Re-prompt synthesis.
"""

import sys
import unittest
from pathlib import Path

# Add src to sys.path
SRC_DIR = Path(__file__).resolve().parent.parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from g3b_compiler.ir import (
    StateNodeType,
    HistoryType,
    Transition,
    StateNode,
    StatechartIR,
)
from g3b_compiler.routing import (
    CognitiveRole,
    ModelTier,
    CognitiveRoutingViolation,
    DualModelRouter,
)
from g3b_compiler.evaluators import (
    FormalModelChecker,
    ModelCheckingFailure,
    HeadlessJourneyWalker,
    JourneyStep,
    PhantomJourneyStepViolation,
    JourneyAuditFailure,
    LeafArtifact,
    ZeroTrustMicroAuditorRegistry,
    SecurityMicroAuditor,
    ContractMicroAuditor,
    CognitiveRoutingAuditor,
    TopologicalMicroAuditor,
    ThermodynamicMicroAuditor,
)


class TestFormalModelCheckerPoisonTraps(unittest.TestCase):
    """Adversarial tests: Verifies that FormalModelChecker traps all defective Statechart IRs."""

    def test_trap_dead_end_state(self):
        """Poison: Non-final atomic state 'trap_leaf' has zero outgoing transitions."""
        poison_root = StateNode(
            id="root",
            node_type=StateNodeType.COMPOUND,
            initial="start",
            states={
                "start": StateNode(
                    id="root.start",
                    node_type=StateNodeType.ATOMIC,
                    transitions=[Transition(event="NEXT", target="root.trap_leaf")],
                ),
                "trap_leaf": StateNode(
                    id="root.trap_leaf",
                    node_type=StateNodeType.ATOMIC,  # NOT marked FINAL, has 0 transitions!
                    transitions=[],
                ),
            },
        )
        chart = StatechartIR(id="poison_dead_end_chart", root=poison_root)
        report = FormalModelChecker.check(chart)

        self.assertFalse(report.is_certified)
        self.assertIn("root.trap_leaf", report.dead_end_states)
        self.assertTrue(any("Dead-End Trap" in d for d in report.defect_summary))

        with self.assertRaises(ModelCheckingFailure):
            FormalModelChecker.assert_certified(chart)

    def test_trap_unreachable_state(self):
        """Poison: State 'orphan_island' is completely disconnected from root.initial."""
        poison_root = StateNode(
            id="root",
            node_type=StateNodeType.COMPOUND,
            initial="active",
            states={
                "active": StateNode(
                    id="root.active",
                    node_type=StateNodeType.ATOMIC,
                    transitions=[Transition(event="FINISH", target="root.done")],
                ),
                "done": StateNode(id="root.done", node_type=StateNodeType.FINAL),
                "orphan_island": StateNode(  # Disconnected from root.initial!
                    id="root.orphan_island",
                    node_type=StateNodeType.ATOMIC,
                    transitions=[Transition(event="BACK", target="root.active")],
                ),
            },
        )
        chart = StatechartIR(id="poison_unreachable_chart", root=poison_root)
        report = FormalModelChecker.check(chart)

        self.assertFalse(report.is_certified)
        self.assertIn("root.orphan_island", report.unreachable_states)
        self.assertTrue(any("Unreachable State Trap" in d for d in report.defect_summary))

    def test_trap_dangling_transition_target(self):
        """Poison: Transition targets non-existent state 'root.phantom_target'."""
        poison_root = StateNode(
            id="root",
            node_type=StateNodeType.COMPOUND,
            initial="start",
            states={
                "start": StateNode(
                    id="root.start",
                    node_type=StateNodeType.ATOMIC,
                    transitions=[Transition(event="GOTO_NOWHERE", target="root.phantom_target")],
                ),
            },
        )
        chart = StatechartIR(id="poison_dangling_chart", root=poison_root)
        report = FormalModelChecker.check(chart)

        self.assertFalse(report.is_certified)
        self.assertTrue(any(d["target"] == "root.phantom_target" for d in report.dangling_transitions))

    def test_trap_parallel_region_conflict(self):
        """Poison: Parallel regions fire uncoordinated conflicting transitions on the same event."""
        r1 = StateNode(
            id="parallel.r1",
            node_type=StateNodeType.COMPOUND,
            initial="s1",
            states={
                "s1": StateNode(
                    id="parallel.r1.s1",
                    node_type=StateNodeType.ATOMIC,
                    transitions=[Transition(event="SHARED_MUTATION", target="parallel.r1.dest_a")],
                ),
                "dest_a": StateNode(id="parallel.r1.dest_a", node_type=StateNodeType.FINAL),
            },
        )
        r2 = StateNode(
            id="parallel.r2",
            node_type=StateNodeType.COMPOUND,
            initial="s2",
            states={
                "s2": StateNode(
                    id="parallel.r2.s2",
                    node_type=StateNodeType.ATOMIC,
                    transitions=[Transition(event="SHARED_MUTATION", target="parallel.r2.dest_b")],
                ),
                "dest_b": StateNode(id="parallel.r2.dest_b", node_type=StateNodeType.FINAL),
            },
        )
        parallel_node = StateNode(
            id="root.parallel_split",
            node_type=StateNodeType.PARALLEL,
            states={"r1": r1, "r2": r2},
        )
        root = StateNode(
            id="root",
            node_type=StateNodeType.COMPOUND,
            initial="parallel_split",
            states={"parallel_split": parallel_node},
        )
        chart = StatechartIR(id="poison_parallel_chart", root=root)
        report = FormalModelChecker.check(chart)

        self.assertFalse(report.is_certified)
        self.assertGreater(len(report.parallel_conflicts), 0)
        self.assertTrue(any("Parallel Region Conflict" in c for c in report.parallel_conflicts))

    def test_legitimate_statechart_certified(self):
        """Certifies that a clean, well-formed statechart passes with zero defects."""
        root = StateNode(
            id="root",
            node_type=StateNodeType.COMPOUND,
            initial="start",
            states={
                "start": StateNode(
                    id="root.start",
                    node_type=StateNodeType.ATOMIC,
                    transitions=[Transition(event="EXECUTE", target="root.done")],
                ),
                "done": StateNode(id="root.done", node_type=StateNodeType.FINAL),
            },
        )
        chart = StatechartIR(id="clean_chart", root=root)
        report = FormalModelChecker.assert_certified(chart)
        self.assertTrue(report.is_certified)
        self.assertEqual(len(report.defect_summary), 0)


class TestHeadlessJourneyWalkerPoisonTraps(unittest.TestCase):
    """Adversarial tests: Verifies [L1-G3B-013] anti-phantom gate and cognitive ergonomics."""

    def test_trap_phantom_journey_step(self):
        """Poison: Journey step asserts completion but produces ZERO external state delta."""
        phantom_step = JourneyStep(
            step_index=0,
            actor_id="user_1",
            action_name="click_checkout",
            target_interface="/cart/checkout",
            expected_observable_change="Order record created with status 'confirmed'",
            # ZERO DELTA: before equals after!
            state_before={"order_count": 0, "status": "cart"},
            state_after={"order_count": 0, "status": "cart"},  # Phantom!
        )

        with self.assertRaises(PhantomJourneyStepViolation):
            HeadlessJourneyWalker.assert_certified(
                journey_id="poison_phantom_journey",
                persona_role="Shopper",
                steps=[phantom_step],
            )

    def test_trap_steps_to_value_overrun(self):
        """Poison: User is forced through 5 onboarding steps before reaching core value (budget <= 3)."""
        steps = [
            JourneyStep(0, "user", "step_1", "ui", state_before={"a": 0}, state_after={"a": 1}, inverse_action="undo_1"),
            JourneyStep(1, "user", "step_2", "ui", state_before={"b": 0}, state_after={"b": 1}, inverse_action="undo_2"),
            JourneyStep(2, "user", "step_3", "ui", state_before={"c": 0}, state_after={"c": 1}, inverse_action="undo_3"),
            JourneyStep(3, "user", "step_4", "ui", state_before={"d": 0}, state_after={"d": 1}, inverse_action="undo_4"),
            JourneyStep(4, "user", "reach_value", "ui", state_before={"v": 0}, state_after={"v": 1, "value_delivered": True}, inverse_action="undo_v"),
        ]

        with self.assertRaises(JourneyAuditFailure):
            HeadlessJourneyWalker.assert_certified(
                journey_id="poison_friction_journey",
                persona_role="Customer",
                steps=steps,
                max_steps_to_value=3,
            )

    def test_trap_missing_functorial_undo(self):
        """Poison: Mutating state change lacks inverse action ([L1-002])."""
        steps = [
            JourneyStep(
                step_index=0,
                actor_id="user",
                action_name="delete_critical_record",
                target_interface="/records/123",
                state_before={"record_exists": True},
                state_after={"record_exists": False, "value_delivered": True},
                inverse_action=None,  # Missing Functorial Undo!
            )
        ]
        report = HeadlessJourneyWalker.walk("poison_no_undo", "Admin", steps)
        self.assertFalse(report.is_certified)
        self.assertFalse(report.undo_lossless)
        self.assertTrue(any("Functorial Undo Violation" in v for v in report.ergonomic_violations))

    def test_legitimate_journey_certified(self):
        """Certifies that a clean 2-step journey with real state deltas and undo passes."""
        steps = [
            JourneyStep(
                step_index=0,
                actor_id="user",
                action_name="capture_margin_note",
                target_interface="/reader/margin",
                expected_observable_change="note_created",
                state_before={"notes_count": 0},
                state_after={"notes_count": 1, "value_delivered": True},
                inverse_action="delete_margin_note",
            )
        ]
        report = HeadlessJourneyWalker.assert_certified(
            journey_id="clean_reading_journey",
            persona_role="Reader",
            steps=steps,
            max_steps_to_value=3,
        )
        self.assertTrue(report.is_certified)
        self.assertEqual(len(report.phantom_steps_detected), 0)


class TestZeroTrustMicroAuditorsPoisonTraps(unittest.TestCase):
    """Adversarial tests: Verifies that Zero-Trust Micro-Auditors trap leaf node defects."""

    def test_trap_hardcoded_secrets_and_injection(self):
        """Poison: Leaf contains an exposed API key and raw SQL injection."""
        poison_leaf = LeafArtifact(
            task_id="leaf_auth_db",
            artifact_type="code",
            content="""
def authenticate(user_input):
    api_key = "sk-live-1234567890abcdef12345"
    query = f"SELECT * FROM users WHERE name = '{user_input}'"
    return cursor.execute(query)
""",
        )
        defects = SecurityMicroAuditor.audit(poison_leaf)
        self.assertEqual(len(defects), 2)
        self.assertTrue(any("credential detected" in d for d in defects))
        self.assertTrue(any("SQL injection" in d for d in defects))

    def test_trap_contract_invariant_violation(self):
        """Poison: Leaf implementation omits mandatory invariant 'balance >= 0'."""
        poison_leaf = LeafArtifact(
            task_id="leaf_wallet",
            artifact_type="code",
            content="""
def debit(amount):
    self.balance -= amount
    return self.balance
""",
            metadata={"required_invariants": ["balance >= 0"]},
        )
        defects = ContractMicroAuditor.audit(poison_leaf)
        self.assertEqual(len(defects), 1)
        self.assertIn("balance >= 0", defects[0])

    def test_trap_cognitive_routing_mismatch(self):
        """Poison [L1-G3B-014]: Leaf node claims emission by Gemini 4 Argon instead of Muscle Flash."""
        poison_leaf = LeafArtifact(
            task_id="leaf_widget",
            artifact_type="code",
            content="def render(): return True",
            emitting_model=ModelTier.BRAIN_ARGON.value,  # VIOLATION: Argon cannot do leaf muscle emission!
        )
        defects = CognitiveRoutingAuditor.audit(poison_leaf)
        self.assertEqual(len(defects), 1)
        self.assertIn("L1-G3B-014 Violation", defects[0])

    def test_trap_dual_model_router_direct_role_violation(self):
        """Poison [L1-G3B-014]: Attempting to route model checker to Muscle Flash or code emission to Argon."""
        orig_argon = DualModelRouter.is_argon_enabled()
        try:
            DualModelRouter.set_argon_enabled(True)
            # 1. Attempting to assign Model Checker to Flash
            with self.assertRaises(CognitiveRoutingViolation):
                DualModelRouter.create_invocation(
                    task_id="check_task",
                    role=CognitiveRole.MODEL_CHECKER,
                    payload={},
                    requested_model=ModelTier.MUSCLE_FLASH,  # Brain role given to Muscle!
                )

            # 2. Attempting to assign Leaf Code Emission to Argon
            with self.assertRaises(CognitiveRoutingViolation):
                DualModelRouter.create_invocation(
                    task_id="leaf_task",
                    role=CognitiveRole.LEAF_CODE_EMISSION,
                    payload={},
                    requested_model=ModelTier.BRAIN_ARGON,  # Muscle role given to Brain!
                )
        finally:
            DualModelRouter.set_argon_enabled(orig_argon)

    def test_trap_topological_multi_node_loopback(self):
        """Poison [L1-G3B-012]: Multi-node cluster leaf binds to 127.0.0.1 loopback."""
        poison_leaf = LeafArtifact(
            task_id="leaf_cluster_node",
            artifact_type="config",
            content="peer_endpoint = 'http://127.0.0.1:8080/gossip'",
            network_endpoints=["http://127.0.0.1:8080"],
            metadata={"is_multi_node_cluster": True},
        )
        defects = TopologicalMicroAuditor.audit(poison_leaf)
        self.assertGreater(len(defects), 0)
        self.assertTrue(any("L1-G3B-012 Violation" in d for d in defects))

    def test_trap_thermodynamic_leaf_token_overrun(self):
        """Poison: Leaf allocated 50 tokens emits 500 tokens."""
        poison_leaf = LeafArtifact(
            task_id="leaf_bloat",
            artifact_type="code",
            content="word " * 200,  # ~200 tokens
            token_budget_allocated=50,  # Cap is 50!
        )
        defects, tokens = ThermodynamicMicroAuditor.audit(poison_leaf)
        self.assertEqual(len(defects), 1)
        self.assertIn("exceeding its allocated leaf quota", defects[0])

    def test_isolated_leaf_reprompt_synthesis(self):
        """Verifies that an audited defect synthesizes an isolated re-prompt under Argon governance."""
        leaf = LeafArtifact(
            task_id="leaf_flawed_calc",
            artifact_type="code",
            content="def calc(): return eval('1+1')",
            metadata={"isolation_depth": 0},
        )
        audit_result = ZeroTrustMicroAuditorRegistry.audit_leaf(leaf)
        self.assertFalse(audit_result.is_passed)
        self.assertIsNotNone(audit_result.remediation_advice)

        # Synthesize isolated re-prompt under Argon governance
        orig_argon = DualModelRouter.is_argon_enabled()
        try:
            DualModelRouter.set_argon_enabled(True)
            reprompt_invocation = DualModelRouter.synthesize_isolated_reprompt(
                failed_leaf_task_id=leaf.task_id,
                leaf_role=CognitiveRole.LEAF_CODE_EMISSION,
                defect_report=audit_result.remediation_advice,
                prior_payload={"source": leaf.content, "isolation_depth": 0},
            )

            self.assertEqual(reprompt_invocation.assigned_model, ModelTier.MUSCLE_FLASH)
            self.assertTrue(reprompt_invocation.is_reprompt)
            self.assertEqual(reprompt_invocation.isolation_depth, 1)
            self.assertEqual(reprompt_invocation.payload["reprompt_governor"], ModelTier.BRAIN_ARGON.value)
            self.assertIn("Defects to remediate", reprompt_invocation.payload["defect_remediation"])
            print("\n[ISOLATED RE-PROMPT CERTIFIED]: Micro-auditor trapped defect and synthesized Argon-governed Flash re-prompt!")
        finally:
            DualModelRouter.set_argon_enabled(orig_argon)


if __name__ == "__main__":
    unittest.main()
