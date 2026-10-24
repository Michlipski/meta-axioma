"""Milestone 4 Verification Suite: Substrate Emission & The Quine Crucible.

Verifies on the live Python 3.14 substrate:
1. [NEG-G1B-001] Anti-Phantom Emission Gate: Rejects missing target_output_dir with PhantomEmissionViolation.
2. Zero-Template IR-Driven Code Emission: Physically emits an application whose classes, invariants,
   pre/postconditions, and statechart transitions are synthesized directly from the IR, passes
   its live subprocess unittest suite, and runs `python3 run.py` cleanly.
3. Live Telemetry Cryptography: Verifies SHA-256 hash chain integrity across all compilation events
   and proves that post-hoc tampering is mathematically detected.
4. The Quine Crucible & Daughter Isolation Protocol:
   - Parent (G3b) emits Daughter (G3b') into an isolated sandbox.
   - Daughter boots in an isolated subprocess (`compile_seed.py`), ingests a novel Tier 1 SoC
     (Biologics Cold-Chain Quorum Monitor), emits a working downstream system, runs its unit tests
     in a child subprocess, and seals its own SHA-256 telemetry ledger.
"""

import copy
import json
import subprocess
import sys
import unittest
from pathlib import Path

# Add src to sys.path
SRC_DIR = Path(__file__).resolve().parent.parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from g3b_compiler import (
    SystemG3bCompiler,
    PhantomEmissionViolation,
    CryptographicTelemetryEngine,
    DynamicBudgetCalibrator,
    CognitiveRole,
    ModelTier,
    CognitiveRoutingViolation,
    SubagentExecutionViolation,
    SubagentExecutionWitness,
    DualModelRouter,
    PersonaRegistry,
    PersonaSpec,
)
from g3b_compiler.soc import (
    SituationOfConcern,
    PitchInput,
    SoCAltitude,
    Actor,
    Friction,
    FrictionSeverity,
    EnvironmentalConstraint,
    ConstraintType,
)


EPOCHS_DIR = Path(__file__).resolve().parent.parent / "epochs"


