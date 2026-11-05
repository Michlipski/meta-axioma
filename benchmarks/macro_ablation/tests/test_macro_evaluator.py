"""Integration tests for MacroEvaluationGauntlet and MacroRunner."""

from pathlib import Path
import shutil
import unittest

from benchmarks.macro_ablation.archetypes import axioma_kv
from benchmarks.macro_ablation.domain_models import (
    AblationMode,
    MacroBenchmarkReport,
    MacroScorecard,
)
from benchmarks.macro_ablation.macro_evaluator import MacroEvaluationGauntlet
from benchmarks.macro_ablation.macro_runner import MacroRunner


class TestMacroEvaluatorIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.workspace_root = Path(__file__).resolve().parent.parent.parent.parent
        cls.test_dir = cls.workspace_root / ".scratch" / "test_macro_integration"
        cls.test_dir.mkdir(parents=True, exist_ok=True)
        cls.gauntlet = MacroEvaluationGauntlet(liveness_timeout=3.0, chaos_timeout=5.0)
        cls.kv_arch = axioma_kv.get_archetype()

    @classmethod
    def tearDownClass(cls):
        if cls.test_dir.exists():
            shutil.rmtree(cls.test_dir, ignore_errors=True)

    def test_full_g4b_evaluation(self):
        app_dir = self.test_dir / "kv_full_g4b"
        axioma_kv.generate_candidate_app(AblationMode.FULL_G4B, app_dir)

        scorecard = self.gauntlet.evaluate_app(app_dir, self.kv_arch, AblationMode.FULL_G4B)
        self.assertTrue(scorecard.tier0_liveness.passed)
        self.assertEqual(scorecard.tier0_multiplier, 1.0)
        self.assertGreaterEqual(scorecard.composite_score, 80.0)
        self.assertEqual(scorecard.composite_score, scorecard.graded_score)

    def test_smoke_ablation_forces_zero_score(self):
        # Ablation 4 has an import crash -> must get identically 0.0 composite score
        app_dir = self.test_dir / "kv_smoke_fail"
        axioma_kv.generate_candidate_app(AblationMode.WO_SUBPROCESS_SMOKE, app_dir)

        scorecard = self.gauntlet.evaluate_app(app_dir, self.kv_arch, AblationMode.WO_SUBPROCESS_SMOKE)
        self.assertFalse(scorecard.tier0_liveness.passed)
        self.assertEqual(scorecard.tier0_multiplier, 0.0)
        self.assertEqual(scorecard.composite_score, 0.0)

    def test_macro_runner_archetype_run(self):
        runner = MacroRunner(workspace_root=self.workspace_root)
        # Run single archetype to keep test quick
        report = runner.run_benchmark(
            archetype_ids=["axioma_kv"],
            modes=[AblationMode.FULL_G4B, AblationMode.WO_SUBPROCESS_SMOKE],
        )
        self.assertIsInstance(report, MacroBenchmarkReport)
        self.assertEqual(len(report.scorecards), 2)
        self.assertIn("axioma_kv", report.summary_matrix)
        self.assertGreaterEqual(report.summary_matrix["axioma_kv"]["full_g4b"], 80.0)
        self.assertEqual(report.summary_matrix["axioma_kv"]["wo_subprocess_smoke"], 0.0)

        # Test Markdown rendering
        md_text = report.to_markdown()
        self.assertIn("# Axioma Macro-Bench", md_text)
        self.assertIn("axioma_kv", md_text)
        self.assertIn("Tier 0 Liveness Impact Note", md_text)

        # Test HTML Dashboard emission
        dash_file = self.test_dir / "test_dashboard.html"
        runner.generate_dashboard_html(report, dash_file)
        self.assertTrue(dash_file.exists())
        self.assertGreater(dash_file.stat().st_size, 500)


if __name__ == "__main__":
    unittest.main()
