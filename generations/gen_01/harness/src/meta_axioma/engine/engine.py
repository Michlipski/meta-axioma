"""Two-Tiered Axiom Engine: Level 0 (Epistemic) and Level 1 (Structural) management."""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple
from meta_axioma.types import Axiom, AxiomLevel, AxiomStatus, NegativeAxiom, PhaseState


class TwoTieredAxiomEngine:
    """Manages the two tiers of axioms, negative invariant vetoes, and phase transition pruning."""

    def __init__(
        self,
        axioms: Optional[List[Axiom]] = None,
        negative_axioms: Optional[List[NegativeAxiom]] = None,
        initial_phase: PhaseState = PhaseState.PHASE_1_META_EXPLORATION,
    ):
        self.axioms: Dict[str, Axiom] = {}
        self.negative_axioms: Dict[str, NegativeAxiom] = {}
        self.phase: PhaseState = initial_phase
        self.lifecycle_logs: List[dict] = []

        if axioms:
            for ax in axioms:
                self.axioms[ax.id] = ax
                self.lifecycle_logs.append({
                    "id": ax.id,
                    "level": ax.level.value,
                    "name": ax.name,
                    "epoch": ax.origin_epoch,
                    "action": "Loaded",
                    "delta_e": ax.delta_e,
                    "status": ax.status.value,
                })

        if negative_axioms:
            for neg in negative_axioms:
                self.negative_axioms[neg.id] = neg

    @property
    def active_axioms(self) -> List[Axiom]:
        """Returns all currently active axioms."""
        return [a for a in self.axioms.values() if a.status == AxiomStatus.ACTIVE]

    @property
    def level_0_epistemic(self) -> List[Axiom]:
        """Returns active Level 0 Epistemic axioms."""
        return [
            a
            for a in self.active_axioms
            if a.level == AxiomLevel.LEVEL_0_EPISTEMIC
        ]

    @property
    def level_1_structural(self) -> List[Axiom]:
        """Returns active Level 1 Structural axioms."""
        return [
            a
            for a in self.active_axioms
            if a.level == AxiomLevel.LEVEL_1_STRUCTURAL
        ]

    @property
    def active_negative_axioms(self) -> List[NegativeAxiom]:
        """Returns active human-injected veto invariants."""
        return [n for n in self.negative_axioms.values() if n.is_active]

    def count_active(self) -> int:
        """Returns total count of active axioms n."""
        return len(self.active_axioms)

    def check_negative_invariants(self, candidate: Axiom) -> Tuple[bool, Optional[str]]:
        """Verifies candidate does not violate any negative axiom."""
        search_space = f"{candidate.name} {candidate.statement} {candidate.operational_rule}".lower()
        for neg in self.active_negative_axioms:
            if neg.forbidden_pattern.lower() in search_space:
                return False, f"Violated Negative Axiom [{neg.id}]: {neg.forbidden_pattern}"
        return True, None

    def commit_axiom(self, axiom: Axiom, epoch: int, delta_e: float) -> None:
        """Commits a candidate axiom to active state."""
        axiom.status = AxiomStatus.ACTIVE
        axiom.origin_epoch = epoch
        axiom.delta_e = delta_e
        self.axioms[axiom.id] = axiom

        self.lifecycle_logs.append({
            "id": axiom.id,
            "level": axiom.level.value,
            "name": axiom.name,
            "epoch": epoch,
            "action": "Committed",
            "delta_e": delta_e,
            "status": AxiomStatus.ACTIVE.value,
        })

    def reject_axiom(self, axiom: Axiom, epoch: int, delta_e: float, reason: str = "Delta E <= 0") -> None:
        """Rejects a candidate axiom."""
        axiom.status = AxiomStatus.REJECTED
        axiom.origin_epoch = epoch
        axiom.delta_e = delta_e
        self.axioms[axiom.id] = axiom

        self.lifecycle_logs.append({
            "id": axiom.id,
            "level": axiom.level.value,
            "name": axiom.name,
            "epoch": epoch,
            "action": f"Rejected ({reason})",
            "delta_e": delta_e,
            "status": AxiomStatus.REJECTED.value,
        })

    def veto_axiom(self, axiom: Axiom, epoch: int, reason: str) -> None:
        """Marks candidate as vetoed by human intervention."""
        axiom.status = AxiomStatus.VETOED
        axiom.origin_epoch = epoch
        self.axioms[axiom.id] = axiom

        self.lifecycle_logs.append({
            "id": axiom.id,
            "level": axiom.level.value,
            "name": axiom.name,
            "epoch": epoch,
            "action": f"Vetoed ({reason})",
            "delta_e": axiom.delta_e,
            "status": AxiomStatus.VETOED.value,
        })

    @property
    def level_0_inactive(self) -> List[Axiom]:
        """Returns Level 0 Epistemic axioms retained as inactive scaffolding post-jettison."""
        return [
            a
            for a in self.axioms.values()
            if a.level == AxiomLevel.LEVEL_0_EPISTEMIC
            and a.status in (AxiomStatus.INACTIVE, AxiomStatus.PRUNED)
        ]

    @property
    def all_level_0_axioms(self) -> List[Axiom]:
        """Returns all Level 0 Epistemic axioms (both active and inactive scaffolding) representing the complete epistemic lineage."""
        return [
            a
            for a in self.axioms.values()
            if a.level == AxiomLevel.LEVEL_0_EPISTEMIC
            and a.status in (AxiomStatus.ACTIVE, AxiomStatus.INACTIVE, AxiomStatus.PRUNED)
        ]

    def inject_negative_axiom(self, neg_axiom: NegativeAxiom) -> None:
        """Adds a human veto invariant to the active negative registry."""
        self.negative_axioms[neg_axiom.id] = neg_axiom

    def execute_jettison(self, epoch: int) -> List[str]:
        """Phase Transition: Retain all Level 0 Epistemic axioms in registry as INACTIVE scaffolding."""
        deactivated_ids: List[str] = []
        for ax in list(self.axioms.values()):
            if ax.level == AxiomLevel.LEVEL_0_EPISTEMIC and ax.status == AxiomStatus.ACTIVE:
                ax.status = AxiomStatus.INACTIVE
                ax.metadata["jettisoned_at_epoch"] = epoch
                deactivated_ids.append(ax.id)
                self.lifecycle_logs.append({
                    "id": ax.id,
                    "level": ax.level.value,
                    "name": ax.name,
                    "epoch": epoch,
                    "action": "Jettison Deactivated (Retained as INACTIVE Scaffolding)",
                    "delta_e": 0.0,
                    "status": AxiomStatus.INACTIVE.value,
                })

        self.phase = PhaseState.PHASE_2_STRUCTURAL_EXECUTION
        return deactivated_ids
