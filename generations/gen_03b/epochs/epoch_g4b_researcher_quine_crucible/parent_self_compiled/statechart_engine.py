"""Dynamically Compiled Hierarchical Statechart Engine for: statechart_soc_system_g3b_researcher_quine."""

from typing import Dict, List, Optional


class InvalidStateTransitionError(RuntimeError):
    """Raised when an event is not legal in the active hierarchical state."""
    pass


class GeneratedStatechartMachine:
    """Executes hierarchical XState v5 semantics for statechart_soc_system_g3b_researcher_quine."""

    INITIAL_LEAF_STATE = 'root.idle'
    PARENT_MAP: Dict[str, str] = {'root.active': 'root', 'active.committing': 'root.active', 'active.completed': 'root.active', 'active.validating': 'root.active', 'root.done': 'root', 'root.idle': 'root'}
    HISTORY_STATES: List[str] = []
    TRANSITIONS: Dict[str, Dict[str, str]] = {'root.active': {'FINISH': 'root.done'}, 'active.committing': {'COMMITTED': 'active.completed', 'UNDO': 'active.validating'}, 'active.validating': {'VALIDATED': 'active.committing'}, 'root.idle': {'START': 'active.validating'}}

    def __init__(self):
        self.active_state: str = self.INITIAL_LEAF_STATE
        self.history: List[str] = []
        self.deep_history: Dict[str, str] = {}

    def send(self, event: str) -> str:
        """Dispatches event up the hierarchical state chain (leaf -> parent compound)."""
        cursor: Optional[str] = self.active_state
        while cursor is not None:
            evt_map = self.TRANSITIONS.get(cursor, {})
            if event in evt_map:
                self.history.append(self.active_state)
                parent_id = self.PARENT_MAP.get(self.active_state)
                if parent_id:
                    self.deep_history[parent_id] = self.active_state
                self.active_state = evt_map[event]
                return self.active_state
            cursor = self.PARENT_MAP.get(cursor)
        raise InvalidStateTransitionError(
            f"Event '{event}' is not handled in state '{self.active_state}' or its ancestors."
        )

    def undo_transition(self) -> str:
        if self.history:
            self.active_state = self.history.pop()
        return self.active_state

    def functorial_undo(self) -> str:
        """[L1-002] Functorial Undo restoring prior hierarchical state."""
        return self.undo_transition()
