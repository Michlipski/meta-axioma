"""Milestone 1 Formal Verification Suite & Quine Representation Crucible.

Verifies:
1. PhysicalTokenMeter & ThermodynamicLedger (60/40 capital partition & Landauer dissipation)
2. Waterloo SoC Models & Normalizer ([L1-G3B-000] Invariant across Tiers 1, 2, 3 and Fractal SoCs)
3. Hierarchical Statechart IR (XState v5 compound, parallel, history states, lossless serialization)
4. Compositional Contract IR (Nouns, Verbs, Pre/Post composition proofs, round-trip serialization)
5. Distributed Topology IR ([L1-G3B-012] Topological Fidelity & Anti-Loopback Gate)
6. The Quine Crucible Representation Test: Mathematically represents System G3b itself in the IR!
"""

import os
import sys
import unittest
from pathlib import Path

# Add src to sys.path
SRC_DIR = Path(__file__).resolve().parent.parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from g3b_compiler.thermodynamics import (
    PhysicalTokenMeter,
    ThermodynamicLedger,
    ProtectedCapitalViolation,
    ThermodynamicExhaustionError,
    BOLTZMANN_K,
    AMBIENT_T_KELVIN,
    LN2,
)
from g3b_compiler.soc import (
    SoCAltitude,
    FrictionSeverity,
    ConstraintType,
    Actor,
    Friction,
    EnvironmentalConstraint,
    SituationOfConcern,
    PitchInput,
    ReferenceProductInput,
    SoCNormalizer,
    SoCNormalizationError,
)
from g3b_compiler.ir import (
    StateNodeType,
    HistoryType,
    Transition,
    StateNode,
    StatechartIR,
    FieldDef,
    DomainNoun,
    DomainVerb,
    VerbCompositionStep,
    ComposedVerb,
    ContractProofWitness,
    ContractIR,
    NodeRole,
    ChannelType,
    ConsensusProtocol,
    TopologyNode,
    NetworkChannel,
    ConsensusContract,
    TopologyIR,
    TopologicalLoopbackViolation,
)


class TestThermodynamicLedger(unittest.TestCase):
    """Verifies physical token counting and thermodynamic capital partition."""

    def test_physical_token_meter(self):
        text = "def compile_system(soc: SituationOfConcern) -> SystemArtifact:\n    return True"
        count = PhysicalTokenMeter.count(text)
        self.assertGreater(count, 10)
        self.assertEqual(PhysicalTokenMeter.count(""), 0)

    def test_capital_partition_and_spend(self):
        ledger = ThermodynamicLedger.create(total_budget=600000)
        self.assertEqual(ledger.total_budget, 600000)
        self.assertEqual(ledger.exploratory_cap, 360000)  # 60%
        self.assertEqual(ledger.protected_floor, 240000)  # 40%

        # Exploratory spend
        ledger.spend_exploratory(100000, bits_erased=50000)
        self.assertEqual(ledger.exploratory_spent, 100000)
        self.assertEqual(ledger.bits_erased, 50000)
        self.assertAlmostEqual(
            ledger.dissipated_joules,
            BOLTZMANN_K * AMBIENT_T_KELVIN * LN2 * 50000,
            places=25
        )

        # Protected spend
        ledger.spend_protected(50000)
        self.assertEqual(ledger.protected_spent, 50000)

        # Attempt to overspend exploratory capital
        with self.assertRaises(ProtectedCapitalViolation):
            ledger.spend_exploratory(300000)  # 100k + 300k > 360k

        # Remaining capacity
        state = ledger.to_dict()
        self.assertEqual(state["exploratory_remaining"], 260000)
        self.assertEqual(state["protected_remaining"], 190000)


