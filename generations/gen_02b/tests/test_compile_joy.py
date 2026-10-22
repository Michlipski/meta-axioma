"""Integration test compiling Axioma Joy through the System G2b Compiler."""

import json
from pathlib import Path
import unittest

from g2b_compiler.engine import SystemG2bCompiler
from g2b_compiler.recursion.models import WorkerType
from g2b_compiler.joy_spec import (
    build_joy_g2b_semantic_ir,
    build_joy_g2b_statechart_ir,
    build_joy_g2b_contract_ir,
)


class TestCompileJoyG2b(unittest.TestCase):

    def test_full_joy_g2b_compilation_pipeline(self):
        compiler = SystemG2bCompiler()
        semantic_ir = build_joy_g2b_semantic_ir()
        statechart_ir = build_joy_g2b_statechart_ir()
        contract_ir = build_joy_g2b_contract_ir()

        output_dir = Path(__file__).parent.parent / "apps" / "axioma_joy"

        pitch = (
            "A mathematical category theory and structural reasoning educational platform for early stage learning "
            "inspired by Eugenia Cheng's triumphant methodology teaching category theory to arts students. "
            "Emphasizing visceral, tangible exploration over rote symbol manipulation."
        )

        # Run compilation with full physical code emission
        artifacts = compiler.compile(
            semantic_ir=semantic_ir,
            statechart_ir=statechart_ir,
            contract_ir=contract_ir,
            target_output_dir=output_dir,
            max_steps_to_value=3,
            port=8120,
            elevator_pitch=pitch,
            total_token_budget=120_000,
            selected_proposal_id="tier_balanced",
            run_id="joy_g2b_compile_run",
        )

        # Verify physical code emission
        self.assertGreaterEqual(len(artifacts.emitted_files), 10)
        self.assertTrue((output_dir / "static" / "index.html").exists())
        self.assertTrue((output_dir / "static" / "machine.js").exists())
        self.assertTrue((output_dir / "static" / "app.js").exists())
        self.assertTrue((output_dir / "static" / "style.css").exists())
        self.assertTrue((output_dir / "server.py").exists())
        self.assertTrue((output_dir / "run.py").exists())
        self.assertTrue((output_dir / "app.json").exists())
        self.assertTrue((output_dir / "data" / "app_state.json").exists())
        self.assertTrue((output_dir / "tests" / "test_runtime.py").exists())
        self.assertTrue((output_dir / "tests" / "test_statechart_execution.py").exists())
        self.assertTrue((output_dir / "recursion_tree.md").exists())
        self.assertTrue((output_dir / "telemetry_dashboard.html").exists())
        self.assertTrue((output_dir / "project_proposals.md").exists())

        # 0. Post-Research Project Proposal Protocol (Option 3 Hybrid Engine)
        self.assertIsNotNone(artifacts.proposal_dossier)
        self.assertEqual(artifacts.proposal_dossier.app_id, "axioma_joy")
        self.assertEqual(len(artifacts.proposal_dossier.proposals), 4)
        self.assertEqual(artifacts.proposal_dossier.selected_proposal_id, "tier_balanced")
        self.assertEqual(artifacts.proposal_dossier.selected_proposal.bounded_token_budget, 120_000)
        self.assertEqual(artifacts.proposal_dossier.selected_proposal.protected_capital, 48_000)
        self.assertEqual(artifacts.proposal_dossier.selected_proposal.exploratory_capital, 72_000)

        # 1. Phase 0-A: Ambitious Discovery & Deliberate Scope-Cutting [L1-G2B-005]
        self.assertIsNotNone(artifacts.scope_dossier)
        self.assertEqual(artifacts.scope_dossier.app_id, "axioma_joy")
        self.assertGreaterEqual(len(artifacts.scope_dossier.ambitious_features), 7)

        # 2. Phase 0-B: Multi-Tier Matrix Interlocking Gate [L1-G2B-001]
        self.assertTrue(artifacts.multi_tier_result.passed)
        self.assertTrue(artifacts.multi_tier_result.tier_1_passed)
        self.assertTrue(artifacts.multi_tier_result.tier_2_passed)
        self.assertTrue(artifacts.multi_tier_result.tier_3_passed)
        self.assertEqual(len(artifacts.multi_tier_result.unresolved_heuristic_violations), 0)

        # 3. Phase 1: Structural Regulation Audit Check
        self.assertTrue(artifacts.regulation_result.is_compliant)
        self.assertEqual(len(artifacts.regulation_result.audit_notes), 0)

        # 4. Phase 3: Model Checking Verification (Formal XState v5)
        model_result = artifacts.model_check_result
        self.assertTrue(model_result.is_valid)
        self.assertEqual(len(model_result.unreachable_states), 0)
        self.assertGreaterEqual(model_result.total_edges, 50)
        self.assertGreater(len(model_result.covering_paths), 10)
        self.assertGreater(len(model_result.negative_test_cases), 500)

        # 5. Phase 4: Viability Gate Check (Steps to Value)
        viability = artifacts.viability_report
        self.assertTrue(viability.passed)
        self.assertLessEqual(viability.steps_to_value, 3)

        # 6. Error Recovery Cycles (Demarcated Exception Enclave [L1-016])
        enclave_cycle = [c for c in viability.error_recovery_cycles if "type_mismatch_enclave" in c["error_state"]]
        self.assertGreater(len(enclave_cycle), 0)
        self.assertTrue(all(c["has_recovery"] for c in enclave_cycle))

        # 7. Phase 6: Substrate & Anti-Mock Audit
        self.assertTrue(artifacts.substrate_lint_result.clean_slate_passed)
        self.assertTrue(artifacts.substrate_lint_result.anti_mock_passed)
        self.assertTrue(artifacts.substrate_lint_result.visual_dignity_passed)
        self.assertTrue(artifacts.substrate_lint_result.passed)

        # 8. Phase 7: Mandatory Post-Emission Runtime Execution Check [NEG-G1B-001]
        self.assertIsNotNone(artifacts.post_emission_report)
        pe = artifacts.post_emission_report
        self.assertTrue(pe.is_verified)
        self.assertTrue(pe.manifest_verified)
        self.assertGreaterEqual(pe.tests_passed, 5)
        self.assertTrue(pe.witness_signature.startswith("WITNESS_PE_"))

        # 9. Thermodynamic Cost Allocator & Protected Capital [L1-G2B-004]
        self.assertIsNotNone(artifacts.cost_allocator)
        expected_protected = int(artifacts.cost_allocator.capital.total_budget * 0.40)
        self.assertEqual(artifacts.cost_allocator.capital.protected_capital, expected_protected)
        total_spent = (
            artifacts.cost_allocator.capital.spent_protected
            + artifacts.cost_allocator.capital.spent_exploratory
        )
        self.assertGreater(total_spent, 0)

        # 10. Dynamic Weighted Recursion & Telemetry [L1-G2B-003]
        self.assertIsNotNone(artifacts.recursion_root)
        self.assertGreaterEqual(len(artifacts.recursion_root.children), 2)
        def get_tree_max_depth(node):
            if not node.children:
                return node.depth
            return max([node.depth] + [get_tree_max_depth(c) for c in node.children])
        max_depth = get_tree_max_depth(artifacts.recursion_root)
        self.assertGreaterEqual(max_depth, 3)

        # 11. Prescribed Subagent Taxonomy Consideration
        expected_taxonomy = {
            WorkerType.ORCHESTRATOR,
            WorkerType.RESEARCH,
            WorkerType.SYNTHESIS,
            WorkerType.ANTI_MOCK_LINTER,
            WorkerType.MODEL_CHECKER,
            WorkerType.STRUCTURAL_REGULATOR,
            WorkerType.USABILITY_AUDITOR,
            WorkerType.ADVERSARIAL_FALSIFIER,
            WorkerType.SUBSTRATE_RUNNER,
        }
        def verify_node_evaluates_all_subagents(node):
            if node.selection_decisions:
                node_evaluated_types = {d.worker_type for d in node.selection_decisions}
                self.assertEqual(
                    node_evaluated_types,
                    expected_taxonomy,
                    f"Node {node.name} did not consider full taxonomy! Missing: {expected_taxonomy - node_evaluated_types}"
                )
            for c in node.children:
                verify_node_evaluates_all_subagents(c)

        verify_node_evaluates_all_subagents(artifacts.recursion_root)

        # 12. Token Accounting Integrity: Exact 120,000 budget scaling
        cost_summary = artifacts.cost_allocator.get_summary()
        self.assertEqual(cost_summary["total_budget"], 120_000)
        self.assertEqual(cost_summary["protected_reserved"], 48_000)
        self.assertEqual(cost_summary["exploratory_reserved"], 72_000)
        self.assertLessEqual(cost_summary["protected_spent"], cost_summary["protected_reserved"])
        self.assertLessEqual(cost_summary["exploratory_spent"], cost_summary["exploratory_reserved"])

        print("\n=== SYSTEM G2b COMPILATION SUCCESS: AXIOMA JOY ===")
        print(f"Anti-Mock Linter: PASSED (anti_mock={artifacts.substrate_lint_result.anti_mock_passed}, clean_slate={artifacts.substrate_lint_result.clean_slate_passed}, visual_dignity={artifacts.substrate_lint_result.visual_dignity_passed})")
        print(f"Structural Regulator: PASSED (Tier 1 structural axioms compliant)")
        print(f"Model Checker: PASSED ({model_result.total_states} states, {model_result.total_edges} transitions, {len(model_result.covering_paths)} covering paths)")
        print(f"Usability Auditor: PASSED (Tier 2 heuristics compliant)")
        print(f"Adversarial Falsifier: PASSED ({len(model_result.negative_test_cases)} negative assertions)")
        print(f"Steps to Value: {viability.steps_to_value} steps (Budget: {viability.max_budget})")
        print(f"Path to Value: {' -> '.join(viability.shortest_path_to_value)}")
        print(f"Multi-Tier Gate: {artifacts.multi_tier_result.audit_summary}")
        print(f"Substrate Runner (Post-Emission): {pe.tests_passed} tests passed (Witness: {pe.witness_signature})")
        print(f"Execution DAG written to: {artifacts.recursion_tree_path}")
        print(f"Telemetry Dashboard written to: {artifacts.telemetry_dashboard_path}")


if __name__ == "__main__":
    unittest.main()
