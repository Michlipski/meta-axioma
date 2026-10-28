"""Tier 1 Situation of Concern & Universal IR Seed Specification for `soc_g4b_researcher`.

Generation 4b Autonomous Decoupled Research Service (Zenith Apex Epistemic Crucible):
1. Root Frictions:
   - The "Builder Shortchanging Research" dilemma: when execution-focused enclaves handle
     their own problem discovery, epistemic depth is compressed to whatever satisfies immediate delivery.
   - Unstructured natural language feedback causes oscillating diffs and prompt bloat.
   - Mode collapse and cosmetic plagiarism: repetitive recycling of standard CRUD/REST patterns.
2. Actors:
   - Human Systems Architect (Michael Lipski): Epistemic Sovereign & Governance Custodian.
   - Sovereign Research Service: Formal correctness, invariant completeness, failure-mode modeling.
   - Primary Builder (G3b / G4b-Dev): AST precision, Landauer efficiency, substrate execution.
   - Protocol Adjudicator: Impartial RFC judge and Merkle telemetry anchor.
3. Architectural Constraints:
   - [L1-G3B-012] Non-loopback network topology across 6 nodes on 192.168.40.0/24 subnet.
   - [L1-G4B-002] Zero-code tool boundary for research enclaves.
   - [L1-G4B-003] Hierarchical Merkle-DAG cryptographic telemetry.
   - [L1-G4B-005] 5-Tier Anti-Bias and Novelty framework (D(Gi, Gj) >= 0.40).
   - [L1-002] 32-state hierarchical XState v5 engine with 1-tap Functorial Undo.
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


REQUIRED_INVARIANTS_RESEARCHER: List[str] = [
    "[L1-G3B-000] Waterloo Situation of Concern Normalization",
    "[L1-G3B-011] Universal & Hierarchical IR Specification",
    "[L1-G3B-012] Topological Fidelity Invariant",
    "[L1-G3B-014] Dual-Model Cognitive Routing Invariant",
    "[L1-G3B-016] Zero-Bypass Micro-Auditor Interception",
    "[L1-G3B-017] Reflexive Quine Daughter Isolation Protocol",
    "[L1-G3B-018] Mandatory Development Process Telemetry Dashboard Deliverable",
    "[L1-G4B-001] Fractal Tree Recursion & Async RFC Protocol Bus",
    "[L1-G4B-002] Zero-Code Research Service Tool Boundary",
    "[L1-G4B-003] Merkle-DAG Cryptographic Telemetry Witness",
    "[L1-G4B-004] Dynamic On-The-Fly Persona Specialization",
    "[L1-G4B-005] Dialectical Inversion & Taboo Distance Matrix",
    "[L1-G4B-006] Extreme Boundary Stress & Byzantine Fuzzing",
    "[L1-002] Functorial State Transitions & Deterministic Undo",
    "[NEG-G1B-001] Empirical Execution Witness & Anti-Phantom Emission Gate",
]


def build_researcher_soc() -> SituationOfConcern:
    """Builds the formal Waterloo Tier 1 Situation of Concern for `soc_g4b_researcher`."""
    return SituationOfConcern(
        soc_id="soc_g4b_researcher",
        title="Generation 4b Autonomous Decoupled Research Service (Zenith Apex Epistemic Crucible)",
        narrative=(
            "In recursive self-compiling systems, the fatal pathology is the Builder Shortchanging Research dilemma. "
            "Generation 4b permanently decouples Research from Development into an autonomous sovereign service "
            "with zero code-emission tools, optimizing purely for epistemic depth, invariant completeness (100%), "
            "and failure-mode coverage under a 5-tier anti-bias framework and formal RFC protocol negotiation."
        ),
        altitude=SoCAltitude.MACRO,
        actors=[
            Actor(
                name="Human Systems Architect",
                role="Epistemic Sovereign & Governance Custodian",
                motivations=[
                    "Steer multi-generational succession",
                    "Preserve thermodynamic compute sanity",
                    "Enforce negative axiom vetoes (NEG-###)",
                ],
                frustrations=[
                    "Silent degradation of invariants",
                    "Agent shortcutting and mode collapse",
                    "Unstructured natural language prompt bloat",
                ],
            ),
            Actor(
                name="Sovereign Research Service",
                role="Theoretical Correctness & Architectural Blueprinting Engine",
                motivations=[
                    "Invariant completeness (100% coverage)",
                    "Topological novelty enforcement (D >= 0.40)",
                    "Formal SMT composition proofs",
                ],
                frustrations=[
                    "Pressure to cut scope for delivery expediency",
                    "Builder attempts to soften invariants",
                ],
            ),
            Actor(
                name="Primary Builder",
                role="AST Synthesizer & Substrate Implementation Engine",
                motivations=[
                    "Clean AST emission",
                    "Substrate runtime test execution (exit code 0)",
                    "Landauer energy efficiency",
                ],
                frustrations=[
                    "Unrealistic research specs exceeding physical token ceilings",
                ],
            ),
            Actor(
                name="Protocol Adjudicator",
                role="Impartial RFC Judge & Merkle Telemetry Anchor",
                motivations=[
                    "Validate formal morphism pre/post-conditions",
                    "Synthesize counter-proofs for invalid RFCs",
                    "Maintain tamper-evident Merkle DAG",
                ],
                frustrations=[
                    "Malformed RFC payloads and untyped evidence",
                ],
            ),
        ],
        frictions=[
            Friction(
                description="The Builder Shortchanging Research dilemma causes premature epistemic truncation",
                severity=FrictionSeverity.CRITICAL,
                impact="Fragile architectures that fail under real-world partition or Byzantine conditions",
            ),
            Friction(
                description="Unstructured natural language error strings cause context explosion and oscillating diffs",
                severity=FrictionSeverity.HIGH,
                impact="Prompt bloat up to 40k tokens and wasted Landauer dissipation",
            ),
            Friction(
                description="Mode collapse and cosmetic plagiarism recycle ubiquitous web patterns",
                severity=FrictionSeverity.HIGH,
                impact="Loss of generational succession value and novelty starvation",
            ),
        ],
        constraints=[
            EnvironmentalConstraint(
                nature=ConstraintType.THERMODYNAMIC,
                description="Strict 60/40 capital partition: 60% Exploratory / 40% Protected",
                boundary_limit="982,300 BPE tokens (C_exploratory=589,380, C_protected=392,920)",
            ),
            EnvironmentalConstraint(
                nature=ConstraintType.ERGONOMIC,
                description="Zero-Code Research Service Tool Boundary",
                boundary_limit="Zero code-writing or shell execution tools in research enclaves",
            ),
            EnvironmentalConstraint(
                nature=ConstraintType.TECHNICAL,
                description="Topological Fidelity Invariant [L1-G3B-012]",
                boundary_limit="6 nodes on 192.168.40.0/24 subnet; 0 loopback addresses allowed",
            ),
        ],
        unmet_needs=[
            "Formal decoupling of discovery from emission via physical sandbox tool boundaries",
            "Asynchronous typed RFC protocol negotiation (SpecAdjustmentRequest -> SpecAmendment)",
            "Multi-island exploration guaranteed to satisfy structural taboo distance D >= 0.40",
            "Deterministic 1-tap Functorial Undo for exploratory research dead-ends",
        ],
    )


def build_researcher_contract_ir() -> ContractIR:
    """Builds the formal ContractIR for `soc_g4b_researcher`."""
    nouns = [
        DomainNoun(
            name="ResearchDeliverableBundle",
            description="Certified sovereign research specification bundle",
            fields=[
                FieldDef("bundle_id", "str", "UUIDv7 identifier"),
                FieldDef("target_soc_id", "str", "Waterloo SoC reference"),
                FieldDef("reference_architecture_hash", "str", "64-char SHA-256 hash"),
                FieldDef("merkle_root", "str", "Root Merkle DAG hash"),
                FieldDef("is_certified", "bool", "Certification status"),
            ],
            invariants=["len(reference_architecture_hash) == 64", "len(merkle_root) == 64"],
        ),
        DomainNoun(
            name="HypothesisDefinition",
            description="SMT-formalized theoretical conjecture",
            fields=[
                FieldDef("hypothesis_id", "str", "Hypothesis identifier"),
                FieldDef("theoretical_claim", "str", "Formal hypothesis prose"),
                FieldDef("expected_complexity_class", "str", "Asymptotic complexity bound"),
                FieldDef("formal_conjecture_z3", "str", "SMT-LIB2 formal assertion"),
            ],
            invariants=["len(theoretical_claim) >= 20"],
        ),
        DomainNoun(
            name="ConstraintAnalysis",
            description="Environmental and topological constraint extraction",
            fields=[
                FieldDef("analysis_id", "str", "Analysis identifier"),
                FieldDef("physical_latency_budget_ms", "int", "Latency ceiling in ms"),
                FieldDef("landauer_erasure_budget_bits", "int", "Maximum bit erasure allowed"),
            ],
            invariants=["physical_latency_budget_ms > 0", "landauer_erasure_budget_bits > 0"],
        ),
        DomainNoun(
            name="FailureModeModel",
            description="Byzantine and partition failure mode taxonomy",
            fields=[
                FieldDef("model_id", "str", "Failure model identifier"),
            ],
            invariants=["len(model_id) > 0"],
        ),
        DomainNoun(
            name="TradeoffMatrix",
            description="Pareto frontier trade-off analysis",
            fields=[
                FieldDef("matrix_id", "str", "Trade-off matrix identifier"),
                FieldDef("selection_proof", "str", "Formal proof of Pareto optimality"),
            ],
            invariants=["len(selection_proof) >= 10"],
        ),
        DomainNoun(
            name="SpecAdjustmentRequest",
            description="Builder RFC requesting specification adjustment",
            fields=[
                FieldDef("request_id", "str", "RFC identifier"),
                FieldDef("target_symbol_urn", "str", "Symbol URN under bottleneck"),
                FieldDef("bottleneck_type", "str", "Classification of bottleneck"),
                FieldDef("proposed_delta", "str", "Concrete requested amendment"),
            ],
            invariants=["len(proposed_delta) > 0"],
        ),
        DomainNoun(
            name="SpecAmendment",
            description="Adjudicated signed amendment or formal counter-proof",
            fields=[
                FieldDef("amendment_id", "str", "Amendment identifier"),
                FieldDef("request_id", "str", "Original RFC identifier"),
                FieldDef("is_approved", "bool", "Approval status"),
                FieldDef("adjudicator_signature", "str", "Cryptographic signature"),
            ],
            invariants=["len(adjudicator_signature) == 64"],
        ),
        DomainNoun(
            name="TabooDistanceMatrix",
            description="Weisfeiler-Lehman topological graph hash distance matrix",
            fields=[
                FieldDef("matrix_id", "str", "Matrix identifier"),
                FieldDef("min_distance_threshold", "float", "Enforced distance threshold"),
            ],
            invariants=["min_distance_threshold >= 0.40"],
        ),
        DomainNoun(
            name="MerkleDagWitness",
            description="Cryptographic Merkle DAG node linking parent hashes",
            fields=[
                FieldDef("node_hash", "str", "SHA-256 node hash"),
                FieldDef("task_id", "str", "Task reference"),
                FieldDef("timestamp_ns", "int", "Nanosecond timestamp"),
            ],
            invariants=["len(node_hash) == 64", "timestamp_ns > 0"],
        ),
        DomainNoun(
            name="EmpiricalTelemetryReport",
            description="Real-time execution telemetry and Landauer dissipation",
            fields=[
                FieldDef("report_id", "str", "Report identifier"),
                FieldDef("landauer_bits_erased", "int", "Total erased bits"),
                FieldDef("substrate_test_exit_code", "int", "Subprocess exit code"),
            ],
            invariants=["substrate_test_exit_code == 0", "landauer_bits_erased >= 0"],
        ),
        DomainNoun(
            name="EpistemicCrucibleTarget",
            description="Crucible campaign objective and token lease",
            fields=[
                FieldDef("target_id", "str", "Target identifier"),
                FieldDef("exploratory_token_lease", "int", "Token lease"),
                FieldDef("required_island_count", "int", "Minimum isolated islands"),
            ],
            invariants=["required_island_count >= 3", "exploratory_token_lease >= 10000"],
        ),
        DomainNoun(
            name="ZeroContextIslandManifest",
            description="Quarantined research island manifest with entropy seed",
            fields=[
                FieldDef("island_id", "str", "Island identifier"),
                FieldDef("assigned_seed_entropy", "str", "Cryptographic entropy seed"),
                FieldDef("quarantine_token_budget", "int", "Per-island budget"),
            ],
            invariants=["quarantine_token_budget > 0"],
        ),
        DomainNoun(
            name="NoveltyArchiveEntry",
            description="Historical architectural novelty archive entry",
            fields=[
                FieldDef("archive_id", "str", "Archive identifier"),
                FieldDef("weisfeiler_lehman_hash", "str", "Graph WL signature"),
                FieldDef("novelty_score", "float", "Lehman-Stanley novelty score"),
            ],
            invariants=["novelty_score >= 0.0"],
        ),
        DomainNoun(
            name="DialecticalNegationSeed",
            description="Injected negative constraint forcing architectural inversion",
            fields=[
                FieldDef("seed_id", "str", "Seed identifier"),
                FieldDef("default_primitive", "str", "Forbidden default primitive"),
                FieldDef("negated_invariant", "str", "Injected NEG_PRIMITIVE invariant"),
            ],
            invariants=["len(negated_invariant) > 0"],
        ),
        DomainNoun(
            name="ExtremeBoundaryArchetype",
            description="Hostile stress profile for edge-case validation",
            fields=[
                FieldDef("archetype_id", "str", "Archetype identifier"),
                FieldDef("stress_dimension", "str", "Dimension under stress"),
                FieldDef("stress_magnitude", "float", "Magnitude multiplier"),
            ],
            invariants=["stress_magnitude > 0.0"],
        ),
        DomainNoun(
            name="ByzantineFuzzVector",
            description="Chaotic network vector for recovery enclave testing",
            fields=[
                FieldDef("vector_id", "str", "Vector identifier"),
                FieldDef("target_channel_id", "str", "Target network channel"),
                FieldDef("is_trapped", "bool", "Trapping verification status"),
            ],
            invariants=["len(target_channel_id) > 0"],
        ),
        DomainNoun(
            name="FormalProofArtifact",
            description="SMT composition proof artifact",
            fields=[
                FieldDef("proof_id", "str", "Proof identifier"),
                FieldDef("solver_engine", "str", "SMT solver signature"),
                FieldDef("solver_result", "str", "UNSAT (valid) or SAT (counter-example)"),
            ],
            invariants=["len(solver_engine) > 0"],
        ),
        DomainNoun(
            name="FunctorialUndoCheckpoint",
            description="Snapshot enabling deterministic 1-tap rollback",
            fields=[
                FieldDef("checkpoint_id", "str", "Checkpoint identifier"),
                FieldDef("statechart_snapshot_hash", "str", "64-char state hash"),
                FieldDef("erased_bits_to_revert", "int", "Thermodynamic bits to reclaim"),
            ],
            invariants=["len(statechart_snapshot_hash) == 64", "erased_bits_to_revert >= 0"],
        ),
    ]

    parent_verb_discovery = DomainVerb(
        name="ComposeEpistemicDiscovery",
        description="Executes full discovery across isolated islands and formalizes hypotheses",
        parameters=[
            FieldDef("target_id", "str", "Crucible target identifier"),
        ],
        return_type="ResearchDeliverableBundle",
        pre_conditions=["exploratory_token_lease >= 60000"],
        post_conditions=["is_certified == True"],
        modifies_nouns=["ResearchDeliverableBundle", "HypothesisDefinition", "MerkleDagWitness"],
    )

    steps_discovery = [
        VerbCompositionStep(
            child_contract_id="sub_island_isolation",
            child_verb_name="SpawnQuarantinedIslands",
            argument_bindings={"target_id": "target_id"},
            output_binding="island_manifests",
        ),
        VerbCompositionStep(
            child_contract_id="sub_hypothesis_engine",
            child_verb_name="FormulateSMTHypotheses",
            argument_bindings={"target_id": "target_id"},
            output_binding="hypotheses",
        ),
        VerbCompositionStep(
            child_contract_id="sub_taboo_filter",
            child_verb_name="FilterTabooDistance",
            argument_bindings={"target_id": "target_id"},
            output_binding="taboo_matrix",
        ),
    ]

    composed = {
        "ComposeEpistemicDiscovery": ComposedVerb(
            parent_verb=parent_verb_discovery,
            child_steps=steps_discovery,
        )
    }

    # Child Sub-Contract 1: Island Isolation
    sub_isolation = ContractIR(
        contract_id="sub_island_isolation",
        title="Zero-Context Island Isolation Subcontract",
        description="Spawns N>=3 hermetic research islands with unique cryptographic entropy seeds.",
    )
    sub_isolation.add_verb(DomainVerb(
        name="SpawnQuarantinedIslands",
        description="Spawn isolated islands and bind entropy seeds.",
        pre_conditions=["exploratory_token_lease >= 60000"],
        post_conditions=["islands_seeded == True"],
        modifies_nouns=["ZeroContextIslandManifest"],
    ))

    # Child Sub-Contract 2: Hypothesis Engine
    sub_hypothesis = ContractIR(
        contract_id="sub_hypothesis_engine",
        title="SMT Hypothesis Formulation Subcontract",
        description="Synthesizes SMT-LIB2 formalized conjectures.",
    )
    sub_hypothesis.add_verb(DomainVerb(
        name="FormulateSMTHypotheses",
        description="Formulate hypotheses under governing axioms.",
        pre_conditions=["islands_seeded == True"],
        post_conditions=["hypotheses_formulated == True"],
        modifies_nouns=["HypothesisDefinition"],
    ))

    # Child Sub-Contract 3: Taboo Filter
    sub_taboo = ContractIR(
        contract_id="sub_taboo_filter",
        title="Weisfeiler-Lehman Taboo Distance Filter Subcontract",
        description="Computes normalized graph distance and enforces D >= 0.40.",
    )
    sub_taboo.add_verb(DomainVerb(
        name="FilterTabooDistance",
        description="Enforces taboo distance threshold across all candidate pairs.",
        pre_conditions=["hypotheses_formulated == True"],
        post_conditions=["taboo_distance_satisfied == True", "is_certified == True"],
        modifies_nouns=["TabooDistanceMatrix", "ResearchDeliverableBundle"],
    ))

    contract = ContractIR(
        contract_id="contract_g4b_researcher",
        title="Generation 4b Autonomous Decoupled Research Service Contract",
        description="Formal invariants, nouns, and verbs governing sovereign research service, SMT proofs, and RFC protocol bus",
        nouns={n.name: n for n in nouns},
        verbs={},
        composed_verbs=composed,
    )

    contract.sub_contracts[sub_isolation.contract_id] = sub_isolation
    contract.sub_contracts[sub_hypothesis.contract_id] = sub_hypothesis
    contract.sub_contracts[sub_taboo.contract_id] = sub_taboo

    return contract


def build_researcher_statechart_ir() -> StatechartIR:
    """Builds the 32-state hierarchical StatechartIR for `soc_g4b_researcher`."""
    # Boot compound state (2 states)
    sn_boot_init = StateNode(id="boot.sovereign_init", node_type=StateNodeType.ATOMIC, description="Sovereign Init", transitions=[
        Transition(event="EV_BOOT_POST", target="boot.quarantine_setup"),
    ])
    sn_boot_setup = StateNode(id="boot.quarantine_setup", node_type=StateNodeType.ATOMIC, description="Quarantine Setup", transitions=[
        Transition(event="EV_BOOT_READY", target="active.epistemic_discovery"),
    ])
    sn_boot = StateNode(
        id="boot",
        node_type=StateNodeType.COMPOUND,
        initial="boot.sovereign_init",
        description="Boot stratum",
        states={
            "boot.sovereign_init": sn_boot_init,
            "boot.quarantine_setup": sn_boot_setup,
        },
    )

    # Stratum 1: epistemic_discovery (6 states)
    sn_quarantine = StateNode(id="island_quarantine", node_type=StateNodeType.ATOMIC, description="Zero-Context Island Quarantine", transitions=[
        Transition(event="EV_ISLANDS_SEEDED", target="hypothesis_formulation"),
    ])
    sn_hyp = StateNode(id="hypothesis_formulation", node_type=StateNodeType.ATOMIC, description="Hypothesis Formulation", transitions=[
        Transition(event="EV_HYPOTHESIS_FORMULATED", target="constraint_boundary_mapping"),
    ])
    sn_bounds = StateNode(id="constraint_boundary_mapping", node_type=StateNodeType.ATOMIC, description="Constraint Boundary Mapping", transitions=[
        Transition(event="EV_BOUNDARIES_MAPPED", target="discovery_evaluating"),
    ])
    sn_eval = StateNode(id="discovery_evaluating", node_type=StateNodeType.ATOMIC, description="Discovery Evaluating", transitions=[
        Transition(event="EV_SHORTCUT_DETECTED", target="anti_shortcut_enclave"),
        Transition(event="EV_CHECKPOINT_DISCOVERY", target="discovery_deep_history"),
        Transition(event="EV_START_FUZZER", target="active.parallel_fuzzer"),
        Transition(event="EV_START_METER", target="active.parallel_meter"),
        Transition(event="EV_DISCOVERY_CERTIFIED", target="active.adversarial_crucible"),
    ])
    sn_disc_hist = StateNode(id="discovery_deep_history", node_type=StateNodeType.HISTORY, history_type=HistoryType.DEEP, description="Discovery Deep History", transitions=[
        Transition(event="EV_RESTORE_DISCOVERY", target="hypothesis_formulation"),
    ])
    sn_anti_shortcut = StateNode(id="anti_shortcut_enclave", node_type=StateNodeType.ATOMIC, description="Anti-Shortcut Recovery Enclave", transitions=[
        Transition(event="EV_UNWIND_SHORTCUT", target="hypothesis_formulation"),
    ])

    sn_discovery = StateNode(
        id="active.epistemic_discovery",
        node_type=StateNodeType.COMPOUND,
        initial="island_quarantine",
        description="Epistemic Discovery Stratum",
        states={
            "island_quarantine": sn_quarantine,
            "hypothesis_formulation": sn_hyp,
            "constraint_boundary_mapping": sn_bounds,
            "discovery_evaluating": sn_eval,
            "discovery_deep_history": sn_disc_hist,
            "anti_shortcut_enclave": sn_anti_shortcut,
        },
    )

    # Stratum 2: adversarial_crucible (8 states)
    sn_nov = StateNode(id="novelty_search_active", node_type=StateNodeType.ATOMIC, description="Novelty Search Active", transitions=[
        Transition(event="EV_EVALUATE_NOVELTY", target="taboo_distance_check"),
    ])
    sn_taboo = StateNode(id="taboo_distance_check", node_type=StateNodeType.ATOMIC, description="Taboo Distance Check (D >= 0.40)", transitions=[
        Transition(event="EV_TABOO_BREACH", target="mode_collapse_enclave"),
        Transition(event="EV_TABOO_SATISFIED", target="dialectical_negation_inject"),
    ])
    sn_mode_col = StateNode(id="mode_collapse_enclave", node_type=StateNodeType.ATOMIC, description="Mode Collapse Recovery Enclave", transitions=[
        Transition(event="EV_FORCE_NEGATION", target="dialectical_negation_inject"),
    ])
    sn_neg = StateNode(id="dialectical_negation_inject", node_type=StateNodeType.ATOMIC, description="Dialectical Negation Inject (NEG_PRIMITIVE)", transitions=[
        Transition(event="EV_NEGATION_APPLIED", target="boundary_stress_fuzzing"),
    ])
    sn_fuzz = StateNode(id="boundary_stress_fuzzing", node_type=StateNodeType.ATOMIC, description="Boundary Stress & Byzantine Fuzzing", transitions=[
        Transition(event="EV_STRESS_PASSED", target="pareto_frontier_filter"),
    ])
    sn_pareto = StateNode(id="pareto_frontier_filter", node_type=StateNodeType.ATOMIC, description="5D Pareto Frontier Filter", transitions=[
        Transition(event="EV_CHECKPOINT_CRUCIBLE", target="crucible_deep_history"),
        Transition(event="EV_PARETO_OPTIMAL", target="crucible_certified"),
    ])
    sn_cruc_hist = StateNode(id="crucible_deep_history", node_type=StateNodeType.HISTORY, history_type=HistoryType.DEEP, description="Crucible Deep History", transitions=[
        Transition(event="EV_RESTORE_CRUCIBLE", target="novelty_search_active"),
    ])
    sn_cert = StateNode(id="crucible_certified", node_type=StateNodeType.ATOMIC, description="Crucible Certified", transitions=[
        Transition(event="EV_EMIT_DELIVERABLES", target="active.protocol_adjudication"),
    ])

    sn_crucible = StateNode(
        id="active.adversarial_crucible",
        node_type=StateNodeType.COMPOUND,
        initial="novelty_search_active",
        description="Adversarial Crucible Stratum",
        states={
            "novelty_search_active": sn_nov,
            "taboo_distance_check": sn_taboo,
            "mode_collapse_enclave": sn_mode_col,
            "dialectical_negation_inject": sn_neg,
            "boundary_stress_fuzzing": sn_fuzz,
            "pareto_frontier_filter": sn_pareto,
            "crucible_deep_history": sn_cruc_hist,
            "crucible_certified": sn_cert,
        },
    )

    # Stratum 3: protocol_adjudication (7 states)
    sn_pub = StateNode(id="spec_bundle_published", node_type=StateNodeType.ATOMIC, description="Spec Bundle Published", transitions=[
        Transition(event="EV_BUILDER_ATTACHED", target="builder_rfc_ingress"),
    ])
    sn_rfc = StateNode(id="builder_rfc_ingress", node_type=StateNodeType.ATOMIC, description="Builder RFC Ingress", transitions=[
        Transition(event="EV_SUBMIT_RFC", target="rfc_counter_proof_eval"),
    ])
    sn_proof = StateNode(id="rfc_counter_proof_eval", node_type=StateNodeType.ATOMIC, description="RFC Counter Proof SMT Evaluation", transitions=[
        Transition(event="EV_AXIOM_VIOLATION", target="rfc_counter_proof_enclave"),
        Transition(event="EV_AMENDMENT_PROVED", target="spec_amendment_signed"),
    ])
    sn_counter = StateNode(id="rfc_counter_proof_enclave", node_type=StateNodeType.ATOMIC, description="RFC Counter-Proof Enclave", transitions=[
        Transition(event="EV_REJECT_RFC_WITH_PROOF", target="builder_rfc_ingress"),
    ])
    sn_sign = StateNode(id="spec_amendment_signed", node_type=StateNodeType.ATOMIC, description="Spec Amendment Signed", transitions=[
        Transition(event="EV_CHECKPOINT_ADJUDICATION", target="adjudication_deep_history"),
        Transition(event="EV_ALL_RFCS_RESOLVED", target="generational_handover_ready"),
    ])
    sn_adj_hist = StateNode(id="adjudication_deep_history", node_type=StateNodeType.HISTORY, history_type=HistoryType.DEEP, description="Adjudication Deep History", transitions=[
        Transition(event="EV_RESTORE_ADJUDICATION", target="spec_bundle_published"),
    ])
    sn_handover = StateNode(id="generational_handover_ready", node_type=StateNodeType.ATOMIC, description="Generational Handover Ready", transitions=[
        Transition(event="EV_TRIGGER_GLOBAL_UNWIND", target="unwind_recovery_enclave"),
        Transition(event="EV_SEAL_CRUCIBLE", target="epistemic_zenith_sealed"),
    ])

    sn_adjudication = StateNode(
        id="active.protocol_adjudication",
        node_type=StateNodeType.COMPOUND,
        initial="spec_bundle_published",
        description="Protocol Adjudication Stratum",
        states={
            "spec_bundle_published": sn_pub,
            "builder_rfc_ingress": sn_rfc,
            "rfc_counter_proof_eval": sn_proof,
            "rfc_counter_proof_enclave": sn_counter,
            "spec_amendment_signed": sn_sign,
            "adjudication_deep_history": sn_adj_hist,
            "generational_handover_ready": sn_handover,
        },
    )

    # Parallel Region 1: concurrent_byzantine_fuzzer (4 states)
    sn_fuzzer_quiescent = StateNode(id="fuzzer_quiescent", node_type=StateNodeType.ATOMIC, description="Fuzzer Quiescent", transitions=[
        Transition(event="EV_FUZZ_TICK", target="fuzzer_generating_vectors"),
    ])
    sn_fuzzer_gen = StateNode(id="fuzzer_generating_vectors", node_type=StateNodeType.ATOMIC, description="Fuzzer Generating Vectors", transitions=[
        Transition(event="EV_VECTORS_DISPATCHED", target="fuzzer_evaluating_response"),
    ])
    sn_fuzzer_eval = StateNode(id="fuzzer_evaluating_response", node_type=StateNodeType.ATOMIC, description="Fuzzer Evaluating Response", transitions=[
        Transition(event="EV_FAULT_TRAPPED", target="fuzzer_fault_trapped"),
    ])
    sn_fuzzer_trap = StateNode(id="fuzzer_fault_trapped", node_type=StateNodeType.ATOMIC, description="Fuzzer Fault Trapped", transitions=[
        Transition(event="EV_FAULT_LOGGED", target="active.epistemic_discovery"),
    ])

    sn_parallel_fuzzer = StateNode(
        id="active.parallel_fuzzer",
        node_type=StateNodeType.COMPOUND,
        initial="fuzzer_quiescent",
        description="Concurrent Byzantine Fuzzer Region",
        states={
            "fuzzer_quiescent": sn_fuzzer_quiescent,
            "fuzzer_generating_vectors": sn_fuzzer_gen,
            "fuzzer_evaluating_response": sn_fuzzer_eval,
            "fuzzer_fault_trapped": sn_fuzzer_trap,
        },
    )

    # Parallel Region 2: landauer_thermodynamic_meter (4 states)
    sn_meter_mon = StateNode(id="meter_monitoring", node_type=StateNodeType.ATOMIC, description="Meter Monitoring", transitions=[
        Transition(event="EV_BIT_ERASURE_EVENT", target="meter_bit_erasure_sample"),
    ])
    sn_meter_sample = StateNode(id="meter_bit_erasure_sample", node_type=StateNodeType.ATOMIC, description="Meter Bit Erasure Sample", transitions=[
        Transition(event="EV_REBALANCE_CAPITAL", target="meter_capital_rebalance"),
    ])
    sn_meter_rebal = StateNode(id="meter_capital_rebalance", node_type=StateNodeType.ATOMIC, description="Meter Capital Rebalance", transitions=[
        Transition(event="EV_BUDGET_EXHAUSTED", target="meter_cutoff_tripped"),
        Transition(event="EV_CONTINUE_MONITORING", target="active.epistemic_discovery"),
    ])
    sn_meter_trip = StateNode(id="meter_cutoff_tripped", node_type=StateNodeType.ATOMIC, description="Meter Cutoff Tripped", transitions=[
        Transition(event="EV_RETRY_METER", target="active.epistemic_discovery"),
    ])

    sn_parallel_meter = StateNode(
        id="active.parallel_meter",
        node_type=StateNodeType.COMPOUND,
        initial="meter_monitoring",
        description="Landauer Thermodynamic Meter Region",
        states={
            "meter_monitoring": sn_meter_mon,
            "meter_bit_erasure_sample": sn_meter_sample,
            "meter_capital_rebalance": sn_meter_rebal,
            "meter_cutoff_tripped": sn_meter_trip,
        },
    )

    # Active compound state (encompassing 3 strata and 2 parallel regions)
    sn_active = StateNode(
        id="active",
        node_type=StateNodeType.COMPOUND,
        initial="active.epistemic_discovery",
        description="Active Research and Adjudication Operations",
        states={
            "active.epistemic_discovery": sn_discovery,
            "active.adversarial_crucible": sn_crucible,
            "active.protocol_adjudication": sn_adjudication,
            "active.parallel_fuzzer": sn_parallel_fuzzer,
            "active.parallel_meter": sn_parallel_meter,
        },
    )

    # Enclaves and Terminal
    sn_unwind_recovery = StateNode(id="unwind_recovery_enclave", node_type=StateNodeType.ATOMIC, description="Global Unwind Recovery Enclave", transitions=[
        Transition(event="EV_UNWIND_COMPLETE", target="generational_handover_ready"),
    ])
    sn_sealed = StateNode(id="epistemic_zenith_sealed", node_type=StateNodeType.FINAL, description="Epistemic Zenith Sealed")

    root = StateNode(
        id="researcher_system",
        node_type=StateNodeType.COMPOUND,
        initial="boot",
        description="Root hierarchical state machine for Generation 4b Sovereign Decoupled Research Service",
        states={
            "boot": sn_boot,
            "active": sn_active,
            "unwind_recovery_enclave": sn_unwind_recovery,
            "epistemic_zenith_sealed": sn_sealed,
        },
    )

    return StatechartIR(
        id="statechart_g4b_researcher",
        root=root,
        context_schema={
            "target_id": "str",
            "campaign_id": "str",
            "erased_bits": "int",
            "unspent_capital": "int",
        },
    )


def build_researcher_topology_ir() -> TopologyIR:
    """Builds the 6-node TopologyIR on 192.168.40.0/24 subnet for `soc_g4b_researcher`."""
    nodes = {
        "node_research_kernel": TopologyNode("node_research_kernel", NodeRole.COMPILER_CORE, "192.168.40.10", 8201, ["epistemic_discovery", "crucible_orchestration"]),
        "node_island_manager": TopologyNode("node_island_manager", NodeRole.WORKER, "192.168.40.20", 8202, ["zero_context_quarantine", "island_spawning"]),
        "node_taboo_engine": TopologyNode("node_taboo_engine", NodeRole.VERIFIER, "192.168.40.30", 8203, ["weisfeiler_lehman_hash", "taboo_distance_matrix"]),
        "node_z3_prover": TopologyNode("node_z3_prover", NodeRole.VERIFIER, "192.168.40.40", 8204, ["smt_solving", "contract_composition_proof"]),
        "node_rfc_bus": TopologyNode("node_rfc_bus", NodeRole.GATEWAY, "192.168.40.50", 8205, ["spec_adjustment_ingress", "protocol_negotiation"]),
        "node_telemetry_evaluator": TopologyNode("node_telemetry_evaluator", NodeRole.STORAGE_LEAF, "192.168.40.60", 8206, ["merkle_dag_anchoring", "landauer_accounting"]),
    }

    channels = [
        NetworkChannel("chan_kernel_to_islands", "node_research_kernel", "node_island_manager", ChannelType.RPC, 8202, 20, True),
        NetworkChannel("chan_islands_to_taboo", "node_island_manager", "node_taboo_engine", ChannelType.STREAM, 8203, 15, True),
        NetworkChannel("chan_kernel_to_prover", "node_research_kernel", "node_z3_prover", ChannelType.RPC, 8204, 25, True),
        NetworkChannel("chan_kernel_to_rfc", "node_research_kernel", "node_rfc_bus", ChannelType.EVENT_BUS, 8205, 10, True),
        NetworkChannel("chan_taboo_to_rfc", "node_taboo_engine", "node_rfc_bus", ChannelType.EVENT_BUS, 8205, 30, True),
        NetworkChannel("chan_rfc_to_prover", "node_rfc_bus", "node_z3_prover", ChannelType.RPC, 8204, 20, True),
        NetworkChannel("chan_telemetry_stream", "node_research_kernel", "node_telemetry_evaluator", ChannelType.STREAM, 8206, 15, True),
        NetworkChannel("chan_kernel_to_telemetry", "node_telemetry_evaluator", "node_research_kernel", ChannelType.EVENT_BUS, 8201, 15, True),
    ]

    consensus = ConsensusContract(
        protocol=ConsensusProtocol.SHEAF_QUORUM,
        quorum_fraction=0.67,
        heartbeat_interval_ms=500,
        partition_strategy="fail_closed",
    )

    return TopologyIR(
        topology_id="topology_g4b_researcher",
        nodes=nodes,
        channels=channels,
        consensus=consensus,
    )


def build_researcher_domain_spec() -> Dict[str, Any]:
    """Returns the serializable domain_spec bundle for `soc_g4b_researcher`."""
    contract = build_researcher_contract_ir()
    statechart = build_researcher_statechart_ir()
    topology = build_researcher_topology_ir()
    endpoints = [
        f"http://{n.host_interface}:{n.port}"
        for n in topology.nodes.values()
    ]
    return {
        "contract_ir": contract.to_dict(),
        "statechart_ir": statechart.to_dict(),
        "topology_ir": topology.to_dict(),
        "endpoints": endpoints,
        "canonical_port": 8201,
        "required_invariants": REQUIRED_INVARIANTS_RESEARCHER,
    }
