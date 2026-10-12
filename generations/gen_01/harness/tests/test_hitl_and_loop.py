"""Unit tests for the HITL controller and core bootstrapping execution loop."""

import asyncio
import pytest
from pathlib import Path
from meta_axioma.config import SystemConfig
from meta_axioma.hitl.intercept import HitlController
from meta_axioma.loop import AxiomBootstrapper
from meta_axioma.types import EpochTelemetry, HitlAction, HitlVerdict, NegativeAxiom


@pytest.mark.asyncio
async def test_bootstrapper_loop_step(tmp_path: Path):
    # Setup temporary markdown persistence
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

    # Custom async HITL callback that approves
    async def mock_hitl(telemetry: EpochTelemetry) -> HitlVerdict:
        return HitlVerdict(action=HitlAction.APPROVE, feedback="Test approved")

    hitl = HitlController(custom_callback=mock_hitl)
    bootstrapper = AxiomBootstrapper(config=config, hitl_controller=hitl)

    # Run Epoch 1
    telemetry = await bootstrapper.step_epoch()

    assert telemetry.epoch == 1
    assert telemetry.tri_fold_metrics is not None
    assert telemetry.tri_fold_metrics.aggregate_delta_e > 0
    assert "Committed" in telemetry.decision

    # Check persistence was updated
    assert "L1-001" in axioms_file.read_text(encoding="utf-8")
    assert "| `1` |" in arch_file.read_text(encoding="utf-8")


@pytest.mark.asyncio
async def test_hitl_veto_negative_axiom_injection(tmp_path: Path):
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

    # Custom async HITL callback that injects a negative axiom veto
    async def mock_veto(telemetry: EpochTelemetry) -> HitlVerdict:
        neg = NegativeAxiom(
            id="NEG-VETO-1",
            name="No Immutable Snapshots",
            forbidden_pattern="immutable snapshots",
            rationale="Testing human veto injection",
            injected_at_epoch=telemetry.epoch,
        )
        return HitlVerdict(
            action=HitlAction.INJECT_NEGATIVE_AXIOM,
            feedback="Vetoed by human operator",
            negative_axiom=neg,
        )

    hitl = HitlController(custom_callback=mock_veto)
    bootstrapper = AxiomBootstrapper(config=config, hitl_controller=hitl)

    telemetry = await bootstrapper.step_epoch()

    assert telemetry.epoch == 1
    assert "Vetoed" in telemetry.decision
    assert len(bootstrapper.engine.active_negative_axioms) == 1
    assert "NEG-VETO-1" in bootstrapper.engine.active_negative_axioms[0].id
