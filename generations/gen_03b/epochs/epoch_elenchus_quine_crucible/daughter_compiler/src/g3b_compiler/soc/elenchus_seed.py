"""Tier 1 Situation of Concern & Universal IR Seed Specification for `soc_epistemic_curiosity_engine`.

Models the Epistemic Curiosity & Socratic Scaffolding Engine (Axioma Elenchus):
1. Root Frictions:
   - Linear progression in standard educational and knowledge-retrieval systems.
   - Premature definitive answer-dumping when hitting cognitive walls in Category Theory / Pure Math,
     bypassing productive struggle and destroying meta-curiosity.
   - Fragile, disconnected knowledge graphs lacking formal prerequisite verification and reversible exploration.
2. Actors:
   - The Explorer (Human): Navigates the knowledge space, defining their current conceptual boundary.
   - The Socratic Probe (Agent): Operates on the frontier of the Explorer's knowledge, generating
     dialectical friction (structural questions, Lakatosian contradictory axioms) rather than answers.
   - The Epistemic Validator (Engine): Formally verifies whether the Explorer has integrated a concept
     before allowing state transitions to higher-order abstractions.
3. Architectural Constraints (The G3b Test):
   - Topological Fidelity ([L1-G3B-012]): Local hardware execution boundaries routing Socratic Probe
     inference to 192.168.10.40:11434 (Ollama running qwen2.5 on RTX 4060 8GB VRAM) with <=25ms latency
     budget and automatic [L1-016] Exception Enclave fallback to the deterministic kernel.
   - Statechart Complexity ([L1-G3B-011], [L1-002]): Deeply nested, non-linear hierarchical statechart
     with recursive deep HISTORY states allowing dead-end traversal, failure, and Functorial Undo rollback.
   - Compositional Contracts ([L1-G3B-011]): Strict epistemic prerequisites where 'Exploring Functors'
     physically cannot be entered unless 'Mastery of Morphisms' pre-condition contracts evaluate to True.
"""

from typing import Dict, Any, List

from .models import (
    SituationOfConcern,
    SoCAltitude,
    Actor,
    Friction,
    FrictionSeverity,
    EnvironmentalConstraint,
    ConstraintType,
)
from .normalizer import SoCNormalizer
from ..ir.contract_ir import (
    ContractIR,
    DomainNoun,
    DomainVerb,
    FieldDef,
    ComposedVerb,
    VerbCompositionStep,
)
from ..ir.statechart_ir import (
    StatechartIR,
    StateNode,
    StateNodeType,
    HistoryType,
    Transition,
)
from ..ir.topology_ir import (
    TopologyIR,
    TopologyNode,
    NodeRole,
    NetworkChannel,
    ChannelType,
    ConsensusContract,
    ConsensusProtocol,
)


SOC_ID_ELENCHUS = "soc_epistemic_curiosity_engine"

REQUIRED_INVARIANTS_ELENCHUS: List[str] = [
    "mastery_of_morphisms == True",
    "latency_ms <= 25",
    "dead_end_rollbacks >= 0",
    "quorum_valid == True",
]


