"""System G1b Compiler Package.

Autonomous, constraint-enforcing software compiler grounded in S0 structural axioms,
XState v5 model-based statecharts, strict epistemic isolation, and transgenerational substrate invariants.
"""

from g1b_compiler.engine import (
    SystemG1bCompiler,
    CompilationArtifacts,
    CompilationVerificationFailure,
    GreedyCompilationViolation,
    PostEmissionExecutionFailure,
    PhantomEmissionViolation,
)
from g1b_compiler.ir.semantic_ir import SemanticDomainIR, EntitySpec, EntityField, DomainCapability, DomainInvariant, FieldType
from g1b_compiler.ir.statechart_ir import StatechartIR, StateNode, Transition, EventSpec
from g1b_compiler.ir.contract_ir import DualBoundaryContractIR, NounContract, VerbContract
from g1b_compiler.verification.model_checker import StatechartModelChecker, ModelCheckResult
from g1b_compiler.verification.viability_gate import ViabilityGate, ViabilityReport
from g1b_compiler.verification.substrate_linter import SubstrateLinter, SubstrateLintResult
from g1b_compiler.verification.post_emission_gate import PostEmissionGate, PostEmissionReport
from g1b_compiler.isolation.regulator import StructuralAxiomRegulator
from g1b_compiler.isolation.falsifier import AdversarialFalsifier
from g1b_compiler.domain_research import (
    DomainArchetype,
    DomainAxiom,
    DomainHeuristic,
    DomainBaselineReport,
    DomainBaselineViolation,
    DomainBaselineResearcher,
)

__all__ = [
    "SystemG1bCompiler",
    "CompilationArtifacts",
    "CompilationVerificationFailure",
    "GreedyCompilationViolation",
    "PostEmissionExecutionFailure",
    "PhantomEmissionViolation",
    "SemanticDomainIR",
    "EntitySpec",
    "EntityField",
    "DomainCapability",
    "DomainInvariant",
    "FieldType",
    "StatechartIR",
    "StateNode",
    "Transition",
    "EventSpec",
    "DualBoundaryContractIR",
    "NounContract",
    "VerbContract",
    "StatechartModelChecker",
    "ModelCheckResult",
    "ViabilityGate",
    "ViabilityReport",
    "SubstrateLinter",
    "SubstrateLintResult",
    "PostEmissionGate",
    "PostEmissionReport",
    "StructuralAxiomRegulator",
    "AdversarialFalsifier",
    "DomainArchetype",
    "DomainAxiom",
    "DomainHeuristic",
    "DomainBaselineReport",
    "DomainBaselineViolation",
    "DomainBaselineResearcher",
]
