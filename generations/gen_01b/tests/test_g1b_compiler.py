import tempfile
import unittest
from pathlib import Path

from g1b_compiler.ir.semantic_ir import SemanticDomainIR, EntitySpec, EntityField, FieldType, DomainCapability, DomainInvariant
from g1b_compiler.ir.statechart_ir import StatechartIR, StateNode, Transition, EventSpec
from g1b_compiler.ir.contract_ir import DualBoundaryContractIR, NounContract, VerbContract
from g1b_compiler.verification.model_checker import StatechartModelChecker
from g1b_compiler.verification.viability_gate import ViabilityGate
from g1b_compiler.verification.substrate_linter import SubstrateLinter
from g1b_compiler.verification.post_emission_gate import PostEmissionGate, MANDATORY_MANIFEST
from g1b_compiler.isolation.regulator import StructuralAxiomRegulator, EpistemicIsolationBreachError
from g1b_compiler.isolation.falsifier import AdversarialFalsifier
from g1b_compiler.engine import (
    SystemG1bCompiler,
    CompilationVerificationFailure,
    PostEmissionExecutionFailure,
    PhantomEmissionViolation,
)
from g1b_compiler.lexis_spec import build_lexis_semantic_ir, build_lexis_contract_ir


class TestSystemG1bCompiler(unittest.TestCase):

    def setUp(self):
        self.semantic_ir = build_lexis_semantic_ir()
        self.contract_ir = build_lexis_contract_ir()
        self.generic_semantic_ir = SemanticDomainIR(
            app_id="test_app",
            title="Test App",
            tagline="A generic test application",
            persona="Developer",
            jtbd_summary="Test the core compilation lifecycle.",
            entities=[],
            capabilities=[DomainCapability(name="TestCapability", description="Core testing action")],
            invariants=[],
            initial_clean_seeds={}
        )
        # Create a valid test statechart: idle -> loading -> ready -> (error -> idle)
        self.valid_machine = StatechartIR(
            machine_id="test_machine",
            initial="idle",
            states={
                "idle": StateNode(
                    id="idle",
                    on={
                        "START": Transition(target="loading", event="START"),
                    }
                ),
                "loading": StateNode(
                    id="loading",
                    on={
                        "SUCCESS": Transition(target="ready", event="SUCCESS"),
                        "FAIL": Transition(target="error", event="FAIL"),
                    }
                ),
                "ready": StateNode(
                    id="ready",
                    meta={"is_value_state": True},
                    on={
                        "RESET": Transition(target="idle", event="RESET"),
                    }
                ),
                "error": StateNode(
                    id="error",
                    meta={"is_error_state": True},
                    on={
                        "RETRY": Transition(target="loading", event="RETRY"),
                        "CANCEL": Transition(target="idle", event="CANCEL"),
                    }
                ),
            },
            events={
                "START": EventSpec(name="START"),
                "SUCCESS": EventSpec(name="SUCCESS"),
                "FAIL": EventSpec(name="FAIL"),
                "RESET": EventSpec(name="RESET"),
                "RETRY": EventSpec(name="RETRY"),
                "CANCEL": EventSpec(name="CANCEL"),
            }
        )

    def test_model_checker_reachability_and_edge_coverage(self):
        checker = StatechartModelChecker(self.valid_machine)
        result = checker.run_full_check()

        self.assertTrue(result.is_valid)
        self.assertEqual(len(result.unreachable_states), 0)
        self.assertEqual(result.total_states, 4)
        self.assertGreaterEqual(len(result.covering_paths), 1)
        self.assertGreater(len(result.negative_test_cases), 0)

    def test_model_checker_detects_unreachable_state(self):
        # Add a disconnected orphan state
        broken_machine = StatechartIR(
            machine_id="broken_machine",
            initial="idle",
            states={
                "idle": StateNode(
                    id="idle",
                    on={"START": Transition(target="ready", event="START")}
                ),
                "ready": StateNode(id="ready"),
                "orphan": StateNode(id="orphan")  # Unreachable!
            },
            events={"START": EventSpec(name="START")}
        )
        checker = StatechartModelChecker(broken_machine)
        result = checker.run_full_check()

        self.assertFalse(result.is_valid)
        self.assertIn("orphan", result.unreachable_states)

    def test_viability_gate_steps_to_value(self):
        gate = ViabilityGate(self.valid_machine, max_steps_to_value=2)
        report = gate.evaluate()

        self.assertTrue(report.passed)
        # idle -> loading -> ready is 2 steps
        self.assertEqual(report.steps_to_value, 2)
        self.assertEqual(report.shortest_path_to_value, ["idle", "loading", "ready"])

    def test_viability_gate_flags_budget_exceeded(self):
        # Budget of 1 step will fail since ready requires 2 steps
        strict_gate = ViabilityGate(self.valid_machine, max_steps_to_value=1)
        report = strict_gate.evaluate()

        self.assertFalse(report.passed)
        self.assertTrue(any("budget" in v for v in report.violations))

    def test_epistemic_isolation_enforcement(self):
        regulator = StructuralAxiomRegulator()
        with self.assertRaises(EpistemicIsolationBreachError):
            regulator.guard_code_emission(proposed_code="const x = 1;")

        contract_ir = DualBoundaryContractIR(app_id="test")
        falsifier = AdversarialFalsifier(self.valid_machine, contract_ir)
        with self.assertRaises(EpistemicIsolationBreachError):
            falsifier.propose_candidate_code("function App() {}")

    def test_substrate_linter(self):
        linter = SubstrateLinter()

        # Test anti-mock detection
        mock_code = "const banner = document.getElementById('simulated-notification');"
        violations = linter.audit_code(mock_code)
        self.assertTrue(any("Anti-Mock Failure" in v for v in violations))

        # Test clean-slate seed check
        dirty_seeds = {"words": [{"word": "foo", "def": "bar"}]}
        seed_violations = linter.audit_clean_slate_seeds(dirty_seeds)
        self.assertTrue(any("Clean-Slate Failure" in v for v in seed_violations))

        clean_seeds = {"words": [{"word": "epistemic", "def": "relating to knowledge"}]}
        clean_violations = linter.audit_clean_slate_seeds(clean_seeds)
        self.assertEqual(len(clean_violations), 0)

    def test_phantom_emission_violation_raised_when_target_omitted(self):
        compiler = SystemG1bCompiler()
        with self.assertRaises(PhantomEmissionViolation):
            compiler.compile(
                semantic_ir=self.generic_semantic_ir,
                statechart_ir=self.valid_machine,
                contract_ir=self.contract_ir,
                target_output_dir=None,
                allow_dry_run=False
            )

    def test_dry_run_allowed_when_explicitly_flagged(self):
        compiler = SystemG1bCompiler()
        artifacts = compiler.compile(
            semantic_ir=self.generic_semantic_ir,
            statechart_ir=self.valid_machine,
            contract_ir=self.contract_ir,
            target_output_dir=None,
            allow_dry_run=True
        )
        self.assertIsNone(artifacts.post_emission_report)
        self.assertEqual(len(artifacts.emitted_files), 0)

    def test_phase_0_domain_baseline_violation_on_missing_table_stakes(self):
        compiler = SystemG1bCompiler()
        from g1b_compiler.domain_research.models import DomainBaselineViolation
        # Attempting to compile an SRS app without required milestone raises DomainBaselineViolation
        with self.assertRaises(DomainBaselineViolation) as ctx:
            compiler.compile(
                semantic_ir=self.semantic_ir,
                statechart_ir=self.valid_machine,
                contract_ir=self.contract_ir,
                target_output_dir=None,
                allow_dry_run=True
            )
        self.assertIn("completion_milestone", str(ctx.exception))

    def test_post_emission_gate_catches_missing_manifest_file(self):
        gate = PostEmissionGate()
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            # Create all except index.html
            for rel in MANDATORY_MANIFEST:
                if rel == "static/index.html":
                    continue
                f = tmppath / rel
                f.parent.mkdir(parents=True, exist_ok=True)
                f.write_text("dummy content", encoding="utf-8")

            with self.assertRaises(PostEmissionExecutionFailure) as ctx:
                gate.verify_manifest(tmppath)
            self.assertIn("static/index.html", str(ctx.exception))

    def test_post_emission_gate_catches_empty_manifest_file(self):
        gate = PostEmissionGate()
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            for rel in MANDATORY_MANIFEST:
                f = tmppath / rel
                f.parent.mkdir(parents=True, exist_ok=True)
                # Write 0 bytes to server.py
                if rel == "server.py":
                    f.write_text("", encoding="utf-8")
                else:
                    f.write_text("non-empty content", encoding="utf-8")

            with self.assertRaises(PostEmissionExecutionFailure) as ctx:
                gate.verify_manifest(tmppath)
            self.assertIn("server.py", str(ctx.exception))
            self.assertIn("0 bytes", str(ctx.exception))

    def test_post_emission_gate_catches_runtime_test_failure(self):
        gate = PostEmissionGate()
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            for rel in MANDATORY_MANIFEST:
                f = tmppath / rel
                f.parent.mkdir(parents=True, exist_ok=True)
                f.write_text("content", encoding="utf-8")

            # Write a failing test in tests/test_failing.py
            fail_test = (
                "import unittest\n"
                "class FailingTest(unittest.TestCase):\n"
                "    def test_failure(self):\n"
                "        self.assertEqual(1, 2)\n"
            )
            (tmppath / "tests" / "test_failing.py").write_text(fail_test, encoding="utf-8")

            with self.assertRaises(PostEmissionExecutionFailure) as ctx:
                gate.verify_and_execute(tmppath)
            self.assertIn("Emitted application failed runtime test execution", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
