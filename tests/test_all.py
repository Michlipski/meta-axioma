"""Comprehensive test suite using standard library unittest for zero-dependency execution."""

import asyncio
import tempfile
import unittest
from pathlib import Path

from meta_axioma.config import SystemConfig
from meta_axioma.engine.engine import TwoTieredAxiomEngine
from meta_axioma.evaluator.evaluator import EfficacyEvaluator
from meta_axioma.hitl.intercept import HitlController
from meta_axioma.loop import AxiomBootstrapper
from meta_axioma.memory import PersistentMemoryManager
from meta_axioma.simulation.decay import ComputeDecayManager
from meta_axioma.simulation.lookahead import AxiomLookaheadEngine
from meta_axioma.simulation.sandbox import SimulationSandbox
from meta_axioma.types import (
    Axiom,
    AxiomLevel,
    AxiomStatus,
    ComputeBudget,
    EpochTelemetry,
    HitlAction,
    HitlVerdict,
    NegativeAxiom,
    PhaseState,
)


class TestAxiomEngine(unittest.TestCase):
    def test_tiers_and_counts(self):
        ax0 = Axiom(
            id="L0-001",
            level=AxiomLevel.LEVEL_0_EPISTEMIC,
            name="Compositionality",
            statement="Composable",
            formal_expression="f(a)",
            operational_rule="Decompose",
            status=AxiomStatus.ACTIVE,
        )
        ax1 = Axiom(
            id="L1-001",
            level=AxiomLevel.LEVEL_1_STRUCTURAL,
            name="Immutability",
            statement="Immutable state",
            formal_expression="s_t+1",
            operational_rule="No in-place mutation",
            status=AxiomStatus.ACTIVE,
        )
        engine = TwoTieredAxiomEngine(axioms=[ax0, ax1])
        self.assertEqual(engine.count_active(), 2)
        self.assertEqual(len(engine.level_0_epistemic), 1)
        self.assertEqual(len(engine.level_1_structural), 1)
        self.assertEqual(engine.phase, PhaseState.PHASE_1_META_EXPLORATION)

    def test_negative_axiom_veto(self):
        engine = TwoTieredAxiomEngine()
        neg = NegativeAxiom(
            id="NEG-001",
            name="No Global State",
            forbidden_pattern="global state",
            rationale="Eliminate side-effects",
            injected_at_epoch=1,
        )
        engine.inject_negative_axiom(neg)
        self.assertEqual(len(engine.active_negative_axioms), 1)

        candidate = Axiom(
            id="L1-FAIL",
            level=AxiomLevel.LEVEL_1_STRUCTURAL,
            name="Shared State",
            statement="Use global state across modules",
            formal_expression="G = S",
            operational_rule="Direct access",
            status=AxiomStatus.CANDIDATE,
        )
        is_clean, reason = engine.check_negative_invariants(candidate)
        self.assertFalse(is_clean)
        self.assertIn("NEG-001", reason)

    def test_the_jettison_transition(self):
        ax0 = Axiom(
            id="L0-001",
            level=AxiomLevel.LEVEL_0_EPISTEMIC,
            name="Compositionality",
            statement="Composable",
            formal_expression="f(a)",
            operational_rule="Decompose",
            status=AxiomStatus.ACTIVE,
        )
        ax1 = Axiom(
            id="L1-001",
            level=AxiomLevel.LEVEL_1_STRUCTURAL,
            name="Immutability",
            statement="Immutable",
            formal_expression="f(s)",
            operational_rule="Pure",
            status=AxiomStatus.ACTIVE,
        )
        engine = TwoTieredAxiomEngine(axioms=[ax0, ax1])
        pruned_ids = engine.execute_jettison(epoch=3)
        self.assertEqual(pruned_ids, ["L0-001"])
        self.assertEqual(engine.phase, PhaseState.PHASE_2_STRUCTURAL_EXECUTION)
        self.assertEqual(len(engine.level_0_epistemic), 0)
        self.assertEqual(len(engine.level_1_structural), 1)


