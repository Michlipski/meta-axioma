"""Unit and integration test suite for System G_1 Compiler Engine.

Verifies complete adherence to the 7 active structural axioms and the
autonomous formulation of the Generation 2 (G_2) successor basis.
"""

import tempfile
import unittest
from pathlib import Path

from g1_compiler import (
    SystemG1Compiler,
    Morphism,
    CategoryFunctor,
    FunctorialPipeline,
    DeepSyntaxNode,
    UniversalGrammar,
    InMemoryAdapter,
    FileSystemAdapter,
    Boundary3PersistenceManager,
    LandauerAccountingLedger,
    ThermodynamicReversibilityAuditor,
    McpGateway,
    McpTool,
    NounField,
    NounSchema,
    VerbStateAutomaton,
    VerbTransition,
    ExceptionEnclave,
    CompositionalBoundaryAuditor,
    IslandGenerator,
    DecoupledAdversarialCrucible,
    K_B_T_LN2,
    MapElitesArchive,
    NonLinearSuccessionGate,
    LinearCompilationViolation,
    NonLinearSearchTrace,
    CrucibleReport,
    BehavioralNiche,
)
from g1_compiler.composition import CompositionalUnit



class TestFunctorMorphismPreservation(unittest.TestCase):
    """Verifies [L1-002] Functorial State Evolution & Morphism Preservation."""

    def test_morphism_composition_and_reversibility(self):
        f = Morphism[int, int](
            name="multiply_two",
            source_type="int",
            target_type="int",
            transform=lambda x: x * 2,
            inverse=lambda y: y // 2,
        )
        g = Morphism[int, int](
            name="add_five",
            source_type="int",
            target_type="int",
            transform=lambda x: x + 5,
            inverse=lambda y: y - 5,
        )
        # Composition: (f ∘ g)(x) = f(g(x))
        h = f.compose(g)
        self.assertEqual(h.apply(10), 30)  # (10 + 5) * 2 = 30
        self.assertTrue(h.is_reversible())
        self.assertEqual(h.invert(30), 10)

    def test_morphism_type_safety(self):
        m_str_to_int = Morphism[str, int](
            name="parse_length",
            source_type="str",
            target_type="int",
            transform=len,
        )
        m_float_to_str = Morphism[float, str](
            name="float_to_str",
            source_type="float",
            target_type="str",
            transform=str,
        )
        # Invalid composition order: m_float_to_str expects float, m_str_to_int produces int
        with self.assertRaises(TypeError):
            m_float_to_str.compose(m_str_to_int)

    def test_functor_laws(self):
        functor = CategoryFunctor("F_Test")
        m1 = Morphism(name="step1", source_type="int", target_type="int", transform=lambda x: x + 1, inverse=lambda y: y - 1)
        m2 = Morphism(name="step2", source_type="int", target_type="int", transform=lambda x: x * 3, inverse=lambda y: y // 3)
        laws = functor.verify_functor_laws(sample_input=7, m1=m1, m2=m2)
        self.assertTrue(laws["identity_preserved"])
        self.assertTrue(laws["composition_preserved"])
        self.assertTrue(laws["functor_law_satisfied"])


class TestUniversalGrammar(unittest.TestCase):
    """Verifies [L1-004] Universal Grammar & Compositional Projection Constraints."""

    def test_deep_ast_validation_and_digest(self):
        node = DeepSyntaxNode(
            node_type="COMPILER_MODULE",
            identifier="ModuleAlpha",
            attributes={"version": "1.0"},
            children=[
                DeepSyntaxNode("STORAGE_ADAPTER", "SubStore", {"adapter": "InMemory"}),
            ],
        )
        self.assertTrue(UniversalGrammar.validate_deep_syntax(node))
        digest = node.compute_deep_digest()
        self.assertEqual(len(digest), 64)

    def test_surface_projections_and_fidelity(self):
        node = DeepSyntaxNode(
            node_type="INVARIANT_SPEC",
            identifier="SpecInvariant",
            attributes={"layer": "structural"},
        )
        ir = UniversalGrammar.project_to_ir(node)
        self.assertEqual(ir["entity"], "SpecInvariant")
        self.assertTrue(UniversalGrammar.verify_projection_fidelity(node, ir))

        trace_doc = UniversalGrammar.project_to_trace_spec(node)
        self.assertIn("TRACE Specification: SpecInvariant", trace_doc)

        schema = UniversalGrammar.project_to_schema(node)
        self.assertEqual(schema["type_name"], "SpecInvariant")


class TestDecoupledPersistenceBoundary3(unittest.TestCase):
    """Verifies [L1-011_3] Decoupled Persistence across Boundary 3."""

    def test_in_memory_adapter(self):
        manager = Boundary3PersistenceManager(adapter=InMemoryAdapter())
        intent = manager.commit_transformation(
            collection="test_col",
            record_id="rec_1",
            delta={"active": True, "value": 42},
        )
        self.assertEqual(intent.boundary, "BOUNDARY_3")
        retrieved = manager.read_state("test_col", "rec_1")
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved["data"]["value"], 42)

    def test_file_system_adapter(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            fs_adapter = FileSystemAdapter(base_directory=Path(tmp_dir))
            manager = Boundary3PersistenceManager(adapter=fs_adapter)
            manager.commit_transformation(
                collection="artifacts",
                record_id="art_01",
                delta={"type": "IR_BYTECODE"},
            )
            retrieved = manager.read_state("artifacts", "art_01")
            self.assertIsNotNone(retrieved)
            self.assertEqual(retrieved["data"]["type"], "IR_BYTECODE")
            self.assertIn("art_01", fs_adapter.list_keys("artifacts"))


class TestLandauerThermodynamics(unittest.TestCase):
    """Verifies [L1-008] Landauer Thermodynamic Reversibility & Erasure Dissipation Accounting."""

    def test_reversible_vs_lossy_operations(self):
        ledger = LandauerAccountingLedger()
        auditor = ThermodynamicReversibilityAuditor(ledger=ledger)

        # Reversible operation: 0 bits erased, 0 Joules dissipated
        rec_rev = auditor.audit_transformation("iso_shift", is_reversible=True, erased_bits=32.0)
        self.assertEqual(rec_rev.erased_bits, 0.0)
        self.assertEqual(rec_rev.dissipated_energy_joules, 0.0)

        # Lossy operation: bits erased, positive Landauer heat dissipated
        rec_lossy = auditor.audit_transformation("truncate_cache", is_reversible=False, erased_bits=128.0)
        self.assertEqual(rec_lossy.erased_bits, 128.0)
        self.assertGreater(rec_lossy.dissipated_energy_joules, 0.0)

        summary = ledger.get_summary()
        self.assertEqual(summary["total_operations"], 2)
        self.assertEqual(summary["total_erased_bits"], 128.0)

    def test_unauthorized_lossy_mutation_raises(self):
        auditor = ThermodynamicReversibilityAuditor()
        with self.assertRaises(PermissionError):
            auditor.audit_transformation("untracked_drop", is_reversible=False, erased_bits=64.0, has_audit_channel=False)


class TestMcpZeroTrustGovernance(unittest.TestCase):
    """Verifies [L1-015] Zero-Trust Dual-Boundary Demarcation & Introspectable MCP Governance."""

    def test_noun_and_verb_governance(self):
        automaton = VerbStateAutomaton(initial_state="INITIAL")
        automaton.register_transition(VerbTransition("INITIAL", "START_COMPILE", "COMPILING"))
        gateway = McpGateway(automaton=automaton)

        schema = NounSchema(
            schema_name="PayloadSchema",
            fields={"source": NounField("source", str), "depth": NounField("depth", int)},
        )
        tool = McpTool(
            name="run_compile",
            description="Compiles payload.",
            input_schema=schema,
            action_verb="START_COMPILE",
            handler=lambda p: {"status": "SUCCESS"},
            sandbox_verifier=lambda p: 0,
        )
        gateway.register_tool(tool)

        # Introspect
        tools = gateway.list_tools()
        self.assertEqual(len(tools), 1)
        self.assertEqual(tools[0]["name"], "run_compile")

        # Execute valid tool
        res = gateway.execute_tool("run_compile", {"source": "main.src", "depth": 3})
        self.assertEqual(res["status"], "SUCCESS")
        self.assertEqual(automaton.current_state, "COMPILING")

        # Illegal repeated verb transition
        with self.assertRaises(PermissionError):
            gateway.execute_tool("run_compile", {"source": "second.src", "depth": 1})

    def test_sandbox_verification_failure_halts_execution(self):
        automaton = VerbStateAutomaton(initial_state="IDLE")
        automaton.register_transition(VerbTransition("IDLE", "DANGEROUS_ACTION", "RUNNING"))
        gateway = McpGateway(automaton=automaton)

        tool = McpTool(
            name="unsafe_tool",
            description="Fails sandbox",
            input_schema=NounSchema("EmptySchema"),
            action_verb="DANGEROUS_ACTION",
            handler=lambda p: {"status": "SHOULD_NOT_RUN"},
            sandbox_verifier=lambda p: 1,  # Non-zero exit code
        )
        gateway.register_tool(tool)

        with self.assertRaises(RuntimeError):
            gateway.execute_tool("unsafe_tool", {})


class TestDemarcatedExceptionEnclaves(unittest.TestCase):
    """Verifies [L1-016] Demarcated Exception Enclaves & Bounded Invariant Suspension."""

    def test_enclave_blast_radius_containment(self):
        with ExceptionEnclave(
            enclave_id="ENCLAVE_TEST_ALPHA",
            suspended_invariants=["L1-002"],
            justification="Intentional boundary bypass for recovery testing.",
            humane_recovery_guidance="Graceful fallback with user notification.",
        ) as enclave:
            # Raise exception inside enclave
            raise RuntimeError("Fatal inner error.")

        # Outside enclave: error was contained, witness emitted
        self.assertIsNotNone(enclave.witness)
        self.assertTrue(enclave.witness.blast_radius_contained)
        self.assertTrue(enclave.witness.state_leakage_prevented)
        self.assertEqual(len(enclave.witness.witness_hash), 64)
        self.assertIn("Graceful fallback", enclave.witness.humane_recovery_guidance)


class TestCompositionalBoundaryIsolation(unittest.TestCase):
    """Verifies [L1-015_1] Compositional Boundary Isolation."""

    def test_compositional_orthogonality(self):
        auditor = CompositionalBoundaryAuditor()
        unit_1 = CompositionalUnit("Parser", "BOUND_1", lambda ctx: {"tokens": 100})
        unit_2 = CompositionalUnit("Optimizer", "BOUND_2", lambda ctx: {"optimizations": 5})

        input_ctx = {"file": "app.code"}
        res = auditor.verify_compositionality(unit_1, unit_2, input_ctx)
        self.assertTrue(res["no_input_mutation"])
        self.assertTrue(res["orthogonal_boundaries"])
        self.assertTrue(res["is_compositional"])


class TestSystemG1CompilerFullSuite(unittest.TestCase):
    """Verifies the complete System G_1 Compiler Engine and G_2 successor formulation."""

    def test_verify_all_nine_structural_axioms(self):
        compiler = SystemG1Compiler()
        results = compiler.verify_all_structural_axioms()

        expected_axioms = [
            "L1-002", "L1-004", "L1-011_3", "L1-008",
            "L1-015", "L1-016", "L1-015_1", "L1-017", "L1-018",
        ]
        self.assertEqual(len(results), 9)

        for ax_id in expected_axioms:
            self.assertIn(ax_id, results)
            res = results[ax_id]
            self.assertTrue(res.passed, f"Axiom {ax_id} failed verification: {res.message}")

    def test_generate_g2_successor_basis(self):
        compiler = SystemG1Compiler()
        g2_basis = compiler.generate_g2_basis()

        self.assertEqual(g2_basis.generation, 2)
        self.assertGreaterEqual(len(g2_basis.targets), 4)
        self.assertGreaterEqual(len(g2_basis.basis_axioms), 4)
        self.assertIn("non-generator systems", g2_basis.high_level_jettison_awareness)

        # Verify Non-Linear Search Trace & Succession Certificate ([L1-017])
        self.assertIsNotNone(g2_basis.search_trace)
        self.assertIsNotNone(g2_basis.succession_certificate)
        self.assertTrue(g2_basis.succession_certificate.startswith("CERT_G1_"))
        self.assertGreaterEqual(len(g2_basis.search_trace.islands_explored), 3)
        self.assertGreaterEqual(len(g2_basis.search_trace.dead_end_candidates), 1)
        self.assertTrue(g2_basis.search_trace.is_verified)

        # Verify G2 targets have non-generator telos alignment
        for target in g2_basis.targets:
            self.assertTrue(len(target.non_generator_telos_alignment) > 0)
            self.assertGreater(target.weight, 0.0)

        # Verify G2 basis axioms are well-defined
        for ax in g2_basis.basis_axioms:
            self.assertTrue(ax.id.startswith("L1-G2-"))
            self.assertTrue(len(ax.formal_expression) > 0)
            self.assertTrue(len(ax.teleological_purpose) > 0)

        # Verify feedback dossier ingestion & inherited constraints
        self.assertIsNotNone(g2_basis.inherited_feedback_dossier)
        self.assertGreaterEqual(len(g2_basis.inherited_negative_constraints), 1)
        self.assertTrue(any("NEG-G2-001" in c for c in g2_basis.inherited_negative_constraints))
        self.assertTrue(any("LES-G1-001" in s for s in g2_basis.lessons_learned_summary))
        self.assertTrue(any(ax.id == "L1-G2-005" for ax in g2_basis.basis_axioms))


class TestNonLinearSearchInvariance(unittest.TestCase):
    """Verifies [L1-017] Non-Linear Exploratory Trajectory & Tree Search Invariance."""

    def test_linear_bypass_rejection(self):
        # Attempting succession verification without trace raises LinearCompilationViolation
        with self.assertRaises(LinearCompilationViolation):
            NonLinearSuccessionGate.verify_trace(None)

    def test_insufficient_islands_rejection(self):
        # Trace with fewer than 3 islands fails
        trace = NonLinearSearchTrace(
            trace_id="TRACE_UNDER_BRANCHED",
            islands_explored=["ISLAND_A", "ISLAND_B"],
            total_candidates_evaluated=4,
            dead_end_candidates=[{"candidate_id": "CAND_X"}],
            crucible_witnesses=[],
            selected_winner_id="CAND_Y",
        )
        with self.assertRaises(LinearCompilationViolation) as ctx:
            NonLinearSuccessionGate.verify_trace(trace)
        self.assertIn("Insufficient island diversity", str(ctx.exception))

    def test_missing_dead_end_witness_rejection(self):
        # Trace with 0 dead ends fails (violating Popperian falsifiability and authentic exploration)
        trace = NonLinearSearchTrace(
            trace_id="TRACE_NO_DEAD_ENDS",
            islands_explored=["ISLAND_A", "ISLAND_B", "ISLAND_C"],
            total_candidates_evaluated=3,
            dead_end_candidates=[],  # 0 dead ends
            crucible_witnesses=[],
            selected_winner_id="CAND_WINNER",
        )
        with self.assertRaises(LinearCompilationViolation) as ctx:
            NonLinearSuccessionGate.verify_trace(trace)
        self.assertIn("Missing dead-end falsification witness", str(ctx.exception))

    def test_multi_island_exploration_and_mutation(self):
        gen = IslandGenerator()
        islands = gen.get_islands()
        self.assertGreaterEqual(len(islands), 3)

        cands = [gen.seed_candidate(i.island_id) for i in islands]
        self.assertEqual(len(cands), len(islands))

        # Test mutation
        mut = gen.mutate(cands[0], mutation_type="ConstraintTightening")
        self.assertEqual(mut.generation_step, 2)
        self.assertIn("L1-016", mut.specification_ast["invariants_embodied"])
        self.assertIn(cands[0].candidate_id, mut.lineage)

        # Test recombination
        recomb = gen.recombine(cands[0], cands[1])
        self.assertIn("Hybrid", recomb.name)
        self.assertIn(cands[0].candidate_id, recomb.lineage)
        self.assertIn(cands[1].candidate_id, recomb.lineage)


class TestDecoupledAdversarialCrucible(unittest.TestCase):
    """Verifies [L1-018] Independent Decoupled Adversarial Falsification."""

    def test_stochastic_chaos_fault_injection(self):
        crucible = DecoupledAdversarialCrucible(random_seed=123)
        gen = IslandGenerator()
        cand = gen.seed_candidate("ISLAND_QUORUM")

        report = crucible.stress_test(cand, chaos_intensity=0.7)
        self.assertEqual(report.candidate_id, cand.candidate_id)
        self.assertEqual(len(report.faults_injected), 3)
        fault_types = {f["type"] for f in report.faults_injected}
        self.assertIn("ASYMMETRIC_NETSPLIT", fault_types)
        self.assertIn("FLAPPING_PACKET_DROP", fault_types)
        self.assertIn("CONCURRENCY_THRASH", fault_types)

        # Verify Landauer dissipation
        self.assertGreater(report.erased_bits, 0.0)
        self.assertGreater(report.dissipated_joules, 0.0)
        self.assertAlmostEqual(
            report.dissipated_joules,
            report.erased_bits * K_B_T_LN2,
            places=30,
        )

        # Verify SHA-256 witness hash
        self.assertEqual(len(report.witness_hash), 64)

    def test_uninsulated_baseline_falsification(self):
        # A fragile candidate (e.g. baseline without enclaves and with high chaos) produces dead-end witness
        crucible = DecoupledAdversarialCrucible(random_seed=999)
        gen = IslandGenerator()
        fragile_cand = gen.seed_candidate("ISLAND_ACTOR")

        # Stress with extreme chaos intensity
        report = crucible.stress_test(fragile_cand, chaos_intensity=1.0)
        self.assertTrue(report.is_falsified)
        self.assertFalse(report.passed)
        self.assertGreater(len(report.failure_details), 0)


class TestMapElitesQualityDiversity(unittest.TestCase):
    """Verifies Quality-Diversity MAP-Elites behavioral preservation."""

    def test_behavioral_niche_discretization_and_stepping_stone_preservation(self):
        archive = MapElitesArchive(brackets_per_dim=5)
        gen = IslandGenerator()
        c1 = gen.seed_candidate("ISLAND_SHEAF")
        c2 = gen.seed_candidate("ISLAND_CRDT")

        # Candidate 1: High consistency, high dissipation
        r1 = CrucibleReport(
            candidate_id=c1.candidate_id,
            passed=True,
            consistency_rate=0.96,
            partition_survival_rate=0.85,
            erased_bits=150.0,
            dissipated_joules=150.0 * K_B_T_LN2,
            p99_latency_ms=20.0,
        )
        # Candidate 2: Moderate consistency, low dissipation (distinct thermal niche)
        r2 = CrucibleReport(
            candidate_id=c2.candidate_id,
            passed=True,
            consistency_rate=0.87,
            partition_survival_rate=0.95,
            erased_bits=30.0,
            dissipated_joules=30.0 * K_B_T_LN2,
            p99_latency_ms=40.0,
        )

        added1 = archive.add_candidate(c1, r1)
        added2 = archive.add_candidate(c2, r2)
        self.assertTrue(added1)
        self.assertTrue(added2)

        # Both preserved despite different scalar trade-offs!
        elites = archive.get_all_elites()
        self.assertEqual(len(elites), 2)
        self.assertGreater(archive.get_coverage(), 0.0)

        winner_c, winner_r = archive.select_pareto_winner()
        self.assertIn(winner_c.candidate_id, [c1.candidate_id, c2.candidate_id])



class TestStandardizedAppStructure(unittest.TestCase):
    """Verifies compliance with the standardized /apps layout specification ([trace/domains/app_specification.domain.md])."""

    def test_axioma_flow_layout_compliance(self):
        from g1_compiler import ApplicationCompiler
        app_path = Path(__file__).parent.parent / "apps" / "axioma_flow"
        validation = ApplicationCompiler.validate_app_layout(app_path)
        self.assertTrue(validation["is_standard_compliant"], f"Layout validation failed: {validation['file_checks']}")
        self.assertEqual(validation["manifest"]["app_id"], "axioma_flow")
        self.assertEqual(validation["manifest"]["generation_origin"], "gen_01")
        self.assertIn("L1-002", validation["manifest"]["invariants_embodied"])

    def test_axioma_lexis_layout_compliance(self):
        from g1_compiler import ApplicationCompiler
        app_path = Path(__file__).parent.parent / "apps" / "axioma_lexis"
        validation = ApplicationCompiler.validate_app_layout(app_path)
        self.assertTrue(validation["is_standard_compliant"], f"Layout validation failed: {validation['file_checks']}")
        self.assertEqual(validation["manifest"]["app_id"], "axioma_lexis")
        self.assertEqual(validation["manifest"]["generation_origin"], "gen_01")
        self.assertIn("L1-002", validation["manifest"]["invariants_embodied"])
    def test_axioma_dual_fsm_layout_compliance(self):
        from g1_compiler import ApplicationCompiler
        app_path = Path(__file__).parent.parent / "apps" / "axioma_dual_fsm"
        validation = ApplicationCompiler.validate_app_layout(app_path)
        self.assertTrue(validation["is_standard_compliant"], f"Layout validation failed: {validation['file_checks']}")
        self.assertEqual(validation["manifest"]["app_id"], "axioma_dual_fsm")
        self.assertEqual(validation["manifest"]["generation_origin"], "gen_01")
        self.assertIn("L1-002", validation["manifest"]["invariants_embodied"])
        self.assertIn("L1-008", validation["manifest"]["invariants_embodied"])
        self.assertIn("L1-015", validation["manifest"]["invariants_embodied"])

    def test_axioma_crossword_layout_compliance(self):
        from g1_compiler import ApplicationCompiler
        app_path = Path(__file__).parent.parent / "apps" / "axioma_crossword"
        validation = ApplicationCompiler.validate_app_layout(app_path)
        self.assertTrue(validation["is_standard_compliant"], f"Layout validation failed: {validation['file_checks']}")
        self.assertEqual(validation["manifest"]["app_id"], "axioma_crossword")
        self.assertEqual(validation["manifest"]["generation_origin"], "gen_01")
        self.assertIn("L1-004", validation["manifest"]["invariants_embodied"])
        self.assertIn("L1-015_1", validation["manifest"]["invariants_embodied"])
        self.assertIn("L1-008", validation["manifest"]["invariants_embodied"])

    def test_axioma_eink_layout_compliance(self):
        from g1_compiler import ApplicationCompiler
        app_path = Path(__file__).parent.parent / "apps" / "axioma_eink"
        validation = ApplicationCompiler.validate_app_layout(app_path)
        self.assertTrue(validation["is_standard_compliant"], f"Layout validation failed: {validation['file_checks']}")
        self.assertEqual(validation["manifest"]["app_id"], "axioma_eink")
        self.assertEqual(validation["manifest"]["generation_origin"], "gen_01")
        self.assertIn("L1-002", validation["manifest"]["invariants_embodied"])
        self.assertIn("L1-011_3", validation["manifest"]["invariants_embodied"])
        self.assertIn("L1-016", validation["manifest"]["invariants_embodied"])

    def test_axioma_swarm_layout_compliance(self):
        from g1_compiler import ApplicationCompiler
        app_path = Path(__file__).parent.parent / "apps" / "axioma_swarm"
        validation = ApplicationCompiler.validate_app_layout(app_path)
        self.assertTrue(validation["is_standard_compliant"], f"Layout validation failed: {validation['file_checks']}")
        self.assertEqual(validation["manifest"]["app_id"], "axioma_swarm")
        self.assertEqual(validation["manifest"]["generation_origin"], "gen_01")
        self.assertIn("L1-008", validation["manifest"]["invariants_embodied"])
        self.assertIn("L1-016", validation["manifest"]["invariants_embodied"])
        self.assertIn("L1-015", validation["manifest"]["invariants_embodied"])

    def test_root_apps_symlink_and_registry(self):
        root_apps = Path(__file__).parent.parent.parent.parent / "apps"
        self.assertTrue((root_apps / "README.md").exists())
        self.assertTrue((root_apps / "axioma_flow").exists())
        self.assertTrue((root_apps / "axioma_flow" / "app.json").exists())
        self.assertTrue((root_apps / "axioma_lexis").exists())
        self.assertTrue((root_apps / "axioma_lexis" / "app.json").exists())
        self.assertTrue((root_apps / "axioma_dual_fsm").exists())
        self.assertTrue((root_apps / "axioma_dual_fsm" / "app.json").exists())
        self.assertTrue((root_apps / "axioma_crossword").exists())
        self.assertTrue((root_apps / "axioma_crossword" / "app.json").exists())
        self.assertTrue((root_apps / "axioma_eink").exists())
        self.assertTrue((root_apps / "axioma_eink" / "app.json").exists())
        self.assertTrue((root_apps / "axioma_swarm").exists())
        self.assertTrue((root_apps / "axioma_swarm" / "app.json").exists())


if __name__ == "__main__":
    unittest.main()
