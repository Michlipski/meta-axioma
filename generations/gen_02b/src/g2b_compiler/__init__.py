"""System G2b Compiler Package.

Autonomous, constraint-enforcing software compiler grounded in:
1. Multi-Tier Axiom Matrix ([L1-G2B-001])
2. Stateful Human Overrides ([L1-G2B-002])
3. Dynamic Weighted Recursion & Worker Taxonomy ([L1-G2B-003])
4. Thermodynamic Capital Partitioning ([L1-G2B-004])
5. Ambitious Discovery & Deliberate Scope-Cutting ([L1-G2B-005])
6. Anti-Phantom Emission Gate & Mandatory Runtime Witness ([NEG-G1B-001])
"""

from g2b_compiler.engine import (
    SystemG2bCompiler,
    CompilationArtifacts,
    CompilationVerificationFailure,
    GreedyCompilationViolation,
    PostEmissionExecutionFailure,
    PhantomEmissionViolation,
)
from g2b_compiler.ir.semantic_ir import (
    SemanticDomainIR,
    EntitySpec,
    EntityField,
    DomainCapability,
    DomainInvariant,
    FieldType,
)
from g2b_compiler.ir.statechart_ir import StatechartIR, StateNode, Transition, EventSpec
from g2b_compiler.ir.contract_ir import DualBoundaryContractIR, NounContract, VerbContract
from g2b_compiler.verification.model_checker import StatechartModelChecker, ModelCheckResult
from g2b_compiler.verification.viability_gate import ViabilityGate, ViabilityReport
from g2b_compiler.verification.substrate_linter import SubstrateLinter, SubstrateLintResult
from g2b_compiler.verification.post_emission_gate import PostEmissionGate, PostEmissionReport
from g2b_compiler.verification.multi_tier_gate import MultiTierInterlockingGate
from g2b_compiler.isolation.regulator import StructuralAxiomRegulator, RegulationAuditResult
from g2b_compiler.isolation.falsifier import AdversarialFalsifier, FalsificationSuite
from g2b_compiler.matrix.models import MultiTierAuditResult, MultiTierAxiomViolation
from g2b_compiler.matrix.heuristics import UsabilityHeuristicAuditor, UNIVERSAL_USABILITY_HEURISTICS
from g2b_compiler.overrides.registry import StatefulOverrideRegistry, HeuristicExemption
from g2b_compiler.recursion.models import WorkerType, RecursionNode, BoundaryOpinion, get_max_recursion_depth
from g2b_compiler.recursion.cost_allocator import ThermodynamicCostAllocator, OutOfProtectedCapitalError, OutOfExploratoryCapitalError
from g2b_compiler.recursion.tree_visualizer import RecursionTreeVisualizer
from g2b_compiler.negotiation.protocol import ScopeNegotiationProtocol, AmbitiousScopeDossier
from g2b_compiler.emission.ast_emitter import TargetCodeEmitterG2b

__all__ = [
    "SystemG2bCompiler",
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
    "MultiTierInterlockingGate",
    "StructuralAxiomRegulator",
    "RegulationAuditResult",
    "AdversarialFalsifier",
    "FalsificationSuite",
    "MultiTierAuditResult",
    "MultiTierAxiomViolation",
    "UsabilityHeuristicAuditor",
    "UNIVERSAL_USABILITY_HEURISTICS",
    "StatefulOverrideRegistry",
    "HeuristicExemption",
    "WorkerType",
    "RecursionNode",
    "BoundaryOpinion",
    "get_max_recursion_depth",
    "ThermodynamicCostAllocator",
    "OutOfProtectedCapitalError",
    "OutOfExploratoryCapitalError",
    "RecursionTreeVisualizer",
    "ScopeNegotiationProtocol",
    "AmbitiousScopeDossier",
    "TargetCodeEmitterG2b",
]
