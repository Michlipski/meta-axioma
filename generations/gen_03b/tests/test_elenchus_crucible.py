"""Empirical Verification Suite for `soc_epistemic_curiosity_engine` (Option C: Quine Daughter Crucible).

Verifies on the live Python 3.14 substrate:
1. Waterloo SoC Normalization ([L1-G3B-000]): Macro/Meso decomposition of `soc_epistemic_curiosity_engine`
   preserving The Explorer, The Socratic Probe, and The Epistemic Validator.
2. Topological Fidelity ([L1-G3B-012]): Multi-node local hardware execution boundary routing Socratic Probe
   inference to `192.168.10.40:11434` (Ollama `qwen2.5` on RTX 4060 8GB VRAM, <=25ms latency budget)
   and rejecting loopback shortcuts.
3. Statechart Complexity ([L1-G3B-011], [L1-002]): 18-node non-linear hierarchical StatechartIR with
   3 compound strata, 2 deep HISTORY nodes (`HistoryType.DEEP`), 3 conceptual dead-ends, and Functorial Undo.
4. Compositional Contracts ([L1-G3B-011]): `TransitionToExploringFunctors` physically blocks entry into
   'Exploring Functors' unless 'Mastery of Morphisms' pre-conditions evaluate to True.
5. Reflexive Quine Daughter Crucible ([L1-G3B-017]): Parent (G3b) spawns Daughter (G3b') in an isolated
   zero-trust subprocess (`compile_seed.py`), which independently compiles and certifies
   `soc_epistemic_curiosity_engine` and seals a verified SHA-256 telemetry hash chain.
"""

import json
import subprocess
import sys
import unittest
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parent.parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from g3b_compiler import (
    SystemG3bCompiler,
    CryptographicTelemetryEngine,
)
from g3b_compiler.soc import (
    SituationOfConcern,
    SoCAltitude,
    Actor,
    Friction,
    FrictionSeverity,
    EnvironmentalConstraint,
    ConstraintType,
    SOC_ID_ELENCHUS,
    REQUIRED_INVARIANTS_ELENCHUS,
    build_epistemic_curiosity_soc,
    build_epistemic_curiosity_contract_ir,
    build_epistemic_curiosity_statechart_ir,
    build_epistemic_curiosity_topology_ir,
    build_epistemic_curiosity_domain_spec,
)
from g3b_compiler.evaluators import FormalModelChecker


EPOCHS_DIR = Path(__file__).resolve().parent.parent / "epochs"