class TestWaterlooSoCNormalizer(unittest.TestCase):
    """Verifies [L1-G3B-000] Situation of Concern Normalization Invariant."""

    def test_normalize_tier1_direct(self):
        soc = SituationOfConcern(
            soc_id="soc_001",
            title="Clinician Transcription Fatigue",
            narrative="Clinicians spend four hours transcribing handwritten notes into rigid EHRs.",
            altitude=SoCAltitude.MACRO,
            actors=[Actor(name="Clinician", role="Medical Staff", frustrations=["Transcription burden"])],
            frictions=[Friction(description="High data entry friction", severity=FrictionSeverity.HIGH)],
            unmet_needs=["Zero-friction patient data capture"],
        )
        normalized = SoCNormalizer.normalize_tier1(soc)
        self.assertEqual(normalized.soc_id, "soc_001")
        self.assertEqual(normalized.actors[0].name, "Clinician")

    def test_deconstruct_tier2_pitch(self):
        pitch = PitchInput(
            title="Lexis Margin Companion",
            elevator_pitch="Build a React app with a spaced-repetition card flip interface for language students.",
            target_audience="Foreign literature readers",
            intended_features=["Margin highlight capture", "Card review modal"],
            solution_biases=["React app", "Card flip interface"],
        )
        soc = SoCNormalizer.deconstruct_pitch(pitch, soc_id="soc_lexis_001")
        self.assertEqual(soc.soc_id, "soc_lexis_001")
        self.assertEqual(soc.altitude, SoCAltitude.MACRO)
        self.assertEqual(len(soc.actors), 1)
        self.assertEqual(soc.actors[0].role, "Foreign literature readers")
        # Preconceived biases extracted and documented
        self.assertTrue(any("React app" in b for b in soc.induced_frictions))
        # Frictions derived from intended features
        self.assertEqual(len(soc.frictions), 2)

    def test_reverse_audit_tier3_product(self):
        ref = ReferenceProductInput(
            product_name="Legacy Anki",
            historical_problem_solved="Efficient memorization via spaced repetition algorithm",
            known_limitations_and_bloat=[
                "Manual card authoring takes hours",
                "Clunky sync setup with desktop dependency",
                "High context switching from reading material",
            ],
        )
        soc = SoCNormalizer.reverse_audit_product(ref, soc_id="soc_anki_audit")
        self.assertEqual(soc.soc_id, "soc_anki_audit")
        self.assertEqual(len(soc.frictions), 3)
        self.assertEqual(soc.frictions[0].severity, FrictionSeverity.HIGH)
        self.assertEqual(len(soc.unmet_needs), 3)

    def test_fractal_decomposition(self):
        parent_soc = SituationOfConcern(
            soc_id="macro_reading",
            title="Reading Flow Breakdown",
            narrative="Readers lose cognitive immersion when encountering unknown vocabulary.",
            altitude=SoCAltitude.MACRO,
            actors=[Actor(name="Reader", role="Student")],
            frictions=[Friction(description="Immersion loss", severity=FrictionSeverity.HIGH)],
            unmet_needs=["Zero-latency word understanding"],
        )
        child_specs = [
            {
                "soc_id": "meso_offline_sync",
                "title": "Offline Reading Sync Tension",
                "narrative": "Reader reads on an airplane without WiFi; captured annotations conflict with cloud.",
                "frictions": [{"description": "Cloud sync failure", "severity": "CRITICAL"}],
                "unmet_needs": ["Local-first multi-device sync without data loss"],
            }
        ]
        SoCNormalizer.decompose_fractal(parent_soc, child_specs)
        self.assertEqual(len(parent_soc.sub_socs), 1)
        child = parent_soc.sub_socs[0]
        self.assertEqual(child.soc_id, "meso_offline_sync")
        self.assertEqual(child.altitude, SoCAltitude.MESO)
        self.assertEqual(child.parent_soc_id, "macro_reading")


