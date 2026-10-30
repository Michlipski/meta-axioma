"""Hierarchical XState v5 Deterministic Statechart Engine (`soc_g4b_governance`).

Enforces:
- Invariant [L1-002]: Statechart Determinism & Deep History H* Preservation.
- Executes the formal 30-State specification across:
  - 4 Compound Strata (20 states: Root, SovereignOperational, EmergencyEnclave, GenerationalHandover)
  - 2 Parallel Orthogonal Regions (10 states: AxiomaticSurveillance, PeerMediation)
  - Deep History Checkpoint state H*
  - 42 Deterministic Event Transitions & Complete Covering Paths
"""

from __future__ import annotations

import copy
import time
from typing import Any, Dict, List, Optional, Set
import uuid

from .domain_models import (
    GovernanceDomainInvariantViolation,
    GovernanceStatechartDefinition,
    GovernanceStatechartEngine as BaseStatechartEngine,
    GovernanceStatechartState,
    StatechartTransitionRecord,
)


class StatechartEngine:
    """High-level sovereign wrapper around the formal XState v5 Statechart execution engine."""

    def __init__(self, initial_state: GovernanceStatechartState = GovernanceStatechartState.GOV_ROOT_IDLE) -> None:
        self._initial_state = initial_state.value
        self._engine = BaseStatechartEngine(initial_state=self._initial_state)

    @property
    def current_state(self) -> GovernanceStatechartState:
        return GovernanceStatechartState(self._engine.current_state)

    @property
    def parallel_surveillance_state(self) -> GovernanceStatechartState:
        return GovernanceStatechartState(self._engine.parallel_surveillance_state)

    @property
    def parallel_mediation_state(self) -> GovernanceStatechartState:
        return GovernanceStatechartState(self._engine.parallel_mediation_state)

    def send(self, event_type: str, payload: Optional[Dict[str, Any]] = None) -> bool:
        """Dispatches an event deterministically through the statechart.

        Returns:
            bool: True if an event was accepted and transitioned, False otherwise.
        """
        initial_stratum = self._engine.current_state
        initial_surv = self._engine.parallel_surveillance_state
        initial_med = self._engine.parallel_mediation_state

        resulting_state = self._engine.send(event_type, payload or {})

        changed = (
            resulting_state != initial_stratum
            or self._engine.parallel_surveillance_state != initial_surv
            or self._engine.parallel_mediation_state != initial_med
        )
        return changed

    def get_active_states(self) -> Set[GovernanceStatechartState]:
        """Returns the set of all active states across compound strata and parallel regions."""
        active: Set[GovernanceStatechartState] = set()
        active.add(GovernanceStatechartState(self._engine.current_state))
        active.add(GovernanceStatechartState(self._engine.parallel_surveillance_state))
        active.add(GovernanceStatechartState(self._engine.parallel_mediation_state))
        return active

    def is_in_state(self, state: GovernanceStatechartState) -> bool:
        """Checks whether the given state is currently active in any stratum or region."""
        return state in self.get_active_states()

    def restore_deep_history(self) -> GovernanceStatechartState:
        """Restores the active operational state from deep history checkpoint H*."""
        self.send("EV_RESTORE_DEEP_HISTORY")
        return self.current_state

    def export_history(self) -> List[StatechartTransitionRecord]:
        """Exports the immutable log of state transitions."""
        return list(self._engine.transition_log)

    def get_transition_count(self) -> int:
        """Returns the total number of transitions recorded."""
        return len(self._engine.transition_log)

    def reset(self) -> None:
        """Resets the statechart engine to its initial state."""
        self._engine = BaseStatechartEngine(initial_state=self._initial_state)
