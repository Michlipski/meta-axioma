"""System G_1 Compiler Engine - Ground-Up Implementation.

Built from the ground up using the 7 active structural axioms of Generation 1:
- [L1-002] Functorial State Evolution & Morphism Preservation
- [L1-004] Universal Grammar & Compositional Projection Constraints
- [L1-011_3] Decoupled Persistence across Boundary 3
- [L1-008] Landauer Thermodynamic Reversibility & Erasure Dissipation Accounting
- [L1-015] Zero-Trust Dual-Boundary Demarcation & Introspectable MCP Governance
- [L1-016] Demarcated Exception Enclaves & Bounded Invariant Suspension
- [L1-015_1] Compositional Boundary Isolation

Mandate: Formulate the basis and evaluation targets for Generation 2 (G_2),
maintaining active teleological awareness of the High-Level Jettison
(optimizing for production non-generator software applications).
"""

from g1_compiler.composition import CompositionalBoundaryAuditor
from g1_compiler.enclaves import ExceptionEnclave, EnclaveAuditWitness
from g1_compiler.engine import SystemG1Compiler
from g1_compiler.functor import Morphism, FunctorialPipeline, CategoryFunctor
from g1_compiler.grammar import DeepSyntaxNode, UniversalGrammar
from g1_compiler.mcp_gateway import (
    McpGateway,
    McpTool,
    NounField,
    NounSchema,
    VerbStateAutomaton,
    VerbTransition,
)
from g1_compiler.app_compiler import (
    ApplicationCompiler,
    ApplicationSpec,
    AppModelSpec,
    AppModelField,
    AppActionSpec,
)
from g1_compiler.persistence import Boundary3StorageAdapter, InMemoryAdapter, FileSystemAdapter, Boundary3PersistenceManager
from g1_compiler.thermodynamics import LandauerAccountingLedger, ThermodynamicReversibilityAuditor
from g1_compiler.types import SystemState, CompilerPhase, G2SuccessorBasis

__all__ = [
    "SystemG1Compiler",
    "ApplicationCompiler",
    "ApplicationSpec",
    "AppModelSpec",
    "AppModelField",
    "AppActionSpec",
    "SystemState",
    "CompilerPhase",
    "G2SuccessorBasis",
    "Morphism",
    "FunctorialPipeline",
    "CategoryFunctor",
    "DeepSyntaxNode",
    "UniversalGrammar",
    "Boundary3StorageAdapter",
    "InMemoryAdapter",
    "FileSystemAdapter",
    "Boundary3PersistenceManager",
    "LandauerAccountingLedger",
    "ThermodynamicReversibilityAuditor",
    "McpGateway",
    "McpTool",
    "NounField",
    "NounSchema",
    "VerbStateAutomaton",
    "VerbTransition",
    "ExceptionEnclave",
    "EnclaveAuditWitness",
    "CompositionalBoundaryAuditor",
]