class TestHierarchicalStatechartIR(unittest.TestCase):
    """Verifies XState v5 compound, parallel, and history states with lossless serialization."""

    def test_hierarchical_statechart_roundtrip(self):
        # Build compound child state
        crucible_children = {
            "generating": StateNode(
                id="crucible.generating",
                node_type=StateNodeType.ATOMIC,
                transitions=[Transition(event="TASK_PRODUCED", target="crucible.auditing")],
            ),
            "auditing": StateNode(
                id="crucible.auditing",
                node_type=StateNodeType.ATOMIC,
                transitions=[
                    Transition(event="AUDIT_PASSED", target="crucible.complete"),
                    Transition(event="AUDIT_FAILED", target="crucible.repairing"),
                ],
            ),
            "repairing": StateNode(
                id="crucible.repairing",
                node_type=StateNodeType.ATOMIC,
                transitions=[Transition(event="REPAIRED", target="crucible.auditing")],
            ),
            "complete": StateNode(id="crucible.complete", node_type=StateNodeType.FINAL),
        }

        crucible_node = StateNode(
            id="root.crucible",
            node_type=StateNodeType.COMPOUND,
            initial="generating",
            states=crucible_children,
            transitions=[Transition(event="CRUCIBLE_DONE", target="root.verified")],
        )

        # Build parallel region
        telemetry_region = StateNode(
            id="parallel.telemetry",
            node_type=StateNodeType.COMPOUND,
            initial="active",
            states={
                "active": StateNode(id="parallel.telemetry.active", node_type=StateNodeType.ATOMIC),
            },
        )
        thermal_region = StateNode(
            id="parallel.thermal",
            node_type=StateNodeType.COMPOUND,
            initial="monitoring",
            states={
                "monitoring": StateNode(id="parallel.thermal.monitoring", node_type=StateNodeType.ATOMIC),
            },
        )

        parallel_node = StateNode(
            id="root.monitoring",
            node_type=StateNodeType.PARALLEL,
            states={"telemetry": telemetry_region, "thermal": thermal_region},
        )

        history_node = StateNode(
            id="root.recovery_history",
            node_type=StateNodeType.HISTORY,
            history_type=HistoryType.DEEP,
        )

        verified_node = StateNode(id="root.verified", node_type=StateNodeType.FINAL)

        root_node = StateNode(
            id="root",
            node_type=StateNodeType.COMPOUND,
            initial="crucible",
            states={
                "crucible": crucible_node,
                "monitoring": parallel_node,
                "recovery_history": history_node,
                "verified": verified_node,
            },
        )

        chart = StatechartIR(
            id="g3b_meta_crucible",
            root=root_node,
            context_schema={"tokens_spent": "int", "active_leaf": "str"},
            initial_context={"tokens_spent": 0, "active_leaf": "root"},
        )

        # Integrity check
        errors = chart.validate_integrity()
        self.assertEqual(errors, [], f"Statechart integrity errors: {errors}")

        # Serialization round-trip: f^-1(f(x)) == x
        json_repr = chart.to_json()
        reconstructed = StatechartIR.from_json(json_repr)
        self.assertEqual(chart.to_dict(), reconstructed.to_dict())
        self.assertEqual(reconstructed.id, "g3b_meta_crucible")
        self.assertEqual(len(reconstructed.get_all_state_ids()), 13)
        self.assertIn("crucible.auditing", reconstructed.get_all_state_ids())