def build_epistemic_curiosity_soc() -> SituationOfConcern:
    """Constructs and normalizes the Tier 1 Situation of Concern for `soc_epistemic_curiosity_engine`."""
    macro_soc = SituationOfConcern(
        soc_id=SOC_ID_ELENCHUS,
        title="Epistemic Curiosity & Socratic Scaffolding Engine",
        narrative=(
            "Current educational and knowledge-retrieval systems enforce linear progression. "
            "When a learner hits a cognitive wall—particularly in highly abstract domains like "
            "category theory or pure mathematics—standard systems provide definitive answers "
            "rather than structural scaffolding. This bypasses the necessary struggle, "
            "destroying meta-curiosity and creating fragile, disconnected knowledge graphs."
        ),
        altitude=SoCAltitude.MACRO,
        actors=[
            Actor(
                name="The Explorer",
                role="Human Learner & Mathematical Navigator",
                motivations=[
                    "Navigate abstract knowledge spaces (Category Theory, Pure Mathematics)",
                    "Define and expand current conceptual boundaries through authentic discovery",
                    "Test bold conjectures safely with reversible rollback from dead-ends",
                ],
                frustrations=[
                    "Linear progression walls that ignore non-linear mathematical intuition",
                    "Systems that prematurely dump textbook answers instead of structural scaffolding",
                    "Fragile, disconnected mental models caused by bypassing productive struggle",
                ],
            ),
            Actor(
                name="The Socratic Probe",
                role="Dialectical Frontier Agent (Local RTX 4060 Ollama Qwen 2.5)",
                motivations=[
                    "Operate strictly on the frontier of the Explorer's verified knowledge boundary",
                    "Generate dialectical friction via structural questions and Lakatosian counter-axioms",
                    "Maintain zero-latency (<25ms) local hardware execution without cloud reliance",
                ],
                frustrations=[
                    "Enterprise cloud latency breaking Socratic flow",
                    "Sycophantic answer-giving that short-circuits epistemic struggle",
                ],
            ),
            Actor(
                name="The Epistemic Validator",
                role="Formal Compositional Contract & Statechart Verification Engine",
                motivations=[
                    "Formally verify conceptual integration before unlocking higher-order abstractions",
                    "Enforce strict compositional pre-conditions ('Mastery of Morphisms' before 'Exploring Functors')",
                    "Preserve functorial undo history across conceptual dead-end rollbacks",
                ],
                frustrations=[
                    "Unverified self-reported progress allowing premature entry into higher abstractions",
                    "State corruption when learners hit contradictions without deep-history rollback",
                ],
            ),
        ],
        frictions=[
            Friction(
                description=(
                    "Linear progression and premature answer-dumping bypass productive struggle "
                    "when learners hit cognitive walls in category theory or pure mathematics"
                ),
                severity=FrictionSeverity.CRITICAL,
                impact="Destroys meta-curiosity and produces fragile, disconnected knowledge graphs",
                trigger_conditions=[
                    "Learner encounters abstract morphism/functor impasse",
                    "System responds with static textbook definition instead of dialectical scaffolding",
                ],
            ),
            Friction(
                description=(
                    "Exploring non-linear mathematical conjectures leads to dead-ends that corrupt "
                    "linear learning state without deep historical rollback"
                ),
                severity=FrictionSeverity.HIGH,
                impact="Penalizes mathematical experimentation and induces fear of failure",
                trigger_conditions=[
                    "Explorer tests a false axiom or non-associative composition",
                ],
            ),
            Friction(
                description=(
                    "Premature state transitions into higher-order abstractions ('Exploring Functors') "
                    "without verified foundational prerequisites ('Mastery of Morphisms')"
                ),
                severity=FrictionSeverity.CRITICAL,
                impact="Builds unstable higher-order abstractions on unverified foundations",
                trigger_conditions=[
                    "Attempting to enter 'Exploring Functors' while 'Mastery of Morphisms' is False",
                ],
            ),
        ],
        constraints=[
            EnvironmentalConstraint(
                nature=ConstraintType.TECHNICAL,
                description=(
                    "Topological Fidelity ([L1-G3B-012]): Local hardware inference routing to "
                    "Ollama endpoint (192.168.10.40:11434) running qwen2.5 on RTX 4060 (8GB VRAM) "
                    "with automatic [L1-016] Exception Enclave deterministic fallback"
                ),
                boundary_limit="192.168.10.40:11434 (qwen2.5, <=25ms latency budget, 8192MB VRAM, zero loopback)",
            ),
            EnvironmentalConstraint(
                nature=ConstraintType.ERGONOMIC,
                description=(
                    "Statechart Complexity ([L1-G3B-011], [L1-002]): Deeply nested, recursive "
                    "historical states enabling dead-end traversal and seamless Functorial Undo rollback"
                ),
                boundary_limit="XState v5 compound + deep history nodes with 1-tap Functorial Undo",
            ),
            EnvironmentalConstraint(
                nature=ConstraintType.TECHNICAL,
                description=(
                    "Compositional Contracts ([L1-G3B-011]): Strict epistemic prerequisites blocking "
                    "'Exploring Functors' until 'Mastery of Morphisms' pre-conditions evaluate to True"
                ),
                boundary_limit="ContractProofWitness certified with 0 unresolved obligations",
            ),
        ],
        unmet_needs=[
            "Zero-latency local Socratic Probe generating Lakatosian counter-axioms on RTX 4060 (qwen2.5)",
            "Non-linear hierarchical Statechart IR with deep history states and Functorial Undo from dead-ends",
            "Compositional Contract IR physically gating 'Exploring Functors' behind verified 'Mastery of Morphisms'",
        ],
    )

    meso_specs = [
        {
            "soc_id": "soc_meso_local_inference",
            "title": "Local Hardware Socratic Inference Boundary (RTX 4060 Ollama Qwen 2.5)",
            "narrative": (
                "Socratic probing requires sub-25ms local LAN inference on dedicated GPU hardware "
                "(192.168.10.40:11434) with an Exception Enclave fallback if the daemon drops offline."
            ),
            "frictions": [
                {
                    "description": "Cloud API latency and loopback illusion in distributed inference routing",
                    "severity": "HIGH",
                    "impact": "Breaks Socratic dialectical cadence",
                    "trigger_conditions": ["Inference routed over WAN or unverified loopback"],
                }
            ],
            "unmet_needs": ["Explicit LAN TopologyIR node at 192.168.10.40:11434 with enclave fallback"],
        },
        {
            "soc_id": "soc_meso_nonlinear_deadends",
            "title": "Non-Linear Dead-End Exploration & Deep History Rollback",
            "narrative": (
                "Learners must be free to follow false conjectures into contradiction traps and "
                "functorially roll back to their exact prior foundational state."
            ),
            "frictions": [
                {
                    "description": "Irreversible state mutation during failed mathematical conjectures",
                    "severity": "HIGH",
                    "impact": "Forces manual reset of learning progress",
                    "trigger_conditions": ["Axiom contradiction encountered in dead-end state"],
                }
            ],
            "unmet_needs": ["Recursive compound states with HistoryType.DEEP restoration"],
        },
        {
            "soc_id": "soc_meso_prerequisite_bypass",
            "title": "Compositional Prerequisite Gate (Morphisms -> Functors)",
            "narrative": (
                "Higher-order category theory strata must be guarded by machine-checkable "
                "precondition contracts over foundational morphism laws."
            ),
            "frictions": [
                {
                    "description": "Entering 'Exploring Functors' without proving associativity and identity laws",
                    "severity": "CRITICAL",
                    "impact": "Epistemic collapse in higher-order abstractions",
                    "trigger_conditions": ["Unchecked state transition request"],
                }
            ],
            "unmet_needs": ["Compositional ContractIR gating 'EnterExploringFunctors' on 'mastery_of_morphisms == True'"],
        },
    ]

    SoCNormalizer.decompose_fractal(macro_soc, meso_specs)
    return SoCNormalizer.normalize_tier1(macro_soc)