class TestComputeDecay(unittest.TestCase):
    def test_inverse_decay_scaling(self):
        config = SystemConfig(
            base_token_budget=10000,
            base_simulation_depth=8,
            decay_alpha=0.5,
            min_token_budget=1000,
            min_simulation_depth=2,
        )
        manager = ComputeDecayManager(config)

        b1 = manager.calculate_budget(1)
        self.assertEqual(b1.token_budget, 10000)
        self.assertEqual(b1.simulation_depth, 8)

        b3 = manager.calculate_budget(3)
        self.assertEqual(b3.token_budget, 5000)
        self.assertEqual(b3.simulation_depth, 4)

        b10 = manager.calculate_budget(10)
        self.assertLess(b10.token_budget, b3.token_budget)
        self.assertGreaterEqual(b10.token_budget, config.min_token_budget)


class TestTriFoldSimulation(unittest.TestCase):
    def test_tri_fold_execution(self):
        config = SystemConfig()
        decay_mgr = ComputeDecayManager(config)
        sandbox = SimulationSandbox()
        evaluator = EfficacyEvaluator(config)

        budget = decay_mgr.calculate_budget(active_axiom_count=2)
        candidate = Axiom(
            id="L1-001",
            level=AxiomLevel.LEVEL_1_STRUCTURAL,
            name="Deterministic State Transitions and Immutability",
            statement="Every architectural state modification must occur via pure deterministic transitions operating over immutable snapshots.",
            formal_expression=r"S_{t+1} = \delta(S_t, a)",
            operational_rule="State mutations without complete lineage and snapshot isolation are rejected.",
            status=AxiomStatus.CANDIDATE,
        )

        results = sandbox.run_simulation(
            candidate=candidate,
            active_axioms=[],
            negative_axioms=[],
            budget=budget,
        )

        self.assertIn("target_1_self_constructor", results)
        self.assertIn("target_2_self_evaluator", results)
        self.assertIn("target_3_control_group", results)

        metrics = evaluator.evaluate_simulation(candidate, results)
        self.assertGreater(metrics.delta_e1, 0)
        self.assertGreater(metrics.delta_e2, 0)
        self.assertGreater(metrics.delta_e3, 0)
        self.assertGreater(metrics.aggregate_delta_e, 0)
        self.assertTrue(evaluator.is_strictly_improving(metrics))

    def test_level_0_epistemic_routing(self):
        config = SystemConfig()
        decay_mgr = ComputeDecayManager(config)
        sandbox = SimulationSandbox()
        evaluator = EfficacyEvaluator(config)

        budget = decay_mgr.calculate_budget(active_axiom_count=2)
        candidate = Axiom(
            id="L0-004",
            level=AxiomLevel.LEVEL_0_EPISTEMIC,
            name="Functorial Translation",
            statement="Map architectural problems across category categories.",
            formal_expression=r"F: \mathcal{C} \to \mathcal{D}",
            operational_rule="Synthesize cross-domain structural functors.",
            status=AxiomStatus.CANDIDATE,
        )

        results = sandbox.run_simulation(
            candidate=candidate,
            active_axioms=[],
            negative_axioms=[],
            budget=budget,
        )

        self.assertIn("target_e1_diversity", results)
        self.assertIn("target_e2_velocity", results)
        self.assertIn("target_e3_yield", results)
        self.assertNotIn("target_1_self_constructor", results)

        metrics = evaluator.evaluate_simulation(candidate, results)
        self.assertGreater(metrics.delta_e1, 0)
        self.assertGreater(metrics.delta_e2, 0)
        self.assertGreater(metrics.delta_e3, 0)
        self.assertGreater(metrics.aggregate_delta_e, 0)
        self.assertTrue(evaluator.is_strictly_improving(metrics))

    def test_jettison_deactivates_epistemic_targets(self):
        sandbox = SimulationSandbox()
        budget = ComputeBudget(
            active_axiom_count=3,
            token_budget=5000,
            simulation_depth=4,
            decay_factor=0.5,
        )

        l0_candidate = Axiom(
            id="L0-004",
            level=AxiomLevel.LEVEL_0_EPISTEMIC,
            name="Functorial Translation",
            statement="Cross-domain map",
            formal_expression="F: C -> D",
            operational_rule="Functor",
            status=AxiomStatus.CANDIDATE,
        )
        l1_candidate = Axiom(
            id="L1-002",
            level=AxiomLevel.LEVEL_1_STRUCTURAL,
            name="Immutable Store",
            statement="Immutable state store",
            formal_expression="S_t+1 = delta(S_t, a)",
            operational_rule="Pure store",
            status=AxiomStatus.CANDIDATE,
        )

        sandbox.jettison_epistemic_targets()
        self.assertTrue(sandbox.is_epistemic_jettisoned)

        # Level 0 must fail
        with self.assertRaises(RuntimeError):
            sandbox.run_simulation(
                candidate=l0_candidate,
                active_axioms=[],
                negative_axioms=[],
                budget=budget,
            )

        # Level 1 must succeed
        results = sandbox.run_simulation(
            candidate=l1_candidate,
            active_axioms=[],
            negative_axioms=[],
            budget=budget,
        )
        self.assertIn("target_1_self_constructor", results)


