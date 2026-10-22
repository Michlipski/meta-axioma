"""Main Compilation Orchestrator Engine for System G1b.

Orchestrates multi-phase compilation from high-level product intent to verified production software.
Enforces:
1. Anti-Greedy Decoupling (Spec -> Semantic IR -> Statechart IR -> Contract IR -> Target Code).
2. Model-Based Flow Verification (XState v5 reachability, 100% edge coverage, negative tests).
3. Strict Epistemic Isolation (Regulator vs Falsifier vs Workers).
4. Pareto Viability & Error Recovery Cycles.
5. Transgenerational Substrate Invariants (Anti-Mock, Clean-Slate, Visual Dignity).
"""

from dataclasses import dataclass, field
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from g1b_compiler.ir.semantic_ir import SemanticDomainIR
from g1b_compiler.ir.statechart_ir import StatechartIR
from g1b_compiler.ir.contract_ir import DualBoundaryContractIR
from g1b_compiler.isolation.regulator import StructuralAxiomRegulator, RegulationAuditResult
from g1b_compiler.isolation.falsifier import AdversarialFalsifier, FalsificationSuite
from g1b_compiler.verification.model_checker import StatechartModelChecker, ModelCheckResult
from g1b_compiler.verification.viability_gate import ViabilityGate, ViabilityReport
from g1b_compiler.verification.substrate_linter import SubstrateLinter, SubstrateLintResult
from g1b_compiler.verification.post_emission_gate import (
    PostEmissionGate,
    PostEmissionReport,
    PostEmissionExecutionFailure,
    PhantomEmissionViolation,
)
from g1b_compiler.domain_research import (
    DomainBaselineResearcher,
    DomainBaselineReport,
    DomainBaselineViolation,
    DomainArchetype,
)


class GreedyCompilationViolation(Exception):
    """Raised when an attempt is made to bypass intermediate IR stages."""
    pass


class CompilationVerificationFailure(Exception):
    """Raised when a candidate system fails model-checking or viability gating."""
    pass


from g1b_compiler.emission.ast_emitter import TargetCodeEmitter


@dataclass
class CompilationArtifacts:
    semantic_ir: SemanticDomainIR
    statechart_ir: StatechartIR
    contract_ir: DualBoundaryContractIR
    model_check_result: ModelCheckResult
    viability_report: ViabilityReport
    falsification_suite: FalsificationSuite
    regulation_result: RegulationAuditResult
    substrate_lint_result: SubstrateLintResult
    output_directory: Optional[Path] = None
    emitted_files: Dict[str, Path] = field(default_factory=dict)
    post_emission_report: Optional[PostEmissionReport] = None
    domain_baseline_report: Optional[DomainBaselineReport] = None


class SystemG1bCompiler:
    """The Generation 1b Autonomous Meta-Compiler."""

    def __init__(self):
        self.regulator = StructuralAxiomRegulator()
        self.linter = SubstrateLinter()
        self.emitter = TargetCodeEmitter()
        self.post_emission_gate = PostEmissionGate()
        self.domain_researcher = DomainBaselineResearcher()

    def compile(
        self,
        semantic_ir: SemanticDomainIR,
        statechart_ir: StatechartIR,
        contract_ir: DualBoundaryContractIR,
        target_output_dir: Optional[Path] = None,
        max_steps_to_value: int = 3,
        port: int = 8090,
        allow_dry_run: bool = False,
        audit_domain_baseline: bool = True
    ) -> CompilationArtifacts:
        """Executes full multi-phase compilation pipeline."""

        # --- Invariant Gate [NEG-G1B-001]: Anti-Phantom Emission Gate ---
        if target_output_dir is None:
            if not allow_dry_run:
                raise PhantomEmissionViolation(
                    "[NEG-G1B-001 Violation] Compilation rejected: Physical code emission target (`target_output_dir`) is mandatory. "
                    "Autonomous compilers and agents cannot declare software compiled without emitting physical code "
                    "and executing post-emission runtime verification. Pass `allow_dry_run=True` to explicitly permit "
                    "abstract verification without physical emission."
                )

        # --- Phase 0: Domain Baseline Research & Grounding ---
        domain_baseline_report: Optional[DomainBaselineReport] = None
        if audit_domain_baseline:
            domain_baseline_report = self.domain_researcher.analyze_and_audit(
                semantic_ir=semantic_ir,
                statechart_ir=statechart_ir,
                strict=True
            )

        # --- Phase 1: Structural Regulation Audit ---
        reg_result = self.regulator.audit_specification(semantic_ir, contract_ir)
        if not reg_result.is_compliant:
            raise CompilationVerificationFailure(
                f"Specification failed Structural Axiom Regulation: {'; '.join(reg_result.audit_notes)}"
            )

        # --- Phase 2: Decoupled Adversarial Falsification ---
        falsifier = AdversarialFalsifier(statechart_ir, contract_ir)
        falsification_suite = falsifier.synthesize_suite()

        # --- Phase 3: Model-Based Statechart Verification (XState Formalism) ---
        checker = StatechartModelChecker(statechart_ir)
        model_result = checker.run_full_check()
        if not model_result.is_valid:
            raise CompilationVerificationFailure(
                f"Statechart model checking failed: {'; '.join(model_result.errors)}"
            )

        # --- Phase 4: Pareto & Product Viability Gating ---
        viability_gate = ViabilityGate(statechart_ir, max_steps_to_value=max_steps_to_value)
        viability_report = viability_gate.evaluate()
        if not viability_report.passed:
            raise CompilationVerificationFailure(
                f"Viability gate rejected statechart: {'; '.join(viability_report.violations)}"
            )

        # --- Phase 5: Concrete Target Code Emission ---
        emitted_files: Dict[str, Path] = {}
        combined_source = ""
        if target_output_dir is not None:
            target_output_dir = Path(target_output_dir)
            emitted_files = self.emitter.emit_application(
                semantic_ir=semantic_ir,
                statechart_ir=statechart_ir,
                contract_ir=contract_ir,
                output_dir=target_output_dir,
                port=port
            )
            # Gather emitted source text for substrate linting
            for path in emitted_files.values():
                if path.suffix in [".html", ".js", ".css", ".py"]:
                    combined_source += "\n" + path.read_text(encoding="utf-8")

        # --- Phase 6: Substrate Quality & Anti-Mock Linter ---
        substrate_result = self.linter.evaluate(
            source_code=combined_source,
            seeds=semantic_ir.initial_clean_seeds
        )
        if not substrate_result.passed:
            raise CompilationVerificationFailure(
                f"Substrate invariant failed on emitted code: {'; '.join(substrate_result.violations)}"
            )

        # --- Phase 7: Mandatory Post-Emission Manifest & Runtime Execution Gate ---
        post_emission_report: Optional[PostEmissionReport] = None
        if target_output_dir is not None:
            post_emission_report = self.post_emission_gate.verify_and_execute(target_output_dir)

        artifacts = CompilationArtifacts(
            semantic_ir=semantic_ir,
            statechart_ir=statechart_ir,
            contract_ir=contract_ir,
            model_check_result=model_result,
            viability_report=viability_report,
            falsification_suite=falsification_suite,
            regulation_result=reg_result,
            substrate_lint_result=substrate_result,
            output_directory=target_output_dir,
            emitted_files=emitted_files,
            post_emission_report=post_emission_report,
            domain_baseline_report=domain_baseline_report
        )

        return artifacts
