#!/usr/bin/env python3
"""Parent G3b Compiler Orchestration Script for `soc_g4b_researcher`.

Option C: Zenith Apex Epistemic Crucible & Universal Research Substrate

Executes:
1. Register live subagent execution witnesses ([L1-G3B-014])
2. Reflexive Quine Daughter Isolation Protocol ([L1-G3B-017])
3. Parent Closed-Loop Semantic Crucible with Self-Healing Remediation ([L1-G3B-016])
4. Zero-Template IR-Driven Emission & Subprocess Test Verification ([NEG-G1B-001])
5. Full Application Directory Audit across 100% of files
6. Cryptographic Telemetry Ledger & Dashboard Emission ([L1-G3B-018])
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
from g3b_compiler.soc.researcher_seed import (
    build_researcher_soc,
    build_researcher_domain_spec,
    REQUIRED_INVARIANTS_RESEARCHER,
)
from g3b_compiler.routing.router import (
    CognitiveRole,
    ModelTier,
    SubagentExecutionWitness,
)
from g3b_compiler.telemetry.cryptographic_telemetry import CryptographicTelemetryEngine


def main():
    print("=" * 80)
    print("SYSTEM G3b COMPILER: G4b RESEARCH SERVICE (`soc_g4b_researcher`)")
    print("OPTION C: ZENITH APEX EPISTEMIC CRUCIBLE & UNIVERSAL RESEARCH SUBSTRATE")
    print("=" * 80)

    # 1. Register Verified Live Subagent Witnesses ([L1-G3B-014])
    witnesses = [
        SubagentExecutionWitness(
            task_id="decompose:root_soc_g4b_researcher",
            subagent_role="Brain Tier Lead Architect & Epistemic Researcher",
            cognitive_role=CognitiveRole.HUMAN_ERGONOMICS_ARCHITECT,
            assigned_model=ModelTier.MUSCLE_FLASH,
            conversation_id="92a9998a-2561-4cdf-a4c5-5822aa285f32",
            prompt_bpe_tokens=1850,
            response_bpe_tokens=9150,
            is_live_agy_subagent=True,
            task_description="Stage 1: Problem Discovery, Formal Contract Proofs, and Architectural Blueprinting",
        ),
        SubagentExecutionWitness(
            task_id="leaf:core_backend_and_functorial_statechart_engine",
            subagent_role="Core Backend & Functorial Engine Synthesizer",
            cognitive_role=CognitiveRole.CORE_ENGINE_SYNTHESIZER,
            assigned_model=ModelTier.MUSCLE_FLASH,
            conversation_id="fc55df09-febe-4bb1-9859-8d61f1eb510d",
            prompt_bpe_tokens=2100,
            response_bpe_tokens=30350,
            is_live_agy_subagent=True,
            task_description="Stage 2: 18 Domain Nouns, 12 Core Backend Modules, 32-State XState v5 Engine",
        ),
        SubagentExecutionWitness(
            task_id="leaf:operational_dashboard_and_telemetry_engine",
            subagent_role="Operational Dashboard & Telemetry Synthesizer",
            cognitive_role=CognitiveRole.OPERATIONAL_DASHBOARD_SYNTHESIZER,
            assigned_model=ModelTier.MUSCLE_FLASH,
            conversation_id="a00859bd-0866-467a-bc8b-0371ca409a6d",
            prompt_bpe_tokens=1450,
            response_bpe_tokens=20730,
            is_live_agy_subagent=True,
            task_description="Stage 2: Standalone Development Process Telemetry Dashboard deliverable",
        ),
        SubagentExecutionWitness(
            task_id="leaf:adversarial_test_and_byzantine_qa_suite",
            subagent_role="Adversarial Test & Byzantine QA Engineer",
            cognitive_role=CognitiveRole.ADVERSARIAL_QA_ENGINEER,
            assigned_model=ModelTier.MUSCLE_FLASH,
            conversation_id="5ce2505f-ee32-41d9-972f-c7fcfacc06c8",
            prompt_bpe_tokens=1650,
            response_bpe_tokens=17270,
            is_live_agy_subagent=True,
            task_description="Stage 2: 29-test empirical adversarial test suite across 7 pillars",
        ),
    ]

    researcher_soc = build_researcher_soc()
    researcher_domain_spec = build_researcher_domain_spec()

    parent_soc = SituationOfConcern(
        soc_id="soc_system_g3b_researcher_quine",
        title="G4b Research Service Quine Self-Compilation",
        narrative=(
            "Generation 3b parent compiler executes recursive self-compilation and compiles "
            "the daughter compiler in an isolated sandbox under the Daughter Isolation Protocol "
            "to certify sovereign G4b Research Service compilation."
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
                boundary_limit="Calibrated 982,300 BPE tokens",
            )
        ],
        unmet_needs=["Verified Daughter subprocess compilation of soc_g4b_researcher"],
    )

    epochs_dir = G3B_ROOT / "epochs"
    quine_sandbox_dir = epochs_dir / "epoch_g4b_researcher_quine_crucible"
    target_output_dir = epochs_dir / "epoch_g4b_researcher"
    app_output_dir = G3B_ROOT / "apps" / "soc_g4b_researcher"

    compiler = SystemG3bCompiler(
        compiler_id="SystemG3b_Parent",
        total_budget=982300,
    )

    # 2. Execute Milestone 4 Quine Daughter Isolation Protocol ([L1-G3B-017])
    print("\n[STEP 1]: Executing Quine Daughter Isolation Protocol...")
    quine_result = compiler.execute_quine_crucible(
        parent_soc=parent_soc,
        novel_downstream_soc=researcher_soc,
        sandbox_root_dir=quine_sandbox_dir,
        downstream_invariants=REQUIRED_INVARIANTS_RESEARCHER,
        downstream_domain_spec=researcher_domain_spec,
        subagent_witnesses=witnesses,
        require_live_subagents=True,
        app_output_dir=app_output_dir,
    )
    print("  ✅ Quine Daughter Crucible Certified!")
    print(f"  Daughter Chain Head: {quine_result['daughter_ledger']['chain_head_hash']}")

    # 3. Execute Parent Compiler with Self-Healing
    print("\n[STEP 2]: Executing Parent Compiler with Self-Healing Remediation...")
    report = compiler.compile(
        seed_input=researcher_soc,
        target_output_dir=target_output_dir,
        app_output_dir=app_output_dir,
        soc_id=researcher_soc.soc_id,
        is_multi_node_cluster=True,
        required_invariants=REQUIRED_INVARIANTS_RESEARCHER,
        inject_fault_on_first_try=True,
        daughter_witness=quine_result["daughter_witness"],
        domain_spec=researcher_domain_spec,
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
    print(f"  Epoch output summary: {run_proc.stdout.strip().splitlines()[-1]}")

    print("\n" + "=" * 80)
    print("COMPILATION & CERTIFICATION COMPLETED SUCCESSFULLY!")
    print(f"Epoch Directory : {target_output_dir}")
    print(f"App Directory   : {app_output_dir}")
    print("=" * 80)


if __name__ == "__main__":
    main()