class TestCompositionalContractIR(unittest.TestCase):
    """Verifies Compositional Contract IR and formal composition verification."""

    def test_compositional_proof_witness(self):
        # 1. Define parent contract
        contract = ContractIR(
            contract_id="contract_g3b_core",
            title="G3b Universal Systems Compiler Core Contract",
            description="Parent contract for compiling software systems from Waterloo SoC.",
        )

        # Domain Nouns
        contract.add_noun(DomainNoun(
            name="NormalizedSoC",
            description="A certified Waterloo Situation of Concern.",
            fields=[
                FieldDef("soc_id", "str"),
                FieldDef("frictions_count", "int"),
            ],
            invariants=["frictions_count > 0"],
        ))

        contract.add_noun(DomainNoun(
            name="EmittedSystemArtifact",
            description="Verified physical system files on disk with passing substrate tests.",
            fields=[
                FieldDef("manifest_path", "str"),
                FieldDef("test_exit_code", "int"),
                FieldDef("passing_assertions", "int"),
            ],
            invariants=["test_exit_code == 0", "passing_assertions > 0"],
        ))

        # Parent Verb
        parent_verb = DomainVerb(
            name="CompileUniversalSystem",
            description="Compiles any software system from a certified SoC to verified disk artifacts.",
            pre_conditions=["soc_certified == True", "exploratory_capital >= 50000"],
            post_conditions=[
                "substrate_tests_passed == True",
                "non_zero_passing_assertions == True",
                "empirical_witness_recorded == True",
            ],
            modifies_nouns=["NormalizedSoC", "EmittedSystemArtifact"],
        )

        # Child Sub-Contracts
        sub_normalizer = ContractIR(
            contract_id="sub_normalizer",
            title="SoC Normalizer Subcontract",
            description="Normalizes input into certified SoC.",
        )
        sub_normalizer.add_verb(DomainVerb(
            name="DeconstructAndCertify",
            description="Transforms input into certified SoC.",
            pre_conditions=["soc_certified == True"],
            post_conditions=["ir_ready == True", "fractal_tasks_queued == True"],
        ))

        sub_crucible = ContractIR(
            contract_id="sub_crucible",
            title="Fractal Task Crucible Subcontract",
            description="Recursively executes subagents on leaf nodes with zero-trust micro-auditing.",
        )
        sub_crucible.add_verb(DomainVerb(
            name="ExecuteFractalCrucible",
            description="Processes task stack and produces verified AST representations.",
            pre_conditions=["ir_ready == True", "fractal_tasks_queued == True"],
            post_conditions=["leaf_nodes_audited == True", "code_manifest_ready == True"],
        ))

        sub_emitter = ContractIR(
            contract_id="sub_emitter",
            title="Substrate Emitter Subcontract",
            description="Emits non-zero files to disk and runs test suite on live substrate.",
        )
        sub_emitter.add_verb(DomainVerb(
            name="EmitAndVerifySubstrate",
            description="Writes files and executes live test suite.",
            pre_conditions=["leaf_nodes_audited == True", "code_manifest_ready == True"],
            post_conditions=[
                "substrate_tests_passed == True",
                "non_zero_passing_assertions == True",
                "empirical_witness_recorded == True",
            ],
            modifies_nouns=["EmittedSystemArtifact"],
        ))

        contract.sub_contracts["sub_normalizer"] = sub_normalizer
        contract.sub_contracts["sub_crucible"] = sub_crucible
        contract.sub_contracts["sub_emitter"] = sub_emitter

        # Composed Verb
        composed = ComposedVerb(
            parent_verb=parent_verb,
            child_steps=[
                VerbCompositionStep("sub_normalizer", "DeconstructAndCertify"),
                VerbCompositionStep("sub_crucible", "ExecuteFractalCrucible"),
                VerbCompositionStep("sub_emitter", "EmitAndVerifySubstrate"),
            ],
        )
        contract.add_composed_verb(composed)

        # Verify Composition Proof Witness
        witness = contract.verify_composition("CompileUniversalSystem")
        self.assertTrue(witness.is_valid, f"Proof witness failed: {witness.unresolved_obligations}")
        self.assertEqual(len(witness.unresolved_obligations), 0)
        self.assertEqual(len(witness.pre_condition_checks), 5)  # 1 from step0 + 2 from step1 + 2 from step2 = 5
        self.assertEqual(len(witness.post_condition_checks), 3)

        # Round-trip serialization: f^-1(f(x)) == x
        json_repr = contract.to_json()
        reconstructed = ContractIR.from_json(json_repr)
        self.assertEqual(contract.to_dict(), reconstructed.to_dict())

    def test_compositional_proof_failure_on_unsatisfied_precondition(self):
        contract = ContractIR(contract_id="broken_parent", title="Broken Parent Contract", description="")
        parent_verb = DomainVerb(
            name="BrokenOp",
            description="",
            pre_conditions=["initial_state == True"],
            post_conditions=["terminal_state == True"],
        )
        sub = ContractIR(contract_id="broken_sub", title="Broken Sub", description="")
        sub.add_verb(DomainVerb(
            name="RequiresMissingSecret",
            description="",
            pre_conditions=["missing_secret_key == True"],  # Unsatisfied!
            post_conditions=["terminal_state == True"],
        ))
        contract.sub_contracts["broken_sub"] = sub
        contract.add_composed_verb(ComposedVerb(
            parent_verb=parent_verb,
            child_steps=[VerbCompositionStep("broken_sub", "RequiresMissingSecret")],
        ))

        witness = contract.verify_composition("BrokenOp")
        self.assertFalse(witness.is_valid)
        self.assertIn("missing_secret_key", witness.unresolved_obligations[0])


