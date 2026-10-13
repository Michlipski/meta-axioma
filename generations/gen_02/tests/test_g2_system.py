"""Unit and Invariant Verification Suite for System G_2 Compiler.

Verifies:
- All 5 Active Structural Basis Axioms (L1-G2-001 through L1-G2-005)
- All 4 Generation 2 Evaluation Targets (G2-T1 through G2-T4)
- Enforceability of Inherited Negative Invariants (NEG-G2-001, NEG-G2-002, NEG-G2-003)
- Autonomous Endogenous Formulation of Generation 3 (G_3) Successor Basis
"""

from pathlib import Path
import unittest

from g2_compiler.basis_generator import G3BasisSynthesizer
from g2_compiler.capability_scoping import CapabilityTokenManager
from g2_compiler.cognitive_ergonomics import CognitiveErgonomicsAuditor
from g2_compiler.engine import SystemG2Compiler
from g2_compiler.galois_substrate import GaloisSubstrateMapper
from g2_compiler.intent_grounding import HumanIntentGroundingGate
from g2_compiler.self_healing import EphemeralSelfHealingEnclave
from g2_compiler.distributed_sheaf_crdt import (
    DistributedSheafCrdtEngine,
    G3EvolutionarySuccessionGate,
    G3SearchTrace,
    LinearCompilationViolation,
    SheafSection,
    CausalVectorClock,
    PairwiseCocycleAuditor,
    K_B_T_LN2,
)
from g2_compiler.types import (
    CapabilitySecurityFault,
    GenerationalRegressionFault,
    IntentAST,
    PersonaModel,
    RepairStatus,
    SubstrateType,
)


