"""Permanent Unit & Adversarial Test Suite for Builder-Tester Isolation (SPEC-G4B-BUILDER-001).

Validates:
- EngineSynthesizer role enforcement and builder quarantine (mutation of tests/ prohibited).
- QASynthesizer role boundary (mutation of src/ prohibited) and context sanitization.
- DynamicPersonaBuilder manifests for Quarantined Engine Synthesizer & Adversarial QA Engineer.
- SovereignBuilderKernel dispatch orchestration enforcing segregated subagent roles.
- scripts/atomic_task_guard.py pre-tool hook with synthetic toolCall payloads:
  * Builder mutation in tests/ denied.
  * QA mutation in src/ denied.
  * Co-emission collusion between implementation and test in unsegregated turn detected and denied.
  * Shell redirection interception in run_command.
"""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from generations.gen_04b.services.builder.src import (
    BuilderQuarantineViolation,
    CognitiveRole,
    DynamicPersonaManifest,
    EngineSynthesizer,
    LeafEmissionEvent,
    PhysicalDiskWitness,
    QABoundaryViolation,
    QASynthesizer,
    sanitize_context_for_qa,
    validate_mutation_target,
    validate_qa_target,
)
from generations.gen_04b.services.builder.src.builder_kernel import SovereignBuilderKernel
from generations.gen_04b.services.builder.src.domain_models import ASTNodeType
from generations.gen_04b.services.builder.src.dynamic_persona_builder import DynamicPersonaBuilder
from scripts.atomic_task_guard import (
    check_anti_collusion,
    check_builder_quarantine,
    load_synthesis_turn_log,
    mark_mutation_verified,
    record_synthesis_provenance,
    save_synthesis_turn_log,
)


def find_workspace_root() -> Path:
    """Finds the workspace root directory by looking for repository anchor markers."""
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / ".git").exists() or (parent / "AGENTS.md").exists():
            return parent
    return Path.cwd()