def build_epistemic_curiosity_contract_ir() -> ContractIR:
    """Constructs the Compositional ContractIR enforcing Category Theory epistemic prerequisites."""
    contract = ContractIR(
        contract_id=f"contract_{SOC_ID_ELENCHUS}",
        title="Epistemic Curiosity Engine Compositional Prerequisite Contract",
        description=(
            "Enforces strict epistemic prerequisites: 'Exploring Functors' physically cannot be "
            "entered unless 'Mastery of Morphisms' pre-conditions evaluate to True."
        ),
    )

    contract.add_noun(DomainNoun(
        name="ExplorerKnowledgeBoundary",
        description="Tracks the Explorer's verified category theory stratum and rollback count.",
        fields=[
            FieldDef("explorer_id", "str"),
            FieldDef("active_stratum", "str"),
            FieldDef("mastery_of_morphisms", "bool"),
            FieldDef("exploring_functors_entered", "bool"),
            FieldDef("dead_end_rollbacks", "int"),
        ],
        invariants=[
            "mastery_of_morphisms == True",
            "dead_end_rollbacks >= 0",
        ],
    ))

    contract.add_noun(DomainNoun(
        name="SocraticProbeSession",
        description="Local RTX 4060 Ollama (qwen2.5) dialectical probe session.",
        fields=[
            FieldDef("probe_id", "str"),
            FieldDef("ollama_endpoint", "str"),
            FieldDef("model_tag", "str"),
            FieldDef("latency_ms", "int"),
            FieldDef("vram_mb", "int"),
        ],
        invariants=[
            "latency_ms <= 25",
            "vram_mb >= 8192",
        ],
    ))

    contract.add_noun(DomainNoun(
        name="EpistemicValidatorGate",
        description="Formal validator certifying concept integration across Sheaf-Quorum nodes.",
        fields=[
            FieldDef("gate_id", "str"),
            FieldDef("target_state", "str"),
            FieldDef("quorum_valid", "bool"),
        ],
        invariants=[
            "quorum_valid == True",
        ],
    ))

    # Child Sub-Contract 1: Foundational Mastery of Morphisms
    sub_morphisms = ContractIR(
        contract_id="sub_foundation_morphisms",
        title="Foundational Mastery of Morphisms Subcontract",
        description="Verifies object-arrow typing, composition associativity, and identity morphisms.",
    )
    sub_morphisms.add_verb(DomainVerb(
        name="CertifyMasteryOfMorphisms",
        description="Certifies that the Explorer has integrated category objects, composition, and identity laws.",
        pre_conditions=[
            "objects_and_arrows_mapped == True",
            "associativity_axiom_verified == True",
            "identity_morphism_verified == True",
        ],
        post_conditions=[
            "mastery_of_morphisms == True",
        ],
        modifies_nouns=["ExplorerKnowledgeBoundary"],
    ))

    # Child Sub-Contract 2: Socratic Probe Dialectical Elenchus
    sub_probe = ContractIR(
        contract_id="sub_socratic_probe",
        title="Socratic Probe Dialectical Elenchus Subcontract",
        description="Generates Lakatosian counter-axioms via local RTX 4060 Qwen 2.5 inference.",
    )
    sub_probe.add_verb(DomainVerb(
        name="ExecuteDialecticalElenchus",
        description="Challenges the Explorer with structural counter-examples at the morphism-functor boundary.",
        pre_conditions=[
            "mastery_of_morphisms == True",
            "local_rtx4060_qwen_ready == True",
        ],
        post_conditions=[
            "socratic_contradiction_resolved == True",
            "functor_laws_scaffolded == True",
        ],
        modifies_nouns=["SocraticProbeSession"],
    ))

    # Child Sub-Contract 3: Epistemic Validator Transition to Exploring Functors
    sub_validator = ContractIR(
        contract_id="sub_epistemic_validator",
        title="Epistemic Validator Higher-Order Abstraction Gate",
        description="Unlocks 'Exploring Functors' only when Mastery of Morphisms and Elenchus evaluate to True.",
    )
    sub_validator.add_verb(DomainVerb(
        name="UnlockExploringFunctors",
        description="Formally transitions Explorer into 'Exploring Functors' state.",
        pre_conditions=[
            "mastery_of_morphisms == True",
            "socratic_contradiction_resolved == True",
            "functor_laws_scaffolded == True",
        ],
        post_conditions=[
            "exploring_functors_entered == True",
            "workflow_completed == True",
            "state_persisted == True",
        ],
        modifies_nouns=["ExplorerKnowledgeBoundary", "EpistemicValidatorGate"],
    ))

    contract.sub_contracts[sub_morphisms.contract_id] = sub_morphisms
    contract.sub_contracts[sub_probe.contract_id] = sub_probe
    contract.sub_contracts[sub_validator.contract_id] = sub_validator

    # Composed Parent Verb: TransitionToExploringFunctors
    parent_verb = DomainVerb(
        name="TransitionToExploringFunctors",
        description=(
            "Compositional transition from foundational morphism inquiry to higher-order "
            "'Exploring Functors' state, strictly gated by Mastery of Morphisms."
        ),
        pre_conditions=[
            "objects_and_arrows_mapped == True",
            "associativity_axiom_verified == True",
            "identity_morphism_verified == True",
            "local_rtx4060_qwen_ready == True",
        ],
        post_conditions=[
            "mastery_of_morphisms == True",
            "exploring_functors_entered == True",
            "workflow_completed == True",
            "state_persisted == True",
        ],
        modifies_nouns=["ExplorerKnowledgeBoundary", "SocraticProbeSession", "EpistemicValidatorGate"],
    )

    contract.add_composed_verb(ComposedVerb(
        parent_verb=parent_verb,
        child_steps=[
            VerbCompositionStep("sub_foundation_morphisms", "CertifyMasteryOfMorphisms"),
            VerbCompositionStep("sub_socratic_probe", "ExecuteDialecticalElenchus"),
            VerbCompositionStep("sub_epistemic_validator", "UnlockExploringFunctors"),
        ],
    ))

    return contract