class TestDistributedTopologyIR(unittest.TestCase):
    """Verifies [L1-G3B-008] and [L1-G3B-012] Anti-Loopback Fidelity Invariant."""

    def test_valid_distributed_topology(self):
        topo = TopologyIR(topology_id="topo_axioma_cluster")
        topo.add_node(TopologyNode("node_orch", NodeRole.ORCHESTRATOR, "192.168.1.10", 8080))
        topo.add_node(TopologyNode("node_verifier", NodeRole.VERIFIER, "192.168.1.20", 8081))
        topo.add_node(TopologyNode("node_storage", NodeRole.STORAGE_LEAF, "192.168.1.30", 8082))

        topo.add_channel(NetworkChannel("ch_orch_ver", "node_orch", "node_verifier", ChannelType.RPC, 8081))
        topo.add_channel(NetworkChannel("ch_orch_stor", "node_orch", "node_storage", ChannelType.STREAM, 8082))

        topo.consensus = ConsensusContract(
            protocol=ConsensusProtocol.SHEAF_QUORUM,
            quorum_fraction=0.67,
            heartbeat_interval_ms=500,
        )

        errors = topo.validate_topological_fidelity()
        self.assertEqual(errors, [])
        topo.assert_topological_fidelity()

        # Lossless round-trip
        json_repr = topo.to_json()
        reconstructed = TopologyIR.from_json(json_repr)
        self.assertEqual(topo.to_dict(), reconstructed.to_dict())

    def test_anti_loopback_gate_violation(self):
        topo = TopologyIR(topology_id="topo_compromised_cluster")
        topo.add_node(TopologyNode("node_1", NodeRole.ORCHESTRATOR, "127.0.0.1", 8080))  # LOOPBACK!
        topo.add_node(TopologyNode("node_2", NodeRole.WORKER, "localhost", 8081))         # LOOPBACK!

        errors = topo.validate_topological_fidelity()
        self.assertEqual(len(errors), 2)
        self.assertTrue(any("L1-G3B-012 Violation" in err for err in errors))

        with self.assertRaises(TopologicalLoopbackViolation):
            topo.assert_topological_fidelity()


