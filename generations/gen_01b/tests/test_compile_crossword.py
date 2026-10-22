"""Integration test compiling Axioma Crossword through the System G1b Compiler."""

import unittest

from g1b_compiler.engine import SystemG1bCompiler
from g1b_compiler.crossword_spec import (
    build_crossword_semantic_ir, build_crossword_statechart_ir, build_crossword_contract_ir
)


class TestCompileCrossword(unittest.TestCase):

    def test_full_crossword_compilation_pipeline(self):
        compiler = SystemG1bCompiler()
        semantic_ir = build_crossword_semantic_ir()
        statechart_ir = build_crossword_statechart_ir()
        contract_ir = build_crossword_contract_ir()

        from pathlib import Path
        output_dir = Path(__file__).parent.parent / "apps" / "axioma_crossword"

        # Run compilation with concrete physical emission
        artifacts = compiler.compile(
            semantic_ir=semantic_ir,
            statechart_ir=statechart_ir,
            contract_ir=contract_ir,
            target_output_dir=output_dir,
            max_steps_to_value=3,
            port=8094
        )

        # Verify physical code emission
        self.assertGreaterEqual(len(artifacts.emitted_files), 7)
        self.assertTrue((output_dir / "static" / "index.html").exists())
        self.assertTrue((output_dir / "static" / "machine.js").exists())
        self.assertTrue((output_dir / "static" / "app.js").exists())
        self.assertTrue((output_dir / "static" / "style.css").exists())
        self.assertTrue((output_dir / "server.py").exists())
        self.assertTrue((output_dir / "app.json").exists())

        # 1. Structural Regulation Audit Check
        self.assertTrue(artifacts.regulation_result.is_compliant)

        # 2. Model Checking Verification
        model_result = artifacts.model_check_result
        self.assertTrue(model_result.is_valid)
        self.assertEqual(len(model_result.unreachable_states), 0)
        self.assertGreater(model_result.total_edges, 15)
        self.assertGreater(len(model_result.covering_paths), 0)

        # 3. Viability Gate Check (Steps to Value)
        viability = artifacts.viability_report
        self.assertTrue(viability.passed)
        # From solving -> dissecting.viewing or solving.completed is <= 3 steps
        self.assertLessEqual(viability.steps_to_value, 3)

        # 4. Error Recovery Cycles
        error_cycles = [c for c in viability.error_recovery_cycles if "synthesizing.error" in c["error_state"]]
        self.assertGreater(len(error_cycles), 0)
        self.assertTrue(all(c["has_recovery"] for c in error_cycles))

        # 5. Clean-Slate Substrate Audit
        self.assertTrue(artifacts.substrate_lint_result.clean_slate_passed)

        # 6. Mandatory Post-Emission Runtime Execution Check [NEG-G1B-001]
        self.assertIsNotNone(artifacts.post_emission_report)
        pe = artifacts.post_emission_report
        self.assertTrue(pe.is_verified)
        self.assertTrue(pe.manifest_verified)
        self.assertGreaterEqual(pe.tests_passed, 4)
        self.assertTrue(pe.witness_signature.startswith("WITNESS_PE_"))

        print("\n=== SYSTEM G1b COMPILATION SUCCESS: AXIOMA CROSSWORD ===")
        print(f"Total States: {model_result.total_states}")
        print(f"Total Transitions Verified: {model_result.total_edges}")
        print(f"Covering Paths Traversed: {len(model_result.covering_paths)}")
        print(f"Negative Assertions Synthesized: {len(model_result.negative_test_cases)}")
        print(f"Steps to Value: {viability.steps_to_value} steps (Budget: {viability.max_budget})")
        print(f"Path to Value: {' -> '.join(viability.shortest_path_to_value)}")
        print(f"Post-Emission Tests Executed on Substrate: {pe.tests_passed} (Witness: {pe.witness_signature})")


if __name__ == "__main__":
    unittest.main()
