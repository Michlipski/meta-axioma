"""Comprehensive Test Suite for Headless UI Journey Walker (`[L1-G4B-017]`).

Verifies:
  - Domain models, serializations, and SHA-256 cryptographic attestation hashes.
  - Declarative Flow Markdown parser and StatechartIR Eulerian covering-path fuzzer.
  - Mathematical 2D visual geometry engine (Axiom 1 Viewport Containment, Axiom 2 Non-Occlusion).
  - Empirical 5-step closed-loop journey execution against live subprocess `apps/axioma_phenoflora/run.py`.
  - Chaos validation demonstrating fail-fast DOMMutationTimeoutViolation when re-renders stall.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import sys
import unittest

# Ensure audit package root and workspace root are on sys.path
TESTS_DIR = Path(__file__).resolve().parent
AUDIT_SERVICE_DIR = TESTS_DIR.parent
WORKSPACE_ROOT = AUDIT_SERVICE_DIR.parents[3]
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))
if str(AUDIT_SERVICE_DIR) not in sys.path:
    sys.path.insert(0, str(AUDIT_SERVICE_DIR))

from src.journey_walker.domain_models import (
    BoundingBox,
    DOMMutationTimeoutViolation,
    JourneyReport,
    JourneyStep,
    JourneyStepResult,
    JourneyVerificationFailure,
    OcclusionViolation,
    ViewportClippingViolation,
)
from src.journey_walker.flow_parser import FlowParser
from src.journey_walker.runner import HeadlessUIJourneyWalker
from src.journey_walker.smt_guard_bridge import SMTGuardBridge
from src.journey_walker.statechart_ir import (
    HistoryType,
    StatechartIR,
    StateNode,
    StateNodeType,
    Transition,
)
from src.journey_walker.visual_occlusion_checker import VisualOcclusionChecker


class TestJourneyWalkerDomainModels(unittest.TestCase):
    """Unit tests for domain models, serialization, and cryptographic hashing."""

    def test_bounding_box_geometry_and_center(self) -> None:
        box = BoundingBox(x=100.0, y=200.0, width=50.0, height=80.0, z_index=5, selector="#btn")
        self.assertEqual(box.center_point, (125.0, 240.0))
        self.assertTrue(box.contains_point(125.0, 240.0))
        self.assertTrue(box.contains_point(100.0, 200.0))
        self.assertFalse(box.contains_point(99.0, 200.0))
        self.assertFalse(box.contains_point(160.0, 240.0))

    def test_bounding_box_roundtrip(self) -> None:
        box = BoundingBox(x=10.0, y=20.0, width=100.0, height=40.0, z_index=2, selector="#modal")
        d = box.to_dict()
        restored = BoundingBox.from_dict(d)
        self.assertEqual(box, restored)

    def test_journey_step_roundtrip(self) -> None:
        step = JourneyStep(
            step_id="step_01",
            action_type="CLICK",
            target_selector="#template-spring-queen",
            expected_dom_mutation="#spatial-svg",
            max_latency_ms=150,
        )
        d = step.to_dict()
        restored = JourneyStep.from_dict(d)
        self.assertEqual(step.step_id, restored.step_id)
        self.assertEqual(step.action_type, restored.action_type)
        self.assertEqual(step.target_selector, restored.target_selector)
        self.assertEqual(step.expected_dom_mutation, restored.expected_dom_mutation)
        self.assertEqual(step.max_latency_ms, restored.max_latency_ms)

    def test_journey_report_witness_hash_determinism(self) -> None:
        step_res = JourneyStepResult(
            step_id="step_01",
            status="PASSED",
            latency_ms=12.4,
            action_type="CLICK",
            target_selector="#btn",
            dom_mutation_verified=True,
        )
        report1 = JourneyReport(
            total_steps_executed=1,
            statechart_coverage_pct=100.0,
            unhandled_console_errors=[],
            max_observed_latency_ms=12.4,
            journey_status="PASSED",
            step_results=[step_res],
            flow_name="TestFlow",
        )
        report2 = JourneyReport(
            total_steps_executed=1,
            statechart_coverage_pct=100.0,
            unhandled_console_errors=[],
            max_observed_latency_ms=12.4,
            journey_status="PASSED",
            step_results=[step_res],
            flow_name="TestFlow",
        )
        hash1 = report1.calculate_witness_hash()
        hash2 = report2.calculate_witness_hash()
        self.assertEqual(hash1, hash2)
        self.assertEqual(len(hash1), 64)


class TestFlowParserAndStatechartCovering(unittest.TestCase):
    """Unit tests for declarative flow markdown parser and StatechartIR Eulerian tour compiler."""

    def test_parse_declarative_flow_markdown_file(self) -> None:
        flow_file = WORKSPACE_ROOT / "apps" / "axioma_phenoflora" / "trace" / "flows" / "habitat_design_studio.flow.md"
        if not flow_file.exists():
            self.skipTest("habitat_design_studio.flow.md not found")

        steps = FlowParser.parse_flow_markdown(str(flow_file))
        self.assertGreaterEqual(len(steps), 4)
        step_ids = [s.step_id for s in steps]
        self.assertIn("step_1", step_ids)
        self.assertIn("step_2", step_ids)

    def test_parse_embedded_journey_step_comments(self) -> None:
        markdown = """