class TestSystemG2Compiler(unittest.TestCase):
    """Formal verification of the constructed System G_2 compiler."""

    def setUp(self) -> None:
        self.compiler = SystemG2Compiler()

    def test_l1_g2_001_galois_substrate_isomorphism(self) -> None:
        """Verifies L1-G2-001: Adjoint Galois Substrate Connection & Multi-Target Preservation."""
        mapper = GaloisSubstrateMapper()
        intent = IntentAST(
            intent_id="intent_test",
            action="sync_nodes",
            target_noun="StateVector",
            parameters={"cluster_size": 4, "quorum": "2/3"},
            constraints=["L1-G2-001"],
        )

        # Test across all supported substrates
        for substrate in SubstrateType:
            audit = mapper.verify_round_trip(intent, substrate)
            self.assertTrue(audit.is_valid, f"Galois round-trip failed for {substrate.value}")
            self.assertTrue(audit.unit_satisfied, "Unit η: Id -> G ∘ F must be satisfied")
            self.assertTrue(audit.counit_satisfied, "Counit ε: F ∘ G -> Id must be satisfied")
            self.assertEqual(audit.round_trip_closure_error, 0.0)

        all_valid, audits = mapper.verify_multi_substrate_preservation(intent)
        self.assertTrue(all_valid)
        self.assertEqual(len(audits), 4)

    def test_l1_g2_002_ephemeral_self_healing_and_blast_containment(self) -> None:
        """Verifies L1-G2-002: Ephemeral Self-Healing Invariant Restoration Loop."""
        enclave = EphemeralSelfHealingEnclave(max_passes=3)
        initial_ctx = {"state": "corrupted", "attempts_needed": 2}

        def unstable_op(ctx: dict) -> dict:
            if ctx.get("repaired") is not True:
                return {"result": "FAILED", "data": None}
            return {"result": "SUCCESS", "data": "restored_payload"}

        def checker(res: dict, ctx: dict) -> tuple[bool, list[str]]:
            if res.get("result") == "SUCCESS":
                return True, []
            return False, ["Payload not restored."]

        def remediator(infractions: list[str], ctx: dict, pass_k: int) -> dict:
            if pass_k >= 1:
                ctx["repaired"] = True
            return ctx

        healing_result = enclave.execute_with_healing(
            operation=unstable_op,
            initial_context=initial_ctx,
            invariant_checker=checker,
            remediator=remediator,
            operation_name="SelfHealingTestOp",
        )

        self.assertEqual(healing_result.status, RepairStatus.HEALED)
        self.assertEqual(healing_result.attempts_executed, 2)
        self.assertFalse(healing_result.blast_leakage_detected, "Parent context must remain untouched")
        self.assertEqual(initial_ctx, {"state": "corrupted", "attempts_needed": 2})

    def test_l1_g2_003_cognitive_ergonomics_and_persona_alignment(self) -> None:
        """Verifies L1-G2-003: Cognitive Ergonomics & Persona Alignment Invariance."""
        auditor = CognitiveErgonomicsAuditor(epsilon_ergonomics=0.50, min_utility_threshold=0.65)
        persona = PersonaModel(
            persona_name="ProductSpecialist",
            domain_familiarity=0.80,
            expected_vocabulary=["task", "board", "column", "status", "undo"],
            daily_goals=["create_task", "move_task"],
            tolerance_threshold=0.35,
        )

        # 1. Ergonomic passing interface
        good_vocab = ["task", "board", "column", "status", "undo", "settings"]
        good_audit = auditor.evaluate_interface_ergonomics(
            persona=persona,
            system_vocabulary=good_vocab,
            interaction_steps=1,
            cryptic_error_count=0,
            undo_available=True,
            task_completion_seconds=2.0,
        )
        self.assertTrue(good_audit.is_acceptable)
        self.assertGreaterEqual(good_audit.utility_score, 0.65)

        # 2. Ergonomic failing interface (cryptic error codes, excessive steps)
        bad_audit = auditor.evaluate_interface_ergonomics(
            persona=persona,
            system_vocabulary=["kernel", "mutex", "inode"],  # complete vocabulary mismatch
            interaction_steps=7,
            cryptic_error_count=3,
            undo_available=False,
            task_completion_seconds=45.0,
        )
        self.assertFalse(bad_audit.is_acceptable)
        self.assertGreater(len(bad_audit.rejection_reasons), 0)

    def test_l1_g2_004_capability_token_zero_trust(self) -> None:
        """Verifies L1-G2-004: Introspectable Zero-Trust Capability Scoping."""
        cap_mgr = CapabilityTokenManager(signing_secret="axioma_test_secret")

        token = cap_mgr.issue_token(
            persona="SecurityArchitect",
            allowed_actions=["inspect_state", "audit_log"],
            ttl_seconds=60.0,
        )

        # Allowed tool action succeeds
        result = cap_mgr.execute_scoped_tool(
            token=token,
            tool_action="inspect_state",
            tool_callable=lambda: "state_ok",
        )
        self.assertEqual(result, "state_ok")

        # Disallowed tool action fails with CapabilitySecurityFault
        with self.assertRaises(CapabilitySecurityFault):
            cap_mgr.execute_scoped_tool(
                token=token,
                tool_action="drop_database",
                tool_callable=lambda: "dropped",
            )

        # Ambient / unscoped action without token fails immediately
        with self.assertRaises(CapabilitySecurityFault):
            cap_mgr.execute_scoped_tool(
                token=None,
                tool_action="inspect_state",
                tool_callable=lambda: "ambient",
            )

        # Check cryptographic witnesses
        witnesses = cap_mgr.get_audit_witnesses()
        self.assertEqual(len(witnesses), 1)

    def test_l1_g2_005_and_neg_g2_001_intent_elicitation_gate(self) -> None:
        """Verifies L1-G2-005 and NEG-G2-001: Mandatory Human Intent Elicitation Gate."""
        gate = HumanIntentGroundingGate()

        # Attempting compilation without prior elicitation fails with GenerationalRegressionFault
        with self.assertRaises(GenerationalRegressionFault) as ctx:
            gate.verify_elicitation_gate("unelicited_new_app")
        self.assertIn("NEG-G2-001 VETO", str(ctx.exception))

        # Registering an unsigned witness also fails (NEG-G2-002)
        gate.create_witness(
            application_id="draft_app",
            persona_name="Designer",
            jtbd_summary="Review layouts",
            daily_workflow="Open dashboard",
            utility_metric_definition="U > 0.8",
            signed_off_by_human=False,
        )
        with self.assertRaises(GenerationalRegressionFault) as ctx2:
            gate.verify_elicitation_gate("draft_app")
        self.assertIn("NEG-G2-002 VETO", str(ctx2.exception))

        # Signed witness succeeds
        signed = gate.create_witness(
            application_id="approved_app",
            persona_name="Designer",
            jtbd_summary="Review layouts",
            daily_workflow="Open dashboard",
            utility_metric_definition="U > 0.8",
            signed_off_by_human=True,
        )
        verified = gate.verify_elicitation_gate("approved_app")
        self.assertEqual(verified.witness_id, signed.witness_id)

    def test_g3_basis_synthesis(self) -> None:
        """Verifies autonomous endogenous formulation of Generation 3 (G_3)."""
        synthesizer = G3BasisSynthesizer(compiler_name="System G_2")
        g3_basis = synthesizer.generate_successor_basis()

        self.assertEqual(g3_basis.generation, 3)
        self.assertEqual(len(g3_basis.targets), 4)
        self.assertEqual(len(g3_basis.basis_axioms), 5)
        self.assertGreaterEqual(len(g3_basis.inherited_negative_constraints), 3)

        target_ids = [t.target_id for t in g3_basis.targets]
        self.assertEqual(target_ids, ["G3-T1", "G3-T2", "G3-T3", "G3-T4"])

        axiom_ids = [a.id for a in g3_basis.basis_axioms]
        self.assertEqual(axiom_ids, ["L1-G3-001", "L1-G3-002", "L1-G3-003", "L1-G3-004", "L1-G3-005"])

    def test_l1_g2_008_distributed_sheaf_crdt_and_evolutionary_succession_gate(self) -> None:
        """Verifies L1-G2-008: Distributed Evolutionary Island Synthesis & Decoupled Chaos Verification."""
        # 1. Negative Test: Linear bypass must be caught
        with self.assertRaises(LinearCompilationViolation):
            G3EvolutionarySuccessionGate.verify_succession_trace(None)

        # 2. Negative Test: Insufficient islands (< 3)
        under_trace = G3SearchTrace(
            trace_id="UNDER_TRACE",
            islands_explored=["ISLAND_1", "ISLAND_2"],
            total_candidates_evaluated=3,
            dead_end_candidates=[{"id": "DEAD"}],
            crucible_witnesses=[],
            selected_winner_id="WINNER",
        )
        with self.assertRaises(LinearCompilationViolation):
            G3EvolutionarySuccessionGate.verify_succession_trace(under_trace)

        # 3. Negative Test: Missing dead ends (< 1)
        no_dead_trace = G3SearchTrace(
            trace_id="NO_DEAD_TRACE",
            islands_explored=["ISLAND_1", "ISLAND_2", "ISLAND_3"],
            total_candidates_evaluated=3,
            dead_end_candidates=[],
            crucible_witnesses=[],
            selected_winner_id="WINNER",
        )
        with self.assertRaises(LinearCompilationViolation):
            G3EvolutionarySuccessionGate.verify_succession_trace(no_dead_trace)

        # 4. Positive Test: Valid multi-island search trace passes gate
        valid_trace = G3SearchTrace(
            trace_id="VALID_TRACE",
            islands_explored=["ISLAND_SHEAF", "ISLAND_CRDT", "ISLAND_ACTOR"],
            total_candidates_evaluated=7,
            dead_end_candidates=[{"id": "DEAD_ACTOR", "reason": "OOM Crash"}],
            crucible_witnesses=[{"status": "PASS"}],
            selected_winner_id="WINNER_CAND",
        )
        cert = G3EvolutionarySuccessionGate.verify_succession_trace(valid_trace)
        self.assertTrue(cert.startswith("CERT_G2_"))
        self.assertTrue(valid_trace.is_verified)

        # 5. Distributed Sheaf-CRDT Engine test
        engine = DistributedSheafCrdtEngine(node_id="node_test_local")
        sec_u = engine.register_subdomain(
            subdomain_id="sub_u",
            initial_data={"route": "mesh_a", "counter": 10},
            boundary_keys=["route"],
        )
        sec_v = SheafSection(
            subdomain_id="sub_u",
            data={"route": "mesh_a", "counter": 20},
            vector_clock=CausalVectorClock(clock={"node_remote": 2}),
            observed_boundary_keys={"route"},
        )
        merged, audit = engine.merge_remote_section(sec_v)
        self.assertTrue(audit.is_consistent)
        self.assertEqual(merged.data["counter"], 20)
        self.assertGreater(engine.total_erased_bits, 0.0)
        self.assertGreater(engine.total_dissipated_joules, 0.0)

    def test_full_system_g2_compilation_cycle(self) -> None:
        """Verifies complete end-to-end System G_2 compilation pass and decay calculation."""
        # Check thermodynamic compute budget (Active n=8: 10000 / (1 + 0.5 * 8) = 2000)
        decay_tokens = self.compiler.compute_decay_capacity()
        self.assertEqual(decay_tokens, 2000)

        # Verify all 8 structural basis axioms (L1-G2-001 through L1-G2-008)
        axiom_results = self.compiler.verify_all_structural_basis_axioms()
        self.assertEqual(len(axiom_results), 8)
        for axiom_id, ok in axiom_results.items():
            self.assertTrue(ok, f"Axiom {axiom_id} failed verification")

        # Compile full generational cycle
        compilation = self.compiler.compile_generational_cycle()
        self.assertTrue(compilation.success)
        self.assertEqual(compilation.generation, 2)
        self.assertEqual(compilation.epoch, 2)
        self.assertEqual(compilation.structural_axioms_verified, 8)
        self.assertEqual(compilation.inherited_vetoes_enforced, 3)
        self.assertTrue(compilation.g3_successor_basis_synthesized)
        self.assertGreater(compilation.aggregate_delta_e, 0.90)



if __name__ == "__main__":
    unittest.main()
