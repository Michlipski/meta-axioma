#!/usr/bin/env python3
"""Parent G3b Compiler Orchestration Script for `soc_byzantine_kinetic_facade`.

Executes:
1. Reflexive Quine Daughter Isolation Protocol (`[L1-G3B-017]`)
2. Parent Closed-Loop Semantic Crucible with Self-Healing Remediation (`[L1-G3B-016]`)
3. Zero-Template IR-Driven Emission & Subprocess Test Verification (`[NEG-G1B-001]`)
4. Full Application Directory Audit across 100% of files
5. Cryptographic Telemetry Ledger & Dashboard Emission
"""

import json
from pathlib import Path
import subprocess
import sys

G3B_ROOT = Path(__file__).resolve().parent
SRC_DIR = G3B_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from g3b_compiler.compiler import SystemG3bCompiler
from g3b_compiler.soc.models import (
    SituationOfConcern,
    SoCAltitude,
    Actor,
    Friction,
    FrictionSeverity,
    EnvironmentalConstraint,
    ConstraintType,
)
from g3b_compiler.soc.facade_seed import (
    build_kinetic_facade_soc,
    build_kinetic_facade_domain_spec,
    REQUIRED_INVARIANTS_FACADE,
)
from g3b_compiler.routing.router import (
    CognitiveRole,
    ModelTier,
    SubagentExecutionWitness,
)
from g3b_compiler.telemetry.cryptographic_telemetry import CryptographicTelemetryEngine


def main():
    print("=" * 80)
    print("SYSTEM G3b COMPILER: AXIOMA KINETIC FAÇADE (`soc_byzantine_kinetic_facade`)")
    print("=" * 80)

    # 1. Register Verified Live Subagent Witnesses ([L1-G3B-014])
    witnesses = [
        SubagentExecutionWitness(
            task_id="decompose:root_soc_byzantine_kinetic_facade",
            subagent_role="G3b Dialectical Architect & SoC Researcher",
            cognitive_role=CognitiveRole.DIALECTICAL_EXPLORATION,
            assigned_model=ModelTier.BRAIN_ARGON,
            conversation_id="66538545-8e57-430d-84af-d7a8d49da5b1",
            prompt_bpe_tokens=833,
            response_bpe_tokens=3250,
            is_live_agy_subagent=True,
        ),
        SubagentExecutionWitness(
            task_id="leaf:core_p2p_mesh_engine_and_pbft_consensus",
            subagent_role="G3b Leaf Synthesizer - Core Mesh Engine",
            cognitive_role=CognitiveRole.LEAF_CODE_EMISSION,
            assigned_model=ModelTier.MUSCLE_FLASH,
            conversation_id="25547f4a-536b-47d7-bdb5-f2850cbeb5df",
            prompt_bpe_tokens=607,
            response_bpe_tokens=2850,
            is_live_agy_subagent=True,
        ),
        SubagentExecutionWitness(
            task_id="leaf:2d_diagnostic_ui_and_verification_suite",
            subagent_role="G3b Leaf Synthesizer - 2D UI & Tests",
            cognitive_role=CognitiveRole.LEAF_CODE_EMISSION,
            assigned_model=ModelTier.MUSCLE_FLASH,
            conversation_id="b520625c-5986-4fe8-8c53-618015d6a68e",
            prompt_bpe_tokens=758,
            response_bpe_tokens=3450,
            is_live_agy_subagent=True,
        ),
    ]

    facade_soc = build_kinetic_facade_soc()
    facade_domain_spec = build_kinetic_facade_domain_spec()

    parent_soc = SituationOfConcern(
        soc_id="soc_system_g3b_facade_quine",
        title="Axioma Kinetic Façade Quine Self-Compilation",
        narrative=(
            "Generation 3b parent compiler executes recursive self-compilation and compiles "
            "the daughter compiler in an isolated sandbox under the Daughter Isolation Protocol."
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
        unmet_needs=["Verified Daughter subprocess compilation of soc_byzantine_kinetic_facade"],
    )

    epochs_dir = G3B_ROOT / "epochs"
    quine_sandbox_dir = epochs_dir / "epoch_byzantine_kinetic_facade_quine_crucible"
    target_output_dir = epochs_dir / "epoch_byzantine_kinetic_facade"
    app_output_dir = G3B_ROOT / "apps" / "axioma_kinetic_facade"

    compiler = SystemG3bCompiler(
        compiler_id="SystemG3b_Parent",
        total_budget=None,  # Calibrated via DynamicBudgetCalibrator
    )

    # 2. Execute Milestone 4 Quine Daughter Isolation Protocol ([L1-G3B-017])
    print("\n[STEP 1]: Executing Quine Daughter Isolation Protocol...")
    quine_result = compiler.execute_quine_crucible(
        parent_soc=parent_soc,
        novel_downstream_soc=facade_soc,
        sandbox_root_dir=quine_sandbox_dir,
        downstream_invariants=REQUIRED_INVARIANTS_FACADE,
        downstream_domain_spec=facade_domain_spec,
        subagent_witnesses=witnesses,
        require_live_subagents=True,
        app_output_dir=app_output_dir,
    )
    print("  ✅ Quine Daughter Crucible Certified!")
    print(f"  Daughter Chain Head: {quine_result['daughter_ledger']['chain_head_hash']}")

    # 3. Execute Parent Compiler
    print("\n[STEP 2]: Executing Parent Compiler with Self-Healing Remediation...")
    report = compiler.compile(
        seed_input=facade_soc,
        target_output_dir=target_output_dir,
        app_output_dir=app_output_dir,
        soc_id=facade_soc.soc_id,
        is_multi_node_cluster=True,
        required_invariants=REQUIRED_INVARIANTS_FACADE,
        inject_fault_on_first_try=True,
        daughter_witness=quine_result["daughter_witness"],
        domain_spec=facade_domain_spec,
        subagent_witnesses=witnesses,
        require_live_subagents=True,
    )

    # 4. Telemetry Integrity Verification
    telemetry = report["telemetry"]
    is_valid = CryptographicTelemetryEngine.verify_ledger_integrity(telemetry)
    print(f"\n[STEP 3]: Telemetry Chain Head: {telemetry['chain_head_hash']}")
    print(f"  Ledger Integrity Verified: {is_valid}")
    assert is_valid, "Cryptographic telemetry integrity check failed!"

    # 5. Run Entrypoint Verification
    print("\n[STEP 4]: Verifying Emitted Epoch Entrypoint...")
    run_proc = subprocess.run(
        [sys.executable, "run.py"],
        cwd=str(target_output_dir),
        capture_output=True,
        text=True,
        timeout=15,
    )
    print(f"  Epoch run.py exit code: {run_proc.returncode}")
    assert run_proc.returncode == 0, f"run.py failed: {run_proc.stderr}"
    print(f"  Epoch output: {run_proc.stdout.strip()}")

    print("\n" + "=" * 80)
    print("COMPILATION & CERTIFICATION COMPLETED SUCCESSFULLY!")
    print(f"Epoch Directory : {target_output_dir}")
    print(f"App Directory   : {app_output_dir}")
    print("=" * 80)


if __name__ == "__main__":
    main()