class TestMilestone4EmissionAndQuineCrucible(unittest.TestCase):
    """End-to-end empirical verification of Milestone 4, Dynamic Budget Calibration, and the Quine Daughter Isolation Protocol."""

    def test_anti_phantom_gate_rejects_missing_output_dir(self):
        """[NEG-G1B-001]: Invoking compile() without target_output_dir raises PhantomEmissionViolation."""
        compiler = SystemG3bCompiler()
        pitch = PitchInput(
            title="Phantom Test",
            elevator_pitch="Should fail immediately without target_output_dir.",
            target_audience="Auditors",
            intended_features=["Validation"],
        )
        with self.assertRaises(PhantomEmissionViolation):
            compiler.compile(seed_input=pitch, target_output_dir=None)

    def test_dynamic_budget_calibrator_accuracy(self):
        """Proves DynamicBudgetCalibrator predicts token envelopes that preserve the 60/40 invariant without 99% unspent padding."""
        clean_est = DynamicBudgetCalibrator.estimate(subsystems_count=1, expected_fault_retries=0)
        self.assertEqual(clean_est.predicted_total_spend, 4800)
        self.assertEqual(clean_est.recommended_total_budget, 7800)
        self.assertEqual(clean_est.exploratory_cap, 4680)
        self.assertEqual(clean_est.protected_floor, 3120)

        fault_est = DynamicBudgetCalibrator.estimate(subsystems_count=1, expected_fault_retries=2)
        self.assertEqual(fault_est.predicted_total_spend, 7040)
        self.assertEqual(fault_est.recommended_total_budget, 11300)
        self.assertEqual(fault_est.exploratory_cap, 6780)
        self.assertEqual(fault_est.protected_floor, 4520)

    def test_apriori_structural_scope_budget_calibration(self):
        """Proves estimate_from_structural_scope() computes accurate pre-execution budgets purely from structural graph counts without post-hoc JSON counting."""
        est = DynamicBudgetCalibrator.estimate_from_structural_scope(
            soc_tree_nodes=13,
            num_nouns=3,
            num_sub_contracts=3,
            num_composed_verbs=1,
            num_statechart_states=18,
            num_topology_nodes=3,
            num_topology_channels=2,
            num_code_leaves=1,
            expected_fault_retries=0,
        )
        self.assertEqual(est.predicted_exploratory_spend, 21314)
        self.assertEqual(est.predicted_protected_spend, 2794)
        self.assertEqual(est.predicted_total_spend, 24108)
        self.assertEqual(est.recommended_total_budget, 44500)
        self.assertEqual(est.exploratory_cap, int(44500 * 0.60))
        self.assertEqual(est.protected_floor, 44500 - est.exploratory_cap)

    def test_full_application_multi_module_budget_and_orthogonal_personas(self):
        """Proves that full production applications with multi-module scope scale to >= 100,000 tokens and support orthogonal personas."""
        # 1. Structural scope with is_full_application=True scales to >= 100,000 tokens
        est = DynamicBudgetCalibrator.estimate_from_structural_scope(
            soc_tree_nodes=15,
            num_nouns=4,
            num_sub_contracts=4,
            num_composed_verbs=2,
            num_statechart_states=18,
            num_topology_nodes=3,
            num_topology_channels=3,
            num_code_leaves=7,
            is_full_application=True,
            expected_fault_retries=2,
        )
        self.assertGreaterEqual(est.recommended_total_budget, 100000)
        self.assertEqual(est.exploratory_cap + est.protected_floor, est.recommended_total_budget)
        self.assertAlmostEqual(est.exploratory_cap / est.recommended_total_budget, 0.60, places=2)

        # 2. Verify all 7 orthogonal personas route to their certified model tiers
        brain_personas = [
            CognitiveRole.HUMAN_ERGONOMICS_ARCHITECT,
            CognitiveRole.DOMAIN_ONTOLOGIST,
            CognitiveRole.DISTRIBUTED_TOPOLOGY_ARCHITECT,
            CognitiveRole.STATECHART_FSM_ENGINEER,
        ]
        orig_argon = DualModelRouter.is_argon_enabled()
        try:
            DualModelRouter.set_argon_enabled(True)
            for role in brain_personas:
                self.assertEqual(DualModelRouter.get_authorized_model(role), ModelTier.BRAIN_ARGON)

            DualModelRouter.set_argon_enabled(False)
            for role in brain_personas:
                self.assertEqual(DualModelRouter.get_authorized_model(role), ModelTier.MUSCLE_FLASH)
        finally:
            DualModelRouter.set_argon_enabled(orig_argon)

        muscle_personas = [
            CognitiveRole.CORE_ENGINE_SYNTHESIZER,
            CognitiveRole.OPERATIONAL_DASHBOARD_SYNTHESIZER,
            CognitiveRole.ADVERSARIAL_QA_ENGINEER,
        ]
        for role in muscle_personas:
            self.assertEqual(DualModelRouter.get_authorized_model(role), ModelTier.MUSCLE_FLASH)

    def test_subagent_execution_witness_and_require_live_subagents(self):
        """Proves [L1-G3B-014] & Directive 5 enforcement of live invoke_subagent witnesses (Brain 'pro' + Muscle 'flash')."""
        out_dir = EPOCHS_DIR / "epoch_m4_hydro_valve"
        compiler = SystemG3bCompiler(compiler_id="SystemG3b_SubagentGate", total_budget=None)
        pitch = PitchInput(
            title="Autonomous Hydrostatic Pressure Valve Controller",
            elevator_pitch="Distributed pressure regulator preventing pipeline overpressure.",
            target_audience="Pipeline Safety Engineers",
            intended_features=["Pressure relief", "Quorum lock"],
        )

        # 1. require_live_subagents=True with no witnesses must raise SubagentExecutionViolation
        with self.assertRaises(SubagentExecutionViolation):
            compiler.compile(
                seed_input=pitch,
                target_output_dir=out_dir,
                soc_id="soc_hydro_valve",
                require_live_subagents=True,
            )

        # 2. Placeholder conversation_id with is_live_agy_subagent=True must raise SubagentExecutionViolation
        bad_witness = SubagentExecutionWitness(
            task_id="soc_research:soc_hydro_valve",
            subagent_role="Fake Brain",
            cognitive_role=CognitiveRole.SOC_NORMALIZATION,
            assigned_model=ModelTier.BRAIN_ARGON,
            conversation_id="mock_conv_123",
            prompt_bpe_tokens=200,
            response_bpe_tokens=400,
            is_live_agy_subagent=True,
        )
        with self.assertRaises(SubagentExecutionViolation):
            DualModelRouter.validate_subagent_witness(bad_witness)

        # 3. Wrong model tier when ENABLE_ARGON=True (Muscle 'flash' used for Brain SOC_NORMALIZATION) must raise CognitiveRoutingViolation
        wrong_tier_witness = SubagentExecutionWitness(
            task_id="soc_research:soc_hydro_valve",
            subagent_role="Misrouted Brain",
            cognitive_role=CognitiveRole.SOC_NORMALIZATION,
            assigned_model=ModelTier.MUSCLE_FLASH,
            conversation_id="9f8e7d6c-5b4a-4321-8765-abcdef012345",
            prompt_bpe_tokens=200,
            response_bpe_tokens=400,
            is_live_agy_subagent=True,
        )
        orig_argon = DualModelRouter.is_argon_enabled()
        try:
            DualModelRouter.set_argon_enabled(True)
            with self.assertRaises(CognitiveRoutingViolation):
                DualModelRouter.validate_subagent_witness(wrong_tier_witness)

            # When ENABLE_ARGON=False, Brain roles gracefully permit Flash
            DualModelRouter.set_argon_enabled(False)
            self.assertEqual(DualModelRouter.validate_subagent_witness(wrong_tier_witness), wrong_tier_witness)
        finally:
            DualModelRouter.set_argon_enabled(orig_argon)

        # 4. Valid Brain (BRAIN_ARGON) + Muscle (MUSCLE_FLASH) witnesses succeed with require_live_subagents=True
        valid_witnesses = [
            SubagentExecutionWitness(
                task_id="decompose:root_soc_hydro_valve",
                subagent_role="G3b SoC Researcher & Dialectical Architect",
                cognitive_role=CognitiveRole.DIALECTICAL_EXPLORATION,
                assigned_model=ModelTier.BRAIN_ARGON,
                conversation_id="a1b2c3d4-e5f6-4789-abcd-111122223333",
                prompt_bpe_tokens=310,
                response_bpe_tokens=620,
                is_live_agy_subagent=True,
            ),
            SubagentExecutionWitness(
                task_id="root_soc_hydro_valve.sub_0.leaf_0",
                subagent_role="G3b Leaf Synthesizer",
                cognitive_role=CognitiveRole.LEAF_CODE_EMISSION,
                assigned_model=ModelTier.MUSCLE_FLASH,
                conversation_id="b2c3d4e5-f6a7-4890-bcde-444455556666",
                prompt_bpe_tokens=420,
                response_bpe_tokens=1150,
                is_live_agy_subagent=True,
            ),
        ]
        report = compiler.compile(
            seed_input=pitch,
            target_output_dir=out_dir,
            soc_id="soc_hydro_valve",
            is_multi_node_cluster=True,
            required_invariants=["pressure_kpa <= 250", "valve_locked == True"],
            subagent_witnesses=valid_witnesses,
            require_live_subagents=True,
        )
        self.assertEqual(report["telemetry"]["live_subagents_spawned_count"], 2)
        self.assertEqual(len(report["telemetry"]["subagent_witnesses"]), 2)

    def test_zero_template_ir_driven_emission_and_cryptographic_telemetry(self):
        """Proves IR-driven code emission, calibrated budget accuracy, 1-command `python3 run.py`, and SHA-256 tamper detection."""
        out_dir = EPOCHS_DIR / "epoch_m4_hydro_valve"
        compiler = SystemG3bCompiler(compiler_id="SystemG3b_HydroVerify", total_budget=None)

        pitch = PitchInput(
            title="Autonomous Hydrostatic Pressure Valve Controller",
            elevator_pitch="Distributed pressure regulator preventing pipeline overpressure.",
            target_audience="Pipeline Safety Engineers",
            intended_features=["Pressure relief", "Quorum lock"],
        )

        report = compiler.compile(
            seed_input=pitch,
            target_output_dir=out_dir,
            soc_id="soc_hydro_valve",
            is_multi_node_cluster=True,
            required_invariants=["pressure_kpa <= 250", "valve_locked == True"],
            inject_fault_on_first_try=True,  # Exercises self-healing + fault-calibrated budget!
        )

        # 1. Verify physical files exist and are non-zero bytes
        expected_files = [
            "domain_models.py",
            "contract_service.py",
            "statechart_engine.py",
            "topology_verifier.py",
            "topology_config.json",
            "run.py",
            "tests/test_emitted_system.py",
            "telemetry_ledger.json",
            "telemetry_dashboard.md",
            "telemetry_dashboard.html",
        ]
        for rel in expected_files:
            p = out_dir / rel
            self.assertTrue(p.exists(), f"Missing emitted file: {p}")
            self.assertGreater(p.stat().st_size, 0, f"Zero-byte emitted file: {p}")

        # 2. Verify custom domain invariants are structurally compiled into domain_models.py
        models_src = (out_dir / "domain_models.py").read_text(encoding="utf-8")
        self.assertIn("pressure_kpa", models_src)
        self.assertIn("250", models_src)
        self.assertIn("valve_locked", models_src)

        # 3. Execute 1-command entrypoint `python3 run.py` in a live subprocess
        run_proc = subprocess.run(
            [sys.executable, "run.py"],
            cwd=str(out_dir),
            capture_output=True,
            text=True,
            timeout=15,
        )
        self.assertEqual(run_proc.returncode, 0, f"run.py failed: {run_proc.stderr}")
        run_json = json.loads(run_proc.stdout)
        self.assertEqual(run_json["contract_id"], "contract_soc_hydro_valve")
        self.assertTrue(run_json["final_contract_state"]["workflow_completed"])

        # 4. Verify SHA-256 Cryptographic Telemetry Chain, Calibration Accuracy, & Tamper Detection
        telemetry_data = report["telemetry"]
        self.assertTrue(CryptographicTelemetryEngine.verify_ledger_integrity(telemetry_data))

        thermo = telemetry_data["thermodynamics"]
        self.assertGreaterEqual(thermo["prediction_accuracy_pct"], 90.0)
        self.assertGreaterEqual(thermo["exploratory_utilization_pct"], 70.0)

        # Tamper with a single token number in a cloned payload and prove verification rejects it!
        tampered = copy.deepcopy(telemetry_data)
        tampered["hash_chain_events"][1]["payload"]["argon_deliberation_tokens"] = 999999
        self.assertFalse(
            CryptographicTelemetryEngine.verify_ledger_integrity(tampered),
            "Tampered telemetry ledger must fail SHA-256 hash chain verification!",
        )

    def test_the_quine_crucible_daughter_isolation_protocol(self):
        """THE ULTIMATE ACCEPTANCE TEST: Parent (G3b) emits Daughter (G3b'), which boots in an

        isolated subprocess and compiles a novel Tier 1 SoC into a verified downstream application!
        """
        quine_sandbox = EPOCHS_DIR / "epoch_m4_quine_crucible"
        compiler = SystemG3bCompiler(compiler_id="SystemG3b_Parent_Quine", total_budget=None)

        # 1. Parent SoC: System G3b's own Waterloo Situation of Concern
        parent_soc = SituationOfConcern(
            soc_id="soc_system_g3b_quine",
            title="Reflexive Universal Systems Compiler Situation of Concern",
            narrative=(
                "Software compilers must transcend single-pass mock templates and prove "
                "reflexive universality by compiling a functionally equivalent daughter compiler "
                "capable of independent downstream application synthesis in an isolated sandbox."
            ),
            altitude=SoCAltitude.MACRO,
            actors=[
                Actor(
                    name="System Architect",
                    role="Zero-Trust Escrow Authority",
                    motivations=["Reflexive self-compilation", "Cryptographic telemetry verification"],
                    frustrations=["Mock archetype templates", "Unverified in-memory claims"],
                )
            ],
            frictions=[
                Friction(
                    description="Inability of toy generators to compile self-hosting compilers",
                    severity=FrictionSeverity.CRITICAL,
                    impact="Architectural stagnation",
                )
            ],
            constraints=[
                EnvironmentalConstraint(
                    nature=ConstraintType.THERMODYNAMIC,
                    description="Strict 60/40 thermodynamic budget conservation",
                    boundary_limit="Calibrated 7,800 tokens",
                )
            ],
            unmet_needs=["Verified daughter compiler execution in isolated subprocess"],
        )

        # 2. Novel Downstream SoC fed to the Daughter Compiler in isolated subprocess
        novel_downstream_soc = SituationOfConcern(
            soc_id="soc_biologics_cold_chain",
            title="Autonomous Biologics Cold-Chain Quorum Monitor",
            narrative=(
                "Clinical biologics shipments suffer thermal excursion spoilage during multi-hop "
                "transit when sensor nodes lack local quorum validation and instant excursion lockouts."
            ),
            altitude=SoCAltitude.MACRO,
            actors=[
                Actor(
                    name="Clinical Pharmacist",
                    role="Biologics Custody Officer",
                    motivations=["Zero thermal spoilage", "Verifiable custody chain"],
                    frustrations=["Delayed cloud alerts", "Unverified sensor drift"],
                )
            ],
            frictions=[
                Friction(
                    description="Cryogenic vaccine degradation during transit handoffs",
                    severity=FrictionSeverity.CRITICAL,
                    impact="Loss of life-saving biologics",
                )
            ],
            constraints=[
                EnvironmentalConstraint(
                    nature=ConstraintType.REGULATORY,
                    description="Strict thermal envelope <= 8 Celsius",
                    boundary_limit="8C ceiling",
                )
            ],
            unmet_needs=["Multi-node quorum sensor verification and excursion lockout"],
        )

        quine_result = compiler.execute_quine_crucible(
            parent_soc=parent_soc,
            novel_downstream_soc=novel_downstream_soc,
            sandbox_root_dir=quine_sandbox,
            downstream_invariants=["temperature_celsius <= 8", "quorum_valid == True"],
        )

        # Verify Quine Certification
        self.assertEqual(quine_result["quine_status"], "CERTIFIED")
        dw = quine_result["daughter_witness"]
        self.assertEqual(dw["daughter_exit_code"], 0)
        self.assertEqual(dw["downstream_soc_id"], "soc_biologics_cold_chain")
        self.assertEqual(dw["downstream_tests_passed"], 4)
        self.assertGreater(dw["downstream_file_count"], 5)
        self.assertGreater(dw["downstream_physical_tokens"], 500)
        self.assertGreaterEqual(dw["daughter_prediction_accuracy_pct"], 95.0)
        self.assertGreaterEqual(dw["daughter_exploratory_utilization_pct"], 75.0)

        # Verify Daughter's emitted downstream app runs `python3 run.py` cleanly
        downstream_dir = Path(quine_result["downstream_app_dir"])
        downstream_run = subprocess.run(
            [sys.executable, "run.py"],
            cwd=str(downstream_dir),
            capture_output=True,
            text=True,
            timeout=15,
        )
        self.assertEqual(downstream_run.returncode, 0)
        downstream_out = json.loads(downstream_run.stdout)
        self.assertEqual(downstream_out["contract_id"], "contract_soc_biologics_cold_chain")

        # Verify both Parent and Daughter SHA-256 telemetry chains are intact
        parent_telemetry = quine_result["parent_report"]["telemetry"]
        daughter_telemetry = quine_result["daughter_ledger"]
        self.assertTrue(CryptographicTelemetryEngine.verify_ledger_integrity(parent_telemetry))
        self.assertTrue(CryptographicTelemetryEngine.verify_ledger_integrity(daughter_telemetry))
        self.assertGreaterEqual(parent_telemetry["thermodynamics"]["prediction_accuracy_pct"], 95.0)

        print(
            f"\n[QUINE DAUGHTER ISOLATION PROTOCOL CERTIFIED]:\n"
            f"  Parent Chain Head   : {parent_telemetry['chain_head_hash']}\n"
            f"  Daughter Chain Head : {daughter_telemetry['chain_head_hash']}\n"
            f"  Daughter Budget Acc : {dw['daughter_prediction_accuracy_pct']}% (Exploratory Pool: {dw['daughter_exploratory_utilization_pct']}%)\n"
            f"  Downstream Target   : {dw['downstream_soc_id']} ({dw['downstream_tests_passed']}/4 tests passing, exit_code=0)"
        )

    def test_mandatory_operational_dashboard_deliverable_enforced(self):
        """[L1-G3B-018]: Proves ProductManagerAuditor rejects plans missing dashboards and compiler physically emits dashboard.html."""
        from g3b_compiler.crucible import (
            TaskType,
            TaskNode,
            SubtaskSpec,
            DecompositionPlan,
            ProductManagerAuditor,
            DialecticalArchitectSubagent,
        )

        # 1. ProductManagerAuditor rejects code module plan lacking operational dashboard
        node = TaskNode(
            task_id="task_app_test",
            task_type=TaskType.DIALECTICAL_ARCH_DECOMPOSITION,
            description="Decompose app without dashboard",
            allocated_token_budget=10000,
            depth=1,
            payload={
                "soc": {"soc_id": "soc_test_app", "title": "Test App"},
                "require_dashboard": True,
            },
        )
        plan_no_dash = DecompositionPlan(
            parent_task_id=node.task_id,
            rationale="Plan without dashboard.",
            subtasks=[
                SubtaskSpec(
                    subtask_id=f"{node.task_id}.leaf_code",
                    task_type=TaskType.LEAF_CODE_MODULE,
                    description="Core logic only",
                    is_leaf=True,
                    budget_fraction=1.0,
                    payload={"soc_id": "soc_test_app"},
                )
            ],
        )
        verdict, _ = ProductManagerAuditor.audit(node, plan_no_dash)
        self.assertFalse(verdict.approved)
        self.assertTrue(any("[L1-G3B-018]" in v for v in verdict.blocking_violations))

        # 2. Delta update resolves missing dashboard violation
        purified, _ = DialecticalArchitectSubagent.synthesize_delta_update(
            node=node,
            current_plan=plan_no_dash,
            blocking_violations=verdict.blocking_violations,
        )
        verdict_clean, _ = ProductManagerAuditor.audit(node, purified)
        self.assertTrue(verdict_clean.approved)

        # 3. Test that SystemG3bCompiler physically emits dashboard.html into app_output_dir
        compiler = SystemG3bCompiler(compiler_id="SystemG3b_DashboardGate")
        test_app_dir = EPOCHS_DIR / "epoch_test_dashboard_app"
        test_epoch_dir = EPOCHS_DIR / "epoch_test_dashboard_epoch"
        test_app_dir.mkdir(parents=True, exist_ok=True)
        # Seed minimal auditable file
        (test_app_dir / "server.py").write_text("# Test server\n", encoding="utf-8")

        pitch = PitchInput(
            title="Dashboard Gate Test App",
            elevator_pitch="Verifying dashboard.html emission.",
            target_audience="Testers",
            intended_features=["Health check"],
        )
        report = compiler.compile(
            seed_input=pitch,
            target_output_dir=test_epoch_dir,
            app_output_dir=test_app_dir,
            soc_id="soc_test_dashboard_app",
        )

        self.assertTrue((test_epoch_dir / "telemetry_dashboard.html").exists())
        self.assertTrue((test_app_dir / "dashboard.html").exists())
        self.assertGreater((test_app_dir / "dashboard.html").stat().st_size, 100)

    def test_persona_registry_architectures_axioms_and_heuristics(self):
        """Proves that all 7 agentic personas possess distinct architectures, governing axioms,

        optimization objective functions, heuristics, and prompt scaffolds to prevent convergence.
        """
        all_specs = PersonaRegistry.list_all()
        self.assertEqual(len(all_specs), 7)

        objectives = set()
        scaffolds = set()

        for spec in all_specs:
            self.assertIsInstance(spec.role, CognitiveRole)
            self.assertTrue(len(spec.governing_axioms) >= 2, f"{spec.role} must have at least 2 formal axioms.")
            self.assertTrue(len(spec.core_heuristics) >= 3, f"{spec.role} must have at least 3 heuristics.")
            self.assertTrue(len(spec.banned_anti_patterns) >= 2, f"{spec.role} must have at least 2 anti-patterns.")
            self.assertTrue(len(spec.input_contract) > 10)
            self.assertTrue(len(spec.output_contract) > 10)
            self.assertTrue(len(spec.system_prompt_scaffold) > 50)

            # Assert non-convergence: distinct objectives and system scaffolds
            self.assertNotIn(spec.optimization_objective, objectives, f"Duplicate objective in {spec.role}")
            self.assertNotIn(spec.system_prompt_scaffold, scaffolds, f"Duplicate scaffold in {spec.role}")
            objectives.add(spec.optimization_objective)
            scaffolds.add(spec.system_prompt_scaffold)

            # Test model tier resolution with Argon flag
            if spec.tier == "Brain":
                self.assertEqual(spec.get_authorized_model(enable_argon=True), ModelTier.BRAIN_ARGON)
                self.assertEqual(spec.get_authorized_model(enable_argon=False), ModelTier.MUSCLE_FLASH)
            else:
                self.assertEqual(spec.get_authorized_model(enable_argon=True), ModelTier.MUSCLE_FLASH)
                self.assertEqual(spec.get_authorized_model(enable_argon=False), ModelTier.MUSCLE_FLASH)


if __name__ == "__main__":
    unittest.main()

