"""Adversarial Test & Byzantine QA Verification Suite (`soc_g4b_researcher`).

In accordance with [NEG-G1B-001] (Empirical Execution Witness & Anti-Phantom Emission Gate),
this suite executes comprehensive unit, integration, and chaos testing for Option C:
Zenith Apex Epistemic Crucible & Universal Research Substrate (soc_g4b_researcher).

Validates:
1. Waterloo SoC Normalization and domain noun instantiation across all 18 models.
2. Invariant bounds checking (pre/post-conditions, zero-code tool boundary, non-loopback network topology on 192.168.40.x).
3. 32-state hierarchical statechart traversal:
   - Happy path through epistemic_discovery -> adversarial_crucible -> protocol_adjudication.
   - Parallel orthogonal regions (concurrent_byzantine_fuzzer and landauer_thermodynamic_meter).
   - Deep history state checkpoints and restorations.
   - 4 Recovery enclaves (anti_shortcut_enclave, mode_collapse_enclave, rfc_counter_proof_enclave, unwind_recovery_enclave).
   - 1-tap Functorial Undo state and bit-reversal mechanics.
4. 5-Tier Anti-Bias Framework:
   - Zero-context island isolation test.
   - Graph taboo distance check (rejecting D < 0.40, accepting D >= 0.40).
   - Dialectical negation injection (NEG_PRIMITIVE).
   - Pareto frontier filtering and Lehman & Stanley novelty metric computation.
5. RFC Protocol Mediation:
   - Submission of SpecAdjustmentRequest.
   - Z3 SMT prover verification and counter-proof generation for invalid RFCs.
   - Signed SpecAmendment generation with cryptographic signature.
6. Merkle-DAG Cryptographic Witness Integrity:
   - Tamper detection (mutating a payload must invalidate parent and root Merkle hashes).
7. Landauer bit-erasure calculation and thermodynamic capital balance enforcement.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import sys
import unittest
from typing import Any, Dict, List

# Locate application root and add to sys.path
APP_ROOT = Path(__file__).resolve().parent.parent
CANDIDATE_PATHS = [
    APP_ROOT,
    APP_ROOT.parent.parent / "apps" / "soc_g4b_researcher",
    APP_ROOT / "downstream_app",
    APP_ROOT.parent.parent / "gen_03b" / "apps" / "soc_g4b_researcher",
]
for p in CANDIDATE_PATHS:
    if p.exists() and str(p) not in sys.path:
        sys.path.insert(0, str(p))

from src.domain_models import (
    BottleneckType,
    ByzantineFuzzVector,
    ConstraintAnalysis,
    DialecticalNegationSeed,
    DomainInvariantViolation,
    EmpiricalTelemetryReport,
    EpistemicCrucibleTarget,
    ExtremeBoundaryArchetype,
    FailureModeModel,
    FormalProofArtifact,
    FunctorialUndoCheckpoint,
    HypothesisDefinition,
    MerkleDagWitness,
    NoveltyArchiveEntry,
    ResearchDeliverableBundle,
    SolverResult,
    SpecAdjustmentRequest,
    SpecAmendment,
    StressDimension,
    TabooDistanceMatrix,
    TradeoffMatrix,
    ZeroContextIslandManifest,
)
from src.research_kernel import (
    ResearchKernelStateError,
    SovereignResearchKernel,
    ZeroCodeBoundaryViolation,
)
from src.island_manager import (
    ExplorationIsland,
    IslandBudgetExceededError,
    IslandQuarantineBreachError,
    ZeroContextIslandManager,
)
from src.dynamic_persona import (
    DynamicPersonaEngine,
    DynamicPersonaSpec,
)
from src.graph_taboo_engine import (
    GraphTabooEngine,
    ModeCollapseEnclaveTriggered,
    TabooDistanceViolation,
)
from src.inversion_engine import (
    DialecticalInversionEngine,
    NegatedPrimitiveViolation,
)
from src.boundary_stress_engine import (
    BoundaryStressEngine,
    BoundaryStressFailure,
)
from src.pareto_frontier import ParetoFrontierOptimizer
from src.z3_prover_bridge import Z3ProverBridge
from src.rfc_protocol_bus import (
    RFCProtocolBus,
    RFCValidationError,
)
from src.merkle_witness_engine import (
    MerkleIntegrityTamperFault,
    MerkleWitnessEngine,
)
from src.statechart_engine import (
    FunctorialUndoError,
    G4bStatechartEngine,
    StatechartTransitionError,
)
from src.auxiliary_hooks import (
    AuditVerificationHook,
    GovernanceSafetyHook,
    TelemetryEvaluationHook,
)


class TestG4bAdversarialAndByzantineQA(unittest.TestCase):
    """Exhaustive unit, integration, and chaos test suite for soc_g4b_researcher."""

    def setUp(self) -> None:
        self.valid_sha_a = hashlib.sha256(b"ARCH_REF_A").hexdigest()
        self.valid_sha_b = hashlib.sha256(b"MERKLE_ROOT_B").hexdigest()

    # =========================================================================
    # 1. Waterloo SoC Normalization & Domain Nouns (All 18 Models)
    # =========================================================================
    def test_01_all_18_domain_nouns_instantiation_and_validation(self) -> None:
        """Verifies instantiation and algebraic invariant validation for all 18 domain models."""
        # 1. ResearchDeliverableBundle
        m1 = ResearchDeliverableBundle(
            bundle_id="bundle_zenith_001",
            target_soc_id="soc_g4b_researcher",
            hypothesis_id="hyp_001",
            constraint_analysis_id="ca_001",
            failure_mode_id="fm_001",
            tradeoff_matrix_id="tm_001",
            reference_architecture_hash=self.valid_sha_a,
            merkle_root=self.valid_sha_b,
            is_certified=True,
        )
        m1.validate_invariants()
        self.assertEqual(m1.bundle_id, "bundle_zenith_001")

        # 2. HypothesisDefinition
        m2 = HypothesisDefinition(
            hypothesis_id="hyp_001",
            theoretical_claim="Decoupled P2P research substrate prevents cognitive contagion.",
            governing_axioms=["[L1-G4B-001]", "[L1-G3B-011]"],
            expected_complexity_class="O(log N)",
            formal_conjecture_z3="(assert (not (= island_A island_B)))",
        )
        m2.validate_invariants()
        self.assertEqual(m2.expected_complexity_class, "O(log N)")

        # 3. ConstraintAnalysis
        m3 = ConstraintAnalysis(
            analysis_id="ca_001",
            physical_latency_budget_ms=25,
            landauer_erasure_budget_bits=15000,
            topological_interfaces=["192.168.40.10:8201", "192.168.40.20:8202"],
            vetoed_negative_axioms=["[NEG-G1B-001] Anti-Phantom Gate"],
        )
        m3.validate_invariants()
        self.assertEqual(m3.physical_latency_budget_ms, 25)

        # 4. FailureModeModel
        m4 = FailureModeModel(
            model_id="fm_001",
            byzantine_vectors=["VECTOR_FORGED_SIGNATURE", "VECTOR_REPLAY_ATTACK"],
            partition_scenarios=["MICROBURST_PACKET_DROP_90"],
            deadlock_states=["STATE_CONSENSUS_STALL"],
            recovery_pipeline_urns=["urn:enclave:byzantine_recovery"],
        )
        m4.validate_invariants()
        self.assertEqual(len(m4.byzantine_vectors), 2)

        # 5. TradeoffMatrix
        m5 = TradeoffMatrix(
            matrix_id="tm_001",
            evaluated_options=["Option A: Decentralized P2P Mesh", "Option B: Sheaf Consensus"],
            pareto_frontier_options=["Option A: Decentralized P2P Mesh"],
            scoring_weights={"latency": 0.30, "bft": 0.40, "thermodynamics": 0.30},
            selection_proof="Option A satisfies Pareto optimality across all 5 dimensions.",
        )
        m5.validate_invariants()
        self.assertEqual(len(m5.pareto_frontier_options), 1)

        # 6. SpecAdjustmentRequest
        m6 = SpecAdjustmentRequest(
            request_id="rfc_req_001",
            builder_node_id="builder_node_primary",
            target_symbol_urn="urn:meta_axioma:g4b:contract:mesh_topology",
            bottleneck_type=BottleneckType.TOKEN_EXHAUSTION,
            empirical_evidence="Physical BPE lease depleted after 250k tokens.",
            proposed_delta="Lease additional 50k tokens from exploratory pool.",
            preserved_invariants=["[L1-012] Landauer Thermodynamic Bound", "[L1-002] Functorial Reversibility"],
        )
        m6.validate_invariants()
        self.assertEqual(m6.bottleneck_type, BottleneckType.TOKEN_EXHAUSTION)

        # 7. SpecAmendment
        m7 = SpecAmendment(
            amendment_id="amend_001",
            request_id="rfc_req_001",
            is_approved=True,
            adjudicator_signature=hashlib.sha256(b"SIG_ADJUDICATOR").hexdigest(),
            amended_contract_ir_delta="Granted 50,000 exploratory lease.",
        )
        m7.validate_invariants()
        self.assertTrue(m7.is_approved)

        # 8. TabooDistanceMatrix
        m8 = TabooDistanceMatrix(
            matrix_id="tdm_001",
            island_ids=["island_A", "island_B", "island_C"],
            distance_entries={"island_A:island_B": 0.52, "island_B:island_C": 0.61, "island_A:island_C": 0.48},
            min_distance_threshold=0.40,
        )
        m8.validate_invariants()
        self.assertEqual(len(m8.distance_entries), 3)

        # 9. MerkleDagWitness
        m9 = MerkleDagWitness(
            node_hash=self.valid_sha_a,
            parent_hashes=[self.valid_sha_b],
            task_id="task_research_01",
            actor_id="actor_brain_pro",
            payload_signature="sig_payload_001",
            timestamp_ns=1761273600000000000,
        )
        m9.validate_invariants()
        self.assertEqual(len(m9.node_hash), 64)

        # 10. EmpiricalTelemetryReport
        m10 = EmpiricalTelemetryReport(
            report_id="telemetry_rep_001",
            epoch_id="epoch_g4b_researcher",
            total_bpe_tokens_spent=145200,
            landauer_bits_erased=4200,
            landauer_heat_joules=1.206e-17,
            module_retry_counts={"kernel": 0, "statechart": 0},
            substrate_test_exit_code=0,
        )
        m10.validate_invariants()
        self.assertEqual(m10.substrate_test_exit_code, 0)

        # 11. EpistemicCrucibleTarget
        m11 = EpistemicCrucibleTarget(
            target_id="tgt_zenith_001",
            problem_statement="Synthesize autonomous universal research substrate with zero-code tool boundary.",
            waterloo_soc_urn="urn:waterloo:soc:g4b_researcher",
            exploratory_token_lease=589380,
            required_island_count=3,
        )
        m11.validate_invariants()
        self.assertGreaterEqual(m11.required_island_count, 3)

        # 12. ZeroContextIslandManifest
        m12 = ZeroContextIslandManifest(
            island_id="island_A_alpha",
            assigned_seed_entropy=hashlib.sha256(b"ENTROPY_ALPHA").hexdigest(),
            isolated_sandbox_path="/tmp/soc_g4b_islands/island_A",
            quarantine_token_budget=50000,
            generated_topology_hash=self.valid_sha_a,
        )
        m12.validate_invariants()
        self.assertEqual(len(m12.generated_topology_hash), 64)

        # 13. NoveltyArchiveEntry
        m13 = NoveltyArchiveEntry(
            archive_id="novelty_arc_001",
            topology_signature="topo_sig_ring_mesh",
            weisfeiler_lehman_hash=hashlib.sha256(b"WL_RING").hexdigest()[:16],
            behavioral_descriptor=[0.95, 0.90, 1.0, 0.85, 0.78],
            novelty_score=0.84,
        )
        m13.validate_invariants()
        self.assertGreaterEqual(len(m13.behavioral_descriptor), 3)

        # 14. DialecticalNegationSeed
        m14 = DialecticalNegationSeed(
            seed_id="neg_seed_001",
            default_primitive="CENTRALIZED_COORDINATOR",
            negated_invariant="NEG-PRIMITIVE-001: Centralized coordinator is strictly forbidden.",
            forced_alternative_archetype="Decentralized P2P gossip mesh with Sheaf-Quorum consensus.",
        )
        m14.validate_invariants()
        self.assertNotEqual(m14.default_primitive, m14.forced_alternative_archetype)

        # 15. ExtremeBoundaryArchetype
        m15 = ExtremeBoundaryArchetype(
            archetype_id="archetype_byzantine_33",
            stress_dimension=StressDimension.BYZANTINE_RATIO,
            stress_magnitude=0.33,
            adversarial_invariants=[
                "Supermajority (>= 2/3) valid confirmations required.",
                "Quarantine forged vector clocks.",
            ],
        )
        m15.validate_invariants()
        self.assertGreater(m15.stress_magnitude, 0.0)

        # 16. ByzantineFuzzVector
        m16 = ByzantineFuzzVector(
            vector_id="fuzz_vec_001",
            target_channel_id="chan_p2p_mesh",
            mutation_payload="FORGED_SIGNATURE:0xDEADBEEF",
            expected_trap_predicate="is_trapped == True",
            is_trapped=False,
        )
        m16.validate_invariants()
        self.assertTrue(bool(m16.target_channel_id))

        # 17. FormalProofArtifact
        m17 = FormalProofArtifact(
            proof_id="proof_morphism_001",
            contract_id="contract_epistemic_crucible",
            verb_morphism="ExecuteCampaignWorkflow",
            solver_engine="NativeSMTProver_v4b",
            solver_result=SolverResult.UNSAT,
            proof_tree_repr="Proof Tree: Validated pre/post conditions and domain invariants under Z3 axioms.",
        )
        m17.validate_invariants()
        self.assertEqual(m17.solver_result, SolverResult.UNSAT)

        # 18. FunctorialUndoCheckpoint
        m18 = FunctorialUndoCheckpoint(
            checkpoint_id="chk_undo_001",
            step_index=5,
            statechart_snapshot_hash=self.valid_sha_a,
            context_delta={"active_state": "hypothesis_formulation", "erased_bits": 512},
            erased_bits_to_revert=512,
        )
        m18.validate_invariants()
        self.assertEqual(len(m18.statechart_snapshot_hash), 64)

    def test_02_all_18_domain_nouns_serialization_roundtrip(self) -> None:
        """Verifies lossless to_dict / from_dict algebraic roundtripping for all 18 models."""
        models = [
            ResearchDeliverableBundle("b1", "s1", "h1", "c1", "f1", "t1", self.valid_sha_a, self.valid_sha_b, True),
            HypothesisDefinition("h1", "Substantive claim >= 20 chars", ["ax1"], "O(1)", "(conjecture)"),
            ConstraintAnalysis("c1", 25, 1000, ["192.168.40.10:8201"], ["NEG-001"]),
            FailureModeModel("f1", ["vec1", "vec2"], ["part1"], ["dead1"], ["rec1"]),
            TradeoffMatrix("t1", ["opt1"], ["opt1"], {"d1": 1.0}, "proof"),
            SpecAdjustmentRequest("r1", "b1", "urn:x", BottleneckType.LATENCY_OVERRUN, "evidence", "delta", ["inv1"]),
            SpecAmendment("a1", "r1", True, "sig", "delta"),
            TabooDistanceMatrix("tdm1", ["i1", "i2"], {"i1:i2": 0.45}, 0.40),
            MerkleDagWitness(self.valid_sha_a, [self.valid_sha_b], "t1", "a1", "sig", 1000),
            EmpiricalTelemetryReport("tr1", "e1", 100, 10, 1.0e-20, {}, 0),
            EpistemicCrucibleTarget("tgt1", "prob", "urn:soc", 20000, 3),
            ZeroContextIslandManifest("isl1", "seed", "/tmp/p", 1000, self.valid_sha_a),
            NoveltyArchiveEntry("na1", "sig", "wl", [1.0, 2.0, 3.0], 0.5),
            DialecticalNegationSeed("dns1", "P1", "neg", "P2"),
            ExtremeBoundaryArchetype("eba1", StressDimension.LATENCY, 10.0, ["inv"]),
            ByzantineFuzzVector("v1", "c1", "payload", "trap", False),
            FormalProofArtifact("p1", "c1", "m1", "solver", SolverResult.UNSAT, "tree"),
            FunctorialUndoCheckpoint("chk1", 1, self.valid_sha_a, {"k": "v"}, 64),
        ]

        classes = [
            ResearchDeliverableBundle, HypothesisDefinition, ConstraintAnalysis, FailureModeModel,
            TradeoffMatrix, SpecAdjustmentRequest, SpecAmendment, TabooDistanceMatrix,
            MerkleDagWitness, EmpiricalTelemetryReport, EpistemicCrucibleTarget, ZeroContextIslandManifest,
            NoveltyArchiveEntry, DialecticalNegationSeed, ExtremeBoundaryArchetype, ByzantineFuzzVector,
            FormalProofArtifact, FunctorialUndoCheckpoint,
        ]

        for m, cls in zip(models, classes):
            d = m.to_dict()
            restored = cls.from_dict(d)
            self.assertEqual(m.to_dict(), restored.to_dict())

    def test_03_domain_invariant_violations_trapped(self) -> None:
        """Verifies that invalid states raise DomainInvariantViolation across key models."""
        # Bundle with certified=True but invalid SHA length
        with self.assertRaises(DomainInvariantViolation):
            ResearchDeliverableBundle("b", "s", "h", "c", "f", "t", "short_hash", self.valid_sha_b, True).validate_invariants()

        # Rejected amendment without counter-proof
        with self.assertRaises(DomainInvariantViolation):
            SpecAmendment("a", "r", False, "sig", "delta", rejection_counter_proof=None).validate_invariants()

        # Taboo threshold below 0.40
        with self.assertRaises(DomainInvariantViolation):
            TabooDistanceMatrix("m", ["i1"], {}, min_distance_threshold=0.35).validate_invariants()

        # Taboo breach below threshold
        with self.assertRaises(DomainInvariantViolation):
            TabooDistanceMatrix("m", ["i1", "i2"], {"i1:i2": 0.25}, min_distance_threshold=0.40).validate_invariants()

        # Non-zero substrate test exit code ([NEG-G1B-001])
        with self.assertRaises(DomainInvariantViolation):
            EmpiricalTelemetryReport("r", "e", 100, 10, 1.0, {}, substrate_test_exit_code=1).validate_invariants()

        # Island count < 3
        with self.assertRaises(DomainInvariantViolation):
            EpistemicCrucibleTarget("t", "p", "urn", 20000, required_island_count=2).validate_invariants()

        # Identical negation primitive and alternative
        with self.assertRaises(DomainInvariantViolation):
            DialecticalNegationSeed("s", "PRIMITIVE_A", "neg", "PRIMITIVE_A").validate_invariants()

        # Negative step index in checkpoint
        with self.assertRaises(DomainInvariantViolation):
            FunctorialUndoCheckpoint("chk", -1, self.valid_sha_a, {}, 0).validate_invariants()

        # ConstraintAnalysis with loopback address
        with self.assertRaises(DomainInvariantViolation):
            ConstraintAnalysis("c_bad", 25, 1000, ["127.0.0.1:8201"], []).validate_invariants()

    # =========================================================================
    # 2. Invariant Bounds Checking, Zero-Code Boundary, Non-Loopback Topology
    # =========================================================================
    def test_04_pre_post_conditions_enforcement(self) -> None:
        """Verifies state machine and kernel pre-condition enforcement."""
        kernel = SovereignResearchKernel(node_ip="192.168.40.10")
        # Pre-condition: cannot formulate hypothesis before initializing campaign
        with self.assertRaises(ResearchKernelStateError):
            kernel.formulate_hypothesis(
                theoretical_claim="Premature substantive claim >= 20 chars",
                governing_axioms=["[L1-001]"],
                expected_complexity_class="O(1)",
                formal_conjecture_z3="(assert true)",
            )

        # Initialize campaign satisfies pre-condition
        target = EpistemicCrucibleTarget(
            target_id="tgt_init_001",
            problem_statement="Test campaign initialization",
            waterloo_soc_urn="urn:soc:test",
            exploratory_token_lease=25000,
            required_island_count=3,
        )
        kernel.initialize_campaign(target)
        hyp = kernel.formulate_hypothesis(
            theoretical_claim="Post-initialization substantive hypothesis >= 20 chars",
            governing_axioms=["[L1-001]"],
            expected_complexity_class="O(1)",
            formal_conjecture_z3="(assert true)",
        )
        self.assertIsNotNone(hyp.hypothesis_id)

    def test_05_zero_code_research_tool_boundary_enforcement(self) -> None:
        """Verifies [L1-G4B-002] Zero-Code Research Boundary: writing code is physically barred."""
        kernel = SovereignResearchKernel(node_ip="192.168.40.10")

        # Banned extensions: .py, .js, .ts, .html, .css, .sh, .c, .rs, .go
        banned_files = ["engine.py", "app.js", "bundle.ts", "ui.html", "style.css", "deploy.sh", "kernel.c", "mesh.rs"]
        for bf in banned_files:
            with self.assertRaises(ZeroCodeBoundaryViolation):
                kernel.enforce_zero_code_boundary(bf, "write")

        # Banned actions: write, execute, compile
        banned_actions = ["write", "execute", "compile"]
        for act in banned_actions:
            with self.assertRaises(ZeroCodeBoundaryViolation):
                kernel.enforce_zero_code_boundary("schema.json", act)

        # Permitted read-only schema inspection
        kernel.enforce_zero_code_boundary("schema.json", "read")
        kernel.enforce_zero_code_boundary("topology.json", "inspect")
        kernel.enforce_zero_code_boundary("contract.json", "evaluate")
        self.assertTrue(True)

    def test_06_non_loopback_network_topology_enforcement(self) -> None:
        """Verifies [L1-G3B-012] Anti-Loopback Invariant: no service or node may bind to loopback."""
        loopback_hosts = ["127.0.0.1", "localhost", "::1", "127.0.1.1"]

        for host in loopback_hosts:
            with self.assertRaises(DomainInvariantViolation):
                SovereignResearchKernel(node_ip=host)

            with self.assertRaises(DomainInvariantViolation):
                ZeroContextIslandManager(node_ip=host)

            with self.assertRaises(DomainInvariantViolation):
                RFCProtocolBus(node_ip=host)

        # Valid cluster subnet binding (192.168.40.0/24)
        k = SovereignResearchKernel(node_ip="192.168.40.10")
        im = ZeroContextIslandManager(node_ip="192.168.40.20")
        bus = RFCProtocolBus(node_ip="192.168.40.50")

        self.assertEqual(k.node_ip, "192.168.40.10")
        self.assertEqual(im.node_ip, "192.168.40.20")
        self.assertEqual(bus.node_ip, "192.168.40.50")

    def test_07_governance_safety_veto_enforcement(self) -> None:
        """Verifies human negative invariant vetoes (NEG-###) via GovernanceSafetyHook."""
        gov = GovernanceSafetyHook(human_architect="Michael Lipski")
        self.assertIn("[NEG-G1B-001] Anti-Phantom Emission Gate", gov.registered_vetoes)

        with self.assertRaises(DomainInvariantViolation):
            gov.verify_action_permitted("write_application_code", {})

        with self.assertRaises(DomainInvariantViolation):
            gov.verify_action_permitted("execute_build_pipeline", {})

        self.assertTrue(gov.verify_action_permitted("inspect_formal_proof", {}))

    # =========================================================================
    # 3. 32-State Hierarchical Statechart Traversal & 1-Tap Functorial Undo
    # =========================================================================
    def test_08_statechart_has_exactly_32_states(self) -> None:
        """Verifies that G4bStatechartEngine defines exactly 32 distinct state nodes."""
        self.assertEqual(len(G4bStatechartEngine.ALL_STATES), 32)

    def test_09_happy_path_statechart_traversal(self) -> None:
        """Executes full end-to-end happy path traversal through all 3 compound strata."""
        engine = G4bStatechartEngine()
        self.assertEqual(engine.active_state, "sovereign_init")

        # Stratum 1: epistemic_discovery
        engine.send("EV_SPAWN_ISLANDS", {"island_count": 3})
        self.assertEqual(engine.active_state, "island_quarantine")

        engine.send("EV_ISLANDS_SEEDED")
        self.assertEqual(engine.active_state, "hypothesis_formulation")

        engine.send("EV_HYPOTHESIS_FORMULATED")
        self.assertEqual(engine.active_state, "constraint_boundary_mapping")

        engine.send("EV_BOUNDARIES_MAPPED")
        self.assertEqual(engine.active_state, "discovery_evaluating")

        engine.send("EV_DISCOVERY_CERTIFIED")
        self.assertEqual(engine.active_state, "novelty_search_active")

        # Stratum 2: adversarial_crucible
        engine.send("EV_EVALUATE_NOVELTY")
        self.assertEqual(engine.active_state, "taboo_distance_check")

        # Taboo satisfied D >= 0.40
        engine.send("EV_TABOO_SATISFIED", {"taboo_distance": 0.58})
        self.assertEqual(engine.active_state, "dialectical_negation_inject")

        engine.send("EV_NEGATION_APPLIED")
        self.assertEqual(engine.active_state, "boundary_stress_fuzzing")

        engine.send("EV_STRESS_PASSED")
        self.assertEqual(engine.active_state, "pareto_frontier_filter")

        engine.send("EV_PARETO_OPTIMAL")
        self.assertEqual(engine.active_state, "crucible_certified")

        engine.send("EV_EMIT_DELIVERABLES")
        self.assertEqual(engine.active_state, "spec_bundle_published")

        # Stratum 3: protocol_adjudication
        engine.send("EV_BUILDER_ATTACHED")
        self.assertEqual(engine.active_state, "builder_rfc_ingress")

        engine.send("EV_SUBMIT_RFC")
        self.assertEqual(engine.active_state, "rfc_counter_proof_eval")

        engine.send("EV_AMENDMENT_PROVED")
        self.assertEqual(engine.active_state, "spec_amendment_signed")

        engine.send("EV_ALL_RFCS_RESOLVED")
        self.assertEqual(engine.active_state, "generational_handover_ready")

        engine.send("EV_SEAL_CRUCIBLE")
        self.assertEqual(engine.active_state, "epistemic_zenith_sealed")
        self.assertTrue(engine.context["is_sealed"])

    def test_10_parallel_orthogonal_regions_concurrency(self) -> None:
        """Verifies concurrent execution of the 2 orthogonal parallel regions (fuzzer and meter)."""
        engine = G4bStatechartEngine()

        # Verify initial parallel states
        self.assertEqual(engine.active_fuzzer_state, "fuzzer_quiescent")
        self.assertEqual(engine.active_meter_state, "meter_monitoring")

        # Step Parallel Region 1: concurrent_byzantine_fuzzer
        engine.send("EV_FUZZ_TICK")
        self.assertEqual(engine.active_fuzzer_state, "fuzzer_generating_vectors")

        engine.send("EV_VECTORS_DISPATCHED")
        self.assertEqual(engine.active_fuzzer_state, "fuzzer_evaluating_response")

        engine.send("EV_BYZANTINE_FAULT_CAUGHT")
        self.assertEqual(engine.active_fuzzer_state, "fuzzer_fault_trapped")

        engine.send("EV_FAULT_LOGGED")
        self.assertEqual(engine.active_fuzzer_state, "fuzzer_quiescent")

        # Step Parallel Region 2: landauer_thermodynamic_meter
        initial_bits = engine.context.get("erased_bits", 0)
        engine.send("EV_BIT_ERASURE_EVENT", {"bits": 256, "tokens": 100})
        self.assertEqual(engine.active_meter_state, "meter_bit_erasure_sample")
        self.assertEqual(engine.context["erased_bits"], initial_bits + 256)

        engine.send("EV_REBALANCE_CAPITAL")
        self.assertEqual(engine.active_meter_state, "meter_monitoring")

        # Verify primary stratum state remained unaffected
        self.assertEqual(engine.active_state, "sovereign_init")

    def test_11_deep_history_checkpoints_and_restorations(self) -> None:
        """Verifies deep history registers capture and preserve hierarchical substate context."""
        engine = G4bStatechartEngine()

        # Advance into hypothesis_formulation in Stratum 1
        engine.send("EV_SPAWN_ISLANDS")
        engine.send("EV_ISLANDS_SEEDED")
        self.assertEqual(engine.active_state, "hypothesis_formulation")

        # Deep history register updated
        engine.send("EV_HYPOTHESIS_FORMULATED")
        self.assertEqual(engine.history_registers["discovery_deep_history"], "hypothesis_formulation")

        # Advance to Stratum 2: novelty_search_active
        engine.send("EV_BOUNDARIES_MAPPED")
        engine.send("EV_DISCOVERY_CERTIFIED")
        self.assertEqual(engine.active_state, "novelty_search_active")

        engine.send("EV_EVALUATE_NOVELTY")
        self.assertEqual(engine.history_registers["crucible_deep_history"], "novelty_search_active")

    def test_12_four_dead_end_recovery_enclaves(self) -> None:
        """Verifies trapping and recovery across all 4 dead-end enclaves."""
        engine = G4bStatechartEngine()

        # 1. anti_shortcut_enclave
        engine.send("EV_SPAWN_ISLANDS")
        engine.send("EV_ISLANDS_SEEDED")
        engine.send("EV_HYPOTHESIS_FORMULATED")
        engine.send("EV_BOUNDARIES_MAPPED")
        self.assertEqual(engine.active_state, "discovery_evaluating")

        # Trap shortcut
        engine.send("EV_SHORTCUT_DETECTED")
        self.assertEqual(engine.active_state, "anti_shortcut_enclave")

        # Recover from shortcut
        engine.send("EV_UNWIND_SHORTCUT")
        self.assertEqual(engine.active_state, "hypothesis_formulation")

        # Advance to Stratum 2
        engine.send("EV_HYPOTHESIS_FORMULATED")
        engine.send("EV_BOUNDARIES_MAPPED")
        engine.send("EV_DISCOVERY_CERTIFIED")
        engine.send("EV_EVALUATE_NOVELTY")
        self.assertEqual(engine.active_state, "taboo_distance_check")

        # 2. mode_collapse_enclave: Triggered by taboo distance < 0.40
        engine.send("EV_TABOO_BREACH", {"taboo_distance": 0.22})
        self.assertEqual(engine.active_state, "mode_collapse_enclave")

        # Force dialectical negation recovery
        engine.send("EV_FORCE_NEGATION")
        self.assertEqual(engine.active_state, "dialectical_negation_inject")
        self.assertTrue(engine.context["negation_injected"])

        # Advance to Stratum 3
        engine.send("EV_NEGATION_APPLIED")
        engine.send("EV_STRESS_PASSED")
        engine.send("EV_PARETO_OPTIMAL")
        engine.send("EV_EMIT_DELIVERABLES")
        engine.send("EV_BUILDER_ATTACHED")
        engine.send("EV_SUBMIT_RFC")
        self.assertEqual(engine.active_state, "rfc_counter_proof_eval")

        # 3. rfc_counter_proof_enclave: Triggered by axiom violation in RFC
        engine.send("EV_AXIOM_VIOLATION")
        self.assertEqual(engine.active_state, "rfc_counter_proof_enclave")

        # Reject with proof returns to ingress
        engine.send("EV_REJECT_RFC_WITH_PROOF")
        self.assertEqual(engine.active_state, "builder_rfc_ingress")

        # 4. unwind_recovery_enclave: Triggered globally
        engine.send("EV_GLOBAL_UNWIND")
        self.assertEqual(engine.active_state, "unwind_recovery_enclave")

    def test_13_one_tap_functorial_undo_and_bit_reversal(self) -> None:
        """Verifies [L1-002] 1-Tap Functorial Undo: restores state snapshot and reclaims erased bits."""
        engine = G4bStatechartEngine()

        # Advance and create checkpoint
        engine.send("EV_SPAWN_ISLANDS", {"island_count": 3})
        engine.send("EV_ISLANDS_SEEDED")
        checkpoint = engine.create_checkpoint("chk_test_hypothesis")
        self.assertEqual(checkpoint.checkpoint_id, "chk_test_hypothesis")

        # Mutate state further and accumulate erased bits
        engine.send("EV_HYPOTHESIS_FORMULATED")
        engine.send("EV_BOUNDARIES_MAPPED")
        engine.send("EV_BIT_ERASURE_EVENT", {"bits": 1024, "tokens": 500})
        self.assertGreater(engine.context["erased_bits"], 0)

        # Execute 1-Tap Functorial Undo
        undo_res = engine.execute_functorial_undo("chk_test_hypothesis")
        self.assertEqual(undo_res["checkpoint_id"], "chk_test_hypothesis")
        self.assertEqual(undo_res["event"], "FUNCTORIAL_UNDO_EXECUTED")
        self.assertEqual(engine.context["erased_bits"], 0)

        # Invalid checkpoint ID raises FunctorialUndoError
        with self.assertRaises(FunctorialUndoError):
            engine.execute_functorial_undo("non_existent_chk")

    # =========================================================================
    # 4. 5-Tier Anti-Bias Framework
    # =========================================================================
    def test_14_tier1_zero_context_island_isolation(self) -> None:
        """Verifies Tier 1: Quarantined research islands execute with zero context leakage."""
        manager = ZeroContextIslandManager(node_ip="192.168.40.20")
        manager.spawn_islands(island_count=3, per_island_token_budget=20000)

        self.assertEqual(len(manager.islands), 3)
        # Verify zero cross-talk across distinct cryptographic entropy seeds
        self.assertTrue(manager.verify_zero_cross_talk())

        # Execute isolated exploration pass for island A
        island_a_id = list(manager.islands.keys())[0]
        manifest_a = manager.execute_island_exploration(
            island_id=island_a_id,
            node_names=["worker_0", "worker_1", "router_0"],
            channel_pairs=[("worker_0", "router_0"), ("worker_1", "router_0")],
        )
        self.assertEqual(manifest_a.island_id, island_a_id)
        self.assertEqual(len(manifest_a.generated_topology_hash), 64)

        # Verify per-island budget enforcement
        island = manager.islands[island_a_id]
        with self.assertRaises(IslandBudgetExceededError):
            island.spend_tokens(50000)  # Exceeds 20,000 budget

    def test_15_tier2_graph_taboo_distance_check(self) -> None:
        """Verifies Tier 2: Weisfeiler-Lehman graph taboo distance rejecting D < 0.40 and accepting D >= 0.40."""
        engine = GraphTabooEngine(min_distance_threshold=0.40, wl_iterations=2)

        topo_base = {
            "nodes": [{"node_id": "n1", "role": "WORKER"}, {"node_id": "n2", "role": "ROUTER"}],
            "edges": [{"source": "n1", "target": "n2"}],
        }

        # Structurally identical topology: D = 0.0 -> Must be rejected (D < 0.40)
        topo_identical = {
            "nodes": [{"node_id": "n1", "role": "WORKER"}, {"node_id": "n2", "role": "ROUTER"}],
            "edges": [{"source": "n1", "target": "n2"}],
        }

        dist_identical = engine.evaluate_pair(topo_base, topo_identical)
        self.assertLess(dist_identical, 0.40)
        with self.assertRaises(TabooDistanceViolation):
            engine.compute_taboo_matrix([topo_base, topo_identical], island_ids=["base", "identical"])

        # Highly diverse topology (mesh cluster with distinct roles)
        topo_diverse = {
            "nodes": [
                {"node_id": "a", "role": "SHEAF_VALIDATOR"},
                {"node_id": "b", "role": "BYZANTINE_MONITOR"},
                {"node_id": "c", "role": "ENCLAVE_GATEWAY"},
                {"node_id": "d", "role": "CRYPTO_ORACLE"},
            ],
            "edges": [
                {"source": "a", "target": "b"},
                {"source": "b", "target": "c"},
                {"source": "c", "target": "d"},
                {"source": "d", "target": "a"},
                {"source": "a", "target": "c"},
            ],
        }

        dist_diverse = engine.evaluate_pair(topo_base, topo_diverse)
        self.assertGreaterEqual(dist_diverse, 0.40)
        matrix = engine.compute_taboo_matrix([topo_base, topo_diverse], island_ids=["base", "diverse"])
        self.assertGreaterEqual(matrix.distance_entries["base:diverse"], 0.40)

    def test_16_tier3_dialectical_negation_injection(self) -> None:
        """Verifies Tier 3: NEG_PRIMITIVE injection and anti-bias architecture auditing."""
        engine = DialecticalInversionEngine()

        # Inject negation of CENTRALIZED_COORDINATOR
        seed = engine.inject_inversion("CENTRALIZED_COORDINATOR")
        self.assertEqual(seed.default_primitive, "CENTRALIZED_COORDINATOR")
        self.assertIn("NEG-PRIMITIVE-001", seed.negated_invariant)

        # Biased architecture containing banned centralized coordinator
        biased_arch = {
            "architecture_id": "biased_mesh",
            "nodes": [
                {"id": "coordinator_0", "role": "master_node"},
                {"id": "worker_0", "role": "worker"},
            ],
            "description": "Central broker coordinates all tasks",
        }
        violations = engine.audit_architecture_against_negations(biased_arch)
        self.assertGreaterEqual(len(violations), 1)

        # Inverted, sound decentralized architecture
        sound_arch = {
            "architecture_id": "sound_mesh",
            "nodes": [
                {"id": "peer_0", "role": "p2p_gossip_peer"},
                {"id": "peer_1", "role": "sheaf_quorum_peer"},
            ],
            "description": "Pure decentralized P2P gossip mesh",
        }
        clean_violations = engine.audit_architecture_against_negations(sound_arch)
        self.assertEqual(len(clean_violations), 0)

    def test_17_tier4_5d_pareto_frontier_filtering(self) -> None:
        """Verifies Tier 4: Multi-objective 5D Pareto vector optimization and non-dominated pruning."""
        optimizer = ParetoFrontierOptimizer(k_nearest_neighbors=2, novelty_threshold=0.20)

        # Pre-seed archive with an entry identical to candidate 2 so candidate 2 has zero novelty
        optimizer.novelty_archive.append(
            NoveltyArchiveEntry("na_seed", "sig_c2", "wl_c2", [0.50, 0.40, 0.37, 0.10], 0.0)
        )

        c1 = {
            "candidate_id": "cand_dominant",
            "invariant_coverage": 1.0,
            "byzantine_resilience": 0.95,
            "steps_to_value": 2,
            "landauer_bits_erased": 2000,
            "landauer_budget_bits": 20000,
            "behavioral_descriptor": [1.0, 0.95, 1.0, 0.90],
        }

        c2 = {
            "candidate_id": "cand_dominated",
            "invariant_coverage": 0.50,
            "byzantine_resilience": 0.40,
            "steps_to_value": 8,
            "landauer_bits_erased": 18000,
            "landauer_budget_bits": 20000,
            "behavioral_descriptor": [0.50, 0.40, 0.37, 0.10],
        }

        c3 = {
            "candidate_id": "cand_tradeoff",
            "invariant_coverage": 0.98,
            "byzantine_resilience": 0.99,
            "steps_to_value": 3,
            "landauer_bits_erased": 5000,
            "landauer_budget_bits": 20000,
            "behavioral_descriptor": [0.98, 0.99, 1.0, 0.75],
        }

        frontier = optimizer.filter_pareto_frontier([c1, c2, c3])
        frontier_ids = [c["candidate_id"] for c in frontier]

        self.assertIn("cand_dominant", frontier_ids)
        self.assertIn("cand_tradeoff", frontier_ids)
        # Dominated solution must be pruned
        self.assertNotIn("cand_dominated", frontier_ids)

    def test_18_tier5_lehman_stanley_novelty_metric_computation(self) -> None:
        """Verifies Tier 5: Lehman & Stanley (2011) k-NN novelty metric calculation."""
        optimizer = ParetoFrontierOptimizer(k_nearest_neighbors=2)

        # Seed archive with an entry
        optimizer.novelty_archive.append(
            NoveltyArchiveEntry("na1", "sig1", "wl1", [0.0, 0.0, 0.0], 1.0)
        )
        optimizer.novelty_archive.append(
            NoveltyArchiveEntry("na2", "sig2", "wl2", [0.1, 0.1, 0.1], 0.9)
        )

        # Distant candidate descriptor achieves high novelty
        distant_novelty = optimizer.compute_novelty_score([10.0, 10.0, 10.0])
        self.assertGreater(distant_novelty, 5.0)

        # Near-identical candidate descriptor achieves very low novelty
        close_novelty = optimizer.compute_novelty_score([0.05, 0.05, 0.05])
        self.assertLess(close_novelty, 0.5)

    # =========================================================================
    # 5. RFC Protocol Mediation & SMT Prover
    # =========================================================================
    def test_19_rfc_submission_and_validation(self) -> None:
        """Verifies builder RFC submission into RFCProtocolBus."""
        bus = RFCProtocolBus(node_ip="192.168.40.50")

        req = SpecAdjustmentRequest(
            request_id="rfc_test_001",
            builder_node_id="builder_01",
            target_symbol_urn="urn:service:p2p_mesh",
            bottleneck_type=BottleneckType.LATENCY_OVERRUN,
            empirical_evidence="Observed WAN roundtrip latency >= 150ms exceeding 25ms local budget.",
            proposed_delta="Adopt optimistic local commit with eventual sheaf reconciliation.",
            preserved_invariants=["[L1-002] Functorial Reversibility", "[L1-G3B-012] Non-Loopback Binding"],
        )

        rfc_id = bus.submit_rfc(req)
        self.assertEqual(rfc_id, "rfc_test_001")
        self.assertIn("rfc_test_001", bus.received_requests)

    def test_20_z3_smt_valid_contract_composition_proof(self) -> None:
        """Verifies Z3ProverBridge formally proves category-theoretic contract composition (UNSAT result)."""
        prover = Z3ProverBridge()

        parent_pre = ["input_validated == true", "node_online == true"]
        parent_post = ["workflow_completed == true", "state_persisted == true"]
        domain_inv = ["total_nodes >= 1"]

        steps = [
            {
                "child_verb_name": "Step1_Validate",
                "child_pre_conditions": ["input_validated == true"],
                "child_post_conditions": ["step1_passed == true"],
            },
            {
                "child_verb_name": "Step2_Process",
                "child_pre_conditions": ["step1_passed == true", "node_online == true"],
                "child_post_conditions": ["workflow_completed == true", "state_persisted == true"],
            },
        ]

        proof = prover.verify_contract_composition(
            contract_id="contract_test_proof",
            verb_name="ExecuteWorkflowMorphism",
            parent_pre_conditions=parent_pre,
            parent_post_conditions=parent_post,
            domain_invariants=domain_inv,
            steps=steps,
        )

        proof.validate_invariants()
        self.assertEqual(proof.solver_result, SolverResult.UNSAT)  # UNSAT of negation = proven valid
        self.assertIsNone(proof.counter_example)
        self.assertIn("Q.E.D.", proof.proof_tree_repr)

    def test_21_invalid_rfc_counter_proof_generation(self) -> None:
        """Verifies SMT prover counter-example synthesis and RFC counter-proof rejection."""
        prover = Z3ProverBridge()

        # Step 1 attempts to require a condition that is NOT in the knowledge base
        parent_pre = ["basic_auth == true"]
        parent_post = ["workflow_completed == true"]
        domain_inv = []

        unprovable_steps = [
            {
                "child_verb_name": "Step_Unsatisfied",
                "child_pre_conditions": ["super_admin_clearance == true"],  # Not provided!
                "child_post_conditions": ["workflow_completed == true"],
            }
        ]

        counter_proof = prover.verify_contract_composition(
            contract_id="contract_invalid",
            verb_name="InvalidMorphism",
            parent_pre_conditions=parent_pre,
            parent_post_conditions=parent_post,
            domain_invariants=domain_inv,
            steps=unprovable_steps,
        )

        counter_proof.validate_invariants()
        self.assertEqual(counter_proof.solver_result, SolverResult.SAT)  # SAT indicates counter-example found
        self.assertIsNotNone(counter_proof.counter_example)
        self.assertIn("super_admin_clearance", counter_proof.counter_example)

    def test_22_signed_spec_amendment_cryptographic_verification(self) -> None:
        """Verifies RFCProtocolBus emits signed SpecAmendment with valid cryptographic signature."""
        bus = RFCProtocolBus(node_ip="192.168.40.50")

        # 1. Approved RFC
        approved_req = SpecAdjustmentRequest(
            request_id="rfc_approve_001",
            builder_node_id="builder_01",
            target_symbol_urn="urn:service:mesh",
            bottleneck_type=BottleneckType.LATENCY_OVERRUN,
            empirical_evidence="Empirical evidence of WAN latency.",
            proposed_delta="Implement asynchronous message queuing.",
            preserved_invariants=["[L1-G3B-011] Universal Contract"],
        )
        bus.submit_rfc(approved_req)
        amendment = bus.adjudicate_rfc("rfc_approve_001")

        self.assertTrue(amendment.is_approved)
        self.assertEqual(len(amendment.adjudicator_signature), 64)
        self.assertIsNone(amendment.rejection_counter_proof)

        # 2. Rejected RFC attempting to inject loopback interface
        illegal_req = SpecAdjustmentRequest(
            request_id="rfc_illegal_002",
            builder_node_id="builder_02",
            target_symbol_urn="urn:service:network",
            bottleneck_type=BottleneckType.COMPLEXITY_LIMIT,
            empirical_evidence="Difficulty with multi-node cluster setup.",
            proposed_delta="Bypass verification and use loopback interface 127.0.0.1.",
            preserved_invariants=["none"],
        )
        bus.submit_rfc(illegal_req)
        rejection = bus.adjudicate_rfc("rfc_illegal_002")

        self.assertFalse(rejection.is_approved)
        self.assertIsNotNone(rejection.rejection_counter_proof)
        self.assertIn("COUNTER-PROOF", rejection.rejection_counter_proof)

    # =========================================================================
    # 6. Merkle-DAG Cryptographic Witness Integrity
    # =========================================================================
    def test_23_merkle_dag_construction_and_genesis_anchor(self) -> None:
        """Verifies genesis anchor and valid sequential Merkle DAG witness chaining."""
        engine = MerkleWitnessEngine(node_ip="192.168.40.60")
        self.assertTrue(engine.verify_dag_integrity())

        w1 = engine.record_witness("task_01", "actor_brain", {"event": "HYPOTHESIS_FORMULATED"})
        w2 = engine.record_witness("task_02", "actor_muscle", {"event": "FUZZ_VECTOR_EVALUATED"})
        w3 = engine.record_witness("task_03", "actor_adjudicator", {"event": "RFC_APPROVED"})

        self.assertEqual(len(engine.nodes), 4)  # Genesis + 3 witnesses
        self.assertTrue(engine.verify_dag_integrity())

    def test_24_merkle_dag_tamper_detection_leaf_mutation(self) -> None:
        """Verifies tamper detection: mutating payload data invalidates node hash and trips MerkleIntegrityTamperFault."""
        engine = MerkleWitnessEngine(node_ip="192.168.40.60")
        engine.record_witness("task_alpha", "actor_01", {"score": 0.95})
        w_beta = engine.record_witness("task_beta", "actor_02", {"verified": True})

        # DAG is clean
        self.assertTrue(engine.verify_dag_integrity())

        # Maliciously mutate payload signature of witness beta
        w_beta.payload_signature = hashlib.sha256(b"CORRUPTED_FORGED_PAYLOAD").hexdigest()

        with self.assertRaises(MerkleIntegrityTamperFault):
            engine.verify_dag_integrity()

    def test_25_merkle_dag_tamper_detection_parent_hash_mutation(self) -> None:
        """Verifies tamper detection: mutating parent hash breaks cryptographic DAG link."""
        engine = MerkleWitnessEngine(node_ip="192.168.40.60")
        engine.record_witness("task_01", "actor_01", {"step": 1})
        w2 = engine.record_witness("task_02", "actor_02", {"step": 2})

        self.assertTrue(engine.verify_dag_integrity())

        # Forged parent hash
        w2.parent_hashes = [hashlib.sha256(b"FORGED_PARENT").hexdigest()]

        with self.assertRaises(MerkleIntegrityTamperFault):
            engine.verify_dag_integrity()

    # =========================================================================
    # 7. Thermodynamics & Chaos Testing
    # =========================================================================
    def test_26_landauer_bit_erasure_and_heat_dissipation(self) -> None:
        """Verifies Landauer minimum theoretical heat dissipation Q = k_B * T * ln(2) * bits."""
        hook = TelemetryEvaluationHook(service_id="telemetry_test")

        k_b = 1.380649e-23
        t = 300.0  # Kelvin
        ln2 = 0.69314718056
        bits_erased = 10000

        expected_q = k_b * t * ln2 * bits_erased  # ~ 2.8718e-17 Joules

        sample = hook.record_thermodynamic_sample(
            bpe_tokens=5000,
            bits_erased=bits_erased,
            temperature_kelvin=t,
        )

        self.assertAlmostEqual(sample["heat_joules"], expected_q, places=22)
        self.assertEqual(sample["bits_erased"], 10000)

    def test_27_thermodynamic_capital_balance_enforcement(self) -> None:
        """Verifies 60% Exploratory Capital vs. 40% Protected Capital invariant partitioning."""
        total_unified_budget = 982300
        exploratory_ceiling = int(total_unified_budget * 0.60)  # 589,380
        protected_floor = int(total_unified_budget * 0.40)      # 392,920

        self.assertEqual(exploratory_ceiling, 589380)
        self.assertEqual(protected_floor, 392920)
        self.assertEqual(exploratory_ceiling + protected_floor, total_unified_budget)

        # Initialize statechart engine with exact calibrated budget
        engine = G4bStatechartEngine(initial_context={
            "exploratory_tokens_unspent": exploratory_ceiling,
            "protected_tokens_floor": protected_floor,
        })

        self.assertEqual(engine.context["exploratory_tokens_unspent"], 589380)
        self.assertEqual(engine.context["protected_tokens_floor"], 392920)

        # Deduct exploratory spend until near-exhaustion
        engine.send("EV_BIT_ERASURE_EVENT", {"bits": 500, "tokens": 589000})
        self.assertLess(engine.context["exploratory_tokens_unspent"], 1024)

        # Trigger rebalance: exploratory exhaustion trips meter_cutoff_tripped
        engine.send("EV_REBALANCE_CAPITAL")
        self.assertEqual(engine.active_meter_state, "meter_cutoff_tripped")

        # Protected capital floor must remain strictly untouched
        self.assertEqual(engine.context["protected_tokens_floor"], 392920)

    def test_28_byzantine_chaos_and_fuzz_vector_trapping(self) -> None:
        """Verifies Byzantine fuzz vectors design and recovery enclave trapping."""
        bse = BoundaryStressEngine()
        vectors = bse.generate_byzantine_fuzz_vectors(
            channel_ids=["p2p_channel_0", "consensus_channel_1"],
            vectors_per_channel=2,
        )

        self.assertEqual(len(vectors), 4)
        for v in vectors:
            v.validate_invariants()

        all_trapped, trap_ratio, untrapped = bse.dispatch_and_verify(vectors)
        self.assertTrue(all_trapped)
        self.assertEqual(trap_ratio, 1.0)
        self.assertEqual(len(untrapped), 0)
        self.assertEqual(len(bse.trapped_faults), 4)

    def test_29_extreme_boundary_stress_archetypes(self) -> None:
        """Verifies loading and validation of all 4 canonical extreme boundary stress archetypes."""
        bse = BoundaryStressEngine()
        archetypes = bse.load_canonical_archetypes()

        self.assertEqual(len(archetypes), 4)
        dim_set = {a.stress_dimension for a in archetypes}

        self.assertIn(StressDimension.PACKET_LOSS, dim_set)
        self.assertIn(StressDimension.BYZANTINE_RATIO, dim_set)
        self.assertIn(StressDimension.LATENCY, dim_set)
        self.assertIn(StressDimension.MEMORY_STARVATION, dim_set)

    def test_30_dialectical_red_team_persona_synthesis_and_validation(self) -> None:
        """Verifies [L1-G4B-009] & [INV-G4B-REDTEAM-001] Pre-Proposal Adversarial Red Team Persona."""
        engine = DynamicPersonaEngine()
        red_team = engine.create_dialectical_red_team_persona()
        self.assertEqual(red_team.role_id, "persona_dialectical_red_team")
        self.assertEqual(red_team.tier, "Brain")
        self.assertIn("[L1-G4B-009] Pre-Proposal Adversarial Review & Red Team Gate", red_team.governing_axioms)
        self.assertIn("[INV-G4B-REDTEAM-001] Adversarial Proposal Stress-Testing Invariant", red_team.governing_axioms)
        self.assertIn("Devil's Advocate Inversion", red_team.core_heuristics[0])
        self.assertTrue(len(red_team.banned_anti_patterns) >= 3)
        self.assertIn("Dialectical Red Team", red_team.system_prompt_scaffold)


if __name__ == "__main__":
    unittest.main()
