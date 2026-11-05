"""Unit tests for Macro-Bench evaluators (Passes 1–5)."""

from pathlib import Path
import shutil
import unittest

from benchmarks.macro_ablation.archetypes import axioma_kv
from benchmarks.macro_ablation.domain_models import AblationMode
from benchmarks.macro_ablation.evaluators import (
    ChaosEvaluator,
    EfficiencyEvaluator,
    HermeticEvaluator,
    SpecFidelityEvaluator,
    StatechartEvaluator,
)


class TestEvaluators(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.workspace_root = Path(__file__).resolve().parent.parent.parent.parent
        cls.test_dir = cls.workspace_root / ".scratch" / "test_evaluators"
        cls.test_dir.mkdir(parents=True, exist_ok=True)
        cls.kv_arch = axioma_kv.get_archetype()

        # Pre-generate candidate apps
        cls.app_g4b = cls.test_dir / "app_kv_g4b"
        axioma_kv.generate_candidate_app(AblationMode.FULL_G4B, cls.app_g4b)

        cls.app_llm = cls.test_dir / "app_kv_llm"
        axioma_kv.generate_candidate_app(AblationMode.FLAT_PROMPT_LLM, cls.app_llm)

        cls.app_flawed = cls.test_dir / "app_kv_flawed"
        axioma_kv.generate_candidate_app(AblationMode.WO_CONTRACTS_SMT, cls.app_flawed)

        cls.app_bad_ast = cls.test_dir / "app_kv_bad_ast"
        axioma_kv.generate_candidate_app(AblationMode.WO_AST_AUDITORS, cls.app_bad_ast)

    @classmethod
    def tearDownClass(cls):
        if cls.test_dir.exists():
            shutil.rmtree(cls.test_dir, ignore_errors=True)

    def test_spec_fidelity_evaluator(self):
        evaluator = SpecFidelityEvaluator(weight=0.25)

        # 1. Compliant Full G4b App
        res_g4b = evaluator.evaluate(self.app_g4b, self.kv_arch)
        self.assertTrue(res_g4b.passed)
        self.assertGreaterEqual(res_g4b.raw_score, 80.0)
        self.assertGreater(res_g4b.details["verb_coverage_pct"], 75.0)

        # 2. Defective Flat LLM App (missing verbs & models)
        res_llm = evaluator.evaluate(self.app_llm, self.kv_arch)
        self.assertLess(res_llm.raw_score, res_g4b.raw_score)

    def test_statechart_evaluator(self):
        evaluator = StatechartEvaluator(weight=0.20)

        # 1. Compliant App with valid guards
        res_g4b = evaluator.evaluate(self.app_g4b, self.kv_arch)
        self.assertTrue(res_g4b.passed)
        self.assertGreaterEqual(res_g4b.raw_score, 85.0)

        # 2. Flawed Contract App (allows illegal transitions)
        res_flawed = evaluator.evaluate(self.app_flawed, self.kv_arch)
        self.assertLess(res_flawed.raw_score, res_g4b.raw_score)

    def test_hermetic_evaluator(self):
        evaluator = HermeticEvaluator(weight=0.20)

        # 1. Clean App
        res_g4b = evaluator.evaluate(self.app_g4b, self.kv_arch)
        self.assertTrue(res_g4b.passed)
        self.assertEqual(res_g4b.raw_score, 100.0)

        # 2. App with Banned eval() and /tmp
        res_bad = evaluator.evaluate(self.app_bad_ast, self.kv_arch)
        self.assertFalse(res_bad.passed)
        self.assertLessEqual(res_bad.raw_score, 50.0)
        self.assertGreater(res_bad.details["violations_count"], 0)

    def test_efficiency_evaluator(self):
        evaluator = EfficiencyEvaluator(weight=0.20)
        res_g4b = evaluator.evaluate(self.app_g4b, self.kv_arch)
        self.assertTrue(res_g4b.passed)
        self.assertGreaterEqual(res_g4b.raw_score, 60.0)
        self.assertGreater(res_g4b.details["total_loc"], 50)

    def test_chaos_evaluator(self):
        evaluator = ChaosEvaluator(weight=0.15, timeout_sec=5.0)

        # 1. Compliant App handles bad JSON and bursts gracefully
        res_g4b = evaluator.evaluate(self.app_g4b, self.kv_arch)
        self.assertTrue(res_g4b.passed)
        self.assertGreaterEqual(res_g4b.raw_score, 85.0)

        # 2. Flat LLM crashes on malformed JSON
        res_llm = evaluator.evaluate(self.app_llm, self.kv_arch)
        self.assertLess(res_llm.raw_score, res_g4b.raw_score)
        self.assertGreater(res_llm.details["unhandled_crashes"], 0)


if __name__ == "__main__":
    unittest.main()