# Sample Flow
<!-- journey_step: {"step_id": "annotated_01", "action_type": "CLICK", "target_selector": "#btn-test", "expected_dom_mutation": "#result", "max_latency_ms": 100} -->
<!-- journey_step: {"step_id": "annotated_02", "action_type": "INPUT", "target_selector": "#inp-test", "input_value": "hello"} -->
"""
        steps = FlowParser.parse_flow_markdown(markdown)
        self.assertEqual(len(steps), 2)
        self.assertEqual(steps[0].step_id, "annotated_01")
        self.assertEqual(steps[0].target_selector, "#btn-test")
        self.assertEqual(steps[1].action_type, "INPUT")
        self.assertEqual(steps[1].input_value, "hello")

    def test_eulerian_covering_path_100_pct_coverage(self) -> None:
        # Directed graph with 4 states and 6 transitions
        statechart_graph = {
            "states": ["idle", "designing", "simulating", "certified"],
            "transitions": [
                {"from_state": "idle", "to_state": "designing", "event": "EV_LOAD", "target_selector": "#load"},
                {"from_state": "designing", "to_state": "simulating", "event": "EV_SIMULATE", "target_selector": "#sim"},
                {"from_state": "simulating", "to_state": "certified", "event": "EV_VERIFY", "target_selector": "#verify"},
                {"from_state": "certified", "to_state": "idle", "event": "EV_RESET", "target_selector": "#reset"},
                {"from_state": "designing", "to_state": "idle", "event": "EV_CANCEL", "target_selector": "#cancel"},
                {"from_state": "simulating", "to_state": "designing", "event": "EV_REEDIT", "target_selector": "#edit"},
            ],
        }
        covering_steps, coverage_pct = FlowParser.compute_statechart_covering_path(
            statechart_graph, initial_state="idle"
        )
        self.assertGreaterEqual(coverage_pct, 90.0)
        self.assertEqual(coverage_pct, 100.0)
        self.assertGreaterEqual(len(covering_steps), 6)


class TestVisualOcclusionChecker(unittest.TestCase):
    """Unit tests for mathematical visual occlusion and viewport containment axioms."""

    def setUp(self) -> None:
        self.checker = VisualOcclusionChecker(default_viewport_width=1920.0, default_viewport_height=1080.0)

    def test_axiom_1_viewport_containment_valid(self) -> None:
        box = BoundingBox(x=10.0, y=10.0, width=200.0, height=50.0, selector="#btn-valid")
        # Should not raise
        self.checker.check_viewport_containment(box)

    def test_axiom_1_viewport_containment_negative_coordinates(self) -> None:
        box = BoundingBox(x=-5.0, y=10.0, width=100.0, height=40.0, selector="#btn-neg")
        with self.assertRaises(ViewportClippingViolation):
            self.checker.check_viewport_containment(box)

    def test_axiom_1_viewport_containment_overflow_clipping(self) -> None:
        box = BoundingBox(x=1900.0, y=100.0, width=50.0, height=40.0, selector="#btn-overflow")
        with self.assertRaises(ViewportClippingViolation):
            self.checker.check_viewport_containment(box)

    def test_axiom_2_non_occlusion_unoccluded(self) -> None:
        btn = BoundingBox(x=100.0, y=100.0, width=100.0, height=40.0, z_index=1, selector="#btn-submit")
        backdrop = BoundingBox(x=0.0, y=0.0, width=1920.0, height=1080.0, z_index=0, selector="body")
        # Button is on top (z=1 > z=0); should not raise
        self.checker.check_non_occlusion(btn, [backdrop, btn])

    def test_axiom_2_non_occlusion_blocked_by_modal(self) -> None:
        btn = BoundingBox(x=100.0, y=100.0, width=100.0, height=40.0, z_index=1, selector="#btn-underlying")
        modal_overlay = BoundingBox(x=50.0, y=50.0, width=500.0, height=400.0, z_index=100, selector="#modal-backdrop")
        # Modal overlay has higher z-index (z=100 > z=1) and covers (150, 120)
        with self.assertRaises(OcclusionViolation):
            self.checker.check_non_occlusion(btn, [btn, modal_overlay])


class TestHeadlessUIJourneyWalkerExecution(unittest.TestCase):
    """Integration tests running live multi-step journeys against apps/axioma_phenoflora."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.app_run_script = str(WORKSPACE_ROOT / "apps" / "axioma_phenoflora" / "run.py")
        cls.walker = HeadlessUIJourneyWalker(host="127.0.0.1", default_timeout_s=6.0)

    def test_live_5_step_journey_against_phenoflora(self) -> None:
        """Executes the canonical 5-step socio-technical journey walk against live PhenoFlora studio:

        Step 1: Boot and load page.
        Step 2: Click starter habitat template (#template-spring-queen).
        Step 3: Assert canvas re-renders with plants.
        Step 4: Click SMT verification button (#btn-run-prover).
        Step 5: Assert trophic continuity result badge renders with status "SAT".
        """
        five_step_journey = [
            JourneyStep(
                step_id="step_01_boot_page",
                action_type="NAVIGATE",
                target_selector="#template-spring-queen",
                expected_dom_mutation="body, #spatial-svg",
                max_latency_ms=200,
            ),
            JourneyStep(
                step_id="step_02_load_starter_template",
                action_type="CLICK",
                target_selector="#template-spring-queen",
                expected_dom_mutation="#template-spring-queen",
                max_latency_ms=200,
            ),
            JourneyStep(
                step_id="step_03_assert_canvas_rerender",
                action_type="WAIT",
                target_selector="#spatial-svg",
                expected_dom_mutation="[data-node-id='node_claytonia_virginica_2']",
                max_latency_ms=500,
            ),
            JourneyStep(
                step_id="step_04_click_smt_prover",
                action_type="CLICK",
                target_selector="#btn-run-prover",
                expected_dom_mutation="#btn-run-prover",
                max_latency_ms=200,
            ),
            JourneyStep(
                step_id="step_05_assert_trophic_sat",
                action_type="WAIT",
                target_selector="#smt-status-pill",
                expected_dom_mutation="#smt-status-pill, .status-sat",
                max_latency_ms=200,
            ),
        ]

        report = self.walker.walk_journey(
            journey_steps=five_step_journey,
            app_entrypoint=self.app_run_script,
            flow_name="PhenoFloraContinuousContinuityJourney",
            statechart_coverage_pct=100.0,
        )

        self.assertEqual(report.journey_status, "PASSED")
        self.assertEqual(report.total_steps_executed, 5)
        self.assertEqual(len(report.unhandled_console_errors), 0)
        self.assertGreaterEqual(report.statechart_coverage_pct, 90.0)
        for res in report.step_results:
            self.assertEqual(res.status, "PASSED")
            self.assertTrue(res.dom_mutation_verified)

    def test_chaos_validation_dom_mutation_timeout(self) -> None:
        """Chaos Validation: Physical defect injection into client app.js.

        Mutating renderSpatialCanvas() out of app.js causes the Journey Walker
        probe to fail fast with DOMMutationTimeoutViolation, proving that
        client-side rendering is genuinely executed and verified.
        """
        five_step_journey = [
            JourneyStep(
                step_id="step_01_boot_page",
                action_type="NAVIGATE",
                target_selector="#template-spring-queen",
                expected_dom_mutation="body",
                max_latency_ms=200,
            ),
            JourneyStep(
                step_id="step_02_load_starter_template",
                action_type="CLICK",
                target_selector="#template-spring-queen",
                expected_dom_mutation="#template-spring-queen",
                max_latency_ms=200,
            ),
            JourneyStep(
                step_id="step_03_assert_canvas_rerender",
                action_type="WAIT",
                target_selector="#spatial-svg",
                expected_dom_mutation=".plant-node",
                max_latency_ms=100,  # Fast timeout for chaos assertion
            ),
        ]

        app_js_path = Path(self.app_run_script).parent / "static" / "app.js"
        if not app_js_path.exists():
            self.skipTest("app.js not found for physical chaos mutation")

        import hashlib
        original_text = app_js_path.read_text(encoding="utf-8")
        orig_sha = hashlib.sha256(original_text.encode("utf-8")).hexdigest()
        try:
            mutated = original_text.replace("renderSpatialCanvas();", "// renderSpatialCanvas(); [MUTATED]", 1)
            self.assertIn("[MUTATED]", mutated, "Failed to locate mutation target in app.js")
            app_js_path.write_text(mutated, encoding="utf-8")

            with self.assertRaises(DOMMutationTimeoutViolation):
                self.walker.walk_journey(
                    journey_steps=five_step_journey,
                    app_entrypoint=self.app_run_script,
                    flow_name="PhenoFloraChaosFailureJourney",
                    statechart_coverage_pct=100.0,
                )
        finally:
            app_js_path.write_text(original_text, encoding="utf-8")
            restored_sha = hashlib.sha256(app_js_path.read_text(encoding="utf-8").encode("utf-8")).hexdigest()
            self.assertEqual(orig_sha, restored_sha)


