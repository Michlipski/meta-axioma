"""Integration and Invariant Test Suite for G4b Sovereign Builder Modules (`soc_g4b_builder`).

Validates:
1. ASTSkeletonizer [Layer A]: typed stubs, body stripping, token ceiling <= 4,096 BPE tokens.
2. DiagnosticEngine & SurgicalPatcher [Layer B]: byte offset calculation, surgical patching, reverse multi-patching.
3. HermeticLinter [Layer C]: loopback IP detection (127.0.0.1, localhost), sys.path tampering, /tmp escape detection.
4. SymbolHypergraphIndexer [Layer D]: canonical URN resolution, topological dependency sort, cycle detection.
5. DynamicPersonaBuilder [L1-G4B-004]: persona synthesis and define_subagent schema export.
6. BudgetLeaseEngine: 60/40 partition, geometric token decay (lambda <= 0.80), Landauer cutoff gate (C_min = 1,024), heat dissipation (Q = k_B * T * ln(2) * bits).
7. BoundedFractalOrchestrator: depth d <= 4, branching b <= 5, subtree healing, Merkle hash propagation.
8. RFCProtocolClient: SpecAdjustmentRequest submission, SpecAmendment ingestion, CounterProof verification.
9. FunctorialUndoManager [L1-002]: checkpoint creation, causal stack rollback, context restoration.
10. QuineCrucibleEngine [L1-016]: daughter sandbox provisioning, emission, execution witness, self-hosting certification.
11. G4bBuilderStatechartEngine: 28-state enumeration, compound strata, parallel regions, deep history, recovery enclaves.
12. SovereignBuilderKernel: end-to-end integration with deliverable bundle ingestion and Merkle attestation.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
import sys
import tempfile
import time
import unittest

BUILDER_ROOT = Path(__file__).resolve().parent.parent
REPO_ROOT = BUILDER_ROOT.parent.parent.parent
for p in [str(BUILDER_ROOT), str(REPO_ROOT)]:
    if p not in sys.path:
        sys.path.insert(0, p)

from generations.gen_04b.protocols.deliverable_bundle import ResearchDeliverableBundle
from generations.gen_04b.protocols.rfc_protocol import BottleneckType, SpecAmendment
from src.ast_skeletonizer import ASTSkeletonizer
from src.budget_lease_engine import BudgetLeaseEngine, LandauerCutoffTripped
from src.builder_kernel import SovereignBuilderKernel
from src.diagnostic_tuples import DiagnosticEngine, SurgicalPatcher
from src.domain_models import (
    ASTNodeType,
    DiagnosticSeverity,
    DiagnosticTuple,
    DomainInvariantViolation,
)
from src.dynamic_persona_builder import DynamicPersonaBuilder
from src.fractal_orchestrator import (
    BoundedFractalOrchestrator,
    FractalBranchingExceededViolation,
    FractalDepthExceededViolation,
)
from src.functorial_undo import FunctorialUndoManager, FunctorialUndoViolation
from src.hermetic_linter import HermeticLinter
from src.hypergraph_indexer import SymbolHypergraphIndexer
from src.quine_crucible import QuineCrucibleEngine
from src.rfc_protocol_client import RFCProtocolClient
from src.statechart_engine import G4bBuilderStatechartEngine


class TestBuilderModules(unittest.TestCase):
    """Exhaustive test suite for all 13 Sovereign Builder subsystems."""

    def test_ast_skeletonizer(self):
        """Verifies function body replacement with Ellipsis and token ceiling."""
        code = '''
def add(a: int, b: int) -> int:
    """Calculates sum."""
    c = a + b
    return c

class Calculator:
    def multiply(self, x: float, y: float) -> float:
        return x * y
'''
        skeletonizer = ASTSkeletonizer()
        snap = skeletonizer.extract_skeleton(code, "calc.py", "urn:axioma:g4b:math:calc#Calculator")
        self.assertIn("def add(a, b)", snap.preserved_signatures)
        self.assertIn("class Calculator()", snap.preserved_signatures)
        self.assertTrue(snap.estimated_bpe_tokens <= 4096)
        self.assertIn("...", snap.skeleton_code)

    def test_diagnostic_and_surgical_patcher(self):
        """Verifies byte offset calculation, surgical patch application, and multi-patching."""
        source = "alpha = 10\nbeta = 20\n"
        diag1 = DiagnosticEngine.create_diagnostic(
            file_path="test.py",
            severity=DiagnosticSeverity.WARNING,
            rule_code="TEST_RULE_1",
            message="Replace 10 with 15",
            source_code=source,
            line=1,
            col=8,
            end_line=1,
            end_col=10,
            suggested_patch="15",
        )
        patched = SurgicalPatcher.apply_patch(source, diag1)
        self.assertEqual(patched, "alpha = 15\nbeta = 20\n")

        # Multi-patching in reverse order
        diag2 = DiagnosticEngine.create_diagnostic(
            file_path="test.py",
            severity=DiagnosticSeverity.WARNING,
            rule_code="TEST_RULE_2",
            message="Replace 20 with 25",
            source_code=source,
            line=2,
            col=7,
            end_line=2,
            end_col=9,
            suggested_patch="25",
        )
        multi_patched = SurgicalPatcher.apply_multi_patch(source, [diag1, diag2])
        self.assertEqual(multi_patched, "alpha = 15\nbeta = 25\n")

    def test_hermetic_linter(self):
        """Verifies detection of loopback IPs, sys.path tampering, and filesystem escapes."""
        linter = HermeticLinter()
        bad_code = "host = '127.0.0.1'\nimport sys\nsys.path.append('/tmp/dir')\n"
        rep = linter.audit_code(bad_code, "bad.py")
        self.assertFalse(rep.passed)
        violation_codes = {v.rule_code for v in rep.violations}
        self.assertIn("HERMETIC_LOOPBACK_PROHIBITED", violation_codes)
        self.assertIn("HERMETIC_SYS_PATH_TAMPERING", violation_codes)
        self.assertIn("HERMETIC_TMP_ESCAPE", violation_codes)

        clean_code = "endpoint = '192.168.40.20'\ndef ok():\n    return 1\n"
        rep_clean = linter.audit_code(clean_code, "clean.py")
        self.assertTrue(rep_clean.passed)

    def test_hypergraph_indexer(self):
        """Verifies canonical URN resolution, topological sort, and cycle detection."""
        indexer = SymbolHypergraphIndexer()
        indexer.index_symbol("urn:axioma:g4b:core:base#BaseClass", ASTNodeType.CLASS_DEF, "base.py")
        indexer.index_symbol(
            "urn:axioma:g4b:core:derived#DerivedClass",
            ASTNodeType.CLASS_DEF,
            "derived.py",
            dependencies=["urn:axioma:g4b:core:base#BaseClass"],
        )
        resolved = indexer.resolve_symbol("urn:axioma:g4b:core:base#BaseClass")
        self.assertIsNotNone(resolved)
        self.assertEqual(resolved.file_path, "base.py")

        order = indexer.topological_sort()
        self.assertEqual(order, [
            "urn:axioma:g4b:core:base#BaseClass",
            "urn:axioma:g4b:core:derived#DerivedClass",
        ])

        # Test cycle detection
        cyclic_indexer = SymbolHypergraphIndexer()
        cyclic_indexer.index_symbol("urn:axioma:g4b:a:node#A", ASTNodeType.MODULE, "a.py", dependencies=["urn:axioma:g4b:b:node#B"])
        cyclic_indexer.index_symbol("urn:axioma:g4b:b:node#B", ASTNodeType.MODULE, "b.py", dependencies=["urn:axioma:g4b:a:node#A"])
        with self.assertRaises(DomainInvariantViolation):
            cyclic_indexer.topological_sort()

    def test_dynamic_persona_builder(self):
        """Verifies dynamic persona generation and define_subagent schema export."""
        persona = DynamicPersonaBuilder.create_ast_specialist_persona()
        self.assertEqual(persona.cognitive_role, "AST_INTERFACE_SPECIALIST")
        params = DynamicPersonaBuilder.to_define_subagent_params(persona)
        self.assertIn("name", params)
        self.assertIn("system_prompt", params)
        self.assertTrue(params["enable_write_tools"])

        # Causal QA Persona
        qa_persona = DynamicPersonaBuilder.create_causal_qa_persona()
        self.assertEqual(qa_persona.cognitive_role, "CAUSAL_QA_ENGINEER")
        self.assertIn("[BLUEPRINT-G4B-CAUSAL-OPT3]", qa_persona.governing_axioms)
        qa_params = DynamicPersonaBuilder.to_define_subagent_params(qa_persona)
        self.assertEqual(qa_params["name"], "causal-qa-and-byzantine-chaos-engineer")

        # Reactive Auditor Persona
        auditor_persona = DynamicPersonaBuilder.create_reactive_auditor_persona()
        self.assertEqual(auditor_persona.cognitive_role, "REACTIVE_MICRO_AUDITOR")
        self.assertIn("[L1-G4B-001]", auditor_persona.governing_axioms)
        auditor_params = DynamicPersonaBuilder.to_define_subagent_params(auditor_persona)
        self.assertEqual(auditor_params["name"], "reactive-statechart-and-micro-auditor")

    def test_budget_lease_engine(self):
        """Verifies 60/40 partition, geometric decay, Landauer cutoff gate, and heat dissipation."""
        engine = BudgetLeaseEngine(total_budget_tokens=100000, decay_lambda=0.80)
        self.assertEqual(engine.protected_capital, 40000)
        self.assertEqual(engine.remaining_exploratory_capital, 60000)

        root_lease = engine.allocate_root_lease("node_root", requested_tokens=10000)
        self.assertEqual(root_lease.allocated_tokens, 10000)

        # Decay: (10000 / 2) * 0.80 = 4000
        child_lease = engine.spawn_child_lease("node_child", root_lease.lease_id, branching_factor=2)
        self.assertEqual(child_lease.allocated_tokens, 4000)

        # Bit erasure and heat dissipation Q = k_B * T * ln(2) * bits
        heat = engine.record_bit_erasure(bits_erased=2048, lease_id=child_lease.lease_id)
        self.assertGreater(heat, 0.0)
        self.assertEqual(child_lease.landauer_bits_erased, 2048)

        # Landauer cutoff gate
        small_engine = BudgetLeaseEngine(total_budget_tokens=2000, decay_lambda=0.50)
        # 60% of 2000 is 1200. Max available = 1200 - 1024 = 176 tokens.
        small_root = small_engine.allocate_root_lease("small_root", requested_tokens=150)
        with self.assertRaises(LandauerCutoffTripped):
            small_engine.allocate_root_lease("overflow_root", requested_tokens=100)

    def test_fractal_orchestrator(self):
        """Verifies bounded fractal tree depth (d <= 4) and branching (b <= 5)."""
        budget = BudgetLeaseEngine(total_budget_tokens=200000)
        orch = BoundedFractalOrchestrator(budget)
        root = orch.create_root_node("Root Task")

        children = []
        for i in range(5):
            c = orch.spawn_child_node(root.node_id, f"Child {i}", "Worker")
            children.append(c)

        # Branching factor overflow: 6th child
        with self.assertRaises(FractalBranchingExceededViolation):
            orch.spawn_child_node(root.node_id, "Child 6 (Overflow)", "Worker")

        # Depth bound: d <= 4
        c0 = children[0]  # depth 1
        d2 = orch.spawn_child_node(c0.node_id, "Depth 2", "Worker")
        d3 = orch.spawn_child_node(d2.node_id, "Depth 3", "Worker")
        d4 = orch.spawn_child_node(d3.node_id, "Depth 4", "Worker")
        with self.assertRaises(FractalDepthExceededViolation):
            orch.spawn_child_node(d4.node_id, "Depth 5 (Overflow)", "Worker")

        # Subtree healing
        diag = DiagnosticTuple(
            diagnostic_id="diag_heal_01",
            file_path="branch.py",
            severity=DiagnosticSeverity.ERROR,
            start_byte=0,
            end_byte=5,
            line_number=1,
            column_number=0,
            rule_code="HEAL_TEST",
            message="Branch fault",
        )
        env = orch.heal_subtree(d2.node_id, diag)
        self.assertFalse(env.resolved)
        orch.resolve_healing(env.envelope_id)
        self.assertTrue(env.resolved)

    def test_rfc_protocol_client(self):
        """Verifies RFC request submission and signed amendment ingestion."""
        client = RFCProtocolClient(builder_node_id="node_builder_test")
        req = client.submit_spec_adjustment_request(
            target_symbol_urn="urn:axioma:g4b:builder:types#Record",
            bottleneck_type=BottleneckType.LATENCY_OVERRUN,
            empirical_evidence="Physical latency spike",
            proposed_delta="Flatten fields",
            preserved_invariants=["[L1-002]"],
        )
        self.assertEqual(req.status.value, "SUBMITTED")

        amendment = SpecAmendment(
            amendment_id="amd_test_01",
            request_id=req.request_id,
            is_approved=True,
            adjudicator_signature="SIG_ECDSA_RESEARCH",
            amended_contract_ir_delta="FLATTEN_APPROVED",
        )
        ok, delta = client.ingest_spec_amendment(amendment)
        self.assertTrue(ok)
        self.assertEqual(delta, "FLATTEN_APPROVED")

    def test_functorial_undo(self):
        """Verifies checkpoint creation, rollback, and bit recovery."""
        mgr = FunctorialUndoManager()
        c1 = mgr.create_checkpoint("STEP_1", {"val": 10}, erased_bits=50)
        c2 = mgr.create_checkpoint("STEP_2", {"val": 20}, erased_bits=150)
        self.assertTrue(mgr.can_undo())

        restored, diff = mgr.undo()
        self.assertEqual(restored.checkpoint_id, c1.checkpoint_id)
        self.assertEqual(restored.state_context["val"], 10)
        self.assertEqual(diff, 100)

        # Cannot undo past genesis
        with self.assertRaises(FunctorialUndoViolation):
            mgr.undo()

    def test_quine_crucible(self):
        """Verifies clean-room daughter sandbox provisioning and self-hosting certification."""
        with tempfile.TemporaryDirectory() as tmpdir:
            crucible = QuineCrucibleEngine(sandbox_base_dir=tmpdir)
            manifest = crucible.certify_daughter_compiler("gen_05a")
            self.assertTrue(manifest.boot_success)
            self.assertTrue(manifest.self_hosting_certified)
            self.assertEqual(len(manifest.daughter_hash), 64)

    def test_statechart_engine(self):
        """Verifies 36-state inventory, transitions, deep history, and 1-tap undo."""
        sc = G4bBuilderStatechartEngine()
        self.assertEqual(len(sc.ALL_STATES), 36)

        # Transition handshake
        sc.send("EV_AWAIT_BUNDLE")
        self.assertEqual(sc.active_main_state, "handshake_awaiting_bundle")
        sc.send("EV_BUNDLE_VALID")
        self.assertEqual(sc.active_main_state, "bundle_validated")

        # 1-tap undo
        restored = sc.undo_step()
        self.assertEqual(restored[0], "handshake_awaiting_bundle")

    def test_builder_kernel_integration(self):
        """Verifies full builder kernel compilation lifecycle and Merkle attestation."""
        kernel = SovereignBuilderKernel(node_ip="192.168.40.20", port=8442, total_budget_tokens=150000)
        bundle = ResearchDeliverableBundle(
            bundle_id="bundle_int_test",
            target_soc_id="soc_g4b_builder",
            hypothesis_id="hyp_01",
            constraint_analysis_id="ca_01",
            failure_mode_id="fm_01",
            tradeoff_matrix_id="tm_01",
            reference_architecture_hash="f" * 64,
            merkle_root="0" * 64,
            is_certified=True,
        )
        exec_bundle = kernel.handshake_and_ingest(bundle)
        self.assertEqual(exec_bundle.status.value, "ACTIVE")

        ok, msg = kernel.compile_module(
            module_path="src/app.py",
            source_code="def run_app():\n    return 'OK'\n",
            symbol_urn="urn:axioma:g4b:app:core#run_app",
        )
        self.assertTrue(ok)

        attestation = kernel.seal_merkle_attestation()
        self.assertEqual(len(attestation.merkle_root), 64)
        self.assertEqual(exec_bundle.status.value, "COMPLETED")

    def test_builder_kernel_causal_lifecycle_methods(self):
        """Verifies BLUEPRINT-G4B-CAUSAL-OPT3 kernel lifecycle methods and physical disk witness."""
        kernel = SovereignBuilderKernel(node_ip="192.168.40.20", port=8442, total_budget_tokens=150000)
        
        # Advance state to ast_skeleton_extracting
        kernel.statechart.send("EV_AWAIT_BUNDLE")
        kernel.statechart.send("EV_BUNDLE_VALID")
        kernel.statechart.send("EV_START_ORCHESTRATION")
        kernel.statechart.send("EV_BRANCH_SPAWN")
        kernel.statechart.send("EV_EVAL_BUDGET")
        kernel.statechart.send("EV_BUDGET_OK")
        kernel.statechart.send("EV_START_SYNTHESIS")
        self.assertEqual(kernel.statechart.active_main_state, "ast_skeleton_extracting")

        # 1. signal_dispatch_builders
        kernel.signal_dispatch_builders()
        self.assertEqual(kernel.statechart.active_main_state, "builders_synthesizing")

        # 2. verify_substrate_emitted with non-zero bytes
        with tempfile.NamedTemporaryFile(suffix=".py", delete=False) as tmp:
            tmp.write(b"def compute(): return 42\n")
            tmp_path = tmp.name

        try:
            witness = kernel.verify_substrate_emitted(tmp_path)
            self.assertEqual(witness.file_path, str(Path(tmp_path).resolve()))
            self.assertGreater(witness.byte_size, 0)
            self.assertEqual(len(witness.sha256_hash), 64)
            self.assertTrue(witness.is_present)
            # After verify_substrate_emitted, state moves to substrate_emitted_gate then surgical_patch_evaluating
            self.assertEqual(kernel.statechart.active_main_state, "surgical_patch_evaluating")

            # Advance to hermetic_linter_auditing and pass linter
            kernel.statechart.send("EV_AUDIT_HERMETIC")
            kernel.statechart.send("EV_LINTER_PASSED")
            self.assertEqual(kernel.statechart.active_main_state, "reactive_audit_evaluating")

            # 3. signal_reactive_audit_ok
            kernel.signal_reactive_audit_ok()
            self.assertEqual(kernel.statechart.active_main_state, "byzantine_chaos_injecting")

            # 4. signal_chaos_tests_passed
            kernel.signal_chaos_tests_passed()
            self.assertEqual(kernel.statechart.active_main_state, "all_leaves_converged_gate")

            # 5. signal_all_leaves_converged
            kernel.signal_all_leaves_converged()
            self.assertEqual(kernel.statechart.active_main_state, "hypergraph_indexing")
        finally:
            Path(tmp_path).unlink(missing_ok=True)

        # Verify zero-byte failure raises DomainInvariantViolation
        with tempfile.NamedTemporaryFile(suffix=".py", delete=False) as empty_tmp:
            empty_path = empty_tmp.name

        try:
            with self.assertRaises(DomainInvariantViolation):
                kernel.verify_substrate_emitted(empty_path)
        finally:
            Path(empty_path).unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
