"""Generation 4b Sovereign Builder Service Package (`services/builder/src`)."""

from .domain_models import (
    ASTNodeType,
    ASTSkeletonSnapshot,
    BuilderExecutionBundle,
    ByzantineChaosReport,
    CausalConvergenceAttestation,
    CognitiveRole,
    DiagnosticSeverity,
    DiagnosticTuple,
    DomainInvariantViolation,
    DynamicPersonaManifest,
    FractalTreeNode,
    FunctorialUndoCheckpoint,
    HermeticLinterReport,
    HierarchicalBudgetLease,
    LeafEmissionEvent,
    LeaseAllocationStatus,
    MerkleTreeRootAttestation,
    PhysicalDiskWitness,
    QuineDaughterManifest,
    QuineReactiveManifest,
    ReactiveAuditReport,
    ReactiveVerificationGate,
    RFCSubmissionRecord,
    SubtreeHealingEnvelope,
    TaskExecutionStatus,
)
from .engine_synthesizer import (
    BuilderQuarantineViolation,
    EngineSynthesizer,
    validate_mutation_target,
)
from .qa_synthesizer import (
    QABoundaryViolation,
    QASynthesizer,
    sanitize_context_for_qa,
    validate_qa_target,
)
from .ui_scaffolder import (
    HermeticityViolation,
    NarrativeHUDTemplate,
    StudioCSSTemplate,
    TactileCanvasTemplate,
    UIScaffolder,
    clamp_coordinates,
    format_narrative_diff,
    screen_to_spatial,
)