class TestQuineCrucibleRepresentation(unittest.TestCase):
    """THE QUINE CRUCIBLE: Proves mathematically that the Universal IR can represent

    System G3b itself (The Autonomous Universal Systems Compiler) before any agent
    or emission logic is executed!
    """

    def test_represent_system_g3b_itself(self):
        # 1. Waterloo SoC of G3b itself
        g3b_soc = SituationOfConcern(
            soc_id="soc_system_g3b",
            title="The Autonomous Universal Systems Compiler Situation of Concern",
            narrative=(
                "Software systems engineering is compromised by simulated completions, "
                "hardcoded archetype templates, monolithic coupling, and greedy generation. "
                "Engineers require an authentic, reflexive software systems compiler that "
                "designs, architects, and compiles any software application or system—including "
                "reflexive systems with the exact same function as itself."
            ),
            altitude=SoCAltitude.MACRO,
            actors=[
                Actor(
                    name="Human System Architect",
                    role="Zero-Trust Overseer & Decision Authority",
                    motivations=["Autonomous system compilation", "Zero simulated completion"],
                    frustrations=["Cosmetic proxy assertions", "Monolithic coupling", "Greedy one-pass generation"],
                ),
                Actor(
                    name="Autonomous Meta-Orchestrator",
                    role="Deterministic FSM & Task Stack Supervisor",
                    motivations=["Mathematical invariant preservation", "Strict thermodynamic token accounting"],
                    frustrations=["Hallucinated reachability", "Unexecuted source files"],
                ),
            ],
            frictions=[
                Friction(
                    description="Simulated multi-agent execution masquerading as real recursion",
                    severity=FrictionSeverity.CRITICAL,
                    impact="Phantom code emissions that fail upon actual deployment",
                    trigger_conditions=["Unbounded generative code emission without physical test execution"],
                ),
                Friction(
                    description="Single-pass greedy synthesis suppressing necessary iterative failure",
                    severity=FrictionSeverity.HIGH,
                    impact="Local optima traps and brittle software designs",
                    trigger_conditions=["Monolithic LLM prompt-completion tunnels"],
                ),
            ],
            constraints=[
                EnvironmentalConstraint(
                    nature=ConstraintType.THERMODYNAMIC,
                    description="Option C 60/40 thermodynamic capital partition (360k exploratory / 240k protected)",
                    boundary_limit="Hard stop at 600,000 tokens with Landauer bit-erasure dissipation tracking",
                ),
                EnvironmentalConstraint(
                    nature=ConstraintType.TECHNICAL,
                    description="Anti-phantom physical emission and substrate execution witness ([NEG-G1B-001])",
                    boundary_limit="Python 3.14 exit code 0 and non-zero passing assertions",
                ),
            ],
            unmet_needs=[
                "Universal expressive domain spanning distributed topologies, rich statecharts, and compilers",
                "Quine daughter self-compilation capability",
                "Fail-fast micro-auditing on a fractal task stack",
            ],
        )

        certified_soc = SoCNormalizer.normalize_tier1(g3b_soc)
        self.assertEqual(certified_soc.soc_id, "soc_system_g3b")

        # 2. Hierarchical Statechart of G3b itself
        # Compound state: The Crucible
        crucible_substates = {
            "task_stack_pop": StateNode(
                id="crucible.task_stack_pop",
                node_type=StateNodeType.ATOMIC,
                transitions=[Transition(event="LEAF_TASK", target="crucible.leaf_subagent_transition")],
            ),
            "leaf_subagent_transition": StateNode(
                id="crucible.leaf_subagent_transition",
                node_type=StateNodeType.ATOMIC,
                transitions=[Transition(event="MICRO_AUDIT_REQUESTED", target="crucible.zero_trust_micro_audit")],
            ),
            "zero_trust_micro_audit": StateNode(
                id="crucible.zero_trust_micro_audit",
                node_type=StateNodeType.ATOMIC,
                transitions=[
                    Transition(event="AUDIT_SUCCESS", target="crucible.task_stack_pop"),
                    Transition(event="AUDIT_DEFECT", target="crucible.isolated_leaf_repair"),
                ],
            ),
            "isolated_leaf_repair": StateNode(
                id="crucible.isolated_leaf_repair",
                node_type=StateNodeType.ATOMIC,
                transitions=[Transition(event="REPAIRED", target="crucible.zero_trust_micro_audit")],
            ),
        }

        crucible_compound = StateNode(
            id="g3b_fsm.crucible",
            node_type=StateNodeType.COMPOUND,
            initial="task_stack_pop",
            states=crucible_substates,
            transitions=[Transition(event="ALL_LEAVES_VERIFIED", target="g3b_fsm.escrow_checkpoint")],
        )

        # Parallel Region: Real-Time Observability & Thermodynamics
        telemetry_stream = StateNode(
            id="observability.telemetry",
            node_type=StateNodeType.COMPOUND,
            initial="streaming",
            states={"streaming": StateNode(id="observability.telemetry.streaming", node_type=StateNodeType.ATOMIC)},
        )
        thermal_watchdog = StateNode(
            id="observability.watchdog",
            node_type=StateNodeType.COMPOUND,
            initial="monitoring",
            states={"monitoring": StateNode(id="observability.watchdog.monitoring", node_type=StateNodeType.ATOMIC)},
        )

        observability_parallel = StateNode(
            id="g3b_fsm.observability",
            node_type=StateNodeType.PARALLEL,
            states={"telemetry": telemetry_stream, "watchdog": thermal_watchdog},
        )

        g3b_root = StateNode(
            id="g3b_fsm",
            node_type=StateNodeType.COMPOUND,
            initial="soc_normalization",
            states={
                "soc_normalization": StateNode(
                    id="g3b_fsm.soc_normalization",
                    node_type=StateNodeType.ATOMIC,
                    transitions=[Transition(event="SOC_CERTIFIED", target="g3b_fsm.crucible")],
                ),
                "crucible": crucible_compound,
                "observability": observability_parallel,
                "escrow_checkpoint": StateNode(
                    id="g3b_fsm.escrow_checkpoint",
                    node_type=StateNodeType.ATOMIC,
                    transitions=[Transition(event="ESCROW_APPROVED", target="g3b_fsm.substrate_emission")],
                ),
                "substrate_emission": StateNode(
                    id="g3b_fsm.substrate_emission",
                    node_type=StateNodeType.ATOMIC,
                    transitions=[Transition(event="TESTS_PASS_EXIT_0", target="g3b_fsm.quine_certified")],
                ),
                "quine_certified": StateNode(id="g3b_fsm.quine_certified", node_type=StateNodeType.FINAL),
            },
        )

        g3b_statechart = StatechartIR(
            id="g3b_self_statechart",
            root=g3b_root,
            context_schema={
                "exploratory_tokens_spent": "int",
                "protected_tokens_spent": "int",
                "active_task_id": "str",
                "task_stack_depth": "int",
            },
            initial_context={
                "exploratory_tokens_spent": 0,
                "protected_tokens_spent": 0,
                "active_task_id": "root",
                "task_stack_depth": 1,
            },
        )

        statechart_errors = g3b_statechart.validate_integrity()
        self.assertEqual(statechart_errors, [], f"G3b Statechart errors: {statechart_errors}")

        # 3. Compositional Contract of G3b itself
        g3b_contract = ContractIR(
            contract_id="contract_g3b_self_compiler",
            title="System G3b Self-Compilation Contract",
            description="Formal contract governing System G3b reflexively compiling an identical daughter compiler.",
        )

        # Nouns
        g3b_contract.add_noun(DomainNoun(
            name="CompilerSourceManifest",
            description="Complete non-zero source manifest of System G3b.",
            fields=[
                FieldDef("file_paths", "list[str]"),
                FieldDef("total_physical_tokens", "int"),
            ],
            invariants=["len(file_paths) > 0", "total_physical_tokens > 1000"],
        ))

        g3b_contract.add_noun(DomainNoun(
            name="DaughterCompilerExecutionWitness",
            description="Substrate execution witness of the daughter compiler running a downstream test.",
            fields=[
                FieldDef("daughter_exit_code", "int"),
                FieldDef("downstream_app_verified", "bool"),
                FieldDef("witness_hash", "str"),
            ],
            invariants=["daughter_exit_code == 0", "downstream_app_verified == True"],
        ))

        # Parent Verb: ReflexiveSelfCompile
        reflexive_verb = DomainVerb(
            name="ReflexiveSelfCompile",
            description="Ingests G3b Waterloo SoC, generates G3b daughter compiler, runs daughter to compile downstream app.",
            pre_conditions=["soc_certified == True", "exploratory_capital >= 50000"],
            post_conditions=[
                "daughter_emitted == True",
                "daughter_booted_in_sandbox == True",
                "downstream_app_compiled == True",
            ],
            modifies_nouns=["CompilerSourceManifest", "DaughterCompilerExecutionWitness"],
        )

        # Child Subcontracts
        sub_synth = ContractIR(contract_id="sub_quine_synth", title="", description="")
        sub_synth.add_verb(DomainVerb(
            name="SynthesizeDaughterSource",
            description="",
            pre_conditions=["soc_certified == True"],
            post_conditions=["daughter_emitted == True"],
        ))

        sub_sandbox = ContractIR(contract_id="sub_quine_sandbox", title="", description="")
        sub_sandbox.add_verb(DomainVerb(
            name="BootDaughterInSandbox",
            description="",
            pre_conditions=["daughter_emitted == True"],
            post_conditions=["daughter_booted_in_sandbox == True"],
        ))

        sub_downstream = ContractIR(contract_id="sub_quine_downstream", title="", description="")
        sub_downstream.add_verb(DomainVerb(
            name="CompileDownstreamApp",
            description="",
            pre_conditions=["daughter_booted_in_sandbox == True"],
            post_conditions=["downstream_app_compiled == True"],
        ))

        g3b_contract.sub_contracts["sub_quine_synth"] = sub_synth
        g3b_contract.sub_contracts["sub_quine_sandbox"] = sub_sandbox
        g3b_contract.sub_contracts["sub_quine_downstream"] = sub_downstream

        g3b_contract.add_composed_verb(ComposedVerb(
            parent_verb=reflexive_verb,
            child_steps=[
                VerbCompositionStep("sub_quine_synth", "SynthesizeDaughterSource"),
                VerbCompositionStep("sub_quine_sandbox", "BootDaughterInSandbox"),
                VerbCompositionStep("sub_quine_downstream", "CompileDownstreamApp"),
            ],
        ))

        quine_witness = g3b_contract.verify_composition("ReflexiveSelfCompile")
        self.assertTrue(quine_witness.is_valid, f"Quine proof failed: {quine_witness.unresolved_obligations}")

        # Lossless JSON roundtripping of the Quine Contract
        reconstructed = ContractIR.from_json(g3b_contract.to_json())
        self.assertEqual(g3b_contract.to_dict(), reconstructed.to_dict())

        # Mathematical Proof Certification Succeeded!
        print(f"\n[QUINE CRUCIBLE CERTIFIED]: System G3b has mathematically represented its own architecture in Universal IR!")


if __name__ == "__main__":
    unittest.main()