class TestBootstrapperLoop(unittest.IsolatedAsyncioTestCase):
    async def test_full_epoch_step_and_persistence(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            axioms_file = tmp_path / "AXIOMS.md"
            arch_file = tmp_path / "ARCHITECTURE.md"

            axioms_file.write_text(
                """# Active Axiom Registry
## Level 0: Meta / Epistemic Axioms
### [L0-001] Compositionality
- **Level:** Level 0 (Meta/Epistemic)
- **Status:** ACTIVE
- **Origin Epoch:** Epoch 0
- **Statement:** Composable
- **Formal Expression:** f(a)
- **Operational Rule:** Decompose
## Level 1: Structural Axioms
## Negative Axiom Invariant Registry
## Axiom Lifecycle Log
""",
                encoding="utf-8",
            )

            arch_file.write_text(
                """# Architectural State
**Current Epoch:** 0
**Phase:** `PHASE_1_META_EXPLORATION`
**Baseline Global Efficacy ($E$):** `1.000`
**Efficacy Derivative ($\\frac{dE}{dt}$):** `+0.000`

| Epoch | Active $n$ | Compute Budget $T(n)$ | $\\Delta E_1$ | $\\Delta E_2$ | $\\Delta E_3$ | Aggregate $\\Delta E$ | Phase | Action / Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `0` | 1 | 10,000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | Phase 1 | Initialized |
""",
                encoding="utf-8",
            )

            config = SystemConfig(
                axioms_path=axioms_file,
                architecture_path=arch_file,
                reports_dir=tmp_path / "reports",
            )
            bootstrapper = AxiomBootstrapper(config=config)

            telemetry = await bootstrapper.step_epoch()
            self.assertEqual(telemetry.epoch, 1)
            self.assertGreater(telemetry.tri_fold_metrics.aggregate_delta_e, 0)
            self.assertIn("Committed", telemetry.decision)

            # Verify files were updated
            ax_text = axioms_file.read_text(encoding="utf-8")
            self.assertIn(telemetry.candidate_axiom.id, ax_text)

            arch_text = arch_file.read_text(encoding="utf-8")
            self.assertIn("| `1` |", arch_text)

    async def test_hitl_veto_negative_axiom(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            axioms_file = tmp_path / "AXIOMS.md"
            arch_file = tmp_path / "ARCHITECTURE.md"

            axioms_file.write_text(
                """# Active Axiom Registry
## Level 0: Meta / Epistemic Axioms
### [L0-001] Compositionality
- **Level:** Level 0 (Meta/Epistemic)
- **Status:** ACTIVE
- **Origin Epoch:** Epoch 0
- **Statement:** Composable
- **Formal Expression:** f(a)
- **Operational Rule:** Decompose
## Level 1: Structural Axioms
## Negative Axiom Invariant Registry
## Axiom Lifecycle Log
""",
                encoding="utf-8",
            )

            arch_file.write_text(
                """# Architectural State
**Current Epoch:** 0
**Phase:** `PHASE_1_META_EXPLORATION`
**Baseline Global Efficacy ($E$):** `1.000`
**Efficacy Derivative ($\\frac{dE}{dt}$):** `+0.000`

| Epoch | Active $n$ | Compute Budget $T(n)$ | $\\Delta E_1$ | $\\Delta E_2$ | $\\Delta E_3$ | Aggregate $\\Delta E$ | Phase | Action / Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `0` | 1 | 10,000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | Phase 1 | Initialized |
""",
                encoding="utf-8",
            )

            config = SystemConfig(
                axioms_path=axioms_file,
                architecture_path=arch_file,
                reports_dir=tmp_path / "reports",
            )

            async def mock_veto(telemetry: EpochTelemetry) -> HitlVerdict:
                neg = NegativeAxiom(
                    id="NEG-VETO-1",
                    name="No Snapshots",
                    forbidden_pattern="immutable snapshots",
                    rationale="Testing human veto",
                    injected_at_epoch=telemetry.epoch,
                )
                return HitlVerdict(
                    action=HitlAction.INJECT_NEGATIVE_AXIOM,
                    feedback="Human vetoed",
                    negative_axiom=neg,
                )

            hitl = HitlController(custom_callback=mock_veto)
            bootstrapper = AxiomBootstrapper(config=config, hitl_controller=hitl)

            telemetry = await bootstrapper.step_epoch()
            self.assertEqual(telemetry.epoch, 1)
            self.assertIn("Vetoed", telemetry.decision)
            self.assertEqual(len(bootstrapper.engine.active_negative_axioms), 1)

    async def test_comparative_evaluation_user_seed(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            axioms_file = tmp_path / "AXIOMS.md"
            arch_file = tmp_path / "ARCHITECTURE.md"

            axioms_file.write_text(
                """# Active Axiom Registry
## Level 0: Meta / Epistemic Axioms
### [L0-001] Compositionality
- **Level:** Level 0 (Meta/Epistemic)
- **Status:** ACTIVE
- **Origin Epoch:** Epoch 0
- **Statement:** Composable
- **Formal Expression:** f(a)
- **Operational Rule:** Decompose
## Level 1: Structural Axioms
## Negative Axiom Invariant Registry
## Axiom Lifecycle Log
""",
                encoding="utf-8",
            )

            arch_file.write_text(
                """# Architectural State
**Current Epoch:** 0
**Phase:** `PHASE_1_META_EXPLORATION`
**Baseline Global Efficacy ($E$):** `1.000`
**Efficacy Derivative ($\\frac{dE}{dt}$):** `+0.000`

| Epoch | Active $n$ | Compute Budget $T(n)$ | $\\Delta E_1$ | $\\Delta E_2$ | $\\Delta E_3$ | Aggregate $\\Delta E$ | Phase | Action / Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `0` | 1 | 10,000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | Phase 1 | Initialized |
""",
                encoding="utf-8",
            )

            config = SystemConfig(
                axioms_path=axioms_file,
                architecture_path=arch_file,
                reports_dir=tmp_path / "reports",
            )

            # User candidate seed
            user_seed = Axiom(
                id="L1-USER-SEED",
                level=AxiomLevel.LEVEL_1_STRUCTURAL,
                name="Decoupled Observability & Explicit Interface Boundaries",
                statement="Decompose all telemetry into decoupled, observable streams across explicit interface boundaries.",
                formal_expression=r"\mathcal{O}(S) \perp \mathcal{T}(S)",
                operational_rule="Prohibit unobserved mutations across interface boundaries.",
                status=AxiomStatus.CANDIDATE,
            )

            async def mock_comparative_hitl(telemetry: EpochTelemetry) -> HitlVerdict:
                # Verify comparative telemetry was captured
                self.assertIsNotNone(telemetry.user_candidate)
                self.assertIsNotNone(telemetry.user_metrics)
                self.assertIsNotNone(telemetry.comparative_summary)
                # Human selects User Seed
                return HitlVerdict(action=HitlAction.APPROVE_USER, feedback="Selected User Seed")

            hitl = HitlController(custom_callback=mock_comparative_hitl)
            bootstrapper = AxiomBootstrapper(config=config, hitl_controller=hitl)

            telemetry = await bootstrapper.step_epoch(user_seed=user_seed)

            self.assertEqual(telemetry.epoch, 1)
            self.assertIn("Committed User Seed [L1-USER-SEED]", telemetry.decision)
            self.assertEqual(len(bootstrapper.engine.level_1_structural), 1)
            self.assertEqual(bootstrapper.engine.level_1_structural[0].id, "L1-USER-SEED")

            # Check persistence
            ax_text = axioms_file.read_text(encoding="utf-8")
            self.assertIn("L1-USER-SEED", ax_text)

    async def test_multi_candidate_tournament_autonomous_epoch(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            axioms_file = tmp_path / "AXIOMS.md"
            arch_file = tmp_path / "ARCHITECTURE.md"

            axioms_file.write_text(
                """# Active Axiom Registry
## Level 0: Meta / Epistemic Axioms
### [L0-001] Compositionality
- **Level:** Level 0 (Meta/Epistemic)
- **Status:** ACTIVE
- **Origin Epoch:** Epoch 0
- **Statement:** Composable
- **Formal Expression:** f(a)
- **Operational Rule:** Decompose
## Level 1: Structural Axioms
## Negative Axiom Invariant Registry
## Axiom Lifecycle Log
""",
                encoding="utf-8",
            )

            arch_file.write_text(
                """# Architectural State
**Current Epoch:** 0
**Phase:** `PHASE_1_META_EXPLORATION`
**Baseline Global Efficacy ($E$):** `1.000`
**Efficacy Derivative ($\\frac{dE}{dt}$):** `+0.000`

| Epoch | Active $n$ | Compute Budget $T(n)$ | $\\Delta E_1$ | $\\Delta E_2$ | $\\Delta E_3$ | Aggregate $\\Delta E$ | Phase | Action / Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `0` | 1 | 10,000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | Phase 1 | Initialized |
""",
                encoding="utf-8",
            )

            config = SystemConfig(
                axioms_path=axioms_file,
                architecture_path=arch_file,
                reports_dir=tmp_path / "reports",
                candidate_pool_size=3,
            )
            bootstrapper = AxiomBootstrapper(config=config)

            # Step autonomous epoch with pool size 3
            telemetry = await bootstrapper.step_epoch()

            self.assertEqual(telemetry.epoch, 1)
            self.assertIsNotNone(telemetry.candidate_pool)
            self.assertEqual(len(telemetry.candidate_pool), 3)
            self.assertIsNotNone(telemetry.tournament_leaderboard)
            self.assertEqual(len(telemetry.tournament_leaderboard), 3)

            # Top candidate was committed
            winner = telemetry.candidate_axiom
            self.assertIsNotNone(winner)
            self.assertIn("Committed Tournament Winner", telemetry.decision)
            self.assertGreater(telemetry.tri_fold_metrics.aggregate_delta_e, 0)

            # Verify winner is active in engine and other candidates were rejected
            self.assertEqual(bootstrapper.engine.count_active(), 2)  # L0-001 + Winner
            active_ids = {a.id for a in bootstrapper.engine.active_axioms}
            self.assertIn(winner.id, active_ids)


class TestAxiomLookaheadAndInactivity(unittest.TestCase):
    def test_jettison_transitions_to_inactive_scaffolding(self):
        ax0 = Axiom(
            id="L0-001",
            level=AxiomLevel.LEVEL_0_EPISTEMIC,
            name="Compositionality",
            statement="Composable",
            formal_expression="f(a)",
            operational_rule="Decompose",
            status=AxiomStatus.ACTIVE,
        )
        ax1 = Axiom(
            id="L1-001",
            level=AxiomLevel.LEVEL_1_STRUCTURAL,
            name="Immutability",
            statement="Immutable",
            formal_expression="f(s)",
            operational_rule="Pure",
            status=AxiomStatus.ACTIVE,
        )
        engine = TwoTieredAxiomEngine(axioms=[ax0, ax1])
        pruned_ids = engine.execute_jettison(epoch=10)

        # Verifications
        self.assertEqual(pruned_ids, ["L0-001"])
        self.assertEqual(engine.phase, PhaseState.PHASE_2_STRUCTURAL_EXECUTION)
        self.assertEqual(ax0.status, AxiomStatus.INACTIVE)
        self.assertEqual(ax0.metadata.get("jettisoned_at_epoch"), 10)
        self.assertEqual(len(engine.level_0_epistemic), 0)
        self.assertEqual(len(engine.level_0_inactive), 1)
        self.assertEqual(engine.count_active(), 1)
        self.assertIn(ax0.id, engine.axioms)  # Still in memory, NOT deleted!

    def test_lookahead_engine_speculation(self):
        config = SystemConfig(base_token_budget=10000, decay_alpha=0.5)
        engine = AxiomLookaheadEngine(config)

        # Create 10 active L0 epistemic axioms and 2 L1 structural axioms
        axioms = []
        for i in range(1, 11):
            axioms.append(
                Axiom(
                    id=f"L0-{i:03d}",
                    level=AxiomLevel.LEVEL_0_EPISTEMIC,
                    name=f"Meta Axiom {i}",
                    statement=f"Statement {i}",
                    formal_expression=f"E_{i}",
                    operational_rule=f"Rule {i}",
                    status=AxiomStatus.ACTIVE,
                )
            )
        for i in range(1, 3):
            axioms.append(
                Axiom(
                    id=f"L1-{i:03d}",
                    level=AxiomLevel.LEVEL_1_STRUCTURAL,
                    name=f"Structural Axiom {i}",
                    statement=f"Statement {i}",
                    formal_expression=f"S_{i}",
                    operational_rule=f"Rule {i}",
                    status=AxiomStatus.ACTIVE,
                )
            )

        candidate = Axiom(
            id="L1-003",
            level=AxiomLevel.LEVEL_1_STRUCTURAL,
            name="Content Addressed Merkle DAG",
            statement="Every artifact is immutable and content-addressed.",
            formal_expression="DAG = Merkle(S)",
            operational_rule="Verify hash before linking.",
            status=AxiomStatus.CANDIDATE,
        )

        res = engine.evaluate_lookahead(
            current_epoch=10,
            active_axioms=axioms,
            candidate_pool=[candidate],
            negative_axioms=[],
            horizon=2,
        )
        analysis = res.to_dict()

        self.assertIn("jettison_branch", analysis)
        self.assertIn("retain_branch", analysis)
        self.assertIn("recommendation", analysis)
        self.assertIn(analysis["recommendation"], ["RECOMMEND_JETTISON", "RECOMMEND_RETAIN", "INCONCLUSIVE"])
        self.assertGreater(analysis["compute_dividend_tokens"], 0)
        self.assertGreater(analysis["compute_dividend_depth"], 0)
        self.assertEqual(analysis["jettison_branch"]["active_axiom_count"], 2)
        self.assertEqual(analysis["retain_branch"]["active_axiom_count"], 12)

    def test_memory_preserves_inactive_section(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            axioms_file = tmp_path / "AXIOMS.md"

            mem = PersistentMemoryManager(
                axioms_path=axioms_file,
                architecture_path=tmp_path / "ARCHITECTURE.md",
            )

            ax_active = Axiom(
                id="L1-001",
                level=AxiomLevel.LEVEL_1_STRUCTURAL,
                name="Structural Rule",
                statement="State is pure",
                formal_expression="S_1",
                operational_rule="Enforce pure state",
                status=AxiomStatus.ACTIVE,
            )
            ax_inactive = Axiom(
                id="L0-001",
                level=AxiomLevel.LEVEL_0_EPISTEMIC,
                name="Epistemic Meta Rule",
                statement="Guide search space",
                formal_expression="E_1",
                operational_rule="Filter ungrounded axioms",
                status=AxiomStatus.INACTIVE,
                metadata={"jettisoned_at_epoch": 10},
            )

            mem.sync_axioms_file([ax_active, ax_inactive], [])
            content = axioms_file.read_text(encoding="utf-8")
            self.assertIn("Inactive Level 0 (Archived Scaffolding)", content)
            self.assertIn("- **Status:** INACTIVE", content)
            self.assertIn("L0-001", content)
            self.assertIn("L1-001", content)

            loaded_axioms, _ = mem.load_axioms()
            self.assertEqual(len(loaded_axioms), 2)
            inactive_loaded = [a for a in loaded_axioms if a.status == AxiomStatus.INACTIVE]
            self.assertEqual(len(inactive_loaded), 1)
            self.assertEqual(inactive_loaded[0].id, "L0-001")

    def test_epistemic_scaffolding_guides_structural_generation(self):
        from meta_axioma.engine.generator import AxiomPromptGenerator

        generator = AxiomPromptGenerator()
        l0_scaffold = [
            Axiom(
                id="L0-003",
                level=AxiomLevel.LEVEL_0_EPISTEMIC,
                name="The Axiom of Exogenous Orthogonality",
                statement="Synthesize principles from non-computing domains",
                formal_expression=r"\mathcal{H} = \mathcal{T}(\mathcal{P})",
                operational_rule="Select a non-computing domain and extract core structural principle",
                status=AxiomStatus.INACTIVE,
            )
        ]
        l1_active = [
            Axiom(
                id="L1-002",
                level=AxiomLevel.LEVEL_1_STRUCTURAL,
                name="Functorial State Evolution",
                statement="Structure preserving functor",
                formal_expression="F(f o g) = F(f) o F(g)",
                operational_rule="Morphism preservation",
                status=AxiomStatus.ACTIVE,
            )
        ]

        # Phase 2: level_0_axioms is empty (active set has 0 L0), but epistemic_scaffolding has L0-003
        prompt = generator.build_discovery_prompt(
            epoch=12,
            phase=PhaseState.PHASE_2_STRUCTURAL_EXECUTION,
            level_0_axioms=[],
            level_1_axioms=l1_active,
            negative_axioms=[],
            compute_tokens=5000,
            epistemic_scaffolding=l0_scaffold,
        )

        self.assertIn("Established Epistemic Scaffolding", prompt)
        self.assertIn("L0-003", prompt)
        self.assertIn("EXOGENOUS SYNTHESIS CONSTRAINT (Governed by L0-003)", prompt)
        self.assertIn("non-computing domain", prompt)

        # Batch generation with epistemic scaffolding
        batch = generator.generate_candidate_batch(
            count=3,
            epoch=12,
            phase=PhaseState.PHASE_2_STRUCTURAL_EXECUTION,
            level_0_axioms=[],
            level_1_axioms=l1_active,
            negative_axioms=[],
            epistemic_scaffolding=l0_scaffold,
        )
        self.assertEqual(len(batch), 3)
        for cand in batch:
            self.assertEqual(cand.level, AxiomLevel.LEVEL_1_STRUCTURAL)
            self.assertIn("exogenous_domain", cand.metadata)


class TestGenerationalArchitecture(unittest.TestCase):
    def test_generational_config_defaults(self):
        config = SystemConfig()
        self.assertEqual(config.active_generation, "gen_01")
        self.assertTrue(str(config.reports_dir).endswith("generations/gen_01/epochs"))
        self.assertTrue(str(config.generations_dir).endswith("generations"))

    def test_generational_directories_exist(self):
        config = SystemConfig()
        gen01_dir = config.generations_dir / "gen_01"
        self.assertTrue(gen01_dir.exists())
        self.assertTrue((gen01_dir / "epochs").exists())
        self.assertTrue((gen01_dir / "epochs" / "data").exists())
        self.assertTrue((gen01_dir / "summary.md").exists())
        self.assertTrue((config.root_dir / "generation_01_summary.md").exists())
        self.assertTrue((config.root_dir / "generation_01_architecture.md").exists())
        self.assertTrue((config.root_dir / "generation_01_axioms.md").exists())
        self.assertTrue((config.root_dir / "overview.md").exists())
        self.assertTrue((config.root_dir / "stack.md").exists())
        self.assertTrue((config.root_dir / "trace" / "overview.md").exists())


class TestProductUsabilityAndEnclave(unittest.TestCase):
    def test_product_usability_target_simulation(self):
        from meta_axioma.targets.product_usability import ProductUsabilityTarget
        target = ProductUsabilityTarget()
        ax = Axiom(
            id="L1-TEST",
            level=AxiomLevel.LEVEL_1_STRUCTURAL,
            name="Test User Experience Flow",
            statement="Clear affordances, graceful error recovery, and persona goal completion.",
            formal_expression="Flow(u) -> Goal",
            operational_rule="Provide humane feedback and low cognitive friction.",
            status=AxiomStatus.CANDIDATE,
        )
        budget = ComputeBudget(active_axiom_count=4, token_budget=4000, simulation_depth=3, decay_factor=0.4)
        res = target.simulate_compilation(candidate=ax, active_axioms=[], negative_axioms=[], budget=budget)
        self.assertTrue(res.compilation_success)
        self.assertGreater(res.raw_delta_e, 0.0)
        self.assertTrue(res.telemetry_details["error_gracefulness"])

    def test_l1_016_candidate_presence(self):
        from meta_axioma.engine.generator import LEVEL_1_STRUCTURAL_CANDIDATE_POOL
        l1_016 = next((a for a in LEVEL_1_STRUCTURAL_CANDIDATE_POOL if a.id == "L1-016"), None)
        self.assertIsNotNone(l1_016)
        self.assertIn("Enclave", l1_016.name)
        self.assertIn("unsafe", l1_016.metadata["exogenous_domain"])


class TestSystemG1Integration(unittest.TestCase):
    def test_g1_compiler_all_structural_axioms_verified(self):
        import sys
        g1_src = str(Path(__file__).parent.parent / "generations" / "gen_01" / "src")
        if g1_src not in sys.path:
            sys.path.insert(0, g1_src)
        from g1_compiler import SystemG1Compiler
        compiler = SystemG1Compiler()
        results = compiler.verify_all_structural_axioms()
        self.assertEqual(len(results), 9)
        for ax_id, res in results.items():
            self.assertTrue(res.passed, f"G1 Invariant {ax_id} failed: {res.message}")

    def test_g1_compiler_generates_g2_successor_basis(self):
        import sys
        g1_src = str(Path(__file__).parent.parent / "generations" / "gen_01" / "src")
        if g1_src not in sys.path:
            sys.path.insert(0, g1_src)
        from g1_compiler import SystemG1Compiler
        compiler = SystemG1Compiler()
        g2_basis = compiler.generate_g2_basis()
        self.assertEqual(g2_basis.generation, 2)
        self.assertGreaterEqual(len(g2_basis.targets), 4)
        self.assertIsNotNone(g2_basis.inherited_feedback_dossier)
        self.assertIsNotNone(g2_basis.search_trace)
        self.assertIsNotNone(g2_basis.succession_certificate)
        self.assertTrue(any("NEG-G2-001" in c for c in g2_basis.inherited_negative_constraints))
        self.assertTrue(any("LES-G1-001" in s for s in g2_basis.lessons_learned_summary))
        self.assertTrue(any(ax.id == "L1-G2-005" for ax in g2_basis.basis_axioms))
        self.assertTrue(any(ax.id == "L1-G2-006" for ax in g2_basis.basis_axioms))
    def test_standardized_apps_registry_and_layout(self):
        import sys
        g1_src = str(Path(__file__).parent.parent / "generations" / "gen_01" / "src")
        if g1_src not in sys.path:
            sys.path.insert(0, g1_src)
        from g1_compiler import ApplicationCompiler
        root = Path(__file__).parent.parent
        self.assertTrue((root / "apps" / "README.md").exists())
        self.assertTrue((root / "apps" / "axioma_flow").exists())
        self.assertTrue((root / "apps" / "axioma_lexis").exists())
        self.assertTrue((root / "apps" / "axioma_dual_fsm").exists())
        self.assertTrue((root / "apps" / "axioma_crossword").exists())
        self.assertTrue((root / "apps" / "axioma_eink").exists())
        self.assertTrue((root / "apps" / "axioma_swarm").exists())
        self.assertTrue((root / "trace" / "domains" / "app_specification.domain.md").exists())

        app_flow_path = root / "generations" / "gen_01" / "apps" / "axioma_flow"
        validation_flow = ApplicationCompiler.validate_app_layout(app_flow_path)
        self.assertTrue(validation_flow["is_standard_compliant"], f"Axioma Flow layout failed: {validation_flow['file_checks']}")

        app_lexis_path = root / "generations" / "gen_01" / "apps" / "axioma_lexis"
        validation_lexis = ApplicationCompiler.validate_app_layout(app_lexis_path)
        self.assertTrue(validation_lexis["is_standard_compliant"], f"Axioma Lexis layout failed: {validation_lexis['file_checks']}")

        app_fsm_path = root / "generations" / "gen_01" / "apps" / "axioma_dual_fsm"
        validation_fsm = ApplicationCompiler.validate_app_layout(app_fsm_path)
        self.assertTrue(validation_fsm["is_standard_compliant"], f"Axioma Dual FSM layout failed: {validation_fsm['file_checks']}")

        app_cw_path = root / "generations" / "gen_01" / "apps" / "axioma_crossword"
        validation_cw = ApplicationCompiler.validate_app_layout(app_cw_path)
        self.assertTrue(validation_cw["is_standard_compliant"], f"Axioma Crossword layout failed: {validation_cw['file_checks']}")

        app_eink_path = root / "generations" / "gen_01" / "apps" / "axioma_eink"
        validation_eink = ApplicationCompiler.validate_app_layout(app_eink_path)
        self.assertTrue(validation_eink["is_standard_compliant"], f"Axioma E-Ink layout failed: {validation_eink['file_checks']}")

        app_swarm_path = root / "generations" / "gen_01" / "apps" / "axioma_swarm"
        validation_swarm = ApplicationCompiler.validate_app_layout(app_swarm_path)
        self.assertTrue(validation_swarm["is_standard_compliant"], f"Axioma Swarm layout failed: {validation_swarm['file_checks']}")


if __name__ == "__main__":
    unittest.main()