def build_epistemic_curiosity_statechart_ir() -> StatechartIR:
    """Constructs the non-linear hierarchical StatechartIR with deep history and dead-end Functorial Undo."""
    foundational_states = {
        "mapping_objects_arrows": StateNode(
            id="foundational_stratum.mapping_objects_arrows",
            node_type=StateNodeType.ATOMIC,
            description="Explorer defines category objects and morphism arrows.",
            transitions=[
                Transition(
                    event="PROPOSE_COMPOSITION",
                    target="foundational_stratum.probing_morphisms",
                    description="Submit candidate composition table to Socratic Probe.",
                )
            ],
        ),
        "probing_morphisms": StateNode(
            id="foundational_stratum.probing_morphisms",
            node_type=StateNodeType.ATOMIC,
            description="Socratic Probe tests associativity and identity axioms.",
            transitions=[
                Transition(
                    event="AXIOM_CONTRADICTION",
                    target="foundational_stratum.dead_end_associativity",
                    description="Conjecture violates (h o g) o f = h o (g o f); enters conceptual dead-end.",
                ),
                Transition(
                    event="VERIFY_MORPHISM_LAWS",
                    target="foundational_stratum.mastery_of_morphisms",
                    guard="associativity_and_identity_hold == True",
                    description="Epistemic Validator certifies foundational morphism mastery.",
                ),
            ],
        ),
        "dead_end_associativity": StateNode(
            id="foundational_stratum.dead_end_associativity",
            node_type=StateNodeType.ATOMIC,
            description="Conceptual dead-end: non-associative arrow composition trap.",
            transitions=[
                Transition(
                    event="FUNCTORIAL_UNDO_ROLLBACK",
                    target="foundational_stratum.foundational_history",
                    actions=["record_refutation_lemma", "restore_foundational_snapshot"],
                    description="Functorial Undo rolls back from dead-end via Deep History node.",
                )
            ],
        ),
        "foundational_history": StateNode(
            id="foundational_stratum.foundational_history",
            node_type=StateNodeType.HISTORY,
            history_type=HistoryType.DEEP,
            description="Deep history restoration node for foundational stratum.",
            transitions=[
                Transition(
                    event="RESTORE_DEEP_HISTORY",
                    target="foundational_stratum.probing_morphisms",
                    description="Restores Explorer to stable foundational probing state.",
                )
            ],
        ),
        "mastery_of_morphisms": StateNode(
            id="foundational_stratum.mastery_of_morphisms",
            node_type=StateNodeType.ATOMIC,
            description="Certified foundational state: Mastery of Morphisms achieved.",
            transitions=[
                Transition(
                    event="REQUEST_HIGHER_ABSTRACTION",
                    target="root.dialectical_gate",
                    guard="mastery_of_morphisms == True",
                    description="Request transition toward Exploring Functors.",
                )
            ],
        ),
    }

    dialectical_gate_states = {
        "evaluating_prerequisites": StateNode(
            id="dialectical_gate.evaluating_prerequisites",
            node_type=StateNodeType.ATOMIC,
            description="Epistemic Validator checks compositional contract pre-conditions.",
            transitions=[
                Transition(
                    event="PREREQUISITE_REJECTED",
                    target="root.foundational_stratum",
                    description="Blocks transition if Mastery of Morphisms is incomplete.",
                ),
                Transition(
                    event="PREREQUISITE_SATISFIED",
                    target="dialectical_gate.socratic_cross_exam",
                    guard="mastery_of_morphisms == True",
                    description="Advances to Socratic elenchus cross-examination.",
                ),
            ],
        ),
        "socratic_cross_exam": StateNode(
            id="dialectical_gate.socratic_cross_exam",
            node_type=StateNodeType.ATOMIC,
            description="Socratic Probe poses Lakatosian counter-axioms on structure preservation.",
            transitions=[
                Transition(
                    event="CONJECTURE_REFUTED",
                    target="dialectical_gate.conceptual_dead_end",
                    description="Explorer's naive mapping fails identity/composition preservation.",
                ),
                Transition(
                    event="ELENCHUS_PASSED",
                    target="dialectical_gate.gate_certified",
                    guard="socratic_contradiction_resolved == True",
                    description="Explorer resolves dialectical tension.",
                ),
            ],
        ),
        "conceptual_dead_end": StateNode(
            id="dialectical_gate.conceptual_dead_end",
            node_type=StateNodeType.ATOMIC,
            description="Conceptual dead-end at the morphism-to-functor boundary.",
            transitions=[
                Transition(
                    event="FUNCTORIAL_UNDO_TO_FOUNDATION",
                    target="foundational_stratum.foundational_history",
                    actions=["log_counterexample_witness", "functorial_rollback"],
                    description="Seamless Functorial Undo back to foundational deep history.",
                )
            ],
        ),
        "gate_certified": StateNode(
            id="dialectical_gate.gate_certified",
            node_type=StateNodeType.ATOMIC,
            description="Epistemic Validator signs proof witness unlocking higher abstraction.",
            transitions=[
                Transition(
                    event="ENTER_EXPLORING_FUNCTORS",
                    target="root.higher_abstraction_stratum",
                    guard="mastery_of_morphisms == True and socratic_contradiction_resolved == True",
                    description="Enters Exploring Functors stratum.",
                )
            ],
        ),
    }

    higher_abstraction_states = {
        "exploring_functors": StateNode(
            id="higher_abstraction_stratum.exploring_functors",
            node_type=StateNodeType.ATOMIC,
            description="High-level state: Exploring Functors F: C -> D preserving identity and composition.",
            transitions=[
                Transition(
                    event="IDENTITY_PRESERVATION_BROKEN",
                    target="higher_abstraction_stratum.functor_dead_end",
                    description="Conjecture violates F(id_X) = id_{F(X)}; enters functor dead-end.",
                ),
                Transition(
                    event="VERIFY_FUNCTORIALITY",
                    target="higher_abstraction_stratum.natural_transformations",
                    guard="functor_laws_verified == True",
                    description="Advances to Natural Transformations.",
                ),
            ],
        ),
        "functor_dead_end": StateNode(
            id="higher_abstraction_stratum.functor_dead_end",
            node_type=StateNodeType.ATOMIC,
            description="Conceptual dead-end: non-functorial graph mapping.",
            transitions=[
                Transition(
                    event="FUNCTORIAL_UNDO_STEP",
                    target="higher_abstraction_stratum.higher_history",
                    actions=["restore_functor_snapshot"],
                    description="Rolls back functor dead-end via deep history.",
                )
            ],
        ),
        "higher_history": StateNode(
            id="higher_abstraction_stratum.higher_history",
            node_type=StateNodeType.HISTORY,
            history_type=HistoryType.DEEP,
            description="Deep history node for higher abstraction stratum.",
            transitions=[
                Transition(
                    event="RESTORE_FUNCTOR_STATE",
                    target="higher_abstraction_stratum.exploring_functors",
                    description="Restores Explorer to Exploring Functors state.",
                )
            ],
        ),
        "natural_transformations": StateNode(
            id="higher_abstraction_stratum.natural_transformations",
            node_type=StateNodeType.ATOMIC,
            description="Explorer verifies naturality squares between functors F and G.",
            transitions=[
                Transition(
                    event="CERTIFY_ABSTRACTION",
                    target="higher_abstraction_stratum.epistemic_integration_complete",
                    description="Completes epistemic integration cycle.",
                )
            ],
        ),
        "epistemic_integration_complete": StateNode(
            id="higher_abstraction_stratum.epistemic_integration_complete",
            node_type=StateNodeType.FINAL,
            description="Terminal certified state for the Category Theory epistemic cycle.",
        ),
    }

    root = StateNode(
        id="root",
        node_type=StateNodeType.COMPOUND,
        initial="foundational_stratum",
        states={
            "foundational_stratum": StateNode(
                id="root.foundational_stratum",
                node_type=StateNodeType.COMPOUND,
                initial="mapping_objects_arrows",
                states=foundational_states,
                description="Foundational Category Theory Stratum (Objects, Morphisms, Associativity).",
            ),
            "dialectical_gate": StateNode(
                id="root.dialectical_gate",
                node_type=StateNodeType.COMPOUND,
                initial="evaluating_prerequisites",
                states=dialectical_gate_states,
                description="Socratic Elenchus & Epistemic Validator Gate.",
            ),
            "higher_abstraction_stratum": StateNode(
                id="root.higher_abstraction_stratum",
                node_type=StateNodeType.COMPOUND,
                initial="exploring_functors",
                states=higher_abstraction_states,
                description="Higher-Order Abstraction Stratum (Exploring Functors & Natural Transformations).",
            ),
        },
    )

    return StatechartIR(
        id=f"statechart_{SOC_ID_ELENCHUS}",
        root=root,
        context_schema={
            "active_stratum": "str",
            "mastery_of_morphisms": "bool",
            "exploring_functors_entered": "bool",
            "dead_end_rollbacks": "int",
            "value_delivered": "bool",
        },
        initial_context={
            "active_stratum": "foundational_stratum",
            "mastery_of_morphisms": False,
            "exploring_functors_entered": False,
            "dead_end_rollbacks": 0,
            "value_delivered": False,
        },
    )


