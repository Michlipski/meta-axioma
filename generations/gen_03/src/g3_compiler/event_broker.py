"""Distributed Event Sourcing & CQRS Broker (L1-G3-004).

Implements append-only distributed event logging, vector clock causal ordering,
deterministic left-fold state projections, and functorial 1-click rollbacks.
"""

from __future__ import annotations

import collections
import copy
import time
import uuid
from typing import Any, Callable, Dict, List, Optional, Tuple

try:
    from .models import DistributedEvent, EventType
except ImportError:
    from models import DistributedEvent, EventType


class DistributedEventBroker:
    """Append-only distributed event log with CQRS read projections and rollback morphisms."""

    def __init__(self):
        self._events: List[DistributedEvent] = []
        self._vector_clocks: Dict[str, int] = collections.defaultdict(int)
        self._projection_state: Dict[str, Any] = {}
        self._projection_reducers: Dict[EventType, Callable[[Dict[str, Any], Dict[str, Any]], None]] = {}
        self._checkpoints: Dict[str, Tuple[int, Dict[str, Any]]] = {}

    def register_reducer(self, event_type: EventType, reducer: Callable[[Dict[str, Any], Dict[str, Any]], None]) -> None:
        """Registers a CQRS projection reducer for an event type."""
        self._projection_reducers[event_type] = reducer

    def append_event(
        self,
        event_type: EventType,
        origin_node_id: str,
        payload: Dict[str, Any],
        capability_token_id: str,
    ) -> DistributedEvent:
        """Appends an immutable event to the log and applies projection reducer."""
        self._vector_clocks[origin_node_id] += 1
        current_vclock = dict(self._vector_clocks)

        event = DistributedEvent(
            event_id=f"evt_g3_{uuid.uuid4().hex[:10]}",
            event_type=event_type,
            origin_node_id=origin_node_id,
            payload=payload,
            capability_token_id=capability_token_id,
            timestamp=time.time(),
            vector_clock=current_vclock,
        )
        self._events.append(event)

        # Apply CQRS projection reducer
        reducer = self._projection_reducers.get(event_type)
        if reducer:
            reducer(self._projection_state, payload)

        return event

    def get_events(self, after_index: int = 0) -> List[DistributedEvent]:
        return self._events[after_index:]

    def get_projection_state(self) -> Dict[str, Any]:
        return copy.deepcopy(self._projection_state)

    def create_checkpoint(self, checkpoint_name: str) -> None:
        """Captures a cluster state checkpoint for instant rollback."""
        self._checkpoints[checkpoint_name] = (len(self._events), copy.deepcopy(self._projection_state))

    def rollback_to_checkpoint(self, checkpoint_name: str, authority_token_id: str) -> bool:
        """Functorially restores projection state to the named checkpoint (L1-G3-004)."""
        cp = self._checkpoints.get(checkpoint_name)
        if not cp:
            return False

        target_event_count, target_state = cp
        # Record rollback event in append-only log to maintain audit trail
        self._projection_state = copy.deepcopy(target_state)
        self.append_event(
            event_type=EventType.ROLLBACK_EXECUTED,
            origin_node_id="cluster_orchestrator",
            payload={"checkpoint": checkpoint_name, "reverted_to_index": target_event_count},
            capability_token_id=authority_token_id,
        )
        return True

    def replay_log_from_scratch(self) -> Dict[str, Any]:
        """Pure left-fold verification: re-runs all reducers over all events from t=0."""
        reconstructed: Dict[str, Any] = {}
        for ev in self._events:
            if ev.event_type == EventType.ROLLBACK_EXECUTED:
                cp_name = ev.payload.get("checkpoint")
                if cp_name in self._checkpoints:
                    reconstructed = dict(self._checkpoints[cp_name][1])
                continue
            reducer = self._projection_reducers.get(ev.event_type)
            if reducer:
                reducer(reconstructed, ev.payload)
        return reconstructed
