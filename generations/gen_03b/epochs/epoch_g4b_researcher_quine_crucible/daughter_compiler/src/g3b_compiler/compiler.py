"""Generation 3b: The Autonomous Universal Systems Compiler (`SystemG3bCompiler`).

Integrates all 4 Escrow Milestones into a unified, reflexive systems compiler:
- Milestone 1: Structural Foundations (Waterloo SoC Normalizer, StatechartIR, ContractIR, TopologyIR, ThermodynamicLedger)
- Milestone 2: The Adversaries (DualModelRouter [L1-G3B-014], FormalModelChecker, HeadlessJourneyWalker [L1-G3B-013], ZeroTrustMicroAuditors)
- Milestone 3: The Semantic Crucible (FractalTaskStack [L1-G3B-015], Stateless Subagents, Zero-Bypass Interception [L1-G3B-016])
- Milestone 4: Substrate Emission & The Quine Crucible (Zero-Template DynamicCodeEmitter, Live Cryptographic Telemetry, Daughter Isolation Protocol)
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional, Union, Callable

from .soc.models import SituationOfConcern, PitchInput, ReferenceProductInput
from .crucible.orchestrator import CrucibleOrchestrator
from .evaluators.micro_auditors import LeafArtifact, ZeroTrustMicroAuditorRegistry
from .routing.router import ModelTier, SubagentExecutionWitness
from .thermodynamics import PhysicalTokenMeter
from .emitter.dynamic_emitter import (
    DynamicCodeEmitter,
    PhantomEmissionViolation,
    PostEmissionExecutionFailure,
)
from .telemetry.cryptographic_telemetry import CryptographicTelemetryEngine


class SystemG3bCompiler:
    """The Autonomous Universal Systems Compiler (Generation 3b)."""

    def __init__(
        self,
        compiler_id: str = "SystemG3b_Parent",
        total_budget: Optional[int] = None,
        d_max: int = 5,
        b_max: int = 8,
        max_leaf_retries: int = 3,
    ):
        self.compiler_id = compiler_id
        self.total_budget = total_budget
        self.d_max = d_max
        self.b_max = b_max
        self.max_leaf_retries = max_leaf_retries

    def compile(
        self,
        seed_input: Union[SituationOfConcern, PitchInput, ReferenceProductInput],
        target_output_dir: Optional[Union[str, Path]] = None,
        soc_id: str = "soc_compiled_system",
        is_multi_node_cluster: bool = True,
        required_invariants: Optional[List[str]] = None,
        inject_fault_on_first_try: bool = False,
        daughter_witness: Optional[Dict[str, Any]] = None,
        custom_leaf_generator: Optional[Callable[[Any], str]] = None,
        domain_spec: Optional[Dict[str, Any]] = None,
        subagent_witnesses: Optional[List[SubagentExecutionWitness]] = None,
        require_live_subagents: bool = False,
        app_output_dir: Optional[Union[str, Path]] = None,
    ) -> Dict[str, Any]:
        """Compiles any seed input into a verified, runnable software system on disk with cryptographic telemetry."""
        # 1. Enforce [NEG-G1B-001] Anti-Phantom Gate upfront
        if not target_output_dir:
            raise PhantomEmissionViolation(
                "[NEG-G1B-001 Violation] SystemG3bCompiler.compile() invoked without target_output_dir."
            )

        out_dir = Path(target_output_dir).resolve()
        telemetry = CryptographicTelemetryEngine(compiler_id=self.compiler_id)

        # 2. Execute Milestone 3 Closed-Loop Semantic Crucible (calibrates budget dynamically if total_budget is None)
        orchestrator = CrucibleOrchestrator(
            total_budget=self.total_budget,
            d_max=self.d_max,
            b_max=self.b_max,
            max_leaf_retries=self.max_leaf_retries,
        )
        crucible_result = orchestrator.run_crucible(
            seed_input=seed_input,
            soc_id=soc_id,
            is_multi_node_cluster=is_multi_node_cluster,
            required_invariants=required_invariants,
            inject_fault_on_first_try=inject_fault_on_first_try,
            custom_leaf_generator=custom_leaf_generator,
            domain_spec=domain_spec,
            subagent_witnesses=subagent_witnesses,
            require_live_subagents=require_live_subagents,
        )

        telemetry.record_event("COMPILATION_INITIATED", {
            "compiler_id": self.compiler_id,
            "soc_id": soc_id,
            "total_budget": orchestrator.ledger.total_budget,
            "predicted_total_spend": orchestrator.ledger.predicted_total_spend,
            "is_multi_node_cluster": is_multi_node_cluster,
            "require_live_subagents": require_live_subagents,
            "subagent_witness_count": len(crucible_result.subagent_witnesses),
        })

        telemetry.record_event("CRUCIBLE_SYNTHESIS_CERTIFIED", {
            "certified_soc_id": crucible_result.certified_soc.soc_id,
            "verified_leaves_count": len(crucible_result.verified_leaves),
            "remediation_count": len(crucible_result.remediation_events),
            "argon_deliberation_tokens": crucible_result.argon_deliberation_tokens,
            "flash_emission_tokens": crucible_result.flash_emission_tokens,
            "argon_verification_tokens": crucible_result.argon_verification_tokens,
        })

        # 3. Execute Milestone 4 Zero-Template Dynamic Code Emission & Subprocess Test Verification
        emission_report = DynamicCodeEmitter.emit_system(
            result=crucible_result,
            target_output_dir=out_dir,
        )

        # 3b. If a full application directory (`app_output_dir`) is supplied, enforce Zero-Trust Micro-Auditing
        # and live subprocess test verification across 100% of the application directory ([L1-G3B-016], [NEG-G1B-001]).
        app_test_witness: Optional[Dict[str, Any]] = None
        app_audit_summary: Optional[Dict[str, Any]] = None
        if app_output_dir is not None:
            app_dir = Path(app_output_dir).resolve()
            if not app_dir.exists() or not app_dir.is_dir():
                raise PhantomEmissionViolation(
                    f"[NEG-G1B-001 Violation] Supplied app_output_dir '{app_dir}' does not exist."
                )
            auditable_exts = {".py", ".js", ".html", ".css"}
            audited_files_count = 0
            audited_app_tokens = 0
            for fp in sorted(app_dir.rglob("*")):
                if not fp.is_file() or "__pycache__" in fp.parts or fp.suffix not in auditable_exts:
                    continue
                content = fp.read_text(encoding="utf-8", errors="ignore")
                file_tokens = PhysicalTokenMeter.count(content)
                rel_name = str(fp.relative_to(app_dir))
                app_leaf = LeafArtifact(
                    task_id=f"app_module:{rel_name}",
                    artifact_type="code",
                    content=content,
                    emitting_model=ModelTier.MUSCLE_FLASH.value,
                    token_budget_allocated=max(16000, file_tokens + 512),
                    metadata={"is_multi_node_cluster": is_multi_node_cluster},
                )
                audit_res = ZeroTrustMicroAuditorRegistry.audit_leaf(app_leaf)
                if not audit_res.is_passed:
                    raise PostEmissionExecutionFailure(
                        f"[L1-G3B-016 Violation] Application file '{rel_name}' in '{app_dir}' failed "
                        f"Zero-Trust Micro-Audit: {audit_res.defects}"
                    )
                audited_files_count += 1
                audited_app_tokens += file_tokens

            if audited_files_count == 0:
                raise PhantomEmissionViolation(
                    f"[NEG-G1B-001 Violation] Supplied app_output_dir '{app_dir}' contains 0 auditable source files."
                )

            if (app_dir / "tests").is_dir():
                app_test_witness = DynamicCodeEmitter.execute_substrate_tests(app_dir)

            app_audit_summary = {
                "app_output_dir": str(app_dir),
                "audited_files_count": audited_files_count,
                "audited_app_tokens": audited_app_tokens,
                "app_test_witness": app_test_witness,
            }
            telemetry.record_event("APP_SUBSTRATE_AUDITED_AND_VERIFIED", app_audit_summary)

        # 4. Seal and emit Live Cryptographic Telemetry Ledger & Dashboard
        telemetry_payload = telemetry.emit_telemetry_artifacts(
            output_dir=out_dir,
            soc_id=crucible_result.certified_soc.soc_id,
            ledger=orchestrator.ledger,
            argon_deliberation_tokens=crucible_result.argon_deliberation_tokens,
            flash_emission_tokens=crucible_result.flash_emission_tokens,
            argon_verification_tokens=crucible_result.argon_verification_tokens,
            remediation_events=crucible_result.remediation_events,
            stack_trace=crucible_result.stack_trace,
            test_execution_witness=emission_report["test_witness"],
            daughter_witness=daughter_witness,
            subagent_witnesses=crucible_result.subagent_witnesses,
            app_output_dir=app_output_dir,
            app_test_witness=app_test_witness,
        )

        # 5. Verify physical emission of operational dashboard deliverable [L1-G3B-018]
        if app_output_dir is not None:
            app_path = Path(app_output_dir).resolve()
            dashboard_file = app_path / "dashboard.html"
            telemetry_html = app_path / "telemetry_dashboard.html"
            if not dashboard_file.exists() and not telemetry_html.exists():
                raise PhantomEmissionViolation(
                    f"[L1-G3B-018 Violation] Application '{app_path.name}' in '{app_path}' lacks "
                    "mandatory live operational dashboard (neither dashboard.html nor telemetry_dashboard.html found)."
                )

        return {
            "compiler_id": self.compiler_id,
            "soc_id": crucible_result.certified_soc.soc_id,
            "crucible_result": crucible_result,
            "emission": emission_report,
            "app_audit": app_audit_summary,
            "telemetry": telemetry_payload,
        }

    def execute_quine_crucible(
        self,
        parent_soc: SituationOfConcern,
        novel_downstream_soc: SituationOfConcern,
        sandbox_root_dir: Union[str, Path],
        downstream_invariants: Optional[List[str]] = None,
        downstream_domain_spec: Optional[Dict[str, Any]] = None,
        subagent_witnesses: Optional[List[SubagentExecutionWitness]] = None,
        require_live_subagents: bool = False,
        inject_fault_on_first_try: bool = False,
        app_output_dir: Optional[Union[str, Path]] = None,
    ) -> Dict[str, Any]:
        """Executes The Quine Crucible under the Daughter Isolation Protocol.

        1. Parent (G3b) synthesizes and emits the Daughter Compiler (G3b') into `sandbox_root_dir/daughter_compiler`.
        2. Writes `novel_downstream_soc` to `sandbox_root_dir/novel_seed_soc.json`.
        3. Boots the Daughter Compiler in a completely isolated subprocess (`compile_seed.py`),
           instructing it to compile `novel_seed_soc.json` into `sandbox_root_dir/downstream_app`.
        4. Audits the Daughter's physical exit code, downstream test witness, and SHA-256 telemetry chain.
        5. Emits the Parent's self-compiled artifact and seals the Parent-Daughter cryptographic telemetry witness.
        """
        sandbox_root = Path(sandbox_root_dir).resolve()
        sandbox_root.mkdir(parents=True, exist_ok=True)

        daughter_compiler_dir = sandbox_root / "daughter_compiler"
        downstream_app_dir = sandbox_root / "downstream_app"
        parent_output_dir = sandbox_root / "parent_self_compiled"

        # 1. Materialize self-hosting Daughter Compiler (G3b') into isolated sandbox
        cli_path = DynamicCodeEmitter.emit_daughter_compiler(daughter_compiler_dir)

        # 2. Serialize novel Tier 1 SoC seed for the Daughter
        seed_payload = novel_downstream_soc.to_dict()
        seed_payload["required_invariants"] = downstream_invariants or [
            "temperature_celsius <= 8",
            "quorum_valid == True",
        ]
        seed_payload["is_multi_node_cluster"] = True
        seed_payload["inject_fault_on_first_try"] = inject_fault_on_first_try
        seed_payload["require_live_subagents"] = require_live_subagents
        if subagent_witnesses is not None:
            seed_payload["subagent_witnesses"] = [w.to_dict() for w in subagent_witnesses]
        if app_output_dir is not None:
            seed_payload["app_output_dir"] = str(Path(app_output_dir).resolve())
        if downstream_domain_spec is not None:
            seed_payload["domain_spec"] = downstream_domain_spec
        seed_json_path = sandbox_root / "novel_seed_soc.json"
        seed_json_path.write_text(json.dumps(seed_payload, indent=2), encoding="utf-8")

        # 3. Boot Daughter Compiler in an isolated subprocess
        cmd = [
            sys.executable,
            str(cli_path),
            "--soc-json",
            str(seed_json_path),
            "--output-dir",
            str(downstream_app_dir),
        ]
        if self.total_budget is not None:
            cmd.extend(["--budget", str(self.total_budget // 2)])

        daughter_proc = subprocess.run(
            cmd,
            cwd=str(daughter_compiler_dir),
            capture_output=True,
            text=True,
            timeout=60,
        )

        if daughter_proc.returncode != 0:
            raise PostEmissionExecutionFailure(
                f"Quine Daughter Compiler subprocess failed (exit_code={daughter_proc.returncode}):\n"
                f"STDOUT:\n{daughter_proc.stdout}\nSTDERR:\n{daughter_proc.stderr}"
            )

        # 4. Hostile Zero-Trust Audit of the Daughter's emitted downstream artifacts & telemetry
        daughter_ledger_path = downstream_app_dir / "telemetry_ledger.json"
        daughter_dashboard_path = downstream_app_dir / "telemetry_dashboard.md"
        if not daughter_ledger_path.exists() or not daughter_dashboard_path.exists():
            raise PhantomEmissionViolation(
                "Daughter compiler failed to emit telemetry_ledger.json or telemetry_dashboard.md."
            )

        daughter_ledger_data = json.loads(daughter_ledger_path.read_text(encoding="utf-8"))
        if not CryptographicTelemetryEngine.verify_ledger_integrity(daughter_ledger_data):
            raise PostEmissionExecutionFailure(
                "Daughter compiler telemetry SHA-256 hash chain failed cryptographic verification!"
            )

        daughter_witness = {
            "daughter_compiler_id": daughter_ledger_data["compiler_id"],
            "daughter_exit_code": daughter_proc.returncode,
            "downstream_soc_id": novel_downstream_soc.soc_id,
            "daughter_chain_head_hash": daughter_ledger_data["chain_head_hash"],
            "downstream_file_count": daughter_ledger_data["disk_substrate"]["file_count"],
            "downstream_physical_tokens": daughter_ledger_data["disk_substrate"]["total_tokens"],
            "downstream_tests_passed": daughter_ledger_data["test_execution_witness"]["tests_run"],
            "daughter_total_budget": daughter_ledger_data["thermodynamics"]["total_budget"],
            "daughter_predicted_spend": daughter_ledger_data["thermodynamics"].get("predicted_total_spend"),
            "daughter_prediction_accuracy_pct": daughter_ledger_data["thermodynamics"].get("prediction_accuracy_pct"),
            "daughter_exploratory_utilization_pct": daughter_ledger_data["thermodynamics"].get("exploratory_utilization_pct"),
            "daughter_exploratory_spent": daughter_ledger_data["thermodynamics"]["exploratory_spent"],
            "daughter_protected_spent": daughter_ledger_data["thermodynamics"]["protected_spent"],
            "daughter_live_subagents_verified": daughter_ledger_data.get("live_subagents_spawned_count", 0),
        }

        # 5. Compile Parent's own self-representation and bind the Daughter Witness into Parent's chain
        parent_report = self.compile(
            seed_input=parent_soc,
            target_output_dir=parent_output_dir,
            soc_id=parent_soc.soc_id,
            is_multi_node_cluster=True,
            required_invariants=["daughter_exit_code == 0", "downstream_app_verified == True"],
            daughter_witness=daughter_witness,
            subagent_witnesses=subagent_witnesses,
            require_live_subagents=require_live_subagents,
        )

        return {
            "quine_status": "CERTIFIED",
            "parent_report": parent_report,
            "daughter_witness": daughter_witness,
            "daughter_ledger": daughter_ledger_data,
            "downstream_app_dir": str(downstream_app_dir),
            "daughter_compiler_dir": str(daughter_compiler_dir),
        }