def build_epistemic_curiosity_topology_ir(inject_fault: bool = False) -> TopologyIR:
    """Constructs the multi-node local hardware TopologyIR targeting RTX 4060 Ollama (192.168.10.40:11434)."""
    topo = TopologyIR(topology_id=f"topo_{SOC_ID_ELENCHUS}")

    host_explorer = "127.0.0.1" if inject_fault else "192.168.10.20"
    host_rtx4060 = "localhost" if inject_fault else "192.168.10.40"
    host_validator = "192.168.10.30"

    topo.add_node(TopologyNode(
        node_id="node_explorer_workstation",
        role=NodeRole.ORCHESTRATOR,
        host_interface=host_explorer,
        port=8097,
        capabilities=["explorer_workbench_ui", "statechart_engine", "functorial_undo"],
        memory_mb_limit=4096,
    ))
    topo.add_node(TopologyNode(
        node_id="node_socratic_rtx4060",
        role=NodeRole.WORKER,
        host_interface=host_rtx4060,
        port=11434,
        capabilities=[
            "ollama_local_inference",
            "model:qwen2.5",
            "gpu:rtx_4060_8gb_vram",
            "lakatosian_counter_axiom_generator",
            "exception_enclave_deterministic_fallback",
        ],
        memory_mb_limit=8192,
    ))
    topo.add_node(TopologyNode(
        node_id="node_epistemic_validator",
        role=NodeRole.VERIFIER,
        host_interface=host_validator,
        port=8098,
        capabilities=["compositional_contract_verifier", "sheaf_quorum_witness"],
        memory_mb_limit=2048,
    ))

    topo.add_channel(NetworkChannel(
        channel_id="ch_socratic_ollama_stream",
        source_node_id="node_explorer_workstation",
        target_node_id="node_socratic_rtx4060",
        channel_type=ChannelType.STREAM,
        port=11434,
        latency_ms_budget=25,
        tls_enforced=False,
    ))
    topo.add_channel(NetworkChannel(
        channel_id="ch_epistemic_contract_rpc",
        source_node_id="node_explorer_workstation",
        target_node_id="node_epistemic_validator",
        channel_type=ChannelType.RPC,
        port=8098,
        latency_ms_budget=15,
        tls_enforced=True,
    ))

    topo.consensus = ConsensusContract(
        protocol=ConsensusProtocol.SHEAF_QUORUM,
        quorum_fraction=0.67,
        heartbeat_interval_ms=500,
        partition_strategy="fail_closed",
    )
    return topo


def build_epistemic_curiosity_domain_spec() -> Dict[str, Any]:
    """Returns the serializable domain_spec bundle for `soc_epistemic_curiosity_engine`."""
    contract = build_epistemic_curiosity_contract_ir()
    statechart = build_epistemic_curiosity_statechart_ir()
    topology = build_epistemic_curiosity_topology_ir(inject_fault=False)
    endpoints = [
        f"http://{n.host_interface}:{n.port}"
        for n in topology.nodes.values()
    ]
    return {
        "contract_ir": contract.to_dict(),
        "statechart_ir": statechart.to_dict(),
        "topology_ir": topology.to_dict(),
        "endpoints": endpoints,
    }