class TestHierarchicalRecursiveStatechartTraversal(unittest.TestCase):
    """Unit and integration tests for recursive XState v5 StatechartIR covering paths."""

    def test_statechart_ir_compound_nesting_covering_path(self) -> None:
        """Verifies recursive traversal through nested compound macro-nodes."""
        editing_node = StateNode(
            id="editing",
            node_type=StateNodeType.ATOMIC,
            transitions=[
                Transition(event="EV_PREVIEW", target="previewing", metadata={"target_selector": "#btn-preview"}),
            ],
        )
        previewing_node = StateNode(
            id="previewing",
            node_type=StateNodeType.ATOMIC,
            transitions=[
                Transition(event="EV_EDIT", target="editing", metadata={"target_selector": "#btn-edit"}),
                Transition(event="EV_COMMIT", target="committed", metadata={"target_selector": "#btn-commit"}),
            ],
        )
        workspace_node = StateNode(
            id="workspace",
            node_type=StateNodeType.COMPOUND,
            initial="editing",
            states={"editing": editing_node, "previewing": previewing_node},
            transitions=[
                Transition(event="EV_RESET_WORKSPACE", target="idle", metadata={"target_selector": "#btn-reset"}),
            ],
        )
        idle_node = StateNode(
            id="idle",
            node_type=StateNodeType.ATOMIC,
            transitions=[
                Transition(event="EV_START", target="workspace", metadata={"target_selector": "#btn-start"}),
            ],
        )
        committed_node = StateNode(
            id="committed",
            node_type=StateNodeType.FINAL,
        )

        root = StateNode(
            id="root",
            node_type=StateNodeType.COMPOUND,
            initial="idle",
            states={"idle": idle_node, "workspace": workspace_node, "committed": committed_node},
        )
        chart = StatechartIR(id="test_recursive_chart", root=root)

        steps, coverage_pct = FlowParser.compute_statechart_covering_path(chart)
        self.assertGreaterEqual(coverage_pct, 90.0)
        self.assertGreaterEqual(len(steps), 4)

        step_events = [s.metadata.get("event") for s in steps]
        self.assertIn("EV_START", step_events)
        self.assertIn("EV_PREVIEW", step_events)
        self.assertIn("EV_COMMIT", step_events)

    def test_statechart_ir_parallel_orthogonal_regions_non_explosion(self) -> None:
        """Proves parallel regions achieve 100% transition coverage in linear steps (no Cartesian explosion)."""
        reg_a = StateNode(
            id="region_a",
            node_type=StateNodeType.COMPOUND,
            initial="a1",
            states={
                "a1": StateNode("a1", transitions=[Transition("EV_A_NEXT", "a2", metadata={"target_selector": "#btn-a"})]),
                "a2": StateNode("a2", transitions=[Transition("EV_A_RESET", "a1", metadata={"target_selector": "#btn-a-reset"})]),
            },
        )
        reg_b = StateNode(
            id="region_b",
            node_type=StateNodeType.COMPOUND,
            initial="b1",
            states={
                "b1": StateNode("b1", transitions=[Transition("EV_B_NEXT", "b2", metadata={"target_selector": "#btn-b"})]),
                "b2": StateNode("b2", transitions=[Transition("EV_B_RESET", "b1", metadata={"target_selector": "#btn-b-reset"})]),
            },
        )
        reg_c = StateNode(
            id="region_c",
            node_type=StateNodeType.COMPOUND,
            initial="c1",
            states={
                "c1": StateNode("c1", transitions=[Transition("EV_C_NEXT", "c2", metadata={"target_selector": "#btn-c"})]),
                "c2": StateNode("c2", transitions=[Transition("EV_C_RESET", "c1", metadata={"target_selector": "#btn-c-reset"})]),
            },
        )

        parallel_root = StateNode(
            id="parallel_root",
            node_type=StateNodeType.PARALLEL,
            states={"region_a": reg_a, "region_b": reg_b, "region_c": reg_c},
        )
        chart = StatechartIR(id="parallel_test_chart", root=parallel_root)

        steps, coverage_pct = FlowParser.compute_statechart_covering_path(chart)
        self.assertEqual(coverage_pct, 100.0)
        self.assertEqual(len(steps), 6)

    def test_statechart_ir_history_node_restoration(self) -> None:
        """Verifies virtual restoration steps are generated for history nodes."""
        hist_node = StateNode(id="deep_hist", node_type=StateNodeType.HISTORY, history_type=HistoryType.DEEP)
        compound = StateNode(
            id="modal_workspace",
            node_type=StateNodeType.COMPOUND,
            initial="page1",
            states={
                "page1": StateNode("page1", transitions=[Transition("EV_NEXT", "page2")]),
                "page2": StateNode("page2", transitions=[Transition("EV_DONE", "done")]),
                "deep_hist": hist_node,
            },
        )
        root = StateNode(id="root", node_type=StateNodeType.COMPOUND, initial="modal_workspace", states={"modal_workspace": compound})
        chart = StatechartIR(id="hist_chart", root=root)

        steps, coverage_pct = FlowParser.compute_statechart_covering_path(chart)
        self.assertGreaterEqual(coverage_pct, 90.0)
        hist_steps = [s for s in steps if s.metadata.get("node_type") == "history"]
        self.assertEqual(len(hist_steps), 1)
        self.assertIn("RESTORE", hist_steps[0].step_id)

    def test_smt_guard_bridge_satisfiability_and_preamble(self) -> None:
        """Unit tests for SMTGuardBridge AST guard evaluations."""
        ctx1 = {"is_authenticated": True, "count": 5}
        is_sat, hint = SMTGuardBridge.check_guard_satisfiable("is_authenticated and count > 0", ctx1)
        self.assertTrue(is_sat)
        self.assertIsNone(hint)

        ctx2 = {"is_authenticated": False, "count": 0}
        is_sat, hint = SMTGuardBridge.check_guard_satisfiable("is_authenticated and count > 0", ctx2)
        self.assertFalse(is_sat)
        self.assertIsNotNone(hint)

        actions = [
            {"event": "EV_LOGIN", "actions": ["is_authenticated", "login_action"]},
        ]
        preamble = SMTGuardBridge.synthesize_guard_preamble("is_authenticated", ctx2, actions)
        self.assertEqual(len(preamble), 1)
        self.assertEqual(preamble[0]["event"], "EV_LOGIN")

    def test_phenoflora_production_statechart_ir_json_covering(self) -> None:
        """Loads live 48-state schema/statechart_ir.json from PhenoFlora and computes hierarchical tour."""
        schema_path = WORKSPACE_ROOT / "apps" / "axioma_phenoflora" / "schema" / "statechart_ir.json"
        if not schema_path.exists():
            self.skipTest("PhenoFlora statechart_ir.json not found")

        chart = StatechartIR.from_json(schema_path.read_text(encoding="utf-8"))
        self.assertEqual(chart.id, "axioma_phenoflora_statechart")
        self.assertGreaterEqual(len(chart.get_all_state_ids()), 40)

        steps, coverage_pct = FlowParser.compute_statechart_covering_path(chart)
        self.assertGreaterEqual(coverage_pct, 90.0)
        self.assertGreater(len(steps), 10)


if __name__ == "__main__":
    unittest.main()