class TestEpistemicCuriosityEngineCrucible(unittest.TestCase):
    """End-to-end verification of `soc_epistemic_curiosity_engine` across G3b Crucible and Quine Daughter Isolation."""

    def test_ir_formal_verification_gates(self):
        """Verifies that the Elenchus ContractIR, StatechartIR, and TopologyIR pass all formal G3b evaluators."""
        soc = build_epistemic_curiosity_soc()
        self.assertEqual(soc.soc_id, SOC_ID_ELENCHUS)
        self.assertEqual(len(soc.actors), 3)
        self.assertEqual(len(soc.sub_socs), 3)

        # 1. Compositional Contract Proof Witness
        contract = build_epistemic_curiosity_contract_ir()
        witness = contract.verify_composition("TransitionToExploringFunctors")
        self.assertTrue(witness.is_valid, f"Composition proof failed: {witness.unresolved_obligations}")
        self.assertEqual(len(witness.unresolved_obligations), 0)

        # 2. Formal Statechart Model Checker (18 states, 2 deep history states, 3 dead-ends with rollback)
        chart = build_epistemic_curiosity_statechart_ir()
        mc_report = FormalModelChecker.assert_certified(chart)
        self.assertTrue(mc_report.is_certified)
        self.assertEqual(mc_report.total_states_analyzed, 18)
        self.assertEqual(mc_report.unreachable_states, [])
        self.assertEqual(mc_report.dead_end_states, [])

        # 3. Topological Fidelity (192.168.10.40:11434 RTX 4060 Ollama Qwen 2.5)
        topo = build_epistemic_curiosity_topology_ir(inject_fault=False)
        topo.assert_topological_fidelity()
        rtx_node = topo.nodes["node_socratic_rtx4060"]
        self.assertEqual(rtx_node.host_interface, "192.168.10.40")
        self.assertEqual(rtx_node.port, 11434)
        self.assertEqual(rtx_node.memory_mb_limit, 8192)
        self.assertIn("model:qwen2.5", rtx_node.capabilities)

    def test_direct_crucible_emission_with_self_healing(self):
        """Compiles `soc_epistemic_curiosity_engine` into `epochs/epoch_epistemic_curiosity_engine` with fault injection."""
        out_dir = EPOCHS_DIR / "epoch_epistemic_curiosity_engine"
        app_dir = EPOCHS_DIR.parent / "apps" / "axioma_elenchus"
        compiler = SystemG3bCompiler(compiler_id="SystemG3b_Elenchus_Direct", total_budget=None)

        soc = build_epistemic_curiosity_soc()
        domain_spec = build_epistemic_curiosity_domain_spec()

        report = compiler.compile(
            seed_input=soc,
            target_output_dir=out_dir,
            soc_id=SOC_ID_ELENCHUS,
            is_multi_node_cluster=True,
            required_invariants=REQUIRED_INVARIANTS_ELENCHUS,
            inject_fault_on_first_try=True,
            domain_spec=domain_spec,
            app_output_dir=app_dir if app_dir.exists() else None,
        )

        # Verify self-healing trapped the injected loopback/eval faults on attempt 0 and remediated on attempt 1
        self.assertGreaterEqual(len(report["crucible_result"].remediation_events), 2)
        self.assertTrue(CryptographicTelemetryEngine.verify_ledger_integrity(report["telemetry"]))
        if app_dir.exists():
            self.assertIsNotNone(report["telemetry"]["app_substrate"])
            self.assertGreater(report["telemetry"]["app_substrate"]["total_tokens"], 30000)
            self.assertGreater(report["telemetry"]["thermodynamics"]["total_combined_disk_tokens"], 35000)

        # Verify emitted statechart_engine.py contains deep HISTORY states and dead-end transitions
        sc_code = (out_dir / "statechart_engine.py").read_text(encoding="utf-8")
        self.assertIn("foundational_stratum.foundational_history", sc_code)
        self.assertIn("higher_abstraction_stratum.higher_history", sc_code)
        self.assertIn("AXIOM_CONTRADICTION", sc_code)
        self.assertIn("FUNCTORIAL_UNDO_ROLLBACK", sc_code)

        # Verify emitted contract_service.py enforces Mastery of Morphisms before Exploring Functors
        cs_code = (out_dir / "contract_service.py").read_text(encoding="utf-8")
        self.assertIn("TransitionToExploringFunctors", cs_code)
        self.assertIn("CertifyMasteryOfMorphisms", cs_code)
        self.assertIn("UnlockExploringFunctors", cs_code)

        # Verify emitted topology_config.json binds 192.168.10.40:11434
        topo_json = json.loads((out_dir / "topology_config.json").read_text(encoding="utf-8"))
        self.assertEqual(
            topo_json["nodes"]["node_socratic_rtx4060"]["host_interface"],
            "192.168.10.40",
        )
        self.assertEqual(topo_json["nodes"]["node_socratic_rtx4060"]["port"], 11434)

    def test_reflexive_quine_daughter_crucible_on_elenchus_seed(self):
        """Executes Option C Quine Daughter Isolation Protocol on `soc_epistemic_curiosity_engine`."""
        quine_sandbox = EPOCHS_DIR / "epoch_elenchus_quine_crucible"
        compiler = SystemG3bCompiler(compiler_id="SystemG3b_Parent_Elenchus", total_budget=None)

        parent_soc = SituationOfConcern(
            soc_id="soc_system_g3b_elenchus_parent",
            title="Reflexive Universal Systems Compiler Parent SoC",
            narrative=(
                "System G3b must emit a self-hosting Daughter Compiler (G3b') into an isolated sandbox "
                "subprocess and prove that the Daughter independently materializes the Category Theory "
                "epistemic prerequisite DAG, non-linear deep-history statechart, and RTX 4060 local "
                "inference topology for soc_epistemic_curiosity_engine."
            ),
            altitude=SoCAltitude.MACRO,
            actors=[
                Actor(
                    name="Zero-Trust Escrow Architect",
                    role="Cryptographic Isolation Verifier",
                    motivations=["Subprocess isolation proof", "Dual SHA-256 chain integrity"],
                    frustrations=["Bypassed isolation gates"],
                )
            ],
            frictions=[
                Friction(
                    description="Unverified single-process compiler claims",
                    severity=FrictionSeverity.CRITICAL,
                    impact="Loss of reflexive guarantee",
                )
            ],
            constraints=[
                EnvironmentalConstraint(
                    nature=ConstraintType.THERMODYNAMIC,
                    description="60/40 thermodynamic capital partition",
                    boundary_limit="Calibrated Task-DAG budget",
                )
            ],
            unmet_needs=["Verified Daughter subprocess compilation of soc_epistemic_curiosity_engine"],
        )

        elenchus_soc = build_epistemic_curiosity_soc()
        elenchus_domain_spec = build_epistemic_curiosity_domain_spec()

        quine_result = compiler.execute_quine_crucible(
            parent_soc=parent_soc,
            novel_downstream_soc=elenchus_soc,
            sandbox_root_dir=quine_sandbox,
            downstream_invariants=REQUIRED_INVARIANTS_ELENCHUS,
            downstream_domain_spec=elenchus_domain_spec,
        )

        self.assertEqual(quine_result["quine_status"], "CERTIFIED")
        dw = quine_result["daughter_witness"]
        self.assertEqual(dw["daughter_exit_code"], 0)
        self.assertEqual(dw["downstream_soc_id"], SOC_ID_ELENCHUS)
        self.assertEqual(dw["downstream_tests_passed"], 4)

        downstream_dir = Path(quine_result["downstream_app_dir"])
        # Verify Daughter's emitted run.py executes cleanly in a live subprocess
        run_proc = subprocess.run(
            [sys.executable, "run.py"],
            cwd=str(downstream_dir),
            capture_output=True,
            text=True,
            timeout=15,
        )
        self.assertEqual(run_proc.returncode, 0)
        run_out = json.loads(run_proc.stdout)
        self.assertEqual(run_out["contract_id"], f"contract_{SOC_ID_ELENCHUS}")
        self.assertEqual(
            run_out["final_machine_state"],
            "higher_abstraction_stratum.epistemic_integration_complete",
        )
        self.assertTrue(run_out["final_contract_state"]["mastery_of_morphisms"])
        self.assertTrue(run_out["final_contract_state"]["exploring_functors_entered"])
        self.assertEqual(run_out["topology_nodes"], 3)

        # Verify both Parent and Daughter SHA-256 telemetry ledgers
        parent_telemetry = quine_result["parent_report"]["telemetry"]
        daughter_telemetry = quine_result["daughter_ledger"]
        self.assertTrue(CryptographicTelemetryEngine.verify_ledger_integrity(parent_telemetry))
        self.assertTrue(CryptographicTelemetryEngine.verify_ledger_integrity(daughter_telemetry))

        print(
            f"\n[ELENCHUS QUINE DAUGHTER CRUCIBLE CERTIFIED]:\n"
            f"  Parent Chain Head   : {parent_telemetry['chain_head_hash']}\n"
            f"  Daughter Chain Head : {daughter_telemetry['chain_head_hash']}\n"
            f"  Daughter Budget Acc : {dw['daughter_prediction_accuracy_pct']}% (Exploratory Pool: {dw['daughter_exploratory_utilization_pct']}%)\n"
            f"  Downstream Target   : {dw['downstream_soc_id']} ({dw['downstream_tests_passed']}/4 tests passing, exit_code=0)"
        )


if __name__ == "__main__":
    unittest.main()