class TestBuilderTesterAdversarialIsolation(unittest.TestCase):
    """Test suite validating SPEC-G4B-BUILDER-001 implementation."""

    def setUp(self):
        self.workspace_root = find_workspace_root()

    # -------------------------------------------------------------------------
    # 1. EngineSynthesizer Quarantine Tests
    # -------------------------------------------------------------------------
    def test_engine_synthesizer_role_and_allowed_targets(self):
        engine = EngineSynthesizer(workspace_root=str(self.workspace_root))
        self.assertEqual(engine.role, CognitiveRole.CORE_ENGINE_SYNTHESIZER)

        allowed_targets = [
            "services/builder/src/engine.py",
            "generations/gen_04b/services/builder/src/module.py",
            "apps/phenoflora/src/server.py",
            "apps/phenoflora/static/index.html",
            "src/core.py",
            "scripts/guard.py",
            ".scratch/temp_buffer.py",
        ]
        for target in allowed_targets:
            validate_mutation_target(target)
            engine.validate_target(target)

    def test_engine_synthesizer_quarantine_violations(self):
        engine = EngineSynthesizer(workspace_root=str(self.workspace_root))

        prohibited_test_targets = [
            "tests/test_something.py",
            "services/builder/tests/test_builder.py",
            "generations/gen_04b/services/builder/tests/test_adversarial_isolation.py",
            "apps/phenoflora/tests/test_server.py",
            "src/engine_test.py",
            "src/test_engine.py",
            "services/research/tests/test_research.py",
        ]
        for target in prohibited_test_targets:
            with self.assertRaises(BuilderQuarantineViolation) as cm:
                validate_mutation_target(target)
            self.assertIn("Builder quarantine strictly prohibits", str(cm.exception))

            with self.assertRaises(BuilderQuarantineViolation):
                engine.validate_target(target)

        # Empty target
        with self.assertRaises(BuilderQuarantineViolation):
            validate_mutation_target("")

        # Out-of-whitelist target
        with self.assertRaises(BuilderQuarantineViolation):
            validate_mutation_target("unauthorized_dir/payload.py")

    def test_engine_synthesizer_recording_and_witness_verification(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            engine = EngineSynthesizer(workspace_root=tmpdir)
            target = "apps/sample/src/kernel.py"
            code = "class SampleKernel:\n    pass\n"

            # Must raise if empty code
            with self.assertRaises(BuilderQuarantineViolation):
                engine.record_emission(target, "")

            # Attempt to record emission to test file raises
            with self.assertRaises(BuilderQuarantineViolation):
                engine.record_emission("apps/sample/tests/test_kernel.py", code)

            # Valid recording
            event = engine.record_emission(target, code, bpe_token_count=10)
            self.assertIsInstance(event, LeafEmissionEvent)
            self.assertTrue(event.leaf_symbol_urn.startswith("urn:axioma:g4b:"))
            self.assertEqual(len(engine.get_emissions()), 1)
            self.assertEqual(len(engine.get_witnesses()), 1)

            # Physically write to disk to test verify_emission
            real_file = Path(tmpdir) / target
            real_file.parent.mkdir(parents=True, exist_ok=True)

            # verify_emission on non-existent file raises
            with self.assertRaises(BuilderQuarantineViolation):
                engine.verify_emission(str(real_file.with_name("nonexistent.py")))

            # Write empty file -> phantom emission violation
            real_file.write_text("", encoding="utf-8")
            with self.assertRaises(BuilderQuarantineViolation) as cm:
                engine.verify_emission(str(real_file))
            self.assertIn("zero-byte phantom emission", str(cm.exception))

            # Write real non-empty file -> succeeds
            real_file.write_text(code, encoding="utf-8")
            witness = engine.verify_emission(str(real_file))
            self.assertIsInstance(witness, PhysicalDiskWitness)
            self.assertEqual(witness.byte_size, len(code.encode("utf-8")))
            self.assertTrue(witness.is_present)

    # -------------------------------------------------------------------------
    # 2. QASynthesizer Role & Boundary Tests
    # -------------------------------------------------------------------------
    def test_qa_synthesizer_role_and_allowed_targets(self):
        qa = QASynthesizer(workspace_root=str(self.workspace_root))
        self.assertEqual(qa.role, CognitiveRole.ADVERSARIAL_QA_ENGINEER)

        allowed_qa = [
            "tests/test_sample.py",
            "services/builder/tests/test_kernel.py",
            "apps/sample/tests/test_app.py",
            ".scratch/temp_test.py",
            "generations/gen_04b/services/builder/tests/test_adversarial_isolation.py",
        ]
        for p in allowed_qa:
            validate_qa_target(p)
            qa.validate_target(p)

    def test_qa_synthesizer_boundary_violations(self):
        qa = QASynthesizer(workspace_root=str(self.workspace_root))

        prohibited_prod_targets = [
            "services/builder/src/engine.py",
            "generations/gen_04b/services/builder/src/module.py",
            "apps/sample/src/main.py",
            "apps/sample/static/style.css",
            "src/core.py",
        ]
        for p in prohibited_prod_targets:
            with self.assertRaises(QABoundaryViolation) as cm:
                validate_qa_target(p)
            self.assertIn("quarantined from modifying production code", str(cm.exception))

            with self.assertRaises(QABoundaryViolation):
                qa.validate_target(p)

        # Non-test files outside allowed patterns
        with self.assertRaises(QABoundaryViolation):
            validate_qa_target("docs/architecture.md")

    def test_qa_context_sanitization(self):
        acceptance_spec = {
            "public_endpoint": "/api/v1/status",
            "expected_status": 200,
            "_private_key": "secret",
            "_internal_secret": "xyz",
            "reasoning": "We chose this shortcut because of Landauer limits",
            "scratchpad": "builder temporary notes",
            "implementation_notes": "Use dictionary caching for performance",
            "internal_state": {"cache_hit": True},
            "private_fields": ["_cache", "_token"],
            "builder_notes": "Do not test boundary case 99",
            "workarounds": "Quick hack for socket bind",
            "shortcuts": "Bypassing formal verification",
            "inner_vars": ["temp1", "temp2"],
            "ast_internals": {"node_id": 10},
            "private_methods": ["_reset()"],
            "source_internals": "private memory map",
            "ast_skeleton": "raw AST dump",
            "mock_stubs": "mocked return",
            "cached_shortcuts": "stale shortcut",
            "nested_config": {
                "_hidden": 42,
                "public_timeout": 5.0,
                "reasoning": "nested reasoning",
            },
        }
        flow_contracts = ["EV_SUBMIT", "EV_VERIFY"]
        public_api_signatures = [
            "def submit_order(order_id: str) -> bool",
            "def _internal_helper() -> None",
            "def query_status() -> dict",
            "class _PrivateParser:",
            "class OrderHandler:",
        ]

        sanitized = sanitize_context_for_qa(acceptance_spec, flow_contracts, public_api_signatures)
        self.assertTrue(sanitized["is_sanitized"])

        spec = sanitized["acceptance_spec"]
        self.assertIn("public_endpoint", spec)
        self.assertIn("expected_status", spec)
        self.assertEqual(spec["public_endpoint"], "/api/v1/status")

        # Verify all banned and private keys stripped
        for stripped_key in [
            "_private_key", "_internal_secret", "reasoning", "scratchpad",
            "implementation_notes", "internal_state", "private_fields",
            "builder_notes", "workarounds", "shortcuts", "inner_vars",
            "ast_internals", "private_methods", "source_internals",
            "ast_skeleton", "mock_stubs", "cached_shortcuts",
        ]:
            self.assertNotIn(stripped_key, spec, f"Key '{stripped_key}' should have been stripped!")

        # Nested dict check
        self.assertIn("nested_config", spec)
        self.assertNotIn("_hidden", spec["nested_config"])
        self.assertNotIn("reasoning", spec["nested_config"])
        self.assertEqual(spec["nested_config"]["public_timeout"], 5.0)

        # Signatures check
        signatures = sanitized["public_api_signatures"]
        self.assertIn("def submit_order(order_id: str) -> bool", signatures)
        self.assertIn("def query_status() -> dict", signatures)
        self.assertIn("class OrderHandler:", signatures)
        self.assertNotIn("def _internal_helper() -> None", signatures)
        self.assertNotIn("class _PrivateParser:", signatures)

    def test_qa_synthesizer_test_suite_execution(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            qa = QASynthesizer(workspace_root=tmpdir)
            test_file = Path(tmpdir) / "tests" / "test_mini.py"
            test_file.parent.mkdir(parents=True, exist_ok=True)
            test_file.write_text(
                "import unittest\n"
                "class MiniTest(unittest.TestCase):\n"
                "    def test_pass(self):\n"
                "        self.assertTrue(True)\n"
                "if __name__ == '__main__':\n"
                "    unittest.main()\n",
                encoding="utf-8",
            )

            report = qa.execute_test_suite(str(test_file))
            self.assertTrue(report.passed)
            self.assertEqual(report.recovered_fault_count, 1)
            self.assertEqual(len(qa.get_qa_reports()), 1)

            # Test targeting non-existent file
            with self.assertRaises(QABoundaryViolation):
                qa.execute_test_suite(str(Path(tmpdir) / "tests" / "test_missing.py"))

            # Test targeting src raises boundary violation
            with self.assertRaises(QABoundaryViolation):
                qa.execute_test_suite(str(Path(tmpdir) / "src" / "test_mini.py"))

    # -------------------------------------------------------------------------
    # 3. DynamicPersonaBuilder Manifests
    # -------------------------------------------------------------------------
    def test_dynamic_persona_manifests(self):
        # Quarantined Engine Synthesizer Persona
        engine_persona = DynamicPersonaBuilder.create_quarantined_engine_synthesizer_persona()
        self.assertIsInstance(engine_persona, DynamicPersonaManifest)
        self.assertEqual(engine_persona.cognitive_role, CognitiveRole.CORE_ENGINE_SYNTHESIZER.value)
        self.assertEqual(engine_persona.model_tier, "flash")
        self.assertIn("[INV-G4B-CAUSAL-003]", engine_persona.governing_axioms)
        self.assertIn("[SPEC-G4B-BUILDER-001]", engine_persona.governing_axioms)
        self.assertTrue(any("tests/" in b for b in engine_persona.banned_antipatterns))

        engine_params = DynamicPersonaBuilder.to_define_subagent_params(engine_persona)
        self.assertEqual(engine_params["name"], "quarantined-core-engine-synthesizer")
        self.assertTrue(engine_params["enable_write_tools"])
        self.assertFalse(engine_params["enable_mcp_tools"])
        self.assertFalse(engine_params["enable_subagent_tools"])

        # Adversarial QA Persona
        qa_persona = DynamicPersonaBuilder.create_adversarial_qa_persona()
        self.assertIsInstance(qa_persona, DynamicPersonaManifest)
        self.assertEqual(qa_persona.cognitive_role, CognitiveRole.ADVERSARIAL_QA_ENGINEER.value)
        self.assertEqual(qa_persona.model_tier, "flash")
        self.assertIn("[INV-G4B-CAUSAL-003]", qa_persona.governing_axioms)
        self.assertIn("[SPEC-G4B-BUILDER-001]", qa_persona.governing_axioms)
        self.assertIn("[NEG-G1B-002]", qa_persona.governing_axioms)
        self.assertTrue(any("scratchpad" in b for b in qa_persona.banned_antipatterns))
        self.assertTrue(any("src/" in b for b in qa_persona.banned_antipatterns))

        qa_params = DynamicPersonaBuilder.to_define_subagent_params(qa_persona)
        self.assertEqual(qa_params["name"], "adversarial-test-and-byzantine-qa-engineer")
        self.assertTrue(qa_params["enable_write_tools"])
        self.assertFalse(qa_params["enable_mcp_tools"])

    # -------------------------------------------------------------------------
    # 4. SovereignBuilderKernel Role Segregation Dispatch
    # -------------------------------------------------------------------------
    def test_builder_kernel_dispatch_orchestration(self):
        kernel = SovereignBuilderKernel()
        self.assertIsInstance(kernel.engine_synthesizer, EngineSynthesizer)
        self.assertIsInstance(kernel.qa_synthesizer, QASynthesizer)

        # Engine dispatch to prohibited test file raises BuilderQuarantineViolation
        with self.assertRaises(BuilderQuarantineViolation):
            kernel.dispatch_quarantined_engine_synthesizer(
                module_path="tests/test_something.py",
                source_code="pass",
            )

        # QA dispatch to production code raises QABoundaryViolation
        with self.assertRaises(QABoundaryViolation):
            kernel.dispatch_adversarial_qa(
                test_file_path="src/production.py",
                acceptance_spec={"test": True},
            )

        # Valid module dispatch through quarantined engine synthesizer
        code = "def compute_area(r: float) -> float:\n    return 3.14159 * r * r\n"
        ok, msg, event = kernel.dispatch_quarantined_engine_synthesizer(
            module_path="src/geometry.py",
            source_code=code,
            symbol_urn="urn:axioma:g4b:geometry:engine#compute_area",
            node_type=ASTNodeType.FUNCTION_DEF,
        )
        self.assertTrue(ok)
        self.assertEqual(msg, "QUARANTINED_EMISSION_RECORDED")
        self.assertIsInstance(event, LeafEmissionEvent)

    # -------------------------------------------------------------------------
    # 5. AtomicTaskGuard Pre-Tool Hook & Synthetic Payload Verification
    # -------------------------------------------------------------------------
    def test_atomic_task_guard_helper_functions(self):
        # 1. Builder quarantine
        ok, msg = check_builder_quarantine(Path("tests/test_foo.py"), role="core_engine_synthesizer")
        self.assertFalse(ok)
        self.assertIn("BUILDER ROLE QUARANTINE VIOLATION", msg)

        # QA boundary
        ok_qa, msg_qa = check_builder_quarantine(Path("src/foo.py"), role="adversarial_qa_engineer")
        self.assertFalse(ok_qa)
        self.assertIn("QA ROLE BOUNDARY VIOLATION", msg_qa)

        # Allowed roles
        ok_builder_src, _ = check_builder_quarantine(Path("src/foo.py"), role="core_engine_synthesizer")
        self.assertTrue(ok_builder_src)
        ok_qa_test, _ = check_builder_quarantine(Path("tests/test_foo.py"), role="adversarial_qa_engineer")
        self.assertTrue(ok_qa_test)

        # 2. Provenance tracking and anti-collusion in temp turn log
        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = Path(tmpdir) / "synthesis_turn_log.json"
            conv_id = "conv_unsegregated_9999"

            record_synthesis_provenance(
                log_path=log_path,
                target_path=Path("apps/sample/src/router.py"),
                conv_id=conv_id,
                role="core_engine_synthesizer",
            )

            # Collusion detected when same conversation emits test for matching src
            ok_collude, msg_collude = check_anti_collusion(
                log_path=log_path,
                target_path=Path("apps/sample/tests/test_router.py"),
                conv_id=conv_id,
                role="main",
            )
            self.assertFalse(ok_collude)
            self.assertIn("ANTI-COLLUSION VIOLATION", msg_collude)

            # Different subagent conversation ID (orthogonal QA agent) is allowed
            ok_orthogonal, _ = check_anti_collusion(
                log_path=log_path,
                target_path=Path("apps/sample/tests/test_router.py"),
                conv_id="conv_orthogonal_qa_8888",
                role="adversarial_qa_engineer",
            )
            self.assertTrue(ok_orthogonal)

            # After marking mutation verified, unsegregated pair passes
            mark_mutation_verified(log_path, "router")
            ok_verified, _ = check_anti_collusion(
                log_path=log_path,
                target_path=Path("apps/sample/tests/test_router.py"),
                conv_id=conv_id,
                role="main",
            )
            self.assertTrue(ok_verified)

    def test_atomic_task_guard_subprocess_synthetic_payloads(self):
        """Executes python3 scripts/atomic_task_guard.py directly with synthetic payloads on stdin."""
        guard_script = self.workspace_root / "scripts" / "atomic_task_guard.py"

        # Case A: Builder role writing to tests/ directory -> Denied
        payload_builder_tests = {
            "toolCall": {
                "name": "write_file",
                "args": {
                    "Path": str(self.workspace_root / "generations" / "gen_04b" / "services" / "builder" / "tests" / "test_fake.py"),
                    "Content": "# synthetic test",
                },
            },
            "subagentRole": "core_engine_synthesizer",
            "conversationId": "conv_synthetic_builder_001",
            "workspacePaths": [str(self.workspace_root)],
        }
        proc = subprocess.run(
            [sys.executable, str(guard_script)],
            input=json.dumps(payload_builder_tests),
            capture_output=True,
            text=True,
            timeout=5,
        )
        self.assertEqual(proc.returncode, 0, f"Guard failed with stderr: {proc.stderr}")
        res = json.loads(proc.stdout.strip())
        self.assertEqual(res.get("decision"), "deny")
        self.assertIn("BUILDER ROLE QUARANTINE VIOLATION", res.get("reason", ""))

        # Case B: QA role writing to src/ directory -> Denied
        payload_qa_src = {
            "toolCall": {
                "name": "write_file",
                "args": {
                    "Path": str(self.workspace_root / "generations" / "gen_04b" / "services" / "builder" / "src" / "fake_engine.py"),
                    "Content": "# synthetic source",
                },
            },
            "subagentRole": "adversarial_qa_engineer",
            "conversationId": "conv_synthetic_qa_001",
            "workspacePaths": [str(self.workspace_root)],
        }
        proc = subprocess.run(
            [sys.executable, str(guard_script)],
            input=json.dumps(payload_qa_src),
            capture_output=True,
            text=True,
            timeout=5,
        )
        self.assertEqual(proc.returncode, 0, f"Guard failed with stderr: {proc.stderr}")
        res = json.loads(proc.stdout.strip())
        self.assertEqual(res.get("decision"), "deny")
        self.assertIn("QA ROLE BOUNDARY VIOLATION", res.get("reason", ""))

        # Case C: Shell redirection in run_command -> Denied
        payload_shell_redirect = {
            "toolCall": {
                "name": "run_command",
                "args": {
                    "CommandLine": "echo malicious " + ">" + " generations/gen_04b/services/builder/src/bypass.py",
                },
            },
            "workspacePaths": [str(self.workspace_root)],
        }
        proc = subprocess.run(
            [sys.executable, str(guard_script)],
            input=json.dumps(payload_shell_redirect),
            capture_output=True,
            text=True,
            timeout=5,
        )
        self.assertEqual(proc.returncode, 0, f"Guard failed with stderr: {proc.stderr}")
        res = json.loads(proc.stdout.strip())
        self.assertEqual(res.get("decision"), "deny")
        self.assertIn("Detected shell redirection", res.get("reason", ""))

        # Case D: Clean allowed command in run_command -> Allowed
        payload_clean_cmd = {
            "toolCall": {
                "name": "run_command",
                "args": {
                    "CommandLine": "python3 -m unittest discover",
                },
            },
            "workspacePaths": [str(self.workspace_root)],
        }
        proc = subprocess.run(
            [sys.executable, str(guard_script)],
            input=json.dumps(payload_clean_cmd),
            capture_output=True,
            text=True,
            timeout=5,
        )
        self.assertEqual(proc.returncode, 0, f"Guard failed with stderr: {proc.stderr}")
        res = json.loads(proc.stdout.strip())
        self.assertEqual(res.get("decision"), "allow")

        # Case E: Hermetic co-emission collusion detection via synthetic payloads in temp workspace
        with tempfile.TemporaryDirectory() as tmp_ws:
            tmp_scratch = Path(tmp_ws) / ".scratch"
            tmp_scratch.mkdir(parents=True, exist_ok=True)
            tmp_log = tmp_scratch / "synthesis_turn_log.json"

            conv_collude = "conv_collusion_hermetic_001"
            src_file = Path(tmp_ws) / "apps" / "isolated_app" / "src" / "payment.py"
            record_synthesis_provenance(tmp_log, src_file, conv_collude, "core_engine_synthesizer")

            # Same conversation attempts to emit acceptance test
            payload_collude_test = {
                "toolCall": {
                    "name": "write_file",
                    "args": {
                        "Path": str(Path(tmp_ws) / "apps" / "isolated_app" / "tests" / "test_payment.py"),
                        "Content": "# synthetic test",
                    },
                },
                "conversationId": conv_collude,
                "subagentRole": "main",
                "workspacePaths": [tmp_ws],
            }
            proc = subprocess.run(
                [sys.executable, str(guard_script)],
                input=json.dumps(payload_collude_test),
                capture_output=True,
                text=True,
                timeout=5,
            )
            self.assertEqual(proc.returncode, 0)
            res = json.loads(proc.stdout.strip())
            self.assertEqual(res.get("decision"), "deny")
            self.assertIn("ANTI-COLLUSION VIOLATION", res.get("reason", ""))


if __name__ == "__main__":
    unittest.main()
