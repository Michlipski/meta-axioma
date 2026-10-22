"""Unit tests for Generation 2b: Multi-Tier Matrix, Stateful Overrides, and Dynamic Weighted Recursion."""

import os
from pathlib import Path
import tempfile
import unittest

from g2b_compiler.matrix.models import Tier1StructuralRule, Tier2UsabilityHeuristic, MultiTierAuditResult
from g2b_compiler.matrix.heuristics import UsabilityHeuristicAuditor, UNIVERSAL_USABILITY_HEURISTICS
from g2b_compiler.overrides.registry import StatefulOverrideRegistry, HeuristicExemption
from g2b_compiler.recursion.models import (
    WorkerType,
    RecursionNode,
    BoundaryOpinion,
    SubagentSelectionDecision,
    PRESCRIBED_TAXONOMY,
    build_taxonomic_selection_evaluations,
    get_max_recursion_depth,
)
from g2b_compiler.recursion.cost_allocator import ThermodynamicCostAllocator, OutOfProtectedCapitalError, OutOfExploratoryCapitalError
from g2b_compiler.recursion.tree_visualizer import RecursionTreeVisualizer
from g2b_compiler.negotiation.protocol import ScopeNegotiationProtocol


class TestGeneration2b(unittest.TestCase):

    def test_universal_usability_heuristics_catalog(self):
        """Verifies Nielsen-Norman 10 and psychophysical laws are registered."""
        self.assertIn("HEUR-UX-001", UNIVERSAL_USABILITY_HEURISTICS)
        self.assertIn("HEUR-UX-003", UNIVERSAL_USABILITY_HEURISTICS)
        self.assertIn("HEUR-COG-001", UNIVERSAL_USABILITY_HEURISTICS)
        self.assertEqual(len(UNIVERSAL_USABILITY_HEURISTICS), 13)

    def test_statechart_usability_auditor_catches_missing_emergency_exit(self):
        """Verifies HEUR-UX-003 catches compound states without emergency exit (CANCEL/ABORT)."""
        auditor = UsabilityHeuristicAuditor()
        flawed_machine = {
            "states": {
                "capturing": {
                    "states": {
                        "typing": {"on": {"SUBMIT": {"target": "hydrating"}}},
                        "hydrating": {}
                    }
                }
            }
        }
        violations = auditor.audit_statechart_usability(flawed_machine)
        self.assertTrue(any(v["heuristic_id"] == "HEUR-UX-003" for v in violations))

    def test_statechart_usability_auditor_passes_with_emergency_exit(self):
        """Verifies statechart passes when CANCEL/ABORT exit exists."""
        auditor = UsabilityHeuristicAuditor()
        valid_machine = {
            "states": {
                "capturing": {
                    "on": {"CANCEL": {"target": "idle"}},
                    "states": {
                        "typing": {"on": {"SUBMIT": {"target": "hydrating"}}}
                    }
                }
            }
        }
        violations = auditor.audit_statechart_usability(valid_machine)
        self.assertEqual(len(violations), 0)

    def test_fitts_law_touch_target_auditor(self):
        """Verifies HEUR-COG-001 flags touch targets under 44px."""
        auditor = UsabilityHeuristicAuditor()
        bad_css = ":root { --touch-target: 32px; }"
        violations = auditor.audit_css_ergonomics(bad_css)
        self.assertTrue(any(v["heuristic_id"] == "HEUR-COG-001" for v in violations))

        good_css = ":root { --touch-target: 48px; }"
        violations_good = auditor.audit_css_ergonomics(good_css)
        self.assertEqual(len(violations_good), 0)

    def test_stateful_override_registry_and_anti_creep(self):
        """Tests persistent exemption registration, lookup, and Heuristic Debt Index."""
        with tempfile.TemporaryDirectory() as tmpdir:
            reg_path = Path(tmpdir) / "heuristic_overrides.json"
            registry = StatefulOverrideRegistry(reg_path)

            # Initially 0 exemptions
            self.assertEqual(len(registry.exemptions), 0)
            self.assertIsNone(registry.is_exempt("HEUR-COG-001", "hash123"))

            # Register stateful exemption
            ex = registry.register_exemption(
                heuristic_id="HEUR-COG-001",
                component_name="eink_compact_table",
                component_hash="hash123",
                human_rationale="Compact e-ink table display requires 36px row height",
                scope="COMPONENT_LOCAL"
            )
            self.assertIsNotNone(registry.is_exempt("HEUR-COG-001", "hash123"))
            self.assertIsNone(registry.is_exempt("HEUR-COG-001", "otherhash"))

            # Re-load from disk to verify persistence
            reloaded = StatefulOverrideRegistry(reg_path)
            self.assertEqual(len(reloaded.exemptions), 1)
            self.assertIsNotNone(reloaded.is_exempt("HEUR-COG-001", "hash123"))

            # Anti-creep check: if 1 exemption out of 5 checkpoints = 0.20 > 0.15 threshold
            debt = registry.compute_debt_report(total_checkpoints=5)
            self.assertTrue(debt.is_creep_warning)

    def test_worker_type_depth_weighting(self):
        """Verifies worker taxonomy depth consumption."""
        self.assertEqual(WorkerType.EXPLORATORY_RESEARCH.depth_weight, 0.5)
        self.assertEqual(WorkerType.SYNTHESIS.depth_weight, 1.0)
        self.assertEqual(WorkerType.TERMINAL_SINK.depth_weight, 0.0)
        self.assertTrue(WorkerType.TERMINAL_SINK.is_terminal)
        self.assertFalse(WorkerType.SYNTHESIS.is_terminal)

    def test_thermodynamic_cost_allocator_capital_partitioning(self):
        """Verifies protected capital (40%) is reserved for terminal nodes and cannot be starved by exploratory nodes."""
        allocator = ThermodynamicCostAllocator(total_tokens=10000)
        # 4,000 protected, 6,000 exploratory
        self.assertEqual(allocator.capital.protected_capital, 4000)
        self.assertEqual(allocator.capital.exploratory_capital, 6000)

        # Lease 5,000 exploratory tokens
        g1 = allocator.lease_tokens("node_research", WorkerType.EXPLORATORY_RESEARCH, 5000)
        self.assertEqual(g1, 5000)

        # Lease terminal verification tokens (draws from protected 4,000)
        g2 = allocator.lease_tokens("node_test", WorkerType.TERMINAL_SINK, 2000)
        self.assertEqual(g2, 2000)

        # Trying to overdraw exploratory capital raises error
        with self.assertRaises(OutOfExploratoryCapitalError):
            allocator.lease_tokens("node_speculative", WorkerType.EXPLORATORY_RESEARCH, 2000)

    def test_boundary_opinion_probe_and_tree_visualization(self):
        """Verifies boundary depth opinion probe logging and Mermaid tree generation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            visualizer = RecursionTreeVisualizer(run_id="run_test_01", telemetry_dir=tmppath)

            root = RecursionNode(
                node_id="root",
                name="Root Orchestrator",
                worker_type=WorkerType.FRACTAL_DECOMPOSITION,
                depth=0,
                effective_depth=0.0,
                status="SUCCESS"
            )
            child1 = RecursionNode(
                node_id="child_1",
                name="Domain Baseline Research",
                worker_type=WorkerType.EXPLORATORY_RESEARCH,
                depth=1,
                effective_depth=0.5,
                parent_id="root",
                status="SUCCESS"
            )
            leaf_test = RecursionNode(
                node_id="child_2",
                name="Runtime Test Verification",
                worker_type=WorkerType.TERMINAL_SINK,
                depth=2,
                effective_depth=1.5,
                parent_id="root",
                status="SUCCESS"
            )
            root.children = [child1, leaf_test]

            # Record boundary reflection probe
            opinion = BoundaryOpinion(
                wants_depth_extension=True,
                confidence=0.85,
                rationale="Regex edge case requires 1 additional sub-pass",
                estimated_token_cost=1200,
                worker_type=WorkerType.SYNTHESIS,
                subgoal="regex_parser"
            )
            visualizer.record_boundary_opinion(leaf_test, opinion)

            # Check jsonl written
            log_file = tmppath / "recursion_depth_opinions.jsonl"
            self.assertTrue(log_file.exists())
            self.assertIn("regex_parser", log_file.read_text(encoding="utf-8"))

            # Emit tree report
            report_path = tmppath / "recursion_tree.md"
            visualizer.emit_tree_report(root, report_path)
            self.assertTrue(report_path.exists())
            report_text = report_path.read_text(encoding="utf-8")
            self.assertIn("flowchart TD", report_text)
            self.assertIn("Root Orchestrator", report_text)

    def test_scope_negotiation_protocol_ambitious_expansion(self):
        """Verifies Phase 0-A ambitious expansion and deliberate scope cutting."""
        protocol = ScopeNegotiationProtocol()
        dossier = protocol.synthesize_ambitious_lexis_vision(
            elevator_pitch="A fast, distraction-free, local-first vocabulary app."
        )
        self.assertEqual(dossier.app_id, "axioma_lexis")
        self.assertGreater(len(dossier.ambitious_features), 5)
        # Check core features are identified
        core = [f for f in dossier.ambitious_features if f.is_retained_in_core]
        expansions = [f for f in dossier.ambitious_features if not f.is_retained_in_core]
        self.assertGreaterEqual(len(core), 5)
        self.assertGreaterEqual(len(expansions), 2)
        self.assertTrue(any(f.feature_id == "FEAT-CLOUD-SYNC" for f in expansions))

    def test_taxonomic_selection_evaluations_guarantees_nine_workers(self):
        """Verifies build_taxonomic_selection_evaluations strictly evaluates all 9 closed taxonomy workers."""
        self.assertEqual(len(PRESCRIBED_TAXONOMY), 9)
        parent = RecursionNode(
            node_id="parent_node",
            name="SynthesisWorker",
            worker_type=WorkerType.SYNTHESIS,
            subgoal="architecture",
            depth=1,
            effective_depth=1.0,
        )
        chosen = [
            SubagentSelectionDecision(
                worker_type=WorkerType.SYNTHESIS,
                chosen=True,
                allotted_tokens=500,
                used_tokens=480,
                subgoal="scope_negotiation",
                rationale="Scope trimming",
            ),
        ]
        rejections = {
            WorkerType.RESEARCH: "Research done upstream",
            WorkerType.ORCHESTRATOR: "Single orchestrator sufficient",
        }
        decisions = build_taxonomic_selection_evaluations(parent, chosen, rejections)
        self.assertEqual(len(decisions), 9)
        evaluated_types = {d.worker_type for d in decisions}
        self.assertEqual(evaluated_types, set(PRESCRIBED_TAXONOMY))

        # Check chosen node has proper attributes
        chosen_dec = [d for d in decisions if d.chosen]
        self.assertEqual(len(chosen_dec), 1)
        self.assertEqual(chosen_dec[0].worker_type, WorkerType.SYNTHESIS)
        self.assertEqual(chosen_dec[0].allotted_tokens, 500)

        # Check unchosen nodes have non-empty rationales
        for d in decisions:
            if not d.chosen:
                self.assertGreater(len(d.rationale), 0)

    def test_token_accounting_integrity_no_double_counting(self):
        """Verifies _sum_allotted_tokens and _sum_used_tokens compute exact sums without double counting."""
        allocator = ThermodynamicCostAllocator(total_tokens=25000)
        root = RecursionNode(
            node_id="root",
            name="Orchestrator",
            worker_type=WorkerType.ORCHESTRATOR,
            depth=0,
            token_cost=allocator.lease_tokens("root", WorkerType.ORCHESTRATOR, 500),
            tokens_used=allocator.record_usage("root", WorkerType.ORCHESTRATOR, 480),
        )
        child1 = RecursionNode(
            node_id="c1",
            name="Research",
            worker_type=WorkerType.RESEARCH,
            depth=1,
            parent_id="root",
            token_cost=allocator.lease_tokens("c1", WorkerType.RESEARCH, 400),
            tokens_used=allocator.record_usage("c1", WorkerType.RESEARCH, 390),
        )
        child2 = RecursionNode(
            node_id="c2",
            name="Linter",
            worker_type=WorkerType.ANTI_MOCK_LINTER,
            depth=1,
            parent_id="root",
            token_cost=allocator.lease_tokens("c2", WorkerType.ANTI_MOCK_LINTER, 500),
            tokens_used=allocator.record_usage("c2", WorkerType.ANTI_MOCK_LINTER, 470),
        )
        root.children = [child1, child2]

        visualizer = RecursionTreeVisualizer(run_id="test_accounting")
        allotted = visualizer._sum_allotted_tokens(root)
        used = visualizer._sum_used_tokens(root)

        # Expected: root(500) + c1(400) + c2(500) = 1400
        self.assertEqual(allotted, 1400)
        summary = allocator.get_summary()
        self.assertEqual(summary["total_allotted"], 1400)

        # Expected: root(480) + c1(390) + c2(470) = 1340
        self.assertEqual(used, 1340)
        self.assertEqual(summary["total_used"], 1340)


if __name__ == "__main__":
    unittest.main()
