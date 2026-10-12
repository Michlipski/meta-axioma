"""Unit tests for the Two-Tiered Axiom Engine and The Jettison transition."""

import pytest
from meta_axioma.engine.engine import TwoTieredAxiomEngine
from meta_axioma.types import Axiom, AxiomLevel, AxiomStatus, NegativeAxiom, PhaseState


def test_axiom_tiers_and_counts():
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
    assert engine.count_active() == 2
    assert len(engine.level_0_epistemic) == 1
    assert len(engine.level_1_structural) == 1
    assert engine.phase == PhaseState.PHASE_1_META_EXPLORATION


def test_negative_axiom_veto_invariant():
    ax0 = Axiom(
        id="L0-001",
        level=AxiomLevel.LEVEL_0_EPISTEMIC,
        name="Compositionality",
        statement="Composable",
        formal_expression="f(a)",
        operational_rule="Decompose",
        status=AxiomStatus.ACTIVE,
    )
    engine = TwoTieredAxiomEngine(axioms=[ax0])

    neg = NegativeAxiom(
        id="NEG-001",
        name="Prohibit Global State",
        forbidden_pattern="global state",
        rationale="Eliminate side-effects",
        injected_at_epoch=1,
    )
    engine.inject_negative_axiom(neg)
    assert len(engine.active_negative_axioms) == 1

    bad_candidate = Axiom(
        id="L1-BAD",
        level=AxiomLevel.LEVEL_1_STRUCTURAL,
        name="Global Registry",
        statement="Introduce global state for shared variables",
        formal_expression="G = S",
        operational_rule="Share global state",
        status=AxiomStatus.CANDIDATE,
    )

    is_clean, reason = engine.check_negative_invariants(bad_candidate)
    assert not is_clean
    assert "NEG-001" in reason


def test_phase_transition_jettison():
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
    assert engine.phase == PhaseState.PHASE_1_META_EXPLORATION

    pruned_ids = engine.execute_jettison(epoch=3)
    assert pruned_ids == ["L0-001"]
    assert engine.phase == PhaseState.PHASE_2_STRUCTURAL_EXECUTION
    # L0 is pruned, only L1 remains active
    assert len(engine.level_0_epistemic) == 0
    assert len(engine.level_1_structural) == 1
    assert engine.count_active() == 1
