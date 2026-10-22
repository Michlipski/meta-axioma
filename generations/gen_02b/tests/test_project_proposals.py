"""Unit tests for the Project Proposal System & Bounded Token Budgeting in System G2b."""

import json
from pathlib import Path
import tempfile
import unittest

from g2b_compiler.negotiation.proposals import (
    ProposalScopeTier,
    ProjectProposalDossier,
    MIN_BUDGET_FLOOR,
    MAX_SAFETY_BUDGET,
    PROTECTED_CAPITAL_RATIO,
)
from g2b_compiler.negotiation.proposal_synthesizer import ProjectProposalSynthesizer
from g2b_compiler.recursion.tree_visualizer import RecursionTreeVisualizer
from g2b_compiler.recursion.models import WorkerType, RecursionNode


class TestProjectProposalProtocol(unittest.TestCase):
    """Tests Option 3 Hybrid Model proposal synthesis and axiomatic constraints."""

    def setUp(self):
        self.synthesizer = ProjectProposalSynthesizer()
        self.pitch = (
            "A fast, distraction-free, local-first vocabulary and spaced repetition studio. "
            "Type just the word -> auto-hydrate definition, pronunciation, and example. "
            "Bite-sized daily reviews with adaptive spaced repetition, 1-tap undo, multi-deck tagging, "
            "retention curve analytics, and calm local-first sync."
        )

    def test_axiomatic_bounding_clamps_extremes(self):
        """Verifies that raw estimates are strictly bounded into [10,000, 1,000,000]."""
        # Lower bound clamping
        self.assertEqual(self.synthesizer.clamp_budget(100), MIN_BUDGET_FLOOR)
        self.assertEqual(self.synthesizer.clamp_budget(9_999), MIN_BUDGET_FLOOR)
        self.assertEqual(self.synthesizer.clamp_budget(10_000), 10_000)

        # Upper bound clamping
        self.assertEqual(self.synthesizer.clamp_budget(1_000_000), 1_000_000)
        self.assertEqual(self.synthesizer.clamp_budget(1_000_001), MAX_SAFETY_BUDGET)
        self.assertEqual(self.synthesizer.clamp_budget(50_000_000), MAX_SAFETY_BUDGET)

        # In-range preservation
        self.assertEqual(self.synthesizer.clamp_budget(50_000), 50_000)
        self.assertEqual(self.synthesizer.clamp_budget(250_000), 250_000)

    def test_proposal_tier_capital_partition_invariant(self):
        """Enforces that 40% protected / 60% exploratory capital invariant is mathematically exact."""
        for budget in [10_000, 25_000, 100_000, 350_000, 750_000, 1_000_000]:
            clamped = self.synthesizer.clamp_budget(budget)
            tier = ProposalScopeTier(
                tier_id="test_tier",
                title="Test Tier",
                target_persona_fit="Test persona",
                included_features=["Feature A"],
                deferred_features=["Feature B"],
                statechart_complexity="8-state",
                verification_depth="Baseline",
                raw_estimated_tokens=budget,
                bounded_token_budget=clamped,
                protected_capital=int(clamped * PROTECTED_CAPITAL_RATIO),
                exploratory_capital=clamped - int(clamped * PROTECTED_CAPITAL_RATIO),
                fractional_allocation={"worker": 1.0},
                rationale="Testing capital partition"
            )
            # Invariant check
            expected_protected = int(clamped * 0.40)
            expected_exploratory = clamped - expected_protected
            self.assertEqual(tier.protected_capital, expected_protected)
            self.assertEqual(tier.exploratory_capital, expected_exploratory)
            self.assertEqual(tier.protected_capital + tier.exploratory_capital, clamped)
            self.assertGreaterEqual(tier.bounded_token_budget, MIN_BUDGET_FLOOR)
            self.assertLessEqual(tier.bounded_token_budget, MAX_SAFETY_BUDGET)

    def test_out_of_bounds_proposal_tier_raises_error(self):
        """Verifies that initializing ProposalScopeTier outside [10k, 1M] raises ValueError."""
        with self.assertRaises(ValueError):
            ProposalScopeTier(
                tier_id="invalid_low",
                title="Invalid Low",
                target_persona_fit="None",
                included_features=[],
                deferred_features=[],
                statechart_complexity="",
                verification_depth="",
                raw_estimated_tokens=5000,
                bounded_token_budget=5000,  # Below 10,000 floor
                protected_capital=2000,
                exploratory_capital=3000,
                fractional_allocation={},
                rationale=""
            )

        with self.assertRaises(ValueError):
            ProposalScopeTier(
                tier_id="invalid_high",
                title="Invalid High",
                target_persona_fit="None",
                included_features=[],
                deferred_features=[],
                statechart_complexity="",
                verification_depth="",
                raw_estimated_tokens=2_000_000,
                bounded_token_budget=2_000_000,  # Above 1,000,000 ceiling
                protected_capital=800_000,
                exploratory_capital=1_200_000,
                fractional_allocation={},
                rationale=""
            )

    def test_synthesizer_generates_comprehensive_spectrum(self):
        """Verifies synthesizer formulates 4 distinct tiers spanning the [10k, 1M] range."""
        dossier = self.synthesizer.synthesize_proposals(
            app_id="axioma_lexis",
            elevator_pitch=self.pitch,
            research_summary="SM-2 curve calibrated, Nielsen-Norman verified."
        )

        self.assertEqual(dossier.app_id, "axioma_lexis")
        self.assertEqual(len(dossier.proposals), 4)

        tier_ids = [p.tier_id for p in dossier.proposals]
        self.assertIn("tier_lean", tier_ids)
        self.assertIn("tier_balanced", tier_ids)
        self.assertIn("tier_comprehensive", tier_ids)
        self.assertIn("tier_maximal", tier_ids)

        budgets = [p.bounded_token_budget for p in dossier.proposals]
        self.assertEqual(budgets[0], 25_000)
        self.assertEqual(budgets[1], 100_000)
        self.assertEqual(budgets[2], 350_000)
        self.assertEqual(budgets[3], 1_000_000)

        # Default active selection should be tier_balanced
        self.assertEqual(dossier.selected_proposal_id, "tier_balanced")
        self.assertIsNotNone(dossier.selected_proposal)
        self.assertEqual(dossier.selected_proposal.tier_id, "tier_balanced")

        # Verify all tiers have workload breakdowns and token justifications
        for p in dossier.proposals:
            self.assertIsNotNone(p.workload_breakdown)
            self.assertIn("research_and_grounding", p.workload_breakdown)
            self.assertIn("architecture_and_ir", p.workload_breakdown)
            self.assertIn("code_and_ast_emission", p.workload_breakdown)
            self.assertIn("model_checking_reachability", p.workload_breakdown)
            self.assertIn("falsification_and_substrate", p.workload_breakdown)
            # Protected capital invariant check
            protected_sum = p.workload_breakdown["model_checking_reachability"] + p.workload_breakdown["falsification_and_substrate"]
            self.assertEqual(protected_sum, p.protected_capital)
            self.assertGreater(len(p.token_justification), 50)
            self.assertIn("Protected Capital", p.token_justification)

        # Verify domain-specific dynamic derivation: another app has different token amounts than axioma_lexis
        dossier_bench = self.synthesizer.synthesize_proposals(
            app_id="axioma_benchmark",
            elevator_pitch="Benchmark app with multi-domain state orchestration.",
        )
        bench_budgets = [p.bounded_token_budget for p in dossier_bench.proposals]
        self.assertNotEqual(bench_budgets[0], budgets[0])  # 28,330 vs 25,000
        self.assertNotEqual(bench_budgets[1], budgets[1])  # 120,000 vs 100,000

    def test_custom_budget_and_explicit_tier_selection(self):
        """Tests selection of tier via explicit proposal ID or matching custom budget."""
        # Explicit ID selection
        dossier_explicit = self.synthesizer.synthesize_proposals(
            app_id="axioma_lexis",
            elevator_pitch=self.pitch,
            selected_proposal_id="tier_comprehensive"
        )
        self.assertEqual(dossier_explicit.selected_proposal_id, "tier_comprehensive")
        self.assertEqual(dossier_explicit.selected_proposal.tier_id, "tier_comprehensive")
        self.assertEqual(dossier_explicit.selected_proposal.bounded_token_budget, 350_000)

        # Budget matching: 25k -> tier_lean
        dossier_lean = self.synthesizer.synthesize_proposals(
            app_id="axioma_lexis",
            elevator_pitch=self.pitch,
            custom_budget=25_000
        )
        self.assertEqual(dossier_lean.selected_proposal_id, "tier_lean")

        # Budget matching: 1,000,000 -> tier_maximal
        dossier_max = self.synthesizer.synthesize_proposals(
            app_id="axioma_lexis",
            elevator_pitch=self.pitch,
            custom_budget=1_000_000
        )
        self.assertEqual(dossier_max.selected_proposal_id, "tier_maximal")

    def test_proposals_telemetry_and_markdown_emission(self):
        """Tests recording proposals to JSONL and emitting the comparison markdown report."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            visualizer = RecursionTreeVisualizer(run_id="test_proposal_run", telemetry_dir=tmppath)
            dossier = self.synthesizer.synthesize_proposals(
                app_id="axioma_lexis",
                elevator_pitch=self.pitch,
                selected_proposal_id="tier_balanced"
            )

            # Record telemetry
            visualizer.record_project_proposals(dossier)
            proposals_jsonl = tmppath / "project_proposals.jsonl"
            self.assertTrue(proposals_jsonl.exists())
            lines = proposals_jsonl.read_text(encoding="utf-8").strip().split("\n")
            self.assertEqual(len(lines), 4)
            for line in lines:
                entry = json.loads(line)
                self.assertEqual(entry["run_id"], "test_proposal_run")
                self.assertEqual(entry["app_id"], "axioma_lexis")
                self.assertIn(entry["tier_id"], ["tier_lean", "tier_balanced", "tier_comprehensive", "tier_maximal"])
                if entry["tier_id"] == "tier_balanced":
                    self.assertTrue(entry["selected"])
                else:
                    self.assertFalse(entry["selected"])

            # Emit report
            report_path = tmppath / "project_proposals.md"
            visualizer.emit_proposals_report(dossier, report_path)
            self.assertTrue(report_path.exists())
            report_text = report_path.read_text(encoding="utf-8")
            self.assertIn("System G2b Project Proposal Dossier", report_text)
            self.assertIn("Lean Core MVP", report_text)
            self.assertIn("Production Balanced Studio", report_text)
            self.assertIn("High-Assurance Comprehensive Studio", report_text)
            self.assertIn("Maximalist Safety-Cap Enterprise Studio", report_text)
            self.assertIn("Task-to-Token Workload Allocation", report_text)
            self.assertIn("Why This Token Budget Fits the Workload", report_text)
            self.assertIn("1,000,000 tok", report_text)
            self.assertIn("SELECTED", report_text)


if __name__ == "__main__":
    unittest.main()
