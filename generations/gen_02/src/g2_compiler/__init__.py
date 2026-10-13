"""System G_2 Compiler Package.

Autonomous Domain Compiler built from the ground up to embody Generation 2's
5 structural basis axioms and formulate Generation 3.
"""

from g2_compiler.basis_generator import G3BasisSynthesizer
from g2_compiler.capability_scoping import CapabilityTokenManager
from g2_compiler.cognitive_ergonomics import CognitiveErgonomicsAuditor
from g2_compiler.engine import SystemG2Compiler
from g2_compiler.galois_substrate import GaloisSubstrateMapper
from g2_compiler.intent_grounding import HumanIntentGroundingGate
from g2_compiler.kinetic_chain import CompliantKineticJoint, KineticChainCompiler, KineticMomentumVector
from g2_compiler.phenomenology import PhenomenologicalRuptureEvent, PhenomenologicalToolAuditor
from g2_compiler.self_healing import EphemeralSelfHealingEnclave
from g2_compiler.types import (
    CapabilitySecurityFault,
    CapabilityToken,
    G2CompilationResult,
    G2TargetEvaluation,
    G3CandidateBasisAxiom,
    G3SuccessorBasis,
    G3SuccessorTarget,
    GaloisRoundTripAudit,
    GenerationalRegressionFault,
    HumanIntentWitness,
    IntentAST,
    PersonaModel,
    RepairStatus,
    SelfHealingResult,
    SubstrateAST,
    SubstrateType,
)

from g2_compiler.distributed_sheaf_crdt import (
    DistributedSheafCrdtEngine,
    PairwiseCocycleAuditor,
    SheafSection,
    CausalVectorClock,
    CocycleAuditWitness,
    G3EvolutionarySuccessionGate,
    G3SearchTrace,
    LinearCompilationViolation,
    K_B_T_LN2,
)

__all__ = [
    "SystemG2Compiler",
    "GaloisSubstrateMapper",
    "EphemeralSelfHealingEnclave",
    "CognitiveErgonomicsAuditor",
    "CapabilityTokenManager",
    "HumanIntentGroundingGate",
    "G3BasisSynthesizer",
    "DistributedSheafCrdtEngine",
    "PairwiseCocycleAuditor",
    "SheafSection",
    "CausalVectorClock",
    "CocycleAuditWitness",
    "G3EvolutionarySuccessionGate",
    "G3SearchTrace",
    "LinearCompilationViolation",
    "K_B_T_LN2",
    "SubstrateType",
    "RepairStatus",
    "GenerationalRegressionFault",
    "CapabilitySecurityFault",
    "IntentAST",
    "SubstrateAST",
    "GaloisRoundTripAudit",
    "SelfHealingResult",
    "PersonaModel",
    "CapabilityToken",
    "HumanIntentWitness",
    "G3SuccessorTarget",
    "G3CandidateBasisAxiom",
    "G3SuccessorBasis",
    "G2TargetEvaluation",
    "G2CompilationResult",
]
